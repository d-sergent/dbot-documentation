# 07 - Vision, Intelligence Artificielle & Traitement Spatiale 3D

## 1. Capteur Principal : Luxonis OAK-D Pro (FF) ⭐ CONFIRMÉ (Juillet 2026)
Le choix s'est porté sur la version **Fixed Focus (FF)** pour garantir la stabilité de la perception visuelle malgré les vibrations mécaniques des moteurs RobStride.

### 1.1 Repartition de la Charge de Calcul (OAK-D VPU ↔ Jetson GPU ↔ Mac M1 Max)

La stratégie visuelle du D-Bot repose sur une **répartition à 3 niveaux** optimisant la latence et la mémoire :

1. **Sur le VPU Myriad X de la caméra OAK-D Pro (4 TOPS)** :
   - **Calcul de Profondeur Stéréo** : Génération de la carte de disparité 3D à 120 FPS via les capteurs infrarouges et le projecteur Laser IR (4700 points).
   - **Filtre WLS Matériel (Weighted Least Squares)** : Lissage et comblement des trous de la carte de profondeur sur la puce OAK-D (économie de 25% de charge CPU Jetson).
   - **Nœud `SpatialLocationCalculator`** : Calcul tridimensionnel des ROIs et génération d'alertes de sécurité immédiates (Z < 500 mm) à < 5 ms.

2. **Sur le GPU NVIDIA Ampere de la Jetson Orin Nano Super (67 TOPS)** :
   - **Triade Visuelle Zero-Shot (YOLO-World v2 - `yolov8m-worldv2`)** :
     - *Mode Développement (PyTorch CUDA)* : Inférence à ~28 FPS (latence 32-38 ms, poids 52 Mo, VRAM ~650 Mo).
     - *Mode Production Optimisé (TensorRT FP16 `.engine`)* : Inférence ultra-rapide à 80-120 FPS (latence 8-12 ms, poids 55 Mo, VRAM ~400 Mo).
     - Basculement automatique : `yolo_world.py` détecte et utilise le fichier `.engine` dès sa compilation locale sur la Jetson via `code/scripts/vision/export_yolo_tensorrt.py`.

3. **Sur le Serveur Compagnon Mac M1 Max 64 Go (Cognition Déportée)** :
   - **Raisonnement Spatiale Complexe & Active Gaze** : Modèles multimodaux **NVIDIA Cosmos 3D Edge / LocateAnything-3B** déportés via gRPC/HTTP pour l'orientation dynamique du cou ("*Regarde le téléphone posé près du clavier*").

### 1.2 Impacts Concrets du Passage à TensorRT FP16 (80+ FPS)

| Critère / Métrique | PyTorch CUDA (Mode Dev) | TensorRT FP16 (Mode Prod) | Impact Concret sur le Robot |
| :--- | :---: | :---: | :--- |
| **Latence Visuelle** | 35 ms | **10 ms** | **3.5x plus rapide** : Poursuite instantanée des cibles en mouvement latéral rapide. |
| **Cadence de Perception** | 28 FPS | **80-100 FPS** | **Synchronisation CAN 100 Hz** : Alignement parfait avec le rafraîchissement moteur 10 ms. |
| **Empreinte VRAM GPU** | 650 Mo | **400 Mo** | **+250 Mo libérés** : Espace mémoire libéré pour la Reconnaissance Faciale et l'Audio DoA. |
| **Tolérance Flou de Bougé** | Moyenne | **Maximale** | Maintien continu du suivi sémantique lors des rotations rapides du cou. |

---

## 2. Intégration Mécanique & Optique

- **Champ de Vision Optique (FOV)** : Conservation du grand angle optique complet (**81° FOV**) sans rognage (*Center Crop*) grâce au scaling matériel ISP (`setIspScale(1, 3)`).
- **Dimensions du perçage** : **98 x 30 mm** (prévoir +0.5 mm de tolérance).
- **Fixation** : 2x vis M3, entraxe de **75 mm**, centrées.
- **Passage Câble** : Encoche de **18 mm** en bas pour le connecteur USB-C coudé.
- **Orientation** : Inclinaison de **-10° à -15°** vers le sol recommandée pour détecter les obstacles proches.

