# RAG Local et Recherche Web Augmentée

Ce guide documente la mise en place d'un système de **RAG (Retrieval-Augmented Generation)** sur Mac Apple Silicon, permettant de coupler la puissance d'un LLM local avec vos documents personnels et des recherches web en temps réel.

## 1. Concept et Objectifs

L'objectif est de transformer le LLM en un assistant expert capable de :
1.  **Consulter vos documents locaux** (PDF, Markdown, Excel, Docx) pour répondre à des questions précises sur vos projets.
2.  **Effectuer des recherches Web** pour compléter ses connaissances avec des informations à jour (News, nouvelles versions de logiciels, cours de bourse, etc.).
3.  **Garantir la confidentialité** : Le traitement des documents et l'inférence restent 100% locaux. Seules les requêtes de recherche web (anonymisées) sortent vers l'extérieur.

---

## 2. Les Composants de la "Stack" RAG

| Composant | Rôle | Recommandation |
| :--- | :--- | :--- |
| **Moteur LLM** | Génération de la réponse | **Ollama** ou **LLMster** |
| **Embeddings** | Vectorisation des documents | **`nomic-embed-text`** (via Ollama) |
| **Vector DB** | Stockage de l'index des docs | **ChromaDB** ou **LanceDB** (souvent intégré) |
| **Search API** | Recherche sur Internet | **Tavily AI** (optimisé pour les LLM) |

---

## 3. Solutions Préconisées

### Option A : Open WebUI (La plus complète)
C'est l'interface la plus puissante, offrant une expérience proche de ChatGPT Plus.

*   **Installation (via Docker)** :
    ```bash
    docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
    ```
*   **Configuration Web Search** :
    1.  Aller dans `Settings > Web Search`.
    2.  Activer la recherche.
    3.  Choisir le moteur **Tavily** et entrer votre clé API (obtenue gratuitement sur [tavily.com](https://tavily.com)).

### Option B : AnythingLLM (La plus simple)
Une application "Desktop" tout-en-un qui gère l'indexation et la recherche sans Docker.
*   **Installation** : Téléchargement sur [useanything.com](https://useanything.com).
*   **Avantage** : Très intuitif pour gérer plusieurs "Workspaces" (un dossier par projet).

### Option C : Perplexica (Le clone de Perplexity)
Spécialisé dans la recherche d'informations massive et la synthèse de sources web.
*   **Installation** : Nécessite Docker Compose.
*   **Usage** : Idéal pour remplacer une recherche Google classique par une réponse structurée et sourcée.

---

## 4. Configuration Optimale (Mac 64 Go)

### Étape 1 : Préparer les Embeddings
Dans votre terminal (session IA), téléchargez le modèle qui servira à "lire" vos PDF :
```bash
ollama pull nomic-embed-text
```

### Étape 2 : Gestion de la RAM
Le RAG consomme de la VRAM supplémentaire pour stocker le contexte des documents retrouvés.
*   **Modèle LLM conseillé** : Utilisez **Llama-3-8B** ou **Mistral-7B** pour des recherches rapides, ou **Llama-3-70B** pour des synthèses très complexes.
*   **Limitation** : Si vous utilisez un modèle de 70B, assurez-vous d'avoir bien appliqué le guide [01 - Optimisation LLM](./01_Optimisation_LLM_Mac_M1Max.md) pour ne pas saturer la RAM avec le KV Cache.

### Étape 3 : Paramétrage de Tavily
Tavily permet de filtrer les résultats pour ne donner au LLM que du texte pur (sans HTML inutile). Dans Open WebUI, réglez le nombre de résultats de recherche sur **5 à 8** pour un bon compromis entre précision et rapidité.

---

## 5. Cas d'Usage D-Bot

Pour le développement du robot, ce système permet de :
*   Indexez toutes les **datasheets** des moteurs RobStride et de la Jetson.
*   Demander : *"Comment configurer le bus CAN sur JetPack 6 en m'appuyant sur mes documents ?"*.
*   Le LLM complètera avec une recherche web : *"Vérifie s'il y a eu des mises à jour du driver InnoMaker depuis Janvier 2026"*.

---

*Document créé en Avril 2026 — Architecture RAG Hybrid Local/Web.*
