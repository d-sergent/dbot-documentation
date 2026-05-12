"""
dbot/vision/oak_camera.py — Interface matérielle pour Luxonis OAK-D Pro
======================================================================
Gère le pipeline DepthAI, le flux RGB et le contrôle des LED IR (Vision Nocturne).
Compatible DepthAI API v2 (Stable).
"""

import depthai as dai
import cv2
import threading
import time

class OAKCameraError(Exception):
    """Erreur personnalisée pour la caméra OAK-D."""
    pass

class DbotCamera:
    """
    Gestionnaire de la caméra OAK-D Pro.
    Permet de récupérer les images et de contrôler les projecteurs IR.
    """
    def __init__(self, resolution="1080p", fps=30):
        self.pipeline = dai.Pipeline()
        self.device = None
        self.is_running = False
        
        # --- Configuration du capteur RGB ---
        self.cam_rgb = self.pipeline.create(dai.node.ColorCamera)
        if resolution == "1080p":
            self.cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        else:
            self.cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
            
        self.cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
        self.cam_rgb.setInterleaved(False)
        self.cam_rgb.setFps(fps)
        self.cam_rgb.setVideoSize(640, 360) # Taille optimisée pour l'IA et le stream
        
        # Sortie Vidéo
        self.xout_video = self.pipeline.create(dai.node.XLinkOut)
        self.xout_video.setStreamName("video")
        self.cam_rgb.video.link(self.xout_video.input)
        
        # Variables de flux
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.thread = None

    def start(self):
        """Démarre la caméra et le thread de capture."""
        if self.is_running:
            return
            
        print("⏳ [Vision] Initialisation de l'OAK-D Pro...")
        try:
            self.device = dai.Device(self.pipeline)
            self.is_running = True
            
            # Démarrage du thread de lecture
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("✅ [Vision] Caméra prête.")
        except Exception as e:
            raise OAKCameraError(f"Impossible de démarrer l'OAK-D : {e}")

    def _run(self):
        """Boucle interne de capture des images."""
        video_queue = self.device.getOutputQueue(name="video", maxSize=4, blocking=False)
        
        while self.is_running:
            try:
                frame_data = video_queue.get()
                if frame_data:
                    frame = frame_data.getCvFrame()
                    with self.frame_lock:
                        self.latest_frame = frame
            except Exception as e:
                print(f"⚠ [Vision] Erreur lecture flux : {e}")
                break

    def get_frame(self):
        """Retourne la dernière image capturée."""
        with self.frame_lock:
            return self.latest_frame

    def set_ir_night_vision(self, enable=True, laser_dot_brightness=200, flood_brightness=0):
        """
        Contrôle la vision nocturne (Spécifique OAK-D Pro).
        
        Args:
            enable (bool): Active ou désactive les projecteurs.
            laser_dot_brightness (int): Puissance du projecteur de points (0-1200mA). 
                                        Aide à la profondeur sur surfaces unies.
            flood_brightness (int): Puissance de la LED IR Flood (0-1500mA).
                                     Éclaire la scène en IR (invisible à l'œil).
        """
        if not self.device:
            return
            
        if enable:
            # Note: Les valeurs sont en mA. 200-400 est généralement suffisant.
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
    cam = DbotCamera()
    try:
        cam.start()
        cam.set_ir_night_vision(True) # Test IR
        time.sleep(2)
        frame = cam.get_frame()
        if frame is not None:
            print(f"✅ Capture réussie : {frame.shape}")
            cv2.imwrite("/tmp/oak_test.jpg", frame)
        time.sleep(1)
    finally:
        cam.stop()
