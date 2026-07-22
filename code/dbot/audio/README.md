# 🎙️ dbot.audio — Package Audio, Capture Streaming & VAD Matériel

Ce sous-module assure l'acquisition audio non-bloquante, la détection vocale matérielle (VAD) et la localisation angulaire 360° (DoA) via la carte Seeed ReSpeaker XVF-3800.

---

## 📄 Fichiers & Rôles

| Fichier | Rôle & Description |
| :--- | :--- |
| **[`audio_io_v2.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/audio/audio_io_v2.py)** | Capture audio non-bloquante avec file d'attente thread-safe `sounddevice` à 16 kHz. Implémente le mécanisme d'interruption instantanée du son (`Barge-In`) sur détection de parole utilisateur. |
| **[`respeaker_sdk.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/audio/respeaker_sdk.py)** | Interface USB avec la carte XMOS XVF-3800. Extrait en temps réel la Direction d'Arrivée de la voix ($0-360°$) et l'état du VAD sans consommer de GPU. |

---

## ⚡ Utilisation Rapide

```python
from dbot.audio.audio_io_v2 import AudioManager

audio = AudioManager()
audio.start_listening()
chunk = audio.read_chunk()
```
