# 22 — Usinage CNC : NestWorks C500

Afin d'y usiner les composants vitaux du robot humanoïde D-Bot (y compris les brackets moteurs, l'avant-bras et la série d'actuateurs cycloïdaux de la *D-Hand*), le projet s'appuie **exclusivement** sur la **[CNC NestWorks C500](https://www.nestworks.ai/)** (voir aussi la [campagne Kickstarter](https://www.kickstarter.com/projects/959480926/nestworks-c500-next-gen-smartest-cnc-with-industrial-power)).

Cette fraiseuse professionnelle "Desktop" est la machine de référence unique pour tout l'aluminium du robot, offrant une synergie parfaite avec notre impression 3D (Qidi).

---

## 📑 Sommaire

- [0. Tableau Récapitulatif des Spécifications (Sources Officielles)](#0-tableau-récapitulatif-des-spécifications-sources-officielles)
- [1. Spécifications Techniques (NestWorks C500)](#1-spécifications-techniques-nestworks-c500)
- [2. Le 4ème Axe Rotatif (Axe A) — Spécifications Complètes](#2-le-4ème-axe-rotatif-axe-a-spécifications-complètes)
  - [Spécifications techniques du 4ème axe](#spécifications-techniques-du-4ème-axe)
  - [2.1 — Perçage Goupille Nœud (3 Axes Direct Broche Z)](#21-perçage-goupille-nœud-3-axes-direct-broche-z)
  - [Applications critiques pour le D-Bot :](#applications-critiques-pour-le-d-bot)
- [3. Outils Métal (Professional Metal Tool Kit)](#3-outils-métal-professional-metal-tool-kit)
- [4. Tolérances et Pinces ER11 (Alerte de Sécurité)](#4-tolérances-et-pinces-er11-alerte-de-sécurité)
- [5. Gestion ATC Spécifique (RFID)](#5-gestion-atc-spécifique-rfid)
- [6. Outillage Spécifique — Opérations Torse D-Bot (Brides + Goupilles)](#6-outillage-spécifique-opérations-torse-d-bot-brides-goupilles)
  - [6.1 — Outil Perçage Goupille Nœud Ø3,8 mm (Axe Z Vertical, 60 mm)](#61-outil-perçage-goupille-nœud-ø38-mm-axe-z-vertical-60-mm)
  - [6.2 — Finition H7 Goupille Nœud Ø4 mm](#62-finition-h7-goupille-nœud-ø4-mm)
  - [6.3 — Goupilles d'Ancrage Épaule Ø3 mm (Axe Z, 3 axes standard)](#63-goupilles-dancrage-épaule-ø3-mm-axe-z-3-axes-standard)
  - [6.4 — Usinage Brides Alu 6061-T6 (Programme CAM standard)](#64-usinage-brides-alu-6061-t6-programme-cam-standard)
  - [6.5 — Checklist Collets ER11 à Commander](#65-checklist-collets-er11-à-commander)
- [7. Procédure d'Alésage de Précision H7 / Logements Roulements (Match Machining & Touch Probe 3D)](#7-procédure-dalésage-de-précision-h7-logements-roulements-match-machining-touch-probe-3d)
  - [7.1 — Protocole Standard en 5 Étapes](#71-protocole-standard-en-5-étapes)
- [8. Protocole d'Usinage des Grandes Pièces Hors-Gabarit — Cas de la Ceinture Alu 3 mm (Retrait ATC & Repositionnement 2 Phases)](#8-protocole-dusinage-des-grandes-pièces-hors-gabarit-cas-de-la-ceinture-alu-3-mm-retrait-atc-repositionnement-2-phases)
  - [8.1 — Préparation de la Machine : Démontage du Râtelier ATC & Mode Manuel](#81-préparation-de-la-machine-démontage-du-râtelier-atc-mode-manuel)
  - [8.2 — Gamme d'Usinage en 2 Phases](#82-gamme-dusinage-en-2-phases)
  - [8.3 — Alternative Commerciale de Repli (Sous-traitance Jet d'Eau 2D)](#83-alternative-commerciale-de-repli-sous-traitance-jet-deau-2d)

---

## 0. Tableau Récapitulatif des Spécifications (Sources Officielles)

| Paramètre | Valeur | Note |
|:---|:---:|:---|
| **Zone de travail X** | **230 mm** | Course X effective |
| **Zone de travail Y** | **213 mm** | Course Y effective |
| **Zone de travail Z** | **128 mm** | Course Z effective |
| **Broche** | **800 W** | Air-cooled, AC Servo |
| **Vitesse broche** | **18 000 tr/min** max | Vitesse de coupe alu : 8 000–12 000 tr/min |
| **Vitesse d'avance max** | **5 000 mm/min** | Rapide |
| **Précision / répétabilité** | **±0,02 mm** | ISO H7 atteignable |
| **Pince broche** | **ER11** | Attention : métrique vs. impérial ! |
| **ATC** | **10+ outils** | Carrousel RFID + Touch probe 3D |
| **Structure** | Cadre alu moulé + table acier | Rigide, 95 kg |
| **Poids** | **~95 kg** (210 lbs) | Posée sur établI ou meuble ddié |
| **4ème axe (option)** | ✅ Acquis | Voir section 2 |

---

## 1. Spécifications Techniques (NestWorks C500)

La C500 n'est pas un jouet de bureau, c'est une fraiseuse de classe industrielle miniaturisée :
- **Broche Haute Puissance** : **800W** (AC Servo motorisée, jusqu'à 18 000 tr/min). Permet d'attaquer directement des blocs d'Aluminium 6061 ou 7075-T6, offrant un couple bien supérieur aux petites broches de 200W courantes sur les CNC de bureau.
- **Zone de travail officielle : 230 mm (X) × 213 mm (Y) × 128 mm (Z)** — largement suffisante pour l'usinage des brides (45 × 120 × 40 mm) et des carters d'épaule du D-Bot.
- **Changeur d'Outil Auto (ATC)** : Carrousel 10+ outils avec puces RFID pour la configuration automatique de la longueur d'outil.
- **Précision Industrielle** : Guidages linéaires (Linear Rails & Ballscrews), suffisante pour garantir la tolérance **ISO H7 (±0.02 mm)** vitale pour l'insertion de nos roulements.
- **Palpage 3D** : Touch probe sans fil intégré pour le repérage parfait des origines pièces.

---

## 2. Le 4ème Axe Rotatif (Axe A) — Spécifications Complètes

L'acquisition du **Module 4ème Axe** de la NestWorks C500 change la donne sur l'ingénierie globale du D-Bot. Il permet de traiter les pièces non seulement en "fraisage plat" (3 axes), mais aussi en "tournage" :

### Spécifications techniques du 4ème axe

| Paramètre | Valeur | Note |
|:---|:---:|:---|
| **Diamètre de serrage min** | **3 mm** | Petites tiges, goupilles |
| **Diamètre de serrage max** | **80 mm** | Tube carbone Ø30mm ✅ |
| **Longueur max (avec contre-pointe)** | **156 mm** | Suffisant pour les brides (45mm) |
| **Longueur max (sans contre-pointe)** | **240 mm** | Suffisant pour torse partiel |
| **Réducteur** | **Harmonique** | Haute précision, sans jeu |
| **Répétabilité angulaire** | **±0,02°** estimée | Hérité du réducteur harmonique |

> [!IMPORTANT]
> **Le tube carbone Ø30mm (d = 30mm) est bien dans la plage 3–80mm du mandrin du 4ème axe.** La longueur hors tout de l'assemblage [Bride Sup + tube + Bride Inf] en X est 45mm, bien en dessous des 156mm (avec contre-pointe). Le 4ème axe est donc utilisable directement pour le perçage de la goupille nœud.

### 2.1 — Perçage Goupille Nœud (3 Axes Direct Broche Z)

> [!TIP]
> **Orientation Z Verticale** : La goupille du nœud central étant **verticale (Axe Z)**, le perçage s'effectue directement en **3 axes direct** par la broche Z de la NestWorks C500, de haut en bas sur **60 mm de profondeur** (15mm Alu Sup + 2mm CFRP + 26mm creux + 2mm CFRP + 15mm Alu Inf). Aucun 4ème axe rotatif n'est nécessaire pour cette opération.

**Séquence de perçage vertical Z — 3 axes C500 :**

```
1. Assembler les 2 brides autour du tube (4× M6 au doigt)
2. Poser l'assemblage à plat sur la table CNC (brider par les ailes en L)
3. Palper la face supérieure de la Bride Sup avec le Touch Probe 3D (Z=0)
4. Lancer le cycle de perçage G83 (broche Z) :
   → Foret carbide Ø3,8 mm
   → Vitesse : 800 tr/min, Avance : 50 mm/min, Peck : 3 mm
   → Profondeur : 60 mm exacts (traversée complète Bride Sup → Tube → Bride Inf)
5. Alésage Ø4mm H7 (interpolation hélicoïdale fraise Ø4mm DLC)
6. Insertion goupille élastique Ø4 mm × 60 mm inox
```

> [!NOTE]
> **Avantage majeur** : La broche Z de la C500 réalise le perçage 60 mm avec une garde disponible de **68 mm** (sur la course de 128 mm). C'est simple, rapide et ultra-précis (±0,02 mm).

### Applications critiques pour le D-Bot :
1. **Les Inserts de Tibia (Bouchons Alu/PA12)** : Au lieu d'usiner un bloc plat et de passer un temps infini à détourer un cylindre en 3D, le 4ème axe tourne la pièce. C'est idéal pour créer parfaitement le cylindre Ø12 mm et ses **gorges de circlips** inférieures.
2. **Taraudage et Filetage Externes** : La puissance de la C500 permet de tailler des pas de vis complexes sur de longs axes de transmission (ex: fileter l'embout d'un bras de levier en titane ou acier) grâce à la rotation couplée de l'axe A.
3. **Bras et Phalanges** : Usinage multi-faces sans devoir démonter et repositionner la pièce dans l'étau. La machine fait pivoter la pièce pour usiner dessus, dessous, et sur les côtés dans la même opération (réduisant le fameux "setup time").
4. **Perçage goupille nœud torse (CFRP + Alu)** : Voir section 2.1 ci-dessus.

---

## 3. Outils Métal (Professional Metal Tool Kit)

Le choix du kit professionnel orienté métal avec revêtement **DLC (Diamond-Like Carbon)** est le pilier de tous nos développements sur de l'Aluminium 7075-T6 pour éviter que l'alu chaud ne "colle" à la fraise.

| Type d'outil | Utilisation sur le D-Bot |
| :--- | :--- |
| **Flat End Mill (1/4")** | Fraise plate (6.35 mm). L'outil "de force" pour ébaucher les gros brackets moteurs (RS-04/05). |
| **O-Type End Mill** | Fraise à 1 dent. Évacuation très rapide des copeaux (idéal poches profondes). |
| **Chamfer Cutter (90°)** | **Indispensable pour le H7.** Permet de casser les angles une fois alésés pour ne pas rayer les micro-roulements à l'insertion. |
| **Ball Nose** | Pour usiner des congés internes dans les phalanges afin de prévenir la rupture sous charge. |

> [!TIP]
> **Règle d'Usinage H7** : Une passe d'ébauche avec une Flat End Mill usée, suivie *impérativement* d'une passe terminale micrométrique avec un outil DLC neuf pour la cote finale.

---

## 4. Tolérances et Pinces ER11 (Alerte de Sécurité)

La NestWorks C500 utilise un système de pince de serrage industriel **ER11**. Le kit de base est souvent livré en métrique américain (fraises de *1/4"* soit 6.35 mm et de *1/8"* soit 3.175 mm). 

**Règle absolue :**
1. **Ne jamais forcer** une fraise métrique de 6 mm dans une pince impériale de 1/4" (6.35 mm).
2. Ce désalignement engendre un "runout" (voile) asymétrique. Un battement de juste **0.02 mm** ruine le fraisage d'un logement de roulement H7, et abîme prématurément la broche de 800W.
3. **Solution** : Ranger les collets NestWorks impériaux séparément. Si vous achetez des fraises européennes (6 mm, 4 mm), commandez les pinces ER11 métriques strictes correspondantes.

---

## 5. Gestion ATC Spécifique (RFID)

Le système ATC de NestWorks opère avec des puces RFID collées sur les **Bit Tool Holders** (les porte-outils, pas directement sur la fraise). 
- **Bénéfice** : La puce n'est pas exposée à la chaleur ou aux vibrations de la coupe. 
- **Maintenance** : Si une fraise casse, il suffit de changer la partie coupante dans le collet. La puce numérotée reste fixée au haut du Tool Holder, conservant ses propriétés et sa longueur pré-calibrée dans le logiciel NestWorks Studio.

---

## 6. Outillage Spécifique — Opérations Torse D-Bot (Brides + Goupilles)

Cette section détaille les outils de coupe précis pour chaque opération du sous-système tube carbone / brides / carters, en tenant compte des contraintes ER11 et du perçage CFRP.

> [!IMPORTANT]
> **Contrainte ER11** : La broche C500 utilise des pinces ER11 (capacité **0,5 à 7 mm maxi**). Tous les outils ci-dessous ont une queue ≤ 7 mm et sont donc compatibles ER11. Ne jamais commander des forets ou fraises avec queue Ø8 mm ou plus.

---

### 6.1 — Outil Perçage Goupille Nœud Ø3,8 mm (Axe Z Vertical, 60 mm)

> [!NOTE]
> La goupille étant **verticale (axe Z)** et le perçage traversant **60 mm**, l'opération utilise un foret carbure de série longue standard (longueur totale ~75–80 mm, longueur de coupe ≥ 65 mm), très facile à vous procurer.

**Spécifications exactes de l'outil :**

| Paramètre | Valeur | Justification |
|:---|:---:|:---|
| **Type** | Foret carbide monobloc | CFRP exige carbure — pas HSS |
| **Diamètre** | **3,8 mm** | Avant-trou (finition Ø4mm H7 ensuite) |
| **Longueur totale** | **≥ 75 mm** | 60mm profondeur + 15mm tige dans collet |
| **Longueur de coupe** | **≥ 65 mm** | Doit traverser 60mm d'assemblage |
| **Diamètre de queue** | **3,8 mm ou 4 mm** | Compatible ER11 (< 7mm) ✅ |
| **Revêtement** | **TiAlN ou DLC** | Résistance à la chaleur + CFRP |
| **Géométrie pointe** | 130–135° | Réduit l'éclatement à la sortie CFRP |

**Paramètres de coupe sur C500 (CFRP + alu 6061) :**

| Paramètre | Valeur | Note |
|:---|:---:|:---|
| **Vitesse broche** | **800 tr/min** | Priorité CFRP |
| **Avance** | **50 mm/min** | Lente |
| **Profondeur totale** | **60 mm** | 15mm Alu Sup + 2mm CFRP + 26mm creux + 2mm CFRP + 15mm Alu Inf |
| **Cycle perçage** | **G83 peck drilling** | Dégagement tous les 3 mm |
| **Lubrification** | **WD-40 léger** | Nettoyage des poussières |

> [!TIP]
> **Garde Z sur C500** : Course Z = 128 mm. Profondeur = 60 mm. Marge disponible = **68 mm** — très confortable et sécurisant pour le travail en 3 axes direct.

**Sourcing recommandé :**
- Foret carbide long series Ø3,8 mm × 150 mm total — chercher sur **Alibre, Sorotec, Hufschmied** (spécialiste composite)
- Référence type : *Hufschmied HPC-PLUS* Ø3,8 mm ou *Carbide 3D Pro* long-series Ø3,8 mm
- Collet ER11 à commander en 3,8 mm métrique (ou 4 mm si queue Ø4 mm)

---

### 6.2 — Finition H7 Goupille Nœud Ø4 mm

Après le perçage à Ø3,8 mm, la finition Ø4 mm H7 se fait par **interpolation hélicoïdale** sur la C500.

| Paramètre | Valeur |
|:---|:---:|
| **Outil** | Fraise carbide Ø4 mm, 2 dents, DLC |
| **Queue** | Ø4 mm (ER11 ✅) |
| **Longueur de coupe** | ≥ 5 mm (interpolation locale) |
| **Stratégie CAM** | Interpolation hélicoïdale descendante, passes ≤ 0,05 mm radial |
| **Vitesse broche** | 6 000 tr/min (alu) |
| **Avance** | 300 mm/min |

> [!NOTE]
> Finition H7 seulement sur les 5–8 mm d'entrée (face DOS, alu) et les 5–8 mm autour des parois CFRP du tube. La goupille élastique se comprime légèrement à l'insertion — le reste du trou (creux du tube + milieu) n'a pas besoin d'alésage de précision.

---

### 6.3 — Goupilles d'Ancrage Épaule Ø3 mm (Axe Z, 3 axes standard)

| Étape | Outil | Ø | Longueur min | ER11 | Vitesse | Avance |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Avant-trou | Foret carbide Ø2,8 mm | 2,8 mm | 30 mm (alu + paroi tube) | ✅ | 3 000 tr/min | 150 mm/min |
| Finition H7 | Fraise carbide Ø3 mm DLC | 3 mm | 5 mm | ✅ | 6 000 tr/min | 200 mm/min |

---

### 6.4 — Usinage Brides Alu 6061-T6 (Programme CAM standard)

| Opération | Outil | Ø | ER11 | Vitesse | Note |
|:---|:---:|:---:|:---:|:---:|:---|
| Surfaçage faces | Fraise Ø6 mm DLC (O-type 1 dent) | 6 mm | ✅ | 10 000 tr/min | Passes 0,3 mm, avance 800 mm/min |
| Demi-alésage R15 mm | Fraise Ø6 mm DLC, interpolation hélicoïdale | 6 mm | ✅ | 10 000 tr/min | Finition H7 : passe 0,05 mm |
| Trous M6 traversants Ø6,3 mm | Foret carbide Ø6,3 mm (ou 1/4") | 6,35 mm | ✅ | 5 000 tr/min | Pas de taraudage — vis + Nylstop |
| Trous M4 traversants Ø4,2 mm | Foret carbide Ø4,2 mm | 4,2 mm | ✅ | 6 000 tr/min | Pas de taraudage — vis + Nylstop |
| Aile en L (poche) | Fraise Ø6 mm DLC | 6 mm | ✅ | 8 000 tr/min | Passes 0,5 mm prof., avance 600 mm/min |
| Chanfreins arêtes H7 | Outil chanfrein 90° | — | ✅ | 8 000 tr/min | Cassage arêtes avant goupille |

> [!TIP]
> **Pas de taraudage prévu** : Les trous M6 et M4 sont tous traversants avec écrous Nylstop — aucun taraud nécessaire dans la C500. Cela simplifie le programme CAM et évite le risque de casse de taraud dans l'alu.

> [!IMPORTANT]
> **Consigne CAM C500 — Dépouille de Serrage (Split Gap 0,8 à 1,0 mm)** :
> Pour éviter la butée parasitaire aluminium contre aluminium au plan de joint :
> 1. Définir le surfaçage du plan de joint de chaque demi-bride à **Z = -0,4 mm à -0,5 mm** en dessous du plan de séparation théorique (profondeur demi-alésage = 14,5 mm).
> 2. Cela garantit un jeu de **0,8 à 1,0 mm** entre les deux brides assemblées autour du tube Ø30 mm, transmettant 100% du serrage des 4× M6 en pincement radial direct.

---

### 6.5 — Checklist Collets ER11 à Commander

| Diamètre outil | Type | Quantité | Usage |
|:---:|:---:|:---:|:---|
| **3,8 mm** (ou 4 mm si queue Ø4) | ER11 métrique | 1 | Foret extra-long goupille nœud |
| **4 mm** | ER11 métrique | 1 | Fraise finition H7 Ø4mm |
| **6 mm** | ER11 métrique | 1 | Fraises DLC principales |
| **6,35 mm (1/4")** | ER11 impérial | Déjà dans kit | Flat end mill 1/4" |
| **3 mm** | ER11 métrique | 1 | Fraise finition H7 Ø3mm |
| **2,8 mm** | ER11 métrique | 1 | Foret avant-trou goupille épaule |
| **4,2 mm** | ER11 métrique | 1 | Foret trous M4 |

> [!NOTE]
> Vérifier que les collets commandés sont **ER11 certifiés** (pas ER16 ou ER20 qui ne s'adaptent pas sur la C500). La cote externe du collet ER11 est D=11,5mm.

---

## 7. Procédure d'Alésage de Précision H7 / Logements Roulements (Match Machining & Touch Probe 3D)

Sur le robot D-Bot, plusieurs pièces critiques intègrent des logements de roulements de grand diamètre en tolérance fine ISO H7 (ex. Platine Pelvis pour roulement croisé CRBH 8016 en `Ø 120 H7`, brides d'épaules, logements de moyeux).

Pour garantir un **ajustement glissant juste H7/h6** sans exiger d'instruments de métrologie coûteux (micromètres 100-125 mm pour usage unique), la NestWorks C500 applique la méthode de l'**appariement direct sur machine (*Match Machining*)** combinée à son **Touch Probe 3D sans fil**.

### 7.1 — Protocole Standard en 5 Étapes

```
[1. Palpage Relatif Roulement]  ──►  [2. Ébauche + Offset Sécurité (+0,10 mm)]
               │
               ▼
[3. Palpage Alésage Usiné]      ──►  [4. Passes de Finition d'Approche (0,02 / 0,01 mm)]
                                                  │
                                                  ▼
                                     [5. Test Fit Physique à la Main] ➔ Validation H7/h6
```

1. **Étape 1 — Palpage du Roulement Réel (Mesure Relative)** :
   - Poser le roulement dégraissé bien à plat et propre sur la table de la C500 (ou bridé doucement en étau de précision).
   - Lancer la macro de palpage bossage extérieur en 4 points (Boss Probing X+, X-, Y+, Y-) avec le Touch Probe 3D.
   - Relever le diamètre extérieur effectif mesuré `D_roulement`.
   - *Bénéfice métrologique* : Les éventuelles dérives thermiques ou d'échelle d'axes s'annulent car c'est la même machine et le même palpeur qui mesurent le composant et usinent la poche.

2. **Étape 2 — Ébauche et Demi-Finition avec Surépaisseur de Sécurité** :
   - Sous Fusion 360 (stratégie 2D Contour ou Bore), programmer l'alésage avec une surépaisseur radiale de finition (*Stock to Leave*) de **`+0,10 mm`** (l'alésage usiné sera sous-dimensionné de 0,20 mm au diamètre, ex. `Ø 119,80 mm` pour un 120 mm nominal).
   - Outil recommandé : Fraise carbure 3 dents Ø 6 mm ou Ø 8 mm DLC (10 000 tr/min, avance 800 mm/min, descente hélicoïdale pas de 0,5 mm, lubrification brumisation d'air/alcool).

3. **Étape 3 — Contrôle Intermédiaire au Touch Probe 3D** :
   - Sans démonter la pièce de son bridage, appeler le Touch Probe 3D et exécuter un cycle de palpage intérieur (Bore Probing) de la poche usinée.
   - Comparer le diamètre usiné effectif avec `D_roulement`.
   - Présenter le roulement physique à la main : il ne doit évidemment pas pénétrer dans le logement.

4. **Étape 4 — Passes d'Approche Successives (Compensation Rayon d'Outil)** :
   - Ajuster la compensation d'usure d'outil (*Tool Wear Offset* / G41) sur le contrôleur de la C500 pour enlever `0,05 mm`, puis relancer la passe de finition.
   - Continuer par micro-passes de **`0,01 à 0,02 mm`** en réessayant manuellement l'insertion du roulement entre chaque passe.

5. **Étape 5 — Validation de l'Ajustement Glissant Juste (H7/h6)** :
   - L'usinage est arrêté dès que la bague extérieure du roulement s'insère manuellement avec une résistance douce et constante (« ajustement gras » sous légère pression de la paume), sans aucun jeu radial perceptible.
   - Chanfreiner à `0,5 mm × 45°` l'entrée du logement pour faciliter l'engagement axial sans abîmer les portées.

---

## 8. Protocole d'Usinage des Grandes Pièces Hors-Gabarit — Cas de la Ceinture Alu 3 mm (Retrait ATC & Repositionnement 2 Phases)

Sur le robot D-Bot, la ceinture intermédiaire en tôle d'Aluminium 7075-T651 (`size: 202,81 mm × 262,52 mm × 3,0 mm`) dépasse les courses standard de la NestWorks C500 en usinage direct d'une seule passe (course Y max = 213 mm vs largeur pièce = 262,5 mm).

Afin de garantir une **totale souveraineté de fabrication en atelier** sans dépendre obligatoirement de sous-traitance externe, la **méthode officielle de référence** consiste à exploiter la C500 en **Mode Manuel sans ATC** avec un protocole de **repositionnement en 2 phases avec recalage Touch Probe 3D**.

### 8.1 — Préparation de la Machine : Démontage du Râtelier ATC & Mode Manuel
1. **Dégagement de la Table** : Retirer le râtelier de porte-outils ATC de la machine pour libérer l'intégralité du plateau rainuré en acier.
2. **Gain de Course Utile** : En mode manuel sans ATC, les fins de course logicielles sont reculées aux limites physiques des vis à billes :
   - Course Axe X : **`240,0 mm`**
   - Course Axe Y : **`210,0 mm`**
   - Course Axe Z : **`128,0 mm`**
3. **Brut Marchand** : Plaque Aluminium 7075-T651 de Blockenstock format `230 mm × 495 mm × 3,0 mm`. La largeur du brut (230 mm) glisse parfaitement entre les montants de la machine selon l'axe X.

### 8.2 — Gamme d'Usinage en 2 Phases

```
[Brut 230 × 495 mm sur Table C500 Dégagée]
       │
       ▼
[PHASE 1 : Usinage Aile Gauche + Demi-Façade + 2 Trous Étalons Ø 4,5 mm]
       │
       ▼
[Translation Manuelle du Brut (+90 mm vers la gauche) & Re-bridage]
       │
       ▼
[Palpage 3D Automatique des 2 Trous Étalons au Touch Probe sans fil]
       │
       ▼
[PHASE 2 : Usinage Aile Droite + Demi-Façade Complémentaire]
       │
       ▼
[Contrôle Métrologique & Ébavurage] ➔ Ceinture Monolithique Terminée (+/- 0,02 mm)
```

1. **Phase 1 — Usinage Côté Gauche & Perçage des Trous Étalons** :
   - Brider la tôle à plat sur la table à l'aide de brides basses (Step Clamps).
   - Définir l'origine WCS G54 sur le coin avant-gauche du brut au Touch Probe 3D.
   - Usiner le flanc gauche (`Y = [-122,58 mm à 0 mm]`), la moitié gauche de la traverse avant et percer les 3 trous M4 (`Ø 4,5 mm`) du côté gauche.
   - Percer impérativement 2 trous lisses étalons de référence (`Ø 4,5 mm`) espacés de 80,0 mm le long de l'axe longitudinal pour le recalage de Phase 2.
   - Détourer le contour intérieur et extérieur de cette moitié avec une fraise carbure 2 dents DLC Ø 3,175 mm (1/8") ou Ø 4,0 mm (12 000 tr/min, avance 600 mm/min, lubrification brumisation).

2. **Repositionnement du Brut** :
   - Desserrer les brides de serrage.
   - Faire glisser la tôle d'aluminium d'environ 90 mm vers la gauche sur la table (axe Y de la machine).
   - Rebrider fermement la tôle sur le plateau en s'assurant de la planéité.

3. **Recalage Automatique au Touch Probe 3D (WCS G55)** :
   - Monter le Touch Probe 3D sans fil dans la broche.
   - Lancer la routine de palpage intérieur en 4 points (Bore Probing) sur le Trou Étalon #1 pour définir l'origine `X = 0, Y = 0`.
   - Palper le Trou Étalon #2 pour corriger automatiquement l'alignement angulaire de rotation de table (*Coordinate System Rotation* G68 ou macro NestWorks Align).
   - Précision de recalage obtenue : **`+/- 0,02 mm`** (invariable et répétable).

4. **Phase 2 — Usinage Côté Droit & Jonction Centrale** :
   - Recharger la fraise carbure DLC.
   - Usiner le flanc droit (`Y = [0 mm à +139,93 mm]`), la moitié droite de la traverse avant et les 3 perçages M4 du flanc droit.
   - La trajectoire de coupe vient tangenter et fermer parfaitement le profil au centre de la façade avant (+X).
   - L'éventuelle micro-reprise d'usinage (`< 0,02 mm`) se situe en plein centre de la façade avant, zone qui est **100% masquée et protégée par le recouvrement du plastron abdominal inférieur P2**.

### 8.3 — Alternative Commerciale de Repli (Sous-traitance Jet d'Eau 2D)
Si l'opérateur souhaite économiser le temps de recalage machine, l'export du fichier DXF 2D monolithique complet (`ceinture_intermediaire_alu_3mm.dxf`) reste disponible pour découpe immédiate en sous-traitance industrielle au **jet d'eau abrasif** ou **laser fibre** (prestataire type John Steel, Sculpteo ou 247TailorSteel, délai 3-5 jours, coût indicatif 25 à 30 € sur tôle Blockenstock).


