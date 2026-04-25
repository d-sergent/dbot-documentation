# Architecture Agentic RAG Expert (Hybrid Local/Cloud)

Ce document décrit l'architecture cible pour transformer un MacBook Pro M1 Max 64 Go en une station d'ingénierie robotique augmentée par l'IA. Cette solution combine la puissance du local pour la confidentialité et l'extraction de données, et l'intelligence du Cloud pour la validation critique.

## 1. Vision d'Ensemble
L'architecture repose sur un concept d'**Agentic Research RAG**. Contrairement à un RAG classique qui "répond" simplement à partir d'un document, ce système planifie, cherche sur le web, compare avec les données locales et fait auditer ses conclusions par un second modèle expert.

---

## 2. Les Quatre Piliers de l'Intelligence

### A. L'Extraction Massive (Local)
*   **Moteur** : Ollama avec **Qwen 3.6 35B (Q6/Q8)**.
*   **Rôle** : Lecture exhaustive des documentations techniques (.pdf, .md, .docx), extraction de tableaux de spécifications (couples, courants, tensions) et rédaction initiale.
*   **Confidentialité** : 100% de vos documents restent sur le Mac.

### B. La Recherche Agentique (Web)
*   **Orchestrateur** : **GPT Researcher**.
*   **Moteur de Recherche** : **Tavily AI**.
*   **Rôle** : Veille technologique en temps réel, étude de la concurrence, recherche de prix et de délais (Lead Time) chez les distributeurs (RS, Mouser, Digi-Key).
*   **Outil** : **Crawl4AI** pour transformer les sites constructeurs en données structurées.

### C. La Mémoire de Précision (LanceDB + Re-ranking)
*   **Moteur Vectoriel** : **LanceDB** (Serverless, ultra-rapide sur Apple Silicon).
*   **Reranker** : **Qwen3-Reranker-0.6B**.
*   **Rôle** : Garantir que les 5 extraits fournis au LLM sont les plus pertinents techniquement (ex: ne pas confondre un couple nominal et un couple de pointe).

### D. L'Audit de Sûreté (Cloud)
*   **Expert Consultant** : **Claude 4.7 Opus** (via API).
*   **Rôle** : Audit final des propositions du modèle local. Vérification des marges de sécurité, de la cohérence thermique et de la viabilité du design.
*   **Sécurité** : Agit comme un garde-fou impitoyable face aux hallucinations potentielles du modèle local.

---

## 3. Schéma de Flux (Workflow)

1.  **Saisie** : "Conçois un axe de rotation pour une charge de 10kg avec les moteurs en stock."
2.  **Analyse Locale (MCP)** : Qwen parcourt votre dossier projet et votre base LanceDB (Datasheets).
3.  **Recherche Web (Tavily)** : L'agent vérifie si de nouveaux moteurs plus performants sont sortis en 2026.
4.  **Synthèse (Qwen 3.6)** : Rédaction d'une proposition avec tableaux comparatifs et estimation budgétaire (BOM).
5.  **Audit (Claude 4.7)** : L'utilisateur clique sur **🛡️ Audit**. Claude analyse la proposition, calcule les risques de surchauffe et valide (ou invalide) la solution.

---

## 4. Bilan des Ressources (Mac 64 Go)

| Composant | Allocation RAM | Technologie |
| :--- | :--- | :--- |
| **macOS + Système** | ~8 Go | Système |
| **Qwen 3.6 35B (Q6_K)** | **~30 Go** | Ollama |
| **LanceDB + Re-ranker** | ~1.5 Go | Python Native |
| **Open WebUI + MCP** | ~1 Go | Python Native |
| **KV Cache (Contexte)** | ~15-20 Go | VRAM Dynamique |
| **Marge de sécurité** | ~4-8 Go | - |

**Avantage décisif** : En restant en "Native Python", macOS gère la RAM de manière fluide via la *Unified Memory*, permettant d'allouer jusqu'à 56 Go au GPU si nécessaire pour des contextes géants.

---

*Document de référence — Architecture RAG Expert Robotique — Avril 2026.*
