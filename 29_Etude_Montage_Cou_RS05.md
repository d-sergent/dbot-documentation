# 29 — Étude : Montage Vertical RS-05 pour le Roll de Tête (Cou)

Cette annexe détaille la conception du montage vertical d'un moteur **RobStride RS-05** destiné à piloter le **Roll** (inclinaison latérale) de la tête du D-Bot, avec un **roulement de support externe** pour délester le rotor des efforts axiaux et radiaux.

> ✅ **Statut (Mars 2026)** : La Solution 4 a été **prototypée et validée** avec un roulement **6804-2RS** (Ø20×Ø32×7mm). Ce roulement offre une marge mécanique supérieure au 6802-2RS initialement étudié, tout en restant largement dans l'enveloppe du moteur. La documentation a été mise à jour en conséquence.

> 📄 **Note** : La section relative à la préparation URDF (nommage Fusion 360, chaîne cinématique du cou, export) a été extraite dans un document dédié : **[30_URDF_Cou_Neck.md](./30_URDF_Cou_Neck.md)**.

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

> 🔴 **Conclusion** : Le roulement 6806-2RS (Ø42 ext.) **dépasse le diamètre du rotor** (Ø41.5 mm). **La solution coplanaire est abandonnée.**

---

## 3. Solutions Étudiées

### 3.1 Solution 1 — Hub Surélevé + Roulement 6806-2RS

Un **tube-hub cylindrique** (Al-6061) se visse sur le rotor (6×M4, Ø24mm) et **s'élève verticalement** de 15-20 mm au-dessus du plan du stator. À cette hauteur, il n'y a plus de conflit géométrique.

| Paramètre | Valeur |
| :--- | :--- |
| **Roulement** | 6806-2RS (Ø30×Ø42×7mm) |
| **Surcoût hauteur** | +15-20 mm |
| **Charge axiale** | ✅ 560 N |
| **Charge radiale** | ✅ 4.6 kN |
| **Reprise de moment** | ✅ Bon |
| **Coût** | ~8 € |

---

### 3.2 Solution 2 — Roulement Ultra-Mince 6706-2RS (Coplanaire)

Le roulement **6706-2RS** (Ø30 × Ø37 × 4mm) a une section de seulement **3.5 mm**. Avec un Ø extérieur de 37 mm, il reste à l'intérieur du rotor (Ø41.5mm), laissant ~2.25 mm par côté pour un carter de précision.

| Paramètre | Valeur |
| :--- | :--- |
| **Roulement** | 6706-2RS (Ø30×Ø37×4mm) |
| **Surcoût hauteur** | +4 mm |
| **Charge axiale** | ⚠️ ~200 N |
| **Charge radiale** | ⚠️ ~1-2 kN |
| **Reprise de moment** | ⚠️ Limitée |
| **Coût** | ~5 € |

> ⚠️ Le carter doit être usiné avec une **tolérance très serrée** (paroi de 2.25mm). Exigeant en précision CNC.

---

### 3.3 Solution 3 — Butée à Aiguilles AXK 2035 (Axial Uniquement)

La butée AXK 2035 (Ø20 × Ø35 × 2mm) s'insère directement entre le hub rotatif et une rondelle de pression fixe, sans problème d'encombrement radial.

| Paramètre | Valeur |
| :--- | :--- |
| **Butée** | AXK 2035 (Ø20×Ø35×2mm) + rondelles AS 2035 |
| **Surcoût hauteur** | +2 mm |
| **Charge axiale** | ✅✅ ~10 kN |
| **Charge radiale** | ❌ Zéro |
| **Reprise de moment** | ❌ Zéro |
| **Coût** | ~3 € |

> ⚠️ **Limitation majeure** : ne reprend que l'effort axial. Les charges radiales restent entièrement sur les roulements internes du RS-05.

---

### 3.4 Solution 4 — Hub Réduit + Roulement 6804-2RS ⭐ PROTOTYPÉE ET VALIDÉE

