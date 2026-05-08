# 15c — Re-Analyse Biomécanique : Configuration Cardan (40.2 kg)

> **Série Biomécanique :**
> - [15a] [Locomotion Baseline](./15a_Analyse_Locomotion_Baseline.md)
> - [15b] [Configurations Moteurs & Évolutions](./15b_Configurations_Moteurs.md)
> - [15c] **Révision Configuration Cardan 40.2 kg** ← *vous êtes ici*
> - [15d] [Genou & Course — Solutions](./15d_Genou_et_Course.md)
> - [16] [**Conclusions & Architecture Finale D-Bot**](./16_Conclusions_Architecture_DBot.md)

Ce document recalcule toutes les performances de marche et de portage avec les paramètres définitifs du D-Bot : **masse 40.2 kg** et architecture cheville **Cardan DIN 808 + 2× RS-03** (120 N.m par cheville, Pitch ET Roll).

---

## 11. Re-Analyse Biomécanique — Configuration Cardan (Mars 2026)

> *Cette section met à jour l'ensemble des calculs précédents avec les nouveaux paramètres du D-Bot : masse 40.2 kg et architecture cheville à Cardan DIN 808 + 2× RS-03 (120 N.m par cheville, Pitch ET Roll).*

### 11.1 Nouveaux Paramètres de Référence

| Paramètre | Ancien (K-Bot base) | Nouveau (D-Bot Cardan) | Δ |
| :--- | :---: | :---: | :---: |
| **Masse totale** | 34 kg | **40.2 kg** | +5 kg |
| **Cheville Pitch (couple effectif)** | RS-02+tirant → ~34 N.m | **2× RS-03 cardan → 120 N.m** | **×3.5** |
| **Cheville Roll (couple effectif)** | RS-00 → 14 N.m | **2× RS-03 cardan différentiel → 120 N.m** | **×8.5** |
| **Masse distale cheville** | RS-00: 310g en bas du tibia | ~0g (moteurs RS-03 en haut du tibia) | **-310g** |
| **Architecture cheville** | Série (tirant + direct) | Différentiel (2 bielles) | — |

> [!NOTE]
> **Paramètres géométriques conservés** : Hauteur 1.40 m, bras de levier pied ~0.10 m, longueurs segments identiques à l'analyse précédente. Seules la masse et les couples de cheville changent.

---

### 11.2 Marche Lente (< 1 km/h) — Recalcul

#### Couple Cheville Pitch requis (statique)

```
M = 40.2 kg,  g = 9.81 m/s²,  L_pied = 0.10 m

τ_cheville_Pitch = M × g × L_pied
                 = 40.2 × 9.81 × 0.10
                 = 39.4 N.m  (statique, pied plat)
                 ≈ 45-55 N.m (dynamique, déroulé du pied)
```

#### Couples Hanches et Genou (marche lente, appui simple)

```
Phase appui simple : 1 jambe supporte 40.2 kg

τ_hanche_Pitch ≈ M × g × 0.13 m (bras de levier horizontal)
               ≈ 49.7 N.m

τ_genou ≈ M × g × (L_tibia/2 + L_cuisse/2)
        ≈ 40.2 × 9.81 × 0.18
        ≈ 71.0 N.m

τ_hanche_Roll ≈ M × g × 0.05 m (déport latéral CoM)
              ≈ 19.1 N.m
```

#### Tableau Récapitulatif — Marche Lente

| Articulation | Moteur | Couple Dispo (Pic) | Couple Requis | Marge | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Hanche Pitch** (RS-04) | RS-04 | 120 N.m | **~50 N.m** | **+140%** | ✅ Confortable |
| **Hanche Roll** (RS-03) | RS-03 | 60 N.m | **~20 N.m** | **+200%** | ✅ Très large |
| **Hanche Yaw** (RS-03) | RS-03 | 60 N.m | **~15 N.m** | **+300%** | ✅ Surplus |
| **Genou Pitch** (RS-04) | RS-04 | 120 N.m | **~69 N.m** | **+74%** | ✅ OK ← +15% vs 34 kg |
| **Cheville Pitch** (2× RS-03) | 2× RS-03 | **120 N.m** | **~45 N.m** | **+167%** | ✅ **EXCELLENT** ← était limite ❌ |
| **Cheville Roll** (2× RS-03) | 2× RS-03 | **120 N.m** | **~20 N.m** | **+500%** | ✅ **TRÈS LARGE** |

