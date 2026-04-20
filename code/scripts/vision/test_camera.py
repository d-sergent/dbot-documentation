#!/usr/bin/env python3
"""
scripts/vision/test_camera.py — Test vidéo OAK‑D Pro (DepthAI 3.x)
===================================================================
Affiche le flux RGB de la caméra OAK‑D Pro dans une fenêtre OpenCV.
API DepthAI 3.x : requestOutput() crée automatiquement le lien XLink,
plus besoin de nœud XLinkOut explicite.
Appuyez sur **q** pour quitter.
"""
import cv2
import depthai as dai


def main():
    print("=" * 50)
    print("  D‑Bot — Test Vidéo OAK‑D Pro")
    print("=" * 50)
    print("Initialisation du pipeline DepthAI 3.x...")

    # DepthAI 3.x : Pipeline utilisé comme context manager
    with dai.Pipeline() as pipeline:

        # Caméra principale (CAM_A = capteur RGB central)
        cam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)

        # requestOutput() retourne un OutputNode ET crée le lien XLink automatiquement
        video_out = cam.requestOutput((640, 360), dai.ImgFrame.Type.BGR888p)

        try:
            with dai.Device(pipeline) as device:
                print("✅ Caméra connectée avec succès.")
                print("Appuyez sur 'q' dans la fenêtre pour quitter.")

                # On passe directement video_out (pas de nom de stream)
                queue = device.getOutputQueue(video_out)

                while True:
                    frame = queue.get().getCvFrame()
                    cv2.imshow("OAK‑D Pro – Vue D‑Bot", frame)
                    if cv2.waitKey(1) == ord('q'):
                        break

        except Exception as e:
            print(f"❌ Erreur : {e}")
        finally:
            cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
