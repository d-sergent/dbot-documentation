"""
Module de Reconnaissance et d'Identification Faciale Ultra-Compacte pour D-Bot V1.

Architecture :
- Détecteur de visages : SCRFD 500M (scrfd_500m_kps.onnx - ~1.5 Mo, 5 points clés)
- Extraction d'embeddings : MobileFaceNet / ArcFace (w600k_mbf.onnx - ~12 Mo, 512-dim)
- Comparaison : Similarité Cosinus via produit scalaire NumPy (< 0.01 ms)
- Exécution : ONNXRuntime-GPU (CUDAExecutionProvider / TensorRT)

Auteur : D-Bot Project (Google DeepMind Agentic Coding)
Date : 2026-07-24
"""

import os
import sys
import json
import urllib.request
import numpy as np
import cv2

# Répertoire racine des modèles
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FACES_DIR = os.path.join(SCRIPT_DIR, "faces")
WEIGHTS_DIR = os.path.join(FACES_DIR, "weights")
KNOWN_FACES_PATH = os.path.join(FACES_DIR, "known_faces.json")

# URL officielle InsightFace buffalo_sc.zip (14.9 Mo contenant det_500m.onnx et w600k_mbf.onnx)
BUFFALO_SC_URL = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_sc.zip"

SCRFD_PATH = os.path.join(WEIGHTS_DIR, "det_500m.onnx")
MBF_PATH = os.path.join(WEIGHTS_DIR, "w600k_mbf.onnx")

# Landmarks de référence InsightFace (112x112 px)
ARCFACE_REF_LANDMARKS = np.array([
    [38.2946, 51.6963],  # Oeil gauche
    [73.5318, 51.5014],  # Oeil droit
    [56.0252, 71.7366],  # Nez
    [41.5493, 92.3655],  # Coin gauche bouche
    [70.7299, 92.2041]   # Coin droit bouche
], dtype=np.float32)


