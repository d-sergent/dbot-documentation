#!/opt/homebrew/bin/python3.11
"""
Assainissement chirurgical, deduplication et compaction de la base LightRAG D-Bot.

Fonctionnalites :
- Elagage des chunks orphelins dans GraphML, entity_chunks, relation_chunks et NanoVectorDB
- Deduplication des documents actifs (y compris entrees 'unknown_source' avec en-tete Fichier:)
- Purge des documents supprimes ou desormais exclus (ex. Code/rag/*.py, *test*.py)
- Compaction de kv_store_llm_response_cache.json (suppression des entrees extract orphelines)
- Synchronisation optionnelle vers le miroir de sauvegarde Google Drive
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

from agent_indexing import IndexingFileLock  # noqa: E402
from rag_chunking import (  # noqa: E402
    collect_docs_files,
    compute_normalized_sha256,
)
from rag_runtime import resolve_default_db_path, sync_db_to_backup_mirror  # noqa: E402
from source_key_utils import (  # noqa: E402
    build_active_source_aliases,
    build_claimed_source_map,
    build_rag_source_key,
    build_section_source_key,
    canonical_source_name,
    extract_rel_path,
    extract_section_key,
)

DEFAULT_DB_PATH = resolve_default_db_path()
DEFAULT_DOCS_ROOT = "/Users/Shared/Mon Google Drive Physique/Documentation"
SEP = "<SEP>"


def _atomic_write_text(target: Path, content: str) -> None:
    """Ecrit un fichier texte de maniere atomique dans le meme repertoire."""
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        tmp_path.replace(target)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def _atomic_write_json(target: Path, payload: object, indent: int | None = None) -> None:
    """Serialise et ecrit un fichier JSON de maniere atomique."""
    text = json.dumps(payload, ensure_ascii=False, indent=indent)
    _atomic_write_text(target, text)


def _load_json_dict(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def _prune_sep_ids(raw: str | None, valid_chunks: set[str]) -> list[str]:
    """Filtre une chaine d'IDs separes par <SEP> en preservant l'ordre sans doublons."""
    if not raw:
        return []
    seen: set[str] = set()
    kept: list[str] = []
    for cid in str(raw).split(SEP):
        if cid and cid in valid_chunks and cid not in seen:
            seen.add(cid)
            kept.append(cid)
    return kept


def _load_valid_chunk_ids(db_path: Path) -> tuple[set[str], int, int]:
    """Charge l'intersection exacte des chunks presentes dans text_chunks et vdb_chunks."""
    tc_raw = json.loads((db_path / "kv_store_text_chunks.json").read_text(encoding="utf-8"))
    vdb_raw = json.loads((db_path / "vdb_chunks.json").read_text(encoding="utf-8"))
    tc_ids = set(tc_raw.keys())
    vdb_ids = {row["__id__"] for row in vdb_raw.get("data", [])}
    return tc_ids & vdb_ids, len(tc_ids), len(vdb_ids)


def _repair_graphml(db_path: Path, valid_chunks: set[str], apply: bool) -> dict[str, int]:
    """Elague les source_id orphelins et supprime les noeuds/aretes sans aucun chunk valide."""
    graph_path = db_path / "graph_chunk_entity_relation.graphml"
    if not graph_path.is_file():
        return {
            "removed_nodes": 0,
            "pruned_nodes": 0,
            "kept_nodes": 0,
            "removed_edges": 0,
            "pruned_edges": 0,
            "kept_edges": 0,
        }
    graph = nx.read_graphml(graph_path)

    nodes_to_remove: list[str] = []
    pruned_nodes = 0
    for node_id, attrs in graph.nodes(data=True):
        raw_src = attrs.get("source_id", "")
        raw_list = [c for c in str(raw_src).split(SEP) if c]
        kept = _prune_sep_ids(raw_src, valid_chunks)
        if not kept:
            nodes_to_remove.append(node_id)
        elif kept != raw_list:
            pruned_nodes += 1
            attrs["source_id"] = SEP.join(kept)

    removed_node_set = set(nodes_to_remove)
    edges_to_remove: list[tuple] = []
    pruned_edges = 0
    for u, v, attrs in graph.edges(data=True):
        if u in removed_node_set or v in removed_node_set:
            edges_to_remove.append((u, v))
            continue
        raw_src = attrs.get("source_id", "")
        raw_list = [c for c in str(raw_src).split(SEP) if c]
        kept = _prune_sep_ids(raw_src, valid_chunks)
        if not kept:
            edges_to_remove.append((u, v))
        elif kept != raw_list:
            pruned_edges += 1
            attrs["source_id"] = SEP.join(kept)

    graph.remove_edges_from(edges_to_remove)
    graph.remove_nodes_from(nodes_to_remove)

    if apply:
        fd, tmp_name = tempfile.mkstemp(prefix=".graphml.", dir=str(db_path))
        os.close(fd)
        tmp_path = Path(tmp_name)
        try:
            nx.write_graphml(graph, tmp_path)
            tmp_path.replace(graph_path)
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise

    return {
        "removed_nodes": len(nodes_to_remove),
        "pruned_nodes": pruned_nodes,
        "kept_nodes": graph.number_of_nodes(),
        "removed_edges": len(edges_to_remove),
        "pruned_edges": pruned_edges,
        "kept_edges": graph.number_of_edges(),
    }


