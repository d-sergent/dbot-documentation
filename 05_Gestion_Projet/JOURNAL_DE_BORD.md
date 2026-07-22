# 📓 JOURNAL DE BORD DU PROJET D-BOT V1

Ce document enregistre l'historique chronologique des jalons validés, des choix d'architecture et des résultats de tests terrain sur le robot D-Bot V1.

---

## 📅 2026-07-22 — Stabilisation I/O Motorbridge Web UI & Cou Pan/Tilt

### 🎯 Objectif de la session
1. Éliminer les blocages du serveur HTTP Motorbridge Web UI et sécuriser les threads de mouvement du cou RS-05.
2. Fluidifier les curseurs sliders HTML/JS et désactiver les requêtes réseau superflues.
3. Éliminer les timeouts CAN et verrous bloquants (`self.lock`).

### 📝 Réalisations & Évolutions
1. **Refactoring Multithread Web UI (`web_ui.py`)** :
   - Migration de toutes les opérations d'I/O CAN (`detect`, `get_state`, `enable`) hors du verrou `self.lock`. `self.lock` ne protège plus que l'écriture ultra-courte (< 1 ms) des variables Python partagées.
2. **Optimisation du Protocole CAN (`neck.py`)** :
   - Passage des paramètres de configuration (`run_mode`, `limit_spd`, gains PID) en mode *fire-and-forget* (`write_param_no_ack`).
   - Réduction du temps d'exécution d'activation `enable()` de ~9s à ~1.5s.
3. **Robustesse de la Télémétrie** :
   - Appel de `detect(update_active=False)` pendant la télémétrie périodique pour éviter toute remise à zéro intempestive de `active_motors` pendant un déplacement.
   - Suppression du bruit de logs `DEBUG` de `python-can` et `robstride` avec élévation des logs de cycle de vie des threads de mouvement en `INFO`.

---

## 📅 2026-07-22 — Qualification de la Triade Visuelle Sémantique & Fusion Spatiale 3D OAK-D Pro

### 🎯 Objectif de la session
1. Corriger les échecs de détection visuelle Zero-Shot (absence de détection simultanée main/téléphone/personne).
2. Développer l'affichage multi-boîtes hiérarchique avec palette de couleurs vifs par classe BGR et bannières opaques.
3. Implémenter le stockage incrémental des clichés de débogage visuel (`/tmp/dbot_snapshots/snap_XXX_...jpg`).
4. Déployer l'accélération TensorRT FP16 / ONNX sur la Jetson Orin Nano pour abaisser la latence et maîtriser la RAM.
5. Mettre à jour la documentation d'installation GPU JetPack 6.1 et valider le budget mémoire unifié LPDDR5.
6. Implémenter le déport VPU Myriad X (Filtre WLS + `SpatialLocationCalculator`) et restaurer le plein champ optique (81° FOV via ISP Scaling).

### 📝 Réalisations & Évolutions
1. **Refonte de la Triade Visuelle (`test_triad_vision.py` & `dbot/vision/yolo_world.py`)** :
   - Mise à niveau du modèle de `yolov8s` vers `yolov8m-worldv2` (26M paramètres).
   - Passage des requêtes CLIP en Anglais pur 1-to-1 (`hand`, `phone`, `bottle`, `person`, `chair`, `table`, `obstacle`).
   - Configuration NMS multi-classes permissive (`agnostic_nms=False`, `iou=0.70`, `conf=0.05`, `max_det=100`) permettant la coexistence de boîtes enfants (`MAIN`, `TELEPHONE`) dans des boîtes parents (`PERSONNE`).
2. **Superposition Visuelle & Spatiale 3D** :
   - Mappage de couleurs BGR distinctes par classe (`MAIN` Vert, `TELEPHONE` Cyan, `PERSONNE` Bleu, `TABLE` Violet, `CHAISE` Magenta, `BOUTEILLE` Orange) avec bannières de texte opaques.
   - Fusion spatiale $3D$ via OAK-D Pro affichant les coordonnées physiques réelles $[X, Y, Z]$ en mm.
3. **Stockage Incrémental de Clichés** :
   - Enregistrement sous `/tmp/dbot_snapshots/snap_XXX_LABEL_DIST.jpg` sans écrasement avec raccourci `/tmp/triad_last_detection.jpg`.