**Principe** : réduire le diamètre du tube-hub de sorte que le roulement entier rentre **à l'intérieur de l'enveloppe du stator** (Ø41.5mm). La bague extérieure est emmanchée dans un carter fixe solidaire du torse. Plus aucun conflit de diamètre.

> ✅ **Prototype validé (Mars 2026)** : Cette solution a été réalisée et testée avec un roulement **6804-2RS** (Ø20×Ø32×7mm). Le Ø extérieur de 32 mm laisse une marge confortable de **4.75 mm par côté** vis-à-vis du bord du rotor (Ø41.5mm), avec une capacité radiale nettement supérieure au 6802-2RS initialement prévu.

```
VUE EN COUPE — SOLUTION 4 : HUB RÉDUIT + 6804-2RS (PROTOTYPE)

   ┌─────────────────────────┐
   │     TÊTE (~2 kg)        │
   └──────────┬──────────────┘
              │ (4× vis M4)
   ┌──────────┴──────────────┐
   │   BRIDE SUPÉRIEURE      │ ← Fixation tête → hub
   └──────────┬──────────────┘
        ┌─────┴─────┐
        │ CARTER    │ ← Al-6061, alésage Ø32mm H7
        │ FIXE      │    fixé au torse/stator
        │           │ ← Bague ext. Ø32mm (FIXE)
        │ ┌───────┐ │
        │ │6804-2R│ │ ← Ø20 int × Ø32 ext × 7mm
        │ └───────┘ │
        │           │ ← Bague int. Ø20mm (TOURNE)
   Circlip E20 ════ ◄ Retenue axiale haute
        └─────┬─────┘
   Épaulem. ►─┴─◄ Retenue axiale basse
        ┌─────┴─────┐
        │ TUBE HUB  │ ← Al-6061, Ø principal 20mm
        │ Ø20/22mm  │    Vissé au rotor via bride 6×M4
        └─────┬─────┘
   ┌──────────┴──────────────┐
   │   ROTOR (Ø41.5mm)       │ ← 6×M4 sur Ø24mm + boss Ø17.7mm
   │   STATOR (46×46×44mm)   │ ← 4×M3 arrière (fixation torse)
   └──────────┬──────────────┘
   ┌──────────┴──────────────┐
   │      TORSE ROBOT        │
   └─────────────────────────┘

   Ø32mm (roulement ext.) << Ø41.5mm (rotor)
   → Marge = 4.75mm par côté ✅
```

#### Tailles de Roulements (Série 6800 Thin-Section) — Comparatif

| Référence | Ø Int. | Ø Ext. | Largeur | Cap. Rad. | Marge/côté vs rotor Ø41.5 | Statut |
| :---: | :---: | :---: | :---: | :--- | :---: | :--- |
| **6802-2RS** | 15 mm | 24 mm | 5 mm | ~1.6 kN | 8.75 mm | Étudié (théorique) |
| **6803-2RS** | 17 mm | 26 mm | 5 mm | ~1.7 kN | 7.75 mm | Alternative valide |
| **6804-2RS** | **20 mm** | **32 mm** | **7 mm** | **~3.0 kN** | **4.75 mm** | ⭐ **Prototypé et validé** |
| 6805-2RS | 25 mm | 37 mm | 7 mm | ~3.2 kN | 2.25 mm | ⚠️ Limite — carter très fin |
| 6806-2RS | 30 mm | 42 mm | 7 mm | ~4.6 kN | — | ❌ Dépasse le rotor |

> **Choix du 6804-2RS** : Le prototype a confirmé que le 6804-2RS offre le meilleur compromis. Sa capacité radiale (~3.0 kN, soit ×150 la charge requise) est largement supérieure au 6802-2RS, le hub Ø20mm est plus rigide et plus facile à usiner, et la marge de 4.75 mm par côté permet un carter avec une paroi confortable d'au moins 3 mm.

---

## 4. Comparatif des 4 Solutions

