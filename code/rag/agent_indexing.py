#!/opt/homebrew/bin/python3.11
"""
Indexation Graph-RAG pilotee par l'agent Antigravity (0 LLM tiers).

Architecture en 3 phases :
  1. prepare_agent_bundle()  : decoupage exact (1600/150 tokens Tiktoken) + routage
                               d'effort adapte (fast/balanced/thorough, jamais extra_high).
  2. Extraction par l'agent  : production des tuples <|#|>...<|COMPLETE|> (et descriptions
                               VLM via lecture visuelle directe des images PNG/JPG).
  3. commit_agent_bundle()   : linter strict + injection deterministe dans le vrai
                               LightRAG.ainsert() (purge, embeddings CPU, ancres JSON).
"""

from __future__ import annotations

import errno
import fcntl
import hashlib
import json
import os
import re
import shutil
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from lightrag import LightRAG
from lightrag.lightrag import chunking_by_token_size
from lightrag.prompt import PROMPTS
from lightrag.utils import TiktokenTokenizer

from rag_chunking import (
    EXCLUDE_DIRS,
    EXCLUDE_FILES,
    IMAGE_EXTS,
    INCLUDE_EXTS,
    PDF_EXTS,
    SVG_EXTS,
    chunking_markdown_anchored,
    collect_docs_files,
    compute_doc_id,
    compute_normalized_sha256,
    extract_pdf_text_cached,
    split_markdown_into_virtual_sections,
)
from source_key_utils import (
    build_active_source_aliases,
    build_claimed_source_map,
    build_rag_source_key,
    build_section_source_key,
    canonical_source_name,
    extract_rel_path,
    extract_section_key,
    is_doc_processed,
)

TUPLE_DELIMITER = PROMPTS.get("DEFAULT_TUPLE_DELIMITER", "<|#|>")
COMPLETION_DELIMITER = PROMPTS.get("DEFAULT_COMPLETION_DELIMITER", "<|COMPLETE|>")

_SVG_SKIP_TAGS = frozenset({"defs", "style", "script", "metadata"})
_SVG_INLINE_TEXT_TAGS = frozenset({"tspan", "a", "textpath"})

_CRITICAL_PREFIXES = (
    "FINAL_",
    "DOSSIER_TECHNIQUE_",
    "STUDY_",
    "GUIDE_COMPLET_",
    "AUDIT_",
)
_METRIC_RE = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:mm|cm|m|kg|g|nm|n\.m|mpa|kpa|v|a|ah|wh|w|hz|khz|mhz|deg|°)\b",
    re.IGNORECASE,
)
_INPUT_TEXT_RE = re.compile(
    r"---Input Text---\s*```(?:[A-Za-z0-9_-]*)\n(.*)\n```(?=\s*(?:---|\Z))",
    re.DOTALL,
)
_SUMMARY_NAME_RE = re.compile(r"^(?:Entity|Relation)\s+Name:\s*(.+)$", re.MULTILINE)
_LATEX_RE = re.compile(
    r"\\(?:text|approx|varnothing|pm|sqrt|circ|times|cdot|frac|mathbf)\b"
)

# Politique de thinking / effort pour l'indexation (sans jamais recourir a extra_high)
AGENT_EFFORT_PROFILES: dict[str, dict[str, Any]] = {
    "fast": {
        "label": "Rapide (aucune sur-reflexion)",
        "default_subagent_model": "flash",
        "critical_subagent_model": "flash",
        "gemini_thinking_level": "minimal",
        "thinking_directive": (
            "Extraction directe 1 passe (zero meta-raisonnement, zero extra_high). "
            "Produis uniquement les lignes entity/relation terminees par <|COMPLETE|>."
        ),
    },
    "balanced": {
        "label": "Equilibre optimal (flash standard + inherit critique, jamais extra_high)",
        "default_subagent_model": "flash",
        "critical_subagent_model": "inherit",
        "gemini_thinking_level": "low",
        "thinking_directive": (
            "Niveau adapte optimal sans extra_high : modele 'flash' rapide en 1 passe sur "
            "chunks standards ; modele 'inherit' concis sur dossiers Niveau 1 / PDF / images VLM."
        ),
    },
    "thorough": {
        "label": "Approfondi borne (inherit 1 passe, jamais extra_high)",
        "default_subagent_model": "inherit",
        "critical_subagent_model": "inherit",
        "gemini_thinking_level": "medium",
        "thinking_directive": (
            "Extraction exhaustive en 1 passe (sans extra_high ni dissertation) : "
            "conserver toutes cotes, tolerances, couples et references McMaster-Carr."
        ),
    },
}


def resolve_effort_profile(effort_profile: str | None) -> str:
    """Normalise un profil d'effort vers fast, balanced (defaut) ou thorough."""
    norm = (effort_profile or "balanced").strip().lower()
    if norm in ("minimal", "low", "fast", "flash"):
        return "fast"
    if norm in ("medium", "high", "thorough", "pro", "critical"):
        return "thorough" if norm in ("thorough", "high", "pro", "critical") else "balanced"
    if norm in AGENT_EFFORT_PROFILES:
        return norm
    return "balanced"


def normalize_chunk_text(text: str) -> str:
    return (text or "").replace("\r\n", "\n").strip()


def compute_chunk_hash(text: str) -> str:
    """Hash SHA-256 deterministe du texte de chunk normalise."""
    return hashlib.sha256(normalize_chunk_text(text).encode("utf-8")).hexdigest()[:24]


def compute_file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _svg_local_tag(tag: object) -> str:
    return tag.split("}", 1)[-1].lower() if isinstance(tag, str) else ""


def _extract_svg_text_node(el: Any) -> str:
    chunks: list[str] = []
    if el.text:
        chunks.append(el.text)
    for child in el:
        if _svg_local_tag(child.tag) in _SVG_INLINE_TEXT_TAGS:
            child_text = _extract_svg_text_node(child)
            if child_text:
                if chunks and ("x" in child.attrib or "y" in child.attrib or "dy" in child.attrib):
                    chunks.append(" ")
                chunks.append(child_text)
        if child.tail:
            chunks.append(child.tail)
    return " ".join("".join(chunks).split())


def _collect_svg_blocks(node: Any, depth: int = 0) -> list[str]:
    blocks: list[str] = []
    current_lines: list[str] = []

    def flush_current() -> None:
        if current_lines:
            blocks.append("\n".join(current_lines))
            current_lines.clear()

    for child in node:
        tag = _svg_local_tag(child.tag)
        if not tag or tag in _SVG_SKIP_TAGS:
            continue
        if tag == "title":
            txt = " ".join("".join(child.itertext()).split())
            if txt:
                prefix = "Titre SVG : " if depth == 0 else "Sous-section : "
                current_lines.append(f"{prefix}{txt}")
        elif tag == "desc":
            txt = " ".join("".join(child.itertext()).split())
            if txt:
                prefix = "Description SVG : " if depth == 0 else "Note : "
                current_lines.append(f"{prefix}{txt}")
        elif tag == "text":
            txt = _extract_svg_text_node(child)
            if txt:
                current_lines.append(txt)
        else:
            child_blocks = _collect_svg_blocks(child, depth + 1)
            if child_blocks:
                if tag == "g" and len(child_blocks) == 1 and "\n" not in child_blocks[0] and depth >= 2:
                    current_lines.append(child_blocks[0])
                elif tag == "g":
                    flush_current()
                    blocks.extend(child_blocks)
                else:
                    for blk in child_blocks:
                        current_lines.extend(blk.splitlines())
    flush_current()
    return blocks


