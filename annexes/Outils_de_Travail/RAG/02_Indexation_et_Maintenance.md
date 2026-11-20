# 🛠️ Indexation et Maintenance du RAG

Pour que le RAG soit efficace, il doit refléter l'état actuel de votre documentation technique et de votre code.

---

## 📅 Routine d'Indexation

### 1. Mise à jour incrémentale (Recommandé)
**Fréquence : Quotidienne ou après chaque session de travail.**
Ce mode scanne uniquement les fichiers modifiés ou nouveaux (Markdown, Python, PDF Docling, schémas `.svg` en texte XML structuré, images VLM) et purge proprement du graphe les fichiers déplacés en archive (`00_Archives_Recherche`, `Archives`) ou supprimés (avec protection des homonymes).

**Via Ollama local sur M1 Max (`qwen3.5:9b`, texte + vision, 0 quota cloud) :**
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider ollama
```

**Via API Gemini (cascade automatique) :**
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --update --provider gemini
```

### 2. Ré-indexation complète
**Fréquence : Rare (une fois par mois ou si la base semble corrompue).**
Ce mode supprime toute la base de données et reconstruit tout le graphe de connaissances à partir de zéro.
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py" --full --provider ollama
```
*Note : En mode local Ollama (`qwen3.5:9b`, `think=False`, `max_async=1`), comptez ~7 à 9 s par appel LLM ; une base complète prend plusieurs dizaines de minutes sans risque d'erreur `429`.*

---

## 🔍 Vérification de la santé du système

Vous pouvez vérifier que la base est bien chargée en regardant les logs du serveur MCP au démarrage :
- **📊 Nodes/Edges** : Doivent être > 0 (généralement autour de 5000+ pour D-Bot).
- **✅ KV Storage** : Indique le nombre de documents indexés.
- **⚖️ Reranker** : Doit afficher `TextCrossEncoder` (`BAAI/bge-reranker-base`).

---

## ⚠️ Résolution de problèmes (Troubleshooting)

### "No relevant document chunks found"
Si le RAG ne trouve rien alors que l'info existe :
1. **Vérifiez le chemin** : Assurez-vous que `RAG_DB_PATH` dans `mcp_config.json` / `.kilo/kilo.jsonc` pointe bien vers `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db`.
2. **Relancez l'indexation** : Un petit `--update` peut suffire.
3. **Redémarrez le serveur MCP / libérez Ollama** : Rechargez la configuration MCP ou exécutez `ask_rag.py --stop-server` si un ancien démon local garde un modèle chargé en mémoire.

### Erreurs de "Asyncio / Await"
Si vous voyez des erreurs de type `An asyncio.Future is required` :
- Cela signifie qu'il y a un décalage entre la version de la bibliothèque et le code. Assurez-vous d'utiliser la version du serveur MCP mise à jour durant cette session (qui gère la parité `async` avec LightRAG 1.4).
