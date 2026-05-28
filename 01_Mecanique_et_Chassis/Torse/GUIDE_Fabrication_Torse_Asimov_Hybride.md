# 🛠️ Guide de Fabrication Hybride : Torse Asimov v1 (FDM PA12-CF + CNC Alu)

Ce document trace la méthodologie d'ingénierie pour adapter la coque centrale du torse de l'Asimov v1 (initialement conçue pour l'impression 3D industrielle par frittage de poudre MJF) aux capacités de fabrication d'un atelier maker avancé (Imprimante FDM Qidi Plus 4 + CNC Desktop type Carvera/C500).

---

## 1. Le Défi Structurel : MJF vs FDM

*   **Le design d'origine (MJF)** : La coque Asimov est un bloc massif monobloc, avec d'énormes cavités internes et des points d'attache critiques (épaules, taille, cou). Le Nylon MJF étant isotrope (pas de couches fragiles), la pièce supporte les contraintes dans tous les sens.
*   **La fabrication FDM (Qidi)** : Même avec du filament PA12-CF (Nylon Carbone), l'impression par dépôt de fil crée des **lignes de couches (Axe Z)** qui sont des points de faiblesse face à l'arrachement. De plus, le volume de la machine (305 x 305 x 280 mm) limite la taille des pièces monoblocs.

---

## 2. La Stratégie de Découpe (Le Split en 4 parties)

Pour que la pièce soit imprimable sans supports massifs, sans warping, et avec une résistance mécanique optimale aux épaules, une découpe en croix est requise :

### A. Découpe Frontale (Avant / Arrière)
*   **Pourquoi ?** Poser les deux moitiés à plat sur le plateau garantit que les lignes de couches (Z) seront **perpendiculaires à l'axe des moteurs d'épaules**. Le couple d'arrachement du bras ne tirera pas sur la séparation des couches, mais compressera la matière, ce qui est infiniment plus solide.
*   **Gain** : Quasi-disparition des supports internes, impression à plat rapide.

### B. Découpe Horizontale (Haut / Bas)
*   **Pourquoi ?** Si le torse assemblé dépasse les 280 mm de hauteur de la Qidi Plus 4, il est impératif de le couper horizontalement (au niveau du milieu du ventre). 
*   **Résultat** : Vous obtenez **4 quadrants** (Avant-Haut, Avant-Bas, Arrière-Haut, Arrière-Bas).

### C. Méthode d'Assemblage des 4 Blocs
1.  **Goupilles de centrage** : Intégrez des trous de Ø3 mm ou Ø4 mm sur les plans de jointure dans Fusion 360 pour y glisser des goupilles en acier inoxydable. Cela garantit un alignement parfait au dixième de millimètre des 4 blocs.
2.  **Inserts à chaud (Heat-set inserts)** : Utilisez des inserts en laiton M4 ou M5 posés au fer à souder, et vissez les parties entre elles depuis l'intérieur.

---

## 3. L'Hybridation Métallique (Utilisation de la CNC)

Le plastique PA12-CF finira par fluer (s'écraser) sous la pression des vis de fixation des moteurs RS-04 (épaules) et RS-06 (taille), entraînant un jeu irrécupérable. La CNC vient compenser ce problème en intégrant un "squelette" d'aluminium localisé.

### A. Flasques d'Épaules (Aluminium 6061-T6 ou 7075, 4-5 mm d'épaisseur)
*   **Action dans Fusion 360** : Créez un renfoncement (une "poche") à l'intérieur de la coque PA12-CF au niveau de la fixation des épaules.
*   **Action sur CNC** : Usinez des disques plats ou des plaques rectangulaires en aluminium perforés aux dimensions du moteur RS-04.
*   **Résultat** : Le moteur est boulonné à travers l'aluminium, qui est lui-même pris en sandwich (ou vissé) dans le boîtier PA12-CF. La charge est répartie sur l'aluminium.

### B. Plaque de Base / Taille (Waist Plate)
*   **Action sur CNC** : Le bas du torse supporte la totalité de la masse supérieure (bras, tête, torse, batterie). Il faut usiner une plaque de fondation solide en aluminium qui viendra s'insérer entre les 4 quadrants imprimés en bas du torse, pour y fixer la mécanique de rotation du bassin (Waist DoF).

### C. (Optionnel) Colonne Vertébrale Interne
Si le design à 4 quadrants manque de rigidité, il est possible d'usiner deux "lattes" en aluminium qui viendront se visser à l'intérieur, de haut en bas, pour relier solidement les quadrants "Haut" aux quadrants "Bas".

---

## 4. Workflow Résumé (Plan d'Action)

1.  **Récupérer le STEP** du torse Asimov v1.
2.  **Fusion 360** : Réaliser les découpes (Split Body) avec le plan XZ (Avant/Arrière) et le plan XY (Haut/Bas).
3.  **Fusion 360** : Modéliser les poches pour inserts CNC et les trous de goupilles.
4.  **CAM (CNC)** : Générer le G-Code pour usiner les plaques d'épaules et de base dans de la tôle d'aluminium de 5 mm.
5.  **Impression** : Imprimer les 4 quadrants en PA12-CF (buse durcie, plateau chaud, enceinte fermée).
6.  **Assemblage final** : Pose des inserts à chaud, encastrement des plaques alu, verrouillage par goupilles et visserie M4/M5.
