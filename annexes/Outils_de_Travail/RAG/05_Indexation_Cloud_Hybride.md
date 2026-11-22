# ☁️ Étude : Indexation Cloud Hybride (Vitesse & Gratuité)

## 1. Pourquoi le Cloud pour l'indexation ?

L'indexation par LightRAG repose sur l'extraction d'entités et de relations par un LLM. En local, elle requiert **`qwen3.8:27b-mlx`** (Ollama MLX) ou **`unsloth/Qwen3.8-27B-GGUF`** (Unsloth `:8888`) pour garantir `0` erreur de format `<|#|>`, ce qui prend quelques minutes à quelques dizaines de minutes selon le volume.
L'utilisation prioritaire des modèles **Gemini Free Tier en ligne** permet :
- **Vitesse** : Traitement en 1 à 2 minutes sur les mises à jour courantes.
- **Précision** : Cascade automatique sur les **`8` modèles Gemini Free Tier non-lite** (`gemini-3.8-flash` -> `gemini-4-hydrogen` -> `gemini-3.6-flash` -> `gemini-3-flash-preview` -> `gemini-flash-latest` -> `gemini-2.5-flash` -> `gemini-3.7-flash` -> `gemini-3.5-flash`, timeout borné `>= 10 s`) ; les variantes `-lite` (`3.5-flash-lite`, `3.1-flash-lite`, `flash-lite-latest`) sont écartées de l'indexation graphe après mesure d'une perte de `-77 %` à `-89 %` des relations (cf. [STUDY_Benchmarks_Indexation_RAG_20261121.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/STUDY_Benchmarks_Indexation_RAG_20261121.md)).
- **Continuité locale garantie** : Si les quotas Free Tier sont épuisés ou en pic `503`, `index_docs.py` bascule automatiquement sur **`ollama/qwen3.8:27b-mlx`**.

---

## 2. Comparatif des Solutions "Free Tier" (Gratuites)

Pour le projet D-Bot, nous utilisons en priorité la cascade Gemini Free Tier sur une mise à jour typique puis les replis locaux/OpenRouter gratuits (voir aussi l'option payante `--provider 1minai` défaut `mistral-small-latest` dans [STUDY_Benchmarks_Indexation_RAG_20261121.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/STUDY_Benchmarks_Indexation_RAG_20261121.md)) :

| Solution | Modèles retenus | Rôle dans D-Bot | Verdict pour D-Bot |
| :--- | :--- | :--- | :--- |
| **Google Gemini API (Free Tier)** | **Index : `8` non-lite** (`3.8-flash` -> `4-hydrogen` -> ... -> `3.5-flash`)<br>**QA & Audit : `3` `-lite`** (`3.1-flash-lite`, `3.5-flash-lite`, `flash-lite-latest`) | Prioritaire par défaut sur `index_docs.py`, `ask_rag.py`, `check_integrity.py` et MCP `auto`/`internal` | 🏆 **Choix principal en ligne** (séparation stricte `-lite` vs `non-lite`, hors Paid-only et `2.5-flash-lite` `404`). |
| **Passerelle `1min.ai`** | **QA & Audit (`auto` Palier 2) : `mistral-small-2603`**<br>**Index (`--provider 1minai`) : `mistral-small-latest`** | Palier 2 rapide par défaut pour **QA & Audit** ; option explicite (`--provider 1minai` / `--with-1minai`) en indexation | ⚡ **Ultra-rapide (`4,69 s` moy., `100 %` QA faisables & Audits `40 Ko+`)** quand Gemini Free Tier est saturé. |
| **Ollama Local MLX (`:11434`)** | **`qwen3.8:27b-mlx`** (index/vision) et **`gemma4:26b`** (QA & Audit) | Repli souverain automatique adapté à chaque tâche | ✅ **Indispensable hors-ligne / anti-quota & référence qualité graphe**. |
| **OpenRouter (`:free`)** | **`nvidia/nemotron-3-super-120b-a12b:free`**, `llama-3.3-70b-instruct:free` | Secours multi-modèles optionnel (`--provider online` / repli) | ⚠️ Utile en secours secondaire (débit variable). |

---

## 3. Stratégie d'Implémentation "Intelligente"

Pour maximiser l'efficacité sans dépenser un centime :

1. **Embeddings & Reranking toujours locaux** : `intfloat/multilingual-e5-large` et `BAAI/bge-reranker-base` tournent sur le Mac (`FastEmbed`), sans envoi de vecteurs dans le cloud.
2. **Cascade Cloud qualité en indexation** : `index_docs.py` balaie les `8` modèles Gemini Free Tier non-lite avant de basculer sans erreur sur `ollama/qwen3.8:27b-mlx`.
3. **Traçabilité complète** : chaque modèle gagnant et chaque bascule apparaissent dans `rag_indexing.log`, le terminal (`🧭`) et les réponses MCP (`> **Trace Moteur RAG** : ...`).
4. **Compatibilité `--update`** : ne traite que les fichiers nouveaux ou modifiés (`--update` actif par défaut).

---

## 4. Configuration Recommandée

### Priorité par défaut : Architecture Hybride à Deux Vitesses
- **Cascade QA & Audit rapide (`auto`)** : `gemini-3.1-flash-lite` -> `gemini-3.5-flash-lite` -> `gemini-flash-lite-latest` (`GEMINI_QA_TIMEOUT_S=15`) -> **`1min.ai` (`mistral-small-2603`)** -> **`Ollama gemma4:26b`** (sinon `qwen3.8:27b-mlx` -> Unsloth -> OpenRouter).
- **Cascade Indexation (non-lite, `0` crédit payant)** : `gemini-3.8-flash` -> `gemini-4-hydrogen` -> `gemini-3.6-flash` -> `gemini-3-flash-preview` -> `gemini-flash-latest` -> `gemini-2.5-flash` -> `gemini-3.7-flash` -> `gemini-3.5-flash` (`GEMINI_HTTP_TIMEOUT_S=60`) -> **`Ollama qwen3.8:27b-mlx`** (`think=False`).
- **Configuration** : Clé API gratuite via [Google AI Studio](https://aistudio.google.com/) (`GEMINI_API_KEY` et `ONEMINAI_API_KEY` dans `.env`).

### Option OpenRouter (`:free`)
- **Modèle par défaut** : `nvidia/nemotron-3-super-120b-a12b:free`
- **Usage** : `--provider online` ou `--provider openrouter`.

---

## 5. Estimation de consommation pour D-Bot

Sur une mise à jour typique de 5 fichiers (après une séance de travail) :
- **Nombre de chunks** : ~15 à 20.
- **Consommation Gemini** : ~25 000 tokens.
- **Coût** : **0,00 EUR** sur Free Tier (avec bascule transparente sur `qwen3.8:27b-mlx` en cas de saturation `429`/`503`).

---

## 6. Arguments CLI de `index_docs.py`

Le script `index_docs.py` accepte les arguments :
- `--provider` : `auto` (défaut : cascade complète Gemini Free Tier puis Ollama `qwen3.8:27b-mlx`), `ollama`, `gemini`, `unsloth` (`local`), `online` ou `openrouter`.
- `--thinking-level` : `minimal`, `low` (défaut), `medium`, `high` (repli auto sans `thinking_config` si `400 INVALID_ARGUMENT`).
- `--api-key` : Votre clé secrète si non définie dans `.env`.
- `--model` : Le nom du modèle à privilégier en tête de cascade.
