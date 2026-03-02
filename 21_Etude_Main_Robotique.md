# Étude Main Robotique : D-Hand Premium

Cette annexe détaille la conception de la main articulée anthropomorphe du D-Bot, basée sur une architecture à **tendons déportés** et des servos **Dynamixel XC330-T288-T** (qualité recherche académique).

## 1. Philosophie de Conception

### Objectif
Obtenir une main de dextérité intermédiaire (8 DOF, ~80 N de grip) permettant la manipulation d'objets courants (outils, bouteilles, poignées de porte), tout en restant réparable, évolutive, et compatible avec l'apprentissage par renforcement (sim-to-real).

### Principe : Actionnement Déporté à Tendons (comme la main humaine)

Dans la main humaine, les muscles responsables de la flexion des doigts sont situés dans l'**avant-bras**, pas dans les doigts eux-mêmes. Des tendons transmettent la force sur de longues distances. La D-Hand reproduit ce principe :

```
┌──────────────────────────────┐
│       AVANT-BRAS D-BOT      │ ← 8 servos XC330 logés ici
│    (structure PA12-CF/Alu)   │ ← Masse moteur : 184g seulement
│                              │
│  Servos → Poulies → Tendons ─┼──→ vers le poignet (RS-00)
└──────────────────────────────┘
                                    │
                               ┌────┴────┐
                               │  MAIN   │ ← Aucun moteur !
                               │  ~250g  │ ← Phalanges PA12-CF
                               └─────────┘    + ressorts de rappel
```

**Avantages** :
- La main est **légère** (~250g) car seules les structures passives s'y trouvent.
- L'inertie au bout du bras est **minimale** → meilleure dynamique de manipulation.
- Les servos dans l'avant-bras sont **facilement accessibles** pour la maintenance.

---

## 2. Choix du Servo : Dynamixel XC330-T288-T

### Pourquoi ce servo ?
C'est le **standard de facto** de la robotique de recherche (Carnegie Mellon LEAP Hand, AGIBOT, Shadow Robot). Il combine compacité extrême, engrenages métaux, et un écosystème logiciel mature.

### Fiche Technique

| Paramètre | Valeur |
| :--- | :--- |
| **Dimensions** | 20 × 34 × 26 mm |
| **Poids** | 23 g |
| **Couple de blocage (12V)** | 1.00 N.m (10.2 kg.cm) |
| **Couple nominal (continu)** | ~0.40 N.m |
| **Vitesse à vide** | 71 RPM (à 12V) |
| **Résolution** | 4096 pas / tour (0.088°) |
| **Encodeur** | Magnétique absolu, sans contact, 12 bits |
| **Réducteur** | Ratio 288:1, engrenages **métaux** |
| **Moteur** | Coreless DC (très faible inertie) |
| **Modes de contrôle** | Position, Vitesse, Courant, PWM, Position+Courant |
| **Protocole** | Dynamixel Protocol 2.0 (TTL, daisy-chain, 4 Mbps) |
| **Tension** | 6.5 – 12V (recommandé 11.1V) |
| **Prix unitaire (EU)** | ~130 € |
| **Backdrivability** | ✅ Mode courant → compliance passive (sécurité) |

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

### 3.1 Affectation des Servos

