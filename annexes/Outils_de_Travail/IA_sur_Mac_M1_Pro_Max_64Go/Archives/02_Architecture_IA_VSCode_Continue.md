# 02 - Architecture IA : VS Code, Continue & Ollama

> **Document de référence — Intelligence Artificielle D-Bot**
> Ce document définit l'architecture finale retenue pour le système IA du projet D-Bot sur MacBook Pro M1 Max 64 Go. Il remplace les études préliminaires par une solution unifiée, 100% intégrée à l'environnement de développement.

---

## 1. Concept et Objectifs
L'objectif est d'utiliser le Mac M1 Max comme une "Station de Contrôle IA" toute-puissante pour développer le robot. Au lieu d'avoir plusieurs interfaces distinctes (comme Open WebUI ou AnythingLLM), **toute l'intelligence est ramenée directement là où le code s'écrit : dans VS Code**.

Cette approche permet de fusionner :
1.  **L'Édition de Code** : Le robot est codé en Python/ROS2.
2.  **L'Indexation RAG** : L'IA lit automatiquement tous les schémas et scripts.
3.  **L'Exécution Autonome** : L'IA peut modifier les fichiers, exécuter des terminaux et tester le robot elle-même.

---

## 2. La "Stack" Technique (Avril 2026)

L'architecture est simplifiée au maximum pour garantir performance et stabilité.

| Composant | Technologie | Rôle |
| :--- | :--- | :--- |
| **Hub Central** | **VS Code** | L'éditeur où l'humain et l'IA collaborent. |
| **Moteur LLM Local** | **Ollama** | Fait tourner les modèles d'IA sur le GPU Metal (M1 Max). |
| **Assistant Chat & RAG** | **Continue** | Extension VS Code pour poser des questions, indexer la codebase (`@codebase`) et générer de l'autocomplete. |
| **Agent Autonome** | **Roo Code** | Extension VS Code qui peut écrire des scripts, créer des dossiers et lancer des commandes terminal de manière autonome. |
| **Recherche Web** | **Tavily AI (MCP)** | Connecté à Continue, permet aux modèles locaux (Ollama) de faire des recherches Internet pour trouver des specs techniques ou des prix. |
| **Vector DB (Index)** | **LanceDB** | Géré *nativement et de manière invisible* par l'extension Continue pour stocker la "mémoire" du projet. |

---

## 3. Le "Cerveau" : Gestion Multi-Modèles

Pour optimiser les 64 Go de RAM, la stack exploite plusieurs modèles simultanément, configurés dans le fichier `config.yaml` de l'extension Continue. 

### A. Le "Sweet Spot" (Équilibre Fluidité / Intelligence)
Il est fortement recommandé d'utiliser les modèles certifiés de la [bibliothèque officielle Ollama](https://ollama.com/library) pour garantir la compatibilité avec les outils (Tool Calling / Tavily).

*   **L'Expert MoE (Efficacité Agentique)** : `Qwen 3.6 35B-A3B`
    *   **Architecture** : Mixture of Experts (35B total, seulement 3B actifs par token).
    *   **Performances** : **73.4%** sur SWE-bench Verified.
    *   **RAM requise (Q8_0)** : ~36 Go (Laisse beaucoup de place pour le contexte RAG).
    *   **Installation** : `ollama pull qwen3.6:35b-a3b-q8_0`

*   **L'Expert Dense (Raisonnement Brut)** : `Qwen 3.6 27B`
    *   **Architecture** : Modèle dense (tous les paramètres sont actifs).
    *   **Performances** : **77.2%** sur SWE-bench Verified (Logique supérieure).
    *   **RAM requise (Q8_0)** : ~29 Go (Fluidité absolue sur M1 Max).
    *   **Installation** : `ollama pull qwen3.6:27b-q8_0`

### B. La "Limite Absolue" (Raisonnement Extrême)
Pour pousser les 64 Go de RAM dans leurs retranchements (max ~48 Go allouables au GPU sans swap), la limite est un modèle de 70B en 4-bit (Q4_K_M). Ils sont plus lents (5-10 tokens/sec) mais d'une logique inégalable pour l'ingénierie logicielle.

*   **Le Génie du Raisonnement** : `DeepSeek-R1-Distill-Llama-70B`
    *   **Architecture** : Modèle "Chain-of-Thought" (réfléchit avant de répondre).
    *   **Performances** : **~85%** sur SWE-bench Verified (Surpasse largement Qwen 3.6 27B).
    *   **RAM requise (Q4_K_M)** : ~42 Go.
    *   **Installation** : `ollama pull deepseek-r1:70b`

