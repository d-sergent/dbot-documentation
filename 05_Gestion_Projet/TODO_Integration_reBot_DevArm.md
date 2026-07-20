# 📝 TODO — EXPLOITATION DU DÉPÔT `reBot-DevArm` (ÉCOSYSTÈME ROBOSTRIDE)
**Plan d'Action Technique pour Réexploiter les Drivers, les Modèles CAO 3D et le Câblage RobStride sur D-Bot**

---

## 1. Contexte & Objectif

Le dépôt local `/Users/Shared/Mon Google Drive Physique/reBot-DevArm` (développé par Seeed Studio pour le bras 6 axes *reBot Arm B601 RS*) utilise exactement le même écosystème de motorisation que D-Bot : **moteurs brushless RobStride (RS00 / RS06), bus CAN 1 Mbps, et alimentation 48V**.

L'objectif de cette TODO est de réexploiter directement le code, les bibliothèques Python, les modèles 3D STEP et les solutions de câblage de ce dépôt pour accélérer le développement de D-Bot.

---

## 2. Feuille de Route Opérationnelle (4 Jalons)

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

### 📌 **Jalon 2 : Modèles CAO 3D & Protection Mécanique des Câbles**
- [ ] **Inspection des Fichiers STEP sous Fusion 360 :**
  - Importer `reBot_B601_RS_v1.0_20260625.step` dans Fusion 360.
  - Vérifier les assemblages mécaniques des moteurs RobStride RS00 et RS06 (interfaces de fixation, ajustements H7, logements de roulements 6803ZZ).
- [ ] **Guidage & Anti-Fatigue des Câbles Articulés :**
  - Récupérer le fichier 3D `RS_Motor1_wiring_harness_clip.stp` (dossier `3D_Printed_Parts`).
  - Adapter ces clips de maintien imprimables (ABS) pour les connecteurs des moteurs de cou (RS-05) et de bras (RS-04/RS-00) de D-Bot afin d'éviter l'usure mécanique par flexion répété.

---

### 📌 **Jalon 3 : Distribution Électrique & Connectique Hybride XT30 2+2**
- [ ] **Schéma du Répartiteur Alimentation / CAN :**
  - Analyser l'architecture du module **XT30 2+2 Power Splitter** (carte de distribution regroupant la ligne 48V et le bus CAN 1 Mbps).
  - Évaluer la fabrication des câbles hybrides XT30 2+2 coudés (longueurs 200mm et 320mm) pour le torse et les membres de D-Bot.

---

### 📌 **Jalon 4 : Banc de Test Web UI pour le Debug Terrain**
- [ ] **Déploiement de l'Interface de Debug Web :**
  - Cloner ou exécuter le serveur Web UI local (`rebot-devarm.w0x7ce.eu`) sur la Jetson Orin Nano.
  - Permettre le test unitaire et le diagnostic immédiat de n'importe quel moteur RobStride branché sur le bus CAN sans avoir à lancer l'architecture ROS 2 complète.

---

## 3. Matrice de Correspondance des Composants

| Composant `reBot-DevArm` | Utilité Directe pour D-Bot V1 | Statut |
| :--- | :--- | :--- |
| **SDK Python Motorbridge** | Driver de test & contrôle MIT pour RobStride RS-00 / RS-04 / RS-05 | 🟩 À tester |
| **Clips câbles `RS_Motor1_...stp`** | Protection anti-fatigue des câbles CAN/48V du cou et des membres | 🟩 À réadapter |
| **Assemblage STEP B601 RS** | Référence CAO d'intégration mécanique des moteurs RobStride | 🟩 Disponible |
| **BOM Câblage XT30 2+2** | Standardisation des bus d'énergie et CAN en cascade dans le corps | 🟩 À étudier |
