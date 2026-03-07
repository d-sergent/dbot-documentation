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
| **Épaule** | **RS-03** (Pitch/Roll) + **RS-02** (Yaw) | 60 / 17 N.m | ✅ V1 |
| **Coude** | **RS-06** | 36 N.m | ✅ V1 |
| **Poignet Roll** | **RS-00** | 14 N.m | ✅ V1 |
| **Main** | **D-Hand Hybrid** (4× XC430 + 4× XC330 + tactile) | ~175 N grip | ✅ V1 |
| **Cou** | **RS-05** (×2) | 5.5 N.m | ✅ V1 |
| **Masse totale** | ~**39 kg** | — | Référence |
| **Vitesse marche** | ~**5-6 km/h** (pratique) | — | Estimé |
| **Course V1** | ~**4 km/h** (algo mid-foot) | — | V1 logiciel |

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

## 4. Bras — RS-03 / RS-02 / RS-00

**Décision : Architecture K-Bot conservée.**

| Articulation | Moteur | Couple |
| :--- | :---: | :---: |
| Épaule Pitch | RS-03 | 60 N.m |
| Épaule Roll | RS-03 | 60 N.m |
| Épaule Yaw | RS-02 | 17 N.m |
| Coude Pitch | RS-06 | 36 N.m |
| Poignet Roll | RS-00 | 14 N.m |

**Capacité de portage (avec D-Hand +434g) :**
- Bras tendu, continu : **~2 kg**
- Bras tendu, pic : **~5 kg**
- Bras plié (coude 90°), sécurité : **~10 kg**

> Voir : [Analyse portage §3](./15a_Analyse_Locomotion_Baseline.md) | [Mise à jour D-Hand](./15c_Revision_Cardan_39kg.md)

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
| Brackets épaules (RS-03) | **Alu 6061 CNC** | C500 |
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
| **Masse totale** | ~39.5 kg | Cardan + D-Hand Hybrid |
| **DOF total** | 28 (24 corps + 2 cou + 2×8 mains) | V1 complet |
| **Vitesse marche max** | ~5-6 km/h (pratique) | RS-04 genou limite |
| **Vitesse course (V1 algo)** | ~4 km/h | Mid-foot strike |
| **Vitesse course (V3 tirant)** | ~8-10 km/h | Mécanisme S2 |
| **Charge portage bras tendu** | ~2 kg continu, ~4 kg pic | RS-03 épaule |
| **Grip main (force)** | **~175 N effectifs** | Hybrid XC430/XC330 |
| **Autonomie** | ~4h | LiPo échangeable |

---

## 8. Points d'Attention V1

> [!WARNING]
> **Genou RS-04 à 97% de son pic à 2-3 km/h.** Nécessite un algorithme de marche soigné (ZMP control, courbe de jerk) pour éviter les pics thermiques. Priorité algorithmique n°1.

> [!WARNING]
> **Coude RS-02 limité à 4.5 kg bras plié** avec la D-Hand Hybrid (+850g au bout du bras). Upgrade RS-06 recommandé si portage lourd bras plié > 4-5 kg est requis.

> [!TIP]
> **Démarrer par le gripper.** Un gripper simple (1× STS3215, 30€) permet de valider le bus RS-00 du poignet et l'intégration mécanique de la main **avant** d'investir ~1 110€ dans la D-Hand Hybrid.

---

*Conclusions établies en Mars 2026. Architecture D-Bot V1 stabilisée.*
