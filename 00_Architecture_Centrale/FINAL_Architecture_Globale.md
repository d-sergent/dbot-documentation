# 16 — Conclusions : Architecture Finale du D-Bot

Ce document présente uniquement les **décisions définitives** pour le D-Bot. Il synthétise l'ensemble des études et analyses précédentes.

> **Pour comprendre le raisonnement derrière chaque choix**, consultez la [Série Biomécanique 15a→15g](../01_Mecanique_et_Chassis/STUDY_Analyse_Biomecanique.md).

---

## Résumé Exécutif

| Zone | Solution Retenue | Couple / Perf | Statut |
| :--- | :--- | :---: | :---: |
| **Cheville Pitch + Roll** | Cardan DIN 808 + **2× RS-03** + bielles | 120 N.m | ✅ V1 |
| **Genou Pitch** | **RS-04** + Courroie GT3 2.5:1 (S6) | 300 N.m | ✅ V1 |
| **Hanche Pitch + Yaw** | **RS-04** (pitch) + **RS-03** (roll/yaw) | 120 / 60 N.m | ✅ V1 |
| **Épaule** | **RS-04** (Pitch) + **RS-03** (Roll) + **RS-02** (Yaw) | 120 / 60 / 17 N.m | ✅ V1 |
| **Coude Pitch** | **RS-03** | 60 N.m | ✅ V1 |
| **Supination Avant-Bras** | **RS-02** | 17 N.m | 🆕 V1 (Doc 22b) |
| **Poignet Pitch** | **RS-00** | 5 N.m | ✅ V1 |
| **Waist Yaw (Taille)** | **RS-06** | 36 N.m | ✅ Acheté & Monté |
| **Main** | **D-Hand Hybrid Premium** (5× STS3250 + 3× HL-3915 + tactile) | ~438 N pic / 140 N nom. | ✅ V1 |
| **Cou** | **RS-05** (×2) | 5.5 N.m | ✅ Achetés & Montés |
| **Masse totale** | **40.4 kg** | Squelette Alu + Hybrid Épaules + D-Hand + GT3 + Waist | Référence |
| **Vitesse marche** | **~5 km/h** (marge XL) | — | Estimé |
| **Course V1** | **~6-8 km/h** (mid-foot strike) | — | V1 logiciel |

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

> Voir : [Étude Cheville Cardan](../01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Cheville_Cardan.md) | [Analyse 40.2 kg](../01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Revision_Cardan.md)

---

## 2. Genou — RS-04 + Courroie GT3 (S6)

**Décision V1 : RS-04 (120 N.m) + Réduction GT3 2.5:1 = 300 N.m effectifs.**

| Scénario | Couple Requis | Couple Dispo (S6) | Verdict |
| :--- | :---: | :---: | :---: |
| Marche lente (< 1 km/h) | ~69 N.m | **300 N.m** | ✅ +330% (Marges XL) |
| Marche normale (2-3 km/h) | ~117 N.m | **300 N.m** | ✅ +156% (Sécurisé) |
| Course pic (172 N.m requis) | **172 N.m** | **300 N.m** | ✅ **Sécurisé** (Marge 42%) |
| Course mid-foot (4 km/h) | **~103 N.m** | **300 N.m** | ✅ **Ultra-Margé** (65%) |

**Évolution planifiée :**
- **V2** (~6 mois) : Tibia en lame carbone flexible pour absorption passive des chocs.
- **V3** (~1 an) : Mécanisme "Atlas" à tirant haute-vitesse pour course > 10 km/h.

> Voir : [Étude Genou — Analyse & Solution GT3](../01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Genou_Cinematique.md) | [Alternatives Transmission](./15h_Alternatives_Transmission_Genou.md)

---

## 3. Hanches — RS-04 (Pitch) + RS-03 (Roll + Yaw) en F-A-R

**Décision : Architecture séquentielle F-A-R (Pitch→Roll→Yaw) — standard Gen2 (Figure 02, Unitree G1).**

| Maillon | Axe | Moteur | Couple Pic | Couple Requis (39 kg, dyn.) | Marge |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | **Hanche Pitch** | RS-04 | 120 N.m | ~19 N.m | **+530%** ✅ |
| **2** | **Hanche Roll** | RS-03 | 60 N.m | ~20 N.m | **+200%** ✅ |
| **3** | **Hanche Yaw** | RS-03 | 60 N.m | ~15 N.m | **+300%** ✅ |

