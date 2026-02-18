# 14 - Cinématique & Choix Moteurs

Ce document détaille l'architecture cinématique du D-Bot (**Standard 24 DOF**) et les spécifications techniques des actionneurs **RobStride**.

## 1. Configuration K-Bot Standard (20 DOF)

### 📊 Architecture Officielle K-Scale
Le K-Bot standard est un robot humanoïde open-source de taille réelle développé par K-Scale Labs, équipé de **20 moteurs RobStride** pour 20 degrés de liberté. La configuration D-Bot étend cette base avec une tête articulée.

**Source** : [K-Scale Official Documentation](https://docs.kscale.dev/robots/k-bot/motor-id-mapping)

---

### 🦾 BRAS (10 moteurs - 5 par bras)

**Configuration par bras :**

| Articulation | Moteur | IDs<br/>(G/D) | Couple<br/>Pic | Couple<br/>Nom. | Poids | Fonction |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Épaule Pitch** | RS-03 | 11 / 21 | 60 N.m | 20 N.m | 880g | Lever le bras |
| **Épaule Roll** | RS-03 | 12 / 22 | 60 N.m | 20 N.m | 880g | Écarter le bras |
| **Épaule Yaw** | RS-02 | 13 / 23 | 17 N.m | 6 N.m | 405g | Rotation interne |
| **Coude Pitch** | RS-02 | 14 / 24 | 17 N.m | 6 N.m | 405g | Flexion |
| **Poignet Roll** | RS-00 | 15 / 25 | 14 N.m | 5 N.m | 310g | Orientation fine |

**Total par bras** : 3 kg environ  
**Total 2 bras** : 10 moteurs (4× RS-03 + 4× RS-02 + 2× RS-00)

---

### 🦵 JAMBES (10 moteurs - 5 par jambe)

**Configuration par jambe :**

| Articulation | Moteur | IDs<br/>(G/D) | Couple<br/>Pic | Couple<br/>Nom. | Poids | Fonction |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Hanche Pitch** | RS-04 | 31 / 41 | 120 N.m | 40 N.m | 1420g | Flexion jambe |
| **Hanche Roll** | RS-03 | 32 / 42 | 60 N.m | 20 N.m | 880g | Équilibre latéral |
| **Hanche Yaw** | RS-03 | 33 / 43 | 60 N.m | 20 N.m | 880g | Rotation hanche |
| **Genou Pitch** | RS-04 | 34 / 44 | 120 N.m | 40 N.m | 1420g | Flexion genou |
| **Cheville Pitch** | RS-02 | 35 / 45 | 17 N.m | 6 N.m | 405g | Propulsion (via mécanisme tirant) |

**Total par jambe** : 4.6 kg environ  
**Total 2 jambes** : 10 moteurs (4× RS-04 + 4× RS-03 + 2× RS-02)

---

### 🔢 INVENTAIRE K-BOT STANDARD

| Modèle | Quantité | Poids Unit. | Poids Total | Usage Principal |
| :---: | :---: | :---: | :---: | :--- |
| **RS-04** | 4 | 1420g | 5.68 kg | Hanches Pitch + Genoux |
| **RS-03** | 8 | 880g | 7.04 kg | Épaules + Rotations hanches |
| **RS-02** | 6 | 405g | 2.43 kg | Coudes + Yaw épaules + Chevilles |
| **RS-00** | 2 | 310g | 0.62 kg | Poignets |
| **TOTAL** | **20** | | **15.77 kg** | Total moteurs K-Bot |

---

### 🤖 ÉVOLUTION D-BOT (24 DOF — "D-Bot Performance")

Le **D-Bot** étend le K-Bot de 20 à **24 DOF** avec trois ajouts. Voir [Analyse Biomécanique](./15_Analyse_Biomecanique.md) pour la justification détaillée de chaque upgrade.

| Ajout D-Bot | Moteur | Quantité | Couple Pic | Fonction |
| :--- | :---: | :---: | :---: | :--- |
| **Cou Pan** (Yaw) | RS-05 | 1 | 5.5 N.m | Rotation horizontale tête |
| **Cou Tilt** (Pitch) | RS-05 | 1 | 5.5 N.m | Inclinaison tête |
| **Cheville Roll** 🆕 | RS-00 | 2 (ajout) | 14 N.m | **Stabilité latérale** (compact, précis) |

**Total D-Bot** : 20 (Base) + 2 (Tête) + 2 (Chevilles Roll) = **24 moteurs**.

> [!NOTE]
> **Mécanisme de cheville K-Bot conservé (Tirant/Linkage)** : Le RS-02 de cheville n'est **pas en prise directe** sur l'axe de la cheville. Il est monté **haut dans le tibia** et actionne le pied via un **mécanisme de tirant** (connecting rod / pushrod). Ce bras de levier crée un avantage mécanique (~2:1) qui multiplie le couple effectif : 17 N.m × 2 ≈ **34 N.m** à la cheville. **Le D-Bot conserve cette architecture éprouvée** pour le Pitch, et ajoute un RS-00 en direct-drive pour le Roll.

![Mécanisme de cheville K-Bot avec tirant (RS-02 haut dans le tibia)](./assets/kbot_ankle_linkage.png)

## 2. Spécifications Moteurs RobStride (Gamme Complète)
Voici les données techniques consolidées pour l'ensemble de la gamme RobStride (Février 2025).  
*Prix officiels RobStride ou sources vérifiées (OpenELAB, AiFitLab) - Hors taxes/livraison.*

| Modèle | Pic<br/>(N.m) | Nom.<br/>(N.m) | Vmax<br/>(RPM) | Poids<br/>(g) | Dim.<br/>(mm) | Ratio | Prix<br/>($) | Volt.<br/>(V) | Usage D-Bot |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **RS-05** | **5.5** | 1.6 | 480 | **191** | 46×46×44 | 7.75:1 | **$120** | 48V (15-60V) | **Cou**, Doigts (futur) |
| **RS-00** | **14.0** | 5.0 | 315 | **310** | 57×57×51 | 10:1 | **$135** | 48V (24-60V) | **Poignet** (Compact, fort couple) |
| **RS-01** | **17.0** | 6.0 | 350 | **380** | 78.5×78.5×40 | 7.75:1 | **$140** | 36V (24-48V) | Alternative RS-02 (36V) |
| **RS-02** | **17.0** | 6.0 | 410 | **405** | 78.5×78.5×45.5 | 7.75:1 | **$160** | 48V (24-60V) | **Coude**, Biceps, Poignet |
| **RS-06** | **36.0** | 11.0 | 480 | **621** | 88×88×49 | 9:1 | **$230** | 48V (15-60V) | Entre-deux (Épaule légère) |
| **RS-03** | **60.0** | 20.0 | 195 | **880** | 106×106×56 | 9:1 | **$250** | 48V (15-60V) | **Épaule**, Hanche rot. |
| **RS-04** | **120.0** | 40.0 | 200 | **1420** | 120×120×56 | 9:1 | **$280** | 48V (15-60V) | **Hanche**, Genou, Cheville |

### Analyse Comparative

####  RS-05 vs RS-00 (Petits Moteurs)
*   **RS-05** : Ultraléger (191g), idéal pour le cou où chaque gramme compte. Couple modeste (5.5 N.m) mais suffisant pour orientation.
*   **RS-00** : Plus dense (310g, +62%) mais délivre **2,5× plus de couple** (14 N.m). Parfait pour un poignet devant porter des charges sans fléchir.

#### RS-01 vs RS-02 (Moteurs Moyens)
*   **Même couple** (17 N.m pic), mais **RS-01** optimisé pour **36V** (idéal pour batteries LiPo 8S), plus compact en profondeur (40mm vs 45.5mm).
*   **RS-02** : Conçu pour **48V**, marginalement plus lourd (+25g). Standard pour D-Bot aux coudes/biceps.

#### RS-06 (Intermédiaire Nouveau)
*   **Niche** : Entre RS-02 (17 N.m) et RS-03 (60 N.m). Avec **36 N.m** et 621g, c'est un compromis pour des articulations nécessitant plus que du RS-02 sans le poids du RS-03.
*   **Usage potentiel** : Épaule de petits robots, torse rotation, ou remplacer un RS-03 si l'on veut économiser 260g et 20$.

#### RS-03 vs RS-04 (Gros Moteurs)
*   **Saut de performance brutal** : RS-03 → 60 N.m (880g) ; RS-04 → **120 N.m** (1420g, +61% poids).
*   **RS-03** : Minimum vital pour l'épaule D-Bot (couple nécessaire pour contrer le bras-de-levier).
*   **RS-04** : Incontournable pour hanches/jambes. **Attention** : Peut briser des pièces PLA/PETG standard → Utiliser **PETG-CF (100% remplissage)** ou **Alu 6061 CNC**.

### Choix pour le D-Bot — Répartition Complète (24 DOF)
| Zone | Moteur | Quantité | Couple Pic | Justification |
| :--- | :---: | :---: | :---: | :--- |
| Cou (Pan/Tilt) | RS-05 | 2 | 5.5 N.m | Légèreté critique (tête avec OAK-D Pro ~100g, LiDAR L2 sur le torse) |
| Poignet | RS-00 | 2 | 14 N.m | Compact, fort couple pour manipulation fine |
| Épaule Yaw + Coude | RS-02 | 4 | 17 N.m | Standard polyvalent 48V |
| Épaule Pitch/Roll | RS-03 | 4 | 60 N.m | Force pour porte-à-faux bras tendu |
| Hanche Roll/Yaw | RS-03 | 4 | 60 N.m | Équilibre latéral + rotation |
| Hanche Pitch + Genou | RS-04 | 4 | 120 N.m | Portance totale (~36 kg robot) |
| **Cheville Pitch** | **RS-02** | **2** | **17 N.m** (×2 avec tirant = ~34 N.m) | **Propulsion via tirant** (architecture K-Bot conservée) |
| **Cheville Roll** 🆕 | **RS-00** | **2** | **14 N.m** | **Stabilité latérale (compact, ratio 10:1)** |

**Total moteurs D-Bot** : 2 + 2 + 4 + 4 + 4 + 4 + 2 + 2 = **24 moteurs**.

## 3. Communication & Alimentation
Tous les moteurs partagent le même protocole :
*   **Bus** : CAN 2.0B @ 1 Mbps.
*   **Alimentation** : 48V DC Nominal (Supportent 24V mais avec couple/vitesse réduits). RS-01 optimisé pour 36V.
*   **Câblage** : Daisy-chain (Chaîne) via connecteurs JST-GH 1.25mm (Data) et XT60 (Power).
*   **Encodeurs** : Dual 14-bit magnetic encoders (haute précision + redondance).
*   **Protection** : IP52 standard (IP67 en option sur certains modèles).

> [!WARNING]
> **Attention au RS-04** : Avec 120 N.m de couple, ce moteur peut briser des pièces imprimées en PLA ou PETG standard en cas de collision. Utilisez impérativement du **PETG-CF** (Remplissage 100%) ou des pièces CNC Alu 6061 pour les brackets de hanches.

> [!NOTE]
> **Prix et Disponibilité** : Les prix sont issus des sources officielles RobStride et distributeurs agréés (OpenELAB, AiFitLab) en Février 2025. Vérifiez la disponibilité avant commande - certains modèles peuvent avoir des délais variables.

---

## 4. Benchmark Industrie — D-Bot vs Robots Haut de Gamme

### 4.1 Comparatif Global (Corps Entier)

| Robot | DOF | DOF/Jambe | Cheville | Méca. Cheville | Couple max jambe | Poids | Actionneurs | Prix |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :--- | :---: |
| **D-Bot (notre)** | **24** | **6** | **2 (P+R)** | **Série QDD** | **120 N.m** (RS-04) | ~38 kg | QDD RobStride 9:1 | ~$5k |
| K-Bot (base) | 20 | 5 | 1 (P) | Tirant (linkage) | 120 N.m (RS-04) | ~34 kg | QDD RobStride 9:1 | ~$4k |
| **Unitree G1** | 23 | **6** | **2** | **Parallèle RSU** | **120 N.m** | 35-47 kg | QDD propriétaire | ~$16k |
| **Tesla Optimus** | 28+ | 6 | 2 | **Parallèle SPU** | **180 N.m** rotary / 8000N linéaire | ~73 kg | Harmonic + Linéaire | N/A |
| **Figure 02** | 28 | 6 | 2 | **Universel + linéaire** | **150 N.m** | ~60 kg | Custom harmonic | N/A |
| **Fourier GR-2** | 53 | ~8 | 2+ | **Parallèle** (FSA 2.0) | **380 N.m** | 63 kg | FSA 2.0 (7 types) | ~$150k |
| **Agility Digit** | 28 | 5 | 2 | **SEA** (élastique) | N/A | 65 kg | Series-Elastic | ~$300k+ |

> [!NOTE]
> **Positionnement D-Bot** : Avec 24 DOF, 6 DOF/jambe et 2 DOF cheville, le D-Bot est au niveau du Unitree G1 en terme d'architecture cinématique, pour un budget 3× inférieur. Le principal écart est le type de mécanisme de cheville (série vs parallèle).

### 4.2 Mécanismes de Cheville — Les 4 Approches

![Comparaison des 3 mécanismes de cheville principaux : Série, Tirant, Parallèle](./assets/ankle_mechanisms_comparison.png)

#### A. Série Direct-Drive (D-Bot Actuel)

Le moteur Pitch (RS-02) est monté **en haut du tibia** avec tirant/bielle (architecture K-Bot conservée). Le Roll (RS-00) est monté **directement à la cheville** en direct-drive.

| Paramètre | Valeur |
| :--- | :--- |
| **Moteurs** | RS-02 (Pitch, haut tibia + tirant) + RS-00 (Roll, à la cheville) |
| **Masse distale** | **~1190g** (880g + 310g) |
| **Couple Pitch effectif** | ~34 N.m (RS-02 17 N.m × ratio tirant ~2:1) |
| **Couple Roll effectif** | 14 N.m (= couple RS-00, suffisant corrections fines) |
| **Complexité** | ⭐ Très faible — assemblage trivial |
| **Coût mécanique** | ~$0 (juste le bracket en L) |

#### B. Tirant / Linkage (K-Bot Original)

Le moteur RS-02 est monté **en haut du tibia** et actionne le pied via un **pushrod** (barre de poussée). Le ratio de levier multiplie le couple.

| Paramètre | Valeur |
| :--- | :--- |
| **Moteurs** | RS-02 (Pitch uniquement), haut dans le tibia |
| **Masse distale** | **~0g** (moteur en haut) |
| **Couple Pitch effectif** | ~34 N.m (17 × ratio ~2:1) |
| **Roll** | ❌ Absent |
| **Complexité** | ⭐⭐ Moyenne — pushrod + pivot |
| **Coût mécanique** | ~$20-50 (barre usinée + pivots) |

#### C. 🆕 Hybride Tirant + Roll Direct (Proposition D-Bot V2)

**Combine le meilleur des deux mondes** : Pitch via tirant (moteur haut, couple multiplié) + Roll en direct-drive à la cheville (correction fine, pas besoin de rapport de levier).

| Paramètre | Valeur |
| :--- | :--- |
| **Moteur Pitch** | RS-02 → **RS-03** monté **haut dans le tibia** + pushrod |
| **Moteur Roll** | RS-00 monté **à la cheville** (direct-drive) |
| **Masse distale** | **~310g** (seulement le RS-00 Roll) |
| **Couple Pitch effectif** | **~120 N.m** (60 × ratio ~2:1) ⚡ |
| **Couple Roll effectif** | 14 N.m (suffisant pour correction latérale) |
| **Complexité** | ⭐⭐⭐ Élevée — pushrod + bracket + pivot |
| **Coût mécanique** | ~$50-100 (barre, pivots, usinage) |

```
  ┌─────┐
  │GENOU│
  └──┬──┘
     │
  ╔══╧══╗ RS-03 Pitch ← Moteur HAUT (880g)
  ║PITCH║──────┐
  ╚═════╝      │ Pushrod
     │ Tibia   │ (barre de poussée)
     │         │
     │         │ Ratio levier ~2:1
     │         │ → 60 × 2 = 120 N.m effectifs !
     │         │
     │    ╔════╧═╗
     └────╢ ROLL ╟── RS-00 (310g) ← Seul moteur EN BAS (compact 57mm)
          ╚══╤═══╝
          ┌──┴──┐
          │PIED │
          └─────┘
```

#### D. Parallèle 2 Bielles Rotulées (Unitree G1, LOLA TUM)

Deux moteurs montés **en haut du tibia**, chacun relié au pied par une **bielle avec rotules** (rod end bearings). Mouvements coordonnés = Pitch, différentiels = Roll. **Aucun moteur à la cheville.**

```
    Moteur A            Moteur B      ← 2 moteurs HAUT dans le tibia
       │                    │
       │ Bielle A           │ Bielle B    ← Tiges filetées M4 avec
       │ (rod end +         │               rod end bearing (rotule)
       │  tige M4)          │               à chaque extrémité
       │                    │
       ╰────────┬───────────╯
                │
           ┌────┴────┐
           │  PIED   │        ← Plateforme mobile (2 DOF)
           └─────────┘

A↑ + B↑ (même sens)    = PITCH (flexion/extension)
A↑ + B↓ (sens opposé) = ROLL  (inversion/éversion)
```

| Paramètre | Valeur |
| :--- | :--- |
| **Moteurs** | 2× RS-02 (ou RS-03 pour plus de couple) haut dans le tibia |
| **Bielles** | 2× tiges filetées M4 inox (60-100mm) + 4× rod end bearings M4 |
| **Masse distale** | **~0g** (seules les bielles sont en bas, ~20g/bielle) |
| **Couple Pitch effectif** | ~34 N.m (2× RS-02) ou ~120 N.m (2× RS-03) |
| **Couple Roll effectif** | ~17 N.m (2× RS-02) ou ~60 N.m (2× RS-03) |
| **Complexité** | ⭐⭐⭐⭐ Très élevée — cinématique parallèle inverse |
| **Coût mécanique** | ~$20-50 (bielles RC + brackets imprimés/CNC) |

**Implémentations industrielles :**

| Robot | Type de bielle | Moteur | Particularité |
| :--- | :--- | :--- | :--- |
| **Unitree G1** | Bielles rotatives parallèles | QDD propriétaire | Mode AB (moteurs) / PR (Pitch-Roll), cinématique inverse intégrée |
| **LOLA (TUM)** | Vis à billes (ball-screw) linéaires | Drives linéaires | 2 vis actionnent le pied — même sens = Pitch, sens inverse = Roll |
| **Tesla Optimus** | SPU (Spherical-Prismatic-Universal) | Actionneurs linéaires custom | Universal joint + prismatic drives, couple >180 N.m (brevet WO2024072984A1) |

> [!WARNING]
> **Fourier GR-2 : marche arrière sur le parallèle.** En septembre 2024, Fourier Intelligence a **abandonné l'architecture parallèle** au profit du série pour le GR-2. Raisons officielles :
> - Simplification du **système de contrôle** (cinématique inverse complexe éliminée)
> - **Débogage** et maintenance facilités  
> - **Coûts de fabrication** réduits
> - Meilleur **transfert sim-to-real** (simulation → robot physique)
>
> C'est un signal fort : le parallèle n'est optimal que si l'on maîtrise parfaitement la cinématique et si les performances l'exigent. Pour un premier prototype, la configuration série ou hybride est plus prudente.

### 4.3 Composants Pré-Assemblés pour Solution Parallèle (Sourcing)

Pour une solution 2-bielles, les composants RC hélicoptère/drone sont **directement réutilisables** :

| Composant | Référence Type | Source | Prix | Note |
| :--- | :--- | :--- | :---: | :--- |
| **Rod end bearing M4** (rotule femelle) | Fisheye ball bearing SA4T/K | AliExpress, eBay | **$3-8 / 10pcs** | Acier roulements, ±15° angle |
| **Tige filetée M4 inox** (bielle) | Tige M4 × 80mm | Quincaillerie | **$2-5** | Longueur réglable (écrou) |
| **Kit pushrod RC complet** | RJX Hobby M3/M4 swashplate linkage | RJXHobby, AliExpress | **$5-12 / kit** | Tige + 2 rod ends pré-assemblés |
| **Rod end M4 double filetage** (CW+CCW) | Pour longueur réglable sans démontage | AliExpress | **$5-10 / lot** | Comme les tirants de direction auto |
| **Rotule industrielle** (Heim joint M4) | M4 male/female rod end | RS Components, Misumi | **$3-8 / pièce** | Qualité supérieure |

> [!NOTE]
> **Il n'existe PAS de kit "2-bielles parallèle pour cheville robot" pré-assemblé clé en main.** Mais les composants individuels (rod ends + tiges) issus du monde RC hélicoptère (plateau cyclique / swashplate) sont **identiques** mécaniquement et coûtent ~$15-25 pour équiper les 2 chevilles. L'assemblage final nécessite un bracket custom (impression 3D ou CNC).

**BOM Estimé — Kit 2 bielles par cheville :**

| Pièce | Qté (×2 chevilles) | Coût |
| :--- | :---: | :---: |
| Rod end bearing M4 (rotules) | 8 (4 par cheville) | ~$8 |
| Tiges filetées M4 × 80mm inox | 4 | ~$5 |
| Écrous M4 frein (nylstop) | 8 | ~$2 |
| Brackets pivot (impression 3D PA12-CF) | 4 (2 haut tibia + 2 bas pied) | ~$15 (filament) |
| Visserie M4 × 12mm inox | 16 | ~$3 |
| **Total bielles** | | **~$33** |

### 4.4 Impact sur la Marche et la Course

| Critère | A. Tirant+Roll (V1) | B. Tirant seul (K-Bot) | C. Tirant RS-03 (V2) | D. Parallèle (V3) |
| :--- | :---: | :---: | :---: | :---: |
| **Masse distale (par jambe)** | 310g | ~0g | **310g** | ~0g |
| **Couple Pitch effectif** | ~34 N.m | ~34 N.m | **~120 N.m** ⚡ | ~34-120 N.m |
| **Couple Roll** | 14 N.m (RS-00) | ❌ | 14 N.m (RS-00) | ~60 N.m |
| **Marche lente (<1 km/h)** | ✅ **OK** (Déroulé pied) | ✅ **OK** (Déroulé pied) | ✅ **Excellent** | ✅ Optimal |
| **Marche normale (2-3 km/h)** | ❌ Couple insuffisant | ❌ (pas de Roll) | ✅ **Excellent** | ✅ Optimal |
| **Marche rapide (3-4 km/h)** | ❌ Couple insuffisant | ❌ (pas de Roll) | ⚠️ Roll au pic | ✅ Bon |
| **Course (>5 km/h)** | ❌ Trop d'inertie | ❌ (1 DOF) | ⚠️ **Possible** | ✅ Optimal |
| **Terrain irrégulier** | ✅ (2 DOF) | ❌ (1 DOF) | ✅ (2 DOF) | ✅ (2 DOF) |
| **Simplicité montage** | ⭐ Trivial | ⭐⭐ Moyen | ⭐⭐⭐ Élevé | ⭐⭐⭐⭐ Très élevé |
| **Coût mécanique** | $0 | $20-50 | $50-100 | $33-100 |

#### Analyse Détaillée de l'Impact Inertiel

```
Moment d'inertie de la jambe pendant le balancement (swing phase) :

I = Σ(m × r²) où r = distance au pivot (hanche)

                    Masse distale    r (dist. hanche)    Contribution I
D-Bot V1 (tirant):  310g             ~0.70 m             152 g.m²  ← RS-00 seul en bas
V2 (RS-03 tirant):  310g             ~0.70 m             152 g.m²  ← Même (RS-00 seul en bas)
V3 (parallèle):    ~40g             ~0.70 m              ~20 g.m²  ← Optimal

→ V1 et V2 ont la même masse distale (~310g = RS-00 Roll seul) car le Pitch est toujours en haut du tibia.
→ Le Parallèle (V3) élimine tout moteur à la cheville.
```

**Conséquences concrètes de l'inertie :**
- **Marche** : Plus l'inertie est basse, plus la jambe balance vite → pas plus rapides, moins de couple requis aux hanches.
- **Course** : À >5 km/h, la fréquence de pas monte à ~3 Hz. Avec seulement 310g en bout de jambe (RS-00 Roll), l'inertie oscillante est déjà faible. Le V3 parallèle l'élimine quasi-totalement → la course devient **envisageable**.
- **Chutes** : Moins d'inertie = réactions de rattrapage plus rapides.

### 4.5 Recommandation Évolutive

| Phase | Config Cheville | Moteurs | Coût additionnel | Pourquoi |
| :--- | :--- | :--- | :---: | :--- |
| **V1** (prototype) | **A. Tirant K-Bot** + RS-00 Roll | RS-02 Pitch (tirant) + RS-00 Roll | $0 | Architecture K-Bot éprouvée, **suffisante pour marche V1** |
| **V2** (optimisation) | **C. Tirant RS-06** + RS-00 Roll | RS-02 → **RS-06** Pitch (tirant) | ~$70 (RS-06 - RS-02) | Couple Pitch ×2 (~72 N.m), **Sweet Spot** poids/couple |
| **V3** (performances) | **D. Parallèle** 2 bielles | 2× RS-06 (ou RS-03) + bielles | ~$33 bielles | Inertie ~0g, couple Roll par différentiel |

> [!TIP]
> **Progression V1 → V2** : Le **RS-06** (36 N.m) est l'upgrade parfait. Il double le couple du RS-02 (72 N.m effectif) pour seulement +75g, permettant la marche rapide et l'absorption des chocs. Le RS-03 (V3) est réservé aux usages extrêmes.
>
> **Progression V2 → V3** : Remplace le tirant + RS-00 par 2 bielles parallèles rotulées. Les 2 moteurs (RS-02 ou RS-03) en parallèle donnent Pitch + Roll par coordination/différentiel. Aucun moteur à la cheville = inertie minimale.

