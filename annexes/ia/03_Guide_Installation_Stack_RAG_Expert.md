# 🚀 Guide Expert : Installation de la Stack Hybrid Agentic RAG (Native Mac)

Ce guide détaille la mise en place d'un système d'intelligence artificielle local de haut niveau sur macOS. Ce système combine la puissance de l'inférence locale (confidentialité) avec la précision de l'audit Cloud (Claude 4.7 Opus).

---

## 📋 1. Architecture du Savoir Partagé
Pour que votre IA soit accessible depuis toutes vos sessions macOS (Standard et IA) sans duplication de données, nous utilisons une infrastructure centralisée.

### A. Création du coffre-fort de données
Ouvrez un terminal et créez l'arborescence dans le répertoire partagé :
```bash
mkdir -p "/Users/Shared/AI_Shared_Knowledge/lancedb/models"
mkdir -p "/Users/Shared/AI_Shared_Knowledge/ollama_models"
# Règle d'or : On donne les pleins accès pour le multi-session
sudo chmod -R 777 "/Users/Shared/AI_Shared_Knowledge"
```

### B. Configuration des dossiers de modèles
*   **LM Studio** : Dans `Settings > Models Directory`, pointez vers `/Users/Shared/AI_Shared_Knowledge/lancedb/models`.
*   **Ollama** : Ajoutez cette ligne à votre fichier `~/.zshrc` (pour chaque session) :
    ```bash
    export OLLAMA_MODELS="/Users/Shared/AI_Shared_Knowledge/ollama_models"
    ```

---

## 🛠️ 2. Environnement & Interface (Open WebUI)
Nous installons l'interface en mode **Python natif** pour maximiser les performances de votre puce M1 Max et économiser 8 Go de RAM par rapport à Docker.

### A. Création de l'Environnement Virtuel (venv)
> [!IMPORTANT]
> L'activation du venv est **obligatoire** avant chaque étape suivante.
```bash
# Création (à ne faire qu'une fois)
python3.11 -m venv "/Users/Shared/AI_Shared_Knowledge/open-webui-env"

# Activation (à faire à chaque nouvelle session de terminal)
source "/Users/Shared/AI_Shared_Knowledge/open-webui-env/bin/activate"
```

### B. Installation de la Stack logicielle
```bash
pip3.11 install open-webui lancedb tantivy pypdf sentence-transformers flashrank tavily-python mcpo
```

### C. Lancement de l'interface
```bash
open-webui serve
```
*Accès : http://localhost:8080*

---

## 🧠 3. Intelligence Vectorielle (LanceDB & Reranking)
Cette couche permet à l'IA de "lire" vos documents PDF locaux et de trier les informations par pertinence.

### A. Configuration du Re-ranker (L'Expert de tri)
Dans l'interface Open WebUI :
1.  Allez dans `Settings > Documents`.
2.  Activez le switch **Hybrid Search** (Indispensable pour voir les options).
3.  Champ **Reranking Model** : Saisissez `BAAI/bge-reranker-v2-m3`.
4.  Réglages de précision : 
    *   **Top K** : `10`
    *   **Top K Reranker** : `5`
5.  Cliquez sur **Save**.

---

## 🌐 4. Recherche Web & Outils (Tavily & MCP)
Cette section connecte votre IA au monde extérieur et à votre système de fichiers.

### A. Recherche Web (Tavily AI)
1.  Dans `Settings > Web Search`, activez **Tavily**.
2.  Saisissez votre clé API et réglez le `Search Depth` sur **Advanced**.

### B. Serveurs MCP (Le Pont Système)
Open WebUI communique via HTTP. Pour Git et les fichiers locaux, utilisez le proxy `mcpo` :

1.  **Pont Fichiers** : 
    ```bash
    mcpo run npx -y @modelcontextprotocol/server-filesystem "/Users/Shared/Mon Google Drive Physique/Documentation"
    ```
2.  **Pont Git** : 
    ```bash
    mcpo run uvx mcp-server-git
    ```
> [!TIP]
> Notez les URLs fournies par `mcpo` (ex: http://localhost:8000) et déclarez-les dans `Settings > Integrations > MCP` sous le type **Streamable HTTP**.

---

## ✅ 5. Validation de la Stack
Testez votre système avec ces trois requêtes dans un nouveau chat :

1.  **Test Git** : *"Donne-moi les 3 derniers commits du dépôt."*
2.  **Test RAG** : *"Quelles sont les spécifications du bus CAN dans mes documents ?"*
3.  **Test Fichiers** : *"Liste les fichiers du dossier `annexes/ia/`."*

---

## 🛡️ 6. Workflow Quotidien "Expert"
1.  **Dégrossissage** : L'IA locale (Qwen 3.6) cherche dans vos documents + Web + Git.
2.  **Audit Final** : Utilisez le bouton **Audit Expert 🛡️** (lié à Claude 4.7 Opus via une Action) pour valider les calculs critiques et la sécurité.

---
*Documentation Finalisée — Avril 2026 — D-Bot Project*
