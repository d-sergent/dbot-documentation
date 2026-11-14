# Spécifications : Architecture IA Locale & Optimisation D-Bot

> [!NOTE]
> Document mis à jour sur l'architecture validée sur MacBook Pro M1 Max (`64 Go`). L'ancien socle `LM Studio / DeepSeek-R1 / Khoj / Qdrant` a été remplacé par le pipeline **LightRAG (`dbot-rag`)**, **Ollama MLX** et **Unsloth Studio**.  
> Référence opérationnelle détaillée : [00_GUIDE_IA_Locale_M1Max_64Go.md](../Annexes/Outils_de_Travail/IA_sur_Mac_M1_Pro_Max_64Go/00_GUIDE_IA_Locale_M1Max_64Go.md).

---

## 📑 Sommaire

- [1. Organisation Documentaire & RAG](#1-organisation-documentaire--rag)
- [2. Stratégie des Modèles & Moteurs Actifs](#2-stratégie-des-modèles--moteurs-actifs)
- [3. Workflow d'Exécution & Escalade Cloud](#3-workflow-dexécution--escalade-cloud)

---

## 1. Organisation Documentaire & RAG

La base documentaire du projet D-Bot suit une hiérarchie stricte destinée à garantir la fraîcheur des réponses RAG :

- **`00_Architecture_Centrale/`** : synthèses consolidées, dimensions et leviers mécaniques.
- **`01_` à `04_`** : dossiers thématiques (`FINAL_` / `DOSSIER_TECHNIQUE_` = vérité active ; `STUDY_` / `AUDIT_` = études et justifications).
- **`Archives/` et `00_Archives_Recherche/`** : exclus automatiquement de l'indexation LightRAG via `EXCLUDE_DIRS`.

### Solution d'Indexation : LightRAG via Serveur MCP (`dbot-rag`)

- **Moteur d'indexation** : [index_docs.py](../Code/rag/index_docs.py) (`--update --provider auto` par défaut : cascade Gemini puis repli Ollama local).
- **Serveur MCP** : [mcp_lightrag_server.py](../Code/rag/mcp_lightrag_server.py), configuré dans [kilo.jsonc](../.kilo/kilo.jsonc) sur la base `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db`.
- **Modèle d'embedding / reranking** : embeddings vectoriels + graphe LightRAG et reranking cross-encoder local (`BAAI/bge-reranker-v2-m3` / `TextCrossEncoder`).

---

## 2. Stratégie des Modèles & Moteurs Actifs

Deux moteurs et trois profils de modèles complémentaires couvrent l'ensemble des besoins locaux sur M1 Max (`64 Go`) sans swap SSD :

1. **Modèle Principal — `Qwen3.8-27B`** :
   - **Unsloth Studio (`http://127.0.0.1:8888/v1`)** : `unsloth/Qwen3.8-27B-GGUF` (`UD-Q4_K_XL` + `mmproj-F16.gguf`) pour orchestration agentique (Tool Healing), raisonnement et audit **Vision CAO**.
   - **Ollama MLX (`http://127.0.0.1:11434`)** : `qwen3.8:27b-mlx` (`18 Go`) pour indexation/synthèse LightRAG et inférence MLX rapide.
2. **Challenger Haute Vitesse — `Gemma 4 26B-A4B`** (`gemma4:26b`, `16 Go` `nvfp4`, `4B` actifs) sous Ollama MLX pour les échanges interactifs privilégiant la vitesse.
3. **Poids Plume Utilitaire — `qwen3.5:9b`** (`7,6 Go`) sous Ollama pour les tâches rapides à très faible empreinte VRAM.

---

## 3. Workflow d'Exécution & Escalade Cloud

1. **Interrogation et édition locale (Antigravity / Kilo + `dbot-rag`)** : l'agent s'appuie en priorité sur `rag_search`, `rag_get_context` et `rag_analyze_impact` pour extraire les cotes, références McMaster-Carr et calculs RDM exacts avant toute modification.
2. **Audit Vision CAO local** : analyse des planches [Visual_Snapshots](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots) via `Qwen3.8-27B` + `mmproj-F16.gguf` sous Unsloth Studio (`:8888`).
3. **Escalade Cloud** : pour les revues d'architecture multi-fichiers ou audits système critiques, bascule vers les modèles frontier Cloud via Antigravity ou la cascade Gemini configurée dans `index_docs.py`.
