# TODO List — Intégration des Modèles d'IA Locales (D-Bot)

Ce document répertorie les tâches et évolutions nécessaires pour l'intégration de modèles d'IA locaux sur la carte NVIDIA Jetson Orin Nano (Super, 8 Go). Cela comprend l'intégration d'un modèle de transcription vocale en streaming à basse latence (**`nvidia/nemotron-3.5-asr-streaming-0.6b`**) et d'un modèle de vision-langage de repérage d'objets sémantique (**`nvidia/LocateAnything-3B`**).

---

## 🎯 Objectifs des évolutions
- **Réduction de la latence vocale :** Passer de ~6 secondes à < 1 seconde de temps de réponse conversationnel.
- **Acquisition audio intelligente :** Détection dynamique de fin de phrase via le VAD matériel du ReSpeaker.
- **Réactivité réflexe (Interruptibilité) :** Détecter des mots-clés d'arrêt d'urgence ("stop") en moins de 150 ms directement depuis le flux audio.
- **Intelligence Physique et Repérage Spatial :** Permettre au robot de localiser n'importe quel objet et de raisonner sur son environnement physique (via des modèles comme LocateAnything ou Cosmos 3 Edge) couplé à la carte de profondeur 3D de la caméra OAK-D Pro.

---

## 📋 Liste des Tâches (To-Do List)

### 💻 Phase 1 : Préparation de l'Environnement (Jetson Orin Nano)
- [ ] **Mise à jour JetPack** : S'assurer que le système utilise JetPack 6.2+ pour activer le mode "Super" (67 TOPS, bande passante de 102 Go/s).
- [ ] **Déploiement des conteneurs NVIDIA** : Configurer des conteneurs Docker optimisés via les ressources du *Jetson AI Lab* pour éviter les conflits de dépendances entre PyTorch, CUDA, NeMo et TensorRT.
- [x] **Installation des dépendances audio/système** :
  - `pip3 install sounddevice numpy`
  - Installer `portaudio19-dev` sur la Jetson (`sudo apt-get install portaudio19-dev`).
- [ ] **Validation initiale des modèles** : Télécharger les poids de Nemotron-3.5-ASR et de LocateAnything-3B sur la Jetson et valider des scripts d'inférence GPU minimaux.

---

### 🎤 Phase 2 : Refactoring du Pipeline Audio (Capture & VAD)
- [x] **Création de la capture non-bloquante** : 
  - Modifier [audio_io_v2.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/audio/audio_io_v2.py) pour remplacer la commande bloquante `parecord` par un flux d'entrée non-bloquant utilisant un callback `sounddevice` poussant des chunks audio (PCM 16kHz Mono 16-bit) dans une queue thread-safe. *(Note: Implémenté via `AudioIOStreaming` avec buffer et processus non bloquant).*
- [x] **Couplage VAD matériel / ASR** :
  - Utiliser le signal `is_speech` renvoyé par le SDK de la carte ReSpeaker XVF3800 ([respeaker_sdk.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/audio/respeaker_sdk.py)) pour fermer proprement le flux audio et signaler la fin de phrase au décodeur Nemotron.

---

### 🧠 Phase 3 : Implémentation du Décodeur de Streaming (Audio)
- [ ] **Création de `dbot/audio/stt_streaming.py`** :
  - Implémenter une classe `StreamingSTTNemotron` reprenant les paramètres d'initialisation de [stt.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/audio/stt.py) mais orientée streaming.
  - Configurer le prompt d'inférence cible sur `"fr-FR"` pour optimiser la vitesse et la précision du français.
  - Gérer l'état du décodeur (cache interne du modèle FastConformer) entre chaque chunk pour assurer la continuité du contexte.

---

