# 📚 rag — Moteur RAG Documentaire Local (LightRAG + FastEmbed)

Ce sous-module gère le système RAG (Retrieval-Augmented Generation) du projet D-Bot. Il permet d'indexer l'ensemble de la documentation technique et de fournir un accès sémantique instantané (< 15 ms).

---

## 📄 Fichiers & Rôles

| Fichier | Rôle & Description |
| :--- | :--- |
| **[`ask_rag.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/ask_rag.py)** | Script de recherche et de questionnement de la base RAG locale.<br>`/opt/homebrew/bin/python3.11 code/rag/ask_rag.py --search-only --mode naive "<votre recherche>"` |
| **[`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py)** | Script de ré-indexation automatique de la documentation Markdown. À exécuter en fin de session de travail.<br>`/opt/homebrew/bin/python3.11 code/rag/index_docs.py` |
| **[`mcp_lightrag_server.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/mcp_lightrag_server.py)** | Serveur FastAPI / MCP exposant l'API LightRAG sur le port `7860`. |

---

## ⚡ Exécution d'une Recherche RAG

```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode naive "moteur RS06 cou"
```
