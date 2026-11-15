#!/usr/bin/env python3
"""
Hook Git Pre-Commit pour le depot D-Bot.
Execute automatiquement l'audit de securite statique (Bandit SAST) et la detection
de secrets/cles d'API avant d'autoriser tout commit Git.

Empeche tout commit contenant une faille critique (shell=True, fuite de secret).
Execution ultra-rapide (< 2 secondes).
"""

import sys
import json
import shutil
import subprocess
from pathlib import Path

PYTHON_BIN = "/opt/homebrew/bin/python3.11"
DOCS_ROOT = Path("/Users/Shared/Mon Google Drive Physique/Documentation")
SCRIPT_PATH = DOCS_ROOT / "Code/security/audit_dbot_security.py"
SYNC_SCRIPT_PATH = DOCS_ROOT / "Code/scripts/cad_tools/sync_visual_snapshots.py"


def sync_and_stage_snapshots():
    """Synchronise automatiquement les snapshots CAO/FEA modifies vers media/ avant commit."""
    if not SYNC_SCRIPT_PATH.is_file():
        return
    print("\n🔄 [Git Pre-Commit] Synchronisation automatique Visual_Snapshots -> media/...")
    res = subprocess.run(
        [PYTHON_BIN, str(SYNC_SCRIPT_PATH), "--sync", "--json"],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print("  ⚠️ Echec non bloquant de la verification snapshots :", res.stderr.strip())
        return
    try:
        payload = json.loads(res.stdout)
    except json.JSONDecodeError:
        return
    updated = payload.get("updated", [])
    if updated:
        git_bin = shutil.which("git") or "/usr/bin/git"
        subprocess.run([git_bin, "-C", str(DOCS_ROOT), "add", "--", *updated], check=False)
        print(f"  ✅ {len(updated)} image(s) media/ mise(s) a jour et ajoutee(s) au commit : {', '.join(updated)}")
    else:
        print(f"  ✅ Snapshots media/ a jour ({len(payload.get('up_to_date', []))} fichier(s)).")


def main():
    sync_and_stage_snapshots()
    if not SCRIPT_PATH.is_file():
        # Si le script d'audit n'est pas trouve, autoriser le commit avec avertissement
        print("⚠️ [Pre-Commit] Script d'audit introuvable a :", SCRIPT_PATH)
        sys.exit(0)

    cmd = [
        PYTHON_BIN,
        str(SCRIPT_PATH),
        "--skip-sca",
        "--severity", "high"
    ]

    print("\n🛡️ [Git Pre-Commit] Verification de securite en cours (SAST + Secrets)...")
    res = subprocess.run(cmd)

    if res.returncode != 0:
        print("\n" + "=" * 70)
        print("🚨 [BLOCAGE PRE-COMMIT] Des failles de securite ou secrets ont ete detectes !")
        print("   Le commit a ete annule pour proteger l'integrite du depot D-Bot.")
        print("   Veuillez corriger les alertes ci-dessus avant de commiter a nouveau.")
        print("=" * 70 + "\n")
        sys.exit(1)

    print("✅ [Git Pre-Commit] Code verifie et conforme. Commit autorise.\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
