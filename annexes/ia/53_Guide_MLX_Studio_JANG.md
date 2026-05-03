# 53 - Guide MLX Studio & Modèles Natifs Apple Silicon (JANG)

> **Document de référence — Intelligence Artificielle D-Bot**
> Ce guide détaille l'utilisation de `MLX Studio` comme moteur d'inférence de pointe sur Mac M1 Max (64 Go), en complément de LM Studio, pour exploiter des formats ultra-optimisés comme le JANG.

---

## 1. Pourquoi utiliser MLX Studio en plus de LM Studio ?

Bien que LM Studio supporte basiquement le format MLX, **MLX Studio** est construit *nativement* autour du framework d'Apple. Cela apporte des avantages techniques impossibles à obtenir autrement :

1. **Le Décodage Spéculatif Natif :** Sous LM Studio, le backend MLX désactive le décodage spéculatif. MLX Studio le gère parfaitement, multipliant par 2 ou 3 la vitesse de génération des gros modèles.
2. **Support Exclusif de la Compression JANG :** MLX Studio est le seul environnement GUI grand public capable de charger les modèles `JANG` (Jang Adaptive N-bit Grading), une compression asymétrique révolutionnaire.
3. **Mémoire Unifiée (`mmap`) Optimisée :** Le chargement en RAM des modèles de 40 Go est quasi instantané, et la mémoire est purgée immédiatement à la fermeture, évitant les crashs de swap fréquents sur LM Studio lors de gros chargements.
4. **Support VLM (Vision) natif :** Les pipelines d'analyse d'images fonctionnent de manière beaucoup plus fluide qu'avec le backend expérimental de LM Studio.

---

## 2. Le "Top 3" des Modèles Recommandés pour MLX Studio (M1 Max 64Go)

### A. L'Outil de Brainstorming Absolu (et VLM)
**Modèle :** `JANGQ-AI/Mistral-Small-4-119B-A6B-JANG_2L`
* **Le Secret :** C'est un modèle *Mixture of Experts* (MoE) de 119 Milliards de paramètres, compressé via JANG. Il n'active que 6B paramètres par token généré.
* **Avantage :** Il "pense" comme un géant mais s'exécute à la vitesse d'un petit modèle (30-40 tok/s). Il inclut la vision (Pixtral) et un mode de raisonnement `[THINK]`.
* **Limite :** La compression JANG à 2-bit peut causer des hallucinations sur les détails ultra-précis (datasheets très spécifiques) ou dégénérer sur des contextes MCP gigantesques.

### B. Le Cerveau d'Ingénierie Pur (La Référence)
**Modèle :** `mlx-community/DeepSeek-R1-Distill-Llama-70B-4bit`
* **Le Secret :** Le format 4-bit (non-JANG) préserve 100% de la logique mathématique. Sur MLX Studio, le décodage spéculatif lui donne une fluidité inespérée.
* **Avantage :** C'est l'encyclopédie mécanique par excellence. Parfait pour poser une équation de couple moteur (Nm) complexe sans aucune erreur.
* **Limite :** Très lourd (prend ~40 Go sur vos 64 Go), à lancer uniquement pour de gros problèmes d'architecture.

### C. L'Architecte Rapide (STEM)
**Modèle :** `mlx-community/DeepSeek-R1-Distill-Qwen-32B-4bit`
* **Le Secret :** Qwen est l'un des meilleurs modèles au monde en Sciences et Mathématiques. 
* **Avantage :** Avec ses 32B (18 Go de RAM), il laisse une marge de manœuvre immense pour vos autres applications et s'exécute à des vitesses fulgurantes.

---

## 3. Optimisation : Le Décodage Spéculatif (Draft Models)

Le décodage spéculatif permet de doubler (voire tripler) la vitesse de génération en utilisant un tout petit modèle ("Draft") qui "devine" les prochains mots, pendant que le gros modèle ("Target") ne fait que vérifier l'exactitude. 

**Règle d'or :** Le modèle brouillon doit **obligatoirement** faire partie de la même "famille" (même Tokenizer) que le modèle principal. 

Voici les recommandations basées sur les retours d'utilisateurs Apple Silicon (M-Series) :

### A. Pour le DeepSeek-R1-Llama-70B
C'est sur ce mastodonte que le décodage spéculatif est le plus vital.
*   **Draft Model idéal :** `mlx-community/Llama-3.2-1B-Instruct` (ou la version 3B).
*   *Pourquoi ?* Le DeepSeek 70B est basé sur l'architecture Llama 3. Le petit 1B va générer la syntaxe de base instantanément, et le 70B validera les concepts mécaniques complexes.

### B. Pour le DeepSeek-R1-Qwen-32B
*   **Draft Model idéal :** `mlx-community/Qwen2.5-0.5B-Instruct` (ou 1.5B).
*   *Pourquoi ?* Le 0.5B est minuscule (moins de 1 Go de RAM). Le coût en mémoire (overhead) est invisible et la vitesse s'envole.

