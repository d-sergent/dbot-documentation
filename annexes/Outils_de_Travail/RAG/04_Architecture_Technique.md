# 🏗️ Architecture Technique du D-Bot RAG

Ce document détaille le fonctionnement "sous le capot" du système pour assurer sa pérennité technique.

---

## 🧩 Les 3 couches de recherche

Le système utilise une architecture dite **"Pipeline de Recherche Avancé"** en 3 étapes :

1.  **Couche Sémantique (Vecteurs)** : 
    - Utilise `intfloat/multilingual-e5-large`.
    - Trouve les passages qui partagent le même sens que la question.
    - Très robuste aux fautes de frappe ou aux synonymes.

2.  **Couche Structurelle (Graphe de Connaissances)** :
    - Utilise les relations `ENTITY -> RELATION -> ENTITY` extraites par le LLM.
    - Permet de relier des informations entre deux fichiers différents (ex: relier un moteur dans la liste d'achats à sa performance dans l'analyse biomécanique).

3.  **Couche de Raffinement (Reranking Local)** :
    - Utilise `BAAI/bge-reranker-v2-m3` via `fastembed`.
    - Trie manuellement les résultats pour s'assurer que les documents avec les scores les plus hauts sont réellement pertinents.

---

## 🛠️ Le Serveur MCP (`mcp_lightrag_server.py`)

C'est le "pont" entre le RAG et vos interfaces (vMLX, Antigravity).

### Caractéristiques de l'implémentation :
- **Mode Context-Only** : Le serveur renvoie le texte brut au LLM final pour éviter les appels circulaires et les erreurs de formatage JSON.
- **Async/Sync Parity** : Le moteur d'embedding est forcé en `async` pour garantir la compatibilité avec la boucle d'événements de LightRAG 1.4+.
- **Failsafe (Mode Naive)** : Si la recherche hybride (complexe) échoue, le serveur bascule automatiquement en recherche vectorielle simple pour garantir une réponse.

---

## 📊 Performance et Matériel
- **CPU** : L'embedding et le Reranking tournent intégralement sur le CPU du Mac (optimisé Apple Silicon).
- **RAM** : Le graphe en mémoire consomme environ 500 Mo à 1 Go selon la taille de la base.
- **Précision** : Le reranker local élimine environ 80% des résultats "presque" pertinents mais hors-sujet.

---

## 📝 Évolutions Futures Possibles
- **Intégration Vision** : Permettre au RAG d'indexer les schémas techniques (JPG/PNG).
- **SEA (Stiffness) Integration** : Ajouter des relations spécifiques pour les calculs de torsion SEA.
