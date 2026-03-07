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
*   **Tension nominale** : **46.8V** (13S Li-ion NMC) — Standard K-Bot.
*   **Tension max (charge)** : 54.6V (13S NMC, chargeur CC/CV dédié).
*   **Connecteur principal** : **Anderson SB50** (anti-spark) ou **XT90-S**.
*   **Distribution** : **PDB (Power Distribution Board)** type Matek PDB-HEX pour éclater le 48V vers les moteurs.
*   **Sécurité** :
    *   Fusible automobile 80A sur la ligne principale.
    *   Bouton d'arrêt d'urgence (E-Stop) coupant l'alim moteurs mais *pas* la Jetson.
    *   MOSFET piloté par Spresense pour coupure logicielle (voir [Guide Watchdog](./11_Guide_SensiEDGE_Watchdog.md)).

> [!NOTE]
> **Pourquoi 13S (48V) et non 12S (44V) ?** Le "S" = nombre de cellules en Série. Chaque cellule NMC fait 3.6V nominal. 13 × 3.6V = 46.8V ≈ "bus 48V" — c'est le standard des RobStride et du K-Bot officiel. En 12S (43.2V), les moteurs fonctionnent mais avec un couple réduit de ~8%. Le passage en 12S LiPo (3.7V/cellule = 44.4V) serait un compromis acceptable pour du RC, mais pour le D-Bot on suit le standard K-Bot.

### Choix de Batteries — NMC 21700 (Stratégie Progressive)

> [!IMPORTANT]
> **Stratégie retenue** : Démarrer avec **1× AT WEY NMC 48V 10 Ah** (Phase 1-3), puis **ajouter la 2ème identique en parallèle** en Phase 4 pour doubler l'autonomie et la symétrie. **Même techno du début à la fin, zéro gaspillage.**

#### 🏆 Batterie Recommandée : AT WEY NMC 48V 10 Ah

| Paramètre | Valeur |
| :--- | :--- |
| **Modèle** | Batterie générique 48V 10 Ah |
| **Chimie** | Li-ion NMC 21700, cellules **LG M50LT** |
| **Tension** | 48V nominale (13S) |
| **Capacité** | 10 Ah (480 Wh) |
| **Poids** | **2.3 kg** par pack |
| **BMS** | 13S NMC intégré, 20-50A continu, 100A pic |
| **Connectique** | Personnalisable à la commande (demander **Anderson SB50**) |
| **Fabrication** | 🇫🇷 Assemblé en France |
| **Prix** | ~250-350 € TTC par pack |

🔗 **Lien d'achat** : [AT WEY — Batterie générique 48V 10Ah](https://atwey.fr/accueil/94-batterie-generique-48v-10ah.html)

> [!TIP]
> **À la commande, préciser** : connecteur Anderson SB50 (ou QS8 anti-spark), BMS 50A continu minimum, usage robotique haute puissance. Demander aussi un **chargeur 13S (54.6V) 4-5A CC/CV**.

#### Pourquoi NMC plutôt que Semi-Solide ?

| Critère | NMC 21700 (AT WEY) | Semi-Solide (Grepow/Tattu) |
| :--- | :--- | :--- |
| **Disponibilité** | ✅ En stock, livraison FR | ❌ Custom, MOQ, délais 4-12 sem. |
| **Poids (10 Ah)** | 2.3 kg | ~1.5 kg (théorique) |
| **Capacité** | 10 Ah (480 Wh) | 6 Ah max (265 Wh) — custom requis |
| **Prix** | ~€300 | ~$400-800 + import |
| **Courant** | 50A continu, 100A pic | Variable, peu documenté |
| **Cycles** | 800-1000 | 300-1000 |
| **Assemblé en FR** | ✅ Oui | ❌ Import Chine |
| **Risque projet** | ✅ Faible | ⚠️ Élevé (approvisionnement) |

→ Le semi-solide sera réévalué en **2027+** quand des packs robotiques <5 kg existeront. Voir [Annexe Semi-Solide](./17_Annexe_Batterie_SemiSolide.md).

#### Alternatives FR Évaluées

| Fournisseur | Chimie | Avantage | Limite |
| :--- | :--- | :--- | :--- |
| [B-Volt](https://www.b-volt.com) | NMC Samsung 35E | Ultra-léger, FR | Moins de capacité |
| [OZO Industries](https://ozo-industries.com) | NMC/LFP custom | Sur-mesure forme et BMS | Plus cher (~€600+) |
| [Li-Tech](https://www.li-tech.fr) | LiFePO4 | Très sûr, 6000 cycles | +40% masse (3-4 kg) |
| [PowerTech](https://www.powertechsystems.eu) | LiFePO4 | Industriel IP65 | Trop lourd pour bipède |

→ Détails dans [Annexe NMC](./16_Annexe_Batterie_NMC.md) et [Annexe Comparatif](./18_Annexe_Batterie_Comparatif.md).

### Positionnement dans le Robot

#### Phase 1-3 : 1 seule batterie (centrée)

```
┌─────────────────────────┐
│       TORSE BAS          │
│                          │
│    ┌──────────────┐      │
│    │  AT WEY #1   │      │   ← À plat, centrée
│    │  480 Wh      │      │      au-dessus du bassin
│    │  2.3 kg      │      │
│    └──────────────┘      │
│      (CdG centré)        │
└─────────────────────────┘
```

#### Phase 4 : 2 batteries en parallèle (symétrie)

```
┌─────────────────────────┐
│       TORSE BAS          │
│                          │
│  ┌──────────┐ ┌──────────┐│
│  │ AT WEY 1 │ │ AT WEY 2 ││  ← 1 de chaque côté
│  │ 480 Wh   │ │ 480 Wh   ││     du bassin
│  │ 2.3 kg   │ │ 2.3 kg   ││
│  └──────────┘ └──────────┘│
│   Total: 960 Wh, 4.6 kg   │
│   Autonomie: ~40-50 min   │
│   (Symétrie + Redondance) │
└─────────────────────────┘
```

> [!WARNING]
> **Mise en parallèle** : Les 2 packs DOIVENT être identiques (même modèle, même âge). Toujours connecter/déconnecter à SoC proche (~50-60%). Utiliser un ORing MOSFET ou des diodes idéales pour éviter les courants d'équilibrage.

### Sécurité Incendie (NMC)

- ✅ Utiliser uniquement des **packs fermés avec BMS dédié** (jamais de cellules nues)
- ✅ **Espace d'air** autour de la batterie dans le torse
- ✅ **Cloisonnement** en matériaux ignifugés (PC/ABS, tôle alu)
- ✅ **Sortie de dégazage** vers l'arrière (ne pas enfermer hermétiquement)
- ✅ **Charge** uniquement avec chargeur **54.6V (13S) CC/CV** dédié, en zone ventilée
- ✅ **Monitoring** température/tension/courant via Spresense (harnais faible puissance du BMS)

### Slot CAD Recommandé

Pour accueillir 1 ou 2 packs AT WEY, prévoir dans le torse 3D :
- **Slot unique (Phase 1-3)** : 200 × 100 × 50 mm (avec marge)
- **Double slot (Phase 4)** : 200 × 180 × 50 mm (2 packs côte-à-côte)
- **Fixation** : Rails ou Velcro industriel + connecteur Anderson accessible par trappe arrière
- **Sangle velcro** + **patin anti-vibration TPU** en fond de slot

### Câblage Batterie → PDB

```
Batterie(s) 13S NMC (Anderson SB50) ─── [Si 2 : ORing MOSFET parallèle]
    │
    ├── Fusible 80A (Automobile, lame)
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
