# 29 - Étude Structurale : Squelette Aluminium du Torse

Ce document détaille la conception du squelette interne rigide en aluminium du D-Bot. L'approche retenue est celle d'une **cage tubulaire boulonnée** (sans soudure), assemblée par des nœuds CNC usinés sur la Carvera / CNC C500.

## 1. Hypothèses Dimensionnelles (V1)

Les dimensions du torse sont les premières hypothèses de travail pour le dimensionnement structurel :

| Paramètre | Valeur | Note |
| :--- | :---: | :--- |
| **Hauteur** (Épaule → Hanche) | **420 mm** | Distance entre la traverse haute et la traverse basse |
| **Largeur** (Face, Droite ↔ Gauche) | **300 mm** | Entraxe entre les montants verticaux latéraux |
| **Profondeur** (Avant ↔ Arrière) | **220 mm** | Épaisseur du torse (plan sagittal) |

> [!IMPORTANT]
> Ces dimensions sont des **hypothèses initiales**. Elles seront affinées lors de la modélisation CAO (Fusion 360) en fonction de l'encombrement réel des composants internes (Batterie 12S, Jetson Orin Nano, PDB Matek, câblage CAN).

## 2. Architecture : Cage Tubulaire Boulonnée

### Principe
Le torse est constitué de **profilés creux en aluminium** (tubes rectangulaires) assemblés sans soudure par des **nœuds de jonction** usinés CNC en aluminium 6061-T6.

**Pourquoi pas de soudure ?**
La soudure TIG/MIG détruit localement le traitement thermique T6, réduisant la résistance de l'aluminium 6060 de ~50% dans la zone affectée thermiquement (ZAT). L'assemblage boulonné conserve 100% des propriétés mécaniques.

### Schéma de la Cage (Vue de Face)

```text
    ← 300 mm (Largeur) →
    ┌─────────────────────┐  ─┬─
    │   Traverse Haute    │   │
    │   (Épaules 35x35)   │   │
    ├─────────────────────┤   │
    │ ↑                 ↑ │   │
    │ │  Montant        │ │   │
    │ │  Vertical       │ │   │  420 mm
    │ │  (40x40)        │ │   │  (Hauteur)
    │ │                 │ │   │
    │ ↓                 ↓ │   │
    ├─────────────────────┤   │
    │   Traverse Basse    │   │
    │   (Hanches 60x60)   │  ─┴─
    └─────────────────────┘
```

### Schéma de la Cage (Vue de Dessus)

```text
    ← 300 mm (Largeur) →
    ┌─────────────────────┐  ─┬─
    │ ■                 ■ │   │
    │ Montant           Montant│ 220 mm
    │ (40x40)           (40x40)│ (Profondeur)
    │ ■                 ■ │   │
    └─────────────────────┘  ─┴─
         (4 montants, un à chaque coin)
```

### Schéma 3D Simplifié (Perspective Isométrique)

```text
        Traverse Haute (35x35)
        ┌──────────────────┐
       /│                 /│
      / │    Épaule      / │
     /  │     G         /  │  Épaule D
    ┌───┼──────────────┐   │
    │   │              │   │
    │   │ Montant 40x40│   │  ← 420 mm
    │   │              │   │
    │   │              │   │
    │   └──────────────┼───┘
    │  /               │  /
    │ /  Traverse Basse│ /   (60x60)
    │/   (Hanches)     │/
    └──────────────────┘
    ↕         ↔          ↕
  220mm    300mm       220mm
```

## 3. Choix des Matériaux

| Composant | Alliage | Justification |
| :--- | :--- | :--- |
| **Tubes (Profilés creux)** | **Alu 6060 T6** | Standard, économique, disponible en tubes de 20x20 à 60x60. Re ≈ 150 MPa. |
| **Nœuds de jonction (CNC)** | **Alu 6061 T6** | Plus dur (Re ≈ 275 MPa), meilleur usinage, résiste mieux aux concentrations de contraintes aux jonctions. |
| **Boulonnerie** | **M6 Acier 12.9** | Obligatoire pour un robot de 40 kg. M4 insuffisant pour les jonctions structurelles du châssis. |
| **Coques extérieures** | **PETG-CF (Impression 3D)** | Viennent refermer la cage. Aucun rôle structurel, uniquement esthétique et protection câblage. |

