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

### Principe du Bus CAN

Le bus CAN (Controller Area Network) est le protocole de communication entre la Jetson et tous les moteurs RobStride. Il fonctionne sur 3 fils :
- **CAN_H** et **CAN_L** : la paire différentielle (signal)
- **GND** : la masse commune — **critique**, sans elle le signal "flotte" et génère des erreurs "Bus Off"

Tous les moteurs d'un même bus sont **chaînés en série** (daisy-chain), du premier au dernier. Le dernier moteur doit porter une **résistance de terminaison 120 Ω**.

---

### Combien de bus CAN et pourquoi ?

> [!NOTE]
> Ce n'est pas un choix arbitraire — c'est **une contrainte physique du protocole CAN** qui impose le découpage en zones.

**Calcul de capacité par bus (1 Mbps) :**
- Taille d'une trame RobStride (position + vitesse + couple) : ~130 bits
- Boucle de contrôle cible : **1 kHz** (1000 commandes/sec/moteur)
- Bande passante consommée par moteur : **~130 kbps**
- Capacité maximale théorique : 1000 / 130 ≈ **7 moteurs**
- **Règle pratique retenue : 5-6 moteurs par bus** (marge pour les acquittements et les pics)

| Bus CAN | Moteurs | Nb | % bande passante |
| :--- | :--- | :---: | :---: |
| **Bus Cou** | RS-05 Pan + RS-05 Tilt | **2** | ~26% ✅ |
| **Bus Jambe G** | RS-04 ×2, RS-03 ×4 | **6** | ~78% ✅ |
| **Bus Jambe D** | RS-04 ×2, RS-03 ×4 | **6** | ~78% ✅ |

> **Les mains (Dynamixel XC430/XC330)** utilisent le protocole **TTL half-duplex** via le module **U2D2** — elles sont **entièrement indépendantes du bus CAN**. Aucun adaptateur CAN n'est nécessaire pour les mains.

---

### Choix du matériel USB2CAN — Étude Comparative

Trois options ont été évaluées :

| Option | Format | Prix total | Ports USB | Isolation | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **4× InnoMaker USB2CAN-C** (simple) | Boîtier ~80×50mm | ~120€ | 4+ | ✅ | Trop encombrant |
| **2× InnoMaker USB2CAN-X2** (dual) | Boîtier ~80×50mm | ~160€ | 2 | ✅ | Cher |
| **1× InnoMaker + 3× CANable Pro** | PCB nu **45×16mm** | **~100-130€** | 4 (hub) | **✅ Isolation 2.5kV** | **✅ Retenu** |

#### Architecture Définitive Retenue

| Adaptateur | Bus | Moteurs | Statut |
| :--- | :--- | :--- | :--- |
| **InnoMaker USB2CAN-C** | Bus Cou | RS-05 Pan + RS-05 Tilt | ✅ Acheté |
| **CANable Pro n°1** | Bus Bras G | 5 moteurs RS | À acheter |
| **CANable Pro n°2** | Bus Bras D | 5 moteurs RS | À acheter |
| **CANable Pro n°3** | Bus Jambe G | 6 moteurs RS | À acheter |
| **CANable Pro n°4** | Bus Jambe D | 6 moteurs RS | À acheter |

> **Note** : 4 CANable Pro sont nécessaires pour les membres. Si le budget est contraint, un 1er achat de 3 CANable Pro suffit pour les 2 bras + 1 jambe (Phase 2-3), le 4e s'achète en Phase 4 avec les jambes.

Le **CANable Pro** est la version avec **isolation galvanique 2.5kV** du CANable 2.0 open-source, au même format ultra-compact (45 × 16 mm). Avec le firmware **candleLight**, il apparaît nativement comme interface `gs_usb` sous Linux — identique à l'InnoMaker.

