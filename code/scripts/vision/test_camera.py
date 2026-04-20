#!/usr/bin/env python3
"""
scripts/vision/test_camera.py — Test vidéo OAK‑D Pro (DepthAI 3.x)
===================================================================
Mode 1 (défaut) : Sauvegarde 5 captures JPEG dans /tmp/dbot_frames/
Mode 2 (--display) : Affichage OpenCV (nécessite un écran direct, pas NoMachine)

Usage :
    python3 test_camera.py           # sauvegarde les frames sur disque
    python3 test_camera.py --display # affichage temps réel (hors NoMachine)
"""
import cv2
import sys
import time
import os
import depthai as dai


SAVE_DIR    = "/tmp/dbot_frames"
FRAME_COUNT = 5   # nb de captures en mode sauvegarde


def main():
    display_mode = "--display" in sys.argv

    print("=" * 50)
    print("  D‑Bot — Test Vidéo OAK‑D Pro")
    print("=" * 50)

    if display_mode:
        print("Mode : Affichage temps réel (appuyer sur q pour quitter)")
    else:
        os.makedirs(SAVE_DIR, exist_ok=True)
        print(f"Mode : Capture disque → {SAVE_DIR}/")
        print(f"  {FRAME_COUNT} images seront sauvegardées puis le script quitte.")

    print("Initialisation du pipeline DepthAI 3.x...")

    try:
        with dai.Pipeline() as pipeline:

            cam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)
            video_out = cam.requestOutput((640, 360), dai.ImgFrame.Type.BGR888p)
            queue = video_out.createOutputQueue()

            pipeline.start()
            print("✅ Caméra connectée avec succès.\n")

            saved = 0
            while pipeline.isRunning():
                frame_data = queue.get()
                if frame_data is None:
                    continue
                frame = frame_data.getCvFrame()

                if display_mode:
                    cv2.imshow("OAK‑D Pro – Vue D‑Bot", frame)
                    if cv2.waitKey(1) == ord('q'):
                        pipeline.stop()
                        break
                else:
                    # Sauvegarde sur disque
                    path = f"{SAVE_DIR}/frame_{saved:03d}.jpg"
                    ok = cv2.imwrite(path, frame)
                    if ok:
                        h, w = frame.shape[:2]
                        print(f"  ✅ Frame {saved} sauvegardée : {path}  [{w}×{h}]")
                    else:
                        print(f"  ❌ Échec sauvegarde frame {saved}")
                    saved += 1
                    if saved >= FRAME_COUNT:
                        pipeline.stop()
                        break
                    time.sleep(0.1)

    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        cv2.destroyAllWindows()

    if not display_mode and saved > 0:
        print(f"\n✅ {saved} images sauvegardées dans {SAVE_DIR}/")
        print("Ouvrez-les avec :")
        print(f"  eog {SAVE_DIR}/  (Eye of GNOME)")
        print(f"  ls -lh {SAVE_DIR}/")


if __name__ == '__main__':
    main()
