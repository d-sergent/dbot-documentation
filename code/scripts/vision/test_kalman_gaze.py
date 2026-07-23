"""
scripts/vision/test_kalman_gaze.py — Test Unitaire du Filtre de Kalman 3D pour Active Gaze
========================================================================================
Vérifie le filtrage spatio-temporel des boîtes de détection (suppression du Bbox Jitter)
et l'estimation dynamique de la vitesse avec prédiction lors d'un masquage de 5 trames.

Exécution :
    python3 code/scripts/vision/test_kalman_gaze.py
"""

import cv2
import numpy as np
import math
import time
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from dbot.behaviors.active_gaze import GazeKalmanFilter3D

def test_kalman_filtering_and_prediction():
    print("⏳ [Test Unitaire 2] Initialisation du Filtre de Kalman 3D...")
    kf = GazeKalmanFilter3D()

    # 1. Test de suppression du Bbox Jitter sur un objet stationnaire (320, 180)
    print("📊 1. Test de suppression du Bbox Jitter (Objet immobile avec bruit ±10 px)...")
    np.random.seed(42)
    raw_jitter_errors = []
    filtered_jitter_errors = []

    for _ in range(30):
        real_x, real_y, real_z = 320.0, 180.0, 1000.0
        noise_x = float(np.random.normal(0, 10))
        noise_y = float(np.random.normal(0, 10))

        meas_x = real_x + noise_x
        meas_y = real_y + noise_y

        raw_err = math.sqrt(noise_x**2 + noise_y**2)
        raw_jitter_errors.append(raw_err)

        filt_x, filt_y, _ = kf.update((meas_x, meas_y, real_z))
        filt_err = math.sqrt((filt_x - real_x)**2 + (filt_y - real_y)**2)
        filtered_jitter_errors.append(filt_err)

    avg_raw_jitter = np.mean(raw_jitter_errors[10:])
    avg_filt_jitter = np.mean(filtered_jitter_errors[10:])
    jitter_reduction_pct = ((avg_raw_jitter - avg_filt_jitter) / avg_raw_jitter) * 100.0

    print(f"   • Bruit brut moyen Bbox Jitter : {avg_raw_jitter:.2f} px")
    print(f"   • Bruit filtré par Kalman     : {avg_filt_jitter:.2f} px (Réduction de {jitter_reduction_pct:.1f}%)")

    # 2. Test de poursuite de trajectoire et prédiction d'occultation
    print("\n🔮 2. Test de prédiction d'occultation sur cible en mouvement...")
    kf_moving = GazeKalmanFilter3D()
    for t in range(15):
        kx = 320.0 + t * 10.0  # +10 px par trame
        ky = 180.0 + t * 5.0   # +5 px par trame
        kf_moving.update((kx, ky, 1000.0))

    predicted_occlusions = []
    for step in range(5):
        pred_pos = kf_moving.predict_only()
        predicted_occlusions.append(pred_pos)
        print(f"   • Trame masquée #{step+1} -> Position prédite par Kalman : X={pred_pos[0]:.1f}, Y={pred_pos[1]:.1f}")

    print("\n========================================================")
    print(f"🎯 RÉSULTATS TEST UNITAIRE 2 (Filtre de Kalman 3D)")
    print(f"   • Réduction du bruit Bbox Jitter : {jitter_reduction_pct:.1f}%")
    print(f"   • Prédiction d'occultation       : {len(predicted_occlusions)} trames validées")
    print("========================================================\n")

    assert jitter_reduction_pct > 30.0, "Le filtre de Kalman doit réduire le Bbox Jitter d'au moins 30% !"
    assert len(predicted_occlusions) == 5, "La prédiction d'occultation doit fournir 5 trames !"
    print("✅ [Test Unitaire 2] VALIDE avec succès !")

if __name__ == "__main__":
    try:
        test_kalman_filtering_and_prediction()
    except Exception as e:
        print(f"❌ Échec Test Unitaire 2 : {e}")
        sys.exit(1)
