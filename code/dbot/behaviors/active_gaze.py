"""
dbot/behaviors/active_gaze.py — Boucle d'Asservissement du Regard (Active Gaze Tracker & Kalman 3D)
================================================================================================
Gère l'asservissement visuel du cou (Pan ID:1 & Tilt ID:2) pour orienter la tête du robot
et maintenir un objet ciblé au centre exact du champ de vision grand angle (81° FOV).

Fonctionnalités :
- Filtre de Kalman 3D (GazeKalmanFilter3D) : élimine le bruit haute fréquence (Bbox Jitter) et estime la vitesse.
- Extrapolation et prédiction de trajectoire spatiale lors d'occultations temporaires.
- Bridage de sécurité absolu aux limites mécaniques définies dans config.py.
"""

import cv2
import numpy as np
import time
import math
import logging

from dbot.config import PAN_MIN_RAD, PAN_MAX_RAD, TILT_MIN_RAD, TILT_MAX_RAD

log = logging.getLogger('active_gaze')

class GazeKalmanFilter3D:
    """
    Filtre de Kalman Spatio-Temporel 3D pour le suivi de cible visuelle.
    Vecteur d'état X = [x, y, z, v_x, v_y, v_z]^T
    Vecteur de mesure Z = [x, y, z]^T
    """
    def __init__(self, dt=0.033, process_noise=1e-3, measurement_noise=100.0):
        self.dt = dt
        self.kf = cv2.KalmanFilter(6, 3)

        # Matrice de transition F
        self.kf.transitionMatrix = np.array([
            [1, 0, 0, dt, 0,  0],
            [0, 1, 0, 0,  dt, 0],
            [0, 0, 1, 0,  0,  dt],
            [0, 0, 0, 1,  0,  0],
            [0, 0, 0, 0,  1,  0],
            [0, 0, 0, 0,  0,  1]
        ], dtype=np.float32)

        # Matrice de mesure H
        self.kf.measurementMatrix = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0]
        ], dtype=np.float32)

        # Covariances de bruit adaptatives (Position lissée R=25.0, Vitesse Q_v=10.0)
        Q = np.eye(6, dtype=np.float32) * 1.0
        Q[3, 3] = 10.0
        Q[4, 4] = 10.0
        Q[5, 5] = 10.0
        self.kf.processNoiseCov = Q
        self.kf.measurementNoiseCov = np.eye(3, dtype=np.float32) * 25.0
        self.kf.errorCovPost = np.eye(6, dtype=np.float32)
        
        self.is_initialized = False

    def reset(self):
        """Réinitialise l'état du filtre."""
        self.is_initialized = False

    def update(self, pos_3d):
        """
        Effectue une étape d'estimation et de correction avec la nouvelle mesure (x, y, z).
        Returns: (x_filtered, y_filtered, z_filtered)
        """
        meas = np.array([[np.float32(pos_3d[0])], [np.float32(pos_3d[1])], [np.float32(pos_3d[2])]], dtype=np.float32)

        if not self.is_initialized:
            self.kf.statePost = np.array([[meas[0][0]], [meas[1][0]], [meas[2][0]], [0], [0], [0]], dtype=np.float32)
            self.is_initialized = True
            return float(pos_3d[0]), float(pos_3d[1]), float(pos_3d[2])

        self.kf.predict()
        corrected = self.kf.correct(meas)
        return float(corrected[0][0]), float(corrected[1][0]), float(corrected[2][0])

    def predict_only(self):
        """
        Effectue une étape de prédiction sans nouvelle mesure (ex: occultation).
        Returns: (x_predicted, y_predicted, z_predicted)
        """
        if not self.is_initialized:
            return 0.0, 0.0, 0.0

        predicted = self.kf.predict()
        return float(predicted[0][0]), float(predicted[1][0]), float(predicted[2][0])

