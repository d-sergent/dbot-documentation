# 🔬 Guide Complet — Capteurs Tactiles MLX90393 : PCB Custom (JLCPCB) & Recyclage des PCBs WowRobo

*Document : GUIDE_PCB_MLX90393_et_Recyclage_WowRobo.md*  
*Créé : juin 2026 — Référence : GUIDE_COMPLET_Fabrication_et_Montage_DHand_V1.md §5.3*

---

## Table des Matières

1. [Contexte et Problème Initial](#1-contexte)
2. [Partie A — PCB Custom 10×10mm pour les Doigts (JLCPCB)](#2-pcb-custom)
   - [Circuit électrique minimal](#21-circuit)
   - [BOM — Liste de composants JLCPCB](#22-bom)
   - [Guide pas-à-pas EasyEDA](#23-easyeda)
   - [Fichier CPL (placement)](#24-cpl)
   - [Checklist DFM avant commande](#25-dfm)
3. [Partie B — Analyse : 1 ou 5 capteurs ?](#3-analyse-paume)
4. [Partie C — IMU vs Capteurs Plantaires : la fausse alternative](#4-imu-vs-pied)
5. [Partie D — Plan complet de recyclage des 20 PCBs WowRobo](#5-recyclage)
6. [Architecture I2C globale du robot](#6-i2c-global)
7. [**Partie E — Quel aimant pour quel emplacement ?**](#7-aimants) ⭐ *Nouveau*

---

## 1. Contexte et Problème Initial {#1-contexte}

Le PCB eFlesh WowRobo acheté (**20 × 20 mm** + 5×5mm languette connecteur) est un **Array 5-capteurs** (5× MLX90393 disposés en croix) conçu pour la paume. Il est physiquement impossible de le fixer sur une phalange distale de 12–15 mm de large.

**Inventaire matériel — Aimants disponibles (Supermagnete) :**

| Référence | Désignation | Grade | Force | Qté | Idéal pour |
|:---|:---|:---:|:---:|:---:|:---|
| **S-03-01-N** | Disque Ø3mm × 1mm | N48 | 190 g | **40** | Doigts, avant-bras |
| **S-08-03-N** | Disque Ø8mm × 3mm | N45 | 1.5 kg | **40** | Semelle pieds, torse |
| **W-05-N** | Cube 5mm × 5mm × 5mm | N42 | 1.1 kg | **10** | Paume (2 PCBs/main) |

> **Voir Partie E** pour l'analyse complète de quel aimant utiliser à quel endroit, avec calculs de champ magnétique.

**Décision d'architecture :**

| Emplacement | Solution retenue | Justification |
|:---|:---|:---|
| Bouts de doigts (5/main) | **PCB custom 10×10mm JLCPCB** (1× MLX90393) | Seule solution < 12mm de large |
| Paume (1/main) | **1× PCB WowRobo** (5 capteurs) | Taille 20×20mm adaptée à la paume |
| Pieds (semelle) | **4× PCBs WowRobo** par pied | Surface 120×80mm suffisante |
| Avant-bras, torse | **PCBs WowRobo spare** | Détection contact/collision |

---

## 2. Partie A — PCB Custom 10×10mm pour les Doigts (JLCPCB) {#2-pcb-custom}

### 2.1 Circuit Électrique Minimal {#21-circuit}

Le MLX90393 en boîtier **QFN-16 (3×3mm)** ne nécessite que 5 composants externes pour fonctionner en mode I2C :

```
                        3.3V (VDD)
                           │
                   ┌───────┴────────────────────────────────────┐
                   │                                            │
                  [C1]                                         [C2]
               100nF/0402                                   10µF/0402
               (decoupl.)                                (bulk decoupl.)
                   │                                            │
                   └───────┬────────────────────────────────────┘
                           │
              ┌────────────┴────────────────────────────────────────┐
              │                                                      │
     VDD ─────┤ Pin 1 (VDD)          Pin 16 (VDDIO) ├───── 3.3V    │
              │                                                      │
  SCL ────[R1]┤ Pin 3 (SCL)           Pin 8 (GND)  ├───── GND      │
  (4.7kΩ)     │                                                      │
  SDA ────[R2]┤ Pin 4 (SDA)           Pin 7 (CS)   ├───── VDD      │  ← CS=HIGH → mode I2C
  (4.7kΩ)     │                                                      │
              │   MLX90393                                           │
  A0 ─────────┤ Pin 5 (A0)            Pin 6 (A1)   ├───── A1       │  ← adresse I2C
  (GND/VDD)   │                                                      │
              │           Pins 9-15 (GND)           │
              │           Pin 2 (INT) ─── NC         │  ← non connecté
              └──────────────────────────────────────┘

  R1, R2 : 4.7kΩ 0402 (pull-up I2C) — OMIS si l'ESP32-S3 a déjà des pull-ups sur le bus
  C1     : 100nF céramique 0402 (MLCC, X5R/X7R, 10V)
  C2     : 10µF céramique 0402 (MLCC, X5R, 10V)
  A0, A1 : soudés à GND ou VDD selon l'adresse souhaitée (voir table)
```

#### Table d'adresses I2C (MLX90393)

| A1 | A0 | Adresse 7-bit | Usage suggéré |
|:---:|:---:|:---:|:---|
| GND | GND | **0x0C** | Index |
| GND | VDD | **0x0D** | Majeur |
| VDD | GND | **0x0E** | Annulaire |
| VDD | VDD | **0x0F** | Auriculaire |

> **Note :** Le Pouce est sur le Bus I2C N°2 de l'ESP32-S3 à l'adresse 0x0C (pas de conflit d'adresses entre les deux bus).

#### Connexion de la broche CS

| Broche | Connexion | Raison |
|:---|:---|:---|
| **CS (Pin 7)** | Reliée à **VDD (3.3V)** | CS=HIGH → mode I2C activé. CS=LOW → mode SPI |
| **INT (Pin 2)** | Non connectée (NC) | Interruption optionnelle, non utilisée ici |
| **TRIG (Pin 14)** | Non connectée (NC) | Trigger externe, non utilisé |

---

### 2.2 BOM — Liste de Composants JLCPCB {#22-bom}

Fichier BOM compatible JLCPCB PCBA (format CSV) :

```csv
Comment,Designator,Footprint,LCSC Part #,Description,Quantity
"MLX90393SLW-ABA-011-RE",U1,"QFN-16_L3.0-W3.0-P0.50-BL","C2827654","MLX90393 3-Axis Magnetometer QFN16",1
"100nF 10V X7R 0402",C1,"C0402","C14663","100nF Decoupling Capacitor 0402",1
"10uF 10V X5R 0402",C2,"C0402","C15525","10uF Bulk Capacitor 0402",1
"4.7kΩ 1% 0402",R1,"R0402","C25900","4.7k Pull-up SDA 0402",1
"4.7kΩ 1% 0402",R2,"R0402","C25900","4.7k Pull-up SCL 0402",1
"JST SH 4-pin 1.0mm",J1,"JST-SH-4P-1.0MM","C160404","JST SH 4P I2C Connector 1.0mm",1
```

> [!WARNING]
> **Vérifiez les références LCSC** sur le site JLCPCB avant de commander : les stocks changent régulièrement. Cherchez `MLX90393` dans la bibliothèque JLCPCB et confirmez la disponibilité de la variante **MLX90393SLW-ABA-011-RE** (I2C/SPI, 3.3V, QFN-16).

> [!TIP]
> Si les résistances pull-up (R1, R2) sont déjà présentes sur la carte de développement ESP32-S3 que vous utilisez (ex: Seeed XIAO ESP32-S3), vous pouvez **supprimer R1 et R2 du BOM** pour réduire le coût et simplifier la conception. La plupart des ESP32-S3 ont des pull-ups internes ou des résistances externes sur leurs bus I2C.

---

### 2.3 Guide Pas-à-Pas EasyEDA {#23-easyeda}

**Prérequis :** Créez un compte gratuit sur [easyeda.com](https://easyeda.com) et sélectionnez **EasyEDA Standard Edition (v6)**.

#### Étape 1 : Créer un nouveau projet

1. Cliquez sur **File → New → Project**
2. Nommez le projet : `MLX90393_10x10_DBot_Finger`
3. Cliquez sur **File → New → Schematic** dans ce projet

#### Étape 2 : Placer le composant MLX90393

1. Appuyez sur `P` (Place component) ou cliquez sur **Place → Component**
2. Dans la barre de recherche, tapez : `MLX90393`
3. Sélectionnez `MLX90393SLW-ABA-011-RE` (LCSC: C2827654)
4. Cliquez pour placer le composant au centre de la feuille

#### Étape 3 : Placer les condensateurs et résistances

1. Placez **C1** : recherchez `100nF 0402`, référence C14663
2. Placez **C2** : recherchez `10uF 0402`, référence C15525
3. Placez **R1** : recherchez `4.7k 0402`, référence C25900
4. Placez **R2** : idem R1
5. Placez **J1** : recherchez `JST SH 4P 1.0mm`, référence C160404

#### Étape 4 : Câbler le schéma

Connectez les fils selon le schéma de la section 2.1 :
1. Appuyez sur `W` pour tracer un fil
2. Reliez VDD → C1 → C2 → Pin VDD et VDDIO du MLX90393
3. Reliez GND → côté négatif C1 et C2 → Pins GND (8, 9–15) du MLX90393
4. Reliez CS (Pin 7) → VDD
5. Reliez SDA (Pin 4) → R2 → connecteur J1 broche 2, et fil → nœud SDA
6. Reliez SCL (Pin 3) → R1 → connecteur J1 broche 3, et fil → nœud SCL
7. Ajoutez des **Power Flags** (Place → Power Port) pour VDD et GND
8. Câblez A0 et A1 à GND (adresse 0x0C) ou à VDD selon le doigt

#### Étape 5 : Passer au PCB Layout

1. Cliquez sur **Design → Convert Schematic to PCB**
2. Une nouvelle fenêtre s'ouvre avec les composants non placés
3. **Définissez les dimensions du PCB :**
   - Cliquez sur **Board Outline** (contour)
   - Tracez un rectangle de **10mm × 10mm**
   - Dans les propriétés, réglez Thickness à **0.8mm** (plus léger, plus fin)

#### Étape 6 : Placer les composants sur le PCB

Ordre de placement recommandé :
1. **U1 (MLX90393)** → au centre exact du PCB (coordonnées X=5, Y=5)
2. **C1 (100nF)** → à 1mm au-dessus du pin VDD de U1 (côté Top)
3. **C2 (10µF)** → à 1mm à droite de C1
4. **R1, R2** → sur le bord gauche du PCB (si inclus)
5. **J1 (connecteur JST)** → sur le bord droit ou bas du PCB, **en dehors** des 10mm si possible (le connecteur peut dépasser légèrement)

#### Étape 7 : Tracer les pistes (Routing)

Largeurs de piste recommandées :
- **Pistes signal (SDA, SCL, A0, A1)** : **0.2mm** (minimum DRC JLCPCB)
- **Pistes alimentation (VDD, GND)** : **0.4mm**
- **Plan de masse (GND Polygon)** : créez un remplissage cuivre GND sur la couche Bottom (`Place → Copper Area`, sélectionnez GND)

Règle critique :
> Placez C1 et C2 aussi proches que possible du pin VDD de U1. La distance idéale est **< 1mm**. Cela réduit l'inductance parasite et filtre efficacement le bruit haute fréquence.

#### Étape 8 : Vérification DRC

1. Cliquez sur **Design → Design Rule Check (DRC)**
2. Réglez les règles minimales JLCPCB :
   - Min Clearance : **0.127mm**
   - Min Track Width : **0.127mm**
   - Min Via Size : **0.4mm** (pad) / **0.2mm** (drill)
3. Corrigez toutes les erreurs avant de continuer

#### Étape 9 : Export des fichiers

1. **Gerbers** : `Fabrication → Generate Gerber` → téléchargez le ZIP
2. **BOM** : `Fabrication → BOM` → exportez en CSV
3. **CPL** (positions) : `Fabrication → Pick and Place` → exportez en CSV

---

### 2.4 Fichier CPL (Placement des Composants) {#24-cpl}

Exemple de CPL à vérifier/ajuster après placement dans EasyEDA :

```csv
Designator,Mid X,Mid Y,Layer,Rotation
U1,5.00,5.00,Top,0
C1,5.00,6.80,Top,90
C2,6.80,6.80,Top,90
R1,1.00,5.00,Top,0
R2,1.00,4.00,Top,0
J1,9.50,5.00,Top,270
```

> Ces coordonnées sont des exemples. Les valeurs réelles dépendent de votre placement dans EasyEDA. Vérifiez toujours que l'orientation de chaque composant correspond à la rotation 3D affichée par JLCPCB lors de l'upload.

---

### 2.5 Checklist DFM Avant Commande {#25-dfm}

Avant de soumettre votre commande sur JLCPCB, vérifiez ces points :

#### Dimensions et couches
- [ ] Taille du PCB : **10mm × 10mm** exactement
- [ ] Épaisseur : **0.8mm** (sélectionner dans les options JLCPCB)
- [ ] Nombre de couches : **2** (Top + Bottom)
- [ ] Couleur du masque de soudure : **Noir** (recommandé pour discrétion)

#### Règles de fabrication
- [ ] Toutes les pistes ≥ **0.127mm** de large
- [ ] Tous les espaces (clearance) ≥ **0.127mm**
- [ ] Vias : diamètre de perçage ≥ **0.2mm**, pad ≥ **0.4mm**
- [ ] Distance bord de piste / bord de PCB ≥ **0.3mm**
- [ ] Aucune piste ne passe sous le pad thermique central du QFN-16

#### Composants (Assembly PCBA)
- [ ] Le MLX90393 est en stock chez JLCPCB (vérifier sur le site)
- [ ] L'orientation du composant U1 dans le CPL correspond à la sérigraphie
- [ ] Les condensateurs C1 et C2 sont à ≤ 1mm du pin VDD de U1
- [ ] Le connecteur JST J1 est accessible et non masqué par d'autres composants

#### Connexions électriques
- [ ] CS (Pin 7) est bien connecté à **VDD** (et non à GND)
- [ ] VDDIO (Pin 16) est connecté à **VDD** (3.3V)
- [ ] Tous les pins GND (8, 9–15) sont connectés au plan de masse
- [ ] INT (Pin 2) est laissé **non connecté** (NC) — ne pas le relier à GND
- [ ] A0 et A1 sont câblés selon l'adresse voulue (voir tableau §2.1)

#### Après réception des PCBs
- [ ] Tester la continuité VDD–GND avec un multimètre (doit être **ouvert**)
- [ ] Scanner le bus I2C avec `i2cdetect` — le MLX90393 doit répondre à l'adresse configurée
- [ ] Lire un registre de status (commande `0x40`) — le bit ERROR (bit 4) doit être à 0

---

## 3. Partie B — Analyse : 1 ou 5 Capteurs en Paume ? {#3-analyse-paume}

### Question posée

> *Le PCB WowRobo comporte 5 capteurs MLX90393 disposés en croix. Avec des aimants de Ø3mm×1mm, est-il judicieux d'utiliser tous les 5 capteurs pour la paume, ou un seul suffirait-il ?*

### Analyse technique

#### Ce que permettent 5 capteurs vs 1 capteur sur la paume

| Capacité | 1 capteur central | 5 capteurs (croix) |
|:---|:---:|:---:|
| Détection pression normale (Z) | ✅ | ✅✅✅ |
| Détection cisaillement (X, Y) | ✅ | ✅✅✅ |
| **Localisation du point de contact** | ❌ | ✅ |
| **Carte de pression (distribution)** | ❌ | ✅ partielle |
| **Détection orientation de l'objet** | ❌ | ✅ |
| **Détection glissement directionnel** | ✅ limité | ✅✅ |

---

### B.0 — Pré-requis : Clarification des deux questions distinctes

La question initiale portait sur deux sujets différents qui sont souvent confondus :

| Question | Sujet | Réponse dans |
|:---|:---|:---|
| **Q1** | 1 capteur MLX90393 par doigt (PCB 10×10mm) au lieu de 5 — impact sur les doigts ? | **Section B.1** |
| **Q2** | Utiliser plusieurs PCBs WowRobo (5 capteurs chacun) sur la paume — est-ce utile ? | **Section B.2** |

---

### B.1 — Conséquences du passage à 1 capteur par doigt (5 → 1)

#### Ce que perd-on avec 1 seul capteur par bout de doigt ?

En théorie, un array de 5 capteurs par doigt offre une meilleure **résolution spatiale**. Mais en pratique, pour une phalange distale de 12–15mm, le bilan est radicalement différent.

#### Le problème physique : le diaphonie magnétique (crosstalk)

Sur un bout de doigt de **12mm de large**, 5 aimants de Ø3mm espacés de 3–4mm se trouveraient à une distance les uns des autres inférieure à leur diamètre. La physique est implacable :

```
   Phalange distale (12mm de large) avec 5 aimants Ø3mm :
   
   ┌──────────────────────────────────┐
   │ ●   ●   ●   ●   ●               │  ← 5 aimants, espacement ~1.5mm entre bords
   │  ↘ ↗ ↘ ↗ ↘ ↗ ↘ ↗              │
   │   Champs magnétiques qui se      │
   │   CHEVAUCHENT et s'annulent !    │
   └──────────────────────────────────┘
   
   Résultat : chaque capteur MLX90393 mesure un mélange
   des champs de son propre aimant ET des 4 voisins.
   La mesure est corrompue et inutilisable sans calibration
   complexe spécifique à chaque capteur.
```

Le champ magnétique d'un aimant Ø3×1mm se propage sur un rayon de **5 à 8mm**. Avec 5 aimants sur 12mm, chaque capteur perçoit **3 à 4 aimants voisins simultanément**. C'est un problème connu (crosstalk matriciel) qui nécessite des matrices de découplage complexes ou des réseaux de neurones dédiés — pour un gain fonctionnel marginal sur une si petite surface.

#### Ce que conserve 1 seul capteur par bout de doigt

> [!IMPORTANT]
> **Un seul MLX90393 par bout de doigt donne 3 mesures indépendantes : Bx, By, Bz.**
> Ces 3 composantes suffisent pour reconstruire un **vecteur de force 3D complet**.

| Mesure | Ce qu'elle détecte | Utilité pour la préhension |
|:---|:---|:---|
| **Bz** (axial, normal) | Force de compression verticale | ⭐⭐⭐⭐⭐ Intensité de serrage |
| **Bx** (latéral) | Cisaillement horizontal | ⭐⭐⭐⭐⭐ Glissement gauche/droite |
| **By** (antéro-post.) | Cisaillement avant/arrière | ⭐⭐⭐⭐⭐ Glissement haut/bas |

**Ce que ces 3 valeurs permettent :**
- ✅ Détecter si l'objet est en contact ou non
- ✅ Mesurer la force de serrage (Bz)
- ✅ Détecter un glissement imminent (variation rapide de Bx/By)
- ✅ Estimer la direction du glissement
- ✅ Différencier contact latéral vs frontal

**Ce qu'on ne peut PAS faire avec 1 capteur :**
- ❌ Localiser précisément *où* sur la pulpe du doigt est le contact (pas de résolution spatiale)
- ❌ Distinguer 2 contacts simultanés sur la même pulpe

#### Verdict pour les doigts : 1 capteur est le BON choix

> [!NOTE]
> **Conclusion : Le passage à 1 capteur par bout de doigt n'est PAS une dégradation — c'est la solution physiquement correcte pour cette taille.**
>
> La recherche (eFlesh, ReSkin, AnySkin) utilise des arrays multi-capteurs sur des surfaces de **20×20mm minimum**. En dessous de cette taille, le crosstalk magnétique dégrade les mesures au point de rendre les capteurs supplémentaires inutiles voire contreproductifs.
>
> **Un seul capteur 3 axes sur la phalange distale est exactement ce qu'utilisent les systèmes tactiles commerciaux les plus performants** (ex: SynTouch BioTac, Digit-Tactip) pour les bouts de doigts de robots.

#### Tableau de synthèse : impact réel sur les capacités de la main

| Capacité de la main | Avec 5 cap./doigt (théorique) | Avec 1 cap./doigt (retenu) | Impact réel |
|:---|:---:|:---:|:---|
| Détection de contact | ✅ | ✅ | **Aucun** |
| Force de serrage | ✅✅ | ✅✅ | **Aucun** |
| Détection de glissement | ✅✅✅ | ✅✅ | **Mineur** (direction ± 30°) |
| Localisation du contact sur la pulpe | ✅ partielle | ❌ | Absent — mais non critique |
| Robustesse aux pannes | ✅✅ | ✅ | Moins de redondance |
| **Faisabilité physique** | ❌ (crosstalk) | ✅✅✅ | **Critique** |
| **Coût** | 5× | 1× | **-80%** |

---

### B.2 — Utiliser plusieurs PCBs WowRobo (5 capteurs chacun) sur la paume

#### La vraie question : 1 ou plusieurs PCBs WowRobo sur la paume ?

La paume humaine fait environ **60 × 80 mm** de surface de contact utile. Un seul PCB WowRobo (20×20mm avec 5 MLX90393) ne couvre qu'une zone de 20×20mm, soit environ **8% de la surface palmaire**.

```
   Vue de la paume (60×80mm) avec différentes configurations :

   OPTION A : 1 PCB (actuel)      OPTION B : 2 PCBs         OPTION C : 3 PCBs
   ┌──────────────────────┐       ┌──────────────────────┐  ┌──────────────────────┐
   │                      │       │  ┌────┐   ┌────┐     │  │  ┌────┐   ┌────┐   │
   │       ┌────┐         │       │  │PCB1│   │PCB2│     │  │  │PCB1│   │PCB2│   │
   │       │PCB1│         │       │  │ 5× │   │ 5× │     │  │  │ 5× │   │ 5× │   │
   │       │ 5× │         │       │  │cap.│   │cap.│     │  │  │cap.│   │cap.│   │
   │       │cap.│         │       │  └────┘   └────┘     │  │  └────┘   └────┘   │
   │       └────┘         │       │                       │  │                    │
   │                      │       │       ┌────┐          │  │       ┌────┐       │
   │  8% couverture       │       │       │    │ vide     │  │       │PCB3│       │
   │  5 capteurs          │       │  16%  │    │          │  │       │ 5× │       │
   │                      │       │  10 cap.   │          │  │  24%  │cap.│       │
   └──────────────────────┘       └──────────────────────┘  │  15 cap.   └────┘  │
                                                             └──────────────────────┘
```

#### Analyse coût/bénéfice de chaque configuration

| Config | PCBs utilisés | MLX90393 | Couverture | Capacités supplémentaires | PCBs spare restants |
|:---|:---:|:---:|:---:|:---|:---:|
| **A — 1 PCB/paume** | 2 (total) | 10 | ~8% | Contact grossier, force, orientation | **16 spare** |
| **B — 2 PCBs/paume** | 4 (total) | 20 | ~16% | + Localisation zone (avant/arrière paume) | **14 spare** |
| **C — 3 PCBs/paume** | 6 (total) | 30 | ~24% | + Détection de plusieurs contacts simultanés | **12 spare** |

#### Ce que l'ajout d'un 2ème et 3ème PCB apporte réellement

**2ème PCB WowRobo sur la paume (de Option A à Option B) :**
- Permet de distinguer un contact dans la **zone thénar** (base du pouce) vs **zone hypothénar** (côté auriculaire)
- Détecte si un objet touche simultanément deux zones distinctes de la paume
- Indispensable pour les objets longs (stylo, tube) où l'orientation est critique
- **Gain pratique : élevé** pour les tâches de manipulation fine

**3ème PCB WowRobo sur la paume (de Option B à Option C) :**
- Ajoute la zone centrale de la paume (voûte)
- Permet une triangulation plus précise de la position du contact
- **Gain pratique : modéré** — la différence est surtout utile pour des tâches de recherche avancée

#### Recommandation finale paume

> [!IMPORTANT]
> **La recommandation est de passer à 2 PCBs WowRobo par paume (Option B).**
>
> Avec votre stock de 20 PCBs, utiliser 4 pour les paumes (2 par paume) au lieu de 2 n'impacte pas significativement les autres usages : vous aurez encore 14 spare après paumes + pieds + avant-bras + torse.

**Disposition recommandée des 2 PCBs sur la paume (60×80mm) :**

```
              ← 60mm →
         ┌────────────────────┐  ↑
         │  ┌────┐   ┌────┐   │  │
         │  │PCB1│   │PCB2│   │  │  80mm
         │  │Méta│   │Zone│   │  │
         │  │carpes   thénar  │  │
         │  └────┘   └────┘   │  │
         │                    │  │
         └────────────────────┘  ↓
              ↑ 5 doigts
```
- **PCB 1** — Zone métacarpienne (bas des doigts 2–4) : 20mm d'offset depuis la base des doigts
- **PCB 2** — Zone thénar/hypothénar (base du pouce et côté auriculaire) : symétrique

#### Bilan PCBs révisé avec 2 PCBs/paume

| Emplacement | PCBs |
|:---|:---:|
| Paumes (×2, 2 PCBs chacune) | **4** |
| Pieds (×2, 4 PCBs chacun) | **8** |
| Avant-bras (×2) | **2** |
| Torse | **2** |
| **Sous-total utilisé** | **16** |
| **Spare** | **4** |
| **Total** | **20** |

> [!TIP]
> Avec 4 spare (au lieu de 6 précédemment), vous avez encore une marge confortable pour remplacer des PCBs endommagés. Et la paume devient bien plus capable.

#### Adressage I2C avec 2 PCBs WowRobo sur la même paume

Les 5 MLX90393 de chaque PCB WowRobo partagent des adresses fixes internes. Avec 2 PCBs sur le même bus I2C, il y a **conflit d'adresses**. Solutions :

1. **Solution simple — Bus I2C séparés :** PCB1 paume sur Bus I2C N°1 de l'ESP32-S3, PCB2 paume sur Bus I2C N°2 (le bus pouce est alors sur Bus N°1 en parallèle — OK si < 4 adresses par bus)
2. **Solution robuste — Multiplexeur TCA9548A** : Un seul composant (TSSOP-24, ~1€ chez JLCPCB) crée 8 canaux I2C isolés. 1 canal par PCB WowRobo → aucun conflit possible

---

## 4. Partie C — IMU vs Capteurs Plantaires : La Fausse Alternative {#4-imu-vs-pied}

### Question posée

> *Si le robot dispose déjà d'un IMU pour l'équilibre, les capteurs plantaires (PCBs WowRobo dans les semelles) apportent-ils encore de la valeur ?*

### Réponse directe

> [!IMPORTANT]
> **OUI, les capteurs plantaires sont indispensables même avec un IMU. L'IMU et les capteurs plantaires ne font PAS la même chose — ils sont complémentaires et irremplaçables l'un par l'autre.**

### Explication : Ce que mesure chaque capteur

| Capteur | Ce qu'il mesure | Ce qu'il NE mesure PAS |
|:---|:---|:---|
| **IMU** | Orientation et accélération du **corps** (torse) | Ce qui se passe sous les pieds |
| **Capteurs plantaires** | Forces au point de **contact sol** | L'orientation globale du corps |

### L'analogie parfaite : l'oreille interne vs les pieds

Imaginez un homme debout les yeux fermés :
- Son **oreille interne** (= IMU) lui dit qu'il penche légèrement à gauche
- Ses **pieds** (= capteurs plantaires) lui disent que tout le poids est sur l'avant du pied droit

**Avec seulement l'oreille interne**, il sait qu'il penche mais ne sait pas **où** il doit appliquer la correction — sur quelle cheville, dans quelle direction du pied.

**Avec les deux**, le cerveau sait exactement : "je penche à gauche, le CoP est sur l'avant-droit, je dois contracter la cheville droite-talon et relâcher la gauche-avant".

### Limitations critiques de l'IMU seul

#### 1. Dérive gyroscopique (IMU drift)

Un gyroscope drift d'environ **1 à 5°/heure** en conditions normales. Sur un sol irrégulier avec des vibrations de moteurs, cette dérive peut atteindre **5 à 15°/heure**. Pour un robot bipède en marche continue :

- Après **10 minutes de marche** → erreur d'attitude de **0.8 à 2.5°**
- À 40kg de masse corporelle, une erreur de **1.5°** se traduit par un **moment déstabilisant de ~10 N·m** sur la hanche

Les capteurs plantaires fournissent une **référence absolue au sol** (le CoP calculé ne drift pas) qui permet de corriger cette dérive.

#### 2. Terrain non-plat et obstacles sous le pied

L'IMU mesure l'orientation du **torse**, pas de la semelle. Sur un sol incliné de 5° ou avec un caillou sous le talon :
- L'IMU voit le torse pencher — mais ne sait pas si c'est normal (montée de marche) ou anormal (chute imminente)
- Le capteur plantaire voit immédiatement que le **talon est sur-chargé** ou que le **CoP est hors de la zone de stabilité** → déclenchement d'un réflexe de cheville

#### 3. Phase d'envol (swing phase)

Pendant la phase d'envol d'une jambe (le pied n'est pas au sol) :
- L'IMU continue de mesurer l'accélération, mais la **jambe volante perturbe la mesure** (son inertie s'additionne au torse)
- Le capteur plantaire de la **jambe d'appui** confirme que 100% du poids est sur ce pied → le contrôleur peut donc calculer précisément le point de pivot

#### 4. Détection de glissement

Un glissement de semelle (chute de μ sur carrelage mouillé) n'est **pas détectable par un IMU** avant que le centre de masse ne commence à chuter (délai de 200–500ms). Les capteurs plantaires détectent le glissement en **< 10ms** via le changement du vecteur de cisaillement horizontal (Bx, By).

### Ce que les capteurs plantaires apportent concrètement

| Apport | Sans capteurs plantaires (IMU seul) | Avec capteurs plantaires |
|:---|:---|:---|
| **Centre de Pression (CoP)** | Estimé par modèle dynamique (imprécis) | Mesuré directement (précis à ±5mm) |
| **ZMP (Zero Moment Point)** | Calculé par simulation | Validé par mesure réelle |
| **Détection glissement** | Après 200–500ms (chute déjà amorcée) | En **< 10ms** (réflexe préventif) |
| **Terrain irrégulier** | Compensation uniquement par modèle | Adaptation terrain réelle |
| **Phase de contact** | Estimée (pas toujours fiable) | Mesurée exactement |
| **Corrections IMU drift** | Non disponible | Recalibration absolue au sol |

### Verdict final

> [!NOTE]
> **L'IMU est le "système vestibulaire" du robot (équilibre global, orientation dans l'espace).**
> **Les capteurs plantaires sont les "récepteurs proprioceptifs plantaires" (ce qui se passe exactement sous chaque pied).**
> 
> Tous les robots bipèdes de référence — Boston Dynamics Atlas, Agility Robotics Digit, Unitree H1, Figure 01 — utilisent **les deux types de capteurs simultanément**. Il n'existe pas de robot bipède performant qui utilise un IMU sans retour de force au sol.

**Conséquence pratique pour le D-Bot :** Les 8 PCBs WowRobo prévus pour les semelles (4 par pied) apportent une valeur **critique et non substituable** par l'IMU.

---

## 5. Partie D — Plan Complet de Recyclage des 20 PCBs WowRobo {#5-recyclage}

### 5.1 Vue d'Ensemble

**Stock disponible : 20 PCBs WowRobo** (20×20mm, 5× MLX90393 chacun)

#### Répartition finale recommandée

| # | Emplacement | PCBs | MLX90393 | Aimants Ø3×1mm | Priorité |
|:---|:---|:---:|:---:|:---:|:---:|
| 1 | Paume Main Droite | 1 | 5 | 5 | 🥈 |
| 2 | Paume Main Gauche | 1 | 5 | 5 | 🥈 |
| 3 | Semelle Pied Droit | 4 | 20 | 20 | 🥇 |
| 4 | Semelle Pied Gauche | 4 | 20 | 20 | 🥇 |
| 5 | Avant-bras Droit | 1 | 5 | 5 | 🥉 |
| 6 | Avant-bras Gauche | 1 | 5 | 5 | 🥉 |
| 7 | Poitrine/Torse | 2 | 10 | 10 | 4 |
| **Spare/Réserve** | — | **6** | 30 | — | — |
| **TOTAL** | | **20** | **100** | **70** | |

> [!WARNING]
> **Aimants nécessaires :** 70 aimants Ø3×1mm au total. Vérifiez votre stock et commandez le complément si nécessaire. Référence Supermagnete (France) : **S-03-01-N** (aimant néodyme N48, Ø3×1mm, ~0.17€/pièce). Lien : [supermagnete.fr](https://www.supermagnete.fr/aimants-ronds-neodyme/aimant-rond-s-03-01-n_S-03-01-N)

---

### 5.2 Priorité 1 — Semelle Plantaire Tactile (8 PCBs, 2 pieds)

#### Architecture de la semelle

La plaque plantaire en carbone mesure **120 × 80 mm** — suffisant pour 4 PCBs de 20×20mm.

```
         ┌─────────────────────────────────────────────┐
         │           PLAQUE CARBONE 120×80mm           │
         │                        (vue de dessous)     │
         │                                              │
         │   ┌─────────┐              ┌─────────┐      │
         │   │ PCB #3  │              │ PCB #4  │      │
         │   │ Métatarse│             │ Métatarse│     │  ← AVANT-PIED
         │   │ Médial  │              │ Latéral │      │
         │   │ (Ø gros │              │ (Ø petit│      │
         │   │  orteil)│              │  orteil)│      │
         │   └─────────┘              └─────────┘      │
         │                                              │
         │             ┌────────────┐                  │
         │             │  PCB #2    │                  │
         │             │ Voûte      │                  │  ← MILIEU
         │             │ plantaire  │                  │
         │             └────────────┘                  │
         │                                              │
         │             ┌────────────┐                  │
         │             │  PCB #1    │                  │
         │             │  Talon     │                  │  ← ARRIÈRE
         │             │ (Calcanéum)│                  │
         │             └────────────┘                  │
         │                                              │
         └─────────────────────────────────────────────┘
              Avant-pied ↑                ↑ Talon
```

#### Coupe transversale de la semelle tactile

```
Surface de contact (sol)
        ↕
┌───────────────────────────────────────────┐ ← Pads TPU (Shore 95A/85A)
│  TPU gyroïde 8%  +  20× aimants Ø3×1mm  │   5–8mm d'épaisseur
│  (noyés dans le TPU en face des capteurs)│
├───────────────────────────────────────────┤
│         Air-gap : 3–4 mm                 │   (espace libre / mousse souple)
├───────────────────────────────────────────┤
│  4× PCBs WowRobo collés sur le carbone   │   face capteurs vers le haut
│  (MLX90393 regardent vers le haut)       │
├───────────────────────────────────────────┤
│  Plaque carbone 3mm (ossature plantaire)  │
└───────────────────────────────────────────┘
        ↕
Sole extérieure (contact direct avec le sol) — optionnellement protégée par un pad antidérapant
```

#### Informations de fabrication semelle

| Élément | Spécification |
|:---|:---|
| **Aimants dans TPU** | 20× Ø3×1mm, 1 par capteur, face aimantée Nord vers le bas (vers le capteur) |
| **Hauteur totale ajoutée** | 5mm (TPU) + 4mm (air-gap) + 1.6mm (PCB) + 3mm (carbone) = **13.6mm** total semelle |
| **Masse ajoutée par pied** | ~8g (PCBs) + ~1g (aimants) + ~15g (TPU étendu) + ~5g (câbles) = **~29g/pied** |
| **Câblage** | 4 câbles I2C JST-SH 4 broches (1.0mm) par pied, longueur 200–300mm, remontent dans le tibia |
| **ESP32-S3 pied** | Fixé dans le bas du tibia (boîtier imprimé PA12-CF), 1 par pied |

#### Adressage I2C des 4 PCBs par pied

Chaque PCB WowRobo a déjà ses 5 MLX90393 avec des adresses I2C fixes configurées en usine (0x0C, 0x0D, 0x0E, 0x0F, 0x18 selon le modèle). Utilisez **2 bus I2C** de l'ESP32-S3 :

```
          ESP32-S3 Pied (dans le tibia)
          ┌──────────────────────────────┐
          │   Bus I2C #1 (GPIO 1/2)      │──── PCB#1 (Talon) + PCB#2 (Voûte)
          │   Bus I2C #2 (GPIO 5/6)      │──── PCB#3 (Méta Médial) + PCB#4 (Méta Latéral)
          └──────────────────────────────┘
```

> Note : Si les adresses des capteurs d'un même PCB WowRobo entrent en conflit avec ceux d'un autre PCB sur le même bus, utilisez un **multiplexeur TCA9548A** (8 canaux I2C, boîtier TSSOP-24, disponible chez JLCPCB). Une alternative simple est d'utiliser les **4 bus I2C logiciels** de l'ESP32-S3 via `Wire` et `Wire1`.

---

### 5.3 Priorité 2 — Paumes des Mains (2 PCBs)

*Référence : GUIDE_COMPLET_Fabrication_et_Montage_DHand_V1.md §5.3*

Usage prévu par eFlesh (Pinto Lab, NYU). Le PCB s'intègre dans l'évidement de 20×20mm du bloc de paume PA12-CF.

Configuration des aimants (1 par capteur) :
- Aimants Ø3×1mm noyés dans la gaine TPU de la paume
- Air-gap nominal : 3–4mm
- Les 5 aimants sont disposés en miroir des 5 capteurs (croix : centre + 4 cardinaux)

Valeur apportée : détection de contact palmar, force et cisaillement, détection d'orientation de l'objet saisi.

---

### 5.4 Priorité 3 — Avant-bras (2 PCBs)

**Fonction : Sécurité HRI (Human-Robot Interaction) et détection de collision**

Intégration :
- Collé sous la coque avant-bras en PA12-CF ou TPU
- 5 aimants Ø3×1mm noyés dans un pad TPU de 5mm d'épaisseur sur l'avant de l'avant-bras
- Câble I2C remonte vers le bus ESP32-S3 du bras

Usage typique :
- Le robot "sent" un contact humain volontaire → comportement coopératif
- Collision non voulue avec un obstacle → réflexe de retrait
- Enrichissement du dataset RL pour l'apprentissage de la manipulation

---

### 5.5 Priorité 4 — Torse / Poitrine (2 PCBs)

**Fonction : Détection de collision frontale et interaction physique**

Intégration :
- Intégrés sous la plaque thoracique (PA12-CF ou composite carbone)
- Pad TPU souple de 8mm (Shore 85A) sur la poitrine
- Câble I2C vers le hub central (Jetson ou ESP32-S3 dédié torse)

Usage :
- Protection des composants internes (batterie, CPU) lors des chutes
- Détection d'appui volontaire (l'humain pose la main sur le torse pour guider le robot)
- Données de contact pour l'apprentissage de comportements sociaux

---

## 6. Architecture I2C Globale du Robot {#6-i2c-global}

### Topologie complète des capteurs tactiles MLX90393

```
                              ┌──────────────────────┐
                              │      JETSON (USB CDC) │
                              └───────────────────────┘
                                        │ USB
              ┌─────────────────────────┴──────────────────────────┐
              │                                                      │
    ┌─────────┴──────┐                                   ┌──────────┴──────┐
    │ ESP32-S3       │                                   │ ESP32-S3        │
    │ MAIN DROITE    │                                   │ MAIN GAUCHE     │
    │ (Bus I²C ×2)   │                                   │ (Bus I²C ×2)   │
    │                │                                   │                 │
    │ Bus1: 4 doigts │                                   │ Bus1: 4 doigts  │
    │ Bus2: pouce    │                                   │ Bus2: pouce     │
    │        + paume │                                   │        + paume  │
    └────────────────┘                                   └─────────────────┘
              │                                                      │
    ┌─────────┴──────┐                                   ┌──────────┴──────┐
    │ ESP32-S3       │                                   │ ESP32-S3        │
    │ PIED DROIT     │                                   │ PIED GAUCHE     │
    │ (dans tibia D) │                                   │ (dans tibia G)  │
    │                │                                   │                 │
    │ Bus1: Talon    │                                   │ Bus1: Talon     │
    │      + Voûte   │                                   │      + Voûte    │
    │ Bus2: Méta Med │                                   │ Bus2: Méta Med  │
    │      + Méta Lat│                                   │      + Méta Lat │
    └────────────────┘                                   └─────────────────┘
              │ USB                                                │ USB
              └───────────────────┬────────────────────────────────┘
                                  │
                         ┌────────┴────────┐
                         │  ESP32-S3 TORSE │
                         │  Avant-bras D/G │
                         │  + Poitrine     │
                         └─────────────────┘
                                  │ USB
                              JETSON
```

### Bilan global des capteurs MLX90393 sur le robot

| Sous-système | PCBs WowRobo | PCBs custom 10×10mm | MLX90393 total |
|:---|:---:|:---:|:---:|
| Doigts mains (5+5) | 0 | **10** | 10 |
| Paumes (×2) | 2 | 0 | 10 |
| Pieds semelles (×2) | 8 | 0 | 40 |
| Avant-bras (×2) | 2 | 0 | 10 |
| Torse | 2 | 0 | 10 |
| **TOTAL** | **14** | **10** | **80** |

### Ressources logicielles

- **Firmware ESP32-S3** : Dépôt eFlesh `/arduino` — compatible multi-bus, multi-capteurs
- **Driver MLX90393** : [Adafruit_MLX90393](https://github.com/adafruit/Adafruit_MLX90393)
- **Fréquence d'acquisition** : 100 Hz par bus I2C (configuration ODR du MLX90393)
- **Protocole** : USB CDC → Jetson → ROS2 topic `/tactile/[location]/[sensor_id]`

---

*Document généré juin 2026 — À mettre à jour après réception et test des PCBs JLCPCB.*  
*Références : GUIDE_COMPLET_Fabrication_et_Montage_DHand_V1.md §5.3 | FINAL_CONSOLIDE_Jambes_et_Pieds.md §3*

---

## 7. Partie E — Quel Aimant pour Quel Emplacement ? {#7-aimants}

> *Analyse physique complète des 3 types d'aimants disponibles (Supermagnete) appliquée aux emplacements du robot.*

### E.1 — Inventaire et Caractéristiques des Aimants

| Référence | Forme | Dimensions | Grade | Br (T) | Force pull | Qté |
|:---|:---|:---|:---:|:---:|:---:|:---:|
| **S-03-01-N** | Disque | Ø3mm × 1mm | N48 | 1.43 T | 190 g | 40 |
| **S-08-03-N** | Disque | Ø8mm × 3mm | N45 | 1.34 T | 1.5 kg | 40 |
| **W-05-N** | Cube | 5×5×5mm | N42 | 1.32 T | 1.1 kg | 10 |

> [!NOTE]
> La force "pull" indiquée par Supermagnete est la force d'attraction au contact direct (air-gap = 0). Elle **n'est pas** la force exercée à la distance de travail (3–10mm). Ce qui compte ici est le **champ magnétique Bz à distance de travail**, calculé ci-dessous.

---

### E.2 — Rappel : Plages Utiles du MLX90393 (Gain Programmable)

Le MLX90393 a un gain **entièrement programmable** via le registre `GAIN_SEL`. Cela change la plage de mesure :

| GAIN_SEL | Sensibilité XY (µT/LSB) | Plage ≈ XY | Sensibilité Z (µT/LSB) | Plage ≈ Z |
|:---:|:---:|:---:|:---:|:---:|
| 0 (max) | 0.805 | ±26 mT | 1.468 | ±48 mT |
| 2 (défaut) | 0.483 | ±16 mT | 0.881 | ±29 mT |
| 4 | 0.322 | ±11 mT | 0.587 | ±19 mT |
| 5 | 0.268 | ±9 mT | 0.489 | ±16 mT |
| **7 (min)** | **0.161** | **±5 mT** | **0.294** | **±10 mT** |

> [!WARNING]
> Ces valeurs correspondent à **RES=0** (résolution standard 16 bits). Si vous passez en RES=1 ou RES=2 (oversampling), les valeurs µT/LSB doublent ou quadruplent — la résolution de mesure s'améliore mais la plage se réduit.
>
> **Règle d'or :** Le champ magnétique au repos (aimant non comprimé) doit être dans la **plage 10–40% du plein fond d'échelle** pour laisser de la marge lors de la déflexion.

En pratique, les 3 plages utiles pour notre système :
- **GAIN_SEL=2** (défaut Adafruit) → plage utile Bz ≈ **±29 mT** → bon pour champs faibles (S-03-01-N à 3-4mm)
- **GAIN_SEL=5** → plage utile Bz ≈ **±16 mT** → bon pour champs forts avec reconfiguration
- **GAIN_SEL=7** (min gain) → plage utile Bz ≈ **±10 mT** mais XY très sensible → à éviter pour notre usage

Repère de saturation effectif pour le calcul : **~50 mT** correspond à la limite haute sûre avec GAIN_SEL entre 2 et 5.

---

### E.3 — Calcul du Champ Magnétique par Aimant et par Distance

> *Formule utilisée : B(z) = (Br/2) × [(z+L)/√(R²+(z+L)²) − z/√(R²+z²)], aimant disque ou cube équivalent.*

#### Tableau complet Bz(mT) vs distance air-gap

```
                         AIR-GAP (distance aimant → surface capteur MLX90393)
Aimant               2mm    3mm    4mm    5mm    6mm    7mm    8mm   10mm   12mm
─────────────────────────────────────────────────────────────────────────────────
S-03-01-N Ø3×1mm    68     30     15      9      5      4      3      1      1
  (N48, Br=1.43T)   ✅G7   ✅OK   ✅OK   ✅OK   ⚠️W   ⚠️W   ⚠️W   ⚠️W   ⚠️W

S-08-03-N Ø8×3mm   224    155    108     76     55     40     30     18     12
  (N45, Br=1.34T)   ❌SAT  ⚠️H   ⚠️H   ⚠️H   ✅G7   ✅G7   ✅OK  ✅OK  ✅OK

W-05-N Cube 5mm    230    142     90     60     42     30     23     13      9
  (N42, Br=1.32T)   ❌SAT  ⚠️H   ⚠️H   ✅G7   ✅OK   ✅OK   ✅OK  ✅OK  ✅OK
─────────────────────────────────────────────────────────────────────────────────
LÉGENDE :
  ❌SAT   Sature le MLX90393 (> ~210 mT), signal invalide, à proscrire
  ⚠️H    Nécessite GAIN_SEL ≥ 5 pour ne pas saturer (> 50 mT)
  ✅G7    Idéal GAIN_SEL=7 (plage ~30-70 mT), très bon signal dynamique
  ✅OK    Idéal GAIN_SEL=2 défaut (plage ~10-30 mT), fonctionnement optimal
  ⚠️W    Champ trop faible (< 5 mT), rapport signal/bruit insuffisant
```

---

### E.4 — Recommandation par Emplacement

#### 🖐 Bouts de Doigts — Phalanges Distales (air-gap TPU : 3–4 mm)

| Aimant | Bz @3mm | Bz @4mm | Verdict |
|:---|:---:|:---:|:---|
| **S-03-01-N** ✅ | **30 mT** | **15 mT** | ✅ **PARFAIT** — signal au cœur de la plage, GAIN_SEL=2 défaut |
| W-05-N ❌ | 142 mT | 90 mT | ❌ Sature avec n'importe quel gain — physiquement inadapté |
| S-08-03-N ❌ | 155 mT | 108 mT | ❌ Sature avec n'importe quel gain — physiquement inadapté |

> [!IMPORTANT]
> **Doigts → uniquement S-03-01-N (Ø3×1mm).** Les grands aimants sont physiquement incompatibles avec un air-gap de 3–4mm sur un bout de doigt : ils saturent le capteur à 100% et la mesure est invalide.

**Configuration :** 1 aimant S-03-01-N par doigt, noyé dans le capuchon TPU, face Nord vers le capteur. Air-gap TPU nominal 3.5mm. GAIN_SEL=2 (défaut Adafruit).

---

#### ✋ Paume (2 PCBs WowRobo, air-gap TPU : 5–7 mm)

| Aimant | Bz @5mm | Bz @7mm | Verdict |
|:---|:---:|:---:|:---|
| S-03-01-N ⚠️ | 9 mT | 4 mT | ⚠️ Trop faible à partir de 6mm, SNR marginal |
| **W-05-N** ✅ | **60 mT** | **30 mT** | ✅ **IDÉAL** — signal fort, plage optimale, cube facile à coller |
| S-08-03-N ⚠️ | 76 mT | 40 mT | ✅ Utilisable mais nécessite GAIN_SEL ajusté + risque si TPU se comprime |

> [!IMPORTANT]
> **Paume → W-05-N (cube 5mm).** Le cube a l'avantage d'une face plane facile à coller dans le TPU. À 5–7mm d'air-gap, il fournit un signal entre 30 et 60 mT — au centre de la plage utile avec GAIN_SEL=7. Vous avez exactement 10 cubes pour les 10 positions (2 PCBs × 5 capteurs × 2 mains) — **parfaite adéquation stock/besoin.**

**Configuration :** 1 cube W-05-N par capteur MLX90393 (10 cubes total pour les 2 paumes), noyé dans la couche TPU palmaire (Shore 85A), face magnétique vers le capteur. Air-gap nominal 6mm. GAIN_SEL=7 (faible gain).

---

#### 🦶 Semelle Plantaire (4 PCBs WowRobo par pied, air-gap variable selon charge)

C'est le cas le plus complexe : le TPU **se comprime** sous le poids du robot.

```
  État du pied         Air-gap TPU    Champ S-03-01-N   Champ S-08-03-N   Champ W-05-N
  ──────────────────   ────────────   ───────────────   ───────────────   ────────────
  Sans charge (debout)    8 mm           3 mT ⚠️W          30 mT ✅OK        23 mT ✅OK
  Mi-charge (marche)      5 mm           9 mT ✅OK          76 mT ⚠️H        60 mT ✅G7
  Pleine charge (impact) 2-3 mm         30-68 mT ✅        155 mT ⚠️H       142 mT ⚠️H
```

**Analyse :**
- **S-03-01-N** sans charge : signal de seulement **3 mT** → proche du bruit → **impossible de détecter si le pied est posé ou en l'air**
- **S-08-03-N** sans charge : **30 mT** → signal clair → on sait que le pied existe même sans pression
- **S-08-03-N** en pleine charge : **155 mT** → nécessite GAIN_SEL ajusté, mais **mesurable** avec GAIN_SEL=7 (plage ±210 mT)
- **W-05-N** en pleine charge : **142 mT** → similaire, borderline mais mesurable

> [!IMPORTANT]
> **Semelle plantaire → S-08-03-N (Ø8×3mm).** C'est le seul aimant qui maintient un **signal utilisable à l'état non-chargé** (pied en l'air pendant la phase swing) tout en restant dans la plage du capteur à pleine charge. Le S-03-01-N est trop faible au repos.
>
> **Réglage GAIN_SEL :** Utiliser GAIN_SEL=5 ou 6 (plage ~50–130 mT) pour couvrir le spectre complet sans-charge/pleine-charge. Le firmware devrait idéalement auto-calibrer le gain à l'initialisation selon la charge au sol.

**Configuration :** 1 aimant S-08-03-N par capteur (20 aimants par pied, 40 total pour 2 pieds). Air-gap TPU nominal 7–8mm. GAIN_SEL=5 (plage ajustée pour couvrir 30→130 mT).

> [!WARNING]
> 40 aimants S-08-03-N consomment votre **stock complet** de ce type. Prévoyez 5–10 pièces supplémentaires en spare (0.31€/pièce).

---

#### 💪 Avant-bras (1 PCB WowRobo par bras, air-gap TPU : 3–5 mm)

| Aimant | Bz @4mm | Verdict |
|:---|:---:|:---|
| **S-03-01-N** ✅ | **15 mT** | ✅ Parfait — même configuration que les doigts |

**Configuration :** 5 aimants S-03-01-N par avant-bras (10 total), TPU 4mm, GAIN_SEL=2.

---

#### 🫁 Torse / Poitrine (2 PCBs WowRobo, air-gap TPU : 6–8 mm)

| Aimant | Bz @7mm | Verdict |
|:---|:---:|:---|
| **S-08-03-N** ✅ | **40 mT** | ✅ Signal fort même avec TPU épais (protection thoracique) |
| W-05-N | 30 mT | ✅ Utilisable si vous manquez de S-08-03-N (cubes déjà alloués à la paume) |

**Configuration :** 10 aimants S-08-03-N (ou W-05-N) pour le torse, TPU 7mm, GAIN_SEL=7.

---

### E.5 — Tableau Récapitulatif Final

| Emplacement | Aimant recommandé | Air-gap | GAIN_SEL | Bz repos | Aimants utilisés |
|:---|:---|:---:|:---:|:---:|:---:|
| Doigts ×10 (5/main×2) | **S-03-01-N** Ø3×1mm | 3.5 mm | 2 (défaut) | ~25 mT | **10** |
| Paume ×2 (×5 cap.) | **W-05-N** Cube 5mm | 6 mm | 7 | ~42 mT | **10** |
| Pieds ×2 (×20 cap.) | **S-08-03-N** Ø8×3mm | 7–8 mm | 5 | ~30 mT | **40** |
| Avant-bras ×2 (×5 cap.) | **S-03-01-N** Ø3×1mm | 4 mm | 2 (défaut) | ~15 mT | **10** |
| Torse ×1 (×10 cap.) | **S-08-03-N** Ø8×3mm | 7 mm | 7 | ~40 mT | **10** |

#### Bilan stock aimants

| Référence | Stock | Utilisés | Spare |
|:---|:---:|:---:|:---:|
| S-03-01-N (Ø3×1mm) | 40 | 10 (doigts) + 10 (avant-bras) = **20** | **20** ✅ |
| S-08-03-N (Ø8×3mm) | 40 | 40 (pieds) + 10 (torse) = **50** | **-10** ⚠️ Commander 10 supplémentaires |
| W-05-N (Cube 5mm) | 10 | 10 (paumes) = **10** | **0** — stock exact |

> [!WARNING]
> **Il manque 10 aimants S-08-03-N** pour compléter le système (40 pieds + 10 torse = 50, stock = 40). Commandez 10 à 15 pièces supplémentaires chez Supermagnete (ref S-08-03-N, ~0.31€/pièce).
>
> **Alternative :** Utiliser les W-05-N en spare sur le torse (à 7mm, ils fournissent 30 mT, acceptable avec GAIN_SEL=7). Dans ce cas, le stock S-08-03-N suffit pour les pieds uniquement.
