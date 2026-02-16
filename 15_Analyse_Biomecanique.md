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
| **Cheville Pitch** (RS-02) | 17 N.m | ~30 N.m | **-43%** | ⚠️ INSUFFISANT |

> [!CAUTION]
> **Point faible critique : La CHEVILLE** (RS-02, 17 N.m pic) est très probablement sous-dimensionnée pour la marche. En phase de poussée (toe-off), la cheville doit générer un couple de ~30-50 N.m pour propulser 34 kg. Le RS-02 est à 17 N.m pic (6 N.m nominal), ce qui est **2 à 3× trop faible**.

#### Explication du Calcul Cheville
```
Couple cheville = Masse × g × Distance CdP-Cheville
                = 34 kg × 9.81 m/s² × 0.10 m (distance talon)
                ≈ 33 N.m minimum statique
                ≈ 50 N.m en dynamique (accélérations)
```

**Conclusion marche lente** : La marche lente de type "shuffle" est possible grâce au surdimensionnement des hanches et genoux, mais sera fortement limitée par les chevilles. La marche sera plutôt un mouvement de type "flat-foot" sans propulsion.

---

### 2.2 Marche Rapide (2-3 km/h)

| Paramètre | Requis | Disponible | Verdict |
| :--- | :---: | :---: | :---: |
| Couple genou dynamique | ~80 N.m | 120 N.m (RS-04) | ✅ Suffisant |
| Couple hanche dynamique | ~70 N.m | 120 N.m (RS-04) | ✅ Suffisant |
| Couple cheville dynamique | ~50-60 N.m | 17 N.m (RS-02) | ❌ **CRITIQUE** |
| Vitesse cycle hanche | ~100 RPM | 200 RPM (RS-04) | ✅ OK |
| Vitesse cycle genou | ~150 RPM | 200 RPM (RS-04) | ✅ Limite |

> [!WARNING]
> **La marche rapide est quasi-impossible** dans la configuration actuelle à cause des chevilles RS-02. Le robot ne peut pas se propulser efficacement. Il est limité à un mode "shuffle" < 1 km/h.

---

### 2.3 Course (> 4 km/h)

La course est **impossible** dans la configuration actuelle :
- Les chevilles (RS-02) n'ont que 17 N.m vs ~100 N.m requis pour la phase de vol
- Les genoux (RS-04, 200 RPM) sont trop lents pour la fréquence de pas requise
- Pas de compliance élastique dans le système actuel

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
| **Cheville** | RS-02 (17 N.m) | Sous-dimensionné 2-3× pour marche | 🔴 **CRITIQUE** |
| **Coude** | RS-02 (17 N.m) | Limite pour portage > 5 kg | 🟡 **MOYEN** |
| **Épaule Pitch** | RS-03 (60 N.m) | Limite pour portage > 3 kg bras tendu | 🟡 **MOYEN** |
| **Cheville Roll** | Aucun | Pas de DOF d'adaptation au sol | 🟠 **IMPORTANT** |

---

## 5. Propositions d'Évolution

### Option A : Upgrade RobStride (Restant dans l'écosystème)

#### A1. Chevilles RS-02 → RS-03

| Paramètre | Avant (RS-02) | Après (RS-03) | Gain |
| :--- | :---: | :---: | :---: |
| Couple Pic | 17 N.m | 60 N.m | **×3.5** |
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

**Verdict** : ⚠️ **INSUFFISANT**. +29% de couple ne résout pas le problème des chevilles (besoin minimum 40 N.m). Et coûte 3× plus cher qu'un RS-02. Passer directement à un RS-03 est meilleur et moins cher.

#### B3. MyActuator RMD-X10 V3 (pour Chevilles)

| Paramètre | RS-02 (actuel) | RMD-X10 V3 | Comparaison |
| :--- | :---: | :---: | :---: |
| Couple Pic | 17 N.m | 50 N.m | **+194%** |
| Couple Nominal | 6 N.m | 12 N.m | +100% |
| Poids | 405g | 1150g | +184% |
| Prix | ~$160 | ~$890 | **×5.5** |

