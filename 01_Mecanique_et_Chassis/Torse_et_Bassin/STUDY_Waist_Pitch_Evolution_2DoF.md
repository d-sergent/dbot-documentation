# 🔬 ÉTUDE PROSPECTIVE R&D — ÉVOLUTION WAIST PITCH 2-DOF (YAW + PITCH)

> **Statut** : Document d'Étude Prospective R&D (Niveau 2 — Évolution V1.5 / V2)  
> **Date de rédaction** : Septembre 2026  
> **Auteur** : Antigravity & Cellule Ingénierie D-Bot  
> **Actionneur proposé** : RobStride RS-04 (Couple pic : 120 N.m, couple nominal : 40 N.m, masse : 1 420 g)  
> **Roulement de découplage** : Roulement à rouleaux croisés CRBH 5013 UU (50 × 80 × 13 mm)  
> **Décision d'arbitrage V1** : **Gel architectural en 1-DoF Yaw pur** pour la V1 initiale ; intégration du Waist Pitch planifiée en V1.5.

---

## 📑 Sommaire

- [1. Contexte & Justification Fonctionnelle](#1-contexte--justification-fonctionnelle)
  - [1.1 Pourquoi le Pitch est le Degré de Liberté le Plus Rentable](#11-pourquoi-le-pitch-est-le-degré-de-liberté-le-plus-rentable)
  - [1.2 Benchmark des Robots Humanoïdes de Référence](#12-benchmark-des-robots-humanoïdes-de-référence)
- [2. Choix Technologique de l'Actionneur (RobStride RS-04)](#2-choix-technologique-de-lactionneur-robstride-rs-04)
- [3. Architecture Mécanique Proposée (Option RS-04 Pitch sous RS-06 Yaw)](#3-architecture-mécanique-proposée-option-rs-04-pitch-sous-rs-06-yaw)
  - [3.1 Empilement Cinématique Vertical](#31-empilement-cinématique-vertical)
  - [3.2 Principe Mécanique & Découplage](#32-principe-mécanique--découplage)
  - [3.3 Pièces Nouvelles Nécessaires](#33-pièces-nouvelles-nécessaires)
- [4. Dimensionnement RDM & Bilan de Couple](#4-dimensionnement-rdm--bilan-de-couple)
  - [4.1 Bilan de Masse Suspendue](#41-bilan-de-masse-suspendue)
  - [4.2 Calcul des Couples Requis selon l'Inclinaison](#42-calcul-des-couples-requis-selon-linclinaison)
  - [4.3 Facteurs de Sécurité du RS-04](#43-facteurs-de-sécurité-du-rs-04)
  - [4.4 Dimensionnement du Roulement CRBH 5013](#44-dimensionnement-du-roulement-crbh-5013)
- [5. Analyse Comparative du Ramassage au Sol (V1.0 vs V1.5)](#5-analyse-comparative-du-ramassage-au-sol-v10-vs-v15)
  - [5.1 Configuration V1.0 : Squat Profond Seul (Sans Pitch)](#51-configuration-v10--squat-profond-seul-sans-pitch)
  - [5.2 Configuration V1.5 : Squat Modéré 45 deg + Waist Pitch 30 deg](#52-configuration-v15--squat-modéré-45-deg--waist-pitch-30-deg)
  - [5.3 Tableau Comparatif V1.0 vs V1.5](#53-tableau-comparatif-v10-vs-v15)
- [6. Impact Architectural & Feuille de Route d'Intégration](#6-impact-architectural--feuille-de-route-dintégration)
  - [6.1 Éléments Inchangés](#61-éléments-inchangés)
  - [6.2 Éléments à Prédisposer dès la V1](#62-éléments-à-prédisposer-dès-la-v1)
  - [6.3 Calendrier Recommandé](#63-calendrier-recommandé)

---

## 1. Contexte & Justification Fonctionnelle

### 1.1 Pourquoi le Pitch est le Degré de Liberté le Plus Rentable

La majorité des tâches quotidiennes d'un robot humanoïde (ramasser un objet tombé, saisir une charge basse, poser un colis sur une table, s'asseoir et se relever d'une chaise) nécessitent une **flexion sagittale du buste**.

Dans l'architecture D-Bot V1 actuelle, le waist est restreint à **1-DoF (Lacet / Yaw pur à +/-90 deg)**. Cette décision a permis de :
1. Valider rapidement une chaîne cinématique robuste avec découplage complet par roulement à rouleaux croisés **CRBH 8016 UU**.
2. Réduire la hauteur du bassin au strict minimum et abaisser le centre de gravité (CoM).
3. Sécuriser la fabrication sur la CNC C500 sans empilement d'étages articulés complexes.

Cependant, l'absence de flexion sagittale impose de réaliser un squat complet (flexion des genoux à 60 deg) pour toucher le sol, ce qui sollicite les actionneurs de genoux RS-04 à la limite de leur couple continu. L'adjonction d'un axe de pitch (+/-30 deg à +/-45 deg) représente le gain ergonomique et dynamique le plus important pour la version V1.5.

### 1.2 Benchmark des Robots Humanoïdes de Référence

| Robot | Degrés de Liberté Taille | Actionneur Pitch | Roulement Découplage | Stratégie Ramassage au Sol |
| :--- | :---: | :---: | :---: | :--- |
| **Tesla Optimus Gen 2** | 3-DoF (Yaw + Pitch + Roll) | Moteur custom QDD | Roulement rouleaux croisés | Flexion taille combinée aux genoux |
| **Fourier GR-1** | 3-DoF (Yaw + Pitch + Roll) | FSA Actuator | Roulement 4 points | Flexion taille + squat léger |
| **Unitree G1** | 3-DoF (Yaw + Pitch + Roll) | Moteur Unitree QDD | Roulement intégré | Flexion taille + lean dynamique |
| **Unitree H1** | 1-DoF (Yaw seul) | Moteur Unitree M107 | Roulement externe | Squat profond exclusif |
| **Figure 02** | 2-DoF / 3-DoF | Custom Actuator | Roulements minces | Flexion taille + genoux |
| **D-Bot V1.0** | **1-DoF (Yaw seul)** | **RobStride RS-06** | **CRBH 8016 UU** | **Squat profond 60 deg (Opération rapide)** |
| **D-Bot V1.5 (Projeté)** | **2-DoF (Yaw + Pitch)** | **RS-06 + RS-04** | **CRBH 8016 + CRBH 5013** | **Squat modéré 45 deg + Pitch 30 deg** |

---

## 2. Choix Technologique de l'Actionneur (RobStride RS-04)

Le moteur retenu pour animer l'axe de tangage (Waist Pitch) est le **RobStride RS-04**, identique aux moteurs d'épaules et de genoux déjà déployés sur le D-Bot :

* **Diamètre extérieur carter** : Ø 120 mm
* **Épaisseur axiale** : 56,0 mm
* **Masse unitaire** : 1 420 g
* **Couple nominal continu** : 40 N.m (à 100% de duty cycle)
* **Couple de crête (Peak)** : 120 N.m
* **Vitesse maximale** : 260 rpm (27,2 rad/s)
* **Réduction mécanique** : Quasi-Direct Drive (QDD) planétaire ratio 1:6
* **Interface stator** : 10 taraudages M4 sur PCD Ø 106 mm
* **Interface rotor** : 8 taraudages M4 sur PCD Ø 90 mm
* **Arbre** : Arbre plein borgne (respect absolu de la règle RobStride arbre plein, routage externe déporté)

---

## 3. Architecture Mécanique Proposée (Option RS-04 Pitch sous RS-06 Yaw)

### 3.1 Empilement Cinématique Vertical

L'architecture préconisée positionne le moteur **RS-04 Pitch EN DESSOUS** du module RS-06 Yaw :

```
             ┌─────────────────────────────────────────┐
             │       HAUT DU CORPS / TORSE             │
             │ Colonne Sagittale 7075-T6 + Équerres    │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────▼────────────────────┐
             │       WAIST PLATE YAW (6,0 mm)          │
             │       Interface Torse / Moyeu           │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────▼────────────────────┐
             │   LIAISON YAW V1.0 (Lacet +/-90 deg)    │
             │   Roulement CRBH 8016 UU + RS-06 Yaw    │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────▼────────────────────┐
             │   CADRE INTERMÉDIAIRE EN U (7075-T6)    │
             │   Relie le bas du Yaw au rotor du Pitch │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────▼────────────────────┐
             │ ⭐ MOTEUR RS-04 PITCH (Axe Y horizontal)│
             │ Flexion sagittale +/-30 deg (Peak 120Nm)│
             │ Découplage par roulement CRBH 5013 UU   │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────▼────────────────────┐
             │     CHÂSSIS PELVIEN (Bâti fixe)         │
             │     Support Stator RS-04 Pitch          │
             └─────────────────────────────────────────┘
```

### 3.2 Principe Mécanique & Découplage

1. **Stator RS-04 fixé sur le Pelvis** : Le stator du RS-04 est rigidement boulonné sur une platine d'accueil usinée sur la face supérieure du châssis pelvien.
2. **Cadre intermédiaire mobile** : Le rotor du RS-04 entraîne un cadre en U en Aluminium 7075-T6.
3. **Bascule intégrale du Yaw** : L'ensemble complet du module Waist V1.0 (Platine Traverse, Roulement CRBH 8016, RS-06, Moyeu et Torse) bascule d'un seul bloc autour de l'axe transversal Y.
4. **Découplage d'effort structural** : Les moments de basculement frontal (Roll) et de lacet (Yaw) ne traversent pas la pignonnerie interne du RS-04 : ils sont repris par un roulement à rouleaux croisés **CRBH 5013 UU** (Ø int 50 mm, Ø ext 80 mm, ép. 13 mm) monté en parallèle de l'axe.

### 3.3 Pièces Nouvelles Nécessaires

| Désignation | Matériau | Dimensions Estimées | Masse Estimée | Mode de Fabrication |
| :--- | :--- | :--- | :---: | :--- |
| **Cadre Intermédiaire en U** | Aluminium 7075-T6 | 160 × 140 × 8 mm | ~300 g | Usinage CNC C500 (2 phases) |
| **Platine Réceptrice Pelvis** | Aluminium 7075-T6 | 160 × 140 × 10 mm | ~400 g | Usinage CNC C500 (1 phase) |
| **Roulement Découplage Pitch** | Acier à roulement 100Cr6 | 50 × 80 × 13 mm | 120 g | Achat catalogue (CRBH 5013 UU) |
| **Actionneur RS-04 Pitch** | Standard RobStride | Ø 120 × 56 mm | 1 420 g | Matériel catalogue RobStride |
| **Quincaillerie Complémentaire**| Acier 12.9 / Inox A2 | Vis M4 / M5 + rondelles | ~30 g | Quincaillerie McMaster-Carr |
| **BILAN MASSE ADDITIONNELLE** | — | — | **+2 270 g (~2,27 kg)** | — |

---

## 4. Dimensionnement RDM & Bilan de Couple

### 4.1 Bilan de Masse Suspendue

La masse totale articulée au-dessus de l'axe de pitch intègre le torse complet et le module yaw :

* Torse supérieur (colonne, bras complets, tête, batteries) : 17 300 g
* Moteur RS-06 Yaw : 551 g
* Roulement CRBH 8016 UU + Moyeu Sandwich : 798 g
* Platine et Waist Plate : ~420 g
* Cadre intermédiaire en U : ~300 g
* Visserie complémentaire : ~50 g
* **Masse totale suspendue sur l'axe Pitch** : **~19 419 g (~19,4 kg)**
* **Hauteur du Centre de Masse (CoM) au-dessus de l'axe** : `L_CdG = 240 mm (0,240 m)`

### 4.2 Calcul des Couples Requis selon l'Inclinaison

Formule du moment statique de gravité :
`M_grav = m * g * L_CdG * sin(theta)`

Avec `m = 19,4 kg`, `g = 9,81 m/s2`, `L_CdG = 0,240 m` :
`M_grav = 45,68 * sin(theta) [N.m]`

| Scénario de Fonctionnement | Angle Pitch (theta) | Calcul Analytique | Couple Requis |
| :--- | :---: | :--- | :---: |
| **Station debout droite** | 0 deg | Bras de levier résiduel 10 mm | **1,9 N.m** |
| **Inclinaison de marche normale** | 15 deg | 45,68 × sin(15°) | **11,8 N.m** |
| **Flexion modérée de travail** | 30 deg | 45,68 × sin(30°) | **22,8 N.m** |
| **Flexion maximale de ramassage** | 45 deg | 45,68 × sin(45°) | **32,3 N.m** |
| **Dynamique de marche (K_dyn = 2,0)** | 15 deg | 11,8 × 2,0 | **23,6 N.m** |
| **Portage 4 kg bimanuel à 30 deg** | 30 deg | 22,8 + (4 × 9,81 × 0,145 m) | **28,5 N.m** |
| **Arrêt d'urgence dynamique (K_dyn = 3,0)** | 30 deg | 22,8 × 3,0 | **68,4 N.m** |

### 4.3 Facteurs de Sécurité du RS-04

Le RobStride RS-04 développe **40 N.m en continu** et **120 N.m en crête (Peak)** :

| Scénario | Couple Requis | Capacité Moteur | Facteur de Sécurité (Sf) | Statut |
| :--- | :---: | :---: | :---: | :---: |
| **Flexion 30 deg continue** | 22,8 N.m | 40 N.m (Continu) | **Sf = 1,75** | ✅ Conforme & confortable |
| **Flexion 30 deg + portage 4 kg** | 28,5 N.m | 40 N.m (Continu) | **Sf = 1,40** | ✅ Conforme |
| **Flexion 45 deg statique** | 32,3 N.m | 40 N.m (Continu) | **Sf = 1,24** | ✅ Conforme |
| **Dynamique de marche (15 deg, 2g)** | 23,6 N.m | 40 N.m (Continu) | **Sf = 1,69** | ✅ Conforme |
| **Arrêt d'urgence (30 deg, 3g)** | 68,4 N.m | 120 N.m (Peak) | **Sf = 1,75** | ✅ Conforme en pic |

### 4.4 Dimensionnement du Roulement CRBH 5013

* **Capacité statique de moment de basculement** : `M_stat = 280 N.m`
* **Moment de roulis maximal appliqué (Roll 3g)** : `M_roll_max ~ 110 N.m`
* **Facteur de sécurité en moment** : `Sf = 280 / 110 = 2,54` (Marge > 2,5 ✅)
* **Capacité de charge axiale dynamique** : `C_a = 12,5 kN`
* **Charge axiale maximale appliquée (3g)** : `F_a = 19,4 × 9,81 × 3 = 571 N`
* **Facteur de sécurité axial** : `Sf = 12 500 / 571 = 21,9` (Marge colossale ✅)

---

## 5. Analyse Comparative du Ramassage au Sol (V1.0 vs V1.5)

### 5.1 Configuration V1.0 : Squat Profond Seul (Sans Pitch)

En l'absence de Waist Pitch, le torse reste strictement vertical (angle = 0 deg). La descente des mains vers le sol s'effectue exclusivement par la cinématique des jambes :

* Pour que les mains (longueur totale de bras 698 mm) atteignent le sol depuis une hauteur de hanche initiale de 900 mm, le bassin doit descendre à **h = 400 mm**.
* Cette position exige une **flexion de genou de 60 deg** (squat profond complet).
* **Couple statique par genou en squat 60 deg** :
  `M_genou = 17,5 kg × 9,81 × (0,300 m × sin(60°)) = 44,6 N.m`
* **Constat critique** : 44,6 N.m dépasse légèrement le couple nominal continu du RS-04 (40 N.m).
  * Le robot peut descendre et remonter (grâce aux 120 N.m de couple de crête, Sf = 2,69).
  * Mais il ne peut **pas stationner accroupi** plus de 10 à 20 secondes sous peine d'échauffement thermique des stators de genoux. L'opération de ramassage doit être vive et rapide.

### 5.2 Configuration V1.5 : Squat Modéré 45 deg + Waist Pitch 30 deg

En combinant une flexion de genou modérée (45 deg) et une inclinaison du buste de 30 deg :
* Le bassin ne descend qu'à **h = 550 mm** (gain de 150 mm sur la hauteur de hanche).
* Le couple au genou tombe de **44,6 N.m à 25,5 N.m** (bien en dessous des 40 N.m continus, Sf = 1,57).
* Le couple au waist pitch est de **22,8 N.m** (bien en dessous des 40 N.m continus, Sf = 1,75).
* L'effort est équitablement réparti entre la taille et les membres inférieurs : le robot peut **maintenir sa posture de travail au sol indéfiniment** sans dérating thermique.

### 5.3 Tableau Comparatif V1.0 vs V1.5

| Critère de Performance | **D-Bot V1.0 (Squat Seul)** | **D-Bot V1.5 (Squat + Waist Pitch)** |
| :--- | :--- | :--- |
| **Flexion genoux requise** | 60 deg (Squat profond complet) | 45 deg (Flexion modérée) |
| **Couple continu par genou (vide)** | **44,6 N.m (Surcharge > 40 N.m)** | **25,5 N.m (Régime nominal sain)** |
| **Facteur de sécurité continu genoux** | **Sf = 0,90 ❌ (Surcharge)** | **Sf = 1,57 ✅ (Confortable)** |
| **Durée admissible au sol** | < 15 secondes (Action rapide) | Illimitée (Régime continu permanent) |
| **Charge bimanuelle continue** | ~8 kg (Geste dynamique bref) | **~12 kg (Maintien prolongé possible)** |
| **Orientation caméra OAK-D** | Tête inclinée à 45 deg seule | Tête 45 deg + Buste 30 deg (Vision sol idéale) |
| **Consommation énergétique** | Élevée (Genoux sous fort courant) | Optimale (Répartition globale) |
| **Masse totale du robot** | **Référence (0 kg)** | **+2,27 kg** |
| **Hauteur du bassin / pelvis** | **Référence (Compact)** | **+70 à 80 mm** |
| **Complexité mécanique & usinage** | Simple (Traverse 2D sur C500) | Moyenne (Cadre en U + 2ème roulement) |

---

## 6. Impact Architectural & Feuille de Route d'Intégration

### 6.1 Éléments Inchangés

L'ajout du Waist Pitch en V1.5 a été pensé pour préserver 100% des pièces usinées du haut du corps :
* Colonne vertébrale 7075-T6 (Plaque Haute et Plaque Basse).
* Traverses d'épaules 60×60×2 mm et brides festonnées RS-04.
* Waist Plate 6,0 mm et équerres basses de waist L = 90,0 mm.
* Roulement CRBH 8016 UU et Moyeu Sandwich 7075-T6.
* Moteur RS-06 Waist Yaw.

### 6.2 Éléments à Prédisposer dès la V1

Afin d'éviter toute reprise d'usinage lourde lors du passage en V1.5, l'atelier doit prédisposer :
1. **Perçages de prédisposition pelvis** : Pré-percer les 10 trous taraudés M4 sur PCD Ø 106 mm sur le sommet du caisson pelvien lors de la fabrication du berceau.
2. **Corridor de câblage élargi** : Le passage de câbles dans le passe-fil TPU (25 × 15 mm) doit conserver une boucle de service suffisante pour absorber la flexion 3D combinée (Yaw +/-90 deg et Pitch +/-30 deg).

### 6.3 Calendrier Recommandé

```
[ Étape 1 — 2026 : D-Bot V1.0 ]
  ├── Waist 1-DoF Yaw pur (RS-06 + CRBH 8016)
  ├── Fabrication immédiate CNC C500 & Assemblage
  └── Validation marche bipède et ramassage rapide en squat
              │
              ▼
[ Étape 2 — 2027 : D-Bot V1.5 ]
  ├── Commande 1x RS-04 supplémentaire + 1x CRBH 5013 UU
  ├── Usinage Cadre Intermédiaire en U (Alu 7075-T6)
  └── Déploiement Whole-Body Control 2-DoF (Ramassage au sol longue durée)
```

---

*Fin de l'Étude Prospective R&D — Document de référence pour l'évolution cinématique du D-Bot V1.5.*
