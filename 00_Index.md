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
    *   Bus CAN Bus (Daisy Chain, GND critique, Stubs).
    *   Alimentation & Protection (XT60, Matek PDB).
    *   Sécurité Wanptek (Mode OCP).

5.  **[Installation et Logiciel](./05_Logiciel_Configuration.md)**
    *   JetPack 6, ROS 2 Humble et micro-ROS.
    *   Liaison série Jetson/Spresense (UART Pins 8/10).
    *   Configuration SocketCAN (1 Mbps).

6.  **[Réseau et Sécurité](./06_Architecture_Reseau.md)**
    *   WiFi 5GHz (Archer T3U) et VPN Wireguard.

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

---
*Documentation exhaustive générée et auditée en Février 2026.*
