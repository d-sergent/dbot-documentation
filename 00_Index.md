# Documentation Projet Robot D-Bot (Évolution 2026)

Bienvenue dans la documentation technique du projet de robot humanoïde basé sur le D-Bot open-source, adapté et amélioré pour une impression sur Qidi Plus 4.

## Table des Matières

1.  **[Synthèse du Projet](./01_Synthese_Projet.md)**
    *   Vision globale et stratégie de développement (Phases).
    *   Architecture matérielle (Jetson + Spresense + OAK-D).
    *   Points de vigilance critique (Audit 2026).

2.  **[Liste des Achats (BOM Consolidée)](./02_Liste_Achats.md)**
    *   Visserie (ISO 7380, DIN 912, Inserts Ruthex).
    *   Motorisation (RS-00 à RS-05) et PDB Matek.
    *   Électronique de contrôle et Audio.

3.  **[Guide Mécanique](./03_Montage_Mecanique.md)**
    *   Paramètres CAO (Chambrages, Tolérances).
    *   Montage des Roulements 608ZZ.
    *   Préparation Commande CNC.

4.  **[Électronique & Câblage](./04_Electronique_Cablage.md)**
    *   Bus CAN (Daisy Chain, GND critique, Stubs).
    *   Alimentation & Protection (XT60, Matek PDB).
    *   Sécurité Wanptek (Mode OCP).

5.  **[Installation et Logiciel](./05_Logiciel_Configuration.md)**
    *   JetPack 6, ROS 2 Humble et micro-ROS.
    *   Liaison série Jetson/Spresense (UART Pins 8/10).
    *   Configuration SocketCAN (1 Mbps).

6.  **[Décisions Architecturales](./06_Decisions_Architecturales.md)**
    *   Choix du Kit Moteur (RS-05).
    *   Carte d'Extension Sony Spresense.
    *   Positionnement LiDAR et Matériaux.

7.  **[Vision et IA](./07_Vision_IA.md)**
    *   OAK-D Pro S2 FF (Encastrement, Tilt, Stéréo Active).
    *   LiDAR Unitree L2 et Fusion de capteurs Isaac ROS.

8.  **[Audio et Perception](./08_Audio_Perception.md)**
    *   Spatialisation 8 micros (PDM), Beamforming et TPU isolation.
    *   Stratégie Double IMU (Stabilisation Regard).

9.  **[Guide Avancé Impression 3D](./09_Guide_Avance_Impression.md)**
    *   Gestion humidité PA12-CF et Slicer Orca.
    *   Recuit "In-Situ" (PLA+, PETG-CF, PA12-CF) et Macros G-Code.

10. **[Installation Buse Tungstène](./10_Guide_Buse_Tungstene.md)**
    *   Maintenance buse et sécurité électrique générale (Wanptek).
    *   Sauvegarde et maintenance préventive.

11. **[Guide SensiEDGE & Sécurité](./11_Guide_SensiEDGE_Watchdog.md)**
    *   Architecture "Power Manager" (Veille/Réveil).
    *   Code C++ Watchdog et Surveillance Batterie 12S.
    *   Intégration capteurs environnementaux (CommonSense).

12. **[Guide Pièces Métal (CNC)](./12_Guide_Parties_Metal_CNC.md)**
    *   Spécifications Alu 6061-T6 et règles de conception.
    *   Préparation fichiers STEP et astuces commande.

13. **[Sécurité Électrique Essentielle](./13_Securite_Electrique.md)**
    *   Paramètres alimentation labo (Safe Start).
    *   Séquence d'allumage/extinction stricte.
    *   Arrêt d'urgence et sécurité mécanique.

14. **[Cinématique & Choix Moteurs](./14_Cinematique_Moteurs.md)**
    *   Architecture 24 DOF (Tête + Bras + Jambes).
    *   Tableau comparatif RobStride (RS-00 à RS-05).
    *   Couple, Poids, Prix et Applications.

---
*Documentation exhaustive générée et auditée en Février 2026.*
