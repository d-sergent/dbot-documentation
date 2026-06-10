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
   - [Génération CAO et fabrication eFlesh Custom](#26-eflesh-cad)
3. [Partie B — Analyse : 1 ou 5 capteurs ?](#3-analyse-paume)
4. [Partie C — IMU vs Capteurs Plantaires : la fausse alternative](#4-imu-vs-pied)
5. [Partie D — Plan complet de recyclage des 20 PCBs WowRobo](#5-recyclage)
6. [Architecture I2C globale du robot](#6-i2c-global)
7. [**Partie E — Quel aimant pour quel emplacement ?**](#7-aimants) ⭐ *Nouveau*
   - [E.1 — Inventaire et Caractéristiques des Aimants](#e1-inventaire)
   - [E.2 — Rappel : Plages Utiles du MLX90393](#e2-plages)
   - [E.3 — Calcul du Champ Magnétique par Distance](#e3-calculs)
   - [E.4 — Recommandation par Emplacement](#e4-reco)
   - [E.5 — Tableau Récapitulatif Final](#e5-recap)
   - [E.6 — Risque de Démagnétisation Thermique (TPU chaud)](#e6-thermique)

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

### 2.6 — Procédure Hybride de Génération CAO et Fabrication eFlesh Custom {#26-eflesh-cad}

Le framework open-source **eFlesh** (développé par le Pinto Lab de NYU) fournit un outil de CAO algorithmique pour générer des capteurs tactiles s'adaptant à n'importe quelle géométrie convexe (comme le bout d'un doigt custom pour la main DHand V1).

> [!CAUTION]
> **Pourquoi la microstructure cut-cell est INDISPENSABLE (et l'infill slicer INTERDIT) dans la zone tactile :**
>
> La microstructure cut-cell d'eFLESH n'est **pas** un simple remplissage. C'est une **lattice paramétrique ingénieurée** qui remplit 3 rôles impossibles à reproduire par un infill gyroïde ou grille standard du slicer :
>
> 1. **Isotropie de déformation** : Un gyroïde ou un grid-infill standard a une rigidité fortement anisotrope (le comportement mécanique varie selon l'axe de la force appliquée — typiquement 2× à 3× plus rigide en Z qu'en XY). Les cut-cells sont conçues pour donner une **réponse isotrope** identique en X, Y et Z, ce qui est critique pour la mesure 3 axes du MLX90393. Sans cela, les composantes Bx et By du champ magnétique sont biaisées et la force de cisaillement est mal estimée (erreur de 30 à 60%).
> 2. **Contrôle du déplacement de l'aimant** : La lattice cut-cell guide le mouvement de l'aimant de manière prédictible et reproductible. Chaque cellule agit comme un micro-ressort calibré. Le réseau de neurones MLP de reconstruction de force (fourni dans le dépôt eFLESH) est entraîné *spécifiquement* sur cette réponse mécanique. Utiliser un infill slicer reviendrait à changer la suspension d'une voiture sans recalibrer l'ABS.
> 3. **Variation spatiale de rigidité** : Via le paramètre `E` (module d'Young) couche par couche dans `cut-cell.ipynb` (`def young(k)`), on peut rendre la zone directement sous l'aimant plus souple (meilleure sensibilité) et les zones périphériques plus rigides (meilleur maintien structurel).

#### Problématique de la pièce TPU du doigt D-Hand

La pièce TPU complète du doigt a **plusieurs fonctions distinctes** :

```
       Vue latérale de la gaine TPU du doigt (coupe)
       
       ┌──────────────────────────────────┐
       │  ZONE C — Ongle / Dos du doigt   │  ← Infill 100% solide
       │  (rigidité, rappel élastique)     │     (PAS de microstructure)
       ├──────────────────────────────────┤
       │  ZONE B — Logement phalange      │  ← Canal d'insertion PA12-CF
       │  PA12-CF + glissière PCB         │     Infill 100% solide
       ├──────────────────────────────────┤
       │  ZONE A — Pulpe tactile          │  ← MICROSTRUCTURE CUT-CELL
       │  (aimant + lattice eFlesh)        │     Générée par le pipeline
       │  ┌─ Peau lisse extérieure ─┐     │
       │  │ ┌── Cut-cell lattice ──┐│     │
       │  │ │  ┌── Poche aimant ──┐││     │
       │  │ │  │   ●  S-03-01-N   │││     │
       │  │ │  └──────────────────┘││     │
       │  │ └──────────────────────┘│     │
       │  └─────────────────────────┘     │
       └──────────────────────────────────┘
            ↓ Face vers le magnétomètre (PCB)
```

**Le défi** : Respecter la microstructure cut-cell dans la **Zone A** (seule zone tactile) tout en conservant un infill 100% solide dans les **Zones B et C** (structurelles), le tout en **une seule pièce monolithique**.

---

#### A. Le Pipeline Officiel eFLESH en 4 Stages

Le processus CAD2eFlesh se décompose en **4 étapes séquentielles** :

##### Stage 1 — CAD-to-Lattice (Notebook `cut-cell.ipynb`)

Convertit la géométrie d'entrée (OBJ/STL) en lattice de microstructures cut-cell.

> [!IMPORTANT]
> **Contrainte d'entrée :** L'outil exige un mesh d'entrée **convexe**. La gaine complète du doigt (concave, avec logement PA12-CF) ne peut PAS être traitée directement. → Solution : extraire uniquement la géométrie de la Zone A (pulpe) en volume convexe simplifié.

##### Stage 2 — Ajout des Poches d'Aimants (Blender ou TinkerCAD)

Creuse dans la lattice les cavités cylindriques pour les aimants.

**Deux méthodes :**
- **Option 1 — Blender** (recommandée pour la précision) :
  ```bash
  blender -b -P create_pouch.py
  ```
  Paramètres dans `create_pouch.py` :
  ```python
  input_path = "/path/to/lattice_output.obj"
  output_path = "/path/to/lattice_with_pouch.obj"
  list_of_magnets = [
      [3.2, 1.1, [X_center, Y_center, Z_center]],
      # [diamètre_pouce_mm, profondeur_mm, [X, Y, Z_du_centre]]
  ]
  ```
- **Option 2 — TinkerCAD** (méthode en ligne, plus simple) :
  Utilisez le workplane TinkerCAD partagé dans le dépôt (ne pas éditer l'original, faire une copie).

##### Stage 3 — Ajout du Slot (logement PCB)

Ajout de la fente d'insertion pour le PCB magnétomètre (10×10mm custom ou glissière pour le câble FPC).

##### Stage 4 — Tranchage et Impression 3D (OrcaSlicer)

Le STL final généré est tranché et imprimé en TPU 95A.

---

#### B. La Peau Lisse Extérieure : Pipeline eFLESH vs. Post-opération Fusion 360

> [!IMPORTANT]
> **Question clé :** Le pipeline eFLESH génère-t-il nativement une coque lisse au-dessus de la microstructure cut-cell ?
>
> **Réponse : Partiellement.** Le notebook `cut-cell.ipynb` prend un paramètre de **`skin thickness`** (épaisseur de paroi externe) typiquement réglé entre **1.0 et 1.2 mm**. Cela produit une enveloppe solide autour de la lattice dans le STL de sortie. **Cependant :**
> - Cette peau est générée uniquement autour du **volume convexe d'entrée** (la Zone A)
> - Elle ne s'étend PAS aux Zones B et C (logement PA12-CF, ongle) qui ne font pas partie du mesh d'entrée
> - La jonction entre la peau de la Zone A et les parois solides des Zones B/C nécessite un **travail de fusion dans Fusion 360**

**Configuration du paramètre `skin thickness` dans `cut-cell.ipynb` :**
```python
# Dans la section de configuration du notebook :
skin_thickness = 1.0  # mm — épaisseur de la coque TPU lisse autour de la lattice
                       # Valeur recommandée : 1.0 mm (2 périmètres de 0.4 mm + overlap)
                       # Minimum absolu : 0.8 mm (fragile, risque de perçage)
                       # Maximum conseillé : 1.5 mm (réduit la sensibilité tactile)
```

**Résultat dans le STL exporté :**
```
     Coupe transversale du STL généré par le pipeline eFLESH
     
     ┌─────────────────────────────────────┐
     │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Peau lisse extérieure (skin_thickness)
     │▓  ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐  ▓│
     │▓  │ │ │ │ │ │ │ │ │ │ │ │ │ │  ▓│ ← Cut-cell lattice (air + poutres TPU)
     │▓  └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘  ▓│
     │▓   ┌──────── POCHE ────────┐     ▓│ ← Cavité aimant Ø3.2 × 1.1mm
     │▓   │    ● S-03-01-N ●      │     ▓│
     │▓   └───────────────────────┘     ▓│
     │▓  ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐  ▓│ ← Lattice sous l'aimant (plus souple)
     │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Peau lisse inférieure (face capteur)
     └─────────────────────────────────────┘
            → SLOT PCB 10×10mm ←
```

Le slicer (OrcaSlicer) doit être configuré avec **Infill 0%** ou **100% solide** (le remplissage interne est déjà dans la géométrie STL, pas besoin d'infill slicer). Les **2 périmètres externes du slicer** s'ajoutent à la peau existante du STL.

---

#### C. Workflow Hybride Complet dans Fusion 360 (Méthode Recommandée)

Fusion 360 est idéal car il permet de **combiner** (Combine → Join) deux corps solides en un seul corps monolithique imprimable, éliminant tout problème de jonction.

##### Étape 1 — Préparation dans Fusion 360 : Séparation en corps

1. Ouvrez le modèle STEP/F3D complet de la gaine TPU du doigt D-Hand V1
2. Utilisez **Modify → Split Body** avec un plan de coupe placé à la limite supérieure de la zone tactile (pulpe)
3. Vous obtenez **2 corps** :
   - **Corps A (Zone tactile)** : Le volume de la pulpe uniquement (face inférieure du doigt). Simplifiez-le en **enveloppe convexe** si nécessaire (`Mesh → Compute Convex Hull` ou manuellement en lissant les concavités)
   - **Corps B (Zone structurelle)** : L'ongle, le dos du doigt, le logement de la phalange PA12-CF, la gaine articulaire
4. **Exportez le Corps A au format OBJ** (Mesh → Export → OBJ) pour le pipeline eFLESH

##### Étape 2 — Pipeline eFLESH sur le Corps A (Ubuntu / WSL2)

1. Transférez le fichier `corps_A_pulpe.obj` sur votre machine Linux (ou WSL2 sur Mac via UTM/Parallels)
2. Ouvrez `cut-cell.ipynb` dans Jupyter et configurez :
   ```python
   input_surface = "corps_A_pulpe.obj"
   cell_size = 3.0    # mm — adapté à l'épaisseur de la pulpe (~3.8 mm)
   skin_thickness = 1.0  # mm — peau lisse autour de la lattice
   
   # Variation spatiale de rigidité par couche (k=0 = couche du bas)
   def young(k):
       if k == 0:       # Couche plancher (face capteur) — rigide
           return 2.0   # MPa
       elif k == 1:     # Couche sous l'aimant — souple (max sensibilité)
           return 0.5   # MPa
       elif k == 2:     # Couche aimant — médium
           return 1.0   # MPa
       else:            # Couches supérieures — progressivement plus rigide
           return 1.5   # MPa
   ```
3. Exécutez toutes les cellules → export du STL lattice
4. Ajoutez les poches d'aimants via `create_pouch.py` (Blender) :
   ```python
   list_of_magnets = [
       [3.2, 1.1, [X_pulpe, Y_pulpe, Z_poche]],  # 1 aimant S-03-01-N
   ]
   ```
5. Exportez le **`corps_A_eflesh_final.stl`**

##### Étape 3 — Fusion dans Fusion 360 (Soudure des 2 corps)

1. **Importez** le `corps_A_eflesh_final.stl` dans Fusion 360 :
   - `Insert → Insert Mesh` → sélectionnez le STL
   - Si nécessaire, convertissez en B-Rep : `Mesh → Convert Mesh` (ou conservez en mesh si la conversion échoue à cause de la complexité de la lattice)
2. **Positionnez** le Corps A eFLESH à l'emplacement exact de la Zone A d'origine :
   - Utilisez `Move/Copy` avec les coordonnées absolues ou `Align` avec les faces de jonction
   - Vérifiez visuellement que la peau extérieure du Corps A s'aligne avec la paroi extérieure du Corps B
3. **Créez la zone de transition (overlap)** :
   - Allongez le Corps A de **0.5 à 1.0 mm dans la zone de chevauchement** avec le Corps B
   - Cela crée un overlap intentionnel de matière à l'interface, éliminant tout défaut de collage inter-couches
4. **Fusionnez les deux corps** :
   - `Modify → Combine` → **Operation : Join** → Body 1 = Corps B, Tool Body = Corps A mesh
   - *Si la fusion mesh/BRep échoue :* Exportez les deux corps en STL séparés et fusionnez-les via `Mesh → Merge Bodies` ou dans un logiciel externe (Meshmixer, Blender Boolean Union)
5. **Lissage de la jonction** (optionnel mais recommandé) :
   - Appliquez un **congé (Fillet)** de 0.3 à 0.5 mm sur l'arête de jonction entre les deux zones pour éviter toute concentration de contrainte
   - Vérifiez visuellement dans la vue Section Analysis que la peau extérieure est continue

> [!TIP]
> **Astuce Fusion 360 pour la peau lisse :** Si la peau lisse générée par le pipeline eFLESH (`skin_thickness`) est insuffisante ou présente des artefacts de voxelisation (escaliers), vous pouvez la renforcer dans Fusion 360 **après la fusion** en appliquant un `Shell` de 0.4 mm sur les faces extérieures de la zone tactile, ou simplement en comptant sur les **2 périmètres du slicer** (0.8 mm) qui s'ajoutent automatiquement lors du tranchage.

##### Étape 4 — Export et Tranchage Multi-Zone dans OrcaSlicer

1. **Export STL** : `File → Export → STL` (format binaire pour fichier plus léger)
2. **Import dans OrcaSlicer** en tant que pièce unique
3. **Configuration multi-zone** (fonctionnalité OrcaSlicer "Modifier") :
   - Clic droit sur la pièce → **"Add Modifier" → "Height Range"**
   - **Zone A (hauteur de la pulpe tactile)** :
     - Infill : **0%** (la microstructure est dans la géométrie — le slicer ne doit rien ajouter dans les cellules d'air)
     - Périmètres (walls) : **2** (0.8 mm) pour renforcer la peau extérieure
     - Top/Bottom layers : **0** (la peau est dans le STL, pas besoin de couches pleines supplémentaires au-dessus de la lattice)
   - **Zones B et C (ongle, gaine articulaire, logement PA12-CF)** :
     - Infill : **100% rectiligne** (rigidité maximale pour le rappel élastique et le maintien du squelette)
     - Périmètres : **3** (1.2 mm)
4. **Matériau** : TPU 95A (Qidi TPU 95A-HF), séché à 65°C pendant 12h
5. **Orientation** : Face arrière (logement PA12-CF) vers le bas sur le plateau

---

#### D. Procédure d'insertion et de scellage de l'aimant

1. **Identification de la couche de pause** : Dans l'aperçu OrcaSlicer, identifiez la couche exacte qui **ferme le dessus de la poche d'aimant** générée par le pipeline eFLESH. Cette couche est visible comme une surface plate au-dessus de la cavité cylindrique.
2. **Ajout de la pause** : Clic droit sur le slider de couche dans Preview → **"Add Pause"** à cette couche. OrcaSlicer insère automatiquement la commande G-code `M601` (Qidi) ou `M600` (Marlin).
3. **Lancement de l'impression** en TPU 95A.
4. **Attente thermique (Pause)** : Lorsque l'imprimante se met en pause, **attendez 1 à 2 minutes**. Cela permet à la buse de s'éloigner (fin du rayonnement thermique direct) et au plastique du logement de descendre à la température stabilisée du plateau (50-60 °C).
5. **Insertion double pastille (SANS froid)** :
   * Prenez un aimant **S-03-01-N** (Ø3×1mm) à température ambiante, préalablement équipé de ses pastilles adhésives isolantes en **Tissu de verre 3M 69** (ou Kapton) collées sur ses deux faces (voir section E.6).
   * Insérez rapidement l'aimant dans sa cavité avec le **pôle Nord orienté vers le bas** (vers le magnétomètre) à l'aide d'une pince non-magnétique (laiton ou plastique).
6. **Reprise** : Relancez l'impression. La buse va extruder le TPU chaud directement sur la pastille supérieure isolante, scellant l'aimant hermétiquement sans l'exposer au pic thermique direct de 220 °C.
7. **Intégration électronique** : Après refroidissement complet, glissez le PCB custom de 10×10 mm dans la glissière inférieure et scellez l'entrée avec un cordon de silicone flexible pour l'étanchéité.

---

#### E. Installation de l'outil de CAO eFlesh (Linux / Ubuntu requis)

> [!WARNING]
> **Mac M1/M2/M3** : L'outil eFLESH nécessite un environnement **Linux x86_64** pour la compilation des outils C++ CGAL. Sur Mac Apple Silicon, utilisez **UTM** (VM Ubuntu gratuite), **Parallels Desktop** (VM Ubuntu), ou **Docker** avec une image Ubuntu. WSL2 n'est disponible que sur Windows.

1. **Prérequis système :**
   Installez les bibliothèques de traitement géométrique 3D requises :
   ```bash
   sudo apt-get update
   sudo apt-get install -y build-essential cmake libgmp-dev libmpfr-dev libcgal-dev libeigen3-dev libsuitesparse-dev libboost-all-dev
   ```
2. **Récupération du dépôt eFlesh :**
   Clonez le dépôt en incluant les sous-modules nécessaires :
   ```bash
   git clone --recurse-submodules https://github.com/notvenky/eFlesh.git
   cd eFlesh
   ```
3. **Configuration de l'environnement Python :**
   Créez et activez l'environnement de dépendances via Conda :
   ```bash
   conda env create -f env.yml
   conda activate eflesh
   ```
4. **Compilation des inflateurs de microstructure :**
   ```bash
   cd microstructure/microstructure_inflators
   chmod +x build.sh
   ./build.sh                # Utilise 12 cœurs CPU par défaut
   # ./build.sh cpu_nodes=4  # Si votre VM a moins de cœurs
   ```
5. **Vérification** : Les notebooks `regular.ipynb` et `cut-cell.ipynb` doivent pouvoir s'exécuter sans erreur depuis `microstructure/microstructure_inflators/`.

#### F. Ressources et Liens Officiels

| Ressource | Lien |
|:---|:---|
| **Dépôt GitHub eFlesh** | [github.com/notvenky/eFlesh](https://github.com/notvenky/eFlesh) |
| **Documentation CAD2eFlesh** | [microstructure/README.md](https://github.com/notvenky/eFlesh/blob/main/microstructure/README.md) |
| **Paper ArXiv** | [arXiv:2506.09994](https://arxiv.org/abs/2506.09994) |
| **Site officiel** | [e-flesh.com](https://e-flesh.com) |
| **PCB Magnetometer (WowRobo)** | [shop.wowrobo.com/products/eflesh-magnetometer-board](https://shop.wowrobo.com/products/eflesh-magnetometer-board) |

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

#### Ce que l'ajout d'un 2ème PCB apporte réellement

**Option B (2 PCBs par paume) :**
- Permet de distinguer un contact dans la **zone thénar** (base du pouce) vs **zone métacarpienne** (base des autres doigts).
- Utile pour les objets de géométries complexes afin d'identifier plus finement le type de contact.
- **Cependant**, le gain pratique pour la préhension robotique générale reste modéré, car la paume sert de butée de force, tandis que la manipulation précise est gérée par les bouts de doigts.

#### Recommandation finale pour la paume

> [!IMPORTANT]
> **La recommandation finale est d'utiliser 1 seul PCB WowRobo par paume (Option A).**
>
> **Pourquoi ce choix ?**
> 1. **Complexité électronique évitée :** Les 5 capteurs de chaque PCB WowRobo ont des adresses I2C fixes. Avec 1 seul PCB, il n'y a aucun conflit. Avec 2 PCBs sur le même bus, les adresses entrent en conflit direct, ce qui impose d'utiliser un multiplexeur I2C (type TCA9548A) ou de dédier des GPIOs pour un second bus I2C par main.
> 2. **Simplicité mécanique :** Le châssis de la main DHand V1 dispose d'un évidement de 20×20 mm parfaitement adapté pour un seul PCB. Intégrer deux PCBs exigerait de modifier et ré-imprimer la structure en PA12-CF de la main et de redessiner la coque TPU souple de la paume.
> 3. **Optimisation des stocks (Spare) :** Utiliser 1 PCB par paume (2 au total pour les deux mains) laisse **6 PCBs WowRobo de rechange (spare)** en réserve, ce qui est très confortable en cas de panne sur les pieds ou le torse.

#### Si vous choisissez l'Option B (2 PCBs par paume) malgré tout :
* **Câblage :** Vous devez utiliser un multiplexeur TCA9548A ou câbler les deux cartes sur des bus I2C distincts de l'ESP32.
* **CAO :** Vous devez adapter le fichier STEP de la paume pour y insérer deux logements de 20×20 mm.

**Disposition recommandée du PCB unique sur la paume (60×80mm) :**

Le PCB central doit être implanté au cœur de la zone de contact principale (creux de la main, légèrement décalé vers la base métacarpienne des doigts 2-3-4). Cela correspond précisément à l'évidement de 20×20 mm prévu sur les plans de la main DHand V1.

#### Bilan d'utilisation des PCBs WowRobo (avec 1 PCB/paume)

| Emplacement | PCBs requis |
|:---|:---:|
| Paumes (×2, 1 PCB par main) | **2** |
| Pieds (×2, 4 PCBs par pied) | **8** |
| Avant-bras (×2, 1 par bras) | **2** |
| Torse | **2** |
| **Sous-total utilisé** | **14** |
| **Spare (réserve)** | **6** |
| **Total** | **20** |

---|:---:|:---:|:---:|:---|:---:|
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

### E.1 — Inventaire et Caractéristiques des Aimants {#e1-inventaire}

| Référence | Forme | Dimensions | Grade | Br (T) | Force pull | Qté |
|:---|:---|:---|:---:|:---:|:---:|:---:|
| **S-03-01-N** | Disque | Ø3mm × 1mm | N48 | 1.43 T | 190 g | 40 |
| **S-08-03-N** | Disque | Ø8mm × 3mm | N45 | 1.34 T | 1.5 kg | 40 |
| **W-05-N** | Cube | 5×5×5mm | N42 | 1.32 T | 1.1 kg | 10 |

> [!NOTE]
> La force "pull" indiquée par Supermagnete est la force d'attraction au contact direct (air-gap = 0). Elle **n'est pas** la force exercée à la distance de travail (3–10mm). Ce qui compte ici est le **champ magnétique Bz à distance de travail**, calculé ci-dessous.

---

### E.2 — Rappel : Plages Utiles du MLX90393 (Gain Programmable) {#e2-plages}

Le MLX90393 possède un gain d'amplification interne **entièrement programmable** via le registre `GAIN_SEL` (de 0 à 7). Plus le gain d'amplification est faible, plus la plage de mesure physique est grande :

| GAIN_SEL | Type de Gain | Sensibilité Z (µT/LSB) | Plage Max Mesurable Z | Usage recommandé |
|:---:|:---:|:---:|:---:|:---|
| **0** | Amplification Min | 1.468 | **±48 mT** (plage max) | Champs très forts (25 à 45 mT) |
| **2 (défaut)** | Amplification Moyenne | 0.881 | **±29 mT** | Champs moyens (12 à 25 mT) |
| **4** | Amplification Moyenne | 0.587 | **±19 mT** | Champs faibles-moyens (8 à 15 mT) |
| **5** | Amplification Forte | 0.489 | **±16 mT** | Champs faibles (6 à 12 mT) |
| **7** | Amplification Max | 0.294 | **±10 mT** (plage min) | Champs très faibles (< 6 mT) |

> [!WARNING]
> Ces valeurs correspondent à **RES=0** (résolution standard 16 bits). Si vous augmentez `RES`, les valeurs µT/LSB augmentent (ce qui améliore la résolution numérique mais réduit proportionnellement la plage de mesure).
>
> **Règle d'or :** Le champ magnétique au repos (aimant non comprimé) doit être dans la **plage 30–60% de la plage maximale** configurée afin de conserver une marge dynamique de détection lors de la compression sans risquer la saturation.

En pratique, pour notre système :
- **Champs forts (Bz > 25 mT)** → Configurer **GAIN_SEL=0** (plage ±48 mT) pour éviter la saturation du CAN.
- **Champs moyens (Bz ≈ 12–25 mT)** → Configurer **GAIN_SEL=2** (défaut Adafruit, plage ±29 mT).
- **Champs faibles (Bz < 8 mT)** → Configurer **GAIN_SEL=5 ou 7** pour amplifier le signal et augmenter le SNR.

> [!IMPORTANT]
> **Limite physique de la plaque Hall :** Indépendamment du gain programmé, la plaque à effet Hall sature physiquement autour de **~50 mT**. Tout champ magnétique supérieur à cette limite donnera une mesure saturée ou erronée, quel que soit le `GAIN_SEL`.

---

### E.3 — Calcul du Champ Magnétique par Aimant et par Distance {#e3-calculs}

> *Formule utilisée : B(z) = (Br/2) × [(z+L)/√(R²+(z+L)²) − z/√(R²+z²)], aimant disque ou cube équivalent.*

#### Tableau complet Bz(mT) vs distance air-gap

```
                         AIR-GAP (distance aimant → surface capteur MLX90393)
Aimant               2mm    3mm    4mm    5mm    6mm    7mm    8mm   10mm   12mm
─────────────────────────────────────────────────────────────────────────────────
S-03-01-N Ø3×1mm    68     30     15      9      5      4      3      1      1
  (N48, Br=1.43T)   ❌SAT  ✅G0   ✅G2   ✅G5   ✅G7   ⚠️W    ⚠️W    ⚠️W    ⚠️W

S-08-03-N Ø8×3mm   224    155    108     76     55     40     30     18     12
  (N45, Br=1.34T)   ❌SAT  ❌SAT  ❌SAT  ❌SAT  ❌SAT  ✅G0   ✅G0   ✅G2   ✅G5

W-05-N Cube 5mm    230    142     90     60     42     30     23     13      9
  (N42, Br=1.32T)   ❌SAT  ❌SAT  ❌SAT  ❌SAT  ✅G0   ✅G0   ✅G2   ✅G5   ✅G5
─────────────────────────────────────────────────────────────────────────────────
LÉGENDE :
  ❌SAT   Sature physiquement le capteur (> 45-50 mT), mesure impossible
  ✅G0    Champ fort (25-45 mT), requiert GAIN_SEL=0 ou 1 (gain min / plage max)
  ✅G2    Champ moyen (12-25 mT), idéal GAIN_SEL=2 ou 3 (défaut)
  ✅G5    Champ faible (6-12 mT), idéal GAIN_SEL=4 ou 5
  ✅G7    Champ très faible (4-6 mT), idéal GAIN_SEL=6 ou 7 pour un meilleur SNR
  ⚠️W    Champ insuffisant (< 4 mT), signal noyé dans le bruit de fond
```

---

### E.4 — Recommandation par Emplacement {#e4-reco}

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

#### ✋ Paume (1 PCB WowRobo par main, air-gap TPU : 5–7 mm)

| Aimant | Bz @5mm | Bz @7mm | Verdict |
|:---|:---:|:---:|:---|
| S-03-01-N ⚠️ | 9 mT | 4 mT | ⚠️ Trop faible au-delà de 5 mm. Alternative possible uniquement à 4.5 mm d'air-gap avec GAIN_SEL=2 |
| **W-05-N** ✅ | **60 mT** | **30 mT** | ✅ **IDÉAL** — mais requiert un air-gap ≥ 6 mm et GAIN_SEL=0 pour éviter la saturation |
| S-08-03-N ❌ | 76 mT | 40 mT | ❌ Sature le capteur à 5 mm. Risque élevé de saturation lors de l'écrasement de la paume |

> [!IMPORTANT]
> **Paume → W-05-N (cube 5mm).** Le cube a l'avantage d'une face plane facile à coller dans le TPU. À 6–7 mm d'air-gap, il fournit un signal fort et stable (30 à 42 mT) — ce qui est parfait à condition de configurer le capteur sur le gain d'amplification minimal **GAIN_SEL=0 (plage ±48 mT)**.
> 
> **Avertissement de conception :** À 5 mm de distance, le champ atteint 60 mT et sature la plaque Hall (limite ~50 mT). Il faut donc s'assurer que l'épaisseur du TPU et de l'air-gap maintient une distance minimale de **6 mm (idéalement 6.5 mm nominal)** au repos, et intégrer des butées mécaniques rigides pour limiter l'écrasement sous forte charge à 5.5 mm minimum.

**Configuration :** 1 cube W-05-N par capteur MLX90393 (10 cubes total pour les 2 paumes - 5 par main), noyé dans la couche TPU palmaire (Shore 85A). Air-gap nominal de 6.5 mm. **Configuration logicielle requise : GAIN_SEL=0 (gain min / plage max)**.

---

#### 🦶 Semelle Plantaire (4 PCBs WowRobo par pied, air-gap variable selon charge)

C'est le cas le plus complexe : le TPU **se comprime** sous le poids du robot.

```
  État du pied         Air-gap TPU    Champ S-03-01-N   Champ S-08-03-N (air-gap accru)
  ──────────────────   ────────────   ───────────────   ───────────────────────────────
  Sans charge (debout)    10 mm           1 mT ⚠️W          18 mT ✅G2 (GAIN_SEL=2 ou 3)
  Mi-charge (marche)       8 mm           3 mT ⚠️W          30 mT ✅G0 (GAIN_SEL=0 ou 1)
  Pleine charge (impact)   7 mm           4 mT ⚠️W          40 mT ✅G0 (GAIN_SEL=0, max)
  Forte compression       < 6 mm          5-9 mT ✅G7       > 55 mT ❌SAT (saturation)
```

**Analyse :**
- **S-03-01-N** : Même à 7 mm de compression, le champ est de seulement **4 mT** (proche du bruit). Au repos (10 mm), il est de **1 mT** (impossible de détecter le contact). Cet aimant est donc **totalement inadapté** pour la semelle.
- **S-08-03-N (Ø8×3mm)** : En augmentant l'air-gap nominal au repos à **10 mm**, on obtient un champ de **18 mT** (très propre avec `GAIN_SEL=2`). Lors de l'impact, le TPU se comprime (l'air-gap descend à 7 mm), le champ monte à **40 mT**, ce qui reste mesurable à `GAIN_SEL=0` sans saturer le capteur.
- **Risque de saturation** : Si le TPU s'écrase au-delà de 3 mm (air-gap < 6.5 mm), le champ dépassera 50 mT et saturera physiquement le capteur. Il est donc **critique de concevoir une butée mécanique rigide** dans la semelle pour limiter l'écrasement maximal du TPU à 7 mm de distance aimant-capteur.

> [!IMPORTANT]
> **Semelle plantaire → S-08-03-N (Ø8×3mm) avec air-gap de 10 mm au repos.** C'est la seule configuration qui maintient un signal clair au repos (18 mT) tout en évitant la saturation lors de la compression de la semelle (jusqu'à 7 mm d'air-gap, Bz = 40 mT).
>
> **Réglage GAIN_SEL :** Configurer à **GAIN_SEL=0 (gain min / plage max)** ou implémenter un auto-gain dynamique pour s'adapter à la charge.

**Configuration :** 1 aimant S-08-03-N par capteur (20 aimants par pied, 40 total pour 2 pieds). Air-gap TPU nominal de 10 mm au repos, limité par butée rigide à 7 mm lors des impacts. GAIN_SEL=0.

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

### E.5 — Tableau Récapitulatif Final {#e5-recap}

| Emplacement | Aimant recommandé | Air-gap (repos) | GAIN_SEL | Bz repos | Butée / Sécurité | Aimants utilisés |
|:---|:---|:---:|:---:|:---:|:---|:---:|
| Doigts ×10 (5/main×2) | **S-03-01-N** Ø3×1mm | 3.5 mm | 2 (défaut) | ~22 mT | N/A | **10** |
| Paume ×2 (×5 cap.) | **W-05-N** Cube 5mm | 6.5 mm | 0 (min gain) | ~36 mT | Butée à 5.5 mm | **10** |
| Pieds ×2 (×20 cap.) | **S-08-03-N** Ø8×3mm | 10.0 mm | 0 (min gain) | ~18 mT | Butée à 7.0 mm | **40** |
| Avant-bras ×2 (×5 cap.) | **S-03-01-N** Ø3×1mm | 4.0 mm | 2 (défaut) | ~15 mT | N/A | **10** |
| Torse ×1 (×10 cap.) | **S-08-03-N** Ø8×3mm | 8.0 mm | 2 (défaut) | ~30 mT | N/A | **10** |

#### Bilan stock aimants

| Référence | Stock | Utilisés | Spare |
|:---|:---:|:---:|:---:|
| S-03-01-N (Ø3×1mm) | 40 | 10 (doigts) + 10 (avant-bras) = **20** | **20** ✅ |
| S-08-03-N (Ø8×3mm) | 40 | 40 (pieds) + 10 (torse) = **50** | **-10** ⚠️ Commander 10 supplémentaires |
| W-05-N (Cube 5mm) | 10 | 10 (paumes) = **10** | **0** — stock exact |

> [!WARNING]
> **Il manque 10 aimants S-08-03-N** pour équiper complètement le torse en plus des pieds.
> 
> **Alternative sans commande supplémentaire :** Si vous ne souhaitez pas commander de nouveaux aimants, vous pouvez utiliser les 20 aimants **S-03-01-N** restants en spare pour le Torse en adaptant l'air-gap à **4.5 mm** au lieu de 8 mm (Bz repos ≈ 12 mT) et en configurant le gain à **GAIN_SEL=4** (plage ±19 mT). Cela fonctionne parfaitement et utilise 100% de votre stock actuel sans coût additionnel !

---

### E.6 — Risque de Démagnétisation Thermique lors de l'Impression 3D (TPU chaud) {#e6-thermique}

> [!CAUTION]
> **Risque critique de perte d'aimantation :** Les aimants néodyme standards (grades N42, N45, N48 de votre stock) ont une température maximale de fonctionnement de **80 °C**. Au-delà de cette température, ils subissent une perte irréversible de leur champ magnétique. Lors de l'impression 3D en TPU, le plastique est extrudé à **220–235 °C**. Déposer du TPU fondu directement sur un aimant inséré in-situ (via une pause d'impression) risque de le démagnétiser partiellement ou totalement, rendant le capteur tactile inopérant.

#### Mécanismes physiques du risque thermique :
1. **Température maximale de travail (80 °C) :** Limite au-delà de laquelle l'aimant perd définitivement une partie de son intensité magnétique par désalignement des domaines magnétiques (pertes irréversibles).
2. **Température de Curie (310 °C) :** Seuil de désaimantation totale et instantanée.
3. **Faible inertie thermique :** Les petits aimants Ø3×1 mm possèdent une masse infime (~0.05 g). La buse d'imprimante chauffée à 220 °C qui passe au-dessus ou dépose du filament en fusion à proximité immédiate peut les faire monter à plus de 100 °C en une fraction de seconde par conduction.

#### Solutions et bonnes pratiques de fabrication :

1. **Option 1 — Insertion mécanique après impression :**
   * **Principe :** Concevoir les coques ou pulpes en TPU avec une fente d'insertion latérale ou un logement ouvert vers l'extérieur (légèrement sous-dimensionné d'environ 0.1 mm pour un ajustement serré).
   * **Avantage :** L'aimant est inséré à température ambiante une fois la pièce entièrement refroidie. Aucun risque thermique.
   * **Fixation :** L'élasticité naturelle du TPU suffit à emprisonner l'aimant. Si nécessaire, sécuriser avec une goutte de colle cyanoacrylate flexible (ex: Loctite 480 ou Super Glue Gel) ou une pointe de silicone.

2. **Option 2 — Protocole d'Insertion In-Situ Sécurisé (Double pastille isolante - SANS froid) — (Recommandée) :**
   * **Principe :** Afin d'éviter tout risque de condensation d'eau (qui nuit à l'adhérence inter-couches du TPU et génère des bulles de vapeur sous l'effet de la buse à 220 °C), les aimants sont maintenus à température ambiante. La protection thermique est assurée par deux pastilles isolantes collées en dessous et au-dessus de l'aimant.
   * **Matériaux recommandés :**
     * **Choix A — Le Ruban Kapton (Polyimide) :** Très fin (0.05 mm), résiste jusqu'à 260 °C (pointe à 400 °C). Offre un excellent écran thermique de contact. Le TPU chaud y adhère bien.
     * **Choix B (Recommandé - Meilleur isolant) — Le Ruban en Tissu de Verre (ex: 3M 69 ou équivalent) :** Plus épais (0.15–0.20 mm), composé de fibres de verre tissées résistantes à 200 °C+. Sa structure fibreuse offre une isolation thermique bien supérieure au Kapton et permet une adhérence mécanique exceptionnelle du TPU dans les mailles du tissu.
   * **Préparation de l'aimant (à l'avance) :**
     * Collez une pastille de ruban isolant (Kapton ou Tissu de verre) découpée au diamètre de l'aimant sur **les deux faces** (dessous et dessus) de l'aimant.
     * *Note : L'épaisseur cumulée (~0.1 à 0.3 mm) s'insère parfaitement dans la tolérance de la cavité (prévue à 1.1 mm de profondeur pour un aimant de 1.0 mm dans la gaine).*
   * **La Pause d'Impression :** Une fois la pause activée, attendez 1 à 2 minutes avant d'insérer l'aimant. Cela permet à la buse de s'éloigner (arrêt du rayonnement thermique direct) et au plastique fraîchement imprimé de descendre à la température stabilisée du plateau (50-60 °C).
   * **Insertion :** Insérez l'aimant double-pastille (à température ambiante, parfaitement sec) dans son logement à l'aide d'une pince non-magnétique (plastique ou laiton) et relancez immédiatement l'impression. Le plastique chaud sera extrudé directement sur la pastille isolante supérieure, protégeant l'aimant du pic thermique.
   * **Où acheter les matériaux :**
     * **Ruban Kapton :** Disponible sur *Amazon.fr* (rechercher "Ruban adhésif Kapton haute température", ~5-8€ le rouleau) ou dans les boutiques d'impression 3D.
     * **Ruban Tissu de Verre 3M 69 :** Disponible sur *Amazon.fr* ou *RS-Components* (rechercher "Ruban adhésif tissu de verre 3M 69", ~15-20€ le rouleau). Un rouleau de 19 mm de large suffit pour des centaines de pastilles.

3. **Option 3 — Choix d'aimants de grade haute température :**
   * Remplacer les aimants de grade **N** (80 °C max) par des aimants de grade **SH** (jusqu'à 150 °C) ou **EH** (jusqu'à 200 °C). *Attention : les aimants fournis dans votre stock actuel sont de grade N.*