### C. Ce qu'il ne faut PAS faire (Les pièges)
*   **Sur le Mistral-119B JANG :** Ne tentez **pas** le décodage spéculatif. C'est déjà un modèle MoE (qui n'utilise que 6B paramètres actifs) et son format JANG est particulier. Ajouter un modèle brouillon ralentirait le système.
*   **Sur le Mistral-Small 24B :** Il est déjà si rapide sur un M1 Max (50+ tok/s) que le coût de gestion de deux modèles en mémoire unifiée annule souvent le gain de vitesse. Le faire tourner seul est plus efficace.

---

## 4. Configuration & Intégration (Continue / Roo Code)

L'objectif est d'utiliser MLX Studio comme "Moteur Industriel" caché en arrière-plan, exactement comme LM Studio, pour qu'il réponde aux requêtes MCP de l'interface VS Code.

**Procédure :**
1. Installez et lancez [MLX Studio](https://mlx.studio).
2. Téléchargez vos modèles (les modèles `mlx-community` ou `JANGQ-AI`).
3. Démarrez le **Serveur API local** dans les paramètres de MLX Studio (vérifiez le port, généralement `8080` ou `1234`).
4. Modifiez votre fichier `config.yaml` de l'extension *Continue* pour pointer l'Architecte vers ce port :

```yaml
models:
  - title: "Architecte (MLX Studio)"
    provider: openai
    model: "mistral-small-4-jang" # ou le nom interne du modèle
    apiBase: "http://localhost:8080/v1" # Remplacer par le port de MLX Studio
```

**Workflow Relais :** 
Gardez LM Studio allumé avec votre **Qwen 35B (L'Exécuteur)** sur le port `1234` pour gérer les requêtes MCP avec fiabilité. Basculez sur le modèle **MLX Studio** directement dans le menu déroulant de *Continue* quand vous avez besoin d'une analyse profonde.

---

## 5. Résolution des problèmes (Troubleshooting)

### A. Freezes et SSD Swap (Modèles JANG)
Si un modèle comme le Mistral-119B ou le Qwen-122B fait "freezer" votre Mac, c'est que MLX Studio essaie d'allouer une fenêtre de contexte trop large (souvent 1 million de tokens par défaut), ce qui sature la RAM et déclenche le swap SSD.

**La Solution "Hard" (Bridage manuel) :**
Puisque l'interface ne propose pas toujours de réglage de "Context Length", j'ai bridé manuellement les modèles dans leurs fichiers de configuration respectifs :
*   **Action :** Modification de `"max_position_embeddings"` de `1048576` vers **`8192`**.
*   **Modèles patchés :**
    *   `Mistral-Small-119B` : [config.json](file:///Users/davidsergent/.cache/huggingface/hub/JANGQ-AI/Mistral-Small-4-119B-A6B-JANG_2L/config.json)
    *   `Qwen3.5-122B` : [config.json](file:///Users/davidsergent/.cache/huggingface/hub/JANGQ-AI/Qwen3.5-122B-A10B-JANG_2S/config.json)

### B. Erreurs de Template (Role Alternation)
Certains modèles sont extrêmement stricts sur l'alternance des rôles User/Assistant. J'ai patché les fichiers `chat_template.jinja` et `tokenizer_config.json` pour supprimer les alertes `TemplateError` bloquantes.

---

### C. Support des Outils (Tooling) sur DeepSeek-R1-32B
Par défaut, le template de chat du modèle DeepSeek-R1 Distill (Qwen) ne supporte pas nativement la variable `tools`, ce qui provoque des avertissements et une utilisation dégradée des outils MCP.

**Le Correctif (Patch de Template) :**
J'ai remplacé le `chat_template` dans le fichier `tokenizer_config.json` du modèle 32B pour inclure la logique XML `<tools>` et `<tool_call>`.
*   **Fichier modifié :** `/Users/davidsergent/.cache/huggingface/hub/mlx-community/DeepSeek-R1-Distill-Qwen-32B-4bit/tokenizer_config.json`
*   **Réglage vMLX :** Assurez-vous que le **"Tool Call Parser"** est réglé sur **`qwen`** ou **`auto`** dans les paramètres du serveur MLX Studio pour ce modèle.

---

## 6. Synthèse des Recommandations Finales (Mai 2026)

| Usage | Modèle Recommandé | Config Spéciale |
| :--- | :--- | :--- |
| **Brainstorming & Vision** | `Mistral-Small-119B JANG` | Context 8k (Fixé), No SSD Cache |
| **Ingénierie (Maths/Physique)** | `DeepSeek-R1-Llama-70B` | **Draft :** Llama-3.2-1B |
| **Code & MCP (VS Code)** | `Mistral-Small-24B-Abliterated` | Context 32k, Standalone |
| **Raisonnement & Outils** | `DeepSeek-R1-Qwen-32B` | **Patch Tooling**, **Draft :** Qwen-0.5B |

> [!TIP]
> Sur un M1 Max 64 Go, privilégiez le **Mistral-24B-Abliterated** pour vos agents autonomes (Roo Code / Continue). Pour des tâches nécessitant un haut niveau de raisonnement technique avec accès aux outils, le **DeepSeek-R1-Qwen-32B** patché est votre meilleure option.

