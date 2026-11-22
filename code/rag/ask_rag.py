#!/opt/homebrew/bin/python3.11
"""
CLI d'interrogation LightRAG D-Bot.

Mode par defaut (--provider auto) :
  - En --search-only : execute d'abord le graphe sans appel LLM via des mots-cles
    lexicaux deterministes (ou --keywords/--hl/--ll), avec repli automatique et
    garanti sur mode="naive" + reranking bge-reranker-base (exit 0).
  - En synthese complete : privilegie la cascade courte rapide Gemini (-lite) ->
    passerelle 1min.ai (mistral-small-2603) -> Ollama local gemma4:26b
    (repli qwen3.8:27b-mlx) -> Unsloth (:8888/v1) -> OpenRouter, avec trace
    explicite du modele utilise.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import warnings
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

from rag_runtime import (  # noqa: E402
    DEFAULT_DB_PATH,
    DEFAULT_EMBED_MODEL,
    DEFAULT_FASTEMBED_CACHE_DIR,
    DEFAULT_OLLAMA_INDEX_MODEL,
    DEFAULT_ONEMINAI_QA_MODEL,
    DEFAULT_OPENROUTER_MODEL,
    QWEN_QA_SAMPLING,
    GeminiCascadeSession,
    ManagedOllamaServer,
    ModelExecutionTracker,
    OneMinAiCascadeSession,
    apply_tiktoken_patch,
    build_gemini_cascade,
    build_local_openai_extra_body,
    build_openai_messages,
    build_rerank_model,
    call_1minai_stateless_async,
    call_openai_chat_adaptive_async,
    check_ollama_ready,
    check_unsloth_ready,
    create_genai_client,
    env_flag,
    extract_lexical_keywords,
    filter_and_clean_chunks,
    format_gemini_error,
    get_gemini_timeout_s,
    is_1minai_compatible_model_override,
    is_gemini_model_name,
    parse_keywords_arg,
    resolve_1minai_config,
    resolve_active_provider,
    resolve_default_db_path,
    resolve_ollama_config,
    resolve_ollama_model_for_role,
    resolve_unsloth_config,
    score_documents_with_reranker,
)

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
_DOC_ENV = Path("/Users/Shared/Mon Google Drive Physique/Documentation/.env")
if not os.environ.get("OPENROUTER_API_KEY") and _DOC_ENV.exists():
    load_dotenv(dotenv_path=_DOC_ENV)

apply_tiktoken_patch()
warnings.filterwarnings("ignore", category=UserWarning, module="fastembed")
warnings.filterwarnings("ignore", message=".*intfloat/multilingual-e5-large now uses mean pooling.*")

try:
    import aiohttp
    import numpy as np
    import openai
    from fastembed import TextEmbedding
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import openai_complete_if_cache
    from lightrag.utils import EmbeddingFunc
except ImportError as exc:
    print(f"Erreur d'importation dans ask_rag.py : {exc}", file=sys.stderr)
    sys.exit(1)

DB_PATH = resolve_default_db_path()
FASTEMBED_CACHE_DIR = os.environ.get("FASTEMBED_CACHE_PATH", DEFAULT_FASTEMBED_CACHE_DIR)

_embed_model = None
_rerank_model = None


def get_embed_model() -> TextEmbedding:
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding(DEFAULT_EMBED_MODEL, cache_dir=FASTEMBED_CACHE_DIR)
    return _embed_model


def get_rerank_model():
    global _rerank_model
    if _rerank_model is None:
        _rerank_model = build_rerank_model(FASTEMBED_CACHE_DIR)
    return _rerank_model


async def fastembed_func(texts: list[str]) -> np.ndarray:
    """Genere les embeddings BGE/E5 pour LightRAG."""
    model = get_embed_model()
    return np.array(list(model.embed(texts)), dtype=np.float32)


async def fastembed_rerank_func(query: str, documents: list[str], top_n: int | None = None, **kwargs) -> list[dict]:
    """Fonction de reranking compatible LightRAG via FastEmbed Cross-Encoder."""
    if not documents:
        return []
    model = get_rerank_model()
    scores = score_documents_with_reranker(model, query, documents)
    indexed = [{"index": i, "relevance_score": sc} for i, sc in enumerate(scores)]
    indexed.sort(key=lambda item: item["relevance_score"], reverse=True)
    return indexed[:top_n] if top_n else indexed


async def rerank_chunks(query: str, chunks: list[dict[str, Any]], top_k: int | None = None) -> list[dict[str, Any]]:
    """Applique le reranker sur les chunks recuperes si absent."""
    if not chunks:
        return []
    if all("rerank_score" in c for c in chunks):
        ordered = sorted(chunks, key=lambda item: float(item.get("rerank_score", 0.0)), reverse=True)
        return ordered[:top_k] if top_k else ordered

    model = get_rerank_model()
    if model is not None:
        texts = [str(c.get("content", "")) for c in chunks]
        scores = score_documents_with_reranker(model, query, texts)
        for chunk, sc in zip(chunks, scores):
            chunk["rerank_score"] = sc
        ordered = sorted(chunks, key=lambda item: float(item.get("rerank_score", 0.0)), reverse=True)
        return ordered[:top_k] if top_k else ordered

    return chunks[:top_k] if top_k else chunks


def _build_ollama_llm_func(
    model_name: str,
    base_url: str,
    num_ctx: int,
    keep_alive: str,
    tracker: ModelExecutionTracker | None = None,
):
    async def ollama_llm(
        prompt: str,
        system_prompt: str | None = None,
        history_messages: list | None = None,
        **kwargs,
    ) -> str:
        if kwargs.get("keyword_extraction"):
            prompt_lower = (prompt or "").lower()
            if "high_level_keywords" in prompt_lower and "low_level_keywords" in prompt_lower:
                hl, ll = extract_lexical_keywords(prompt)
                return json.dumps({"high_level_keywords": hl, "low_level_keywords": ll}, ensure_ascii=False)

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history_messages:
            for item in history_messages:
                if isinstance(item, dict) and "role" in item and "content" in item:
                    messages.append({"role": item["role"], "content": str(item["content"])})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "think": False,
            "keep_alive": keep_alive,
            "options": {
                "temperature": QWEN_QA_SAMPLING["temperature"],
                "top_p": QWEN_QA_SAMPLING["top_p"],
                "top_k": QWEN_QA_SAMPLING["top_k"],
                "min_p": QWEN_QA_SAMPLING["min_p"],
                "repeat_penalty": QWEN_QA_SAMPLING["repeat_penalty"],
                "num_ctx": num_ctx,
            },
        }
        timeout = aiohttp.ClientTimeout(total=180)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(f"{base_url}/api/chat", json=payload) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise RuntimeError(f"Erreur HTTP Ollama {resp.status} ({base_url}) : {body[:200]}")
                data = await resp.json()
                text = str(data.get("message", {}).get("content", "")).strip()
                if not text:
                    raise RuntimeError(f"Reponse Ollama vide ({model_name} sur {base_url})")
                if tracker is not None:
                    tracker.record_success("ollama", model_name)
                return text

    return ollama_llm


def _build_unsloth_llm_func(
    model_name: str,
    base_url: str,
    api_key: str,
    tracker: ModelExecutionTracker | None = None,
):
    async def unsloth_llm(
        prompt: str,
        system_prompt: str | None = None,
        history_messages: list | None = None,
        **kwargs,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history_messages:
            for item in history_messages:
                if isinstance(item, dict) and "role" in item and "content" in item:
                    messages.append({"role": item["role"], "content": str(item["content"])})
        messages.append({"role": "user", "content": prompt})

        client = openai.AsyncOpenAI(base_url=base_url, api_key=api_key, max_retries=0)
        resp = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=QWEN_QA_SAMPLING["temperature"],
            top_p=QWEN_QA_SAMPLING["top_p"],
            presence_penalty=QWEN_QA_SAMPLING["presence_penalty"],
            extra_body=build_local_openai_extra_body(
                top_k=QWEN_QA_SAMPLING["top_k"],
                min_p=QWEN_QA_SAMPLING["min_p"],
                repeat_penalty=QWEN_QA_SAMPLING["repeat_penalty"],
            ),
        )
        content = resp.choices[0].message.content or ""
        if not content.strip():
            finish = resp.choices[0].finish_reason
            raise RuntimeError(f"Reponse Unsloth vide ({base_url}, finish_reason={finish})")
        if tracker is not None:
            tracker.record_success("unsloth", model_name)
        return content

    return unsloth_llm


def _build_gemini_llm_func(
    model_name: str | None,
    api_key: str,
    tracker: ModelExecutionTracker | None = None,
    role: str = "qa",
):
    cascade = build_gemini_cascade(role=role, explicit_model=model_name)
    timeout_s = get_gemini_timeout_s(role=role)
    client = create_genai_client(api_key=api_key, timeout_s=timeout_s)
    session = GeminiCascadeSession(
        cascade,
        timeout_s=timeout_s,
        thinking_budget=100,
        rpm_delay=0.0,
        wait_on_transient=False,
        tracker=tracker,
    )

    async def gemini_llm(
        prompt: str,
        system_prompt: str | None = None,
        history_messages: list | None = None,
        **kwargs,
    ) -> str:
        text, _ = await session.call(
            client,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            max_tokens=int(kwargs.get("max_tokens", 4096)),
            temperature=float(kwargs.get("temperature", 0.2)),
            tracker=tracker,
        )
        if not text:
            raise RuntimeError(f"Cascade Gemini indisponible ({', '.join(cascade[:3])}...)")
        return text

    return gemini_llm


async def _noop_search_only_llm(prompt: str, system_prompt: str | None = None, history_messages=None, **kwargs) -> str:
    """Stub sans reseau utilise en --search-only lorsque le graphe est alimente par mots-cles."""
    raise RuntimeError("Aucun appel LLM ne doit etre effectue en mode --search-only sans --llm-keywords.")


def _resolve_qa_ollama_target(explicit_model: str | None) -> str:
    """Choisit le modele Ollama QA (gemma4:26b par defaut, surcharge CLI non-Gemini acceptee)."""
    if explicit_model and not is_gemini_model_name(explicit_model):
        return explicit_model.strip()
    _, default_qa_model, _, _ = resolve_ollama_config(role="qa")
    return default_qa_model


def _select_provider_with_lifecycle(
    args: argparse.Namespace,
    managed_ollama: ManagedOllamaServer,
    need_llm: bool,
) -> str | None:
    """
    Selectionne le fournisseur actif (Gemini en ligne par defaut en 'auto', puis
    repli local Ollama gemma4:26b -> Unsloth -> OpenRouter).
    Ne demarre aucun serveur lourd lors des recherches --search-only par defaut.
    """
    ollama_url, _, _, _ = resolve_ollama_config(role="qa")
    unsloth_url, _, unsloth_key = resolve_unsloth_config()
    ollama_model = _resolve_qa_ollama_target(args.model)
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    openrouter_key = args.api_key or os.environ.get("OPENROUTER_API_KEY", "").strip()

    if not need_llm:
        return None

    pref = args.provider
    if pref in ("local", "vmlx"):
        pref = "unsloth"

    auto_start_allowed = args.auto_start if args.auto_start is not None else True

    if pref == "ollama":
        if check_ollama_ready(ollama_url, required_model=ollama_model, timeout=0.5):
            return "ollama"
        if auto_start_allowed and managed_ollama.ensure_started():
            if check_ollama_ready(ollama_url, required_model=ollama_model, timeout=1.0):
                return "ollama"
            if not args.model and check_ollama_ready(ollama_url, required_model=DEFAULT_OLLAMA_INDEX_MODEL, timeout=1.0):
                managed_ollama.model = DEFAULT_OLLAMA_INDEX_MODEL
                return "ollama"
            print(
                f"⚠️ Ollama demarre sur {ollama_url}, mais le modele '{ollama_model}' n'est pas installe.",
                file=sys.stderr,
            )
            managed_ollama.cleanup()
        return None

    if pref == "auto":
        # En --provider auto, priorite aux API cloud rapides (Gemini -lite puis 1min.ai) ;
        # le demarrage paresseux d'Ollama ne survient qu'au repli local effectif.
        _, _, oneminai_key = resolve_1minai_config(role="qa")
        if gemini_key or oneminai_key:
            return "auto"
        resolved = resolve_active_provider(
            "auto",
            ollama_url=ollama_url,
            ollama_model=ollama_model,
            unsloth_url=unsloth_url,
            unsloth_api_key=unsloth_key,
            gemini_key=gemini_key,
            openrouter_key=openrouter_key,
            role="qa",
            prefer_online=True,
            oneminai_key=oneminai_key,
        )
        if resolved:
            return "auto"
        if auto_start_allowed and managed_ollama.ensure_started():
            if check_ollama_ready(ollama_url, required_model=ollama_model, timeout=1.0):
                return "auto"
            if check_ollama_ready(ollama_url, required_model=DEFAULT_OLLAMA_INDEX_MODEL, timeout=1.0):
                managed_ollama.model = DEFAULT_OLLAMA_INDEX_MODEL
                return "auto"
            managed_ollama.cleanup()
        return None

    return resolve_active_provider(
        pref,
        ollama_url=ollama_url,
        ollama_model=ollama_model,
        unsloth_url=unsloth_url,
        unsloth_api_key=unsloth_key,
        gemini_key=gemini_key,
        openrouter_key=openrouter_key,
        role="qa",
        prefer_online=True,
    )


def _build_auto_qa_llm_func(
    *,
    model_override: str | None,
    api_key_override: str | None,
    managed_ollama: ManagedOllamaServer,
    auto_start_allowed: bool,
    tracker: ModelExecutionTracker,
):
    """Cascade live QA : Gemini (-lite) -> 1min.ai (mistral-small-2603) -> Ollama (gemma4:26b) -> Unsloth -> OpenRouter."""
    ollama_url, _, ollama_num_ctx, ollama_keep_alive = resolve_ollama_config(role="qa")
    unsloth_url, unsloth_model, unsloth_key = resolve_unsloth_config()
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    openrouter_key = (api_key_override or os.environ.get("OPENROUTER_API_KEY", "")).strip()

    explicit_ollama = model_override if (model_override and not is_gemini_model_name(model_override)) else None
    ollama_candidates: list[str] = []
    for cand in (
        explicit_ollama,
        resolve_ollama_model_for_role("qa", base_url=ollama_url),
        DEFAULT_OLLAMA_INDEX_MODEL,
    ):
        if cand and cand not in ollama_candidates:
            ollama_candidates.append(cand)

    gemini_cascade = build_gemini_cascade("qa", explicit_model=model_override if is_gemini_model_name(model_override) else None)
    gemini_timeout_s = get_gemini_timeout_s("qa")
    genai_client = create_genai_client(gemini_key, timeout_s=gemini_timeout_s) if gemini_key else None
    gemini_session = GeminiCascadeSession(
        gemini_cascade,
        timeout_s=gemini_timeout_s,
        thinking_budget=100,
        rpm_delay=0.0,
        wait_on_transient=False,
        tracker=tracker,
    )
    oneminai_session = OneMinAiCascadeSession(
        role="qa",
        model_override=model_override,
        api_key_override=api_key_override if (api_key_override and not gemini_key) else None,
        timeout_s=30.0,
    )
    fallback_logged = False

    async def auto_qa_llm(
        prompt: str,
        system_prompt: str | None = None,
        history_messages: list | None = None,
        **kwargs,
    ) -> str:
        nonlocal fallback_logged
        if genai_client is not None and not gemini_session.cloud_exhausted:
            text, used_model = await gemini_session.call(
                genai_client,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                max_tokens=int(kwargs.get("max_tokens", 4096)),
                temperature=float(kwargs.get("temperature", 0.2)),
                tracker=tracker,
            )
            if text:
                return text

        if kwargs.get("keyword_extraction"):
            prompt_lower = (prompt or "").lower()
            if "high_level_keywords" in prompt_lower and "low_level_keywords" in prompt_lower:
                hl, ll = extract_lexical_keywords(prompt)
                return json.dumps({"high_level_keywords": hl, "low_level_keywords": ll}, ensure_ascii=False)

        if oneminai_session.is_available:
            om_text = await oneminai_session.call(
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                temperature=kwargs.get("temperature", 0.2),
                max_tokens=kwargs.get("max_tokens", 4096),
                tracker=tracker,
            )
            if om_text:
                return om_text

        if (genai_client is not None or oneminai_session.api_key) and not fallback_logged:
            fallback_logged = True
            print(
                f"🔄 Cascade Cloud (Gemini -lite / 1min.ai) indisponible -> repli local QA (Ollama {ollama_candidates[0]}).",
                file=sys.stderr,
            )

        ollama_ready = check_ollama_ready(ollama_url, required_model=None, timeout=0.5)
        if not ollama_ready and auto_start_allowed:
            ollama_ready = managed_ollama.ensure_started()
        if ollama_ready:
            for cand_model in ollama_candidates:
                if check_ollama_ready(ollama_url, required_model=cand_model, timeout=0.5):
                    try:
                        ollama_fn = _build_ollama_llm_func(
                            cand_model, ollama_url, ollama_num_ctx, ollama_keep_alive, tracker=tracker
                        )
                        return await ollama_fn(prompt, system_prompt=system_prompt, history_messages=history_messages, **kwargs)
                    except Exception as oe:
                        tracker.record_failure("ollama", cand_model, format_gemini_error(oe))

        if check_unsloth_ready(unsloth_url, unsloth_key, timeout=0.5):
            try:
                unsloth_fn = _build_unsloth_llm_func(unsloth_model, unsloth_url, unsloth_key, tracker=tracker)
                return await unsloth_fn(prompt, system_prompt=system_prompt, history_messages=history_messages, **kwargs)
            except Exception as ue:
                tracker.record_failure("unsloth", unsloth_model, format_gemini_error(ue))

        if openrouter_key:
            or_fn = get_llm_func("openrouter", model_override=None, api_key_override=openrouter_key, tracker=tracker)
            return await or_fn(prompt, system_prompt=system_prompt, history_messages=history_messages, **kwargs)

        raise RuntimeError(f"Aucun backend RAG joignable ({tracker.format_summary()})")

    return auto_qa_llm


def get_llm_func(
    provider_name: str,
    model_override: str | None = None,
    api_key_override: str | None = None,
    tracker: ModelExecutionTracker | None = None,
):
    """Construit la coroutine LLM adaptee au fournisseur selectionne."""
    ollama_url, ollama_model, ollama_num_ctx, ollama_keep_alive = resolve_ollama_config(role="qa")
    unsloth_url, unsloth_model, unsloth_key = resolve_unsloth_config()

    if provider_name == "ollama":
        eff_model = model_override or resolve_ollama_model_for_role("qa", base_url=ollama_url)
        return _build_ollama_llm_func(
            eff_model,
            ollama_url,
            ollama_num_ctx,
            ollama_keep_alive,
            tracker=tracker,
        )

    if provider_name == "unsloth":
        return _build_unsloth_llm_func(
            model_override or unsloth_model,
            unsloth_url,
            api_key_override or unsloth_key,
            tracker=tracker,
        )

    if provider_name == "gemini":
        gem_key = api_key_override or os.environ.get("GEMINI_API_KEY", "").strip()
        if not gem_key:
            raise ValueError("GEMINI_API_KEY manquante.")
        return _build_gemini_llm_func(model_override, gem_key, tracker=tracker, role="qa")

    if provider_name == "1minai":
        base_url, default_model, def_key = resolve_1minai_config(role="qa")
        om_key = (api_key_override or def_key).strip()
        if not om_key:
            raise ValueError("ONEMINAI_API_KEY manquante.")
        target_model = (
            model_override.strip()
            if (model_override and is_1minai_compatible_model_override(model_override))
            else default_model
        )

        async def oneminai_llm(prompt: str, system_prompt: str | None = None, history_messages=None, **kwargs):
            messages = build_openai_messages(prompt, system_prompt=system_prompt, history_messages=history_messages)
            eff_temp = 0.2 if kwargs.get("temperature") is None else float(kwargs["temperature"])
            eff_max_tokens = int(kwargs.get("max_tokens") or 4096)
            content, _, _ = await call_1minai_stateless_async(
                target_model,
                messages,
                base_url=base_url,
                api_key=om_key,
                temperature=eff_temp,
                max_tokens=eff_max_tokens,
                timeout_s=30.0,
            )
            if tracker is not None:
                tracker.record_success("1minai", target_model)
            return content

        return oneminai_llm

    if provider_name == "openrouter":
        or_key = api_key_override or os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not or_key:
            raise ValueError("OPENROUTER_API_KEY manquante.")
        target_model = model_override or DEFAULT_OPENROUTER_MODEL

        async def openrouter_llm(prompt: str, system_prompt: str | None = None, history_messages=None, **kwargs):
            text = await openai_complete_if_cache(
                target_model,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages or [],
                base_url="https://openrouter.ai/api/v1",
                api_key=or_key,
                **kwargs,
            )
            if tracker is not None:
                tracker.record_success("openrouter", target_model)
            return text

        return openrouter_llm

    raise ValueError(f"Fournisseur inconnu : {provider_name}")


def _resolve_search_keywords(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    """Construit (hl_keywords, ll_keywords) depuis les flags CLI ou l'extracteur lexical."""
    shared_kw = parse_keywords_arg(args.keywords)
    hl = parse_keywords_arg(args.hl) or list(shared_kw)
    ll = parse_keywords_arg(args.ll) or list(shared_kw)
    if hl or ll:
        if not hl:
            hl = list(ll)
        if not ll:
            ll = list(hl)
        return hl, ll
    return extract_lexical_keywords(args.query)


