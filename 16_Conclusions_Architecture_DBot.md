# 16 — Conclusions : Architecture Finale du D-Bot

Ce document présente uniquement les **décisions définitives** pour le D-Bot. Il synthétise l'ensemble des études et analyses précédentes.

> **Pour comprendre le raisonnement derrière chaque choix**, consultez la [Série Biomécanique 15a→15g](./15_Analyse_Biomecanique.md).

---

## Résumé Exécutif

| Zone | Solution Retenue | Couple / Perf | Statut |
| :--- | :--- | :---: | :---: |
| **Cheville Pitch + Roll** | Cardan DIN 808 + **2× RS-03** + bielles | 120 N.m | ✅ V1 |
| **Genou Pitch** | **RS-04** + Courroie GT3 1.5:1 (S6) | 180 N.m | ✅ V1 |
| **Hanche Pitch + Yaw** | **RS-04** (pitch) + **RS-03** (roll/yaw) | 120 / 60 N.m | ✅ V1 |
| **Épaule** | **RS-04** (Pitch) + **RS-03** (Roll) + **RS-02** (Yaw) | 120 / 60 / 17 N.m | ✅ V1 |
| **Coude** | **RS-06** | 36 N.m | ✅ V1 |
| **Poignet Roll** | **RS-00** | 14 N.m | ✅ V1 |
| **Main** | **D-Hand Hybrid** (4× XC430 + 4× XC330 + tactile) | ~175 N grip | ✅ V1 |
| **Cou** | **RS-05** (×2) | 5.5 N.m | ✅ V1 |
| **Masse totale** | ~**40.4 kg** (avant allégement 3D) | — | Référence |
| **Vitesse marche** | ~**2 km/h** (genou 101%) | — | Estimé |
| **Course V1** | ~**3-4 km/h** (algo mid-foot, transitoires) | — | V1 logiciel |

---

## 1. Cheville — Architecture Cardan + 2× RS-03

**Décision : Cardan DIN 808 Série G (acier C45, axe 12mm) + 2× RS-03 (bielles carbone).**

