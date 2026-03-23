# 12 - Guide Usinage & Pièces Métallurgiques CNC

Ce guide détaille la procédure pour concevoir et usiner les pièces structurelles en aluminium (Alu 6061 ou 7075). Avec la disposition de notre **fraiseuse CNC C500**, toutes les pièces soumises à de grosses contraintes doivent être systématiquement usinées sur place, bien que les principes restent applicables pour des services en ligne.

## 1. Spécifications Techniques
*   **Matériau** : **Aluminium 6061-T6** (Standard aérospatial, bon compromis résistance/poids).
*   **Finition de surface** : **"As Machined"** (Brut d'usinage).
    *   *Conseil* : Ne demandez pas de "Bead Blasting" (Microbillage) ou d'Anodisation pour les prototypes (Phase 2). Cela réduit le coût de 20% à 30%.
*   **Tolérances** : Standard **ISO 2768-m** (+/- 0.1mm) suffisant pour le D-Bot.

## 2. Préparation des Fichiers 3D
*   **Format** : Exportez uniquement en **STEP (.stp / .step)**. Le STL n'est pas accepté pour l'usinage CNC.
*   **Nettoyage CAO** :
    *   Supprimez tous les textes gravés, logos ou décorations en relief. L'usinage de ces détails minuscules explose le temps machine et le prix.
    *   Vérifiez les **rayons internes**. Un outil de fraiseuse est rond. Évitez les angles internes à 90° parfaits, mettez un rayon de 2mm ou 3mm là où c'est possible.

## 3. Points de Contrôle D-Bot
### Alésages (Trous précis)
*   **Dowel Pins** : Les trous pour les goupilles de centrage (3mm et 4mm) doivent être précis (H7 si possible, sinon standard).
*   **Interfaces Moteurs** : Les surfaces de contact avec les moteurs Robstride doivent être parfaitement planes pour dissiper la chaleur du moteur vers le châssis.

## 4. Règle d'or : Interfaces RS-04 (Hanches et Genoux)

Pour dissiper la chaleur et bloquer le cisaillement massif des moteurs **RS-04 (120 N.m)**, il faut **systématiquement faire usiner** sur la **CNC C500** une plaque d'interface en alliage d'Aluminium (5 mm d'épaisseur mini) venant s'intercaler entre le moteur et le squelette en PA12-CF.
Cette plaque d'aluminium jouera deux rôles critiques :
1.  **Dissipateur Thermique (Heatsink)** : Les moteurs QDD chauffent à l'arrêt en retenant les 40kg du robot. L'aluminium absorbera massivement cette chaleur.
2.  **Cage anti-Cisaillement** : La plaque protégera la structure en fibre de carbone imprimée d'une potentielle destruction par ovalisation des trous.

## 5. Astuces de Commande / Production
*   **Regroupement** : Usinez toutes les pièces d'un coup (Bras Droit + Gauche).
*   **Symétrie** : Vérifiez si vos pièces sont identiques (x2) ou symétriques (Miroir). En CNC, une pièce miroir nécessite un nouveau réglage CAO.
*   **Taraudage** : Indiquez clairement sur vos plans d'usinage (Machine C500) quels trous utiliseront la fraise à tarauder (M3, M4).