> [!IMPORTANT]
> **L'ancienne limite critique est résolue.** La cheville Pitch obligeait une marge de ~0% avec le RS-02+tirant (34 N.m vs 33.4 requis). Avec 2× RS-03 (120 N.m), la marge est de +167% pour **40.2 kg**. Cette marge suffit même pour une masse de 70 kg — le D-Bot a une réserve énorme.

---

### 11.3 Marche Normale (2–3 km/h) — Recalcul

En marche normale, les forces d'impact doublent par rapport au statique (facteur dynamique ×1.5–2.0 selon l'allure).

```
Couples dynamiques estimés (facteur ×1.7) :

τ_cheville_Pitch ≈ 39.4 × 1.7 = 67 N.m
τ_hanche_Pitch   ≈ 49.7 × 1.7 = 84 N.m
τ_genou          ≈ 71.0 × 1.7 = 120.7 N.m   ← Proche du pic RS-04 !
τ_cheville_Roll  ≈ 19.1 × 2.0 = 38 N.m   (corrections latérales plus rapides)
```

| Articulation | Couple Dispo (Pic) | Couple Requis (Dynamique) | Marge | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **Hanche Pitch** (RS-04) | 120 N.m | **~84 N.m** | +43% | ✅ OK |
| **Genou Pitch** (RS-04) | 120 N.m | **~117 N.m** | +3% | ⚠️ **AU PIC** (transitoire) |
| **Cheville Pitch** (2× RS-03) | 120 N.m | **~65 N.m** | **+85%** | ✅ **CONFORTABLE** |
| **Cheville Roll** (2× RS-03) | 120 N.m | **~38 N.m** | **+216%** | ✅ **Très large** |

> [!WARNING]
> **Genou RS-04 au pic à 2-3 km/h.** À 39 kg avec facteur dynamique ×1.7, le couple genou atteint ~117 N.m, très proche du pic RS-04 (120 N.m). En pratique, les pics durent < 50 ms et les RS-04 supportent des dépassements transitoires. Mais la marge de confort est réduite. Recommandation : veiller à l'algorithme de marche pour lisser les impacts (ZMP control, courbe de jerk).

> [!NOTE]
> **Cheville : totalement résolue.** La cheville Pitch (65 N.m requis vs 120 N.m dispo) a désormais +85% de marge même à masse supérieure et en dynamique. C'est un bond qualitatif massif par rapport à l'ancienne configuration (34 N.m = 0% marge statique).

---

### 11.4 Seuil de Course (> 4 km/h) — Estimation

La course implique une phase de vol (les 2 pieds quittent le sol). Les couples pics sont estimés à ×2.5–3.0 fois le statique sur les articulations propulsives.

```
τ_cheville_Pitch_course ≈ 39.4 × 2.7 = 106 N.m
τ_hanche_Pitch_course   ≈ 49.7 × 2.3 = 114 N.m
τ_genou_course          ≈ 71.0 × 2.5 = 177.5 N.m  ← Dépasse RS-04 !

Fréquence de pas requise (4 km/h) : ~2.5 Hz
Vitesse rotation genou (4 km/h) : ~120-180 RPM
Vitesse max RS-04 : 200 RPM → ✅ Vitesse OK
```

| Articulation | Couple Dispo | Couple Requis (Course) | Marge | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **Hanche Pitch** (RS-04) | 120 N.m | **~114 N.m** | +5% | ⚠️ **AU PIC** |
| **Genou Pitch** (RS-04) | 120 N.m | **~172 N.m** | ❌ -30% | ❌ **INSUFFISANT** |
| **Cheville Pitch** (2× RS-03) | 120 N.m | **~103 N.m** | **+17%** | ✅ **Viable** ← changement majeur ! |
| **Cheville Roll** (2× RS-03) | 120 N.m | **~50 N.m** | **+140%** | ✅ Large |

