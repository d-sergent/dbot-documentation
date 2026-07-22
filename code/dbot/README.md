# 🤖 dbot — Package Python Principal du D-Bot

Ce dossier contient le cœur de la bibliothèque Python `dbot` installable sur la Jetson Orin Nano (`pip install -e .`).

---

## 🗂️ Structure des Sous-Modules

```
dbot/
├── config.py         ← Configuration centralisée (limites Pan/Tilt, baudrates, IDs CAN)
├── vision/           ← Module de perception sémantique YOLO-World v2, OAK-D Pro & Fusion 3D
├── motors/           ← Module de contrôle des moteurs RobStride RS-05/RS06 et Web UI CAN
├── audio/            ← Module d'acquisition audio streaming sounddevice & VAD ReSpeaker
├── behaviors/        ← Boucles d'asservissement haut-niveau (Active Gaze, VOR)
├── brain/            ← Client de communication hybride gRPC/HTTP avec le Mac
└── balance/          ← (Phase 4) Estimation d'équilibre et IMU torse BMI270
```

---

## 📄 Documentation Détaillée par Sous-Module

- 👁️ **[Vision & Spatiale 3D](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/vision/README.md)** : `dbot.vision`
- ⚙️ **[Moteurs & CANbus](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/motors/README.md)** : `dbot.motors`
- 🎙️ **[Audio & VAD](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/audio/README.md)** : `dbot.audio`
- 🧠 **[Comportements Haut-Niveau](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/behaviors/README.md)** : `dbot.behaviors`
