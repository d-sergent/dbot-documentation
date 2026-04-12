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

#### Topologie Réseau (Data CAN) : Le Multi-Bus
Le câblage de communication exige rigueur et méthode à 1 Mbps pour éviter les réflexions et les désynchronisations :
1.  **En Étoile / Y (Interdit)** : Ne séparez jamais le câble CAN en "Y" au niveau du bassin. Les "stubs" (dérivations) dépassant 30 cm ruinent le signal.
2.  **Chaîne Unique (Déconseillée)** : Faire une série qui descend jusqu'au pied, puis remonte toute la jambe pour repartir vers la seconde, triple la longueur filaire et les risques de cassure.
3.  **Multi-Bus (Recommandé)** : C'est le standard des quadrupèdes. Utilisez plusieurs ports CAN matériels sur le Maître (ex: InnoMaker double port). Adressez un Bus 1 indépendant qui descend le long de la jambe gauche, et un Bus 2 pour la jambe droite.
*   **Terminaison** : Placez les résistances de **120 Ω** sur l'interface maître USB2CAN, ainsi que sur le circuit du TOUT DERNIER moteur en bout de **chaque** bus (le pied de chaque jambe).

#### Module de Débogage Pré-Assemblage (R-Link)
Pour initialiser vos moteurs, calibrer le firmware et attribuer les ID (1, 2, 3...) via la suite *RobStride Studio*, **un seul module R-Link (USB vers CAN) est suffisant** pour tout votre banc de test.
> [!IMPORTANT]
> **Isolation Galvanique** : Veillez à acquérir une version du R-Link *avec* isolation galvanique (Optocoupleur). Faute de quoi, une erreur de câblage sur le banc de test pourrait balancer les 48V de la ligne de puissance directement dans votre port USB, détruisant instantanément la carte mère de votre ordinateur de développement.

___

## 3. Sony Spresense & OAK-D Pro

### OAK-D Pro (Vision)
*   Agit comme un capteur USB3.
*   Intègre une **IMU (BNO085/BMI270)** — **utilisée uniquement pour la stabilisation du regard**, pas pour l'équilibre du corps (voir [18 — Stratégie IMU](./18_Strategie_IMU_Fusion.md)).

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

### Topologie de Puissance (48V) : ÉTOILE OBLIGATOIRE

> [!CAUTION]
> **DANGER FONTE XT30 / Daisy-Chain** : S'il est tentant de chaîner les câbles de puissance d'un RS-04 à l'autre le long de la jambe (comme pour le data), c'est une manipulation **interdite et dangereuse**. Le petit connecteur XT30 au dos du moteur supporte **30A continu max**. Un RS-04 tire jusqu'à **90A en pic**. Un chaînage de puissance fondra immédiatement le premier connecteur de la cuisse, et causera une chute de tension extrême (*Under-voltage error*) pour la cheville. 

Le 48V de chaque moteur doit impérativement rejoindre un connecteur inoccupé de la carte de distribution centrale de la manière la plus directe possible (Topologie Étoile / Parallèle).

