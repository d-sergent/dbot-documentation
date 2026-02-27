# Étude Cheville D-Bot — Historique Évolutif & Architecture Cardan

Ce document retrace l'évolution des solutions envisagées pour la cheville du D-Bot, puis détaille l'architecture finale retenue : un **cardan central DIN 808** couplé à un **système différentiel à 2 bielles** (type Optimus), actionné par **2× RS-03 par cheville**.

---

## 1. Historique des Solutions Étudiées

L'architecture de la cheville a traversé cinq itérations avant d'aboutir au design final.

### Étape 1 — K-Bot Standard (Architecture de Base)
Le K-Bot original utilise un seul **RS-02 monté en haut du tibia**, actionné via un mécanisme de **tirant (pushrod)** avec un ratio de levier ~2:1.
- **Couple effectif** : ~34 N.m (17 N.m × 2)
- **DOF** : 1 seul (Pitch)
- **Roll** : ❌ Absent
- **Problème** : Pas de stabilité latérale, marche uniquement sur sol plat.

### Étape 2 — Rotule GE12UK (Premier Pivot Envisagé)
Tentative d'ajout d'un pivot central avec une **rotule radiale GE12UK** (roulement lisse sphérique).
- **Débattement** : ±15° seulement
- **Problème** : Débattement insuffisant pour marcher sur des pentes, s'accroupir ou absorber les chocs. Le mécanisme arrive en butée mécanique rapidement, risquant de casser les pièces PA12-CF ou de griller les moteurs.
- **Verdict** : ❌ Écarté — limite cinématique trop basse.

### Étape 3 — Ajout RS-00 Roll Direct-Drive (D-Bot V1)
Ajout d'un **RS-00** (14 N.m, 310g) monté directement à la cheville pour le Roll, en conservant le RS-02+tirant pour le Pitch.
- **DOF** : 2 (Pitch + Roll)
- **Avantage** : Simple à implémenter, assemblage trivial.
- **Problème** : 310g de masse distale (inertie oscillante), RS-02+tirant toujours limité à ~34 N.m pour le Pitch (marche rapide impossible).
- **Analyse** : Voir [Analyse Biomécanique §7](./15_Analyse_Biomecanique.md).

### Étape 4 — RS-06 "Sweet Spot" avec Tirant (D-Bot V2)
Remplacement du RS-02 par un **RS-06** (36 N.m, 621g) dans le tibia, avec tirant.
- **Couple Pitch effectif** : ~72 N.m (36 × 2)
- **Avantage** : Double le couple pour seulement +75g, marche rapide possible.
- **RS-00 Roll conservé** (14 N.m).
- **Analyse** : Voir [Cinématique §4.5](./14_Cinematique_Moteurs.md).
- **Verdict** : ⚠️ Solution correcte mais le Roll reste au pic en marche rapide.

### Étape 5 — Architecture Cardan + Double Bielles (RETENUE ✅)
Abandon du tirant au profit d'un **cardan central** (DIN 808, acier C45) + **2 bielles rotulées** actionnées par **2× RS-03** par cheville.
- **Couple Pitch** : 120 N.m (2× 60 N.m en mode synchrone)
- **Couple Roll** : 120 N.m (2× 60 N.m en mode différentiel)
- **Masse distale** : ~0g (moteurs en haut du tibia)
- **Inspiré de** : Tesla Optimus (mécanisme à bielles parallèles)
- **Verdict** : ✅ **Architecture finale du D-Bot.**

---

## 2. Architecture Retenue — Cheville Différentielle à Cardan

### Principe de Fonctionnement

La cheville fonctionne en "trépied" :
- Le **Cardan Central** : Supporte 100% du poids du robot (~38-40 kg). Il permet un débattement très élevé (+30°/−45° en Pitch, ±25° en Roll) sans butée structurelle.
- Les **2 Bielles (Pushrods) à l'Arrière** : Reliées chacune à un RS-03 monté en haut du tibia.

