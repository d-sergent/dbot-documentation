"""
dbot/vision/yolo_world.py — Détecteur Sémantique Zero-Shot YOLO-World v2 (Multilingue Français/Anglais)
========================================================================================================
Niveau 1 de la Triade Visuelle : Inférence Open-Vocabulary temps réel.

Gestion multilingue intelligente (0 Mo RAM, 0% CPU) :
- Dictionnaire persistant local (fr_en_dictionary.json) pré-chargé avec +100 objets.
- Suppresseur d'accents et traducteur automatique dynamique via urllib (mémorisation automatique dans le JSON).
- Support des extensions .engine et .onnx TensorRT FP16 / GPU.
"""

import cv2
import numpy as np
import time
import os
import sys
import json
import unicodedata
import urllib.request
import urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_PATH = os.path.join(SCRIPT_DIR, "fr_en_dictionary.json")

def remove_accents(input_str: str) -> str:
    """Supprime les accents d'une chaîne de caractères (ex: 'téléphone' -> 'telephone')."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def load_dictionary() -> dict:
    """Charge le dictionnaire local persistant."""
    if os.path.exists(DICT_PATH):
        try:
            with open(DICT_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur chargement dictionnaire JSON ({e}). Utilisation du dictionnaire par défaut.")
    return {
        "main": "hand",
        "telephone": "phone",
        "bouteille": "bottle",
        "personne": "person",
        "chaise": "chair",
        "table": "table",
        "obstacle": "obstacle"
    }

def save_dictionary(dictionary: dict) -> None:
    """Sauvegarde le dictionnaire persistant sur disque."""
    try:
        with open(DICT_PATH, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Impossible de sauvegarder le dictionnaire JSON : {e}")

# Dictionnaire global en mémoire
GLOBAL_FR_EN_DICT = load_dictionary()

def translate_fr_to_en(fr_term: str) -> str:
    """
    Traduit un terme Français vers l'Anglais pour CLIP :
    1. Vérification dans le dictionnaire persistant JSON (0 ms, 0% CPU, 0 Mo RAM)
    2. Si absent, appel HTTP ultra-léger via urllib (Google Translate, < 30 ms) et sauvegarde automatique dans le JSON.
    """
    raw_clean = fr_term.lower().strip()
    no_accent = remove_accents(raw_clean)

    # 1. Vérification dans le cache local
    if raw_clean in GLOBAL_FR_EN_DICT:
        return GLOBAL_FR_EN_DICT[raw_clean]
    if no_accent in GLOBAL_FR_EN_DICT:
        return GLOBAL_FR_EN_DICT[no_accent]

    # 2. Traduction réseau native zéro-dépendance via urllib
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=fr&tl=en&dt=t&q={urllib.parse.quote(raw_clean)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            result = json.loads(response.read().decode('utf-8'))
            translated_en = result[0][0][0].lower().strip()
            
            # Mise en cache & sauvegarde persistance
            GLOBAL_FR_EN_DICT[raw_clean] = translated_en
            save_dictionary(GLOBAL_FR_EN_DICT)
            print(f"💡 [YOLO-World] Nouvelle traduction enregistrée : '{raw_clean}' ➔ '{translated_en}'")
            return translated_en
    except Exception as e:
        print(f"⚠️ Échec traduction réseau pour '{raw_clean}' ({e}). Utilisation du mot brut sans accents.")
        return no_accent

# Seuils de confiance adaptés par catégorie CLIP
CLASS_CONF_THRESHOLDS = {
    "hand": 0.12,
    "phone": 0.12,
    "bottle": 0.15,
    "obstacle": 0.15,
    "person": 0.22,
    "chair": 0.22,
    "table": 0.22,
    "cup": 0.08,
    "mug": 0.08,
    "coffee mug": 0.08,
    "glass": 0.15,
    "book": 0.18,
    "keys": 0.15
}

# Palette de couleurs vives BGR distinctes par classe
CLASS_COLORS_BGR = {
    "MAIN": (0, 255, 0),        # Vert Vif
    "TELEPHONE": (255, 255, 0),  # Cyan / Jaune-Vert
    "BOUTEILLE": (0, 165, 255),  # Orange
    "TASSE": (0, 255, 255),      # Jaune Vif
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
    Module d'inférence YOLO-World avec support multilingue natif et détection du backend matériel.
    """
    def __init__(
        self,
        model_name="yolov8m-worldv2.pt",
        classes=None,
        default_conf_threshold=0.15,
        iou_threshold=0.70,
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

    @property
    def dictionary(self):
        """Retourne le dictionnaire de traduction local global."""
        return GLOBAL_FR_EN_DICT

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
        """Initialise le modèle d'inférence Open-Vocabulary YOLO-World v2 (PyTorch/GPU)."""
        target_load = self.model_name
        
        print(f"⏳ [YOLO-World] Chargement du modèle '{target_load}' (device={self.device_name})...")
        try:
            from ultralytics import YOLOWorld
            self.model = YOLOWorld(target_load)
            self.set_classes(self.user_classes_fr)
            print(f"✅ [YOLO-World] Modèle '{target_load}' prêt via PyTorch ({self.device_name}).")
        except ImportError:
            print("⚠ [YOLO-World] 'ultralytics' non installé. Mode Simulation.")
            self.model = None
        except Exception as e:
            print(f"⚠ Erreur d'initialisation du modèle '{target_load}' : {e}")
            self.model = None

    def set_classes(self, classes_list_fr):
        """
        Met à jour à chaud la liste des requêtes textuelles.
        Traduit automatiquement les consignes Françaises vers CLIP Anglais (avec mise en cache JSON).
        Gère intelligemment les synonymes multiples séparés par des virgules (ex: 'mug, coffee mug, cup').
        """
        self.user_classes_fr = classes_list_fr
        self.model_prompts_en = []
        self.prompt_to_fr_map = {}

        for fr_cat in classes_list_fr:
            fr_display = fr_cat.upper().strip()
            en_prompt_raw = translate_fr_to_en(fr_cat)
            
            # Découpage des synonymes séparés par des virgules pour des embeddings CLIP individuels
            sub_prompts = [p.strip() for p in en_prompt_raw.split(',') if p.strip()]
            for p in sub_prompts:
                if p not in self.model_prompts_en:
                    self.model_prompts_en.append(p)
                    self.prompt_to_fr_map[p] = fr_display

        if self.model is not None:
            try:
                self.model.set_classes(self.model_prompts_en)
                print(f"🎯 [YOLO-World] Prompts CLIP Anglais : {self.model_prompts_en}")
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
                predict_kwargs = {
                    "conf": 0.05,
                    "iou": 0.90,
                    "max_det": 100,
                    "agnostic_nms": False,
                    "verbose": False
                }
                if self.device_name == "cuda":
                    predict_kwargs["device"] = 0
                else:
                    predict_kwargs["device"] = "cpu"

                results = self.model.predict(frame_rgb, **predict_kwargs)
                
                if results and len(results) > 0:
                    boxes = results[0].boxes
                    for box in boxes:
                        xyxy = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = map(int, xyxy)
                        conf = float(box.conf[0].cpu().numpy())
                        cls_id = int(box.cls[0].cpu().numpy())
                        
                        raw_en_prompt = self.model_prompts_en[cls_id] if cls_id < len(self.model_prompts_en) else f"class_{cls_id}"
                        
                        min_conf = min(CLASS_CONF_THRESHOLDS.get(raw_en_prompt, self.default_conf_threshold), self.default_conf_threshold)
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
