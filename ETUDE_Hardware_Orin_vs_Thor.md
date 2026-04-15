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

## 2. Analyse Stratégique pour le D-Bot

### Option A : Jetson Orin Nano (8 Go) — Déjà achetée
- **Avantage** : Légère, consommation très faible (10W-15W).
- **Inconvénient** : Suffisante pour la cinématique de base (ROS2) et la vision (OAK-D), mais ne pourra pas faire tourner de gros algorithmes d'IA en local si le besoin se présente plus tard.

### Option B : Évolution vers Orin AGX (64 Go)
- **Avantage** : Puissance colossale, permet d'envisager beaucoup plus d'algorithmes et de traitements lourds directement dans le robot.
- **Inconvénient** : Consommation importante (jusqu'à 60W), ce qui réduit le temps de marche autonome.

---
**Conclusion :** L'Orin Nano 8 Go actuelle est parfaite pour finaliser l'assemblage et la marche via ROS2. Le passage à une architecture plus lourde (Orin 64 Go ou Thor) pourra être évalué pour une future itération (V2) en fonction des besoins algorithmiques.
