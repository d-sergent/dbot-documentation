#!/usr/bin/env python3
"""
scripts/vision/test_camera.py — Test vidéo OAK‑D Pro (DepthAI 3.x)
===================================================================
Affiche le flux RGB de la caméra OAK‑D Pro dans une fenêtre OpenCV.
API compatible DepthAI 3.x (node.Camera.build + requestOutput).
Appuyez sur **q** pour quitter.
"""
import cv2
import depthai as dai


def main():
    print("=" * 50)
    print("  D‑Bot — Test Vidéo OAK‑D Pro")
    print("=" * 50)
    print("Initialisation du pipeline DepthAI 3.x...")

    # 1️⃣ Pipeline
    pipeline = dai.Pipeline()

    # 2️⃣ Caméra couleur — API DepthAI 3.x
    #    .build() remplace setBoardSocket() + setResolution() séparés
    cam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)

    # 3️⃣ Flux de sortie en 640×360 BGR pour l'affichage
    video_out = cam.requestOutput(
        (640, 360),
        type=dai.ImgFrame.Type.BGR888p,
    )

    # 4️⃣ Nœud XLinkOut → envoie le flux vers l'hôte (Jetson)
    xout = pipeline.create(dai.node.XLinkOut)
    xout.setStreamName("rgb")
    video_out.link(xout.input)

    # 5️⃣ Connexion et boucle d'affichage
    try:
        with dai.Device(pipeline) as device:
            print("✅ Caméra connectée avec succès.")
            print("Appuyez sur 'q' dans la fenêtre pour quitter.")
            q = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            while True:
                frame = q.get().getCvFrame()
                cv2.imshow("OAK‑D Pro – Vue D‑Bot", frame)
                if cv2.waitKey(1) == ord('q'):
                    break
    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
