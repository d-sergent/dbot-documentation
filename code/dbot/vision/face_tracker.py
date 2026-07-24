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

# URL officielles InsightFace
BUFFALO_SC_URL = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_sc.zip"
BUFFALO_L_URL  = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"

SCRFD_PATH     = os.path.join(WEIGHTS_DIR, "det_500m.onnx")
MBF_PATH       = os.path.join(WEIGHTS_DIR, "w600k_mbf.onnx")
RESNET50_PATH  = os.path.join(WEIGHTS_DIR, "w600k_r50.onnx")

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


def download_and_extract_models(use_resnet50: bool = True):
    """Télécharge l'archive officielle InsightFace (buffalo_l.zip ou buffalo_sc.zip) et extrait les modèles ONNX."""
    url = BUFFALO_L_URL if use_resnet50 else BUFFALO_SC_URL
    zip_name = "buffalo_l.zip" if use_resnet50 else "buffalo_sc.zip"
    zip_path = os.path.join(WEIGHTS_DIR, zip_name)
    desc = "ArcFace ResNet50 (buffalo_l.zip - 280 Mo)" if use_resnet50 else "MobileFaceNet (buffalo_sc.zip - 15 Mo)"

    print(f"⏳ Téléchargement du pack modèle officiel InsightFace {desc}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(zip_path, 'wb') as f:
            f.write(resp.read())

        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(WEIGHTS_DIR)

        if os.path.exists(zip_path):
            os.remove(zip_path)
        print(f"✅ [FaceTracker] Pack `{desc}` installé avec succès dans '{WEIGHTS_DIR}' !")
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement de '{zip_name}' : {e}")
        if use_resnet50:
            print("⚠️ Repli sur le pack MobileFaceNet (buffalo_sc.zip)...")
            download_and_extract_models(use_resnet50=False)


class FaceTracker:
    """
    Gestionnaire de Détection et d'Identification Faciale Haute Précision (SCRFD + ResNet50 ArcFace + SVM).
    """

    def __init__(self, match_threshold: float = 0.30, use_gpu: bool = True, use_resnet50: bool = True):
        self.match_threshold = match_threshold
        self.use_gpu = use_gpu
        self.use_resnet50 = use_resnet50

        ensure_directory(FACES_DIR)
        ensure_directory(WEIGHTS_DIR)

        # Choix du modèle d'embedding (ResNet50 Haute Précision par défaut)
        target_rec_path = RESNET50_PATH if use_resnet50 else MBF_PATH

        if not os.path.exists(SCRFD_PATH) or not os.path.exists(target_rec_path):
            download_and_extract_models(use_resnet50=use_resnet50)

        self.rec_path = target_rec_path if os.path.exists(target_rec_path) else MBF_PATH

        self.session_det = None
        self.session_rec = None
        self.svm_classifier = None
        self.svm_classes = []
        self._init_onnx_sessions()

        # Dictionnaire mémoire des visages connus {name: [vector1, vector2]}
        self.known_faces = self.load_known_faces()
        self._train_svm_classifier()

    def _init_onnx_sessions(self):
        """Initialise les sessions ONNXRuntime pour SCRFD et ArcFace ResNet50."""
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
                }))
                print("⚡ [FaceTracker] GPU CUDA activé pour ONNXRuntime ArcFace ResNet50.")

        try:
            if os.path.exists(SCRFD_PATH):
                self.session_det = ort.InferenceSession(SCRFD_PATH, providers=providers)
            if os.path.exists(self.rec_path):
                self.session_rec = ort.InferenceSession(self.rec_path, providers=providers)
            
            model_name = "ArcFace ResNet50 (w600k_r50)" if "w600k_r50" in self.rec_path else "MobileFaceNet (w600k_mbf)"
            print(f"✅ [FaceTracker] Modèles SCRFD_500M & {model_name} initialisés avec succès !")
        except Exception as e:
            print(f"⚠️ Erreur d'initialisation ONNXRuntime GPU ({e}). Tentative en CPU pure...")
            try:
                if os.path.exists(SCRFD_PATH):
                    self.session_det = ort.InferenceSession(SCRFD_PATH, providers=['CPUExecutionProvider'])
                if os.path.exists(self.rec_path):
                    self.session_rec = ort.InferenceSession(self.rec_path, providers=['CPUExecutionProvider'])
            except Exception as e2:
                print(f"❌ Échec initialisation CPU FaceTracker : {e2}")
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

    def _train_svm_classifier(self):
        """Entraîne un classifieur SVM à noyau linéaire (Étape 3) si au moins 2 profils existent."""
        if not self.known_faces or len(self.known_faces) < 2:
            self.svm_classifier = None
            self.svm_classes = []
            return

        try:
            from sklearn.svm import SVC
            X, y = [], []
            for name, vecs in self.known_faces.items():
                for v in vecs:
                    X.append(v)
                    y.append(name)

            if len(set(y)) >= 2 and len(X) >= 3:
                clf = SVC(kernel='linear', C=1.0, probability=True)
                clf.fit(X, y)
                self.svm_classifier = clf
                self.svm_classes = list(clf.classes_)
                print(f"🎯 [FaceTracker] Classifieur SVM (Étape 3) entraîné sur {len(X)} échantillons pour {len(self.svm_classes)} profil(s).")
            else:
                self.svm_classifier = None
        except Exception as e:
            self.svm_classifier = None

    def identify_embedding(self, embedding: np.ndarray, margin_threshold: float = 0.02) -> tuple[str, float]:
        """
        Compare un vecteur 512-dim via SVM à séparation optimale (Étape 3) ou centroïdes cosinus.
        """
        if not self.known_faces or len(embedding) == 0:
            return "INCONNU", 0.0

        # Étape 3 : Si un classifieur SVM est disponible et entraîné, utilisation de l'hyperplan optimal
        if self.svm_classifier is not None and len(self.svm_classes) >= 2:
            try:
                probs = self.svm_classifier.predict_proba([embedding])[0]
                best_idx = int(np.argmax(probs))
                best_name = str(self.svm_classes[best_idx])
                best_prob = float(probs[best_idx])
                
                # Verification cosinus pour eviter les faux positifs hors-base
                known_vecs = self.known_faces.get(best_name, [])
                if known_vecs:
                    mean_vec = np.mean(known_vecs, axis=0)
                    norm = np.linalg.norm(mean_vec)
                    if norm > 0:
                        mean_vec = mean_vec / norm
                    cos_sim = float(np.dot(embedding, mean_vec))
                else:
                    cos_sim = best_prob

                if best_prob >= 0.40 and cos_sim >= self.match_threshold:
                    print(f"\r🎯 [SVM Match ✅] Identification: '{best_name}' (Probabilité: {best_prob*100:.1f}% | Cosinus: {cos_sim*100:.1f}%)", flush=True)
                    return best_name, cos_sim
            except Exception:
                pass

        scores = {}
        for name, known_vecs in self.known_faces.items():
            # 1. Score par centroïde moyen
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

    def _scrfd_preprocess(self, bgr_img: np.ndarray, input_size=(640, 640)):
        """Letterbox resize + normalisation ArcFace pour SCRFD."""
        img_h, img_w = bgr_img.shape[:2]
        target_h, target_w = input_size
        scale = min(target_h / img_h, target_w / img_w)
        new_h = max(1, int(img_h * scale))
        new_w = max(1, int(img_w * scale))
        resized = cv2.resize(bgr_img, (new_w, new_h))
        padded = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        padded[:new_h, :new_w] = resized
        blob = (padded.astype(np.float32) - 127.5) / 128.0
        blob = np.transpose(blob, (2, 0, 1))
        blob = np.expand_dims(blob, 0)
        return blob, scale

    def _nms(self, boxes: np.ndarray, scores: np.ndarray, iou_thresh: float = 0.4) -> list:
        """NMS simple NumPy (Non-Maximum Suppression)."""
        x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]
        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(int(i))
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            inter = np.maximum(0, xx2 - xx1 + 1) * np.maximum(0, yy2 - yy1 + 1)
            iou = inter / (areas[i] + areas[order[1:]] - inter)
            order = order[1:][iou <= iou_thresh]
        return keep

    def _scrfd_decode(self, outputs: list, orig_shape: tuple, scale: float,
                      input_size=(640, 640), conf_thresh: float = 0.45) -> list:
        """
        Décode les sorties brutes du modèle SCRFD 500M.
        Strides [8, 16, 32], num_anchors=2 par location, 6 ou 9 tenseurs en sortie.
        Returns: liste de dicts {'bbox', 'landmarks', 'score'}.
        """
        strides = [8, 16, 32]
        num_anchors = 2
        img_h, img_w = orig_shape[:2]
        has_kps = (len(outputs) >= 9)
        out_per_stride = 3 if has_kps else 2
        faces = []

        for s_idx, stride in enumerate(strides):
            feat_h = input_size[0] // stride
            feat_w = input_size[1] // stride

            score_out = outputs[s_idx * out_per_stride].reshape(-1)
            bbox_out  = outputs[s_idx * out_per_stride + 1].reshape(-1, 4)
            kps_out   = outputs[s_idx * out_per_stride + 2].reshape(-1, 10) if has_kps else None

            # Génération des centres d'ancres
            anchor_cx, anchor_cy = [], []
            for row in range(feat_h):
                for col in range(feat_w):
                    for _ in range(num_anchors):
                        anchor_cx.append(col * stride)
                        anchor_cy.append(row * stride)
            anchor_cx = np.array(anchor_cx, dtype=np.float32)
            anchor_cy = np.array(anchor_cy, dtype=np.float32)

            valid = score_out >= conf_thresh
            if not np.any(valid):
                continue

            v_scores  = score_out[valid]
            v_bboxes  = bbox_out[valid]
            v_cx      = anchor_cx[valid]
            v_cy      = anchor_cy[valid]
            v_kps     = kps_out[valid] if kps_out is not None else None

            # Décodage bboxes (coordonnées dans l'image originale)
            x1 = np.clip((v_cx - v_bboxes[:, 0] * stride) / scale, 0, img_w)
            y1 = np.clip((v_cy - v_bboxes[:, 1] * stride) / scale, 0, img_h)
            x2 = np.clip((v_cx + v_bboxes[:, 2] * stride) / scale, 0, img_w)
            y2 = np.clip((v_cy + v_bboxes[:, 3] * stride) / scale, 0, img_h)

            for i in range(len(v_scores)):
                lmks = None
                if v_kps is not None:
                    lmks = v_kps[i].reshape(5, 2).copy()
                    lmks[:, 0] = np.clip((v_cx[i] + lmks[:, 0] * stride) / scale, 0, img_w)
                    lmks[:, 1] = np.clip((v_cy[i] + lmks[:, 1] * stride) / scale, 0, img_h)

                faces.append({
                    'bbox': (int(x1[i]), int(y1[i]), int(x2[i]), int(y2[i])),
                    'score': float(v_scores[i]),
                    'landmarks': lmks
                })

        if not faces:
            return []

        # NMS global sur tous les candidats
        boxes_arr  = np.array([[f['bbox'][0], f['bbox'][1], f['bbox'][2], f['bbox'][3]] for f in faces], dtype=np.float32)
        scores_arr = np.array([f['score'] for f in faces], dtype=np.float32)
        keep = self._nms(boxes_arr, scores_arr, iou_thresh=0.4)
        return [faces[i] for i in keep]

    def detect_faces_scrfd(self, bgr_crop: np.ndarray, conf_thresh: float = 0.40) -> list:
        """
        Détecte les visages dans bgr_crop avec le modèle SCRFD 500M (det_500m.onnx).
        Returns: liste de dicts {'bbox':(x1,y1,x2,y2), 'landmarks':np.array(5x2), 'score':float}.
        Retourne [] si aucun visage détecté ou si session_det non initialisée.
        """
        if self.session_det is None or bgr_crop is None or bgr_crop.size == 0:
            return []

        input_size = (640, 640)
        try:
            blob, scale = self._scrfd_preprocess(bgr_crop, input_size)
            input_name = self.session_det.get_inputs()[0].name
            outputs = self.session_det.run(None, {input_name: blob})
            return self._scrfd_decode(outputs, bgr_crop.shape, scale, input_size, conf_thresh)
        except Exception as e:
            return []

    def process_person_crop(self, frame_bgr: np.ndarray, person_bbox: tuple, hd_frame: np.ndarray = None) -> tuple[str, float, tuple]:
        """
        Pipeline complet de reconnaissance :
          YOLO bbox personne → Découpage HD 1080p → SCRFD (visage exact + 5 keypoints) → align_face ArcFace → embedding → identification.
        Returns: (name, sim, face_bbox_in_frame)
        """
        x1, y1, x2, y2 = person_bbox
        h, w = frame_bgr.shape[:2]

        head_h = int((y2 - y1) * 0.55)
        hx1, hy1 = max(0, x1), max(0, y1)
        hx2, hy2 = min(w, x2), min(h, y1 + head_h)

        # Étape 2 : Si un flux HD 1080p est fourni, découpage dans la haute résolution d'origine !
        if hd_frame is not None and hd_frame.size > 0:
            hd_h, hd_w = hd_frame.shape[:2]
            scale_x = hd_w / float(w)
            scale_y = hd_h / float(h)

            hx1_hd, hy1_hd = max(0, int(x1 * scale_x)), max(0, int(y1 * scale_y))
            hx2_hd = min(hd_w, int(x2 * scale_x))
            head_h_hd = int((int(y2 * scale_y) - hy1_hd) * 0.55)
            hy2_hd = min(hd_h, hy1_hd + head_h_hd)

            head_crop = hd_frame[hy1_hd:hy2_hd, hx1_hd:hx2_hd]
            scale_face_x = 1.0 / scale_x
            scale_face_y = 1.0 / scale_y
        else:
            head_crop = frame_bgr[hy1:hy2, hx1:hx2]
            scale_face_x = 1.0
            scale_face_y = 1.0

        if head_crop.size == 0:
            return "INCONNU", 0.0, (x1, y1, x2, y2)

        # === 1. Détection SCRFD du visage dans le crop HD ===
        faces = self.detect_faces_scrfd(head_crop, conf_thresh=0.35)

        if faces:
            # Visage avec meilleur score de confiance
            best = max(faces, key=lambda f: f['score'])
            bx1, by1, bx2, by2 = best['bbox']
            lmks = best['landmarks']

            # === 2. Alignement ArcFace avec les 5 keypoints SCRFD ===
            if lmks is not None and len(lmks) == 5:
                aligned = self.align_face(head_crop, lmks)
            else:
                face_roi = head_crop[max(0, by1):min(head_crop.shape[0], by2),
                                     max(0, bx1):min(head_crop.shape[1], bx2)]
                aligned = cv2.resize(face_roi if face_roi.size > 0 else head_crop, (112, 112))

            # Coordonnées absolues dans le frame d'affichage (mises à l'échelle)
            bx1_s, by1_s = int(bx1 * scale_face_x), int(by1 * scale_face_y)
            bx2_s, by2_s = int(bx2 * scale_face_x), int(by2 * scale_face_y)
            face_bbox_frame = (
                max(0, hx1 + bx1_s), max(0, hy1 + by1_s),
                min(w, hx1 + bx2_s), min(h, hy1 + by2_s)
            )

        else:
            # === Fallback anatomique ===
            ch, cw = head_crop.shape[:2]
            ay1_r, ay2_r = int(ch * 0.05), int(ch * 0.90)
            ax1_r, ax2_r = int(cw * 0.10), int(cw * 0.90)
            face_roi = head_crop[ay1_r:ay2_r, ax1_r:ax2_r]
            aligned = cv2.resize(face_roi if face_roi.size > 0 else head_crop, (112, 112))
            
            ax1_s, ay1_s = int(ax1_r * scale_face_x), int(ay1_r * scale_face_y)
            ax2_s, ay2_s = int(ax2_r * scale_face_x), int(ay2_r * scale_face_y)
            face_bbox_frame = (
                max(0, hx1 + ax1_s), max(0, hy1 + ay1_s),
                min(w, hx1 + ax2_s), min(h, hy1 + ay2_s)
            )

        # === 3. Embedding ArcFace + Identification ===
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
        self._train_svm_classifier()
        print(f"✅ Visage d'embedding enregistré pour '{clean_name}' (Total échantillons: {len(self.known_faces[clean_name])}).")
        return True

    def deduplicate_identities(self, face_results: list) -> list:
        """
        Garantit l'unicité physique de chaque identité enregistrée dans une même trame.
        Si une personne (ex: 'Émilie') est détectée 2 fois (chevauchement YOLO),
        seule la détection avec la meilleure similarité est conservée.
        """
        seen_names = {}
        for idx, res in enumerate(face_results):
            name = res.get("name", "INCONNU")
            sim = res.get("sim", 0.0)
            if name != "INCONNU":
                if name in seen_names:
                    prev_idx, prev_sim = seen_names[name]
                    if sim > prev_sim:
                        # Rétrograder la détection précédente en INCONNU
                        face_results[prev_idx]["name"] = "INCONNU"
                        face_results[prev_idx]["sim"] = 0.0
                        seen_names[name] = (idx, sim)
                    else:
                        # Rétrograder la détection actuelle en INCONNU
                        res["name"] = "INCONNU"
                        res["sim"] = 0.0
                else:
                    seen_names[name] = (idx, sim)
        return face_results
