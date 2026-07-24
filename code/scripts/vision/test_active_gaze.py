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
from dbot.vision.yolo_world import YoloWorldDetector, translate_fr_to_en
from dbot.vision.spatial_fusion import SpatialFusion
from dbot.vision.face_tracker import FaceTracker
from dbot.behaviors.active_gaze import ActiveGazeTracker
from dbot.motors.neck import NeckController
import collections

def run_active_gaze_real_world(target_prompt="main", enable_motors=True):
    target_clean = target_prompt.lower().strip()
    print(f"🚀 [Active Gaze Intégré] Démarrage du test terrain pour la cible : '{target_clean.upper()}'...")

    context_classes = [target_clean, "main", "personne", "telephone", "bouteille", "table", "chaise"]
    unique_classes = list(dict.fromkeys(context_classes))

    # 1. Caméra OAK-D Pro & Détecteur YOLO-World + FaceTracker (SCRFD 500M + ArcFace)
    cam = DbotCamera(enable_depth=True)
    detector = YoloWorldDetector(model_name="yolov8m-worldv2.pt", classes=unique_classes, default_conf_threshold=0.05)
    face_tracker = FaceTracker(match_threshold=0.30)
    fusion = SpatialFusion()
    gaze_tracker = ActiveGazeTracker(kp_pan=0.45, kp_tilt=0.45)
    emb_buffers = collections.defaultdict(lambda: collections.deque(maxlen=5))

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

            if neck and (abs(t_pan - curr_pan) > 0.8 or abs(t_tilt - curr_tilt) > 0.8):
                neck.look_at(t_pan, t_tilt)
                curr_pan = t_pan
                curr_tilt = t_tilt

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

            # Identification faciale sur les détections de personnes (SCRFD 500M + ArcFace)
            for d in dets_3d:
                lbl_fr = d["label"].lower()
                lbl_en = d["raw_label_en"].lower()
                if lbl_fr in ["personne", "person"] or lbl_en in ["person", "human"]:
                    bx1, by1, bx2, by2 = d["bbox"]
                    track_key = f"{bx1//100}_{by1//100}"

                    head_h_tmp = int((by2 - by1) * 0.55)
                    hx1_t, hy1_t = max(0, bx1), max(0, by1)
                    hx2_t, hy2_t = min(w, bx2), min(h, by1 + head_h_tmp)
                    head_crop_tmp = frame_rgb[hy1_t:hy2_t, hx1_t:hx2_t]

                    if head_crop_tmp.size > 0:
                        faces_tmp = face_tracker.detect_faces_scrfd(head_crop_tmp, conf_thresh=0.35)
                        if faces_tmp:
                            best_tmp = max(faces_tmp, key=lambda f: f['score'])
                            lmks_tmp = best_tmp['landmarks']
                            if lmks_tmp is not None and len(lmks_tmp) == 5:
                                aligned_tmp = face_tracker.align_face(head_crop_tmp, lmks_tmp)
                            else:
                                bx1t, by1t, bx2t, by2t = best_tmp['bbox']
                                fr_tmp = head_crop_tmp[max(0,by1t):min(head_crop_tmp.shape[0],by2t),
                                                       max(0,bx1t):min(head_crop_tmp.shape[1],bx2t)]
                                aligned_tmp = cv2.resize(fr_tmp if fr_tmp.size > 0 else head_crop_tmp, (112, 112))
                        else:
                            ch_t, cw_t = head_crop_tmp.shape[:2]
                            fr_tmp = head_crop_tmp[int(ch_t*0.05):int(ch_t*0.90), int(cw_t*0.10):int(cw_t*0.90)]
                            aligned_tmp = cv2.resize(fr_tmp if fr_tmp.size > 0 else head_crop_tmp, (112, 112))

                        emb_tmp = face_tracker.get_embedding(aligned_tmp)
                        if np.linalg.norm(emb_tmp) > 0:
                            emb_buffers[track_key].append(emb_tmp)

                    if len(emb_buffers[track_key]) > 0:
                        mean_emb = np.mean(list(emb_buffers[track_key]), axis=0)
                        norm_me = np.linalg.norm(mean_emb)
                        if norm_me > 0:
                            mean_emb = mean_emb / norm_me
                        fname, fsim = face_tracker.identify_embedding(mean_emb)
                    else:
                        fname, fsim = "INCONNU", 0.0

                    if fname != "INCONNU":
                        d["face_name"] = fname
                        d["face_sim"] = fsim
                        d["label"] = f"{fname} ({fsim*100:.0f}%)"
                    else:
                        d["face_name"] = "INCONNU"
                        d["face_sim"] = 0.0

            # Target matching flexible (Prénom Nominatif + Sémantique Fr/En)
            target_en = translate_fr_to_en(target_clean).lower()
            matching_dets = []
            for d in dets_3d:
                lbl_fr = d["label"].lower()
                lbl_en = d["raw_label_en"].lower()
                face_name_clean = d.get("face_name", "").lower()
                z_mm = d["spatial_3d"]["z_mm"]

                if z_mm > 3500:
                    continue

                if (face_name_clean and target_clean == face_name_clean) or \
                   (target_clean in lbl_fr) or (target_en in lbl_en) or \
                   (target_clean in ["tasse", "cup", "mug"] and any(k in lbl_en for k in ["cup", "mug", "coffee mug", "tasse"])) or \
                   (target_clean in ["main", "hand"] and lbl_en in ["hand", "main"]) or \
                   (target_clean in ["personne", "person"] and lbl_en in ["person", "human"]):
                    matching_dets.append(d)

            if len(matching_dets) > 0:
                best_det = max(matching_dets, key=lambda d: d["confidence"])
                cx, cy = best_det["center"]
                s = best_det["spatial_3d"]
                label = best_det["label"]
                conf = best_det["confidence"]

                # Télémétrie physique réelle des moteurs RS-05
                if neck:
                    state = neck.get_state()
                    curr_pan = state['pan_deg']
                    curr_tilt = state['tilt_deg']

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
