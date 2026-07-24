# 🤖 D-Bot Code Base

Package Python de contrôle et d'intelligence artificielle du robot humanoïde D-Bot.

---

## 🗂️ Structure Globale du Dépôt

```
Code/
├── dbot/              ← Package Python principal `dbot` (vision, motors, audio, behaviors)
│   ├── vision/        ← Perception sémantique YOLO-World v2, OAK-D Pro & Fusion 3D
│   ├── motors/        ← Contrôle des moteurs RobStride RS-05/RS06 & Web UI CAN
│   ├── audio/         ← Acquisition audio sounddevice & VAD ReSpeaker
│   ├── behaviors/     ← Boucles d'asservissement haut-niveau (Active Gaze, Audio Gaze)
│   ├── brain/         ← Communication hybride avec le serveur Mac
│   └── balance/       ← Estimation d'équilibre et IMU torse BMI270
├── dbot_next/         ← Stack Master Streaming Hybride (Mac Companion Server & Audio Streaming)
│   ├── companion_server.py                ← Serveur unique ASR (Groq/Whisper) + LLM (Gemini) + TTS (Qwen3-TTS MLX)
│   └── scripts/start_companion_server.sh  ← Script d'administration (--start, --restart, --stop, --status, --logs)
├── scripts/           ← Scripts d'exécution et de qualification terrain
│   ├── vision/        ← Test Triade Visuelle & Exporteur TensorRT FP16
│   ├── motors/        ← Test dynamique du Cou Pan/Tilt RS-05
│   ├── audio/         ← Test audio & VAD
│   └── system/        ← Diagnostic matériel et bus CAN
└── rag/               ← Moteur RAG documentaire local (LightRAG + FastEmbed)
```

---

## 📄 Index des Documentations README par Sous-Dossier

- 🤖 **[Package Python `dbot`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/README.md)** : Vue d'ensemble de la bibliothèque.
- ⚡ **[Stack Streaming `dbot_next`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/README.md)** : Serveur Compagnon Déporté (ASR Groq/Whisper + Gemini + Qwen3-TTS).
- 👁️ **[Vision & Spatiale 3D](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/vision/README.md)** : `dbot.vision` (YOLO-World v2, OAK-D Pro, SpatialFusion).
- ⚙️ **[Moteurs & CANbus](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/motors/README.md)** : `dbot.motors` (RobStride RS-05, Singleton CAN, Web UI).
- 🎙️ **[Audio & VAD](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/audio/README.md)** : `dbot.audio` (ReSpeaker XVF-3800, sounddevice).
- 🧠 **[Comportements Haut-Niveau](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/behaviors/README.md)** : `dbot.behaviors` (Active Gaze, Audio Gaze Tracking).
- 🛠️ **[Scripts d'Exécution](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/README.md)** : Dossier racine des scripts.
- 👁️ **[Scripts Vision & TensorRT](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/README.md)** : `scripts/vision/` (`test_triad_vision.py`, `export_yolo_tensorrt.py`).
- ⚙️ **[Scripts Moteurs](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/motors/README.md)** : `scripts/motors/` (`test_neck.py`).
- 📚 **[Moteur RAG Documentaire](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/README.md)** : `rag/` (`ask_rag.py`, `index_docs.py`).

---

## ⚡ Installation (Jetson — première fois)

```bash
# Clone sparse (code uniquement, sans la documentation)
git clone --filter=blob:none --sparse \
    https://github.com/d-sergent/dbot-documentation.git \
    ~/dbot
cd ~/dbot
git sparse-checkout set code/

# Installer le package en mode développement
cd ~/dbot/code
pip3 install -e .
```

## 🔄 Mise à jour
```bash
cd ~/dbot && git pull
```

## 🧪 Tests Rapides

```bash
# Test Triade Visuelle & Fusion 3D
python3 code/scripts/vision/test_triad_vision.py

# Diagnostic Moteurs Web UI
python3 -m dbot.motors.web_ui
```
