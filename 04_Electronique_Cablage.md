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

### Choix de Batteries (Comparatif)

#### Phase 2-3 (Bras + Tests debout) — LiPo Standard

| Modèle | Techno | Capacité | Énergie | Poids | Dimensions (mm) | Prix | Note |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Tattu 12S 10Ah 30C** | LiPo | 10 Ah | 444 Wh | **2.8 kg** | 182×67×115 | ~$270 | ✅ Dispo immédiatement, fiable |
| Tattu Pro 12S 22Ah LiHV | LiHV Smart | 22 Ah | 1003 Wh | 5.75 kg | 236×172×116 | ~$400 | ❌ Trop lourd |

#### Phase 4 (Marche) — Semi-Solide Haut de Gamme

| Modèle | Techno | Densité | Capacité | Énergie | Poids | Dimensions estimées (mm) | Prix | Note |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Grepow Semi-Solid 12S Custom (×1)** | Semi-solide NMC | 350 Wh/kg | 12 Ah | 530 Wh | **~1.5 kg** | **~180×100×60** | ~$500-700 | 🏆 1 batterie au bassin |
| **Grepow Semi-Solid 12S Custom (×2)** | Semi-solide NMC | 350 Wh/kg | 6 Ah ×2 | 530 Wh total | **~0.75 kg ×2** | **~140×80×45 ×2** | ~$600-800 | 🏆 2 batteries latérales |
| Foxtech Diamond Pro 12S | Semi-solide Li-Ion | 330 Wh/kg | 27 Ah | 1.2 kWh | ~3.6 kg | ~250×120×80 | ~$800-1200 | Conçu drone lourd |

> [!TIP]
> **Estimation des dimensions Grepow Custom** : Les batteries semi-solides de type pouch cell ont une densité volumique de ~500-600 Wh/L. Pour **530 Wh**, cela donne un volume de ~0.9-1.1L. En format **1 batterie plate** : environ **180 × 100 × 60 mm** (comparable à un livre de poche épais). En format **2 batteries fines** : environ **140 × 80 × 45 mm** chacune (comparable à un smartphone épais).

### Positionnement dans le Robot

| Config | Position | Volume à prévoir | Avantage | Inconvénient |
| :--- | :--- | :---: | :--- | :--- |
| **1× grosse** | Au-dessus des hanches, centre du torse bas | **180×100×60 mm** | CdG bas et centré, 1 seul connecteur | Bloc encombrant |
| **2× petites** | 1 de chaque côté du bassin (symétrique) | **140×80×45 mm ×2** | CdG symétrique, hot-swap possible, redondance | 2 connecteurs, câblage parallèle |

> [!IMPORTANT]
> **Recommandation** : Prévoir un **slot batterie de 200 × 110 × 70 mm** dans le torse bas lors du design CAO. Ce volume absorbe les 2 configurations (1 grosse ou 2 petites avec séparateur). Ajouter un support vibration en **TPU** (2mm) et une sangle velcro pour le maintien.

### Câblage Batterie → PDB

```
Batterie 12S (XT90-S)
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
