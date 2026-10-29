#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
clean_visual_snapshots.py — Nettoyeur de Captures Visuelles CAO Orphelines (D-Bot)
=============================================================================
Ce script inspecte le répertoire souverain des captures d'écran CAO haute définition :
/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/

Il analyse :
1. Le dossier 'Pieces_Isolees/' : compare chaque dossier de pièce avec les
   composants actifs de la maquette numérique (via dbot_cad_manifest.json et
   AUDIT_METROLOGIQUE_Torse_et_Bassin.json).
2. Le dossier 'Vues_Ensemble/' : détecte les anciens doublons de numérotation
   antérieurs à l'introduction de la vue de dessous (04_vue_dessous.png).

Il détecte et purge :
- Les pièces renommées ou scindées (ex: 'Corniere' scindée en 'Corniere_haute' et 'Corniere_basse')
- Les composants obsolètes supprimés (ex: 'Panier_Batterie_Coulissant', 'Capot_Verrouillage_Batterie')
- Les anciens fichiers d'ensemble mal indexés (ex: 04_vue_profil_droit.png supplanté par 05_vue_profil_droit.png)

Usage :
  python3 clean_visual_snapshots.py            # Diagnostic et simulation (dry-run)
  python3 clean_visual_snapshots.py --dry-run  # Simulation explicite
  python3 clean_visual_snapshots.py --purge    # Purge réelle des dossiers et fichiers orphelins
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime

SNAPSHOTS_DIR = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots"
PIECES_DIR = os.path.join(SNAPSHOTS_DIR, "Pieces_Isolees")
ENSEMBLE_DIR = os.path.join(SNAPSHOTS_DIR, "Vues_Ensemble")

MANIFEST_PATH = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/Bibliotheque_Composants_STEP/dbot_cad_manifest.json"
AUDIT_PATH = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Audits/AUDIT_METROLOGIQUE_Torse_et_Bassin.json"

OFFICIAL_ENSEMBLE_VIEWS = {
    "01_vue_face.png",
    "02_vue_arriere.png",
    "03_vue_dessus.png",
    "04_vue_dessous.png",
    "05_vue_profil_droit.png",
    "06_vue_profil_gauche.png",
    "07_vue_isometrique.png"
}


def load_active_components():
    """Charge l'ensemble des noms de composants actifs depuis les sources de vérité CAO."""
    active_names = set()

    # 1. Manifeste STEP
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for comp_info in data.get("components", {}).values():
                    c_name = comp_info.get("component_name")
                    s_name = comp_info.get("safe_name")
                    if c_name:
                        active_names.add(c_name.strip())
                    if s_name:
                        active_names.add(s_name.strip())
        except Exception as e:
            print(f"⚠️ Avertissement lecture manifeste STEP : {e}")

    # 2. Audit Métrologique JSON (pour détecter les pièces ayant des corps bRep réels)
    if os.path.exists(AUDIT_PATH):
        try:
            with open(AUDIT_PATH, "r", encoding="utf-8") as f:
                audit_data = json.load(f)
                for c in audit_data.get("components", []):
                    c_name = c.get("component_name")
                    bodies = c.get("bodies", [])
                    # Une pièce est active si elle a au moins un corps ou si c'est un sous-ensemble
                    if c_name and (len(bodies) > 0 or "ASV1" in c_name or "RS04" in c_name or "EL05" in c_name):
                        active_names.add(c_name.strip())
        except Exception as e:
            print(f"⚠️ Avertissement lecture audit métrologique : {e}")

    # Familles reconnues et sous-dossiers légitimes
    active_names.update([
        "RS04",
        "EL05",
        "Bassin_Pelvis",
        "Plastron_Ventral_Torse",
        "ceinture",
        "colonne_vertébrale"
    ])

    return active_names


def is_folder_active(folder_name, active_names):
    """Vérifie si un dossier de pièce isolée correspond à un composant actif."""
    f_norm = folder_name.strip()
    if f_norm in active_names:
        return True

    # Vérification insensible à la casse et tolérance tirets bas / espaces
    f_lower = f_norm.lower()
    for a in active_names:
        a_lower = a.lower()
        if f_lower == a_lower:
            return True
        if f_lower.replace("_", " ") == a_lower.replace("_", " "):
            return True

    return False


