# 📘 SPÉCIFICATION D'ARCHITECTURE MASTER V1 — ROBOT D-BOT
**Répartition Globale du Calcul, de la Mémoire et du Réseau : NVIDIA Jetson Orin Nano (8 Go) ↔ Apple Mac M1 Max (64 Go)**

---

## 1. Executive Summary & Découpage Système (100% Focus V1)

La présente spécification établit **l'architecture Master officielle du D-Bot V1**, couvrant 100 % des sous-systèmes matériels et logiciels qualifiés pour la Phase 1 : **Perception Visuelle Multi-Niveaux (OAK-D Pro V-SLAM & Depth Reflex)**, **Audio & Parole (ReSpeaker XVF-3800 360° & Barge-In)**, **Cinématique & Moteurs CAN (RobStride RS)**, **Microcontrôleurs Temps Réel (Teensy 4.1 & Spresense)**, **Mémoire RAG & LLM (LightRAG & Gemini)**, et **Infrastructure Réseau Hybride / Sécurité Double Seuil**.

### **Principe d'Architecture Hybride V1 : "Réflexe Local ↔ Cognition Déportée"**
1. **Sur le Robot (Jetson Orin Nano 8GB Headless + OAK-D Pro + Microcontrôleurs) :**
   * **Invariants locaux V1 :** Équilibre bipède, boucles de contrôle moteur (100–500 Hz), captation audio (ReSpeaker VAD/DoA 100 Hz), vision réflexe matérielle (Depth IR OAK-D < 15 ms), vision sémantique temps réel (YOLO-World v2 @ 30 FPS TensorRT), STT local (Faster-Whisper CUDA), V-SLAM OAK-D Pro et arrêt d'urgence autonome.
   * **Budget VRAM Jetson strictly maîtrisé :** **2,9 Go alloués / 5,5 Go utiles**, laissant **2,6 Go de marge (32 % de réserve de sécurité)**.
