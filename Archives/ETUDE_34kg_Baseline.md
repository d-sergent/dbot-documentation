# 15a — Analyse Biomécanique : Locomotion et Portage (Baseline K-Bot)

> **Série Biomécanique :**
> - [15a] **Locomotion Baseline** ← *vous êtes ici*
> - [15b] [Configurations Moteurs & Évolutions](./15b_Configurations_Moteurs.md)
> - [15c] [Révision Configuration Cardan 39 kg](./15c_Revision_Cardan_39kg.md)
> - [15d] [Genou & Course — Solutions](./15d_Genou_et_Course.md)
> - [16] [**Conclusions & Architecture Finale D-Bot**](./16_Conclusions_Architecture_DBot.md)

Ce document analyse les capacités mécaniques du D-Bot dans sa configuration de base (héritée du K-Bot) : couples requis pour la marche, la course et le portage, et synthèse des faiblesses initiales.

---

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
| **Cheville Pitch** (RS-02) | 17 N.m (×2 tirant = 34) | ~34 N.m | **≈0%** | ⚠️ **VIABLE (Limite)** |

> [!WARNING]
> **Verdict Révisé : La CHEVILLE est viable mais limite.**
> Avec un bras de levier de **0.10 m** (pointe du pied), le couple requis est de **~33.4 N.m**.
> Le D-Bot V1 (34 N.m) couvre juste ce besoin statique.
> **Conséquence** : La marche lente est possible avec déroulé du pied, mais la marge pour les accélérations brutales (marche rapide) est faible. Le centre de pression devra rester maîtrisé.

> [!NOTE]
> **⬆️ Ce calcul concerne le mécanisme tirant**. Le ratio ~2:1 du K-Bot est essentiel ici. Sans lui (direct drive 17 N.m), le robot tomberait. L'upgrade V2 (RS-03) reste pertinent pour gagner de la marge de sécurité et permettre la course.

#### Explication du Calcul Cheville
```
Couple cheville = Masse × g × Bras de Levier (Axe → Pointe)
                = 34 kg × 9.81 m/s² × 0.10 m (Pied 10 cm)
                ≈ 33.4 N.m minimum statique
                ≈ 50 N.m en dynamique (marche rapide)
```

**Conclusion marche lente** : Le D-Bot V1 (RS-02) est **capable de marcher**. Le couple de 34 N.m suffit pour l'équilibre statique sur la pointe des pieds (33.4 N.m). C'est une excellente nouvelle pour la Phase 4 V1. La stratégie "Pied Court" a payé.

> [!TIP]
> **Compromis de Conception : Longueur du Pied**
> *   **Pied Court** = Bras de levier réduit = **Moins de couple moteur requis**. (C'est préférable pour les moteurs faibles).
> *   **Pied Long** = Grand polygone de sustentation = **Meilleure stabilité**.
>
> Pour le D-Bot V1, réduire la distance "Axe ↔ Pointe" (ex: 12-15 cm) aiderait le RS-02 à supporter la charge, au prix d'une stabilité statique réduite.


---

### 2.2 Marche Rapide (2-3 km/h)

| Paramètre | Requis | Disponible | Verdict |
| :--- | :---: | :---: | :---: |
| Couple genou dynamique | ~80 N.m | 120 N.m (RS-04) | ✅ Suffisant |
| Couple hanche dynamique | ~70 N.m | 120 N.m (RS-04) | ✅ Suffisant |
| Couple cheville dynamique | ~50 N.m | ~34 N.m (RS-02 + tirant) | ⚠️ **LIMITÉ** |

> [!NOTE]
> Ces estimations sont pour une marche à **~2-3 km/h**.

> [!WARNING]
> **La marche rapide est quasi-impossible** dans la configuration K-Bot de base à cause des chevilles RS-02. Le robot ne peut pas se propulser efficacement. Il est limité à un mode "shuffle" < 1 km/h.

> [!NOTE]
> **⬆️ Config K-Bot de base analysée ici.** Le D-Bot conserve le RS-02 avec **tirant (~34 N.m effectif)**. Pour la marche lente (<2 km/h), c'est suffisant. La marche rapide nécessite une optimisation du tirant ou un upgrade RS-03 (V2).

---

### 2.3 Course (> 4 km/h)

La course est **impossible** dans la configuration K-Bot de base :
- Les chevilles (RS-02 + tirant) ont ~34 N.m vs ~100 N.m requis pour la course pour la phase de vol
- Les genoux (RS-04, 200 RPM) sont trop lents pour la fréquence de pas requise
- Pas de compliance élastique dans le système actuel

> [!NOTE]
> **⬆️ Config K-Bot de base.** Avec le RS-02 + tirant (~34 N.m), la course reste hors portée V1. Il faudrait un upgrade RS-03 (V2) + mécanismes SEA (Series Elastic Actuator) — voir section 10.

---

## 3. Analyse de la Capacité de Portage

### 3.1 Portage à Bout de Bras (Bras Tendu Horizontal)

C'est le **cas le plus défavorable** car le bras-de-levier est maximal.

#### Masses Actualisées du Bras (avec D-Hand Premium)

| Segment | Masse Ancienne | Masse Actuelle | Δ |
| :--- | :---: | :---: | :---: |
| Bras (épaule → coude) | ~2.5 kg | ~2.5 kg | — |
| Avant-bras (coude → poignet) | ~1.5 kg | ~1.5 kg | — |
| **8× Dynamixel XC330 (dans avant-bras)** | 0 | **+0.184 kg** | +184g |
| **Structure main + poulies + tendons** | 0 | **+0.250 kg** | +250g |
| **Total avant-bras + main** | ~1.5 kg | **~1.93 kg** | +434g |
| **Total bras complet** | ~3 kg | **~4.43 kg** | +1.43 kg |

#### Modèle Mécanique Mis à Jour (Bras Tendu)

```
L_bras = 0.25 m,  L_avant-bras = 0.22 m

Couple épaule (bras seul) =
    M_bras × g × (L_bras / 2) + M_avant-bras+main × g × (L_bras + L_avant-bras / 2)
  = 2.5 × 9.81 × 0.125 + 1.93 × 9.81 × (0.25 + 0.11)
  = 3.07 + 6.82
  = ~9.9 N.m   ← quasi identique à l'ancien (~10 N.m), car +0.43 kg × 0.36 m ≈ +1.5 N.m
                  compensé par la redistribution de masse

Avec charge externe (L = 0.47 m) :
  Couple épaule total = 9.9 + M_charge × 9.81 × 0.47
```

| Charge Portée | Couple Épaule Requis | Couple Dispo (RS-03) | Verdict |
| :---: | :---: | :---: | :---: |
| **0 kg** (bras + main seuls) | ~9.9 N.m | 60 N.m pic / 20 N.m nom. | ✅ OK |
| **1 kg** | ~14.5 N.m | 60 / 20 N.m | ✅ OK |
| **2 kg** | ~19.2 N.m | 60 / 20 N.m | ⚠️ Limite nominale |
| **2.1 kg** | ~20 N.m | 60 / **20 N.m** nom. | 🎯 **Limite nominale exacte** |
| **3 kg** | ~23.8 N.m | 60 / 20 N.m | ⚠️ Au-dessus nominal |
| **5 kg** | ~33.1 N.m | 60 / 20 N.m | ❌ > 1.5× nominal |
| **10 kg** | ~56.2 N.m | 60 / 20 N.m | ❌ Presque pic |

> [!IMPORTANT]
> **Limite de portage à bout de bras : inchangée.** L'ajout de la D-Hand (+434g) ne modifie pas significativement la capacité de portage (décalage de seulement ~1.5 N.m supplémentaire à l'épaule). La limite reste **~2 kg en continu** (couple nominal RS-03 = 20 N.m) et ~**5 kg momentanément** (pic 60 N.m).

