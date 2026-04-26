# Architecture Agentic RAG Expert (Hybrid Local/Cloud)

Ce document définit l'architecture finale retenue pour le système de **RAG Agentique** du projet D-Bot sur MacBook Pro M1 Max 64 Go. Il remplace les études préliminaires par une solution optimisée, native et multi-session.

## 1. Concept et Objectifs
L'objectif est de transformer le LLM en un assistant expert capable de fusionner trois sources de savoir en un seul raisonnement :
1.  **Savoir Interne (Local)** : Vos PDFs techniques, datasheets et fichiers projets indexés dans une base vectorielle.
2.  **Savoir Externe (Web)** : Veille concurrentielle, prix et stocks en temps réel via des agents de recherche.
3.  **Savoir de Validation (Cloud)** : Audit critique par un modèle de classe mondiale (Claude 4.7 Opus) pour garantir la sécurité mécanique et thermique.

---

## 2. La "Stack" Technique Décidée (Native Mac)

Pour maximiser la RAM et la performance, nous avons banni Docker au profit d'une installation **Native Python**.

| Composant | Technologie | Rôle |
| :--- | :--- | :--- |
| **Moteur LLM** | **Ollama** | Inférence locale (Qwen 3.6 35B Q6/Q8). |
| **Embeddings** | **nomic-embed-text** | Vectorisation des documents locaux. |
| **Vector DB** | **LanceDB** (Shared) | Stockage ultra-rapide sur `/Users/Shared`. |
| **Reranker** | **Qwen3-Reranker** | Précision chirurgicale des résultats techniques. |
| **Interface** | **Open WebUI** | Chat, gestion des documents et des agents. |
| **Recherche Web** | **Tavily AI** | Recherche optimisée pour les LLM. |
| **Audit Expert** | **Claude 4.7 Opus** | Audit de sécurité et validation finale. |

---

## 3. Fonctionnement Multi-Session (Antigravity Bridge)
La stack est conçue pour être "transverse" entre vos sessions macOS :
*   **Session IA** : Héberge le serveur Ollama et l'interface Open WebUI pour isoler la charge RAM.
*   **Session Principale** : Permet à **Antigravity** d'accéder à la base LanceDB via le dossier partagé `/Users/Shared/AI_Shared_Knowledge/`.
*   **Pont de Données** : La base de connaissances est commune, permettant une collaboration fluide entre l'humain, l'agent de code (Antigravity) et l'agent de recherche (Qwen).

---

## 4. Workflow de Décision Robotique
1.  **Planification** : L'utilisateur pose une question complexe sur un design.
2.  **RAG Local** : LanceDB extrait les specs des moteurs en stock.
3.  **Recherche Web** : Tavily récupère les prix et délais chez les distributeurs (RS/Mouser).
4.  **Synthèse** : Qwen 3.6 rédige une proposition avec une **BOM (Bill of Materials)**.
5.  **Audit de Sûreté** : Un clic sur le bouton **🛡️ Audit** envoie la synthèse à Claude 4.7 Opus pour une validation des marges de sécurité et des risques de panne.

---

*Document de référence final — Architecture RAG D-Bot — Avril 2026.*
