# 🛠️ dbot_next.scripts — Scripts de Gestion & Boucle Conversationnelle

Ce dossier regroupe les scripts d'administration des serveurs Mac et les boucles conversationnelles interactives autonomes de la Jetson.

---

## 📄 Fichiers & Rôles

| Fichier | Cible | Dépendance Mac | Description |
| :--- | :--- | :---: | :--- |
| **[`start_companion_server.sh`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/scripts/start_companion_server.sh)** | **Mac** | Port 8001 | Manager du serveur compagnon unifié (ASR + LLM + TTS). Options : `--restart`, `--stop`, `--status`, `--logs`. |
| **[`start_companion_server_tts.sh`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/scripts/start_companion_server_tts.sh)** | **Mac** | Port 8002 | Manager du serveur TTS Seul Qwen3-TTS MLX (Architecture Direct Cloud). Options : `--restart`, `--stop`, `--status`, `--logs`. |
| **[`test_companion_streaming.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/scripts/test_companion_streaming.py)** | **Jetson** | Oui (Port 8001) | Mode 1 : Client Jetson pour l'architecture All-in-One (ASR + LLM + TTS exécutés sur Mac). |
| **[`test_jetson_direct_cloud.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/scripts/test_jetson_direct_cloud.py)** | **Jetson** | Oui (Port 8002) | Mode 2 : Client Jetson pour l'architecture Direct Cloud (ASR Groq & LLM Gemini direct Jetson, TTS Qwen3-TTS Mac). |
| **[`test_jetson_edge_cloud.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/scripts/test_jetson_edge_cloud.py)** | **Jetson** | **Non (100% Jetson)** | Mode 3 : Architecture 100% Autonome Jetson (ASR Groq & LLM Gemini direct Jetson, TTS Microsoft Edge-TTS `fr-FR-HenriNeural`). |

---

## ⚡ Exécution

### Mode 1 — Compagnon Complet (Port 8001)
```bash
# Sur le Mac :
./Code/dbot_next/scripts/start_companion_server.sh --restart

# Sur la Jetson :
python3 code/dbot_next/scripts/test_companion_streaming.py
```

### Mode 2 — Jetson Direct Cloud (TTS Mac Port 8002)
```bash
# Sur le Mac :
./Code/dbot_next/scripts/start_companion_server_tts.sh --restart

# Sur la Jetson :
python3 code/dbot_next/scripts/test_jetson_direct_cloud.py
```

### Mode 3 — Jetson Edge Cloud (100% Jetson, Sans Mac)
```bash
# Sur la Jetson (Pas besoin d'allumer le Mac !) :
# Prérequis unique sur Jetson : pip3 install edge-tts
python3 code/dbot_next/scripts/test_jetson_edge_cloud.py
```
