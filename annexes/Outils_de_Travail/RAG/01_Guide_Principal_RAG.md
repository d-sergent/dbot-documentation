# 🤖 Guide Principal : D-Bot Graph RAG

Ce guide centralise toutes les instructions pour utiliser le système de recherche intelligente (RAG) du projet D-Bot. Le système utilise **LightRAG** (Graphe de connaissances + Vecteurs) et un **Reranker local** pour une précision maximale.

---

## 🚀 Commandes Rapides (Le Pense-Bête)

### 1. Mettre à jour la base (À faire quotidiennement)
Ajoute les nouveaux fichiers, schémas `.svg` (texte XML), PDF ou images modifiées, et purge proprement les fichiers archivés ou supprimés :

**Mode local recommandé (Ollama `qwen3.5:9b`, texte + vision, sans limite de quota) :**
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider ollama
```

**Mode cloud Gemini (cascade Flash/Lite) :**
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider gemini
```

**Mise à jour instantanée d'un seul fichier via MCP CLI :**
```bash
rag --index "01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md" --provider ollama
```

### 2. Poser une question technique en ligne de commande
Idéal pour une réponse ultra-rapide sans ouvrir d'interface.

```bash
# Recherche pure sans LLM (0 Go RAM GPU : injecte hl_keywords/ll_keywords puis repli naive garanti)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode hybrid "Votre question"

# Recherche hybride avec mots-cles explicites (contourne l'extraction LLM)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode hybrid --keywords "RB8016,RS-06,waist" "Votre question"

# Synthèse en cascade auto (Ollama -> Unsloth Studio -> Gemini -> OpenRouter)
# Demarre Ollama a la demande si aucun backend ne repond et l'arrete en fin de requete
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" "Votre question"

# Synthèse forcee via Unsloth Studio (:8888/v1) ou Ollama (:11434)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" "Votre question" --provider unsloth

# Liberer manuellement la memoire unifiee Ollama apres une session
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --stop-server
```

---

## 💬 Usage avec les LLMs

### Dans Kilo / Unsloth Studio & Ollama (Modèles locaux)
Le serveur MCP `dbot-rag` doit être actif. Pour forcer l'usage du RAG, utilisez cette syntaxe :
> *"Utilise l'outil `rag_search` pour me dire : [Votre question]"*

### Dans Antigravity (Cloud)
Antigravity a accès au même serveur MCP (`llm_mode="antigravity"` par défaut, 0 Go RAM LLM). Vous pouvez lui demander des analyses croisées complexes :
> *"Analyse l'impact d'un changement de batterie sur les moteurs RS-04 en utilisant le RAG."*

---

## 🛠️ Maintenance du Serveur MCP
Le serveur est situé ici : `Code/rag/mcp_lightrag_server.py`.
Si vous modifiez le code du serveur, n'oubliez pas de le **redémarrer** dans les réglages de votre client MCP.

### Fonctionnalités incluses :
- **Recherche Hybride sans LLM (`--search-only` / `antigravity`)** : Combine graphe (via mots-clés lexicaux `hl_keywords`/`ll_keywords`) et vecteurs sans charger de LLM en RAM.
- **Reranking Automatique** : Trie les résultats par pertinence réelle (`BAAI/bge-reranker-base`).
- **Cascade & Fallback Résilients** : Si le graphe ne trouve rien, bascule automatiquement en mode `naive` ; en synthèse `auto`, cascade `Ollama (qwen3.8:27b-mlx)` -> `Unsloth Studio (:8888/v1)` -> `Gemini` -> `OpenRouter` (côté MCP `internal` : `Gemini` -> `Ollama` avec démarrage/arrêt de session -> `Unsloth`).
- **Accès SVG XML & PDF garanti** : `.svg` et `.pdf` ne sont pas filtrés par `RAG_SKIP_IMAGES`.

---

## 📁 Dossiers Clés
- **Base de données** : `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db/`
- **Code source** : `/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/`
- **Logs d'indexation** : `/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/rag_indexing.log` (et `~/.ollama/logs/server.log` pour Ollama).
