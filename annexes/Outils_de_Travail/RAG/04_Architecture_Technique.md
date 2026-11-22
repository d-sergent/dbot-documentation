# 🏗️ Architecture Technique du D-Bot RAG

Ce document détaille le fonctionnement "sous le capot" du système pour assurer sa pérennité technique.

---

## 🏗️ Pourquoi cette Architecture ?

### Le problème du RAG classique pour D-Bot
Un RAG vectoriel classique (Qdrant ou LanceDB seul) répond bien à "qu'est-ce que dit la doc sur les bras ?", mais est **aveugle aux relations de cause à effet** entre documents différents. Si votre fichier `27_Etude_Epaule_Architecture.md` indique une masse de bras de 1.2 kg, et que `15d_Genou_et_Course.md` décrit les exigences de couple pour courir, un RAG classique ne fera jamais le lien entre ces deux informations.

### La solution : LightRAG (Graph RAG)
LightRAG combine deux types de mémoire :
1. **Vectorielle** : Recherche par similarité sémantique.
2. **Graphe de connaissances** : Relations entité → entité.

Lors de l'indexation, le système extrait des **entités** (composants, masses, couples, vitesses...) et leurs **relations** (impacte, limite, requiert, détermine...). Ces relations sont stockées dans un graphe qui permet des analyses d'impact croisées.

```
Exemple de graphe extrait de votre documentation :

[Bras Robot] ──pèse──> [1.2 kg]
[Masse Bras]  ──contribue_à──> [Masse Totale Robot]
[Masse Totale]──détermine──> [Couple Requis Cheville]
[Couple Requis]──limite──> [Vitesse de Course Max]
[Vitesse Course]──contraint──> [Moteur Genou RS06]
```

---

## 🧩 Les 3 couches de recherche

Le système utilise une architecture dite **"Pipeline de Recherche Avancé"** en 3 étapes :

1.  **Couche Sémantique (Vecteurs)** : 
    - Utilise `intfloat/multilingual-e5-large`.
    - Trouve les passages qui partagent le même sens que la question.
    - Très robuste aux fautes de frappe ou aux synonymes.

2.  **Couche Structurelle (Graphe de Connaissances)** :
    - Utilise les relations `ENTITY -> RELATION -> ENTITY` extraites par le LLM.
    - Permet de relier des informations entre deux fichiers différents (ex: relier un moteur dans la liste d'achats à sa performance dans l'analyse biomécanique).

3.  **Couche de Raffinement (Reranking Local)** :
    - Utilise `BAAI/bge-reranker-base` via `fastembed` (`TextCrossEncoder`).
    - Trie localement les résultats pour s'assurer que les documents avec les scores sigmoïdes les plus hauts sont remontés en tête.

---

## 🛠️ Le Serveur MCP (`mcp_lightrag_server.py`) & CLI (`ask_rag.py`)

C'est le "pont" entre le RAG et vos interfaces (Antigravity, Kilo Code, Unsloth Studio, CLI shell).

### Caractéristiques de l'implémentation :
- **Mode Context-Only & Routage Hybride à Deux Vitesses (`Index` vs `QA/Audit`)** : Avec `--search-only` (CLI) ou `llm_mode='antigravity'` (MCP explicite), l'extracteur lexical déterministe (`rag_runtime.extract_lexical_keywords`) injecte `hl_keywords` et `ll_keywords` pour interroger le graphe sans appel LLM (`0 Go` RAM GPU). En mode par défaut (`--provider auto` et MCP `llm_mode='auto'`) :
  - **Indexation** (`index_docs.py`, `rag_index_document`) : **`8` modèles Gemini Free Tier non-lite** -> **`Ollama qwen3.8:27b-mlx`** (`0` crédit `1min.ai`).
  - **QA rapide & Audit rapide** (`ask_rag.py`, `check_integrity.py`, `rag_search`, `rag_analyze_impact`, `rag_audit_integrity`) : **cascade courte Gemini `-lite`** (`3.1-flash-lite` -> `3.5-flash-lite` -> `flash-lite-latest`, `timeout >= 10 s`, retry sans `thinking_config`) -> **`1min.ai` (`mistral-small-2603`)** -> **`Ollama gemma4:26b`** (sinon `qwen3.8:27b-mlx` / Unsloth / OpenRouter, puis repli `antigravity` sous MCP `auto`).