def _repair_kv_chunks(file_path: Path, valid_chunks: set[str], apply: bool) -> dict[str, int]:
    """Filtre chunk_ids dans kv_store_entity_chunks.json ou kv_store_relation_chunks.json."""
    if not file_path.is_file():
        return {"removed": 0, "pruned": 0, "kept": 0}
    store = json.loads(file_path.read_text(encoding="utf-8"))
    cleaned: dict = {}
    removed = 0
    pruned = 0

    for key, val in store.items():
        if isinstance(val, dict):
            orig = list(val.get("chunk_ids", []))
            kept = [c for c in dict.fromkeys(orig) if c in valid_chunks]
            if not kept:
                removed += 1
                continue
            if kept != orig or val.get("count") != len(kept):
                pruned += 1
                val = dict(val)
                val["chunk_ids"] = kept
                val["count"] = len(kept)
            cleaned[key] = val
        elif isinstance(val, list):
            kept = [c for c in dict.fromkeys(val) if c in valid_chunks]
            if not kept:
                removed += 1
                continue
            if kept != val:
                pruned += 1
            cleaned[key] = kept

    if apply and (removed > 0 or pruned > 0):
        _atomic_write_json(file_path, cleaned)

    return {"removed": removed, "pruned": pruned, "kept": len(cleaned)}


def _repair_vdb(file_path: Path, valid_chunks: set[str], apply: bool) -> dict[str, int]:
    """Synchronise un index NanoVectorDB JSON en preservant exactement la matrice float32."""
    if not file_path.is_file():
        return {"removed": 0, "pruned": 0, "kept": 0}
    raw = json.loads(file_path.read_text(encoding="utf-8"))
    dim = int(raw["embedding_dim"])
    rows = raw.get("data", [])
    matrix = np.frombuffer(base64.b64decode(raw["matrix"]), dtype=np.float32).reshape(-1, dim)
    if len(rows) != matrix.shape[0]:
        raise RuntimeError(
            f"Incoherence matrice dans {file_path.name}: len(data)={len(rows)} vs matrix={matrix.shape[0]}"
        )

    keep_indices: list[int] = []
    kept_rows: list[dict] = []
    removed = 0
    pruned = 0

    for idx, row in enumerate(rows):
        raw_src = row.get("source_id", "")
        raw_list = [c for c in str(raw_src).split(SEP) if c]
        kept = _prune_sep_ids(raw_src, valid_chunks)
        if not kept:
            removed += 1
            continue
        if kept != raw_list:
            pruned += 1
            row = dict(row)
            row["source_id"] = SEP.join(kept)
        keep_indices.append(idx)
        kept_rows.append(row)

    new_matrix = matrix[keep_indices] if keep_indices else np.empty((0, dim), dtype=np.float32)
    if new_matrix.shape != (len(kept_rows), dim):
        raise RuntimeError(f"Erreur shape apres filtrage sur {file_path.name}")

    if apply and (removed > 0 or pruned > 0):
        updated = {
            **raw,
            "data": kept_rows,
            "matrix": base64.b64encode(np.ascontiguousarray(new_matrix, dtype=np.float32).tobytes()).decode(),
        }
        _atomic_write_json(file_path, updated)

    return {"removed": removed, "pruned": pruned, "kept": len(kept_rows)}


