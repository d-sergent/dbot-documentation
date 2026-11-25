#!/opt/homebrew/bin/python3.11
"""Gestionnaire natif Python de SearXNG sans Docker pour D-Bot (macOS Apple Silicon).

Installe, configure, demarre et arrete une instance SearXNG + Granian strictement
isolee dans /Users/Shared/dbot_searxng (.venv via uv + Python 3.11, 0 Docker,
0 pollution du Python systeme Homebrew, 0 Mo RAM lorsque arrete).
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

from rag_runtime import _is_loopback_url  # noqa: E402

DEFAULT_SEARXNG_ROOT = Path("/Users/Shared/dbot_searxng")
DEFAULT_SEARXNG_HOST = "127.0.0.1"
DEFAULT_SEARXNG_PORT = 8088
DEFAULT_SEARXNG_URL = f"http://{DEFAULT_SEARXNG_HOST}:{DEFAULT_SEARXNG_PORT}"

UV_BIN = Path("/Users/davidsergent/.local/bin/uv")
PYTHON311_BIN = Path("/opt/homebrew/bin/python3.11")
GIT_BIN = Path("/opt/homebrew/bin/git")
PS_BIN = Path("/bin/ps")
SEARXNG_REPO_URL = "https://github.com/searxng/searxng.git"


def resolve_searxng_root() -> Path:
    """Retourne le repertoire racine d'installation de SearXNG natif."""
    raw = os.environ.get("DBOT_SEARXNG_ROOT", "").strip()
    return Path(raw) if raw else DEFAULT_SEARXNG_ROOT


def resolve_searxng_url() -> str:
    """Retourne l'URL locale loopback de SearXNG (defaut http://127.0.0.1:8088)."""
    raw = os.environ.get("SEARXNG_URL", "").strip().rstrip("/")
    return raw or DEFAULT_SEARXNG_URL


def is_searxng_installed(root: Path | None = None) -> bool:
    """Verifie si le depot SearXNG, le venv Granian et settings.yml sont presents."""
    base = Path(root) if root else resolve_searxng_root()
    return (
        (base / "repo" / "searx" / "webapp.py").is_file()
        and (base / ".venv" / "bin" / "granian").is_file()
        and (base / "settings.yml").is_file()
    )


def write_searxng_settings(
    root: Path,
    *,
    host: str = DEFAULT_SEARXNG_HOST,
    port: int = DEFAULT_SEARXNG_PORT,
    overwrite: bool = False,
) -> Path:
    """Genere settings.yml avec cle secret_key aleatoire 256 bits et sortie JSON activee."""
    base = Path(root)
    base.mkdir(parents=True, exist_ok=True)
    settings_path = base / "settings.yml"
    if settings_path.exists() and not overwrite:
        try:
            os.chmod(settings_path, 0o600)
        except OSError:
            pass
        return settings_path

    secret_token = secrets.token_hex(32)
    yaml_text = (
        "# Configuration SearXNG D-Bot souveraine (mono-utilisateur loopback)\n"
        "use_default_settings: true\n\n"
        "server:\n"
        f'  bind_address: "{host}"\n'
        f"  port: {int(port)}\n"
        f'  secret_key: "{secret_token}"\n'
        "  limiter: false\n"
        "  image_proxy: false\n\n"
        "search:\n"
        '  default_lang: "fr-FR"\n'
        "  formats:\n"
        "    - html\n"
        "    - json\n"
    )
    settings_path.write_text(yaml_text, encoding="utf-8")
    os.chmod(settings_path, 0o600)
    return settings_path


def _run_step(cmd: list[str], *, cwd: Path | None = None) -> None:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()[-1500:]
        raise RuntimeError(f"Echec commande {' '.join(cmd)} (code {proc.returncode}): {detail}")


