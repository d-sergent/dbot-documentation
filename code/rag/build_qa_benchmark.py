#!/usr/bin/env python3
"""Orchestrate Unsloth Studio Data Recipes to build the D-Bot QA benchmark.

Uploads Level-1 D-Bot markdown sources into Unsloth Studio's Data Recipe API,
validates and saves the reusable recipe definition, triggers a generation job
on the active local model (unsloth/Qwen3.8-27B-GGUF), applies strict D-Bot
content validators (French text, zero dollar/LaTeX markers, grounded evidence),
and merges deduplicated seed questions from AUDIT_QUESTION_REPONSE.json into
Annexes/Outils_de_Travail/RAG/BENCHMARK_QA_DBOT_120.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / ".env"
AUDIT_SEED_PATH = REPO_ROOT / "Annexes/Outils_de_Travail/RAG/AUDIT_QUESTION_REPONSE.json"
BENCHMARK_OUT_PATH = REPO_ROOT / "Annexes/Outils_de_Travail/RAG/BENCHMARK_QA_DBOT_120.json"

DEFAULT_SOURCES = [
    REPO_ROOT / "01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md",
    REPO_ROOT / "01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Calculs_FEA_Torse_et_Bassin.md",
    REPO_ROOT / "05_Gestion_Projet/FINAL_Liste_Achats_BOM.md",
]

DEFAULT_BASE_URL = "http://127.0.0.1:8888"
DEFAULT_RECIPE_ID = "dbot-qa-benchmark-v1"
DEFAULT_RECIPE_NAME = "D-Bot QA Benchmark (Torse, FEA & BOM)"
DEFAULT_BLOCK_ID = "dbot_level1_qa_seed"
DEFAULT_MODEL = "unsloth/Qwen3.8-27B-GGUF"
DEFAULT_VARIANT = "UD-Q4_K_XL"

DOLLAR_CHAR = chr(36)
LATEX_PATTERN = re.compile(
    r"\\(?:text|varnothing|pm|approx|circ|sqrt|mathbf|frac|times|cdot|alpha|beta|sigma|delta|mu)\b"
)
FRENCH_HINT_PATTERN = re.compile(
    r"\b(?:le|la|les|de|des|du|un|une|et|est|sont|pour|par|avec|dans|sur|quel|quelle|quels|quelles|combien)\b",
    re.IGNORECASE,
)


def load_dotenv_value(key: str) -> str:
    """Read an environment variable or fall back to the repository .env file."""
    env_val = os.environ.get(key, "").strip()
    if env_val:
        return env_val
    if not ENV_PATH.is_file():
        return ""
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        k, v = stripped.split("=", 1)
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    return ""


def api_request(
    base_url: str,
    path: str,
    api_key: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    raw_body: bytes | None = None,
    content_type: str | None = None,
    timeout: int = 30,
) -> Any:
    """Send an authenticated HTTP request to the local Unsloth Studio API."""
    url = base_url.rstrip("/") + path
    headers: dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    data: bytes | None = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif raw_body is not None:
        data = raw_body
        if content_type:
            headers["Content-Type"] = content_type

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} on {method} {path}: {err_body}") from exc


def build_multipart_form(
    fields: dict[str, str],
    file_field: str,
    filename: str,
    file_bytes: bytes,
) -> tuple[bytes, str]:
    """Encode a multipart/form-data request body without third-party dependencies."""
    boundary = f"----dbot-boundary-{uuid4().hex}"
    chunks: list[bytes] = []
    for key, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode("utf-8")
        )
    chunks.append(f"--{boundary}\r\n".encode("utf-8"))
    chunks.append(
        (
            f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'
            "Content-Type: text/markdown; charset=utf-8\r\n\r\n"
        ).encode("utf-8")
    )
    chunks.append(file_bytes)
    chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def upload_unstructured_sources(
    base_url: str,
    api_key: str,
    block_id: str,
    source_paths: list[Path],
    *,
    chunk_size: int = 1800,
    chunk_overlap: int = 200,
) -> tuple[list[str], list[str], dict[str, Any]]:
    """Upload markdown files as Unsloth Studio unstructured seed files and inspect them."""
    file_ids: list[str] = []
    file_names: list[str] = []
    for src in source_paths:
        if not src.is_file():
            raise FileNotFoundError(f"Missing seed source file: {src}")
        raw_bytes = src.read_bytes()
        body, ctype = build_multipart_form(
            {"block_id": block_id},
            "file",
            src.name,
            raw_bytes,
        )
        res = api_request(
            base_url,
            "/api/data-recipe/seed/upload-unstructured-file",
            api_key,
            method="POST",
            raw_body=body,
            content_type=ctype,
            timeout=60,
        )
        if res.get("status") != "ok":
            raise RuntimeError(f"Upload failed for {src.name}: {res}")
        file_ids.append(res["file_id"])
        file_names.append(res["filename"])

    inspect_res = api_request(
        base_url,
        "/api/data-recipe/seed/inspect-upload",
        api_key,
        method="POST",
        payload={
            "block_id": block_id,
            "file_ids": file_ids,
            "file_names": file_names,
            "preview_size": 5,
            "unstructured_chunk_size": chunk_size,
            "unstructured_chunk_overlap": chunk_overlap,
        },
        timeout=60,
    )
    resolved_paths = inspect_res.get("resolved_paths") or []
    if not resolved_paths:
        raise RuntimeError(f"inspect-upload did not return resolved_paths: {inspect_res}")
    return resolved_paths, file_names, inspect_res


def build_recipe_payload(
    resolved_paths: list[str],
    *,
    model_name: str,
    gguf_variant: str,
    chunk_size: int,
    chunk_overlap: int,
    rows: int,
) -> dict[str, Any]:
    """Build a valid Unsloth Studio RecipePayload for D-Bot technical QA generation."""
    system_prompt = (
        "Tu es un ingénieur senior en robotique humanoïde chargé de construire un jeu d'évaluation "
        "technique strictement factuel pour le robot D-Bot. "
        "Règles impératives : rédige uniquement en français technique ; "
        "n'utilise JAMAIS de syntaxe LaTeX ni aucun symbole dollar ; "
        "écris les unités et grandeurs en texte brut (mm, kg, MPa, N.m, Sf, deg) ; "
        "n'invente aucune valeur absente de l'extrait fourni."
    )
    user_prompt = (
        "Analyse l'extrait technique suivant issu de `{{ source_file }}` :\n\n"
        "{{ chunk_text }}\n\n"
        "Si cet extrait contient au moins une donnée d'ingénierie exploitable "
        "(dimension mécanique en mm, masse, contrainte Von Mises en MPa, coefficient de sécurité Sf, "
        "couple moteur ou de serrage en N.m, référence catalogue McMaster-Carr à 9 caractères, "
        "actionneur RobStride ou règle d'architecture/câblage), définis `answerable` à true et génère "
        "une question précise, sa réponse factuelle complète en français avec les valeurs exactes, "
        "la citation verbatim correspondante extraite mot pour mot de l'extrait (`evidence_quote`), "
        "et la valeur numérique ou référence clé (`numeric_token`). "
        "Si l'extrait ne contient qu'un sommaire, un titre ou des liens sans valeur technique concrète, "
        "définis `answerable` à false et laisse des chaînes courtes factuelles."
    )

    recipe = {
        "model_providers": [
            {
                "name": "unsloth-local",
                "endpoint": "",
                "is_local": True,
                "provider_type": "openai",
                "extra_headers": {},
                "extra_body": {},
            }
        ],
        "mcp_providers": [],
        "model_configs": [
            {
                "alias": "qwen38_local",
                "model": model_name,
                "gguf_variant": gguf_variant,
                "provider": "unsloth-local",
                "inference_parameters": {
                    "temperature": 0.25,
                    "top_p": 0.9,
                    "max_tokens": 900,
                    "max_parallel_requests": 1,
                },
            }
        ],
        "seed_config": {
            "source": {
                "seed_type": "unstructured",
                "paths": resolved_paths,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
            },
            "sampling_strategy": "shuffle",
            "selection_strategy": None,
        },
        "tool_configs": [],
        "columns": [
            {
                "column_type": "llm-structured",
                "name": "qa_struct",
                "drop": True,
                "model_alias": "qwen38_local",
                "system_prompt": system_prompt,
                "prompt": user_prompt,
                "with_trace": "none",
                "extract_reasoning_content": False,
                "output_format": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "answerable",
                        "category",
                        "question",
                        "answer",
                        "evidence_quote",
                        "numeric_token",
                    ],
                    "properties": {
                        "answerable": {"type": "boolean"},
                        "category": {
                            "type": "string",
                            "enum": [
                                "metrology_dimensions",
                                "fea_rdm",
                                "bom_hardware",
                                "architecture",
                            ],
                        },
                        "question": {"type": "string"},
                        "answer": {"type": "string"},
                        "evidence_quote": {"type": "string"},
                        "numeric_token": {"type": "string"},
                    },
                },
            },
            {
                "column_type": "expression",
                "name": "answerable",
                "drop": False,
                "expr": "{{ qa_struct.answerable }}",
                "dtype": "str",
            },
            {
                "column_type": "expression",
                "name": "category",
                "drop": False,
                "expr": "{{ qa_struct.category }}",
                "dtype": "str",
            },
            {
                "column_type": "expression",
                "name": "question",
                "drop": False,
                "expr": "{{ qa_struct.question }}",
                "dtype": "str",
            },
            {
                "column_type": "expression",
                "name": "answer",
                "drop": False,
                "expr": "{{ qa_struct.answer }}",
                "dtype": "str",
            },
            {
                "column_type": "expression",
                "name": "evidence_quote",
                "drop": False,
                "expr": "{{ qa_struct.evidence_quote }}",
                "dtype": "str",
            },
            {
                "column_type": "expression",
                "name": "numeric_token",
                "drop": False,
                "expr": "{{ qa_struct.numeric_token }}",
                "dtype": "str",
            },
            {
                "column_type": "expression",
                "name": "source_doc",
                "drop": False,
                "expr": "{{ source_file }}",
                "dtype": "str",
            },
        ],
        "processors": [
            {
                "processor_type": "drop_columns",
                "name": "drop_intermediate_cols",
                "column_names": ["chunk_text", "source_file", "qa_struct"],
            }
        ],
    }

    run = {
        "rows": rows,
        "execution_type": "full",
        "run_name": f"dbot-qa-{rows}",
        "output_formats": ["jsonl"],
    }

    ui = {
        "nodes": [
            {"id": "seed", "x": 160, "y": 420, "width": 380},
            {"id": "unsloth-local", "x": 620, "y": 120, "width": 380},
            {"id": "qwen38_local", "x": 620, "y": 300, "width": 380},
            {"id": "qa_struct", "x": 620, "y": 500, "width": 400},
            {"id": "question", "x": 1120, "y": 240, "width": 360},
            {"id": "answer", "x": 1120, "y": 400, "width": 360},
            {"id": "evidence_quote", "x": 1120, "y": 560, "width": 360},
        ],
        "edges": [
            {
                "from": "unsloth-local",
                "to": "qwen38_local",
                "type": "semantic",
                "source_handle": "semantic-out-bottom",
                "target_handle": "semantic-in-top",
            },
            {
                "from": "qwen38_local",
                "to": "qa_struct",
                "type": "semantic",
                "source_handle": "semantic-out-bottom",
                "target_handle": "data-in-top",
            },
            {
                "from": "seed",
                "to": "qa_struct",
                "type": "canvas",
                "source_handle": "data-out",
                "target_handle": "data-in",
            },
        ],
        "layout_direction": "LR",
        "seed_source_type": "unstructured",
        "unstructured_chunk_size": str(chunk_size),
        "unstructured_chunk_overlap": str(chunk_overlap),
    }

    return {"recipe": recipe, "run": run, "ui": ui}


def save_recipe_record(
    base_url: str,
    api_key: str,
    recipe_id: str,
    recipe_name: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Create or update a saved recipe in Unsloth Studio's library."""
    now_ms = int(time.time() * 1000)
    existing: dict[str, Any] | None = None
    try:
        existing = api_request(
            base_url,
            f"/api/data-recipe/recipes/{recipe_id}",
            api_key,
            method="GET",
        )
    except RuntimeError:
        existing = None

    body: dict[str, Any] = {
        "id": recipe_id,
        "name": recipe_name,
        "payload": payload,
        "createdAt": existing["createdAt"] if existing else now_ms,
        "updatedAt": max(now_ms, (existing["updatedAt"] + 1) if existing else now_ms),
    }
    if existing:
        body["baseUpdatedAt"] = existing["updatedAt"]

    return api_request(
        base_url,
        f"/api/data-recipe/recipes/{recipe_id}",
        api_key,
        method="PUT",
        payload=body,
        timeout=30,
    )


