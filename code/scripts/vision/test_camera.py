#!/usr/bin/env python3
"""
scripts/vision/test_camera.py — Test vidéo OAK‑D Pro (DepthAI 3.x)
===================================================================
API DepthAI 3.x complète :
  - Pipeline comme context manager
  - pipeline.start() pour démarrer (pas de Device(pipeline))
  - video_out.get() pour récupérer les frames directement
Appuyez sur **q** pour quitter.
"""
import cv2
import depthai as dai


def main():
    print("=" * 50)
    print("  D‑Bot — Test Vidéo OAK‑D Pro")
    print("=" * 50)
    print("Initialisation du pipeline DepthAI 3.x...")

    try:
        with dai.Pipeline() as pipeline:

            # Caméra principale — .build() configure le socket
            cam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)

            # requestOutput crée le flux + le lien XLink automatiquement
            video_out = cam.requestOutput((640, 360), dai.ImgFrame.Type.BGR888p)

            # Démarrage du pipeline (connexion à la caméra)
            pipeline.start()
            print("✅ Caméra connectée avec succès.")
            print("Appuyez sur 'q' dans la fenêtre pour quitter.")

            while pipeline.isRunning():
                # Récupération du frame directement via video_out
                frame_data = video_out.get()
                if frame_data is not None:
                    frame = frame_data.getCvFrame()
                    cv2.imshow("OAK‑D Pro – Vue D‑Bot", frame)

                if cv2.waitKey(1) == ord('q'):
                    pipeline.stop()
                    break

    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
