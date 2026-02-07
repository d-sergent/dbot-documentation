# Synthèse du Projet D-Bot (Évolution)

## 1. Vision et Objectifs
Le projet consiste à construire un robot humanoïde basé sur la plateforme open-source **D-Bot**, mais en l'améliorant significativement avec des actionneurs modernes et une intelligence embarquée avancée.

### Améliorations Clés (vs D-Bot Original)
- **Motorisation Avancée** : Intégration de moteurs **Robstride RS05** (x2) pour renforcer le cou et les poignets, en plus du kit standard (RS01-RS04).
- **Perception 3D** : Ajout d'un **LiDAR Unitree L2** (sur la tête) et d'une caméra stéréoscopique **OAK-D Pro**.
- **Intelligence Embarquée** : Cerveau principal **NVIDIA Jetson Orin Nano** couplé à une **Sony Spresense** pour la gestion audio/capteurs temps réel.
- **Fabrication** : Impression 3D haute qualité sur une **Qidi Plus 4** avec du filament **PETG-CF** (PETG renforcé fibre de carbone) pour la rigidité structurelle.

## 2. Architecture Matérielle
L'architecture repose sur une séparation claire entre la puissance de calcul (IA) et le contrôle temps réel (Moteurs/Capteurs bas niveau).

```mermaid
graph TD
    A[NVIDIA Jetson Orin Nano] -- USB3 (High Speed) --> B[Sony Spresense]
    A -- USB/CAN --> C[InnoMaker USB2CAN-C]
    C -- Bus CAN (1 Mbps) --> D[Moteurs Robstride]
    A -- USB3 --> E[OAK-D Pro (Vision AI)]
    A -- USB --> F[LiDAR Unitree L2]

    subgraph "Contrôle Moteur"
    D --> D1[RS01..04 (Membres)]
    D --> D2[RS05 (Cou/Poignets)]
    end

    subgraph "Perception Audio/Sensor"
    B --> B1[Micros (Beamforming)]
    B --> B2[Capteurs I2C/SPI]
    end
```

## 3. Plateforme de Fabrication (Qidi Plus 4)
La Qidi Plus 4 a été choisie pour sa capacité à imprimer des matériaux techniques à haute température.

- **Matériau Recommandé** : PETG-CF (Facile à imprimer, rigide, esthétique carbone).
- **Paramètres Critiques** :
  - **Chambrages (Counterbore)** : Indispensables pour noyer les têtes de vis.
  - **Tolérances** : Marge de 0.5mm sur les diamètres de perçage vis.
  - **Remplissage** : 100% pour les pièces de force (hanches, épaules), 40% gyroid pour les coques esthétiques.

---
**Note** : Ce projet est une évolution active. Les choix techniques documentés ici reflètent l'état des lieux en Février 2026.
