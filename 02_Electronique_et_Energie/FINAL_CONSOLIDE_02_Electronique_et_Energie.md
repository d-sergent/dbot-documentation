# 🦾 Spécifications Finales – 02 Électronique et Énergie (D‑Bot V1.x)

> **Version du document :** V1.0 – 16 mai 2026  
> **Portée :** Toutes les pièces, sous‑systèmes d’alimentation, de distribution, de conversion, de communication et de capteurs associés au module 02 Électronique & Énergie du robot humanoïde D‑Bot (40 kg).  
> **Sources principales :** `FINAL_Bilan_Tensions.md`, `STUDY_Electronique_Historique.md`, `STUDY_Motorisation_QDD_RobStride.md`, `STUDY_Watchdog_Robot.md`.  
> **Conformité :** Toutes les valeurs proviennent d’une source datée ou d’un résultat de test réel. En cas d’ambiguïté, la donnée la plus récente a été retenue ; les points non résolus sont listés dans la section 6.

---

## 1. Vue d’Ensemble (Version Actuelle)

L’architecture électrique du D‑Bot repose sur :

* **Source principale** : batterie Li‑ion NMC 13 S ≈ 48 V (46,8 V nominal, 54,6 V max).  
* **Distribution** : bus‑bar central (torse) à 48 V, alimentant **six zones** (bras G/D, jambe G/D, cou/tête, logique).  
* **Conversion** : quatre rails de tension secondaire dérivés du 48 V via des convertisseurs buck isolés : 19 V (Jetson), 12 V Logique (10 A), 12 V Puissance (20 A) et 5 V (Always‑On).  
* **Communication** : CAN 2.0 B @ 1 Mbps (RobStride) via cinq adaptateurs USB‑CAN (1 × InnoMaker, 4 × CANable Pro) et un hub USB 3.0 industriel (10 ports).  
* **Supervision** : Sony Spresense « Always‑On » (watchdog, lecture ADC, IMU BMI270).  

---

## 2. Spécifications Matérielles Validées

