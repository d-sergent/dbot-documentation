#!/usr/bin/env python3
"""
Script d'audit de securite unifie pour le projet D-Bot.
Orchestre trois niveaux d'analyse defensive :
1. SCA (Software Composition Analysis) : detection des CVEs dans les dependances via pip-audit / OSV.
2. SAST (Static Application Security Testing) : audit du code source Python via Bandit.
3. Secret Scanning : detection des fuites d'identifiants et de cles API en clair dans le code.

Zero dependance externe requise (utilise uvx pour executer les moteurs d'analyse de maniere isolee).
"""

import os
import sys
import re
import shutil
import argparse
import subprocess
from pathlib import Path

# Constantes de chemins
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CODE_DIR = PROJECT_ROOT / "Code"
DEFAULT_PYTHON = "/opt/homebrew/bin/python3.11"
DEFAULT_SITE_PACKAGES = "/opt/homebrew/lib/python3.11/site-packages"
UV_PATH = Path("/Users/davidsergent/.local/bin/uv")
UVX_PATH = Path("/Users/davidsergent/.local/bin/uvx")

# Detection binaire uvx
if not UVX_PATH.is_file():
    found_uvx = shutil.which("uvx")
    if found_uvx:
        UVX_PATH = Path(found_uvx)

# Motifs de cles d'API pour le Secret Scanning
SECRET_PATTERNS = [
    ("Cle OpenAI (sk-...)", re.compile(r"sk-[a-zA-Z0-9]{32,}")),
    ("Cle Groq Cloud (gsk_...)", re.compile(r"gsk_[a-zA-Z0-9]{40,}")),
    ("Cle Google Gemini (AIzaSy...)", re.compile(r"AIzaSy[a-zA-Z0-9_-]{33}")),
    ("Cle OpenRouter (sk-or-v1-...)", re.compile(r"sk-or-v1-[a-f0-9]{64}")),
    ("Cle Privee RSA/OpenSSH", re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----")),
]

# Fichiers et dossiers ignores par defaut pour le scan de secrets
IGNORE_EXTENSIONS = {
    ".pyc", ".png", ".jpg", ".jpeg", ".svg", ".step", ".stp", ".FCStd",
    ".stl", ".bin", ".onnx", ".engine", ".log", ".safetensors", ".pt", ".pth",
    ".npy", ".npz", ".wav", ".mp3", ".pkl"
}
IGNORE_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "build", "dist",
    "node_modules", "Exports_CAO_DBot", "models_cache", "rag_storage"
}
MAX_FILE_SIZE_BYTES = 1024 * 1024  # 1 Mo max par fichier pour le scan de secrets


def print_banner():
    banner = """
======================================================================
           SHIELD D-BOT : AUDIT DE SECURITE UNIFIE
   SCA (CVEs) | SAST (Code Source) | Scan de Secrets
======================================================================
"""
    print(banner)


def run_sca_audit(python_bin: str, site_packages_dir: str) -> int:
    """Analyse les vulnerabilites CVEs des bibliotheques via pip-audit isole sous uvx."""
    print("\n🔍 [1/3] Audit SCA des dependances logicielles (pip-audit & Base OSV)...")
    if not UVX_PATH.is_file():
        print("  ⚠️ Binaire uvx introuvable. Veuillez verifier le chemin d'acces a uv.")
        return 1

    if not Path(site_packages_dir).is_dir():
        print(f"  ⚠️ Repertoire site-packages introuvable : {site_packages_dir}")
        return 1

    cmd = [
        str(UVX_PATH),
        "--python", python_bin,
        "pip-audit",
        "--path", site_packages_dir,
        "--format", "columns",
        "--desc", "on"
    ]
    
    print(f"  ⚙️ Execution : pip-audit sur {site_packages_dir}")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print("  ✅ Aucune vulnerabilite critique detectee dans les packages installes.")
            return 0
        else:
            print("  ⚠️ Vulnerabilites connues detectees par pip-audit :")
            lines = res.stdout.strip().splitlines()
            if lines:
                for line in lines[:25]:
                    print(f"    {line}")
                if len(lines) > 25:
                    print(f"    ... ({len(lines) - 25} autres lignes tronquees, relancer avec --full pour tout voir)")
            else:
                print(res.stderr.strip()[:500])
            return res.returncode
    except Exception as e:
        print(f"  ❌ Erreur lors du lancement de pip-audit : {e}")
        return 1


