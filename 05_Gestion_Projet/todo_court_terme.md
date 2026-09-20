# 📋 TODO MASTER V1 — FEUILLE DE ROUTE ET SUIVI D'AVANCEMENT D-BOT

Ce document regroupe le suivi consolidé du projet **D-Bot V1 (Architecture Hybride Master)**. Il permet d'évaluer l'avancement global, depuis la validation physique de la tête jusqu'au contrôle cinématique et cognitif complet.

---

## 🟢 0. Briques Systèmes Déjà Validées et Opérationnelles

- [x] **Architecture Master V1 Hybride** : Répartition "Réflexe Local (Jetson 8 Go) ↔ Cognition Déportée (Mac M1 Max 64 Go)" formalisée dans [FINAL_Architecture_Master_V1_Hybride.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/05_Gestion_Projet/FINAL_Architecture_Master_V1_Hybride.md).
- [x] **Infrastructure Réseau Hybride** : Client léger `llm_client.py` opérationnel sur Jetson communiquant avec le serveur Mac via HTTP/gRPC.
- [x] **Moteur RAG Documentaire** : Serveur local LightRAG + FastEmbed hébergé sur Mac (port 7860/FastAPI) requêtable en ~15 ms.
- [x] **Capture Audio Non-Bloquante** : Script `audio_io_v2.py` sur Jetson exploitant un flux `sounddevice` streaming et une file d'attente thread-safe.
- [x] **VAD Matériel & Direction d'Arrivée (DoA 360°)** : Intégration de la carte ReSpeaker XVF-3800 (`respeaker_sdk.py`) pour la détection vocale matérielle et la localisation angulaire sans charge GPU.
- [x] **Barge-In Matériel (Interruption Vocal)** : Coupure instantanée de l'audio `aplay` et émission d'un signal d'interruption dès détection de parole utilisateur.
- [x] **Inspection Mécanique & Fichiers CAO STEP** : Modèles RobStride RS00 / RS04 / RS05 / RS06 qualifiés sous Fusion 360 pour les assemblages d'articulation.
- [x] **Dossier Technique Mécanique Torse V2.6 & Fixation Moteur Cou RS-05** : Validation complète du torse (colonne 7075-T6 5 mm avec jonction sandwich coupe droite Z=0 et 4 goupilles ISO 8734 Ø3×14 mm en carré 80×80 mm à Z=±40 mm et Y=±40 mm, brides d'épaules monoblocs festonnées à 10 lobes R=25,64 mm avec évidements latéraux élargis à 202,3 g/bride soit -129,2 g net sur le torse, inserts traversants Ø 35 mm Option B, équerres cou 30×30×3 mm Option C sans taraudage ni oblong, fixation directe du moteur cou RS-05 sur plaque de cou 4,68 mm via 4 vis FHC M3 × 8 mm par le dessous, liaison plaque cou ➔ équerres par 4 vis CHC M4 × 16 mm par le dessus sans fraisure sur perçages lisses Ø 4,3 mm, rectangle de vissage équerres 30×45 mm, protocole de montage inversé naturel, devis Blockenstock & visserie France Bricovis) dans [DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md).
- [x] **Dossier Technique Mécanique Bassin & Liaison Active Waist Yaw V1.2** : Création et qualification du dossier de référence, renommage du répertoire en `01_Mecanique_et_Chassis/Torse_et_Bassin`, intégration de la motorisation RobStride RS-06 (36 N.m, ID 21), validation du découplage d'efforts par roulement à rouleaux croisés industriel **CRBH 8016 UU** (80 x 120 x 16 mm, 520 N.m, Sf = 2.36 face aux 17.3 kg suspendus et 220 N.m max), conception de la **Platine d'Interface Waist monolithique** usinée sur CNC NestWorks C500 dans disque Alu 7075-T651 Ø 150 x 15 mm, conception du **Moyeu d'Accouplement Sandwich 7075-T6** (pincement de la bague intérieure par 4 vis FHC M4 sur PCD Ø 68 mm à 45°, précharge 19,2 kN), intégration de la butée angulaire physique par doigt externe (Solution A, +/- 95 deg) et corridor central/déporté de passage de câbles dans [DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md).
- [x] **Audit Métrologique Automatisé CAO Fusion 360 (Torse v88)** : Pipeline Python bidirectionnel développé (`AuditTorse.py` + `ModifyTorse.py`). Recalibrage des masses de structure en Alu 7075 (1 735,3 g mesurés vs 1 754 g doc, conformité 99%), validation métrologique de la coupe droite Z=0 et du carré de goupilles 80×80 mm ISO 8734, de la Waist Plate 7075 (Ø 80 mm central, 4 fraisures FHC M4), de la Plaque de Cou 7075 (4 fraisures FHC M3 dessous, 4 perçages lisses M4 dessus sans fraisure) et des équerres L=90 mm (waist) et L=50 mm (cou).

---

## 📐 FINALISATION CAO TORSE & BASSIN (Demi-Modèle Droit ➔ Symétrie Complète)

### Phase 1 : Ajustements Côté Droit (Fusion 360)
- [ ] **Moyeu Waist 7075** : Ajouter 4 trous borgnes taraudés M4 (prof. 12 mm, filet 10 mm) sur PCD Ø 68,00 mm à 45° (`X = ±24,04 mm`, `Y = ±24,04 mm`) pour recevoir les 4 vis FHC M4 de la Waist Plate.
- [ ] **Platine d'Interface Waist Monolithique** : Modéliser le disque Alu 7075-T6 Ø 140 × 12 mm (alésage central stator RS-06 Ø 88 H7, siège supérieur roulement CRBH 8016 Ø 120 H7 × 3 mm, 4 taraudages M3 flasque PCD Ø 128 mm) en remplacement d'`ASV1_200_16A.step`.
- [ ] **Butée Angulaire Waist Yaw** : Modéliser le doigt de butée externe (15 × 15 × 10 mm) sous la Waist Plate et implanter les 2 vis CHC M5 à ±95° sur la platine fixe.

### Phase 2 : Symétrie Miroir Finale (Plan Sagittal Y = 0,0 mm)
- [ ] **Symétrie Épaule Gauche** : Dupliquer par miroir la `Bride Epaule` (+202,3 g) et le moteur `RS04 droit` ➔ `RS04 gauche` (+551 g) avec les 10 vis M4 et rondelles Nord-Lock.
- [ ] **Symétrie Cornières Gauches** : Dupliquer l'`Equerre cou` (+46,6 g) et l'`Equerre waist` (+42,1 g) sur le flanc gauche de la colonne avec leur visserie de pincement.
- [ ] **Contrôle Final Global** : Relancer `AuditTorse.py` pour valider le bilan de masse du torse complet assemblé (~4,3 kg avec moteurs RS-04/RS-05/RS-06).
- [x] **Stratégie d'Alimentation 48V à 3 Niveaux** : Schéma d'alimentation validé (Wanptek 60V/5A, MeanWell LRS-600-48 600W, Batterie 48V 13S NMC).
- [x] **Triade Visuelle Temps Réel & Fusion Spatiale 3D** : Couplage OAK-D Pro + YOLO-World v2 Zero-Shot + SpatialFusion (`test_triad_vision.py`) avec détection multi-boîtes hiérarchique, classification multicolore et coordonnées 3D réelles [X, Y, Z] en mm.
- [x] **Déport VPU Myriad X (OAK-D Pro)** : Intégration du filtre matériel WLS et du nœud `SpatialLocationCalculator` (Z < 500 mm) dans `oak_camera.py`.
- [x] **Motorbridge Web UI & Contrôle du Cou** : Diagnostic temps réel et asservissement fluide des moteurs du cou Pan/Tilt RS-05 (`web_ui.py` + `neck.py`).
- [x] **Support du Français & Mappage Multilingue YOLO-World** : Dictionnaire persistant local `fr_en_dictionary.json` (+150 mots) et traduction automatique zéro-ressource via `urllib` dans `yolo_world.py`.
- [x] **Active Gaze & Regard Actif (`test_active_gaze.py`)** : Asservissement angulaire du cou Pan/Tilt sur les cibles visuelles sémantiques 3D (`active_gaze.py`) et serveur compagnon Mac (`server_active_gaze_mac.py`).

---

## 🎯 BLOCK 1 : Validation Physique Tête / Cou & Alimentation Atelier (Priorité Immédiate)

- [ ] **Démontage du casque** : Libérer l'accès aux mécanismes et aux 2 moteurs du cou RS-05 (Pan & Tilt).
- [ ] **Câblage & Longueur de câbles RS-05** : Raccorder les moteurs et ajuster les longueurs pour garantir les rotations sans contrainte ni tension.
- [x] **Tableau de Bord Web UI (`Motorbridge` Web UI)** : Serveur léger Web UI développé dans `Code/dbot/motors/web_ui.py` sur la Jetson Orin Nano pour contrôler et visualiser en temps réel la télémétrie des 2 moteurs RS-05 du cou (angles, températures, tension, erreurs CAN0) depuis le navigateur du Mac (`http://ubuntu.local:8080`).
- [x] **Premier test dynamique du Cou (Sans Casque)** : Valider les rotations Pan/Tilt via `web_ui.py` et `test_neck.py` avec mouvements LERP fluides et non-bloquants.
- [ ] **Remontage du casque & Butées logicielles** : Définir et verrouiller les angles limites dans `config.py` pour éviter tout choc mécanique entre le casque et la structure.
- [x] **Orientation Tête sur DoA Audio** : Coupler la position angulaire des RS-05 avec la direction DoA (0-360°) de la ReSpeaker pour orienter la tête vers la voix (`dbot/behaviors/audio_gaze.py`).
- [ ] **Intégration Simultanée des Capteurs Tête** : Brancher et valider la marche simultanée de l'OAK-D Pro, du ReSpeaker et des moteurs du cou.
- [ ] **Station d'Alimentation Atelier 600W** : Imprimer le boîtier 3D `RS-power-Top Cover.stp` et assembler le bloc MeanWell LRS-600-48 (48V / 12.5A) avec connecteurs XT30 2+2.

---

## 🎯 BLOCK 2 : Synthèse Vocale HD Streaming & Solution Secours Locale

- [x] **Pipeline Conversationnel Déporté Complet (ASR + LLM + TTS sur Mac)** : 
  - `companion_server.py` (port 8001) valide — chaîne WebSocket `Jetson → Mac → Jetson` opérationnelle.
  - VAD logicielle RMS calibrée automatiquement au démarrage (seuil adaptatif 150 RMS min) + pre-roll 5 chunks.
  - Groq Cloud Whisper Large v3 Turbo (< 300 ms) + Faster-Whisper `small` CPU fallback (~900 ms) + Gemini 2.0 Flash LLM + Qwen3-TTS MLX GPU (M1 Max).
  - Bugs résolus : inspection WebSocket Starlette, double conversion stéréo/mono, VAD SDK instable, hallucinations Whisper, auto-interruption pendant la réponse du robot.
- [x] **Architecture Autonome "Jetson Edge Cloud" (Mode 3 - PAR DÉFAUT PRODUCTION)** :
  - **100% Autonome Jetson** : Script `test_jetson_edge_cloud.py` exécutant l'ASR Groq Cloud, le LLM Gemini 2.0 Flash et le TTS Microsoft Edge-TTS (`fr-FR-HenriNeural`) directement sur la Jetson sans dépendre d'un serveur Mac (0€, illimité).
  - **Compatibilité Audio ReSpeaker** : Conversion automatique MP3 ➔ WAV 24 kHz mono (`_convert_mp3_to_wav()`) assurant une restitution parfaite sur l'amplificateur JST 5W via `paplay`.
- [x] **Architecture Découplée "Jetson Direct Cloud" (Mode 2 - Port 8002)** :
  - **Côté Mac** : Serveur TTS ultra-léger `companion_server_tts_mac.py` (Port 8002) et script `start_companion_server_tts.sh`.
  - **Côté Jetson** : Script `test_jetson_direct_cloud.py` exécutant ASR Groq et LLM Gemini 2.0 Flash en direct via Internet, et ne demandant que la synthèse vocale Qwen3-TTS au Mac sur le port 8002.
  - **Gestion Mémoire GPU Metal** : Correction des fuites mémoire MLX (`mx.metal.clear_cache()` + `gc.collect()`, bridage `max_tokens=1024` et `repetition_penalty=1.1`, verrou `asyncio.Lock`), éliminant 100% des saturations RAM et plantages système.
  - **Conservation** : Conservation persistance de la version All-in-One Mac (`companion_server_full_mac.py`, Port 8001).
- [x] **Intégration API ElevenLabs Streaming (Annulé)** : Évalué et annulé au profit de Microsoft Edge-TTS (100% gratuit, illimité, ultra-rapide et direct sur Jetson).
- [ ] **Fallback Vocale Local (Jetson Orin Nano)** : Installer et configurer **Kokoro-ONNX** (`onnxruntime-gpu`) avec la voix française `ff_siwis` sur la Jetson pour assurer le secours hors-ligne en cas de déconnexion Wi-Fi > 2s.
- [ ] **Heartbeat Watchdog (5 Hz)** : Valider la bascule automatique en mode dégradé (LLM local Ollama + Kokoro TTS) en cas d'interruption du signal Wi-Fi.

---

## 🎯 BLOCK 3 : Perception 3D, Regard Actif & IA Physique (OAK-D + Cosmos / LocateAnything)

- [x] **Triade Visuelle & Fusion Spatiale 3D (OAK-D Pro + YOLO-World v2)** :
  - Intégration de YOLO-World v2 Zero-Shot (`yolov8m-worldv2.pt` / `.onnx` / `.engine`) avec NMS permissif et dictionnaire de couleurs vives BGR par classe (`MAIN`, `TELEPHONE`, `PERSONNE`, `TABLE`, `CHAISE`, `BOUTEILLE`).
  - Association tridimensionnelle des boîtes 2D avec la carte de profondeur stéréo pour extraire les coordonnées physiques réelles [X, Y, Z] en mm.
- [x] **Optimisation VPU Myriad X (OAK-D Pro)** :
  - Intégrer le filtre matériel WLS sur le VPU OAK-D pour combler les trous de la profondeur (économie de 25% CPU Jetson).
  - Configurer le nœud matériel **`SpatialLocationCalculator`** sur l'OAK-D pour générer des alertes de sécurité 3D (Z < 500 mm) à < 5 ms.
- [x] **Support du Français & Mappage Multilingue YOLO-World** :
  - Dictionnaire persistant local `fr_en_dictionary.json` (+150 mots) et traduction automatique zéro-ressource via `urllib` dans `yolo_world.py`.
- [x] **Reconnaissance & Identification de Visages (Face Recognition / Tracking)** :
  - Module d'extraction et d'identification faciale ultra-compact (`face_tracker.py` avec SCRFD 500M `det_500m.onnx` 5 points clés + MobileFaceNet ArcFace `w600k_mbf.onnx` 512-dim), lissage temporel sur 5 trames, score centroïde et serveur Web UI MJPEG (http://ubuntu.local:8090) pour enregistrer et reconnaître nommément les visages du foyer.
- [x] **Feuille de Route Discrimination Faciale Intra-Familiale High-Precision (Validée)** :
  - Étape 1 : Passage au modèle haute capacité ArcFace ResNet50 (`w600k_r50.onnx` ~160 Mo, 512-dim) sur GPU CUDA (scores 93%+).
  - Étape 2 : Découpage HD natif Full-Resolution (1920x1080 px) directement sur le flux brut Sony OAK-D Pro (x3.5 densité de pixels optiques sur le visage).
  - Étape 3 : Classifieur SVM à marge maximale local (`sklearn.svm.SVC`) et filtre de déduplication physico-spatiale par trame.
- [x] **Expérience "Active Gaze" & Cognition 3D Déportée sur Mac (`test_active_gaze.py`)** :
  - Capturer le flux RGB 1080p de l'OAK-D Pro et exécuter l'inférence de repérage visuel (*Visual Grounding*) avec **LocateAnything-3B / NVIDIA Cosmos 3D Edge** **déporté sur le Mac M1 Max (64 Go)** via HTTP/gRPC (`server_active_gaze_mac.py`).
  - Asservir le cou en Pan/Tilt pour qu'il centre physiquement l'objet ciblé au milieu du champ de vision ("Regarde la tasse").

### 🚀 Optimisations Avancées du Regard Actif & Fluidification Pan-Tilt (Validées)
- [x] **Inférence TensorRT FP16 Ultra-Rapide 80+ FPS (`yolov8m-worldv2.engine`)** :
  - Compilation locale sur GPU Ampere (57.1 Mo) réduisant la latence de perception à 8-10 ms (cadence 80-120 FPS, VRAM 400 Mo) avec chargement bivalent résilient et repli automatique PyTorch CUDA.
- [x] **Asservissement Physique en Boucle Fermée sur Télémétrie CAN** :
  - Lecture en temps réel de la position angulaire réelle des moteurs `neck.get_state()` à 100 Hz éliminant l'emballement d'angle en fin de course.
- [x] **Verrouillage Statique par Hystérésis Adaptative (65 px à 117 px)** :
  - Élargissement du deadband au centre + filtre d'action angulaire minimal de 0.8° éliminant 100% des micro-tressautements diagonaux à l'arrêt.
- [x] **Gain Proportionnel Dynamique Non-Linéaire Kp(e)** :
  - Variation automatique du gain de 0.20 (centre) à 0.55 (bord du champ) pour une accélération de rattrapage ultra-réactive lors des mouvements récents rapides.
- [x] **Extrapolation Kalman 3D Étendue à 15 Trames (500 ms)** :
  - Maintien continu de la trajectoire par inertie en cas de flou de bougé ou d'occultation temporaire.
- [x] **Notificateur Automatique d'Enrichissement du Dictionnaire** :
  - Suivi des nouveaux mots ajoutés dans `fr_en_dictionary.json` et message de rappel au démarrage pour suggérer une re-compilation 80+ FPS en 1 clic.

---

## 🎯 BLOCK 4 : Cinématique Inverse, Dynamics Pinocchio & LeRobot (Bras & Corps)

- [ ] **SDK Python `Motorbridge` & Contrôle MIT** : Valider les trames de commande MIT (Kp, Kd, theta, dtheta, tau_ff) et la lecture continue de la télémétrie sur les bus CAN 1 Mbps.
- [x] **Prototypage 3D & Recuit Thermique (Sunlu FilaDryer E2)** : Protocole de fabrication des brackets d'épaule (RS-04/RS-03/RS-02) sur Qidi Plus 4 en PETG-CF / PA12-CF / PPA-CF, métrologie de séchage/recuit au Sunlu E2 (110°C) et formalisation dans [11_Prototypage_Mecanique_et_Recuit_Sunlu_E2.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/impression_3d/11_Prototypage_Mecanique_et_Recuit_Sunlu_E2.md).
- [ ] **Calibration Zero-Offset** : Exécuter la procédure d'alignement zéro des encodeurs absolus 14-bit des articulations.
- [ ] **Moteur Dynamique `Pinocchio` (INRIA/LAAS)** :
  - Charger l'URDF complet de D-Bot sous `Pinocchio` sur la Jetson et le Mac.
  - Calculer et injecter le couple de compensation de gravité G(q) via le feedforward tau_ff dans la commande des moteurs.
- [ ] **Intégration Hugging Face `LeRobot`** : Adapter l'interface `LeRobot` pour enregistrer des téléopérations de bras et fabriquer des datasets de démonstration pour l'apprentissage par imitation (*ACT / Diffusion Policy*).
- [ ] **Extension Web UI Flotte Complète** : Étendre l'interface de diagnostic Motorbridge à l'ensemble des 27 moteurs CAN du robot lors de l'assemblage des membres et du torse.

---

## 🎯 BLOCK 5 : Base Documentaire RAG & Maintenance Outillage (Mac M1 Max)

- [ ] **Achèvement de l'Indexation Complète RAG V1** :
  - Finaliser l'indexation incrémentale des 79 documents restants via `Code/rag/index_docs.py` (avec sauvegarde continue du journal `indexed_files.json` document par document).
  - Contrôler l'absence d'erreurs réseau ou de saturation de quota LLM/VLM Gemini.
- [ ] **Contrôle d'Intégrité & Recette du Graphe de Connaissances** :
  - Exécuter `Code/rag/check_integrity.py` pour valider la consistance de la base `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db` (nœuds, arêtes NetworkX, vecteurs NanoVectorDB).
  - Valider des requêtes croisées de test via `Code/rag/ask_rag.py` (modes `naive`, `local`, `global`, `hybrid`).
- [ ] **Mise à Niveau des Outils d'Indexation RAG (Post-Campagne)** :
  - Mettre à jour `lightrag-hku` (1.5.4 ➔ 1.5.7) pour bénéficier du durcissement du graphe, du parsing Markdown optimisé et du support de `USER_PROMPT_PREFIX`.
  - Mettre à jour les dépendances utilitaires : `pypdf` (6.7.5 ➔ 6.18.1), `aiohttp` (3.13.5 ➔ 3.14.3) et `tiktoken` (0.12.0 ➔ 0.14.0).
- [ ] **Qualification de Migration SDK `google-genai` (1.66.0 ➔ 2.23.0)** :
  - Tester la compatibilité ascendante de l'API v2 avec les fonctions d'extraction de `Code/rag/index_docs.py` et la vision VLM (`analyze_image_with_vlm`).
  - Valider la non-régression avant déploiement définitif.

