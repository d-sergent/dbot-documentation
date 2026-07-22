"""
dbot/vision/yolo_world.py — Détecteur Sémantique Zero-Shot YOLO-World v2
========================================================================
Niveau 1 de la Triade Visuelle : Inférence Open-Vocabulary temps réel.

Supporte la traduction automatique des prompts Français -> Anglais pour le modèle CLIP
d'OpenAI, tout en restituant des labels en Français dans les résultats de détection.
"""

import cv2
import numpy as np
import time
import os
import sys

# Dictionnaire de correspondance Français -> Anglais CLIP
FR_TO_EN_PROMPTS = {
    "main": "hand",
    "telephone": "mobile phone",
    "bouteille": "bottle",
    "personne": "person",
    "chaise": "chair",
    "obstacle": "obstacle",
    "escalier": "stairs",
    "verre": "glass",
    "stylo": "pen",
    "livre": "book"
}

# Dictionnaire inverse Anglais -> Français pour les logs
EN_TO_FR_PROMPTS = {v: k for k, v in FR_TO_EN_PROMPTS.items()}

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
        confidence_threshold=0.25,
        device=None
    ):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.user_classes_fr = classes or ["personne", "bouteille", "main", "telephone", "chaise", "obstacle"]
        self.model_classes_en = []
        
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
                    print("⚠ [YOLO-World] Pilote CUDA PyTorch non reconnu. Utilisation de 'cpu'.")
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
            
            # Application des classes personnalisées avec traduction Anglais CLIP
            self.set_classes(self.user_classes_fr)
            print(f"✅ [YOLO-World] Modèle prêt. Prompts CLIP Anglais : {self.model_classes_en}")
        except ImportError:
            print("⚠ [YOLO-World] 'ultralytics' non installé. Utilisation du mode Simulation.")
            self.model = None
        except Exception as e:
            print(f"⚠ [YOLO-World] Erreur d'initialisation modèle : {e}. Bascule en mode dégradé.")
            self.model = None

    def set_classes(self, classes_list_fr):
        """
        Met à jour à chaud la liste des requêtes textuelles.
        Convertit automatiquement les termes Français vers l'Anglais pour CLIP.
        """
        self.user_classes_fr = classes_list_fr
        # Traduction des requêtes pour CLIP
        self.model_classes_en = [FR_TO_EN_PROMPTS.get(c.lower().strip(), c.lower().strip()) for c in classes_list_fr]
        
        if self.model is not None:
            try:
                self.model.set_classes(self.model_classes_en)
                print(f"🎯 [YOLO-World] Requêtes CLIP (Anglais) : {self.model_classes_en}")
                print(f"🇫🇷 [YOLO-World] Prompts utilisateur (Français) : {self.user_classes_fr}")
            except Exception as e:
                print(f"⚠ [YOLO-World] Erreur mise à jour classes : {e}")

    def detect(self, frame):
        """
        Exécute la détection Zero-Shot sur une image OpenCV (BGR).
        
        Args:
            frame (ndarray): Image BGR numpy
            
        Returns:
            tuple: (liste de dict détections, latence en ms)
        """
        if frame is None:
            return [], 0.0

        t0 = time.perf_counter()
        detections = []

        if self.model is not None:
            try:
                results = self.model.predict(
                    frame,
                    conf=self.confidence_threshold,
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
                        
                        # Récupération du nom en Anglais puis traduction en Français pour l'utilisateur
                        raw_en_label = self.model_classes_en[cls_id] if cls_id < len(self.model_classes_en) else f"class_{cls_id}"
                        fr_label = EN_TO_FR_PROMPTS.get(raw_en_label, raw_en_label)

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
                    print(f"⚠ [YOLO-World] Rejet CUDA en prédiction. Bascule automatique sur CPU.")
                    self.device_name = "cpu"
                    return self.detect(frame)
                else:
                    print(f"⚠ [YOLO-World] Erreur inférence : {e}")
        else:
            # Mode Fallback / Simulation
            h, w = frame.shape[:2]
            detections.append({
                "label": self.user_classes_fr[0] if self.user_classes_fr else "objet",
                "confidence": 0.92,
                "bbox": (int(w*0.3), int(h*0.3), int(w*0.7), int(h*0.7)),
                "center": (int(w*0.5), int(h*0.5))
            })

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        return detections, latency_ms

    def annotate_frame(self, frame, detections):
        """
        Dessine les bboxes 2D, étiquettes et confiances sur l'image pour prévisualisation.
        """
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

if __name__ == "__main__":
    print("🚀 Test Unitaire : dbot.vision.yolo_world (Mappage CLIP Anglais/Français)")
    detector = YoloWorldDetector(confidence_threshold=0.25)
    
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(dummy_frame, "D-Bot Vision Test", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    detections, latence = detector.detect(dummy_frame)
    print(f"📊 Détections ({latence:.2f} ms) : {detections}")