**Changement vs architecture antérieure :**
- Ancien ordre **R-A-F** (Yaw→Roll→Pitch) remplacé par l'ordre **F-A-R** (Pitch→Roll→Yaw).
- Le RS-04 Pitch est maintenant en **Maillon 1** (fixé au bassin/bas du torse), Roll en 2, Yaw en 3 (vers la cuisse).
- Packaging anatomique amélioré, bassin plus fin, proportions Gen2.
- **GT3 étudiée et rejetée** : le RS-04 Pitch en direct drive ne dépasse jamais 25% de ses capacités en locomotion — aucun renfort mécanique nécessaire.

> Voir : [26 — Étude Bloc Pelvien Hanche](../01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Bloc_Pelvien_Hanche.md)

---

## 4. Bras — RS-04 / RS-03 / RS-02 / RS-00 ⭐ UPGRADE HYBRIDE

**Décision : Épaule Pitch RS-04 + Épaule Roll RS-03 + Coude RS-03 + Supination RS-02 + Poignet RS-00 (Architecture "Forearm Supination" — Biomimétique Tesla Optimus Gen 3).**

> 🆕 **Changement vs K-Bot** : L'épaule Pitch passe de RS-03 (60 N.m, 880g) à **RS-04 (120 N.m, 1420g)** pour ×2.5 de portage frontal. L'épaule Roll reste en **RS-03** (suffisant en latéral). Le coude passe de RS-02 (17 N.m) à **RS-03 (60 N.m)** pour ×3.5 de flexion (décision validée fin mai 2026 pour doubler la capacité de portage à 4.3 kg continu). Un **RS-02 de Supination** est ajouté directement après le RS-03 : il fait pivoter l'avant-bras entier (architecture biomimétique, voir [Doc 22b](../01_Mecanique_et_Chassis/Bras_et_Mains/STUDY_Poignet_Optimus.md)). Le **RS-00** est redéfini uniquement comme moteur de **Poignet Pitch** (extrémité distale).

| Articulation | Moteur | Couple Pic | Couple Nom. | Masse | Notes |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Épaule Pitch | **RS-04** | **120 N.m** | 40 N.m | 1420g | |
| Épaule Roll | **RS-03** | 60 N.m | 20 N.m | 880g | |
| Épaule Yaw | **RS-02** | 17 N.m | 6 N.m | 405g | |
| Coude Pitch | **RS-03** | **60 N.m** | 20 N.m | 880g | |
| **Supination Avant-Bras** | **RS-02** | **17 N.m** | 6 N.m | 405g | 🆕 Biomimétique (Doc 22b) |
| Poignet Pitch | **RS-00** | 14 N.m | 5 N.m | 310g | (Pitch uniquement) |

**Capacité de portage (avec D-Hand +850g total, bras = ~3 kg) — 1 bras :**

| Scénario | Couple requis | Moteur limitant | Capacité |
| :--- | :---: | :---: | :---: |
| **Bras tendu (frontal), continu** | ~33 N.m | Pitch RS-04 (40 N.m nom.) | ✅ **~5 kg** continu |
| **Bras tendu (frontal), pic** | ~55 N.m | Pitch RS-04 (120 N.m pic) | ✅ **~10 kg** pic |
| **Bras plié 90°, sécurité** | ~30 N.m | Coude **RS-03** (20 N.m nom.) | ✅ **~14-16 kg** sécurité |

> [!TIP]
> **Portage à 2 bras (charge symétrique)** : chaque moteur ne porte que la moitié de la charge. Les capacités sont doublées : ~**10 kg continu** bras tendus frontaux, ~**16-20 kg continu** bras pliés à 90°. La limite devient alors l'équilibre du robot (centre de gravité) et la tenue du genou (GT3 → 300 N.m), pas les moteurs de bras.

> ⚠️ **Impact sur la masse du robot** : L'activation de la taille en RS-06 et le coude en RS-03 amènent la masse totale à **~40.4 kg** (avant allégement 3D, LiDAR V2 décompté). Le genou RS-04 opère à ~100% de sa capacité à 2-3 km/h, permettant une marche sécurisée à 2 km/h. Voir §9 et §11 pour la stratégie d'allégement 3D.

### 🔮 Évolution Future — GT3 Coude (Non déployée en V1)

> [!NOTE]
> **Cette évolution n'est pas prévue pour la V1.** Elle est documentée ici pour tracer le cheminement de réflexion et guider une future itération si les besoins opérationnels l'exigent.

