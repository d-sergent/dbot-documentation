---
name: dbot-rag-agent-index
description: >-
  Indexe la documentation et les schémas/images D-Bot dans LightRAG directement
  via Antigravity (0 LLM tiers, 0 crédit 1min.ai, 0 RAM Ollama), avec niveau de
  thinking adapté par document/chunk (flash standard, inherit critique, jamais extra_high).
---

# Indexation RAG D-Bot par l'Agent Antigravity (`0` LLM tiers)

Utiliser cette compétence lorsque l'utilisateur demande d'indexer ou mettre à jour des fichiers dans `lightrag_dbot_db` **sans recourir aux LLMs tiers** (`Gemini`, `1min.ai`, `OpenRouter`, `Ollama`), ou via les outils MCP `rag_prepare_agent_index` / `rag_commit_agent_index`.

## 1. Politique de Thinking Adapté (Jamais `extra_high`)

- **Profil par défaut : `effort_profile="balanced"`** :
  - **Chunks standards (`~80 %` du corpus : Markdown courant, Python, SVG XML)** : assignés au palier **`flash` (`effort="low"`)**. Extraction directe en une passe, sans méta-réflexion. *Ne jamais utiliser `flash_lite` (perte mesurée de `-77 %` à `-89 %` des arêtes sur notices PDF).*
  - **Chunks critiques (`FINAL_`, `DOSSIER_TECHNIQUE_`, `STUDY_`, `GUIDE_COMPLET_`, tableaux denses `>= 4` lignes, PDF Docling, images CAO/FEA)** : assignés au palier **`inherit` (`effort="medium"`)** pour préserver toutes cotes, tolérances et références McMaster-Carr, **sans jamais activer `extra_high`**.
- **Profil `fast`** : force `flash` (`minimal/low`) sur tout le lot.
- **Profil `thorough`** : force `inherit` (`medium` borné, 1 passe concise, toujours sans `extra_high`).

## 2. Procédure en 3 Étapes (MCP ou CLI)

### Étape 1 — Préparer le lot (`0` LLM)
Appeler l'outil MCP `rag_prepare_agent_index` (ou CLI `index_docs.py --prepare-agent`) :
- Paramètres : `files` (optionnel, ex. `["01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md"]` ; omis pour scanner uniquement les fichiers modifiés/nouveaux) et `effort_profile="balanced"`.
- Récupérer `job_id`, `manifest_path`, `extractions_path`, la liste `images` éventuelle et les `chunks` (`chunk_hash`, `recommended_subagent_model`, `content`).

### Étape 2 — Extraire le graphe (et VLM si images) en respectant le palier
1. **Images raster (`.png`, `.jpg`, `.webp`)** : lire chaque image avec `read_file`, rédiger une description technique factuelle concise (`300–800` tokens, sans symbole dollar ni LaTeX) dans `vlm_descriptions[rel_path]`, puis générer ses tuples dans `vlm_extractions[rel_path]`.
2. **Chunks texte** :
   - **Petit lot (`<= 12` chunks)** : produire directement en 1 passe dans `chunk_extractions[chunk_hash]` (ou inline).
   - **Lot moyen/grand (`> 12` chunks, hors `--full` massif)** : déléguer les chunks `flash` en parallèle via `run_workflow` / `invoke_subagent(..., Model="flash")` et traiter les chunks `inherit` au palier principal/sous-agent `inherit` (zéro sur-réflexion `extra_high`).
3. **Format strict LightRAG** pour chaque chunk :
   - `entity<|#|>entity_name<|#|>entity_type<|#|>entity_description` (`4` champs exacts, noms canoniques D-Bot `RB8016`, `RS-04`, `PA12-CF`, sans CamelCase fantaisie ni troncature)
   - `relation<|#|>source_entity<|#|>target_entity<|#|>keywords_virgules<|#|>relationship_description` (`5` champs exacts, sans utiliser `<|#|>` dans les mots-clés)
   - Dernière ligne obligatoire : `<|COMPLETE|>`
   - **Zéro symbole dollar et zéro LaTeX.**

### Étape 3 — Valider et Committer dans LightRAG (`< 2 s`)
Appeler l'outil MCP `rag_commit_agent_index` (avec `job_id` et `extractions` inline ou `extractions_path`) ou exécuter `index_docs.py --commit-agent <job_id>` :
- Le linter valide `100 %` des `chunk_hash`, l'arité `<|#|>`, `<|COMPLETE|>` et le SHA-256 source avant toute écriture.
- LightRAG exécute son vrai `ainsert()` (purge ancienne version, embeddings FastEmbed, graphes, `full_entities`, `full_relations`, `indexed_files.json`) avec `0` appel LLM tiers (`ReplayAgentLLM` + résumeur dédupliquant déterministe sur fusions `>= force_llm_summary_on_merge`).
