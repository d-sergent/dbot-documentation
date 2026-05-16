# 🦾 Spécifications Finales : 03 Intelligence et Logiciel (D‑Bot)

---

## 1. Vue d’Ensemble (Version Actuelle)

Le module **Intelligence & Logiciel** regroupe l’ensemble du « cerveau » du D‑Bot :  
- **Noyau de calcul** : NVIDIA **Jetson Orin Nano Super** (8 Go RAM, 67 TOPS, consommation 10‑15 W).  
- **Système d’exploitation** : Ubuntu 22.04 LTS (JetPack 6, ROS 2 Humble).  
- **Middleware** : ROS 2 Humble + NVIDIA Isaac ROS (accélération vision).  
- **Passerelle temps réel** : **Sony Spresense** (Micro‑ROS client, firmware Arduino/NuttX).  
- **Capteurs principaux** : IMU BMI270 (torse, via Spresense), caméra stéréo **OAK‑D Pro**, microphone **ReSpeaker XVF‑3800**.  
- **Bus de commande moteur** : CAN 1 Mbps (adaptateur **InnoMaker RS‑05**, SocketCAN).  
- **Audio** : VAD matériel sur ReSpeaker, STT Faster‑Whisper (small, CUDA), TTS Piper‑TTS (fr_FR‑siwis‑medium).  
- **LLM** : Architecture hybride — **Google Gemini 3.1 Flash Lite** (cloud) en mode principal, **Ollama + Qwen2.5‑0.5B** (local) en secours.  
- **Gestion de la RAM** : désactivation de GDM (multi‑user.target) libère ~1,5 GiB pour ROS 2/vision.  

> **Dernière mise à jour des sources** : Mars 2026 (config Jetson) – 12 mai 2026 (IA conversationnelle) – 25 mai 2026 (Isaac Gym).  

---

## 2. Spécifications Matérielles Validées

| Élément | Référence / Modèle | Fonction | Interface | Paramètres clés | Validation |
|---|---|---|---|---|---|
| **CPU / GPU** | **NVIDIA Jetson Orin Nano Super** (8 GB, 67 TOPS) | Calcul général, ROS 2, vision | PCIe / USB‑3.0 | Consommation 10‑15 W, 1 TB eMMC | ✔︎ (installé) |
| **OS** | Ubuntu 22.04 + JetPack 6 | Système d’exploitation | — | Kernel 5.10, ROS 2 Humble | ✔︎ |
| **CAN‑Adapter** | **InnoMaker RS‑05** (USB‑CAN) | Bus moteur RobStride | USB → `can0`/`can1` (SocketCAN) | 1 Mbps, ID 1d50:606f | ✔︎ |
| **Micro‑ROS Agent** | ROS 2 Humble | Passerelle Jetson ↔ Spresense | `/dev/ttyTHS0` (Pins 8/10) | Baud 115200, ROS 2 topic bridge | ✔︎ |
| **Spresense** | Sony Spresense (Arduino/NuttX) | Firmware temps réel, IMU, watchdog | UART → Jetson | Publie `/imu/balance`, `/power/status` | ✔︎ |
| **IMU** | **BMI270** (Add‑on Spresense) | Mesure d’accélération/gyroscope du torse | I2C (via Spresense) | 16 bit, ±2000 dps, ±16 g | ✔︎ |
| **Caméra** | **OAK‑D Pro** (Luxonis) | Vision stéréo + profondeur | USB‑3.0 (PCIe) | 1280×800 px, 30 fps, 1 Gbps | ✔︎ |
| **Microphone** | **ReSpeaker XVF‑3800** | Capture audio, DoA, VAD matériel | I2S / USB | 4‑mic array, Beamforming | ✔︎ |
| **STT** | **Faster‑Whisper small** (CUDA) | Transcription voix → texte | GPU CUDA | Latence ≈ 1.2 s, 2 GB VRAM | ✔︎ |
| **TTS** | **Piper‑TTS** (fr_FR‑siwis‑medium.onnx) | Synthèse vocale | CPU | < 100 ms, 1 GB RAM | ✔︎ |
| **LLM – Cloud** | **Google Gemini 3.1 Flash Lite** | Dialogue, reasoning | HTTPS API | Latence < 0.5 s, coût gratuit | ✔︎ |
| **LLM – Local** | **Ollama + Qwen2.5‑0.5B** | Fallback offline | Local socket | 0.5 B params, < 2 GB RAM | ✔︎ |
| **ROS 2 Nodes** | `kbot_vision`, `kbot_motor_control`, `kbot_audio`, `kbot_balance`, `kbot_joint_states` | Gestion fonctionnelle | ROS 2 topics | — | ✔︎ |
| **Docker** | Images ROS 2 Humble + Isaac ROS | Isolation environnement | Docker Engine | GPU‑enabled, 2 GB RAM base | ✔︎ |
| **Backup SD** | Hynix P310 SSD externe (2 TB) | Clone de la carte SD | USB‑3.0 | `dd if=/dev/sdX of=backup_$(date).img` | ✔︎ |

