# 28 - Synthèse des Dimensions Physiques et Leviers (D-Bot)

Ce document centralise toutes les hypothèses de dimensions physiques, longueurs de membres, et bras de leviers utilisées jusqu'à présent pour les calculs de cinématique, de locomotion et de couple du robot D-Bot. 

Il sert de point de référence unique (Source of Truth) pour la modélisation CAO et la commande numérique.

## 1. Dimensions Globales et Torse (Hypothèse V1)

| Paramètre | Valeur | Statut |
| :--- | :---: | :--- |
| **Hauteur Totale** | **~1.47 m** | Cible (recalculée avec torse 420 mm) |
| **Torse (Hauteur Épaule → Hanche)** | **420 mm** | ✅ Hypothèse V1 |
| **Torse (Largeur, Droite ↔ Gauche)** | **300 mm** | ✅ Hypothèse V1 |
| **Torse (Profondeur, Avant ↔ Arrière)** | **220 mm** | ✅ Hypothèse V1 |
| Largeur d'Épaules (Entraxe RS-04 Pitch) | ~300 mm | Déterminée par la cage alu |
| Largeur de Bassin (Entraxe RS-04 Hanche) | ~300 mm | Déterminée par la cage alu |

> Voir [29_Etude_Squelette_Torse_Alu.md](./29_Etude_Squelette_Torse_Alu.md) pour l'étude structurale complète de la cage aluminium.

## 2. Membres Inférieurs (Jambes)
*Données déduites de `15a_Analyse_Locomotion_Baseline.md`.*
- **Cuisse (Axe Hanche -> Axe Genou)** : ~350 mm (35 cm).
- **Tibia (Axe Genou -> Axe Cheville)** : ~350 mm (35 cm).
    - *Note de fabrication* : Si l'on utilise un tube carbone structurel, sa longueur propre est estimée à environ ~220 mm. La longueur cinématique de 350 mm est atteinte en incluant les brackets haut (genou) et bas (cheville).
- **Pied (Levier Cheville -> Orteil/Talon)** : ~100 mm (10 cm).

### Leviers Spécifiques (Cinématique du Genou à Tirant)
*Données déduites de l'intégration GT3 et architecture à tirant.*
- **Bras de Manivelle (Crank haut, lié au moteur RS-04)** : 60 mm.
- **Bras de Levier (Genou bas, lié au tibia)** : 90 mm.
- **Longueur du Tirant (Bielle de transmission)** : ~250 mm.
- **Bras de levier projeté au sol** : ~180 mm (18 cm). 
    - *Note* : C'est cette distance horizontale (centre de gravité -> appui du pied) lors de la marche genoux fléchis qui a permis de calculer l'exigence de couple critique de 16.2 N.m par jambe (soit ~300 N.m après marge de sécurité dynamique).

## 3. Membres Supérieurs (Bras)
- **Bras (Axe Épaule -> Axe Coude)** : ~250 mm (25 cm).
- **Avant-bras (Axe Coude -> Axe Poignet)** : ~220 mm (22 cm).
- **Main (Axe Poignet -> Bout effecteur)** : ~250 mm (25 cm).
- **Allonge combinée de l'avant-bras et main** : ~470 mm (47 cm).

## 4. Tête et Capteurs
- **OAK-D Pro (Vision)** : Entraxe de fixation de 75 mm (vis M3). Encastrement ~98x30 mm.
- **Cou (Double RS-05)** : *[Incertain - À figer en CAO]* - La superposition ou juxtaposition des deux moteurs RS-05 définira la hauteur totale du cou et le débattement de la tête.

## 5. Synthèse des Incertitudes (À définir pour la construction)
Pour sécuriser la modélisation CAO finale et la génération des fichiers URDF (pour ROS 2 / Isaac Gym), les points suivants doivent être impérativement relevés et figés une fois le design 3D terminé :

1.  **L'entraxe Y des hanches** : C'est la largeur du bassin. Elle est critique pour planifier la marche, l'équilibre latéral et le balancement (transfert de masse gauche/droite).
2.  **L'entraxe Y des épaules** : Détermine l'espace disponible dans le torse supérieur (pour les Matek PDB et l'électronique) et les collisions possibles entre les bras et le buste.
3.  **La position X, Y, Z du Centre de Masse (CoM)** : À extraire du logiciel de CAO (Fusion 360) une fois le torse numériquement peuplé par la batterie 12S, l'ordinateur de bord (Jetson) et le câblage.

## 6. Schéma Visuel Simplifié (Stick-Figure)

Voici une représentation schématique du squelette du D-Bot avec les dimensions principales calculées :

```text
                  [ LiDAR ]
               [ OAK-D Pro ]
                    |    Cou (RS-05 × 2, À figer)
                .---o---.  <── Épaules (Traverse 35×35)
       Bras    /    |    \           ← 300 mm →
     (250mm)  o     |     o
             /      |      \     ┐
    Av-Bras o       |       o    │
    (220mm) |       |       |    │  Torse
            |       |       |    │  420 mm
      Main  o       |       o    │  (Cage Alu)
    (250mm) |   .---o---.   |    │  Prof: 220 mm
            X  /  60×60  \  X    ┘
              o  (Hanches) o  <── Bassin (Traverse 60×60)
              |           |
              |           |  Cuisse
              |           |  (350 mm)
              |           |
              o           o  <── Genou (Manivelle: 60mm / Levier: 90mm)
              |           |
              |           |  Tibia
              |           |  (350 mm)
              |           |
              o           o  <── Cheville
             /_\         /_\ 
            Pied (Levier : 100 mm)

    |──────────────────────────────|
    Hauteur Totale Estimée : ~ 1.47 m
    (Cou + 420 + 350 + 350 + 100 + pieds)
```
