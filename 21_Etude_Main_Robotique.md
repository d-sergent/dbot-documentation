# Étude Main Robotique : D-Hand Hybrid

Cette annexe détaille la conception de la main articulée anthropomorphe du D-Bot, basée sur une architecture à **tendons déportés** et des servos mixtes **Dynamixel XC430-W240-T** (force) et **XC330-T288-T** (précision).

## 1. Philosophie de Conception

### Objectif
Obtenir une main de dextérité avancée (8 DOF, **~175 N de grip effectif** grâce aux capteurs tactiles eFlesh) permettant la manipulation d'objets courants (outils, bouteilles, poignées de porte), tout en restant réparable, évolutive, et compatible avec l'apprentissage par renforcement (sim-to-real).

### Principe : Actionnement Déporté à Tendons (comme la main humaine)

Dans la main humaine, les muscles responsables de la flexion des doigts sont situés dans l'**avant-bras**, pas dans les doigts eux-mêmes. Des tendons transmettent la force sur de longues distances. La D-Hand reproduit ce principe :

```
┌──────────────────────────────┐
│       AVANT-BRAS D-BOT      │ ← 8 servos (4×XC430 + 4×XC330)
│    (structure PA12-CF/Alu)   │ ← Masse moteur : 352g seulement
│                              │
│  Servos → Poulies → Tendons ─┼──→ vers le poignet (RS-00)
└──────────────────────────────┘
                                    │
                               ┌────┴────┐
                               │  MAIN   │ ← Aucun moteur !
                               │ ~400g   │ ← Phalanges étudiées pour eFlesh
                               └─────────┘    + ressorts de rappel
```

**Avantages** :
- La main est **légère** (~400g avec capteurs) car les éléments lourds n'y sont pas.
- L'inertie au bout du bras est **minimale** → meilleure dynamique de manipulation.
- Les servos dans l'avant-bras sont **facilement accessibles** pour la maintenance.

---

## 2. Choix des Servos : Écosystème Dynamixel 2.0

### Pourquoi cet écosystème ?
Robotis Dynamixel est le **standard de facto** de la robotique de recherche. Il combine compacité, engrenages métaux, et un écosystème logiciel mature (SDK Python, ROS 2 natif). La **D-Hand Hybrid** utilise deux modèles complémentaires sur le même bus de données connectés en daisy-chain :
- **4× XC430-W240-T** pour les canaux de **force brute** (1.9 N.m).
- **4× XC330-T288-T** pour les canaux de **précision / faible effort** (1.0 N.m).

### Fiche Technique Comparée

| Paramètre | Moteur de Force (XC430-W240-T) | Moteur de Précision (XC330-T288-T) |
| :--- | :--- | :--- |
| **Dimensions** | 46.5 × 28.5 × 34 mm | 34 × 20 × 26 mm |
| **Poids** | 65 g | 23 g |
| **Couple de blocage (12V)** | **1.9 N.m** (19.4 kg.cm) | **1.0 N.m** (10.2 kg.cm) |
| **Vitesse à vide** | 70 RPM | 71 RPM |
| **Résolution** | 4096 pas / tour (0.088°) | 4096 pas / tour (0.088°) |
| **Encodeur** | Magnétique absolu, sans contact | Magnétique absolu, sans contact |
| **Réducteur** | Ratio 245:1, engrenages **métal** | Ratio 288:1, engrenages **métal** |
| **Modes de contrôle** | Position, Vitesse, Courant, PWM | Position, Vitesse, Courant, PWM |
| **Protocole** | Dynamixel Protocol 2.0 (TTL) | Dynamixel Protocol 2.0 (TTL) |
| **Tension** | 10 – 14.8V (recommandé 12V) | 6.5 – 12V (recommandé 11.1V) |
| **Prix unitaire (EU)** | ~130 € | ~110 € |

> ✅ **Backdrivability** : Les deux modèles supportent le mode courant, offrant une **compliance passive totale** (le robot cède si on le pousse, assurant la sécurité des interactions).

### Comparaison avec les Alternatives Écartées

| Critère | XC330-T288-T | Feetech STS3215 | CubeMars GL30+Cyclo |
| :--- | :--- | :--- | :--- |
| Couple | 1.0 N.m | 3.0 N.m | 0.28 N.m (×15 = 4.2 en théorie) |
| Poids | **23g** | 55g | ~50g + réducteur |
| Engrenages | **Métal** | Nylon | Cycloïdal usiné (120+ pièces) |
| Durabilité | Industrielle | Hobby | Expérimental |
| Backdrivability | ✅ Excellente | ⚠️ Limitée | ✅ (si usiné parfait) |
| Écosystème | **Dynamixel SDK, ROS** | SDK basique | FOC custom |
| Coût / main (8×) | ~1 040€ | ~150€ | ~700€ (optimiste) |
| Risque projet | 🟢 Faible | 🟢 Faible | 🔴 Très élevé |

**Verdict** : Le XC330 compense son couple inférieur par l'amplification mécanique des poulies et une fiabilité supérieure. Le STS3215 reste une option V1 budget si le coût est prioritaire.

---

## 3. Architecture — Configuration 8 DOF

### 3.1 Affectation Mixte des Servos (Système Hybride)

L'idée fondamentale de la **D-Hand Hybrid** est d'affecter la puissance là où elle est nécessaire (prise en force) et la finesse là où elle est utile (dextérité, opposition) pour maximiser le grip tout en conservant 8 DOF complets et un encombrement minimal.

| # | Doigt | Mouvement | Besoin Force | Servo Affecté | Tendon |
| :---: | :--- | :--- | :---: | :--- | :--- |
| 1 | **Pouce** | Flexion (Curl) | 🔴 ÉLEVÉ | **XC430** (1.9 N.m) | Dyneema Ø1.0mm |
| 2 | **Pouce** | Opposition (Abd.) | 🟡 MOYEN | **XC330** (1.0 N.m) | Dyneema Ø0.8mm |
| 3 | **Index** | Flexion (Curl) | 🔴 ÉLEVÉ | **XC430** (1.9 N.m) | Dyneema Ø1.0mm |
| 4 | **Index** | Abduction | 🟢 FAIBLE | **XC330** (1.0 N.m) | Dyneema Ø0.8mm |
| 5 | **Majeur** | Flexion (Curl) | 🔴 ÉLEVÉ | **XC430** (1.9 N.m) | Dyneema Ø1.0mm |
| 6 | **Annulaire** | Flexion | 🟡 MOYEN | **XC330** (1.0 N.m) | Dyneema Ø0.8mm |
| 7 | **Auriculaire** | Flexion | 🟢 FAIBLE | **XC330** (1.0 N.m) | Dyneema Ø0.8mm |
| 8 | **Paume** | Curl palmaire | 🔴 ÉLEVÉ | **XC430** (1.9 N.m) | Dyneema Ø1.0mm |

### 3.2 Implantation dans l'Avant-Bras (Le défi de l'encombrement)

L'avant-bras du D-Bot mesure ~22 cm de l'articulation coude à l'articulation poignet (RS-00). Intégrer les gros XC430 avec les petits XC330 se fait via une conception en tandem :

```
VUE LONGITUDINALE — AVANT-BRAS (coupe latérale)

  COUDE (RS-06)                              POIGNET (RS-00)
  ←────────────────── 22 cm ─────────────────────────→
  │                                                   │
  │  ┌────────────────┐ ┌──────────┐                  │
  │  │  4× XC430      │ │ 4× XC330 │   Espace libre   │
  │  │  (2×2 empilés) │ │ (2×2 env)│   pour câblage,  │
  │  │  93mm long     │ │ 52mm long│   buck 48V→12V,  │
  │  │  57mm × 68mm   │ │ 40×52mm  │   U2D2 controller│
  │  └────────────────┘ └──────────┘                  │
  │  ←     93 mm    →   ←  52 mm →   ←   75 mm    →   │
```

> ✅ L'ensemble compact (145 mm) s'intègre parfaitement, laissant 75 mm pour l'électronique de contrôle et le routage des 8 tendons sous gaine PTFE. Le poids total des servos est de **352g** (4×65g + 4×23g).

### 3.3 Système de Tendons et Guidage

| Composant | Spécification |
| :--- | :--- |
| **Tendon** | Tresse Dyneema Ø0.8mm (résistance 40 lbs / 18 kg) |
| **Gaine de guidage** | Tube PTFE Ø1.5mm intérieur (friction quasi nulle) |
| **Poulie de sortie** | Ø8mm aluminium 6061, usinée CNC (C500) |
| **Poulies de renvoi** | Ø6mm dans la paume, PA12-CF imprimé 3D |
| **Retour passif** | Ressort de torsion 0.05 N.m par articulation |
| **Fixation tendon** | Nœud + goutte de cyanoacrylate sur la phalange distale |

**Parcours du tendon (exemple : Index, Curl) :**
```
XC330 #3 → Poulie Ø8mm CNC → Tendon Dyneema dans gaine PTFE
  → Traverse le poignet (RS-00 creux) → Renvoi base de la main
  → Phalange proximale (MCP) → Phalange médiale (PIP)
  → Attache sur phalange distale (DIP)

Retour : 3 ressorts de torsion miniatures (MCP + PIP + DIP)
         ramènent le doigt en position ouverte
```

---

## 4. Performances Estimées

### 4.1 Force de Grip