| Élément | Référence | Tension d’alimentation | Courant max (typ.) | Fonction | Remarques |
|---|---|---|---|---|---|
| **Batterie principale** | 13 S Li‑ion NMC (VAE 48 V) – 10 Ah, BMS 30 A continu (≥ 50 A pic) | 46,8 V nom. (54,6 V max) | 30 A continu / 50 A pic | Source d’énergie principale | Voir §4.2 |
| **Fusible principal** | Fusible automobile 80 A (type ANL/MIDI) | – | 80 A | Protection ligne 48 V | Coupure E‑Stop ne coupe pas la Jetson |
| **Bus‑bar central** | Bus‑bar laiton étamé 8 bornes (double) | 48 V | 80 A total | Point de distribution central | [À COMPLÉTER] fabricant exact |
| **Convertisseur 48 V → 19 V** | Buck isolé, 48 → 19 V, 5 A, 95 W | 48 V | 5 A | Alimente Jetson Orin Nano Super | Modèle exact non indiqué – à préciser |
| **Convertisseur 48 V → 12 V Logique** | Buck 60 V in / 12 V out, 10 A (type Mean Well DDR‑120C‑12 ou Homelylife) | 48 V | 10 A | Hub USB Industriel, solénoïdes tête | Fournisseur à confirmer |
| **Convertisseur 48 V → 12 V Puissance** | Buck 60 V in / 12 V out, 20 A (ou DROK 25A par bras) | 48 V | 20 A | 16 × Feetech (STS3250/HL-3915) | Fournisseur à confirmer |
| **Convertisseur 48 V → 5 V** | Buck isolé, 5 A, 25 W | 48 V | 5 A | Spresense, hub USB, accessoires | Fournisseur à confirmer |
| **Hub USB 3.0 Industriel (10 ports)** | StarTech ST103008U2C ou Sabrent HB‑BU10 (aluminium, alimentation 7‑24 V) | 12 V (alimenté par rail 12 V Logique) | 10 A total (≈ 1 A/port) | Centralise les périphériques USB | Modèle exact à valider |
| **Adaptateur CAN USB InnoMaker** | InnoMaker USB2CAN‑C (isolé 2.5 kV) | 48 V bus | – | Bus Cou (2 × RS‑05) | Acheté, firmware candleLight |
| **Adaptateur CANable Pro × 4** | CANable Pro (isolé 2.5 kV, PCB 45 × 16 mm) | 48 V bus | – | Bus Bras G/D, Jambe G/D | Achetés, firmware candleLight |
| **Module de debug CAN** | Interface opto‑couplée (isolée) | 48 V bus | – | Configuration ID moteurs, firmware | Acheté |
| **Module Dual MOSFET D4184** | Driver MOSFET D4184 (2 × N‑channel) | 12 V (rail 12 V Logique) | 2 × 0,6 A (solénoïdes) | Pilotage solénoïdes tête | Diodes 1N4007 à souder en parallèle |
| **Solénoïdes tête** | LEX‑SOLEN‑04, 12 V, 0,6 A chacun | 12 V | 0,6 A | Blocage/déblocage tête | 2 unités |
| **Sony Spresense Standard Board** | CXD5602PWBEXT1, 6 ADC, 3,3 V I/O | 5 V (Always‑On) | 1 A (typ.) | Watchdog, lecture FSR, IMU, UART | Achetée |
| **IMU BMI270** | SparkFun BMI270 Breakout (SEN‑22397) | 3,3 V (via Spresense) | – | Équilibre bipède (416 Hz) | Connecté I2C Qwiic |
| **Feetech STS3250 / HL-3915** | Servomoteur TTL, 12 V, 1.5 A (max) | 12 V Puissance | 1.5 A (max) | Actionneurs mains (16 unités) | Alimentés via buck 12 V Puissance (ou DROK 25A) |
| **Moteurs RobStride (QDD)** | Voir tableau [3.1] ci‑dessous | 48 V (15‑60 V admissible) | Voir tableau [3.1] | Actionneurs membres (26 unités) | Tous connectés au bus CAN |
| **Micro‑Hub eFlesh (ESP32‑S3)** | ESP32‑S3 USB‑Hub, régulation 5 → 3,3 V | 5 V (USB Hub) | – | Gestion 9‑16 × MLX90393 (tactile) par main | Aucun rail externe requis |
| **Capteurs MLX90393** | Magnétomètre 3‑axis, 0‑5 V | 3,3 V (via micro‑hub) | – | Tactile eFlesh (mains) | 9‑16 par main |
| **Capteurs FSR (Force Sensing Resistor)** | 4 × FSR par pied, résistance variable 1 kΩ‑∞ | 3,3 V (via régulation locale) | – | Détection de charge plantaire | Connectés aux ADC Spresense |
| **Résistances de terminaison CAN** | 120 Ω, 1 % | – | – | Placées sur le dernier moteur de chaque chaîne CAN (sauf bus Cou) | Conforme à la norme CAN |
| **Câbles d’alimentation** | Silicone 14 AWG (rouge/noir) – 5 m | 48 V | – | RS‑04 (grosses articulations) | Bobine achetée |
| **Câbles d’alimentation** | Silicone 18 AWG (rouge/noir) – 15 m | 48 V | – | Tous les autres moteurs (RS‑03, RS‑02, RS‑06, RS‑05, RS‑00) | Bobine achetée |
| **Connecteurs XT60 / XT30** | XT60 (30 A) pour troncs, XT30 (15 A) pour moteurs | – | – | Connexions 48 V entre bus‑bar et zones | Tous soudés selon procédure |
| **WAGO 221‑415 (5‑entrées)** | Levier, 32 A, 450 V, 0,2‑4 mm² | – | – | Splitters locaux bras (5 entrées) | Achetés |
| **WAGO 221‑413 (3‑entrées)** | Levier, 32 A, 450 V, 0,2‑4 mm² | – | – | Splitters locaux cou/tête | Achetés |
| **Mini‑busbars 6‑bornes** | Laiton, 60 V+, 30 A par borne | – | – | Splitters locaux jambes | Achetés |
| **Fusibles lame** | 30 A (bras), 50 A (jambes), 5 A (cou), 80 A (principal) | – | – | Protection par zone | Achetés |
| **Bouton E‑Stop** | Coup de poing NC, 48 V compatible | – | – | Coupure alimentation moteurs (pas Jetson) | Acheté |
| **MOSFET Haute‑côté BTS50085** | 100 V, 5 A, opto‑isolé | – | – | Coupure 48 V pilotée par Spresense | [À COMPLÉTER] |
| **Diviseur de tension batterie → Spresense** | R1 = 150 kΩ, R2 = 10 kΩ (3,3 V ref) | – | – | Surveillance tension batterie | Implémenté dans firmware |
| **Diodes de roue‑libre** | 1N4007 (x2 par solénoïde) | – | – | Protection MOSFET D4184 | À souder |
| **Câbles USB‑C → USB‑A blindés** | 30 cm, 90 Ω, ferrite | – | – | Connexion CANable Pro au hub | Achetés |
| **Câbles JST‑GH 4‑broches** | 1,25 mm pitch, 0,5 mm² | – | – | CAN H/L/GND/VCC logique des moteurs | Achetés |
| **Connecteur Qwiic → pins mâles** | Adafruit 4209 | – | – | Liaison BMI270 à Spresense | Acheté |