- **Indexation Directe par Agent Antigravity (`rag_prepare_agent_index` + `rag_commit_agent_index` / `agent_indexing.py`)** : permet à Antigravity d'indexer sans appel LLM tiers (`0` Gemini, `0` `1min.ai`, `0` Ollama) en 3 temps : découpage exact Tiktoken (`1600/150`) + routage de thinking (`effort_profile="balanced"` : `flash` sur texte courant, `inherit` sur Niveau 1 / PDF / images VLM, **jamais `extra_high`**), extraction canonique `<|#|>...<|COMPLETE|>` (et lecture visuelle directe des `.png`/`.jpg`), puis linter bloquant et replay déterministe (`ReplayAgentLLM` + résumeur dédupliquant sans LLM) dans le vrai `LightRAG.ainsert()`.
- **Traçabilité `ModelExecutionTracker`** : Chaque retour Python (`ask_rag.py`, `check_integrity.py`, `index_docs.py`) et MCP (`Trace Moteur RAG`) affiche explicitement le fournisseur, le modèle exact utilisé et les bascules éventuelles.
- **Async/Sync Parity** : Le moteur d'embedding est forcé en `async` pour garantir la compatibilité avec la boucle d'événements de LightRAG 1.4+.
- **Failsafe (Mode Naive)** : Si la recherche graphe (`hybrid`/`local`/`global`) échoue ou ne remonte aucun extrait, le moteur bascule automatiquement en recherche vectorielle `naive` + reranking (code de sortie `0`).
- **Filtrage sélectif `RAG_SKIP_IMAGES`** : Ne filtre que les images raster (`IMAGE_EXTS`), sans jamais masquer les schémas `.svg` XML ni les manuels `.pdf`.

---

## 📊 Performance et Matériel
- **CPU** : L'embedding (`intfloat/multilingual-e5-large`) et le Reranking (`BAAI/bge-reranker-base`) tournent localement sur Apple Silicon (`~1 s` en `--search-only`).
- **GPU Unifié (Ollama MLX)** :
  - Indexation graphe & Vision (`OLLAMA_MODEL`) : **`qwen3.8:27b-mlx`** (`18 Go` disque, `22,93 GiB` VRAM, `think=False`, `num_ctx=16384`), seul modèle local garantissant `0` erreur de délimiteur `<|#|>` LightRAG.
  - QA & Audit rapides (`OLLAMA_QA_MODEL` / `OLLAMA_AUDIT_MODEL`) : **`gemma4:26b`** (`16 Go` disque, `18,28 GiB` VRAM, `1,12 s` moy., `0,43 s` TTFT, `2,55×` plus rapide que `qwen3.8:27b-mlx`, avec repli sur `qwen3.8:27b-mlx` s'il est absent). Démarré uniquement en cas de repli cloud et déchargé (`keep_alive=0`) en fin de session gérée.
- **RAM Graphe** : Le graphe en mémoire consomme environ 500 Mo à 1 Go selon la taille de la base.

---

## 📝 Capacités Multimodales & Évolutions
- **Vision Images Raster (Implémentée)** : Analyse technique des `.png`, `.jpg`, `.jpeg`, `.webp` par VLM (cascade Gemini VLM `GEMINI_VLM_CASCADE` puis repli local Ollama `qwen3.8:27b-mlx`) dans `index_docs.py` et `rag_index_document`.
- **Schémas Vectoriels `.svg` (Implémentée)** : Extraction XML structurée sécurisée (`defusedxml`) des balises `<title>`, `<desc>`, `<text>` et `<tspan>` groupées par panneau `<g>`, ignorant `<defs>`, `<style>` et géométrie brute.
- **Purge & Intégrité du Graphe (Implémentée)** : Suppression synchronisée des reliquats archivés/supprimés avec protection contre les collisions d'homonymes (`README.md`, `__init__.py`) et identifiant canonique `doc-<md5>`.
- **SEA (Stiffness) Integration** : Piste future pour enrichir le graphe sur les calculs de torsion SEA.