**Verdict** : ⚠️ **POSSIBLE mais coûteux**. Couple suffisant pour les chevilles (50 N.m pic) mais très lourd (1.15 kg) et très cher ($890). Le RS-03 RobStride fait mieux (60 N.m, 880g, $250).

---

### Option C : Configuration "D-Bot Performance" (Recommandée)

Combinaison optimale des upgrades identifiés :

| Zone | Avant | Après | Changement | Surcoût |
| :--- | :---: | :---: | :--- | :---: |
| **Cheville** | 2× RS-02 | **2× RS-03** | 17→60 N.m (×3.5) | +$180 |
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
| **Cheville** | 2× RS-02 | **2× RS-03** | 17→60 N.m (×3.5) | +$180 |
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

#### Solution S1 : Ajout d'un RS-02 par cheville (Config "6 DOF Jambe")

C'est la solution la plus directe, mentionnée par K-Scale eux-mêmes comme extension possible.

| Paramètre | Détail |
| :--- | :--- |
| **Moteur ajouté** | 2× RS-02 (1 par cheville) |
| **DOF cheville** | Pitch (existant) + **Roll (nouveau)** |
| **Couple Roll** | 17 N.m (suffisant pour correction latérale) |
| **Surpoids** | +810g (2× 405g) |
| **Surcoût** | +$320 (2× $160) |
| **DOF total robot** | 22 → **24 DOF** (D-Bot) |
| **Complexité mécanique** | Moyenne — Nécessite un bracket d'articulation additionnel |

**Avantage** : Le couple de Roll cheville n'a PAS besoin d'être aussi élevé que le Pitch. Le RS-02 (17 N.m) est suffisant car le Roll est un mouvement de **correction fine**, pas de propulsion. Les forces latérales sont 3-5× inférieures aux forces sagittales.

**Justification du RS-02 vs RS-03** :
```
Couple Roll cheville requis (estimation) :
= Masse × g × Décalage_latéral_CoG
= 36 kg × 9.81 × 0.03 m (décalage latéral max)
≈ 10.6 N.m (statique)
≈ 15 N.m (dynamique avec marges)

→ RS-02 (17 N.m pic, 6 N.m nominal) = SUFFISANT avec marge de 13%
```

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

### 7.4 Recommandation : Solution S1 (RS-02 Roll Cheville)

La Solution S1 est recommandée car :
- ✅ Couple suffisant (17 N.m vs ~15 N.m requis)
- ✅ Compatible écosystème RobStride existant
- ✅ Mentionnée par K-Scale comme extension envisagée
- ✅ Surpoids modéré (+810g sur une position basse)
- ✅ Porte le D-Bot à **24 DOF** (objectif initial)

---

## 8. Configurations Finales Révisées

### 🏆 Option C-Révisée : "D-Bot Performance" (RECOMMANDÉE)

Intègre l'upgrade des chevilles (Pitch → RS-03) + ajout Roll cheville (RS-02) + coudes améliorés (RS-06).

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
| **Cheville Pitch** | **RS-03** | **2** | **60 N.m** | **880g** | **Propulsion (upgrade)** |
| **Cheville Roll** | **RS-02** | **2** | **17 N.m** | **405g** | **Stabilité latérale (NOUVEAU)** |

#### Bilan Option C-Révisée

| Impact | Détail |
| :--- | :--- |
| **Total moteurs** | **24 moteurs** (objectif D-Bot atteint ✅) |
| **Poids moteurs** | ~18.3 kg |
| **Poids robot total** | ~38.2 kg |
| **Surpoids vs K-Bot** | +2.19 kg (chevilles upgrade + Roll + coudes) |
| **Surcoût vs K-Bot** | +$640 total |
| **DOF total** | **24 DOF** |
| **Marche** | ✅ Stable, propulsée, avec adaptation latérale |
| **Marche rapide** | ✅ 2-3 km/h réalisable |
| **Terrain irrégulier** | ✅ Adaptation active du pied |
| **Portage bras plié** | ✅ ~10 kg |

### Option D-Révisée : "D-Bot Maximal"

