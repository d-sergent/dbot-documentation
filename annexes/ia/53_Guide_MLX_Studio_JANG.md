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

## 3. Configuration & Intégration (Continue / Roo Code)

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
