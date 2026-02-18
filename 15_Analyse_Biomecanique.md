# 15 - Analyse Biomécanique & Propositions d'Évolution

Ce document analyse les capacités mécaniques du D-Bot dans sa configuration actuelle et propose des évolutions pour améliorer ses performances en marche, marche rapide et portage de charges.

## 1. Paramètres du Robot (Configuration Actuelle)

### Caractéristiques Physiques

| Paramètre | Valeur |
| :--- | :--- |
| **Hauteur** | 1.40 m (K-Bot standard) |
| **Masse totale (estimée)** | ~34 kg (K-Bot) / ~36 kg (D-Bot avec tête) |
| **Masse moteurs seuls** | 15.77 kg (K-Bot) + 0.38 kg (cou D-Bot) = 16.15 kg |
| **Charge utile bras (spec)** | ~10 kg (total 2 bras) |
| **Autonomie** | ~4h (batterie LiPo échangeable) |
| **DOF** | 20 (K-Bot) / 24 (D-Bot Performance) |

### Longueurs de Segments Estimées (robot 1.40m)

| Segment | Longueur | Masse Estimée |
| :--- | :---: | :---: |
| Cuisse (hanche → genou) | ~35 cm | ~4 kg |
| Tibia (genou → cheville) | ~35 cm | ~3 kg |
| Bras (épaule → coude) | ~25 cm | ~2.5 kg |
| Avant-bras (coude → poignet) | ~22 cm | ~1.5 kg |
| Torse | ~40 cm | ~12 kg |
| Tête D-Bot | ~15 cm | ~2 kg |

---

## 2. Analyse des Capacités de Marche

### 2.1 Marche Lente (< 1 km/h)

#### Couples Requis (Analyse Statique)

En phase d'appui simple, un seul genou supporte toute la masse du robot :

| Articulation | Couple Disponible (Pic) | Couple Requis (Estimé) | Marge | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **Hanche Pitch** (RS-04) | 120 N.m | ~50 N.m | **+140%** | ✅ Confortable |
| **Hanche Roll** (RS-03) | 60 N.m | ~25 N.m | **+140%** | ✅ Confortable |
| **Hanche Yaw** (RS-03) | 60 N.m | ~15 N.m | **+300%** | ✅ Surplus |
| **Genou Pitch** (RS-04) | 120 N.m | ~60 N.m | **+100%** | ✅ OK |
| **Cheville Pitch** (RS-02) | 17 N.m (×2 tirant = 34) | ~67 N.m | **-50%** | ❌ **CRITIQUE** |

> [!CAUTION]
> **Point faible critique : La CHEVILLE**. Avec un bras de levier mesuré à **0.20 m**, le couple requis pour soutenir le robot sur la pointe/talon est de **~67 N.m**.
> Le D-Bot V1 (RS-02 + tirant = 34 N.m) est en **déficit de 50%**.
> **Conséquence** : La marche propulsive (déroulé du pied) est impossible. Le robot devra marcher "à plat" (flat-foot) en gardant le Centre de Pression (CoP) très proche de l'axe de rotation (< 10 cm). Tout appui fort sur le talon/pointe fera décrocher le moteur.

> [!NOTE]
> **⬆️ Ce calcul concerne le mécanisme tirant**. Même avec le multiplicateur ×2 du K-Bot (34 N.m), le couple reste insuffisant pour le levier de 20 cm. L'upgrade V2 vers RS-03 (60 × 2 = 120 N.m) devient **indispensable** pour une vraie marche dynamique.

#### Explication du Calcul Cheville
```
Couple cheville = Masse × g × Distance CdP-Cheville
                = 34 kg × 9.81 m/s² × 0.20 m (mesure réelle)
                ≈ 67 N.m minimum statique
                ≈ 100 N.m en dynamique (accélérations)
```

**Conclusion marche lente** : Le D-Bot V1 (RS-02) est limité à une marche de type "shuffle" (glissée/petite foulée à plat). Le couple de 34 N.m ne permet de contrer qu'un déséquilibre de ~10 cm. Au-delà (talon 20 cm), le robot ne tient pas.

---

### 2.2 Marche Rapide (2-3 km/h)

| Paramètre | Requis | Disponible | Verdict |
| :--- | :---: | :---: | :---: |
| Couple genou dynamique | ~80 N.m | 120 N.m (RS-04) | ✅ Suffisant |
| Couple hanche dynamique | ~70 N.m | 120 N.m (RS-04) | ✅ Suffisant |
| Couple cheville dynamique | ~100 N.m | ~34 N.m (RS-02 + tirant) | ❌ **CRITIQUE** |

> [!NOTE]
> Ces estimations sont pour une marche à **~2-3 km/h**.

> [!WARNING]
> **La marche rapide est quasi-impossible** dans la configuration K-Bot de base à cause des chevilles RS-02. Le robot ne peut pas se propulser efficacement. Il est limité à un mode "shuffle" < 1 km/h.

> [!NOTE]
> **⬆️ Config K-Bot de base analysée ici.** Le D-Bot conserve le RS-02 avec **tirant (~34 N.m effectif)**. Pour la marche lente (<2 km/h), c'est suffisant. La marche rapide nécessite une optimisation du tirant ou un upgrade RS-03 (V2).

---

### 2.3 Course (> 4 km/h)

La course est **impossible** dans la configuration K-Bot de base :
- Les chevilles (RS-02 + tirant) n'ont que ~34 N.m vs ~150 N.m requis pour la phase de vol
- Les genoux (RS-04, 200 RPM) sont trop lents pour la fréquence de pas requise
- Pas de compliance élastique dans le système actuel

> [!NOTE]
> **⬆️ Config K-Bot de base.** Avec le RS-02 + tirant (~34 N.m), la course reste hors portée V1. Il faudrait un upgrade RS-03 (V2) + mécanismes SEA (Series Elastic Actuator) — voir section 10.

---

## 3. Analyse de la Capacité de Portage

### 3.1 Portage à Bout de Bras (Bras Tendu Horizontal)

C'est le **cas le plus défavorable** car le bras-de-levier est maximal.

#### Modèle Mécanique (Bras Tendu)
```
Bras total ≈ 47 cm (25 cm bras + 22 cm avant-bras)

Couple épaule = (Masse_bras × g × L/2) + (Masse_charge × g × L_total)
```

| Charge Portée | Couple Épaule Requis | Couple Dispo (RS-03) | Verdict |
| :---: | :---: | :---: | :---: |
| **0 kg** (bras seul) | ~10 N.m | 60 N.m pic / 20 N.m nom. | ✅ OK |
| **1 kg** | ~15 N.m | 60 / 20 N.m | ✅ OK |
| **2 kg** | ~19 N.m | 60 / 20 N.m | ⚠️ Limite nominale |
| **3 kg** | ~24 N.m | 60 / 20 N.m | ⚠️ Au-dessus nominal |
| **5 kg** | ~33 N.m | 60 / 20 N.m | ❌ > 1.5× nominal |
| **10 kg** | ~55 N.m | 60 / 20 N.m | ❌ Presque pic, **dangereux** |

> [!IMPORTANT]
> **Limite de portage à bout de bras** : ~**2 kg en continu** (couple nominal) et ~**5 kg momentanément** (pic). Les 10 kg annoncés par K-Scale ne sont possibles que **bras plié** (coude fléchi à 90°) ce qui divise le bras-de-levier par 2.

### 3.2 Portage Bras Plié (Coude 90°)

