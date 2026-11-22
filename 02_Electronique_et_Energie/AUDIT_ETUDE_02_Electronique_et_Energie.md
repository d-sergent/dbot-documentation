# 🔍 Rapport d'Audit d'Ingénierie : 02 Électronique et Énergie (D-Bot)

> **Date de revue :** 22 novembre 2026  
> **Rôle :** Design Review — Ingénierie Électronique, Énergie, Bus Temps Réel & Sécurité  
> **Sources auditées (9 fichiers actifs du module 02) :**  
> `FINAL_CONSOLIDE_02_Electronique_et_Energie.md`, `FINAL_Bilan_Tensions.md`, `Bus_de_Donnees/FINAL_CAN_Bus_Topology.md`, `Power_Distribution/FINAL_Distribution_Arbre.md`, `Power_Distribution/STUDY_Batterie_NMC.md`, `Schemas_Cablage/FINAL_Solenoids_Wiring.md`, `STUDY_Motorisation_QDD_RobStride.md`, `STUDY_Watchdog_Robot.md`, `STUDY_Electronique_Historique.md`.  
> **Sources Niveau 1 de recoupement :**  
> `00_Architecture_Centrale/FINAL_CONSOLIDE_00_Architecture_Centrale.md` (~38,6-38,7 kg, 27 RobStride + 16 Feetech acquis à 100 %), `05_Gestion_Projet/FINAL_Liste_Achats_BOM.md`, `01_Mecanique_et_Chassis/Bras_et_Mains/AUDIT_ETUDE_Bras_et_Mains.md`, `01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Calculs_FEA_Torse_et_Bassin.md`.

---

## 📑 Sommaire