def _prune_vdb_chunks(
    file_path: Path,
    kept_chunk_ids: set[str],
    repaired_chunk_fps: dict[str, str],
    apply: bool,
) -> dict[str, int]:
    """Filtre vdb_chunks.json sur les chunks survivants tout en preservant la matrice float32."""
    if not file_path.is_file():
        return {"removed": 0, "updated_fp": 0, "kept": 0}
    raw = json.loads(file_path.read_text(encoding="utf-8"))
    dim = int(raw["embedding_dim"])
    rows = raw.get("data", [])
    matrix = np.frombuffer(base64.b64decode(raw["matrix"]), dtype=np.float32).reshape(-1, dim)
    if len(rows) != matrix.shape[0]:
        raise RuntimeError(
            f"Incoherence matrice dans {file_path.name}: len(data)={len(rows)} vs matrix={matrix.shape[0]}"
        )

    keep_indices: list[int] = []
    kept_rows: list[dict] = []
    removed = 0
    updated_fp = 0

    for idx, row in enumerate(rows):
        cid = str(row.get("__id__", ""))
        if cid not in kept_chunk_ids:
            removed += 1
            continue
        new_fp = repaired_chunk_fps.get(cid)
        if new_fp and row.get("file_path") != new_fp:
            row = dict(row)
            row["file_path"] = new_fp
            updated_fp += 1
        keep_indices.append(idx)
        kept_rows.append(row)

    new_matrix = matrix[keep_indices] if keep_indices else np.empty((0, dim), dtype=np.float32)
    if new_matrix.shape != (len(kept_rows), dim):
        raise RuntimeError(f"Erreur shape apres filtrage sur {file_path.name}")

    if apply and (removed > 0 or updated_fp > 0):
        updated = {
            **raw,
            "data": kept_rows,
            "matrix": base64.b64encode(np.ascontiguousarray(new_matrix, dtype=np.float32).tobytes()).decode(),
        }
        _atomic_write_json(file_path, updated)

    return {"removed": removed, "updated_fp": updated_fp, "kept": len(kept_rows)}


def _resolve_doc_rel_map(
    ds_map: dict[str, Any],
    fd_map: dict[str, Any],
    idx_map: dict[str, Any],
    docs_root: Path,
    active_rel_set: set[str],
    active_basenames: set[str],
) -> dict[str, str | None]:
    """Resout le chemin relatif canonique de chaque doc_id dans doc_status."""
    doc_id_to_idx_rel: dict[str, str] = {}
    for abs_p, entry in idx_map.items():
        if not isinstance(entry, dict):
            continue
        try:
            rel = str(Path(abs_p).resolve().relative_to(docs_root.resolve()))
        except Exception:
            rel = abs_p
        if entry.get("doc_id"):
            doc_id_to_idx_rel[str(entry["doc_id"])] = rel
        for sec in (entry.get("sections") or {}).values():
            if isinstance(sec, dict) and sec.get("doc_id"):
                doc_id_to_idx_rel[str(sec["doc_id"])] = rel

    flat_to_rel: dict[str, str] = {}
    base_to_unique_rel: dict[str, str] = {}
    base_counts: Counter[str] = Counter()
    for rel in active_rel_set:
        flat = rel.replace("/", "--") if "/" in rel else f"root--{rel}"
        flat_to_rel[flat] = rel
        b = os.path.basename(rel)
        base_counts[b] += 1
        base_to_unique_rel[b] = rel

    resolved: dict[str, str | None] = {}
    for d_id, d_data in ds_map.items():
        if not isinstance(d_data, dict):
            continue
        fd_entry = fd_map.get(d_id)
        rel = extract_rel_path(fd_entry.get("content", "")) if isinstance(fd_entry, dict) else None
        if not rel and d_id in doc_id_to_idx_rel:
            rel = doc_id_to_idx_rel[d_id]
        if not rel:
            fp = str(d_data.get("file_path", "") or "").strip()
            if "/" in fp:
                try:
                    p = Path(fp)
                    rel = (
                        str(p.resolve().relative_to(docs_root.resolve()))
                        if p.is_absolute()
                        else fp
                    )
                except Exception:
                    rel = fp
            else:
                canon = canonical_source_name(fp)
                if fp in flat_to_rel:
                    rel = flat_to_rel[fp]
                elif canon in flat_to_rel:
                    rel = flat_to_rel[canon]
                elif canon in active_basenames and base_counts.get(canon, 0) == 1:
                    rel = base_to_unique_rel[canon]
        resolved[d_id] = rel
    return resolved


