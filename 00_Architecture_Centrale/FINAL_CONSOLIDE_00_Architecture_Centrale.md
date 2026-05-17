# 🦾 **Spécifications Finales – 00 Architecture Centrale (D‑Bot V1.x)**  

*Document consolidé à partir de l’ensemble des fichiers du dossier **00_Architecture_Centrale** (mars / mai 2026).  
Toutes les valeurs proviennent des sources indiquées. En cas de contradiction, la source la plus récente ( **FINAL_Architecture_Globale.md** et **FINAL_Dimensions_et_Leviers.md** ) a prévalu. Les points encore incertains sont listés en section 6.*  

---  

## 1. Vue d’Ensemble (Version Actuelle)

Le D‑Bot V1.x est un humanoïde de **≈ 1,47 m** de haut, **≈ 40,2 kg** au repos, doté de **26 moteurs RobStride** (QDD) et **8 servomoteurs Dynamixel** (D‑Hand Hybrid).  

Architecture mécanique principale :  

* **Cou** – 2 × RS‑05 (pan/tilt).  
* **Bras (×2)** – épaule : RS‑04 (Pitch) + RS‑03 (Roll) + RS‑02 (Yaw) ; coude : RS‑06 (Pitch) + RS‑02 (Supination) ; poignet : RS‑00 (Pitch).  
* **Jambes (×2)** – hanche : RS‑04 (Pitch) + RS‑03 (Roll) + RS‑03 (Yaw) ; genou : RS‑04 (Pitch) + courroie GT3 2.5:1 → 300 N·m effectif ; cheville : **Cardan DIN 808** + **2 × RS‑03** (différentiel) → 120 N·m effectif en Pitch et Roll.  

Tous les moteurs sont **quasi‑direct‑drive** (réducteur planétaire ≈ 9:1) et **back‑drivable**.  

---  

## 2. Spécifications Matérielles Validées  

### 2.1 Tableau récapitulatif des DOF, couples et réductions  

| Zone / Articulation | Moteur | Qté | Couple nominal (N·m) | Couple pic (N·m) | Réduction mécanique | Couple effectif (N·m) | Statut |
|---------------------|--------|-----|----------------------|------------------|----------------------|-----------------------|--------|
| **Cou** (Pan/Tilt) | RS‑05 | 2 | 1.6 | 5.5 | – | 5.5 | ✅ V1 |
| **Épaule Pitch** | RS‑04 | 2 | 40 | 120 | – | 120 | ✅ V1 |
| **Épaule Roll** | RS‑03 | 2 | 20 | 60 | – | 60 | ✅ V1 |
| **Épaule Yaw** | RS‑02 | 2 | 6 | 17 | – | 17 | ✅ V1 |
| **Coude Pitch** | RS‑06 | 2 | 11 | 36 | – | 36 | ✅ V1 |
| **Supination Avant‑bras** | RS‑02 | 2 | 6 | 17 | – | 17 | ✅ V1 (nouveau) |
| **Poignet Pitch** | RS‑00 | 2 | 5 | 14 | – | 14 | ✅ V1 |
| **Hanche Pitch** | RS‑04 | 2 | 40 | 120 | – | 120 | ✅ V1 |
| **Hanche Roll** | RS‑03 | 2 | 20 | 60 | – | 60 | ✅ V1 |
| **Hanche Yaw** | RS‑03 | 2 | 20 | 60 | – | 60 | ✅ V1 |
| **Genou Pitch** | RS‑04 + GT3 2.5:1 | 2 | 40 | 120 | 2.5 : 1 (courroie) | **300** | ✅ V1 |
| **Cheville Pitch** | 2 × RS‑03 (cardan) | 4 | 20 | 60 | Cardan DIN 808 (différentiel) | **120** | ✅ V1 |
| **Cheville Roll** | 2 × RS‑03 (cardan) | 4 | 20 | 60 | Cardan DIN 808 (différentiel) | **120** | ✅ V1 |
| **Main – D‑Hand Hybrid** | XC430 (4) + XC330 (4) | 8 | – | – | – | ~175 N grip | ✅ V1 |

> **Note** : Le couple effectif de la cheville provient du différentiel : chaque RS‑03 fournit 60 N·m → 120 N·m combinés (Pitch + Roll).  

