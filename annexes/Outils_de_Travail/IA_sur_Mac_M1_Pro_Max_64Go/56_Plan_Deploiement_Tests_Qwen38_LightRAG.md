# Plan de Déploiement & Bancs d'Essai — `Qwen3.8-27B`, LightRAG & Écosystème Unsloth (Points 1, 2 et 3)

> **Document de référence D-Bot (`Apple M1 Max 64 Go`)** — Version opérationnelle du `2026-11-14`  
> **Étude amont associée** : [55_Rapport_Expert_Qwen38_Unsloth_M1Max.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/IA_sur_Mac_M1_Pro_Max_64Go/55_Rapport_Expert_Qwen38_Unsloth_M1Max.md)  
> **Règle d'exécution D-Bot** : ce document **planifie et spécifie** les patchs et commandes de test ; aucune modification des scripts [`Code/rag/`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag) ni aucune exécution de [`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py) ne doit être lancée automatiquement sans validation explicite.

> [!IMPORTANT]
> **Architecture du déploiement en 4 phases séquentielles** :
> - **Phase 0 — Pré-requis & Isolation Sandbox** : verrouillage de la base de production `lightrag_dbot_db`, correction de la dérive de ports (`:8006 / :8008 / :8012 / :8080`), préparation des caches et choix des 2 documents étalons.
> - **Phase 1 (Point 1) — Alignement Paramétrique `Qwen3.8` & Chunking** : déploiement des réglages Qwen/Unsloth `Non-Thinking` (`top_p=0.80`, `top_k=20`, `min_p=0.0`, `repeat_penalty=1.0`, `presence_penalty`), séparation Extraction vs Synthèse QA, correction `extra_body` / `max_tokens`, et test `chunk_token_size = 1600 / 1800` avec `gleaning = 1` maintenu.
> - **Phase 2 (Point 2) — Banc d'Essai Concurrence A / B / C** : mesure comparative stricte en environnement vierge entre **Piste A** (`Ollama 0.40.16` MLX parallèle), **Piste B** (`Unsloth Dynamic V3.1 UD-Q4_K_XL` + `MTP` sur `llama-server b10639` `-np 2..3`) et **Piste C** (`vMLX 1.6.19` `--continuous-batching`), avant promotion éventuelle sur les `111` fichiers en file.
> - **Phase 3 (Point 3) — Déploiement Écosystème Unsloth D-Bot** : création d'un banc QA français via Unsloth `Data Recipes` couplé à [`AUDIT_QUESTION_REPONSE.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/AUDIT_QUESTION_REPONSE.json), activation d'agents de code locaux (`unsloth start`, `.kilo/kilo.jsonc`) et audit VLM sur [`Visual_Snapshots`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots).

---

## 📑 Sommaire