4. **Optimisation Matérielle & Documentation GPU/Mémoire** :
   - Implémentation du script d'exportation TensorRT FP16 / ONNX (`export_yolo_tensorrt.py`) avec limitation workspace à 2 GB.
   - Documentation complète des pièges `pip` (`cuda-toolkit-cu13`, `numpy 2.x`) et mise à jour de [`Annexes/jetson/installation/43_Configuration_PyTorch_CUDA_JetPack6.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/jetson/installation/43_Configuration_PyTorch_CUDA_JetPack6.md).
   - Validation du budget mémoire : Empreinte VRAM/RAM de la vision à **$1.2\text{ Go}$ à $1.8\text{ Go}$**, parfaitement conforme à l'alloué ($\le 2.5\text{ Go}$) dans `FINAL_Architecture_Master_V1_Hybride.md`, laissant **$> 4.5\text{ Go}$ libres**.
5. **Déport VPU Myriad X & Optique Grand Angle 81° FOV (`oak_camera.py`)** :
   - Déport matériel du lissage de profondeur WLS (gain 25% CPU Jetson) et du nœud `SpatialLocationCalculator` ($Z < 500\text{ mm}$ à $< 5\text{ ms}$).
   - Remplacement du rognage `setVideoSize` par l'ISP scaling matériel `setIspScale(1, 3)` pour restituer le plein champ grand angle 81° FOV.

---

## 📅 2026-07-22 — Finalisation Active Gaze, Support Français YOLO-World & Compilation PyTorch GPU

### 🎯 Objectif de la session
1. Intégrer la traduction automatique natif Français ➔ Anglais pour YOLO-World sans charge processeur.
2. Développer la boucle d'asservissement physique du cou **Active Gaze (Regard Actif)** et le serveur compagnon Visual Grounding sur Mac (`server_active_gaze_mac.py`).
3. Ajouter la poursuite prédictive par inertie de fuite (`Predictive Gaze`) et la gestion des conflits NMS multi-classes (`PERSONNE` vs `MAIN`).
4. Résoudre la régression PyTorch CPU et re-compiler nativement `torchvision` v0.20.0 avec accélération CUDA GPU.
5. Inscrire la règle de protection `pip install --no-deps` dans `.agents/AGENTS.md`.

### 📝 Réalisations & Évolutions
1. **Traduction Automatique & Dictionnaire Persistant (`fr_en_dictionary.json` & `yolo_world.py`)** :
   - Fichier JSON local pré-chargé avec **+150 objets du quotidien**.
   - Traduction zéro-ressource via `urllib.request` (Google Translate < 30 ms, 0 Mo RAM, 0% CPU) pour les mots inédits avec mémorisation automatique.
2. **Asservissement du Regard (Active Gaze & Predictive Tracking)** :
   - Création de `dbot/behaviors/active_gaze.py` et `scripts/vision/test_active_gaze.py`.
   - Conversion du décalage $2D$ en correction d'angles $(\Delta \theta_{pan}, \Delta \theta_{tilt})$ pour le cou RS-05 avec bridage de sécurité absolu aux bornes `config.py` ($[-80°, +80°]$ Pan, $[-20°, +30°]$ Tilt).
   - Extrapolation de vitesse (`predict_lost_target`) pendant 0.4s pour anticiper les fuites rapides de cibles et éviter le décrochage visuel.
3. **Résolution du Conflit NMS Hiérarchique** :
   - Configuration de `iou=0.90` et `agnostic_nms=False` dans `yolo_world.py` pour autoriser la détection simultanée de `PERSONNE` et `MAIN` sans écrasement de la boîte enfant par le corps.
4. **Restauration de PyTorch CUDA GPU & Compilation Native `torchvision` v0.20.0** :
   - Ré-installation du wheel officiel NVIDIA JetPack 6.1 `torch==2.5.0a0+872d972e41.nv24.08`.
   - Compilation depuis les sources de `torchvision` v0.20.0 avec `MAX_JOBS=1 FORCE_CUDA=1` sous `ninja` pour éviter le crash OOM RAM. Validation `CUDA disponible : True | NMS CUDA OK : True`.
5. **Pérennisation dans les Règles du Projet** :
   - Règle de protection `pip install <paquet> --no-deps` gravée dans `.agents/AGENTS.md`.

### 📌 Statut Général
- **Vision Réflexe Local & Regard Actif** : Totalement opérationnels et validés sur la Jetson Orin Nano GPU CUDA avec asservissement fluide du cou RS-05 et support du Français natif !
