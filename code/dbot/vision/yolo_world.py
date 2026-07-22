"""
dbot/vision/yolo_world.py — Détecteur Sémantique Zero-Shot YOLO-World v2
========================================================================
Niveau 1 de la Triade Visuelle : Inférence Open-Vocabulary temps réel.

Support Multi-Boîtes & Visualisation Multi-Couleurs :
- Palette BGR distincte par classe (MAIN, TELEPHONE, BOUTEILLE, PERSONNE, TABLE, CHAISE, OBSTACLE).
- NMS non-agnostique autorisant le chevauchement et l'imbrication des boîtes multi-classes (agnostic_nms=False).
"""

import cv2
import numpy as np
import time
import os
import sys

# Mappage strict 1-to-1 Français <-> Anglais CLIP
FR_TO_EN_CLASS = {
    "main": "hand",
    "telephone": "phone",
    "bouteille": "bottle",
    "personne": "person",
    "chaise": "chair",
    "table": "table",
    "obstacle": "obstacle"
}

EN_TO_FR_CLASS = {v: k.upper() for k, v in FR_TO_EN_CLASS.items()}

# Seuils de confiance adaptés par catégorie CLIP
CLASS_CONF_THRESHOLDS = {
    "hand": 0.20,
    "phone": 0.20,
    "bottle": 0.25,
    "obstacle": 0.25,
    "person": 0.35,
    "chair": 0.35,
    "table": 0.32
}

# Palette de couleurs vives BGR distinctes par classe
CLASS_COLORS_BGR = {
    "MAIN": (0, 255, 0),        # Vert Vif
    "TELEPHONE": (255, 255, 0),  # Cyan / Jaune-Vert
    "BOUTEILLE": (0, 165, 255),  # Orange
    "PERSONNE": (255, 100, 0),   # Bleu Électrique
    "TABLE": (255, 0, 180),      # Rose / Violet
    "CHAISE": (180, 50, 255),    # Magenta
    "OBSTACLE": (0, 0, 255)      # Rouge Vif
}
DEFAULT_COLOR = (200, 200, 200)

class YoloWorldError(Exception):
    """Erreur personnalisée pour le module YOLO-World."""
    pass

