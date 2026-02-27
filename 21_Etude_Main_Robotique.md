# Étude Main Robotique : D-Hand CNC Edition

Cette annexe résume les travaux d'ingénierie préliminaires visant à concevoir une main articulée anthropomorphe pour le robot humanoïde D-Bot, en exploitant les capacités d'usinage de précision de la commande numérique (CNC) NestWorks C500.

## 1. Philosophie et Conception Hybride

L'objectif est d'atteindre une dextérité "proche de l'humain" (Force et Vitesse) tout en maintenant l'esprit QDD (Quasi-Direct Drive) du projet global. Pour ce faire, nous nous affranchissons des limites du plastique imprimé 3D. 

L'architecture choisie est **Hybride (Tendons + Actionnement Déporté)**, inspirée du projet open-source *Faive Hand* de l'ETH Zurich, mais optimisée pour l'usinage Aluminium 7075-T6.

*   **Structure CNC (Squelette)** : Phalanges usinées en alliage d'aluminium aéronautique 7075-T6. Intégration de micro-roulements à billes (série MR) éliminant les frictions, et usinage de poulies de renvoi microscopiques polies.
*   **Transmission (Tendons)** : Tresse Dyneema (résistance 40-60 lbs), bien plus résistante que l'acier à poids égal, circulant dans des canaux sans friction (usinage CNC).
*   **Actionnement Déporté** : Les moteurs pour les doigts (Index, Majeur, Annulaire+Auriculaire) sont logés dans l'avant-bras pour alléger la main de la charge morte. 
*   **Actionnement Direct** : Le Pouce dispose de 2 moteurs dédiés logés de manière proximale pour assurer les mouvements d'opposition très réactifs.

## 2. Choix de Motorisation : Compacité et QDD

Loger 6 à 8 muscles/moteurs dans le volume conique restreint d'un avant-bras (Ø 90mm coude à Ø 50mm poignet) est le défi majeur de cette main. 
Les moteurs du système central (ex: Robstride 01 ou MyActuator RMD-X4) sont beaucoup trop massifs. À l'inverse, la solution de luxe de Unitree (F-1515, équipant le G1) propose un réducteur planétaire à un coût unitaire exorbitant (~200€) et limite la fluidité (Backdrivability).

**Le choix optimal retenu est : Le CubeMars GL30 II.**

C'est un moteur "Pancake" typique pour Gimbals, très silencieux et contrôlable en courant pur (FOC).
*   **Diamètre** : 35 mm.
*   **Épaisseur** : 16 mm.
*   **Couple natif** : 0.28 Nm.

### L'Intégration "Linear Staggered Stack"
Grâce à la CNC, le châssis de l'avant-bras deviendra un bloc moteur monobloc usiné "en quinconce" (Linear Staggered Stack). Les moteurs GL30 seront fixés deux par deux, décalés vers le poignet le long d'une colonne vertébrale, maintenant le diamètre total en dessous des standards anatomiques (environ 35 mm de large !).

## 3. Le "Secret" Mécanique : Réduction Cycloïdale Usinée 15:1

Le point faible du GL30 (0.28 Nm) est qu'il est insuffisant pour agripper fermement un objet (Force cible visée : 40 Newtons). Une simple réduction par poulie (ratio nécessaire 1:13) est topologiquement impossible dans l'avant-bras.

La CNC C500 résout ce problème en permettant d'usiner un **miniature Réducteur Cycloïdal de Ratio 15:1**.
*   **Gains** : Le couple passe théoriquement à **3.36 Nm** (Force de serrage > 37 N par doigt au bout d'un doigt de 9 cm).
*   **Réversibilité** : Le profil cycloïdal garantit que la main restera souple quand les moteurs sont éteints, respectant l'esprit QDD (aucune blessure possible lors d'interactions humaines).
*   *Note Technique d'Usinage* : Tolérances fixées à ± 0,02 mm (utilisation de piges d'acier de 3mm pour les goupilles du rotor interne). Un script Python générant les fichiers `.dxf` du profil (15 lobes / excentricité de 0.75mm) est utilisé pour le parcours d'outil.

## 4. Estimation de Coût et Performances

### Performances Attendues
| Caractéristique | D-Hand CNC Edition |
| :--- | :--- |
| Force de Saisie (Grip) | 50 - 80 N (Capable de porter une charge d'environ 5 kg par main) |
| Vitesse de Fermeture | < 0.3 s (Temps de réponse type réflexe) |
| Charge Utile | ~5 kg par main |
| Poids de la main (sans électronique) | ~650 g à 850 g (Moteurs et Aluminium compris) |

### Structure des Coûts (Estimatif par main - 6 moteurs)
*   Moteurs CubeMars GL30 + Drivers : ~450 €
*   Aluminium Brut 7075 : ~50 €
*   Roulements et Visserie de précision : ~60 €
*   Tendon Dyneema : ~15 €
*   **Total Estimé : ~575 € / Main.**

Comparativement, la main Unitree G1 équipée en F-1515 excèderait les 1 500 € par main tout en sacrifiant une part importante de la fluidité (Backdrivability).

## 5. Prochaines Étapes
- Import CAO et optimisation CNC pour les pièces de jonction articulées dérivées des fichiers *Faive / OpenLoong*.
- Test physique du premier bloc réducteur cycloïdal 15:1 usiné en 7075-T6.
- Moulage silicone sur les phalanges en aluminium pour maximiser l'adhésion d'impact.
