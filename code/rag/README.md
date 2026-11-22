# 📚 rag — Moteur RAG Documentaire Local (LightRAG + FastEmbed)

Ce sous-module gère le système RAG (Retrieval-Augmented Generation) du projet D-Bot. Il permet d'indexer l'ensemble de la documentation technique et de fournir un accès sémantique instantané (< 15 ms).

---

## 📄 Fichiers & Rôles

| Fichier | Rôle & Description |
| :--- | :--- |
| **[`rag_cli.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/rag_cli.py)** | Client MCP CLI pour le RAG D-Bot — lance le serveur MCP `dbot-rag` en mode `--llm-mode auto` par défaut (`Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b` avec repli Antigravity ; `--provider` / `--model` transmis à tous les outils).<br>`rag "moteur RS04 spécifications"` (ou `/opt/homebrew/bin/rag "votre recherche"`) |
| **[`ask_rag.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/ask_rag.py)** | Script de recherche et QA directe (sans MCP). En `--provider auto` (défaut) : **cascade courte `Gemini -lite` -> `1min.ai` (`mistral-small-2603`) -> `Ollama gemma4:26b`** (sinon `qwen3.8:27b-mlx` -> Unsloth -> OpenRouter) ; en `--search-only` : `0` appel LLM.<br>`/opt/homebrew/bin/python3.11 Code/rag/ask_rag.py --search-only --mode hybrid "<votre recherche>"` |
| **[`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py)** | Script de ré-indexation incrémentale par section et complète (Markdown, Code, PDF Docling caché, `.svg` XML, images VLM). Pipeline 3 phases (VLM -> sections/lots -> purge), `--summary-mode deterministic` (défaut, `force_llm_summary_on_merge=24`), `--gleaning-mode adaptive` (défaut : `1` critiques/PDF/SVG, `0` standard), `--batch-size 8`, `--no-section-split`, `--mirror-backup`. En `--provider auto` (`0` crédit payant) : **Gemini Free Tier non-lite -> Ollama `qwen3.8:27b-mlx`** (`think=False`) ; mode direct sans LLM tiers via **`--prepare-agent` / `--commit-agent`** ([`agent_indexing.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/agent_indexing.py)).<br>`/opt/homebrew/bin/python3.11 Code/rag/index_docs.py --update --provider auto` |
| **[`rag_chunking.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/rag_chunking.py)** | Module partagé de découpage et filtrage : chunking Markdown ancré `##` / `###` (*fence-safe* et répétant les en-têtes de tableaux), sections virtuelles `##` (`>= 24 Ko` et `>= 3` H2), SHA-256 normalisé (ignore espaces/CRLF/`## Sommaire`), exclusions corpus (`Code/rag/*.py`, `*test*.py`, `tests/` tout en conservant `Code/rag/README.md`), politique `resolve_gleaning_for_doc` et cache disque PDF `.docling_cache/`. |
| **[`repair_db_sync.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/repair_db_sync.py)** | Outil de maintenance, hygiène et compaction (`0` LLM) sous `IndexingFileLock` : purge des fichiers exclus (`--purge-excluded`), déduplication (`--dedupe-docs`) incluant réparation `unknown_source` via en-tête `Fichier:`, compaction des entrées `llm_response_cache` orphelines (`--compact-cache`), synchronisation `GraphML`/`NanoVectorDB` (`--full-hygiene`) et miroir `rsync` vers Google Drive (`--sync-mirror`). |
| **[`check_integrity.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/check_integrity.py)** | Audit d'intégrité Graph-RAG autonome générant `AUDIT_INTEGRITE.md` et `AUDIT_QUESTION_REPONSE.json`. En `--provider auto` (défaut) : **cascade courte `Gemini -lite` -> `1min.ai` (`mistral-small-2603`) -> `Ollama gemma4:26b`** (sinon `qwen3.8:27b-mlx` -> Unsloth -> OpenRouter). |
| **[`rag_quality_audit.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/rag_quality_audit.py)** | Moteur d'audit qualité 100 % lecture seule (`0` LLM) : score `0–100` par fichier, détection chunking `1200/100`, sous-extraction, rétention cotes/McMaster-Carr, ancrage lexical, santé GraphML et export HTML autonome (`--html`). Utilisable même pendant une indexation active. |
| **[`rag_monitor_ui.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/rag_monitor_ui.py)** | Cockpit web local `FastAPI` (`http://127.0.0.1:8765`) : suivi live des lots/fusions, état stockage SSD local vs miroir Drive + action `--full-hygiene --sync-mirror`, matrice avec badges sections `##` & gleaning (`G1`/`G0`), sélecteurs V2 (`auto`/`ollama`/`gemini`/`1minai`, `--summary-mode`, `--gleaning-mode`, `--batch-size`), inspecteur par section, test Retrieval/Benchmark `120` sans LLM et protection `IndexingFileLock` (`HTTP 409`). |
| **[`mcp_lightrag_server.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/mcp_lightrag_server.py)** | Serveur MCP exposant `9` outils (`rag_search`, `rag_get_context`, `rag_analyze_impact`, `rag_list_topics`, `rag_audit_integrity`, `rag_resolve_audit`, `rag_index_document`, **`rag_prepare_agent_index`**, **`rag_commit_agent_index`**) en **`llm_mode="auto"` par défaut** et **trace explicite (`Trace Moteur RAG`)**. |

---

## ⚡ Recherche, Indexation & Contrôle d'Intégrité via le RAG D-Bot (MCP)

```bash
# Recherche un sujet précis (mode local/naive — retrieval pur, pas de LLM requis)
rag "moteur d'épaule RS04 spécifications"

# Recherche sémantique hybride (défaut --llm-mode auto : Gemini -lite -> 1min.ai -> gemma4:26b, repli Antigravity)
rag --search "stratégie de bus CAN-FD"

# Indexation au fil de l'eau d'un document modifié (auto = Gemini non-lite puis repli Ollama qwen3.8:27b-mlx)
rag --index "01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md"
rag --index "01_Mecanique_et_Chassis/Torse_et_Bassin/media/solution_c_bride_monobloc_7075_et_vis_traversantes.svg" --provider ollama

# Analyse d'impact systémique (défaut auto, ou --llm-mode antigravity pour extraits bruts sans LLM)
rag --impact "hausse de masse du torse sur la course de l'épaule"
rag --impact "hausse de masse du torse" --llm-mode antigravity

# Liste des thématiques indexées
rag --topics "moteurs"

# Audit d'intégrité rapide (défaut --llm-mode auto : Gemini -lite -> 1min.ai mistral-small-2603 -> gemma4:26b)
rag --audit cinematique_moteurs

# Audit d'intégrité strict en délégation IDE (--llm-mode antigravity, 0 LLM externe)
rag --audit cinematique_moteurs --llm-mode antigravity

# Audit d'intégrité global (tous les domaines)
rag --audit

# Résolution des contradictions et génération du plan de correction (PLAN_CORRECTION.md)
rag --resolve --from-json

# Ré-indexation incrémentale par défaut (--update --provider auto, diff par section, summary deterministic, lots de 8)
/opt/homebrew/bin/python3.11 Code/rag/index_docs.py --update --provider auto --summary-mode deterministic --batch-size 8 --mirror-backup

# Hygiène complète & compaction de la base SSD locale (déduplication, purge exclus, cache LLM, 0 LLM)
/opt/homebrew/bin/python3.11 Code/rag/repair_db_sync.py --full-hygiene --apply --sync-mirror

# Ré-indexation incrémentale 100 % locale sur Mac via Ollama (texte + SVG XML + images VLM)
/opt/homebrew/bin/python3.11 Code/rag/index_docs.py --update --provider ollama

# Ré-indexation incrémentale via cascade Gemini seule
/opt/homebrew/bin/python3.11 Code/rag/index_docs.py --update --provider gemini --thinking-level low

# Optionnel : forcer le mode multi-modèles gratuits (Online / OpenRouter)
/opt/homebrew/bin/python3.11 Code/rag/index_docs.py --update --provider online

# Cockpit Web local de monitoring qualité RAG (http://127.0.0.1:8765 — lecture seule sûre pendant indexation)
/opt/homebrew/bin/python3.11 Code/rag/rag_monitor_ui.py --port 8765

# Audit qualité CLI (0 LLM) ou export rapport HTML statique autonome
/opt/homebrew/bin/python3.11 Code/rag/rag_quality_audit.py --top 25
/opt/homebrew/bin/python3.11 Code/rag/rag_quality_audit.py --html /tmp/dbot_rag_health.html
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
3. **Retournant les extraits** indexés depuis la base LightRAG locale SSD (`/Users/Shared/dbot_rag_local/lightrag_dbot_db`, avec miroir de sauvegarde explicite sur Google Drive via `--mirror-backup` ou `--sync-mirror`)

Le serveur MCP et `ask_rag.py --search-only` injectent des mots-cles lexicaux (`hl_keywords`/`ll_keywords`) et appliquent un **repli automatique** en mode `naive` (retrieval pur, vectoriel + reranking) si aucun serveur LLM local (Ollama / Unsloth) n'est actif -> zero dependance LLM et 0 Go de RAM GPU pour les recherches documentaires.

### ⚡ Stockage SSD Local, Indexation par Section & Optimisations Pipeline

- **Base active sur SSD local (`/Users/Shared/dbot_rag_local/lightrag_dbot_db`)** : élimine la latence I/O et les verrous du File Provider Google Drive pendant les réécritures JSON/GraphML/NanoVectorDB. Le dossier `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db` est conservé comme miroir de sauvegarde (`rsync` atomique via `--mirror-backup` ou `repair_db_sync.py --sync-mirror`).
- **Indexation incrémentale par section (`##`) & chunking ancré Markdown** (`rag_chunking.py`) : les fichiers Markdown volumineux (`>= 24 Ko` et `>= 3` titres `##`) sont découpés en sections virtuelles indépendantes. Modifier une seule section ne ré-indexe que son `doc_id`, sans invalider les autres sections. Le chunker `chunking_markdown_anchored` s'aligne sur `##`/`###`, respecte les blocs de code et répète l'en-tête sur les grands tableaux découpés.
- **Empreinte SHA-256 normalisée** : ignore les variations de fin de ligne CRLF, espaces en fin de ligne et éditions pures de `## Sommaire` (`0` appel LLM lorsqu'aucun contenu technique n'a changé).
- **Fusions déterministes, gleaning adaptatif & insertion par lots** : `force_llm_summary_on_merge=24`, résumés de fusion gérés par `--summary-mode deterministic` par défaut (options `gemma4` ou `llm`), gleaning adaptatif `--gleaning-mode adaptive` (`1` passe de rattrapage sur critiques/`SYNTHESE_METROLOGIQUE_`/PDF/SVG, `0` sur fichiers standard), insertion groupée `--batch-size 8`, ordonnancement 3 phases (VLM images regroupées d'abord pour préserver le KV prefix cache -> sections/textes -> purge groupée -> `ainsert` par lots) et cache disque PDF `.docling_cache/`.
- **Hygiène du corpus** : exclusion automatique de la plomberie RAG (`Code/rag/*.py`) et des tests (`*test*.py`, `tests/`), tout en conservant `Code/rag/README.md`.

### Modes de recherche & Contrôle Qualité

| Mode | Outil MCP | LLM requis | Usage |
|---|---|---|---|
| Contexte précis | `rag_get_context` (local) | Non (fallback naive) | Spécifications, valeurs numériques |
| Recherche sémantique | `rag_search` (hybrid) | Oui si synthèse demandée | Questions générales |
| Analyse d'impact | `rag_analyze_impact` (global) | Oui (`internal` / Antigravity) | Cause -> effet entre composants |
| Liste thématiques | `rag_list_topics` (naive) | Non | Explorer les sujets indexés |
| Audit d'intégrité | `rag_audit_integrity` (global) | Non avec `llm_mode='antigravity'` (utilise abonnement IDE) / Oui si `'internal'` | Détection des contradictions et désynchronisations |
| Résolution d'audit | `rag_resolve_audit` (naive/local) | Non (retrieval pur) | Localisation des fichiers contradictoires & plan de correction |
| Indexation au fil de l'eau | `rag_index_document` (insertion) | Oui (`auto` = Gemini non-lite -> Ollama `qwen3.8:27b-mlx`, `0` crédit ; ou `1minai` explicite) | Mise à jour immédiate d'un document modifié (`.md`, `.py`, `.pdf`, `.svg` XML, images) |
| Indexation directe Antigravity (`0` LLM tiers) | `rag_prepare_agent_index` + `rag_commit_agent_index` | Non (piloté par l'agent hôte avec `effort_profile="balanced"` : `flash` standard / `inherit` critique, jamais `extra_high`) | Indexation incrémentale ou ciblée haute qualité sur abonnement Antigravity (texte, PDF, `.svg`, VLM) |

### 🧭 Stratégie de Routage à Deux Vitesses (`Indexation Qualité` vs `QA & Audit Rapides`)

Le pipeline distingue strictement **l'indexation graphe** (`0` crédit payant, qualité maximale hors `-lite`) des **requêtes & audits rapides** (`Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b`, configuré en `--provider auto` côté Python et `llm_mode="auto"` par défaut côté MCP) :

| Outil / Tâche RAG | Cascade Gemini Free Tier (Palier 1) | Passerelle `1min.ai` (Palier 2) | Repli Local Optimal (Palier 3) | Mode `antigravity` (`0` LLM) |
| :--- | :--- | :--- | :--- | :--- |
| **Indexation graphe & VLM** (`index_docs.py`, `rag_index_document`) | **Cascade qualité strictement non-lite (`8` modèles texte / `6` VLM)** :<br>`gemini-3.8-flash` -> `gemini-4-hydrogen` -> `gemini-3.6-flash` -> `gemini-3-flash-preview` -> `gemini-flash-latest` -> `gemini-2.5-flash` -> `gemini-3.7-flash` -> `gemini-3.5-flash` *(sans `-lite`)* | **Désactivée par défaut** (`0` crédit en `auto`). Activable sur demande (`--with-1minai` / `--provider 1minai`, défaut **`mistral-small-latest`** à `0,480 cr/tok`) | **Ollama `qwen3.8:27b-mlx`** (`think=False`, démarré à la demande ; **jamais** `gemma4:26b` en indexation) | — |
| **QA rapide, Impact & Audit rapide** (`ask_rag.py`, `check_integrity.py`, `rag_search`, `rag_analyze_impact`, `rag_audit_integrity`) | **Cascade courte `-lite` seule (`3` modèles)** :<br>`gemini-3.1-flash-lite` -> `gemini-3.5-flash-lite` -> `gemini-flash-lite-latest` *(timeout `15 s`)* | **Actif par défaut en palier 2 (`auto`)** :<br>**`mistral-small-2603`** (`ONEMINAI_QA_MODEL` / `ONEMINAI_AUDIT_MODEL`, **`4,69 s` moy.**, `100 %` QA faisables & Audits `40 Ko+`) | **Ollama `gemma4:26b`** (`OLLAMA_QA_MODEL`, **`1,12 s` moy.**, repli `qwen3.8:27b-mlx` si absent) -> Unsloth `:8888` -> OpenRouter | `--search-only` ou `llm_mode="antigravity"` explicite (et repli auto si tous LLM HS sous `llm_mode="auto"`) |

- **Compatibilité `thinking_config` & Timeout `>= 10 s`** : la session Gemini (`rag_runtime.GeminiCascadeSession`) borne strictement chaque requête à `>= 10 s` (évite tout gel de `20 min` en pic `503`) et retente automatiquement sans `thinking_config` si un modèle léger de `GEMINI_QA_CASCADE` rejette `thinking_budget=0` (`400 INVALID_ARGUMENT` observé sur `gemini-3.5-flash-lite` et `gemini-flash-lite-latest`).
- **Traces systématiques** :
  - **Python CLI** : affiche `🧭 gemini / <modele> [role=...] | bascules: ...` (ou `ollama / gemma4:26b` / `qwen3.8:27b-mlx`) dans `stderr`, `stdout` (`[Moteur RAG : ...]`), `rag_indexing.log` et `AUDIT_INTEGRITE.md`.
  - **Serveur MCP** : chaque réponse inclut `> **Trace Moteur RAG** : ...` avec le fournisseur, le modèle exact et les éventuelles bascules (`Cache LightRAG` en cas de hit dans `kv_store_llm_response_cache.json`, ou `Aucun LLM — mode antigravity`).

### 🦙 Mode Local Ollama (`--provider ollama` : `qwen3.8:27b-mlx` & `gemma4:26b`)

Pour indexer ou interroger le RAG **100 % hors-ligne sans dépendance aux quotas cloud (`429`/`503`)**, le pipeline pilote **Ollama** (`127.0.0.1:11434`) en sélectionnant automatiquement le bon modèle :

1. **Indexation graphe & Vision technique (`OLLAMA_MODEL`)** : **`qwen3.8:27b-mlx`** (`18 Go`, `22,93 GiB` VRAM). Seul modèle local sans corruption des délimiteurs `<\|#\|>` LightRAG.
2. **Requêtes QA & Audits rapides (`OLLAMA_QA_MODEL` / `OLLAMA_AUDIT_MODEL`)** : **`gemma4:26b`** (`16 Go`, `18,28 GiB` VRAM, `1,12 s` moy. en QA, repli automatique sur `qwen3.8:27b-mlx` s'il n'est pas installé).
3. **Optimisation vitesse & formatage (`/api/chat`)** :
   - Les scripts imposent **`"think": False`**, **`num_ctx = 16384`** (`8192` en vision `OLLAMA_VLM_NUM_CTX`) et parallélisme `max_async = 1`.
4. **Schémas vectoriels `.svg` (Extracteur XML structuré)** :
   - Les `.svg` ne sont pas traités comme des images bitmap : `index_docs.py` et `mcp_lightrag_server.py` extraient via `defusedxml` les balises `<title>`, `<desc>`, `<text>` et `<tspan>` regroupées par `<g>`, tout en ignorant `<defs>`, `<style>`, `<script>` et les tracés géométriques bruts.
   - `mcp_lightrag_server.py` a retiré `.svg` et `.pdf` d'`IMAGE_EXTS` : même avec `RAG_SKIP_IMAGES=true`, les schémas `.svg` et manuels `.pdf` restent toujours interrogeables.

### 🛡️ Cascade Gemini & Mode Économe (`--provider gemini` / `auto`)

Lorsque Gemini est utilisé (`--provider auto` ou `--provider gemini`) :
1. **Cascade qualité d'indexation (`8` modèles non-lite)** (`index_docs.py` / `rag_index_document`) : `gemini-3.8-flash` -> `gemini-4-hydrogen` -> `gemini-3.6-flash` -> `gemini-3-flash-preview` -> `gemini-flash-latest` -> `gemini-2.5-flash` -> `gemini-3.7-flash` -> `gemini-3.5-flash` (hors modèles Paid-only `gemini-4-argon`/`carbon`/`neon`, modèles `404` retirés comme `gemini-2.5-flash-lite`, et variantes `-lite` écartées de l'indexation après mesure d'une chute de `-77 %` à `-89 %` des relations sur manuels jumeaux — conservées uniquement dans `GEMINI_QA_CASCADE` ; voir [STUDY_Benchmarks_Indexation_RAG_20261121.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/STUDY_Benchmarks_Indexation_RAG_20261121.md)).
2. **Niveaux d'effort (*Thinking Level*)** : `--thinking-level minimal` (`0`, bascule sans `thinking_config` si rejeté) ou `low` (`100` tokens, défaut).
3. **Cadencement anti-saturation (`429`)** : en indexation, parallélisme séquentiel (`max_async = 1`) avec pause de `2,5 s` ; en QA interactive (`ask_rag.py` / MCP), bascule instantanée sans attente (`timeout=15 s`).

### 🪙 Passerelle 1min.ai (`ONEMINAI_QA_MODEL` / `ONEMINAI_MODEL` & coupe-circuit auto)

- **Séparation stricte par rôle (`auto`)** :
  - En **indexation** (`index_docs.py` / `rag_index_document`), `--provider auto` **n'utilise jamais `1min.ai`** (`Gemini non-lite -> Ollama qwen3.8:27b-mlx`, `0` crédit payant sauf `--with-1minai` ou `--provider 1minai`, défaut **`mistral-small-latest`** à `0,480 cr/tok`).
  - En **QA rapide & Audit rapide** (`ask_rag.py`, `check_integrity.py`, et outils MCP en `llm_mode="auto"`), **`1min.ai` (`mistral-small-2603`) est activé par défaut en Palier 2** après la cascade courte `Gemini -lite` et avant `Ollama gemma4:26b`, avec extracteur lexical déterministe sur `keyword_extraction` (aucun crédit dépensé pour extraire les mots-clés) et coupe-circuit automatique sur quota `402`/`429`.
- **Endpoint sans état (*stateless*)** : `https://api.1min.ai/openai/v1` (évite l'accumulation d'historique de `/api/features`), avec pré-bridage proactif et adaptation automatique `HTTP 400` : plafond `4096` tokens de sortie sur `mistral-small-latest`, suppression de `temperature` sur les modèles incompatibles (`deepseek-flash`, `gpt-5-nano`, `gpt-5.4-nano`, `gpt-6-luna`, `o1`/`o3`/`o4-mini`) et bascule sur `max_completion_tokens`.
- **Bancs d'essai empiriques complets (`2026-11-21`, détails dans [STUDY_Benchmarks_Indexation_RAG_20261121.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/STUDY_Benchmarks_Indexation_RAG_20261121.md))** :
  - **`mistral-small-2603` (`Mistral Small 4` — défaut `ONEMINAI_QA_MODEL` & `ONEMINAI_AUDIT_MODEL`)** : vainqueur QA & Audit (`4,69 s` moy., `1,33–2,35 s` en QA, **`3/3` QA faisables + `2/2` Audits `36–40 Ko`** sans troncature ni `context_length_exceeded`, `6/6` sans symbole dollar ni LaTeX, ~`2×` plus rapide que `gpt-6-luna`, `qwen3.7-flash` et `gpt-4o-mini` qui échouent respectivement par troncature, erreur factuelle IMU ou référence McMaster erronée).
  - **`mistral-small-latest` (défaut `ONEMINAI_MODEL` en indexation)** : meilleur coût/rappel sur chunks `1600` tok (**`0,480` cr/tok**, `146` nœuds / `158` arêtes / `12/12` cotes), mais fenêtre ~`16K` tokens sur `1min.ai` provoquant `HTTP 400 context_length_exceeded` en Audit — réservé à l'indexation `--provider 1minai`.
  - **`qwen3.7-flash` / `gpt-6-luna` / `gpt-4o-mini`** : surclassés en QA/Audit par `mistral-small-2603` (cf. banc 6 tâches dans `STUDY_Benchmarks_Indexation_RAG_20261121.md`).
- **Diagnostic `0` crédit & Tarifs** : `/opt/homebrew/bin/python3.11 Code/rag/check_1minai.py` liste les `49` modèles actifs sur `/openai/v1/models` (cet endpoint ne renvoie aucun champ tarifaire ; consulter l'*AI Credit Calculator* sur `1min.ai` pour le coût théorique sans appel, et le bilan `in=... tok, out=... tok` d'`index_docs.py --provider 1minai` après essai).

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
| `RAG_DB_PATH` | `/Users/Shared/dbot_rag_local/lightrag_dbot_db` | Chemin de la base LightRAG active sur SSD local (repli automatique sur la base Drive historique si seul ce dernier existe) |
| `RAG_SUMMARY_MODE` | `deterministic` | Stratégie de résumé lors de fusion d'entités/relations (`deterministic` = 0 LLM, `gemma4`, `llm`) |
| `RAG_GLEANING_MODE` | `adaptive` | Passe de gleaning LightRAG (`adaptive` = `1` sur critiques/PDF/SVG et `0` sur standard ; `on` = `1` partout ; `off` = `0` partout) |
| `RAG_FORCE_LLM_SUMMARY_ON_MERGE` | `24` | Seuil LightRAG de fragments décrits avant déclenchement d'un résumé de fusion |
| `RAG_INSERT_BATCH_SIZE` | `8` | Taille de lot pour `rag.ainsert(...)` groupé en phase 3 |
| `RAG_SECTION_SPLIT_MIN_BYTES` | `24576` | Seuil minimal en octets (`24 Ko`) pour activer le découpage en sections virtuelles `##` |
| `RAG_EXCLUDE_TESTS_AND_PLUMBING` | `true` | Exclut `Code/rag/*.py` et `*test*.py` / `tests/` du graphe RAG (conserve `Code/rag/README.md`) |
| `RAG_AUTO_MIRROR_BACKUP` | `false` | Synchronise automatiquement `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db` après une indexation réussie |
| `RAG_SKIP_IMAGES` | `true` | Filtre uniquement les chunks issus d'images raster (`IMAGE_EXTS`, n'exclut ni `.svg` ni `.pdf`) + nettoie `![]()` |
| `RAG_LLM_PROVIDER` | `auto` | Fournisseur du serveur MCP pour `auto`/`internal` (`auto` = Gemini -lite -> 1min.ai -> gemma4:26b en QA/audit ; Gemini non-lite -> qwen3.8:27b-mlx en index) |
| `RAG_AUTO_START_SERVER` | `true` | Démarre `ollama serve` à la demande lors d'un repli local si aucun serveur n'est actif, et l'arrête en fin de session |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | URL racine du démon Ollama local |
| `OLLAMA_MODEL` | `qwen3.8:27b-mlx` | Modèle Ollama utilisé pour l'indexation graphe et la vision (`think=False`), ou en ultime repli si `gemma4:26b` est absent |
| `OLLAMA_QA_MODEL` | `gemma4:26b` | Modèle Ollama rapide par défaut pour **QA ET Audit rapides** (`ask_rag.py`, `check_integrity.py`, `rag_search`, `rag_audit_integrity`, `rag_analyze_impact`) |
| `ONEMINAI_QA_MODEL` / `ONEMINAI_AUDIT_MODEL` | `mistral-small-2603` | Modèle `1min.ai` rapide (Palier 2 QA & Audit en mode `auto`, accepte `40 Ko+` sans limite 16K) |
| `ONEMINAI_MODEL` / `ONEMINAI_BASE_URL` | `mistral-small-latest` / `https://api.1min.ai/openai/v1` | Modèle d'indexation explicite (`--provider 1minai` / `--with-1minai`) et passerelle stateless OpenAI-compat |
| `GEMINI_HTTP_TIMEOUT_S` / `GEMINI_QA_TIMEOUT_S` | `60` / `15` | Timeout HTTP par tentative Gemini (minimum strict `10 s` exigé par Google API) |

> **Note** : `unsloth/Qwen3.8-27B-GGUF` (+ `mmproj-F16.gguf`), `qwen3.8:27b-mlx` et `gemma4:26b` sont des modèles **VLM**. Avec `RAG_SKIP_IMAGES=false`, les chunks images textuels sont inclus tout en nettoyant les liens markdown `![]()`.

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
      "RAG_DB_PATH": "/Users/Shared/dbot_rag_local/lightrag_dbot_db",
      "RAG_LLM_PROVIDER": "auto",
      "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
      "OLLAMA_MODEL": "qwen3.8:27b-mlx",
      "OLLAMA_QA_MODEL": "gemma4:26b",
      "UNSLOTH_BASE_URL": "http://127.0.0.1:8888/v1",
      "UNSLOTH_MODEL": "unsloth/Qwen3.8-27B-GGUF",
      "RAG_SKIP_IMAGES": "false"
    },
    "enabled": true, "timeout": 300000
  }
},
"permission": { "dbot-rag_*": "allow", "dbot_rag_*": "allow" }
```

> Le format a été migré de `experimental.mcpServers` (déprécié) vers la clé `mcp` (standard actuel). Les outils MCP sont en `allow` pour un usage sans prompt d'approbation. Les variables canoniques `UNSLOTH_BASE_URL` / `UNSLOTH_MODEL` / `UNSLOTH_API_KEY` pointent vers Unsloth Studio (`:8888/v1`), tout en conservant la rétrocompatibilité silencieuse avec les anciennes variables `VMLX_*`.
