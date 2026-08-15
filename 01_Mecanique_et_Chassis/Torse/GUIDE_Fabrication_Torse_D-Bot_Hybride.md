# 🛠️ Guide de Fabrication Hybride : Torse D-Bot V1
### Architecture Cruciforme Squelettique (Alu CNC + Tube Carbone) & Coque Secondaire PA12-CF

*Ce document constitue le guide officiel et complet de fabrication, d'usinage CNC, d'impression 3D FDM et d'assemblage du torse pour le robot humanoïde D-Bot V1 (40,4 kg).*

> [!NOTE]
> **Évolution architecturale majeure** : Le torse s'appuie sur une **architecture cruciforme métallique et composite** (plaque sagittale 2D + traverse carbone Ø30 mm + cages H-bracket d'épaules en Alu 7075-T6) reprenant l'intégralité des efforts dynamiques. La coque en PA12-CF est une **coque secondaire allégée** dédiée à la protection, au guidage des batteries et à l'esthétique bionique.
>
> 📄 **Documents associés** : [ETUDE_Dimensionnement_Colonne_Vertebrale.md](./ETUDE_Dimensionnement_Colonne_Vertebrale.md) · [JOURNAL_DE_BORD.md](../../05_Gestion_Projet/JOURNAL_DE_BORD.md)

---

## 1. Principe Architectural : Le Squelette Cruciforme Interne

### A. Philosophie de Conception

Le torse du D-Bot est adapté des formes extérieures d'Asimov v1 (mise à l'échelle de +18%), avec une refonte totale de l'infrastructure porteuse interne :

| Élément | Ancien design (Asimov pur) | Nouveau design (D-Bot V1 Cruciforme) |
|:---|:---|:---|
| **Structure porteuse** | Coque PA12-CF seule (6 périmètres, 35% infill) | **Squelette cruciforme Alu 6061/7075 + Tube Carbone 3K** |
| **Rôle de la coque** | Primaire (porte tous les efforts) | **Secondaire** (protection, habillage, transmission locale) |
| **Colonne vertébrale** | 2 lattes alu latérales (irréalisable) | **1 plaque sagittale à lumières 2D** (dos ➔ ventre, 5.0 mm Alu 6061-T6) |
| **Traverse épaules** | Aucune | **Tube carbone 3K Ø30 mm** reliant les 2 épaules |
| **Liaison d'épaules** | Disques plats alu 5 mm | **2 Cages H-Bracket Alu 7075-T6 (2 plaques 5mm évidées Ø95mm + bride 48.2mm + tirants M5 à 23.4°)** |
| **Batterie** | 1 panier coulissant central | **2 paniers latéraux symétriques (G + D) avec Hot-Swap** |
| **Orientation impression** | Dos au plateau (horizontal) | **Verticale** (debout sur le plan de coupe) |

---

### B. Schéma de la Structure Cruciforme

![Schéma d'Architecture de la Structure Cruciforme du Torse](./media/structure_cruciforme.svg)

*Schéma d'architecture 2D de la structure cruciforme du torse D-Bot : Vue de Face (Plan Frontal avec la traverse carbone Ø30mm, la plaque sagittale à lumières 2D 5mm et les moteurs RS-04/RS-06) et Vue de Dessus (Plan Transversal avec l'orientation sagittale dos->ventre et les 2 paniers batteries latéraux).*

---

### C. Rigidité Comparée

| Sollicitation | Ancien (lattes) | Nouveau (cruciforme V1) | Gain | Note |
|:---|:---:|:---:|:---:|:---|
| **Flexion Pitch** (avant/arrière) | I ≈ 773 000 mm4 | I ≈ 506 667 mm4 (plaque nette + brides) | **~×0.8** | Facteur de sécurité Sf = 7.36 (nominal) / 5.26 (extrême) |
| **Flexion Roll** (latérale) | Bon | **Excellent avec Cages H-Bracket (tirants M5 R=72mm / 23.4°)** | **×15.5** | Flèche au cou < 0.10 mm (0.097 mm), libère les batteries |
| **Torsion Yaw** | Très faible | Bon (traverse Ø30 mm + nœud demi-coquilles) | **×5-8** | Verrouillage positif par goupille Ø4 mm |
| **Compression axiale** | Bon | Excellent | **×2** | Repris directement par la plaque sagittale |

---

## 2. Colonne Sagittale 2D (Option B — Plaques 5,0 mm Alu 6061-T6)

### A. Spécifications Générales

