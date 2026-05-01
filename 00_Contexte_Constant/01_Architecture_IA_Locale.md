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

## 2. Stratégie des Modèles (Le Duo LM Studio)

Pour concilier vitesse d'interaction MCP (outils) et profondeur de réflexion mécanique, nous adoptons une stratégie à deux modèles. Voici les liens exacts vers les meilleurs forks "Hugging Face" optimisés pour les Mac M1 Max sous LM Studio.

### A. Le "Scout" (Rapide, Spécialiste Outils MCP & Code)
*   **Rôle :** Interface quotidienne, requêtes RAG, recherches Web (Tavily), exécution d'outils. Il doit être extrêmement rigoureux sur le format JSON des outils.
*   **Modèles recommandés (Recherchez ces noms exacts dans LM Studio) :**
    1.  **Option Mistral (Le plus fiable pour le MCP) :** 
        `bartowski/Mistral-Small-24B-Instruct-2501-GGUF` (Privilégiez la version `Q4_K_M` ou `Q5_K_M`).
    2.  **Option Qwen (Le meilleur pour le code pur) :** 
        `mlx-community/Qwen2.5-Coder-14B-Instruct-4bit` (Version MLX native pour Apple Silicon, ultra rapide).

### B. L'"Architecte" (Raisonnement Profond & Cinématique)
*   **Rôle :** Résolution de problèmes complexes (physique, conception du D-Bot, logique mathématique).
*   **Spécificité :** Utilise la logique "Chain of Thought" (`<think>...</think>`). Il prendra 10 à 20 secondes à répondre, mais sa réflexion sera digne d'un bureau d'études.
*   **Modèles recommandés (Recherchez ces noms exacts dans LM Studio) :**
    1.  **L'Équilibre Parfait (32B) :** 
        `bartowski/DeepSeek-R1-Distill-Llama-32B-GGUF` (Version `Q4_K_M` ~19GB de VRAM). C'est le sommet de la réflexion locale actuelle.
    2.  **La Variante Qwen (32B) :**
        `bartowski/DeepSeek-R1-Distill-Qwen-32B-GGUF` (Excellent si le problème est fortement lié à du code logiciel complexe).

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
