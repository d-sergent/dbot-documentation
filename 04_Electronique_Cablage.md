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
2.  Régler la limite de courant à **3.0A** pour 2× RS-05 (voir [Doc 33 §1](./annexes/robstride/configuration_initiale/33_Test_Multi_Moteurs_CAN_Banc.md) pour le détail par moteur).
3.  Activer le mode **OCP** (Overcurrent Protection).
4.  Séquence : Allumer l'alim → Vérifier tension → Brancher XT30 → `Enable` logiciel.

> [!WARNING]
> **3 bornes Wanptek : (+), (-) et (⏚ GND).** Brancher les moteurs et le module de debug sur la borne **(-)** uniquement. La borne **(⏚ GND)** est la terre de protection secteur (PE) — ne rien brancher dessus. Voir [Doc 04 §4b](./04_Electronique_Cablage.md#4b-c%C3%A2bles-de-puissance-moteurs--guide-dachat-et-longueurs) pour le détail.

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

La solution retenue est un **système de busbars** (barres de distribution cuivre) avec des **pigtails XT60 pré-câblés** vissés aux bornes. C'est le standard industriel pour la robotique, **sans aucune soudure** :

#### Composants du Système

| Composant | Spécification | Qté | Prix | Source |
| :--- | :--- | :---: | :---: | :--- |
| **Busbar double** (+ et -) | Cuivre étamé, 60V/100A, 6-12 bornes à vis | 1 | ~15-25 € | Amazon.fr : `"busbar 12 positions 60V 100A"` |
| **Pigtails XT60 femelles** | XT60 femelle → fils nus 14 AWG, 30 cm | 8 | ~2-3 €/pièce | Amazon.fr : `"XT60 female pigtail 14AWG"` |
| **Pigtails XT30 femelles** | XT30 femelle → fils nus 18 AWG, 30 cm | 6 | ~1-2 €/pièce | Amazon.fr : `"XT30 female pigtail 18AWG"` |
| **DC-DC 48V→5V** | Buck converter isolé, 5V 5A (25W) | 1 | ~10-15 € | Amazon.fr : `"48V to 5V DC-DC converter 5A"` |
| **Fusible 80A + porte-fusible** | Lame automobile ANL/MIDI | 1 | ~5-8 € | Amazon.fr |
| **Bouton E-Stop** | Coup de poing NC + câble | 1 | ~8-12 € | Amazon.fr |
| **Total système** | | | **~60-90 €** | |

#### Schéma de Distribution

```text
Batterie 13S NMC (XT60 ou XT90-S)
    │
    ├── Fusible 80A (lame automobile)
    │
    ├── E-Stop (Bouton d'arrêt d'urgence, NC)
    │
    └── BUSBAR DOUBLE (+ et -)  ← Barres cuivre avec bornes à vis
         │
         │   [Pigtails XT60 vissés aux bornes — gros moteurs]
         ├── XT60 → RS-04 Épaule Pitch G     (14 AWG)
         ├── XT60 → RS-04 Épaule Pitch D     (14 AWG)
         ├── XT60 → RS-04 Hanche Pitch G     (14 AWG)
         ├── XT60 → RS-04 Hanche Pitch D     (14 AWG)
         ├── XT60 → RS-04 Genou G            (14 AWG)
         ├── XT60 → RS-04 Genou D            (14 AWG)
         │
         │   [Pigtails XT30/XT60 — moteurs moyens]
         ├── XT60 → RS-03 Épaule Roll G      (18 AWG)
         ├── XT60 → RS-03 Épaule Roll D      (18 AWG)
         ├── XT30 → RS-03 Hanche Roll G      (18 AWG)
         ├── XT30 → RS-03 Hanche Roll D      (18 AWG)
         ├── XT30 → RS-03 Hanche Yaw G       (18 AWG)
         ├── XT30 → RS-03 Hanche Yaw D       (18 AWG)
         ├── XT30 → RS-03 Cheville G ×2      (18 AWG)
         ├── XT30 → RS-03 Cheville D ×2      (18 AWG)
         │
         │   [Pigtails XT30 — petits moteurs]
         ├── XT30 → RS-06 Coude G            (18 AWG)
         ├── XT30 → RS-06 Coude D            (18 AWG)
         ├── XT30 → RS-02 Épaule Yaw G       (18 AWG)
         ├── XT30 → RS-02 Épaule Yaw D       (18 AWG)
         ├── XT30 → RS-00 Poignet G          (18 AWG)
         ├── XT30 → RS-00 Poignet D          (18 AWG)
         ├── XT30 → RS-05 Cou Pan            (18 AWG)
         ├── XT30 → RS-05 Cou Tilt           (18 AWG)
         │
         │   [Alimentation logique]
         └── DC-DC 48V→5V (Jetson + Spresense)
```

#### Principe Sans Soudure

```
1. Le pigtail XT60 a déjà le connecteur soudé d'usine
2. L'autre bout est un fil nu (14 ou 18 AWG)
3. Vous dénudez 8mm du fil nu
4. Vous l'insérez dans la borne à vis du busbar
5. Vous serrez la vis → Contact fait → Zéro soudure

   [XT60 femelle] ══════════ fil 14AWG ══════════ [borne à vis busbar]
        ↑                                              ↑
   Se branche                                    Se visse
   sur le moteur                                  sur la barre cuivre
```

> [!TIP]
> **Avantage majeur du busbar** : modulaire. Ajouter ou retirer un moteur = 1 vis. Pas de PCB à ressouder, pas de nappe à refaire. Idéal pour un prototype en évolution constante.

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
