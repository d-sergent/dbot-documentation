#!/opt/homebrew/bin/python3.11
"""
Primitives partagees pour la resilience, la configuration des backends LLM,
le reranking, le filtrage documentaire et le cycle de vie Ollama du RAG D-Bot.
"""

from __future__ import annotations

import asyncio
import ast
import atexit
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import numpy as np
import requests
import tiktoken

try:
    from fastembed.rerank.cross_encoder import TextCrossEncoder as _RerankerImpl
except ImportError:
    try:
        from fastembed import TextReranker as _RerankerImpl  # type: ignore[attr-defined]
    except ImportError:
        _RerankerImpl = None


DEFAULT_LOCAL_DB_PATH = "/Users/Shared/dbot_rag_local/lightrag_dbot_db"
DEFAULT_DRIVE_MIRROR_DB_PATH = "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"


def resolve_default_db_path() -> str:
    """Resout le chemin de base LightRAG actif (env > local SSD > miroir Drive)."""
    env_val = (os.environ.get("RAG_DB_PATH") or "").strip()
    if env_val:
        return env_val
    if Path(DEFAULT_LOCAL_DB_PATH).exists():
        return DEFAULT_LOCAL_DB_PATH
    if Path(DEFAULT_DRIVE_MIRROR_DB_PATH).exists():
        return DEFAULT_DRIVE_MIRROR_DB_PATH
    return DEFAULT_LOCAL_DB_PATH


DEFAULT_DB_PATH = resolve_default_db_path()
DEFAULT_FASTEMBED_CACHE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/models_cache"
DEFAULT_EMBED_MODEL = "intfloat/multilingual-e5-large"
DEFAULT_RERANK_MODEL = "BAAI/bge-reranker-base"

DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_INDEX_MODEL = "qwen3.8:27b-mlx"
DEFAULT_OLLAMA_QA_MODEL = "gemma4:26b"
DEFAULT_OLLAMA_MODEL = DEFAULT_OLLAMA_INDEX_MODEL
DEFAULT_UNSLOTH_BASE_URL = "http://127.0.0.1:8888/v1"
DEFAULT_UNSLOTH_MODEL = "unsloth/Qwen3.8-27B-GGUF"
DEFAULT_OPENROUTER_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
DEFAULT_ONEMINAI_BASE_URL = "https://api.1min.ai/openai/v1"
DEFAULT_ONEMINAI_MODEL = "mistral-small-latest"
DEFAULT_ONEMINAI_QA_MODEL = "mistral-small-2603"
DEFAULT_ONEMINAI_AUDIT_MODEL = "mistral-small-2603"
ONEMINAI_AUTO_FREE_MODEL = "qwen3.7-flash"
ONEMINAI_RECOMMENDED_MODELS = (
    "mistral-small-latest",
    "mistral-small-2603",
    "qwen3.7-flash",
    "gpt-6-luna",
    "deepseek-flash",
    "qwen-flash",
    "gpt-5.4-nano",
    "gpt-4o-mini",
)

_ONEMINAI_QUIRKS_LOCK = threading.Lock()
_ONEMINAI_BASE_OMIT_TEMP = frozenset(
    {"deepseek-flash", "gpt-5-nano", "gpt-5.4-nano", "gpt-6-luna", "o1", "o3", "o4-mini"}
)
_ONEMINAI_BASE_MAX_OUTPUT_CAPS: dict[str, int] = {"mistral-small-latest": 4096}
_ONEMINAI_OMIT_TEMP_MODELS: set[str] = set(_ONEMINAI_BASE_OMIT_TEMP)
_ONEMINAI_USE_MAX_COMPLETION_TOKENS_MODELS: set[str] = set()
_ONEMINAI_MAX_OUTPUT_CAPS: dict[str, int] = dict(_ONEMINAI_BASE_MAX_OUTPUT_CAPS)
_ONEMINAI_OMIT_OPTIONAL_PARAMS: dict[str, set[str]] = {}

# Cascade Gemini Free Tier courte et rapide (strictement -lite, sans modeles non-lite) pour QA & Audit.
GEMINI_QA_CASCADE = (
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
)
# Indexation graphe LightRAG : exclut les modeles '-lite' (sous-extraction mesuree de -77 % a -89 %
# de relations et 50-90 % de gleaning a vide sur manuels jumeaux vs qwen3.8:27b-mlx).
GEMINI_INDEX_CASCADE = (
    "gemini-3.8-flash",
    "gemini-4-hydrogen",
    "gemini-3.6-flash",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
    "gemini-2.5-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
)
GEMINI_VLM_CASCADE = (
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3-flash-preview",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
)
GEMINI_THINKING_BUDGETS = {"minimal": 0, "low": 100, "medium": 512, "high": 1024}
_NON_FREE_OR_DEAD_GEMINI = frozenset(
    {
        "gemini-1.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-pro",
        "gemini-3.1-pro-preview",
        "gemini-4-argon",
        "gemini-4-carbon",
        "gemini-4-neon",
    }
)

# Les SVG (schemas vectoriels) et PDF sont volontairement conserves comme contenu textuel utile.
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")

# Profil Qwen3.8 / Gemma 4 Non-Thinking pour extraction structuree et synthese QA RAG.
QWEN_EXTRACT_SAMPLING = {
    "temperature": 0.1,
    "top_p": 0.80,
    "top_k": 20,
    "min_p": 0.0,
    "repeat_penalty": 1.0,
    "presence_penalty": 0.3,
}
QWEN_QA_SAMPLING = {
    "temperature": 0.7,
    "top_p": 0.80,
    "top_k": 20,
    "min_p": 0.0,
    "presence_penalty": 0.0,
    "repeat_penalty": 1.0,
}

_STOPWORDS = frozenset(
    {
        "a", "ai", "ainsi", "alors", "an", "and", "apres", "are", "as", "at", "au",
        "aucun", "aucune", "aux", "avec", "avoir", "be", "bon", "by", "car", "ce",
        "cela", "ces", "cet", "cette", "ceux", "chaque", "comment", "comme", "contre",
        "d", "dans", "de", "depuis", "des", "do", "doit", "donc", "dont", "du",
        "elle", "elles", "en", "encore", "entre", "est", "et", "etaient", "etais",
        "etait", "ete", "etre", "faire", "fait", "faut", "for", "from", "how",
        "il", "ils", "in", "into", "is", "it", "je", "juste", "l", "la", "le",
        "les", "leur", "leurs", "lors", "lui", "ma", "mais", "me", "meme", "mes",
        "moi", "moins", "mon", "ne", "ni", "nom", "non", "nos", "not", "notre",
        "nous", "of", "on", "ont", "or", "ou", "par", "parce", "pas", "peu", "peut",
        "peux", "plus", "pour", "pourquoi", "precis", "precise", "propos", "qu",
        "quand", "que", "quel", "quelle", "quelles", "quels", "qui", "quoi", "sa",
        "sans", "se", "selon", "sera", "ses", "si", "son", "sont", "sous", "soit",
        "suis", "sur", "ta", "tandis", "te", "tes", "that", "the", "this", "to",
        "ton", "tous", "tout", "toute", "toutes", "tres", "tu", "un", "une", "vos",
        "votre", "vous", "what", "when", "where", "which", "who", "why", "with",
        "y",
    }
)

_TECH_TOKEN_RE = re.compile(
    r"(?:[A-Za-z]+[-_/]?\d+[A-Za-z0-9._/-]*|\d+(?:[.,]\d+)?\s?(?:mm|cm|m|nm|deg|v|a|w|go|ko|hz|khz|mhz|mpa|kg|g)|[A-Z]{2,}[A-Za-z0-9_-]*)",
    re.IGNORECASE,
)


