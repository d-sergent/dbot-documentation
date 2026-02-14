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
| **Robstride 03** | 2 | **60 Nm** | Épaule (Force brute - Pitch/Roll) |
| **Robstride 02** | 2 | **17 Nm** | Épaule Yaw / Coude |
| **Robstride 00** | 1 | 14 Nm | Poignet Roll |

### Phase 3 : Deuxième Bras (5 DOF identiques)
*Même configuration que Phase 2, symétriquement.*

### Phase 4 : Jambes + Cou (14 DOF)
| Modèle | Quantité | Couple (Peak) | Usage |
| :--- | :--- | :--- | :--- |
| **Robstride 04** | 4 | **120 Nm** | Hanches Pitch + Genoux |
| **Robstride 03** | 4 | **60 Nm** | Hanches Roll/Yaw |
| **Robstride 03** | 2 | **60 Nm** | Chevilles Pitch (upgrade vs K-Bot) |
| **Robstride 02** | 2 | **17 Nm** | Chevilles Roll (**NOUVEAU**, stabilité latérale) |
| **Robstride 05** | 2 | **5.5 Nm** | Cou Pan/Tilt |

> **Note** : Configuration basée sur l'Option D-Révisée "D-Bot Maximal" (24 DOF). Voir [Analyse Biomécanique](./15_Analyse_Biomecanique.md) pour le détail et les alternatives.

### Autres Composants Électroniques
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :--- | :--- |
| **Robstride 04** | - | Hanches / Torse Pivot (Marche) | - |
| Distribution (PDB) | **Matek PDB-HEX** (Master) + **PDB-XT60-W** (Satellites) | 2 + 4 | Hubs de puissance pro |
| Connectique Data | **JST-GH 4-pin** (Silicone / Holybro) | 30m | Fils torsadés blindés |
| Maintenance Tête | **WAGO 221-413 / 415** | 10 | Connecteurs rapides sans soudure |
| Alimentation Labo | **Wanptek DPS605U** (60V/5A) | 1 | Réglage précis 24V/48V + OCP |
| Interface CAN | **InnoMaker USB2CAN-C** | 1 | Natif Linux (SocketCAN) |

> **Note** : Vérifiez bien que les moteurs arrivent avec leurs câbles d'alimentation (XT60) et data (JST-GH). Sinon, commander séparément.

---

## 3. Électronique & Cerveau (Détail Phase 1 & 2)

| Composant | Modèle | Note |
| :--- | :--- | :--- |
| **Cerveau IA** | NVIDIA Jetson Orin Nano (8GB) | Le modèle Super est un plus, mais le 8GB suffit. |
| **Vision (Tête)** | Luxonis OAK-D Pro | Version Fixed-Focus (FF) recommandée (vibrations). |
### Électronique de Contrôle
- **Sony Spresense** :
    - *Main Board* + *Extension Board* (Standard).
    - **Note sémantique** : L'Extension Board Standard est préférée pour ses 8 entrées micro (vs 4 sur la version LTE).
    - **Connectivité** : Pour la LTE, utilisez un shield tiers (Waveshare SIM7600) via UART pour conserver les 8 micros.
- **IMU Torse (Équilibre)** : **Bosch BMI270 Add-on Board** (Switch Science) — 6 axes, I2C/SPI, compatible Spresense. **C'est l'IMU principale d'équilibre** du robot (voir [Stratégie IMU](./08_Audio_Perception.md)).
- ~~**SensiEDGE CommonSense**~~ : ⚠️ **Non disponible au grand public** (réservée aux professionnels). Remplacée par le BMI270 Add-on Board ci-dessus.
- **Audio** : 8x Microphones numériques MEMS (PDM) + câbles blindés.

### Capteurs d'Équilibre (Phase 4)
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :--- | :--- |
| **IMU Torse** | BMI270 Add-on Board (Spresense) | 1 | IMU primaire d'équilibre — 416 Hz, 6 axes |
| **Capteurs plantaires** | FSR 402 (Force Sensing Resistor) | 8 (4/pied) | Mesure du Centre de Pression (CoP) — connectés aux ADC Spresense |
| *Alternative IMU* | *Sony Multi-IMU Add-on Board* | *1* | *16 MEMS, précision classe FOG — si besoin haute précision* |

### Sécurité & Gestion d'Énergie (Power Management)
| Composant | Référence | Rôle |
| :--- | :--- | :--- |
| **Régulateur Veille** | **Mean Well DDR-15G-5** (ou Buck 60V->5V) | Alimente la Spresense en permanence (Always-On). |
| **Switch Puissance** | **Infineon BTS50085-1TMA** (ou MOSFET Opto) | Coupe le 44V (Jetson/Moteurs) sur ordre de la Spresense. |
| **Pont Diviseur** | Résistances 150kΩ + 10kΩ | Surveillance de la tension batterie 12S. |
| **Condensa.** | 1000µF / 63V (Low ESR) | Filtrage des pics de tension au branchement. |
| **Connecteur** | **XT90-S** (Anti-Spark) | Obligatoire pour la batterie 12S (évite l'arc électrique). |
| **LiDAR** | **Unitree L2** | FOV 360°x90°, Portée 30m, IMU intégrée. |
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
| **WiFi Imprimante** | **TP-Link Archer T3U** | AC1300 Mbps, USB 3.0. Connectivité stable pour Qidi Plus 4. |

---

## 5. Consommables & Outils
*   **Frein Filet** : **Loctite 222** (Faible/Moyen). Indispensable ! Les vibrations des moteurs Robstride desserrent les vis M3 en quelques heures sans cela.
*   **Clés Allen** : Jeu de clés de précision (Facom ou Wera) pour ne pas foire les têtes de vis.
