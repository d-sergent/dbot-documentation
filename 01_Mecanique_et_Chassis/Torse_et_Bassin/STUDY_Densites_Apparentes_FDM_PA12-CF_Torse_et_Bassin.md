---
Fichier: 01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md
Projet: D-Bot
Type: Étude d'Ingénierie Mécanique & Métrologie FDM (Niveau 2)
Auteur: Architecte Système Senior en Robotique Humanoïde
Date: 13 Novembre 2026 (Réaligné sur Torse-123 v42)
Modèle CAO de référence: Autodesk Fusion 360 Torse-123 v42
Documents associés: Audits/AUDIT_METROLOGIQUE_Torse_et_Bassin.json, SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md, DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md, DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md
---

# 🔬 ÉTUDE D'INGÉNIERIE MÉCANIQUE — Méthodologie des Densités Apparentes FDM (PA12-CF) dans Autodesk Fusion 360

> **Statut du document** : Étude technique de Niveau 2 validant la calibration des masses réelles imprimées dans la maquette numérique CAO (`Torse-123 v42`).  
> **Objet** : Établir la méthodologie industrielle d'affectation des matériaux physiques custom à densité apparente équivalente pour compenser la géométrie pleine (B-Rep solide) de Fusion 360 et obtenir la masse réelle, le centre de gravité (CoM) et les matrices d'inertie exacts du robot D-Bot.  
> **État réel dans `Torse-123 v42`** : `Chassis_Structurel_Bassin_Last` (`630,52 cm3`) est déjà calibré à `0,700 g/cm3` (`441,36 g`), tandis que les `20` autres instances polymères (ainsi que les `6` sous-corps composites du `Plastron_Ventral_Torse`) restent encore à la densité pleine brute `1,015 g/cm3` dans l'export `v42` (surévaluation théorique de **`~2,1 à 2,3 kg`** selon [`SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md)). Les `8` occurrences de hanches `ASV1_200` (`02A..09C`) incluses dans ce relevé sont **en cours de définition côté CAO (non définitives)**.

---

## 📑 Sommaire

