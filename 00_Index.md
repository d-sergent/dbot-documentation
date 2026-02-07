# Documentation Projet Robot D-Bot (Évolution 2026)

Bienvenue dans la documentation technique du projet de robot humanoïde basé sur le D-Bot open-source, adapté et amélioré pour une impression sur Qidi Plus 4.

## Table des Matières

1.  **[Synthèse du Projet](./01_Synthese_Projet.md)**
    *   Vision globale
    *   Architecture matérielle (Jetson + Spresense + OAK-D)
    *   Impression 3D (Qidi Plus 4)

2.  **[Liste des Achats (BOM Consolidée)](./02_Liste_Achats.md)**
    *   Visserie (M3, M4, M5, Inserts)
    *   Moteurs (Robstride RS05, RS01-RS04)
    *   Électronique (InnoMaker, Connecteurs, Câbles)
    *   Liens d'achat recommandés

3.  **[Guide Mécanique](./03_Montage_Mecanique.md)**
    *   Paramètres d'impression & Fusion 360 (Chambrages, Tolérances)
    *   Intégration des moteurs supplémentaires (Cou, Poignets)
    *   Positionnement LiDAR Unitree L2

4.  **[Électronique & Câblage](./04_Electronique_Cablage.md)**
    *   Architecture CAN Bus (Jetson -> USB2CAN -> Robstride)
    *   Alimentation & Protection (XT60, Masses)
    *   Choix Spresense (Standard vs LTE) & OAK-D Pro

5.  **[Logiciel & Configuration](./05_Logiciel_Configuration.md)**
    *   Configuration SocketCAN sur Jetson (Linux)
    *   Intégration ROS2 (Idées : Beamforming, SLAM)
    *   Outils de développement

6.  **[Décisions Architecturales](./06_Decisions_Architecturales.md)**
    *   Pourquoi la Spresense Extension Board Standard ?
    *   Positionnement LiDAR.

7.  **[Guide Usinage CNC (Phase 2)](./07_Guide_Usinage_CNC.md)**
    *   Préparation des fichiers STEP (Alu 6061).
    *   Astuces pour réduire les coûts.

8.  **[Sécurité & Mise en Marche](./08_Securite_Mise_En_Marche.md)**
    *   Paramétrage Alimentation (24V / 1A).
    *   Séquence d'allumage critique.
    *   Arrêt d'urgence.

---
*Documentation générée automatiquement à partir des archives de discussion (Février 2026).*
