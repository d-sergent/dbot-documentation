# Étude : Structure en Tube Carbone pour les Membres Supérieurs (Bras & Avant-Bras)

Ce document détaille l'analyse d'ingénierie mécanique validant l'utilisation de profilés cylindriques en fibre de carbone pour l'humérus (bras) et l'avant-bras du D-Bot, ainsi que les méthodes d'intégration et d'assemblage associées.

---

## 1. Justification Technologique (Pourquoi le carbone aux bras ?)

L'application de tubes en fibre de carbone aux membres supérieurs est extrêmement pertinente et apporte des bénéfices critiques pour un robot humanoïde agile :

*   **Réduction de l'inertie en balancement** : En marche dynamique, le balancement des bras agit comme un pendule passif ou actif pour contrecarrer le moment de lacet généré par le bassin et les jambes. Des bras plus légers permettent une oscillation beaucoup plus rapide sans injecter de forces perturbatrices massives dans le buste, ce qui stabilise la marche générale.
*   **Soulagement des couples statiques** : Réduire le poids de l'avant-bras et du bras éloigne la masse de l'axe de pivotement de l'épaule (grand bras de levier). Cela diminue considérablement la charge constante exercée sur les moteurs RS-04 (Pitch) et RS-03 (Roll) d'épaule, réduisant la consommation électrique et limitant l'échauffement statique.
*   **Tenue mécanique aux efforts modérés** : Contrairement aux jambes qui subissent les impacts répétés du poids du robot (40 kg + facteurs dynamiques), les efforts subis par les bras sont modérés. Le portage maximal cible étant de ~2 kg (voire 3-4 kg), les sollicitations en flexion, torsion et arrachement restent parfaitement dans la zone de confort des liaisons collées sur carbone.

---

## 2. Intégration par Segment

### 2.1 L'Avant-Bras (Coude ➔ Poignet)
L'avant-bras relie le moteur du coude (RS-06) au poignet (moteur RS-00 et cluster de servomoteurs Dynamixel de la main).
*   **Spécification Tube** : Un **Tube Carbone de Ø25 mm ou Ø30 mm** (épaisseur de paroi ~1.5 mm à 2 mm) offre le meilleur compromis poids/rigidité.
*   **Méthode de raccordement** : Utilisation d'inserts cylindriques en aluminium 6061-T6 (usinés CNC) ou en filament PA12-CF (imprimés à haute densité). Ces inserts sont collés à la colle époxy structurelle bi-composant (type DP490 de 3M) à l'intérieur du tube carbone.
*   **Méthode de verrouillage** : Pour sécuriser la liaison face aux vibrations et prévenir les risques de glissement du collage, l'insert et le tube sont traversés et verrouillés par une **goupille élastique double (Mécanindus) de Ø2 mm ou Ø2.5 mm**.

### 2.2 Le Bras / Humérus (Épaule ➔ Coude)
L'humérus relie l'axe de rotation de l'épaule (RS-03/RS-02) au moteur du coude (RS-06). Il subit principalement des efforts de flexion sous charge bras tendu.
*   **Spécification Tube** : Un **Tube Carbone de Ø35 mm ou Ø40 mm** est nécessaire pour garantir une rigidité structurelle parfaite en flexion.
*   **Méthode de raccordement** : Même technique d'inserts en aluminium collés. La goupille de verrouillage Mécanindus (Ø3 mm ou Ø4 mm) travaille en cisaillement pur, offrant une résistance structurelle indestructible.
*   **Liaison Moteurs** : Les inserts se prolongent par des platines de fixation planes usinées CNC, venant se visser directement sur les cloches d'entraînement des moteurs RobStride.

---

## 3. Synthèse d'Intégration (Membres Supérieurs)

| Segment | Diamètre Tube | Type d'Insert | Verrouillage Mécanique | Bénéfice Principal |
| :--- | :---: | :--- | :--- | :--- |
| **Humérus (Bras)** | **Ø35 - Ø40 mm** | Aluminium 6061 CNC | Goupille Mécanindus Ø3-4mm | Rigidité flexion bras tendu, élimination du jeu |
| **Avant-Bras** | **Ø25 - Ø30 mm** | Alu CNC ou PA12-CF | Goupille Mécanindus Ø2-2.5mm | Réduction drastique d'inertie pour la main, gain de poids |
