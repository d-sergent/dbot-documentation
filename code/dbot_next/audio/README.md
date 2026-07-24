# 🎙️ dbot_next.audio — Capture Audio Streaming & VAD Logicielle

Ce dossier contient la brique d'acquisition audio streaming et de VAD logicielle de seconde génération pour la Jetson Orin Nano.

---

## 📄 Fichiers & Rôles

| Fichier | Rôle & Description |
| :--- | :--- |
| **[`audio_io_streaming.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/audio/audio_io_streaming.py)** | Capture audio non-bloquante via `parecord` (PulseAudio) ou `arecord` (ALSA Direct). Extrait en temps réel le canal gauche mono 16 kHz, gère la queue d'acquisition thread-safe, réveille l'amplificateur JST et déverrouille le gain ALSA `Capture Switch` / `Capture Volume`. |

---

## ⚙️ Caractéristiques Techniques

- **Capture** : 16 kHz / 16-bit PCM.
- **Canaux** : Extraction du canal gauche mono depuis la capture 2 canaux de la ReSpeaker XVF-3800.
- **Thread-safe** : Boucle de lecture asynchrone alimentant une file `queue.Queue`.
- **Réveil Matériel** : Invoque `pactl` et `amixer` au démarrage pour sortir la source du mode `SUSPENDED` et activer l'amplificateur JST.
