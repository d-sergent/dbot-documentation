# 📖 Guide d'Utilisation : Système RAG & Audit D-Bot

Ce document explique comment maintenir et utiliser le système de Mémoire Graph-RAG du projet D-Bot (`Gemini Free Tier` prioritaire par défaut -> repli local spécialisé par tâche + traçabilité explicite du modèle utilisé).

## 📑 Sommaire

- [1. Indexation des Documents](#1-indexation-des-documents)
- [2. Audit d'Intégrité](#2-audit-dintégrité)
- [3. Interrogation de la base (`ask_rag.py` & `rag`)](#3-interrogation-de-la-base-ask_ragpy--rag)
- [4. Intégration Antigravity, Kilo & MCP (`dbot-rag`)](#4-intégration-antigravity-kilo--mcp-dbot-rag)
- [5. Maintenance, Traces Modèles & Logs](#5-maintenance-traces-modèles--logs)
- [6. Diagnostic et Maintenance](#6-diagnostic-et-maintenance)

## 1. Indexation des Documents

Le système scanne l'intégralité du dossier `Documentation/` pour extraire les entités et relations entre les composants.

### Lancement automatique (`--provider auto`, défaut) : Cascade Gemini Free Tier (non-lite) -> Repli Local `qwen3.8:27b-mlx` (`0` crédit payant)
Tente d'abord les **`8` modèles Gemini Free Tier non-lite** (`gemini-3.8-flash` -> `gemini-4-hydrogen` -> `gemini-3.6-flash` -> `gemini-3-flash-preview` -> `gemini-flash-latest` -> `gemini-2.5-flash` -> `gemini-3.7-flash` -> `gemini-3.5-flash` ; VLM `GEMINI_VLM_CASCADE`), puis bascule directement sur **Ollama local `qwen3.8:27b-mlx`** (`think=False`, démarré à la demande et arrêté en fin de lot ; **`0` crédit payant**, référence qualité sans troncature `4096` tokens ni sous-extraction `-lite`, cf. [STUDY_Benchmarks_Indexation_RAG_20261121.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/STUDY_Benchmarks_Indexation_RAG_20261121.md)). L'option `--with-1minai` (ou `RAG_AUTO_1MINAI=true` dans `.env`) permet si souhaité d'insérer 1min.ai en palier intermédiaire :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider auto
```

### Lancement via Ollama 100 % local (`qwen3.8:27b-mlx` — Texte, Vision & SVG XML)
Pour une indexation **100 % locale sans limite de quota**, utilisant `qwen3.8:27b-mlx` (`think=False`, `num_ctx=16384`, runner MLX GPU — seul modèle local sans erreur `<|#|>`) pour les textes, les schémas `.svg` (extracteur XML `defusedxml`) et les images `.png`/`.jpg` :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider ollama
```

*Variables optionnelles : `OLLAMA_BASE_URL` (défaut `http://127.0.0.1:11434`), `OLLAMA_MODEL` (défaut `qwen3.8:27b-mlx`), `OLLAMA_QA_MODEL` (défaut `gemma4:26b`), `OLLAMA_NUM_CTX` (`16384`), `OLLAMA_VLM_NUM_CTX` (`8192`), `GEMINI_HTTP_TIMEOUT_S` (`60`, min `10`), `GEMINI_QA_TIMEOUT_S` (`15`, min `10`).*

### Lancement via Cloud Gemini seul (Cascade)
Pour une indexation utilisant uniquement l'API Google Gemini avec bascule automatique Free Tier :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider gemini --thinking-level low
```

### Lancement via Cloud (Mode Round-Robin Optimisé)
Pour une indexation gratuite utilisant Gemini et OpenRouter avec gestion automatique des quotas :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider online
```

### Lancement via OpenRouter Seul
Pour forcer l'indexation via un modèle spécifique sur OpenRouter :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider openrouter --model nvidia/nemotron-3-super-120b-a12b:free
```

### Lancement via 1min.ai (`--provider 1minai` explicite, crédits 1min.ai)
Utilise la passerelle *stateless* `https://api.1min.ai/openai/v1` (`ONEMINAI_API_KEY` dans `.env`) avec suivi exact des tokens consommés (`in`/`out`). `--provider auto` ne touche jamais vos crédits 1min.ai :
```bash
# Lister les modeles actifs sur votre compte (0 credit depense)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/check_1minai.py"

# Indexer via 1min.ai (defaut mistral-small-latest ~0.480 cr/tok, ou --model mistral-small-2603 / qwen3.7-flash / gpt-6-luna)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider 1minai
```

### Lancement via Unsloth Studio (Local port 8888)
Pour une indexation locale via le serveur OpenAI-compatible Unsloth Studio (`unsloth/Qwen3.8-27B-GGUF`) :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider unsloth
```

> [!IMPORTANT]
> **Optimisation Ressources :** Sur Mac M1 Max (`64 Go`), ne gardez qu'un seul gros modèle `26–27B` chargé à la fois (`qwen3.8:27b-mlx` = `22,93 GiB` VRAM pour l'indexation/audit ; `gemma4:26b` = `18,28 GiB` VRAM pour le QA rapide). Ne jamais utiliser `gemma4:26b` pour indexer LightRAG (`-67,4 %` d'arêtes).

### Indexation directe par Antigravity (`0` LLM tiers — MCP & CLI)
Pour indexer des mises à jour sans solliciter Gemini, `1min.ai` ni Ollama, le module [`agent_indexing.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/agent_indexing.py) expose un pipeline 3 temps (**Prepare -> Extraction Antigravity -> Replay `LightRAG.ainsert()`**) via les outils MCP `rag_prepare_agent_index` / `rag_commit_agent_index` (compétence [`dbot-rag-agent-index`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/.agents/skills/dbot-rag-agent-index/SKILL.md)) ou la CLI :
- **Politique de thinking optimale (`--effort-profile balanced`, défaut)** : attribue automatiquement **`flash`** (`effort=low`, 1 passe directe sans sur-réflexion) aux chunks courants (Markdown, Python, SVG XML) et réserve **`inherit`** (`effort=medium`, jamais `extra_high`) aux dossiers Niveau 1 (`FINAL_`, `DOSSIER_TECHNIQUE_`, `STUDY_`, tableaux denses), PDF et images VLM (`.png`/`.jpg`).
```bash
# Préparer un lot (profil balanced par défaut, ou --effort-profile fast / thorough)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --prepare-agent --effort-profile balanced --files "Code/rag/README.md"

# Valider et committer dans LightRAG après extraction agent (0 appel LLM tiers)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --commit-agent "<job_id>"
```

### Indexation unitaire rapide via MCP CLI (`rag --index`)
Pour indexer immédiatement un fichier modifié (`.md`, `.py`, `.pdf`, `.svg`, image) via la cascade `auto` (Gemini -> `qwen3.8:27b-mlx`) ou `--provider ollama` :
```bash
rag --index "01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md"
```

## 2. Audit d'Intégrité

### Lancement de l'Audit d'Intégrité
L'audit interroge le graphe en mode `global` pour détecter les contradictions techniques entre les documents. Par défaut (`--provider auto`), il suit la cascade rapide **Gemini Free Tier `-lite` -> `1min.ai` (`mistral-small-2603`) -> Ollama `gemma4:26b`** (sinon `qwen3.8:27b-mlx` / Unsloth), tout en inscrivant le modèle réel utilisé dans l'en-tête du rapport :

```bash
# Audit automatique rapide (Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/check_integrity.py"

# Audit 100 % local via Ollama (gemma4:26b par defaut, ou --model qwen3.8:27b-mlx)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/check_integrity.py" --provider ollama
```

**Résultats générés :**
- `Annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md` : Rapport d'audit complet (inclut `> **Moteur réel utilisé** : ...`)
- `Annexes/Outils_de_Travail/RAG/AUDIT_QUESTION_REPONSE.json` : Questions structurées avec IDs

### Structure du fichier AUDIT_QUESTION_REPONSE.json
Le fichier JSON contient une structure claire avec :
```json
[
  {
    "id": 1,
    "section": "Nom de la section",
    "question": "Texte de la question",
    "answer": "Réponse à remplir"
  }
]
```

### Workflow de Résolution des Anomalies
Plutôt que de chercher et corriger les incohérences vous-même, nous avons mis en place un flux de travail "Human-in-the-loop" avec structure JSON.

**Nouveau workflow :**

1. **Générer l'audit :**
   ```bash
   /opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/check_integrity.py"
   ```
   -> Crée `AUDIT_INTEGRITE.md` et `AUDIT_QUESTION_REPONSE.json`

2. **Remplir les réponses :**
   - Éditer le fichier `AUDIT_QUESTION_REPONSE.json`
   - Remplir le champ `"answer"` pour chaque question
   - Le nombre de questions évolue automatiquement selon l'audit

3. **Générer le prompt de correction :**
   ```bash
   /opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/resolve_audit.py"
   ```
   -> Lit `AUDIT_QUESTION_REPONSE.json` avec questions + réponses
   -> Génère `PROMPT_CORRECTION.md`
   -> Affiche le prompt prêt à être utilisé

4. **Collez le prompt dans l'interface de l'IA de votre choix :**
   - **Antigravity** : Collez simplement le prompt dans le chat
   - **Kilo (Unsloth Studio `:8888` / Ollama `:11434`)** : Permet d'exploiter les modèles locaux retenus (`unsloth/Qwen3.8-27B-GGUF`, `qwen3.8:27b-mlx`, `gemma4:26b`) avec le serveur MCP `dbot-rag`

*L'IA va alors chercher les fichiers, préparer un plan de modification dans `PLAN_CORRECTION.md`, et **attendre votre validation ("OK")** avant de toucher à la documentation.*

**Avantages du nouveau système :**
- ✅ Le nombre de questions évolue automatiquement selon l'audit
- ✅ Structure claire : `id`, `section`, `question`, `answer`
- ✅ Modification facile : éditez simplement le JSON pour changer une réponse
- ✅ Traçabilité : chaque question a un ID unique et le modèle utilisé est tracé

## 3. Interrogation de la base (`ask_rag.py` & `rag`)

L'outil `ask_rag.py` utilise `--provider auto` par défaut (**cascade courte `Gemini -lite` -> `1min.ai` (`mistral-small-2603`) -> Ollama `gemma4:26b`** -> `qwen3.8:27b-mlx` -> Unsloth -> OpenRouter). Il affiche systématiquement `[Moteur RAG : ...]` sous la réponse et sur `stderr`.

```bash
# Recherche uniquement sans serveur LLM (0 Go RAM, graphe lexical + repli naive garanti)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode hybrid "Votre question"

# Recherche hybride avec mots-cles cibles explicites
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode hybrid --keywords "RB8016,RS-06,waist" "Votre question"

# Synthèse auto (Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" "Votre question"

# Synthèse locale forcée via Ollama (gemma4:26b par défaut en QA) ou Unsloth Studio (:8888)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" "Votre question" --provider ollama
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" "Votre question" --provider unsloth

# Recherche MCP CLI (defaut --llm-mode auto : Gemini -lite -> 1min.ai -> gemma4:26b)
rag --search "Couple et visserie RS-04"

# Décharger le modèle Ollama pour libérer la RAM unifiée en fin de session
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --stop-server
```

## 4. Intégration Antigravity, Kilo & MCP (`dbot-rag`)

Les outils D-Bot sont configurés dans `.kilo/kilo.jsonc` et `~/.gemini/antigravity/mcp_config.json` sur le serveur `Code/rag/mcp_lightrag_server.py` (pointant vers `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db`).
- **Mode `auto` (défaut MCP `rag_search`, `rag_analyze_impact`, `rag_audit_integrity`)** : exécute la cascade rapide **Gemini `-lite` (`3` modèles) -> `1min.ai` (`mistral-small-2603`) -> Ollama `gemma4:26b`** (sinon `qwen3.8:27b-mlx` / Unsloth / OpenRouter), avec repli transparent vers l'extraction brute `antigravity` si tous les backends échouent et trace `> **Trace Moteur RAG** : ...`.
- **Mode `internal`** : même cascade LLM rapide sans repli sur les extraits bruts `antigravity`.
- **Mode `antigravity` (explicite)** : extraction graphe/vecteur sans appel LLM externe (`> **Trace Moteur RAG** : Aucun LLM ...`).
- **Indexation (`rag_index_document` en `auto`)** : reste strictement **`Gemini non-lite -> Ollama qwen3.8:27b-mlx`** (`0` crédit `1min.ai` sans option explicite).

## 5. Maintenance, Traces Modèles & Logs

- **Trace en retour Python & MCP** :
  - Chaque appel Python (`ask_rag.py`, `check_integrity.py`) et MCP retourne `[Moteur RAG : <fournisseur> / <modele> [role=...] | bascules: ...]` indiquant quel modèle a répondu et quelles bascules (`503`, `429`, `400`) ont eu lieu (ou `Cache LightRAG (réponse en cache — 0 appel LLM)` lors d'un hit de cache).
- **Logs d'indexation** : Consultables dans `Code/rag/rag_indexing.log`.
  - `💎 Moteur d'indexation actif : Gemini (<modele>)` / `🦙 Moteur d'indexation actif : Ollama (qwen3.8:27b-mlx)`
  - `🧭 Moteur(s) d'indexation utilisés : ...` en synthèse finale.
- **Hash des fichiers** : Situé dans `lightrag_dbot_db/indexed_files.json`.

## 6. Diagnostic et Maintenance

### Lancer les tests unitaires de résilience RAG (offline)
```bash
/opt/homebrew/bin/python3.11 -m unittest "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/test_rag_resilience.py" -v
```

### Vérifier les modèles Gemini disponibles sur votre clé
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/check_gemini.py"
```

### Tester la connectivité OpenRouter
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/test_openrouter.py"
```

---
**Dernière mise à jour** : 2026-11-21 (architecture deux vitesses : Indexation `Gemini non-lite -> qwen3.8:27b-mlx` `0` crédit ; QA & Audit rapides `Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b` + `llm_mode="auto"` par défaut côté MCP/CLI)
