# ⚙️ dbot.motors — Package de Contrôle Moteur RobStride & Bus CAN

Ce sous-module gère le contrôle bas niveau des moteurs brushless RobStride (RS-05, RS-06, RS-00) sur bus CAN 1 Mbps et fournit l'interface de diagnostic Web UI.

---

## 📄 Fichiers & Rôles

| Fichier | Rôle & Description |
| :--- | :--- |
| **[`neck.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/motors/neck.py)** | Contrôleur du cou 2-DOF (Pan ID:1 & Tilt ID:2). Implémente le contrôle angulaire interpolé, la gestion du modulo $2\pi$, les butées logicielles de sécurité et l'arrêt d'urgence E-STOP (< 1 ms). |
| **[`can_bus.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/motors/can_bus.py)** | Singleton Mutex du bus CAN (`can0` 1 Mbps). Protège le bus des collisions d'I/O multithreadées et gère l'envoi/réception des trames RobStride. |
| **[`web_ui.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/motors/web_ui.py)** | Serveur HTTP/JSON Web UI embarqué (`http://ubuntu.local:8080`). Permet le contrôle dynamique par sliders et la télémesure en temps réel (angles, vitesse, Vbus 48V, températures, erreurs CAN). |

---

## ⚡ Lancement du Serveur Web UI de Diagnostic Moteurs

Sur la Jetson Orin Nano :

```bash
python3 -m dbot.motors.web_ui
```

Accès depuis le navigateur du Mac : `http://ubuntu.local:8080`