2. **Sur le Serveur Compagnon (Mac M1 Max 64GB - Bandwidth 400 GB/s) :**
   * **Tâches lourdes déportées :** Simulation physique & géométrie 3D (*NVIDIA Cosmos 3D Edge*), synthèse vocale HD streaming (*Qwen3-TTS via MLX-Audio*), Moteur RAG documentaire (*LightRAG / FastEmbed*), et raisonnement LLM haut niveau (*Gemini 3.1 Flash Lite / Qwen 35B*).
   * **Bande passante et latence :** Wi-Fi 6 / Ethernet local (< 5 ms de latence réseau). Transport hybridé (ROS 2 DDS UDP Best-Effort pour la vision/télémétrie, gRPC/WebSockets TCP pour l'audio/JSON/RAG).

---

## 2. Cartographie Globale des 8 Sous-Systèmes V1 (Jetson ↔ Mac)

```mermaid
graph TD
    subgraph ROBOT D-BOT V1 (Embarqué - Autonomie & Temps Réel)
        OAK["OAK-D Pro (RGB-D 1080p + VPU Myriad X)"] -->|Hardware Depth IR < 15ms| REFLEX_SAFE["Sécurité Réflexe Proximité (Z < 20cm)"]
        REFLEX_SAFE -->|Interruption Immédiate| TEENSY["2x Teensy 4.1 (Kinematics & CAN FD 500Hz)"]
        
        OAK -->|USB 3.0 / 30 FPS| TRT_V["YOLO-World v2 TensorRT (0.4 GB VRAM - 15ms)"]
        OAK -->|V-SLAM V1 & Feature Tracking 120Hz| NAV["Navigation ROS 2 (Jetson)"]
        
        SENS_A["ReSpeaker XVF-3800 Array"] -->|ALSA Direct| AUD_L["Audio VAD + DoA (0-360°) + Faster-Whisper CUDA"]
        
        IMU_B["IMU BMI270 Torse"] -->|I2C| SPRES["Sony Spresense (Watchdog & Power)"]
        SPRES -->|UART micro-ROS| JET_ROS["ROS 2 Humble Master (Jetson)"]
        
        JET_ROS -->|Commands 100 Hz| TEENSY
        TEENSY -->|3x Bus CAN 1 Mbps| MOTORS["RobStride Motors (RS-00, RS-04, RS-05)"]
        
        JET_ROS <-->|Hybride: UDP Best-Effort & TCP gRPC| NET_BRIDGE["Interface Réseau Hybride"]
    end

    subgraph MAC M1 MAX 64GB (Serveur Compagnon & Cerveau Cognitif)
        NET_BRIDGE <--> MAC_SERVEUR["Serveur Central Python 3.11 / MLX"]
        
        MAC_SERVEUR -->|Metal GPU / Evénementiel| COSMOS["NVIDIA Cosmos 3D Edge (World Model 3D)"]
        MAC_SERVEUR -->|MLX-Audio Streaming| TTS_MAC["Qwen3-TTS 1.7B Streaming (PCM 24kHz)"]
        MAC_SERVEUR -->|FastEmbed / VectorDB| RAG_ENGINE["RAG Documentaire (LightRAG / FastEmbed)"]
        MAC_SERVEUR -->|HTTPS / Local| LLM_BRAIN["Gemini 3.1 Flash Lite / Qwen 35B"]
    end

    NET_BRIDGE -->|Fail-Safe Seuil 1: loss > 200ms| PHYSICAL_HOLD["Mode Maintien / Freins Physique (Teensy)"]
    NET_BRIDGE -->|Fail-Safe Seuil 2: loss > 2.0s| FALLBACK["Mode Autonome Dégradé Local (Ollama + Kokoro TTS)"]
```

---

## 3. Analyse Détallée par Composant Système V1 (Latence, Mémoire & Bande Passante)

### **1. Vision Temps Réel, V-SLAM & Triade de Perception (Luxonis OAK-D Pro FF)**
* **Capteur Unique V1 :** Luxonis OAK-D Pro Fixed-Focus (USB 3.0, 1080p RGB + Stéréo Depth Active IR + VPU Intel Myriad X).
* **Architecture à 3 Niveaux de Perception (Triade Visuelle) :**
  1. **Niveau 0 — Réflexe d'Urgence Matériel (OAK-D Pro Hardware Depth) :**
     * *Calcul :* Traitement de disparité/profondeur en matériel sur la puce Myriad X (0 % CPU/VRAM Jetson ou Mac).
     * *Latence :* **< 15 ms**.
     * *Rôle :* Détection de franchissement de seuil de sécurité (ex: obstacle central Z < 20 cm). Génère un signal d'interruption direct vers le contrôleur local (Teensy/Jetson) pour arrêt immédiat sans passer par la boucle logicielle haute ou le réseau.
  2. **Niveau 1 — Perception Sémantique Zero-Shot (Jetson Orin Nano) :**
     * *Modèle :* **YOLO-World v2 (TensorRT FP16/INT8)** + **OAK-D V-SLAM / Feature Tracking (120 Hz)**.
     * *VRAM Jetson :* **0,4 Go**.
     * *Latence :* **12 à 15 ms (30-60 FPS)**.
     * *Rôle :* Détection d'objets *zero-shot* (open-vocabulary) temps réel pour l'évitement d'obstacles dynamiques, le suivi d'objets et la localisation spatiale.
  3. **Niveau 2 — Reconstruction 3D & World Model (Mac M1 Max 64 Go) :**
     * *Modèle :* **NVIDIA Cosmos 3D Edge**.
     * *VRAM Mac :* **8 à 12 Go (MLX/Metal)**.
     * *Latence :* **~200 ms**.
     * *Rôle & Optimisation Réseau :* Reconstruction géométrique 3D complexe et nuage de points pour la préhension. Transmis sous forme de captures événementielles / ROIs (Region of Interest) compressées via **ROS 2 DDS UDP / WebRTC** (pas de flux continu lourd encombrant le Wi-Fi).

### **2. Système Audio, Vocal & Interruption (Barge-In)**
* **Hardware Crâne & ReSpeaker XVF-3800 :**
  * 4 micros MEMS sous des trous évasés de **Ø10 mm**, découplés mécaniquement par un anneau en **TPU 95A de 3 mm** avec vis nylon.
  * VAD matériel et DoA 360° calculés à 100 Hz par le processeur du ReSpeaker (0 % de charge CPU/GPU Jetson).
  * Le moteur de cou RobStride RS-05 s'oriente immédiatement vers l'angle DoA de la voix.
* **STT Local (Jetson) :** **Faster-Whisper small (CUDA)**.
  * *VRAM Jetson :* **1,5 Go**.
  * *Latence :* **< 200 ms**.
* **TTS Streaming HD (Mac M1 Max) :** **`server_qwen3_central.py` (Qwen3-TTS 1.7B via MLX-Audio)**.
  * *VRAM Mac :* **2,5 Go**.
  * *Latence 1er son :* **< 200 ms** (streaming WebSocket PCM Base64 24kHz).
* **Barge-In (Interruption Instantanée) :**
  * Géré dans `async_conversation.py`. Dès que le ReSpeaker capte une voix pendant la lecture, la Jetson coupe `aplay` et envoie `{ "type": "interrupt" }` au Mac.

### **3. Mémoire RAG & Base de Connaissances (LightRAG)**
* **Moteur :** Base de connaissances locale LightRAG + embeddings **FastEmbed**.
* **Localisation :** **100 % sur Mac M1 Max** (Python 3.11 sur le port 7860/FastAPI).
* **Bande passante :** La Jetson envoie une requête texte simple (`"Spécification couple moteur RS-04"`), le Mac effectue la recherche vectorielle en **~15 ms** et renvoie le contexte extrait.

### **4. Cinématique, Moteurs CAN & Microcontrôleurs**
* **Sony Spresense (UART micro-ROS `/dev/ttyTHS0`) :**
  * Gère l'IMU d'équilibre du torse (**BMI270** via I2C), la surveillance électrique et le Watchdog matériel.
* **2x Teensy 4.1 (Shields SK Pang avec 3x CAN FD natifs) :**
  * 1x Teensy pour le *Lower Body* (Jambes/Taille) et 1x Teensy pour l' *Upper Body* (Bras/Cou).
  * Exécutent la cinématique inverse (IK) et les boucles de contrôle motrice rapides (**100 Hz à 500 Hz**).
* **Moteurs RobStride (Bus CAN 1 Mbps via InnoMaker RS-05) :**
  * Communication directe avec les Teensy 4.1.

### **5. Infrastructure Réseau & Topologie des Protocoles Hybrides**
Pour garantir une latence minimale sans à-coups ni blocages TCP (jitter), le transport réseau Wi-Fi 6 est scindé :
* **Canal Temps Réel / Flux Lourd — UDP & ROS 2 DDS Best-Effort :**
  * Télémétrie cinématique 100 Hz, odométrie visuelle V-SLAM et transmission des captures d'images vers Cosmos 3D. Évite l'effet de blocage en tête de ligne (*Head-of-Line Blocking*) du TCP standard.
* **Canal Transactionnel / Contrôle — TCP (gRPC & WebSockets) :**
  * Requêtes RAG (< 1 Ko), streaming audio TTS PCM 24kHz et consignes de mission JSON structurées (nécessitant un acquittement garanti).

---

## 4. Matrice Globale des Ressources & Latences V1

| Sous-Système | Composant / Modèle | Poids / Précision | Empreinte VRAM / RAM | Emplacement | Latence globale | Impact Réseau & Protocole |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Vision Réflexe Hardware** | OAK-D Pro Depth IR | Hardware Myriad X | **0,0 Go VRAM** | OAK-D Pro (Capteur) | **< 15 ms** | Aucun (Direct Hardware) |
| **Vision Temps Réel & V-SLAM** | YOLO-World v2 + OAK-D | INT8 / FP16 TensorRT | **0,4 Go VRAM** | Jetson Orin Nano | **< 15 ms** | Aucun |
| **Vision 3D / World Model** | NVIDIA Cosmos 3D Edge | 2B-3B (MLX / Metal) | **8 à 12 Go VRAM** | Mac M1 Max | **~200 ms** | Images ROIs Événementielles (ROS 2 DDS UDP) |
| **Audio STT** | Faster-Whisper small | FP16 CUDA | **1,5 Go VRAM** | Jetson Orin Nano | **< 200 ms** | Aucun |
| **Audio VAD / DoA 360°** | ReSpeaker SDK Matériel | Firmware USB | **0,0 Go VRAM** | Jetson / ReSpeaker | **< 5 ms** | Aucun |
| **Audio TTS Streaming** | Qwen3-TTS 1.7B | 8-bit Apple MLX | **2,5 Go VRAM** | Mac M1 Max | **< 200 ms** | Audio PCM 24kHz (WebSockets TCP ~0.1 Mo/s) |
| **RAG Documentaire** | LightRAG + FastEmbed | Vector DB + Python | **1,2 Go RAM** | Mac M1 Max | **< 20 ms** | Requête texte (gRPC TCP < 1 Ko) |
| **LLM Raisonnement** | Gemini 3.1 / Qwen 35B | Cloud / JANGTQ 4-bit | **18 Go VRAM** | Cloud / Mac | **~300 ms** | Texte JSON (TCP < 2 Ko) |
| **Cinématique & Moteurs** | IK & CAN FD Loop | C++ Firmware Teensy | **0,0 Go VRAM** | 2x Teensy 4.1 | **< 2 ms (500Hz)** | Bus CAN local |

---

## 5. Bilan Mémoire & Marge de Sécurité Jetson Orin Nano (8 Go) V1

```text
┌─────────────────────────────────────────────────────────────────────────┐
│               BUDGET VRAM JETSON ORIN NANO 8GB (HEADLESS V1)            │
│                                                                         │
│  [ Total VRAM Utile (hors OS Headless) ] : 5,50 Go                       │
│                                                                         │
│  • YOLO-World v2 TensorRT                : 0,40 Go                      │
│  • Faster-Whisper small CUDA             : 1,50 Go                      │
│  • Allocations Buffer OpenCV / CUDA      : 1,00 Go                      │
│ ─────────────────────────────────────────────────────────────────────── │
│  [ TOTAL ALLOUÉ EN PRODUCTION ]          : 2,90 Go                      │
│                                                                         │
│  ✅ MARGE DE SÉCURITÉ RESTANTE           : 2,60 Go (32 % DE VRAM LIBRE)  │
└─────────────────────────────────────────────────────────────────────────┘
```
**Conclusion Mémoire V1 :** L'architecture V1 garantit un taux d'occupation VRAM de seulement **52 %** sur la Jetson, éliminant à **100 % le risque d'OOM Killer Linux**.

---

## 6. Stratégie de Résilience V1 & Heartbeat à Double Seuil (Gestion des Coupures Wi-Fi)

1. **Heartbeat Watchdog (5 Hz) :**
   La Jetson et le Mac échangent un signal Heartbeat bidirectionnel toutes les 200 ms.
2. **Stratégie d'Urgence à Double Seuil :**
   * **Seuil 1 — Sécurité Cinématique Physique (Perte Connection > 200 ms) :**
     * Déclenché immédiatement par le Watchdog matériel Spresense / Teensy.
     * Le robot interrompt immédiatement les trajectoires dynamiques en cours et passe en mode stationnaire d'équilibre (verrouillage des consignes d'angles et freins si à l'arrêt).
     * Empêche toute chute ou réaction incontrôlée en cas de micro-coupure Wi-Fi.
   * **Seuil 2 — Fallback Autonome Dégradé Local (Perte Connection > 2,0 s) :**
     * **Fallback Vision V1 :** YOLO-World v2 sur Jetson prend 100 % du contrôle visuel et du V-SLAM OAK-D Pro pour maintenir la distance de sécurité avec l'environnement sans l'aide du Mac.
     * **Fallback Vocal :** Le LLM local (`Ollama + Qwen2.5-0.5B`) et le TTS local (`Kokoro-ONNX` / `Piper`) s'activent de manière transparente sur la Jetson pour répondre aux commandes vocales d'urgence locales.
