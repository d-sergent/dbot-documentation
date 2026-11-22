#!/opt/homebrew/bin/python3.11
import argparse
import asyncio
import base64
import inspect
import io
import json
import os
import shutil
import sys
import tempfile
import time
import hashlib
import logging
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from itertools import cycle

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

from source_key_utils import (
    build_active_source_aliases,
    build_claimed_source_map,
    build_rag_source_key,
    build_section_source_key,
    extract_rel_path,
    extract_section_key,
    is_doc_processed,
)
from rag_runtime import (
    DEFAULT_OLLAMA_QA_MODEL,
    GEMINI_INDEX_CASCADE,
    GEMINI_THINKING_BUDGETS,
    GEMINI_VLM_CASCADE,
    ManagedOllamaServer,
    _find_ollama_binary,
    _is_loopback_url,
    _ollama_model_matches,
    build_gemini_cascade,
    call_1minai_stateless_async,
    classify_gemini_error,
    format_gemini_error,
    get_gemini_timeout_s,
    is_1minai_permanent_or_quota_error,
    is_1minai_temperature_omitted,
    resolve_1minai_auto_index_target,
    resolve_default_db_path,
    resolve_ollama_config,
    sync_db_to_backup_mirror,
)
from rag_chunking import (
    EXCLUDE_DIRS,
    EXCLUDE_FILES,
    IMAGE_EXTS,
    INCLUDE_EXTS,
    PDF_EXTS,
    SVG_EXTS,
    chunking_markdown_anchored,
    collect_docs_files,
    compute_doc_id as _shared_compute_doc_id,
    compute_normalized_sha256,
    extract_pdf_text_cached,
    is_entity_summary_prompt,
    resolve_gleaning_for_doc,
    sanitize_lightrag_extraction_output,
    split_markdown_into_virtual_sections,
)
from agent_indexing import (
    IndexingFileLock,
    commit_agent_bundle,
    deterministic_merge_descriptions,
    prepare_agent_bundle,
    resolve_effort_profile,
)

# Charger les variables d'environnement (.env du projet)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
if not os.environ.get("OPENROUTER_API_KEY") and os.path.exists("/Users/Shared/Mon Google Drive Physique/Documentation/.env"):
    load_dotenv(dotenv_path="/Users/Shared/Mon Google Drive Physique/Documentation/.env")

# ─── Hack Tiktoken ────────────────────────────────────────────────────────────
import tiktoken
_original_encode = tiktoken.Encoding.encode
def _safe_encode(self, text, *args, **kwargs):
    kwargs["disallowed_special"] = ()
    return _original_encode(self, text, *args, **kwargs)
tiktoken.Encoding.encode = _safe_encode


# ─── Filtre Stderr "Deep Silence" ────────────────────────────────────────────
# LightRAG écrit les tracebacks directement sur stderr (pas via logging).
# On remplace sys.stderr par un filtre ligne-par-ligne qui bloque les stacks.
class StderrQuietFilter:
    """Filtre sys.stderr : supprime les blocs Traceback, garde les lignes utiles."""
    SKIP_PATTERNS = (
        "Traceback (most recent",
        "  File \"",
        "    ",         # lignes indentées de traceback
        "ValueError:",
        "RuntimeError:",
        "Exception:",
        "google.api_core",
        "During handling",
        "The above exception",
        "raise prefixed",
        "raise ValueError",
        "^^^^",
        "~~~~",
    )

    def __init__(self, original):
        self._original = original
        self._in_traceback = False

    def write(self, msg):
        for line in msg.splitlines(keepends=True):
            stripped = line.strip()
            if stripped.startswith("Traceback"):
                self._in_traceback = True
            if self._in_traceback:
                # On cherche la fin du bloc : une ligne vide après le bloc
                if stripped == "" :
                    self._in_traceback = False
                return  # on jette tout le bloc
            # Lignes hors traceback : on vérifie les patterns courts
            if any(stripped.startswith(p) for p in self.SKIP_PATTERNS):
                return
            self._original.write(line)

    def flush(self):
        self._original.flush()

    def fileno(self):
        return self._original.fileno()

sys.stderr = StderrQuietFilter(sys.stderr)

# ─── Configuration Logging Python ────────────────────────────────────────────
class NoExcInfoFilter(logging.Filter):
    def filter(self, record):
        record.exc_info = None
        record.exc_text = None
        # Bloque les messages verbeux de LightRAG via logging
        msg = record.getMessage()
        for pat in ("Error in decorated function", "Failed to extract", "Traceback"):
            if pat in msg:
                return False
        return True

formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')

handler_stdout = logging.StreamHandler(sys.stdout)
handler_stdout.setFormatter(formatter)
handler_stdout.addFilter(NoExcInfoFilter())

def _detect_running_in_tests(argv: list[str] | None = None) -> bool:
    """Detecte un runner unittest/pytest via sys.argv (sans tester sys.modules)."""
    if os.environ.get("RAG_DISABLE_FILE_LOG", "").strip().lower() in ("1", "true", "yes"):
        return True
    args_list = list(sys.argv if argv is None else argv)
    if not args_list:
        return False
    arg0 = str(args_list[0] or "")
    base0 = os.path.basename(arg0)
    if base0 in ("pytest", "py.test") or base0.startswith("test_"):
        return True
    if arg0.endswith("/unittest/__main__.py") or base0 == "unittest":
        return True
    for tok in args_list[1:4]:
        t_base = os.path.basename(str(tok or ""))
        if t_base in ("unittest", "pytest", "py.test") or t_base.startswith("test_"):
            return True
    return False


_CUSTOM_LOG_PATH = os.environ.get("RAG_INDEX_LOG_PATH", "").strip()
_RUNNING_IN_TESTS = _detect_running_in_tests()
if _RUNNING_IN_TESTS and not _CUSTOM_LOG_PATH:
    handler_file: logging.Handler = logging.NullHandler()
else:
    _log_target = Path(_CUSTOM_LOG_PATH) if _CUSTOM_LOG_PATH else (Path(__file__).resolve().parent / "rag_indexing.log")
    handler_file = logging.FileHandler(_log_target, encoding="utf-8")
    handler_file.setFormatter(formatter)
    handler_file.addFilter(NoExcInfoFilter())

logging.basicConfig(level=logging.INFO, handlers=[handler_stdout, handler_file], force=True)
logger = logging.getLogger("D-Bot-RAG")


# ─── Configuration Chemins ───────────────────────────────────────────────────
DOCS_ROOT = Path("/Users/Shared/Mon Google Drive Physique/Documentation")
DB_PATH   = Path(resolve_default_db_path())
INDEX_LOG = DB_PATH / "indexed_files.json"

# ─── Stratégie Round-Robin Hybride (Gemini + OpenRouter) ────────────────────────
import aiohttp

MODELS_ROTATION = [
    {"name": "models/gemini-3.8-flash", "type": "gemini"},
    {"name": "models/gemini-3.6-flash", "type": "gemini"},
    {"name": "models/gemini-2.5-flash", "type": "gemini"},
    {"name": "poolside/laguna-s-2.1:free", "type": "openrouter"},
    {"name": "nvidia/nemotron-3-super-120b-a12b:free", "type": "openrouter"},
    {"name": "nvidia/nemotron-3-ultra-550b-a55b:free", "type": "openrouter"},
    {"name": "inclusionai/ling-3.0-flash-fin:free", "type": "openrouter"},
    {"name": "nvidia/nemotron-3.5-lightning:free", "type": "openrouter"},
]
model_cycle = cycle(MODELS_ROTATION)
# Au lieu de tuer un modèle après 3 erreurs, on le met en "pause" jusqu'à un certain timestamp
stats = {m["name"]: {"success": 0, "failures": 0, "locked_until": 0} for m in MODELS_ROTATION}

# ─── Imports LLM / Embedding ──────────────────────────────────────────────────
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="fastembed")

try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import openai_complete_if_cache
    from lightrag.utils import EmbeddingFunc
    from fastembed import TextEmbedding
    import numpy as np
    from google import genai
    from google.genai import types as genai_types
    from PIL import Image
    import pypdf
    import requests
    import defusedxml.ElementTree as DefusedET
except ImportError as e:
    logger.error(f"Dépendance manquante : {e}")
    sys.exit(1)


class _ForwardWarningToHandler(logging.Handler):
    """Transfère les logs externes >= min_level (ou filtrés) vers rag_indexing.log."""

    def __init__(
        self,
        target_handler: logging.Handler,
        min_level: int = logging.WARNING,
        info_predicate=None,
    ):
        super().__init__(level=min_level)
        self._target = target_handler
        self._info_predicate = info_predicate

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno < logging.WARNING:
            if self._info_predicate is None or not self._info_predicate(record.getMessage()):
                return
        self._target.handle(record)


def _is_lightrag_chunk_progress(msg: str) -> bool:
    """Retient uniquement les lignes de progression chunk/KG de LightRAG."""
    return (
        ("Chunk " in msg and " of " in msg)
        or "Rebuilding knowledge" in msg
    )


def _configure_third_party_loggers() -> None:
    """Rattache rag_indexing.log aux loggers à propagate=False (ex. LightRAG)."""
    logging.getLogger("nano-vectordb").setLevel(logging.WARNING)
    for ext_name in ("lightrag", "nano-vectordb"):
        ext_logger = logging.getLogger(ext_name)
        if not any(isinstance(f, NoExcInfoFilter) for f in ext_logger.filters):
            ext_logger.addFilter(NoExcInfoFilter())
        if not ext_logger.propagate and not any(
            isinstance(h, _ForwardWarningToHandler) for h in ext_logger.handlers
        ):
            min_lvl = logging.INFO if ext_name == "lightrag" else logging.WARNING
            pred = _is_lightrag_chunk_progress if ext_name == "lightrag" else None
            ext_logger.addHandler(_ForwardWarningToHandler(handler_file, min_lvl, pred))


_configure_third_party_loggers()

# ─── Embeddings Locaux (FastEmbed) ───────────────────────────────────────────
import warnings
warnings.filterwarnings("ignore", message=".*intfloat/multilingual-e5-large now uses mean pooling.*")

DEFAULT_CACHE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/models_cache"
FASTEMBED_CACHE_DIR = os.environ.get("FASTEMBED_CACHE_PATH", DEFAULT_CACHE_DIR)
_embed_model = TextEmbedding("intfloat/multilingual-e5-large", cache_dir=FASTEMBED_CACHE_DIR)
EMBEDDING_DIM = 1024

async def fastembed_func(texts: list[str]) -> np.ndarray:
    embeddings = list(_embed_model.embed(texts))
    return np.array(embeddings, dtype=np.float32)

embedding_func = EmbeddingFunc(
    embedding_dim=EMBEDDING_DIM,
    max_token_size=8192,
    func=fastembed_func
)

# ─── LLM Factory ─────────────────────────────────────────────────────────────

# Paramètres recommandés Qwen3.8 / Unsloth en mode Non-Thinking pour l'extraction structurée
QWEN_EXTRACT_SAMPLING = {
    "temperature": 0.1,
    "top_p": 0.80,
    "top_k": 20,
    "min_p": 0.0,
    "repeat_penalty": 1.0,
    "presence_penalty": 0.3,
}


def _build_local_extra_body(call_kwargs: dict) -> dict:
    """Construit extra_body pour desactiver Thinking et fixer l'echantillonnage Qwen3.8 sur Unsloth / llama-server."""
    extra_body = {
        "chat_template_kwargs": {"enable_thinking": False},
        "top_k": call_kwargs.pop("top_k", QWEN_EXTRACT_SAMPLING["top_k"]),
        "min_p": call_kwargs.pop("min_p", QWEN_EXTRACT_SAMPLING["min_p"]),
        "repeat_penalty": call_kwargs.pop("repeat_penalty", QWEN_EXTRACT_SAMPLING["repeat_penalty"]),
    }
    user_extra = call_kwargs.pop("extra_body", None)
    if isinstance(user_extra, dict):
        extra_body.update(user_extra)
    return extra_body


def _build_openai_messages(
    prompt: str,
    system_prompt: str | None = None,
    history_messages: list | None = None,
) -> list[dict[str, str]]:
    """Construit la liste de messages OpenAI/Ollama en incluant history_messages."""
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    for msg in history_messages or []:
        if isinstance(msg, dict) and "role" in msg and msg.get("content"):
            messages.append({"role": str(msg["role"]), "content": str(msg["content"])})
    messages.append({"role": "user", "content": prompt})
    return messages


def _build_gemini_contents(
    prompt: str,
    history_messages: list | None = None,
    system_prompt: str | None = None,
) -> tuple[list[genai_types.Content] | str, str | None]:
    """Convertit prompt + history_messages en contents multi-tours Gemini (roles user/model)."""
    if not history_messages:
        return prompt, system_prompt

    extra_system = [system_prompt] if system_prompt else []
    contents: list[genai_types.Content] = []
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


async def _post_json_aiohttp(
    url: str,
    payload: dict,
    *,
    timeout_s: float,
    headers: dict[str, str] | None = None,
    service_name: str = "HTTP",
    include_error_body: bool = False,
) -> dict:
    """Exécute un POST JSON asynchrone via aiohttp et convertit les erreurs transport en RuntimeError."""
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


async def _call_openrouter_chat(
    model_name: str,
    prompt: str,
    system_prompt: str | None = None,
    history_messages: list | None = None,
    timeout_s: int = 45,
) -> str:
    """Appel HTTP OpenRouter partagé avec support de history_messages."""
    or_key = os.environ.get("OPENROUTER_API_KEY")
    if not or_key:
        raise RuntimeError("OPENROUTER_API_KEY manquante")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {or_key}", "Content-Type": "application/json"}
    messages = _build_openai_messages(prompt, system_prompt, history_messages)
    data = await _post_json_aiohttp(
        url,
        {"model": model_name, "messages": messages},
        timeout_s=timeout_s,
        headers=headers,
        service_name="OpenRouter",
    )
    if "error" in data:
        err_info = data["error"]
        raise RuntimeError(
            f"OpenRouter_{err_info.get('code', 'Error')}: {err_info.get('message', 'Unknown error')}"
        )
    choices = data.get("choices")
    if not choices:
        raise RuntimeError("OpenRouter response missing 'choices'")
    return choices[0]["message"]["content"]


