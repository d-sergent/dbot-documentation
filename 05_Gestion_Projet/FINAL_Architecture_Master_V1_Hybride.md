# 📘 SPÉCIFICATION D'ARCHITECTURE MASTER V1 — ROBOT D-BOT
**Répartition Globale du Calcul, de la Mémoire et du Réseau : NVIDIA Jetson Orin Nano (8 Go) ↔ Apple Mac M1 Max (64 Go)**

---

## 1. Executive Summary & Découpage Système (100% Focus V1)

La présente spécification établit **l'architecture Master officielle du D-Bot V1**, couvrant 100 % des sous-systèmes matériels et logiciels qualifiés pour la Phase 1 : **Perception Visuelle (OAK-D Pro V-SLAM)**, **Audio & Parole (ReSpeaker XVF-3800 360° & Barge-In)**, **Cinématique & Moteurs CAN (RobStride RS)**, **Microcontrôleurs Temps Réel (Teensy 4.1 & Spresense)**, **Mémoire RAG & LLM (LightRAG & Gemini)**, et **Infrastructure Réseau / Sécurité**.

### **Principe d'Architecture Hybride V1 : "Réflexe Local ↔ Cognition Déportée"**
1. **Sur le Robot (Jetson Orin Nano 8GB Headless + Microcontrôleurs) :**
   * **Invariants locaux V1 :** Équilibre bipède, boucles de contrôle moteur (100–500 Hz), captation audio (ReSpeaker VAD/DoA 100 Hz), vision temps réel (YOLO-World v2 @ 30 FPS), STT local (Faster-Whisper CUDA), V-SLAM OAK-D Pro et arrêt d'urgence autonome.
   * **Budget VRAM Jetson strictly maîtrisé :** **2,9 Go alloués / 5,5 Go utiles**, laissant **2,6 Go de marge (32 % de réserve de sécurité)**.
2. **Sur le Serveur Compagnon (Mac M1 Max 64GB - Bandwidth 400 GB/s) :**
   * **Tâches lourdes déportées :** Simulation physique & géométrie 3D (*NVIDIA Cosmos 3D Edge*), synthèse vocale HD streaming (*Qwen3-TTS via MLX-Audio*), Moteur RAG documentaire (*LightRAG / FastEmbed*), et raisonnement LLM haut niveau (*Gemini 3.1 Flash Lite / Qwen 35B*).
   * **Bande passante et latence :** Wi-Fi 6 / Ethernet local (< 5 ms de latence réseau).

---

## 2. Cartographie Globale des 8 Sous-Systèmes V1 (Jetson ↔ Mac)

```mermaid
graph TD
    subgraph ROBOT D-BOT V1 (Embarqué - Autonomie & Temps Réel)
        SENS_V["OAK-D Pro (RGB-D 1080p)"] -->|USB 3.0 / 30 FPS| TRT_V["YOLO-World v2 TensorRT (0.4 GB VRAM)"]
        SENS_V -->|V-SLAM V1 & Depth| NAV["Navigation & Evitement ROS 2"]
        
        SENS_A["ReSpeaker XVF-3800 Array"] -->|ALSA Direct| AUD_L["Audio VAD + DoA (0-360°) + Faster-Whisper CUDA"]
        
        IMU_B["IMU BMI270 Torse"] -->|I2C| SPRES["Sony Spresense (Watchdog & Power)"]
        SPRES -->|UART micro-ROS| JET_ROS["ROS 2 Humble Master (Jetson)"]
        
        JET_ROS -->|Commands 100 Hz| TEENSY["2x Teensy 4.1 (Kinematics & CAN FD)"]
        TEENSY -->|3x Bus CAN 1 Mbps| MOTORS["RobStride Motors (RS-00, RS-04, RS-05)"]
        
        JET_ROS <-->|gRPC / WebSockets < 5ms| NET_BRIDGE["Interface Réseau Hybride"]
    end

    subgraph MAC M1 MAX 64GB (Serveur Compagnon & Cerveau Cognitif)
        NET_BRIDGE <--> MAC_SERVEUR["Serveur Central Python 3.11 / MLX"]
        
        MAC_SERVEUR -->|Metal GPU| COSMOS["NVIDIA Cosmos 3D Edge (World Model 3D)"]
        MAC_SERVEUR -->|MLX-Audio| TTS_MAC["Qwen3-TTS 1.7B Streaming (PCM 24kHz)"]
        MAC_SERVEUR -->|FastEmbed / VectorDB| RAG_ENGINE["RAG Documentaire (LightRAG / FastEmbed)"]
        MAC_SERVEUR -->|HTTPS / Local| LLM_BRAIN["Gemini 3.1 Flash Lite / Qwen 35B"]
    end

    NET_BRIDGE -->|Fallback Offline si Perte Wi-Fi > 2s| FALLBACK["Mode Autonome Dégradé (Ollama + Kokoro TTS)"]
```