def apply_tiktoken_patch() -> None:
    """Autorise les tokens speciaux bruts (<|endoftext|>, etc.) dans tiktoken."""
    if getattr(tiktoken.Encoding.encode, "_dbot_safe_patched", False):
        return
    original_encode = tiktoken.Encoding.encode

    def _safe_encode(self, text: str, *args: Any, **kwargs: Any):
        kwargs["disallowed_special"] = ()
        return original_encode(self, text, *args, **kwargs)

    setattr(_safe_encode, "_dbot_safe_patched", True)
    tiktoken.Encoding.encode = _safe_encode  # type: ignore[method-assign]


def env_flag(name: str, default: bool = False) -> bool:
    """Lit un booleen depuis une variable d'environnement."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def resolve_unsloth_config() -> tuple[str, str, str]:
    """
    Resout (base_url, model, api_key) pour Unsloth Studio / llama-server (:8888/v1)
    avec retrocompatibilite silencieuse des anciennes variables VMLX_*.
    """
    base_url = (
        os.environ.get("UNSLOTH_BASE_URL")
        or os.environ.get("VMLX_BASE_URL")
        or DEFAULT_UNSLOTH_BASE_URL
    ).strip().rstrip("/")
    model = (
        os.environ.get("UNSLOTH_MODEL")
        or os.environ.get("VMLX_MODEL")
        or DEFAULT_UNSLOTH_MODEL
    ).strip()
    api_key = (
        os.environ.get("UNSLOTH_API_KEY")
        or os.environ.get("VMLX_API_KEY")
        or "EMPTY"
    ).strip() or "EMPTY"
    return base_url, model, api_key


def resolve_1minai_config(role: str | None = None) -> tuple[str, str, str]:
    """
    Resout (base_url, model, api_key) pour la passerelle OpenAI-compatible 1min.ai.
    - role='qa'    -> ONEMINAI_QA_MODEL / DEFAULT_ONEMINAI_QA_MODEL (mistral-small-2603)
    - role='audit' -> ONEMINAI_AUDIT_MODEL / DEFAULT_ONEMINAI_AUDIT_MODEL (mistral-small-2603)
    - role='index' / None -> ONEMINAI_MODEL / DEFAULT_ONEMINAI_MODEL (mistral-small-latest)
    """
    base_url = (os.environ.get("ONEMINAI_BASE_URL") or DEFAULT_ONEMINAI_BASE_URL).strip().rstrip("/")
    if base_url == "https://api.1min.ai":
        base_url = DEFAULT_ONEMINAI_BASE_URL
    norm_role = normalize_rag_role(role) if role is not None else "index"
    if norm_role == "qa":
        model = (os.environ.get("ONEMINAI_QA_MODEL") or DEFAULT_ONEMINAI_QA_MODEL).strip()
    elif norm_role == "audit":
        model = (
            os.environ.get("ONEMINAI_AUDIT_MODEL")
            or os.environ.get("ONEMINAI_QA_MODEL")
            or DEFAULT_ONEMINAI_AUDIT_MODEL
        ).strip()
    else:
        model = (os.environ.get("ONEMINAI_MODEL") or DEFAULT_ONEMINAI_MODEL).strip()
    api_key = (os.environ.get("ONEMINAI_API_KEY") or "").strip()
    return base_url, model, api_key


def is_1minai_compatible_model_override(model_name: str | None) -> bool:
    """Indique si une surcharge --model cible bien un modele 1min.ai (hors tags Ollama/OpenRouter/Gemini)."""
    val = (model_name or "").strip()
    if not val or is_gemini_model_name(val) or ":" in val:
        return False
    low = val.lower()
    return not low.startswith(("unsloth/", "models/"))


def resolve_1minai_auto_index_target(
    *,
    allow_1minai: bool | None = None,
    disallow_1minai: bool = False,
) -> tuple[bool, str, str, str]:
    """
    Resout le palier intermediaire optionnel 1min.ai pour l'indexation en mode auto.
    Desactive par defaut pour preserver les credits et la qualite (activation explicite
    via --with-1minai ou RAG_AUTO_1MINAI=true). Force qwen3.7-flash sauf RAG_AUTO_ALLOW_PAID_1MINAI=true.
    Retourne (actif, base_url, model, api_key).
    """
    if disallow_1minai:
        return False, "", "", ""
    enabled = (allow_1minai is True) or (allow_1minai is None and env_flag("RAG_AUTO_1MINAI", False))
    if not enabled:
        return False, "", "", ""
    base_url, configured_model, api_key = resolve_1minai_config()
    if not api_key or "<VOTRE_CLE" in api_key:
        return False, base_url, "", ""
    if env_flag("RAG_AUTO_ALLOW_PAID_1MINAI", False):
        target_model = configured_model or ONEMINAI_AUTO_FREE_MODEL
    else:
        target_model = ONEMINAI_AUTO_FREE_MODEL
    return True, base_url, target_model, api_key


def is_1minai_permanent_or_quota_error(error_text: str) -> bool:
    """Indique si une erreur 1min.ai releve de l'authentification, du solde/quota ou d'un modele absent."""
    low = (error_text or "").lower()
    return any(
        tok in low
        for tok in (
            "401",
            "402",
            "403",
            "404",
            "unauthorized",
            "invalid_api_key",
            "api key",
            "insufficient",
            "quota",
            "credit",
            "balance",
            "payment",
            "billing",
            "model_not_found",
        )
    )


def fetch_1minai_models(
    base_url: str | None = None,
    api_key: str | None = None,
    timeout: float = 10.0,
) -> list[str]:
    """Liste les modeles actifs sur /openai/v1/models de 1min.ai sans consommer de credit."""
    def_url, _, def_key = resolve_1minai_config()
    eff_url = (base_url or def_url).strip().rstrip("/")
    eff_key = (api_key if api_key is not None else def_key).strip()
    if not eff_key:
        raise ValueError("ONEMINAI_API_KEY manquante.")
    resp = requests.get(
        f"{eff_url}/models",
        headers={"Authorization": f"Bearer {eff_key}"},
        timeout=timeout,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"1min.ai HTTP {resp.status_code}: {resp.text[:200]}")
    payload = resp.json()
    items = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        return []
    models: list[str] = []
    for entry in items:
        if isinstance(entry, dict) and entry.get("id"):
            models.append(str(entry["id"]))
        elif isinstance(entry, str) and entry.strip():
            models.append(entry.strip())
    return sorted(dict.fromkeys(models))


def _norm_1minai_model(model: str) -> str:
    return (model or "").strip().lower()


def is_1minai_temperature_omitted(model: str) -> bool:
    """Indique si ce modele 1min.ai requiert d'omettre le parametre temperature."""
    norm = _norm_1minai_model(model)
    with _ONEMINAI_QUIRKS_LOCK:
        return norm in _ONEMINAI_OMIT_TEMP_MODELS


def reset_1minai_model_quirks() -> None:
    """Reinitialise les contournements 1min.ai memorises aux valeurs de base (pour tests)."""
    with _ONEMINAI_QUIRKS_LOCK:
        _ONEMINAI_OMIT_TEMP_MODELS.clear()
        _ONEMINAI_OMIT_TEMP_MODELS.update(_ONEMINAI_BASE_OMIT_TEMP)
        _ONEMINAI_USE_MAX_COMPLETION_TOKENS_MODELS.clear()
        _ONEMINAI_MAX_OUTPUT_CAPS.clear()
        _ONEMINAI_MAX_OUTPUT_CAPS.update(_ONEMINAI_BASE_MAX_OUTPUT_CAPS)
        _ONEMINAI_OMIT_OPTIONAL_PARAMS.clear()


