# 💬 Usage du RAG avec les LLMs (vMLX & Antigravity)

Ce guide explique comment faire pour que vos modèles d'IA utilisent réellement la base de connaissances plutôt que de "halluciner" des réponses.

---

## 🏗️ Utilisation dans vMLX (Local)

Le modèle local (ex: Qwen-35B ou Mistral-119B) n'appelle pas toujours les outils de lui-même par défaut. 

### La "Phrase Magique"
Pour forcer l'usage du RAG, commencez votre question par :
> **"En utilisant tes outils RAG, réponds à : [Votre question]"**

### Les outils disponibles :
1.  **`rag_search`** : Pour les recherches générales.
2.  **`rag_analyze_impact`** : Pour les relations de cause à effet (ex: changement de moteur).
3.  **`rag_get_context`** : Pour extraire des spécifications techniques précises (couples, poids, dimensions).

### Interprétation des résultats
Depuis notre mise à jour, le serveur MCP renvoie des **extraits bruts**. Vous verrez apparaître des blocs comme :
`[Source 1: 15_Analyse_Biomecanique.md] [Score: 0.92] ...`
C'est normal et c'est ce qui permet au modèle d'être précis.

---

## 🛸 Utilisation dans Antigravity (Cloud)

Antigravity est nativement "Agentic". Il sait quand il a besoin de chercher dans la documentation. 

### Exemples de requêtes performantes :
- *"Antigravity, cherche dans le RAG quel est le ratio de réduction du genou et analyse si on peut porter 5kg de plus."*
- *"Vérifie dans la doc si le code audio `stt.py` est à jour avec la dernière version du RAG."*

---

## 🎯 Astuces pour de meilleures réponses

1.  **Soyez spécifique** : Au lieu de "le moteur", dites "le RS-04" ou "le moteur de hanche".
2.  **Demandez des preuves** : *"Donne-moi le couple du RS-04 et cite la source du RAG."*
3.  **Reformulez** : Si le RAG ne trouve rien, essayez de retirer les adjectifs (ex: au lieu de "le superbe pignon en alu", cherchez "pignon alu genou").
