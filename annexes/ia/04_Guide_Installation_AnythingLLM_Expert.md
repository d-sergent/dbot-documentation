# ⚡ Guide Rapide : Installation AnythingLLM Expert (Zéro Friction)

AnythingLLM Desktop est l'alternative "Tout-en-un" idéale si vous trouvez Open WebUI trop complexe à configurer. Il supporte nativement le protocole MCP (sans proxy) et utilise LanceDB en interne.

---

## 📥 1. Installation de base
1.  **Téléchargement** : Allez sur [useanything.com](https://useanything.com/) et téléchargez la version macOS (Apple Silicon).
2.  **Installation** : Glissez l'application dans votre dossier `Applications`.
3.  **Premier lancement** : Suivez l'assistant de configuration initiale.

---

## 🧠 2. Connexion aux Modèles (Ollama)
AnythingLLM va se connecter à votre instance Ollama déjà configurée.

1.  Allez dans **Settings** (icône clé à molette en bas à gauche) → **AI Providers**.
2.  **LLM Provider** : Sélectionnez `Ollama`.
3.  **Ollama URL** : `http://127.0.0.1:11434`.
4.  **Model** : Sélectionnez votre modèle (ex: `qwen-expert` que nous avons créé).
5.  **Token context window** : Réglez sur `64000` (conforme à notre optimisation).

---

## 📁 3. Gestion documentaire (RAG via LanceDB)
AnythingLLM utilise LanceDB par défaut pour indexer vos fichiers.

1.  Créez un **Workspace** (ex: `D-Bot-Docs`).
2.  Cliquez sur le bouton "Upload" (icône nuage).
3.  Déposez vos dossiers de documentation (`/Users/Shared/Mon Google Drive Physique/Documentation`).
4.  Cliquez sur **Move to Workspace** puis **Save and Embed**.
    *L'IA a maintenant accès à tous vos fichiers avec une recherche vectorielle ultra-rapide.*

---

## 🌐 4. Recherche Web (Tavily AI)
Plus besoin de plugins complexes, c'est intégré.

1.  Allez dans **Settings** → **Tools**.
2.  Cherchez la section **Google Search / Tavily**.
3.  **Search Provider** : Sélectionnez `Tavily`.
4.  Saisissez votre clé API Tavily.
5.  Dans votre Workspace, activez l'outil "Web Search" dans les paramètres.

---

## 🛠️ 5. Serveurs MCP (Le point fort : Pas de mcpo !)
AnythingLLM Desktop peut parler directement aux serveurs MCP en `stdio`.

1.  Allez dans **Settings** → **Tools** → **MCP Servers**.
2.  Cliquez sur **Add MCP Server**.
3.  **Configuration Git** :
    *   **Name** : `LocalGit`
    *   **Mode** : `stdio`
    *   **Command** : `uvx`
    *   **Args** : `mcp-server-git -r "/Users/Shared/Mon Google Drive Physique/Documentation"`
4.  **Configuration Filesystem** :
    *   **Name** : `LocalFiles`
    *   **Mode** : `stdio`
    *   **Command** : `uvx`
    *   **Args** : `filesystem-operations-mcp --root-dir "/Users/Shared/Mon Google Drive Physique/Documentation"`

---

## ✅ 6. Validation
Dans votre Workspace, posez ces questions :
1.  *"Fais une recherche web sur les dernières nouveautés du bus CAN InnoMaker."* (Test Tavily)
2.  *"Quels sont les derniers commits du dossier Documentation ?"* (Test MCP Git)
3.  *"Analyse mes PDFs et donne-moi les specs de la liaison CAN."* (Test RAG/LanceDB)

---
*Guide AnythingLLM Expert — Version Avril 2026*