def extract_svg_text(path: Path) -> str:
    """Extrait le texte structure (<title>, <desc>, <text>) d'un SVG via defusedxml."""
    import defusedxml.ElementTree as DefusedET

    try:
        raw_xml = path.read_text(encoding="utf-8")
        root = DefusedET.fromstring(raw_xml)
    except Exception:
        return ""
    return "\n\n".join(_collect_svg_blocks(root))


def extract_pdf_text(path: Path, db_path: Path | None = None) -> str:
    """Extrait le texte d'un PDF via Docling (avec cache disque) puis pypdf en repli."""
    return extract_pdf_text_cached(path, db_path=db_path)


def prepare_non_image_content(
    path: Path,
    docs_root: Path,
    *,
    db_path: Path | None = None,
) -> str:
    """Construit exactement le document texte avec en-tete YAML attendu par LightRAG."""
    try:
        relative = str(path.resolve().relative_to(docs_root.resolve()))
    except ValueError:
        relative = path.name
    ext = path.suffix.lower()

    if ext in PDF_EXTS:
        pdf_text = extract_pdf_text(path, db_path=db_path)
        if not pdf_text.strip():
            return ""
        header = f"---\nFichier: {relative}\nType: Document PDF\nProjet: D-Bot\n---\n\n"
        return (header + f"# Document PDF : {path.name}\n\n" + pdf_text).strip()

    if ext in SVG_EXTS:
        svg_text = extract_svg_text(path)
        if not svg_text.strip():
            return ""
        header = f"---\nFichier: {relative}\nType: Schéma Vectoriel SVG (Texte XML)\nProjet: D-Bot\n---\n\n"
        return (header + f"# Schéma Technique SVG : {path.name}\n\n" + svg_text).strip()

    content = path.read_text(encoding="utf-8")
    header = f"---\nFichier: {relative}\nProjet: D-Bot\n---\n\n"
    return (header + content).strip()


def format_vlm_document(relative: str, file_name: str, vlm_description: str) -> str:
    header = f"---\nFichier: {relative}\nType: Image VLM (Antigravity)\nProjet: D-Bot\n---\n\n"
    return header + f"# Analyse Visuelle et Spécifications Techniques : {file_name}\n\n" + vlm_description.strip()


def classify_chunk_effort(
    rel_path: str,
    chunk_text: str,
    effort_profile: str = "balanced",
    *,
    is_image: bool = False,
) -> tuple[str, str, str]:
    """
    Determine le palier optimal (sans jamais extra_high) pour ce chunk :
    retourne (recommended_subagent_model, effort_tier, effort_reason).
    """
    profile_key = resolve_effort_profile(effort_profile)
    cfg = AGENT_EFFORT_PROFILES[profile_key]
    if profile_key == "fast":
        return cfg["default_subagent_model"], "low", "profile_fast"

    name = os.path.basename(rel_path)
    ext = Path(rel_path).suffix.lower()
    if is_image or ext in IMAGE_EXTS:
        return cfg["critical_subagent_model"], "medium", "vlm_visual_inspection"

    table_rows = sum(1 for line in chunk_text.splitlines() if line.strip().startswith("|") and line.count("|") >= 2)
    metric_hits = len(_METRIC_RE.findall(chunk_text))

    if name.startswith(_CRITICAL_PREFIXES) or ext in PDF_EXTS:
        return cfg["critical_subagent_model"], "medium", "niveau1_or_datasheet"
    if table_rows >= 4 or metric_hits >= 12:
        return cfg["critical_subagent_model"], "medium", "dense_tables_or_metrics"

    return cfg["default_subagent_model"], "low", "standard_text"


def _resolve_target_files(raw_files: list[str], docs_root: Path) -> tuple[list[Path], list[str]]:
    resolved: list[Path] = []
    missing: list[str] = []
    seen: set[Path] = set()
    for raw_f in raw_files:
        cand_input = Path(raw_f).expanduser()
        candidates = [cand_input] if cand_input.is_absolute() else [cand_input, docs_root / cand_input]
        match = next((c.resolve() for c in candidates if c.is_file()), None)
        if match is None:
            missing.append(raw_f)
            continue
        if match not in seen:
            seen.add(match)
            resolved.append(match)
    return resolved, missing


def _chunk_content(
    content: str,
    *,
    tokenizer: TiktokenTokenizer,
    chunk_size: int,
    chunk_overlap: int,
) -> list[dict[str, Any]]:
    return chunking_markdown_anchored(
        tokenizer,
        content,
        None,
        False,
        chunk_overlap,
        chunk_size,
    )


def _load_json_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _rel_path_from_doc_entry(doc_id: str, d_data: dict, fd_map: dict, docs_root: Path) -> str | None:
    fd_entry = fd_map.get(doc_id)
    if isinstance(fd_entry, dict):
        rel = extract_rel_path(fd_entry.get("content", ""))
        if rel:
            return rel
    fp = d_data.get("file_path", "") or ""
    if "/" in fp:
        try:
            p = Path(fp)
            if p.is_absolute():
                return str(p.resolve().relative_to(docs_root.resolve()))
            return str(Path(fp))
        except Exception:
            return fp
    return None


def _is_orphan_entry(
    d_id: str,
    d_data: dict,
    rel: str | None,
    active_rel_set: set[str],
    all_files_str: set[str],
    active_basenames: set[str],
    docs_root: Path,
    active_flat_keys: set[str] | None = None,
) -> bool:
    if d_id.startswith("dup-"):
        return False
    if rel is not None:
        return rel not in active_rel_set
    fp = (d_data.get("file_path", "") or "").strip()
    if not fp or fp == "unknown_source":
        return False
    if "/" in fp:
        cand = str(Path(fp).resolve()) if Path(fp).is_absolute() else str((docs_root / fp).resolve())
        return cand not in all_files_str
    base = os.path.basename(fp)
    if active_flat_keys and (fp in active_flat_keys or base in active_flat_keys):
        return False
    return base not in active_basenames


