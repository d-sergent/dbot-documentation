# 🧠 dbot.behaviors — Boucles de Comportement Haut-Niveau

Ce sous-module rassemble les scripts d'asservissement et de comportement réflexe/cognitif haut-niveau du D-Bot.

---

## 📄 Fichiers & Rôles

| Fichier | Rôle & Description |
| :--- | :--- |
| **[`gaze_tracker.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/behaviors/gaze_tracker.py)** | Boucle d'asservissement du cou Pan/Tilt sur les coordonnées visuelles d'un objet ciblé ou sur la direction de la voix utilisateur ($DoA 360°$). |
| **[`active_gaze.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/behaviors/active_gaze.py)** | Comportement "Regard Actif" couplant la détection sémantique Zero-Shot et l'orientation fluide de la tête. |

---

## ⚡ Lancement de l'Active Gaze

```bash
python3 -m dbot.behaviors.active_gaze
```