| # | Doigt | Mouvement | Tendon |
| :---: | :--- | :--- | :--- |
| 1 | **Pouce** | Flexion/Extension (Curl) | Dyneema Ø0.8mm |
| 2 | **Pouce** | Abduction/Adduction (Opposition) | Dyneema Ø0.8mm |
| 3 | **Index** | Flexion (Curl) | Dyneema Ø0.8mm |
| 4 | **Index** | Abduction (Écartement) | Dyneema Ø0.8mm |
| 5 | **Majeur** | Flexion (Curl) | Dyneema Ø0.8mm |
| 6 | **Annulaire** | Flexion (couplé mécaniquement à #7) | Dyneema Ø0.8mm |
| 7 | **Auriculaire** | Flexion (couplé mécaniquement à #6) | Dyneema Ø0.8mm |
| 8 | **Paume** | Curl palmaire global (prise de force) | Dyneema Ø1.0mm |

### 3.2 Implantation dans l'Avant-Bras

L'avant-bras du D-Bot mesure ~22 cm de l'articulation coude à l'articulation poignet (RS-00), avec un diamètre de ~90 mm au coude et ~50 mm au poignet.

```
VUE LONGITUDINALE — AVANT-BRAS (coupe latérale)

  COUDE (RS-02)                              POIGNET (RS-00)
    ←───── 22 cm ──────────────────────────────→
    │                                           │
    │  ┌──────────────────┐                     │
    │  │  8× XC330         │   Espace libre     │
    │  │  3 rangées        │   pour câblage,    │
    │  │  (10 cm)          │   buck 48V→12V,    │
    │  │                   │   U2D2 controller  │
    │  └──────────────────┘                     │
    │  ← 10 cm →            ← 12 cm →          │
```

```
VUE EN COUPE TRANSVERSALE (section au niveau des servos)

              ← ~60 mm →
    ┌────────────────────────────┐
    │  ╔═══════╗ ╔═══════╗      │
    │  ║ XC330 ║ ║ XC330 ║      │  Rangée 1 (Pouce + Index curl)
    │  ║ 20×34 ║ ║ 20×34 ║      │  20mm large × 34mm haut
    │  ╚═══════╝ ╚═══════╝      │
    │  ╔═══════╗ ╔═══════╗      │
    │  ║ XC330 ║ ║ XC330 ║      │  Rangée 2 (décalée 26mm)
    │  ╚═══════╝ ╚═══════╝      │  (Pouce abd. + Index abd.)
    │  ╔═══════╗ ╔═══════╗      │
    │  ║ XC330 ║ ║ XC330 ║      │  Rangée 3
    │  ╚═══════╝ ╚═══════╝      │  (Majeur + Annulaire/Auriculaire)
    │       ╔═══════╗           │
    │       ║ XC330 ║           │  Rangée 4 (Paume)
    │       ╚═══════╝           │
    └────────────────────────────┘

    Encombrement : 60mm largeur × 60mm profondeur × 102mm longueur
    Total : 8 × 23g = 184g de servos
```

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
| **D-Hand Premium** | **~80-100 N** | **8** | **~250g** | **~1 220€** | 8× XC330 |
| LEAP Hand v2 (CMU) | ~80 N | 17 | ~400g | ~4 000€ | 17× Dynamixel |
| Main humaine | ~300-400 N | 27 | ~400g | N/A | — |
| K-Bot Gripper | ~50 N | 1 | ~100g | ~30€ | 1× STS3215 |

### 4.3 Vitesse

| Métrique | D-Hand Premium | Main Humaine |
| :--- | :---: | :---: |
| Temps de fermeture | ~0.5 s | ~0.3 s |
| Temps de prise de force | ~0.7 s | ~0.5 s |

---

## 5. BOM — D-Hand Premium (par main)

| Composant | Qté | Prix Unit. | Total |
| :--- | :---: | :---: | :---: |
| Dynamixel XC330-T288-T | 8 | 130 € | 1 040 € |
| U2D2 (USB↔Dynamixel) | 1 | 35 € | 35 € |
| U2D2 Power Hub | 1 | 25 € | 25 € |
| Buck Converter 48V→12V (5A) | 1 | 15 € | 15 € |
| Tendons Dyneema (bobine 50m) | 1 | 15 € | 15 € |
| Tubes PTFE Ø1.5mm (10m) | 1 | 8 € | 8 € |
| Ressorts de torsion miniatures | 16 | 0.50 € | 8 € |
| Roulements MR52ZZ (2×5×2.5mm) | 16 | 1 € | 16 € |
| Structure main (PA12-CF, impr. 3D) | 1 lot | — | 20 € |
| Poulies Ø8mm alu CNC (C500) | 8 | 5 € | 40 € |
| Visserie M2/M2.5 inox | lot | — | 10 € |
| **TOTAL par main** | | | **~1 230 €** |

**Pour les 2 mains : ~2 460 €.**

### Alimentation
Les XC330 fonctionnent à 12V. Le D-Bot utilise du 48V. Un **Buck Converter 48V→12V 5A** (~15€) sera intégré dans le châssis avant-bras. Courant total max des 8 servos : 8 × 0.88A = 7A (stall), ~3A en usage normal — le buck suffit largement.

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

---

## 7. Comparatif Complet : Deux Philosophies de D-Hand

La conception de la D-Hand n'est pas gravée dans le marbre. Deux approches radicalement différentes ont été étudiées. Ce chapitre les présente côte à côte pour vous permettre de choisir en connaissance de cause.

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

### Comparatif Final Côte à Côte

| Critère | D-Hand Premium (8× XC330) | D-Hand Standard (6× STS3215) |
| :--- | :---: | :---: |
| **Coût total (2 mains)** | **~2 080 €** 🔴 | **~350 €** 🟢 |
| **DOF par main** | **8** | 6 |
| **Poids servos (par main)** | **184 g** 🟢 | 330 g 🔴 |
| **Couple brut** | 1.0 N.m | **3.0 N.m** 🟢 |
| **Bruit fonctionnement** | **~35 dB** 🟢 | ~43 dB 🟡 |
| **Backdrivability** | ✅ Totale 🟢 | ⚠️ Partielle |
| **Intégration avant-bras** | ✅ Aisée (60×60×102mm) | ⚠️ Contrainte (nécessite 6 servos min) |
| **Force de grip estimée** | ~80-100 N | **~120-150 N** (couple brut × poulies) |
| **Écosystème logiciel** | **Dynamixel SDK + ROS 2 natif** 🟢 | Python SCSerial + wrapper 🟡 |
| **Niveau de risque projet** | 🟢 Faible | 🟡 Moyen (intégration plus serrée) |

---

### Recommandations Stratégiques

> **Choisir la Solution A (XC330)** si :
> - Vous privilégiez l'interaction sécurisée avec des humains (compliance totale en mode courant).
> - L'intelligence artificielle et le sim-to-real (Isaac Gym) sont une priorité dès la V1.
> - Vous voulez le bras le plus léger possible pour maximiser la dynamique du bras.

> **Choisir la Solution B (STS3215)** si :
> - Le budget est la contrainte primaire (économie de ~1 680 € sur les 2 mains).
> - Vous préférez commencer avec une main fonctionnelle "à moindre coût" et upgrader en XC330 pour la V2.
> - L'objectif prioritaire est la manipulation d'objets lourds (bouteilles, outils) plutôt que la dextérité fine.
> - Vous acceptez de réduire à **6 DOF** par main (les doigts 4 et 5 couplés).

---
*Étude réalisée en Février/Mars 2026. Prix basés sur ROBOTIS-EU, RobotShop et distributeurs AliExpress.*
