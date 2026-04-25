## 1. Prérequis Système & Partage Multi-Session
Pour que la stack soit accessible depuis votre session principale (Antigravity) et votre session IA (Ollama/LMS), nous utilisons le répertoire partagé de macOS.

1.  **Création du dossier de savoir partagé** :
    ```bash
    mkdir -p "/Users/Shared/AI_Shared_Knowledge/lancedb"
    # Donner les accès aux deux sessions
    sudo chmod -R 777 "/Users/Shared/AI_Shared_Knowledge"
    ```
2.  **Homebrew & Python** : Installez-les via brew (voir section précédente).
3.  **uv** : `curl -LsSf https://astral.sh/uv/install.sh | sh`.

---

## 2. Étape 1 : Inférence Locale (Ollama)
... (Section inchangée) ...

---

## 3. Étape 2 : Interface Native (Open WebUI)
Nous installons Open WebUI en mode natif pour économiser la RAM.
1.  Créez un environnement dédié dans le dossier partagé (optionnel mais conseillé) :
    ```bash
    python3.11 -m venv "/Users/Shared/AI_Shared_Knowledge/open-webui-env"
    source "/Users/Shared/AI_Shared_Knowledge/open-webui-env/bin/activate"
    ```
2.  Installez Open WebUI et les dépendances RAG :
    ```bash
    pip install open-webui lancedb tantivy pypdf sentence-transformers flashrank
    ```
3.  Lancez le serveur :
    ```bash
    open-webui serve
    ```

---

## 4. Étape 3 : Recherche Agentique (Tavily & GPT Researcher)
... (Section inchangée) ...

---

## 5. Étape 4 : Fonctions Expertes (LanceDB Partagée)
Dans l'interface Open WebUI, créez une nouvelle **Function**. **IMPORTANT** : Modifiez le chemin de la base de données pour pointer vers le dossier partagé :

```python
# Dans votre classe Tools
self.db_path = "/Users/Shared/AI_Shared_Knowledge/lancedb"
self.docs_path = "/Users/Shared/Mon Google Drive Physique/Documentation" 
```

**Bénéfice** : Antigravity pourra exécuter des scripts de recherche directement sur ce dossier depuis votre session principale sans que vous ayez à basculer de session.

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