**Sources d'achat :**
- **[openlightlabs.com](https://openlightlabs.com)** : fabricant officiel, ~45 USD, qualité garantie
- **AliExpress** : chercher `"CANable Pro isolated 2.5kV"` ou `"USB CAN isolated candleLight"`, ~20-35€
- **[Tindie.com](https://tindie.com)** : vendeurs vérifiés, ~30-40€

> [!WARNING]
> Sur AliExpress, vérifier que la fiche mentionne explicitement **"2.5kV galvanic isolation"**. Les CANable 2.0 standard (sans isolation) sont souvent vendus sous le même nom.

```
Jetson Orin Nano
    └── Hub USB (modèle à choisir après liste complète des périphériques)
         ├── InnoMaker USB2CAN-C (✅ Acheté) → Bus Cou    (RS-05 ×2)
         ├── CANable Pro n°1    (à acheter) → Bus Bras G (RS-04/03/02/06/00)
         ├── CANable Pro n°2    (à acheter) → Bus Bras D (idem)
         ├── CANable Pro n°3    (à acheter) → Bus Jambe G (RS-04 ×2 + RS-03 ×4)
         └── CANable Pro n°4    (à acheter) → Bus Jambe D (idem)

Dynamixel (Mains) :
    └── Hub USB → U2D2 Main G  (TTL, indépendant CAN)
    └── Hub USB → U2D2 Main D  (TTL, indépendant CAN)
```

---

### Topologie du Câblage Data (CAN) par Bus

> [!CAUTION]
> **Interdiction absolue de faire un "Y" (étoile)** : Ne dérivez jamais le câble CAN. Les stubs > 30 cm corrompent le signal à 1 Mbps.

```
CANable/InnoMaker
      │
   Moteur ID-1 ── Moteur ID-2 ── ... ── Moteur ID-N
                                               │
                                      [Résistance 120 Ω]
```

**Règles :**
1. Chaque moteur a un **ID unique sur son bus** (configurer via module de debug avant montage)
2. La résistance **120 Ω** se place **uniquement sur le dernier moteur** de la chaîne
3. Le fil **GND** doit relier l'adaptateur CAN à la masse commune moteurs (borne **-** du busbar)

**Couleurs des fils RobStride :**
- **CAN_H** → Fil Jaune
- **CAN_L** → Fil Blanc
- **GND** → Fil Noir

---

### Module de Debug (✅ Déjà Acheté)

Le module de debug est un outil de **configuration uniquement** — il ne sert pas à faire tourner le robot en conditions normales. Il sert à :
- Attribuer les **ID uniques** (1, 2, 3...) à chaque moteur via *RobStride Studio*
- Mettre à jour les firmwares moteurs
- Tester un moteur individuellement sur le banc

**Un seul module de debug suffit** pour configurer tous vos moteurs, un à un.

> [!IMPORTANT]
> **Isolation galvanique obligatoire** : Votre module de debug possède une isolation galvanique (optocoupleur). C'est indispensable pour protéger votre PC lors des sessions de debug sur le banc avec le 48V.

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
2.  Régler la limite de courant à **3.0A** pour 2× RS-05 (voir [Doc 33 §1](./annexes/robstride/configuration_initiale/33_Test_Multi_Moteurs_CAN_Banc.md) pour le détail par moteur).
3.  Activer le mode **OCP** (Overcurrent Protection).
4.  Séquence : Allumer l'alim → Vérifier tension → Brancher XT30 → `Enable` logiciel.

> [!TIP]
> **Manuel Utilisateur** : Le manuel de la Wanptek est disponible ici : [dps605U.pdf](./manuels/dps605U.pdf).

> [!WARNING]
> **3 bornes Wanptek : (+), (-) et (⏚ GND).** Brancher les moteurs et le module de debug sur la borne **(-)** uniquement. La borne **(⏚ GND)** est la terre de protection secteur (PE) — ne rien brancher dessus. Voir [Doc 04 §4b](./04_Electronique_Cablage.md#4b-c%C3%A2bles-de-puissance-moteurs--guide-dachat-et-longueurs) pour le détail.

> [!IMPORTANT]
> **Pourquoi couper les fils pré-étamés d'usine ?**
> Les moteurs arrivent avec des fils étamés (soudure au bout) pour faciliter la soudure sur PCB. Cependant, pour une **connexion mécanique** (WAGO à ressort ou Cosse ronde à sertir), l'étain est trop rigide et "flue" (se déforme) avec le temps, ce qui peut desserrer la connexion. 
> **Action** : Coupez les 5 derniers mm d'étain pour retrouver le cuivre nu souple avant de l'insérer dans un WAGO ou une cosse.

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

### Choix de Batteries — Stratégie Progressive (Avril 2026)

> [!IMPORTANT]
> **Stratégie retenue : Progressive en 2 phases.** La forme finale du torse n'étant pas encore validée, l'espace batterie exact est inconnu. On démarre avec une batterie **standard VAE 48V** (format rectangulaire universel, achat immédiat) pour prototyper, puis on passera à du **sur-mesure** (forme optimisée pour le CdG du robot) une fois le châssis figé.

---

#### Phase 1 — Prototype : Batterie VAE Standard 48V (Achat Immédiat)

Une batterie de vélo électrique 48V (13S) est le choix le plus pragmatique pour le prototype :
- Disponible immédiatement sur Amazon.fr, AliExpress, ou chez des spécialistes FR
- BMS 13S intégré avec protection (surcharge, sous-tension, court-circuit)
- Connecteur XT60 ou Anderson souvent inclus
- Format boîte rectangulaire « universel » facile à fixer avec du Velcro

| Paramètre | Spécification Recherchée |
| :--- | :--- |
| **Chimie** | Li-ion NMC (18650 ou 21700) |
| **Tension** | 48V nominale (13S), 54.6V max charge |
| **Capacité** | 10 Ah minimum (480 Wh) |
| **BMS** | 30A continu minimum (50A+ recommandé) |
| **Connecteur** | XT60 pré-câblé (ou adaptable) |
| **Poids** | 2.5–4.0 kg selon les cellules |
| **Budget** | 180–350 € TTC |

**Où acheter (vérifié accessible en France, Avril 2026) :**

| Source | Type | Prix | Avantage | Lien |
| :--- | :--- | :---: | :--- | :--- |
| **Save My Battery** | Assemblage FR, cellules marque | ~300–450 € | 🇫🇷 SAV français, cellules Samsung/LG | [savemybattery.fr](https://www.savemybattery.fr) |
| **Yose Power** | VAE standard, stock EU | ~200–300 € | Livraison rapide Europe, bon rapport qualité/prix | [yosepower.com](https://www.yosepower.com) |
| **Amazon.fr / AliExpress** | VAE générique | ~180–280 € | Achat immédiat, livraison 48h-7j | Recherche : `"batterie 48V 13S 10Ah BMS"` |

> [!WARNING]
> **Vérifier impérativement** avant achat :
> - Le **BMS est bien 13S** (pas 12S = 44.4V incompatible)
> - Le courant de décharge continu est **≥ 30A** (les batteries VAE bas de gamme sont parfois limitées à 15-20A)
> - Le connecteur de sortie (XT60 de préférence, sinon Anderson PP30 ou PP45)
> - Les avis récents (éviter les batteries avec cellules reconditionnées)

---

#### Phase 2 — Production : Batterie Sur-Mesure (Quand le Châssis est Figé)

Une fois le torse CAO validé et l'espace batterie défini, passer commande chez un assembleur français :

| Fournisseur | Spécialité | Avantage | Contact |
| :--- | :--- | :--- | :--- |
| **[Save My Battery](https://www.savemybattery.fr)** | Assemblage NMC sur mesure | 🇫🇷 FR, cellules Samsung 50E, forme custom | Via site web |
| **[OZO Industries](https://www.ozo-electric.com)** | NMC/LFP custom, bureau d'études | 🇫🇷 FR (Éguilles), BMS CAN possible | batteries@ozo-electric.com |
| **[Neogy](https://www.neogy.fr)** | Batteries haute performance | 🇫🇷 FR, expertise robotique et mobilité | Via site web |

**Cahier des charges à fournir** :
- Tension : 48V (13S NMC)
- Capacité : 10-15 Ah (480-720 Wh)
- Courant continu : 50A minimum, pic 100A
- Dimensions max : à définir selon le torse CAO
- Connecteur : XT90-S (anti-spark) ou Anderson SB50
- BMS : avec sortie monitoring (idéalement CAN ou UART pour la Jetson)
- Budget : 400-700 €

---

#### Pourquoi NMC et pas LiFePO4 ?

| Critère | NMC 21700 | LiFePO4 |
| :--- | :--- | :--- |
| **Densité massique** | ~250 Wh/kg | ~160 Wh/kg |
| **Poids pour 480 Wh** | **~2.0-2.5 kg** | ~3.0-4.0 kg |
| **Tension/cellule** | 3.6V → 13S = 46.8V ✅ | 3.2V → 15S nécessaire ❌ |
| **Cycles** | 800-1000 | 2000-6000 |
| **Sécurité** | ⚠️ BMS indispensable | ✅ Plus stable chimiquement |
| **Verdict** | **Retenu** (poids critique pour bipède) | Exclu (trop lourd, 15S incompatible) |

---

### Sécurité Incendie (NMC)

- ✅ Utiliser uniquement des **packs fermés avec BMS dédié** (jamais de cellules nues)
- ✅ **Espace d'air** autour de la batterie dans le torse
- ✅ **Cloisonnement** en matériaux ignifugés (PC/ABS, tôle alu)
- ✅ **Sortie de dégazage** vers l'arrière (ne pas enfermer hermétiquement)
- ✅ **Charge** uniquement avec chargeur **54.6V (13S) CC/CV** dédié, en zone ventilée
- ✅ **Monitoring** température/tension/courant via Spresense (harnais faible puissance du BMS)

### Positionnement dans le Robot

- **Phase Prototype** : Batterie VAE fixée par Velcro industriel + sangle dans le torse bas, accessible par trappe arrière
- **Phase Production** : Pack sur-mesure intégré dans un slot CAO dédié avec patin anti-vibration TPU
- **Dimensions à prévoir** : ~200 × 100 × 70 mm minimum (format VAE standard)

> [!TIP]
> **Évolution future** : Quand le design du torse sera figé, une 2ème batterie identique pourra être ajoutée en parallèle (symétrie gauche/droite) pour doubler l'autonomie (~40-50 min → ~80-100 min). Les 2 packs DOIVENT être identiques (même modèle, même âge). Utiliser un ORing MOSFET pour éviter les courants d'équilibrage.

### Topologie de Puissance (48V) : ÉTOILE OBLIGATOIRE

> [!CAUTION]
> **DANGER FONTE XT30 / Daisy-Chain** : S'il est tentant de chaîner les câbles de puissance d'un RS-04 à l'autre le long de la jambe (comme pour le data), c'est une manipulation **interdite et dangereuse**. Le petit connecteur XT30 au dos du moteur supporte **30A continu max**. Un RS-04 tire jusqu'à **90A en pic**. Un chaînage de puissance fondra immédiatement le premier connecteur de la cuisse, et causera une chute de tension extrême (*Under-voltage error*) pour la cheville.

Le 48V de chaque moteur doit impérativement rejoindre la barre de distribution centrale de la manière la plus directe possible (Topologie Étoile / Parallèle).

### Distribution : Système Busbar + Pigtails (Sans Soudure)

> [!WARNING]
> **Le Matek PDB-HEX (drone) est INCOMPATIBLE** avec le bus 48V du D-Bot (tension max 18V). Ne pas utiliser de PDB drone standard.

#### Architecture Retenue : Distribution Hiérarchique "Arbre" (Standard Industrie)

L'architecture de distribution du D-Bot suit le modèle hiérarchique utilisé par les robots humanoïdes industriels (Unitree H1/G1, Tesla Optimus) : un **busbar central compact** dans le torse qui alimente **des lignes "tronc" fusionnées par zone**, chacune aboutissant à un **splitter local** dans chaque membre.

> [!NOTE]
> **Pourquoi pas un busbar géant à 27 bornes ?** Avec 24 moteurs + 3 convertisseurs, un busbar unique dans le torse serait un nœud de 27 paires de câbles — ingérable, lourd, et sans isolation de fautes. En découpant en zones avec des splitters locaux, on obtient :
> - Seulement **7 câbles "tronc"** qui quittent le torse (au lieu de 27)
> - **Protection fusible par zone** → un court-circuit dans une jambe ne coupe pas les bras
> - **Déconnexion rapide** d'un membre entier via un seul connecteur XT60
> - Câbles courts vers les moteurs (< 30 cm) → moins de chutes de tension

#### Vue Globale — Topologie en Arbre

```
                    ┌─────────────────────────────────────────────┐
                    │          TORSE (Busbar Central 8 bornes)     │
                    │                                             │
     Batterie ──── Fusible 80A ──── E-Stop ──── BUSBAR (+ / -)   │
                    │                 │                            │
                    │    ┌────────────┼────────────┐              │
                    │    │            │            │              │
                    └────┼────────────┼────────────┼──────────────┘
                         │            │            │
                    ┌────┴───┐   ┌────┴───┐   ┌───┴──────┐
                    │ Tronc  │   │ Tronc  │   │  Tronc   │
                    │ Bras G │   │ Bras D │   │ Logique  │
                    │ 30A    │   │ 30A    │   │ 5V / 19V │
                    └───┬────┘   └───┬────┘   └──────────┘
                        │            │
              ┌─────────┴──┐   ┌────┴─────────┐
              │Splitter    │   │Splitter       │
              │Bras G      │   │Bras D         │
              │(WAGO/mini  │   │(WAGO/mini     │
              │ busbar)    │   │ busbar)       │
              └────────────┘   └───────────────┘

     ┌────────────┐  ┌────────────┐
     │ Tronc      │  │ Tronc      │
     │ Jambe G    │  │ Jambe D    │
     │ 50A        │  │ 50A        │
     └─────┬──────┘  └─────┬──────┘
           │               │
     ┌─────┴──────┐  ┌─────┴──────┐
     │Splitter    │  │Splitter    │      ┌────────────┐
     │Jambe G     │  │Jambe D     │      │ Tronc      │
     │(mini       │  │(mini       │      │ Cou / Tête │
     │ busbar)    │  │ busbar)    │      │ 5A         │
     └────────────┘  └────────────┘      └────────────┘
```

#### Découpage en 7 Zones

| Zone | Moteurs / Charges | N° moteurs | Fusible | AWG tronc | Connecteur tronc |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Bras G** | RS-04 + RS-03 + RS-02 + RS-06 + RS-00 + Buck→12V | 5 + 1 | **30A** | **14 AWG** | XT60 |
| **Bras D** | (idem) | 5 + 1 | **30A** | **14 AWG** | XT60 |
| **Jambe G** | RS-04 × 2 + RS-03 × 3 + RS-02 | 6 | **50A** | **12 AWG** | XT60 |
| **Jambe D** | (idem) | 6 | **50A** | **12 AWG** | XT60 |
| **Cou / Tête** | RS-05 × 2 | 2 | **5A** | **18 AWG** | XT30 |
| **Logique** | DC-DC 48V→5V (Spresense) + DC-DC 48V→19V (Jetson) | 0 | **5A** | **18 AWG** | fils vissés |
| **E-Stop** | Bouton arrêt d'urgence NC | — | — | — | panneau |
| **TOTAL bornes sur busbar central** | | | | | **7 paires (+/-)** |

> **Résultat** : le busbar central n'a besoin que de **~8 bornes par rail** (7 zones + 1 entrée batterie) → un **busbar double 8-12 bornes** unique suffit pour le robot complet.

#### Rôle des WAGO 221 (✅ Déjà Achetés)

> [!TIP]
> **Les WAGO 221-413 (3 entrées) et 221-415 (5 entrées) sont les splitters locaux** à l'intérieur de chaque membre. Ils ne remplacent pas le busbar central — ils font le travail de distribution finale après le tronc fusionné.

```
Exemple — Splitter Bras G (situé dans l'épaule ou haut du bras) :

Câble Tronc 14 AWG (XT60 depuis busbar)
    │
    └── WAGO 221-415 (5 entrées, 32A max)
         ├── (+) → XT60 pigtail → RS-04 Épaule Pitch      14 AWG
         ├── (+) → XT30 pigtail → RS-03 Épaule Roll        18 AWG
         ├── (+) → XT30 pigtail → RS-02 Épaule Yaw         18 AWG
         ├── (+) → XT30 pigtail → RS-06 Coude Pitch        18 AWG
         └── (+) → XT30 pigtail → RS-00 Poignet Roll       18 AWG

    └── WAGO 221-415 (5 entrées) → même chose pour le (-)

    └── Buck 48V→12V 5A → WAGO 221-413 (3 entrées) → 8 Dynamixel main
```

**Pourquoi les WAGO et non un mini-busbar dans le membre ?**
- Les WAGO 221 sont compacts (18×6×16mm), sans outil (levier), et supportent **32A / 450V** → bien au-delà de nos besoins
- Ils acceptent du **0.2 à 4 mm²** (24 à 12 AWG) → parfait pour mixer 14 et 18 AWG
- Ils sont transparents → vérification visuelle du contact
- **Déjà achetés** ✅

> [!WARNING]
> Les WAGO 221 sont adaptés pour les **bras et le cou** (courant par zone ≤ 30A). Pour les **jambes** (50A par zone avec 2× RS-04 + 3× RS-03), utilisez un **mini-busbar 6 bornes** comme splitter local au lieu des WAGO (limités à 32A de capacité nominale).

#### Schéma Détaillé de Distribution

```text
Batterie 13S NMC 48V (XT90-S / Anderson SB50)
    │
    ├── Fusible principal 80A (ANL/MIDI lame)
    │
    ├── E-Stop (Coup de poing NC — coupe moteurs, pas Jetson)
    │
    └── BUSBAR CENTRAL DOUBLE 8-12 bornes (torse)
         │
         │  ═══ ZONE BRAS GAUCHE ═══════════════════════════════
         ├── Fusible 30A lame ──→ XT60 tronc (14 AWG, ~40cm)
         │   └── Splitter Bras G (WAGO 221-415 × 2, dans épaule)
         │        ├── XT30 → RS-04 Épaule Pitch G      (14 AWG, ~15cm)
         │        ├── fils → RS-03 Épaule Roll G       (18 AWG, ~15cm)
         │        ├── fils → RS-02 Épaule Yaw G        (18 AWG, ~20cm)
         │        ├── fils → RS-06 Coude G             (18 AWG, ~40cm)
         │        ├── fils → RS-00 Poignet G           (18 AWG, ~60cm)
         │        └── Buck 48V→12V → 8× Dynamixel main G
         │
         │  ═══ ZONE BRAS DROIT ════════════════════════════════
         ├── Fusible 30A lame ──→ XT60 tronc (14 AWG, ~40cm)
         │   └── Splitter Bras D (idem)
         │
         │  ═══ ZONE JAMBE GAUCHE ══════════════════════════════
         ├── Fusible 50A lame ──→ XT60 tronc (12 AWG, ~30cm)
         │   └── Mini-busbar 6 bornes (bassin G)
         │        ├── XT30 → RS-04 Hanche Pitch G      (14 AWG, ~15cm)
         │        ├── fils → RS-03 Hanche Roll G       (18 AWG, ~15cm)
         │        ├── fils → RS-03 Hanche Yaw G        (18 AWG, ~20cm)
         │        ├── XT30 → RS-04 Genou G             (14 AWG, ~50cm)
         │        ├── fils → RS-03 Cheville Pitch G    (18 AWG, ~80cm)
         │        └── fils → RS-03 Cheville Roll G     (18 AWG, ~80cm)
         │
         │  ═══ ZONE JAMBE DROITE ══════════════════════════════
         ├── Fusible 50A lame ──→ XT60 tronc (12 AWG, ~30cm)
         │   └── Mini-busbar 6 bornes (bassin D, idem)
         │
         │  ═══ ZONE COU / TÊTE ═══════════════════════════════
         ├── Fusible 5A ──→ fils tronc (18 AWG)
         │   └── WAGO 221-413
         │        ├── fils → RS-05 Cou Pan             (18 AWG, ~20cm)
         │        └── fils → RS-05 Cou Tilt            (18 AWG, ~20cm)
         │
         │  ═══ ZONE LOGIQUE ══════════════════════════════════
         └── DC-DC 48V→5V (Spresense always-on)
             DC-DC 48V→19V (Jetson Orin Nano)
```

#### Avantages de cette Architecture

| Critère | Busbar plat (ancienne) | Arbre hiérarchique (retenue) |
| :--- | :---: | :---: |
| Câbles au torse | 27 paires | **7 paires** |
| Isolation de faute | Non (1 fusible 80A) | **Oui (fusible par zone)** |
| Déconnecter un bras | 5 vis au busbar | **1 XT60** |
| Longueur câble max | 1.2m (busbar→cheville) | **0.8m (splitter→cheville)** |
| Nœud de câbles torse | ❌ Dense | **✅ Aéré** |
| Extension/maintenance | Compliqué | **Modulaire** |
| Standard industriel | Non | **Oui (Unitree, Tesla)** |

#### Composants du Système Complet

| Composant | Spécification | Qté | Prix | Source |
| :--- | :--- | :---: | :---: | :--- |
| **Busbar double (12 bornes M4)** | Laiton étamé, 150A, couvercle anti-étincelle | 1 | ✅ Acheté | Amazon / Marine Grade |
| **Mini-busbars 6 bornes** | Laiton, 60V+, pour bassin jambes | 2 | ~8-12 €/pce | Amazon.fr : `"bus bar 6 way 60V"` |
| **WAGO 221-415 (5 entrées)** | Levier, 32A, 450V, 0.2-4mm² | 4 (×2 par bras) | ✅ Déjà achetés | — |
| **WAGO 221-413 (3 entrées)** | Levier, 32A, 450V | 6 | ✅ Déjà achetés | — |
| **Fusibles lame + porte-fusibles** | 30A ×2 (bras) + 50A ×2 (jambes) + 5A ×1 (cou) + 80A ×1 (principal) | 6 | ~3-5 € le lot | Amazon.fr : `"porte-fusible lame automobile en ligne"` |
| **Connecteurs XT60/XT30 nus** | Mâle/Femelle (pré-étamés) | 1 lot | ✅ Déjà achetés | Fabrication pigtails moteurs & troncs |
| **Câble 18 AWG Silicone** | Rouleau 30m (Rouge + Noir) | 1 | ✅ Acheté | Liaison petits moteurs (RS-05, 00, 02, 06, 03) |
| **Câble 14 AWG Silicone** | 5m (Rouge + Noir) | 1 | ✅ Acheté | Liaison gros moteurs (RS-04) |
| **DC-DC 48V→5V** | Buck isolé, 5V 5A (25W) | 1 | ~10-15 € | Amazon.fr : `"48V to 5V DC-DC converter 5A"` |
| **DC-DC 48V→19V** | Buck, 19V 5A (95W) | 1 | ~15-20 € | Amazon.fr : `"48V to 19V DC-DC converter 5A"` |
| **Buck 48V→12V 5A** | Entrée ≥ 60V, sortie 12V 5A | 2 | ~10-18 €/pce | Amazon.fr : `"DC DC converter 48V 12V 5A 60W"` |
| **Bouton E-Stop** | Coup de poing NC | 1 | ~8-12 € | Amazon.fr |
| **Total estimé** | | | **~60-80 €** | |

#### Où Trouver les Busbars

> [!TIP]
> **Le secteur nautique** (bateaux) fabrique exactement ces composants pour la distribution DC 12V/24V/48V avec des bornes robustes, couvercle de protection, et laiton étamé anti-corrosion. Ils supportent tous 60V+ malgré la mention "12/24V".

| Source | Terme de recherche | Avantage |
| :--- | :--- | :--- |
| **Amazon.fr** | `"dual bus bar 12 way"` ou `"bus bar 6 way marine"` | Livraison rapide, ~10-25 € |
| **SVB Marine** ([svb24.com](https://www.svb24.com)) | Blue Sea Systems, BEP Marine | Qualité premium, couvercle inclus |
| **Seatronic.fr** ([seatronic.fr](https://www.seatronic.fr)) | "Bornier de raccordement" | Spécialiste FR, bon SAV |
| **RS Components** ([fr.rs-online.com](https://fr.rs-online.com)) | "Power distribution block" | Qualité industrielle |

**Checklist avant achat busbar** :
- ✅ **Laiton étamé** (pas aluminium pur)
- ✅ **Couvercle transparent** (anti court-circuit)
- ✅ Bornes acceptant **12-14 AWG** (≥ 2.5 mm²)
- ✅ Courant nominal **≥ 100A** par rail

#### Câblage Mixte (Sur-mesure + Sans Soudure)

L'avantage d'avoir vos propres connecteurs nus est de pouvoir fabriquer des câbles pile à la bonne longueur. Le câblage se fait en deux étapes :

**1. Côté Connecteurs (XT60 / XT30) : Soudure (RS-04 et Troncs uniquement)**
*   **Connexion Moteur ↔ WAGO** : Seul le gros moteur **RS-04** possède un connecteur (XT30 Mâle) d'origine. Vous devez lui fabriquer un "pigtail" : soudez un XT30 *Femelle* aux fils rouge/noir, et l'autre extrémité ira dans le WAGO. 
*   **Pour tous les autres moteurs (RS-03, RS-02, RS-06...)** : Leurs câbles sont nus et pré-étamés d'usine. **Ne soudez aucun connecteur !** Coupez juste le petit bout étamé avec une pince coupante pour retrouver le cuivre pur souple, puis insérez-le directement dans le WAGO ou la cosse ronde.
*   **Troncs Détachables (Busbar ↔ Membre)** : Soudez un XT60 *Femelle* sur le câble qui part du torse. Soudez un XT60 *Mâle* sur celui qui part du bras/jambe. Pour retirer le membre, il suffit de déclipser cette prise.
*   *Note équipement* : Le câble 14 AWG et les XT60 pompent beaucoup de chaleur. Utilisez un fer puissant (≥ 60W) et n'oubliez pas la gaine thermo-rétractable.

**2. Côté Busbar et WAGO : Interdiction de souder !**
Une fois les XT soudés, l'autre extrémité de vos fils (qui se banche sur les répartiteurs) ne doit **jamais** être soudée ou étamée (l'étain est mou et se desserre avec le temps sous la pression).

```
WAGO 221 (dans les bras et cou) ──────────────────────────────────
  1. Dénuder 12mm du câble silicone (cuivre nu pur)
  2. Ouvrir le levier orange
  3. Insérer le cuivre nu et fermer. Le ressort garantit la tension à vie.

BUSBAR CENTRAL / MINI-BUSBARS (vis M4) ───────────────────────────
  1. Dénuder le fil
  2. Insérer le cuivre nu dans une cosse ronde à sertir (Ring Terminal M4)
  3. Sertir fermement avec une vraie pince à sertir
  4. Visser la cosse sur le busbar.

  [XT60 soudé] ════ fil 14 AWG sur-mesure ════ [Cosse ronde sertie] ──> Vissé au Busbar
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

## 4c. Séquence de Validation — Wanptek → Batterie

La Wanptek DPS605U peut alimenter le busbar directement, exactement comme la batterie le ferait :

```
Wanptek (+) ──── Borne (+) busbar   ← fil 14 AWG, 30-50 cm
Wanptek (-) ──── Borne (-) busbar
                     │
                     ├── Pigtail XT30 → Moteur 1
                     ├── Pigtail XT30 → Moteur 2
                     └── Buck 48V→12V → Dynamixel (main)
```

La limite est le **courant maximum de la Wanptek : 5A**. Voici les zones de validité :

### Composition du Bras — Rappel (Pourquoi pas de "test bras complet" avec Wanptek)

| Articulation | Moteur/Servo | Protocole | Tension | Courant typique | Wanptek |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Épaule Pitch | **RS-04** | CAN | 48V | 10–22 A | ❌ |
| Épaule Roll | **RS-03** | CAN | 48V | 6–15 A | ❌ |
| Épaule Yaw | RS-02 | CAN | 48V | ~2–5 A | ✅ |
| Coude | RS-06 | CAN | 48V | ~4–10 A | ⚠️ |
| Poignet Roll | RS-00 | CAN | 48V | ~1.5–4 A | ✅ |
| Main ×4 XC430 | Dynamixel | TTL | **12V** | ~0.5 A/servo | ✅ via buck |
| Main ×4 XC330 | Dynamixel | TTL | **12V** | ~0.3 A/servo | ✅ via buck |

> [!IMPORTANT]
> Il n'existe **pas de test bras complet sans batterie** : l'épaule Pitch (RS-04) est l'articulation proximale. Par contre, le segment "coude → poignet → main" est entièrement testable avec la Wanptek + un buck 48V→12V.

### Intégration de la Main — Architecture Buck 48V→12V

La D-Hand utilise des servos **Dynamixel TTL à 12V**, totalement différents des RobStride (CAN, 48V). Un buck connecté sur le busbar 48V permet d'alimenter tout depuis la même source :

```
Wanptek 48V (ou batterie)
     │
     └──→ Busbar 48V / GND
               │
               ├──→ RS-06 (coude)      48V CAN
               ├──→ RS-02 (épaule yaw) 48V CAN
               ├──→ RS-00 (poignet)    48V CAN
               │
               └──→ Buck 48V→12V 5A
                    GND commun busbar ✅
                          │
                          └──→ U2D2 → XC430 ×4 + XC330 ×4
                                        12V TTL
```

**La masse GND est automatiquement commune** — tout part du même busbar. C'est aussi l'architecture définitive de production.

#### Budget Courant — Avant-Bras + Main avec Wanptek

| Composant | Courant @ 48V | Calcul |
| :--- | :---: | :--- |
| RS-06 coude | ~2 A | mouvement léger |
| RS-02 yaw | ~1 A | mouvement léger |
| RS-00 poignet | ~0.8 A | mouvement léger |
| Buck (→ 8 servos Dynamixel) | ~0.8 A | 12V×3A ÷ 48V ÷ 0.9 eff. |
| **Total** | **~4.6 A** | **≤ 5A Wanptek ✅** |

> Faisable pour des mouvements doux et séquentiels. Un pic RS-06 en accélération rapide déclenche l'OCP Wanptek — protection automatique, pas un problème.

#### Buck à Commander (Utile Maintenant + Indispensable en Production)

> [!WARNING]
> La batterie chargée est à **54.6V max**. Il faut un buck supportant **≥ 60V en entrée** — les modules limités à 40V ne conviennent pas.

| Spec | Valeur |
| :--- | :--- |
| Tension entrée max | **≥ 60V** |
| Tension sortie | 12V (réglable) |
| Courant sortie | **5A minimum** (60W) |
| Recherche Amazon.fr | `"DC DC converter 48V 12V 5A 60W"` ou `"step down 60V 12V 5A"` |
| Prix | ~10–18 € |
| Quantité | **2** (1 par bras, identiques en production) |

---

### Roadmap Complète — Tous les Tests Possibles par Segment

```
╔══════════════════════════════════════════════════════════════════════╗
║  ZONE WANPTEK SUFFISANTE (5A @ 48V)                                 ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1. CONFIGURATION INDIVIDUELLE — TOUS LES MOTEURS       < 1A ✅     ║
║     • ID unique (1..24), zéro mécanique, limites soft               ║
║     • RS-04 IDLE < 1A  (dès qu'il bouge → OCP)                     ║
║     • Outil : MotorStudio + module de debug                         ║
║     • Wanptek : 24V ou 48V, limite 1A par moteur                    ║
║                                                                      ║
║  2. SCAN CAN MULTI-MOTEURS                              ~0A ✅       ║
║     • Vérification adressage, baudrate, version firmware            ║
║     • Aucun mouvement = aucune limite courant                       ║
║                                                                      ║
║  3. TEST COU (2× RS-05)                                ~1–3A ✅     ║
║     • Pan + Tilt, mouvements amplitude complète                     ║
║     • Wanptek : 24V, limite 3A                                      ║
║                                                                      ║
║  4a. TEST AVANT-BRAS ROBSTRIDE ISOLÉ                   ~3–4A ✅     ║
║     • RS-06 (coude) + RS-02 (yaw) + RS-00 (poignet)                ║
║     • Pas d'épaule = pas de RS-04 ✅                                ║
║     • Mouvements séquentiels doux                                   ║
║                                                                      ║
║  4b. TEST MAIN DYNAMIXEL SEULE                         ~3A@12V ✅   ║
║     • Wanptek réglée à 12V (déconnecter RobStride)                  ║
║     • 8 servos via U2D2, Python SDK ou Dynamixel Wizard             ║
║     • Grip, amplitude doigts, mesure courant par servo              ║
║                                                                      ║
║  4c. TEST AVANT-BRAS + MAIN INTÉGRÉ                    ~4.6A ✅     ║
║     • Nécessite Buck 48V→12V sur busbar ← ACHETER AVANT             ║
║     • RS-06 + RS-02 + RS-00 (48V) + Dynamixel via buck (12V)       ║
║     • Gestes de préhension complets, mouvements doux               ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  ⚡ BATTERIE INDISPENSABLE (VAE 48V 13S) — Acheter avant étape 5    ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  5. PREMIER MOUVEMENT RS-04 / RS-03                    > 10A        ║
║     • Épaule pitch, hanche, genou, cheville                         ║
║     • Même un RS-04 à vide en accélération > 5A                    ║
║                                                                      ║
║  6. TEST BRAS COMPLET (épaule + avant-bras + main)                  ║
║     • 5 RobStride + 8 Dynamixel coordonnés                          ║
║     • Pick & place, gestes de manipulation                          ║
║                                                                      ║
║  7. TEST JAMBE                                                       ║
║     • RS-04 hanche pitch + genou                                    ║
║     • RS-03 hanche Roll/Yaw + cheville (×2 par cheville)            ║
║                                                                      ║
║  8. TEST DEBOUT — ÉQUILIBRE BIPÈDE STATIQUE                          ║
║     • Tous moteurs actifs                                            ║
║     • IMU BMI270 + FSR pieds en boucle de contrôle                 ║
║                                                                      ║
║  9. MARCHE DYNAMIQUE                                                 ║
║     • 2ème batterie recommandée (autonomie doublée)                 ║
║     • ORing MOSFET pour mise en parallèle des 2 packs              ║
╚══════════════════════════════════════════════════════════════════════╝
```

> [!TIP]
> **Avantage de la Wanptek en phases 1–4** : la limite OCP est une **protection active**. Une batterie peut débiter 100A dans un court-circuit et fondre les connecteurs — la Wanptek coupe proprement. Ne passez à la batterie qu'à l'étape 5.
>
> **Batterie à acheter avant l'étape 5.** Voir [§4 — Batterie Progressive](#choix-de-batteries--stratégie-progressive-avril-2026).

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