```text
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

## 4b. Câbles de Puissance Moteurs — Guide d'Achat et Longueurs

### Courants par Modèle de Moteur

| Moteur | Courant continu | Courant crête | AWG adapté | Utilisation D-Bot |
| :---: | :---: | :---: | :---: | :--- |
| **RS-05** | ~0.8 A | ~3 A | 20–22 AWG | Cou (Pan + Tilt) |
| **RS-00** | ~1.5 A | ~4 A | 20–22 AWG | Poignets Roll |
| **RS-02** | ~2 A | ~5 A | 18–20 AWG | Épaule Yaw |
| **RS-06** | ~4 A | ~10 A | 18–20 AWG | Coudes |
| **RS-03** | ~6 A | ~15 A | 18 AWG | Épaule Roll, Hanches R/Y, Chevilles |
| **RS-04** | ~10 A | ~22 A | **14–16 AWG** | Épaule Pitch, Hanche Pitch, Genoux |

### Stratégie Rationalisée — 2 Calibres Seulement

> [!TIP]
> Plutôt que d'acheter un calibre différent par moteur, **deux calibres couvrent toute la gamme** sans compromis critique :
> - **14 AWG** → RS-04 uniquement (les plus gourmands)
> - **18 AWG silicone souple** → Tous les autres moteurs (RS-05, RS-00, RS-02, RS-06, RS-03)
>
> Le 18 AWG est certifié pour 16A continu. Le RS-03 pointe brièvement à 15A — largement toléré. Ce compromis évite de gérer 4-5 calibres différents.

### Wanptek — Quelle borne utiliser ?

> [!WARNING]
> La Wanptek DPS605U (et les alimentations de labo similaires) dispose de **3 bornes de sortie** :
> - **(+)** : +24V/48V du circuit → brancher vos XT30/XT60 (+) moteurs ✅
> - **(-)** : 0V du circuit (masse de référence) → brancher vos XT30/XT60 (-) moteurs ET le GND du module de debug CAN ✅
> - **(⏚ GND)** : Terre de sécurité secteur (PE, reliée à la prise murale) → **ne rien brancher dessus** ❌
>
> Brancher le module de debug sur la borne ⏚ au lieu de (-) = référence CAN flottante = erreurs "Bus Off" immédiates.

### Longueurs Estimées par Zone — Câble 14 AWG (RS-04)

Distance PDB (bassin/torse) → moteur, par conducteur :

| Moteur | Qty | Longueur estimée | Total par couleur |
| :--- | :---: | :---: | :---: |
| Épaule Pitch (RS-04 ×2) | 2 | ~50 cm | 1.0 m |
| Hanche Pitch (RS-04 ×2) | 2 | ~30 cm | 0.6 m |
| Genou (RS-04 ×2) | 2 | ~60 cm | 1.2 m |
| **Sous-total** | 6 | | **2.8 m** |
| Marge 30% | | | **+0.8 m** |
| **Total à avoir par couleur** | | | **~3.6 m** |

> Une bobine de **5m par couleur** (rouge + noir) couvre tous les RS-04 avec marge confortable.

### Longueurs Estimées par Zone — Câble 18 AWG (Tous les autres)

| Zone | Moteurs | Qty | Longueur/moteur | Total par couleur |
| :--- | :---: | :---: | :---: | :---: |
| Cou | RS-05 | 2 | 40 cm | 0.8 m |
| Poignets | RS-00 | 2 | 80 cm | 1.6 m |
| Épaule Yaw | RS-02 | 2 | 55 cm | 1.1 m |
| Coudes | RS-06 | 2 | 70 cm | 1.4 m |
| Épaule Roll | RS-03 | 2 | 55 cm | 1.1 m |
| Hanches Roll/Yaw | RS-03 | 4 | 25 cm | 1.0 m |
| Chevilles | RS-03 | 4 | 65 cm | 2.6 m |
| **Sous-total** | **18** | | | **9.6 m** |
| Marge 30% | | | | **+2.9 m** |
| **Total à avoir par couleur** | | | | **~12.5 m** |

> Commander **15m par couleur** (rouge + noir) en 18 AWG silicone.

### Recommandations d'Achat (disponible en France)

| Câble | Format | Où acheter | Recherche | Prix estimé |
| :--- | :--- | :--- | :--- | :---: |
| 14 AWG silicone rouge | Bobine séparée 5m | Amazon.fr | `"silicone wire 14AWG red 5m"` | ~10-15 € |
| 14 AWG silicone noir | Bobine séparée 5m | Amazon.fr | `"silicone wire 14AWG black 5m"` | ~10-15 € |
| **18 AWG silicone rouge** | **Bobine séparée 15m** | Amazon.fr | `"silicone wire 18AWG red 15m"` | ~15-20 € |
| **18 AWG silicone noir** | **Bobine séparée 15m** | Amazon.fr | `"silicone wire 18AWG black 15m"` | ~15-20 € |

> [!IMPORTANT]
> **Fils séparés, pas bipolaires.** Acheter des bobines **rouge et noir séparément** (pas un câble bipolaire avec les 2 conducteurs dans la même gaine). Dans un robot, le + et le - d'un même moteur passent souvent par des chemins légèrement différents dans les passages d'articulation. Des fils séparés offrent la flexibilité de routing nécessaire et sont plus faciles à passer dans les passages étroits.
>
> **Silicone obligatoire** (pas PVC) : la gaine silicone reste souple à froid, résiste à 200°C, et supporte les flexions répétées dans les articulations mobiles.

### Récapitulatif Budget Câble Puissance

| Achat | AWG | Quantité | Statut | Prix |
| :--- | :---: | :---: | :---: | :---: |
| 14 AWG rouge + noir | 14 | 5m × 2 couleurs | ✅ Déjà acheté | — |
| **18 AWG rouge + noir silicone** | 18 | 15m × 2 couleurs | 🛒 À acheter | **~30-40 €** |
| **Total investissement câble puissance** | | | | **~30-40 €** |

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
