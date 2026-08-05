# 15d — Étude du Genou : Solutions et Transmission GT3

> **Série Biomécanique :**
> - [15a] [Locomotion Baseline](./15a_Analyse_Locomotion_Baseline.md)
> - [15b] [Configurations Moteurs & Évolutions](./15b_Configurations_Moteurs.md)
> - [15c] [Révision Configuration Cardan 40.2 kg](STUDY_Revision_Cardan.md)
> - [15d] **Genou — Analyse & Solution GT3** ← *vous êtes ici*
> - [15e] [Alternatives Moteurs Genou](./15e_Alternatives_Moteurs_Genou.md)
> - [15f] [Portage de Charges & Marche](STUDY_Marche_Dynamique.md)
> - [16] [**Conclusions & Architecture Finale D-Bot**](../../00_Architecture_Centrale/FINAL_Architecture_Globale.md)

Ce document analyse pourquoi le genou RS-04 (120 N.m) devient le facteur limitant pour la course (172 N.m requis), explore 5 solutions graduelles (S1 à S5), puis détaille la **Solution S6 (Courroie GT3)** retenue comme évolution V2 de référence. La S6 est la seule qui cumule amplification de couple, réduction d'inertie et compatibilité avec l'architecture F-A-R de la hanche.

---

### 1.2 Illustations des Concepts et Transmission GT3

![Séquence cinématique S2 Genou Tirant](../../Assets/img_s2_cinematique_sequence.png)

*Figure 1.1 : Séquence cinématique de flexion/extension du genou à tirant.*

![Schéma Genou à Tirant S2](../../Assets/img_s2_genou_tirant.png)

*Figure 1.2 : Détail de la tringlerie et du tirant mécanique du genou S2.*

![Transmission Courroie GT3 Genou S6](../../Assets/img_s6_gt3_knee_transmission.png)

*Figure 1.3 : Architecture de transmission par courroie synchrone GT3 (Solution S6).*

---

### 1.1 Analyse des Facteurs Limitants

```
τ_genou_course = τ_statique × F_dynamique × F_impact

τ_statique  = M × g × bras_levier_cuisse = 39 × 9.81 × 0.18 = 68.8 N.m
F_dynamique = amplification cinétique (vitesse + accélération angulaire)
F_impact    = pic à l'atterrissage (contact du pied)

À 4 km/h (phase de vol) :
  F_dynamique ≈ 1.5,  F_impact ≈ 1.7  →  Total = 68.8 × 2.5 ≈ 172 N.m
```

**Décomposition du problème :**

| Facteur | Contribution | Levier disponible |
| :--- | :---: | :---: |
| **Masse du robot** (40.2 kg) | Élevée | Faible (difficile à réduire) |
| **Bras de levier cuisse** (0.18 m) | Modérée | Moyen (géométrie fixe) |
| **Facteur dynamique** (×1.5) | Modérée | Fort (algorithme) |
| **Facteur d'impact** (×1.7) | Élevée | Fort (mécanique + algorithme) |
| **Couple disponible RS-04** (120 N.m) | N/A | Moyen (amplification) |

**Déficit à combler : 177.5 − 120 = 57.5 N.m** (soit +48% au-dessus de la capacité RS-04)

---

## 2. Solutions Explorées (S1 à S5)

### S1 — Optimisation Algorithmique de la Foulée (Gratuit, immédiat)

**Principe** : Modifier le pattern de marche pour réduire les facteurs dynamique et d'impact, sans aucun changement matériel.

| Stratégie | Réduction τ | Couple résultant | Faisabilité |
| :--- | :---: | :---: | :---: |
| A. Foulée courte | ~15% | 146 N.m | ✅ Facile |
| B. Crouch gait | ~3% | 167 N.m | ✅ Facile |
| **C. Mid-foot strike** | **~28%** | **124 N.m** | ✅ Facile |
| **A+C combiné** | **~40%** | **~103 N.m** | ✅ **Sous la limite !** |

> [!TIP]
> **S1 seul peut suffire pour un V1.** La combinaison foulée courte + mid-foot strike ramène le couple genou à ~103 N.m, sous les 120 N.m du RS-04. Vitesse de course : **4-5 km/h**. C'est la solution zéro coût à implémenter d'abord.

---

### S2 — Mécanisme Tirant au Genou

**Principe** : Déplacer le moteur RS-04 en haut de cuisse et l'accoupler au genou via un **tirant carbone 1.5:1**, amplifiant le couple ET réduisant la masse distale.

```
τ_genou_effectif = 120 × 1.5 = 180 N.m ✅
```

**Point critique**: Le couple varie selon l'angle de flexion :

