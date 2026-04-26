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

### B. Installation de la Stack Python
Une fois le venv activé, lancez cette commande pour installer tous les outils :
```bash
pip3.11 install open-webui lancedb tantivy pypdf sentence-transformers flashrank tavily-python mcpo
```

### C. Optimisation Expert (Modelfile Ollama)
Pour maximiser les performances sur votre M1 Max et éviter les temps de rechargement :
1.  **Créez un fichier nommé `Modelfile`** :
    ```dockerfile
    FROM qwen3.6:35b-a3b
    # Force l'utilisation maximale du GPU Metal
    PARAMETER num_gpu 99
    # Contexte équilibré pour 64Go de RAM (64k tokens)
    PARAMETER num_ctx 64000
    # Garde le modèle en RAM pendant 24h
    PARAMETER keep_alive "24h"
    # Stop sequence
    PARAMETER stop "User:"
    ```
2.  **Créez votre modèle optimisé** :
    ```bash
    ollama create qwen-expert -f Modelfile
    ```

---

## 🧠 3. Intelligence Vectorielle (LanceDB & Reranking)
Cette couche permet à l'IA de "lire" vos documents PDF locaux et de trier les informations.

### A. Configuration du Re-ranker (Précision Technique)
Dans l'interface Open WebUI :
1.  Allez dans `Settings > Documents`.
2.  Activez le switch **Hybrid Search** (Indispensable pour voir les options).
3.  Champ **Reranking Model** : Saisissez exactement `BAAI/bge-reranker-v2-m3`.
4.  Réglages de précision : **Top K** : `10` / **Top K Reranker** : `5`.
5.  Cliquez sur **Save**.

---

## 🌐 4. Serveurs MCP (Accès Système via mcpo)
Cette section connecte votre IA à vos fichiers et à Git via un pont HTTP.

### A. Lancement des Services (Terminaux séparés)
> [!CAUTION]
> **Syntaxe Critique** : Ne pas utiliser le mot `run`. Utilisez `--` pour séparer les options de mcpo de la commande.

1.  **Service Fichiers** (Terminal 1) : 
    ```bash
    source "/Users/Shared/AI_Shared_Knowledge/open-webui-env/bin/activate"
    mcpo --port 8000 -- uvx filesystem-operations-mcp --root-dir "/Users/Shared/Mon Google Drive Physique/Documentation"
    ```
2.  **Service Git** (Terminal 2) : 
    ```bash
    source "/Users/Shared/AI_Shared_Knowledge/open-webui-env/bin/activate"
    mcpo --port 8001 -- uvx mcp-server-git -r "/Users/Shared/Mon Google Drive Physique/Documentation"
    ```

### B. Résolution des problèmes de Droits (User "ia")
Si un serveur (notamment Git) plante au démarrage, vérifiez les permissions :
```bash
# Test de lecture Git pour l'utilisateur courant
cd "/Users/Shared/Mon Google Drive Physique/Documentation"
git status
# Si erreur "Permission denied", débloquez le dossier :
sudo chmod -R 777 "/Users/Shared/Mon Google Drive Physique/Documentation"
```

### C. Déclaration dans l'interface Open WebUI
1.  Allez dans **⚙️ Admin Settings** → **External Tools**.
2.  Cliquez sur **+** (Add Server).
3.  **Type** : `MCP (Streamable HTTP)`. / **Auth** : `None`.
4.  **URL** : L'URL affichée par mcpo (ex: `http://localhost:8000`).

---

## ✅ 5. Validation & Workflow
1.  **Test Git** : *"Quels sont les 3 derniers commits ?"*
2.  **Test RAG** : *"Quelles sont les specs du bus CAN ?"*
3.  **Audit** : Utilisez le bouton **Audit Expert 🛡️** pour la validation finale via Claude 4.7.

---
*Guide d'installation final (Version 100% Python corrigée) — Avril 2026*