Par analogie avec la **Solution S6 GT3 du genou** (RS-04 remonté dans le fémur → 300 N.m), il serait possible d'appliquer le même principe au coude :

**Principe** : Relocaliser le RS-03 depuis le coude vers **l'humérus** (zone entre épaule et coude), et le relier à l'axe du coude par une courroie GT3. L'avant-bras (qui contient les 16 servomoteurs Feetech de la D-Hand) n'est **pas concerné** par cet encombrement.

```
ARCHITECTURE GT3 COUDE (Évolution V3) :

[ÉPAULE]
   │
[HUMÉRUS] — RS-03 Coude RELOCALISÉ + Pignon petit
   │          ← Courroie GT3 9mm (~200mm entraxe)
[COUDE]   — Grand pignon = AXE COUDE (remplace RS-03 direct)
   │
[AVANT-BRAS] — 16× Servos Feetech D-Hand (inchangé)
```

**Bénéfices calculés (ratio 2:1) :**

| Paramètre | RS-03 Direct (V1) | GT3 2:1 (V3) |
|:---|:---:|:---:|
| **Couple coude nominal** | 20 N.m | **40 N.m** (+100%) |
| **Couple coude pic** | 60 N.m | **120 N.m** |
| **Portage bras plié, 1 bras** | ~14-16 kg | **~30 kg continu** |
| **Portage bras plié, 2 bras** | ~28-32 kg | **~60 kg continu** |
| **Masse retirée du coude** | 0g | −880g (RS-03) + 160g (GT3) = **−720g** distaux ⭐ |
| **Coût** | 0€ | ~53€ (même BOM que GT3 genou) |

> La réduction de masse distale (−720g au coude) améliore aussi la dynamique des gestes rapides et réduit la sollicitation du RS-04 Pitch lors des accélérations du bras.

**Raison du report en V3** : absence de déficit critique de couple (RS-03 à ~50% en pic pour 10 kg, non problématique en usage courant). La complexité mécanique n'est pas justifiée avant validation des cas d'usage opérationnels concrets.


> Voir : [Analyse portage §3](./15a_Analyse_Locomotion_Baseline.md) | [Comparatif Option Hybride](./15b_Configurations_Moteurs.md)

---

## 5. Main — D-Hand Hybrid Premium (5× STS3250 + 3× HL-3915 + eFlesh)

**Décision : Architecture tandem déporté mixte, servos STS3250 (force) et HL-3915 (précision) dans l'avant-bras.**

| Paramètre | Valeur |
| :--- | :--- |
| Servos | 5× **Feetech STS3250** (force) + 3× **HL-3915** (précision/force matérielle) |
| Emplacement | Avant-bras (14.5 cm sur 20 cm dispo), 480g de moteurs |
| DOF actifs | 8 (Pouce ×2, Index ×2, Majeur, Annulaire, Auriculaire, Paume) |
| Force grip | **~438 N pic / 140 N continu** (niveau Tesla Optimus Gen 2) |
| Tactile | **Options T2 (eFlesh 3-axes)** sur la pulpe des doigts |
| Poids total (Main + Avant-bras) | **~913g** |
| Tendons | Dyneema DM20 Ø1.0mm, gaines PTFE, poulies CNC Ø12mm (au fond de gorge) |
| Coût par main | ~**1 110 €** (Servos + BOM + eFlesh) |
| Protocole | SCServo TTL, ROS 2, SDK SCServo |

**Évolution V4** : Phalanges Alu 7075 CNC (C500) pour durabilité maximale.

> Voir : [Étude Main Robotique](../01_Mecanique_et_Chassis/Bras_et_Mains/00_Archives_Recherche/STUDY_Main_D_Hand.md)

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
| **Masse totale** | **40.4 kg** | Squelette Alu + Hybrid Épaules + D-Hand + GT3 + Waist |
| **DOF total** | 27 corps RobStride + 16 mains Feetech = **43 DOF actifs** | V1 complet |
| **Vitesse marche sécurisée** | **~5 km/h** (à vide) | Marge genou 300 N.m |
| **Vitesse marche max** | **~7 km/h** | Limite physique RS-04 (Vitesse) |
| **Vitesse course (V1 algo)** | **~6-8 km/h** | Marge couple XL (Course pic OK) |
| **Vitesse course (V3 tirant genou)** | ~10 km/h | Mécanisme future "Atlas" |
| **Charge utile (Portage marchant)**| **~20 kg** (à 2.5 km/h) | Utilisation genou ~65% (GT3) |
| **Charge utile (Bras tendu frontal)**| **~5 kg** (en continu) | Limite épaule RS-04 |
| **Charge utile (Bras plié 90°)** | **~14-16 kg** (sécurité) | Limite coude RS-03 |
| **Grip main (force)** | **~438 N pic / 140 N nom.** | Hybrid STS3250/HL-3915 |
| **Autonomie** | **~1.5h - 3h** | NMC 48V 10Ah (extensible ×2) |

