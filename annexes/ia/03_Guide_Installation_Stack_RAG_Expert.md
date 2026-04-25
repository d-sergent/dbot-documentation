# Guide d'Installation de la Stack RAG Expert (Native Mac)

Ce guide détaille les étapes pour installer la totalité de la stack **Hybrid Agentic RAG** sur macOS sans Docker.

## 1. Prérequis Système & Partage Multi-Session
Pour que la stack soit accessible depuis vos différentes sessions (Standard et IA), nous utilisons le répertoire partagé de macOS.

1.  **Création du dossier de savoir partagé** :
    ```bash
    mkdir -p "/Users/Shared/AI_Shared_Knowledge/lancedb/models"
    # Donner les accès aux deux sessions (Crucial pour le partage)
    sudo chmod -R 777 "/Users/Shared/AI_Shared_Knowledge"
    ```
    > [!IMPORTANT]
    > **Note Technique** : LanceDB est une base de données "embedded". Les fichiers (format Apache Arrow) sont physiquement stockés dans ce dossier. Contrairement à une base classique, il n'y a pas de "serveur" à lancer ; c'est l'accès direct aux fichiers qui permet le partage entre vos sessions.
2.  **Configuration LM Studio (Session Standard)** :
    *   Ouvrez LM Studio > Settings.
    *   Changez le **Models Directory** pour : `/Users/Shared/AI_Shared_Knowledge/lancedb/models`.
3.  **Homebrew, Python & uv** : Installez-les via brew (voir section précédente).

---

## 2. Étape 1 : Inférence Locale (Choix du Moteur)

### Option A : LLMster (`lms`) - [Recommandé pour la simplicité]
Idéal car il partage nativement le dossier de LM Studio sans aucune importation.
1.  **Installation** (Session IA) :
    ```bash
    npm install -g @lmstudio/lms
    ```
2.  **Lancement** :
    ```bash
    lms server start
    lms load <nom-du-modèle-téléchargé>
    ```

### Option B : Ollama - [Recommandé pour l'écosystème]
Plus puissant pour les embeddings et la vision. 
1.  **Installation** : Téléchargez l'app sur [ollama.com](https://ollama.com).
2.  **Partage Multi-Session (Important)** : 
    Par défaut, Ollama stocke les modèles dans `~/.ollama`. Pour partager les modèles entre sessions, ajoutez ceci à votre fichier `~/.zshrc` dans **chaque session** :
    ```bash
    export OLLAMA_MODELS="/Users/Shared/AI_Shared_Knowledge/ollama_models"
    ```
3.  **Téléchargement direct** :
    ```bash
    # Télécharger sans lancer
    ollama pull qwen3.6:35b-a3b
    # Télécharger et lancer immédiatement
    ollama run qwen3.6:35b-a3b
    ```
4.  **Modèle d'Embedding** : `ollama pull nomic-embed-text`.

---

## 3. Étape 2 : Interface Native (Open WebUI)
> [!IMPORTANT]
> **RÈGLE D'OR** : Toutes les commandes Python suivantes **DOIVENT** être exécutées après avoir activé l'environnement virtuel. Ne l'oubliez jamais, sous peine d'erreurs de bibliothèques manquantes.
> ```bash
> source "/Users/Shared/AI_Shared_Knowledge/open-webui-env/bin/activate"
> ```

1.  **Création de l'environnement virtuel dans le dossier partagé** :
    ```bash
    # À ne faire qu'une seule fois
    python3.11 -m venv "/Users/Shared/AI_Shared_Knowledge/open-webui-env"
    source "/Users/Shared/AI_Shared_Knowledge/open-webui-env/bin/activate"
    ```
    > [!TIP]
    > **Pourquoi ici ?** En installant le venv dans `/Users/Shared`, toutes les bibliothèques installées via `pip3.11` sont physiquement stockées au même endroit pour vos deux sessions. Vous économisez de l'espace disque et garantissez que les deux sessions utilisent exactement les mêmes versions de code.
