# ⚡ dbot_next — Architecture Master Hybride & Stream Audio Déporté

`dbot_next` est l'architecture de seconde génération du D-Bot V1. Elle établit une chaîne conversationnelle et réactive déportée à ultra-basse latence entre la **Jetson Orin Nano (Client Robot)** et le **Mac M1 Max (Serveur Compagnon)** via WebSocket bidirectionnel.

---

## 🗂️ Structure du Dossier `dbot_next`

```
Code/dbot_next/
├── companion_server_full_mac.py       ← (Version A) Serveur All-in-One Mac (ASR + LLM + TTS, Port 8001)
├── companion_server_tts_mac.py        ← (Version B - Action 1) Serveur TTS Seul Qwen3-TTS MLX (Port 8002)
├── companion_setup_mac.sh             ← Script d'installation venv Mac
├── audio/
│   └── audio_io_streaming.py          ← Capture parecord/arecord 16kHz mono + VAD RMS
├── brain/
│   └── llm_client_streaming.py        ← Client Gemini 2.0 Flash Streaming
└── scripts/
    ├── start_companion_server.sh      ← Manager Mac pour Version A (Port 8001)
    ├── start_companion_server_tts.sh  ← Manager Mac pour Version B TTS (Port 8002)
    ├── test_companion_streaming.py    ← Client Jetson pour Version A (Port 8001)
    └── test_jetson_direct_cloud.py    ← Client Jetson pour Version B Direct Cloud (Action 1)
```

---

## 🏗️ Comparatif des Deux Architectures Available

### Version A — Mac All-in-One (Historique, Port 8001)
Toute la logique ASR, LLM et TTS est centralisée sur le Mac :
```bash
# Sur le Mac :
./Code/dbot_next/scripts/start_companion_server.sh --restart

# Sur la Jetson :
python3 code/dbot_next/scripts/test_companion_streaming.py
```

### Version B — Jetson Direct Cloud (Action 1 - Nouvelle, Port 8002)
La Jetson fait l'ASR (Groq) et le LLM (Gemini 2.0 Flash) en direct via Internet, et ne sollicite le Mac que pour le TTS Qwen3-TTS (Port 8002) :
```bash
# 1. Sur le Mac : Lancer le serveur TTS Seul sur le port 8002
./Code/dbot_next/scripts/start_companion_server_tts.sh --restart

# 2. Sur la Jetson : Lancer le client Direct Cloud
export DBOT_MAC_IP="192.168.68.120"
python3 code/dbot_next/scripts/test_jetson_direct_cloud.py
```

---

## 🚀 Architecture de Streaming Déporté (Jetson ↔ Mac)

```
┌───────────────────────────────────────────────────────────────────┐
│ JETSON ORIN NANO (Client Robot)                                   │
│  parecord --device=SOURCE --channels=2 --format=s16le             │
│  ➔ AudioIOStreaming (canal gauche mono 16 kHz extrait en queue)   │
│  ➔ VAD logicielle RMS (seuil 150 RMS min + pre-roll 5 chunks)     │
│  ➔ Mute VAD anti-auto-écoute pendant paplay                      │
│  ➔ WebSocket /conversation (chunks PCM base64) ─────────────┐    │
└─────────────────────────────────────────────────────────────│─────┘
                                                              │
┌─────────────────────────────────────────────────────────────│─────┐
│ MAC COMPAGNON (companion_server.py, Port 8001 / companion_server_tts_mac.py, Port 8002)
│  ➔ Groq Cloud Whisper Large v3 Turbo (< 300 ms)             │←────┘
│     (ou Fallback Faster-Whisper small CPU local ~900 ms)          │
│  ➔ Gemini 2.0 Flash LLM Streaming (Cloud, premier token ~0 ms)    │
│  ➔ Qwen3-TTS MLX VoiceDesign (GPU Metal 24 kHz, ~0 ms chunk)      │
│     (Sécurisé : mx.metal.clear_cache(), gc.collect(), asyncio.Lock) │
│  └─ WebSocket (paquets JSON audio base64 + texte) ──────────┐     │
└─────────────────────────────────────────────────────────────│─────┘
                                                              │
┌─────────────────────────────────────────────────────────────│─────┐
│ JETSON (Lecture Audio) ─────────────────────────────────────│←────┘
│  PCM 24 kHz ➔ paplay --device=SINK_RESPEAKER                      │
│  ➔ DAC ReSpeaker XVF-3800 ➔ Ampli JST 5W ➔ Haut-Parleur          │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Commandes de Gestion et Lancement

### 1. Sur le Mac Compagnon

#### Administration du Serveur (`start_companion_server.sh`)
```bash
# Démarrer ou relancer proprement le serveur (charge les modèles ASR/TTS/LLM)
./Code/dbot_next/scripts/start_companion_server.sh --restart

# Vérifier le statut du serveur et le mode ASR actif
./Code/dbot_next/scripts/start_companion_server.sh --status

# Suivre les logs de conversation en temps réel (Ctrl+C pour quitter)
./Code/dbot_next/scripts/start_companion_server.sh --logs

# Arrêter le serveur
./Code/dbot_next/scripts/start_companion_server.sh --stop
```

### 2. Sur la Jetson Orin Nano

#### Lancement de la boucle conversationnelle
```bash
cd ~/dbot
git pull
export DBOT_MAC_IP="192.168.68.120"
python3 code/dbot_next/scripts/test_companion_streaming.py
```

---

## ⏱️ Profilage de Latence Validé (Juillet 2026)

Le serveur intègre un profilage multi-étapes en millisecondes :

| Étape | Mode Local | Mode Groq Cloud |
| :--- | :---: | :---: |
| **VAD Fin de phrase** | 1600 ms | 1600 ms |
| **ASR Speech-to-Text** | 993 ms (Faster-Whisper `small`) | **~200 ms** (Whisper Turbo) |
| **LLM Gemini 2.0 Flash** | ~0 ms (streaming) | ~0 ms (streaming) |
| **TTS Qwen3-TTS GPU Metal** | ~0 ms (streaming) | ~0 ms (streaming) |
| 🚀 **LATENCE TOTALE PERÇUE** | **1553 ms** | **~750 ms** |

---

## ⚙️ Configuration `.env`

Le serveur lit le fichier `.env` à la racine de la documentation :

```env
GEMINI_API_KEY=AIzaSyCDvYBHHAMImxX...
OPENROUTER_API_KEY=sk-or-v1-d224f895...
GROQ_API_KEY=gsk_...
```

Si `GROQ_API_KEY` est renseigné, Groq Cloud ASR est activé par défaut. Si omis ou vide, le serveur bascule automatiquement sur Faster-Whisper `small` local.

> [!NOTE]
> **Choix Architectural Groq vs ElevenLabs** : **Groq Cloud ASR** a été retenu comme fournisseur principal de transcription vocale en raison de son **Free Tier extrêmement généreux (7200 secondes d'audio par heure, soit 2 heures gratuites/heure)** et d'une latence d'inférence exceptionnelle (< 300 ms avec Whisper Large v3 Turbo). À l'inverse, ElevenLabs limite son offre gratuite à 10 000 caractères par mois (~10 minutes d'audio totales).

