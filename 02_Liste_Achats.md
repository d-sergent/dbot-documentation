# Liste des Achats (BOM Consolidée)

## 1. Visserie & Fixations (Hardware)
**Stratégie** : Utilisation de vis **DIN 912 (Tête Cylindrique)** en Acier Inoxydable A2 (Inox 304) pour la résistance à la corrosion, ou Acier Noir 12.9 pour les axes moteurs de force.

### Quantités Requises (D-Bot + 2x RS-05)
| Type | Diamètre | Longueur | Quantité Est. | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Vis CHC** | M3 | 6mm - 12mm | ~240 | Fixations électroniques, caches, small motors |
| **Vis CHC** | M4 | 10mm - 15mm | ~160 | Structure principale, moteurs RS-01-RS-04 |
| **Vis CHC** | M5 | 12mm - 20mm | ~40 | Hanches, Grosses articulations |
| **Écrous/Rondelles** | M3/M4/M5 | - | ~150 de chaque | - |

### Liens d'Achat Recommandés
*   **Protorx (France)** : [Lien vers Boîtes M3/M4 Inox](https://www.protorx.com) - *Idéal pour un stock propre*.
*   **Vis-Express** : [Lien vers M4 DIN 912 Inox A2](https://www.vis-express.fr) - *Livraison rapide*.
*   **ScrewsAndMore** : [Lien vers Assortiment 400pcs](https://www.screwsandmore.de) - *Rapport quantité/prix*.

> **Conseil** : Achetez un kit "Build Complet" (1225pcs M2-M5) pour avoir du stock, et complétez avec des sachets de 50 vis M4 Acier 12.9 pour les moteurs.

### Inserts Filetés (Heat-set)
*   **Marque Recommandée** : **Ruthex** (ou CNC Kitchen).
*   **Modèle** : RX-M3x5.7 (M3) et versions "Longues" pour M4.
*   **Pourquoi ?** Les moletages opposés offrent la meilleure résistance à l'arrachement dans le PETG-CF.
*   **Acheter chez** : [3DJake France](https://www.3djake.fr) ou Amazon.

---

## 2. Moteurs & Actionneurs (Par Phase)

### Phase 1 : Tête / Torse (Aucun Moteur)
*   Focus uniquement sur les capteurs et l'intelligence.

### Phase 2 : Premier Bras (5 DOF)
| Modèle | Quantité | Couple (Peak) | Usage |
| :--- | :--- | :--- | :--- |
| **Robstride 04** | 1 (**✅ Acheté**) | **120 Nm** | Épaule Pitch (Force levage frontal) |
| **Robstride 03** | 1 (**✅ Acheté**) | **60 Nm** | Épaule Roll (Écartement latéral) |
| **Robstride 06** | 1 (**✅ Acheté**) | **36 Nm** | Coude |
| **Robstride 02** | 1 (**✅ Acheté**) | **17 Nm** | Épaule Yaw |
| **Robstride 00** | 1 (**✅ Acheté**) | 14 Nm | Poignet Roll |

### Phase 3 : Deuxième Bras (5 DOF identiques)
*Même configuration que Phase 2, symétriquement.*

### Phase 4 : Jambes + Cou (14 DOF)
| Modèle | Quantité | Couple (Peak) | Usage |
| :--- | :--- | :--- | :--- |
| **Robstride 04** | 4 | **120 Nm** | Hanches Pitch + Genoux |
| **Robstride 03** | 4 | **60 Nm** | Hanches Roll/Yaw |
| **Robstride 03** | 4 | **60 Nm** | Chevilles Pitch+Roll (**2× par cheville**, architecture cardan + bielles) |
| **Robstride 05** | 2 (**✅ Achetés**) | **5.5 Nm** | Cou Pan/Tilt |

> **Note** : Architecture cheville = Cardan DIN 808 + 2× RS-03 par cheville (différentiel Pitch/Roll). Voir [Étude Cheville](./20_Etude_Cheville_Cardan.md) pour le détail.

### Phase 5 : Mains (16 DOF — 8 par main)
| Modèle | Quantité | Couple (Peak) | Usage |
| :--- | :--- | :--- | :--- |
| **Dynamixel XC430-W240-T** | 8 | **1.9 Nm** | Canaux de Force (Pouces, Index, Majeurs, Paumes) |
| **Dynamixel XC330-T288-T** | 8 | **1.0 Nm** | Canaux de Précision (Oppositions, Abductions, Annulaires, Auriculaires) |
| **U2D2** (USB↔Dynamixel) | 2 | — | Interface bus TTL (1 par main) |
| **Buck 48V→12V 5A** | 2 | — | Alimentation servos main |
| **Kit Tactile eFlesh** | 2 | — | Silicone Ecoflex 00-30, 10× MLX90393, 10× aimants N52 par main |

> **Note** : Voir [Étude Main Robotique](./21_Etude_Main_Robotique.md) pour l'architecture D-Hand Premium.

### Autres Composants Électroniques
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :--- | :--- |
| Distribution (PDB) | **Matek PDB-HEX** (Master) + **PDB-XT60-W** (Satellites) | 2 + 4 | Hubs de puissance pro |
| Connectique Data | **JST-GH 4-pin** (Silicone / Holybro) | 30m | Fils torsadés blindés |
| Maintenance Tête | **WAGO 221-413 / 415** | 10 (**✅ Achetés**) | Connecteurs rapides sans soudure |
| Alimentation Labo | **Wanptek DPS605U** (60V/5A) | 1 (**✅ Achetée**) | Réglage précis 24V/48V + OCP |
| Interface CAN | **InnoMaker USB2CAN-C** | 1 (**✅ Achetée**) | Natif Linux (SocketCAN) |

> **Note** : Vérifiez bien que les moteurs arrivent avec leurs câbles d'alimentation (XT60) et data (JST-GH). Sinon, commander séparément.

---

## 3. Électronique & Cerveau (Détail Phase 1 & 2)

| Composant | Modèle | Note |
| :--- | :--- | :--- |
| **Cerveau IA** | NVIDIA Jetson Orin Nano (8GB) | Le modèle Super est un plus, mais le 8GB suffit. (**✅ Achetée**) |
| **Vision (Tête)** | [Luxonis OAK-D Pro FF](https://www.mouser.fr/ProductDetail/Luxonis/OAK-D-PRO-FF?qs=Znm5pLBrcAK58KqDdxCLeQ%3D%3D) | Version Fixed-Focus (FF) recommandée (vibrations). |
### Électronique de Contrôle
- **Sony Spresense** :
    - [*Main Board*](https://www.mouser.fr/ProductDetail/Sony-Spresense/CXD5602PWBMAIN1_FG_875607611_P?qs=%252B6g0mu59x7Ifurwfgmhhqg%3D%3D) + [*Extension Board* (Standard)](https://www.mouser.fr/ProductDetail/Sony-Spresense/CXD5602PWBEXT1E_FG_875612931_P?qs=%252B6g0mu59x7IfMFVSCO3mMw%3D%3D).
    - **Note sémantique** : L'Extension Board Standard est préférée pour ses 8 entrées micro (vs 4 sur la version LTE).
    - **Connectivité** : Pour la LTE, utilisez un shield tiers (Waveshare SIM7600) via UART pour conserver les 8 micros.
- **IMU Torse (Équilibre)** : [**SparkFun 6DoF IMU Breakout - BMI270** (Réf: `SEN-22397`)](https://www.mouser.fr/ProductDetail/SparkFun/SEN-22397?qs=1Kr7Jg1SGW8PccltG0E4HQ%3D%3D) + Câble. 
    - **C'est l'IMU principale d'équilibre** du robot (voir [Stratégie IMU](./08_Audio_Perception.md)). 
    - **Câblage Requis** : Il vous faut impérativement accompagner cette carte d'un **câble adaptateur Qwiic vers Pins Mâles** (Réf Mouser : [Adafruit 4209](https://www.mouser.fr/ProductDetail/Adafruit/4209?qs=PzGy0jfpSMuV28p8L2H4sQ%3D%3D)) pour la brancher facilement sur les pins classiques de la Spresense Extension Board sans faire de soudures compliquées.
    - *Alternative (Difficile à sourcer)* : La carte `SSCI-079782` (Switch Science) qui s'enfiche directement sur la Spresense reste excellente mais est très dure à trouver en Europe.
- ~~**SensiEDGE CommonSense**~~ : ⚠️ Remplacée par la BMI270 ci-dessus car introuvable.
- **Audio** : 8x Microphones numériques MEMS (PDM) + câbles blindés.

### Capteurs d'Équilibre (Phase 4)
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :--- | :--- |
| **IMU Torse** | [SparkFun BMI270 Qwiic (SEN-22397)](https://www.mouser.fr/ProductDetail/SparkFun/SEN-22397?qs=1Kr7Jg1SGW8PccltG0E4HQ%3D%3D) | 1 | IMU primaire d'équilibre — 416 Hz |
| **Capteurs plantaires** | FSR 402 (Force Sensing Resistor) | 8 (4/pied) | Mesure du Centre de Pression (CoP) — connectés aux ADC Spresense |
| *Alternative IMU* | *Sony Multi-IMU Add-on Board* | *1* | *16 MEMS, précision classe FOG — si besoin haute précision* |

### Sécurité & Gestion d'Énergie (Power Management)
| Composant | Référence | Rôle |
| :--- | :--- | :--- |
| **Régulateur Veille** | **Mean Well DDR-15G-5** (ou Buck 60V->5V) | Alimente la Spresense en permanence (Always-On). |
| **Switch Puissance** | **Infineon BTS50085-1TMA** (ou MOSFET Opto) | Coupe le 48V (Jetson/Moteurs) sur ordre de la Spresense. |
| **Pont Diviseur** | Résistances 150kΩ + 10kΩ | Surveillance de la tension batterie 13S (48V). |
| **Condensa.** | 1000µF / 63V (Low ESR) | Filtrage des pics de tension au branchement. |
| **Connecteur** | **Anderson SB50** (anti-spark) ou XT90-S | Connecteur haute puissance pour batterie 13S NMC 48V. |
| **Batterie (×1 → ×2)** | **[AT WEY NMC 48V 10 Ah](https://atwey.fr/accueil/94-batterie-generique-48v-10ah.html)** | 480 Wh, 2.3 kg, 13S NMC 21700 LG M50LT, BMS 50A, ~€300/pack — Assemblé 🇫🇷. Acheter 1 dès Phase 1, 2ème en Phase 4 (voir [Détails](./04_Electronique_Cablage.md#4-alimentation--batterie)). |
| **Chargeur 13S** | **54.6V CC/CV 4-5A** | Chargeur dédié Li-ion 13S NMC. Demander à AT WEY ou fournisseur FR. |
| ~~**LiDAR**~~ | ~~**Unitree L2**~~ | ⚠️ **Repoussé à la V2**. SLAM assuré par l'OAK-D Pro en V1. Voir [Analyse LiDAR](./19_Perception_Spatiale_LiDAR.md). |
| **Alimentation Labo** | **Wanptek DPS605U** | Indispensable Phase 2 (Régler sur 24V / Lim. 1A). |

### Interface CAN & Câbles
*   **Adaptateur USB-CAN** : **InnoMaker USB2CAN-C**
    *   *Critique* : Basé sur firmware `gs_usb` (compatible Linux natif).
*   **Connecteurs Data** : **JST-GH 1.25mm** (Marque Holybro recommandée pour la qualité).
    *   Acheter des câbles "tout faits" si possible pour éviter de sertir du 1.25mm.
*   **Connecteurs Puissance** : **XT60** (Jaune).
*   **Câble Bus CAN** : Utiliser impérativement des **paires torsadées** pour CAN_H / CAN_L.

---

## 4. Infrastructure & Connexion
| Composant | Modèle | Usage |
| :--- | :--- | :--- |
| **WiFi Imprimante** | **TP-Link Archer T3U** (**✅ Acheté**) | AC1300 Mbps, USB 3.0. Connectivité stable pour Qidi Plus 4. |

---

## 5. Consommables & Outils
*   **Frein Filet** : **Loctite 222** (Faible/Moyen). Indispensable ! Les vibrations des moteurs Robstride desserrent les vis M3 en quelques heures sans cela.
*   **Clés Allen** : Jeu de clés de précision (Facom ou Wera) pour ne pas foire les têtes de vis.
