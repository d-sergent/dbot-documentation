#!/opt/homebrew/bin/python3.11
"""Moteur d'audit qualite et de sante pour la base LightRAG D-Bot (100 % lecture seule).

Analyse les stores JSON/GraphML de lightrag_dbot_db sans jamais instancier LightRAG
ni acquerir de verrou d'ecriture, ce qui garantit un fonctionnement sur pendant qu'une
indexation est en cours. Calcule un score de sante (0-100) par document et produit
des sorties CLI, JSON ou HTML autonome.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import networkx as nx
import requests

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

from agent_indexing import (  # noqa: E402
    COMPLETION_DELIMITER,
    IMAGE_EXTS,
    PDF_EXTS,
    SVG_EXTS,
    TUPLE_DELIMITER,
    _METRIC_RE,
    _is_orphan_entry,
    _rel_path_from_doc_entry,
    collect_docs_files,
    is_indexing_lock_active,
    validate_single_extraction,
)
from rag_chunking import (  # noqa: E402
    CRITICAL_DOC_PREFIXES,
    compute_normalized_sha256,
    resolve_gleaning_for_doc,
)
from rag_runtime import (  # noqa: E402
    DEFAULT_DRIVE_MIRROR_DB_PATH,
    DEFAULT_LOCAL_DB_PATH,
    resolve_default_db_path,
)
from source_key_utils import (  # noqa: E402
    build_active_source_aliases,
    canonical_source_name,
    extract_rel_path,
    extract_section_key,
)

DEFAULT_DOCS_ROOT = Path(
    os.environ.get("RAG_DOCS_ROOT", "/Users/Shared/Mon Google Drive Physique/Documentation")
)
DEFAULT_DB_PATH = Path(resolve_default_db_path())
DEFAULT_LOG_PATH = Path(__file__).resolve().parent / "rag_indexing.log"
DEFAULT_BENCHMARK_PATH = (
    DEFAULT_DOCS_ROOT / "Annexes/Outils_de_Travail/RAG/BENCHMARK_QA_DBOT_120.json"
)
DEFAULT_AUDIT_MD_PATH = DEFAULT_DOCS_ROOT / "Annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md"

CAD_AUDIT_JSON_REL = (
    "01_Mecanique_et_Chassis/Torse_et_Bassin/Audits/AUDIT_METROLOGIQUE_Torse_et_Bassin.json"
)
CAD_TARGET_DOCS_RELS = (
    "01_Mecanique_et_Chassis/Torse_et_Bassin/SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md",
    "01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md",
    "01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md",
    "01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md",
    "01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Bilan_Masse_Global_et_Opportunite_Waist_Pitch_2DoF.md",
)
LOCAL_BOM_REL = "01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md"
GLOBAL_BOM_REL = "05_Gestion_Projet/FINAL_Liste_Achats_BOM.md"
TORSE_MEDIA_REL = "01_Mecanique_et_Chassis/Torse_et_Bassin/media"
_CAD_KEY_PARTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Plastron_Ventral_Torse", ("Plastron_Ventral_Torse",)),
    ("RB8016", ("RB8016",)),
    ("Traverse_Renfort_Bassin", ("Traverse_Renfort_Bassin",)),
    ("colonne vertebrale", ("colonne vertébrale", "colonne vertebrale")),
    ("Chassis_Structurel_Bassin_Last", ("Chassis_Structurel_Bassin_Last",)),
    ("Waist_Plate_7075", ("Waist_Plate_7075",)),
    ("Selle de Pont Pelvis", ("Selle de Pont Pelvis",)),
    ("Bride Epaule", ("Bride Epaule",)),
    ("Moyeu_Waist_Sandwich_7075", ("Moyeu_Waist_Sandwich_7075",)),
)
_TORSE_VER_RE = re.compile(r"Torse-123\s*v(\d+)", re.IGNORECASE)
_MASS_G_RE = re.compile(r"(\d+(?:\.\d+)?)\s*g\b", re.IGNORECASE)
_MASS_KG_RE = re.compile(r"(\d+(?:\.\d+)?)\s*kg\b", re.IGNORECASE)
LEVEL1_DOC_PREFIXES = (
    "FINAL_",
    "DOSSIER_TECHNIQUE_",
    "GUIDE_COMPLET_",
    "SYNTHESE_METROLOGIQUE_",
)
LEVEL2_STUDY_PREFIXES = ("STUDY_",)
LEVEL2_AUDIT_PREFIXES = ("AUDIT_",)

CRITICAL_PREFIXES = CRITICAL_DOC_PREFIXES

_MCMASTER_RE = re.compile(r"\b9\d{4}[A-Za-z]\d{3}\b")
_ROBSTRIDE_RE = re.compile(r"\bRS-?0[0-6]\b", re.IGNORECASE)
_NUM_UNIT_VALUE_RE = re.compile(r"\b(\d+(?:[.,]\d+)?)\s*(?:mm|cm|m|kg|g|nm|n\.m|mpa|kpa|v|a|ah|wh|w|hz|khz|mhz|deg)\b", re.IGNORECASE)
_CAMEL_SPLIT_ARTIFACT_RE = re.compile(r"\b[A-Z][a-z]{2,}[A-Z][a-z]{1,}\s+[A-Z][a-z]?\b")
_LATEX_ARTIFACT_RE = re.compile(r"\\(?:text|approx|varnothing|pm|sqrt|circ|times|cdot|frac|mathbf)\b")
_DOLLAR_CHAR = chr(36)
_LOG_ENGINE_RE = re.compile(r"Moteur d'indexation actif\s*:\s*(.+)$")
_LOG_PROGRESS_RE = re.compile(r"\[(\s*\d+/\s*\d+)\]\s*(?:📄\s*)?(.+?)(?:\s+\[.*\])?$")
_LOG_TIME_RE = re.compile(r"^\[(\d{2}:\d{2}:\d{2})\]")
_LOG_CHUNK_RE = re.compile(
    r"Chunk\s+(\d+)\s+of\s+(\d+)\s+extracted\s+(\d+)\s+Ent\s+\+\s+(\d+)\s+Rel\s+(.+)$"
)
_LOG_OLLAMA_CALL_RE = re.compile(r"\[Ollama\s+#(\d+)\]\s+(.+)$")
_LOG_BATCH_RE = re.compile(r"Insertion lot LightRAG\s*\((.+)\)(?:\.\.\.)?\s*$")
_LOG_SUMMARY_STATS_RE = re.compile(r"Résumés de fusion\s*\(([^)]+)\):\s*(.+)$")
_TOKEN_NORM_RE = re.compile(r"[a-z0-9]{3,}")

_FRENCH_STOPWORDS = frozenset(
    {
        "les", "des", "une", "pour", "par", "avec", "dans", "sur", "est", "sont",
        "qui", "que", "aux", "pas", "plus", "sans", "sous", "entre", "vers", "cette",
        "ces", "tout", "tous", "tres", "etre", "avoir", "fait", "donc", "mais",
        "the", "and", "for", "with", "from", "that", "this", "are", "was",
    }
)


def _norm_ascii(text: str) -> str:
    nfd = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in nfd if not unicodedata.combining(ch)).lower()


def _safe_read_json(
    path: Path, retries: int = 3, delay_s: float = 0.15
) -> tuple[Any | None, str | None]:
    """Lit un JSON de maniere resiliente meme pendant une reecriture concurrente."""
    if not path.exists():
        return None, f"Fichier absent: {path.name}"
    last_err: str | None = None
    for attempt in range(max(1, retries)):
        try:
            raw = path.read_text(encoding="utf-8")
            return json.loads(raw), None
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            last_err = f"{path.name}: {type(exc).__name__}: {exc}"
            if attempt + 1 < retries:
                time.sleep(delay_s)
    return None, last_err


def _safe_read_graphml(
    path: Path, retries: int = 3, delay_s: float = 0.2
) -> tuple[nx.Graph | None, str | None]:
    """Charge un fichier GraphML avec reessais en cas de flush simultane."""
    if not path.exists():
        return None, f"Fichier absent: {path.name}"
    last_err: str | None = None
    for attempt in range(max(1, retries)):
        try:
            graph = nx.read_graphml(path)
            return graph, None
        except Exception as exc:
            last_err = f"{path.name}: {type(exc).__name__}: {exc}"
            if attempt + 1 < retries:
                time.sleep(delay_s)
    return None, last_err


_TEST_LOG_MARKERS = (
    "TestRagResilience",
    "test_rag_resilience.py",
    "mistral-small-test",
    "missing:model",
    "[DB: db |",
    "sample.md",
    "DOSSIER_Torse.md",
    "DOSSIER_Bassin.md",
    "gpt-5.6-luna",
    "test_agent_indexing",
)


def _filter_production_log_lines(lines: list[str]) -> list[str]:
    """Exclut les rafales de logs issues de tests unitaires (identifiees par horodatage)."""
    test_timestamps: set[str] = set()
    for line in lines:
        if any(marker in line for marker in _TEST_LOG_MARKERS):
            tm = _LOG_TIME_RE.match(line)
            if tm:
                test_timestamps.add(tm.group(1))
    if not test_timestamps:
        return lines
    filtered: list[str] = []
    for line in lines:
        tm = _LOG_TIME_RE.match(line)
        if tm and tm.group(1) in test_timestamps:
            continue
        if any(marker in line for marker in _TEST_LOG_MARKERS):
            continue
        filtered.append(line)
    return filtered


def _tail_lines(path: Path, max_lines: int = 160, max_bytes: int = 131072) -> list[str]:
    """Lit rapidement les dernieres lignes d'un journal sans charger 15+ Mo."""
    if not path.is_file():
        return []
    try:
        size = path.stat().st_size
        with path.open("rb") as fh:
            if size > max_bytes:
                fh.seek(size - max_bytes)
            chunk = fh.read()
        lines = chunk.decode("utf-8", errors="replace").splitlines()
        if size > max_bytes and lines:
            lines = lines[1:]
        return lines[-max_lines:]
    except OSError:
        return []


def _detect_running_index_pids() -> list[int]:
    """Detecte uniquement les processus python executant index_docs.py (exclut le daemon schedule/sidecar)."""
    try:
        res = subprocess.run(
            ["ps", "-axo", "pid=,command="],
            capture_output=True,
            text=True,
            timeout=1.5,
            check=False,
        )
        if res.returncode != 0 or not res.stdout.strip():
            return []
        self_pid = os.getpid()
        pids: list[int] = []
        for line in res.stdout.splitlines():
            parts = line.strip().split(None, 1)
            if len(parts) < 2 or not parts[0].isdigit():
                continue
            pid_val = int(parts[0])
            cmd_str = parts[1]
            if pid_val == self_pid:
                continue
            if "Code/rag/index_docs.py" not in cmd_str:
                continue
            if "multicall schedule" in cmd_str or "agentapi new-conversation" in cmd_str:
                continue
            first_bin = os.path.basename(cmd_str.split()[0]).lower()
            if not first_bin.startswith("python"):
                continue
            pids.append(pid_val)
        return pids
    except Exception:
        return []


