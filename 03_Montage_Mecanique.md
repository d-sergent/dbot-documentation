# Guide Mécanique et Impression 3D

## 1. Paramètres### Visserie Industrielle
Le projet utilise deux standards principaux :
1.  **ISO 7380 (Tête Bombée)** : Profil bas, idéal pour l'esthétique et éviter d'accrocher les câbles.
2.  **DIN 912 (Tête Cylindrique)** : Indispensable pour les zones à fort couple (hanches). Permet un serrage monumental.

#### Paramètres de Chambrage (Fusion 360 - Vis DIN 912)
| Dimension | Symbole | M3 (DIN 912) | M4 (DIN 912) |
| :--- | :--- | :--- | :--- |
| Diamètre Chambrage | Dcb | **6.5 mm** | **8.5 mm** |
| Profondeur Chambrage | Hcb | **3.5 mm** | **4.5 mm** |
| Trou Insert (PETG-CF) | dh | 4.2 - 4.5 mm | 5.6 - 5.8 mm |
| Épaisseur Plancher | T | 3.0 mm min | 4.0 mm min |

---

### Inserts et Roulements
- **Inserts Ruthex** : Utilisez les versions **Longues (8.1mm)** pour les RS-04. Les versions courtes (5.7mm) suffisent pour les carters.

### Commande CNC (Aluminium 6061)
- **Format** : Fichiers `.step` uniquement.
- **Rayons** : Rayons internes de **2mm minimum** (usinage fraise).
- **Finition** : "As Machined" (le plus économique).

### Chambrages (Counterbore) pour têtes de vis DIN 912
L'objectif est de noyer la tête de vis pour qu'elle ne dépasse pas, tout en laissant passer la clé Allen.
| Paramètre | Symbole | M3 | M4 |
| :--- | :--- | :--- | :--- |
| **Diamètre Chambrage** | $D_{cb}$ | **6.5 mm** | **8.5 mm** |
| **Profondeur** | $H_{cb}$ | **3.5 mm** | **4.5 mm** |
| **Passage de vis** | $d$ | 3.4 mm | 4.5 mm |

> **Astuce Fusion 360** : Utilisez l'outil *Hole (H)* > *Counterbore* > *Simple* > *Flat*.

### Trous pour Inserts (Heat-set)
Ces diamètres sont optimisés pour les inserts Ruthex standards.
| Paramètre | M3 | M4 |
| :--- | :--- | :--- | 
| **Diamètre perçage** | **4.2 - 4.5 mm** | **5.6 - 5.8 mm** |
| **Épaisseur paroi min** | 1.6 mm | 2.0 mm |
| **Épaisseur fond plan** | **3.0 mm** (Min) | **4.0 mm** (Min) |

---

## 2. Impression 3D (Qidi Plus 4)

### Matériau Recommandé : PETG-CF
Le PETG renforcé fibre de carbone (PETG-CF) est le meilleur compromis pour le D-Bot sur cette machine.
*   **Avantages** : Rigidité accrue (moins de flexion que le PETG pur), aspect mat qui cache les couches, bonne tenue en température (vers 80°C).
*   **Inconvénients** : Abrasif (utilisez une buse acier trempé).

*   **(A) PLA** : Pour le prototypage rapide et validation de forme. **(~20€/kg)**
*   **(B) PETG-CF** (Recommandé) : Rigide, facile à imprimer, esthétique carbone. Suffisant pour 80% du robot. **(~30€/kg)**
*   **(C) PA12-CF** (Nylon Carbone) : Performance ultime (Chaleur/Choc). Nécessite enceinte chauffée + séchage pro. Pour les pièces critiques uniquement (Hanches). **(~100€/kg)**

### Comparatif Matériaux
| Critère | PLA (Proto) | PETG-CF (Standard) | PA12-CF (Pro) |
| :--- | :--- | :--- | :--- |
| **Coût (Est.)** | 20€ / kg | **30€ / kg** | 100€ / kg |
| **Rigidité** | Moyenne | Élevée | Très Élevée |
| **Résistance Chaleur** | Faible (50°C) | Moyenne (75°C) | Haute (100°C+) |
| **Facilité Impression** | Très Facile | Facile | Difficile (Warping) |
| **Usage D-Bot** | Tests de forme | **Coques, Bras, Tête** | Gears, Hanches |

