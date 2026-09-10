# 28 - Synthèse des Dimensions Physiques et Leviers (D-Bot)

> **Dernière Révision** : Septembre 2026 (Intégration Architecture Torse V2 Tout Métal & Module Bassin/Waist Yaw RS-06)

Ce document centralise toutes les hypothèses de dimensions physiques, longueurs de membres, et bras de leviers utilisées jusqu'à présent pour les calculs de cinématique, de locomotion et de couple du robot D-Bot. 

Il sert de point de référence unique (Source of Truth) pour la modélisation CAO et la commande numérique.

## 📑 Sommaire

- [1. Dimensions Globales et Torse](#1-dimensions-globales-et-torse-architecture-v2-tout-métal--septembre-2026)
- [2. Membres Inférieurs (Jambes)](#2-membres-inférieurs-jambes)
- [3. Membres Supérieurs (Bras)](#3-membres-supérieurs-bras)
- [4. Tête et Capteurs](#4-tête-et-capteurs)
- [5. Bassin (Pelvis) & Liaison Active Waist Yaw RS-06](#5-bassin-pelvis--liaison-active-waist-yaw-rs-06)
- [6. Synthèse des Incertitudes](#6-synthèse-des-incertitudes-à-définir-pour-la-construction)
- [7. Schémas Visuels et Proportions](#7-schémas-visuels-et-proportions)
- [8. Estimation du Poids de la D-Hand Hybrid](#8-estimation-du-poids-de-la-d-hand-hybrid)

## 1. Dimensions Globales et Torse (Architecture V2 Tout Métal — Septembre 2026)

| Paramètre | Valeur | Statut |
| :--- | :---: | :--- |
| **Hauteur Totale** | **~1,55 m** | ✅ Figée (scale +18% du torse + module Waist Yaw) |
| **Masse Totale de Référence** | **~40,4 kg** | ✅ Châssis hybride alu/carbone, 27 moteurs RobStride QDD, 2 packs 12S Li-Ion, 2 D-Hand |
| **Degrés de Liberté Torse** | **1 DOF Actif (Waist Yaw)** | ✅ Motorisé par **RobStride RS-06** (36 N.m pic, 11 N.m nom., Ø 88 mm, 621 g, CAN-FD ID 21) |
| **Torse (Hauteur Coque Physique)** | **432,67 mm** (coque nue) | ✅ Scalée à +18% en CAO pour l'intégration des moteurs RS-04 |
| **Torse (Hauteur Cinématique Épaule ➔ Hanche)** | **495,60 mm** | ✅ Inclut : coque 432,67 mm + Waist Plate 6,0 mm + roulement 4 pts 10 mm + bague RS-06 + demi-épaisseur du bassin. Utiliser cette valeur pour l'URDF (`waist_yaw_joint` ➔ `shoulder_pitch_joint`). |
| **Torse (Largeur de Coque)** | **295,00 mm** (coque nue) | ✅ Scalée à +18% en CAO (anciennement 250 mm) |
| **Torse (Profondeur de Coque)** | **259,60 mm** (coque nue) | ✅ Scalée à +18% en CAO (anciennement 220 mm) |
| **Largeur d'Épaules (Entraxe RS-04 Pitch)** | **~378 mm** | ✅ Scalée (+18% de ~320 mm) avec déport des moteurs RS-04 |
| **Largeur de Bassin (Entraxe RS-04 Hanche)** | **~378 mm** | ✅ Scalée (+18% de ~320 mm) avec déport moteurs |

### Architecture Mécanique du Torse V2 (Tout Métal, Août-Septembre 2026)

L'ancienne architecture composite (cage alu boulonnée, tube carbone, split-monocoque PA12-CF) est **obsolète**. Le design retenu est le **Squelette Séminal Tout Métal** :

| Composant Structurel | Matériau & Dimensions | Masse Réelle (CAO) |
| :--- | :--- | :---: |
| **Colonne Sagittale (2 plaques évidées 2D)** | Alu 7075-T6, 5,0 mm, largeur 94~100 mm | **~315 g** |
| **2 Brides d'Épaule Monoblocs** | Alu 7075-T651, Ø 120 x 50 mm (Flasque 5 + Hub 13,2 + Bossage 15 mm) | **533,7 g** |
| **2 Demi-Traverses d'Épaule** | Tube carré 60x60x2 mm Alu 6060-T6, L = 80,05 mm | **200,1 g** |
| **2 Inserts carrés colonne** | Alu 7075-T6, 55,8x55,8x15 mm | **173,0 g** |
| **2 Semelles éclisses** | Alu 7075-T6, 100x130x5 mm | **135,2 g** |
| **4 Équerres de liaison (cou & waist)** | Alu 6060-T6, cornière 30x30x3 mm | **117,6 g** |
| **Tuyères + Ventilateurs + Visserie** | PA12-CF, Noctua NF-A4x20, visserie M4/M5 | **~280,8 g** |
| **TOTAL Bloc Haut Torse (Squelette Métal Complet)** | — | **~1 754 g** |

| Masse Suspendue Totale (Haut du Corps) | **~17 300 g (~17,3 kg)** |
| :--- | :---: |
| *Inclut : torse V2, 2 bras complets, 2 D-Hand, tête/cou 2x RS-05, 2 packs 12S batteries, Jetson, PDB, câblage* | *Valeur révisée V2, conservative* |

> 📄 **Document actif Torse** : [DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md](../01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md)  
> 📄 **Document actif Bassin** : [DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md](../01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md)  
> 📄 **Analyse stratégique (historique)** : [ANALYSE_STRATEGIE_Torse.md](../01_Mecanique_et_Chassis/Torse_et_Bassin/ANALYSE_STRATEGIE_Torse.md)

## 2. Membres Inférieurs (Jambes)
*Données déduites de `15a_Analyse_Locomotion_Baseline.md`.*
- **Cuisse (Axe Hanche -> Axe Genou)** : ~350 mm (35 cm).
- **Tibia (Axe Genou -> Axe Cheville)** : ~350 mm (35 cm).
    - *Note de fabrication* : Si l'on utilise un tube carbone structurel, sa longueur propre est estimée à environ ~220 mm. La longueur cinématique de 350 mm est atteinte en incluant les brackets haut (genou) et bas (cheville).
- **Pied (Levier Cheville -> Orteil/Talon)** : ~100 mm (10 cm).

### Leviers Spécifiques (Cinématique du Genou à Tirant)
*Données déduites de l'intégration GT3 et architecture à tirant.*
- **Bras de Manivelle (Crank haut, lié au moteur RS-04)** : 60 mm.
- **Bras de Levier (Genou bas, lié au tibia)** : 90 mm.
- **Longueur du Tirant (Bielle de transmission)** : ~250 mm.
- **Bras de levier projeté au sol** : ~180 mm (18 cm). 
    - *Note* : C'est cette distance horizontale (centre de gravité -> appui du pied) lors de la marche genoux fléchis qui a permis de calculer l'exigence de couple critique de 16.2 N.m par jambe (soit ~300 N.m après marge de sécurité dynamique).

## 3. Membres Supérieurs (Bras)
- **Bras (Axe Épaule -> Axe Coude)** : ~250 mm (25 cm).
- **Avant-bras (Axe Coude -> Axe Poignet)** : ~220 mm (22 cm).
- **Main (Axe Poignet -> Bout effecteur)** : ~250 mm (25 cm).
- **Allonge combinée de l'avant-bras et main** : ~470 mm (47 cm).

## 4. Tête et Capteurs
- **Hauteur totale Tête + Cou** : **250 mm** (25 cm) - *Hypothèse figer*.
- **OAK-D Pro (Fixed Focus - Vision)** : Entraxe de fixation de 75 mm (vis M3). Encastrement ~98x30 mm.
- **Cou (Double RS-05)** : La superposition des moteurs s'inscrit dans l'enveloppe globale de 250 mm allouée à la tête et au cou.

## 5. Bassin (Pelvis) & Liaison Active Waist Yaw RS-06

Le bassin constitue le noeud structurel le plus sollicité du robot. Il reçoit l'intégralité du poids du haut du corps (~17,3 kg) et le transmet aux jambes via les 2 moteurs RS-04 Hip Pitch.

| Paramètre Bassin | Valeur | Statut |
| :--- | :---: | :--- |
| **Moteur Waist Yaw** | **RobStride RS-06** (36 N.m pic, 11 N.m nom., Ø 88 mm, 621 g) | ✅ Acheté & Validé |
| **Roulement Structurel Principal** | **Roulement a rouleaux croises CRBH 8016 UU (80x120x16 mm, P5)** | ✅ Validé, a commander (AliExpress ~60-90 EUR, 2-4 sem.) |
| **Platine d'Interface Waist** | Alu 7075-T6, Ø 140 x 12 mm, alésage Ø 88 H7, siège roulement Ø 120 H7 x 3 mm, ~265 g | ✅ Dimensionnée (usiner après réception roulement) |
| **Entraxe Hanches (RS-04 Hip Pitch)** | **~378 mm** | ✅ Scalé +18% |
| **Chaîne Cinématique Hanches** | **F-A-R** (Flexion Pitch RS-04 ➔ Abduction Roll RS-03 ➔ Rotation Yaw RS-03) | ✅ Validée |
| **Butée Angulaire Mécanique** | Double ergot DIN 6325 Ø 5 mm + rainure en arc +/- 95 deg | ✅ Dimensionnée |
| **Débattement Waist Yaw** | Logiciel : +/- 90 deg / Physique : +/- 95 deg | ✅ |

### Sourcing du Roulement Structurel Waist (Chemin Critique)

Le roulement structurel du Waist est le composant le plus critique et à délai le plus long du bassin. Il doit reprendre les moments de basculement (56 à 220 N.m) et les charges radiales (90 à 300 N) tout en laissant un passage central d'au moins Ø 40 mm pour les câbles 48V et CAN-FD.

#### Option A — Roulement à Rouleaux Croisés RB 8016 / CRBH 8016 (80x120x16 mm) ⭐ Recommandée

Les rouleaux croisés à 90 deg offrent la rigidité maximale en basculement (~500+ N.m) et un jeu angulaire quasi-nul. La référence **RB 8016 / CRBH 8016** (Ø int 80 mm, Ø ext 120 mm, épaisseur 16 mm) est la plus proche des contraintes dimensionnelles du D-Bot.

| Fournisseur | Plateforme | Recherche / Lien | Prix Estimé | Délai |
| :--- | :--- | :--- | :---: | :---: |
| **Luoyang (Chine)** | [AliExpress](https://www.aliexpress.com) | Rechercher **"RB8016 crossed roller bearing"** ou **"CRBH8016"** | **40 a 90 EUR** | 2-4 sem. |
| **123Roulement (France)** | [123roulement.com](https://www.123roulement.com) | Contacter le service client avec ref **"CRBH 8016 UU"** | **150 a 350 EUR** (devis) | 2-6 sem. |
| **Rubix (France, ex-Brammer)** | [rubix.com/fr](https://www.rubix.com/fr-fr/) | Demander devis **"Roulement rouleaux croisés 80x120x16"** | **200 a 400 EUR** | 3-6 sem. |
| **MISUMI Europe** | [misumi-ec.com](https://www.misumi-ec.com) | Configurateur en ligne, série THK **RB 8016** | **250 a 500 EUR** | 2-4 sem. |
| **GMT Europe (Allemagne)** | [gmteurope.de](https://www.gmteurope.de) | Ref **RU 85 UU CC0** (55x120x15 mm, avec trous de montage) | **300 a 500 EUR** | 3-5 sem. |

#### Option B — Roulement à Billes 4 Points de Contact QJ 210 (50x90x20 mm)

Moins rigide que les rouleaux croisés mais beaucoup plus accessible et moins cher. Le QJ210 (Ø int 50 mm, Ø ext 90 mm, 20 mm) nécessiterait une adaptation des cotes du bassin (alésage plus petit). Peu recommandé pour le D-Bot en raison du petit diamètre intérieur (passage câbles limité).

| Fournisseur | Réf | Prix | Note |
| :--- | :--- | :---: | :--- |
| **123Roulement (France)** | [QJ210-MA SKF](https://www.123roulement.com) | **~103 EUR TTC** | Ø int 50 mm trop petit pour le passage des câbles |
| **Le Bon Roulement** | [lebonroulement.com](https://www.lebonroulement.com) | **~86 EUR HT** | Alternative FAG/NKE disponible |

> **Recommandation** : Commander un **CRBH 8016 UU** (ou équivalent RB 8016) sur AliExpress (~60-80 EUR, classe P5 minimum) en premier pour tester l'intégration. Adapter le diamètre de la Waist Plate à Ø ext 120 mm (au lieu de 110 mm) et l'alésage interne du bassin à 120 mm. Le passage central de Ø 80 mm reste largement suffisant pour les câbles.

---

## 6. Synthèse des Incertitudes (À définir pour la construction)
Pour sécuriser la modélisation CAO finale et la génération des fichiers URDF (pour ROS 2 / Isaac Gym), les points suivants doivent être impérativement relevés et figés une fois le design 3D terminé :

1.  **L'entraxe Y des hanches** : C'est la largeur du bassin. Elle est critique pour planifier la marche, l'équilibre latéral et le balancement (transfert de masse gauche/droite).
2.  **L'entraxe Y des épaules** : Détermine l'espace disponible dans le torse supérieur (pour les Matek PDB et l'électronique) et les collisions possibles entre les bras et le buste.
3.  **La position X, Y, Z du Centre de Masse (CoM)** : À extraire du logiciel de CAO (Fusion 360) une fois le torse numériquement peuplé par la batterie 12S, l'ordinateur de bord (Jetson) et le câblage.
4.  **Référence finale du roulement Waist** : La cote exacte (Ø int / Ø ext / épaisseur) conditionne les dimensions du caisson pelvien et de la Waist Plate. Commander le roulement en priorité.

## 7. Schémas Visuels et Proportions

### Plan Coté (Blueprint Proportionnel)
Ce plan technique illustre les proportions approximatives des segments verticaux (hauteur totale initiale : ~1 470 mm avant scale +18% du torse et intégration du module Waist, hauteur révisée actuelle : **~1 550 mm**).

![Blueprint Proportionnel D-Bot](./assets/img_robot_full_blueprint.png)
*Illustration : Proportions de référence (Tête/Cou: 250, Torse: 432,67 (coque) / 495,60 (cinématique), Cuisse: 350, Tibia: 350, Pied: 100). Hauteur totale révisée : ~1 550 mm.*

### Rendu 3D Global (Conceptuel)
![Squelette Complet D-Bot](./assets/img_robot_full_skeleton.png)
*Illustration : Vue globale du squelette intégrant la structure torse en aluminium 7075-T6 ancrée aux membres robotisés.*

## 8. Estimation du Poids de la D-Hand Hybrid

Cette section détaille l'estimation masse-par-poste du D-Hand v1 (Scénario A : phalanges ORCA + actionneurs D-Hand) en précisant les hypothèses de calcul pour chaque composant.

### 8.1 Hypothèses d'Estimation

| Hypothèse | Base de calcul |
| :--- | :--- |
| **Densité PA12-CF** | 1.01 g/cm³ (PA12 nylon standard + ~15% fibres de carbone) |
| **Densité Aluminium 6061** | 2.70 g/cm³ |
| **Densité Silicone (EcoFlex 00-30)** | ~1.07 g/cm³ |
| **Volume phalange ORCA** | Estimé d'après les dimensions normales ORCA dans le fichier STEP (longueur moy. 35 mm, section 10×12 mm, creux = ~60% plein). Volume effectif estimé ~1.5 cm³/phalange. |
| **Volume paume (Palm Block)** | Bloc alu 100×80×25 mm = 200 cm³, moins ~50% de matière usinée → ~100 cm³ effectifs |
| **Volume poulies CNC** | Cylindre Ø16mm × 8mm d'épaisseur × 8 pièces = ~1.3 cm³/poulie |

### 8.2 Tableau de Masse Poste par Poste

| Composant | Quantité | Masse unitaire | Masse totale | Source / Hypothèse |
| :--- | :---: | :---: | :---: | :--- |
| **Servomoteur Feetech STS3250** | 5 | 74.5 g | **372.5 g** | Datasheet Feetech (source confirmée) |
| **Servomoteur Feetech HL-3915** | 3 | 35.8 g | **107.4 g** | Datasheet Feetech (source confirmée) |
| **Phalanges doigts (3 par doigt × 4 doigts)** | 12 | ~1.5 g | **~18 g** | PA12-CF 1.01 g/cm³, volume creux ~1.5 cm³ |
| **Phalanges pouce (3 phalanges)** | 3 | ~2.0 g | **~6 g** | Pouce légèrement plus massif |
| **Paume CNC (Palm Block, Alu 6061)** | 1 | — | **~270 g** | 100 cm³ effectif × 2.70 g/cm³ |
| **Poulies CNC (Spools, Alu 6061)** | 8 | ~3.5 g | **~28 g** | Ø16mm × 8mm → 1.3 cm³ × 2.70 g/cm³ |
| **Roulements MR84ZZ (4×8×3 mm)** | 35 | ~0.6 g | **~21 g** | Roulement acier chromé standard |
| **Câbles Dyneema Ø0.60 mm** | 8 brins ~150 cm | ~0.3 g/m | **~3 g** | 8 × 1.5 m × 0.3 g/m (Dyneema ultra léger) |
| **Tubes PTFE Ø0.9×1.5 mm** | ~200 cm total | ~1.0 g/m | **~2 g** | Téflon très léger |
| **Goupilles Inox 2×6 mm** | 20 | ~0.3 g | **~6 g** | Acier inoxydable |
| **Axes Inox 3×55 mm** | 4 | ~3.5 g | **~14 g** | Acier inoxydable |
| **Peau Silicone (5 doigts, 1.5 mm)** | 5 | ~3 g | **~15 g** | EcoFlex 00-30, volume pellicule 3 cm³/doigt |
| **Vis & Quincaillerie restante** | — | — | **~10 g** | Estimation forfaitaire (M2, M4) |
| **Câblage Dynamixel (bus daisy-chain)** | — | — | **~15 g** | Fils inter-servo (~30cm total, AWG26) |
| **Capteurs eFlesh (3 axes, 5 doigts)** | 5 | ~5 g | **~25 g** | Estimation module PCB + câble FFC étroit |
| **TOTAL D-HAND HYBRID v1** | | | **~913 g** | |

### 8.3 Comparatif de Poids avec l'ORCA et les Concurrents

| Main | Poids Référence | Commentaire |
| :--- | :---: | :--- |
| **ORCA Hand Base (17 DOF)** | ~1 300 g | 17× Dynamixel, paume imprimée + tour |
| **ORCA Hand Lite (9 DOF)** | ~650 g | 9× Feetech, plus léger |
| **D-Hand Hybrid v1 (8 DOF)** | **~913 g** | Paume alu (plus lourde que ORCA), mais moteurs réduits de 17 → 8 |
| **Tesla Optimus Gen3** | ~800 g (estimé) | Architecture propriétaire non publiée |

> [!NOTE]
> **La paume en Aluminium CNC (+270 g)** est le poste de masse le plus élevé. Si le poids final devient critique pour l'équilibre dynamique du bras, une paume en **PA12-CF imprimée** (comme l'ORCA originale) ramènerait ce poste à ~70 g, abaissant le poids total de la main à **~585 g** — soit une réduction de 200 g.

### 8.4 Impact sur le Bras (Section 3 du document)

Le **couple résistant** que les moteurs d'épaule doivent supporter dû au seul poids de la main (913 g ≈ 8.95 N) :

- Bras : 250 mm + Avant-bras : 220 mm + Main : 250 mm = **720 mm = 0.72 m**

Le **couple résistant** que les moteurs d'épaule doivent supporter dû au seul poids de la main (913 g ≈ 8.95 N) :

```
M_shoulder = F × l = 8.95 N × 0.72 m = 6.44 N.m
```

Ce couple de 6.44 N.m s'ajoute au poids de l'avant-bras et du bras propre et reste dans les capacités normales des moteurs d'épaule (RS-04 ou équivalent).

*Estimation D-Hand Hybrid v1, Mars 2026.*