```
      ┌─────┐
      │GENOU│
      └──┬──┘
         │
    ╔════╧════╗   ╔════╧════╗
    ║ RS-03 A ║   ║ RS-03 B ║  ← 2 moteurs HAUT du tibia
    ╚════╤════╝   ╚════╤════╝    (chacun 60 N.m pic, 880g)
         │             │
         │ Bielle A    │ Bielle B    ← Tubes carbone 3K
         │ (rotule M5) │ (rotule M5)   Ø10/8mm
         │             │
         ╰──────┬──────╯
                │
           ╔════╧════╗
           ║ CARDAN  ║  ← DIN 808, Série G, Acier C45
           ║ (pivot) ║    Supporte 100% du poids
           ╚════╤════╝
           ┌────┴────┐
           │  PIED   │
           └─────────┘

    A↓ + B↓ (même sens)    = PITCH (flexion/extension)
    A↓ + B↑ (sens opposé) = ROLL  (inversion/éversion)
```

### Bilan des Performances

| Paramètre | Valeur |
| :--- | :--- |
| **Couple Pitch effectif** | 120 N.m (2× RS-03 synchrones) |
| **Couple Roll effectif** | 120 N.m (2× RS-03 différentiels) |
| **Marge vs besoin statique (33 N.m)** | **+260%** |
| **Masse distale** | ~0g (moteurs haut du tibia) |
| **Débattement Pitch** | +30° / −45° |
| **Débattement Roll** | ±25° |
| **DOF total jambe** | 6 (Hanche P/R/Y + Genou + Cheville P/R) |
| **Moteurs par jambe** | 6 (2× RS-04 + 2× RS-03 hanche + 2× RS-03 cheville) |

---

## 3. Achats et Montage

### A. Joint de Cardan Central
Joint de cardan simple **Série G** (douilles lisses, résistantes aux chocs), norme DIN 808, acier C45, axe 12 mm.
- **Mouvement** : la transmission de couple se fait par montage à **rainure de clavette (Keyway)** de 4 mm.
- **Fournisseurs France** :
  - **Michaud Chailly** : Réf. A5-473-12 (qualité premium, option rainure).
  - **HPC Europe** : Réf. UJ-12.

### B. Fixation et Maintien Axial
L'axe en acier rectifié (12mm h6) doit être immobilisé axialement :
- **Bagues d'arrêt (Shaft Collars)** en acier, 2 parties (fendues), de chaque côté du cardan.
  - **HPC Europe** : BAG2-012 ou **Michaud Chailly / Ruland** : F2-39-12. Vis de classe 12.9.

### C. Bielles (Pushrods) et Rotules
- **Bielles** : Tubes carbone 3K (Ø ext 10mm / Ø int 8mm) — rigidité maximale, pas de flambement.
- **Rotules d'extrémité** : Embouts M5.
  - **Igus EBRM-05** (polymère, ultra léger)
  - **SAK 5 C** (acier/PTFE, sur 123Roulement).

### D. Protection (Soufflet)
Soufflet de protection en néoprène (vendu en option avec le cardan chez RS, Michaud ou HPC). Indispensable pour protéger l'articulation de la poussière.

---

## 4. Impact sur la Configuration Globale

L'adoption de cette architecture modifie la configuration moteur des jambes :

| Articulation | Moteur | Qté (×2 jambes) | Couple | Note |
| :--- | :---: | :---: | :---: | :--- |
| Hanche Pitch | RS-04 | 2 | 120 N.m | Inchangé (K-Bot) |
| Hanche Roll | RS-03 | 2 | 60 N.m | Inchangé |
| Hanche Yaw | RS-03 | 2 | 60 N.m | Inchangé |
| Genou Pitch | RS-04 | 2 | 120 N.m | Inchangé |
| **Cheville A** | **RS-03** | **2** | **60 N.m** | **NOUVEAU** (remplace RS-02 tirant) |
| **Cheville B** | **RS-03** | **2** | **60 N.m** | **NOUVEAU** (remplace RS-00 Roll) |

**Total moteurs jambes** : 12 (au lieu de 10 pour K-Bot + 2 RS-00 Roll précédents)
**Surpoids** : +2× (880g − 405g) + 2× (880g − 310g) = +950g + 1140g = **+2.09 kg** vs V1.
**Surcoût** : +2× ($250 − $160) + 2× ($250 − $135) = +$180 + $230 = **+$410** vs V1.

> [!IMPORTANT]
> **Ce surpoids est en position BASSE (tibia)**, donc l'impact sur le centre de gravité est minimal. L'avantage de couple (+260% de marge) et la suppression de toute masse distale (~0g vs 310g/cheville) compensent largement.

---
*Étude réalisée en Février 2026. Basée sur les analyses biomécaniques documentées dans les Annexes 14 et 15.*
