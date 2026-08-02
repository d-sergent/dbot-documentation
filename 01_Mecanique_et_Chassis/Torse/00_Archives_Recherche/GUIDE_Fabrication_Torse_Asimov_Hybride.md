# ⚠️ DOCUMENT OBSOLÈTE — Ne plus utiliser pour la conception

> [!CAUTION]
> **Ce document est obsolète depuis Mai 2026.** Il a été remplacé par le [GUIDE_Fabrication_Torse_D-Bot_Hybride.md](./GUIDE_Fabrication_Torse_D-Bot_Hybride.md) qui intègre :
> - L'architecture **cruciforme interne** (plaque isogrid sagittale + traverse carbone)
> - Les **2 paniers batterie latéraux** avec hot-swap
> - L'orientation d'impression **verticale** (au lieu de « dos au plateau »)
> - Les **cylindres d'épaule alu** (au lieu des disques plats)
> - Les paramètres d'impression **allégés** (coque secondaire)
>
> Le présent document est conservé comme archive historique du raisonnement d'ingénierie initial.

---

# 🛠️ ~~Guide de Fabrication Hybride : Torse Asimov v1 (FDM PA12-CF + CNC Alu)~~ (ARCHIVÉ)

Ce document trace la méthodologie d'ingénierie révisée pour fabriquer et assembler la coque centrale du torse de l'Asimov v1 (initialement conçue pour le frittage de poudre industriel MJF) en l'adaptant aux capacités d'un atelier maker avancé (Imprimante FDM **Qidi Plus 4** + CNC Desktop **C500**) et aux exigences de couple des moteurs RobStride RS-04 (120 N.m).

---

## 1. Le Défi Structurel : MJF vs FDM et efforts d'épaules

*   **Le design d'origine (MJF)** : La coque Asimov d'origine est un bloc monobloc isotrope très résistant, imprimé par frittage.
*   **La fabrication FDM (Qidi)** : L'impression par dépôt de fil (FDM) crée des couches anisotropes. La liaison inter-couche (axe Z de l'imprimante) est le point faible face aux contraintes de traction et de délamination.
*   **Le couple de l'épaule (120 N.m)** : Le moteur RobStride RS-04 d'épaule génère un moment de flexion énorme sur le collet de l'épaule (traction en haut, compression en bas). Si le collet d'épaule était imprimé debout (avec des couches en rondelles empilées verticalement), l'épaule s'arracherait net à sa racine sous l'effet du bras de levier.

---

## 2. La Stratégie Ultime : Le Split unique en 2 parties (Haut / Bas) – Dos au plateau

Pour obtenir des **brides d'épaules 100 % monoblocs (cercles continus à 360°)** sans affaiblir la structure par une coupe en quatre, nous adoptons la stratégie de la **découpe horizontale unique au niveau du ventre** en orientant le dos à plat sur le plateau.

### A. Orientation d'impression : "Le Dos au plateau"

Chaque moitié (Thorax et Pelvis) est orientée avec sa **face dorsale posée à plat sur le lit d'impression** :
*   **Axe Z de l'imprimante = Axe Y du robot** (Profondeur, de l'intérieur vers l'extérieur).
*   **Axe X de l'imprimante = Axe X du robot** (Largeur, de gauche à droite).
*   **Axe Y de l'imprimante = Axe Z du robot** (Hauteur).

### B. Pourquoi cette orientation est un chef-d'œuvre d'ingénierie :

