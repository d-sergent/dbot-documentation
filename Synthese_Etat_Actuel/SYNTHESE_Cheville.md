# Synthèse : Cheville (Ankle) - État de l'Art

Ce document résume la configuration finale et aboutie du système articulé de la cheville pour le D-Bot (Phase V1).

## 1. Architecture & Actionneurs
- **Mécanique** : Joint universel (**Cardan**) de type **DIN 808**.
- **Moteurs** : **2× Unitree RS-03** par cheville (montage en différentiel ou découplé selon l'axe).
- **Performances** :
  - **Couple Pitch (Flexion)** : **120 N.m** (Pic).
  - **Couple Roll (Latéral)** : **120 N.m** (Pic).
  - **Marge statique** (39 kg) : **+167%** (Besoin ~45 N.m).
  - **Marge dynamique** (Course) : **+17%** (Besoin ~103 N.m).

## 2. Évolutions Majeures
- **Ancienne Version** : RS-02 + Tirant (34 N.m). Rejetée car marge nulle (0%) à 34 kg.
- **Gain Architecture Cardan** :
  - Multiplication par **3.5** du couple de flexion.
  - Multiplication par **8** du couple latéral (stabilité XL).
  - Suppression du point de fragilité des tirants mécaniques.

## 3. Analyse de Charge (39 kg)
| Scénario | Charge (%) | Stabilité | Verdict |
| :--- | :---: | :---: | :---: |
| Marche normale (3 km/h)| ~37% | Excellente | 🟢 Résolu |
| Correction d'équilibre | < 50% | Très Réactive | 🟢 Idéal |
| Course (V1) | ~86% | Viable | 🟡 Limite |

## 4. Liens et Archives
- **Révision Architecture 39 kg** : [15c_Revision_Cardan_39kg.md](../15c_Revision_Cardan_39kg.md)
- **Analyse Biomécanique** : [15_Analyse_Biomecanique.md](../15_Analyse_Biomecanique.md)
- **Historique des Choix** : 
  - [Archives/ETUDE_RS02_Tirant.md](../Archives/ETUDE_RS02_Tirant.md) (L'ancienne solution abandonnée)