Ajoute les RS-04 aux épaules en plus de la config C-Révisée :

| Zone | Moteur | Qté | Couple Pic | Changement vs K-Bot |
| :--- | :---: | :---: | :---: | :--- |
| Épaule Pitch/Roll | **RS-04** | 4 | **120 N.m** | Upgrade RS-03→RS-04 |
| Coude | **RS-06** | 2 | **36 N.m** | Upgrade RS-02→RS-06 |
| Cheville Pitch | **RS-03** | 2 | **60 N.m** | Upgrade RS-02→RS-03 |
| Cheville Roll | **RS-02** | 2 | **17 N.m** | **NOUVEAU** |
| Reste | Inchangé | - | - | - |

| Impact | Détail |
| :--- | :--- |
| **Total moteurs** | **24 moteurs** |
| **Poids robot total** | ~41.7 kg |
| **Surcoût vs K-Bot** | +$760 total |
| **Portage bras tendu** | **5 kg continu** |
| **Portage bras plié** | **15+ kg théorique** |

---

## 9. Comparatif des Configurations

| Critère | K-Bot Standard | D-Bot Perf (C-Rév.) | D-Bot Max (D-Rév.) |
| :--- | :---: | :---: | :---: |
| **DOF** | 20 | **24** | **24** |
| **Moteurs** | 20 | **24** | **24** |
| **Poids robot** | 34 kg | 38.2 kg | 41.7 kg |
| **Surcoût** | Base | +$640 | +$760 |
| **Marche lente** | ⚠️ Shuffle | ✅ Stable | ✅ Stable |
| **Marche rapide** | ❌ Impossible | ✅ 2-3 km/h | ✅ 2-3 km/h |
| **Terrain irrégulier** | ❌ Impossible | ✅ Roll actif | ✅ Roll actif |
| **Stabilité latérale** | ❌ Hanches seules | ✅ Cheville Roll | ✅ Cheville Roll |
| **Portage bras tendu** | 2 kg | 3 kg | **5 kg** |
| **Portage bras plié** | ~5 kg | **10 kg** | **15+ kg** |
| **Tête articulée** | ❌ | ✅ Pan/Tilt | ✅ Pan/Tilt |

> [!IMPORTANT]
> **L'Option D-Révisée est désormais recommandée** si le portage est un objectif. Le Roll cheville compense le CdG plus haut, et la différence D vs C n'est que de +$120 / +1.35 kg pour un gain de portage majeur (5 kg bras tendu vs 3 kg). Les deux options nécessitent un re-tuning algorithmes identique en complexité. **L'Option C reste pertinente uniquement si la priorité absolue est l'autonomie batterie.**

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

| Priorité | Amélioration | Coût | Difficulté | Impact |
| :---: | :--- | :---: | :---: | :--- |
| 🔴 **1** | IMU haute fréquence | ~$30 | Faible | Indispensable pour tout contrôle d'équilibre |
| 🔴 **2** | Pieds plus grands (+2 cm) | ~$0 | Faible | +30% de base de support |
| 🟠 **3** | Batterie en position basse | ~$0 | Faible | CdG abaissé de 5-10 cm |
| 🟡 **4** | Semelle antidérapante | ~$5 | Faible | Meilleure adhérence au sol |
| 🟡 **5** | Capteurs de force plantaires | ~$100 | Moyen | Mesure directe du CoP |
| 🟢 **6** | Semelle courbe (rocker) | ~$10 | Moyen | Transition de pas naturelle |
| 🟢 **7** | Orteils passifs | ~$15 | Moyen | Meilleur toe-off |
| 🔵 **8** | SEA (élasticité série) | ~$50 | Élevé | Absorption de chocs, V2 |
| 🔵 **9** | DOF Taille Yaw | ~$250 | Élevé | Virages naturels, V2 |

> [!TIP]
> **Les 4 premières améliorations coûtent moins de $35 au total** et sont toutes réalisables immédiatement avec une simple impression 3D (pieds), un composant ($30 IMU), et un repositionnement de batterie ($0). Elles auront collectivement un impact **considérable** sur la stabilité.