| Angle Genou | Factor sin | Couple Genou Effectif |
| :---: | :---: | :---: |
| 0° (tendu) | 1.00 | **180 N.m** |
| 60° | 0.82 | 148 N.m |
| 90° (assis) | 0.50 | 90 N.m |
| **120° (accroupi)** | **0.17** | **31 N.m ⚠️** |

> [!WARNING]
> **Point mort (Dead Center)** : Quand le bras de manivelle et le tirant sont parfaitement alignés, le couple est nul. Le design du bras de manivelle doit placer ce point mort en dehors de la plage 0-120°. À forte flexion (120°), le couple tombe à 31 N.m — insuffisant pour se relever d'un accroupi profond. Ce défaut a pesé dans le choix final en faveur de la GT3 (voir §3.3).

---

### S3 — SEA (Series Elastic Actuator)

**Principe** : Intercaler un ressort calibré entre la sortie du RS-04 et le pivot du genou. Le ressort stocke l'énergie à l'impact et la restitue en pic de puissance.

| Paramètre | Direct Drive | SEA |
| :--- | :---: | :---: |
| Couple moteur max | 120 N.m | 120 N.m |
| **Couple pic articulaire** | 120 N.m | **~180-250 N.m** |
| Absorption d'énergie | ❌ | ✅ |
| Poids ajouté | 0g | +200g |
| Complexité | ⭐ | ⭐⭐⭐⭐ |

---

### S4 — Double RS-04 en Parallèle

**Principe** : 2× RS-04 sur le même axe.

```
τ_total = 240 N.m ✅
+870g / genou, +$400 / genou — solution brute force non retenue.
```

> [!WARNING]
> +1.74 kg par genou (×2 = +3.48 kg) aggrave l'inertie et augmente la masse totale, recréant du besoin de couple. Boucle négative.

---

### S5 — Tibia Carbone Flexible (Leg Spring)

**Principe** : Lame carbone à la place du tibia rigide — stockage passif d'énergie à l'impact.

```
Réduction couple genou : ~22%  (172 → 134 N.m)
Masse : neutre ou négatif (carbone < PA12-CF)
Coût : ~50-150€

Combinaison S5 + S1 (mid-foot strike) :
  172 × 0.78 × 0.72 = ~96 N.m ← sous les 120 N.m ✅
```

---

### Comparatif S1-S5

| Solution | τ max | Coût | Masse Ajoutée | Complexité |
| :--- | :---: | :---: | :---: | :---: |
| **S1. Algo mid-foot + foulée** | ~103 N.m | **0€** | **0g** | ⭐ |
| **S5+S1. Tibia carbone + algo** | ~96 N.m | ~100€ | **-50g** | ⭐⭐ |
| **S2. Tirant genou** | ~180 N.m | ~150€ | -670g | ⭐⭐⭐ |
| **S3. SEA** | ~200 N.m | ~200€ | +200g | ⭐⭐⭐⭐ |
| **S2+S3. Tirant + SEA** | ~270 N.m | ~350€ | -470g | ⭐⭐⭐⭐⭐ |
| **S4. 2× RS-04 parallèle** | ~240 N.m | +$400 | +870g | ⭐⭐ |

---

## 3. Solution Retenue — S6 : Courroie GT3

### 3.1 Pourquoi la GT3 et pas le Tirant (S2) ?

Malgré ses qualités, la solution S2 (tirant) présente un problème fondamental : le **point mort géométrique** à forte flexion (31 N.m à 120°) et la fatigue mécanique des pivots rotule. La GT3 résout ces deux problèmes.

Par ailleurs, avec l'adoption de l'architecture **F-A-R pour la hanche** (Pitch→Roll→Yaw), le RS-04 Hip Pitch est maintenant situé **au niveau du bassin/bas du torse**. Il n'est plus adjacent au RS-04 du genou. Cela simplifie considérablement le packaging du haut de cuisse : le RS-04 du genou peut être **relocalisé seul** en haut de cuisse via la GT3 sans interférence avec le RS-04 de la hanche.

> [!IMPORTANT]
> **En architecture F-A-R**, le seul moteur qui descend dans la cuisse via la courroie GT3 est le **RS-04 Knee**. Le RS-04 Hip Pitch reste fixe dans le bassin (Maillon 1 de la chaîne F-A-R). Les deux RS-04 ne sont donc **pas côte à côte** — ce qui avait été envisagé à tort dans la configuration historique R-A-F.

---

### 3.2 Principe de la Solution S6

Au lieu de laisser le RS-04 directement sur l'axe du genou (1:1), on le **déplace en haut de la cuisse** et on relie sa sortie à l'axe du genou via une **courroie GT3 avec réduction 2.5:1**.

