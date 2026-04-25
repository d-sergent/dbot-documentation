# Optimisation LLM Locale sur Mac Apple Silicon (M1/M2/M3)

Ce guide résume la stratégie d'optimisation pour faire tourner des modèles de langage (LLM) de grande taille (ex: 70B paramètres) sur une configuration haut de gamme type **MacBook Pro M1 Max 64 Go**.

## 1. La Stratégie de la Session Dédiée

Pour maximiser l'utilisation de la RAM unifiée (Unified Memory), il est recommandé de créer une **session utilisateur macOS dédiée à l'IA**.

### Pourquoi cette approche ?
*   **Nettoyage des ressources** : Élimine tous les processus gourmands en arrière-plan (Chrome, Slack, Docker, Indexation Spotlight).
*   **Maximisation de la VRAM** : Sur Mac, la RAM est partagée. Moins le système utilise de RAM pour l'interface, plus il en reste pour charger les poids du modèle et le cache de contexte (KV Cache).
*   **Contexte élevé** : Un contexte de 32k ou 128k tokens consomme énormément de VRAM supplémentaire par rapport aux poids fixes du modèle.

---

## 2. Le Workflow Optimal : "Shopping" vs "Inférence"

| Étape | Outil | Session | Pourquoi ? |
| :--- | :--- | :--- | :--- |
| **Recherche & Download** | **LM Studio** | Standard | Excellente interface pour explorer Hugging Face et tester rapidement. |
| **Inférence (Run)** | **LLMster (`lms`)** | **Dédiée IA** | La version "Headless" (sans GUI) de LM Studio. Très léger, idéal pour l'arrière-plan. |
| **Inférence (Alternative)** | **Ollama** | **Dédiée IA** | Très simple, gère son propre registre de modèles. |

### Partage des Modèles
Pour éviter de dupliquer les fichiers `.gguf` (très lourds), créez un dossier partagé entre les deux utilisateurs :
`📂 /Users/Shared/Models`

---

## 3. Interfaces Recommandées (GUI Light)

Une fois le moteur (Ollama ou LLMster) lancé dans votre session IA, vous pouvez utiliser une interface pour discuter. Voici les meilleures options pour Mac :

*   **Enchanted** (App Store) : Une application **native macOS** extrêmement légère et élégante. Parfait pour rester dans l'écosystème Apple sans consommer de RAM inutile.
*   **Chatbox** : Une application multi-plateforme très propre qui se connecte facilement aux API locales (Ollama/LMS).
*   **Open WebUI** (via Docker) : L'interface la plus puissante (proche de ChatGPT), mais plus lourde car elle nécessite Docker. Recommandée uniquement si vous avez besoin de fonctions avancées (RAG, gestion de documents).

---

## 4. GGUF vs MLX : Lequel choisir ?

Sur Apple Silicon, vous rencontrerez deux formats principaux. Voici comment choisir :

| Critère | **GGUF** (Ollama, LMS) | **MLX** (Natif Apple) |
| :--- | :--- | :--- |
| **Vitesse** | Très élevée | **Maximale (+20-30%)** |
| **Choix** | **Immense** (Tout Hugging Face) | Limité aux modèles récents |
| **Usage** | Stable, simple, universel | Expérimental, ultra-rapide |

**Règle d'or** : Privilégiez le **GGUF** pour l'intelligence et la diversité (modèles 30B+). Utilisez **MLX** si vous avez besoin d'une vitesse de lecture extrême sur des modèles plus petits ou des contextes géants.

---

## 5. Commande "Pro" : Libérer la limite de VRAM

Par défaut, macOS limite la mémoire allouée au GPU à environ **70-80%** de la RAM totale. Sur une machine de 64 Go, cela bride l'utilisation à ~48 Go. 

Pour repousser cette limite et dédier, par exemple, **56 Go** au GPU sur les 64 Go disponibles, utilisez la commande suivante dans le terminal de votre session dédiée :

```bash
# Vérifier la limite actuelle (en Mo)
sysctl iogpu.wired_limit_mb

# Augmenter la limite à 56 Go (56 * 1024 = 57344)
# Nécessite les droits sudo
sudo sysctl iogpu.wired_limit_mb=57344
```

> [!CAUTION]
> Ne poussez pas la limite à 100% de votre RAM. Le système a besoin de 4 à 8 Go pour ses fonctions vitales, sinon le Mac risque de "freezer" ou de redémarrer brutalement.

---

## 6. Recommandations de Modèles de Pointe (Avril 2026)

Avec 64 Go de RAM, vous pouvez faire tourner les modèles les plus récents sortis en ce mois d'avril 2026.

1.  **Qwen-3.6-35B (Instruct) - [RECOMMANDÉ Q6 ou Q8]** : Le "Sweet Spot" absolu pour 64 Go. 
    *   **Q6_K** (~30 Go) : Le meilleur rapport performance/poids.
    *   **Q8_0** (~36 Go) : Pour une précision chirurgicale (calculs de couple, cinématique) rivalisant avec Claude 4.
2.  **Llama-4-Scout (109B MoE / 17B actifs)** : **Le monstre du contexte**. Grâce à ses 10 millions de tokens de fenêtre de contexte, il peut "lire" l'intégralité de votre documentation et de votre code source simultanément. À utiliser en GGUF (Q4_K).
3.  **Qwen-3.6-27B (Dense)** : Une alternative ultra-rapide pour des réponses instantanées avec une précision chirurgicale.
4.  **Gemma-4-31B (Dense)** : **L'excellence multimodale**. À privilégier si vous intégrez des flux vidéo ou image (via OAK-D) dans vos réflexions IA.

---

## 7. Benchmarks : Local (M1 Max) vs Cloud (Anthropic)

Comparaison des performances (Avril 2026) pour percevoir le gap entre les modèles locaux et les fleurons du Cloud :

| Benchmark | Qwen 3.6 (35B) | Gemma 4 (31B) | Claude 3.5 Sonnet | Claude 4.6 Sonnet | **Claude 4.7 Opus** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **MMLU-Pro** | 86.8% | 85.2% | 84.1% | 89.3% | **94.2%** |
| **GPQA Diamond** | 84.8% | 84.3% | 79.4% | 89.9% | **95.1%** |
| **HumanEval (Code)**| 82.1% | 81.5% | 80.5% | 92.0% | **98.4%** |
| **Vision (MMMU)** | 74.2% | **76.9%** | 68.2% | 75.6% | **85.2%** |

> [!TIP]
> **Observation** : Le Qwen 3.6 local dépasse déjà le Claude 3.5 Sonnet Cloud dans presque tous les domaines techniques. Le gap avec Claude 4.7 Opus reste marqué pour le raisonnement de très haut niveau ("Zero-Fault"), mais l'absence de latence réseau rend le modèle local souvent plus productif pour l'itération rapide.

---

*Document mis à jour le 25 Avril 2026 — Intégration des benchmarks comparatifs Anthropic.*