> **NB :** Tous les éléments listés ci‑dessus sont **validés** (commande passée ou stock disponible) pour la version V1.x du robot.

---

## 3. Nomenclature (BOM Locale)

| # | Référence fabricant / SKU | Désignation | Quantité | Prix (€/unité) | Fournisseur | Remarques |
|---|---------------------------|-------------|----------|----------------|-------------|-----------|
| 1 | **BMS 13S 30A** | Batterie VAE 48 V 10 Ah (Li‑ion NMC) | 1 | 300‑450 | Save My Battery / Yose Power / Amazon | Vérifier 13 S, 30 A cont. |
| 2 | **Fusible 80A** | Fusible automobile ANL 80 A | 1 | 3‑5 | Amazon.fr | – |
| 3 | **Fusible 30A** | Lame 30 A (bras) | 2 | 2‑3 | Amazon.fr | – |
| 4 | **Fusible 50A** | Lame 50 A (jambes) | 2 | 2‑4 | Amazon.fr | – |
| 5 | **Fusible 5A** | Lame 5 A (cou) | 1 | 1‑2 | Amazon.fr | – |
| 6 | **Bus‑bar 8‑bornes** | Laiton étamé, 150 A, double | 1 | [À COMPLÉTER] | SVB Marine / RS‑Components | – |
| 7 | **Mini‑busbar 6‑bornes** | Laiton, 60 V+, 30 A | 2 | 8‑12 | Amazon.fr | – |
| 8 | **WAGO 221‑415** | Splitter 5‑entrées | 4 | 0 (déjà acheté) | – | – |
| 9 | **WAGO 221‑413** | Splitter 3‑entrées | 6 | 0 (déjà acheté) | – | – |
|10| **Buck 48→19 V 5 A** | DC‑DC isolé 95 W | 1 | 15‑20 | Amazon.fr | Modèle exact à préciser |
|11| **Buck 48→12 V 10 A** | DC‑DC 60 V in / 12 V out | 1 | 10‑18 | Amazon.fr | Mean Well DDR‑120C‑12 ou Homelylife |
|12| **Buck 48→12 V 20 A** | DC‑DC 60 V in / 12 V out | 1 | 10‑18 | Amazon.fr | – |
|13| **Buck 48→5 V 5 A** | DC‑DC isolé 25 W | 1 | 10‑15 | Amazon.fr | – |
|14| **Hub USB 3.0 10 ports** | StarTech ST103008U2C (ou Sabrent HB‑BU10) | 1 | 70‑120 | Amazon.fr | Alimentation 12 V requise |
|15| **InnoMaker USB2CAN‑C** | CAN‑USB isolé 2.5 kV | 1 | 45‑55 | OpenLightLabs / Tindie | Firmware candleLight |
|16| **CANable Pro** | CAN‑USB isolé 2.5 kV (PCB) | 4 | 30‑40 | OpenLightLabs / AliExpress / Tindie | – |
|17| **Module Debug CAN** | Interface opto‑couplée | 1 | 25‑35 | OpenLightLabs | – |
|18| **Dual MOSFET D4184** | Driver 2 × MOSFET | 1 | 8‑12 | Amazon.fr | Diodes 1N4007 à souder |
|19| **Solénoïde LEX‑SOLEN‑04** | 12 V 0,6 A | 2 | 5‑8 | Digi‑Key / Mouser | – |
|20| **Spresense Standard Board** | CXD5602PWBEXT1 | 1 | 70‑90 | Sony Store / Mouser | – |
|21| **BMI270 Breakout** | SparkFun SEN‑22397 | 1 | 12‑15 | SparkFun / Digi‑Key | – |
|22| **ESP32‑S3 Micro‑Hub** | USB‑Hub + 3,3 V LDO | 2 | 10‑15 | AliExpress / Tindie | – |
|23| **MLX90393** | Magnétomètre 3‑axis | 16‑32 (selon nombre de capteurs) | 2‑3 | Digi‑Key / Mouser | – |
|24| **FSR 4 × par pied** | Force Sensing Resistor | 8 | 1‑2 | SparkFun / Digi‑Key | – |
|25| **Câble Silicone 14 AWG** | Rouge + Noir, 5 m | 1 bobine | 10‑15 | Amazon.fr | – |
|26| **Câble Silicone 18 AWG** | Rouge + Noir, 15 m | 1 bobine | 15‑20 | Amazon.fr | – |
|27| **Connecteurs XT60** | Mâle/Femelle, 30 A | 12 (troncs + moteurs RS‑04) | 0,5‑1 | Amazon.fr | Soudés sur troncs |
|28| **Connecteurs XT30** | Mâle/Femelle, 15 A | 30 (moteurs RS‑03/02/06/05/00) | 0,3‑0,5 | Amazon.fr | Soudés sur moteurs |
|29| **JST‑GH 4‑pin** | 1,25 mm pitch, 0,5 mm² | 26 sets | 0,2‑0,4 | Digi‑Key | – |
|30| **Diodes 1N4007** | 1000 V, 1 A | 2 × solénoïde | 0,05 | Digi‑Key | – |
|31| **MOSFET Haute‑côté BTS50085** | Smart‑Switch 100 V 5 A | 1 | [À COMPLÉTER] | Infineon / Digi‑Key | – |
|32| **Bouton E‑Stop** | Coup de poing NC, 48 V | 1 | 8‑12 | Amazon.fr | – |
|33| **Résistances 120 Ω** | 1 % 0,25 W | 5 (terminations) | 0,1 | Digi‑Key | – |

