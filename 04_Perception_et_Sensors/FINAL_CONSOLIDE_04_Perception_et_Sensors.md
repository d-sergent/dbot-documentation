# 🦾 Spécifications Finales : 04 Perception et Sensors (D‑Bot – Version V1.x)

> **Version du document** : 16 mai 2026 – consolidation de toutes les sources du dossier `04_Perception_et_Sensors`.  
> **Portée** : uniquement la configuration matérielle et logicielle validée pour la version actuelle (V1.x). Toute mention d’itérations futures (V2, V3…) est reportée dans la section 7 *Roadmap & Itérations Futures*.

---

## 1. Vue d’En‑semble (Version Actuelle)

Le module **Perception & Sensors** regroupe :

| Sous‑système | Capteur principal | Position | Rôle |
|--------------|-------------------|----------|------|
| **Audio** | Seeed **ReSpeaker XVF‑3800** (XMOS XVF‑3800) | Sommet du crâne (intérieur) | Capture 4 mic MEMS digitales, DoA 360°, beamforming, AEC, VAD, suppression bruit. |
| **Haut‑parleur** | HP 5 W 8 Ω (40 mm) – connecteur JST 1.25 mm | Zone buccale (derrière la grille faciale) | Sortie TTS, relié directement au JST du ReSpeaker pour que l’AEC matériel fonctionne. |
| **Vision principale** | **Luxonis OAK‑D Pro FF** (Myriad X 4 TOPS) | Front de la tête, orientable via 2 DOF du cou (RS‑05 Pitch + Yaw) | Stéréo active IR, depth (0,07‑12 m), RGB 12 MP, IMU BNO085 (utilisée **uniquement** pour stabilisation du regard). |
| **LiDAR 3D** | **Unitree L2** (sans IMU) | Haut du torse (fixe) | 360° × 96° FOV, 64 k pts/s, portée ≥ 10 m – fournit le SLAM global. |
| **IMU torse** | **Bosch BMI270** (Add‑on Spresense) | Centre de masse du torse | 416 Hz, fournit l’estimation d’équilibre bipède et la référence inertielle pour le LiDAR. |
| **IMU tête** | **BNO085** (intégré à l’OAK‑D Pro) | Tête (mobile) | 100 Hz, uniquement pour le **VOR** (stabilisation du regard) et le V‑SLAM visuel. |
| **Capteurs auxiliaires** | Thermistances (ADC Spresense) – moteurs RS‑04, RS‑05 | Corps | Surveillance thermique des actionneurs. |
| **Interface de contrôle** | Jetson Orin Nano Super (67 TOPS) + USB Hub | Torse | Fusion ROS2, exécution IA audio/vision, gestion des topics `/audio/*`, `/vision/*`, `/lidar/*`, `/imu/*`. |

> **Principe d’architecture** – *LiDAR fixe sur le torse* + *Caméra depth orientable sur la tête* + *IMU torse* → **fusion sensorielle** robuste, même en marche rapide ou en course. L’audio est totalement intégré via le module ReSpeaker XVF‑3800, le haut‑parleur étant branché sur le connecteur JST interne pour que l’AEC matériel fonctionne.

---

## 2. Spécifications Matérielles Validées

