# Décisions Architecturales

Ce document recense les choix techniques structurants effectués durant la phase de conception (Discussions Février 2026).

## 1. Choix du Kit Moteur
**Décision** : Ajouter 2 moteurs **Robstride 05 (RS05)** au kit standard.
*   **Pourquoi ?** Le kit de base manquait de couple au niveau du cou et des poignets pour un humanoïde de cette taille.
*   **Conséquence** : Nécessite des vis spécifiques (M4 Acier 12.9) et un ancrage châssis renforcé (PETG-CF 100% Infill).

## 2. Carte d'Extension Sony Spresense
**Choix** : **Extension Board Standard** (vs LTE Extension Board).
*   **Motif Principal** : Capacités Audio et Évolutivité.
    *   La carte Standard permet de connecter jusqu'à **8 microphones numériques** (essentiel pour le *beamforming* et l'interaction vocale avancée).
    *   Elle possède des connecteurs Arduino compatibles, permettant d'ajouter un shield LTE tiers plus tard si nécessaire.
    *   La carte LTE officielle sacrifie trop d'I/O audios (max 4 micros) pour un usage "autonome outdoor" qui n'est pas la priorité immédiate.

## 3. Positionnement LiDAR (Unitree L2)
**Choix** : **Haut du Torse, devant le cou, incliné 10-20° vers l'avant**.
*   **Alternatives rejetées** :
    - *Sommet de la tête* : FOV idéal mais nécessite un câble passant dans le cou articulé (Pan/Tilt RS-05) — risque d'usure et de torsion du câble, poids en hauteur (+CdG).
    - *Tibia* : Trop bas, ne voit pas les tables ni les obstacles en hauteur.
    - *Bassin* : Occulté par les jambes lors de la marche.
*   **Avantage du torse haut** :
    - Champ de vision 360° dégagé (les bras n'occultent que temporairement lors de manipulation).
    - Pas de contrainte mécanique de câble articulé.
    - Position stable (pas de vibrations du cou Pan/Tilt) = meilleur SLAM.
    - L'inclinaison de 10-20° compense le décalage par rapport au sol.
*   **Compensation** : L'OAK-D Pro (vision stéréo) dans la tête complète le champ de vision frontal quand les bras sont levés.

## 4. Matériaux et Fixations
*   **Visserie** : Standardisation sur **DIN 912** (Cylindrique) Inox A2.
*   **Inserts** : Laiton (type Ruthex) préférés à l'Inox.
    *   *Raison* : L'Inox conduit mal la chaleur, rendant la pose dans le plastique très risquée (fonte excessive autour de l'insert). La longueur de l'insert prime sur sa matière.
