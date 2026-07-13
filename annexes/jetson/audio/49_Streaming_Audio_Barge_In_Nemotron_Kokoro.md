# 49 — Architecture Audio Temps Réel (Streaming STT, Kokoro-ONNX et Barge-In)

> *Document créé en Juillet 2026 — Documentation de la stack expérimentale D-Bot Next.*

Ce document détaille l'architecture, l'installation et le protocole de test de la nouvelle stack audio avancée **D-Bot Next** (`Code/dbot_next/`). Cette stack introduit le traitement de la parole en continu (streaming) et l'interruptibilité naturelle du robot (*Barge-In*).

---

## 1. Objectifs de la Stack D-Bot Next

La stack audio initiale (V1/V2) fonctionnait par enregistrements de fichiers entiers (via `arecord` / `parecord`), ce qui imposait une latence importante (~6 secondes entre la fin de phrase de l'utilisateur et le début de parole du robot). 

La stack **D-Bot Next** résout ce problème en introduisant :
1.  **L'acquisition continue non bloquante** (`sounddevice`) avec découpage en chunks de 160 ms.
2.  **La reconnaissance vocale en continu** (Streaming ASR) via `nvidia/nemotron-3.5-asr-streaming-0.6b` exécuté sur GPU (CUDA).
3.  **La synthèse vocale générative ultra-rapide** (Kokoro-ONNX) avec accélération GPU, permettant de démarrer la parole en moins de 150 ms.
4.  **L'interruptibilité en temps réel (Barge-In)** : Si l'utilisateur parle pendant que le robot s'exprime, le son se coupe immédiatement et le robot se remet en écoute.

---

## 2. Structure des Fichiers

Tous les développements de cette stack sont isolés dans `Code/dbot_next/` :

*   **`audio/audio_io_streaming.py`** : Gère la capture audio en tâche de fond via callback `sounddevice` et interroge le SDK USB du ReSpeaker pour coupler le statut du VAD matériel.
*   **`audio/stt_streaming.py`** : Décodeur de streaming basé sur NeMo (`BatchedFrameASRRNNT`). Il intègre également la détection à la volée des mots-clés d'interruption (*"stop"*, *"arrête"*).
*   **`audio/tts_kokoro.py`** : Synthétiseur Kokoro-82M ONNX utilisant `onnxruntime-gpu` (CUDA). La lecture audio s'effectue via des processus asynchrones (`subprocess.Popen` sur aplay/paplay) pour être interruptible instantanément.
*   **`brain/llm_client_streaming.py`** : Version avec streaming de réponse (Gemini streamGenerateContent et Ollama local `stream=True`).
*   **`brain/async_conversation.py`** : Automate d'états principal coordonnant l'écoute, la réflexion et la parole.

---

## 3. Installation des Dépendances (sur la Jetson)

Exécutez ces commandes depuis la Jetson Orin Nano pour installer les outils requis :

```bash
# 1. Dépendances système pour l'acquisition audio
sudo apt-get update
sudo apt-get install -y portaudio19-dev libsndfile1 ffmpeg

# 2. Installation des packages Python requis
pip3 install sounddevice kokoro-onnx soundfile

# 3. Installation spécifique de onnxruntime-gpu (via l'index Jetson AI Lab de NVIDIA pour JP6)
pip3 install --extra-index-url https://pypi.jetson-ai-lab.dev onnxruntime-gpu
```

---

## 4. Téléchargement des Modèles Vocaux Kokoro

Pour utiliser Kokoro-ONNX en local sur la Jetson, vous devez télécharger le modèle et le fichier de voix.

```bash
# Créer le répertoire de stockage
mkdir -p ~/.local/share/kokoro
cd ~/.local/share/kokoro

# Télécharger le modèle ONNX (v1.0) et les matrices de voix
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

---

## 5. Procédure de Test et Validation

### 5.1 Test d'acquisition Micro (sounddevice)
Ce script valide que le flux audio du ReSpeaker est lu sans saccades et que le VAD matériel est correctement couplé.
```bash
PYTHONPATH=. python3 dbot_next/scripts/test_mic_streaming.py
```

### 5.2 Test de synthèse vocale (Kokoro GPU + Interruption)
Ce script valide que Kokoro est bien accéléré sur GPU (CUDA) et simule une interruption au milieu d'une longue phrase pour valider l'arrêt net du son.
```bash
PYTHONPATH=. python3 dbot_next/scripts/test_tts_kokoro.py
```

### 5.3 Test de la transcription en continu (ASR)
Ce script affiche à l'écran ce que vous dites en temps réel.
```bash
PYTHONPATH=. python3 dbot_next/scripts/test_stt_streaming.py
```

### 5.4 Test de la boucle globale de conversation
Lancez le script de démarrage officiel pour couper PulseAudio et activer l'automate de production :
```bash
bash dbot_next/scripts/run_bot_next.sh
```

Dites une phrase. Le robot commencera à répondre. Coupez-lui la parole en disant *"Arrête"* ou en parlant simplement : le robot doit cesser de parler immédiatement et se remettre à vous écouter.
