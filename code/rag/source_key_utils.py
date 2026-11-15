"""Utilitaires partagés pour la génération de clés sources sans collision dans LightRAG.

LightRAG déduplique les documents par nom de fichier canonique (via ``Path(file_path).name``
dans ``normalize_document_file_path``). Ce module garantit des clés ``file_path`` uniques
pour les fichiers homonymes répartis dans plusieurs sous-dossiers tout en préservant
l'extension d'origine (requise pour le filtrage VLM/média) et la rétrocompatibilité
des fichiers à nom unique.
"""

from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Mapping

try:
    from lightrag.utils_pipeline import normalize_document_file_path as _lightrag_norm_path
except ImportError:  # pragma: no cover - repli si importé hors environnement LightRAG
    _lightrag_norm_path = None

_HEADER_FILE_RE = re.compile(r"^---\s*\nFichier:\s*(.+?)\n")


def extract_rel_path(content: str) -> str | None:
    """Extrait le chemin relatif inscrit dans l'en-tête ``Fichier:`` d'un document."""
    if not content:
        return None
    match = _HEADER_FILE_RE.match(content)
    return match.group(1).strip() if match else None


def canonical_source_name(file_path: str) -> str:
    """Reproduit la normalisation ``file_path`` appliquée par LightRAG (basename canonique)."""
    cleaned = (file_path or "").strip()
    if not cleaned:
        return ""
    if _lightrag_norm_path is not None:
        try:
            return str(_lightrag_norm_path(cleaned)).strip()
        except Exception:
            pass
    return os.path.basename(cleaned)


def is_doc_processed(row: object) -> bool:
    """Indique si une entrée ``doc_status`` LightRAG confirme un statut ``processed``."""
    if not isinstance(row, Mapping):
        return False
    status = row.get("status")
    status_val = getattr(status, "value", status)
    return str(status_val or "").strip().lower() == "processed"


def build_claimed_source_map(
    ds_snapshot: Mapping[str, Mapping],
    resolved_rels: Mapping[str, str | None],
    exclude_ids: set[str] | None = None,
) -> dict[str, set[str | None]]:
    """Construit l'index ``{cle_canonique: {rel_paths_proprietaires}}`` depuis ``doc_status``."""
    claimed: dict[str, set[str | None]] = {}
    excluded = exclude_ids or set()
    for d_id, d_data in ds_snapshot.items():
        if d_id in excluded or d_id.startswith("dup-") or not isinstance(d_data, Mapping):
            continue
        fp = str(d_data.get("file_path", "") or "").strip()
        if not fp or fp == "unknown_source":
            continue
        canon = canonical_source_name(fp)
        if not canon or canon == "unknown_source":
            continue
        claimed.setdefault(canon, set()).add(resolved_rels.get(d_id))
    return claimed


def _hashed_source_candidate(flat_token: str, rel_path: str) -> str:
    """Ajoute un suffixe MD5 court avant l'extension en cas de collision sur forme aplatie."""
    stem, ext = os.path.splitext(flat_token)
    digest = hashlib.md5(rel_path.encode("utf-8"), usedforsecurity=False).hexdigest()[:6]
    return f"{stem}--{digest}{ext}"


def _token_conflicts(
    token: str,
    rel_path: str,
    claimed_sources: Mapping[str, set[str | None]] | None,
    other_basenames: set[str] | None,
) -> bool:
    """Vérifie si une clé candidate entre en collision avec un autre document."""
    canon = canonical_source_name(token)
    if other_basenames and canon in other_basenames:
        return True
    if not claimed_sources:
        return False
    owners = claimed_sources.get(canon)
    if not owners:
        return False
    return any(owner is None or owner != rel_path for owner in owners)


def build_rag_source_key(
    rel_path: str,
    name_counts: Mapping[str, int] | None = None,
    claimed_sources: Mapping[str, set[str | None]] | None = None,
    other_basenames: set[str] | None = None,
) -> str:
    """Retourne un ``file_path`` sûr sans collision LightRAG pour ``rel_path``.

    - Conserve ``rel_path`` tel quel (que LightRAG réduit en ``basename``) si le nom
      de fichier est unique et libre dans ``doc_status``.
    - Aplatit le chemin relatif avec ``--`` (ex. ``Code--dbot--README.md``) dès qu'un
      homonyme existe ou qu'un autre document revendique déjà le même basename.
    - Bascule sur un suffixe déterministe par empreinte si la forme aplatie collisionne
      elle-même avec un autre chemin.
    """
    rel_clean = (rel_path or "").strip()
    if not rel_clean:
        return rel_clean

    basename = os.path.basename(rel_clean)
    has_homonym = bool(
        (name_counts is not None and name_counts.get(basename, 0) > 1)
        or _token_conflicts(basename, rel_clean, claimed_sources, other_basenames)
    )
    if not has_homonym:
        return rel_clean

    if "/" not in rel_clean and not _token_conflicts(basename, rel_clean, claimed_sources, None):
        return rel_clean

    base_flat = rel_clean.replace("/", "--") if "/" in rel_clean else f"root--{rel_clean}"
    if not _token_conflicts(base_flat, rel_clean, claimed_sources, other_basenames):
        return base_flat

    hashed = _hashed_source_candidate(base_flat, rel_clean)
    if not _token_conflicts(hashed, rel_clean, claimed_sources, other_basenames):
        return hashed

    stem, ext = os.path.splitext(hashed)
    idx = 2
    while True:
        candidate = f"{stem}-{idx}{ext}"
        if not _token_conflicts(candidate, rel_clean, claimed_sources, other_basenames):
            return candidate
        idx += 1


def build_active_source_aliases(active_rel_set: set[str]) -> set[str]:
    """Construit l'ensemble des formes aplaties possibles pour les fichiers actifs."""
    aliases: set[str] = set()
    for rel in active_rel_set:
        flat = rel.replace("/", "--") if "/" in rel else f"root--{rel}"
        aliases.add(flat)
        aliases.add(_hashed_source_candidate(flat, rel))
    return aliases