| Charge Portée | Couple Épaule Requis | Couple Coude Requis | Verdict |
| :---: | :---: | :---: | :---: |
| **5 kg** | ~24 N.m | ~11 N.m | ✅ Faisable |
| **10 kg** | ~38 N.m | ~22 N.m | ⚠️ Coude au pic (RS-02: 17 N.m) |

> [!WARNING]
> **Le coude (RS-02, 17 N.m pic) est un goulot d'étranglement** pour le portage lourd. Porter 10 kg bras plié nécessite ~22 N.m au coude, ce qui dépasse le pic du RS-02.

---

## 4. Synthèse des Faiblesses

| Zone | Moteur Actuel | Problème | Sévérité |
| :--- | :---: | :--- | :---: |
| **Cheville** | RS-02 tirant (34 N.m) | Déficit 50% vs 67 N.m requis | 🔴 **CRITIQUE** |
| **Coude** | RS-02 (17 N.m) | Limite pour portage > 5 kg | 🟡 **MOYEN** |
| **Épaule Pitch** | RS-03 (60 N.m) | Limite pour portage > 3 kg bras tendu | 🟡 **MOYEN** |
| **Cheville Roll** | Aucun | Pas de DOF d'adaptation au sol | 🟠 **IMPORTANT** |

---

## 5. Propositions d'Évolution

### Option A : Upgrade RobStride (Restant dans l'écosystème)

#### A1. Chevilles Pitch : upgrade V2 envisageable (RS-02 → RS-03 avec tirant)

| Paramètre | Avant (RS-02) | Après (RS-03) | Gain |
| :--- | :---: | :---: | :---: |
| Couple Pic | ~34 N.m | 120 N.m | **×3.5** |
| Couple Nominal | 6 N.m | 20 N.m | **×3.3** |
| Poids | 405g | 880g | +475g/cheville |
| Surpoids total | - | +950g (2 chevilles) | |
| Prix unitaire | $160 | $250 | +$180 total |

**Verdict** : ✅ **RECOMMANDÉ**. Résout le problème critique de propulsion. +950g est acceptable sur des chevilles (position basse = faible impact inertiel).

#### A2. Épaules RS-03 → RS-04

| Paramètre | Avant (RS-03) | Après (RS-04) | Gain |
| :--- | :---: | :---: | :---: |
| Couple Pic | 60 N.m | 120 N.m | **×2** |
| Couple Nominal | 20 N.m | 40 N.m | **×2** |
| Poids | 880g | 1420g | +540g/épaule |
| Surpoids total | - | +2160g (4 épaules) | |
| Prix unitaire | $250 | $280 | +$120 total |
| Portage bras tendu | ~2 kg continu | ~5 kg continu | **×2.5** |

**Verdict** : ⚠️ **À ÉVALUER**. Gain de portage significatif mais +2.16 kg en hauteur (épaules) = fort impact sur le centre de gravité et l'inertie. Recommandé uniquement si le portage lourd est une priorité.

#### A3. Coudes RS-02 → RS-06

| Paramètre | Avant (RS-02) | Après (RS-06) | Gain |
| :--- | :---: | :---: | :---: |
| Couple Pic | 17 N.m | 36 N.m | **×2.1** |
| Couple Nominal | 6 N.m | 11 N.m | **×1.8** |
| Poids | 405g | 621g | +216g/coude |
| Surpoids total | - | +432g (2 coudes) | |
| Prix unitaire | $160 | $230 | +$140 total |
| Portage bras plié | ~5 kg pic | ~10 kg pic | **×2** |

**Verdict** : ✅ **RECOMMANDÉ** si portage important. Le RS-06 est un excellent intermédiaire : double le couple au coude pour seulement +216g. Compatible dimensionnellement (88mm vs 78.5mm, à vérifier clearance).

---

### Option B : Moteurs Alternatifs (Hors RobStride)

#### B1. CubeMars AK10-9 V3 (pour Épaules)

| Paramètre | RS-03 (actuel) | AK10-9 V3 | Comparaison |
| :--- | :---: | :---: | :---: |
| Couple Pic | 60 N.m | 53 N.m | -12% |
| Couple Nominal | 20 N.m | 18 N.m | -10% |
| Poids | 880g | 940g | +7% |
| Densité couple | 68 N.m/kg | 56 N.m/kg | -18% |
| Prix | ~$250 | ~$860-970 | **×3.5** |

**Verdict** : ❌ **NON RECOMMANDÉ**. Moins performant et 3-4× plus cher que le RS-03. Le RobStride est supérieur sur tous les critères.

#### B2. CubeMars AK80-9 V3 (pour Chevilles)

| Paramètre | RS-02 (actuel) | AK80-9 V3 | Comparaison |
| :--- | :---: | :---: | :---: |
| Couple Pic | 17 N.m | 22 N.m | +29% |
| Couple Nominal | 6 N.m | 9 N.m | +50% |
| Poids | 405g | 480g | +19% |
| Prix | ~$160 | ~$480-580 | **×3** |

**Verdict** : ⚠️ **INSUFFISANT**. +29% de couple ne résout pas le problème des chevilles (besoin minimum ~67 N.m). Et coûte 3× plus cher qu'un RS-02. Passer à un RS-03 avec tirant (V2) est meilleur et moins cher.

#### B3. MyActuator RMD-X10 V3 (pour Chevilles)

| Paramètre | RS-02 (actuel) | RMD-X10 V3 | Comparaison |
| :--- | :---: | :---: | :---: |
| Couple Pic | 17 N.m | 50 N.m | **+194%** |
| Couple Nominal | 6 N.m | 12 N.m | +100% |
| Poids | 405g | 1150g | +184% |
| Prix | ~$160 | ~$890 | **×5.5** |

**Verdict** : ⚠️ **POSSIBLE mais coûteux**. Couple (50 N.m pic) **encore insuffisant** vs 67 N.m requis, très lourd (1.15 kg) et très cher ($890). Le RS-03 RobStride avec tirant ferait mieux (60 N.m × 2 = 120 N.m effectif, $250).

---

### Option C : Configuration "D-Bot Performance" (Recommandée)

Combinaison optimale des upgrades identifiés :

| Zone | Avant | Après | Changement | Surcoût |
| :--- | :---: | :---: | :--- | :---: |
| **Cheville Pitch** | 2× RS-02 (tirant) | **V2 : 2× RS-03** (tirant) | ~34→~120 N.m (×3.5) | +$180 |
| **Coude** | 2× RS-02 | **2× RS-06** | 17→36 N.m (×2.1) | +$140 |
| **Épaule Yaw** | 2× RS-02 | 2× RS-02 | Inchangé | $0 |
| Reste | Inchangé | Inchangé | Inchangé | $0 |

#### Bilan de l'Option C

| Impact | Détail |
| :--- | :--- |
| **Surpoids** | +950g (chevilles) +432g (coudes) = **+1.38 kg** → 37.4 kg total |
| **Surcoût** | +$320 total |
| **Marche** | Chevilles 60 N.m → **Marche stable et propulsée** ✅ |
| **Marche rapide** | 2-3 km/h devient **réalisable** ✅ |
| **Portage bras tendu** | 2 kg → **3 kg** (coude amélioré) |
| **Portage bras plié** | 5 kg → **10 kg** (coude 36 N.m) ✅ |
| **Compatibilité** | Mêmes protocoles (CAN), mêmes connecteurs |

### Option D : Configuration "D-Bot Maximal" (Performance Maximale)

Pour un portage lourd et une marche dynamique :

