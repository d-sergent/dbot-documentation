# Guide d'Installation de la Stack RAG Expert (Native Mac)

Ce guide détaille les étapes pour installer la totalité de la stack **Hybrid Agentic RAG** sur macOS sans Docker.

## 1. Prérequis Système & Partage Multi-Session
Pour que la stack soit accessible depuis vos différentes sessions, nous utilisons le répertoire partagé de macOS.

1.  **Création du dossier de savoir partagé** :
    ```bash
    mkdir -p "/Users/Shared/AI_Shared_Knowledge/lancedb"
    # Donner les accès aux deux sessions
    sudo chmod -R 777 "/Users/Shared/AI_Shared_Knowledge"
    ```
2.  **Homebrew & Python** :
    ```bash
    brew install python@3.11
    ```
3.  **uv** (gestionnaire Python ultra-rapide) :
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

---

## 2. Étape 1 : Inférence Locale (Ollama)
1.  **Installation** : Téléchargez et installez l'application depuis [ollama.com](https://ollama.com).
2.  **Modèle de Raisonnement** : Installez le Qwen 3.6 35B (version optimisée pour votre RAM) :
    ```bash
    ollama run qwen3.6:35b-a3b-q6_k
    ```
3.  **Modèle d'Embedding** : Indispensable pour que l'IA puisse "comprendre" vos PDFs :
    ```bash
    ollama pull nomic-embed-text
    ```
4.  **Vérification** : Tapez `ollama list` pour vérifier que les deux modèles sont présents.

---

## 3. Étape 2 : Interface Native (Open WebUI)
Nous installons Open WebUI en mode natif (Python) pour économiser les ~8 Go de RAM habituellement réservés par Docker.

1.  **Création de l'environnement virtuel** :
    ```bash
    python3.11 -m venv "/Users/Shared/AI_Shared_Knowledge/open-webui-env"
    source "/Users/Shared/AI_Shared_Knowledge/open-webui-env/bin/activate"
    ```
2.  **Installation des dépendances** :
    ```bash
    pip install open-webui lancedb tantivy pypdf sentence-transformers flashrank
    ```
3.  **Lancement** :
    ```bash
    open-webui serve
    ```
    *Accès via http://localhost:8080*

---

## 4. Étape 3 : Recherche Web (Tavily AI)
1.  **Clé API** : Récupérez votre clé gratuite sur [tavily.com](https://tavily.com).
2.  **Configuration** : Dans Open WebUI > Settings > Web Search :
    *   Activer la recherche.
    *   Moteur : **Tavily**.
    *   Clé API : Coller votre clé.

---

## 5. Étape 4 : Fonctions Expertes (LanceDB & Reranker)
Créez une **Function** dans Open WebUI (Workspace > Functions) avec les paramètres suivants :
*   **Database Path** : `/Users/Shared/AI_Shared_Knowledge/lancedb`
*   **Documents Path** : Le chemin de votre dossier de documentation robotique.
*   **Re-ranker** : Configurez le modèle `Qwen3-Reranker-0.6B` pour utiliser le device `mps` (Metal).

---

## 6. Étape 5 : Serveur MCP & Audit Claude
1.  **Accès Fichiers** : Lancez le serveur MCP pour vos projets :
    ```bash
    uvx mcp-server-filesystem "/Users/Shared/Mon Google Drive Physique/Documentation"
    ```
2.  **Action d'Audit** : Créez une **Action** nommée "Audit Expert 🛡️" liée à Claude 4.7 Opus pour la validation finale des calculs et de la sécurité.

---

*Guide d'installation final — Avril 2026.*