> [!NOTE]
> **Pourquoi l'impact est si faible ?** Les moteurs XC330 (184g) sont dans l'avant-bras, à ~36 cm de l'épaule. La main (250g) est à ~47 cm. Le bras de levier crée seulement +1.5 N.m supplémentaire sur l'épaule — négligeable face aux 60 N.m disponibles au pic.

### 3.2 Portage Bras Plié (Coude 90°)

```
Avant-bras horizontal (coude à 90°) : L_avant-bras = 0.22 m

Couple coude (avant-bras seul) = M_avant-bras+main × g × L_avant-bras / 2
                                = 1.93 × 9.81 × 0.11
                                ≈ 2.1 N.m   (était ~0.8 N.m, +1.3 N.m)

Disponible pour charge : RS-02 (17 N.m) - 2.1 = **14.9 N.m**
  → Max charge coude : 14.9 / (0.22 m) = ~68 N ≈ **6.8 kg au coude**
```

| Charge Portée | Couple Épaule Requis | Couple Coude Requis | Verdict |
| :---: | :---: | :---: | :---: |
| **0 kg** (avant-bras seul) | ~14.7 N.m | ~2.1 N.m | ✅ OK |
| **5 kg** | ~26.3 N.m | ~13.1 N.m | ✅ OK (RS-02 : 17 N.m pic) |
| **7 kg** | ~33.3 N.m | ~17.5 N.m | ⚠️ Coude RS-02 au pic |
| **10 kg** | ~44.3 N.m | ~24.1 N.m | ❌ Coude RS-02 dépassé |

> [!WARNING]
> **La D-Hand augmente la charge propre de l'avant-bras de +434g**, ce qui réduit légèrement la capacité de portage bras plié. Le coude RS-02 atteint son pic à ~7 kg de charge (au lieu de ~9 kg avant). La limite pratique reste **5 kg bras plié en sécurité**.

> [!TIP]
> **Upgrade coude RS-02 → RS-06** (36 N.m au lieu de 17 N.m) : Avec la D-Hand, la limite bras plié passerait à **~15 kg** avec un RS-06. Cost : +$70. Voir [Config Biomécanique Option C §8](./15_Analyse_Biomecanique.md#8-configurations-finales-révisées).

---
*Mis à jour Mars 2026 : Prise en compte de la D-Hand Premium (8× XC330, +0.184 kg + structure +0.250 kg = +0.434 kg total avant-bras).*

---

## 4. Synthèse des Faiblesses

| Zone | Moteur Actuel | Problème | Sévérité |
| :--- | :---: | :--- | :---: |
| **Cheville** | RS-02 tirant (34 N.m) | Suffisant statique (33 N.m) | ✅ **OK (Marche)** |
| **Coude** | RS-02 (17 N.m) | Limite pour portage > 5 kg | 🟡 **MOYEN** |
| **Épaule Pitch** | RS-03 (60 N.m) | Limite pour portage > 3 kg bras tendu | 🟡 **MOYEN** |
| **Cheville Roll** | Aucun | Pas de DOF d'adaptation au sol | 🟠 **IMPORTANT** |

---
