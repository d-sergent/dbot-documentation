# Électronique & Câblage

## 1. Schéma Global de Connexion
L'architecture repose sur un bus CAN centralisé et des liaisons USB High-Speed.

### Cerveau Principal (NVIDIA Jetson Orin Nano)
*   **Alimentation** : 19V DC (via Jack ou XT60 régulé).
*   **Rôle** : Orchestrateur ROS2, Vision IA, Planification de mouvement.
*   **Ports** :
    *   **USB A** -> **InnoMaker USB2CAN** (Contrôle Moteurs)
    *   **USB C** -> **OAK-D Pro** (Vision Stéréo + IA)
    *   **USB A** -> **Sony Spresense** (Audio / Capteurs TR)

---

## 2. Bus CAN (Moteurs Robstride)
C'est la colonne vertébrale du robot. Une erreur ici rend le robot inerte.

### Adaptateur : InnoMaker USB2CAN-C
*   **Firmware** : `gs_usb` (Natif Linux).
*   **Configuration Switch** : Mettre le switch **120 \Omega** sur **ON** (si l'adaptateur est en début de chaîne).
*   **Câblage Bornier** :
    *   **CAN_H** -> Fil Vert (souvent) du moteur.
    *   **CAN_L** -> Fil Jaune (souvent) du moteur.
    *   **GND** -> **CRITIQUE**. Relier la masse de l'USB2CAN à la masse commune des moteurs (Batterie -). Sans ça, le signal flotte et crée des erreurs "Bus Off".

### Bus de Communication (CAN 1 Mbps)
Le Bus CAN est le système nerveux du D-Bot. Une erreur de câblage ici rend le robot incontrôlable.

#### Règle d'or du Câblage 3 fils
Bien que différentiel, le CAN exige une référence commune :
1.  **CAN_H** (Jaune)
2.  **CAN_L** (Blanc)
3.  **GND** (Noir) : **CRITIQUE.** Doit relier la borne GND de l'InnoMaker à la masse des moteurs.
*Note : Le fil rouge (VCC 5V) du Hub Holybro ne doit JAMAIS être connecté aux moteurs alimentés en 48V.*

#### Architecture Daisy Chain
- **Stubs** : Les dérivations vers les moteurs doivent mesurer moins de **30 cm**.
- **Terminaison** : Une résistance de **120 Ω** doit être placée à chaque extrémité (Jetson et dernier moteur).
- **Torsion** : Torsader les fils (33 tours/mètre) pour annuler les EMI.

___

## 3. Sony Spresense & OAK-D Pro

### OAK-D Pro (Vision)
*   Agit comme un capteur USB3.
*   Intègre une **IMU (BNO085/BMI270)** — **utilisée uniquement pour la stabilisation du regard**, pas pour l'équilibre du corps (voir [Stratégie IMU](./08_Audio_Perception.md)).

### Sony Spresense (Audio & I/O)
*   **Carte Extension Choisie** : **Standard Board** (CXD5602PWBEXT1).
    *   *Raison* : Permet de brancher jusqu'à **8 microphones numériques** pour le Beamforming (localisation de la voix).
    *   *Évolutabilité* : Headers Arduino compatibles pour ajouter des shields futurs.
*   **Alternative LTE** : Si le robot doit sortir en extérieur (hors Wi-Fi), une **LTE Extension Board** aurait été préférée, mais la Standard offre plus de flexibilité I/O audio pour un robot social.
*   **Liaison Jetson** : Via USB (Port principal micro-USB de la Spresense). La Spresense apparaît comme un périphérique série (`/dev/ttyUSBx`) ou Audio USB selon le sketch chargé.

---

### Mise sous tension (Sécurité Wanptek)
Pour les premiers tests moteurs (Banc d'essai) :
1.  Régler la tension à **24.0V** (ou 48V) à vide.
2.  Régler la limite de courant à **1.000A** (en court-circuitant les pinces).
3.  Activer le mode **OCP** (Overcurrent Protection).
4.  Séquence : Allumer l'alim -> Vérifier tension -> Brancher XT60 -> `Enable` logiciel.

## 4. Alimentation & Batterie

### Spécifications Système
*   **Tension nominale** : **44.4V** (12S LiPo) ou **45.6V** (12S LiHV).
*   **Tension max (charge)** : 50.4V (LiPo) / 52.8V (LiHV).
*   **Connecteur principal** : **XT90-S** (Anti-Spark — obligatoire pour 12S, évite l'arc électrique).
*   **Distribution** : **PDB (Power Distribution Board)** type Matek PDB-HEX pour éclater le 48V vers les moteurs.
*   **Sécurité** :
    *   Fusible automobile sur la ligne principale.
    *   Bouton d'arrêt d'urgence (E-Stop) coupant l'alim moteurs mais *pas* la Jetson.
    *   MOSFET piloté par Spresense pour coupure logicielle (voir [Guide Watchdog](./11_Guide_SensiEDGE_Watchdog.md)).

### Choix de Batteries — Semi-Solide (Stratégie Progressive)

> [!IMPORTANT]
> **Stratégie retenue** : Acheter **1 seule batterie semi-solide 12S ~6 Ah** dès le début. La positionner **à plat, centrée au bassin**. En Phase 4 (marche), acheter **la 2ème identique** pour obtenir la symétrie latérale. **Zéro gaspillage**, même batterie du début à la fin.

#### Comparatif Fournisseurs Semi-Solide 12S

| # | Fournisseur / Modèle | Densité | Capacité dispo | Poids estimé (6 Ah) | Dimensions estimées (6 Ah) | Prix unitaire | Achat |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| 🏆 | **Grepow Semi-Solid Custom** | **350 Wh/kg** | Sur mesure (5-84 Ah) | **~0.76 kg** | **~140×80×45 mm** | ~$300-400 | OEM — Devis |
| 2 | **Foxtech Diamond Pro 330** | 330 Wh/kg | 22-36 Ah (stock) | ~0.81 kg* | ~150×85×45 mm* | ~$518 (17.5 Ah) | Boutique en ligne |
| 3 | **Tattu/GenAce Semi-Solid** | 300 Wh/kg | 30 Ah (stock) | ~0.89 kg* | ~155×90×50 mm* | ~$350-450 | Boutique en ligne |
| 4 | **HereWin Semi-Solid** | 310 Wh/kg | 26-35 Ah (stock) | ~0.86 kg* | ~150×85×48 mm* | ~$400-600 | Contact direct |
| 5 | **KKLIPO Solid-State** | 320 Wh/kg | 20 Ah (stock) | ~0.83 kg* | ~145×85×46 mm* | ~$300-500 | Contact direct |

*\* Dimensions estimées par extrapolation pour 6 Ah — les modèles catalogue sont plus gros (22+ Ah). Une commande custom est nécessaire pour obtenir 6 Ah.*

> [!TIP]
> **Estimation des dimensions pour 6 Ah (265 Wh)** : Densité volumique semi-solide ~500-600 Wh/L → Volume ~0.45-0.53 L → Format pouch cell plat : environ **140 × 80 × 45 mm** (~taille d'un smartphone épais). Pour **2× 6 Ah en parallèle** (12 Ah, 530 Wh) : même taille ×2.

#### 🔗 Liens Fournisseurs (Contact / Achat)

| Fournisseur | Lien | Action |
| :--- | :--- | :--- |
| **Grepow** | [grepow.com/custom-battery](https://www.grepow.com/custom-battery-solution.html) — Email : **info@grepow.com** | Envoyer un devis avec : 12S, 6 Ah, semi-solide, connecteur XT90-S, BMS intégré |
| **Foxtech** | [foxtechfpv.com/diamond-batteries](https://www.foxtechfpv.com/diamond-pro-330wh-kg-high-energy-density-semi-solid-state-li-ion-battery.html) | Achat direct — Modèle 12S le plus petit |
| **Tattu/GenAce** | [genstattu.com](https://www.genstattu.com/) — [gensace.de](https://www.gensace.de/) (EU) | Boutique — Chercher "Semi Solid 12S" |
| **HereWin** | [herewinpower.com](https://www.herewinpower.com/semi-solid-state-drone-battery/) | Contact commercial — Préciser usage robot |
| **KKLIPO** | [kklipo360.com](https://www.kklipo360.com/) | Contact — Demander 12S 6 Ah solid-state |

### Positionnement dans le Robot

#### Phase 1-3 : 1 seule batterie (centrée)

```
┌─────────────────────────┐
│       TORSE BAS          │
│                          │
│    ┌──────────────┐      │
│    │  BATTERIE 1  │      │   ← À plat, centrée
│    │  140×80×45   │      │      au-dessus du bassin
│    └──────────────┘      │
│      (CdG centré)        │
└─────────────────────────┘
```

#### Phase 4 : 2 batteries (symétrie latérale)

```
┌─────────────────────────┐
│       TORSE BAS          │
│                          │
│  ┌──────────┐ ┌──────────┐│
│  │ BATT. 1  │ │ BATT. 2  ││  ← 1 de chaque côté
│  │ 140×80   │ │ 140×80   ││     du bassin
│  │ ×45      │ │ ×45      ││
│  └──────────┘ └──────────┘│
│   (Symétrie + Redondance) │
└─────────────────────────┘
```

> [!IMPORTANT]
> **Recommandation CAO** : Prévoir un **slot batterie de 200 × 180 × 50 mm** dans le torse bas. Ce volume absorbe les 2 phases :
> - Phase 1-3 : 1 batterie centrée + mousse de calage latéral
> - Phase 4 : 2 batteries côte à côte avec séparateur TPU 2mm
> Ajouter une **sangle velcro** et un **patin anti-vibration TPU** en fond de slot.

### Câblage Batterie → PDB

```
Batterie(s) 12S (XT90-S) ─── [Si 2 : Y-Splitter XT90-S parallèle]
    │
    ├── Fusible 30A (Automobile, lame)
    │
    ├── E-Stop (Bouton d'arrêt d'urgence)
    │
    ├── MOSFET Spresense (Pin D13) — Coupure logicielle
    │
    └── PDB (Matek PDB-HEX)
         ├── Moteurs RS-04 Hanches (XT60 ×4)
         ├── Moteurs RS-03 Épaules/Hanches (XT60 ×8)
         ├── Moteurs RS-02/00/05 (XT30 ×10)
         └── DC-DC 48V→5V (Jetson + Spresense)
```

---

## 5. Capteurs de Force (FSR) - Phase 4
Pour la marche dynamique, chaque pied est équipé de 4 capteurs FSR (Force Sensing Resistor) pour mesurer le Centre de Pression (CoP).

### Schéma de Câblage (Pont Diviseur)
Les FSR sont des résistances variables (Infini à vide -> ~1kΩ appuyé). La Spresense lit une **tension** (ADC). Il faut donc un circuit diviseur.

```
      3.3V (Spresense VREF)
        │
        │
       [ ]  FSR (Capteur de force)
        │
        ├─── vers Pin Analogique (A0, A1, A2, A3)
        │
       [ ]  Résistance Pull-down (R = 10kΩ)
        │
       GND
```

### Connexion Spresense
*   **Haut de l'Extension Board** : Pins `A0` à `A3` (4 canaux).
*   **Multiplexage** : Si vous avez 8 FSR (4 par pied) et seulement 4 entrées analogiques libres :
    *   Option A : Mettre les FSR Avant en parallèle (moyenne) et Arrière en parallèle. = 2 fils par pied.
    *   Option B : Utiliser un multiplexeur I2C (ex: ADS1115) pour lire 4 canaux supplémentaires.
    *   *Reco Prototype* : Option A (Suffisant pour savoir si le poids est sur les pointes ou les talons).