### Paramètres de Slicer (OrcaSlicer / QidiSlicer)
*   **Matériau** : Creality Hyper **PETG-CF** (Recommandé pour débuter).
    *   *Alternative Pro* : **PA12-CF** (Nylon Carbone). Plus rigide et résistant à la chaleur, mais nécessite une enceinte chauffée et un séchage parfait. À réserver aux utilisateurs expérimentés.
*   **Températures** :
    *   **Buse** : 270°C
    *   **Plateau** : 80°C
    *   **Chambre (Active)** : 50°C
*   **Vitesse** : 200-300 mm/s.
*   **Hauteur de couche** : 0.20 mm (Standard) ou 0.16 mm (Précision engrenages).
*   **Périmètres (Walls)** : **4 à 5 murs minimum**. C'est le plus important pour la solidité des filetages/inserts.
*   **Remplissage (Infill)** :
    *   **100% (Solid)** pour : Hanches, Épaules, Supports Moteurs.
    *   **40% (Gyroid)** pour : Coques, avant-bras, tête.
*   **Séchage** : Obligatoire avant impression (65°C / 6h).

---

## 3. Montage des Moteurs Robstride

### Sécurisation Haute Charge (RS-04: 120 N.m)
Le couple pharaonique des moteurs RS-04 (Hanches et Genoux) génère des efforts de cisaillement massifs d'environ 4000 N sur le cercle de perçage radial. Pour empêcher les vis de cisailler ou les pièces plastiques (PA12-CF/PETG-CF) de s'écraser et de s'ovaliser sous la pression :
1.  **Goupilles de Positionnement (Dowel Pins)** : Ne comptez **jamais** sur le corps des vis pour encaisser le couple. Insérez impérativement 2 goupilles cylindriques rectifiées en acier trempé (Ø5mm ou Ø6mm en diamétralement opposé) pour reprendre le cisaillement pur.
2.  **Interface Aluminium CNC** : Usinez systématiquement une plaque en Aluminium de 5mm à la **CNC C500** (cf. [Guide CNC](./12_Guide_Parties_Metal_CNC.md)) entre le stator RS-04 et le squelette pour dissiper l'énorme chaleur générée par le moteur à l'arrêt, et servir de cage de rétention.
3.  **Visserie Acier 12.9** : Remplacez l'inox A2 standard par de la visserie de classe **12.9** (Acier bruni) sécurisée avec du frein-filet **Loctite 243** (Bleu) pour anticiper les chocs de la course.
4.  **Inserts et Rondelles** : Le serrage sur plastique requiert systématiquement de larges rondelles d'appui.

### Intégration Robstride 05 (RS-05) - Cou / Poignets
*   **Ancrage** : Le couple de pointe (5.5 Nm) est élevé pour du plastique.
    *   Utilisez des **vis M4 x 12mm Acier 12.9 (Noir)** pour fixer le corps moteur au châssis. L'Inox est trop "mou" pour ces zones de force pure si vous démontez souvent.
*   **Longueur de vis** : Règle d'or = Épaisseur pièce plastique + (Profondeur trou moteur - 1mm).
    *   *Ne forcez jamais* si la vis touche le fond du trou borgne du moteur ! Vous détruiriez le filetage interne du stator.

### Maintenance Rapide (Connectique Tête/Cou)
- **Tête/Cou** : L'utilisation de borniers **WAGO 221-413 (3 entrées)** ou **415 (5 entrées)** est vivement recommandée pour les liaisons LiDAR et moteurs de cou. Cela permet de remplacer un capteur ou un moteur en 30 secondes sans soudure, tout en garantissant un contact électrique fiable face aux vibrations.

### Roulements à Section Fine (Articulations Actives)
*   Pour les **articulations actives** (hanches, genoux, cou), utilisez impérativement les **roulements à section fine** (6807-2RS, 6705-2RS) documentés dans la BOM §1.