## 4. Dimensionnement Structurel (Robot 40 kg)

### Hypothèses de Chargement
- **Masse totale robot** : 40 kg → Poids statique P = 40 × 9.81 ≈ **392 N**
- **Facteur dynamique (Marche)** : ×2.5 à ×3 (impacts au sol, accélérations)
- **Force de design** : F_dyn = 392 × 3 ≈ **1 180 N** (cas majorant)
- **Couple de torsion (Hanches)** : Les RS-04 (120 N.m peak) exercent un moment de réaction sur la traverse basse

### Analyse par Composant

#### A. Montants Verticaux (4x Tubes 40×40×2 mm, Alu 6060 T6)

Les montants verticaux reprennent la compression axiale (poids du haut du corps) et la flexion latérale (porte-à-faux des épaules).

| Paramètre | Valeur |
| :--- | :--- |
| Section | 40 × 40 mm, épaisseur 2 mm |
| Aire de section | A = 4 × (40 × 2) - 4 × (2 × 2) = 304 mm² |
| Moment d'inertie | I ≈ 70 700 mm⁴ |
| Longueur libre (hauteur torse) | **420 mm** |
| **Contrainte compression** (P/4 par montant) | σ = (1180/4) / 304 ≈ **0.97 MPa** |
| **Limite élastique 6060 T6** | Re = 150 MPa |
| **Facteur de sécurité (Compression)** | **FS ≈ 155** ✅ (Très confortable) |

**Vérification Flambage (Euler)** :
- Pcr = π² × E × I / L² = π² × 69 000 × 70 700 / 420² ≈ **272 kN** par montant
- Charge appliquée par montant ≈ 295 N
- **FS flambage ≈ 922** ✅ (Aucun risque)

#### B. Traverse Basse / Hanches (60×60×2 mm, Alu 6060 T6)

C'est la pièce la plus sollicitée : elle reprend le couple de torsion des moteurs RS-04 de hanche et les charges de flexion des jambes.

| Paramètre | Valeur |
| :--- | :--- |
| Section | 60 × 60 mm, épaisseur 2 mm |
| Moment d'inertie (Flexion) | I ≈ 230 000 mm⁴ |
| Moment d'inertie polaire (Torsion) | J ≈ 350 000 mm⁴ |
| Portée libre (largeur torse) | **300 mm** |
| **Couple de torsion appliqué** | M_t = 120 N.m (pic RS-04) |
| **Contrainte de torsion** | τ = M_t × (d/2) / J ≈ 120 000 × 30 / 350 000 ≈ **10.3 MPa** |
| **Contrainte de flexion** (charge jambe) | σ_f = F × L / (4 × W) ≈ **5.1 MPa** |
| **Contrainte combinée (Von Mises)** | σ_eq ≈ √(σ² + 3τ²) ≈ √(26 + 318) ≈ **18.6 MPa** |
| **Limite élastique** | 150 MPa |
| **Facteur de sécurité** | **FS ≈ 8.1** ✅ |

> [!TIP]
> La traverse basse de 60×60 offre un facteur de sécurité de 8, ce qui est excellent. Cela laisse de la marge pour les chocs et les mouvements brusques lors de la marche.

#### C. Traverse Haute / Épaules (35×35×2 mm, Alu 6060 T6)

Moins sollicitée que la traverse basse. Elle reprend le poids des bras (~4 kg par bras en incluant les moteurs) et les moments de flexion des épaules.

| Paramètre | Valeur |
| :--- | :--- |
| Section | 35 × 35 mm, épaisseur 2 mm |
| Moment d'inertie | I ≈ 36 200 mm⁴ |
| Portée libre (largeur torse) | **300 mm** |
| **Charge par bras** | ~40 N (4 kg × 9.81) |
| **Moment de flexion** | M = 40 × 150 = 6 000 N.mm |
| **Contrainte de flexion** | σ = M × c / I = 6 000 × 17.5 / 36 200 ≈ **2.9 MPa** |
| **Facteur de sécurité** | **FS ≈ 52** ✅ |

### Résumé des Facteurs de Sécurité

