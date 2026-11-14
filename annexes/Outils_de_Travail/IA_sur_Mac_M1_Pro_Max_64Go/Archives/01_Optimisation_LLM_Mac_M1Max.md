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

### 7.1 Comparatif Général (Modèles Denses)

| Benchmark | Qwen 3.6 (35B) | Gemma 4 (31B) | Claude 3.5 Sonnet | Claude 4.6 Sonnet | **Claude 4.7 Opus** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **MMLU-Pro** | 86.8% | 85.2% | 84.1% | 89.3% | **94.2%** |
| **GPQA Diamond** | 84.8% | 84.3% | 79.4% | 89.9% | **95.1%** |
| **HumanEval (Code)**| 82.1% | 81.5% | 80.5% | 92.0% | **98.4%** |
| **Vision (MMMU)** | 74.2% | **76.9%** | 68.2% | 75.6% | **85.2%** |

### 7.2 Comparatif Spécifique : Votre Bibliothèque JANG/MLX

*Note : Les données marquées "N/D" (Non Disponible) signifient que les benchmarks officiels stricts pour ces versions spécifiques (modèles JANG 2-bit/4-bit, CRACK ou futures versions fictives) n'ont pas été publiés sur internet ou diffèrent selon la quantification.*

| Benchmark | DeepSeek-R1 (32B) | Qwen 3.5 (122B 2-bit) | Mistral 4 (119B 2-bit) | Nemotron 3 Nano (30B) | MiniMax M2.7 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **MMLU-Pro** | 73.9% | N/D | N/D | N/D | N/D |
| **GPQA Diamond** | 61.5% | N/D | N/D | N/D | N/D |
| **HumanEval (Code)**| 80.7% | N/D | N/D | N/D | N/D |
| **Vision (MMMU)** | N/A (Texte pur) | N/D | N/D | N/D (Audio/Texte) | N/D |

### 7.3 Performances des Modèles de Base (Non-Quantifiés)

Voici les métriques de référence (FP16/BF16) pour les modèles bruts qui servent de fondation à votre bibliothèque :

| Benchmark | Qwen 3.5 (122B) | Mistral Small 4 (119B) | Nemotron 3 Nano (30B) | **Gemma 4 (31B Dense)** | **Gemma 4 (26B MoE)** | **MiniMax M2.7** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **MMLU-Pro** | 86.1% | 78.0% | ~86.1% | 85.2% | 81.5% | **~87.2%** |
| **GPQA Diamond** | 86.6% | 71.2% | N/D | 84.3% | 82.3% | **87.4%** |
| **HumanEval (Code)**| 41.6% | (LiveCodeBench+) | **78.05%** | 81.5% | 77.1% | (56.2% SWE-Pro) |
| **Paramètres Actifs**| 10B | 6.5B | 3B | **31B** | **4B** | N/D |

### 7.4 Comprendre les Benchmarks et la Taille des Modèles

#### Définition des métriques :
*   **MMLU-Pro** : Test de culture générale académique multi-disciplinaire (Maths, Droit, Histoire, etc.). Conçu pour être très difficile afin d'éliminer la réussite par "chance" des QCM.
*   **GPQA Diamond** : Le "boss final" du raisonnement. Questions de sciences de niveau doctorat (Physique, Bio, Chimie). Même des experts humains avec un PhD dans un autre domaine échouent souvent à ce test.
*   **HumanEval** : Test de génération de code Python. Le modèle doit écrire le corps d'une fonction à partir d'une consigne. Le score est le pourcentage de réussite aux tests unitaires automatisés.

> [!NOTE]
> **Le Paradoxe de la Densité (30B vs 122B)** : 
> Comment le **Nemotron 30B** peut-il égaler le **Qwen 122B** sur le MMLU-Pro ? 
> C'est une question de **densité de connaissances**. Le Nemotron est un "Spécialiste Optimisé" : il a été entraîné sur des données extrêmement triées et "sur-apprises" pour saturer sa mémoire de connaissances académiques. Le Qwen 122B est un "Géant Généraliste" : il a plus de "place" pour stocker des nuances complexes et du raisonnement de fond, même si ses scores aux QCM académiques sont similaires. 
> **En pratique** : Pour une question de cours, ils se valent. Pour un problème de conception inédit, le 122B sera bien plus robuste.

#### Comparaison Spécifique : Gemma 4 (31B Dense vs 26B MoE)

La famille Gemma 4 propose deux approches radicalement différentes :
*   **Gemma 4 31B (Dense)** : Le moteur de raisonnement pur. Il utilise ses 31 milliards de paramètres pour chaque mot généré. C'est le plus **intelligent** (meilleurs scores GPQA et Code), mais il est plus lent.
*   **Gemma 4 26B-A4B (MoE)** : Le moteur d'efficacité. Bien qu'il ait 26B de paramètres au total, il n'en active que **4B** par mot. Il est **5 à 8 fois plus rapide** que le 31B, tout en restant à seulement ~2-3% de ses performances intellectuelles. 

**Verdict** : Pour votre Mac M1 Max, la version **31B Dense** est la plus "performante" intellectuellement, mais la version **26B MoE** est la plus "performante" pour un usage fluide au quotidien.

> [!IMPORTANT]
> **Hiérarchie de l'Intelligence et Quantification** : 
> Peut-on considérer que les modèles quantifiés vont suivre le même ordre d'intelligence ? **Oui, dans 90% des cas.** Un Qwen 122B même écrasé en 2-bit restera fondamentalement plus intelligent, nuancé et cultivé qu'un modèle de 9B en 8-bit. La quantification (JANG/GGUF) retire de la *précision mathématique*, pas de la *connaissance*. 
> 
> **Les exceptions (La perte en 2-bit) :**
> *   **Le Code et les Mathématiques** : C'est là que la quantification agressive (2-bit) fait le plus de dégâts. Un petit modèle 30B en 8-bit (comme le DeepSeek R1) fera souvent un meilleur code qu'un monstre de 120B en 2-bit, car le code demande une syntaxe exacte où une perte de précision sur un seul token détruit la fonction.
> *   **La Cohérence à long terme** : Sur des textes très longs, un modèle 2-bit (non optimisé avec des formats mixtes comme le JANG_K) peut se mettre à bégayer ou tourner en boucle, chose que le modèle de base ne fait jamais.
> 
> **En résumé :** Pour de la discussion, de la culture G, ou de l'analyse sémantique, l'ordre de base est respecté. Pour du code ou des maths exacts, privilégiez les modèles quantifiés au minimum en 4-bit (JANG4/Q4), même s'ils sont plus petits.

---

*Document mis à jour le 14 Mai 2026 — Intégration de l'inventaire JANG/MLX et analyse approfondie des benchmarks.*
