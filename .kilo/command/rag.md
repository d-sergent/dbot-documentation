---
description: Recherche dans la base RAG D-Bot
---

Recherche les informations demandées dans la base Graph-RAG LightRAG du D-Bot. Utilise le wrapper `/opt/homebrew/bin/rag` pour interroger le serveur MCP `dbot-rag` (ou `ask_rag.py --search-only` en repli direct).

- Recherche par défaut : contexte précis (`rag_get_context`, 0 Go RAM LLM).
- Option `--search` : recherche hybride graphe + vecteurs via mots-clés lexicaux (ou `--llm-mode internal` si une synthèse locale Ollama/Unsloth est voulue).
- Inclus dans les résultats : documents `.md`, code Python, manuels `.pdf` et schémas `.svg`.

Présente les extraits et références exactes (cotes, codes McMaster-Carr, moteurs) de manière synthétique.
