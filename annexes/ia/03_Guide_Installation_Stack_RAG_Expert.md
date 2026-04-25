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

## 4. Étape 3 : Recherche Web (Tavily AI)
Tavily est le "bras armé" de votre système sur Internet.

### A. Configuration Open WebUI (Usage Quotidien)
1.  **Activation** : Allez dans `Settings > Web Search`.
2.  **Paramètres Recommandés** :
    *   **Search Engine** : Tavily.
    *   **Tavily API Key** : Votre clé.
    *   **Search Depth** : `Advanced` (pour des rapports d'ingénierie précis).
    *   **Max Results** : 5 (excellent compromis coût/vitesse).
3.  **Utilisation** : Dans le chat, activez l'icône "Web Search". Qwen utilisera alors Tavily automatiquement si la question le nécessite.

### B. Usage Standalone (Script Python)
Si vous voulez effectuer une recherche rapide sans lancer l'interface graphique :
1.  **Installation** : `pip3.11 install tavily-python`.
2.  **Exécution du script** :
    ```bash
    export TAVILY_API_KEY="votre_clé_ici"
    python "/Users/Shared/Mon Google Drive Physique/Documentation/code/scripts/ia/test_tavily_search.py"
    ```
    *Ce script affiche une synthèse de la recherche et les sources les plus pertinentes.*

---

## 5. Étape 4 : Intelligence Vectorielle (LanceDB & Re-ranker)
LanceDB est la base de données qui stocke vos documents. Le Re-ranker est le modèle qui garantit la précision technique.

1.  **Installation des moteurs** (Dans votre venv `open-webui-env`) :
    ```bash
    pip3.11 install lancedb tantivy pypdf sentence-transformers flashrank
    ```
2.  **Configuration du Re-ranker (Optimisation Mac)** :
    Pour que le réordonnancement soit instantané, nous utilisons la puce graphique (GPU) de votre M1 Max.
    *   Modèle conseillé : `Qwen/Qwen3-Reranker-0.6B`.
    *   Accélération : Assurez-vous que `device='mps'` est spécifié dans vos scripts (Metal Performance Shaders).

---

## 6. Étape 5 : Vérification par Script (Standalone)
Avant de configurer l'interface, vérifiez que les moteurs accèdent bien à vos fichiers et au web.

1.  **Test LanceDB** :
    ```bash
    python "/Users/Shared/Mon Google Drive Physique/Documentation/code/scripts/ia/test_lancedb_rag.py"
    ```
2.  **Test Tavily** :
    ```bash
    python "/Users/Shared/Mon Google Drive Physique/Documentation/code/scripts/ia/test_tavily_search.py"
    ```

---

## 7. Étape 6 : Configuration de la Fonction RAG (Open WebUI)
Pour que l'interface utilise LanceDB, vous devez créer une "Function" (ou un "Tool") avec le code suivant.

1.  **Accès** : Dans Open WebUI, allez dans `Workspace > Tools` (ou `Functions`).
2.  **Création** : Cliquez sur `+ New Tool`.
3.  **Code** : Copiez le contenu du fichier suivant :
    👉 [open_webui_lancedb_filter.py](../../code/scripts/ia/open_webui_lancedb_filter.py)
4.  **Paramètres (Valves)** : Une fois enregistré, vérifiez les "Valves" pour pointer sur :
    *   `db_path`: `/Users/Shared/AI_Shared_Knowledge/lancedb`
    *   `collection_name`: `technical_docs`
5.  **Activation** : Dans n'importe quel nouveau chat, activez le filtre "LanceDB Expert RAG" via l'icône de réglages du modèle.

---

## 8. Étape 7 : Serveur MCP & Audit Claude
1.  **Accès Fichiers** : Lancez le serveur MCP pour vos projets :
    ```bash
    uvx mcp-server-filesystem "/Users/Shared/Mon Google Drive Physique/Documentation"
    ```
2.  **Action d'Audit** : Créez une **Action** nommée "Audit Expert 🛡️" liée à Claude 4.7 Opus pour la validation finale des calculs et de la sécurité.

---

## 9. Utilisation au Quotidien
Une fois configuré, votre workflow est le suivant :
1.  **Dégrossissage** : Qwen local cherche dans LanceDB + Web -> Proposition.
2.  **Audit** : Un clic sur le bouclier 🛡️ envoie la proposition à Claude pour certification.

---

*Guide d'installation final — Avril 2026.*