1.  **Collerettes d'épaules monoblocs et continues (360°) :** Puisqu'il n'y a pas de découpe avant/arrière, les logements cylindriques des épaules sont imprimés en cercles complets et continus. La planéité et la résistance à l'écrasement lors du serrage du moteur **RS-04** sont maximales.
2.  **Résistance à la flexion conservée :** Les filaments de carbone (PA12-CF) courent le long de la largeur du robot (axe X), liant le corps du torse au cylindre d'épaule avec des lignes continues. Le collet travaille ainsi en traction longitudinale (le long du fil), évitant tout risque de délamination inter-couche.
3.  **Respect parfait du volume de la Qidi Plus 4 (305 x 305 x 280 mm) :**
    *   Largeur de pièce : **295 mm** (passe de justesse dans 305 mm. *Attention critique aux jupes, bordures et lignes de purge du slicer : il ne reste que 5 mm de marge de chaque côté !*).
    *   Hauteur d'un demi-torse (longueur Y-robot) : **~216 mm** (passe sans problème dans 305 mm).
    *   Profondeur du torse (hauteur Z de l'impression) : **259,60 mm** (passe sous la limite matérielle de 280 mm, offrant 20.4 mm de marge de sécurité verticale).
    *   *Note : Le scale de +18% exploite l'enveloppe utile de l'imprimante à plus de 90 % !*
4.  **Impression sans supports internes :** La pièce se présentant comme un "bol" ou une cuve ouverte vers le haut, l'intérieur du torse s'imprime dans le vide sans aucun support interne. Des supports arborescents légers soutiendront uniquement les légères courbures du dos à l'extérieur.

---

## 3. L'Hybridation Métallique (Usinage CNC C500)

Pour supporter les couples massifs des épaules (moteurs RS-04 à 120 N.m) et garantir une rigidité structurelle absolue face au fluage et à la flexion, le torse en FDM PA12-CF est consolidé par un **cadre d'armature en aluminium 6061-T6 fermé et indéformable**, entièrement usinable sur la CNC de bureau **C500** :

### A. Les Plaques Structurelles Horizontales (Scale +18 % d'Asimov v1)
*   **Plaque Supérieure (Niveau Cou, Alu 6061-T6, 5 mm d'épaisseur) :** Ancrée au sommet du Thorax. Elle sert de fondation solide pour le collet du cou et l'articulation de la tête.
*   **Plaque Inférieure de Base / Taille (Waist Plate, Alu 6061-T6, 6 mm d'épaisseur) :** Ancrée tout en bas de la coque abdominale du torse rigide. Elle ferme le bas du torse et sert d'interface de liaison rigide avec le roulement de grand diamètre à section fine du module active Waist Yaw situé juste en dessous.
*   **Bénéfice :** Ces deux plaques horizontales prennent en sandwich les coques PA12-CF et verrouillent la géométrie tridimensionnelle du buste.

### B. La Colonne Vertébrale Interne (Lattes verticales de 5 mm)
*   **Conception :** Deux lattes ou profilés plats en aluminium (épaisseur **5 mm**) usinés à la CNC C500 sont installés verticalement à l'intérieur du torse.
*   **Rôle :** Ces lattes relient rigidement par double boulonnage la plaque supérieure (cou) et la plaque inférieure (taille). Elles font office d'**attelles structurelles (splint)** longitudinales, reprenant 100 % des contraintes de flexion et de torsion du buste, déchargeant ainsi entièrement les coques en plastique de ces efforts mécaniques. Elles traversent notre plan de joint d'impression abdominal fixe.

### C. Flasques d'Épaules (Aluminium 6061-T6, 5 mm d'épaisseur)
*   **Rôle :** Insérées dans une poche interne usinée/imprimée (5 mm de profondeur) à l'intérieur de l'épaule. Elles prennent le PA12-CF en sandwich avec la bride du moteur **RS-04**.
*   **Bénéfice :** Les vis de fixation du moteur se serrent dans l'aluminium, dissipant la chaleur du moteur RS-04 (120 N.m) et bloquant tout cisaillement dû aux couples.

---

## 4. Paramètres de Tranchage (Slicing) Optimisés pour le PA12-CF

L'impression du PA12-CF (Nylon chargé Carbone) pour des pièces soumises à de fortes charges structurelles (couple d'épaule de 120 N.m) requiert un paramétrage rigoureux dans le slicer (Qidi Print / OrcaSlicer). 

### A. Remplissage (Infill) : 35% Gyroïde

*   **Type de motif : Gyroïde (Gyroid)**
    *   **Isotropie mécanique 3D :** Contrairement aux motifs 2D (Grille, Triangles) qui n'offrent de résistance que dans le plan XY, le gyroïde est une structure tridimensionnelle qui offre une résistance uniforme et isotrope dans les 3 axes (X, Y, Z). C'est indispensable pour encaisser les moments combinés de flexion de l'épaule et de torsion de la taille.
    *   **Zéro croisement de lignes (Sécurité d'impression critique) :** Les motifs comme *Grille* ou *Cubic* se croisent sur une même couche, créant de micro-surépaisseurs de matière plastique à chaque intersection. Le PA12-CF étant très visqueux et chargé de fibres abrasives, la buse percute continuellement ces "bosses". Sur une impression volumineuse de plus de 20 heures (220 mm de hauteur Z), ces collisions répétées finissent par provoquer des décalages de couche (*layer shifts*) ou par décoller la pièce du plateau. Le gyroïde, tracé par une onde continue sans aucun chevauchement sur la même couche, élimine à 100% ce risque mécanique.
    *   **Fluidité d'extrusion :** Il maintient une vitesse et un débit d'extrusion constants, limitant les sous-extrusions locales.
*   **Taux de remplissage : 35%**
    *   **Le piège du 100% :** Un remplissage à 100% est contre-productif. Il augmente massivement la masse thermique, ce qui génère des contraintes de retrait phénoménales (warping) provoquant la déformation ou le décollement de la pièce, tout en consommant inutilement du filament très coûteux.
    *   **Rendement mécanique optimal :** Entre 30% et 40%, on obtient le meilleur ratio rigidité/poids. Au-delà de 40%, l'augmentation de la résistance mécanique est négligeable (rendements fortement décroissants).

### B. Périmètres et Épaisseur de Paroi (Le paramètre le plus influent)

En ingénierie des coques, la rigidité en flexion et en torsion dépend principalement de la matière située à la périphérie (moment d'inertie). Les parois externes font tout le travail mécanique.

*   **Choix de la buse : 0,6 mm vs 0,4 mm (Carbure de Tungstène)**
    *   **Buse de 0,6 mm (Option de base) :** Permet d'imprimer plus vite et d'extruder des couches plus épaisses pour réduire le nombre d'interfaces.
    *   **Buse de 0,4 mm en Carbure de Tungstène (Option validée et performante) :** Le carbure de tungstène possède une conductivité thermique exceptionnelle (proche du laiton et infiniment supérieure à l'acier trempé). Cela garantit une liquéfaction parfaite du nylon et limite drastiquement le risque de bouchage par rapport à l'acier trempé. **Vous pouvez tout à fait utiliser votre buse 0,4 mm en carbure de tungstène sans en racheter une autre**, en appliquant l'astuce de la largeur d'extrusion forcée.
*   **Nombre de parois (Wall Loops) et Largeur d'extrusion :**
    *   **Configuration 0,6 mm :** 5 périmètres (largeur de ligne à 0,6 mm = coque solide de **3,0 mm**).
    *   **Configuration 0,4 mm (Carbure) :** Forcer la **largeur d'extrusion à 0,48 mm** dans le slicer (une buse de 0,4 mm peut sans problème étaler du filament sur 120% de sa largeur) et régler sur **6 périmètres** (6 x 0,48 mm = coque solide de **2,88 mm**). Cela permet d'obtenir la même résistance qu'une buse 0,6 mm tout en limitant le temps d'impression.
*   **Couches supérieures et inférieures (Top/Bottom Layers) : 6 couches.**
    *   Garantit une excellente rigidité superficielle aux extrémités et scelle hermétiquement la structure interne.

### C. Profil Thermique, Hauteurs de Couche et Vitesses (Qidi Plus 4)

*   **Hauteur de couche :**
    *   **Avec Buse 0,6 mm :** 0,24 mm à 0,30 mm.
    *   **Avec Buse 0,4 mm (Carbure) :** **0,16 mm à 0,20 mm maximum**. Pour les pièces structurelles, la hauteur de couche ne doit pas dépasser 50% du diamètre de la buse afin d'assurer un écrasement parfait des couches et maximiser l'adhésion inter-couche (axe Z).
    *   **Hauteur de couche variable (Adaptive Layer Height) : Fortement déconseillée.** Bien que séduisante pour lisser les courbes du dos, elle est déconseillée pour du PA12-CF structurel car :
        1.  La variation dynamique du débit perturbe la contre-pression dans la buse de 0,4 mm, augmentant le risque de sous-extrusion locale ou de bouchage (les fibres se coinçant dans les couches ultra-fines).
        2.  Elle crée des taux de refroidissement et de retrait inégaux le long de la pièce, ce qui peut voiler le plan de jointure.
        3.  *Si vous souhaitez l'activer pour lisser le dos,* **bridez strictement** les limites dans votre slicer entre **0,15 mm (Minimum)** et **0,20 mm (Maximum)** pour conserver la masse thermique et la pression d'extrusion nécessaires à la cohésion mécanique.
*   **Température de buse :**
    *   **Avec Buse 0,6 mm :** 295°C - 300°C.
    *   **Avec Buse 0,4 mm (Carbure) :** **290°C - 295°C**. Grâce à l'excellente conductivité thermique du carbure de tungstène, le nylon fond de manière homogène même à débit élevé, sans avoir besoin de surchauffer.
*   **Température du plateau :** 85°C - 90°C avec application d'un primaire d'adhérence spécialisé (ex: Magigoo PA ou colle PVP en bâton).
*   **Chambre activement chauffée :** **60°C** (indispensable pour éliminer le warping).
*   **Refroidissement (Part Cooling Fan) :** Désactivé (0%) ou limité à 10% maximum pour les ponts.
*   **Vitesse d'impression :**
    *   **Avec Buse 0,6 mm :** 50 - 70 mm/s.
    *   **Avec Buse 0,4 mm (Carbure) :** **40 - 55 mm/s** pour les parois externes et internes. Réduire légèrement la vitesse avec une buse plus fine permet de limiter la pression dans la buse et d'assurer un alignement optimal des fibres de carbone.

### D. Conditionnement du filament (Le facteur n°1 d'échec)

Le PA12 (Nylon) est extrêmement hydrophile. Même chargé de carbone, il absorbe l'humidité de l'air en quelques heures, ce qui provoque la formation de micro-bulles de vapeur d'eau lors de l'extrusion (bruit de crépitement), détruisant l'adhérence des couches et rendant la pièce cassante comme du verre.
1.  **Séchage initial :** Sécher la bobine au four ou dans un sécheur actif à **90°C pendant 6 à 8 heures** avant de lancer l'impression.
2.  **Impression sous atmosphère contrôlée :** Imprimer impérativement à partir d'une boîte sèche hermétique (*Drybox*) reliée directement à l'imprimante, maintenant un taux d'humidité inférieur à 10%.

### E. Slicer Settings Reference Table (OrcaSlicer / Qidi Print)

Ce tableau récapitule tous les réglages dans leur dénomination officielle en **anglais** pour vous permettre de les retrouver instantanément dans **OrcaSlicer** ou **Qidi Print** :

| Catégorie | Paramètre (FR) | Slicer Setting Name (EN) | Slicer Tab / Menu Path (EN) | Recommended Value | Description & Note |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Printer** | Diamètre de buse | **Nozzle Diameter** | `Printer settings` ➔ `Extruder` ➔ `Nozzle` | `0.4 mm` | Type : **Tungsten Carbide** (Carbure de Tungstène) |
| **Quality** | Hauteur de couche | **Layer Height** | `Process` ➔ `Quality` ➔ `Layer Height` | `0.18 mm` | Ou `0.20 mm` max pour une cohésion inter-couche optimale |
| **Quality** | Largeur d'extrusion | **Line Width / Extrusion Width** | `Process` ➔ `Quality` ➔ `Line Width` | `0.48 mm` | À forcer sur toutes les lignes (Outer, Inner, Infill, etc.) |
| **Strength** | Nombre de parois | **Wall Loops / Perimeters** | `Process` ➔ `Strength` ➔ `Walls` | `6` | Donne une coque extérieure solide de **2,88 mm** |
| **Strength** | Couches sup. / inf. | **Top / Bottom Shell Layers** | `Process` ➔ `Strength` ➔ `Shells` | `6` / `6` | Scelle hermétiquement et rigidifie la structure |
| **Strength** | Motif de remplissage | **Infill Pattern** | `Process` ➔ `Strength` ➔ `Sparse infill` | `Gyroid` | Évite 100% des collisions de buse sur les longs prints |
| **Strength** | Taux de remplissage | **Infill Density** | `Process` ➔ `Strength` ➔ `Sparse infill` | `35%` | *Pro-Tip :* Mettre `45%` localement via un *Modifier Volume* sur l'épaule |
| **Filament** | Température de buse | **Nozzle Temperature** | `Filament settings` ➔ `Filament` ➔ `Nozzle temperature` | `290°C - 295°C` | Température optimale de fusion du PA12 |
| **Filament** | Température plateau | **Bed Temperature** | `Filament settings` ➔ `Filament` ➔ `Bed temperature` | `85°C - 90°C` | Avec colle Magigoo PA ou PVP sur plateau PEI |
| **Filament** | Chambre chauffée | **Chamber Temperature** | `Filament settings` ➔ `Filament` ➔ `Chamber temperature` | `60°C` | Chambre active de la Qidi Plus 4 à allumer impérativement |
| **Cooling** | Ventilation pièce | **Part Cooling Fan Speed** | `Filament settings` ➔ `Cooling` ➔ `Part cooling fan` | `0%` | Désactivée pour une adhésion Z maximale (max 10% pour ponts) |
| **Speed** | Vitesse parois ext. | **Outer Wall Speed** | `Process` ➔ `Speed` ➔ `Walls` | `40 - 45 mm/s` | Une vitesse modérée améliore l'alignement des fibres |
| **Speed** | Vitesse parois int. | **Inner Wall Speed** | `Process` ➔ `Speed` ➔ `Walls` | `50 - 55 mm/s` | Maintient un flux d'extrusion régulier |
| **Speed** | Vitesse remplissage | **Sparse Infill Speed** | `Process` ➔ `Speed` ➔ `Infill` | `50 - 55 mm/s` | Stabilité du flux thermique |
| **Support** | Activer supports | **Enable Support** | `Process` ➔ `Support` ➔ `Support` | `Checked (Yes)` | Type : **Tree (Organic)**, uniquement à l'extérieur |
| **Travel** | Saut en Z | **Z-hop when Retracting** | `Printer settings` ➔ `Extruder` ➔ `Retraction` | `0.4 mm` | Type : **Normal** ou **Slope**. Évite de racler le remplissage |
| **Others** | Couche variable | **Adaptive Layer Height** | `Top Toolbar` ➔ `Variable Layer Height (Icon)` | `Disabled` | Conserver une hauteur constante (ou bridée entre `0.15` et `0.20 mm`) |
### F. Slicer Settings Reference Table for PLA Prototyping (OrcaSlicer / Qidi Print)

Imprimer un prototype à l'échelle (+18 %) en **PLA** standard (ou PLA+ / PLA Tough) avant de lancer l'impression finale en PA12-CF est une étape hautement recommandée. Cela vous permettra de valider physiquement à moindre coût et très rapidement :
1.  Le bon encastrement et le perçage des moteurs **RobStride RS-04** dans les épaules.
2.  La tolérance d'assemblage de la lèvre d'emboîtement abdominale (*Lap Joint*).
3.  Le passage des inserts alu CNC (flasques, colonnes, waist plate) et le cheminement des câbles internes.

Pour ce prototype, la priorité est donnée à **la vitesse d'impression** et à **l'économie de filament** (remplissage léger, parois réduites) plutôt qu'à la résistance mécanique brute :

| Catégorie | Paramètre (FR) | Slicer Setting Name (EN) | Slicer Tab / Menu Path (EN) | Recommended Value (PLA) | Description & Note |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Printer** | Diamètre de buse | **Nozzle Diameter** | `Printer settings` ➔ `Extruder` ➔ `Nozzle` | `0.4 mm` | Buse Carbure ou Laiton standard (aucune abrasion avec le PLA) |
| **Quality** | Hauteur de couche | **Layer Height** | `Process` ➔ `Quality` ➔ `Layer Height` | **`0.28 mm`** | Hauteur importante pour imprimer deux fois plus vite (mode draft) |
| **Quality** | Largeur d'extrusion | **Line Width / Extrusion Width** | `Process` ➔ `Quality` ➔ `Line Width` | `0.42 mm` | Largeur standard pour conserver une bonne fidélité dimensionnelle |
| **Strength** | Nombre de parois | **Wall Loops / Perimeters** | `Process` ➔ `Strength` ➔ `Walls` | **`3`** | Suffisant pour valider les formes et les filetages, économise du fil |
| **Strength** | Couches sup. / inf. | **Top / Bottom Shell Layers** | `Process` ➔ `Strength` ➔ `Shells` | `4` / `4` | Gain de temps et de matière substantiel |
| **Strength** | Motif de remplissage | **Infill Pattern** | `Process` ➔ `Strength` ➔ `Sparse infill` | `Grid` ou `Gyroid` | Le motif *Grid* (Grille) est le plus rapide à imprimer pour du PLA |
| **Strength** | Taux de remplissage | **Infill Density** | `Process` ➔ `Strength` ➔ `Sparse infill` | **`10% - 15%`** | Remplissage léger amplement suffisant pour un prototype d'étude |
| **Filament** | Température de buse | **Nozzle Temperature** | `Filament settings` ➔ `Filament` ➔ `Nozzle temperature` | `210°C - 220°C` | Température d'extrusion standard pour le PLA |
| **Filament** | Température plateau | **Bed Temperature** | `Filament settings` ➔ `Filament` ➔ `Bed temperature` | `55°C - 60°C` | Température d'accroche standard PLA (PEI texturé ou lisse) |
| **Filament** | Chambre chauffée | **Chamber Temperature** | `Filament settings` ➔ `Filament` ➔ `Chamber temperature` | **`0°C (OFF)`** | **⚠️ ATTENTION CRITIQUE :** Éteindre le chauffage de chambre et **laisser le capot supérieur ou la porte de l'imprimante OUVERTE**. Le PLA déteste la chaleur confinée qui provoque le bouchage de la buse par *heat creep* (remontée de chaleur dans l'extrudeur). |
| **Cooling** | Ventilation pièce | **Part Cooling Fan Speed** | `Filament settings` ➔ `Cooling` ➔ `Part cooling fan` | **`100%`** | Refroidissement maximal indispensable pour figer le PLA et réussir les ponts |
| **Speed** | Vitesse parois ext. | **Outer Wall Speed** | `Process` ➔ `Speed` ➔ `Walls` | `100 - 120 mm/s` | Vitesse élevée grâce aux performances CoreXY de la Qidi Plus 4 |
| **Speed** | Vitesse parois int. | **Inner Wall Speed** | `Process` ➔ `Speed` ➔ `Walls` | `150 - 200 mm/s` | Remplissage rapide des parois |
| **Speed** | Vitesse remplissage | **Sparse Infill Speed** | `Process` ➔ `Speed` ➔ `Infill` | `200 - 250 mm/s` | Permet de gagner plusieurs heures sur les volumes internes |
| **Support** | Activer supports | **Enable Support** | `Process` ➔ `Support` ➔ `Support` | `Checked (Yes)` | Type : **Tree (Organic)**. Les supports en PLA se détachent très facilement |
| **Travel** | Saut en Z | **Z-hop when Retracting** | `Printer settings` ➔ `Extruder` ➔ `Retraction` | `0.2 mm` | Type : **Normal**. Évite les collisions mineures de déplacement |
| **Others** | Couche variable | **Adaptive Layer Height** | `Top Toolbar` ➔ `Variable Layer Height (Icon)` | `Disabled` | Inutile ici, le but est d'aller le plus vite possible |

### G. Optimisation des Supports d'Impression (Retour d'expérience Slicer)

La simulation de tranchage en orientation « dos au plateau » révèle un volume de supports arborescents important, concentré sur **trois zones critiques** :

1.  **Sous les collerettes d'épaules :** Les cylindres de montage moteur se projettent horizontalement depuis le corps du torse, formant un porte-à-faux massif (*cantilever*) sans aucune surface de soutien en dessous. Le slicer est donc contraint de construire de hauts piliers de support depuis le plateau.
2.  **Sur les courbes de la poitrine (face avant) :** La paroi avant monte verticalement puis s'incurve progressivement vers l'extérieur, créant des surplombs organiques de plus en plus prononcés (>45°).
3.  **Sur certaines géométries internes :** Le design Asimov v1 d'origine (conçu pour du frittage MJF auto-supporté) peut contenir des nervures, bossages ou routages de câbles qui génèrent des surplombs internes nécessitant des supports.

#### G.1 Réglages slicer pour réduire les supports

| Slicer Setting (EN) | Slicer Tab / Menu Path (EN) | Recommended Value | Effet |
| :--- | :--- | :---: | :--- |
| **Support Threshold Angle** | `Process` ➔ `Support` ➔ `Support` | `55° - 60°` | Remplace le 45° par défaut. Le PA12-CF et le PLA peuvent ponter des surplombs jusqu'à 55-60° sans effondrement. Élimine une grande partie des supports sur les courbes douces. |
| **Support on Build Plate Only** | `Process` ➔ `Support` ➔ `Support` | `Checked (Yes)` | **Élimine tous les supports internes.** Le slicer ne construira des supports qu'à partir du plateau. Les petits surplombs internes doivent ponter seuls. |
| **Support Top Z Distance** | `Process` ➔ `Support` ➔ `Support` | `0.28 - 0.36 mm` | 1,5× à 2× la hauteur de couche. Augmente l'espace entre le support et la pièce. Facilite **considérablement** le retrait (critique en PA12-CF car le nylon adhère fortement au support). |
| **Support Interface Layers** | `Process` ➔ `Support` ➔ `Support` | `2 layers` | Active une fine couche de transition entre le support et la pièce. Donne un état de surface plus propre là où les supports touchent. |
| **Support Interface Density** | `Process` ➔ `Support` ➔ `Support` | `50%` | Densité réduite pour l'interface de support → retrait plus facile. |
| **Support Base Pattern** | `Process` ➔ `Support` ➔ `Support` | `Default` ou `Grid` | La structure *Grid* pour le corps des supports est moins dense que *Rectilinear*. |

#### G.2 Modifications CAO recommandées (Fusion 360)

Pour réduire structurellement le volume de supports **à la source**, indépendamment du slicer :

*   **Chanfreins autoportants sous les collets d'épaules :** Là où les cylindres d'épaule rejoignent le corps du torse, modéliser un **chanfrein ou congé progressif à 45° minimum** sur la face inférieure. Cela crée une transition auto-supportée qui permet à l'imprimante de construire le cylindre progressivement au lieu de le démarrer en porte-à-faux brutal. C'est la modification la plus efficace pour réduire les supports.
*   **Simplification des nervures internes héritées du design MJF :** Le design d'origine a été conçu pour le frittage de poudre (100% auto-supporté). Si certaines nervures ou bossages internes ne sont pas strictement structurels, les supprimer ou les remplacer par des géométries imprimables à 45° éliminera les supports internes résiduels.

#### G.3 Stratégie différenciée : Prototype PLA vs Version Finale PA12-CF

| | **Prototype PLA** | **Version Finale PA12-CF** |
| :--- | :--- | :--- |
| **Threshold Angle** | 55° - 60° | 55° (rester conservateur avec le nylon) |
| **Build Plate Only** | ✅ Oui | ✅ Oui |
| **Inclinaison de la pièce (10-15°)** | ✅ Autorisée — réduit fortement les supports sous les collets. La précision de la face d'appui moteur n'est pas critique pour un test d'ajustement. | ❌ Interdite — la planéité parfaite des faces d'appui des collets (pour les flasques alu + moteur RS-04) nécessite que le dos soit strictement à plat. |
| **Retrait des supports** | Facile (le PLA casse proprement) | Difficile (le PA12-CF adhère fortement, utiliser un cutter et des pinces fines). Augmenter le *Support Top Z Distance* à 0.36 mm. |
| **Chanfreins CAO** | Optionnels (mais testez-les !) | **Fortement recommandés** pour minimiser la quantité de support à retirer sur la pièce finale. |

---

## 5. Modélisation CAO : Split Rigide & Liaison Active Waist Yaw sous Fusion 360

Cette section détaille la méthodologie géométrique pour modéliser le split rigide du torse et la liaison de taille rotative active de l'Asimov v1 (mises à l'échelle à +18 %) adaptée pour le moteur **RobStride RS-03** :

### A. Le Split Abdominal Rigide du Torse (Pour la Qidi Plus 4)
Le torse doit être divisé horizontalement au niveau du ventre uniquement pour l'impression 3D, mais rester 100 % rigide à l'assemblage :

1. **Création du bandeau de renfort interne (Avant le Split) :**
   * Créez un plan décalé (`Offset Plane`) à la hauteur de coupe abdominale.
   * Créez une esquisse et utilisez `Project/Include` ➔ **Intersect** (Intersection) de la surface externe du torse.
   * Effectuez un décalage (**Offset**, touche `O`) de cette courbe de **-2,88 mm** (paroi interne nominale de 6 périmètres) et un second décalage de **-5,88 mm** (limite du renfort).
   * Extrudez cette couronne de **8 mm** vers le haut et **8 mm** vers le bas en mode **Join** (Symmetric, 8 mm) sur le torse. L'épaisseur locale passe ainsi à **5,88 mm** à cheval sur le plan de coupe.
2. **Scission du torse (Split Body) :**
   * Lancer `Split Body` sur le torse complet en utilisant le plan décalé comme outil de coupe. On obtient le **Thorax (Haut)** et la **coque abdominale (Bas)**.
3. **Modélisation du décrochement rigide (Lap Joint) :**
   * Créez une esquisse sur la face plane supérieure de la coque abdominale (bas) et tracez un **Offset de -3,00 mm** vers l'intérieur pour marquer la ligne de jointure médiane.
   * Extrudez la couronne externe (comprise entre le bord externe et la ligne décalée) vers le haut (+Z) de **3,00 mm** en mode **Join** sur la coque abdominale. Vous obtenez la lèvre mâle.
   * Affichez le *Thorax* et utilisez l'outil **Combine** (*Target* : Thorax, *Tool* : coque abdominale, *Operation* : **Cut**, ⚠️ **Keep Tools : Coché**). Le Thorax dispose de sa rainure femelle.
4. **Application des tolérances de jeu au Press Pull :**
   * Masquez la coque abdominale et appliquez l'outil **Press Pull** (`Q`) sur la gorge femelle du Thorax :
     * **Jeu Radial (Ajustement horizontal) :** Sélectionnez la face verticale de la rainure et entrez **-0,15 mm** de décalage pour élargir la gorge et compenser les tolérances d'extrusion du PA12-CF.
     * **Jeu Axial (Ajustement vertical) :** Sélectionnez la face horizontale supérieure de fond de rainure et entrez **-0,10 mm**. Cela garantit que le serrage principal s'effectue sur le plan de jointure externe nominal visible, masquant tout jour à l'extérieur.
5. **Fixations et bossages M4 internes :**
   * Dessinez **4 à 6 bossages internes** (Ø12 mm) répartis le long de la circonférence intérieure :
     * *Côté Thorax :* Passage lisse de Ø4,2 mm lamé pour noyer la tête de vis M4.
     * *Côté coque abdominale :* Logement de Ø5,8 mm et 9 mm de profondeur pour insert en laiton M4 posé à chaud.

---

### B. L'Armature Métallique Interne (Cadre fermé C500)
Pour rigidifier le buste face aux moments d'épaules et de taille :
1. **Intégration des plaques d'armature :**
   * Importez la plaque supérieure (cou, alu 5 mm) et la plaque inférieure (Waist Plate, alu 6 mm) de la BOM d'origine d'Asimov v1.
   * Appliquez un **scale global de +18 %** sur ces deux composants.
   * Modélisez des épaulements internes de 5 mm et 6 mm dans les coques imprimées pour emboîter ces plaques à leurs extrémités.
2. **Couplage de la Colonne (Lattes alu de 5 mm) :**
   * Modélisez des taraudages M4 aux extrémités des lattes alu CNC de 5 mm et sur les plaques horizontales.
   * Les deux lattes sont vissées rigidement à la plaque supérieure du cou et à la plaque inférieure de taille, formant une armature en parallélépipède métallique indéformable qui s'insère dans les coques PA12-CF.

---

### C. La Liaison Active Waist Yaw (RobStride RS-03)
La rotation s'effectue sous la plaque inférieure du torse rigide (Waist Plate de 6 mm) :
1. **Le scale global de la liaison rotative Asimov v1 (+18 %) :**
   * Le logement moteur d'Asimov v1 conçu pour un Cubemars AK80 de 98 mm passe à un diamètre de **115,6 mm** après le scale de +18 %.
2. **La bague d'adaptation CNC pour le RobStride RS-03 :**
   * Nous choisissons le moteur **RobStride RS-03** (diamètre de 106 mm, couple de pointe **60 N.m**).
   * Pour l'encastrer dans l'alésage de 115,6 mm du châssis, modélisez une **bague d'adaptation cylindrique en aluminium 6061-T6** ayant un diamètre intérieur de 106 mm (ajustement glissant sur le RS-03) et un diamètre extérieur de 115,6 mm (ajustement glissant dans le boîtier pelvis inférieur).
   * La bague comporte une collerette supérieure de 1,5 mm d'épaisseur pour venir se visser sur le châssis et servir de pont thermique de dissipation. L'épaisseur radiale de la bague est de seulement **4,8 mm** (très légère et facile à usiner avec la C500).
3. **Le roulement de lacet :**
   * Modélisez un épaulement circulaire de Ø110 mm sous la plaque alu de taille pour emboîter la bague interne du roulement à section fine de grand diamètre d'Asimov v1 (scalé à +18 %). La bague externe est vissée sur le boîtier pelvis inférieur.
4. **Accouplement mécanique :**
   * Le stator du RS-03 est bridé au fond du pelvis inférieur (fixe).
   * Le rotor (arbre de sortie) du RS-03 est accouplé au centre de la plaque en alu de taille du torse rigide (mobile).

---

## 6. Workflow Résumé (Plan d'Action Révisé)

1.  **Fusion 360 - Conception CAO :**
    *   Mettre à l'échelle (+18 %) les fichiers originaux du torse et de la taille d'Asimov v1.
    *   Réaliser le split rigide abdominal avec le bandeau de renfort interne, le Lap Joint de 3 mm et ses tolérances d'ajustement (0,15 mm radial / 0,10 mm axial).
    *   Modéliser la bague d'adaptation en aluminium CNC de 4,8 mm d'épaisseur radiale pour encastrer le RobStride RS-03 (106 mm) dans le logement de l'AK80 (115,6 mm).
    *   Dessiner les poches internes de **5 mm** de profondeur pour les flasques d'épaules.
2.  **Usinage CNC (C500) :**
    *   Usiner les deux flasques d'épaules (**5 mm** alu 6061), les lattes de colonne vertébrale (**5 mm** alu 6061), la plaque supérieure de cou (**5 mm** alu 6061), la plaque de taille/Waist Plate (**6 mm** alu 6061) et la bague d'adaptation du RS-03 (**6 mm** alu 6061 ou bloc).
3.  **Impression 3D (Qidi Plus 4) :**
    *   Trancher le Thorax et l'Abdomen en orientant leur **dos plat contre le plateau**.
    *   Configurer le profil de tranchage en PA12-CF selon la **Section 4** (Buse 0,4 mm Carbure, 6 périmètres à 0,48 mm, 35% Gyroïde).
    *   Activer les supports arborescents uniquement à l'extérieur.
4.  **Assemblage du Torse Rigide :**
    *   Poser à chaud les inserts filetés M4 en laiton dans les coques PA12-CF.
    *   Encastrer les flasques alu d'épaules et monter les moteurs RobStride RS-04 (120 N.m).
    *   Assembler le Thorax (Haut) et l'Abdomen (Bas) via l'emboîtement Lap Joint, et serrer les vis de liaison M4 des bossages internes.
    *   Insérer le cadre d'armature métallique vertical (les deux lattes alu de 5 mm vissées sur la plaque de cou en haut et la plaque de taille en bas) et sécuriser à la Loctite 243. Le torse forme un bloc unique 100 % rigide.
5.  **Assemblage de la liaison rotative Waist Yaw :**
    *   Monter la bague d'adaptation alu CNC de 4,8 mm sur le corps du moteur RobStride RS-03, et encastrer le moteur dans son berceau dans le pelvis inférieur.
    *   Poser le roulement à section fine de Ø110 mm sous la plaque alu de taille du torse rigide.
    *   Accoupler mécaniquement le rotor du RS-03 au centre de la plaque alu de taille et boulonner la bague du roulement sur le pelvis inférieur.
    *   Appliquer de la **Loctite 243** sur toutes les vis métalliques. Câbler le bus CAN-FD (ID 21) et la puissance 48V de la taille vers la PDB principale.
