# ⚡ dbot_next — Architecture Master Hybride & Stream Audio Déporté

`dbot_next` est l'architecture de seconde génération du D-Bot V1. Elle établit une chaîne conversationnelle et réactive déportée à ultra-basse latence entre la **Jetson Orin Nano (Client Robot)** et le **Mac M1 Max (Serveur Compagnon)** via WebSocket bidirectionnel.

---

## 🗂️ Structure du Dossier `dbot_next`

```
Code/dbot_next/
├── companion_server.py                ← Serveur WebSocket Central (ASR + LLM + TTS)
├── companion_setup_mac.sh             ← Script d'installation de l'environnement venv Mac
├── audio/                             ← Moteur de capture streaming et VAD
│   └── audio_io_streaming.py          ← Capture parecord/arecord stéréo ➔ mono 16kHz + VAD
├── brain/                             ← Connecteurs LLM Streaming
│   └── llm_client_streaming.py        ← Client Gemini 2.0 Flash avec streaming de tokens
├── scripts/                           ← Utilities et scripts de gestion
│   ├── start_companion_server.sh      ← Script d'administration Mac (--start, --restart, --stop, --status, --logs)
│   └── test_companion_streaming.py    ← Boucle conversationnelle interactive autonome Jetson
└── tts_server/                        ← Serveurs de synthèse spécifiques
    └── server_qwen3_central.py        ← Serveur standalone Qwen3-TTS
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
│ MAC COMPAGNON (companion_server.py, Port 8001)              │     │
│  ➔ Groq Cloud Whisper Large v3 Turbo (< 300 ms)             │←────┘
│     (ou Fallback Faster-Whisper small CPU local ~900 ms)          │
│  ➔ Gemini 2.0 Flash LLM Streaming (Cloud, premier token ~0 ms)    │
│  ➔ Qwen3-TTS MLX VoiceDesign (GPU Metal 24 kHz, ~0 ms chunk)      │
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
