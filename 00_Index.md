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
    *   Unitree L2 (Option V2) et Fusion de capteurs Isaac ROS.

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
    *   Code C++ Watchdog et Surveillance Batterie 13S (48V).
    *   Intégration capteurs environnementaux (CommonSense).

12. **Usinage CNC et Métal**
    *   12a — [Guide Pièces Métal (Bases)](./12_Guide_Parties_Metal_CNC.md) (Règles générales et Aluminum 6061-T6).
    *   12b — [Bibliothèque C500 & Vitesses de Coupe](./12b_Bibliotheque_C500_Vitesses_Coupe.md) (RPM/Feeds DLC et Ajustements H7).

13. **[Sécurité Électrique Essentielle](./13_Securite_Electrique.md)**
    *   Paramètres alimentation labo (Safe Start).
    *   Séquence d'allumage/extinction stricte.
    *   Arrêt d'urgence et sécurité mécanique.

14. **[Cinématique & Choix Moteurs](./14_Cinematique_Moteurs.md)**
    *   Architecture 24 DOF (Tête + Bras + Jambes).
    *   Tableau comparatif RobStride (RS-00 à RS-06).
    *   Couple, Poids, Prix et Applications.

15. **[Analyse Biomécanique — Hub de Navigation](./15_Analyse_Biomecanique.md)**
    *   15a — [Locomotion & Portage Baseline](./15a_Analyse_Locomotion_Baseline.md)
    *   15b — [Configurations Moteurs & Évolutions (Options A/B/C/D)](./15b_Configurations_Moteurs.md)
    *   15c — [Révision Cardan 39 kg](./15c_Revision_Cardan_39kg.md)
    *   15d — [Genou & Course — 5 Solutions](./15d_Genou_et_Course.md)
    *   15e — [Alternatives Moteurs Genou](./15e_Alternatives_Moteurs_Genou.md)
    *   15f — [Portage de Charges & Marche](./15f_Portage_Charges_et_Marche.md)
    *   15g — [Solution S6 : Courroie GT3 Genou](./15g_Solution_S6_Courroie_GT3_Genou.md)
    *   15h — [Alternatives Transmission Genou](./15h_Alternatives_Transmission_Genou.md)

16. **[Conclusions & Architecture Finale D-Bot](./16_Conclusions_Architecture_DBot.md)**
    *   Décisions définitives par articulation (cheville, genou, hanche, bras, main).
    *   Performances globales estimées (vitesse, charge, grip).
    *   Points d'attention V1 et roadmap évolution.

---

### Annexes

16. **[Annexe — Recherche Batteries NMC](./16_Annexe_Batterie_NMC.md)**
    *   Packs NMC 21700 48V disponibles en France (AT WEY, B-Volt, OZO).
    *   Intégration et schéma électrique 48V.

17. **[Annexe — État des Lieux Semi-Solide](./17_Annexe_Batterie_SemiSolide.md)**
    *   Analyse du marché semi-solide (2026) : aucun pack compact viable.
    *   Veille technologique 2027+.

18. **[Annexe — Comparatif Batteries & Scénarios](./18_Annexe_Batterie_Comparatif.md)**
    *   Tableau NMC vs LiFePO4 vs Semi-Solide.
    *   Scénarios court/moyen/long terme.

19. **[Perception Spatiale & LiDAR (V2)](./19_Perception_Spatiale_LiDAR.md)**
    *   Analyse complète Unitree L2 (points forts et problèmes IMU confirmés).
    *   Benchmark industrie (G1, Optimus, Figure 02, Digit).
    *   Alternatives évaluées (Livox MID-360, 2D LiDARs, multi-caméras, vision pure).
    *   Solution retenue : **Triple fusion L2 + OAK-D Pro + BMI270**.

21. **[Étude Cheville Cardan](./20_Etude_Cheville_Cardan.md)**
    *   Historique évolutif (GE12UK → Série → RS-06 → **Cardan DIN 808**).
    *   Architecture retenue : 2× RS-03 + double bielles (type Optimus).
    *   Achats : cardans Michaud Chailly, bielles carbone, rotules Igus.

22. **[Étude Main Robotique — D-Hand Premium](./21_Etude_Main_Robotique.md)**
    *   8 DOF, servos **Dynamixel XC330-T288-T** dans l'avant-bras.
    *   Tendons Dyneema, poulies CNC, grip ~80-100 N.
    *   Feuille de route et intégration logicielle (Dynamixel SDK + ROS 2).

23. **[Usinage CNC C500](./22_Usinage_CNC_C500.md)**
    *   Outils métal DLC et règles d'ébavurage (H7).
    *   Danger des collets : Séparation Impérial vs Métrique.
    *   Gestion intelligente des porte-outils (RFID).

24. **[Stratégie Ultralight Sous-Genou](./23_Strategie_Ultralight_Sous_Genou.md)**
    *   Gestion de l'inertie distale par hybridation de matériaux.
    *   Bielles et Tibia en carbone + embouts PA12-CF.
    *   Architecture de pied composite (Carbone/TPU) pour l'amorti.

25. **[Étude Extension Carbone (Fémur & Bras)](./24_Etude_Extension_Carbone_Membres.md)**
    *   Analyse de l'architecture Tube Carbone + Goupille Mécanindus pour les autres membres.
    *   Validation pour les Bras (Humérus) et Avant-Bras.
    *   Limites et complexité d'intégration pour le Fémur (Cuisse).

26. **[Étude : Compatibilité IA & Apprentissage par Renforcement (Isaac Gym)](./25_Compatibilite_IA_Isaac_Gym.md)**
    *   Standards URDF de l'industrie pour les algorithmes RL (NVIDIA).
    *   Analyse du Waist Yaw (Rotation Z) et des degrés de liberté Bras/Épaule/Main.
    *   Stratégie Sim2Real pour le D-Bot V1.

27. **[Étude : Architecture du Bloc Pelvien (Cardan de Hanche)](./26_Etude_Bloc_Pelvien_Hanche.md)**
    *   Analyse de la chaîne cinématique de la hanche (Yaw → Roll → Pitch).
    *   Comparatif de l'approche K-Bot vs Tesla Optimus / Unitree.
    *   Jonction du dernier maillon (Pitch) avec le Fémur Hybride Sandwich.

28. **[Étude : Architecture Épaule D-Bot (Positionnement Moteurs)](./27_Etude_Epaule_Architecture.md)**
    *   Analyse de l'architecture K-Bot (empilement perpendiculaire RS-03/RS-02).
    *   Comparatif Tesla Optimus, Unitree H1, Figure 02, Atlas Électrique.
    *   Recommandation Stacked Perpendicular avec brackets CNC Alu.

29. **[Glossaire Technique Robotique](./28_Glossaire_Technique.md)**
    *   Définitions détaillées des concepts (Pitch, Roll, Yaw, Gimbal Lock, Backdrivability...).

30. **[Étude : Montage Vertical RS-05 pour le Roll de Tête](./29_Etude_Montage_Cou_RS05.md)**
    *   Montage vertical du RS-05 avec roulement de support externe (6001-2RS).
    *   Schéma de montage, flux de forces, choix du roulement et BOM.
    *   Vérification de couple gravitationnel et séquence de montage.

---
*Documentation exhaustive générée et auditée en Février/Mars 2026.*