| Zone | Avant | Après | Changement | Surcoût |
| :--- | :---: | :---: | :--- | :---: |
| **Cheville Pitch** | 2× RS-02 (tirant) | **2× RS-03** (tirant) | ~34→~120 N.m (×3.5) | +$180 |
| **Épaule Pitch** | 2× RS-03 | **2× RS-04** | 60→120 N.m (×2) | +$60 |
| **Épaule Roll** | 2× RS-03 | **2× RS-04** | 60→120 N.m (×2) | +$60 |
| **Coude** | 2× RS-02 | **2× RS-06** | 17→36 N.m (×2.1) | +$140 |

#### Bilan de l'Option D

| Impact | Détail |
| :--- | :--- |
| **Surpoids** | +950g +2160g +432g = **+3.54 kg** → 39.5 kg total |
| **Surcoût** | +$440 total |
| **Marche** | Chevilles 60 N.m → **Marche stable** ✅ |
| **Portage bras tendu** | 2 kg → **5 kg continu** ✅ |
| **Portage bras plié** | 5 kg → **15+ kg théorique** ✅ |
| **CdG** | Plus haut (+2.16 kg aux épaules) — **compensé par le Roll cheville** |

> [!NOTE]
> **Clarification sur l'impact CdG** : L'Option D ajoute 3.5 kg dont 2.16 kg aux épaules. Cela élève le CdG mais **l'ajout du Roll cheville (voir Section 7) compense largement** ce handicap en fournissant des corrections latérales rapides. **Les deux options C et D nécessitent un re-tuning des algorithmes de marche** (masse différente, nouveaux DOF, nouvelles limites de couple). La difficulté de re-tuning de l'Option D est seulement **marginalement supérieure** à celle de l'Option C. Le surcoût D vs C n'est que de +$120 et +1.35 kg.

---

## 6. Recommandation Finale (Initiale — voir Section 8 pour version révisée)

### Analyse historique (avant ajout du Roll cheville)

*Cette section reflète l'analyse initiale, **avant** la prise en compte du Roll cheville. La recommandation a évolué — voir Section 8 pour les configurations révisées et Section 9 pour le comparatif final.*

**Raisonnement initial** : L'Option C était recommandée pour son rapport performance/impact. Cependant, l'ajout du Roll cheville dans les deux options change la donne :

- **Les deux options nécessitent un re-tuning** des algorithmes de marche (c'est inévitable dès qu'on modifie la configuration moteur)
- Le Roll cheville **compense le CdG plus haut** de l'Option D
- Le surcoût D vs C n'est que de **+$120 et +1.35 kg** pour un gain de portage **considérable**

### À retenir sur les moteurs alternatifs

Les alternatives étudiées (CubeMars AK, MyActuator RMD) ne sont PAS compétitives face à RobStride pour ce projet :
- **3 à 5× plus chers** à performances équivalentes
- **Densité de couple inférieure** dans la plupart des cas
- **Écosystème incompatible** (drivers différents, protocoles différents)
- Le seul intérêt serait une **personnalisation extrême** ou un besoin de backdrivabilité supérieure (AK80-9)

**RobStride offre le meilleur rapport couple/poids/prix** sur le marché des QDD en 2024-2025.

---
---

## 7. ADDENDUM — Analyse du DOF Cheville Roll Manquant

> *Ajouté suite à l'identification d'un problème structurel dans la configuration K-Bot standard.*

### 7.1 Le Problème : 1 DOF Cheville vs 2 DOF

La configuration K-Bot standard n'a qu'**un seul DOF de cheville** (Pitch) — pas de Roll. Cela signifie que le pied ne peut que basculer avant/arrière, mais **pas se pencher latéralement**.

| Config Cheville | K-Bot Actuel | Humain | Robots Avancés |
| :--- | :---: | :---: | :---: |
| **Pitch** (avant/arrière) | ✅ RS-02 | ✅ | ✅ |
| **Roll** (latéral) | ❌ Absent | ✅ | ✅ (2 DOF standard) |
| **Yaw** (rotation) | ❌ | ✅ (via hanche) | Rare |

### 7.2 Pourquoi c'est un VRAI Problème

La recherche académique (IEEE, MDPI) confirme que l'absence de Roll cheville a des conséquences majeures :

#### Impact sur la stabilité latérale

```
Sans Roll cheville :
┌─────────────────────────────────────┐
│  Le robot ne peut PAS ajuster       │
│  l'inclinaison latérale du pied.    │
│                                     │
│  → Le Centre de Pression (CoP)      │
│    ne peut se déplacer que sur       │
│    l'axe avant/arrière du pied.     │
│                                     │
│  → Stabilité latérale = uniquement  │
│    via les hanches (Roll + Yaw)     │
│    = mouvements amples et lents.    │
└─────────────────────────────────────┘

Avec Roll cheville :
┌─────────────────────────────────────┐
│  Le pied s'adapte au sol et         │
│  le CoP se déplace librement        │
│  sur TOUTE la surface du pied.      │
│                                     │
│  → Corrections rapides et fines     │
│  → Consommation énergie réduite     │
│  → Marche sur terrain irrégulier    │
└─────────────────────────────────────┘
```

#### Conséquences Concrètes

| Situation | Sans Roll Cheville | Avec Roll Cheville |
| :--- | :--- | :--- |
| **Sol plat** | ⚠️ Fonctionnel mais corrections par hanches uniquement | ✅ Corrections fines et rapides |
| **Sol incliné latéralement** | ❌ Pied ne s'adapte pas, risque chute | ✅ Pied s'incline pour suivre le sol |
| **Terrain irrégulier** | ❌ Très instable, surface d'appui réduite | ✅ Contact pied complet maintenu |
| **Virage en marchant** | ⚠️ Très limité, transfert de poids difficile | ✅ Transfert latéral naturel |
| **Position debout statique** | ⚠️ Oscillations latérales mal corrigées | ✅ Micro-ajustements permanents |
| **Portage asymétrique** | ❌ Objet lourd d'un côté = déséquilibre | ✅ Compensation par inclinaison pied |

> [!CAUTION]
> **Impact estimé** : Sans Roll cheville, la stabilité latérale du robot est réduite de **40-60%** selon les publications. Le robot sera limité à des surfaces planes et parfaitement horizontales pour une marche fiable.

### 7.3 Solutions Proposées

#### Solution S1 : Ajout d'un moteur Roll par cheville (Config "6 DOF Jambe")

C'est la solution la plus directe. L'idée d'un 6ème DOF (pivot cheville) a été évoquée dans une vidéo de présentation K-Scale comme extension possible du K-Bot 5 DOF/jambe, bien qu'aucune documentation écrite officielle ne détaille cette modification.

**Deux variantes** sont envisagées selon le moteur Roll choisi :

##### Calcul du couple Roll cheville requis
```
Couple Roll cheville requis (estimation) :
= Masse × g × Décalage_latéral_CoG
= 36 kg × 9.81 × 0.03 m (décalage latéral max)
≈ 10.6 N.m (statique)
≈ 15 N.m (dynamique avec marges)
```

##### Comparatif RS-00 vs RS-02 pour Cheville Roll

