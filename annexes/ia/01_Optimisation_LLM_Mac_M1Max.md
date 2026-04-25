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
| **Inférence (Run)** | **Ollama** ou **Llama.cpp** | **Dédiée IA** | Inférence "Lean" sans l'over-head d'une application Electron. |

### Partage des Modèles
Pour éviter de dupliquer les fichiers `.gguf` (très lourds), créez un dossier partagé entre les deux utilisateurs :
`📂 /Users/Shared/Models`

---

## 3. Commande "Pro" : Libérer la limite de VRAM

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

## 4. Recommandations de Modèles (Config 64 Go)

Sur un M1 Max 64 Go, les modèles suivants sont recommandés pour un équilibre parfait vitesse/intelligence :

1.  **Llama-3-70B-Instruct (Quantification Q4_K_M)** : Le modèle de référence pour la réflexion complexe.
2.  **Command R (35B)** : Excellent pour le RAG et les longs contextes.
3.  **Mistral Large** : Très puissant pour le code et le français.

---

*Document créé en Avril 2026 suite aux tests de performance sur D-Bot Brain.*
