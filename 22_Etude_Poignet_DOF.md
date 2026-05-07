# 22 — Étude : Poignet D-Bot — DOF, Encombrement & Recommandation

> **Contexte** : Ce document consolide l'analyse comparative des DOF de poignet (réalisée en Mai 2026) et l'étude d'intégration mécanique d'un RS-00 Pitch supplémentaire dans l'avant-bras. Il aboutit à une **recommandation définitive** pour la V1 du D-Bot.

---

## Partie 1 — Analyse Comparative (DOF Poignet dans l'industrie)

### 1.1 État des lieux : D-Bot V1 vs Concurrents

| Robot | DOF Poignet | Axes | Moteurs Poignet | Statut |
| :--- | :---: | :--- | :--- | :--- |
| **D-Bot V1** | **1** | Roll uniquement (RS-00) | 1× RS-00 (14 N.m, 310g) | ✅ En production |
| **OpenArm** | **3** | Roll + Pitch + Yaw | 3× DM-J4310 (7 N.m pic) | Open-source |
| **Tesla Optimus Gen3** | **2** | Pitch + Yaw *(le Roll est assuré par l'avant-bras)* | 2 moteurs dédiés (brevets Oct. 2024) | Production |
| **Unitree G1 Standard** | **0** | Aucun (bras 5-DOF) | — | Limité |
| **Unitree G1-EDU** | **2** | Pitch (±92.5°) + Yaw (±92.5°) | 2 moteurs optionnels | Option payante |
| **Main humaine** | **3** | Roll + Pitch + Yaw | — | Référence |

### 1.2 Classification des 3 axes par importance

Extrait de **[25_Compatibilite_IA_Isaac_Gym.md](../25_Compatibilite_IA_Isaac_Gym.md)** :

| Axe | Action | Statut IA | D-Bot V1 |
| :--- | :--- | :---: | :---: |
| **Wrist Roll (Z)** | Tourner une poignée de porte | 🟢 **Obligatoire** | ✅ RS-00 |
| **Wrist Pitch (Y)** | Casser le poignet bas/haut | 🟡 **Recommandé** | ❌ |
| **Wrist Yaw (X)** | Saluer de la main | 🔴 Optionnel | ❌ |

> [!IMPORTANT]
> Le **Wrist Pitch** est classé "Recommandé" (non Optionnel) par votre propre étude IA. Et la conclusion du document 25 précise : *"Il ne lui manque que 3 DOFs d'ingénierie fine (le Waist Yaw et les Poignets Pitch) pour atteindre les capacités cinématiques exactes d'un Tesla Optimus."*

> [!NOTE]
> **Clarification Tesla Optimus** : D'après les brevets d'Octobre 2024, le poignet Optimus dispose exactement de **2 DOF : Pitch + Yaw**. Le Roll (torsion) n'est pas un axe dédié au poignet — il est assuré en amont par la **Supination/Pronation de l'avant-bras** (Elbow Yaw). Tesla a donc une architecture Coude Yaw + Poignet Pitch + Poignet Yaw, soit 3 axes répartis différemment des nôtres. Notre RS-00 Roll au poignet couvre fonctionnellement ce que Tesla réalise avec son Coude Yaw.

### 1.3 Tâches impossibles sans Wrist Pitch

| Tâche | Avec Roll seul | Avec Roll + Pitch |
| :--- | :---: | :---: |
| Tourner une poignée de porte | ✅ | ✅ |
| Verser de l'eau depuis une bouteille | ✅ | ✅ |
| **Ramasser un objet au sol (bras tendu)** | ⚠️ Posture compensée | ✅ Naturel |
| **Poser un objet sur une étagère haute** | ⚠️ Posture compensée | ✅ Naturel |
| **Taper sur un clavier / presser un bouton** | ⚠️ Imprécis | ✅ Précis |
| Compatibilité policies RL (PANDA, ALOHA) | ❌ Incompatible | 🟡 Adaptable |

---

## Partie 2 — Étude d'Intégration Mécanique dans l'Avant-Bras

### 2.1 Spécifications exactes du RS-00

Sources croisées (RAG interne + documentation RobStride officielle) :

| Paramètre | Valeur |
| :--- | :--- |
| **Diamètre externe** | Ø50 mm |
| **Hauteur (longueur axiale)** | **57 mm** |
| **Poids** | **310 g** |
| **Couple pic** | 14 N.m |
| **Couple nominal** | 5 N.m |
| **Rapport de réduction** | 10:1 |
| **Vitesse à vide** | 315 RPM |
| **Bus** | CAN 1 Mbps |
| **Tension** | 48 VDC |

> ✅ **Bonne nouvelle** : Le RS-00 a un diamètre de **Ø50 mm**, ce qui rentre dans un avant-bras de Ø80 mm avec 15 mm de paroi de chaque côté.

### 2.2 Budget spatial actuel de l'avant-bras

D'après **[21_Etude_Main_Robotique.md](../21_Etude_Main_Robotique.md)** (section 3.2) :

```
VUE LONGITUDINALE ACTUELLE — AVANT-BRAS (22 cm total)

  COUDE (RS-06)                                     POIGNET (RS-00 Roll)
  ←───────────────────────── 220 mm ──────────────────────────→
  │                                                            │
  │  ┌────────────────┐  ┌──────────┐  ┌──────────────────┐  │
  │  │  4× XC430      │  │ 4× XC330 │  │   Espace libre   │  │
  │  │  (2×2 empilés) │  │ (2×2)    │  │   Buck 48V→12V   │  │
  │  │  93mm long     │  │ 52mm     │  │   U2D2 Controller│  │
  │  └────────────────┘  └──────────┘  └──────────────────┘  │
  │  ←    93 mm     →    ← 52 mm →     ←      75 mm       →  │
                                                     ↑
                                           C'est ici qu'on cherche
                                           à loger le RS-00 Pitch
```

**Bilan actuel** : 93 + 52 = **145 mm occupés**, **75 mm libres** pour l'électronique.

### 2.3 Le RS-00 Pitch tient-il dans les 75 mm ?

Le RS-00 mesure **57 mm de hauteur axiale**. Si on le positionne dans la zone électronique de 75 mm :

```
VUE LONGITUDINALE PROPOSÉE — AVANT-BRAS (22 cm total)

  COUDE (RS-06)                                        POIGNET
  ←───────────────────────── 220 mm ────────────────────────→
  │                                                          │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
  │  │ 4× XC430 │  │ 4× XC330 │  │ RS-00    │  │ Élec.  │  │
  │  │ 93mm     │  │ 52mm     │  │ PITCH    │  │ ~18mm  │  │
  │  │          │  │          │  │ 57mm     │  │(compact│  │
  │  └──────────┘  └──────────┘  └──────────┘  └────────┘  │
  │  ← 93mm →      ← 52mm →      ← 57mm →      ← 18mm →   │
                                                     ↑
                                            ⚠️ Zone électronique
                                            compressée à 18 mm
```

> [!WARNING]
> **93 + 52 + 57 = 202 mm** sur 220 mm disponibles → il ne reste que **18 mm** pour l'électronique. C'est **très serré** mais pas impossible selon l'architecture électronique choisie.

### 2.4 Hypothèse retenue : U2D2 Power Hub déporté vers le torse ou l'épaule

> [!IMPORTANT]
> **Décision d'architecture préalable** : Le U2D2 Power Hub (contrôleur Dynamixel, 40×18×16mm) et le câblage associé seront positionnés soit dans le **torse**, soit dans la partie **humerus entre l'épaule et le coude**. Seul le **Buck converter 48V→12V** reste dans l'avant-bras. Cette décision est indépendante du nombre de DOF choisi et libère **~35 mm** dans l'avant-bras dès la V1.

Avec cette hypothèse, le budget spatial réel de l'avant-bras pour l'électronique n'est plus 75 mm mais :
```
  75mm (total libre) - 57mm (RS-00 Pitch) = 18mm restants pour l'électronique
  → Avec U2D2 déporté : seul le Buck compact reste (~15×27mm)
  → 18mm est suffisant pour un Buck ultra-compact (ex: Pololu D24V90F12 : 15mm de long)
```

Cela **ouvre de nouvelles options** que le tableau initial ne montrait pas :

| Option | DOF | Avant-bras | Espace électro | Commentaire |
| :--- | :---: | :---: | :---: | :--- |
| **A. Statu quo** | 1 (Roll) | 220mm | 75mm | Fonctionnel, limité IA |
| **B. +Pitch seul** | 2 (Roll+Pitch) | 220mm | ~18mm (Buck compact) | ✅ **Faisable** avec U2D2 déporté |
| **C. +Pitch + allongement** | 2 (Roll+Pitch) | 240mm | ~38mm | ✅ Plus confortable |
| **D. +Pitch+Yaw (3 DOF)** | 3 (Roll+Pitch+Yaw) | 220mm* | ~18mm pour 2 RS-00 en série | ⚠️ Très serré, défi esthétique (voir §2.6) |
| **E. +Pitch+Yaw + allongement** | 3 (Roll+Pitch+Yaw) | 240mm | ~38mm | 🟡 Faisable mais défi esthétique |

*220mm sans allongement en option D : 93+52+57(Pitch)+57(Yaw) = 259mm > 220mm → **impossible sans allonger significativement** (au moins +40mm)*

> [!WARNING]
> L'Option D (3 DOF sans allongement) est **mathématiquement impossible** : 2 RS-00 en série = 114mm, plus les 145mm des servos doigts = 259mm > 220mm. Il faudrait impérativement allonger à au moins 260mm pour 3 DOF en série classique.

### 2.5 Impact sur le routage des tendons Dyneema

C'est le **vrai défi technique** de l'ajout du Wrist Pitch. Les 8 tendons Dyneema doivent maintenant traverser **2 articulations motorisées** (Roll + Pitch) avant d'atteindre les doigts :

```
TRAJET TENDON (avant modification) :
  XC430/XC330 → Poulie → Gaine PTFE → [RS-00 Roll] → Main → Doigt

TRAJET TENDON (après modification) :
  XC430/XC330 → Poulie → Gaine PTFE → [RS-00 Pitch] → [RS-00 Roll] → Main → Doigt
                                            ↑
                               Boucle de service nécessaire :
                               longueur de gaine supplémentaire ≈ 80-100mm
                               (rayon de courbure min. gaine PTFE ~30mm)
```

**Impact sur la longueur totale des gaines** : +80 à +100 mm par tendon. Gérable avec des gaines PTFE flexibles Ø1.5mm, à condition de prévoir les boucles de service au niveau du Pitch.

---

## Partie 2bis — Défi Esthétique du Poignet 3-DOF

### 2.6 Le problème de compacité et d'esthétique humanoïde

Empiler 3 moteurs RS-00 en série (Roll → Pitch → Yaw) crée une "colonne vertébrale" de **171 mm** (3 × 57mm) à l'extrémité distale du bras — soit une zone tubulaire presque aussi longue que l'avant-bras lui-même. C'est fonctionnel, mais **visuellement éloigné d'un poignet humanoïde naturel**.

```
  Vue de côté — Poignet 3-DOF en série (approche naïve)

  AVANT-BRAS ─────→  [RS-00 Roll] ─→ [RS-00 Pitch] ─→ [RS-00 Yaw] ─→ MAIN
                         57mm              57mm             57mm
                       ←──────────── 171 mm ────────────→
                               ↑ Visuellement : un "tuyau"
                               très peu humanoid
```

### 2.7 Solutions esthétiques étudiées dans l'industrie

**Approche Tesla Optimus — Poignet offset + routage tendons intelligent :**
Tesla n'empile pas 3 moteurs. La « magie » est que le **Roll de l'avant-bras** (Elbow Yaw / Supination-Pronation) est réalisé en amont (niveau coude) avec un moteur plus puissant, ce qui permet de n'avoir que **2 petits moteurs au poignet** dans un boîtier compact.

**Approche envisageable pour D-Bot :**
Plutôt que d'ajouter un 3ème RS-00 en série au poignet, on pourrait déplacer le **RS-02 Épaule Yaw** vers le **Coude Yaw (Supination)** — ce que votre document 25 appelle "Elbow Yaw" (classé 🟡 Optionnel). Cette redistribution permettrait d'avoir :

```
  Architecture alternative ("Tesla-like") :

  RS-04 Épaule Pitch
  RS-03 Épaule Roll
  RS-02 Épaule Yaw   →  déplacé au coude = Forearm Supination
  RS-06 Coude Pitch
  RS-00 Poignet Pitch   (nouveau)
  RS-00 Poignet Roll    (existant)
  → Bras 6 DOF — même architecture que Tesla Optimus !
```

> [!NOTE]
> Cette alternative "Tesla-like" présente l'avantage de garder un **poignet de seulement 2 RS-00** (Roll + Pitch, ~114mm), visuellement acceptable, tout en gagnant la Supination de l'avant-bras (RS-02 au coude). Cependant, elle implique une refonte de l'épaule : le Yaw d'épaule est remplacé par le Forearm Yaw. C'est une **décision d'architecture majeure** à évaluer en V2.

### 2.8 Verdict esthétique pour la V1

| Architecture | DOF | Esthétique poignet | Complexité refonte |
| :--- | :---: | :---: | :---: |
| **V1 actuelle (1 DOF)** | 5 bras | ✅ Très compact | Aucune |
| **V1.1 +Pitch (2 DOF)** | 6 bras | ✅ Acceptable (~114mm poignet) | Faible |
| **3 DOF série naïf** | 7 bras | ❌ "Tuyau" 171mm, peu humanoïde | Moyenne |
| **3 DOF Tesla-like** | 6 bras* | ✅ Compact (même que V1.1) | **Élevée (refonte épaule)** |

*Tesla-like = 6 DOF bras avec redistribution Épaule Yaw → Forearm Supination

> [!TIP]
> Pour la V1, la contrainte esthétique **plaide clairement pour 2 DOF au poignet** (Roll + Pitch). C'est le choix de Tesla Optimus, d'Unitree G1-EDU, et c'est cohérent avec l'architecture actuelle du D-Bot sans refonte majeure.

---

## Partie 3 — Impact sur la Capacité de Portage

### 3.1 Données de référence (RAG — Conclusions Architecture)

D'après **[16_Conclusions_Architecture_DBot.md](../16_Conclusions_Architecture_DBot.md)** :

| Scénario | Couple requis | Moteur limitant | Capacité actuelle |
| :--- | :---: | :---: | :---: |
| **Bras tendu (frontal), continu** | ~33 N.m | RS-04 Pitch (40 N.m nom.) | **~5 kg continu** |
| **Bras tendu (frontal), pic** | ~55 N.m | RS-04 Pitch (120 N.m pic) | **~10 kg pic** |
| **Bras plié 90°** | ~30 N.m | RS-06 Coude (36 N.m nom.) | **~8-10 kg** |

### 3.2 Impact de l'ajout du RS-00 Pitch sur le portage

L'ajout du RS-00 Pitch place **310g supplémentaires** dans l'avant-bras, à environ **10-15 cm du poignet** (soit ~17-18 cm du coude). Voici les calculs d'impact :

```
BRAS DE LEVIER — Calcul de l'impact du RS-00 Pitch additionnel

Masse RS-00 Pitch ajouté : 0.310 kg
Position dans l'avant-bras : ~15 cm du coude (0.15 m)
Position par rapport à l'épaule Pitch (bras tendu) : ~55 + 15 = ~70 cm (0.70 m)

Couple additionnel sur l'épaule Pitch :
  τ = m × g × d = 0.310 × 9.81 × 0.70 = 2.13 N.m

Perte de portage (bras tendu, continu) :
  Δportage = τ / (g × d_bras) = 2.13 / (9.81 × 0.70) ≈ 0.31 kg

Capacité de portage résiduelle (bras tendu) :
  5.0 kg → ~4.7 kg continu (-6%)
```

> [!NOTE]
> **L'impact est de -310g de portage**, soit une réduction de ~6% de la capacité de charge à bras tendu. C'est **totalement négligeable** en pratique.

### 3.3 Impact si l'avant-bras est allongé de 20 mm (Option D)

Si on choisit d'allonger l'avant-bras de 220 → 240 mm pour ne pas comprimer l'électronique :

```
Longueur avant-bras : +20mm (0.02 m)
Masse structure additionnelle estimée : ~50g (alu 7075 tubulaire)

Couple additionnel sur l'épaule (bras tendu) :
  τ_structure = 0.050 × 9.81 × 0.75 = 0.37 N.m  (≈ 55g de portage perdus)

Couple additionnel RS-00 (plus éloigné de 20mm) :
  τ_RS00 = 0.310 × 9.81 × 0.72 = 2.19 N.m  (≈ 0.31 kg de portage perdus)

Impact total : ~-0.36 kg sur le portage à bras tendu (5.0 → ~4.64 kg)
```

> [!TIP]
> Même en allongeant l'avant-bras de 20mm, la perte de portage reste **inférieure à 400g** sur 5 kg, soit **-7.2%** — acceptable. La capacité de 4.6 kg continu à bras tendu reste largement suffisante pour les usages quotidiens du robot.

### 3.4 Impact sur l'anthropomorphisme (longueur du bras)

Un avant-bras humain moyen mesure environ **24-26 cm** (coude → poignet), ce qui est nettement plus que les 22 cm actuels du D-Bot. Allonger à 24 cm (+20 mm) rapprocherait le D-Bot des proportions humaines, ce qui est un avantage pour le sim-to-real.

---

## Partie 4 — Recommandation Finale

### 4.1 Résumé consolidé des options (avec U2D2 déporté comme hypothèse de base)

| Critère | A : Statu quo | B : +Pitch 220mm | C : +Pitch 240mm | D : +Pitch+Yaw 260mm |
| :--- | :---: | :---: | :---: | :---: |
| **DOF poignet** | 1 (Roll) | 2 (Roll+Pitch) | 2 (Roll+Pitch) | 3 (Roll+Pitch+Yaw) |
| **Compatibilité IA** | ⚠️ Partielle | ✅ Bonne | ✅ Bonne | ✅✅ Totale |
| **Espace électro** | 75mm | **~18mm** (Buck compact ✅) | **~38mm** (confortable) | **~18mm** (Buck compact ✅) |
| **Perte de portage** | 0% | -6% | -7.2% | -12% |
| **Longueur avant-bras** | 220mm | 220mm | **240mm** | **260mm** |
| **Esthétique poignet** | ✅ Compact | ✅ Acceptable | ✅ Acceptable | ⚠️ Tuyau 171mm |
| **Coût** | 0€ | ~100€/bras | ~110€/bras | ~200€/bras |
| **Masse ajoutée/bras** | 0g | 310g | 360g | 620g |

### 4.2 🏆 Recommandation

> [!IMPORTANT]
> **Recommandation V1 : Option B — Ajouter le RS-00 Pitch, conserver 220 mm, déporter le U2D2.**

**Justification en 5 points :**

1. **Le U2D2 déporté résout le problème d'espace** : En positionnant le U2D2 Power Hub dans le torse ou l'humérus, seul un Buck converter ultra-compact reste dans l'avant-bras. 18 mm suffisent pour un Pololu D24V90F12 (15mm de long). L'Option C à 240mm n'est plus nécessaire.

2. **220 mm préserve le ratio esthétique du bras** : La main D-Hand (~18cm) + avant-bras (22cm) + bras (33cm) donne des proportions proches du standard humanoïde. 240mm allonge légèrement mais reste acceptable si un jour on monte à 3 DOF.

3. **2 DOF est le choix optimal pour l'esthétique** : La section §2.8 démontre qu'un poignet 3-DOF en série naïf crée un "tuyau" de 171mm visuellement disgracieux. Tesla Optimus et Unitree G1-EDU s'arrêtent tous deux à **2 DOF au poignet**.

4. **La perte de portage (-6%) est négligeable** : Le D-Bot conserve ~4.7 kg à bras tendu continu, bien au-dessus des besoins courants.

5. **La route vers le 3-DOF reste ouverte** : Si un Wrist Yaw est souhaité en V2, allonger à 240mm + ajouter un 3ème RS-00 sera faisable. Mais il faudra alors étudier une architecture "Tesla-like" (redistribution Épaule Yaw → Forearm Supination) pour conserver un poignet compact et esthétique.

### 4.3 Architecture cible V1.1

```
CHAÎNE CINÉMATIQUE BRAS D-BOT V1.1 (6 DOF)

ÉPAULE              ÉPAULE          ÉPAULE         COUDE          POIGNET         POIGNET     MAIN
RS-04 Pitch    RS-03 Roll     RS-02 Yaw      RS-06 Pitch    RS-00 Roll    RS-00 Pitch  D-Hand 8DOF
   │               │               │              │               │              │           │
   DOF 1           DOF 2           DOF 3          DOF 4          DOF 5         DOF 6       DOF 7→14

Bras passe de 5 DOF → 6 DOF (+1 Wrist Pitch)
Main inchangée : 8 DOF
Total membre supérieur : 14 DOF par bras (contre 13 actuellement)
```

### 4.4 Nouvelle disposition de l'avant-bras (240 mm)

```
VUE LONGITUDINALE — AVANT-BRAS V1.1 (240 mm)

  COUDE (RS-06)                                              POIGNET
  ←───────────────────────── 240 mm ─────────────────────────────→
  │                                                               │
  │  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐  │
  │  │ 4× XC430 │  │ 4× XC330 │  │  RS-00    │  │  Électro.  │  │
  │  │ 93mm     │  │ 52mm     │  │  PITCH    │  │  ~38mm     │  │
  │  │ 57×68mm  │  │ 40×52mm  │  │  57mm     │  │  Buck+câbl │  │
  │  └──────────┘  └──────────┘  └───────────┘  └────────────┘  │
  │  ← 93mm →      ← 52mm →      ← 57mm →        ← 38mm →      │
                                       ↑
                                  RS-00 Pitch ici
                                  (Ø50mm < Ø80mm ✅)
```

**RS-00 Roll** reste à l'extrémité distale (il constitue l'articulation du poignet proprement dite, entre l'avant-bras et la main).

---

## Récapitulatif Budgétaire (Option B recommandée)

| Composant | Quantité | Prix Unit. | Total |
| :--- | :---: | :---: | :---: |
| RS-00 Pitch supplémentaire | 2 (1/bras) | ~80-100 € | **~200 €** |
| Buck converter ultra-compact (Pololu D24V90F12 ou équiv.) | 2 | ~15 € | **~30 €** |
| Câbles CAN supplémentaires | 2 | ~5 € | **~10 €** |
| Gaines PTFE supplémentaires (~100mm/tendon × 8) | 1 lot | ~5 € | **~5 €** |
| **Total V1.1 — Option B (2 bras)** | | | **~245 €** |

**Note** : Le U2D2 Power Hub est déporté dans le torse/épaule — pas de coût supplémentaire (déplacement, pas d'achat). Un câble de bus Dynamixel légèrement plus long peut être nécessaire (~5€).

**Poids ajouté total (2 bras)** : 2 × 310g (RS-00) = **620g**
**Nouveau poids robot estimé** : 39.4 + 0.62 = **~40.0 kg**

### Option C (si allongement préféré pour plus de confort)

| Composant additionnel vs Option B | Coût | Masse |
| :--- | :---: | :---: |
| Structure avant-bras allongée +20mm (alu tubulaire) | ~20 € | +100g (2 bras) |
| **Total Option C** | **~265 €** | **+720g** |

---

*Étude réalisée le 07/05/2026 à partir du RAG D-Bot (documents 14, 16, 21, 25) et des spécifications officielles RobStride. Sources web : documentation RobStride, OpenArm, Tesla Optimus brevets, Unitree G1 specs.*