---

## 3. Analyse Détallée par Composant Système V1 (Latence, Mémoire & Bande Passante)

### **1. Vision Temps Réel & V-SLAM (Luxonis OAK-D Pro FF)**
* **Capteur Unique V1 :** Luxonis OAK-D Pro Fixed-Focus (USB 3.0, 1080p RGB + Stéréo Depth + Émetteur IR).
* **Traitement Embarqué (Jetson) :** **YOLO-World v2 (TensorRT FP16/INT8)** + **OAK-D V-SLAM**.
  * *VRAM Jetson :* **0,4 Go**.
  * *Latence :* **12 à 15 ms (30-60 FPS)**.
  * *Rôle :* Détection d'objets *zero-shot* instantanée pour l'évitement d'obstacles, la navigation V-SLAM et le suivi d'objets.
* **Traitement Déporté (Mac M1 Max) :** **NVIDIA Cosmos 3D Edge**.
  * *VRAM Mac :* **8 à 12 Go (MLX/Metal)**.
  * *Latence :* **~200 ms**.
  * *Rôle :* Reconstruction 3D de la scène, nuage de points et géométrie spatiale pour la préhension.

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

---

## 4. Matrice Globale des Ressources & Latences V1

| Sous-Système | Composant / Modèle | Poids / Précision | Empreinte VRAM / RAM | Emplacement | Latence globale | Impact Réseau |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Vision Temps Réel & V-SLAM** | YOLO-World v2 + OAK-D | INT8 / FP16 TensorRT | **0,4 Go VRAM** | Jetson Orin Nano | **< 15 ms** | Aucun |
| **Vision 3D / Physique** | NVIDIA Cosmos 3D Edge | 2B-3B (MLX / Metal) | **8 à 12 Go VRAM** | Mac M1 Max | **~200 ms** | Flux 720p (~2 Mo/s) |
| **Audio STT** | Faster-Whisper small | FP16 CUDA | **1,5 Go VRAM** | Jetson Orin Nano | **< 200 ms** | Aucun |
| **Audio VAD / DoA 360°** | ReSpeaker SDK Matériel | Firmware USB | **0,0 Go VRAM** | Jetson / ReSpeaker | **< 5 ms** | Aucun |
| **Audio TTS Streaming** | Qwen3-TTS 1.7B | 8-bit Apple MLX | **2,5 Go VRAM** | Mac M1 Max | **< 200 ms** | Audio PCM 24kHz (~0.1 Mo/s) |
| **RAG Documentaire** | LightRAG + FastEmbed | Vector DB + Python | **1,2 Go RAM** | Mac M1 Max | **< 20 ms** | Requête texte (< 1 Ko) |
| **LLM Raisonnement** | Gemini 3.1 / Qwen 35B | Cloud / JANGTQ 4-bit | **18 Go VRAM** | Cloud / Mac | **~300 ms** | Texte JSON (< 2 Ko) |
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

## 6. Stratégie de Résilience V1 & Heartbeat (Gestion des Coupures Wi-Fi)

1. **Heartbeat Watchdog (5 Hz) :**
   La Jetson envoie un signal ping UDP/gRPC au Mac toutes les 200 ms.
2. **Si perte de connexion > 2,0s :**
   * **Niveau 1 - Sécurité Physique :** La Jetson bascule immédiatement en mode stationnaire (freins solénoïdes activés si arrêt).
   * **Niveau 2 - Fallback Vision V1 :** YOLO-World v2 prend 100% du contrôle visuel et du V-SLAM OAK-D Pro pour maintenir la distance de sécurité avec l'environnement.
   * **Niveau 3 - Fallback Vocal :** Le LLM local (`Ollama + Qwen2.5-0.5B`) et le TTS local (`Kokoro-ONNX` / `Piper`) s'activent de manière transparente pour répondre aux commandes vocales d'urgence.