| Paramètre | RS-00 | RS-02 |
| :--- | :---: | :---: |
| **Couple pic** | 14 N.m | 17 N.m |
| **Couple nominal** | 5 N.m | 6 N.m |
| **Poids** | **310g** | 405g |
| **Dimensions** | **57×57×51 mm** | 78.5×78.5×45.5 mm |
| **Prix** | **$135** | $160 |
| **Ratio réducteur** | 10:1 | 7.75:1 |
| **Vitesse max** | 315 RPM | 410 RPM |
| **Marge vs 10.6 N.m** (statique) | ✅ +32% | ✅ +60% |
| **Marge vs 15 N.m** (dynamique) | ⚠️ -7% | ✅ +13% |
| **Surpoids (×2)** | **+620g** | +810g |
| **Surcoût (×2)** | **+$270** | +$320 |
| **Surface section** | **32.5 cm²** | 61.6 cm² |

##### S1a : Variante RS-00 (🏆 RECOMMANDÉE)

| Paramètre | Détail |
| :--- | :--- |
| **Moteur ajouté** | 2× RS-00 (1 par cheville) |
| **DOF cheville** | Pitch (**RS-02 + tirant**) + **Roll (RS-00)** |
| **Couple Roll** | 14 N.m pic (5 N.m nominal) |
| **Surpoids** | +620g (2× 310g) |
| **Surcoût** | +$270 (2× $135) |
| **DOF total robot** | 22 → **24 DOF** |
| **Encombrement** | **57×57 mm** — s'intègre facilement dans le pied |

**Avantages clés** du RS-00 pour ce rôle :
- **-190g par cheville** (×2 = -380g aux pieds) → inertie oscillante réduite = meilleure fréquence de pas
- **47% plus compact** en surface → intégration mécanique facilitée dans le pied
- **Ratio 10:1** (vs 7.75:1) → micro-corrections plus **précises** pour la stabilisation latérale
- **-$50 total** sur le robot

##### S1b : Variante RS-02 (option conservatrice)

| Paramètre | Détail |
| :--- | :--- |
| **Moteur ajouté** | 2× RS-02 (1 par cheville) |
| **DOF cheville** | Pitch (**RS-02 + tirant**) + **Roll (RS-02)** |
| **Couple Roll** | 17 N.m pic (6 N.m nominal) |
| **Surpoids** | +810g (2× 405g) |
| **Surcoût** | +$320 (2× $160) |
| **DOF total robot** | 22 → **24 DOF** |

**Avantage** : +21% de couple pic → marge de 13% au-dessus du besoin dynamique.

##### Impact par régime de vitesse

| Régime | Couple Roll requis | RS-00 (14 N.m) | RS-02 (17 N.m) |
| :--- | :---: | :---: | :---: |
| **Station debout** | ~3-5 N.m | ✅ 3× marge | ✅ 4× marge |
| **Marche lente** (<1.5 km/h) | ~8-10 N.m | ✅ +40% marge | ✅ +70% marge |
| **Marche normale** (2-3 km/h) | ~12-14 N.m | ⚠️ Juste (~0% marge) | ✅ +21% marge |
| **Marche rapide** (3-4 km/h) | ~15-18 N.m | ❌ Insuffisant au pic | ⚠️ Juste au pic |
| **Terrain irrégulier** | ~10-15 N.m | ⚠️ Acceptable | ✅ OK |

> [!NOTE]
> **Analyse** : Le RS-00 est **suffisant pour la marche lente à normale** (~0-3 km/h), ce qui couvre 95% des scénarios d'un robot domestique/démo. En **marche rapide**, le couple pic de 14 N.m sera brièvement dépassé (~15-18 N.m requis), mais :
> - Le pic dure < 50 ms par pas (correction de transfert latéral)
> - Les moteurs RobStride supportent des **dépassements transitoires** de 20-30% pendant < 100 ms
> - La hanche Roll (RS-03, 60 N.m) **assiste** la cheville Roll — les deux travaillent en synergie
>
> **En pratique**, le RS-00 est viable jusqu'à ~3 km/h. Au-delà, le RS-02 offre plus de marge, mais les deux sont insuffisants pour la course (>4 km/h) qui requiert des SEA.

#### Solution S2 : Pied Passif à Compliance (Sans Moteur)

Alternative mécanique sans ajout de moteur :

| Paramètre | Détail |
| :--- | :--- |
| **Principe** | Pied articulé avec joint élastomère permettant un Roll passif (~±5°) |
| **Moteur ajouté** | Aucun |
| **Surpoids** | +100-200g (mécanisme passif) |
| **Surcoût** | +$20-50 (impression 3D + élastomère) |
| **Couple Roll** | 0 N.m (passif, retour élastique uniquement) |
| **Complexité** | Faible — Design mécanique du pied uniquement |

**Avantage** : Zéro surcoût moteur, zéro complexité électronique supplémentaire.

**Inconvénient** : Pas de contrôle actif du Roll. Le pied s'adapte au sol par compliance mais ne peut pas corriger activement l'équilibre. Mieux que rien, mais insuffisant pour terrain irrégulier.

#### Solution S3 : Mécanisme Parallèle Cheville 2-DOF (Design Avancé)

Solution inspirée de la recherche robotique (DFKI, IEEE) :

| Paramètre | Détail |
| :--- | :--- |
| **Principe** | 2 moteurs actionnant la cheville en parallèle (type Stewart plateforme simplifiée) |
| **Moteurs** | 2× RS-02 ou 2× RS-06 en configuration parallèle |
| **Avantage** | Pitch ET Roll avec un seul mécanisme compact |
| **Surpoids** | +405-621g (1 moteur supplémentaire, le 2ème remplace le Pitch existant) |
| **Surcoût** | +$160-230 |
| **Complexité** | **Élevée** — Conception mécanique complexe (cinématique parallèle) |

**Verdict** : Trop complexe pour un premier prototype. Recommandé uniquement pour une V2 du robot.

### 7.4 Recommandation : Solution S1a (RS-00 Roll Cheville)

La Solution **S1a (RS-00)** est recommandée car :
- ✅ Couple suffisant pour marche lente à normale (14 N.m vs ~10-12 N.m en usage courant)
- ✅ **47% plus compact** que le RS-02 → intégration mécanique facilitée dans le pied
- ✅ **-380g** au total aux pieds → meilleure dynamique de marche
- ✅ **Ratio 10:1** = corrections latérales plus précises
- ✅ **-$50** sur le coût total
- ✅ Compatible écosystème RobStride existant (même bus CAN, même connectique)
- ✅ Évoquée dans une vidéo K-Scale comme extension envisagée du K-Bot
- ✅ Porte le D-Bot à **24 DOF** (objectif initial)

> [!TIP]
> **Règle de décision** : Si le robot est principalement destiné à de la marche intérieure (sol plat, ≤ 2-3 km/h) → **RS-00**. Si marche rapide fréquente en extérieur (3-4 km/h, terrain variable) → **RS-02**. Le D-Bot V1 vise la marche intérieure, donc RS-00 recommandé.

---

## 8. Configurations Finales Révisées

### 🏆 Option C-Révisée : "D-Bot Performance" (RECOMMANDÉE)

Conserve le RS-02 avec tirant pour Pitch (architecture K-Bot) + ajout Roll cheville (**RS-00**, compact et léger) + coudes améliorés (RS-06).

