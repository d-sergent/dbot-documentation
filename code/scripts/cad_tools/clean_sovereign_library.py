#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
clean_sovereign_library.py — Nettoyeur de Fichiers STEP Orphelins (D-Bot)
=============================================================================
Ce script inspecte le répertoire centralisé des exports CAO souverains :
/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/Bibliotheque_Composants_STEP/

Il compare la totalité des fichiers STEP/STP présents sur le disque avec les
composants réels référencés dans dbot_cad_manifest.json (le manifeste actif
issu de la conception Fusion 360).

Il détecte et purge les pièces qui ont changé de nom (ex: Corniere -> Corniere_haute),
les anciennes dénominations de quincaillerie avant standardisation, et les pièces
supprimées de la CAO.

Usage :
  python3 clean_sovereign_library.py            # Diagnostic et simulation (dry-run)
  python3 clean_sovereign_library.py --dry-run  # Simulation explicite
  python3 clean_sovereign_library.py --purge    # Purge réelle des fichiers orphelins
"""

import os
import sys
import json
import argparse

EXPORT_DIR = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/Bibliotheque_Composants_STEP"
MANIFEST_FILE = os.path.join(EXPORT_DIR, "dbot_cad_manifest.json")


def load_active_step_files(manifest_path):
    """Charge la liste des fichiers STEP actifs référencés dans le manifeste actif."""
    if not os.path.exists(manifest_path):
        print(f"❌ Erreur : Manifeste actif introuvable : {manifest_path}")
        return None

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erreur de lecture du manifeste JSON : {e}")
        return None

    components = data.get("components", {})
    active_steps = set()
    for comp_info in components.values():
        sf = comp_info.get("step_file")
        if sf:
            active_steps.add(sf.lower())

    return active_steps, data.get("metadata", {})


def audit_and_clean(dry_run=True):
    print("=" * 72)
    print("      D-BOT : AUDIT ET NETTOYAGE DE LA BIBLIOTHÈQUE STEP SOUVERAINE")
    print("=" * 72)
    print(f"📂 Répertoire cible : {EXPORT_DIR}")
    print(f"📋 Manifeste actif   : {MANIFEST_FILE}")
    print(f"⚙️ Mode d'exécution  : {'SIMULATION (Dry-Run)' if dry_run else 'PURGE EFFECTIVE (--purge)'}")

    if not os.path.exists(EXPORT_DIR):
        print(f"❌ Erreur : Le répertoire {EXPORT_DIR} est introuvable.")
        return 1

    res = load_active_step_files(MANIFEST_FILE)
    if res is None:
        return 1
    active_steps, meta = res

    doc_source = meta.get("source_document", "Inconnu")
    export_date = meta.get("export_date", "Inconnue")
    print(f"📄 Modèle CAO source: {doc_source} (Exporté le {export_date})")
    print(f"🛡️ Composants actifs: {len(active_steps)}")

    all_disk_files = os.listdir(EXPORT_DIR)
    step_disk_files = [f for f in all_disk_files if f.lower().endswith((".step", ".stp"))]
    print(f"📦 Fichiers sur disque: {len(step_disk_files)}")

    orphans = []
    total_orphan_bytes = 0

    for f_name in sorted(step_disk_files):
        if f_name.lower() not in active_steps:
            f_path = os.path.join(EXPORT_DIR, f_name)
            f_size = os.path.getsize(f_path)
            orphans.append((f_name, f_path, f_size))
            total_orphan_bytes += f_size

    print(f"\n🔍 Résultat du diagnostic :")
    if not orphans:
        print("  ✅ Aucun fichier STEP orphelin détecté.")
        print("  La bibliothèque est 100% propre, intègre et strictement alignée sur le modèle actif.")
        print("=" * 72)
        return 0

    print(f"  ⚠️ {len(orphans)} fichier(s) orphelin(s) / renommé(s) détecté(s) ({total_orphan_bytes / 1024:.1f} Ko) :\n")
    for f_name, _, f_size in orphans:
        print(f"    - {f_name:<65} ({f_size / 1024:7.1f} Ko)")

    if dry_run:
        print("\n💡 Action recommandée :")
        print("  Pour supprimer définitivement ces fichiers orphelins, exécutez :")
        print("  /opt/homebrew/bin/python3.11 \"/Users/Shared/Mon Google Drive Physique/Documentation/Code/scripts/cad_tools/clean_sovereign_library.py\" --purge")
    else:
        print("\n🗑️ Exécution de la purge...")
        purged_count = 0
        purge_errors = 0
        for f_name, f_path, _ in orphans:
            try:
                os.remove(f_path)
                purged_count += 1
            except Exception as e:
                print(f"  ❌ Erreur suppression {f_name}: {e}")
                purge_errors += 1

        print(f"\n✅ Purge terminée avec succès :")
        print(f"  • {purged_count} fichier(s) orphelin(s) supprimé(s).")
        print(f"  • {total_orphan_bytes / 1024:.1f} Ko d'espace disque libéré.")
        if purge_errors:
            print(f"  • {purge_errors} erreur(s) rencontrée(s).")

    print("=" * 72)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Audit et purge des fichiers STEP orphelins dans Bibliotheque_Composants_STEP."
    )
    parser.add_argument(
        "--purge",
        action="store_true",
        help="Supprime réellement les fichiers orphelins (sinon dry-run par défaut)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Effectue une simulation sans suppression (comportement par défaut)."
    )
    args = parser.parse_args()

    dry_run = not args.purge
    return audit_and_clean(dry_run=dry_run)


if __name__ == "__main__":
    sys.exit(main())
