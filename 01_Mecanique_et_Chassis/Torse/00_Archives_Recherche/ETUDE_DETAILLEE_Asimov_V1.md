# 🔬 Étude Détaillée de l'Asimov v1 : Spécifications et Architecture du Torse

Ce document fournit une analyse d'ingénierie approfondie du robot humanoïde open-source **Asimov v1** (développé par Menlo Research), en se basant sur le dépôt officiel `asimovinc/asimov-1` et la documentation technique `docs.menlo.ai`.

---

## 🎨 Architecture Visuelle de l'Asimov v1

Voici le rendu structurel 3D officiel de l'Asimov v1 montrant la complexité de son torse et de son intégration mécanique :

![Structure mécanique du torse de l'Asimov v1](media/design_asimov_v1_style.png)

---

## 📊 1. Spécifications Générales et Performances

L'Asimov v1 est conçu comme un humanoïde de recherche de taille moyenne, visant un excellent rapport coût/performance grâce à une fabrication optimisée.

| Caractéristique | Spécification Officielle |
|:---|:---:|
| **Développeur** | Menlo Research |
| **Hauteur** | 1,20 m |
| **Masse totale** | 35 kg |
| **Degrés de liberté (DoF)** | **25 actionnés** + 2 articulations d'orteil passives |
| **Vitesse de marche** | ~1.2 m/s à 1.5 m/s |
| **Licence Matérielle** | **CERN-OHL-S-2.0** (Open Source matériel fort) |
| **Licence Logicielle** | GPL-2.0 |

---

## ⚙️ 2. Répartition des Degrés de Liberté (DoF)

Les 25 degrés de liberté actionnés sont répartis de manière modulaire à travers les sous-systèmes :

*   **Jambes (12 DoF)** : 6 DoF par jambe (Hanche Yaw/Roll/Pitch, Genou Pitch, Cheville Pitch/Roll). Plus 1 joint d'orteil passif par pied pour l'absorption d'impacts au sol.
*   **Bras et Mains (10 DoF)** : 5 DoF par bras (Épaule Pitch/Roll/Yaw, Coude Pitch, Poignet/Main).
*   **Torse et Cou (3 DoF)** :
    *   **Lombaires/Bassin (1 DoF)** : Pivot Yaw ou Pitch pour dissocier le mouvement des hanches du thorax.
    *   **Cou / Tête (2 DoF)** : Pitch et Yaw pour l'orientation de la suite de capteurs visuels (caméras).

---

## 🔩 3. Architecture du Torse et Conception Structurelle

Le torse de l'Asimov v1 sert de **noyau central** pour la distribution de puissance, le calcul et les ancrages de membres. Sa conception repose sur trois piliers :

### A. La Modularité : L'Interface de Montage Universelle
Menlo Research a breveté / libéré un système de **montage moteur universel**. Les membres (bras et jambes) se boulonnent sur le torse via des colliers de serrage et des flasques standardisés. 
*   **Avantage pour D-Bot** : Cela permet d'isoler le bloc thorax et le bloc pelvis, facilitant les tests de résistance et les modifications sur Fusion 360 sans devoir manipuler l'assemblage complet du robot.

### B. Choix des Matériaux : Le Compromis "Alu 7075" & "PA12-MJF"
Pour supporter les couples massifs générés par le haut du corps et le ballant des bras sans fléchir, le torse n'utilise pas d'impression FDM classique :
1.  **Pièces de type "A" (Structurales)** : Les supports d'épaules, la colonne centrale et les brides de serrage des moteurs sont **usinés en commande numérique (CNC) dans de l'aluminium 7075-T6**. Cela garantit une absence de déformation torsionnelle sous de fortes contraintes dynamiques.
2.  **Pièces de type "C" (Non-structurales)** : Les supports de cartes électroniques, les berceaux de batterie et les carénages de protection sont imprimés en **Nylon PA12 avec la technologie HP Multi Jet Fusion (MJF)**. Ce procédé élimine la délamination des couches et offre une excellente résistance aux vibrations.

### C. Gestion Électronique et Thermique
*   **Emplacement de la Batterie** : Positionnée tout en bas du torse pour abaisser le centre de gravité et stabiliser la marche.
*   **Châssis Ouvert** : Le torse n'est pas scellé hermétiquement. Il utilise une structure en cage ouverte qui assure un refroidissement passif naturel des drivers de moteurs et de l'ordinateur embarqué (généralement situé au centre du thorax).

---

## 💡 4. Préconisations pour le D-Bot basées sur l'Asimov v1

*   **Ne pas tout imprimer en FDM** : L'Asimov v1 prouve que pour un robot de plus de 30 kg, les liaisons lombaires et d'épaules du torse doivent impérativement être en métal (alu CNC) ou, à défaut, renforcées par des inserts métalliques épais. Votre option hybride (tubes carbone Ø25 mm traversant des blocs PA12-CF) est une excellente alternative à l'aluminium CNC d'Asimov.
*   **Copier leur système de câblage** : L'Asimov utilise des goulottes de guidage intégrées directement dans les pièces imprimées en Nylon du torse pour acheminer proprement le bus CAN-FD et la puissance sans frottement sur les parties mobiles.