---

## 8. Points d'Attention V1

> [!IMPORTANT]
> **✅ Genou RS-04 + GT3 (S6) :** L'ajout de la réduction 2.5:1 fait passer le couple de 120 N.m à **300 N.m**. À 2-3 km/h, le moteur n'est sollicité qu'à **~40%** de sa capacité.
> - **Vitesse sécurisée** : Augmentée à 5 km/h.
> - **Thermique** : Excellente dissipation prévue (faible courant requis en croisière).
> - **Stabilité** : Les marges de couple permettent de corriger les perturbations d'équilibre bien plus agressivement.

> [!IMPORTANT]
> **✅ Coude RS-03 + Supination RS-02 (Architecture Forearm Supination)** : Le coude RS-03 (60 N.m) assure la flexion du bras. Le RS-02 ajouté immédiatement après assure la rotation de l'avant-bras entier (Supination/Pronation). Cette architecture biomimétique (inspirée du Tesla Optimus Gen 3) élimine le crosstalk des tendons de la D-Hand, rend le poignet compact (RS-00 Pitch uniquement), et abaisse l'inertie distale. Voir [Doc 22b](../01_Mecanique_et_Chassis/Bras_et_Mains/STUDY_Poignet_Optimus.md).

> [!TIP]
> **Démarrer par le gripper.** Un gripper simple (1× STS3215, 30€) permet de valider le bus RS-00 du poignet et l'intégration mécanique de la main **avant** d'investir ~1 110€ dans la D-Hand Hybrid.

---

*Conclusions établies en Mars 2026, mises à jour Juin 2026. Architecture D-Bot V1 stabilisée — **Option Hybride + Forearm Supination** : RS-04 Pitch + RS-03 Roll épaules + RS-03 coude + **RS-02 Supination** + RS-00 Poignet Pitch + Cardan DIN 808 + 2×RS-03 chevilles + RS-06 Waist Yaw + D-Hand Hybrid Premium. **27 moteurs RobStride.** Masse moteurs de référence : 22.32 kg.*

---

## 9. Bilan Masse Détaillé (Moteurs vs Structure)

### 9.1 Masse des Moteurs — Inventaire Complet

| Moteur | Rôle | Qté | Masse unit. | Masse totale |
| :--- | :--- | :---: | :---: | :---: |
| **RS-05** | Cou Pan + Tilt | 2 | 191g | **382g** |
| **RS-04** | Épaule Pitch (×2) + Hanche Pitch (×2) + Genou (×2) | 6 | 1420g | **8 520g** |
| **RS-03** | Épaule Roll (×2) + Coude Pitch (×2) + Hanche Roll (×2) + Hanche Yaw (×2) + Cheville Cardan (×4) | 12 | 880g | **10 560g** |
| **RS-06** | Taille (Waist Yaw) | 1 | 621g | **621g** |
| **RS-02** | Épaule Yaw (×2) + **Supination Avant-Bras (×2)** 🆕 | 4 | 405g | **1 620g** |
| **RS-00** | Poignet Pitch (×2) | 2 | 310g | **620g** |
| **TOTAL MOTEURS (27)** | | **27** | | **22 323g = 22.32 kg** |

### 9.2 Masse Structurelle Estimée

> La masse structurelle est estimée par déduction depuis la base K-Bot (34 kg total, 15.77 kg de moteurs → **18.23 kg de structure**), ajustée pour les éléments D-Bot spécifiques.

