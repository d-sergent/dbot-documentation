# 🦾 Spécifications Finales – 02 Électronique et Énergie (D‑Bot V1.x)

> **Version du document :** V1.1 – 25 novembre 2026  
> **Portée :** Toutes les pièces, sous‑systèmes d’alimentation, de distribution, de conversion, de communication et de capteurs associés au module 02 Électronique & Énergie du robot humanoïde D‑Bot (40 kg).  
> **Sources principales :** `FINAL_Bilan_Tensions.md`, `STUDY_Electronique_Historique.md`, `STUDY_Motorisation_QDD_RobStride.md`, `STUDY_Watchdog_Robot.md`, `AUDIT_ETUDE_02_Electronique_et_Energie.md` (points 1-2), manuels `Manuels/RS0x*` et `Manuels/CANFD/`.  
> **Conformité :** Toutes les valeurs proviennent d’une source datée ou d’un résultat de test réel. En cas d’ambiguïté, la donnée la plus récente a été retenue ; les points non résolus sont listés dans la section 6.

---


## 📑 Sommaire

- [**1. Vue d’Ensemble (Version Actuelle)**](#1-vue-densemble-version-actuelle)
- [**2. Spécifications Matérielles Validées**](#2-spécifications-matérielles-validées)
  - [2.1 Budget de Bande Passante CAN et Affectation des 27 Moteurs](#21-budget-de-bande-passante-can-et-affectation-des-27-moteurs)
- [**3. Nomenclature (BOM Locale)**](#3-nomenclature-bom-locale)
- [**4. État de la Conception (CAD & Simulation)**](#4-état-de-la-conception-cad-simulation)
- [**5. Instructions de Montage Critiques**](#5-instructions-de-montage-critiques)
  - [5.1 Câblage du Système Réflexe (Spresense ➔ Teensy)](#51-câblage-du-système-réflexe-spresense-teensy)
  - [5.2 Tableau de Montage Général](#52-tableau-de-montage-général)
- [**6. Backlog Technique & Questions en Suspens**](#6-backlog-technique-questions-en-suspens)
- [**7. Roadmap & Itérations Futures (Optionnel)**](#7-roadmap-itérations-futures-optionnel)

---

## 1. Vue d’Ensemble (Version Actuelle)

L’architecture électrique du D‑Bot repose sur :

* **Source principale** : batterie Li‑ion NMC 13 S ≈ 48 V (46,8 V nominal, 54,6 V max).  
* **Distribution** : bus‑bar central (torse) à 48 V, alimentant **six zones** (bras G/D, jambe G/D, cou/tête, logique).  
* **Conversion** : quatre rails de tension secondaire dérivés du 48 V via des convertisseurs buck isolés : 19 V (Jetson), 12 V Logique (10 A), 12 V Puissance (20 A) et 5 V (Always‑On).  
* **Cervelet (Locomotion)** : 2x **Teensy 4.1 + Shields Triple CAN FD (SK Pang)** gérant 6 bus CAN (4x CAN 2.0B 1 Mbps sur CAN1/CAN2 + 2x CAN3 compatibles CAN-FD, exploités en 1 Mbps par défaut) de manière décentralisée (Upper Body / Lower Body). Boucle Teensy ↔ moteurs à 500 Hz pour les jambes et la taille, 250 Hz pour les bras, 100 Hz pour le cou ; politique RL à 50 Hz sur la Jetson ; voir §2.1. Les adaptateurs USB-CAN InnoMaker/CANable ont été retirés de l'architecture embarquée (relégués aux tests sur banc).
* **Lien Cerveau-Cervelet** : La communication entre la Jetson et les Teensys se fait via **USB natif** (très haut débit 480 Mbps) pour la phase de prototypage (V1). Les ports Ethernet (RJ45) présents sur les shields SK Pang sont gardés en réserve pour une éventuelle V2 industrielle nécessitant une tolérance absolue aux chocs et déconnexions physiques (via protocole UDP / micro-ROS).
* **Supervision (Moelle Épinière)** : Sony Spresense « Always‑On » (watchdog, lecture ADC, IMU BMI270) couplée aux Teensys via UART pour les réflexes d'amortissement matériels.  

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
| **Hub USB 3.0 (Petit Format)** | Petit hub USB 3.0 standard (non industriel) | 5 V | – | Centralise les Teensy, l'OAK-D et le Spresense vers la Jetson | Allègement du robot suite à la suppression des CANable |
| **Cervelet (Locomotion)** | **2x Teensy 4.1** (NXP i.MX RT1062, 600MHz) | 5 V (USB) | – | Calculs d'IK, PID, équilibre temps réel | 1x Lower Body, 1x Upper Body |
| **Shields Triple CAN FD** | **2x SK Pang Teensy 4.1 Triple CAN Board** | 12 V (rail 12 V Logique) | – | 2x CAN 2.0B (CAN1/CAN2) + 1x CAN-FD (CAN3), terminaisons 120 Ω côté Teensy, LCD de télémétrie | Se clipe sur le Teensy. Remplace les CANable/InnoMaker |
| **Module de debug CAN** | Interface opto‑couplée (isolée) | 48 V bus | – | Configuration ID moteurs, firmware sur PC | Acheté |
| **Module Dual MOSFET D4184** | Driver MOSFET D4184 (2 × N‑channel) | 12 V (rail 12 V Logique) | 2 × 0,6 A (solénoïdes) | Pilotage solénoïdes tête | Diodes 1N4007 à souder en parallèle |
| **Solénoïdes tête** | LEX‑SOLEN‑04, 12 V, 0,6 A chacun | 12 V | 0,6 A | Blocage/déblocage tête | 2 unités |
| **Sony Spresense Standard Board** | CXD5602PWBEXT1, 6 ADC, 3,3 V I/O | 5 V (Always‑On) | 1 A (typ.) | Watchdog, lecture FSR, IMU, UART | Achetée |
| **IMU BMI270** | SparkFun BMI270 Breakout (SEN‑22397) | 3,3 V (via Spresense) | – | Équilibre bipède (416 Hz) | Connecté I2C Qwiic |
| **Feetech STS3250 / HL-3915** | Servomoteur TTL, 12 V, 1.5 A (max) | 12 V Puissance | 1.5 A (max) | Actionneurs mains (16 unités) | Alimentés via buck 12 V Puissance (ou DROK 25A) |
| **Moteurs RobStride (QDD)** | Voir tableau [3.1] ci‑dessous | 48 V (15‑60 V admissible) | Voir tableau [3.1] | Actionneurs membres (27 unités, dont Waist Yaw RS-06) ; affectation des bus au §2.1 | Tous connectés au bus CAN |
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
| **Câbles USB‑C → USB‑A blindés** | 30 cm, 90 Ω, ferrite | – | – | Connexion des 2 Teensy 4.1 au hub | Achetés |
| **Câbles JST‑GH 4‑broches** | 1,25 mm pitch, 0,5 mm² | – | – | CAN H/L/GND/VCC logique des moteurs | Achetés |
| **Connecteur Qwiic → pins mâles** | Adafruit 4209 | – | – | Liaison BMI270 à Spresense | Acheté |

> **NB :** Tous les éléments listés ci‑dessus sont **validés** (commande passée ou stock disponible) pour la version V1.x du robot.

### 2.1 Budget de Bande Passante CAN et Affectation des 27 Moteurs

> [!NOTE]
> **Correctif des points bloquants n°1 et n°2 (`AUDIT_ETUDE_02_Electronique_et_Energie.md`, revue du 22 novembre 2026)** : réconciliation matérielle des 6 bus réels (`2x Teensy 4.1 + SK Pang Triple CAN`), intégration du 27e moteur (`Waist Yaw RS-06`) et dimensionnement sans saturation du trafic bidirectionnel (commande + retour d'état).

* **Ressources matérielles réelles :** Chaque Teensy 4.1 possède `3` contrôleurs FlexCAN dont **seul `CAN3` gère le CAN-FD** (`CAN1` et `CAN2` sont en CAN 2.0B classique). Sur deux cartes + shields SK Pang Triple CAN, le robot dispose donc de **`4` bus CAN 2.0B + `2` bus compatibles CAN-FD**, tous exploités par défaut en **CAN 2.0B à 1 Mbps**.
* **Hypothèses de trafic (manuels `Manuels/RS0xUser Manual*.pdf` & `Manuels/CANFD/`) :**
  * Format par défaut : trame étendue `29 bits`, `8 octets` de données, débit `1 Mbps` (commande type 23 acceptant `1M / 500K / 250K / 125K`).
  * En mode MIT, chaque moteur émet **1 trame de retour** pour **1 trame de commande**, soit **2 trames par moteur et par cycle**.
  * Variantes CAN-FD (`Manuels/CANFD/`, jusqu'à `5 Mbps` en phase de données via `F_CMD` `05 = 5M`, `06 = 4M`, `07 = 3M`, `08 = 2M`, `01 = 1M`, cf. `Annexes/robstride/firmware/01_Notes_Maj_Firmware.md` §6.2) : charge utile inchangée à `8 octets` ; l'arbitrage, l'accusé de réception, la fin de trame et l'intervalle inter-trames restent à `1 Mbps`.
* **Durées de trame et critère d'acceptation :**
  * **CAN 2.0B étendu 29 bits, 8 octets à 1 Mbps** (intervalle inter-trames inclus) : `131 bits` min / `~140 bits` typique / `160 bits` pire cas -> durée d'une paire commande + retour `T_paire` = **`262 µs` min / `280 µs` typique / `320 µs` pire cas**.
  * **CAN-FD 5 Mbps** (arbitrage `1 Mbps`, données `5 Mbps`, BRS) : `~72 µs` typique / `80 µs` pire cas par trame -> `T_paire` ≈ **`145 µs` typique / `160 µs` pire cas**.
  * **Trame standard 11 bits, 8 octets** (protocole MIT natif via type 25 -> `2`) : `111 à 135 bits`.
  * **Formule :** `Charge_bus = N_moteurs x f_boucle x T_paire`.
  * **Critère d'acceptation :** charge **`<= 70 %` en typique** et **`<= 80 %` en pire cas** (marge réservée aux trames d'erreur, lectures/écritures de paramètres types 17/18 et trames de défaut type 21).

| Scénario de référence | Nb moteurs | Fréquence | Charge CAN 2.0B (typique / pire cas) | Charge CAN-FD 5 Mbps (typique / pire cas) | Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Membre complet à 1 kHz | 6 | 1 000 Hz | 168 % / 192 % | 87 % / 96 % | ❌ Saturé / non admissible |
| Membre complet à 500 Hz | 6 | 500 Hz | 84 % / 96 % | 43 % / 48 % | ❌ Non admissible en 2.0B / ✅ OK en FD |
| Membre complet à 400 Hz | 6 | 400 Hz | 67 % / 77 % | – | ✅ Limite en 2.0B |
| 3 moteurs à 1 kHz (ex. cou + Waist) | 3 | 1 000 Hz | 84 % / 96 % | 44 % / 48 % | ❌ Non admissible en 2.0B / ✅ OK en FD |
| 2 moteurs à 1 kHz (cou seul) | 2 | 1 000 Hz | 56 % / 64 % | 29 % / 32 % | ✅ OK |
| 4 moteurs à 500 Hz | 4 | 500 Hz | 56 % / 64 % | 29 % / 32 % | ✅ OK |
| 5 moteurs à 500 Hz | 5 | 500 Hz | 70 % / 80 % | ~36 % / 40 % | ✅ Limite en 2.0B / ✅ OK en FD |
| 4 moteurs à 1 kHz (CAN-FD) | 4 | 1 000 Hz | – | 58 % / 64 % | ✅ OK en CAN-FD uniquement |

* **Principe de commande MIT retenu :** En mode MIT, la loi d'impédance `tau = Kp*(q_des - q) + Kd*(dq_des - dq) + tau_ff` est calculée **à l'intérieur du contrôleur de chaque moteur** à la fréquence de sa boucle interne de courant. Le bus CAN ne transporte que les consignes et les retours d'état : la raideur et l'amortissement ne dépendent donc pas du débit CAN. Une boucle Teensy ↔ moteurs à **`500 Hz`** pour les jambes et la taille représente `10x` la fréquence de la politique RL (`50 Hz` sur Jetson) pour une latence de bus de `2 ms`. Le `1 kHz` n'est requis que pour un contrôle en couple pur de type MPC/WBC (hors périmètre V1).

#### Affectation retenue des 27 moteurs sur les 6 bus (répartition bas du corps 4 / 4 / 5)

| Teensy | Port | Mode matériel | Moteurs affectés | Nb | Fréquence | Charge CAN 2.0B (typique / pire cas) | Si variante CAN-FD 5 Mbps |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Lower** | `CAN1` | CAN 2.0B | Hanche G (`RS-04` Pitch + `RS-03` Roll + `RS-03` Yaw) + Genou G (`RS-04`) | 4 | 500 Hz | 56 % / 64 % | – (port non FD) |
| **Lower** | `CAN2` | CAN 2.0B | Hanche D (`RS-04` Pitch + `RS-03` Roll + `RS-03` Yaw) + Genou D (`RS-04`) | 4 | 500 Hz | 56 % / 64 % | – (port non FD) |
| **Lower** | `CAN3` | Compatible FD | 4x `RS-03` cheville (cardans G + D) + `Waist Yaw RS-06` | 5 | 500 Hz | 70 % / 80 % *(limite)* | ~36 % / 40 % |
| **Upper** | `CAN1` | CAN 2.0B | Bras G (`RS-04` épaule pitch, `RS-03` roll, `RS-02` yaw, `RS-03` coude, `RS-10P` supination, `RS-00` poignet) | 6 | 250 Hz | 42 % / 48 % | – (port non FD) |
| **Upper** | `CAN2` | CAN 2.0B | Bras D (`RS-04` épaule pitch, `RS-03` roll, `RS-02` yaw, `RS-03` coude, `RS-10P` supination, `RS-00` poignet) | 6 | 250 Hz | 42 % / 48 % | – (port non FD) |
| **Upper** | `CAN3` | Compatible FD | Cou (`2x RS-05` Pan + Tilt) | 2 | 100 Hz | 6 % / 6 % | ~3 % |

*(Total vérifié : `4 + 4 + 5 + 6 + 6 + 2 = 27` actionneurs RobStride.)*

* **Leviers si `CAN3` Lower dépasse les seuils lors des essais au banc :**
  1. Activer le mode **CAN-FD à 5 Mbps** sur `CAN3` si la variante CAN-FD des `RS-03` et `RS-06` reçus est confirmée (`~36 à 40 %` de charge).
  2. Basculer les moteurs en **protocole MIT natif** (trames standard `11 bits` via type 25 -> `2`) : `~60 %` typique / `~68 %` pire cas.
  3. Abaisser `CAN3` Lower à **`400 Hz`** (`56 %` typique / `64 %` pire cas).
* **Ordre de câblage `CAN3` Lower (chaînage série obligatoire) :** `Teensy Lower (120 Ω intégrée au shield SK Pang)` -> `Waist Yaw RS-06` -> `Cheville G A (RS-03)` -> `Cheville G B (RS-03)` -> `Cheville D A (RS-03)` -> `Cheville D B (RS-03, terminaison 120 Ω en bout de bus)`.
  * Longueur estimée : `~3,2 m` `[À VALIDER au harnais]`, dérivations `< 30 cm`.
  * **Règle mécanique RobStride (arbres pleins) :** aucun moteur RobStride ne dispose d'arbre creux traversant ; tout câble CAN et 48 V contourne le `Waist RS-06` et les actionneurs par les corridors latéraux/ventraux avec boucle de service libre.
  * Si activation CAN-FD `5 Mbps`, valider impérativement la qualité du signal sur ce harnais au banc avant déploiement.

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
|15| **InnoMaker USB2CAN‑C** | CAN‑USB isolé 2.5 kV | 1 | 45‑55 | OpenLightLabs / Tindie | Outil de debug banc uniquement (hors robot embarqué) |
|16| **CANable Pro** | CAN‑USB isolé 2.5 kV (PCB) | 4 | 30‑40 | OpenLightLabs / AliExpress / Tindie | Outil de debug banc uniquement (hors robot embarqué) |
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
|33| **Résistances 120 Ω** | 1 % 0,25 W | 6 (1 par bus, côté dernier moteur ; extrémité Teensy intégrée au shield SK Pang) | 0,1 | Digi‑Key | – |

> **[À COMPLÉTER]** indique les informations (fabricant, prix exact) qui n’apparaissent pas explicitement dans les sources fournies.

---

## 4. État de la Conception (CAD & Simulation)

| Sous‑module | Fichier CAD | Statut | Commentaire |
|---|---|---|---|
| Bus‑bar central & splitters | `02_Elec_Busbar.step` | ✅ Modélisé, vérifié dimensions | Export STL pour impression de support |
| Supports CANable Pro | `CANable_Cluster.step` | ❌ Obsolète (CANable retirés de l'architecture embarquée) | Remplacé par l'architecture `2x Teensy 4.1 + SK Pang Triple CAN` |
| Boîtier hub USB | `Hub_Enclosure.step` | ✅ Modélisé, pré‑impression | Prévoir découpe pour ventilation |
| Câblage d’alimentation 48 V | `Power_Wiring_48V.iam` | ✅ Simulé (PTC, chute de tension) | Vérif. perte < 0,2 V sur troncs |
| Distribution logique 12 V/5 V | `Logic_Distribution.step` | ✅ Modélisé | Inclut buck, régulateurs locaux |
| Montage Spresense + BMI270 | `Spresense_Mount.step` | ✅ Modélisé | Emplacement dans torse, accès USB |
| Montage solénoïdes tête | `Solenoid_Mount.step` | ✅ Modélisé | Prévoir espace pour diodes |
| Câblage CAN (daisy‑chain) | `CAN_Topology.iam` | ✅ Vérifié (pas de stubs > 30 cm) | Terminaisons 120 Ω ajoutées |

---

## 5. Instructions de Montage Critiques

### 5.1 Câblage du Système Réflexe (Spresense ➔ Teensy)

Pour garantir un temps de réaction < 1 ms en cas de chute, la Moelle Épinière (Spresense) et le Cervelet (Teensy) communiquent via une architecture hybride :
1. **Ligne d'Interruption (Vitesse pure) :** La broche `D2` de la Spresense est reliée à la broche `Pin 2` des deux Teensys. Si l'IMU détecte une chute, `D2` passe à l'état `HIGH`. Les Teensys déclenchent une interruption matérielle et forcent instantanément les moteurs en mode "Amortisseur" (Damping).
2. **Ligne UART (Diagnostic) :** La broche `TX` (D1) Spresense est reliée à la broche `RX2` (Pin 7) des Teensys, et `RX` (D0) à `TX2` (Pin 8). Cela permet d'échanger des logs détaillés sur la chute.

> **⚠️ AVERTISSEMENT CRITIQUE (RISQUE DE DESTRUCTION MATÉRIELLE) :**  
> Le processeur du Teensy 4.1 **ne tolère absolument pas le 5V**. Sur la carte d'extension de la Sony Spresense, **vous devez IMPÉRATIVEMENT positionner le cavalier (jumper) de tension GPIO sur `3.3V`** avant de relier les fils UART ou Interrupt. L'oubli de ce jumper détruira les broches du Teensy.

### 5.2 Tableau de Montage Général

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
|11| **Identification variante CAN 2.0B / CAN-FD des 27 moteurs reçus + mesure de charge réelle des 6 bus au banc** – vérifier si les lots livrés supportent le CAN-FD `5 Mbps` (`Manuels/CANFD/`) ou uniquement le CAN 2.0B `1 Mbps`. | `AUDIT_ETUDE_02_Electronique_et_Energie.md` (point 1), `Manuels/RS0x*`, `Manuels/CANFD/`. | Haute | Tester 1 seul moteur sur alimentation Wanptek : lire le paramètre baud dans Motor Studio (`motor_baud` `0x2009` ou `baud` `0x2022`/`0x2024` selon modèle) ; une variante CAN-FD accepte `F_CMD` `05` à `08` en type 23 (redémarrage moteur requis, puis revenir à `01` = `1 Mbps`). Mesurer ensuite la charge réelle via les compteurs d'erreurs FlexCAN du Teensy ou `candump` sur CANable au banc. |
|12| **Figer les IDs CAN des 27 moteurs par bus** – table d'adressage unique `ID` par articulation et par port `CAN1..CAN3` sur Teensy Lower/Upper. | §2.1 et `FINAL_CAN_Bus_Topology.md`. | Moyenne | `[À COMPLÉTER]` Attribuer et vérifier les 27 IDs uniques avant câblage définitif des harnais. |

---

## 7. Roadmap & Itérations Futures (Optionnel)

| Future version | Sujet / Amélioration | Impact attendu |
|---|---|---|
| **V2** | Ajout d’un **rail 3,3 V dédié** (au lieu de dérivation via Spresense) pour les capteurs eFlesh et IMU. | Réduction du bruit sur le rail 5 V, meilleure isolation. |
| **V2** | **SVS Électromagnétique** (solénoïde de verrouillage) sur les RS‑04 pour éliminer la dissipation statique. | Autonomie accrue, moins de chauffe au repos. |
| **V3** | **Batterie sur‑mesure** (forme adaptée au torse) – 15 Ah, 50 A cont. | Augmentation de l’autonomie à ≈ 1 h 30. |
| **V1.5** | **Activation CAN-FD 5 Mbps sur les 2 bus `CAN3`** (si variante CAN-FD confirmée au banc sur `RS-03`, `RS-06`, `RS-05`). | Réduction de la charge `CAN3 Lower` de `70 %` à `~36-40 %` à `500 Hz`. |
| **V2** | **Contrôleurs CAN-FD SPI additionnels (`MCP2518FD`) ou 3e Teensy** si un contrôle en couple pur à `1 kHz` (`MPC / WBC`) devient requis. | Débit `5 Mbps` sur les bus membres sans saturation. |
| **V4** | **Intégration d’un deuxième MOSFET BTS50085** en parallèle (ORing) pour la redondance de l’alimentation principale. | Sécurité accrue, gestion de la défaillance d’un pack. |
| **V5** | **Remplacement du hub USB 3.0 industriel** par un hub **PCIe‑Express** pour bande passante vidéo OAK‑D Pro. | Latence réduite, support de caméras 4K à 120 fps. |

*Toutes les itérations futures sont **excluses** des tableaux principaux et ne concernent pas la version V1.x décrite dans ce document.*