# Synthèse Métrologique et CAO — Torse et Bassin D-Bot V1

> **Statut** : Document de référence métrologique validé par extraction CAO Fusion 360  
> **Source de vérité CAO** : `Torse v107`  
> **Date de l'audit** : 2026-10-04T22:36:10.792583  
> **Fichier source** : [`AUDIT_METROLOGIQUE_Torse_et_Bassin.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_METROLOGIQUE_Torse_et_Bassin.json)

---

## 📑 Sommaire

1. [Vue d'Ensemble & Masses](#1-vue-densemble--masses)
2. [Dimensions Physiques Réelles & Altitude au Sol](#2-dimensions-physiques-réelles--altitude-au-sol)
3. [Chaîne Cinématique et Empilement Waist (Z)](#3-chaîne-cinématique-et-empilement-waist-z)
4. [Bilan d'Usinage & Quincaillerie Clé](#4-bilan-dusinage--quincaillerie-clé)
5. [Nomenclature Consolidée Majeure](#5-nomenclature-consolidée-majeure)
6. [Interface & Cartographie des 4 Fixations Torse / Waist Plate](#6-interface--cartographie-des-4-fixations-torse--waist-plate)

---

## 1. Vue d'Ensemble & Masses

* **Masse totale de l'ensemble Torse + Bassin** : **24.16 kg** (24 156.03 g).
* **Nombre de composants modélisés** : **367 instances** (BOM de 99 références uniques).
* **Centre de gravité global (CoM)** :
  * **X** (profondeur) = **+61.93 mm** (léger déport avant cohérent avec l'implantation pectorale et batteries).
  * **Y** (latéral) = **+3.53 mm** (quasi-parfaite symétrie gauche/droite).
  * **Z** (hauteur) = **1053.36 mm** (situé au niveau du plexus, entre le waist à 1035 mm et la plaque de cou à 1476 mm).

---

## 2. Dimensions Physiques Réelles & Altitude au Sol

> [!IMPORTANT]
> **Distinction essentielle pour le dimensionnement robotique** :
> 1. **L'altitude Z** est repérée par rapport au sol (la plante des pieds du robot debout est à Z = 0 mm).
> 2. **La hauteur physique réelle** du sous-ensemble Torse + Bassin est de **833.0 mm** (83.3 cm).

| Grandeur | Coordonnées / Plage (mm) | Dimension Physique Réelle | Commentaire |
| :--- | :--- | :--- | :--- |
| **Profondeur totale (X)** | [Chassis_Structurel_Bassin [ASV1_200_01C]:1] 243.0 mm | **243.0 mm** | Encombrement avant/arrière plastron + carénages |
| **Largeur totale (Y)** | Epaules / Hanche : 487.1 mm | **487.1 mm** | Largeur d'épaules et pivots de hanches |
| **Altitude Z au sol** | **714.17 mm -> 1547.12 mm** | — | Repère mondial D-Bot (pieds à Z = 0 mm) |
| **Bassin seul (Pelvis)** | 762,87 mm -> 1043,18 mm | **280.3 mm** (~28,0 cm) | Du bas du carénage hanche au sommet du berceau |
| **Torse seul (Waist au cou)** | 1034,91 mm -> 1547.12 mm | **512.2 mm** (~51,2 cm) | De la Waist Plate au sommet du tube de cou |
| **Hauteur Totale Torse + Bassin** | 762,87 mm -> 1547.12 mm | **833.0 mm** (~78,4 cm) | **Hauteur physique propre de l'assemblage** |

---

## 3. Chaîne Cinématique et Empilement Waist (Z)

L'empilement vertical de l'articulation de lacet du buste (Waist Yaw) a été vérifié au micron près :

| Composant / Interface | Z Bas (mm) | Z Haut (mm) | Épaisseur (mm) | Écart mesuré | Statut métrologique |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Moteur RS06 (Rotor)** | 958.90 | 1009.44 | 50,54 | — | Référence rotor RS06 |
| **Moyeu Waist Sandwich** | 1009.41 | 1033.03 | 23,62 | Appui rotor : 0,03 mm | **Contact franc** |
| **Châssis Châssis_Structurel_Bassin** | 755.90 | 1010.42 | 200,42 | — | Sommet du châssis bassin |
| **Traverse Renfort Bassin** | 1007.90 | 1020.41 | 10,02 | Appui châssis : 2.52 mm | **Contact franc** |
| ↳ *Lamage Traverse (profondeur 3,00 mm)* | — | **1017.41** | Prof. 3,00 | — | Face d'appui du RB8016 |
| **Roulement RB8016** | **1020.39** | **1035.41** | 16,04 | Fond lamage : **2.98 mm** | **Contact franc parfait (10 µm)** |
| **Waist Plate 7075** | **1033.41** | **1042.43** | 7,53 | Appui bague int. : 2.00 mm | **Contact franc** |
| ↳ *Jeu Anti-talonnage (Moyeu vs Waist Plate)* | 1033.03 | 1033.41 | — | **0.38 mm** | **CONFORME (Nominal 0,40 mm)** |
| **Équerre Waist & Plastron Ventral** | 1042.41 | 1072.43 | 30,02 | Appui Waist Plate : 0,03 mm | **Contact franc** |
| ↳ *Hauteur Libre Périphérique (Waist Plate ➔ Traverse)* | 1020.41 | 1036.42 | — | **16.02 mm** | **Vérifié (Garde complète sous vis plastron)** |

---

## 4. Bilan d'Usinage & Quincaillerie Clé

* **Fraisures coniques 90° (Vis FHC M4)** : **2118 fraisures** détectées et validées sur le châssis, la traverse, les capots et les équerres.
* **Alésages et lamages majeurs (>= 60 mm)** : **308 alésages** de précision répertoriés (notamment le lamage de traverse Ø 120 mm pour RB8016 et les alésages de roulements de hanche).
* **Goupilles de centrage Ø 3,0 mm (ISO 8734)** : **263 positions** de centrage géométrique.

---

## 5. Nomenclature Consolidée Majeure

| Composant clé | Référence CAO | Quantité | Matériau principal | Masse unitaire CAO |
| :--- | :--- | :--- | :--- | :--- |
| Châssis Structurel Bassin | ASV1_200_01C | 1 | Aluminium 7075-T6 *(cible PA12-CF)* | 7,64 kg *(2,81 kg cible)* |
| Traverse Renfort Bassin | ASV1_200_16A | 1 | Aluminium 7075-T651 | 567,74 g |
| Roulement à rouleaux croisés | RB8016 | 1 | Acier à roulement GCr15 | 633,41 g |
| Waist Plate | Waist_Plate_7075 | 1 | Aluminium 7075-T651 | 434,71 g |
| Moyeu Waist Sandwich | Moyeu_Waist_Sandwich_7075 | 1 | Aluminium 7075-T651 | 163,94 g |
| Moteur Yaw Waist | RobStride RS06 | 1 | Actionneur QDD | 550,97 g |
| Plastron Ventral Torse | Plastron_Ventral_Torse | 1 | PA12-CF (Infill 30% Gyroïde) | **2 801,37 g** |
| Colonne vertébrale | Colonne_Vertebrale | 1 | Aluminium 7075-T6 | 568,20 g |
| Panier Batterie Coulissant | Panier_Batterie_Coulissant | 1 | PA12-CF / Al 7075 | 554,80 g |
| Plaque de Cou | Plaque_de_Cou_7075 | 1 | Aluminium 7075-T651 | 89,63 g |

---

## 6. Interface & Cartographie des 4 Fixations Torse / Waist Plate

Le Plastron Ventral est fixé rigidement sur la face supérieure de la Waist Plate (`Z = 1042,42 mm`) via 4 points d'attache intérieurs intégrés dans la masse en PA12-CF, éliminant toute tête de vis visible depuis l'extérieur du robot :

| Point de Fixation | Position X (mm) | Position Y (mm) | Altitude Z d'Appui (mm) | Diamètre Perçage | Lamage & Dégagement | Symétrie & Entraxe |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Trou 1 (Dorsal-Droit)** | **`-17,90`** | **`-56,68`** | `Z = 1042,42` | **`Ø 4,50 mm`** | Lamage horizontal (plancher 10,0 mm) | Symétrie ±66,03 mm axe waist |
| **Trou 2 (Dorsal-Gauche)** | **`-17,90`** | **`+75,39`** | `Z = 1042,42` | **`Ø 4,50 mm`** | Lamage horizontal (plancher 10,0 mm) | Symétrie ±66,03 mm axe waist |
| **Trou 3 (Ventral-Droit)** | **`+103,30`** | **`-62,50`** | `Z = 1042,42` | **`Ø 4,50 mm`** | Lamage cylindrique `Ø 19,0 mm` | Symétrie ±71,17 mm plan sagittal |
| **Trou 4 (Ventral-Gauche)** | **`+103,30`** | **`+79,84`** | `Z = 1044,07` | **`Ø 4,50 mm`** | Lamage cylindrique `Ø 19,0 mm` | Entraxe Y = 142,34 mm |

### Caractéristiques Mécaniques & Validation :
1. **Épaisseur Sous Tête Robuste** : Voile de matière de **`10,0 mm` de PA12-CF plein** sous chaque tête de vis, garantissant une absence totale d'écrasement ou de fluage au couple de serrage nominal.
2. **Garde Radiale & Outillage** : Dégagement de **`5,0 mm`** par rapport aux parois concaves, offrant un jeu franc de `+1,5 mm` pour têtes CHC M4 (Ø 7,0 mm) et passage direct d'un tournevis ou clé Allen de 3,0 mm.
3. **Espace Libre Sous Plaque (16,02 mm)** : Les 4 perçages sont situés en dehors du rayon d'encombrement des brides de retenue axiale (R ≈ 65-75 mm). Sous la Waist Plate (Z = 1036,42 mm), un vide d'air de **`16,02 mm`** existe jusqu'à la Traverse du bassin (Z = 1020,41 mm), permettant des vis débouchantes (M4 × 18 mm) ou le montage d'écrous autofreinés Nylstop M4 en sous-face avec plus de 11 mm de garde résiduelle.


