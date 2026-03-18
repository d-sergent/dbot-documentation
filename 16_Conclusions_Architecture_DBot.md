# 16 — Conclusions : Architecture Finale du D-Bot

Ce document présente uniquement les **décisions définitives** pour le D-Bot. Il synthétise l'ensemble des études et analyses précédentes.

> **Pour comprendre le raisonnement derrière chaque choix**, consultez la [Série Biomécanique 15a→15d](./15_Analyse_Biomecanique.md).

---

## Résumé Exécutif

| Zone | Solution Retenue | Couple / Perf | Statut |
| :--- | :--- | :---: | :---: |
| **Cheville Pitch + Roll** | Cardan DIN 808 + **2× RS-03** + bielles | 120 N.m | ✅ V1 |
| **Genou Pitch** | **RS-04** + algo mid-foot strike | 120 N.m | ✅ V1 |
| **Hanche Pitch + Yaw** | **RS-04** (pitch) + **RS-03** (roll/yaw) | 120 / 60 N.m | ✅ V1 |
| **Épaule** | **RS-04** (Pitch/Roll) + **RS-02** (Yaw) | 120 / 17 N.m | ✅ V1 |
| **Coude** | **RS-06** | 36 N.m | ✅ V1 |
| **Poignet Roll** | **RS-00** | 14 N.m | ✅ V1 |
| **Main** | **D-Hand Hybrid** (4× XC430 + 4× XC330 + tactile) | ~175 N grip | ✅ V1 |
| **Cou** | **RS-05** (×2) | 5.5 N.m | ✅ V1 |
| **Masse totale** | ~**41.5 kg** | — | Référence |
| **Vitesse marche** | ~**2-3 km/h** (pratique sécurisée) | — | Estimé |
| **Course V1** | ~**4 km/h** (algo mid-foot, transitoires) | — | V1 logiciel |

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

## 4. Bras — RS-04 / RS-06 / RS-02 / RS-00 ⭐ UPGRADE MAXIMAL

**Décision : Épaules RS-04 + Coude RS-06 (Option D Révisée — Portage Maximal).**

> 🆕 **Changement vs K-Bot** : L'épaule passe de RS-03 (60 N.m, 880g) à **RS-04 (120 N.m, 1420g)** pour ×2 de portage. Le coude passe de RS-02 (17 N.m) à **RS-06 (36 N.m)** pour ×2 de flexion chargée. Ce choix implique +2.16 kg aux épaules et +0.43 kg aux coudes (voir impact masse §7).

| Articulation | Moteur | Couple Pic | Couple Nom. | Masse |
| :--- | :---: | :---: | :---: | :---: |
| Épaule Pitch | **RS-04** | **120 N.m** | 40 N.m | 1420g |
| Épaule Roll | **RS-04** | **120 N.m** | 40 N.m | 1420g |
| Épaule Yaw | RS-02 | 17 N.m | 6 N.m | 405g |
| Coude Pitch | **RS-06** | **36 N.m** | 11 N.m | 621g |
| Poignet Roll | RS-00 | 14 N.m | 5 N.m | 310g |

**Capacité de portage (avec D-Hand +850g total, bras = ~3 kg):**

| Scénario | Couple requis | Moteur limitant | Capacité |
| :--- | :---: | :---: | :---: |
| **Bras tendu, continu** (épaule limite) | ~33 N.m | RS-04 (40 N.m nom.) | ✅ **~5 kg** continu |
| **Bras tendu, pic** | ~55 N.m | RS-04 (120 N.m pic) | ✅ **~10 kg** pic |
| **Bras plié 90°, sécurité** (coude limite) | ~30 N.m | RS-06 (36 N.m nom.) | ✅ **~8-10 kg** sécurité |
| **Bras plié 90°, pic** | ~55 N.m | RS-06 (36 N.m pic) | ⚠️ **~15 kg** théorique |

> ⚠️ **Impact sur la masse du robot** : Les RS-04 épaules (+2160g vs RS-03) portent la masse totale à **~41.5 kg** (vs 39.5 kg avec RS-03). Voir §7 et §8 pour les conséquences sur la marche.

> Voir : [Analyse portage §3](./15a_Analyse_Locomotion_Baseline.md) | [Options A2/D (15b)](./15b_Configurations_Moteurs.md)

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
| Brackets épaules (RS-04) | **Alu 6061/7075 CNC** | C500 |
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
| **Masse totale** | **~41.5 kg** | Cardan + RS-04 épaules + D-Hand Hybrid |
| **DOF total** | 24 corps RobStride + 2×8 mains Dynamixel = **40 DOF actifs** | V1 complet |
| **Vitesse marche sécurisée** | **~2 km/h** (marge genou 120 N.m) | RS-04 genou à 104% à 2-3 km/h |
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
> **⚠️ Genou RS-04 à ~104% de son pic à 2-3 km/h avec 41.5 kg.** Avec la masse accrue (+2.16 kg aux épaules vs RS-03), le couple genou en marche normale atteint ~125 N.m vs 120 N.m pic RS-04. Conséquences pratiques :
> - **Vitesse sécurisée recommandée : 1.5-2 km/h** pour rester dans les limites nominales.
> - À 2-3 km/h : genou opère sur les **pics transitoires** (< 50 ms) que le RS-04 supporte en mode impulsionnel — viable mais limites thermiques à surveiller.
> - **Priorité algorithmique n°1** : ZMP control + courbe de jerk + mid-foot strike pour lisser les impacts.
> - **Compromis assumé** : Le gain de portage (+5 kg bras tendu vs +2 kg avec RS-03) justifie cette contrainte pour les phases statiques ou manipulation lourde. La marche rapide est secondaire dans l'usage robotique prévu.

> [!IMPORTANT]
> **✅ Coude RS-06 (upgrade RS-02)** : Le coude RS-06 permet un portage bras plié de 8-10 kg en continu (vs ~4.5 kg avec RS-02). C'est l'upgrade complémentaire indispensable aux RS-04 épaules.

> [!TIP]
> **Démarrer par le gripper.** Un gripper simple (1× STS3215, 30€) permet de valider le bus RS-00 du poignet et l'intégration mécanique de la main **avant** d'investir ~1 110€ dans la D-Hand Hybrid.

---

*Conclusions établies en Mars 2026. Architecture D-Bot V1 stabilisée — **Option D Révisée complète** : RS-04 épaules + RS-06 coude + Cardan DIN 808 + 2×RS-03 chevilles + D-Hand Hybrid. Masse de référence : ~41.5 kg.*
