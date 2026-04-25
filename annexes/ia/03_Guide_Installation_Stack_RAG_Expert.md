# 🚀 Guide Expert : Installation de la Stack Hybrid Agentic RAG (Native Mac)

Ce guide détaille la mise en place d'un système d'intelligence artificielle local de haut niveau sur macOS. Ce système combine la puissance de l'inférence locale (confidentialité) avec la précision de l'audit Cloud (Claude 4.7 Opus).

---

## 📋 1. Architecture du Savoir Partagé (Infrastructure)
Pour que votre IA soit accessible depuis toutes vos sessions macOS (Standard et IA) sans duplication de données, nous utilisons une infrastructure centralisée.

### A. Création des répertoires physiques
Exécutez ces commandes pour préparer le stockage partagé :
```bash
mkdir -p "/Users/Shared/AI_Shared_Knowledge/lancedb/models"
mkdir -p "/Users/Shared/AI_Shared_Knowledge/ollama_models"
# Règle d'or : On donne les pleins accès pour le multi-session
sudo chmod -R 777 "/Users/Shared/AI_Shared_Knowledge"
```

### B. Configuration des dossiers de modèles
*   **LM Studio** : Dans `Settings > Models Directory`, pointez vers `/Users/Shared/AI_Shared_Knowledge/lancedb/models`.
*   **Ollama** : Ajoutez cette ligne à votre fichier `~/.zshrc` (dans chaque session) :
    ```bash
    export OLLAMA_MODELS="/Users/Shared/AI_Shared_Knowledge/ollama_models"
    ```

---

## 🛠️ 2. Environnement & Logiciels de Base
Nous installons l'interface en mode **Python natif** pour maximiser les performances de votre puce M1 Max.

### A. Création et Activation de l'Environnement Virtuel (venv)
> [!IMPORTANT]
> L'activation du venv est **obligatoire** avant toute installation ou exécution.
```bash
# 1. Création de l'environnement (Une seule fois)
python3.11 -m venv "/Users/Shared/AI_Shared_Knowledge/open-webui-env"

# 2. Activation de l'environnement (À chaque ouverture de terminal)
source "/Users/Shared/AI_Shared_Knowledge/open-webui-env/bin/activate"
```

### B. Installation de la Stack Python (Précision Chirurgicale)
Une fois le venv activé, lancez cette commande unique pour installer tous les outils :
```bash
pip3.11 install open-webui lancedb tantivy pypdf sentence-transformers flashrank tavily-python mcpo
```
*Note : `mcpo` est l'outil qui servira de pont entre vos serveurs locaux et l'interface web.*

---

## 🧠 3. Intelligence Vectorielle (LanceDB & Reranking)
Cette couche permet à l'IA de "lire" vos documents PDF locaux et de trier les informations.

### A. Configuration du Re-ranker (Précision Technique)
Dans l'interface Open WebUI (http://localhost:8080) :
1.  Allez dans `Settings > Documents`.
2.  Activez le switch **Hybrid Search** (Indispensable pour voir les options suivantes).
3.  Champ **Reranking Model** : Saisissez exactement `BAAI/bge-reranker-v2-m3`.
4.  Réglages de précision : 
    *   **Top K** : `10`
    *   **Top K Reranker** : `5`
5.  Cliquez sur **Save** en bas à droite.

---

## 🌐 4. Recherche Web & Serveurs MCP (Accès Système)
Cette section connecte votre IA au web et à vos fichiers locaux sans utiliser Node.js.

### A. Recherche Web (Tavily AI)
1.  Dans `Settings > Web Search`, activez **Tavily**.
2.  Saisissez votre clé API et réglez le `Search Depth` sur **Advanced**.

### B. Lancement des Serveurs MCP via mcpo (Pont HTTP)
Ouvrez deux terminaux séparés (avec venv activé) pour lancer les services :

1.  **Service Fichiers** (Terminal 1) : 
    ```bash
    mcpo run uvx filesystem-operations-mcp --root-dir "/Users/Shared/Mon Google Drive Physique/Documentation"
    ```
2.  **Service Git** (Terminal 2) : 
    ```bash
    mcpo run uvx mcp-server-git
    ```

### C. Déclaration dans l'interface Open WebUI (Conforme Doc Officielle)
1.  Allez dans **⚙️ Admin Settings** (Paramètres d'administration) → **External Tools** (Outils externes).
2.  Cliquez sur le bouton **+** (Add Server).
3.  **Type** : Sélectionnez impérativement **MCP (Streamable HTTP)**.
4.  **Auth** : Sélectionnez **None** (pour un usage local).
5.  **URL** : Copiez l'URL affichée par mcpo (ex: `http://localhost:8000`).
6.  Cliquez sur **Save**.

> [!CAUTION]
> **Important** : Les terminaux exécutant `mcpo` doivent rester **ouverts** pendant toute l'utilisation d'Open WebUI. Si vous les fermez, l'IA perdra l'accès à ses outils système.

## ✅ 5. Validation Finale de la Stack
Testez le bon fonctionnement avec ces trois questions dans le chat :

1.  **Test Git** : *"Quels sont les 3 derniers messages de commit sur ce dépôt ?"*
2.  **Test RAG** : *"Quelles sont les spécifications critiques du bus CAN dans mes PDFs ?"*
3.  **Test Filesystem** : *"Quels fichiers sont présents dans le dossier `code/scripts/ia/` ?"*

---

## 🛡️ 6. Workflow Quotidien "Expert"
1.  **Recherche** : L'IA locale (Qwen 3.6) cherche dans vos documents + Web + Git.
2.  **Audit Final** : Utilisez le bouton **Audit Expert 🛡️** (lié à Claude 4.7 Opus via une Action) pour valider les calculs critiques.

---
*Guide d'installation final (Version 100% Python) — Avril 2026*