### 🛡️ Phase 4 : Système d'Arrêt d'Urgence et Mots-Clés (Hotwords)
- [x] **Moteur d'interruption en temps réel** :
  - Ajouter un analyseur de jetons (tokens) en sortie directe de l'ASR streaming.
  - Déclencher un signal d'arrêt matériel instantané si le mot `"stop"`, `"danger"`, `"bloqué"` ou `"arrête"` est détecté dans le flux (latence cible < 150 ms).
  - Connecter ce signal aux contrôleurs moteurs (moteurs Feetech de [motors](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/motors/) et Robstride).
  *(Note : Le principe d'interruption a été validé différemment via le Barge-In matériel basé sur la simple détection vocale VAD de dbot_next).*

---

### 🔗 Phase 5 : Intégration Globale et Dialogue
- [x] **Pipeline de conversation asynchrone** :
  - Connecter la sortie finale de la transcription à [llm_client.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/brain/llm_client.py) (Gemini Flash ou Ollama local) dès la détection de la fin de parole.
  - Évaluer la possibilité d'utiliser le mode streaming sur [llm_client.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/brain/llm_client.py) pour envoyer les premiers mots générés par l'IA vers le moteur de synthèse vocale (`tts.py`) pendant que la suite de la phrase est encore en cours de génération.
  *(Note : Réalisé avec succès dans l'orchestrateur asynchrone actuel).*

---

### 👁️ Phase 6 : Intelligence Spatiale et Repérage (LocateAnything-3B vs Cosmos 3 Edge)
*(Architecture hybride : Raisonnement / Sémantique sur GPU Jetson et géométrie stéréo sur VPU OAK-D)*

#### 🎯 Expérience de Validation : "Active Gaze" (Regard Actif)
*Objectif : Exploiter le matériel fonctionnel actuel (Caméra OAK-D + 2 moteurs Cou + Audio déporté Mac) pour tester la boucle complète de repérage visuel avec LocateAnything et Cosmos, sans risque mécanique.*

- [ ] **Étape 1 : Le test "Statique" (Vision pure)**
  - Charger LocateAnything sur la Jetson (quantifié INT4 TensorRT).
  - Capturer une image statique via l'OAK-D et exécuter une inférence avec un prompt écrit en dur (ex: "tasse rouge").
  - Valider l'extraction de la Bounding Box 2D et mesurer le temps d'inférence (latence GPU).
- [ ] **Étape 2 : L'asservissement du Cou (Gaze Tracking)**
  - Interfacer le résultat de la Bounding Box avec `test_neck.py` (`NeckController`).
  - Convertir l'écart pixel (centre objet vs centre caméra) en angles Pan/Tilt.
  - Asservir les moteurs pour que le robot centre physiquement la cible dans son champ de vision.
- [ ] **Étape 3 : Le test vocal complet & Comparatif Cosmos**
  - Raccorder la boucle audio (Nemotron/Mac) pour que l'invite textuelle soit dictée à la voix.
  - Répéter le test complet avec Cosmos 3 Edge.
  - Comparer la latence et la compréhension de consignes abstraites entre les deux modèles.

#### ⚙️ Implémentation Détaillée
- [ ] **Déploiement et Test de LocateAnything-3B (Baseline Visual Grounding)** :
  - Télécharger [nvidia/LocateAnything-3B](https://huggingface.co/nvidia/LocateAnything-3B) sur la Jetson Orin Nano.
  - Optimiser via TensorRT (version quantifiée INT4) pour valider le pipeline d'extraction de bounding boxes 2D depuis une invite textuelle.
- [ ] **Évaluation de NVIDIA Cosmos 3 Edge (World Model pour l'IA Physique)** :
  - *Objectif :* Évaluer Cosmos 3 Edge (~4B paramètres) comme cerveau spatial "tout-en-un" en remplacement/super-ensemble de LocateAnything.
  - Quantifier le modèle en INT4 via TensorRT pour tenir dans les 8 Go unifiés de la Jetson.
  - Tester ses capacités de "Physical Reasoning" : au lieu de renvoyer de simples coordonnées, lui faire évaluer la scène, le contexte physique et la faisabilité de préhension (Grasping).
- [ ] **Interface de détection et Raisonnement (GPU Jetson)** :
  - Créer un script `Code/dbot/vision/test_active_gaze.py` chargé de recevoir le flux d'images 2D de la caméra OAK-D.
  - Comparer la latence et la pertinence entre la détection sémantique stricte (LocateAnything) et le raisonnement physique embarqué (Cosmos 3 Edge).
- [ ] **Couplage géométrique avec OAK-D (2D → 3D via VPU embarqué)** :
  - Configurer le pipeline DepthAI pour calculer la carte de profondeur stéréo directement sur la puce de la caméra (soulageant l'Orin Nano).
  - Utiliser le nœud matériel **`SpatialLocationCalculator`** (SDK DepthAI) pour extraire dynamiquement les coordonnées spatiales tridimensionnelles `[X, Y, Z]` (en mètres) de la zone d'intérêt ciblée par l'IA.
  - Mettre en place un filtrage (moyenne spatiale et élimination des aberrations de profondeur) pour sécuriser la mesure.
- [ ] **Pilotage de la cinématique de saisie (Grasping)** :
  - Envoyer les coordonnées `[X, Y, Z]` physiques à l'algorithme de cinématique inverse pour orienter le bras et piloter les servomoteurs Feetech afin de saisir l'objet ou exécuter l'action prédite par Cosmos.

---

### 🗣️ Phase 7 : Intégration de la Synthèse Vocale Générative (Kokoro-ONNX)
- [ ] **Installation des dépendances de Kokoro** :
  - Installer `kokoro-onnx` et `onnxruntime-gpu` dans l'environnement Jetson pour garantir l'accélération matérielle GPU (via CUDA Execution Provider).
- [ ] **Acquisition du modèle et des voix** :
  - Récupérer les poids du modèle Kokoro-82M exporté en ONNX (`kokoro-v0_19.onnx` ou ultérieur).
  - Télécharger le fichier de configuration et les matrices de voix (`voices.bin` contenant la voix française féminine `ff_siwis`).
- [ ] **Refactoring de la classe TTS (`dbot/audio/tts.py`)** :
  - Implémenter la classe `KokoroTTS` (ou adapter `LocalTTS`) pour charger le modèle ONNX en VRAM et générer le flux audio à partir du texte en français.
  - S'assurer que le pipeline génère les fichiers WAV temporaires de manière non bloquante avec une latence d'inférence cible < 150 ms.
- [ ] **Optimisation par découpage de phrases (Streaming TTS)** :
  - Associer le streaming de texte du LLM (Phase 5) à un système de découpage par ponctuation (ex : virgules, points) pour lancer la synthèse vocale de la première partie de la phrase pendant que l'IA génère la suite.

---

### 🌐 Phase 8 : Architecture Distribuée / Calcul Déporté (Alternative Wi-Fi)
*(À tester et comparer après validation des méthodes 100% locales pour optimiser la latence globale et libérer de la mémoire sur la Jetson Orin Nano)*

- [x] **Mise en place du serveur d'inférence distant** :
  - Configurer un serveur Ollama local ou une API gRPC/WebSocket sur un ordinateur compagnon du réseau Wi-Fi local (PC fixe avec carte graphique dédiée ou Mac M-Series).
  - Déporter l'exécution du LLM et de la base RAG sur cette machine hôte.
- [x] **Création du client léger sur la Jetson** :
  - Modifier [llm_client.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/brain/llm_client.py) pour qu'il puisse basculer dynamiquement entre l'adresse IP locale (localhost) et l'adresse IP du serveur compagnon.
- [x] **Streaming et transport de flux** :
  - Adapter le script de vision pour envoyer les requêtes de localisation (bounding boxes) au modèle de vision (VLM) hébergé à distance, ou tester la transmission des images clés pour l'inférence.
*(Note : Validé et implémenté de manière robuste à travers la Phase 10).*
- ### 🎙️ Phase 9 : Voix Personnalisée D-Bot — F5-TTS Français en Serveur Local (Mac)
*(Solution C finale — Clonage avec F5-TTS déporté sur Mac, client ultra-léger et fallback Kokoro sur Jetson)*

**Objectif** : Donner à D-Bot une voix unique, naturelle et reconnaissable en français (timbre issu du sample "La CAF"), tout en conservant une latence acceptable. Le Mac (M1 Max Pro) héberge le serveur TTS F5-TTS accéléré par le GPU (MPS) ; la Jetson Orin Nano reste libérée de cette charge.

---

#### 🏗️ Architecture Globale de la Solution C

```
┌─────────────────────────┐         LAN Wi-Fi (~10-50 ms)         ┌───────────────────────────────────┐
│   Jetson Orin Nano      │  ─── HTTP POST /synthesize ────────►  │   Mac M1 Max (Serveur F5-TTS)     │
│                         │                                        │                                   │
│  dbot_next :            │  ◄── audio/wav (streaming/fichier) ──  │   F5-TTS (Français)               │
│  - STT (Nemotron)       │                                        │   + voix de référence CAF         │
│  - LLM (Ollama/Gemini)  │                                        │   + API FastAPI/HTTP (7860)       │
│  - Client TTS léger     │                                        │                                   │
│  - Kokoro (fallback)    │                                        └───────────────────────────────────┘
└─────────────────────────┘
```

**Flux d'une interaction** :
1. L'utilisateur parle → Nemotron transcrit (Jetson)
2. Le LLM génère une réponse phrase par phrase (streaming)
3. Chaque phrase est envoyée en POST HTTP au Mac
4. Le Mac F5-TTS génère l'audio WAV avec la voix clonée (~1.5s - 3s)
5. Le WAV est renvoyé à la Jetson et joué via `aplay`
6. Si le Mac est inaccessible → Kokoro local (Jetson GPU) prend le relais automatiquement

---

#### 📦 Étape 1 — Installation de F5-TTS sur le Mac

- [x] **Créer l'environnement et installer les dépendances** :
  ```bash
  python3.11 -m venv ~/.venvs/cosyvoice
  source ~/.venvs/cosyvoice/bin/activate
  pip install f5-tts fastapi uvicorn soundfile torch torchaudio torchcodec setuptools<=80.10.2
  ```

- [x] **Vérifier l'accès au GPU Apple Silicon (MPS)** :
  ```python
  import torch
  assert torch.backends.mps.is_available(), "MPS non disponible !"
  ```

---

#### 🎤 Étape 2 — Voix de Référence et Modèle Français

- [x] **Télécharger et valider la voix de référence** :
  * Fichier source : `/Users/davidsergent/Downloads/LA-CAF-MIX-RADIO.mp3`
  * Texte de référence associé :
    > "Vous avez déclaré être sans ressources et vous toucher à ce titre plusieurs aides de votre CAF. C'est étrange car l'Ursafe nous dit que vous êtes cadres supérieurs. En CDI, curieux, non ?"

- [x] **Télécharger le checkpoint F5-TTS français (RASPIAUDIO)** :
  * Fichier de poids : `model_last_reduced.pt` (téléchargé et mis en cache via `cached_path`)
  * Vocabulaire : `vocab.txt` (téléchargé et mis en cache)

---

#### 🌐 Étape 3 — Créer le Serveur FastAPI sur le Mac

Le script du serveur est opérationnel dans le dépôt :
👉 **[server_f5tts.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/tts_server/server_f5tts.py)**

- [ ] **Lancement automatique du serveur au démarrage (Optionnel)** :
  ```bash
  source ~/.venvs/cosyvoice/bin/activate
  python "/Users/Shared/Mon Google Drive Physique/Documentation/Code/dbot_next/tts_server/server_f5tts.py"
  # Serveur accessible sur le port 7860
  ```

---

#### 🤖 Étape 4 — Créer le Client TTS sur la Jetson

- [ ] **Créer `Code/dbot_next/audio/tts_f5tts_client.py`** :

  ```python
  """
  Client TTS F5-TTS — A déployer sur la Jetson Orin Nano.
  Envoie les phrases au serveur Mac M1 Max et joue l'audio reçu.
  Repli automatique sur Kokoro local si le serveur est inaccessible.
  """
  import os, requests, tempfile, subprocess
  from dbot_next.audio.tts_kokoro import KokoroTTS
  
  TTS_SERVER_URL = os.getenv("DBOT_TTS_SERVER", "http://192.168.68.XXX:7860")
  TIMEOUT_S      = 6.0  # Temps max avant bascule automatique sur Kokoro
  
  class F5TTSClient:
      def __init__(self, server_url: str = TTS_SERVER_URL):
          self.server_url = server_url.rstrip("/")
          self._fallback  = None
          self._server_ok = self._check_server()
  
      def _check_server(self) -> bool:
          try:
              r = requests.get(f"{self.server_url}/status", timeout=2)
              return r.status_code == 200 and r.json().get("status") == "ready"
          except Exception:
              print(f"⚠ [F5-TTS Client] Serveur {self.server_url} inaccessible → repli sur Kokoro.")
              return False
  
      def _get_fallback(self) -> KokoroTTS:
          if self._fallback is None:
              self._fallback = KokoroTTS()
          return self._fallback
  
      def speak(self, text: str):
          if not text:
              return
          if self._server_ok:
              try:
                  r = requests.post(
                      f"{self.server_url}/synthesize",
                      json={"text": text},
                      timeout=TIMEOUT_S
                  )
                  if r.status_code == 200:
                      with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                          tf.write(r.content)
                          tmp_path = tf.name
                      subprocess.run(["aplay", tmp_path], check=True, stderr=subprocess.DEVNULL)
                      os.remove(tmp_path)
                      return
              except Exception as e:
                  print(f"⚠ [F5-TTS Client] Erreur serveur ({e}) → repli Kokoro.")
                  self._server_ok = False
          # Repli local sur Kokoro
          self._get_fallback().speak(text)
  ```

- [ ] **Configurer l'adresse IP du Mac dans le fichier `.env` de la Jetson** :
  ```bash
  # Ajouter dans ~/dbot/code/.env :
  DBOT_TTS_SERVER=http://192.168.68.XXX:7860
  ```

- [ ] **Modifier `async_conversation.py`** pour utiliser `F5TTSClient` :
  ```python
  # Dans dbot_next/brain/async_conversation.py
  # Remplacer : self.tts = KokoroTTS()
  # Par :
  from dbot_next.audio.tts_f5tts_client import F5TTSClient
  self.tts = F5TTSClient()
  ```

---

#### ✅ Étape 5 — Validation Complète

- [ ] **Test du serveur depuis la Jetson** :
  ```bash
  curl -X POST http://192.168.68.XXX:7860/synthesize \
    -H "Content-Type: application/json" \
    -d '{"text": "Bonjour, ceci est un test de voix F5-TTS déportée."}' \
    --output /tmp/test_lan.wav && aplay /tmp/test_lan.wav
  ```

- [ ] **Test de la latence LAN** :
  ```bash
  time curl -X POST http://192.168.68.XXX:7860/synthesize \
    -H "Content-Type: application/json" \
    -d '{"text": "Test de vitesse."}' \
    --output /tmp/test_latency.wav
  # Objectif : < 3.0s total après warm-up
  ```

- [ ] **Test du repli automatique sur Kokoro** : Couper le serveur sur le Mac et vérifier que D-Bot bascule sur Kokoro local sans erreur.

---

#### 📝 Notes et Contraintes

| Paramètre | Valeur |
|---|---|
| Modèle | F5-TTS Français (`RASPIAUDIO/F5-French-MixedSpeakers-reduced`) |
| Matériel serveur | Mac M1 Max (GPU MPS) |
| RAM requise Mac | ~1.5 Go |
| Latence moyenne Mac | ~2.0s - 3.5s par phrase (avec `nfe_step=16`) |
| Transport LAN Wi-Fi | ~10-50 ms |
| Audio de référence | `LA-CAF-MIX-RADIO.mp3` |
| Fallback automatique | Kokoro local ONNX (GPU Jetson Orin Nano) |

- [ ] **Test de la boucle conversationnelle complète** :
  ```bash
  bash dbot_next/scripts/run_bot_next.sh
  # Vérifier que la voix clonée est bien utilisée pour toutes les réponses dynamiques.
  ```

---

### 🎙️ Phase 10 : Centralisation de l'Intelligence en Streaming (Gemini + Qwen3-TTS VoiceDesign MLX)
*(Solution Finale Sélectionnée — Inférence déportée sur Mac, streaming de phrases via WebSocket, et fallback local)*

**Objectif** : Atteindre un temps de réaction conversationnel sous la barre de la seconde (~800 ms) avec une voix française d'une qualité inégalée (VoiceDesign), tout en centralisant le traitement du LLM (Gemini 2.0 Flash) et de la génération audio sur le Mac compagnon (Apple Silicon GPU).

#### 🏗️ Architecture Globale de la Solution
```
    [ HUMAIN ] 
        │ (Parole)
        ▼
┌─────────────────────────────────────────────────────────────┐
│ JETSON ORIN NANO (Robot D-Bot)                              │
│                                                             │
│ 1. Capture Audio & VAD (sounddevice)                        │
│ 2. Transcription ASR (Nemotron local)                       │
│ 3. Envoi du prompt texte brut via WebSocket                 │
└─────────────────────────────────────────────────────────────┘
        │
        │ (Lien LAN Wi-Fi / Filaire) ~10 ms
        ▼
┌─────────────────────────────────────────────────────────────┐
│ MAC M1 MAX PRO (Serveur Central LLM + TTS)                  │
│                                                             │
│ 4. Appel Gemini 2.0 Flash (SSE Streaming API avec alt=sse)  │
│ 5. Découpe des phrases et envoi immédiat du texte au robot  │
│ 6. Inférence Qwen3-TTS (1.7B VoiceDesign MLX 8-bit)         │
└─────────────────────────────────────────────────────────────┘
        │
        │ (Streaming WebSocket de Chunks Audio PCM 24kHz) ~10 ms
        ▼
┌─────────────────────────────────────────────────────────────┐
│ JETSON ORIN NANO (Lecture & Historique)                     │
│                                                             │
│ 7. Lecture de flux brut (PCM) via aplay ou paplay           │
│ 8. Gestion de l'interruption (Barge-In)                     │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
    [ HUMAIN ] (Entend la réponse en < 900 ms)
```

#### 📦 Fichiers Implémentés
1. **Serveur Mac Compagnon** : [server_qwen3_central.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/tts_server/server_qwen3_central.py)
   * Initialise le modèle quantifié `Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit` via le framework `mlx-audio`.
   * Gère le streaming Gemini et l'envoi progressif des chunks PCM audio 24kHz au format JSON (base64).
2. **Client Jetson** : [tts_qwen3_central_client.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/audio/tts_qwen3_central_client.py)
   * Client WebSocket asynchrone gérant la reconnexion et le décodage.
   * Dirige le flux audio brut directement vers l'entrée standard d'un processus `aplay` (ou `paplay`) persistant pour une lecture fluide et sans latence d'initialisation.
3. **Orchestrateur** : [async_conversation.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/brain/async_conversation.py)
   * Intègre la logique du client centralisé avec reconnexion automatique.
   * **Barge-In** : Envoie un signal d'interruption `{ "type": "interrupt" }` au serveur Mac pour stopper l'inférence dès que l'utilisateur commence à parler.
   * **Fallback local automatique** : Si le serveur du Mac n'est pas joignable sous 2.0s, active de manière transparente le LLM local (Ollama) et le TTS local (Kokoro-ONNX).

---

#### 🧪 Performances mesurées (Mac M1 Max Pro)
- **Latence Premier Texte (Gemini)** : **572 ms**
- **Latence Premier Audio (TTFA Qwen3-TTS)** : **816 ms** ⚡ (Inférence MLX 8-bit avec chunks de 0.4s)
- **RTF (Real-Time Factor)** : **0.36x** (génère l'audio 2.7x plus vite que sa durée de lecture)

---

#### 🗣️ Configuration de la Voix (Masculine / Féminine)
Le prompt de conception de la voix (VoiceDesign) se configure directement dans le script du serveur [server_qwen3_central.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/tts_server/server_qwen3_central.py).

##### Pour une voix féminine par défaut (Voix actuelle) :
```python
INSTRUCT_FR = (
    "A sophisticated young French woman speaking with a soft, elegant, native French accent. "
    "The tone is calm, clear, and professional."
)
```

##### Pour basculer sur une voix masculine chaleureuse :
Modifiez la variable `INSTRUCT_FR` dans [server_qwen3_central.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/tts_server/server_qwen3_central.py) :
```python
INSTRUCT_FR = (
    "A friendly male voice with a warm, natural, native French accent and a smooth, steady cadence. "
    "Very clear pronunciation."
)
```
*Note : Pour appliquer le changement de voix, il suffit de modifier cette variable et de relancer le script sur le Mac compagnon.*

---

### ⚙️ Phase 11 : Architecture Matérielle Décentralisée (Hiérarchie Biologique)
*(Objectif : Libérer 40 à 60% de CPU/GPU sur la Jetson pour l'IA (Cosmos 3 Edge) en déléguant le contrôle temps réel à des microcontrôleurs dédiés, et améliorer la sécurité mécanique).*

- [x] **Acquisition et Modification Matérielle** :
  - Commander 2x microcontrôleurs **Teensy 4.1**.
  - Commander 2x **Shields "Teensy 4.1 Triple CAN Board"** (SK Pang Electronics via leur site UK ou Buyzero Allemagne). Ils intègrent les transceivers, le régulateur de tension et un écran LCD de télémétrie.
  - Commander 2x **Serial Bus Servo Adapter (A)** (Waveshare SKU: 25514, ~5€) pour l'interface ESP32 <-> Feetech.
  - Déposer (retirer) les adaptateurs USB-CAN (InnoMaker et CANable Pro) de la Jetson. Ils seront conservés uniquement comme outils de débogage sur un PC annexe.
- [x] **Le "Cervelet" : Locomotion et Cinématique (Architecture Double Teensy 4.1)** :
  - Implémenter une séparation matérielle via 2 microcontrôleurs Teensy 4.1 (600 MHz, 3x CAN FD chacun).
  - **Teensy #1 (Lower Body)** : Gère exclusivement l'équilibre, l'IK des jambes et de la taille à 1000Hz.
  - **Teensy #2 (Upper Body)** : Gère l'IK des bras et du cou.
  - *Bénéfice :* Élimine les adaptateurs USB-CAN (InnoMaker/CANable) du robot, décuple la bande passante (6 bus CAN FD) et permet à la Jetson de ne transmettre que des ordres de haut niveau (ex: "Marche à 2km/h", coordonnées X,Y,Z).
  - *Documenté :* Choix du matériel (Shields SK Pang) et architecture physique (USB vs Ethernet) intégrés dans `FINAL_CONSOLIDE_02_Electronique_et_Energie.md`.
- [x] **Les "Ganglions" : Smart Hands Autonomes (ESP32-S3)** :
  - Conserver l'ESP32-S3 (Micro-Hub Tactile) actuel des mains, mais lui confier le pilotage direct (Série TTL) des moteurs Feetech.
  - *Bénéfice :* Boucle de "Force Feedback" locale ultra-rapide (2 ms). L'ESP32 lit les capteurs eFlesh (MLX90393) et ajuste la force de préhension des Feetech de manière autonome, sans aucun aller-retour vers la Jetson.
  - *Documenté :* Intégré en tant que source de vérité dans `GUIDE_COMPLET_Fabrication_et_Montage_DHand_V1.md`.
- [x] **La "Moelle Épinière" : Système Réflexe Avancé (Sony Spresense)** :
  - Élever le rôle de la carte Sony Spresense existante (qui lit l'IMU Torse à 416Hz) en véritable centre de sécurité matériel.
  - *Amélioration du réflexe :* Câblage hybride (Interruption Matérielle sur D2 + UART sur D0/D1) vers les Teensys.
  - *Bénéfice :* En cas de chute inévitable, la broche d'interruption permet aux Teensys de passer instantanément (< 1 ms) les moteurs en mode "Amortisseur" (Damping). Le robot absorbe le choc en s'effondrant en douceur, protégeant les réducteurs.
  - *Documenté :* Brochage et Avertissement Critique (3.3V) intégrés dans `FINAL_CONSOLIDE_02_Electronique_et_Energie.md` (Section 5.1).

---

### 📝 Notes d'Architecture : Pourquoi le Teensy 4.1 et vision long-terme (STM32)
*(Réflexion sur l'évolution vers un standard industriel)*

- **Le choix actuel (Teensy 4.1)** :
  - C'est le "Sweet Spot" pour le prototypage D-Bot : offre 95% des performances nécessaires (600 MHz, 3x CAN FD) pour 10% de la complexité de développement par rapport à un système industriel.
  - Utilise l'écosystème Arduino/Teensyduino (librairies prêtes à l'emploi comme `FlexCAN_T4`).
- **Vision V2 / Industrialisation (Gamme STM32H7)** :
  - Si le robot devait être industrialisé ou requérir un contrôle d'une précision absolue (zéro jitter temporel), il faudra migrer vers une architecture **STM32H7** (ex: cartes Nucleo) programmée en C/C++ Baremetal ou avec un RTOS (Zephyr, FreeRTOS, micro-ROS).
  - *Déterminisme :* Le STM32 permet un accès bas niveau aux registres (TCM, DMA, NVIC) garantissant un contrôle PID à 1000 Hz exact, sans les interruptions de bas niveau de l'écosystème Arduino.
  - *Débogage :* Accès matériel natif via sondes ST-LINK (JTAG/SWD) pour un débogage pas-à-pas en temps réel et profiling (très complexe à obtenir sur Teensy).
  - *Pérennité & Sécurité :* Puces garanties 10-15 ans par STMicroelectronics, répondant aux normes de sécurité automobile/industrielle (SIL/ASIL), et facilement intégrables sur un circuit imprimé (PCB) sur mesure pour le torse du robot.