| Poste | Matériau envisagé | Masse estimée | Allégement possible |
| :--- | :--- | :---: | :---: |
| Torse + Bassin (Squelette Alu CNC) | Tubes 6060 + Nœuds CNC | **2.36 kg** | ✗ usiné — fixe |
| Fémurs D+G (cuisse) | PA12-CF sandwich ou carbone | ~1.5 kg | → 1.0-1.2 kg (−25%) |
| Tibias D+G | Tube carbone 3K Ø30mm | ~0.8 kg | → 0.5 kg (−38%) |
| Pieds D+G | PA12-CF 100% + semelle TPU | ~0.8 kg | → 0.6 kg (−25%) |
| Bras (humérus + avant-bras) ×2 | PA12-CF + alu | ~1.5 kg | → 1.2 kg (−20%) |
| Cardan DIN 808 ×2 + bielles | Acier C45 | ~0.6 kg | ✗ usiné — fixe |
| Brackets hanches/genoux | Alu 6061/7075 CNC | ~1.5 kg | → 1.1 kg (isogrid) |
| Transmission Genou (GT3 ×2) | Courroies + Pignons Alu | **0.32 kg** | ✗ fixe |
| Brackets épaules | Alu 6061/7075 CNC | ~0.7 kg | → 0.5 kg (allégé) |
| Tête + cou (boîtier capteurs) | PETG-CF | ~0.4 kg | → 0.3 kg |
| Batterie 48V 10Ah (AT WEY NMC) | — | **2.3 kg** | ✗ fixe |
| Jetson Orin Nano 8GB | — | 0.3 kg | ✗ fixe |
| Spresense (Watchdog/IMU/FSR) | — | **0.20 kg** | ✗ fixe |
| OAK-D Pro FF | — | 0.091 kg | ✗ fixe |
| ~~Unitree L2 LiDAR~~ | — | ~~0.23 kg~~ | ⚠️ Repoussé **V2** |
| Audio (ReSpeaker + HP 5W) | — | **0.05 kg** | 🆕 Simplifié |
| D-Hand Hybrid ×2 | Servos + Dyneema + Structure | **1.57 kg** | ✗ fixe |
| Câblage, connecteurs, visserie | — | ~0.7 kg | → 0.5 kg (optimisé) |
| **TOTAL STRUCTUREL (estimé)** | | **~15.96 kg** | **→ ~12.46 kg (optimisé)** |

### 9.3 Masse Totale Robot — 3 Scénarios

> 🆕 **Mise à jour Mai 2026** : Ajout de 2× RS-02 Supination (+0.81 kg moteurs) suite à la décision de l'architecture Forearm Supination (Doc 22b).

| Scénario | Moteurs | Structure | **Total** | Impact genou 2-3 km/h |
| :--- | :---: | :---: | :---: | :---: |
| **A — Option D Révisée (2× RS-04 épaules)** | 22.26 kg | ~17.0 kg | **~39.3 kg** | ✅ ~118/300 N.m (39%) |
| **B — Option Hybride (Adoptée)** | **22.32 kg** | ~18.08 kg | **~40.4 kg** | ✅ ~120/300 N.m (~40%) |
| **C — Scénario B + allégement 3D** | **22.32 kg** | ~14.58 kg | **~36.9 kg** | ✅ ~110/300 N.m (37%) — marge XL |

> [!NOTE]
> Le Scénario B converge désormais naturellement vers la cible officielle de **~40.4 kg** : l'intégration active du RS-06 à la taille (Waist Yaw) et du RS-03 aux coudes (+1.14 kg de motorisation totale) porte le total moteurs à 22.32 kg.

> [!TIP]
> **Objectif cible réaliste** : Le scénario C + allégement modéré (structure à ~14.6 kg) amène le robot autour de **36.9 kg**. À cette masse, le genou RS-04 opère avec une réserve de puissance monumentale (>60%) → **marche et course sans aucune contrainte thermique**.

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
Masse cible : 40.2 - 2.0 = ~38.2 kg

τ_genou à 2-3 km/h :
= (38.5 / 39) × 117 N.m × 1.7 (dynamique)
= 0.987 × 117 = 115.5 N.m
→ Marge RS-04 (avec GT3 300 N.m) : (300 - 115.5) / 300 = **+61%** ← réserve massive

τ_genou à 3-4 km/h (Course pic) :
= (38.5 / 39) × 68.8 × 2.2 (facteur dynamique rapide)
= 148 N.m → **✅ Marge GT3 : (300 - 148) / 300 = +50%**
→ La course est possible même **sans** mid-foot strike (148 < 300 N.m).
```

**Vitesse de marche maximale théorique à ~38.5 kg :**
```
v_max (marche sans phase de vol) ≈ 9.3 × (38.5/39)^-1 → ~9.5 km/h théorique
En pratique (marge thermique + contrôle) : ~4-5 km/h → BIEN meilleur que 2-3 km/h actuel
```

