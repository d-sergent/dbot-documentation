# ☁️ Étude : Indexation Cloud Hybride (Vitesse & Gratuité)

## 1. Pourquoi le Cloud pour l'indexation ?

L'indexation par LightRAG repose sur l'extraction d'entités et de relations par un LLM. En local (vMLX), cette tâche est séquentielle et lente (15-30 min pour D-Bot). 
L'utilisation d'une API Cloud permet :
- **Vitesse** : Traitement en 1 à 2 minutes.
- **Précision** : Modèles "Frontier" (Gemini 1.5 Pro, GPT-4o) plus performants pour structurer les données.
- **Parallélisme** : Possibilité d'envoyer plusieurs chunks simultanément.

---

## 2. Comparatif des Solutions "Free Tier" (Gratuites)

Pour le projet D-Bot, nous cherchons une solution qui permet d'indexer ~200-300 chunks gratuitement.

| Solution | Modèle recommandé | Limites Gratuites (Free Tier) | Verdict pour D-Bot |
| :--- | :--- | :--- | :--- |
| **Google Gemini API** | **Gemini 1.5 Flash** | 15 RPM / 1M TPM / 1500 RPD | 🏆 **Meilleur choix**. Très généreux, rapide et précis. |
| **Groq Cloud** | **Llama 3.1 70B** | 30 RPM / 1440 RPD | ✅ **Excellent**. Le plus rapide au monde, parfait pour l'extraction. |
| **OpenAI** | **GPT-4o mini** | Pas de Free Tier réel (système de crédits payants) | ❌ Trop coûteux pour un usage "hobby". |
| **Anthropic** | **Claude 3 Haiku** | Crédits limités | ❌ Moins généreux que Google/Groq. |

---

## 3. Stratégie d'Implémentation "Intelligente"

Pour maximiser l'efficacité sans dépenser un centime :

1.  **Embeddings Locaux (Toujours)** : On conserve `FastEmbed` sur le Mac. Envoyer des vecteurs sur le Cloud est inutile, lent et consomme des tokens.
2.  **Extraction Cloud (Optionnelle)** : On utilise Gemini ou Groq uniquement pour l'étape `extract_entities`.
3.  **Persistance Hybride** : La base de données reste stockée sur `/Users/Shared/`, peu importe le moteur qui a généré les données.
4.  **Compatibilité `--update`** : L'option Cloud ne traitera que les nouveaux fichiers, économisant ainsi les quotas d'API.

---

## 4. Configuration Recommandée

### Option A : Google Gemini (Recommandé)
- **Modèle** : `gemini-1.5-flash`
- **Avantage** : Fenêtre de contexte immense, très stable.
- **Configuration** : Clé API gratuite via [Google AI Studio](https://aistudio.google.com/).

### Option B : Groq
- **Modèle** : `llama-3.1-70b-versatile`
- **Avantage** : Vitesse fulgurante (latence quasi nulle).
- **Configuration** : Clé API via [Groq Console](https://console.groq.com/).

---

## 5. Estimation de consommation pour D-Bot

Sur une mise à jour typique de 5 fichiers (après une séance de travail) :
- **Nombre de chunks** : ~15 à 20.
- **Consommation Gemini** : ~25 000 tokens.
- **Coût** : **0,00 €** (largement en dessous du quota journalier de 1 500 requêtes).

---

## 6. Prochaines Étapes : Mise à jour du script

Le script `index_docs.py` sera modifié pour accepter les arguments :
- `--provider` : `local` (vMLX), `gemini` ou `openai-compatible`.
- `--api-key` : Votre clé secrète.
- `--model` : Le nom du modèle choisi.
