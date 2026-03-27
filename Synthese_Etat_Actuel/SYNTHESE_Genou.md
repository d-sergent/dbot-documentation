# Synthèse : Genou (Knee) - État de l'Art

Ce document résume la configuration finale et aboutie du système articulé du genou pour le D-Bot (Phase V1).

## 1. Actionneur & Transmission
- **Moteur** : Unitree **RS-04** (120 N.m pic).
- **Transmission** : Courroie synchrone **GT3** (Solution S6).
- **Réduction** : **2.5:1** (Pignon 20T sur moteur / 50T sur genou).
- **Performances** :
  - **Couple Pic** : **300 N.m**.
  - **Masse Transmission** : ~320 g.
  - **Vitesse Max** : ~1.5 m/s (Marche sécurisée à 5 km/h).

## 2. Intégration Mécanique
- **Position Moteur** : Déporté en haut du fémur (pancake vertical) pour réduire l'inertie du tibia.
- **Structure** : Brackets en aluminium **7075-T6 CNC** avec allégement **Isogrid** (nervures de 5mm).
- **Tension** : Galet tendeur à ressort sur le brin mou.

## 3. Analyse de Charge (39-40 kg)
| Scénario | Charge (%) | Vitesse | Marge |
| :--- | :---: | :---: | :---: |
| Marche lente (2 km/h) | ~40% | Basse | Très Large |
| Portage (Charge 20 kg) | ~65% | 2.5 km/h | Confortable |
| Course (Pic) | ~90% | > 6 km/h | Limite Thermique |

## 4. Liens et Archives
- **Analyse de Portage** : [15f_Portage_Charges_et_Marche.md](../15f_Portage_Charges_et_Marche.md)
- **Détails Montage GT3** : [15g_Solution_S6_Courroie_GT3_Genou.md](../15g_Solution_S6_Courroie_GT3_Genou.md)
- **Études Historiques** : 
  - [Archives/ETUDE_Verrin_vs_GT3.md](../Archives/ETUDE_Verrin_vs_GT3.md) (Raison du rejet du vérin)
  - [Archives/ETUDE_Chaines_Rouleaux.md](../Archives/ETUDE_Chaines_Rouleaux.md) (Raison du rejet de la chaîne)
