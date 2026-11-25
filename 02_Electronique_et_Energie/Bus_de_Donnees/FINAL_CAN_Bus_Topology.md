# FINAL - Topologie du Bus CAN (Moteurs RobStride)

> **Version :** V1.1 – 25 novembre 2026 (alignée sur [FINAL_CONSOLIDE_02_Electronique_et_Energie.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/02_Electronique_et_Energie/FINAL_CONSOLIDE_02_Electronique_et_Energie.md) §2.1 et `AUDIT_ETUDE_02_Electronique_et_Energie.md` points 1-2).

Le bus CAN est la colonne vertébrale du robot. Cette fiche définit le protocole, la segmentation des 6 bus pour les 27 moteurs RobStride et le matériel de communication.

## 📑 Sommaire

- [**1. Principe du Bus CAN**](#1-principe-du-bus-can)
- [**2. Segmentation des Bus (Bande passante)**](#2-segmentation-des-bus-bande-passante)
- [**3. Matériel et Architecture USB**](#3-matériel-et-architecture-usb)
- [**4. Câblage et Couleurs**](#4-câblage-et-couleurs)

---

## 1. Principe du Bus CAN

* **Protocole actif par défaut :** CAN 2.0B à **1 Mbps** (trame étendue 29 bits, 8 octets de données ; 2 trames par moteur et par cycle en mode MIT : 1 commande + 1 retour d'état).
* **Compatibilité CAN-FD :** Sur chaque couple **Teensy 4.1 + shield SK Pang Triple CAN**, seuls les ports **`CAN3`** disposent d'un contrôleur et d'un transceiver **CAN-FD** (`CAN1` et `CAN2` restent en CAN 2.0B classique). L'activation CAN-FD (jusqu'à 5 Mbps sur les variantes moteurs `Manuels/CANFD/`) reste optionnelle après test d'identification au banc.
* **Signaux :** `CAN_H`, `CAN_L`, `GND` (indispensable).
* **Terminaison :** Résistance `120 Ω` côté Teensy (intégrée au shield SK Pang — vérifier la position du cavalier de terminaison sur le shield `[À COMPLÉTER]`) et résistance `120 Ω` sur le dernier moteur de chaque chaîne daisy-chain.
* **Exception Cou :** Pas de terminaison supplémentaire requise côté moteur sur le bus du cou (`2x RS-05`) si câbles `< 30 cm`.

---

## 2. Segmentation des Bus (Bande passante)

Pour éviter toute saturation en CAN 2.0B à 1 Mbps, les boucles bas niveau Teensy ↔ moteurs sont cadencées à **500 Hz** (jambes + taille), **250 Hz** (bras) et **100 Hz** (cou), pour une politique RL à **50 Hz** sur la Jetson. En mode MIT, la loi d'impédance (`tau = Kp*(q_des - q) + Kd*(dq_des - dq) + tau_ff`) tourne dans le contrôleur interne du moteur ; le débit du bus n'affecte donc ni la raideur ni l'amortissement.

* **Formule :** `Charge_bus = N_moteurs x f_boucle x T_paire`, avec `T_paire` = `280 µs` typique / `320 µs` pire cas en CAN 2.0B à `1 Mbps` (`~145 µs` / `160 µs` en CAN-FD `5 Mbps`).
* **Critère d'acceptation :** charge **`<= 70 %` en typique** et **`<= 80 %` en pire cas**.

| Teensy | Port | Mode matériel | Moteurs affectés | Nb | Fréquence | Charge CAN 2.0B (typique / pire cas) | Si variante CAN-FD 5 Mbps |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Lower** | `CAN1` | CAN 2.0B | Hanche G (`RS-04` Pitch + `RS-03` Roll + `RS-03` Yaw) + Genou G (`RS-04`) | 4 | 500 Hz | 56 % / 64 % | – (port non FD) |
| **Lower** | `CAN2` | CAN 2.0B | Hanche D (`RS-04` Pitch + `RS-03` Roll + `RS-03` Yaw) + Genou D (`RS-04`) | 4 | 500 Hz | 56 % / 64 % | – (port non FD) |
| **Lower** | `CAN3` | Compatible FD | 4x `RS-03` cheville (cardans G + D) + `Waist Yaw RS-06` | 5 | 500 Hz | 70 % / 80 % *(limite)* | ~36 % / 40 % |
| **Upper** | `CAN1` | CAN 2.0B | Bras G (`RS-04` épaule pitch, `RS-03` roll, `RS-02` yaw, `RS-03` coude, `RS-10P` supination, `RS-00` poignet) | 6 | 250 Hz | 42 % / 48 % | – (port non FD) |
| **Upper** | `CAN2` | CAN 2.0B | Bras D (`RS-04` épaule pitch, `RS-03` roll, `RS-02` yaw, `RS-03` coude, `RS-10P` supination, `RS-00` poignet) | 6 | 250 Hz | 42 % / 48 % | – (port non FD) |
| **Upper** | `CAN3` | Compatible FD | Cou (`2x RS-05` Pan + Tilt) | 2 | 100 Hz | 6 % / 6 % | ~3 % |

*(Total : `27` moteurs RobStride. Pour les leviers de marge sur `CAN3 Lower` et le détail complet du calcul, voir [FINAL_CONSOLIDE_02_Electronique_et_Energie.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/02_Electronique_et_Energie/FINAL_CONSOLIDE_02_Electronique_et_Energie.md) §2.1.)*

---

## 3. Matériel et Architecture USB

L'architecture embarquée repose sur deux contrôleurs **Teensy 4.1 + shields SK Pang Triple CAN** reliés en USB (480 Mbps) à la Jetson Orin Nano via le hub USB. Les adaptateurs **CANable Pro** et **InnoMaker USB2CAN-C** ne sont plus utilisés sur le robot : ils sont réservés aux **tests et au debug sur banc**. Les anciens ponts `U2D2 / Dynamixel` ont été supprimés au profit de `ESP32-S3 + Waveshare 25514` pour les `16` servomoteurs Feetech des mains.

| Équipement connecté à la Jetson | Liaison | Rôle / Bus gérés | Nb d'axes |
| :--- | :--- | :--- | :---: |
| **Teensy 4.1 Lower** + SK Pang Triple CAN | USB via Hub | `CAN1` (Hanche/Genou G), `CAN2` (Hanche/Genou D), `CAN3` (4x Cheville + `Waist RS-06`) | 13 |
| **Teensy 4.1 Upper** + SK Pang Triple CAN | USB via Hub | `CAN1` (Bras G), `CAN2` (Bras D), `CAN3` (Cou `2x RS-05`) | 14 |
| **Sony Spresense** (`CXD5602PWBEXT1`) | USB via Hub (+ UART/D2 vers Teensy) | Watchdog, ADC `V_bat` / FSR, IMU `BMI270`, réflexe d'amortissement `< 1 ms` | – |
| **2x ESP32-S3 + Waveshare 25514** (Mains G/D) | USB via Hub | `16x` servos Feetech `STS3250 / HL-3915` (SCServo TTL) + capteurs tactiles eFlesh `MLX90393` | 16 |
| *Outils de banc (hors robot)* | USB vers PC / banc | `CANable Pro` / `InnoMaker USB2CAN-C` / Module debug série : config ID, OTA, mesure `candump` | – |

---

## 4. Câblage et Couleurs

* **Daisy-Chain :** Interdiction de faire des "Y" (étoiles), sauf dérivation `< 30 cm` pour le bus du cou (`RS-05` à 100 Hz). Les stubs doivent rester `< 30 cm`.
* **Ordre de chaînage `CAN3 Lower` :** `Teensy Lower (120 Ω shield)` -> `Waist Yaw RS-06` -> `Cheville G A (RS-03)` -> `Cheville G B (RS-03)` -> `Cheville D A (RS-03)` -> `Cheville D B (RS-03, terminaison 120 Ω en bout de bus)` (`~3,2 m` estimés `[À VALIDER au harnais]`).
* **Règle de contournement des moteurs (arbres pleins) :** Tous les moteurs RobStride (`RS-00` à `RS-06`, `RS-10P`) possèdent un arbre de sortie plein et un carter fermé. Tout câble CAN et puissance 48 V doit contourner les actionneurs (en particulier le `Waist RS-06` par le corridor ventral dédié) et ne jamais traverser l'axe d'un moteur.
* **Couleurs fils RobStride :**
  * **CAN_H** : Jaune
  * **CAN_L** : Blanc
  * **GND** : Noir
* **Masse commune :** Le fil `GND` CAN doit relier l'interface CAN à la borne `(-)` de référence commune.