class ActiveGazeTracker:
    """
    Régulateur d'asservissement du cou avec filtre de Kalman 3D et prédiction de trajectoire.
    """
    def __init__(
        self,
        fov_h_deg=81.0,
        fov_v_deg=50.0,
        kp_pan=0.45,
        kp_tilt=0.45,
        deadband_pixels=15,
        max_predict_frames=5
    ):
        self.fov_h_deg = fov_h_deg
        self.fov_v_deg = fov_v_deg
        self.kp_pan = kp_pan
        self.kp_tilt = kp_tilt
        self.deadband_pixels = deadband_pixels
        self.max_predict_frames = max_predict_frames
        
        self.min_pan_deg = math.degrees(PAN_MIN_RAD)   # -80.0°
        self.max_pan_deg = math.degrees(PAN_MAX_RAD)   # +80.0°
        self.min_tilt_deg = math.degrees(TILT_MIN_RAD) # -20.0°
        self.max_tilt_deg = math.degrees(TILT_MAX_RAD) # +30.0°

        # Filtre de Kalman 3D
        self.kalman = GazeKalmanFilter3D()
        self.lost_frames_count = 0

    def compute_head_target(self, target_center_2d, frame_width, frame_height, current_pan_deg, current_tilt_deg, depth_z_mm=1000.0):
        """
        Calcule les nouvelles consignes angulaires (Pan, Tilt) après filtrage par Kalman 3D.
        
        target_center_2d : (cx, cy) en pixels
        Returns: (new_pan_deg, new_tilt_deg, is_centered)
        """
        cx_raw, cy_raw = target_center_2d
        
        # 1. Filtrage Kalman anti-jitter
        cx_filt, cy_filt, _ = self.kalman.update((cx_raw, cy_raw, depth_z_mm))

        center_x = frame_width / 2.0
        center_y = frame_height / 2.0

        error_x_px = cx_filt - center_x
        error_y_px = cy_filt - center_y  # En image OpenCV, Y va vers le bas

        self.lost_frames_count = 0

        # Zone morte centralisée
        if abs(error_x_px) < self.deadband_pixels and abs(error_y_px) < self.deadband_pixels:
            return current_pan_deg, current_tilt_deg, True

        # Conversion écart pixels -> delta angles en degrés
        deg_per_px_h = self.fov_h_deg / frame_width
        deg_per_px_v = self.fov_v_deg / frame_height

        delta_pan_deg = (error_x_px * deg_per_px_h) * self.kp_pan
        delta_tilt_deg = (-error_y_px * deg_per_px_v) * self.kp_tilt

        # 🚨 BRIDAGE HARDWARE ABSOLU : Ne peut JAMAIS dépasser les bornes de config.py
        new_pan_deg = max(self.min_pan_deg, min(self.max_pan_deg, current_pan_deg + delta_pan_deg))
        new_tilt_deg = max(self.min_tilt_deg, min(self.max_tilt_deg, current_tilt_deg + delta_tilt_deg))

        return new_pan_deg, new_tilt_deg, False

    def predict_lost_target(self, current_pan_deg, current_tilt_deg, frame_width=640, frame_height=360):
        """
        En cas de perte temporaire de la cible (ex: sortie rapide du champ de vision / occultation),
        utilise la prédiction du filtre de Kalman 3D pendant 'max_predict_frames' trames.
        
        Returns: (new_pan_deg, new_tilt_deg, is_predicting)
        """
        self.lost_frames_count += 1
        if self.lost_frames_count <= self.max_predict_frames and self.kalman.is_initialized:
            pred_cx, pred_cy, _ = self.kalman.predict_only()
            
            center_x = frame_width / 2.0
            center_y = frame_height / 2.0

            error_x_px = pred_cx - center_x
            error_y_px = pred_cy - center_y

            deg_per_px_h = self.fov_h_deg / frame_width
            deg_per_px_v = self.fov_v_deg / frame_height

            delta_pan_deg = (error_x_px * deg_per_px_h) * self.kp_pan
            delta_tilt_deg = (-error_y_px * deg_per_px_v) * self.kp_tilt

            new_pan_deg = max(self.min_pan_deg, min(self.max_pan_deg, current_pan_deg + delta_pan_deg))
            new_tilt_deg = max(self.min_tilt_deg, min(self.max_tilt_deg, current_tilt_deg + delta_tilt_deg))

            log.info(f"🔮 [Kalman 3D Predict] Poursuite par inertie (+{self.lost_frames_count} trames) -> Pan={new_pan_deg:+.1f}°")
            return new_pan_deg, new_tilt_deg, True

        return current_pan_deg, current_tilt_deg, False