2.  **Installation des dépendances** :
    ```bash
    pip3.11 install open-webui lancedb tantivy pypdf sentence-transformers flashrank tavily-python
    ```
3.  **Lancement** :
    ```bash
    open-webui serve
    ```
    *Accès via http://localhost:8080*

---

## 4. Étape 3 : Intelligence Vectorielle (LanceDB & Re-ranker)
Cette étape installe les deux "moteurs" de votre savoir :
1.  **LanceDB (Le Bibliothécaire)** : Il stocke et retrouve les documents.
2.  **Le Re-ranker (L'Expert)** : Il relit les résultats de LanceDB pour ne donner que les plus pertinents à l'IA. C'est lui qui évite que l'IA ne raconte n'importe quoi en confondant deux moteurs.

**Configuration du Re-ranker (Dans l'interface Open WebUI)** :
*   Allez dans `Settings > Documents`.
*   Activez d'abord le switch **Hybrid Search** (Indispensable pour faire apparaître les options de Reranking).
*   Cherchez **Reranking Model** et tapez : `BAAI/bge-reranker-v2-m3`.
*   Réglez **Top K** sur `10` et **Top K Reranker** sur `5`.
*   Cliquez sur **Save** en bas à droite.

---

## 5. Étape 4 : Recherche Web (Tavily AI)
Tavily est le "bras armé" de votre système sur Internet.

### A. Configuration Open WebUI (Usage Quotidien)
1.  **Activation** : Allez dans `Settings > Web Search`.
2.  **Paramètres Recommandés** :
    *   **Search Engine** : Tavily.
    *   **Tavily API Key** : Votre clé.
    *   **Search Depth** : `Advanced` (pour des rapports d'ingénierie précis).
    *   **Max Results** : 5.
3.  **Utilisation** : Dans le chat, activez l'icône "Web Search".

---

## 6. Étape 5 : Configuration de l'Outil RAG (Open WebUI)
Pour que l'IA puisse "appeler" votre base de documents locale, vous devez créer un **Tool**.

1.  **Accès** : Dans Open WebUI, allez dans `Workspace > Tools`.
2.  **Création** : Cliquez sur `+ New Tool`.
3.  **Code** : Copiez-collez le contenu de ce fichier :
    👉 [open_webui_lancedb_filter.py](../../code/scripts/ia/open_webui_lancedb_filter.py)
4.  **Enregistrement** : Cliquez sur `Save`. 
    *Note : Si vous avez une erreur "No Tools class found", vérifiez que vous avez bien copié la classe `class Tools:`.*

---

## 7. Étape 6 : Serveurs MCP (Accès Fichiers & Git)
Les serveurs MCP permettent à l'IA d'interagir directement avec votre système.

1.  **Accès Fichiers** (Lecture/Écriture) :
    ```bash
    # Recommandé (Node.js) :
    npx -y @modelcontextprotocol/server-filesystem "/Users/Shared/Mon Google Drive Physique/Documentation"
    
    # Alternative (Python) :
    # uvx filesystem-operations-mcp --root-dir "/Users/Shared/Mon Google Drive Physique/Documentation"
    ```
2.  **Accès Git** (Historique & Commits) :
    ```bash
    uvx mcp-server-git
    ```
    > [!NOTE]
    > **Attention** : Si vous lancez ces commandes à la main, il est normal de voir une erreur `JSONRPCMessage`. Ces serveurs doivent être configurés dans l'onglet **Integrations > MCP** d'Open WebUI pour fonctionner avec l'IA.
3.  **Action d'Audit Claude** : Créez une **Action** nommée "Audit Expert 🛡️" liée à Claude 4.7 Opus pour la validation finale.

---

## 8. Utilisation au Quotidien
Une fois configuré, votre workflow est le suivant :
1.  **Dégrossissage** : Qwen local cherche dans LanceDB + Web -> Proposition.
2.  **Audit** : Un clic sur le bouclier 🛡️ envoie la proposition à Claude pour certification.

---

*Guide d'installation final — Avril 2026.*
