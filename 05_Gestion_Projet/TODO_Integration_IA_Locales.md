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
*(Architecture hybride : sémantique sur GPU Jetson et géométrie stéréo sur VPU OAK-D)*

- [ ] **Déploiement du modèle de vision** :
  - Télécharger [nvidia/LocateAnything-3B](https://huggingface.co/nvidia/LocateAnything-3B) sur la Jetson Orin Nano.
  - Optimiser le modèle via TensorRT et tester la version quantifiée 4-bit (INT4) pour économiser la mémoire de la Jetson (~1.8 Go).
- [ ] **Interface de détection sémantique (GPU Jetson)** :
  - Créer un script `Code/dbot/vision/locater.py` chargé de recevoir un flux d'images 2D de la caméra OAK-D et une invite textuelle (ex: *"the green screwdriver"*), et de renvoyer les coordonnées de la bounding box 2D `[xmin, ymin, xmax, ymax]`.
- [ ] **Couplage géométrique avec OAK-D (2D → 3D via VPU embarqué)** :
  - Configurer le pipeline DepthAI pour calculer la carte de profondeur stéréo directement sur la puce de la caméra (soulageant l'Orin Nano).
  - Utiliser le nœud matériel **`SpatialLocationCalculator`** (SDK DepthAI) pour extraire dynamiquement les coordonnées spatiales tridimensionnelles `[X, Y, Z]` (en mètres) de la zone d'intérêt (ROI) délimitée par la bounding box 2D calculée par LocateAnything.
  - Mettre en place un filtrage (moyenne spatiale et élimination des aberrations de profondeur) pour sécuriser la mesure.
- [ ] **Pilotage de la cinématique de saisie (Grasping)** :
  - Envoyer les coordonnées `[X, Y, Z]` physiques à l'algorithme de cinématique inverse pour orienter le bras et piloter les servomoteurs Feetech afin de saisir précisément l'objet localisé.

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

- [ ] **Mise en place du serveur d'inférence distant** :
  - Configurer un serveur Ollama local ou une API gRPC/WebSocket sur un ordinateur compagnon du réseau Wi-Fi local (PC fixe avec carte graphique dédiée ou Mac M-Series).
  - Déporter l'exécution du LLM et de la base RAG sur cette machine hôte.
- [ ] **Création du client léger sur la Jetson** :
  - Modifier [llm_client.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/brain/llm_client.py) pour qu'il puisse basculer dynamiquement entre l'adresse IP locale (localhost) et l'adresse IP du serveur compagnon.
- [ ] **Streaming et transport de flux** :
  - Adapter le script de vision pour envoyer les requêtes de localisation (bounding boxes) au modèle de vision (VLM) hébergé à distance, ou tester la transmission des images clés pour l'inférence.
- [ ] **Benchmark comparatif de latence** :
  - Mesurer et comparer précisément :
    - Temps de réponse (Time to First Token)
    - Débit de génération (Tokens/sec)
    - Stabilité de connexion et sensibilité au jitter Wi-Fi.

---

### 🎙️ Phase 9 : Voix Personnalisée D-Bot — CosyVoice 2 en Serveur Local (Mac M2)
*(Solution C — Clonage zéro-shot avec serveur TTS déporté sur Mac, client ultra-léger sur Jetson)*

**Objectif** : Donner à D-Bot une voix unique et reconnaissable en français (masculine ou sur mesure), tout en conservant une latence acceptable pour la conversation (~500-800 ms/phrase). Le Mac M2 héberge le serveur TTS de clonage de voix ; la Jetson Orin Nano reste libérée de cette charge.

---

#### 🏗️ Architecture Globale de la Solution C

```
┌─────────────────────────┐         LAN Wi-Fi (~10-50 ms)         ┌───────────────────────────────────┐
│   Jetson Orin Nano      │  ─── HTTP POST /synthesize ────────►  │   Mac M2 (Serveur TTS CosyVoice)  │
│                         │                                        │                                   │
│  dbot_next :            │  ◄── audio/wav (streaming chunks) ───  │   CosyVoice 2 (0.5B)              │
│  - STT (Nemotron)       │                                        │   + voix de référence encodée     │
│  - LLM (Ollama/Gemini)  │                                        │   + API FastAPI/HTTP              │
│  - Client TTS léger     │                                        │                                   │
│  - Kokoro (fallback)    │                                        └───────────────────────────────────┘
└─────────────────────────┘
```

**Flux d'une interaction** :
1. L'utilisateur parle → Nemotron transcrit (Jetson)
2. Le LLM génère une réponse phrase par phrase (streaming)
3. Chaque phrase est envoyée en POST HTTP au Mac
4. Le Mac CosyVoice génère l'audio WAV avec la voix clonée (~300-700 ms)
5. Le WAV est renvoyé à la Jetson et joué via aplay/paplay
6. Si le Mac est inaccessible → Kokoro local prend le relais automatiquement

---

#### 📦 Étape 1 — Installation de CosyVoice 2 sur le Mac M2

- [ ] **Créer un environnement Python dédié** :
  ```bash
  # Sur le Mac M2
  python3 -m venv ~/.venvs/cosyvoice
  source ~/.venvs/cosyvoice/bin/activate
  ```

- [ ] **Installer les dépendances** :
  ```bash
  pip install cosyvoice2-eu fastapi uvicorn soundfile torch
  ```
  *(Le paquet `cosyvoice2-eu` est le fork optimisé pour le français/allemand de CosyVoice 2.)*

- [ ] **Valider que CosyVoice fonctionne** :
  ```python
  # test_cosyvoice.py — à lancer sur le Mac
  from cosyvoice2_eu import CosyVoice2
  import soundfile as sf
  
  model = CosyVoice2("iic/CosyVoice2-0.5B")
  
  # Test avec voix de référence (10-15s de parole propre dans un fichier .wav)
  for chunk in model.inference_zero_shot(
      "Bonjour, je suis D-Bot, votre assistant robotique.",
      "Texte exact prononcé dans le fichier de référence...",
      open("ma_voix_reference.wav", "rb").read(),
      stream=True
  ):
      sf.write("/tmp/test_output.wav", chunk["tts_speech"].numpy(), 22050)
  ```

---

#### 🎤 Étape 2 — Préparer la Voix de Référence

Le clonage de voix nécessite un **fichier audio de référence** de 10 à 15 secondes, propre (sans bruit de fond), avec le locuteur qui parle de manière naturelle et continue.

- [ ] **Choisir et enregistrer la voix de référence** :
  - Option A : Enregistrer sa propre voix via QuickTime Player ou Audacity (Mac).
  - Option B : Extraire un passage d'un livre audio français libre de droits (LibriVox).
  - Option C : Utiliser un clip d'un acteur (usage personnel uniquement).

- [ ] **Formater le fichier audio de référence** :
  ```bash
  # Convertir en WAV mono, 22050 Hz (format attendu par CosyVoice)
  ffmpeg -i source_audio.mp3 -ac 1 -ar 22050 reference_voice.wav
  ```

- [ ] **Stocker le fichier de référence et son texte** :
  - Placer `reference_voice.wav` dans `~/cosyvoice_server/`
  - Écrire dans `reference_text.txt` le contenu **exact** prononcé dans le fichier audio (nécessaire pour la qualité du clonage).

---

#### 🌐 Étape 3 — Créer le Serveur FastAPI sur le Mac

- [ ] **Créer le script du serveur** dans `Code/dbot_next/tts_server/` :

  **`server_cosyvoice.py`** :
  ```python
  """
  Serveur TTS CosyVoice 2 — A déployer sur le Mac M2
  Expose une API HTTP POST /synthesize sur le réseau LAN local.
  """
  from fastapi import FastAPI, HTTPException
  from fastapi.responses import StreamingResponse
  from pydantic import BaseModel
  from cosyvoice2_eu import CosyVoice2
  import soundfile as sf
  import numpy as np
  import io, os
  
  app = FastAPI(title="D-Bot TTS Server")
  
  # Chemin vers le fichier de référence de voix et son texte
  VOICE_REF_WAV  = os.path.expanduser("~/cosyvoice_server/reference_voice.wav")
  VOICE_REF_TEXT = open(os.path.expanduser("~/cosyvoice_server/reference_text.txt")).read().strip()
  SAMPLE_RATE    = 22050
  
  # Chargement du modèle au démarrage (une seule fois)
  print("⏳ [TTS Server] Chargement de CosyVoice 2...")
  model = CosyVoice2("iic/CosyVoice2-0.5B")
  ref_audio = open(VOICE_REF_WAV, "rb").read()
  print("✅ [TTS Server] Prêt à synthétiser.")
  
  class SynthRequest(BaseModel):
      text: str
      language: str = "fr"
  
  @app.post("/synthesize")
  async def synthesize(req: SynthRequest):
      """Synthétise du texte en audio WAV avec la voix de référence clonée."""
      if not req.text.strip():
          raise HTTPException(status_code=400, detail="Texte vide.")
      try:
          audio_chunks = []
          for chunk in model.inference_zero_shot(
              req.text, VOICE_REF_TEXT, ref_audio, stream=True
          ):
              audio_chunks.append(chunk["tts_speech"].numpy())
          audio = np.concatenate(audio_chunks)
          buf = io.BytesIO()
          sf.write(buf, audio, SAMPLE_RATE, format="WAV")
          buf.seek(0)
          return StreamingResponse(buf, media_type="audio/wav")
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
  
  if __name__ == "__main__":
      import uvicorn
      uvicorn.run(app, host="0.0.0.0", port=7860)
  ```

- [ ] **Lancer le serveur** (à faire avant de démarrer D-Bot) :
  ```bash
  source ~/.venvs/cosyvoice/bin/activate
  python ~/cosyvoice_server/server_cosyvoice.py
  # Serveur accessible sur http://<ip-du-mac>:7860
  ```

- [ ] **Vérifier le bon fonctionnement depuis le Mac lui-même** :
  ```bash
  curl -X POST http://localhost:7860/synthesize \
    -H "Content-Type: application/json" \
    -d '{"text": "Test de synthèse vocale sur le serveur local."}' \
    --output /tmp/test_server.wav && afplay /tmp/test_server.wav
  ```

---

#### 🤖 Étape 4 — Créer le Client TTS sur la Jetson

- [ ] **Créer `Code/dbot_next/audio/tts_cosyvoice_client.py`** :

  ```python
  """
  Client TTS CosyVoice — A déployer sur la Jetson Orin Nano.
  Envoie les phrases au serveur Mac M2 et joue l'audio reçu.
  Repli automatique sur Kokoro si le serveur est inaccessible.
  """
  import os, requests, tempfile, subprocess
  from dbot_next.audio.tts_kokoro import KokoroTTS
  
  TTS_SERVER_URL = os.getenv("DBOT_TTS_SERVER", "http://192.168.68.XXX:7860")
  TIMEOUT_S      = 5.0  # Si pas de réponse en 5s, bascule vers Kokoro
  
  class CosyVoiceClient:
      def __init__(self, server_url: str = TTS_SERVER_URL):
          self.server_url = server_url.rstrip("/")
          self._fallback  = None
          self._server_ok = self._check_server()
  
      def _check_server(self) -> bool:
          try:
              r = requests.get(f"{self.server_url}/docs", timeout=2)
              return r.status_code == 200
          except Exception:
              print(f"⚠ [CosyVoice Client] Serveur {self.server_url} inaccessible → repli sur Kokoro.")
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
                      json={"text": text, "language": "fr"},
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
                  print(f"⚠ [CosyVoice Client] Erreur serveur ({e}) → repli Kokoro.")
                  self._server_ok = False
          # Repli local sur Kokoro
          self._get_fallback().speak(text)
  ```

- [ ] **Configurer l'adresse IP du Mac dans le fichier `.env`** :
  ```bash
  # Ajouter dans ~/dbot/code/.env :
  DBOT_TTS_SERVER=http://192.168.68.XXX:7860
  ```
  *(Remplacer XXX par l'IP LAN de votre Mac, visible depuis la Jetson)*

- [ ] **Modifier `async_conversation.py`** pour utiliser `CosyVoiceClient` à la place de `KokoroTTS` :
  ```python
  # Dans dbot_next/brain/async_conversation.py
  # Remplacer : self.tts = KokoroTTS()
  # Par :
  from dbot_next.audio.tts_cosyvoice_client import CosyVoiceClient
  self.tts = CosyVoiceClient()
  ```

---

#### ✅ Étape 5 — Validation Complète

- [ ] **Test du serveur depuis la Jetson** :
  ```bash
  # Depuis la Jetson, remplacer XXX par l'IP du Mac
  curl -X POST http://192.168.68.XXX:7860/synthesize \
    -H "Content-Type: application/json" \
    -d '{"text": "Bonjour, ceci est un test de voix clonée depuis la Jetson."}' \
    --output /tmp/test_lan.wav && aplay /tmp/test_lan.wav
  ```

- [ ] **Test de la latence LAN** :
  ```bash
  time curl -X POST http://192.168.68.XXX:7860/synthesize \
    -H "Content-Type: application/json" \
    -d '{"text": "Quelle est la latence de synthèse sur le réseau local ?"}' \
    --output /tmp/test_latency.wav
  # Objectif : < 800 ms total
  ```

- [ ] **Test du repli automatique sur Kokoro** : Couper le serveur Mac et vérifier que D-Bot bascule sur Kokoro sans erreur ni plantage.

- [ ] **Test de la boucle conversationnelle complète** :
  ```bash
  bash dbot_next/scripts/run_bot_next.sh
  # Vérifier que la voix clonée est bien utilisée pour toutes les réponses dynamiques.
  ```

---

#### 📝 Notes et Contraintes

| Paramètre | Valeur |
|---|---|
| Modèle | CosyVoice 2 (`iic/CosyVoice2-0.5B`) via paquet `cosyvoice2-eu` |
| Matériel serveur | Mac M2 (Apple Silicon, MPS backend) |
| RAM requise Mac | ~4-5 Go |
| Latence estimée Mac M2 | ~300-700 ms/phrase |
| Latence réseau LAN | ~10-50 ms |
| **Latence totale perçue** | **~500-800 ms/phrase** |
| Audio de référence | WAV mono, 22050 Hz, 10-15 secondes minimum |
| Port du serveur | 7860 (modifiable via variable d'env) |
| Fallback automatique | Kokoro-ONNX GPU sur la Jetson si serveur inaccessible |

