# 🤖 D-Bot — Référentiel des Exports CAO Souverains (FreeCAD & STEP)

Ce répertoire constitue l'archive locale et souveraine de l'ensemble des modèles CAO 3D du robot humanoïde D-Bot.
Il permet de sauvegarder, synchroniser et exploiter tous les sous-ensembles du robot sous des formats ouverts, pérennes et indépendants du cloud Autodesk (B-Rep STEP ISO 10303-21 et fichiers natifs FreeCAD 1.1 `.FCStd`).

---

## 📑 Sommaire

1. [Architecture Modulaire des Dossiers](#architecture-modulaire-des-dossiers)
2. [Sous-Ensembles du Robot D-Bot](#sous-ensembles-du-robot-d-bot)
3. [Bibliothèque Partagée des Composants STEP](#bibliothèque-partagée-des-composants-step)
4. [Procédure d'Export pour un Nouveau Membre](#procédure-dexport-pour-un-nouveau-membre)
5. [Contrôle Qualité et Métrologie](#contrôle-qualité-et-métrologie)

---

## Architecture Modulaire des Dossiers

```text
Exports_CAO_DBot/
├── 00_Robot_Complet/                  <- Assemblage maître regroupant tous les membres
├── 01_Torse_et_Bassin/                <- Torse [ASV1_100] et Bassin Pelvis [ASV1_200]
│   ├── DBot_Torse_et_Bassin_Souverain.FCStd  (Modèle FreeCAD colorisé 113 Mo)
│   └── manifest_torse_v98.json               (356 occurrences géométriques)
├── 02_Tete_et_Cou/                    <- Tête robotique, capteurs OAK-D / Realsense, cou EL-05
├── 03_Bras_et_Epaules/                <- Épaules 3 DDL, bras, coudes RS-03 / RS-04
├── 04_Mains_DHand/                    <- Mains articulées sous-actionnées D-Hand (5 doigts)
├── 05_Jambes_et_Hanches/              <- Hanches pitch/roll/yaw, genoux 4-bar, chevilles, pieds
└── Bibliotheque_Composants_STEP/      <- Référentiel dédupliqué de tous les composants B-Rep
```

---

## Sous-Ensembles du Robot D-Bot

| Sous-Ensemble | Code Projet | Statut CAO | Fichiers Principaux |
| :--- | :--- | :--- | :--- |
| **Torse & Bassin** | `ASV1_100` / `ASV1_200` | **Validé & Reconstruit** | `DBot_Torse_et_Bassin_Souverain.FCStd` (172 pièces) |
| **Tête & Cou** | `ASV1_300` | À exporter | Caméras RVB-D, actionneur linéaire EL-05, rotule |
| **Bras & Épaules** | `ASV1_400` | À exporter | Épaules pitch/roll/yaw (RS-04), coudes (RS-03) |
| **Mains D-Hand** | `ASV1_500` | À exporter | Doigts articulés, servomoteurs déportés, tendons |
| **Jambes & Hanches** | `ASV1_600` | À exporter | Hanches QDD (RS-06), genoux démultipliés, chevilles |
| **Robot Complet** | `D-Bot V2` | En cours d'agrégation | `DBot_Robot_Complet.FCStd` |

---

## Bibliothèque Partagée des Composants STEP

Le dossier `Bibliotheque_Composants_STEP/` centralise tous les solides B-Rep uniques.
Grâce à la déduplication :
- Chaque vis normalisée McMaster-Carr (`91812A252`, `92855A422`, `92290A168`) n'est stockée qu'une seule fois, même si elle est instanciée des dizaines de fois dans le robot.
- Les actionneurs RobStride (`RS06_v1.step`, `RS04_droit.step`, `EL05_v1.step`) et les roulements (`RB8016.step`) sont réutilisés d'un membre à l'autre sans duplication de géométrie.

---

## Procédure d'Export pour un Nouveau Membre

Lorsqu'un nouveau sous-ensemble (ex. Bras ou Tête) est prêt dans Fusion 360 :

1. **Dans Fusion 360** :
   - Ouvrir la conception active.
   - Lancer le script souverain : **Utilitaires > Scripts et compléments > Mes scripts > ExportSovereignCAD**.
   - Le script extrait les composants uniques dans `Bibliotheque_Composants_STEP/` et génère le manifeste d'assemblage JSON.

2. **Reconstruction dans FreeCAD** :
   - L'agent Antigravity assemble les pièces avec leurs matrices de placement 3D exactes.
   - Les propriétés de matériaux (`Aluminium 7075-T6`, `PA12-CF`, `Acier Inox`) et les couleurs réelles sont injectées.
   - Le fichier maître `.FCStd` est sauvegardé dans le dossier du sous-ensemble correspondant.

---

## Contrôle Qualité et Métrologie

Chaque export fait l'objet d'un contrôle rigoureux :
- Zéro approximation géométrique : conservation intégrale des congés d'usinage, chanfreins et fraisures coniques.
- Vérification des boîtes englobantes globales (Largeur, Profondeur, Hauteur) pour valider l'absence de pièces dérivantes ou déportées.
- Validation de l'arbre FreeCAD sous forme de conteneurs modulaires `App::Part`.