- [1. Problématique Industrielle : La Masse Pleine CAO vs La Réalité FDM](#1-problématique-industrielle--la-masse-pleine-cao-vs-la-réalité-fdm)
- [2. Formulation Physique de la Densité Apparente Équivalente](#2-formulation-physique-de-la-densité-apparente-équivalente)
- [3. Barème de Calibration Structurale en `Torse-123 v42`](#3-barème-de-calibration-structurale-en-torse-123-v42)
  - [3.1 Catégorie A : Peaux Cosmétiques, Capots & Collet (0,55 g/cm3)](#31-catégorie-a--peaux-cosmétiques-capots--collet-055-gcm3)
  - [3.2 Catégorie B : Coque Torse C1/C2 et Panier Batterie (0,62 g/cm3)](#32-catégorie-b--coque-torse-c1c2-et-panier-batterie-062-gcm3)
  - [3.3 Catégorie C : Coque Bassin « Last » Calibrée (0,70 g/cm3 vs 0,85 g/cm3 Historique)](#33-catégorie-c--coque-bassin--last--calibrée-070-gcm3-vs-085-gcm3-historique)
- [4. Comparatif Métrologique Détaillé Pièce par Pièce (`Torse-123 v42`)](#4-comparatif-métrologique-détaillé-pièce-par-pièce-torse-123-v42)
- [5. Impact Global sur le Centre de Masse et le Bilan Massique Réel](#5-impact-global-sur-le-centre-de-masse-et-le-bilan-massique-réel)
- [6. Automatisation logicielle via Script Python Fusion 360](#6-automatisation-logicielle-via-script-python-fusion-360)
- [7. Paramètres Recommandés pour les Trancheurs FDM (OrcaSlicer / Qidi Plus 4)](#7-paramètres-recommandés-pour-les-trancheurs-fdm-orcaslicer--qidi-plus-4)

---

## 1. Problématique Industrielle : La Masse Pleine CAO vs La Réalité FDM

Dans les logiciels de CAO mécanique (Autodesk Fusion 360, SolidWorks, CATIA, Siemens NX), les composants modélisés sont des volumes géométriques continus fermés dits **B-Rep solides (Boundary Representation)**. 

Lorsque l'utilisateur affecte un matériau physique comme le `PA12-CF` (Nylon 12 chargé à 15 % de fibres de carbone courtes) avec sa densité nominale brute de fonderie :
```text
rho_solide = 1,015 g/cm3  (soit 1 015 kg/m3)
```
le moteur physique multiplie directement le volume géométrique total par cette densité.

Or, en fabrication additive industrielle (FDM / FFF sur Qidi Plus 4) :
1. Les pièces ne sont **jamais 100 % pleines** : elles sont constituées d'une coquille externe (parois de périmètres et couches planes supérieure/inférieure) et d'un volume interne évidé comblé par un motif alvéolaire (remplissage gyroïde à 15 %, 25 % ou 75 %).
2. L'écart entre la masse théorique CAO pleine et la masse réelle pesée en atelier atteint **30 % à 50 % d'erreur par excès** sur les grandes pièces de carrosserie.
3. Cet écart fausse dramatiquement les calculs de dynamique des solides : le centre de gravité (CoM) calculé est artificiellement déplacé, les moments d'inertie (Ixx, Iyy, Izz) sont surévalués de près de 40 %, et les régulateurs d'asservissement d'équilibre de marche (WBC / MPC) se retrouvent décalibrés.

La pratique d'excellence en ingénierie robotique consiste à introduire dans la bibliothèque du document CAO des **matériaux physiques à densité apparente effective**, calibrés d'après les pesées réelles de tranchage slicer.

---

## 2. Formulation Physique de la Densité Apparente Équivalente

Pour un composant donné de volume CAO `V_cad` (en cm3), sa masse réelle fabriquée `M_reelle` (en g) se décompose en deux termes :
```text
M_reelle = M_coquille + M_infill
M_coquille = V_coquille * rho_solide
M_infill = (V_cad - V_coquille) * taux_infill * rho_solide
```

La **densité apparente effective** `rho_apparent` à appliquer dans Fusion 360 s'établit alors par la relation :
```text
rho_apparent = M_reelle / V_cad
rho_apparent = rho_solide * [ (V_coquille / V_cad) * (1 - taux_infill) + taux_infill ]
```

Comme le ratio `V_coquille / V_cad` dépend de l'épaisseur de paroi de la pièce :
* Pour une paroi mince de 2,5 mm avec 3 périmètres (1,35 mm par face), la coquille représente une part dominante du volume.
* Pour une pièce massive de 30 à 50 mm d'épaisseur (comme le bassin), l'infill représente plus de 70 % du volume interne.

---

## 3. Barème de Calibration Structurale en `Torse-123 v42`

Pour concilier rigueur physique et simplicité de maintenance dans Fusion 360, les pièces polymères du robot D-Bot sont segmentées en **3 catégories**, chacune associée à un matériau custom dédié :

```
             ┌──────────────────────────────────────────────────────────────┐
             │        BARÈME DES MATÉRIAUX FDM D-BOT V1 (Torse-123 v42)     │
             └──────────────────────────────────────────────────────────────┘
                                             │
        ┌────────────────────────────────────┼────────────────────────────────────┐
        ▼                                    ▼                                    ▼
 [CATÉGORIE A]                        [CATÉGORIE B]                        [CATÉGORIE C]
 Peaux, Capots & Collet               Coque Torse & Paniers                Coque Pelvienne « Last »
 Infill 12% - 15%                     Infill 20% - 25%                     Coque 5 mm / Infill 15%
 rho = 0,550 g/cm3                    rho = 0,620 g/cm3                    rho = 0,700 g/cm3 (v42)
```

---

### 3.1 Catégorie A : Peaux Cosmétiques, Capots & Collet (0,55 g/cm3)

* **Nom du matériau dans Fusion 360** : `PA12-CF (Cosmetique Infill 15% Gyroide)`
* **Densité apparente cible** : **`0,550 g/cm3`** *(Note métrologique `v42` : bien que ce libellé soit déjà affecté aux composants cosmétiques dans Fusion 360, sa propriété densité sous-jacente y vaut encore `1,015 g/cm3` dans l'audit `v42` ; les masses `v42` brutes et calibrées sont toutes deux reportées au §4)*.
* **Composants assignés** :
  - `Carenage_Pectoral_Haut [ASV1_100_04C]` (`200,82 cm3`)
  - `Carenage_Lombaire_Arriere [ASV1_100_06C_v1]` (`203,65 cm3`)
  - `Platine_Connectique_Facade` (`35,73 cm3`)
  - `Cou - Tube collet` (`51,13 cm3`)
  - `Support Batterie Central` (`29,95 cm3`) & `2x Fixation Batterie` (`10,18 cm3`)
  - `Capot_Droit` / `Capot_Gauche` (`113,38 cm3` la paire — ou Catégorie B `0,620 g/cm3`)
  - Coquilles/capots de hanches `ASV1_200` (**en cours de définition côté CAO, non définitives**).
* **Justification technique** : Ces pièces d'habillage sont déchargées d'effort primaire (la mécanique portante est assurée à 100 % par le squelette aluminium `7075-T6` / `6060-T6`). Avec `3` périmètres (`0,45 mm`) et un remplissage gyroïde `12 % - 15 %`, le ratio masse/volume mesuré sur OrcaSlicer est de `0,54 à 0,56 g/cm3`.

---

### 3.2 Catégorie B : Coque Torse C1/C2 et Panier Batterie (0,62 g/cm3)

* **Nom du matériau dans Fusion 360** : `PA12-CF (Torse Infill 25% Gyroide)`
* **Densité apparente cible** : **`0,620 g/cm3`**
* **Composants assignés** :
  - `Plastron_Ventral_Torse [ASV1_100_01]` (`6` sous-corps composites `2 763,06 cm3` : `Torse_Haut_C1`, `Torse_Haut_C2`, `Torse droit/gauche`, `Torse bassin`, `Torse bas ok` — hors `ceinture` aluminium `16,17 cm3`)
  - `Panier_Batterie_Droit` & `Panier_Batterie_Gauche` (`605,75 cm3` la paire)
  - `Capot_Droit` & `Capot_Gauche` (`113,38 cm3` la paire)
* **Justification technique** : Ces composants possèdent des parois de `3,0 à 4,0 mm` (`4` périmètres extérieurs) et un remplissage gyroïde de `25 %`, complétés par des zones locales `100 %` pleines autour des bossages et glissières de batterie. Le ratio masse/volume mesuré s'établit à `0,615 - 0,625 g/cm3`.

---

### 3.3 Catégorie C : Coque Bassin « Last » Calibrée (0,70 g/cm3 vs 0,85 g/cm3 Historique)

* **Nom du matériau actif dans Fusion 360 (`Torse-123 v42`)** : `PA12-CF (Coque 5mm Infill 15% Gyroide)`
* **Densité apparente réelle appliquée en CAO `v42`** : **`0,700 g/cm3`** *(l'ancienne catégorie historique à `0,850 g/cm3` correspondait à l'époque où le `Chassis_Structurel_Bassin` massif `2 724,2 cm3` reprenait seul les efforts de hanches avant la création du squelette métallique « Pont de Hanches »)*.
* **Composant assigné** :
  - `Chassis_Structurel_Bassin_Last` (`630,52 cm3` -> **`441,36 g`** en `v42`)
* **Justification technique** : Avec le passage au squelette porteur tout-métal **« Pont de Hanches »** (`Aluminium 7075-T6` + `6060-T6`), la coque pelvienne devient une coque mince de `5 mm` évidée (`630,52 cm3` au lieu des `2 724,2 cm3` initiaux) à remplissage `15 %` gyroïde, ce qui fixe sa densité équivalente réelle à **`0,700 g/cm3`** (`441,36 g` déjà comptabilisés dans l'audit `v42`).

---

## 4. Comparatif Métrologique Détaillé Pièce par Pièce (`Torse-123 v42`)

Le tableau ci-dessous confronte les valeurs brutes extraites de [`Audits/AUDIT_METROLOGIQUE_Torse_et_Bassin.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/Audits/AUDIT_METROLOGIQUE_Torse_et_Bassin.json) (`Torse-123 v42`) aux masses cibles après calibration FDM complète :

| Composant / Corps (`Torse-123 v42`) | Volume CAO (`cm3`) | État Matériau dans `v42` (`rho` actuel) | Masse Brute `v42` (`g`) | Catégorie / Densité Cible (`g/cm3`) | Masse Calibrée Cible (`g`) | Delta vs `v42` (`g`) |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **`Plastron_Ventral_Torse`** *(6 corps PA12-CF, hors ceinture Alu)* | `2 763,06` | `Unknown` (`1,015 g/cm3`) | `2 804,55` | **PA12-CF Torse 25% (`0,620`)** | **`1 713,10`** | **`-1 091,45 g`** |
| **`Panier_Batterie_Gauche` + `Droit`** | `605,75` | `PA12-CF Cosm.` (`1,015 g/cm3` non calibré) | `614,83` | **PA12-CF Torse 25% (`0,620`)** | **`375,57`** | **`-239,26 g`** |
| **`Capot_Gauche` + `Droit`** *(Verrouillage batterie)* | `113,38` | `PA12-CF Cosm.` (`1,015 g/cm3` non calibré) | `115,09` | **PA12-CF Torse 25% (`0,620`)** | **`70,30`** | **`-44,79 g`** |
| **`Carenage_Lombaire_Arriere`** | `203,65` | `PA12-CF Cosm.` (`1,015 g/cm3` non calibré) | `206,71` | **PA12-CF Cosmétique 15% (`0,550`)** | **`112,01`** | **`-94,70 g`** |
| **`Carenage_Pectoral_Haut`** | `200,82` | `PA12-CF Cosm.` (`1,015 g/cm3` non calibré) | `203,84` | **PA12-CF Cosmétique 15% (`0,550`)** | **`110,45`** | **`-93,39 g`** |
| **`Platine_Connectique_Facade`** | `35,73` | `PA12-CF Cosm.` (`1,015 g/cm3` non calibré) | `36,27` | **PA12-CF Cosmétique 15% (`0,550`)** | **`19,65`** | **`-16,62 g`** |
| **`Cou - Tube collet`** *(3 sous-corps)* | `51,13` | `PA12-CF Cosm.` (`1,015 g/cm3` non calibré) | `51,90` | **PA12-CF Cosmétique 15% (`0,550`)** | **`28,12`** | **`-23,78 g`** |
| **`Support Batterie Central`** + **`2x Fixation Batterie`** | `40,13` | `PA12-CF Cosm.` (`1,015 g/cm3` non calibré) | `40,73` | **PA12-CF Cosmétique 15% (`0,550`)** | **`22,07`** | **`-18,66 g`** |
| **`Chassis_Structurel_Bassin_Last`** | `630,52` | **`PA12-CF Coque 5mm` (`0,700 g/cm3` DÉJÀ CALIBRÉ)** | **`441,36`** | **Déjà calibré (`0,700`)** | **`441,36`** | **`0,00 g`** |
| **Capots Hanches `02A/03A/04B/05B`** *(`ASV1_200` — WIP)* | `413,47` | `PA12-CF Cosm.` (`1,015 g/cm3` non calibré) | `419,68` | **PA12-CF Cosmétique 15% (`0,550`)** | `227,41` *(cible)* | `-192,27 g` |
| **Supports/Liaisons `06C/07C/08C/09C`** *(`ASV1_200` — WIP)* | `915,77` | `PA12-CF Cosm.` (`1,015 g/cm3` non calibré) | `929,51` | **En cours de définition côté CAO (non définitives)** | *Non retenues en structure* | *Jusqu'à `-929,5 g`* |
| **TOTAL POLYMÈRES TORSE + BASSIN (`Torse-123 v42`)** | **`5 973,41`** | *Mixte (`0,700` sur coque Last / `1,015` ailleurs)* | **`5 864,47 g`** | *Calibration complète* | **`~3,12 kg`** *(avec capots WIP)* / **`~3,56 kg`** *(sans recalib. hanches WIP)* | **`-2,1` à `-2,7 kg`** |

> [!NOTE]
> **Statut des Occurrences Hanches `ASV1_200` (`Torse-123 v42`) :**  
> Dans l'assemblage `Torse-123 v42`, les `8` occurrences de hanches `ASV1_200` (`Support_Hanche_G/D [06C/08C]`, `Liaison_Hanche_G/D [07C/09C]`, `Capot_Lateral_Hanche_G/D [04B/05B]`, `Capot_Protection_Hanche_Frontal_G/D [02A/03A]`) sont explicitement identifiées comme **en cours de définition côté CAO (non définitives)**. Leurs masses brutes (`1 349,19 g` au total) ne doivent donc pas être confondues avec l'objectif final d'habillage pelvien calibré (`~680 - 861 g`).

---

## 5. Impact Global sur le Centre de Masse et le Bilan Massique Réel

L'application complète de la calibration FDM sur l'assemblage `Torse-123 v42` conduit au bilan physique suivant :

1. **Masse totale du sous-ensemble Torse + Bassin (`Torse-123 v42`)** :
   - **Masse brute mesurée dans l'audit `v42`** : **`18,32 kg` (`18 316,38 g`)**, dont `20` instances polymères et `6` sous-corps du `Plastron_Ventral_Torse` restés à `1,015 g/cm3` (soit **`~+2,1 à +2,3 kg`** de marge théorique par rapport à un infill gyroïde réel `15 - 25 %`, tel que quantifié dans [`SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md)).
   - **Masse physique estimée après calibration FDM complète** : **`~16,1 - 16,2 kg`** en incluant les actionneurs `v42` (`4x RS-04`, `1x RS-06`, `1x EL05 / RS-05` Pan) et le roulement `RB8016` *(et en tenant compte du delta acier vs masse réelle des `RS-04` expliquée dans [`FINAL_BOM_Torse_et_Waist_D-Bot.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md))*.
   - **Masse consolidée du robot D-Bot V1.0 complet (43 DOF)** : **`40,03 kg`** en configuration plastron `25 %` (`39,04 kg` avec peau C1/C2 affinée à `2,5 mm`), intégrant les `27` RobStride, les `2` bras complets (`12,79 kg`), la tête/cou (`2x RS-05 / EL05`), les batteries `12S` et le bassin « Pont de Hanches » ([`STUDY_Bilan_Masse_Global_et_Opportunite_Waist_Pitch_2DoF.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Bilan_Masse_Global_et_Opportunite_Waist_Pitch_2DoF.md)).
2. **Centre de masse (CoM) sous Fusion 360 (`Torse-123 v42`)** :
   - Avant calibration complète des peaux thoraciques, le CoM brut du sous-ensemble Torse + Bassin se situe à **`(X = +61,06 mm ; Y = +8,03 mm ; Z = 1 128,75 mm)`** au-dessus du sol.
   - Le recalage de `-1,09 kg` sur le `Plastron_Ventral_Torse` (centré à l'avant du torse) réduit directement le déport sagittal vers `+X` et abaisse d'autant le moment de flexion statique sur le `Waist Yaw` et les `Hip Pitch`.

---

## 6. Automatisation logicielle via Script Python Fusion 360

Pour éviter toute manipulation manuelle fastidieuse et sujette à erreur dans l'interface graphique de Fusion 360, le script officiel suivant a été déployé :

```text
/Users/Shared/Mon Google Drive Physique/Documentation/Code/scripts/fusion360/ApplyPA12CFMaterials/ApplyPA12CFMaterials.py
```

### Fonctionnalités du script automatisé :
1. **Création native des 3 matériaux physiques** dans la bibliothèque interne du document (`design.materials`) avec leurs densités effectives respectives (`0,55`, `0,62` et `0,85 g/cm3`).
2. **Attribution de l'apparence visuelle noire mat** pour assurer l'homogénéité esthétique du robot.
3. **Cartographie intelligente par mots-clés** assignant automatiquement chaque pièce à sa catégorie de charge.
4. **Protection de la quincaillerie et des pièces métalliques internes** (préservation automatique de la ceinture en aluminium 7075 et des vis).
5. **Génération d'un rapport de synthèse instantané** affichant le delta de masse unitaire et global dans une boîte de dialogue Fusion 360.

---

## 7. Paramètres Recommandés pour les Trancheurs FDM (OrcaSlicer / Qidi Plus 4)

Pour que la réalité physique d'atelier corresponde fidèlement aux densités apparentes modélisées dans Fusion 360, les gabarits de tranchage suivants doivent être appliqués dans OrcaSlicer :

| Paramètre Slicer | Catégorie A (Carénages) | Catégorie B (Torse & Batterie) | Catégorie C (Châssis Bassin) |
| :--- | :---: | :---: | :---: |
| **Diamètre de buse (Nozzle)** | 0,4 mm (acier trempé) | 0,4 mm ou 0,6 mm | 0,6 mm (recommandé résistance) |
| **Hauteur de couche (Layer Height)** | 0,20 mm | 0,20 mm | 0,24 mm à 0,28 mm |
| **Nombre de parois (Wall Loops)** | **3 parois (1,35 mm)** | **4 parois (1,80 mm)** | **6 à 8 parois (3,60 mm)** |
| **Couches supérieures / inférieures** | 4 couches pleines | 5 couches pleines | 6 couches pleines |
| **Motif de remplissage (Infill Pattern)** | **Gyroïde (Gyroid)** | **Gyroïde (Gyroid)** | **Gyroïde ou Rectiligne croisé** |
| **Densité de remplissage (Infill %)** | **15 %** | **25 %** | **75 % à 80 %** |
| **Vitesse d'impression interne** | 120 à 150 mm/s | 80 à 100 mm/s | 60 à 80 mm/s (liaison inter-couches) |
| **Température d'extrusion** | 290 °C | 295 °C | 300 °C (fusion maximale) |
| **Température du plateau (PEI)** | 80 °C | 80 °C | 85 °C |
| **Chambre chauffée active** | 55 °C à 65 °C | 60 °C à 65 °C | 65 °C (zéro délaminage) |
| **Modificateurs locaux 100 % solides** | Non requis | **Obligatoires sur bossages M4** | **Obligatoires sur appuis hanches/roulement** |

---

Cette étude constitue la référence métrologique officielle pour l'assainissement de la nomenclature générale et la synchronisation des modèles numériques du robot D-Bot V1.
