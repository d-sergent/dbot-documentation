# Synthèse Métrologique et CAO — Torse et Bassin D-Bot V1

> **Statut** : Document de référence métrologique validé par extraction CAO Fusion 360  
> **Source de vérité CAO** : `Torse-123 v52`  
> **Date de l'audit** : 2026-11-22T22:55:43.586895  
> **Fichier source** : [`AUDIT_METROLOGIQUE_Torse_et_Bassin.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/Audits/AUDIT_METROLOGIQUE_Torse_et_Bassin.json)  
> **Audits complémentaires (`Audits/`)** : `AUDIT_CINEMATIQUE_Torse_et_Bassin.json`, `AUDIT_ALIGNEMENT_Torse_et_Bassin.json`

---

## 📑 Sommaire

1. [Vue d'Ensemble & Masses](#1-vue-densemble--masses)
2. [Dimensions Physiques Réelles & Altitude au Sol](#2-dimensions-physiques-réelles--altitude-au-sol)
3. [Chaîne Cinématique et Empilement Waist (Z)](#3-chaîne-cinématique-et-empilement-waist-z)
4. [Architecture Modulaire Torse C1 / C2 & Ceinture](#4-architecture-modulaire-torse-c1--c2--ceinture)
5. [Bilan d'Usinage & Quincaillerie Clé](#5-bilan-dusinage--quincaillerie-clé)
6. [Nomenclature Consolidée Majeure](#6-nomenclature-consolidée-majeure)

---

## 1. Vue d'Ensemble & Masses

* **Masse totale de l'ensemble Torse + Bassin** : **16.34 kg** (16338.97 g).
* **Nombre de composants modélisés** : **628 instances** (BOM de 129 références uniques).
* **Centre de gravité global (CoM)** :
  * **X** (profondeur) = **+62.13 mm** (déport avant cohérent avec l'implantation pectorale et les tiroirs batteries).
  * **Y** (latéral) = **+8.34 mm** (symétrie gauche/droite par rapport au plan médian machine).
  * **Z** (hauteur) = **1127.23 mm** (situé au niveau du plexus, entre le waist à 1033.42 mm et la plaque de cou à 1476.10 mm).

---

## 2. Dimensions Physiques Réelles & Altitude au Sol

> [!IMPORTANT]
> **Distinction essentielle pour le dimensionnement robotique** :
> 1. **L'altitude Z** est repérée par rapport au sol (la plante des pieds du robot debout est à Z = 0 mm).
> 2. **La hauteur physique réelle** du sous-ensemble Torse + Bassin est de **832.95 mm** (83.3 cm).

| Grandeur | Coordonnées / Plage (mm) | Dimension Physique Réelle | Commentaire |
| :--- | :--- | :--- | :--- |
| **Profondeur totale (X)** | -71.70 mm -> 171.27 mm | **242.97 mm** | Encombrement avant/arrière plastron + carénages |
| **Largeur totale (Y)** | -245.87 mm -> 241.19 mm | **487.06 mm** | Largeur d'épaules et pivots de hanches |
| **Altitude Z au sol** | **714.17 mm -> 1547.12 mm** | — | Repère mondial D-Bot (pieds à Z = 0 mm) |
| **Bassin seul (Pelvis)** | 714.19 mm -> 1035.40 mm | **321.21 mm** (~32.1 cm) | Du bas des supports de hanche au sommet du berceau |
| **Torse seul (Waist au cou)** | 1033.42 mm -> 1547.12 mm | **513.70 mm** (~51.4 cm) | De la Waist Plate au sommet du collet de cou |
| **Hauteur Totale Torse + Bassin** | 714.17 mm -> 1547.12 mm | **832.95 mm** (~83.3 cm) | **Hauteur physique propre de l'assemblage** |

---

## 3. Chaîne Cinématique et Empilement Waist (Z)

L'empilement vertical de l'articulation de lacet du buste (Waist Yaw) a été vérifié au micron près :

| Composant / Interface | Z Bas (mm) | Z Haut (mm) | Épaisseur (mm) | Écart mesuré | Statut métrologique |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Moteur RS06 (Rotor)** | 958.90 | 1009.44 | 50.54 | — | Référence rotor RS06 |
| **Moyeu Waist Sandwich** | 1009.42 | 1033.02 | 23.60 | Appui rotor : 0.02 mm | **Contact franc** |
| **Châssis Structurel Bassin** | 800.94 | 1020.95 | 220.01 | Enveloppe coque PA12-CF | Coque pelvienne encastrée |
| **Traverse Renfort Bassin** | 1007.92 | 1020.40 | 12.48 | Sur Pont de Hanches (Alu 7075) | **Interface Waist maître** |
| ↳ *Lamage Traverse (profondeur 3,00 mm)* | — | **1017.40** | Prof. 3,00 | — | Face d'appui du RB8016 |
| **Roulement RB8016** | **1017.42** | **1033.42** | 16.00 | Fond lamage : **0.02 mm** | **Contact franc** |
| **Waist Plate 7075** | **1033.42** | **1042.42** | 9.00 | Appui bague int. : 0.00 mm | **Contact franc** |
| ↳ *Jeu Anti-talonnage (Moyeu vs Waist Plate)* | 1033.02 | 1033.42 | — | **0.40 mm** | **Jeu de sécurité axial** |
| **Équerre Waist & Plastron Ventral** | 1042.42 | 1072.42 | 30.00 | Appui Waist Plate : 0.00 mm | **Contact franc** |

---

## 4. Architecture Modulaire Torse C1 / C2 & Ceinture

| Élément | Nom du Corps | Z Bas (mm) | Z Haut (mm) | Épaisseur / Hauteur Z (mm) | Volume (cm3) | Masse propre |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Demi-fût Supérieur (C1)** | Torse_Haut_C1 | 1235.45 | 1471.42 | 235.97 mm | 1551.27 | 1085.88 g |
| **Ceinture Intermédiaire Alu** | ceinture | 1233.5 | 1236.5 | 3.0 mm | 16.17 | 45.43 g |
| **Demi-fût Inférieur (C2)** | Torse_Haut_C2 | 1110.42 | 1234.55 | 124.13 mm | 613.64 | 429.57 g |

---

## 5. Bilan d'Usinage & Quincaillerie Clé

* **Fraisures coniques 90° (pièces structurelles usinées/imprimées)** : **423 fraisures** dédoublonnées (hors visserie/moteurs).
* **Alésages et lamages majeurs (>= 60 mm, pièces structurelles)** : **88 surfaces d'alésages** répertoriées (lamage Traverse Ø 120 mm, alésages Waist Plate Ø 80/130/170 mm, interfaces bassin).
* **Goupilles / alésages fins Ø 3,0 mm (pièces structurelles)** : **44 perçages** répertoriés (hors moteurs STEP).

---

## 6. Nomenclature Consolidée Majeure

| Composant clé | Référence CAO | Quantité | Matériau / Note | Masse unitaire | Masse totale |
| :--- | :--- | :---: | :--- | ---: | ---: |
| 1_1_06_EB1203-503_1 | `1_1_06_EB1203-503_1` | 4 | Acier | 717.36 g | 2869.44 g |
| Plastron_Ventral_Torse | `ASV1_100_01` | 1 | PA12-CF (6 corps) + ceinture Alu 7075 | 1979.60 g | 1979.60 g |
| 1_1_02_EB1201-501_1 | `1_1_02_EB1201-501_1` | 4 | Acier | 285.41 g | 1141.64 g |
| _GYOS72-17_93_I__1 | `_GYOS72-17_93_I__1` | 4 | Acier | 207.96 g | 831.84 g |
| Bride Epaule | `Bride Epaule` | 4 | Aluminium 7075 | 202.30 g | 809.20 g |
| 1_1_06_EB1203-504_1 | `1_1_06_EB1203-504_1` | 4 | Acier | 168.34 g | 673.36 g |
| RB8016 | `1` | 1 | Acier | 633.41 g | 633.41 g |
| Traverse_Renfort_Bassin [ASV1_200_16A] | `ASV1_200_16A.step` | 1 | Aluminium 7075 | 565.76 g | 565.76 g |
| colonne vertébrale | `colonne vertébrale` | 1 | Aluminium 7075 | 489.50 g | 489.50 g |
| Chassis_Structurel_Bassin_Last | `Chassis_Structurel_Bassin_Last` | 1 | PA12-CF (Coque 5mm Infill 15% Gyroide) | 481.19 g | 481.19 g |
| Waist_Plate_7075 | `Waist_Plate_7075` | 1 | Aluminium 7075 | 433.24 g | 433.24 g |
| Selle de Pont Pelvis [ASV1_200_10] | `ASV1_200_10` | 1 | Aluminium 7075 | 338.98 g | 338.98 g |
| semelle éclisse | `semelle éclisse` | 2 | Aluminium 7075 | 158.32 g | 316.64 g |
| DIANJIBAN-2_SW0001_1_1 | `DIANJIBAN-2_SW0001_1_1` | 4 | Acier | 72.91 g | 291.64 g |
| 1_1_06_EB823-507_AF0^1_1_06_EB823-509_ASM_FL82BLW33-48V-35N.m(开模版)(1)_FL82BLW33-48V-35N.m(开模版)(1).STEP | `1_1_06_EB823-507_AF0^1_1_06_EB823-509_ASM_FL82BLW33-48V-35N.m(开模版)(1)_FL82BLW33-48V-35N.m(开模版)(1).STEP` | 1 | Acier | 235.19 g | 235.19 g |
| 1_21_121000046___61810_50__1 | `1_21_121000046___61810_50__1` | 4 | Acier | 56.36 g | 225.44 g |
| Support_Hanche_Gauche [ASV1_200_06C] | `ASV1_200_06C.step` | 1 | PA12-CF (Cosmetique Infill 15% Gyroide) [En cours de définition CAO] | 204.79 g | 204.79 g |
| Support_Hanche_Droit [ASV1_200_08C] | `ASV1_200_08C.step` | 1 | PA12-CF (Cosmetique Infill 15% Gyroide) [En cours de définition CAO] | 204.78 g | 204.78 g |
| Insert | `Insert` | 2 | Aluminium 7075 | 85.71 g | 171.42 g |
| Panier_Batterie_Gauche | `Panier_Batterie_Gauche` | 1 | PA12-CF (Cosmetique Infill 15% Gyroide) | 169.62 g | 169.62 g |
| Panier_Batterie_Droit | `Panier_Batterie_Droit` | 1 | PA12-CF (Cosmetique Infill 15% Gyroide) | 169.60 g | 169.60 g |
| Moyeu_Waist_Sandwich_7075 | `Moyeu_Waist_Sandwich_7075` | 1 | Aluminium 7075 | 163.94 g | 163.94 g |
| Corniere basse | `Corniere_Basse_7075` | 2 | Aluminium 7075 | 70.34 g | 140.68 g |
| Carenage_Lombaire_Arriere | `ASV1_100_06C_v1` | 1 | PA12-CF (Cosmetique Infill 15% Gyroide) | 114.05 g | 114.05 g |
| Carenage_Pectoral_Haut | `ASV1_100_04C` | 1 | PA12-CF (Cosmetique Infill 15% Gyroide) | 112.46 g | 112.46 g |
| Tube transverse Epaules gauche | `Tube transverse Epaules gauche` | 1 | Aluminium 6060-T6 | 100.04 g | 100.04 g |
| Tube transverse Epaules droit | `Tube transverse Epaules droit` | 1 | Aluminium 6060-T6 | 100.04 g | 100.04 g |
| 1_1_06_EB823-511^FL82BLW33-48V-35N.m(开模版)(1)_FL82BLW33-48V-35N.m(开模版)(1).STEP | `1_1_06_EB823-511^FL82BLW33-48V-35N.m(开模版)(1)_FL82BLW33-48V-35N.m(开模版)(1).STEP` | 1 | Acier | 98.76 g | 98.76 g |

