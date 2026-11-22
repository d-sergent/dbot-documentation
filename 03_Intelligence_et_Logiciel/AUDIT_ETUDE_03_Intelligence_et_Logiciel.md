# 🔍 Rapport d'Audit d'Ingénierie : 03 Intelligence et Logiciel (D-Bot)

> **Date de revue :** 22 novembre 2026  
> **Rôle :** Design Review — Ingénierie Logicielle Embarquée, Architecture Calcul, Simulation RL & IA  
> **Sources auditées (6 fichiers actifs du module 03) :**  
> `FINAL_CONSOLIDE_03_Intelligence_et_Logiciel.md`, `FINAL_Config_OS_Jetson.md`, `STUDY_Comparatif_Orin_Thor.md`, `STUDY_Configuration_IA_Locale.md`, `STUDY_LLM_Conversationnel.md`, `STUDY_Simulation_Isaac_Gym.md`.  
> **Sources Niveau 1 & Arborescence Code vérifiée :**  
> `00_Architecture_Centrale/FINAL_CONSOLIDE_00_Architecture_Centrale.md` (43 DOF = 27 RobStride + 16 Feetech), `02_Electronique_et_Energie/FINAL_CONSOLIDE_02_Electronique_et_Energie.md` (2x Teensy 4.1 Triple CAN FD), `04_Perception_et_Sensors/AUDIT_ETUDE_04_Perception_et_Sensors.md`, `05_Gestion_Projet/FINAL_Liste_Achats_BOM.md`, et contrôle direct des fichiers sous `Code/dbot/` et `Code/scripts/`.

---

## 📑 Sommaire

