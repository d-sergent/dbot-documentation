#!/opt/homebrew/bin/python3.11
"""Mini-site web local FastAPI de monitoring qualite pour LightRAG D-Bot.

Fonctionne en mode strictement non-intrusif (lecture seule JSON/GraphML +
retrieval vectoriel en memoire NumPy/FastEmbed) meme lorsqu'une indexation
index_docs.py est active en parallele. Toute action d'ecriture est bloquee
(HTTP 409) des que .indexing.lock ou index_docs.py est actif.
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import re
import subprocess
import sys
import threading
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, Field

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

from agent_indexing import IMAGE_EXTS, compute_rag_disk_stamp, is_indexing_lock_active  # noqa: E402
from rag_quality_audit import (  # noqa: E402
    DEFAULT_AUDIT_MD_PATH,
    DEFAULT_BENCHMARK_PATH,
    DEFAULT_DB_PATH,
    DEFAULT_DOCS_ROOT,
    DEFAULT_LOG_PATH,
    _safe_read_json,
    detect_live_indexing_status,
    export_static_html_report,
    inspect_document_detail,
    run_full_audit,
)
from rag_studio_service import (  # noqa: E402
    DBOT_SYSTEM_PROMPT_BASE,
    DEFAULT_SNAPSHOTS_ROOT,
    build_cad_drift_messages,
    build_chat_context,
    build_system_prompt,
    build_vlm_cad_context,
    complete_llm_chat,
    encode_image_file_b64,
    get_engines_status,
    list_visual_snapshots,
    load_arena_questions,
    resolve_profile_target,
    resolve_snapshot_path,
    run_arena_comparison,
    search_searxng,
    start_searxng,
    stop_searxng,
    stream_llm_chat,
    unload_ollama_models,
)
from source_key_utils import (  # noqa: E402
    canonical_source_name,
    extract_rel_path,
    extract_section_key,
)

DEFAULT_CACHE_DIR = os.environ.get(
    "FASTEMBED_CACHE_PATH",
    "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/models_cache",
)
_MODEL_NAME_RE = re.compile(r"^[A-Za-z0-9_.:/-]{1,80}$")


class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=600)
    top_k: int = Field(default=8, ge=1, le=30)
    use_reranker: bool = True
    skip_images: bool = True


class ReindexRequest(BaseModel):
    rel_paths: list[str] = Field(..., min_length=1, max_length=100)
    provider: str = Field(default="auto")
    model: str | None = Field(default=None)
    summary_mode: str = Field(default="deterministic")
    gleaning_mode: str = Field(default="adaptive")
    batch_size: int = Field(default=8, ge=1, le=32)
    mirror_backup: bool = Field(default=False)
    no_section_split: bool = Field(default=False)


class HygieneRequest(BaseModel):
    full_hygiene: bool = Field(default=True)
    sync_mirror: bool = Field(default=False)
    dry_run: bool = Field(default=False)


class UnloadOllamaRequest(BaseModel):
    models: list[str] = Field(default_factory=list, max_length=16)


class WebSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=600)
    max_results: int = Field(default=5, ge=1, le=8)
    categories: str = Field(default="general", pattern="^(general|it|science|news)$")
    fetch_pages: bool = True


class ChatMessageInput(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=16000)


class ChatStreamRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    profile: str = Field(default="ollama_gemma4")
    context_mode: str = Field(default="hybrid", pattern="^(hybrid|naive|file|none)$")
    target_rel_path: str | None = Field(default=None, max_length=500)
    top_k: int = Field(default=8, ge=1, le=20)
    thinking: bool = Field(default=False)
    use_web: bool = Field(default=False)
    web_max_results: int = Field(default=5, ge=1, le=8)
    web_categories: str = Field(default="general", pattern="^(general|it|science|news)$")
    web_fetch_pages: bool = Field(default=True)
    history: list[ChatMessageInput] = Field(default_factory=list, max_length=20)
    max_tokens: int = Field(default=1800, ge=64, le=8192)
    custom_url: str | None = Field(default=None, max_length=300)
    custom_model: str | None = Field(default=None, max_length=120)


class VlmAnalyzeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)
    profile: str = Field(default="ollama_gemma4")
    snapshot_rel_path: str | None = Field(default=None, max_length=500)
    image_b64: str | None = Field(default=None, max_length=15_000_000)
    include_cad_context: bool = Field(default=True)
    thinking: bool = Field(default=False)
    max_tokens: int = Field(default=1600, ge=64, le=4096)


class CadDiagnoseRequest(BaseModel):
    mode: str = Field(default="diagnose", pattern="^(diagnose|diff)$")
    profile: str = Field(default="ollama_gemma4")
    rel_path: str = Field(default="", max_length=500)
    drift_item: dict[str, Any] = Field(default_factory=dict)
    thinking: bool = Field(default=False)


class ArenaTargetInput(BaseModel):
    profile: str = Field(..., min_length=1, max_length=60)
    custom_url: str | None = Field(default=None, max_length=300)
    custom_model: str | None = Field(default=None, max_length=120)
    thinking: bool = Field(default=False)


class ArenaRunRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    targets: list[ArenaTargetInput] = Field(..., min_length=2, max_length=4)
    use_rag: bool = Field(default=True)
    use_web: bool = Field(default=False)
    context_mode: str = Field(default="hybrid", pattern="^(hybrid|naive)$")
    unload_ollama_between: bool = Field(default=True)
    expected_token: str | None = Field(default=None, max_length=200)
    max_tokens: int = Field(default=1200, ge=64, le=4096)


class _AuditCache:
    """Cache thread-safe a duree de vie bornee pour accelerer la navigation UI."""

    def __init__(
        self,
        *,
        db_path: Path,
        docs_root: Path,
        log_path: Path,
        ttl_s: float = 20.0,
    ) -> None:
        self.db_path = Path(db_path)
        self.docs_root = Path(docs_root)
        self.log_path = Path(log_path)
        self.ttl_s = ttl_s
        self._lock = threading.Lock()
        self._cached_at = 0.0
        self._report: dict[str, Any] | None = None

    def get_report(self, force_refresh: bool = False) -> dict[str, Any]:
        with self._lock:
            now = time.monotonic()
            if (
                not force_refresh
                and self._report is not None
                and (now - self._cached_at) < self.ttl_s
            ):
                # Actualise uniquement le statut temps reel sans relire les 230 Mo de cache
                refreshed = dict(self._report)
                refreshed["live_indexing"] = detect_live_indexing_status(
                    self.db_path, self.log_path
                )
                return refreshed

        report = run_full_audit(
            db_path=self.db_path,
            docs_root=self.docs_root,
            log_path=self.log_path,
            include_log_scan=True,
        )
        with self._lock:
            self._report = report
            self._cached_at = time.monotonic()
        return report


_LEX_STOPWORDS = frozenset(
    {
        "les", "des", "une", "pour", "par", "avec", "dans", "sur", "est", "sont",
        "qui", "que", "quel", "quelle", "quelles", "quels", "plus", "sans", "sous",
        "cette", "tout", "elle", "entre", "associe", "associee", "associes",
        "associees", "utilise", "utilisee", "utilisees", "specifie", "specifiee",
        "valeur", "calcule", "calculee", "indiquee", "reste", "fixation",
        "traversante", "couple", "serrage", "deux", "ainsi",
    }
)
_LEX_RARE_NUM_RE = re.compile(r"\b\d+(?:\.\d+)+\b")
_LEX_CATALOG_RE = re.compile(r"\b(?:9\d{4}[a-z]\d{3}|rs-?0\d|bmi270|dm20|dw20|rb8016|kt|m[3-8]|imu|dyneema)\b")
_LEX_WORD_RE = re.compile(r"[a-z0-9]{2,}")


def _norm_lex(text: str) -> str:
    """Normalise accents, casse et virgules decimales pour le rappel lexical."""
    nfd = unicodedata.normalize("NFKD", text or "")
    folded = "".join(ch for ch in nfd if not unicodedata.combining(ch)).lower()
    return re.sub(r"(\d),(\d)", r"\1.\2", folded)


def _extract_query_terms(query: str) -> tuple[list[str], list[str], list[str]]:
    """Extrait termes techniques rares, termes generaux et bigrammes de la requete."""
    norm_q = _norm_lex(query)
    rare: list[str] = []
    seen_rare: set[str] = set()
    for pat in (_LEX_RARE_NUM_RE, _LEX_CATALOG_RE):
        for m in pat.finditer(norm_q):
            tok = m.group(0)
            if tok not in seen_rare:
                seen_rare.add(tok)
                rare.append(tok)

    general: list[str] = []
    seen_gen: set[str] = set()
    for w in _LEX_WORD_RE.findall(norm_q):
        if len(w) >= 4 and w not in _LEX_STOPWORDS and w not in seen_rare and w not in seen_gen:
            seen_gen.add(w)
            general.append(w)

    bigrams = [f"{general[i]} {general[i + 1]}" for i in range(len(general) - 1)]
    return rare, general, bigrams


def _score_row_lexical(norm_text: str, rare: list[str], general: list[str], bigrams: list[str]) -> float:
    if not norm_text:
        return 0.0
    score = 0.0
    for term in rare:
        if term in norm_text:
            score += 3.0
    for term in general:
        if term in norm_text:
            score += 1.0
    for bg in bigrams:
        if bg in norm_text:
            score += 2.0
    return score


class _ReadOnlyVectorSearcher:
    """Moteur vectoriel + rappel lexical + reranker en memoire pure sans instancier LightRAG."""

    def __init__(self, db_path: Path, cache_dir: str = DEFAULT_CACHE_DIR) -> None:
        self.db_path = Path(db_path)
        self.cache_dir = cache_dir
        self._lock = threading.Lock()
        self._stamp: tuple | None = None
        self._rows: list[dict[str, Any]] = []
        self._norm_matrix: np.ndarray | None = None
        self._tc_map: dict[str, Any] = {}
        self._doc_rel_map: dict[str, str] = {}
        self._doc_section_map: dict[str, str | None] = {}
        self._row_norm_texts: list[str] = []
        self._embed_model: Any = None
        self._rerank_model: Any = None

    def _ensure_models(self, need_rerank: bool) -> None:
        if self._embed_model is None:
            from fastembed import TextEmbedding

            self._embed_model = TextEmbedding(
                "intfloat/multilingual-e5-large", cache_dir=self.cache_dir
            )
        if need_rerank and self._rerank_model is None:
            try:
                from fastembed.rerank.cross_encoder import TextCrossEncoder

                self._rerank_model = TextCrossEncoder(
                    "BAAI/bge-reranker-base", cache_dir=self.cache_dir
                )
            except Exception:
                try:
                    from fastembed import TextReranker

                    self._rerank_model = TextReranker(
                        "BAAI/bge-reranker-base", cache_dir=self.cache_dir
                    )
                except Exception:
                    self._rerank_model = None

    def _ensure_index_loaded(self) -> None:
        cur_stamp = compute_rag_disk_stamp(self.db_path)
        if self._norm_matrix is not None and cur_stamp == self._stamp:
            return
        vdb_raw, err = _safe_read_json(self.db_path / "vdb_chunks.json")
        if not isinstance(vdb_raw, dict):
            raise RuntimeError(err or "Impossible de lire vdb_chunks.json")
        tc_raw, _ = _safe_read_json(self.db_path / "kv_store_text_chunks.json")
        tc_map = tc_raw if isinstance(tc_raw, dict) else {}
        fd_raw, _ = _safe_read_json(self.db_path / "kv_store_full_docs.json")
        fd_map = fd_raw if isinstance(fd_raw, dict) else {}

        doc_rel_map: dict[str, str] = {}
        doc_section_map: dict[str, str | None] = {}
        for did, fd_entry in fd_map.items():
            if not isinstance(fd_entry, dict):
                continue
            fd_txt = str(fd_entry.get("content") or "")
            rel = extract_rel_path(fd_txt)
            if rel:
                doc_rel_map[str(did)] = rel
            sec = extract_section_key(fd_txt)
            if sec:
                doc_section_map[str(did)] = sec

        dim = int(vdb_raw.get("embedding_dim", 1024))
        rows = list(vdb_raw.get("data") or [])
        mat_b64 = vdb_raw.get("matrix") or ""
        if rows and mat_b64:
            mat = np.frombuffer(base64.b64decode(mat_b64), dtype=np.float32).reshape(-1, dim)
            norms = np.linalg.norm(mat, axis=1, keepdims=True)
            norms = np.where(norms == 0.0, 1.0, norms)
            norm_mat = mat / norms
        else:
            norm_mat = np.empty((0, dim), dtype=np.float32)

        row_norm_texts: list[str] = []
        for row in rows:
            cid = str(row.get("__id__", ""))
            tc_row = tc_map.get(cid) if isinstance(tc_map.get(cid), dict) else {}
            content = str(tc_row.get("content") or row.get("content") or "")
            row_norm_texts.append(_norm_lex(content))

        self._rows = rows
        self._norm_matrix = norm_mat
        self._tc_map = tc_map
        self._doc_rel_map = doc_rel_map
        self._doc_section_map = doc_section_map
        self._row_norm_texts = row_norm_texts
        self._stamp = cur_stamp

    def search(
        self,
        query: str,
        *,
        top_k: int = 8,
        use_reranker: bool = True,
        skip_images: bool = True,
    ) -> list[dict[str, Any]]:
        with self._lock:
            self._ensure_index_loaded()
            self._ensure_models(need_rerank=use_reranker)
            if self._norm_matrix is None or len(self._rows) == 0:
                return []

            q_vec = np.array(list(self._embed_model.embed([query]))[0], dtype=np.float32)
            q_norm = float(np.linalg.norm(q_vec))
            if q_norm > 0.0:
                q_vec = q_vec / q_norm
            sims = self._norm_matrix @ q_vec

            dense_pool = min(len(self._rows), max(top_k * 6, 45))
            top_dense_idx = [int(i) for i in np.argsort(sims)[::-1][:dense_pool]]
            seen_idx = set(top_dense_idx)

            rare_terms, gen_terms, bigrams = _extract_query_terms(query)
            lex_scores: dict[int, float] = {}
            if rare_terms or gen_terms:
                lex_candidates: list[tuple[float, int]] = []
                for idx, norm_txt in enumerate(self._row_norm_texts):
                    sc = _score_row_lexical(norm_txt, rare_terms, gen_terms, bigrams)
                    if sc > 0.0:
                        lex_scores[idx] = sc
                        if idx not in seen_idx and sc >= 2.0:
                            lex_candidates.append((sc + 0.1 * float(sims[idx]), idx))
                lex_candidates.sort(key=lambda item: item[0], reverse=True)
                top_lex_idx = [idx for _, idx in lex_candidates[:20]]
            else:
                top_lex_idx = []

            merged_idx = top_dense_idx + top_lex_idx

            candidates: list[dict[str, Any]] = []
            for idx in merged_idx:
                row = self._rows[int(idx)]
                cid = str(row.get("__id__", ""))
                tc_row = self._tc_map.get(cid) if isinstance(self._tc_map.get(cid), dict) else {}
                content = str(tc_row.get("content") or row.get("content") or "")
                file_path = str(tc_row.get("file_path") or row.get("file_path") or "")
                full_doc_id = str(row.get("full_doc_id") or tc_row.get("full_doc_id") or "")

                rel_hint = ""
                for line in content.splitlines()[:6]:
                    if line.startswith("Fichier:"):
                        rel_hint = line.split(":", 1)[1].strip()
                        break

                resolved_fp = (
                    rel_hint
                    or self._doc_rel_map.get(full_doc_id)
                    or canonical_source_name(file_path)
                    or file_path
                )
                ext = Path(resolved_fp).suffix.lower()
                if skip_images and ext in IMAGE_EXTS:
                    continue
                candidates.append(
                    {
                        "chunk_id": cid,
                        "full_doc_id": full_doc_id,
                        "file_path": resolved_fp,
                        "section_key": self._doc_section_map.get(full_doc_id),
                        "cosine_score": round(float(sims[int(idx)]), 4),
                        "lexical_score": round(float(lex_scores.get(int(idx), 0.0)), 2),
                        "rerank_score": None,
                        "content": content,
                    }
                )

            if use_reranker and self._rerank_model is not None and candidates:
                texts = [c["content"] for c in candidates]
                raw_scores = list(self._rerank_model.rerank(query, texts))
                for cand, s_val in zip(candidates, raw_scores):
                    cand["rerank_score"] = round(
                        float(1.0 / (1.0 + math.exp(-float(s_val)))), 4
                    )
                candidates.sort(
                    key=lambda c: (c["rerank_score"] if c["rerank_score"] is not None else 0.0),
                    reverse=True,
                )
            else:
                candidates.sort(
                    key=lambda c: c["cosine_score"] + min(0.30, 0.05 * c["lexical_score"]),
                    reverse=True,
                )

            return candidates[:top_k]


def _validate_target_rel_paths(rel_paths: list[str], docs_root: Path) -> list[str]:
    root_resolved = docs_root.resolve()
    validated: list[str] = []
    seen: set[str] = set()
    for raw in rel_paths:
        cand = (root_resolved / raw).resolve()
        if not cand.is_relative_to(root_resolved) or not cand.is_file():
            raise HTTPException(
                status_code=400, detail=f"Chemin fichier invalide ou introuvable: {raw}"
            )
        rel = str(cand.relative_to(root_resolved))
        if rel not in seen:
            seen.add(rel)
            validated.append(rel)
    return validated


def _run_benchmark_eval(
    searcher: _ReadOnlyVectorSearcher,
    benchmark_path: Path,
    *,
    top_k: int = 10,
    use_reranker: bool = True,
) -> dict[str, Any]:
    raw, err = _safe_read_json(benchmark_path)
    if not isinstance(raw, dict):
        raise HTTPException(status_code=404, detail=err or "Benchmark QA introuvable")

    qa_items = list(raw.get("data_recipes_qa") or [])
    results: list[dict[str, Any]] = []
    r1 = 0
    r5 = 0
    r10 = 0
    mrr_sum = 0.0
    tok_hits = 0

    for item in qa_items:
        q = str(item.get("question") or "")
        expected_doc = str(item.get("source_doc") or "")
        expected_tok = str(item.get("numeric_token") or "").replace(",", ".").strip()
        hits = searcher.search(q, top_k=top_k, use_reranker=use_reranker, skip_images=True)

        rank: int | None = None
        tok_found = False
        for idx, h in enumerate(hits, 1):
            fp = h["file_path"]
            if expected_doc and (expected_doc in fp or os.path.basename(fp) == expected_doc):
                if rank is None:
                    rank = idx
            if expected_tok and expected_tok in h["content"].replace(",", "."):
                tok_found = True

        if rank is not None:
            if rank <= 1:
                r1 += 1
            if rank <= 5:
                r5 += 1
            if rank <= 10:
                r10 += 1
            mrr_sum += 1.0 / rank
        if tok_found:
            tok_hits += 1

        results.append(
            {
                "id": item.get("id"),
                "category": item.get("category"),
                "source_doc": expected_doc,
                "numeric_token": item.get("numeric_token"),
                "question": q,
                "matched_rank": rank,
                "token_found": tok_found,
                "top_hit_file": hits[0]["file_path"] if hits else "",
                "top_hit_score": (
                    hits[0]["rerank_score"]
                    if hits and hits[0]["rerank_score"] is not None
                    else (hits[0]["cosine_score"] if hits else 0.0)
                ),
            }
        )

    n = max(1, len(qa_items))
    return {
        "benchmark_name": raw.get("benchmark_name", "D-Bot QA Benchmark"),
        "total_questions": len(qa_items),
        "recall_at_1": round(r1 / n, 3),
        "recall_at_5": round(r5 / n, 3),
        "recall_at_10": round(r10 / n, 3),
        "mrr": round(mrr_sum / n, 3),
        "numeric_token_hit_rate": round(tok_hits / n, 3),
        "items": results,
    }


def _build_dashboard_html() -> str:
    """Retourne l'application monopage du cockpit qualite (zero CDN externe)."""
    return """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>D-Bot LightRAG — Cockpit Qualite</title>
<style>
:root {
  --bg:#0b1120; --panel:#111a2e; --card:#16223b; --border:#273654;
  --text:#e2e8f0; --muted:#94a3b8; --accent:#38bdf8;
  --ok:#10b981; --warn:#f59e0b; --crit:#ef4444;
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; font-size:14px; }
header { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px; padding:14px 20px; background:var(--panel); border-bottom:1px solid var(--border); position:sticky; top:0; z-index:20; }
.brand { display:flex; align-items:center; gap:10px; font-weight:700; font-size:16px; }
.pill { display:inline-flex; align-items:center; gap:6px; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:600; border:1px solid var(--border); background:var(--card); }
.pill.live { background:#451a03; border-color:#f59e0b; color:#fde68a; }
.pill.idle { background:#052e16; border-color:#10b981; color:#a7f3d0; }
.dot { width:8px; height:8px; border-radius:50%; background:currentColor; }
.pill.live .dot { animation:pulse 1.4s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.25} }
.actions { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
button, select, input { background:var(--card); color:var(--text); border:1px solid var(--border); border-radius:8px; padding:7px 12px; font-size:13px; }
button { cursor:pointer; font-weight:600; }
button:hover:not(:disabled) { border-color:var(--accent); color:#fff; }
button.primary { background:#0284c7; border-color:#0284c7; color:#fff; }
button.danger { background:#991b1b; border-color:#dc2626; color:#fff; }
button:disabled { opacity:0.45; cursor:not-allowed; }
nav.tabs { display:flex; gap:6px; padding:10px 20px; background:#0e1729; border-bottom:1px solid var(--border); overflow-x:auto; }
nav.tabs button { background:transparent; border:1px solid transparent; color:var(--muted); padding:8px 14px; }
nav.tabs button.active { background:var(--card); border-color:var(--border); color:var(--accent); }
main { padding:16px 24px; width:100%; max-width:none; margin:0; }
.tab-pane { display:none; }
.tab-pane.active { display:block; }
.kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-bottom:18px; }
.card { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:14px; min-width:0; }
.kpi-val { font-size:24px; font-weight:700; color:var(--accent); }
.kpi-lbl { font-size:12px; color:var(--muted); margin-top:4px; }
.two-col { display:grid; grid-template-columns:minmax(0, 1fr) minmax(0, 1fr); gap:14px; margin-bottom:16px; }
@media (max-width:960px) { .two-col { grid-template-columns:1fr; } }
.bar-row { display:flex; align-items:center; gap:10px; margin:7px 0; font-size:12px; }
.bar-lbl { width:190px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; color:var(--muted); }
.bar-track { flex:1; height:10px; background:#0b1120; border-radius:999px; overflow:hidden; }
.bar-fill { height:100%; background:var(--accent); border-radius:999px; }
.toolbar { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:12px; align-items:center; }
table { width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--border); border-radius:10px; overflow:hidden; font-size:12.5px; }
th, td { padding:8px 10px; border-bottom:1px solid var(--border); text-align:left; vertical-align:top; }
th { background:#0b1220; color:var(--muted); font-weight:600; position:sticky; top:0; }
tr:hover td { background:#18243f; }
.badge { display:inline-block; padding:2px 8px; border-radius:999px; font-weight:700; font-size:11px; }
.badge.critical { background:#7f1d1d; color:#fecaca; }
.badge.warning { background:#78350f; color:#fde68a; }
.badge.healthy { background:#064e3b; color:#a7f3d0; }
.tag { display:inline-block; padding:2px 6px; margin:1px 3px 1px 0; border-radius:5px; font-size:11px; background:#0f172a; border:1px solid var(--border); color:#cbd5e1; }
code, pre { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12px; }
pre { background:#090f1d; border:1px solid var(--border); border-radius:8px; padding:10px; overflow:auto; max-height:280px; white-space:pre-wrap; word-break:break-word; }
.split { display:grid; grid-template-columns:minmax(0, 1.1fr) minmax(0, 1fr); gap:14px; }
@media (max-width:1100px) { .split { grid-template-columns:1fr; } }
.banner-ro { display:none; margin-bottom:14px; padding:10px 14px; border-radius:8px; background:#451a03; border:1px solid #d97706; color:#fde68a; }
.banner-ro.show { display:block; }
#subgraph-svg { width:100%; height:420px; background:#090f1d; border:1px solid var(--border); border-radius:10px; }
.muted { color:var(--muted); }
.modal-backdrop { display:none; position:fixed; inset:0; background:rgba(2,6,23,0.78); z-index:50; align-items:center; justify-content:center; padding:20px; }
.modal-backdrop.show { display:flex; }
.modal-box { background:var(--panel); border:1px solid var(--border); border-radius:12px; max-width:94vw; width:100%; max-height:86vh; overflow:auto; padding:18px 22px; box-shadow:0 20px 50px rgba(0,0,0,0.65); }
.modal-hdr { display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid var(--border); padding-bottom:10px; margin-bottom:14px; }
.help-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
@media (max-width:960px) { .help-grid { grid-template-columns:1fr; } }
.help-list { margin:6px 0 0 0; padding-left:18px; line-height:1.55; font-size:12.5px; color:var(--text); }
.help-list li { margin-bottom:6px; }
.pill.warn { background:#451a03; border-color:#f59e0b; color:#fde68a; }
.pill.down { background:#450a0a; border-color:#ef4444; color:#fecaca; }
.banner-warn { display:none; margin-bottom:14px; padding:10px 14px; border-radius:8px; background:#451a03; border:1px solid #f59e0b; color:#fde68a; align-items:center; justify-content:space-between; gap:10px; }
.banner-warn.show { display:flex; }
textarea { background:var(--card); color:var(--text); border:1px solid var(--border); border-radius:8px; padding:9px 12px; font-size:13px; font-family:inherit; resize:vertical; }
.chat-grid { display:grid; grid-template-columns:minmax(0, 2.2fr) minmax(360px, 1fr); gap:14px; }
@media (max-width:1100px) { .chat-grid { grid-template-columns:1fr; } }
#chat-sources-box { overflow-wrap:anywhere; word-break:break-word; }
.chat-log { height:calc(100vh - 280px); min-height:520px; overflow:auto; background:#090f1d; border:1px solid var(--border); border-radius:10px; padding:12px; display:flex; flex-direction:column; gap:10px; }
.chat-msg { padding:10px 12px; border-radius:10px; border:1px solid var(--border); line-height:1.5; white-space:pre-wrap; word-break:break-word; }
.chat-msg.user { background:#132a4a; border-color:#0284c7; align-self:flex-end; max-width:90%; }
.chat-msg.assistant { background:#111a2e; align-self:stretch; }
.chat-meta { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin-bottom:6px; font-size:11.5px; color:var(--muted); }
.chat-think { margin:6px 0; border:1px dashed var(--border); border-radius:8px; padding:6px 8px; background:#0b1222; font-size:12px; }
.chip-row { display:flex; flex-wrap:wrap; gap:6px; margin-top:6px; align-items:center; }
.copy-chip { background:#0f172a; border:1px solid var(--accent); color:var(--accent); border-radius:6px; padding:3px 8px; font-size:11.5px; cursor:pointer; }
.drop-zone { border:2px dashed var(--border); border-radius:10px; padding:14px; text-align:center; background:#090f1d; cursor:pointer; margin-bottom:10px; }
.drop-zone.dragover { border-color:var(--accent); background:#0f1e36; }
.snap-list { max-height:260px; overflow:auto; border:1px solid var(--border); border-radius:8px; background:#090f1d; }
.snap-item { padding:7px 10px; border-bottom:1px solid var(--border); cursor:pointer; font-size:12px; display:flex; justify-content:space-between; gap:8px; }
.snap-item:hover, .snap-item.active { background:#18243f; color:var(--accent); }
.arena-cols { display:grid; grid-template-columns:minmax(0, 1fr) minmax(0, 1fr); gap:14px; margin-top:12px; }
@media (max-width:1000px) { .arena-cols { grid-template-columns:1fr; } }
</style>
</head>
<body>
<header>
  <div class="brand">
    <span>D-Bot LightRAG — Cockpit &amp; Studio</span>
    <span id="live-pill" class="pill idle" title="Etat temps reel du verrou d'indexation LightRAG"><span class="dot"></span><span id="live-pill-txt">Verification...</span></span>
    <span id="storage-pill" class="pill" title="Taille de la base active sur SSD local et du miroir Google Drive">Stockage...</span>
    <span id="ollama-pill" class="pill" title="Etat Ollama :11434 et VRAM occupee">Ollama...</span>
    <span id="unsloth-pill" class="pill" title="Etat Unsloth Studio :8888">Unsloth...</span>
    <span id="searxng-pill" class="pill" title="Etat SearXNG natif Python (:8088, 0 Docker)">SearXNG...</span>
    <span id="ram-pill" class="pill" title="Memoire unifiee macOS utilisee (M1 Max 64 Go)">RAM...</span>
  </div>
  <div class="actions">
    <button id="btn-toggle-searxng" onclick="toggleSearxng()" title="Demarrer ou arreter SearXNG natif Python (:8088, 0 Docker, ~32 Mo RAM actif)">Demarrer SearXNG</button>
    <button id="btn-unload-ollama" onclick="unloadOllamaVram()" title="Libere immediatement les modeles charges en VRAM Ollama (keep_alive=0)">Decharger Ollama VRAM</button>
    <button id="btn-run-hygiene" onclick="triggerHygiene(true)" title="Purge les orphelins, elague le graphe, compacte le cache LLM inutilise et synchronise le SSD local vers Google Drive">Hygiene &amp; Miroir Drive</button>
    <button id="btn-refresh-audit" onclick="loadAudit(true)" title="Force le recalcul immediat du score de sante de tous les fichiers">Rafraichir l'audit</button>
    <button onclick="downloadHtmlSnapshot()" title="Telecharge un rapport HTML autonome de l'audit actuel">Exporter HTML</button>
    <button id="btn-open-help" onclick="toggleHelpModal(true)" title="Guide complet des boutons, options d'indexation et Studio IA">? Aide &amp; Guide</button>
  </div>
</header>

<nav class="tabs">
  <button class="active" data-tab="overview" onclick="switchTab('overview', this)">Vue Globale</button>
  <button data-tab="files" onclick="switchTab('files', this)">Matrice Fichiers & Re-indexation</button>
  <button data-tab="inspector" onclick="switchTab('inspector', this)">Inspecteur & Sous-Graphe</button>
  <button data-tab="graph" onclick="switchTab('graph', this)">Graphe & Synchronisation</button>
  <button data-tab="cad" onclick="switchTab('cad', this)">Parite CAO / BOM / SVG</button>
  <button data-tab="retrieval" onclick="switchTab('retrieval', this)">Test Retrieval & Arena</button>
  <button data-tab="chat" onclick="switchTab('chat', this)">Chat D-Bot</button>
  <button data-tab="vision" onclick="switchTab('vision', this)">Vision CAO / FEA</button>
</nav>

<main>
  <div id="ro-banner" class="banner-ro"></div>
  <div id="ram-guard-banner" class="banner-warn"><span id="ram-guard-text"></span><button onclick="unloadOllamaVram()">Decharger Ollama</button></div>

  <section id="tab-overview" class="tab-pane active">
    <div id="kpi-overview" class="kpi-grid"></div>
    <div class="two-col">
      <div class="card"><h3>Repartition Chunking & Sante</h3><div id="chart-health"></div></div>
      <div class="card"><h3>Top Anomalies Detectees</h3><div id="chart-reasons"></div></div>
    </div>
    <div class="two-col">
      <div class="card"><h3>Activations Moteurs (rag_indexing.log)</h3><div id="chart-engines"></div></div>
      <div class="card">
        <h3>Journal d'Indexation Temps Reel (20 dernieres lignes)</h3>
        <div id="live-chunk-meta" class="muted" style="margin-bottom:8px; font-size:12px;"></div>
        <pre id="live-log-tail"></pre>
      </div>
    </div>
  </section>

  <section id="tab-files" class="tab-pane">
    <div class="toolbar">
      <input id="f-search" type="text" placeholder="Filtrer par chemin ou anomalie..." oninput="renderFilesTable()" style="min-width:250px;">
      <select id="f-status" onchange="renderFilesTable()">
        <option value="all">Tous statuts</option>
        <option value="critical">Critiques</option>
        <option value="warning">Avertissements</option>
        <option value="healthy">Sains</option>
      </select>
      <select id="f-priority" onchange="renderFilesTable()">
        <option value="all">Toutes priorites</option>
        <option value="critical">Niveau 1 / PDF / SVG</option>
        <option value="standard">Standard</option>
        <option value="image">Images VLM</option>
      </select>
      <select id="f-reason" onchange="renderFilesTable()">
        <option value="all">Toutes anomalies</option>
      </select>
      <select id="re-provider" title="Moteur LLM">
        <option value="auto" selected>Moteur: auto (Gemini -> Ollama)</option>
        <option value="ollama">Moteur: ollama (qwen3.8:27b-mlx)</option>
        <option value="gemini">Moteur: gemini (Free Tier non-lite)</option>
        <option value="1minai">Moteur: 1minai (mistral-small-latest)</option>
      </select>
      <select id="re-summary" title="Mode de fusion hubs">
        <option value="deterministic" selected>Fusion: deterministic (0 LLM)</option>
        <option value="gemma4">Fusion: gemma4</option>
        <option value="llm">Fusion: llm</option>
      </select>
      <select id="re-gleaning" title="Politique de gleaning">
        <option value="adaptive" selected>Gleaning: adaptive (1 crit / 0 std)</option>
        <option value="on">Gleaning: on (1 partout)</option>
        <option value="off">Gleaning: off (0 partout)</option>
      </select>
      <select id="re-batch" title="Taille de lot rag.ainsert">
        <option value="4">Lot: 4</option>
        <option value="8" selected>Lot: 8</option>
        <option value="16">Lot: 16</option>
      </select>
      <label><input id="re-mirror" type="checkbox"> Miroir Drive</label>
      <button onclick="selectVisibleFiles(true)">Cocher visibles (max 25)</button>
      <button onclick="selectVisibleFiles(false)">Decocher tout</button>
      <button class="primary" onclick="copySelectedCommand()">Copier commande CLI</button>
      <button id="btn-run-reindex" class="danger" onclick="triggerReindex()">Re-indexer selection</button>
    </div>
    <pre id="cli-preview" style="display:none; margin-bottom:12px;"></pre>
    <div style="overflow:auto; max-height:68vh;">
      <table>
        <thead>
          <tr>
            <th></th><th>Score</th><th>Priorite</th><th>Fichier</th><th>Chunking</th>
            <th>Ent / Rel</th><th>Rel/1k tok</th><th>Retention</th><th>Ancrage</th><th>Anomalies</th><th>Action</th>
          </tr>
        </thead>
        <tbody id="files-tbody"></tbody>
      </table>
    </div>
  </section>

  <section id="tab-inspector" class="tab-pane">
    <div class="toolbar">
      <span id="insp-title" class="muted">Selectionnez un fichier dans l'onglet Matrice Fichiers (bouton Inspecter).</span>
    </div>
    <div class="split">
      <div class="card">
        <h3>Chunks & Sortie Cache LLM</h3>
        <div id="insp-chunks"></div>
      </div>
      <div class="card">
        <h3>Sous-graphe Local (<span id="insp-graph-stats">0</span>)</h3>
        <svg id="subgraph-svg" viewBox="0 0 680 420"></svg>
        <div id="insp-node-detail" class="muted" style="margin-top:8px;">Cliquez sur un noeud du graphe pour voir sa description.</div>
      </div>
    </div>
  </section>

  <section id="tab-graph" class="tab-pane">
    <div id="kpi-graph" class="kpi-grid"></div>
    <div class="two-col">
      <div class="card">
        <h3>Clusters d'entites quasi-doublons</h3>
        <div id="graph-dups" style="max-height:320px; overflow:auto;"></div>
      </div>
      <div class="card">
        <h3>Documents orphelins en base (<span id="orphans-count">0</span>)</h3>
        <div id="graph-orphans" style="max-height:320px; overflow:auto;"></div>
      </div>
    </div>
    <div class="card">
      <h3>Dernier rapport d'integrite Markdown (AUDIT_INTEGRITE.md)</h3>
      <pre id="audit-md-preview" style="max-height:340px;"></pre>
    </div>
  </section>

  <section id="tab-cad" class="tab-pane">
    <div id="kpi-cad" class="kpi-grid"></div>
    <div class="card" style="margin-bottom:14px;">
      <h3>1. Controle Metrologique &amp; Versions (JSON CAO &lt;-&gt; Dossiers Markdown)</h3>
      <div style="overflow:auto;">
        <table>
          <thead>
            <tr>
              <th>Statut</th><th>Document cible</th><th>Versions CAO citees</th><th>Pieces controlees / Derive</th><th>Anomalies detectees</th><th>Diagnostic IA</th>
            </tr>
          </thead>
          <tbody id="cad-docs-tbody"></tbody>
        </table>
      </div>
    </div>
    <div class="two-col">
      <div class="card">
        <h3>2. Parite Quincaillerie McMaster-Carr (CAO &lt;-&gt; FINAL_BOM)</h3>
        <div id="cad-bom-box" style="max-height:360px; overflow:auto;"></div>
      </div>
      <div class="card">
        <h3>3. Fraicheur des Schemas SVG &amp; Snapshots (mtime CAO vs SVG)</h3>
        <div id="cad-svg-box" style="max-height:360px; overflow:auto;"></div>
      </div>
    </div>
    <div class="card" style="margin-top:14px;">
      <h3>4. Hierarchie Bi-Temporelle Niveau 1 &gt; Niveau 2 (Etudes STUDY_ plus recentes que FINAL_ / DOSSIER_TECHNIQUE_)</h3>
      <div id="cad-bitemporal-box" style="max-height:320px; overflow:auto;"></div>
    </div>
  </section>

  <section id="tab-retrieval" class="tab-pane">
    <div class="toolbar">
      <input id="q-input" type="text" placeholder="Question technique D-Bot (ex: couple serrage IMU plaque haute 91292A017)..." style="flex:1; min-width:300px;">
      <select id="q-topk">
        <option value="5">Top 5</option>
        <option value="8" selected>Top 8</option>
        <option value="15">Top 15</option>
      </select>
      <label><input id="q-rerank" type="checkbox" checked> Reranker BGE</label>
      <label><input id="q-skipimg" type="checkbox" checked> Ignorer images</label>
      <button class="primary" onclick="runRetrieval()">Tester Retrieval</button>
      <button onclick="runBenchmark()">Lancer Benchmark QA (100 % sans LLM)</button>
    </div>
    <div id="retrieval-results"></div>
    <div id="benchmark-results" style="margin-top:16px;"></div>

    <div class="card" style="margin-top:18px;">
      <h3 style="margin-top:0;">Comparateur A/B &amp; Arena Locale (Sequentiel 64 Go M1 Max)</h3>
      <div class="toolbar">
        <select id="arena-q-select" onchange="onSelectArenaQuestion()" style="max-width:440px;">
          <option value="">-- Charger une question depuis BENCHMARK_QA_DBOT_120.json --</option>
        </select>
        <input id="arena-token" type="text" placeholder="Token attendu (optionnel, ex: 85 MPa)" style="width:220px;">
        <label><input id="arena-rag" type="checkbox" checked> Injecter contexte RAG</label>
        <label><input id="arena-web" type="checkbox"> + Web (SearXNG)</label>
        <select id="arena-rag-mode">
          <option value="hybrid" selected>Mode RAG: hybrid</option>
          <option value="naive">Mode RAG: naive</option>
        </select>
        <label><input id="arena-unload-between" type="checkbox" checked> Decharger Ollama entre runs</label>
      </div>
      <div class="toolbar">
        <label>Cible A:
          <select id="arena-t1">
            <option value="ollama_gemma4" selected>Ollama gemma4:26b (Quotidien)</option>
            <option value="unsloth_qwen38">Unsloth Qwen3.8-27B-GGUF</option>
            <option value="ollama_qwen38">Ollama qwen3.8:27b-mlx</option>
          </select>
        </label>
        <label>Cible B:
          <select id="arena-t2" onchange="toggleCustomArenaFields()">
            <option value="unsloth_qwen38" selected>Unsloth Qwen3.8-27B-GGUF</option>
            <option value="ollama_qwen38">Ollama qwen3.8:27b-mlx</option>
            <option value="ollama_gemma4">Ollama gemma4:26b</option>
            <option value="custom_openai">Serveur OpenAI local custom (loopback)</option>
          </select>
        </label>
        <input id="arena-custom-url" type="text" placeholder="http://127.0.0.1:8080/v1" style="display:none; width:210px;">
        <input id="arena-custom-model" type="text" placeholder="nom-modele" style="display:none; width:160px;">
        <button id="btn-run-arena" class="primary" onclick="runArena()">Lancer Arena Sequentielle</button>
      </div>
      <textarea id="arena-question" rows="2" style="width:100%;" placeholder="Saisissez la question technique a evaluer cote a cote..."></textarea>
      <div id="arena-results" style="margin-top:12px;"></div>
    </div>
  </section>

  <section id="tab-chat" class="tab-pane">
    <div class="toolbar">
      <label>Profil:
        <select id="chat-profile">
          <option value="ollama_gemma4" selected>Rapide &amp; Multimodal : Ollama gemma4:26b</option>
          <option value="unsloth_qwen38">Expert Ingenierie : Unsloth Qwen3.8-27B-GGUF</option>
          <option value="ollama_qwen38">Souverain MLX : Ollama qwen3.8:27b-mlx</option>
        </select>
      </label>
      <label>Contexte:
        <select id="chat-context-mode">
          <option value="hybrid" selected>Hybride (Vecteurs + GraphML)</option>
          <option value="naive">Vectoriel + Rerank BGE</option>
          <option value="file">Fichier specifique</option>
          <option value="none">Chat libre (0 RAG)</option>
        </select>
      </label>
      <span id="chat-target-badge" class="tag" style="display:none;"></span>
      <button id="btn-clear-target-file" onclick="clearChatTargetFile()" style="display:none;">Retirer fichier</button>
      <label><input id="chat-thinking" type="checkbox"> Activer Thinking</label>
      <label><input id="chat-use-web" type="checkbox"> + Web (SearXNG)</label>
      <select id="chat-web-cat" title="Categorie de recherche SearXNG">
        <option value="general" selected>Web: general</option>
        <option value="it">Web: dev / IT</option>
        <option value="science">Web: science</option>
        <option value="news">Web: actualites</option>
      </select>
      <label title="Lire le contenu texte des 3 premieres pages publiques (filtre anti-SSRF)"><input id="chat-web-fetch" type="checkbox" checked> Lire pages</label>
      <button onclick="resetChatSession()">Nouvelle session</button>
    </div>
    <div class="chat-grid">
      <div class="card">
        <div id="chat-messages" class="chat-log"></div>
        <div class="chip-row" style="margin-top:8px;">
          <button class="copy-chip" onclick="setChatPrompt('Donne le couple de serrage, la reference McMaster-Carr et le materiau des fixations du roulement RB8016.')">RB8016 &amp; Vis</button>
          <button class="copy-chip" onclick="setChatPrompt('Resume les contraintes Von Mises max et le facteur de securite Sf pour la Bride Epaule RS-04.')">FEA Bride RS-04</button>
          <button class="copy-chip" onclick="setChatPrompt('Explique la regle de routage de cable sur les actionneurs RobStride RS-00 a RS-06.')">Routage RobStride</button>
        </div>
        <div class="toolbar" style="margin-top:8px; margin-bottom:0; align-items:flex-end;">
          <textarea id="chat-input" rows="2" style="flex:1;" placeholder="Posez votre question technique D-Bot (Ctrl+Entree pour envoyer)..." onkeydown="if((event.ctrlKey||event.metaKey)&&event.key==='Enter'){event.preventDefault();sendChatMessage();}"></textarea>
          <button id="btn-chat-send" class="primary" onclick="sendChatMessage()">Envoyer</button>
          <button id="btn-chat-stop" class="danger" onclick="stopChatStream()" disabled>Arreter</button>
        </div>
      </div>
      <div class="card">
        <h3 style="margin-top:0;">Sources &amp; References McMaster Detectees</h3>
        <div id="chat-mcmaster-box" class="chip-row" style="margin-bottom:10px;"><span class="muted">Aucune reference detectee pour l'instant.</span></div>
        <div id="chat-sources-box" style="max-height:calc(100vh - 310px); min-height:490px; overflow:auto;"><span class="muted">Les extraits LightRAG, entites GraphML et liens vers l'Inspecteur apparaitront ici.</span></div>
      </div>
    </div>
  </section>

  <section id="tab-vision" class="tab-pane">
    <div class="two-col">
      <div class="card">
        <h3 style="margin-top:0;">1. Navigateur Visual_Snapshots &amp; Import Image</h3>
        <div class="toolbar">
          <select id="vlm-group" onchange="renderSnapshotList()">
            <option value="ALL">Tous dossiers</option>
            <option value="Vues_Ensemble">Vues_Ensemble</option>
            <option value="Assemblages">Assemblages</option>
            <option value="Pieces_Isolees">Pieces_Isolees</option>
          </select>
          <input id="vlm-filter" type="text" placeholder="Filtrer piece (ex: selle, bride, pelvis)..." oninput="renderSnapshotList()" style="flex:1;">
          <button onclick="loadSnapshots()">Actualiser PNG</button>
        </div>
        <div id="vlm-snap-list" class="snap-list"></div>
        <div id="vlm-drop-zone" class="drop-zone" style="margin-top:10px;" onclick="document.getElementById('vlm-file-input').click()">
          Glissez-deposez ici une capture PNG/JPG/WebP (ou cliquez pour importer)
          <input id="vlm-file-input" type="file" accept="image/png,image/jpeg,image/webp" style="display:none;" onchange="handleVlmFileInput(this.files)">
        </div>
        <div id="vlm-preview-wrap" style="text-align:center;">
          <div id="vlm-selected-label" class="muted" style="margin-bottom:6px;">Aucune image selectionnee.</div>
          <img id="vlm-preview-img" alt="Apercu CAO" style="max-width:100%; max-height:280px; border-radius:8px; border:1px solid var(--border); display:none;">
        </div>
      </div>
      <div class="card">
        <h3 style="margin-top:0;">2. Inspection Multimodale CAO / FEA</h3>
        <div class="toolbar">
          <label>Modele VLM:
            <select id="vlm-profile">
              <option value="ollama_gemma4" selected>Ollama gemma4:26b (VLM Natif)</option>
              <option value="unsloth_qwen38">Unsloth Qwen3.8-27B-GGUF</option>
            </select>
          </label>
          <label><input id="vlm-include-cad" type="checkbox" checked> Croiser JSON metrologique + RAG</label>
          <label><input id="vlm-thinking" type="checkbox"> Thinking</label>
        </div>
        <div class="chip-row" style="margin-bottom:8px;">
          <button class="copy-chip" onclick="setVlmPrompt('Decris la geometrie visible, identifie les perçages, bossages et symetries par rapport au JSON metrologique CAO.')">Controler silhouette &amp; percages</button>
          <button class="copy-chip" onclick="setVlmPrompt('Verifie les degagements d assemblage, l absence d interference visuelle et rappelle le passage de cable deporte si un moteur RobStride est present.')">Degagements &amp; routage</button>
          <button class="copy-chip" onclick="setVlmPrompt('Lis les zones critiques, concentrations de contraintes ou annotations visibles sur cette capture FEA / technique.')">Analyser carte FEA</button>
        </div>
        <textarea id="vlm-prompt" rows="3" style="width:100%;" placeholder="Question d'inspection sur l'image selectionnee..."></textarea>
        <div class="toolbar" style="margin-top:8px;">
          <button id="btn-vlm-analyze" class="primary" onclick="runVlmAnalysis()">Analyser Image</button>
        </div>
        <div id="vlm-result" style="max-height:360px; overflow:auto;"></div>
      </div>
    </div>
  </section>
</main>

<div id="cad-diag-modal" class="modal-backdrop" onclick="if(event.target===this)toggleCadDiagModal(false)">
  <div class="modal-box">
    <div class="modal-hdr">
      <h2 id="cad-diag-title" style="margin:0; font-size:16px; color:var(--accent);">Diagnostic CAO / BOM / SVG</h2>
      <div style="display:flex; gap:8px;">
        <button id="btn-copy-cad-diag" onclick="copyCadDiagText()">Copier diagnostic / diff</button>
        <button onclick="toggleCadDiagModal(false)">Fermer (Echap)</button>
      </div>
    </div>
    <div id="cad-diag-meta" class="muted" style="margin-bottom:8px; font-size:12px;"></div>
    <div id="cad-diag-chips" class="chip-row" style="margin-bottom:8px;"></div>
    <pre id="cad-diag-body" style="max-height:60vh;"></pre>
  </div>
</div>

<div id="help-modal" class="modal-backdrop" onclick="if(event.target===this)toggleHelpModal(false)">
  <div class="modal-box">
    <div class="modal-hdr">
      <h2 style="margin:0; font-size:17px; color:var(--accent);">Guide du Cockpit Qualite LightRAG D-Bot</h2>
      <button onclick="toggleHelpModal(false)">Fermer (Echap)</button>
    </div>
    <div class="help-grid">
      <div class="card">
        <h3 style="margin-top:0;">1. Bandeau Haut &amp; Maintenance (Hygiene)</h3>
        <ul class="help-list">
          <li><strong>Base disponible / Indexation active</strong> : surveille le verrou <code>.indexing.lock</code> et <code>.indexing_progress.json</code>. Pendant une indexation, l'interface passe automatiquement en lecture seule et affiche la barre de progression en direct.</li>
          <li><strong>SSD local ... Mo | Miroir ... Mo</strong> : compare la taille de la base active sur SSD local (<code>/Users/Shared/dbot_rag_local/lightrag_dbot_db</code>) avec la sauvegarde sur Google Drive. Un ecart signifie que de nouvelles indexations ou du cache doivent etre compactes/synchronises.</li>
          <li><strong>Hygiene &amp; Miroir Drive</strong> : lance <code>repair_db_sync.py --full-hygiene --apply --sync-mirror</code>. Cette etape : (1) purge les documents/chunks/vecteurs orphelins ou archives, (2) elague chirurgicalement les noeuds et aretes morts de <code>graph_chunk_entity_relation.graphml</code>, (3) compacte <code>kv_store_llm_response_cache.json</code> en supprimant les vieilles entrees de cache non referencees, et (4) synchronise le SSD local vers Google Drive.</li>
          <li><strong>Rafraichir l'audit</strong> : recalcule immediatement tous les scores (vide le cache de 20 s).</li>
          <li><strong>Exporter HTML</strong> : telecharge une photographie HTML autonome du rapport.</li>
        </ul>
      </div>
      <div class="card">
        <h3 style="margin-top:0;">2. Options de Re-indexation (Matrice Fichiers)</h3>
        <ul class="help-list">
          <li><strong>Moteur (Provider)</strong> :
            <br>- <code>auto (Gemini -&gt; Ollama)</code> : utilise la cascade Gemini Free Tier non-lite en priorite puis bascule automatiquement sur Ollama local (<code>qwen3.8:27b-mlx</code>) si les quotas cloud sont satures.
            <br>- <code>ollama (qwen3.8:27b-mlx)</code> : force le modele local souverain 27B MLX (recommande pour les dossiers techniques et tableaux critiques).
            <br>- <code>gemini</code> / <code>1minai</code> : force uniquement le fournisseur cloud choisi.</li>
          <li><strong>Fusion (Summary Mode)</strong> : <code>deterministic (0 LLM)</code> (recommande : fusionne les descriptions d'entites par deduplication instantanee sans appel LLM), <code>gemma4</code> ou <code>llm</code> (appelle un LLM sur les gros noeuds hubs <code>&gt;= 24</code> fragments).</li>
          <li><strong>Gleaning (Passe de relecture)</strong> : <code>adaptive</code> (recommande : <code>G1</code> = 1 passe de relecture sur les fichiers critiques Niveau 1 / PDF / SVG, <code>G0</code> = 0 passe sur les fichiers standards/code), <code>on</code> (<code>G1</code> partout) ou <code>off</code> (<code>G0</code> partout).</li>
          <li><strong>Lot &amp; Miroir Drive</strong> : taille de lot <code>rag.ainsert</code> (<code>8</code> par defaut) et synchronisation optionnelle vers Google Drive en fin de traitement.</li>
          <li><strong>Re-indexer selection / Copier commande CLI</strong> : lance en arriere-plan (ou copie) <code>index_docs.py --files ...</code> en purgeant automatiquement l'ancien cache LLM des fichiers coches.</li>
        </ul>
      </div>
      <div class="card">
        <h3 style="margin-top:0;">3. Scores, Badges &amp; Colonnes</h3>
        <ul class="help-list">
          <li><strong>Score (0 a 100)</strong> : somme de 5 sous-scores — Synchro &amp; chunking <code>1600/150</code> (<code>20 pts</code>), Densite graphe entites/relations (<code>25 pts</code>), Integrite syntaxique cache (<code>20 pts</code>), Retention des cotes/references (<code>20 pts</code>) et Hygiene/Ancrage lexical (<code>15 pts</code>).</li>
          <li><strong>Statuts de sante</strong> :
            <br>- <span class="badge healthy">Sain (&gt;= 75)</span> : extraction complete et bien ancree.
            <br>- <span class="badge warning">Avertissement (50-74)</span> : ou fichier critique encore en ancien chunking <code>1200/100</code>.
            <br>- <span class="badge critical">Critique (&lt; 50)</span> : non traite, 0 entite/relation ou ancrage <code>&lt; 60 %</code>.</li>
          <li><strong>Badges <code>G1 / G0</code> et <code>N sec. ##</code></strong> : politique de gleaning du fichier, et nombre de sous-documents virtuels decoupes par section <code>##</code> (pour les gros Markdown <code>&gt;= 24 Ko</code>).</li>
          <li><strong>Retention &amp; Ancrage</strong> : <code>%</code> des valeurs chiffrees/codes (<code>mm</code>, <code>Nm</code>, McMaster, <code>RS-04</code>...) retrouvees dans l'extraction, et <code>%</code> des entites presentes dans le texte source.</li>
        </ul>
      </div>
      <div class="card">
        <h3 style="margin-top:0;">4. Dictionnaire des Anomalies (Top Anomalies)</h3>
        <ul class="help-list">
          <li><code>LEGACY_1200_100</code> (<code>-3 pts</code>) : fichier indexe dans le passe avec l'ancien decoupage <code>1200/100</code> (avant passage a <code>1600/150</code>). Comme <code>--update</code> ne touche qu'aux fichiers modifies, ce compteur reste stable tant que ces anciens fichiers (souvent deja sains) ne sont pas modifies ou re-indexes.</li>
          <li><code>MISSING_COMPLETE_TAG</code> (<code>-2 a -8 pts</code>) : ancienne passe LLM terminee sans balise <code>&lt;|COMPLETE|&gt;</code>.</li>
          <li><code>SYNTAX_ERRORS_EXTRACT</code> / <code>BROKEN_DELIMITERS</code> : lignes historiques mal formatees en cache (corrigees a la re-indexation par le nouveau sanitizer).</li>
          <li><code>LOW_METRIC_RETENTION</code> / <code>LOW_REL_DENSITY</code> / <code>LOW_ENT_DENSITY</code> : faible densite de cotes ou de relations (frequent sur du code Python ; sur un dossier technique, re-indexer avec <code>Moteur: ollama</code>).</li>
          <li><code>UNGROUNDED_ENTITIES</code> : entites extraites en francais non retrouvees litteralement dans un fichier source anglais/code.</li>
          <li><code>DOLLAR_OR_LATEX_ARTIFACT</code> / <code>EMPTY_GLEANING_HIGH</code> / <code>NO_CACHE_TRACE</code> : residu dollar/LaTeX en cache, passe <code>G1</code> majoritairement vide, ou trace cache absente.</li>
          <li><code>CAD_VERSION_DRIFT</code> / <code>PART_MASS_DRIFT</code> / <code>CAD_BOM_MISSING_REF</code> / <code>STALE_VISUAL_SNAPSHOT</code> : derive deterministe en temps reel entre <code>AUDIT_METROLOGIQUE_Torse_et_Bassin.json</code>, les dossiers techniques, la BOM McMaster-Carr et les schemas <code>media/*.svg</code>.</li>
        </ul>
      </div>
      <div class="card">
        <h3 style="margin-top:0;">5. Studio IA Local (Gemma4 + Unsloth Qwen3.8 + Garde RAM)</h3>
        <ul class="help-list">
          <li><strong>Bandeau Moteurs &amp; RAM</strong> : surveille Ollama (<code>:11434</code>), Unsloth Studio (<code>:8888</code>) et la RAM macOS. Le bouton <code>Decharger Ollama VRAM</code> libere la VRAM (<code>keep_alive=0</code>) avant de lancer Unsloth pour eviter les swap sur 64 Go.</li>
          <li><strong>Verrou d'indexation</strong> : si <code>.indexing.lock</code> est actif, Chat, VLM, Diagnostic CAO et Arena sont verrouilles (HTTP 409) par securite.</li>
          <li><strong>Chat D-Bot &amp; Vision CAO</strong> : streaming SSE avec raisonnement depliable, citations cliquables vers l'Inspecteur, extraction 1-clic des references McMaster-Carr 9 caracteres, et navigation directe dans <code>Visual_Snapshots</code>.</li>
          <li><strong>Diagnostic CAO &amp; Arena A/B</strong> : propositions de correctifs strictement en lecture seule (aucune ecriture disque) et comparatif sequentiel TTFT / tok/s sur <code>BENCHMARK_QA_DBOT_120.json</code>.</li>
          <li><strong>Recherche Web Souveraine (SearXNG natif :8088, 0 Docker)</strong> : demarrez/arretez SearXNG a la demande depuis le bandeau haut (<code>0 Mo</code> lorsque arrete), puis cochez <code>+ Web (SearXNG)</code> dans <code>Chat D-Bot</code> ou <code>Arena</code>. Protection anti-SSRF sur les URL externes et priorite absolue a la verite terrain D-Bot.</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<script>
let AUDIT_DATA = null;
let SELECTED_RELS = new Set();

function toggleHelpModal(show) {
  var m = document.getElementById("help-modal");
  if (!m) return;
  m.className = show ? "modal-backdrop show" : "modal-backdrop";
}

document.addEventListener("keydown", function(e) {
  if (e.key === "Escape") {
    toggleHelpModal(false);
    toggleCadDiagModal(false);
  }
});

function escapeHtml(str) {
  return String(str == null ? "" : str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function switchTab(tabId, btn) {
  document.querySelectorAll(".tab-pane").forEach(function(el) { el.classList.remove("active"); });
  document.querySelectorAll("nav.tabs button").forEach(function(el) { el.classList.remove("active"); });
  document.getElementById("tab-" + tabId).classList.add("active");
  if (btn) btn.classList.add("active");
  if (tabId === "vision" && !VLM_SNAPSHOTS_LOADED) loadSnapshots();
  if (tabId === "retrieval" && !ARENA_QUESTIONS_LOADED) loadArenaQuestions();
}

function renderBars(containerId, items, color) {
  var el = document.getElementById(containerId);
  if (!items || !items.length) { el.innerHTML = "<span class='muted'>Aucune donnee.</span>"; return; }
  var maxVal = Math.max.apply(null, items.map(function(i) { return i.val; }).concat([1]));
  el.innerHTML = items.map(function(i) {
    var pct = Math.round((i.val / maxVal) * 100);
    return "<div class='bar-row'><div class='bar-lbl' title='" + escapeHtml(i.label) + "'>" + escapeHtml(i.label) +
      "</div><div class='bar-track'><div class='bar-fill' style='width:" + pct + "%;background:" + (i.color || color || "#38bdf8") + "'></div></div>" +
      "<div style='min-width:54px;text-align:right;'>" + escapeHtml(i.val) + "</div></div>";
  }).join("");
}

function formatElapsed(sec) {
  if (sec == null) return "-";
  var s = Math.max(0, Math.round(Number(sec)));
  var m = Math.floor(s / 60);
  var r = s % 60;
  return m > 0 ? (m + "m " + r + "s") : (r + "s");
}

function updateStoragePill(storage) {
  var sp = document.getElementById("storage-pill");
  if (!sp || !storage) return;
  var kind = storage.is_local_ssd ? "SSD local" : "Drive";
  var mir = storage.mirror_exists ? (" | Miroir " + storage.mirror_size_mb + " Mo") : " | Miroir absent";
  sp.className = storage.is_local_ssd ? "pill idle" : "pill";
  sp.textContent = kind + " " + storage.db_size_mb + " Mo" + mir;
  sp.title = "Base: " + (storage.db_path || "") + " | Miroir: " + (storage.mirror_path || "");
}

function updateLiveBanner(live) {
  var pill = document.getElementById("live-pill");
  var txt = document.getElementById("live-pill-txt");
  var banner = document.getElementById("ro-banner");
  var btnRe = document.getElementById("btn-run-reindex");
  var btnHy = document.getElementById("btn-run-hygiene");
  var chunkMeta = document.getElementById("live-chunk-meta");
  if (live && live.indexing_active) {
    pill.className = "pill live";
    txt.textContent = "Indexation active — Mode Lecture Seule";
    banner.className = "banner-ro show";
    var procParts = (live.processing_docs || []).map(function(p) {
      return escapeHtml(p.file_path) + " (" + p.chunks_count + " chunks, " + formatElapsed(p.elapsed_s) + ")";
    });
    var vramParts = (live.ollama_ps || []).map(function(m) {
      return escapeHtml(m.name) + " " + m.size_vram_gb + " Go VRAM (ctx " + m.context_length + ")";
    });
    var extraMeta = [];
    var prog = live.progress || null;
    var progBarHtml = "";
    var headLine = "<strong>Indexation en cours detectee</strong> (verrou=" + escapeHtml(live.lock_active) +
      ", moteur=" + escapeHtml((prog && prog.active_engine) || live.active_engine || "inconnu") +
      ", fichier=" + escapeHtml(live.current_progress || "-") + ").";

    if (prog) {
      var phaseLabels = { prepare: "Preparation", purge: "Purge", insert: "Insertion lots", mirror_backup: "Miroir Drive" };
      var phTxt = phaseLabels[prog.phase] || prog.phase || "En cours";
      var pct = Math.max(0, Math.min(100, Number(prog.pct || 0)));
      var unitTxt = (prog.total_units > 0)
        ? (prog.done_units + "/" + prog.total_units + " unites (" + pct.toFixed(0) + " %)")
        : ((prog.prepared_files || 0) + "/" + (prog.total_files || 0) + " fichiers prepares");
      var fileTxt = (prog.done_files || 0) + "/" + (prog.total_files || 0) + " fichiers termines";
      var batchTxt = (prog.total_batches > 0) ? (" | Lot " + (prog.current_batch_index || 0) + "/" + prog.total_batches + " (G" + (prog.current_batch_gleaning != null ? prog.current_batch_gleaning : "?") + ")") : "";
      headLine = "<strong>" + escapeHtml(phTxt) + " : " + escapeHtml(unitTxt) + "</strong> | " + escapeHtml(fileTxt) +
        escapeHtml(batchTxt) + " | Moteur: " + escapeHtml(prog.active_engine || live.active_engine || "auto") +
        " | Temps: " + formatElapsed(prog.elapsed_s);
      if (prog.current_batch_files && prog.current_batch_files.length) {
        extraMeta.push("Lot actif: " + prog.current_batch_files.slice(0, 4).map(escapeHtml).join(", ") + (prog.current_batch_files.length > 4 ? "..." : ""));
      }
      if (prog.failed_units > 0) extraMeta.push("Echecs: " + prog.failed_units);
      progBarHtml = "<div class='bar-track' style='margin:8px 0;height:12px;background:#1e293b;'><div class='bar-fill' style='width:" + pct + "%;background:#f59e0b;'></div></div>";
    }

    if (live.current_batch) extraMeta.push("Log lot: <strong>" + escapeHtml(live.current_batch) + "</strong>");
    if (live.current_chunk_progress) extraMeta.push("Chunk: <strong>" + escapeHtml(live.current_chunk_progress) + "</strong>");
    if (live.last_ollama_call) extraMeta.push(escapeHtml(live.last_ollama_call));
    if (live.summary_stats_line) extraMeta.push("Fusions: " + escapeHtml(live.summary_stats_line));
    if (procParts.length) extraMeta.push("En cours DB: " + procParts.join(" ; "));
    if (vramParts.length) extraMeta.push("Ollama VRAM: " + vramParts.join(" ; "));

    banner.innerHTML = headLine + progBarHtml + (extraMeta.length ? extraMeta.join(" | ") + "<br>" : "") +
      "Le dashboard reste pleinement operationnel en lecture seule ; les ecritures sont verrouillees par securite.";
    if (chunkMeta) {
      chunkMeta.innerHTML = extraMeta.length ? extraMeta.join(" | ") : "Indexation active en attente du prochain log chunk...";
    }
    if (btnRe) btnRe.disabled = true;
    if (btnHy) btnHy.disabled = true;
  } else {
    pill.className = "pill idle";
    txt.textContent = "Base disponible";
    banner.className = "banner-ro";
    if (chunkMeta) {
      var idleParts = [];
      if (live && live.last_log_time) idleParts.push("Dernier evenement log: " + live.last_log_time);
      if (live && live.current_chunk_progress) idleParts.push(live.current_chunk_progress);
      if (live && live.summary_stats_line) idleParts.push("Fusions: " + live.summary_stats_line);
      chunkMeta.textContent = idleParts.length ? idleParts.join(" | ") : "Aucune indexation active.";
    }
    if (btnRe) btnRe.disabled = false;
    if (btnHy) btnHy.disabled = false;
  }
  var logTail = document.getElementById("live-log-tail");
  if (logTail && live && live.recent_log_lines) {
    logTail.textContent = live.recent_log_lines.join("\\n");
  }
}

async function pollLiveStatus() {
  try {
    var resp = await fetch("/api/status");
    if (!resp.ok) return;
    var live = await resp.json();
    updateLiveBanner(live);
  } catch (e) {}
}

async function loadAudit(forceRefresh) {
  var btn = document.getElementById("btn-refresh-audit");
  if (btn) { btn.disabled = true; btn.textContent = "Rafraichissement..."; }
  try {
    var url = forceRefresh ? "/api/audit?refresh=1" : "/api/audit";
    var resp = await fetch(url);
    if (!resp.ok) { alert("Erreur chargement audit HTTP " + resp.status); return; }
    AUDIT_DATA = await resp.json();
    renderAll();
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = "Rafraichir l'audit"; }
  }
}

function renderAll() {
  if (!AUDIT_DATA) return;
  updateLiveBanner(AUDIT_DATA.live_indexing);
  updateStoragePill(AUDIT_DATA.storage);
  var s = AUDIT_DATA.summary || {};
  var st = AUDIT_DATA.storage || {};
  var g = AUDIT_DATA.graph_health || {};
  var hc = s.health_counts || {};
  var storageVal = (st.is_local_ssd ? "SSD local " : "Drive ") + (st.db_size_mb || 0) + " Mo";

  document.getElementById("kpi-overview").innerHTML = [
    ["Score moyen base", (s.avg_health_score || 0) + " / 100", "#38bdf8"],
    ["Critiques (a re-indexer)", hc.critical || 0, "#ef4444"],
    ["Avertissements", hc.warning || 0, "#f59e0b"],
    ["Fichiers sains", hc.healthy || 0, "#10b981"],
    ["Disque / doc_status / log", (s.disk_files_count || 0) + " / " + (s.doc_status_count || 0) + " / " + (s.indexed_files_log_count || 0), "#38bdf8"],
    ["Sections virtuelles ##", (s.sectioned_files_count || 0) + " fichiers / " + (s.virtual_sections_total || 0) + " sec.", "#38bdf8"],
    ["Stockage actif", storageVal, st.is_local_ssd ? "#10b981" : "#f59e0b"],
    ["Orphelins / Cache sans COMPLETE", (s.orphans_count || 0) + " / " + (s.cache_missing_complete || 0), "#f59e0b"],
    ["Derive CAO / BOM", (AUDIT_DATA.cad_drift && AUDIT_DATA.cad_drift.available) ? (s.cad_drift_alerts_count || 0) : "-", (s.cad_drift_alerts_count || 0) > 0 ? "#f59e0b" : "#10b981"]
  ].map(function(k) {
    return "<div class='card'><div class='kpi-val' style='color:" + k[2] + "'>" + escapeHtml(k[1]) + "</div><div class='kpi-lbl'>" + escapeHtml(k[0]) + "</div></div>";
  }).join("");

  var chunkBars = Object.keys(s.chunk_opts_breakdown || {}).map(function(k) {
    return { label: k, val: s.chunk_opts_breakdown[k], color: k.indexOf("1600") >= 0 ? "#10b981" : "#f59e0b" };
  });
  renderBars("chart-health", chunkBars);

  var reasonBars = Object.keys(s.reason_counts || {}).slice(0, 10).map(function(k) {
    return { label: k, val: s.reason_counts[k], color: "#ef4444" };
  });
  renderBars("chart-reasons", reasonBars);

  var engines = (AUDIT_DATA.log_summary && AUDIT_DATA.log_summary.engine_activations) || {};
  var engBars = Object.keys(engines).map(function(k) {
    return { label: k, val: engines[k], color: "#38bdf8" };
  });
  renderBars("chart-engines", engBars);

  var rSel = document.getElementById("f-reason");
  var prevR = rSel.value;
  rSel.innerHTML = "<option value='all'>Toutes anomalies</option>" + Object.keys(s.reason_counts || {}).map(function(r) {
    return "<option value='" + escapeHtml(r) + "'>" + escapeHtml(r) + " (" + s.reason_counts[r] + ")</option>";
  }).join("");
  if (prevR) rSel.value = prevR;

  renderFilesTable();
  renderGraphTab();
  renderCadTab();
}

function getFilteredDocs() {
  if (!AUDIT_DATA) return [];
  var q = (document.getElementById("f-search").value || "").toLowerCase();
  var st = document.getElementById("f-status").value;
  var pr = document.getElementById("f-priority").value;
  var rs = document.getElementById("f-reason").value;
  return (AUDIT_DATA.documents || []).filter(function(d) {
    if (st !== "all" && d.health_status !== st) return false;
    if (pr !== "all" && d.priority !== pr) return false;
    if (rs !== "all" && (d.reasons || []).indexOf(rs) < 0) return false;
    if (q) {
      var hay = (d.rel_path + " " + (d.reasons || []).join(" ")).toLowerCase();
      if (hay.indexOf(q) < 0) return false;
    }
    return true;
  });
}

function renderFilesTable() {
  var docs = getFilteredDocs();
  var tbody = document.getElementById("files-tbody");
  tbody.innerHTML = docs.slice(0, 300).map(function(d) {
    var checked = SELECTED_RELS.has(d.rel_path) ? "checked" : "";
    var ret = d.metric_retention != null ? Math.round(d.metric_retention * 100) + " %" : "-";
    var grd = d.grounding_rate != null ? Math.round(d.grounding_rate * 100) + " %" : "-";
    var tags = (d.reasons || []).map(function(r) { return "<span class='tag'>" + escapeHtml(r) + "</span>"; }).join("");
    var secBadge = (d.sections_count && d.sections_count > 0)
      ? " <span class='tag'>" + d.sections_count + " sec. ##</span>"
      : "";
    var gTag = "<span class='tag'>G" + (d.gleaning_policy != null ? d.gleaning_policy : 1) + "</span>";
    return "<tr>" +
      "<td><input type='checkbox' " + checked + " onchange='toggleSelectDoc(" + JSON.stringify(d.rel_path) + ", this.checked)'></td>" +
      "<td><span class='badge " + escapeHtml(d.health_status) + "'>" + d.score + "</span></td>" +
      "<td>" + escapeHtml(d.priority) + " " + gTag + "</td>" +
      "<td><code>" + escapeHtml(d.rel_path) + "</code>" + secBadge + "</td>" +
      "<td>" + escapeHtml(d.chunk_opts) + "</td>" +
      "<td>" + d.entities_count + " / " + d.relations_count + "</td>" +
      "<td>" + d.relations_per_1k_tok + "</td>" +
      "<td>" + ret + "</td>" +
      "<td>" + grd + "</td>" +
      "<td>" + (tags || "<span class='muted'>OK</span>") + "</td>" +
      "<td style='white-space:nowrap;'><button onclick='inspectFile(" + JSON.stringify(d.rel_path) + ")'>Inspecter</button> " +
      "<button onclick='openFileInChat(" + JSON.stringify(d.rel_path) + ")'>Discuter</button></td>" +
      "</tr>";
  }).join("");
}

function toggleSelectDoc(rel, isChecked) {
  if (isChecked) SELECTED_RELS.add(rel); else SELECTED_RELS.delete(rel);
}

function selectVisibleFiles(select) {
  if (!select) { SELECTED_RELS.clear(); renderFilesTable(); return; }
  getFilteredDocs().slice(0, 25).forEach(function(d) { SELECTED_RELS.add(d.rel_path); });
  renderFilesTable();
}

function _readReindexOpts() {
  return {
    provider: (document.getElementById("re-provider") && document.getElementById("re-provider").value) || "auto",
    summary_mode: (document.getElementById("re-summary") && document.getElementById("re-summary").value) || "deterministic",
    gleaning_mode: (document.getElementById("re-gleaning") && document.getElementById("re-gleaning").value) || "adaptive",
    batch_size: Number((document.getElementById("re-batch") && document.getElementById("re-batch").value) || 8),
    mirror_backup: Boolean(document.getElementById("re-mirror") && document.getElementById("re-mirror").checked)
  };
}

function copySelectedCommand() {
  var arr = Array.from(SELECTED_RELS);
  if (!arr.length) { alert("Cochez au moins un fichier."); return; }
  var opts = _readReindexOpts();
  var quoted = arr.map(function(p) { return '"' + p + '"'; }).join(" ");
  var cmd = '/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py"' +
    ' --provider ' + opts.provider +
    ' --summary-mode ' + opts.summary_mode +
    ' --gleaning-mode ' + opts.gleaning_mode +
    ' --batch-size ' + opts.batch_size +
    (opts.mirror_backup ? ' --mirror-backup' : '') +
    ' --files ' + quoted;
  var box = document.getElementById("cli-preview");
  box.style.display = "block";
  box.textContent = cmd;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(cmd).catch(function() {});
  }
}

async function triggerReindex() {
  var arr = Array.from(SELECTED_RELS);
  if (!arr.length) { alert("Cochez au moins un fichier."); return; }
  var opts = _readReindexOpts();
  var resp = await fetch("/api/actions/reindex", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      rel_paths: arr,
      provider: opts.provider,
      summary_mode: opts.summary_mode,
      gleaning_mode: opts.gleaning_mode,
      batch_size: opts.batch_size,
      mirror_backup: opts.mirror_backup
    })
  });
  var data = await resp.json();
  if (!resp.ok) { alert("Action refusee : " + (data.detail || resp.status)); return; }
  alert("Re-indexation V2 lancee (PID=" + data.pid + ", " + data.provider + ", gleaning=" + data.gleaning_mode + ") sur " + data.files_count + " fichier(s).");
  pollLiveStatus();
}

async function triggerHygiene(syncMirror) {
  var resp = await fetch("/api/actions/hygiene", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      full_hygiene: true,
      sync_mirror: Boolean(syncMirror),
      dry_run: false
    })
  });
  var data = await resp.json();
  if (!resp.ok) { alert("Action refusee : " + (data.detail || resp.status)); return; }
  alert("Hygiene & compaction lancee (PID=" + data.pid + (data.sync_mirror ? ", avec miroir Drive" : "") + ").");
  pollLiveStatus();
}

async function inspectFile(relPath) {
  switchTab("inspector", document.querySelector("nav.tabs button[data-tab='inspector']"));
  document.getElementById("insp-title").textContent = "Chargement de " + relPath + "...";
  var resp = await fetch("/api/file?rel_path=" + encodeURIComponent(relPath));
  if (!resp.ok) { document.getElementById("insp-title").textContent = "Erreur HTTP " + resp.status; return; }
  var data = await resp.json();
  var a = data.audit || {};
  var secTxt = (a.sections_count && a.sections_count > 0) ? (" | Sections: <strong>" + a.sections_count + "</strong>") : "";
  document.getElementById("insp-title").innerHTML = "<strong>" + escapeHtml(relPath) + "</strong> | Score: <span class='badge " +
    escapeHtml(a.health_status) + "'>" + a.score + "/100</span>" + secTxt + " | doc_id: <code>" + escapeHtml(a.doc_id || "absent") +
    "</code> <button style='margin-left:8px;' onclick='openFileInChat(" + JSON.stringify(relPath) + ")'>Discuter de ce fichier</button>";

  var chunksHtml = (data.chunks || []).map(function(c) {
    var errs = (c.syntax_errors || []).length
      ? "<div style='color:#fca5a5;margin:4px 0;'>Erreurs syntaxe : " + escapeHtml(c.syntax_errors.join(" ; ")) + "</div>"
      : "<div style='color:#6ee7b7;margin:4px 0;'>Syntaxe OK</div>";
    var rawCache = (c.cache_passes || []).map(function(p) {
      return "=== Passe " + p.pass_index + " (COMPLETE=" + p.has_complete + ", " + p.char_len + " car.) ===\\n" + p.raw_return;
    }).join("\\n\\n");
    var secInfo = c.section_key ? (" | Section: <code>" + escapeHtml(c.section_key) + "</code>") : "";
    return "<details style='margin-bottom:10px;border:1px solid #273654;border-radius:8px;padding:8px;'>" +
      "<summary><strong>Chunk #" + (c.order + 1) + "</strong> (" + c.tokens + " tok | VDB=" + c.in_vdb_chunks +
      " | Ent=" + c.entities.length + " | Rel=" + c.relations.length + ")" + secInfo + "</summary>" +
      errs +
      "<div class='two-col' style='margin-top:6px;'>" +
      "<div><div class='muted'>Texte source</div><pre>" + escapeHtml(c.content_preview) + "</pre></div>" +
      "<div><div class='muted'>Cache LLM brut</div><pre>" + escapeHtml(rawCache || "Aucune entree cache") + "</pre></div>" +
      "</div></details>";
  }).join("");
  document.getElementById("insp-chunks").innerHTML = chunksHtml || "<span class='muted'>Aucun chunk en base pour ce document.</span>";
  renderSubgraph(data.subgraph || { nodes: [], edges: [] });
}

function renderSubgraph(sg) {
  var svg = document.getElementById("subgraph-svg");
  var nodes = sg.nodes || [];
  var edges = sg.edges || [];
  document.getElementById("insp-graph-stats").textContent = nodes.length + " noeuds / " + edges.length + " aretes";
  if (!nodes.length) { svg.innerHTML = "<text x='20' y='40' fill='#94a3b8'>Aucun noeud associe dans GraphML.</text>"; return; }

  var W = 680, H = 420, cx = W / 2, cy = H / 2;
  var pos = {};
  nodes.forEach(function(n, idx) {
    var ring = idx === 0 ? 0 : (1 + Math.floor((idx - 1) / 14));
    var r = ring === 0 ? 0 : Math.min(185, 65 + (ring - 1) * 48);
    var angle = (idx * 2.39996);
    pos[n.id] = { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle), node: n };
  });

  var out = [];
  edges.forEach(function(e) {
    var a = pos[e.source], b = pos[e.target];
    if (!a || !b) return;
    out.push("<line x1='" + a.x.toFixed(1) + "' y1='" + a.y.toFixed(1) + "' x2='" + b.x.toFixed(1) + "' y2='" + b.y.toFixed(1) + "' stroke='#334155' stroke-width='1.2'/>");
  });
  nodes.forEach(function(n) {
    var p = pos[n.id];
    var rad = Math.max(5, Math.min(13, 4 + Math.sqrt(n.degree || 1) * 1.4));
    var col = n.degree === 0 ? "#ef4444" : "#38bdf8";
    out.push("<g style='cursor:pointer' onclick='showNodeInfo(" + JSON.stringify(n) + ")'>" +
      "<circle cx='" + p.x.toFixed(1) + "' cy='" + p.y.toFixed(1) + "' r='" + rad.toFixed(1) + "' fill='" + col + "' stroke='#0b1120' stroke-width='1.5'/>" +
      "<text x='" + (p.x + rad + 3).toFixed(1) + "' y='" + (p.y + 4).toFixed(1) + "' fill='#cbd5e1' font-size='10'>" + escapeHtml(n.id.slice(0, 26)) + "</text></g>");
  });
  svg.innerHTML = out.join("");
}

function showNodeInfo(n) {
  document.getElementById("insp-node-detail").innerHTML =
    "<strong>" + escapeHtml(n.id) + "</strong> [" + escapeHtml(n.type) + ", degre=" + n.degree + "] : " + escapeHtml(n.description || "-");
}

function renderGraphTab() {
  var g = AUDIT_DATA.graph_health || {};
  document.getElementById("kpi-graph").innerHTML = [
    ["Noeuds GraphML", g.nodes || 0],
    ["Aretes GraphML", g.edges || 0],
    ["Noeuds isoles (degre 0)", g.degree_zero_nodes || 0],
    ["Composantes connexes", g.connected_components || 0],
    ["Chunks KV / VDB", (g.text_chunks_count || 0) + " / " + (g.vdb_chunks_count || 0)],
    ["Vecteurs Ent / Rel", (g.vdb_entities_count || 0) + " / " + (g.vdb_relationships_count || 0)]
  ].map(function(k) {
    return "<div class='card'><div class='kpi-val'>" + escapeHtml(k[1]) + "</div><div class='kpi-lbl'>" + escapeHtml(k[0]) + "</div></div>";
  }).join("");

  var dups = g.potential_duplicate_clusters || [];
  document.getElementById("graph-dups").innerHTML = dups.length
    ? dups.map(function(d) { return "<div style='margin:4px 0;'><code>" + escapeHtml(d.key) + "</code> : " + escapeHtml(d.variants.join(" | ")) + "</div>"; }).join("")
    : "<span class='muted'>Aucun cluster doublon detecte.</span>";

  var orphans = AUDIT_DATA.orphans || [];
  document.getElementById("orphans-count").textContent = orphans.length;
  document.getElementById("graph-orphans").innerHTML = orphans.length
    ? orphans.slice(0, 100).map(function(o) { return "<div style='margin:4px 0;'><code>" + escapeHtml(o.doc_id) + "</code> — " + escapeHtml(o.rel_or_file) + "</div>"; }).join("")
    : "<span class='muted'>Aucun orphelin en base.</span>";

  loadAuditMd();
}

function _registerCadDriftItem(relPath, payload) {
  window._CAD_DRIFT_ITEMS = window._CAD_DRIFT_ITEMS || [];
  var idx = window._CAD_DRIFT_ITEMS.length;
  window._CAD_DRIFT_ITEMS.push({ rel_path: relPath || "", drift_item: payload || {} });
  return idx;
}

function _cadActionButtons(idx) {
  return "<button onclick='runCadDiagnose(" + idx + ", &quot;diagnose&quot;, &quot;ollama_gemma4&quot;)'>Diagnostiquer (Gemma4)</button> " +
    "<button onclick='runCadDiagnose(" + idx + ", &quot;diff&quot;, &quot;unsloth_qwen38&quot;)'>Proposer Diff (Unsloth)</button>";
}

function renderBitemporalBox(bt) {
  var btBox = document.getElementById("cad-bitemporal-box");
  if (!btBox) return;
  bt = bt || {};
  var pending = bt.pending_consolidations || [];
  var hdr = "<div style='margin-bottom:10px;'>" +
    "Niveau 1 (Verite Terrain) : <strong>" + (bt.level1_count || 0) + " fichiers</strong> | " +
    "Etudes STUDY_ anterieures (supplantees / t_invalid) : <strong>" + (bt.level2_superseded_count || 0) + "</strong> | " +
    "Etudes STUDY_ plus recentes a consolider : <span class='badge " + (pending.length > 0 ? "warning" : "healthy") + "'>" + pending.length + "</span>" +
    "</div>";
  if (!pending.length) {
    btBox.innerHTML = hdr + "<span class='badge healthy'>Aucune etude STUDY_ plus recente que son dossier Niveau 1.</span>";
    return;
  }
  var rows = pending.map(function(it) {
    var idx = _registerCadDriftItem(it.target_level1_rel_path || it.study_rel_path, it);
    return "<tr>" +
      "<td><code>" + escapeHtml(it.study_rel_path) + "</code></td>" +
      "<td>" + escapeHtml(it.study_date) + "</td>" +
      "<td><code>" + escapeHtml(it.target_level1_rel_path) + "</code></td>" +
      "<td>" + escapeHtml(it.target_level1_date) + "</td>" +
      "<td><span class='badge warning'>+" + escapeHtml(it.lead_days) + " j</span></td>" +
      "<td style='white-space:nowrap;'>" + _cadActionButtons(idx) + "</td>" +
      "</tr>";
  }).join("");
  btBox.innerHTML = hdr + "<table><thead><tr><th>Etude STUDY_ recente</th><th>Date etude</th><th>Dossier Niveau 1 cible</th><th>Date Niveau 1</th><th>Avance</th><th>Diagnostic IA</th></tr></thead><tbody>" + rows + "</tbody></table>";
}

function renderCadTab() {
  window._CAD_DRIFT_ITEMS = [];
  var cd = AUDIT_DATA.cad_drift || {};
  var kpiBox = document.getElementById("kpi-cad");
  var docsBody = document.getElementById("cad-docs-tbody");
  var bomBox = document.getElementById("cad-bom-box");
  var svgBox = document.getElementById("cad-svg-box");
  renderBitemporalBox(cd.bitemporal_hierarchy || {});
  if (!kpiBox || !docsBody || !bomBox || !svgBox) return;

  if (!cd.available) {
    kpiBox.innerHTML = "<div class='card'><div class='kpi-val'>Indisponible</div><div class='kpi-lbl'>AUDIT_METROLOGIQUE_Torse_et_Bassin.json absent</div></div>";
    docsBody.innerHTML = "<tr><td colspan='6' class='muted'>Aucun audit metrologique CAO trouve dans le workspace.</td></tr>";
    bomBox.innerHTML = "<span class='muted'>Donnees indisponibles.</span>";
    svgBox.innerHTML = "<span class='muted'>Donnees indisponibles.</span>";
    return;
  }

  var cs = cd.cad_summary || {};
  var bc = cd.bom_check || {};
  var sf = cd.svg_freshness || {};
  var docChecks = cd.doc_checks || [];
  var alignedCount = docChecks.filter(function(d) { return d.status === "aligned"; }).length;
  var driftCount = docChecks.filter(function(d) { return d.status === "drift"; }).length;
  var missLocal = (bc.missing_in_local_bom || []).length;
  var missGlobal = (bc.missing_in_global_bom || []).length;

  kpiBox.innerHTML = [
    ["Modele CAO Reference", (cs.document_name || "-") + " (" + (cs.total_mass_kg || 0) + " kg)", "#38bdf8"],
    ["Instances / Refs BOM CAO", (cs.instances_count || 0) + " / " + (cs.unique_bom_count || 0), "#38bdf8"],
    ["Docs Alignes / En Derive", alignedCount + " / " + driftCount, driftCount > 0 ? "#f59e0b" : "#10b981"],
    ["McMaster CAO (Manq. Loc / Glob)", (bc.cad_refs_count || 0) + " (" + missLocal + " / " + missGlobal + ")", (missLocal + missGlobal) > 0 ? "#ef4444" : "#10b981"],
    ["SVG Anterieurs a CAO", (sf.svgs_older_than_cad_count || 0) + " / " + (sf.total_svgs || 0), (sf.svgs_older_than_cad_count || 0) > 0 ? "#f59e0b" : "#10b981"]
  ].map(function(k) {
    return "<div class='card'><div class='kpi-val' style='color:" + k[2] + "'>" + escapeHtml(k[1]) + "</div><div class='kpi-lbl'>" + escapeHtml(k[0]) + "</div></div>";
  }).join("");

  docsBody.innerHTML = docChecks.map(function(d) {
    var badgeCls = d.status === "aligned" ? "healthy" : (d.status === "drift" ? "warning" : "critical");
    var vers = (d.versions_found && d.versions_found.length) ? d.versions_found.join(", ") : "-";
    var issHtml = (d.issues || []).length
      ? d.issues.map(function(i) { return "<div><span class='tag'>" + escapeHtml(i.code) + "</span> " + escapeHtml(i.message) + "</div>"; }).join("")
      : "<span class='muted'>Aucune derive detectee</span>";
    var idx = _registerCadDriftItem(d.rel_path, d);
    return "<tr>" +
      "<td><span class='badge " + badgeCls + "'>" + escapeHtml(d.status) + "</span></td>" +
      "<td><code>" + escapeHtml(d.rel_path) + "</code></td>" +
      "<td>" + escapeHtml(vers) + "</td>" +
      "<td>" + (d.checked_parts || 0) + " / " + (d.drifted_parts || 0) + "</td>" +
      "<td>" + issHtml + "</td>" +
      "<td style='white-space:nowrap;'>" + _cadActionButtons(idx) + "</td>" +
      "</tr>";
  }).join("");

  var bomParts = [];
  bomParts.push("<div style='margin-bottom:8px;'><strong>BOM Locale</strong> (<code>" + escapeHtml(bc.local_bom_rel || "-") + "</code>) : " +
    (missLocal === 0 ? "<span class='badge healthy'>100 % des " + (bc.cad_refs_count || 0) + " refs presentes</span>" : "<span class='badge critical'>" + missLocal + " manquante(s)</span>") + "</div>");
  if (missLocal > 0) {
    var bomLocalIdx = _registerCadDriftItem(bc.local_bom_rel || "", { kind: "missing_in_local_bom", items: bc.missing_in_local_bom });
    bomParts.push("<div style='margin-bottom:6px;'>" + _cadActionButtons(bomLocalIdx) + "</div>");
    bomParts.push("<div style='margin-bottom:8px;'>" + bc.missing_in_local_bom.map(function(m) {
      return "<div><span class='tag'>" + escapeHtml(m.ref) + "</span> " + escapeHtml(m.component_name || "") + " (qte " + (m.quantity || 1) + ")</div>";
    }).join("") + "</div>");
  }
  bomParts.push("<div style='margin-bottom:8px;'><strong>BOM Globale</strong> (<code>" + escapeHtml(bc.global_bom_rel || "-") + "</code>) : " +
    (missGlobal === 0 ? "<span class='badge healthy'>Complete</span>" : "<span class='badge warning'>" + missGlobal + " manquante(s) en CAO->Globale</span>") + "</div>");
  if (missGlobal > 0) {
    var bomGlobIdx = _registerCadDriftItem(bc.global_bom_rel || "", { kind: "missing_in_global_bom", items: bc.missing_in_global_bom });
    bomParts.push("<div style='margin-bottom:6px;'>" + _cadActionButtons(bomGlobIdx) + "</div>");
    bomParts.push("<div>" + bc.missing_in_global_bom.map(function(m) {
      return "<div><span class='tag'>" + escapeHtml(m.ref) + "</span> " + escapeHtml(m.component_name || "") + " (qte " + (m.quantity || 1) + ")</div>";
    }).join("") + "</div>");
  }
  if ((bc.extra_in_local_bom || []).length) {
    bomParts.push("<div class='muted' style='margin-top:8px;font-size:12px;'>Refs BOM locale absentes du JSON CAO : " + escapeHtml(bc.extra_in_local_bom.join(", ")) + "</div>");
  }
  bomBox.innerHTML = bomParts.join("");

  var svgParts = [];
  svgParts.push("<div style='margin-bottom:8px;'>Exports_CAO_DBot : <strong>" + (sf.exports_available ? "Disponible" : "Non monte") + "</strong>" +
    (sf.newest_snapshot_png ? (" | Dernier PNG : <code>" + escapeHtml(sf.newest_snapshot_png) + "</code>") : "") + "</div>");
  if ((sf.stale_manifest_pngs || []).length) {
    svgParts.push("<div style='margin-bottom:8px;color:#fca5a5;'>Snapshots manifestes desynchronises : " +
      sf.stale_manifest_pngs.map(function(x) { return "<code>" + escapeHtml(x.target) + "</code> (" + escapeHtml(x.reason) + ")"; }).join(", ") + "</div>");
  } else if (sf.exports_available) {
    svgParts.push("<div style='margin-bottom:8px;color:#6ee7b7;'>Parite SHA-256 des snapshots manifestes OK.</div>");
  }
  var olderSvgs = sf.svgs_older_than_cad || [];
  if (olderSvgs.length) {
    var svgIdx = _registerCadDriftItem("", { kind: "svgs_older_than_cad", svgs: olderSvgs });
    svgParts.push("<div style='margin-bottom:6px;'><strong>SVG anterieurs au JSON CAO (" + (sf.svgs_older_than_cad_count || olderSvgs.length) + ") :</strong> " + _cadActionButtons(svgIdx) + "</div>");
    svgParts.push(olderSvgs.map(function(s) {
      return "<div style='margin:3px 0;'><code>" + escapeHtml(s.file_name) + "</code> <span class='muted'>(-" + escapeHtml(s.lag_hours) + " h)</span></div>";
    }).join(""));
  } else {
    svgParts.push("<span class='badge healthy'>Tous les schemas SVG sont posterieurs ou egaux au JSON CAO.</span>");
  }
  svgBox.innerHTML = svgParts.join("");
}

async function loadAuditMd() {
  try {
    var resp = await fetch("/api/audit-integrity-md");
    if (!resp.ok) return;
    var data = await resp.json();
    document.getElementById("audit-md-preview").textContent = data.content || "Aucun AUDIT_INTEGRITE.md.";
  } catch (e) {}
}

async function runRetrieval() {
  var q = (document.getElementById("q-input").value || "").trim();
  if (!q) return;
  var box = document.getElementById("retrieval-results");
  box.innerHTML = "<div class='card'>Calcul embedding FastEmbed + reranking BGE en cours...</div>";
  var resp = await fetch("/api/retrieval/test", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: q,
      top_k: Number(document.getElementById("q-topk").value || 8),
      use_reranker: document.getElementById("q-rerank").checked,
      skip_images: document.getElementById("q-skipimg").checked
    })
  });
  var data = await resp.json();
  if (!resp.ok) { box.innerHTML = "<div class='card'>Erreur : " + escapeHtml(data.detail || resp.status) + "</div>"; return; }
  box.innerHTML = (data.results || []).map(function(r, idx) {
    var secTag = r.section_key ? (" <span class='tag'>sec: " + escapeHtml(r.section_key) + "</span>") : "";
    return "<div class='card' style='margin-bottom:10px;'>" +
      "<div><strong>#" + (idx + 1) + "</strong> <code>" + escapeHtml(r.file_path) + "</code>" + secTag + " | Cosine=" + r.cosine_score +
      (r.rerank_score != null ? " | Rerank=" + r.rerank_score : "") + "</div>" +
      "<pre style='margin-top:8px;'>" + escapeHtml(r.content) + "</pre></div>";
  }).join("") || "<div class='card'>Aucun extrait retourne.</div>";
}

async function runBenchmark() {
  var box = document.getElementById("benchmark-results");
  box.innerHTML = "<div class='card'>Evaluation de BENCHMARK_QA_DBOT_120.json en cours...</div>";
  var resp = await fetch("/api/benchmark/run", { method: "POST" });
  var data = await resp.json();
  if (!resp.ok) { box.innerHTML = "<div class='card'>Erreur : " + escapeHtml(data.detail || resp.status) + "</div>"; return; }
  var summary = "<div class='kpi-grid'>" +
    "<div class='card'><div class='kpi-val'>" + Math.round(data.recall_at_1 * 100) + " %</div><div class='kpi-lbl'>Recall@1</div></div>" +
    "<div class='card'><div class='kpi-val'>" + Math.round(data.recall_at_5 * 100) + " %</div><div class='kpi-lbl'>Recall@5</div></div>" +
    "<div class='card'><div class='kpi-val'>" + Math.round(data.recall_at_10 * 100) + " %</div><div class='kpi-lbl'>Recall@10</div></div>" +
    "<div class='card'><div class='kpi-val'>" + data.mrr + "</div><div class='kpi-lbl'>MRR</div></div>" +
    "<div class='card'><div class='kpi-val'>" + Math.round(data.numeric_token_hit_rate * 100) + " %</div><div class='kpi-lbl'>Token Cible Trouve</div></div>" +
    "</div>";
  var rows = (data.items || []).map(function(it) {
    var ok = it.matched_rank != null && it.matched_rank <= 5;
    return "<tr><td><span class='badge " + (ok ? "healthy" : "critical") + "'>" + (it.matched_rank || "MISS") + "</span></td>" +
      "<td>" + (it.token_found ? "OK" : "ABSENT") + "</td>" +
      "<td><code>" + escapeHtml(it.source_doc) + "</code></td>" +
      "<td><code>" + escapeHtml(it.numeric_token || "-") + "</code></td>" +
      "<td>" + escapeHtml(it.question) + "</td>" +
      "<td><code>" + escapeHtml(it.top_hit_file) + "</code> (" + it.top_hit_score + ")</td></tr>";
  }).join("");
  box.innerHTML = summary + "<table><thead><tr><th>Rang</th><th>Token</th><th>Source attendue</th><th>Token</th><th>Question</th><th>Top 1 remonte</th></tr></thead><tbody>" + rows + "</tbody></table>";
}

function downloadHtmlSnapshot() {
  window.open("/api/export/html", "_blank");
}

var CHAT_HISTORY = [];
var CHAT_TARGET_FILE = null;
var CHAT_ABORT = null;
var VLM_SNAPSHOTS_DATA = null;
var VLM_SNAPSHOTS_LOADED = false;
var VLM_SELECTED_SNAPSHOT = null;
var VLM_UPLOADED_B64 = null;
var ARENA_QUESTIONS = [];
var ARENA_QUESTIONS_LOADED = false;
var CAD_DIAG_LAST_TEXT = "";
var SEARXNG_RUNNING = false;

function copyTextOneClick(txt, btn) {
  if (!navigator.clipboard) return;
  navigator.clipboard.writeText(txt || "").then(function() {
    if (btn) {
      var old = btn.textContent;
      btn.textContent = "Copie OK";
      setTimeout(function() { btn.textContent = old; }, 1200);
    }
  });
}

function renderMcmasterChips(refs) {
  if (!refs || !refs.length) return "<span class='muted'>Aucune reference McMaster-Carr 9 car. detectee.</span>";
  return refs.map(function(code) {
    return "<button class='copy-chip' title='Copier uniquement " + escapeHtml(code) + " pour Fusion 360' onclick='copyTextOneClick(" + JSON.stringify(code) + ", this)'>" + escapeHtml(code) + " (Copier)</button>";
  }).join("");
}

function hasDollarOrLatexClient(txt) {
  if (!txt) return false;
  if (txt.indexOf(String.fromCharCode(36)) !== -1) return true;
  return /\\\\text\\{|\\\\approx|\\\\pm|\\\\varnothing|\\\\sqrt\\{|\\\\circ/.test(txt);
}

function formatRichAnswerHtml(rawText) {
  var txt = String(rawText || "");
  var fence = String.fromCharCode(96, 96, 96);
  var parts = txt.split(fence);
  if (parts.length === 1) return "<div style='white-space:pre-wrap;'>" + escapeHtml(txt) + "</div>";
  var out = [];
  for (var i = 0; i < parts.length; i++) {
    if (i % 2 === 0) {
      if (parts[i]) out.push("<div style='white-space:pre-wrap;'>" + escapeHtml(parts[i]) + "</div>");
    } else {
      var lines = parts[i].split("\\n");
      var lang = lines[0].trim();
      var codeBody = lines.length > 1 ? lines.slice(1).join("\\n") : parts[i];
      out.push("<div style='margin:6px 0;'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;'>" +
        "<span class='tag'>" + escapeHtml(lang || "code") + "</span>" +
        "<button class='copy-chip' onclick='copyTextOneClick(" + JSON.stringify(codeBody) + ", this)'>Copier bloc</button></div>" +
        "<pre style='margin:0;'>" + escapeHtml(codeBody) + "</pre></div>");
    }
  }
  return out.join("");
}

async function loadEnginesStatus() {
  try {
    var resp = await fetch("/api/engines/status");
    if (!resp.ok) return;
    var st = await resp.json();
    var ol = st.ollama || {};
    var un = st.unsloth || {};
    var sx = st.searxng || {};
    var mem = st.memory || {};
    var idx = st.indexing || {};

    var olPill = document.getElementById("ollama-pill");
    if (olPill) {
      if (!ol.reachable) {
        olPill.className = "pill down";
        olPill.textContent = "Ollama : OFF";
      } else {
        var loadedNames = (ol.loaded_models || []).map(function(m) { return m.name; });
        olPill.className = (ol.total_vram_gb > 0) ? "pill warn" : "pill idle";
        olPill.textContent = loadedNames.length
          ? ("Ollama : " + loadedNames.join(", ") + " (" + ol.total_vram_gb + " Go)")
          : "Ollama : Pret (0 Go VRAM)";
      }
    }

    var unPill = document.getElementById("unsloth-pill");
    if (unPill) {
      if (!un.reachable) {
        unPill.className = "pill down";
        unPill.textContent = "Unsloth : OFF";
      } else {
        unPill.className = "pill idle";
        unPill.textContent = "Unsloth : Actif (:8888)";
      }
    }

    var sxPill = document.getElementById("searxng-pill");
    var sxBtn = document.getElementById("btn-toggle-searxng");
    SEARXNG_RUNNING = Boolean(sx.reachable || sx.running_pid);
    if (sxPill) {
      if (!sx.installed) {
        sxPill.className = "pill down";
        sxPill.textContent = "SearXNG : Non installe";
      } else if (sx.reachable) {
        sxPill.className = "pill idle";
        sxPill.textContent = "SearXNG : Actif (" + (sx.rss_mb || 0) + " Mo)";
      } else {
        sxPill.className = "pill";
        sxPill.textContent = "SearXNG : OFF (0 Mo)";
      }
    }
    if (sxBtn) {
      sxBtn.disabled = !sx.installed;
      sxBtn.textContent = SEARXNG_RUNNING ? "Arreter SearXNG" : "Demarrer SearXNG";
    }

    var ramPill = document.getElementById("ram-pill");
    if (ramPill) {
      if (mem.available) {
        ramPill.className = mem.percent_used >= 85 ? "pill warn" : "pill";
        ramPill.textContent = "RAM : " + mem.used_gb + " / " + mem.total_gb + " Go (" + mem.percent_used + " %)";
      } else {
        ramPill.className = "pill";
        ramPill.textContent = "RAM : N/A";
      }
    }

    var warnBanner = document.getElementById("ram-guard-banner");
    var warnTxt = document.getElementById("ram-guard-text");
    if (warnBanner && warnTxt) {
      var reasons = st.warning_reasons || [];
      if (reasons.length) {
        warnBanner.classList.add("show");
        warnTxt.textContent = reasons.join(" | ");
      } else {
        warnBanner.classList.remove("show");
      }
    }

    var locked = Boolean(idx.lock_active);
    ["btn-unload-ollama", "btn-chat-send", "btn-vlm-analyze", "btn-run-arena"].forEach(function(id) {
      var el = document.getElementById(id);
      if (el) el.disabled = locked;
    });
  } catch (e) {}
}

async function toggleSearxng() {
  var btn = document.getElementById("btn-toggle-searxng");
  if (btn) {
    btn.disabled = true;
    btn.textContent = SEARXNG_RUNNING ? "Arret..." : "Demarrage...";
  }
  try {
    var endpoint = SEARXNG_RUNNING ? "/api/engines/searxng/stop" : "/api/engines/searxng/start";
    var resp = await fetch(endpoint, { method: "POST" });
    if (!resp.ok) {
      var err = await resp.json();
      alert("Action SearXNG echouee : " + (err.detail || resp.status));
    }
  } finally {
    await loadEnginesStatus();
  }
}

async function unloadOllamaVram() {
  var btn = document.getElementById("btn-unload-ollama");
  if (btn) btn.disabled = true;
  try {
    var resp = await fetch("/api/engines/ollama/unload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    if (!resp.ok) {
      var err = await resp.json();
      alert("Dechargement bloque : " + (err.detail || resp.status));
    }
  } finally {
    await loadEnginesStatus();
  }
}

function openFileInChat(relPath) {
  CHAT_TARGET_FILE = relPath;
  var modeSel = document.getElementById("chat-context-mode");
  if (modeSel) modeSel.value = "file";
  var badge = document.getElementById("chat-target-badge");
  var clr = document.getElementById("btn-clear-target-file");
  if (badge) { badge.style.display = "inline-block"; badge.textContent = "Fichier: " + relPath; }
  if (clr) clr.style.display = "inline-block";
  switchTab("chat", document.querySelector("nav.tabs button[data-tab='chat']"));
  var inp = document.getElementById("chat-input");
  if (inp) inp.focus();
}

function clearChatTargetFile() {
  CHAT_TARGET_FILE = null;
  var modeSel = document.getElementById("chat-context-mode");
  if (modeSel && modeSel.value === "file") modeSel.value = "hybrid";
  var badge = document.getElementById("chat-target-badge");
  var clr = document.getElementById("btn-clear-target-file");
  if (badge) badge.style.display = "none";
  if (clr) clr.style.display = "none";
}

function resetChatSession() {
  CHAT_HISTORY = [];
  var box = document.getElementById("chat-messages");
  if (box) box.innerHTML = "";
  var mc = document.getElementById("chat-mcmaster-box");
  if (mc) mc.innerHTML = "<span class='muted'>Session reinitialisee.</span>";
}

function setChatPrompt(txt) {
  var inp = document.getElementById("chat-input");
  if (inp) { inp.value = txt; inp.focus(); }
}

function stopChatStream() {
  if (CHAT_ABORT) CHAT_ABORT.abort();
}

async function sendChatMessage() {
  var inp = document.getElementById("chat-input");
  var query = (inp && inp.value || "").trim();
  if (!query) return;
  var profile = document.getElementById("chat-profile").value;
  var ctxMode = document.getElementById("chat-context-mode").value;
  if (ctxMode === "file" && !CHAT_TARGET_FILE) {
    alert("Selectionnez un fichier via Discuter dans la matrice, ou passez en mode Hybride.");
    return;
  }
  var thinking = document.getElementById("chat-thinking").checked;

  var logBox = document.getElementById("chat-messages");
  var userBubble = document.createElement("div");
  userBubble.className = "chat-msg user";
  userBubble.textContent = query;
  logBox.appendChild(userBubble);
  inp.value = "";

  var asstBubble = document.createElement("div");
  asstBubble.className = "chat-msg assistant";
  asstBubble.innerHTML = "<div class='chat-meta'><span class='tag'>" + escapeHtml(profile) + "</span> <span class='tag'>" + escapeHtml(ctxMode) + "</span> <span class='chat-stat muted'>Connexion...</span></div>" +
    "<details class='chat-think' style='display:none;'><summary>Raisonnement (thinking)</summary><pre class='think-pre' style='margin-top:6px;'></pre></details>" +
    "<div class='answer-body'></div><div class='chip-row answer-chips'></div>";
  logBox.appendChild(asstBubble);
  logBox.scrollTop = logBox.scrollHeight;

  var statEl = asstBubble.querySelector(".chat-stat");
  var thinkDet = asstBubble.querySelector(".chat-think");
  var thinkPre = asstBubble.querySelector(".think-pre");
  var ansBody = asstBubble.querySelector(".answer-body");
  var chipsEl = asstBubble.querySelector(".answer-chips");

  var sendBtn = document.getElementById("btn-chat-send");
  var stopBtn = document.getElementById("btn-chat-stop");
  sendBtn.disabled = true;
  stopBtn.disabled = false;
  CHAT_ABORT = new AbortController();

  var accAnswer = "";
  var accThink = "";
  try {
    var resp = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: CHAT_ABORT.signal,
      body: JSON.stringify({
        query: query,
        profile: profile,
        context_mode: ctxMode,
        target_rel_path: CHAT_TARGET_FILE,
        thinking: thinking,
        use_web: Boolean(document.getElementById("chat-use-web") && document.getElementById("chat-use-web").checked),
        web_categories: (document.getElementById("chat-web-cat") && document.getElementById("chat-web-cat").value) || "general",
        web_fetch_pages: Boolean(document.getElementById("chat-web-fetch") && document.getElementById("chat-web-fetch").checked),
        history: CHAT_HISTORY.slice(-8)
      })
    });
    if (!resp.ok) {
      var errObj = await resp.json();
      throw new Error(errObj.detail || ("HTTP " + resp.status));
    }
    var reader = resp.body.getReader();
    var decoder = new TextDecoder("utf-8");
    var buf = "";
    while (true) {
      var rd = await reader.read();
      if (rd.done) break;
      buf += decoder.decode(rd.value, { stream: true }).replace(/\\r/g, "");
      var frames = buf.split("\\n\\n");
      buf = frames.pop() || "";
      frames.forEach(function(frame) {
        var evName = "message";
        var dataStr = "";
        frame.split("\\n").forEach(function(ln) {
          if (ln.indexOf("event:") === 0) evName = ln.slice(6).trim();
          else if (ln.indexOf("data:") === 0) dataStr += ln.slice(5).trim();
        });
        if (!dataStr) return;
        var ev = JSON.parse(dataStr);
        if (evName === "context") {
          var srcBox = document.getElementById("chat-sources-box");
          var srcs = ev.sources || [];
          var webSrcs = ev.web_sources || [];
          var gSum = ev.graph_summary ? ("<div style='margin-bottom:8px;'><strong>Sous-graphe LightRAG</strong><pre>" + escapeHtml(ev.graph_summary) + "</pre></div>") : "";
          var sHtml = srcs.map(function(s) {
            return "<div style='border:1px solid #273654;border-radius:8px;padding:8px;margin-bottom:8px;'>" +
              "<div><a href='#' style='color:#38bdf8;font-weight:700;' onclick='inspectFile(" + JSON.stringify(s.rel_path) + ");return false;'>" + escapeHtml(s.rel_path) + "</a> " +
              "<span class='tag'>score=" + escapeHtml(s.score) + "</span></div>" +
              "<div class='muted' style='font-size:11.5px;margin-top:4px;'>" + escapeHtml(s.snippet) + "</div></div>";
          }).join("");
          var wHtml = "";
          if (ev.web_error) {
            wHtml += "<div style='border:1px solid #f59e0b;border-radius:8px;padding:8px;margin-bottom:8px;color:#fde68a;'>SearXNG indisponible : " + escapeHtml(ev.web_error) + "</div>";
          }
          if (webSrcs.length) {
            wHtml += "<div style='margin:8px 0 6px 0;'><strong>Sources Web SearXNG (" + webSrcs.length + ")</strong></div>" +
              webSrcs.map(function(w) {
                var safeHref = (w.url && (w.url.indexOf("http://") === 0 || w.url.indexOf("https://") === 0)) ? w.url : "#";
                return "<div style='border:1px solid #0e7490;border-radius:8px;padding:8px;margin-bottom:8px;background:#0a1929;'>" +
                  "<div><a href='" + escapeHtml(safeHref) + "' target='_blank' rel='noopener noreferrer' style='color:#22d3ee;font-weight:700;'>" + escapeHtml(w.title || safeHref) + "</a> " +
                  "<span class='tag'>" + escapeHtml(w.engine || "web") + "</span></div>" +
                  "<div class='muted' style='font-size:11px;word-break:break-all;'>" + escapeHtml(w.url || "") + "</div>" +
                  "<div class='muted' style='font-size:11.5px;margin-top:4px;'>" + escapeHtml(w.snippet || "") + "</div></div>";
              }).join("");
          }
          srcBox.innerHTML = gSum + sHtml + wHtml || "<span class='muted'>Mode sans retrieval RAG ni Web (0 sources).</span>";
        } else if (evName === "thinking") {
          accThink += (ev.delta || "");
          thinkDet.style.display = "block";
          thinkPre.textContent = accThink;
        } else if (evName === "token") {
          accAnswer += (ev.delta || "");
          statEl.textContent = "Streaming...";
          ansBody.textContent = accAnswer;
          logBox.scrollTop = logBox.scrollHeight;
        } else if (evName === "done") {
          accAnswer = ev.answer || accAnswer;
          ansBody.innerHTML = formatRichAnswerHtml(accAnswer);
          var m = ev.metrics || {};
          var latexFlag = ev.has_dollar_or_latex ? "<span class='badge warning'>Attention LaTeX/Dollar</span>" : "<span class='badge healthy'>Zero-Dollar OK</span>";
          statEl.innerHTML = "TTFT " + m.ttft_s + " s | " + m.tok_per_s + " tok/s | " + m.total_s + " s " + latexFlag;
          var mcRefs = ev.mcmaster_refs || [];
          document.getElementById("chat-mcmaster-box").innerHTML = renderMcmasterChips(mcRefs);
          chipsEl.innerHTML = "<button class='copy-chip' onclick='copyTextOneClick(" + JSON.stringify(accAnswer) + ", this)'>Copier reponse</button> " + (mcRefs.length ? renderMcmasterChips(mcRefs) : "");
          CHAT_HISTORY.push({ role: "user", content: query });
          CHAT_HISTORY.push({ role: "assistant", content: accAnswer });
        } else if (evName === "error") {
          statEl.innerHTML = "<span class='badge critical'>Erreur</span>";
          ansBody.textContent = ev.message || "Erreur moteur LLM";
        }
      });
    }
  } catch (err) {
    if (err.name === "AbortError") {
      statEl.textContent = "Interrompu par utilisateur";
    } else {
      statEl.innerHTML = "<span class='badge critical'>Erreur</span>";
      ansBody.textContent = err.message || String(err);
    }
  } finally {
    sendBtn.disabled = false;
    stopBtn.disabled = true;
    CHAT_ABORT = null;
    loadEnginesStatus();
  }
}

async function loadSnapshots() {
  var box = document.getElementById("vlm-snap-list");
  if (!box) return;
  try {
    var resp = await fetch("/api/vlm/snapshots");
    if (!resp.ok) return;
    VLM_SNAPSHOTS_DATA = await resp.json();
    VLM_SNAPSHOTS_LOADED = true;
    renderSnapshotList();
  } catch (e) {}
}

function renderSnapshotList() {
  var box = document.getElementById("vlm-snap-list");
  if (!box || !VLM_SNAPSHOTS_DATA) return;
  if (!VLM_SNAPSHOTS_DATA.available) {
    box.innerHTML = "<div class='muted' style='padding:10px;'>Dossier Visual_Snapshots non monte : " + escapeHtml(VLM_SNAPSHOTS_DATA.root) + "</div>";
    return;
  }
  var grp = document.getElementById("vlm-group").value;
  var flt = (document.getElementById("vlm-filter").value || "").toLowerCase();
  var groups = VLM_SNAPSHOTS_DATA.groups || {};
  var list = [];
  Object.keys(groups).forEach(function(k) {
    if (grp !== "ALL" && k !== grp) return;
    (groups[k] || []).forEach(function(item) { list.push(item); });
  });
  if (flt) list = list.filter(function(it) { return it.rel_path.toLowerCase().indexOf(flt) !== -1; });
  if (!list.length) {
    box.innerHTML = "<div class='muted' style='padding:10px;'>Aucun snapshot correspondant.</div>";
    return;
  }
  box.innerHTML = list.slice(0, 200).map(function(it) {
    var cls = VLM_SELECTED_SNAPSHOT === it.rel_path ? "snap-item active" : "snap-item";
    return "<div class='" + cls + "' onclick='selectSnapshot(" + JSON.stringify(it.rel_path) + ")'>" +
      "<span><code>" + escapeHtml(it.rel_path) + "</code></span>" +
      "<span class='muted'>" + it.size_kb + " Ko</span></div>";
  }).join("");
}

function selectSnapshot(relPath) {
  VLM_SELECTED_SNAPSHOT = relPath;
  VLM_UPLOADED_B64 = null;
  renderSnapshotList();
  var img = document.getElementById("vlm-preview-img");
  var lbl = document.getElementById("vlm-selected-label");
  lbl.textContent = "Snapshot : " + relPath;
  img.src = "/api/vlm/snapshot-image?rel_path=" + encodeURIComponent(relPath);
  img.style.display = "inline-block";
}

function handleVlmFileInput(files) {
  if (!files || !files.length) return;
  var f = files[0];
  var reader = new FileReader();
  reader.onload = function(ev) {
    VLM_SELECTED_SNAPSHOT = null;
    VLM_UPLOADED_B64 = String(ev.target.result || "");
    renderSnapshotList();
    var img = document.getElementById("vlm-preview-img");
    var lbl = document.getElementById("vlm-selected-label");
    lbl.textContent = "Image importee : " + f.name;
    img.src = VLM_UPLOADED_B64;
    img.style.display = "inline-block";
  };
  reader.readAsDataURL(f);
}

function setVlmPrompt(txt) {
  var el = document.getElementById("vlm-prompt");
  if (el) { el.value = txt; el.focus(); }
}

async function runVlmAnalysis() {
  var prompt = (document.getElementById("vlm-prompt").value || "").trim();
  if (!prompt) { alert("Saisissez une question pour l'analyse image."); return; }
  if (!VLM_SELECTED_SNAPSHOT && !VLM_UPLOADED_B64) { alert("Selectionnez un snapshot ou importez une image."); return; }
  var out = document.getElementById("vlm-result");
  var btn = document.getElementById("btn-vlm-analyze");
  btn.disabled = true;
  out.innerHTML = "<div class='card'>Analyse multimodale VLM en cours...</div>";
  try {
    var resp = await fetch("/api/vlm/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: prompt,
        profile: document.getElementById("vlm-profile").value,
        snapshot_rel_path: VLM_SELECTED_SNAPSHOT,
        image_b64: VLM_UPLOADED_B64,
        include_cad_context: document.getElementById("vlm-include-cad").checked,
        thinking: document.getElementById("vlm-thinking").checked
      })
    });
    var data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || ("HTTP " + resp.status));
    var m = data.metrics || {};
    var thinkHtml = data.thinking ? ("<details class='chat-think'><summary>Raisonnement VLM</summary><pre>" + escapeHtml(data.thinking) + "</pre></details>") : "";
    var srcsHtml = (data.sources || []).map(function(s) {
      return "<span class='tag'><a href='#' style='color:#38bdf8;' onclick='inspectFile(" + JSON.stringify(s.rel_path) + ");return false;'>" + escapeHtml(s.rel_path) + "</a></span>";
    }).join(" ");
    out.innerHTML = "<div class='card'>" +
      "<div class='chat-meta'><strong>" + escapeHtml(data.model) + "</strong> | TTFT " + m.ttft_s + " s | " + m.tok_per_s + " tok/s | " + m.total_s + " s " +
      (data.has_dollar_or_latex ? "<span class='badge warning'>LaTeX detecte</span>" : "<span class='badge healthy'>Zero-Dollar OK</span>") + "</div>" +
      thinkHtml +
      formatRichAnswerHtml(data.answer) +
      "<div class='chip-row'><button class='copy-chip' onclick='copyTextOneClick(" + JSON.stringify(data.answer) + ", this)'>Copier analyse</button>" + renderMcmasterChips(data.mcmaster_refs) + "</div>" +
      (srcsHtml ? ("<div style='margin-top:8px;'>Sources RAG : " + srcsHtml + "</div>") : "") +
      "</div>";
  } catch (err) {
    out.innerHTML = "<div class='card'><span class='badge critical'>Erreur VLM</span> " + escapeHtml(err.message || err) + "</div>";
  } finally {
    btn.disabled = false;
    loadEnginesStatus();
  }
}

function toggleCadDiagModal(show) {
  var m = document.getElementById("cad-diag-modal");
  if (m) m.className = show ? "modal-backdrop show" : "modal-backdrop";
}

function copyCadDiagText() {
  copyTextOneClick(CAD_DIAG_LAST_TEXT, document.getElementById("btn-copy-cad-diag"));
}

async function runCadDiagnose(idx, mode, profile) {
  var entry = (window._CAD_DRIFT_ITEMS || [])[idx];
  if (!entry) return;
  document.getElementById("cad-diag-title").textContent = (mode === "diff" ? "Proposition Diff Read-Only (" + profile + ")" : "Diagnostic Derive CAO (" + profile + ")") + (entry.rel_path ? (" — " + entry.rel_path) : "");
  document.getElementById("cad-diag-meta").textContent = "Generation en cours (strictement lecture seule, aucune modification disque)...";
  document.getElementById("cad-diag-chips").innerHTML = "";
  document.getElementById("cad-diag-body").textContent = "Patientez...";
  CAD_DIAG_LAST_TEXT = "";
  toggleCadDiagModal(true);
  try {
    var resp = await fetch("/api/cad/diagnose", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mode: mode,
        profile: profile,
        rel_path: entry.rel_path,
        drift_item: entry.drift_item
      })
    });
    var data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || ("HTTP " + resp.status));
    var m = data.metrics || {};
    CAD_DIAG_LAST_TEXT = data.answer || "";
    document.getElementById("cad-diag-meta").textContent = "Modele : " + data.model + " | TTFT " + m.ttft_s + " s | " + m.tok_per_s + " tok/s | Zero modification disque";
    document.getElementById("cad-diag-chips").innerHTML = renderMcmasterChips(data.mcmaster_refs || []);
    document.getElementById("cad-diag-body").textContent = CAD_DIAG_LAST_TEXT;
  } catch (err) {
    document.getElementById("cad-diag-meta").textContent = "Echec";
    document.getElementById("cad-diag-body").textContent = err.message || String(err);
  } finally {
    loadEnginesStatus();
  }
}

async function loadArenaQuestions() {
  var sel = document.getElementById("arena-q-select");
  if (!sel) return;
  try {
    var resp = await fetch("/api/arena/questions");
    if (!resp.ok) return;
    var data = await resp.json();
    ARENA_QUESTIONS = data.items || [];
    ARENA_QUESTIONS_LOADED = true;
    sel.innerHTML = "<option value=''>-- Charger une question depuis BENCHMARK_QA_DBOT_120.json (" + ARENA_QUESTIONS.length + ") --</option>" +
      ARENA_QUESTIONS.map(function(it, i) {
        return "<option value='" + i + "'>[" + escapeHtml(it.id) + "] " + escapeHtml(it.question.slice(0, 95)) + "</option>";
      }).join("");
  } catch (e) {}
}

function onSelectArenaQuestion() {
  var sel = document.getElementById("arena-q-select");
  var idx = sel && sel.value !== "" ? Number(sel.value) : -1;
  if (idx < 0 || !ARENA_QUESTIONS[idx]) return;
  var it = ARENA_QUESTIONS[idx];
  document.getElementById("arena-question").value = it.question || "";
  document.getElementById("arena-token").value = it.numeric_token || "";
}

function toggleCustomArenaFields() {
  var isCust = document.getElementById("arena-t2").value === "custom_openai";
  document.getElementById("arena-custom-url").style.display = isCust ? "inline-block" : "none";
  document.getElementById("arena-custom-model").style.display = isCust ? "inline-block" : "none";
}

async function runArena() {
  var q = (document.getElementById("arena-question").value || "").trim();
  if (!q) { alert("Saisissez une question pour lancer l'Arena."); return; }
  var t1 = document.getElementById("arena-t1").value;
  var t2 = document.getElementById("arena-t2").value;
  var target2 = { profile: t2 };
  if (t2 === "custom_openai") {
    target2.custom_url = document.getElementById("arena-custom-url").value.trim();
    target2.custom_model = document.getElementById("arena-custom-model").value.trim();
  }
  var out = document.getElementById("arena-results");
  var btn = document.getElementById("btn-run-arena");
  btn.disabled = true;
  out.innerHTML = "<div class='card'>Execution sequentielle en cours (A puis B)...</div>";
  try {
    var resp = await fetch("/api/arena/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: q,
        targets: [{ profile: t1 }, target2],
        use_rag: document.getElementById("arena-rag").checked,
        use_web: Boolean(document.getElementById("arena-web") && document.getElementById("arena-web").checked),
        context_mode: document.getElementById("arena-rag-mode").value,
        unload_ollama_between: document.getElementById("arena-unload-between").checked,
        expected_token: document.getElementById("arena-token").value.trim() || null
      })
    });
    var data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || ("HTTP " + resp.status));
    var rows = (data.results || []).map(function(r) {
      var m = r.metrics || {};
      var tokCell = r.token_matched == null ? "-" : (r.token_matched ? "<span class='badge healthy'>OK</span>" : "<span class='badge critical'>ABSENT</span>");
      var lxCell = r.has_dollar_or_latex ? "<span class='badge warning'>LaTeX/Dollar</span>" : "<span class='badge healthy'>OK</span>";
      return "<tr><td><strong>" + escapeHtml(r.label) + "</strong></td>" +
        "<td><span class='badge " + (r.status === "ok" ? "healthy" : "critical") + "'>" + escapeHtml(r.status) + "</span></td>" +
        "<td>" + (m.ttft_s != null ? m.ttft_s + " s" : "-") + "</td>" +
        "<td>" + (m.tok_per_s || 0) + " tok/s</td>" +
        "<td>" + (m.total_s || 0) + " s</td>" +
        "<td>" + (r.ram_used_gb != null ? r.ram_used_gb + " Go" : "-") + "</td>" +
        "<td>" + tokCell + "</td><td>" + lxCell + "</td></tr>";
    }).join("");
    var cards = (data.results || []).map(function(r) {
      return "<div class='card'>" +
        "<div class='chat-meta'><strong>" + escapeHtml(r.label) + "</strong> | " + (r.metrics.tok_per_s || 0) + " tok/s</div>" +
        (r.error ? ("<div style='color:#fca5a5;'>" + escapeHtml(r.error) + "</div>") : formatRichAnswerHtml(r.answer)) +
        "<div class='chip-row'><button class='copy-chip' onclick='copyTextOneClick(" + JSON.stringify(r.answer || "") + ", this)'>Copier</button>" + renderMcmasterChips(r.mcmaster_refs || []) + "</div></div>";
    }).join("");
    out.innerHTML = "<table><thead><tr><th>Cible</th><th>Statut</th><th>TTFT</th><th>Debit</th><th>Duree</th><th>RAM Mac</th><th>Token Cible</th><th>Zero-Dollar</th></tr></thead><tbody>" + rows + "</tbody></table>" +
      "<div class='arena-cols'>" + cards + "</div>";
  } catch (err) {
    out.innerHTML = "<div class='card'><span class='badge critical'>Erreur Arena</span> " + escapeHtml(err.message || err) + "</div>";
  } finally {
    btn.disabled = false;
    loadEnginesStatus();
  }
}

(function initVlmDropZone() {
  var dz = document.getElementById("vlm-drop-zone");
  if (!dz) return;
  dz.addEventListener("dragover", function(e) { e.preventDefault(); dz.classList.add("dragover"); });
  dz.addEventListener("dragleave", function() { dz.classList.remove("dragover"); });
  dz.addEventListener("drop", function(e) {
    e.preventDefault();
    dz.classList.remove("dragover");
    if (e.dataTransfer && e.dataTransfer.files) handleVlmFileInput(e.dataTransfer.files);
  });
})();

loadAudit(false);
loadEnginesStatus();
setInterval(pollLiveStatus, 5000);
setInterval(loadEnginesStatus, 10000);
</script>
</body>
</html>"""


