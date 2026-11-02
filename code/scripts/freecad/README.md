# 🛠️ Boîte à Outils FreeCAD Souveraine — Projet Humanoïde D-Bot

> [!NOTE]
> Ce dossier regroupe l'ensemble des scripts Python, pipelines de calcul par éléments finis (FEA / CalculiX), outils de mise en plan 2D souveraine et macros interactives GUI développés sur-mesure pour **Autodesk FreeCAD 1.1+** dans le cadre du projet robotique humanoïde D-Bot.

---

## 📑 Sommaire

1. [Vue d'Ensemble des Macros Graphiques GUI (.FCMacro)](#1-vue-densemble-des-macros-graphiques-gui-fcmacro)
2. [Description Détaillée des Macros](#2-description-détaillée-des-macros)
   - [Animer_Deformation_FEA.FCMacro](#a-animer_deformation_feafcmacro--animation--von-mises)
   - [ToggleComponentColors.FCMacro](#b-togglecomponentcolorsfcmacro--shift--n-fusion-360)
3. [Procédure d'Installation et de Synchronisation](#3-procédure-dinstallation-et-de-synchronisation)
4. [Pipelines de Calcul par Éléments Finis CLI (CalculiX / Gmsh)](#4-pipelines-de-calcul-par-éléments-finis-cli-calculix--gmsh)
5. [Outils de Dessin Technique et Mise en Plan 2D](#5-outils-de-dessin-technique-et-mise-en-plan-2d)

---

## 1. Vue d'Ensemble des Macros Graphiques GUI (.FCMacro)

Les macros FreeCAD permettent d'ajouter des fonctionnalités interactives en 1 clic dans l'interface graphique de FreeCAD pour les revues de conception et le dépouillement RDM :

| Fichier Macro | Emplacement Dépôt | Fonction Principale | Déclencheur UI |
| :--- | :--- | :--- | :--- |
| **`Animer_Deformation_FEA.FCMacro`** | [`Code/scripts/freecad/Animer_Deformation_FEA.FCMacro`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/freecad/Animer_Deformation_FEA.FCMacro) | Active instantanément le panneau officiel de résultats CalculiX avec dégradé Von Mises, curseur d'échelle et bouton d'animation oscillatoire dynamique `Start Animation`. | `Macro > Macros... > Exécuter` |
| **`ToggleComponentColors.FCMacro`** | [`Code/scripts/freecad/ToggleComponentColors.FCMacro`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/freecad/ToggleComponentColors.FCMacro) | Émule le raccourci `Shift + N` d'Autodesk Fusion 360 : bascule d'un clic entre couleurs distinctes pastel (nombre d'or) et finitions réelles (Alu 7075, PA12-CF, RobStride, Inox). | `Macro > Macros... > Exécuter` |

---

## 2. Description Détaillée des Macros

### A. `Animer_Deformation_FEA.FCMacro` — Animation & Von Mises

* **Problème résolu** : Lorsque les simulations FEA sont résolues en ligne de commande headless (`freecadcmd`), FreeCAD génère parfaitement les résultats numériques CalculiX mais n'instancie pas le contrôleur d'interface graphique (`VPResultMechanical`). Le double-clic sur `CCX_Results` ne répond donc pas à l'ouverture du fichier dans le GUI.
* **Actions exécutées par la macro** :
  1. Ferme proprement tout panneau de tâche modal en cours (évite le verrouillage d'édition).
  2. Masque automatiquement le solide opaque CAO brut et les pipelines VTK pour dégager le maillage coloré.
  3. Attache le contrôleur officiel `view_result_mechanical.VPResultMechanical` au résultat.
  4. Préconfigure l'affichage sur le critère de Von Mises (`Sabs`).
  5. Ouvre le panneau officiel des tâches FreeCAD avec le curseur **Facteur d'échelle de déformation** et le bloc **Contrôle de l'animation** (`Start Animation`).
* **Utilisation type** : Visualiser la flexion réelle sous effort de la colonne vertébrale, des cornières de torse, des chapes de hanche ou des biellettes de cheville.

### B. `ToggleComponentColors.FCMacro` — "Shift + N" Fusion 360

* **Problème résolu** : Dans les assemblages complexes (Torse, Bassin, Jambes), toutes les pièces en aluminium 7075 partagent la même teinte grise naturelle, rendant difficile la distinction visuelle des liaisons et des interfaces mécaniques.
* **Actions exécutées par la macro** :
  * **Mode 1 (Couleurs d'occurrences)** : Génère une teinte pastel harmonieuse et contrastée pour chaque pièce via la suite du nombre d'or (`phi = 0.618033...`), avec une saturation douce (0.65) et une luminosité optimale (0.88).
  * **Mode 2 (Matériaux réels)** : Rétablit fidèlement les teintes photoréalistes du robot :
    * Aluminium 7075-T6 anodisé / usiné : `(0.78, 0.79, 0.82)`
    * Polymère composite PA12-CF noir mat : `(0.18, 0.18, 0.20)`
    * Moteurs QDD RobStride (RS-00 à RS-06) carter sombre : `(0.12, 0.13, 0.15)`
    * Bagues de roulements acier chromé 100Cr6 : `(0.85, 0.88, 0.92)`
    * Visserie inox A2-70 / classe 12.9 : `(0.40, 0.42, 0.45)`

---

## 3. Procédure d'Installation et de Synchronisation

Sous macOS, FreeCAD 1.1 stocke les macros utilisateur dans le dossier système versionné :
```text
/Users/davidsergent/Library/Application Support/FreeCAD/v1-1/Macro/
```

### Commande de synchronisation automatique (Dépôt Git -> FreeCAD) :
Pour déployer ou mettre à jour toutes les macros du dépôt directement dans FreeCAD, exécuter la commande suivante :
```bash
cp /Users/Shared/Mon\ Google\ Drive\ Physique/Documentation/Code/scripts/freecad/*.FCMacro "$HOME/Library/Application Support/FreeCAD/v1-1/Macro/"
```

---

## 4. Pipelines de Calcul par Éléments Finis CLI (CalculiX / Gmsh)

Ces scripts exécutent des analyses RDM complètes de manière autonome en arrière-plan sans nécessiter d'interaction graphique :

* [`simulate_colonne_basse.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/freecad/simulate_colonne_basse.py) :
  * Modèle : Colonne vertébrale basse en alliage d'aluminium 7075-T651 (`E = 71 700 MPa`, `nu = 0,33`, `Re = 505 MPa`).
  * Cas de charges : Roulis transversal (Roll 50 N.m / 178 N) et Tangage frontal (Pitch 140 N.m / 500 N).
  * Solveur : CalculiX `ccx` avec maillage tétraédrique volumique quadratique C3D10 (53 900 nœuds).
  * Sorties : Fichiers `.FCStd` natifs et lanceurs exécutables 1-clic `.command`.
* [`simulate_corniere_torsion.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/freecad/simulate_corniere_torsion.py) :
  * Modèle : Cornière Haute Nervurée 7075-T6.
  * Cas de charges : Lacet transversal (210 N), Traction axiale (210 N), Flexion frontale (210 N).
  * Analyse statistique : Extraction de la contrainte au 95e percentile (P95) pour éliminer les singularités géométriques de maillage.

---

## 5. Outils de Dessin Technique et Mise en Plan 2D

* [`generate_sovereign_2d_drawings.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/freecad/generate_sovereign_2d_drawings.py) : Génération autonome de plans d'atelier 2D conformes aux normes ISO/DIN pour usinage CNC 3 axes et 5 axes.
* [`generate_expert_technical_drawing.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/freecad/generate_expert_technical_drawing.py) : Moteur de cotation géométrique, ajustements tolérancés (H7/g6, H7/m6, H7/p6) et cartouches normalisés.
* [`update_svg_plan.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/freecad/update_svg_plan.py) : Injection des cotes et vues vectorielles SVG dans la documentation technique active.