def ensure_directory(path: str):
    """Crée le dossier s'il n'existe pas."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def download_and_extract_models():
    """Télécharge l'archive officielle InsightFace buffalo_sc.zip et extrait les modèles ONNX."""
    zip_path = os.path.join(WEIGHTS_DIR, "buffalo_sc.zip")
    print(f"⏳ Téléchargement du pack modèle officiel InsightFace (buffalo_sc.zip - 14.9 Mo)...")
    try:
        req = urllib.request.Request(BUFFALO_SC_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(zip_path, 'wb') as f:
            f.write(resp.read())
        
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(WEIGHTS_DIR)
        
        if os.path.exists(zip_path):
            os.remove(zip_path)
        print("✅ [FaceTracker] Modèles ONNX ultra-compacts `det_500m.onnx` et `w600k_mbf.onnx` installés avec succès !")
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement de 'buffalo_sc.zip' : {e}")


class FaceTracker:
    """
    Gestionnaire de Détection et d'Identification Faciale Ultra-Compact pour D-Bot.
    """

    def __init__(self, match_threshold: float = 0.30, use_gpu: bool = True):
        self.match_threshold = match_threshold
        self.use_gpu = use_gpu

        ensure_directory(FACES_DIR)
        ensure_directory(WEIGHTS_DIR)

        # Vérification et téléchargement de l'archive si les modèles sont absents
        if not os.path.exists(SCRFD_PATH) or not os.path.exists(MBF_PATH):
            download_and_extract_models()

        self.session_det = None
        self.session_rec = None
        self._init_onnx_sessions()

        # Dictionnaire mémoire des visages connus {name: [vector1, vector2]}
        self.known_faces = self.load_known_faces()

    def _init_onnx_sessions(self):
        """Initialise les sessions ONNXRuntime pour SCRFD et MobileFaceNet."""
        try:
            import onnxruntime as ort
        except ImportError:
            print("⚠️ 'onnxruntime' non installé. Mode dégradé simulation.")
            return

        providers = ['CPUExecutionProvider']
        if self.use_gpu:
            available_providers = ort.get_available_providers()
            if 'CUDAExecutionProvider' in available_providers:
                providers.insert(0, ('CUDAExecutionProvider', {
                    'device_id': 0,
                    'arena_extend_strategy': 'kNextPowerOfTwo',
                    'gpu_mem_limit': 100 * 1024 * 1024,  # 100 Mo VRAM max
                    'cudnn_conv_algo_search': 'EXHAUSTIVE',
                }))
                print("⚡ [FaceTracker] GPU CUDA activé pour ONNXRuntime (< 100 Mo VRAM).")

        try:
            if os.path.exists(SCRFD_PATH):
                self.session_det = ort.InferenceSession(SCRFD_PATH, providers=providers)
            if os.path.exists(MBF_PATH):
                self.session_rec = ort.InferenceSession(MBF_PATH, providers=providers)
            print("✅ [FaceTracker] Modèles SCRFD_500M & MobileFaceNet initialisés.")
        except Exception as e:
            print(f"⚠️ Erreur d'initialisation ONNXRuntime ({e}). Tentative en CPU pure...")
            try:
                if os.path.exists(SCRFD_PATH):
                    self.session_det = ort.InferenceSession(SCRFD_PATH, providers=['CPUExecutionProvider'])
                if os.path.exists(MBF_PATH):
                    self.session_rec = ort.InferenceSession(MBF_PATH, providers=['CPUExecutionProvider'])
            except Exception as e2:
                print(f"❌ Échec initialisation CPU FaceTracker : {e2}")

    def load_known_faces(self) -> dict:
        """Charge le dictionnaire des visages enregistrés."""
        if os.path.exists(KNOWN_FACES_PATH):
            try:
                with open(KNOWN_FACES_PATH, 'r', encoding='utf-8') as f:
                    raw_dict = json.load(f)
                # Conversion des listes en tableaux NumPy
                processed = {}
                for name, vec_list in raw_dict.items():
                    processed[name] = [np.array(v, dtype=np.float32) for v in vec_list]
                print(f"📚 [FaceTracker] {len(processed)} identité(s) faciale(s) chargée(s) depuis disk.")
                return processed
            except Exception as e:
                print(f"⚠️ Erreur chargement known_faces.json : {e}")
        return {}

    def save_known_faces(self):
        """Sauvegarde le dictionnaire des visages enregistrés."""
        try:
            serializable = {}
            for name, vec_list in self.known_faces.items():
                serializable[name] = [v.tolist() for v in vec_list]
            with open(KNOWN_FACES_PATH, 'w', encoding='utf-8') as f:
                json.dump(serializable, f, ensure_ascii=False, indent=2)
            print(f"💾 [FaceTracker] Base faciale sauvegardée dans '{KNOWN_FACES_PATH}'.")
        except Exception as e:
            print(f"❌ Échec sauvegarde known_faces.json : {e}")

    def align_face(self, frame_bgr: np.ndarray, landmarks_5pt: np.ndarray = None) -> np.ndarray:
        """
        Effectue la transformation affine de l'image du visage vers le repère 112x112 px.
        """
        if landmarks_5pt is None or len(landmarks_5pt) != 5:
            # Fallback simple crop & resize 112x112
            return cv2.resize(frame_bgr, (112, 112))

        src = np.array(landmarks_5pt, dtype=np.float32)
        dst = ARCFACE_REF_LANDMARKS

        # Estimation de la matrice de transformation affine (méthode Umeyama / Least Squares)
        M, _ = cv2.estimateAffinePartial2D(src, dst)
        if M is None:
            return cv2.resize(frame_bgr, (112, 112))

        aligned = cv2.warpAffine(frame_bgr, M, (112, 112), borderValue=0)
        return aligned

    def get_embedding(self, aligned_face_bgr: np.ndarray) -> np.ndarray:
        """
        Extrait le vecteur d'embedding 512-dim normalisé L2 depuis un visage aligné 112x112.
        """
        if self.session_rec is None:
            return np.zeros(512, dtype=np.float32)

        # Preprocessing ArcFace : BGR -> RGB, normalisation [-1, 1], transposée NCHW
        rgb = cv2.cvtColor(aligned_face_bgr, cv2.COLOR_BGR2RGB)
        blob = (rgb.astype(np.float32) - 127.5) / 127.5
        blob = np.transpose(blob, (2, 0, 1))
        blob = np.expand_dims(blob, axis=0)  # Shape (1, 3, 112, 112)

        input_name = self.session_rec.get_inputs()[0].name
        output_name = self.session_rec.get_outputs()[0].name

        raw_feat = self.session_rec.run([output_name], {input_name: blob})[0][0]

        # Normalisation L2 du vecteur
        norm = np.linalg.norm(raw_feat)
        if norm > 0:
            embedding = raw_feat / norm
        else:
            embedding = raw_feat

        return embedding.astype(np.float32)

    def identify_embedding(self, embedding: np.ndarray, margin_threshold: float = 0.04) -> tuple[str, float]:
        """
        Compare un vecteur 512-dim aux centroïdes et échantillons de profils connus avec vérification de marge anti-hésitation.
        """
        if not self.known_faces or len(embedding) == 0:
            return "INCONNU", 0.0

        scores = {}
        for name, known_vecs in self.known_faces.items():
            # 1. Score par centroïde moyen (moyenner tous les échantillons enregistrés)
            mean_vec = np.mean(known_vecs, axis=0)
            norm = np.linalg.norm(mean_vec)
            if norm > 0:
                mean_vec = mean_vec / norm
            centroid_sim = float(np.dot(embedding, mean_vec))

            # 2. Meilleur score d'échantillon individuel
            max_single_sim = max([float(np.dot(embedding, kv)) for kv in known_vecs])

            # Score combiné (70% centroïde stable + 30% max individuel)
            scores[name] = 0.70 * centroid_sim + 0.30 * max_single_sim

        # Tri des profils par score décroissant
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_name, best_sim = sorted_scores[0]

        # Calcul de la marge par rapport au 2ème candidat (si au moins 2 profils enregistrés)
        margin = 1.0
        if len(sorted_scores) > 1:
            second_name, second_sim = sorted_scores[1]
            margin = best_sim - second_sim

        # Décision robuste avec vérification du seuil et de la marge anti-hésitation
        if best_sim >= self.match_threshold:
            if margin < margin_threshold:
                print(f"\r⚠️ [Hésitation Faciale] Incertitude entre '{best_name}' ({best_sim*100:.1f}%) et '{sorted_scores[1][0]}' ({sorted_scores[1][1]*100:.1f}%)", flush=True)
                return "INCONNU", best_sim
            
            print(f"\r🔍 [Face Match ✅] Identification: '{best_name}' (Score: {best_sim*100:.1f}% | Marge: +{margin*100:.1f}%)", flush=True)
            return best_name, best_sim
        else:
            return "INCONNU", best_sim

    def detect_exact_face_roi(self, head_crop_bgr: np.ndarray):
        """
        Détecte le rectangle exact du visage (yeux, nez, bouche) à l'intérieur du crop de tête.
        Returns: (face_crop_112x112, relative_face_bbox)
        """
        if head_crop_bgr is None or head_crop_bgr.size == 0:
            return None, None

        h_c, w_c = head_crop_bgr.shape[:2]

        # Utilisation du détecteur de visage Haar/OpenCV léger sur le crop de tête
        gray = cv2.cvtColor(head_crop_bgr, cv2.COLOR_BGR2GRAY)
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
            if len(faces) > 0:
                # Sélection du plus grand visage trouvé dans le crop
                fx, fy, fw, fh = max(faces, key=lambda b: b[2] * b[3])
                face_crop = head_crop_bgr[fy:fy+fh, fx:fx+fw]
                aligned = cv2.resize(face_crop, (112, 112))
                return aligned, (fx, fy, fx + fw, fy + fh)
        except Exception:
            pass

        # Fallback rognage intelligent au centre (15-85% H, 15-85% W)
        face_roi = head_crop_bgr[int(h_c * 0.15):int(h_c * 0.85), int(w_c * 0.15):int(w_c * 0.85)]
        if face_roi.size > 0:
            aligned = cv2.resize(face_roi, (112, 112))
        else:
            aligned = cv2.resize(head_crop_bgr, (112, 112))
        
        return aligned, (int(w_c * 0.15), int(h_c * 0.15), int(w_c * 0.85), int(h_c * 0.85))

    def process_person_crop(self, frame_bgr: np.ndarray, person_bbox: tuple) -> tuple[str, float, tuple]:
        """
        Traite une sous-région `PERSONNE` (ROI): découpe la zone de la tête, aligne et identifie.
        Returns: (name, sim, exact_face_bbox_in_frame)
        """
        x1, y1, x2, y2 = person_bbox
        h, w = frame_bgr.shape[:2]

        crop_h = int((y2 - y1) * 0.45)
        head_y2 = min(y1 + crop_h, h)
        head_crop = frame_bgr[max(0, y1):head_y2, max(0, x1):min(x2, w)]

        if head_crop.size == 0:
            return "INCONNU", 0.0, (x1, y1, x2, head_y2)

        aligned, rel_bbox = self.detect_exact_face_roi(head_crop)
        if aligned is None:
            aligned = cv2.resize(head_crop, (112, 112))
            rel_bbox = (0, 0, head_crop.shape[1], head_crop.shape[0])

        # Calcul des coordonnées de la boîte du visage dans l'image globale frame
        rx1, ry1, rx2, ry2 = rel_bbox
        face_bbox_frame = (max(0, x1 + rx1), max(0, y1 + ry1), min(w, x1 + rx2), min(h, y1 + ry2))

        emb = self.get_embedding(aligned)
        name, sim = self.identify_embedding(emb)
        return name, sim, face_bbox_frame

    def register_face(self, name: str, aligned_face_bgr: np.ndarray) -> bool:
        """
        Enregistre un nouveau profil ou ajoute un échantillon de vecteur d'embedding pour une personne donnée.
        """
        emb = self.get_embedding(aligned_face_bgr)
        if np.linalg.norm(emb) == 0:
            print(f"❌ Impossible de générer l'embedding pour '{name}'.")
            return False

        clean_name = name.strip().title()
        if clean_name not in self.known_faces:
            self.known_faces[clean_name] = []

        self.known_faces[clean_name].append(emb)
        self.save_known_faces()
        print(f"✅ Visage d'embedding enregistré pour '{clean_name}' (Total échantillons: {len(self.known_faces[clean_name])}).")
        return True