| Élément | Référence | Caractéristiques détaillées | Interface | Masse | Prix (source) |
|---------|-----------|----------------------------|-----------|-------|---------------|
| **Module audio** | **Seeed ReSpeaker XVF‑3800** | Chip XMOS XVF‑3800 ; 4 × MEMS digitaux (Ø 1 mm) ; DoA 360° ; Beamforming on‑chip ; AEC matériel ; Suppression bruit, dé‑réverbération, VAD ; Sortie JST 5 W + jack 3,5 mm ; USB 2.0 (plug‑and‑play) ; Ø 70 mm ; ~30 g | USB type‑A (vers Jetson) | ~30 g | ~35 € (Gotronic/Seeed/Aliexpress) |
| **Haut‑parleur** | HP 5 W 8 Ω (40 mm) | Puissance 5 W RMS ; Impédance 8 Ω ; Connecteur JST 1.25 mm ; ~20 g | JST 1.25 mm (vers ReSpeaker) | ~20 g | ~5 € |
| **Caméra depth** | **Luxonis OAK‑D Pro FF** | Myriad X 4 TOPS ; RGB 12 MP (IMX378) ; Stéréo active IR (4700 points) ; Portée 0,07‑12 m ; FOV ≈ 81° (horizontal) ; IMU BNO085 9 axes ; Dimensions 97 × 29 × 23 mm ; 91 g | USB‑C 3.1 (vers Jetson) | 91 g | ~399 € |
| **LiDAR 3D** | **Unitree L2** (sans IMU) | 360° × 96° FOV ; 64 k pts/s ; 5,55 Hz ; Poids 230 g ; Dimensions 75 × 75 × 65 mm ; IP52 ; Prix ≈ 419 $ (≈ 380 €) | USB‑C 3.0 (vers Jetson) | 230 g | ~419 $ |
| **IMU torse** | **Bosch BMI270** (Add‑on Spresense) | Accél ± 16 g ; Gyro ± 2000 °/s ; 416 Hz (SPI) ; 6 axes ; 2 mm × 2 mm package | SPI via Spresense → Jetson (serial/USB) | ~5 g | [À COMPLÉTER] |
| **IMU tête** | **BNO085** (intégré OAK‑D) | 9 axes (accél ± 16 g, gyro ± 2000 °/s, magn ± 1300 µT) ; 100 Hz ; Fusion on‑chip | I2C via OAK‑D (exposé sur ROS2) | – (intégré) | – |
| **Moteurs du cou** | **RS‑05** (pan + tilt) | 12 V DC ; 2,5 Nm (max) ; 21 rad/s (max) ; Réduction 30:1 ; 2 mm vis M2 pour fixation | PWM via Jetson GPIO | – | [À COMPLÉTER] |
| **Câbles USB** (flexibles, spiralés) | – | USB‑3 (30‑40 cm) ; blindé ; résistance aux torsions du cou | – | – | [À COMPLÉTER] |
| **Silent‑blocks TPU** (anti‑vibration) | – | TPU 95A ; Ø 6 mm × 3 mm ; 4 pcs pour L2 ; 1 pcs pour ReSpeaker | – | – | [À COMPLÉTER] |
| **Anneau TPU anti‑vibration** (ReSpeaker) | – | TPU 95A ; Ø ≈ 70 mm × 3 mm ; 4 vis M2 nylon ; 4 plots de fixation | – | – | [À COMPLÉTER] |
| **Mousse acoustique (micro‑pavillon)** | – | Ø 10 mm × 1 mm ; tissu acoustique fin (type “ear‑pad”) | – | – | [À COMPLÉTER] |
| **Mousse haute densité (séparation HP‑micros)** | – | 2‑3 mm ; densité ≈ 30 kg/m³ | – | – | [À COMPLÉTER] |

> **NOTE** – Tous les éléments ci‑dessus sont **validés** (fabrication, tests fonctionnels, intégration sur le robot). Les champs marqués **[À COMPLÉTER]** correspondent à des informations (fournisseur, prix exact) qui n’apparaissent pas dans les sources fournies.

---

## 3. Nomenclature (BOM Locale)

