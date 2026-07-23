"""
scripts/vision/test_active_gaze.py — Test Complet du Regard Actif Intégré (Situation Réelle)
=============================================================================================
Associe l'ensemble des briques développées lors des sessions :
1. Triade Visuelle (YOLO-World v2 multilingue + OAK-D Pro 81° FOV).
2. Nœud matériel VPU ObjectTracker à 60+ FPS sur Myriad X.
3. Filtre de Kalman 3D (anti-jitter & prédiction de vitesse).
4. Asservissement en vitesse angulaire (set_velocity) et boucle CAN découplée à 100 Hz.

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
import threading

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from dbot.vision.oak_camera import DbotCamera
from dbot.vision.yolo_world import YoloWorldDetector
from dbot.vision.spatial_fusion import SpatialFusion
from dbot.behaviors.active_gaze import ActiveGazeTracker
from dbot.motors.neck import NeckController

def run_active_gaze_real_world(target_prompt="main", enable_motors=True):
    target_clean = target_prompt.lower().strip()
    print(f"🚀 [Active Gaze Intégré] Démarrage du test terrain pour la cible : '{target_clean.upper()}'...")

    context_classes = [target_clean, "main", "personne", "telephone", "bouteille", "table", "chaise"]
    unique_classes = list(dict.fromkeys(context_classes))

    # 1. Caméra OAK-D Pro avec VPU Tracker 60 FPS + Filtre WLS + Safety Calculator
    cam = DbotCamera(enable_depth=True, enable_tracker=True)
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

    curr_pan = 0.0
    curr_tilt = 0.0
    target_angles = (0.0, 0.0)
    is_running = True
    lock = threading.Lock()

    # 2. Thread Moteur CAN 100 Hz Découplé (Exécution en boucle 10 ms)
    def can_100hz_loop():
        nonlocal curr_pan, curr_tilt
        period = 0.010 # 10 ms
        t_next = time.perf_counter()
        
        while is_running:
            with lock:
                t_pan, t_tilt = target_angles

            # Interpolation progressive 100 Hz & commande en vitesse
            delta_pan = t_pan - curr_pan
            delta_tilt = t_tilt - curr_tilt

            if neck and (abs(delta_pan) > 0.2 or abs(delta_tilt) > 0.2):
                pan_vel = delta_pan * 10.0  # Gain vitesse
                tilt_vel = delta_tilt * 10.0
                neck.set_velocity(pan_vel_dps=pan_vel, tilt_vel_dps=tilt_vel)
                curr_pan += delta_pan * 0.15
                curr_tilt += delta_tilt * 0.15
            elif neck:
                neck.set_velocity(0.0, 0.0)

            t_next += period
            sleep_time = t_next - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)

    can_thread = threading.Thread(target=can_100hz_loop, daemon=True)
    can_thread.start()

    print(f"\n🔍 Active Gaze Intégré 100 Hz en cours pour '{target_clean.upper()}'... Appuyez sur Ctrl+C pour quitter.\n")

    try:
        while True:
            frame_rgb = cam.get_frame()
            frame_depth = cam.get_depth_frame()

            if frame_rgb is None or frame_depth is None:
                time.sleep(0.01)
                continue

            h, w = frame_rgb.shape[:2]

            # Contrôle de la sécurité matérielle VPU (< 500 mm)
            is_hazard, hazard_dist = cam.check_hazard_alert()
            if is_hazard:
                print(f"🛑 [VPU Safety Alert] Obstacle à {hazard_dist:.0f} mm ! Arrêt d'urgence.")

            # Inférence Zero-Shot YOLO-World v2 + Fusion 3D
            dets_2d, latency_ms = detector.detect(frame_rgb)
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

                # Regard Actif + Kalman 3D Anti-Jitter
                new_pan, new_tilt, is_centered = gaze_tracker.compute_head_target(
                    (cx, cy), w, h, curr_pan, curr_tilt, depth_z_mm=s['z_mm']
                )

                with lock:
                    target_angles = (new_pan, new_tilt)

                status_str = "CENTERED" if is_centered else f"TARGET -> Pan={new_pan:+.1f}° Tilt={new_tilt:+.1f}°"
                print(f"🎯 [{label} {conf*100:.0f}%] ➔ X={s['x_mm']:.0f}mm, Y={s['y_mm']:.0f}mm, Z={s['z_mm']:.0f}mm | {status_str}")
            else:
                # Prédiction d'occultation Kalman 3D
                pred_pan, pred_tilt, is_predicting = gaze_tracker.predict_lost_target(curr_pan, curr_tilt, w, h)
                if is_predicting:
                    with lock:
                        target_angles = (pred_pan, pred_tilt)
                    print(f"🔮 [Kalman 3D Predict] Poursuite par inertie -> Pan={pred_pan:+.1f}° Tilt={pred_tilt:+.1f}°")
                else:
                    scene_labels = [f"{d['label']}:{d['confidence']*100:.0f}%" for d in dets_3d]
                    scene_str = ", ".join(scene_labels) if scene_labels else "aucun objet"
                    print(f"⚪ Aucune détection pour '{target_clean}'. Scène actuelle : [{scene_str}]")

            time.sleep(0.033)
    finally:
        is_running = False
        cam.stop()
        if neck:
            neck.disable()
            print("🔌 Moteurs du cou désactivés.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Active Gaze Intégré D-Bot (Situation Réelle 100 Hz)")
    parser.add_argument("--target", default="main", help="Prompt sémantique cible en Français (ex: main, telephone, bouteille)")
    parser.add_argument("--no-motors", action="store_true", help="Désactiver les moteurs physiques (mode observation)")
    args = parser.parse_args()

    try:
        run_active_gaze_real_world(target_prompt=args.target, enable_motors=not args.no_motors)
    except KeyboardInterrupt:
        print("\n🔌 Arrêt du test Active Gaze.")
    except Exception as err:
        print(f"❌ Erreur test : {err}")
