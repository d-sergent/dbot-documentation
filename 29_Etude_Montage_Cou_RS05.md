# 29 — Étude : Montage Vertical RS-05 pour le Roll de Tête (Cou)

Cette annexe détaille la conception du montage vertical d'un moteur **RobStride RS-05** destiné à piloter le **Roll** (inclinaison latérale) de la tête du D-Bot, avec un **roulement de support externe** pour délester le rotor des efforts axiaux et radiaux.

---

## 1. Contexte et Problématique

### 1.1 Cahier des Charges

| Paramètre | Valeur |
| :--- | :--- |
| **Moteur** | RobStride RS-05 (191g, 46×46×44mm) |
| **Couple pic** | 5.5 N.m |
| **Couple nominal** | 1.6 N.m |
| **Masse de la tête** | ~2 kg (structure + capteurs OAK-D Pro + électronique) |
| **Mouvement** | Roll (inclinaison latérale gauche/droite) |
| **Orientation moteur** | Vertical, stator fixé au torse, rotor vers le haut |
| **Amplitude souhaitée** | ±30° à ±45° |

### 1.2 Particularité Critique : Interface Rotor RS-05 (Pas de Sortie d'Arbre !)

> ⚠️ **Point fondamental** : À la différence de nombreux actionneurs, le RS-05 ne possède **aucun arbre de sortie saillant**. Le rotor est **affleurant avec le stator**, exposant uniquement une **face plane avec un plot de centrage** et des **trous filetés**.

![Photo du RS-05 (Vue de dessus) — Rotor et Stator affleurants](./assets/img_rs05_photo_top.png)
*Vue photographique de la face supérieure du RS-05 avec ses 3 plots de centrage.*

![Plan de montage officiel RobStride RS-05 — Interface rotor et fixations](./assets/img_rs05_drawing.png)

### Interface du Rotor RS-05 (données plan officiel)

| Élément | Dimension |
| :--- | :--- |
| **Trous visserie STATOR (interface périphérique)** | **8× M3 Profondeur 6 mm** (EQS sur ø38.5mm) |
| **Trous visserie ROTOR (interface tournante)** | **6× M4 Profondeur 3 mm** (EQS sur ø24mm) + 3 plots |
| **Alésage central côté rotor** | ø24 mm |
| **Diamètre rotor** | ø41.5 mm |
| **Diamètre extérieur corps moteur** | ø46 mm |
| **Profondeur totale** | 44 mm |
| **Fixation stator (arrière)** | 4× M3 Profondeur 8 mm |

