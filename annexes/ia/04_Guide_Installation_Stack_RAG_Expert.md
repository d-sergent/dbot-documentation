# Guide d'Installation de la Stack RAG Expert (Native Mac)

Ce guide détaille les étapes pour installer la totalité de la stack **Hybrid Agentic RAG** sur macOS sans Docker.

## 1. Prérequis Système
Avant de commencer, assurez-vous d'avoir :
*   **Homebrew** installé (`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`).
*   **Python 3.11+** installé via brew : `brew install python@3.11`.
*   **uv** (gestionnaire Python ultra-rapide) : `curl -LsSf https://astral.sh/uv/install.sh | sh`.

---

## 2. Étape 1 : Inférence Locale (Ollama)
1.  Téléchargez Ollama sur [ollama.com](https://ollama.com).
2.  Installez le modèle principal :
    ```bash
    ollama run qwen3.6:35b-a3b-q6_k
    ```
3.  Installez le modèle d'embedding (pour le RAG) :
    ```bash
    ollama pull nomic-embed-text
    ```

---

## 3. Étape 2 : Interface Native (Open WebUI)
Nous installons Open WebUI en mode natif pour économiser la RAM.
1.  Créez un environnement dédié :
    ```bash
    python3.11 -m venv ~/open-webui-env
    source ~/open-webui-env/bin/activate
    ```
2.  Installez Open WebUI et les dépendances RAG :
    ```bash
    pip install open-webui lancedb tantivy pypdf sentence-transformers flashrank
    ```
3.  Lancez le serveur :
    ```bash
    open-webui serve
    ```
    *Accès via http://localhost:8080*

---

## 4. Étape 3 : Recherche Agentique (Tavily & GPT Researcher)
1.  **Clé API** : Créez un compte sur [tavily.com](https://tavily.com) et récupérez votre clé.
2.  **Installation de GPT Researcher** :
    ```bash
    git clone https://github.com/assafelovic/gpt-researcher.git
    cd gpt-researcher
    pip install -r requirements.txt
    ```
3.  **Lien avec l'IA** : Dans Open WebUI > Settings > Web Search, activez Tavily et entrez votre clé.

---

## 5. Étape 4 : Fonctions Expertes (LanceDB & Reranker)
Dans l'interface Open WebUI, créez une nouvelle **Function** (Workspace > Functions > Create) :
1.  Copiez le code d'intégration **LanceDB** (voir annexe dédiée ou discussion).
2.  Configurez le chemin de votre dossier technique (ex: `~/Documents/Robotique_Docs`).
3.  Activez le **Qwen3-Reranker-0.6B** dans le code en utilisant le device `mps` pour profiter du GPU du Mac.

---

## 6. Étape 5 : Serveur MCP (Accès Fichiers)
Pour que l'IA puisse lire vos fichiers de projet en temps réel :
1.  Utilisez `uv` pour lancer un serveur de fichiers sécurisé :
    ```bash
    uvx mcp-server-filesystem /votre/chemin/vers/projets
    ```
2.  Dans Open WebUI > Settings > Connections > MCP Servers, ajoutez l'URL locale du serveur.

---

## 7. Étape 6 : Bouton d'Audit Claude 4.7 Opus
Cette étape lie votre local au Cloud pour la sécurité.
1.  Créez une **Action** dans Open WebUI nommée "Audit Expert 🛡️".
2.  Configurez la **Valve** avec votre clé API Anthropic.
3.  Utilisez le prompt d'audit expert pour forcer Claude à critiquer les calculs de Qwen (Couples, thermique, SdF).

---

## 8. Vérification Finale
Lancez une discussion et tapez :
> *"Indexe mes documents, lis mes contraintes dans mon dossier projet via MCP, cherche les prix des moteurs sur le web et propose-moi une solution technique. Enfin, demande un audit à Claude."*

**Si les icônes de recherche, de lecture de fichier et de bouclier d'audit s'activent successivement, votre stack est opérationnelle.**

---

*Guide d'installation — Stack RAG Expert — Version Native Mac M1 Max.*
