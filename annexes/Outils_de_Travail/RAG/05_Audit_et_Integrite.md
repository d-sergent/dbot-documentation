# 05 — Audit & Intégrité (Système RAG & Parité CAO)

Ce document décrit les deux outils complémentaires d'assurance qualité du projet D-Bot :
1. **L'audit contradictoire Graph-RAG (`check_integrity.py`)** avec filtrage bi-temporel `Niveau 1 > Niveau 2`.
2. **Le contrôleur déterministe temps réel (`rag_quality_audit.py` & `rag_monitor_ui.py`)** incluant le contrôle `CAO JSON <-> Markdown / BOM / SVG`.

---

## 📑 Sommaire

- [1. Présentation](#1-présentation)
- [2. Audit Contradictoire Graph-RAG et Filtrage Bi-Temporel](#2-audit-contradictoire-graph-rag-et-filtrage-bi-temporel)
- [3. Contrôle Qualité Temps Réel et Parité CAO BOM SVG](#3-contrôle-qualité-temps-réel-et-parité-cao-bom-svg)
- [4. Utilisation et Cockpit Web](#4-utilisation-et-cockpit-web)
- [5. Processus de Correction](#5-processus-de-correction)
- [6. Maintenance des Outils](#6-maintenance-des-outils)

---

## 1. Présentation

L'outil **RAG Audit** assure la cohérence technique de la documentation et du graphe de connaissances **LightRAG** du robot D-Bot :
- **`check_integrity.py`** utilise le **Mode Global** du Graph-RAG pour comparer les informations dispersées dans le corpus et détecter les contradictions techniques (masses, moteurs RobStride, bus CAN, capteurs) tout en respectant la hiérarchie documentaire officielle.
- **`rag_quality_audit.py` & `rag_monitor_ui.py`** vérifient en **100 % lecture seule et sans LLM** (`< 5 s` pour le corpus complet, `< 0,2 s` pour le contrôle CAO) la santé de la base LightRAG, la rétention des cotes/références et l'alignement réel entre Fusion 360 (`AUDIT_METROLOGIQUE_Torse_et_Bassin.json`), les dossiers techniques, la nomenclature McMaster-Carr et les schémas vectoriels `.svg`.

---

## 2. Audit Contradictoire Graph-RAG et Filtrage Bi-Temporel

Contrairement à une recherche classique, `check_integrity.py` interroge le graphe en **Mode Global** et injecte automatiquement la hiérarchie bi-temporelle calculée par `compute_bitemporal_doc_hierarchy()` (`Code/rag/rag_quality_audit.py`) via `build_bitemporal_audit_query()` :

1. **Cas 1 (`t_invalid` — Études antérieures ignorées)** : toute divergence provenant d'un document **Niveau 2 (`STUDY_` ou `AUDIT_`)** plus ancien que le document **Niveau 1 (`FINAL_`, `DOSSIER_TECHNIQUE_`, `GUIDE_COMPLET_`, `SYNTHESE_METROLOGIQUE_`)** du même dossier est ignorée automatiquement. Cela élimine les faux positifs sur les anciennes hypothèses déjà tranchées.
2. **Cas 2 (`Niveau 1 vs Niveau 1` — Priorité critique)** : toute contradiction entre deux documents officiels de Niveau 1 est signalée en priorité absolue avec une `**Question :**` dédiée.
3. **Cas 3 (`Consolidation en attente`)** : tout fichier `STUDY_` plus récent sur disque que le document Niveau 1 de son dossier est listé explicitement dans la requête d'audit afin de vérifier si ses nouveaux résultats (FEA CalculiX, bilans de masse, architecture) doivent être reportés dans le dossier final.

L'en-tête du rapport généré (`AUDIT_INTEGRITE.md`) inclut systématiquement le compteur `Filtre Bi-Temporel (Niveau 1 > Niveau 2)` indiquant le nombre de documents Niveau 1, d'études antérieures ignorées (`t_invalid`) et d'études récentes à consolider.

---

## 3. Contrôle Qualité Temps Réel et Parité CAO BOM SVG

Implémenté dans `audit_cad_doc_drift()` (`Code/rag/rag_quality_audit.py`) en mode **100 % déterministe et lecture seule (`0` LLM, `0 Go` VRAM)**, ce contrôleur complète l'audit LightRAG sur trois axes :

1. **Parité Métrologique & Versions (`AUDIT_METROLOGIQUE_Torse_et_Bassin.json <-> Dossiers Markdown`)** :
   - Vérifie les versions `Torse-123 vNN` citées (`CAD_VERSION_DRIFT`).
   - Vérifie la masse totale d'assemblage et les masses unitaires des pièces structurelles clés (`Plastron_Ventral_Torse`, `RB8016`, `Traverse_Renfort_Bassin`, `colonne vertébrale`, `Chassis_Structurel_Bassin_Last`, `Waist_Plate_7075`, `Selle de Pont Pelvis`, `Bride Epaule`, `Moyeu_Waist_Sandwich_7075`) (`PART_MASS_DRIFT`).
2. **Parité Quincaillerie McMaster-Carr (`CAO <-> FINAL_BOM`)** :
   - Compare les références McMaster-Carr extraites de `hardware_bom` / `components` dans le JSON CAO avec [FINAL_BOM_Torse_et_Waist_D-Bot.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md) et [FINAL_Liste_Achats_BOM.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/05_Gestion_Projet/FINAL_Liste_Achats_BOM.md) (`CAD_BOM_MISSING_REF`).
3. **Fraîcheur des Schémas Vectoriels & Snapshots (`mtime CAO vs SVG`)** :
   - Compare la date de modification des fichiers `.svg` dans `01_Mecanique_et_Chassis/Torse_et_Bassin/media/` à celle du dernier JSON métrologique Fusion 360.
   - Contrôle la parité SHA-256 des captures PNG déclarées dans `Code/scripts/cad_tools/snapshot_sync_manifest.json` vis-à-vis de `Exports_CAO_DBot` (`STALE_VISUAL_SNAPSHOT`).

---

## 4. Utilisation et Cockpit Web

### Lancement de l'Audit Contradictoire (`check_integrity.py`)
Par défaut (`--provider auto` et MCP `llm_mode="auto"`), l'audit suit la cascade rapide à 3 paliers : **Gemini Free Tier `-lite`** (`gemini-3.1-flash-lite` -> `gemini-3.5-flash-lite` -> `gemini-flash-lite-latest`) -> **`1min.ai` (`mistral-small-2603`)** -> **Ollama `gemma4:26b`** (sinon `qwen3.8:27b-mlx` / Unsloth `unsloth/Qwen3.8-27B-GGUF`), tout en inscrivant le modèle réel utilisé dans l'en-tête du rapport :

```bash
# Audit automatique rapide (Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/check_integrity.py"

# Audit 100 % local via Ollama (gemma4:26b par defaut, ou --model qwen3.8:27b-mlx)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/check_integrity.py" --provider ollama
```

### Lancement du Contrôle Qualité Temps Réel et du Cockpit Web
```bash
# Audit qualite CLI temps reel (0 LLM : sante LightRAG + derive CAO / BOM / SVG)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/rag_quality_audit.py" --top 10

# Cockpit Web FastAPI (http://127.0.0.1:8765 — onglet "Parite CAO / BOM / SVG" et endpoint /api/cad-drift)
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/rag_monitor_ui.py" --port 8765
```

Dans le Cockpit Web (`http://127.0.0.1:8765`), l'onglet **Parite CAO / BOM / SVG** regroupe 4 panneaux :
1. **Contrôle Métrologique & Versions** (`JSON CAO <-> Dossiers Markdown`).
2. **Parité Quincaillerie McMaster-Carr** (`CAO <-> FINAL_BOM`).
3. **Fraîcheur des Schémas SVG & Snapshots** (`mtime CAO vs SVG`).
4. **Hiérarchie Bi-Temporelle Niveau 1 > Niveau 2** (liste des études `STUDY_` plus récentes que leur document Niveau 1 cible).

### Emplacement du Rapport
Le rapport contradictoire Graph-RAG est généré et écrasé à chaque passage dans :
`Annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md` (avec `> **Moteur réel utilisé** : ...` et `> **Filtre Bi-Temporel** : ...`).

---

## 5. Processus de Correction

Chaque section du rapport d'audit `check_integrity.py` se termine par une série de **Questions de Validation**.

**Procédure recommandée :**
1. **Lecture** : Parcourez `AUDIT_INTEGRITE.md` ou l'onglet **Parite CAO / BOM / SVG** dans le Cockpit Web.
2. **Arbitrage** : Pour chaque incohérence, décidez quelle source fait foi (le JSON CAO souverain `Torse-123` pour la géométrie/BOM, ou le document Niveau 1 validé).
3. **Correction Assistée** : Utilisez `resolve_audit.py` ou demandez directement dans le chat Antigravity d'aligner les fichiers identifiés ; aucune réécriture autonome n'est jamais appliquée la nuit sans votre validation.

---

## 6. Maintenance des Outils

- Les thématiques d'audit Graph-RAG sont définies dans le dictionnaire `AUDITS` de `Code/rag/check_integrity.py` (qui supporte `auto`, `gemini`, `1minai`, `ollama`, `unsloth`/`local` et `openrouter`).
- Les pièces structurelles étalons et les documents cibles du contrôle CAO déterministe sont configurés dans `_CAD_KEY_PARTS` et `CAD_TARGET_DOCS_RELS` au début de `Code/rag/rag_quality_audit.py`.

---
*Dernière mise à jour : 22 Novembre 2026*