def _compact_llm_cache(
    db_path: Path,
    kept_chunk_ids: set[str],
    apply: bool,
    summary_keep_limit: int = 1500,
) -> dict[str, int]:
    """Supprime les entrees 'extract' orphelines et borne les anciens 'summary'."""
    cache_path = db_path / "kv_store_llm_response_cache.json"
    if not cache_path.is_file():
        return {"before": 0, "after": 0, "removed_extract": 0, "removed_summary": 0}

    tc_map = _load_json_dict(db_path / "kv_store_text_chunks.json")
    referenced_extract_keys: set[str] = set()
    for cid in kept_chunk_ids:
        tc_row = tc_map.get(cid)
        if isinstance(tc_row, dict):
            for ck in tc_row.get("llm_cache_list") or []:
                referenced_extract_keys.add(str(ck))

    cache_map = _load_json_dict(cache_path)
    before_count = len(cache_map)
    kept_cache: dict[str, Any] = {}
    summary_items: list[tuple[int, str, Any]] = []
    removed_extract = 0

    for k, v in cache_map.items():
        if not isinstance(v, dict):
            kept_cache[k] = v
            continue
        ctype = str(v.get("cache_type") or "").strip().lower()
        if ctype == "extract":
            cid = str(v.get("chunk_id") or "")
            if k in referenced_extract_keys or (cid and cid in kept_chunk_ids):
                kept_cache[k] = v
            else:
                removed_extract += 1
        elif ctype == "summary":
            ts = int(v.get("update_time") or v.get("create_time") or 0)
            summary_items.append((ts, k, v))
        else:
            kept_cache[k] = v

    summary_items.sort(key=lambda item: item[0], reverse=True)
    kept_summaries = summary_items[: max(0, int(summary_keep_limit))]
    removed_summary = len(summary_items) - len(kept_summaries)
    for _, sk, sv in kept_summaries:
        kept_cache[sk] = sv

    if apply and (removed_extract > 0 or removed_summary > 0):
        _atomic_write_json(cache_path, kept_cache)

    return {
        "before": before_count,
        "after": len(kept_cache),
        "removed_extract": removed_extract,
        "removed_summary": removed_summary,
    }


