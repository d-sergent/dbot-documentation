# Guide Préparation Fichiers CNC

Ce guide détaille la procédure pour commander les pièces structurelles en aluminium (Alu 6061) auprès de services d'usinage en ligne (JLCPCB, PCBWay, Xometry).

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

## 4. Astuces de Commande
*   **Regroupement** : Commandez toutes les pièces d'un coup (Bras Droit + Gauche).
*   **Symétrie** : Vérifiez si vos pièces sont identiques (x2) ou symétriques (Miroir). En CNC, une pièce miroir est une référence différente.
*   **Taraudage** : Indiquez clairement sur les plans 2D (PDF associés) quels trous doivent être taraudés (M3, M4). Sinon, ils seront livrés en trous lisses.