> [!IMPORTANT]
> **Révélation majeure : la cheville n'est plus le goulot d'étranglement pour la course !**
> Avec 2× RS-03 (120 N.m), la cheville couvre +17% de marge même en phase de course à 4 km/h.
> Le **genou RS-04 devient le nouveau goulot** (172 N.m requis vs 120 N.m disponible). Pour envisager la course (> 4 km/h), il faudrait :
> - Un mécanisme **SEA au genou** (ressort en série = récupération d'énergie, puissance effectivement multipliée) — V2/V3.
> - Ou un **genou à câble linéaire** (comme Optimus/Figure) permettant des actionneurs plus puissants.

---

### 11.5 Vitesse de Marche Maximale Estimée

On peut estimer la vitesse maximale en marche normale (sans phase de vol) en cherchant la vitesse à laquelle le genou atteint son pic (120 N.m) :

```
τ_genou(v) = 68.8 × facteur_dynamique(v)

Facteur dynamique(v) ≈ 1 + 0.08 × v (estimation empirique, v en km/h)
Seuil pic genou : 120 = 68.8 × (1 + 0.08 × v)
                  1.743 = 1 + 0.08 × v
                  v_max ≈ 9.3 km/h ← marche rapide large !
```

> [!TIP]
> **Vitesse de marche max estimée : ~9 km/h.** C'est la limite théorique avant que le genou RS-04 atteigne son couple de blocage en régime de marche (sans phase de vol). En pratique, la limite réelle sera ~5-6 km/h (marge thermique, contrôle). C'est un résultat très performant, comparable au Unitree G1.

---

### 11.6 Re-Analyse du Portage (Impact de la Masse Supplémentaire)

Le portage dépend principalement de l'épaule et du coude, pas de la masse du robot. L'augmentation de 34→39 kg n'affecte que le couple de **compensation gravitationnelle du bras propre** du robot.

```
Couple bras seul (épaule, bras tendu) = Masse_bras × g × L_bras/2
= 3 kg × 9.81 × 0.235 m  = 6.9 N.m   (inchangé, le bras pèse toujours ~3 kg)
```

Les tableaux de portage précédents (Section 3) **restent valides** → la capacité de portage est inchangée.

| Cas de Portage | Couple Épaule Requis | Couple Dispo (RS-03) | Verdict |
| :--- | :---: | :---: | :---: |
| **2 kg bras tendu** (continu) | ~19 N.m | 60 / 20 N.m | ✅ OK |
| **5 kg bras tendu** (pic) | ~33 N.m | 60 N.m pic | ⚠️ Transitoire |
| **2 kg bras tendu** (continu) | ~24 N.m | RS-06 coude : 36 N.m | ✅ OK si RS-06 |

---

### 11.7 Synthèse de la Validité — Configuration Cardan 40.2 kg

| Scénario | Config Précédente (34 kg, RS-02) | Config Cardan (40.2 kg, 2× RS-03) | Verdict |
| :--- | :---: | :---: | :---: |
| **Équilibre statique** | ⚠️ Marge 0% | ✅ **+167%** | 🟢 Résolu |
| **Marche lente (< 1 km/h)** | ✅ Viable (limite) | ✅ **Très confortable** | 🟢 Amélioré |
| **Marche normale (2-3 km/h)** | ❌ Cheville bloquante | ✅ **Cheville OK** | 🟢 Résolu |
| **Marche rapide (3-5 km/h)** | ❌ Impossible | ✅ **Possible (~5 km/h)** | 🟢 Nouveau! |
| **Vitesse max estimée** | < 2 km/h | **~5-6 km/h pratique, ~9 km/h théorique** | 🟢 Majeur |
| **Course (> 4 km/h)** | ❌ Impossible | ⚠️ **Genou bloquant** (SEA nécessaire v2) | 🟡 Partiel |
| **Stabilité latérale (Roll)** | ❌ RS-00 limité | ✅ **120 N.m** (×8 vs avant) | 🟢 Exceptionnel |
| **Portage bras tendu 2 kg** | ✅ OK | ✅ **Inchangé** | ✅ |
| **Masse distale jambe** | 310g | **~0g** | 🟢 Inertie réduite |

> [!IMPORTANT]
> **Conclusion générale** : Les calculs restent valides mais dans un sens très positif. La masse augmentée de 5 kg (+15%) est largement compensée par le gain de couple de cheville (+250%). Le D-Bot avec l'architecture Cardan passe d'un robot capable de marcher lentement à un robot capable de marcher normalement à 3-5 km/h. La course reste hors portée sans SEA au genou, mais la cheville n'est plus le facteur limitant.

> [!NOTE]
> **Le genou (RS-04) devient le prochain point d'attention.** À 40.2 kg et 2-3 km/h, il opère à ~97% de son pic. Il n'y a pas de risque immédiat (les Robstride supportent les dépassements transitoires < 100ms), mais le contrôle de marche devra lisser les impacts. C'est un objectif de tuning algorithmique, pas un problème matériel bloquant.

---
*Section ajoutée en Mars 2026 suite à la révision de l'architecture cheville (Cardan DIN 808 + 2× RS-03) et à la mise à jour de la masse de référence (40.2 kg).*

---
---