def _run_doc_and_chunk_hygiene(
    db_path: Path,
    docs_root: Path,
    *,
    dedupe_docs: bool,
    purge_excluded: bool,
    apply: bool,
) -> tuple[dict[str, Any], set[str]]:
    """Nettoie doublons, unknown_source et fichiers exclus/supprimes de maniere atomique."""
    ds_path = db_path / "kv_store_doc_status.json"
    fd_path = db_path / "kv_store_full_docs.json"
    fe_path = db_path / "kv_store_full_entities.json"
    fr_path = db_path / "kv_store_full_relations.json"
    tc_path = db_path / "kv_store_text_chunks.json"
    vdb_c_path = db_path / "vdb_chunks.json"
    idx_path = db_path / "indexed_files.json"

    ds_map = _load_json_dict(ds_path)
    fd_map = _load_json_dict(fd_path)
    fe_map = _load_json_dict(fe_path)
    fr_map = _load_json_dict(fr_path)
    tc_map = _load_json_dict(tc_path)
    idx_map = _load_json_dict(idx_path)

    vdb_raw = json.loads(vdb_c_path.read_text(encoding="utf-8"))
    vdb_chunk_ids = {str(r.get("__id__")) for r in (vdb_raw.get("data") or []) if isinstance(r, dict)}

    docs_dir = docs_root.resolve()
    disk_files = collect_docs_files(docs_dir)
    all_files_str = {str(p.resolve()) for p in disk_files}
    disk_by_rel = {str(p.resolve().relative_to(docs_dir)): p.resolve() for p in disk_files}
    active_rel_set = set(disk_by_rel.keys())
    active_name_counts = Counter(p.name for p in disk_files)
    active_basenames = set(active_name_counts.keys())
    active_flat_keys = build_active_source_aliases(active_rel_set)

    resolved_rels = _resolve_doc_rel_map(
        ds_map, fd_map, idx_map, docs_dir, active_rel_set, active_basenames
    )

    idx_expected_ids: set[str] = set()
    for entry in idx_map.values():
        if not isinstance(entry, dict):
            continue
        if entry.get("doc_id"):
            idx_expected_ids.add(str(entry["doc_id"]))
        for sec in (entry.get("sections") or {}).values():
            if isinstance(sec, dict) and sec.get("doc_id"):
                idx_expected_ids.add(str(sec["doc_id"]))

    docs_to_remove: set[str] = set()
    purged_dup_prefix = 0
    purged_excluded_count = 0
    deduped_count = 0

    for d_id, d_data in ds_map.items():
        if d_id.startswith("dup-"):
            docs_to_remove.add(d_id)
            purged_dup_prefix += 1
            continue
        if not isinstance(d_data, dict):
            docs_to_remove.add(d_id)
            continue
        rel = resolved_rels.get(d_id)
        if purge_excluded:
            is_excluded = False
            if rel is not None:
                is_excluded = rel not in active_rel_set
            else:
                fp = str(d_data.get("file_path", "") or "").strip()
                if fp and fp != "unknown_source":
                    base = os.path.basename(fp)
                    if fp not in active_flat_keys and base not in active_flat_keys and base not in active_basenames:
                        is_excluded = True
            if is_excluded:
                docs_to_remove.add(d_id)
                purged_excluded_count += 1

    if dedupe_docs:
        grouped: dict[tuple[str, str | None], list[str]] = defaultdict(list)
        rel_sections: dict[str, set[str | None]] = defaultdict(set)
        for d_id in ds_map:
            if d_id in docs_to_remove:
                continue
            rel = resolved_rels.get(d_id)
            if not rel:
                continue
            fd_entry = fd_map.get(d_id)
            sec_k = extract_section_key(fd_entry.get("content", "")) if isinstance(fd_entry, dict) else None
            grouped[(rel, sec_k)].append(d_id)
            rel_sections[rel].add(sec_k)

        for rel, sk_set in rel_sections.items():
            non_null_secs = {sk for sk in sk_set if sk is not None}
            if len(non_null_secs) >= 2 and None in sk_set:
                for old_mono_id in grouped.get((rel, None), []):
                    docs_to_remove.add(old_mono_id)
                    deduped_count += 1

        def _candidate_rank(did: str) -> tuple[int, int, int, int, int, str]:
            d_row = ds_map.get(did) or {}
            st_ok = 1 if str(d_row.get("status", "")).lower() == "processed" else 0
            c_list = list(d_row.get("chunks_list") or [])
            valid_c = sum(1 for cid in c_list if cid in tc_map and cid in vdb_chunk_ids)
            in_idx = 1 if did in idx_expected_ids else 0
            c_opts = str(((d_row.get("metadata") or {}).get("chunk_opts") or ""))
            is_1600 = 1 if "1600" in c_opts else 0
            upd = str(d_row.get("updated_at") or d_row.get("created_at") or "")
            return (st_ok, 1 if valid_c > 0 else 0, in_idx, is_1600, valid_c, upd)

        for (rel, sec_k), dids in grouped.items():
            if len(dids) <= 1:
                continue
            ranked = sorted(dids, key=_candidate_rank, reverse=True)
            for loser in ranked[1:]:
                if loser not in docs_to_remove:
                    docs_to_remove.add(loser)
                    deduped_count += 1

        # Retire les entrees bloquees en 'processing' sans aucun chunk valide
        for d_id, d_row in list(ds_map.items()):
            if d_id in docs_to_remove or not isinstance(d_row, dict):
                continue
            if str(d_row.get("status", "")).lower() != "processed":
                c_list = list(d_row.get("chunks_list") or [])
                valid_c = sum(1 for cid in c_list if cid in tc_map and cid in vdb_chunk_ids)
                if valid_c == 0:
                    docs_to_remove.add(d_id)

    kept_doc_ids = [d_id for d_id in ds_map if d_id not in docs_to_remove]

    # Repare les file_path 'unknown_source' sur les documents survivants
    repaired_doc_fps: dict[str, str] = {}
    repaired_chunk_fps: dict[str, str] = {}
    if dedupe_docs:
        surviving_ds = {d_id: ds_map[d_id] for d_id in kept_doc_ids}
        surviving_rels = {d_id: resolved_rels.get(d_id) for d_id in kept_doc_ids}
        claimed_sources = build_claimed_source_map(surviving_ds, surviving_rels)
        for d_id in kept_doc_ids:
            d_row = ds_map[d_id]
            rel = resolved_rels.get(d_id)
            if not rel or not isinstance(d_row, dict):
                continue
            fp_cur = str(d_row.get("file_path") or "").strip()
            if fp_cur not in ("", "unknown_source") and "/" not in fp_cur:
                continue
            fd_entry = fd_map.get(d_id)
            sec_k = extract_section_key(fd_entry.get("content", "")) if isinstance(fd_entry, dict) else None
            if sec_k:
                new_fp = build_section_source_key(rel, sec_k, claimed_sources=claimed_sources)
            else:
                other_bases = {
                    canonical_source_name(rv)
                    for did2, rv in surviving_rels.items()
                    if rv and rv != rel and did2 not in docs_to_remove
                }
                new_fp = build_rag_source_key(
                    rel,
                    name_counts=active_name_counts,
                    claimed_sources=claimed_sources,
                    other_basenames=other_bases,
                )
            claimed_sources.setdefault(canonical_source_name(new_fp), set()).add(rel)
            repaired_doc_fps[d_id] = new_fp
            for cid in d_row.get("chunks_list") or []:
                repaired_chunk_fps[str(cid)] = new_fp

    kept_chunk_ids: set[str] = set()
    for d_id in kept_doc_ids:
        for cid in (ds_map[d_id].get("chunks_list") or []):
            if cid in tc_map and cid in vdb_chunk_ids:
                kept_chunk_ids.add(str(cid))

    # Synchronise indexed_files.json avec les survivants
    new_idx_map: dict[str, Any] = {}
    survivors_by_rel: dict[str, list[tuple[str, str | None]]] = defaultdict(list)
    for d_id in kept_doc_ids:
        rel = resolved_rels.get(d_id)
        if rel:
            fd_entry = fd_map.get(d_id)
            sk = extract_section_key(fd_entry.get("content", "")) if isinstance(fd_entry, dict) else None
            survivors_by_rel[rel].append((d_id, sk))

    for abs_p_str, entry in idx_map.items():
        try:
            res_abs = str(Path(abs_p_str).resolve())
        except Exception:
            res_abs = abs_p_str
        if res_abs not in all_files_str:
            continue
        if not isinstance(entry, dict):
            continue
        new_entry = dict(entry)
        p_obj = Path(res_abs)
        rel = str(p_obj.relative_to(docs_dir))
        surv = survivors_by_rel.get(rel, [])
        if surv:
            sec_surv = [(did, sk) for did, sk in surv if sk is not None]
            if len(sec_surv) >= 2:
                sec_dict = {}
                for did, sk in sec_surv:
                    sec_dict[str(sk)] = {"doc_id": did, "sha256": "", "title": str(sk)}
                new_entry["doc_id"] = sec_surv[0][0]
                new_entry["sections"] = sec_dict
            else:
                new_entry["doc_id"] = surv[0][0]
                new_entry.pop("sections", None)
            if p_obj.suffix.lower() in (".md", ".py", ".txt") and not new_entry.get("content_sha256"):
                try:
                    if p_obj.stat().st_mtime <= float(new_entry.get("mtime", 0)) + 0.5:
                        new_entry["content_sha256"] = compute_normalized_sha256(
                            p_obj.read_text(encoding="utf-8"), ext=p_obj.suffix.lower()
                        )
                except OSError:
                    pass
        new_idx_map[res_abs] = new_entry

    pruned_chunks_kv = len(tc_map) - len([cid for cid in tc_map if cid in kept_chunk_ids])

    if apply:
        new_ds = {}
        for d_id in kept_doc_ids:
            row = dict(ds_map[d_id])
            if d_id in repaired_doc_fps:
                row["file_path"] = repaired_doc_fps[d_id]
            new_ds[d_id] = row
        _atomic_write_json(ds_path, new_ds)
        _atomic_write_json(fd_path, {k: v for k, v in fd_map.items() if k in kept_doc_ids})
        _atomic_write_json(fe_path, {k: v for k, v in fe_map.items() if k in kept_doc_ids})
        _atomic_write_json(fr_path, {k: v for k, v in fr_map.items() if k in kept_doc_ids})

        new_tc = {}
        for cid in tc_map:
            if cid not in kept_chunk_ids:
                continue
            crow = dict(tc_map[cid]) if isinstance(tc_map[cid], dict) else tc_map[cid]
            if isinstance(crow, dict) and cid in repaired_chunk_fps:
                crow["file_path"] = repaired_chunk_fps[cid]
            new_tc[cid] = crow
        _atomic_write_json(tc_path, new_tc)
        _atomic_write_json(idx_path, new_idx_map, indent=2)

    vdb_c_stats = _prune_vdb_chunks(vdb_c_path, kept_chunk_ids, repaired_chunk_fps, apply=apply)

    summary = {
        "docs_before": len(ds_map),
        "docs_after": len(kept_doc_ids),
        "removed_docs": len(docs_to_remove),
        "purged_dup_prefix": purged_dup_prefix,
        "purged_excluded": purged_excluded_count,
        "deduped_docs": deduped_count,
        "repaired_unknown_source": len(repaired_doc_fps),
        "chunks_before": len(tc_map),
        "chunks_after": len(kept_chunk_ids),
        "pruned_text_chunks": pruned_chunks_kv,
        "vdb_chunks": vdb_c_stats,
        "indexed_files_before": len(idx_map),
        "indexed_files_after": len(new_idx_map),
    }
    return summary, kept_chunk_ids


