"""
dbot/vision/face_tracker.py — Détection et Tracking Spatial de visages
======================================================================
Utilise le VPU de l'OAK-D pour détecter les visages et calculer leur position 3D.
"""

import depthai as dai
import cv2
import numpy as np

class FaceTracker:
    """
    Gère la détection de visages en 3D (Spatial Detection).
    Permet de savoir où se trouve l'utilisateur par rapport au robot.
    """
    def __init__(self, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold
        self.model_name = "face-detection-retail-0005"
        
        # Le pipeline sera configuré pour inclure la détection spatiale
        self.pipeline = dai.Pipeline()
        self._setup_pipeline()

    def _setup_pipeline(self):
        # 1. Nœuds Caméra
        cam_rgb = self.pipeline.create(dai.node.ColorCamera)
        mono_left = self.pipeline.create(dai.node.MonoCamera)
        mono_right = self.pipeline.create(dai.node.MonoCamera)
        stereo = self.pipeline.create(dai.node.StereoDepth)
        
        # 2. Nœud de Détection Spatiale (IA + Profondeur)
        spatial_det = self.pipeline.create(dai.node.MobileNetSpatialDetectionNetwork)
        
        # Sorties
        xout_rgb = self.pipeline.create(dai.node.XLinkOut)
        xout_det = self.pipeline.create(dai.node.XLinkOut)
        
        xout_rgb.setStreamName("rgb")
        xout_det.setStreamName("det")
        
        # Configuration Caméras
        cam_rgb.setPreviewSize(300, 300) # Requis par le modèle face-detection
        cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        cam_rgb.setInterleaved(False)
        
        mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        
        # Configuration Stéréo
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        stereo.setDepthAlign(dai.CameraBoardSocket.RGB)
        
        # Configuration IA Spatiale
        # Note: On suppose que le blob est téléchargeable ou présent
        spatial_det.setBlobPath(self._get_model_path())
        spatial_det.setConfidenceThreshold(self.confidence_threshold)
        spatial_det.inputDepth.setBlocking(False)
        spatial_det.setBoundingBoxScaleFactor(0.5)
        spatial_det.setDepthLowerThreshold(100)
        spatial_det.setDepthUpperThreshold(5000)
        
        # Liens
        mono_left.out.link(stereo.left)
        mono_right.out.link(stereo.right)
        
        cam_rgb.preview.link(spatial_det.input)
        stereo.depth.link(spatial_det.inputDepth)
        
        spatial_det.passthrough.link(xout_rgb.input)
        spatial_det.out.link(xout_det.input)

    def _get_model_path(self):
        # Pour simplifier, on utilise un chemin relatif ou un téléchargement automatique via depthai_sdk si dispo
        # Ici on pointe vers un chemin standard
        import os
        return os.path.expanduser("~/dbot/models/face-detection-retail-0005_openvino_2021.4_4shave.blob")

    def run_detection(self, device):
        """
        Lit les données du device et retourne les visages détectés.
        
        Returns:
            list: Liste de dict { 'id', 'x', 'y', 'z', 'conf' } (coordonnées en mm)
        """
        q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        q_det = device.getOutputQueue(name="det", maxSize=4, blocking=False)
        
        in_rgb = q_rgb.get()
        in_det = q_det.get()
        
        faces = []
        if in_det is not None:
            for det in in_det.detections:
                faces.append({
                    "conf": det.confidence,
                    "x": det.spatialCoordinates.x,
                    "y": det.spatialCoordinates.y,
                    "z": det.spatialCoordinates.z
                })
        
        return faces, in_rgb.getCvFrame() if in_rgb else None

if __name__ == "__main__":
    # Test unitaire
    tracker = FaceTracker()
    print("⏳ Démarrage du Face Tracker 3D...")
    with dai.Device(tracker.pipeline) as device:
        while True:
            faces, frame = tracker.run_detection(device)
            if faces:
                for f in faces:
                    print(f"👤 Visage détecté : X={f['x']:.0f}mm, Y={f['y']:.0f}mm, Z={f['z']:.0f}mm")
            
            if frame is not None:
                cv2.imshow("D-Bot Vision - Face Tracking", frame)
            
            if cv2.waitKey(1) == ord('q'):
                break
