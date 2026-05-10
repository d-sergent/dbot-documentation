# 47 — Cerveau IA Local : Ollama & Choix du Modèle LLM

*Dernière mise à jour : 10 Mai 2026*

---

## 1. Architecture du Cerveau D-Bot

Le cerveau conversationnel de D-Bot repose sur **Ollama**, un serveur LLM local qui tourne directement sur la Jetson Orin Nano. Le code Python n'envoie jamais de données à un serveur Cloud.

```
chatbot_local_v2.py
        │
        ▼
code/dbot/brain/llm_client.py  ← DbotBrain
        │
        ▼ (HTTP localhost:11434)
   [Ollama Server]  ← tourne en background sur la Jetson
        │
        ▼
   [Modèle LLM en VRAM Jetson]
```

**Fichier de code** : `code/dbot/brain/llm_client.py`

---

## 2. Démarrage du Serveur Ollama

> [!IMPORTANT]
> Le serveur Ollama **doit impérativement être actif** avant de lancer `chatbot_local_v2.py`. Sans lui, le robot obtient une erreur de connexion.

### Lancement manuel (session de développement)

```bash
# Terminal 1 — Démarrer le serveur (garde ce terminal ouvert)
ollama serve

# Terminal 2 — Lancer le chatbot
python3 ~/dbot/code/scripts/behaviors/chatbot_local_v2.py
```

### Lancement automatique au démarrage (mode production)

Pour que D-Bot démarre seul sans intervention :

```bash
# Créer le service systemd
sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama LLM Server — D-Bot Cerveau
After=network.target

[Service]
Type=simple
User=david
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=5
Environment=OLLAMA_HOST=0.0.0.0:11434

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
```

### Vérifier que le serveur est actif

```bash
curl http://localhost:11434/api/tags
# Doit retourner la liste des modèles installés
```

---

## 3. Gestion des Modèles

### Télécharger un modèle

```bash
ollama pull qwen2.5:3b           # Modèle actuel (référence)
ollama pull nemotron-mini        # Nemotron 3 Nano 4B (recommandé 2026)
ollama pull gemma3:4b            # Gemma 3 4B (alternative Google)
```

### Lister les modèles installés

```bash
ollama list
```

### Choisir le modèle sans modifier le code

```bash
# La variable d'environnement DBOT_LLM_MODEL surcharge le défaut
DBOT_LLM_MODEL=nemotron-mini python3 code/scripts/behaviors/chatbot_local_v2.py
```

---

## 4. Analyse Comparative des Modèles (Mai 2026)

> [!NOTE]
> Ces benchmarks sont mesurés sur **Jetson Orin Nano Super 8Go** avec quantification Q4_K_M et `llama.cpp`/Ollama. La latence de réponse cible pour une conversation fluide est **< 3 secondes**.

| Modèle | Params actifs | VRAM estimée | Vitesse (tok/s) | Qualité FR | Ollama | Verdict D-Bot |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Qwen2.5:3b** | 3B | ~2.2 Go | ~12 tok/s | ⭐⭐⭐⭐ | ✅ | Référence stable actuelle |
| **Nemotron 3 Nano 4B** | 4B | ~2.3 Go | **~18-20 tok/s** | ⭐⭐⭐⭐⭐ | ✅ GGUF | ⭐ **Recommandé 2026** |
| **Gemma 3 4B** | 4B | ~3.0 Go | ~15 tok/s | ⭐⭐⭐⭐ | ✅ | Bonne alternative |
| Nemotron 30B-A3B | 3B actifs | ~4.5 Go | ~10 tok/s | ⭐⭐⭐⭐⭐ | Expérimental | Trop lourd pour Nano |
| **Gemini Nano** | N/A | Android uniquement | ❌ | N/A | ❌ | **Non compatible Jetson** |

### Pourquoi Nemotron 3 Nano 4B est le meilleur choix en 2026

> [!IMPORTANT]
> **NVIDIA a conçu Nemotron 3 Nano 4B spécifiquement pour le Jetson Orin.** Son architecture hybride **Mamba-Transformer** est particulièrement efficace sur les petites séquences conversationnelles, ce qui correspond exactement à l'usage D-Bot (réponses courtes, 2-3 phrases).

**Avantages concrets** :
- **+50-67% plus rapide** que Qwen2.5:3b (18-20 tok/s vs 12 tok/s)
- **Même empreinte mémoire** (~2.3 Go) → Pas d'impact sur le reste du système
- **Optimisé par NVIDIA** pour les Tensor Cores du Jetson (accélération native)
- Excellent score sur les benchmarks d'instructions (IFEval) → Respecte mieux les règles de personnalité D-Bot

**Pourquoi pas Gemini Nano ?**
Gemini Nano est un modèle Android intégré dans l'OS via Android AICore. Il n'est **pas disponible comme poids ouverts** et ne peut pas être déployé sur Linux/Jetson. Pour un usage Google sur Jetson, utiliser **Gemma 3** (les poids sont ouverts sur Hugging Face et disponibles via Ollama).

---

## 5. Optimisation Mémoire pour le Cerveau

> [!WARNING]
> Le LLM, le STT (Whisper) et la vision (OAK-D) se partagent les 8 Go. Respectez les règles suivantes pour éviter les crashes OOM.

| Service | RAM/VRAM | Statut |
| :--- | :---: | :--- |
| Ollama + modèle 4B | ~2.3 Go | Toujours actif |
| Faster-Whisper (small, GPU) | ~0.5 Go | Chargé à la demande |
| OAK-D Pro (vision) | ~0.3 Go | Toujours actif |
| Système Ubuntu + ROS2 | ~1.5 Go | Toujours actif |
| **Total estimé** | **~4.6 Go** | ✅ Marge de 3.4 Go |

**Commandes de libération mémoire avant de lancer le chatbot** :
```bash
# Fermer l'interface graphique si elle est active
sudo systemctl isolate multi-user.target

# Libérer les caches
sudo sysctl -w vm.drop_caches=3

# Activer le mode performance Jetson
sudo nvpmodel -m 0
sudo jetson_clocks
```

---

## 6. Fonctionnalités du Client (`llm_client.py`)

### Sélection du modèle

```python
# Par défaut (code)
brain = DbotBrain()                              # Utilise DBOT_LLM_MODEL ou nemotron-mini

# Via variable d'environnement (sans modifier le code)
# DBOT_LLM_MODEL=qwen2.5:3b python3 chatbot_local_v2.py

# En passant le modèle explicitement
brain = DbotBrain(model_name="gemma3:4b")
```

### Recherche Web intégrée (Function Calling)

Le cerveau dispose d'un outil de recherche DuckDuckGo. Quand on lui pose une question sur des événements récents, il recherche automatiquement sur le web avant de répondre. Nécessite `pip install ddgs`.

### Gestion de la mémoire conversationnelle

```python
brain.trim_memory(max_messages=10)  # Évite la saturation VRAM
brain.reset_memory()                # Repart d'une conversation vierge
```

---

*Document créé le 10/05/2026 — Mis à jour à chaque changement de modèle recommandé.*
