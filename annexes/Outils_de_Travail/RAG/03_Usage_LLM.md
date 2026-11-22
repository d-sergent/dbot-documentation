# 💬 Usage du RAG avec les LLMs (Kilo / Unsloth Studio / Ollama & Antigravity)

Ce guide explique comment faire pour que vos modèles d'IA utilisent réellement la base de connaissances plutôt que de "halluciner" des réponses.

---

## 🏗️ Utilisation locale (Kilo / Unsloth Studio / Ollama)

Un modèle local (`Qwen3.8-27B`, `Gemma 4 26B-A4B`, `qwen3.5:9b`) n'appelle pas toujours les outils de lui-même par défaut s'il n'est pas guidé. 

### La "Phrase Magique"
Pour forcer l'usage du RAG, commencez votre question par :
> **"En utilisant tes outils RAG, réponds à : [Votre question]"**

### Les outils disponibles :
1.  **`rag_search`** : Pour les recherches générales.
2.  **`rag_analyze_impact`** : Pour les relations de cause à effet (ex: changement de moteur).
3.  **`rag_get_context`** : Pour extraire des spécifications techniques précises (couples, poids, dimensions).

### Interprétation des résultats et Traces Moteur
- **Mode `auto` (défaut MCP `rag_search`, `rag_analyze_impact`, `rag_audit_integrity` & CLI `ask_rag.py` / `check_integrity.py`)** : synthétise via la cascade rapide **Gemini `-lite` -> `1min.ai` (`mistral-small-2603`) -> Ollama `gemma4:26b`** (sinon `qwen3.8:27b-mlx` / Unsloth), en basculant automatiquement vers les extraits bruts `antigravity` sous MCP si tous les LLM échouent, et en affichant systématiquement `> **Trace Moteur RAG** : <fournisseur> / <modele> | bascules: ...`.
- **Mode `internal`** : impose la même cascade LLM rapide sans repli sur les extraits bruts `antigravity`.
- **Mode `antigravity` (`--search-only` / `llm_mode="antigravity"`)** : le serveur renvoie directement les **extraits bruts rerankés** (`[Source 1: ...] [Score: 0.92]`) avec `> **Trace Moteur RAG** : Aucun LLM (...)` pour synthèse directe par l'agent actif sans aucun appel LLM.

---

## 🛸 Utilisation dans Antigravity (Cloud)

Antigravity est nativement "Agentic". Il sait quand il a besoin de chercher dans la documentation. 

### Exemples de requêtes performantes :
- *"Antigravity, cherche dans le RAG quel est le ratio de réduction du genou et analyse si on peut porter 5kg de plus."*
- *"Vérifie dans la doc si le code audio `stt.py` est à jour avec la dernière version du RAG."*

---

## 🎯 Astuces pour de meilleures réponses

1.  **Soyez spécifique** : Au lieu de "le moteur", dites "le RS-04" ou "le moteur de hanche".
2.  **Demandez des preuves** : *"Donne-moi le couple du RS-04 et cite la source du RAG."*
3.  **Reformulez** : Si le RAG ne trouve rien, essayez de retirer les adjectifs (ex: au lieu de "le superbe pignon en alu", cherchez "pignon alu genou").