*   **L'Alternative Non-Censurée** : `R1-1776 70B`
    *   **Architecture** : Version "decensored" de DeepSeek-R1 par Perplexity AI (aucune limite de réponse).
    *   **Performances** : **~85%** sur SWE-bench Verified (Logique intacte).
    *   **RAM requise (Q4_K_M)** : ~42 Go.
    *   **Installation** : `ollama pull r1-1776:70b` (Source: [ollama.com/library/r1-1776](https://ollama.com/library/r1-1776))

*   **Le Couteau Suisse Ultime** : `Llama 3.3 70B`
    *   **Architecture** : Modèle dense de référence.
    *   **Performances** : **~75%** sur SWE-bench Verified. Ne perd jamais le fil.
    *   **RAM requise (Q4_K_M)** : ~41 Go.
    *   **Installation** : `ollama pull llama3.3:70b`

*   **Le Monstre du Code** : `Qwen 2.5 72B Instruct`
    *   **Architecture** : Modèle dense spécialisé code.
    *   **Performances** : **~77%** sur SWE-bench Verified.
    *   **RAM requise (Q4_K_M)** : ~43 Go.
    *   **Installation** : `ollama pull qwen2.5:72b`

### C. Les Modèles Utilitaires
*   **L'Assistant Rapide** : `Llama 3 8B`. Pour des questions basiques sans charger le GPU. (`ollama pull llama3`)
*   **Le Vectoriseur** : `nomic-embed-text`. Tourne en tâche de fond pour l'indexation LanceDB de la codebase. (`ollama pull nomic-embed-text`)
*   **L'Autocomplete** : `Starcoder 2 3B`. Prédit la prochaine ligne de code pendant la frappe. (`ollama pull starcoder2:3b`)

---

## 4. Comparatif de Puissance (Cloud vs Local Quantisé)

Afin de situer la puissance de notre "Station M1 Max" face aux géants du Cloud, voici un comparatif des performances de nos modèles locaux (après quantification pour tenir dans les 64 Go de RAM) face aux derniers modèles d'Anthropic (Avril 2026).

| Modèle (Avril 2026) | Type d'Hébergement | SWE-bench (Code) | MMLU (Logique) | Confidentialité | Coût |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Claude 4.7 Opus** | Cloud (API) | ~92% | ~90% | Serveurs US | $$$$ |
| **Claude 4.5 Sonnet** | Cloud (API) | ~88% | ~85% | Serveurs US | $$ |
| **DeepSeek-R1 70B (Q4)** | **Local (M1 Max)** | **~85%** | **~82%** | **Totale (100% Local)** | **Gratuit** |
| **Qwen 3.6 27B (Q8)** | **Local (M1 Max)** | **~77%** | **~76%** | **Totale (100% Local)** | **Gratuit** |
| **Llama 3.3 70B (Q4)** | **Local (M1 Max)** | **~75%** | **~80%** | **Totale (100% Local)** | **Gratuit** |
| **Qwen 3.6 35B-A3B (Q8)**| **Local (M1 Max)** | **~73%** | **~72%** | **Totale (100% Local)** | **Gratuit** |

> [!NOTE]
> La légère perte de performance due à la quantification (Q4/Q8) est largement compensée par la gratuité illimitée et la sécurité absolue de votre code source (le projet D-Bot n'est jamais envoyé sur internet).

---

## 5. Workflow de Développement Bipède

1.  **Recherche d'Information** : L'utilisateur demande à Continue comment intégrer un capteur LiDAR.
    *   *Commande* : `@tavily Trouve les specs du LiDAR Unitree L2 et @codebase regarde comment je l'intègre dans mes scripts actuels.*
2.  **Génération de Code** : Continue propose un script Python `lidar_driver.py`.
3.  **Exécution Autonome** : Si la tâche nécessite de modifier plusieurs fichiers et de tester, l'utilisateur passe sur **Roo Code** et demande :
    *   *"Crée le driver LiDAR, ajoute-le à l'architecture système, puis lance le script de test pour voir si les ports série répondent."*
4.  **Partage Multi-Session** : Le dossier `~/.continue` (contenant LanceDB) et les extensions VS Code sont stockés dans le dossier public `/Users/Shared/vscode-common` pour être accessibles par toutes les sessions macOS du M1 Max (voir le [Guide 48](./48_Configuration_VSCode_MultiSession_IA.md)).

---

*Document de référence final — Architecture IA VS Code D-Bot — Avril 2026.*