```
CONFIGURATION DIRECTE (avant GT3) :
[HANCHE - RS-04 Pitch fixé au bassin] ← Architecture F-A-R
         │
     CUISSE (fémur)
         │
[GENOU - RS-04 Knee sur l'axe]   ← 120 N.m, 167 RPM


CONFIGURATION GT3 (S6) :
[HANCHE - RS-04 Pitch fixé au bassin] ← Architecture F-A-R, inchangé
         │
     CUISSE (haut) : RS-04 Knee RELOCALISÉ + Pignon 20T ←── GT3
         │
         │ Courroie GT3 9mm (~650mm de tour)
         │       Brin moteur : pignon 20T (Ø32mm)
         │       Brin genou  : pignon 50T (Ø51mm)
         │
[GENOU - Grand pignon 50T = AXE GENOU] ← 300 N.m, 67 RPM
```

**Disposition spatiale dans la cuisse (Vue de face, architecture F-A-R confirmée) :**

```
┌────────────────────────────────────────┐
│           BASSIN                       │
│   RS-04 Hip Pitch ← Maillon 1 F-A-R   │
│   Axe Pitch (fixe dans bassin)         │
│       ↓                                │
│   RS-03 Roll  ← Maillon 2             │
│   RS-03 Yaw   ← Maillon 3             │
└──────────────────┬─────────────────────┘
                   │
       ╔═══════════╧═════════════╗
       ║  HAUT CUISSE (fémur)   ║
       ║                        ║
       ║  RS-04 Knee (Relocalisé)║ ← Moteur FIXE à la cuisse
       ║  [||||||] Pignon 20T   ║   via bracket alu CNC
       ╚══════════╤═════════════╝
                  │  Courroie GT3 9mm (~400mm d'entraxe)
                  │
             ◉───┘ Pignon 50T
       ══════╪═════════════════ ← Axe Genou Pitch
             │
          TIBIA
```

> [!TIP]
> **Avantage clé du découplage F-A-R + GT3** : Le RS-04 Hip Pitch (bassin, Maillon 1) et le RS-04 Knee (haut cuisse, via GT3) sont dans deux zones distinctes. Aucun conflit d'encombrement. La cuisse n'abrite que le RS-04 Knee relocalisé, la courroie, et les brackets RS-03 (qui pendent du bassin en Maillons 2-3).

---

### 3.3 Performances Calculées (Ratio 2.5:1)

| Paramètre | Direct Drive (RS-04 1:1) | GT3 2.5:1 (S6) | Δ |
| :--- | :---: | :---: | :---: |
| **Couple genou** | 120 N.m | **300 N.m** | **+150%** |
| **Vitesse max genou** | 167 RPM | **67 RPM** | -60% |
| **Temps flexion 0→90°** | 0.15 s | **0.36 s** | Acceptable |
| Marche 2.5 km/h (vide) | 101% ⚠️ | **39%** ✅ | Très confortable |
| Portage 20 kg marchant | Impossible | **~65%** ✅ | Viable |
| Course 5 km/h | 143% ❌ | **~57%** ✅ | Très confortable |
| Course 8 km/h | 185% ❌ | **~73%** ✅ | Confortable |

> [!IMPORTANT]
> **Pourquoi 2.5:1 et pas 1.5:1 ?** Le genou, contrairement à la hanche, est soumis à des couples énormes (117 N.m en marche normale). Le ratio 2.5:1 amène 300 N.m — une marge qui absorbe aussi bien le portage de 20 kg que les pics de course. Le tirant (S2) plafonnerait à 180 N.m avec son point mort à forte flexion. La GT3 2.5:1 n'a pas ce défaut.

**Alternative ratio 1.5:1 :**

| Paramètre | GT3 1.5:1 |
| :--- | :---: |
| Couple genou | **180 N.m** |
| Vitesse max genou | 111 RPM |
| Marche avec 10 kg | **~85%** ✅ |
| Course 5 km/h | **~96%** ⚠️ (limite thermique) |
| Course 8 km/h | ~122% ❌ |

---

### 3.4 BOM & Masse Ajoutée

| Composant | Spéc. | Qté | Prix | Source |
| :--- | :--- | :---: | :---: | :--- |
| **Courroie GT3 fermée** | GT3, 9mm, ~650mm | 2 (D+G) | ~15€ | Amazon / AliExpress |
| **Pignon moteur** | GT3, 20 dents, alésage Ø8mm alu | 2 | ~8€ | AliExpress |
| **Pignon genou** | GT3, 50 dents, alésage Ø12mm alu | 2 | ~18€ | AliExpress |
| **Galet tendeur** | Roulement 625ZZ Ø16 + bras ressort | 2 | ~5€ | AliExpress |
| **Ressort de tension** | Traction 2N, ~30mm | 2 | ~2€ | Quincaillerie |
| **Visserie + support** | M4 inox + entretoises CNC | lot | ~5€ | — |
| **TOTAL (2 jambes)** | | | **~53€** | |

