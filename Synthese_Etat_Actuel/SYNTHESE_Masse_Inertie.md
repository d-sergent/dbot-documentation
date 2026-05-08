# SYNTHÈSE : Masse, Inertie & Équilibre

## 1. Bilan des Masses (Mai 2026)
Le D-Bot a évolué vers une configuration "Performance" plus lourde mais plus capable.

| Segment | Masse estimée | Note |
| :--- | :---: | :--- |
| **Moteurs (26 RobStride)** | **21.2 kg** | Inclut 2x RS-02 supination additionnels |
| **Mains (2x D-Hand Hybrid)** | **1.6 kg** | 16 servos Dynamixel + tendons + structure |
| **Batterie (13S 10Ah NMC)** | **2.3 kg** | Standard VAE pour Phase 1 |
| **Structure & Électronique** | **15.1 kg** | Squelette Alu CNC + PA12-CF + Jetson |
| **TOTAL (Robot Complet)** | **~40.2 kg** | **Masse de référence actuelle** |

## 2. Analyse de l'Inertie
L'ajout de moteurs aux bras a été compensé par une meilleure répartition :
- **Bras** : Les moteurs lourds (RS-04, RS-02) sont proximaux. L'inertie distale est minimisée (seulement RS-00 au poignet).
- **Jambes** : Architecture cardan permettant de remonter les moteurs RS-03 dans le tibia. Masse distale quasi-nulle.
- **Résultat** : Le robot est plus lourd mais plus "nerveux" dans ses mouvements de balancement.

## 3. Marges de Puissance (Genou/Cheville)
Malgré les **40.2 kg**, les marges restent excellentes grâce aux upgrades :
- **Cheville (120 N.m)** : Marge de **+160%** en statique.
- **Genou (300 N.m via GT3)** : Marge de **+60%** en marche normale (2-3 km/h).

## 4. Stratégie IMU & Équilibre
- **IMU Principale (Body)** : **BMI270** située sur la Sony Spresense dans le torse (Fréquence : 416 Hz).
- **IMU Vision (Head)** : IMU interne de l'OAK-D, utilisée exclusivement pour la stabilisation du regard (VOR) et non pour l'équilibre global.
- **Capteurs Sol** : 8x FSR (4 par pied) pour le calcul du Centre de Pression (CoP).

---
*Dernière mise à jour : Mai 2026*
