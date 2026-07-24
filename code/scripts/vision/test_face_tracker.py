"""
Script de Test et d'Enregistrement de Visages en Temps Réel pour D-Bot V1.

Usage :
1. Mode Reconnaissance en Temps Réel :
   python3 code/scripts/vision/test_face_tracker.py

2. Mode Enregistrement d'un nouveau profil (ex: 'David') :
   python3 code/scripts/vision/test_face_tracker.py --register "David"

Auteur : D-Bot Project (Google DeepMind Agentic Coding)
Date : 2026-07-24
"""

import os
import sys
import time
import argparse
import cv2
import numpy as np

# Inclusion du chemin racine pour importer le package dbot
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
if CODE_ROOT not in sys.path:
    sys.path.insert(0, CODE_ROOT)

from dbot.vision.face_tracker import FaceTracker
from dbot.vision.yolo_world import YOLOWorldDetector

try:
    from dbot.vision.oak_camera import OAKCamera
    OAK_AVAILABLE = True
except ImportError:
    OAK_AVAILABLE = False


def main():
    parser = argparse.ArgumentParser(description="Test & Enregistrement Reconnaissance Faciale D-Bot")
    parser.add_argument("--register", type=str, default="", help="Nom de la personne à enregistrer (ex: 'David')")
    parser.add_argument("--threshold", type=float, default=0.40, help="Seuil de similarité cosinus (défaut: 0.40)")
    parser.add_argument("--use-webcam", action="store_true", help="Forcer l'utilisation de la webcam au lieu de l'OAK-D")
    args = parser.parse_args()

    print("🚀 [FaceTracker Test] Initialisation du système de reconnaissance faciale ultra-compact...")
    tracker = FaceTracker(match_threshold=args.threshold)
    detector = YOLOWorldDetector(classes_fr=["personne"], conf_threshold=0.25)

    use_oak = OAK_AVAILABLE and not args.use_webcam
    cam = None

    if use_oak:
        print("⏳ [Vision] Initialisation de la caméra OAK-D Pro...")
        try:
            cam = OAKCamera()
            cam.start()
            print("✅ [Vision] Caméra OAK-D Pro opérationnelle.")
        except Exception as e:
            print(f"⚠️ Échec démarrage OAK-D Pro ({e}). Repli sur OpenCV VideoCapture...")
            use_oak = False

    if not use_oak:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print("❌ Erreur : Aucune caméra disponible (OAK-D ou Webcam).")
            sys.exit(1)
        print("✅ [Vision] Webcam OpenCV active.")

    register_mode = len(args.register.strip()) > 0
    target_name = args.register.strip().title()

    if register_mode:
        print(f"📸 [MODE ENREGISTREMENT] Positionnez le visage de '{target_name}' au centre du champ.")
        print("   Appuyez sur la touche 'SPACE' dans la fenêtre d'affichage (ou Ctrl+C) pour capturer et enregistrer.")
    else:
        print("🔍 [MODE RECONNAISSANCE] Inférence faciale active. Appuyez sur 'q' pour quitter.")

    try:
        while True:
            t0 = time.perf_counter()

            if use_oak:
                frame, spatial_dets = cam.get_frame_with_spatial()
            else:
                ret, frame = cam.read()
                if not ret:
                    break
                spatial_dets = []

            if frame is None:
                continue

            h, w = frame.shape[:2]
            detections, latency_ms = detector.detect(frame)

            # Traitement des personnes détectées par YOLO-World
            for det in detections:
                if det["label"] == "PERSONNE":
                    bbox = det["bbox"]
                    x1, y1, x2, y2 = bbox

                    # Inférence Faciale sur la ROI du visage (haut du corps)
                    name, sim = tracker.process_person_crop(frame, bbox)

                    # Couleur : Vert si reconnu, Jaune si Inconnu
                    color = (0, 255, 0) if name != "INCONNU" else (0, 255, 255)
                    label_text = f"{name} ({sim*100:.0f}%)" if name != "INCONNU" else "PERSONNE INCONNUE"

                    # Dessin du rectangle et de la bannière
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.rectangle(frame, (x1, max(0, y1 - 30)), (x1 + len(label_text) * 11, y1), color, -1)
                    cv2.putText(frame, label_text, (x1 + 5, max(15, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

            # Réticule et Guide de Centrage Visuel en Mode Enregistrement
            if register_mode:
                cx, cy = w // 2, h // 2
                box_w, box_h = 240, 240
                rx1, ry1 = cx - box_w // 2, cy - box_h // 2
                rx2, ry2 = cx + box_w // 2, cy + box_h // 2

                # Vérification si la tête de la personne est dans la zone de visée centrale
                is_centered = False
                for det in detections:
                    if det["label"] == "PERSONNE":
                        bx1, by1, bx2, by2 = det["bbox"]
                        hx, hy = (bx1 + bx2) // 2, by1 + int((by2 - by1) * 0.20)
                        if rx1 <= hx <= rx2 and ry1 <= hy <= ry2:
                            is_centered = True
                            break

                target_color = (0, 255, 0) if is_centered else (0, 165, 255)
                # Dessin du cadre de centrage et de la croix centrale
                cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), target_color, 2)
                cv2.line(frame, (cx - 15, cy), (cx + 15, cy), target_color, 2)
                cv2.line(frame, (cx, cy - 15), (cx, cy + 15), target_color, 2)

                if is_centered:
                    status_str = f"✅ VISAGE DE '{target_name}' CENTRÉ - APPUYEZ SUR ESPACE"
                    cv2.putText(frame, status_str, (30, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
                else:
                    status_str = f"➡️ RECENTRER LE VISAGE DE '{target_name}' DANS LE CADRE VERT"
                    cv2.putText(frame, status_str, (30, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 165, 255), 2)

            t1 = time.perf_counter()
            fps = 1.0 / max(0.001, t1 - t0)

            cv2.putText(frame, f"FPS: {fps:.1f} | Latence Vision: {latency_ms:.1f}ms", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.imshow("D-Bot Face Tracker", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif register_mode and key == 32:  # Touche ESPACE
                # Capture et enregistrement du visage
                for det in detections:
                    if det["label"] == "PERSONNE":
                        x1, y1, x2, y2 = det["bbox"]
                        crop_h = int((y2 - y1) * 0.40)
                        head_crop = frame[max(0, y1):min(y1 + crop_h, h), max(0, x1):min(x2, w)]
                        if head_crop.size > 0:
                            aligned = cv2.resize(head_crop, (112, 112))
                            success = tracker.register_face(target_name, aligned)
                            if success:
                                print(f"🎉 Enregistrement réussi pour '{target_name}' !")
                                register_mode = False
                                break

    except KeyboardInterrupt:
        print("\n🛑 Arrêt par l'utilisateur.")
    finally:
        if use_oak and cam:
            cam.stop()
        elif cam:
            cam.release()
        cv2.destroyAllWindows()
        print("✅ Ressources nettoyées.")


if __name__ == "__main__":
    main()
