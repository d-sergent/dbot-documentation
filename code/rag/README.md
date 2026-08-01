# 📚 rag — Moteur RAG Documentaire Local (LightRAG + FastEmbed)

Ce sous-module gère le système RAG (Retrieval-Augmented Generation) du projet D-Bot. Il permet d'indexer l'ensemble de la documentation technique et de fournir un accès sémantique instantané (< 15 ms).

---

## 📄 Fichiers & Rôles

| Fichier | Rôle & Description |
| :--- | :--- |
| **[`rag_cli.py`](file:///Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/rag_cli.py)** | Client MCP CLI pour le RAG D-Bot — lance le serveur MCP `dbot-rag` et interroge la base LightRAG via le protocole MCP.<br>`rag "moteur RS04 spécifications"` (ou `/opt/homebrew/bin/rag "votre recherche"`) |
| **[`ask_rag.py`](file:///Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py)** | Script de recherche directe (sans MCP) dans la base RAG locale.<br>`/opt/homebrew/bin/python3.11 code/rag/ask_rag.py --search-only --mode naive "<votre recherche>"` |
| **[`index_docs.py`](file:///Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py)** | Script de ré-indexation automatique de la documentation Markdown. À exécuter en fin de session de travail.<br>`/opt/homebrew/bin/python3.11 code/rag/index_docs.py` |
| **[`mcp_lightrag_server.py`](file:///Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/mcp_lightrag_server.py)** | Serveur MCP exposant 4 outils : `rag_search`, `rag_get_context`, `rag_analyze_impact`, `rag_list_topics`. |

---

## ⚡ Recherche via le RAG D-Bot (MCP)

```bash
# Recherche un sujet précis (mode local/naive — retrieval pur, pas de LLM requis)
rag "moteur d'épaule RS04 spécifications"

# Recherche sémantique hybride (nécessite vLLM en local pour la synthèse LLM)
rag --search "impact d'une hausse de masse du bras sur la course de l'épaule"

# Liste des thématiques indexées
rag --topics "moteurs"
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

### Modes de recherche

| Mode | Outil MCP | LLM requis | Usage |
|---|---|---|---|
| Contexte précis | `rag_get_context` (local) | Non (fallback naive) | Spécifications, valeurs numériques |
| Recherche sémantique | `rag_search` (hybrid) | Oui (vLLM) | Questions générales |
| Analyse d'impact | `rag_analyze_impact` (global) | Oui (vLLM) | Cause → effet entre composants |
| Liste thématiques | `rag_list_topics` (naive) | Non | Explorer les sujets indexés |

### Démarrer le serveur vLLM (optionnel — pour le mode hybride)

```bash
vllm serve JANGQ-AI/Qwen3.6-35B-A3B-JANGTQ4 --port 8080
```

> Sans vLLM, `rag --search` bascule automatiquement en mode `naive` (retrieval pur) avec un avertissement, mais reste fonctionnel.

---

## 🔗 Configuration MCP (`.kilo/kilo.jsonc`)

```jsonc
"mcp": {
  "dbot-rag": {
    "type": "local",
    "command": ["/opt/homebrew/bin/python3.11", ".../mcp_lightrag_server.py"],
    "environment": {
      "PYTHONPATH": ".../Code/rag",
      "RAG_DB_PATH": ".../lightrag_dbot_db",
      "VMLX_BASE_URL": "http://127.0.0.1:8080/v1"
    },
    "enabled": true,
    "timeout": 30000
  }
},
"permission": {
  "dbot-rag_*": "allow"
}
```

> Le format a été migré de `experimental.mcpServers` (déprécié) vers la clé `mcp` (standard actuel). Les outils MCP sont en `allow` pour un usage sans prompt d'approbation.
