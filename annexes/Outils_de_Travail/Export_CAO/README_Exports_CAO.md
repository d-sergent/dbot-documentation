# 🤖 D-Bot — Référentiel des Exports CAO Souverains (FreeCAD & STEP)

Ce répertoire constitue l'archive locale et souveraine de l'ensemble des modèles CAO 3D du robot humanoïde D-Bot.
Il permet de sauvegarder, synchroniser et exploiter tous les sous-ensembles du robot sous des formats ouverts, pérennes et indépendants du cloud Autodesk (B-Rep STEP ISO 10303-21 et fichiers natifs FreeCAD 1.1 `.FCStd`).

---

## 📑 Sommaire

1. [Architecture Modulaire des Dossiers](#architecture-modulaire-des-dossiers)
2. [Sous-Ensembles du Robot D-Bot](#sous-ensembles-du-robot-d-bot)
3. [Bibliothèque Partagée des Composants STEP](#bibliothèque-partagée-des-composants-step)
4. [Procédure d'Export et d'Audit Unifié](#procédure-dexport-et-daudit-unifié)
5. [Contrôle Qualité et Métrologie](#contrôle-qualité-et-métrologie)
6. [Politique Git, LightRAG et Stockage Souverain](#politique-git-lightrag-et-stockage-souverain)

---

## Architecture Modulaire des Dossiers

```text
Exports_CAO_DBot/
├── 00_Robot_Complet/                        <- Assemblage maître regroupant tous les membres
├── 01_Torse_et_Bassin/                      <- Torse [ASV1_100] et Bassin Pelvis [ASV1_200]
│   ├── DBot_Torse_et_Bassin_Souverain.FCStd    (Jumeau FreeCAD reconstruit — Torse-123 v42)
│   ├── Audits/                                 (AUDIT_METROLOGIQUE, CINEMATIQUE, ALIGNEMENT JSON + SYNTHESE .md)
│   ├── Plans_2D/                               (Plans cotés 2D générés depuis les modèles STEP/FCStd)
│   └── Visual_Snapshots/                       (Vues_Ensemble/ et Pieces_Isolees/ PNG haute définition)
├── 02_Tete_et_Cou/                          <- Tête robotique, capteurs OAK-D / Realsense, cou EL-05
├── 03_Bras_et_Epaules/                      <- Épaules 3 DDL, bras, coudes RS-03 / RS-04
├── 04_Mains_DHand/                          <- Mains articulées sous-actionnées D-Hand (5 doigts)
├── 05_Jambes_et_Hanches/                    <- Hanches pitch/roll/yaw, genoux 4-bar, chevilles, pieds
└── Bibliotheque_Composants_STEP/            <- Référentiel dédupliqué (212 composants B-Rep uniques + dbot_cad_manifest.json)
```

---

## Sous-Ensembles du Robot D-Bot

| Sous-Ensemble | Code Projet | Statut CAO | Fichiers Principaux |
| :--- | :--- | :--- | :--- |
| **Torse & Bassin** | `ASV1_100` / `ASV1_200` | **Validé & Reconstruit (`Torse-123 v42`)** | `DBot_Torse_et_Bassin_Souverain.FCStd` (`614` instances / `125` réf. / `18,32 kg`), `Audits/`, `Plans_2D/`, `Visual_Snapshots/` |
| **Tête & Cou** | `ASV1_300` | À exporter | Caméras RVB-D, actionneurs rotatifs RobStride `RS-05` (`EL05`, `Tilt` ici / `Pan` dans `Torse-123`), rotule |
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

### Nettoyage Automatique & Zéro Fichier Orphelin
Pour éviter l'accumulation de solides obsolètes lorsque des pièces changent de nom (ex. `Corniere` renommée en `Corniere_haute`), que la quincaillerie est standardisée ou que des composants sont supprimés de la CAO :
1. **Purge Automatique à l'Export (`ExportSovereignCAD.py`)** :
   - À chaque exécution dans Fusion 360, le script compare les fichiers `.step` présents sur disque avec la liste des composants actifs de l'assemblage.
   - Tous les fichiers orphelins sont automatiquement supprimés et consignés dans `manifest["metadata"]["purged_orphans"]`.
2. **Outil CLI de Maintenance Dédié (`clean_sovereign_library.py`)** :
   - Le script [`clean_sovereign_library.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/cad_tools/clean_sovereign_library.py) permet de lancer un diagnostic ou une purge depuis le terminal :
     - Diagnostic sans suppression : `/opt/homebrew/bin/python3.11 "Code/scripts/cad_tools/clean_sovereign_library.py" --dry-run`
     - Purge effective : `/opt/homebrew/bin/python3.11 "Code/scripts/cad_tools/clean_sovereign_library.py" --purge`

---

## Procédure d'Export et d'Audit Unifié

Lorsqu'un sous-ensemble (Torse, Bassin, Bras ou Tête) est validé dans Fusion 360, le workflow officiel enchaîne deux scripts complémentaires (`Shift + S`) :

1. **Audit Unifié 4-en-1 (`AuditTorse`)** :
   - Lancer [`AuditTorse/AuditTorse.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/fusion360/AuditTorse/AuditTorse.py).
   - Génère en une seule passe `Audits/AUDIT_METROLOGIQUE_<SousSection>.json`, `Audits/AUDIT_CINEMATIQUE_<SousSection>.json`, `Audits/AUDIT_ALIGNEMENT_<SousSection>.json`, la synthèse [`SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md) et les captures PNG dans `Visual_Snapshots/`.
2. **Export Souverain B-Rep (`ExportSovereignCAD`)** :
   - Lancer [`ExportSovereignCAD/ExportSovereignCAD.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/fusion360/ExportSovereignCAD/ExportSovereignCAD.py).
   - Exporte les composants B-Rep uniques dans `Bibliotheque_Composants_STEP/`, purge automatiquement les anciens `.step` orphelins et écrit `dbot_cad_manifest.json`.
3. **Reconstruction et Cotation dans FreeCAD** :
   - L'importateur reconstitue l'assemblage avec ses matrices 4x4, ses matériaux (`Aluminium 7075-T6`, `PA12-CF`, `Acier Inox / 12.9`) et sauvegarde le fichier maître `.FCStd` + `Plans_2D/`.
   - Consulter le guide complet : [`GUIDE_OUTILS_DIAGNOSTIC_FUSION360.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/Export_CAO/GUIDE_OUTILS_DIAGNOSTIC_FUSION360.md) et [`GUIDE_Sauvegarde_Souveraine_Fusion360_vers_FreeCAD.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/Export_CAO/GUIDE_Sauvegarde_Souveraine_Fusion360_vers_FreeCAD.md).

---

## Contrôle Qualité et Métrologie

Chaque export fait l'objet d'un contrôle rigoureux :
- Zéro approximation géométrique : conservation intégrale des congés d'usinage, chanfreins et fraisures coniques.
- Vérification des boîtes englobantes globales (Largeur, Profondeur, Hauteur), de la verticalité des montants et de l'axialité des tubes transverses Épaules / Hanches.
- Validation de l'arbre FreeCAD sous forme de conteneurs modulaires `App::Part`.

---

## Politique Git, LightRAG et Stockage Souverain

- **Dumps d'audit JSON (`Audits/AUDIT_*.json`)** : isolés dans `01_Mecanique_et_Chassis/<SousEnsemble>/Audits/` et **exclus de Git** via [`.gitignore`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/.gitignore) ainsi que de **LightRAG** (`index_docs.py` n'indexe que `.md`, `.txt`, `.pdf`), tout en étant répliqués dans `Exports_CAO_DBot/<SousEnsemble>/Audits/`.
- **Synthèse Métrologique (`SYNTHESE_METROLOGIQUE_<SousSection>.md`)** : **suivie dans Git et indexée dans LightRAG** pour servir de référence numérique fiable à toute l'ingénierie et aux requêtes RAG.