def resolve_job_dir(db_path: Path, job_id_or_path: str) -> Path:
    """Resout un job_id ou chemin explicite vers son dossier de travail."""
    cand = Path(job_id_or_path).expanduser()
    if cand.is_file() and cand.name == "manifest.json":
        return cand.parent.resolve()
    if cand.is_dir() and (cand / "manifest.json").exists():
        return cand.resolve()
    return (db_path / ".agent_jobs" / job_id_or_path).resolve()


def _build_chunks_for_text(
    *,
    content: str,
    rel_path: str,
    eff_profile: str,
    eff_tokenizer: TiktokenTokenizer,
    eff_chunk_size: int,
    eff_overlap: int,
    section_key: str | None = None,
    section_title: str | None = None,
) -> tuple[list[str], list[dict[str, Any]], Counter[str]]:
    """Decoupe un document ou une section virtuelle et retourne ses metadonnees de chunks."""
    raw_chunks = _chunk_content(
        content,
        tokenizer=eff_tokenizer,
        chunk_size=eff_chunk_size,
        chunk_overlap=eff_overlap,
    )
    doc_chunk_hashes: list[str] = []
    chunk_entries: list[dict[str, Any]] = []
    tier_counts: Counter[str] = Counter()
    total_c = len(raw_chunks)
    for idx, rc in enumerate(raw_chunks):
        c_text = str(rc.get("content", ""))
        c_hash = compute_chunk_hash(c_text)
        rec_model, tier, reason = classify_chunk_effort(rel_path, c_text, eff_profile, is_image=False)
        tier_counts[f"chunk:{rec_model}"] += 1
        doc_chunk_hashes.append(c_hash)
        entry: dict[str, Any] = {
            "chunk_hash": c_hash,
            "exact_sha256": hashlib.sha256(c_text.encode("utf-8")).hexdigest()[:24],
            "doc_rel": rel_path,
            "chunk_index": idx,
            "total_doc_chunks": total_c,
            "tokens": int(rc.get("tokens") or 0),
            "recommended_subagent_model": rec_model,
            "effort_tier": tier,
            "effort_reason": reason,
            "content": c_text,
        }
        if section_key is not None:
            entry["section_key"] = section_key
            entry["section_title"] = section_title or section_key
        chunk_entries.append(entry)
    return doc_chunk_hashes, chunk_entries, tier_counts


