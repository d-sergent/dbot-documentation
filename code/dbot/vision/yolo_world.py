"""
dbot/vision/yolo_world.py — Détecteur Sémantique Zero-Shot YOLO-World v2
========================================================================
Niveau 1 de la Triade Visuelle : Inférence Open-Vocabulary temps réel.

Incorpore la gestion du NMS imbriqué (iou=0.35) pour isoler les objets tenus en main,
ainsi que l'ajout des catégories de mobilier (table, meuble) pour éviter les fausses
classifications de chaises.
"""

import cv2
import numpy as np
import time
import os
import sys

# Dictionnaire de correspondance Français -> Ensembles de Prompts CLIP Descriptifs en Anglais
FR_TO_CLIP_ENSEMBLES = {
    "main": ["human hand", "open hand", "hand holding an object", "forearm"],
    "telephone": ["smartphone", "mobile phone", "cell phone", "holding a phone", "phone screen"],
    "bouteille": ["water bottle", "plastic bottle", "bottle"],
    "table": ["table", "coffee table", "wooden table", "desk"],
    "personne": ["person", "human body", "human"],
    "chaise": ["chair", "armchair", "sofa"],
    "obstacle": ["obstacle", "barrier"]
}

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
        confidence_threshold=0.35,
        iou_threshold=0.35,
        device=None
    ):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.model = None
        self.user_classes_fr = classes or ["main", "telephone", "bouteille", "table", "personne", "chaise", "obstacle"]
        
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
        Génère un ensemble de prompts Anglais descriptifs pour CLIP.
        """
        self.user_classes_fr = classes_list_fr
        self.model_prompts_en = []
        self.prompt_to_fr_map = {}

        for fr_cat in classes_list_fr:
            cat_key = fr_cat.lower().strip()
            descriptors = FR_TO_CLIP_ENSEMBLES.get(cat_key, [cat_key])
            for desc in descriptors:
                self.model_prompts_en.append(desc)
                self.prompt_to_fr_map[desc] = fr_cat.upper()

        if self.model is not None:
            try:
                self.model.set_classes(self.model_prompts_en)
                print(f"🎯 [YOLO-World] Ensembles de prompts CLIP Anglais ({len(self.model_prompts_en)}) : {self.model_prompts_en}")
                print(f"🇫🇷 [YOLO-World] Prompts utilisateur (Français) : {self.user_classes_fr}")
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
                    conf=self.confidence_threshold,
                    iou=self.iou_threshold, # Permet aux objets tenus en main de ne pas être supprimés
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
                        fr_label = self.prompt_to_fr_map.get(raw_en_prompt, raw_en_prompt.upper())

                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)

                        detections.append({
                            "label": fr_label,
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
                "confidence": 0.92,
                "bbox": (int(w*0.3), int(h*0.3), int(w*0.7), int(h*0.7)),
                "center": (int(w*0.5), int(h*0.5))
            })

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        return detections, latency_ms

    def annotate_frame(self, frame, detections):
        annotated = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            label = det["label"]
            conf = det["confidence"]
            cx, cy = det["center"]

            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(annotated, (cx, cy), 4, (0, 0, 255), -1)

            text = f"{label} {conf*100:.0f}%"
            cv2.putText(
                annotated, text, (x1, max(y1 - 8, 20)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

        return annotated
