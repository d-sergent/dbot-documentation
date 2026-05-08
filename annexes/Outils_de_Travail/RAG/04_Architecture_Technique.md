# 🏗️ Architecture Technique du D-Bot RAG

Ce document détaille le fonctionnement "sous le capot" du système pour assurer sa pérennité technique.

Ce document détaille le fonctionnement "sous le capot" du système pour assurer sa pérennité technique.

---

## 🏗️ Pourquoi cette Architecture ?

### Le problème du RAG classique pour D-Bot
Un RAG vectoriel classique (Qdrant ou LanceDB seul) répond bien à "qu'est-ce que dit la doc sur les bras ?", mais est **aveugle aux relations de cause à effet** entre documents différents. Si votre fichier `27_Etude_Epaule_Architecture.md` indique une masse de bras de 1.2 kg, et que `15d_Genou_et_Course.md` décrit les exigences de couple pour courir, un RAG classique ne fera jamais le lien entre ces deux informations.

### La solution : LightRAG (Graph RAG)
LightRAG combine deux types de mémoire :
1. **Vectorielle** : Recherche par similarité sémantique.
2. **Graphe de connaissances** : Relations entité → entité.

Lors de l'indexation, le système extrait des **entités** (composants, masses, couples, vitesses...) et leurs **relations** (impacte, limite, requiert, détermine...). Ces relations sont stockées dans un graphe qui permet des analyses d'impact croisées.

```
Exemple de graphe extrait de votre documentation :

[Bras Robot] ──pèse──> [1.2 kg]
[Masse Bras]  ──contribue_à──> [Masse Totale Robot]
[Masse Totale]──détermine──> [Couple Requis Cheville]
[Couple Requis]──limite──> [Vitesse de Course Max]
[Vitesse Course]──contraint──> [Moteur Genou RS06]
```

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