def _probe_ollama_ps(ollama_base: str | None = None) -> list[dict[str, Any]]:
    """Interroge rapidement /api/ps d'Ollama local pour afficher le modele actif en VRAM."""
    base = (ollama_base or os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
    if not base.startswith(("http://127.0.0.1", "http://localhost")):
        return []
    try:
        resp = requests.get(f"{base}/api/ps", timeout=0.8)
        if resp.status_code != 200:
            return []
        payload = resp.json()
        models = []
        for m in payload.get("models") or []:
            vram_bytes = int(m.get("size_vram") or m.get("size") or 0)
            models.append(
                {
                    "name": str(m.get("name") or m.get("model") or ""),
                    "size_vram_gb": round(vram_bytes / (1024 ** 3), 2),
                    "context_length": int(m.get("context_length") or 0),
                    "runner": str(m.get("runner") or ""),
                }
            )
        return models
    except Exception:
        return []


def _read_processing_docs(db_dir: Path) -> list[dict[str, Any]]:
    """Retourne les documents actuellement au statut 'processing' dans doc_status."""
    ds_raw, _ = _safe_read_json(db_dir / "kv_store_doc_status.json", retries=2, delay_s=0.1)
    if not isinstance(ds_raw, dict):
        return []
    now_ts = time.time()
    out: list[dict[str, Any]] = []
    for doc_id, row in ds_raw.items():
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "")).strip().lower() != "processing":
            continue
        meta = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        start_ts = meta.get("process_start_time")
        elapsed_s: float | None = None
        if isinstance(start_ts, (int, float)) and start_ts > 0:
            elapsed_s = round(max(0.0, now_ts - float(start_ts)), 1)
        out.append(
            {
                "doc_id": str(doc_id),
                "file_path": str(row.get("file_path") or doc_id),
                "chunks_count": int(row.get("chunks_count") or len(row.get("chunks_list") or [])),
                "elapsed_s": elapsed_s,
                "track_id": str(row.get("track_id") or ""),
            }
        )
    return out


def detect_live_indexing_status(
    db_path: Path = DEFAULT_DB_PATH,
    log_path: Path = DEFAULT_LOG_PATH,
) -> dict[str, Any]:
    """Inspecte le verrou POSIX, les processus, doc_status, Ollama /api/ps et rag_indexing.log."""
    db_dir = Path(db_path)
    lock_active = is_indexing_lock_active(db_dir)
    pids = _detect_running_index_pids()
    raw_recent_lines = _tail_lines(log_path, max_lines=400, max_bytes=131072)
    recent_lines = _filter_production_log_lines(raw_recent_lines)

    log_age_s: float | None = None
    if log_path.is_file():
        try:
            log_age_s = round(max(0.0, time.time() - log_path.stat().st_mtime), 1)
        except OSError:
            log_age_s = None

    active_engine = ""
    current_progress = ""
    current_chunk_progress = ""
    last_ollama_call = ""
    current_batch = ""
    summary_stats_line = ""
    last_time = ""
    for line in reversed(recent_lines):
        if not last_time:
            tm = _LOG_TIME_RE.match(line)
            if tm:
                last_time = tm.group(1)
        if not active_engine:
            em = _LOG_ENGINE_RE.search(line)
            if em:
                active_engine = em.group(1).strip()
        if not current_progress:
            pm = _LOG_PROGRESS_RE.search(line)
            if pm:
                current_progress = f"[{pm.group(1).strip()}] {pm.group(2).strip()}"
        if not current_chunk_progress:
            cm = _LOG_CHUNK_RE.search(line)
            if cm:
                current_chunk_progress = (
                    f"Chunk {cm.group(1)}/{cm.group(2)} ({cm.group(3)} Ent + {cm.group(4)} Rel)"
                )
        if not last_ollama_call:
            om = _LOG_OLLAMA_CALL_RE.search(line)
            if om:
                last_ollama_call = f"Ollama #{om.group(1)}: {om.group(2).strip()}"
        if not current_batch:
            bm = _LOG_BATCH_RE.search(line)
            if bm:
                current_batch = bm.group(1).strip()
        if not summary_stats_line:
            sm = _LOG_SUMMARY_STATS_RE.search(line)
            if sm:
                summary_stats_line = f"{sm.group(1).strip()}: {sm.group(2).strip()}"
        if (
            active_engine
            and current_progress
            and last_time
            and current_chunk_progress
            and last_ollama_call
            and current_batch
            and summary_stats_line
        ):
            break

    indexing_active = bool(lock_active or pids)
    progress_payload: dict[str, Any] | None = None
    if indexing_active:
        prog_raw, _ = _safe_read_json(db_dir / ".indexing_progress.json", retries=1, delay_s=0.05)
        if isinstance(prog_raw, dict):
            started_ts = float(prog_raw.get("started_at") or time.time())
            elapsed_s = round(max(0.0, time.time() - started_ts), 1)
            total_u = int(prog_raw.get("total_units") or 0)
            done_u = int(prog_raw.get("done_units") or 0)
            total_f = int(prog_raw.get("total_files") or 0)
            prep_f = int(prog_raw.get("prepared_files") or 0)
            pct = (
                round(min(100.0, 100.0 * done_u / total_u), 1)
                if total_u > 0
                else (round(min(100.0, 100.0 * prep_f / total_f), 1) if total_f > 0 else 0.0)
            )
            progress_payload = {
                **prog_raw,
                "elapsed_s": elapsed_s,
                "pct": pct,
            }
            if log_age_s is not None and log_age_s > elapsed_s + 5.0:
                if prog_raw.get("active_engine"):
                    active_engine = str(prog_raw["active_engine"])
                if prog_raw.get("phase") == "prepare" and total_f > 0:
                    cur_f = str(prog_raw.get("current_file") or "")
                    current_progress = f"[{prep_f}/{total_f}] Preparation {cur_f}".strip()
                elif total_u > 0:
                    b_files = list(prog_raw.get("current_batch_files") or [])
                    cur_f = ", ".join(b_files[:2]) + ("..." if len(b_files) > 2 else "")
                    current_progress = f"[{done_u}/{total_u} unites] {cur_f}".strip()

    processing_docs = _read_processing_docs(db_dir) if indexing_active else []
    ollama_ps = _probe_ollama_ps() if indexing_active else []
    return {
        "indexing_active": indexing_active,
        "lock_active": lock_active,
        "active_pids": pids,
        "readonly_enforced": indexing_active,
        "active_engine": active_engine,
        "current_progress": current_progress,
        "current_chunk_progress": current_chunk_progress,
        "last_ollama_call": last_ollama_call,
        "current_batch": current_batch,
        "summary_stats_line": summary_stats_line,
        "progress": progress_payload,
        "processing_docs": processing_docs,
        "ollama_ps": ollama_ps,
        "last_log_time": last_time,
        "log_age_s": log_age_s,
        "recent_log_lines": recent_lines[-20:],
    }


def parse_indexing_log_summary(log_path: Path = DEFAULT_LOG_PATH) -> dict[str, Any]:
    """Resume les statistiques globales de rag_indexing.log en lecture stream."""
    if not log_path.is_file():
        return {
            "exists": False,
            "total_lines": 0,
            "complete_delimiter_warnings": 0,
            "found_pair_warnings": 0,
            "engine_activations": {},
            "recent_warnings": [],
        }

    total_lines = 0
    complete_warn = 0
    found_pair_warn = 0
    engines: Counter[str] = Counter()
    recent_warnings: list[str] = []
    try:
        with log_path.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                total_lines += 1
                if "Complete delimiter" in line:
                    complete_warn += 1
                if "found " in line and "/5" in line:
                    found_pair_warn += 1
                em = _LOG_ENGINE_RE.search(line)
                if em:
                    engines[em.group(1).strip()] += 1
                if "WARNING:" in line or "ERROR:" in line:
                    recent_warnings.append(line.strip())
                    if len(recent_warnings) > 15:
                        recent_warnings.pop(0)
    except OSError:
        pass

    return {
        "exists": True,
        "size_mb": round(log_path.stat().st_size / (1024 * 1024), 2),
        "total_lines": total_lines,
        "complete_delimiter_warnings": complete_warn,
        "found_pair_warnings": found_pair_warn,
        "engine_activations": dict(engines.most_common(12)),
        "recent_warnings": recent_warnings,
    }


def _classify_priority(rel_path: str) -> str:
    name = os.path.basename(rel_path)
    ext = Path(rel_path).suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if name.startswith(CRITICAL_PREFIXES) or ext in PDF_EXTS or ext in SVG_EXTS:
        return "critical"
    return "standard"


def _extract_tech_tokens(text: str) -> set[str]:
    """Extrait valeurs chiffrees avec unite, codes McMaster-Carr et IDs RobStride."""
    tokens: set[str] = set()
    for m in _NUM_UNIT_VALUE_RE.finditer(text or ""):
        tokens.add(m.group(1).replace(",", ".").lower())
    for m in _MCMASTER_RE.finditer(text or ""):
        tokens.add(m.group(0).upper())
    for m in _ROBSTRIDE_RE.finditer(text or ""):
        tokens.add(m.group(0).upper().replace("-", ""))
    return tokens


def _extract_entity_relation_rows(raw_output: str) -> tuple[list[list[str]], list[list[str]]]:
    entities: list[list[str]] = []
    relations: list[list[str]] = []
    body = (raw_output or "").split(COMPLETION_DELIMITER, 1)[0]
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue
        parts = s.split(TUPLE_DELIMITER)
        kind = parts[0].strip().lower()
        if kind == "entity" and len(parts) == 4:
            entities.append([p.strip() for p in parts])
        elif kind == "relation" and len(parts) == 5:
            relations.append([p.strip() for p in parts])
    return entities, relations


def _check_entity_grounding(entity_names: list[str], source_text: str) -> tuple[float, list[str]]:
    """Mesure la proportion d'entites ancrees lexicalement dans le texte source."""
    if not entity_names:
        return 1.0, []
    norm_src = _norm_ascii(source_text)
    src_tokens = set(_TOKEN_NORM_RE.findall(norm_src))
    grounded = 0
    ungrounded: list[str] = []
    for name in entity_names:
        norm_name = _norm_ascii(name)
        if not norm_name:
            continue
        if norm_name in norm_src:
            grounded += 1
            continue
        words = [w for w in _TOKEN_NORM_RE.findall(norm_name) if w not in _FRENCH_STOPWORDS]
        if not words or any(w in src_tokens for w in words):
            grounded += 1
        else:
            ungrounded.append(name)
    total = max(1, len(entity_names))
    return round(grounded / total, 3), ungrounded[:12]


def _resolve_doc_rel_paths(
    ds_map: dict[str, Any],
    fd_map: dict[str, Any],
    idx_map: dict[str, Any],
    docs_root: Path,
    active_rel_set: set[str],
    active_basenames: set[str],
) -> tuple[dict[str, str | None], dict[str, list[str]]]:
    """Resout le rel_path exact pour chaque doc_id et repere les collisions/doublons."""
    doc_id_to_idx_rel: dict[str, str] = {}
    for abs_p, entry in idx_map.items():
        if not isinstance(entry, dict):
            continue
        did = entry.get("doc_id")
        if not did:
            continue
        try:
            rel = str(Path(abs_p).resolve().relative_to(docs_root.resolve()))
        except Exception:
            rel = abs_p
        doc_id_to_idx_rel[did] = rel

    flat_to_rel: dict[str, str] = {}
    base_to_unique_rel: dict[str, str] = {}
    base_counts: Counter[str] = Counter()
    for rel in active_rel_set:
        flat = rel.replace("/", "--") if "/" in rel else f"root--{rel}"
        flat_to_rel[flat] = rel
        b = os.path.basename(rel)
        base_counts[b] += 1
        base_to_unique_rel[b] = rel

    resolved_rels: dict[str, str | None] = {}
    rel_to_doc_ids: dict[str, list[str]] = defaultdict(list)

    for d_id, d_data in ds_map.items():
        if not isinstance(d_data, dict):
            continue
        rel = _rel_path_from_doc_entry(d_id, d_data, fd_map, docs_root)
        if not rel and d_id in doc_id_to_idx_rel:
            rel = doc_id_to_idx_rel[d_id]
        if not rel:
            fp = str(d_data.get("file_path", "") or "").strip()
            canon = canonical_source_name(fp)
            if fp in flat_to_rel:
                rel = flat_to_rel[fp]
            elif canon in flat_to_rel:
                rel = flat_to_rel[canon]
            elif canon in active_basenames and base_counts.get(canon, 0) == 1:
                rel = base_to_unique_rel[canon]
        resolved_rels[d_id] = rel
        if rel:
            rel_to_doc_ids[rel].append(d_id)

    return resolved_rels, dict(rel_to_doc_ids)