| Paramètre | Valeur |
|:---|:---|
| **Matériau** | Aluminium 6061-T6, tôle de 5,0 mm d'épaisseur |
| **Orientation** | Plan sagittal (dos ➔ ventre), verticale sur toute la hauteur du torse |
| **Conception retenue** | **Option B (Lumières 2D Traversantes ⭐)** : Évidements 100% débouchants en 1 seule passe |
| **Dimensions brutes** | ~432 mm (hauteur totale) × **120,0 mm (profondeur max d'usinage C500)** |
| **Découpage** | En **2 parties** (Haute 142,67 mm + Basse 290,0 mm) jointes au Nœud Central d'épaule (h = 290 mm) |
| **Jonction des 2 parties** | **Nœud Demi-Coquilles CNC Alu** + Tube Carbone Ø30 mm + Goupille Verticale Z (60 mm) |
| **Fixation haute & basse** | **Équerres CNC Alu en Sandwich (L-Brackets)** fixées par vis M4 traversantes |
| **Masse totale 2 plaques** | **~355 g** (vs 668 g pleine — **économie de 313 g / -47%**) |

#### Solution de Fixation Haute et Basse (Équerres CNC L-Brackets en Sandwich)

![Solution de fixation par équerres L-Brackets en sandwich](./media/solution_liaison_embase_cou.svg)

*Principe d'assemblage en sandwich : 2 équerres en L en aluminium 6061-T6 (à gauche et à droite) enserrent la tôle de 5 mm avec 3 à 4 vis traversantes M4. Le rebord horizontal des équerres est vissé sur les plaques circulaires de cou (5 mm) et de taille (6 mm).*

---

### B. Justification & Comparatif des Formes d'Évidements

![Comparatif des options d'usinage de la colonne vertébrale](./media/comparatif_plaques_colonne.svg)

> [!IMPORTANT]
> **Pourquoi l'Option B (Lumières 2D) est le Choix Idéal :**
> 1. **Solidité supérieure** : Propose un facteur de sécurité **Sf = 9.21** sous choc dynamique de 220 N.m à la base (Sigma_max = 26.05 MPa), très supérieur à l'Isogrid (Sf = 5.70).
> 2. **Gain de poids massif (-47%)** : Économise 313 g sur la colonne (355 g contre 668 g en plaque pleine).
> 3. **Fiabilité d'Usinage C500** : Découpe en **une seule passe 2D débouchante** en 15 minutes total. Risque de voilement nul et aucun retournement de pièce requis (pas de Flip Z).

![Plaques de Colonne Vertébrale Évidées 2D](./media/plaques_colonne_2d_evidees.svg)

---

### C. Fabrication CNC sur NestWorks C500

| Étape | Détail |
|:---|:---|
| **1. Bridage** | Fixer la tôle brute 6061-T6 de 5,0 mm à plat sur la table C500 (sur martyr MDF) |
| **2. Outil** | Fraise carbure Ø6 mm DLC (O-Type 1 dent) |
| **3. Paramètres de coupe** | Vitesse 10 000 tr/min, avance 800 mm/min, passes de Z = -1,25 mm (4 passes) |
| **4. Lumières 2D** | Découpe 100% débouchante à Z = -5,2 mm en une passe continue |
| **5. Contour & Perçages** | Découpe du profil sagittal + trous M4 de fixation |
| **Temps estimé** | **~15 minutes au total pour les 2 plaques** |

---

## 3. Traverse Horizontale Ø30 mm & Nœud Central Demi-Coquilles

### A. Spécifications du Tube Carbone

> [!IMPORTANT]
> **Orientation du tube** : Le tube carbone est transversal (axe X, gauche ↔ droite). Il passe perpendiculairement au plan sagittal des plaques de colonne. Le tube **ne traverse pas** la tôle pleine : il s'insère dans le joint naturel entre la Colonne Supérieure et la Colonne Inférieure, au niveau de l'axe des épaules (h = 290 mm), enserré par les deux demi-coquilles alu.

| Paramètre | Valeur |
|:---|:---|
| **Matériau** | Tube carbone 3K, époxy, Ø30 mm extérieur / Ø26 mm intérieur (paroi 2.0 mm) |
| **Longueur** | ~260 mm (entraxe des brides d'épaule) |
| **Axe** | **Transversal (X)**, perpendiculaire au plan sagittal des plaques |
| **Masse** | ~70 g |
| **Rigidité torsionnelle** | J ≈ 52 000 mm4 (×15 par rapport à une plaque de 5 mm de même largeur) |
| **Fixation aux épaules** | Emmanché sur 35.0 mm dans la bride monobloc Alu 7075-T651, fente de pincement 2×M4 + goupille Ø4×40 mm sur bouchon alu interne |
| **Fixation centrale (nœud)** | **2 demi-coquilles CNC Alu 7075-T6** (Bride Sup. + Bride Inf., 120×45×21 mm) serrant le tube sur 45 mm, boulonnées aux plaques |

---

### B. Nœud d'Intersection Plaque/Traverse — Système Demi-Coquilles

![Nœud d'intersection — Système Demi-Coquilles Alu CNC](./media/noeud_demi_coquilles_bride.svg)

*Vue en coupe frontale (plan sagittal Y-Z) et vue de dessus (plan transversal X-Y) du nœud d'intersection. Le tube carbone Ø30 mm est transversal (axe X). La Bride Supérieure s'appuie sur la face inférieure de la Colonne Supérieure via ses ailes en L ; la Bride Inférieure s'appuie sur la face supérieure de la Colonne Inférieure. Les deux brides sont serrées l'une contre l'autre par 4× vis M6 traversantes + écrous Nylstop, créant le pincement du tube carbone sur 45 mm de portée.*

#### Bénéfices Mécaniques & Optimisation Géométrique :
1. **Plaques de colonne 100% continues** : Aucun perçage affaiblissant dans la tôle de 5 mm au point de moment maximal (M = 131 N.m dynamique).
2. **Distribution d'effort sur 120 mm** : Les ailes en L portent sur toute la largeur sagittale des plaques.
3. **Pincement fiable sans taraudage fragile** : Vis M6 traversantes avec écrous frein Nylstop (pression de contact 6.3 MPa sur le composite).
4. **Épaisseur de demi-bride optimisée (6.0 mm au dos du demi-alésage R15)** : Hauteur unitaire d'une demi-bride = 21.0 mm (hauteur totale du nœud assemblé = **42.0 mm**, au lieu de 60.0 mm sur-dimensionnés), libérant **18.0 mm d'espace vertical libre** dans le torse et réduisant la masse de -115 g.
5. **Verrouillage positif par goupille Ø4 mm (axe Z vertical décalée à X = 12.0 mm)** : La goupille est **décalée latéralement en X** pour contourner la tranche de la plaque sagittale centrale (5.0 mm). Traversante sur 42.0 mm de hauteur (Bride Sup 6.0 mm + tube 30.0 mm + Bride Inf 6.0 mm), elle utilise la même **goupille élastique standardisée Ø 4.0 mm × 40 mm (ISO 8752 Inox)** que les épaules.
6. **Dépouille de serrage du plan de joint (Split Gap = 1.0 mm net / 0.8 à 1.0 mm)** : Chaque demi-alésage cylindrique est usiné à une profondeur de **14.5 mm** (au lieu de 15.0 mm théorique, soit un surfaçage à Z = -0.5 mm sur le plan de joint). Cette cote garantit un **espace libre de 1.0 mm net** entre la Bride Supérieure et la Bride Inférieure à l'assemblage, interdisant toute butée prématurée aluminium contre aluminium et convertissant 100% de la précharge des 4 vis M6 en pression radiale directe (6.3 MPa, friction > 12 000 N) sur le composite carbone.

---

### C. Stratégie de Perçage Vertical Z sur NestWorks C500

| Goupille | Position | Direction | Diamètre | Profondeur | Outillage C500 |
|:---|:---|:---:|:---:|:---:|:---|
| **Nœud central** | Brides demi-coquilles (décalée à X = 12.0 mm) | **Axe Z (Vertical)** | Ø4 mm H7 | **40 mm à 42 mm** | **C500 — 3 axes direct (broche Z)** |
| **Ancrage épaule gauche** | Bride alu 7075 + tube extrémité gauche | Axe Z (Vertical) | Ø4 mm H7 | **40 mm** | C500 — 3 axes direct |
| **Ancrage épaule droit** | Bride alu 7075 + tube extrémité droit | Axe Z (Vertical) | Ø4 mm H7 | **40 mm** | C500 — 3 axes direct |

> [!TIP]
> **Toutes les goupilles sont axées en Z (Verticales) et standardisées en Ø 4.0 mm × 40 mm.** Elles sont donc 100% réalisables en 3 axes directs par la broche Z de la NestWorks C500, sans aucun 4ème axe rotatif requis.

---

## 4. Architecture Finale des Épaules : Cages H-Bracket Alu 7075-T6 & Brides Monoblocs

### A. Architecture : Cage H-Bracket & Bride Monobloc d'Épaule (×2 épaules)

![Schéma d'Architecture Vectoriel Blueprint — Cage H-Bracket & Bride Épaule RS-04 D-Bot V1](./media/hbracket_rs04_quasi_final_blueprint.svg)

*Blueprint d'ingénierie 2D de l'assemblage d'épaule quasi-final (Fusion 360). Vue de Face (Plan Y-Z) : stator RS-04 Ø120 mm + 2 plaques H-bracket 5 mm 7075-T6 identiques évidées à Ø95 mm (10× vis M4 sur PCD Ø106 mm) + 2 tirants M5 aux oreilles diagonales à 23.4° (Z=±66.1 mm, Y=±28.6 mm, R=72 mm). Vue Latérale / Coupe (Plan X-Z) : sandwich axial 49 mm (Plaque avant orange 5 mm -> Stator RS-04 39 mm -> Plaque arrière orange 5 mm + Bride jaune 48.2 mm), tirants axiaux CHC M5×60 mm, tube carbone Ø30 mm avec bouchon interne alu Ø26/18×34.5 mm, pincement radial 2×M4 et goupille Ø4×40 mm Mecanindus.*

> [!IMPORTANT]
> **Évidement Central Ø95 mm (epaule9.png)** : Les plaques 5 mm 7075-T6 sont évidées au centre sous forme de couronne annulaire (Ø ext 120 mm / Ø int 95 mm, largeur radiale 12.5 mm). Cet évidement procure un **gain de masse massif de -100 g par plaque (soit -400 g sur le torse pour les 4 plaques !)** tout en dégageant le passage des câbles XT30/CAN-FD et la ventilation directe du stator RS-04.

---

### B. Nomenclature & Spécifications de la Cage H-Bracket (Par Épaule)

| Paramètre | Valeur |
|:---|:---|
| **Plaques H-bracket (orange, ×2 par épaule)** | **Alu 7075-T6, 5.0 mm** (2 plaques IDENTIQUES : Avant + Arrière, **Évidement central Ø95mm** -> gain -400g total sur torse) → couronne annulaire Ø120/Ø95mm + 2 oreilles cylindriques pour tirants M5 → **10× vis M4 sur PCD Ø106mm** sur stator RS-04 (pince radiale = 3.35 mm, Sf_bearing = 61) |
| **Perçage oreilles M5 (CNC C500)** | **Ø 5.5 mm (ISO 273 — Moyen)** → jeu radial 0.25 mm pour empilement sans contrainte + **chanfreins 0.5 mm × 45°** sur les 2 faces |
| **Bride fixation tube (jaune/bleue, 1 par épaule)** | **Bride monobloc Alu 7075-T651, 48.20 mm total** → flasque 13.20 mm + socket tube 35.0 mm (L/D=1.17) + fente pincement 2×M4 + goupille Ø4×40 mm. Se monte **par-dessus la plaque arrière orange** et se fixe au stator par 6 vis M4 traversantes. Sourcing: disque brut Ø120×50 mm Blockenstock |
| **Bouchon interne anti-écrasement (×1 par bride)** | **Alu 7075-T651, Ø 26.0 ext / Ø 18.0 int × 34.5 mm de long** → collé à l'époxy dans le tube carbone Ø 30×26 mm (jeu axial 0.5 mm). Absorbe la pression de pincement et sert d'appui direct pour la goupille Ø 4.0 mm |
| **Fixation Stator AVANT (×10 vis M4 par épaule)** | **Vis CHC M4 × 10 mm (ISO 4762 / DIN 912 classe 8.8 ou Inox A2)** — Vissage direct à travers la plaque avant 5.0 mm dans les 10 trous borgnes M4 sur PCD Ø106 mm du stator RS-04 (engagement 4.2 mm) |
| **Fixation Stator ARRIÈRE — Hors Bride (×4 vis M4 par épaule)** | **Vis CHC M4 × 10 mm (ISO 4762 / DIN 912 classe 8.8 ou Inox A2)** — Vissage direct à travers la plaque arrière 5.0 mm seule sur les 4 trous exposés du PCD Ø106 mm (engagement 4.2 mm) |
| **Fixation Bride Épaule + Stator ARRIÈRE (×6 vis M4 par épaule)** | **Vis CHC M4 × 25 mm (ISO 4762 / DIN 912 classe 8.8 ou 10.9 ou Inox A2)** — Traversant la flasque de bride (13.20 mm) + plaque arrière (5.00 mm) + rondelle (0.8 mm) dans les 6 trous borgnes du stator RS-04 (engagement 5.2 à 6.0 mm) |
| **Perçage stator plaques 5mm (CNC C500)** | **Ø 4.3 mm (ISO 273 — Moyen)** sur PCD Ø 106.0 mm (10 trous par plaque) + **chanfreins 0.5 mm × 45°** |
| **Perçage flasque bride 13.2mm (CNC C500)** | **Ø 4.3 mm (ISO 273 — Moyen)** sur PCD Ø 106.0 mm (6 trous traversants) + **chanfreins 0.5 mm × 45°** |
| **Rondelles stator & bride (×20 par épaule)** | **ISO 7089 / DIN 125A (M4)** → Ø int. 4.3 mm / Ø ext. 9.0 mm, épaisseur 0.8 mm (10 sur face avant, 4 sur plaque arrière hors bride, 6 sur flasque de bride) |
| **Pincement radial tube (×2 vis M4 par bride)** | **Vis CHC M4 × 18 mm ou M4 × 20 mm (ISO 4762 / DIN 912 classe 8.8 ou 10.9 zingué)** — Traversantes sur bloc de pincement de 11.0 mm de largeur (vis #1 à 8.0 mm du bord, vis #2 à 25.0 mm du bord, entraxe 17.0 mm) |
| **Perçage pincement M4 (CNC C500)** | **Ø 4.3 mm (ISO 273 — Moyen)** → perçage traversant sur méplats + **chanfreins 0.5 mm × 45°** |
| **Rondelles pincement (×4 par bride)** | **ISO 7089 / DIN 125A (M4)** → Ø int. 4.3 mm / Ø ext. 9.0 mm, épaisseur 0.8 mm (2 sous tête vis CHC, 2 sous écrou Nylstop M4) |
| **Écrous frein pincement (×2 par bride)** | **ISO 7040 / DIN 985 — M4 (Nylstop)** → écrou hexagonal autofreiné avec bague nylon, hauteur 4.0 mm |
| **Goupille sécurité bride (×1 par bride)** | **Goupille élastique Mécanindus Ø 4.0 mm × 40 mm (ISO 8752 / DIN 1481 Inox)** → perçage Ø 4.0 mm H7 traversant toute la douille alu (40.0 mm) et le bouchon alu interne (s'aligne à fleur Ø 40 mm) |
| **Tirants M5 axiaux (×2 par épaule)** | **Vis CHC M5 × 60 mm (ISO 4762 / DIN 912 classe 8.8 ou 10.9 zingué)** — Longueur optimale validée pour empilement 49.0 mm à 51.0 mm (saillie bague nylon = +2.4 mm) |
| **Rondelles tirants (×4 par épaule)** | **ISO 7089 / DIN 125A (M5)** → Ø int. 5.3 mm / Ø ext. 10.0 mm, épaisseur 1.0 mm (2 sous tête vis CHC, 2 sous écrou Nylstop) |
| **Écrous frein tirants (×2 par épaule)** | **ISO 7040 / DIN 985 — M5 (Nylstop)** → écrou hexagonal autofreiné avec bague nylon, hauteur 5.0 mm |
| **Position tirant HAUT** | Z = +66.1 mm, Y = +28.6 mm (R = 72 mm, angle 23.4° de la verticale) |
| **Position tirant BAS** | Z = -66.1 mm, Y = -28.6 mm (diamétralement opposé) |
| **Sourcing plaques 5mm 7075-T6** | Blockenstock — chute 5×160×160 mm 7075-T6 @ 9.60 EUR/pièce — **4 pièces** (2 avant + 2 arrière) → 38.40 EUR |
| **Sourcing bride 48.2mm** | Blockenstock — disque Ø 120×50 mm alu 7075-T651 @ ~25.00 EUR/pièce — **2 pièces** (une par épaule) → ~50.00 EUR |
| **Sourcing bouchons alu** | Blockenstock — barre ronde [Ø 30×500 mm Alu 7075-T651 filé](https://www.blockenstock.fr/c-30x500mm-alu-7075-file-t651-c2x21035319) @ **16.20 EUR TTC (13.50 EUR HT)** — **1 pièce** |
| **Sourcing demi-coquilles nœud central** | Blockenstock — plat méplat [25×50×500 mm Alu 7075-T6](https://www.blockenstock.fr/25x-50x500mm-alu-7075-t6-c2x21792953) @ **39.38 EUR TTC (32.82 EUR HT)** — **1 pièce** (débit en 2 tronçons de 135 mm) |

---

### C. Calcul d'Empilement & Validation Constructeur RobStride RS-04

> [!NOTE]
> **Vérification Constructeur RobStride RS-04 (Manuel Constructeur Page 10)** :
> - **Taraudages Stator** : PCD Ø 106.0 mm (+/- 0.1 mm), 10 taraudages M4 borgnes par face, profondeur borgne = **5.0 mm Min à 6.0 mm Max**.
> - **Consigne d'Avertissement Constructeur** : *"When fixing, the screw depth should not exceed the depth of the casing thread"* (La pénétration de la vis ne doit pas excéder la profondeur du filetage).
>
> **1. Fixation Stator Directe sur Plaque 5 mm (CHC M4 × 10 mm — 10 vis AV + 4 vis AR)** :
> - Plaque H-bracket 7075-T6 : 5.00 mm + Rondelle DIN 125A M4 : 0.80 mm = **5.80 mm sous tête**.
> - Pénétration dans le stator : $10.00 - 5.80 = \mathbf{4.20\text{ mm}}$.
> - Conforme à la règle constructeur : $4.20\text{ mm} \le 5\text{ à }6\text{ mm}$, tenue optimale ($> 1\times D = 4.0\text{ mm}$) et **garde de sécurité de 1.80 mm au fond du trou borgne**.
>
> **2. Fixation Bride d'Épaule + Plaque 5 mm sur Stator (CHC M4 × 25 mm — 6 vis AR)** :
> - Flasque de bride d'épaule : 13.20 mm + Plaque arrière : 5.00 mm + Rondelle : 0.80 mm = **19.00 mm sous tête**.
> - Pénétration dans le stator : $25.00 - 19.00 = \mathbf{6.00\text{ mm}}$ (ou **5.20 mm** avec rondelle élastique/Nord-Lock de 1.6 mm).
> - Conforme à la règle constructeur : engagement net de 5.2 à 6.0 mm sans risque de talonnage.
>
> **3. Vis de Pincement Radial (CHC M4 × 18 mm ou M4 × 20 mm)** :
> - Bloc de pincement (11.0 mm) + 2 rondelles DIN 125A (1.6 mm) + Écrou Nylstop M4 (4.0 mm) + Saillie 2 filets (1.4 mm) = **18.0 mm**.
>
> **4. Vis Tirant M5 (CHC M5 × 60 mm)** :
> - Plaque AV (5.0 mm) + Corps RS-04 (39.0 à 41.0 mm) + Plaque AR (5.0 mm) = 49.0 à 51.0 mm. Accessoires (2× rondelles 1.0 mm + écrou Nylstop 5.0 mm + saillie 1.6 mm) = 7.6 mm. Total = **56.6 mm** (vis **ISO 4762 CHC M5 × 60 mm** exacte).

> [!CAUTION]
> **RÈGLE CRITIQUE CAO : FENTE DE PINCEMENT DU TUBE (Split Gap = 1.0 mm)** :
> Ne **JAMAIS** dessiner une fente de pincement de 0.1 mm dans Fusion 360 ! 
> Lors du serrage des vis M4 à 3.0 N.m, une fente de 0.1 mm provoque une **butée franche prématurée alu contre alu**, ce qui absorbe 100% de la force de serrage et **annule toute pression radiale sur le tube carbone**.
> La fente de pincement doit impérativement avoir une ouverture de **1.0 mm net (±0.1 mm)** sur toute la portée de 35.0 mm.

---

### D. Tutoriel : Importation McMaster-Carr dans Fusion 360

> [!TIP]
> **Procédure d'importation pas-à-pas :**
> 1. Dans Fusion 360, aller dans **Insert** ➔ **Insert McMaster-Carr Component**.
> 2. Rechercher et sélectionner les références exactes :
>    - **Vis CHC M4 × 10 mm Stator Direct (ISO 4762)** : `M4 x 10 Socket Head Screw` ➔ *Metric* ➔ *M4* ➔ *10 mm* (Réf McMaster **`91290A150`** Acier 12.9 ou **`92290A140`** Inox 18-8).
>    - **Vis CHC M4 × 25 mm Bride Épaule (ISO 4762)** : `M4 x 25 Socket Head Screw` ➔ *Metric* ➔ *M4* ➔ *25 mm* (Réf McMaster **`91290A170`** Acier 12.9 ou **`92290A148`** Inox 18-8).
>    - **Vis CHC M4 × 18 mm Pincement (ISO 4762)** : `M4 x 18 Socket Head Screw` (ou `M4 x 20`) ➔ *Metric* ➔ *M4* ➔ *18 mm* (ou *20 mm*).
>    - **Vis CHC M5 × 60 mm Tirants (ISO 4762)** : `M5 x 60 Socket Head Screw` ➔ *Metric* ➔ *M5* ➔ *60 mm* (Réf McMaster **`91290A268`**).
>    - **Rondelles M4 (DIN 125A / ISO 7089)** : `M4 Flat Washer` ➔ *Metric* ➔ *For M4 Screw Size* (Réf McMaster **`93475A230`** Inox 18-8, Ø int 4.3 mm, Ø ext 9.0 mm, ép. 0.8 mm).
>    - **Rondelles M5 (DIN 125A / ISO 7089)** : `M5 Flat Washer` ➔ *Metric* ➔ *For M5 Screw Size* (Réf McMaster **`93475A240`** Inox 18-8, Ø int 5.3 mm, Ø ext 10.0 mm, ép. 1.0 mm).
>    - **Écrous Nylstop M4 (DIN 985 / ISO 7040)** : `M4 Nylon-Insert Locknut` ➔ *Metric* ➔ *M4 Thread*.
>    - **Écrous Nylstop M5 (DIN 985 / ISO 7040)** : `M5 Nylon-Insert Locknut` ➔ *Metric* ➔ *M5 Thread* (Réf McMaster **`90631A113`**).
>    - **Goupille Élastique Mécanindus Ø 4.0 mm × 40 mm (ISO 8752)** : `4mm Slotted Spring Pin 40mm` ➔ *Pins* ➔ *Spring Pins* ➔ *Slotted Pins* ➔ *Metric* ➔ *4 mm Diameter* ➔ *40 mm Length* (Réf McMaster **`98380A425`** Inox ou **`92383A211`** Acier Ressort).
> 3. Dérouler la section *Product Detail*, sélectionner **3D STEP** et cliquer sur **Download**.
> 4. Appliquer une contrainte **Joint** (`J`) coaxial sur les perçages.

---

### E. Validation CAO Fusion 360 (Vérification epaule1 à epaule9)

![Vue d'Ensemble 3D Fusion 360 de l'Assemblage d'Épaule Quasi-Final](./media/epaule_cao_1_vue_ensemble.png)
*Figure 4.1 (epaule1) : Vue d'ensemble 3D de l'assemblage complet d'épaule : les 2 plaques H-bracket identiques (orange) en Aluminium 7075-T6 (5.0 mm), la bride d'ancrage d'épaule monobloc (jaune) en Aluminium 7075-T651 (48.20 mm total), le tube carbone Ø30 mm (bleu) et le moteur RS-04.*

![Vue de Profil du Sandwich Épaule](./media/epaule_cao_2_vue_profil.png)
*Figure 4.2 (epaule2) : Vue de profil montrant le sandwich axial : Plaque avant orange (5.0 mm) -> Moteur RS-04 (39 mm) -> Plaque arrière orange (5.0 mm) + Bride d'ancrage jaune (48.20 mm).*

![Mesure d'Emprise de 35.00 mm du Tube Carbone](./media/epaule_cao_3_cotation_emprise_35mm.png)
*Figure 4.3 (epaule3) : Cotation CAO de la longueur de portée de l'alésage tube carbone : **35.00 mm net** (ratio L/D = 1.17, supérieur au standard ISO 1.0×D = 30.0 mm).*

![Mesure de l'Épaisseur du Flasque Plat de 13.20 mm](./media/epaule_cao_4_cotation_flasque_13.2mm.png)
*Figure 4.4 (epaule4) : Cotation CAO de l'épaisseur de la flasque d'embase de la bride jaune : **13.20 mm net**.*

![Validation de l'Épaisseur de 5.00 mm de la Plaque 7075-T6](./media/epaule_cao_5_cotation_plaque_5mm.png)
*Figure 4.5 (epaule5) : Cotation CAO de l'épaisseur de la plaque H-bracket orange : **5.00 mm net en Aluminium 7075-T6**.*

![Vue Face Avant Bras RS-04 et Vis M5 Stator](./media/epaule_cao_6_vue_face_bras_6xM5.png)
*Figure 4.6 (epaule6) : Vue de face avant (côté bras) du moteur RS-04.*

![Vue Face Arrière Torse et Ancrage Tube Carbone](./media/epaule_cao_7_vue_arriere_torse.png)
*Figure 4.7 (epaule7) : Vue face arrière (côté torse) montrant l'intégration de la bride d'ancrage jaune et de la colonne vertébrale (5.0 mm).*

![Validation de la Hauteur Hors-Tout de 48.20 mm de la Bride Monobloc](./media/epaule_cao_8_hauteur_hors_tout_48.2mm.png)
*Figure 4.8 (epaule8) : Mesure de la hauteur hors-tout axiale de la bride d'épaule monobloc : **48.20 mm net** (valide le brut disque Blockenstock Ø 120 × 50 mm).*

![Validation de l'Évidement Central Ø95 mm des Plaques H-Bracket](./media/epaule_cao_9_evidement_central_95mm.png)
*Figure 4.9 (epaule9) : Vue axiale de la plaque H-bracket orange montrant l'évidement central **Ø 95.0 mm** (gain -400 g sur le torse et aération RS-04).*

---

### F. Performance Roll Validée

| Solution | I_roll (mm4) | Flèche au cou | Espace batterie |
|:---|:---:|:---:|:---:|
| Sans renfort | 23 682 | ~1.5 mm | ✅ Libre |
| Tirants verticaux ±60 mm (abandonnée) | 164 802 | ~0.21 mm | ❌ Occupé |
| **Cage H-bracket 23.4°, R=72mm (retenue V1)** | **366 262** | **~0.097 mm** | ✅ **Libre à 100%** |

---

## 5. Coque Secondaire PA12-CF & Impression Verticale

### A. Justification de l'Impression Verticale (Debout)

Avec le squelette cruciforme reprenant tous les efforts structurels, la coque PA12-CF n'est plus la structure porteuse primaire. Cela autorise l'impression **verticale** (torse debout), réduisant de 75% le volume de supports.

![Orientation d'impression FDM verticale des demi-torses en PA12-CF](./media/orientation_impression_verticale.svg)

---

### B. Stratégie de Découpe CAO : 2 Anneaux 360° Monoblocs

Pour imprimer dans le volume de la **Qidi Plus 4** (305 × 305 × 280 mm) :
1. **Thorax Haut** (hauteur ~216 mm) : Imprimé collet du cou vers le haut, plan de coupe abdominal sur le plateau.
2. **Abdomen Bas** (hauteur ~190 mm) : Imprimé taille vers le bas, plan de coupe abdominal vers le haut.
3. **Plan de Joint Abdominal (Lap Joint 3.0 mm)** : Profilé rainure-languette (1.5 mm × 2.0 mm) avec jeu de 0.2 mm, verrouillé par 6 à 8 vis CHC M4 prenant prise dans des inserts laiton Ruthex M4 chauffés.

---

## 6. Paramètres de Tranchage (OrcaSlicer / Qidi Plus 4)

### A. Paramètres Globaux (Zone Courante)

| Paramètre (FR) | Slicer Setting Name (EN) | Recommended Value | Note |
|:---|:---|:---:|:---|
| Diamètre de buse | **Nozzle Diameter** | `0.4 mm` | Type : **Tungsten Carbide** (Carbure de Tungstène) |
| Hauteur de couche | **Layer Height** | `0.20 mm` | Précision et vitesse équilibrées |
| Nombre de parois | **Wall Loops** | **`4`** | Épaisseur de paroi 1.92 mm |
| Couches sup. / inf. | **Top / Bottom Shell Layers** | **`4` / `4`** | Fermeture propre |
| Motif de remplissage | **Infill Pattern** | `Gyroid` | Isotrope |
| Taux de remplissage | **Infill Density** | **`20%`** | Coque secondaire allégée |
| Température de buse | **Nozzle Temperature** | `290°C - 295°C` | PA12-CF |
| Température plateau | **Bed Temperature** | `85°C - 90°C` | Magigoo PA |
| Chambre chauffée | **Chamber Temperature** | `60°C` | Indispensable pour PA12-CF |
| Type de supports | **Enable Support** | `Tree (Organic)` | **Support on Build Plate Only** |

---

### B. Zone d'Épaule : Modifier Volume Cylindrique

Pour renforcer localement le collet d'épaule dans le slicer :
1. Clic droit sur le modèle Thorax ➔ **Add Modifier** ➔ **Cylinder**.
2. Dimensionner : `Size X = 120 mm`, `Size Y = 120 mm`, `Size Z = 80 mm`.
3. Positionner le cylindre centré sur le collet d'épaule.
4. Surcharger les paramètres locaux : **Wall loops = 6**, **Infill density = 35%**, **Top/Bottom layers = 6**.

---

### C. Prototype de Validation en PLA

| Paramètre PLA | Valeur | Note |
|:---|:---:|:---|
| **Layer Height** | `0.28 mm` | Mode draft rapide |
| **Wall Loops** | `3` | Suffisant pour test d'ajustement |
| **Infill Density** | `10% - 15% (Grid)` | Gain de temps |
| **Chamber Temperature** | **`0°C (OFF / Capot ouvert)`** | Évite le bouchage (heat creep) |
| **Part Cooling Fan** | `100%` | Refroidissement maximal PLA |

---

## 7. Système de Batteries : 2 Paniers Latéraux Hot-Swap

### A. Architecture des Paniers Symétriques

Les tirants d'épaule à 23.4° libérant l'espace latéral sous les épaules, le torse intègre **2 paniers latéraux symétriques** coulissant depuis l'arrière :

![Vue de dessus des paniers batteries latéraux](./media/paniers_batteries_hot_swap_vue_dessus.svg)

*Vue de dessus des 2 paniers batteries latéraux guidés entre la coque extérieure et la plaque sagittale centrale.*

| Paramètre | 2 Batteries Latérales (V1) |
|:---|:---:|
| **Configuration** | **2× Packs 12S NMC 48V (5Ah à 6Ah)** |
| **Énergie totale** | **480 Wh à 576 Wh** (+20% vs batterie unique) |
| **Tension nominale** | 44.4 V (parallèle via diodes ORing) |
| **Dimensions unitaires** | ~220 × 50 × 65 mm chacune |
| **Guidage & Coulissement** | Rails PA12-CF + cornières alu 10×10 mm sur la plaque sagittale + bandes PTFE 0.2 mm |
| **Verrouillage** | Loquet quart-de-tour (Dzus) accessible depuis l'arrière |

---

### B. Circuit Électrique Hot-Swap ORing

Le circuit permet de remplacer un pack batterie à chaud sans interruption de tension pour les calculateurs et contrôleurs :

![Schéma électrique Hot-Swap ORing avec Diodes Schottky](./media/schema_electrique_hot_swap_oring.svg)

| Composant | Référence | Spécifications | Rôle |
|:---|:---|:---|:---|
| **2× Diodes Schottky** | **MBR4060PT** (TO-247) | 40A, 60V, V_forward = 0.45V | Diodes ORing montées sur radiateurs alu fixés à la plaque sagittale |
| **2× BMS 12S** | BMS 12S 20A-30A | Protection intégrée pack | Protection surcharge / décharge |
| **4× Connecteurs** | **XT60** mâle/femelle | 60A max, câble 10 AWG silicone | Connexion automatique en fin de course de panier |
| **1× Fusible PTC** | Resettable 40A | Protection bus principal | Sécurité PDB |

---

## 8. Liaisons d'Extrémités (Cou & Waist Yaw RS-06)

### A. Plaque Supérieure de Cou (Alu 6061-T6, 5.0 mm)
* **Fonction** : Fermeture haute du torse, fixation du collet de cou pour le RS-05 Yaw/Pitch, ancrage de la plaque sagittale haute via équerres L-Brackets sandwich.

### B. Plaque Inférieure / Waist Plate (Alu 6061-T6, 6.0 mm)
* **Fonction** : Fermeture basse du torse, interface rigide avec le module Waist Yaw actif.
* **Moteur Waist** : **RobStride RS-06** (36 N.m pic / 11 N.m nominal, Ø88 mm, 621 g, CAN-FD ID 21).
* **Bague d'adaptation CNC** : Alu 6061-T6 (Ø int. 88 mm / Ø ext. 115.6 mm, épaisseur radiale 13.8 mm) adaptant le carter Asimov v1 au moteur RS-06.
* **Roulement** : Section fine Ø110 mm à 4 points de contact.

---

## 9. Workflow de Fabrication Révisé (Plan d'Action Pas-à-Pas)

### Phase 1 — Conception CAO (Fusion 360)
1. ☐ Mettre à l'échelle (+18%) les fichiers originaux Asimov v1.
2. ☐ Modéliser la **plaque de colonne sagittale à lumières 2D** (Option B, R = 18 mm) en 2 parties.
3. ☐ Modéliser les **2 cages H-bracket d'épaule** : Plaques 5 mm Alu 7075-T6 évidées à Ø95 mm + Brides monoblocs 48.2 mm Alu 7075-T651 reliées par les 2 tirants M5 à 23.4° ($R = 72\text{ mm}$).
4. ☐ Modéliser le **nœud d'intersection** à demi-coquilles (Bride Sup. + Bride Inf. Alu 6061-T6).
5. ☐ Dessiner les **2 paniers batterie latéraux** et les coulisses centrales sur la plaque sagittale.
6. ☐ Réaliser le **split abdominal rigide** (Lap Joint 3 mm, inserts laiton M4).
7. ☐ Modéliser la **bague d'adaptation CNC pour RS-06**.

### Phase 2 — Usinage CNC (NestWorks C500)
1. ☐ Usiner les 2 demi-plaques de colonne sagittale (Alu 6061-T6, 5 mm — lumières 2D traversantes).
2. ☐ Usiner les **4 plaques H-bracket (5 mm)** (2 avant + 2 arrière identiques) dans la tôle **Alu 7075-T6 5×160×160 mm Blockenstock** — Évidement central Ø 95 mm, 10 trous lisses **Ø 4.3 mm (ISO 273 Moyen)** sur PCD Ø 106 mm + 2 perçages tirants M5 à **Ø 5.5 mm** avec chanfreins 0.5 mm × 45°.
3. ☐ Usiner les **2 brides d'épaule monoblocs (H = 48.20 mm)** dans les disques bruts **Ø 120 × 50 mm Alu 7075-T651 Blockenstock** — alésage Ø 30.05 mm H7 sur 35.0 mm, flasque 13.2 mm, fente 1.0 mm et trou goupille Ø 4.0 mm H7.
4. ☐ Usiner les **2 bouchons internes anti-écrasement (Ø 26.0 mm h6 ext / Ø 18.0 mm int × 34.5 mm de long)** dans la **barre ronde Alu 7075-T651 Ø 30 mm Blockenstock**.
5. ☐ Usiner les **2 demi-coquilles du nœud central (120×45×21 mm)** dans le plat brut **25×50×500 mm Alu 7075-T6 Blockenstock** — demi-alésage usiné à 14.5 mm de profondeur (surfaçage Z = -0.5 mm) pour créer le **Split Gap de 1.0 mm**, perçages lisses Ø 6.3 mm pour les 4 vis M6 traversantes.
6. ☐ Usiner la plaque de cou (Alu 5 mm) et la Waist Plate (Alu 6 mm).
7. ☐ Usiner la bague d'adaptation RS-06 (Alu 6061-T6).
8. ☐ Couper le tube carbone Ø30 mm à ~260 mm, chanfreiner et percer la goupille centrale Ø 4.0 mm × 40 mm (décalée à X = 12.0 mm) à travers le nœud assemblé.

### Phase 3 — Impression 3D (Qidi Plus 4)
1. ☐ **Prototype PLA** : Imprimer les 2 demi-coques verticalement en PLA (couche 0.28 mm) pour valider les ajustements.
2. ☐ **Version finale PA12-CF** : Imprimer verticalement (Thorax haut + Abdomen bas) avec Modifier Volume cylindrique aux épaules (6 parois, 35% infill).
3. ☐ Supports arborescents (`Tree`) uniquement sous les collerettes d'épaule (`Build Plate Only`).

### Phase 4 — Assemblage Mécanique de Précision & Serrage Dynamométrique
1. ☐ Poser les inserts filetés M4 en laiton dans les coques PA12-CF (260°C).
2. ☐ Assembler la plaque sagittale 2D et le nœud central sur la traverse carbone Ø30 mm avec sa goupille centrale Ø 4.0 mm × 40 mm (décalée à X = 12.0 mm).
3. ☐ Monter les cages H-bracket d'épaule :
   - Insérer les bouchons alu 7075 (34.5 mm) dans le tube carbone Ø30 mm.
   - Poser la bride 48.2 mm sur le tube et **insérer la goupille Mécanindus Ø 4.0 mm × 40 mm Inox** au maillet plastique.
   - Monter les tirants axiaux M5 (**Vis CHC M5 × 60 mm ISO 4762** + rondelles DIN 125A + écrous Nylstop M5).
4. ☐ Appliquer le **Protocole de Serrage Dynamométrique à 3.0 N.m** sur les 2× vis M4 de pincement de chaque bride (avec écrous Nylstop M4 + rondelles Nord-Lock, sans Loctite).
5. ☐ Monter les moteurs RS-04 dans les cages d'épaule :
   - Face Avant : **10× Vis CHC M4 × 10 mm (ISO 4762)** + rondelles DIN 125A M4 (engagement 4.20 mm).
   - Face Arrière : **4× Vis CHC M4 × 10 mm** (hors bride) + **6× Vis CHC M4 × 25 mm** (traversant bride 13.2 mm + plaque 5.0 mm, engagement 5.2 à 6.0 mm).
   - Router les câbles XT30/CAN par l'évidement central Ø95 mm.
6. ☐ Assembler la plaque de cou et la Waist Plate via les équerres L-Brackets.
7. ☐ Assembler le Thorax et l'Abdomen via le Lap Joint et les vis M4 des bossages.

### Phase 5 — Intégration Électrique & Batteries Hot-Swap
1. ☐ Monter les diodes Schottky MBR4060PT sur leurs radiateurs alu vissés sur la plaque sagittale.
2. ☐ Câbler les connecteurs XT60 à l'arrière des paniers et le bus 48V vers la PDB Matek.
3. ☐ Insérer les 2 packs batterie et tester le basculement hot-swap sans coupure.

### Phase 6 — Liaison Waist Yaw
1. ☐ Monter la bague d'adaptation CNC sur le moteur RS-06.
2. ☐ Poser le roulement à section fine Ø110 mm sous la Waist Plate et accoupler le rotor RS-06 au centre de la Waist Plate.
3. ☐ Raccorder le bus CAN-FD (ID 21) et la puissance 48V.

---

## 10. Questions Ouvertes Résolues & Points d'Attention

* ✅ **Fixation Stator RS-04** : Validée sur le manuel officiel RobStride (profondeur borgne 5 à 6 mm, PCD Ø106 mm × 10 vis M4).
* ✅ **Liaison Tube-Bride** : 100% mécanique sans collage (pincement 2×M4 à 3.0 N.m sur fente 1.0 mm + bouchon alu 7075 + goupille Ø4×40 mm affleurante).
* ✅ **Rigidité Roll** : Validée par la cage H-Bracket (tirants M5 à 23.4°, $R = 72\text{ mm}$, flèche < 0.1 mm), libérant l'espace pour le hot-swap des batteries.
* ⚠️ **Attention Atelier** : Toujours engager la goupille Mécanindus Ø 4.0 mm **AVANT** de réaliser le serrage dynamométrique final des vis M4 de pincement de la bride.
