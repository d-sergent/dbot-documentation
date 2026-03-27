# Logiciel & Configuration

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
    - `/audio/direction` : Angle DoA calculé par beamforming.
    - `/imu/balance` : Données IMU torse (BMI270 Add-on) pour le contrôle d'équilibre.
    - `/power/status` : Tension batterie 13S (48V) et température interne.
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
4.  **kbot_balance** : Contrôleur d'équilibre. Lit `/imu/balance` (BMI270 torse) + `/joint_states` (encodeurs moteurs) et publie les corrections de couple sur les hanches/chevilles.
5.  **kbot_joint_states** : Publie les positions/vitesses/couples des 24 moteurs via les encodeurs 14-bit RobStride intégrés (`/joint_states`).

### Idées Algorithmiques
*   **Beamforming (Audio)** : Utiliser les micros de la Spresense pour orienter la tête vers celui qui parle.
*   **Équilibre (IMU Torse)** : Lire l'IMU BMI270 du torse (via Spresense) pour le contrôle d'équilibre bipède. **Ne PAS utiliser l'IMU de l'OAK-D** (tête) pour l'équilibre — elle bouge indépendamment du corps.
*   **Propriöception (Encodeurs)** : Les encodeurs 14-bit doubles de chaque moteur RobStride fournissent la position et la vitesse articulaire en temps réel. L'estimation de couple via le courant moteur peut remplacer des capteurs de force/couple externes.

---

## 3. Outils de Développement
*   **Fusion 360** : CAO Mécano-Soudée.
*   **Docker** : Recommandé sur la Jetson pour isoler l'environnement ROS2 Humble/Jazzy.

---

## 4. Audit de Sécurité & Agent IA (OpenClaw)

L'agent IA et le système global doivent être audités régulièrement pour garantir qu'aucune vulnérabilité (permissions de fichiers, accès aux outils, limites de l'agent) n'est apparue au cours du développement.

### Configuration & Diagnostic
Avant de lancer le service, assurez-vous que la configuration est valide :
- **Configuration initiale** : `openclaw configure` (permet de lier Ollama, les modèles et les canaux).
- **Diagnostic** : `openclaw doctor --fix` (détecte et répare automatiquement les erreurs de config).

### Démarrage du Service Gateway
Pour lancer le service de communication de l'agent :
```bash
openclaw gateway
```

### Procédure de maintenance hebdomadaire
1.  **Audit Approfondi** : Analyse toute la trajectoire de sécurité et l'espace d'action.
    ```bash
    openclaw security audit --deep
    ```
2.  **Correction Automatique** : Applique les correctifs suggérés (fermeture de canaux, révision des permissions).
    ```bash
    openclaw security audit --fix
    ```

> [!IMPORTANT]
> Ne jamais sauter la phase d'audit après l'ajout d'un nouvel outil (outil de manipulation de fichiers, accès réseau ou nouveau driver moteur) pour s'assurer que l'agent IA reste dans son périmètre de sécurité.

---

## 5. Ollama (LLM Local)

**Ollama** permet d'exécuter des modèles de langage (LLM) en local sur le poste de développement (Mac Apple Silicon).

### Installation d'un modèle
Les modèles ne sont pas inclus par défaut. Vous devez les télécharger avant de les utiliser dans OpenClaw :
```bash
ollama pull mistral:7b
```

### Démarrage en Service (Arrière-plan)
Pour lancer Ollama au démarrage et le maintenir actif en arrière-plan :
```bash
brew services start ollama
```

### Démarrage Manuel (Optimisé)
Si vous préférez un lancement ponctuel sans service, utilisez les variables d'environnement d'optimisation :
```bash
OLLAMA_FLASH_ATTENTION="1" OLLAMA_KV_CACHE_TYPE="q8_0" /opt/homebrew/opt/ollama/bin/ollama serve
```

| Variable | Effet |
| :--- | :--- |
| `OLLAMA_FLASH_ATTENTION=1` | Active **Flash Attention** — réduit la consommation mémoire et accélère l'inférence. |
| `OLLAMA_KV_CACHE_TYPE=q8_0` | Quantifie le **KV Cache en Q8_0** — réduit l'empreinte VRAM tout en conservant une bonne qualité. |

> [!TIP]
> Sur Apple Silicon (M1/M2/M3/M4), ces optimisations permettent de charger des modèles plus grands (ex: 70B Q4) dans la mémoire unifiée GPU/CPU.
