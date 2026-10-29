#!/usr/bin/env python3
"""
Hook Git Pre-Commit pour le depot D-Bot.
Execute automatiquement l'audit de securite statique (Bandit SAST) et la detection
de secrets/cles d'API avant d'autoriser tout commit Git.

Empeche tout commit contenant une faille critique (shell=True, fuite de secret).
Execution ultra-rapide (< 2 secondes).
"""

import sys
import subprocess
from pathlib import Path

PYTHON_BIN = "/opt/homebrew/bin/python3.11"
SCRIPT_PATH = Path("/Users/Shared/Mon Google Drive Physique/Documentation/Code/security/audit_dbot_security.py")

def main():
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