def wait_for_job_completion(
    base_url: str,
    api_key: str,
    job_id: str,
    *,
    poll_interval_s: float = 5.0,
    timeout_s: int = 1800,
) -> dict[str, Any]:
    """Poll Unsloth Studio's Data Recipe job status until terminal completion."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        status = api_request(
            base_url,
            f"/api/data-recipe/jobs/{job_id}/status",
            api_key,
            method="GET",
            timeout=30,
        )
        state = str(status.get("status") or "").lower()
        if state in {"completed", "succeeded", "done", "failed", "error", "cancelled"}:
            return status
        time.sleep(poll_interval_s)
    raise TimeoutError(f"Data Recipe job {job_id} timed out after {timeout_s}s")


def _normalize_space(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", " ", normalized).strip().lower()


def validate_generated_row(
    row: dict[str, Any],
    source_texts: dict[str, str],
) -> tuple[bool, str]:
    """Validate D-Bot QA row: answerable, French, zero-dollar, zero-LaTeX, source-grounded."""
    ans_flag = str(row.get("answerable") or "").strip().lower()
    if ans_flag not in {"true", "1", "yes"}:
        return False, "unanswerable_chunk"

    question = str(row.get("question") or "").strip()
    answer = str(row.get("answer") or "").strip()
    quote = str(row.get("evidence_quote") or "").strip()
    num_tok = str(row.get("numeric_token") or "").strip()
    source_doc = str(row.get("source_doc") or "").strip()

    if len(question) < 12 or len(answer) < 8:
        return False, "too_short"

    combined = f"{question}\n{answer}\n{quote}"
    if DOLLAR_CHAR in combined:
        return False, "contains_dollar_sign"
    if LATEX_PATTERN.search(combined):
        return False, "contains_latex"
    if not FRENCH_HINT_PATTERN.search(f"{question} {answer}"):
        return False, "not_french"

    if source_doc not in source_texts:
        return False, f"unknown_source:{source_doc}"

    src_norm = _normalize_space(source_texts[source_doc])
    quote_norm = _normalize_space(quote)
    num_norm = _normalize_space(num_tok)

    quote_ok = bool(quote_norm and len(quote_norm) >= 12 and quote_norm in src_norm)
    num_ok = bool(num_norm and num_norm in src_norm)
    if not (quote_ok or num_ok):
        return False, "ungrounded_quote_and_numeric"

    return True, "ok"


def load_deduplicated_audit_seeds(audit_path: Path) -> list[dict[str, Any]]:
    """Load AUDIT_QUESTION_REPONSE.json and collapse duplicate/empty artifact entries."""
    if not audit_path.is_file():
        return []
    raw_items = json.loads(audit_path.read_text(encoding="utf-8"))
    seen_questions: set[str] = set()
    cleaned: list[dict[str, Any]] = []
    for item in raw_items:
        q = str(item.get("question") or "").strip()
        if len(q) < 15 or not any(ch.isalpha() for ch in q):
            continue
        norm_q = _normalize_space(q)
        if norm_q in seen_questions:
            continue
        seen_questions.add(norm_q)
        cleaned.append(
            {
                "seed_id": item.get("id"),
                "section": str(item.get("section") or "").strip(),
                "question": q,
                "answer": str(item.get("answer") or "").strip(),
                "source_file": audit_path.name,
                "origin": "audit_question_reponse",
            }
        )
    return cleaned


def run_benchmark_pipeline(args: argparse.Namespace) -> int:
    """Execute end-to-end Unsloth Data Recipe validation, execution, and benchmark assembly."""
    api_key = load_dotenv_value("UNSLOTH_API_KEY")
    if not api_key:
        raise RuntimeError("Missing UNSLOTH_API_KEY in environment or .env")

    source_paths = [Path(p).resolve() for p in args.sources]
    source_texts = {p.name: p.read_text(encoding="utf-8") for p in source_paths}

    print(f"Uploading {len(source_paths)} Level-1 files to {args.base_url} ...")
    resolved_paths, file_names, inspect_res = upload_unstructured_sources(
        args.base_url,
        api_key,
        args.block_id,
        source_paths,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    print(
        f"Seed inspected: files={file_names}, total_chunks={inspect_res.get('total_rows')}, "
        f"columns={inspect_res.get('columns')}"
    )

    payload = build_recipe_payload(
        resolved_paths,
        model_name=args.model,
        gguf_variant=args.variant,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        rows=args.rows,
    )

    val_res = api_request(
        args.base_url,
        "/api/data-recipe/validate",
        api_key,
        method="POST",
        payload=payload,
        timeout=60,
    )
    print(f"Recipe validate result: valid={val_res.get('valid')}, errors={val_res.get('errors')}")
    if not val_res.get("valid"):
        raise RuntimeError(f"Data Recipe validation failed: {val_res}")

    saved = save_recipe_record(
        args.base_url,
        api_key,
        args.recipe_id,
        args.recipe_name,
        payload,
    )
    print(f"Saved recipe record in Unsloth Studio library: id={saved.get('id')}")

    if args.validate_only:
        return 0

    t0 = time.monotonic()
    job_resp = api_request(
        args.base_url,
        "/api/data-recipe/jobs",
        api_key,
        method="POST",
        payload=payload,
        timeout=60,
    )
    job_id = job_resp["job_id"]
    print(f"Started Data Recipe job_id={job_id} for rows={args.rows}")

    final_status = wait_for_job_completion(
        args.base_url,
        api_key,
        job_id,
        poll_interval_s=5.0,
        timeout_s=args.timeout,
    )
    elapsed_s = time.monotonic() - t0
    print(
        f"Job finished in {elapsed_s:.1f}s: status={final_status.get('status')}, "
        f"artifact_path={final_status.get('artifact_path')}"
    )
    if str(final_status.get("status") or "").lower() != "completed":
        raise RuntimeError(f"Data Recipe job did not complete cleanly: {final_status}")

    # Fetch generated rows via paginated dataset endpoint
    all_rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        page = api_request(
            args.base_url,
            f"/api/data-recipe/jobs/{job_id}/dataset?limit=200&offset={offset}",
            api_key,
            method="GET",
            timeout=60,
        )
        batch = page.get("dataset") or []
        all_rows.extend(batch)
        offset += len(batch)
        if not batch or offset >= int(page.get("total") or 0):
            break

    accepted_qa: list[dict[str, Any]] = []
    rejected_reasons: dict[str, int] = {}
    seen_q: set[str] = set()

    # Load existing items if --merge-existing is enabled
    if args.merge_existing and args.output.is_file():
        existing_doc = json.loads(args.output.read_text(encoding="utf-8"))
        for item in existing_doc.get("data_recipes_qa", []):
            norm_q = _normalize_space(str(item.get("question") or ""))
            if norm_q and norm_q not in seen_q:
                seen_q.add(norm_q)
                accepted_qa.append(item)

    for idx, row in enumerate(all_rows):
        ok, reason = validate_generated_row(row, source_texts)
        if not ok:
            rejected_reasons[reason] = rejected_reasons.get(reason, 0) + 1
            continue
        q_text = str(row["question"]).strip()
        norm_q = _normalize_space(q_text)
        if norm_q in seen_q:
            rejected_reasons["duplicate_question"] = rejected_reasons.get("duplicate_question", 0) + 1
            continue
        seen_q.add(norm_q)
        item_hash = hashlib.sha256(f"{row['source_doc']}:{q_text}".encode("utf-8")).hexdigest()[:12]
        accepted_qa.append(
            {
                "id": f"dr_{item_hash}",
                "category": str(row["category"]).strip(),
                "source_doc": str(row["source_doc"]).strip(),
                "question": q_text,
                "answer": str(row["answer"]).strip(),
                "evidence_quote": str(row["evidence_quote"]).strip(),
                "numeric_token": str(row["numeric_token"]).strip(),
                "job_id": job_id,
                "origin": "unsloth_data_recipes",
            }
        )

    audit_seeds = load_deduplicated_audit_seeds(AUDIT_SEED_PATH)
    target_total = 100
    benchmark_doc = {
        "benchmark_name": "D-Bot Engineering Technical QA Benchmark",
        "version": "1.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "recipe_id": args.recipe_id,
        "last_job_id": job_id,
        "model": args.model,
        "gguf_variant": args.variant,
        "status": "complete" if len(accepted_qa) >= target_total else "starter_bootstrapped",
        "target_data_recipes_items": target_total,
        "counts": {
            "raw_generated_rows": len(all_rows),
            "validated_data_recipes_qa": len(accepted_qa),
            "rejected_rows": sum(rejected_reasons.values()),
            "rejection_breakdown": rejected_reasons,
            "deduplicated_audit_seeds": len(audit_seeds),
        },
        "source_corpus": [str(p.relative_to(REPO_ROOT)) for p in source_paths],
        "audit_seeds": audit_seeds,
        "data_recipes_qa": accepted_qa,
    }

    rendered = json.dumps(benchmark_doc, ensure_ascii=False, indent=2) + "\n"
    if DOLLAR_CHAR in rendered or LATEX_PATTERN.search(rendered):
        raise ValueError("Sanity check failed: forbidden dollar sign or LaTeX detected in benchmark JSON")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(
        f"Benchmark written to {args.output}: "
        f"validated_qa={len(accepted_qa)}, rejected={rejected_reasons}, audit_seeds={len(audit_seeds)}"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run D-Bot QA Data Recipe in Unsloth Studio")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--recipe-id", default=DEFAULT_RECIPE_ID)
    parser.add_argument("--recipe-name", default=DEFAULT_RECIPE_NAME)
    parser.add_argument("--block-id", default=DEFAULT_BLOCK_ID)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--variant", default=DEFAULT_VARIANT)
    parser.add_argument("--chunk-size", type=int, default=1800)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    parser.add_argument("--rows", type=int, default=12)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--merge-existing", action="store_true")
    parser.add_argument("--output", type=Path, default=BENCHMARK_OUT_PATH)
    parser.add_argument("--sources", nargs="*", default=[str(p) for p in DEFAULT_SOURCES])
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run_benchmark_pipeline(parse_args()))
