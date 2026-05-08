# 🤖 Guide Principal : D-Bot Graph RAG

Ce guide centralise toutes les instructions pour utiliser le système de recherche intelligente (RAG) du projet D-Bot. Le système utilise **LightRAG** (Graphe de connaissances + Vecteurs) et un **Reranker local** pour une précision maximale.

---

## 🚀 Commandes Rapides (Le Pense-Bête)

### 1. Mettre à jour la base (À faire quotidiennement)
Ajoute les nouveaux fichiers ou les modifications du jour à la mémoire du robot.
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/index_docs.py" --update
```

### 2. Poser une question technique en ligne de commande
Idéal pour une réponse ultra-rapide sans ouvrir d'interface.

```bash
# Recherche pure (affiche les extraits sans utiliser de LLM)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/ask_rag.py" "Votre question" --search-only

# Synthèse avec un modèle local (Qwen)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/ask_rag.py" "Votre question" --provider local

# Synthèse via OpenRouter avec Tencent Hunyuan 3 (Puissant et gratuit)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/ask_rag.py" "Votre question" --provider openrouter --model tencent/hy3-preview:free
```

---

## 💬 Usage avec les LLMs

### Dans vMLX (Modèles locaux)
Le serveur MCP doit être actif. Pour forcer l'usage du RAG, utilisez cette syntaxe :
> *"Utilise l'outil `rag_search` pour me dire : [Votre question]"*

### Dans Antigravity (Gemini/Cloud)
Antigravity a accès au même serveur MCP. Vous pouvez lui demander des analyses croisées complexes :
> *"Analyse l'impact d'un changement de batterie sur les moteurs RS-04 en utilisant le RAG."*

---

## 🛠️ Maintenance du Serveur MCP
Le serveur est situé ici : `code/rag/mcp_lightrag_server.py`.
Si vous modifiez le code du serveur, n'oubliez pas de le **redémarrer** dans les réglages de vMLX ou de votre client MCP.

### Fonctionnalités incluses :
- **Recherche Hybride** : Combine le graphe (relations) et les vecteurs (mots-clés).
- **Reranking Automatique** : Trie les résultats par pertinence réelle (modèle BGE-M3).
- **Fallback Résilient** : Si le graphe ne trouve rien, bascule automatiquement en mode "Naive" pour ne jamais vous laisser sans réponse.

---

## 📁 Dossiers Clés
- **Base de données** : `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db/`
- **Code source** : `/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/`
- **Logs vMLX** : À surveiller pour vérifier le chargement du Reranker et les scores de pertinence.
