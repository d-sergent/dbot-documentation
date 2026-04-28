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

Pour optimiser les 64 Go de RAM, la stack exploite plusieurs modèles simultanément, configurés dans le fichier `config.yaml` de l'extension Continue :

1.  **L'Expert Code (Lourd)** : `Qwen 3.6 35B` (MoE) ou `27B` (Dense). Utilisé pour résoudre les bugs complexes de ROS2.
2.  **L'Assistant Rapide (Léger)** : `Llama 3 8B`. Utilisé pour des questions rapides sans faire chauffer la machine.
3.  **Le Vectoriseur** : `nomic-embed-text`. Un tout petit modèle qui tourne en tâche de fond pour alimenter LanceDB.
4.  **L'Autocomplete** : `Starcoder 2 3B`. Prédit la prochaine ligne de code pendant la frappe.

---

## 4. Workflow de Développement Bipède

1.  **Recherche d'Information** : L'utilisateur demande à Continue comment intégrer un capteur LiDAR.
    *   *Commande* : `@tavily Trouve les specs du LiDAR Unitree L2 et @codebase regarde comment je l'intègre dans mes scripts actuels.*
2.  **Génération de Code** : Continue propose un script Python `lidar_driver.py`.
3.  **Exécution Autonome** : Si la tâche nécessite de modifier plusieurs fichiers et de tester, l'utilisateur passe sur **Roo Code** et demande :
    *   *"Crée le driver LiDAR, ajoute-le à l'architecture système, puis lance le script de test pour voir si les ports série répondent."*
4.  **Partage Multi-Session** : Le dossier `~/.continue` (contenant LanceDB) et les extensions VS Code sont stockés dans le dossier public `/Users/Shared/vscode-common` pour être accessibles par toutes les sessions macOS du M1 Max (voir le [Guide 48](./48_Configuration_VSCode_MultiSession_IA.md)).

---

*Document de référence final — Architecture IA VS Code D-Bot — Avril 2026.*
