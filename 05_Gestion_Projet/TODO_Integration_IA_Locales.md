# TODO List — Intégration des Modèles d'IA Locales (D-Bot)

Ce document répertorie les tâches et évolutions nécessaires pour l'intégration de modèles d'IA locaux sur la carte NVIDIA Jetson Orin Nano (Super, 8 Go). Cela comprend l'intégration d'un modèle de transcription vocale en streaming à basse latence (**`nvidia/nemotron-3.5-asr-streaming-0.6b`**) et d'un modèle de vision-langage de repérage d'objets sémantique (**`nvidia/LocateAnything-3B`**).

---

## 🎯 Objectifs des évolutions
- **Réduction de la latence vocale :** Passer de ~6 secondes à < 1 seconde de temps de réponse conversationnel.
- **Acquisition audio intelligente :** Détection dynamique de fin de phrase via le VAD matériel du ReSpeaker.
- **Réactivité réflexe (Interruptibilité) :** Détecter des mots-clés d'arrêt d'urgence ("stop") en moins de 150 ms directement depuis le flux audio.
- **Repérage d'objets sémantique (Vocabulaire ouvert) :** Permettre au robot de localiser n'importe quel objet dans l'espace en combinant le VLM (vision-langage) et la carte de profondeur 3D de la caméra OAK-D Pro.

---

## 📋 Liste des Tâches (To-Do List)

### 💻 Phase 1 : Préparation de l'Environnement (Jetson Orin Nano)
- [ ] **Mise à jour JetPack** : S'assurer que le système utilise JetPack 6.2+ pour activer le mode "Super" (67 TOPS, bande passante de 102 Go/s).
- [ ] **Déploiement des conteneurs NVIDIA** : Configurer des conteneurs Docker optimisés via les ressources du *Jetson AI Lab* pour éviter les conflits de dépendances entre PyTorch, CUDA, NeMo et TensorRT.
- [ ] **Installation des dépendances audio/système** :
  - `pip3 install sounddevice numpy`
  - Installer `portaudio19-dev` sur la Jetson (`sudo apt-get install portaudio19-dev`).
- [ ] **Validation initiale des modèles** : Télécharger les poids de Nemotron-3.5-ASR et de LocateAnything-3B sur la Jetson et valider des scripts d'inférence GPU minimaux.

---

### 🎤 Phase 2 : Refactoring du Pipeline Audio (Capture & VAD)
- [ ] **Création de la capture non-bloquante** : 
  - Modifier [audio_io_v2.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/audio/audio_io_v2.py) pour remplacer la commande bloquante `parecord` par un flux d'entrée non-bloquant utilisant un callback `sounddevice` poussant des chunks audio (PCM 16kHz Mono 16-bit) dans une queue thread-safe.
- [ ] **Couplage VAD matériel / ASR** :
  - Utiliser le signal `is_speech` renvoyé par le SDK de la carte ReSpeaker XVF3800 ([respeaker_sdk.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/audio/respeaker_sdk.py)) pour fermer proprement le flux audio et signaler la fin de phrase au décodeur Nemotron.

---

### 🧠 Phase 3 : Implémentation du Décodeur de Streaming (Audio)
- [ ] **Création de `dbot/audio/stt_streaming.py`** :
  - Implémenter une classe `StreamingSTTNemotron` reprenant les paramètres d'initialisation de [stt.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/audio/stt.py) mais orientée streaming.
  - Configurer le prompt d'inférence cible sur `"fr-FR"` pour optimiser la vitesse et la précision du français.
  - Gérer l'état du décodeur (cache interne du modèle FastConformer) entre chaque chunk pour assurer la continuité du contexte.

---

### 🛡️ Phase 4 : Système d'Arrêt d'Urgence et Mots-Clés (Hotwords)
- [ ] **Moteur d'interruption en temps réel** :
  - Ajouter un analyseur de jetons (tokens) en sortie directe de l'ASR streaming.
  - Déclencher un signal d'arrêt matériel instantané si le mot `"stop"`, `"danger"`, `"bloqué"` ou `"arrête"` est détecté dans le flux (latence cible < 150 ms).
  - Connecter ce signal aux contrôleurs moteurs (moteurs Feetech de [motors](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/motors/) et Robstride).

---

### 🔗 Phase 5 : Intégration Globale et Dialogue
- [ ] **Pipeline de conversation asynchrone** :
  - Connecter la sortie finale de la transcription à [llm_client.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/brain/llm_client.py) (Gemini Flash ou Ollama local) dès la détection de la fin de parole.
  - Évaluer la possibilité d'utiliser le mode streaming sur [llm_client.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/brain/llm_client.py) pour envoyer les premiers mots générés par l'IA vers le moteur de synthèse vocale (`tts.py`) pendant que la suite de la phrase est encore en cours de génération.

---

### 👁️ Phase 6 : Intégration de LocateAnything-3B (Visual Grounding)
- [ ] **Déploiement du modèle de vision** :
  - Télécharger [nvidia/LocateAnything-3B](https://huggingface.co/nvidia/LocateAnything-3B) sur la Jetson Orin Nano.
  - Optimiser le modèle via TensorRT et tester la version quantifiée 4-bit (INT4) pour économiser la mémoire de la Jetson (~1.8 Go).
- [ ] **Interface de détection sémantique** :
  - Créer un script `Code/dbot/vision/locater.py` chargé de recevoir un flux d'images 2D de la caméra OAK-D et une invite textuelle (ex: *"the green screwdriver"*), et de renvoyer les coordonnées de la bounding box 2D `[xmin, ymin, xmax, ymax]`.
- [ ] **Couplage géométrique avec OAK-D (2D → 3D)** :
  - Développer le pipeline de projection pour mapper la bounding box 2D sur la carte de profondeur stéréo générée à la volée sur la puce de la caméra OAK-D Pro.
  - Convertir ce rectangle en coordonnées spatiales tridimensionnelles réelles `[X, Y, Z]` (mètres).
- [ ] **Pilotage de la cinématique de saisie (Grasping)** :
  - Envoyer les coordonnées `[X, Y, Z]` physiques à l'algorithme de cinématique inverse pour orienter le bras et piloter les servomoteurs Feetech afin de saisir précisément l'objet localisé.