---

## 3. Nomenclature (BOM Locale)

| # | Référence | Désignation | Fournisseur | Prix (USD) | Quantité | Remarques |
|---|---|---|---|---|---|---|
| 1 | **JETSON‑ORIN‑NANO‑SUPER‑8G** | Jetson Orin Nano Super 8 GB | NVIDIA | [À COMPLÉTER] | 1 | Image JetPack 6 (JP6.2.1) |
| 2 | **INNOMAKER‑RS05‑USB‑CAN** | Adaptateur CAN USB 1 Mbps | InnoMaker | [À COMPLÉTER] | 1 | Identifiant USB 1d50:606f |
| 3 | **SPRESENSE‑DEV‑KIT** | Sony Spresense Development Kit | Sony | [À COMPLÉTER] | 1 | Firmware Arduino/NuttX |
| 4 | **BMI270‑ADD‑ON** | IMU 6‑DOF (BMI270) | Bosch | [À COMPLÉTER] | 1 | Connecté à Spresense |
| 5 | **OAK‑D‑PRO** | Caméra stéréo + AI | Luxonis | [À COMPLÉTER] | 1 | USB‑3.0 |
| 6 | **RESPONSER‑XVF‑3800** | Microphone array 4‑mic | Seeed Studio | [À COMPLÉTER] | 1 | Beamforming hardware |
| 7 | **FAST‑WHISPER‑SMALL‑CUDA** | Modèle STT (CUDA) | OpenAI / Faster‑Whisper | Open‑source | 1 | GPU requis |
| 8 | **PIPER‑TTS‑FR‑SIWIS‑MEDIUM** | Synthèse vocale ONNX | Piper‑TTS | Open‑source | 1 | < 100 ms |
| 9 | **GEMINI‑FLASH‑LITE** | LLM Cloud (API) | Google | Gratuit (quota) | — | API‑Key requis |
|10| **OLLAMA‑QWEN‑0.5B** | LLM local fallback | Ollama | Open‑source | 1 | Docker image |
|11| **HYNIX‑P310‑SSD‑2TB** | SSD externe pour backup | Hynix | [À COMPLÉTER] | 1 | USB‑3.0 |
|12| **CABLE‑CAN‑TWISTED‑PAIR‑120Ω** | Câblage CAN (torsadé) | [À COMPLÉTER] | [À COMPLÉTER] | 2 m | Terminaison 120 Ω aux deux extrémités |
|13| **POWER‑SUPPLY‑48V‑10A** | Alimentation principale du robot | [À COMPLÉTER] | [À COMPLÉTER] | 1 | Fournit 48 V à la carte de puissance |
|14| **MOSFET‑POWER‑SWITCH** | Coupure d’alimentation en cas de watchdog | [À COMPLÉTER] | [À COMPLÉTER] | 1 | Commandé par Spresense |
|15| **CAN‑UTILS** (paquet) | Outils Linux `candump`, `cansend` | Ubuntu repo | Gratuit | — | Install via `apt-get` |
|…| | **(Tous les autres câbles, vis, écrous, supports mécaniques)** | Voir dossier `02_Mecanique/BOM` | — | — | Non‑reproductible ici (hors du périmètre logiciel) |

> **Note** : Tous les prix et fournisseurs non explicités dans les sources sont indiqués **[À COMPLÉTER]** conformément à la règle 3.

---

## 4. État de la Conception (CAD & Simulation)

| Élément | Statut | Fichiers associés | Commentaires |
|---|---|---|---|
| **URDF / MJCF** | ✔︎ (version V1.0) | `code/dbot/description/robot.urdf.xacro` | Conformité aux 40 DOFs décrits (12 jambes, 10 bras, 16 doigts, 2 tête). |
| **Simulation Isaac Gym** | ✔︎ (scène de marche + manipulation basique) | `sim/isaac_gym/robot_gym.py` | Utilise le modèle URDF ci‑dessus, sans Waist Yaw. |
| **ROS 2 Launch Files** | ✔︎ (modulaire) | `launch/robot_launch.py`, `launch/vision_launch.py` | Sépare vision, contrôle moteur, audio. |
| **Dockerfile** | ✔︎ (ROS 2 Humble + Isaac ROS) | `docker/Dockerfile` | GPU‑enabled, expose `8080` pour NoMachine. |
| **Tests Unitaires** | ✔︎ (CI GitHub) | `tests/test_can_interface.py`, `tests/test_micro_ros.py` | Passés sur Jetson + Spresense. |
| **Documentation** | ✔︎ (Markdown) | `docs/03_Intelligence_et_Logiciel/…` | Toutes les sources listées ci‑dessus. |

---

## 5. Instructions de Montage Critiques

