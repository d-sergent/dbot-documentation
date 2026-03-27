# Étude Matérielle : Orin vs Thor (Horizon 2026-2027)

## 1. Comparatif des Générations

| Caractéristique | Jetson AGX Orin (64 Go) | Jetson AGX Thor (128 Go) | Gain / Écart |
| :--- | :--- | :--- | :--- |
| **Architecture GPU** | Ampere (2020) | **Blackwell (2025)** | +1 Génération |
| **Puissance IA** | 275 TOPS (INT8) | **2070 TFLOPS (FP4)** | **~7.5×** |
| **RAM (Unifiée)** | 64 Go LPDDR5 | **128 Go LPDDR5X** | **2×** |
| **Bande Passante** | 204 Go/s | **273 Go/s** | +34% |
| **Consommation** | 15W - 60W | **40W - 130W** | +116% (Pointe) |
| **Disponibilité** | Immédiate | Limité (DevKit d'été 2025) | - |

## 2. Analyse Stratégique : L'approche "Remote Brain"

L'idée d'acheter une carte **maintenant** pour déporter les calculs OpenClaw pendant la phase d'étude est **excellente**.

### Avantages de l'achat immédiat (Orin 64 Go)
1. **Stabilité Logicielle** : JetPack 6.x est mature. Tout votre code ROS2 et OpenClaw tournera sans "essuyer les plâtres".
2. **Consommation/Autonomie** : La consommation de l'Orin (max 60W) est beaucoup plus gérable pour une batterie 13S embarquée que les 130W potentiels de la Thor.
3. **Coût** : L'Orin 64 Go se trouve à ~1900-2000$. La Thor sera probablement au-delà de 3000$.

### Avantages de l'attente (Thor 128 Go)
1. **LLM de Classe Mondiale** : 128 Go de RAM permettent de faire tourner des modèles de **70B paramètres** (Llama 3/4) avec une fluidité exceptionnelle.
2. **Physique AI** : Thor est optimisée nativement pour les "Foundation Models" de robotique (marche, manipulation).

## 3. Recommandation pour le D-Bot

> [!TIP]
> **Le Sweet Spot Immédiat :** Investissez dans une **Jetson AGX Orin 64 Go**. 
> - **Pourquoi :** C'est le standard actuel des robots humanoïdes les plus avancés (ex: K-Bot). 
> - **Usage :** Installez-la dans un petit boîtier sur votre bureau. Connectez votre Mac dessus en Ethernet. 
> - **Action :** Faites tourner OpenClaw et le serveur d'embeddings sur l'Orin. Votre Mac redevient fluide et vous testez "en conditions réelles" la latence de réflexion du robot.
> - **Futur :** Dans 2 ans, si le D-Bot a besoin d'un "Level Up", le passage de l'Orin à la Thor se fera sans douleur car les scripts et les modèles sont compatibles (CUDA).

---
**Conclusion :** N'attendez pas. L'Orin 64 Go déporté est le meilleur investissement pour valider votre architecture logicielle dès aujourd'hui.