def create_app(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    docs_root: Path = DEFAULT_DOCS_ROOT,
    log_path: Path = DEFAULT_LOG_PATH,
    benchmark_path: Path = DEFAULT_BENCHMARK_PATH,
    audit_md_path: Path = DEFAULT_AUDIT_MD_PATH,
    snapshots_root: Path = DEFAULT_SNAPSHOTS_ROOT,
    cache_ttl_s: float = 20.0,
) -> FastAPI:
    """Construit l'application FastAPI du cockpit qualite LightRAG D-Bot."""
    app = FastAPI(title="D-Bot LightRAG Quality Monitor", version="1.1.0")
    audit_cache = _AuditCache(
        db_path=db_path, docs_root=docs_root, log_path=log_path, ttl_s=cache_ttl_s
    )
    searcher = _ReadOnlyVectorSearcher(db_path=db_path)

    def _assert_llm_ready_for_interactive_use() -> None:
        live = detect_live_indexing_status(db_path=db_path, log_path=log_path)
        if live["indexing_active"] or is_indexing_lock_active(Path(db_path)):
            raise HTTPException(
                status_code=409,
                detail="Une indexation RAG est active (.indexing.lock). Inference et gestion VRAM bloquees par securite.",
            )

    @app.get("/", response_class=HTMLResponse)
    def index_page() -> HTMLResponse:
        return HTMLResponse(_build_dashboard_html())

    @app.get("/api/status")
    def api_status() -> JSONResponse:
        return JSONResponse(detect_live_indexing_status(db_path=db_path, log_path=log_path))

    @app.get("/api/audit")
    def api_audit(refresh: bool = Query(default=False)) -> JSONResponse:
        return JSONResponse(audit_cache.get_report(force_refresh=refresh))

    @app.get("/api/cad-drift")
    def api_cad_drift(refresh: bool = Query(default=False)) -> JSONResponse:
        report = audit_cache.get_report(force_refresh=refresh)
        return JSONResponse(report.get("cad_drift") or {"available": False})

    @app.get("/api/file")
    def api_file_detail(rel_path: str = Query(..., min_length=1)) -> JSONResponse:
        try:
            detail = inspect_document_detail(
                rel_path, db_path=db_path, docs_root=docs_root
            )
            return JSONResponse(detail)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/audit-integrity-md")
    def api_audit_integrity_md() -> JSONResponse:
        if not Path(audit_md_path).is_file():
            return JSONResponse({"exists": False, "content": ""})
        txt = Path(audit_md_path).read_text(encoding="utf-8", errors="replace")
        return JSONResponse({"exists": True, "content": txt[:120000]})

    @app.get("/api/export/html")
    def api_export_html() -> Response:
        report = audit_cache.get_report(force_refresh=False)
        html_doc = export_static_html_report(report, output_path=None)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        headers = {
            "Content-Disposition": f'attachment; filename="dbot_rag_health_{stamp}.html"'
        }
        return Response(content=html_doc, media_type="text/html; charset=utf-8", headers=headers)

    @app.post("/api/retrieval/test")
    def api_retrieval_test(req: RetrievalRequest) -> JSONResponse:
        try:
            hits = searcher.search(
                req.query,
                top_k=req.top_k,
                use_reranker=req.use_reranker,
                skip_images=req.skip_images,
            )
            return JSONResponse({"query": req.query, "results": hits})
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/api/benchmark/run")
    def api_benchmark_run() -> JSONResponse:
        return JSONResponse(
            _run_benchmark_eval(
                searcher, Path(benchmark_path), top_k=10, use_reranker=True
            )
        )

    @app.post("/api/actions/reindex")
    def api_action_reindex(req: ReindexRequest) -> JSONResponse:
        live = detect_live_indexing_status(db_path=db_path, log_path=log_path)
        if live["indexing_active"] or is_indexing_lock_active(Path(db_path)):
            raise HTTPException(
                status_code=409,
                detail="Une indexation RAG est deja en cours. Re-indexation bloquee par securite.",
            )
        if req.provider not in ("ollama", "auto", "gemini", "1minai"):
            raise HTTPException(status_code=400, detail="Fournisseur non autorise.")
        if req.summary_mode not in ("deterministic", "gemma4", "llm"):
            raise HTTPException(status_code=400, detail="summary_mode invalide.")
        if req.gleaning_mode not in ("adaptive", "on", "off"):
            raise HTTPException(status_code=400, detail="gleaning_mode invalide.")
        if req.model and not _MODEL_NAME_RE.match(req.model):
            raise HTTPException(status_code=400, detail="Nom de modele invalide.")

        validated_rels = _validate_target_rel_paths(req.rel_paths, Path(docs_root))
        index_script = Path(__file__).resolve().parent / "index_docs.py"
        cmd = [
            sys.executable,
            str(index_script),
            "--provider",
            req.provider,
            "--summary-mode",
            req.summary_mode,
            "--gleaning-mode",
            req.gleaning_mode,
            "--batch-size",
            str(req.batch_size),
        ]
        if req.model:
            cmd.extend(["--model", req.model])
        if req.mirror_backup:
            cmd.append("--mirror-backup")
        if req.no_section_split:
            cmd.append("--no-section-split")
        cmd.extend(["--files", *validated_rels])

        env = os.environ.copy()
        env["RAG_DB_PATH"] = str(db_path)
        proc = subprocess.Popen(cmd, env=env, cwd=str(docs_root))
        return JSONResponse(
            status_code=202,
            content={
                "status": "started",
                "pid": proc.pid,
                "files_count": len(validated_rels),
                "files": validated_rels,
                "provider": req.provider,
                "summary_mode": req.summary_mode,
                "gleaning_mode": req.gleaning_mode,
                "batch_size": req.batch_size,
                "mirror_backup": req.mirror_backup,
            },
        )

    @app.post("/api/actions/hygiene")
    def api_action_hygiene(req: HygieneRequest) -> JSONResponse:
        live = detect_live_indexing_status(db_path=db_path, log_path=log_path)
        if live["indexing_active"] or is_indexing_lock_active(Path(db_path)):
            raise HTTPException(
                status_code=409,
                detail="Une indexation RAG est deja en cours. Maintenance bloquee par securite.",
            )
        repair_script = Path(__file__).resolve().parent / "repair_db_sync.py"
        cmd = [
            sys.executable,
            str(repair_script),
            "--db-path",
            str(db_path),
            "--docs-root",
            str(docs_root),
        ]
        if req.full_hygiene:
            cmd.append("--full-hygiene")
        if not req.dry_run:
            cmd.extend(["--apply", "--no-backup"])
        if req.sync_mirror:
            cmd.append("--sync-mirror")

        env = os.environ.copy()
        env["RAG_DB_PATH"] = str(db_path)
        proc = subprocess.Popen(cmd, env=env, cwd=str(docs_root))
        return JSONResponse(
            status_code=202,
            content={
                "status": "started",
                "pid": proc.pid,
                "dry_run": req.dry_run,
                "full_hygiene": req.full_hygiene,
                "sync_mirror": req.sync_mirror,
            },
        )

    @app.get("/api/engines/status")
    def api_engines_status() -> JSONResponse:
        return JSONResponse(get_engines_status(db_path=db_path, log_path=log_path))

    @app.post("/api/engines/ollama/unload")
    def api_engines_ollama_unload(req: UnloadOllamaRequest) -> JSONResponse:
        _assert_llm_ready_for_interactive_use()
        res = unload_ollama_models(req.models or None)
        return JSONResponse(res)

    @app.post("/api/engines/searxng/start")
    def api_engines_searxng_start() -> JSONResponse:
        try:
            return JSONResponse(start_searxng())
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/engines/searxng/stop")
    def api_engines_searxng_stop() -> JSONResponse:
        return JSONResponse(stop_searxng())

    @app.post("/api/web/search")
    def api_web_search(req: WebSearchRequest) -> JSONResponse:
        res = search_searxng(
            req.query,
            max_results=req.max_results,
            categories=req.categories,
            fetch_pages=req.fetch_pages,
        )
        if not res.get("available"):
            raise HTTPException(
                status_code=502,
                detail=str(res.get("error") or "SearXNG local injoignable."),
            )
        return JSONResponse(res)

    @app.post("/api/chat/stream")
    def api_chat_stream(req: ChatStreamRequest) -> StreamingResponse:
        _assert_llm_ready_for_interactive_use()
        try:
            target = resolve_profile_target(
                req.profile,
                custom_url=req.custom_url,
                custom_model=req.custom_model,
                thinking=req.thinking,
            )
            ctx_info = build_chat_context(
                query=req.query,
                context_mode=req.context_mode,
                docs_root=docs_root,
                db_path=db_path,
                searcher=searcher,
                target_rel_path=req.target_rel_path,
                top_k=req.top_k,
                use_web=req.use_web,
                web_max_results=req.web_max_results,
                web_categories=req.web_categories,
                web_fetch_pages=req.web_fetch_pages,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        messages: list[dict[str, Any]] = [{"role": "system", "content": build_system_prompt(use_web=req.use_web)}]
        for prev in req.history[-8:]:
            messages.append({"role": prev.role, "content": prev.content})
        user_content = (
            f"Contexte D-Bot recupere (mode={ctx_info['mode']}, web={req.use_web}) :\n{ctx_info['context_text']}\n\nQuestion :\n{req.query}"
            if ctx_info.get("context_text")
            else req.query
        )
        messages.append({"role": "user", "content": user_content})

        def _sse_gen() -> Any:
            ctx_payload = {
                "mode": ctx_info["mode"],
                "sources": ctx_info.get("sources") or [],
                "web_sources": ctx_info.get("web_sources") or [],
                "web_error": ctx_info.get("web_error"),
                "graph_summary": ctx_info.get("graph_summary") or "",
            }
            yield f"event: context\ndata: {json.dumps(ctx_payload, ensure_ascii=False)}\n\n"
            for ev in stream_llm_chat(target=target, messages=messages, max_tokens=req.max_tokens):
                ev_type = str(ev.get("type") or "token")
                yield f"event: {ev_type}\ndata: {json.dumps(ev, ensure_ascii=False)}\n\n"

        return StreamingResponse(_sse_gen(), media_type="text/event-stream")

    @app.get("/api/vlm/snapshots")
    def api_vlm_snapshots() -> JSONResponse:
        return JSONResponse(list_visual_snapshots(snapshots_root=snapshots_root))

    @app.get("/api/vlm/snapshot-image")
    def api_vlm_snapshot_image(rel_path: str = Query(..., min_length=1)) -> Response:
        try:
            img_path = resolve_snapshot_path(rel_path, snapshots_root=snapshots_root)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        ext = img_path.suffix.lower()
        media = "image/png" if ext == ".png" else ("image/webp" if ext == ".webp" else "image/jpeg")
        return Response(content=img_path.read_bytes(), media_type=media)

    @app.post("/api/vlm/analyze")
    def api_vlm_analyze(req: VlmAnalyzeRequest) -> JSONResponse:
        _assert_llm_ready_for_interactive_use()
        if not req.snapshot_rel_path and not req.image_b64:
            raise HTTPException(status_code=400, detail="Fournissez snapshot_rel_path ou image_b64.")
        try:
            target = resolve_profile_target(req.profile, thinking=req.thinking)
            if req.snapshot_rel_path:
                img_path = resolve_snapshot_path(req.snapshot_rel_path, snapshots_root=snapshots_root)
                img_b64 = encode_image_file_b64(img_path)
                img_label = req.snapshot_rel_path
            else:
                img_b64 = str(req.image_b64 or "").strip()
                img_label = "image_importee"
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        cad_ctx = (
            build_vlm_cad_context(
                docs_root=docs_root,
                searcher=searcher,
                query_hint=f"{img_label} {req.prompt}",
            )
            if req.include_cad_context
            else {"cad_context": "", "rag_context": "", "sources": []}
        )
        user_txt = (
            f"Analyse visuelle CAO/FEA pour : {img_label}\n"
            + (f"\nMetriques JSON CAO associees :\n{cad_ctx['cad_context']}\n" if cad_ctx.get("cad_context") else "")
            + (f"\nExtraits RAG associes :\n{cad_ctx['rag_context']}\n" if cad_ctx.get("rag_context") else "")
            + f"\nConsigne utilisateur :\n{req.prompt}"
        )
        messages = [
            {"role": "system", "content": DBOT_SYSTEM_PROMPT_BASE},
            {"role": "user", "content": user_txt},
        ]
        try:
            res = complete_llm_chat(
                target=target,
                messages=messages,
                images_b64=[img_b64],
                max_tokens=req.max_tokens,
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        return JSONResponse(
            {
                "image_label": img_label,
                "model": res["metrics"]["model"],
                "answer": res["answer"],
                "thinking": res.get("thinking") or "",
                "mcmaster_refs": res.get("mcmaster_refs") or [],
                "has_dollar_or_latex": bool(res.get("has_dollar_or_latex")),
                "metrics": res["metrics"],
                "sources": cad_ctx.get("sources") or [],
            }
        )

    @app.post("/api/cad/diagnose")
    def api_cad_diagnose(req: CadDiagnoseRequest) -> JSONResponse:
        _assert_llm_ready_for_interactive_use()
        try:
            target = resolve_profile_target(req.profile, thinking=req.thinking)
            messages = build_cad_drift_messages(
                mode=req.mode,
                rel_path=req.rel_path,
                drift_item=req.drift_item,
                docs_root=docs_root,
            )
            res = complete_llm_chat(target=target, messages=messages, max_tokens=1600)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return JSONResponse(
            {
                "mode": req.mode,
                "rel_path": req.rel_path,
                "model": res["metrics"]["model"],
                "answer": res["answer"],
                "thinking": res.get("thinking") or "",
                "mcmaster_refs": res.get("mcmaster_refs") or [],
                "has_dollar_or_latex": bool(res.get("has_dollar_or_latex")),
                "metrics": res["metrics"],
            }
        )

    @app.get("/api/arena/questions")
    def api_arena_questions() -> JSONResponse:
        return JSONResponse(load_arena_questions(benchmark_path=benchmark_path))

    @app.post("/api/arena/run")
    def api_arena_run(req: ArenaRunRequest) -> JSONResponse:
        _assert_llm_ready_for_interactive_use()
        try:
            resolved_targets = [
                resolve_profile_target(
                    t.profile,
                    custom_url=t.custom_url,
                    custom_model=t.custom_model,
                    thinking=t.thinking,
                )
                for t in req.targets
            ]
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        out = run_arena_comparison(
            question=req.question,
            targets=resolved_targets,
            use_rag=req.use_rag,
            context_mode=req.context_mode,
            unload_ollama_between=req.unload_ollama_between,
            docs_root=docs_root,
            db_path=db_path,
            searcher=searcher,
            use_web=req.use_web,
            expected_token=req.expected_token,
            max_tokens=req.max_tokens,
        )
        return JSONResponse(out)

    return app


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Serveur Web local de monitoring qualite RAG D-Bot (FastAPI)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Adresse bind locale (defaut: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Port HTTP local (defaut: 8765)")
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--docs-root", type=Path, default=DEFAULT_DOCS_ROOT)
    parser.add_argument("--snapshots-root", type=Path, default=DEFAULT_SNAPSHOTS_ROOT)
    parser.add_argument("--ttl", type=float, default=20.0, help="Cache audit en secondes")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    app = create_app(
        db_path=args.db_path,
        docs_root=args.docs_root,
        snapshots_root=args.snapshots_root,
        cache_ttl_s=args.ttl,
    )
    print(f"D-Bot RAG Quality Monitor pret sur http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