GEMINI_CASCADE_MODELS = GEMINI_INDEX_CASCADE


def _ensure_ollama_available(
    managed_ollama: ManagedOllamaServer,
    *,
    require_model: bool = True,
) -> tuple[bool, str]:
    """Démarre Ollama local si nécessaire (boucle locale) et vérifie la disponibilité du modèle cible."""
    if not managed_ollama.ensure_started():
        return (
            False,
            f"Serveur Ollama injoignable sur {managed_ollama.base_url} et démarrage automatique impossible.",
        )
    if require_model:
        ok, diag = _check_ollama_ready(managed_ollama.base_url, managed_ollama.model)
        if not ok:
            return False, f"Ollama actif sur {managed_ollama.base_url}, mais {diag}"
    return True, "OK"


def _classify_ollama_stage(prompt: str, history_messages: list | None) -> str:
    """Identifie le role d'un appel Ollama LightRAG pour le suivi de progression."""
    if history_messages:
        return "gleaning"
    low = (prompt or "").lower()
    if "many entities" in low and "missed" in low:
        return "gleaning"
    if "---task---" in low or "extract entities" in low:
        return "extract"
    if "description list" in low or "summarize" in low:
        return "resume"
    if "high_level_keywords" in low:
        return "keywords"
    return "appel"


def _build_ollama_llm_func(
    explicit_model: str | None = None,
    semaphore: asyncio.Semaphore | None = None,
    managed_ollama: ManagedOllamaServer | None = None,
    auto_state: dict | None = None,
):
    """Construit l'adaptateur asynchrone Ollama /api/chat (think=False, sampling Qwen3.8)."""
    ollama_base = _get_ollama_base_url()
    target_model = _get_ollama_model(explicit_model)
    _, _, num_ctx, keep_alive = resolve_ollama_config()
    verified_local = False
    init_lock = asyncio.Lock()
    call_counter = 0

    async def _post_ollama(payload: dict, stage: str, prompt_chars: int) -> str:
        nonlocal verified_local, call_counter
        eff_managed = (auto_state.get("managed_ollama") if auto_state else None) or managed_ollama
        if eff_managed is not None:
            async with init_lock:
                already_ok = bool(auto_state.get("ollama_verified")) if auto_state else verified_local
                if not already_ok:
                    ok, diag = await asyncio.to_thread(_ensure_ollama_available, eff_managed, require_model=True)
                    if not ok:
                        raise RuntimeError(diag)
                    if auto_state is not None:
                        auto_state["ollama_verified"] = True
                    else:
                        verified_local = True

        call_counter += 1
        call_id = call_counter
        t_start = time.perf_counter()
        logger.info(
            f"🦙 [Ollama #{call_id}] {stage} en cours ({target_model}, ~{prompt_chars} car.)..."
        )
        data = await _post_json_aiohttp(
            f"{ollama_base}/api/chat",
            payload,
            timeout_s=600,
            service_name="Ollama",
            include_error_body=True,
        )
        content = (data.get("message") or {}).get("content", "")
        if not content:
            raise RuntimeError("Réponse Ollama vide")
        elapsed_s = time.perf_counter() - t_start
        logger.info(
            f"🦙 [Ollama #{call_id}] {stage} terminé en {elapsed_s:.1f}s -> {len(content)} car."
        )
        return content

    async def llm_ollama(prompt, system_prompt=None, history_messages=[], **kwargs):
        messages = _build_openai_messages(prompt, system_prompt, history_messages)
        stage = _classify_ollama_stage(prompt, history_messages)
        prompt_chars = len(prompt or "")

        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "think": False,
            "keep_alive": keep_alive,
            "options": {
                "num_ctx": num_ctx,
                "temperature": kwargs.get("temperature", QWEN_EXTRACT_SAMPLING["temperature"]),
                "top_p": kwargs.get("top_p", QWEN_EXTRACT_SAMPLING["top_p"]),
                "top_k": kwargs.get("top_k", QWEN_EXTRACT_SAMPLING["top_k"]),
                "min_p": kwargs.get("min_p", QWEN_EXTRACT_SAMPLING["min_p"]),
                "repeat_penalty": kwargs.get("repeat_penalty", QWEN_EXTRACT_SAMPLING["repeat_penalty"]),
                "presence_penalty": kwargs.get("presence_penalty", QWEN_EXTRACT_SAMPLING["presence_penalty"]),
                "num_predict": kwargs.get("max_tokens", 8192),
            },
        }
        if semaphore is not None:
            async with semaphore:
                return await _post_ollama(payload, stage, prompt_chars)
        return await _post_ollama(payload, stage, prompt_chars)

    return llm_ollama


def _resolve_auto_models(explicit_model: str | None) -> tuple[list[str], str]:
    """Détermine la cascade Gemini complète (tous modèles Free Tier) et le modèle Ollama local de repli."""
    if explicit_model and "gemini" in explicit_model.lower():
        return build_gemini_cascade("index", explicit_model), _get_ollama_model(None)
    return build_gemini_cascade("index", None), _get_ollama_model(explicit_model)


def _check_ollama_ready(ollama_base: str, target_model: str) -> tuple[bool, str]:
    """Vérifie sans charger le modèle que le daemon Ollama répond et possède target_model."""
    try:
        resp = requests.get(f"{ollama_base}/api/tags", timeout=3)
        if resp.status_code != 200:
            return False, f"HTTP {resp.status_code}"
        models = [str(m.get("name") or m.get("model") or "") for m in (resp.json().get("models") or [])]
        if any(_ollama_model_matches(candidate, target_model) for candidate in models):
            return True, "OK"
        return False, f"modèle '{target_model}' absent (disponibles: {', '.join(models[:5]) or 'aucun'})"
    except Exception as err:
        return False, str(err)[:120]


def _get_gemini_timeout_s() -> float:
    """Retourne le timeout HTTP par requête Gemini en secondes (minimum strict 10s, défaut 60s)."""
    return get_gemini_timeout_s("index", minimum_s=10.0)


def _create_genai_client(api_key: str | None, timeout_s: float | None = None) -> genai.Client | None:
    """Instancie un client Google GenAI muni d'un timeout HTTP explicite (>= 10s en millisecondes)."""
    if not api_key:
        return None
    effective_timeout_s = _get_gemini_timeout_s() if timeout_s is None else max(10.0, float(timeout_s))
    http_options = genai_types.HttpOptions(timeout=int(round(effective_timeout_s * 1000)))
    return genai.Client(api_key=api_key, http_options=http_options)


async def _generate_gemini_text_async(
    client: genai.Client,
    model_name: str,
    contents_payload,
    config: genai_types.GenerateContentConfig,
    timeout_s: float,
    grace_s: float = 5.0,
) -> str:
    """Exécute generate_content dans un thread avec timeout asyncio borné."""
    loop = asyncio.get_running_loop()
    wait_budget_s = max(0.05, float(timeout_s)) + max(0.0, float(grace_s))
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
        raise TimeoutError(f"Gemini timeout après {wait_budget_s:.1f}s ({model_name})") from err
    return getattr(response, "text", None) or ""


def _format_gemini_error(err: Exception) -> str:
    """Formate une exception Gemini/httpx en conservant le nom de classe utile au routage."""
    return format_gemini_error(err)


def _classify_gemini_error(err_msg: str) -> str:
    """Classe une erreur Gemini en auth / permanent / rate_limit / other."""
    return classify_gemini_error(err_msg)


def _create_auto_state(
    args,
    api_key: str | None,
    managed_ollama: ManagedOllamaServer | None = None,
) -> dict:
    """Initialise l'état partagé du routeur --provider auto (Gemini -> 1min.ai gratuit -> Ollama)."""
    cascade, ollama_model = _resolve_auto_models(args.model)
    th_level = getattr(args, "thinking_level", "low").lower()
    oneminai_enabled, oneminai_url, oneminai_model, oneminai_key = resolve_1minai_auto_index_target(
        allow_1minai=True if bool(getattr(args, "with_1minai", False)) else None,
        disallow_1minai=bool(getattr(args, "no_1minai", False)),
    )
    return {
        "cascade": cascade,
        "ollama_model": ollama_model,
        "managed_ollama": managed_ollama,
        "ollama_verified": False,
        "thinking_budget": GEMINI_THINKING_BUDGETS.get(th_level, 100),
        "http_timeout_s": _get_gemini_timeout_s(),
        "rpm_delay": max(0.0, float(os.environ.get("GEMINI_RPM_DELAY", "2.5"))),
        "cloud_min_kb": max(0.0, float(getattr(args, "cloud_min_kb", 0.0))),
        "cloud_exhausted": not bool(api_key),
        "vlm_gemini_exhausted": not bool(api_key),
        "oneminai_enabled": oneminai_enabled,
        "oneminai_exhausted": not oneminai_enabled,
        "oneminai_url": oneminai_url,
        "oneminai_model": oneminai_model,
        "oneminai_key": oneminai_key,
        "oneminai_ok": 0,
        "oneminai_err": 0,
        "oneminai_consecutive_err": 0,
        "oneminai_prompt_tokens": 0,
        "oneminai_completion_tokens": 0,
        "oneminai_switched_logged": False,
        "prefer_local_doc": False,
        "switched_logged": False,
        "exhausted_models": set(),
        "no_thinking_models": set(),
        "cooldown_until": {},
        "transient_hits": {},
        "gemini_ok": {m: 0 for m in cascade},
        "vlm_ok": {},
        "gemini_err": 0,
        "ollama_ok": 0,
        "ollama_err": 0,
        "ollama_sem": asyncio.Semaphore(1),
    }


async def _call_gemini_cascade(
    client: genai.Client,
    state: dict,
    prompt: str,
    system_prompt: str | None = None,
    history_messages: list | None = None,
    **kwargs,
) -> tuple[str | None, str | None]:
    """Tente la cascade Gemini sans boucle infinie ; retourne (texte, modèle) ou (None, None) si épuisée."""
    cascade = state["cascade"]
    timeout_s = float(state.get("http_timeout_s") or _get_gemini_timeout_s())
    waited_cooldown = False
    no_thinking_models = state.setdefault("no_thinking_models", set())
    contents_payload, effective_system = _build_gemini_contents(
        prompt, history_messages=history_messages, system_prompt=system_prompt
    )

    while not state["cloud_exhausted"]:
        now = time.time()
        candidates = [
            m for m in cascade
            if m not in state["exhausted_models"] and now >= state["cooldown_until"].get(m, 0.0)
        ]
        if not candidates:
            pending = [
                state["cooldown_until"][m] - now
                for m in cascade
                if m not in state["exhausted_models"] and state["cooldown_until"].get(m, 0.0) > now
            ]
            if pending and not waited_cooldown:
                wait_s = max(1.0, min(46.0, max(pending) + 0.05))
                logger.warning(f"⏳ Rate-limit Gemini temporaire : pause {wait_s:.0f}s avant dernière tentative...")
                await asyncio.sleep(wait_s)
                for m_cool in list(state["cooldown_until"]):
                    if state["cooldown_until"][m_cool] <= now + wait_s + 0.1:
                        state["cooldown_until"].pop(m_cool, None)
                waited_cooldown = True
                continue
            state["cloud_exhausted"] = True
            break

        for current_model in candidates:
            use_thinking = current_model not in no_thinking_models
            try:
                cfg_kwargs = dict(
                    system_instruction=effective_system,
                    max_output_tokens=kwargs.get("max_tokens", 8192),
                    temperature=kwargs.get("temperature", QWEN_EXTRACT_SAMPLING["temperature"]),
                )
                if use_thinking:
                    cfg_kwargs["thinking_config"] = genai_types.ThinkingConfig(thinking_budget=state["thinking_budget"])
                cfg = genai_types.GenerateContentConfig(**cfg_kwargs)
                text = await _generate_gemini_text_async(
                    client,
                    current_model,
                    contents_payload,
                    cfg,
                    timeout_s=timeout_s,
                )
                if not text.strip():
                    raise RuntimeError("Réponse Gemini vide")
                state["transient_hits"][current_model] = 0
                state["cooldown_until"].pop(current_model, None)
                state["gemini_ok"][current_model] = state["gemini_ok"].get(current_model, 0) + 1
                if state["rpm_delay"] > 0:
                    await asyncio.sleep(state["rpm_delay"])
                return text, current_model
            except Exception as err:
                err_s = _format_gemini_error(err)
                if use_thinking and "invalid_argument" in err_s.lower() and "deadline" not in err_s.lower():
                    no_thinking_models.add(current_model)
                    try:
                        cfg_retry = genai_types.GenerateContentConfig(
                            system_instruction=effective_system,
                            max_output_tokens=kwargs.get("max_tokens", 8192),
                            temperature=kwargs.get("temperature", QWEN_EXTRACT_SAMPLING["temperature"]),
                        )
                        text_retry = await _generate_gemini_text_async(
                            client,
                            current_model,
                            contents_payload,
                            cfg_retry,
                            timeout_s=timeout_s,
                        )
                        if text_retry.strip():
                            state["transient_hits"][current_model] = 0
                            state["cooldown_until"].pop(current_model, None)
                            state["gemini_ok"][current_model] = state["gemini_ok"].get(current_model, 0) + 1
                            logger.info(f"ℹ️ Gemini {current_model} : compatibilité activée sans thinking_config.")
                            if state["rpm_delay"] > 0:
                                await asyncio.sleep(state["rpm_delay"])
                            return text_retry, current_model
                    except Exception as retry_err:
                        err_s = _format_gemini_error(retry_err)

                kind = _classify_gemini_error(err_s)
                state["gemini_err"] += 1
                if kind == "auth":
                    logger.error(f"❌ Clé ou accès Gemini refusé ({err_s[:80]}). Bascule immédiate sur Ollama local ({state['ollama_model']}).")
                    state["exhausted_models"].update(cascade)
                    state["cloud_exhausted"] = True
                    return None, None
                if kind == "permanent":
                    logger.warning(f"⚠️ Gemini {current_model} épuisé/indisponible ({err_s[:70]}). Exclu pour la session.")
                    state["exhausted_models"].add(current_model)
                    continue

                hits = state["transient_hits"].get(current_model, 0) + 1
                state["transient_hits"][current_model] = hits
                if hits >= 2 or waited_cooldown:
                    logger.warning(f"⚠️ Gemini {current_model} saturé après nouvel essai ({err_s[:70]}). Exclu pour la session.")
                    state["exhausted_models"].add(current_model)
                else:
                    cool_s = 45.0 if kind == "rate_limit" else 5.0
                    state["cooldown_until"][current_model] = time.time() + cool_s
                    logger.warning(f"⚠️ Gemini {current_model} limité ({err_s[:70]}). Cooldown {cool_s:.0f}s et passage au modèle suivant.")

        if all(m in state["exhausted_models"] for m in cascade):
            state["cloud_exhausted"] = True

    return None, None


