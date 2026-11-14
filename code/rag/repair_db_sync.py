#!/opt/homebrew/bin/python3.11
"""
Assainissement chirurgical de la base LightRAG D-Bot.

Supprime les references a des chunks orphelins (issus d'anciens documents
purges) dans le graphe GraphML, les tables KV entity_chunks / relation_chunks
et les index vectoriels NanoVectorDB (vdb_entities / vdb_relationships),
tout en conservant intactes les donnees et embeddings des chunks valides.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import networkx as nx
import numpy as np

DEFAULT_DB_PATH = os.environ.get(
    "RAG_DB_PATH", "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"
)
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


def create_backup(db_path: Path) -> Path:
    """Cree une sauvegarde complete horodatee dans le repertoire parent."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"{db_path.name}_backup_{stamp}"
    shutil.copytree(db_path, backup_path)
    return backup_path


def run_repair(db_path: Path, apply: bool, make_backup: bool) -> int:
    """Execute le diagnostic, la reparation optionnelle et la verification finale."""
    if not db_path.is_dir():
        print(f"Repertoire introuvable : {db_path}")
        return 1

    valid_chunks, tc_count, vdb_count = _load_valid_chunk_ids(db_path)
    print(
        f"Base : {db_path}\n"
        f"Chunks valides : {len(valid_chunks)} (text_chunks={tc_count}, vdb_chunks={vdb_count})"
    )

    if apply and make_backup:
        backup_path = create_backup(db_path)
        print(f"Sauvegarde creee : {backup_path}")

    g_stats = _repair_graphml(db_path, valid_chunks, apply=apply)
    ec_stats = _repair_kv_chunks(db_path / "kv_store_entity_chunks.json", valid_chunks, apply=apply)
    rc_stats = _repair_kv_chunks(db_path / "kv_store_relation_chunks.json", valid_chunks, apply=apply)
    ve_stats = _repair_vdb(db_path / "vdb_entities.json", valid_chunks, apply=apply)
    vr_stats = _repair_vdb(db_path / "vdb_relationships.json", valid_chunks, apply=apply)

    mode_label = "APPLIQUE" if apply else "SIMULATION (--dry-run)"
    print(f"\n=== BILAN [{mode_label}] ===")
    print(f"  graphml          : {g_stats}")
    print(f"  entity_chunks    : {ec_stats}")
    print(f"  relation_chunks  : {rc_stats}")
    print(f"  vdb_entities     : {ve_stats}")
    print(f"  vdb_relationships: {vr_stats}")

    if apply:
        # Verification post-ecriture : aucun orphelin ne doit subsister
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
        return 0 if leftovers == 0 else 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Assainit les references de chunks orphelins dans LightRAG")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Chemin de la base LightRAG")
    parser.add_argument("--dry-run", action="store_true", help="Analyse sans modifier la base (defaut si --apply absent)")
    parser.add_argument("--apply", action="store_true", help="Applique les suppressions/elagages avec sauvegarde")
    parser.add_argument("--no-backup", action="store_true", help="Desactive la copie de sauvegarde prealable")
    args = parser.parse_args()
    return run_repair(Path(args.db_path), apply=args.apply, make_backup=not args.no_backup)


if __name__ == "__main__":
    raise SystemExit(main())
