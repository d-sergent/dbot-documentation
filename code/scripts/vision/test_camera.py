#!/usr/bin/env python3
"""
scripts/vision/test_camera.py — Test vidéo OAK‑D Pro (DepthAI 2.x)
===================================================================
Affiche le flux RGB de la caméra OAK‑D Pro dans une fenêtre OpenCV.
Appuyez sur **q** pour quitter.
"""

import cv2
import depthai as dai
# XLinkOut is accessed via dai.node.XLinkOut (no direct import needed)


def main():
    print("=" * 50)
    print("  D‑Bot — Test Vidéo OAK‑D Pro")
    print("=" * 50)
    print("Initialisation du pipeline DepthAI...")

    # 1️⃣ Pipeline
    pipeline = dai.Pipeline()

    # 2️⃣ Caméra couleur – utilisation du nouveau nœud Camera
    cam_rgb = pipeline.create(dai.node.Camera)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)  # Caméra principale
    cam_rgb.setResolution(dai.CameraResolution.THE_1080_P)
    cam_rgb.setInterleaved(False)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    cam_rgb.setFps(30)
    cam_rgb.setPreviewSize(640, 360)
    cam_rgb.setPreviewKeepAspectRatio(True)

    # 3️⃣ Sortie vers l’hôte (XLinkOut)
    xout_rgb = pipeline.create(dai.node.XLinkOut)
    xout_rgb.setStreamName("rgb")
    cam_rgb.preview.link(xout_rgb.input)

    # 4️⃣ Connexion et boucle d’affichage
    try:
        with dai.Device(pipeline) as device:
            print("✅ Caméra connectée avec succès.")
            print("Affichage du flux vidéo – appuyez sur 'q' pour quitter.")
            q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            while True:
                in_rgb = q_rgb.get()          # récupère le frame
                frame = in_rgb.getCvFrame()
                cv2.imshow("OAK‑D Pro – Vue D‑Bot", frame)
                if cv2.waitKey(1) == ord('q'):
                    break
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à la caméra : {e}")


if __name__ == '__main__':
    main()