- [**0. Décision d'Architecture Retenue**](#0-décision-darchitecture-retenue)
- [**1. Vérification des Calculs Clés**](#1-vérification-des-calculs-clés)
  - [1.1 Budget Mémoire, TDP et Performances Jetson](#11-budget-mémoire-tdp-et-performances-jetson)
  - [1.2 Cohérence Cinématique, Matérielle et Arborescence Code](#12-cohérence-cinématique-matérielle-et-arborescence-code)
  - [1.3 Pipeline Vocal, Simulation Sim2Real et Infrastructure RAG Locale](#13-pipeline-vocal-simulation-sim2real-et-infrastructure-rag-locale)
- [**2. Carte des Dépendances Inter-Membres**](#2-carte-des-dépendances-inter-membres)
- [**3. Manques Critiques & Incertitudes**](#3-manques-critiques-incertitudes)
- [**4. Propositions d'Amélioration**](#4-propositions-damélioration)
- [**5. Synthèse du Niveau de Maturité**](#5-synthèse-du-niveau-de-maturité)

---

## 0. Décision d'Architecture Retenue

| Choix de Conception | Spécification Retenue | Justification Technique | Source(s) |
| :--- | :--- | :--- | :--- |
| **Calculateur Embarqué V1** | **NVIDIA Jetson Orin Nano Super 8 Go (`67 TOPS`)**, Ubuntu 22.04 + JetPack 6 (`JP6.2.1`), mode headless | Déjà achetée ; l'arrêt de GDM (`multi-user.target`) récupère `~1,5 Go` de RAM pour les pipelines vision/audio | `FINAL_CONSOLIDE_03`, `FINAL_Config_OS_Jetson.md`, `STUDY_Comparatif_Orin_Thor.md` |
| **Middleware & État Réel Code** | Cible documentée : **ROS 2 Humble + Isaac ROS + Micro-ROS** ; état réel actuel : modules Python autonomes sous `Code/dbot/` | Découplage modulaire (`audio`, `vision`, `brain`, `behaviors`, `motors`, `balance`) en attendant les nœuds ROS 2 / Teensy | `FINAL_Config_OS_Jetson.md`, inspection `Code/dbot/` & `Code/scripts/` |
| **Boucle Conversationnelle Hybride** | **ReSpeaker XVF-3800** (VAD/AEC HW) -> **Faster-Whisper small (CUDA)** -> **Gemini 3.1 Flash Lite** / fallback **Ollama Qwen2.5:0.5b** -> **Piper-TTS** | Déporte le raisonnement lourd vers le Cloud (< 0,5 s LLM) tout en gardant un repli local hors-ligne minimal | `STUDY_LLM_Conversationnel.md`, `FINAL_CONSOLIDE_03` (§1-§2) |
| **Simulation & RL (Sim2Real)** | Entraînement RL à partir d'un URDF/MJCF aligné standards humanoïdes, mains passives (~250-300 g) pour la locomotion, vision active 2 DOF cou | Réutilisation de politiques locomotrices standards et compensation de l'absence de `Waist Pitch` par le `Head Pan/Tilt` | `STUDY_Simulation_Isaac_Gym.md` (§1-§4) |
| **IA Locale d'Atelier (Hors Robot)** | **MacBook Pro M1 Max (`64 Go`)** avec **LightRAG (`dbot-rag`)**, **Ollama MLX** (`qwen3.8:27b-mlx`, `gemma4:26b`, `qwen3.5:9b`) et **Unsloth Studio** | Remplace l'ancien socle `LM Studio / DeepSeek-R1 / Khoj / Qdrant` ; zéro coût API pour l'indexation et la revue CAO/FEA | `STUDY_Configuration_IA_Locale.md` (§1-§3) |
| **Exploitation & Sauvegarde** | Scripts `start_autonomous.sh` / `start_nomachine.sh`, clonage système sur SSD externe **Hynix P310** via `dd` | Permet de basculer entre dev graphique et production headless et de sécuriser l'environnement JetPack 6 | `FINAL_Config_OS_Jetson.md` (§1), `STUDY_LLM_Conversationnel.md` (§4) |

---

## 1. Vérification des Calculs Clés

### 1.1 Budget Mémoire, TDP et Performances Jetson

1. **Dépassement du budget RAM/VRAM unifiée sur Jetson Orin Nano Super (`8 Go`) — Risque OOM**
   * **Sources :** `FINAL_CONSOLIDE_03` (§1-§2), `STUDY_LLM_Conversationnel.md` (§1-§2), recoupé avec `AUDIT_ETUDE_04_Perception_et_Sensors.md` (§1.14).
   * **Recalcul de la mémoire disponible vs allouée (mémoire unifiée CPU + GPU de `8,0 Go`, soit `~7,4 à 7,6 Go` exploitables) :**
     * Gain headless (arrêt GDM) : `~1,5 Go` libérés, laissant `~0,8 Go` pour Ubuntu 22.04 headless minimal.
     * Empilement simultané déclaré dans `03/` + `04/` :
       * OS Ubuntu 22.04 headless : `~0,8 Go`
       * Docker + ROS 2 Humble + Isaac ROS (`FINAL_CONSOLIDE_03` §2) : `~2,0 Go`
       * Faster-Whisper `small` CUDA (`FINAL_CONSOLIDE_03` §2) : `~2,0 Go`
       * Piper-TTS (`FINAL_CONSOLIDE_03` §2) : `1,0 Go` déclaré (`~0,2-0,3 Go` en pratique avec ONNX)
       * Fallback local Ollama `Qwen2.5-0.5B` (`FINAL_CONSOLIDE_03` §2) : `< 2,0 Go` (typiquement `~1,0-1,5 Go` avec contexte + runner Ollama)
       * Vision OAK-D + RTAB-Map / YOLO-World (`Code/dbot/vision/`) : `~1,5-2,0 Go`
     * **Total simultané :** `0,8 + 2,0 + 2,0 + 1,0 + 1,2 + 1,5 = 8,5 Go` (fourchette réelle **`7,8 à 9,5 Go`**, même avec Piper à `0,3 Go`).
   * **Hypothèse implicite :** La documentation additionne chaque brique isolément sans jamais sommer le pied mémoire simultané sur l'unique pool de `8 Go` partagé CPU/GPU.
   * **Statut & Criticité :** 🔴 **BLOQUANT** — Risque critique de terminaison par l'`OOM Killer` Linux en mission autonome (particulièrement lors d'une coupure Wi-Fi déclenchant Ollama). Nécessite de quantifier Whisper en `int8` (`~0,6-0,8 Go`), imposer `OLLAMA_KEEP_ALIVE=0` et éviter la couche Docker (`~1-2 Go`) si non indispensable.

2. **Enveloppe thermique et consommation TDP (`10-15 W` déclaré vs `25 W` en Super Mode `67 TOPS`)**
   * **Sources :** `FINAL_CONSOLIDE_03` (§1-§2), `STUDY_Comparatif_Orin_Thor.md` (§2).
   * **Vérification :** `FINAL_CONSOLIDE_03` combine la puissance `67 TOPS` avec une consommation de `10-15 W`. Or, sur la Jetson Orin Nano Super (JetPack 6.2), le profil **`67 TOPS` (`MAXN Super`)** correspond à un TDP de **`25 W`** (le profil `15 W` limite l'enveloppe à `~40 TOPS`). Avec la caméra `OAK-D Pro` (`~4,5 W`) et le `ReSpeaker` (`~1,5 W`), la consommation du bloc cerveau atteint **`~31-35 W`** en charge IA (totalement couverte par le buck `19 V / 5 A = 95 W`, soit `~37 %` d'utilisation).
   * **Statut & Criticité :** 🟠 **IMPORTANT** — Ajuster la spécification TDP à `25 W` en mode `67 TOPS` et valider la ventilation/évacuation thermique dans le caisson du torse fermé pour prévenir le *thermal throttling*.

3. **Comparatif Jetson AGX Orin vs AGX Thor (hétérogénéité d'unités FP4 vs INT8)**
   * **Source :** `STUDY_Comparatif_Orin_Thor.md` (§1).
   * **Vérification arithmétique :**
     * Puissance IA : `2070 / 275 = 7,527x` (`~7,5x` arithmétiquement cohérent), **MAIS** compare `275 TOPS` en **INT8** (AGX Orin) à `2070 TFLOPS` en **FP4 sparse** (AGX Thor). À précision comparable (`INT8/FP8`), le gain réel est d'environ `3,5x à 4x`, pas `7,5x`.
     * Bande passante mémoire : `(273 - 204) / 204 = +33,82 %` (`+34 %` ✅ validé).
     * Consommation pointe : `(130 - 60) / 60 = +116,67 %` (`+116 %` ✅ validé). À `130 W` en V2, un buck `19 V 95 W` serait surchargé de `+36,8 %`.
   * **Statut & Criticité :** 🟢 **SUGGESTION** — Préciser l'unité (`FP4 vs INT8`) et noter la refonte d'alimentation nécessaire en cas de passage futur à Thor.

---

### 1.2 Cohérence Cinématique, Matérielle et Arborescence Code

4. **Désynchronisation cinématique critique (`40 DOF` sans Waist Yaw vs `43 DOF` acquis à 100 %)**
   * **Sources :** `STUDY_Simulation_Isaac_Gym.md` (§1-§4 & Bilan), `FINAL_CONSOLIDE_03` (§4, §7), vs `FINAL_CONSOLIDE_00_Architecture_Centrale.md` (§1-§2.1) et `FINAL_Liste_Achats_BOM.md` (§2).
   * **Comparaison ligne à ligne des actionneurs et DOF :**
     * Modèle documenté en `03/` : `12 jambes + 0 torse (Waist Yaw absent, reporté en V2/V4) + 10 bras (2x5 DOF : RS-03 épaule pitch, RS-02 coude, sans supination avant-bras) + 16 mains (Dynamixel XC330) + 2 cou (RS-05) = 40 DOF` (`24 DOF` locomotion).
     * Réalité matérielle acquise (`100 %` en atelier) : `12 jambes + 1 torse (Waist Yaw RS-06 monté) + 12 bras (2x6 DOF : RS-04 épaule pitch, RS-03 épaule roll, RS-02 épaule yaw, RS-03 coude pitch, RS-10P supination Option B, RS-00 poignet pitch) + 16 mains (Feetech 10x STS3250 + 6x HL-3915) + 2 cou (RS-05) = 43 DOF` (**`27` RobStride + `16` Feetech**).
   * **Vérification :** Il y a **`9` désaccords actionneurs/DOF majeurs** (Waist Yaw `RS-06` déjà présent, `RS-04` au lieu de `RS-03` à l'épaule pitch, `RS-03` au lieu de `RS-02` au coude pitch, `2x RS-10P` supination absents du 03, `Feetech` au lieu de `Dynamixel XC330`, et mention fantaisiste en V4 d'un *"Poignet Pitch RS-04"* de 1,42 kg / 120 Nm ou d'un *"RS-07"* inexistant).
   * **Statut & Criticité :** 🔴 **BLOQUANT** — Toute modélisation URDF/MJCF et toute politique RL entraînée selon `STUDY_Simulation_Isaac_Gym.md` échouerait au transfert Sim2Real sur le robot réel.

5. **Spécifications matérielles/OS erronées et 7 livrables logiciels fantômes dans `FINAL_CONSOLIDE_03`**
   * **Sources :** `FINAL_CONSOLIDE_03` (§2, §3, §4, §7), vérifié sur le système de fichiers réel (`Code/dbot/`, `Code/scripts/`).
   * **Erreurs factuelles détectées :**
     * `1 TB eMMC` sur `Jetson Orin Nano Super` (§2) : la Jetson Orin Nano ne dispose pas d'eMMC 1 To (elle démarre sur **microSD** ou **NVMe M.2**, d'ailleurs la section §1/§5 indique correctement une carte SD).
     * `Kernel 5.10` avec `JetPack 6` (§2, §6) : **JetPack 6 (`L4T R36.x`) repose sur le noyau Linux `5.15`** (c'est JetPack 5 qui utilisait le 5.10).
     * Références BOM altérées : `INNOMAKER-RS05-USB-CAN` (confusion entre `InnoMaker USB2CAN-C` et moteur `RS-05`), `RESPONSER-XVF-3800` (coquille pour `ReSpeaker XVF-3800`), `LiDAR L2 (Ouster)` (c'est un **Unitree L2**), `Waist Pitch RS-07` (`RS-07` inexistant dans la gamme RobStride).
   * **Contrôle réel d'existence des fichiers marqués `✔︎` dans `FINAL_CONSOLIDE_03` (§4) :**
     * **7 / 7 chemins d'architecture/CI déclarés `✔︎` sont INEXISTANTS sur disque :** `Code/dbot/description/robot.urdf.xacro`, `sim/isaac_gym/robot_gym.py`, `launch/robot_launch.py`, `launch/vision_launch.py`, `docker/Dockerfile`, `tests/test_can_interface.py`, `tests/test_micro_ros.py`.
     * **Fichiers réellement présents :** une base Python opérationnelle sous `Code/dbot/` (`brain/llm_client.py`, `audio/audio_io_v2.py`, `audio/stt.py`, `audio/tts.py`, `audio/respeaker_sdk.py`, `vision/oak_camera.py`, `vision/yolo_world.py`, `vision/spatial_fusion.py`, `vision/depth_reflex.py`, `motors/can_bus.py`, `motors/neck.py`, `motors/arm.py`, `motors/legs.py`, `balance/imu.py`, `balance/stabilizer.py`, `motors/web_ui.py`) et les scripts `Code/scripts/{audio,behaviors,motors}/`.
   * **Statut & Criticité :** 🔴 **BLOQUANT** — Document consolidé non fiable en tant que Niveau 1 tant que les faux états `✔︎` et erreurs matérielles ne sont pas purgés.

6. **Incohérence Bus Moteurs (InnoMaker direct vs 2x Teensy 4.1 CAN-FD) et niveau UART `1,8 V` vs `3,3 V`**
   * **Sources :** `FINAL_CONSOLIDE_03` (§1, §2, §5 étape 3), `FINAL_Config_OS_Jetson.md` (§1), vs `FINAL_CONSOLIDE_02` (§1, §5.1) et `FINAL_Liste_Achats_BOM.md` (§3).
   * **Vérification :**
     * Le dossier 03 décrit uniquement une interface directe `Jetson -> InnoMaker USB-CAN -> SocketCAN can0/can1` sous Linux Ubuntu standard (sans noyau temps réel `PREEMPT_RT`), alors que le dossier 02 et la BOM ont adopté **`2x Teensy 4.1 + Shields SK Pang Triple CAN FD`** (6 bus CAN-FD temps réel reliés en USB 480 Mbps à la Jetson) et déclassé les adaptateurs USB-CAN au rôle de debug.
     * `FINAL_CONSOLIDE_03` (§5 étape 3) indique à tort que l'UART `/dev/ttyTHS0` sur les broches `8/10` du connecteur 40 pins de la Jetson est en **`1,8 V`**. En réalité, le header 40 pins de la Jetson Orin Nano intègre des translateurs de niveau (**`3,3 V`** natif sur le header, compatible avec la Spresense configurée en jumper `3,3 V`), tandis que le mode de liaison Spresense <-> Jetson reste ambigu (UART `/dev/ttyTHS0` Micro-ROS dans `03/` vs USB `/dev/ttyUSBx` via hub dans `02/`).
   * **Statut & Criticité :** 🔴 **BLOQUANT** — Trancher un protocole unique Jetson <-> 2x Teensy 4.1 et aligner la tension/liaison Spresense entre `02/` et `03/`.

---

### 1.3 Pipeline Vocal, Simulation Sim2Real et Infrastructure RAG Locale

7. **Latence conversationnelle bout-en-bout (`~2,1 s` réelle vs `< 1 s` revendiquée)**
   * **Sources :** `STUDY_LLM_Conversationnel.md` (§1, lignes 24-35), `FINAL_CONSOLIDE_03` (§2).
   * **Recalcul :** `VAD Matériel (~0,2-0,3 s fin de parole) + STT Faster-Whisper small CUDA (~1,2 s) + LLM Gemini 3.1 Flash Lite (< 0,5 s) + TTS Piper (< 0,1 s) = ~2,0 à 2,1 s` (hors latence réseau TLS/Wi-Fi). Le chiffre `< 1 s` ne s'applique donc qu'au sous-ensemble `LLM + TTS`, pas au tour de parole complet.
   * **Statut & Criticité :** 🟠 **IMPORTANT** — Réviser la cible documentée ou activer le streaming LLM + quantisation STT `int8` + mouvement d'attention `audio_gaze.py` dès le DoA (`< 100 ms`).

8. **Obsolescence d'Isaac Gym et adéquation poste de développement (`Mac M1 Max 64 Go`)**
   * **Sources :** `STUDY_Simulation_Isaac_Gym.md` (§1-§4), `STUDY_Configuration_IA_Locale.md` (§2).
   * **Vérification :** NVIDIA a arrêté le développement d'**Isaac Gym** au profit d'**Isaac Lab** (basé sur Isaac Sim). De plus, Isaac Gym et Isaac Sim exigent un GPU NVIDIA RTX sous Linux/Windows, alors que la machine principale d'ingénierie du projet (`STUDY_Configuration_IA_Locale.md`) est un **MacBook Pro M1 Max (`64 Go`)** (architecture Apple Silicon ARM64/MLX sans CUDA).
   * **Statut & Criticité :** 🟠 **IMPORTANT** — Adopter **MuJoCo / MJX (JAX/Metal/CPU)** comme simulateur de référence local exécutable directement sur M1 Max (et facilement exportable vers **Isaac Lab** si un poste/cloud RTX est utilisé pour l'entraînement massif).

9. **Désynchronisation de `STUDY_Configuration_IA_Locale.md` sur la stack RAG active**
   * **Sources :** `STUDY_Configuration_IA_Locale.md` (§1), vs `Code/rag/rag_runtime.py` (lignes 38-57) et `.kilo/kilo.jsonc`.
   * **Écarts constatés :** Le document pointe encore l'index actif vers `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db` (devenu le miroir de sauvegarde depuis l'offload SSD `/Users/Shared/dbot_rag_local/lightrag_dbot_db`) et mentionne `BAAI/bge-reranker-v2-m3` alors que `rag_runtime.py` utilise `intfloat/multilingual-e5-large` + `BAAI/bge-reranker-base`.
   * **Statut & Criticité :** 🟡 **À SURVEILLER** — Mettre à jour `STUDY_Configuration_IA_Locale.md` pour refléter la configuration RAG exacte en production.

10. **Liens morts et hygiène de maintenance OS Jetson (`FINAL_Config_OS_Jetson.md`)**
    * **Source :** `FINAL_Config_OS_Jetson.md` (§0, §1).
    * **Écarts constatés :** Les 3 liens d'installation (`./annexes/jetson/installation/...`) pointent dans `03_Intelligence_et_Logiciel/annexes/` (inexistant) au lieu de `../Annexes/jetson/...` ; la commande `dd` de sauvegarde SD n'indique pas le démontage préalable ni `bs=4M conv=fsync`, et l'exigence vitale JetPack 6 (`pip install <pkg> --no-deps` pour préserver PyTorch GPU CUDA natif) n'y figure pas.
    * **Statut & Criticité :** 🟡 **À SURVEILLER** — Corriger les 3 chemins relatifs et ajouter la procédure de protection PyTorch CUDA + sauvegarde SD démontée sur Mac.

---

## 2. Carte des Dépendances Inter-Membres

* **[Budget RAM/VRAM unifiée Jetson `8 Go` & TDP `25 W` Super Mode]** -> **[04 Perception & 02 Énergie]** -> Impose le partage strict de la mémoire entre `RTAB-Map / OAK-D / YOLO-World` (`40-60 %` GPU) et la boucle vocale CUDA, tout en dimensionnant le refroidissement du torse et le rail `19 V` (`~31-35 W` système avec USB).
* **[Cervelet `2x Teensy 4.1 + SK Pang Triple CAN FD` (6 bus)]** -> **[03 Logiciel Moteur]** -> Remplace les nœuds `kbot_motor_control` / `SocketCAN` directs sur Jetson par une séparation à deux niveaux : boucle PID/MIT/Damping à `500 Hz - 1 kHz` sur les Teensy, consignes/télémétrie haut niveau à `50-100 Hz` sur Jetson.
* **[Cinématique réelle `43 DOF` (`27` RobStride dont `Waist Yaw RS-06` + `RS-10P` + `16` Feetech)]** -> **[03 Simulation & Contrôle]** -> Oblige à reconstruire l'URDF/MJCF de simulation avec le `Waist Yaw RS-06` actif, les bonnes masses/couples (`RS-04` épaule, `RS-03` coude, `RS-10P` supination) et l'inertie réelle du torse (`18,80 kg` bloc supérieur, `Z_cog = 1290 mm`).
* **[Watchdog Spresense (`BMI270` 416 Hz, ligne `D2 -> Teensy Pin 2 < 1 ms`)]** -> **[02 Sécurité & 03 Contrôle d'Équilibre]** -> Délègue la mise en amortissement réflexe d'urgence au matériel (Teensy + Spresense) pour contourner la gigue non temps réel d'Ubuntu 22.04 sur Jetson.
* **[Latence vocale bout-en-bout (`~2,1 s`) + DoA `ReSpeaker XVF-3800`]** -> **[01 Cou (`2x RS-05`)]** -> Le suivi directionnel `audio_gaze.py` / `look_at_speaker_v1.py` fournit un retour comportemental immédiat (`< 100 ms`) pendant le traitement STT/LLM.
* **[Architecture mains `ESP32-S3 + Waveshare 25514` (`16x Feetech` + `eFlesh MLX90393`)]** -> **[01 Bras/Mains & 03 Manipulation]** -> Remplace l'ancien pont `U2D2 / Dynamixel` par des paquets série `ESP32-S3` centralisant commande doigts et retour tactile 3 axes pour les futures politiques RL de préhension.
* **[Mode headless (`systemctl isolate multi-user.target`)]** -> **[04 Audio & Vision]** -> Libère le verrou PulseAudio/GDM bloquant le ReSpeaker XVF-3800 tout en récupérant `~1,5 Go` de RAM sur les `8 Go`.
* **[Évolution V2 `Jetson AGX Orin (60 W)` / `Thor (130 W)`]** -> **[02 Énergie & 01 Torse]** -> Exige une mise à niveau du convertisseur `19 V` (actuellement `95 W` max), du volume/dissipation thermique du torse et de la capacité batterie `13S`.

---

## 3. Manques Critiques & Incertitudes

1. 🔴 **Absence complète des livrables URDF/MJCF, nœuds ROS 2, Dockerfile et tests automatisés déclarés `✔︎`**
   * *Source :* `FINAL_CONSOLIDE_03` (§4), vérifié par inspection directe du dépôt.
   * *Risque :* Aucune simulation dynamique, aucun lancement ROS 2 unifié et aucune suite de tests CI moteur/Spresense n'existent réellement à ce jour.
   * *Action :* Mettre à jour `FINAL_CONSOLIDE_03` sur le code Python réellement existant (`Code/dbot/`) et créer un vrai `robot.xml` (MuJoCo) / `robot.urdf` dérivé de la CAO et d'`AUDIT_METROLOGIQUE_Torse_et_Bassin.json`.

2. 🔴 **Aucun arbitrage d'ordonnancement RAM/VRAM sur les `8 Go` de la Jetson**
   * *Source :* `FINAL_CONSOLIDE_03` (§2), `STUDY_LLM_Conversationnel.md` (§1-§2).
   * *Risque :* Plantage OOM dès activation conjointe de la vision (`OAK-D` + `YOLO-World`), du STT CUDA (`2 Go`), de Docker (`2 Go`) et du fallback Ollama (`1-2 Go`).
   * *Action :* Réaliser un benchmark mesuré sur Jetson réelle (`tegrastats` + `free -m`) combinant vision, Faster-Whisper `int8`, Piper-TTS et politique de contrôle, puis documenter l'allocation maximale par processus.

3. 🔴 **Protocole de communication `Jetson <-> 2x Teensy 4.1` non spécifié**
   * *Source :* `FINAL_CONSOLIDE_02` (§1-§2) vs `FINAL_CONSOLIDE_03` (§2).
   * *Risque :* Les 27 actionneurs RobStride restent impossibles à piloter en boucle coordonnée tant que le firmware Teensy (USB CDC / Ethernet UDP), le format binaire des consignes/retours et les délais de watchdog ne sont pas définis.
   * *Action :* Rédiger la spécification d'interface (trame binaire compacte avec CRC-16, fréquence cible `50-200 Hz` Jetson -> Teensy et `500 Hz - 1 kHz` Teensy -> CAN-FD) et implémenter le pont associé dans `Code/dbot/motors/`.

4. 🟠 **Absence de noyau temps réel (`PREEMPT_RT`) et gigue potentielle de la boucle d'équilibre**
   * *Source :* `FINAL_CONSOLIDE_03` (§2) et `FINAL_Config_OS_Jetson.md` (§1).
   * *Risque :* Sous Ubuntu 22.04 standard, un pic CPU/GPU vision ou un GC Python bloque la boucle au-delà de quelques millisecondes, déstabilisant le contrôleur d'équilibre (`kbot_balance`).
   * *Action :* Maintenir impérativement les boucles rapides (`Damping` réflexe, interpolation et contrôle impédance MIT `>= 500 Hz`) sur les **2x Teensy 4.1** et valider sous stress CPU/GPU sur Jetson que la boucle politique RL tient `50-100 Hz` sans décrochage (`jitter < 2 ms`).

5. 🟠 **Ambiguïté sur le lien physique `Spresense <-> Jetson` (USB vs UART `/dev/ttyTHS0`)**
   * *Source :* `FINAL_CONSOLIDE_03` (§2, §5 étape 3) vs `FINAL_CONSOLIDE_02` (§2, §5.2).
   * *Risque :* Erreur de câblage ou conflit de périphérique (`/dev/ttyTHS0` vs `/dev/ttyUSBx`), et latence heartbeat non mesurée.
   * *Action :* Trancher un canal unique (recommandé : **USB série** pour l'auto-alimentation test et le monitoring + ligne matérielle dédiée `Pin D12` pour le heartbeat PWM/toggle) et vérifier au multimètre le niveau `3,3 V` avant raccordement.

6. 🟠 **Profil thermique de la Jetson Orin Nano Super à `25 W` dans le torse fermé non testé**
   * *Source :* `FINAL_CONSOLIDE_03` (§6 n°3).
   * *Risque :* Brider automatiquement les fréquences GPU/CPU (*thermal throttling*) en milieu clos PA12-CF après quelques minutes d'inférence vision + audio.
   * *Action :* Mesurer les températures CPU/GPU (`tegrastats`) pendant 20 min en charge continue dans l'enveloppe fermée du torse et définir les ouïes/flux d'extraction dans le carénage.

7. 🟡 **Fiabilité non testée du `Function Calling` hors-ligne sur `Qwen2.5-0.5B`**
   * *Source :* `STUDY_LLM_Conversationnel.md` (§1, §3), `FINAL_CONSOLIDE_03` (§6 n°9).
   * *Risque :* Un modèle de `0,5 B` paramètres produit fréquemment des appels d'outils malformés ou hallucinés en repli hors-ligne.
   * *Action :* Écrire un jeu de test automatisé de bascule réseau coupée (`Code/dbot/brain/llm_client.py`) avec routeur d'intentions déterministe en secours du LLM `0,5 B`.

8. 🟡 **Absence de procédure reproductible de provisionnement Jetson & protection JetPack 6 (`--no-deps`)**
   * *Source :* `FINAL_Config_OS_Jetson.md` (§1) vs règle projet `.agents/AGENTS.md`.
   * *Risque :* Une simple commande `pip install` sans `--no-deps` écrase le PyTorch compilé CUDA 12.2/12.6 par une wheel CPU générique, rendant l'accélération GPU (`Faster-Whisper`, `YOLO-World`) inutilisable.
   * *Action :* Documenter systématiquement `--no-deps` dans `FINAL_Config_OS_Jetson.md` et scriptifier l'installation complète.

---

## 4. Propositions d'Amélioration

| Priorité (Ratio Bénéfice / Complexité) | Proposition Chiffrée & Action Concrète | Impact Technique & Gains Attendus |
| :--- | :--- | :--- |
| **1. Très Haut / Faible** | **Refondre `FINAL_CONSOLIDE_03_Intelligence_et_Logiciel.md` sur la vérité terrain** : corriger `1 TB eMMC -> microSD/NVMe`, `Kernel 5.10 -> 5.15`, `25 W Super Mode`, `43 DOF (27 RobStride dont Waist RS-06 + RS-10P + 16 Feetech)`, retirer les 7 fichiers `✔︎` inexistants au profit des modules réels `Code/dbot/`, et séparer la stack embarquée Jetson de la stack atelier Mac (`STUDY_Configuration_IA_Locale.md`). | Restaure 100 % de fiabilité Niveau 1 et élimine les hallucinations documentaires dans les requêtes LightRAG. |
| **2. Très Haut / Faible** | **Optimiser le budget RAM Jetson pour rester `< 5,5 Go / 8 Go`** : exécuter Faster-Whisper `small` en **`int8`** (`~0,6-0,8 Go` VRAM au lieu de `2,0 Go`), fixer `OLLAMA_KEEP_ALIVE=0` pour décharger `Qwen2.5:0.5b` dès le retour du cloud, et exécuter la stack en natif headless (économie de `~1,5-2,0 Go` vs Docker en V1). | Dégage `~2,5 à 3,0 Go` de marge de sécurité permanente sur les `8 Go` unifiés et supprime le risque de crash OOM en marche. |
| **3. Très Haut / Moyenne** | **Migrer la simulation vers `MuJoCo / MJX` (et `Isaac Lab`) avec un modèle unique `43 DOF`** : abandonner Isaac Gym (déprécié) au profit de MuJoCo (exécutable directement sur le Mac M1 Max `64 Go` sans GPU NVIDIA) à partir d'un fichier `robot.xml` généré sur les cotes réelles `Torse-123 v42` et `AUDIT_METROLOGIQUE_Torse_et_Bassin.json`. | Permet le prototypage et la vérification de politiques RL directement en local sur Mac avec le vrai `Waist Yaw RS-06` et les vraies inerties. |
| **4. Très Haut / Moyenne** | **Spécifier et coder la passerelle temps réel `Jetson <-> 2x Teensy 4.1`** : trame USB CDC binaire (`COBS` + `CRC-16`) transportant 27 consignes/états moteurs à `100-200 Hz`, pendant que chaque Teensy boucle localement sur `3` bus CAN-FD à `500 Hz - 1 kHz` avec bascule autonome Damping sur perte heartbeat. | Résout le blocage temps réel de Linux et aligne intégralement `Code/dbot/motors/` sur l'architecture électronique validée du module 02. |
| **5. Haut / Faible** | **Réduire la latence conversationnelle perçue de `~2,1 s` à `< 1,2 s`** : déclencher immédiatement l'orientation du cou (`audio_gaze.py` via DoA ReSpeaker `< 100 ms`), activer le décodage Whisper `int8` + `beam_size=1` (`~0,5-0,7 s`) et streamer la réponse Gemini phrase par phrase vers `Piper-TTS`. | Divise par ~2 le temps mort ressenti en interaction tout en diminuant la charge VRAM. |
| **6. Haut / Faible** | **Corriger les liens et sécurités d'exploitation dans `FINAL_Config_OS_Jetson.md`** : réparer les chemins `../Annexes/jetson/installation/...`, imposer `pip install --no-deps` pour protéger PyTorch CUDA JetPack 6, et documenter le clonage `dd bs=4M conv=fsync` sur carte SD démontée. | Protège l'environnement GPU contre toute casse lors de mises à jour et supprime les liens brisés dans le corpus RAG. |

---

## 5. Synthèse du Niveau de Maturité

**★★☆☆☆ — Socle applicatif Python prometteur sur Jetson, mais documentation consolidée 03 obsolète et architecture logicielle encore déconnectée de la mécanique 43 DOF et des 2x Teensy 4.1.**

Les briques individuelles audio, vision et LLM hybride existent concrètement dans `Code/dbot/` (`audio_io_v2.py`, `stt.py`, `llm_client.py`, `oak_camera.py`, `yolo_world.py`, `depth_reflex.py`) et la séparation entre cloud rapide et repli local est judicieuse. Toutefois, **quatre ruptures critiques** bloquent l'intégration système : dépassement certain de la mémoire unifiée `8 Go` en charge simultanée (`7,8-9,5 Go`), divergence cinématique majeure (`40 DOF` sans Waist vs `43 DOF` acquis), présence de 7 fichiers logiciels/URDF fictifs marqués `✔︎` ainsi que d'erreurs matérielles/OS (`1 TB eMMC`, `Kernel 5.10`, `RS-07`, `1,8 V UART`), et absence de passerelle définie vers les `2x Teensy 4.1 Triple CAN FD`. Une remise à niveau ciblée de `FINAL_CONSOLIDE_03`, un profilage RAM/thermique mesuré et un vrai modèle `MuJoCo 43 DOF` permettront d'atteindre rapidement `★★★★☆`.