def run_sast_audit(python_bin: str, target_dir: Path, min_severity: str = "medium") -> int:
    """Analyse statique de securite du code Python via Bandit sous uvx."""
    print(f"\n🔍 [2/3] Audit SAST du code source Python (Bandit sur {target_dir.name})...")
    if not UVX_PATH.is_file():
        print("  ⚠️ Binaire uvx introuvable.")
        return 1

    flag = "-ll" if min_severity == "medium" else "-lll"
    cmd = [
        str(UVX_PATH),
        "--python", python_bin,
        "bandit",
        "-r", str(target_dir),
        flag
    ]

    print(f"  ⚙️ Execution : bandit sur {target_dir} (Severite >= {min_severity.upper()})")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print("  ✅ Aucune faille de severite moyenne ou haute detectee dans le code source.")
            return 0
        else:
            print("  ⚠️ Faiblesses potentielles detectees dans le code Python :")
            output_lines = res.stdout.strip().splitlines()
            # Filtrer pour presenter le rapport synthetique
            for line in output_lines:
                if ">> Issue:" in line or "Severity:" in line or "Location:" in line:
                    print(f"    {line.strip()}")
            return res.returncode
    except Exception as e:
        print(f"  ❌ Erreur lors du lancement de Bandit : {e}")
        return 1


def run_secret_scanning(target_dir: Path) -> int:
    """Scanne les fichiers de code pour reperer d'eventuelles cles secretes hardcodees."""
    print(f"\n🔍 [3/3] Scan des secrets et identifiants en clair dans {target_dir.name}...")
    leaks_found = 0

    for root, dirs, files in os.walk(target_dir):
        # Exclure les dossiers ignores
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file_name in files:
            file_path = Path(root) / file_name
            if file_path.suffix.lower() in IGNORE_EXTENSIONS:
                continue

            try:
                if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                    continue
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, start=1):
                        # Ignorer les lignes de documentation contenant des points de suspension
                        if "..." in line:
                            continue
                        for label, pattern in SECRET_PATTERNS:
                            if pattern.search(line):
                                print(f"  🚨 Fuite suspectee ({label}) dans {file_path.relative_to(PROJECT_ROOT)}:{line_num}")
                                leaks_found += 1
            except Exception:
                continue

    if leaks_found == 0:
        print("  ✅ Aucun secret ou cle API en clair detecte dans le code source.")
        return 0
    else:
        print(f"  ⚠️ {leaks_found} motif(s) de secret suspect(s) identifie(s). Verifiez vos fichiers.")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Audit de securite unifie D-Bot")
    parser.add_argument("--python", default=DEFAULT_PYTHON, help="Chemin du binaire Python a auditer")
    parser.add_argument("--site-packages", default=DEFAULT_SITE_PACKAGES, help="Chemin du dossier site-packages")
    parser.add_argument("--code-dir", default=str(CODE_DIR), help="Chemin du dossier de code source a scanner")
    parser.add_argument("--severity", choices=["medium", "high"], default="high", help="Niveau de severite minimal Bandit")
    parser.add_argument("--skip-sca", action="store_true", help="Passer l'audit des dependances pip-audit")
    parser.add_argument("--skip-sast", action="store_true", help="Passer l'audit statique Bandit")
    parser.add_argument("--skip-secrets", action="store_true", help="Passer le scan des secrets")

    args = parser.parse_args()
    print_banner()

    status = {
        "sca": 0,
        "sast": 0,
        "secrets": 0
    }

    if not args.skip_sca:
        status["sca"] = run_sca_audit(args.python, args.site_packages)

    if not args.skip_sast:
        status["sast"] = run_sast_audit(args.python, Path(args.code_dir), min_severity=args.severity)

    if not args.skip_secrets:
        status["secrets"] = run_secret_scanning(Path(args.code_dir))

    print("\n======================================================================")
    print("                      BILAN DE L'AUDIT DE SECURITE")
    print("======================================================================")
    print(f"  1. Audit Dependances (CVEs)  : {'PASSED' if status['sca'] == 0 else 'ACTION REQUISE (CVEs detectees)'}")
    print(f"  2. Audit Code Source (SAST)  : {'PASSED' if status['sast'] == 0 else 'ACTION REQUISE (Alertes Bandit)'}")
    print(f"  3. Scan des Secrets (Cles)   : {'PASSED' if status['secrets'] == 0 else 'ACTION REQUISE (Secrets trouves)'}")
    print("======================================================================\n")

    overall_code = max(status.values())
    sys.exit(overall_code)


if __name__ == "__main__":
    main()