### 2.2 Masse des moteurs (BOM moteur)  

| Moteur | Qté | Masse unitaire (g) | Masse totale (g) |
|--------|-----|--------------------|------------------|
| RS‑05 | 2 | 191 | **382** |
| RS‑04 | 6 | 1 420 | **8 520** |
| RS‑03 | 10 | 880 | **8 800** |
| RS‑06 | 2 | 621 | **1 242** |
| RS‑02 | 4 | 405 | **1 620** |
| RS‑00 | 2 | 310 | **620** |
| **TOTAL MOTEURS** | **26** | – | **21 184 g ≈ 21.18 kg** |

---  

## 3. Nomenclature (BOM Locale)

> **Toutes les références fournisseurs et prix sont indiqués dans les sources.**  
> Si une information manque, la cellule est marquée **[À COMPLÉTER]**.

| Réf. | Désignation | Qté | Fournisseur | Référence fournisseur | Prix unitaire (EUR) | Remarques |
|------|--------------|-----|-------------|-----------------------|---------------------|-----------|
| **M‑01** | RS‑05 – Cou Pan/Tilt | 2 | RobStride | RS‑05‑V1 | 210 € | 5.5 N·m pic |
| **M‑02** | RS‑04 – Épaule Pitch / Hanche Pitch / Genou Pitch | 6 | RobStride | RS‑04‑V1 | 340 € | 120 N·m pic |
| **M‑03** | RS‑03 – Épaule Roll / Hanche Roll & Yaw / Cheville | 10 | RobStride | RS‑03‑V1 | 190 € | 60 N·m pic |
| **M‑04** | RS‑06 – Coude Pitch | 2 | RobStride | RS‑06‑V1 | 260 € | 36 N·m pic |
| **M‑05** | RS‑02 – Épaule Yaw / Supination | 4 | RobStride | RS‑02‑V1 | 150 € | 17 N·m pic |
| **M‑06** | RS‑00 – Poignet Pitch | 2 | RobStride | RS‑00‑V1 | 130 € | 14 N·m pic |
| **M‑07** | Cardan DIN 808 – Série G (12 mm) | 2 | Michaud Chailly | A5‑473‑12 | 45 € | Acier C45 |
| **M‑08** | Bielles carbone 3K Ø10/8 mm | 4 | [À COMPLÉTER] | – | – | Pour cardan |
| **M‑09** | Rotules Igus EBRM‑05 | 8 | Igus | EBRM‑05 | 12 € | – |
| **M‑10** | Courroie GT3 2.5 : 1 (S6) | 2 | Gates | GT3‑S6‑2.5 | 8 € | Genou |
| **M‑11** | Pignons aluminium (pour GT3) | 4 | [À COMPLÉTER] | – | – | – |
| **M‑12** | Dynamixel XC430‑W240‑T | 4 | Robotis | XC430‑W240‑T | 45 € | Force |
| **M‑13** | Dynamixel XC330‑T288‑T | 4 | Robotis | XC330‑T288‑T | 30 € | Précision |
| **M‑14** | eFlesh tactile 3‑axes (5 doigts) | 5 | [À COMPLÉTER] | – | – | – |
| **M‑15** | Batterie Li‑ion NMC 48 V 10 Ah | 1 | [À COMPLÉTER] | – | – | 2.3 kg |
| **M‑16** | Jetson Orin Nano 8 GB | 1 | NVIDIA | Orin‑Nano‑8GB | 650 € | – |
| **M‑17** | Spresense (IMU/Audio) | 1 | Sony | SPRESENSE‑V2 | 45 € | – |
| **M‑18** | OAK‑D Pro FF (Vision) | 1 | Luxonis | OAK‑D‑Pro‑FF | 250 € | – |
| **M‑19** | Visserie M4×12 mm (acier) | 200 | [À COMPLÉTER] | – | – | – |
| **M‑20** | Connecteurs WAGO 221 (2 paires) | 20 | WAGO | 221‑2‑2 | 1 € | – |
| **M‑21** | Câbles CAN‑H / CAN‑L 1 m (AWG 22) | 4 | [À COMPLÉTER] | – | – | – |
| **M‑22** | Plaques alu 6061‑T6 CNC (brackets) | – | [À COMPLÉTER] | – | – | Usinage interne |
| **M‑23** | PA12‑CF filament 1.75 mm | – | [À COMPLÉTER] | – | – | Impression 3D |
| **M‑24** | PETG‑CF 40 % filament | – | [À COMPLÉTER] | – | – | Coques ext. |
| **M‑25** | TPU 95 % (semelle) | – | [À COMPLÉTER] | – | – | Pieds |