- [**0. Décision d'Architecture Retenue**](#0-décision-darchitecture-retenue)
- [**1. Vérification des Calculs Clés**](#1-vérification-des-calculs-clés)
  - [1.1 Bus CAN et Cervelet](#11-bus-can-et-cervelet)
  - [1.2 Chaîne de Sécurité, Batterie et Watchdog](#12-chaîne-de-sécurité-batterie-et-watchdog)
  - [1.3 Rails Secondaires, Câblage Puissance et Actionneurs](#13-rails-secondaires-câblage-puissance-et-actionneurs)
- [**2. Carte des Dépendances Inter-Membres**](#2-carte-des-dépendances-inter-membres)
- [**3. Manques Critiques & Incertitudes**](#3-manques-critiques-incertitudes)
- [**4. Propositions d'Amélioration**](#4-propositions-damélioration)
- [**5. Synthèse du Niveau de Maturité**](#5-synthèse-du-niveau-de-maturité)

---

## 0. Décision d'Architecture Retenue

| Choix de Conception | Spécification Retenue | Justification Technique | Source(s) |
| :--- | :--- | :--- | :--- |
| **Source Principale 48 V** | Batterie Li-ion NMC 13S 21700 (`46,8 V` nom., `54,6 V` max, `39,0 V` min, `10 Ah`) | Meilleure densité massique (`200-250 Wh/kg` vs `130-160 Wh/kg` LFP) ; approche en 2 phases (VAE puis sur-mesure torse) | `FINAL_CONSOLIDE_02`, `STUDY_Batterie_NMC.md`, `STUDY_Electronique_Historique.md` |
| **Distribution 48 V en Arbre** | Busbar central double 12 bornes M4 `150 A` -> troncs fusionnés par zone -> splitters locaux | Évite le chaînage XT30 (risque fusion sous forts pics `RS-04`), isole les fautes par membre et réduit le toron torse à 7 paires | `FINAL_Distribution_Arbre.md`, `STUDY_Electronique_Historique.md`, `FINAL_Liste_Achats_BOM.md` |
| **Rails Secondaires Régulés** | `19 V / 5 A` (Jetson), `12 V Logique / 10 A` (Hub/Solénoïdes), `12 V Puissance` (`2x DROK 25 A` mains), `5 V Always-On / 5 A` (Spresense) + LDO `3,3 V` | Isole la logique sensible et la Jetson des appels de courant transitoires des 16 servomoteurs de mains et des 27 moteurs | `FINAL_Bilan_Tensions.md`, `FINAL_CONSOLIDE_02`, `FINAL_Liste_Achats_BOM.md` |
| **Cervelet & Bus Moteurs** | Architecture cible **2x Teensy 4.1 + 2x Shields SK Pang Triple CAN FD** (6 bus CAN FD, lien USB `480 Mbps` vers Jetson, RJ45 en réserve V2) | Remplace les adaptateurs USB-CAN `InnoMaker + 4x CANable Pro` pour garantir le déterminisme temps réel Upper/Lower Body | `FINAL_CONSOLIDE_02` (§1-§2), `FINAL_Liste_Achats_BOM.md` (§3) |
| **Supervision & Sécurité** | Sony Spresense Always-On (`CXD5602PWBEXT1`, watchdog + ADC `V_bat`/FSR + IMU `BMI270` 416 Hz + ligne `D2 -> Pin 2` Teensy < 1 ms), E-Stop NC, 2x `LEX-SOLEN-04` + `D4184` | Réaction matérielle aux chutes indépendante de Linux/Jetson et verrouillage mécanique passif du Tilt de tête | `STUDY_Watchdog_Robot.md`, `FINAL_Solenoids_Wiring.md`, `FINAL_CONSOLIDE_02` (§5.1) |
| **Motorisation QDD & Mains** | 27 actionneurs RobStride `48 V` (`15-60 V` admissible, `RS-01` 36 V exclu) + 16 servos Feetech `STS3250`/`HL-3915` (`12 V` SCServo TTL via `ESP32-S3` + `Waveshare 25514`) | Réversibilité (backdrivability), contrôle d'impédance sans capteur d'effort externe sur les membres et grip continu `140 N` sur les mains | `STUDY_Motorisation_QDD_RobStride.md`, `FINAL_CONSOLIDE_00`, `FINAL_Liste_Achats_BOM.md` |

---

## 1. Vérification des Calculs Clés

### 1.1 Bus CAN et Cervelet

1. **Saturation du bus CAN 2.0B à 1 Mbps sur 6 moteurs à 1 kHz**
   * **Sources :** `FINAL_CAN_Bus_Topology.md` (§2), `STUDY_Electronique_Historique.md` (§2).
   * **Calcul déclaré :** `6 moteurs * 1 000 Hz * 130 bits/trame = 780 kbps = 78 %` de charge sur un bus à `1 Mbps`.
   * **Recalcul physique (bidirectionnel) :** Les actionneurs RobStride en boucle MIT émettent **une trame de retour (RX)** pour chaque trame de commande (TX), soit `2` trames étendues 29 bits par moteur et par cycle (`128 à 150 bits` avec bit-stuffing) :
     * TX seul à `1 kHz` : `6 * 1 000 * 130 = 780 kbps` (`78 %`).
     * TX + RX à `1 kHz` (`130 bits/trame`) : `6 * 2 * 1 000 * 130 = 1 560 kbps` (**156 % de saturation**).
     * TX + RX à `1 kHz` (`150 bits/trame` avec stuffing) : `6 * 2 * 1 000 * 150 = 1 800 kbps` (**180 % de saturation**).
     * TX + RX à `500 Hz` : `6 * 2 * 500 * 130 = 780 kbps` (`78 %`, montant à `900 kbps = 90 %` à `150 bits/trame`).
   * **Hypothèse implicite :** Le calcul des documents ne prenait en compte que la moitié du trafic (TX seul). En CAN 2.0B à `1 Mbps`, la boucle à `1 kHz` sur 6 moteurs est **physiquement impossible**.
   * **Statut & Criticité :** 🔴 **BLOQUANT** — Impose soit d'activer **CAN-FD (2 à 5 Mbps sur la phase data)** via les shields `SK Pang Triple CAN FD` + Teensy 4.1 (vérifier la compatibilité CAN-FD réelle de chaque génération de firmware RobStride déjà reçue, certains modèles étant livrés en CAN 2.0B `1 Mbps` ou nécessitant une mise à jour/paramétrage CAN-FD), soit de plafonner les bus en CAN 2.0B à `400-500 Hz` (ou `<= 3 moteurs` par bus pour `1 kHz`).

2. **Contradiction architecturale CAN/USB et omission du 27e moteur (`Waist Yaw RS-06`)**
   * **Sources :** `FINAL_CAN_Bus_Topology.md` (§2-§3), `FINAL_CONSOLIDE_02` (§1-§3), `STUDY_Electronique_Historique.md` (§2), vs `FINAL_CONSOLIDE_00` (§2.1).
   * **Vérification du comptage :**
     * Topologie historique documentée : `2 (Cou) + 6 (Bras G) + 6 (Bras D) + 6 (Jambe G) + 6 (Jambe D) = 26 moteurs` (sans Waist Yaw).
     * Inventaire réel acquis (`FINAL_CONSOLIDE_00`) : `2 (Cou) + 12 (Bras) + 1 (Waist Yaw RS-06) + 12 (Jambes) = 27 moteurs RobStride`.
     * Architecture Teensy 4.1 : `2` cartes x `3` ports = **`6` bus CAN-FD disponibles** (contre `5` bus listés précédemment sur `InnoMaker + 4x CANable`), tandis que `FINAL_CONSOLIDE_02` (§3) conserve `CANable Pro x4`, `InnoMaker` et `câbles CANable` dans la BOM et indique dans le texte *"sans les CANable"*. De même, `U2D2 x2` (Dynamixel) reste dans les schémas alors que les mains utilisent `ESP32-S3 + Waveshare 25514` pour `16x Feetech`.
   * **Statut & Criticité :** 🔴 **BLOQUANT** — Affecter explicitement `Waist Yaw RS-06` (par ex. sur le 6e bus Teensy ou partagé sur le Bus Cou à seulement `2 + 1 = 3` moteurs = `39 % TX+RX` à `1 kHz` même en CAN 2.0B) et trancher la BOM active.

---

### 1.2 Chaîne de Sécurité, Batterie et Watchdog

3. **Pont diviseur batterie (`150 kOhm / 10 kOhm`) et bug de conversion ADC (`5,0 V` vs `3,3 V`)**
   * **Sources :** `STUDY_Watchdog_Robot.md` (§2-§3, lignes 66-70 & 101-117), `FINAL_CONSOLIDE_02` (§2, §5.1, §6 n°8).
   * **Calcul matériel vérifié :**
     * Ratio : `(R1 + R2) / R2 = (150 000 + 10 000) / 10 000 = 16,0`.
     * `V_out = V_bat / 16` : à `39,0 V` (seuil bas 13S) -> `2,438 V` ; à `46,8 V` (nominal) -> `2,925 V` ; à `54,6 V` (pleine charge) -> **`3,413 V`** ; à `55,0 V` -> **`3,438 V`** ; en pic régénératif à `58,0 V` -> **`3,625 V`**.
   * **Défaut 1 (Surtension ADC) :** `FINAL_CONSOLIDE_02` (§5.1) impose impérativement le jumper Spresense Extension Board sur **`3,3 V`** pour ne pas détruire les broches du Teensy 4.1. Or `V_out` dépasse `3,3 V` dès `V_bat > 52,8 V` (`3,413 V` en fin de charge normale `54,6 V`), saturant l'ADC et exposant l'entrée analogique `A0`.
   * **Défaut 2 (Bug logiciel C++) :** Dans `STUDY_Watchdog_Robot.md` (ligne 114), le code calcule `vOut = (raw * 5.0) / 1023.0` (référence `5,0 V`) sur une carte configurée à `3,3 V`, introduisant une erreur de `+51,5 %` (`5,0 / 3,3 = 1,5152`). Au seuil critique réel `V_bat = 39,0 V` (`V_out = 2,438 V`, `raw = 756`), le firmware lit **`59,12 V`** -> **la protection décharge profonde ne se déclenche jamais !** (De plus, sur la Spresense, il faut aussi vérifier la plage native du CAN sur `A0` de l'Extension Board : `3,3 V` vs `5,0 V` selon le cavalier `CN1` et le pont de mesure embarqué).
   * **Recalcul dimensionnement sûr :** Avec `R1 = 180 kOhm, R2 = 10 kOhm` (`ratio = 19,0`), `54,6 V -> 2,874 V` et `60,0 V -> 3,158 V` (avec `R1 = 200 kOhm, R2 = 10 kOhm`, `ratio = 21,0` -> `54,6 V -> 2,600 V` et `60,0 V -> 2,857 V`), protégé par Zener `3,3 V` + condensateur de filtrage `100 nF` sur `A0` et constante `3,3 V` dans le code.
   * **Statut & Criticité :** 🔴 **BLOQUANT** — Risque cumulé de surtension ADC et de destruction par décharge profonde des packs NMC.

4. **Logique défaillante du Watchdog Heartbeat sur niveau statique `HIGH`**
   * **Sources :** `STUDY_Watchdog_Robot.md` (§3, lignes 151-162).
   * **Code analysé :** `if (digitalRead(PIN_HEARTBEAT) == HIGH) { lastHeartbeat = millis(); }` avec `WATCHDOG_TIMEOUT = 5000 ms`.
   * **Vérification :** Si la Jetson subit un gel système (kernel panic ou blocage logiciel) au moment où sa broche GPIO est à l'état `1` logique (`HIGH`), `PIN_HEARTBEAT` reste figée à `HIGH`, `lastHeartbeat` est réinitialisé toutes les `100 ms` et le watchdog ne se déclenchera **jamais**.
   * **Statut & Criticité :** 🔴 **BLOQUANT** — Remplacer impérativement par une détection de changement d'état (front montant/descendant sur signal carré, par ex. `1 Hz` ou `10 Hz`) et vérifier l'absence de verrouillage sur `LOW` ou `HIGH`.

5. **Inadéquation matérielle du Switch `BTS50085` et erreur de topologie E-Stop**
   * **Sources :** `FINAL_CONSOLIDE_02` (§2, §5.2 étape 9), `STUDY_Watchdog_Robot.md` (§2, lignes 71-75), `STUDY_Electronique_Historique.md` (§4.2, §4).
   * **Vérification composants & topologie :**
     * `FINAL_CONSOLIDE_02` décrit un `BTS50085` de `100 V, 5 A` comme interrupteur principal 48 V des moteurs et de la Jetson. En fiche technique Infineon, le `BTS50085-1TMA` est un PROFET haute-côté limité à **`58 V` max absolu (`V_bb` max)** et `~44 A` nominal : il est sous-dimensionné en courant face au fusible principal `80 A` (et aux `2x 50 A` des jambes) et sans marge face aux pics régénératifs (> `58 V`) au-delà d'une batterie `13S` à `54,6 V`.
     * Sur le schéma `STUDY_Electronique_Historique.md` (lignes 90-98 et 517), le bouton **E-Stop** est câblé **entre le fusible principal `80 A` et le busbar central**, d'où partent aussi les convertisseurs `48V->19V` (Jetson) et `48V->5V` (Spresense). Dans cette topologie, appuyer sur l'E-Stop coupe **aussi** la Jetson et la Spresense, en contradiction avec la spécification (*"coupure alimentation moteurs, PAS Jetson"*).
   * **Statut & Criticité :** 🔴 **BLOQUANT** — Le départ `48 V Logique Always-On` (Spresense + Jetson) doit être dérivé **en amont** du contacteur/E-Stop puissance moteurs (derrière son propre fusible), et la coupure puissance `48 V / >= 100 A` doit utiliser un relais statique / contacteur DC haute tension (`Kilovac` / `Song Chuan`) ou un banc MOSFET back-to-back `100 V` avec résistance de précharge.

6. **Batterie 13S vs 12S, bilan énergétique (`468 Wh` vs `480 Wh`) et BMS `30 A`**
   * **Sources :** `STUDY_Batterie_NMC.md` (§1-§3), `FINAL_CONSOLIDE_02` (§1-§2), `STUDY_Electronique_Historique.md` (§4.2), vs `STUDY_Motorisation_QDD_RobStride.md` (§2.1), `STUDY_Watchdog_Robot.md` (ligne 8).
   * **Recalcul batterie 13S Li-ion NMC :**
     * Tension nominale : `13 * 3,6 V = 46,8 V` ; pleine charge : `13 * 4,2 V = 54,6 V` ; coupure basse (`3,0 V/cellule`) : `39,0 V`.
     * Énergie réelle 1 pack `10 Ah` : `46,8 V * 10 Ah = 468 Wh` (les documents affichent `480 Wh` calculés à `48 V`, soit un léger écart de `+2,5 %`). Avec 80 % de profondeur de décharge utile (`374 Wh`), l'autonomie pour 1 pack est de **`~75 min` à `300 W`**, **`~45 min` à `500 W`**, **`~28 min` à `800 W`**.
     * Traces résiduelles `12S` dans `STUDY_Motorisation_QDD_RobStride.md` (`50,4 V`) et `STUDY_Watchdog_Robot.md` (ligne 8) : écart nominal `-7,69 %` (`43,2 V` vs `46,8 V`), mais la limite `54,6 V` (13S) + surtensions régénératives confirme bien l'élimination du `RS-01` (`48 V max`) au profit des `RS-02..RS-10P` (`60 V max`).
   * **Incohérence BMS :** Le BMS prototype spécifié à **`30 A continu / 50 A pic`** dans `FINAL_CONSOLIDE_02` (§2-§3) est inférieur au fusible principal (`80 A`) et à un seul tronc de jambe (`50 A`) -> il coupera intempestivement le robot complet dès qu'une jambe et un bras solliciteront plus de `1,4 kW` instantanés (chute immédiate du bipède).
   * **Statut & Criticité :** 🔴 **BLOQUANT** — Exiger un BMS `13S >= 50 A continu / 100 A pic` dès le pack Phase 1 (ou brider explicitement le courant total par logiciel sous `25-30 A` en phase d'essais statiques).

---

### 1.3 Rails Secondaires, Câblage Puissance et Actionneurs

7. **Sous-dimensionnement du fusible Tronc Logique (`5 A`) face à la puissance des convertisseurs**
   * **Sources :** `FINAL_Distribution_Arbre.md` (§1), `FINAL_Bilan_Tensions.md` (§1), `STUDY_Electronique_Historique.md` (§4.1 & §4.2).
   * **Recalcul de puissance et courant côté 48 V (rendement buck `eta = 0,90`) :**
     * Puissance cumulée maximale des 4 rails : `95 W (19 V) + 120 W (12 V Log.) + 240 W (12 V Pwr) + 25 W (5 V) = 480 W`.
     * Courant 48 V si tous les bucks étaient sur ce départ : `480 / (46,8 * 0,90) = 11,40 A` (et **`13,68 A`** à `39,0 V`).
     * Même sur le périmètre `Logique` (`19 V 95 W + 12 V Logique 120 W + 5 V 25 W = 240 W`) : `I_48V = 240 / (46,8 * 0,90) = 5,70 A` (et **`6,84 A`** à `39,0 V`) -> **dépasse le fusible `5 A`** !
     * Si seuls `19 V + 5 V` (`120 W`) sont sur le tronc Logique (`12 V Logique` alimenté séparément) : `I_48V = 2,85 A` à `46,8 V` (`3,42 A` à `39,0 V`), mais la marge sous `5 A` reste faible face aux appels capacitifs à l'allumage (inrush).
   * **Statut & Criticité :** 🔴 **BLOQUANT** — Passer le départ Logique à **`10 A`** (en séparant clairement sur le busbar ce qui va vers `19 V`, `12 V Logique` et `5 V`) avec fil `16-18 AWG`.

8. **Bilan Thermique Statique RS-03 vs RS-04 et distinction Courant de Phase vs Courant Bus DC**
   * **Source :** `STUDY_Motorisation_QDD_RobStride.md` (§2.1).
   * **Recalcul à couple statique `T = 20,6 N.m` (posture fléchie) :**
     * `RS-03` (`R = 0,39 Ohm`, `Kt = 2,36 N.m/A`) : `I_q = 20,6 / 2,36 = 8,73 A` (doc `~8,5 A`) -> `P = 0,39 * 8,73^2 = 29,71 W` (avec `8,5 A` : `28,18 W`, doc `~28 W`).
     * `RS-04` (`R = 0,16 Ohm`, `Kt = 2,10 N.m/A`) : `I_q = 20,6 / 2,10 = 9,81 A` (doc `~9,5 A`) -> `P = 0,16 * 9,81^2 = 15,40 W` (avec `9,5 A` : `14,44 W`, doc `~14,5 W`).
   * **Hypothèse non explicitée & clarification physique :**
     * La formule suppose une résistance équivalente monophasée compatible avec `P = R * I^2` (si `R` est une résistance phase-à-phase, la puissance Joule triphasée réelle peut différer selon la convention `I_q`).
     * Ces `9,81 A` sont le **courant de phase Q-axis**, et non le courant DC tiré sur la batterie `48 V`. À vitesse nulle (`0 rpm`), 4x `RS-04` dissipent `4 * 15,40 = 61,6 W` de pertes Joule, soit seulement `61,6 / 46,8 ~ 1,32 A` tirés sur le bus batterie (+ pertes ESC).
   * **Statut & Criticité :** 🟠 **IMPORTANT** — Arithmétique cohérente (`-48 %` de chauffe en passant au `RS-04`), mais requiert une mesure thermique réelle en atelier (thermocouple sur les flasques CNC 7075-T6 pendant 10 min debout) et la vérification de `R` dans les manuels PDF `Manuels/RS04User Manual260713.pdf`.

9. **Chutes de tension cuivre (`< 0,2 V`), `12 AWG` absent de la BOM et connecteurs `XT30` sur `RS-04`**
   * **Sources :** `FINAL_Distribution_Arbre.md` (§1-§2), `FINAL_CONSOLIDE_02` (§3-§4), `STUDY_Electronique_Historique.md` (§4, §4b), `FINAL_Liste_Achats_BOM.md` (§2).
   * **Recalcul exact (`rho_Cu = 0,0172 Ohm*mm^2/m`, longueur boucle aller + retour `2 * L`) :**
     * Tronc Jambe `12 AWG` (`3,31 mm^2`, `L = 0,30 m`, `I = 50 A`) : `R = 3,12 mOhm`, `dV = 0,156 V`, `P = 7,79 W` -> conforme `< 0,2 V`, **MAIS le `12 AWG` n'apparaît dans aucune ligne d'achat des BOM !**
     * Tronc Bras `14 AWG` (`2,08 mm^2`, `L = 0,40 m`, `I = 30 A`) : `R = 6,62 mOhm`, `dV = 0,198 V`, `P = 5,95 W` -> juste à la limite `0,2 V`.
     * Genou `RS-04` `14 AWG` (`L = 0,60 m`) : à `22 A` (`dV = 0,218 V`, `4,80 W`) acceptable ; en revanche, si un pic moteur atteint `90 A` (affirmé dans `STUDY_Electronique_Historique.md` ligne 491 vs `22 A crête` ligne 736), `dV = 0,893 V`, `P = 80,4 W` et le **connecteur XT30** (`STUDY_Electronique_Historique.md` lignes 610/624/699, limité à `15 A` continu / `30 A` court terme) fond !
     * Cheville `RS-03` `18 AWG` (`0,823 mm^2`, `L = 0,80 m`, `I = 15 A` crête) : `R = 33,44 mOhm`, `dV = 0,502 V`, `P = 7,52 W` -> **dépasse le seuil `< 0,2 V`** revendiqué en simulation `FINAL_CONSOLIDE_02` (§4).
   * **Statut & Criticité :** 🟠 **IMPORTANT** — Ajouter du `12 AWG` en BOM, passer les deux câbles chevilles longs (`0,8 m`) en `16 AWG` (`dV` réduite à `~0,31 V`) ou `14 AWG`, et clarifier le courant crête réel `RS-04` (`XT60` obligatoire au lieu de `XT30` sur pigtails/moteurs si `I_pic > 30 A`, ou vérification du connecteur natif réel reçu sur nos `RS-04`).

10. **Bilan courant Mains (Feetech acquis vs ancien calcul Dynamixel) et architecture Buck `12 V`**
    * **Sources :** `FINAL_Bilan_Tensions.md` (§2), `STUDY_Electronique_Historique.md` (§4.1), `FINAL_CONSOLIDE_02` (§2), vs `FINAL_Liste_Achats_BOM.md` (§2-§5.1) et `AUDIT_ETUDE_Bras_et_Mains.md` (§1.8, §2).
    * **Recalcul :**
      * Ancien chiffrage conservé dans `02/` : `16 * 1,14 A = 18,24 A` (`~18,2 A` Dynamixel `XC430/XC330`) derrière 1 buck unique `20 A`.
      * Matériel réel acquis (2 mains D-Hand Hybrid = `10x STS3250 + 6x HL-3915`) : `2 * 8,5 A = 17,0 A` nominal (`204 W`), **`2 * 12,0 A = 24,0 A` en grip soutenu (`288 W`)**, et jusqu'à `51 A` (`612 W`) en blocage sans bridage firmware. Un buck central unique `20 A` serait en surcharge dès un grip simultané des deux mains.
      * Solution déjà réceptionnée dans `FINAL_Liste_Achats_BOM.md` : **`2x DROK 48V->12V 25 A` (1 par bras = `50 A` cumulés, `300 W/bras`, protégés par `PTC 15 A`)**.
    * **Statut & Criticité :** 🟠 **IMPORTANT** — Mettre à jour `FINAL_Bilan_Tensions.md` et `FINAL_CONSOLIDE_02` pour supprimer les références Dynamixel/`U2D2` et acter les `2x DROK 25 A` + `PTC 15 A`.

11. **Oubli de 3 moteurs (`RS-06` + `2x RS-10P`) dans les métrés câbles `18 AWG`**
    * **Source :** `STUDY_Electronique_Historique.md` (§4b, lignes 761-787).
    * **Vérification des sommes :**
      * `14 AWG` : `2*0,5 + 2*0,3 + 2*0,6 = 2,8 m` (`+30 % = 3,64 m` -> bobine `5 m` suffisante pour les 6 `RS-04`, hors troncs `14 AWG` bras qui consomment ~`0,8 m` additionnels -> `4,44 m / 5 m`, marge très serrée).
      * `18 AWG` : `2*0,4 + 2*0,8 + 2*0,55 + 2*0,7 + 2*0,55 + 4*0,25 + 4*0,65 = 9,6 m` (`+30 % = 12,48 m`), MAIS ce décompte porte sur **`18` moteurs (`18 + 6 = 24`)**, alors que le robot complet compte **`27` moteurs RobStride** (il manque `1x Waist Yaw RS-06` + `2x RS-10P` supination avant-bras, et le coude est toujours noté `RS-06` au lieu de `RS-03`).
    * **Statut & Criticité :** 🟠 **IMPORTANT** — Recalculer sur les 27 moteurs réels (`21` moteurs hors `RS-04`, soit ~`11,2 m` bruts / `~14,6 m` avec marge 30 % par couleur — la bobine de `15 m` devient limite).

12. **Solénoïdes de tête `LEX-SOLEN-04` (`1,2 A` vs `2 A`) et banc Wanptek (`4,63 A <= 5 A`)**
    * **Sources :** `FINAL_Solenoids_Wiring.md` (§1-§2), `FINAL_Bilan_Tensions.md` (§2), `STUDY_Electronique_Historique.md` (§4.4 & §6).
    * **Recalcul :**
      * Solénoïdes : `2 * 0,6 A = 1,2 A` (`14,4 W` à `12 V`) -> provision de `2 A` dans `FINAL_Bilan_Tensions.md` valide (`+67 %` de marge). **Toutefois**, le schéma ASCII de `FINAL_Solenoids_Wiring.md` (lignes 33-49) représente les deux solénoïdes et leurs deux diodes `1N4007` en cascade verticale ambiguë ressemblant à un montage série alors que le texte impose un branchement parallèle.
      * Banc Wanptek avant-bras : `2,0 + 1,0 + 0,8 + (12 V * 3 A / 48 V / 0,90) = 2,0 + 1,0 + 0,8 + 0,83 = 4,63 A <= 5,0 A` (calcul mathématique juste, mais à actualiser pour refléter `RS-03 + RS-10P + RS-00` + servos Feetech).
    * **Statut & Criticité :** 🟡 **À SURVEILLER** — Clarifier le schéma ASCII parallèle des solénoïdes pour éviter un montage en série à l'atelier (sous `6 V`, les solénoïdes ne débloqueraient pas).

---

## 2. Carte des Dépendances Inter-Membres

* **[Masse batterie 13S (`2,3-4,6 kg`) & support central]** -> **[01 Torse & Bassin]** -> Impacte directement le CoG torse (`Z = 1290 mm`), le moment d'arrêt d'urgence E-Stop (`140 N.m`) calculé en FEA et le dimensionnement de l'interface batterie (`M4x18`, aimants quick-swap).
* **[27 actionneurs RobStride à arbres pleins sans perçage traversant + lacet Waist `+/- 80 deg` / `+/- 95 deg`]** -> **[01 Torse & Bassin]** -> Tous les harnais 48 V et CAN-FD traversant le Waist doivent contourner le `RS-06` par le corridor ventral ouvert en U (`45 x 20 mm`) avec boucle de service libre (`150-200 mm`), torsion linéique `<= 0,6-1,0 deg/mm` et rayon de courbure `>= 10 * D_cable`.
* **[Migration vers 2x Teensy 4.1 Triple CAN FD (6 bus) via USB/Ethernet]** -> **[03 Intelligence & Logiciel]** -> Rend caducs les anciens pilotes directs `SocketCAN / gs_usb` de la Jetson (`kbot_motor_control`) et impose un protocole temps réel Jetson <-> Teensy.
* **[Cavalier GPIO Spresense bloqué sur `3,3 V` pour protéger les Teensy 4.1]** -> **[02 Chaîne ADC & 04 Perception]** -> Rend le diviseur batterie `150 kOhm / 10 kOhm` critique au-delà de `52,8 V` et impose de vérifier les niveaux logiques de tous les périphériques I2C/UART reliés à la Spresense.
* **[Pertes Joule statiques `15,4 W / RS-04` (hanches/genoux)]** -> **[01 Jambes & Torse]** -> Exige un contact thermique franc sur les brides/plaques usinées CNC `7075-T6` pour éviter la dérive thermique et l'activation de la protection moteur.
* **[Alimentation `2x DROK 25 A` + `ESP32-S3` + `Waveshare 25514` sur chaque bras]** -> **[01 Bras & Mains]** -> Impose l'intégration physique de ces 3 modules dans les ~200 mm d'avant-bras (remplace le buck central `20 A` et les `U2D2`).
* **[Budget courant USB & `12 V Logique` (OAK-D ~900 mA, ReSpeaker ~300 mA, L2 futur 0,5-1 A, 2x Teensy, Spresense)]** -> **[03 Jetson & 04 Perception]** -> Nécessite un hub USB alimenté dédié `>= 3-5 A @ 5 V` (via `12 V Logique`) pour éviter les déconnexions USB en charge IA/audio.
* **[Capacité BMS batterie (`30 A` prototype vs `>= 50-100 A` dynamique)]** -> **[01 Jambes & 03 Locomotion RL]** -> Limite directement les accélérations admissibles, les gains `Kp/Kd` et l'enveloppe de couple dynamique autorisée avant coupure BMS.
* **[Nombre de canaux analogiques nécessaires (`8 FSR + V_bat + thermistances >= 13`) vs `6 ADC` Spresense]** -> **[01 Pieds & 04 Équilibre]** -> Impose soit le regroupement matériel 2x2 des FSR par pied, soit l'ajout d'un multiplexeur I2C (`ADS1115`).
* **[Ligne d'interruption matérielle `Spresense D2 -> Teensy Pin 2` (`< 1 ms`)]** -> **[03 Contrôle / Locomotion]** -> Permet le passage instantané des 27 moteurs en mode amorti (Damping) lors d'une chute ou perte heartbeat sans attendre la boucle Linux de la Jetson.

---

## 3. Manques Critiques & Incertitudes

1. 🔴 **Double architecture CAN non réconciliée & omission de `Waist Yaw RS-06`**
   * *Contexte :* Coexistence dans le même dossier de `2x Teensy 4.1 Triple CAN FD` (`FINAL_CONSOLIDE_02`), `1x InnoMaker + 4x CANable Pro` (`FINAL_CAN_Bus_Topology.md`) et `2x U2D2 Dynamixel` (`STUDY_Electronique_Historique.md`), avec seulement 26 moteurs routés sur 27 réels.
   * *Risque :* Câblage réel incompatible avec le logiciel embarqué, harnais Waist non routé sur un bus CAN dédié, perte de temps en atelier.
   * *Action :* Mettre à jour `FINAL_CAN_Bus_Topology.md` pour figer l'affectation exacte des 6 ports CAN FD des 2 Teensy 4.1 sur les 27 RobStride et supprimer les références `CANable`/`U2D2`/`Dynamixel`.

2. 🔴 **Absence de protection contre les surtensions de freinage régénératif (module de décharge) & de précharge**
   * *Contexte :* Aucun circuit anti-étincelle (précharge) ni étage dissipateur régénératif (shunt / module de décharge type `Manuels/Discharge Module User Manual V1.0.pdf`, pourtant présent dans les manuels du dépôt !) n'est intégré dans les schémas 48 V.
   * *Risque :* Au branchement du pack `54,6 V`, arc destructeur sur les connecteurs et appel capacitif sur les 27 ESC + 5 bucks ; lors d'un freinage dynamique de jambe (`RS-04`), remontée de tension bus `> 60 V` détruisant les convertisseurs DC-DC (`V_in_max = 60 V`) et le switch `BTS50085`.
   * *Action :* Intégrer le module de décharge/freinage régénératif sur le busbar puissance, valider la tenue `V_in >= 60-72 V` des bucks et imposer `XT90-S` (anti-spark) ou `Anderson SB50` + circuit de précharge.

3. 🔴 **Saturation des 6 entrées ADC de la Spresense (`6` entrées pour `10 à 15` capteurs)**
   * *Contexte :* `STUDY_Watchdog_Robot.md` et `STUDY_Electronique_Historique.md` (§5) demandent `8` FSR (4 par pied) + `1` mesure `V_bat` + des thermistances sur les `RS-04` (`4 à 6` canaux), alors que `CXD5602PWBEXT1` ne possède que `6` broches analogiques (`A0` à `A5`).
   * *Risque :* Impossibilité matérielle de câbler simultanément tous les capteurs plantaires CoP et la surveillance thermique.
   * *Action :* Trancher entre l'option A (2 canaux FSR parallélisés par pied = 4 ADC) et l'ajout d'ADC I2C externes (`ADS1115`) pour libérer les broches analogiques.

4. 🟠 **Références commerciales manquantes (`[À COMPLÉTER]`) pour les convertisseurs logiques & switch haute-côté**
   * *Contexte :* `FINAL_CONSOLIDE_02` (§2-§3 et §6) laisse sans SKU exact les bucks `48V->19V 5A`, `48V->12V 10A`, `48V->5V 5A` et le switch de coupure puissance.
   * *Risque :* Achat d'un module DC-DC non isolé ou limité à `48-50 V` en entrée qui grille dès la pleine charge `13S` (`54,6 V`).
   * *Action :* Sélectionner uniquement des convertisseurs industriels certifiés `V_in >= 60-75 V` (ex. série `Mean Well DDR-120C` / `DDR-15G` / `DDR-60G`) et compléter la BOM.

5. 🟠 **Incohérence `12 AWG` manquant en BOM & connecteurs `XT30` vs courant crête réel `RS-04`**
   * *Contexte :* `FINAL_Distribution_Arbre.md` spécifie des troncs Jambes en `12 AWG`, absents des BOM d'achat, et des pigtails `XT30` sur `RS-04` alors que les documents citent alternativement `22 A` crête et `90 A` pic pour le `RS-04`.
   * *Risque :* Échauffement excessif ou fusion connecteur sur les membres inférieurs lors d'impacts dynamiques.
   * *Action :* Vérifier le courant de phase vs DC bus maximal réel dans `Manuels/RS04User Manual260713.pdf` et inspecter la prise réelle des moteurs `RS-04` en atelier.

6. 🟠 **Fichiers CAO listés `✅ Modélisé` inexistants sur le dépôt**
   * *Contexte :* `FINAL_CONSOLIDE_02` (§4) référence 8 fichiers (`02_Elec_Busbar.step`, `CANable_Cluster.step`, `Power_Wiring_48V.iam`, etc.) qui n'existent ni dans `02_Electronique_et_Energie/` ni dans les dossiers actifs inspectés.
   * *Risque :* Impression 3D ou routage harnais sans géométrie validée.
   * *Action :* Exporter les vrais modèles CAO électroniques depuis Fusion 360 vers `Exports_CAO_DBot/` ou marquer ces livrables `[EN COURS]` dans `FINAL_CONSOLIDE_02`.

7. 🟡 **Perte de l'isolation galvanique `2,5 kV` lors du passage aux 2x Teensy 4.1**
   * *Contexte :* Les anciens `CANable Pro` apportaient une isolation galvanique `2,5 kV` entre le bus 48 V moteurs et le port USB de la Jetson ; les shields `SK Pang Triple CAN FD` pour Teensy 4.1 utilisent des transceivers CAN non isolés partageant la masse puissance/logique.
   * *Risque :* Boucle de masse, bruit EMI sur USB 3.0 (OAK-D/audio) ou remontée de transitoire 48 V vers la Jetson en cas de défaut masse.
   * *Action :* Ajouter un isolateur USB (`ADuM3160` / `ADuM4160`) entre le hub et chaque Teensy, ou un isolateur numérique sur la ligne UART/Interrupt Spresense <-> Teensy.

8. 🟡 **Absence d'essai physique d'échauffement en régime stationnaire et de vérification du faisceau CAN torsadé en torsion**
   * *Contexte :* Aucun essai thermique 10 min debout (`< 55 deg C`) ni test de tenue mécanique `+/- 95 deg` du harnais Waist n'a encore été enregistré.
   * *Action :* Exécuter le protocole de test thermique avec thermocouple + contrôle d'erreurs CAN (`candump` / compteurs `ERR` Teensy) sous mouvement cyclique du Waist.

---

## 4. Propositions d'Amélioration

| Priorité (Ratio Bénéfice / Complexité) | Proposition Chiffrée & Action Concrète | Impact Technique & Gains Attendus |
| :--- | :--- | :--- |
| **1. Très Haut / Faible** | **Corriger le diviseur batterie et le firmware Spresense** (`STUDY_Watchdog_Robot.md`) : remplacer `150 kOhm / 10 kOhm` par `180 kOhm / 10 kOhm` (`1 %`, `V_out = 2,87 V` à `54,6 V` et `3,16 V` à `60,0 V`) + Zener `3,3 V` + capa `100 nF`, corriger la constante `5.0 -> 3.3` en C++ et passer la détection heartbeat sur **front (changement d'état)** à `2-10 Hz`. | Élimine 100 % du risque de destruction d'entrée ADC à pleine charge et restaure deux fonctions vitales (coupure décharge profonde à `39,0 V` et reboot anti-freeze Jetson). Coût < 2 EUR. |
| **2. Très Haut / Faible** | **Réconcilier un schéma unique Module 02 aligné sur le stock réel** : acter dans `FINAL_CONSOLIDE_02`, `FINAL_CAN_Bus_Topology.md` et `FINAL_Bilan_Tensions.md` la topologie `2x Teensy 4.1 + 2x SK Pang Triple CAN FD` (6 bus incluant `Waist Yaw RS-06`), les `2x DROK 25 A` mains Feetech, les `ESP32-S3 + Waveshare 25514`, et supprimer toutes mentions obsolètes (`CANable`, `U2D2`, `Dynamixel`, `12S`). | Supprime toutes les contradictions inter-documents pour le câblage en atelier et unifie la base de vérité LightRAG avant les achats restants. |
| **3. Très Haut / Moyenne** | **Dissocier physiquement le bus `48 V Logique Always-On` du bus `48 V Puissance` + intégrer le module de décharge** : piquer les bucks `19 V` (Jetson) et `5 V` (Spresense) **en amont** de l'E-Stop avec un fusible dédié `10 A`, et monter derrière l'E-Stop un contacteur DC `>= 100 A` (en remplacement du `BTS50085`) + précharge + `Discharge Module V1.0` réglé vers `56-58 V`. | Garantit que l'E-Stop ne coupe jamais la Jetson ni la Spresense, absorbe les pics régénératifs `< 60 V` et élimine l'arc d'allumage. |
| **4. Haut / Faible** | **Activer CAN-FD (ou plafonner à `500 Hz` en CAN 2.0B) et isoler l'USB des Teensy** : placer le bus Cou (`2x RS-05`) + `Waist Yaw RS-06` sur un des 6 bus Teensy (`3` moteurs = `39 %` TX+RX à `1 kHz` même en CAN 2.0B), passer les 4 bus membres en CAN-FD `2-4 Mbps` si supporté par les moteurs reçus (sinon `500 Hz`), et insérer `2x` isolateurs USB `ADuM3160` devant les Teensy. | Supprime la saturation mathématique `156-180 %` du bus CAN à `1 kHz` et rétablit l'isolation galvanique entre puissance `48 V` et Jetson. |
| **5. Haut / Faible** | **Compléter la BOM câblage et capteurs** : ajouter `2-3 m` de silicone `12 AWG` pour les troncs Jambes `50 A`, passer les câbles longs chevilles `RS-03` (`0,8 m`) en `16 AWG` (`dV` réduite de `0,502 V` à `~0,31 V`), acheter `2x ADS1115` (`~10 EUR` les 2) pour lire `8 FSR` + thermistances en I2C, et modifier le schéma ASCII `FINAL_Solenoids_Wiring.md` en vrai montage parallèle (avec diodes Schottky `SS34` si pilotage PWM). | Respecte la tenue thermique/chute de tension sur les membres, lève la saturation des `6 ADC` Spresense et prévient toute erreur de câblage des solénoïdes. |
| **6. Haut / Moyenne** | **Calibrer la batterie Phase 1 à `>= 50 A continu / 100 A pic`** (`AT WEY` ou sur-mesure `13S NMC`) avec prise `XT90-S` anti-spark, plutôt qu'un pack VAE générique limité à `30 A` continu. | Évite les coupures BMS intempestives et la chute mécanique du robot dès les phases d'essais jambes complètes (étapes 7-8). |

---

## 5. Synthèse du Niveau de Maturité

**★★☆☆☆ — Conception matérielle bien amorcée (composants majeurs acquis), mais maturité électrique et documentaire insuffisante pour une mise sous tension complète sur batterie.**

La structure globale en arbre 48 V, l'isolation multi-rails (`19 V / 12 V Logique / 12 V Puissance DROK / 5 V`), le passage au cervelet dual `Teensy 4.1 Triple CAN FD` et le choix des `RS-04` aux hanches/genoux (`-48 %` de pertes Joule statiques) constituent une base d'ingénierie saine. Cependant, **six défauts bloquants** empêchent la validation en sécurité : saturation bidirectionnelle du bus CAN 2.0B à `1 kHz` (`156-180 %`), erreur critique `5,0 V / 3,3 V` du diviseur batterie sur Spresense (coupure décharge profonde inopérante + dépassement `3,3 V`), watchdog figé sur `HIGH` statique, coupure `BTS50085` + E-Stop mal placé, fusible Logique `5 A` sous-dimensionné (`5,7-6,8 A` en charge) et double architecture non réconciliée (`Teensy` vs `CANable/U2D2`, omission du 27e moteur `RS-06`). La levée de ces 6 points hissera immédiatement le module à un niveau `★★★★☆` prêt pour l'intégration sur banc Wanptek puis batterie `13S`.