def _format_search_output(
    query: str,
    mode_label: str,
    chunks: list[dict[str, Any]],
    entities: list[dict[str, Any]] | None = None,
    relationships: list[dict[str, Any]] | None = None,
    hl_keywords: list[str] | None = None,
    ll_keywords: list[str] | None = None,
) -> str:
    """Formate proprement le contexte recupere sans troncature ni dependance externe."""
    lines = [f"=== Recherche LightRAG [--mode {mode_label}] : {query} ==="]
    if hl_keywords or ll_keywords:
        lines.append(f"Mots-cles HL : {', '.join(hl_keywords or [])}")
        lines.append(f"Mots-cles LL : {', '.join(ll_keywords or [])}")
    lines.append("")

    if entities:
        lines.append(f"--- Entites du graphe ({len(entities[:8])}/{len(entities)}) ---")
        for ent in entities[:8]:
            name = ent.get("entity_name", ent.get("id", "?"))
            desc = str(ent.get("description", "")).replace("\n", " ").strip()
            lines.append(f"- {name}: {desc[:240]}")
        lines.append("")

    if relationships:
        lines.append(f"--- Relations du graphe ({len(relationships[:8])}/{len(relationships)}) ---")
        for rel in relationships[:8]:
            src = rel.get("src_id", "?")
            tgt = rel.get("tgt_id", "?")
            desc = str(rel.get("description", "")).replace("\n", " ").strip()
            lines.append(f"- {src} -> {tgt}: {desc[:220]}")
        lines.append("")

    if not chunks:
        lines.append("Aucun extrait pertinent trouve dans la base.")
        return "\n".join(lines)

    lines.append(f"--- Extraits documentaires classes ({len(chunks)}) ---")
    for idx, chunk in enumerate(chunks, start=1):
        source = chunk.get("file_path") or "source_inconnue"
        score = chunk.get("rerank_score")
        score_tag = f" | Rerank: {float(score):.4f}" if score is not None else ""
        content = str(chunk.get("content", "")).strip()
        lines.append(f"\n[Doc {idx}] Source: {source}{score_tag}")
        lines.append(content)
    return "\n".join(lines)


