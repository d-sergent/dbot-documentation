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

### Phase 2 : Premier Bras (5 DOF)
| Modèle | Quantité | Couple (Peak) | Usage |
| :--- | :--- | :--- | :--- |
| **Robstride 04** | 1 (**✅ Acheté**) | **120 Nm** | Épaule Pitch (Force levage frontal) |
| **Robstride 03** | 1 (**✅ Acheté**) | **60 Nm** | Épaule Roll (Écartement latéral) |
| **Robstride 06** | 1 (**✅ Acheté**) | **36 Nm** | Coude |

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
| **Buck 48V→12V 5A** | 2 | — | Alimentation servos main depuis bus 48V. **⚠️ Entrée ≥ 60V obligatoire** (batterie = 54.6V chargée). Recherche : `"DC DC converter 48V 12V 5A 60W"`. ~10-18 €/pièce |
| **Kit Tactile eFlesh** | 2 | — | Silicone Ecoflex 00-30, 10× MLX90393, 10× aimants N52 par main |

> **Note** : Voir [Étude Main Robotique](./21_Etude_Main_Robotique.md) pour l'architecture D-Hand Premium.

### Autres Composants Électroniques
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :--- | :--- |
| Distribution Centrale | **Busbar double cuivre (Busbar 2 voies)** 12 x M4, 150A + Couvercle | 1 | (**✅ Acheté**) Torse. Distribution centrale validée 48V/150A. |
| Distribution Jambes | **Mini-busbars 6 bornes** cuivre, 60V+ | 2 | Splitters locaux bassin G/D. Amazon `"bus bar 6 way marine"`. ~8-12 €/pce |
| Splitters Bras/Cou | **WAGO 221-413 / 221-415** | 10 (**✅ Achetés**) | Splitters locaux dans les bras (2×WAGO-415 par bras) et le cou (WAGO-413). 32A / 450V sans soudure. |
| Fusibles par zone | **Porte-fusible lame en ligne** + fusibles 80A ×1 + 50A ×2 + 30A ×2 + 5A ×1 | 6 | Isolation de faute par membre. Amazon `"porte-fusible lame automobile en ligne"`. ~3-5 € le lot |
| Connecteurs XT60/XT30 | **Connecteurs nus Mâle/Femelle (pré-étamés)** | 1 lot | (**✅ Achetés**) Pour fabriquer les pigtails sur-mesure des moteurs et les troncs détachables. |
| Câbles de Puissance | **Rouleaux Silicone 14 AWG et 18 AWG** | 1 lot | (**✅ Achetés**) Rouge + Noir. 14 AWG (troncs/gros moteurs), 18 AWG (rouleau 30m pour petits moteurs). |
| Alimentation Labo | **Wanptek DPS605U** (60V/5A) | 1 (**✅ Achetée**) | Indispensable Phases 1-4 (48V). Limite 3A pour RS-04/05 (voir [§4c](./04_Electronique_Cablage.md#4c-séquence-de-validation--wanptek--batterie)). Manuel : [dps605U.pdf](./manuels/dps605U.pdf). |
| Interface CAN — Bus Cou | **InnoMaker USB2CAN-C** | 1 (**✅ Acheté**) | Bus Cou : RS-05 Pan + Tilt (2 moteurs). Manuel : [usb2can.pdf](./manuels/usb2can.pdf). |
| Interface CAN — Bus Membres | **CANable Pro** (isolation galvanique 2.5kV, firmware candleLight) | 4 (à acheter) | 1 par membre (Bras G, Bras D, Jambe G, Jambe D). Achat progressif possible. Sources : [openlightlabs.com](https://openlightlabs.com) ~45 USD, AliExpress `"CANable Pro isolated 2.5kV"` ~20-35€, [Tindie](https://tindie.com) ~30-40€. Vérifier la mention **"2.5kV galvanic isolation"**. |
| Hub USB | **Hub USB alimenté multi-ports** | 1 (à choisir) | Choix différé — à déterminer après liste complète des périphériques Jetson (CAN ×5, U2D2 ×2, module de debug, Spresense, OAK-D...). |
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
    - **C'est l'IMU principale d'équilibre** du robot (voir [18 — Stratégie IMU](./18_Strategie_IMU_Fusion.md)). 
    - **Câblage Requis** : Il vous faut impérativement accompagner cette carte d'un **câble adaptateur Qwiic vers Pins Mâles** (Réf Mouser : [Adafruit 4209](https://www.mouser.fr/ProductDetail/Adafruit/4209?qs=PzGy0jfpSMuV28p8L2H4sQ%3D%3D) **✅ Acheté**) pour la brancher facilement sur les pins classiques de la Spresense Extension Board sans faire de soudures compliquées.
    - *Alternative (Difficile à sourcer)* : La carte `SSCI-079782` (Switch Science) qui s'enfiche directement sur la Spresense reste excellente mais est très dure à trouver en Europe.
- ~~**SensiEDGE CommonSense**~~ : ⚠️ Remplacée par la BMI270 ci-dessus car introuvable.
- **Audio (Système Simplifié)** : [**Seeed ReSpeaker XVF-3800 USB 4-Mic Array**](https://www.gotronic.fr) (**✅ Acheté**) + [**CQRobot 5W 8Ω Miniature Speaker (JST-PH2.0)**](https://www.amazon.fr) (**✅ Acheté**)
    - Remplace l'ancien système 8 micros PDM + Jabra Speak 510. Voir [08 — Architecture Audio](./08_Architecture_Audio.md).
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
| **Batterie Phase 1 (prototype)** | **Batterie VAE 48V 13S NMC 10Ah BMS 30A+** (format boîte, connecteur XT60) | ~180-350 €. Sources vérifiées FR : [Save My Battery](https://www.savemybattery.fr) (~350€) ou [Yose Power](https://www.yosepower.com) (~250€) ou Amazon.fr (`"batterie 48V 13S 10Ah BMS"`). **Vérifier : BMS 13S, ≥30A continu, connecteur XT60.** Voir [§4](./04_Electronique_Cablage.md#4-alimentation--batterie). |
| **Batterie Phase 2 (production)** | **Pack sur-mesure 48V 13S NMC, forme optimisée** | ~400-700 €. À commander quand le torse CAO est figé : [OZO Electric](mailto:batteries@ozo-electric.com) ou [Save My Battery](https://www.savemybattery.fr) ou [Neogy](https://www.neogy.fr). |
| **Chargeur 13S** | **54.6V CC/CV 4-5A** | Chargeur dédié Li-ion 13S NMC (souvent livré avec la batterie VAE). |
| ~~**LiDAR**~~ | ~~**Unitree L2**~~ | ⚠️ **Repoussé à la V2**. SLAM assuré par l'OAK-D Pro en V1. Voir [Analyse LiDAR](./19_Perception_Spatiale_LiDAR.md). |

### Interface CAN & Câbles
*   **Adaptateur USB-CAN** : **InnoMaker USB2CAN-C**
    *   *Critique* : Basé sur firmware `gs_usb` (compatible Linux natif).
*   **Module de Debug** : **R-Link**
    *   Un seul module USB vers CAN suffit pour paramétrer tous les moteurs via *RobStride Studio*. Exiger l'**Isolation Galvanique** pour protéger le PC de la tension 48V.
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
*   **Filament Flexible** : **1x Bobine Qidi TPU 95A-HF**. C'est le matériau universel officiel pour toutes les pièces souples du robot (supports amortisseurs pour les micros, semelles antidérapantes des pieds en utilisant le "Fuzzy Skin").
*   **Outils Filetage CNC (C500)** : **1x Micro-fraise à fileter M3 (1 dent, DLC)** + **1x Foret carbure 2.5mm**. (Queue de 4mm). Obligatoire pour fileter mécaniquement vos pièces Aluminium sans risquer de casser des tarauds manuels. (Acheter spécialisé : e.g., CncFraises).
*   **Frein Filet** : **Loctite 222** (Faible) pour visserie M3 (coques, électronique). **Loctite 243** (Moyen, Bleu) pour visserie M4/M5 haute charge (moteurs RS-04, brackets CNC). Indispensable ! Les vibrations desserrent les vis en quelques heures sans cela.
*   **Clés Allen** : Jeu de clés de précision (Facom ou Wera) pour ne pas foire les têtes de vis.
