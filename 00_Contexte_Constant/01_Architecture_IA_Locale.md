# Spécifications : Architecture IA Locale & Optimisation D-Bot

Ce document définit l'architecture de travail pour l'utilisation d'IA locales (via LM Studio) appliquées à la conception et au développement du projet robotique D-Bot.

---

## 1. Réorganisation de la Documentation

Pour optimiser le contexte de l'IA (le "KV Cache") et éviter de saturer la mémoire avec les 50 documents actuels, l'arborescence sera structurée hiérarchiquement :

*   **`00_Contexte_Constant/`** : Un résumé ultra-condensé (architecture globale, état actuel, contraintes matérielles). C'est le *seul* dossier qui pourra être injecté manuellement en permanence pour orienter le modèle.
*   **`01_Dossier_Etudes/`** : Historique des recherches, justifications des choix d'ingénierie (ex: moteurs RS-06 vs RS-03, choix de la courroie GT3).
*   **`02_Implementation/`** : Code source C++, Python, scripts de configuration et architecture logicielle.
*   **`03_Annexes/`** : Tutoriels, méthodologies, datasheets brutes.

### Solution d'Indexation (Le "RAG" Local via MCP)
**Objectif :** Permettre à l'IA de trouver l'information pertinente instantanément sans relire les 50 fichiers.
**Choix Technologique : Serveur MCP Vectoriel (RAG)**
*   Au lieu d'utiliser l'outil `filesystem` basique, nous utiliserons un Serveur MCP spécialisé en RAG (comme *Khoj* ou un script MCP *Qdrant* local).
*   **Fonctionnement :** Une base vectorielle indexe en arrière-plan les dossiers `01` et `02`. Quand le modèle a besoin d'info, il appelle l'outil MCP de recherche sémantique.
*   *Modèle d'embedding recommandé :* `nomic-embed-text` (ultra-léger et rapide).

---

## 2. Stratégie des Modèles (Le Duo LM Studio / MLX)

Pour concilier vitesse d'interaction MCP (outils) et profondeur de réflexion mécanique, nous adoptons une stratégie à deux modèles. Voici les meilleures options optimisées pour un Mac M1 Max (64 Go).

### A. Le "Scout" / L'Exécuteur (Rapide, Spécialiste Outils MCP & Code)
*   **Rôle :** Interface quotidienne, requêtes RAG, recherches Web (Tavily), exécution d'outils. Il doit être extrêmement rigoureux sur le format JSON des outils et rapide. Ne possède pas de balise `<think>`.
*   **Modèles recommandés :**
    1.  **L'Agent Ultime (35B/27B) :** 
        `mlx-community/Qwen3.6-35B-4bit` (ou la variante 27B). Le sommet pour l'usage intensif d'outils (MCP) avec une excellente culture générale, tout en restant très rapide grâce au format MLX natif Apple.
    2.  **Le Sprinter (14B) :** 
        `mlx-community/Qwen2.5-Coder-14B-Instruct-4bit`. Ultra rapide et agréable au quotidien, parfait pour du code pur ou des tâches simples.
    3.  **L'Option Mistral (24B) :** 
        `bartowski/Mistral-Small-24B-Instruct-2501-GGUF` (`Q4_K_M`). L'alternative européenne, très fiable et rigoureuse.

### B. L'"Architecte" (Raisonnement Profond, Mécanique & Cinématique)
*   **Rôle :** Résolution de problèmes d'ingénierie complexes (calculs de couple, choix de matériaux, physique, conception du D-Bot).
*   **Spécificité :** Utilise la logique "Chain of Thought" (`<think>...</think>`). Il prendra son temps pour éviter les hallucinations mathématiques.
*   **Modèles recommandés :**
    1.  **L'Équilibre Parfait Physique/Calculs (32B) :** 
        `bartowski/DeepSeek-R1-Distill-Qwen-32B-GGUF` (Version `Q4_K_M` ~19GB). Le meilleur ratio Vitesse/Intelligence. (Note : Llama n'existe pas en 32B natif, c'est l'architecture Qwen qui domine cette catégorie).
    2.  **L'Encyclopédie Industrielle & Matériaux (70B MLX) :**
        `mlx-community/deepseek-r1-distill-llama-70b-4bit`. Le "Graal" pour brainstormer sur l'usinage CNC ou des choix structurels complexes. Le format MLX permet à ce monstre de tourner de manière fluide sur M1 Max, moyennant environ 40 Go de RAM unifiée.
    3.  **L'Alternative Généraliste (27B) :**
        `bartowski/gemma-2-27b-it-GGUF`. Sans balise think, mais doté d'une culture académique redoutable pour lier l'électronique et la mécanique, sans être aussi lourd qu'un 70B.

---

## 3. Workflow & Intégration Cloud (Hybride)
*   Le travail quotidien, la recherche documentaire et la génération de code se font à 100% en local et gratuitement via **LM Studio + MCP** avec les modèles "Scout".
*   **Escalade Cloud :** Lors de "Checkpoints" majeurs du projet (ex: validation de l'architecture de la cheville ou du multi-room audio), une session sera ouverte avec un modèle cloud (Claude 3.5 Sonnet / Opus / GPT-4o) pour une revue d'expert.

---

## 4. Prochaines Étapes Techniques (À réaliser ensemble)
1.  **Restructuration Git :** Créer la nouvelle arborescence des dossiers (`00` à `03`) et y déplacer les 50 fichiers actuels.
2.  **Téléchargement des Modèles :** Récupérer le *Scout* (Mistral-Small) et l'*Architecte* (R1-Llama-32B) dans LM Studio via les liens HuggingFace fournis.
3.  **Choix et Installation de l'Indexeur (RAG) :** Définir et installer le serveur MCP qui gérera la base de données vectorielle pour remplacer la recherche basique par une recherche sémantique.
4.  **Tests de Charge :** Lancer le modèle 32B dans LM Studio et vérifier l'occupation de la mémoire unifiée sur le M1 Max (ajustement du *GPU Offload* si nécessaire).