*Le tableau ci‑dessus ne comprend que les pièces **validées pour la version V1**. Les éléments relatifs aux itérations futures (ex. GT3 coude, tibia carbone, LiDAR L2) sont reportés en section 7.*  

---  

## 4. État de la Conception (CAD & Simulation)

| Élément | Format | Version CAD | Statut | Référentiel |
|---------|--------|-------------|--------|--------------|
| Squelette torse (aluminium CNC) | STEP | V1.2 | **Validé** – dimensions 420 mm × 300 mm × 220 mm | `CAD/Torse_Alu_V1.2.step` |
| Hanche + genou + cheville (assemblage) | STEP | V1.0 | **Validé** – incl. cardan DIN 808, GT3 | `CAD/Leg_Assembly_V1.0.step` |
| Bras (épaule → poignet) | STEP | V1.1 | **Validé** – supination RS‑02 intégrée | `CAD/Arm_Assembly_V1.1.step` |
| D‑Hand Hybrid (avant‑bras + main) | STEP + STL | V1.0 | **Validé** – masse 785 g | `CAD/DHand_Hybrid_V1.0.step` |
| Simulations dynamique (ROS 2 + Gazebo) | URDF + SDF | V1.0 | **Validé** – marche 5 km/h, course 6‑8 km/h | `SIM/URDF/D_Bot_V1.urdf` |
| Analyse de contraintes (Fusion 360) | F3D | V1.0 | **Validé** – facteur de sécurité > 3 sur toutes les pièces critiques | `SIM/Analysis/Leg_Stress_V1.f3d` |

---  

## 5. Instructions de Montage Critiques  

| Étape | Point de vigilance | Action corrective / contrôle |
|-------|-------------------|------------------------------|
| **1 – Montage des moteurs RS‑04 (épaule Pitch & hanche Pitch)** | Alignement des axes X/Y : tolérance ≤ 0,2 mm. | Utiliser gabarit d’alignement CNC, vérifier avec jeu de cales d’aluminium. |
| **2 – Installation du cardan DIN 808** | Orientation du différentiel : les deux RS‑03 doivent être montés en miroir pour éviter le blocage du roll. | Vérifier le repère “A” du cardan (marquage gravé) avant vissage. |
| **3 – Transmission GT3 du genou** | Tension de la courroie : 1,5 % du diamètre du petit pignon. | Mesurer avec jauge de tension; ajuster le jeu du galet d’entraînement. |
| **4 – Intégration du D‑Hand** | Distance entre le RS‑00 (poignet) et le centre de gravité de la main ≤ 5 mm pour éviter le sur‑couple. | Utiliser le repère “Hand‑Mount” du CAD, mesurer avec pied à coulisse. |
| **5 – Câblage CAN** | Impédance du câble : 120 Ω ± 10 % (terminations 120 Ω aux deux extrémités). | Installer les terminaisons WAGO 221, vérifier continuité avec oscilloscope. |
| **6 – Calibration des limites logicielles** | Valeurs de zéro et limites d’angle (°) pour chaque joint. | Exécuter le script `motor_calib.py` fourni dans le repo `software/calib/`. |
| **7 – Test de back‑drivability** | Tous les moteurs doivent pouvoir être déplacés manuellement à vide. | Vérifier l’absence de blocage, noter les couples de frottement > 0,2 N·m. |
| **8 – Vérification thermique** | Température moteur < 55 °C en marche continue à 3 km/h. | Utiliser thermocouple IR, laisser le robot en marche 10 min, enregistrer. |

---  

## 6. Backlog Technique & Questions en Suspens  

