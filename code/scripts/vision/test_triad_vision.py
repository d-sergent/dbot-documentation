"""
scripts/vision/test_triad_vision.py — Test Complet de la Triade Visuelle D-Bot
===============================================================================
Couple OAK-D Pro (via DbotCamera avec déport VPU Myriad X), YOLO-World v2 (Zero-Shot TensorRT/ONNX)
et SpatialFusion pour afficher en direct la position 3D (X, Y, Z) des objets repérés.

Option Debug / Photo Incrémentale : Enregistre des clichés numérotés et horodatés dans
'/tmp/dbot_snapshots/snap_XXX_LABEL_DIST.jpg' avec surcouche visuelle multi-couleurs complète.
"""

import cv2
import numpy as np
import time
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from dbot.vision.oak_camera import DbotCamera
from dbot.vision.yolo_world import YoloWorldDetector, CLASS_COLORS_BGR, DEFAULT_COLOR
from dbot.vision.spatial_fusion import SpatialFusion

SNAPSHOT_DIR = "/tmp/dbot_snapshots"
LAST_SNAPSHOT_PATH = "/tmp/triad_last_detection.jpg"

def run_triad_test(save_snapshots=True):
    print("🚀 [Triade Visuelle] Démarrage du test d'intégration avec déport VPU OAK-D...")

    if save_snapshots:
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        print(f"📁 Dossier de clichés incrémentaux : '{SNAPSHOT_DIR}'")

    target_classes = ["main", "telephone", "bouteille", "table", "personne", "chaise", "obstacle"]
    print(f"🎯 Prompts sémantiques cibles : {target_classes}")
    
    detector = YoloWorldDetector(model_name="yolov8m-worldv2.pt", classes=target_classes)
    fusion = SpatialFusion()
    cam = DbotCamera(enable_depth=True, hazard_distance_mm=500)

    cam.start()
    cam.set_ir_night_vision(True, laser_dot_brightness=200)

    print("\n✅ Triade Visuelle Active ! Approchez votre main, votre téléphone ou une bouteille (< 1.5 m).")
    print(f"📸 Clichés incrémentaux activés dans '{SNAPSHOT_DIR}'.")
    print("🔍 Surveillance en cours... Appuyez sur Ctrl+C pour quitter.\n")

    fps_count = 0
    snapshot_counter = 0
    t_start = time.time()
    last_snapshot_time = 0

    try:
        while True:
            frame_rgb = cam.get_frame()
            frame_depth = cam.get_depth_frame()
            is_hazard, hazard_dist_mm = cam.check_hazard_alert()

            if frame_rgb is None or frame_depth is None:
                time.sleep(0.01)
                continue

            # Étape 1 : Inférence YOLO-World (Modèle Medium v8m, TensorRT/ONNX/PyTorch)
            detections_2d, latency_ms = detector.detect(frame_rgb)

            # Étape 2 : Fusion Spatiale 3D
            detections_3d = fusion.compute_spatial_3d(detections_2d, frame_depth)

            # Étape 3 : Filtrage Zone d'Action (< 3.5 m pour tout capturer dans la pièce)
            fps_count += 1
            all_valid_dets = [d for d in detections_3d if 0 < d["spatial_3d"]["z_mm"] <= 3500]

            # Sauvegarde d'un cliché incrémental si détections présentes (intervalle 1s)
            if save_snapshots and len(all_valid_dets) > 0 and (time.time() - last_snapshot_time > 1.0):
                snapshot_counter += 1
                
                # Annoter TOUTES les détections de la scène avec leurs bannières colorées
                annotated = detector.annotate_frame(frame_rgb, all_valid_dets)
                
                first_label = all_valid_dets[0]["label"].upper()
                first_dist = all_valid_dets[0]["spatial_3d"]["z_mm"]

                # Ajout des coordonnées 3D sous chaque boîte
                for det in all_valid_dets:
                    x1, y1, x2, y2 = det["bbox"]
                    label = det["label"]
                    s = det["spatial_3d"]
                    color = CLASS_COLORS_BGR.get(label.upper(), DEFAULT_COLOR)
                    
                    pos_str = f"X:{s['x_mm']:.0f} Y:{s['y_mm']:.0f} Z:{s['z_mm']:.0f}mm"
                    cv2.putText(
                        annotated, pos_str, (x1, min(y2 + 20, annotated.shape[0] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.50, color, 2
                    )

                snapshot_filename = f"snap_{snapshot_counter:03d}_{first_label}_{first_dist:.0f}mm.jpg"
                snapshot_filepath = os.path.join(SNAPSHOT_DIR, snapshot_filename)
                
                cv2.imwrite(snapshot_filepath, annotated)
                cv2.imwrite(LAST_SNAPSHOT_PATH, annotated)
                
                last_snapshot_time = time.time()

            if time.time() - t_start >= 1.0:
                hazard_str = f" 🛡 DANGER VPU: {hazard_dist_mm:.0f}mm" if is_hazard else ""
                print(f"⚡ [Triade Stats] FPS: {fps_count} | Latence Inférence: {latency_ms:.1f} ms | Détections: {len(all_valid_dets)}{hazard_str}")
                
                if len(all_valid_dets) > 0:
                    for det in all_valid_dets:
                        label = det["label"]
                        conf = det["confidence"]
                        s = det["spatial_3d"]
                        print(f"   🎯 [{label.upper()} {conf*100:.0f}%] ➔ X={s['x_mm']:.0f}mm, Y={s['y_mm']:.0f}mm, Z={s['z_mm']:.0f}mm ({s['z_mm']/1000.0:.2f}m)")
                    print(f"   📸 Cliché #{snapshot_counter:03d} enregistré dans '{SNAPSHOT_DIR}'")
                else:
                    print("   ⚪ Aucune détection dans la scène.")

                fps_count = 0
                t_start = time.time()

            time.sleep(0.01)
    finally:
        cam.stop()

if __name__ == "__main__":
    try:
        run_triad_test(save_snapshots=True)
    except KeyboardInterrupt:
        print("\n🔌 Arrêt du test visuel.")
    except Exception as err:
        print(f"❌ Erreur test : {err}")
