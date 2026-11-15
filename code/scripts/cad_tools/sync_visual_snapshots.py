#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_visual_snapshots.py — Synchronisation Deterministe Visual_Snapshots -> Documentation/media
=============================================================================================
Maintient automatiquement la parite binaire (SHA-256) entre les rendus HD stockes dans
Exports_CAO_DBot (Visual_Snapshots) et leurs copies locales embarquees dans les dossiers
media/ de la documentation D-Bot.

Utilisations :
  - Appel direct :
      python3 sync_visual_snapshots.py --sync
      python3 sync_visual_snapshots.py --check
      python3 sync_visual_snapshots.py --discover
  - Appel automatique :
      * En fin d'execution de export_all_fea_snapshots.py
      * Lors de chaque commit Git via Code/security/git_hook_pre_commit.py
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_ROOT = SCRIPT_DIR.parent.parent.parent
MANIFEST_PATH = SCRIPT_DIR / "snapshot_sync_manifest.json"


def compute_sha256(file_path: Path) -> str:
    """Calcule l'empreinte SHA-256 d'un fichier binaire."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def load_manifest(manifest_path: Path = MANIFEST_PATH) -> tuple[Path, list[dict]]:
    """Charge le manifeste JSON de correspondance source -> cible."""
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    exports_rel = data.get("exports_root_rel", "../Exports_CAO_DBot")
    exports_root = (DOCS_ROOT / exports_rel).resolve()
    return exports_root, data.get("mappings", [])


def sync_snapshots(
    check_only: bool = False,
    strict: bool = False,
    quiet: bool = False,
) -> dict:
    """
    Verifie ou synchronise les snapshots declares dans le manifeste.

    Retourne un dictionnaire contenant les listes 'updated', 'up_to_date',
    'stale', 'missing_source', 'missing_target', et 'exports_available'.
    """
    exports_root, mappings = load_manifest()
    result = {
        "exports_available": exports_root.is_dir(),
        "updated": [],
        "up_to_date": [],
        "stale": [],
        "missing_source": [],
        "missing_target": [],
    }

    if not exports_root.is_dir():
        if not quiet:
            print(f"⚠️ [Snapshot Sync] Dossier source introuvable ({exports_root}) — synchronisation ignoree.")
        return result

    for entry in mappings:
        src = exports_root / entry["source"]
        dst = DOCS_ROOT / entry["target"]

        if not src.is_file():
            result["missing_source"].append(entry["source"])
            if not quiet:
                print(f"  ⚠️ Source absente : {src}")
            continue

        src_hash = compute_sha256(src)
        dst_exists = dst.is_file()
        dst_hash = compute_sha256(dst) if dst_exists else None

        if dst_exists and src_hash == dst_hash:
            result["up_to_date"].append(entry["target"])
            continue

        if check_only:
            if not dst_exists:
                result["missing_target"].append(entry["target"])
                if not quiet:
                    print(f"  ❌ Cible manquante : {entry['target']} (depuis {entry['source']})")
            else:
                result["stale"].append(entry["target"])
                if not quiet:
                    print(
                        f"  ⚠️ Desynchronise : {entry['target']} "
                        f"(local={dst_hash[:12]} != source={src_hash[:12]})"
                    )
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        result["updated"].append(entry["target"])
        if not quiet:
            action = "Mis a jour" if dst_exists else "Copie initiale"
            size_kib = dst.stat().st_size / 1024.0
            print(f"  ✅ {action} : {entry['target']} ({size_kib:.1f} Ko, sha256={src_hash[:12]})")

    if not quiet and not check_only and not result["updated"] and not result["missing_source"]:
        print(f"  ✅ Tous les snapshots ({len(result['up_to_date'])}) sont deja a jour.")

    if strict and result["missing_source"]:
        raise FileNotFoundError(f"Sources manquantes : {result['missing_source']}")

    return result


def discover_unmapped_overlaps(quiet: bool = False) -> list[dict]:
    """Detecte d'eventuelles images en double entre Exports_CAO_DBot et Documentation/**/media/."""
    exports_root, mappings = load_manifest()
    if not exports_root.is_dir():
        return []

    mapped_targets = {str((DOCS_ROOT / m["target"]).resolve()) for m in mappings}
    export_index: dict[str, list[Path]] = {}
    for root, _, files in os.walk(exports_root):
        for fname in files:
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                export_index.setdefault(fname, []).append(Path(root) / fname)

    overlaps = []
    ignore_dirs = {".git", "__pycache__", "Archives", "lightrag_db", "rag_storage"}
    for root, dirs, files in os.walk(DOCS_ROOT):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        if Path(root).name != "media":
            continue
        for fname in sorted(files):
            if fname in export_index:
                target_abs = str((Path(root) / fname).resolve())
                if target_abs not in mapped_targets:
                    overlaps.append(
                        {
                            "target": str((Path(root) / fname).relative_to(DOCS_ROOT)),
                            "sources": [str(p.relative_to(exports_root)) for p in export_index[fname]],
                        }
                    )

    if not quiet:
        if overlaps:
            print("⚠️ [Snapshot Discover] Images homonymes non declarees dans le manifeste :")
            for item in overlaps:
                print(f"  - {item['target']} <-> {item['sources']}")
        else:
            print("✅ [Snapshot Discover] Aucune image homonyme oubliee hors manifeste.")
    return overlaps


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synchronisation automatique des snapshots CAO/FEA vers les dossiers media/."
    )
    parser.add_argument("--check", action="store_true", help="Verifie sans copier (code retour non nul si ecart).")
    parser.add_argument("--sync", action="store_true", help="Synchronise les cibles modifiees ou manquantes (defaut).")
    parser.add_argument("--discover", action="store_true", help="Recherche d'eventuels doublons non encore declares.")
    parser.add_argument("--strict", action="store_true", help="Echoue si une source du manifeste est absente.")
    parser.add_argument("--json", action="store_true", help="Affiche le resultat JSON sur stdout.")
    args = parser.parse_args()

    try:
        res = sync_snapshots(check_only=args.check, strict=args.strict, quiet=args.json)
    except FileNotFoundError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    if args.discover:
        overlaps = discover_unmapped_overlaps(quiet=args.json)
        res["unmapped_overlaps"] = overlaps

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))

    if args.check and (res["stale"] or res["missing_target"]):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
