# Synthèse Métrologique et CAO — Torse et Bassin D-Bot V1

> **Statut** : Document de référence métrologique validé par extraction CAO Fusion 360  
> **Source de vérité CAO** : `Torse v94`  
> **Date de l'audit** : 2026-09-22T22:24:17.542105  
> **Fichier source** : [`AUDIT_METROLOGIQUE_Torse_et_Bassin.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_METROLOGIQUE_Torse_et_Bassin.json)

---

## 📑 Sommaire

1. [Vue d'Ensemble & Masses](#1-vue-densemble--masses)
2. [Dimensions Physiques Réelles & Altitude au Sol](#2-dimensions-physiques-réelles--altitude-au-sol)
3. [Chaîne Cinématique et Empilement Waist (Z)](#3-chaîne-cinématique-et-empilement-waist-z)
4. [Bilan d'Usinage & Quincaillerie Clé](#4-bilan-dusinage--quincaillerie-clé)
5. [Nomenclature Consolidée Majeure](#5-nomenclature-consolidée-majeure)

---

## 1. Vue d'Ensemble & Masses

* **Masse totale de l'ensemble Torse + Bassin** : **16.71 kg** (16712.6 g).
* **Nombre de composants modélisés** : **306 instances** (BOM de 94 références uniques).
* **Centre de gravité global (CoM)** :
  * **X** (profondeur) = **+61.80 mm** (léger déport avant cohérent avec l'implantation pectorale et batteries).
  * **Y** (latéral) = **+9.07 mm** (quasi-parfaite symétrie gauche/droite).
  * **Z** (hauteur) = **1146.27 mm** (situé au niveau du plexus, entre le waist à 1035 mm et la plaque de cou à 1476 mm).

---

## 2. Dimensions Physiques Réelles & Altitude au Sol

> [!IMPORTANT]
> **Distinction essentielle pour le dimensionnement robotique** :
> 1. **L'altitude Z** est repérée par rapport au sol (la plante des pieds du robot debout est à Z = 0 mm).
> 2. **La hauteur physique réelle** du sous-ensemble Torse + Bassin est de **784.2 mm** (78.4 cm).

| Grandeur | Coordonnées / Plage (mm) | Dimension Physique Réelle | Commentaire |
| :--- | :--- | :--- | :--- |
| **Profondeur totale (X)** | [Chassis_Structurel_Bassin [ASV1_200_01C]:1] 243.0 mm | **243.0 mm** | Encombrement avant/arrière plastron + carénages |
| **Largeur totale (Y)** | Epaules / Hanche : 383.5 mm | **383.5 mm** | Largeur d'épaules et pivots de hanches |
| **Altitude Z au sol** | **762.87 mm -> 1547.12 mm** | — | Repère mondial D-Bot (pieds à Z = 0 mm) |
| **Bassin seul (Pelvis)** | 762,87 mm -> 1043,18 mm | **280.3 mm** (~28,0 cm) | Du bas du carénage hanche au sommet du berceau |
| **Torse seul (Waist au cou)** | 1034,91 mm -> 1547.12 mm | **512.2 mm** (~51,2 cm) | De la Waist Plate au sommet du tube de cou |
| **Hauteur Totale Torse + Bassin** | 762,87 mm -> 1547.12 mm | **784.2 mm** (~78,4 cm) | **Hauteur physique propre de l'assemblage** |

---

## 3. Chaîne Cinématique et Empilement Waist (Z)

L'empilement vertical de l'articulation de lacet du buste (Waist Yaw) a été vérifié au micron près :

| Composant / Interface | Z Bas (mm) | Z Haut (mm) | Épaisseur (mm) | Écart mesuré | Statut métrologique |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Moteur RS06 (Rotor)** | 960.40 | 1010.94 | 50,54 | — | Référence rotor RS06 |
| **Moyeu Waist Sandwich** | 1010.91 | 1034.53 | 23,62 | Appui rotor : 0,03 mm | **Contact franc** |
| **Châssis Châssis_Structurel_Bassin** | 811.50 | 1011.92 | 200,42 | — | Sommet du châssis bassin |
| **Traverse Renfort Bassin** | 1011.89 | 1021.91 | 10,02 | Appui châssis : 0.03 mm | **Contact franc** |
| ↳ *Lamage Traverse (profondeur 3,00 mm)* | — | **1018.91** | Prof. 3,00 | — | Face d'appui du RB8016 |
| **Roulement RB8016** | **1018.90** | **1034.94** | 16,04 | Fond lamage : **0.01 mm** | **Contact franc parfait (10 µm)** |
| **Waist Plate 7075** | **1034.91** | **1042.44** | 7,53 | Appui bague int. : 0.03 mm | **Contact franc** |
| ↳ *Jeu Anti-talonnage (Moyeu vs Waist Plate)* | 1034.53 | 1034.91 | — | **0.38 mm** | **CONFORME (Nominal 0,40 mm)** |
| **Équerre Waist & Plastron Ventral** | 1042.41 | 1072.43 | 30,02 | Appui Waist Plate : 0,03 mm | **Contact franc** |

---

## 4. Bilan d'Usinage & Quincaillerie Clé

* **Fraisures coniques 90° (Vis FHC M4)** : **1967 fraisures** détectées et validées sur le châssis, la traverse, les capots et les équerres.
* **Alésages et lamages majeurs (>= 60 mm)** : **255 alésages** de précision répertoriés (notamment le lamage de traverse Ø 120 mm pour RB8016 et les alésages de roulements de hanche).
* **Goupilles de centrage Ø 3,0 mm (ISO 8734)** : **165 positions** de centrage géométrique.

---

## 5. Nomenclature Consolidée Majeure

| Composant clé | Référence CAO | Quantité | Matériau principal | Masse unitaire |
| :--- | :--- | :--- | :--- | :--- |
| Châssis Structurel Bassin | ASV1_200_01C | 1 | Aluminium 7075-T6 | 3,79 kg |
| Traverse Renfort Bassin | ASV1_200_16A | 1 | Aluminium 7075-T6 | 247 g |
| Roulement à rouleaux croisés | RB8016 | 1 | Acier à roulement | 633 g |
| Waist Plate | Waist_Plate_7075 | 1 | Aluminium 7075-T6 | 320 g |
| Moyeu Waist Sandwich | Moyeu_Waist_Sandwich_7075 | 1 | Aluminium 7075-T6 | 165 g |
| Moteur Yaw Waist | RobStride RS06 | 1 | Actionneur QDD | 551 g |
| Plastron Ventral Torse | Plastron_Ventral_Torse | 1 | Aluminium 7075-T6 | 2,84 kg |
| Colonne vertébrale | Colonne_Vertebrale | 1 | Aluminium 7075-T6 / Carbone | 568 g |
| Panier Batterie Coulissant | Panier_Batterie_Coulissant | 1 | PA12-CF / Al 7075 | 555 g |
| Plaque de Cou | Plaque_de_Cou_7075 | 1 | Aluminium 7075-T6 | 90 g |

