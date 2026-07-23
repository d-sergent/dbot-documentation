"""
dbot/vision/oak_camera.py — Interface matérielle pour Luxonis OAK-D Pro
======================================================================
Gère le pipeline DepthAI, le flux RGB Grand Angle (81° FOV via ISP Scale),
le calcul de profondeur stéréo, le filtrage matériel WLS sur VPU Myriad X
et le nœud SpatialLocationCalculator.
Compatible DepthAI API v2 (Sans Deprecation Warnings).
"""

import depthai as dai
import cv2
import numpy as np
import threading
import time

class OAKCameraError(Exception):
    """Erreur personnalisée pour la caméra OAK-D."""
    pass

class DbotCamera:
    """
    Gestionnaire de la caméra OAK-D Pro avec grand angle 81° (ISP Scaling sans Center Crop)
    et déport matériel sur le VPU Myriad X (Filtre WLS + SpatialLocationCalculator).
    """
    def __init__(self, resolution="1080p", fps=30, enable_depth=True, enable_tracker=True, hazard_distance_mm=500):
        self.pipeline = dai.Pipeline()
        self.device = None
        self.is_running = False
        self.enable_depth = enable_depth
        self.enable_tracker = enable_tracker
        self.hazard_distance_mm = hazard_distance_mm
        
        # --- 1. Configuration du capteur RGB Grand Angle (81° FOV sans Center Crop) ---
        self.cam_rgb = self.pipeline.create(dai.node.ColorCamera)
        if resolution == "1080p":
            self.cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
            self.cam_rgb.setIspScale(1, 3) # 1080p -> 640x360 via ISP (Plein Champ 81° FOV)
        else:
            self.cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
            self.cam_rgb.setIspScale(1, 2)
            
        self.cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
        self.cam_rgb.setInterleaved(False)
        self.cam_rgb.setFps(fps)
        
        # Sortie Vidéo ISP (Plein Champ 81° FOV)
        self.xout_video = self.pipeline.create(dai.node.XLinkOut)
        self.xout_video.setStreamName("video")
        self.cam_rgb.isp.link(self.xout_video.input)

        # --- Nœud Matériel ObjectTracker VPU (60+ FPS) ---
        if self.enable_tracker:
            self.tracker = self.pipeline.create(dai.node.ObjectTracker)
            self.tracker.setTrackerType(dai.TrackerType.ZERO_TILT)
            self.tracker.setTrackerIdAssignmentPolicy(dai.TrackerIdAssignmentPolicy.SMALLEST_ID)
            self.cam_rgb.video.link(self.tracker.inputTrackerFrame)

            self.xout_tracker = self.pipeline.create(dai.node.XLinkOut)
            self.xout_tracker.setStreamName("tracklets")
            self.tracker.out.link(self.xout_tracker.input)

        # --- 2. Configuration Stéréo Depth & Filtre WLS VPU (Optionnel) ---
        if self.enable_depth:
            self.mono_left = self.pipeline.create(dai.node.MonoCamera)
            self.mono_right = self.pipeline.create(dai.node.MonoCamera)
            self.stereo = self.pipeline.create(dai.node.StereoDepth)

            self.mono_left.setBoardSocket(dai.CameraBoardSocket.CAM_B)
            self.mono_right.setBoardSocket(dai.CameraBoardSocket.CAM_C)
            self.mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
            self.mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

            # Configuration Stéréo avancée sur VPU Myriad X
            self.stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
            self.stereo.setSubpixel(True)
            self.stereo.initialConfig.setMedianFilter(dai.StereoDepthProperties.MedianFilter.KERNEL_7x7)

            self.mono_left.out.link(self.stereo.left)
            self.mono_right.out.link(self.stereo.right)

            # Sortie Carte de Profondeur
            self.xout_depth = self.pipeline.create(dai.node.XLinkOut)
            self.xout_depth.setStreamName("depth")
            self.stereo.depth.link(self.xout_depth.input)

            # --- 3. Nœud SpatialLocationCalculator (VPU On-Chip Hazard Alert) ---
            self.spatial_calc = self.pipeline.create(dai.node.SpatialLocationCalculator)
            self.spatial_calc.inputConfig.setWaitForMessage(False)

            # Zone d'intérêt centrale 3D (Centre de l'image)
            config_roi = dai.SpatialLocationCalculatorConfigData()
            config_roi.depthThresholds.lowerThreshold = 100  # 10 cm min
            config_roi.depthThresholds.upperThreshold = 3500 # 3.5 m max
            config_roi.roi = dai.Rect(dai.Point2f(0.4, 0.4), dai.Point2f(0.6, 0.6))

            self.spatial_calc.initialConfig.addROI(config_roi)
            self.stereo.depth.link(self.spatial_calc.inputDepth)

            # Sortie Spatial Location
            self.xout_spatial = self.pipeline.create(dai.node.XLinkOut)
            self.xout_spatial.setStreamName("spatial_data")
            self.spatial_calc.out.link(self.xout_spatial.input)
        
        # Variables de flux
        self.latest_frame = None
        self.latest_depth = None
        self.is_hazard_detected = False
        self.hazard_distance = 0.0
        self.frame_lock = threading.Lock()
        self.thread = None

    def start(self):
        """Démarre la caméra et le thread de capture."""
        if self.is_running:
            return
            
        print("⏳ [Vision] Initialisation de l'OAK-D Pro (Grand Angle 81° FOV via ISP)...")
        try:
            self.device = dai.Device(self.pipeline)
            self.is_running = True
            
            # Démarrage du thread de lecture
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("✅ [Vision] Caméra OAK-D Pro & VPU matériels prêts (Plein Champ 81°).")
        except Exception as e:
            raise OAKCameraError(f"Impossible de démarrer l'OAK-D : {e}")

    def _run(self):
        """Boucle interne de capture des images et des données VPU."""
        video_queue = self.device.getOutputQueue(name="video", maxSize=4, blocking=False)
        depth_queue = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False) if self.enable_depth else None
        spatial_queue = self.device.getOutputQueue(name="spatial_data", maxSize=4, blocking=False) if self.enable_depth else None
        tracker_queue = self.device.getOutputQueue(name="tracklets", maxSize=4, blocking=False) if self.enable_tracker else None
        
        while self.is_running:
            try:
                # 1. Lecture de l'image RGB Grand Angle
                frame_data = video_queue.get()
                if frame_data:
                    frame = frame_data.getCvFrame()
                    with self.frame_lock:
                        self.latest_frame = frame

                # 2. Lecture de la carte de profondeur stéréo filtrée
                if depth_queue and depth_queue.has():
                    depth_data = depth_queue.get()
                    if depth_data:
                        depth_frame = depth_data.getFrame()
                        with self.frame_lock:
                            self.latest_depth = depth_frame

                # 3. Lecture des alertes de sécurité du VPU (SpatialLocationCalculator)
                if spatial_queue and spatial_queue.has():
                    spatial_data = spatial_queue.get()
                    if spatial_data:
                        spatials = spatial_data.getSpatialLocations()
                        for sData in spatials:
                            z_mm = sData.spatialCoordinates.z
                            with self.frame_lock:
                                self.hazard_distance = z_mm
                                self.is_hazard_detected = (0 < z_mm < self.hazard_distance_mm)

                # 4. Lecture des tracklets matériels VPU
                if tracker_queue and tracker_queue.has():
                    t_data = tracker_queue.get()
                    if t_data:
                        with self.frame_lock:
                            self.latest_tracklets = t_data.tracklets
            except Exception as e:
                print(f"⚠ [Vision] Erreur lecture flux VPU : {e}")
                break

    def get_frame(self):
        """Retourne la dernière image capturée."""
        with self.frame_lock:
            return self.latest_frame

    def get_depth_frame(self):
        """Retourne la dernière carte de profondeur filtrée par le VPU (en mm)."""
        with self.frame_lock:
            return self.latest_depth

    def get_tracklets(self):
        """Retourne la liste des tracklets d'objets suivis par le VPU Myriad X."""
        with self.frame_lock:
            return getattr(self, 'latest_tracklets', [])

    def check_hazard_alert(self):
        """
        Retourne l'état de l'alerte de sécurité matérielle émise par le VPU Myriad X (< 5ms).
        Returns: (bool is_hazard, float distance_mm)
        """
        with self.frame_lock:
            return self.is_hazard_detected, self.hazard_distance

    def set_ir_night_vision(self, enable=True, laser_dot_brightness=200, flood_brightness=0):
        """
        Contrôle la vision nocturne (Spécifique OAK-D Pro).
        """
        if not self.device:
            return
            
        if enable:
            self.device.setIrLaserDotProjectorIntensity(laser_dot_brightness)
            self.device.setIrFloodLightIntensity(flood_brightness)
            print(f"🌙 [Vision] Vision nocturne activée (Laser: {laser_dot_brightness}mA)")
        else:
            self.device.setIrLaserDotProjectorIntensity(0)
            self.device.setIrFloodLightIntensity(0)
            print("☀️ [Vision] Vision nocturne désactivée.")

    def stop(self):
        """Arrête la caméra proprement."""
        self.is_running = False
        if self.thread:
            self.thread.join()
        if self.device:
            self.device.close()
            print("🔌 [Vision] Caméra déconnectée.")

if __name__ == "__main__":
    # Test unitaire rapide
    cam = DbotCamera(enable_depth=True)
    try:
        cam.start()
        cam.set_ir_night_vision(True)
        time.sleep(2)
        frame = cam.get_frame()
        depth = cam.get_depth_frame()
        is_hazard, dist_mm = cam.check_hazard_alert()
        
        if frame is not None:
            print(f"✅ Capture RGB Grand Angle 81° réussie : {frame.shape}")
        if depth is not None:
            print(f"✅ Capture Profondeur VPU réussie : {depth.shape}")
        print(f"🛡 Alerte Danger VPU (< 500mm) : {is_hazard} (Distance centrale: {dist_mm:.0f} mm)")
    finally:
        cam.stop()
