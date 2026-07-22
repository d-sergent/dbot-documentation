"""
dbot/behaviors/active_gaze.py — Boucle d'Asservissement du Regard (Active Gaze Tracker)
====================================================================================
Gère l'asservissement visuel du cou (Pan ID:1 & Tilt ID:2) pour orienter la tête du robot
et maintenir un objet ciblé au centre exact du champ de vision grand angle (81° FOV).

Fonctionnalités :
- Régulateur angulaire proportionnel avec zone morte centralisée (Deadband).
- Conversion de l'écart pixel 2D en delta d'angles Pan/Tilt (FOV H: 81°, FOV V: 50°).
- Interfaçage avec DbotCamera, YoloWorldDetector, SpatialFusion et NeckController.
"""

import cv2
import numpy as np
import time
import math
import logging

log = logging.getLogger('active_gaze')

class ActiveGazeTracker:
    """
    Régulateur d'asservissement du cou pour le recentrage visuel dynamique.
    """
    def __init__(
        self,
        fov_h_deg=81.0,
        fov_v_deg=50.0,
        kp_pan=0.35,
        kp_tilt=0.35,
        deadband_pixels=20
    ):
        self.fov_h_deg = fov_h_deg
        self.fov_v_deg = fov_v_deg
        self.kp_pan = kp_pan
        self.kp_tilt = kp_tilt
        self.deadband_pixels = deadband_pixels
        
        self.current_pan_deg = 0.0
        self.current_tilt_deg = 0.0

    def compute_head_target(self, target_center_2d, frame_width, frame_height, current_pan_deg, current_tilt_deg):
        """
        Calcule les nouvelles consignes angulaires (Pan, Tilt) pour recentrer la cible.
        
        target_center_2d : (cx, cy) en pixels
        Returns: (new_pan_deg, new_tilt_deg, is_centered)
        """
        cx, cy = target_center_2d
        center_x = frame_width / 2.0
        center_y = frame_height / 2.0

        error_x_px = cx - center_x
        error_y_px = cy - center_y  # En image OpenCV, Y va vers le bas

        # Zone morte centralisée
        if abs(error_x_px) < self.deadband_pixels and abs(error_y_px) < self.deadband_pixels:
            return current_pan_deg, current_tilt_deg, True

        # Conversion écart pixels -> delta angles en degrés
        # Un décalage X positif (objet à droite) nécessite de tourner la tête vers la droite (+Pan)
        # Un décalage Y positif (objet en bas) nécessite d'incliner la tête vers le bas (-Tilt)
        deg_per_px_h = self.fov_h_deg / frame_width
        deg_per_px_v = self.fov_v_deg / frame_height

        delta_pan_deg = (error_x_px * deg_per_px_h) * self.kp_pan
        delta_tilt_deg = (-error_y_px * deg_per_px_v) * self.kp_tilt

        new_pan_deg = current_pan_deg + delta_pan_deg
        new_tilt_deg = current_tilt_deg + delta_tilt_deg

        return new_pan_deg, new_tilt_deg, False