> **[À COMPLÉTER]** indique les informations (fabricant, prix exact) qui n’apparaissent pas explicitement dans les sources fournies.

---

## 4. État de la Conception (CAD & Simulation)

| Sous‑module | Fichier CAD | Statut | Commentaire |
|---|---|---|---|
| Bus‑bar central & splitters | `02_Elec_Busbar.step` | ✅ Modélisé, vérifié dimensions | Export STL pour impression de support |
| Supports CANable Pro | `CANable_Cluster.step` | ✅ Modélisé, assemblage prévu | Espacement 5 mm, ventilation |
| Boîtier hub USB | `Hub_Enclosure.step` | ✅ Modélisé, pré‑impression | Prévoir découpe pour ventilation |
| Câblage d’alimentation 48 V | `Power_Wiring_48V.iam` | ✅ Simulé (PTC, chute de tension) | Vérif. perte < 0,2 V sur troncs |
| Distribution logique 12 V/5 V | `Logic_Distribution.step` | ✅ Modélisé | Inclut buck, régulateurs locaux |
| Montage Spresense + BMI270 | `Spresense_Mount.step` | ✅ Modélisé | Emplacement dans torse, accès USB |
| Montage solénoïdes tête | `Solenoid_Mount.step` | ✅ Modélisé | Prévoir espace pour diodes |
| Câblage CAN (daisy‑chain) | `CAN_Topology.iam` | ✅ Vérifié (pas de stubs > 30 cm) | Terminaisons 120 Ω ajoutées |