| Critère | Sol. 1 : Hub surélevé 6806 | Sol. 2 : Ultra-mince 6706 | Sol. 3 : Butée AXK | Sol. 4 : Hub réduit 6804 ⭐ |
| :--- | :---: | :---: | :---: | :---: |
| **Faisabilité** | ✅ Bonne | ⚠️ Très serré | ✅ Simple | ✅✅ Excellente |
| **Charge axiale** | ✅ 560 N | ⚠️ ~200 N | ✅✅ ~10 kN | ✅ ~1.9 kN |
| **Charge radiale** | ✅ 4.6 kN | ⚠️ ~1 kN | ❌ Zéro | ✅ ~3.0 kN |
| **Reprise de moment** | ✅ Bon | ⚠️ Faible | ❌ Zéro | ✅ Bon |
| **Surcoût hauteur** | ⚠️ +15-20 mm | ✅ +4 mm | ✅✅ +2 mm | ✅ +10-15 mm |
| **Complexité usinage** | 🟡 Modérée | 🔴 Carter très précis | 🟢 Très simple | 🟢 Simple (alésage Ø32 H7) |
| **Coût** | ~8 € | ~5 € | ~3 € | ~4-6 € |
| **Encombrement radial** | ⚠️ Dépasse le stator | ⚠️ Limite | ✅ Compact | ✅ Compact (marge 4.75mm) |
| **Statut** | Théorique | Théorique | Théorique | ⭐ **Prototype validé** |

---

## 5. Séquence de Montage (Solution 4 — 6804-2RS)

```
SÉQUENCE DE MONTAGE — HUB RÉDUIT Ø20mm + 6804-2RS

1. [PRÉPARATION À LA PRESSE] Emmancher la bague extérieure du 6804-2RS
   dans le CARTER FIXE (emmanchement serré Ø32mm H7/r6).
   ⚠️ Appliquer l'effort uniquement sur la bague extérieure.
        ↓
2. Fixer le STATOR RS-05 au torse (4× M3 arrière).
        ↓
3. Assembler la BRIDE D'ADAPTATION + TUBE HUB (Ø20/22mm)
   sur la face du rotor RS-05 :
   - Centrage sur le boss Ø17.7mm du rotor
   - Serrer 6× vis M4 à ~1.5 N.m
        ↓
4. Installer le sous-ensemble [CARTER + ROULEMENT] par le dessus :
   - La bague intérieure s'emmanche sur le Ø20mm du tube hub
     jusqu'à l'épaulement butée basse (ajustement H7/k6)
   - Insérer les vis du carter SANS serrer (jeux Ø3.5mm)
        ↓
5. Auto-centrage : faire tourner le moteur à la main quelques tours.
   Le roulement aligne le carter. Serrer les vis du carter au couple.
        ↓
6. Insérer le CIRCLIP E20 dans sa gorge sur le tube hub
   (retenue axiale haute).
        ↓
7. Fixer la structure de la tête sur le dessus du tube hub (4× M4).
        ↓
✅ VÉRIFICATION : La tête tourne librement en Roll
   sans jeu axial perceptible. Le roulement reprend le poids
   de la tête, protégeant les roulements internes du RS-05.
```

> ⚠️ **Détail critique — Retenue axiale** : Le tube-hub doit comporter un **épaulement** (passage de Ø20mm à ~Ø22mm à la base) pour servir de butée basse. Un circlip E20 en gorge supérieure assure la retenue haute. Sans ces deux éléments, la bague intérieure peut translater sous charge.

---

## 6. Vérification du Couple Nécessaire

### 6.1 Couple Gravitationnel pour le Roll