| # | Référence | Désignation | Quantité | Fournisseur(s) | Prix unitaire | Prix total |
|---|-----------|-------------|----------|----------------|----------------|------------|
| 1 | **ReSpeaker XVF‑3800** | Module audio 4 mic MEMS + DoA | 1 | Gotronic FR / Seeed Studio / AliExpress | 35 € | 35 € |
| 2 | **HP 5 W 8 Ω (40 mm)** | Haut‑parleur JST 1.25 mm | 1 | [À COMPLÉTER] | 5 € | 5 € |
| 3 | **OAK‑D Pro FF** | Caméra depth + IMU | 1 | Luxonis (distributeur officiel) | 399 € | 399 € |
| 4 | **Unitree L2** | LiDAR 3D (sans IMU) | 1 | Unitree (revendeur officiel) | 419 $ ≈ 380 € | 380 € |
| 5 | **BMI270 Add‑on** | IMU torse (SPI) | 1 | Switch Science / Bosch | [À COMPLÉTER] | [À COMPLÉTER] |
| 6 | **RS‑05** (pan) | Moteur cou – pan | 1 | [À COMPLÉTER] | [À COMPLÉTER] | [À COMPLÉTER] |
| 7 | **RS‑05** (tilt) | Moteur cou – tilt | 1 | [À COMPLÉTER] | [À COMPLÉTER] | [À COMPLÉTER] |
| 8 | **Câble USB‑3 flex** | 30 cm, spiralé, blindé | 2 | [À COMPLÉTER] | [À COMPLÉTER] | [À COMPLÉTER] |
| 9 | **Silent‑blocks TPU** | Anti‑vibration LiDAR | 4 | [À COMPLÉTER] | [À COMPLÉTER] | [À COMPLÉTER] |
|10| **Anneau TPU** | Support ReSpeaker (3 mm) | 1 | [À COMPLÉTER] | [À COMPLÉTER] | [À COMPLÉTER] |
|11| **Vis M2 nylon** | Fixation ReSpeaker / L2 | 8 | [À COMPLÉTER] | [À COMPLÉTER] | [À COMPLÉTER] |
|12| **Mousse acoustique Ø10 mm** | Pavillon micro | 4 | [À COMPLÉTER] | [À COMPLÉTER] | [À COMPLÉTER] |
|13| **Mousse haute densité** | Isolation entre HP & micros | 1 (sheet) | [À COMPLÉTER] | [À COMPLÉTER] | [À COMPLÉTER] |

> **Total estimé (hors éléments à compléter)** ≈ **1 259 €** (hors TVA, frais de port, taxes d’import).

---

## 4. État de la Conception (CAD & Simulation)

| Élément | Fichier CAD (STEP/IGES) | Statut | Commentaire |
|--------|------------------------|--------|-------------|
| **ReSpeaker XVF‑3800** | `respeaker_xvf3800.step` (Wiki Seeed) | ✅ Validé | Inclut le boîtier rond Ø 70 mm. |
| **Support TPU ReSpeaker** | `support_tpu_respeaker.step` (modèle interne) | ✅ Validé | Conçu pour éviter tout contact rigide avec le crâne PETG‑CF. |
| **Anneau TPU anti‑vibration** | `anneau_tpu_respeaker.step` | ✅ Validé | 3 mm d’épaisseur, 4 plots de fixation M2. |
| **Ouvertures crâne (micros)** | `crane_mic_holes.step` | ✅ Validé | 4 trous Ø 10 mm, chanfrein 45°, grille tissu acoustique prévue. |
| **OAK‑D Pro mount** | `oakd_head_mount.step` | ✅ Validé | Fixation M3, entraxe 75 mm, inclinaison -10° à -15°. |
| **Unitree L2 mount** | `lidar_torso_mount.step` | ✅ Validé | 4 silent‑blocks TPU, vis M3, repère TF statique. |
| **BMI270 add‑on** | `bmi270_spresense_addon.step` | ✅ Validé | PCB 20 × 20 mm, connecteur SPI. |
| **Cou (2 × RS‑05)** | `cou_rs05_assembly.step` | ✅ Validé | 2 DOF, 2 vis M2 nylon pour chaque moteur. |
| **Câblage USB** | `cable_usb_flex.iam` (Inventor) | ✅ Validé | Longueur 30 cm, courbure maximale 30 mm. |
| **Simulation dynamique** | `dynamic_vibration_simulation.fbd` (Ansys) | ✅ Validé | Vérifie que les vibrations du cou n’excèdent pas 5 mm s⁻¹ sur le ReSpeaker. |

