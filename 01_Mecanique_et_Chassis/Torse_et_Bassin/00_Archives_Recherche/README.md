# 📦 Archives de Recherche — Torse D-Bot

*Ce dossier contient les études exploratoires, audits et guides de fabrication devenus obsolètes suite à l'adoption de l'**architecture cruciforme** (Août 2026).*

> [!WARNING]
> **Ces documents sont archivés à titre historique.** Ils ne reflètent pas l'état actuel de la conception du torse D-Bot. Pour les spécifications actuelles, consulter les documents à la racine du dossier `Torse/`.

---

## Documents Archivés

| Document | Objet | Raison d'archivage |
|:---|:---|:---|
| **STUDY_Squelette_Torse.md** | Étude de la cage tubulaire alu boulonnée (V1) — 12 profilés, 8 nœuds CNC, 48 vis M6, 2.36 kg | Architecture **déclarée obsolète** — trop lourde (784 g de connexions), usinage 5 axes requis pour les nœuds |
| **FINAL_CONSOLIDE_Torse.md** | Spécifications consolidées de l'approche monocoque hybride Asimov (2 lattes alu latérales) | **Remplacé** par l'architecture cruciforme (plaque isogrid sagittale + traverse carbone) |
| **AUDIT_ETUDE_Torse.md** | Audit d'ingénierie du STUDY_Squelette + FINAL_CONSOLIDE | Audite des documents **eux-mêmes obsolètes** — les vérifications de calcul restent correctes mais portent sur une architecture abandonnée |
| **GUIDE_Fabrication_Torse_Asimov_Hybride.md** | Ancien guide de fabrication (architecture monocoque Asimov v1 scalée +18%) | **Explicitement remplacé** par `GUIDE_Fabrication_Torse_D-Bot_Hybride.md` (mention en en-tête du nouveau guide) |
| **ETUDE_DETAILLEE_Asimov_V1.md** | Étude détaillée du robot Asimov V1 (base de référence pour le scale +18%) | Document de **veille technologique** — les données utiles sont intégrées dans le guide de fabrication actif |
| **GUIDE_Modelisation_et_Securisation_Torse.md** | Guide de modélisation Fusion 360 pour les Options A (Spine Carbone) et C (Split-Monocoque) | Options A et C **non retenues** — remplacées par l'architecture cruciforme |
| **RECHERCHE_CAD_Robots_OpenSource.md** | Recherche de modèles CAD open-source (Berkeley Humanoid Lite, Axon, pib) | Document de **veille technologique** — les recommandations sont intégrées dans l'ANALYSE_STRATEGIE |

---

## Documents Actifs (Racine du Dossier Torse/)

| Document | Rôle |
|:---|:---|
| **ANALYSE_STRATEGIE_Torse.md** | Justification stratégique du choix de l'architecture cruciforme |
| **ETUDE_Dimensionnement_Colonne_Vertebrale.md** | Étude de dimensionnement mécanique de la colonne vertébrale (Option B — lumières 2D traversantes) |
| **GUIDE_Fabrication_Torse_D-Bot_Hybride.md** | Guide de fabrication complet du torse cruciforme (plaques, brides, carters, impression, assemblage) |
