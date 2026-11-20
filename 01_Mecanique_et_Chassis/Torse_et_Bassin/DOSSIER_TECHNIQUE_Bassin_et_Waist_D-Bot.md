# 🦾 Dossier Technique : Bassin (Pelvis) & Liaison Active Waist Yaw — D-Bot V1.x

> **Statut** : Document de référence officiel — Conception Mécanique & Dimensionnement  
> **Auteur** : Équipe D-Bot & Pair-Programming Antigravity  
> **Date** : Novembre 2026  
> **Version** : 1.4 (Réalignement CAO Souverain `Torse-123 v42` — Architecture Pont de Hanches, Élargissement Waist 175 × 175 mm & Roulement RB8016)  
> **Système CAO** : Autodesk Fusion 360 (`Torse-123 v42` — Scale Pelvis 1.2776, Pont de Hanches 7075/6060, Interface 175 × 175 mm & Roulement CRBH 8016 / RB8016)

---

## 📑 Sommaire

- [1. Architecture Globale & Rôle Fonctionnel du Bassin](#1-architecture-globale--rôle-fonctionnel-du-bassin)
  - [1.1 Contexte Morphologique du D-Bot V1.x](#11-contexte-morphologique-du-d-bot-v1x)
  - [1.2 Le Rôle Pivot du Waist Yaw (Lacet de Taille)](#12-le-rôle-pivot-du-waist-yaw-lacet-de-taille)
  - [1.3 Le Bassin comme Nœud de Répartition Structurel](#13-le-bassin-comme-nœud-de-répartition-structurel)
- [2. Bilan Biomécanique & Cartographie Complète des Efforts](#2-bilan-biomécanique--cartographie-complète-des-efforts)
  - [2.1 Bilan des Masses Suspendues au-dessus du Waist](#21-bilan-des-masses-suspendues-au-dessus-du-waist)
  - [2.2 Charge Axiale Pure (Compression Statique & Dynamique)](#22-charge-axiale-pure-compression-statique--dynamique)
  - [2.3 Moments de Basculement Critiques (Tangage Pitch & Roulis Roll)](#23-moments-de-basculement-critiques-tangage-pitch--roulis-roll)
  - [2.4 Forces Radiales de Cisaillement](#24-forces-radiales-de-cisaillement)
  - [2.5 Couple de Rotation en Lacet (Yaw Torque)](#25-couple-de-rotation-en-lacet-yaw-torque)
- [3. Analyse Critique des Roulements & Choix Technologique](#3-analyse-critique-des-roulements--choix-technologique)
  - [3.1 Diagnostic de la Butée Axiale à Aiguilles Seule (AXK 5578 / OD78 ID55 H5)](#31-diagnostic-de-la-butée-axiale-à-aiguilles-seule-axk-5578--od78-id55-h5)
  - [3.2 Benchmark Asimov v1 : Pourquoi l'Absence de Roulement Externe est Inadaptée au D-Bot](#32-benchmark-asimov-v1--pourquoi-labsence-de-roulement-externe-est-inadaptée-au-d-bot)
  - [3.3 Roulement 4 Points Section Mince (Étude Initiale : Remplacé)](#33-roulement-4-points-section-mince-étude-initiale--remplacé)
  - [3.4 Solution Retenue : Roulement à Rouleaux Croisés CRBH 8016 (80 x 120 x 16 mm)](#34-solution-retenue--roulement-à-rouleaux-croisés-crbh-8016-80-x-120-x-16-mm)
  - [3.5 Tableau Synthétique Comparatif des Solutions de Guidage](#35-tableau-synthétique-comparatif-des-solutions-de-guidage)
- [4. Motorisation du Waist Yaw : Intégration du RobStride RS-06](#4-motorisation-du-waist-yaw--intégration-du-robstride-rs-06)
  - [4.1 Spécifications de l'Actionneur RS-06](#41-spécifications-de-lactionneur-rs-06)
  - [4.2 Platine d'Interface Waist / Traverse de Renfort Pelvis (Alu 7075-T6, 174,90 × 174,84 × 12,51 mm)](#42-platine-dinterface-waist--traverse-de-renfort-pelvis-alu-7075-t6-17490--17484--1251-mm)
  - [4.3 Schéma de Transmission & Découplage des Charges](#43-schéma-de-transmission--découplage-des-charges)
  - [4.4 Schéma Vectoriel d'Ingénierie & Détails d'Exécution CRBH 8016](#44-schéma-vectoriel-dingénierie--détails-dexécution-crbh-8016)
  - [4.5 Système de Bridage Axial Z du Roulement RB8016](#45-système-de-bridage-axial-z-du-roulement-rb8016)
    - [4.5.1 Pourquoi Augmenter le Redan de la Waist Plate de 1,5 mm à 3,0 mm ?](#451-pourquoi-augmenter-le-redan-de-la-waist-plate-de-15-mm-à-30-mm-)
    - [4.5.2 Implantation des 4 Brides Étagées en L aux 4 Coins (45°)](#452-implantation-des-4-brides-étagées-en-l-aux-4-coins-45)
    - [4.5.3 Fiche Technique Dimensionnelle Complète de la Bride en L (Fusion 360)](#453-fiche-technique-dimensionnelle-complète-de-la-bride-en-l-fusion-360)
- [5. Interfaces Mécaniques & Chaîne Cinématique Pelvienne](#5-interfaces-mécaniques--chaîne-cinématique-pelvienne)
  - [5.1 Interface Supérieure : Waist Plate 7075 (176,11 × 173,05 mm) & Équerres Basses L = 90,0 mm](#51-interface-supérieure--waist-plate-7075-17611--17305-mm--équerres-basses-l--900-mm)
    - [5.1.1 Cartographie Complète des Perçages, Vis CHC M4 & Pincement Sandwich](#511-cartographie-complète-des-perçages-vis-chc-m4--pincement-sandwich)
    - [5.1.2 Prototypage des Livrables 2D & Fabrication Assistée par API (DXF, Blueprint SVG & Fiche Atelier)](#512-prototypage-des-livrables-2d--fabrication-assistée-par-api-dxf-blueprint-svg--fiche-atelier)
  - [5.2 Le Bloc Pelvien Inférieur (Pelvis Asimov Scalé 1.2776 & Pont de Hanches `v42`)](#52-le-bloc-pelvien-inférieur-pelvis-asimov-scalé-12776--pont-de-hanches-v42)
  - [5.3 Connexion avec les Hanches en Chaîne F-A-R (RS-04 Hip Pitch)](#53-connexion-avec-les-hanches-en-chaîne-f-a-r-rs-04-hip-pitch)
    - [5.3.1 Intégration Stator RS-04 : Fixation Arrière Monoface & Dissipation Thermique Pelvienne](#531-intégration-stator-rs-04--fixation-arrière-monoface--dissipation-thermique-pelvienne)
    - [5.3.2 Intégration Rotor RS-04 : Roulement Croisé Interne & Protection par Goupilles Calibrées](#532-intégration-rotor-rs-04--roulement-croisé-interne--protection-par-goupilles-calibrées)
  - [5.4 Système de Butée Mécanique de Lacet (+/- 95°) & Sécurisation Globale](#54-système-de-butée-mécanique-de-lacet---95--sécurisation-globale)
    - [5.4.1 Architecture de Sécurisation Globale à 3 Paliers (+/- 80°, +/- 82°, +/- 95°)](#541-architecture-de-sécurisation-globale-à-3-paliers---80---82---95)
    - [5.4.2 Preuve Cinématique de Non-Interférence des 4 Écrous Nylstop M4 sous Waist Plate](#542-preuve-cinématique-de-non-interférence-des-4-écrous-nylstop-m4-sous-waist-plate)
  - [5.5 Système de Câblage à Lumières Concentriques d'Arc Arrière (Traverse 69° vs Waist Plate 125°) et Zéro Cisaillement](#55-système-de-câblage-à-lumières-concentriques-darc-arrière-traverse-69-vs-waist-plate-125-et-zéro-cisaillement)
  - [5.6 Gestion Thermique du RS-06 Waist & Ventilation du Caisson Pelvien](#56-gestion-thermique-du-rs-06-waist--ventilation-du-caisson-pelvien)
  - [5.7 Tableau Récapitulatif des Chanfreins, Fraisures & Ébavurages du Bassin & Waist](#57-tableau-récapitulatif-des-chanfreins-fraisures--ébavurages-du-bassin--waist)
- [6. Nomenclature Matérielle & Approvisionnement (BOM)](#6-nomenclature-matérielle--approvisionnement-bom)
- [7. Recommandations de Modélisation CAO Fusion 360](#7-recommandations-de-modélisation-cao-fusion-360)
  - [7.1 Import Direct du Modèle 3D CAO du Roulement (Méthode Recommandée Fusion 360)](#71-import-direct-du-modèle-3d-cao-du-roulement-méthode-recommandée-fusion-360)
  - [7.2 Procédure de Modélisation & Assemblage Sous Fusion 360](#72-procédure-de-modélisation--assemblage-sous-fusion-360)
  - [7.3 Modélisation du Moyeu d'Accouplement & Pincement Sandwich (Alu 7075-T6)](#73-modélisation-du-moyeu-daccouplement--pincement-sandwich-alu-7075-t6)
  - [7.4 Tableau des Références McMaster-Carr pour Modélisation CAO Fusion 360 (Bassin & Waist)](#74-tableau-des-références-mcmaster-carr-pour-modélisation-cao-fusion-360-bassin--waist)
  - [7.5 Tableau Synthétique des Couples Dynamométriques & Outillage d'Atelier (Bassin & Waist)](#75-tableau-synthétique-des-couples-dynamométriques--outillage-datelier-bassin--waist)
- [8. Checklist de Contrôle & Métrologie Avant Usinage C500](#8-checklist-de-contrôle--métrologie-avant-usinage-c500)

---

## 1. Architecture Globale & Rôle Fonctionnel du Bassin

### 1.1 Contexte Morphologique du D-Bot V1.x

Le robot humanoïde bipède **D-Bot V1.x** est dimensionné selon les caractéristiques anthropomorphes suivantes :
- **Hauteur totale** : `~1,58 m` — En CAO active **`Torse-123 v42`**, le sous-ensemble **Torse + Bassin** présente une **hauteur physique réelle (feuilles visibles) de `832,95 mm`** sur plage `Z: [714,17 ; 1547,12 mm]` (`890,76 mm` selon la boîte englobante brute `physical_components_bounding_box_mm`, qui inclut l'enveloppe d'origine/esquisse du conteneur vide `Ensemble hanche:1` descendant à `Z = 656,36 mm`).
- **Masse totale de référence** : Robot complet estimé à **`~38–40 kg`** (châssis hybride Alu 7075/6060 + PA12-CF, 26 actionneurs RobStride QDD dont **`1x RobStride RS-05 (réf. constructeur / CAO : EL05 / EL05_ASM_1_ASM)`** Pan cou modélisé dans `Torse-123 v42` + 2e RS-05 Tilt dans `02_Tete_et_Cou`, 2 packs batteries 12S Li-Ion, préhenseurs D-Hand). En CAO active `Torse-123 v42`, l'ensemble **Torse + Bassin** mesure **`18 316,38 g` (`18,32 kg`) bruts** (`~16,1–16,2 kg` théoriques une fois les 20 pièces/sous-corps PA12-CF restants calibrés depuis `rho = 1,015 g/cm3` vers la densité gyroïde réelle, seule `Chassis_Structurel_Bassin_Last` étant déjà calibrée à `0,700 g/cm3` / `441,36 g`).
- **Origine CAO du torse et du bassin** : Dérivés des fichiers open-source du projet **Asimov v1** (Menlo Research), soumis à un **scale uniforme de facteur 1,2776** sur le caisson pelvien et à un évasement de l'interface basse du torse à **`175 × 175 mm`** afin d'intégrer le squelette porteur **« Pont de Hanches »** (`Tube 60x60 L=46,33 mm`, `Selle de Pont`, `2x Brides v87`) et les gros actionneurs d'épaules et de hanches **RobStride RS-04** (`120 N.m` pic).
- **Envergure médio-latérale du Pelvis (Y)** : **`487,06 mm`** hors-tout en CAO `v42` (`Y: [-245,87 ; +241,19 mm]` au niveau des capots/supports externes `ASV1_200`, marqués *en cours de définition côté CAO — non définitifs*, tandis que les 2 actionneurs `RS-04` Hip Pitch portés par le Pont de Hanches sont recentrés sur le berceau métallique).

![Architecture Vectorielle du Bassin et Liaison Waist Yaw](./media/architecture_bassin_waist_yaw_roulement.svg)

*Blueprint d'ingénierie vectoriel officiel du bloc pelvien et de la liaison active Waist Yaw (D-Bot V1.x). Panel 1 : Coupe axiale montrant le découplage mécanique entre la reprise des moments de basculement (56 à 220 N.m) par le roulement à rouleaux croisés CRBH 8016 / RB8016 (`80 × 120 × 16 mm`) et la transmission du couple pur (36 N.m) par le moteur RobStride RS-06 centré via son Moyeu Sandwich CNC Alu 7075-T651. Panel 2 : Architecture pelvienne en vue de face en chaîne cinématique F-A-R (RS-04 Pitch ➔ RS-03 Roll ➔ RS-03 Yaw, enveloppe Y = 487,06 mm). Panel 3 : Expertise critique des roulements comparant l'inadéquation de la butée AXK 5578 seule face au roulement CRBH 8016 retenu.*

### 1.2 Le Rôle Pivot du Waist Yaw (Lacet de Taille)

L'articulation du **Waist Yaw (rotation Z de la taille)** assure une fonction essentielle dans la commande globale du robot (Whole-Body Control / WBC) :
1. **Dissociation Locomotion / Manipulation** : Permet au haut du corps d'orienter le buste et les deux bras vers une zone de travail (table, étagère, préhension asymétrique) pendant que le bassin et les jambes maintiennent une trajectoire de marche stable en ligne droite.
2. **Compensation du Moment Cinétique (Balancement)** : Lors de la marche dynamique, l'oscillation en contre-phase du buste et des bras permet d'annuler une partie du moment d'inertie de lacet produit par les jambes en mouvement alternatif, réduisant l'effort nécessaire au sol pour ne pas dévier de cap.
3. **Réduction de la Dépense Énergétique** : Évite de devoir faire tourner l'ensemble du robot "en crabe" ou en pas chassés pour des ajustements d'orientation du haut du corps de +/- 45°.

### 1.3 Le Bassin comme Nœud de Répartition Structurel

Le bassin mécanique (Pelvis) constitue le carrefour le plus sollicité de tout le robot :
- Il reçoit **vers le haut** l'intégralité du poids et des moments de basculement du torse, des bras et de la tête via la **Waist Plate** et la liaison pivot de taille.
- Il transmet **vers le bas** l'ensemble des charges aux deux jambes via les actionneurs **RS-04 Hip Pitch** fixés sur ses flancs droit et gauche (envergure transversale `Y = 487,09 mm`).
- Il héberge les répartiteurs de puissance électrique secondaire (mini-busbars 6 bornes 60V pour la distribution vers les membres inférieurs).

---

## 2. Bilan Biomécanique & Cartographie Complète des Efforts

### 2.1 Bilan des Masses Suspendues au-dessus du Waist

Toutes les masses situées au-dessus du plan de joint de la taille sont intégralement portées par le module Waist Yaw. Le tableau ci-dessous détaille cette masse suspendue en configuration V1 officielle :

| Sous-Système | Composants Inclus | Masse Estimée |
| :--- | :--- | :---: |
| **Squelette Métallique Torse V2 (Alu 7075/6060)** | Colonne sagittale, brides monoblocs, traverses tube carré, inserts, éclisses, équerres, tuyères, ventilateurs, visserie | `1 763 g` |
| **Coques & Carénages Abdominaux** | Coques imprimées PA12-CF (Thorax, Abdomen) | `1 000 g` |
| **Moteurs d'Épaules & Bras (x2)** | 2x RS-04 Pitch, 2x RS-03 Roll, 2x RS-02 Yaw, 2x RS-03 Coude, 2x RS-10P Sup *(Option B reçue)*, 2x RS-00 | `8 530 g` |
| **Membres Supérieurs (Bras Carbone & D-Hand)** | Tubes carbone 3K, brides alu, 2 mains D-Hand Hybrid Premium | `2 100 g` |
| **Tête & Cou** | 2x moteurs RS-05, équerres cou, caméra RGB-D RealSense, structure tête | `1 150 g` |
| **Pack Énergie Torse (Batteries 12S)** | 2 packs Li-Ion 12S / 50V montés en paniers latéraux hot-swap | `1 600 g` |
| **Électronique & Câblage Haut** | Jetson Orin Nano / AGX, PDB haute puissance, diodes ORing, faisceaux | `950 g` |
| **Marge & Quincaillerie Non Comptée** | Marge forfaitaire câbles, capteurs, fixations diverses | `350 g` |
| **TOTAL MASSE SUSPENDUE (Haut du Corps)** | **Torse V2 + Bras + Tête + Énergie + Calcul** | **`~17 443 g (~17,4 kg)`** |

> [!NOTE]
> **Révision & Réconciliation CAO (`Torse-123 v42`)** : Le bilan de masse ci-dessus représente l'enveloppe **robot complet** au-dessus du Waist (incluant bras complets `~2,1 kg` + tête + batteries + électronique haute) pour un dimensionnement RDM conservatif sur `18,3 kg`. En CAO active **`Torse-123 v42`** (qui inclut Torse + Bassin + 4× RS-04 + RS-06 + **`1× EL05 / RS-05 Pan cou`**, hors bras/jambes), la masse totale mesurée est de **`18 316,38 g` (`18,32 kg`) bruts** (`~16,1–16,2 kg` calibrés une fois les 20 pièces/sous-corps PA12-CF encore à `rho = 1,015 g/cm3` ajustés au gyroïde 15 %, soit `-2,1 à -2,3 kg`). Tous les calculs d'efforts et de moments ci-dessous restent donc strictement conservatifs.

### 2.2 Charge Axiale Pure (Compression Statique & Dynamique)

- **Effort Axial Statique (F_z_stat)** :
  `F_z_stat = m_suspendue * g = 18,3 kg * 9,81 m/s^2 = 179,5 N (~180 N)`
- **Facteur d'Accélération Dynamique (Marche & Réception de Saut)** :
  Lors de la marche normale, les accélérations verticales alternées introduisent un facteur de charge de `1,5 à 2,0 g`. En cas de trébuchement, d'arrêt d'urgence ou de choc dynamique, le facteur d'impact atteint couramment `3,0 g`.
  `F_z_dyn_max = 3,0 * F_z_stat = 3,0 * 180 N = 540 N`

> **Constat Axial** : La force de compression verticale pure (`180 N` statique, `540 N` pic dynamique) est modérée. N'importe quel roulement à aiguilles ou à billes du commerce reprend plusieurs kilonewtons en compression pure. **Le véritable défi mécanique ne se situe pas là.**

### 2.3 Moments de Basculement Critiques (Tangage Pitch & Roulis Roll)

Le centre de gravité (CdG) du haut du corps est situé à environ `h_CdG = 220 à 250 mm` au-dessus de la Waist Plate. De plus, les bras peuvent s'étendre horizontalement en avant ou sur les côtés (portée `~0,55 m`), portant des charges utiles (manipulation de charges jusqu'à 3 kg par main).

#### A. Moment de Tangage Sagittal (Pitch — Avant / Arrière)
- **Posture Droite (Statique)** : En posture neutre, un léger désalignement de 30 mm du CdG produit :
  `M_pitch_statique = 180 N * 0,03 m = 5,4 N.m`
- **Flexion du Buste en Avant (30° d'inclinaison)** : Le CdG avance de `~120 mm` :
  `M_pitch_flexion = 180 N * 0,12 m = 21,6 N.m`
- **Deux Bras Tendus Portant 2 kg Chacun** :
  `M_pitch_bras = (2 bras * 1,2 kg + 2 charges * 2,0 kg) * 9,81 * 0,55 m = 6,4 kg * 9,81 * 0,55 m = 34,5 N.m`
  `M_pitch_total = 21,6 + 34,5 = 56,1 N.m`
- **Accélération / Décélération Brusque (Freinage d'Urgence)** :
  Une décélération horizontale de `1,0 g` sur le buste à `h = 0,25 m` de la taille génère :
  `M_pitch_choc = 180 N * 0,25 m = 45 N.m` (qui s'additionne au moment de flexion).
- **Moment Sagittal Pic de Calcul (Dimensionnement Châssis Torse V2)** :
  La colonne vertébrale est calculée pour un choc de basculement extrême de **`275 N.m`** (facteur de sécurité `Sf = 12,58` dans l'Alu 7075-T6).

#### B. Moment de Roulis Frontal (Roll — Gauche / Droite)
- **Marche sur une Jambe d'Appui (Single Support Phase)** :
  Le bassin bascule latéralement de 2 à 5°. Pour stabiliser le buste, le robot compense par un moment latéral :
  `M_roll_marche = 25 à 45 N.m`
- **Port de Charge Asymétrique (3 kg dans une seule main, bras tendu à 0,50 m)** :
  `M_roll_charge = (3,0 kg + 1,2 kg bras) * 9,81 * 0,50 m = 20,6 N.m`
- **Moment Frontal Pic Combiné** :
  `M_roll_pic = 60 à 110 N.m`

### 2.4 Forces Radiales de Cisaillement

Les accélérations latérales et sagittales lors des transferts d'appui de la marche bipède exercent un cisaillement horizontal direct sur la liaison rotative :
`F_radial_dyn = m_suspendue * a_transversale = 18,3 kg * (0,5 à 1,0 g) = 90 à 180 N` (avec des pics à `~300 N` lors des impacts au sol).

### 2.5 Couple de Rotation en Lacet (Yaw Torque)

- **Couple résistant en rotation pure** : Généré par l'inertie de rotation du buste (`I_zz ~ 0,18 kg.m^2`) lors des accélérations angulaires rapides (`alpha = 20 à 50 rad/s^2`) :
  `T_yaw_dyn = I_zz * alpha = 0,18 * 50 = 9,0 N.m`
- **Couple Pic Prévu pour le Moteur RS-06** : **`36 N.m`** (avec un couple continu nominal de **`11 N.m`**).
  Le ratio de couple disponible / couple requis est :
  `Ratio = 36 N.m / 9 N.m = 4,0 (Marge de sécurité confortable de 300 %)`

---

## 3. Analyse Critique des Roulements & Choix Technologique

### 3.1 Diagnostic de la Butée Axiale à Aiguilles Seule (AXK 5578 / OD78 ID55 H5)

La référence `THRUST-BEARING-OD78ID55H5` correspond au standard ISO **AXK 5578** (cage à aiguilles axiale `55 × 78 × 3 mm` accompagnée de deux rondelles de roulement trempées `AS 5578` de 1 mm, épaisseur totale = `5,00 mm`).

*(Voir l'illustration détaillée du phénomène de décollement dans le **Panneau 3 du blueprint vectoriel** ci-dessus).*

#### Diagnostic d'Inadéquation de l'AXK 5578 Seule à la Taille :
1. **Zéro Reprise Radiale (0 N)** : Une butée axiale n'a strictement aucun épaulement de guidage radial. Les rondelles plates glisseraient librement sur le plan XY sous le moindre effort de cisaillement transversal (`90 à 300 N`), désaxant immédiatement le rotor du moteur RS-06 et endommageant ses réducteurs planétaires.
2. **Fonctionnement Unidirectionnel Ouvert (Décollement sous Moment)** : Une butée axiale ne travaille qu'en compression pure d'un seul côté. Dès qu'un moment de tangage (`M_pitch > 5,4 N.m`) est appliqué :
   - Le bord avant de la butée encaisse toute la charge en contrainte locale ponctuelle.
   - Le bord arrière **se décolle physiquement de son appui** car la butée est incapable d'exercer la moindre traction.
   - Il en résulte un **jeu angulaire majeur**, le buste du robot bascule d'avant en arrière comme une charnière branlante, rendant impossible tout équilibrage par le contrôleur RL.
3. **Risque Mortel pour l'Actionneur RS-06** : Si la butée n'empêche pas le basculement, c'est le petit roulement interne du moteur RobStride RS-06 qui se retrouve à encaisser le moment de flexion de `50 à 110 N.m`, entraînant la destruction des roulements internes du moteur et la casse des satellites du réducteur.

> [!CAUTION]
> **Conclusion Formelle** : Le roulement à aiguilles `AXK 5578` **ne peut absolument pas être utilisé seul** pour assurer la liaison rotative du Waist. Il exigerait l'ajout d'au minimum deux roulements rigides à billes à gorge profonde supplémentaires pour le guidage radial et d'un système de précharge bilatérale complexe, annulant tout gain d'encombrement.

---

### 3.2 Benchmark Asimov v1 : Pourquoi l'Absence de Roulement Externe est Inadaptée au D-Bot

L'inspection approfondie du modèle CAO d'origine de l'**Asimov v1** (Menlo Research) montre que la plaque inférieure du torse est vissée directement sur la bride de sortie d'un gros actionneur modulaire intégré (type AK80 / Unitree), sans roulement auxiliaire externe :

1. **Le Contexte Spécifique d'Asimov v1** :
   - Le robot Asimov d'origine est un prototype de laboratoire de dimension modeste (1,20 m, ~30-35 kg), doté d'un haut de corps très compact (< 14 kg).
   - L'actionneur employé intègre d'origine un roulement de sortie renforcé à double rangée de billes ou à contact oblique capable de tolérer des moments légers à faible vitesse.
   - Les concepteurs ont visé un compromis d'extrême compacité axiale (zéro millimètre ajouté en Z) au détriment de la rigidité sous forte dynamique.

2. **Pourquoi D-Bot V1.x Ne Peut Pas Adopter ce Montage Direct** :
   - **Masse Suspendue Élevée** : Le torse du D-Bot est agrandi de **+18 %**, pèse **18,3 kg** suspendus (avec deux packs 12S Li-Ion en fond de coffre et des bras de 55 cm portant des charges).
   - **Moteur RobStride RS-06 Ultra-Compact** : Le RS-06 (621 g, Ø 88 mm) a été choisi pour son ratio couple/masse exceptionnel (36 N.m pic), mais ses roulements internes sont petits et optimisés pour la rotation, pas pour faire office de palier structural de tout le squelette.
   - **Conclusion Mécanique** : Confier les 18,3 kg et les moments de basculement de `56 à 220 N.m` aux seuls roulements internes du RS-06 provoquerait un matage rapide des pistes, l'arc-boutement des satellites planétaires et une destruction rapide de l'actionneur.

---

### 3.3 Roulement 4 Points Section Mince (Étude Initiale : Remplacé)

> [!NOTE]
> **Section conservée pour traçabilité.** L'étude initiale préconisait un roulement à 4 points de contact section mince (Ø int 90 mm, Ø ext 110 mm, ép 10 mm, type CSXB / Kaydon Reali-Slim). Cependant, **aucune référence standard n'existe en ces dimensions exactes**. Les séries CSXB ont des cotes impériales (pouces), et la conversion la plus proche ne correspond pas aux cotes métriques spécifiées. Le sourcing s'est avéré impossible dans des délais et coûts raisonnables. Cette solution est donc **remplacée** par le roulement à rouleaux croisés CRBH 8016 (section 3.4).

Les principes d'ingénierie restent valides :
1. **Géométrie en Arc Gothique** : Chaque bille en contact en 4 points simultanés avec les bagues (traction + compression bilatérale).
2. **Reprise simultanée des 3 composantes d'efforts** : axiale, radiale, et moment de basculement.
3. **Section mince → grand alésage central** pour le passage des câbles.

---

### 3.4 Solution Retenue : Roulement à Rouleaux Croisés CRBH 8016 (80 x 120 x 16 mm)

Après étude de sourcing approfondie (Septembre 2026), la solution retenue pour le D-Bot est un **roulement à rouleaux croisés standard industriel** :

#### Référence Validée : CRBH 8016 UU (ou équivalent RB 8016 UU)

| Paramètre | Valeur |
| :--- | :---: |
| **Diamètre Intérieur (Ø int)** | **`80 mm`** |
| **Diamètre Extérieur (Ø ext)** | **`120 mm`** |
| **Épaisseur (B)** | **`16 mm`** |
| **Type de Roulement** | Rouleaux croisés 90 deg, bagues intégrales (non fendu) |
| **Joints** | UU (joints des 2 côtés, protection poussière) |
| **Classe de Précision** | **P5** minimum (runout < 0,01 mm) |
| **Matériau** | Acier à roulement GCr15 trempé (62 HRC) |
| **Charge Axiale Dynamique (Ca)** | ~22 kN |
| **Charge Radiale Dynamique (Cr)** | ~15 kN |
| **Moment de Basculement Statique (M0)** | **~520 N.m** |
| **Rigidité en Basculement** | ~250 N.m/arcmin |
| **Masse** | ~250-350 g |
| **Passage Central Câbles** | **Ø 80 mm** (largement > 40 mm requis) |

#### Pourquoi les Rouleaux Croisés sont Supérieurs au 4 Points :
1. **Rigidité torsionnelle 3 à 4 fois supérieure** au roulement à billes : les rouleaux cylindriques disposés en croix à 90 deg dans une gorge en V unique offrent une déformation élastique quasi-nulle sous fort moment de basculement.
2. **Capacité en moment de basculement : 520 N.m** (vs ~300 N.m pour un 4 points de section comparable), soit un facteur de sécurité de **x2,36** face au pire cas D-Bot (arrêt d'urgence à 220 N.m).
3. **Standard industriel immédiatement disponible** : Référence de catalogue (THK, IKO, génériques Luoyang), disponible sur AliExpress pour **60 à 90 EUR** en 2-4 semaines.
4. **Technologie de référence en robotique humanoïde** : Les robots Unitree H1/G1, Figure 02, et Tesla Optimus utilisent tous des rouleaux croisés pour leurs articulations à forte charge.

#### Sourcing Validé (Septembre 2026)

| Fournisseur | Plateforme | Recherche / Référence | Prix Estimé | Délai |
| :--- | :--- | :--- | :---: | :---: |
| **Luoyang (Chine)** | [AliExpress](https://www.aliexpress.com) | Rechercher **"CRBH8016 UU crossed roller bearing P5"** | **40 à 90 EUR** | 2-4 sem. |
| **123Roulement (France)** | [123roulement.com](https://www.123roulement.com) | Contacter le service client : **"CRBH 8016 UU"** | **150 à 350 EUR** (devis) | 2-6 sem. |
| **Rubix (France)** | [rubix.com/fr](https://www.rubix.com/fr-fr/) | Devis **"Roulement rouleaux croisés 80x120x16"** | **200 à 400 EUR** | 3-6 sem. |
| **MISUMI Europe** | [misumi-ec.com](https://www.misumi-ec.com) | Configurateur série THK **RB 8016** | **250 à 500 EUR** | 2-4 sem. |

> [!IMPORTANT]
> **Statut Réception & Métrologie Réelle (Validé en Atelier au 25 Septembre 2026)** :  
> Le roulement **RB8016** est **✅ REÇU ET CONTRÔLÉ EN ATELIER**.  
> Le certificat officiel d'inspection d'usine émis par **LUOYANG E-FIND PRECISION BEARING MANUFACTURING CO., LTD (EFANT)** (Rapport Test N° 01 du 15/09/2026, tamponné par le Département Qualité) confirme une précision métrologique remarquable de classe **P4 / P2** :
> * **Diamètre Intérieur (d)** : Standard `80 mm (0 / -0,008 mm)` ➔ **Mesuré réel = `79,996 mm`** (Écart de seulement -4 µm vs nominal, ajustement glissant doux parfait avec le fût du Moyeu Sandwich).
> * **Diamètre Extérieur (D)** : Standard `120 mm (0 / -0,010 mm)` ➔ **Mesuré réel = `119,995 mm`** (Écart de seulement -5 µm vs nominal, ajustement H7/h6 idéal dans le lamage de Traverse).
> * **Hauteur de Montage (B)** : Standard `16 mm (0 / -0,075 mm)` ➔ **Mesuré réel = `15,965 mm`** (Écart de -35 µm).
> * **Hauteur de Montage (B1)** : Standard `16 mm (0 / -0,100 mm)` ➔ **Mesuré réel = `15,955 mm`** (Écart de -45 µm).
> * **Battement Radial Intérieur (Kia)** : Standard <= 0,005 mm ➔ **Mesuré réel = `0,003 mm` (3 µm !)**
> * **Battement Axial Intérieur (Sia)** : Standard <= 0,005 mm ➔ **Mesuré réel = `0,003 mm` (3 µm !)**
> * **Conclusion Usine** : **合格 (Conforme / Passed)**.
>
> ![Rapport de Contrôle Métrologique EFANT Luoyang — Roulement RB8016](./media/test_report_efant_rb8016.jpg)
> *Certificat officiel d'inspection d'usine Luoyang E-Find Precision Bearing (EFANT) — RB8016 réceptionné pour le D-Bot (15/09/2026).*

---

### 3.5 Tableau Synthétique Comparatif des Solutions de Guidage

| Critère Mécanique | Butée Aiguilles AXK 5578 (Seule) | Montage Direct sur Moteur (Asimov v1) | ~~Roulement 4 Pts Section Mince~~ | **Rouleaux Croisés CRBH 8016 ✅** |
| :--- | :---: | :---: | :---: | :---: |
| **Reprise Charge Axiale (F_z)** | Excellente (> 100 kN) | Modérée (~1,5 kN) | ~~Excellente (> 20 kN)~~ | **Exceptionnelle (> 22 kN)** |
| **Reprise Charge Radiale (F_xy)** | **NULLE (0 N) ❌** | Modérée (~1 kN) | ~~Excellente (> 10 kN)~~ | **Exceptionnelle (> 15 kN)** |
| **Reprise Moment Basculement** | **NULLE (Décollement) ❌** | Faible (< 40 N.m) | ~~> 300 N.m~~ | **> 520 N.m ✅** |
| **Protection du Moteur RS-06** | Nulle (Moteur détruit) | Nulle (Moteur en direct) | ~~100% découplé~~ | **100% découplé ✅** |
| **Jeu Angulaire sous Moment** | Inacceptable (Bascule) | Prise de jeu progressive | ~~Zéro (précharge)~~ | **Zéro absolu (ultra-rigide) ✅** |
| **Passage Central Câblage** | Moyen (Ø 55 mm) | Restreint | ~~Ø 90 mm~~ | **Ø 80 mm ✅** |
| **Hauteur / Épaisseur Z** | Ultra-fine (5 mm) | Nulle (0 mm) | ~~10 mm~~ | **16 mm** (compensé par la Platine) |
| **Disponibilité Marché** | Standard | N/A | ~~Introuvable ❌~~ | **Standard industriel ✅** |
| **Prix** | ~10 EUR | 0 EUR | ~~Inconnu (custom)~~ | **60-90 EUR ✅** |
| **Verdict D-Bot V1.2** | **REJETÉ ❌** | **REJETÉ ❌** | **REMPLACÉ** | **SOLUTION OFFICIELLE ✅** |

---

## 4. Motorisation du Waist Yaw : Intégration du RobStride RS-06

### 4.1 Spécifications de l'Actionneur RS-06

L'actionneur **RobStride RS-06** a été sélectionné, commandé et validé pour motoriser l'axe Waist Yaw :
- **Technologie** : Moteur synchrone sans balais à aimants permanents avec réducteur planétaire intégré (Quasi-Direct Drive — QDD).
- **Couple Maximal (Pic)** : **`36 N.m`**.
- **Couple Continu (Nominal)** : **`11 N.m`**.
- **Vitesse Maximale** : **`~31 rad/s (300 rpm)`**.
- **Diamètre Extérieur Carter (Stator)** : **`Ø 85,3 mm` (encombrement CAO `v42` `85,31 × 83,58 × 50,54 mm`, bride Ø 88,0 mm)**.
- **Hauteur / Épaisseur Totale** : **`50,54 mm`** hors-tout en CAO `v42` (`Z = [958,90 ; 1009,44 mm]`).
- **Masse** : **`550,97 g`** mesurés en CAO `Torse-123 v42` (`~551–621 g` selon faisceau/visserie).
- **Protocole de Communication** : CAN-FD haute vitesse, identifiant officiel : **`ID CAN = 21`** (terminaison 120 ohms intégrée ou chaînée).

### 4.2 Platine d'Interface Waist / Traverse de Renfort Pelvis (Alu 7075-T6, 174,90 × 174,84 × 12,51 mm)

> [!NOTE]
> **Révision V1.4 (Conforme CAO `Torse-123 v42`, Élargissement 175 × 175 mm, Squelette Pont de Hanches & Vis CHC M3 Tête Basse DIN 7984)** : 
> 1. **Usinage direct in-situ & Élargissement** : La platine est issue de la plaque supérieure du bassin (`Traverse_Renfort_Bassin [ASV1_200_16A]:1`), au format quasi-carré de **`174,90 × 174,84 mm`** (épaisseur brute `10,02 mm` en périphérie, portée à `12,51 mm` au centre via bossage inférieur ; masse brute historique pré-évidement = `617,39 g`, masse réelle certifiée CAO **`Torse-123 v42` = `566,74 g`**, volume `201,69 cm3`). Elle repose désormais sur les **4 `Montants de Hanche 20×20×2` (`L = 65,77 mm`)** du squelette **Pont de Hanches**.
> 2. **Fixation directe du Stator RS-06 & Bossage Inférieur 2,49 mm (Option 1 Validée)** : La face inférieure de la traverse reçoit un bossage cylindrique descendant de `2,49 mm` (cote `Z = 1007,90 mm`) qui comble l'entrefer axial et vient plaquer en **contact franc métal-métal** sur le sommet du stator du RobStride RS-06 (`Z_max = 1009,44 mm`). L'alésage est étagé en 4 gradins fonctionnels :
>    - **Étage 1 — Siège Supérieur Roulement** : `Ø 120,00 mm H7` (prof. `3,00 mm`, de `Z = 1020,41 mm` à `Z = 1017,41 mm`) pour loger et caler la bague extérieure du CRBH 8016 UU (`Z = [1017,40 ; 1033,44 mm]`).
>    - **Étage 2 — Chambre de Dégagement Collerette Moyeu** : `Ø 96,00 mm` (de `Z = 1017,41 mm` à `Z = 1010,93 mm`) ménageant un jeu radial franc de `2,25 mm` autour de la collerette tournante (Ø 91,52 mm) du `Moyeu_Waist_Sandwich_7075`.
>    - **Étage 3 — Collerette Fixe de Bridage Stator & Vis Tête Basse** : Plan d'appui des têtes de vis à `Z = 1010,93 mm` (épaisseur saine de bride sous tête = `3,03 mm`) percé de **8 trous lisses Ø 3,50 mm sur PCD `Ø 82,00 mm`** avec lamages cylindriques **`Ø 6,00 mm`**. La fixation réelle exige **8 vis CHC M3 × 12 mm Tête Basse DIN 7984 Inox 18-8** (McMaster-Carr `92855A313` ; `1` instance représentative insérée dans la BOM CAO `v42`, `8` au montage atelier). Les têtes (hauteur 2,00 mm, Ø 5,50 mm, sommet à `Z = 1012,93 mm`) ménagent un **entrefer vertical de sécurité franc (Air Gap) de `1,48 mm (~1,5 mm)`** sous la collerette tournante du Moyeu Sandwich.
>    - **Étage 4 — Alésage Central Traversant Passage Rotor** : **`Ø 74,56 mm`** (de `Z = 1010,93 mm` à `Z = 1007,90 mm`), laissant un jeu radial franc de **`11,28 mm`** autour du bossage rotor et du col inférieur du Moyeu Sandwich.
> 3. **Fixation Pelvis / Pont de Hanches sur 4 vis d'angles FHC M5 affleurantes (Validée `v42`)** : Les 4 trous d'angles (R = 78,67 mm à 45°) sont fraisés à 90° (`Ø 10,40 mm × prof. 3,10 mm`) pour vis FHC M5 affleurantes à **0,0 mm**, préservant la libre rotation de la Waist Plate. Dans l'architecture finale **Pont de Hanches (`Torse-123 v42`)**, ces 4 perçages reçoivent **4 vis `FHC M5 × 18 mm [92125A213]`** taraudées directement dans les **4 `Inserts Hanche Haut [ASV1_200_13]`** (`9,25 g`/u) logés au sommet des montants `20×20×2` *(sur la variante historique à coque porteuse PA12-CF seule, 4 vis `FHC M5 × 25 [92125A230]` traversaient le plafond PA12-CF vers 4 écrous hex `[90631A113]` en poches de 8,50 mm)*.
> 4. **Intégration de la Lumière Concentrique d'Arc Arrière & Congés R1.5** : La Traverse intègre en zone postérieure (-X) la fente en arc de cercle concentrique de **`69,05°`** (R_int = 64,75 mm, R_ext = 84,75 mm, largeur 20,0 mm, congés d'extrémités Ø 16 mm, congés d'arêtes R = 1,5 mm sur faces supérieure et inférieure) centrée sur l'axe du rotor RS-06 (`X = +49,23 mm, Y = +9,36 mm`), garantissant une assise rigide et un passage fluide sans frottement.

![Plan d'Ingénierie Waist Élargie 175×175 mm, Lumières Concentriques d'Arc et Course +/- 80°](./media/plan_waist_elargie_v102.svg)

*Plan d'ingénierie vectoriel officiel de la Traverse et de la Waist Plate (Alu 7075-T651, réaligné CAO **`Torse-123 v42`**). Panneau 1 : Vue de dessus montrant le format extérieur de 174,90 × 174,84 mm, l'implantation de la lumière arrière concentrique de 69,05° sur la Traverse fixe et de 125,05° sur la Waist Plate tournante (R = 64,75 à 84,75 mm, largeur 20 mm, centrage rigoureux à X = +49,23 mm, Y = +9,36 mm), le passage libre du faisceau Ø 15 mm sur une course de +/- 80°, les 4 vis d'angles FHC M5 affleurantes à 0,0 mm (`FHC M5×18 [92125A213]` sur Pont de Hanches), les 4 taraudages M4 des brides en L sur PCD Ø 136 mm, la chambre de dégagement Ø 96 mm du moyeu, le cercle de bridage stator (8× CHC M3×12 Tête Basse DIN 7984 sur PCD Ø 82 mm) et l'alésage central traversant Ø 74,56 mm. Panneau 2 : Coupe axiale X-Z révélant l'empilement avec saillie de 13 mm, bride en L, entrefer de 1,0 mm sous la Waist Plate et congés R = 1,5 mm sur arêtes des lumières. Panneau 3 : Fiche technique métrologique actualisée **`v42`** (**Waist Plate = `433,53 g`**, **Traverse = `566,74 g`**) et visserie normalisée McMaster-Carr.*

#### Contexte Dimensionnel & Origine Asimov :
Le châssis pelvien comporte une plaque supérieure de renfort et de fermeture (`Traverse_Renfort_Bassin` / `ASV1_200_16A`). Élargie à **`174,90 × 174,84 mm`** de largeur avec une épaisseur périphérique de **`10,02 mm`** (portée à **`12,51 mm`** au centre par le bossage inférieur), cette pièce est **directement usinée in-situ pour former la Platine d'Interface Waist D-Bot**, garantissant une continuité structurelle et thermique maximale.

#### Définition Métrologique Conforme CAO `Torse-123 v42` :
- **Matière** : Aluminium **7075-T6** (masse réelle certifiée CAO **`Torse-123 v42` = `566,74 g`**, volume = `201,69 cm3`, `Z = [1007,90 ; 1020,41 mm]`).
- **Format Extérieur Fini** : Quasi-carré aux coins arrondis de **`174,90 mm × 174,84 mm (+/- 0,2 mm)`**.
- **Épaisseur Finie** : **`10,02 mm (+/- 0,05 mm)`** en périphérie (appui sur les 4 `Montants 20×20` / `Inserts Hauts` à `Z = 1010,41 mm`), **`12,51 mm`** au centre via bossage descendant de `2,49 mm` (face inférieure d'appui stator à `Z = 1007,90 mm`).
- **Distance de Contact Stator** : Contact rigide métal-métal franc et direct à `Z = 1007,90–1009,44 mm`.
- **Alésage Central Traversant (Passage Rotor RS-06 & Col Moyeu)** : **`Ø 74,56 mm (+0,05 / 0,00)`** — de `Z = 1010,93 mm` à `Z = 1007,90 mm`. Laisse un jeu radial franc de **`11,28 mm`** autour du bossage rotor Ø 52,0 mm et de la liaison vissée basse du `Moyeu_Waist_Sandwich_7075`.
- **Fixation Stator RS-06 (Collerette de Bridage Intégrée & DIN 7984)** :
  - **8 vis à tête cylindrique basse DIN 7984 CHC M3 × 12 mm en Inox 18-8** (McMaster-Carr **`92855A313`** — `1` vis repère modélisée dans la BOM `v42`, **`8` requises au montage**).
  - **Cercle primitif** : **`PCD Ø 82,00 mm (+/- 0,05 mm)`** (`R = 41,00 mm`), 8 trous orientés à `22,5°`, `67,5°`, `112,5°`, `157,5°`, `202,5°`, `247,5°`, `292,5°` et `337,5°`.
  - **Lamages cylindriques de dégagement de tête (face supérieure à Z = 1010,93 mm)** : Diamètre **`Ø 6,00 mm`**, logeant avec aisance la tête de vis DIN 7984 (diamètre de tête **`5,50 mm`**, hauteur de tête **`2,00 mm`**).
  - **Épaisseur de matière bridée sous tête** : `1010,93 - 1007,90 =` **`3,03 mm`** d'Alu 7075-T6 plein.
  - **Implantation filetée dans le stator RS-06** : `12,00 - 3,03 =` **`8,97 mm (~9,0 mm)`** de filet utile dans les taraudages M3 borgnes du carter moteur.
  - **Couple de serrage & RDM** : Serrage dynamométrique calibré à **`1,3 à 1,4 N.m`** (clé Allen 2,0 mm + Loctite 243). Cisaillement sous couple de crête (36 N.m) : `tau = 21,8 MPa` (limite admissible 545 MPa, **facteur de sécurité Sf = 25,0**). Précharge globale de 15,2 kN conférant un couple transmissible par pure adhérence de **`93,5 N.m`** (2,6 fois le couple de choc maxi).
- **Chambre de Dégagement Collerette Moyeu** : **`Ø 96,00 mm`**, profondeur `6,48 mm` (de `Z = 1017,41 mm` à `Z = 1010,93 mm`). Offre un jeu radial de `2,24 mm` autour de la collerette tournante (Ø 91,52 mm) et un **jeu axial de sécurité franc de `1,48 mm (~1,5 mm)`** au-dessus des têtes de vis DIN 7984 (sommet à `Z = 1012,93 mm`, collerette moyeu à `Z = 1014,41 mm`). Zéro frottement garanti.
- **Siège Roulement (Lamage Face Supérieure)** : **`Ø 120,000 mm H7 (+0,000 / +0,035)`**, profondeur **`3,00 mm (+/- 0,05 mm)`** (de `Z = 1020,41 mm` à `Z = 1017,41 mm`) — centre et retient la bague extérieure fixe du CRBH 8016 UU. Épaisseur résiduelle sous le siège = 7,02 mm.
- **4× Vis de Fixation d'Angles ➔ Pont de Hanches (et Pelvis Historique)** :
  - **Architecture Active `Torse-123 v42` (Pont de Hanches)** : **4 vis à tête fraisée FHC M5 × 18 mm Inox 18-8** (McMaster **`92125A213`**), taraudées directement dans les 4 `Inserts Hanche Haut [ASV1_200_13]` emmanchés dans les montants `20×20×2` (`L = 65,77 mm`). *(Montage historique sur coque PA12-CF seule : 4 vis `FHC M5 × 25 mm [92125A230]` avec rondelles DIN 125A M5 `93475A240` et écrous hex `90631A113` en poches de 8,50 mm à 1,8–2,0 N.m)*.
  - **Coordonnées CAO réelles** : `X = ±56,08 mm`, `Y = ±55,17 mm`, rayon mesuré **`R = 78,67 mm`** sur les diagonales à 45° (PCD `~157,3 mm`).
  - **Fraisures coniques 90° (face supérieure)** : Diamètre supérieur **`Ø 10,40 mm`**, profondeur **`3,10 mm`**. Garantit un **noyage à fleur rigoureux à 0,0 mm** (zéro frottement avec le balayage de la Waist Plate mobile).
  - **Épaisseur saine résiduelle sous tête** : `10,02 - 3,10 =` **`6,92 mm`** de métal plein en Alu 7075-T6 (résistance au cisaillement > 30 kN).
  - **Pont de matière plein face aux brides** : Arête extérieure de fraisure à `R = 78,67 - 5,20 =` **`73,47 mm`**, laissant un pont plein de **`1,47 mm`** d'Alu 7075-T6 continu face au talon arrière de chaque bride en L (`R = 72,00 mm`).
  - **Suppression des 4 trous latéraux** : Élimine définitivement le risque de fragilisation mécanique à proximité du siège Ø 120 mm.
- **4× Taraudages M4 pour Brides Étagées en L** : 4 perçages borgnes taraudés M4 × 0,7 mm (avant-trou foret carbure Ø 3,30 mm, profondeur taraudée utile 8,0 mm, prof. perçage 10,0 mm) sur PCD **`Ø 136,0 mm`** (`R = 68,0 mm`, soit `X = ±48,08 mm`, `Y = ±48,08 mm`), orientés à **45°, 135°, 225° et 315°** vers les 4 coins massifs. Serrage par vis CHC M4 × 16 mm (`92290A154`, couple 2,8-3,0 N.m + Loctite 243).
- **Lumière Concentrique d'Arc Arrière (`69,05°`, `R = 64,75..84,75 mm`, larg. `20,0 mm`)** : Usinée en zone postérieure (`-X`) autour de l'axe rotor RS-06 (`X = +49,23 mm, Y = +9,36 mm`) avec congés R = 1,5 mm *(remplace définitivement l'ancienne lumière oblongue frontale de 30 × 16 mm)*.
- **Butées Mécaniques Matérielles (+/- 95,0° à R = 80,50 mm)** : **[Modification CAO prévue avant usinage CNC — Non encore modélisée dans `Torse-123 v42`]** Doigt mobile implanté à `0°` côté `+X` pleine matière sous l'aile externe de `Waist_Plate_7075` (`X = +129,73 mm, Y = +9,36 mm`) venant frapper 2 plots fixes amortis TPU 95A posés sur `Traverse_Renfort_Bassin` à **`+/- 109,86°`** (`X = +21,89 mm, Y = +85,07 mm` et `Y = -66,35 mm`, contact exact à `+/- 95,0°`, voir §5.4).
- **Concentricité Ø 74,56 / Ø 82 / Ø 96 / Ø 120** : **`< 0,02 mm`**.
- **Planéité Face Inférieure & Bossage** : **`< 0,03 mm`** (appui plan franc sur carter stator et montants Pont de Hanches).
- **Centre de Gravité CoM (`v42`)** : `X = +55,43 mm`, `Y = +9,36 mm`, `Z = 1014,56 mm`.

> [!IMPORTANT]
> **Gamme d'usinage sur NestWorks C500** : Pièce 2.5D usinable en 2 phases sur la NestWorks C500 (~45 min).
> - Phase 1 (face sup) : surfaçage + siège Ø 120 H7 × 3 mm + 4 perçages Ø 5,1 mm coins + 4 fraisures 90° Ø 10,4 mm (prof. 3,1 mm) + 4 taraudages M4 PCD Ø 136 + chanfreins.
> - Phase 2 (retournement) : surfaçage face inf à 10,02 mm + alésage dégagement Ø 102 mm prof. 7 mm + chanfrein alésage + ébavurage.
>
> **PROTOCOLE ATELIER C500 — ALÉSAGE SIÈGE ROULEMENT Ø 120 H7 (MATCH MACHINING)** :
> Pour éviter tout risque de sur-alésage et s'affranchir de l'achat d'un micromètre 100-125 mm, l'usinage du siège Ø 120 H7 s'effectue par appariement direct avec le roulement physique sur la C500 :
> 1. **Réception & Dégraissage du Roulement** : Nettoyer la bague extérieure du CRBH 8016 UU et la poser propre sur la table de la machine.
> 2. **Contrôle relatif au Touch Probe 3D** : Lancer le cycle automatique de palpage extérieur 4 points (Boss Probing X+, X-, Y+, Y-) pour relever le diamètre extérieur effectif `D_roulement`.
> 3. **Ébauche avec Surépaisseur de Sécurité** : Programmer l'interpolation circulaire sous Fusion 360 avec une surépaisseur radiale de finition (*Stock to Leave*) de `+0,10 mm` (alésage usiné à ~`Ø 119,80 mm`). Utiliser une fraise carbure DLC 3 dents Ø 6 mm ou Ø 8 mm (10 000 tr/min, avance 800 mm/min, lubrification brumisation/air comprimé).
> 4. **Passes de Finition d'Approche (Sans Démonter la Pièce)** :
>    - Présenter le roulement à la main au-dessus du logement : il ne rentre pas.
>    - Palper l'alésage usiné au Touch Probe 3D (cycle Bore Probing) pour mesurer le diamètre réel obtenu.
>    - Ajuster la compensation de rayon d'outil (*Tool Wear Offset*) pour retirer `0,05 mm`, relancer la passe de finition.
>    - Répéter par micro-passes de `0,01 à 0,02 mm` en présentant le roulement physique entre chaque passe.
> 5. **Validation d'Ajustement Glissant Juste (H7/h6)** : Le cycle s'arrête dès que le roulement s'insère manuellement avec une résistance douce ("ajustement gras"), sans aucun jeu radial perceptible. La cote est alors rigoureusement parfaite à 0,0 mm sans instrument de métrologie externe.

### 4.3 Schéma de Transmission & Découplage des Charges

Le principe fondamental de la conception mécanique du D-Bot est le **découplage absolu entre la génération de couple et la reprise des charges structurales** :

1. **Le Roulement CRBH 8016 (Ø 80×120×16 mm)** encaisse l'intégralité des efforts perturbateurs : les `~17,3 kg` de compression axiale, les `180 N` de cisaillement et les `56 à 220 N.m` de moment de basculement. Sa capacité en moment (520 N.m) offre un facteur de sécurité de x2,36 dans le pire cas.
2. **Le Moteur RobStride RS-06** n'encaisse strictement aucun effort de basculement. Son arbre de sortie (rotor) ne transmet que le couple de rotation pur en lacet (**36 N.m max**), garantissant une durée de vie maximale et l'absence d'usure anormale des réducteurs.

### 4.4 Schéma Vectoriel d'Ingénierie & Détails d'Exécution CRBH 8016

Le schéma vectoriel ci-dessous regroupe les détails d'exécution géométrique issus de l'expertise mécanique pour un montage sans frottement et sans perte de course :

![Schéma d'Expertise et Points de Vigilance Waist Yaw](./media/schema_vigilances_mecaniques_waist_crbh8016.svg)

*Schéma technique d'ingénierie vectoriel officiel (D-Bot V1.2).*
- **Panneau 1 (Coupe Axiale Z)** : Détaillant la retenue axiale Z de la bague extérieure et le redan sous la Waist Plate créant un entrefer de sécurité face aux éléments en rotation (voir section 4.5 pour la résolution détaillée de la saillie de 13 mm et des 4 brides étagées en L).
- **Panneau 2 (Cinématique de Butée)** : Démontrant que 2 goupilles espacées de 15 mm consomment 19.2° d'angle mort sur une rainure de 190°, et validant la solution optimale à goupille unique DIN 6325 Ø 8 mm (course nominale +/- 95° préservée, tenue > 45 kN).
- **Panneau 3 (Traversée Électrique & Gamme C500)** : Implantation du corridor latéral déporté (25 × 15 mm) avec boucle de service (L = 150 mm) et checklist de validation avant usinage.

### 4.5 Système de Bridage Axial Z du Roulement RB8016

L'inspection géométrique approfondie sous Fusion 360 (`Torse v95`) a mis en évidence une contrainte dimensionnelle critique concernant la bague extérieure du roulement :
- **Épaisseur de la Traverse Verte (`Traverse_Renfort_Bassin`)** : `10,02 mm`.
- **Profondeur du lamage de réception** : `3,00 mm` (face supérieure de `Z = 1018,91 mm` à `Z = 1021,91 mm`).
- **Hauteur axiale du roulement RB8016** : `16,00 mm`.
- **Saillie libre du roulement au-dessus de la traverse** : `16,00 - 3,00 =` **`13,00 mm`**. La bague extérieure du roulement dépasse donc de 13,00 mm dans le vide au-dessus de la traverse.

![Architecture de Bridage Axial Z du Roulement RB8016](./media/schema_principe_brides_retenue_rb8016_waist.svg)

*Schéma vectoriel d'ingénierie officiel (D-Bot V1.x) : Résolution de la saillie de 13 mm du RB8016.*
- **Panneau 1 (Coupe Axiale Z)** : Comparaison entre le Cas A (redan initial de 1,50 mm, inexploitable car l'espace d'air ne permet pas d'insérer une bride rigide sans collision en rotation) et le Cas B (redan optimisé à **`3,00 mm`** sous la Waist Plate, libérant un entrefer total de 3,0 mm pour loger un bec de bride rigide de **`2,00 mm`** tout en préservant un entrefer de sécurité de **`1,00 mm`** franc).
- **Panneau 2 (Vue de Dessus)** : Implantation des 4 brides étagées en "L" orientées à 45° dans les 4 coins dégagés de la Traverse, hors de l'encombrement étroit (94 mm) de la Waist Plate.
- **Panneau 3 (Plan de Fabrication de la Bride en L)** : Cotation fonctionnelle 3D complète (dimensions hors-tout 16,00 × 15,00 × 15,00 mm, embase 12,00 mm, bec 4,00 × 2,00 mm, mur 3,50 mm, trou lisse Ø 4,50 mm centré à X = +8,00 mm, hauteur d'épaulement 13,00 mm, vis CHC M4 × 16 mm `[92290A154]` sur PCD Ø 136,0 mm à 45°, masse réelle CAO `Torse-123 v42` = `4,12 g`/bride, soit `16,48 g` les 4 en Alu 7075 ; enveloppe X-Y orientée à 45° = `21,95 × 21,95 × 15,02 mm` sur `Z = [1020,39 ; 1035,41 mm]`).

#### 4.5.1 Pourquoi Augmenter le Redan de la Waist Plate de 1,5 mm à 3,0 mm ?

1. **Cas A (Redan initial de 1,50 mm) — Inexploitable & Dangereux** :
   - L'espace d'air entre le sommet de la bague extérieure fixe du roulement et la face inférieure de la Waist Plate en rotation n'est que de `1,50 mm` (comme mesuré directement à l'outil inspect de Fusion 360).
   - Une bride métallique de retenue axiale doit présenter une rigidité suffisante pour encaisser les chocs dynamiques verticaux (+Z) lors de la marche bipède. Son bec de pincement doit mesurer au minimum `2,00 mm` d'épaisseur.
   - Avec seulement 1,50 mm d'espace, une bride de 2 mm crée une **interférence frontale de 0,5 mm** (collision franche). Même une bride amincie à 1,5 mm frotterait métal contre métal (0 mm de garde), bloquant la rotation ou créant une usure abrasive catastrophique.
2. **Cas B (Redan augmenté à 3,00 mm) — Solution Optimale & Validée** :
   - En augmentant la hauteur du redan circulaire d'appui sous la Waist Plate de **`1,50 mm à 3,00 mm`** (plage comprise entre Ø 80,0 mm et Ø 92,0 mm), la face inférieure de la plaque s'élève à `Z = +3,00 mm` au-dessus de la bague extérieure.
   - La bride étagée en "L" dispose ainsi de l'espace idéal : son bec de **`2,00 mm`** vient plaquer fermement la bague extérieure acier, tandis qu'il subsiste un **entrefer d'air franc de `1,00 mm`** (`3,00 - 2,00 = 1,00 mm`) entre le dessus de la bride et le dessous de la Waist Plate en rotation.
   - **Zéro frottement parasite garanti** sur l'intégralité de la course angulaire (+/- 90°).
   - **Impact cinématique nul** : L'élévation de `+1,5 mm` du torse complet sur l'axe Z est strictement négligeable à l'échelle d'un humanoïde de ~1,58 m et améliore même les dégagements autour des carters des moteurs de hanches RS-04.

#### 4.5.2 Implantation des 4 Brides Étagées en L aux 4 Coins (45°)

Les 4 brides sont positionnées aux 4 coins diagonaux de la traverse pelvienne :
- **Orientation** : Inclinées à `45,0°` par rapport aux axes sagittal X et médio-latéral Y (sur le PCD nominal Ø 136,00 mm, rayon R = 68,00 mm).
- **Dégagement géométrique parfait** : Sur la nouvelle interface élargie `Torse v102` (`175 × 175 mm`), la Waist Plate (176,11 × 173,05 mm) survole les 4 brides étagées grâce au redan surélevé de **`+3,00 mm`**, préservant l'entrefer d'air franc de **`1,00 mm`** sans aucun contact métallique lors des rotations de +/- 90°.
- **Fixation & Remplacement aisé** : Chaque bride est fixée par **1 vis CHC M4 × 16 mm Inox 316 (McMaster `92290A154`)** vissée dans un trou borgne taraudé M4 (profondeur taraudée 8 à 10 mm, avant-trou Ø 3,30 mm) percé dans la Traverse sur PCD **`Ø 136,00 mm`** (`R = 68,00 mm` à 45°). Ce montage indépendant permet de déposer ou remplacer le roulement en retirant simplement les 4 vis M4 sans toucher au berceau pelvien ni au moteur RS-06.

#### 4.5.3 Fiche Technique Dimensionnelle Complète de la Bride en L (Fusion 360)

Pour assurer une modélisation CAO exacte et sans ambiguïté du composant `Bride_Retenue_RB8016_L`, voici la cotation fonctionnelle tridimensionnelle complète :

```
             ◄── 4,0 mm ──►◄── 3,5 mm ──►◄──────── 8,5 mm ────────►
             (Avancée bec)   (Mur vert.)         (Semelle)
                            ▲           ▲
              ┌─────────────┴───────────┐ ─── Z = 15,0 mm (Sommet)
              │  BEC SUPÉRIEUR (2 mm)   │
  ────────────┴─────────────┐           │ ─── Z = 13,0 mm (Face appui roulement)
  Bague ext. RB8016         │    MUR    │
  (Acier Ø 120 mm)          │  VERTICAL │
                            │  (13 mm)  │
                            │           │ ─── Z = 5,0 mm (Haut semelle)
                            │           └───────────┬─────────────┐
                            │      Trou Ø 4,5 mm    │  VIS M4     │
  ──────────────────────────┴───────────────────────┼─────────────┘ ─── Z = 0,0 mm (Assise Traverse)
  Traverse Pelvis                                   │
                                                    ▼
  X = -4,0 mm               X = 0,0 mm              X = +8,0 mm   X = +12,0 mm
  (Bout du bec)             (Appui roulement)       (Axe vis)     (Talon arrière)
```

##### 1. Dimensions Synthétiques par Axe
| Axe Géométrique | Paramètre | Cote Nominale | Description Fonctionnelle |
| :--- | :--- | :---: | :--- |
| **Axe X (Profondeur radiale)** | **Longueur Hors-Tout** | **`16,00 mm`** | `4,0 mm` (bec) + `12,0 mm` (embase de fixation) |
| | **Avancée du Bec** | **`4,00 mm`** | Surplomb de maintien sur la face supérieure de la bague extérieure acier (Ø 120 mm) |
| | **Épaisseur Mur Vertical** | **`3,50 mm`** | Rigidité maximale sous l'effort de serrage axial Z |
| | **Position Axe Trou Vis** | **`X = +8,00 mm`** | Centré à 4,5 mm du mur vertical (passage rondelle Ø 9 mm) et 4,0 mm du talon arrière |
| **Axe Y (Largeur transverse)** | **Largeur d'Extrusion** | **`15,00 mm`** | Assise stable sous rondelle DIN 125A M4 (Ø 9,0 mm) avec 3,0 mm de matière latérale |
| **Axe Z (Hauteur verticale)** | **Hauteur Hors-Tout** | **`15,00 mm`** | Épaulement vertical (13,0 mm) + Bec de pincement (2,0 mm) |
| | **Hauteur sous Bec** | **`13,00 mm`** | Épouse rigoureusement la saillie du roulement RB8016 au-dessus de la traverse |
| | **Épaisseur Semelle** | **`5,00 mm`** | Semelle d'appui rigide sous la tête de vis CHC M4 |

##### 2. Coordonnées des Sommets pour l'Esquisse 2D (Fusion 360)
Origine `(X = 0,0 mm, Z = 0,0 mm)` placée au coin inférieur d'appui contre le cylindre extérieur du roulement :
- **P1** : `(0,00, 0,00) mm` — Origine : coin inférieur d'assise face au roulement
- **P2** : `(0,00, 13,00) mm` — Face d'appui vertical contre la bague extérieure du RB8016
- **P3** : `(-4,00, 13,00) mm` — Dessous du bec (contact plan supérieur bague extérieure acier)
- **P4** : `(-4,00, 15,00) mm` — Bout supérieur extrême du bec
- **P5** : `(+3,50, 15,00) mm` — Sommet arrière du mur vertical
- **P6** : `(+3,50, 5,00) mm` — Raccordement supérieur de la semelle d'embase
- **P7** : `(+12,00, 5,00) mm` — Talon arrière supérieur
- **P8** : `(+12,00, 0,00) mm` — Talon arrière inférieur (assise sur la traverse)

##### 3. Quincaillerie & Implantation Traverse Associée
- **Trou de passage dans la bride** : Trou lisse traversant **`Ø 4,50 mm`** (ISO 273 Moyen) à `X = +8,00 mm` et `Y = 7,50 mm` (milieu de l'embase).
- **Taraudage dans la Traverse** : Trou borgne taraudé **M4 × 0,7 mm** (avant-trou foret carbure Ø 3,30 mm, profondeur taraudée utile 8,0 mm, prof. perçage 10,0 mm) positionné à `45,0°` sur un cercle primitif **PCD = `Ø 136,00 mm`** (`R = 68,00 mm`, coordonnées relatives `X = ±48,08 mm`, `Y = ±48,08 mm`).
- **Vis CHC M4 × 16 mm** Inox 316 (McMaster **`92290A154`** / Inox 18-8 **`91292A115`**) + **Rondelle DIN 125A M4** Inox 316 (McMaster **`93475A230`**).
- **Couple de serrage recommandé** : **`2,8 à 3,0 N.m`** avec frein-filet Loctite 243.

##### 4. Dégagement Géométrique & Indépendance face aux Vis d'Angles Pelvis (Option A Validée)
- **Talon arrière de chaque bride** : Situé au rayon `R = 60,00 mm` (rayon extérieur roulement) + `12,00 mm` (longueur d'embase) = **`72,00 mm`**.
- **Axe de la vis d'angle Pelvis** : Centre du trou situé au rayon **`R = 78,67 mm`** sur les diagonales à 45° (`X = ±56,08 mm`, `Y = ±55,17 mm`).
- **Fraisure conique 90° (Ø 10,40 mm)** : Rayon interne de la fraisure = `78,67 - (10,40 / 2) =` **`73,47 mm`**.
- **Pont de matière saine en Alu 7075-T6** : `73,47 - 72,00 =` **`1,47 mm`** de métal plein continu entre l'arête conique de la fraisure et la face arrière de la bride.
- **Indépendance fonctionnelle absolue** : Le bridage axial de la bague extérieure du roulement (4 vis CHC M4 × 16 mm sur PCD Ø 136 mm serrées à 3,0 N.m dans les taraudages de la traverse) et l'ancrage structural du berceau pelvien (4 vis FHC M5 × 25 mm traversantes serrées à 2,0 N.m dans les poches PA12-CF) disposent de leurs propres lignes de charge indépendantes. Aucun risque d'interférence, d'empilement d'efforts parasites ou d'écrasement mutuel.

---

## 5. Interfaces Mécaniques & Chaîne Cinématique Pelvienne

### 5.1 Interface Supérieure : Waist Plate 7075 (176,11 × 173,05 mm) & Équerres Basses L = 90,0 mm

La connexion avec le haut du corps s'effectue via la **Waist Plate** (plaque inférieure maîtresse du torse) :
- **Matériau** : Aluminium **7075-T651**, épaisseur hors-tout **`9,02 mm`** (`Z = [1033,41 ; 1042,43 mm]`, épaisseur plaque 6,02 mm + redan inférieur de 3,00 mm, masse réelle certifiée CAO **`Torse-123 v42` = `433,53 g`**, volume `154,28 cm3`).
- **Dimensions de contour** : Format élargi quasi-carré **`176,11 × 173,05 mm`** (épousant l'évasement bas du `Plastron_Ventral_Torse` à 175 mm et la Traverse pelvienne).
- **Liaison avec la Colonne Sagittale** : Réalisée par les **2 Équerres Basses de Waist** (`Equerre waist`, `L = 90,02 mm`, cornière `30,02 × 30,02 mm`, modélisées en **Alu 7075** en CAO `Torse-123 v42`, masse réelle **`42,11 g`/u** soit **`84,22 g` la paire**) :
  - Flanc vertical pincé sur la colonne par **4 vis CHC M4 × 20 mm traversantes `[92290A168]` + 8 rondelles DIN 125A `[93475A230]` + 4 écrous Nylstop M4 `[93625A150]`** (entraxes réguliers de 18 mm, entraxe total 54 mm).
  - Aile horizontale fixée et bridée directement par les **4 vis traversantes CHC M4 × 20 mm `[92290A168]` du sandwich moyeu** (2 vis par équerre à `X = ±24,04 mm`, `Y = ±24,04 mm`) traversant l'équerre (`3,0 mm`) et la Waist Plate (`6,0 mm`) pour s'ancrer directement dans le Moyeu 7075-T6 (`10` vis `92290A168` au total dans la BOM `v42`). Les 4 anciens perçages intermédiaires superflus sont supprimés (encastrement direct monolithique).
  - Couple de serrage normalisé : **`2,8 à 3,0 N.m`** (facteur de sécurité au basculement `Sf = 1,68` face au choc de 275 N.m, et sécurité au glissement lacet `Sf = 3,63` face aux 36 N.m du moteur).
- **Redan d'Appui Bague Intérieure (Face Inférieure)** :
  - Usinage d'une portée circulaire en saillie de **`+3,0 mm`** sur la plage de diamètre comprise entre **`Ø 80,0 mm et Ø 92,0 mm`** (zone de contact exclusive avec la bague intérieure mobile du CRBH 8016).
  - La surface au-delà de Ø 95,0 mm reste usinée en retrait de 3,0 mm, garantissant un **entrefer d'air franc de 1,0 mm** au-dessus des 4 brides étagées en L (bec de 2,0 mm) et de **3,0 mm face à la bague extérieure fixe**. Zéro frottement parasite garanti.
- **Lumières Concentriques d'Arc de Câblage & Zéro Cisaillement (Traverse 69,0° vs Waist Plate 125,0°)** :
  - **Zone d'Implantation** : Zone postérieure (-X), centrée sur l'axe du rotor RS-06 et du roulement RB8016 (`X = +49,23 mm`, `Y = +9,36 mm`, zéro décentrage). Rayon intérieur `R_int = 64,75 mm`, rayon extérieur `R_ext = 84,75 mm`, largeur radiale de passage nette de **`20,0 mm`** (rayon médian `R = 74,75 mm`).
  - **Sur la Traverse Pelvis (Fixe)** : Fente en arc de cercle de **`69,0°`** (congés d'extrémités demi-circulaires Ø 16,0 mm). Ponts de matière sains en Alu 7075-T6 : `4,75 mm` face à la bague extérieure du roulement RB8016, `3,31 mm` face au bord extérieur arrière.
  - **Sur la Waist Plate Torse (Mobile)** : Fente en arc de cercle élargie à **`125,0°`** (congés d'extrémités Ø 16,0 mm). Ponts de matière sains : `14,9 mm` sur les flancs latéraux gauche et droit, dégagement franc `> 14 mm` en X face aux cornières de colonne vertébrale.
  - **Usinage des Congés R = 1,5 mm (Faces Supérieure et Inférieure)** : Congé continu de **`R = 1,5 mm`** (fraise quart de cercle CNC C500) sur l'intégralité du pourtour d'entrée et de sortie des deux plaques. Ce pavillon adoucit la pression de Hertz et élimine tout risque d'abrasion ou de coupure sous vibrations et torsion cyclique.
  - **Cinématique de Recouvrement & Course +/- 80°** :
    - À 0° (position neutre) : fenêtre de passage commune de **`97,0°`** (`126,6 mm` d'arc libre).
    - À +/- 80° (braquage maximal) : fenêtre utile résiduelle de **`17,05°`** (`22,24 mm` d'arc libre).
    - Pour un faisceau de câbles conditionné de **Ø 15,0 mm** (lignes 48V AWG 12 + bus CAN-FD sous gaine tressée extensible PET), la marge de jeu libre est de **`+7,24 mm`** : **zéro effet guillotine**, le faisceau glisse librement dans la fente rotor et absorbe la rotation par torsion hélicoïdale continue (`0,50° / mm` sur L = 160 mm).
- **Butée Mécanique de Lacet (+/- 95,0° à R = 80,50 mm)** :
  - Pour éviter la lumière banane dorsale (`-X`, `R = 64,75..84,75 mm`), le doigt mobile est implanté côté avant **`+X` (`0°`, pleine matière)** et bloque sur les 2 plots fixes amortis TPU 95A placés à `+/- 109,86°` (`contact à +/- 95,0°`, `>= 13°` après la butée logicielle `+/- 80..82°`).

![Schéma Explicatif : Cinématique des Lumières Concentriques d'Arc](./media/schema_explicatif_corridor_vs_encoche_u.svg)

*Schéma vectoriel pédagogique d'ingénierie : Architecture cinématique du harnais à fentes concentriques en arc de cercle. Panneau 1 : Pièce fixe du bas (Traverse bassin avec fente de 69,0°). Panneau 2 : Pièce mobile du haut (Waist Plate torse avec fente élargie à 125,0°). Panneau 3 : Démonstration dynamique du recouvrement utile (126,6 mm à 0° et 22,2 mm à +/- 80° pour un faisceau Ø 15 mm, marge saine +7,2 mm, torsion hélicoïdale 0,50°/mm, congés R = 1,5 mm, zéro cisaillement métal-métal).*

#### 5.1.1 Cartographie Complète des Perçages, Vis CHC M4 & Pincement Sandwich

Le verrouillage axial et la transmission du couple de rotation de taille (Waist Yaw) reposent sur un **assemblage en étau (sandwich)** ultra-rigide prenant en compression directe la bague intérieure du roulement **RB8016** (ou **CRBH8016**) entre :
1. **L'étage supérieur** : Les ailes horizontales des **2 Équerres Basses** (épaisseur 3,00 mm en Alu 6060-T6) reposant sur la **Waist Plate** (épaisseur 6,00 mm en Alu 6061-T6 ou 7075-T6), dont la face inférieure usine un redan d'appui circulaire de `+3,00 mm` (plage comprise entre Ø 80,0 mm et Ø 92,0 mm).
2. **Le roulement intermédiaire** : La bague intérieure mobile du RB8016 (alésage intérieur Ø 80,00 mm, portée extérieure Ø 95,00 mm, épaisseur axiale 16,00 mm).
3. **La pièce inférieure d'accouplement** : Le **Moyeu d'Accouplement Sandwich** (`Moyeu_Waist_Sandwich_7075` en Alu 7075-T651, masse réelle `v42` = **`163,94 g`**, volume `58,34 cm3`, encombrement `91,52 × 91,52 × 23,62 mm` sur `Z = [1009,41 ; 1033,03 mm]`) :
   - Son fût cylindrique rectifié (Ø 80,00 mm tolérance h6, soit +0,000 / -0,019 mm) guide l'alésage du roulement sur **`15,60 mm`** de hauteur axiale (préservant 97,5 % de la portée de guidage).
   - **Règle d'or de précharge anti-talonnage (Jeu axial obligatoire)** : Le sommet du fût (`Z = 1033,03 mm`) est volontairement usiné en **retrait axial nominal de `0,40 mm`** (`0,38 mm` mesurés en CAO `v42` face à `Z = 1033,41 mm`) sous la face supérieure de la bague intérieure du roulement. Ce jeu d'entrefer franc interdit tout contact direct aluminium/aluminium entre le sommet du moyeu et la Waist Plate lors du serrage, garantissant que 100 % de la force de précharge axiale des 4 vis CHC M4 (19,2 kN) compresse exclusivement la bague intérieure en acier du roulement sans aucun court-circuit d'effort.
   - Sa collerette annulaire inférieure (Ø 91,52 mm × épaisseur 3,00 mm) vient en appui franc sous la face inférieure de la bague intérieure du roulement.
   - 4 trous borgnes taraudés M4 (profondeur 12,0 mm, filet utile 10,0 mm) sont usinés dans la face supérieure du fût sur le diamètre primitif **PCD Ø 68,00 mm** (rayon R = 34,00 mm) orientés à 45,0° des axes principaux.
   - Son embase inférieure (Ø 65,0 mm × hauteur 5,00 mm) descend sous le roulement et se boulonne directement sur le rotor RobStride RS-06 (vis repère `91292A113` CHC M3×10 modélisée en `v42`, `4–6` vis selon couronne rotor).
   - **Hauteur totale monobloc du moyeu** : `23,62 mm` mesurés en CAO `v42` (`3,00 mm` collerette + `15,60 mm` fût + `5,00 mm` embase).

Le serrage axial est assuré par **4 vis à tête cylindrique à six pans creux CHC M4 × 20 mm (ISO 4762 / DIN 912, classe 10.9 ou 12.9 acier noir)** insérées depuis le dessus des ailes horizontales des 2 équerres basses (2 vis par équerre, avec rondelles plates DIN 125A sous tête) et traversant l'équerre (`3,0 mm`) puis la Waist Plate (`6,0 mm`) pour venir se visser directement dans le Moyeu 7075-T6.

---

##### A. Tableau Cartographique Millimétrique des 4 Perçages CHC M4

Les 4 vis sont disposées aux 4 sommets d'un carré d'entraxe linéaire de `48,08 mm` inscrit dans le cercle primitif **PCD Ø 68,00 mm** (Rayon primitif `R = 34,00 mm`). L'orientation est inclinée à exactement **`45,0°`** par rapport à l'axe sagittal (`X`) et l'axe médio-latéral (`Y`), positionnant 2 vis sur l'équerre gauche et 2 vis sur l'équerre droite :

`X = R * cos(45,0°) = 34,00 * 0,707107 = +24,04 mm` (ou `-24,04 mm`)  
`Y = R * sin(45,0°) = 34,00 * 0,707107 = +24,04 mm` (ou `-24,04 mm`)

| Repère Trou | Cadran & Position | Coordonnée X (Sagittale) | Coordonnée Y (Latérale) | Cote Z d'Entrée | Perçage Lisse Traversant (Équerre + Waist Plate) | Logement de Tête (Face Supérieure) | Taraudage Borgne (Moyeu 7075) | Visserie Normalisée Associée |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- |
| **CHC #1** | **Avant-Gauche (Av-G)** | **`+24,04 mm`** | **`-24,04 mm`** | `Z = +3,00 mm` (Dessus Équerre G) | Foret carbure **`Ø 4,50 mm`** traversant Équerre (3 mm) + Waist (6 mm) | Tête CHC en surface sur aile équerre (+ rondelle DIN 125A M4) | Borgne Ø 3,3 mm prof. 12 mm / Taraudé M4x0.7 prof. 10 mm | Vis CHC M4 × 20 mm cl. 10.9/12.9 / Loctite 243 |
| **CHC #2** | **Avant-Droit (Av-D)** | **`+24,04 mm`** | **`+24,04 mm`** | `Z = +3,00 mm` (Dessus Équerre D) | Foret carbure **`Ø 4,50 mm`** traversant Équerre (3 mm) + Waist (6 mm) | Tête CHC en surface sur aile équerre (+ rondelle DIN 125A M4) | Borgne Ø 3,3 mm prof. 12 mm / Taraudé M4x0.7 prof. 10 mm | Vis CHC M4 × 20 mm cl. 10.9/12.9 / Loctite 243 |
| **CHC #3** | **Arrière-Droit (Ar-D)** | **`-24,04 mm`** | **`+24,04 mm`** | `Z = +3,00 mm` (Dessus Équerre D) | Foret carbure **`Ø 4,50 mm`** traversant Équerre (3 mm) + Waist (6 mm) | Tête CHC en surface sur aile équerre (+ rondelle DIN 125A M4) | Borgne Ø 3,3 mm prof. 12 mm / Taraudé M4x0.7 prof. 10 mm | Vis CHC M4 × 20 mm cl. 10.9/12.9 / Loctite 243 |
| **CHC #4** | **Arrière-Gauche (Ar-G)** | **`-24,04 mm`** | **`-24,04 mm`** | `Z = +3,00 mm` (Dessus Équerre G) | Foret carbure **`Ø 4,50 mm`** traversant Équerre (3 mm) + Waist (6 mm) | Tête CHC en surface sur aile équerre (+ rondelle DIN 125A M4) | Borgne Ø 3,3 mm prof. 12 mm / Taraudé M4x0.7 prof. 10 mm | Vis CHC M4 × 20 mm cl. 10.9/12.9 / Loctite 243 |

---

##### B. Caractéristiques Géométriques du Perçage Traversant & Sandwich Équerre + Waist Plate

Pour le montage traversant direct des 4 vis CHC M4 :

1. **Diamètre de Passage Lisse Traversant** :
   * **`Ø 4,50 mm`** (**Recommandé — Tolérance ISO 273 Série Moyenne**) : Percé identiquement dans l'aile de l'équerre (`3,0 mm`) et dans la Waist Plate (`6,0 mm`).
   * Laisse un jeu radial de `0,25 mm` autour du corps de vis M4, autorisant un assemblage glissant sans coincement ni contrainte parasite d'alignement.

2. **Montage Direct en Surface sur l'Équerre (Zéro Lamage, Zéro Fraisage)** :
   * La tête cylindrique DIN 912 (diamètre `d_k = 7,0 mm`, hauteur `k = 4,0 mm`) repose sur l'aile horizontale de l'équerre avec une rondelle plate standard **DIN 125A M4** (`Ø 9,0 mm × 0,8 mm`).
   * **Épaisseur totale bridée sous tête** : **`9,00 mm d'aluminium plein`** (`3,0 mm` cornière + `6,0 mm` Waist Plate).
   * **Avantage mécanique décisif** : Cette prise en étau continue crée un encastrement direct monobloc entre la cornière de colonne vertébrale et le moyeu tournant, supprimant tout fléchissement de plaque intermédiaire.
   * **Suppression des perçages superflus** : L'aile horizontale ne requiert aucun perçage supplémentaire. Les 4 anciens perçages intermédiaires de la plaque sont éliminés, simplifiant la fabrication CNC.

3. **Ébavurage & Finition Métal-Métal** :
   * Micro-chanfrein d'ébavurage de **`0,3 mm × 45°`** obligatoire sur les deux faces de l'équerre et de la Waist Plate pour garantir un contact plan rigoureusement franc à 0,0 mm.

---

##### C. Taraudage du Moyeu 7075-T6 & Longueur d'Implantation des Vis

Le corps du Moyeu étant en alliage haute résistance **Aluminium 7075-T651** (`Rm = 540 MPa`, `Rp0.2 = 470 MPa`) :
1. **Perçage de l'Avant-Trou Borgne** : Foret hélicoïdal carbure **`Ø 3,30 mm`**, profondeur de perçage **`12,00 mm`** depuis la face supérieure du fût.
2. **Chanfrein d'Entrée de Taraudage** : **`0,5 mm × 45°`** (débouchant à `Ø 4,50 mm`).
3. **Taraudage Machine M4×0,70** : Tolérance **ISO 2 (6H)**, profondeur de filet utile rectifié **`10,00 mm`**.
4. **Bilan d'Engagement de la Vis CHC M4 × 20 mm (Sandwich Équerre + Waist Plate)** :
   - Longueur totale sous tête de la vis CHC M4 : `L = 20,00 mm`.
   - Épaisseur de la rondelle DIN 125A sous tête : `0,80 mm`.
   - Épaisseur traversée totale (Équerre 3 mm + Waist Plate 6 mm) : `9,00 mm`.
   - Entrefer de précharge libre (retrait fût anti-talonnage) : `0,40 mm`.
   - **Longueur de pénétration filetée effective dans le moyeu** :  
     `L_eng = 20,00 mm - 0,80 mm - 9,00 mm - 0,40 mm =` **`9,80 mm`**
   - **Ratio d'implantation sur diamètre nominal** :  
     `Ratio = L_eng / d = 9,80 mm / 4,00 mm =` **`2,45 * d`** (très supérieur au minimum aéronautique de `1,5 * d`).
   - **Garde au fond de trou borgne** :  
     `Garde = 12,00 mm - 9,80 mm =` **`2,20 mm`** (zéro risque de talonnage).

---

##### D. Dimensionnement RDM & Tenue Mécanique du Serrage Sandwich (Zéro Glissement)

Le dimensionnement mécanique du serrage sandwich a été validé selon les critères normalisés VDI 2230 :

1. **Caractéristiques Mécaniques de la Visserie CHC M4 Classe 10.9 ou 12.9** :
   - Section résistante sous traction : `A_s = 8,78 mm^2`.
   - Limite d'élasticité : `Re = 940 MPa` (cl. 10.9) ou `1 080 MPa` (cl. 12.9).
   - Résistance à la rupture en traction : `Rm = 1 040 MPa` (cl. 10.9) ou `1 220 MPa` (cl. 12.9).
2. **Précharge Axiale de Montage (Couple C = 2,8 N.m)** :
   - Avec un coefficient de frottement moyen sous tête et dans les filets `mu = 0,14` (lubrification légère ou frein-filet Loctite 243 à l'état liquide) :  
     `F_0 ~ C / (0,16 * P + 0,58 * d_2 * mu + 0,5 * d_tête * mu)`  
     `F_0 ~ 4 800 N` (soit `~480 kgf` de précharge élastique par vis).
3. **Effort de Pincement Axial Total du Sandwich** :
   - Sur les 4 vis réparties symétriquement :  
     `F_pincement_total = 4 * 4 800 N = 19 200 N = 19,2 kN` (soit `~1,92 tonne` de pression continue).
   - Cette compression de 19,2 kN bride infailliblement la bague intérieure du roulement RB8016, éliminant tout jeu axial parasite et garantissant une rigidité angulaire maximale en lacet.
4. **Pression d'Assise Sous Tête de Vis CHC (Vérification Matage Alu)** :
   - Avec une rondelle standard DIN 125A M4 (Ø int 4,3 mm, Ø ext 9,0 mm) ou rondelle DIN 433 (Ø int 4,3 mm, Ø ext 8,0 mm) :  
     `Surface_portante ~ pi/4 * (8,0^2 - 4,5^2) = 34,4 mm^2`  
     `Pression_contact = 4 800 N / 34,4 mm^2 = 139,5 MPa`.  
   - La limite d'écrasement admissible de l'Aluminium 6061-T6 est `Rp0.2 = 276 MPa` (et `470 MPa` en 7075-T6). Facteur de sécurité au matage sous rondelle : `Sf = 276 / 139,5 = 1,98` en 6061-T6 (et `3,37` en 7075-T6). Zéro risque d'enfoncement plastique.
5. **Résistance Ultime à l'Arrachement en Traction Pure (Charges Dynamiques Torse)** :
   - Capacité limite de rupture en traction des 4 vis classe 10.9 :  
     `F_rupture = 4 * A_s * Rm = 4 * 8,78 mm^2 * 1 040 MPa = 36 524 N = 36,5 kN` (soit `~3,65 tonnes`).
   - En comparaison, la capacité dynamique axiale du roulement RB8016 est de `C_a = 22,0 kN`. Le sandwich de visserie est plus résistant que le roulement lui-même (`Sf = 36,5 / 22,0 = 1,66`).
   - Sous la charge de suspension dynamique maximale du haut du corps (masse torse + bras = 17,3 kg, soit sous une décélération extrême de 3G un effort de traction axiale de `F_traction = 17,3 kg * 9,81 m/s^2 * 3 = 509 N`) :  
     `Facteur_Securite_Traction = 36 524 N / 509 N = 71,7` (marge de sécurité extrême > 70).
6. **Résistance au Cisaillement des Filets dans l'Aluminium 7075-T6** :
   - Résistance admissible au cisaillement de l'Alu 7075-T6 : `tau_rupture ~ 330 MPa`.
   - Surface de cisaillement du taraudage sur `L_eng = 10,0 mm` :  
     `A_filet = pi * d_nom * 0,75 * L_eng = 3,1416 * 4,00 mm * 0,75 * 10,00 mm = 94,25 mm^2`.
   - Résistance à l'arrachement du taraudage par vis :  
     `F_arrachement_taraudage = 94,25 mm^2 * 330 MPa = 31 100 N = 31,1 kN` par vis !  
   - Les 4 taraudages offrent une résistance théorique cumulée de `124 kN` (12,4 tonnes). La vis en acier céderait en traction bien avant que les filets dans l'Alu 7075 ne s'arrachent.

---

##### E. Guide de Modélisation CAO Fusion 360 (Outil `Hole` / Touche `H`)

Pour implémenter ces 4 perçages CHC avec une précision paramétrique absolue sous **Autodesk Fusion 360** :

1. **Création de l'Esquisse 2D (Face Supérieure de la Waist Plate)** :
   - Sélectionner la face supérieure plane de la Waist Plate (`Waist_Plate_6mm`).
   - Cliquer sur **Créer une esquisse** (*Create Sketch*).
   - Tracer un cercle de construction (`Type: Construction`, touche `X`) centré sur l'Origine axiale (axe Z), de diamètre **`68,00 mm`**.
   - Tracer deux droites de construction diagonales passant par le centre à **`+45,0°`** et **`-45,0°`** de l'axe X.
   - Avec l'outil **Point** (`Create > Point`), poser 4 points d'esquisse à l'intersection du cercle Ø 68 mm et des deux droites diagonales.
   - Cliquer sur **Terminer l'esquisse** (*Finish Sketch*).
2. **Génération des 4 Trous via la Commande Perçage (`Hole`, Touche `H`)** :
   - Taper la touche **`H`** pour ouvrir la boîte de dialogue `Hole`.
   - **Placement** : Choisir `À partir de l'esquisse (plusieurs trous)` (*From sketch (multiple holes)*). Sélectionner les 4 points créés.
   - **Option 1 (Tête en Surface — Recommandé)** :
     - **Type de trou (`Hole Type`)** : **Simple (`Simple`)**.
     - **Type de perçage (`Hole Tap Type`)** : **Simple (`Simple`)**.
     - **Étendue (`Extent`)** : `À travers tout` (*Through All*) ou `Distance = 6,00 mm`.
     - **Diamètre du trou lisse** : **`4,50 mm`**.
   - **Option 2 (Tête Noyée / Lamée — DIN 7984 tête basse)** :
     - **Type de trou (`Hole Type`)** : **Lamé (`Counterbore`)**.
     - **Diamètre du lamage** : **`8,00 mm`** (ou `8,50 mm`).
     - **Profondeur du lamage** : **`3,20 mm`**.
     - **Diamètre de passage lisse** : **`4,50 mm`**.
   - Cliquer sur **OK**. Les 4 trous sont générés proprement.
3. **Modélisation des 4 Trous Borgnes Taraudés sur le Moyeu 7075-T6** :
   - Sélectionner la face supérieure du fût du composant `Moyeu_Waist_Sandwich_7075`.
   - Créer une esquisse, projeter les 4 points ou répliquer le cercle PCD Ø 68,0 mm à 45,0°.
   - Lancer la commande **Perçage (`Hole`, touche `H`)** :
     - **Type de trou (`Hole Type`)** : **Simple (`Simple Hole`)**.
     - **Type de perçage (`Hole Tap Type`)** : **Taraudé (`Tapped`)**.
     - **Profil de filetage (`Thread Type`)** : **ISO Métrique profil (`ISO Metric profile`)**.
     - **Taille (`Size`)** : **`4.0 mm`**.
     - **Désignation (`Designation`)** : **`M4x0.7`**.
     - **Classe de tolérance (`Class`)** : **`6H`**.
     - **Profondeur de perçage foret (`Hole Depth`)** : **`12,00 mm`**.
     - **Profondeur de filetage effectif (`Thread Depth`)** : **`10,00 mm`**.
     - **Pointe de foret (`Drill Point Angle`)** : **`118,0 deg`**.
   - Appliquer ensuite un **Chanfrein (`Chamfer`)** de **`0,50 mm × 45°`** sur l'arête d'entrée de chaque trou.

---

##### F. Consignes d'Atelier & Gamme d'Usinage CNC C500

Pour l'usinage sur la fraiseuse CNC NestWorks C500 :
1. **Perçage de la Waist Plate (Alu 6061-T6 ou 7075-T6)** :
   - Foret carbure monobloc **Ø 4,50 mm** non revêtu ou DLC (spécial aluminium).
   - Vitesse de coupe : `Vc = 120 m/min` (`N ~ 8 500 tr/min`), avance par dent `fz = 0,05 mm/dent`.
   - Cycle de perçage avec débourrage périodique (`G83`, pas de débourrage `Q = 2,0 mm`) et arrosage fluide continu pour éviter le collage de l'aluminium sur les goujures.
2. **Usinage du Lamage Optionnel (si retenu)** :
   - Fraise carbure 2 lèvres Ø 6 mm ou Ø 8 mm travaillant en interpolation hélicoïdale ou poche circulaire (`2D Pocket` Fusion 360). Vitesse `Vc = 150 m/min`, avance par dent `fz = 0,04 mm/dent`.
3. **Ébavurage & Contrôle Métrologique** :
   - Réaliser un micro-chanfrein `0,3 mm × 45°` sur chaque face.
   - Insérer une vis de référence CHC M4 × 16 mm avec sa rondelle dans chaque trou : la vis doit s'insérer librement sans contrainte géométrique (glissement doux sans jeu excessif).

---

#### 5.1.2 Prototypage des Livrables 2D & Fabrication Assistée par API (DXF, Blueprint SVG & Fiche Atelier)

Afin de dépasser le cadre des simples captures d'écran raster et de valider la chaîne numérique complète jusqu'à l'usinage en atelier, la **Platine Waist 7075 (`Waist_Plate_7075`)** a servi de banc d'essai étalon pour prototyper les 3 nouveaux livrables 2D automatisables par script Python :

##### 1. Livrable A : Export Vectoriel 1:1 DXF pour Fraiseuse CNC & Découpe Laser
- **Principe d'automatisation API** :
  - Le script Fusion 360 [`Export2DWaistPlate.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/fusion360/Export2DWaistPlate/Export2DWaistPlate.py) isole l'occurrence `Waist_Plate_7075:1`.
  - Il identifie automatiquement sa face plane maîtresse (normale axiale Z, surface maximale `~154 cm2`).
  - Il instancie une esquisse temporaire 2D (`comp.sketches.add(best_face)`), projette le contour extérieur avec congés R=10 mm et l'intégralité des perçages (`sketch.project(body)`), puis exporte le profil à l'échelle 1:1 stricte via `sketch.saveAsDXF()`.
  - L'esquisse temporaire est immédiatement purgée de la timeline pour ne laisser aucune pollution paramétrique dans l'historique du modèle 3D.
- **Fichier de fabrication généré** :
  - Emplacement souverain : `Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/Pieces_Isolees/Waist_Plate_7075/Waist_Plate_7075_Usinage_1to1.dxf`
  - Utilisation : Prêt pour FAO (Fusion CAM, CAMBam, FreeCAD Path) ou sous-traitance laser/eau (SendCutSend, John Steel).

##### 2. Livrable B : Plan Technique Vectoriel Blueprint Coté Haute Résolution (SVG Normalisé)
Le solveur géométrique B-Rep de Fusion 360 fournit instantanément les coordonnées réelles sans aucune approximation de mesure manuelle. Le schéma ci-dessous regroupe le plan de fabrication complet généré au standard D-Bot (Dark Blueprint `#0f172a`, alésage H7, coupe A-A cotée, cartouche ISO 7200 et quincaillerie McMaster-Carr associée — remplace les anciens plans 2D/fiches archivés) :

![Plan Technique Coté Waist Plate 7075](./media/blueprint_waist_plate_7075_cote.svg)

- **Cotes dimensionnelles certifiées B-Rep (`Torse-123 v42`)** :
  - Largeur hors-tout : `176,11 mm` (axe X).
  - Profondeur hors-tout : `173,05 mm` (axe Y).
  - Épaisseur nominale : `9,02 mm` (axe Z, dont plaque `6,02 mm` + redan `+3,00 mm`).
  - Alésage central traversant roulement RB8016 : `Ø 80,00 mm H7 (+0,030 / 0,000 mm)`.
  - Épaulement redan de centrage RB8016 : `Ø 89,62 mm`, profondeur `3,00 mm`.
  - Lumière concentrique arrière d'arc : `125,05°`, `R_int = 64,75 mm` (`Ø 129,50 mm`), `R_ext = 84,75 mm` (`Ø 169,50 mm`), largeur `20,0 mm`.
  - Perçages sandwich Moyeu 7075 + Équerres Waist : `4x Ø 4,50 mm` sur cercle primitif PCD `Ø 68,00 mm` à 45,0° (`48,08 × 48,08 mm`).
  - Perçages liaison basse `Plastron_Ventral_Torse` / `Corniere basse` : perçages `Ø 4,50 mm` pour vis `CHC M4×18 [92290A161]` et `CHC M4×14 [91290A150]` + `Nord-Lock M4 [91812A252]`.
  - Masse finie certifiée CAO (`Torse-123 v42`) : **`433,53 g`** (Aluminium 7075-T6, volume `154,28 cm3`).

*(Note : l'export PDF historique `v105` obsolète `Waist_Plate_7075_Plan_Certifie.pdf` a été purgé ; le blueprint vectoriel `v42` ci-dessus et le fichier DXF 1:1 font foi.)*

---

### 5.2 Le Bloc Pelvien Inférieur (Pelvis Asimov Scalé 1.2776 & Pont de Hanches `v42`)

Le bassin (`Bassin_Pelvis [ASV1_200]`) sert de berceau structurel pour la motricité inférieure et supporte la liaison de taille. L'architecture historique (caisson porteur plein PA12-CF scalé `1,2776`) a évolué en CAO active **`Torse-123 v42`** vers un **découplage complet Squelette Métallique / Habillage Cosmétique Non Porteur** :

- **Encombrement géométrique réel du Pelvis complet (`Bassin_Pelvis [ASV1_200]` en `v42`)** :
  - **Largeur Y** : `487,08 mm` (plage `Y: [-245,88 ; +241,19 mm]`).
  - **Profondeur sagittale X** : `233,96 mm` (plage `X: [-66,42 ; +167,54 mm]`).
  - **Hauteur axiale Z** : `315,61 mm` (plage `Z: [714,17 ; 1029,78 mm]`, ou jusqu'à `1035,41 mm` au sommet des `4x Bride_Retenue_RB8016_L` sur la `Traverse_Renfort_Bassin`).
  - **Coque centrale `Chassis_Structurel_Bassin_Last` (Calibrée PA12-CF 5 mm / 15 % Gyroïde)** : **`441,36 g`** (seule pièce PA12-CF déjà calibrée à **`rho = 0,700 g/cm3`** sur `630,52 cm3`, dimensions `207,75 × 313,03 × 225,34 mm`, `Z = [800,88 ; 1026,22 mm]` ; remplace l'ancien bloc massif de `2 805,69 g` / `6 185,68 g` hist.). Elle joue désormais un rôle purement cosmétique et de guidage interne de câbles.

> [!WARNING]
> **Statut des 8 Occurrences Externes de Hanches `ASV1_200` (En cours de définition côté CAO — Non définitives)** :
> Dans le modèle `Torse-123 v42`, les **8 occurrences de hanches héritées de `Bassin_Pelvis [ASV1_200]`** restent conservées à titre provisoire pour référence géométrique et gabarit d'encombrement (`487,06 mm` en Y), **en cours de définition côté CAO et non définitives** :
> - `Support_Hanche_Gauche [ASV1_200_06C]` (`371,19 g`, PA12-CF `1,015 g/cm3` brut) & `Support_Hanche_Droit [ASV1_200_08C]` (`371,16 g`) — *Non définitives (en cours de définition CAO)*
> - `Liaison_Hanche_Gauche [ASV1_200_07C]` (`93,98 g`, PA12-CF `1,015 g/cm3` brut) & `Liaison_Hanche_Droit [ASV1_200_09C]` (`93,18 g`) — *Non définitives (en cours de définition CAO)*
> - `Capot_Lateral_Hanche_Gauche [ASV1_200_04B]` (`135,53 g`, PA12-CF `1,015 g/cm3` brut) & `Capot_Lateral_Hanche_Droit [ASV1_200_05B]` (`135,53 g`) — *Non définitives (en cours de définition CAO)*
> - `Capot_Protection_Hanche_Frontal_G [ASV1_200_02A]` (`74,31 g`, PA12-CF `1,015 g/cm3` brut) & `Capot_Protection_Hanche_Frontal_D [ASV1_200_03A]` (`74,31 g`) — *Non définitives (en cours de définition CAO)*
>
> *(Note : ces 8 pièces totalisent `1 349,19 g` bruts en `v42` à `rho = 1,015 g/cm3`, contre `~930 g` une fois calibrées au gyroïde 15 %, et feront l'objet d'un carénage optimisé autour des `RS-04` du Pont de Hanches).*

> [!NOTE]
> **Architecture Finale Certifiée CAO (`Torse-123 v42`) — Squelette Métallique « Pont de Hanches »** :
> Le chemin de charge primaire entre la `Traverse_Renfort_Bassin` (`566,74 g`) et les `2x RS-04` Hip Pitch (`1 559,43 g`/u avec accouplement en CAO `v42`) est assuré à 100 % par le squelette tubulaire tout-métal **« Pont de Hanches »** (`1 114,87 g` porteurs dont `978,09 g` structure Alu + `136,78 g` visserie) :
> - `4x Montants de Hanche 20×20×2 mm [ASV1_200_11]` (`L = 65,77 mm`, `25,71 g`/u en Alu 6060-T6) + `8x Inserts Hanche Bas/Haut [ASV1_200_12/13]` (`15,82 × 15,82 × 15,02 mm`, `9,25 g`/u en Alu 7075), fixés aux coins de la Traverse par **`4x FHC M5 × 18 mm [92125A213]`** et traversés transversalement par **`8x CHC M4 × 25 [91292A122]`** + **`8x Rondelles M4 [93475A230]`** + **`8x Nylstop M4 [93625A150]`**.
> - `Selle de Pont Pelvis [ASV1_200_10]` en Alu 7075 (`140,04 × 145,04 × 22,03 mm`, **`338,98 g`**), solidarisée par **`4x CHC M5 × 35 [91290A661]`** + **`4x CHC M5 × 20 [92290A242]`** + `8x [93475A240]` + `4x Nylstop M5 [93625A200]`.
> - `Tube transverse Hanches [60x60]` en Alu 6060-T6 (`60,02 × 46,33 × 60,02 mm`, **`57,67 g`**) et **`2x Bride Epaule` v87** (`202,30 g`/u en Alu 7075) bridés par **`2x CHC M5 × 80 mm [91290A276]`** + **`4x Rondelles M5 [93475A240]`** + **`2x Nylstop M5 [93625A200]`**.
> - `RS-06 Waist` : logé au centre exact sous la Traverse (`Z = [958,90 ; 1009,44 mm]`) avec dégagement périphérique total entre les 4 montants `20×20`. Consulter [`STUDY_Squelette_Pelvien_Pont_de_Hanches.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Squelette_Pelvien_Pont_de_Hanches.md) et [`SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md).

### 5.3 Connexion avec les Hanches en Chaîne F-A-R (RS-04 Hip Pitch)

Le D-Bot V1.x utilise officiellement l'ordre cinématique **F-A-R (Flexion Pitch ➔ Abduction Roll ➔ Rotation Yaw)** pour les hanches :
- **Maillon 1 (Hip Pitch — Moteurs RS-04 sur `Bride Epaule v87`)** :
  - Deux moteurs **RobStride RS-04** (`120 N.m` pic, `1 420 g` nus / `1 559,4 g` ensemble CAO) sont montés de part et d'autre du **Pont de Hanches** via **2 `Bride Epaule` v87** (`202,30 g`/u en Alu 7075) solidaires du `Tube transverse Hanches [60x60]` (`L = 46,33 mm`, `57,67 g`).
  - Leurs axes sont colinéaires à l'axe médio-latéral transversal (`Y`).
  - Le stator du RS-04 est rigidement boulonné sur la `Bride Epaule v87` (`4x CHC M4×16 [90128A214]` en Zone 1 + `6x TB M4×25 [92855A422]` en Zone 2 + `10x Nord-Lock M4 [91812A252]` par côté ; cf. alerte atelier profondeur borgne 6,0 mm ci-dessous).
  - Le rotor du RS-04 porte le **L-Bracket Pitch-Roll** (usinage 7075-T6) qui descend vers le moteur RS-03 Roll (implanté dans l'enveloppe hanches de `487,06 mm` avec habillages externes `ASV1_200` actuellement *en cours de définition côté CAO*).
- **Avantage biomécanique décisif de cette implantation** :
  - Les deux plus lourds moteurs de jambe (`2 × 1,42 kg = 2,84 kg`) sont immobiles par rapport au bassin. Ils n'ajoutent aucune inertie lors du swing latéral de jambe, permettant une dynamique de marche ultra-réactive.

---

#### 5.3.1 Intégration Stator RS-04 : Fixation Arrière Monoface & Dissipation Thermique Pelvienne

![Intégration Stator RobStride RS-04 — Fixation Arrière & Dissipation Thermique](./media/schema_integration_stator_rs04_pelvis_et_femur.svg)

*Blueprint d'ingénierie vectoriel officiel — Intégration Stator RobStride RS-04 (DOC-ENG-RS04-ST). Panel 1 : Coupe axiale X-Z montrant l'emboîtement du bossage arrière Ø 94 mm dans l'alésage pilote Ø 95,0 mm H7 du flasque pelvien Alu 7075-T6 (5,0 mm), le contact franc à 0,0 mm sur l'épaulement Ø 120 mm, le film fin de pâte thermique Noctua NT-H1, et l'assemblage sécurisé par vis CHC M4 × 12 mm cl. 12.9 + rondelles Nord-Lock (pénétration 5,2 mm, garde de fond saine 0,8 mm dans le trou borgne de 6,0 mm). Panel 2 : Vue de face arrière du stator illustrant le PCD Ø 106,0 mm (10 trous M4 à 36°), les connecteurs CAN-FD / 48V Power et l'échappement silicone des câbles déporté. Panel 3 : Synthèse RDM (précharge 41 kN, M_frottement = 326 N.m >> 120 N.m, Sf = ×2,72, reprise tranchant 860 N par alésage) et bilan thermique constructeur (équivalence 345 × 345 mm).*

##### 1. Géométrie du Stator & Justification de la Fixation Monoface Arrière Seule (`Bride Epaule v87`)
Le stator du moteur RobStride RS-04 présente une couronne de 10 taraudages borgnes M4 sur **PCD Ø 106,0 mm** (contournage extérieur circonscrit `Ø 120,0 mm` / alésage pilote de centrage `Ø 97,00 mm H7` de la `Bride Epaule v87`) sur sa face arrière :
- **Pourquoi la fixation arrière seule sur `Bride Epaule v87` est-elle retenue ?**
  - **Reprise de l'Effort Tranchant Vertical (Choc de Marche 860 N)** : L'effort dynamique lors d'un impact au sol (`~35 kg × 2,5g ≈ 860 N`) est repris à **100 % par l'alésage de centrage pilote (`Ø 97,00 mm H7` sur la `Bride Epaule v87`, avec jeu radial/bague de centrage sur épaulement stator)** usiné dans l'Aluminium 7075-T6 (épaisseur de bride `5,0 mm` en Zone 1, moyeu `18,2 mm` en Zone 2). Le cisaillement direct sur les vis M4 est nul.
  - **Tenue au Couple de Pointe en Torsion (120 N.m Pic)** : Les 10 vis CHC M4 serrées à `3,0 N.m` avec rondelles frein Nord-Lock M4 (`91812A252`, `20` paires pour les 2 hanches) maintiennent une précharge axiale largement supérieure au glissement sous `120 N.m` (cf. [`STUDY_Calculs_FEA_Bride_Epaule_RS04.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Calculs_FEA_Bride_Epaule_RS04.md)).
  - **Abandon Définitif de la Cage H-Bracket Avant** : L'ajout d'une plaque avant enfermant le stator en sandwich apporterait 350 g de masse morte superflue par côté (soit **700 g sur le bassin**), compliquerait la maintenance et confinerait la face avant du moteur.

##### 2. Règle Inviolable de la Profondeur Borgne Stator (`6,0 mm MAX` — Zone 1 & Zone 2 `Bride Epaule v87`)
Le plan officiel constructeur (`RS04User Manual260112.pdf`, page 10) spécifie : `10-M4 EQS Blind Hole 6`.
- **Zone 2 (6 bossages épais `18,2 mm` du moyeu `Bride Epaule v87`)** : **6 vis CHC M4 × 25 mm Tête Basse DIN 7984 (`92855A422`)** + **Nord-Lock M4 (`91812A252`, ~1,8 mm)** -> pénétration filetée exacte `25,0 - 18,2 - 1,8 = 5,0 mm` (garde de fond saine **`1,0 mm`**).
- **Zone 1 (4 oreilles périphériques `5,0 mm` entre échancrures)** : Dans la CAO `Torse-123 v42`, des vis **`CHC M4 × 16 mm [90128A214]`** sont insérées en guise de repères. **Vigilance atelier obligatoire** : avec `5,0 mm` de flasque + `1,8 mm` de Nord-Lock, une vis de `16 mm` engage `9,2 mm > 6,0 mm` (risque de talonnage dans le taraudage borgne stator de `6,0 mm` !). **Au montage atelier réel, utiliser impérativement `CHC M4 × 12 mm [91290A154]`** (`12,0 - 6,8 = 5,20 mm` de prise utile, garde de fond **`0,80 mm`**) ou interposer une entretoise calibrée de `4 mm`.

##### 3. Rôle de Plaque Dissipatrice Géante (Heat Sink) du Squelette Pelvien
Le manuel RobStride spécifie qu'un couple continu de **40 N.m** requiert une plaque métallique dissipatrice de `345 × 345 mm` (ou `220 × 200 mm` pour 35 N.m) :
- Les **2 `Bride Epaule v87`** (`202,30 g`/u), rigidement couplées à la **Selle de Pont** (`338,98 g`), aux **4 Montants `20×20`**, au **Tube `60×60`** et à la **`Traverse_Renfort_Bassin` (`566,74 g`)**, forment un pont thermique continu de **plus de `1,5 kg` d'Aluminium 7075 / 6060**.
- **Protocole d'Atelier** : Application d'un film fin de pâte thermique non conductrice (*Noctua NT-H1* ou *Arctic MX-4*) sur la face d'appui stator et dans l'alésage pilote pour abaisser la résistance thermique de contact (-40 %).
- **Corridor de Câblage Déporté (Zéro Arbre Creux)** : Le faisceau 48V et CAN-FD sortant de l'arrière du RS-04 contourne la bride via les dégagements périphériques (règle RobStride arbre plein, zéro perçage axial).

---

#### 5.3.2 Intégration Rotor RS-04 : Roulement Croisé Interne & Protection par Goupilles Calibrées

![Intégration Rotor RobStride RS-04 — Roulement Croisé Interne & Protection par Goupilles Calibrées](./media/schema_integration_rotor_rs04_decouplage_et_goupilles.svg)

*Blueprint d'ingénierie vectoriel officiel — Intégration Rotor RobStride RS-04 (DOC-ENG-RS04-RT). Panel 1 : Coupe axiale détaillée illustrant le roulement à rouleaux croisés intégré d'origine dans le RS-04 (capacité au basculement 150-200 N.m), reprenant intégralement les moments dynamiques de hanche (50 à 90 N.m) sans nécessiter de roulement externe. Panel 2 : Motif d'accouplement du rotor montrant les 9 vis M5 sur PCD Ø 36,0 mm (traction pure) et les 5 alésages de goupilles sur PCD Ø 35,86 mm (2× Ø 5,0 mm + 3× Ø 6,0 mm ISO 8734 reprenant 100% du cisaillement sous 120 N.m). Panel 3 : Matrice de décision système comparant l'épaule (zéro roulement externe), la hanche (roulement interne + goupilles), le genou (courroie GT3 2,5:1) et la taille (roulement externe CRBH 8016 indispensable).*

##### 1. Pourquoi le Rotor RS-04 Ne Nécessite Aucun Roulement Externe à la Hanche
À la différence des petits servomoteurs ou des moteurs brushless simples montés sur de petits roulements à billes, le RobStride RS-04 est un **actionneur quasi-direct (QDD) à réducteur cycloïdal industriel** :
- **Roulement à Rouleaux Croisés Interne Intégré** : L'étage de sortie du RS-04 intègre d'usine un roulement à rouleaux croisés de grand diamètre (piste moyenne ~ Ø 80 mm) avec galets cylindriques croisés à 90° dans une gorge en V trempée.
- **Capacité de Charge Intégrée** : Ce roulement interne tolère une charge radiale de plus de 3 000 N et un **moment de basculement admissible (*tilting moment*) de 150 à 200 N.m**.
- **Efforts Réels Mesurés à la Hanche Bipède (Robot 35 kg)** :
  - En marche normale (foulée 1,2 m/s) : moment de basculement latéral de hanche `M_lat ≈ 35 à 55 N.m`.
  - Lors d'un impact de talon ou d'une décélération vive (K_dyn = 2,0) : pic de basculement `M_pic ≈ 80 à 90 N.m`.
  - Facteur de sécurité interne : `Sf = 160 N.m / 90 N.m =` **`×1,78 à ×2,20 ✅`**.
- **Verdict d'Architecture Système** :
  - Le roulement interne du RS-04 est **pleinement suffisant** pour encaisser les charges de hanche.
  - Ajouter un gros roulement externe auxiliaire (type CRBH ou palier 4 points) à chaque hanche ajouterait ~300 g de masse morte par articulation (+600 g sur le bas du corps), allongerait l'envergure transversale des hanches et créerait un hyperstatisme axial extrêmement complexe à usiner et aligner.

##### 2. La Règle d'Or RDM : Découplage Traction / Cisaillement par Goupilles Calibrées
Si le roulement interne encaisse parfaitement les moments de basculement, la transmission du couple de torsion pur (120 N.m pic) et des à-coups angulaires ne doit **JAMAIS reposer sur le cisaillement des vis de fixation** :
- **Motif Hybride Officiel du Rotor RS-04** :
  - **9 Trous Borgnes Taraudés M5 (PCD Ø 36,0 ± 0,1 mm)** : profondeur utile minimale 6,5 mm (serrage par vis CHC M5 classe 12.9 à 5,5 N.m avec frein-filet Loctite 243).
  - **5 Trous Alésés pour Goupilles de Centrage (PCD Ø 35,86 ± 0,025 mm)** :
    - **2 alésages rectifiés `Ø 5,0 (+0 / -0,01) mm`**.
    - **3 alésages rectifiés `Ø 6,0 (+0 / -0,01) mm`**.
- **Principe de Découplage des Sollicitations** :
  - Les **5 goupilles cylindriques rectifiées trempées ISO 8734 / DIN 6325** (tolérance m6 emmanchées serrées dans le L-bracket ou le fémur) reprennent **100% de l'effort de cisaillement** lors des accélérations de marche et des blocages de réducteur.
  - Les **9 vis M5 travaillent exclusivement en traction pure**, maintenant un placage axial franc et rigide entre la face du rotor et le L-Bracket.
  - Ce découplage garantit une durée de vie infinie sans matage de filet, sans desserrage sous vibrations et sans jeu angulaire (zéro backlash parasite).

##### 3. Matrice de Décision Synthétique de l'Architecture D-Bot

| Articulation | Moteur | Roulement Externe Dédié ? | Justification Mécanique & Cinématique |
| :--- | :---: | :---: | :--- |
| **Épaule Pitch** | RS-04 | **NON ❌ (0 g)** | Moments bras modérés (24 à 73 N.m). Roulement interne RS-04 largement suffisant. Zéro cage, gain de 368 g/bras. |
| **Hanche Hip Pitch** | RS-04 | **NON ❌ (0 g)** | Moments de hanche (50 à 90 N.m) < 160 N.m admissibles. **5 goupilles ISO 8734 obligatoires** pour le couple de 120 N.m. |
| **Genou Knee** | RS-04 | **NON ❌ (0 g)** | Transmission déportée courroie GT3 (ratio 2,5:1). Le rotor ne subit que la tension courroie (50 N). L'axe genou 50T a son propre palier. |
| **Taille Waist Yaw** | RS-06 | **OUI ✅ (CRBH 8016)** | Torse complet suspendu (~17,3–18,3 kg dynamique ; `18,32 kg` bruts Torse+Bassin CAO `v42`), générant 56 à 220 N.m. Le petit RS-06 (36 N.m) exige un découplage axial absolu. |

### 5.4 Système de Butée Mécanique de Lacet (+/- 95°) & Sécurisation Globale

> [!IMPORTANT]
> **Statut CAO (`Torse-123 v42`) — Modification Prévue Avant Usinage CNC** :
> Le système de butée mécanique matérielle **Palier 3 (`+/- 95,0°`, doigt mobile côté avant `+X` sous l'aile `6,00 mm` de `Waist_Plate_7075` + 2 plots fixes amortis TPU 95A sur `Traverse_Renfort_Bassin` à `R = 80,50 mm` / `±109,86°`)** décrit ci-dessous **n'est pas encore modélisé dans `Torse-123 v42`**. Toutes les cotes ci-dessous sont calibrées directement sur `Torse-123 v42` (aile ext. Waist `6,00 mm` à `Z = 1036,42..1042,42 mm`, aile ext. Traverse `10,02 mm` à `Z = 1010,39..1020,41 mm`, zéro conflit avec la lumière banane dorsale `-X`).

![Schéma de Butée Angulaire par Doigt Externe](./media/schema_butee_angulaire_doigt_externe_waist.svg)

*Blueprint vectoriel d'ingénierie actualisé (`Torse-123 v42`) — Panneau 1 : Vue de dessus polaire montrant le doigt mobile côté `+X` (`0°`), sa course exacte `+/- 95,0°` et les 2 plots fixes amortis TPU 95A centrés à `±109,86°` sur `R = 80,50 mm` hors des brides `RB8016` (`R_max ~ 72,4 mm`), des vis FHC de coin et de la fente dorsale `-X`. Panneau 2 : Coupe axiale Z (`Z = 1010..1042 mm`), cotation complète des 3 pièces (`WST-07A/B/C`) et tableau des coordonnées Fusion 360.*

![Sécurisation de la Rotation Waist Yaw & Preuve de Non-Interférence Nylstop](./media/schema_securisation_rotation_waist_et_non_interference_nylstop.svg)

*Schéma d'ingénierie vectoriel officiel mis à jour (Torse v107) : Panneau 1 — Vue cinématique de dessus XY montrant l'orbite des 4 vis/écrous de fixation du Plastron Ventral (R = 88,8 mm à 94,2 mm) restant strictement à l'extérieur des 4 brides étagées en L (R_max = 79,5 mm), avec une marge radiale nette minimale de +5,3 mm. Panneau 2 — Coupe axiale Z cotée illustrant l'espace libre de 16,02 mm sous la Waist Plate et la garde résiduelle de 11,01 mm au-dessus de la Traverse. Panneau 3 — Matrice de synthèse des 3 niveaux de sécurité angulaire et des gardes métrologiques.*

Afin de sécuriser physiquement et logiciellement la rotation de lacet de taille face à tout risque de vrillage destructeur du faisceau électrique ou de collision interne, le sous-système de pivot pelvien intègre une chaîne de protection redondante à 3 niveaux articulée avec le dimensionnement élargi `Torse v107` :

#### 5.4.1 Architecture de Sécurisation Globale à 3 Paliers (+/- 80°, +/- 82°, +/- 95°)

1. **Palier 1 — Course Nominale Asservie (Whole-Body Control / Motion Planning) : `[-80,0°, +80,0°]` (160,0° total)** :
   - Plage dynamique exploitée en temps réel par les algorithmes de marche, de stabilisation et de manipulation bimanuelle.
   - Respecte scrupuleusement la loi de torsion linéique admissible du faisceau électrique (`<= 0,50° / mm` sur les 160 mm de boucle libre).

2. **Palier 2 — Butée Logicielle & Arrêt d'Urgence Firmware (Soft Limits) : `+/- 82,0°`** :
   - Surveillé en permanence par le firmware de l'actionneur RobStride RS-06 (encodeur absolu 17 bits) et la boucle de contrôle bas niveau (Jetson Orin Nano).
   - En cas de dépassement de +/- 82,0° (emballement de trajectoire ou perte de convergence), coupure immédiate de la commande en couple, déclenchement d'un freinage rhéostatique dynamique et passage en état d'arrêt d'urgence sécurisé (E-Stop).

3. **Palier 3 — Butée Mécanique Matérielle Infranchissable (Hard Stop) : `+/- 95,0°` (190,0° total) *(Modification CAO prévue avant usinage CNC)*** :
   - **Positionnement Géométrique & Rayon d'Implantation (`R = 80,50 mm`)** :
     - Implanté sur le cercle **`R = 80,50 mm`** centré sur l'axe RS-06 / RB8016 (`X_0 = +49,23 mm`, `Y_0 = +9,36 mm`). Ce rayon garantit simultanément **`+3,10 mm` de jeu radial franc** au-delà des 4 brides `Bride_Retenue_RB8016_L` (`R_int_doigt = 75,50 mm > R_max_reel_bride = 72,4 mm`), **`+6,70 mm` de bord sain** sur les flancs `+/- Y` de la `Traverse_Renfort_Bassin` (`Y_max = +96,77 mm`, `Y_min = -78,06 mm`), et **`+3,33 mm` de garde radiale** intérieure vis-à-vis des 4 vis du `Plastron_Ventral_Torse` (`R = 88,83..94,17 mm`, `Z >= 1034,93 mm`).
   - **Design Mécanique du Doigt Mobile (`WST-07A`, sous l'aile externe de `Waist_Plate_7075`)** :
     - *Position neutre (`0,0°`, côté `+X` Avant)* : Implanté côté avant `+X` en pleine matière (`X_centre = +49,23 + 80,50 = +129,73 mm`, `Y_centre = +9,36 mm`, laissant **`+2,55 mm` de bord** devant `X_max = +137,28 mm` ; la zone `-X` à `X = -31,27 mm` est proscrite car occupée par l'arc banane `125,05°` `R = 64,75..84,75 mm`).
     - *Architecture physique* : Bloc usiné en **Aluminium 7075-T6** de dimensions **`10,0 mm` (radial X) × `18,0 mm` (tangentiel Y) × `8,00 mm` (hauteur Z)**, chanfreins `0,5 mm × 45°`, plaqué sous l'aile périphérique de la `Waist_Plate_7075` (`Z_inf_ext = 1036,42 mm`, épaisseur locale `6,00 mm`). Emprise verticale **`Z = [1028,42 ; 1036,42 mm]`** (au-dessus du sommet maximal `1026,22 mm` de `Chassis_Structurel_Bassin_Last`).
     - *Fixation par le dessous (Respect Doctrine "Zéro Lamage/Fraisure <= 10 mm" & Zéro saillie sous Plastron)* : Aucune fraisure ni lamage n'est creusé dans les `6,00 mm` de la `Waist_Plate_7075` et aucune tête de vis ne dépasse au-dessus de `Z = 1042,42 mm` sous le `Plastron_Ventral_Torse`. Le doigt comporte `2×` perçages lisses `Ø 4,50 mm` (entraxe tangentiel **`d = 10,00 mm`**) et se fixe par-dessous via **`2× vis CHC M4 × 14 mm classe 12.9` (`91290A150`)** + **`2× rondelles DIN 125A M4` (`93475A230`, ép. 0,8 mm)** vissées au Loctite 243 (serrage `2,8 N.m`) dans `2×` taraudages directs `M4 × 0,7 mm` de `Waist_Plate_7075` (prise filetée `14,0 - 8,8 = 5,20 mm`, retrait `-0,80 mm` sous la face supérieure `1042,42 mm` ; bas des têtes CHC à `Z = 1023,62 mm`, soit **`+3,21 mm` de vide** au-dessus de `Traverse`).
   - **Design Mécanique des Deux Plots de Butée Fixe (`WST-07B/C`, sur `Traverse_Renfort_Bassin`)** :
     - *Loi angulaire exacte autour du pivot `[49,23 ; 9,36]` (`0° = +X`)* :
       - Demi-angle du doigt mobile (`±9,0 mm` à `R = 80,50 mm`) : `atan(9,0 / 80,50) =` **`6,38°`**.
       - Demi-angle avant du plot Alu (`±9,0 mm`) + capuchon amortisseur **TPU 95A** frontal (`3,00 mm`) = `12,0 mm` -> `atan(12,0 / 80,50) =` **`8,48°`**.
       - Pour obtenir un contact franc exactement à **`+/- 95,0°`** de rotation du torse : la face d'impact TPU se situe à `95,0° + 6,38° =` **`+/- 101,38°`**, et le **centre géométrique de chaque plot fixe Alu** est implanté à **`+/- 109,86°`** (face arrière Alu à `+/- 116,24°`, soit à `>= 35,2°` devant la fente banane Traverse à `+/- 151,45°` et à `29,1–29,8 mm` centre-à-centre des vis FHC `NW/SW` à `+/- 131°`).
     - *Coordonnées cartésiennes des centres de plots sur `Traverse_Renfort_Bassin` (`Z_sup = 1020,41 mm`, ép. aile locale `10,02 mm`)* :
       - **Plot Gauche (`+109,86°`)** : **`X = +21,89 mm` ; `Y = +85,07 mm`** (vis M4 à `[17,18 ; +83,37]` et `[26,59 ; +86,77]`).
       - **Plot Droit (`-109,86°`)** : **`X = +21,89 mm` ; `Y = -66,35 mm`** (vis M4 à `[26,59 ; -68,05]` et `[17,18 ; -64,65]`).
     - *Architecture physique (`WST-07B`)* : Bloc usiné en **Aluminium 7075-T6** (`10,0 mm` radial × `18,0 mm` tangentiel × `11,50 mm` hauteur Z, emprise `Z = [1020,41 ; 1031,91 mm]`), percé `2× Ø 4,50 mm` avec lamages cylindriques **`Ø 7,50 mm × prof. 5,50 mm`** (semelle porteuse `6,00 mm`, tête CHC noyée à `-1,50 mm` sous le sommet du plot) et vissé dans 2 taraudages borgnes `M4 × 0,7` prof. `8,00 mm` de la Traverse via **`4× vis CHC M4 × 14 mm classe 12.9` (`91290A150`)** (serrage `2,8 N.m` + Loctite 243).
     - *Amortisseur frontal imprimé 3D (`WST-07C`)* : Capuchon creux fermé sur 5 faces (ouvert en bas `-Z`) imprimé à l'envers en **TPU 95A** (`100 %`, zéro support), de format extérieur **`12,40 × 22,20 × 12,70 mm`** (`congés R = 1,5 mm`, `R_int = 74,30 mm` / `R_ext = 86,70 mm`) et de poche interne **`9,90 × 17,90 × 11,50 mm`** (serrage élastique `-0,05 mm`/paroi, chanfrein d'entrée bas `0,5 × 45°`). Parois : **`3,00 mm`** côté choc (`±101,38°`), **`1,20 mm`** sur les 3 autres faces et sur la coiffe supérieure (`Z_TPU_max = 1033,11 mm`). *(Option : `2× Ø 5,0 mm` sur coiffe pour clé Allen 3 mm.)*
   - **Cinématique de Choc & Gardes Verticales (`Torse-123 v42`)** :
     - *Zone de contact franc (Recouvrement vertical)* : `h_contact = 1031,91 - 1028,42 =` **`3,49 mm`** (~`3,5 mm` pleine face sur `10,0 mm` radial, `A_contact = 34,9 mm^2`).
     - *Garde d'air au-dessus du capuchon TPU (`Z_TPU_max = 1033,11 mm`)* : `Z_waist_ext - Z_TPU_max = 1036,42 - 1033,11 =` **`+3,31 mm` d'air franc** (`+4,51 mm` sur Alu seul — rend le capuchon mécaniquement captif tant que `Waist_Plate` est montée).
     - *Garde d'air sous les vis du doigt mobile* : `Z_tete_vis - Z_traverse = 1023,62 - 1020,41 =` **`+3,21 mm` d'air franc**.
   - **Résistance RDM au Rayon `R = 80,50 mm`** :
     - Effort tangentiel statique sous couple crête `RS-06` (`36 N.m`) : `F_tang = 36 / 0,0805 = 447,2 N`.
     - Choc dynamique d'inertie torse (`k_dyn = 2,5`) : `F_dyn ~ 1 118 N`.
     - Pression de matage sur Alu 7075 (`34,9 mm^2`) : `Sigma_matage = 1 118 / 34,9 = 32,0 MPa << 505 MPa` (`Sf_matage = 15,8`).
     - Couple de basculement (`h_moy ~ 9,75 mm` depuis plan Traverse sur plot) : `M_bascul = 1 118 × 0,00975 ~ 10,9 N.m` dynamique (statique `4,36 N.m`), repris en traction par l'entraxe `d = 10,0 mm` (`436 N` statique soit `< 8 %` de la précharge d'une vis `M4 12.9` ~ `5 500 N`). Cisaillement des `2× M4 12.9` : `Tau_dyn = 1 118 / (2 × 8,78) = 63,7 MPa << 600 MPa` (`Sf_cisaillement > 9,4` dynamique / `23` statique).

##### Cartographie Complète des Perçages, Lamages & Taraudages d'Atelier (CNC C500 / Perçeuse à Colonne)

Le tableau ci-dessous récapitule les coordonnées cartésiennes exactes (repère CAO `Torse-123 v42`) à appliquer sous Fusion 360 et sur la machine CNC NestWorks C500 :

| Repère Opération | Pièce Usinée | Rôle & Composant | Coordonnées Cartésiennes (`Torse-123 v42`) | Diamètre & Outil CNC | Profondeur d'Usinage | Spécifications d'Atelier & Visserie |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TARA-W00A** | **`Waist_Plate_7075`**<br>(aile ext. ép. `6,00 mm`) | **2 Taraudages Fixation Doigt** (+X, 0°) | Trou 1 : `X = +129,73 ; Y = +4,36 mm`<br>Trou 2 : `X = +129,73 ; Y = +14,36 mm` | Foret **`Ø 3,30 mm`** + Taraud **`M4 × 0,7 mm (6H)`** | Débouchant (`6,00 mm`), chanfrein `0,2 × 45°` | **Zéro lamage / zéro fraisure** sur Waist Plate (`<= 10 mm`). Reçoit par dessous **2× CHC M4×14 [91290A150]** + rondelles `[93475A230]` (prise `5,20 mm`, zéro saillie face sup. `1042,42`). |
| **PERC-W01** | **Doigt Mobile `WST-07A`**<br>(`10 × 18 × 8,00 mm`) | **2 Perçages Lisses Doigt** | Entraxe tangentiel `d = 10,00 mm`<br>(centré sur `[+129,73 ; +9,36]`) | Foret **`Ø 4,50 mm`** | Débouchant (`8,00 mm`), chanfreins `0,3 × 45°` | **Zéro lamage** (visse par en-dessous avec rondelle `[93475A230]` sous tête). |
| **LAMA-W01** | **2 Plots Fixes `WST-07B`**<br>(`10 × 18 × 11,50 mm`) | **4 Lamages & Perçages** (2 par plot) | Entraxe tangentiel `d = 10,00 mm`<br>Symétrie sur largeur `10,0 mm` | Foret **`Ø 4,50 mm`** + Fraise à lamer **`Ø 7,50 mm`** | Perçage `11,50 mm` + Lamage prof. **`5,50 mm`** | Semelle restante **`6,00 mm`**. Têtes CHC M4 (H = 4,0 mm) noyées `-1,50 mm` sous le sommet `1031,91`. |
| **TARA-W02** | **`Traverse_Renfort_Bassin`**<br>(aile ext. ép. `10,02 mm`) | **2 Taraudages Plot G** (`+109,86°`) | Centre : `X = +21,89 ; Y = +85,07 mm`<br>Vis : `[17,18 ; +83,37]` & `[26,59 ; +86,77]` | Foret **`Ø 3,30 mm`** + Taraud **`M4 × 0,7 mm (6H)`** | Avant-trou borgne prof. **`9,00 mm`** / Filet **`8,00 mm`** | Chanfrein entrée `0,4 mm × 45°`. Reste `1,02 mm` sous trou borgne dans `10,02 mm`. Reçoit **2× CHC M4 × 14 mm [91290A150]** (`2,8 N.m`). |
| **TARA-W03** | **`Traverse_Renfort_Bassin`**<br>(aile ext. ép. `10,02 mm`) | **2 Taraudages Plot D** (`-109,86°`) | Centre : `X = +21,89 ; Y = -66,35 mm`<br>Vis : `[26,59 ; -68,05]` & `[17,18 ; -64,65]` | Foret **`Ø 3,30 mm`** + Taraud **`M4 × 0,7 mm (6H)`** | Avant-trou borgne prof. **`9,00 mm`** / Filet **`8,00 mm`** | Chanfrein entrée `0,4 mm × 45°`. Reste `1,02 mm` sous trou borgne dans `10,02 mm`. Reçoit **2× CHC M4 × 14 mm [91290A150]** (`2,8 N.m`). |

4. **Palier 4 — Protection Anti-Guillotine du Faisceau Électrique (cf. Section 5.5)** :
   - Fente stator fixe de 69,05° dans la Traverse pelvienne combinée à la fente rotor mobile élargie à 125,05° dans la Waist Plate.
   - À l'extrême nominal de +/- 80,0°, le recouvrement résiduel libre est de `17,05°`, offrant une fenêtre de passage traversante de **`22,24 mm`** d'arc pour un faisceau de Ø 15 mm, soit une **marge saine garantie de `+7,24 mm`** de vide d'air franc sans aucun risque de pincement ni cisaillement.

---

#### 5.4.2 Preuve Cinématique de Non-Interférence des 4 Écrous Nylstop M4 sous Waist Plate

Lors de la modélisation de `Torse v107`, 4 perçages traversants ont été intégrés sur la Waist Plate (`Waist_Plate_7075`) pour sécuriser l'assise basse du Plastron Ventral (`Plastron_Ventral_V2`). L'analyse métrologique complète ci-dessous démontre rigoureusement l'absence totale de collision ou de gêne cinématique si le plastron est fixé par des vis CHC M4 associées à des **écrous autofreinés Nylstop M4** (DIN 985) placés sous la Waist Plate :

##### 1. Coordonnées et Orbites Radiales des 4 Perçages de Fixation

L'axe de rotation du RS-06 et du roulement RB8016 est positionné à `X_0 = +49,23 mm` et `Y_0 = +9,36 mm`. Les rayons orbitaux `R = sqrt((X - X_0)^2 + (Y - Y_0)^2)` décrits lors de la rotation sont les suivants :

| Point de Fixation | Coordonnées CAO (X, Y) | Décalage Delta_X / Delta_Y | Rayon Orbital (R) | Position Géométrique |
| :--- | :---: | :---: | :---: | :--- |
| **H1 (Arrière-Droit)** | `X = -17,90 mm, Y = -56,68 mm` | `-67,13 mm / -66,04 mm` | **`R1 = 94,17 mm`** | Zone dorsale droite |
| **H2 (Arrière-Gauche)** | `X = -17,90 mm, Y = +75,39 mm` | `-67,13 mm / +66,03 mm` | **`R2 = 94,16 mm`** | Zone dorsale gauche |
| **H3 (Avant-Droit)** | `X = +103,30 mm, Y = -62,50 mm` | `+54,07 mm / -71,86 mm` | **`R3 = 89,93 mm`** | Zone ventrale droite |
| **H4 (Avant-Gauche)** | `X = +103,30 mm, Y = +79,84 mm` | `+54,07 mm / +70,48 mm` | **`R4 = 88,83 mm`** | Zone ventrale gauche |

##### 2. Absence Totale d'Interférence Radiale avec les 4 Brides de Retenue RB8016

- **Emprise Radiale Maximale des Brides** : Les 4 brides étagées en L (`Bride_Retenue_RB8016_L`) fixées à 45°, 135°, 225° et 315° sur PCD Ø 136 mm sont strictement confinées à l'intérieur d'un cylindre de rayon maximal **`R_max_brides = 79,52 mm`**.
- **Gabarit Enveloppe d'un Écrou Nylstop M4 (DIN 985 / ISO 10511)** :
  - Surplat : `s = 7,00 mm`.
  - Diamètre sur-coins maximal : `e = 8,00 mm` (rayon d'encombrement `r_nut = 4,00 mm`).
- **Marges de Dégagement Radial Mesurées** :
  - **Sur H1 et H2** : Garde à l'axe = `94,16 - 79,52 = +14,64 mm` ➔ **Garde au sur-coin de l'écrou = `+10,64 mm`**.
  - **Sur H3** : Garde à l'axe = `89,93 - 79,52 = +10,41 mm` ➔ **Garde au sur-coin de l'écrou = `+6,41 mm`**.
  - **Sur H4 (Point le plus proche)** : Garde à l'axe = `88,83 - 79,52 = +9,31 mm` ➔ **Garde au sur-coin de l'écrou = `+5,31 mm`**.
- **Conclusion Radiale** : Sur l'intégralité de la rotation (de `-95,0°` à `+95,0°` et même sur 360°), l'orbite des écrous reste rigoureusement en dehors du cylindre des brides. Il y a un **vide radial permanent garanti supérieur à 5,3 mm**.

##### 3. Absence Totale d'Interférence Axiale en Z avec la Traverse Pelvienne

- **Entrefer Vertical Libre Disponible** :
  - Altitude face inférieure de la Waist Plate : **`Z = 1036,42 mm`**.
  - Altitude face supérieure de la Traverse Renfort Pelvis : **`Z = 1020,41 mm`**.
  - Espace vertical libre total sous plaque : `1036,42 - 1020,41 =` **`16,01 mm`** (confirmé 16 mm de vide d'air).
- **Hauteur Hors-Tout de l'Écrou Nylstop M4 (DIN 985)** :
  - Écrou Nylstop standard : `h = 5,00 mm` (bague polyamide incluse).
  - Avec rondelle plate DIN 125A M4 (épaisseur 0,8 mm) ou DIN 433 (0,5 mm) : encombrement total `h_tot = 5,50 mm` à `5,80 mm`.
  - Altitude de la face inférieure de l'écrou : `Z = 1036,42 - 5,00 = 1031,42 mm`.
- **Garde Axiale Résiduelle au-dessus de la Traverse** :
  - `Z_garde = 1031,42 - 1020,41 =` **`+11,01 mm de vide d'air franc`** (et `+10,21 mm` avec rondelle DIN 125A).
- **Conclusion Axiale** : Les écrous Nylstop M4 lévitent à plus de **`11,0 mm` au-dessus de la Traverse**. Zéro frottement, zéro contact de surface.

##### 4. Dégagement Face aux Butées Mécaniques Fixes (`R = 80,50 mm`)

- **Altitude et Rayon des Plots Fixes (`WST-07B/C`)** : Implantés sur la Traverse à `R = 80,50 mm` (`R_ext_Alu = 85,50 mm`, `R_ext_TPU = 86,70 mm`) et culminant à `Z = 1031,91 mm` (Alu) / `1033,11 mm` (coiffe TPU `1,20 mm`).
- **Dégagement Radial et Vertical avec les Vis du Plastron (`R = 88,83..94,17 mm`)** :
  - Avec l'Option B retenue (`v42`, taraudage direct dans `Waist_Plate`, zéro écrou Nylstop pendant sous `Waist_Plate`), les 4 perçages/vis du Plastron restent en dehors de l'enveloppe des plots (`88,83 - 86,70 = +2,13 mm` de marge radiale à l'axe) ET plus haut verticalement (`Z >= 1034,93 mm > 1033,11 mm`, soit `+1,82 mm` de garde verticale même en survol à `~57°` de lacet). Aucun contact possible.

##### 5. Arbitrage de Réalisation en Atelier : Écrous Nylstop M4 vs Taraudage Direct dans la Waist Plate

Bien que l'utilisation d'écrous Nylstop M4 soit **100% validée mécaniquement et cinématiquement sans la moindre interférence**, deux options d'assemblage restent offertes pour l'atelier :

1. **Option A — Montage Traversant avec Écrous Autofreinés Nylstop M4 (Option Validée)** :
   - Vis CHC M4 × 16 mm insérées par le dessus dans le Plastron Ventral, traversant la Waist Plate (perçages lisses Ø 4,5 mm), serrées par écrous Nylstop M4 DIN 985 sous la plaque.
   - *Avantage* : Remplacement aisé en cas d'usure de filetage.
   - *Contrainte d'atelier* : Nécessite de maintenir l'écrou sous la plaque avec une clé plate ou douille fine de 7 mm lors du serrage dans l'entrefer de 16 mm.

2. **Option B — Taraudage Direct M4 dans la Waist Plate 7075-T6 (Recommandation Atelier Senior)** :
   - La Waist Plate présentant une épaisseur massive de **`6,00 mm` en Aluminium 7075-T6** certifié (Rm > 540 MPa), un taraudage direct M4 au pas standard de 0,7 mm offre **`8,5 filets en prise`** (soit `1,5 × Ø_vis`).
   - La résistance à l'arrachement du filet en 7075-T6 est supérieure à la charge de rupture de la vis acier classe 8.8 ou 10.9 (la vis casse avant que le filet en aluminium ne s'arrache).
   - *Avantage majeur* : Démontage et remontage ultra-rapides du plastron lors de la maintenance en atelier, par le dessus, à la simple clé Allen de 3 mm, sans avoir à accéder à l'espace confiné sous la plaque.

### 5.5 Système de Câblage à Lumières Concentriques d'Arc Arrière (Traverse 69° vs Waist Plate 125°) et Zéro Cisaillement

Pour permettre le transit sans contrainte des lignes d'alimentation de puissance et de communication différentielle entre le haut du corps (batteries 13S/48V, calculateurs Jetson/Mac) et le bas du corps (actionneurs de hanches RS-04, busbars pelviens et bus CAN-FD), l'interface de lacet de taille (Waist Yaw +/- 80°) a été validée selon les standards les plus exigeants de la robotique humanoïde de pointe (Boston Dynamics Atlas, Tesla Optimus Gen 2, Unitree H1/G1) :

#### A. Diagnostic Critique des Fentes Fermées Identiques & Risque d'Effet Guillotine
L'étude cinématique fine du modèle CAO `Torse v102` a mis en évidence la loi physique du recouvrement entre deux fentes fermées en rotation relative :
1. **Loi de Recouvrement Angulaire Dégressif** :
   - Si la Traverse fixe et la Waist Plate mobile possèdent deux fentes fermées identiques de 68,8°, l'ouverture traversante commune décroît linéairement selon la formule :  
     `Ouverture_utile(theta) = 68,8° - |theta|`
   - À `theta = +/- 34,4°`, l'ouverture ne fait plus que la moitié (`34,4°`).
   - À `theta = +/- 68,8°`, le recouvrement devient strictement **nul (0,0°)** : fermeture totale du passage.
   - Au-delà de +/- 68,8°, les fentes sont disjointes et les arêtes métalliques agissent comme une cisaille franche (**effet guillotine pur**), tranchant net les conducteurs 48V et les paires CAN-FD.
2. **Dimensionnement du Faisceau Électrique Traversant** :
   - Le faisceau regroupe : 2 conducteurs silicone 12 AWG (+48V et GND, isolant haute flexibilité), 2 paires torsadées blindées CAN-FD, le tout sous gaine tressée extensible anti-abrasion en polyester (PET).
   - Le diamètre effectif du faisceau assemblé atteint **`Ø 14,0 à Ø 15,0 mm`** (soit un arc de **`11,5°`** au rayon médian `R = 74,75 mm`).

#### B. Géométrie Validée des Deux Lumières Concentriques en Arc de Cercle
Pour autoriser une rotation sans bride de **`+/- 80,0°`** (et jusqu'à `+/- 82,0°` en marge de sécurité), l'architecture adopte un couple de lumières concentriques dissymétriques situées en **zone postérieure (-X)** :

1. **Centrage Rigoureux & Zéro Décentrage** :
   - Centre géométrique des arcs : **`X = +49,23 mm, Y = +9,36 mm`** (aligné au micron près sur l'axe du rotor RS-06 et du roulement RB8016).
   - Rayon intérieur : **`R_int = 64,75 mm`** (Ø 129,50 mm).
   - Rayon extérieur : **`R_ext = 84,75 mm`** (Ø 169,50 mm).
   - Largeur radiale nette de passage : **`20,00 mm`** (rayon médian de passage `R_mid = 74,75 mm`).
   - Raccordements d'extrémités : congés demi-circulaires de **`Ø 16,00 mm`** (rayon R = 8,0 mm).
2. **Lumière Stator Fixe (Traverse Renfort Bassin)** :
   - Ouverture angulaire : **`69,05°`** (demi-angle de `34,52°` de part et d'autre de 180°).
   - Masse réelle CAO (`Torse-123 v42`) : **`566,74 g`** (en Aluminium 7075-T6, volume `201,69 cm3`).
   - Pont de matière intérieur face à la bague extérieure du roulement RB8016 : **`4,75 mm`** de métal plein continu.
   - Pont de matière résiduel arrière : **`3,31 mm`**.
3. **Lumière Rotor Mobile (Waist Plate 7075)** :
   - Ouverture angulaire élargie : **`125,05°`** (demi-angle de `62,52°` de part et d'autre de 180°).
   - Masse réelle CAO (`Torse-123 v42`) : **`433,53 g`** (en Aluminium 7075-T6, volume `154,28 cm3`).
   - Flancs latéraux gauche et droit résiduels : **`14,9 mm`** de matière pleine de chaque côté.
   - Dégagement franc face aux cornières de colonne vertébrale : **`> 14,0 mm`** en X.

#### C. Spécification d'Atelier : Congés R = 1,5 mm sur Arêtes d'Entrée et Sortie
Conformément aux règles de l'art aérospatial et robotique, les arêtes vives d'usinage sont strictement proscrites :
* **Usinage des Congés** : Congé continu de **`R = 1,5 mm`** appliqué sur l'intégralité du contour fermé des faces supérieure et inférieure des deux plaques (`Waist_Plate_7075` et `Traverse_Renfort_Bassin`).
* **Rôle Fonctionnel** :
  - Élimine tout tranchant résiduel d'usinage CNC.
  - Forme un pavillon d'appui doux évitant la concentration de contraintes de contact (Hertz).
  - Laisse `3,0 mm` de flanc droit vertical au centre de la tôle de 6,0 mm pour un guidage net.
* **Procédé CNC C500** : Usiné directement en reprise à la fraise quart de cercle R1.5 (corner rounding endmill) ou fraise conique à 45°, suivi d'un toilage manuel doux grain 400/800.

#### D. Cinématique de Recouvrement Dynamique & Zéro Cisaillement (+/- 80°)
Le fonctionnement dynamique du passage de faisceau sur toute la plage de lacet valide l'absence absolue de cisaillement :

| Angle de Lacet (theta) | Recouvrement Angulaire Libre | Arc Traversant Libre (R = 74,75 mm) | Marge Nette pour Faisceau Ø 15 mm | Comportement Cinématique |
| :--- | :--- | :--- | :--- | :--- |
| **0° (Neutre)** | `34,52° + 62,52° = 97,05°` | **126,6 mm** | **+111,6 mm** | Dégagement immense |
| **40°** | `57,05°` | **74,4 mm** | **+59,4 mm** | Dégagement très large |
| **80° (Cible Nominale)** | `17,05°` | **22,24 mm** | **+7,24 mm** | **PARFAIT (Passage fluide sans contact)** |
| **82° (Sécurité Mécanique)** | `15,05°` | **19,63 mm** | **+4,63 mm** | Passage franc sécurisé |

* **Condition d'installation** : Le câble est ancré sur la colonne vertébrale à `Z = 1080 mm` et dans le pelvis à `Z = 950 mm`. Il n'est pas pincé dans la lumière de la Waist Plate, mais glisse librement le long de celle-ci, absorbant la rotation par une **torsion hélicoïdale douce de `0,50° / mm`** sur une longueur libre de `L = 160 mm` (très en-deçà du seuil critique de `1,0° / mm`).

#### E. Maintenance en Atelier & Démontabilité Modulaire (Zéro Dessoudage)
* **Passage Intégral des Connecteurs Haute Puissance** : Grâce à la largeur radiale de **`20,0 mm`** et la longueur d'arc de 69° / 125°, les connecteurs de puissance **XT60** (`15,5 × 8,0 mm`) ou **XT90** (`21,0 × 10,0 mm`) traversent l'ouverture sans aucun besoin de dessouder ni débrocher les câbles en atelier.
* **Gaine de Protection** : Faisceau gainé sous tresse textile extensible en polyester PET haute ténacité avec colliers de retenue souples.

---

### 5.6 Gestion Thermique du RS-06 Waist & Ventilation du Caisson Pelvien

L'actionneur RobStride RS-06 (couple continu nominal de 11 N.m, couple de crête de 36 N.m) dissipe entre **15 W et 25 W thermiques** en régime de régulation Whole-Body Control (WBC) actif continu. Implanté au cœur du caisson pelvien fermé, sa dissipation thermique repose sur une stratégie hybride à deux niveaux :

#### A. Dissipation Conductive Primaire (Alu 7075-T6 Métal-Métal)
* **Contact Direct Traverse ➔ Stator** : La `Traverse_Renfort_Bassin` (épaisseur totale `12,51 mm` en Aluminium 7075-T6, masse réelle `v42` = **`566,74 g`**) présente un bossage inférieur descendant à `Z = 1007,90 mm` qui vient en contact plan métal-métal direct sur la face supérieure du stator du RS-06 (`Z_max = 1009,44 mm`).
* **Pont Thermique Métallique Massif** : Ce couplage serré par les vis CHC M3 DIN 7984 transforme la Traverse (`566,74 g`) et le squelette métallique **Pont de Hanches** (`~978 g` d'Alu 7075/6060 dont `Selle 338,98 g`, `4× Montants 102,84 g` et `2× Brides 404,60 g`) en un **dissipateur thermique massif conductif** (> 1,5 kg d'Alu, conductivité thermique lambda = 130 W/m.K) qui draine les calories loin de la coque cosmétique isolante `Chassis_Structurel_Bassin_Last` (`441,36 g` PA12-CF).

#### B. Aération Passive & Convection Pelvienne (Option A — Standard Atelier)
* **4 Lumières Oblongues de Convection (20 × 8 mm)** : Usinées sur les flasques latéraux et la trappe inférieure du pelvis en PA12-CF, ces ouïes permettent d'établir un tirage thermique naturel par effet de cheminée (air frais aspiré par la trappe basse `ASV1_200_15C`, air chaud refoulé par les lumières latérales hautes).
* **Bilan Température Passive** : Cette circulation d'air abaisse l'échauffement interne de `Delta_T = +60 °C` à **`Delta_T ~ +35 °C`**, maintenant le stator en dessous de 65 °C pour une température ambiante d'atelier de 25 °C à 30 °C.

#### C. Ventilation Forcée Active Optionnelle (Option B — Prédisposition Noctua 5V PWM)
* **Emplacement & Fixation** : Un logement pour micro-ventilateur silencieux **Noctua NF-A3x10** (30 × 30 × 10 mm, alimentation 5V, masse 10 g) est prédisposé sur la trappe d'accès pelvienne inférieure `PEL-14`.
* **Pilotage Thermocontrolé CAN** : Le ventilateur est raccordé sur une sortie PWM 5V du contrôleur et n'est activé que si la télémétrie thermique CAN du RS-06 dépasse le seuil de **`T_stator > 55 °C`**.
* **Bilan Température Active** : En cas de manœuvres dynamiques prolongées de Whole-Body Control, la ventilation forcée stabilise la température stator à **`T_stator < 48 °C`** (Delta_T < +18 °C), garantissant une longévité maximale des aimants néodyme et des roulements.

---

### 5.7 Tableau Récapitulatif des Chanfreins, Fraisures & Ébavurages du Bassin & Waist

L'ensemble des pièces mobiles et fixes du bloc pelvien et de la liaison de taille subit des contraintes combinées élevées (moments de basculement jusqu'à 220 N.m, compression continue de 19,2 kN et passage dynamique du faisceau 48V/CAN-FD). Le respect des chanfreins et ébavurages ci-dessous est **strictement obligatoire** pour garantir la tenue d'assemblage et la sécurité électrique :

| Composant & Zone | Face / Arête Concernée | Type d'Usinage / Outil | Cote Spécifiée | Rôle Mécanique & Justification d'Atelier |
| :--- | :--- | :--- | :---: | :--- |
| **1. Équerres Basses Waist (30×30×3, L = 90 mm)** | Aile Horizontale — Face Supérieure (sous têtes CHC M4 et rondelles DIN 125A) | Fraise à chanfreiner C500 | **`0,3 mm × 45°`** | Assise plane parfaite pour la rondelle plate standard DIN 125A M4 (Ø 9,0 mm, rayon 4,5 mm arrivant à 2,88 mm du bord libre). |
| **1. Équerres Basses Waist (30×30×3, L = 90 mm)** | Aile Horizontale — Face Inférieure (contact plan d'appui Waist Plate) | Fraise à chanfreiner C500 | **`0,3 mm × 45°`** | **Obligatoire** : Élimine le morfil de perçage pour garantir un **contact plan métal-métal franc à 0,0 mm** lors du serrage sandwich 19,2 kN sur la bague intérieure RB8016. |
| **1. Équerres Basses Waist (30×30×3, L = 90 mm)** | Aile Horizontale — Congés d'Angles Extérieurs | Fraise 2 lèvres ou meuleuse | **`R = 5,0 mm`** | Remplace les congés initiaux R = 10 mm pour que la rondelle DIN 125A repose à 100% sur une face plane sans déborder sur la courbure. |
| **1. Équerres Basses Waist (30×30×3, L = 90 mm)** | Aile Verticale — Face Intérieure (contact bilatéral colonne 5 mm) | Fraise à chanfreiner C500 ou outil à main | **`0,3 mm × 45°`** | Placage plan bilatéral sans aucun jour avec les flancs en Alu 7075-T6 de la colonne sagittale basse. |
| **1. Équerres Basses Waist (30×30×3, L = 90 mm)** | Aile Verticale — Face Extérieure (sous têtes CHC M4 et écrous Nylstop) | Fraise à chanfreiner C500 | **`0,3 mm × 45°`** | Portée plane des rondelles DIN 125A M4 sous tête et sous écrou Nylstop M4 (couple 3,0 N.m). |
| **1. Équerres Basses Waist (30×30×3, L = 90 mm)** | 2 Chants Sciés d'Extrémités (L = 90,0 mm) & Arêtes Libres | Lime fine d'ajusteur ou bande abrasive | **`0,5 mm × 45°`** | Élimination des bavures de tronçonnage, sécurité lors des manipulations et protection des câbles environnants. |
| **2. Waist Plate 7075 (176,11 × 173,05 × 9,02 mm)** | Face Supérieure — 4 Perçages Traversants Sandwich Ø 4,50 mm | Fraise à chanfreiner C500 | **`0,3 mm × 45°`** | Assise plane rigoureuse sous les ailes d'équerres basses sans discontinuité ni pont d'effort parasite. |
| **2. Waist Plate 7075 (176,11 × 173,05 × 9,02 mm)** | Face Inférieure — Redan d'Appui Bague Intérieure (+3,00 mm, Ø 80 à Ø 92 mm) | Outil de surfaçage / tournage CNC | **`0,3 mm × 45°`** | Raccordement franc de l'épaulement assurant un contact plan exclusif avec l'acier de la bague intérieure du RB8016. |
| **2. Waist Plate 7075 (176,11 × 173,05 × 9,02 mm)** | Face Inférieure — Débouché des 4 Perçages Traversants Ø 4,50 mm | Fraise à chanfreiner C500 | **`0,3 mm × 45°`** | Ébavurage propre éliminant tout copeau résiduel à proximité immédiate des chemins de roulement. |
| **2. Waist Plate 7075 (176,11 × 173,05 × 9,02 mm)** | Face Inférieure (aile ext. 6,00 mm) — 2 Taraudages Directs M4 Fixation Doigt Mobile *(Mod. CAO prévue avant CNC)* | Foret carbure Ø 3,30 mm + taraud machine M4 × 0,7 | **Zéro lamage / zéro fraisure — Chanfreins `0,2 mm × 45°` (Haut & Bas)** | *(Prévu avant CNC)* Vissage par dessous via 2 vis CHC M4 × 14 mm (`91290A150`) + rondelles (`93475A230`) à `R = 80,50 mm` (`X = +129,73 mm`, zéro saillie face sup. `1042,42`). |
| **2. Waist Plate 7075 (176,11 × 173,05 × 9,02 mm)** | Lumière Concentrique d'Arc Arrière (`125,05°`, `R = 64,75..84,75 mm`, larg. `20,0 mm`) | Fraise de contournage CNC + quart de cercle R1.5 | **Congé continu `R = 1,5 mm` (Haut & Bas)** | **Zéro cisaillement** : Pavillon adouci anti-abrasion préservant `22,24 mm` d'arc libre à `+/- 80°` (faisceau Ø 15 mm). |
| **2. Waist Plate 7075 (176,11 × 173,05 × 9,02 mm)** | Contour Périmétrique Extérieur (176,11 × 173,05 mm) | Fraise de contournage C500 | **`0,5 mm × 45°`** | Cassage d'arête sur tout le pourtour supérieur et inférieur de la plaque. |
| **3. Traverse / Platine d'Interface (Alu 7075-T6, 174,90 × 174,84 × 12,51 mm)** | Face Supérieure — Siège Logement Roulement (Ø 120,00 mm H7, prof. 3,0 mm) | Outil d'alésage circulaire CNC | **Congé fond `R = 0,5 mm` + Entrée `0,5 mm × 45°`** | L'entrée pilote à 45° facilite l'insertion sans forcer de la bague extérieure du CRBH 8016 ; le congé R = 0,5 mm garantit un appui au fond sans talonnage sur le rayon constructeur (r = 1,0 mm). |
| **3. Traverse / Platine d'Interface (Alu 7075-T6, 174,90 × 174,84 × 12,51 mm)** | Face Supérieure — Chambre Dégagement Moyeu (Ø 96,00 mm) & Assise Vis Stator (Z = 1010,93 mm) | Fraise circulaire CNC | **Congé fond `R = 0,3 mm` + Chanfrein `0,3 mm × 45°`** | Dégagement radial franc (+2,24 mm) autour de la collerette tournante (Ø 91,52 mm) et plan d'assise rigoureusement plat pour les têtes basses DIN 7984. |
| **3. Traverse / Platine d'Interface (Alu 7075-T6, 174,90 × 174,84 × 12,51 mm)** | Face Supérieure — 8 Perçages Traversants Fixation Stator RS-06 (Ø 3,50 mm sur PCD Ø 82,00 mm) | Foret carbure Ø 3,50 mm + fraise à lamer plate Ø 6,00 mm | **Lamages cylindriques `Ø 6,00 mm` sur plan Z = 1010,93 mm + Chanfreins `0,2 mm × 45°` (des 2 côtés)** | Assise plane parfaite pour les têtes basses DIN 7984 (Ø 5,5 mm) et débouché franc sans morfil sur la face inférieure d'appui stator (Z = 1007,90 mm). |
| **3. Traverse / Platine d'Interface (Alu 7075-T6, 174,90 × 174,84 × 12,51 mm)** | Alésage Central Traversant (Passage Bossage Rotor RS-06 Ø 52 mm) | Outil d'alésage CNC Ø 74,56 mm | **`0,5 mm × 45°` (Haut & Bas)** | Dégagement très large sans contact (jeu radial 11,28 mm franc). |
| **3. Traverse / Platine d'Interface (Alu 7075-T6, 174,90 × 174,84 × 12,51 mm)** | 4 Perçages Traversants d'Angles Fixation Pelvis / Pont de Hanches (diagonales à 45°, R = 78,67 mm) | Fraise à chanfreiner 90° C500 | **Face sup : Fraisure conique 90° `Ø 10,40 mm × prof. 3,10 mm` (affleurante 0,0 mm)<br>Face inf : Chanfrein `0,3 mm × 45°`** | Noyage rigoureusement à fleur (0,0 mm) des têtes de vis FHC M5 (`M5×18 [92125A213]` sur Pont de Hanches `v42`) : supprime toute surépaisseur sous la Waist Plate tournante et préserve 1,47 mm de pont matière face aux brides. |
| **3. Traverse / Platine d'Interface (Alu 7075-T6, 174,90 × 174,84 × 12,51 mm)** | 4 Taraudages Borgnes M4 Brides Étagées en L (coins à 45° sur PCD Ø 136,00 mm) | Foret carbure Ø 3,30 mm + fraise chanfrein | **Chanfrein entrée `0,4 mm × 45°`** | Évite le refoulement du premier filet taraudé lors du serrage des 4 vis CHC M4 × 16 mm (`92290A154`) des brides (couple 2,8-3,0 N.m). |
| **3. Traverse / Platine d'Interface (Alu 7075-T6, 174,90 × 174,84 × 12,51 mm)** | Face Supérieure — 4 Taraudages Borgnes M4 Butées Fixes (`±109,86°` à `R = 80,50 mm`, contact `±95,0°`, 2 vis / plot) *(Mod. CAO prévue avant CNC)* | Foret carbure Ø 3,30 mm prof. 9,0 mm + taraud machine M4 prof. 8,0 mm | **Chanfrein entrée `0,4 mm × 45°`** | *(Prévu avant CNC)* Logements taraudés M4 (`X = +21,89 mm, Y = +85,07 mm` et `Y = -66,35 mm`, entraxe d = 10,0 mm) pour 4 vis CHC M4 × 14 mm (`91290A150`, couple 2,8 N.m, `Sf_cisaillement > 9`). |
| **3. Traverse / Platine d'Interface (Alu 7075-T6, 174,90 × 174,84 × 12,51 mm)** | Lumière Concentrique d'Arc Arrière (`69,05°`, `R = 64,75..84,75 mm`, larg. `20,0 mm`) | Fraise hélicoïdale CNC + quart de cercle R1.5 | **Congé continu `R = 1,5 mm` (Haut & Bas)** | Fente centrée sur l'axe RS-06 laissant passer les connecteurs XT60/XT90 sans dessoudage ni cisaillement sur `+/- 80°`. |
| **3. Traverse / Platine d'Interface (Alu 7075-T6, 174,90 × 174,84 × 12,51 mm)** | Contour Extérieur Format Pelvis Scalé 1.2776 (174,90 × 174,84 mm × 12,51 mm) | Outil de fraisage / contournage | **`0,8 mm × 45°` (Haut & Bas)** | Élimination des arêtes vives extérieures et finition premium. |
| **4. Moyeu d'Accouplement Sandwich (Alu 7075-T651)** | Fût Cylindrique de Centrage Bague Intérieure (Ø 80,00 mm h6 × hauteur 15,60 mm) | Outil de tournage CNC | **Chanfrein supérieur `0,5 mm × 45°` + Gorge fond `R = 0,3 mm`** | Insertion glissante juste dans l'alésage du roulement sans bavure et contact franc contre la collerette. |
| **4. Moyeu d'Accouplement Sandwich (Alu 7075-T651)** | 4 Taraudages Borgnes M4 Sandwich (PCD Ø 68,00 mm à 45°) | Foret carbure Ø 3,30 mm + fraise chanfrein | **Chanfrein entrée `0,5 mm × 45°`** | Débouche à Ø 4,50 mm, guidant parfaitement les vis CHC M4 × 20 mm sans déformation du plan d'appui. |
| **4. Moyeu d'Accouplement Sandwich (Alu 7075-T651)** | Collerette Annulaire Inférieure (Ø 91,52 mm × 3,0 mm) | Outil de tournage CNC | **`0,4 mm × 45°`** | Contact franc et plan sous la bague intérieure du roulement. |
| **4. Moyeu d'Accouplement Sandwich (Alu 7075-T651)** | Embase Inférieure Raccordement Rotor RS-06 (Ø 65 mm × 5,0 mm) | Foret Ø 3,40 mm + fraise chanfrein | **`0,3 mm × 45°` (des 2 côtés)** | Perçages de passage vis CHC M3 chanfreinés pour fixation directe sur rotor (`91292A113`). |
| **5. Brides Étagées en L de Retenue Axiale (4 brides Alu 7075)** | Épaulement Vertical (H = 13,00 mm) & Assise Inférieure | Fraise 2 lèvres C500 | **Congé d'angle `R = 0,3 mm`** | Épouse rigoureusement la saillie axiale de 13,00 mm du roulement RB8016 au-dessus de la Traverse sans talonnage (`4,12 g`/bride `v42`). |
| **5. Brides Étagées en L de Retenue Axiale (4 brides Alu 7075)** | Bec Supérieur de Pincement (épaisseur 2,00 mm, avancée 4 mm) & Perçage M4 | Fraise d'usinage + foret carbure Ø 4,50 mm | **`0,3 mm × 45°` (toutes arêtes)** | Assise plane sur la face supérieure de la bague extérieure acier (Ø 110 à 120 mm) et passage franc de la vis CHC M4 × 16 mm (`92290A154`). |
| **6. `Bride Epaule v87` Hanches (Liaison Moteurs RS-04 Hip Pitch sur Pont de Hanches)** | Alésage Pilote de Centrage Stator RS-04 (`Ø 97,00 mm H7`) | Fraise circulaire CNC | **`0,5 mm × 45°`** | Emboîtement centré du stator RobStride RS-04 sur les `2× Brides v87` (`202,30 g`/u) du Pont de Hanches. |
| **6. `Bride Epaule v87` Hanches (Liaison Moteurs RS-04 Hip Pitch sur Pont de Hanches)** | 20 Perçages Fixation Stator RS-04 (Ø 4,30 mm — Zone 1 `5 mm` & Zone 2 `18,2 mm`) | Fraise à chanfreiner C500 | **`0,5 mm × 45°` (des 2 côtés)** | Assise plane pour rondelles frein Nord-Lock M4 (`91812A252`, `20` paires hanches) ; respecter la règle borgne `6,0 mm` max en Zone 1 (`M4×12`). |
| **6. Coque Cosmétique `Chassis_Structurel_Bassin_Last` (PA12-CF)** | Ouïes et Orifices Déportés de Faisceaux Membres Inférieurs | Post-traitement / passe-fil | **Passe-fil souple TPU / EPDM** | Routage déporté des câbles 48V et CAN-FD des jambes à travers la coque non porteuse (`441,36 g`, zéro arbre creux). |

---

## 6. Nomenclature Matérielle & Approvisionnement (BOM)

| Repère | Désignation Composant | Spécification Technique | Réf Fournisseur / Standard | Qté | Fonction Mécanique |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **M-04** | **Moteur Waist Yaw** | RobStride RS-06 (36 N.m pic, 11 N.m nom., CAN-FD, arbre plein, `550,97 g` CAO `v42`) | RobStride / RS-06-V1 | 1 | Motorisation active du lacet de taille (Acheté & Monté) |
| **B-01** | **Roulement Principal Waist** | **Roulement à rouleaux croisés CRBH 8016 UU (Ø int 80 mm, Ø ext 120 mm, ép 16 mm, `633,41 g` CAO)** | **CRBH8016 UU / RB8016 UU (AliExpress Luoyang)** | 1 | Reprise intégrale de F_z, F_xy, M_pitch et M_roll (520 N.m) |
| **A-01** | **Traverse / Platine Waist** | **Usinage `Traverse_Renfort_Bassin` Alu 7075-T6 (174,90 × 174,84 × 12,51 mm, bossage inf. -2,49 mm, alésage étagé Ø 74,56 / PCD Ø 82 / Ø 96 / Ø 120 H7, lumière d'arc arrière `69,05°`, 4 taraudages M4 brides ; `[Mod. CAO prévue avant CNC]` : butées M4 à R = 80,50 mm / ±109,86°)** | **Usinage interne CNC C500** | 1 | Siège bague ext. RB8016 + fixation directe stator RS-06 (`Z = 1007,90 mm`) + plateau haut Pont de Hanches (`566,74 g` en CAO `v42`) |
| **HUB-01** | **Moyeu d'Accouplement Sandwich** | **Moyeu CNC tournage/fraisage Alu 7075-T651 (Fût Ø 80 h6 × 15,60 mm avec retrait anti-talonnage 0,38–0,40 mm, collerette Ø 91,52 × 3 mm, embase RS-06, hauteur `23,62 mm`, 4 taraudages borgnes M4 sur PCD Ø 68 mm, `163,94 g` CAO `v42`)** | **Usinage interne CNC C500** | **1** | **Accouplement rotor RS-06 ➔ Waist Plate et pincement sandwich bague intérieure RB8016** |
| **BRIDE-01 à 04** | **Brides Étagées en L** | **4 cavaliers rigides Alu 7075-T6 (H = 15,02 mm, épaulement 13,00 mm, bec 2,00 mm, trou lisse Ø 4,50 mm, `4,12 g`/u soit `16,48 g` les 4 en CAO `v42`)** | **Usinage CNC C500 ou ébauche atelier** | **4** | **Maintien axial positif (+Z) de la bague extérieure du RB8016 sans frottement (entrefer d'air 1,00 mm sous Waist Plate)** |
| **P-01** | **Waist Plate** | Plaque usinée Alu 7075-T6 (176,11 × 173,05 × 9,02 mm, redan +3,0 mm, aile ext. 6,00 mm, lumière d'arc arrière `125,05°`, `433,53 g` CAO `v42` ; `[Mod. CAO prévue]` : 2× M4 doigt à R = 80,50 mm) | Découpe & Usinage CNC C500 | 1 | Fermeture basse torse, portée bague intérieure et passage faisceau sans cisaillement (`433,53 g` réels `v42`) |
| **G-01 / WST-07A** | **Doigt Mobile Butée `±95°`** *(Mod. CAO prévue avant CNC)* | Plot usiné Alu 7075 (`10 × 18 × 8,00 mm`) + `2× CHC M4×14 [91290A150]` + `2× [93475A230]` par dessous | À modéliser en CAO avant CNC | 1 | Ergot mobile de butée mécanique franche côté `+X` (`0°`) à `R = 80,50 mm` (`X = +129,73 mm`, `Y = +9,36 mm`) |
| **BUTEES-01 / WST-07B/C** | **Plots Fixes `±95°` + TPU 95A** *(Mod. CAO prévue avant CNC)* | 2 Plots usinés Alu 7075 (`10 × 18 × 11,50 mm`) + `4× CHC M4 × 14 mm [91290A150]` + 2 capuchons **TPU 95A** (`ép. 3,0 mm`) | À modéliser en CAO avant CNC | 2 | Butées fixes à `±109,86°` sur Traverse à `R = 80,50 mm` (contact effectif à `±95,0°`) |
| **TPU-01** | **Passe-Fil Souple Fendu Faisceau** | Manchon souple fendu TPU 95A / PET gaine tressée pour passage d'arc `69,05° / 125,05°` (`larg. 20,0 mm`) | Impression 3D FDM | 1 | Protection anti-frottement amovible sans dessoudage des connecteurs XT60/XT90 |
| **E-02** | **Équerres Basses Waist** | `Equerre waist` en Aluminium 7075 (30,02 × 30,02 mm, `L = 90,02 mm`, **`42,11 g`/u = `84,22 g` la paire** en CAO `v42`) | Usinage CNC / Cornière 7075 | 2 | Ancrage rigide colonne sagittale 5 mm ➔ Waist Plate & Moyeu 7075 |
| **V-01** | **Vis Pincement Colonne** | Vis CHC M4 × 20 mm Inox 316 (`92290A168`, `10` au total en `v42`) | ISO 4762 / DIN 912 | 4 | Pincement traversant des équerres sur colonne 5 mm (avec écrous Nylstop M4 `93625A150`) |
| **V-02** | **Vis Fixation Waist Plate** | *Supprimé / Intégré dans V-05* | — | 0 | Encastrement direct monolithique assuré par les 4 vis CHC M4 × 20 mm traversantes |
| **V-03** | **Vis Fixation Traverse ➔ Pont de Hanches / Pelvis** | **`4× Vis FHC M5 × 18 mm [92125A213]`** *(Pont de Hanches `v42`)* *(ou `4× FHC M5 × 25 [92125A230]` si coque PA12-CF seule)* | **ISO 10642 / DIN 7991 (`92125A213`)** | **4** | **Fixation affleurante 0,0 mm aux 4 coins de la Traverse (`R = 78,67 mm`) dans les `4× Inserts Hanche Haut`** |
| **V-04** | **Vis Brides Axiales Roulement** | **Vis CHC M4 × 16 mm Inox 316** | **ISO 4762 / DIN 912 (McMaster `92290A154`)** | **4** | **Serrage des 4 brides étagées en L dans les 4 coins de la Traverse sur PCD Ø 136 mm (couple 2,8-3,0 N.m + Loctite 243)** |
| **V-05** | **Vis Serrage Sandwich Waist** | **Vis CHC M4 × 20 mm Inox 316 (`92290A168` en `v42`) ou acier 12.9 (`91290A160`)** | **ISO 4762 / DIN 912** | **4** | **Pincement axial sandwich Équerres (3 mm) + Waist Plate (9 mm) ➔ Moyeu 7075 (couple 2,8-3,0 N.m, L_eng = 9,8 mm)** |
| **V-06** | **Vis Fixation Stator RS-06** | **Vis CHC M3 × 12 mm Tête Basse DIN 7984 Inox 18-8** | **DIN 7984 (McMaster `92855A313`)** | **8** *(1 repère CAO `v42`)* | **Fixation directe du stator RS-06 sur la Traverse sur PCD Ø 82,0 mm (couple 1,3-1,4 N.m, Loctite 243, air gap franc 1,48 mm)** |
| **N-01** | **Écrous Frein Nylstop M4** | Écrous autofreinés bague nylon DIN 985 | ISO 7040 / DIN 985 (McMaster `93625A150`) | 4 | Verrouillage anti-vibrations visserie d'équerres sur colonne (3,0 N.m) |
| **N-02** | **Écrous M5 Pelvis** | **Écrous Nylstop M5 `93625A200`** *(Pont de Hanches `v42`, `6×` sur Selle/Tube)* ou **Hex DIN 934 `90631A113`** *(legacy poches PA12-CF)* | **ISO 7040 / DIN 985 (`93625A200`)** | **6** *(ou 4 hex)* | Bridage M5 Pont de Hanches (`4× M5×35` + `2× M5×80`) ; `FHC M5×18` Traverse vissées directement dans `Inserts Hauts` |
| **W-01** | **Rondelles Plates M4** | Rondelles plates standard DIN 125A M4 (Ø ext 9 mm) | ISO 7089 / DIN 125A (McMaster `93475A230`) | 16 | 8 rondelles sur colonne + 4 rondelles sous têtes CHC M4 sandwich + 4 rondelles sous têtes vis de brides |
| **W-02** | **Rondelles Plates M5** | Rondelles plates standard DIN 125A M5 (Ø ext 10,0 mm, ép 1,0 mm) | ISO 7089 / DIN 125A (McMaster `93475A240`) | 16 | `16` rondelles sur Pont de Hanches `v42` (`Selle`, `Inserts Bas`, `Tube 60x60`) + `4` sous écrous si coque PA12-CF |
| **D-01** | **Brut Platine / Traverse Waist** | **Plaque carrée 200 × 200 × 15 mm Alu 7075-T651** | **Blockenstock (~25-30 EUR TTC)** | **1** | **Brut d'usinage C500 pour Traverse_Renfort_Bassin (couvre les 174,90 × 174,84 × 12,51 mm finis)** |
| **D-02** | **Brut Waist Plate** | **Plaque carrée 200 × 200 × 12 mm Alu 7075-T651** | **Blockenstock (~20-25 EUR TTC)** | **1** | **Brut d'usinage C500 pour Waist_Plate_7075 (couvre les 176,11 × 173,05 × 9,02 mm finis)** |
| **D-03** | **Rond Brut Moyeu Sandwich** | **Barre ronde Ø 100 × 35 mm Alu 7075-T651** | **Blockenstock (~10-12 EUR TTC)** | **1** | **Brut de tournage/fraisage pour Moyeu d'Accouplement Waist** |

---

## 7. Recommandations de Modélisation CAO Fusion 360

![Vue Éclatée, Découplage Bicolore et Guide CAO Fusion 360 Waist](./media/schema_empilement_eclate_et_cinematique_waist.svg)

*Guide d'ingénierie visuel officiel (D-Bot V1.2) : Panneau 1 — Vue éclatée axiale verticale Z (lévitation des 6 étages). Panneau 2 — Schéma fonctionnel bicolore (Bleu = Bâti fixe bassin, Orange = Équipage mobile torse, Vert = Entrefer d'air franc de 1.5 mm). Panneau 3 — Recette de modélisation CAO pas-à-pas sous Autodesk Fusion 360 (4 corps simples et 3 liaisons Joints).*

### 7.1 Import Direct du Modèle 3D CAO du Roulement (Méthode Recommandée Fusion 360)

Pour intégrer le roulement **RB8016** (ou **CRBH8016**) dans l'assemblage sans avoir à redessiner les rouleaux et chemins de roulement internes, il est fortement recommandé d'insérer directement le composant 3D STEP normalisé via la bibliothèque intégrée à Autodesk Fusion 360 :

1. **Accès au Menu Intégré** :
   - Dans le ruban supérieur de l'espace de travail **Conception** (*Design*), cliquer sur le menu déroulant **Insérer** (*Insert*).
   - Sélectionner **Contenu du fabricant** (*Manufacturer Part Content*) ou l'icône de catalogue de composants partenaires (**PartCommunity / TraceParts**).
2. **Recherche de la Référence Normalisée** :
   - Dans la barre de recherche du catalogue intégré, taper la désignation normalisée : `RB8016` ou `RB 8016 UU` (ou alternativement `CRBH8016`).
   - Sélectionner le modèle standard (fabricant THK, IKO ou générique Luoyang / Cadenas, cotes 80 × 120 × 16 mm).
3. **Téléchargement & Insertion Directe dans l'Assemblage** :
   - Choisir le format d'export : **3D STEP (.stp)** ou **Autodesk Fusion 360 (.f3d)**.
   - Cliquer sur **Insérer directement dans le design** (*Insert into current design*).
   - Le composant 3D s'ajoute automatiquement dans l'arborescence du projet, avec ses surfaces cylindriques et arêtes d'appui immédiatement prêtes pour l'application des contraintes d'assemblage (*Joints* / *Rigid* / *Revolute*).

> [!TIP]
> **Alternative Hors Ligne / Glisser-Déposer** :
> Si la bibliothèque en ligne Autodesk est indisponible, télécharger directement le fichier STEP `RB8016UU` depuis la bibliothèque **THK CAD Data Library** ([thk.com](https://www.thk.com)) ou **TraceParts**, puis le glisser-déposer (*Drag & Drop*) dans le panneau de données (*Data Panel*) de Fusion 360.

### 7.2 Procédure de Modélisation & Assemblage Sous Fusion 360

![Plans d'Usinage et Cotation 2D Fusion 360 — Waist Yaw](./media/schema_cao_assemblage_waist_rs06_fusion360.svg)

*Blueprint vectoriel d'ingénierie officiel pour les cotes d'usinage et esquisses CAO : Coupe axiale Z-X cotée, chronologie d'atelier, esquisse cotée de la Waist Plate et esquisse cotée de la Traverse.*

1. **Insertion du Pelvis & Scale 3D dans Fusion 360** :
   - Créer un composant maître `[02_Bassin_Pelvis]` distinct du composant `[01_Torse]`.
   - Importer le composant pelvien dérivé d'Asimov v1 et lui appliquer la commande **Scale** avec le **facteur d'échelle uniforme `1,2776`** sur tous les axes (X, Y, Z) depuis son point d'origine, atteignant une envergure hanches de **`487,09 mm`** et un encombrement de `233,17 × 487,08 × 312,80 mm`.
2. **Modélisation de la Waist Plate Élargie (`Waist_Plate_7075`, `433,53 g` en `v42`)** :
   - Format extérieur : `176,11 × 173,05 mm`, épaisseur totale `9,02 mm` en Alu 7075-T6 (`Z = [1033,41 ; 1042,43 mm]`).
   - **Face inférieure — Redan d'appui bague intérieure** : Redan circulaire de saillie **`+3,00 mm`** entre Ø 80,0 mm et Ø 89,62 mm (appui sur bague intérieure Ø 80–95 mm). Le reste de la face au-delà de Ø 95,0 mm est laissé en retrait de 3,0 mm (`1,00 mm` d'entrefer au-dessus des 4 brides `Z_max = 1035,41 mm`).
   - **Zone postérieure — Lumière concentrique d'arc de câblage (`125,05°`)** : Fente d'arc `R = 64,75..84,75 mm`, largeur `20,0 mm`, centrée à `X = +49,23 mm, Y = +9,36 mm`, congés `R = 1,5 mm`.
   - **Face inférieure — Logement doigt de butée mobile (`0°` côté `+X`) *(Modification CAO prévue avant usinage CNC)*** : À ajouter sous l'aile externe (`6,00 mm`) de la Waist Plate à `R = 80,50 mm` (`X = +129,73 mm, Y = +9,36 mm`, 2× taraudages directs M4 sans lamage).
   - **Interface de fixation du Plastron Ventral (`Plastron_Ventral_Torse`)** : 4 vis `CHC M4 × 18 [92290A161]` à l'avant/latéral (`16,0 mm` d'entrefer libre sous la Waist Plate, hors cylindre des brides `R_max = 79,52 mm`).
3. **Usinage in-situ de la Traverse / Platine d'Interface (`Traverse_Renfort_Bassin`, `566,74 g` en `v42`)** :
   - Format extérieur : `174,90 × 174,84 mm` × `10,02 mm` d'épaisseur périphérique, `12,51 mm` au centre (Alu 7075-T6, `Z = [1007,90 ; 1020,41 mm]`).
   - Bossage inférieur central : extrusion cylindrique descendante de `2,49 mm` assurant le contact franc sur le stator RS-06 (`Z = 1007,90–1009,44 mm`).
   - Siège roulement face supérieure : **Ø 120,00 mm H7**, profondeur `3,00 mm` (`Z = [1017,41 ; 1020,41 mm]`).
   - Chambre intermédiaire de dégagement moyeu : **Ø 96,00 mm** procurant `2,24 mm` de jeu radial pour la collerette tournante (Ø 91,52 mm) du `Moyeu_Waist_Sandwich_7075`.
   - Fixation stator RS-06 (`Z = 1010,93 mm`) : 8 trous traversants **Ø 3,50 mm** sur PCD **`Ø 82,00 mm`** avec lamages **Ø 6,00 mm** pour vis CHC M3 × 12 mm Tête Basse DIN 7984 (`92855A313`). Entrefer axial `1,48 mm` sous la collerette du moyeu.
   - Alésage central traversant de passage rotor : **Ø 74,56 mm** laissant `11,28 mm` de jeu radial.
   - 4 perçages d'angles à 45° (`R = 78,67 mm`) avec fraisures coniques 90° (Ø 10,40 × 3,10 mm) pour **`4× FHC M5 × 18 [92125A213]`** dans les `4× Inserts Hanche Haut` du Pont de Hanches.
   - 4 taraudages M4 de brides étagées en L sur PCD **`Ø 136,00 mm`**.
   - Lumière concentrique d'arc arrière (`69,05°`, `R = 64,75..84,75 mm`, larg. `20,0 mm`) centrée sur RS-06 avec congés `R = 1,5 mm`.
   - **Butées fixes (`±109,86°` à `R = 80,50 mm` pour contact `±95,0°`)** : ***[Modification CAO prévue avant usinage CNC]*** 2 emplacements à `+109,86°` (`X = +21,89 mm`, `Y = +85,07 mm`) et `-109,86°` (`X = +21,89 mm`, `Y = -66,35 mm`).
4. **Modélisation & Insertion des 4 Brides Étagées en L (`Bride_Retenue_RB8016_L`, `4,12 g`/u en `v42`)** :
   - Encombrement unitaire **`16,00 × 15,00 × 15,00 mm`** (`21,95 × 21,95 × 15,02 mm` en boîte AABB orientée à 45° sur `Z = [1020,39 ; 1035,41 mm]`, `R_max_reel ~ 72,4 mm`).
   - 4 brides répétées à 45°, 135°, 225°, 315° et fixées par `4× CHC M4 × 16 mm [92290A154]` + `4× [93475A230]`.
5. **Modélisation du Système de Butée Mécanique (`+/- 95,0°`) *(Modification CAO prévue avant usinage CNC)*** :
   - Ajout à effectuer avant usinage C500 : doigt mobile `WST-07A` (`10 × 18 × 8,00 mm`, vissé par dessous à `X = +129,73 mm, Y = +9,36 mm`) et 2 plots fixes `WST-07B` Alu 7075 (`10 × 18 × 11,50 mm`, `4× CHC M4×14 [91290A150]`) coiffés de capuchons **TPU 95A** (`ép. 3,0 mm`) sur Traverse à `R = 80,50 mm` (`±109,86°`).
6. **Définition de la Liaison Pivot (Revolute Joint)** :
   - **Origine du Joint** : Centre géométrique de l'axe de rotation du roulement (`X = +49,23 mm`, `Y = +9,36 mm`, plan d'appui Z).
   - **Axe de Rotation** : Axe `Z` global (Yaw).
   - **Limites Angulaires logicielles (Joint Limits)** : Définir un débattement nominal de **`-90,0°` à `+90,0°`** (la butée physique intervenant à `+/- 95,0°`).
7. **Contrôle d'Interférence Statique & Dynamique** :
   - Exécuter la fonction `Interference Detection` entre la Waist Plate en rotation (+/- 45°) et les carters des deux moteurs **RS-04 Hip Pitch** du bassin, ainsi qu'entre le dessous de la plaque et le dessus des 4 brides (maintien de l'entrefer d'air franc de 1,00 mm).
   - Vérifier le jeu radial franc de `>= +3,10 mm` (`R_int = 75,50 mm` vs `R_max_reel ~ 72,4 mm` des brides) et la garde d'air de `+3,21 mm` sous les têtes de vis du doigt sur toute la plage `+/- 95,0°`.
8. **Export URDF / Isaac Gym** :
   - Nom du joint dans l'URDF officiel : `waist_yaw_joint`.
   - Limites URDF associées : `lower="-1.5708"`, `upper="1.5708"`, `effort="36.0"`, `velocity="31.4"`.

### 7.3 Modélisation du Moyeu d'Accouplement & Pincement Sandwich (Alu 7075-T6)

![Plan Coté du Moyeu d'Accouplement et Pincement Sandwich Waist](./media/schema_moyeu_accouplement_waist_sandwich_rs06.svg)

*Blueprint vectoriel d'ingénierie officiel du Moyeu d'Accouplement Waist (D-Bot V1.2) :*
- **Panneau 1 (Coupe Axiale Z Assemblée)** : Détaillant la prise en étau (sandwich) continue de la bague intérieure de 16,0 mm du RB8016 entre le redan inférieur de la Waist Plate (+3,0 mm) et la collerette du Moyeu (Ø 91,5 mm × 3 mm), le serrage direct par les 4 vis CHC M4 × 20 mm supérieures traversant les ailes des équerres basses (3 mm) et la Waist Plate (9 mm), l'entrefer de précharge anti-talonnage de 0,40 mm entre le fût du moyeu et la Waist Plate (garantissant 100% du serrage sur l'acier du roulement), et l'entrefer d'air de protection de 2,0 mm au-dessus du stator fixe.
- **Panneau 2 (Plan Coté 2D de Fabrication CNC)** : Fût cylindrique de centrage Ø 80,00 mm tolérance h6 (+0,000 / -0,019 mm) de hauteur 15,60 mm (retrait mesuré `0,38 mm` sous bague en `v42`), collerette inférieure Ø 91,52 mm, embase de fixation rotor RS-06 Ø 65,00 mm, hauteur totale `23,62 mm` (`163,94 g` CAO `v42`) et dégagement d'outil.
- **Panneau 3 (Vue de Dessus Cotée & Implantation des 4 Trous M4)** : Cartographie des 4 trous borgnes taraudés M4 sur le diamètre primitif PCD Ø 68,00 mm (rayon R = 34,00 mm) orientés à 45,0°, avec leurs coordonnées cartésiennes sagittales/latérales exactes `X = +/- 24,04 mm` et `Y = +/- 24,04 mm`.

#### Spécifications & Rôle de la Pièce :
1. **Double Fonction Clé** : Cette pièce monobloc usinée en tournage/fraisage CNC résout simultanément :
   - Le raccordement mécanique avec la face supérieure affleurante du rotor RobStride RS-06 (qui se situe sous le roulement).
   - Le verrouillage axial bidirectionnel de la bague intérieure du roulement RB8016 (22 kN en traction et compression).
2. **Pincement de la Bague Intérieure (Prise en Sandwich)** :
   - Par le dessus : Les ailes horizontales des 2 équerres basses (3,0 mm) posées sur la face supérieure de la Waist Plate (redan inférieur +3,0 mm en contact exclusif avec la bague intérieure Ø 80 à Ø 92 mm).
   - Par le dessous : La collerette annulaire Ø 91,5 mm × 3,0 mm du Moyeu.
   - Sommet du fût : Usiné à **`15,60 mm`** de hauteur, ménageant un **entrefer d'air de précharge de `0,40 mm`** sous la Waist Plate.
   - Serrage : 4 vis CHC M4 × 20 mm traversant les équerres et la Waist Plate viennent se visser dans les 4 taraudages borgnes M4 (prof. 12 mm, filet 10 mm sur PCD Ø 68,0 mm) du Moyeu (prise filetée 9,8 mm).
3. **Transmission du Couple Moteur (36 N.m)** :
   - L'embase inférieure Ø 65 mm descend sous le roulement et se boulonne directement sur les perçages d'origine du rotor RS-06.
   - Un jeu d'air protecteur franc de **2,0 mm** est préservé entre le moyeu tournant et le carter extérieur fixe du stator.

---

### 7.4 Tableau des Références McMaster-Carr pour Modélisation CAO Fusion 360 (Bassin & Waist)

Pour modéliser avec une fidélité géométrique absolue l'ensemble du module Pelvis & Waist dans Autodesk Fusion 360, insérer directement les modèles 3D STEP normalisés via le menu **Insérer** (`Insert`) ➔ **Insert McMaster-Carr Component** :

| Sous-Ensemble & Rôle Mécanique | Composant Normalisé | Norme / Standard | Réf Catalogue McMaster | Quantité (Module Bassin) | Spécifications d'Usinage & Diamètres de Perçage Associés |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **1. LIAISON SANDWICH WAIST YAW (ÉQUERRES ➔ WAIST PLATE ➔ MOYEU 7075)** | | | | | |
| • **Serrage Sandwich Continu (Bague Intérieure RB8016)** | Vis CHC M4 × 20 mm | ISO 4762 / DIN 912 | **`92290A168`** *(Inox 316, CAO `v42`)*<br>**`91290A160`** *(Acier 12.9)* | **4 vis** (2 / équerre) | **Perçage lisse traversant Ø 4,50 mm** chanfreiné à **`0,3 mm × 45°`** traversant Équerres (3 mm) et Waist Plate (9 mm). Vissage dans 4 taraudages borgnes Moyeu 7075 (avant-trou **Ø 3,30 mm** prof. 12 mm, taraudage M4×0,7 prof. utile 10 mm sur PCD Ø 68,0 mm à 45°). Prise filetée = **`9,80 mm`**, couple 2,8 à 3,0 N.m + Loctite 243. |
| • **Rondelles d'Appui Ailes Équerres Waist** | Rondelles Plates M4 DIN 125A | ISO 7089 / DIN 125A | **`93475A230`** (Inox 18-8) | **4 rondelles** | **Diamètre de passage Ø 4,30 mm**. Dimensions : Ø intérieur 4,3 mm / Ø extérieur 9,0 mm / épaisseur 0,8 mm. Portée plane à 100 % sur l'aile d'équerre (congé d'angle R = 5,0 mm, garde au bord = 2,88 mm). |
| **2. PINCEMENT SAGITTAL COLONNE VERTÉBRALE BASSE** | | | | | |
| • **Pincement Flanc Équerres ➔ Colonne 5 mm** | Vis CHC M4 × 20 mm | ISO 4762 / DIN 912 | **`92290A168`** *(Inox 316, CAO `v42`)*<br>**`91290A160`** *(Acier 12.9)* | **4 vis** traversantes | **Perçages lisses traversants Ø 4,30 mm** coaxiaux dans Équerre G (3 mm) + Colonne (5 mm) + Équerre D (3 mm) = 11 mm. Entraxes réguliers 18,0 mm (54 mm total). |
| • **Rondelles Pincement Colonne Basse** | Rondelles Plates M4 DIN 125A | ISO 7089 / DIN 125A | **`93475A230`** (Inox 18-8) | **8 rondelles** (4 sous tête, 4 sous écrou) | **Diamètre de passage Ø 4,30 mm**. Dimensions : Ø intérieur 4,3 mm / Ø extérieur 9,0 mm / épaisseur 0,8 mm. |
| • **Écrous de Verrouillage Colonne Basse** | Écrous Frein Nylstop M4 | ISO 7040 / DIN 985 | **`93625A150`** (Inox 18-8)<br>**`94645A101`** (Acier Cl.10) | **4 écrous** | Bague nylon autofreinée indesserrable aux vibrations (couple nominal 3,0 N.m), montés sur vis traversantes **Ø 4,30 mm**. |
| **3. FIXATION TRAVERSE / PLATINE D'INTERFACE ➔ PONT DE HANCHES (`v42`) & RS-06** | | | | | |
| • **Fixation Coins Traverse ➔ Inserts Hauts (`Pont de Hanches v42`)** | **Vis FHC M5 × 18 mm** *(Pont de Hanches `v42`)*<br>*(Alt. FHC M5 × 25 si coque PA12-CF seule)* | ISO 10642 / DIN 7991 | **`92125A213`** *(Inox 18-8 M5×18, CAO `v42`)*<br>*(Alt. `92125A230` M5×25 Inox 316)* | **4 vis** (diagonales à 45°) | **Perçages lisses Ø 5,30 mm** avec **fraisure conique 90° Ø 10,40 mm × profondeur 3,10 mm** sur face supérieure de Traverse (`R = 78,67 mm`, affleurantes à 0,0 mm). Vissées directement dans les `4× Inserts Hanche Haut [ASV1_200_13]`. |
| • **Fixation Stator RS-06 ➔ Traverse (Option 1 Validée)** | Vis CHC M3 × 12 mm Tête Basse | DIN 7984 | **`92855A313`** (Inox 18-8) | **8 vis** *(1 repère `v42`)* | **8 perçages traversants lisses Ø 3,50 mm** sur PCD **`Ø 82,00 mm`** avec **lamages cylindriques Ø 6,00 mm** sur `Z = 1010,93 mm`. Air gap **`1,48 mm`** sous collerette Moyeu. Serrage **`1,3 à 1,4 N.m`** + Loctite 243. |
| • **Rondelles d'Appui Pont de Hanches / Pelvis** | Rondelles Plates M5 DIN 125A | ISO 7089 / DIN 125A | **`93475A240`** (Inox 18-8) | **16** *(Pont de Hanches)*<br>*(+4 si poches PA12-CF)* | **Diamètre de passage Ø 5,30 mm** (Ø ext 10,0 mm). Sur `4× M5×35 [91290A661]`, `4× M5×20 [92290A242]` et `2× M5×80 [91290A276]` du Pont de Hanches `v42`. |
| • **Écrous M5 Pont de Hanches (et Poches PA12-CF)** | **Écrous Frein Nylstop M5** *(Pont de Hanches)* / Hex DIN 934 *(poches)* | ISO 7040 / DIN 985 | **`93625A200`** *(Nylstop M5 `v42`, 6×)*<br>*(Alt. `90631A113` hex DIN 934 si poches PA12-CF)* | **6 écrous** | Verrouillage des `4× M5×35 [91290A661]` (`Selle`) et `2× M5×80 [91290A276]` (`Tube 60×60` + `Brides`). |
| **4. RETENUE AXIALE ROULEMENT CRBH 8016 (4 BRIDES ÉTAGÉES EN L 16 × 15 × 15 mm)** | | | | | |
| • **Fixation des 4 Brides en L sur la Traverse** | Vis CHC M4 × 16 mm | ISO 4762 / DIN 912 | **`92290A154`** (Inox 316, CAO `v42`)<br>**`91290A154`** (Acier 12.9) | **4 vis** (coins à 45°) | **Perçages lisses traversants Ø 4,50 mm** centrés à `X = +8,00 mm`. Vissage dans 4 taraudages borgnes M4 de la Traverse sur PCD **Ø 136,00 mm** (couple 2,8 à 3,0 N.m + Loctite 243). |
| • **Rondelles d'Appui Vis de Brides** | Rondelles Plates M4 DIN 125A | ISO 7089 / DIN 125A | **`93475A230`** (Inox 18-8) | **4 rondelles** | **Diamètre de passage Ø 4,30 mm**. Sous têtes CHC M4 des brides. |
| **5. BUTÉE MÉCANIQUE ANGULAIRE DE TAILLE (+/- 95,0°) — *(Mod. CAO prévue avant usinage CNC)*** | | | | | |
| • **Doigt Mobile sous Waist Plate (`WST-07A`)** *(Mod. CAO prévue)* | Plot 7075 (`10,0×18,0×8,00 mm`) + `2× CHC M4 × 14 mm` + `2× DIN 125A M4` | ISO 4762 / DIN 125A | **`91290A150`** *(2× CHC M4×14)*<br>+ **`93475A230`** *(2× DIN 125A)* | **1 ensemble** | *(Prévu avant CNC)* Implanté à `R = 80,50 mm` à `0°` (`+X` Avant : `[+129,73 ; +9,36 mm]`) sous aile ext. `6,00 mm` de la Waist Plate. Vissé **par dessous** dans taraudages M4 (prise `5,20 mm`, zéro dépassement sous Plastron). |
| • **Butées Fixes sur Traverse (`WST-07B/C`, +/- 95,0°)** *(Mod. CAO prévue)* | 2 Plots 7075 (`10,0×18,0×11,50 mm`) + `4× CHC M4 × 14 mm` + 2× Capuchons TPU 95A | ISO 4762 / TPU 95A | **`91290A150`** *(4× CHC M4×14)*<br>+ `TPU 95A` *(impression 3D, 3,00 mm)* | **2 plots / 4 vis** | *(Prévu avant CNC)* Vissés par dessus (lamage `Ø 7,5×5,5`) sur 2×2 taraudages borgnes M4 (`prof. 9 mm`, prise `8,00 mm`) de la Traverse à `R = 80,50 mm` / `±109,86°` (face choc `±101,38°` : Gauche `[+21,89 ; +85,07]`, Droit `[+21,89 ; -66,35 mm]`). Couple `2,8 N.m`. |
| **6. ACCOUPLEMENT ROTOR ROBSTRIDE RS-06 ➔ EMBASE MOYEU 7075** | | | | | |
| • **Boulonnerie Rotor RS-06 ➔ Embase Moyeu** | Vis CHC M3 × 10 mm | ISO 4762 / DIN 912 | **`91292A113`** (Inox 18-8, repère `v42`) | **4 à 6 vis** *(1 repère `v42`)* | **Perçages lisses traversants Ø 3,40 mm** traversant l'embase moyeu (ép. 5,0 mm). Vissage direct dans rotor RS-06 (couple 1,3–1,4 N.m + Loctite 243). |
| **7. FIXATION DES MOTEURS DE HANCHES RS-04 HIP PITCH ➔ BRIDES `v87` HANCHES (`Torse-123 v42`)** | | | | | |
| • **Fixation Stator RS-04 Hip Pitch ➔ Brides `v87` Hanches (`Torse-123 v42`)** | Vis CHC M4 × 16 mm (Zone 1 `5 mm`) + CHC M4 × 25 mm Tête Basse (Zone 2 `18,2 mm`) | ISO 4762 / DIN 7984 | **`90128A214`** (`8×` M4×16 repères `v42` — *utiliser **`91290A154` M4×12** en atelier, prof. borgne 6 mm max !*)<br>**`92855A422`** (`12×` M4×25 TB) | **20 vis** (10 / hanche) | **Perçages lisses traversants Ø 4,30 mm** sur `2× Bride Epaule v87` (`202,30 g`/u) du Pont de Hanches. Vigilance stricte sur les 4 vis Zone 1 : 6,0 mm max taraudage stator RS-04. |
| • **Sécurité Anti-Vibrations Stators Hanches** | Rondelles Frein Nord-Lock M4 (NL4) | Spécification Nord-Lock | **`91812A252`** *(CAO `v42`)*<br>*(Alt. `92620A203`)* | **20 paires** (10 / hanche) | **Diamètre de passage Ø 4,30 mm**. Rondelles à cames appariées NL4 sous toutes les têtes de vis RS-04. |

---

### 7.5 Tableau Synthétique des Couples Dynamométriques & Outillage d'Atelier (Bassin & Waist)

Tous les serrages d'assemblage du module Pelvis & Waist doivent être rigoureusement effectués à la clé dynamométrique étalonnée selon les valeurs ci-dessous :

| Liaison Mécanique & Composant | Filetage & Type de Vis | Norme & Réf McMaster | Couple Dynamométrique | Outillage Recommandé | Freinage & Recommandations |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Fixation Stator RS-06 ➔ Traverse (Option 1 Validée)** | **M3 × 12 mm Tête Basse** | **DIN 7984 (`92855A313`)** | **`1,3 à 1,4 N.m`** | Clé Allen 2,0 mm | **Loctite 243 (Bleu)** — Entrefer 1,48 mm franc sous moyeu tournant |
| **Accouplement Rotor RS-06 ➔ Embase Moyeu 7075** | M3 × 10 mm CHC | ISO 4762 (`91292A113`) | **`1,3 à 1,4 N.m`** | Clé Allen 2,5 mm | **Loctite 243 (Bleu)** — Serrage en étoile |
| **Serrage Sandwich Continu (Waist Plate ➔ Moyeu 7075)** | M4 × 20 mm CHC | ISO 4762 (`92290A168` / `91290A160`) | **`2,8 à 3,0 N.m`** | Clé Allen 3,0 mm | **Loctite 243 (Bleu)** — Pincement 19,2 kN bague int. RB8016 |
| **Fixation des 4 Brides en L ➔ Traverse** | M4 × 16 mm CHC | ISO 4762 (`92290A154`) | **`2,8 à 3,0 N.m`** | Clé Allen 3,0 mm | **Loctite 243 (Bleu)** + Rondelle DIN 125A M4 (`93475A230`) |
| **Fixation Doigt + 2 Plots Butées (+/- 95,0°)** *(Mod. CAO prévue)* | M4 × 14 mm CHC (`×6`) + `2×` DIN 125A M4 | ISO 4762 (`91290A150`) / `93475A230` | **`2,8 N.m`** | Clé Allen 3,0 mm | **Loctite 243 (Bleu)** — Capuchons amortisseurs TPU 95A (ép. choc `3,00 mm`) |
| **Pincement Équerres Waist ➔ Colonne 5 mm** | M4 × 20 mm CHC | ISO 4762 (`92290A168` / `91290A160`) | **`3,0 N.m`** | Clé Allen 3,0 mm + Clé 7 | **Écrous Nylstop M4 (`93625A150`)** |
| **Fixation Coins Traverse ➔ Inserts Hauts (`Pont de Hanches v42`)** | M5 × 18 mm FHC 90° | ISO 10642 (`92125A213`) | **`4,5 à 5,0 N.m`** *(alu)* / **`1,8–2,0 N.m`** *(si PA12-CF)* | Clé Allen 3,0 mm | **Loctite 243 (Bleu)** dans `4× Inserts Hanche Haut` (ou `92125A230` + `90631A113` si PA12-CF) |
| **Fixation Stators RS-04 Hanche ➔ Brides `v87` Hanches (`v42`)** | Zone 1 : M4 × 12 mm (`91290A154` atelier vs `90128A214` CAO)<br>Zone 2 : M4 × 25 TB (`92855A422`) | ISO 4762 / DIN 7984 | **`3,0 N.m`** | Clé Allen 3,0 / 2,5 mm | **Rondelles Nord-Lock M4 (`91812A252`)** *(prof. borgne 6,0 mm max en Zone 1)* |

---

## 8. Checklist de Contrôle & Métrologie Avant Usinage C500

- [x] **Roulement RB8016 UU (EFANT Luoyang) reçu et contrôlé en atelier** (Rapport d'inspection EFANT N° 01 du 15/09/2026 : d = 79,996 mm, D = 119,995 mm, B = 15,965 mm, faux-rond radial/axial de 0,003 mm / 3 µm — Classe de précision P4/P2).
- [x] **Modèle CAO `Torse-123 v42` audité et synchronisé (`SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md`)** :
  - Format élargi `Waist_Plate_7075` (`176,11 × 173,05 × 9,02 mm`, `433,53 g`, redan `+3,00 mm`, lumière d'arc `125,05°`), `Traverse_Renfort_Bassin` (`174,90 × 174,84 × 12,51 mm`, `566,74 g`, lumière d'arc `69,05°`), `Moyeu_Waist_Sandwich_7075` (`23,62 mm`, `163,94 g`, jeu anti-talonnage `0,38 mm`), `4× Bride_Retenue_RB8016_L` (`4,12 g`/u, jeu `1,00 mm`), et squelette **Pont de Hanches** (`Tube 60×60 L = 46,33 mm`, `Selle 338,98 g`, `4× Montants 20×20`, `8× Inserts`, `2× Brides v87`) modélisés en CAO.
- [ ] **Actions CAO à finaliser avant usinage CNC C500 & commandes complémentaires** :
  - **Modification CAO prévue avant usinage CNC — Butée mécanique côté avant `+X` (`+/- 95,0°` à `R = 80,50 mm`)** : ajouter sous `Waist_Plate_7075` le doigt mobile `WST-07A` à `0°` (`+X` : `X = +129,73 mm, Y = +9,36 mm`) et sur `Traverse_Renfort_Bassin` les 2 plots fixes `WST-07B/C` à `±109,86°` (face choc `±101,38°` : Gauche `[+21,89 ; +85,07 mm]`, Droit `[+21,89 ; -66,35 mm]`).
  - **8 occurrences externes de hanches `ASV1_200` (`Support_Hanche`, `Liaison_Hanche`, `Capot_Lateral`, `Capot_Protection_Frontal` G/D)** : finaliser côté CAO (actuellement *en cours de définition, non définitives*) puis calibrer les densités PA12-CF restantes (20 corps actuellement à `rho = 1,015 g/cm3`).
  - **Zone 1 Brides `v87` Hanches (`RS-04`)** : remplacer en atelier/CAO les `8× M4×16 [90128A214]` par **`CHC M4×12 [91290A154]`** pour respecter la profondeur borgne `6,0 mm` max du carter stator RS-04.
- [ ] **Bruts commandés (Blockenstock)** :
  - Plaque carrée Alu 7075-T651 200 × 200 × 15 mm (`Traverse_Renfort_Bassin` 174,90 × 174,84 × 12,51 mm).
  - Plaque carrée Alu 7075-T651 200 × 200 × 12 mm (`Waist_Plate_7075` 176,11 × 173,05 × 9,02 mm).
  - Barre ronde Alu 7075-T651 Ø 100 × 35 mm (`Moyeu_Waist_Sandwich_7075`) + barre/plat pour `Selle de Pont` (`140 × 145 × 22 mm`).
- [ ] **Visserie complète vérifiée & commandée** :
  - 8 vis CHC M3 × 12 mm Tête Basse DIN 7984 Inox 18-8 (`92855A313`) pour fixation directe stator RS-06 sur la Traverse (`1` repère CAO `v42`, `8` réelles requises).
  - 8 vis CHC M4 × 20 mm (`92290A168` Inox 316 ou `91290A160` 12.9) + 12 rondelles DIN 125A M4 (`93475A230`) + 4 Nylstop M4 (`93625A150`) pour sandwich Moyeu & pincement Équerres Waist.
  - 4 vis CHC M4 × 16 mm (`92290A154`) + 4 rondelles M4 (`93475A230`) pour les 4 brides étagées en L.
  - Squelette « Pont de Hanches » (`Torse-123 v42`) : `4× FHC M5×18 [92125A213]`, `4× CHC M5×20 [92290A242]`, `4× CHC M5×35 [91290A661]`, `2× CHC M5×80 [91290A276]`, `6× Nylstop M5 [93625A200]`, `16× Rondelles M5 [93475A240]`, `8× CHC M4×25 [91292A122]`, `8× Nylstop M4 [93625A150]`.
  - *(Après ajout CAO butées +/- 95,0°)* : `6× CHC M4×14 [91290A150]` + `2× rondelles DIN 125A M4 [93475A230]` + `2× capuchons TPU 95A` (impression 3D sur mesure, ép. choc `3,00 mm`).
  - 1 tube frein-filet normal Loctite 243 (bleu).
- [ ] **Métrologie & Alésage C500 du Roulement** : Palpage au Touch Probe 3D C500 du CRBH 8016 réceptionné et usinage du siège Ø 120 H7 par passes d'approche successives (*Match Machining* direct sur table, ajustement H7/h6 glissant juste).
- [x] **Pied à coulisse numérique de précision acquis** : SHAHE 5110-150 (0-150 mm, IP54, acier inoxydable trempé, règle en verre, résolution 0,01 mm).
- [ ] **Contrôle final sur table d'assemblage (interférences & boucle câble)** : Vérifier la garde `+/- 80°` dans les lumières d'arc arrière (`69,05° / 125,05°`, recouvrement libre `22,24 mm` à `+/- 80°`) avec faisceau `Ø 15 mm` et boucle de service `L = 160 mm` (`<= 0,50° / mm`).

---
*Fin du Dossier Technique — Validé pour modélisation CAO et fabrication atelier D-Bot V1.x.*