**Masse ajoutée (2 jambes) :**

| Composant | Masse unit. | ×2 jambes |
| :--- | :---: | :---: |
| Courroie GT3 9mm × 600mm | ~25g | 50g |
| Pignon 20T alu | ~15g | 30g |
| Pignon 50T alu | ~85g | 170g |
| Galet tendeur + ressort | ~20g | 40g |
| Visserie + support | ~15g | 30g |
| **TOTAL** | **~160g/jambe** | **~320g** |

> ✅ **320 grammes pour les deux jambes** — négligeable face aux +2 840g d'un double RS-04 (S4) ou aux +400g d'un tirant (S2).

---

### 3.5 Comparatif GT3 vs Autres Solutions

| Critère | S2 (Tirant) | S4 (2× RS-04) | **S6 (GT3)** |
| :--- | :---: | :---: | :---: |
| **Couple max** | 180 N.m | 240 N.m | **300 N.m** |
| **Masse ajoutée** | ~-670g | **+870g** | **+160g** ⭐ |
| **Coût** | ~150€ | +$400 | **~53€** ⭐ |
| **Point mort à forte flexion** | ⚠️ Oui (31 N.m @ 120°) | Non | **Non** ⭐ |
| **Backlash** | ~0° (rigide) | ~0° | ~0.5-1° |
| **Backdrivability** | Partielle | ✅ | **✅** |
| **Réduction inertie distale** | ✅ (moteur en haut) | ❌ | **✅** ⭐ |
| **Compatibilité F-A-R hanche** | ✅ | ✅ | **✅** ⭐ |
| **Complexité mécanique** | ⭐⭐⭐ (bielles, pivots) | ⭐⭐ | **⭐** ⭐ |

---

### 3.6 Points de Vigilance

**Backlash (jeu angulaire)**
- Courroie GT3 : 0.5-1.5° selon tension.
- **Galet tendeur à ressort permanent** maintient la tension même si la courroie s'allonge avec le temps.
- **Largeur 9mm minimum** : les courroies 6mm ont plus de jeu.
- **Pignons aluminium usiné** — pas imprimés 3D.

**Durée de vie**
- GT3 de qualité (Gates, Continental) : > 10 millions de cycles à 240 N.m.
- Remplacement en cas de rupture : 5 minutes, 15€.

**Alignement**
- Les deux pignons doivent être coplanaires à ±1mm.
- Entretoises CNC ou imprimées PA12-CF pour le calage latéral.

---

### 3.7 Guide de Montage

1. **Fixer le RS-04 Knee** sur un bracket alu en haut de cuisse, arbre de sortie vers le bas (parallèle au fémur).
2. **Installer le pignon 20T** sur l'arbre RS-04 avec vis de serrage.
3. **Installer le grand pignon 50T** directement sur l'axe de rotation du genou.
4. **Enfiler la courroie GT3** autour des deux pignons. Ajuster l'entraxe si nécessaire.
5. **Monter le galet tendeur** (~5-10N de force) sur le brin mou.
6. **Vérifier l'alignement** : faire tourner le moteur à la main — la courroie doit rester centrée sans déport latéral.

---

## 4. Roadmap d'Évolution

| Phase | Solution | Vitesse Course | Délai |
| :--- | :--- | :---: | :---: |
| **V1 (immédiat)** | S1 algorithmique (mid-foot strike + foulée courte) | ~4 km/h | Logiciel |
| **V2 (3-6 mois)** | **S6 : GT3 2.5:1 (300 N.m)** | **~8 km/h** | Mécanique |
| **V3 (1 an)** | GT3 + SEA en torsion (S3) sur le grand pignon | **~10+ km/h** | Avancé |
| **V4 (ambitieux)** | GT3 + solénoïde switchable Direct/GT3 | Mode vitesse / couple | R&D |

> [!IMPORTANT]
> **Priorité V1 : l'algorithme de marche.** La stratégie mid-foot strike est gratuite et implémentable en logiciel pur. C'est le chantier n°1 dès que la marche est validée. La GT3 (V2) est le quickwin mécanique le plus rentable pour passer à la course.

---

*Document fusionné en Avril 2026 (anciens 15d + 15g) — Analyse basée sur τ_genou_course = 177.5 N.m (40.2 kg, 4 km/h, facteur ×2.5), limite RS-04 = 120 N.m. Architecture hanche F-A-R (Pitch→Roll→Yaw) adoptée — RS-04 Knee et RS-04 Hip Pitch dans des zones distinctes (bassin vs haut cuisse).*