def prepare_agent_bundle(
    *,
    docs_root: Path,
    db_path: Path,
    files: list[str] | None = None,
    effort_profile: str = "balanced",
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    full: bool = False,
    section_split: bool = True,
    job_id: str | None = None,
    tokenizer: TiktokenTokenizer | None = None,
) -> dict[str, Any]:
    """
    Scanne les documents cibles, les decoupe avec les memes bornes que LightRAG
    (chunking ancre Markdown + sections virtuelles sur gros .md), et ecrit
    manifest.json + extractions.json dans db_path/.agent_jobs/<job_id>.
    """
    eff_profile = resolve_effort_profile(effort_profile)
    profile_cfg = AGENT_EFFORT_PROFILES[eff_profile]
    eff_chunk_size = int(chunk_size or os.environ.get("CHUNK_SIZE", "1600"))
    eff_overlap = int(chunk_overlap if chunk_overlap is not None else os.environ.get("CHUNK_OVERLAP_SIZE", "150"))
    eff_tokenizer = tokenizer or TiktokenTokenizer()

    docs_root = docs_root.resolve()
    db_path = db_path.resolve()
    all_files = collect_docs_files(docs_root)
    all_files_str = {str(p) for p in all_files}
    active_rel_set = {str(p.relative_to(docs_root)) for p in all_files}
    active_name_counts = Counter(p.name for p in all_files)
    active_basenames = set(active_name_counts.keys())
    active_flat_keys = build_active_source_aliases(active_rel_set)

    log_idx = _load_json_dict(db_path / "indexed_files.json") if not full else {}
    ds_disk = _load_json_dict(db_path / "kv_store_doc_status.json")
    fd_disk = _load_json_dict(db_path / "kv_store_full_docs.json")

    processed_ids: set[str] = set()
    processed_rels: set[str] = set()
    processed_basenames: set[str] = set()
    existing_docs_by_rel: dict[str, dict[str, str | None]] = {}
    orphan_entries: list[list[str]] = []

    for d_id, d_data in ds_disk.items():
        if not isinstance(d_data, dict):
            continue
        rel = _rel_path_from_doc_entry(d_id, d_data, fd_disk, docs_root)
        if rel and not d_id.startswith("dup-"):
            fd_entry = fd_disk.get(d_id)
            sec_k = extract_section_key(fd_entry.get("content", "")) if isinstance(fd_entry, dict) else None
            existing_docs_by_rel.setdefault(rel, {})[d_id] = sec_k
        if d_data.get("status") == "processed":
            processed_ids.add(d_id)
            if rel:
                processed_rels.add(rel)
            fp_name = os.path.basename(d_data.get("file_path", "") or "")
            if fp_name and fp_name != "unknown_source":
                processed_basenames.add(fp_name)
        if _is_orphan_entry(
            d_id,
            d_data,
            rel,
            active_rel_set,
            all_files_str,
            active_basenames,
            docs_root,
            active_flat_keys=active_flat_keys,
        ):
            orphan_entries.append([d_id, rel or d_data.get("file_path", "") or d_id])

    def _entry_docs_processed(entry: dict[str, Any], rel_p: str, fname: str) -> bool:
        sec_map = entry.get("sections")
        if isinstance(sec_map, dict) and sec_map:
            return all(
                isinstance(s, dict) and s.get("doc_id") in processed_ids
                for s in sec_map.values()
            )
        cached_id = entry.get("doc_id")
        if cached_id in processed_ids or rel_p in processed_rels:
            return True
        if active_name_counts.get(fname, 0) == 1 and fname in processed_basenames:
            return True
        return False

    def _file_needs_update(p: Path) -> bool:
        entry = log_idx.get(str(p))
        if not isinstance(entry, dict):
            return True
        rel_p = str(p.relative_to(docs_root))
        if not _entry_docs_processed(entry, rel_p, p.name):
            return True
        if entry.get("mtime", 0) >= os.path.getmtime(p):
            return False
        ext_low = p.suffix.lower()
        stored_sha = entry.get("content_sha256")
        if stored_sha and ext_low in (".md", ".py", ".txt"):
            try:
                cur_norm_sha = compute_normalized_sha256(p.read_text(encoding="utf-8"), ext=ext_low)
                if cur_norm_sha == stored_sha:
                    return False
            except OSError:
                pass
        return True

    missing_files: list[str] = []
    if files:
        to_update, missing_files = _resolve_target_files(files, docs_root)
        to_delete: list[dict[str, str]] = []
        orphan_entries = []
    elif full:
        to_update = all_files
        to_delete = [
            {"path_str": p_str, "basename": Path(p_str).name}
            for p_str in log_idx
            if p_str not in all_files_str
        ]
    else:
        to_update = [p for p in all_files if _file_needs_update(p)]
        to_delete = [
            {"path_str": p_str, "basename": Path(p_str).name}
            for p_str in log_idx
            if p_str not in all_files_str
        ]

    eff_job_id = job_id or f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    job_dir = db_path / ".agent_jobs" / eff_job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    documents_meta: list[dict[str, Any]] = []
    chunks_meta: list[dict[str, Any]] = []
    images_meta: list[dict[str, Any]] = []
    section_files_meta: dict[str, dict[str, Any]] = {}
    tier_counts: Counter[str] = Counter()

    for path in to_update:
        try:
            rel_path = str(path.resolve().relative_to(docs_root))
        except ValueError:
            rel_path = str(path.resolve())
        file_sha = compute_file_sha256(path)
        ext = path.suffix.lower()

        if ext in IMAGE_EXTS:
            rec_model, tier, reason = classify_chunk_effort(rel_path, "", eff_profile, is_image=True)
            tier_counts[f"image:{rec_model}"] += 1
            images_meta.append(
                {
                    "rel_path": rel_path,
                    "source_abs": str(path.resolve()),
                    "file_name": path.name,
                    "file_sha256": file_sha,
                    "recommended_subagent_model": rec_model,
                    "effort_tier": tier,
                    "effort_reason": reason,
                }
            )
            documents_meta.append(
                {
                    "rel_path": rel_path,
                    "source_abs": str(path.resolve()),
                    "file_sha256": file_sha,
                    "ext": ext,
                    "is_image": True,
                    "chunk_hashes": [],
                }
            )
            continue

        if ext == ".md" and section_split:
            raw_md = path.read_text(encoding="utf-8")
            file_norm_sha = compute_normalized_sha256(raw_md, ext=".md")
            v_sections = split_markdown_into_virtual_sections(raw_md, rel_path)
            if v_sections is not None:
                prev_entry = log_idx.get(str(path.resolve())) if not full else {}
                prev_sections = (
                    prev_entry.get("sections")
                    if isinstance(prev_entry, dict) and isinstance(prev_entry.get("sections"), dict)
                    else {}
                )
                target_doc_ids = {s["doc_id"] for s in v_sections}
                obsolete_ids = [
                    did
                    for did in existing_docs_by_rel.get(rel_path, {})
                    if did not in target_doc_ids
                ]
                section_files_meta[rel_path] = {
                    "source_abs": str(path.resolve()),
                    "content_sha256": file_norm_sha,
                    "obsolete_doc_ids": obsolete_ids,
                    "sections": {
                        s["section_key"]: {
                            "doc_id": s["doc_id"],
                            "sha256": s["content_sha256"],
                            "title": s["section_title"],
                        }
                        for s in v_sections
                    },
                }
                for sec in v_sections:
                    prev_sec = prev_sections.get(sec["section_key"])
                    is_unchanged = (
                        not full
                        and sec["doc_id"] in processed_ids
                        and isinstance(prev_sec, dict)
                        and prev_sec.get("sha256") == sec["content_sha256"]
                    )
                    if is_unchanged:
                        continue
                    doc_chunk_hashes, ch_list, ch_tiers = _build_chunks_for_text(
                        content=sec["content"],
                        rel_path=rel_path,
                        eff_profile=eff_profile,
                        eff_tokenizer=eff_tokenizer,
                        eff_chunk_size=eff_chunk_size,
                        eff_overlap=eff_overlap,
                        section_key=sec["section_key"],
                        section_title=sec["section_title"],
                    )
                    tier_counts.update(ch_tiers)
                    chunks_meta.extend(ch_list)
                    documents_meta.append(
                        {
                            "rel_path": rel_path,
                            "source_abs": str(path.resolve()),
                            "file_sha256": file_sha,
                            "content_sha256": file_norm_sha,
                            "ext": ext,
                            "is_image": False,
                            "doc_id": sec["doc_id"],
                            "section_key": sec["section_key"],
                            "section_title": sec["section_title"],
                            "section_sha256": sec["content_sha256"],
                            "content_char_len": len(sec["content"]),
                            "chunk_hashes": doc_chunk_hashes,
                        }
                    )
                continue

        full_content = prepare_non_image_content(path, docs_root, db_path=db_path)
        if not full_content or not full_content.strip():
            continue

        if ext in (".md", ".py", ".txt"):
            file_norm_sha = compute_normalized_sha256(path.read_text(encoding="utf-8"), ext=ext)
        else:
            file_norm_sha = compute_normalized_sha256(full_content, ext=ext)

        doc_chunk_hashes, ch_list, ch_tiers = _build_chunks_for_text(
            content=full_content,
            rel_path=rel_path,
            eff_profile=eff_profile,
            eff_tokenizer=eff_tokenizer,
            eff_chunk_size=eff_chunk_size,
            eff_overlap=eff_overlap,
        )
        tier_counts.update(ch_tiers)
        chunks_meta.extend(ch_list)
        documents_meta.append(
            {
                "rel_path": rel_path,
                "source_abs": str(path.resolve()),
                "file_sha256": file_sha,
                "content_sha256": file_norm_sha,
                "ext": ext,
                "is_image": False,
                "doc_id": compute_doc_id(full_content),
                "content_char_len": len(full_content),
                "chunk_hashes": doc_chunk_hashes,
            }
        )

    manifest = {
        "job_id": eff_job_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "docs_root": str(docs_root),
        "db_path": str(db_path),
        "effort_profile": eff_profile,
        "effort_summary": {
            "label": profile_cfg["label"],
            "thinking_directive": profile_cfg["thinking_directive"],
            "tier_counts": dict(tier_counts),
        },
        "chunk_size": eff_chunk_size,
        "chunk_overlap": eff_overlap,
        "missing_files": missing_files,
        "documents": documents_meta,
        "section_files": section_files_meta,
        "chunks": chunks_meta,
        "images": images_meta,
        "to_delete": to_delete,
        "orphan_ids": orphan_entries,
    }

    manifest_path = job_dir / "manifest.json"
    extractions_path = job_dir / "extractions.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if not extractions_path.exists():
        extractions_template = {
            "job_id": eff_job_id,
            "vlm_descriptions": {},
            "vlm_extractions": {},
            "chunk_extractions": {},
            "entity_summaries": {},
        }
        extractions_path.write_text(
            json.dumps(extractions_template, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return {
        "job_id": eff_job_id,
        "job_dir": str(job_dir),
        "manifest_path": str(manifest_path),
        "extractions_path": str(extractions_path),
        "manifest": manifest,
    }


def validate_single_extraction(raw_output: str, label: str = "chunk") -> list[str]:
    """Verifie strictement format <|#|> + <|COMPLETE|> + absence de dollar/LaTeX."""
    errs: list[str] = []
    if not isinstance(raw_output, str) or not raw_output.strip():
        return [f"{label}: extraction vide"]

    if "$" in raw_output:
        errs.append(f"{label}: symbole dollar interdit detecte")
    if _LATEX_RE.search(raw_output):
        errs.append(f"{label}: commande LaTeX interdite detectee")
    if COMPLETION_DELIMITER not in raw_output:
        errs.append(f"{label}: balise finale '{COMPLETION_DELIMITER}' manquante")

    body = raw_output.split(COMPLETION_DELIMITER, 1)[0]
    entity_count = 0
    for line_no, line in enumerate(body.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split(TUPLE_DELIMITER)
        rec_type = parts[0].strip().lower()
        if rec_type == "entity":
            if len(parts) != 4 or any(not p.strip() for p in parts):
                errs.append(f"{label} L{line_no}: ligne 'entity' invalide ({len(parts)} champs, 4 attendus)")
            else:
                entity_count += 1
        elif rec_type == "relation":
            if len(parts) != 5 or any(not p.strip() for p in parts):
                errs.append(f"{label} L{line_no}: ligne 'relation' invalide ({len(parts)} champs, 5 attendus)")
        else:
            errs.append(f"{label} L{line_no}: type d'enregistrement inconnu '{parts[0][:24]}'")

    if entity_count == 0:
        errs.append(f"{label}: aucune entite valide extraite")
    return errs


def validate_agent_extractions(
    manifest: dict[str, Any],
    extractions: dict[str, Any],
    *,
    allow_stale: bool = False,
) -> tuple[list[str], dict[str, str], dict[str, str]]:
    """
    Valide completement extractions contre manifest avant ecriture en base.
    Retourne (erreurs, chunk_map_by_hash, vlm_docs_by_rel).
    """
    errors: list[str] = []
    chunk_map_raw = extractions.get("chunk_extractions") or {}
    vlm_desc_raw = extractions.get("vlm_descriptions") or {}
    vlm_ext_raw = extractions.get("vlm_extractions") or {}

    if not allow_stale:
        for doc in manifest.get("documents", []):
            src_abs = Path(doc["source_abs"])
            if not src_abs.exists():
                errors.append(f"Fichier source absent depuis preparation : {doc['rel_path']}")
                continue
            cur_sha = compute_file_sha256(src_abs)
            if cur_sha != doc.get("file_sha256"):
                errors.append(
                    f"Fichier modifie apres preparation ({doc['rel_path']}) — relancer rag_prepare_agent_index."
                )

    resolved_chunk_map: dict[str, str] = {}
    for ch in manifest.get("chunks", []):
        c_hash = ch["chunk_hash"]
        val = chunk_map_raw.get(c_hash)
        if not val:
            errors.append(
                f"Extraction manquante pour chunk {c_hash} ({ch['doc_rel']} #{ch['chunk_index']})"
            )
            continue
        lbl = f"{ch['doc_rel']}#{ch['chunk_index']}({c_hash[:8]})"
        errs = validate_single_extraction(val, label=lbl)
        if errs:
            errors.extend(errs)
            continue
        resolved_chunk_map[c_hash] = val.strip()
        exact_hash = ch.get("exact_sha256")
        if exact_hash:
            resolved_chunk_map[exact_hash] = val.strip()

    vlm_docs_by_rel: dict[str, str] = {}
    tokenizer = TiktokenTokenizer()
    chunk_size = int(manifest.get("chunk_size", 1600))
    chunk_overlap = int(manifest.get("chunk_overlap", 150))

    for img in manifest.get("images", []):
        rel_p = img["rel_path"]
        desc = (vlm_desc_raw.get(rel_p) or vlm_desc_raw.get(img["file_name"]) or "").strip()
        if not desc:
            errors.append(f"Description VLM manquante pour l'image : {rel_p}")
            continue
        if "$" in desc or _LATEX_RE.search(desc):
            errors.append(f"Description VLM ({rel_p}) contient un dollar ou une commande LaTeX interdite")
            continue
        vlm_doc = format_vlm_document(rel_p, img["file_name"], desc)
        vlm_docs_by_rel[rel_p] = vlm_doc

        img_chunks = _chunk_content(
            vlm_doc,
            tokenizer=tokenizer,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        single_ext = vlm_ext_raw.get(rel_p) or vlm_ext_raw.get(img["file_name"])
        for idx, ic in enumerate(img_chunks):
            ic_text = str(ic.get("content", ""))
            ic_hash = compute_chunk_hash(ic_text)
            ic_exact = hashlib.sha256(ic_text.encode("utf-8")).hexdigest()[:24]
            ext_txt = chunk_map_raw.get(ic_hash) or (single_ext if len(img_chunks) == 1 else None)
            if not ext_txt:
                errors.append(
                    f"Extraction graphe manquante pour l'image VLM {rel_p} (chunk {idx + 1}/{len(img_chunks)}, hash={ic_hash})"
                )
                continue
            errs = validate_single_extraction(ext_txt, label=f"VLM:{rel_p}#{idx}")
            if errs:
                errors.extend(errs)
                continue
            resolved_chunk_map[ic_hash] = ext_txt.strip()
            resolved_chunk_map[ic_exact] = ext_txt.strip()

    return errors, resolved_chunk_map, vlm_docs_by_rel


def deterministic_merge_descriptions(prompt: str, max_chars: int = 1800) -> str:
    """
    Synthetise localement sans LLM tiers un prompt summarize_entity_descriptions
    par deduplication deterministe des phrases JSON.
    """
    name_m = _SUMMARY_NAME_RE.search(prompt)
    entity_name = name_m.group(1).strip() if name_m else "Entite D-Bot"

    descriptions: list[str] = []
    fenced_m = re.search(r"Description List:\s*```(?:[A-Za-z0-9_-]*)\n(.*?)\n```", prompt, re.DOTALL)
    raw_block = fenced_m.group(1) if fenced_m else prompt
    for line in raw_block.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("{"):
            try:
                obj = json.loads(s)
                val = str(obj.get("description") or "").strip()
                if val:
                    descriptions.append(val)
                continue
            except Exception:
                pass
        if not s.startswith(("---", "Description", "Entity", "Relation", "```")):
            descriptions.append(s)

    seen_norm: set[str] = set()
    kept_parts: list[str] = []
    total_len = 0
    for desc in descriptions:
        clean = " ".join(desc.split()).strip()
        norm = clean.lower()
        if not clean or norm in seen_norm:
            continue
        if total_len + len(clean) + 2 > max_chars and kept_parts:
            break
        seen_norm.add(norm)
        kept_parts.append(clean)
        total_len += len(clean) + 2

    if not kept_parts:
        return f"{entity_name} : composant ou concept technique du projet D-Bot."
    joined = " ".join(kept_parts)
    if entity_name.lower() not in joined.lower()[:120]:
        return f"{entity_name} — {joined}"
    return joined


def build_replay_agent_llm(
    chunk_extractions_by_hash: dict[str, str],
    entity_summaries: dict[str, str] | None = None,
    stats_out: dict[str, int] | None = None,
):
    """
    Construit une coroutine llm_model_func 100% locale rejouant les extractions
    de l'agent sans appeler aucun LLM tiers.
    """
    summary_overrides = {
        str(k).strip().lower(): str(v).strip()
        for k, v in (entity_summaries or {}).items()
        if str(k).strip() and str(v).strip()
    }

    async def replay_agent_llm(
        prompt: str,
        system_prompt: str | None = None,
        history_messages: list | None = None,
        **kwargs,
    ) -> str:
        prompt_txt = str(prompt or "")
        m_input = _INPUT_TEXT_RE.search(prompt_txt)
        if m_input:
            raw_chunk = m_input.group(1)
            candidates = [
                compute_chunk_hash(raw_chunk),
                hashlib.sha256(raw_chunk.encode("utf-8")).hexdigest()[:24],
            ]
            for h in candidates:
                if h in chunk_extractions_by_hash:
                    if stats_out is not None:
                        stats_out["chunks_replayed"] = stats_out.get("chunks_replayed", 0) + 1
                    return chunk_extractions_by_hash[h]
            raise RuntimeError(
                f"Chunk inattendu lors du replay agent (hash={candidates[0]}) — verifier chunk_size/overlap."
            )

        if "Description List:" in prompt_txt and "---Task---" in prompt_txt:
            name_m = _SUMMARY_NAME_RE.search(prompt_txt)
            e_name = name_m.group(1).strip() if name_m else ""
            if stats_out is not None:
                stats_out["summaries_merged"] = stats_out.get("summaries_merged", 0) + 1
            if e_name.lower() in summary_overrides:
                return summary_overrides[e_name.lower()]
            return deterministic_merge_descriptions(prompt_txt)

        raise RuntimeError(
            "Appel LLM inattendu pendant le commit agent (ni extraction de chunk ni resume de fusion)."
        )

    return replay_agent_llm


def _swap_rag_runtime_for_replay(
    rag: LightRAG,
    replay_llm: Any,
    *,
    chunk_size: int,
    chunk_overlap: int,
    force_llm_summary_on_merge: int,
) -> dict[str, Any]:
    """Sauvegarde et remplace proprement les attributs + role_llm_funcs + chunker de LightRAG."""
    states = getattr(rag, "_role_llm_states", {}) or {}
    saved_roles = {k: st.raw_func for k, st in states.items()}
    saved = {
        "llm_model_func": rag.llm_model_func,
        "entity_extract_max_gleaning": rag.entity_extract_max_gleaning,
        "force_llm_summary_on_merge": rag.force_llm_summary_on_merge,
        "chunk_token_size": rag.chunk_token_size,
        "chunk_overlap_token_size": rag.chunk_overlap_token_size,
        "chunking_func": getattr(rag, "chunking_func", chunking_by_token_size),
        "role_raw_funcs": saved_roles,
    }
    rag.llm_model_func = replay_llm
    rag.entity_extract_max_gleaning = 0
    rag.force_llm_summary_on_merge = max(8, int(force_llm_summary_on_merge))
    rag.chunk_token_size = int(chunk_size)
    rag.chunk_overlap_token_size = int(chunk_overlap)
    rag.chunking_func = chunking_markdown_anchored
    if hasattr(rag, "_apply_chunk_size_overlay"):
        rag._apply_chunk_size_overlay()
    for st in states.values():
        st.raw_func = replay_llm
    if hasattr(rag, "_rebuild_role_llm_funcs"):
        rag._rebuild_role_llm_funcs()
    return saved


def _restore_rag_runtime(rag: LightRAG, saved: dict[str, Any]) -> None:
    rag.llm_model_func = saved["llm_model_func"]
    rag.entity_extract_max_gleaning = saved["entity_extract_max_gleaning"]
    rag.force_llm_summary_on_merge = saved["force_llm_summary_on_merge"]
    rag.chunk_token_size = saved["chunk_token_size"]
    rag.chunk_overlap_token_size = saved["chunk_overlap_token_size"]
    if "chunking_func" in saved:
        rag.chunking_func = saved["chunking_func"]
    if hasattr(rag, "_apply_chunk_size_overlay"):
        rag._apply_chunk_size_overlay()
    states = getattr(rag, "_role_llm_states", {}) or {}
    for k, raw_fn in (saved.get("role_raw_funcs") or {}).items():
        if k in states:
            states[k].raw_func = raw_fn
    if hasattr(rag, "_rebuild_role_llm_funcs"):
        rag._rebuild_role_llm_funcs()


async def _purge_doc_ids_rag(rag: LightRAG, doc_ids: list[str]) -> int:
    purged = 0
    seen: set[str] = set()
    for d_id in doc_ids:
        if not d_id or d_id in seen:
            continue
        seen.add(d_id)
        if not d_id.startswith("dup-"):
            try:
                res = await rag.adelete_by_doc_id(d_id)
                st = getattr(res, "status", "")
                if st == "success":
                    purged += 1
                    continue
                if st == "not_found":
                    continue
            except Exception:
                pass
        try:
            await rag.doc_status.delete([d_id])
            purged += 1
        except Exception:
            pass
    return purged


def _find_matching_ids_in_snapshot(
    ds_snapshot: dict,
    resolved_rels: dict[str, str | None],
    target_abs: str,
    rel_target: str | None,
    target_basename: str,
    allow_basename_match: bool,
    extra_doc_id: str | None = None,
    target_source_key: str | None = None,
) -> list[str]:
    matched: list[str] = []
    if extra_doc_id and extra_doc_id in ds_snapshot:
        matched.append(extra_doc_id)
    for d_id, d_data in ds_snapshot.items():
        rel_entry = resolved_rels.get(d_id)
        fp_entry = d_data.get("file_path", "") or ""
        if rel_target and rel_entry == rel_target:
            matched.append(d_id)
        elif fp_entry in (target_abs, rel_target) or (target_source_key and fp_entry == target_source_key):
            matched.append(d_id)
        elif (
            allow_basename_match
            and rel_entry is None
            and fp_entry != "unknown_source"
            and "/" not in fp_entry
            and os.path.basename(fp_entry) == target_basename
        ):
            matched.append(d_id)
    return matched


async def commit_agent_bundle(
    *,
    rag: LightRAG,
    db_path: Path,
    job_id_or_path: str,
    extractions: dict[str, Any] | None = None,
    extractions_path: str | None = None,
    apply_deletes: bool = True,
    force_llm_summary_on_merge: int = 24,
    allow_stale: bool = False,
    cleanup: bool = True,
) -> dict[str, Any]:
    """
    Valide les extractions fournies par l'agent et committe atomiquement chaque document
    dans le vrai pipeline LightRAG.ainsert() sans aucun appel LLM tiers.
    """
    db_path = db_path.resolve()
    job_dir = resolve_job_dir(db_path, job_id_or_path)
    manifest_file = job_dir / "manifest.json"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest agent introuvable : {manifest_file}")

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    docs_root = Path(manifest["docs_root"]).resolve()

    merged_extractions: dict[str, Any] = {
        "vlm_descriptions": {},
        "vlm_extractions": {},
        "chunk_extractions": {},
        "entity_summaries": {},
    }
    ext_file = Path(extractions_path).expanduser().resolve() if extractions_path else (job_dir / "extractions.json")
    if ext_file.exists():
        disk_ext = _load_json_dict(ext_file)
        for key in merged_extractions:
            if isinstance(disk_ext.get(key), dict):
                merged_extractions[key].update(disk_ext[key])
    if isinstance(extractions, dict):
        for key in merged_extractions:
            if isinstance(extractions.get(key), dict):
                merged_extractions[key].update(extractions[key])

    val_errors, chunk_map_by_hash, vlm_docs_by_rel = validate_agent_extractions(
        manifest, merged_extractions, allow_stale=allow_stale
    )
    if val_errors:
        raise ValueError("Validation extractions agent echouee :\n- " + "\n- ".join(val_errors))

    replay_stats: dict[str, int] = {"chunks_replayed": 0, "summaries_merged": 0}
    replay_llm = build_replay_agent_llm(
        chunk_map_by_hash,
        entity_summaries=merged_extractions.get("entity_summaries"),
        stats_out=replay_stats,
    )

    all_files = collect_docs_files(docs_root)
    active_name_counts = Counter(p.name for p in all_files)
    active_basenames = set(active_name_counts.keys())

    async with rag.doc_status._storage_lock:
        ds_snapshot = dict(rag.doc_status._data)
    fd_map: dict[str, Any] = {}
    if ds_snapshot and rag.full_docs:
        try:
            rows = await rag.full_docs.get_by_ids(list(ds_snapshot.keys()))
            fd_map = {d_id: row for d_id, row in zip(ds_snapshot.keys(), rows) if isinstance(row, dict)}
        except Exception:
            fd_map = {}

    resolved_rels = {
        d_id: _rel_path_from_doc_entry(d_id, d_data, fd_map, docs_root)
        for d_id, d_data in ds_snapshot.items()
    }
    log_path = db_path / "indexed_files.json"
    log_idx = _load_json_dict(log_path)

    deleted_count = 0
    orphan_count = 0
    replaced_count = 0
    committed_docs: list[dict[str, Any]] = []
    failed_docs: list[dict[str, str]] = []

    saved_runtime = _swap_rag_runtime_for_replay(
        rag,
        replay_llm,
        chunk_size=int(manifest.get("chunk_size", 1600)),
        chunk_overlap=int(manifest.get("chunk_overlap", 150)),
        force_llm_summary_on_merge=force_llm_summary_on_merge,
    )
    try:
        stale_dups = [d_id for d_id in list(ds_snapshot.keys()) if d_id.startswith("dup-")]
        if stale_dups:
            await _purge_doc_ids_rag(rag, stale_dups)
            for d_id in stale_dups:
                ds_snapshot.pop(d_id, None)
                resolved_rels.pop(d_id, None)

        if apply_deletes:
            for d_entry in manifest.get("to_delete", []):
                p_str = d_entry["path_str"]
                t_path = Path(p_str)
                try:
                    rel_t = str(t_path.resolve().relative_to(docs_root))
                except Exception:
                    rel_t = None
                expected_flat = (
                    (rel_t.replace("/", "--") if "/" in rel_t else f"root--{rel_t}")
                    if rel_t
                    else None
                )
                matched = _find_matching_ids_in_snapshot(
                    ds_snapshot,
                    resolved_rels,
                    p_str,
                    rel_t,
                    d_entry["basename"],
                    d_entry["basename"] not in active_basenames,
                    extra_doc_id=(log_idx.get(p_str) or {}).get("doc_id"),
                    target_source_key=expected_flat,
                )
                deleted_count += await _purge_doc_ids_rag(rag, matched)
                for mid in matched:
                    ds_snapshot.pop(mid, None)
                    resolved_rels.pop(mid, None)
                log_idx.pop(p_str, None)

            for o_id, _ in manifest.get("orphan_ids", []):
                orphan_count += await _purge_doc_ids_rag(rag, [o_id])
                ds_snapshot.pop(o_id, None)
                resolved_rels.pop(o_id, None)

        section_files = manifest.get("section_files") or {}
        if isinstance(section_files, dict):
            obsolete_all: list[str] = []
            for sf_meta in section_files.values():
                if isinstance(sf_meta, dict):
                    obsolete_all.extend(sf_meta.get("obsolete_doc_ids") or [])
            if obsolete_all:
                replaced_count += await _purge_doc_ids_rag(rag, obsolete_all)
                for oid in obsolete_all:
                    ds_snapshot.pop(oid, None)
                    resolved_rels.pop(oid, None)
                    fd_map.pop(oid, None)

        section_content_cache: dict[str, dict[str, str]] = {}
        staged_inserts: list[dict[str, Any]] = []

        for doc in manifest.get("documents", []):
            rel_path = doc["rel_path"]
            src_abs = Path(doc["source_abs"])
            sec_key = doc.get("section_key")

            if doc.get("is_image"):
                full_content = vlm_docs_by_rel.get(rel_path, "")
            elif sec_key:
                if rel_path not in section_content_cache:
                    raw_md = src_abs.read_text(encoding="utf-8")
                    secs = split_markdown_into_virtual_sections(raw_md, rel_path) or []
                    section_content_cache[rel_path] = {s["section_key"]: s["content"] for s in secs}
                full_content = section_content_cache[rel_path].get(sec_key, "")
            else:
                full_content = prepare_non_image_content(src_abs, docs_root, db_path=db_path)

            if not full_content.strip():
                failed_docs.append({"rel_path": rel_path, "section_key": sec_key, "reason": "contenu_vide"})
                continue

            expected_flat = rel_path.replace("/", "--") if "/" in rel_path else f"root--{rel_path}"
            base_name = src_abs.name
            if sec_key:
                matched = []
                for d_id, d_data in ds_snapshot.items():
                    if resolved_rels.get(d_id) != rel_path:
                        continue
                    fd_entry = fd_map.get(d_id)
                    existing_sec = extract_section_key(fd_entry.get("content", "")) if isinstance(fd_entry, dict) else None
                    if existing_sec in (sec_key, None) or d_id == doc.get("doc_id"):
                        matched.append(d_id)
            else:
                matched = _find_matching_ids_in_snapshot(
                    ds_snapshot,
                    resolved_rels,
                    str(src_abs),
                    rel_path,
                    base_name,
                    active_name_counts.get(base_name, 0) <= 1,
                    extra_doc_id=(log_idx.get(str(src_abs)) or {}).get("doc_id"),
                    target_source_key=expected_flat,
                )
            if matched:
                replaced_count += await _purge_doc_ids_rag(rag, matched)
                for mid in matched:
                    ds_snapshot.pop(mid, None)
                    resolved_rels.pop(mid, None)
                    fd_map.pop(mid, None)

            claimed_sources = build_claimed_source_map(ds_snapshot, resolved_rels)
            if sec_key:
                source_key = build_section_source_key(
                    rel_path,
                    sec_key,
                    claimed_sources=claimed_sources,
                )
            else:
                other_basenames = {
                    canonical_source_name(rv)
                    for rv in resolved_rels.values()
                    if rv and rv != rel_path
                }
                source_key = build_rag_source_key(
                    rel_path,
                    name_counts=active_name_counts,
                    claimed_sources=claimed_sources,
                    other_basenames=other_basenames,
                )
            doc_id = compute_doc_id(full_content)
            ds_snapshot[doc_id] = {"file_path": source_key, "status": "pending"}
            resolved_rels[doc_id] = rel_path
            staged_inserts.append(
                {
                    "doc": doc,
                    "rel_path": rel_path,
                    "src_abs": src_abs,
                    "sec_key": sec_key,
                    "doc_id": doc_id,
                    "source_key": source_key,
                    "content": full_content,
                }
            )

        if len(staged_inserts) == 1:
            it = staged_inserts[0]
            await rag.ainsert(it["content"], ids=[it["doc_id"]], file_paths=[it["source_key"]])
        elif len(staged_inserts) > 1:
            await rag.ainsert(
                [it["content"] for it in staged_inserts],
                ids=[it["doc_id"] for it in staged_inserts],
                file_paths=[it["source_key"] for it in staged_inserts],
            )

        failed_section_files: set[str] = set()
        for it in staged_inserts:
            doc = it["doc"]
            rel_path = it["rel_path"]
            src_abs = it["src_abs"]
            sec_key = it["sec_key"]
            doc_id = it["doc_id"]
            source_key = it["source_key"]

            inserted_row = await rag.doc_status.get_by_id(doc_id)
            if is_doc_processed(inserted_row):
                row_copy = (
                    dict(inserted_row)
                    if isinstance(inserted_row, dict)
                    else {"file_path": source_key, "status": "processed"}
                )
                row_copy.setdefault("file_path", source_key)
                ds_snapshot[doc_id] = row_copy
                resolved_rels[doc_id] = rel_path
                if not sec_key:
                    entry_log: dict[str, Any] = {
                        "mtime": os.path.getmtime(src_abs),
                        "doc_id": doc_id,
                    }
                    if doc.get("content_sha256"):
                        entry_log["content_sha256"] = doc["content_sha256"]
                    log_idx[str(src_abs)] = entry_log
                committed_entry: dict[str, Any] = {
                    "rel_path": rel_path,
                    "doc_id": doc_id,
                    "source_key": source_key,
                    "is_image": bool(doc.get("is_image")),
                }
                if sec_key:
                    committed_entry["section_key"] = sec_key
                committed_docs.append(committed_entry)
            else:
                if sec_key:
                    failed_section_files.add(rel_path)
                st_val = inserted_row.get("status") if isinstance(inserted_row, dict) else "absent"
                failed_docs.append({"rel_path": rel_path, "section_key": sec_key, "reason": f"statut={st_val}"})

        if isinstance(section_files, dict):
            for rel_p, sf_meta in section_files.items():
                if rel_p in failed_section_files or not isinstance(sf_meta, dict):
                    continue
                src_abs = Path(sf_meta["source_abs"])
                sec_dict = sf_meta.get("sections") or {}
                if not sec_dict or not src_abs.exists():
                    continue
                first_doc_id = next(iter(sec_dict.values()))["doc_id"]
                log_idx[str(src_abs)] = {
                    "mtime": os.path.getmtime(src_abs),
                    "doc_id": first_doc_id,
                    "content_sha256": sf_meta.get("content_sha256", ""),
                    "sections": sec_dict,
                }

        db_path.mkdir(parents=True, exist_ok=True)
        log_path.write_text(json.dumps(log_idx, indent=2, ensure_ascii=False), encoding="utf-8")
    finally:
        _restore_rag_runtime(rag, saved_runtime)

    if cleanup and not failed_docs and job_dir.parent.name == ".agent_jobs":
        shutil.rmtree(job_dir, ignore_errors=True)

    return {
        "job_id": manifest["job_id"],
        "effort_profile": manifest.get("effort_profile", "balanced"),
        "committed": committed_docs,
        "failed": failed_docs,
        "replaced_count": replaced_count,
        "deleted_count": deleted_count,
        "orphan_count": orphan_count,
        "chunks_replayed": replay_stats["chunks_replayed"],
        "summaries_merged": replay_stats["summaries_merged"],
    }


RAG_WATCH_FILES = (
    "indexed_files.json",
    "kv_store_doc_status.json",
    "kv_store_full_docs.json",
    "graph_chunk_entity_relation.graphml",
)


def compute_rag_disk_stamp(db_path: Path) -> tuple[tuple[str, int, int] | None, ...]:
    """Empreinte legere (mtime_ns, taille) des fichiers cles LightRAG sur disque."""
    stamp: list[tuple[str, int, int] | None] = []
    for fname in RAG_WATCH_FILES:
        fpath = db_path / fname
        try:
            st = fpath.stat()
            stamp.append((fname, st.st_mtime_ns, st.st_size))
        except OSError:
            stamp.append(None)
    return tuple(stamp)


def _is_flock_busy(exc: OSError) -> bool:
    return isinstance(exc, BlockingIOError) or exc.errno in (errno.EAGAIN, errno.EACCES)


def is_indexing_lock_active(db_path: Path) -> bool:
    """Indique si un autre processus detient actuellement le verrou .indexing.lock."""
    lock_file = Path(db_path) / ".indexing.lock"
    if not lock_file.exists():
        return False
    try:
        with lock_file.open("a+", encoding="utf-8") as fh:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                if _is_flock_busy(exc):
                    return True
                raise
            finally:
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                except OSError:
                    pass
    except OSError:
        return False
    return False


class IndexingFileLock:
    """Verrou POSIX non-bloquant evitant deux ecritures LightRAG concurrentes."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.lock_file = self.db_path / ".indexing.lock"
        self._fh: Any = None

    def acquire(self) -> IndexingFileLock:
        self.db_path.mkdir(parents=True, exist_ok=True)
        fh = self.lock_file.open("a+", encoding="utf-8")
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            fh.close()
            if _is_flock_busy(exc):
                raise RuntimeError(
                    f"Une indexation RAG est deja en cours sur {self.db_path}."
                ) from exc
            raise
        self._fh = fh
        return self

    def release(self) -> None:
        fh = self._fh
        self._fh = None
        if fh is None:
            return
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            fh.close()

    def __enter__(self) -> IndexingFileLock:
        return self.acquire()

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.release()
