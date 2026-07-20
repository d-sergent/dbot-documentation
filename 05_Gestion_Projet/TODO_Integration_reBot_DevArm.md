# 📝 TODO — EXPLOITATION DU DÉPÔT `reBot-DevArm` (ÉCOSYSTÈME ROBOSTRIDE)
**Plan d'Action Technique pour Réexploiter les Drivers, le Framework LeRobot, la Dynamique Pinocchio, la CAO 3D et l'Alimentation 48V sur D-Bot**

---

## 1. Contexte & Objectif

Le dépôt local `/Users/Shared/Mon Google Drive Physique/reBot-DevArm` (développé par Seeed Studio pour le bras 6 axes *reBot Arm B601 RS*) utilise exactement le même écosystème de motorisation que D-Bot : **moteurs brushless RobStride (RS00 / RS06), bus CAN 1 Mbps, et alimentation 48V**.

L'objectif de cette TODO est de réexploiter directement les 5 piliers technologiques de ce dépôt (SDK Motorbridge, Hugging Face LeRobot, Pinocchio Dynamics, CAO/Câblage 3D, et Station 48V) pour accélérer le développement de D-Bot.

---

## 2. Feuille de Route Opérationnelle (6 Jalons)

### 📌 **Jalon 1 : Drivers & SDK Python RobStride (`Motorbridge`)**
- [ ] **Extraire & Tester le SDK `Motorbridge` :**
  - Récupérer les classes Python du SDK Motorbridge (`motorbridge.seeedstudio.com`) situées dans le dépôt.
  - Valider le fonctionnement sous Python 3.11 sur le Mac et la Jetson avec l'adaptateur USB-CAN InnoMaker RS-05 (`can0`/`can1`).
- [ ] **Validation des Modes de Commande RobStride :**
  - Valider la trame du mode **MIT Control** ($K_p, K_d, \theta, \dot{\theta}, \tau_{ff}$) pour la commande souple des moteurs.
  - Valider la lecture de la télémétrie en boucle continue : position (encodeur 14-bit), vitesse, courant (couple) et température moteur.
- [ ] **Procédure de Calibration Zero-Offset :**
  - Intégrer les scripts de remise à zéro de l'encodeur absolu pour l'alignement mécanique des articulations.

---

### 📌 **Jalon 2 : Intégration Hugging Face `LeRobot` (Imitation Learning)**
- [ ] **Adaptateur D-Bot pour `LeRobot` :**
  - Étudier le composant `rebot_arm_b601_rs_lerobot` ([wiki.seeedstudio.com](https://wiki.seeedstudio.com/rebot_arm_b601_rs_lerobot/)).
  - Adapter l'interface `LeRobot` pour enregistrer des téléopérations de bras D-Bot et créer des jeux de données de démonstration d'actions.
- [ ] **Entraînement de Politiques de Manipulation Autonome :**
  - Configurer l'entraînement de politiques de comportement (*Diffusion Policy*, *ACT*) sur le Mac M1 Max pour les tâches de préhension.

---

### 📌 **Jalon 3 : Moteur Dynamique & Cinématique `Pinocchio` (INRIA/LAAS)**
- [ ] **Intégration de `Pinocchio` (Python/C++) :**
  - Installer `pinocchio` via Conda / PyPI sur le Mac et la Jetson.
  - Charger l'URDF complet de D-Bot dans Pinocchio pour calculer en **< 1 ms** la matrice de masse, la dynamique inverse et les jacobiens.
- [ ] **Compensation de Gravité Temps Réel :**
  - Implémenter le calcul de couple de gravité $G(q)$ en boucle ouverte/fermée et l'injecter via le terme $\tau_{ff}$ dans la commande MIT des 27 moteurs RobStride.

---

### 📌 **Jalon 4 : Tableau de Bord & Diagnostic Web UI (`Motorbridge` Web UI)**
- [ ] **Déploiement de l'Interface Web de Debug :**
  - Exécuter le serveur Web UI local (`rebot-devarm.w0x7ce.eu`) sur la Jetson ou le Mac.
  - Créer le **Tableau de Bord de Santé de D-Bot** : visualisation graphique en temps réel des températures, tensions, erreurs CAN et positions des 27 moteurs sans lancer ROS 2.

---

### 📌 **Jalon 5 : Modèles CAO 3D & Protection Mécanique des Câbles**
- [ ] **Inspection des Fichiers STEP sous Fusion 360 :**
  - Importer `reBot_B601_RS_v1.0_20260625.step` dans Fusion 360.
  - Vérifier les assemblages mécaniques des moteurs RobStride RS00 et RS06 (interfaces de fixation, ajustements H7, logements de roulements 6803ZZ).
- [ ] **Guidage & Anti-Fatigue des Câbles Articulés :**
  - Récupérer le fichier 3D `RS_Motor1_wiring_harness_clip.stp` (dossier `3D_Printed_Parts`).
  - Adapter ces clips de maintien imprimables (ABS) pour les connecteurs des moteurs de cou (RS-05) et de bras (RS-04/RS-00) de D-Bot afin d'éviter l'usure mécanique par flexion répétée.
- [ ] **Matrice de Décision Matériaux (Aluminium CNC vs ABS) :**
  - Valider le remplacement des pièces soumises à de forts couples (chevilles, genoux, hanches) par de l'Aluminium CNC 5052 selon les recommandations de Seeed.

---

### 📌 **Jalon 6 : Station d'Alimentation 48V 600W & Distribution XT30 2+2**
- [ ] **Fabrication de la Station d'Alimentation d'Atelier :**
  - Commander le bloc d'alimentation industriel **MeanWell LRS-600-48** (48V 12.5A 600W).
  - Imprimer les coques 3D avant/arrière du boîtier d'alimentation `RS-power-Top Cover.stp` et y intégrer la prise IEC 3-en-1 avec interrupteur.
- [ ] **Faisceau & Distributeurs XT30 2+2 :**
  - Fabriquer les câbles hybrides XT30 2+2 (48V + Bus CAN 1 Mbps) coudés et droits.
  - Intégrer les cartes de répartition **XT30 2+2 Power Splitter** dans le torse de D-Bot.

---

## 3. Matrice de Correspondance Globale des Composants

| Élement / Brique `reBot-DevArm` | Utilité Directe pour D-Bot V1 | Statut |
| :--- | :--- | :--- |
| **Hugging Face `LeRobot`** | Apprentissage par démonstration d'actions de manipulation | 🟩 À adapter |
| **Moteur Dynamique `Pinocchio`** | Compensation de gravité & IK < 1 ms sur 27 moteurs | 🟩 À intégrer |
| **SDK Python `Motorbridge`** | Driver de test & contrôle MIT pour RobStride RS-00 / RS-04 / RS-05 | 🟩 À tester |
| **`Motorbridge` Web UI** | Tableau de bord de diagnostic visuel des 27 moteurs CAN | 🟩 À déployer |
| **Boîtier Alimentation MeanWell 600W** | Station de charge et banc d'essai d'atelier 48V sécurisée | 🟩 À imprimer |
| **Clips câbles `RS_Motor1_...stp`** | Protection anti-fatigue des câbles CAN/48V du cou et des membres | 🟩 À réadapter |
| **Assemblage STEP B601 RS** | Référence CAO d'intégration mécanique des moteurs RobStride | 🟩 Disponible |
| **BOM Câblage XT30 2+2** | Standardisation des bus d'énergie et CAN en cascade dans le corps | 🟩 À confectionner |
