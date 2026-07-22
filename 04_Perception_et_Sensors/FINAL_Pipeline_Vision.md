# 07 - Vision, Intelligence Artificielle & Traitement Spatiale 3D

## 1. Capteur Principal : Luxonis OAK-D Pro (FF) ⭐ CONFIRMÉ (Juillet 2026)
Le choix s'est porté sur la version **Fixed Focus (FF)** pour garantir la stabilité de la perception visuelle malgré les vibrations mécaniques des moteurs RobStride.

### 1.1 Repartition de la Charge de Calcul (OAK-D VPU ↔ Jetson GPU ↔ Mac M1 Max)

La stratégie visuelle du D-Bot repose sur une **répartition à 3 niveaux** optimisant la latence et la mémoire :

1. **Sur le VPU Myriad X de la caméra OAK-D Pro (4 TOPS)** :
   - **Calcul de Profondeur Stéréo** : Génération de la carte de disparité $3D$ à 120 FPS via les capteurs infrarouges et le projecteur Laser IR (4700 points).
   - **Filtre WLS Matériel (Weighted Least Squares)** : Lissage et comblement des trous de la carte de profondeur sur la puce OAK-D (économie de 25% de charge CPU Jetson).
   - **Nœud `SpatialLocationCalculator`** : Calcul tridimensionnel des ROIs et génération d'alertes de sécurité immédiates ($Z < 500\text{ mm}$) à $< 5\text{ ms}$.

2. **Sur le GPU NVIDIA Ampere de la Jetson Orin Nano Super (67 TOPS)** :
   - **Triade Visuelle Zero-Shot (YOLO-World v2 - `yolov8m-worldv2`)** : Inférence sémantique temps réel en TensorRT FP16 / ONNX ($> 40\text{ FPS}$, latence $\sim 15\text{ ms}$, VRAM $\sim 1.2\text{ Go}$).

3. **Sur le Serveur Compagnon Mac M1 Max 64 Go (Cognition Déportée)** :
   - **Raisonnement Spatiale Complexe & Active Gaze** : Modèles multimodaux **NVIDIA Cosmos 3D Edge / LocateAnything-3B** déportés via gRPC/HTTP pour l'orientation dynamique du cou ("*Regarde le téléphone posé près du clavier*").

---

## 2. Intégration Mécanique & Optique

- **Dimensions du perçage** : **98 x 30 mm** (prévoir +0.5 mm de tolérance).
- **Fixation** : 2x vis M3, entraxe de **75 mm**, centrées.
- **Passage Câble** : Encoche de **18 mm** en bas pour le connecteur USB-C coudé.
- **Orientation** : Inclinaison de **-10° à -15°** vers le sol recommandée pour détecter les obstacles proches.

---

## 3. Architecture Logicielle (`dbot/vision`)

Le système de vision est structuré autour de quatre modules Python principaux :
- **`code/dbot/vision/oak_camera.py`** : Interface DepthAI v2 gérant le capteur RGB, la stéréo active IR, le filtre matériel WLS et le nœud `SpatialLocationCalculator`.
- **`code/dbot/vision/yolo_world.py`** : Moteur d'inférence sémantique Zero-Shot YOLO-World v2 avec accélération TensorRT FP16 / ONNX et superposition multi-couleurs.
- **`code/dbot/vision/spatial_fusion.py`** : Fusion spatiale tridimensionnelle associant les Bounding Boxes $2D$ et la carte de profondeur pour extraire les coordonnées physiques réelles $[X, Y, Z]$ en mm.
- **`code/scripts/vision/test_triad_vision.py`** : Script de qualification sur le terrain avec sauvegarde incrémentale sous `/tmp/dbot_snapshots/snap_XXX_...jpg`.
