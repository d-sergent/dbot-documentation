"""
scripts/vision/test_active_gaze.py — Test Complet du Regard Actif (Active Gaze)
==============================================================================
Raccorde la Triade Visuelle (YOLO-World v2 multilingue + OAK-D Pro 81° FOV),
la fusion spatiale 3D, le régulateur ActiveGazeTracker et les moteurs du cou RS-05.

Fonctionnalités avancées :
- Détection hiérarchique simultanée de la PERSONNE ET de la MAIN (NMS classe-spécifique).
- Seuil de confiance ultra-permissif (0.05) pour objets complexes.
- Poursuite prédictive par inertie de vitesse (Predictive Gaze) si la cible s'échappe vite.

Exécution sur la Jetson :
    python3 code/scripts/vision/test_active_gaze.py --target "main"
    python3 code/scripts/vision/test_active_gaze.py --target "telephone"
"""

import cv2
import numpy as np
import time
import sys
import os
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from dbot.vision.oak_camera import DbotCamera
from dbot.vision.yolo_world import YoloWorldDetector
from dbot.vision.spatial_fusion import SpatialFusion
from dbot.behaviors.active_gaze import ActiveGazeTracker
from dbot.motors.neck import NeckController

def run_active_gaze_test(target_prompt="main", enable_motors=True):
    target_clean = target_prompt.lower().strip()
    print(f"🚀 [Active Gaze] Démarrage du test pour la cible : '{target_clean}'...")

    # Banque complète de contextes incluant simultanément PERSONNE et MAIN
    context_classes = [target_clean, "main", "personne", "telephone", "bouteille", "table", "chaise"]
    unique_classes = list(dict.fromkeys(context_classes))

    cam = DbotCamera(enable_depth=True)
    # Seuil ultra-permissif à 0.05
    detector = YoloWorldDetector(model_name="yolov8m-worldv2.pt", classes=unique_classes, default_conf_threshold=0.05)
    fusion = SpatialFusion()
    gaze_tracker = ActiveGazeTracker(kp_pan=0.45, kp_tilt=0.45)

    neck = None
    if enable_motors:
        try:
            print("⏳ Connexion et activation des moteurs du cou RS-05...")
            neck = NeckController()
            neck.detect()
            neck.enable()
            print("✅ Moteurs du cou prêts et activés.")
        except Exception as e:
            print(f"⚠️ Impossible d'activer les moteurs du cou ({e}). Mode observation pure.")
            neck = None

    cam.start()
    cam.set_ir_night_vision(True)

    print(f"\n🔍 Active Gaze en cours pour '{target_clean.upper()}'... Appuyez sur Ctrl+C pour quitter.\n")

    curr_pan = 0.0
    curr_tilt = 0.0

    try:
        while True:
            frame_rgb = cam.get_frame()
            frame_depth = cam.get_depth_frame()

            if frame_rgb is None or frame_depth is None:
                time.sleep(0.01)
                continue

            h, w = frame_rgb.shape[:2]

            # 1. Détection sémantique YOLO-World (support du Français natif)
            dets_2d, latency_ms = detector.detect(frame_rgb)

            # 2. Fusion Spatiale 3D
            dets_3d = fusion.compute_spatial_3d(dets_2d, frame_depth)

            # Target matching
            matching_dets = [
                d for d in dets_3d 
                if 0 < d["spatial_3d"]["z_mm"] <= 3500 and (
                    target_clean in d["label"].lower() or 
                    target_clean in d["raw_label_en"].lower() or
                    (target_clean in ["main", "hand"] and d["raw_label_en"] in ["hand", "main"])
                )
            ]

            if len(matching_dets) > 0:
                best_det = max(matching_dets, key=lambda d: d["confidence"])
                cx, cy = best_det["center"]
                s = best_det["spatial_3d"]
                label = best_det["label"]
                conf = best_det["confidence"]

                # 3. Calcul du recentrage angulaire de la tête
                new_pan, new_tilt, is_centered = gaze_tracker.compute_head_target(
                    (cx, cy), w, h, curr_pan, curr_tilt
                )

                status_str = "CENTERED" if is_centered else f"MOVING -> Pan={new_pan:+.1f}° Tilt={new_tilt:+.1f}°"
                print(f"🎯 [{label} {conf*100:.0f}%] ➔ X={s['x_mm']:.0f}mm, Y={s['y_mm']:.0f}mm, Z={s['z_mm']:.0f}mm | {status_str}")

                if neck and not is_centered:
                    neck.look_at(new_pan, new_tilt)
                    curr_pan = new_pan
                    curr_tilt = new_tilt
            else:
                # 4. Prédiction de trajectoire en cas de sortie rapide du champ de vision
                pred_pan, pred_tilt, is_predicting = gaze_tracker.predict_lost_target(curr_pan, curr_tilt)
                if is_predicting:
                    print(f"🔮 [Inertie Fuite] Anticipation fuite rapide -> Pan={pred_pan:+.1f}° Tilt={pred_tilt:+.1f}°")
                    if neck:
                        neck.look_at(pred_pan, pred_tilt)
                        curr_pan = pred_pan
                        curr_tilt = pred_tilt
                else:
                    scene_labels = [f"{d['label']}:{d['confidence']*100:.0f}%" for d in dets_3d]
                    scene_str = ", ".join(scene_labels) if scene_labels else "aucun objet"
                    print(f"⚪ Aucune détection pour '{target_clean}'. Scène actuelle : [{scene_str}]")

            time.sleep(0.08)
    finally:
        cam.stop()
        if neck:
            neck.disable()
            print("🔌 Moteurs du cou désactivés.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Active Gaze D-Bot (Regard Actif & Recentrage Cou)")
    parser.add_argument("--target", default="main", help="Prompt sémantique cible en Français (ex: main, telephone, bouteille)")
    parser.add_argument("--no-motors", action="store_true", help="Désactiver les moteurs physiques (mode observation)")
    args = parser.parse_args()

    try:
        run_active_gaze_test(target_prompt=args.target, enable_motors=not args.no_motors)
    except KeyboardInterrupt:
        print("\n🔌 Arrêt du test Active Gaze.")
    except Exception as err:
        print(f"❌ Erreur test : {err}")