async def get_llm_func(
    args,
    auto_state: dict | None = None,
    managed_ollama: ManagedOllamaServer | None = None,
):
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    
    if args.provider in ("local", "unsloth"):
        from rag_runtime import resolve_unsloth_config

        base_url, default_model, unsloth_key = resolve_unsloth_config()
        model = args.model or default_model
        logger.info(
            f"🔗 Mode UNSLOTH/LOCAL : {model} sur {base_url} "
            f"[enable_thinking=False, top_p={QWEN_EXTRACT_SAMPLING['top_p']}, "
            f"presence_penalty={QWEN_EXTRACT_SAMPLING['presence_penalty']}]"
        )

        async def llm_local(prompt, system_prompt=None, history_messages=[], **kwargs):
            call_kwargs = dict(kwargs)
            call_kwargs.setdefault("max_tokens", 8192)
            call_kwargs.setdefault("temperature", QWEN_EXTRACT_SAMPLING["temperature"])
            call_kwargs.setdefault("top_p", QWEN_EXTRACT_SAMPLING["top_p"])
            call_kwargs.setdefault("presence_penalty", QWEN_EXTRACT_SAMPLING["presence_penalty"])
            extra_body = _build_local_extra_body(call_kwargs)
            res = await openai_complete_if_cache(
                model,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                base_url=base_url,
                api_key=unsloth_key,
                extra_body=extra_body,
                **call_kwargs
            )
            return res
        return llm_local

    elif args.provider == "auto":
        state = auto_state if auto_state is not None else _create_auto_state(args, api_key, managed_ollama=managed_ollama)
        eff_managed = state.get("managed_ollama") or managed_ollama
        if eff_managed is not None and state.get("managed_ollama") is None:
            state["managed_ollama"] = eff_managed
        client = _create_genai_client(api_key, timeout_s=state["http_timeout_s"])
        ollama_base = _get_ollama_base_url()
        ollama_fn = _build_ollama_llm_func(
            state["ollama_model"],
            semaphore=state["ollama_sem"],
            managed_ollama=eff_managed,
            auto_state=state,
        )
        ollama_ok, ollama_diag = _check_ollama_ready(ollama_base, state["ollama_model"])
        if ollama_ok:
            state["ollama_verified"] = True

        tier2_txt = (
            f" -> repli 1min.ai gratuit ({state['oneminai_model']})"
            if state.get("oneminai_enabled")
            else ""
        )
        if state["cloud_exhausted"]:
            if state.get("oneminai_enabled"):
                logger.warning(
                    f"⚠️ GEMINI_API_KEY absente : mode AUTO démarre sur 1min.ai gratuit ({state['oneminai_model']}) "
                    f"-> dernier repli local Ollama ({state['ollama_model']})."
                )
            else:
                logger.warning(
                    f"⚠️ GEMINI_API_KEY absente : mode AUTO démarre directement sur Ollama ({state['ollama_model']})."
                )
        else:
            seuil_txt = f" | seuil Cloud >= {state['cloud_min_kb']:.0f} Ko" if state["cloud_min_kb"] > 0 else ""
            logger.info(
                f"⚡ Mode AUTO : Gemini ({', '.join(state['cascade'][:3])}... | timeout={state['http_timeout_s']:.0f}s)"
                f"{seuil_txt}{tier2_txt} -> dernier repli Ollama ({state['ollama_model']})"
            )
        if ollama_ok:
            logger.info(f"🦙 Dernier repli local vérifié prêt : {state['ollama_model']} sur {ollama_base}")
        elif eff_managed is not None and _is_loopback_url(ollama_base) and _find_ollama_binary():
            logger.info(
                f"ℹ️ Repli local Ollama en veille : démarrage automatique à la demande sur {ollama_base} ({state['ollama_model']})."
            )
        else:
            logger.warning(f"⚠️ Ollama local non prêt ({ollama_diag}) : le dernier repli échouera si cloud + 1min.ai s'épuisent.")

        async def llm_auto(prompt, system_prompt=None, history_messages=[], **kwargs):
            if client is not None and not state["cloud_exhausted"] and not state["prefer_local_doc"]:
                res, used_model = await _call_gemini_cascade(
                    client,
                    state,
                    prompt,
                    system_prompt=system_prompt,
                    history_messages=history_messages,
                    **kwargs,
                )
                if res:
                    if used_model and state.get("last_logged_model") != used_model:
                        state["last_logged_model"] = used_model
                        logger.info(f"💎 Moteur d'indexation actif : Gemini ({used_model})")
                    return res
                if state["cloud_exhausted"] and not state["switched_logged"]:
                    state["switched_logged"] = True
                    if not state.get("oneminai_exhausted", True):
                        logger.warning(
                            f"🔄 Cascade Gemini épuisée -> bascule sur le palier 2 : 1min.ai gratuit "
                            f"({state['oneminai_model']})."
                        )
                    else:
                        logger.warning(
                            f"🔄 Cascade Gemini épuisée -> bascule automatique sur Ollama local "
                            f"({state['ollama_model']}) pour terminer l'indexation."
                        )

            if not state.get("oneminai_exhausted", True) and not state["prefer_local_doc"]:
                messages = _build_openai_messages(prompt, system_prompt, history_messages)
                eff_temp = (
                    QWEN_EXTRACT_SAMPLING["temperature"]
                    if kwargs.get("temperature") is None
                    else kwargs["temperature"]
                )
                eff_max_tokens = kwargs.get("max_tokens") or 8192
                try:
                    om_text, in_tok, out_tok = await call_1minai_stateless_async(
                        state["oneminai_model"],
                        messages,
                        base_url=state["oneminai_url"],
                        api_key=state["oneminai_key"],
                        temperature=eff_temp,
                        max_tokens=eff_max_tokens,
                        timeout_s=120.0,
                        post_json_fn=_post_json_aiohttp,
                        on_param_adapted=lambda desc: logger.info(
                            f"⚙️ Adaptation parametre 1min.ai ({state['oneminai_model']}) : {desc} -> nouvel essai"
                        ),
                    )
                    state["oneminai_ok"] += 1
                    state["oneminai_consecutive_err"] = 0
                    state["oneminai_prompt_tokens"] += in_tok
                    state["oneminai_completion_tokens"] += out_tok
                    om_tag = f"1minai:{state['oneminai_model']}"
                    if state.get("last_logged_model") != om_tag:
                        state["last_logged_model"] = om_tag
                        logger.info(f"🪙 Moteur d'indexation actif : 1min.ai ({state['oneminai_model']})")
                    return om_text
                except Exception as om_err:
                    state["oneminai_err"] += 1
                    state["oneminai_consecutive_err"] += 1
                    if is_1minai_permanent_or_quota_error(str(om_err)) or state["oneminai_consecutive_err"] >= 2:
                        state["oneminai_exhausted"] = True
                        if not state.get("oneminai_switched_logged"):
                            state["oneminai_switched_logged"] = True
                            logger.warning(
                                f"🔄 Palier 2 1min.ai ({state['oneminai_model']}) indisponible/épuisé ({str(om_err)[:90]}) "
                                f"-> bascule automatique sur dernier repli Ollama ({state['ollama_model']})."
                            )
                    else:
                        logger.warning(
                            f"⚠️ Erreur transitoire 1min.ai ({state['oneminai_model']}) : {str(om_err)[:90]} "
                            f"-> repli chunk vers Ollama ({state['ollama_model']})."
                        )

            try:
                res = await ollama_fn(prompt, system_prompt=system_prompt, history_messages=history_messages, **kwargs)
                state["ollama_ok"] += 1
                ollama_tag = f"ollama:{state['ollama_model']}"
                if state.get("last_logged_model") != ollama_tag:
                    state["last_logged_model"] = ollama_tag
                    logger.info(f"🦙 Moteur d'indexation actif : Ollama ({state['ollama_model']})")
                return res
            except Exception:
                state["ollama_err"] += 1
                raise

        return llm_auto

    elif args.provider == "ollama":
        ollama_base = _get_ollama_base_url()
        target_model = _get_ollama_model(args.model)
        num_ctx = int(os.environ.get("OLLAMA_NUM_CTX", "16384"))
        logger.info(
            f"🦙 Mode OLLAMA : {target_model} sur {ollama_base} "
            f"[think=False, num_ctx={num_ctx}, num_predict=8192, "
            f"top_p={QWEN_EXTRACT_SAMPLING['top_p']}, presence_penalty={QWEN_EXTRACT_SAMPLING['presence_penalty']}, lang=French]"
        )
        return _build_ollama_llm_func(args.model, managed_ollama=managed_ollama)

    elif args.provider == "1minai":
        from rag_runtime import resolve_1minai_config

        base_url, default_model, env_key = resolve_1minai_config()
        target_model = args.model or default_model
        eff_key = (args.api_key or env_key).strip()
        if not eff_key:
            raise ValueError("ONEMINAI_API_KEY manquante dans .env (ou passez --api-key).")

        oneminai_stat_key = f"1minai:{target_model}"
        stats[oneminai_stat_key] = {
            "success": 0,
            "failures": 0,
            "locked_until": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
        }
        temp_desc = (
            "omit (contrainte modele)"
            if is_1minai_temperature_omitted(target_model)
            else str(QWEN_EXTRACT_SAMPLING["temperature"])
        )
        logger.info(
            f"🪙 Mode 1MIN.AI (stateless OpenAI-compat) : {target_model} sur {base_url} "
            f"[temperature={temp_desc}, max_tokens=8192]"
        )

        async def llm_1minai(prompt, system_prompt=None, history_messages=[], **kwargs):
            messages = _build_openai_messages(prompt, system_prompt, history_messages)
            eff_temp = (
                QWEN_EXTRACT_SAMPLING["temperature"]
                if kwargs.get("temperature") is None
                else kwargs["temperature"]
            )
            eff_max_tokens = kwargs.get("max_tokens") or 8192
            try:
                content, in_tok, out_tok = await call_1minai_stateless_async(
                    target_model,
                    messages,
                    base_url=base_url,
                    api_key=eff_key,
                    temperature=eff_temp,
                    max_tokens=eff_max_tokens,
                    timeout_s=120.0,
                    post_json_fn=_post_json_aiohttp,
                    on_param_adapted=lambda change_desc: logger.info(
                        f"⚙️ Adaptation parametre 1min.ai ({target_model}) : {change_desc} -> nouvel essai"
                    ),
                )
                stats[oneminai_stat_key]["success"] += 1
                stats[oneminai_stat_key]["prompt_tokens"] += in_tok
                stats[oneminai_stat_key]["completion_tokens"] += out_tok
                return content
            except Exception:
                stats[oneminai_stat_key]["failures"] += 1
                raise

        return llm_1minai

    elif args.provider == "openrouter":
        target_model = args.model or "tencent/hy3-preview:free"
        logger.info(f"🌐 Mode OPENROUTER : Modèle unique {target_model}")

        async def llm_openrouter(prompt, system_prompt=None, history_messages=[], **kwargs):
            return await _call_openrouter_chat(
                target_model,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
            )

        return llm_openrouter

    elif args.provider == "gemini":
        timeout_s = _get_gemini_timeout_s()
        client = _create_genai_client(api_key, timeout_s=timeout_s)
        models_cascade = build_gemini_cascade("index", args.model)
        target_model = models_cascade[0]
        th_level_str = getattr(args, "thinking_level", "low").lower()
        thinking_budget = GEMINI_THINKING_BUDGETS.get(th_level_str, 100)
        logger.info(
            f"💎 Mode GEMINI : Cascade {target_model} ({len(models_cascade)} modèles Free Tier) "
            f"[Budget raisonnement: {thinking_budget} tokens ({th_level_str}) | timeout={timeout_s:.0f}s]"
        )

        exhausted_models = set()
        no_thinking_models = set()
        last_logged = [None]

        async def call_openrouter_fallback(model_name, p, sp, hist):
            try:
                return await _call_openrouter_chat(
                    model_name, p, system_prompt=sp, history_messages=hist, timeout_s=25
                )
            except Exception:
                return None

        async def llm_gemini(prompt, system_prompt=None, history_messages=[], **kwargs):
            contents_payload, effective_system = _build_gemini_contents(
                prompt, history_messages=history_messages, system_prompt=system_prompt
            )

            for current_model in models_cascade:
                if current_model in exhausted_models:
                    continue
                use_thinking = current_model not in no_thinking_models
                try:
                    cfg_kwargs = dict(
                        system_instruction=effective_system,
                        max_output_tokens=kwargs.get("max_tokens", 8192),
                        temperature=kwargs.get("temperature", 0.1),
                    )
                    if use_thinking:
                        cfg_kwargs["thinking_config"] = genai_types.ThinkingConfig(thinking_budget=thinking_budget)
                    cfg = genai_types.GenerateContentConfig(**cfg_kwargs)
                    text = await _generate_gemini_text_async(
                        client,
                        current_model,
                        contents_payload,
                        cfg,
                        timeout_s=timeout_s,
                    )
                    if text.strip():
                        if current_model in stats:
                            stats[current_model]["success"] += 1
                        else:
                            stats[current_model] = {"success": 1, "failures": 0, "locked_until": 0}
                        if last_logged[0] != current_model:
                            last_logged[0] = current_model
                            logger.info(f"💎 Moteur d'indexation actif : Gemini ({current_model})")
                        await asyncio.sleep(2.5)  # Respect du quota RPM
                        return text
                except Exception as e:
                    err_s = _format_gemini_error(e)
                    if use_thinking and "invalid_argument" in err_s.lower() and "deadline" not in err_s.lower():
                        no_thinking_models.add(current_model)
                        try:
                            cfg_retry = genai_types.GenerateContentConfig(
                                system_instruction=effective_system,
                                max_output_tokens=kwargs.get("max_tokens", 8192),
                                temperature=kwargs.get("temperature", 0.1),
                            )
                            text_retry = await _generate_gemini_text_async(
                                client,
                                current_model,
                                contents_payload,
                                cfg_retry,
                                timeout_s=timeout_s,
                            )
                            if text_retry.strip():
                                if current_model in stats:
                                    stats[current_model]["success"] += 1
                                else:
                                    stats[current_model] = {"success": 1, "failures": 0, "locked_until": 0}
                                if last_logged[0] != current_model:
                                    last_logged[0] = current_model
                                    logger.info(f"💎 Moteur d'indexation actif : Gemini ({current_model})")
                                await asyncio.sleep(2.5)
                                return text_retry
                        except Exception as retry_err:
                            err_s = _format_gemini_error(retry_err)

                    kind = _classify_gemini_error(err_s)
                    if current_model in stats:
                        stats[current_model]["failures"] += 1
                    else:
                        stats[current_model] = {"success": 0, "failures": 1, "locked_until": 0}
                    if any(k in err_s.lower() for k in ("timeout", "timed out", "504", "deadline_exceeded")):
                        logger.warning(f"⚠️ Timeout Gemini ({current_model}: {err_s[:80]}). Passage au modèle suivant...")
                        continue
                    elif kind in ("auth", "permanent", "rate_limit") or any(k in err_s for k in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE")) or "quota" in err_s.lower() or "high demand" in err_s.lower():
                        logger.warning(f"⚠️ Modèle {current_model} saturé ou indisponible ({err_s[:70]}). Verrouillé pour cette session, bascule immédiate sur la cascade.")
                        exhausted_models.add(current_model)
                        continue
                    else:
                        logger.warning(f"⚠️ Erreur LLM ({current_model}): {err_s[:80]}. Nouvelle tentative...")
                        await asyncio.sleep(2)
                        continue

            # Repli de secours sur OpenRouter gratuit si tous les modèles Gemini gratuits sont saturés
            for or_model in ["nvidia/nemotron-3-super-120b-a12b:free", "meta-llama/llama-3.3-70b-instruct:free"]:
                res = await call_openrouter_fallback(or_model, prompt, system_prompt, history_messages)
                if res:
                    if or_model in stats:
                        stats[or_model]["success"] += 1
                    else:
                        stats[or_model] = {"success": 1, "failures": 0, "locked_until": 0}
                    logger.info(f"🟢 Repli OpenRouter ({or_model}) réussi.")
                    await asyncio.sleep(2.0)
                    return res

            logger.error("❌ Tous les modèles Gemini et OpenRouter sont temporairement saturés. Pause de 15s...")
            await asyncio.sleep(15)
            return await llm_gemini(prompt, system_prompt=system_prompt, history_messages=history_messages, **kwargs)

        return llm_gemini

    elif args.provider == "online":
        timeout_s = _get_gemini_timeout_s()
        logger.info(f"🚀 Round-Robin Online Parallélisé ({len(MODELS_ROTATION)} modèles | timeout={timeout_s:.0f}s)")
        client = _create_genai_client(api_key, timeout_s=timeout_s)

        async def llm_online_round_robin(prompt, system_prompt=None, history_messages=[], **kwargs):
            contents_payload, effective_system = _build_gemini_contents(
                prompt, history_messages=history_messages, system_prompt=system_prompt
            )

            while True:
                unlocked_model_found = False
                now = time.time()

                for _ in range(len(MODELS_ROTATION)):
                    model_cfg = next(model_cycle)
                    model_name = model_cfg["name"]
                    model_type = model_cfg["type"]
                    s = stats[model_name]
                    log_id = model_name.split('/')[-1]

                    if now < s["locked_until"]:
                        continue

                    unlocked_model_found = True
                    try:
                        if model_type == "gemini":
                            gem_cfg = genai_types.GenerateContentConfig(
                                system_instruction=effective_system,
                                max_output_tokens=kwargs.get("max_tokens", 4096),
                                temperature=kwargs.get("temperature", 0.1)
                            )
                            result_text = await _generate_gemini_text_async(
                                client,
                                model_name,
                                contents_payload,
                                gem_cfg,
                                timeout_s=timeout_s,
                            )
                            if not result_text.strip():
                                raise RuntimeError("Réponse Gemini vide")

                        elif model_type == "openrouter":
                            # Appel HTTP pur pour OpenRouter (0 log parasite de LightRAG)
                            result_text = await _call_openrouter_chat(
                                model_name,
                                prompt,
                                system_prompt=system_prompt,
                                history_messages=history_messages,
                            )
     
                        s["success"] += 1
                        s["failures"] = 0  # Réinitialisation des erreurs sur un succès
                        logger.info(f"🔵 [{log_id}] OK:{s['success']} -> ✅ OK")
                        await asyncio.sleep(2.5)  # Espace de 2.5s pour respecter ~15-20 RPM
                        return result_text
                    
                    except Exception as e:
                        err_msg = _format_gemini_error(e)
                        s["failures"] += 1
                        # Pénalité courte adaptée :
                        # Si 429 temporaire (rate limit par minute), pause courte de 20s suffisant pour libérer la minute glissante.
                        # Sinon 15s par défaut.
                        penalty = 20 if "429" in err_msg else 15
                        s["locked_until"] = now + penalty
                        
                        logger.warning(f"🔵 [{log_id}] OK:{s['success']} ERR:{s['failures']} -> ⚠️ PAUSE ({penalty}s) | Rate-limit temporaire")
                        now = time.time()
                        continue
                
                if not unlocked_model_found:
                    now = time.time()
                    remaining_times = [s["locked_until"] - now for m in MODELS_ROTATION if s["locked_until"] > now]
                    sleep_time = min(remaining_times) if remaining_times else 10
                    sleep_time = max(5.0, min(30.0, sleep_time))
                    
                    logger.warning(f"🚨 TOUS LES MODELES ONLINE SONT EN PAUSE. Attente de {sleep_time:.1f}s...")
                    await asyncio.sleep(sleep_time)
        
        return llm_online_round_robin

# ─── Utilitaires ─────────────────────────────────────────────────────────────

def collect_files() -> list[Path]:
    return collect_docs_files(DOCS_ROOT)

def load_index_log() -> dict:
    if INDEX_LOG.exists():
        with open(INDEX_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_index_log(log_idx: dict):
    DB_PATH.mkdir(parents=True, exist_ok=True)
    with open(INDEX_LOG, "w", encoding="utf-8") as f:
        json.dump(log_idx, f, indent=2, ensure_ascii=False)

def compute_doc_id(content: str) -> str:
    """Calcule l'identifiant MD5 canonique compatible avec LightRAG (contenu nettoyé)."""
    return "doc-" + hashlib.md5(content.strip().encode("utf-8"), usedforsecurity=False).hexdigest()


def _extract_rel_path(content: str) -> str | None:
    """Extrait le chemin relatif inscrit dans l'en-tête injecté par prepare_document."""
    return extract_rel_path(content)


def _rel_path_from_doc_entry(doc_id: str, d_data: dict, full_docs_map: dict) -> str | None:
    """Résout le chemin relatif (relatif à DOCS_ROOT) d'un document LightRAG sans ambiguïté d'homonyme."""
    fd_entry = full_docs_map.get(doc_id)
    if isinstance(fd_entry, dict):
        rel = _extract_rel_path(fd_entry.get("content", ""))
        if rel:
            return rel
    fp = d_data.get("file_path", "") or ""
    if "/" in fp:
        try:
            p = Path(fp)
            if p.is_absolute():
                return str(p.resolve().relative_to(DOCS_ROOT.resolve()))
            return str(Path(fp))
        except Exception:
            return fp
    return None


def _relative_doc_path(path: Path, docs_root: Path | None = None) -> str:
    """Retourne le chemin relatif à DOCS_ROOT, ou le chemin résolu s'il est hors dépôt."""
    root = DOCS_ROOT if docs_root is None else docs_root
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def _resolve_cli_files(
    raw_files: list[str], docs_root: Path | None = None
) -> tuple[list[Path], list[str]]:
    """Résout les chemins --files (absolu, ~, CWD ou relatif à DOCS_ROOT) sans doublons."""
    root = DOCS_ROOT if docs_root is None else docs_root
    resolved: list[Path] = []
    missing: list[str] = []
    seen: set[Path] = set()
    for raw_f in raw_files:
        cand_input = Path(raw_f).expanduser()
        candidates = (
            [cand_input]
            if cand_input.is_absolute()
            else [cand_input, root / cand_input]
        )
        match = next((c.resolve() for c in candidates if c.is_file()), None)
        if match is None:
            missing.append(raw_f)
            continue
        if match not in seen:
            seen.add(match)
            resolved.append(match)
    return resolved, missing


def _is_orphan_entry(
    d_id: str,
    d_data: dict,
    rel: str | None,
    active_rel_set: set[str],
    all_files_str: set[str],
    active_basenames: set[str],
    active_flat_keys: set[str] | None = None,
) -> bool:
    """Détermine si une entrée doc_status correspond à un fichier archivé ou supprimé du disque."""
    if d_id.startswith("dup-"):
        return False
    if rel is not None:
        return rel not in active_rel_set
    fp = (d_data.get("file_path", "") or "").strip()
    if not fp or fp == "unknown_source":
        return False
    if "/" in fp:
        cand = str(Path(fp).resolve()) if Path(fp).is_absolute() else str((DOCS_ROOT / fp).resolve())
        return cand not in all_files_str
    base = os.path.basename(fp)
    if active_flat_keys and (fp in active_flat_keys or base in active_flat_keys):
        return False
    return base not in active_basenames


def _load_disk_state(
    all_files_str: set[str], active_rel_set: set[str], active_basenames: set[str]
) -> tuple[set[str], set[str], set[str], list[str]]:
    """Lit les stores JSON locaux en lecture seule pour détecter le statut réel et les orphelins."""
    processed_ids, processed_rels, processed_basenames = set(), set(), set()
    orphan_ids: list[str] = []
    active_flat_keys = build_active_source_aliases(active_rel_set)
    status_file = DB_PATH / "kv_store_doc_status.json"
    full_docs_file = DB_PATH / "kv_store_full_docs.json"
    if not status_file.exists():
        return processed_ids, processed_rels, processed_basenames, orphan_ids

    try:
        ds = json.loads(status_file.read_text(encoding="utf-8"))
        fd = json.loads(full_docs_file.read_text(encoding="utf-8")) if full_docs_file.exists() else {}
        for d_id, d_data in ds.items():
            rel = _rel_path_from_doc_entry(d_id, d_data, fd)
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
                active_flat_keys=active_flat_keys,
            ):
                orphan_ids.append(d_id)
    except Exception as err:
        logger.debug(f"Lecture état disque doc_status/full_docs ignorée: {err}")
    return processed_ids, processed_rels, processed_basenames, orphan_ids


async def _snapshot_doc_status_and_full_docs(rag: LightRAG) -> tuple[dict, dict]:
    """Capture l'état actif de doc_status et résout les contenus full_docs associés."""
    async with rag.doc_status._storage_lock:
        ds_snapshot = dict(rag.doc_status._data)
    if not ds_snapshot or not rag.full_docs:
        return ds_snapshot, {}
    try:
        rows = await rag.full_docs.get_by_ids(list(ds_snapshot.keys()))
        fd_map = {
            d_id: row
            for d_id, row in zip(ds_snapshot.keys(), rows)
            if isinstance(row, dict)
        }
        return ds_snapshot, fd_map
    except Exception as err:
        logger.debug(f"Impossible de charger full_docs via get_by_ids: {err}")
        return ds_snapshot, {}


def _find_matching_doc_ids(
    ds_snapshot: dict,
    resolved_rels: dict[str, str | None],
    target_abs: str,
    rel_target: str | None,
    target_basename: str,
    allow_basename_match: bool,
    extra_doc_id: str | None = None,
    target_source_key: str | None = None,
) -> list[str]:
    """Identifie tous les doc_id dans doc_status correspondant exactement à un fichier cible."""
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


def _supports_delete_llm_cache(delete_fn) -> bool:
    """Indique si adelete_by_doc_id accepte le parametre delete_llm_cache."""
    try:
        params = inspect.signature(delete_fn).parameters.values()
    except (TypeError, ValueError):
        return False
    return any(
        p.name == "delete_llm_cache" or p.kind == inspect.Parameter.VAR_KEYWORD
        for p in params
    )


async def _purge_doc_ids(
    rag: LightRAG,
    doc_ids: list[str],
    label: str,
    *,
    delete_llm_cache: bool = True,
) -> int:
    """Supprime proprement doc_ids des chunks, vecteurs, cache LLM et graphe LightRAG."""
    purged = 0
    seen: set[str] = set()
    delete_fn = getattr(rag, "adelete_by_doc_id", None)
    pass_cache_flag = delete_fn is not None and _supports_delete_llm_cache(delete_fn)
    for d_id in doc_ids:
        if not d_id or d_id in seen:
            continue
        seen.add(d_id)
        if not d_id.startswith("dup-"):
            try:
                if pass_cache_flag:
                    res = await delete_fn(d_id, delete_llm_cache=delete_llm_cache)
                else:
                    res = await delete_fn(d_id)
                status = getattr(res, "status", "")
                if status == "success":
                    purged += 1
                    continue
                if status == "not_found":
                    continue
                logger.warning(
                    f"⚠️ Purge graphe incomplète pour {label} ({d_id}) [{status}]: "
                    f"{getattr(res, 'message', '')} -> repli doc_status."
                )
            except Exception as err:
                logger.warning(f"⚠️ Échec adelete_by_doc_id pour {label} ({d_id}): {err} -> repli doc_status.")
        try:
            await rag.doc_status.delete([d_id])
            purged += 1
        except Exception as err:
            logger.warning(f"Impossible de supprimer {d_id} de doc_status: {err}")
    return purged

VLM_MODELS = list(GEMINI_VLM_CASCADE)

def _get_ollama_base_url() -> str:
    """Retourne l'URL racine d'Ollama (sans /v1 final)."""
    raw = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip().rstrip("/")
    return raw[:-3] if raw.endswith("/v1") else raw


def _get_ollama_model(explicit_model: str | None = None) -> str:
    """Résout le modèle Ollama actif (argument CLI, variable d'env ou défaut qwen3.8:27b-mlx)."""
    return explicit_model or os.environ.get("OLLAMA_MODEL", "qwen3.8:27b-mlx")


_VLM_TECHNICAL_PROMPT = (
    "Tu es un expert en ingénierie mécanique, robotique et électronique pour le projet D-Bot.\n"
    "Analyse cette image technique en détail. Décris avec précision :\n"
    "1. Les composants mécaniques, électroniques, moteurs, roulements, fixations ou assemblages visibles.\n"
    "2. Toutes les cotations, dimensions, références, marquages ou annotations textuelles (ex: AXK 5578, M4x70, etc.).\n"
    "3. La géométrie, le montage et la fonction technique de ce sous-ensemble.\n"
    "Fournis une description technique exhaustive et structurée."
)


def _encode_image_for_ollama(image_path: Path, max_dim: int = 1600) -> str:
    """Charge et redimensionne l'image si besoin puis l'encode en base64 PNG pour Ollama."""
    with Image.open(image_path) as img:
        if max(img.size) > max_dim:
            img = img.copy()
            img.thumbnail((max_dim, max_dim))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("ascii")


def analyze_image_with_vlm_ollama(
    image_path: Path,
    model_name: str | None = None,
    managed_ollama: ManagedOllamaServer | None = None,
) -> str:
    """Analyse une image technique localement via l'endpoint Ollama /api/chat (think=False)."""
    if managed_ollama is not None:
        ok, diag = _ensure_ollama_available(managed_ollama, require_model=True)
        if not ok:
            raise RuntimeError(diag)
    ollama_base = _get_ollama_base_url()
    target_model = _get_ollama_model(model_name)
    img_b64 = _encode_image_for_ollama(image_path)
    payload = {
        "model": target_model,
        "messages": [
            {
                "role": "user",
                "content": _VLM_TECHNICAL_PROMPT,
                "images": [img_b64],
            }
        ],
        "stream": False,
        "think": False,
        "keep_alive": os.environ.get("OLLAMA_KEEP_ALIVE", "10m"),
        "options": {
            "num_ctx": int(os.environ.get("OLLAMA_VLM_NUM_CTX", "8192")),
            "temperature": QWEN_EXTRACT_SAMPLING["temperature"],
            "top_p": QWEN_EXTRACT_SAMPLING["top_p"],
            "top_k": QWEN_EXTRACT_SAMPLING["top_k"],
            "min_p": QWEN_EXTRACT_SAMPLING["min_p"],
            "repeat_penalty": QWEN_EXTRACT_SAMPLING["repeat_penalty"],
            "presence_penalty": QWEN_EXTRACT_SAMPLING["presence_penalty"],
            "num_predict": 4096,
        },
    }
    try:
        resp = requests.post(f"{ollama_base}/api/chat", json=payload, timeout=600)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as err:
        raise RuntimeError(f"Ollama VLM injoignable sur {ollama_base} ({type(err).__name__}: {err})") from err
    content = (data.get("message") or {}).get("content", "")
    if not content:
        raise RuntimeError(f"Réponse VLM Ollama vide pour {image_path.name}")
    logger.info(f"   🦙 VLM Ollama réussi ({target_model}) pour {image_path.name}")
    return content


def analyze_image_with_vlm(client: genai.Client, image_path: Path, auto_state: dict | None = None) -> str:
    if not client:
        raise RuntimeError("API Client VLM non disponible")

    img = Image.open(image_path)
    prompt = _VLM_TECHNICAL_PROMPT

    last_error = None
    for model_name in VLM_MODELS:
        try:
            cfg = genai_types.GenerateContentConfig(
                thinking_config=genai_types.ThinkingConfig(thinking_budget=100)
            )
            response = client.models.generate_content(
                model=model_name,
                contents=[img, prompt],
                config=cfg
            )
            if response and response.text:
                logger.info(f"   ✨ VLM Gemini réussi ({model_name}) pour {image_path.name}")
                if auto_state is not None:
                    vlm_counts = auto_state.setdefault("vlm_ok", {})
                    vlm_counts[f"gemini:{model_name}"] = vlm_counts.get(f"gemini:{model_name}", 0) + 1
                return response.text
        except Exception as e:
            last_error = str(e)
            if "invalid_argument" in last_error.lower() and "deadline" not in last_error.lower():
                try:
                    response_retry = client.models.generate_content(
                        model=model_name,
                        contents=[img, prompt],
                    )
                    if response_retry and response_retry.text:
                        logger.info(f"   ✨ VLM Gemini réussi ({model_name}, sans thinking_config) pour {image_path.name}")
                        if auto_state is not None:
                            vlm_counts = auto_state.setdefault("vlm_ok", {})
                            vlm_counts[f"gemini:{model_name}"] = vlm_counts.get(f"gemini:{model_name}", 0) + 1
                        return response_retry.text
                except Exception as retry_err:
                    last_error = str(retry_err)
            if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                logger.warning(f"⚠️ Quota 429 sur {model_name} pour {image_path.name}. Basculement sur le modèle VLM suivant...")
                time.sleep(2)
                continue
            else:
                logger.warning(f"⚠️ Erreur sur {model_name}: {last_error}")
                continue

    raise RuntimeError(f"Échec de l'analyse VLM sur {image_path.name} après tous les modèles (Dernière erreur: {last_error})")

def extract_pdf_text(path: Path) -> str:
    txt = extract_pdf_text_cached(path, db_path=DB_PATH)
    if txt:
        logger.info(f"   ✨ Extraction PDF réussie/cachée pour {path.name} ({len(txt)} caractères)")
    return txt


_SVG_SKIP_TAGS = frozenset({"defs", "style", "script", "metadata"})
_SVG_INLINE_TEXT_TAGS = frozenset({"tspan", "a", "textpath"})


def _svg_local_tag(tag: object) -> str:
    """Retourne le nom local en minuscules d'une balise SVG (sans espace de noms)."""
    return tag.split("}", 1)[-1].lower() if isinstance(tag, str) else ""


def _extract_svg_text_node(el) -> str:
    """Extrait le texte normalisé d'un noeud <text> SVG et de ses enfants <tspan>."""
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


def _collect_svg_blocks(node, depth: int = 0) -> list[str]:
    """Parcourt l'arbre XML SVG et regroupe les textes exploitables par panneau <g>."""
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
    """Extrait le contenu textuel structuré (<title>, <desc>, <text>) d'un fichier SVG via defusedxml."""
    try:
        raw_xml = path.read_text(encoding="utf-8")
        root = DefusedET.fromstring(raw_xml)
    except Exception as e:
        logger.warning(f"⚠️ Erreur de lecture XML SVG {path.name}: {e}")
        return ""
    return "\n\n".join(_collect_svg_blocks(root))


def _auto_sort_key(path: Path) -> tuple[int, int, str]:
    """Trie les gros documents textuels d'abord, puis images, puis petits SVG."""
    ext = path.suffix.lower()
    if ext in SVG_EXTS:
        tier = 0
    elif ext in IMAGE_EXTS:
        tier = -1
    else:
        tier = -2
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    return (tier, -size, str(path))


def prepare_document(
    path: Path,
    genai_client: genai.Client = None,
    provider: str = "auto",
    model: str | None = None,
    auto_state: dict | None = None,
    managed_ollama: ManagedOllamaServer | None = None,
) -> str:
    relative = _relative_doc_path(path)
    ext = path.suffix.lower()
    
    if ext in IMAGE_EXTS:
        ollama_model = auto_state["ollama_model"] if auto_state else model
        eff_managed = (auto_state.get("managed_ollama") if auto_state else None) or managed_ollama
        use_ollama_vlm = provider == "ollama" or (
            provider == "auto"
            and (
                not genai_client
                or (auto_state is not None and (auto_state["cloud_exhausted"] or auto_state["vlm_gemini_exhausted"]))
            )
        )
        if use_ollama_vlm:
            logger.info(f"🦙 Analyse VLM Ollama en cours pour l'image: {path.name}...")
            try:
                vlm_desc = analyze_image_with_vlm_ollama(path, ollama_model, managed_ollama=eff_managed)
                if auto_state is not None:
                    eff_vlm_model = _get_ollama_model(ollama_model)
                    vlm_counts = auto_state.setdefault("vlm_ok", {})
                    vlm_counts[f"ollama:{eff_vlm_model}"] = vlm_counts.get(f"ollama:{eff_vlm_model}", 0) + 1
                header = f"---\nFichier: {relative}\nType: Image VLM (Ollama)\nProjet: D-Bot\n---\n\n"
                return header + f"# Analyse Visuelle et Spécifications Techniques : {path.name}\n\n" + vlm_desc
            except Exception as e:
                logger.warning(f"⚠️ Ignoré pour cette session (Ollama VLM): {e}")
                return ""
        if provider == "1minai" and not genai_client:
            logger.info(f"ℹ️ Image ignorée en --provider 1minai sans GEMINI_API_KEY VLM : {path.name}")
            return ""
        logger.info(f"📸 Analyse VLM en cours pour l'image: {path.name}...")
        try:
            vlm_desc = analyze_image_with_vlm(genai_client, path, auto_state=auto_state)
            header = f"---\nFichier: {relative}\nType: Image VLM\nProjet: D-Bot\n---\n\n"
            return header + f"# Analyse Visuelle et Spécifications Techniques : {path.name}\n\n" + vlm_desc
        except Exception as e:
            if provider == "auto":
                auto_state["vlm_gemini_exhausted"] = True
                logger.warning(f"⚠️ VLM Gemini indisponible pour {path.name} ({e}). Bascule sur VLM Ollama local...")
                try:
                    vlm_desc = analyze_image_with_vlm_ollama(path, ollama_model, managed_ollama=eff_managed)
                    eff_vlm_model = _get_ollama_model(ollama_model)
                    vlm_counts = auto_state.setdefault("vlm_ok", {})
                    vlm_counts[f"ollama:{eff_vlm_model}"] = vlm_counts.get(f"ollama:{eff_vlm_model}", 0) + 1
                    header = f"---\nFichier: {relative}\nType: Image VLM (Ollama repli)\nProjet: D-Bot\n---\n\n"
                    return header + f"# Analyse Visuelle et Spécifications Techniques : {path.name}\n\n" + vlm_desc
                except Exception as err_ol:
                    logger.warning(f"⚠️ Ignoré pour cette session (VLM Gemini + Ollama): {err_ol}")
                    return ""
            logger.warning(f"⚠️ Ignoré pour cette session: {e}")
            return ""

    elif ext in PDF_EXTS:
        logger.info(f"📄 Extraction du texte PDF: {path.name}...")
        pdf_text = extract_pdf_text(path)
        header = f"---\nFichier: {relative}\nType: Document PDF\nProjet: D-Bot\n---\n\n"
        return header + f"# Document PDF : {path.name}\n\n" + pdf_text

    elif ext in SVG_EXTS:
        logger.info(f"📐 Extraction XML SVG: {path.name}...")
        svg_text = extract_svg_text(path)
        if not svg_text.strip():
            logger.warning(f"⚠️ Aucun texte exploitable dans le SVG {path.name}, ignoré.")
            return ""
        header = f"---\nFichier: {relative}\nType: Schéma Vectoriel SVG (Texte XML)\nProjet: D-Bot\n---\n\n"
        return header + f"# Schéma Technique SVG : {path.name}\n\n" + svg_text

    else:
        try:
            content = path.read_text(encoding="utf-8")
            header = f"---\nFichier: {relative}\nProjet: D-Bot\n---\n\n"
            return header + content
        except Exception as e:
            logger.warning(f"⚠️ Erreur de lecture {path.name}: {e}")
            return ""

async def _call_gemma4_summary_async(prompt: str, system_prompt: str | None = None) -> str | None:
    """Genere un resume de fusion LightRAG via Gemma 4 (rapide, prose pure sans delimiteurs)."""
    ollama_base = _get_ollama_base_url()
    qa_model = os.environ.get("OLLAMA_QA_MODEL", DEFAULT_OLLAMA_QA_MODEL).strip() or DEFAULT_OLLAMA_QA_MODEL
    ok, _ = _check_ollama_ready(ollama_base, qa_model)
    if not ok:
        return None
    payload = {
        "model": qa_model,
        "messages": _build_openai_messages(prompt, system_prompt, None),
        "stream": False,
        "think": False,
        "keep_alive": os.environ.get("OLLAMA_KEEP_ALIVE", "10m"),
        "options": {
            "num_ctx": 8192,
            "temperature": 0.2,
            "top_p": 0.80,
            "top_k": 20,
            "num_predict": 1500,
        },
    }
    try:
        data = await _post_json_aiohttp(
            f"{ollama_base}/api/chat",
            payload,
            timeout_s=120,
            service_name="Ollama-Summary",
            include_error_body=False,
        )
        content = ((data.get("message") or {}).get("content") or "").strip()
        return content or None
    except Exception:
        return None


_PROGRESS_FILENAME = ".indexing_progress.json"


def _write_progress_state(db_dir: Path, state: dict) -> None:
    """Ecrit .indexing_progress.json de facon atomique pour le cockpit web."""
    target = Path(db_dir) / _PROGRESS_FILENAME
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=".progress.", dir=str(target.parent))
        tmp_path = Path(tmp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(state, fh, ensure_ascii=False)
            tmp_path.replace(target)
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise
    except OSError:
        pass


def _clear_progress_state(db_dir: Path) -> None:
    target = Path(db_dir) / _PROGRESS_FILENAME
    try:
        if target.exists():
            target.unlink()
    except OSError:
        pass


def _resolve_live_engine_label(args, auto_state: dict | None) -> str:
    if auto_state is not None:
        if auto_state.get("cloud_exhausted"):
            if auto_state.get("oneminai_enabled") and not auto_state.get("oneminai_exhausted", True):
                return f"1min.ai ({auto_state.get('oneminai_model')})"
            return f"Ollama ({auto_state.get('ollama_model')})"
        return str(auto_state.get("last_model") or "Gemini (cascade auto)")
    if getattr(args, "provider", "") == "ollama":
        return f"Ollama ({_get_ollama_model(getattr(args, 'model', None))})"
    return str(getattr(args, "provider", "auto"))


def wrap_llm_with_summary_mode(
    base_llm,
    summary_mode: str,
    summary_stats: dict[str, int] | None = None,
):
    """Enveloppe llm_func pour court-circuiter les syntheses et nettoyer les delimiteurs."""
    eff_mode = (summary_mode or "deterministic").strip().lower()

    async def llm_with_summary_policy(prompt, system_prompt=None, history_messages=[], **kwargs):
        if eff_mode != "llm" and is_entity_summary_prompt(prompt, history_messages):
            if eff_mode == "gemma4":
                gemma_txt = await _call_gemma4_summary_async(prompt, system_prompt)
                if gemma_txt:
                    if summary_stats is not None:
                        summary_stats["gemma4"] = summary_stats.get("gemma4", 0) + 1
                    return gemma_txt
            if summary_stats is not None:
                summary_stats["deterministic"] = summary_stats.get("deterministic", 0) + 1
            return deterministic_merge_descriptions(prompt)
        raw_out = await base_llm(prompt, system_prompt=system_prompt, history_messages=history_messages, **kwargs)
        return sanitize_lightrag_extraction_output(raw_out) if isinstance(raw_out, str) else raw_out

    return llm_with_summary_policy


async def run_indexing(args):
    if getattr(args, "prepare_agent", None) is not None:
        raw_job = None if args.prepare_agent in ("auto", "") else str(args.prepare_agent)
        eff_profile = resolve_effort_profile(getattr(args, "effort_profile", "balanced"))
        chunk_size = int(os.environ.get("CHUNK_SIZE", "1600"))
        chunk_overlap = int(os.environ.get("CHUNK_OVERLAP_SIZE", "150"))
        prep = prepare_agent_bundle(
            docs_root=DOCS_ROOT,
            db_path=DB_PATH,
            files=args.files,
            effort_profile=eff_profile,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            full=bool(args.full),
            section_split=not bool(getattr(args, "no_section_split", False)),
            job_id=raw_job,
        )
        man = prep["manifest"]
        logger.info(
            f"📦 Lot Agent prepare ({prep['job_id']}) [profil={man['effort_profile']}] : "
            f"{len(man['documents'])} doc(s), {len(man['chunks'])} chunk(s), {len(man['images'])} image(s) VLM, "
            f"{len(man['to_delete'])} suppression(s), {len(man['orphan_ids'])} orphelin(s)."
        )
        print(
            json.dumps(
                {
                    "job_id": prep["job_id"],
                    "manifest_path": prep["manifest_path"],
                    "extractions_path": prep["extractions_path"],
                    "effort_profile": man["effort_profile"],
                    "effort_summary": man["effort_summary"],
                    "documents": len(man["documents"]),
                    "chunks": len(man["chunks"]),
                    "images": len(man["images"]),
                    "to_delete": len(man["to_delete"]),
                    "orphan_ids": len(man["orphan_ids"]),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    force_summary_merge = max(8, int(os.environ.get("RAG_FORCE_LLM_SUMMARY_ON_MERGE", "24")))

    if getattr(args, "commit_agent", None):
        chunk_size = int(os.environ.get("CHUNK_SIZE", "1600"))
        chunk_overlap = int(os.environ.get("CHUNK_OVERLAP_SIZE", "150"))

        async def _noop_agent_init_llm(*a, **k):
            raise RuntimeError("ReplayAgentLLM doit intercepter tout appel LLM durant --commit-agent.")

        with IndexingFileLock(DB_PATH):
            rag_commit = LightRAG(
                working_dir=str(DB_PATH),
                llm_model_func=_noop_agent_init_llm,
                embedding_func=embedding_func,
                chunking_func=chunking_markdown_anchored,
                chunk_token_size=chunk_size,
                chunk_overlap_token_size=chunk_overlap,
                force_llm_summary_on_merge=force_summary_merge,
                llm_model_max_async=1,
                default_llm_timeout=600,
                addon_params={"language": "French"},
            )
            await rag_commit.initialize_storages()
            _configure_third_party_loggers()
            res_commit = await commit_agent_bundle(
                rag=rag_commit,
                db_path=DB_PATH,
                job_id_or_path=str(args.commit_agent),
                extractions_path=getattr(args, "extractions", None),
                force_llm_summary_on_merge=force_summary_merge,
            )
            logger.info(
                f"✅ Commit Agent termine ({res_commit['job_id']}) : "
                f"{len(res_commit['committed'])} doc(s) committe(s), {res_commit['chunks_replayed']} chunk(s), "
                f"{res_commit['replaced_count']} remplace(s), {res_commit['deleted_count']} supprime(s)."
            )
            logger.info(f"🧭 Moteur(s) d'indexation utilisés : antigravity/self-agent ({res_commit['effort_profile']})")
            print(json.dumps(res_commit, ensure_ascii=False, indent=2))
            if getattr(args, "mirror_backup", False) or os.environ.get("RAG_AUTO_MIRROR_BACKUP", "").strip().lower() in ("1", "true", "yes"):
                ok_m, msg_m = sync_db_to_backup_mirror(DB_PATH)
                logger.info(f"💾 Miroir sauvegarde : {msg_m}" if ok_m else f"⚠️ Miroir sauvegarde : {msg_m}")
        return

    all_files = collect_files()
    all_files_str = {str(p) for p in all_files}
    active_rel_set = {str(p.relative_to(DOCS_ROOT)) for p in all_files}
    active_name_counts = Counter(p.name for p in all_files)
    active_basenames = set(active_name_counts.keys())
    log_idx = load_index_log() if not args.full else {}

    processed_ids, processed_rels, processed_basenames, pending_orphans = _load_disk_state(
        all_files_str, active_rel_set, active_basenames
    )

    def _entry_docs_processed(entry: dict, rel: str, fname: str) -> bool:
        sec_map = entry.get("sections")
        if isinstance(sec_map, dict) and sec_map:
            return all(
                isinstance(s, dict) and s.get("doc_id") in processed_ids
                for s in sec_map.values()
            )
        cached_id = entry.get("doc_id")
        if cached_id in processed_ids or rel in processed_rels:
            return True
        if active_name_counts.get(fname, 0) == 1 and fname in processed_basenames:
            return True
        return False

    mtime_refreshes: dict[str, float] = {}

    def file_needs_update(p: Path) -> bool:
        entry = log_idx.get(str(p))
        if not isinstance(entry, dict):
            return True
        rel = str(p.relative_to(DOCS_ROOT))
        if not _entry_docs_processed(entry, rel, p.name):
            return True
        cur_mtime = os.path.getmtime(p)
        if entry.get("mtime", 0) >= cur_mtime:
            return False
        ext_low = p.suffix.lower()
        stored_sha = entry.get("content_sha256")
        if stored_sha and ext_low in (".md", ".py", ".txt"):
            try:
                cur_sha = compute_normalized_sha256(p.read_text(encoding="utf-8"), ext=ext_low)
                if cur_sha == stored_sha:
                    mtime_refreshes[str(p)] = cur_mtime
                    return False
            except OSError:
                pass
        return True

    if args.files:
        to_update, missing_files = _resolve_cli_files(args.files)
        for missing_f in missing_files:
            logger.warning(f"⚠️ Fichier introuvable (--files ignoré) : {missing_f}")
        to_delete = []
        check_orphans = False
        if not to_update:
            logger.error("❌ Aucun fichier valide trouvé pour --files.")
            return
    elif args.full:
        to_update = all_files
        to_delete = [path_str for path_str in list(log_idx.keys()) if path_str not in all_files_str]
        check_orphans = bool(pending_orphans)
    else:
        to_update = [p for p in all_files if file_needs_update(p)]
        to_delete = [path_str for path_str in list(log_idx.keys()) if path_str not in all_files_str]
        check_orphans = bool(pending_orphans)

    if not to_update and not to_delete and not check_orphans:
        if mtime_refreshes:
            for p_str, new_mt in mtime_refreshes.items():
                if isinstance(log_idx.get(p_str), dict):
                    log_idx[p_str]["mtime"] = new_mt
            save_index_log(log_idx)
            logger.info(f"✅ Tout est à jour ({len(mtime_refreshes)} mtime(s) normalisés sans changement sémantique).")
        else:
            logger.info("✅ Tout est à jour.")
        return

    indexing_lock = IndexingFileLock(DB_PATH)
    try:
        indexing_lock.acquire()
    except RuntimeError as lock_err:
        logger.warning(f"⏳ {lock_err}")
        return

    managed_ollama: ManagedOllamaServer | None = None
    did_write = False
    run_started_at = time.time()
    try:
        api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
        genai_client = _create_genai_client(api_key)
        auto_state: dict | None = None
        if args.provider == "auto":
            auto_state = _create_auto_state(args, api_key)
            managed_ollama = ManagedOllamaServer(base_url=_get_ollama_base_url(), model=auto_state["ollama_model"])
            auto_state["managed_ollama"] = managed_ollama
            to_update = sorted(to_update, key=_auto_sort_key)
        elif args.provider == "ollama":
            managed_ollama = ManagedOllamaServer(base_url=_get_ollama_base_url(), model=_get_ollama_model(args.model))

        if managed_ollama is not None and (
            args.provider == "ollama"
            or (
                auto_state is not None
                and auto_state["cloud_exhausted"]
                and auto_state.get("oneminai_exhausted", True)
            )
        ):
            ok, diag = _ensure_ollama_available(managed_ollama, require_model=True)
            if not ok:
                logger.error(f"❌ {diag}")
                return
            if auto_state is not None:
                auto_state["ollama_verified"] = True

        base_llm_func = await get_llm_func(args, auto_state=auto_state, managed_ollama=managed_ollama)
        summary_mode = getattr(args, "summary_mode", "deterministic")
        gleaning_mode = str(
            getattr(args, "gleaning_mode", os.environ.get("RAG_GLEANING_MODE", "adaptive")) or "adaptive"
        ).strip().lower()
        summary_stats = {"deterministic": 0, "gemma4": 0}
        llm_func = wrap_llm_with_summary_mode(base_llm_func, summary_mode, summary_stats=summary_stats)

        # Parallélisme & chunking pilotables via variables d'environnement (défauts 1600/150 validés Phase 1-2)
        default_async = 2 if args.provider == "1minai" else (1 if args.provider in ("local", "ollama", "gemini", "auto") else 4)
        max_async = max(1, int(os.environ.get("LLM_MAX_ASYNC", str(default_async))))
        chunk_size = int(os.environ.get("CHUNK_SIZE", "1600"))
        chunk_overlap = int(os.environ.get("CHUNK_OVERLAP_SIZE", "150"))

        rag = LightRAG(
            working_dir=str(DB_PATH),
            llm_model_func=llm_func,
            embedding_func=embedding_func,
            chunking_func=chunking_markdown_anchored,
            chunk_token_size=chunk_size,
            chunk_overlap_token_size=chunk_overlap,
            force_llm_summary_on_merge=force_summary_merge,
            llm_model_max_async=max_async,
            default_llm_timeout=600,
            enable_llm_cache_for_entity_extract=not bool(getattr(args, "no_cache", False)),
            addon_params={"language": "French"},
        )
        await rag.initialize_storages()
        _configure_third_party_loggers()

        ds_snapshot, fd_map = await _snapshot_doc_status_and_full_docs(rag)
        resolved_rels = {
            d_id: _rel_path_from_doc_entry(d_id, d_data, fd_map)
            for d_id, d_data in ds_snapshot.items()
        }
        active_flat_keys = build_active_source_aliases(active_rel_set)

        stale_dup_ids = [d_id for d_id in list(ds_snapshot.keys()) if d_id.startswith("dup-")]
        if stale_dup_ids:
            purged_dups = await _purge_doc_ids(rag, stale_dup_ids, "doc_status(dup-*)")
            for d_id in stale_dup_ids:
                ds_snapshot.pop(d_id, None)
                resolved_rels.pop(d_id, None)
                fd_map.pop(d_id, None)
            logger.info(f"🧹 {purged_dups} entrée(s) dup-* résiduelle(s) nettoyée(s) dans doc_status.")
            if purged_dups:
                did_write = True

        # ── Phase 2A : Suppressions & orphelins ──
        if to_delete:
            logger.info(f"🗑️  Nettoyage intelligent : Suppression de {len(to_delete)} fichier(s) exclu(s)/supprimé(s)...")
            for path_str in to_delete:
                target_path = Path(path_str)
                try:
                    rel_target = str(target_path.relative_to(DOCS_ROOT))
                except ValueError:
                    rel_target = None

                expected_flat = (
                    (rel_target.replace("/", "--") if "/" in rel_target else f"root--{rel_target}")
                    if rel_target
                    else None
                )
                matched_ids = _find_matching_doc_ids(
                    ds_snapshot=ds_snapshot,
                    resolved_rels=resolved_rels,
                    target_abs=path_str,
                    rel_target=rel_target,
                    target_basename=target_path.name,
                    allow_basename_match=(target_path.name not in active_basenames),
                    extra_doc_id=log_idx[path_str].get("doc_id"),
                    target_source_key=expected_flat,
                )
                purged_n = await _purge_doc_ids(rag, matched_ids, target_path.name)
                for mid in matched_ids:
                    ds_snapshot.pop(mid, None)
                    resolved_rels.pop(mid, None)
                    fd_map.pop(mid, None)
                del log_idx[path_str]
                did_write = True
                logger.info(f"   [-] Purgé ({purged_n} entrée(s) RAG) : {target_path.name}")
            save_index_log(log_idx)

        if check_orphans:
            orphan_entries = [
                (d_id, resolved_rels.get(d_id) or d_data.get("file_path", "") or d_id)
                for d_id, d_data in list(ds_snapshot.items())
                if _is_orphan_entry(
                    d_id,
                    d_data,
                    resolved_rels.get(d_id),
                    active_rel_set,
                    all_files_str,
                    active_basenames,
                    active_flat_keys=active_flat_keys,
                )
            ]
            if orphan_entries:
                logger.info(
                    f"🧹 Purge des {len(orphan_entries)} document(s) orphelin(s)/archivé(s) résiduel(s) dans LightRAG..."
                )
                for o_id, o_label in orphan_entries:
                    purged_n = await _purge_doc_ids(rag, [o_id], str(o_label))
                    ds_snapshot.pop(o_id, None)
                    resolved_rels.pop(o_id, None)
                    fd_map.pop(o_id, None)
                    if purged_n:
                        did_write = True
                        logger.info(f"   [-] Orphelin purgé : {o_label} ({o_id})")

        # ── Phase 1 : Preparation (VLM images d'abord pour preserver le KV Prefix Cache, puis textes/sections) ──
        if to_update:
            # Placer les images VLM avant les textes pour regrouper les appels homogenes
            images_first = [p for p in to_update if p.suffix.lower() in IMAGE_EXTS]
            non_images = [p for p in to_update if p.suffix.lower() not in IMAGE_EXTS]
            ordered_update = images_first + non_images
            logger.info(
                f"📂 Préparation de {len(ordered_update)} fichier(s) "
                f"[DB: {DB_PATH.name} | Parallélisme: {max_async} | Chunk: {chunk_size}/{chunk_overlap} | Summary: {summary_mode} | Gleaning: {gleaning_mode}]..."
            )
        else:
            ordered_update = []

        purge_queue: list[tuple[str, str]] = []
        insert_units: list[dict] = []
        section_file_plans: dict[str, dict] = {}
        use_section_split = not bool(getattr(args, "no_section_split", False))

        for i, path in enumerate(ordered_update, 1):
            rel_path = _relative_doc_path(path)
            ext = path.suffix.lower()
            _write_progress_state(
                DB_PATH,
                {
                    "phase": "prepare",
                    "started_at": run_started_at,
                    "updated_at": time.time(),
                    "provider": args.provider,
                    "summary_mode": summary_mode,
                    "gleaning_mode": gleaning_mode,
                    "batch_size": max(1, int(getattr(args, "batch_size", 8))),
                    "active_engine": _resolve_live_engine_label(args, auto_state),
                    "total_files": len(ordered_update),
                    "prepared_files": i,
                    "done_files": 0,
                    "current_file": rel_path,
                    "total_units": len(insert_units),
                    "done_units": 0,
                    "failed_units": 0,
                },
            )

            if ext == ".md" and use_section_split:
                try:
                    raw_md = path.read_text(encoding="utf-8")
                except Exception as read_err:
                    logger.warning(f"⚠️ Erreur de lecture {path.name}: {read_err}")
                    continue
                v_sections = split_markdown_into_virtual_sections(raw_md, rel_path)
                if v_sections is not None:
                    file_norm_sha = compute_normalized_sha256(raw_md, ext=".md")
                    force_sections = bool(args.full or args.files)
                    prev_entry = log_idx.get(str(path)) if not force_sections else {}
                    prev_sections = (
                        prev_entry.get("sections")
                        if isinstance(prev_entry, dict) and isinstance(prev_entry.get("sections"), dict)
                        else {}
                    )
                    target_ids = {s["doc_id"] for s in v_sections}
                    for d_id in list(ds_snapshot.keys()):
                        if resolved_rels.get(d_id) == rel_path and d_id not in target_ids:
                            purge_queue.append((d_id, path.name))
                            ds_snapshot.pop(d_id, None)
                            resolved_rels.pop(d_id, None)
                            fd_map.pop(d_id, None)

                    changed_sections = []
                    for sec in v_sections:
                        prev_sec = prev_sections.get(sec["section_key"])
                        is_unchanged = (
                            not force_sections
                            and sec["doc_id"] in processed_ids
                            and isinstance(prev_sec, dict)
                            and prev_sec.get("sha256") == sec["content_sha256"]
                        )
                        if not is_unchanged:
                            changed_sections.append(sec)

                    section_file_plans[str(path)] = {
                        "mtime": os.path.getmtime(path),
                        "content_sha256": file_norm_sha,
                        "sections": {
                            s["section_key"]: {
                                "doc_id": s["doc_id"],
                                "sha256": s["content_sha256"],
                                "title": s["section_title"],
                            }
                            for s in v_sections
                        },
                        "pending_doc_ids": {s["doc_id"] for s in changed_sections},
                        "failed": False,
                    }
                    logger.info(
                        f"[{i:3d}/{len(ordered_update)}] 📄 {path.name} "
                        f"[{len(changed_sections)}/{len(v_sections)} section(s) à indexer]"
                    )
                    for sec in changed_sections:
                        for d_id in list(ds_snapshot.keys()):
                            if resolved_rels.get(d_id) != rel_path:
                                continue
                            fd_entry = fd_map.get(d_id)
                            existing_sec = (
                                extract_section_key(fd_entry.get("content", ""))
                                if isinstance(fd_entry, dict)
                                else None
                            )
                            if existing_sec in (sec["section_key"], None) or d_id == sec["doc_id"]:
                                purge_queue.append((d_id, f"{path.name}#{sec['section_key']}"))
                                ds_snapshot.pop(d_id, None)
                                resolved_rels.pop(d_id, None)
                                fd_map.pop(d_id, None)

                        claimed_sources = build_claimed_source_map(ds_snapshot, resolved_rels)
                        source_key = build_section_source_key(
                            rel_path,
                            sec["section_key"],
                            claimed_sources=claimed_sources,
                        )
                        ds_snapshot[sec["doc_id"]] = {"file_path": source_key, "status": "pending"}
                        resolved_rels[sec["doc_id"]] = rel_path
                        doc_kb = len(sec["content"]) / 1024.0
                        prefer_local = bool(
                            auto_state is not None
                            and auto_state["cloud_min_kb"] > 0
                            and doc_kb < auto_state["cloud_min_kb"]
                        )
                        insert_units.append(
                            {
                                "path": path,
                                "rel_path": rel_path,
                                "section_key": sec["section_key"],
                                "doc_id": sec["doc_id"],
                                "source_key": source_key,
                                "content": sec["content"],
                                "content_sha256": file_norm_sha,
                                "prefer_local": prefer_local,
                                "gleaning": resolve_gleaning_for_doc(rel_path, gleaning_mode),
                                "is_section": True,
                            }
                        )
                    continue

            content = prepare_document(
                path,
                genai_client,
                provider=args.provider,
                model=args.model,
                auto_state=auto_state,
                managed_ollama=managed_ollama,
            )
            if not content:
                continue

            if ext in (".md", ".py", ".txt"):
                try:
                    file_norm_sha = compute_normalized_sha256(path.read_text(encoding="utf-8"), ext=ext)
                except OSError:
                    file_norm_sha = compute_normalized_sha256(content, ext=ext)
            else:
                file_norm_sha = compute_normalized_sha256(content, ext=ext)

            doc_kb = len(content) / 1024.0
            prefer_local = False
            if auto_state is not None:
                min_kb = auto_state["cloud_min_kb"]
                prefer_local = bool(min_kb > 0 and doc_kb < min_kb)
                if prefer_local:
                    route_tag = f"🦙 Ollama seuil ({doc_kb:.1f} Ko < {min_kb:.0f} Ko)"
                elif auto_state["cloud_exhausted"]:
                    if not auto_state.get("oneminai_exhausted", True):
                        route_tag = f"🪙 1min.ai repli ({doc_kb:.1f} Ko)"
                    else:
                        route_tag = f"🦙 Ollama repli ({doc_kb:.1f} Ko)"
                else:
                    route_tag = f"💎 Gemini ({doc_kb:.1f} Ko)"
                logger.info(f"[{i:3d}/{len(ordered_update)}] 📄 {path.name} [{route_tag}]")
            else:
                logger.info(f"[{i:3d}/{len(ordered_update)}] 📄 {path.name}")

            expected_flat = rel_path.replace("/", "--") if "/" in rel_path else f"root--{rel_path}"
            matching_ids = _find_matching_doc_ids(
                ds_snapshot=ds_snapshot,
                resolved_rels=resolved_rels,
                target_abs=str(path),
                rel_target=rel_path,
                target_basename=path.name,
                allow_basename_match=(active_name_counts.get(path.name, 0) <= 1),
                extra_doc_id=log_idx.get(str(path), {}).get("doc_id"),
                target_source_key=expected_flat,
            )
            for mid in matching_ids:
                purge_queue.append((mid, path.name))
                ds_snapshot.pop(mid, None)
                resolved_rels.pop(mid, None)
                fd_map.pop(mid, None)

            claimed_sources = build_claimed_source_map(ds_snapshot, resolved_rels)
            source_key = build_rag_source_key(
                rel_path,
                name_counts=active_name_counts,
                claimed_sources=claimed_sources,
            )
            doc_id = compute_doc_id(content)
            ds_snapshot[doc_id] = {"file_path": source_key, "status": "pending"}
            resolved_rels[doc_id] = rel_path
            insert_units.append(
                {
                    "path": path,
                    "rel_path": rel_path,
                    "section_key": None,
                    "doc_id": doc_id,
                    "source_key": source_key,
                    "content": content,
                    "content_sha256": file_norm_sha,
                    "prefer_local": prefer_local,
                    "gleaning": resolve_gleaning_for_doc(rel_path, gleaning_mode),
                    "is_section": False,
                }
            )

        # ── Phase 2B : Purge groupee avant insertion ──
        if purge_queue:
            _write_progress_state(
                DB_PATH,
                {
                    "phase": "purge",
                    "started_at": run_started_at,
                    "updated_at": time.time(),
                    "provider": args.provider,
                    "summary_mode": summary_mode,
                    "gleaning_mode": gleaning_mode,
                    "batch_size": max(1, int(getattr(args, "batch_size", 8))),
                    "active_engine": _resolve_live_engine_label(args, auto_state),
                    "total_files": len(ordered_update),
                    "prepared_files": len(ordered_update),
                    "done_files": 0,
                    "total_units": len(insert_units),
                    "done_units": 0,
                    "failed_units": 0,
                },
            )
            purged_ids_seen: set[str] = set()
            for pid, plabel in purge_queue:
                if pid in purged_ids_seen:
                    continue
                purged_ids_seen.add(pid)
                purged_n = await _purge_doc_ids(rag, [pid], plabel)
                if purged_n:
                    did_write = True

        # ── Phase 3 : Insertion en lots (batch ainsert + gleaning adaptatif) ──
        batch_size = max(1, int(getattr(args, "batch_size", 8)))
        gleaning_stats = {0: 0, 1: 0}
        done_units = 0
        failed_units = 0
        done_files_set: set[str] = set()
        if insert_units:
            buckets = [
                (False, 1, [u for u in insert_units if not u["prefer_local"] and u["gleaning"] == 1]),
                (False, 0, [u for u in insert_units if not u["prefer_local"] and u["gleaning"] == 0]),
                (True, 1, [u for u in insert_units if u["prefer_local"] and u["gleaning"] == 1]),
                (True, 0, [u for u in insert_units if u["prefer_local"] and u["gleaning"] == 0]),
            ]
            total_batches = sum(
                (len(b_units) + batch_size - 1) // batch_size
                for _, _, b_units in buckets
                if b_units
            )
            batch_idx = 0
            prev_gleaning = getattr(rag, "entity_extract_max_gleaning", 1)
            try:
                for pref_local, glean_val, bucket_units in buckets:
                    if not bucket_units:
                        continue
                    rag.entity_extract_max_gleaning = glean_val
                    if auto_state is not None:
                        auto_state["prefer_local_doc"] = pref_local
                    for b_start in range(0, len(bucket_units), batch_size):
                        batch = bucket_units[b_start : b_start + batch_size]
                        batch_idx += 1
                        _write_progress_state(
                            DB_PATH,
                            {
                                "phase": "insert",
                                "started_at": run_started_at,
                                "updated_at": time.time(),
                                "provider": args.provider,
                                "summary_mode": summary_mode,
                                "gleaning_mode": gleaning_mode,
                                "batch_size": batch_size,
                                "active_engine": _resolve_live_engine_label(args, auto_state),
                                "total_files": len(ordered_update),
                                "prepared_files": len(ordered_update),
                                "done_files": len(done_files_set),
                                "total_units": len(insert_units),
                                "done_units": done_units,
                                "failed_units": failed_units,
                                "current_batch_index": batch_idx,
                                "total_batches": total_batches,
                                "current_batch_gleaning": glean_val,
                                "current_batch_files": [u["rel_path"] for u in batch],
                            },
                        )
                        try:
                            if len(batch) == 1:
                                u0 = batch[0]
                                await rag.ainsert(u0["content"], ids=[u0["doc_id"]], file_paths=[u0["source_key"]])
                            else:
                                logger.info(
                                    f"📦 Insertion lot LightRAG ({len(batch)} doc(s), gleaning={glean_val} : "
                                    f"{', '.join(u['source_key'] for u in batch[:4])}"
                                    f"{'...' if len(batch) > 4 else ''})..."
                                )
                                await rag.ainsert(
                                    [u["content"] for u in batch],
                                    ids=[u["doc_id"] for u in batch],
                                    file_paths=[u["source_key"] for u in batch],
                                )
                            did_write = True
                            gleaning_stats[glean_val] = gleaning_stats.get(glean_val, 0) + len(batch)
                            for u in batch:
                                inserted_row = await rag.doc_status.get_by_id(u["doc_id"])
                                if is_doc_processed(inserted_row):
                                    row_copy = (
                                        dict(inserted_row)
                                        if isinstance(inserted_row, dict)
                                        else {"file_path": u["source_key"], "status": "processed"}
                                    )
                                    row_copy.setdefault("file_path", u["source_key"])
                                    ds_snapshot[u["doc_id"]] = row_copy
                                    resolved_rels[u["doc_id"]] = u["rel_path"]
                                    if u["is_section"]:
                                        plan = section_file_plans.get(str(u["path"]))
                                        if plan is not None:
                                            plan["pending_doc_ids"].discard(u["doc_id"])
                                    else:
                                        done_files_set.add(u["rel_path"])
                                        log_idx[str(u["path"])] = {
                                            "mtime": os.path.getmtime(u["path"]),
                                            "doc_id": u["doc_id"],
                                            "content_sha256": u["content_sha256"],
                                        }
                                else:
                                    failed_units += 1
                                    if u["is_section"]:
                                        plan = section_file_plans.get(str(u["path"]))
                                        if plan is not None:
                                            plan["failed"] = True
                                    st_val = (
                                        inserted_row.get("status")
                                        if isinstance(inserted_row, dict)
                                        else "absent/rejeté (dup-*)"
                                    )
                                    logger.warning(
                                        f"⚠️ Indexation non confirmée pour {u['rel_path']} "
                                        f"({u['doc_id']}, clé={u['source_key']}, statut={st_val!r}) "
                                        f"— indexed_files.json conservé intact pour réessai."
                                    )
                            done_units += len(batch)
                            for p_str, plan in section_file_plans.items():
                                if not plan["failed"] and not plan["pending_doc_ids"]:
                                    done_files_set.add(_relative_doc_path(Path(p_str)))
                                    sec_dict = plan["sections"]
                                    first_did = next(iter(sec_dict.values()))["doc_id"]
                                    log_idx[p_str] = {
                                        "mtime": plan["mtime"],
                                        "doc_id": first_did,
                                        "content_sha256": plan["content_sha256"],
                                        "sections": sec_dict,
                                    }
                            save_index_log(log_idx)
                        except Exception as e:
                            failed_units += len(batch)
                            done_units += len(batch)
                            for u in batch:
                                if u["is_section"] and str(u["path"]) in section_file_plans:
                                    section_file_plans[str(u["path"])]["failed"] = True
                            logger.warning(f"⚠️ Échec d'indexation du lot ({len(batch)} doc(s)): {e}")
                        _write_progress_state(
                            DB_PATH,
                            {
                                "phase": "insert",
                                "started_at": run_started_at,
                                "updated_at": time.time(),
                                "provider": args.provider,
                                "summary_mode": summary_mode,
                                "gleaning_mode": gleaning_mode,
                                "batch_size": batch_size,
                                "active_engine": _resolve_live_engine_label(args, auto_state),
                                "total_files": len(ordered_update),
                                "prepared_files": len(ordered_update),
                                "done_files": len(done_files_set),
                                "total_units": len(insert_units),
                                "done_units": done_units,
                                "failed_units": failed_units,
                                "current_batch_index": batch_idx,
                                "total_batches": total_batches,
                                "current_batch_gleaning": glean_val,
                                "current_batch_files": [u["rel_path"] for u in batch],
                            },
                        )
            finally:
                rag.entity_extract_max_gleaning = prev_gleaning

        for p_str, plan in section_file_plans.items():
            if not plan["failed"] and not plan["pending_doc_ids"]:
                sec_dict = plan["sections"]
                first_did = next(iter(sec_dict.values()))["doc_id"]
                log_idx[p_str] = {
                    "mtime": plan["mtime"],
                    "doc_id": first_did,
                    "content_sha256": plan["content_sha256"],
                    "sections": sec_dict,
                }
        for p_str, new_mt in mtime_refreshes.items():
            if isinstance(log_idx.get(p_str), dict):
                log_idx[p_str]["mtime"] = new_mt

        save_index_log(log_idx)
        logger.info("🎉 Synthèse Finale :")
        logger.info(
            f"  - Résumés de fusion ({summary_mode}): deterministe={summary_stats['deterministic']}, "
            f"gemma4={summary_stats['gemma4']}, force_llm_summary_on_merge={force_summary_merge}"
        )
        logger.info(
            f"  - Gleaning ({gleaning_mode}): gleaning=1 sur {gleaning_stats[1]} unité(s), "
            f"gleaning=0 sur {gleaning_stats[0]} unité(s)"
        )
        if auto_state is not None:
            for m_name, ok_count in auto_state["gemini_ok"].items():
                if ok_count > 0 or m_name in auto_state["exhausted_models"]:
                    stat_tag = " [EXHAUSTED]" if m_name in auto_state["exhausted_models"] else ""
                    logger.info(f"  - {m_name}: OK={ok_count}{stat_tag}")
            logger.info(f"  - Gemini erreurs/bascules: ERR={auto_state['gemini_err']}")
            if auto_state.get("oneminai_enabled") or auto_state.get("oneminai_ok", 0) > 0 or auto_state.get("oneminai_err", 0) > 0:
                om_tag = " [EXHAUSTED]" if auto_state.get("oneminai_exhausted") else ""
                logger.info(
                    f"  - 1min.ai ({auto_state.get('oneminai_model')}): OK={auto_state.get('oneminai_ok', 0)} | "
                    f"ERR={auto_state.get('oneminai_err', 0)} | in={auto_state.get('oneminai_prompt_tokens', 0)} tok | "
                    f"out={auto_state.get('oneminai_completion_tokens', 0)} tok{om_tag}"
                )
            logger.info(f"  - Ollama local ({auto_state['ollama_model']}): OK={auto_state['ollama_ok']} | ERR={auto_state['ollama_err']}")
            for vlm_name, v_count in (auto_state.get("vlm_ok") or {}).items():
                logger.info(f"  - VLM ({vlm_name}): OK={v_count}")
            used_parts = [f"gemini/{m} (x{c})" for m, c in auto_state["gemini_ok"].items() if c > 0]
            if auto_state.get("oneminai_ok", 0) > 0:
                used_parts.append(
                    f"1minai/{auto_state['oneminai_model']} "
                    f"(x{auto_state['oneminai_ok']}, in={auto_state['oneminai_prompt_tokens']} tok, "
                    f"out={auto_state['oneminai_completion_tokens']} tok)"
                )
            if auto_state["ollama_ok"] > 0:
                used_parts.append(f"ollama/{auto_state['ollama_model']} (x{auto_state['ollama_ok']})")
            if used_parts:
                logger.info(f"🧭 Moteur(s) d'indexation utilisés : {', '.join(used_parts)}")
        elif args.provider == "ollama":
            logger.info(f"🧭 Moteur d'indexation utilisé : ollama/{_get_ollama_model(args.model)} (think=False)")
        elif args.provider in ("local", "unsloth"):
            from rag_runtime import resolve_unsloth_config
            _, u_model, _ = resolve_unsloth_config()
            logger.info(f"🧭 Moteur d'indexation utilisé : unsloth/{args.model or u_model}")
        elif args.provider == "1minai":
            from rag_runtime import resolve_1minai_config
            _, d_model, _ = resolve_1minai_config()
            used_model = args.model or d_model
            s = stats.get(f"1minai:{used_model}", {"success": 0, "failures": 0, "prompt_tokens": 0, "completion_tokens": 0})
            logger.info(
                f"🧭 Moteur d'indexation utilisé : 1minai/{used_model} "
                f"(OK={s['success']}, ERR={s['failures']}, in={s.get('prompt_tokens', 0)} tok, out={s.get('completion_tokens', 0)} tok)"
            )
        elif args.provider == "gemini":
            used_g = [f"{k} (OK={v['success']}, ERR={v['failures']})" for k, v in stats.items() if v["success"] > 0 or v["failures"] > 0]
            for line in used_g:
                logger.info(f"  - {line}")
            used_ok = [f"{k} (x{v['success']})" for k, v in stats.items() if v["success"] > 0]
            if used_ok:
                logger.info(f"🧭 Moteur(s) d'indexation utilisés : {', '.join(used_ok)}")
        else:
            for m in MODELS_ROTATION:
                name = m["name"]
                logger.info(f"  - {name}: OK={stats[name]['success']} | ERR={stats[name]['failures']}")

        if did_write and (
            getattr(args, "mirror_backup", False)
            or os.environ.get("RAG_AUTO_MIRROR_BACKUP", "").strip().lower() in ("1", "true", "yes")
        ):
            _write_progress_state(
                DB_PATH,
                {
                    "phase": "mirror_backup",
                    "started_at": run_started_at,
                    "updated_at": time.time(),
                    "provider": args.provider,
                    "summary_mode": summary_mode,
                    "gleaning_mode": gleaning_mode,
                    "batch_size": batch_size,
                    "active_engine": _resolve_live_engine_label(args, auto_state),
                    "total_files": len(ordered_update),
                    "prepared_files": len(ordered_update),
                    "done_files": len(done_files_set),
                    "total_units": len(insert_units),
                    "done_units": len(insert_units),
                    "failed_units": failed_units,
                },
            )
            ok_m, msg_m = sync_db_to_backup_mirror(DB_PATH)
            logger.info(f"💾 Miroir sauvegarde : {msg_m}" if ok_m else f"⚠️ Miroir sauvegarde : {msg_m}")
    finally:
        try:
            _clear_progress_state(DB_PATH)
            if managed_ollama is not None:
                managed_ollama.cleanup()
        finally:
            indexing_lock.release()

def build_arg_parser() -> argparse.ArgumentParser:
    """Construit le parser CLI avec les défauts incrémental (--update) et --provider auto."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Réindexation complète depuis zéro")
    parser.add_argument(
        "--update",
        action="store_true",
        default=True,
        help="Mise à jour incrémentale (actif par défaut si --full et --files sont absents)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Chemins de fichiers spécifiques à réindexer (absolus, relatifs au CWD ou relatifs à DOCS_ROOT)",
    )
    parser.add_argument(
        "--provider",
        choices=["auto", "local", "unsloth", "ollama", "1minai", "online", "openrouter", "gemini"],
        default="auto",
        help="Fournisseur LLM (défaut: auto = Gemini Free Tier -> Ollama local ; --with-1minai pour ajouter 1min.ai en palier 2)",
    )
    parser.add_argument(
        "--with-1minai",
        action="store_true",
        default=False,
        help="Active le palier intermédiaire 1min.ai entre Gemini et Ollama en mode --provider auto",
    )
    parser.add_argument(
        "--no-1minai",
        action="store_true",
        default=False,
        help="Force la désactivation du palier intermédiaire 1min.ai en mode --provider auto",
    )
    parser.add_argument(
        "--cloud-min-kb",
        type=float,
        default=0.0,
        help="En --provider auto, taille texte minimale (Ko) pour utiliser Gemini avant envoi direct à Ollama (défaut: 0)",
    )
    parser.add_argument(
        "--thinking-level",
        choices=["minimal", "low", "medium", "high"],
        default="low",
        help="Niveau d'effort de réflexion Gemini (défaut: low = 100 tok, jamais extra_high)",
    )
    parser.add_argument(
        "--prepare-agent",
        nargs="?",
        const="auto",
        default=None,
        help="Prépare un lot JSON de chunks/images pour indexation directe par Antigravity (0 LLM tiers)",
    )
    parser.add_argument(
        "--commit-agent",
        type=str,
        default=None,
        help="Valide et committe dans LightRAG un lot agent préparé (job_id ou chemin manifest.json)",
    )
    parser.add_argument(
        "--extractions",
        type=str,
        default=None,
        help="Fichier JSON d'extractions agent optionnel pour --commit-agent (défaut: extractions.json du job)",
    )
    parser.add_argument(
        "--effort-profile",
        choices=["fast", "balanced", "thorough"],
        default="balanced",
        help="Profil d'effort adapté pour --prepare-agent (défaut: balanced = flash standard + inherit critique, jamais extra_high)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Forcer un modèle spécifique (défaut par fournisseur, ex: qwen3.8:27b-mlx pour ollama)",
    )
    parser.add_argument(
        "--summary-mode",
        choices=["deterministic", "gemma4", "llm"],
        default=os.environ.get("RAG_SUMMARY_MODE", "deterministic"),
        help="Mode de synthèse lors des fusions d'entités hubs (défaut: deterministic = 0 appel LLM)",
    )
    parser.add_argument(
        "--gleaning-mode",
        choices=["adaptive", "on", "off"],
        default=os.environ.get("RAG_GLEANING_MODE", "adaptive"),
        help="Passe de gleaning LightRAG : adaptive (1 sur critiques/PDF/SVG, 0 sur standard), on (1 partout), off (0 partout)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=int(os.environ.get("RAG_INSERT_BATCH_SIZE", "8")),
        help="Nombre maximum de documents insérés par lot rag.ainsert() (défaut: 8)",
    )
    parser.add_argument(
        "--no-section-split",
        action="store_true",
        default=False,
        help="Désactive le découpage en sous-documents virtuels par section ## sur les gros .md",
    )
    parser.add_argument(
        "--mirror-backup",
        action="store_true",
        default=False,
        help="Synchronise la base locale vers le miroir Google Drive en fin d'indexation",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        default=False,
        help="Désactive la lecture du cache LLM d'extraction LightRAG (enable_llm_cache_for_entity_extract=False)",
    )
    parser.add_argument("--api-key", type=str)
    return parser


def parse_cli_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse les arguments CLI en désactivant --update lorsque --full ou --files est fourni."""
    args = build_arg_parser().parse_args(argv)
    if args.full or args.files or args.prepare_agent or args.commit_agent:
        args.update = False
    return args


async def main():
    args = parse_cli_args()
    await run_indexing(args)

if __name__ == "__main__":
    asyncio.run(main())
