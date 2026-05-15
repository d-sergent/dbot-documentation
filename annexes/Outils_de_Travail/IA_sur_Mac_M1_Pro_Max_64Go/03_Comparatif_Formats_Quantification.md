# Comparatif des Formats de Quantification (Mac Apple Silicon)

Sur Mac (M1/M2/M3), le choix du format de quantification est crucial pour équilibrer la **mémoire vive (RAM)**, la **vitesse** et l'**intelligence**. Voici le comparatif détaillé entre les standards industriels et les formats communautaires de pointe.

## 1. Tableau Récapitulatif

| Format | Type | Précision (IQ) | VRAM (30B) | Vitesse (Mac) | Usage Idéal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MXFP4** | Standard (FP4) | ⭐⭐⭐⭐⭐ | ~18 Go | 🚀🚀🚀🚀 | Intelligence maximale & standardisation. |
| **JANGTQ** | Adaptatif (Mixte) | ⭐⭐⭐⭐⭐ | ~15-18 Go | 🚀🚀🚀🚀 | Le meilleur ratio IQ / Go sur Mac. |
| **JANGQT2** | Agressif (2-bit) | ⭐⭐ | ~8-10 Go | 🚀🚀🚀🚀🚀 | Faire tenir des modèles géants (>100B). |
| **GGUF (Q4_K_M)** | Classique (INT4) | ⭐⭐⭐ | ~19 Go | 🚀🚀 | Compatibilité universelle (CPU/GPU). |

---

## 2. Analyse détaillée par format

### MXFP4 (Microscaling Floating Point 4-bit)
C'est le nouveau standard de l'industrie (OCP).
*   **Technique** : Utilise des nombres à virgule flottante sur 4 bits avec des facteurs d'échelle partagés par petits groupes.
*   **Points Forts** : Une fidélité au modèle original impressionnante. Il est nativement supporté par les derniers moteurs d'inférence (MLX).
*   **Points Faibles** : Quantification uniforme (toutes les parties du modèle sont compressées de la même façon).

### JANG / JANGTQ (Jang Adaptive N-bit Grading)
C'est le format "intelligent" de la communauté Mac.
*   **Technique** : C'est une quantification **adaptative**. Elle identifie les parties "sensibles" du cerveau du modèle (comme l'attention) et les garde en haute précision (6-8 bits), tandis qu'elle compresse agressivement les parties moins critiques (MLP) en 2-4 bits.
*   **Points Forts** : À poids égal, un modèle JANG est souvent plus "intelligent" qu'un modèle MXFP4 car il protège mieux ses neurones vitaux.
*   **Points Faibles** : Nécessite un "runtime" spécifique (souvent intégré dans Osaurus AI ou vMLX).

### JANGQT2 (La variante 2-bit)
La version "poids plume" pour les cas extrêmes.
*   **Technique** : Pousse la compression à l'extrême (moyenne de 2 bits par paramètre).
*   **Points Forts** : Permet de faire tourner un modèle de 120 milliards de paramètres (comme Mistral Large) sur un Mac qui n'a que 32 Go ou 48 Go de RAM.
*   **Points Faibles** : Perte de nuance marquée. Le modèle peut devenir répétitif ou faire des erreurs de syntaxe dans le code.

---

## 3. Quelle stratégie pour votre M1 Max 64 Go ?

Avec **64 Go de RAM**, vous êtes dans la position idéale : vous n'avez pas besoin de sacrifier l'intelligence pour la place.

1.  **Priorité 1 : JANGTQ ou MXFP4**
    *   Pour vos modèles de 30B à 70B (Gemma 4, Qwen 3.5), utilisez toujours ces formats. Ils prendront entre 15 et 35 Go, vous laissant assez de place pour un contexte de 128k tokens.
2.  **L'exception JANGQT2**
    *   Ne l'utilisez **que** si vous voulez tester des modèles dépassant les 150 milliards de paramètres. Pour tout ce qui est inférieur, le gain de place ne justifie pas la perte de QI.
3.  **Abliterated (CRACK)**
    *   Notez que le format (JANG ou MXFP) est indépendant de l'alignement. Vous pouvez avoir un `Gemma-MXFP4-CRACK` (le meilleur des deux mondes : précis et sans filtres).

---
*Document créé le 14 Mai 2026 — Guide de sélection de quantification pour configurations 64Go+.*
