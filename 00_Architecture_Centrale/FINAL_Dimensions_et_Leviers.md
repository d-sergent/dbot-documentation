# 28 - Synthèse des Dimensions Physiques et Leviers (D-Bot)

Ce document centralise toutes les hypothèses de dimensions physiques, longueurs de membres, et bras de leviers utilisées jusqu'à présent pour les calculs de cinématique, de locomotion et de couple du robot D-Bot. 

Il sert de point de référence unique (Source of Truth) pour la modélisation CAO et la commande numérique.

## 1. Dimensions Globales et Torse (Révision Hybride Asimov v1 - Mai 2026)

| Paramètre | Valeur | Statut |
| :--- | :---: | :--- |
| **Hauteur Totale** | **~1.55 m** | 🔄 Ajustée de ~1.47 m à ~1.55 m (dû au scale +18% du torse, +75.6 mm et intégration du module Waist) |
| **Degrés de Liberté Torse** | **1 DOF Actif (Waist Yaw)** | 🔄 Intégration active du moteur **RobStride RS-03** et de la liaison rotative Asimov v1 (+18 %) sous la plaque inférieure du torse. |
| **Torse (Hauteur Épaule ➔ Hanche)** | **495,60 mm** (cinématique) | 🔄 Ajustée (+18% de 420 mm) suite à l'agrandissement |
| **Torse (Hauteur Coque Physique)** | **432,67 mm** (coque nue) | 🔄 Scalée à +18% en CAO pour l'intégration des moteurs RS-04 |
| **Torse (Largeur de Coque)** | **295,00 mm** (coque nue) | 🔄 Scalée à +18% en CAO (anciennement 250 mm) |
| **Torse (Profondeur de Coque)** | **259,60 mm** (coque nue) | 🔄 Scalée à +18% en CAO (anciennement 220 mm) |
| **Largeur d'Épaules (Entraxe RS-04 Pitch)** | **~378 mm** | 🔄 Ajustée (+18% de ~320 mm) avec déport des moteurs RS-04 |
| **Largeur de Bassin (Entraxe RS-04 Hanche)** | **~378 mm** | 🔄 Ajustée (+18% de ~320 mm) avec déport moteurs |

> Voir le [Guide de Fabrication Hybride Torse Asimov](../01_Mecanique_et_Chassis/Torse/GUIDE_Fabrication_Torse_Asimov_Hybride.md) pour la méthode de split FDM, renforts CNC et intégration de la bague moteur RS-03.

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

## 5. Synthèse des Incertitudes (À définir pour la construction)
Pour sécuriser la modélisation CAO finale et la génération des fichiers URDF (pour ROS 2 / Isaac Gym), les points suivants doivent être impérativement relevés et figés une fois le design 3D terminé :

1.  **L'entraxe Y des hanches** : C'est la largeur du bassin. Elle est critique pour planifier la marche, l'équilibre latéral et le balancement (transfert de masse gauche/droite).
2.  **L'entraxe Y des épaules** : Détermine l'espace disponible dans le torse supérieur (pour les Matek PDB et l'électronique) et les collisions possibles entre les bras et le buste.
3.  **La position X, Y, Z du Centre de Masse (CoM)** : À extraire du logiciel de CAO (Fusion 360) une fois le torse numériquement peuplé par la batterie 12S, l'ordinateur de bord (Jetson) et le câblage.

## 6. Schémas Visuels et Proportions

### Plan Coté (Blueprint Proportionnel)
Ce plan technique illustre les proportions exactes des segments verticaux discutés (Hauteur totale : 1470 mm).

![Blueprint Proportionnel D-Bot](./assets/img_robot_full_blueprint.png)
*Illustration : Les dimensions sont respectées (Tête/Cou: 250, Torse: 420, Cuisse: 350, Tibia: 350, Pied: 100)*

### Rendu 3D Global (Conceptuel)
![Squelette Complet D-Bot](./assets/img_robot_full_skeleton.png)
*Illustration : Vue globale du squelette intégrant la cage torse en aluminium ancrée aux membres robotisés.*

## 7. Estimation du Poids de la D-Hand Hybrid

Cette section détaille l'estimation masse-par-poste du D-Hand v1 (Scénario A : phalanges ORCA + actionneurs D-Hand) en précisant les hypothèses de calcul pour chaque composant.

### 7.1 Hypothèses d'Estimation

| Hypothèse | Base de calcul |
| :--- | :--- |
| **Densité PA12-CF** | 1.01 g/cm³ (PA12 nylon standard + ~15% fibres de carbone) |
| **Densité Aluminium 6061** | 2.70 g/cm³ |
| **Densité Silicone (EcoFlex 00-30)** | ~1.07 g/cm³ |
| **Volume phalange ORCA** | Estimé d'après les dimensions normales ORCA dans le fichier STEP (longueur moy. 35 mm, section 10×12 mm, creux = ~60% plein). Volume effectif estimé ~1.5 cm³/phalange. |
| **Volume paume (Palm Block)** | Bloc alu 100×80×25 mm = 200 cm³, moins ~50% de matière usinée → ~100 cm³ effectifs |
| **Volume poulies CNC** | Cylindre Ø16mm × 8mm d'épaisseur × 8 pièces = ~1.3 cm³/poulie |

### 7.2 Tableau de Masse Poste par Poste

| Composant | Quantité | Masse unitaire | Masse totale | Source / Hypothèse |
| :--- | :---: | :---: | :---: | :--- |
| **Servomoteur XC430-T240BB-T** | 4 | 65 g | **260 g** | Datasheet Robotis (source confirmée) |
| **Servomoteur XC330-T228-T** | 4 | 23 g | **92 g** | Datasheet Robotis (source confirmée) |
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
| **TOTAL D-HAND HYBRID v1** | | | **~785 g** | |

### 7.3 Comparatif de Poids avec l'ORCA et les Concurrents

| Main | Poids Référence | Commentaire |
| :--- | :---: | :--- |
| **ORCA Hand Base (17 DOF)** | ~1 300 g | 17× Dynamixel, paume imprimée + tour |
| **ORCA Hand Lite (9 DOF)** | ~650 g | 9× Feetech, plus léger |
| **D-Hand Hybrid v1 (8 DOF)** | **~785 g** | Paume alu (plus lourde que ORCA), mais moteurs réduits de 17 → 8 |
| **Tesla Optimus Gen3** | ~800 g (estimé) | Architecture propriétaire non publiée |

> [!NOTE]
> **La paume en Aluminium CNC (+270 g)** est le poste de masse le plus élevé. Si le poids final devient critique pour l'équilibre dynamique du bras, une paume en **PA12-CF imprimée** (comme l'ORCA originale) ramènerait ce poste à ~70 g, abaissant le poids total de la main à **~585 g** — soit une réduction de 200 g.

### 7.4 Impact sur le Bras (Section 3 du document)

La D-Hand Hybrid v1 est montée à l'extrémité du bras via le poignet RS-00. Le **bras de levier dynamique** lors d'une extension horizontale complète est (axe épaule → pulpe) :

- Bras : 250 mm + Avant-bras : 220 mm + Main : 250 mm = **720 mm = 0.72 m**

Le **couple résistant** que les moteurs d'épaule doivent supporter dû au seul poids de la main (785 g ≈ 7.7 N) :

```
M_shoulder = F × l = 7.7 N × 0.72 m = 5.5 N.m
```

Ce couple de 5.5 N.m s'ajoute au poids de l'avant-bras et du bras propre et reste dans les capacités normales des moteurs d'épaule (RS-04 ou équivalent).

*Estimation D-Hand Hybrid v1, Mars 2026.*