---

## 5. Instructions de Montage Critiques

| Étape | Action | Points de vigilance |
|---|---|---|
| **1. Pré‑préparation des câbles moteurs** | Couper les 5 mm d’étain des câbles fournis (RS‑03/02/06/05/00) pour exposer le cuivre nu. | Utiliser pince coupante fine, éviter d’endommager le fil. |
| **2. Soudure des connecteurs XT60/XT30** | Souder les fiches mâles/femelles sur les troncs (48 V) et sur chaque moteur RS‑04 (XT60) ou RS‑03/… (XT30). | Utiliser fer ≥ 60 W, appliquer gaine thermo‑rétractable. |
| **3. Insertion dans WAGO** | Insérer le fil nu (sans soudure) dans les leviers WAGO 221. | Vérifier que le fil est bien enfoncé, pas de jeu. |
| **4. Pose des résistances de terminaison** | Installer 120 Ω sur le dernier moteur de chaque chaîne CAN (hors bus Cou). | S’assurer que la résistance est bien entre CAN_H et CAN_L, pas à la masse. |
| **5. Connexion des buck** | Alimenter chaque buck depuis le bus‑bar 48 V, vérifier la polarité. | Mesurer la sortie avant de connecter les charges (± 5 %). |
| **6. Montage du hub USB** | Fixer le hub sur le rail 12 V Logique, raccorder l’alimentation 12 V. | Vérifier la continuité GND entre hub et bus CAN (ground commun). |
| **7. Installation du module Dual MOSFET D4184** | Souder les diodes 1N4007 en parallèle à chaque solénoïde, puis connecter le MOSFET au rail 12 V Logique et aux GPIO 3.3 V de la Jetson. | Vérifier orientation des diodes (cathode vers +). |
| **8. Intégration Spresense + BMI270** | Connecter le BMI270 via câble Qwiic à la Spresense, brancher les 6 ADC aux FSR. | S’assurer que le diviseur batterie (150 kΩ/10 kΩ) ne dépasse pas 3,3 V sur A0. |
| **9. Vérification E‑Stop** | Brancher le bouton NC entre le +48 V et le fusible principal (coupure moteurs). | Tester l’arrêt complet des moteurs sans couper la Jetson. |
| **10. Test de mise sous tension** | Alimenter le bus‑bar avec la batterie ou la Wanptek (48 V, OCP ≤ 3 A). | Vérifier les tensions de chaque rail, le boot de la Jetson, puis la réponse du watchdog. |

---

## 6. Backlog Technique & Questions en Suspens