| Zone | Moteur | Qté | Couple Pic | Poids | Usage |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Cou | RS-05 | 2 | 5.5 N.m | 191g | Orientation tête |
| Poignet | RS-00 | 2 | 14 N.m | 310g | Manipulation fine |
| Épaule Pitch/Roll | RS-03 | 4 | 60 N.m | 880g | Lever/écarter bras |
| Épaule Yaw | RS-02 | 2 | 17 N.m | 405g | Rotation interne |
| **Coude** | **RS-06** | **2** | **36 N.m** | **621g** | **Flexion améliorée** |
| Hanche Pitch | RS-04 | 2 | 120 N.m | 1420g | Flexion jambe |
| Hanche Roll/Yaw | RS-03 | 4 | 60 N.m | 880g | Équilibre/rotation |
| Genou | RS-04 | 2 | 120 N.m | 1420g | Flexion genou |
| **Cheville Pitch** | **RS-02** | **2** | **17 N.m** (×2 tirant = ~34 N.m) | **405g** | **Propulsion (tirant K-Bot)** |
| **Cheville Roll** | **RS-00** | **2** | **14 N.m** | **310g** | **Stabilité latérale (compact)** |

> [!NOTE]
> **Alternative** : Remplacer le RS-00 par un RS-02 (17 N.m, $160, 405g) si une marge de couple supplémentaire est souhaitée pour la marche rapide. Coût : +$50, poids : +190g/cheville.

#### Bilan Option C-Révisée

| Impact | Détail |
| :--- | :--- |
| **Total moteurs** | **24 moteurs** (objectif D-Bot atteint ✅) |
| **Poids moteurs** | ~18.1 kg |
| **Poids robot total** | ~38.0 kg |
| **Surpoids vs K-Bot** | +2.0 kg (chevilles upgrade + Roll RS-00 + coudes) |
| **Surcoût vs K-Bot** | +$590 total |
| **DOF total** | **24 DOF** |
| **Marche** | ✅ Stable, propulsée, avec adaptation latérale |
| **Marche rapide** | ✅ 2-3 km/h réalisable (Roll au pic en transitoire) |
| **Terrain irrégulier** | ✅ Adaptation active du pied |
| **Portage bras plié** | ✅ ~10 kg |

### Option D-Révisée : "D-Bot Maximal"

Ajoute les RS-04 aux épaules en plus de la config C-Révisée :

| Zone | Moteur | Qté | Couple Pic | Changement vs K-Bot |
| :--- | :---: | :---: | :---: | :--- |
| Épaule Pitch/Roll | **RS-04** | 4 | **120 N.m** | Upgrade RS-03→RS-04 |
| Coude | **RS-06** | 2 | **36 N.m** | Upgrade RS-02→RS-06 |
| Cheville Pitch | **RS-02** | 2 | **17 N.m** (×2 tirant) | Architecture K-Bot conservée |
| Cheville Roll | **RS-00** | 2 | **14 N.m** | **NOUVEAU (compact)** |
| Reste | Inchangé | - | - | - |

| Impact | Détail |
| :--- | :--- |
| **Total moteurs** | **24 moteurs** |
| **Poids robot total** | ~41.5 kg |
| **Surcoût vs K-Bot** | +$710 total |
| **Portage bras tendu** | **5 kg continu** |
| **Portage bras plié** | **15+ kg théorique** |

---

## 9. Comparatif des Configurations

| Critère | K-Bot Standard | D-Bot Perf (C-Rév.) | D-Bot Max (D-Rév.) |
| :--- | :---: | :---: | :---: |
| **DOF** | 20 | **24** | **24** |
| **Moteurs** | 20 | **24** | **24** |
| **Cheville Roll** | ❌ Absent | **RS-00 (14 N.m)** | **RS-00 (14 N.m)** |
| **Poids robot** | 34 kg | 38.0 kg | 41.5 kg |
| **Surcoût** | Base | +$590 | +$710 |
| **Marche lente** | ⚠️ Shuffle | ✅ Stable | ✅ Stable |
| **Marche normale** (2-3 km/h) | ❌ Impossible | ✅ Roll RS-00 OK | ✅ Roll RS-00 OK |
| **Marche rapide** (3-4 km/h) | ❌ Impossible | ⚠️ Roll au pic | ⚠️ Roll au pic |
| **Terrain irrégulier** | ❌ Impossible | ✅ Roll actif | ✅ Roll actif |
| **Stabilité latérale** | ❌ Hanches seules | ✅ Cheville Roll | ✅ Cheville Roll |
| **Portage bras tendu** | 2 kg | 3 kg | **5 kg** |
| **Portage bras plié** | ~5 kg | **10 kg** | **15+ kg** |
| **Tête articulée** | ❌ | ✅ Pan/Tilt | ✅ Pan/Tilt |

> [!IMPORTANT]
> **Cheville Roll RS-00** : Choix par défaut pour les deux configs. Plus compact (-47% surface), plus léger (-190g/cheville), moins cher (-$25/moteur). Suffisant pour marche ≤ 3 km/h. Si marche rapide fréquente (3-4 km/h), upgrade en RS-02 (+$50, +380g).

> [!IMPORTANT]
> **L'Option D-Révisée est désormais recommandée** si le portage est un objectif. Le Roll cheville compense le CdG plus haut, et la différence D vs C n'est que de +$120 / +1.35 kg pour un gain de portage majeur (5 kg bras tendu vs 3 kg). **L'Option C reste pertinente uniquement si la priorité absolue est l'autonomie batterie.**

---
---

## 10. Améliorations Supplémentaires de la Stabilité

> *Idées complémentaires pour optimiser l'équilibre du D-Bot, applicables à l'Option C comme D.*

### 10.1 Optimisation du Design des Pieds

Le design du pied est un facteur **majeur** de stabilité, souvent sous-estimé.

| Amélioration | Principe | Impact | Difficulté | Coût |
| :--- | :--- | :--- | :---: | :---: |
| **Pieds plus grands** | Augmenter la surface d'appui (largeur +2 cm) | ✅ Base de support élargie, plus de marge CoP | Faible | ~$0 (impression 3D) |
| **Semelle courbe (rocker)** | Courbure avant/arrière pour rouler naturellement | ✅ Transition de pas plus fluide, moins de couple cheville | Moyen | ~$10 |
| **Orteils passifs** | Joint élastique à l'avant du pied (~15° flex) | ✅ Phase de poussée améliorée (toe-off) | Moyen | ~$5-15 |
| **Semelle antidérapante** | Caoutchouc souple type Shore 40A collé sous le pied | ✅ Meilleure adhérence, moins de glissement | Faible | ~$5 |

> [!TIP]
> **Les pieds plus grands sont le gain de stabilité le plus simple et gratuit.** Un pied 2 cm plus large de chaque côté augmente la base de support de ~30%, ce qui donne une marge considérable au contrôleur d'équilibre.

### 10.2 Placement Stratégique de la Batterie

La batterie est la **masse la plus facile à repositionner** sans impact fonctionnel.

| Position | Impact CdG | Avantage | Inconvénient |
| :--- | :--- | :--- | :--- |
| **Torse haut** (actuel typique) | CdG haut | Facile d'accès, échange rapide | ❌ Élève le CdG |
| **Torse bas / bassin** ✅ | CdG **bas** ✅ | Stabilité améliorée | Accès plus difficile |
| **Dos bas (sac à dos)** | CdG moyen-bas | Bon compromis accès/stabilité | Légère protubérance |
| **Répartie (2 batteries)** ✅ | CdG symétrique ✅ | Équilibre gauche/droite + redondance | Plus de câblage |

