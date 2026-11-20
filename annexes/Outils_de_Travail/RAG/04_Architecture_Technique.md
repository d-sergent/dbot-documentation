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
- **Mode Context-Only & Synthèse Hybride** : Par défaut (`llm_mode='antigravity'` côté MCP ou `--search-only` côté `ask_rag.py`), l'extracteur lexical déterministe (`rag_runtime.extract_lexical_keywords`) injecte `hl_keywords` et `ll_keywords` pour interroger le graphe sans appel LLM (`0 Go` RAM GPU). En mode `internal` / synthèse : cascade MCP (`Gemini` -> `Ollama qwen3.8:27b-mlx` -> `Unsloth :8888`) ou cascade CLI (`Ollama` -> `Unsloth` -> `Gemini` -> `OpenRouter`), avec démarrage/arrêt automatique d'Ollama à la session si nécessaire.
- **Async/Sync Parity** : Le moteur d'embedding est forcé en `async` pour garantir la compatibilité avec la boucle d'événements de LightRAG 1.4+.
- **Failsafe (Mode Naive)** : Si la recherche graphe (`hybrid`/`local`/`global`) échoue ou ne remonte aucun extrait, le moteur bascule automatiquement en recherche vectorielle `naive` + reranking (code de sortie `0`).
- **Filtrage sélectif `RAG_SKIP_IMAGES`** : Ne filtre que les images raster (`IMAGE_EXTS`), sans jamais masquer les schémas `.svg` XML ni les manuels `.pdf`.

---

## 📊 Performance et Matériel
- **CPU** : L'embedding (`intfloat/multilingual-e5-large`) et le Reranking (`BAAI/bge-reranker-base`) tournent localement sur Apple Silicon (`~1 s` en `--search-only`).
- **GPU Unifié (Ollama MLX)** :
  - Indexation (`--provider ollama`) : `qwen3.5:9b` (`nvfp4`, `think=False`, `num_ctx=16384`) consomme ~11–13,5 GiB sur 64 Go et cohabite avec Fusion 360.
  - Synthèse QA (`--provider ollama` ou `auto`) : `qwen3.8:27b-mlx` (~18–27,6 Go), démarré uniquement si requis et déchargé (`keep_alive=0`) + arrêté en fin de session lorsqu'il a été lancé par le RAG.
- **RAM Graphe** : Le graphe en mémoire consomme environ 500 Mo à 1 Go selon la taille de la base.

---

## 📝 Capacités Multimodales & Évolutions
- **Vision Images Raster (Implémentée)** : Analyse technique des `.png`, `.jpg`, `.jpeg`, `.webp` par VLM (Ollama local `qwen3.5:9b` ou Gemini Flash) dans `index_docs.py` et `rag_index_document`.
- **Schémas Vectoriels `.svg` (Implémentée)** : Extraction XML structurée sécurisée (`defusedxml`) des balises `<title>`, `<desc>`, `<text>` et `<tspan>` groupées par panneau `<g>`, ignorant `<defs>`, `<style>` et géométrie brute.
- **Purge & Intégrité du Graphe (Implémentée)** : Suppression synchronisée des reliquats archivés/supprimés avec protection contre les collisions d'homonymes (`README.md`, `__init__.py`) et identifiant canonique `doc-<md5>`.
- **SEA (Stiffness) Integration** : Piste future pour enrichir le graphe sur les calculs de torsion SEA.
