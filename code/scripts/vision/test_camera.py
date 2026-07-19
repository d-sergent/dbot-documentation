#!/usr/bin/env python3
"""
scripts/vision/test_camera.py — Test vidéo OAK‑D Pro
===================================================================
Mode 1 (défaut) : Sauvegarde 5 captures JPEG dans /tmp/dbot_frames/
Mode 2 (--display) : Affichage OpenCV (nécessite un écran direct, pas NoMachine)
"""
import cv2
import sys
import time
import os

# Ajouter le dossier Code à l'environnement Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from dbot.vision.oak_camera import DbotCamera

SAVE_DIR    = "/tmp/dbot_frames"
FRAME_COUNT = 5

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

    cam = None
    try:
        cam = DbotCamera(resolution="1080p", fps=30)
        cam.start()

        saved = 0
        warmup = 0
        WARMUP_FRAMES = 10
        
        while True:
            frame = cam.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            if display_mode:
                cv2.imshow("OAK‑D Pro – Vue D‑Bot", frame)
                if cv2.waitKey(1) == ord('q'):
                    break
            else:
                if warmup < WARMUP_FRAMES:
                    warmup += 1
                    if warmup == 1:
                        print(f"  ⏳ Warm-up auto-exposition ({WARMUP_FRAMES} frames)...")
                    time.sleep(0.1)
                    continue
                
                path = f"{SAVE_DIR}/frame_{saved:03d}.jpg"
                ok = cv2.imwrite(path, frame)
                if ok:
                    h, w = frame.shape[:2]
                    print(f"  ✅ Frame {saved} sauvegardée : {path}  [{w}×{h}]")
                else:
                    print(f"  ❌ Échec sauvegarde frame {saved}")
                
                saved += 1
                if saved >= FRAME_COUNT:
                    break
                time.sleep(0.1)

    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        if cam:
            cam.stop()
        cv2.destroyAllWindows()

    if not display_mode and saved > 0:
        print(f"\n✅ {saved} images sauvegardées dans {SAVE_DIR}/")
        print("Ouvrez-les avec :")
        print(f"  ls -lh {SAVE_DIR}/")

if __name__ == '__main__':
    main()
