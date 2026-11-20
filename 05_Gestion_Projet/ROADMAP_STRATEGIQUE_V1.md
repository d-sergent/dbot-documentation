# 🗺️ ROADMAP & ACTIONS OUVERTES — D-BOT V1

> **Règle d'hygiène stricte** : ce fichier ne conserve **que les tâches ouvertes `[ ]`** et les blocages actifs. Dès qu'une tâche est validée dans un document `FINAL_` / `DOSSIER_TECHNIQUE_` / `STUDY_`, la supprimer ici (historique suivi via `git log`).  
> **Specs techniques de référence** : [DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md) · [DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md) · [DOSSIER_TECHNIQUE_Calculs_FEA_Torse_et_Bassin.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Calculs_FEA_Torse_et_Bassin.md) · [FINAL_Liste_Achats_BOM.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/05_Gestion_Projet/FINAL_Liste_Achats_BOM.md)

---

## 1. CAO & Fabrication Torse / Bassin (Pré-usinage C500)
*Prérequis avant lancement usinage CNC et intégration corps complet.*

- [ ] **Butée de lacet arrière (`+/- 95 deg`)** : Modéliser dans Fusion 360 sous `Waist_Plate_7075` (doigt Alu 7075 `16x12x8 mm`, `2x` FHC M4) et sur `Traverse_Renfort_Bassin` (`2x` plots fixes `20x12x9,5 mm` à `+/- 95 deg` avec patins PU 90 ShA, `2x` CHC M4x16 12.9 chacun).
- [ ] **Tirants bas monoblocs en T (Lame + Sabot)** : Remplacer l'assemblage 2 pièces (`Corniere basse` + `Support Corniere`) par le tirant monobloc nervuré avec semelle 90 deg (`2x` CHC M4x12 borgnes dans `Waist_Plate_7075`), puis valider `Inspect > Interference` face au panier batterie (garde >= `8,5 mm`).
- [ ] **Définition CAO Hanches (`ASV1_200`)** : Finaliser les `8` occurrences de hanches en cours de définition dans l'assemblage `Torse-123`.
- [ ] **Approvisionnement & Débit Alu 7075-T6** : Commander `20x100x500mm alu 7075 T6` (Blockenstock, réf `20x100x500mm-alu-7075-t6`, 59,41 EUR TTC) et débiter `2` coupons de `240 mm` pour usinage C500.

## 2. Banc Atelier, Tête / Cou & Secours Audio (Jetson)
*Dépendances : station 48V atelier pour essais continus sans batterie.*

- [ ] **Station d'alimentation atelier 600W** : Imprimer le boîtier `RS-power-Top Cover.stp` et assembler le bloc `MeanWell LRS-600-48` (`48 V / 12,5 A`) avec connecteurs `XT30 2+2`.
- [ ] **Intégration finale Tête / Cou (`2x RS-05`)** : Démonter le casque, ajuster le passage/longueur des câbles sur toute la course Pan/Tilt, remonter le casque, verrouiller les butées logicielles dans `config.py` et valider `OAK-D Pro + ReSpeaker XVF-3800 + cou` en simultané.
- [ ] **Fallback vocal hors-ligne (`Jetson`)** : Déployer `Kokoro-ONNX` (`onnxruntime-gpu`, voix `ff_siwis`) et valider le Watchdog `5 Hz` basculant sur `Ollama + Kokoro` si coupure Wi-Fi > `2 s`.

## 3. Corps Complet, Motorisation & Contrôle (`27 / 27` moteurs acquis — 100 %)
*Dépendances : assemblage mécanique Torse/Membres + `2x Teensy 4.1` CAN FD.*

- [ ] **Bus CAN, `Motorbridge` & Zéro encodeurs** : Qualifier les trames MIT (`Kp, Kd, theta, dtheta, tau_ff`) à `1 Mbps`, calibrer le `Zero-Offset` des encodeurs `14-bit` et étendre `web_ui.py` aux `27` moteurs.
- [ ] **Dynamique `Pinocchio` & Imitation `LeRobot`** : Charger l'URDF complet sous `Pinocchio` (feedforward `G(q)` via `tau_ff`) et connecter `LeRobot` (`ACT / Diffusion Policy`).

## 4. Outillage IA Mac & Qualité RAG
- [ ] **Campagne `Qwen3.8` / LightRAG & Benchmark QA** : Finaliser la réindexation manuelle (`index_docs.py`), l'audit d'intégrité (`check_integrity.py`) et le benchmark QA (`BENCHMARK_QA_DBOT_120.json`) selon [56_Plan_Deploiement_Tests_Qwen38_LightRAG.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/IA_sur_Mac_M1_Pro_Max_64Go/56_Plan_Deploiement_Tests_Qwen38_LightRAG.md).
