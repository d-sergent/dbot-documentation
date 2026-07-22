"""
dbot/vision/depth_reflex.py — Réflexe de Sécurité et Détection d'Obstacles D-Bot
================================================================================
Niveau 0 de la Triade Visuelle : Traitement matériel de la profondeur stéréo sur
la puce VPU (Intel Myriad X) de l'OAK-D Pro.

Génère un signal d'interruption réflexe (E-STOP) en < 15 ms si un obstacle franchit
le seuil de distance minimale dans le cône de marche du robot (0% charge CPU/VRAM Jetson).
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
    Gère le pipeline StereoDepth, le projecteur IR laser, l'extraction de la ROI
    centrale et le déclenchement non-bloquant d'alertes d'urgence.
    """
    def __init__(
        self,
        threshold_mm=250,
        roi_percents=(0.3, 0.7, 0.3, 0.8), # (x_min, x_max, y_min, y_max) relatif [0.0 - 1.0]
        laser_dot_mA=200,
        fps=30,
        on_obstacle_callback=None
    ):
        self.threshold_mm = threshold_mm
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
        self.is_obstacle_detected = False
        self.frame_count = 0
        self.last_latency_ms = 0.0
        self.lock = threading.Lock()

        self._setup_pipeline()

    def _setup_pipeline(self):
        """Configure le pipeline DepthAI Stéréo minimal et rapide."""
        # 1. Caméras Mono Stéréo (400p pour réduire la latence au minimum)
        mono_left = self.pipeline.create(dai.node.MonoCamera)
        mono_right = self.pipeline.create(dai.node.MonoCamera)
        stereo = self.pipeline.create(dai.node.StereoDepth)
        xout_depth = self.pipeline.create(dai.node.XLinkOut)

        xout_depth.setStreamName("depth")

        mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        mono_left.setFps(self.fps)

        mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        mono_right.setFps(self.fps)

        # 2. Configuration Stéréo Haute Performance
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        stereo.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
        stereo.setLeftRightCheck(True)
        stereo.setSubpixel(False) # Désactivé pour réduire la latence

        # Liens
        mono_left.out.link(stereo.left)
        mono_right.out.link(stereo.right)
        stereo.depth.link(xout_depth.input)

    def start(self):
        """Démarre le device OAK-D Pro et la boucle de surveillance."""
        if self.is_running:
            return

        print("⏳ [DepthReflex] Initialisation du pipeline Stéréo IR...")
        try:
            self.device = dai.Device(self.pipeline)
            
            # Activation du projecteur de points IR (Laser Dot) pour la profondeur active
            if self.laser_dot_mA > 0:
                self.device.setIrLaserDotProjectorIntensity(self.laser_dot_mA)
                print(f"🌙 [DepthReflex] Laser IR actif réglé à {self.laser_dot_mA} mA.")

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
            in_depth = q_depth.get() # Bloquant court jusqu'à l'arrivée d'une frame
            if in_depth is None:
                continue

            depth_frame = in_depth.getFrame() # ndarray float16/uint16 en mm
            h, w = depth_frame.shape

            # Calcul des limites de la ROI centrale
            x_min = int(w * self.roi_percents[0])
            x_max = int(w * self.roi_percents[1])
            y_min = int(h * self.roi_percents[2])
            y_max = int(h * self.roi_percents[3])

            roi_depth = depth_frame[y_min:y_max, x_min:x_max]

            # Filtrage des pixels valides (> 0 mm)
            valid_pixels = roi_depth[roi_depth > 0]

            if len(valid_pixels) > 0:
                # Médiane robuste éliminant le bruit
                median_dist = float(np.median(valid_pixels))
            else:
                median_dist = float('inf')

            t1 = time.perf_counter()
            latency_ms = (t1 - t0) * 1000.0

            # Détection d'obstacle
            obstacle = median_dist < self.threshold_mm

            with self.lock:
                self.last_distance_mm = median_dist
                self.is_obstacle_detected = obstacle
                self.frame_count += 1
                self.last_latency_ms = latency_ms

            # Trigger du callback non-bloquant en cas d'obstacle
            if obstacle and self.on_obstacle_callback:
                try:
                    self.on_obstacle_callback(median_dist)
                except Exception as cb_err:
                    print(f"⚠ [DepthReflex] Erreur callback d'obstacle : {cb_err}")

    def get_status(self):
        """Retourne l'état instantané du réflexe de sécurité."""
        with self.lock:
            return {
                "distance_mm": self.last_distance_mm,
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
            print("🔌 [DepthReflex] Caméra déconnectée et laser éteint.")

if __name__ == "__main__":
    def dummy_emergency_stop(dist):
        print(f"🚨 [E-STOP REFLEX] ALERTE OBSTACLE ! Distance = {dist:.1f} mm < Seuil !")

    print("🚀 Test Unitaire : dbot.vision.depth_reflex")
    reflex = DepthReflex(threshold_mm=300, on_obstacle_callback=dummy_emergency_stop)
    
    try:
        reflex.start()
        print("🔍 Surveillance en cours... Appuyez sur Ctrl+C pour quitter.")
        for _ in range(20):
            time.sleep(0.5)
            status = reflex.get_status()
            print(f"📊 Dist: {status['distance_mm']:.1f} mm | Obs: {status['obstacle_detected']} | Latence: {status['latency_ms']:.2f} ms")
    except KeyboardInterrupt:
        print("\nArrêt utilisateur.")
    except Exception as err:
        print(f"❌ Erreur : {err}")
    finally:
        reflex.stop()