def get_dir_size(path):
    """Calcule la taille totale d'un dossier en octets."""
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            p = os.path.join(root, f)
            if not os.path.islink(p):
                total += os.path.getsize(p)
    return total


def audit_and_clean_visual_snapshots(dry_run=True):
    print("=" * 75)
    print("      D-BOT : AUDIT ET NETTOYAGE DU DOSSIER VISUAL_SNAPSHOTS")
    print("=" * 75)
    print(f"📂 Répertoire cible : {SNAPSHOTS_DIR}")
    print(f"⚙️ Mode d'exécution  : {'SIMULATION (Dry-Run)' if dry_run else 'PURGE EFFECTIVE (--purge)'}")

    if not os.path.exists(SNAPSHOTS_DIR):
        print(f"❌ Erreur : Le répertoire {SNAPSHOTS_DIR} est introuvable.")
        return 1

    active_names = load_active_components()
    print(f"🛡️ Composants actifs identifiés : {len(active_names)}")

    # -------------------------------------------------------------
    # 1. Audit de Pieces_Isolees
    # -------------------------------------------------------------
    orphan_piece_folders = []
    total_piece_orphan_bytes = 0

    if os.path.exists(PIECES_DIR):
        for entry in sorted(os.listdir(PIECES_DIR)):
            entry_path = os.path.join(PIECES_DIR, entry)
            if not os.path.isdir(entry_path) or entry.startswith("."):
                continue

            # Cas particulier connu de renommage / scission ou composants vidés
            is_obsolete = False
            reason = ""

            if entry == "Corniere":
                is_obsolete = True
                reason = "Scindée le 2026-10-27 en 'Corniere_haute' et 'Corniere_basse'"
            elif entry == "Panier_Batterie_Coulissant":
                is_obsolete = True
                reason = "Remplacé par 'Panier_Batterie_Droit' et 'Panier_Batterie_Gauche'"
            elif entry == "Capot_Verrouillage_Batterie":
                is_obsolete = True
                reason = "Supprimé (verrouillage intégré dans les paniers latéraux)"
            elif not is_folder_active(entry, active_names):
                is_obsolete = True
                reason = "Non référencé dans les composants actifs de la CAO"

            if is_obsolete:
                size_bytes = get_dir_size(entry_path)
                mtime = os.path.getmtime(entry_path)
                dt_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                files_count = len([f for f in os.listdir(entry_path) if not f.startswith(".")])
                orphan_piece_folders.append((entry, entry_path, size_bytes, dt_str, files_count, reason))
                total_piece_orphan_bytes += size_bytes

    # -------------------------------------------------------------
    # 2. Audit de Vues_Ensemble (Doublons d'indexation suite à la vue dessous)
    # -------------------------------------------------------------
    orphan_ensemble_files = []
    total_ensemble_orphan_bytes = 0

    if os.path.exists(ENSEMBLE_DIR):
        all_ensemble_files = sorted(os.listdir(ENSEMBLE_DIR))
        for f in all_ensemble_files:
            if f.startswith(".") or not f.endswith(".png"):
                continue

            f_path = os.path.join(ENSEMBLE_DIR, f)
            mtime = os.path.getmtime(f_path)
            dt_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            f_size = os.path.getsize(f_path)

            # Si le fichier ne fait pas partie des 7 vues officielles actives
            # OU s'il s'agit d'un doublon antérieur (ex: 04_vue_profil_droit antérieur à 04_vue_dessous)
            if f not in OFFICIAL_ENSEMBLE_VIEWS:
                reason = "Fichier non répertorié dans la nomenclature officielle des 7 vues"
                orphan_ensemble_files.append((f, f_path, f_size, dt_str, reason))
                total_ensemble_orphan_bytes += f_size
            elif f in ["04_vue_profil_droit.png", "05_vue_profil_gauche.png", "06_vue_isometrique.png"]:
                # Ces 3 fichiers correspondent à l'ancien indexage à 6 vues
                # Vérifions s'il existe la version à jour (05_vue_profil_droit, 06_vue_profil_gauche, 07_vue_isometrique)
                has_updated_counterpart = (
                    (f == "04_vue_profil_droit.png" and "05_vue_profil_droit.png" in all_ensemble_files) or
                    (f == "05_vue_profil_gauche.png" and "06_vue_profil_gauche.png" in all_ensemble_files) or
                    (f == "06_vue_isometrique.png" and "07_vue_isometrique.png" in all_ensemble_files)
                )
                if has_updated_counterpart and dt_str < "2026-10-27 21:20":
                    reason = "Ancien indexage 6 vues (supplanté par l'indexage 7 vues avec vue de dessous)"
                    orphan_ensemble_files.append((f, f_path, f_size, dt_str, reason))
                    total_ensemble_orphan_bytes += f_size

    # -------------------------------------------------------------
    # 3. Affichage du Bilan Diagnostic
    # -------------------------------------------------------------
    total_orphans = len(orphan_piece_folders) + len(orphan_ensemble_files)
    total_bytes = total_piece_orphan_bytes + total_ensemble_orphan_bytes

    print("\n🔍 RÉSULTAT DU DIAGNOSTIC :")
    if total_orphans == 0:
        print("  ✅ Aucun élément orphelin ou obsolète détecté dans Visual_Snapshots.")
        print("  Le dossier est 100% synchronisé avec l'assemblage actif.")
        print("=" * 75)
        return 0

    if orphan_piece_folders:
        print(f"\n📁 Dossiers obsolètes ou renommés dans 'Pieces_Isolees/' ({len(orphan_piece_folders)}) :")
        for name, _, size, dt, count, reason in orphan_piece_folders:
            print(f"  • {name:<32} [{count} fichiers, {size / 1024:6.1f} Ko, {dt}]")
            print(f"    └─ Motifs : {reason}")

    if orphan_ensemble_files:
        print(f"\n🖼️ Fichiers d'ensemble obsolètes dans 'Vues_Ensemble/' ({len(orphan_ensemble_files)}) :")
        for name, _, size, dt, reason in orphan_ensemble_files:
            print(f"  • {name:<32} [{size / 1024:6.1f} Ko, {dt}]")
            print(f"    └─ Motifs : {reason}")

    print(f"\n📊 Bilan : {len(orphan_piece_folders)} dossier(s) et {len(orphan_ensemble_files)} fichier(s) orphelin(s) ({total_bytes / 1024:.1f} Ko à libérer).")

    # -------------------------------------------------------------
    # 4. Action de Purge ou Recommandation Dry-Run
    # -------------------------------------------------------------
    if dry_run:
        print("\n💡 Action recommandée :")
        print("  Pour supprimer définitivement ces éléments orphelins, exécutez la commande suivante :")
        print("  /opt/homebrew/bin/python3.11 \"/Users/Shared/Mon Google Drive Physique/Documentation/Code/scripts/cad_tools/clean_visual_snapshots.py\" --purge")
    else:
        print("\n🗑️ Exécution de la purge effective...")
        purged_dirs = 0
        purged_files = 0
        errors = 0

        # Purge des dossiers de pièces
        for name, path, _, _, _, _ in orphan_piece_folders:
            try:
                shutil.rmtree(path)
                purged_dirs += 1
                print(f"  ✅ Dossier supprimé : {name}")
            except Exception as e:
                print(f"  ❌ Erreur suppression dossier {name} : {e}")
                errors += 1

        # Purge des fichiers d'ensemble
        for name, path, _, _, _ in orphan_ensemble_files:
            try:
                os.remove(path)
                purged_files += 1
                print(f"  ✅ Fichier supprimé : {name}")
            except Exception as e:
                print(f"  ❌ Erreur suppression fichier {name} : {e}")
                errors += 1

        print(f"\n🎉 Purge terminée avec succès :")
        print(f"  • {purged_dirs} dossier(s) supprimé(s).")
        print(f"  • {purged_files} fichier(s) supprimé(s).")
        print(f"  • {total_bytes / 1024:.1f} Ko d'espace disque libéré.")
        if errors:
            print(f"  • {errors} erreur(s) rencontrée(s).")

    print("=" * 75)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Audit et purge des pièces et vues obsolètes dans Visual_Snapshots."
    )
    parser.add_argument(
        "--purge",
        action="store_true",
        help="Supprime réellement les éléments orphelins (sinon dry-run par défaut)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Effectue une simulation sans suppression (comportement par défaut)."
    )
    args = parser.parse_args()

    dry_run = not args.purge
    return audit_and_clean_visual_snapshots(dry_run=dry_run)


if __name__ == "__main__":
    sys.exit(main())