def _partition_doc_ids_for_rel(
    cand_ids: list[str],
    idx_entry: dict[str, Any] | None,
    ds_map: dict[str, Any],
    fd_map: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Separe les doc_id actifs (monolithique ou sections virtuelles) des vrais doublons."""
    if isinstance(idx_entry, dict) and isinstance(idx_entry.get("sections"), dict) and idx_entry["sections"]:
        expected_ids = [
            str(sec["doc_id"])
            for sec in idx_entry["sections"].values()
            if isinstance(sec, dict) and sec.get("doc_id")
        ]
        present_expected = [did for did in expected_ids if did in ds_map]
        if present_expected:
            active_set = set(present_expected)
            dup_ids = [did for did in cand_ids if did not in active_set]
            return present_expected, dup_ids

    sec_pairs: list[tuple[str, str | None]] = []
    for did in cand_ids:
        fd_entry = fd_map.get(did)
        sk = extract_section_key(fd_entry.get("content", "")) if isinstance(fd_entry, dict) else None
        sec_pairs.append((did, sk))

    sectioned = [(did, sk) for did, sk in sec_pairs if sk is not None]
    if sectioned:
        best_by_sec: dict[str, str] = {}
        by_sec: dict[str, list[str]] = defaultdict(list)
        for did, sk in sectioned:
            by_sec[str(sk)].append(did)
        active_ids: list[str] = []
        active_set: set[str] = set()
        for sk, dids in by_sec.items():
            dids_sorted = sorted(
                dids,
                key=lambda d: str((ds_map.get(d) or {}).get("updated_at", "")),
                reverse=True,
            )
            best_by_sec[sk] = dids_sorted[0]
            active_ids.append(dids_sorted[0])
            active_set.add(dids_sorted[0])
        dup_ids = [did for did in cand_ids if did not in active_set]
        return active_ids, dup_ids

    primary_id: str | None = None
    if idx_entry and idx_entry.get("doc_id") in ds_map:
        primary_id = str(idx_entry["doc_id"])
    elif cand_ids:
        sorted_cands = sorted(
            cand_ids,
            key=lambda d: str((ds_map.get(d) or {}).get("updated_at", "")),
            reverse=True,
        )
        primary_id = sorted_cands[0]
    dup_ids = [did for did in cand_ids if did != primary_id]
    return ([primary_id] if primary_id else []), dup_ids


def _dir_size_and_mtime(target_dir: Path) -> tuple[float, float | None]:
    """Calcule la taille totale en Mo et le mtime max des stores KV d'une base."""
    if not target_dir.is_dir():
        return 0.0, None
    total_bytes = 0
    max_mt: float | None = None
    try:
        for item in target_dir.iterdir():
            if not item.is_file():
                continue
            try:
                st = item.stat()
                total_bytes += st.st_size
                if item.name.startswith("kv_store_") and (max_mt is None or st.st_mtime > max_mt):
                    max_mt = st.st_mtime
            except OSError:
                continue
    except OSError:
        return 0.0, None
    return round(total_bytes / (1024.0 * 1024.0), 1), max_mt


def _compute_storage_info(db_dir: Path) -> dict[str, Any]:
    """Retourne les informations SSD local vs miroir Google Drive en lecture seule."""
    db_size_mb, db_max_mt = _dir_size_and_mtime(db_dir)
    mirror_dir = Path(DEFAULT_DRIVE_MIRROR_DB_PATH)
    mirror_exists = mirror_dir.is_dir()
    mirror_size_mb, mirror_max_mt = _dir_size_and_mtime(mirror_dir) if mirror_exists else (0.0, None)
    try:
        is_local_ssd = db_dir.resolve() == Path(DEFAULT_LOCAL_DB_PATH).resolve()
    except OSError:
        is_local_ssd = False
    delta_s: float | None = None
    if db_max_mt is not None and mirror_max_mt is not None:
        delta_s = round(db_max_mt - mirror_max_mt, 1)
    return {
        "db_path": str(db_dir),
        "is_local_ssd": is_local_ssd,
        "db_size_mb": db_size_mb,
        "mirror_path": str(mirror_dir),
        "mirror_exists": mirror_exists,
        "mirror_size_mb": mirror_size_mb,
        "mirror_delta_s": delta_s,
    }


def _score_document(
    *,
    rel_path: str,
    abs_path: Path | None,
    doc_id: str | None,
    d_data: dict[str, Any] | None,
    fd_entry: dict[str, Any] | None,
    idx_entry: dict[str, Any] | None,
    duplicate_ids: list[str],
    fe_map: dict[str, Any],
    fr_map: dict[str, Any],
    tc_map: dict[str, Any],
    cache_map: dict[str, Any],
    vdb_chunk_ids: set[str],
    docs_root: Path,
    section_doc_ids: list[str] | None = None,
    ds_map: dict[str, Any] | None = None,
    fd_map: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evalue un document selon les 6 dimensions qualite sans aucun appel LLM."""
    priority = _classify_priority(rel_path)
    reasons: list[str] = []
    warnings_detail: list[str] = []

    eff_doc_ids = [d for d in (section_doc_ids or ([doc_id] if doc_id else [])) if d]
    disk_exists = abs_path is not None and abs_path.is_file()
    disk_mtime = abs_path.stat().st_mtime if disk_exists and abs_path else None
    disk_size_kb = round(abs_path.stat().st_size / 1024.0, 2) if disk_exists and abs_path else 0.0

    # Cas fichier present sur disque mais absent de la base
    gleaning_mode = os.environ.get("RAG_GLEANING_MODE", "adaptive")
    gleaning_policy = resolve_gleaning_for_doc(rel_path, gleaning_mode)
    if not doc_id or not isinstance(d_data, dict):
        reasons.append("NOT_INDEXED")
        return {
            "rel_path": rel_path,
            "file_name": os.path.basename(rel_path),
            "folder": str(Path(rel_path).parent) if "/" in rel_path else ".",
            "priority": priority,
            "gleaning_policy": gleaning_policy,
            "doc_id": None,
            "sections_count": 0,
            "section_doc_ids": [],
            "duplicate_doc_ids": duplicate_ids,
            "status_db": "absent",
            "health_status": "critical",
            "score": 0,
            "disk_size_kb": disk_size_kb,
            "chunk_opts": "",
            "chunks_count": 0,
            "vdb_chunks_present": 0,
            "tokens_total": 0,
            "entities_count": 0,
            "relations_count": 0,
            "entities_per_1k_tok": 0.0,
            "relations_per_1k_tok": 0.0,
            "metric_retention": None,
            "grounding_rate": None,
            "syntax_errors_pass1": 0,
            "missing_complete_count": 0,
            "empty_gleaning_rate": 0.0,
            "updated_at": "",
            "reasons": reasons,
            "warnings": ["Document present sur disque mais absent de kv_store_doc_status.json."],
            "recommended_action": _recommend_action(rel_path, priority, reasons),
            "subscores": {
                "sync_chunking": 0,
                "graph_density": 0,
                "syntax_integrity": 0,
                "metric_retention": 0,
                "hygiene_grounding": 0,
            },
        }

    if len(eff_doc_ids) > 1 and ds_map is not None:
        sec_statuses = [str((ds_map.get(d) or {}).get("status", "unknown")).lower() for d in eff_doc_ids]
        if all(st == "processed" for st in sec_statuses):
            status_db = "processed"
        elif any(st == "processing" for st in sec_statuses):
            status_db = "processing"
        else:
            status_db = next((st for st in sec_statuses if st != "processed"), "unknown")
        chunk_ids_seen: set[str] = set()
        chunk_ids: list[str] = []
        for did in eff_doc_ids:
            for cid in ((ds_map.get(did) or {}).get("chunks_list") or []):
                if cid not in chunk_ids_seen:
                    chunk_ids_seen.add(cid)
                    chunk_ids.append(cid)
    else:
        status_db = str(d_data.get("status", "unknown")).lower()
        chunk_ids = list(d_data.get("chunks_list") or [])

    meta = d_data.get("metadata") if isinstance(d_data.get("metadata"), dict) else {}
    chunk_opts = str(meta.get("chunk_opts") or "")
    chunks_count = len(chunk_ids)
    updated_at = str(d_data.get("updated_at") or d_data.get("created_at") or "")

    # 1. Synchronisation & Chunking (0 - 20 pts)
    sync_pts = 0
    if status_db == "processed":
        sync_pts += 8
    elif status_db == "processing":
        reasons.append("STUCK_PROCESSING")
        warnings_detail.append("Document bloque au statut 'processing'.")
    else:
        reasons.append(f"STATUS_{status_db.upper()}")

    stale_mtime = False
    if idx_entry and disk_mtime is not None:
        if float(idx_entry.get("mtime", 0)) + 1.0 < disk_mtime:
            sha_matches = False
            stored_sha = idx_entry.get("content_sha256")
            if stored_sha and abs_path is not None and abs_path.suffix.lower() in (".md", ".py", ".txt"):
                try:
                    cur_sha = compute_normalized_sha256(
                        abs_path.read_text(encoding="utf-8"), ext=abs_path.suffix.lower()
                    )
                    sha_matches = cur_sha == stored_sha
                except OSError:
                    sha_matches = False
            if sha_matches:
                sync_pts += 6
            else:
                stale_mtime = True
                reasons.append("STALE_MTIME")
                warnings_detail.append("Fichier modifie sur disque apres la derniere entree indexed_files.json.")
        elif idx_entry.get("doc_id") and idx_entry.get("doc_id") not in eff_doc_ids:
            reasons.append("INDEX_LOG_MISMATCH")
            warnings_detail.append("doc_id de indexed_files.json different de doc_status.")
        else:
            sync_pts += 6
    elif disk_exists:
        reasons.append("UNTRACKED_IN_INDEX_LOG")
        warnings_detail.append("Absent de indexed_files.json (suivi incremental incomplet).")
        sync_pts += 2

    vdb_present = sum(1 for cid in chunk_ids if cid in vdb_chunk_ids)
    if chunks_count > 0 and vdb_present == chunks_count:
        sync_pts += 3
    elif chunks_count > 0:
        reasons.append("MISSING_VDB_CHUNKS")
        warnings_detail.append(f"Chunks absents de vdb_chunks.json ({vdb_present}/{chunks_count}).")

    if "1600" in chunk_opts:
        sync_pts += 3
    elif chunk_opts:
        reasons.append("LEGACY_1200_100")
        sync_pts += 0
    else:
        sync_pts += 1

    if duplicate_ids:
        reasons.append("DUPLICATE_DOC_IDS")
        warnings_detail.append(f"{len(duplicate_ids)} ancienne(s) entree(s) doc_id coexistent pour ce fichier.")

    # 2. Densite graphe & entites/relations (0 - 25 pts)
    if len(eff_doc_ids) > 1:
        entity_names_seen: set[str] = set()
        entity_names: list[str] = []
        relation_pairs_seen: set[tuple[str, str]] = set()
        relation_pairs: list[list[str]] = []
        for did in eff_doc_ids:
            fe_e = fe_map.get(did) if isinstance(fe_map.get(did), dict) else {}
            for en in fe_e.get("entity_names") or []:
                if en not in entity_names_seen:
                    entity_names_seen.add(en)
                    entity_names.append(en)
            fr_e = fr_map.get(did) if isinstance(fr_map.get(did), dict) else {}
            for rp in fr_e.get("relation_pairs") or []:
                if isinstance(rp, (list, tuple)) and len(rp) >= 2:
                    key_rp = (str(rp[0]), str(rp[1]))
                    if key_rp not in relation_pairs_seen:
                        relation_pairs_seen.add(key_rp)
                        relation_pairs.append([key_rp[0], key_rp[1]])
        entities_count = len(entity_names)
        relations_count = len(relation_pairs)
    else:
        fe_entry = fe_map.get(doc_id) if isinstance(fe_map.get(doc_id), dict) else {}
        fr_entry = fr_map.get(doc_id) if isinstance(fr_map.get(doc_id), dict) else {}
        entity_names = list(fe_entry.get("entity_names") or [])
        relation_pairs = list(fr_entry.get("relation_pairs") or [])
        entities_count = int(fe_entry.get("count", len(entity_names)) or 0)
        relations_count = int(fr_entry.get("count", len(relation_pairs)) or 0)

    tokens_total = 0
    source_parts: list[str] = []
    for cid in chunk_ids:
        tc_row = tc_map.get(cid)
        if isinstance(tc_row, dict):
            tokens_total += int(tc_row.get("tokens") or 0)
            source_parts.append(str(tc_row.get("content") or ""))

    if not source_parts and isinstance(fd_entry, dict):
        full_txt = str(fd_entry.get("content") or "")
        source_parts.append(full_txt)
        if tokens_total == 0:
            tokens_total = max(1, len(full_txt) // 4)

    source_text = "\n".join(source_parts)
    k_tok = max(0.25, tokens_total / 1000.0)
    ent_per_1k = round(entities_count / k_tok, 2)
    rel_per_1k = round(relations_count / k_tok, 2)

    density_pts = 25
    if entities_count == 0:
        density_pts = 0
        reasons.append("ZERO_ENTITIES")
    elif relations_count == 0 and tokens_total >= 200:
        density_pts = 4
        reasons.append("ZERO_RELATIONS")
    elif priority != "image" and tokens_total >= 450:
        min_rel_rate = 5.0 if priority == "critical" else 3.5
        if rel_per_1k < min_rel_rate:
            ratio = rel_per_1k / min_rel_rate
            density_pts = max(5, round(25 * ratio))
            reasons.append("LOW_REL_DENSITY")
            warnings_detail.append(
                f"Faible densite de relations ({rel_per_1k}/1k tok vs cible >= {min_rel_rate})."
            )
        elif ent_per_1k < 4.5:
            density_pts = 16
            reasons.append("LOW_ENT_DENSITY")

    # 3. Inspection syntaxique & gleaning dans kv_store_llm_response_cache.json (0 - 20 pts)
    syntax_errors_pass1 = 0
    missing_complete = 0
    broken_delims = 0
    gleaning_total = 0
    gleaning_empty = 0
    cache_text_parts: list[str] = []
    cache_entries_found = 0

    for cid in chunk_ids:
        tc_row = tc_map.get(cid)
        if not isinstance(tc_row, dict):
            continue
        cache_keys = list(tc_row.get("llm_cache_list") or [])
        extract_entries: list[dict[str, Any]] = []
        for ck in cache_keys:
            c_obj = cache_map.get(ck)
            if isinstance(c_obj, dict) and c_obj.get("cache_type", "extract") == "extract":
                extract_entries.append(c_obj)
        for pos, c_obj in enumerate(extract_entries):
            cache_entries_found += 1
            ret = str(c_obj.get("return") or "")
            cache_text_parts.append(ret)
            if COMPLETION_DELIMITER not in ret:
                missing_complete += 1
            if "<|#||>" in ret:
                broken_delims += 1
            if pos == 0:
                errs = validate_single_extraction(ret, label=cid)
                if errs:
                    syntax_errors_pass1 += len(errs)
            else:
                gleaning_total += 1
                stripped_g = ret.replace(COMPLETION_DELIMITER, "").strip()
                if len(stripped_g) < 40 or stripped_g.upper() == "NONE":
                    gleaning_empty += 1

    empty_gleaning_rate = round(gleaning_empty / gleaning_total, 2) if gleaning_total > 0 else 0.0
    syntax_pts = 20
    if chunks_count > 0 and cache_entries_found == 0:
        syntax_pts = 10
        reasons.append("NO_CACHE_TRACE")
    else:
        if syntax_errors_pass1 > 0:
            syntax_pts -= min(12, syntax_errors_pass1 * 3)
            reasons.append("SYNTAX_ERRORS_EXTRACT")
        if missing_complete > 0:
            syntax_pts -= min(8, missing_complete * 2)
            reasons.append("MISSING_COMPLETE_TAG")
        if broken_delims > 0:
            syntax_pts -= min(6, broken_delims * 3)
            reasons.append("BROKEN_DELIMITERS")
        if gleaning_total >= 3 and empty_gleaning_rate >= 0.75 and priority == "critical":
            syntax_pts -= 4
            reasons.append("EMPTY_GLEANING_HIGH")
    syntax_pts = max(0, syntax_pts)

    # 4. Retention des valeurs chiffrees et references McMaster/RobStride (0 - 20 pts)
    src_metrics = _extract_tech_tokens(source_text)
    extracted_blob = "\n".join(cache_text_parts) + "\n" + " ".join(entity_names)
    metric_retention: float | None = None
    metric_pts = 20
    if len(src_metrics) >= 5 and priority != "image":
        ext_norm = extracted_blob.upper().replace(",", ".").replace("-", "")
        kept = sum(1 for tok in src_metrics if tok.upper().replace("-", "") in ext_norm)
        metric_retention = round(kept / len(src_metrics), 3)
        if metric_retention < 0.35:
            metric_pts = max(2, round(20 * (metric_retention / 0.55)))
            reasons.append("LOW_METRIC_RETENTION")
            warnings_detail.append(
                f"Retention faible des cotes/references ({kept}/{len(src_metrics)}, {metric_retention*100:.0f} %)."
            )
        elif metric_retention < 0.55:
            metric_pts = 14

    # 5. Hygiene lexicale & ancrage reel dans le document source (0 - 15 pts)
    grounding_rate, ungrounded_samples = _check_entity_grounding(entity_names, source_text)
    hygiene_pts = 15
    if entity_names and grounding_rate < 0.65:
        hygiene_pts -= 10
        reasons.append("UNGROUNDED_ENTITIES")
        warnings_detail.append(
            f"Entites non retrouvees dans le texte source ({grounding_rate*100:.0f} % ancrees) : {', '.join(ungrounded_samples[:5])}"
        )
    elif entity_names and grounding_rate < 0.80:
        hygiene_pts -= 4

    unknown_count = sum(1 for e in entity_names if "unknown" in e.lower())
    camel_artifacts = sum(1 for e in entity_names if _CAMEL_SPLIT_ARTIFACT_RE.search(e))
    latex_or_dollar = sum(
        1 for txt in cache_text_parts if _DOLLAR_CHAR in txt or _LATEX_ARTIFACT_RE.search(txt)
    )
    if unknown_count > 0:
        hygiene_pts -= min(5, unknown_count * 2)
        reasons.append("UNKNOWN_ENTITIES")
    if camel_artifacts >= 3:
        hygiene_pts -= 3
        reasons.append("CAMELCASE_ARTIFACTS")
    if latex_or_dollar > 0:
        hygiene_pts -= 3
        reasons.append("DOLLAR_OR_LATEX_ARTIFACT")
    hygiene_pts = max(0, hygiene_pts)

    score = max(0, min(100, sync_pts + density_pts + syntax_pts + metric_pts + hygiene_pts))

    if (
        status_db != "processed"
        or entities_count == 0
        or (relations_count == 0 and tokens_total >= 250)
        or grounding_rate < 0.60
        or score < 50
    ):
        health_status = "critical"
    elif (
        score < 75
        or stale_mtime
        or ("LEGACY_1200_100" in reasons and priority == "critical")
        or bool(duplicate_ids)
    ):
        health_status = "warning"
    else:
        health_status = "healthy"

    if len(eff_doc_ids) > 1:
        sections_count = len(eff_doc_ids)
    elif isinstance(fd_entry, dict) and extract_section_key(fd_entry.get("content", "")) is not None:
        sections_count = 1
    else:
        sections_count = 0

    return {
        "rel_path": rel_path,
        "file_name": os.path.basename(rel_path),
        "folder": str(Path(rel_path).parent) if "/" in rel_path else ".",
        "priority": priority,
        "gleaning_policy": gleaning_policy,
        "doc_id": doc_id,
        "sections_count": sections_count,
        "section_doc_ids": eff_doc_ids,
        "duplicate_doc_ids": duplicate_ids,
        "status_db": status_db,
        "health_status": health_status,
        "score": score,
        "disk_size_kb": disk_size_kb,
        "chunk_opts": chunk_opts or "inconnu",
        "chunks_count": chunks_count,
        "vdb_chunks_present": vdb_present,
        "tokens_total": tokens_total,
        "entities_count": entities_count,
        "relations_count": relations_count,
        "entities_per_1k_tok": ent_per_1k,
        "relations_per_1k_tok": rel_per_1k,
        "metric_retention": metric_retention,
        "grounding_rate": grounding_rate,
        "ungrounded_samples": ungrounded_samples,
        "syntax_errors_pass1": syntax_errors_pass1,
        "missing_complete_count": missing_complete,
        "empty_gleaning_rate": empty_gleaning_rate,
        "updated_at": updated_at,
        "reasons": reasons,
        "warnings": warnings_detail,
        "recommended_action": _recommend_action(rel_path, priority, reasons),
        "subscores": {
            "sync_chunking": sync_pts,
            "graph_density": density_pts,
            "syntax_integrity": syntax_pts,
            "metric_retention": metric_pts,
            "hygiene_grounding": hygiene_pts,
        },
    }


def _recommend_action(rel_path: str, priority: str, reasons: list[str]) -> str:
    if not reasons:
        return "Aucune action requise"
    if "NOT_INDEXED" in reasons or "STALE_MTIME" in reasons:
        engine = "--provider ollama" if priority == "critical" else "--provider auto"
        return f'index_docs.py {engine} --files "{rel_path}"'
    if any(
        r in reasons
        for r in (
            "ZERO_ENTITIES",
            "ZERO_RELATIONS",
            "UNGROUNDED_ENTITIES",
            "LOW_REL_DENSITY",
            "LOW_METRIC_RETENTION",
            "LEGACY_1200_100",
            "STUCK_PROCESSING",
            "SYNTAX_ERRORS_EXTRACT",
        )
    ):
        return f'index_docs.py --provider ollama --files "{rel_path}"'
    if "DUPLICATE_DOC_IDS" in reasons or "MISSING_VDB_CHUNKS" in reasons:
        return "repair_db_sync.py --apply ou re-indexation unitaire"
    return f'index_docs.py --provider auto --files "{rel_path}"'


def _audit_graph_health(
    graph: nx.Graph | None,
    tc_ids: set[str],
    vdb_chunk_ids: set[str],
    vdb_ent_count: int,
    vdb_rel_count: int,
) -> dict[str, Any]:
    if graph is None:
        return {
            "available": False,
            "nodes": 0,
            "edges": 0,
            "degree_zero_nodes": 0,
            "connected_components": 0,
            "orphan_graph_nodes": 0,
            "potential_duplicate_clusters": [],
            "top_hubs": [],
            "vdb_chunks_count": len(vdb_chunk_ids),
            "text_chunks_count": len(tc_ids),
            "vdb_entities_count": vdb_ent_count,
            "vdb_relationships_count": vdb_rel_count,
        }

    valid_chunks = tc_ids & vdb_chunk_ids
    deg_zero: list[str] = []
    orphan_nodes = 0
    norm_groups: dict[str, list[str]] = defaultdict(list)

    for node_id, attrs in graph.nodes(data=True):
        deg = graph.degree(node_id)
        if deg == 0:
            deg_zero.append(str(node_id))
        src_ids = [c for c in str(attrs.get("source_id", "")).split("<SEP>") if c]
        if valid_chunks and src_ids and not any(c in valid_chunks for c in src_ids):
            orphan_nodes += 1
        norm_key = re.sub(r"[^a-z0-9]", "", _norm_ascii(str(node_id)))
        if len(norm_key) >= 4:
            norm_groups[norm_key].append(str(node_id))

    dup_clusters = [
        {"key": k, "variants": sorted(set(v))}
        for k, v in norm_groups.items()
        if len(set(v)) >= 2
    ]
    dup_clusters.sort(key=lambda item: len(item["variants"]), reverse=True)

    top_hubs = [
        {
            "id": str(nid),
            "degree": int(deg),
            "entity_type": str(graph.nodes[nid].get("entity_type", "")),
        }
        for nid, deg in sorted(graph.degree(), key=lambda x: x[1], reverse=True)[:20]
    ]

    try:
        comp_count = nx.number_connected_components(graph.to_undirected())
    except Exception:
        comp_count = 0

    return {
        "available": True,
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "degree_zero_nodes": len(deg_zero),
        "degree_zero_samples": deg_zero[:25],
        "connected_components": comp_count,
        "orphan_graph_nodes": orphan_nodes,
        "potential_duplicate_clusters": dup_clusters[:30],
        "top_hubs": top_hubs,
        "vdb_chunks_count": len(vdb_chunk_ids),
        "text_chunks_count": len(tc_ids),
        "chunks_only_in_kv": len(tc_ids - vdb_chunk_ids),
        "chunks_only_in_vdb": len(vdb_chunk_ids - tc_ids),
        "vdb_entities_count": vdb_ent_count,
        "vdb_relationships_count": vdb_rel_count,
    }


def _extract_vdb_summary(path: Path) -> tuple[set[str], int, str | None]:
    raw, err = _safe_read_json(path)
    if not isinstance(raw, dict):
        return set(), 0, err
    rows = raw.get("data") or []
    ids = {str(r.get("__id__")) for r in rows if isinstance(r, dict) and r.get("__id__")}
    return ids, len(rows), None


def _normalize_cad_text(text: str) -> str:
    """Normalise accents, separateurs de milliers et virgules decimales pour le controle CAO."""
    cleaned = _norm_ascii(text or "").replace("\u00a0", " ").replace("\u202f", " ")
    cleaned = cleaned.replace("`", "").replace("*", "")
    cleaned = re.sub(r"(\d),(\d)", r"\1.\2", cleaned)
    for _ in range(2):
        cleaned = re.sub(r"(?<=\d)\s+(?=\d{3}\b)", "", cleaned)
    return cleaned


def _compute_file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def _extract_cad_reference_snapshot(cad_data: dict[str, Any]) -> dict[str, Any]:
    """Extrait les grandeurs de reference depuis AUDIT_METROLOGIQUE_Torse_et_Bassin.json."""
    meta = cad_data.get("metadata") if isinstance(cad_data.get("metadata"), dict) else {}
    summary = (
        cad_data.get("assembly_summary")
        if isinstance(cad_data.get("assembly_summary"), dict)
        else {}
    )
    components = [c for c in (cad_data.get("components") or []) if isinstance(c, dict)]
    hardware_bom = (
        cad_data.get("hardware_bom")
        if isinstance(cad_data.get("hardware_bom"), dict)
        else {}
    )

    doc_name = str(meta.get("document_name") or "Inconnu")
    ver_match = _TORSE_VER_RE.search(doc_name)
    cad_version_num = int(ver_match.group(1)) if ver_match else None

    total_mass_g = float(summary.get("total_mass_g") or 0.0)
    phys_bbox = summary.get("physical_components_bounding_box_mm") or summary.get("bounding_box_mm") or {}
    phys_size = list(phys_bbox.get("size") or [])
    com_mm = list(summary.get("center_of_mass_mm") or [])

    key_parts: list[dict[str, Any]] = []
    for label, aliases in _CAD_KEY_PARTS:
        aliases_norm = tuple(_norm_ascii(a) for a in aliases)
        matches: list[dict[str, Any]] = []
        for comp in components:
            if comp.get("is_container"):
                continue
            iname = str(comp.get("instance_name") or "")
            cname = str(comp.get("component_name") or "")
            full_norm = _norm_ascii(f"{iname} {cname}")
            if label == "RB8016" and "bride" in full_norm:
                continue
            if any(al in full_norm for al in aliases_norm):
                matches.append(comp)
        if matches:
            unit_mass = float(matches[0].get("mass_g") or 0.0)
            qty = len(matches)
            key_parts.append(
                {
                    "label": label,
                    "aliases_norm": aliases_norm,
                    "unit_mass_g": round(unit_mass, 2),
                    "total_mass_g": round(sum(float(m.get("mass_g") or 0.0) for m in matches), 2),
                    "quantity": qty,
                }
            )

    mcm_details: dict[str, dict[str, Any]] = {}
    for key, entry in hardware_bom.items():
        if not isinstance(entry, dict):
            continue
        blob = " ".join(
            [
                str(key),
                str(entry.get("component_name") or ""),
                str(entry.get("part_number") or ""),
                str(entry.get("description") or ""),
            ]
        )
        for m in _MCMASTER_RE.findall(blob):
            ref = m.upper()
            mcm_details[ref] = {
                "ref": ref,
                "component_name": str(entry.get("component_name") or key),
                "description": str(entry.get("description") or ""),
                "quantity": int(entry.get("quantity") or 1),
            }

    if not mcm_details:
        raw_blob = json.dumps(cad_data, ensure_ascii=False)
        for m in _MCMASTER_RE.findall(raw_blob):
            ref = m.upper()
            if ref not in mcm_details:
                mcm_details[ref] = {
                    "ref": ref,
                    "component_name": ref,
                    "description": "",
                    "quantity": 1,
                }

    return {
        "document_name": doc_name,
        "cad_version_num": cad_version_num,
        "timestamp": str(meta.get("timestamp") or ""),
        "total_mass_g": round(total_mass_g, 2),
        "total_mass_kg": round(total_mass_g / 1000.0, 2),
        "instances_count": len(components),
        "unique_bom_count": len(hardware_bom),
        "physical_size_mm": phys_size,
        "center_of_mass_mm": com_mm,
        "key_parts": key_parts,
        "mcmaster_refs": mcm_details,
    }


def _check_doc_against_cad(
    rel_path: str,
    abs_path: Path,
    cad_snap: dict[str, Any],
) -> dict[str, Any]:
    """Compare un document Markdown technique aux grandeurs extraites du JSON CAO."""
    raw_text = abs_path.read_text(encoding="utf-8", errors="replace")
    norm_text = _normalize_cad_text(raw_text)
    lines = norm_text.splitlines()

    cad_ver = cad_snap.get("cad_version_num")
    total_g = float(cad_snap.get("total_mass_g") or 0.0)
    total_kg = float(cad_snap.get("total_mass_kg") or 0.0)

    versions_found = sorted({int(v) for v in _TORSE_VER_RE.findall(norm_text)})
    issues: list[dict[str, str]] = []

    if cad_ver is not None and versions_found and max(versions_found) < cad_ver:
        issues.append(
            {
                "code": "CAD_VERSION_DRIFT",
                "severity": "warning",
                "message": (
                    f"Version CAO mentionnee Torse-123 v{max(versions_found)} "
                    f"(vs {cad_snap['document_name']} dans le JSON CAO)."
                ),
            }
        )

    total_mass_mentioned = False
    has_current_total = False
    old_total_candidates: list[float] = []
    for line in lines:
        if any(
            kw in line
            for kw in (
                "masse totale",
                "total haut du corps",
                "masse cao",
                "masse brute",
                "torse + bassin",
            )
        ):
            total_mass_mentioned = True
            for m in _MASS_G_RE.findall(line):
                val = float(m)
                if 12000.0 <= val <= 28000.0:
                    if abs(val - total_g) <= 2.0:
                        has_current_total = True
                    else:
                        old_total_candidates.append(val)
            for m in _MASS_KG_RE.findall(line):
                val_kg = float(m)
                if 12.0 <= val_kg <= 28.0:
                    if abs(val_kg - total_kg) <= 0.02:
                        has_current_total = True
                    elif abs(val_kg - total_kg) > 0.03:
                        old_total_candidates.append(round(val_kg * 1000.0, 2))

    if total_mass_mentioned and old_total_candidates and not has_current_total and total_g > 0:
        issues.append(
            {
                "code": "PART_MASS_DRIFT",
                "severity": "warning",
                "message": (
                    f"Masse totale CAO obsolete ({old_total_candidates[0]:.2f} g "
                    f"vs {total_g:.2f} g / {total_kg:.2f} kg dans {cad_snap['document_name']})."
                ),
            }
        )

    checked_parts = 0
    drifted_parts = 0
    for part in cad_snap.get("key_parts") or []:
        aliases = part["aliases_norm"]
        unit_g = float(part["unit_mass_g"])
        qty_mass_g = float(part["total_mass_g"])
        if unit_g <= 0:
            continue
        matching_lines = [ln for ln in lines if any(al in ln for al in aliases)]
        if not matching_lines:
            continue

        line_masses: list[float] = []
        for ln in matching_lines:
            is_table_row = ln.lstrip().startswith("|")
            other_aliases_in_ln = any(
                other["label"] != part["label"]
                and any(oa in ln for oa in other["aliases_norm"])
                for other in cad_snap.get("key_parts") or []
            )
            if is_table_row and not other_aliases_in_ln:
                search_slices = [ln]
            else:
                search_slices = []
                for al in aliases:
                    start = 0
                    while True:
                        pos = ln.find(al, start)
                        if pos < 0:
                            break
                        search_slices.append(ln[pos : pos + 140])
                        start = pos + len(al)
            for sl in search_slices:
                for m in _MASS_G_RE.findall(sl):
                    val = float(m)
                    if (0.5 * unit_g) <= val <= (1.5 * max(unit_g, qty_mass_g)):
                        line_masses.append(val)
        if not line_masses:
            continue

        checked_parts += 1
        has_match = any(
            abs(v - unit_g) <= 0.5 or abs(v - qty_mass_g) <= 0.8 for v in line_masses
        )
        if not has_match:
            drifted_parts += 1
            issues.append(
                {
                    "code": "PART_MASS_DRIFT",
                    "severity": "warning",
                    "message": (
                        f"Masse piece '{part['label']}' divergente : "
                        f"{line_masses[0]:.2f} g citee vs {unit_g:.2f} g en CAO ({cad_snap['document_name']})."
                    ),
                }
            )

    return {
        "rel_path": rel_path,
        "exists": True,
        "status": "drift" if issues else "aligned",
        "versions_found": [f"v{v}" for v in versions_found],
        "checked_parts": checked_parts,
        "drifted_parts": drifted_parts,
        "issues": issues,
    }


def _check_svg_and_snapshot_freshness(
    docs_dir: Path,
    cad_mtime: float,
    exports_root: Path | None,
) -> dict[str, Any]:
    """Controle la fraicheur temporelle des SVG media/ et des snapshots PNG face au JSON CAO."""
    svg_dir = docs_dir / TORSE_MEDIA_REL
    svg_files = sorted(svg_dir.glob("*.svg")) if svg_dir.is_dir() else []

    eff_exports = (
        Path(exports_root)
        if exports_root is not None
        else (docs_dir.resolve().parent / "Exports_CAO_DBot")
    )
    snapshots_dir = eff_exports / "01_Torse_et_Bassin" / "Visual_Snapshots"
    exports_available = eff_exports.is_dir()
    newest_png_mtime: float | None = None
    newest_png_name: str | None = None
    if snapshots_dir.is_dir():
        pngs = list(snapshots_dir.rglob("*.png"))
        if pngs:
            newest_png = max(pngs, key=lambda p: p.stat().st_mtime)
            newest_png_mtime = newest_png.stat().st_mtime
            newest_png_name = newest_png.name

    older_than_cad: list[dict[str, Any]] = []
    for svg in svg_files:
        smtime = svg.stat().st_mtime
        if smtime + 60.0 < cad_mtime:
            lag_h = round((cad_mtime - smtime) / 3600.0, 1)
            older_than_cad.append(
                {
                    "file_name": svg.name,
                    "svg_mtime_iso": datetime.fromtimestamp(smtime, tz=timezone.utc).isoformat(),
                    "lag_hours": lag_h,
                }
            )
    older_than_cad.sort(key=lambda item: item["lag_hours"], reverse=True)

    stale_manifest_pngs: list[dict[str, str]] = []
    manifest_path = Path(__file__).resolve().parent.parent / "scripts/cad_tools/snapshot_sync_manifest.json"
    if exports_available and manifest_path.is_file():
        manifest_raw, _ = _safe_read_json(manifest_path)
        for entry in (manifest_raw or {}).get("mappings") or []:
            src = eff_exports / str(entry.get("source") or "")
            dst = docs_dir / str(entry.get("target") or "")
            if src.is_file():
                if not dst.is_file():
                    stale_manifest_pngs.append(
                        {"target": str(entry.get("target")), "reason": "missing_target"}
                    )
                elif _compute_file_sha256(src) != _compute_file_sha256(dst):
                    stale_manifest_pngs.append(
                        {"target": str(entry.get("target")), "reason": "sha256_mismatch"}
                    )

    return {
        "total_svgs": len(svg_files),
        "svgs_older_than_cad_count": len(older_than_cad),
        "svgs_older_than_cad": older_than_cad[:25],
        "exports_available": exports_available,
        "newest_snapshot_png": newest_png_name,
        "newest_snapshot_mtime_iso": (
            datetime.fromtimestamp(newest_png_mtime, tz=timezone.utc).isoformat()
            if newest_png_mtime is not None
            else None
        ),
        "stale_manifest_pngs": stale_manifest_pngs,
    }


def compute_bitemporal_doc_hierarchy(
    docs_root: Path = DEFAULT_DOCS_ROOT,
) -> dict[str, Any]:
    """Classe les documents actifs par niveau (Niveau 1 > Niveau 2) et fraicheur temporelle."""
    docs_dir = Path(docs_root)
    if not docs_dir.is_dir():
        return {
            "level1_count": 0,
            "level2_study_count": 0,
            "level2_superseded_count": 0,
            "pending_consolidations_count": 0,
            "pending_consolidations": [],
            "superseded_studies": [],
        }

    root_res = docs_dir.resolve()
    by_folder: dict[str, list[tuple[str, Path, float]]] = defaultdict(list)
    total_l1 = 0
    total_l2_study = 0

    for p in collect_docs_files(docs_dir):
        if p.suffix.lower() != ".md":
            continue
        try:
            rel = str(p.resolve().relative_to(root_res))
        except ValueError:
            rel = p.name
        folder_rel = str(Path(rel).parent) if "/" in rel else "."
        mtime = p.stat().st_mtime
        by_folder[folder_rel].append((rel, p, mtime))

    pending_consolidations: list[dict[str, Any]] = []
    superseded_studies: list[dict[str, Any]] = []
    superseded_count = 0

    for folder_rel, items in sorted(by_folder.items()):
        l1_items = [
            it for it in items if it[1].name.startswith(LEVEL1_DOC_PREFIXES)
        ]
        l2_studies = [
            it for it in items if it[1].name.startswith(LEVEL2_STUDY_PREFIXES)
        ]
        total_l1 += len(l1_items)
        total_l2_study += len(l2_studies)
        if not l1_items or not l2_studies:
            continue

        newest_l1_rel, _, max_l1_mtime = max(l1_items, key=lambda it: it[2])
        l1_date = datetime.fromtimestamp(max_l1_mtime, tz=timezone.utc).strftime("%Y-%m-%d")

        for study_rel, _, study_mtime in sorted(l2_studies, key=lambda it: it[2], reverse=True):
            study_date = datetime.fromtimestamp(study_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
            if study_mtime > max_l1_mtime + 60.0:
                pending_consolidations.append(
                    {
                        "folder": folder_rel,
                        "study_rel_path": study_rel,
                        "study_date": study_date,
                        "target_level1_rel_path": newest_l1_rel,
                        "target_level1_date": l1_date,
                        "lead_days": round((study_mtime - max_l1_mtime) / 86400.0, 1),
                    }
                )
            else:
                superseded_count += 1
                superseded_studies.append(
                    {
                        "folder": folder_rel,
                        "study_rel_path": study_rel,
                        "study_date": study_date,
                        "superseded_by": newest_l1_rel,
                        "superseded_by_date": l1_date,
                    }
                )

    pending_consolidations.sort(key=lambda item: item["lead_days"], reverse=True)
    return {
        "level1_count": total_l1,
        "level2_study_count": total_l2_study,
        "level2_superseded_count": superseded_count,
        "pending_consolidations_count": len(pending_consolidations),
        "pending_consolidations": pending_consolidations,
        "superseded_studies": superseded_studies[:40],
    }


def audit_cad_doc_drift(
    docs_root: Path = DEFAULT_DOCS_ROOT,
    exports_root: Path | None = None,
) -> dict[str, Any]:
    """Compare de maniere 100 % deterministe et lecture seule le JSON CAO, la BOM, les docs et les SVG."""
    docs_dir = Path(docs_root)
    bitemporal = compute_bitemporal_doc_hierarchy(docs_dir)
    cad_path = docs_dir / CAD_AUDIT_JSON_REL
    if not cad_path.is_file():
        return {
            "available": False,
            "status": "unavailable",
            "alerts_count": 0,
            "alerts": [],
            "doc_checks": [],
            "bom_check": {},
            "svg_freshness": {},
            "bitemporal_hierarchy": bitemporal,
        }

    cad_raw, err = _safe_read_json(cad_path)
    if not isinstance(cad_raw, dict):
        return {
            "available": False,
            "status": "error",
            "error": err or "JSON CAO illisible",
            "alerts_count": 0,
            "alerts": [],
            "doc_checks": [],
            "bom_check": {},
            "svg_freshness": {},
            "bitemporal_hierarchy": bitemporal,
        }

    cad_mtime = cad_path.stat().st_mtime
    cad_snap = _extract_cad_reference_snapshot(cad_raw)

    doc_checks: list[dict[str, Any]] = []
    alerts: list[dict[str, str]] = []
    for rel in CAD_TARGET_DOCS_RELS:
        p = docs_dir / rel
        if not p.is_file():
            doc_checks.append(
                {
                    "rel_path": rel,
                    "exists": False,
                    "status": "missing",
                    "versions_found": [],
                    "checked_parts": 0,
                    "drifted_parts": 0,
                    "issues": [],
                }
            )
            continue
        chk = _check_doc_against_cad(rel, p, cad_snap)
        doc_checks.append(chk)
        for iss in chk["issues"]:
            alerts.append(
                {
                    "severity": iss["severity"],
                    "code": iss["code"],
                    "target_file": rel,
                    "message": iss["message"],
                }
            )

    # Controle 2 : parite McMaster-Carr CAO <-> BOM locale & globale
    cad_mcm_map = cad_snap.get("mcmaster_refs") or {}
    cad_mcm_set = set(cad_mcm_map.keys())

    def _extract_doc_mcm(rel_p: str) -> tuple[bool, set[str]]:
        fp = docs_dir / rel_p
        if not fp.is_file():
            return False, set()
        txt = fp.read_text(encoding="utf-8", errors="replace")
        return True, {m.upper() for m in _MCMASTER_RE.findall(txt)}

    local_exists, local_mcm = _extract_doc_mcm(LOCAL_BOM_REL)
    global_exists, global_mcm = _extract_doc_mcm(GLOBAL_BOM_REL)

    missing_local = (
        [cad_mcm_map[r] for r in sorted(cad_mcm_set - local_mcm)] if local_exists else []
    )
    missing_global = (
        [cad_mcm_map[r] for r in sorted(cad_mcm_set - global_mcm)] if global_exists else []
    )
    extra_local = sorted(local_mcm - cad_mcm_set) if local_exists else []

    if missing_local:
        refs_str = ", ".join(item["ref"] for item in missing_local[:8])
        alerts.append(
            {
                "severity": "critical",
                "code": "CAD_BOM_MISSING_REF",
                "target_file": LOCAL_BOM_REL,
                "message": (
                    f"{len(missing_local)} reference(s) McMaster-Carr presente(s) en CAO "
                    f"absente(s) de la BOM locale : {refs_str}"
                ),
            }
        )
    if missing_global:
        refs_str = ", ".join(item["ref"] for item in missing_global[:8])
        alerts.append(
            {
                "severity": "warning",
                "code": "CAD_BOM_MISSING_REF",
                "target_file": GLOBAL_BOM_REL,
                "message": (
                    f"{len(missing_global)} reference(s) McMaster-Carr presente(s) en CAO "
                    f"absente(s) de la BOM globale : {refs_str}"
                ),
            }
        )

    bom_check = {
        "local_bom_rel": LOCAL_BOM_REL,
        "global_bom_rel": GLOBAL_BOM_REL,
        "cad_refs_count": len(cad_mcm_set),
        "local_bom_refs_count": len(local_mcm),
        "global_bom_refs_count": len(global_mcm),
        "missing_in_local_bom": missing_local,
        "missing_in_global_bom": missing_global,
        "extra_in_local_bom": extra_local,
    }

    # Controle 3 : fraicheur des SVG et snapshots PNG
    svg_freshness = _check_svg_and_snapshot_freshness(docs_dir, cad_mtime, exports_root)
    if svg_freshness["stale_manifest_pngs"]:
        alerts.append(
            {
                "severity": "warning",
                "code": "STALE_VISUAL_SNAPSHOT",
                "target_file": TORSE_MEDIA_REL,
                "message": (
                    f"{len(svg_freshness['stale_manifest_pngs'])} snapshot(s) PNG dans media/ "
                    "desynchronise(s) vis-a-vis de Exports_CAO_DBot."
                ),
            }
        )

    has_crit = any(a["severity"] == "critical" for a in alerts)
    has_warn = any(a["severity"] == "warning" for a in alerts) or (
        svg_freshness["svgs_older_than_cad_count"] > 0
    )
    overall_status = "critical" if has_crit else ("warning" if has_warn else "healthy")

    return {
        "available": True,
        "status": overall_status,
        "cad_json_rel": CAD_AUDIT_JSON_REL,
        "cad_mtime_iso": datetime.fromtimestamp(cad_mtime, tz=timezone.utc).isoformat(),
        "cad_summary": {
            "document_name": cad_snap["document_name"],
            "cad_version_num": cad_snap["cad_version_num"],
            "timestamp": cad_snap["timestamp"],
            "total_mass_g": cad_snap["total_mass_g"],
            "total_mass_kg": cad_snap["total_mass_kg"],
            "instances_count": cad_snap["instances_count"],
            "unique_bom_count": cad_snap["unique_bom_count"],
            "physical_size_mm": cad_snap["physical_size_mm"],
            "center_of_mass_mm": cad_snap["center_of_mass_mm"],
            "key_parts_checked": [
                {
                    "label": p["label"],
                    "unit_mass_g": p["unit_mass_g"],
                    "total_mass_g": p["total_mass_g"],
                    "quantity": p["quantity"],
                }
                for p in cad_snap["key_parts"]
            ],
        },
        "alerts_count": len(alerts),
        "alerts": alerts,
        "doc_checks": doc_checks,
        "bom_check": bom_check,
        "svg_freshness": svg_freshness,
        "bitemporal_hierarchy": bitemporal,
    }


def run_full_audit(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    docs_root: Path = DEFAULT_DOCS_ROOT,
    log_path: Path = DEFAULT_LOG_PATH,
    include_log_scan: bool = True,
) -> dict[str, Any]:
    """Execute un audit complet en lecture seule de la base LightRAG D-Bot."""
    t0 = time.perf_counter()
    db_dir = Path(db_path)
    docs_dir = Path(docs_root)

    read_warnings: list[str] = []

    idx_raw, err = _safe_read_json(db_dir / "indexed_files.json")
    if err:
        read_warnings.append(err)
    idx_map = idx_raw if isinstance(idx_raw, dict) else {}

    ds_raw, err = _safe_read_json(db_dir / "kv_store_doc_status.json")
    if err:
        read_warnings.append(err)
    ds_map = ds_raw if isinstance(ds_raw, dict) else {}

    fd_raw, err = _safe_read_json(db_dir / "kv_store_full_docs.json")
    if err:
        read_warnings.append(err)
    fd_map = fd_raw if isinstance(fd_raw, dict) else {}

    fe_raw, err = _safe_read_json(db_dir / "kv_store_full_entities.json")
    if err:
        read_warnings.append(err)
    fe_map = fe_raw if isinstance(fe_raw, dict) else {}

    fr_raw, err = _safe_read_json(db_dir / "kv_store_full_relations.json")
    if err:
        read_warnings.append(err)
    fr_map = fr_raw if isinstance(fr_raw, dict) else {}

    tc_raw, err = _safe_read_json(db_dir / "kv_store_text_chunks.json")
    if err:
        read_warnings.append(err)
    tc_map = tc_raw if isinstance(tc_raw, dict) else {}

    cache_raw, err = _safe_read_json(db_dir / "kv_store_llm_response_cache.json")
    if err:
        read_warnings.append(err)
    cache_map = cache_raw if isinstance(cache_raw, dict) else {}

    vdb_chunk_ids, vdb_chunk_len, err = _extract_vdb_summary(db_dir / "vdb_chunks.json")
    if err:
        read_warnings.append(err)
    _, vdb_ent_len, err = _extract_vdb_summary(db_dir / "vdb_entities.json")
    if err:
        read_warnings.append(err)
    _, vdb_rel_len, err = _extract_vdb_summary(db_dir / "vdb_relationships.json")
    if err:
        read_warnings.append(err)

    graph, err = _safe_read_graphml(db_dir / "graph_chunk_entity_relation.graphml")
    if err:
        read_warnings.append(err)

    disk_files = collect_docs_files(docs_dir) if docs_dir.is_dir() else []
    disk_by_rel: dict[str, Path] = {}
    for p in disk_files:
        try:
            rel = str(p.resolve().relative_to(docs_dir.resolve()))
        except ValueError:
            rel = p.name
        disk_by_rel[rel] = p

    active_rel_set = set(disk_by_rel.keys())
    all_files_str = {str(p.resolve()) for p in disk_files}
    active_basenames = {p.name for p in disk_files}
    active_flat_keys = build_active_source_aliases(active_rel_set)

    # Index lookup par chemin relatif
    idx_by_rel: dict[str, dict[str, Any]] = {}
    for abs_p, entry in idx_map.items():
        if not isinstance(entry, dict):
            continue
        try:
            rel = str(Path(abs_p).resolve().relative_to(docs_dir.resolve()))
        except Exception:
            rel = abs_p
        idx_by_rel[rel] = entry

    resolved_rels, rel_to_doc_ids = _resolve_doc_rel_paths(
        ds_map, fd_map, idx_map, docs_dir, active_rel_set, active_basenames
    )

    documents: list[dict[str, Any]] = []
    for rel_path in sorted(active_rel_set):
        abs_p = disk_by_rel[rel_path]
        idx_entry = idx_by_rel.get(rel_path)
        cand_ids = [did for did in rel_to_doc_ids.get(rel_path, []) if not did.startswith("dup-")]
        active_ids, dup_ids = _partition_doc_ids_for_rel(
            cand_ids,
            idx_entry if isinstance(idx_entry, dict) else None,
            ds_map,
            fd_map,
        )
        primary_id = active_ids[0] if active_ids else None

        doc_audit = _score_document(
            rel_path=rel_path,
            abs_path=abs_p,
            doc_id=primary_id,
            d_data=ds_map.get(primary_id) if primary_id else None,
            fd_entry=fd_map.get(primary_id) if primary_id else None,
            idx_entry=idx_entry,
            duplicate_ids=dup_ids,
            fe_map=fe_map,
            fr_map=fr_map,
            tc_map=tc_map,
            cache_map=cache_map,
            vdb_chunk_ids=vdb_chunk_ids,
            docs_root=docs_dir,
            section_doc_ids=active_ids,
            ds_map=ds_map,
            fd_map=fd_map,
        )
        documents.append(doc_audit)

    # Orphelins en base (absents du disque actif)
    orphans: list[dict[str, Any]] = []
    for d_id, d_data in ds_map.items():
        if not isinstance(d_data, dict):
            continue
        rel = resolved_rels.get(d_id)
        if _is_orphan_entry(
            d_id,
            d_data,
            rel,
            active_rel_set,
            all_files_str,
            active_basenames,
            docs_dir,
            active_flat_keys=active_flat_keys,
        ):
            orphans.append(
                {
                    "doc_id": d_id,
                    "rel_or_file": rel or str(d_data.get("file_path", "")),
                    "status": str(d_data.get("status", "")),
                    "updated_at": str(d_data.get("updated_at", "")),
                }
            )

    # Audit deterministe temps reel CAO JSON <-> Markdown / BOM / SVG (Brique 1)
    cad_drift = audit_cad_doc_drift(docs_root=docs_dir)
    alerts_by_rel: dict[str, list[dict[str, str]]] = defaultdict(list)
    for al in cad_drift.get("alerts") or []:
        tgt = str(al.get("target_file") or "")
        if tgt:
            alerts_by_rel[tgt].append(al)
    for doc in documents:
        doc_alerts = alerts_by_rel.get(doc["rel_path"], [])
        if not doc_alerts:
            continue
        doc["cad_drift_issues"] = doc_alerts
        for al in doc_alerts:
            code = str(al.get("code") or "")
            if code and code not in doc["reasons"]:
                doc["reasons"].append(code)
            msg = str(al.get("message") or "")
            if msg and msg not in doc["warnings"]:
                doc["warnings"].append(msg)
        if any(al.get("severity") == "critical" for al in doc_alerts):
            if doc["health_status"] == "healthy":
                doc["health_status"] = "warning"
        elif doc["health_status"] == "healthy":
            doc["health_status"] = "warning"

    # Tri par severite puis score croissant (les plus urgents en premier)
    status_rank = {"critical": 0, "warning": 1, "healthy": 2}
    priority_rank = {"critical": 0, "standard": 1, "image": 2}
    documents.sort(
        key=lambda d: (
            status_rank.get(d["health_status"], 9),
            priority_rank.get(d["priority"], 9),
            d["score"],
            d["rel_path"],
        )
    )

    chunk_opts_counts = Counter(
        str(((v.get("metadata") or {}).get("chunk_opts") or "inconnu"))
        for v in ds_map.values()
        if isinstance(v, dict)
    )
    status_counts = Counter(
        str(v.get("status") or "unknown")
        for v in ds_map.values()
        if isinstance(v, dict)
    )
    reason_counts = Counter(r for doc in documents for r in doc["reasons"])
    health_counts = Counter(doc["health_status"] for doc in documents)

    # Stats globales cache extraction
    extract_entries = [
        v
        for v in cache_map.values()
        if isinstance(v, dict) and v.get("cache_type", "extract") == "extract"
    ]
    cache_missing_complete = sum(
        1 for v in extract_entries if COMPLETION_DELIMITER not in str(v.get("return") or "")
    )
    cache_broken_delim = sum(
        1 for v in extract_entries if "<|#||>" in str(v.get("return") or "")
    )
    cache_short = sum(
        1
        for v in extract_entries
        if len(str(v.get("return") or "").replace(COMPLETION_DELIMITER, "").strip()) < 40
    )

    graph_health = _audit_graph_health(
        graph=graph,
        tc_ids=set(tc_map.keys()),
        vdb_chunk_ids=vdb_chunk_ids,
        vdb_ent_count=vdb_ent_len,
        vdb_rel_count=vdb_rel_len,
    )

    avg_score = (
        round(sum(d["score"] for d in documents) / len(documents), 1) if documents else 0.0
    )
    live_status = detect_live_indexing_status(db_dir, log_path)
    log_summary = parse_indexing_log_summary(log_path) if include_log_scan else {}

    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
    storage_info = _compute_storage_info(db_dir)
    sectioned_files_count = sum(1 for d in documents if int(d.get("sections_count") or 0) > 0)
    virtual_sections_total = sum(int(d.get("sections_count") or 0) for d in documents)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audit_duration_ms": elapsed_ms,
        "db_path": str(db_dir),
        "docs_root": str(docs_dir),
        "storage": storage_info,
        "live_indexing": live_status,
        "read_warnings": read_warnings,
        "summary": {
            "disk_files_count": len(disk_files),
            "indexed_files_log_count": len(idx_map),
            "full_docs_count": len(fd_map),
            "doc_status_count": len(ds_map),
            "text_chunks_count": len(tc_map),
            "vdb_chunks_count": vdb_chunk_len,
            "sectioned_files_count": sectioned_files_count,
            "virtual_sections_total": virtual_sections_total,
            "avg_health_score": avg_score,
            "health_counts": dict(health_counts),
            "doc_status_breakdown": dict(status_counts),
            "chunk_opts_breakdown": dict(chunk_opts_counts),
            "reason_counts": dict(reason_counts.most_common()),
            "orphans_count": len(orphans),
            "cache_total_keys": len(cache_map),
            "cache_extract_keys": len(extract_entries),
            "cache_missing_complete": cache_missing_complete,
            "cache_broken_delimiters": cache_broken_delim,
            "cache_short_or_empty_glean": cache_short,
            "cad_drift_alerts_count": int(cad_drift.get("alerts_count") or 0),
        },
        "cad_drift": cad_drift,
        "graph_health": graph_health,
        "log_summary": log_summary,
        "orphans": orphans,
        "documents": documents,
    }


def inspect_document_detail(
    rel_path: str,
    *,
    db_path: Path = DEFAULT_DB_PATH,
    docs_root: Path = DEFAULT_DOCS_ROOT,
) -> dict[str, Any]:
    """Retourne le detail chunk par chunk (source, cache LLM brut, sous-graphe) d'un fichier."""
    db_dir = Path(db_path)
    docs_dir = Path(docs_root)

    idx_map = _safe_read_json(db_dir / "indexed_files.json")[0] or {}
    ds_map = _safe_read_json(db_dir / "kv_store_doc_status.json")[0] or {}
    fd_map = _safe_read_json(db_dir / "kv_store_full_docs.json")[0] or {}
    fe_map = _safe_read_json(db_dir / "kv_store_full_entities.json")[0] or {}
    fr_map = _safe_read_json(db_dir / "kv_store_full_relations.json")[0] or {}
    tc_map = _safe_read_json(db_dir / "kv_store_text_chunks.json")[0] or {}
    cache_map = _safe_read_json(db_dir / "kv_store_llm_response_cache.json")[0] or {}
    vdb_chunk_ids, _, _ = _extract_vdb_summary(db_dir / "vdb_chunks.json")
    graph, _ = _safe_read_graphml(db_dir / "graph_chunk_entity_relation.graphml")

    disk_files = collect_docs_files(docs_dir) if docs_dir.is_dir() else []
    active_rel_set = {str(p.resolve().relative_to(docs_dir.resolve())) for p in disk_files}
    active_basenames = {p.name for p in disk_files}
    _, rel_to_doc_ids = _resolve_doc_rel_paths(
        ds_map, fd_map, idx_map, docs_dir, active_rel_set, active_basenames
    )

    abs_p = (docs_dir / rel_path).resolve()
    if not abs_p.is_relative_to(docs_dir.resolve()):
        raise ValueError("Chemin hors docs_root interdit.")

    idx_entry = idx_map.get(str(abs_p))
    cand_ids = [did for did in rel_to_doc_ids.get(rel_path, []) if not did.startswith("dup-")]
    active_ids, dup_ids = _partition_doc_ids_for_rel(
        cand_ids,
        idx_entry if isinstance(idx_entry, dict) else None,
        ds_map,
        fd_map,
    )
    primary_id = active_ids[0] if active_ids else None

    doc_audit = _score_document(
        rel_path=rel_path,
        abs_path=abs_p if abs_p.is_file() else None,
        doc_id=primary_id,
        d_data=ds_map.get(primary_id) if primary_id else None,
        fd_entry=fd_map.get(primary_id) if primary_id else None,
        idx_entry=idx_entry if isinstance(idx_entry, dict) else None,
        duplicate_ids=dup_ids,
        fe_map=fe_map,
        fr_map=fr_map,
        tc_map=tc_map,
        cache_map=cache_map,
        vdb_chunk_ids=vdb_chunk_ids,
        docs_root=docs_dir,
        section_doc_ids=active_ids,
        ds_map=ds_map,
        fd_map=fd_map,
    )

    chunk_ids: list[str] = []
    chunk_seen: set[str] = set()
    for did in active_ids:
        for cid in ((ds_map.get(did) or {}).get("chunks_list") or []):
            if cid not in chunk_seen:
                chunk_seen.add(cid)
                chunk_ids.append(cid)
    chunks_detail: list[dict[str, Any]] = []
    for order, cid in enumerate(chunk_ids):
        tc_row = tc_map.get(cid) if isinstance(tc_map.get(cid), dict) else {}
        content = str(tc_row.get("content") or "")
        chunk_doc_id = str(tc_row.get("full_doc_id") or "")
        fd_chunk_doc = (
            fd_map.get(chunk_doc_id)
            if chunk_doc_id and isinstance(fd_map.get(chunk_doc_id), dict)
            else {}
        )
        section_key = extract_section_key(fd_chunk_doc.get("content", "")) if fd_chunk_doc else None
        cache_entries = []
        parsed_entities: list[dict[str, str]] = []
        parsed_relations: list[dict[str, str]] = []
        syntax_errors: list[str] = []

        for pos, ck in enumerate(tc_row.get("llm_cache_list") or []):
            c_obj = cache_map.get(ck)
            if not isinstance(c_obj, dict):
                continue
            ret = str(c_obj.get("return") or "")
            if pos == 0:
                syntax_errors = validate_single_extraction(ret, label=cid)
            ents, rels = _extract_entity_relation_rows(ret)
            for e in ents:
                parsed_entities.append(
                    {"name": e[1], "type": e[2], "description": e[3]}
                )
            for r in rels:
                parsed_relations.append(
                    {
                        "source": r[1],
                        "target": r[2],
                        "keywords": r[3],
                        "description": r[4],
                    }
                )
            cache_entries.append(
                {
                    "cache_key": ck,
                    "pass_index": pos + 1,
                    "has_complete": COMPLETION_DELIMITER in ret,
                    "char_len": len(ret),
                    "raw_return": ret,
                }
            )

        chunks_detail.append(
            {
                "chunk_id": cid,
                "doc_id": chunk_doc_id,
                "section_key": section_key,
                "order": order,
                "tokens": int(tc_row.get("tokens") or 0),
                "in_vdb_chunks": cid in vdb_chunk_ids,
                "content_preview": content[:3000],
                "content_len": len(content),
                "syntax_errors": syntax_errors,
                "entities": parsed_entities,
                "relations": parsed_relations,
                "cache_passes": cache_entries,
            }
        )

    # Sous-graphe du document depuis GraphML
    subgraph = {"nodes": [], "edges": []}
    if graph is not None and active_ids:
        doc_ent_set: set[str] = set()
        for did in active_ids:
            fe_entry = fe_map.get(did) if isinstance(fe_map.get(did), dict) else {}
            doc_ent_set.update(fe_entry.get("entity_names") or [])
        chunk_set = set(chunk_ids)
        nodes_keep: set[str] = set()
        for nid, attrs in graph.nodes(data=True):
            srcs = {s for s in str(attrs.get("source_id", "")).split("<SEP>") if s}
            if str(nid) in doc_ent_set or (chunk_set and srcs & chunk_set):
                nodes_keep.add(str(nid))
                if len(nodes_keep) >= 80:
                    break
        subgraph["nodes"] = [
            {
                "id": nid,
                "type": str(graph.nodes[nid].get("entity_type", "unknown")),
                "degree": int(graph.degree(nid)),
                "description": str(graph.nodes[nid].get("description", ""))[:240],
            }
            for nid in sorted(nodes_keep)
        ]
        for u, v, attrs in graph.edges(data=True):
            su, sv = str(u), str(v)
            if su in nodes_keep and sv in nodes_keep:
                subgraph["edges"].append(
                    {
                        "source": su,
                        "target": sv,
                        "keywords": str(attrs.get("keywords", ""))[:120],
                    }
                )
                if len(subgraph["edges"]) >= 180:
                    break

    return {
        "audit": doc_audit,
        "chunks": chunks_detail,
        "subgraph": subgraph,
    }


def export_static_html_report(report: dict[str, Any], output_path: Path | None = None) -> str:
    """Genere un rapport HTML autonome (zero dependance CDN) a partir d'un bilan."""
    s = report.get("summary", {})
    g = report.get("graph_health", {})
    cd = report.get("cad_drift") or {}
    docs = report.get("documents", [])
    live = report.get("live_indexing", {})
    hc = s.get("health_counts", {})

    rows_html: list[str] = []
    for doc in docs:
        badge_cls = doc["health_status"]
        reasons_str = ", ".join(doc["reasons"]) if doc["reasons"] else "OK"
        ret_str = (
            f"{doc['metric_retention']*100:.0f} %"
            if doc.get("metric_retention") is not None
            else "-"
        )
        grd_str = (
            f"{doc['grounding_rate']*100:.0f} %"
            if doc.get("grounding_rate") is not None
            else "-"
        )
        rows_html.append(
            "<tr>"
            f"<td><span class='badge {html.escape(badge_cls)}'>{doc['score']}</span></td>"
            f"<td>{html.escape(doc['priority'])}</td>"
            f"<td><code>{html.escape(doc['rel_path'])}</code></td>"
            f"<td>{html.escape(doc['chunk_opts'])}</td>"
            f"<td>{doc['entities_count']} / {doc['relations_count']}</td>"
            f"<td>{doc['relations_per_1k_tok']}</td>"
            f"<td>{ret_str}</td>"
            f"<td>{grd_str}</td>"
            f"<td>{html.escape(reasons_str)}</td>"
            "</tr>"
        )

    reidx_cmds = [
        doc["recommended_action"]
        for doc in docs
        if doc["health_status"] in ("critical", "warning")
    ][:30]
    live_banner = (
        f"INDEXATION EN COURS ({html.escape(str(live.get('active_engine') or 'active'))})"
        if live.get("indexing_active")
        else "Base au repos"
    )

    page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>D-Bot RAG Quality Snapshot</title>
<style>
body {{ background:#0f172a; color:#e2e8f0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; margin:0; padding:24px; }}
h1,h2 {{ color:#f8fafc; margin-top:0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-bottom:20px; }}
.card {{ background:#1e293b; border:1px solid #334155; border-radius:10px; padding:14px; }}
.val {{ font-size:24px; font-weight:700; color:#38bdf8; }}
.lbl {{ font-size:12px; color:#94a3b8; }}
table {{ width:100%; border-collapse:collapse; background:#1e293b; border-radius:10px; overflow:hidden; font-size:13px; }}
th,td {{ padding:8px 10px; border-bottom:1px solid #334155; text-align:left; }}
th {{ background:#0b1220; color:#94a3b8; }}
.badge {{ display:inline-block; padding:2px 8px; border-radius:999px; font-weight:700; font-size:12px; }}
.badge.critical {{ background:#7f1d1d; color:#fecaca; }}
.badge.warning {{ background:#78350f; color:#fde68a; }}
.badge.healthy {{ background:#064e3b; color:#a7f3d0; }}
pre {{ background:#0b1220; padding:12px; border-radius:8px; overflow:auto; border:1px solid #334155; }}
</style>
</head>
<body>
<h1>D-Bot LightRAG — Rapport Qualite ({html.escape(report.get("generated_at", ""))})</h1>
<p>Etat lors du snapshot : <strong>{live_banner}</strong> | Duree audit : {report.get("audit_duration_ms", 0)} ms</p>
<div class="grid">
  <div class="card"><div class="val">{s.get("avg_health_score", 0)}/100</div><div class="lbl">Score moyen</div></div>
  <div class="card"><div class="val">{hc.get("critical", 0)}</div><div class="lbl">Critiques (a re-indexer)</div></div>
  <div class="card"><div class="val">{hc.get("warning", 0)}</div><div class="lbl">Avertissements</div></div>
  <div class="card"><div class="val">{hc.get("healthy", 0)}</div><div class="lbl">Sains</div></div>
  <div class="card"><div class="val">{g.get("nodes", 0)} / {g.get("edges", 0)}</div><div class="lbl">Noeuds / Aretes GraphML</div></div>
  <div class="card"><div class="val">{g.get("degree_zero_nodes", 0)}</div><div class="lbl">Noeuds isoles (degre 0)</div></div>
  <div class="card"><div class="val">{cd.get("alerts_count", 0) if cd.get("available") else "-"}</div><div class="lbl">Alertes derive CAO / BOM</div></div>
</div>
<h2>Commandes prioritaires suggerees (top 30)</h2>
<pre>{html.escape(chr(10).join(reidx_cmds) if reidx_cmds else "Tout est sain.")}</pre>
<h2>Detail par fichier ({len(docs)})</h2>
<table>
<thead><tr><th>Score</th><th>Priorite</th><th>Fichier</th><th>Chunking</th><th>Ent/Rel</th><th>Rel/1k tok</th><th>Retention</th><th>Ancrage</th><th>Anomalies</th></tr></thead>
<tbody>{"".join(rows_html)}</tbody>
</table>
</body>
</html>"""
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(page, encoding="utf-8")
    return page


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit qualite 100 % lecture seule du RAG LightRAG D-Bot"
    )
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--docs-root", type=Path, default=DEFAULT_DOCS_ROOT)
    parser.add_argument("--json", action="store_true", help="Affiche le bilan complet au format JSON")
    parser.add_argument("--html", type=Path, default=None, help="Exporte un rapport HTML autonome")
    parser.add_argument("--top", type=int, default=20, help="Nombre de fichiers prioritaires a afficher")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    report = run_full_audit(db_path=args.db_path, docs_root=args.docs_root)

    if args.html is not None:
        export_static_html_report(report, args.html)
        print(f"Rapport HTML ecrit dans : {args.html}")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    s = report["summary"]
    g = report["graph_health"]
    live = report["live_indexing"]
    hc = s["health_counts"]
    print(f"=== D-Bot RAG Quality Audit ({report['audit_duration_ms']} ms) ===")
    print(
        f"Indexation active : {live['indexing_active']} "
        f"(lock={live['lock_active']}, pids={live['active_pids']}, moteur={live['active_engine'] or '-'})"
    )
    print(
        f"Fichiers disque: {s['disk_files_count']} | doc_status: {s['doc_status_count']} | "
        f"indexed_files: {s['indexed_files_log_count']} | orphelins: {s['orphans_count']}"
    )
    print(
        f"Score moyen: {s['avg_health_score']}/100 | "
        f"Critiques: {hc.get('critical', 0)} | Warnings: {hc.get('warning', 0)} | Sains: {hc.get('healthy', 0)}"
    )
    print(
        f"GraphML: {g['nodes']} noeuds, {g['edges']} aretes, {g['degree_zero_nodes']} isoles (degre 0)"
    )
    cd = report.get("cad_drift") or {}
    if cd.get("available"):
        cs = cd.get("cad_summary") or {}
        sf = cd.get("svg_freshness") or {}
        print(
            f"CAO JSON: {cs.get('document_name')} ({cs.get('total_mass_kg')} kg) | "
            f"Alertes derive: {cd.get('alerts_count', 0)} | "
            f"SVG anterieurs a CAO: {sf.get('svgs_older_than_cad_count', 0)}/{sf.get('total_svgs', 0)}"
        )
    print(f"Top {args.top} fichiers prioritaires a surveiller / re-indexer :")
    for doc in report["documents"][: max(1, args.top)]:
        print(
            f"  [{doc['score']:3d}/100] [{doc['health_status']:8s}] [{doc['priority']:8s}] "
            f"{doc['rel_path']} -> {', '.join(doc['reasons']) or 'OK'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
