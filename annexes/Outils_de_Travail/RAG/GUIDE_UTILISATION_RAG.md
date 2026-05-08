# 📖 Guide d'Utilisation : Système RAG & Audit D-Bot

Ce document explique comment maintenir et utiliser le système de Mémoire Graph-RAG du projet D-Bot.

## 🚀 1. Indexation des Documents

Le système scanne l'intégralité du dossier `Documentation/` pour extraire les entités et relations entre les composants.

### Lancement via Cloud (Mode Round-Robin Optimisé)
Pour une indexation rapide et gratuite utilisant Gemini et OpenRouter (Tencent) avec gestion automatique des quotas :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/index_docs.py" --update --provider online
```

### Lancement via OpenRouter Seul (Tencent)
Pour forcer l'indexation via un modèle spécifique sur OpenRouter (ex: Tencent Hunyuan 3) :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/index_docs.py" --update --provider openrouter --model tencent/hy3-preview:free
```

### Lancement via vMLX (Local)
Pour une indexation 100% locale (ex: via Qwen 35B tournant sur vMLX) :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/index_docs.py" --update --provider local
```

> [!IMPORTANT]
> **Optimisation Ressources :** Avant de lancer une indexation locale (vMLX), il est fortement conseillé de couper tous les serveurs MCP (notamment le serveur RAG) pour libérer de la RAM/VRAM et éviter les conflits d'accès à la base de données.

## 🛡️ 2. Audit d'Intégrité

### Lancement de l'Audit d'Intégrité
L'audit interroge le graphe pour détecter les contradictions techniques entre les documents.

```bash
# Audit Rapide (via Gemini)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/check_integrity.py" --provider gemini

# Audit de Haute Précision (via Tencent/OpenRouter) : Force une nouvelle réflexion sans cache
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/check_integrity.py" --provider openrouter --model tencent/hy3-preview:free --clear-cache
```

**Résultats générés :**
- `annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md` : Rapport d'audit complet
- `annexes/Outils_de_Travail/RAG/AUDIT_QUESTION_REPONSE.json` : Questions structurées avec IDs

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
   /opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/check_integrity.py" --provider openrouter
   ```
   → Crée `AUDIT_INTEGRITE.md` et `AUDIT_QUESTION_REPONSE.json`

2. **Remplir les réponses :**
   - Éditer le fichier `AUDIT_QUESTION_REPONSE.json`
   - Remplir le champ `"answer"` pour chaque question
   - Le nombre de questions évolue automatiquement selon l'audit

3. **Générer le prompt de correction :**
   ```bash
   /opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/resolve_audit.py"
   ```
   → Lit `AUDIT_QUESTION_REPONSE.json` avec questions + réponses
   → Génère `PROMPT_CORRECTION.md`
   → Affiche le prompt prêt à être utilisé

4. **Collez le prompt dans l'interface de l'IA de votre choix :**
   - **Antigravity** : Collez simplement le prompt dans le chat
   - **Continue (VS Code)** : Permet de choisir n'importe quel modèle (Local ou OpenRouter) pour faire les modifications
   - **vMLX Studio** : À condition que le serveur MCP y soit actif

*L'IA va alors chercher les fichiers, préparer un plan de modification dans `PLAN_CORRECTION.md`, et **attendre votre validation ("OK")** avant de toucher à la documentation.*

**Avantages du nouveau système :**
- ✅ Le nombre de questions évolue automatiquement selon l'audit
- ✅ Structure claire : `id`, `section`, `question`, `answer`
- ✅ Modification facile : éditez simplement le JSON pour changer une réponse
- ✅ Traçabilité : chaque question a un ID unique

## 🤖 3. Interrogation de la base (Synthesis)

L'outil `ask_rag.py` permet de poser des questions complexes.

```bash
# Synthèse via OpenRouter (Moteur Tencent Hunyuan 3 - Gratuit et puissant)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/ask_rag.py" "Votre question" --provider openrouter --model tencent/hy3-preview:free

# Synthèse via modèle local (vMLX)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/ask_rag.py" "Votre question" --provider local

# Recherche uniquement (sans synthèse LLM, affiche les extraits)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/ask_rag.py" "Votre question" --search-only
```

## 🤖 4. Intégration vMLX & MCP

Pour utiliser les outils D-Bot (RAG, calculs, recherche) directement dans l'interface de chat de **vMLX**, vous devez configurer le chemin du serveur MCP.

### Configuration du Path MCP
Dans les réglages de vMLX (Config MCP), renseignez le chemin suivant :
`/Users/davidsergent/.cache/mcp/mcp-config.json`

## ⚠️ 5. Maintenance et Logs

- **Logs d'indexation** : Consultables dans `code/rag/rag_indexing.log`. 
- **Format du Log** : 
    - `🔵 [MODELE] OK:X ERR:Y -> ✅ OK` : Succès.
    - `🔵 [MODELE] OK:X ERR:Y -> ⚠️ QUOTA` : Quota atteint pour ce modèle, bascule automatique.
- **Hash des fichiers** : Situé dans `lightrag_dbot_db/indexed_files.json`.

## ⚠️ 6. Diagnostic et Maintenance

### Tester la connectivité OpenRouter
Si vous avez un doute sur la disponibilité d'un modèle gratuit ou sur la validité de votre clé API :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/test_openrouter.py"
```

---
**Dernière mise à jour** : 2026-05-08 (Ajout workflow JSON structuré AUDIT_QUESTION_REPONSE.json)