| N° | Question / Incertitude | Source / Contexte | Priorité | Action proposée |
|---|---|---|---|---|
| 1 | **Modèle exact du buck 48 → 19 V (Jetson)** – plusieurs références possibles (Mean Well, D‑Series, etc.). | `FINAL_Bilan_Tensions.md` indique seulement « Buck 48V→19V 5A 95 W ». | Haute | Vérifier le bon de commande ou le numéro de série du module déjà en stock. |
| 2 | **Fournisseur du bus‑bar central (8 bornes)** – aucune référence précise. | Mentionné dans le texte, pas de SKU. | Moyenne | Contacter SVB Marine ou RS‑Components pour obtenir un modèle certifié 150 A, 8 bornes. |
| 3 | **MOSFET Haute‑côté BTS50085** – aucune référence d’achat ni prix. | `STUDY_Watchdog_Robot.md` décrit le composant mais pas le fournisseur. | Moyenne | Recherche sur Digi‑Key/ Mouser, commander un lot de 2 unités. |
| 4 | **Valeur exacte du buck 48 → 12 V 20 A (Power)** – plusieurs modèles (Mean Well DDR‑240C‑12, Homelylife). | `FINAL_Bilan_Tensions.md` indique seulement « Buck 48V→12V 20A ». | Haute | Confirmer le modèle déjà acquis ou choisir le plus adapté (≥ 60 V in). |
| 5 | **Compatibilité du hub USB 3.0 industriel avec le buck 12 V Logique** – besoin de vérifier la tension d’entrée maximale du hub. | `STUDY_Electronique_Historique.md` indique alimentation 7‑24 V. | Basse | Mesurer la tension d’entrée du hub en condition de charge (12 V) – si > 24 V, remplacer. |
| 6 | **Longueur exacte des câbles 14 AWG et 18 AWG** – les estimations sont basées sur des mesures approximatives. | `STUDY_Electronique_Historique.md` (tableau longueurs). | Moyenne | Faire un relevé sur le prototype final et ajuster les bobines commandées. |
| 7 | **Numéro de série du module de debug CAN** – nécessaire pour la configuration du firmware. | Mentionné comme « déjà acheté », mais pas de référence. | Basse | Vérifier l’étiquette du composant en stock. |
| 8 | **Valeur de la résistance de pull‑down (10 kΩ) du diviseur batterie** – confirmée mais pas de tolérance. | `STUDY_Watchdog_Robot.md`. | Basse | Utiliser 1 % 10 kΩ, vérifier la lecture ADC (≈ 3,3 V à 55 V). |
| 9 | **Gestion thermique du RS‑04 (hanches/genoux)** – besoin d’un calcul détaillé de dissipation et d’un plan de refroidissement (aluminium CNC). | `STUDY_Motorisation_QDD_RobStride.md` indique 14,5 W dissipation, mais pas de dissipateur. | Haute | Concevoir un insert aluminium avec contact thermique (pâte thermique) et valider par simulation CFD. |
|10| **Éventuelle utilisation d’un ORing MOSFET pour la mise en parallèle de deux packs batterie** – non implémenté dans V1. | Roadmap future (section 7). | Faible | Documenter la solution pour la version V2. |

---

## 7. Roadmap & Itérations Futures (Optionnel)

| Future version | Sujet / Amélioration | Impact attendu |
|---|---|---|
| **V2** | Ajout d’un **rail 3,3 V dédié** (au lieu de dérivation via Spresense) pour les capteurs eFlesh et IMU. | Réduction du bruit sur le rail 5 V, meilleure isolation. |
| **V2** | **SVS Électromagnétique** (solénoïde de verrouillage) sur les RS‑04 pour éliminer la dissipation statique. | Autonomie accrue, moins de chauffe au repos. |
| **V3** | **Batterie sur‑mesure** (forme adaptée au torse) – 15 Ah, 50 A cont. | Augmentation de l’autonomie à ≈ 1 h 30. |
| **V3** | **CAN FD** (2 Mbps) pour augmenter la bande passante des bus moteurs. | Possibilité d’ajouter plus de capteurs en temps réel. |
| **V4** | **Intégration d’un deuxième MOSFET BTS50085** en parallèle (ORing) pour la redondance de l’alimentation principale. | Sécurité accrue, gestion de la défaillance d’un pack. |
| **V5** | **Remplacement du hub USB 3.0 industriel** par un hub **PCIe‑Express** pour bande passante vidéo OAK‑D Pro. | Latence réduite, support de caméras 4K à 120 fps. |

*Toutes les itérations futures sont **excluses** des tableaux principaux et ne concernent pas la version V1.x décrite dans ce document.*