| Paramètre | Valeur |
| :--- | :--- |
| Couple Pitch effectif | **120 N.m** (+167% vs besoin statique 38 N.m) |
| Couple Roll effectif | **120 N.m** (×8 vs l'ancien RS-00 à 14 N.m) |
| Masse distale ajoutée | **~0g** (moteurs RS-03 logés en haut du tibia) |
| Débattement Pitch | +30° / −45° |
| Débattement Roll | ±25° |

Fournisseurs : Cardan **Michaud Chailly** A5-473-12, bielles carbone 3K Ø10/8mm, rotules **Igus EBRM-05**.

> Voir : [Étude Cheville Cardan](./20_Etude_Cheville_Cardan.md) | [Analyse 39 kg](./15c_Revision_Cardan_39kg.md)

---

## 2. Genou — RS-04 + Optimisation Algorithmique

**Décision V1 : RS-04 (120 N.m) + pattern de marche mid-foot strike.**

| Scénario | Couple Requis | Couple Dispo | Verdict |
| :--- | :---: | :---: | :---: |
| Marche lente (< 1 km/h) | ~69 N.m | 120 N.m | ✅ +74% |
| Marche normale (2-3 km/h) | ~117 N.m | 120 N.m | ⚠️ Transitoires OK |
| Course algo mid-foot (4 km/h) | **~103 N.m** | 120 N.m | ✅ **Viable** |

**Évolution planifiée :**
- **V2** (~6 mois) : Tibia en lame carbone flexible → τ_genou_course ~134 N.m → +12% marge
- **V3** (~1 an) : Mécanisme tirant dans la cuisse (ratio 1.5:1 → 180 N.m, type Atlas) → course 8-10 km/h

> Voir : [Genou & Course](./15d_Genou_et_Course.md)

---

## 3. Hanches — RS-04 + RS-03

**Décision : Architecture K-Bot conservée — RS-04 (Pitch, 120 N.m) et RS-03 (Roll/Yaw, 60 N.m).**

| Articulation | Moteur | Couple Pic | Couple Requis (39 kg) | Marge |
| :--- | :---: | :---: | :---: | :---: |
| Hanche Pitch | RS-04 | 120 N.m | ~50 N.m | **+140%** ✅ |
| Hanche Roll | RS-03 | 60 N.m | ~20 N.m | **+200%** ✅ |
| Hanche Yaw | RS-03 | 60 N.m | ~15 N.m | **+300%** ✅ |

Aucune modification requise — marges très confortables même à 39 kg.

---

## 4. Bras — RS-04 / RS-03 / RS-06 / RS-02 / RS-00 ⭐ UPGRADE HYBRIDE

**Décision : Épaule Pitch RS-04 + Épaule Roll RS-03 + Coude RS-06 (Option Hybride — Compromis Idéal Max Portage / Masse).**

> 🆕 **Changement vs K-Bot** : L'épaule Pitch passe de RS-03 (60 N.m, 880g) à **RS-04 (120 N.m, 1420g)** pour ×2.5 de portage frontal. L'épaule Roll reste en **RS-03** (suffisant en latéral, économise 1.08 kg sur la paire vs 2× RS-04). Le coude passe de RS-02 (17 N.m) à **RS-06 (36 N.m)** pour ×2 de flexion. 

| Articulation | Moteur | Couple Pic | Couple Nom. | Masse |
| :--- | :---: | :---: | :---: | :---: |
| Épaule Pitch | **RS-04** | **120 N.m** | 40 N.m | 1420g |
| Épaule Roll | **RS-03** | 60 N.m | 20 N.m | 880g |
| Épaule Yaw | RS-02 | 17 N.m | 6 N.m | 405g |
| Coude Pitch | **RS-06** | **36 N.m** | 11 N.m | 621g |
| Poignet Roll | RS-00 | 14 N.m | 5 N.m | 310g |

**Capacité de portage (avec D-Hand +850g total, bras = ~3 kg):**

| Scénario | Couple requis | Moteur limitant | Capacité |
| :--- | :---: | :---: | :---: |
| **Bras tendu (frontal), continu** | ~33 N.m | Pitch RS-04 (40 N.m nom.) | ✅ **~5 kg** continu |
| **Bras tendu (frontal), pic** | ~55 N.m | Pitch RS-04 (120 N.m pic) | ✅ **~10 kg** pic |
| **Bras tendu (latéral), continu** | ~33 N.m | Roll RS-03 (20 N.m nom.) | ⚠️ **~2.5 kg** continu |
| **Bras plié 90°, sécurité** | ~30 N.m | Coude RS-06 (36 N.m nom.) | ✅ **~8-10 kg** sécurité |

> ⚠️ **Impact sur la masse du robot** : Cette configuration hybride amène la masse totale à **~40.4 kg** (avant allégement 3D). Le genou RS-04 opère à ~101% de sa capacité à 2-3 km/h, permettant une marche sécurisée à 2 km/h. Voir §9 et §11 pour la stratégie d'allégement 3D.

> Voir : [Analyse portage §3](./15a_Analyse_Locomotion_Baseline.md) | [Comparatif Option Hybride](./15b_Configurations_Moteurs.md)

---

## 5. Main — D-Hand Hybrid (4× XC430 + 4× XC330 + eFlesh)

**Décision : Architecture tandem déporté mixte, servos XC430 (force) et XC330 (précision) dans l'avant-bras.**

| Paramètre | Valeur |
| :--- | :--- |
| Servos | 4× **Dynamixel XC430-W240-T** (force) + 4× **XC330-T288-T** (précision) |
| Emplacement | Avant-bras (14.5 cm sur 22 cm dispo), 352g de moteurs |
| DOF actifs | 8 (Pouce ×2, Index ×2, Majeur, Annulaire, Auriculaire, Paume) |
| Force grip | **~175 N effectifs** (niveau Tesla Optimus) |
| Tactile | **Options T2 (eFlesh 3-axes)** sur la pulpe des doigts |
| Poids total (Main + Avant-bras) | **~850g** |
| Tendons | Dyneema Ø0.8mm-1.0mm, gaines PTFE, poulies CNC Ø8mm |
| Coût par main | ~**1 110 €** (Servos + BOM + eFlesh) |
| Protocole | Dynamixel 2.0 TTL, ROS 2, SDK Python |

**Évolution V4** : Phalanges Alu 7075 CNC (C500) pour durabilité maximale.

> Voir : [Étude Main Robotique](./21_Etude_Main_Robotique.md)

---

## 6. Matériaux — Stratégie Hybride

**Décision : Squelette aluminium CNC pour les zones de force, impression 3D partout ailleurs.**

| Zone | Matériau | Machine |
| :--- | :--- | :---: |
| Brackets hanches/genoux (RS-04) | **Alu 6061/7075 CNC** | C500 |
| Brackets épaules (RS-04/03) | **Alu 6061/7075 CNC** | C500 |
| Pivot cheville (cardan) | **Acier C45** (DIN 808) | Commerce |
| Tibia / avant-bras structure | **PA12-CF** ou Alu tube | Qidi/C500 |
| Pied / semelle | **PA12-CF** 100% | Qidi |
| Torse (structure interne) | **PA12-CF** 100% | Qidi |
| Coques extérieures | **PETG-CF** 40% gyroid | Qidi |
| Tête / boîtier capteurs | **PETG-CF** 60% | Qidi |
| Phalanges main V1 | **PA12-CF** | Qidi |
| Phalanges main V4 | **Alu 7075** | C500 |

---

## 7. Performances Globales Estimées

| Métrique | Estimation | Config |
| :--- | :---: | :---: |
| **Masse totale** | **~40.4 kg** | Cardan + Épaule Hybride (RS-04/03) + D-Hand |
| **DOF total** | 24 corps RobStride + 2×8 mains Dynamixel = **40 DOF actifs** | V1 complet |
| **Vitesse marche sécurisée** | **~2 km/h** (marge genou 120 N.m) | RS-04 genou à 101% à 2-3 km/h |
| **Vitesse marche max** | ~3 km/h (algo ZMP, pics transitoires ok) | RS-04 genou à 97→104% |
| **Vitesse course (V1 algo)** | ~3-4 km/h | Mid-foot strike (genou au pic) |
| **Vitesse course (V3 tirant genou)** | ~8-10 km/h | Mécanisme S2 (V3 future) |
| **Charge portage bras tendu** | **~5 kg continu, ~10 kg pic** | RS-04 épaule (×2.5 vs RS-03) |
| **Charge portage bras plié 90°** | **~8-10 kg sécurité, ~15 kg pic** | RS-06 coude |
| **Grip main (force)** | **~175 N effectifs** | Hybrid XC430/XC330 |
| **Autonomie** | ~4h | LiPo échangeable |

---

## 8. Points d'Attention V1

> [!WARNING]
> **⚠️ Genou RS-04 à ~101% de son pic à 2-3 km/h avec 40.4 kg.** Avec la masse ajustée grâce aux épaules hybrides (-1.08 kg vs Option D), le couple genou en marche normale atteint ~121 N.m vs 120 N.m pic RS-04. Conséquences pratiques :
> - **Vitesse sécurisée recommandée : 2 km/h** pour rester dans les limites nominales.
> - À 2-3 km/h : genou opère sur les **pics transitoires** (< 50 ms) — viable mais limites thermiques à surveiller.
> - **Priorité algorithmique n°1** : ZMP control + courbe de jerk + mid-foot strike pour lisser les impacts.
> - **Compromis assumé** : Le gain de portage (+5 kg frontal vs +2 kg ancestral) justifie cette contrainte.

> [!IMPORTANT]
> **✅ Coude RS-06 (upgrade RS-02)** : Le coude RS-06 permet un portage bras plié de 8-10 kg en continu (vs ~4.5 kg avec RS-02). C'est l'upgrade complémentaire indispensable aux RS-04 épaules.

> [!TIP]
> **Démarrer par le gripper.** Un gripper simple (1× STS3215, 30€) permet de valider le bus RS-00 du poignet et l'intégration mécanique de la main **avant** d'investir ~1 110€ dans la D-Hand Hybrid.

---

*Conclusions établies en Mars 2026. Architecture D-Bot V1 stabilisée — **Option Hybride complète** : RS-04 Pitch + RS-03 Roll épaules + RS-06 coude + Cardan DIN 808 + 2×RS-03 chevilles + D-Hand Hybrid. Masse de référence : ~40.4 kg.*

---

## 9. Bilan Masse Détaillé (Moteurs vs Structure)

### 9.1 Masse des Moteurs — Inventaire Complet

| Moteur | Rôle | Qté | Masse unit. | Masse totale |
| :--- | :--- | :---: | :---: | :---: |
| **RS-05** | Cou Pan + Tilt | 2 | 191g | **382g** |
| **RS-04** | Épaule Pitch (×2) + Hanche Pitch (×2) + Genou (×2) | 6 | 1420g | **8 520g** |
| **RS-03** | Épaule Roll (×2) + Hanche Roll (×2) + Hanche Yaw (×2) + Cheville Cardan (×4) | 10 | 880g | **8 800g** |
| **RS-06** | Coude (×2) | 2 | 621g | **1 242g** |
| **RS-02** | Épaule Yaw (×2) | 2 | 405g | **810g** |
| **RS-00** | Poignet Roll (×2) | 2 | 310g | **620g** |
| **TOTAL MOTEURS (24)** | | **24** | | **20 374g = 20.37 kg** |

### 9.2 Masse Structurelle Estimée

> La masse structurelle est estimée par déduction depuis la base K-Bot (34 kg total, 15.77 kg de moteurs → **18.23 kg de structure**), ajustée pour les éléments D-Bot spécifiques.

| Poste | Matériau envisagé | Masse estimée | Allégement possible |
| :--- | :--- | :---: | :---: |
| Torse + Bassin (structure interne) | PA12-CF (isogrid/sandwich) | ~3.5 kg | → 2.8 kg (−20%) |
| Fémurs D+G (cuisse) | PA12-CF sandwich ou carbone | ~1.5 kg | → 1.0-1.2 kg (−25%) |
| Tibias D+G | Tube carbone 3K Ø30mm | ~0.8 kg | → 0.5 kg (−38%) |
| Pieds D+G | PA12-CF 100% + semelle TPU | ~0.8 kg | → 0.6 kg (−25%) |
| Bras (humérus + avant-bras) ×2 | PA12-CF + alu | ~1.5 kg | → 1.2 kg (−20%) |
| Cardan DIN 808 ×2 + bielles | Acier C45 | ~0.6 kg | ✗ usiné — fixe |
| Brackets hanches/genoux | Alu 6061/7075 CNC | ~1.5 kg | → 1.1 kg (isogrid) |
| Brackets épaules | Alu 6061/7075 CNC | ~0.7 kg | → 0.5 kg (allégé) |
| Tête + cou (boîtier capteurs) | PETG-CF | ~0.4 kg | → 0.3 kg |
| Batterie 48V 10Ah (AT WEY NMC) | — | **2.3 kg** | ✗ fixe |
| Jetson Orin Nano 8GB | — | 0.3 kg | ✗ fixe |
| Spresense + électronique | — | 0.3 kg | ✗ fixe |
| OAK-D Pro FF | — | 0.091 kg | ✗ fixe |
| Unitree L2 LiDAR | — | 0.23 kg | ✗ fixe |
| D-Hand Hybrid ×2 | Servos + Dyneema | **1.7 kg** | ✗ fixe |
| Câblage, connecteurs, visserie | — | ~0.8 kg | → 0.6 kg (optimisé) |
| **TOTAL STRUCTUREL (estimé)** | | **~17.0 kg** | **→ ~13.5 kg (optimisé)** |

### 9.3 Masse Totale Robot — 3 Scénarios

| Scénario | Moteurs | Structure | **Total** | Impact genou 2-3 km/h |
| :--- | :---: | :---: | :---: | :---: |
| **A — Option D Révisée (2× RS-04 épaules)** | 21.45 kg | ~17.0 kg | **~41.5 kg** | ⚠️ ~125 N.m (104% de 120) |
| **B — Option Hybride (Adoptée)** | 20.37 kg | ~17.0 kg | **~40.4 kg** | ⚠️ ~121 N.m (~101%) |
| **C — Scénario B + allégement 3D** | 20.37 kg | ~14.0 kg | **~34-36 kg** | ✅ ~107 N.m (89%) — marche confortable |

> [!TIP]
> **Objectif cible réaliste** : Le scénario B + allégement modéré (structure à ~15 kg) amène le robot autour de **35-36 kg**. À cette masse, le genou RS-04 opère à ~85-90% de son pic à 2-3 km/h → **marche normale confortable et course envisageable sans compromis**.

---

## 10. Analyse : Épaule — RS-04 Pitch + RS-03 Roll (Config Hybride)

### 10.1 Justification Biomécanique

Le **Pitch** (lever le bras en avant) est l'axe le plus sollicité car il lutte contre la gravité sur la totalité de la longueur du bras :

```
τ_pitch (bras tendu + 5 kg payload) :
= bras seul : 3 kg × 9.81 × 0.30 m = 8.8 N.m
+ payload   : 5 kg × 9.81 × 0.60 m = 29.4 N.m
= 38.2 N.m → RS-04 nominal (40 N.m) = +5% marge ✅
→ RS-03 nominal (20 N.m)            = INSUFFISANT ❌
```

Le **Roll** (écarter le bras latéralement) est sollicité au maximum uniquement bras horizontal avec charge latérale — un usage moins fréquent :

```
τ_roll_max (bras écarté 90° + 5 kg) :
= 38.2 N.m (même calcul)
→ RS-04 nominal (40 N.m) : confortable ✅
→ RS-03 nominal (20 N.m) : marginal à 5 kg ⚠️ mais 60 N.m pic largement suffisant ✅
→ RS-03 : OK pour portage latéral ≤ 2 kg continu, 5 kg en pic
```

### 10.2 Comparatif des Options Épaule

| Config | Moteur Pitch | Moteur Roll | Portage frontal | Portage latéral | Masse épaules | Coût |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Option A (Abandonnée)** | RS-04 | RS-04 | 5 kg continu | 5 kg continu | **5 680g** | $560 |
| **Option B (hybride)** ⭐ | RS-04 | **RS-03** | 5 kg continu | **~2 kg continu, 5 kg pic** | **4 600g** | $530 |
| K-Bot original | RS-03 | RS-03 | ~2 kg continu | ~2 kg continu | 3 520g | $500 |

> **Économie Option B vs A** : −1 080g par robot, −$30, et la capacité frontale (le cas principal) est identique.

> [!NOTE]
> **Recommandation** : L'**Option B hybride (RS-04 Pitch + RS-03 Roll)** est le meilleur compromis. La quasi-totalité des tâches de manipulation domestique (saisir, porter, placer un objet) solicite le Pitch frontal. Le Roll latéral n'est sous contrainte maximale que lors de portage bras horizontal X tendus — un geste rare. Économiser 1 kg aux épaules a un impact direct sur le genou.

---

## 11. Stratégie Allégement — Impression 3D & Optimisation

L'objectif est d'atteindre la masse cible de **~35 kg** (±2 kg) pour que le genou RS-04 opère à **< 90%** de son pic à 2-3 km/h, déblocant une marche confortable et une course envisageable.

### 11.1 Leviers d'Allégement par Priorité

| Priorité | Pièce | Approche | Gain estimé | Difficulté |
| :---: | :--- | :--- | :---: | :---: |
| 🔴 **1** | **Tibias** | Tube carbone 3K Ø30mm (ou alu 2014) à la place de PA12-CF plein | −300g | Moyen |
| 🔴 **2** | **Fémurs** | Design sandwich carbone/mousse + isogrid CNC alu | −300-500g | Élevé |
| 🟠 **3** | **Brackets hanches/genoux** | Alu 7075 ajouré (toile de 5mm + nervures) | −400g | Moyen |
| 🟠 **4** | **Torse bas + bassin** | Isogrid PA12-CF (40% gyroid adaptatif) | −300g | Faible |
| 🟡 **5** | **Câblage** | Câbles ultra-flex silicone 26AWG (−30% poids vs silicone standard) | −100g | Faible |
| 🟡 **6** | **Pieds** | PA12-CF creux 30% gyroid (seule la semelle est pleine) | −150g | Faible |
| 🟢 **7** | **Visserie M4** | Titane EN 3.7164 pour les boulons moteurs (−60% masse) | −50-80g | Élevé |

> Gain total potentiel avec toutes ces optimisations : **−1.5 à −2.5 kg** sur la structure.

### 11.2 Impact sur les Marges de Marche

En combinant **Config Hybride B** (RS-03 Roll épaule) + **Allégement 2 kg structure** :

```
Masse cible : 40.4 - 2.0 = ~38.5 kg

τ_genou à 2-3 km/h :
= (38.5 / 39) × 117 N.m × 1.7 (dynamique)
= 0.987 × 117 = 115.5 N.m
→ Marge RS-04 : (120 - 115.5) / 120 = +3.8% ← marge confortable

τ_genou à 3-4 km/h :
= (38.5 / 39) × 68.8 × 2.2 (facteur dynamique rapide)
= 148 N.m → dépasse RS-04 → course : algorithme SEA ou mid-foot nécessaire
```

**Vitesse de marche maximale théorique à ~38.5 kg :**
```
v_max (marche sans phase de vol) ≈ 9.3 × (38.5/39)^-1 → ~9.5 km/h théorique
En pratique (marge thermique + contrôle) : ~4-5 km/h → BIEN meilleur que 2-3 km/h actuel
```