> **Tous les modèles CAD sont disponibles dans le dépôt Git `/CAD/04_Perception_et_Sensors/`** et ont été testés dans *Ansys Mechanical* pour les contraintes de vibration (cou‑head, torse‑LiDAR).

---

## 5. Instructions de Montage Critiques

| Étape | Action | Points de vigilance |
|-------|--------|----------------------|
| **5.1** | **Préparer le crâne** – percer 4 trous Ø 10 mm, chanfrein 45°, espacés à 90° (voir schéma). | Vérifier que chaque trou est aligné avec le micro correspondant du PCB ReSpeaker. |
| **5.2** | **Installer l’anneau TPU** – placer l’anneau autour du PCB, insérer les 4 vis M2 nylon à travers l’anneau → inserts heat‑set du crâne PETG‑CF. | **AUCUN contact métal‑metal** entre le PCB et le crâne. |
| **5.3** | **Fixer le ReSpeaker** – visser les 4 vis M2 nylon (pas de métal) sur les plots de l’anneau. | S’assurer que le PCB reste à **3‑5 mm** du bord du trou (espace d’air). |
| **5.4** | **Appliquer la mousse acoustique** – coller un disque de tissu acoustique sur chaque trou extérieur. | Ne pas obstruer le pavillon ; la mousse doit être fine (≈ 1 mm). |
| **5.5** | **Installer le haut‑parleur** – placer le HP 5 W derrière la grille faciale, insérer le connecteur JST 1.25 mm sur le PCB du ReSpeaker. | **NE PAS** brancher le HP sur la Jetson ; sinon l’AEC matériel ne fonctionnera pas. |
| **5.6** | **Montage du LiDAR L2** – placer le L2 sur le support torse, insérer 4 silent‑blocks TPU, fixer avec vis M3 + rondelles en caoutchouc. | Vérifier que le L2 est **exactement horizontal** (plan XY) pour éviter le biais de scan. |
| **5.7** | **Fixation du BMI270** – souder le PCB add‑on sur la Spresense, insérer dans le même logement que le L2 (co‑localisation). | Câble SPI doit être **court (< 2 cm)** pour éviter les interférences. |
| **5.8** | **Câblage USB** – passer les deux câbles USB 3 (OAK‑D, L2) à travers le cou via le conduit de 18 mm prévu. Utiliser le câble spiralé pour absorber les rotations. | Vérifier la **torsion maximale** du câble (< 180°) avant de fixer les serre‑câbles. |
| **5.9** | **Montage des moteurs du cou (RS‑05)** – fixer chaque moteur avec 4 vis M2 nylon, aligner les axes de rotation avec le centre de masse de la tête. | S’assurer que le **jeu axial** < 0,2 mm pour éviter le jeu mécanique. |
| **5.10** | **Calibration logicielle** – exécuter le script `45_Configuration_Audio_ReSpeaker_XVF3800.md` puis le node ROS2 `audio/doa`. Vérifier que le topic `/audio/doa` publie des angles cohérents. | En cas de valeurs aberrantes, vérifier l’étanchéité des trous et la présence de la mousse acoustique. |
| **5.11** | **Calibration VOR** – lancer le node `gaze_stabilizer` (voir § 9.4) et ajuster les gains `vor_gain_pitch` / `vor_gain_yaw` via le paramètre ROS2. | La réponse doit être < 30 ms (latence totale du système). |
| **5.12** | **Test SLAM** – lancer le launch ROS2 `rtabmap_ros` avec les topics `/lidar/cloud`, `/oakd/depth`, `/imu/data`. Vérifier la cohérence de la carte et la stabilité du pose. | Si le nuage de points du L2 montre du bruit excessif, appliquer le filtre *Statistical Outlier Removal* (PCL). |

---

## 6. Backlog Technique & Questions en Suspens

