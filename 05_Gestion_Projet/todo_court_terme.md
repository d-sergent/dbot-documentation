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
- [x] **Stratégie d'Alimentation 48V à 3 Niveaux** : Schéma d'alimentation validé (Wanptek 60V/5A, MeanWell LRS-600-48 600W, Batterie 48V 13S NMC).
- [x] **Triade Visuelle Temps Réel & Fusion Spatiale 3D** : Couplage OAK-D Pro + YOLO-World v2 Zero-Shot + SpatialFusion (`test_triad_vision.py`) avec détection multi-boîtes hiérarchique, classification multicolore et coordonnées $3D$ réelles $(X, Y, Z)$ en mm.
- [x] **Déport VPU Myriad X (OAK-D Pro)** : Intégration du filtre matériel WLS et du nœud `SpatialLocationCalculator` ($Z < 500\text{ mm}$) dans `oak_camera.py`.
- [x] **Motorbridge Web UI & Contrôle du Cou** : Diagnostic temps réel et asservissement fluide des moteurs du cou Pan/Tilt RS-05 (`web_ui.py` + `neck.py`).
- [x] **Support du Français & Mappage Multilingue YOLO-World** : Dictionnaire persistant local `fr_en_dictionary.json` (+150 mots) et traduction automatique zéro-ressource via `urllib` dans `yolo_world.py`.

---

## 🎯 BLOCK 1 : Validation Physique Tête / Cou & Alimentation Atelier (Priorité Immédiate)

- [ ] **Démontage du casque** : Libérer l'accès aux mécanismes et aux 2 moteurs du cou RS-05 (Pan & Tilt).
- [ ] **Câblage & Longueur de câbles RS-05** : Raccorder les moteurs et ajuster les longueurs pour garantir les rotations sans contrainte ni tension.
- [x] **Tableau de Bord Web UI (`Motorbridge` Web UI)** : Serveur léger Web UI développé dans `Code/dbot/motors/web_ui.py` sur la Jetson Orin Nano pour contrôler et visualiser en temps réel la télémétrie des 2 moteurs RS-05 du cou (angles, températures, tension, erreurs CAN0) depuis le navigateur du Mac (`http://ubuntu.local:8080`).
- [x] **Premier test dynamique du Cou (Sans Casque)** : Valider les rotations Pan/Tilt via `web_ui.py` et `test_neck.py` avec mouvements LERP fluides et non-bloquants.
- [ ] **Remontage du casque & Butées logicielles** : Définir et verrouiller les angles limites dans `config.py` pour éviter tout choc mécanique entre le casque et la structure.
- [ ] **Orientation Tête sur DoA Audio** : Coupler la position angulaire des RS-05 avec la direction DoA (0-360°) de la ReSpeaker pour orienter la tête vers la voix.
- [ ] **Intégration Simultanée des Capteurs Tête** : Brancher et valider la marche simultanée de l'OAK-D Pro, du ReSpeaker et des moteurs du cou.
- [ ] **Station d'Alimentation Atelier 600W** : Imprimer le boîtier 3D `RS-power-Top Cover.stp` et assembler le bloc MeanWell LRS-600-48 (48V / 12.5A) avec connecteurs XT30 2+2.

---

## 🎯 BLOCK 2 : Synthèse Vocale HD Streaming & Solution Secours Locale

- [ ] **Serveur TTS Streaming HD Compagnon (Mac)** : Finaliser et valider `server_qwen3_central.py` (Qwen3-TTS / F5-TTS via MLX-Audio) avec streaming WebSocket/HTTP (latence < 200 ms).
- [ ] **Fallback Vocale Local (Jetson Orin Nano)** : Installer et configurer **Kokoro-ONNX** (`onnxruntime-gpu`) avec la voix française `ff_siwis` sur la Jetson pour assurer le secours hors-ligne en cas de déconnexion Wi-Fi > 2s.
- [ ] **Heartbeat Watchdog (5 Hz)** : Valider la bascule automatique en mode dégradé (LLM local Ollama + Kokoro TTS) en cas d'interruption du signal Wi-Fi.

---

## 🎯 BLOCK 3 : Perception 3D, Regard Actif & IA Physique (OAK-D + Cosmos / LocateAnything)

- [x] **Triade Visuelle & Fusion Spatiale 3D (OAK-D Pro + YOLO-World v2)** :
  - Intégration de YOLO-World v2 Zero-Shot (`yolov8m-worldv2.pt` / `.onnx` / `.engine`) avec NMS permissif et dictionnaire de couleurs vives BGR par classe (`MAIN`, `TELEPHONE`, `PERSONNE`, `TABLE`, `CHAISE`, `BOUTEILLE`).
  - Association tridimensionnelle des boîtes $2D$ avec la carte de profondeur stéréo pour extraire les coordonnées physiques réelles $[X, Y, Z]$ en mm.
- [x] **Optimisation VPU Myriad X (OAK-D Pro)** :
  - Intégrer le filtre matériel WLS sur le VPU OAK-D pour combler les trous de la profondeur (économie de 25% CPU Jetson).
  - Configurer le nœud matériel **`SpatialLocationCalculator`** sur l'OAK-D pour générer des alertes de sécurité $3D$ ($Z < 500\text{ mm}$) à $< 5\text{ ms}$.
- [x] **Support du Français & Mappage Multilingue YOLO-World** :
  - Dictionnaire persistant local `fr_en_dictionary.json` (+150 mots) et traduction automatique zéro-ressource via `urllib` dans `yolo_world.py`.
- [ ] **Reconnaissance & Identification de Visages (Face Recognition / Tracking)** :
  - Ajouter un module d'extraction d'embeddings faciaux (`face_tracker.py` / MobileFaceNet) pour reconnaître et identifier nommément les visages des membres du foyer.
- [ ] **Expérience "Active Gaze" & Cognition 3D Déportée sur Mac (`test_active_gaze.py`)** :
  - Capturer le flux RGB 1080p de l'OAK-D Pro et exécuter l'inférence de repérage visuel (*Visual Grounding*) avec **LocateAnything-3B / NVIDIA Cosmos 3D Edge** **déporté sur le Mac M1 Max (64 Go)** via HTTP/gRPC.
  - Asservir le cou en Pan/Tilt pour qu'il centre physiquement l'objet ciblé au milieu du champ de vision ("Regarde la tasse").

---

## 🎯 BLOCK 4 : Cinématique Inverse, Dynamics Pinocchio & LeRobot (Bras & Corps)

- [ ] **SDK Python `Motorbridge` & Contrôle MIT** : Valider les trames de commande MIT ($K_p, K_d, \theta, \dot{\theta}, \tau_{ff}$) et la lecture continue de la télémétrie sur les bus CAN 1 Mbps.
- [ ] **Calibration Zero-Offset** : Exécuter la procédure d'alignement zéro des encodeurs absolus 14-bit des articulations.
- [ ] **Moteur Dynamique `Pinocchio` (INRIA/LAAS)** :
  - Charger l'URDF complet de D-Bot sous `Pinocchio` sur la Jetson et le Mac.
  - Calculer et injecter le couple de compensation de gravité $G(q)$ via le feedforward $\tau_{ff}$ dans la commande des moteurs.
- [ ] **Intégration Hugging Face `LeRobot`** : Adapter l'interface `LeRobot` pour enregistrer des téléopérations de bras et fabriquer des datasets de démonstration pour l'apprentissage par imitation (*ACT / Diffusion Policy*).
- [ ] **Extension Web UI Flotte Complète** : Étendre l'interface de diagnostic Motorbridge à l'ensemble des 27 moteurs CAN du robot lors de l'assemblage des membres et du torse.