def build_1minai_chat_payload(
    model: str,
    messages: list[dict[str, Any]],
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
    stream: bool | None = False,
    extra_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Construit le payload Chat Completions 1min.ai selon les contraintes connues du modele."""
    norm = _norm_1minai_model(model)
    with _ONEMINAI_QUIRKS_LOCK:
        omit_temp = norm in _ONEMINAI_OMIT_TEMP_MODELS
        use_mct = norm in _ONEMINAI_USE_MAX_COMPLETION_TOKENS_MODELS
        output_cap = _ONEMINAI_MAX_OUTPUT_CAPS.get(norm)
        omitted_opts = set(_ONEMINAI_OMIT_OPTIONAL_PARAMS.get(norm, ()))

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    if temperature is not None and not omit_temp and "temperature" not in omitted_opts:
        payload["temperature"] = temperature
    if max_tokens is not None:
        eff_max_tokens = min(int(max_tokens), output_cap) if output_cap is not None else int(max_tokens)
        if use_mct and "max_completion_tokens" not in omitted_opts:
            payload["max_completion_tokens"] = eff_max_tokens
        elif not use_mct and "max_tokens" not in omitted_opts:
            payload["max_tokens"] = eff_max_tokens
    if stream is not None and "stream" not in omitted_opts:
        payload["stream"] = stream
    if extra_params:
        for key, val in extra_params.items():
            if val is not None and key not in omitted_opts:
                payload[key] = val
    return payload


def _extract_error_param_and_msg(error_text: str) -> tuple[str | None, str]:
    raw = str(error_text or "").strip()
    start = raw.find("{")
    param: str | None = None
    msg = raw
    if start != -1:
        snippet = raw[start:]
        parsed: Any = None
        try:
            parsed = json.loads(snippet)
        except Exception:
            try:
                parsed = ast.literal_eval(snippet)
            except Exception:
                parsed = None
        if isinstance(parsed, dict):
            err_obj = parsed.get("error") if isinstance(parsed.get("error"), dict) else parsed
            if err_obj.get("param"):
                param = str(err_obj["param"]).strip()
            if err_obj.get("message"):
                msg = str(err_obj["message"]).strip()
    if param is None:
        match = re.search(r"""["']param["']\s*:\s*["']([^"']+)["']""", raw)
        if match:
            param = match.group(1).strip()
    return param, msg


def adapt_1minai_payload_from_error(
    model: str,
    payload: dict[str, Any],
    error_text: str,
) -> tuple[dict[str, Any], str] | None:
    """
    Adapte automatiquement le payload 1min.ai apres un HTTP 400 de parametre refuse
    (ex: 'Omit temperature for this model.', ou conversion 'max_tokens' -> 'max_completion_tokens').
    """
    raw_low = (error_text or "").lower()
    if not any(
        tok in raw_low
        for tok in (
            "400",
            "invalid_request_error",
            "unsupported_parameter",
            "unsupported_value",
            "unsupported",
            "omit ",
            "extra_forbidden",
            "unknown parameter",
        )
    ):
        return None

    param, msg = _extract_error_param_and_msg(error_text)
    msg_low = msg.lower()
    param_low = (param or "").lower()
    norm = _norm_1minai_model(model)
    new_payload = dict(payload)

    def _record_omitted(field_name: str) -> None:
        with _ONEMINAI_QUIRKS_LOCK:
            if field_name == "temperature":
                _ONEMINAI_OMIT_TEMP_MODELS.add(norm)
            else:
                _ONEMINAI_OMIT_OPTIONAL_PARAMS.setdefault(norm, set()).add(field_name)

    if "temperature" in new_payload and (param_low == "temperature" or "temperature" in msg_low):
        new_payload.pop("temperature", None)
        _record_omitted("temperature")
        return new_payload, "retrait temperature"

    tok_field = (
        "max_completion_tokens"
        if "max_completion_tokens" in new_payload
        else ("max_tokens" if "max_tokens" in new_payload else None)
    )
    if tok_field is not None and (
        param_low in ("max_tokens", "max_completion_tokens")
        or any(k in msg_low for k in ("max_tokens", "max_completion_tokens", "output limit"))
    ):
        cap_match = re.search(
            r"(?:maximum(?:\s+of)?|at\s+most|<=|limit(?:\s+is|\s+of)?)\s*(\d{3,6})\b",
            msg_low,
        )
        cur_val = new_payload.get(tok_field)
        if cap_match and isinstance(cur_val, int):
            cap_val = int(cap_match.group(1))
            if 256 <= cap_val < cur_val:
                new_payload[tok_field] = cap_val
                with _ONEMINAI_QUIRKS_LOCK:
                    _ONEMINAI_MAX_OUTPUT_CAPS[norm] = cap_val
                return new_payload, f"{tok_field}<={cap_val}"

        if tok_field == "max_tokens":
            max_tok_val = new_payload.pop("max_tokens")
            if "max_completion_tokens" in msg_low:
                new_payload["max_completion_tokens"] = max_tok_val
                with _ONEMINAI_QUIRKS_LOCK:
                    _ONEMINAI_USE_MAX_COMPLETION_TOKENS_MODELS.add(norm)
                return new_payload, "max_tokens->max_completion_tokens"
            _record_omitted("max_tokens")
            return new_payload, "retrait max_tokens"

        new_payload.pop("max_completion_tokens", None)
        _record_omitted("max_completion_tokens")
        return new_payload, "retrait max_completion_tokens"

    for candidate in (
        "max_completion_tokens",
        "top_p",
        "presence_penalty",
        "frequency_penalty",
        "response_format",
        "stream",
    ):
        if candidate in new_payload and (param_low == candidate or candidate in msg_low):
            new_payload.pop(candidate, None)
            _record_omitted(candidate)
            return new_payload, f"retrait {candidate}"

    return None


async def call_openai_chat_adaptive_async(
    client: Any,
    model: str,
    messages: list[dict[str, Any]],
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
    extra_params: dict[str, Any] | None = None,
    max_adaptations: int = 3,
) -> Any:
    """Appelle client.chat.completions.create avec adaptation automatique des parametres refuses (HTTP 400)."""
    req_kwargs = build_1minai_chat_payload(
        model,
        messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=None,
        extra_params=extra_params,
    )
    req_kwargs.pop("model", None)
    req_kwargs.pop("messages", None)

    for _ in range(max_adaptations + 1):
        try:
            return await client.chat.completions.create(
                model=model,
                messages=messages,
                **req_kwargs,
            )
        except Exception as exc:
            err_body = getattr(exc, "body", None)
            err_detail = json.dumps(err_body) if isinstance(err_body, dict) else str(exc)
            adapted = adapt_1minai_payload_from_error(model, req_kwargs, err_detail or str(exc))
            if adapted is None:
                raise
            req_kwargs, _ = adapted
    return await client.chat.completions.create(model=model, messages=messages, **req_kwargs)


async def _default_post_json_aiohttp(
    url: str,
    payload: dict[str, Any],
    *,
    timeout_s: float,
    headers: dict[str, str] | None = None,
    service_name: str = "1min.ai",
    include_error_body: bool = True,
) -> dict[str, Any]:
    import aiohttp

    timeout = aiohttp.ClientTimeout(total=timeout_s)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    err_txt = await resp.text() if include_error_body else ""
                    detail = f": {err_txt[:500]}" if err_txt else ""
                    raise RuntimeError(f"{service_name} HTTP {resp.status}{detail}")
                return await resp.json()
    except (aiohttp.ClientError, OSError, asyncio.TimeoutError) as err:
        raise RuntimeError(f"{service_name} injoignable sur {url} ({type(err).__name__}: {err})") from err


async def call_1minai_stateless_async(
    model: str,
    messages: list[dict[str, Any]],
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    temperature: float | None = 0.1,
    max_tokens: int | None = 8192,
    timeout_s: float = 120.0,
    post_json_fn: Any = None,
    on_param_adapted: Any = None,
    max_transient_retries: int = 2,
) -> tuple[str, int, int]:
    """
    Execute un appel Chat Completions stateless 1min.ai avec adaptation automatique HTTP 400
    et retries transitoires (429/5xx/timeout). Retourne (texte, prompt_tokens, completion_tokens).
    """
    def_url, def_model, def_key = resolve_1minai_config()
    eff_url = (base_url or def_url).strip().rstrip("/")
    eff_model = (model or def_model).strip()
    eff_key = (api_key if api_key is not None else def_key).strip()
    if not eff_key:
        raise ValueError("ONEMINAI_API_KEY manquante.")

    payload = build_1minai_chat_payload(
        eff_model,
        messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
    )
    headers = {
        "Authorization": f"Bearer {eff_key}",
        "Content-Type": "application/json",
    }
    url = f"{eff_url}/chat/completions"
    sender = post_json_fn or _default_post_json_aiohttp

    transient_retries = 0
    param_adaptations = 0
    last_err: Exception | None = None
    while True:
        try:
            data = await sender(
                url,
                payload,
                timeout_s=timeout_s,
                headers=headers,
                service_name="1min.ai",
                include_error_body=True,
            )
            choices = data.get("choices") or []
            content = ((choices[0].get("message") or {}).get("content") or "") if choices else ""
            if not str(content).strip():
                raise RuntimeError(f"Reponse 1min.ai vide ({eff_model})")
            usage = data.get("usage") or {}
            return (
                str(content),
                int(usage.get("prompt_tokens") or 0),
                int(usage.get("completion_tokens") or 0),
            )
        except Exception as err:
            last_err = err
            if param_adaptations < 3:
                adapted = adapt_1minai_payload_from_error(eff_model, payload, str(err))
                if adapted is not None:
                    payload, change_desc = adapted
                    param_adaptations += 1
                    if on_param_adapted is not None:
                        on_param_adapted(change_desc)
                    continue
            err_low = str(err).lower()
            if (
                not is_1minai_permanent_or_quota_error(err_low)
                and transient_retries < max_transient_retries
                and any(tok in err_low for tok in ("429", "500", "502", "503", "504", "timeout", "injoignable"))
            ):
                transient_retries += 1
                await asyncio.sleep(2.0 * transient_retries)
                continue
            break
    raise RuntimeError(f"Echec 1min.ai ({eff_model}) : {last_err}") from last_err


def build_openai_messages(
    prompt: str,
    system_prompt: str | None = None,
    history_messages: list[Any] | None = None,
) -> list[dict[str, str]]:
    """Construit la liste normalisee de messages OpenAI Chat Completions."""
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": str(system_prompt)})
    for item in history_messages or []:
        if isinstance(item, dict) and "role" in item and "content" in item:
            messages.append({"role": str(item["role"]), "content": str(item["content"])})
    messages.append({"role": "user", "content": str(prompt)})
    return messages


class OneMinAiCascadeSession:
    """Session 1min.ai stateless avec coupe-circuit sur quota/erreur permanente pour QA & Audit."""

    def __init__(
        self,
        *,
        role: str = "qa",
        model_override: str | None = None,
        api_key_override: str | None = None,
        timeout_s: float | None = None,
        cooldown_s: float = 120.0,
    ) -> None:
        self.role = normalize_rag_role(role)
        base_url, def_model, def_key = resolve_1minai_config(role=self.role)
        self.base_url = base_url
        self.model = (
            model_override.strip()
            if (model_override and is_1minai_compatible_model_override(model_override))
            else def_model
        )
        self.api_key = (api_key_override if api_key_override is not None else def_key).strip()
        self.timeout_s = float(timeout_s if timeout_s is not None else (60.0 if self.role == "audit" else 30.0))
        self.cooldown_s = max(0.0, float(cooldown_s))
        self.consecutive_failures = 0
        self._exhausted_until = 0.0

    @property
    def is_available(self) -> bool:
        if not self.api_key or "<VOTRE_CLE" in self.api_key:
            return False
        if self._exhausted_until > 0.0 and time.monotonic() < self._exhausted_until:
            return False
        return True

    def reset_circuit_breaker(self) -> None:
        self.consecutive_failures = 0
        self._exhausted_until = 0.0

    async def call(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        history_messages: list[Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = 4096,
        tracker: ModelExecutionTracker | None = None,
    ) -> str | None:
        if not self.is_available:
            return None
        messages = build_openai_messages(prompt, system_prompt=system_prompt, history_messages=history_messages)
        eff_temp = (0.1 if self.role == "audit" else 0.2) if temperature is None else float(temperature)
        eff_max_tokens = int(max_tokens or 4096)
        try:
            content, _, _ = await call_1minai_stateless_async(
                self.model,
                messages,
                base_url=self.base_url,
                api_key=self.api_key,
                temperature=eff_temp,
                max_tokens=eff_max_tokens,
                timeout_s=self.timeout_s,
                max_transient_retries=1,
            )
            self.consecutive_failures = 0
            self._exhausted_until = 0.0
            if tracker is not None:
                tracker.record_success("1minai", self.model)
            return content
        except Exception as exc:
            err_msg = format_gemini_error(exc)
            if tracker is not None:
                tracker.record_failure("1minai", self.model, err_msg)
            self.consecutive_failures += 1
            if is_1minai_permanent_or_quota_error(str(exc)) or self.consecutive_failures >= 2:
                self._exhausted_until = time.monotonic() + (self.cooldown_s or 3600.0)
            return None


def normalize_rag_role(role: str | None) -> str:
    """Normalise un role RAG en 'index', 'qa' ou 'audit'."""
    norm = (role or "index").strip().lower()
    if norm in ("qa", "search", "query", "chat"):
        return "qa"
    if norm in ("audit", "impact", "reasoning", "integrity"):
        return "audit"
    return "index"


def resolve_ollama_config(role: str = "index") -> tuple[str, str, int, str]:
    """
    Resout (base_url, model, num_ctx, keep_alive) pour Ollama local selon la tache.
    - role='qa' / 'audit' -> gemma4:26b (OLLAMA_QA_MODEL / OLLAMA_AUDIT_MODEL, rapide en QA et Audit)
    - role='index'        -> qwen3.8:27b-mlx (OLLAMA_MODEL, fidele en extraction graphe)
    """
    base_url = (os.environ.get("OLLAMA_BASE_URL") or DEFAULT_OLLAMA_BASE_URL).strip().rstrip("/")
    if base_url.endswith("/v1"):
        base_url = base_url[:-3]
    norm_role = normalize_rag_role(role)
    if norm_role == "qa":
        model = (os.environ.get("OLLAMA_QA_MODEL") or DEFAULT_OLLAMA_QA_MODEL).strip()
    elif norm_role == "audit":
        model = (
            os.environ.get("OLLAMA_AUDIT_MODEL")
            or os.environ.get("OLLAMA_QA_MODEL")
            or DEFAULT_OLLAMA_QA_MODEL
        ).strip()
    else:
        model = (os.environ.get("OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL).strip()
    num_ctx = int(os.environ.get("OLLAMA_NUM_CTX", "16384"))
    keep_alive = os.environ.get("OLLAMA_KEEP_ALIVE", "10m").strip() or "10m"
    return base_url, model, num_ctx, keep_alive


def resolve_ollama_model_for_role(
    role: str = "index",
    explicit_model: str | None = None,
    base_url: str | None = None,
) -> str:
    """
    Retourne le meilleur modele Ollama pour le role demande, avec repli de gemma4:26b
    vers qwen3.8:27b-mlx si Ollama est deja actif en qa/audit sans gemma4:26b installe.
    """
    if explicit_model and explicit_model.strip():
        return explicit_model.strip()
    resolved_url, preferred_model, _, _ = resolve_ollama_config(role=role)
    if normalize_rag_role(role) in ("qa", "audit"):
        fallback_model = (os.environ.get("OLLAMA_MODEL") or DEFAULT_OLLAMA_INDEX_MODEL).strip()
        target_url = base_url or resolved_url
        if (
            fallback_model
            and fallback_model != preferred_model
            and check_ollama_ready(target_url, required_model=None, timeout=0.35)
            and not check_ollama_ready(target_url, required_model=preferred_model, timeout=0.35)
            and check_ollama_ready(target_url, required_model=fallback_model, timeout=0.35)
        ):
            return fallback_model
    return preferred_model


def build_local_openai_extra_body(
    top_k: int = 20,
    min_p: float = 0.0,
    repeat_penalty: float = 1.0,
) -> dict[str, Any]:
    """Construit extra_body Qwen3.8 Non-Thinking pour serveurs OpenAI-compatibles locaux."""
    return {
        "top_k": top_k,
        "min_p": min_p,
        "repeat_penalty": repeat_penalty,
        "chat_template_kwargs": {"enable_thinking": False},
    }


def _ollama_model_matches(installed_name: str, target_model: str) -> bool:
    norm = installed_name.strip().lower()
    target = target_model.strip().lower()
    if not norm or not target:
        return False
    if norm == target:
        return True
    if ":" not in target and norm == f"{target}:latest":
        return True
    return False


def check_ollama_ready(
    base_url: str | None = None,
    required_model: str | None = None,
    timeout: float = 0.5,
) -> bool:
    """Preflight HTTP rapide sur /api/tags d'Ollama (avec verification optionnelle du modele)."""
    resolved_url, _, _, _ = resolve_ollama_config()
    url = (base_url or resolved_url).strip().rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    try:
        resp = requests.get(f"{url}/api/tags", timeout=timeout)
        if resp.status_code != 200:
            return False
        if not required_model:
            return True
        payload = resp.json()
        models = payload.get("models")
        if not isinstance(models, list):
            return False
        for item in models:
            if not isinstance(item, dict):
                continue
            candidate = str(item.get("name") or item.get("model") or "")
            if _ollama_model_matches(candidate, required_model):
                return True
        return False
    except (requests.RequestException, ValueError):
        return False


def check_unsloth_ready(
    base_url: str | None = None,
    api_key: str | None = None,
    timeout: float = 0.5,
) -> bool:
    """Preflight HTTP rapide sur /models d'Unsloth Studio / llama-server."""
    resolved_url, _, resolved_key = resolve_unsloth_config()
    url = (base_url or resolved_url).strip().rstrip("/")
    key = api_key if api_key is not None else resolved_key
    headers = {"Authorization": f"Bearer {key}"} if key and key != "EMPTY" else {}
    try:
        resp = requests.get(f"{url}/models", headers=headers, timeout=timeout)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def resolve_active_provider(
    preferred: str = "auto",
    ollama_url: str | None = None,
    ollama_model: str | None = None,
    unsloth_url: str | None = None,
    unsloth_api_key: str | None = None,
    gemini_key: str | None = None,
    openrouter_key: str | None = None,
    timeout: float = 0.5,
    role: str = "qa",
    prefer_online: bool = True,
    oneminai_key: str | None = None,
) -> str | None:
    """
    Determine le fournisseur LLM actif.
    En mode auto + prefer_online=True :
    - 'qa' / 'audit' : Gemini (-lite) -> 1min.ai -> Ollama gemma4:26b -> Unsloth -> OpenRouter
    - 'index'        : Gemini (non-lite) -> Ollama qwen3.8:27b-mlx -> Unsloth -> OpenRouter (jamais 1min.ai)
    """
    norm = (preferred or "auto").strip().lower()
    if norm in ("local", "vmlx"):
        norm = "unsloth"

    norm_role = normalize_rag_role(role)
    eff_ollama_url, eff_ollama_model, _, _ = resolve_ollama_config(role=norm_role)
    eff_ollama_url = ollama_url or eff_ollama_url
    eff_ollama_model = ollama_model or eff_ollama_model

    eff_unsloth_url, _, eff_unsloth_key = resolve_unsloth_config()
    eff_unsloth_url = unsloth_url or eff_unsloth_url
    eff_unsloth_key = unsloth_api_key if unsloth_api_key is not None else eff_unsloth_key

    eff_gemini = (gemini_key if gemini_key is not None else os.environ.get("GEMINI_API_KEY", "")).strip()
    eff_openrouter = (
        openrouter_key if openrouter_key is not None else os.environ.get("OPENROUTER_API_KEY", "")
    ).strip()
    _, _, def_1minai = resolve_1minai_config(role=norm_role)
    eff_1minai = (oneminai_key if oneminai_key is not None else def_1minai).strip()

    if norm != "auto":
        if norm == "ollama":
            return "ollama" if check_ollama_ready(eff_ollama_url, eff_ollama_model, timeout=timeout) else None
        if norm == "unsloth":
            return "unsloth" if check_unsloth_ready(eff_unsloth_url, eff_unsloth_key, timeout=timeout) else None
        if norm == "gemini":
            return "gemini" if eff_gemini else None
        if norm == "openrouter":
            return "openrouter" if eff_openrouter else None
        if norm == "1minai":
            return "1minai" if eff_1minai else None
        return None

    if prefer_online:
        if eff_gemini:
            return "gemini"
        if norm_role in ("qa", "audit") and eff_1minai:
            return "1minai"

    if check_ollama_ready(eff_ollama_url, eff_ollama_model, timeout=timeout):
        return "ollama"
    if check_unsloth_ready(eff_unsloth_url, eff_unsloth_key, timeout=timeout):
        return "unsloth"
    if eff_gemini:
        return "gemini"
    if norm_role in ("qa", "audit") and eff_1minai:
        return "1minai"
    if eff_openrouter:
        return "openrouter"
    return None


def _is_loopback_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").strip().lower()
    return host in ("", "127.0.0.1", "localhost", "::1")


def _find_ollama_binary() -> str | None:
    candidate = shutil.which("ollama")
    if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
        return candidate
    fallback = "/usr/local/bin/ollama"
    if os.path.isfile(fallback) and os.access(fallback, os.X_OK):
        return fallback
    return None


class ManagedOllamaServer:
    """
    Gere le demarrage a la demande d'ollama serve et le nettoyage en fin de session.
    Ne tue jamais un demon Ollama deja lance avant notre execution.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        resolved_url, resolved_model, _, _ = resolve_ollama_config()
        self.base_url = (base_url or resolved_url).strip().rstrip("/")
        if self.base_url.endswith("/v1"):
            self.base_url = self.base_url[:-3]
        self.model = (model or resolved_model).strip()
        self._proc: subprocess.Popen[bytes] | None = None
        self.started_by_us: bool = False
        self._atexit_registered: bool = False
        self._cleaned_up: bool = False

    def ensure_started(self, timeout_s: float = 15.0) -> bool:
        """Demarre ollama serve en mono-slot M1 Max uniquement si absent."""
        if self._proc is not None and self._proc.poll() is None and check_ollama_ready(self.base_url, timeout=0.5):
            return True

        if check_ollama_ready(self.base_url, timeout=0.5):
            self.started_by_us = False
            return True

        if not _is_loopback_url(self.base_url):
            return False

        ollama_bin = _find_ollama_binary()
        if not ollama_bin:
            return False

        env = os.environ.copy()
        env.setdefault("OLLAMA_NUM_PARALLEL", "1")
        env.setdefault("OLLAMA_MAX_LOADED_MODELS", "1")
        env.setdefault("OLLAMA_FLASH_ATTENTION", "1")
        netloc = urlparse(self.base_url).netloc
        if netloc:
            env["OLLAMA_HOST"] = netloc

        print(
            f"🚀 Demarrage automatique d'Ollama local ({self.base_url}, modele={self.model})...",
            file=sys.stderr,
        )
        try:
            self._proc = subprocess.Popen(
                [ollama_bin, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
                start_new_session=True,
                shell=False,
            )
        except OSError as exc:
            print(f"⚠️ Echec lancement Ollama : {exc}", file=sys.stderr)
            self._proc = None
            return False

        self.started_by_us = True
        self._cleaned_up = False
        if not self._atexit_registered:
            atexit.register(self.cleanup)
            self._atexit_registered = True

        deadline = time.monotonic() + max(timeout_s, 1.0)
        while time.monotonic() < deadline:
            if self._proc.poll() is not None:
                self._proc = None
                self.started_by_us = False
                return False
            if check_ollama_ready(self.base_url, timeout=0.4):
                return True
            time.sleep(0.25)

        self.cleanup()
        return False

    def unload_model(self, model: str | None = None, timeout: float = 3.0) -> bool:
        """Decharge le modele de la memoire unifiee via keep_alive=0."""
        target = (model or self.model).strip()
        if not target or not check_ollama_ready(self.base_url, timeout=0.4):
            return False
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": target, "keep_alive": 0, "prompt": ""},
                timeout=timeout,
            )
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def cleanup(self, force_unload_external: bool = False) -> None:
        """Decharge le modele et arrete ollama serve uniquement si nous l'avons demarre."""
        if self._cleaned_up and not force_unload_external:
            return

        if self.started_by_us or force_unload_external:
            self.unload_model()

        if self.started_by_us and self._proc is not None:
            proc = self._proc
            if proc.poll() is None:
                print("🛑 Arret d'Ollama demarre pour cette session (liberation RAM)...", file=sys.stderr)
                try:
                    proc.terminate()
                    proc.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    try:
                        proc.wait(timeout=2.0)
                    except subprocess.TimeoutExpired:
                        pass
                except OSError:
                    pass
            self._proc = None
            self.started_by_us = False

        self._cleaned_up = True


def parse_keywords_arg(raw: str | None) -> list[str]:
    """Decoupe une chaine CSV CLI en liste de mots-cles nettoyes."""
    if not raw:
        return []
    seen: set[str] = set()
    items: list[str] = []
    for part in re.split(r"[,;\n]+", raw):
        token = part.strip()
        lowered = token.lower()
        if token and lowered not in seen:
            seen.add(lowered)
            items.append(token)
    return items


def _strip_accents_basic(text: str) -> str:
    replacements = str.maketrans("àâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ", "aaaeeeeiioouuucAAAEEEEIIOOUUUC")
    return text.translate(replacements)


def extract_lexical_keywords(query: str) -> tuple[list[str], list[str]]:
    """
    Extrait des mots-cles deterministes (hl_keywords, ll_keywords) sans appel LLM.
    Permet a LightRAG kg_query() de contourner get_keywords_from_query() hors ligne.
    """
    cleaned = (query or "").strip()
    if not cleaned:
        return [], []

    ll_keywords: list[str] = []
    seen_ll: set[str] = set()

    def _add_ll(tok: str) -> None:
        val = tok.strip(" \t\r\n.,;:!?()[]{}<>\"'`")
        key = _strip_accents_basic(val).lower()
        if not val or key in seen_ll:
            return
        seen_ll.add(key)
        ll_keywords.append(val)

    for match in _TECH_TOKEN_RE.findall(cleaned):
        candidate = match.strip()
        if _strip_accents_basic(candidate).lower() not in _STOPWORDS and len(candidate) >= 2:
            _add_ll(candidate)

    content_words: list[str] = []
    for raw_tok in re.findall(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9._/-]*", cleaned):
        norm_tok = _strip_accents_basic(raw_tok).lower()
        if norm_tok in _STOPWORDS or len(raw_tok) < 3:
            continue
        content_words.append(raw_tok)
        _add_ll(raw_tok)

    hl_keywords: list[str] = []
    seen_hl: set[str] = set()

    def _add_hl(tok: str) -> None:
        val = tok.strip()
        key = _strip_accents_basic(val).lower()
        if val and key not in seen_hl:
            seen_hl.add(key)
            hl_keywords.append(val)

    if content_words:
        _add_hl(" ".join(content_words[:6]))
        for idx in range(len(content_words) - 1):
            _add_hl(f"{content_words[idx]} {content_words[idx + 1]}")
        for word in content_words[:6]:
            _add_hl(word)

    if not ll_keywords:
        _add_ll(cleaned)
    if not hl_keywords:
        _add_hl(cleaned)

    return hl_keywords[:12], ll_keywords[:12]


def build_rerank_model(cache_dir: str | Path | None = None, model_name: str = DEFAULT_RERANK_MODEL) -> Any | None:
    """Charge le modele Cross-Encoder FastEmbed compatible TextCrossEncoder / TextReranker."""
    if _RerankerImpl is None:
        return None
    target_cache = str(cache_dir or os.environ.get("FASTEMBED_CACHE_PATH", DEFAULT_FASTEMBED_CACHE_DIR))
    try:
        return _RerankerImpl(model_name, cache_dir=target_cache)
    except Exception as exc:
        print(f"⚠️ Impossible de charger le Reranker ({model_name}) : {exc}", file=sys.stderr)
        return None


def score_documents_with_reranker(rerank_model: Any, query: str, documents: list[str]) -> list[float]:
    """Retourne des scores normalises [0.0, 1.0] via sigmoide avec gestion gracieuse d'erreur."""
    if not documents or rerank_model is None:
        return [0.0 for _ in documents]
    try:
        raw_scores = list(rerank_model.rerank(query, documents))
        return [float(1.0 / (1.0 + np.exp(-float(score)))) for score in raw_scores]
    except Exception as exc:
        print(f"⚠️ Echec technique du Reranking : {exc}", file=sys.stderr)
        return [0.0 for _ in documents]


def filter_and_clean_chunks(chunks: list[dict[str, Any]], skip_images: bool = True) -> list[dict[str, Any]]:
    """
    Filtre les chunks d'images bitmap si demande tout en conservant .svg et .pdf.
    Trie par rerank_score decroissant lorsqu'il est deja present.
    """
    if not chunks:
        return []
    result: list[dict[str, Any]] = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        file_path = str(chunk.get("file_path") or "").strip().lower()
        if skip_images and file_path.endswith(IMAGE_EXTS):
            continue
        result.append(chunk)

    if result and any("rerank_score" in c for c in result):
        result.sort(key=lambda item: float(item.get("rerank_score", 0.0)), reverse=True)
    return result


def is_gemini_model_name(model_name: str | None) -> bool:
    """Indique si un nom de modele designe un modele API Google Gemini."""
    norm = (model_name or "").strip().lower()
    if norm.startswith("models/"):
        norm = norm[7:]
    return norm.startswith("gemini-")


def get_gemini_timeout_s(role: str = "index", minimum_s: float = 10.0) -> float:
    """
    Retourne le timeout HTTP par requete Gemini en secondes (minimum strict 10s exige par Google API).
    - role='index' : GEMINI_HTTP_TIMEOUT_S (defaut 60s)
    - role='qa' / 'audit' : GEMINI_QA_TIMEOUT_S (defaut 15s)
    """
    norm_role = normalize_rag_role(role)
    env_key = "GEMINI_HTTP_TIMEOUT_S" if norm_role == "index" else "GEMINI_QA_TIMEOUT_S"
    default_val = "60" if norm_role == "index" else "15"
    raw = os.environ.get(env_key) or os.environ.get("GEMINI_HTTP_TIMEOUT_S") or default_val
    try:
        return max(float(minimum_s), 10.0, float(raw))
    except ValueError:
        return max(float(minimum_s), 10.0, float(default_val))


def build_gemini_cascade(role: str = "qa", explicit_model: str | None = None) -> list[str]:
    """Construit la cascade ordonnee de modeles Gemini Free Tier adaptee a la tache."""
    raw_role = (role or "qa").strip().lower()
    env_models = [m.strip() for m in os.environ.get("GEMINI_AUTO_MODELS", "").split(",") if m.strip()]
    if env_models:
        base = list(env_models)
    elif raw_role == "vlm":
        base = list(GEMINI_VLM_CASCADE)
    elif normalize_rag_role(raw_role) == "index":
        base = list(GEMINI_INDEX_CASCADE)
    else:
        base = list(GEMINI_QA_CASCADE)

    ordered: list[str] = []
    seen: set[str] = set()

    def _push(candidate: str | None) -> None:
        val = (candidate or "").strip()
        if not val:
            return
        norm = val[7:] if val.startswith("models/") else val
        if norm not in seen:
            seen.add(norm)
            ordered.append(norm)

    if explicit_model and is_gemini_model_name(explicit_model):
        _push(explicit_model)

    env_default = (os.environ.get("RAG_DEFAULT_MODEL") or "").strip()
    env_norm = env_default[7:] if env_default.startswith("models/") else env_default
    if env_default and is_gemini_model_name(env_default) and env_norm not in _NON_FREE_OR_DEAD_GEMINI:
        _push(env_default)

    for candidate in base:
        _push(candidate)
    return ordered


def create_genai_client(api_key: str | None = None, timeout_s: float | None = None):
    """Instancie un client Google GenAI avec timeout HTTP >= 10s pour eviter tout blocage."""
    eff_key = (api_key if api_key is not None else os.environ.get("GEMINI_API_KEY", "")).strip()
    if not eff_key:
        return None
    from google import genai
    from google.genai import types as genai_types

    eff_timeout = max(10.0, float(timeout_s if timeout_s is not None else get_gemini_timeout_s("qa")))
    http_options = genai_types.HttpOptions(timeout=int(round(eff_timeout * 1000)))
    return genai.Client(api_key=eff_key, http_options=http_options)


def build_gemini_contents(
    prompt: str,
    history_messages: list | None = None,
    system_prompt: str | None = None,
):
    """Convertit prompt + history_messages en contents multi-tours Gemini (roles user/model)."""
    if not history_messages:
        return prompt, system_prompt
    from google.genai import types as genai_types

    extra_system = [system_prompt] if system_prompt else []
    contents: list[Any] = []
    for msg in history_messages:
        if not isinstance(msg, dict):
            continue
        text = str(msg.get("content") or "")
        if not text.strip():
            continue
        raw_role = str(msg.get("role") or "user").lower()
        if raw_role == "system":
            extra_system.append(text)
            continue
        gem_role = "model" if raw_role in ("assistant", "model") else "user"
        contents.append(
            genai_types.Content(role=gem_role, parts=[genai_types.Part.from_text(text=text)])
        )
    contents.append(
        genai_types.Content(role="user", parts=[genai_types.Part.from_text(text=prompt)])
    )
    effective_system = "\n\n".join(extra_system) if extra_system else None
    return contents, effective_system


def format_gemini_error(err: Exception) -> str:
    """Formate une exception Gemini/httpx en conservant son type utile."""
    msg = str(err).strip().replace("\n", " ")
    cls_name = type(err).__name__
    if not msg:
        return cls_name
    if "timeout" in cls_name.lower() and "timeout" not in msg.lower():
        return f"{cls_name}: {msg}"
    return msg


def classify_gemini_error(err_msg: str) -> str:
    """Classe une erreur Gemini en auth / permanent / rate_limit / other."""
    low = (err_msg or "").lower()
    if any(k in low for k in ("api_key_invalid", "api key not valid", "permission_denied", "unauthenticated", "401", "403")):
        return "auth"
    if any(k in low for k in ("404", "not_found", "invalid_argument", "perday", "per_day", "daily", "limit: 0")):
        return "permanent"
    if any(
        k in low
        for k in (
            "429",
            "resource_exhausted",
            "perminute",
            "rpm",
            "tpm",
            "503",
            "504",
            "unavailable",
            "high demand",
            "overloaded",
            "quota",
            "timeout",
            "timed out",
            "deadline_exceeded",
        )
    ):
        return "rate_limit"
    return "other"


def _compact_error_tag(err_msg: str) -> str:
    low = (err_msg or "").lower()
    for code, label in (
        ("503", "503 UNAVAILABLE"),
        ("504", "504 DEADLINE"),
        ("deadline_exceeded", "504 DEADLINE"),
        ("429", "429 QUOTA"),
        ("resource_exhausted", "429 QUOTA"),
        ("404", "404 NOT_FOUND"),
        ("400", "400 INVALID_ARG"),
        ("timeout", "TIMEOUT"),
    ):
        if code in low:
            return label
    cleaned = " ".join((err_msg or "ERREUR").split())
    return cleaned[:42]


class ModelExecutionTracker:
    """Enregistre les modeles tentes/utilises pour fournir une trace claire en Python et MCP."""

    def __init__(self, role: str = "qa", default_no_llm_label: str | None = None) -> None:
        self.role = normalize_rag_role(role)
        self.default_no_llm_label = default_no_llm_label or "Aucun LLM (mode lexical/antigravity)"
        self.fallback_note: str | None = None
        self.successes: Counter[tuple[str, str]] = Counter()
        self.failures: list[tuple[str, str, str]] = []
        self._failure_keys: set[tuple[str, str, str]] = set()
        self.last_provider: str | None = None
        self.last_model: str | None = None
        self._lock = threading.Lock()

    def record_success(self, provider: str, model: str) -> None:
        with self._lock:
            pair = (provider, model)
            self.successes[pair] += 1
            self.last_provider = provider
            self.last_model = model

    def record_failure(self, provider: str, model: str, reason: str) -> None:
        tag = _compact_error_tag(reason)
        with self._lock:
            item = (provider, model, tag)
            if item not in self._failure_keys:
                self._failure_keys.add(item)
                self.failures.append(item)

    def format_summary(self) -> str:
        with self._lock:
            if not self.successes:
                if self.failures:
                    failed_str = ", ".join(f"{p}/{m} ({r})" for p, m, r in self.failures[:4])
                    if self.fallback_note:
                        return f"{self.fallback_note} | echecs: {failed_str}"
                    return f"Echec LLM [role={self.role}] | echecs: {failed_str}"
                return self.default_no_llm_label

            parts = []
            for (prov, mod), count in self.successes.most_common():
                suffix = f" x{count}" if count > 1 else ""
                parts.append(f"{prov} / {mod}{suffix}")
            summary = f"{', '.join(parts)} [role={self.role}]"
            if self.failures:
                hops = ", ".join(f"{m}->{r}" for _, m, r in self.failures[:4])
                if len(self.failures) > 4:
                    hops += f" (+{len(self.failures) - 4})"
                summary += f" | bascules: {hops}"
            return summary

    def format_markdown_line(self) -> str:
        return f"> **Trace Moteur RAG** : {self.format_summary()}"


async def generate_gemini_text_async(
    client: Any,
    model_name: str,
    contents_payload: Any,
    config: Any,
    timeout_s: float,
    grace_s: float = 5.0,
) -> str:
    """Execute generate_content dans un thread avec timeout asyncio borne."""
    loop = asyncio.get_running_loop()
    wait_budget_s = max(10.0, float(timeout_s)) + max(0.0, float(grace_s))
    try:
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda m=model_name, c=config, payload=contents_payload: client.models.generate_content(
                    model=m,
                    contents=payload,
                    config=c,
                ),
            ),
            timeout=wait_budget_s,
        )
    except asyncio.TimeoutError as err:
        raise TimeoutError(f"Gemini timeout apres {wait_budget_s:.1f}s ({model_name})") from err
    return getattr(response, "text", None) or ""


class GeminiCascadeSession:
    """Routeur resilient sur la cascade Gemini avec cache des echecs et retry sans thinking_config."""

    def __init__(
        self,
        cascade: list[str],
        *,
        timeout_s: float = 15.0,
        thinking_budget: int = 100,
        rpm_delay: float = 0.0,
        cooldown_s: float = 45.0,
        wait_on_transient: bool = False,
        tracker: ModelExecutionTracker | None = None,
    ) -> None:
        self.cascade = list(cascade)
        self.timeout_s = max(10.0, float(timeout_s))
        self.thinking_budget = thinking_budget
        self.rpm_delay = max(0.0, float(rpm_delay))
        self.cooldown_s = max(5.0, float(cooldown_s))
        self.wait_on_transient = wait_on_transient
        self.tracker = tracker
        self.exhausted_models: set[str] = set()
        self.cooldown_until: dict[str, float] = {}
        self.transient_hits: dict[str, int] = {}
        self.no_thinking_models: set[str] = set()
        self.cloud_exhausted: bool = False

    def _build_config(
        self,
        model_name: str,
        effective_system: str | None,
        max_tokens: int,
        temperature: float,
        *,
        use_thinking: bool,
    ):
        from google.genai import types as genai_types

        kwargs: dict[str, Any] = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        if effective_system:
            kwargs["system_instruction"] = effective_system
        if use_thinking and self.thinking_budget is not None:
            kwargs["thinking_config"] = genai_types.ThinkingConfig(thinking_budget=self.thinking_budget)
        return genai_types.GenerateContentConfig(**kwargs)

    async def call(
        self,
        client: Any,
        prompt: str,
        *,
        system_prompt: str | None = None,
        history_messages: list | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        tracker: ModelExecutionTracker | None = None,
    ) -> tuple[str | None, str | None]:
        if client is None or not self.cascade:
            self.cloud_exhausted = True
            return None, None

        active_tracker = tracker or self.tracker
        contents_payload, effective_system = build_gemini_contents(
            prompt, history_messages=history_messages, system_prompt=system_prompt
        )
        waited_cooldown = False

        while True:
            now = time.time()
            candidates = [
                m for m in self.cascade
                if m not in self.exhausted_models and now >= self.cooldown_until.get(m, 0.0)
            ]
            if not candidates:
                pending = [
                    self.cooldown_until[m] - now
                    for m in self.cascade
                    if m not in self.exhausted_models and self.cooldown_until.get(m, 0.0) > now
                ]
                if self.wait_on_transient and pending and not waited_cooldown:
                    wait_s = max(1.0, min(46.0, max(pending) + 0.05))
                    await asyncio.sleep(wait_s)
                    for m_cool in list(self.cooldown_until):
                        if self.cooldown_until[m_cool] <= now + wait_s + 0.1:
                            self.cooldown_until.pop(m_cool, None)
                    waited_cooldown = True
                    continue
                if all(m in self.exhausted_models for m in self.cascade):
                    self.cloud_exhausted = True
                return None, None

            for current_model in candidates:
                use_thinking = (current_model not in self.no_thinking_models) and (self.thinking_budget is not None)
                try:
                    cfg = self._build_config(
                        current_model,
                        effective_system,
                        max_tokens,
                        temperature,
                        use_thinking=use_thinking,
                    )
                    text = await generate_gemini_text_async(
                        client,
                        current_model,
                        contents_payload,
                        cfg,
                        timeout_s=self.timeout_s,
                    )
                    if not text.strip():
                        raise RuntimeError("Reponse Gemini vide")
                    self.transient_hits[current_model] = 0
                    self.cooldown_until.pop(current_model, None)
                    if active_tracker is not None:
                        active_tracker.record_success("gemini", current_model)
                    if self.rpm_delay > 0:
                        await asyncio.sleep(self.rpm_delay)
                    return text, current_model
                except Exception as err:
                    err_s = format_gemini_error(err)
                    if use_thinking and "invalid_argument" in err_s.lower() and "deadline" not in err_s.lower():
                        self.no_thinking_models.add(current_model)
                        try:
                            cfg_retry = self._build_config(
                                current_model,
                                effective_system,
                                max_tokens,
                                temperature,
                                use_thinking=False,
                            )
                            text_retry = await generate_gemini_text_async(
                                client,
                                current_model,
                                contents_payload,
                                cfg_retry,
                                timeout_s=self.timeout_s,
                            )
                            if text_retry.strip():
                                self.transient_hits[current_model] = 0
                                if active_tracker is not None:
                                    active_tracker.record_success("gemini", current_model)
                                if self.rpm_delay > 0:
                                    await asyncio.sleep(self.rpm_delay)
                                return text_retry, current_model
                        except Exception as retry_err:
                            err_s = format_gemini_error(retry_err)

                    kind = classify_gemini_error(err_s)
                    if active_tracker is not None:
                        active_tracker.record_failure("gemini", current_model, err_s)
                    if kind == "auth":
                        self.exhausted_models.update(self.cascade)
                        self.cloud_exhausted = True
                        return None, None
                    if kind == "permanent":
                        self.exhausted_models.add(current_model)
                        continue
                    self.cooldown_until[current_model] = time.time() + self.cooldown_s
                    hits = self.transient_hits.get(current_model, 0) + 1
                    self.transient_hits[current_model] = hits
                    if self.wait_on_transient and (hits >= 2 or waited_cooldown):
                        self.exhausted_models.add(current_model)

            if not self.wait_on_transient:
                return None, None
            if all(m in self.exhausted_models for m in self.cascade):
                self.cloud_exhausted = True
                return None, None


def sync_db_to_backup_mirror(
    source_db: Path,
    mirror_db: Path | None = None,
) -> tuple[bool, str]:
    """Synchronise la base LightRAG locale vers le miroir de sauvegarde Google Drive."""
    src = Path(source_db).resolve()
    raw_src_str = str(source_db)
    if not src.is_dir():
        return False, f"Source introuvable : {src}"
    if raw_src_str.startswith(("/tmp/", "/var/folders/", "/private/tmp/", "/private/var/folders/")):
        return False, "Miroir ignore pour repertoire sandbox temporaire."

    target = Path(
        mirror_db or os.environ.get("RAG_BACKUP_MIRROR_PATH") or DEFAULT_DRIVE_MIRROR_DB_PATH
    ).resolve()
    if src == target:
        return False, "Source et miroir identiques ; synchronisation ignoree."

    target.mkdir(parents=True, exist_ok=True)
    rsync_bin = shutil.which("rsync")
    if rsync_bin:
        cmd = [
            rsync_bin,
            "-a",
            "--delete",
            "--exclude",
            ".indexing.lock",
            "--exclude",
            ".agent_jobs/",
            "--exclude",
            ".docling_cache/",
            f"{src}/",
            f"{target}/",
        ]
        try:
            proc = subprocess.run(
                cmd,
                shell=False,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
            if proc.returncode == 0:
                return True, f"Miroir synchronise vers {target}"
            err_msg = (proc.stderr or proc.stdout or f"exit {proc.returncode}").strip()
            return False, f"Echec rsync miroir ({err_msg[:200]})"
        except (OSError, subprocess.SubprocessError) as exc:
            return False, f"Erreur rsync miroir : {exc}"

    try:
        ignored = shutil.ignore_patterns(".indexing.lock", ".agent_jobs", ".docling_cache")
        shutil.copytree(src, target, dirs_exist_ok=True, ignore=ignored)
        return True, f"Miroir copie (shutil) vers {target}"
    except OSError as exc:
        return False, f"Erreur copie miroir : {exc}"