```
G_roll = m × g × L × sin(θ)

  m = 2 kg (masse tête)
  g = 9.81 m/s²
  L = 0.05 m (bras de levier CdG → axe)
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

Le roulement 6804-2RS reprenant la totalité des charges statiques, le RS-05 ne fournit que le **couple de Roll pur**, avec une marge confortable.

---

## 7. BOM — Récapitulatif Achat (Solution 4 — Prototype Validé)

| Composant | Référence | Qté | Prix Unit. | Fournisseur |
| :--- | :--- | :---: | :---: | :--- |
| Roulement radial étanche | **6804-2RS** (Ø20×Ø32×7mm) | 1 | ~3-5 € | SKF, NSK, Amazon |
| Tube Hub | Al 6061 Ø20 × 12-15mm hauteur (CNC) | 1 | Usinage maison | Stock alu |
| Carter fixe (bague) | Al 6061, alésage Ø32mm H7 (CNC) | 1 | Usinage maison | Stock alu |
| Bride d'adaptation | Al 6061 (fixation 6×M4 → tube Ø20) | 1 | Usinage maison | Stock alu |
| Circlip | E20 (retenue axiale haute) | 1 | ~0.30 € | Visserie standard |
| Visserie | 6× M4×8 CHC (fixation bride→rotor) | 1 set | ~0.50 € | Visserie standard |
| Visserie | 4× M4 (fixation tête→hub) | 1 set | ~0.50 € | Visserie standard |

**Coût total ajouté** : **< 15 €** pour une solution compacte, robuste et validée en prototype.

---

## 8. Assurer la Concentricité des Axes (Rotor vs Stator)

Une contrainte majeure est que l'axe de la bague intérieure (liée au rotor) et celui de la bague extérieure (liée au carter fixe) soient **parfaitement alignés**. Tout désalignement crée usure, vibrations et surconsommation.

### 8.1 Côté Rotor : Concentricité par usinage CNC (Bague intérieure)

- **Référence native** : Le RS-05 possède un bossage usiné de **Ø17.7 mm** conçu pour le centrage physique.
- **Règle impérative** : Le Tube-Hub doit être usiné en **une seule prise CNC (même posage)** : l'alésage de centrage (Ø17.7mm H7) et le diamètre extérieur recevant le roulement (Ø20mm k6) partagent ainsi strictement le même axe de révolution.
- **Résultat** : Zéro faux-rond une fois le hub posé sur le bossage du RS-05.

### 8.2 Côté Stator : Auto-centrage au montage (Bague extérieure)

On utilise **le roulement lui-même comme gabarit d'alignement** lors du montage.

1. **Jeux de fixation** : Les trous de fixation du carter sont surdimensionnés (ex : Ø3.5 mm pour des vis M3), laissant un flottement de quelques dixièmes.
2. **Assemblage à blanc** : Le carter (avec roulement pressé) est glissé sur le tube-hub. Les vis du carter sont insérées mais **non serrées**.
3. **Auto-alignement** : Le roulement, pièce de précision, force le carter flottant dans la position concentrique exacte.
4. Faire tourner le moteur à la main quelques tours pour libérer toute contrainte résiduelle.
5. **Serrage final** : Bloquer les vis du carter au couple. Le carter est immuablement positionné.

---

## 9. Conclusion

> **⭐ Le montage pivot indépendant avec roulement 6804-2RS (Solution 4) est la solution recommandée et validée par prototype.**
>
> L'analyse dimensionnelle a confirmé l'impossibilité d'un montage coplanaire (espace radial de 5.25 mm insuffisant pour tout roulement standard). La solution retenue réduit le tube-hub à Ø20mm de sorte que le roulement 6804-2RS (Ø20×Ø32×7mm) rentre largement dans l'enveloppe du moteur (marge de 4.75 mm par côté). Le carter fixe reprend **100% des charges statiques** (poids de la tête, moments de basculement). Le RS-05 ne fournit que le couple de Roll pur, avec une marge nominale de ×2.3.
>
> Le prototype a également confirmé que le 6804-2RS est plus avantageux que le 6802-2RS initialement modélisé : hub plus rigide, usinage du carter simplifié (paroi d'au moins 3 mm), et capacité radiale doublée (~3.0 kN vs ~1.6 kN).

---

*Dernière mise à jour : Mars 2026. Voir aussi : [30_URDF_Cou_Neck.md](./30_URDF_Cou_Neck.md) pour la préparation URDF de ce sous-assemblage.*