---

## 3. Architecture Logicielle (`dbot/vision`)

Le système de vision est structuré autour de cinq modules Python principaux :
- **`code/dbot/vision/oak_camera.py`** : Interface DepthAI v2 gérant le capteur RGB en plein champ 81° FOV, la stéréo active IR, le filtre matériel WLS et le nœud `SpatialLocationCalculator`.
- **`code/dbot/vision/yolo_world.py`** : Moteur d'inférence sémantique Zero-Shot YOLO-World v2 avec accélération TensorRT FP16 / ONNX et superposition multi-couleurs.
- **`code/dbot/vision/face_tracker.py`** : Module de reconnaissance faciale nommée ultra-compacte (SCRFD 500M `det_500m.onnx` avec 5 points clés + MobileFaceNet `w600k_mbf.onnx` ArcFace 512-dim). Intègre l'alignement affine par transformation d'Umeyama, la comparaison hybride centroïde/pic (seuil de marge 2%), le lissage temporel sur 5 trames et la persistance JSON.
- **`code/dbot/vision/spatial_fusion.py`** : Fusion spatiale tridimensionnelle associant les Bounding Boxes 2D et la carte de profondeur pour extraire les coordonnées physiques réelles [X, Y, Z] en mm.
- **`code/scripts/vision/test_face_tracker.py`** : Script d'exécution temps réel et d'enregistrement de visages déporté via serveur Web UI MJPEG (http://ubuntu.local:8090) avec interface graphique de cadrage.
- **`code/scripts/vision/test_triad_vision.py`** : Script de qualification sur le terrain avec sauvegarde incrémentale sous `/tmp/dbot_snapshots/snap_XXX_...jpg`.

---

## 4. Pipeline de Reconnaissance Faciale Nommée (`face_tracker.py`)

La reconnaissance faciale est directement couplée à la détection de personnes YOLO-World v2 :

```
[YOLO-World / TensorRT 80+ FPS] ➔ Bbox "PERSONNE" 2D
       │
       ▼
[Crop Haut du Corps (55% H)]
       │
       ▼
[SCRFD 500M ONNX] ➔ Détection Visage Exact + 5 Points Clés (Yeux, Nez, Coins Bouche)
       │
       ▼
[align_face()] ➔ Transformation Affine vers Repère Normalisé (112 x 112 px)
       │
       ▼
[MobileFaceNet ArcFace ONNX] ➔ Extraction Vecteur Embedding 512-dim Normalisé L2
       │
       ▼
[Buffer de Lissage Temporel] ➔ Moyenne Glissante sur 5 Trames (Suppression des fluctuations)
       │
       ▼
[Score Hybride & Centroïde] ➔ 70% Centroïde Moyen + 30% Peak (Seuil Marge 2%)
       │
       ▼
[Résolution Nommée & Fusion 3D] ➔ Identité ("David", "Léa") + Coordonnées 3D [X, Y, Z] mm
```

### 4.1 Caractéristiques Clés & Performances
- **Empreinte VRAM / Mémoire** : < 100 Mo VRAM GPU (inhibition de l'allocation globale ONNX CUDA).
- **Temps de Comparaison Vectorielle** : < 0.01 ms via produit scalaire NumPy 512-dim.
- **Fiabilité Terrain** : Scores de similarité élevés (70% - 95%) avec séparation des profils familiaux et zéro fausse alerte "INCONNU".
- **Serveur Web UI MJPEG (Port 8090)** : Permet l'enregistrement à distance d'un membre du foyer via navigateur web (`--register "Prénom"`) sans interrompre le flux vidéo.
