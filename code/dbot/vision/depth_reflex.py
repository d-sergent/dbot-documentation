"""
dbot/vision/depth_reflex.py — Réflexe de Sécurité et Détection d'Obstacles D-Bot
================================================================================
Niveau 0 de la Triade Visuelle : Traitement matériel de la profondeur stéréo sur
la puce VPU (Intel Myriad X) de l'OAK-D Pro.

Génère un signal d'interruption réflexe (E-STOP) en < 15 ms si un obstacle franchit
le seuil de distance minimale ou aveugle la caméra par trop grande proximité (< 15cm).
"""

import depthai as dai
import numpy as np
import threading
import time
import sys

class DepthReflexError(Exception):
    """Erreur personnalisée pour le module de réflexe de profondeur."""
    pass

class DepthReflex:
    """
    Module de réflexe de profondeur haute fréquence pour OAK-D Pro.
    Gère le pipeline StereoDepth avec ExtendedDisparity (MinZ ~9 cm), le projecteur IR,
    l'extraction de la ROI centrale, la détection d'aveuglement et les alertes E-STOP.
    """
    def __init__(
        self,
        threshold_mm=300,
        invalid_ratio_threshold=0.40, # 40% de pixels 0 = obstacle trop proche (< 15 cm)
        roi_percents=(0.3, 0.7, 0.3, 0.8), # (x_min, x_max, y_min, y_max)
        laser_dot_mA=200,
        fps=30,
        on_obstacle_callback=None
    ):
        self.threshold_mm = threshold_mm
        self.invalid_ratio_threshold = invalid_ratio_threshold
        self.roi_percents = roi_percents
        self.laser_dot_mA = laser_dot_mA
        self.fps = fps
        self.on_obstacle_callback = on_obstacle_callback
        
        self.pipeline = dai.Pipeline()
        self.device = None
        self.is_running = False
        self.thread = None

        # Variables d'état
        self.last_distance_mm = float('inf')
        self.last_invalid_ratio = 0.0
        self.is_obstacle_detected = False
        self.frame_count = 0
        self.last_latency_ms = 0.0
        self.lock = threading.Lock()

        self._setup_pipeline()

    def _setup_pipeline(self):
        """Configure le pipeline DepthAI Stéréo minimal et rapide."""
        # 1. Caméras Mono Stéréo (400p)
        mono_left = self.pipeline.create(dai.node.MonoCamera)
        mono_right = self.pipeline.create(dai.node.MonoCamera)
        stereo = self.pipeline.create(dai.node.StereoDepth)
        xout_depth = self.pipeline.create(dai.node.XLinkOut)

        xout_depth.setStreamName("depth")

        mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_left.setBoardSocket(dai.CameraBoardSocket.CAM_B) # CAM_B = LEFT
        mono_left.setFps(self.fps)

        mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_right.setBoardSocket(dai.CameraBoardSocket.CAM_C) # CAM_C = RIGHT
        mono_right.setFps(self.fps)

        # 2. Configuration Stéréo avec Extended Disparity pour réduire la MinZ (9 cm)
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
        stereo.setLeftRightCheck(True)
        stereo.setExtendedDisparity(True) # Divise par 2 la distance minimale de détection !
        stereo.setSubpixel(False)

        # Liens
        mono_left.out.link(stereo.left)
        mono_right.out.link(stereo.right)
        stereo.depth.link(xout_depth.input)

    def start(self):
        """Démarre le device OAK-D Pro et la boucle de surveillance."""
        if self.is_running:
            return

        print("⏳ [DepthReflex] Initialisation du pipeline Stéréo IR (Extended Disparity)...")
        try:
            self.device = dai.Device(self.pipeline)
            
            if self.laser_dot_mA > 0:
                try:
                    self.device.setIrLaserDotProjectorIntensity(self.laser_dot_mA)
                    print(f"🌙 [DepthReflex] Laser IR actif réglé.")
                except Exception as ir_err:
                    print(f"⚠ [DepthReflex] Avertissement Laser IR : {ir_err}")

            self.is_running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            print("✅ [DepthReflex] Module de réflexe prêt et actif.")
        except Exception as e:
            raise DepthReflexError(f"Impossible de démarrer OAK-D DepthReflex : {e}")

    def _run_loop(self):
        """Boucle de traitement de la carte de profondeur à haute fréquence."""
        q_depth = self.device.getOutputQueue(name="depth", maxSize=2, blocking=False)
        
        while self.is_running:
            t0 = time.perf_counter()
            in_depth = q_depth.get()
            if in_depth is None:
                continue

            depth_frame = in_depth.getFrame()
            h, w = depth_frame.shape

            x_min = int(w * self.roi_percents[0])
            x_max = int(w * self.roi_percents[1])
            y_min = int(h * self.roi_percents[2])
            y_max = int(h * self.roi_percents[3])

            roi_depth = depth_frame[y_min:y_max, x_min:x_max]
            total_pixels = roi_depth.size

            # Filtrage des pixels valides (> 0 mm)
            valid_pixels = roi_depth[roi_depth > 0]
            invalid_pixels_count = total_pixels - len(valid_pixels)
            invalid_ratio = invalid_pixels_count / float(total_pixels) if total_pixels > 0 else 0.0

            # Calcul de distance
            if len(valid_pixels) > 0:
                median_dist = float(np.median(valid_pixels))
            else:
                median_dist = 0.0 # En dessous de la distance min

            t1 = time.perf_counter()
            latency_ms = (t1 - t0) * 1000.0

            # Détection d'obstacle :
            # 1. Distance mesurée sous le seuil (ex: < 300 mm)
            # OR 2. Aveuglement de proximité (plus de 40% de pixels 0 dans la ROI -> obstacle à < 10-15 cm!)
            obstacle = (median_dist < self.threshold_mm) or (invalid_ratio > self.invalid_ratio_threshold)

            with self.lock:
                self.last_distance_mm = median_dist
                self.last_invalid_ratio = invalid_ratio
                self.is_obstacle_detected = obstacle
                self.frame_count += 1
                self.last_latency_ms = latency_ms

            if obstacle and self.on_obstacle_callback:
                try:
                    self.on_obstacle_callback(median_dist, invalid_ratio)
                except Exception as cb_err:
                    print(f"⚠ [DepthReflex] Erreur callback obstacle : {cb_err}")

    def get_status(self):
        """Retourne l'état instantané du réflexe de sécurité."""
        with self.lock:
            return {
                "distance_mm": self.last_distance_mm,
                "invalid_ratio": self.last_invalid_ratio,
                "obstacle_detected": self.is_obstacle_detected,
                "threshold_mm": self.threshold_mm,
                "latency_ms": self.last_latency_ms,
                "frames": self.frame_count
            }

    def stop(self):
        """Arrête le réflexe et éteint les projecteurs IR."""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.device:
            try:
                self.device.setIrLaserDotProjectorIntensity(0)
            except Exception:
                pass
            self.device.close()
            print("🔌 [DepthReflex] Caméra déconnectée.")

if __name__ == "__main__":
    def dummy_emergency_stop(dist, inv_ratio):
        reason = f"Distance = {dist:.1f} mm" if inv_ratio < 0.40 else f"PROXIMITÉ EXTRÊME (< 10cm, {inv_ratio*100:.0f}% pixels masqués)"
        print(f"🚨 [E-STOP REFLEX] ALERTE OBSTACLE ! ({reason})")

    print("🚀 Test Unitaire : dbot.vision.depth_reflex (Optimisé Proximité)")
    reflex = DepthReflex(threshold_mm=300, on_obstacle_callback=dummy_emergency_stop)
    
    try:
        reflex.start()
        print("🔍 Surveillance en cours... Placez votre main très proche (< 15 cm) pour tester.")
        for _ in range(25):
            time.sleep(0.5)
            status = reflex.get_status()
            print(f"📊 Dist: {status['distance_mm']:.1f} mm | Masqué: {status['invalid_ratio']*100:.0f}% | Obs: {status['obstacle_detected']} | Latence: {status['latency_ms']:.2f} ms")
    except KeyboardInterrupt:
        print("\nArrêt utilisateur.")
    except Exception as err:
        print(f"❌ Erreur : {err}")
    finally:
        reflex.stop()
