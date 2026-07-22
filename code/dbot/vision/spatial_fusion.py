"""
dbot/vision/spatial_fusion.py — Fusion Spatiale 2D ➔ 3D pour OAK-D & YOLO
========================================================================
Associe les Bounding Boxes 2D produites par YOLO-World v2 avec la carte de
profondeur stéréo d'OAK-D Pro pour obtenir la position tridimensionnelle
physique (X, Y, Z) en millimètres de n'importe quel objet repéré.
"""

import numpy as np
import math

class SpatialFusion:
    """
    Calculateur de géométrie spatiale 3D à partir d'une carte de profondeur et de Bounding Boxes 2D.
    """
    def __init__(self, hfov_deg=69.0, vfov_deg=55.0):
        self.hfov_rad = math.radians(hfov_deg)
        self.vfov_rad = math.radians(vfov_deg)

    def compute_spatial_3d(self, detections_2d, depth_frame):
        """
        Calcule les coordonnées 3D (X, Y, Z) en mm pour chaque détection 2D.
        
        Args:
            detections_2d (list of dict): Détections avec 'bbox': (x1, y1, x2, y2)
            depth_frame (ndarray): Carte de profondeur numpy uint16 en mm
            
        Returns:
            list of dict: Détections enrichies avec 'spatial_3d': {'x_mm', 'y_mm', 'z_mm'}
        """
        if depth_frame is None or len(detections_2d) == 0:
            return detections_2d

        h_img, w_img = depth_frame.shape
        
        # Focales virtuelles d'après le Champ de Vision (FOV)
        fx = w_img / (2.0 * math.tan(self.hfov_rad / 2.0))
        fy = h_img / (2.0 * math.tan(self.vfov_rad / 2.0))
        cx_img = w_img / 2.0
        cy_img = h_img / 2.0

        enriched_detections = []

        for det in detections_2d:
            det_copy = dict(det)
            x1, y1, x2, y2 = det["bbox"]

            # Clamp aux limites de l'image
            x1_c = max(0, min(w_img - 1, x1))
            x2_c = max(0, min(w_img - 1, x2))
            y1_c = max(0, min(h_img - 1, y1))
            y2_c = max(0, min(h_img - 1, y2))

            roi_depth = depth_frame[y1_c:y2_c, x1_c:x2_c]
            valid_depths = roi_depth[roi_depth > 0]

            if len(valid_depths) > 0:
                z_mm = float(np.median(valid_depths))
            else:
                z_mm = 0.0

            # Calcul des coordonnées physiques X, Y (Repère Caméra : X vers la droite, Y vers le bas, Z vers l'avant)
            cx_box, cy_box = det["center"]
            x_mm = (cx_box - cx_img) * z_mm / fx if z_mm > 0 else 0.0
            y_mm = (cy_box - cy_img) * z_mm / fy if z_mm > 0 else 0.0

            det_copy["spatial_3d"] = {
                "x_mm": round(x_mm, 1),
                "y_mm": round(y_mm, 1),
                "z_mm": round(z_mm, 1)
            }

            enriched_detections.append(det_copy)

        return enriched_detections

if __name__ == "__main__":
    print("🚀 Test Unitaire : dbot.vision.spatial_fusion")
    fusion = SpatialFusion()
    
    # Carte de profondeur synthétique (480x640, remplie avec 1500 mm = 1.5m)
    dummy_depth = np.full((480, 640), 1500, dtype=np.uint16)
    
    dummy_dets = [
        {"label": "bouteille", "confidence": 0.85, "bbox": (200, 150, 280, 350), "center": (240, 250)},
        {"label": "personne", "confidence": 0.91, "bbox": (400, 100, 550, 400), "center": (475, 250)}
    ]

    results = fusion.compute_spatial_3d(dummy_dets, dummy_depth)
    for r in results:
        s = r["spatial_3d"]
        print(f"🎯 Obj '{r['label']}' -> 3D Spatiale: X={s['x_mm']}mm, Y={s['y_mm']}mm, Z={s['z_mm']}mm")