class YoloWorldDetector:
    """
    Module d'inférence YOLO-World pour la détection Zero-Shot / Open-Vocabulary.
    """
    def __init__(
        self,
        model_name="yolov8s-worldv2.pt",
        classes=None,
        default_conf_threshold=0.22,
        iou_threshold=0.45,
        device=None
    ):
        self.model_name = model_name
        self.default_conf_threshold = default_conf_threshold
        self.iou_threshold = iou_threshold
        self.model = None
        self.user_classes_fr = classes or ["main", "telephone", "bouteille", "personne", "table", "chaise", "obstacle"]
        
        self.model_prompts_en = []
        self.prompt_to_fr_map = {}
        
        self.device_name = device or self._detect_best_device()
        self._init_model()

    def _detect_best_device(self):
        """Détermine le meilleur device disponible (CUDA vs CPU)."""
        try:
            import torch
            if torch.cuda.is_available():
                try:
                    _ = torch.zeros(1).cuda()
                    return "cuda"
                except Exception:
                    return "cpu"
            else:
                return "cpu"
        except Exception:
            return "cpu"

    def _init_model(self):
        """Initialise le modèle d'inférence YOLO-World."""
        print(f"⏳ [YOLO-World] Initialisation du modèle '{self.model_name}' sur {self.device_name}...")
        try:
            from ultralytics import YOLOWorld
            self.model = YOLOWorld(self.model_name)
            self.set_classes(self.user_classes_fr)
            print(f"✅ [YOLO-World] Modèle prêt sur {self.device_name}.")
        except ImportError:
            print("⚠ [YOLO-World] 'ultralytics' non installé. Mode Simulation.")
            self.model = None
        except Exception as e:
            print(f"⚠ Erreur d'initialisation modèle : {e}")
            self.model = None

    def set_classes(self, classes_list_fr):
        """
        Met à jour à chaud la liste des requêtes textuelles.
        Convertit automatiquement en prompts Anglais uniques 1-to-1 pour CLIP.
        """
        self.user_classes_fr = classes_list_fr
        self.model_prompts_en = []
        self.prompt_to_fr_map = {}

        for fr_cat in classes_list_fr:
            cat_key = fr_cat.lower().strip()
            en_prompt = FR_TO_EN_CLASS.get(cat_key, cat_key)
            if en_prompt not in self.model_prompts_en:
                self.model_prompts_en.append(en_prompt)
                self.prompt_to_fr_map[en_prompt] = EN_TO_FR_CLASS.get(en_prompt, fr_cat.upper())

        if self.model is not None:
            try:
                self.model.set_classes(self.model_prompts_en)
                print(f"🎯 [YOLO-World] Prompts CLIP Anglais Nettes : {self.model_prompts_en}")
                print(f"🇫🇷 [YOLO-World] Mappage Français : {self.prompt_to_fr_map}")
            except Exception as e:
                print(f"⚠ Erreur mise à jour classes : {e}")

    def detect(self, frame_bgr):
        """
        Exécute la détection Zero-Shot sur une image BGR OpenCV avec conversion RGB.
        """
        if frame_bgr is None:
            return [], 0.0

        t0 = time.perf_counter()
        detections = []

        # Conversion BGR -> RGB pour corriger la vision des couleurs par l'IA CLIP
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        if self.model is not None:
            try:
                results = self.model.predict(
                    frame_rgb,
                    conf=0.18,
                    iou=self.iou_threshold,
                    agnostic_nms=False, # Argument Ultralytics exact pour NMS non-agnostique
                    device=self.device_name,
                    verbose=False
                )
                
                if results and len(results) > 0:
                    boxes = results[0].boxes
                    for box in boxes:
                        xyxy = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = map(int, xyxy)
                        conf = float(box.conf[0].cpu().numpy())
                        cls_id = int(box.cls[0].cpu().numpy())
                        
                        raw_en_prompt = self.model_prompts_en[cls_id] if cls_id < len(self.model_prompts_en) else f"class_{cls_id}"
                        
                        min_conf = CLASS_CONF_THRESHOLDS.get(raw_en_prompt, self.default_conf_threshold)
                        if conf < min_conf:
                            continue

                        fr_label = self.prompt_to_fr_map.get(raw_en_prompt, raw_en_prompt.upper())

                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)

                        detections.append({
                            "label": fr_label,
                            "raw_label_en": raw_en_prompt,
                            "confidence": conf,
                            "bbox": (x1, y1, x2, y2),
                            "center": (cx, cy)
                        })
            except Exception as e:
                if "CUDA" in str(e) and self.device_name != "cpu":
                    self.device_name = "cpu"
                    return self.detect(frame_bgr)
                else:
                    print(f"⚠ Erreur inférence : {e}")
        else:
            h, w = frame_bgr.shape[:2]
            detections.append({
                "label": self.user_classes_fr[0].upper() if self.user_classes_fr else "OBJET",
                "raw_label_en": "hand",
                "confidence": 0.92,
                "bbox": (int(w*0.3), int(h*0.3), int(w*0.7), int(h*0.7)),
                "center": (int(w*0.5), int(h*0.5))
            })

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        return detections, latency_ms

    def annotate_frame(self, frame, detections):
        """
        Dessine les bboxes 2D avec des couleurs distinctes par classe et bannières colorées.
        """
        annotated = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            label = det["label"]
            conf = det["confidence"]
            cx, cy = det["center"]

            color = CLASS_COLORS_BGR.get(label.upper(), DEFAULT_COLOR)

            # 1. Rectangle Bounding Box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.circle(annotated, (cx, cy), 4, (0, 0, 255), -1)

            # 2. Bannière de fond colorée pour le texte
            text = f"{label} {conf*100:.0f}%"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.55
            thickness = 2
            
            (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            
            banner_y1 = max(0, y1 - text_h - 8)
            banner_y2 = max(text_h + 8, y1)
            
            # Fond opaque de la couleur de la classe
            cv2.rectangle(annotated, (x1, banner_y1), (x1 + text_w + 10, banner_y2), color, -1)
            
            # Texte blanc en contraste
            cv2.putText(
                annotated, text, (x1 + 5, banner_y2 - 5),
                font, font_scale, (255, 255, 255), thickness
            )

        return annotated
