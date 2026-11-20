# 📖 Guide d'Utilisation : Système RAG & Audit D-Bot

Ce document explique comment maintenir et utiliser le système de Mémoire Graph-RAG du projet D-Bot.

## 🚀 1. Indexation des Documents

Le système scanne l'intégralité du dossier `Documentation/` pour extraire les entités et relations entre les composants.

### Lancement via Ollama (Local M1 Max — Texte, Vision & SVG XML) *(Recommandé)*
Pour une indexation **100 % locale sans limite de quota**, utilisant `qwen3.5:9b` (`think=False`, `num_ctx=16384`, runner MLX GPU) pour les textes, les schémas `.svg` (extracteur XML `defusedxml`) et les images `.png`/`.jpg` :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider ollama
```

*Variables optionnelles : `OLLAMA_BASE_URL` (défaut `http://127.0.0.1:11434`), `OLLAMA_MODEL` (défaut `qwen3.5:9b`), `OLLAMA_NUM_CTX` (`16384`), `OLLAMA_VLM_NUM_CTX` (`8192`).*

### Lancement via Cloud Gemini (Cascade)
Pour une indexation utilisant l'API Google Gemini avec bascule automatique entre modèles Flash/Lite :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider gemini --thinking-level low
```

### Lancement via Cloud (Mode Round-Robin Optimisé)
Pour une indexation gratuite utilisant Gemini et OpenRouter avec gestion automatique des quotas :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider online
```

### Lancement via OpenRouter Seul (Tencent)
Pour forcer l'indexation via un modèle spécifique sur OpenRouter (ex: Tencent Hunyuan 3) :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider openrouter --model tencent/hy3-preview:free
```

### Lancement via Unsloth Studio (Local port 8888)
Pour une indexation locale via le serveur OpenAI-compatible Unsloth Studio (`unsloth/Qwen3.8-27B-GGUF`) :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider unsloth
```

> [!IMPORTANT]
> **Optimisation Ressources :** Si vous passez par Unsloth Studio (`Qwen3.8-27B`, ~18-27 Go), coupez les autres gros serveurs pour libérer de la mémoire unifiée. Avec **Ollama + `qwen3.5:9b`** (~11-13 Go en pointe sur 64 Go), l'indexation cohabite confortablement avec Fusion 360.

### Indexation unitaire rapide via MCP CLI (`rag --index`)
Pour indexer immédiatement un fichier modifié (`.md`, `.py`, `.pdf`, `.svg`, image) via Ollama local :
```bash
rag --index "01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md" --provider ollama
```

## 🛡️ 2. Audit d'Intégrité

### Lancement de l'Audit d'Intégrité
L'audit interroge le graphe pour détecter les contradictions techniques entre les documents.

```bash
# Audit Rapide (via Gemini)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/check_integrity.py" --provider gemini

# Audit local via Ollama (demarrage automatique si inactif, arret en fin d'audit)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/check_integrity.py" --provider ollama
```

**Résultats générés :**
- `Annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md` : Rapport d'audit complet
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
   /opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/check_integrity.py" --provider ollama
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
   - **Kilo (Unsloth Studio `:8888` / Ollama `:11434`)** : Permet d'exploiter les modèles locaux retenus (`Qwen3.8-27B`, `Gemma 4 26B-A4B`, `qwen3.5:9b`) avec le serveur MCP `dbot-rag`

*L'IA va alors chercher les fichiers, préparer un plan de modification dans `PLAN_CORRECTION.md`, et **attendre votre validation ("OK")** avant de toucher à la documentation.*

**Avantages du nouveau système :**
- ✅ Le nombre de questions évolue automatiquement selon l'audit
- ✅ Structure claire : `id`, `section`, `question`, `answer`
- ✅ Modification facile : éditez simplement le JSON pour changer une réponse
- ✅ Traçabilité : chaque question a un ID unique

## 🤖 3. Interrogation de la base (`ask_rag.py`)

L'outil `ask_rag.py` utilise `--provider auto` par défaut (`Ollama -> Unsloth -> Gemini -> OpenRouter`).

```bash
# Recherche uniquement sans serveur LLM (0 Go RAM, graphe lexical + repli naive garanti)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode hybrid "Votre question"

# Recherche hybride avec mots-cles cibles explicites
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode hybrid --keywords "RB8016,RS-06,waist" "Votre question"

# Synthèse via cascade auto (demarre/arrete Ollama automatiquement si aucun backend actif)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" "Votre question"

# Synthèse via Unsloth Studio (:8888, unsloth/Qwen3.8-27B-GGUF)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" "Votre question" --provider unsloth

# Decharger le modele Ollama pour liberer la RAM unifiee en fin de session
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --stop-server
```

## 🤖 4. Intégration Antigravity, Kilo & MCP (`dbot-rag`)

Les outils D-Bot sont configurés dans `.kilo/kilo.jsonc` et `/Users/davidsergent/.gemini/config/mcp_config.json` sur le serveur `Code/rag/mcp_lightrag_server.py` (pointant vers `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db`).

## ⚠️ 5. Maintenance et Logs

- **Logs d'indexation** : Consultables dans `Code/rag/rag_indexing.log`.
- **Format du Log** :
    - `🔵 [MODELE] OK:X ERR:Y -> ✅ OK` : Succès.
    - `🔵 [MODELE] OK:X ERR:Y -> ⚠️ QUOTA` : Quota atteint pour ce modèle, bascule automatique.
- **Hash des fichiers** : Situé dans `lightrag_dbot_db/indexed_files.json`.

## ⚠️ 6. Diagnostic et Maintenance

### Tester les tests de resilience RAG (offline)
```bash
/opt/homebrew/bin/python3.11 -m unittest "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/test_rag_resilience.py" -v
```

### Tester la connectivité OpenRouter
Si vous avez un doute sur la disponibilité d'un modèle gratuit ou sur la validité de votre clé API :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/test_openrouter.py"
```

---
**Dernière mise à jour** : 2026-11-18 (`--provider auto`, contournement lexical `hl_keywords`/`ll_keywords` sans LLM en `--search-only`, gestion session `ollama serve`, alignment Unsloth `:8888/v1`)