async def _run_search_only(rag: LightRAG, args: argparse.Namespace) -> int:
    """
    Execute --search-only sans jamais planter sur erreur de connexion LLM :
    mode cible avec mots-cles lexicaux (ou LLM si --llm-keywords), puis repli vers naive.
    """
    skip_images = args.skip_images
    hl_kw: list[str] = []
    ll_kw: list[str] = []
    active_mode = args.mode

    if args.mode == "naive":
        result = await rag.aquery_data(
            args.query,
            param=QueryParam(
                mode="naive",
                only_need_context=True,
                top_k=args.top_k,
                chunk_top_k=args.top_k,
                enable_rerank=True,
            ),
        )
    else:
        if not args.llm_keywords:
            hl_kw, ll_kw = _resolve_search_keywords(args)
        try:
            param = QueryParam(
                mode=args.mode,
                only_need_context=True,
                top_k=args.top_k,
                chunk_top_k=args.top_k,
                hl_keywords=hl_kw,
                ll_keywords=ll_kw,
                enable_rerank=True,
            )
            result = await rag.aquery_data(args.query, param=param)
        except Exception as exc:
            print(
                f"⚠️ Recherche graphe '{args.mode}' indisponible ({exc}). Basculement vers mode='naive'.",
                file=sys.stderr,
            )
            active_mode = f"naive (repli depuis {args.mode})"
            result = await rag.aquery_data(
                args.query,
                param=QueryParam(
                    mode="naive",
                    only_need_context=True,
                    top_k=args.top_k,
                    chunk_top_k=args.top_k,
                    enable_rerank=True,
                ),
            )

    data = result.get("data", {}) if isinstance(result, dict) else {}
    raw_chunks = data.get("chunks", []) or []
    entities = data.get("entities", []) or []
    relationships = data.get("relationships", []) or []

    chunks = filter_and_clean_chunks(raw_chunks, skip_images=skip_images)
    if not chunks and raw_chunks and skip_images:
        chunks = filter_and_clean_chunks(raw_chunks, skip_images=False)

    if not chunks and args.mode != "naive" and not active_mode.startswith("naive"):
        print(
            f"⚠️ Mode '{args.mode}' sans extrait direct, repli complementaire vers mode='naive'.",
            file=sys.stderr,
        )
        naive_res = await rag.aquery_data(
            args.query,
            param=QueryParam(
                mode="naive",
                only_need_context=True,
                top_k=args.top_k,
                chunk_top_k=args.top_k,
                enable_rerank=True,
            ),
        )
        naive_data = naive_res.get("data", {}) if isinstance(naive_res, dict) else {}
        naive_raw = naive_data.get("chunks", []) or []
        chunks = filter_and_clean_chunks(naive_raw, skip_images=skip_images) or naive_raw
        active_mode = f"{args.mode} + repli naive"

    ranked = await rerank_chunks(args.query, chunks, top_k=args.top_k)
    print(
        _format_search_output(
            args.query,
            active_mode,
            ranked,
            entities=entities,
            relationships=relationships,
            hl_keywords=hl_kw,
            ll_keywords=ll_kw,
        )
    )
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interroger le RAG D-Bot (LightRAG)")
    parser.add_argument("query", nargs="?", default="", help="La question ou requete de recherche")
    parser.add_argument("--mode", choices=["naive", "local", "global", "hybrid", "mix"], default="hybrid")
    parser.add_argument(
        "--search-only",
        action="store_true",
        help="Recupere les extraits et le graphe sans synthese LLM",
    )
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument(
        "--provider",
        choices=["auto", "ollama", "unsloth", "local", "gemini", "1minai", "openrouter"],
        default="auto",
        help="Fournisseur LLM (defaut: auto = Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b -> Unsloth -> OpenRouter)",
    )
    parser.add_argument("--model", type=str, default=None, help="Surcharge du nom de modele LLM")
    parser.add_argument("--api-key", type=str, default=None, help="Cle API explicite si requise")
    parser.add_argument("--keywords", type=str, default=None, help="Mots-cles CSV injectes en HL et LL sans LLM")
    parser.add_argument("--hl", type=str, default=None, help="High-level keywords CSV explicites")
    parser.add_argument("--ll", type=str, default=None, help="Low-level keywords CSV explicites")
    parser.add_argument(
        "--llm-keywords",
        action="store_true",
        help="Force l'extraction de mots-cles par LLM meme avec --search-only",
    )
    parser.add_argument(
        "--skip-images",
        dest="skip_images",
        action="store_true",
        default=env_flag("RAG_SKIP_IMAGES", True),
        help="Exclut les images bitmap tout en conservant .svg et .pdf (actif par defaut)",
    )
    parser.add_argument(
        "--no-skip-images",
        dest="skip_images",
        action="store_false",
        help="Inclut aussi les descriptions d'images PNG/JPG dans les resultats",
    )
    parser.add_argument(
        "--auto-start",
        dest="auto_start",
        action="store_true",
        default=None,
        help="Autorise le demarrage automatique d'Ollama local si un LLM est requis",
    )
    parser.add_argument(
        "--no-auto-start",
        dest="auto_start",
        action="store_false",
        help="Interdit de lancer Ollama automatiquement",
    )
    parser.add_argument(
        "--keep-server",
        action="store_true",
        help="Garde Ollama actif apres la requete s'il a ete demarre automatiquement",
    )
    parser.add_argument(
        "--stop-server",
        action="store_true",
        help="Decharge le modele Ollama (et arrete le serveur s'il est gere) en fin de session",
    )
    return parser