| Composant | Section (mm) | Contrainte Max (MPa) | FS | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| Montants verticaux | 40×40×2 | 0.97 | **155** | ✅ Très sûr |
| Traverse basse (Hanches) | 60×60×2 | 18.6 | **8.1** | ✅ Robuste |
| Traverse haute (Épaules) | 35×35×2 | 2.9 | **52** | ✅ Confortable |

## 5. Estimation de Masse du Squelette

| Pièce | Section | Longueur | Quantité | Masse unitaire | Total |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Montant vertical | 40×40×2 | 420 mm | 4 | ~136 g | **544 g** |
| Traverse basse (Largeur) | 60×60×2 | 300 mm | 2 | ~190 g | **380 g** |
| Traverse basse (Profondeur) | 60×60×2 | 220 mm | 2 | ~139 g | **278 g** |
| Traverse haute (Largeur) | 35×35×2 | 300 mm | 2 | ~108 g | **216 g** |
| Traverse haute (Profondeur) | 35×35×2 | 220 mm | 2 | ~79 g | **158 g** |
| Nœuds CNC (8 angles) | Blocs 6061 | ~50×50×50 | 8 | ~50 g | **400 g** |
| Boulonnerie M6 | - | - | ~48 | ~8 g | **384 g** |
| | | | | **TOTAL** | **≈ 2.36 kg** |

> Le squelette représente environ **5.9%** de la masse totale du robot (40 kg). C'est un ratio excellent pour une structure primaire.

## 6. Nœuds de Jonction (Usinés CNC)

### Principe d'Assemblage
Chaque coin de la cage est connecté par un **nœud tri-axial** usiné dans un bloc d'aluminium 6061 T6. Le nœud comporte des tenons cylindriques ou rectangulaires qui s'insèrent à l'intérieur des tubes creux.

```text
     Tube 35x35            Tube 35x35
     (Traverse)            (Traverse)
         │                     │
         ▼                     ▼
    ┌────┤     ┌───────┐      ├────┐
    │    │     │       │      │    │
    │    └─────┤ NOEUD ├──────┘    │
    │          │  CNC  │           │
    │          │ (6061)│           │
    │          └───┬───┘           │
    │              │               │
    │              ▼               │
    │         Tube 40x40           │
    │         (Montant)            │
```

### Spécifications d'Usinage
- **Matériau brut** : Bloc Alu 6061 T6, ~50×50×50 mm
- **Tolérances tenons** : Ajustement glissant **h7/H7** (insertion manuelle, sans jeu excessif)
- **Fixation** : 2× vis M6 par face de tenon (traversantes à travers le tube)
- **Frein filet** : Loctite 243 (Moyen) sur toutes les vis M6 du châssis

## 7. Intégration avec les Autres Systèmes

### Points de Fixation sur la Cage
| Zone | Composant Fixé | Type de Fixation |
| :--- | :--- | :--- |
| Traverse haute (face) | Moteurs RS-04 Épaule (via platine) | Vis M5 + Inserts |
| Traverse haute (dessus) | Moteurs RS-05 Cou (via platine) | Vis M4 |
| Traverse basse | Cluster RS-04 Hanche (×2) | Vis M6 directement dans le nœud |
| Montants latéraux | Platines PDB Matek, Jetson | Vis M3 dans des inserts taraudés collés |
| Montant arrière | Batterie 12S (sur glissière) | Rails alu + sangle Velcro |
| Coques PETG-CF | Fermeture esthétique | Vis M3 dans inserts Ruthex sur la coque |

### Passage de Câbles
Les tubes creux de 40×40 peuvent servir de **chemin de câbles intégré** pour le bus CAN et l'alimentation, protégeant naturellement les fils des EMI et des pincements.

## 8. Prochaines Étapes

1. **Modélisation CAO (Fusion 360)** : Dessiner la cage complète avec les nœuds et vérifier l'encombrement interne.
2. **Commande Tubes** : Sourcer les tubes 6060 T6 aux bonnes longueurs (fournisseurs : Bikar Metalle, Thyssenkrupp Materials France).
3. **Usinage Nœuds** : Programmer les parcours CNC pour les 8 nœuds d'angle sur la Carvera / C500.
4. **Prototypage** : Assembler un premier cadre à blanc pour valider les ajustements avant de fixer les composants.
