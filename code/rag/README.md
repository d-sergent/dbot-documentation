# 📚 rag — Moteur RAG Documentaire Local (LightRAG + FastEmbed)

Ce sous-module gère le système RAG (Retrieval-Augmented Generation) du projet D-Bot. Il permet d'indexer l'ensemble de la documentation technique et de fournir un accès sémantique instantané (< 15 ms).

---

## 📄 Fichiers & Rôles

| Fichier | Rôle & Description |
| :--- | :--- |
| **[`rag_cli.py`](file:///Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/rag_cli.py)** | Client MCP CLI pour le RAG D-Bot — lance le serveur MCP `dbot-rag` et interroge la base LightRAG via le protocole MCP.<br>`rag "moteur RS04 spécifications"` (ou `/opt/homebrew/bin/rag "votre recherche"`) |
| **[`ask_rag.py`](file:///Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py)** | Script de recherche directe (sans MCP) dans la base RAG locale.<br>`/opt/homebrew/bin/python3.11 code/rag/ask_rag.py --search-only --mode naive "<votre recherche>"` |
| **[`index_docs.py`](file:///Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py)** | Script de ré-indexation par lots (Solution 1). Supporte `--provider antigravity` avec `gemini-3.8-flash` et raisonnement économe.<br>`/opt/homebrew/bin/python3.11 code/rag/index_docs.py --provider antigravity --thinking-level low` |
| **[`mcp_lightrag_server.py`](file:///Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/mcp_lightrag_server.py)** | Serveur MCP exposant 7 outils : `rag_search`, `rag_get_context`, `rag_analyze_impact`, `rag_list_topics`, `rag_audit_integrity`, `rag_resolve_audit`, `rag_index_document`. |

---

## ⚡ Recherche, Indexation & Contrôle d'Intégrité via le RAG D-Bot (MCP)

```bash
# Recherche un sujet précis (mode local/naive — retrieval pur, pas de LLM requis)
rag "moteur d'épaule RS04 spécifications"

# Recherche sémantique hybride (délégation Antigravity par défaut, ou --llm-mode internal pour vLLM)
rag --search "stratégie de bus CAN-FD"

# Indexation au fil de l'eau d'un document modifié (Solution 2 - Économe en quota Antigravity)
rag --index "01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_Synthese_Mecanique_Torse.md"
rag --index "01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_Synthese_Mecanique_Torse.md" --thinking-level minimal

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

# Ré-indexation par lots de fin de session (Antigravity gemini-3.8-flash en mode low par défaut)
/opt/homebrew/bin/python3.11 code/rag/index_docs.py

# Optionnel : forcer l'ancien mode multi-modèles gratuits (Online / OpenRouter)
/opt/homebrew/bin/python3.11 code/rag/index_docs.py --provider online
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
| Indexation au fil de l'eau | `rag_index_document` (insertion) | Oui (Antigravity SDK `gemini-3.8-flash`) | Mise à jour immédiate d'un document modifié (quelques secondes) |

### 🛡️ Optimisation des Quotas d'Abonnement Antigravity (Raisonnement Économe)

Pour préserver vos quotas d'abonnement Antigravity lors des extractions d'entités par LightRAG :
1. **Modèle de référence** : `gemini-3.8-flash` (recommandé officiellement par Google pour le meilleur ratio vitesse / consommation de quota).
2. **Niveaux d'effort de raisonnement (*Thinking Level*)** :
   - `--thinking-level minimal` : Coupe les tokens de réflexion superflus ("thought tokens"). Le modèle extrait directement les entités et relations au format JSON. Réduction de plus de 80 % de la consommation de quota par rapport à un mode standard.
   - `--thinking-level low` : Réflexion concise ultra-courte (mode par défaut recommandé).
3. **Cadencement anti-saturation (Rate-Limit 429)** :
   - Parallélisme séquentiel strict (`max_async = 1`) avec pause de courtoisie (2,5 s) pour ne jamais saturer le débit de requêtes.

### 📄 Traitement Intelligent des Notices & Manuels PDF (Docling)

Pour les notices techniques et manuels constructeur PDF (RobStride `RS00` à `RS06`, alimentations Wanptek, capteurs MLX90393) :
- **Moteur principal** : **Docling** (IBM Research) avec modèle **TableFormer**.
- **Reconstruction des tableaux** : extrait avec exactitude les tableaux de caractéristiques (couples, tensions, brochages JST, registres CANopen) au format tableau Markdown lisible par le graphe.
- **Résilience** : bascule automatique sur `pypdf` en cas d'indisponibilité pour garantir la continuité de service.

### Démarrer le serveur vLLM (optionnel — pour le mode hybride)

```bash
# Qwen 3.6 27B (VLM — port 8012)
vllm serve lmstudio-community/Qwen3.6-27B-MLX-8bit --port 8012

# Gemma 4 31B (non-VLM — port 8006)
vllm serve JANGQ-AI/Gemma-4-31B-it-JANG_4M --port 8006
```

> Le RAG D-Bot utilise **Qwen 3.6 27B (port 8012)** par défaut. Sans serveur vLLM, `rag --search` bascule automatiquement en mode `naive` (retrieval pur) avec un avertissement, mais reste fonctionnel.

### Gestion des images (modèles VLM vs non-VLM)

La base RAG contient des chunks d'images (`.png`, `.svg`) — du texte extrait par un modèle VLM. La stratégie dépend de la capacité du modèle :

| Variable | Valeur par défaut | Description |
|---|---|---|
| `RAG_SKIP_IMAGES` | `true` | Filtre les chunks d'images + nettoie markdown `![]()` 

> **Note** : Qwen 3.6 27B est un modèle **VLM**. Le config `RAG_SKIP_IMAGES=false` est utilisé — les chunks images sont inclus (texte VLM). Les références markdown `![]()` sont **toujours nettoyées** pour empêcher Kilo de lire les fichiers images.

Pour désactiver le filtrage (modèle VLM), ajoutez dans `.kilo/kilo.jsonc` → `mcp.dbot-rag.environment` :
```jsonc
"RAG_SKIP_IMAGES": "false"
```

---

## 🔗 Configuration MCP (`.kilo/kilo.jsonc`)

```jsonc
"model": "vmlx/qwen3.6-27b",            // modèle par défaut (VLM)
"small_model": "vmlx/gemma-4-31b",       // modèle secondaire (non-VLM)
"provider": {
  "vmlx": {                               // ← Qwen 3.6 27B (port 8012, VLM)
    "options": { "apiKey": "not-needed", "baseURL": "http://127.0.0.1:8012/v1" },
    "models": { "qwen3.6-27b": { "name": "lmstudio-community/Qwen3.6-27B-MLX-8bit" } }
  },
  "vmlx-gemma": {                          // ← Gemma 4 31B (port 8006, non-VLM)
    "options": { "apiKey": "not-needed", "baseURL": "http://127.0.0.1:8006/v1" },
    "models": { "gemma-4-31b": { "name": "JANGQ-AI/Gemma-4-31B-it-JANG_4M" } }
  }
},
"mcp": {
  "dbot-rag": {
    "type": "local",
    "command": ["/opt/homebrew/bin/python3.11", ".../mcp_lightrag_server.py"],
    "environment": {
      "PYTHONPATH": ".../Code/rag",
      "RAG_DB_PATH": ".../lightrag_dbot_db",
      "VMLX_BASE_URL": "http://127.0.0.1:8012/v1",
      "VMLX_MODEL": "lmstudio-community/Qwen3.6-27B-MLX-8bit",
      "RAG_SKIP_IMAGES": "true"
    },
    "enabled": true, "timeout": 30000
  }
},
"permission": { "dbot-rag_*": "allow" }
```

> Le format a été migré de `experimental.mcpServers` (déprécié) vers la clé `mcp` (standard actuel). Les outils MCP sont en `allow` pour un usage sans prompt d'approbation.
