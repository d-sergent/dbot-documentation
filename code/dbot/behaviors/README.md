# 🧠 dbot.behaviors — Boucles de Comportement Haut-Niveau

Ce sous-module rassemble les scripts d'asservissement et de comportement réflexe/cognitif haut-niveau du D-Bot.

---

## 📄 Fichiers & Rôles

| Fichier | Rôle & Description |
| :--- | :--- |
| **[`audio_gaze.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/behaviors/audio_gaze.py)** | Asservissement angulaire du cou Pan/Tilt sur la direction de la voix utilisateur ($DoA 360°$) renvoyée par le ReSpeaker XVF-3800. |
| **[`active_gaze.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/behaviors/active_gaze.py)** | Comportement "Regard Actif" couplant la détection sémantique Zero-Shot et l'orientation fluide de la tête. |
| **[`gaze_tracker.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/behaviors/gaze_tracker.py)** | Boucle de suivi visuel sémantique continu. |

---

## ⚡ Lancement de l'Active Gaze

```bash
python3 -m dbot.behaviors.active_gaze
```
