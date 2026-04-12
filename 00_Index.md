# Documentation Projet Robot D-Bot (Évolution 2026)

Bienvenue dans la documentation technique du projet de robot humanoïde D-Bot. Cette documentation est optimisée pour l'IA et la consultation rapide.

## 🚀 ÉTAT DE L'ART (SYNTHÈSES PAR ARTICULATION)
*Pour une vision technique immédiate des dernières décisions validées (RobStride & Dynamixel).*

- **[Synthèse : Épaule (Shoulder 3 DOF)](./Synthese_Etat_Actuel/SYNTHESE_Epaule.md)**
- **[Synthèse : Hanche (Hip 3 DOF)](./Synthese_Etat_Actuel/SYNTHESE_Hanche.md)**
- **[Synthèse : Genou (Knee 300Nm)](./Synthese_Etat_Actuel/SYNTHESE_Genou.md)**
- **[Synthèse : Cheville (Ankle Cardan)](./Synthese_Etat_Actuel/SYNTHESE_Cheville.md)**
- **[Synthèse : Mains (D-Hand Hybrid)](./Synthese_Etat_Actuel/SYNTHESE_Mains.md)**
- **[Synthèse : Torse & Cou (Neck)](./Synthese_Etat_Actuel/SYNTHESE_Torse_Cou.md)**
- **[Synthèse : Audio & IMU](./Synthese_Etat_Actuel/SYNTHESE_Audio_IMU.md)**
- **[Synthèse : Électronique & Câblage](./Synthese_Etat_Actuel/SYNTHESE_Electronique.md)**

---

## 📖 GUIDES DE RÉFÉRENCE (V1)

1.  **[Synthèse du Projet](./01_Synthese_Projet.md)** : Vision, Roadmaps et Architecture CPU/IA.
2.  **[Liste des Achats (BOM)](./02_Liste_Achats.md)** : Composants exacts et liens marchands.
3.  **[Guide Montage Mécanique](./03_Montage_Mecanique.md)** : Tolérances, roulements et CNC.
4.  **[Électronique & Câblage](./04_Electronique_Cablage.md)** : Bus CAN, Star Power 48V et PDB.
5.  **[Logiciel & IA Libre (OpenClaw)](./05_Logiciel_Configuration.md)** : JetPack, ROS2, mROS et Config Agent.
7.  **[Vision et IA](./07_Vision_IA.md)** : OAK-D Pro S2 FF et LiDAR Unitree L2 (V2).
8.  **[Architecture Audio](./08_Architecture_Audio.md)** : XMOS XVF-3800 et Haut-Parleur.
18. **[Stratégie IMU et Fusion](./18_Strategie_IMU_Fusion.md)** : Équilibre Bipède (416Hz) et V-SLAM.
9.  **[Guide Impression 3D](./annexes/impression_3d/09_Guide_Avance_Impression.md)** : Orca Slicer, PA12-CF et Recuit.
12a. **[Guide Pièces Métal CNC](./annexes/cnc/12_Guide_Parties_Metal_CNC.md)** : C500, Alu 7075-T6 et plaques RS-04.
12b. **[Bibliothèque CNC NestWorks](./annexes/cnc/12b_Bibliotheque_C500_Vitesses_Coupe.md)** : Vitesses de coupe et ajustements H7.
14. **[Cinématique & Moteurs](./14_Cinematique_Moteurs.md)** : Tableau comparatif RobStride.

---

## 🛠️ ANNEXES & GUIDES DE DEBUG
*Guides d'interfaçage ponctuel et configurations de bas niveau.*
### Actionneurs RobStride
#### Configuration Initiale
- 31. **[Guide Debug RS-05 — Module EL05 & MotorStudio](./annexes/robstride/configuration_initiale/31_Guide_Debug_RS05_MotorStudio.md)** : Câblage CAN, DIP switches, procédure Wanptek, et connexion logicielle MotorStudio.
- 32. **[Configuration ID, Zéro & Limites (RS-05 Cou)](./annexes/robstride/configuration_initiale/32_Configuration_ID_Limites_Cou.md)** : Procédure ID, calibration du zéro et bornes de rotation logicielles.

#### Firmware
- **[Notes de Mise à Jour Firmware (04/2026)](./annexes/robstride/firmware/01_Notes_Maj_Firmware.md)** : Traduction exhaustive du changelog des firmwares (séries RS00 à RS06) avec explications sur le calibrage, l'anti-rétro-entraînement et le watchdog.

---

## 🏛️ DOSSIERS D'ÉTUDES (ARCHIVES)
*Historique des calculs, alternatives explorées et décisions passées.*

- **[Étude 34 kg Baseline](./Archives/ETUDE_34kg_Baseline.md)** (Ancienne config K-Bot)
- **[Étude Configurations Moteurs](./Archives/ETUDE_Configurations_Moteurs_Historique.md)** (Évolution A/B/C/D)
- **[Étude Alternatives Moteurs Genou](./Archives/ETUDE_Alternatives_Moteurs_Genou.md)**
- **[Étude Transmissions Genou](./Archives/ETUDE_Knee_Legacy_Transmissions.md)** (Vérin vs GT3)
- **[Étude Comparatif Batteries](./Archives/ETUDE_Batterie_Comparatif.md)**
- **[Étude Batteries Semi-Solide](./Archives/ETUDE_Batterie_Semi_Solide.md)**
- **[Étude Cheville Cardan](./20_Etude_Cheville_Cardan.md)**


---
*Documentation réorganisée en Mars 2026 pour optimiser la clarté et l'indexation IA.*
*Documentation exhaustive générée et auditée en Février/Mars 2026.*
