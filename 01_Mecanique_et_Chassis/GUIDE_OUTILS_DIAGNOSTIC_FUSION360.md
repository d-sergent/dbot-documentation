# Guide Technique — Suite d'Outils de Diagnostic Cinématique & Assainissement Fusion 360 (D-Bot V1)

> **Document Officiel de Référence** : Manuel d'exploitation et de diagnostic des assemblages complexes sous Autodesk Fusion 360 pour le projet humanoïde D-Bot.  
> **Auteur** : Antigravity & Ingénierie D-Bot  
> **Dernière révision** : 20 septembre 2026  
> **Statut** : Validé et Opérationnel  

---

## 📑 Sommaire

* [1. Introduction & Contexte Technique](#1-introduction--contexte-technique)
  * [1.1 Les Enjeux de la Modélisation Paramétrique sous Fusion 360](#11-les-enjeux-de-la-modélisation-paramétrique-sous-fusion-360)
  * [1.2 Les Limitations Découvertes sur l'API Autodesk](#12-les-limitations-découvertes-sur-lapi-autodesk)
* [2. Présentation Générale de la Suite d'Outils](#2-présentation-générale-de-la-suite-doutils)
* [3. Fiche Technique — Outil 1 : ProbeSelectedComponent](#3-fiche-technique--outil-1--probeselectedcomponent)
  * [3.1 Rôle & Scénario d'Utilisation](#31-rôle--scénario-dutilisation)
  * [3.2 Mode d'Emploi Pas-à-Pas](#32-mode-demploi-pas-à-pas)
  * [3.3 Exemple de Résultat Obtenu](#33-exemple-de-résultat-obtenu)
* [4. Fiche Technique — Outil 2 : MeasureFaceGap](#4-fiche-technique--outil-2--measurefacegap)
  * [4.1 Rôle & Scénario d'Utilisation](#41-rôle--scénario-dutilisation)
  * [4.2 Mode d'Emploi Pas-à-Pas](#42-mode-demploi-pas-à-pas)
  * [4.3 Critères Métrologiques & Seuils d'Alerte](#43-critères-métrologiques--seuils-dalerte)
* [5. Fiche Technique — Outil 3 : TimelineKinematicInspector](#5-fiche-technique--outil-3--timelinekinematicinspector)
  * [5.1 Rôle & Contournement du Blocage Temporel](#51-rôle--contournement-du-blocage-temporel)
  * [5.2 Mode d'Emploi Pas-à-Pas](#52-mode-demploi-pas-à-pas)
  * [5.3 Structure du Rapport Généré](#53-structure-du-rapport-généré)
* [6. Fiche Technique — Outil 4 : CleanBrokenConstraints](#6-fiche-technique--outil-4--cleanbrokenconstraints)
  * [6.1 Rôle & Prévention des Crashs C++](#61-rôle--prévention-des-crashs-c)
  * [6.2 Mode d'Emploi Pas-à-Pas](#62-mode-demploi-pas-à-pas)
* [7. Protocole d'Atelier pour Résoudre un Conflit Cinématique](#7-protocole-datelier-pour-résoudre-un-conflit-cinématique)
* [8. Le Standard des Fichiers d'Audit JSON (AUDIT_METROLOGIQUE)](#8-le-standard-des-fichiers-daudit-json-audit_metrologique)
* [9. Répertoire & Emplacements des Scripts](#9-répertoire--emplacements-des-scripts)

---

## 1. Introduction & Contexte Technique

### 1.1 Les Enjeux de la Modélisation Paramétrique sous Fusion 360

La conception mécanique du robot humanoïde D-Bot fait intervenir des assemblages denses comprenant plusieurs dizaines de sous-ensembles (bassin, torse, actionneurs QDD RobStride, roulements à rouleaux croisés, colonnes et platines CNC).

Dans Autodesk Fusion 360, la chronologie paramétrique (*Timeline / Design History*) enregistre chaque étape dans le temps. Lorsqu'une pièce est insérée, déplacée ou contrainte, son état cinématique dépend directement :
1. De sa position d'insertion initiale.
2. Des **Groupes Rigides** (*Rigid Groups*) créés dans le composant parent.
3. Des **Liaisons natives** (*Joints* et *As-Built Joints*).
4. Des **Contraintes d'assemblage** (*Assembly Constraints*) et de leurs regroupements (*Constraint Sets*).

Lorsqu'une anomalie survient (par exemple un roulement qui flotte à 2,48 mm au-dessus de son lamage), l'identification de la cause racine est souvent masquée par la complexité de l'arbre et les imbrications de l'historique.

### 1.2 Les Limitations Découvertes sur l'API Autodesk

Les sessions d'ingénierie du Waist D-Bot ont mis en évidence trois écueils critiques de l'API Fusion 360 :
* **L'erreur `<Cannot be edited before rolling back>`** : Il est impossible d'interroger les entités géométriques (`entityOne`, `entityTwo`) d'une contrainte d'assemblage située dans le passé tant que le marqueur de timeline est positionné à la fin du document.
* **Le crash fatal (SIGSEGV) sur les contraintes corrompues** : Lorsqu'une contrainte présente un code d'erreur interne (`healthState = 4`, par exemple suite à la suppression d'une arête de référence), toute tentative de lecture aveugle de ses propriétés par l'API déréférence un pointeur nul dans le noyau C++ Autodesk, provoquant la fermeture brutale de Fusion 360.
* **L'invisibilité des contraintes enfants** : Les contraintes individuelles sont automatiquement regroupées par Fusion dans des dossiers parents nommés `Jeu de contraintes X`. Un scan superficiel s'arrête au nom du dossier sans révéler les pièces réellement liées.

---

## 2. Présentation Générale de la Suite d'Outils

Pour pallier définitivement ces limitations et doter l'équipe d'une boîte à outils d'inspection instantanée, 4 scripts spécialisés ont été développés :

| Script / Outil | Type d'Action | Cible Principale | Bénéfice Clé |
| :--- | :---: | :--- | :--- |
| **`ProbeSelectedComponent`** | Diagnostic ciblé | Pièce sélectionnée (1 clic) | Zéro scan global, réponse en 0,1 s, liste tous les verrous |
| **`MeasureFaceGap`** | Palpeur métrologique | 2 faces sélectionnées | Écart normal au micron près, détection de contact franc |
| **`TimelineKinematicInspector`** | Cartographie complète | Document entier | Voyage temporel transparent, déjoue l'erreur de rollback |
| **`CleanBrokenConstraints`** | Maintenance & santé | Contraintes en erreur | Élimine les contraintes corrompues, prévient 100 % des crashs |
| **`AuditTorse`** | Audit métrologique JSON | Sous-ensemble CAO complet | Génère le standard `AUDIT_METROLOGIQUE_<SousSection>.json` (masses, CoG, BBox, perçages) |
| **`extract_fusion_properties`** | Exportateur robotique | Modèle 3D complet | Extrait récursivement les inerties et repères de liaisons pour URDF / Isaac Sim |

---

## 3. Fiche Technique — Outil 1 : ProbeSelectedComponent

### 3.1 Rôle & Scénario d'Utilisation

**Quand l'utiliser ?**
Dès qu'un composant refuse de bouger, semble bloqué ou sur-contraint. Au lieu de fouiller dans des dizaines de dossiers de l'arbre de création, cet outil inspecte exclusivement la pièce sélectionnée.

### 3.2 Mode d'Emploi Pas-à-Pas

1. Dans la fenêtre graphique 3D ou dans le navigateur Fusion 360, **cliquez sur le composant** à inspecter (ex : `RB8016:2`).
2. Appuyez sur **`Shift + S`** (menu *Utilitaires* ➔ *Scripts et compléments*).
3. Sélectionnez **`ProbeSelectedComponent`** et cliquez sur **Exécuter** (*Run*).
4. *(Note : Si aucun composant n'était sélectionné à l'avance, le script vous invite automatiquement à cliquer sur la pièce).*

### 3.3 Exemple de Résultat Obtenu

Une boîte de dialogue s'affiche instantanément :

```text
=== RAPPORT D'INSPECTION : RB8016:2 ===
• Composant parent : Bassin_Pelvis [ASV1_200]
• Fixé au sol (isGrounded) : NON (Libre)
• BBox Z : [1018.900, 1034.940] mm (Hauteur = 16.040 mm)
• BBox X : [-10.780, 109.240] mm | Y : [-50.650, 69.370] mm

--- GROUPES RIGIDES CONTENANT CE COMPOSANT ---
  Aucun groupe rigide ne contient cette pièce.

--- LIAISONS (JOINTS) TOUCHANT CE COMPOSANT ---
  🔹 [Joint] 'Liaison_Rigide_RB8016_Traverse' [ACTIF] dans 'Bassin_Pelvis [ASV1_200]' ➔ Relié à : 'Traverse_Renfort_Bassin'
```

---

## 4. Fiche Technique — Outil 2 : MeasureFaceGap

### 4.1 Rôle & Scénario d'Utilisation

**Quand l'utiliser ?**
Pour valider métrologiquement qu'une pièce est parfaitement plaquée sur son siège (ex : fond de lamage, face d'appui d'équerre, contact entretoise). Il remplace l'inspection visuelle incertaine par une mesure géométrique rigoureuse au micron près.

### 4.2 Mode d'Emploi Pas-à-Pas

1. Appuyez sur **`Shift + S`** ➔ sélectionnez **`MeasureFaceGap`** ➔ **Exécuter**.
2. **Invite 1** : Cliquez sur la face de référence (ex : face plane du fond de lamage de la traverse).
3. **Invite 2** : Cliquez sur la face cible (ex : face plane inférieure du roulement).
4. Le script calcule les normales, les points d'origine et la projection vectorielle.

### 4.3 Critères Métrologiques & Seuils d'Alerte

* **Contact Franc Conforme (`Écart <= 0,02 mm`)** : Les deux plans sont en contact métal-métal rigoureux.
* **Jeu Parasite (`Écart > 0,02 mm`)** : Alerte explicite indiquant la valeur du jeu en millimètres et en microns (ex : `2,480 mm (2480 µm)`).
* **Parallélisme** : Calcule l'angle résiduel en degrés (tolérance nominale `< 0,1 deg`).
* **Coaxialité (pour cylindres)** : Calcule le désaxage radial entre deux alésages ou arbres cylindriques.

---

## 5. Fiche Technique — Outil 3 : TimelineKinematicInspector

### 5.1 Rôle & Contournement du Blocage Temporel

**Principe d'ingénierie :**
Pour contourner l'interdiction de l'API Autodesk (`Cannot be edited before rolling back`), cet outil effectue un **pilotage automatisé et transparent de la chronologie** :
1. Il enregistre la position finale de la timeline (`design.timeline.markerPosition`).
2. Pour chaque contrainte saine, il déplace le curseur de timeline juste sur la contrainte via `timelineObject.rollTo(True)`.
3. À cette position temporelle, l'API autorise la lecture complète et native de `entityOne` et `entityTwo`.
4. Il restaure impérativement la timeline à la fin via un bloc `finally: design.timeline.moveToEnd()`.

### 5.2 Mode d'Emploi Pas-à-Pas

1. Appuyez sur **`Shift + S`** ➔ sélectionnez **`TimelineKinematicInspector`** ➔ **Exécuter**.
2. L'écran effectue un balayage rapide de la chronologie pendant quelques secondes.
3. Le rapport exhaustif est sauvegardé dans :
   `Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/timeline_kinematic_map.txt`.

### 5.3 Structure du Rapport Généré

```text
================================================================================
CARTOGRAPHIE CINÉMATIQUE EXHAUSTIVE PAR VOYAGE TEMPOREL — D-BOT
Document : Torse v91
================================================================================

🔹 [1] 'Contrainte 169' (#1) dans 'Torse v91'
     Type : Aligner (BRepFace <---> BRepFace)
     Liaison : 'RB8016:2' <---> 'Waist_Plate_7075:1'

🔹 [2] 'Contrainte 171' (#1) dans 'Bassin_Pelvis [ASV1_200]'
     Type : Aligner (BRepFace <---> BRepFace)
     Liaison : 'Moyeu_Waist_Sandwich_7075:1' <---> 'RB8016:2'
```

---

## 6. Fiche Technique — Outil 4 : CleanBrokenConstraints

### 6.1 Rôle & Prévention des Crashs C++

**Pourquoi cet outil est indispensable :**
Lors des itérations de conception sous Fusion 360, la modification d'un chanfrein, d'un perçage ou d'un corps peut laisser des contraintes orphelines dont les géométries de référence ont disparu. Ces contraintes passent en statut d'erreur (`healthState = 4`). 

Leur présence dans le modèle :
1. Ralentit le solveur d'assemblage.
2. Crée des blocages cinématiques fantômes.
3. Provoque des plantages intempestifs de Fusion 360 lors de l'exécution de scripts d'analyse.

### 6.2 Mode d'Emploi Pas-à-Pas

1. Appuyez sur **`Shift + S`** ➔ sélectionnez **`CleanBrokenConstraints`** ➔ **Exécuter**.
2. Si le modèle est sain : un message confirme `Modèle 100% sain (zéro anomalie)`.
3. Si des contraintes corrompues sont détectées :
   * Une boîte de dialogue liste chaque élément défaillant avec son composant et son code d'erreur.
   * L'outil demande : *"Souhaitez-vous les SUPPRIMER DÉFINITIVEMENT pour assainir le modèle ?"*
   * Cliquez sur **Oui** pour purger le solveur en toute sécurité.

---

## 7. Protocole d'Atelier pour Résoudre un Conflit Cinématique

Pour diagnostiquer et résoudre tout problème d'assemblage futur sur le D-Bot, suivre scrupuleusement ce protocole en 4 phases :

```text
  [ PHASE 1 : SÉCURITÉ ] ➔ Lancer 'CleanBrokenConstraints' pour assainir le solveur.
            │
            ▼
  [ PHASE 2 : MESURE ]   ➔ Lancer 'MeasureFaceGap' pour quantifier le jeu réel en microns.
            │
            ▼
  [ PHASE 3 : CIBLAGE ]  ➔ Lancer 'ProbeSelectedComponent' sur la pièce bloquée.
            │
            ▼
  [ PHASE 4 : DÉCISION ] ➔ Si une contrainte parasite est identifiée :
                           - La supprimer ou la modifier.
                           - Recalculer l'empilement global (non-fragmentation système).
                           - Repasser 'MeasureFaceGap' pour valider le contact franc (0,00 mm).
```

---

## 8. Le Standard des Fichiers d'Audit JSON (AUDIT_METROLOGIQUE)

Pour garantir une traçabilité rigoureuse et standardisée entre les modèles 3D Fusion 360 et la documentation d'ingénierie, chaque sous-ensemble mécanique du robot dispose d'un fichier d'audit JSON normé en majuscules :

* **Format du nommage officiel** :  
  `AUDIT_METROLOGIQUE_<SousSection>.json`

### Cartographie par sous-ensemble :
1. **Torse & Bassin** :  
   [`01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_METROLOGIQUE_Torse_et_Bassin.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_METROLOGIQUE_Torse_et_Bassin.json)
2. **Bras & Mains** :  
   `01_Mecanique_et_Chassis/Bras_et_Mains/AUDIT_METROLOGIQUE_Bras_et_Mains.json`
3. **Jambes & Pieds** :  
   `01_Mecanique_et_Chassis/Jambes_et_Pieds/AUDIT_METROLOGIQUE_Jambes_et_Pieds.json`
4. **Tête & Cou** :  
   `01_Mecanique_et_Chassis/Tete_et_Cou/AUDIT_METROLOGIQUE_Tete_et_Cou.json`

### Données extraites par le standard :
* **Masses réelles & CoG** : Masse de chaque pièce en grammes, masse cumulée, centre de gravité global `[X, Y, Z]` en millimètres.
* **Volumes & Bounding Boxes** : Encombrement `[X, Y, Z]` min/max au millième de millimètre pour valider les assises et les interférences.
* **Perçages & Chambrages** : Recensement automatique des perçages lisses, taraudages M3/M4/M5, fraisures 90° FHC et chambrages CHC.
* **Quincaillerie & BOM** : Extraction automatique des références McMaster-Carr, moteurs RobStride et roulements industriels.

---

## 9. Répertoire & Emplacements des Scripts

La boîte à outils d'assemblage sous Fusion 360 est centralisée dans :

* **Répertoire racine des scripts** :  
  [`Documentation/Code/scripts/fusion360/`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/fusion360/)

### Outils Pérennes & Actifs (Catégorie A) :
1. **Palpeur métrologique 2 faces** :  
   [`MeasureFaceGap/MeasureFaceGap.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/fusion360/MeasureFaceGap/MeasureFaceGap.py)
2. **Diagnostic ciblé sur sélection** :  
   [`ProbeSelectedComponent/ProbeSelectedComponent.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/fusion360/ProbeSelectedComponent/ProbeSelectedComponent.py)
3. **Docteur de santé d'assemblage** :  
   [`CleanBrokenConstraints/CleanBrokenConstraints.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/fusion360/CleanBrokenConstraints/CleanBrokenConstraints.py)
4. **Inspecteur par voyage temporel** :  
   [`TimelineKinematicInspector/TimelineKinematicInspector.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/fusion360/TimelineKinematicInspector/TimelineKinematicInspector.py)
5. **Audit métrologique JSON global** :  
   [`AuditTorse/AuditTorse.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/fusion360/AuditTorse/AuditTorse.py)
6. **Exportateur URDF / Physique** :  
   [`extract_fusion_properties.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/fusion360/extract_fusion_properties.py)

### Archives d'Opérations CAO Spécifiques :
* **Script de conversion et renommage Asimov ➔ D-Bot** :  
  [`archives/ModifyTorse/ModifyTorse.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/fusion360/archives/ModifyTorse/ModifyTorse.py)