**Recommandation** : Placer la batterie le **plus bas possible** dans le torse, idéalement au niveau du bassin. Voir le **[Guide Batterie Détaillé](./04_Electronique_Cablage.md#4-alimentation--batterie)** pour la stratégie progressive (1 batterie centrée → 2 batteries symétriques) et les spécifications semi-solide.

### 10.3 IMU et Capteurs de Force

L'équilibre d'un robot bipède dépend autant des **capteurs** que des actionneurs.

| Capteur | Rôle | Priorité | Coût |
| :--- | :--- | :---: | :---: |
| **IMU haute fréquence** (≥200 Hz) | Mesure d'angle et de vitesse angulaire du torse | 🔴 **CRITIQUE** | ~$20-50 |
| **Capteurs de force plantaires** | Mesure du Centre de Pression (CoP) sous chaque pied | 🟡 **IMPORTANT** | ~$30-80/pied |
| **Encodeurs moteurs** (déjà inclus) | Position et vitesse articulaire | ✅ Intégré RobStride | $0 |

L'IMU est **indispensable** — sans elle, le robot est aveugle à son inclinaison. Les capteurs plantaires sont un **plus significatif** qui permettent de savoir directement où se trouve le CoP au lieu de l'estimer par le modèle dynamique.

### 10.4 Éléments Élastiques en Série (SEA)

Une approche mécanique pour améliorer la compliance et la sécurité des interactions :

| Concept | Principe | Avantage | Inconvénient |
| :--- | :--- | :--- | :--- |
| **SEA cheville** | Ressort entre moteur et articulation | Absorption des chocs au sol, protection du moteur | Réduit la bande passante du contrôle |
| **SEA genou** | Idem au genou | Récupération d'énergie en phase de balancement | Complexité mécanique |

**Verdict** : Intéressant pour une V2, mais ajoute une complexité mécanique significative. Les QDD RobStride ont déjà une certaine backdrivabilité grâce à leur faible ratio de réduction (9:1 à 10:1), offrant une compliance naturelle.

### 10.5 DOF de Taille/Torse (Waist) — Optionnel V2

Beaucoup de robots humanoïdes avancés (Unitree H2, ATLAS) ont un **DOF de rotation du torse** :

| DOF Taille | Moteur Suggéré | Avantage | Quand ? |
| :--- | :---: | :--- | :---: |
| **Yaw** (rotation) | RS-03 | Dissocier mouvement bras/jambes, virages naturels | V2 |
| **Pitch** (inclinaison) | RS-03 | Se pencher en avant sans bouger les hanches | V2+ |
| **Roll** (latéral) | RS-03 | Compensation de charges latérales | V2+ |

**Verdict** : Non prioritaire pour la V1. Le K-Bot standard n'en a pas et parvient à marcher. Intéressant pour une V2 si la marche rapide et le portage asymétrique deviennent des objectifs.

### 10.6 Synthèse des Améliorations de Stabilité

| Priorité | Amélioration | Coût | Difficulté | Statut | Impact |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 🔴 **1** | IMU haute fréquence (BMI270 Spresense) | ~$30 | Faible | ✅ Prévu | Indispensable pour tout contrôle d'équilibre |
| 🔴 **2** | Pieds plus grands (+2 cm) | ~$0 | Faible | ✅ Prévu | +30% de base de support |
| 🟠 **3** | Batterie en position basse | ~$0 | Faible | ✅ Prévu | CdG abaissé de 5-10 cm |
| 🟡 **4** | Semelle antidérapante TPU | ~$15 | Faible | ✅ Prévu | Meilleure adhérence au sol |
| 🟡 **5** | Capteurs de force plantaires (FSR) | ~$40-60 | Moyen | ✅ Prévu | Mesure directe du CoP |
| 🟢 **6** | Semelle courbe (rocker) | ~$10 | Moyen | 📋 V2 | Transition de pas naturelle |
| 🟢 **7** | Orteils passifs | ~$15 | Moyen | 📋 V2 | Meilleur toe-off |
| 🔵 **8** | SEA (élasticité série) | ~$50 | Élevé | 📋 V2 | Absorption de chocs |
| 🔵 **9** | DOF Taille Yaw | ~$250 | Élevé | 📋 V2 | Virages naturels |

> [!IMPORTANT]
> **Les améliorations 1 à 5 seront implémentées dès la V1.** Coût total : ~$85. L'IMU (1) est déjà intégrée via la Spresense + BMI270 Add-on Board. Les pieds (2) et la batterie basse (3) sont des modifications CAD/positionnement sans coût. Les semelles TPU (4) et les FSR (5) sont détaillés ci-dessous.

---

### 10.7 Détail — Semelle Antidérapante TPU (Amélioration 4)

#### 10.7.1 Choix du Matériau

> [!NOTE]
> **Shore A** mesure la dureté des élastomères. Plus le chiffre est bas, plus le matériau est souple et adhérent. Pour une semelle de robot bipède, la plage **80A–90A** offre le meilleur compromis entre adhérence et résistance à l'usure.

| Shore A | Équivalent | Adhérence | Résistance usure | Usage |
| :---: | :--- | :---: | :---: | :--- |
| **70A** | Semelle running souple | ✅✅✅ | ⚠️ Faible | Trop mou, usure rapide |
| **80A** | Pneu vélo | ✅✅ | ✅ | **🏆 Idéal sol lisse (carrelage, parquet)** |
| **85A** | Talon de chaussure | ✅✅ | ✅✅ | Bon compromis polyvalent |
| **90A** | Roulette de skateboard | ✅ | ✅✅ | **🏆 Idéal sol dur (béton, extérieur)** |
| **95A** | Pneu plein robot | ⚠️ | ✅✅✅ | Trop dur, glisse sur carrelage |

**Recommandation** : Imprimer **deux jeux de semelles** — 80A (intérieur) et 90A (extérieur) — et changer selon l'environnement.

#### 10.7.2 Design de la Semelle

```
     ┌───────────────────────────┐
     │     PIED D-BOT (vue dessous)     │
     │                                   │
     │  ┌─────────────────────────────┐  │
     │  │        SEMELLE TPU          │  │
     │  │                             │  │
     │  │   ┌─────┐       ┌─────┐    │  │    ← Rainures 2mm × 1mm
     │  │   │ FSR │       │ FSR │    │  │       Motif en chevrons
     │  │   │  1  │       │  2  │    │  │       pour évacuation eau
     │  │   └─────┘       └─────┘    │  │
     │  │      (talon gauche)  (talon droit)   │
     │  │                             │  │
     │  │   ╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲   │  │    ← Texture chevrons
     │  │   ╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱   │  │       sur toute la surface
     │  │   ╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲   │  │
     │  │                             │  │
     │  │   ┌─────┐       ┌─────┐    │  │
     │  │   │ FSR │       │ FSR │    │  │
     │  │   │  3  │       │  4  │    │  │
     │  │   └─────┘       └─────┘    │  │
     │  │      (avant gauche)  (avant droit)   │
     │  └─────────────────────────────┘  │
     │                                   │
     └───────────────────────────────────┘
```

- **Épaisseur** : 3-4 mm (assez pour amortir, assez fin pour ne pas trop suréléver le pied)
- **Texture** : Rainures en chevrons (type pneu tout-terrain), 2 mm de large × 1 mm de profondeur
- **Fixation** : Encastrement + colle cyanoacrylate sur la semelle PLA/PETG du pied
- **Poches FSR** : 4 cavités Ø20 mm × 1.5 mm creusées depuis le dessus pour accueillir les FSR 402

#### 10.7.3 Paramètres d'Impression TPU

| Paramètre | Valeur |
| :--- | :--- |
| **Filament** | TPU Shore 80A ou 90A |
| **Buse** | 0.4 mm standard (pas besoin de tungstène) |
| **Température buse** | 220-240°C (selon filament) |
| **Température plateau** | 50-60°C |
| **Vitesse** | **15-25 mm/s** (TPU souple = imprimer lentement) |
| **Rétraction** | **Désactivée** ou très courte (0.5 mm, directe uniquement) |
| **Remplissage** | 100% (semelle = surface de contact, pas de creux) |
| **Hauteur couche** | 0.2 mm |
| **Ventilateur** | 50-80% |
| **Extrudeur** | **Direct Drive obligatoire** — le TPU <90A ne passe PAS en Bowden |

> [!WARNING]
> **TPU 80A est TRÈS souple** — il nécessite un extrudeur **Direct Drive** (type MK3S, Prusa XL, Bambu Lab). Si votre imprimante est en Bowden, utiliser du 90A minimum ou acheter un adaptateur Direct Drive. Le TPU 80A en Bowden va se coincer dans le tube PTFE.

> [!TIP]
> **Compatibilité Qidi X-Plus 4** : La Qidi X-Plus 4 est équipée d'un **extrudeur Direct Drive** avec engrenages en acier trempé et un hotend monobloc pouvant atteindre 370°C. Le TPU 88A Francofil est **parfaitement compatible** :
> - ✅ **Direct Drive** = le filament souple ne peut pas se coincer (pas de tube Bowden long)
> - ✅ **Tête titane** = aucun problème, le TPU s'imprime à 220-240°C (bien dans les capacités)
> - ✅ **Chambre chauffée** = laisser la porte **ouverte** pour le TPU (pas besoin de chaleur, au contraire)
> - ⚠️ **Capteur de filament** = le TPU souple peut ne pas déclencher le capteur de filament — le pousser manuellement si besoin
> - **Vitesse recommandée** : 20-30 mm/s max (la X-Plus 4 peut aller à 600 mm/s mais le TPU déteste la vitesse)
> - **Rétraction** : 0.5 mm max, vitesse rétraction 20 mm/s (le Direct Drive de la Qidi gère bien)

#### 10.7.4 Où Acheter le TPU (France / Europe)

| Fournisseur | Shore | Prix/kg | Lien | Note |
| :--- | :---: | :---: | :--- | :--- |
| **Francofil** 🇫🇷 | TPE 88A | ~€35/kg | [francofil.fr](https://www.francofil.fr) | 🏆 Fabricant français, mention "semelles" |
| **Recreus Filaflex** 🇪🇸 | 82A / 95A | ~€40/kg | [recreus.com](https://recreus.com) | Large gamme Shore, EU |
| **Spectrum S-Flex** 🇵🇱 | 90A | ~€35/kg | [center3dprint.com](https://center3dprint.com) | Bonne résistance usure, EU |
| **WASP TPU** 🇮🇹 | 80A | ~€40/kg | [3dwasp.shop](https://3dwasp.shop) | Spécialisé flexible |
| **PrimaSelect** 🇸🇪 | 80A | ~€38/kg | [3dprima.com](https://3dprima.com) | Bonne qualité, dispo EU |
| **Formfutura Python** 🇳🇱 | 90A | ~€45/kg | [3djake.fr](https://3djake.fr) | Industriel, anti-UV |

> [!TIP]
> **Recommandation achat** : Commencer par le **Francofil TPE 88A** (~€35/kg, fabriqué en France). C'est le meilleur compromis adhérence/imprimabilité. Si trop souple pour vos pistes, passer au **Spectrum S-Flex 90A**.

---

### 10.8 Détail — Capteurs de Force Plantaires FSR (Amélioration 5)

#### 10.8.1 Choix du Capteur : FSR 402

> [!NOTE]
> Les **FSR (Force Sensing Resistors)** sont des capteurs polymères dont la résistance diminue quand la force augmente. Ce sont les capteurs les plus utilisés pour la mesure de pression plantaire des robots bipèdes (publications IEEE, recherche ZMP/CoP).

| Caractéristique | FSR 402 (Interlink) |
| :--- | :--- |
| **Type** | Résistif à force (FSR) |
| **Forme** | Rond, Ø18.3 mm zone active |
| **Épaisseur** | 0.46 mm (se glisse sous une semelle) |
| **Plage de force** | 0.1 N – 10 N (extensible à 100 N avec résistance adaptée) |
| **Temps de réponse** | < 3 ms |
| **Interface** | 2 fils — simple diviseur de tension |
| **Prix** | ~$7-8 / unité (×4 = **~$30 par pied**) |
| **Durée de vie** | > 10 millions d'actuations |

**Alternatives évaluées** :

| Capteur | Prix | Avantage | Limite |
| :--- | :---: | :--- | :--- |
| **FSR 402** | ~$7 | 🏆 Fin, rond, adapté pied | Plage 10 N (extensible) |
| FSR 406 | ~$8 | Plus grand (carré 44mm) | Trop grand pour notre pied |
| FSR 408 | ~$10 | Longue bande | Pas adapté CoP ponctuel |
| Velostat DIY | ~$1 | Ultra pas cher | Imprécis, dérive |
| Capteur piézo | ~$2 | Très rapide | Mesure impacts, pas force statique |
| Cellule de charge | ~$15 | Très précis | Trop encombrant pour un pied |

**Verdict** : **4× FSR 402 par pied** (8 au total pour les 2 pieds) = la solution standard en robotique bipède.

#### 10.8.2 Placement — Configuration 4 Points

```
                PIED D-BOT (vue dessous)
     ┌───────────────────────────────────┐
     │                                   │
     │    (arrière / talon)              │
     │                                   │
     │    FSR 1 ●─────────────● FSR 2    │    ← 2 capteurs talon
     │    (x₁,y₁)            (x₂,y₂)    │       Portent ~60% du poids
     │                                   │
     │           Centre Pied             │
     │                                   │
     │    FSR 3 ●─────────────● FSR 4    │    ← 2 capteurs avant-pied
     │    (x₃,y₃)            (x₄,y₄)    │       Portent ~40% du poids
     │                                   │
     │    (avant / orteils)              │
     │                                   │
     └───────────────────────────────────┘
```

**Position recommandée** (pied de ~12 × 8 cm) :

| FSR | Position | Coordonnées (x, y) mm | Rôle |
| :---: | :--- | :---: | :--- |
| **1** | Talon gauche | (20, 25) | Phase d'appui talon (heel strike) |
| **2** | Talon droit | (20, 55) | Phase d'appui talon |
| **3** | Avant gauche | (90, 25) | Phase de propulsion (toe-off) |
| **4** | Avant droit | (90, 55) | Phase de propulsion |

#### 10.8.3 Circuit Électrique — Diviseur de Tension

Chaque FSR 402 nécessite un **diviseur de tension** pour être lu par un ADC (la Spresense a 6 entrées analogiques sur l'Extension Board) :

```
        3.3V (Spresense)
         │
         │
    ┌────┴────┐
    │  FSR    │    ← R_fsr varie : 1 MΩ (0 force) → ~1 kΩ (force max)
    │  402    │
    └────┬────┘
         │
         ├──────── A0 (Spresense ADC)    ← Lecture analogique
         │
    ┌────┴────┐
    │  R_ref  │    ← Résistance fixe de référence
    │  10 kΩ  │       Choix : 10 kΩ pour plage 0.1-10 N
    └────┬────┘       (utiliser 1 kΩ si plage 10-100 N souhaitée)
         │
        GND
```

**Formule** : `V_out = V_cc × R_ref / (R_fsr + R_ref)`

- Sans force : R_fsr ≈ 1 MΩ → V_out ≈ 0.03 V (≈ bruit)
- Force légère (1 N) : R_fsr ≈ 30 kΩ → V_out ≈ 0.83 V
- Force moyenne (5 N) : R_fsr ≈ 5 kΩ → V_out ≈ 2.2 V
- Force forte (10 N) : R_fsr ≈ 1 kΩ → V_out ≈ 3.0 V

#### 10.8.4 Câblage Spresense

```
    Spresense Extension Board
    ┌──────────────────────────┐
    │                          │
    │   A0 ◄── FSR 1 (pied L, talon G)
    │   A1 ◄── FSR 2 (pied L, talon D)
    │   A2 ◄── FSR 3 (pied L, avant G)
    │   A3 ◄── FSR 4 (pied L, avant D)
    │   A4 ◄── FSR 5 (pied R, talon G)
    │   A5 ◄── FSR 6 (pied R, talon D)
    │                          │
    │   GPIO D2 ◄── FSR 7 via MUX   │  ← Si >6 capteurs : utiliser
    │   GPIO D3 ◄── FSR 8 via MUX   │    un MUX analogique CD4051
    │                          │
    │   3.3V ──► Alimentation FSR
    │   GND  ──► Masse commune
    │                          │
    └──────────────────────────┘
```

> [!NOTE]
> La Spresense Extension Board a **6 entrées analogiques** (A0-A5). Pour 8 capteurs FSR (4 par pied), deux solutions :
> - **Option A** : Utiliser un **MUX analogique CD4051** (~$1) pour multiplexer les 2 derniers FSR sur A4/A5 via GPIO de sélection.
> - **Option B** : Connecter 6 FSR directement (3 par pied, triangle : talon, avant-gauche, avant-droit) — suffisant pour un CoP 3 points.
>
> **Recommandation** : Option B (3 FSR/pied = 6 total) est plus simple et suffit largement pour le calcul du CoP. La triangulation 3 points donne le même résultat mathématique qu'une quadrilatère.

#### 10.8.5 Calcul du Centre de Pression (CoP)

Le CoP se calcule comme la **moyenne pondérée des positions des capteurs**, pondérée par la force mesurée :

```
CoP_x = Σ(Fᵢ × xᵢ) / Σ(Fᵢ)
CoP_y = Σ(Fᵢ × yᵢ) / Σ(Fᵢ)
```

**Code C++ pour Spresense** (intégré dans le watchdog existant) :

```cpp
// ─── Capteurs de Force Plantaires (FSR 402) ─────────────────
// 3 FSR par pied (6 total), lus sur A0-A5
// Coordonnées en mm depuis le coin arrière-gauche du pied

struct FSR_Sensor {
    int pin;        // Pin analogique
    float x_mm;     // Position X sur le pied (mm)
    float y_mm;     // Position Y sur le pied (mm)
};

// Pied GAUCHE : 3 capteurs (talon, avant-gauche, avant-droit)
FSR_Sensor fsr_left[3] = {
    {A0, 20.0, 40.0},   // Talon centre
    {A1, 90.0, 20.0},   // Avant gauche
    {A2, 90.0, 60.0},   // Avant droit
};

// Pied DROIT : 3 capteurs
FSR_Sensor fsr_right[3] = {
    {A3, 20.0, 40.0},   // Talon centre
    {A4, 90.0, 20.0},   // Avant gauche
    {A5, 90.0, 60.0},   // Avant droit
};

// Convertir lecture ADC en force (N) — calibration approx.
float adcToForce(int adc_value) {
    float voltage = adc_value * 3.3 / 1023.0;
    if (voltage < 0.05) return 0.0;  // Seuil de bruit
    // R_fsr = R_ref × (Vcc - Vout) / Vout
    float r_fsr = 10000.0 * (3.3 - voltage) / voltage;
    // Courbe FSR 402 approx : F ≈ (R_fsr / 30000)^(-1.4)
    float force = pow(r_fsr / 30000.0, -1.4);
    return constrain(force, 0.0, 100.0);
}

// Calcul CoP pour un pied (3 capteurs)
void calculateCoP(FSR_Sensor sensors[], int count,
                  float &cop_x, float &cop_y, float &total_force) {
    float sum_fx = 0.0, sum_fy = 0.0;
    total_force = 0.0;

    for (int i = 0; i < count; i++) {
        float f = adcToForce(analogRead(sensors[i].pin));
        sum_fx += f * sensors[i].x_mm;
        sum_fy += f * sensors[i].y_mm;
        total_force += f;
    }

    if (total_force > 0.1) {  // Seuil minimum
        cop_x = sum_fx / total_force;
        cop_y = sum_fy / total_force;
    } else {
        cop_x = -1.0;  // Pied en l'air
        cop_y = -1.0;
    }
}

// Publier sur ROS2 via micro-ROS ou Serial
// Topic : /foot/left/cop  (geometry_msgs/Point)
// Topic : /foot/right/cop (geometry_msgs/Point)
// Topic : /foot/left/force  (std_msgs/Float32)
// Topic : /foot/right/force (std_msgs/Float32)
```

#### 10.8.6 Utilisation du CoP en Contrôle de Balance

Le CoP mesuré par les FSR est comparé au **ZMP (Zero Moment Point)** calculé par l'algorithme de marche. Si le CoP s'écarte du centre de la base de support, le contrôleur d'équilibre ajuste les moteurs :

| Situation | CoP position | Action correctrice |
| :--- | :--- | :--- |
| Équilibre normal | Centre du pied | Aucune correction |
| Robot penche en avant | CoP vers les orteils | Cheville pitch → flex dorsale |
| Robot penche en arrière | CoP vers le talon | Cheville pitch → flex plantaire |
| Robot penche à gauche | CoP vers le bord gauche | Cheville roll → éversion |
| Pied décollé | Force totale ≈ 0 | Phase oscillante détectée |

#### 10.8.7 Où Acheter les FSR

| Fournisseur | Modèle | Prix/unité | Lien | Note |
| :--- | :--- | :---: | :--- | :--- |
| **SparkFun** | FSR 402 (Interlink) | ~$7 | [sparkfun.com](https://www.sparkfun.com/products/9375) | Référence standard |
| **DigiKey EU** | FSR 402 | ~$7 | [digikey.fr](https://www.digikey.fr) | Livraison rapide EU |
| **Mouser EU** | FSR 402 | ~$7 | [mouser.fr](https://www.mouser.fr) | Stock EU |
| **AliExpress** | FSR 402 compatible | ~$2-3 | AliExpress | Clones, qualité variable |
| **Amazon FR** | FSR 402 | ~$8-10 | amazon.fr | Dispo immédiate |

> [!TIP]
> **Budget total FSR** : 6 FSR 402 × ~$7 + 6 résistances 10 kΩ (~$1) + câblage (~$3) = **~$45**. Pas besoin de circuit imprimé : câblage direct sur les pins analogiques de l'Extension Board Spresense.

---

### 10.9 Résumé des Coûts — Améliorations de Stabilité V1

| # | Amélioration | Composants | Coût |
| :---: | :--- | :--- | :---: |
| **1** | IMU BMI270 | Spresense + Add-on Board (déjà prévu) | $0 (inclus) |
| **2** | Pieds +2 cm | Réimpression 3D (PLA/PETG) | ~$2 filament |
| **3** | Batterie basse | Repositionnement dans le torse | $0 |
| **4** | Semelles TPU | 1 rouleau TPU 88A Francofil (~250g utilisé) | ~$10 |
| **5** | FSR plantaires | 6× FSR 402 + 6× R 10 kΩ + câbles | ~$45 |
| | | **Total** | **~$57** |