**Conséquence directe** : Il est **impossible** de monter un roulement directement sur un arbre de rotor (il n'existe pas). La solution doit être une **architecture flasque/moyeu** boulonnée sur la face du rotor, avec un roulement **annulaire** ou **thin-section** positionné autour de ce moyeu.

---

## 2. ⚠️ Conflit Géométrique : Pourquoi un Roulement Coplanaire ne Rentre PAS

### 2.1 Analyse Dimensionnelle du Problème

Le principe initial était de placer un roulement annulaire (type 6806-2RS) **dans le même plan** que la face du rotor, entre la zone de fixation du rotor (Ø24mm) et le bord du stator (Ø41.5mm). **Cette solution est physiquement impossible** en raison de l'espace radial insuffisant.

```
VUE DE DESSUS — CONFLIT GÉOMÉTRIQUE

         Corps stator (46×46 mm carré)
         ┌──────────────────────────────────────┐
         │                                      │
         │   8×M3 stator (Ø38.5mm)             │
         │      ○──○──○──○──○──○──○──○          │
         │                                      │
         │     ┌── Face Rotor Ø41.5mm ──┐       │
         │     │                        │       │
         │     │   Têtes vis M4 ≈ Ø31mm │       │
         │     │      ●  ●  ●           │       │
         │     │      ●  ●  ●           │       │
         │     │   6×M4 sur Ø24mm       │       │
         │     │   + boss Ø17.7mm       │       │
         │     │                        │       │
         │     └────────────────────────┘       │
         └──────────────────────────────────────┘

Espace radial disponible entre têtes vis M4 et bord rotor :
  (Ø41.5 − Ø31) / 2 = 5.25 mm par côté

Section du roulement 6806-2RS :
  (Ø42 − Ø30) / 2 = 6 mm par côté

→ 6 mm > 5.25 mm ⇒ LE ROULEMENT NE RENTRE PAS ! ❌
```

### 2.2 Détail des Cotes Critiques

| Élément | Diamètre | Source |
| :--- | :--- | :--- |
| Boss centrage rotor | Ø17.7 mm | Plan officiel |
| Cercle perçage M4 (rotor) | **Ø24 mm** | Plan officiel |
| Limite extérieure têtes vis M4 (≈Ø7mm) | ≈ **Ø31 mm** | Calcul |
| Cercle perçage M3 (stator) | Ø38.5 mm | Plan officiel |
| Face du rotor | **Ø41.5 mm** | Plan officiel |
| Corps stator (carré) | 46 × 46 mm | Plan officiel |
| **Roulement 6806-2RS — bague int.** | **Ø30 mm** | Catalogue |
| **Roulement 6806-2RS — bague ext.** | **Ø42 mm** | Catalogue |

> 🔴 **Conclusion** : Le roulement 6806-2RS (Ø42 ext.) **dépasse le diamètre du rotor** (Ø41.5 mm). Il n'y a aucune surface fixe (stator) pour accueillir un carter à ce diamètre dans le même plan. **La solution coplanaire est abandonnée.**

---

## 3. Trois Solutions Viables

### 3.1 Solution 1 — Hub Surélevé + Roulement 6806-2RS ⭐ RECOMMANDÉE

Au lieu de coincer le roulement dans l'espace minuscule entre rotor et stator, on **empile** le roulement **au-dessus** du moteur, sur un étage séparé.

![Solution 1 : Hub Surélevé + Roulement 6806-2RS — Vue en coupe](./assets/img_rs05_solution1_hub_sureleve.png)

**Principe :**

Un **tube-hub cylindrique** (Al-6061) se visse sur le rotor (6×M4, Ø24mm) et **s'élève verticalement** de 15-20 mm au-dessus du plan du stator. À cette hauteur, il n'y a plus de conflit géométrique : le roulement peut avoir n'importe quel diamètre. Le carter fixe (qui tient la bague extérieure) se fixe au torse du robot, indépendamment du stator.

```
   ┌─────────────────────────┐
   │     TÊTE (~2 kg)        │
   └──────────┬──────────────┘
              │ (vis M4)
   ╔══════════╧══════════════╗
   ║   BAGUE EXT. (fixe)    ║ ← Fixée au CARTER (solidaire du torse)
   ║  ┌──────────────────┐  ║
   ║  │   ROULEMENT      │  ║ ← 6806-2RS : Ø30×Ø42×7mm
   ║  └──────────────────┘  ║    (n'importe quel diamètre ici !)
   ║   BAGUE INT. (tourne)  ║ ← Solidaire du TUBE HUB
   ╚══════════╤══════════════╝
              │
   ┌──────────┴──────────────┐
   │   TUBE HUB (Al 6061)   │ ← Cylindre creux, Ø ext ~30mm
   │   Hauteur ~15-20mm     │    Centré sur boss Ø17.7mm
   │   Vissé 6×M4 au rotor  │    S'élève AU-DESSUS du stator
   └──────────┬──────────────┘
              │
   ┌──────────┴──────────────┐
   │   ROTOR (Ø24mm M4)     │ ← Face affleurante du RS-05
   │   STATOR (Ø41.5mm)     │
   │   Corps 46×46×44mm     │
   └──────────┬──────────────┘
              │ (4×M3 arrière → torse)
   ┌──────────┴──────────────┐
   │      TORSE ROBOT        │
   └─────────────────────────┘
```

| Paramètre | Valeur |
| :--- | :--- |
| **Tube Hub** | Al 6061, Ø ext 30mm, hauteur 15-20mm, centrage Ø17.7mm + 3 plots, fixation 6×M4 |
| **Roulement** | 6806-2RS (Ø30×Ø42×7mm) |
| **Carter fixe** | Al 6061 ou PA12-CF, alésage Ø42mm H7, fixé au torse |
| **Surcoût hauteur** | +15-20 mm au-dessus du moteur |
| **Charge axiale** | ✅ 560 N (largement suffisant pour 19.6 N) |
| **Charge radiale** | ✅ 4.6 kN |
| **Reprise de moment** | ✅ Bon |
| **Coût** | ~8 € (roulement + usinage maison) |

> ✅ **Avantage majeur** : Aucune contrainte de diamètre — le roulement standard 6806-2RS reprend **tous les efforts** (axial, radial, moment). Solution robuste et éprouvée.

---

### 3.2 Solution 2 — Roulement Ultra-Mince 6706-2RS (Coplanaire)

Si l'on souhaite absolument **minimiser la hauteur** du montage, il existe des roulements à **section extraordinairement fine** (série 6700) qui peuvent se glisser entre le rotor et le stator.

![Solution 2 : Roulement Ultra-Mince 6706-2RS — Vue en coupe](./assets/img_rs05_solution2_roulement_mince.png)

**Principe :**

Le roulement **6706-2RS** (Ø30 × Ø37 × 4mm) a une section de seulement **3.5 mm**. Avec un Ø extérieur de 37 mm, il reste **à l'intérieur** du rotor (Ø41.5mm), laissant ~2.25 mm par côté pour un carter de précision.

| Référence | Ø int | Ø ext | Section | Largeur |
| :--- | :--- | :--- | :--- | :--- |
| **6706-2RS** | 30 mm | **37 mm** | **3.5 mm** | 4 mm |
| 6806-2RS (référence) | 30 mm | 42 mm | 6 mm | 7 mm |

| Paramètre | Valeur |
| :--- | :--- |
| **Hub** | Al 6061, Ø ext 30mm, épaisseur ~8mm, épaulement Ø30 pour bague int. |
| **Roulement** | 6706-2RS (Ø30×Ø37×4mm) |
| **Carter fixe** | Usinage de précision — épaisseur paroi ≈ 2.25mm seulement ! |
| **Surcoût hauteur** | +4 mm seulement |
| **Charge axiale** | ⚠️ ~200 N (suffisant pour 19.6 N mais faible marge) |
| **Charge radiale** | ⚠️ ~1-2 kN (faible) |
| **Reprise de moment** | ⚠️ Limitée (section très mince) |
| **Coût** | ~5 € |

> ⚠️ **Attention** : Le carter doit être usiné avec une **tolérance très serrée** (paroi de 2.25mm). Cette solution est faisable mais exigeante en précision d'usinage et offre moins de marge mécanique.

---

### 3.3 Solution 3 — Butée à Aiguilles AXK 2035 (Axial Uniquement)

Pour ne reprendre que **la charge axiale** (le poids de la tête = 19.6 N), une **butée à aiguilles plate** est extrêmement mince et se glisse comme une rondelle entre le hub et un support fixe.

![Solution 3 : Butée à Aiguilles AXK 2035 — Vue en coupe](./assets/img_rs05_solution3_butee_aiguilles.png)

**Principe :**

La butée AXK 2035 (Ø20 × Ø35 × **2 mm**) s'insère directement entre le hub rotatif et une rondelle de pression fixe, sans aucun problème d'encombrement radial. Le Ø extérieur de 35 mm reste largement dans l'enveloppe du rotor (Ø41.5mm).

| Référence | Ø int | Ø ext | Épaisseur | Charge axiale stat. |
| :--- | :--- | :--- | :--- | :--- |
| **AXK 2035** | 20 mm | **35 mm** | **2 mm** | ~10 kN |
| AXK 2542 | 25 mm | 42 mm | 2 mm | ~15 kN |

| Paramètre | Valeur |
| :--- | :--- |
| **Hub** | Al 6061, Ø ext 35mm, épaisseur ~6mm |
| **Butée** | AXK 2035 (Ø20×Ø35×2mm) + 2 rondelles AS (AS 2035) |
| **Surcoût hauteur** | +2 mm seulement ! |
| **Charge axiale** | ✅✅ ~10 kN (excellent, ×500 la charge requise) |
| **Charge radiale** | ❌ Zéro — ne reprend pas les efforts latéraux |
| **Reprise de moment** | ❌ Zéro — ne reprend pas le basculement |
| **Coût** | ~3 € |

> ⚠️ **Limitation majeure** : La butée à aiguilles ne reprend **que l'effort axial** (poids vertical de la tête). Les charges radiales et les moments de basculement restent entièrement supportés par les roulements internes du RS-05. Cette solution est viable car la charge est faible (2 kg), mais elle n'offre **aucune protection** contre les chocs latéraux.

---

## 4. Comparatif des 3 Solutions

| Critère | Sol. 1 : Hub Surélevé 6806 | Sol. 2 : Ultra-Mince 6706 | Sol. 3 : Butée AXK 2035 |
| :--- | :---: | :---: | :---: |
| **Faisabilité** | ✅ Excellente | ⚠️ Très serré (2.25mm) | ✅ Simple |
| **Charge axiale** | ✅ 560 N | ⚠️ ~200 N | ✅✅ ~10 kN |
| **Charge radiale** | ✅ 4.6 kN | ⚠️ ~1 kN | ❌ Zéro |
| **Moment (tilt)** | ✅ Bon | ⚠️ Faible | ❌ Zéro |
| **Surcoût hauteur** | ⚠️ +15-20 mm | ✅ +4 mm | ✅✅ +2 mm |
| **Complexité usinage** | 🟡 Tube + carter | 🔴 Carter très précis | 🟢 Très simple |
| **Coût** | ~8 € | ~5 € | ~3 € |

> **🟢 Recommandation finale : Solution 1 (Hub Surélevé + 6806-2RS)** — C'est la seule qui offre une **vraie reprise de tous les efforts** (axial, radial, moment) avec un roulement standard facile à trouver. Le surcoût en hauteur de 15-20 mm est parfaitement acceptable pour le cou d'un robot humanoïde.
>
> La Solution 3 (butée à aiguilles) est un **excellent complément** si l'on souhaite en plus soulager l'effort axial de façon ultra-compacte, par exemple en la plaçant directement sous le tube-hub de la Solution 1.

---

## 5. Séquence de Montage (Solution 1 Recommandée)

```
SÉQUENCE DE MONTAGE — SOLUTION 1 : HUB SURÉLEVÉ

1. Fixer le STATOR RS-05 au torse (4× M3 arrière)
        ↓
2. Monter le CARTER FIXE sur la structure du torse
   (alésage Ø42mm H7 pour bague ext.)
   Positionné ~20mm au-dessus du plan du stator
        ↓
3. Emmancher la bague extérieure du 6806-2RS dans le carter
   (emmanchement serré H7/r6 ou k6)
        ↓
4. Assembler le TUBE HUB sur la face du rotor RS-05 :
   - Centrage ø17.7mm boss rotor + alignement 3 plots
   - Serrer 6× vis M4 à couple approprié (~1.5 N.m)
        ↓
5. La bague intérieure du 6806 s'emboîte sur l'épaulement
   ø30mm du tube hub (emmanchement tournant H7/k6)
        ↓
6. Fixer la structure de la tête sur le dessus du tube hub (4× M4)
        ↓
✅ VÉRIFICATION : La tête doit tourner librement en Roll
   sans jeu axial perceptible. Le roulement reprend
   le poids de la tête, pas le moteur.
```

---

## 6. Vérification du Couple Nécessaire

### 6.1 Couple Gravitationnel pour le Roll

```
G_roll = m × g × L × sin(θ)

  m = 2 kg (masse tête)
  g = 9.81 m/s²
  L = 0.05 m (bras de levier Centre de gravité → axe)
  θ = 45° (inclinaison maximale)

G_roll = 2 × 9.81 × 0.05 × sin(45°) ≈ 0.69 N.m
```

### 6.2 Marge RS-05

| Paramètre | Valeur |
| :--- | :--- |
| **Couple gravitationnel max** | 0.69 N.m (à 45°) |
| **Couple nominal RS-05** | 1.6 N.m |
| **Couple pic RS-05** | 5.5 N.m |
| **Marge nominale** | ×2.3 ✅ |
| **Marge pic** | ×8 ✅ |

---

## 7. BOM — Récapitulatif Achat (Solution 1)

| Composant | Référence | Qté | Prix Unit. | Fournisseur |
| :--- | :--- | :---: | :---: | :--- |
| Roulement thin-section | **6806-2RS** (30×42×7mm) | 1 | ~4-6 € | SKF, NSK, Amazon |
| Tube Hub | Alu 6061 Ø30 × 20mm hauteur (CNC) | 1 | Usinage maison | Stock alu |
| Carter fixe annulaire | Alu 6061 (CNC) ou PA12-CF | 1 | Usinage/impression | Stock |
| Visserie | 6× M4×8 CHC (fixation hub→rotor) | 1 | ~0.50 € | Visserie standard |
| Visserie | 4× M4 (fixation tête→hub) | 1 | ~0.50 € | Visserie standard |

**Coût total ajouté** : **< 15 €** pour une solution professionnelle et durable.

---

## 8. Conclusion

> **🟢 Le montage avec roulement de support est fortement recommandé, avec l'architecture HUB SURÉLEVÉ + roulement annulaire 6806-2RS (Solution 1).**
>
> L'analyse dimensionnelle a révélé un **conflit géométrique critique** : l'espace radial disponible entre le cercle de vis M4 du rotor (Ø24mm) et le bord du stator (Ø41.5mm) est trop étroit (5.25 mm) pour accueillir un roulement 6806-2RS (section 6 mm) dans le même plan. **Un montage coplanaire avec un 6806-2RS est impossible.**
>
> La solution retenue consiste à **surélever le roulement** au-dessus du moteur grâce à un tube-hub cylindrique (Al-6061, hauteur 15-20mm), ce qui élimine tout conflit de diamètre. Le carter fixe se monte indépendamment sur le torse, et l'ensemble reprend **100% des charges statiques** (poids de la tête de 2 kg, moments de basculement).
>
> Le RS-05 ne fournit alors que le **couple de Roll pur** (0.69 N.m max vs 1.6 N.m nominal), avec une marge confortable de ×2.3.
>
> Les 8× M3 périphériques du moteur appartiennent au **stator** et servent uniquement à fixer le moteur au torse. Le stator ne peut être fixé que par l'**arrière** (4× M3).
