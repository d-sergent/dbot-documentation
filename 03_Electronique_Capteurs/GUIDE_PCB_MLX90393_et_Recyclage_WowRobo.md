# 🔬 Guide Complet — Capteurs Tactiles MLX90393 : PCB Custom (JLCPCB) & Recyclage des PCBs WowRobo

*Document : GUIDE_PCB_MLX90393_et_Recyclage_WowRobo.md*  
*Créé : juin 2026 — Référence : GUIDE_COMPLET_Fabrication_et_Montage_DHand_V1.md §5.3*

---

## Table des Matières

1. [Contexte et Problème Initial](#1-contexte)
2. [Partie A — PCB Custom 10×10mm pour les Doigts (JLCPCB)](#2-pcb-custom)
   - [Circuit électrique minimal](#21-circuit)
   - [BOM — Liste de composants JLCPCB](#22-bom)
   - [Guide pas-à-pas EasyEDA](#23-easyeda)
   - [Fichier CPL (placement)](#24-cpl)
   - [Checklist DFM avant commande](#25-dfm)
3. [Partie B — Analyse : 1 ou 5 capteurs en paume ?](#3-analyse-paume)
4. [Partie C — IMU vs Capteurs Plantaires : la fausse alternative](#4-imu-vs-pied)
5. [Partie D — Plan complet de recyclage des 20 PCBs WowRobo](#5-recyclage)
6. [Architecture I2C globale du robot](#6-i2c-global)

---

## 1. Contexte et Problème Initial {#1-contexte}

Le PCB eFlesh WowRobo acheté (**20 × 20 mm** + 5×5mm languette connecteur) est un **Array 5-capteurs** (5× MLX90393 disposés en croix) conçu pour la paume. Il est physiquement impossible de le fixer sur une phalange distale de 12–15 mm de large.

**Inventaire matériel initial :**
- **20× PCBs WowRobo** (20×20mm, 5× MLX90393 chacun)
- **Aimants néodyme Ø3mm × 1mm** (quantité à préciser) — N48 ou N52

**Décision d'architecture :**

| Emplacement | Solution retenue | Justification |
|:---|:---|:---|
| Bouts de doigts (5/main) | **PCB custom 10×10mm JLCPCB** (1× MLX90393) | Seule solution < 12mm de large |
| Paume (1/main) | **1× PCB WowRobo** (5 capteurs) | Taille 20×20mm adaptée à la paume |
| Pieds (semelle) | **4× PCBs WowRobo** par pied | Surface 120×80mm suffisante |
| Avant-bras, torse | **PCBs WowRobo spare** | Détection contact/collision |

---

## 2. Partie A — PCB Custom 10×10mm pour les Doigts (JLCPCB) {#2-pcb-custom}

### 2.1 Circuit Électrique Minimal {#21-circuit}

Le MLX90393 en boîtier **QFN-16 (3×3mm)** ne nécessite que 5 composants externes pour fonctionner en mode I2C :

```
                        3.3V (VDD)
                           │
                   ┌───────┴────────────────────────────────────┐
                   │                                            │
                  [C1]                                         [C2]
               100nF/0402                                   10µF/0402
               (decoupl.)                                (bulk decoupl.)
                   │                                            │
                   └───────┬────────────────────────────────────┘
                           │
              ┌────────────┴────────────────────────────────────────┐
              │                                                      │
     VDD ─────┤ Pin 1 (VDD)          Pin 16 (VDDIO) ├───── 3.3V    │
              │                                                      │
  SCL ────[R1]┤ Pin 3 (SCL)           Pin 8 (GND)  ├───── GND      │
  (4.7kΩ)     │                                                      │
  SDA ────[R2]┤ Pin 4 (SDA)           Pin 7 (CS)   ├───── VDD      │  ← CS=HIGH → mode I2C
  (4.7kΩ)     │                                                      │
              │   MLX90393                                           │
  A0 ─────────┤ Pin 5 (A0)            Pin 6 (A1)   ├───── A1       │  ← adresse I2C
  (GND/VDD)   │                                                      │
              │           Pins 9-15 (GND)           │
              │           Pin 2 (INT) ─── NC         │  ← non connecté
              └──────────────────────────────────────┘

  R1, R2 : 4.7kΩ 0402 (pull-up I2C) — OMIS si l'ESP32-S3 a déjà des pull-ups sur le bus
  C1     : 100nF céramique 0402 (MLCC, X5R/X7R, 10V)
  C2     : 10µF céramique 0402 (MLCC, X5R, 10V)
  A0, A1 : soudés à GND ou VDD selon l'adresse souhaitée (voir table)
```

#### Table d'adresses I2C (MLX90393)

| A1 | A0 | Adresse 7-bit | Usage suggéré |
|:---:|:---:|:---:|:---|
| GND | GND | **0x0C** | Index |
| GND | VDD | **0x0D** | Majeur |
| VDD | GND | **0x0E** | Annulaire |
| VDD | VDD | **0x0F** | Auriculaire |

> **Note :** Le Pouce est sur le Bus I2C N°2 de l'ESP32-S3 à l'adresse 0x0C (pas de conflit d'adresses entre les deux bus).

#### Connexion de la broche CS

| Broche | Connexion | Raison |
|:---|:---|:---|
| **CS (Pin 7)** | Reliée à **VDD (3.3V)** | CS=HIGH → mode I2C activé. CS=LOW → mode SPI |
| **INT (Pin 2)** | Non connectée (NC) | Interruption optionnelle, non utilisée ici |
| **TRIG (Pin 14)** | Non connectée (NC) | Trigger externe, non utilisé |

---

### 2.2 BOM — Liste de Composants JLCPCB {#22-bom}

Fichier BOM compatible JLCPCB PCBA (format CSV) :

```csv
Comment,Designator,Footprint,LCSC Part #,Description,Quantity
"MLX90393SLW-ABA-011-RE",U1,"QFN-16_L3.0-W3.0-P0.50-BL","C2827654","MLX90393 3-Axis Magnetometer QFN16",1
"100nF 10V X7R 0402",C1,"C0402","C14663","100nF Decoupling Capacitor 0402",1
"10uF 10V X5R 0402",C2,"C0402","C15525","10uF Bulk Capacitor 0402",1
"4.7kΩ 1% 0402",R1,"R0402","C25900","4.7k Pull-up SDA 0402",1
"4.7kΩ 1% 0402",R2,"R0402","C25900","4.7k Pull-up SCL 0402",1
"JST SH 4-pin 1.0mm",J1,"JST-SH-4P-1.0MM","C160404","JST SH 4P I2C Connector 1.0mm",1
```

> [!WARNING]
> **Vérifiez les références LCSC** sur le site JLCPCB avant de commander : les stocks changent régulièrement. Cherchez `MLX90393` dans la bibliothèque JLCPCB et confirmez la disponibilité de la variante **MLX90393SLW-ABA-011-RE** (I2C/SPI, 3.3V, QFN-16).

> [!TIP]
> Si les résistances pull-up (R1, R2) sont déjà présentes sur la carte de développement ESP32-S3 que vous utilisez (ex: Seeed XIAO ESP32-S3), vous pouvez **supprimer R1 et R2 du BOM** pour réduire le coût et simplifier la conception. La plupart des ESP32-S3 ont des pull-ups internes ou des résistances externes sur leurs bus I2C.

---

### 2.3 Guide Pas-à-Pas EasyEDA {#23-easyeda}

**Prérequis :** Créez un compte gratuit sur [easyeda.com](https://easyeda.com) et sélectionnez **EasyEDA Standard Edition (v6)**.

#### Étape 1 : Créer un nouveau projet

1. Cliquez sur **File → New → Project**
2. Nommez le projet : `MLX90393_10x10_DBot_Finger`
3. Cliquez sur **File → New → Schematic** dans ce projet

#### Étape 2 : Placer le composant MLX90393

1. Appuyez sur `P` (Place component) ou cliquez sur **Place → Component**
2. Dans la barre de recherche, tapez : `MLX90393`
3. Sélectionnez `MLX90393SLW-ABA-011-RE` (LCSC: C2827654)
4. Cliquez pour placer le composant au centre de la feuille

#### Étape 3 : Placer les condensateurs et résistances

1. Placez **C1** : recherchez `100nF 0402`, référence C14663
2. Placez **C2** : recherchez `10uF 0402`, référence C15525
3. Placez **R1** : recherchez `4.7k 0402`, référence C25900
4. Placez **R2** : idem R1
5. Placez **J1** : recherchez `JST SH 4P 1.0mm`, référence C160404

#### Étape 4 : Câbler le schéma

Connectez les fils selon le schéma de la section 2.1 :
1. Appuyez sur `W` pour tracer un fil
2. Reliez VDD → C1 → C2 → Pin VDD et VDDIO du MLX90393
3. Reliez GND → côté négatif C1 et C2 → Pins GND (8, 9–15) du MLX90393
4. Reliez CS (Pin 7) → VDD
5. Reliez SDA (Pin 4) → R2 → connecteur J1 broche 2, et fil → nœud SDA
6. Reliez SCL (Pin 3) → R1 → connecteur J1 broche 3, et fil → nœud SCL
7. Ajoutez des **Power Flags** (Place → Power Port) pour VDD et GND
8. Câblez A0 et A1 à GND (adresse 0x0C) ou à VDD selon le doigt

#### Étape 5 : Passer au PCB Layout

1. Cliquez sur **Design → Convert Schematic to PCB**
2. Une nouvelle fenêtre s'ouvre avec les composants non placés
3. **Définissez les dimensions du PCB :**
   - Cliquez sur **Board Outline** (contour)
   - Tracez un rectangle de **10mm × 10mm**
   - Dans les propriétés, réglez Thickness à **0.8mm** (plus léger, plus fin)

#### Étape 6 : Placer les composants sur le PCB

Ordre de placement recommandé :
1. **U1 (MLX90393)** → au centre exact du PCB (coordonnées X=5, Y=5)
2. **C1 (100nF)** → à 1mm au-dessus du pin VDD de U1 (côté Top)
3. **C2 (10µF)** → à 1mm à droite de C1
4. **R1, R2** → sur le bord gauche du PCB (si inclus)
5. **J1 (connecteur JST)** → sur le bord droit ou bas du PCB, **en dehors** des 10mm si possible (le connecteur peut dépasser légèrement)

#### Étape 7 : Tracer les pistes (Routing)

Largeurs de piste recommandées :
- **Pistes signal (SDA, SCL, A0, A1)** : **0.2mm** (minimum DRC JLCPCB)
- **Pistes alimentation (VDD, GND)** : **0.4mm**
- **Plan de masse (GND Polygon)** : créez un remplissage cuivre GND sur la couche Bottom (`Place → Copper Area`, sélectionnez GND)

Règle critique :
> Placez C1 et C2 aussi proches que possible du pin VDD de U1. La distance idéale est **< 1mm**. Cela réduit l'inductance parasite et filtre efficacement le bruit haute fréquence.

#### Étape 8 : Vérification DRC

1. Cliquez sur **Design → Design Rule Check (DRC)**
2. Réglez les règles minimales JLCPCB :
   - Min Clearance : **0.127mm**
   - Min Track Width : **0.127mm**
   - Min Via Size : **0.4mm** (pad) / **0.2mm** (drill)
3. Corrigez toutes les erreurs avant de continuer

#### Étape 9 : Export des fichiers

1. **Gerbers** : `Fabrication → Generate Gerber` → téléchargez le ZIP
2. **BOM** : `Fabrication → BOM` → exportez en CSV
3. **CPL** (positions) : `Fabrication → Pick and Place` → exportez en CSV

---

### 2.4 Fichier CPL (Placement des Composants) {#24-cpl}

Exemple de CPL à vérifier/ajuster après placement dans EasyEDA :

```csv
Designator,Mid X,Mid Y,Layer,Rotation
U1,5.00,5.00,Top,0
C1,5.00,6.80,Top,90
C2,6.80,6.80,Top,90
R1,1.00,5.00,Top,0
R2,1.00,4.00,Top,0
J1,9.50,5.00,Top,270
```

> Ces coordonnées sont des exemples. Les valeurs réelles dépendent de votre placement dans EasyEDA. Vérifiez toujours que l'orientation de chaque composant correspond à la rotation 3D affichée par JLCPCB lors de l'upload.

---

### 2.5 Checklist DFM Avant Commande {#25-dfm}

Avant de soumettre votre commande sur JLCPCB, vérifiez ces points :

#### Dimensions et couches
- [ ] Taille du PCB : **10mm × 10mm** exactement
- [ ] Épaisseur : **0.8mm** (sélectionner dans les options JLCPCB)
- [ ] Nombre de couches : **2** (Top + Bottom)
- [ ] Couleur du masque de soudure : **Noir** (recommandé pour discrétion)

#### Règles de fabrication
- [ ] Toutes les pistes ≥ **0.127mm** de large
- [ ] Tous les espaces (clearance) ≥ **0.127mm**
- [ ] Vias : diamètre de perçage ≥ **0.2mm**, pad ≥ **0.4mm**
- [ ] Distance bord de piste / bord de PCB ≥ **0.3mm**
- [ ] Aucune piste ne passe sous le pad thermique central du QFN-16

#### Composants (Assembly PCBA)
- [ ] Le MLX90393 est en stock chez JLCPCB (vérifier sur le site)
- [ ] L'orientation du composant U1 dans le CPL correspond à la sérigraphie
- [ ] Les condensateurs C1 et C2 sont à ≤ 1mm du pin VDD de U1
- [ ] Le connecteur JST J1 est accessible et non masqué par d'autres composants

#### Connexions électriques
- [ ] CS (Pin 7) est bien connecté à **VDD** (et non à GND)
- [ ] VDDIO (Pin 16) est connecté à **VDD** (3.3V)
- [ ] Tous les pins GND (8, 9–15) sont connectés au plan de masse
- [ ] INT (Pin 2) est laissé **non connecté** (NC) — ne pas le relier à GND
- [ ] A0 et A1 sont câblés selon l'adresse voulue (voir tableau §2.1)

#### Après réception des PCBs
- [ ] Tester la continuité VDD–GND avec un multimètre (doit être **ouvert**)
- [ ] Scanner le bus I2C avec `i2cdetect` — le MLX90393 doit répondre à l'adresse configurée
- [ ] Lire un registre de status (commande `0x40`) — le bit ERROR (bit 4) doit être à 0

---

## 3. Partie B — Analyse : 1 ou 5 Capteurs en Paume ? {#3-analyse-paume}

### Question posée

> *Le PCB WowRobo comporte 5 capteurs MLX90393 disposés en croix. Avec des aimants de Ø3mm×1mm, est-il judicieux d'utiliser tous les 5 capteurs pour la paume, ou un seul suffirait-il ?*

### Analyse technique

#### Ce que permettent 5 capteurs vs 1 capteur sur la paume

| Capacité | 1 capteur central | 5 capteurs (croix) |
|:---|:---:|:---:|
| Détection pression normale (Z) | ✅ | ✅✅✅ |
| Détection cisaillement (X, Y) | ✅ | ✅✅✅ |
| **Localisation du point de contact** | ❌ | ✅ |
| **Carte de pression (distribution)** | ❌ | ✅ partielle |
| **Détection orientation de l'objet** | ❌ | ✅ |
| **Détection glissement directionnel** | ✅ limité | ✅✅ |

#### Le problème spécifique des aimants Ø3×1mm sur la paume

La paume a une surface de contact utile d'environ **60×80mm**. Chaque capteur MLX90393 ne "voit" qu'un aimant placé dans un rayon de **3–5mm** au-dessus de lui. Avec des aimants de Ø3mm×1mm :

```
   Zone de sensibilité d'un capteur MLX90393 avec aimant Ø3×1mm :
   
   ┌─────────────────────────────────────────┐
   │                                         │
   │   Rayon de sensibilité : ~3 à 5 mm     │
   │   Résolution spatiale : ~6 à 10 mm²    │
   │                                         │
   │   Pour couvrir la paume (60×80mm),     │
   │   il faudrait environ 40 à 100 capteurs │
   │                                         │
   │   5 capteurs → couvrent ~5% de la      │
   │   surface palmaire totale               │
   └─────────────────────────────────────────┘
```

#### Verdict sur la paume multi-capteurs

> [!IMPORTANT]
> **Conclusion : OUI, il est judicieux d'utiliser les 5 capteurs du PCB WowRobo pour la paume — mais avec une configuration adaptée.**

**Pourquoi 5 capteurs apportent une vraie valeur :**

1. **Localisation du contact :** Avec 5 magnétomètres en croix (centre + 4 cardinaux à ~8mm d'écart), le logiciel peut interpoler la **position centroïde** d'un objet en contact avec la paume, même si l'objet est plus grand que la zone de détection d'un seul capteur.

2. **Détection d'orientation :** Un objet posé en biais sur la paume active plusieurs capteurs différentiellement. L'analyse des vecteurs Bx/By de chaque capteur permet de calculer l'**angle d'incidence** de l'objet — essentiel pour un ajustement de préhension.

3. **Redondance et robustesse :** Si un capteur tombe en panne, les 4 autres continuent à fonctionner.

**La vraie limitation : couverture surfacique insuffisante**

Avec des aimants de Ø3mm, la **plage de détection n'est pas uniforme sur toute la paume**. Les zones sans aimant (en dehors des 5 positions) ne seront pas détectées. C'est une limitation réelle mais acceptable pour une V1.

**Recommandation adaptée :**

| Configuration | Aimants | Couverture | Qualité de mesure |
|:---|:---|:---|:---|
| **Option A — Usage direct** (recommandé V1) | 5 aimants Ø3×1mm noyés dans le TPU en face de chaque capteur | ~5% de la paume | ✅ Suffisant pour la détection de contact palmar grossier |
| **Option B — Aimants plus grands** | 5 aimants Ø6×2mm à la place de Ø3×1mm | ~15% de la paume | ✅✅ Meilleure sensibilité, champ plus étendu |
| **Option C — PCB + TPU étendu** (recommandé V2) | PCB WowRobo + couche TPU gyroïde sur toute la paume (60×80mm) avec matrice de petits aimants | ~60% de la paume | ✅✅✅ Approche vraie "peau tactile" |

> [!TIP]
> **Pour la V1** : Utilisez les aimants Ø3×1mm que vous avez déjà. La mesure ne sera pas "carte de pression complète" mais sera suffisante pour détecter si un objet est bien tenu, et dans quelle direction il exerce une force. C'est la même approche que celle du Pinto Lab (NYU) dans les publications originales d'eFlesh.

---

## 4. Partie C — IMU vs Capteurs Plantaires : La Fausse Alternative {#4-imu-vs-pied}

### Question posée

> *Si le robot dispose déjà d'un IMU pour l'équilibre, les capteurs plantaires (PCBs WowRobo dans les semelles) apportent-ils encore de la valeur ?*

### Réponse directe

> [!IMPORTANT]
> **OUI, les capteurs plantaires sont indispensables même avec un IMU. L'IMU et les capteurs plantaires ne font PAS la même chose — ils sont complémentaires et irremplaçables l'un par l'autre.**

### Explication : Ce que mesure chaque capteur

| Capteur | Ce qu'il mesure | Ce qu'il NE mesure PAS |
|:---|:---|:---|
| **IMU** | Orientation et accélération du **corps** (torse) | Ce qui se passe sous les pieds |
| **Capteurs plantaires** | Forces au point de **contact sol** | L'orientation globale du corps |

### L'analogie parfaite : l'oreille interne vs les pieds

Imaginez un homme debout les yeux fermés :
- Son **oreille interne** (= IMU) lui dit qu'il penche légèrement à gauche
- Ses **pieds** (= capteurs plantaires) lui disent que tout le poids est sur l'avant du pied droit

**Avec seulement l'oreille interne**, il sait qu'il penche mais ne sait pas **où** il doit appliquer la correction — sur quelle cheville, dans quelle direction du pied.

**Avec les deux**, le cerveau sait exactement : "je penche à gauche, le CoP est sur l'avant-droit, je dois contracter la cheville droite-talon et relâcher la gauche-avant".

### Limitations critiques de l'IMU seul

#### 1. Dérive gyroscopique (IMU drift)

Un gyroscope drift d'environ **1 à 5°/heure** en conditions normales. Sur un sol irrégulier avec des vibrations de moteurs, cette dérive peut atteindre **5 à 15°/heure**. Pour un robot bipède en marche continue :

- Après **10 minutes de marche** → erreur d'attitude de **0.8 à 2.5°**
- À 40kg de masse corporelle, une erreur de **1.5°** se traduit par un **moment déstabilisant de ~10 N·m** sur la hanche

Les capteurs plantaires fournissent une **référence absolue au sol** (le CoP calculé ne drift pas) qui permet de corriger cette dérive.

#### 2. Terrain non-plat et obstacles sous le pied

L'IMU mesure l'orientation du **torse**, pas de la semelle. Sur un sol incliné de 5° ou avec un caillou sous le talon :
- L'IMU voit le torse pencher — mais ne sait pas si c'est normal (montée de marche) ou anormal (chute imminente)
- Le capteur plantaire voit immédiatement que le **talon est sur-chargé** ou que le **CoP est hors de la zone de stabilité** → déclenchement d'un réflexe de cheville

#### 3. Phase d'envol (swing phase)

Pendant la phase d'envol d'une jambe (le pied n'est pas au sol) :
- L'IMU continue de mesurer l'accélération, mais la **jambe volante perturbe la mesure** (son inertie s'additionne au torse)
- Le capteur plantaire de la **jambe d'appui** confirme que 100% du poids est sur ce pied → le contrôleur peut donc calculer précisément le point de pivot

#### 4. Détection de glissement

Un glissement de semelle (chute de μ sur carrelage mouillé) n'est **pas détectable par un IMU** avant que le centre de masse ne commence à chuter (délai de 200–500ms). Les capteurs plantaires détectent le glissement en **< 10ms** via le changement du vecteur de cisaillement horizontal (Bx, By).

### Ce que les capteurs plantaires apportent concrètement

| Apport | Sans capteurs plantaires (IMU seul) | Avec capteurs plantaires |
|:---|:---|:---|
| **Centre de Pression (CoP)** | Estimé par modèle dynamique (imprécis) | Mesuré directement (précis à ±5mm) |
| **ZMP (Zero Moment Point)** | Calculé par simulation | Validé par mesure réelle |
| **Détection glissement** | Après 200–500ms (chute déjà amorcée) | En **< 10ms** (réflexe préventif) |
| **Terrain irrégulier** | Compensation uniquement par modèle | Adaptation terrain réelle |
| **Phase de contact** | Estimée (pas toujours fiable) | Mesurée exactement |
| **Corrections IMU drift** | Non disponible | Recalibration absolue au sol |

### Verdict final

> [!NOTE]
> **L'IMU est le "système vestibulaire" du robot (équilibre global, orientation dans l'espace).**
> **Les capteurs plantaires sont les "récepteurs proprioceptifs plantaires" (ce qui se passe exactement sous chaque pied).**
> 
> Tous les robots bipèdes de référence — Boston Dynamics Atlas, Agility Robotics Digit, Unitree H1, Figure 01 — utilisent **les deux types de capteurs simultanément**. Il n'existe pas de robot bipède performant qui utilise un IMU sans retour de force au sol.

**Conséquence pratique pour le D-Bot :** Les 8 PCBs WowRobo prévus pour les semelles (4 par pied) apportent une valeur **critique et non substituable** par l'IMU.

---

## 5. Partie D — Plan Complet de Recyclage des 20 PCBs WowRobo {#5-recyclage}

### 5.1 Vue d'Ensemble

**Stock disponible : 20 PCBs WowRobo** (20×20mm, 5× MLX90393 chacun)

#### Répartition finale recommandée

| # | Emplacement | PCBs | MLX90393 | Aimants Ø3×1mm | Priorité |
|:---|:---|:---:|:---:|:---:|:---:|
| 1 | Paume Main Droite | 1 | 5 | 5 | 🥈 |
| 2 | Paume Main Gauche | 1 | 5 | 5 | 🥈 |
| 3 | Semelle Pied Droit | 4 | 20 | 20 | 🥇 |
| 4 | Semelle Pied Gauche | 4 | 20 | 20 | 🥇 |
| 5 | Avant-bras Droit | 1 | 5 | 5 | 🥉 |
| 6 | Avant-bras Gauche | 1 | 5 | 5 | 🥉 |
| 7 | Poitrine/Torse | 2 | 10 | 10 | 4 |
| **Spare/Réserve** | — | **6** | 30 | — | — |
| **TOTAL** | | **20** | **100** | **70** | |

> [!WARNING]
> **Aimants nécessaires :** 70 aimants Ø3×1mm au total. Vérifiez votre stock et commandez le complément si nécessaire. Référence Supermagnete (France) : **S-03-01-N** (aimant néodyme N48, Ø3×1mm, ~0.17€/pièce). Lien : [supermagnete.fr](https://www.supermagnete.fr/aimants-ronds-neodyme/aimant-rond-s-03-01-n_S-03-01-N)

---

### 5.2 Priorité 1 — Semelle Plantaire Tactile (8 PCBs, 2 pieds)

#### Architecture de la semelle

La plaque plantaire en carbone mesure **120 × 80 mm** — suffisant pour 4 PCBs de 20×20mm.

```
         ┌─────────────────────────────────────────────┐
         │           PLAQUE CARBONE 120×80mm           │
         │                        (vue de dessous)     │
         │                                              │
         │   ┌─────────┐              ┌─────────┐      │
         │   │ PCB #3  │              │ PCB #4  │      │
         │   │ Métatarse│             │ Métatarse│     │  ← AVANT-PIED
         │   │ Médial  │              │ Latéral │      │
         │   │ (Ø gros │              │ (Ø petit│      │
         │   │  orteil)│              │  orteil)│      │
         │   └─────────┘              └─────────┘      │
         │                                              │
         │             ┌────────────┐                  │
         │             │  PCB #2    │                  │
         │             │ Voûte      │                  │  ← MILIEU
         │             │ plantaire  │                  │
         │             └────────────┘                  │
         │                                              │
         │             ┌────────────┐                  │
         │             │  PCB #1    │                  │
         │             │  Talon     │                  │  ← ARRIÈRE
         │             │ (Calcanéum)│                  │
         │             └────────────┘                  │
         │                                              │
         └─────────────────────────────────────────────┘
              Avant-pied ↑                ↑ Talon
```

#### Coupe transversale de la semelle tactile

```
Surface de contact (sol)
        ↕
┌───────────────────────────────────────────┐ ← Pads TPU (Shore 95A/85A)
│  TPU gyroïde 8%  +  20× aimants Ø3×1mm  │   5–8mm d'épaisseur
│  (noyés dans le TPU en face des capteurs)│
├───────────────────────────────────────────┤
│         Air-gap : 3–4 mm                 │   (espace libre / mousse souple)
├───────────────────────────────────────────┤
│  4× PCBs WowRobo collés sur le carbone   │   face capteurs vers le haut
│  (MLX90393 regardent vers le haut)       │
├───────────────────────────────────────────┤
│  Plaque carbone 3mm (ossature plantaire)  │
└───────────────────────────────────────────┘
        ↕
Sole extérieure (contact direct avec le sol) — optionnellement protégée par un pad antidérapant
```

#### Informations de fabrication semelle

| Élément | Spécification |
|:---|:---|
| **Aimants dans TPU** | 20× Ø3×1mm, 1 par capteur, face aimantée Nord vers le bas (vers le capteur) |
| **Hauteur totale ajoutée** | 5mm (TPU) + 4mm (air-gap) + 1.6mm (PCB) + 3mm (carbone) = **13.6mm** total semelle |
| **Masse ajoutée par pied** | ~8g (PCBs) + ~1g (aimants) + ~15g (TPU étendu) + ~5g (câbles) = **~29g/pied** |
| **Câblage** | 4 câbles I2C JST-SH 4 broches (1.0mm) par pied, longueur 200–300mm, remontent dans le tibia |
| **ESP32-S3 pied** | Fixé dans le bas du tibia (boîtier imprimé PA12-CF), 1 par pied |

#### Adressage I2C des 4 PCBs par pied

Chaque PCB WowRobo a déjà ses 5 MLX90393 avec des adresses I2C fixes configurées en usine (0x0C, 0x0D, 0x0E, 0x0F, 0x18 selon le modèle). Utilisez **2 bus I2C** de l'ESP32-S3 :

```
          ESP32-S3 Pied (dans le tibia)
          ┌──────────────────────────────┐
          │   Bus I2C #1 (GPIO 1/2)      │──── PCB#1 (Talon) + PCB#2 (Voûte)
          │   Bus I2C #2 (GPIO 5/6)      │──── PCB#3 (Méta Médial) + PCB#4 (Méta Latéral)
          └──────────────────────────────┘
```

> Note : Si les adresses des capteurs d'un même PCB WowRobo entrent en conflit avec ceux d'un autre PCB sur le même bus, utilisez un **multiplexeur TCA9548A** (8 canaux I2C, boîtier TSSOP-24, disponible chez JLCPCB). Une alternative simple est d'utiliser les **4 bus I2C logiciels** de l'ESP32-S3 via `Wire` et `Wire1`.

---

### 5.3 Priorité 2 — Paumes des Mains (2 PCBs)

*Référence : GUIDE_COMPLET_Fabrication_et_Montage_DHand_V1.md §5.3*

Usage prévu par eFlesh (Pinto Lab, NYU). Le PCB s'intègre dans l'évidement de 20×20mm du bloc de paume PA12-CF.

Configuration des aimants (1 par capteur) :
- Aimants Ø3×1mm noyés dans la gaine TPU de la paume
- Air-gap nominal : 3–4mm
- Les 5 aimants sont disposés en miroir des 5 capteurs (croix : centre + 4 cardinaux)

Valeur apportée : détection de contact palmar, force et cisaillement, détection d'orientation de l'objet saisi.

---

### 5.4 Priorité 3 — Avant-bras (2 PCBs)

**Fonction : Sécurité HRI (Human-Robot Interaction) et détection de collision**

Intégration :
- Collé sous la coque avant-bras en PA12-CF ou TPU
- 5 aimants Ø3×1mm noyés dans un pad TPU de 5mm d'épaisseur sur l'avant de l'avant-bras
- Câble I2C remonte vers le bus ESP32-S3 du bras

Usage typique :
- Le robot "sent" un contact humain volontaire → comportement coopératif
- Collision non voulue avec un obstacle → réflexe de retrait
- Enrichissement du dataset RL pour l'apprentissage de la manipulation

---

### 5.5 Priorité 4 — Torse / Poitrine (2 PCBs)

**Fonction : Détection de collision frontale et interaction physique**

Intégration :
- Intégrés sous la plaque thoracique (PA12-CF ou composite carbone)
- Pad TPU souple de 8mm (Shore 85A) sur la poitrine
- Câble I2C vers le hub central (Jetson ou ESP32-S3 dédié torse)

Usage :
- Protection des composants internes (batterie, CPU) lors des chutes
- Détection d'appui volontaire (l'humain pose la main sur le torse pour guider le robot)
- Données de contact pour l'apprentissage de comportements sociaux

---

## 6. Architecture I2C Globale du Robot {#6-i2c-global}

### Topologie complète des capteurs tactiles MLX90393

```
                              ┌──────────────────────┐
                              │      JETSON (USB CDC) │
                              └───────────────────────┘
                                        │ USB
              ┌─────────────────────────┴──────────────────────────┐
              │                                                      │
    ┌─────────┴──────┐                                   ┌──────────┴──────┐
    │ ESP32-S3       │                                   │ ESP32-S3        │
    │ MAIN DROITE    │                                   │ MAIN GAUCHE     │
    │ (Bus I²C ×2)   │                                   │ (Bus I²C ×2)   │
    │                │                                   │                 │
    │ Bus1: 4 doigts │                                   │ Bus1: 4 doigts  │
    │ Bus2: pouce    │                                   │ Bus2: pouce     │
    │        + paume │                                   │        + paume  │
    └────────────────┘                                   └─────────────────┘
              │                                                      │
    ┌─────────┴──────┐                                   ┌──────────┴──────┐
    │ ESP32-S3       │                                   │ ESP32-S3        │
    │ PIED DROIT     │                                   │ PIED GAUCHE     │
    │ (dans tibia D) │                                   │ (dans tibia G)  │
    │                │                                   │                 │
    │ Bus1: Talon    │                                   │ Bus1: Talon     │
    │      + Voûte   │                                   │      + Voûte    │
    │ Bus2: Méta Med │                                   │ Bus2: Méta Med  │
    │      + Méta Lat│                                   │      + Méta Lat │
    └────────────────┘                                   └─────────────────┘
              │ USB                                                │ USB
              └───────────────────┬────────────────────────────────┘
                                  │
                         ┌────────┴────────┐
                         │  ESP32-S3 TORSE │
                         │  Avant-bras D/G │
                         │  + Poitrine     │
                         └─────────────────┘
                                  │ USB
                              JETSON
```

### Bilan global des capteurs MLX90393 sur le robot

| Sous-système | PCBs WowRobo | PCBs custom 10×10mm | MLX90393 total |
|:---|:---:|:---:|:---:|
| Doigts mains (5+5) | 0 | **10** | 10 |
| Paumes (×2) | 2 | 0 | 10 |
| Pieds semelles (×2) | 8 | 0 | 40 |
| Avant-bras (×2) | 2 | 0 | 10 |
| Torse | 2 | 0 | 10 |
| **TOTAL** | **14** | **10** | **80** |

### Ressources logicielles

- **Firmware ESP32-S3** : Dépôt eFlesh `/arduino` — compatible multi-bus, multi-capteurs
- **Driver MLX90393** : [Adafruit_MLX90393](https://github.com/adafruit/Adafruit_MLX90393)
- **Fréquence d'acquisition** : 100 Hz par bus I2C (configuration ODR du MLX90393)
- **Protocole** : USB CDC → Jetson → ROS2 topic `/tactile/[location]/[sensor_id]`

---

*Document généré juin 2026 — À mettre à jour après réception et test des PCBs JLCPCB.*  
*Références : GUIDE_COMPLET_Fabrication_et_Montage_DHand_V1.md §5.3 | FINAL_CONSOLIDE_Jambes_et_Pieds.md §3*