- [1. Phase 0 — Pré-requis, isolation sandbox et audit des écarts](#1-phase-0--pré-requis-isolation-sandbox-et-audit-des-écarts)
  - [1.1 Pourquoi ne jamais benchmarker directement sur la base de production](#11-pourquoi-ne-jamais-benchmarker-directement-sur-la-base-de-production)
  - [1.2 Dérives de ports et de modèles détectées dans la stack D-Bot](#12-dérives-de-ports-et-de-modèles-détectées-dans-la-stack-d-bot)
  - [1.3 Sauvegarde et préparation des répertoires sandbox et fichiers étalons](#13-sauvegarde-et-préparation-des-répertoires-sandbox-et-fichiers-étalons)
- [2. Phase 1 (Point 1) — Alignement des paramètres Qwen3.8 et optimisation du chunking](#2-phase-1-point-1--alignement-des-paramètres-qwen38-et-optimisation-du-chunking)
  - [2.1 Matrice exacte des réglages cibles avant et après](#21-matrice-exacte-des-réglages-cibles-avant-et-après)
  - [2.2 Spécifications des modifications Python proposées (avant implémentation)](#22-spécifications-des-modifications-python-proposées-avant-implémentation)
  - [2.3 Protocole de validation unitaire Point 1 et critères Go No-Go](#23-protocole-de-validation-unitaire-point-1-et-critères-go-no-go)
- [3. Phase 2 (Point 2) — Banc d'essai comparatif A B C sur la concurrence](#3-phase-2-point-2--banc-dessai-comparatif-a-b-c-sur-la-concurrence)
  - [3.1 Règles d'équité expérimentale et métriques relevées](#31-règles-déquité-expérimentale-et-métriques-relevées)
  - [3.2 Piste A — Ollama 0.40.16 MLX nvfp4 avec parallélisme activé](#32-piste-a--ollama-04016-mlx-nvfp4-avec-parallélisme-activé)
  - [3.3 Piste B — Unsloth Dynamic V3.1 GGUF et MTP via llama-server b10639](#33-piste-b--unsloth-dynamic-v31-gguf-et-mtp-via-llama-server-b10639)
  - [3.4 Piste C — vMLX 1.6.19 Continuous Batching sur MLX natif](#34-piste-c--vmlx-1619-continuous-batching-sur-mlx-natif)
  - [3.5 Script de dépouillement automatique et grille de décision](#35-script-de-dépouillement-automatique-et-grille-de-décision)
  - [3.6 Résultats mesurés des 6 campagnes sandbox et verdict définitif](#36-résultats-mesurés-des-6-campagnes-sandbox-et-verdict-définitif)
- [4. Phase 3 (Point 3) — Déploiement général d'Unsloth sur le dépôt D-Bot](#4-phase-3-point-3--déploiement-général-dunsloth-sur-le-dépôt-d-bot)
  - [4.1 Chantier 3A — Jeu étalon QA français via Data Recipes et AUDIT_QUESTION_REPONSE](#41-chantier-3a--jeu-étalon-qa-français-via-data-recipes-et-audit_question_reponse)
  - [4.2 Chantier 3B — Agents locaux de code, tool calling auto-réparateur et vision CAO](#42-chantier-3b--agents-locaux-de-code-tool-calling-auto-réparateur-et-vision-cao)
  - [4.3 Chantier 3C — Périmètre fine-tuning et distillation Jetson Orin Nano](#43-chantier-3c--périmètre-fine-tuning-et-distillation-jetson-orin-nano)
  - [4.4 Bilan mesuré de la Phase 3 (Jalon J4)](#44-bilan-mesuré-de-la-phase-3-jalon-j4)
- [5. Phase 4 — Calendrier d'exécution, plan de rollback et contrôle DevSecOps](#5-phase-4--calendrier-dexécution-plan-de-rollback-et-contrôle-devsecops)
  - [5.1 Séquencement recommandé des 4 jalons](#51-séquencement-recommandé-des-4-jalons)
  - [5.2 Procédure de rollback immédiat en cas de régression](#52-procédure-de-rollback-immédiat-en-cas-de-régression)
  - [5.3 Contrôle de sécurité obligatoire post-modification](#53-contrôle-de-sécurité-obligatoire-post-modification)

---

## 1. Phase 0 — Pré-requis, isolation sandbox et audit des écarts

### 1.1 Pourquoi ne jamais benchmarker directement sur la base de production

L'inspection de [`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py#L114-L116) montre que `DB_PATH` est actuellement figé sur `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db` (`535` documents enregistrés, `13 931` entrées de cache LLM, `11 788` nœuds et `16 250` arêtes dans le graphe au démarrage du dernier run).

Lancer les essais **Point 1** ou **Point 2** directement sur ce dossier provoquerait trois biais bloquants :
1. **Pollution par le cache LLM (`kv_store_llm_response_cache.json`)** : LightRAG met en cache chaque requête par empreinte de prompt/modèle/paramètres ou renvoie l'historique existant, ce qui fausse totalement les mesures de vitesse réelle.
2. **Purge destructive partielle** : `index_docs.py` supprime puis reconstruit les entités liées au document traité dans `graph_chunk_entity_relation.graphml`, ce qui modifierait le graphe actif D-Bot à chaque itération de test.
3. **Impossibilité de comparer à périmètre identique** : pour arbitrer objectivement **Ollama** vs **Unsloth Dynamic V3.1** vs **vMLX**, chaque piste doit partir d'un répertoire cible **strictement vierge**.

### 1.2 Dérives de ports et de modèles détectées dans la stack D-Bot

Avant de lancer la Phase 2, l'audit des fichiers de configuration a révélé **quatre valeurs par défaut incohérentes** qui exposeraient les tests `--provider local` et les requêtes QA à des erreurs de connexion ou à une fuite de mode *Thinking* :

| Composant inspecté | Port par défaut (`VMLX_BASE_URL`) | Modèle par défaut | Anomalie critique détectée | Correction d'harmonisation |
| :--- | :--- | :--- | :--- | :--- |
| [`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py#L187-L202) (`--provider local`) | `:8008/v1` | `JANGQ-AI/Qwen3.5-9B-JANG_4S` | Ne transmet pas `extra_body={"chat_template_kwargs": {"enable_thinking": False}}` ; force `max_async=1` (`L964`). | Lire `RAG_DB_PATH` et `LLM_MAX_ASYNC` depuis l'environnement ; injecter `extra_body` et sampling complet sur `local`. |
| [`mcp_lightrag_server.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/mcp_lightrag_server.py#L60-L66) | `:8006/v1` | `JANGQ-AI/Gemma-4-31B-it-JANG_4M` (`OLLAMA_MODEL="qwen3.8:27b-mlx"`) | Passe `max_tokens=2048` par défaut à Ollama (`L418`) et seulement `max_tokens=512` au fallback OpenAI (`L432`) ; aucun `top_p=0.80` ni `presence_penalty`. | Aligner le profil QA (`temp=0.7`, `top_p=0.80`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.0`, `max_tokens=4096`). |
| [`ask_rag.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/ask_rag.py#L23-L25) | `:8080/v1` | `JANGQ-AI/Qwen3.6-35B-A3B-JANGTQ4` | Aucun `--provider ollama` disponible (`local\|openrouter` uniquement) ; filtre `allowed` (`L113`) supprime `top_k`, `presence_penalty` et `extra_body`. | Ajouter `--provider ollama` et autoriser les paramètres d'échantillonnage Qwen3.8 dans `allowed`. |
| [`.kilo/kilo.jsonc`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/.kilo/kilo.jsonc#L51-L69) | `:8012/v1` (`vmlx`) et `:8006/v1` (`vmlx-gemma`) | `Qwen3.6-27B-MLX-8bit` + env `mcp.dbot-rag` sur `:8012` | Le serveur MCP reçoit `VMLX_BASE_URL` `:8012` alors qu'`index_docs.py` vise `:8008`. | Standardiser les ports : `:11434` Ollama, `:8008` vMLX indexation, `:8014` `llama-server` bench, `:8888` Unsloth Studio. |

### 1.3 Sauvegarde et préparation des répertoires sandbox et fichiers étalons

Avant toute opération sur le code ou sur les index :
1. **Sauvegarde froide de la base de production** (hors dossier `Documentation`, sur disque local `/tmp` ou sauvegarde dédiée) :

```bash
cp -a "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db" "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db_backup_20261114"
```

2. **Création des 5 bacs à sable strictement isolés** (Phase 1 chunking + Pistes A, B, C) :

```bash
mkdir -p /tmp/lightrag_bench/p1_c1200 /tmp/lightrag_bench/p1_c1600 /tmp/lightrag_bench/p2_ollama_a /tmp/lightrag_bench/p2_unsloth_b /tmp/lightrag_bench/p2_vmlx_c /tmp/lightrag_bench/reports
```

3. **Jeu de 2 fichiers étalons retenus** (vérifiés dans `01_Mecanique_et_Chassis/Torse_et_Bassin/`) :
   - **Étalon rapide multi-essais (`19 Ko`, ~`3–5` chunks)** : [`STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md) — idéal pour exécuter rapidement `6` passes comparatives (`Pistes A1, A2, B1, B2, C1, C2`) avec une faible variance et des grandeurs physiques chiffrées (`g/cm3`, masses CAO vs FDM).
   - **Étalon dense validation finale (`28 Ko`, ~`5–8` chunks)** : [`STUDY_Calculs_FEA_Bride_Epaule_RS04.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Calculs_FEA_Bride_Epaule_RS04.md) — réservé à la **finale entre les 2 meilleures pistes** pour vérifier la tenue sur tableaux RDM (`85 MPa`, `Sf = 5,92`, géométries `RS-04`).

---

## 2. Phase 1 (Point 1) — Alignement des paramètres `Qwen3.8` et optimisation du chunking

### 2.1 Matrice exacte des réglages cibles avant et après

Cette phase corrige les divergences identifiées dans la section `1.2` du rapport expert entre la calibration officielle [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) / [Unsloth Qwen3.8](https://unsloth.ai/docs/models/qwen3.8) et les scripts actuels :

| Paramètre | Régime 1 : Extraction graphe ([`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py)) | Régime 2 : Synthèse QA ([`mcp_lightrag_server.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/mcp_lightrag_server.py) & [`ask_rag.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/ask_rag.py)) | Valeur actuelle avant patch | Justification technique |
| :--- | :--- | :--- | :--- | :--- |
| **Mode Thinking** | `think=False` / `enable_thinking=False` | `think=False` (défaut rapide) ; option `low/medium` pour requêtes complexes | `think=False` sur Ollama seul (manquant sur `local`) | Supprime les `500–2000` tokens cachés `<think>` sur les extractions simples `<|#|>`. |
| **`temperature`** | **`0.1`** | **`0.7`** | `0.1` partout | Maintient le déterminisme syntaxique à l'extraction, redonne de la fluidité de synthèse en QA. |
| **`top_p`** | **`0.80`** | **`0.80`** | `0.95` (défaut hérité) | Valeur officielle Qwen/Unsloth en mode `Instruct / Non-Thinking`. |
| **`top_k`** | **`20`** | **`20`** | `20` Ollama / `40` `llama.cpp` | Évite les dérives lexicales sous `llama-server` ou `vMLX`. |
| **`min_p`** | **`0.0`** | **`0.0`** | `0` Ollama / `0.05–0.1` `llama.cpp` | Fixation explicite requise : `min_p > 0` dégrade Qwen3.8 selon Unsloth. |
| **`repeat_penalty`** | **`1.0`** | **`1.0`** | `1.0` Ollama / `1.1` `unsloth inference` | Empêche la corruption des identifiants (`91292A118`, `RS-04`, `Torse-123 v42`). |
| **`presence_penalty`** | **`0.3`** | **`1.0`** | `0.0` partout | Coupe les répétitions en queue de description (`0.3` évite tout switch vers l'anglais). |
| **`chunk_token_size`** | **`1600`** (candidat A) puis **`1800`** (candidat B) | s/o | `1200` (défaut LightRAG) | Réduit le nombre de chunks de `~25 %` tout en respectant largement `num_ctx=16384`. |
| **`chunk_overlap_token_size`** | **`150`** | s/o | `100` (défaut LightRAG) | Préserve les entêtes de tableaux CAO/BOM à cheval entre deux chunks. |
| **`entity_extract_max_gleaning`** | **`1`** (inchangé) | s/o | `1` | Indispensable : Pass 2 rapporte `+59 %` d'entités et `+73 %` de relations mesurées. |

### 2.2 Spécifications des modifications Python proposées (avant implémentation)

Les 4 adaptations ciblées ci-dessous doivent être appliquées dans [`Code/rag/`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag) après ton accord, sans changer le comportement par défaut si aucune variable d'environnement de test n'est passée :

1. **Dans [`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py#L114-L246) (`DB_PATH`, `llm_local`, `llm_ollama`, `LightRAG`)** :
   - **Ligne `115`** : permettre la surcharge sandbox sans risque pour la prod :
     - `DB_PATH = Path(os.environ.get("RAG_DB_PATH", "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"))`
   - **Lignes `187-203` (`args.provider == "local"`)** : injecter systématiquement les paramètres Qwen Non-Thinking compatibles OpenAI/vMLX/`llama-server` :
     - `extra_body = kwargs.pop("extra_body", {})` avec `{"chat_template_kwargs": {"enable_thinking": False}, "top_k": 20, "min_p": 0.0, "repeat_penalty": 1.0}`
     - valeurs par défaut explicites : `temperature=kwargs.pop("temperature", 0.1)`, `top_p=kwargs.pop("top_p", 0.80)`, `presence_penalty=kwargs.pop("presence_penalty", 0.3)`
   - **Lignes `222-233` (`args.provider == "ollama"`)** : compléter le dictionnaire `"options"` envoyé à `/api/chat` :
     - ajouter `"top_p": kwargs.get("top_p", 0.80)`, `"top_k": kwargs.get("top_k", 20)`, `"min_p": 0.0`, `"repeat_penalty": 1.0`, `"presence_penalty": kwargs.get("presence_penalty", 0.3)`.
   - **Bloc `run_indexing` / `LightRAG`** : rendre pilotables par environnement la concurrence, `--files` et le chunking :
     - `max_async = max(1, int(os.environ.get("LLM_MAX_ASYNC", "1" if args.provider in ("local", "ollama", "gemini") else "4")))`
     - `chunk_size = int(os.environ.get("CHUNK_SIZE", "1600"))` et `chunk_overlap = int(os.environ.get("CHUNK_OVERLAP_SIZE", "150"))` passés explicitement à `LightRAG(..., chunk_token_size=chunk_size, chunk_overlap_token_size=chunk_overlap, llm_model_max_async=max_async)` (basculé de `1200/100` vers **`1600/150`** après validation des essais J2/J3, avec résolution `--files` relative au `CWD` ou à `DOCS_ROOT` dans [`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py#L563-L591)).

2. **Dans [`mcp_lightrag_server.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/mcp_lightrag_server.py#L331-L438) (`_call_ollama_chat` & `llm_func`)** :
   - Compléter `"options"` dans `_call_ollama_chat` (`L335-340`) avec `"top_p": 0.80`, `"top_k": 20`, `"min_p": 0.0`, `"repeat_penalty": 1.0`, `"presence_penalty": 1.0`.
   - Dans `llm_func` (`L416-438`), passer le défaut de synthèse QA à `temperature=kwargs.get("temperature", 0.7)` et `max_tokens=kwargs.get("max_tokens", 4096)` (au lieu de `0.1` / `2048` sur Ollama et `512` sur le fallback OpenAI).

3. **Dans [`ask_rag.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/ask_rag.py#L98-L159)** :
   - Ajouter le support `--provider ollama` pointant vers `http://127.0.0.1:11434/api/chat` (`think=False`).
   - Étendre `allowed` (`L113`) pour inclure `"top_p"`, `"presence_penalty"`, `"extra_body"` et fixer les défauts QA (`temperature=0.7`, `top_p=0.80`).

### 2.3 Protocole de validation unitaire Point 1 et critères Go No-Go

Les 3 essais suivants s'exécutent sous `Ollama` actuel (`max_async=1`) afin d'isoler **uniquement** l'effet des hyperparamètres et du `chunk_token_size` sur [`STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md) :

1. **Essai 1.0 (Témoin `chunk=1200`, anciens réglages sans `presence_penalty`)** :

```bash
env RAG_DB_PATH="/tmp/lightrag_bench/p1_c1200" CHUNK_SIZE=1200 CHUNK_OVERLAP_SIZE=100 /opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --provider ollama --files "01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md"
```

2. **Essai 1.1 (`chunk=1600`, `overlap=150`, réglages Qwen3.8 alignés)** :

```bash
env RAG_DB_PATH="/tmp/lightrag_bench/p1_c1600" CHUNK_SIZE=1600 CHUNK_OVERLAP_SIZE=150 /opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --provider ollama --files "01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md"
```

3. **Critères Go / No-Go Point 1** (validés avant de passer à la Phase 2) :
   - **Intégrité syntaxique** : `0` avertissement `Complete delimiter can not be found` ni `Recovering mis-prefixed relation` dans la sortie console.
   - **Gain temps attendu** : baisse de `>= 15 %` du temps wall-clock grâce à la réduction du nombre de chunks (`text_chunks.json`).
   - **Qualité graphe & langue** : nombre d'entités uniques dans `kv_store_full_entities.json` supérieur ou égal à `95 %` du témoin `1.0` (`0` régression des grandeurs clés `PA12-CF`, densités `g/cm3`), et description majoritairement en français (`< 5 %` de phrases anglaises parasites). Si `presence_penalty=0.3` provoque des mots anglais, abaisser à `0.15`.
   - *Optionnel si Essai 1.1 concluant* : tester `CHUNK_SIZE=1800` sur un dossier clone `/tmp/lightrag_bench/p1_c1800` pour vérifier s'il reste sous les `8192` tokens de sortie sans troncature.

---

## 3. Phase 2 (Point 2) — Banc d'essai comparatif A B C sur la concurrence

### 3.1 Règles d'équité expérimentale et métriques relevées

L'audit du run `Calculs_FEA` a montré que **`73,9 %` du temps total** vient du décodage séquentiel (`max_async=1`). Pour tester si `max_async = 2` ou `3` apporte un gain réel d'agrégat sur Apple M1 Max (`51,3 GiB` budget GPU), les trois moteurs sont comparés dans des conditions strictement équivalentes :
- **Un seul moteur LLM chargé à la fois** en mémoire unifiée (`64 Go`), pour éviter toute contention de bande passante mémoire (`400 Go/s` sur M1 Max) ou swap SSD.
- **Même `chunk_token_size`** validé en Phase 1 (ex. `1600 / 150`), même fichier étalon initial (`STUDY_Densites_Apparentes...`, `19 Ko`), puis validation finale sur `STUDY_Calculs_FEA_Bride_Epaule_RS04.md` (`28 Ko`).
- **Répertoire sandbox vierge obligatoire** avant chaque run (sinon les appels frappent le cache MD5 LightRAG au lieu de solliciter le moteur).
- **Métriques collectées** : durée wall-clock totale (`s`), nombre de chunks, nombre d'appels LLM, débit cumulé (`tokens générés / durée`), acceptation MTP (`%`), pic RAM moteur (`RSS` en `GiB`), erreurs de format, et nombre d'entités/relations extraites.

### 3.2 Piste A — Ollama 0.40.16 MLX nvfp4 avec parallélisme activé

Ollama est la référence déjà fonctionnelle (`32,3 tok/s`, `68,5 %` MTP). Le test A consiste à vérifier si son runner MLX parallélise réellement `2` requêtes simultanées ou s'il les sérialise en interne :

1. **Redémarrer le serveur Ollama avec `OLLAMA_NUM_PARALLEL=2`** (dans un terminal dédié pour observer le flux en direct, après arrêt de l'instance précédente) :

```bash
pkill -x ollama || true
sleep 2
env OLLAMA_NUM_PARALLEL=2 OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 ollama serve
```

2. **Lancer le benchmark sandbox Piste A (`max_async=2`)** dans un second terminal :

```bash
rm -rf /tmp/lightrag_bench/p2_ollama_a && mkdir -p /tmp/lightrag_bench/p2_ollama_a
env RAG_DB_PATH="/tmp/lightrag_bench/p2_ollama_a" CHUNK_SIZE=1600 CHUNK_OVERLAP_SIZE=150 LLM_MAX_ASYNC=2 /opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --provider ollama --files "01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md"
```

3. **Vérifier dans `~/.ollama/logs/server.log` si `2` requêtes `/api/chat` se chevauchent en temps et vérifier le taux MTP** :

```bash
tail -n 120 /Users/davidsergent/.ollama/logs/server.log | grep -E "GIN|mtp|kv|parallel"
```

### 3.3 Piste B — Unsloth Dynamic V3.1 GGUF et MTP via llama-server b10639

Le cache actuel (`snapshots/4ca720788d1e01f1bff70c033e0d0028fd02e502/`) date du 23 août (`0` tenseur MTP). Pour tester **Dynamic V3.1** dans des conditions loyales avec prédiction multi-tokens :

1. **Télécharger la mise à jour Dynamic V3.1 `UD-Q4_K_XL` (`17,66 Go`), le modèle brouillon `MTP` (`1,37 Go`) et le projecteur vision `mmproj-F16.gguf` (`0,93 Go`)** :

```bash
hf download unsloth/Qwen3.8-27B-GGUF --include "*UD-Q4_K_XL*" "MTP/*" "mmproj-F16.gguf"
```

2. **Repérer le chemin exact des fichiers téléchargés dans le nouveau snapshot HF** :

```bash
ls -lh /Users/davidsergent/.cache/huggingface/hub/models--unsloth--Qwen3.8-27B-GGUF/snapshots/*/ /Users/davidsergent/.cache/huggingface/hub/models--unsloth--Qwen3.8-27B-GGUF/snapshots/*/MTP/
```

3. **Démarrer le serveur Unsloth `llama-server b10639` sur le port `:8014` (`-np 2`, KV `q8_0`, MTP actif, mode Non-Thinking forcé côté serveur et gabarit Jinja)** *(remplacer `<SNAPSHOT_HASH>` par le hash affiché à l'étape 2)* :

```bash
/Users/davidsergent/.unsloth/llama.cpp/llama-server \
  -m "/Users/davidsergent/.cache/huggingface/hub/models--unsloth--Qwen3.8-27B-GGUF/snapshots/<SNAPSHOT_HASH>/Qwen3.8-27B-UD-Q4_K_XL.gguf" \
  -md "/Users/davidsergent/.cache/huggingface/hub/models--unsloth--Qwen3.8-27B-GGUF/snapshots/<SNAPSHOT_HASH>/MTP/mtp-Qwen3.8-27B-Q4_0.gguf" \
  --spec-type draft-mtp \
  --spec-draft-n-max 3 \
  -ngl 99 -ngld 99 \
  -fa on \
  -ctk q8_0 -ctv q8_0 \
  -c 32768 \
  -np 2 \
  --jinja \
  --reasoning off \
  --temp 0.1 --top-p 0.80 --top-k 20 --min-p 0.0 --repeat-penalty 1.0 --presence-penalty 0.3 \
  --host 127.0.0.1 --port 8014
```

*Note de réglage* : avec `-c 32768` et `-np 2`, chaque slot dispose de `16 384` tokens de contexte (cohérent avec `num_ctx=16384` d'Ollama). Si la RAM reste sous `34 GiB`, un second run peut tester `-c 49152 -np 3` + `LLM_MAX_ASYNC=3`.

4. **Test unitaire HTTP `1` appel** (vérifier `0` balise `<think>` et activation effective de `draft-mtp` dans les logs `llama-server`) :

```bash
curl -s http://127.0.0.1:8014/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"qwen3.8-ud-q4_k_xl","messages":[{"role":"user","content":"Cite les trois constantes principales d un calcul FEA en une phrase francaise."}],"temperature":0.1,"max_tokens":128}'
```

5. **Lancer le benchmark sandbox Piste B (`--provider local`, `max_async=2`)** :

```bash
rm -rf /tmp/lightrag_bench/p2_unsloth_b && mkdir -p /tmp/lightrag_bench/p2_unsloth_b
env RAG_DB_PATH="/tmp/lightrag_bench/p2_unsloth_b" CHUNK_SIZE=1600 CHUNK_OVERLAP_SIZE=150 LLM_MAX_ASYNC=2 VMLX_BASE_URL="http://127.0.0.1:8014/v1" /opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --provider local --model "qwen3.8-ud-q4_k_xl" --files "01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md"
```

### 3.4 Piste C — vMLX 1.6.19 Continuous Batching sur MLX natif

Aujourd'hui, aucun checkpoint MLX ou JANG de `Qwen3.8-27B` n'est présent dans `/Users/davidsergent/.cache/huggingface/hub/`. La Piste C nécessite donc au préalable de vérifier si un checkpoint MLX 4-bit `Qwen3.8-27B` (ex. `mlx-community/Qwen3.8-27B-4bit` ou variante JANG publiée sur Hugging Face) est compatible avec le bundle `transformers 5.12.1` / `mlx-lm 0.31.3` de `vMLX.app 1.6.19` (daté du 31 juillet).

1. **Arrêter le serveur Piste B (`llama-server`), puis tester le démarrage `vmlx-engine serve` sur le port `:8008` avec Continuous Batching et Thinking désactivé par défaut** *(remplacer `<REPO_MLX_QWEN38>` par l'identifiant HF MLX validé)* :

```bash
/Applications/vMLX.app/Contents/Resources/bundled-python/python/bin/vmlx-engine serve "<REPO_MLX_QWEN38>" \
  --host 127.0.0.1 \
  --port 8008 \
  --continuous-batching \
  --default-enable-thinking false \
  --reasoning-parser qwen3 \
  --max-tokens 8192 \
  --cache-memory-percent 0.15 \
  --max-cache-blocks 500
```

2. **Test de compatibilité impératif avant benchmark** (vérifier au démarrage dans les logs que `native_mtp` est actif et qu'aucune exception `KeyError: 'qwen3_5'` / erreur template Jinja ne survient) :

```bash
curl -s http://127.0.0.1:8008/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"<REPO_MLX_QWEN38>","messages":[{"role":"user","content":"Reponds uniquement OK si le template Qwen3.8 fonctionne."}],"temperature":0.1,"max_tokens":32,"chat_template_kwargs":{"enable_thinking":false}}'
```

*Règle Go / No-Go immédiate* : si `vmlx-engine serve` échoue au chargement du tokenizer/modèle (version `transformers 5.12.1` antérieure à `Qwen3.8`), **clore la Piste C sans bricoler les paquets internes de `vMLX.app`** et attendre une mise à jour de `vMLX.app`. Sinon, enchaîner sur le run sandbox :

3. **Lancer le benchmark sandbox Piste C (`--provider local`, `max_async=2`, puis `3`)** :

```bash
rm -rf /tmp/lightrag_bench/p2_vmlx_c && mkdir -p /tmp/lightrag_bench/p2_vmlx_c
env RAG_DB_PATH="/tmp/lightrag_bench/p2_vmlx_c" CHUNK_SIZE=1600 CHUNK_OVERLAP_SIZE=150 LLM_MAX_ASYNC=2 VMLX_BASE_URL="http://127.0.0.1:8008/v1" /opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --provider local --model "<REPO_MLX_QWEN38>" --files "01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md"
```

### 3.5 Script de dépouillement automatique et grille de décision

Une fois les runs sandbox terminés, exécuter ce script de lecture pure pour extraire les comptes exacts de chaque répertoire `/tmp/lightrag_bench/*` sans biais d'interprétation :

```bash
/opt/homebrew/bin/python3.11 - << 'EOF'
import json
from pathlib import Path
import xml.etree.ElementTree as ET

base = Path("/tmp/lightrag_bench")
for run_dir in sorted(p for p in base.iterdir() if p.is_dir() and p.name != "reports"):
    chunks_f = run_dir / "kv_store_text_chunks.json"
    ent_f = run_dir / "kv_store_full_entities.json"
    rel_f = run_dir / "kv_store_full_relations.json"
    graph_f = run_dir / "graph_chunk_entity_relation.graphml"
    chunks = len(json.loads(chunks_f.read_text())) if chunks_f.exists() else 0
    ents = sum(len(v.get("entity_names", [])) for v in json.loads(ent_f.read_text()).values()) if ent_f.exists() else 0
    rels = sum(len(v.get("relation_pairs", [])) for v in json.loads(rel_f.read_text()).values()) if rel_f.exists() else 0
    nodes, edges = 0, 0
    if graph_f.exists():
        root = ET.parse(graph_f).getroot()
        ns = {"g": "http://graphml.graphdrawing.org/xmlns"}
        nodes = len(root.findall(".//g:node", ns))
        edges = len(root.findall(".//g:edge", ns))
    print(f"{run_dir.name:15s} | chunks={chunks:2d} | full_ent={ents:3d} | full_rel={rels:3d} | graph_nodes={nodes:3d} | graph_edges={edges:3d}")
EOF
```

**Critères de promotion pour l'indexation des `111` fichiers en attente** :

| Critère | Seuil éliminatoire | Pondération | Piste gagnante sélectionnée si... |
| :--- | :--- | :--- | :--- |
| **Stabilité format `<\|COMPLETE\|>`** | `0` chunk raté / `0` timeout | Bloquante (`100 %` exigé) | Aucun rollback sur fallback structuré |
| **Temps wall-clock réel** | Doit battre le témoin `max_async=1` | `40 %` | Gain `>= 25 %` mesuré à qualité constante (`<= 28 s` amortis/chunk ou `> 42 tok/s` cumulés) |
| **Richesse du graphe (`nodes + edges`)** | `>= 95 %` du témoin Ollama Phase 1 | `40 %` | Conservation complète des valeurs numériques, matériaux et liens `McMaster` |
| **Marge mémoire M1 Max (`64 GiB`)** | Pic RSS moteur `<= 42 GiB` | `20 %` | Laisse `>= 20 GiB` à macOS, IDE et client LightRAG/FastEmbed |

> [!NOTE]
> **Rappel d'architecture sur les `111` fichiers** : si `vMLX` n'est pas encore compatible `Qwen3.8` et que `Ollama` sérialise malgré `OLLAMA_NUM_PARALLEL=2`, alors **Piste B (`llama-server b10639` + `UD-Q4_K_XL Dynamic V3.1` + `MTP`)** devient le candidat principal pour casser `max_async=1`. À qualité/vitesse comparables, revalider obligatoirement sur le 2e fichier étalon [`STUDY_Calculs_FEA_Bride_Epaule_RS04.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Calculs_FEA_Bride_Epaule_RS04.md) avant de lancer manuellement `index_docs.py --update`.

### 3.6 Résultats mesurés des 6 campagnes sandbox et verdict définitif

Les campagnes sandbox menées le `2026-11-14` dans `/tmp/lightrag_bench/*` (base de production intacte) ont départagé de manière expérimentale le chunking Phase 1 et les trois moteurs concurrents Phase 2 :

#### 1. Tableau comparatif consolidé (Phase 1 & Phase 2 — Étalon 1 `19 Ko`, puis Validation finale Étalon 2 `28 Ko`)

| Campagne | Étalon | Moteur & configuration réelle | Durée `real` | Écart vs `p1_c1600` | Chunks / Appels | `<\|COMPLETE\|>` & langue | Nœuds (chiffrés) | Arêtes (chiffrées) | RAM moteur observée | Statut |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`p1_c1200`** | Étalon 1 (`19 Ko`) | Ollama MLX KV `f16`, `async=1`, `1200/100` | `609.38 s` (`101.6 s/chunk`) | `+18.1 %` (`1.18x`) | `6` / `12` | `12/12`, `0` anglais | `99` (`69`) | `147` (`96`) | `23.51 GiB` (pic) | Ancien défaut |
| **`p1_c1600`** | Étalon 1 (`19 Ko`) | **Ollama MLX KV `f16`, `async=1`, `1600/150`** | **`515.78 s` (`103.2 s/chunk`)** | **Réf. (`1.00x`)** | **`5` / `10`** | **`10/10`, `0` anglais** | **`100` (`79`)** | **`135` (`99`)** | **`27.57 GiB` (pic)** | **GAGNANT** |
| **`p2_ollama_a`** | Étalon 1 (`19 Ko`) | Ollama MLX KV `q8_0`, `async=2`, `1600/150` | `504.70 s` (`100.9 s/chunk`) | `-2.1 %` (`0.98x`) | `5` / `10` | `10/10`, `0` anglais | `85` (`61`) | `126` (`86`) | `22.49 GiB` (pic) | **NO-GO** |
| **`p2_unsloth_b`** | Étalon 1 (`19 Ko`) | `llama-server b12340` `UD-Q4_K_XL` + `MTP`, `-cb -np 2` | `620.57 s` (`124.1 s/chunk`) | `+20.3 %` (`1.20x`) | `5` / `10` | `10/10`, `0` anglais | `88` (`62`) | `135` (`95`) | `26.82 GiB` (RSS) | **NO-GO** |
| **`p2_vmlx_c`** | Étalon 1 (`19 Ko`) | `vmlx-engine 1.6.19` `Qwen3.8-27B-4bit`, `async=2`, `--prefill-batch-size 1` | `1 096.76 s` (`219.4 s/chunk`) | `+112.6 %` (`2.13x`) | `5` / `10` | `10/10`, `0` anglais | `97` (`58`) | `134` (`86`) | `17.12 GiB` (RSS) | **NO-GO** |
| **`p1_c1600_fea`** | Étalon 2 (`28 Ko`) | **Ollama MLX KV `f16`, `async=1`, `1600/150`** | **`748.85 s` (`107.0 s/chunk`)** | — (`12 min 29 s`) | **`7` / `14`** | **`14/14`, `0` anglais** | **`121` (`103`*)** | **`157` (`86`*)** | `14.96 GiB` (fin run) | **VALIDÉ (GO)** |
| **`p1_gemma4_c1600`** *(2026-11-21)* | Étalon 1 (`19 Ko`) | Ollama MLX `gemma4:26b` (`A4B`), `async=1`, `1600/150` | `160.0 s` (`32.0 s/chunk`) | `-69.0 %` (`3.22x` plus rapide) | `5` / `10` | `10/10` `<\|COMPLETE\|>`, `0` anglais, **`37` relations `<\|#\|\|>` (`30` warnings `4/5`)** | `69` (`46`*) | `44` (`42`*) | Auto-stop | **NO-GO (Graphe)** |

*\*Note métrologique `p1_c1600_fea` & `p1_gemma4_c1600` : décompte des valeurs numériques effectué strictement sur `entity_id + description / keywords` (hors `source_id`), et relevé RAM `p1_c1600_fea` effectué en fin d'exécution sur le runner `PID 30709`.*

#### 2. Enseignements physiques et causes racines mesurées

1. **Saturation mémoire M1 Max (`64 GiB`, `400 Go/s`) en `LLM_MAX_ASYNC=2`** :
   - **Piste A (`Ollama`, `OLLAMA_NUM_PARALLEL=2`, `KV q8_0`)** : le runner MLX d'Ollama **sérialise en interne** les appels parallèles (gain marginal de `-2.1 %`, `504.70 s` vs `515.78 s`, loin du critère `>= 25 %`), dégrade le hit de cache préfixe (`78.8 % -> 71.0 %`) et fait chuter la richesse du graphe (`100 -> 85` nœuds).
   - **Piste B (`llama-server b12340`, `UD-Q4_K_XL` + `draft-mtp`)** : le parallélisme est réel (`1 146.33 s` cumulés sur `581.45 s` serveur = `1.97x`, `87.5 %` d'acceptation MTP `11 228 / 12 831`), mais la bande passante mémoire divisée entre `2` slots tombe à `16.1 tok/s` par slot (`77.8 tok/s` en prefill), portant le temps total à `620.57 s` (`+20.3 %` plus lent que `p1_c1600`) avec `88` nœuds.
   - **Piste C (`vmlx-engine`, `mlx-community/Qwen3.8-27B-4bit`, `--text-only`)** : le co-prefill de prompts `> 2048` tokens déclenche un plantage `HTTP 500` dans `BatchMambaCache.extend()` (`(1,3,10240)` vs `(2,2048,10240)`), contournable uniquement en imposant `--prefill-batch-size 1`. Surtout, l'absence de tête MTP, la désactivation du cache paginé RAM (`backend=block-disk-only`) entraînant `230.38 s` de persistances SSD cumulées (`185.06 s` de blocage d'admission) et `17 721` tokens de recalcul delta SSM GPU plafonnent le débit à `7.01 tok/s` pondéré par requête (`13.25 tok/s` nets) et doublent la durée (`1 096.76 s`). En outre, les nœuds chiffrés chutent à `58` (`73.4 %` de `p1_c1600`).

2. **Validation finale sur l'étalon dense FEA (`p1_c1600_fea`) et stratégie d'interrogation** :
   - La configuration **`p1_c1600`** conserve le meilleur compromis vitesse/qualité (`107.0 s/chunk`, `14/14` `<|COMPLETE|>`, préservation exacte des grandeurs RDM critiques : `133,1 MPa`, `0,2622 mm`, `Sf_peak = 3,79`, `Sf_P95 = 19,50`, `505 MPa`, `570 MPa`, `71 700 MPa`, `85°C`, `202,30 g`, `55,80 × 55,80 mm`, `Nord-Lock M4`, `Loctite 243`).
   - Sur les `8` références catalogue `McMaster-Carr` du document, toutes (`8/8`) restent intactes dans `kv_store_text_chunks.json` / `vdb_chunks`, mais seules `2/8` (`90631A113`, `93625A200`) forment un nœud nominatif dans le graphe, confirmant l'usage impératif du mode `--mode naive` de [`ask_rag.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/ask_rag.py) pour les cotes exactes et codes catalogue, et `--mode hybrid` pour les dépendances cinématiques/RDM.

3. **Standard de production retenu pour D-Bot (`111` fichiers en attente)** :
   - **Serveur** : `env OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_FLASH_ATTENTION=1 ollama serve` (KV `f16` natif, sans `OLLAMA_KV_CACHE_TYPE=q8_0`).
   - **Indexation** : [`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py) `--provider ollama` avec défauts **`CHUNK_SIZE=1600`**, **`CHUNK_OVERLAP_SIZE=150`**, **`LLM_MAX_ASYNC=1`** (`~105 s/chunk` en moyenne, recommandé en exécution manuelle de nuit pour les `111` fichiers), avec **`qwen3.8:27b-mlx`** comme unique modèle d'extraction locale validé.
   - **Échec mesuré de `gemma4:26b` en indexation (`p1_gemma4_c1600` du `2026-11-21`, `NO-GO`)** : bien que `3,22×` plus rapide (`160,0 s` vs `515,78 s`), `gemma4:26b` corrompt le délimiteur LightRAG en double barre `<|#||>` (`37` lignes cassées, `30` warnings `found 4/5 fields`), ajoute des backticks parasites, altère un identifiant (`Autodesk Fusion 364`) et ampute le graphe de `-31,0 %` des nœuds (`69` vs `100`, `46` chiffrés vs `79`) et `-67,4 %` des arêtes (`44` vs `135`). Il est donc **écarté de l'indexation LightRAG** et réservé à l'inférence rapide/QA/dialogue (`Banc A` validé dans [57_Veille_et_Benchmark_Modeles_Robotique_Ollama_Unsloth.md](./57_Veille_et_Benchmark_Modeles_Robotique_Ollama_Unsloth.md)).
   - **Campagne complémentaire Cloud vs Local du `2026-11-21` (`1min.ai` & `Gemini Free Tier`)** : les `19` micro-sondes `1min.ai`, les tests complets `5` chunks sur Étalon 1 (`mistral-small-latest` vainqueur `1minai` à `0,480 cr/tok` vs `gpt-6-luna` / `mistral-small-2603` / `qwen3.7-flash`) et l'audit des manuels jumeaux `Gemini -lite` vs `qwen3.8:27b-mlx` (`-77 %` à `-89 %` de relations -> exclusion des `-lite` de `GEMINI_INDEX_CASCADE`) sont consignés dans [STUDY_Benchmarks_Indexation_RAG_20261121.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/STUDY_Benchmarks_Indexation_RAG_20261121.md).
   - **Rôle conservé pour `UD-Q4_K_XL` V3.1 + `mmproj-F16.gguf`** : Phase 3 (Unsloth Studio `:8888`, Thinking Mode, Tool Calling auto-réparateur et vision CAO).

---

## 4. Phase 3 (Point 3) — Déploiement général d'Unsloth sur le dépôt D-Bot

### 4.1 Chantier 3A — Jeu étalon QA français via Data Recipes et AUDIT_QUESTION_REPONSE

L'audit de [`AUDIT_QUESTION_REPONSE.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/AUDIT_QUESTION_REPONSE.json) montre que le dépôt dispose déjà d'une graine de **`19` questions-réponses** structurées (`section`, `question`, `answer`, `id`), ce qui est insuffisant pour départager finement `qwen3.8:27b-mlx` versus `Qwen3.8-UD-Q4_K_XL` Dynamic V3.1 ou `gemma4:26b` sur des chiffres d'ingénierie.

**Workflow recommandé dans Unsloth Studio (`http://127.0.0.1:8888`, module `Data Recipes` / `~/.unsloth/studio/data-designer/`)** :

1. **Démarrer Unsloth Studio** (en veillant à ne pas dépasser le budget RAM si Ollama tourne simultanément) :

```bash
/Users/davidsergent/.local/bin/unsloth studio --port 8888 --host 127.0.0.1
```

2. **Corpus source d'entrée (3 documents de Vérité Terrain Niveau 1)** :
   - [`DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md)
   - [`DOSSIER_TECHNIQUE_Calculs_FEA_Torse_et_Bassin.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Calculs_FEA_Torse_et_Bassin.md)
   - [`FINAL_Liste_Achats_BOM.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/05_Gestion_Projet/FINAL_Liste_Achats_BOM.md)
3. **Recette nodale Data Recipes (`100` paires QA cibles)** :
   - **Générateur (`Qwen3.8-27B-UD-Q4_K_XL` V3.1)** : produire `40` questions de métrologie/cotes (`mm`, masses `kg`, entraxes), `35` questions FEA/RDM (`MPa`, coefficients `Sf`, charges `N`/`Nm`) et `25` questions BOM/quincaillerie (`9` caractères alphanumériques `McMaster-Carr`, références `RobStride`, couples de serrage `N.m`).
   - **Validateurs automatiques en sortie de pipeline** :
     - Langue strictement française, réponse sourcée vers un nom de fichier et une valeur numérique exacte présente dans le texte source.
     - Rejet de tout signe dollar ou syntaxe LaTeX dans les réponses générées (conformité aux règles D-Bot).
4. **Exploitation comme banc de non-régression RAG (`mcp_lightrag_server.py` / `ask_rag.py`)** :
   - Fusionner les `19` entrées de [`AUDIT_QUESTION_REPONSE.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/AUDIT_QUESTION_REPONSE.json) + `100` paires Data Recipes dans `Annexes/Outils_de_Travail/RAG/BENCHMARK_QA_DBOT_120.json`.
   - Comparer le taux d'exactitude numérique (cotes exactes, `0` confusion d'actionneur ou d'arbre creux) entre l'index Ollama actuel et un graphe extrait par Dynamic V3.1.

### 4.2 Chantier 3B — Agents locaux de code, tool calling auto-réparateur et vision CAO

Pour le développement quotidien hors indexation (`AuditTorse.py`, scripts `Code/rag/`, simulations RDM, analyse de rendus CAO), `Qwen3.8-27B` bascule en **Thinking Mode** (`temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=0.0`, `preserve_thinking=True`) derrière la passerelle Unsloth Studio (`:8888`) afin de bénéficier de l'auto-réparation JSON des appels d'outils :

1. **Lancement en ligne de commande unifiée (`unsloth studio run`)** :

```bash
/Users/davidsergent/.local/bin/unsloth studio run \
  --model unsloth/Qwen3.8-27B-GGUF \
  --gguf-variant UD-Q4_K_XL \
  --speculative-type mtp \
  --spec-draft-n-max 4 \
  --parallel 2 \
  --max-seq-length 65536 \
  --host 127.0.0.1 \
  --port 8888
```

*(Note : en cas de besoin de précision maximale sur du code critique, tu as assez de RAM sur `64 Go` pour monter ensuite à `--gguf-variant UD-Q5_K_XL` (`20,98 Go`), au prix d'un léger recul de `tok/s`.)*

2. **Connexion directe des agents IDE / CLI (`unsloth start`)** :

```bash
/Users/davidsergent/.local/bin/unsloth start claude
```

Ou pour VS Code Copilot Chat / OpenCode :

```bash
/Users/davidsergent/.local/bin/unsloth start vscode
```

3. **Profil proposé pour [`.kilo/kilo.jsonc`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/.kilo/kilo.jsonc)** (à ajouter uniquement après validation de l'API key imprimée par `unsloth studio run`, et en gardant `127.0.0.1:8888/v1`) :

```json
    "unsloth-qwen38": {
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "http://127.0.0.1:8888/v1",
        "apiKey": "REMPLACER_PAR_CLE_UNSLOTH_STUDIO"
      },
      "models": {
        "unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL": {
          "name": "Qwen3.8 27B Dynamic V3.1 (Thinking + Tool Healing)"
        }
      }
    }
```

4. **Audit multimodal des planches CAO (`mmproj-F16.gguf`)** :
   - Lors de la rédaction ou vérification de schémas SVG face aux captures [`Visual_Snapshots`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots), charger conjointement `Qwen3.8-27B-UD-Q4_K_XL.gguf` et `mmproj-F16.gguf` dans Unsloth Studio (interface Chat/Vision `:8888`) ou `llama-server --mmproj ...` pour contrôler les cotes, alignements gauche/droite et perçages sans quota externe.

### 4.3 Chantier 3C — Périmètre fine-tuning et distillation Jetson Orin Nano

Conformément à l'analyse hardware de la section `3.3` de [`55_Rapport_Expert_Qwen38_Unsloth_M1Max.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/IA_sur_Mac_M1_Pro_Max_64Go/55_Rapport_Expert_Qwen38_Unsloth_M1Max.md), **aucun fine-tuning 27B n'est déployé sur le MacBook Pro M1 Max**. Ce chantier reste en réserve (exécution CUDA externe / Kaggle `2× T4`) uniquement si l'un des deux besoins suivants est avéré :
- **Cas 1 (Extracteur LightRAG ultra-rapide 1-passe)** : si même après Phase 1+2 les réindexations restent jugées trop lentes, entraîner un LoRA `QLoRA 4-bit` CUDA sur un jeu de `300–500` chunks D-Bot validés (`<|#|>`, français strict, zéro gleaning requis) et l'exporter en GGUF pour M1 Max.
- **Cas 2 (Embarqué robot Jetson Orin Nano `8 Go`)** : distiller depuis les paires Data Recipes + `Qwen3.8-27B` vers un petit modèle (`<= 4B` ou `Qwen3.5/3.8` compact) pour le dialogue/supervision embarquée hors ligne sur la Jetson du robot.

### 4.4 Bilan mesuré de la Phase 3 (Jalon J4)

Toutes les briques critiques de l'écosystème Unsloth (`http://127.0.0.1:8888`) ont été câblées, réparées et mesurées sur le poste M1 Max (`UD-Q4_K_XL` + `mmproj-F16.gguf` + MTP `n_max=4`) :

1. **Sécurisation & Unification `:8888/v1`** : isolation de [`.kilo/kilo.jsonc`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/.kilo/kilo.jsonc) dans [`.gitignore`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/.gitignore), chargement centralisé `.env` (`UNSLOTH_API_KEY`) dans [`ask_rag.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/ask_rag.py), [`mcp_lightrag_server.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/mcp_lightrag_server.py), [`check_integrity.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/check_integrity.py) et [`rag_cli.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/rag_cli.py), et correction de [`check_integrity.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/check_integrity.py) (`kv_store_llm_response_cache.json`, réglages Non-Thinking `:8888/v1`, déduplication de `19 -> 6` questions uniques).
2. **Assainissement LightRAG & Accélération `×3` en synthèse locale** :
   - [`repair_db_sync.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/repair_db_sync.py) a purgé `343` nœuds et `500` arêtes orphelines sur `186` anciens `doc_id` et rétabli le reranking `BAAI/bge-reranker-base` dans [`mcp_lightrag_server.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/mcp_lightrag_server.py) (`0` warning en requête).
   - Le plafonnement local `RAG_QUERY_MAX_TOKENS=9500` (`chunk_top_k=5..6`) et le relèvement du timeout MCP Kilo (`300 000 ms`) réduisent la latence de [`ask_rag.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/ask_rag.py) de **`311,62 s -> 101,65 s`** en `naive` et de **`411,28 s -> 137,67 s`** en `hybrid` (`154,64 s` via MCP `/opt/homebrew/bin/rag --search --llm-mode internal`), avec consigne texte brut sans LaTeX (`has_dollar=False`).
3. **Tool Calling (`Thinking Mode`), Vision CAO (`mmproj-F16.gguf`) & Benchmark QA** :
   - **Tool Calling (`reasoning_effort="low"`, `preserve_thinking=True`)** : `8,67 s` au Tour 1 (`tool_calls` JSON valide) + `13,5 s` au Tour 2 (`552` tokens réutilisés en cache KV), restitution exacte de `4` références McMaster-Carr et du couple `2,2 N.m`.
   - **Vision CAO** : `100 %` d'exactitude OCR FEA sur [`Bride_Epaule_VonMises.png`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/Pieces_Isolees/Bride_Epaule/Bride_Epaule_VonMises.png) (`70,47 s`) et comptage orthogonal exact `10/10` sur [`Bride_Epaule_face.png`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/Pieces_Isolees/Bride_Epaule/Bride_Epaule_face.png) (`88,32 s`) ; sur vue d'assemblage dense ([`01_vue_face.png`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/Vues_Ensemble/01_vue_face.png)), `reasoning_effort="low"` (`147,71 s`, `finish=stop`) évite la saturation `2048` tokens du mode `xhigh` par défaut.
   - **Data Recipes (socle QA facultatif extensible à `100` paires)** : recette `dbot-qa-benchmark-v1` enregistrée dans Unsloth Studio (`10` paires validées en `185,3 s`, fusionnées dans [`BENCHMARK_QA_DBOT_120.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/BENCHMARK_QA_DBOT_120.json) via [`build_qa_benchmark.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/build_qa_benchmark.py)).

---

## 5. Phase 4 — Calendrier d'exécution, plan de rollback et contrôle DevSecOps

### 5.1 Séquencement recommandé des 4 jalons

| Jalon | Contenu exact | Statut & Durée mesurée | Livrable / Décision |
| :--- | :--- | :--- | :--- |
| **J1 — Sauvegarde & Patchs Phase 1** | Backup `lightrag_dbot_db`, mise à jour contrôlée de `index_docs.py`, `mcp_lightrag_server.py`, `ask_rag.py` | **FAIT (2026-11-14)** | `RAG_DB_PATH` + sampling Qwen3.8 + fix `--files` (`1600/150` par défaut) + `audit_dbot_security.py` `PASSED` |
| **J2 — Essais Point 1 (Chunking)** | Runs sandbox Ollama sur `STUDY_Densites_Apparentes...` (`1200/100` vs `1600/150`) | **FAIT (`609.38 s` vs `515.78 s`)** | Gain `-15.4 %`, richesse chiffrée max (`100` nœuds / `79` chiffrés) -> **`1600/150` validé** |
| **J3 — Banc A / B / C & Validation Finale** | Runs parallèles Pistes A, B, C + confirmation sur `STUDY_Calculs_FEA_Bride_Epaule_RS04.md` | **FAIT (2026-11-14)** (`504.7 s`, `620.6 s`, `1 096.8 s`, `748.9 s`) | Pistes A/B/C `NO-GO` ; **`Ollama MLX f16` + `async=1` + `1600/150` promu** (`p1_c1600_fea` `14/14` `<\|COMPLETE\|>`) |
| **J4 — Écosystème Unsloth (Point 3)** | Setup `unsloth studio` `:8888`, réparation sync/rerank + cap `9 500` tokens RAG, Tool Calling Thinking, Vision CAO `mmproj-F16.gguf`, Data Recipes starter & fix `check_integrity.py` | **FAIT (2026-11-14)** | [`BENCHMARK_QA_DBOT_120.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/BENCHMARK_QA_DBOT_120.json), [`repair_db_sync.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/repair_db_sync.py), [`build_qa_benchmark.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/build_qa_benchmark.py), `rag ×3` plus rapide (`0` warning), `audit_dbot_security.py` `PASSED` |

### 5.2 Procédure de rollback immédiat en cas de régression

En cas d'anomalie sur les scripts RAG ou les résultats d'extraction :
1. **Repli instantané du code Python** : restaurer `Code/rag/` via Git sans toucher au reste du dépôt :

```bash
git checkout -- Code/rag/index_docs.py Code/rag/mcp_lightrag_server.py Code/rag/ask_rag.py
```

2. **Repli instantané de la base RAG** (uniquement si une opération a touché la prod par erreur) : supprimer le répertoire actif et renommer la sauvegarde `lightrag_dbot_db_backup_20261114`.
3. **Nettoyage des bacs à sable temporaires** une fois le gagnant promu :

```bash
rm -rf /tmp/lightrag_bench
```

### 5.3 Contrôle de sécurité obligatoire post-modification

Conformément aux règles DevSecOps D-Bot, **toute modification appliquée aux fichiers `Code/rag/*.py` en Phase 1** devra immédiatement être suivie d'un audit SAST & secrets retournant le code de sortie `0` (`PASSED`) avant tout commit ou utilisation en production :

```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/security/audit_dbot_security.py" --skip-sca
```