async def run_cli(args: argparse.Namespace) -> int:
    if args.stop_server and not args.query.strip():
        managed = ManagedOllamaServer()
        ok = managed.unload_model()
        print("🛑 Modele Ollama decharge." if ok else "ℹ️ Aucun modele/serveur Ollama actif a decharger.")
        return 0

    if not args.query.strip():
        print("❌ Erreur : veuillez fournir une requete (ou --stop-server seul).", file=sys.stderr)
        return 2

    if not os.path.exists(DB_PATH):
        print(f"❌ Erreur : base RAG introuvable dans {DB_PATH}", file=sys.stderr)
        return 1

    ollama_url, _, _, _ = resolve_ollama_config(role="qa")
    ollama_model = _resolve_qa_ollama_target(args.model)
    managed_ollama = ManagedOllamaServer(base_url=ollama_url, model=ollama_model)

    need_llm = (not args.search_only) or (args.search_only and args.llm_keywords and args.mode != "naive")
    if args.search_only and not need_llm and args.auto_start is True:
        print(
            "ℹ️ --search-only utilise les mots-cles lexicaux sans charger le LLM (utilisez --llm-keywords pour forcer le LLM).",
            file=sys.stderr,
        )

    no_llm_label = (
        "Aucun LLM (recherche graphe/vecteur --search-only)"
        if args.search_only
        else "Cache LightRAG (réponse en cache — 0 appel LLM)"
    )
    tracker = ModelExecutionTracker(role="qa", default_no_llm_label=no_llm_label)
    exit_code = 0
    try:
        active_provider = _select_provider_with_lifecycle(args, managed_ollama, need_llm=need_llm)

        if need_llm and active_provider is None:
            if args.search_only:
                print(
                    "⚠️ Aucun serveur LLM joignable pour --llm-keywords ; bascule vers mots-cles lexicaux.",
                    file=sys.stderr,
                )
                args.llm_keywords = False
                llm_model_func = _noop_search_only_llm
            else:
                print(
                    "❌ Aucun backend LLM disponible (Gemini, Ollama, Unsloth ou OpenRouter).\n"
                    "Conseil : utilisez --search-only (0 Go RAM) ou verifiez 'ollama serve' / 'unsloth'.",
                    file=sys.stderr,
                )
                return 1
        elif active_provider == "auto":
            auto_start_allowed = args.auto_start if args.auto_start is not None else True
            llm_model_func = _build_auto_qa_llm_func(
                model_override=args.model,
                api_key_override=args.api_key,
                managed_ollama=managed_ollama,
                auto_start_allowed=auto_start_allowed,
                tracker=tracker,
            )
            print(
                f"🔗 Pipeline actif : auto (Gemini -lite -> 1min.ai {DEFAULT_ONEMINAI_QA_MODEL} -> Ollama gemma4:26b)",
                file=sys.stderr,
            )
        elif active_provider is not None:
            eff_model_override = args.model
            if active_provider == "ollama" and not eff_model_override:
                eff_model_override = getattr(managed_ollama, "model", None) or ollama_model
            llm_model_func = get_llm_func(
                active_provider,
                model_override=eff_model_override,
                api_key_override=args.api_key,
                tracker=tracker,
            )
            print(f"🔗 Backend actif : {active_provider}", file=sys.stderr)
        else:
            llm_model_func = _noop_search_only_llm

        rag = LightRAG(
            working_dir=DB_PATH,
            llm_model_func=llm_model_func,
            embedding_func=EmbeddingFunc(embedding_dim=1024, max_token_size=8192, func=fastembed_func),
            rerank_model_func=fastembed_rerank_func,
        )
        await rag.initialize_storages()

        if args.search_only:
            exit_code = await _run_search_only(rag, args)
            print(f"🧭 {tracker.format_summary()}", file=sys.stderr)
        else:
            print(f"🔍 Interrogation en cours ({args.mode}, provider={active_provider})...", file=sys.stderr)
            answer = await rag.aquery(
                args.query,
                param=QueryParam(
                    mode=args.mode,
                    top_k=args.top_k,
                    chunk_top_k=args.top_k,
                    enable_rerank=True,
                ),
            )
            trace_line = tracker.format_summary()
            print(f"🧭 {trace_line}", file=sys.stderr)
            print("\n=== Reponse RAG ===\n")
            print(f"[Moteur RAG : {trace_line}]\n")
            print(answer)
    except Exception as exc:
        print(f"❌ Erreur lors de la requete : {exc}", file=sys.stderr)
        exit_code = 1
    finally:
        if args.stop_server:
            managed_ollama.cleanup(force_unload_external=True)
        elif managed_ollama.started_by_us and not args.keep_server:
            managed_ollama.cleanup()

    return exit_code


async def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    code = await run_cli(args)
    if code != 0:
        sys.exit(code)


if __name__ == "__main__":
    asyncio.run(main())
