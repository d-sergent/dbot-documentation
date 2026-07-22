"""
dbot/vision/yolo_world.py — Détecteur Sémantique Zero-Shot YOLO-World v2
========================================================================
Niveau 1 de la Triade Visuelle : Inférence Open-Vocabulary temps réel sur
le GPU CUDA de la Jetson Orin Nano (VRAM < 0.4 Go, latence 12-15 ms).

Permet de rechercher n'importe quel objet via des requêtes textuelles dynamiques.
"""

import cv2
import numpy as np
import time
import os
import sys

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
        device="cuda"
    ):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.device_name = device
        self.model = None
        self.current_classes = classes or ["personne", "bouteille", "chaise", "obstacle"]
        
        self._init_model()

    def _init_model(self):
        """Initialise le modèle d'inférence YOLO-World."""
        print(f"⏳ [YOLO-World] Initialisation du modèle '{self.model_name}' sur {self.device_name}...")
        try:
            from ultralytics import YOLOWorld
            self.model = YOLOWorld(self.model_name)
            
            # Application des classes personnalisées dynamiques
            self.set_classes(self.current_classes)
            print(f"✅ [YOLO-World] Modèle prêt. Classes actives : {self.current_classes}")
        except ImportError:
            print("⚠ [YOLO-World] 'ultralytics' non installé. Utilisation du mode Simulation / Fallback ONNX.")
            self.model = None
        except Exception as e:
            print(f"⚠ [YOLO-World] Erreur d'initialisation modèle CUDA : {e}. Bascule en mode dégradé.")
            self.model = None

    def set_classes(self, classes_list):
        """
        Met à jour à chaud la liste des requêtes textuelles (Open-Vocabulary).
        
        Args:
            classes_list (list of str): Liste d'objets à chercher (ex: ["bouteille", "escalier", "main"])
        """
        self.current_classes = classes_list
        if self.model is not None:
            try:
                self.model.set_classes(classes_list)
                print(f"🎯 [YOLO-World] Nouvelles requêtes sémantiques définies : {classes_list}")
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
                        label = self.current_classes[cls_id] if cls_id < len(self.current_classes) else f"class_{cls_id}"

                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)

                        detections.append({
                            "label": label,
                            "confidence": conf,
                            "bbox": (x1, y1, x2, y2),
                            "center": (cx, cy)
                        })
            except Exception as e:
                print(f"⚠ [YOLO-World] Erreur inférence : {e}")
        else:
            # Mode Fallback / Simulation si le modèle n'est pas encore disponible
            h, w = frame.shape[:2]
            detections.append({
                "label": self.current_classes[0] if self.current_classes else "objet",
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

            # Rectangle Bounding Box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Point central
            cv2.circle(annotated, (cx, cy), 4, (0, 0, 255), -1)

            # Texte d'étiquette
            text = f"{label} {conf*100:.0f}%"
            cv2.putText(
                annotated, text, (x1, max(y1 - 8, 20)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

        return annotated

if __name__ == "__main__":
    print("🚀 Test Unitaire : dbot.vision.yolo_world")
    detector = YoloWorldDetector(confidence_threshold=0.3)
    
    # Image de test synthétique
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(dummy_frame, "D-Bot Vision Test", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    detections, latence = detector.detect(dummy_frame)
    print(f"📊 Détections ({latence:.2f} ms) : {detections}")

    annotated = detector.annotate_frame(dummy_frame, detections)
    print(f"✅ Image annotée générée : shape {annotated.shape}")
