# 📚 rag — Moteur RAG Documentaire Local (LightRAG + FastEmbed)

Ce sous-module gère le système RAG (Retrieval-Augmented Generation) du projet D-Bot. Il permet d'indexer l'ensemble de la documentation technique et de fournir un accès sémantique instantané (< 15 ms).

---

## 📄 Fichiers & Rôles

| Fichier | Rôle & Description |
| :--- | :--- |
| **[`rag_cli.py`](file:///Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/rag_cli.py)** | Client MCP CLI pour le RAG D-Bot — lance le serveur MCP `dbot-rag` et interroge la base LightRAG via le protocole MCP.<br>`rag "moteur RS04 spécifications"` (ou `/opt/homebrew/bin/rag "votre recherche"`) |
| **[`ask_rag.py`](file:///Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py)** | Script de recherche directe (sans MCP) dans la base RAG locale.<br>`/opt/homebrew/bin/python3.11 code/rag/ask_rag.py --search-only --mode naive "<votre recherche>"` |
| **[`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py)** | Script de ré-indexation incrémentale et complète (Markdown, Code, PDF Docling, schémas `.svg` via extracteur XML, images VLM). Supporte `ollama` (`qwen3.5:9b` local, texte + vision, `think=False`), `gemini` (cascade), `local` (vMLX) et `online`.<br>`/opt/homebrew/bin/python3.11 Code/rag/index_docs.py --update --provider ollama` |
| **[`mcp_lightrag_server.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/mcp_lightrag_server.py)** | Serveur MCP exposant 7 outils : `rag_search`, `rag_get_context`, `rag_analyze_impact`, `rag_list_topics`, `rag_audit_integrity`, `rag_resolve_audit`, `rag_index_document` (avec support `auto` / `ollama` / `gemini`, SVG XML et images VLM). |

---

## ⚡ Recherche, Indexation & Contrôle d'Intégrité via le RAG D-Bot (MCP)

```bash
# Recherche un sujet précis (mode local/naive — retrieval pur, pas de LLM requis)
rag "moteur d'épaule RS04 spécifications"

# Recherche sémantique hybride (délégation Antigravity par défaut, ou --llm-mode internal pour vLLM)
rag --search "stratégie de bus CAN-FD"

# Indexation au fil de l'eau d'un document modifié (auto = Gemini puis repli Ollama)
rag --index "01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md"
rag --index "01_Mecanique_et_Chassis/Torse_et_Bassin/media/solution_c_bride_monobloc_7075_et_vis_traversantes.svg" --provider ollama

# Analyse d'impact systémique (cause à effet entre composants)
rag --impact "hausse de masse du torse sur la course de l'épaule"
rag --impact "hausse de masse du torse" --llm-mode internal

# Liste des thématiques indexées
rag --topics "moteurs"

# Audit d'intégrité via votre abonnement Antigravity (mode par défaut, 0 token externe)
rag --audit cinematique_moteurs

# Audit d'intégrité via le modèle LLM interne vLLM / OpenRouter (comme avant)
rag --audit cinematique_moteurs --llm-mode internal

# Audit d'intégrité global (tous les domaines)
rag --audit

# Résolution des contradictions et génération du plan de correction (PLAN_CORRECTION.md)
rag --resolve --from-json

# Ré-indexation incrémentale par défaut (--update --provider auto : Gemini gros->petits puis repli Ollama)
/opt/homebrew/bin/python3.11 Code/rag/index_docs.py

# Ré-indexation incrémentale 100 % locale sur Mac via Ollama (texte + SVG XML + images VLM)
/opt/homebrew/bin/python3.11 Code/rag/index_docs.py --update --provider ollama

# Ré-indexation incrémentale via cascade Gemini seule
/opt/homebrew/bin/python3.11 Code/rag/index_docs.py --update --provider gemini --thinking-level low

# Optionnel : forcer le mode multi-modèles gratuits (Online / OpenRouter)
/opt/homebrew/bin/python3.11 Code/rag/index_docs.py --update --provider online
```

Le wrapper `rag` est installé dans `/opt/homebrew/bin/rag` et disponible depuis le shell.
Dans Kilo Code, utilisez `/rag "votre question"`.

---

## 🏗️ Architecture & Accès au RAG D-Bot

### Pourquoi un client MCP (`rag_cli.py`) ?

La configuration MCP dans `.kilo/kilo.jsonc` est lue par **l'extension VS Code Kilo Code** (ou le CLI `kilo`), qui agit comme *client MCP* : il démarre le serveur `dbot-rag` en processus enfant et expose ses outils (`rag_search`, `rag_get_context`, etc.).

Lorsque Kilo tourne en tant qu'**agent autonome continu** (`kilo-auto/free`), le runtime ne lit pas la configuration MCP et ne démarre pas le serveur. Le client `rag_cli.py` combler ce manque en :
1. **Démarrant le serveur MCP** `mcp_lightrag_server.py` en sous-processus (via `mcp.client.stdio.stdio_client`)
2. **Communiquant via le protocole MCP** (initialize → tools/list → tools/call)
3. **Retournant les extraits** indexés depuis la base LightRAG (`lightrag_dbot_db`)

Le serveur MCP a un **fallback automatique** en mode `naive` (retrieval pur, vectoriel + reranking) si le serveur vLLM local n'est pas disponible → aucune dépendance LLM pour les recherches de spécifications.

### Modes de recherche & Contrôle Qualité

| Mode | Outil MCP | LLM requis | Usage |
|---|---|---|---|
| Contexte précis | `rag_get_context` (local) | Non (fallback naive) | Spécifications, valeurs numériques |
| Recherche sémantique | `rag_search` (hybrid) | Oui si synthèse demandée | Questions générales |
| Analyse d'impact | `rag_analyze_impact` (global) | Oui (vLLM) | Cause → effet entre composants |
| Liste thématiques | `rag_list_topics` (naive) | Non | Explorer les sujets indexés |
| Audit d'intégrité | `rag_audit_integrity` (global) | Non avec `llm_mode='antigravity'` (utilise abonnement IDE) / Oui si `'internal'` | Détection des contradictions et désynchronisations |
| Résolution d'audit | `rag_resolve_audit` (naive/local) | Non (retrieval pur) | Localisation des fichiers contradictoires & plan de correction |
| Indexation au fil de l'eau | `rag_index_document` (insertion) | Oui (`auto` = Gemini puis Ollama, ou `ollama` local) | Mise à jour immédiate d'un document modifié (`.md`, `.py`, `.pdf`, `.svg` XML, images) |

### 🦙 Mode Local Ollama (`--provider ollama` & `qwen3.5:9b`)

Pour indexer et interroger le RAG **sans aucune dépendance aux quotas cloud (`429`/`503`)**, le pipeline supporte nativement **Ollama** (`127.0.0.1:11434`) :

1. **Modèle conseillé sur Mac M1 Max (64 Go)** : **`qwen3.5:9b`** (`7.6 Go`, quantifié `nvfp4`, 100 % GPU via `mlx`). Il gère nativement le **texte** (extraction d'entités LightRAG) et la **vision** (captures PNG/JPG).
2. **Optimisation vitesse & formatage (`/api/chat`)** :
   - Le script impose **`"think": False`** (coupe la chaîne de réflexion par défaut de `qwen3.5:9b`) et **`temperature = 0.1`**.
   - Fenêtre de contexte fixée à **`num_ctx = 16384`** (`OLLAMA_NUM_CTX`, `8192` en vision `OLLAMA_VLM_NUM_CTX`) avec parallélisme `max_async = 1`.
3. **Schémas vectoriels `.svg` (Extracteur XML structuré)** :
   - Les `.svg` ne sont plus traités comme des images bitmap : `index_docs.py` et `mcp_lightrag_server.py` extraient de façon sécurisée (`defusedxml`) les balises `<title>`, `<desc>`, `<text>` et `<tspan>` regroupées par panneau `<g>`, tout en ignorant `<defs>`, `<style>`, `<script>` et les tracés géométriques bruts.
   - `mcp_lightrag_server.py` a retiré `.svg` et `.pdf` d'`IMAGE_EXTS` : même avec `RAG_SKIP_IMAGES=true`, les schémas `.svg` et manuels `.pdf` restent toujours interrogeables.

### 🛡️ Cascade Gemini & Mode Économe (`--provider gemini`)

Lorsque `--provider gemini` est utilisé :
1. **Cascade automatique** : `gemini-3.1-flash-lite` -> `gemini-3.5-flash-lite` -> `gemini-3.6-flash` -> `gemini-3.7-flash` -> `gemini-flash-lite-latest` -> `gemini-2.5-flash`, avec repli OpenRouter gratuit en fin de cascade.
2. **Niveaux d'effort (*Thinking Level*)** : `--thinking-level minimal` (`0` token) ou `low` (`100` tokens, défaut).
3. **Cadencement anti-saturation (`429`)** : parallélisme séquentiel strict (`max_async = 1`) avec pause de `2,5 s`.

### 📄 Traitement Intelligent des Notices & Manuels PDF (Docling)

Pour les notices techniques et manuels constructeur PDF (RobStride `RS00` à `RS06`, alimentations Wanptek, capteurs MLX90393) :
- **Moteur principal** : **Docling** (IBM Research) avec modèle **TableFormer**.
- **Reconstruction des tableaux** : extrait avec exactitude les tableaux de caractéristiques (couples, tensions, brochages JST, registres CANopen) au format tableau Markdown lisible par le graphe.
- **Résilience** : bascule automatique sur `pypdf` en cas d'indisponibilité pour garantir la continuité de service.

### Démarrer l'inférence locale (M1 Max 64 Go)

Le socle local utilise **Ollama MLX** (`http://127.0.0.1:11434`) et **Unsloth Studio** (`http://127.0.0.1:8888/v1`, `unsloth/Qwen3.8-27B-GGUF` `UD-Q4_K_XL` + `mmproj-F16.gguf` Vision CAO). Voir [00_GUIDE_IA_Locale_M1Max_64Go.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/IA_sur_Mac_M1_Pro_Max_64Go/00_GUIDE_IA_Locale_M1Max_64Go.md).

> Sans serveur local joignable, `rag --search` / `ask_rag.py` bascule vers les modèles configurés ou en mode `naive` (retrieval pur) selon l'appelant.

### Gestion des images (modèles VLM vs non-VLM)

La base RAG contient des descriptions textuelles d'images raster (`.png`, `.jpg`, `.webp`) générées par VLM, ainsi que l'extraction XML structurée des schémas `.svg`.

| Variable | Valeur par défaut | Description |
|---|---|---|
| `RAG_SKIP_IMAGES` | `true` | Filtre uniquement les chunks issus d'images raster (`IMAGE_EXTS`, n'exclut ni `.svg` ni `.pdf`) + nettoie `![]()` |
| `RAG_LLM_PROVIDER` | `auto` | Fournisseur du serveur MCP pour `internal` (`auto` = Gemini puis repli Ollama puis Unsloth `:8888`, ou forcer `ollama` / `gemini` / `vmlx`) |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | URL racine du démon Ollama local |
| `OLLAMA_MODEL` | `qwen3.8:27b-mlx` (dans `.kilo/kilo.jsonc`) / `qwen3.5:9b` (défaut CLI) | Modèle Ollama utilisé pour texte, graphe et vision (`think=False`) |

> **Note** : `unsloth/Qwen3.8-27B-GGUF` (+ `mmproj-F16.gguf`) et `qwen3.5:9b` sont des modèles **VLM**. Avec `RAG_SKIP_IMAGES=false`, les chunks images textuels sont inclus tout en nettoyant les liens markdown `![]()`.

Pour désactiver le filtrage (modèle VLM), ajoutez dans `.kilo/kilo.jsonc` → `mcp.dbot-rag.environment` :
```jsonc
"RAG_SKIP_IMAGES": "false"
```

---

## 🔗 Configuration MCP (`.kilo/kilo.jsonc`)

```jsonc
"model": "unsloth-qwen38/unsloth/Qwen3.8-27B-GGUF",
"small_model": "unsloth-qwen38/unsloth/Qwen3.8-27B-GGUF",
"provider": {
  "unsloth-qwen38": {
    "npm": "@ai-sdk/openai-compatible",
    "options": { "apiKey": "sk-unsloth-VOTRE_CLE", "baseURL": "http://127.0.0.1:8888/v1" },
    "models": { "unsloth/Qwen3.8-27B-GGUF": { "name": "Qwen3.8 27B Dynamic V3.1 UD-Q4_K_XL" } }
  },
  "ollama": {
    "options": { "apiKey": "ollama", "baseURL": "http://localhost:11434/v1" },
    "models": {
      "qwen3.8:27b-mlx": { "name": "qwen3.8:27b-mlx" },
      "gemma4:26b": { "name": "gemma4:26b" },
      "qwen3.5:9b": { "name": "qwen3.5:9b" }
    }
  }
},
"mcp": {
  "dbot-rag": {
    "type": "local",
    "command": ["/opt/homebrew/bin/python3.11", ".../mcp_lightrag_server.py"],
    "environment": {
      "PYTHONPATH": ".../Code/rag",
      "RAG_DB_PATH": ".../lightrag_dbot_db",
      "RAG_LLM_PROVIDER": "auto",
      "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
      "OLLAMA_MODEL": "qwen3.8:27b-mlx",
      "VMLX_BASE_URL": "http://127.0.0.1:8888/v1",
      "VMLX_MODEL": "unsloth/Qwen3.8-27B-GGUF",
      "RAG_SKIP_IMAGES": "false"
    },
    "enabled": true, "timeout": 300000
  }
},
"permission": { "dbot-rag_*": "allow", "dbot_rag_*": "allow" }
```

> Le format a été migré de `experimental.mcpServers` (déprécié) vers la clé `mcp` (standard actuel). Les outils MCP sont en `allow` pour un usage sans prompt d'approbation. Les variables d'environnement internes `VMLX_BASE_URL` / `VMLX_MODEL` sont conservées par compatibilité avec `mcp_lightrag_server.py` et pointent vers Unsloth Studio (`:8888`).
