# 🤖 Guide Principal : D-Bot Graph RAG

Ce guide centralise toutes les instructions pour utiliser le système de recherche intelligente (RAG) du projet D-Bot. Le système utilise **LightRAG** (Graphe de connaissances + Vecteurs) et un **Reranker local** pour une précision maximale.

---

## 🚀 Commandes Rapides (Le Pense-Bête)

### 1. Mettre à jour la base (À faire quotidiennement)
Ajoute les nouveaux fichiers, schémas `.svg` (texte XML), PDF ou images modifiées, et purge proprement les fichiers archivés ou supprimés :

**Mode automatique recommandé (`--provider auto` : cascade complète Gemini Free Tier -> repli local `qwen3.8:27b-mlx`) :**
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py"
```

**Mode 100 % local Ollama (`qwen3.8:27b-mlx`, texte + vision, sans quota cloud) :**
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider ollama
```

**Mode cloud Gemini seul (`gemini-3.8-flash` -> cascade Free Tier) :**
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider gemini
```

**Mise à jour instantanée d'un seul fichier via MCP CLI (`auto` = Gemini non-lite -> `qwen3.8:27b-mlx`) :**
```bash
rag --index "01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md"
```

**Indexation directe par Antigravity sans LLM tiers (`effort_profile="balanced"`, sans `extra_high`) :**
```bash
rag --prepare-agent --effort-profile balanced "01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md"
```
*(Ou directement dans le chat Antigravity via les outils MCP `rag_prepare_agent_index` et `rag_commit_agent_index`.)*

### 2. Poser une question technique en ligne de commande
Idéal pour une réponse ultra-rapide sans ouvrir d'interface (`[Moteur RAG : ...]` affiché systématiquement).

```bash
# Recherche pure sans LLM (0 Go RAM GPU : injecte hl_keywords/ll_keywords puis repli naive garanti)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode hybrid "Votre question"

# Recherche hybride avec mots-cles explicites (contourne l'extraction LLM)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode hybrid --keywords "RB8016,RS-06,waist" "Votre question"

# Synthèse auto (Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b -> Unsloth -> OpenRouter)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" "Votre question"

# Synthèse forcee 100 % locale via Ollama (gemma4:26b en QA) ou Unsloth Studio (:8888/v1)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" "Votre question" --provider ollama
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" "Votre question" --provider unsloth

# Liberer manuellement la memoire unifiee Ollama apres une session
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --stop-server
```

### 3. Contrôler la qualité RAG et la parité CAO / BOM / SVG (0 LLM, Temps Réel)
Vérifie instantanément l'état de la base LightRAG, les écarts entre `AUDIT_METROLOGIQUE_Torse_et_Bassin.json` et les dossiers techniques/BOM, la fraîcheur des `.svg` et la hiérarchie bi-temporelle `Niveau 1 > Niveau 2` (aussi intégrée dans `check_integrity.py`) :

```bash
# Audit qualite CLI (0 LLM)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/rag_quality_audit.py" --top 10

# Cockpit Web FastAPI (http://127.0.0.1:8765 — onglet Parite CAO / BOM / SVG)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/rag_monitor_ui.py" --port 8765
```

---

## 💬 Usage avec les LLMs

### Dans Kilo / Unsloth Studio & Ollama (Modèles locaux)
Le serveur MCP `dbot-rag` doit être actif. Pour forcer l'usage du RAG, utilisez cette syntaxe :
> *"Utilise l'outil `rag_search` pour me dire : [Votre question]"*

### Dans Antigravity (Cloud)
Antigravity a accès au même serveur MCP (`llm_mode="auto"` par défaut : `Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b` avec repli transparent `antigravity` ; passer `llm_mode="antigravity"` pour forcer les extraits bruts à `0` LLM externe). Vous pouvez lui demander des analyses croisées complexes :
> *"Analyse l'impact d'un changement de batterie sur les moteurs RS-04 en utilisant le RAG."*

---

## 🛠️ Maintenance du Serveur MCP
Le serveur est situé ici : `Code/rag/mcp_lightrag_server.py`.
Si vous modifiez le code du serveur, n'oubliez pas de le **redémarrer** dans les réglages de votre client MCP.

### Fonctionnalités incluses :
- **Recherche Hybride sans LLM (`--search-only` / `llm_mode="antigravity"`)** : Combine graphe (via mots-clés lexicaux `hl_keywords`/`ll_keywords`) et vecteurs sans charger de LLM en RAM.
- **Reranking Automatique** : Trie les résultats par pertinence réelle (`BAAI/bge-reranker-base`).
- **Cascade & Fallback Résilients à Deux Vitesses** : Si le graphe ne trouve rien, bascule automatiquement en mode `naive`. En mode `auto` :
  - **Indexation** (`index_docs.py`, `rag_index_document`, `0` crédit par défaut) : **`8` modèles Gemini non-lite** -> **`Ollama qwen3.8:27b-mlx`** (voir [STUDY_Benchmarks_Indexation_RAG_20261121.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/STUDY_Benchmarks_Indexation_RAG_20261121.md)).
  - **QA rapide & Audit rapide** (`ask_rag.py`, `check_integrity.py`, `rag_search`, `rag_analyze_impact`, `rag_audit_integrity` en `llm_mode="auto"` par défaut) : **cascade courte `3` modèles Gemini `-lite`** (`3.1-flash-lite` -> `3.5-flash-lite` -> `flash-lite-latest`) -> **`1min.ai` (`mistral-small-2603`)** -> **`Ollama gemma4:26b`** (sinon `qwen3.8:27b-mlx` -> Unsloth -> OpenRouter, et repli `antigravity` si tous HS).
- **Traçabilité systématique (`Trace Moteur RAG`)** : chaque réponse Python et MCP indique le modèle exact utilisé (et les bascules éventuelles).
- **Accès SVG XML & PDF garanti** : `.svg` et `.pdf` ne sont pas filtrés par `RAG_SKIP_IMAGES`.

---

## 📁 Dossiers Clés
- **Base de données** : `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db/`
- **Code source** : `/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/`
- **Logs d'indexation** : `/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/rag_indexing.log` (et `~/.ollama/logs/server.log` pour Ollama).
