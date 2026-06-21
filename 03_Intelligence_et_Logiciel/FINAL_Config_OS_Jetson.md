# Logiciel & Configuration

## 0. Installation de base (JetPack & Accès Distant)
Pour rappel, la configuration initiale complète du cerveau du D-Bot (Jetson Orin Nano Super) est documentée en annexe :
- **[40 — Installation JetPack (BalenaEtcher)](./annexes/jetson/installation/40_Installation_JetPack_6.md)** : Flashage de l'image `JP6.2.1` et premier démarrage.
- **[41 — Accès Distant Headless (NoMachine & SSH)](./annexes/jetson/installation/41_Acces_Distant_NoMachine.md)** : Prise de contrôle du bureau Ubuntu à distance depuis votre Mac.
- **[42 — Configuration Bus CAN InnoMaker + RS-05](./annexes/jetson/liaison_can/42_Configuration_CAN_InnoMaker_RS05.md)** : Câblage, activation SocketCAN et règles udev pour le Bus 1 (Cou).

---

## 1. NVIDIA Jetson (SocketCAN)
La configuration du bus CAN est essentielle pour piloter les moteurs Robstride.

### Prérequis Linux
```bash
sudo apt-get update
sudo apt-get install can-utils
```

### Couche Jetson (Middleware)
Le D-Bot tourne sous **Ubuntu 22.04 (JetPack 6)** avec **ROS 2 Humble**.
- **Micro-ROS Agent** : Gère la passerelle avec la Sony Spresense via `/dev/ttyTHS0` (Pins 8/10).
- **NVIDIA Isaac ROS** : Accélération matérielle pour la vision (OAK-D).

### Couche Spresense (Temps Réel)
La Spresense exécute un firmware Arduino/NuttX avec **Micro-ROS Client**.
- **Topics publiés** :
    - `/imu/balance` : Données IMU torse (BMI270 Add-on) pour le contrôle d'équilibre.
    - `/power/status` : Tension batterie 13S (48V) et température interne.
- **Fonction Watchdog** : Le firmware surveille le heartbeat de la Jetson et coupe le MOSFET de puissance en cas de freeze.

### Maintenance et Sauvegarde Système
Pour éviter de perdre des heures de configuration ROS2 en cas de corruption de carte SD :
- **Clonage de sécurité** : Créez régulièrement un clone de la carte SD sur un SSD externe (ex: Hynix P310) avant chaque mise à jour majeure via la commande :
  ```bash
  # Remplacez /dev/sdX par l'identifiant de votre carte SD
  sudo dd if=/dev/sdX of=backup_dbot_date.img status=progress
  ```

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
3.  **kbot_audio** : Interface avec le **ReSpeaker XVF-3800**. Reçoit la direction du son (DoA) et publie une cible pour la tête (`/head_target`).
4.  **kbot_balance** : Contrôleur d'équilibre. Lit `/imu/balance` (BMI270 torse) + `/joint_states` (encodeurs moteurs) et publie les corrections de couple sur les hanches/chevilles.
5.  **kbot_joint_states** : Publie les positions/vitesses/couples des 27 moteurs via les encodeurs 14-bit RobStride intégrés (`/joint_states`).

### Idées Algorithmiques
*   **Beamforming (Audio)** : Géré matériellement par le **ReSpeaker XVF-3800** pour orienter la tête vers celui qui parle.
*   **Équilibre (IMU Torse)** : Lire l'IMU BMI270 du torse (via Spresense) pour le contrôle d'équilibre bipède. **Ne PAS utiliser l'IMU de l'OAK-D** (tête) pour l'équilibre — elle bouge indépendamment du corps.
*   **Propriöception (Encodeurs)** : Les encodeurs 14-bit doubles de chaque moteur RobStride fournissent la position et la vitesse articulaire en temps réel. L'estimation de couple via le courant moteur peut remplacer des capteurs de force/couple externes.

---

## 3. Outils de Développement
*   **Fusion 360** : CAO Mécano-Soudée.
*   **Docker** : Recommandé sur la Jetson pour isoler l'environnement ROS2 Humble/Jazzy.

---
*Dernière mise à jour : Mars 2026*