| Étape | Action | Risques / Points de vigilance |
|---|---|---|
| **1. Installation JetPack** | Flash image `JP6.2.1` via BalenaEtcher (voir annexe 40) | Vérifier checksum de l’image ; ne pas brancher de périphériques USB pendant le premier boot. |
| **2. Configuration CAN** | - `sudo apt-get install can-utils` <br> - `sudo modprobe gs_usb` <br> - `sudo ip link set can0 up type can bitrate 1000000` | S’assurer que le câble CAN est torsadé, terminaisations 120 Ω présentes. En cas de “Bus‑off”, vérifier continuité et GND commun. |
| **3. Couplage Spresense ↔ Jetson** | Connecter UART (`/dev/ttyTHS0`) aux pins 8/10, config 115200 8N1 | Vérifier que le niveau logique est 1.8 V (Jetson) – utiliser un convertisseur si nécessaire. |
| **4. Démarrage ROS 2** | `ros2 launch dbot robot_launch.py` | Le node `kbot_balance` doit être lancé **après** que le topic `/imu/balance` soit actif (vérifier avec `ros2 topic list`). |
| **5. Activation du watchdog Spresense** | Flash firmware (voir `spresense/firmware/`) | Le watchdog coupe le MOSFET en cas de perte de heartbeat ; tester en débranchant le réseau Ethernet. |
| **6. Audio** | Lancer `code/scripts/audio/start_autonomous.sh` (mode headless) ou `start_nomachine.sh` (mode dev) | En mode headless, désactiver GDM (`systemctl isolate multi-user.target`) pour libérer 1.5 GiB RAM. |
| **7. Backup SD** | `sudo dd if=/dev/mmcblk0 of=backup_$(date +%F).img bs=4M status=progress` | Faire avant chaque mise à jour majeure du système. |
| **8. LLM Cloud** | Configurer `code/dbot/brain/llm_client.py` avec la clé API Gemini | Vérifier quota quotidien, fallback sur Ollama si la connexion échoue. |

---

## 6. Backlog Technique & Questions en Suspens

| N° | Question / Incertitude | Priorité | Commentaire |
|---|---|---|---|
| 1 | **Fournisseur / Prix du Jetson Orin Nano Super** (référence exacte du SKU) | Haute | Aucun prix indiqué dans les sources. |
| 2 | **Compatibilité du driver CAN InnoMaker avec le kernel 5.10** (versions récentes) | Moyenne | Fonctionne en test, mais pas de validation long‑terme. |
| 3 | **Gestion de la chaleur du Jetson sous charge IA** (profil thermique) | Moyenne | Pas de dissipateur / ventilateur décrit. |
| 4 | **Synchronisation temps réel entre Spresense watchdog et ROS 2** (latence maximale tolérée) | Haute | Aucun chiffre fourni ; besoin de mesure. |
| 5 | **Capacité du réseau Wi‑Fi du Jetson pour le streaming vidéo OAK‑D** (débit requis) | Basse | Non mesuré, mais recommandé > 20 Mbps. |
| 6 | **Licences des modèles IA (Faster‑Whisper, Piper‑TTS)** – conformité commerciale | Moyenne | Vérifier obligations de redistribution. |
| 7 | **Plan de mise à jour du firmware Spresense** (procédure OTA) | Basse | Aucun mécanisme décrit. |
| 8 | **Gestion des collisions CAN (priorités, arbitration)** – paramétrage du bus | Moyenne | Documenté uniquement dans le code `kbot_motor_control`. |
| 9 | **Stratégie de récupération après perte du cloud LLM** – bascule automatique | Haute | Script `llm_client.py` mentionne fallback, mais pas de test automatisé. |

---

## 7. Roadmap & Itérations Futures (Optionnel)

| Version cible | Nouveaux éléments prévus | Source d’origine |
|---|---|---|
| **V2 (2027)** | - Ajout **Waist Yaw** (actuateur RS‑06) <br> - Poignet Pitch supplémentaire (actuateur RS‑04) <br> - Upgrade GPU : **Jetson AGX Thor** (128 Go, 2070 TFLOPS) | *STUDY_Comparatif_Orin_Thor.md* |
| **V2.1** | - Intégration d’un **LiDAR L2** (Ouster) pour perception 3D <br> - Migration du LLM cloud vers **Gemini 1.5 Pro** (plus de tokens) | *STUDY_Intelligence_Conversationnelle.md* |
| **V3** | - Remplacement du **Faster‑Whisper small** par **Whisper‑large‑v2** (GPU 8 GB) <br> - Déploiement d’un **RAG local** (Qdrant + nomic‑embed‑text) pour documentation interne | *STUDY_Configuration_IA_Locale.md* |
| **V4** | - Ajout d’un **Waist Pitch** (actuateur RS‑07) pour postures de levage <br> - Main **Dexterous** à 12 DOFs (Shadow‑Hand) | *STUDY_Simulation_Isaac_Gym.md* |

*Toutes les itérations futures sont **exclusivement** listées dans cette section, conformément à la règle 4.*