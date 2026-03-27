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

### Avantages de l'option Hybride (Orin Nano 8 Go + Cloud)
1. **Poids & Autonomie** : Réduction massive de la consommation (10W vs 60W). Idéal pour maximiser le temps de marche.
2. **Intelligence Maximum** : Accès aux modèles de pointe (GPT-4o, Claude 3.5) sans les contraintes de RAM locale.
3. **Sécurité Déportée** : Le Gateway OpenClaw doit être sécurisé via **Tailscale** et un **Token d'authentification**.

## 3. Recommandation pour le D-Bot

> [!TIP]
> **Le Sweet Spot Immédiat :**
> - **Option A (Performance)** : Investissez dans une **Jetson AGX Orin 64 Go** pour une autonomie totale et privée.
> - **Option B (Légèreté)** : Gardez l'**Orin Nano 8 Go** et déportez la réflexion lourde sur votre Mac ou dans le Cloud via un tunnel sécurisé.

---
**Conclusion :** N'attendez pas. L'Orin 64 Go déporté est le meilleur investissement pour valider votre architecture logicielle dès aujourd'hui.