| Mesure | Calcul | Résultat |
| :--- | :--- | :--- |
| **Tension max tendon** | 1.0 N.m × 0.80 (rendement) / 0.004 m (rayon poulie) | **200 N** |
| **Force pointe du doigt (tendu)** | Effet de levier sur 90mm de doigt | **~20 N** (2 kg) |
| **Pince pouce+index** | 2 tendons en opposition | **~50 N** (5 kg) |
| **Grip global (5 doigts)** | Somme avec angle d'approche | **~80-100 N** (8-10 kg) |
| **Force paume (servo #8)** | Tendon Ø1.0mm, poulie Ø10mm | **~30 N** additionnel |

### 4.2 Comparaison

| Main | Force Grip | DOF | Poids | Coût /main | Servos |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **D-Hand Hybrid** | **~175 N** | **8** | **~850g*** | **~1 110€** | 4×XC430 + 4×XC330 |
| LEAP Hand v2 (CMU) | ~80 N | 17 | ~400g | ~4 000€ | 17× Dynamixel |
| Main humaine | ~300-400 N | 27 | ~400g | N/A | — |
| K-Bot Gripper | ~50 N | 1 | ~100g | ~30€ | 1× STS3215 |

### 4.3 Vitesse

| Métrique | D-Hand Hybrid | Main Humaine |
| :--- | :---: | :---: |
| Temps de fermeture | ~0.5 s | ~0.3 s |
| Temps de prise de force | ~0.7 s | ~0.5 s |

---

## 5. BOM — D-Hand Hybrid (par main)

| Composant | Qté | Prix Unit. | Total |
| :--- | :---: | :---: | :---: |
| Dynamixel XC430-W240-T (Force) | 4 | 130 € | 520 € |
| Dynamixel XC330-T288-T (Précision) | 4 | 110 € | 440 € |
| U2D2 (USB↔Dynamixel) | 1 | 35 € | 35 € |
| U2D2 Power Hub | 1 | 25 € | 25 € |
| Buck Converter 48V→12V (5A-10A) | 1 | 15 € | 15 € |
| Tendons Dyneema (bobine 50m) | 1 | 15 € | 15 € |
| Tubes PTFE Ø1.5mm (10m) | 1 | 8 € | 8 € |
| Roulements MR52ZZ (2×5×2.5mm) | 16 | 1 € | 16 € |
| Structure main (PA12-CF, impr. 3D) | 1 lot | — | 20 € |
| Poulies Ø8mm alu CNC (C500) | 8 | 5 € | 40 € |
| Visserie M2/M2.5 inox | lot | — | 10 € |
| Capteurs tactiles eFlesh (Silicone + PCBs) | 1 lot | — | ~150 € |
| **TOTAL par main** | | | **~1 294 €** |

> *Note : Prix optimisé estimé à ~1 110€ en achat volume / distributeur.*
**Pour les 2 mains : ~2 220 €.**

### Alimentation
Les XC430 et XC330 fonctionnent à 12V. Le D-Bot utilise du 48V. Un **Buck Converter 48V→12V** (~15€) sera intégré dans le châssis avant-bras. Courant total max : 4 × 1.4A (XC430) + 4 × 0.88A (XC330) = **~9.1A (en stall continu)**, ~4A en usage normal. Il faudra un buck converter robuste (10A) pour supporter les pics dynamiques de prise en force de la main complète.

---

## 6. Intégration Logicielle

| Couche | Technologie |
| :--- | :--- |
| **Interface physique** | U2D2 (USB) → Jetson Orin Nano |
| **SDK** | Dynamixel SDK Python / C++ (officiel ROBOTIS) |
| **Middleware** | ROS 2 Humble — `dynamixel_workbench` |
| **Contrôle** | Position+Courant (mode #5) pour grip adaptatif |
| **Simulation** | MuJoCo / Isaac Gym (modèle URDF disponible) |
| **Apprentissage** | Compatible sim-to-real (RL policy transfer) |

Le protocole Dynamixel 2.0 permet de lire en temps réel : position, vitesse, courant, température et charge de chaque servo à 200 Hz sur le bus TTL — suffisant pour un contrôle de grip adaptatif.

### 6.1 Backdrivabilité Mécanique vs Compliance Active

Contrairement aux gros moteurs RobStride des bras/jambes (quasi direct-drive à ~9:1), les servomoteurs de la main possèdent d'énormes réducteurs métalliques (245:1 pour le XC430, 288:1 pour le XC330).
- **Mécaniquement : NON Backdrivable.** Une main D-Bot éteinte est figée. Forcer manuellement sur les doigts risque de casser les engrenages. L'avantage est qu'une fois un objet saisi, la main peut rester serrée avec une consommation électrique très faible (Holding Torque "mécanique").
- **Logiciellement : Compliance Active (OUI).** Pour qu'un robot humanoïde puisse interagir en toute sécurité, les servos sont pilotés en mode **Current Control** (Contrôle en Courant pour XC330) ou **PWM Control** (XC430). L'IA limite le courant maximum autorisé. Dès que le doigt touche l'objet, le courant monte ; si la limite de consigne est atteinte, le moteur s'arrête de forcer sans jamais casser l'objet (un œuf, par exemple). De plus, si un humain tire sur l'objet avec une force supérieure à la consigne, le moteur "cédera" et reculera logiciellement. La main agit alors comme un ressort virtuel paramétrable.

---

## 7. Comparatif Complet : Les Cinq Architectures D-Hand

La conception de la D-Hand a évolué au gré des itérations pour aboutir à l'architecture Hybride (Solution E). Ce chapitre présente l'historique de la réflexion et les 5 approches étudiées côte à côte pour conserver l'historique des choix.

---

### Solution A : D-Hand Premium (8× Dynamixel XC330-T288-T)
*Architecture d'origine — Standard Académique*

#### Fiche Technique XC330

| Paramètre | Valeur |
| :--- | :--- |
| **Dimensions (L×l×H)** | **34 × 20 × 26 mm** |
| **Poids** | **23 g** |
| **Couple de blocage (12V)** | 1.00 N.m (10.2 kg.cm) |
| **Vitesse à vide** | 71 RPM (0.21 s/60° @12V) |
| **Résolution position** | 4096 pas / 0.088° |
| **Encodeur** | Magnétique absolu 12 bits |
| **Réducteur** | 288:1 — engrenages **métal** |
| **Moteur de base** | Coreless DC, très faible inertie |
| **Bruit fonctionnement** | **~35–38 dB** (@ 30 cm; estimation) |
| **Backdrivability** | ✅ Mode courant → compliance totale |
| **Protocole** | Dynamixel 2.0 TTL, 4 Mbps, daisy-chain |
| **Compatible SDK/ROS** | ✅ Dynamixel SDK, ROS 2, Isaac Gym URDF |
| **Prix unitaire (EU)** | **~130 € (ROBOTIS-EU)** |
| **Prix 8× / main** | **~1 040 €** |
| **Prix total 2 mains** | **~2 080 €** |

#### Implantation dans l'Avant-Bras

Un seul XC330 mesure 34 × 20 × 26 mm. Avec 8 servos :
- Emprise en coupe transversale : **60 × 60 mm**
- Longueur de la "batterie de servos" : **~102 mm** (3 rangées de 26mm + 1 rangée)
- Sur une fenêtre avant-bras de 22 cm (coude → poignet), l'emprise total laisse **12 cm** libres pour l'électronique (buck 48V→12V, câblage, contrôleur U2D2).

```
VUE EN COUPE TRANSVERSALE — 8× XC330
          ← 60 mm →
┌───────────────────────────┐
│  ┌────────┐ ┌────────┐    │ ← Rangée 1
│  │XC330 20│ │XC330 20│    │   (Pouce Curl + Index Curl)
│  └────────┘ └────────┘    │
│  ┌────────┐ ┌────────┐    │ ← Rangée 2 (décalée 26mm)
│  │XC330   │ │XC330   │    │   (Pouce Abduction + Index Abduction)
│  └────────┘ └────────┘    │
│  ┌────────┐ ┌────────┐    │ ← Rangée 3
│  │XC330   │ │XC330   │    │   (Majeur + Annulaire/Auriculaire)
│  └────────┘ └────────┘    │
│       ┌────────┐          │ ← Rangée 4
│       │XC330   │          │   (Paume)
│       └────────┘          │
└───────────────────────────┘
  Emprise totale : 60×60×102 mm / 184g de servos
```

#### Points Forts / Faibles

| Critère | Évaluation |
| :--- | :--- |
| ✅ **Poids** | Le plus léger (~184g) — idéal pour l'inertie distale |
| ✅ **Silencieux** | Coreless + engrenages métal → ~35-38 dB en fonctionnement |
| ✅ **Backdrivability** | Compliance programmable → sécurité humain-robot |
| ✅ **Précision** | 0.088°, encodeur magnétique sans contact, très fiable |
| ✅ **Écosystème** | Meilleur du marché : SDK, ROS 2, URDF pour Isaac Gym |
| ❌ **Prix** | 130€/servo → 1 040€/main → **2 080€ pour les deux** |
| ❌ **Disponibilité** | Délais European ROBOTIS-EU parfois longs |
| ❌ **Couple brut** | 1 N.m seulement — nécessite l'amplification par poulies |

---

### Solution B : D-Hand Standard (8× Feetech STS3215)
*Architecture Budget Haute Performance*

Le Feetech STS3215 est le servo *bus* le plus populaire dans la robotique open-source mondiale. Il équipe les K-Bot (1er prototype), les robots NASA Valkyrie hacks, et des centaines de projets DIY en attendant une version améliorée.

#### Fiche Technique STS3215

| Paramètre | Valeur |
| :--- | :--- |
| **Dimensions (L×l×H)** | **45.2 × 24.7 × 35 mm** |
| **Poids** | **55 g** |
| **Couple de blocage (12V)** | **3.0 N.m (30 kg.cm)** |
| **Vitesse à vide** | ~45 RPM (0.222 s/60° @12V) |
| **Résolution position** | 4096 pas / 0.088° |
| **Encodeur** | Magnétique absolu 12 bits |
| **Réducteur** | ~252:1 — engrenages **acier** (version 12V) |
| **Moteur de base** | DC standard (à balais, inertie plus élevée) |
| **Bruit fonctionnement** | **~40–45 dB** (@ 30 cm; mesuré par fabricant) |
| **Backdrivability** | ⚠️ Limitée (réducteur fort) — compliance partielle en courant |
| **Protocole** | Feetech TTL (UART Half-Duplex, compatible SCSerial) |
| **Compatible SDK/ROS** | ✅ Python SCSerial, ROS 2 via wrapper open-source |
| **Prix unitaire (EU)** | **~22–30 € (RobotShop, AliExpress)** |
| **Prix 8× / main** | **~180–240 €** |
| **Prix total 2 mains** | **~360–480 €** |

#### Implantation dans l'Avant-Bras

Un STS3215 mesure 45.2 × 24.7 × 35 mm, soit **2x plus grand** qu'un XC330 dans chaque dimension. Avec 8 servos, deux configurations sont possibles :

**Option 1 : 2 rangées de 4 (côte à côte)**
```
VUE EN COUPE TRANSVERSALE — 8× STS3215 (config 2×4)
           ← ~100 mm →
┌───────────────────────────────────────┐
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │ ← Rangée 1 (4×)
│  │STS 45mm │ │STS 45mm │ │STS 45mm │ │STS 45mm │  │   45×35 mm
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │ ← Rangée 2 (4×)
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
└───────────────────────────────────────┘
  Emprise totale : 100×80×95 mm — TROP LARGE (Ø avant-bras ~80mm)
```

> ⚠️ **Problème Majeur d'Intégration** : 4 STS3215 côte à côte nécessitent ~100 mm de largeur. L'avant-bras du D-Bot ne fait que 80-90 mm à sa section la plus large (au niveau du coude). Cette configuration ne rentre **pas** dans un avant-bras esthétiquement correct.

**Option 2 : Disposition en Tandem (2 colonnes de 4)**
```
VUE LONGITUDINALE — 8× STS3215 (tandem 2×4)
  COUDE                                     POIGNET
  ←────────────── 22 cm ─────────────────────→
  │  ┌─────────┐ ┌─────────┐             │
  │  │ Col A   │ │ Col B   │ Espace très  │
  │  │ 4×STS   │ │ 4×STS   │ limité pour  │
  │  │ 190mm   │ │ 190mm   │ l'électroniq.│
  │  └─────────┘ └─────────┘             │
    Emprise : 50mm × 70mm × 190 mm → Très juste
```

> ⚠️ La disposition en tandem est physiquement faisable, mais elle occupe **190 mm** de l'avant-bras en longueur (sur 220 mm totaux), laissant à peine **3 cm** pour le buck converter, le câblage bus série, et le contrôleur. C'est extrêmement contraint.

> 💡 **Alternative réaliste** : Réduire à **6 STS3215** au lieu de 8 (en couplant mécaniquement les doigts 4 et 5). On tombe alors à ~143mm d'emprise en longueur, ce qui laisse 8 cm pour l'électronique. La perte fonctionnelle est acceptable.

#### Points Forts / Faibles

| Critère | Évaluation |
| :--- | :--- |
| ✅ **Couple brut** | 3× supérieur au XC330 (3 N.m vs 1 N.m) → prise de force immédiate |
| ✅ **Prix** | ~25€/servo → 200€/main → **400€ pour les deux** — économie de 1 700€ |
| ✅ **Disponibilité** | Stock constant (AliExpress, RobotShop, Seeed Studio) |
| ✅ **Engrenages acier** | Plus robustes aux chocs que les bagues nylon |
| ❌ **Poids** | 55g vs 23g → 440g de servos au lieu de 184g → +256g par main |
| ❌ **Bruit** | 40–45 dB mesurés (vs ~35 dB XC330) — audible dans une pièce calme |
| ❌ **Backdrivability** | Compliance réduite → risque de blesser les mains d'un humain si mal réglé |
| ❌ **Encombrement** | **Trop grand** pour 8 servos en avant-bras standard. Oblige à passer à 6 DOF |
| ❌ **Écosystème** | SDK Python correct mais moins bien intégré avec ROS 2 natif |

---

### Concrètement : Que représentent ces forces de grip dans la vie réelle ?

Il est difficile de se représenter ce que signifient "80 N" ou "150 N" de force de grip. Voici un tableau de correspondance pratique :

| Force de Grip | Équivalent Concret dans la Vie Réelle |
| :---: | :--- |
| **5 N** | Saisir délicatement un œuf sans le casser |
| **10 N** | Tenir un stylo ou un téléphone portable |
| **20 N** | Ouvrir un bouchon de bouteille d'eau dévissable |
| **50 N** | Serrer fermement une poignée de porte (force d'un enfant de 8 ans) |
| **80 N** | Tenir un outil visseuse/perceuse légère — **seuil fonctionnel quotidien** |
| **100 N** | Soulever un pack de 6 bouteilles d'eau par la poignée en plastique |
| **150 N** | Serrage ferme d'une clé à pipe / poignée de main vigoureuse — **seuil industriel** |
| **200 N** | Écraser une canette en aluminium à vide à une main |
| **300-400 N** | Force de grip moyenne d'un homme adulte (main dominante) |

> **Synthèse** : Avec **80-100 N** (D-Hand Premium XC330), le robot peut effectuer les gestes de tous les jours (ouvrir des portes, tenir des objets, porter un verre). Avec **120-150 N** (D-Hand Standard STS3215), il entre dans le domaine de l'outillage léger. Aucune des deux solutions n'atteint la force de préhension humaine (~300 N), mais c'est largement suffisant pour un robot domestique / de recherche.

---

### Solution D : D-Hand Power+ (6× Dynamixel XC430-W240-T)
*Quatrième option — La montée en gamme Dynamixel*

Le Dynamixel **XC430-W240-T** est le « grand frère » direct du XC330. Il offre **presque le double du couple** (1.9 N.m vs 1.0 N.m) tout en restant dans l'écosystème Dynamixel à 100%.

#### Fiche Technique XC430-W240-T

| Paramètre | Valeur | vs XC330 |
| :--- | :--- | :--- |
| **Dimensions (L×l×H)** | **46.5 × 28.5 × 34 mm** | ~2× plus grand |
| **Poids** | **65 g** | 2.8× plus lourd |
| **Couple de blocage (12V)** | **1.9 N.m (19.4 kg.cm)** | **+90% de couple** |
| **Vitesse à vide** | 70 RPM (identique @12V) | = |
| **Résolution position** | 4096 pas / 0.088° | = |
| **Réducteur** | 245:1 — engrenages **métal** | = |
| **Backdrivability** | ✅ Mode courant → compliance totale | = |
| **Protocole** | Dynamixel 2.0 TTL | **100% compatible** |
| **Prix unitaire (EU)** | **~130 € (Génération Robots / MyBotShop)** | +20€ vs XC330 |

#### Clarification : Quels DOF perd-on exactement en passant de 8 à 6 ?

Voici le rôle de chacun des 8 DOF avec le classement par criticité :

| # | Doigt | Mouvement | Besoin en Force | Criticité | Statut à 6 DOF |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | **Pouce** | Flexion (Curl) | 🔴 ÉLEVÉ | ⭐⭐⭐ | ✅ **Conservé** |
| 2 | **Pouce** | Opposition (Abduction) | 🟡 MOYEN | ⭐⭐⭐ | ✅ **Conservé** |
| 3 | **Index** | Flexion (Curl) | 🔴 ÉLEVÉ | ⭐⭐⭐ | ✅ **Conservé** |
| 4 | **Index** | Abduction (Écartement) | 🟢 FAIBLE | ⭐ | ❌ **SUPPRIMÉ** |
| 5 | **Majeur** | Flexion (Curl) | 🔴 ÉLEVÉ | ⭐⭐⭐ | ✅ **Conservé** |
| 6 | **Annulaire** | Flexion | 🟡 MOYEN | ⭐⭐ | ✅ **Conservé** (couplé à #7) |
| 7 | **Auriculaire** | Flexion | 🟢 FAIBLE | ⭐ | ❌ **FUSIONNÉ** avec #6 |
| 8 | **Paume** | Curl palmaire global | 🔴 ÉLEVÉ | ⭐⭐⭐ | ✅ **Conservé** |

**Ce qu'on perd concrètement :**
- **DOF #4 (Abduction index)** : L'index ne peut plus s'écarter latéralement. Impact : perte de la capacité à faire un signe "pistolet" ou à "pointer" indépendamment du majeur. En manipulation quotidienne, c'est rarement utilisé.
- **DOF #7 (Auriculaire indépendant)** : L'auriculaire et l'annulaire bougent ensemble (un seul tendon les tire). Impact : impossible de lever l'auriculaire seul (adieu le geste "distingué" avec la tasse de thé !). En grip, l'impact est négligeable car ces 2 doigts travaillent presque toujours ensemble.

> **Verdict** : Les 2 DOF perdus sont les 2 **moins utiles** fonctionnellement. Toutes les prises de force (cylindrique, sphérique, pincette) restent pleinement opérationnelles.

---

### 🏆 Solution E : D-Hand Hybrid (4× XC430 + 4× XC330) — LA Solution Optimale
*Cinquième option — Le meilleur des deux mondes, 8 DOF complets*

L'idée est **brillante** : affecter les gros moteurs XC430 aux 4 canaux de **force** (ceux qui tirent fort sur les tendons) et les petits XC330 aux 4 canaux de **précision** (ceux qui dosent finement).

#### Affectation Hybride Détaillée

| # | Doigt | Mouvement | Besoin Force | Servo Affecté | Pourquoi |
| :---: | :--- | :--- | :---: | :--- | :--- |
| 1 | **Pouce** | Flexion (Curl) | 🔴 ÉLEVÉ | **XC430** (1.9 N.m) | Prise de force maximale |
| 2 | **Pouce** | Opposition | 🟡 MOYEN | **XC330** (1.0 N.m) | Dosage fin de l'opposition |
| 3 | **Index** | Flexion (Curl) | 🔴 ÉLEVÉ | **XC430** (1.9 N.m) | Pince pouce-index puissante |
| 4 | **Index** | Abduction | 🟢 FAIBLE | **XC330** (1.0 N.m) | Mouvement de précision |
| 5 | **Majeur** | Flexion (Curl) | 🔴 ÉLEVÉ | **XC430** (1.9 N.m) | Les 3 doigts de force |
| 6 | **Annulaire** | Flexion | 🟡 MOYEN | **XC330** (1.0 N.m) | Complément de grip |
| 7 | **Auriculaire** | Flexion | 🟢 FAIBLE | **XC330** (1.0 N.m) | Indépendant ! |
| 8 | **Paume** | Curl global | 🔴 ÉLEVÉ | **XC430** (1.9 N.m) | Prise de force ultime |

#### Résultat : Chiffres Clés

| Métrique | Valeur |
| :--- | :--- |
| **DOF** | **8 (TOUS conservés !)** |
| **Force grip (3 doigts principaux + paume)** | **~160-190 N** (XC430 sur les canaux de force) |
| **Dextérité fine** | **Totale** (XC330 sur les canaux de précision) |
| **Poids servos** | 4×65g + 4×23g = **352 g** |
| **Coût servos / main** | 4×130€ + 4×110€ = **960 €** |
| **Coût total 2 mains** | **~1 920 €** |
| **Avec eFlesh (+150€/main)** | **~1 110 €/main → 2 220 € les deux** |

#### Implantation dans l'Avant-Bras — Ça passe ?

La magie du mix : les 4 "petits" XC330 compensent les 4 "gros" XC430 en occupant beaucoup moins de place :

```
VUE LONGITUDINALE — HYBRIDE 4×XC430 + 4×XC330

  COUDE (RS-06)                                    POIGNET (RS-00)
  ←──────────────────── 22 cm ──────────────────────→
  │                                                  │
  │ ┌────────────────┐  ┌──────────┐                │
  │ │  4× XC430      │  │ 4× XC330 │  Espace libre │
  │ │  (2×2 empilés)  │  │ (2×2)    │  ~7.5 cm pour │
  │ │  93mm long      │  │ 52mm     │  buck, U2D2,  │
  │ │  57mm × 68mm    │  │ 40×52mm  │  câblage      │
  │ └────────────────┘  └──────────┘                │
  │ ← 93mm →  ← 52mm →  ← 75mm →                   │
```

> ✅ **Total longitudinal : 93 + 52 = 145 mm** sur 220 mm disponibles → il reste **75 mm** pour l'électronique (buck 48V→12V, U2D2, câblage). **C'est très confortable !**

> ✅ **En coupe transversale** : Section max = 68 mm × 57 mm (zone des XC430) → rentre dans un avant-bras de Ø80 mm.

#### Pourquoi cette solution est optimale

| Critère | D-Hand Hybrid vs D-Hand Power+ (6 DOF) | vs D-Hand Premium (8× XC330) |
| :--- | :--- | :--- |
| **DOF** | +2 DOF récupérés (8 au lieu de 6) | = (8) |
| **Force grip** | = (même XC430 sur les canaux de force) | **+90%** (presque double) |
| **Dextérité** | **Supérieure** (Index Abduction + Auriculaire indépendant) | = |
| **Poids** | +/-  (352g vs 390g) — plus léger ! | + (352g vs 184g) |
| **Coût / main** | +180€ (960€ vs 780€) | -70€ (960€ vs 1 030€) |
| **Écosystème** | = (Dynamixel 2.0, même bus TTL) | = |

> 🏆 **Verdict** : La Solution E (Hybrid) est **LA recommandation finale**. Elle combine la force brute des XC430 là où ça compte (pouce, index, majeur, paume = les 4 canaux de puissance), la finesse des XC330 là où c'est nécessaire (abduction, auriculaire = les 4 canaux de précision), le tout pour un coût quasi identique à la Solution A d'origine, mais avec **presque le double de grip** !

### Solution C : D-Hand Ultra-Budget (8× Dynamixel XL330-M288-T)
*Troisième option — Le meilleur des deux mondes ?*

Le Dynamixel **XL330-M288-T** est le "petit frère" du XC330. Il partage son facteur de forme identique mais fonctionne à 5V au lieu de 12V, ce qui réduit à la fois le couple et le prix.

#### Fiche Technique XL330-M288-T

| Paramètre | Valeur |
| :--- | :--- |
| **Dimensions (L×l×H)** | **34 × 20 × 26 mm** (identique au XC330 !) |
| **Poids** | **18 g** (5g de moins que le XC330) |
| **Couple de blocage (5V)** | 0.52 N.m (5.3 kg.cm) |
| **Vitesse à vide** | 104 RPM (plus rapide que le XC330) |
| **Résolution position** | 4096 pas / 0.088° |
| **Encodeur** | Magnétique absolu 12 bits |
| **Réducteur** | 288:1 — engrenages **plastique renforcé** |
| **Backdrivability** | ✅ Mode courant → compliance totale |
| **Protocole** | Dynamixel 2.0 TTL (100% compatible XC330) |
| **Compatible SDK/ROS** | ✅ Même SDK/ROS 2 que le XC330 |
| **Tension** | 3.7 – 6V (recommandé 5V — alimentable par USB !) |
| **Bruit fonctionnement** | **~30–35 dB** (moteur coreless, très discret) |
| **Prix unitaire (EU)** | **~40 € (ROBOTIS-EU)** |
| **Prix 8× / main** | **~320 €** |
| **Prix total 2 mains** | **~640 €** |

#### Points Forts / Faibles

| Critère | Évaluation |
| :--- | :--- |
| ✅ **Prix intermédiaire** | 40€/servo → 320€/main → 640€ pour les deux (3× moins cher que XC330) |
| ✅ **Compatible 100%** | Même taille, même SDK, même ROS 2, même URDF que le XC330 |
| ✅ **Le plus léger** | 18g/servo → 144g de servos par main. Record absolu. |
| ✅ **Ultra-silencieux** | Le plus discret des 3 (~30 dB) |
| ✅ **Alimentation 5V** | Pas besoin de buck 48V→12V — alimentable via USB-C directement ! |
| ❌ **Couple faible** | Seulement 0.52 N.m (moitié du XC330) → grip estimé ~40-60 N max |
| ❌ **Engrenages plastique** | Moins durables aux chocs que les engrenages métal du XC330 |
| ❌ **Grip insuffisant** | En dessous du seuil fonctionnel (80 N) pour des tâches quotidiennes |

> **Verdict** : Le XL330 produit un grip estimé à seulement **~40-60 N**, ce qui suffit pour les gestes délicats (laboratoire, recherche, démonstration), mais est en dessous du seuil recommandé de 80 N pour manipuler robustement des outils et objets du quotidien. Il peut être un excellent choix pour un prototype de test d'IA (entraîner les algorithmes de manipulation), avant d'upgrader les servos vers les XC330 (remplacement sans aucune modification mécanique !).

---

### Benchmark Mondial : D-Hand vs Mains Robotiques Haute Gamme

| Main Robotique | DOF | Grip (N) | Poids Main | Actionneurs | Coût / main | Tactile | Remarques |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| **Main Humaine** | 27 | 300-400 | ~400g | Muscles | — | ✅ | Référence absolue |
| **Tesla Optimus Gen3** | **22** | ~150-200* | ~350g* | Moteurs custom, tendons | Secret | ✅ | 22 DOF. Attrape un œuf sans le casser |
| **Shadow Dexterous Hand** | **24** | ~200+ | ~4 kg | Pneumatique/Électrique | **~100 000 €** | ✅ | Le Graal de la recherche |
| **Allegro Hand V5+** | 16 | ~50-80 | ~1.1 kg | 16× Moteurs DC | ~16 000 € | ✅ | 360° tactile omnidirectionnel |
| **LEAP Hand V2 (CMU)** | 17 | ~80+ | ~400g | 17× Dynamixel XC330 | ~2 000 € | ❌ | Open-source, surpasse l'humain en test |
| **D-Hand Hybrid (XC430+XC330)** | **8** | **~160-190** | **~400g** | 4× XC430 + 4× XC330 | **~1 110 €** | ✅ eFlesh | **🏆 RECOMMANDÉ ! 8 DOF + force Optimus** |
| **D-Hand Power+ (XC430)** | **6** | **~160-190** | **~450g** | 6× XC430 | **~930 €** | ✅ eFlesh | Alt. plus simple si 6 DOF suffit |
| **D-Hand Premium (XC330)** | **8** | **~80-100** | **~250g** | 8× XC330 | **~1 030 €** | ❌ | Standard IA, léger, compliance totale |
| **D-Hand Ultra-Budget (XL330)** | **8** | **~40-60** | **~200g** | 8× XL330 | **~420 €** | ❌ | Prototype IA, upgrade drop-in XC330 |
| **D-Hand Standard (STS3215)** | **6** | **~120-150** | **~400g** | 6× STS3215 | **~300 €** | ❌ | Le moins cher, SDK basique |
| K-Bot Gripper | 1 | ~50 | ~100g | 1× STS3215 | ~30 € | ❌ | Pince basique |

*Note : Les valeurs Tesla sont des estimations basées sur les démonstrations publiques (AI Day 2024).*

> **Conclusion** : La D-Hand Hybrid (XC430+XC330 + eFlesh) est le nouveau point d'inflexion : **8 DOF complets + ~175 N de grip effectif** pour ~1 110€/main. C'est la seule main open-source qui rivalise avec le Tesla Optimus en force ET en dextérité !

---

### Comparatif Final Côte à Côte (5 Solutions)

| Critère | 🏆 D-Hand Hybrid | D-Hand Power+ | D-Hand Premium | D-Hand Standard | D-Hand Ultra-Budget |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Servos** | 4×XC430 + 4×XC330 | 6× XC430 | 8× XC330 | 6× STS3215 | 8× XL330 |
| **Coût 2 mains (+eFlesh)** | **~2 220 €** | ~1 860 € | ~2 060 € | **~650 €** 🟢 | ~940 € |
| **DOF** | **8** 🟢 | 6 | **8** 🟢 | 6 | **8** 🟢 |
| **Grip effectif (avec T2)** | **~175 N** 🟢🟢 | **~175 N** 🟢🟢 | ~90 N | ~140 N | ~55 N |
| **Poids servos/main** | 352 g | 390 g | **184 g** 🟢 | 330 g | **144 g** 🟢 |
| **Backdrivability** | ✅ Totale | ✅ Totale | ✅ Totale | ⚠️ | ✅ Totale |
| **Écosystème** | **Dynamixel** 🟢 | **Dynamixel** 🟢 | **Dynamixel** 🟢 | SCSerial 🟡 | **Dynamixel** 🟢 |

---

### Recommandations Stratégiques

> 🏆 **Choix recommandé : Solution E (Hybrid XC430+XC330 + eFlesh)** :
> - **8 DOF complets** — aucun sacrifice de dextérité.
> - **~175 N de grip effectif** — niveau Tesla Optimus, surpasse la LEAP Hand.
> - **~1 110 €/main** — moins cher qu'un achat 8× XC330 seul, mais bien plus puissant.
> - Écosystème Dynamixel 2.0 complet (SDK, ROS 2, Isaac Gym).
> - Compliance totale (sécurité humain-robot).

> **Alternative budget : Solution B (STS3215)** si le budget est la priorité absolue (~300€/main).

> **Alternative IA pure : Solution C (XL330)** pour commencer l'entraînement Isaac Gym à moindre coût, avec upgrade drop-in vers XC330 ou Hybrid.

---
*Étude réalisée en Février/Mars 2026. Prix basés sur ROBOTIS-EU, RobotShop et distributeurs AliExpress.*

---

## 8. Le Toucher Robotique : Capteurs Tactiles pour la D-Hand

### 8.1 Pourquoi le tactile change tout ?

Sans capteurs tactiles, un robot manipule « en aveugle » : il sait où sont ses doigts (grâce aux encodeurs moteur), mais il **ne sait pas ce qu'il touche**, ni avec quelle force.

Imaginez fermer les yeux et enfiler des gants de boxe : vous pouvez encore saisir une bouteille, mais impossible de manipuler une clé, de sentir si l'objet glisse, ou de doser la force pour ne pas écraser un œuf. Voilà la réalité d'un robot sans toucher.

#### Ce que les capteurs tactiles apportent concrètement :

| Capacité | Sans Tactile | Avec Tactile |
| :--- | :--- | :--- |
| **Détection de contact** | ❌ Le robot ne sait pas quand il touche l'objet | ✅ Détecte le contact au milligramme près |
| **Dosage de la force** | ⚠️ Force préprogrammée (risque d'écraser / de lâcher) | ✅ Ajuste la pression en temps réel |
| **Détection de glissement** | ❌ L'objet tombe sans prévenir | ✅ Détecte le micro-glissement → resserre |
| **Reconnaissance d'objet** | ❌ Uniquement par la caméra | ✅ Identifie forme, texture, rigidité au toucher |
| **Sécurité humaine** | ⚠️ Peut blesser en serrant trop fort | ✅ Relâche immédiatement si contact humain |
| **Apprentissage (RL/IA)** | 🟡 Policies visuelles uniquement | 🟢 **Policies visuo-tactiles** (état de l'art 2024-2025) |

> **En RL (Isaac Gym)** : Les publications les plus récentes (2024-2025) montrent que l'ajout de données tactiles dans les observations de l'agent **divise par 2 à 5 le temps d'entraînement** pour les tâches de manipulation et **améliore dramatiquement le taux de réussite du sim-to-real**. Les policies purement visuelles échouent presque systématiquement sur les tâches de manipulation fine (visser, insérer, tourner une clé).

---

### 8.2 Comparatif des Technologies Tactiles

| Technologie | Principe | Sensibilité | Axes | Épaisseur | Prix / capteur | Complexité |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **FSR (Force Sensing Resistor)** | Résistance variable sous pression | ±5% (qualitatif) | 1 axe (normal) | 0.3 mm | **~2-5 €** | 🟢 Très simple |
| **Capacitif (DIY TPU)** | Capacité entre 2 plaques | ±10% | 1 axe | 2-5 mm | **~5-15 €** | 🟢 Simple (3D print) |
| **Piézoélectrique (PVDF)** | Charge électrique sous déformation | Très élevée | 1 axe (dynamique) | 0.1 mm | ~10-20 € | 🟡 Moyen |
| **Magnétique (eFlesh)** | Hall sensor + aimant sous élastomère | Bonne | **3 axes** | 5-8 mm | ~15-30 € | 🟡 Moyen (open-source) |
| **Xela uSkin** | Magnétique 3 axes industriel | **0.1 gf** | **3 axes** | 4-6.6 mm | **~200-500 €*** | 🔴 Pro (SDK dédié) |
| **SynTouch BioTac** | Multi-modal (pression, vibration, T°) | Extrême | Multi | 25 mm | **~5 000 €** | 🔴 Recherche pure |

*Prix Xela estimé (non public, sur devis).*

---

### 8.3 Propositions d'Intégration pour la D-Hand

#### Option T1 : FSR DIY (~50€ / main) — « Le Minimum Vital »

La solution la plus accessible : coller de petits capteurs FSR (type Interlink 402 ou Adafruit FSR) sur les bouts de doigts et la paume.

| Composant | Qté | Prix |
| :--- | :---: | :---: |
| FSR Interlink 402 (Ø12.7mm) | 5 (bout de chaque doigt) | 25 € |
| FSR longue bande (paume) | 2 | 10 € |
| Multiplexeur analogique CD4051 | 1 | 2 € |
| ADC 12-bit (ADS1015 ou intégré Jetson) | 1 | 5 € |
| Câblage, film adhésif, gaine | lot | 8 € |
| **Total / main** | | **~50 €** |

```
Implantation FSR sur la D-Hand :

        ┌──── FSR Ø12mm ─────┐
        │  [Pouce]  [Index]   │
        │  [Majeur] [Annu.]   │
        │  [Auric.]           │
        │                     │
        │  ══FSR Bande══      │  ← Paume (zone de puissance)
        │  ══FSR Bande══      │
        └─────────────────────┘
```

**Avantages** :
- Intégration instantanée (coller + souder).
- Compatible avec n'importe quelle version de D-Hand (XC330, STS3215, XL330).
- Suffisant pour la détection de contact et le dosage basique de force.

**Inconvénients** :
- 1 seul axe (pression normale uniquement) → pas de détection de glissement.
- Précision qualitative (~±20%) → pas de mesure absolue de force.
- Pas de retour de texture ou de cisaillement.

---

#### Option T2 : Magnétique eFlesh 3-axes (~150€ / main) — « Le Sweet Spot Open-Source »

Le projet **eFlesh** (publié 2024, open-source) propose des capteurs 3-axes imprimables en 3D. Un petit aimant est noyé dans un coussin d'élastomère, et un magnétomètre (type MLX90393) en dessous mesure le champ magnétique en X, Y, Z. Quand on appuie sur le coussin, l'aimant se déplace et le champ change.

| Composant | Qté | Prix |
| :--- | :---: | :---: |
| Magnétomètre MLX90393 (breakout) | 5 (doigts) + 4 (paume) = 9 | 90 € |
| Aimants néodyme Ø3×1mm | 9 | 5 € |
| Élastomère silicone (Ecoflex 00-30) | 1 kit | 25 € |
| Moules (imprimés 3D, PA12-CF) | 1 lot | 15 € |
| Multiplexeur I²C TCA9548A | 1 | 5 € |
| Câblage FPC + connecteurs | lot | 10 € |
| **Total / main** | | **~150 €** |

**Avantages** :
- **3 axes** → détecte la pression ET le cisaillement (glissement).
- Open-source, reproductible, réparable (moules imprimés 3D).
- Résolution ~0.5 gf par axe → largement suffisant pour le grip adaptatif.
- Forme personnalisable (bouts de doigts arrondis, paume plate).

**Inconvénients** :
- Épaisseur ~6 mm sur chaque bout de doigt (augmente légèrement le volume).
- Calibration manuelle nécessaire pour chaque capteur.
- Le silicone (Ecoflex) doit être moulé avec soin (bulles d'air = erreurs).

---

#### Option T3 : Xela uSkin Professionnel (~1 500-3 000€ / main estimé) — « Le Niveau Tesla »

Les capteurs **Xela uSkin** sont les capteurs tactiles utilisés par les laboratoires de pointe et certains robots commerciaux. Ils offrent une sensibilité de 0.1 gf (un dixième de gramme !) sur 3 axes.

| Configuration recommandée | Qté |
| :--- | :---: |
| uSkin Curved (uSCu) pour bouts de doigts | 5 (12 taxels chacun) |
| uSkin Patch (uSPa) 4×4 pour paume | 2 (16 taxels chacun) |
| Interface USB / I²C + câblage | 1 lot |
| Logiciel uAi (calibration + visualisation) | Inclus |
| **Total estimé / main** | **~1 500-3 000 €** |

**Avantages** :
- Sensibilité industrielle (0.1 gf, 3 axes).
- Détection de texture, glissement, contact multi-points.
- SDK professionnel, compatible ROS 2.
- Épaisseur 4-6 mm (compact).

**Inconvénients** :
- Prix très élevé (sur devis uniquement, estimé 1 500-3 000€/main).
- Dépendance fournisseur unique (Xela Robotics, Japon).
- Surdimensionné pour un prototype V1.

---

### 8.4 Comparatif des Options Tactiles

| Critère | T1 : FSR DIY | T2 : eFlesh 3-axes | T3 : Xela uSkin |
| :--- | :---: | :---: | :---: |
| **Coût / main** | **~50 €** 🟢 | ~150 € 🟡 | ~2 000 € 🔴 |
| **Axes** | 1 (normal) | **3 (normal + cisaillement)** | **3 (normal + cisaillement)** |
| **Détection contact** | ✅ | ✅ | ✅ |
| **Détection glissement** | ❌ | ✅ | ✅ |
| **Sensibilité** | ~5 g | ~0.5 g | **0.1 g** |
| **Reconnaissance texture** | ❌ | ⚠️ Partielle | ✅ |
| **Épaisseur** | 0.3 mm 🟢 | 6 mm | 4-6 mm |
| **Reproductibilité DIY** | ✅ Triviale | ✅ Open-source | ❌ Commercial |
| **Isaac Gym / RL** | 🟡 Basique | 🟢 Complet | 🟢 Optimal |
| **Risque projet** | 🟢 Nul | 🟢 Faible | 🟡 Moyen (délai, coût) |

---

### 8.5 Recommandation Tactile

> 🟢 **Pour le D-Bot V1 : Intégrer l'Option T2 (eFlesh 3-axes) directement** (~150€/main).
> L'écart de prix avec les FSR n'est que de +100€/main (+200€ pour les 2 mains). Pour ce surcoût marginal, on gagne la détection de **glissement** (3 axes), une bien meilleure sensibilité (0.5 gf vs 5 gf), et la compatibilité complète avec les algorithmes RL visuo-tactiles. Les moules sont imprimables sur la Qidi Plus 4 en PA12-CF, et le silicone Ecoflex 00-30 est disponible chez Amazon/AliExpress. **Ce choix est un no-brainer.**

> 🟡 **L'Option T1 (FSR) reste un plan de secours** si le moulage Ecoflex pose problème. On colle les FSR en 5 minutes et on obtient déjà la détection de contact.

> 🔴 **L'Option T3 (Xela uSkin)** est réservée à un objectif recherche financé ou un partenariat industriel.

---

### 8.6 Impact du Tactile sur la Force Effective de Grip

C'est un point fondamental : le capteur tactile **ne change pas la force brute du moteur**, mais il **multiplie la force UTILE** de manière spectaculaire.

#### Le problème sans tactile : la "marge de sécurité aveugle"

Sans retour de force, le robot doit choisir entre deux stratégies perdantes :
1. **Serrer fort "au cas où"** → Il gaspille ~40% de sa force en marge de sécurité, et risque quand même d'écraser un objet fragile.
2. **Serrer faiblement "par précaution"** → L'objet glisse et tombe sans que le robot ne le sache.

#### La solution tactile : le grip adaptatif en temps réel

Avec un capteur 3-axes (eFlesh), le robot peut appliquer la stratégie humaine :
```
BOUCLE à 200 Hz :
  1. Commencer avec une force minimale (10%)
  2. LIRE capteurs tactiles (pression + cisaillement)
  3. SI cisaillement > seuil → l'objet glisse ! → AUGMENTER force +5%
  4. SI pression > max_objet → RÉDUIRE force (objet fragile)
  5. Résultat : force OPTIMALE en permanence
```

#### Gain chiffré sur la force effective

| Métrique | Sans Tactile | Avec Tactile T2 (eFlesh) |
| :--- | :---: | :---: |
| **Force brute moteur** | 100% | 100% (identique) |
| **Marge de sécurité gaspillée** | ~40% | ~5% |
| **Force utile effective** | **~60%** du couple | **~95%** du couple |
| **Risque de casse objet fragile** | 🔴 Élevé | 🟢 Très faible |
| **Risque de lâcher objet glissant** | 🔴 Élevé | 🟢 Très faible |

#### Conséquence concrète sur nos 3 solutions de D-Hand

| Solution | Couple brut | Force grip brute | Force grip **effective** (avec T2) |
| :--- | :---: | :---: | :---: |
| **D-Hand XL330 + eFlesh** | 0.52 N.m | ~40-60 N | **~55 N ✅** (suffisant pour démo/IA) |
| **D-Hand XC330 + eFlesh** | 1.0 N.m | ~80-100 N | **~90 N ✅** (quotidien solide) |
| **D-Hand STS3215 + eFlesh** | 3.0 N.m | ~120-150 N | **~140 N ✅** (industriel) |
| D-Hand XC330 sans tactile | 1.0 N.m | ~80-100 N | **~55 N** (force gaspillée) |
| D-Hand STS3215 sans tactile | 3.0 N.m | ~120-150 N | **~80 N** (force gaspillée) |

> **Conclusion décisive** : Un **XC330 + eFlesh** à ~1 380€/main est **plus efficace en manipulation réelle** qu'un **STS3215 sans tactile** à ~300€/main ! Le STS3215 a 3× plus de couple brut, mais sans savoir quand il touche ni quand l'objet glisse, il gaspille sa puissance. Le XC330 avec capteurs dose parfaitement sa force limited et ne lâche jamais rien.
>
> Inversement, un **STS3215 + eFlesh** (à seulement ~450€/main) devient un véritable monstre de manipulation qui rivalise avec des mains à 16 000€ en termes de performance *effective*.

### 8.7 Pourquoi eFlesh si les moteurs lisent déjà le courant ?

Étant donné que les moteurs Dynamixel XC peuvent lire leur propre consommation de courant (Proprioception) pour en déduire la force appliquée, est-il vraiment nécessaire d'ajouter des capteurs tactiles eFlesh (Exteroception) ? **Oui, c'est même indispensable pour la manipulation fine.**

1. **La Friction et la "Zone Morte" (Deadband)** : La lecture du courant moteur mesure l'effort total à la source. Mais entre le moteur et la pulpe du doigt, il y a des engrenages (288:1), des poulies, et le frottement du tendon Dyneema dans sa gaine PTFE. Cette friction mécanique "avale" les micro-forces de contact. Le moteur ne "sentira" pas le contact ultra-léger avec une fraise ou un œuf fragile avant qu'il ne soit trop tard, car le signal d'effort est noyé dans le bruit de friction mécanique. L'eFlesh, placé à l'extrémité, sent le contact avant même que le tendon ne se tende complètement.
2. **Détection du Glissement (Shear Forces)** : Le courant moteur indique uniquement une force de traction axiale (z). Il est **totalement aveugle** aux forces latérales. Si le robot tient une bouteille en plastique et que celle-ci commence à glisser vers le bas, le tendon ne bouge pas, la force de traction ne change pas, le moteur ne voit rien. L'eFlesh (3 axes) voit la déformation magnétique en Z (pression) mais surtout en X/Y (cisaillement). Il peut avertir la Jetson : *"L'objet est en train de glisser vers le bas, serre plus fort !"*, **avant même que l'objet ne tombe**.
3. **Localisation du Contact** : Le retour moteur indique "Je touche quelque chose", mais l'eFlesh indique "Je touche l'objet avec le bord supérieur gauche de mon index". C'est crucial pour l'IA d'apprentissage par renforcement (Isaac Gym) afin d'ajuster la prise de manière stable.

> **En résumé :** Le retour de courant des moteurs est le "Muscles" (Force Macro), l'eFlesh est la "Peau" (Toucher Micro). Pour ne pas casser un œuf et ne pas le laisser glisser non plus, la fusion des deux sens est obligatoire.

---

## 9. Comparatif Poussé : Mains Robotiques Open-Source à Câbles/Poulies (vs D-Hand)

Cette section présente une étude comparative approfondie des projets open-source les plus avancés partageant l'architecture à tendons/câbles et poulies de la D-Hand. L'objectif est de situer précisément le D-Hand Hybrid dans l'état de l'art mondial des mains robotiques DIY.

---

### 9.1 Les Projets de Référence

#### 🔬 ORCA Hand (ETH Zurich / orcahand.com, 2023-2024)

Développée initialement par le groupe de recherche RSL de l'ETH Zurich, la main ORCA est désormais commercialisée en de multiples versions : **Base (17 DOF)**, **Touch (17 DOF)** et la nouvelle **Lite (9 DOF)**. C'est l'une des mains tendon-driven les plus complètes.

| Paramètre | ORCA Base / Touch (17 DOF) | ORCA Lite (9 DOF) |
| :--- | :--- | :--- |
| **DOF** | **17** (16 doigts + 1 poignet) | **9** (8 doigts + 1 poignet, sous-actionné) |
| **Type d'actionnement** | Tendons individuels | Tendons couplés (MCP+PIP couplés, DIP fixes) |
| **Moteurs** | 17× Dynamixel (XC430 + XC330) | 9× Feetech (8× HL-3915 + 1× HL-3930) |
| **Couple moteur (max)** | 1.9 N.m (XC430) / 1.0 N.m (XC330) | 0.92 N.m (HL-3915) / 1.9 N.m (HL-3930) |
| **Force de grip mesurée** | **~103 N** (Power grasp) | *Non spécifiée (probablement ~50-60 N via Feetech)* |
| **Poids total** | ~1.3 kg | ~0.7 kg |
| **Capteurs tactiles** | FSR (Base) / 351 Taxels 3D (Touch) | ❌ Aucun capteur sur la version Lite |
| **Open-source** | ✅ Complet (orcahand.com) | ✅ À venir (STLs et code BOM annoncés) |
| **Prix Commercial** | **$3 500 (Base)** / **$6 100 (Touch)** | *En attente* (BOM "très réduit" attendu) |

**Points forts de la gamme :** La référence académique devenue produit commercial de la version complète. La version *Touch* offre la meilleure intégration tactile 3D. La nouvelle version *Lite* tente de s'aligner sur des budgets réels d'amateurs avec l'abandon des Dynamixel au profit de Feetech.
**Points faibles :** La version Lite perd l'indépendance des doigts (sous-actionnement), utilise des moteurs Feetech moins performants en compliance, et n'a aucun retour tactile. La version Touch est hors de prix ($6 100).

---

#### 🤖 RUKA Hand (NYU, Open-source, 2024)

Développée par des chercheurs de NYU (New York University), RUKA vise le meilleur compromis entre coût, accessibilité et performance fonctionnelle.

| Paramètre | Détail |
| :--- | :--- |
| **DOF** | **15** (sous-actionnés, 5 doigts dont pouce 3 DOF) |
| **Type d'actionnement** | Tendons tressés (câble pêche) dans gaines PTFE + poulies |
| **Moteurs** | 3× Dynamixel **XM430-W210-T** (Pouce) + 8× **XL330-M288-T** (Doigts) |
| **Nombre de servos** | **11 servos** (déportés dans l'avant-bras) |
| **Couple max moteur** | 4.1 N.m (XM430) / 0.52 N.m (XL330) |
| **Force de grip (Power grasp)** | **~60 N** (levée de >6 kg) |
| **Force de pince (Pinch)** | ~2.74 N (pulpe-à-pulpe) — dosage fin |
| **Force glissement (DIP/PIP)** | 33 N |
| **Poids** | Compact (structure PLA+TPU) |
| **Taille** | ~18 cm (taille adulte) |
| **Capteurs tactiles** | ❌ Aucun capteur embarqué |
| **Retour proprioceptif** | Via lecture de courant Dynamixel uniquement |
| **Contrôle** | Apprentissage (calibration avec gant Motion Capture Manus VR) |
| **Temps d'assemblage** | <7 heures |
| **Open-source** | ✅ Complet : STLs, code, doc sur GitHub (NYU Robotics) |
| **Coût matière** | **~$500 à $1 300** selon qualité des servos |
| **SDK/ROS** | ✅ Dynamixel SDK + ROS 2 |
| **Matériaux** | PLA (structure) + Filaflex Foamy TPU (coussins) + Dyneema/fil pêche + PTFE |

**Points forts :** Excellent rapport coût/DOF, compatibilité Dynamixel totale, très bien documenté, taille humaine réelle.
**Points faibles :** Pas de capteurs tactiles, faible force de pince pouce-index (2.74 N — délicat pour manipulation), dépend d'un système de calibration Motion Capture externe.

---

#### 🦾 BiDexHand V4 (Open-source, 2024)

Projet communautaire avec architecture biomimétique avancée et 16 DOF complets câble-poulie.

| Paramètre | Détail |
| :--- | :--- |
| **DOF** | **16** (biomimétique, articulations MCP/PIP/DIP + pouce opposable) |
| **Type d'actionnement** | Câbles + poulies (N-configuration) |
| **Moteurs** | **15× FeeTech SCS** (série bus) — 1 servo par joint actif |
| **Couple moteur (max)** | ~3.0 N.m (STS3215-class) |
| **Force mesurée à la pulpe** | **~21 N** (2.14 N par doigt × multiplication mécanique) |
| **Charge maximale levée** | ~4.5 kg (≈ 45 N) |
| **Capteurs tactiles** | ❌ Non intégrés dans la version V4 |
| **Poids** | Compact (impression 3D) |
| **Open-source** | ✅ Complet sur GitHub (BOM, STLs, ROS 2) |
| **Coût matière estimé** | **~$300–500** (15× FeeTech SCS à ~15-20 $/servo + 3D print) |
| **SDK/ROS** | ✅ ROS 2 + packages de contrôle inclus |
| **Montage servos** | Déportés dans le "Proximal Servo Sleeve" (proche poignet) |

**Points forts :** Le plus abordable pour 16 DOF, ROS 2 natif, architecture câble-poulie la plus proche de notre conception, excellente réduction d'inertie distale.
**Points faibles :** Force par doigt mesurée modeste (2.14 N), pas de capteurs tactiles, servos FeeTech moins fiables sur long terme, pas de compliance logicielle native aussi poussée que Dynamixel.

---

#### 🔗 ILDA Hand (Linkage-Driven, Étude Harvard/MIT, 2022)

Projet académique de référence, utilisé pour cadrer les performances des mains dextres. Architecture par bielles et non par câbles purs, mais cité pour sa comparaison de force.

| Paramètre | Détail |
| :--- | :--- |
| **DOF** | **15** (20 joints, une bielle par joint) |
| **Type d'actionnement** | Bielles mécaniques (linkage-driven) — pas de câbles |
| **Force à la pulpe du doigt** | **34 N** (mesurée) |
| **Poids** | 1.1 kg |
| **Taille** | 218 mm max |
| **Capteurs tactiles** | ✅ Intégrés (tactile sensing) |
| **Open-source** | ⚠️ Partiel (publication ArXiv/papers uniquement, pas de STLs publics) |
| **Coût** | Non disponible (composants usinés précision) |

> Mentionnée uniquement pour référence de performance. **Non reproductible en DIY** en raison des tolérances d'usinage très fines.

---

### 9.2 Tableau Comparatif Global

| Critère | 🏆 **D-Hand Hybrid** (Notre choix) | **ORCA Hand (Base/Touch)** | **ORCA Lite** (Nouveau) | **RUKA Hand** (NYU) | **BiDexHand V4** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **DOF** | **8** | 17 | 9 | 15 | 16 |
| **Type actionnement** | Câbles + poulies Ø8mm alu | Câbles + poulies | Câbles (couplés) | Câbles fil pêche PTFE | Câbles + poulies |
| **Moteurs** | 4× XC430 + 4× XC330 | Dynamixel XC (17×) | 9× Feetech HL | 3× XM430 + 8× XL330 | 15× FeeTech SCS |
| **Nb servos** | **8** | 17 | 9 | 11 | 15 |
| **Couple max** | 1.9 N.m (XC430) | 1.9 N.m (XC430) | 0.92 N.m (HL3915) | 4.1 N.m (XM430) | ~3.0 N.m (STS) |
| **Force grip (Power)** | **~160-190 N*** | ~103 N (mesuré) | Inconnue (~50 N) | ~60 N (>6 kg) | ~45 N (~4.5 kg) |
| **Capteurs tactiles** | ✅ eFlesh 3 axes (optionnel) | ✅ FSR ou 351 Taxels | ❌ Aucun | ❌ Aucun | ❌ Aucun |
| **Compliance active** | ✅✅ Totale (mode courant) | ✅✅ Totale (Dynamixel) | ⚠️ Limitée (Feetech) | ✅ Partielle (Dynamixel) | ⚠️ Partielle (FeeTech) |
| **Poids main** | **~400g** (avg) | ~1 300g | ~700g | Compact (<400g) | Compact (<300g) |
| **Prix /main** | **~1 110 €** (avec eFlesh) | **$3 500 à $6 100** | BOM DIY à venir | **~500-1 300 $** | **~300-500 $** |
| **Reproductibilité DIY** | ✅ Bonne (CNC C500 + Qidi Plus 4) | ✅ Bonne (<8h) | ✅ Très bonne (<7h) | ✅ Bonne | ❌ Non |
| **Open-source** | ✅ (ce doc) | ✅ Complet (orcahand.com) | ✅ Complet (GitHub NYU) | ✅ Complet (GitHub) | ⚠️ Partiel |
| **Niveau complexité** | 🟡 Moyen | 🔴 Élevé | 🟢 Faible-Moyen | 🟢 Moyen | 🔴 Très élevé |

*\* Force estimée par calcul (moteur → poulie → tendon → phalange). Pas encore validée par mesure physique sur prototype D-Hand.*

---

### 9.3 Focus : Comparaison de la Force de Pince et de Grip

La force de prise est le critère fonctionnel le plus important pour la manipulation d'objets du quotidien.

#### Force de Grip en Power Grasp (Prise Cylindrique Complète)

| Main | Force Mesurée | Correspondance Quotidienne |
| :--- | :---: | :--- |
| **ORCA Hand** | **103 N** ✅ | Porter un pack de 6 bouteilles (10 kg) |
| **D-Hand Hybrid** (calc.) | **~160-175 N** ✅✅ | Serrer vigoureusement une poignée de porte + tenir un outil |
| **RUKA Hand** | **~60 N** ⚠️ | Tenir un stylo épais / ouvrir un bouchon |
| **BiDexHand V4** | **~45 N** ⚠️ | Tenir un verre, objet léger |
| **Main Humaine** (ref.) | **300-400 N** | — |

> **Notre position :** La D-Hand Hybrid avec les XC430 sur les canaux de force a la force calculée la plus élevée de tous les projets DIY comparés, y compris l'ORCA Hand académique. **À valider par mesure sur prototype.**

#### Force de Pince Pouce-Index (Pinch Grasp)

| Main | Force de Pince | Correspondance Quotidienne |
| :--- | :---: | :--- |
| **ILDA Hand** | **34 N** ✅ | Tenir fermement une clé à l'appel |
| **D-Hand Hybrid** (calc.) | **~50 N** ✅✅ | Pincer et soulever une pièce mécanique |
| **BiDexHand V4** | **~21 N** ⚠️ | Pincer une feuille de papier |
| **ORCA Hand** | **~30 N** (estimé) | Tenir une bille |
| **RUKA Hand** | **2.74 N** ❌ | Pincer une feuille millimétrée |

> La faiblesse critique de RUKA est sa pince (2.74 N mesurés) car les XL330 n'ont que 0.52 N.m de couple. C'est sa limitation majeure vs notre XC430+XC330.

---

### 9.4 Architecture Mécanique : Câbles et Poulies (Points de Différenciation)

Le tableau ci-dessous compare les choix d'architecture pour le routage des tendons et des poulies :

| Aspect | D-Hand Hybrid | ORCA Hand | RUKA Hand | BiDexHand V4 |
| :--- | :--- | :--- | :--- | :--- |
| **Matière tendon** | Dyneema Ø0.8mm (40 lbs) | Acier inox / Dyneema | Fil de pêche tressé | Dyneema/FeeTech câble |
| **Gaine de guidage** | PTFE Ø1.5mm int. | PTFE tube custom | PTFE tube (Bowden style) | Gaines intégrées |
| **Matière poulies** | **Alu 6061 Ø8mm (CNC C500)** | Imprimées PLA renforcé | Imprimées PLA | Imprimées PLA |
| **Retour passif** | Ressorts torsion 0.05 N.m | Ressorts torsion intégrés | Ressorts enrobés dans la phalange | Ressorts impression TPU |
| **Fixation tendon** | Nœud + cyanoacrylate | Serre-câble + manchon | Nœud + époxy | Nœud |
| **Chemin de câble** | Traversée RS-00 (poignet creux) | Poignet propriétaire | Poignet tubulaire dédié | Proximal Sleeve tubulaire |

**Avantage D-Hand** : les poulies en aluminium usiné CNC offrent une durabilité supérieure aux poulies imprimées (usure quasi nulle sur Dyneema vs PLA qui creuse à l'usage).

---

### 9.5 Verdict et Positionnement du D-Hand Hybrid

| Critère | D-Hand Hybrid | ORCA | RUKA | BiDexHand |
| :--- | :---: | :---: | :---: | :---: |
| **Force brute** | 🥇 1er (~175N calc) | 🥈 2ème (103N mesuré) | 🥉 3ème (~60N) | 4ème (~45N) |
| **Dextérité** | 🥉 3ème (8 DOF) | 🥇 1er (17 DOF) | 🥈 2ème (15 DOF) | 🥈 2ème (16 DOF) |
| **Coût** | 🥉 3ème (~1 110€) | 4ème (~2 000€) | 🥇 1er (~650€) | 🥈 2ème (~400€) |
| **Compliance** | 🥇 1er (Dynamixel mode courant) | 🥇 1er (= , Dynamixel) | 🥈 2ème | 🥉 3ème (FeeTech) |
| **Poids** | 🥈 2ème (~400g) | 4ème (1 300g) | 🥇 1er (<300g) | 🥇 1er (<300g) |
| **Tactile** | 🥇 1er (eFlesh 3 axes) | 🥉 3ème (FSR basic) | ❌ Absent | ❌ Absent |
| **Maturité technique** | 🥇 Haut niveau | 🥇 Très haut | 🥈 Haut | 🥇 Haut |
| **Difficulté build** | 🥈 Moyen | 🔴 Élevé | 🥇 Faible | 🥇 Faible |

> [!TIP]
> **Conclusion** : Le D-Hand Hybrid n'est pas le moins cher ni le plus dextère, mais il est le **seul projet** qui combine simultanément : force de grip estimée maximale **+ capteurs 3 axes + compliance active totale + intégration ROS 2 / Isaac Gym**. C'est le seul comparable au Tesla Optimus Gen3 en termes de force effective estimée dans le monde open-source.

> [!NOTE]
> **Ce qu'il manque vs l'ORCA** : 9 DOF supplémentaires (abductions des doigts, oppositions fines). Ces DOF supplémentaires permettent des prises en "pincette à 3 doigts" et des manipulations en rotation dans la paume ("in-hand manipulation"). Ce manque pourra être comblé en V2 si l'IA de manipulation dépasse les capacités de l'ORCA Hand en tests comparatifs grâce aux capteurs eFlesh.

*Source des données : arxiv.org (ORCA 2024, RUKA 2024), GitHub BiDexHand V4, orcahand.com, humanoid.guide. Mars 2026.*

---

## 10. Étude de Mix : Utiliser l'ORCA Hand comme Base Mécanique pour la D-Hand

### 10.1 Le Constat

Notre plus grande faiblesse actuelle est le **manque de design mécanique concret pour les doigts** du D-Hand Hybrid. Nous avons la théorie (8 DOF, servos XC430+XC330, tendons Dyneema, poulies alu), mais pas encore les fichiers CAD des phalanges, de la paume ni du routage de câble.

L'ORCA Hand, elle, dispose de **tout cela en open-source** :
- **Fichiers STEP + STL** prêts à imprimer (disponibles sur orcahand.com/legacy/files)
- **Guide d'assemblage en 31 étapes** avec photos détaillées
- **BOM complète** sur GitHub (orcahand/orca_core)
- **Modèles URDF/MJCF** pour la simulation (orcahand/orcahand_description)
- **Environnement de simulation** Isaac Gym (orcahand/orca-gym)
- **Système de téléopération** (orcahand/orca_retargeter)

La question est : **peut-on réutiliser les pièces mécaniques ORCA tout en gardant notre stratégie d'actionnement D-Hand ?**

---

### 10.2 Les 4 Scénarios de Mix Possibles

#### Scénario A : « ORCA Fingers + D-Hand Actionneurs » (Recommandé ✅)

**Concept** : Prendre les phalanges ORCA (imprimées PA12-CF) telles quelles, mais les relier à **nos 8 servos Dynamixel XC430/XC330** au lieu des 17 servos ORCA.

| Composant | Source | Modification requise |
| :--- | :--- | :--- |
| **Phalanges (proximale, médiane, distale)** | ORCA v1 (fichiers STEP) | Aucune — canaux de tendon compatibles |
| **Paume (palm)** | ORCA v1 (fichier STEP) | Adaptations mineures : réduire les 17 passages à 8 |
| **Tendons** | D-Hand (Dyneema Ø0.8mm) | Compatible directement avec les canaux ORCA |
| **Gaines PTFE** | D-Hand (Ø1.5mm int.) | Même approche que l'ORCA (tube Téflon) |
| **Poulies** | D-Hand (Alu CNC Ø8mm) | Avantage : plus durables que les poulies imprimées ORCA |
| **Servomoteurs** | D-Hand (4× XC430 + 4× XC330) | Montage dans l'avant-bras avec bride custom |
| **Nœuds de tendon** | ORCA (Ashley Stopper Knot) | ✅ Adopter cette technique éprouvée |
| **Retour passif (extension)** | ORCA (ressorts torsion) | Compatible directement |
| **Capteurs tactiles** | D-Hand (eFlesh 3 axes) | Montage sur pulpe distale ORCA (à vérifier encombrement) |

**Couplage des tendons (passage de 17 à 8 DOF) :**

| Doigt | ORCA (3 servos indépendants) | D-Hand Mix (tendons couplés) |
| :--- | :--- | :--- |
| **Index** | MCP curl + PIP curl + Abduction | 1× XC430 (MCP+PIP couplés) + 1× XC330 (Abduction) |
| **Majeur** | MCP curl + PIP curl + Abduction | 1× XC430 (MCP+PIP couplés) |
| **Annulaire** | MCP curl + PIP curl + Abduction | Couplé avec Majeur sur même XC430 |
| **Auriculaire** | MCP curl + PIP curl + Abduction | Couplé avec Annulaire |
| **Pouce** | IP + MCP + Opposition | 1× XC430 (IP+MCP couplés) + 1× XC330 (Opposition) |
| **Abd. Index/Aur.** | 2× servos indépendants | 1× XC330 (partagé) |

**Avantages :**
- ✅ **Gain de temps énorme** : pas besoin de dessiner les phalanges from scratch
- ✅ **Design validé** : >10 000 cycles prouvés sur les doigts ORCA
- ✅ **Mêmes matériaux** : PA12-CF + Dyneema + PTFE = identique à notre baseline
- ✅ **Ashley Stopper Knot** : technique de fixation tendon bien documentée, meilleure que notre colle cyano
- ✅ **Simulation prête** : URDF/MJCF directement disponible pour Isaac Gym
- ✅ **Force supérieure** : les XC430 (1.9 Nm) délivrent 2× plus de couple que les HL-3915 de l'ORCA Lite

**Risques :**
- ⚠️ Adapter la paume ORCA (17 chemins → 8) nécessite une retouche CAD
- ⚠️ Vérifier l'encombrement des capteurs eFlesh dans la pulpe distale ORCA

**Coût estimé :**

| Poste | Prix |
| :--- | ---: |
| 4× XC430-T240BB-T | 560 € |
| 4× XC330-T228T | 280 € |
| Filament PA12-CF (phalanges) | ~30 € |
| Dyneema + PTFE + ressorts | ~25 € |
| Poulies alu CNC (8×) | ~40 € |
| eFlesh 3 axes (5 doigts) | ~175 € |
| **Total** | **~1 110 €** |

---

#### Scénario B : « Full ORCA Lite Replica + eFlesh » (Budget)

**Concept** : Reproduire l'ORCA Lite telle quelle (9 DOF, servos Feetech), mais ajouter nos capteurs eFlesh 3 axes.

| Composant | Source |
| :--- | :--- |
| Phalanges + Paume | ORCA Lite (STLs à venir) |
| Servomoteurs | 9× Feetech HL-3915/HL-3930 |
| Capteurs | eFlesh 3 axes (ajout custom) |

| Avantage | Inconvénient |
| :--- | :--- |
| ✅ Coût minimal (<900 $ + eFlesh) | ❌ Perte totale de compliance active |
| ✅ Assemblage très simple | ❌ Couple faible (0.92 Nm vs 1.9 Nm) |
| ✅ Open-source complet bientôt | ❌ Aucune lecture de courant fine sur Feetech |

**Verdict** : ❌ Ne convient PAS pour le D-Bot. La perte de compliance active Dynamixel est rédhibitoire pour la manipulation RL.

---

#### Scénario C : « Full ORCA Base Replica » (Haut de Gamme)

**Concept** : Reproduire l'ORCA Base complète (17 DOF) avec ses 17 servos Dynamixel.

| Avantage | Inconvénient |
| :--- | :--- |
| ✅ 17 DOF = dextérité maximale | ❌ Coût x2 (~2 000 € en composants) |
| ✅ Design 100% validé | ❌ 17 servos = 17× plus de câblage |
| ✅ Simulation Isaac Gym native | ❌ Poids élevé (1.3 kg) |
| | ❌ Complexité d'assemblage élevée |

**Verdict** : ⚠️ Option V2 viable si la V1 montre que 8 DOF sont insuffisants pour la manipulation cible.

---

#### Scénario D : « ORCA Fingers + Paume D-Hand Custom » (Avancé)

**Concept** : Prendre les phalanges ORCA, mais reconcevoir entièrement la paume en aluminium CNC (C500) pour un montage plus rigide et une intégration parfaite avec le poignet RS-00 du D-Bot.

| Avantage | Inconvénient |
| :--- | :--- |
| ✅ Intégration parfaite avec le chassis D-Bot | ❌ Nécessite un design CNC de paume complet |
| ✅ Rigidité supérieure (alu vs PA12-CF) | ❌ Coût CNC additionnel |
| ✅ Poulies alu intégrées dans la paume | ❌ Temps de développement plus long |

**Verdict** : 🟡 Réservé à la V2. La paume imprimée (Scénario A) suffira pour la V1.

---

### 10.3 Ressources ORCA Disponibles sur GitHub

L'écosystème ORCA est remarquablement complet (12 repos, mis à jour en Mars 2026) :

| Repo GitHub | Contenu | Utilité pour D-Hand |
| :--- | :--- | :--- |
| `orcahand/orca_core` | Contrôleur Python (354 ⭐) | ✅ Base du driver servo, à adapter pour nos 8 DOF |
| `orcahand/orcahand_description` | URDF + MJCF (246 ⭐) | ✅✅ Essentiel pour Isaac Gym simulation |
| `orcahand/orca_sim` | Environnement de simulation | ✅ Benchmark comparatif |
| `orcahand/orca-gym` | Isaac Gym (forked from K-Scale) | ✅✅ Template RL direct pour manipulation |
| `orcahand/orca_retargeter` | Téléopération (gant → main) | ✅ Pour la collecte de données humaines |
| `orcahand/rwr_system` | Dataset et inférence | 🟡 Avancé, V2 |
| **Site orcahand.com** | Fichiers STEP/STL + BOM + Guide 31 étapes | ✅✅✅ La base mécanique de notre V1 |

---

### 10.4 Recommandation Finale : Scénario A

> [!IMPORTANT]
> **Le Scénario A « ORCA Fingers + D-Hand Actionneurs »** est le chemin optimal pour la V1 du D-Hand Hybrid.

**Pourquoi :**

1. **Gain de temps** : au lieu de 2-3 mois de conception CAD des phalanges, on peut les imprimer en 24h depuis les fichiers STEP existants.
2. **Fiabilité prouvée** : les doigts ORCA ont résisté à 10 000+ cycles continus, c'est le meilleur test de fatigue disponible en open-source.
3. **Force supérieure** : nos XC430 (1.9 Nm) offrent **2× le couple** des Feetech HL-3915 de l'ORCA Lite (0.92 Nm), donc nous surpassons la force de l'ORCA Lite avec le même nombre de DOF.
4. **Tactile unique** : aucune version ORCA (hors Touch à $6 100) n'offre les capteurs eFlesh 3 axes que nous intégrons pour ~175 €.
5. **Simulation native** : on hérite directement de l'environnement Isaac Gym (`orca-gym`) et des modèles URDF/MJCF (`orcahand_description`).
6. **Couplage câbles Ashley Stopper** : la technique de nœud ORCA est supérieure à notre approche initiale (colle cyano), car elle permet un démontage non destructif et un re-tensionnement facile.

**Plan d'action concret :**

| Étape | Action | Durée estimée |
| :---: | :--- | :---: |
| 1 | Télécharger les fichiers STEP v1 depuis orcahand.com/legacy/files | 10 min |
| 2 | Imprimer les phalanges en PA12-CF sur le Qidi Plus 4 | ~8h |
| 3 | Modifier la paume ORCA dans Fusion 360 (17 → 8 passages) | ~4h |
| 4 | Usiner 8 poulies Ø8mm en alu 6061 sur la CNC C500 | ~2h |
| 5 | Assembler avec la technique Ashley Stopper (guide 31 étapes ORCA) | ~6h |
| 6 | Intégrer les capteurs eFlesh dans les pulpes distales | ~3h |
| 7 | Connecter les 8 servos via Dynamixel Bus + orca_core adapté | ~2h |
| 8 | Tester dans Isaac Gym avec l'URDF ORCA modifié | ~4h |
| **Total** | | **~30h** |

> [!TIP]
> **Versus from-scratch** : concevoir les phalanges à zero nécessiterait environ 2-3 mois de travail CAD + tests itératifs. Le Scénario A réduit ce délai à **~30 heures** de travail effectif (1 semaine à temps partiel).

---

## 11. Stratégie de Fabrication Hybride (Impression 3D vs Usinage CNC)

L’hybridation ne concerne pas seulement le design (ORCA) et l’actionnement (D-Hand/Dynamixel), elle s'applique aussi aux méthodes de fabrication. Le D-Bot dispose d’un écosystème de production in-house très performant : une imprimante **Qidi Plus 4** (enceinte chauffée 65°C) et une fraiseuse CNC **NestWorks C500**. 

Voici l'analyse d'ingénierie dictant comment chaque pièce du "Scénario A" doit être fabriquée pour garantir une robustesse de niveau industriel.

### 11.1 Ce qui doit être IMPRIMÉ en 3D (Qidi Plus 4)

L'impression 3D est irremplaçable pour la création de pièces aux géométries internes complexes ou devant absorber des micro-chocs.

#### 🦴 Les Phalanges (Doigts) : PA12-CF (Nylon Carbone)
*   **Pourquoi l'imprimer ?** Les doigts ORCA possèdent des **canaux internes tubulaires** (souvent courbes) permettant au tendon Dyneema de glisser librement à travers les phalanges. Réaliser ces canaux courbes en usinage CNC 3 axes est physiquement impossible. De plus, des doigts en aluminium massif augmenteraient dramatiquement l'inertie du système, ralentissant les mouvements rapides et augmentant la charge sur les servomoteurs.
*   **Pourquoi le PA12-CF ?** Le Nylon (PA12) est auto-lubrifiant (réduit la friction contre les pièces contiguës des articulations qui n'ont pas de roulements à billes). L'ajout de fibres de carbone (CF) lui confère une rigidité absolue, empêchant le doigt de "plier" sous les 15 kg de tension du tendon.
*   **Méthode** : Fichiers `.3mf` pré-configurés ORCA (si compatibles) ou slicés manuellement pour la Qidi avec support dédié.

#### 🧽 La Peau Tactile (Finger Pads) : Silicone Coulé + FDM (Moule)
*   **Méthode** : Les moules négatifs (molds) sont imprimés en PLA basique, puis du silicone (de type EcoFlex ou DragonSkin) y est coulé pour former la pulpe. L'eFlesh viendra s'insérer sous cette couche.

---

### 11.2 Ce qui DOIT être USINÉ en CNC (NestWorks C500)

La CNC intervient là où l'impression 3D montre ses limites : la résistance au cisaillement continu (fil à couper le beurre) et la rigidité structurelle sous charge asymétrique lourde.

#### ⚙️ Les Poulies d'Enroulement (Spools) : Aluminium 6061
*   **Problème de la 3D** : Dans le design ORCA original, le treuil (spool) fixé sur le servo est imprimé en plastique. Sous l'effort (1.9 Nm d'un XC430 sur un rayon de 8 mm = **>230 N de tension** sur le fil), le fin fil Dyneema (Ø0.8mm) crée une pression locale extrême. À la longue, le fil "scie" le plastique, modifiant le diamètre de la poulie et détruisant la calibration Isaac Gym.
*   **Solution CNC** : Usiner 8 poulies dans un lopin (barre ronde) d'Aluminium 6061 ou 7075.
*   **Bénéfice** : Usure structurelle du tambour strictement égale à zéro, durabilité infinie, calibration mathématique stable.

#### 🧱 La Paume (Carpals / Palm Block) : Aluminium 6061 (Recommandé)
*   **Problème de la 3D** : La paume est le point de concentration des contraintes centrales de toute la main. Elle encaisse simultanément la poussée des objets saisis et la force de compression des 8 tendons tirant à l'unisson (potentiellement >100 kg de force cumulée). Une paume en plastique imprimé – même en CF – va subir des micro-déformations (flex ou fluage) sous charge maximale, faussant la précision des IK (Inverse Kinematics).
*   **Solution CNC** : La paume est généralement un bloc relativement "carré", usinable en 2.5D ou 3D sur trois ou quatre faces sur la C500. 
*   **Bénéfice** : Un châssis "Rock Solid". Les articulations à la base des doigts (MCP) s'ancreront dans de l'aluminium (zéro jeu mécanique), éliminant toute torsion latérale de la main lorsque le poignet bouge brusquement, et offrant un ancrage parfait avec le poignet RS-00 du bras.

#### 🔩 Brides de Support Moteurs (Avant-bras) : Aluminium 6061
*   **Rôle** : Les 8 servomoteurs XC430/XC330 seront entassés dans l'avant-bras. S'ils sont montés sur du plastique, l'avant-bras peut fléchir ou vibrer lors des accélérations (jitter). D'autre part, les moteurs chauffent en maintien de force continue.
*   **Bénéfice CNC** : Une plaque/cage d'intégration moteur usinée en aluminium sert de **dissipateur thermique géant** (heatsink) rayonnant la chaleur des XC430 vers l'extérieur du robot, tout en augmentant la densité structurelle de l'avant-bras.

### 11.3 Synthèse du Flux de Production (D-Hand v1)

| Composant | Matériau | Procédé | Outil | Raison principale |
| :--- | :--- | :--- | :--- | :--- |
| **Phalanges** | PA12-CF | Impression FDM | Qidi Plus 4 | Canaux internes / Légèreté |
| **Moule des peaux** | PLA | Impression FDM | Qidi Plus 4 | Pièce jetable / Coût |
| **Peau Tactile** | Silicone | Coulée manuelle | — | Compliance adhérente |
| **Paume (Palm)** | Alu 6061 | Fraisage CNC 3+1 axes | NestWorks C500 | Rigidité absolue / Zéro fluage |
| **Poulies (Spools)**| Alu 6061 | Fraisage / Tournage | NestWorks C500 | Résistance à la découpe du câble |
| **Bride Moteurs** | Alu 6061 | Fraisage CNC 2.5D | NestWorks C500 | Dissipation thermique / Rigidité |
| **Routage tendons**| Tube PTFE | Coupe manuelle | — | Glissement sans friction (Téflon) |
