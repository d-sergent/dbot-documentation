# Logiciel & Configuration

## 1. NVIDIA Jetson (SocketCAN)
La configuration du bus CAN est essentielle pour piloter les moteurs Robstride.

### Prérequis Linux
```bash
sudo apt-get update
sudo apt-get install can-utils
```

### Couche Jetson (Middleware)
Le D-bot tourne sous **Ubuntu 22.04 (JetPack 6)** avec **ROS 2 Humble**.
- **Micro-ROS Agent** : Gère la passerelle avec la Sony Spresense via `/dev/ttyTHS0` (Pins 8/10).
- **NVIDIA Isaac ROS** : Accélération matérielle pour la vision (OAK-D).

### Couche Spresense (Temps Réel)
La Spresense exécute un firmware Arduino/NuttX avec **Micro-ROS Client**.
- **Topics publiés** :
    - `/audio/direction` : Angle DoA calculé par beamforming.
    - `/imu/data` : Données fusionnées (IMU Tête + SensiEDGE).
    - `/power/status` : Tension batterie 12S et température interne (CommonSense).
- **Fonction Watchdog** : Le firmware surveille le heartbeat de la Jetson et coupe le MOSFET de puissance en cas de freeze.
- **Liaison Audio** : Flux 8 canaux via **UAC 2.0** (USB) pour une qualité Hi-Res (192 kHz).

### Activation de l'Interface CAN
L'adaptateur InnoMaker est reconnu comme `can0` (parfois `can1`).
Le débit standard Robstride est **1 Mbps** (1,000,000 bps).

**Commande d'activation :**
```bash
sudo ip link set can0 up type can bitrate 1000000
```

**Commande de diagnostic (candump) :**
```bash
candump can0
```
*Si vous voyez des lignes défiler (ex: `can0 141 [8] ...`), la communication est établie.*

### Dépannage
*   **Erreur "Bus-off"** : Souvent un problème physique (Fils non torsadés, Terminaison 120 Ohm manquante, GND non relié).
*   **Interface introuvable** : Vérifiez `lsusb` (ID 1d50:606f) et chargez le module si besoin : `sudo modprobe gs_usb`.

---

## 2. Architecture ROS2
L'objectif est d'avoir un système réactif où la vision influence directement les moteurs.

### Noeuds ROS2 Suggérés
1.  **kbot_vision** : Wrapper pour l'OAK-D Pro. Publie les objets détectés (`/detections`) et l'odométrie visuelle (`/odom`).
2.  **kbot_motor_control** : Lit `/cmd_vel` ou `/joint_states` et envoie les trames CAN brutes aux moteurs.
3.  **kbot_audio** : Interface avec la Spresense. Reçoit la direction du son (x,y,z) et publie une cible pour la tête (`/head_target`).

### Idées Algorithmiques
*   **Beamforming (Audio)** : Utiliser les micros de la Spresense pour orienter la tête vers celui qui parle.
*   **Stabilisation (IMU)** : Lire l'IMU de l'OAK-D (Torse/Tête) pour compenser les mouvements (Self-balancing) via les moteurs de hanche.

---

## 3. Outils de Développement
*   **Fusion 360** : CAO Mécano-Soudée.
*   **Docker** : Recommandé sur la Jetson pour isoler l'environnement ROS2 Humble/Jazzy.