def create_backup(db_path: Path) -> Path:
    """Cree une sauvegarde complete horodatee dans le repertoire parent."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"{db_path.name}_backup_{stamp}"
    shutil.copytree(db_path, backup_path)
    return backup_path


def run_repair(
    db_path: Path,
    apply: bool,
    make_backup: bool,
    *,
    docs_root: Path = Path(DEFAULT_DOCS_ROOT),
    dedupe_docs: bool = False,
    purge_excluded: bool = False,
    compact_cache: bool = False,
    sync_mirror: bool = False,
) -> int:
    """Execute le diagnostic, la reparation optionnelle et la verification finale."""
    if not db_path.is_dir():
        print(f"Repertoire introuvable : {db_path}")
        return 1

    def _execute_all() -> int:
        if apply and make_backup:
            backup_path = create_backup(db_path)
            print(f"Sauvegarde creee : {backup_path}")

        hygiene_stats: dict[str, Any] | None = None
        if dedupe_docs or purge_excluded:
            hygiene_stats, valid_chunks = _run_doc_and_chunk_hygiene(
                db_path,
                docs_root,
                dedupe_docs=dedupe_docs,
                purge_excluded=purge_excluded,
                apply=apply,
            )
            tc_count = hygiene_stats["chunks_before"]
            vdb_count = hygiene_stats["vdb_chunks"]["kept"] + hygiene_stats["vdb_chunks"]["removed"]
        else:
            valid_chunks, tc_count, vdb_count = _load_valid_chunk_ids(db_path)

        print(
            f"Base : {db_path}\n"
            f"Chunks valides retenus : {len(valid_chunks)} (text_chunks={tc_count}, vdb_chunks={vdb_count})"
        )

        g_stats = _repair_graphml(db_path, valid_chunks, apply=apply)
        ec_stats = _repair_kv_chunks(db_path / "kv_store_entity_chunks.json", valid_chunks, apply=apply)
        rc_stats = _repair_kv_chunks(db_path / "kv_store_relation_chunks.json", valid_chunks, apply=apply)
        ve_stats = _repair_vdb(db_path / "vdb_entities.json", valid_chunks, apply=apply)
        vr_stats = _repair_vdb(db_path / "vdb_relationships.json", valid_chunks, apply=apply)
        cache_stats = (
            _compact_llm_cache(db_path, valid_chunks, apply=apply)
            if compact_cache
            else None
        )

        mode_label = "APPLIQUE" if apply else "SIMULATION (--dry-run)"
        print(f"\n=== BILAN [{mode_label}] ===")
        if hygiene_stats is not None:
            print(f"  doc_hygiene      : {hygiene_stats}")
        print(f"  graphml          : {g_stats}")
        print(f"  entity_chunks    : {ec_stats}")
        print(f"  relation_chunks  : {rc_stats}")
        print(f"  vdb_entities     : {ve_stats}")
        print(f"  vdb_relationships: {vr_stats}")
        if cache_stats is not None:
            print(f"  llm_cache        : {cache_stats}")

        if apply:
            check_g = _repair_graphml(db_path, valid_chunks, apply=False)
            check_ec = _repair_kv_chunks(db_path / "kv_store_entity_chunks.json", valid_chunks, apply=False)
            check_rc = _repair_kv_chunks(db_path / "kv_store_relation_chunks.json", valid_chunks, apply=False)
            check_ve = _repair_vdb(db_path / "vdb_entities.json", valid_chunks, apply=False)
            check_vr = _repair_vdb(db_path / "vdb_relationships.json", valid_chunks, apply=False)
            leftovers = (
                check_g["removed_nodes"] + check_g["pruned_nodes"]
                + check_g["removed_edges"] + check_g["pruned_edges"]
                + check_ec["removed"] + check_ec["pruned"]
                + check_rc["removed"] + check_rc["pruned"]
                + check_ve["removed"] + check_ve["pruned"]
                + check_vr["removed"] + check_vr["pruned"]
            )
            print(f"Verification post-reparation : reliquats orphelins = {leftovers}")
            if leftovers != 0:
                return 2
            if sync_mirror:
                ok_m, msg_m = sync_db_to_backup_mirror(db_path)
                print(f"Miroir sauvegarde : {msg_m}")
                if not ok_m:
                    return 3
        return 0

    if apply:
        with IndexingFileLock(db_path):
            return _execute_all()
    return _execute_all()


def main() -> int:
    parser = argparse.ArgumentParser(description="Assainit, deduplique et compacte la base LightRAG D-Bot")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Chemin de la base LightRAG")
    parser.add_argument("--docs-root", default=DEFAULT_DOCS_ROOT, help="Racine de la documentation")
    parser.add_argument("--dry-run", action="store_true", help="Analyse sans modifier la base (defaut si --apply absent)")
    parser.add_argument("--apply", action="store_true", help="Applique les suppressions/elagages avec sauvegarde")
    parser.add_argument("--no-backup", action="store_true", help="Desactive la copie de sauvegarde prealable")
    parser.add_argument("--dedupe-docs", action="store_true", help="Deduplique les doc_id et repare unknown_source")
    parser.add_argument("--purge-excluded", action="store_true", help="Purge les documents supprimes ou desormais exclus")
    parser.add_argument("--compact-cache", action="store_true", help="Supprime les entrees extract orphelines du cache LLM")
    parser.add_argument(
        "--full-hygiene",
        action="store_true",
        help="Active --dedupe-docs, --purge-excluded et --compact-cache en une passe",
    )
    parser.add_argument(
        "--sync-mirror",
        action="store_true",
        help="Synchronise la base locale vers le miroir Google Drive apres reparation",
    )
    args = parser.parse_args()
    do_dedupe = bool(args.dedupe_docs or args.full_hygiene)
    do_purge = bool(args.purge_excluded or args.full_hygiene)
    do_compact = bool(args.compact_cache or args.full_hygiene)
    return run_repair(
        Path(args.db_path),
        apply=args.apply,
        make_backup=not args.no_backup,
        docs_root=Path(args.docs_root),
        dedupe_docs=do_dedupe,
        purge_excluded=do_purge,
        compact_cache=do_compact,
        sync_mirror=bool(args.sync_mirror),
    )


if __name__ == "__main__":
    raise SystemExit(main())