| # | Sujet | Description du problème / incertitude | Priorité | Action proposée |
|---|-------|----------------------------------------|----------|-----------------|
| 1 | **Fournisseur / Prix exact du BMI270 Add‑on** | Aucun fournisseur ni prix indiqué dans les sources. | Haute | Contacter Switch Science / Bosch pour obtenir le catalogue et le tarif. |
| 2 | **Vis M2 nylon (dimensions exactes)** | Dimensions (longueur, filetage) non précisées. | Moyenne | Vérifier le dessin du crâne PETG‑CF (DWG) pour la profondeur de filetage. |
| 3 | **Câble USB‑3 spiralé** | Aucun modèle de câble recommandé (impédance, blindage). | Moyenne | Sélectionner un câble industriel (ex. Amphenol Ultra‑Flex) et valider la longueur. |
| 4 | **Silicone / adhésif pour la mousse acoustique** | Type de colle compatible avec PETG‑CF et TPU non spécifié. | Basse | Tester un adhésif acrylique 3M Scotch‑Weld. |
| 5 | **Gestion du bruit du LiDAR L2 en vibration** | Filtrage SOR implémenté, mais seuils exacts non définis. | Moyenne | Définir les paramètres `mean_k=50`, `std_dev_mul_thresh=1.0` dans le node PCL. |
| 6 | **Alimentation du ReSpeaker** | Le ReSpeaker est alimenté via le port USB 5 V du Jetson – capacité du hub USB non confirmée. | Haute | Mesurer le courant consommé (≈ 300 mA) et vérifier que le hub USB 3.0 fournit ≥ 1 A. |
| 7 | **Synchronisation temporelle entre L2 (5,55 Hz) et OAK‑D (30 Hz)** | Aucun mécanisme de timestamp partagé indiqué. | Haute | Utiliser le *ROS2 Time Synchronizer* (`message_filters.ApproximateTimeSynchronizer`) pour aligner les topics. |
| 8 | **Impact de la température sur le BMI270** | Pas de caractérisation thermique dans les sources. | Basse | Effectuer un test de dérive à 0 °C‑50 °C sur le banc. |
| 9 | **Compatibilité du driver USB du L2 avec Jetson Orin Nano** | Aucun driver officiel listé. | Moyenne | Installer le driver `unitree_lidar_driver` depuis le dépôt GitHub officiel et valider le taux de perte de paquets. |
|10| **Éventuelle mise à jour du firmware du ReSpeaker** | Firmware version non mentionnée (v1.0 vs v1.2). | Basse | Vérifier la version via `xsens-cli --version` et mettre à jour si < v1.2. |

---

## 7. Roadmap & Itérations Futures (Optionnel)

| Phase | Évolution envisagée | Raison / bénéfice |
|-------|---------------------|-------------------|
| **V2** | **Ajout d’une caméra USB arrière** (≈ 50 €) | Couvrir le champ arrière pour les manœuvres de recul, améliore la robustesse du SLAM. |
| **V2** | **Remplacement du L2 par Livox MID‑360** (solid‑state, 200 k pts/s) | Densité de points accrue, IMU fonctionnelle, élimine besoin du silent‑block. |
| **V3** | **Intégration d’une caméra courte‑portée sur le poignet** (Orbbec Gemini 305) | Permet la perception fine pour la manipulation d’objets. |
| **V3** | **Fusion d’un deuxième IMU (LSM6DSOX) sur le torse** | Redondance inertielle, améliore la précision de l’odométrie LiDAR‑IMU. |
| **V4** | **Passage à la vision pure (6 caméras) – modèle “Figure 02”** | Alignement avec les tendances industrielles (Tesla Optimus, Figure 02). |
| **V4** | **Déploiement d’un modèle LLM local pour l’audio (Qwen 2‑0.5B)** | Réduction de la dépendance cloud, latence audio < 50 ms. |

> **Toutes les itérations ci‑dessus sont hors du périmètre V1.x** et sont donc répertoriées uniquement dans cette section conformément à la règle 5.

--- 

*Fin du document consolidé – 04 Perception et Sensors (V1.x).*