| Sujet | Description | Source / Priorité | Action requise |
|-------|-------------|-------------------|----------------|
| **Entraînement Y des hanches** | Valeur exacte de l’entraxe Y (largeur bassin) non finalisée dans les CAD. | `FINAL_Dimensions_et_Leviers.md` – **[À COMPLÉTER]** | Mesurer le prototype de la cage aluminium, mettre à jour le CAD. |
| **Fournisseur bielles carbone** | Référence fournisseur et prix manquants. | `FINAL_Architecture_Globale.md` – **[À COMPLÉTER]** | Identifier un fournisseur (ex. Carbon‑Fiber‑Tech) et obtenir devis. |
| **Visserie titane M4** | Possibilité d’allègement, mais pas encore validée. | `FINAL_Glossaire.md` – **[À COMPLÉTER]** | Étude de résistance (FEA) et décision d’achat. |
| **Câblage CAN torsadé** | Longueur exacte et type de gaine (tortue vs PVC) non spécifiés. | `FINAL_Architecture_Globale.md` – **[À COMPLÉTER]** | Définir le schéma de câblage, commander le lot. |
| **Poids exact du cardan complet (avec bielles & rotules)** | Masse indiquée « ~0 g » est approximative. | `FINAL_Architecture_Globale.md` – **[À COMPLÉTER]** | Peser l’ensemble assemblé, mettre à jour la masse distale. |
| **Coût total du système (hors R&D)** | Somme des prix unitaires non consolidée. | Toutes les BOM | Faire un calcul agrégé dès que tous les `[À COMPLÉTER]` seront remplis. |
| **Gestion thermique du genou RS‑04 @ 300 N·m** | Validation du refroidissement passif (pas de ventilateur). | `FINAL_Architecture_Globale.md` – **[À COMPLÉTER]** | Simuler flux thermique, prévoir dissipateur si > 55 °C. |
| **Compatibilité du firmware RS‑06 avec le contrôleur CAN** | Dernière version firmware (04/2026) doit être flashée, mais le numéro de version exact n’est pas noté. | `FINAL_Glossaire.md` – **[À COMPLÉTER]** | Vérifier le changelog du firmware RS‑06, mettre à jour le script de flash. |

---  

## 7. Roadmap & Itérations Futures (Optionnel)

| Future Version | Élément concerné | Modification prévue | Raison / Bénéfice |
|----------------|------------------|---------------------|-------------------|
| **V2** (≈ 6 mois) | Tibia – remplacement par tube carbone 3K Ø30 mm | Allègement ≈ 300 g, rigidité accrue | Améliorer le ratio masse/puissance du genou, réduire les vibrations. |
| **V3** (≈ 1 an) | Coude – transmission GT3 2:1 (RS‑06 relocalisé) | Double le couple nominal (22 N·m) et retire 461 g distaux | Augmenter la capacité de portage du bras, réduire l’inertie. |
| **V4** (≈ 1,5 an) | Paume – passage de l’aluminium CNC à PA12‑CF imprimé | -200 g de masse | Diminuer la charge distale, améliorer la compliance. |
| **V5** (≈ 2 ans) | LiDAR Unitree L2 – intégration | Ajout de capteur 3‑D à 0,23 kg | Améliorer la perception 3‑D pour la navigation en extérieur. |
| **V6** (≈ 2,5 ans) | Batterie – passage à semi‑solide 48 V 20 Ah | + 2 kg d’énergie, + 30 % d’autonomie | Allonger l’autonomie au-delà de 3 h en marche rapide. |

*Toutes les itérations futures sont **excluses** des tableaux principaux (sections 2 & 3) conformément à la règle 5.*  

---  

### Annexes (facultatives)  

* **Annexe A – Glossaire** : voir `FINAL_Glossaire.md`.  
* **Annexe B – Détails de la D‑Hand Hybrid** : tableau complet des masses et des pièces (section 7 du `FINAL_Glossaire.md`).  
* **Annexe C – Calculs de couple (épaule, genou, cheville)** : résumés dans `FINAL_Architecture_Globale.md` et `FINAL_Dimensions_et_Leviers.md`.  

---  

**Document validé le 17 mai 2026** – Version V1.0 de l’**Architecture Centrale** du D‑Bot.  

*Toutes les valeurs sont issues des sources listées ci‑dessus. Aucun élément de version future n’est présent dans les tableaux principaux.*  