### Architecture Articulaire : Montage en Chape (Simple Soutien) vs Double Soutien
Pour le design mécanique des jonctions de genou et de hanche du D-Bot (39 kg), deux écoles d'ingénierie s'affrontent :
1.  **Le Double Soutien (Hyperstatique / Cage)** : Consiste à enfermer le RS-04 dans une cage avec deux gros roulements externes soutenant l'axe de chaque côté du stator pour totalement isoler le moteur. *Risque Majeur* : L'alignement des deux roulements externes avec les roulements internes du moteur doit être parfait au micron près. Le moindre défaut de concentricité lors d'un assemblage génère des contraintes internes qui ruineront le moteur par friction.
2.  **Montage en Chape Rigide (Recommandé)** : C'est le standard de l'industrie (ex: Unitree Go2). Le stator du moteur D-Bot est fixé d'un côté. L'axe de sortie (rotor) traverse le membre et est supporté par **un seul** roulement à l'extrémité opposée (montage en porte-à-faux supporté).
    *   **Mise en œuvre D-Bot** : Utilisez un support en Aluminium 7075 usiné à la CNC C500. Du côté opposé au moteur, insérez un roulement étanche à section fine **6807-2RS** (pour laisser passer les câbles XT30/CAN de 35mm). L'ensemble doit être lié par une entretoise transversale extrêmement rigide assurant la coaxialité parfaite.

### Fixation Axiale des Roulements sur Arbre (Aluminium CNC)
L'assemblage des roulements à section fine sur l'axe en aluminium de la chape demande une géométrie stricte pour durer :
1.  **L'Épaulement (Butée)** : Il sert de référence perpendiculaire. Sa hauteur doit **uniquement** s'appuyer sur la bague *intérieure* du roulement. S'il est trop haut et frotte la bague extérieure ou le joint 2RS, votre moteur forcera et surchauffera.
2.  **La Gorge de Décharge** : La CNC laissera toujours un rayon (congé d'outil) à la base de l'épaulement, ce qui crée un faux-rond repoussant le roulement. Usinez une toute petite gorge de décharge dans cet angle pour garantir que le roulement plaque à plat contre le mur de l'épaulement.
3.  **Rétention par le Haut (Le Piège)** :
    *   *Cou / Bras (Léger)* : Le blocage par un simple **Circlips** (anneau élastique) suffit amplement. Assurez-vous d'usiner la gorge à la largeur exacte du roulement (+0.05 mm) pour éviter tout "cliquetis" qui éroderait l'axe en alu.
    *   *Genoux / Hanches (Lourd 39 kg)* : Un choc latéral brutal peut faire sauter un circlips de sa gorge. Sur ces gros points névralgiques, remplacez-le par un **Écrou à encoches (Écrou KM)** ou une grosse entretoise pleine vissée en bout d'arbre. C'est plus lourd, mais indestructible.

---

## 4. Intégration Cheville 2-DOF (Roll + Pitch) [Phase 4] — Architecture Cardan DIN 808

> ⚠️ **Mise à jour Mars 2026** : L'ancienne architecture (RS-02 Pitch + RS-00 Roll avec Bracket en L) a été **remplacée** par le système **Cardan DIN 808 + 2× RS-03 + Bielles Carbone**, retenu pour sa robustesse et ses performances supérieures (120 N.m Pitch + 120 N.m Roll). Voir [20_Etude_Cheville_Cardan.md](./20_Etude_Cheville_Cardan.md) pour l'étude complète.

### Principe
Les deux moteurs **RS-03** (60 N.m chacun) sont fixés **en haut du tibia** (pas dans le pied). Chacun actionne la cheville via une **bielle en carbone** (tube 3K Ø10/8mm) avec un ratio d'amplification mécanique de ~2:1, portant le couple effectif à **120 N.m** par axe (Pitch et Roll). Le joint de liaison est un **Cardan DIN 808 Série G** (acier C45, axe 12mm) commercial.

### Avantages vs Ancien Design
| Critère | Ancien (RS-02+RS-00) | Nouveau (Cardan + 2×RS-03) |
| :--- | :---: | :---: |
| Couple Pitch | ~34 N.m | **120 N.m** |
| Couple Roll | 14 N.m | **120 N.m** |
| Masse distale (pied) | ~870g (moteurs) | **~0g** (moteurs en haut du tibia) |
| Robustesse | Fragile | Acier C45 industriel |

### Pièces Clés
*   **Cardan** : Michaud Chailly A5-473-12 (DIN 808, Ø axe 12mm).
*   **Bielles** : Tubes carbone 3K Ø10/8mm + rotules Igus EBRM-05.
*   **Capteurs FSR** : 4× FSR 402 dans la semelle du pied (mesure du CoP).
*   **Semelle** : PA12-CF + patin TPU/caoutchouc 2mm pour le grip.

> Pour le détail complet (fournisseurs, montage, cinématique) : **[Étude Cheville Cardan](./20_Etude_Cheville_Cardan.md)** | **[Révision 39 kg](./15c_Revision_Cardan_39kg.md)**

