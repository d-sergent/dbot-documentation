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
| **DOF** | 20 (K-Bot) / 22 (D-Bot) |

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
| **Inconvénient** | CdG plus haut (+2.16 kg aux épaules), autonomie réduite |

> [!WARNING]
> **L'Option D ajoute 3.5 kg**, ce qui réduit l'autonomie d'environ 15-20% et déplace le centre de gravité vers le haut. Conséquence : le contrôle de l'équilibre est plus difficile et les algorithmes de marche doivent être retuned.

---

## 6. Recommandation Finale

### 🏆 Option C "D-Bot Performance" est RECOMMANDÉE

**Raison** : Meilleur rapport performance/impact.
- Résout le problème **CRITIQUE** des chevilles (+$180, +950g)
- Améliore significativement le portage des coudes (+$140, +432g)
- Surpoids total modéré (+1.38 kg)
- Reste 100% dans l'écosystème RobStride (compatibilité garantie)

### Configuration Finale "D-Bot Performance"

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
| **Cheville** | **RS-03** | **2** | **60 N.m** | **880g** | **Propulsion** |

**Total** : 22 moteurs, ~17.5 kg de moteurs, ~37.4 kg robot complet

### À retenir sur les moteurs alternatifs

Les alternatives étudiées (CubeMars AK, MyActuator RMD) ne sont PAS compétitives face à RobStride pour ce projet :
- **3 à 5× plus chers** à performances équivalentes
- **Densité de couple inférieure** dans la plupart des cas
- **Écosystème incompatible** (drivers différents, protocoles différents)
- Le seul intérêt serait une **personnalisation extrême** ou un besoin de backdrivabilité supérieure (AK80-9)

**RobStride offre le meilleur rapport couple/poids/prix** sur le marché des QDD en 2024-2025.
