#!/usr/bin/env python3
"""
scripts/vision/test_camera.py — Test RGB OAK-D Pro
===================================================
Ouvre le flux vidéo RGB de l'OAK-D Pro et l'affiche dans une fenêtre.
Utile pour valider la communication et le positionnement de la caméra.

Appuyez sur 'q' pour quitter.
"""

import cv2
import depthai as dai

def main():
    print("=" * 50)
    print("  D-Bot — Test Vidéo OAK-D Pro")
    print("=" * 50)
    print("Initialisation du pipeline DepthAI...")

    # 1. Création du pipeline
    pipeline = dai.Pipeline()

    # 2. Configuration de la caméra couleur
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A) # Caméra principale
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setInterleaved(False)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    cam_rgb.setFps(30)
    # Redimensionnement pour affichage fluide
    cam_rgb.setPreviewKeepAspectRatio(True)
    cam_rgb.setPreviewSize(640, 360) 

    # 3. Nœud de sortie vers la Jetson (Host)
    xout_rgb = pipeline.create(dai.node.XLinkOut)
    xout_rgb.setStreamName("rgb")
    cam_rgb.preview.link(xout_rgb.input)

    # 4. Connexion et démarrage
    try:
        with dai.Device(pipeline) as device:
            print("✅ Caméra connectée avec succès.")
            print("Affichage du flux vidéo. Cliquez sur la fenêtre et appuyez sur 'q' pour quitter.")
            
            queue_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            
            while True:
                # Récupération de l'image (frame)
                in_rgb = queue_rgb.get() 
                frame = in_rgb.getCvFrame()
                
                # Affichage
                cv2.imshow("OAK-D Pro - Vue D-Bot", frame)
                
                # Attente 1ms et vérification si la touche 'q' est pressée
                if cv2.waitKey(1) == ord('q'):
                    break
                    
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à la caméra : {e}")

if __name__ == '__main__':
    main()