def install_searxng_native(
    root: Path | None = None,
    *,
    host: str = DEFAULT_SEARXNG_HOST,
    port: int = DEFAULT_SEARXNG_PORT,
    update_repo: bool = False,
) -> dict[str, Any]:
    """Clone SearXNG, cree le venv Python 3.11 via uv et installe Granian."""
    base = Path(root) if root else resolve_searxng_root()
    base.mkdir(parents=True, exist_ok=True)
    repo_dir = base / "repo"
    venv_dir = base / ".venv"
    venv_python = venv_dir / "bin" / "python"

    if not UV_BIN.is_file():
        raise RuntimeError(f"uv introuvable a l'emplacement attendu : {UV_BIN}")
    if not PYTHON311_BIN.is_file():
        raise RuntimeError(f"Python 3.11 introuvable : {PYTHON311_BIN}")
    if not GIT_BIN.is_file():
        raise RuntimeError(f"git introuvable : {GIT_BIN}")

    if not (repo_dir / "searx" / "webapp.py").is_file():
        _run_step([str(GIT_BIN), "clone", "--depth", "1", SEARXNG_REPO_URL, str(repo_dir)])
    elif update_repo:
        _run_step([str(GIT_BIN), "-C", str(repo_dir), "pull", "--ff-only"])

    if not venv_python.is_file():
        _run_step([str(UV_BIN), "venv", "--python", str(PYTHON311_BIN), str(venv_dir)])

    _run_step(
        [
            str(UV_BIN),
            "pip",
            "install",
            "--python",
            str(venv_python),
            "setuptools",
            "wheel",
            "granian",
        ]
    )

    req_file = repo_dir / "requirements.txt"
    if req_file.is_file():
        _run_step(
            [
                str(UV_BIN),
                "pip",
                "install",
                "--python",
                str(venv_python),
                "-r",
                str(req_file),
            ]
        )
        _run_step(
            [
                str(UV_BIN),
                "pip",
                "install",
                "--python",
                str(venv_python),
                "--no-build-isolation",
                "--no-deps",
                "-e",
                str(repo_dir),
            ]
        )
    else:
        _run_step(
            [
                str(UV_BIN),
                "pip",
                "install",
                "--python",
                str(venv_python),
                "--no-build-isolation",
                "-e",
                str(repo_dir),
            ]
        )

    settings_path = write_searxng_settings(base, host=host, port=port, overwrite=False)
    env = os.environ.copy()
    env["SEARXNG_SETTINGS_PATH"] = str(settings_path)
    check = subprocess.run(
        [str(venv_python), "-c", "import searx.webapp; print('SEARX_IMPORT_OK')"],
        cwd=str(repo_dir),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if check.returncode != 0:
        detail = (check.stderr or check.stdout or "").strip()[-1000:]
        raise RuntimeError(f"Verification import searx.webapp echouee : {detail}")

    return get_searxng_status(root=base, url=f"http://{host}:{int(port)}")


def _read_pid_info(pid_file: Path) -> tuple[int | None, float | None]:
    if not pid_file.is_file():
        return None, None
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None, None
    if pid <= 0 or not PS_BIN.is_file():
        return None, None

    proc = subprocess.run(
        [str(PS_BIN), "-o", "rss=,command=", "-p", str(pid)],
        capture_output=True,
        text=True,
        timeout=2.0,
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None, None
    line = proc.stdout.strip()
    parts = line.split(None, 1)
    if len(parts) < 2:
        return None, None
    try:
        rss_kb = int(parts[0])
    except ValueError:
        return None, None
    cmd_str = parts[1].lower()
    if "granian" not in cmd_str and "searx" not in cmd_str:
        return None, None
    return pid, round(rss_kb / 1024.0, 1)


def _probe_searxng_config(base_url: str, *, timeout: float = 1.5) -> tuple[bool, int | None, str | None]:
    clean_url = base_url.rstrip("/")
    if not _is_loopback_url(clean_url):
        return False, None, f"URL SearXNG non-loopback refusee : {clean_url}"
    req = urllib.request.Request(
        f"{clean_url}/config",
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="replace"))
            engines = payload.get("engines") if isinstance(payload, dict) else None
            count = len(engines) if isinstance(engines, list) else None
            return True, count, None
    except urllib.error.HTTPError as exc:
        return False, None, f"HTTP {exc.code}"
    except Exception as exc:
        return False, None, str(exc)


def get_searxng_status(root: Path | None = None, url: str | None = None) -> dict[str, Any]:
    """Retourne l'etat complet d'installation, PID, RSS Mo et sante HTTP de SearXNG."""
    base = Path(root) if root else resolve_searxng_root()
    base_url = (url or resolve_searxng_url()).rstrip("/")
    installed = is_searxng_installed(base)
    pid, rss_mb = _read_pid_info(base / "searxng.pid")
    reachable, engines_count, err = _probe_searxng_config(base_url, timeout=1.5)
    return {
        "installed": installed,
        "reachable": reachable,
        "running_pid": pid,
        "rss_mb": rss_mb if reachable or pid else 0.0,
        "base_url": base_url,
        "root": str(base),
        "settings_path": str(base / "settings.yml"),
        "engines_count": engines_count,
        "error": None if reachable else err,
    }


def start_searxng(
    root: Path | None = None,
    *,
    host: str = DEFAULT_SEARXNG_HOST,
    port: int = DEFAULT_SEARXNG_PORT,
    wait_ready_s: float = 15.0,
) -> dict[str, Any]:
    """Demarre Granian + searx.webapp:app en arriere-plan et attend /config."""
    base = Path(root) if root else resolve_searxng_root()
    if not is_searxng_installed(base):
        raise RuntimeError(
            f"SearXNG natif non installe dans {base}. Executez searxng_manager.py install."
        )
    target_url = f"http://{host}:{int(port)}"
    cur = get_searxng_status(root=base, url=target_url)
    if cur["reachable"]:
        return cur

    granian_bin = base / ".venv" / "bin" / "granian"
    settings_path = base / "settings.yml"
    log_path = base / "searxng.log"
    pid_path = base / "searxng.pid"

    env = os.environ.copy()
    env["SEARXNG_SETTINGS_PATH"] = str(settings_path)
    env.pop("SEARXNG_SECRET", None)

    cmd = [
        str(granian_bin),
        "--interface",
        "wsgi",
        "--host",
        host,
        "--port",
        str(int(port)),
        "--workers",
        "1",
        "searx.webapp:app",
    ]
    with log_path.open("ab") as log_fh:
        proc = subprocess.Popen(
            cmd,
            cwd=str(base / "repo"),
            env=env,
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    pid_path.write_text(f"{proc.pid}\n", encoding="utf-8")

    deadline = time.monotonic() + float(wait_ready_s)
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(
                f"Granian s'est arrete prematurement (code {proc.returncode}). Voir {log_path}"
            )
        ok, _, _ = _probe_searxng_config(target_url, timeout=1.0)
        if ok:
            return get_searxng_status(root=base, url=target_url)
        time.sleep(0.3)

    raise RuntimeError(f"Timeout attente SearXNG ({wait_ready_s} s) sur {target_url}")


def stop_searxng(root: Path | None = None, *, url: str | None = None) -> dict[str, Any]:
    """Arrete proprement le serveur Granian SearXNG pour liberer 100 % de sa RAM."""
    base = Path(root) if root else resolve_searxng_root()
    pid_path = base / "searxng.pid"
    pid, _ = _read_pid_info(pid_path)
    if pid is not None:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pid = None

        if pid is not None:
            deadline = time.monotonic() + 4.0
            while time.monotonic() < deadline:
                cur_pid, _ = _read_pid_info(pid_path)
                if cur_pid is None:
                    break
                time.sleep(0.2)
            else:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                time.sleep(0.2)

    pid_path.unlink(missing_ok=True)
    return get_searxng_status(root=base, url=url)


def test_searxng_query(
    query: str,
    *,
    max_results: int = 5,
    base_url: str | None = None,
) -> dict[str, Any]:
    """Execute une requete /search?format=json pour valider SearXNG en direct."""
    root_url = (base_url or resolve_searxng_url()).rstrip("/")
    if not _is_loopback_url(root_url):
        raise ValueError(f"URL non-loopback refusee : {root_url}")
    qs = urllib.parse.urlencode({"q": query, "format": "json", "language": "fr-FR"})
    req = urllib.request.Request(
        f"{root_url}/search?{qs}",
        headers={"Accept": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=10.0) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))
    results = []
    for item in (data.get("results") or [])[:max_results]:
        if isinstance(item, dict):
            results.append(
                {
                    "title": str(item.get("title") or ""),
                    "url": str(item.get("url") or ""),
                    "engine": str(item.get("engine") or ""),
                    "content": str(item.get("content") or "")[:240],
                }
            )
    return {
        "query": query,
        "number_of_results": data.get("number_of_results"),
        "count": len(results),
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gestionnaire natif SearXNG D-Bot (0 Docker)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_inst = sub.add_parser("install", help="Installe SearXNG + Granian dans /Users/Shared/dbot_searxng")
    p_inst.add_argument("--root", type=Path, default=resolve_searxng_root())
    p_inst.add_argument("--host", default=DEFAULT_SEARXNG_HOST)
    p_inst.add_argument("--port", type=int, default=DEFAULT_SEARXNG_PORT)
    p_inst.add_argument("--update", action="store_true")

    p_start = sub.add_parser("start", help="Demarre SearXNG sur 127.0.0.1:8088")
    p_start.add_argument("--root", type=Path, default=resolve_searxng_root())
    p_start.add_argument("--host", default=DEFAULT_SEARXNG_HOST)
    p_start.add_argument("--port", type=int, default=DEFAULT_SEARXNG_PORT)

    p_stop = sub.add_parser("stop", help="Arrete SearXNG et libere sa RAM")
    p_stop.add_argument("--root", type=Path, default=resolve_searxng_root())

    p_stat = sub.add_parser("status", help="Affiche l'etat JSON de SearXNG")
    p_stat.add_argument("--root", type=Path, default=resolve_searxng_root())

    p_test = sub.add_parser("test-search", help="Teste une requete /search?format=json")
    p_test.add_argument("query", help="Requete de test")
    p_test.add_argument("--max-results", type=int, default=3)

    args = parser.parse_args(argv)
    if args.command == "install":
        res = install_searxng_native(
            root=args.root, host=args.host, port=args.port, update_repo=args.update
        )
    elif args.command == "start":
        res = start_searxng(root=args.root, host=args.host, port=args.port)
    elif args.command == "stop":
        res = stop_searxng(root=args.root)
    elif args.command == "status":
        res = get_searxng_status(root=args.root)
    else:
        res = test_searxng_query(args.query, max_results=args.max_results)

    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
