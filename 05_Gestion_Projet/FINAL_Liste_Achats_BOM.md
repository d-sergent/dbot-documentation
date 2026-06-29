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

### Roulements à Section Fine (Articulations)
Pour un ratio Moment/Poids optimal en montage de type "Chape", fuyez les roulements standards (60xx) beaucoup trop profonds et lourds. Utilisez les séries *67xx* ou *68xx* :
*   **Pour le Moteur RS-04 (Hanches/Genoux) : 6807-2RS**
    *   *Dimensions* : 35 mm (Int) × 47 mm (Ext) × 7 mm (Ép).
    *   *Masse & Capacité* : ~30g, Capacité radiale **4.8 kN** (~480 kg). Le large diamètre interne permet de passer vos câbles XT30 et CAN !
*   **Pour le Moteur RS-03 (Cou/Chevilles) : 6705-2RS**
    *   *Dimensions* : 25 mm (Int) × 32 mm (Ext) × 4 mm (Ép).
    *   *Masse* : ~11g, hyper léger.
> [!CAUTION]
> **Joints 2RS Obligatoires** : Achetez exclusivement des versions "2RS" (Joints d'étanchéité en caoutchouc). Vos pièces en PA12-CF vont générer une fine poussière de carbone très abrasive qui détruira des roulements métalliques ouverts (ZZ) en quelques heures.

### Accouplements à Bride (Pour moteurs QDD plats RS-02 / RS-00)
Pour réaliser le découplage des efforts et reproduire une cinématique de type "Spline Coupling" (voir Doc 23), voici les références industrielles compatibles avec la face plate des moteurs Robstride.

*   **KTR BoWex FLE-PA (La solution industrielle idéale)** : Accouplement à denture avec bride en nylon. Conçu pour se visser sur des volants plats. Encaisse des couples monstrueux, autorise le glissement axial et le désalignement.
    *   *Acheter chez* : [KTR France (Catalogue Direct)](https://www.ktr.com/fr/produits/details/produits/accouplements/accouplements-a-frette/bowex-fle-pa/)
*   **Douilles Cannelées à Embase (La mécanique rigide)** : Flanged Spline Nuts. Création d'une liaison coulissante (Spline) pure 100% métallique. Idéal pour un démontage rapide.
    *   *Acheter chez* : [MISUMI Europa (Série Arbres et Douilles cannelés)](https://www.misumi-europe.com/fr/vona2/mech_design/M0100000000/M0103000000/M0103030000/)
*   **Moyeu à Bride Rigide (La méthode de prototypage rapide)** : Rigid Flange Shaft Coupling. Permet de créer un arbre cylindrique classique à partir des 6 trous M4 du RS-02. Vous pouvez ensuite utiliser un accouplement Oldham ou flector standard du commerce.
    *   *Où trouver* : Amazon France, Boutiques CNC / Modélisme (Cherchez `Flange Coupling Connector`).

> **Astuce d'intégration** : Le cercle de perçage (Bolt Circle) du RS-02 n'est pas standardisé pour ces composants. Prévoyez d'imprimer en 3D ou de découper au laser une **plaque d'adaptation (Adapter Plate)** de 3 à 5 mm d'épaisseur pour lier les trous du moteur à ceux de l'accouplement acheté.

---

## 2. Moteurs & Actionneurs (Par Phase)

### Phase 1 : Tête / Torse (Aucun Moteur)
*   Focus uniquement sur les capteurs et l'intelligence.

### Phase 2 : Premier Bras (6 DOF)
| Modèle | Quantité | Couple (Peak) | Usage |
| :--- | :--- | :--- | :--- |
| **Robstride 04** | 1 (**✅ Acheté**) | **120 Nm** | Épaule Pitch (Force levage frontal) |
| **Robstride 03** | 2 (**✅ Achetés**) | **60 Nm** | Épaule Roll + Coude Pitch |
| **Robstride 02** | 2 (**1× ✅ Acheté** / 1× à commander) | **17 Nm** | Épaule Yaw (1× ✅ Acheté) + Supination Avant-Bras (1× à commander) |
| **Robstride 00** | 1 (**✅ Acheté**) | **14 Nm** | Poignet Pitch |
| **Robstride 06** | 0 | **36 Nm** | (Le RS-06 acheté a été relocalisé comme actuateur actif pour la Taille/Waist Yaw) |

### Phase 3 : Deuxième Bras (6 DOF identiques)
| Modèle | Quantité | Couple (Peak) | Usage |
| :--- | :--- | :--- | :--- |
| **Robstride 04** | 1 (**✅ Acheté**) | **120 Nm** | Épaule Pitch |
| **Robstride 03** | 2 (**1× ✅ Acheté** / 1× à commander) | **60 Nm** | Épaule Roll (1× ✅ Acheté) + Coude Pitch (1× à commander) |
| **Robstride 02** | 2 | **17 Nm** | Épaule Yaw + Supination Avant-Bras (À commander) |
| **Robstride 00** | 1 | **14 Nm** | Poignet Pitch (À commander) |

### Phase 4 : Jambes + Cou + Taille (15 DOF)
| Modèle | Quantité | Couple (Peak) | Usage |
| :--- | :--- | :--- | :--- |
| **Robstride 04** | 4 | **120 Nm** | Hanches Pitch + Genoux |
| **Robstride 03** | 4 | **60 Nm** | Hanches Roll/Yaw |
| **Robstride 03** | 4 | **60 Nm** | Chevilles Pitch+Roll (**2× par cheville**, architecture cardan + bielles) |
| **Robstride 05** | 2 (**✅ Achetés & Montés**) | **5.5 Nm** | Cou Pan/Tilt |
| **Robstride 06** | 1 (**✅ Acheté & Monté**) | **36 Nm** | Taille (Waist Yaw) |

> **Note** : Architecture cheville = Cardan DIN 808 + 2× RS-03 par cheville (différentiel Pitch/Roll). Voir [Étude Cheville](../01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Cheville_Cardan.md) pour le détail.

### Phase 5 : Mains (16 DOF — 8 par main)
Le système D-Hand Hybrid Premium nécessite des servomoteurs performants, une quincaillerie de haute précision pour le passage des tendons, des capteurs tactiles magnétiques 3 axes (eFlesh) et des consommables spécifiques. Les quantités indiquées ci-dessous correspondent au **robot complet (2 mains)**.

#### 5.1 Motorisation & Alimentation
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :---: | :--- |
| **Servo de Force (flexion)** | **Feetech STS3250** (12V, 4.9 Nm) | 10 | **✅ Achetés** : 5 par main, flexion/serrage, SCServo TTL. |
| **Servo de Précision (opposition)** | **Feetech HL-3915** (12V, 1.39 Nm) | 6 | **✅ Achetés** : 3 par main, opposition pouce, abduction, SCServo TTL. |
| **Debug Feetech** | **Module URT-2 (USB-TTL SCServo)** | 2 | **1× ✅ Acheté** (sur 2 requis pour le robot complet) : Interface de com série TTL. |
| **Alimentation Servos** | **DROK 48V→12V 25A (IP67)** | 2 | **✅ Reçus** : 1 par bras, monté sur l'avant-bras pour dissipation thermique. |
| **Fusible Réarmable** | **PTC 15A** | 2 | 1 par main, protection surcourant de la ligne 12V. À commander. |

#### 5.2 Quincaillerie & Guidage Mécanique
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :---: | :--- |
| **Poulies d'Enroulement** | **Poulies Ø14mm Alu 7075** | 16 | 8 par main, usinage CNC (C500) avec roulement MR84ZZ intégré. |
| **Micro-roulements** | **MR84ZZ** (4 × 8 × 3 mm) | 72 | 36 par main (24 joints + 8 spools + 4 base pouce). **✅ Commandés** (lot 100pcs AliExpress). |
| **Roulements Moyen** | **6 × 13 × 5 mm** | 4 | 2 par main, pivot de base du pouce. À commander. |
| **Axes Chapes** | **Goupilles acier rectifié 2 × 6 mm** | 40 | 20 par main, blocage des chapes MCP/PIP/DIP. À commander. |
| **Axes Support Doigts** | **Axes inox rectifié 3 × 55 mm** | 8 | 4 par main, axes principaux de montage. À commander. |
| **Tubes de Guidage PTFE 1.9** | **PTFE Ø1.5 mm (ID) / 1.9 mm (OD)** | 1 (5m) | **✅ Acheté (5m)** : Guidage nominal (Option B). |
| **Tubes de Guidage PTFE 1.6** | **PTFE Ø1.2 mm (ID) / 1.6 mm (OD)** | 1 (5m) | **✅ Acheté (5m)** : Guidage alternatif plus fin. |

#### 5.3 Système Tactile eFlesh (Grip Intel)
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :---: | :--- |
| **PCB Paume eFlesh** | **WowRobo eFlesh Array** (5× MLX90393) | 4 | **✅ Achetés** (lot global de 20) : 2 arrays par paume (Option B). |
| **PCB Doigt eFlesh** | **PCB Custom 10 × 10 mm (ou 10 × 14 mm)** | 10 | 5 par main (1 par doigt), avec 1× MLX90393. À faire fabriquer (JLCPCB PCBA). |
| **Micro-Hub Tactile** | **Seeed Studio XIAO ESP32-S3 (Pack 3PCS)** | 1 (pack) | **✅ Acheté (Pack 3PCS)** : Permet d'équiper les 2 mains (1 par main) + 1 carte de secours/banc d'essai. I2C vers USB. |
| **Cordon Data** | **Câble JST-SH 4 broches (STEMMA QT / Qwiic)** | 16 | 8 par main, femelle-femelle, longueur 100mm. À commander. |
| **Aimants Doigts** | **Néodyme S-03-01-N (Disque Ø3 × 1 mm)** | 10 | 5 par main, insérés dans la pulpe TPU. **✅ Achetés** (lot global de 40). |
| **Aimants Paume** | **Néodyme W-05-N (Cube 5 × 5 × 5 mm)** | 4 | 2 par main, insérés dans la paume TPU. **✅ Achetés** (lot global de 10). |

#### 5.4 Tendons & Retours Passifs
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :---: | :--- |
| **Tendon Actif (Flexion)** | **Tresse Dyneema DM20 Ø1.0 mm** | 1 | Bobine de 50m. Résistance ~980 N, zéro fluage (zéro-creep). À commander. |
| **Tendon Passif (Retour)** | **Cordon élastique TPU Ø0.8 mm** | 1 | Bobine de 25m (Beadalon Elasticity). **✅ Reçu** (en stock). |
| **Manchons de Sertissage** | **Sleeves Ø1.5 mm (Alu ou Cuivre)** | 50 | 25 par main. Amagnétiques pour éviter les perturbations. À commander. |
| **Vis de Pression** | **Vis sans tête M3 × 4 mm (bout plat)** | 10 | 5 par main, bridage mécanique des élastiques dans la paume. À commander. |

#### 5.5 Outils & Consommables Spécifiques
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :---: | :--- |
| **Pince à sertir** | **Pince à sleeves de pêche** (0.1–2 mm) | 1 | Pour la micro-compression des manchons sans endommager la tresse. À commander. |
| **Colle Structurelle** | **3M DP490 (Époxy bicomposant)** | 1 cart. | Pour l'assemblage carbone/métal de la structure. À commander. |
| **Colle Rapide** | **Loctite Super Glue Gel** | 1 tube | Pour le maintien instantané des aimants et des nœuds. À commander. |

> **Note** : Voir [Étude Main Robotique](../01_Mecanique_et_Chassis/Bras_et_Mains/STUDY_Main_D_Hand.md) pour l'architecture D-Hand Hybrid consolidée.


### Autres Composants Électroniques
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :--- | :--- |
| Distribution Centrale | **Busbar double cuivre (Busbar 2 voies)** 12 x M4, 150A + Couvercle | 1 | (**✅ Acheté**) Torse. Distribution centrale validée 48V/150A. |
| Distribution Jambes | **Mini-busbars 6 bornes** cuivre, 60V+ | 2 | Splitters locaux bassin G/D. Amazon `"bus bar 6 way marine"`. ~8-12 €/pce |
| Splitters Bras/Cou | **WAGO 221-413 / 221-415** | 10 (**✅ Achetés**) | Splitters locaux dans les bras (2×WAGO-415 par bras) et le cou (WAGO-413). 32A / 450V sans soudure. |
| Fusibles par zone | **Porte-fusible lame en ligne** + fusibles 80A ×1 + 50A ×2 + 30A ×2 + 5A ×1 | 6 | Isolation de faute par membre. Amazon `"porte-fusible lame automobile en ligne"`. ~3-5 € le lot |
| Connecteurs XT60/XT30 | **Connecteurs nus Mâle/Femelle (pré-étamés)** | 1 lot | (**✅ Achetés**) Pour fabriquer les pigtails sur-mesure des moteurs et les troncs détachables. |
| Câbles de Puissance | **Rouleaux Silicone 14 AWG et 18 AWG** | 1 lot | (**✅ Achetés**) Rouge + Noir. 14 AWG (troncs/gros moteurs), 18 AWG (rouleau 30m pour petits moteurs). |
| Alimentation Labo | **Wanptek DPS605U** (60V/5A) | 1 (**✅ Achetée**) | Indispensable Phases 1-4 (48V). Limite 3A pour RS-04/05 (voir [§4c](../02_Electronique_et_Energie/STUDY_Electronique_Historique.md#4c-séquence-de-validation--wanptek--batterie)). Manuel : [dps605U.pdf](./manuels/dps605U.pdf). |
| Interface CAN — Bus Cou | **InnoMaker USB2CAN-C** | 1 (**✅ Acheté**) | Bus Cou : RS-05 Pan + Tilt (2 moteurs). Manuel : [usb2can.pdf](./manuels/usb2can.pdf). |
| Interface CAN — Bus Membres | **CANable Pro** (isolation galvanique 2.5kV, firmware candleLight) | 4 (**✅ Achetés**) | 1 par membre (Bras G, Bras D, Jambe G, Jambe D). Isolation 2.5kV validée. |
| Hub USB | **Hub USB 3.0 Industriel Alimenté (7+ ports)** | 1 | Modèle recommandé : **Sabrent Aluminum 7-Port** ou **StarTech Metal Hub**. Alimenté sur le rail 12V (via Buck) pour stabiliser les 5 bus CAN + Spresense + 2× U2D2. |
| Module de Debug | **Module de Debug RobStride (Isolation Galvanique)** | 1 (**✅ Acheté**) | Config/debug uniquement via RobStride Studio. 1 seul suffit pour tous les moteurs. |

> **Note** : Vérifiez bien que les moteurs arrivent avec leurs câbles d'alimentation (XT60) et data (JST-GH). Sinon, commander séparément.

---

## 3. Électronique & Cerveau (Détail Phase 1 & 2)

| Composant | Modèle | Note |
| :--- | :--- | :--- |
| **Cerveau IA** | **NVIDIA Jetson Orin Nano Super** (8GB, 67 TOPS) | (**✅ Achetée**) |
| **Vision (Tête)** | [Luxonis OAK-D Pro FF](https://www.mouser.fr/ProductDetail/Luxonis/OAK-D-PRO-FF?qs=Znm5pLBrcAK58KqDdxCLeQ%3D%3D) | (**✅ Achetée**) Version Fixed-Focus (FF) recommandée (vibrations). |
### Électronique de Contrôle
- **Sony Spresense** :
    - [*Main Board*](https://www.mouser.fr/ProductDetail/Sony-Spresense/CXD5602PWBMAIN1_FG_875607611_P?qs=%252B6g0mu59x7Ifurwfgmhhqg%3D%3D) + [*Extension Board* (Standard)](https://www.mouser.fr/ProductDetail/Sony-Spresense/CXD5602PWBEXT1E_FG_875612931_P?qs=%252B6g0mu59x7IfMFVSCO3mMw%3D%3D) (**✅ Achetées**).
    - **Note** : La Spresense **ne gère plus l'audio** (remplacé par le ReSpeaker). Ses rôles restants : Watchdog, Power Management, IMU BMI270, FSR, Thermistances.
- **IMU Torse (Équilibre)** : [**SparkFun 6DoF IMU Breakout - BMI270** (Réf: `SEN-22397`)](https://www.mouser.fr/ProductDetail/SparkFun/SEN-22397?qs=1Kr7Jg1SGW8PccltG0E4HQ%3D%3D) (**✅ Achetée**) + Câble. 
    - **C'est l'IMU principale d'équilibre** du robot (voir [18 — Stratégie IMU](../04_Perception_et_Sensors/STUDY_IMU_Fusion.md)). 
    - **Câblage Requis** : Il vous faut impérativement accompagner cette carte d'un **câble adaptateur Qwiic vers Pins Mâles** (Réf Mouser : [Adafruit 4209](https://www.mouser.fr/ProductDetail/Adafruit/4209?qs=PzGy0jfpSMuV28p8L2H4sQ%3D%3D) **✅ Acheté**) pour la brancher facilement sur les pins classiques de la Spresense Extension Board sans faire de soudures compliquées.
    - *Alternative (Difficile à sourcer)* : La carte `SSCI-079782` (Switch Science) qui s'enfiche directement sur la Spresense reste excellente mais est très dure à trouver en Europe.
- ~~**SensiEDGE CommonSense**~~ : ⚠️ Remplacée par la BMI270 ci-dessus car introuvable.
- **Audio (Système Simplifié)** : [**Seeed ReSpeaker XVF-3800 USB 4-Mic Array**](https://www.gotronic.fr) (**✅ Acheté**) + [**CQRobot 5W 8Ω Miniature Speaker (JST-PH2.0)**](https://www.amazon.fr) (**✅ Acheté**)
    - Remplace l'ancien système 8 micros PDM + Jabra Speak 510. Voir [08 — Architecture Audio](../04_Perception_et_Sensors/FINAL_Architecture_Audio.md).
    - Fournit : DoA 360° + Beamforming + AEC + Noise Suppression + sortie HP JST 5W.
    - Interface : **USB** → Jetson (PulseAudio natif).
    - [Ressources & Modèles CAO (Wiki)](https://wiki.seeedstudio.com/respeaker_xvf3800_introduction/#resources)

### Capteurs d'Équilibre (Phase 4)
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :--- | :--- |
| **IMU Torse** | [SparkFun BMI270 Qwiic (SEN-22397)](https://www.mouser.fr/ProductDetail/SparkFun/SEN-22397?qs=1Kr7Jg1SGW8PccltG0E4HQ%3D%3D) | 1 (**✅ Achetée**) | IMU primaire d'équilibre — 416 Hz |
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
| **Batterie Phase 1 (prototype)** | **Batterie VAE 48V 13S NMC 10Ah BMS 30A+** (format boîte, connecteur XT60) | ~180-350 €. Sources vérifiées FR : [Save My Battery](https://www.savemybattery.fr) (~350€) ou [Yose Power](https://www.yosepower.com) (~250€) ou Amazon.fr (`"batterie 48V 13S 10Ah BMS"`). **Vérifier : BMS 13S, ≥30A continu, connecteur XT60.** Voir [§4](../02_Electronique_et_Energie/STUDY_Electronique_Historique.md#4-alimentation--batterie). |
| **Batterie Phase 2 (production)** | **Pack sur-mesure 48V 13S NMC, forme optimisée** | ~400-700 €. À commander quand le torse CAO est figé : [OZO Electric](mailto:batteries@ozo-electric.com) ou [Save My Battery](https://www.savemybattery.fr) ou [Neogy](https://www.neogy.fr). |
| **Chargeur 13S** | **54.6V CC/CV 4-5A** | Chargeur dédié Li-ion 13S NMC (souvent livré avec la batterie VAE). |
| ~~**LiDAR**~~ | ~~**Unitree L2**~~ | ⚠️ **Repoussé à la V2**. SLAM assuré par l'OAK-D Pro en V1. Voir [Analyse LiDAR](../04_Perception_et_Sensors/STUDY_LiDAR_Slam.md). |
| **Solénoïdes de Blocage** | [LEX-SOLEN-04 (Push Pull 12V)](https://www.lextronic.fr/solenoide-electroaimant-12v-lexsolen04-58749.html) | 2 (**✅ Achetés**) | Verrouillage statique du Tilt de tête (Parking Brake). |
| **Driver Solénoïde** | **Module Dual MOSFET D4184 (Logic Level)** | 1 | Indispensable : Ce modèle réagit bien au 3.3V de la Jetson (évite la surchauffe vs IRF520). |
| **Protection Inductive** | **Diode 1N4007** | 2 | **CRITIQUE** : À visser sur les borniers en parallèle du solénoïde pour absorber le pic de coupure. |
| **Buck 12V (Logique)** | **Buck DC-DC 60V In / 12V 10A Out** | 1 | Alimentation Hub USB (5A) + Solénoïdes Tête (2A). |
| **Buck 12V (Puissance)** | **Convertisseur DROK 48V→12V 25A (IP67)** | 2 | **Dédié** : 1 convertisseur par bras (2 au total) pour alimenter les 16x servomoteurs Feetech des mains. **✅ Reçus** |
| **Hub USB Central** | **10 Ports USB 3.0 Alimenté** | 1 | **Minimum 10 ports**. Modèles : **StarTech ST103008U2C** (Top) ou **Sabrent HB-BU10** (Compact). |
| **Régulateurs Locaux** | **AMS1117-3.3** (LDO 3.3V 800mA) | 4 | **Crucial** : Alimente FSR localement. |
| **Micro-Hubs Tactiles** | **ESP32-S3-DevKitC-1** (ou similaire) | 2 | **Option B** : Acquisition eFlesh USB pour les mains. |

### Interface CAN & Perception

| Composant | Référence / Modèle | Qté | Usage |
| :--- | :--- | :---: | :--- |
| **Adaptateur USB-CAN** | **InnoMaker USB2CAN-C** | 1 | Bus Cou (basé sur firmware `gs_usb`). |
| **Module de Debug** | **R-Link** | 1 | Paramétrage moteurs via *RobStride Studio*. |
| **Antenne GPS Active** | **Molex 1330980515** (U.FL 3.3V) | 1 | Localisation GNSS "Home positionning". |
| **Caméra Spresense HDR** | **Sony CXD5602PWBCAM2W** (120° FOV) | 1 | **Recommandé** : Vision 120° HDR pour sécurité sol. |
| **Caméra Spresense Standard** | **Sony CXD5602PWBCAM1E** (78° FOV) | 1 | **Alternative** : Analyse "réflexe" locale via TF Lite Micro. |
| **Caméra Poignet** | **USB 1080p Autofocus** | 1 | **Optionnel** : Vision macro manipulation. |
| **Connecteurs Data** | **JST-GH 1.25mm** (Holybro) | 1 lot | Signal (Préférer câbles pré-sertis). |
| **Connecteurs Pui.** | **XT60** (Jaune) | 1 lot | Alimentation générale et batteries. |
| **Câble Bus CAN** | **Paires Torsadées** | 1 lot | Indispensable pour l'immunité aux parasites. |

---

## 4. Infrastructure & Connexion
| Composant | Modèle | Usage |
| :--- | :--- | :--- |
| **WiFi Imprimante** | **TP-Link Archer T3U** (**✅ Acheté**) | AC1300 Mbps, USB 3.0. Connectivité stable pour Qidi Plus 4. |

---

## 5. Consommables & Outils
*   **Filament Flexible** : **1x Bobine Qidi TPU 95A-HF**. C'est le matériau universel officiel pour toutes les pièces souples du robot (supports amortisseurs pour les micros, semelles antidérapantes des pieds en utilisant le "Fuzzy Skin").
*   **Outils Filetage CNC (C500)** : **1x Micro-fraise à fileter M3 (1 dent, DLC)** + **1x Foret carbure 2.5mm**. (Queue de 4mm). Obligatoire pour fileter mécaniquement vos pièces Aluminium sans risquer de casser des tarauds manuels. (Acheter spécialisé : e.g., CncFraises).
*   **Frein Filet** : **Loctite 222** (Faible) pour visserie M3 (coques, électronique). **Loctite 243** (Moyen, Bleu) pour visserie M4/M5 haute charge (moteurs RS-04, brackets CNC). Indispensable ! Les vibrations desserrent les vis en quelques heures sans cela.
*   **Protection Thermique (Aimants tactile)** : **1x Rouleau de Ruban Adhésif en Tissu de Verre (ex: 3M 69)** ou à défaut du **Ruban Kapton**. Indispensable pour réaliser les pastilles d'isolation double-face sur les aimants NdFeB et éviter leur démagnétisation sous l'effet du TPU extrudé chaud à 220 °C. (Acheter chez : Amazon.fr, RS-Components ou Farnell).
*   **Clés Allen** : Jeu de clés de précision (Facom ou Wera) pour ne pas foire les têtes de vis.
