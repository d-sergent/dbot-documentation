#!/opt/homebrew/bin/python3.11
"""
Serveur MCP pour LightRAG — Documentation D-Bot

Expose 4 outils MCP utilisables par n'importe quel LLM compatible MCP (Antigravity, Claude, Unsloth, etc.) :
  - rag_search        : Recherche sémantique hybride dans la documentation
  - rag_analyze_impact: Analyse de cause à effet croisée entre composants
  - rag_get_context   : Contexte précis autour d'un sujet spécifique
  - rag_list_topics   : Liste les grandes thématiques indexées

Configuration dans mcp-config.json :
  {
    "dbot-rag": {
      "command": "python3",
      "args": ["/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/mcp_lightrag_server.py"],
      "env": {
        "UNSLOTH_BASE_URL": "http://127.0.0.1:8888/v1",
        "RAG_DB_PATH": "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"
      }
    }
  }

Prérequis : pip install lightrag-hku lancedb fastembed mcp
"""

import asyncio
import base64
import contextvars
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path

_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

from source_key_utils import (
    build_claimed_source_map,
    build_rag_source_key,
    build_section_source_key,
    canonical_source_name,
    extract_rel_path,
    extract_section_key,
    is_doc_processed,
)
from agent_indexing import (
    AGENT_EFFORT_PROFILES,
    COMPLETION_DELIMITER,
    TUPLE_DELIMITER,
    commit_agent_bundle,
    compute_rag_disk_stamp,
    deterministic_merge_descriptions,
    is_indexing_lock_active,
    prepare_agent_bundle,
    resolve_effort_profile,
)
from rag_chunking import (
    chunking_markdown_anchored,
    compute_normalized_sha256,
    extract_pdf_text_cached,
    is_entity_summary_prompt,
    resolve_gleaning_for_doc,
    sanitize_lightrag_extraction_output,
    split_markdown_into_virtual_sections,
)

# ─── Hack Tiktoken ────────────────────────────────────────────────────────────
# Désactive globalement la vérification des "special tokens" (<|endoftext|>)
# pour éviter que les requêtes ou le graphe ne fassent planter le tokenizer.
import tiktoken
_original_encode = tiktoken.Encoding.encode
def _safe_encode(self, text, *args, **kwargs):
    kwargs["disallowed_special"] = ()
    return _original_encode(self, text, *args, **kwargs)
tiktoken.Encoding.encode = _safe_encode

# ─── Configuration & Environnement ────────────────────────────────────────────

from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
if not os.environ.get("GEMINI_API_KEY") and Path("/Users/Shared/Mon Google Drive Physique/Documentation/.env").exists():
    load_dotenv(dotenv_path="/Users/Shared/Mon Google Drive Physique/Documentation/.env")

DOCS_ROOT             = Path(os.environ.get("RAG_DOCS_ROOT", "/Users/Shared/Mon Google Drive Physique/Documentation"))
REPORT_PATH           = DOCS_ROOT / "annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md"
QUESTIONS_JSON_PATH   = DOCS_ROOT / "annexes/Outils_de_Travail/RAG/AUDIT_QUESTION_REPONSE.json"
PLAN_CORRECTION_PATH  = DOCS_ROOT / "annexes/Outils_de_Travail/RAG/PLAN_CORRECTION.md"
PROMPT_CORRECTION_PATH = DOCS_ROOT / "annexes/Outils_de_Travail/RAG/PROMPT_CORRECTION.md"
_RAG_DIR = str(Path(__file__).resolve().parent)
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

from rag_runtime import (
    DEFAULT_OLLAMA_INDEX_MODEL,
    DEFAULT_OPENROUTER_MODEL,
    GEMINI_VLM_CASCADE,
    GeminiCascadeSession,
    ManagedOllamaServer,
    ModelExecutionTracker,
    OneMinAiCascadeSession,
    apply_tiktoken_patch,
    build_gemini_cascade,
    build_local_openai_extra_body,
    build_openai_messages,
    call_1minai_stateless_async,
    check_ollama_ready,
    check_unsloth_ready,
    create_genai_client,
    env_flag,
    extract_lexical_keywords,
    format_gemini_error,
    get_gemini_timeout_s,
    is_1minai_compatible_model_override,
    is_1minai_permanent_or_quota_error,
    is_gemini_model_name,
    normalize_rag_role,
    resolve_1minai_auto_index_target,
    resolve_1minai_config,
    resolve_default_db_path,
    resolve_ollama_config,
    resolve_unsloth_config,
)

DB_PATH               = Path(resolve_default_db_path())

VMLX_BASE_URL, VMLX_MODEL, VMLX_API_KEY = resolve_unsloth_config()
UNSLOTH_BASE_URL, UNSLOTH_MODEL, UNSLOTH_API_KEY = VMLX_BASE_URL, VMLX_MODEL, VMLX_API_KEY
OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_NUM_CTX, OLLAMA_KEEP_ALIVE = resolve_ollama_config(role="index")
_, OLLAMA_QA_MODEL, _, _ = resolve_ollama_config(role="qa")
_, OLLAMA_AUDIT_MODEL, _, _ = resolve_ollama_config(role="audit")
RAG_LLM_PROVIDER      = os.environ.get("RAG_LLM_PROVIDER", "auto").strip().lower()
RAG_AUTO_START_SERVER = env_flag("RAG_AUTO_START_SERVER", True)
_MANAGED_OLLAMA       = ManagedOllamaServer(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
SKIP_IMAGES           = env_flag("RAG_SKIP_IMAGES", True)
IMAGE_EXTS            = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}
RASTER_VLM_EXTS       = {".png", ".jpg", ".jpeg", ".webp"}

_CURRENT_RAG_ROLE: contextvars.ContextVar[str] = contextvars.ContextVar("_CURRENT_RAG_ROLE", default="qa")
_CURRENT_TRACKER: contextvars.ContextVar[ModelExecutionTracker | None] = contextvars.ContextVar("_CURRENT_TRACKER", default=None)
_CURRENT_PROVIDER_OVERRIDE: contextvars.ContextVar[str | None] = contextvars.ContextVar("_CURRENT_PROVIDER_OVERRIDE", default=None)
_CURRENT_MODEL_OVERRIDE: contextvars.ContextVar[str | None] = contextvars.ContextVar("_CURRENT_MODEL_OVERRIDE", default=None)
_GEMINI_SESSIONS: dict[str, GeminiCascadeSession] = {}
_ONEMINAI_SESSIONS: dict[str, OneMinAiCascadeSession] = {}


def _get_oneminai_session(role: str, model_override: str | None = None) -> OneMinAiCascadeSession:
    norm_role = normalize_rag_role(role)
    _, def_model, live_key = resolve_1minai_config(role=norm_role)
    eff_model = (
        model_override.strip()
        if (model_override and is_1minai_compatible_model_override(model_override))
        else def_model
    )
    cache_key = f"{norm_role}:{eff_model}"
    sess = _ONEMINAI_SESSIONS.get(cache_key)
    if sess is None or sess.api_key != live_key:
        sess = OneMinAiCascadeSession(role=norm_role, model_override=model_override)
        _ONEMINAI_SESSIONS[cache_key] = sess
    return sess

# Profils d'échantillonnage recommandés Qwen3.8 / Unsloth (mode Non-Thinking)
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
    "repeat_penalty": 1.0,
    "presence_penalty": 1.0,
}

_md_img               = re.compile(r'!\[.*?\]\(.*?\)')
_orphan_ref           = re.compile(r'\[image:.*?\]', re.IGNORECASE)

# ─── Imports ──────────────────────────────────────────────────────────────────

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, CallToolResult
    import mcp.types as types
except ImportError:
    print("❌ Package 'mcp' manquant. Lancez : pip install mcp", file=sys.stderr)
    sys.exit(1)

try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import openai_complete_if_cache
    from lightrag.utils import EmbeddingFunc
    from fastembed import TextEmbedding
    # Le reranker change de nom/emplacement selon les versions de fastembed
    TextRerankerClass = None
    try:
        from fastembed import TextReranker
        TextRerankerClass = TextReranker
    except ImportError:
        try:
            from fastembed.rerank.cross_encoder import TextCrossEncoder
            TextRerankerClass = TextCrossEncoder
        except ImportError:
            pass
    
    HAS_RERANKER = TextRerankerClass is not None
except ImportError as e:
    print(f"❌ Dépendance manquante : {e}", file=sys.stderr)
    print("   Lancez : pip install lightrag-hku lancedb fastembed", file=sys.stderr)
    sys.exit(1)

# ─── Initialisation (Lazy — au premier appel) ─────────────────────────────────

_rag_instance = None
_rag_disk_path: str | None = None
_rag_disk_stamp: tuple | None = None
_rag_reload_lock_pair: tuple[int, asyncio.Lock] | None = None


def _get_rag_reload_lock() -> asyncio.Lock:
    global _rag_reload_lock_pair
    loop_id = id(asyncio.get_running_loop())
    if _rag_reload_lock_pair is None or _rag_reload_lock_pair[0] != loop_id:
        _rag_reload_lock_pair = (loop_id, asyncio.Lock())
    return _rag_reload_lock_pair[1]


def _mark_rag_disk_fresh(db_dir: Path | None = None) -> None:
    global _rag_disk_path, _rag_disk_stamp
    target = Path(db_dir or DB_PATH)
    _rag_disk_path = str(target)
    _rag_disk_stamp = compute_rag_disk_stamp(target)
import warnings
warnings.filterwarnings("ignore", message=".*intfloat/multilingual-e5-large now uses mean pooling.*")

DEFAULT_CACHE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/models_cache"
FASTEMBED_CACHE_DIR = os.environ.get("FASTEMBED_CACHE_PATH", DEFAULT_CACHE_DIR)

_embed_model  = None


def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding("intfloat/multilingual-e5-large", cache_dir=FASTEMBED_CACHE_DIR)
    return _embed_model


import numpy as np


async def fastembed_func(texts: list[str]) -> np.ndarray:
    """Retourne un np.ndarray shape (N, DIM) — ASYNC obligatoire pour la parité avec ask_rag.py."""
    model = get_embed_model()
    return np.array(list(model.embed(texts)), dtype=np.float32)


embedding_func = EmbeddingFunc(
    embedding_dim=1024,
    max_token_size=8192,
    func=fastembed_func
)


_rerank_model = None


def get_rerank_model():
    global _rerank_model
    if not HAS_RERANKER:
        return None
    if _rerank_model is None:
        try:
            print("⏳ Chargement du modèle de Rerank local (bge-reranker-base)...", file=sys.stderr)
            _rerank_model = TextRerankerClass("BAAI/bge-reranker-base", cache_dir=FASTEMBED_CACHE_DIR)
        except Exception as e:
            print(f"⚠️ Impossible de charger le Reranker : {e}", file=sys.stderr)
            return None
    return _rerank_model


async def fastembed_rerank_func(query: str, documents: list[str], top_n: int = None, **kwargs) -> list[dict]:
    """Fonction de Reranking native pour LightRAG basée sur FastEmbed Cross-Encoder."""
    if not documents:
        return []
    model = get_rerank_model()
    if model is None:
        return [{"index": i, "relevance_score": 0.0} for i in range(len(documents))]
    try:
        scores = list(model.rerank(query, documents))
        indexed = [
            {"index": i, "relevance_score": float(1.0 / (1.0 + np.exp(-float(s))))}
            for i, s in enumerate(scores)
        ]
        indexed.sort(key=lambda x: x["relevance_score"], reverse=True)
        return indexed[:top_n] if top_n else indexed
    except Exception as e:
        print(f"⚠️ Échec technique du Reranking natif : {e}", file=sys.stderr)
        return [{"index": i, "relevance_score": 0.0} for i in range(len(documents))]


async def fast_rerank_func(query: str, chunks: list) -> list:
    """Ré-ordonne les morceaux de texte manuellement (si non déjà rerankés par LightRAG)."""
    if not chunks:
        return chunks
    if "rerank_score" in chunks[0]:
        return sorted(chunks, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
    if not HAS_RERANKER:
        return chunks

    model = get_rerank_model()
    if model is None:
        return chunks

    try:
        texts = [c.get("content", "") for c in chunks]
        print(f"⚖️  Reranking de {len(chunks)} morceaux...", file=sys.stderr)
        scores = list(model.rerank(query, texts))

        # Association score normalisé sigmoïde [0.0, 1.0] + chunk
        for i, score in enumerate(scores):
            chunks[i]["rerank_score"] = float(1.0 / (1.0 + np.exp(-float(score))))

        return sorted(chunks, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
    except Exception as e:
        print(f"⚠️ Échec technique du Reranking : {e}", file=sys.stderr)
        return chunks


# --- Fonctions LLM & Intégration Gemini Flash (SDK google-genai) ---

_genai_clients: dict[float, object] = {}


def get_genai_client(timeout_s: float | None = None):
    eff_timeout = max(10.0, float(timeout_s if timeout_s is not None else get_gemini_timeout_s("qa")))
    cached = _genai_clients.get(eff_timeout)
    if cached is not None:
        return cached
    try:
        client = create_genai_client(timeout_s=eff_timeout)
        if client is not None:
            _genai_clients[eff_timeout] = client
        return client
    except Exception as ge:
        print(f"⚠️ Erreur initialisation genai.Client: {ge}", file=sys.stderr)
        return None


_SVG_SKIP_TAGS = frozenset({"defs", "style", "script", "metadata"})
_SVG_INLINE_TEXT_TAGS = frozenset({"tspan", "a", "textpath"})
_VLM_TECHNICAL_PROMPT = (
    "Tu es un expert en ingénierie mécanique, robotique et électronique pour le projet D-Bot.\n"
    "Analyse cette image technique en détail. Décris avec précision :\n"
    "1. Les composants mécaniques, électroniques, moteurs, roulements, fixations ou assemblages visibles.\n"
    "2. Toutes les cotations, dimensions, références, marquages ou annotations textuelles (ex: AXK 5578, M4x70, etc.).\n"
    "3. La géométrie, le montage et la fonction technique de ce sous-ensemble.\n"
    "Fournis une description technique exhaustive et structurée."
)


def _compute_doc_id(content: str) -> str:
    """Calcule l'identifiant MD5 canonique compatible LightRAG."""
    return "doc-" + hashlib.md5(content.strip().encode("utf-8"), usedforsecurity=False).hexdigest()


def _svg_local_tag(tag: object) -> str:
    return tag.split("}", 1)[-1].lower() if isinstance(tag, str) else ""


def _extract_svg_text_node(el) -> str:
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
    """Extrait le contenu textuel structuré (<title>, <desc>, <text>) d'un SVG via defusedxml."""
    import defusedxml.ElementTree as DefusedET

    raw_xml = path.read_text(encoding="utf-8")
    root = DefusedET.fromstring(raw_xml)
    return "\n\n".join(_collect_svg_blocks(root))


def _encode_image_for_ollama(image_path: Path, max_dim: int = 1600) -> str:
    """Encode une image PNG redimensionnée en base64 pour l'endpoint Ollama /api/chat."""
    from PIL import Image

    with Image.open(image_path) as img:
        if max(img.size) > max_dim:
            img = img.copy()
            img.thumbnail((max_dim, max_dim))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("ascii")


async def _call_ollama_chat(
    prompt: str,
    system_prompt: str | None = None,
    history_messages: list | None = None,
    model_name: str | None = None,
    images: list[str] | None = None,
    num_ctx: int | None = None,
    temperature: float = QWEN_EXTRACT_SAMPLING["temperature"],
    max_tokens: int = 8192,
    top_p: float = QWEN_EXTRACT_SAMPLING["top_p"],
    top_k: int = QWEN_EXTRACT_SAMPLING["top_k"],
    min_p: float = QWEN_EXTRACT_SAMPLING["min_p"],
    repeat_penalty: float = QWEN_EXTRACT_SAMPLING["repeat_penalty"],
    presence_penalty: float = QWEN_EXTRACT_SAMPLING["presence_penalty"],
) -> str:
    """Appelle Ollama /api/chat avec think=False et profil d'échantillonnage Qwen3.8."""
    import aiohttp

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    for msg in history_messages or []:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})
    user_msg: dict = {"role": "user", "content": prompt}
    if images:
        user_msg["images"] = images
    messages.append(user_msg)

    payload = {
        "model": model_name or OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "think": False,
        "keep_alive": OLLAMA_KEEP_ALIVE,
        "options": {
            "num_ctx": num_ctx or OLLAMA_NUM_CTX,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "min_p": min_p,
            "repeat_penalty": repeat_penalty,
            "presence_penalty": presence_penalty,
            "num_predict": max_tokens,
        },
    }
    timeout = aiohttp.ClientTimeout(total=600)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload) as resp:
            if resp.status != 200:
                err_txt = await resp.text()
                raise RuntimeError(f"Ollama HTTP {resp.status}: {err_txt[:200]}")
            data = await resp.json()
            content = (data.get("message") or {}).get("content", "")
            if not content:
                raise RuntimeError("Réponse Ollama vide")
            return content


def _get_gemini_session(role: str, thinking_budget: int = 100, wait_on_transient: bool = False) -> GeminiCascadeSession:
    norm = normalize_rag_role(role)
    key = f"{norm}:{thinking_budget}:{int(wait_on_transient)}"
    sess = _GEMINI_SESSIONS.get(key)
    if sess is None:
        sess = GeminiCascadeSession(
            build_gemini_cascade(norm),
            timeout_s=get_gemini_timeout_s(norm),
            thinking_budget=thinking_budget,
            rpm_delay=2.5 if norm == "index" else 0.0,
            wait_on_transient=wait_on_transient,
        )
        _GEMINI_SESSIONS[key] = sess
    return sess


async def _call_gemini_chat(
    prompt: str,
    system_prompt: str | None = None,
    history_messages: list | None = None,
    model_name: str | None = None,
    thinking_level_str: str = "low",
    role: str = "qa",
    tracker: ModelExecutionTracker | None = None,
    wait_on_transient: bool = False,
) -> tuple[str | None, str | None]:
    """Appelle la cascade Gemini Free Tier avec timeout borne (>= 10s) et bascule automatique."""
    timeout_s = get_gemini_timeout_s(role)
    client = get_genai_client(timeout_s=timeout_s)
    if client is None:
        return None, None
    th_budget = 0 if thinking_level_str == "minimal" else 100
    if model_name and is_gemini_model_name(model_name):
        sess = GeminiCascadeSession(
            build_gemini_cascade(role, explicit_model=model_name),
            timeout_s=timeout_s,
            thinking_budget=th_budget,
            rpm_delay=2.5 if normalize_rag_role(role) == "index" else 0.0,
            wait_on_transient=wait_on_transient,
        )
    else:
        sess = _get_gemini_session(role, thinking_budget=th_budget, wait_on_transient=wait_on_transient)
    return await sess.call(
        client,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        max_tokens=8192 if normalize_rag_role(role) == "index" else 4096,
        temperature=0.1 if normalize_rag_role(role) == "index" else 0.2,
        tracker=tracker,
    )


async def _try_ollama_role_chat(
    prompt: str,
    *,
    role: str,
    model_override: str | None,
    system_prompt: str | None,
    history_messages: list,
    tracker: ModelExecutionTracker | None,
    kwargs: dict,
) -> str | None:
    """Tente Ollama avec le meilleur modele adapte au role (gemma4:26b en QA/Audit, qwen3.8:27b-mlx en Index)."""
    norm_role = normalize_rag_role(role)
    candidates: list[str] = []
    if model_override and not is_gemini_model_name(model_override) and ":" in model_override:
        candidates.append(model_override.strip())
    if norm_role in ("qa", "audit"):
        role_model = OLLAMA_AUDIT_MODEL if norm_role == "audit" else OLLAMA_QA_MODEL
        for m in (role_model, OLLAMA_MODEL, DEFAULT_OLLAMA_INDEX_MODEL):
            if m and m not in candidates:
                candidates.append(m)
    else:
        for m in (OLLAMA_MODEL, DEFAULT_OLLAMA_INDEX_MODEL):
            if m and m not in candidates:
                candidates.append(m)

    ollama_ready = check_ollama_ready(OLLAMA_BASE_URL, timeout=0.4)
    if not ollama_ready and RAG_AUTO_START_SERVER:
        _MANAGED_OLLAMA.model = candidates[0]
        ollama_ready = _MANAGED_OLLAMA.ensure_started()
    if not ollama_ready:
        return None

    sampling = QWEN_EXTRACT_SAMPLING if norm_role == "index" else QWEN_QA_SAMPLING
    for cand in candidates:
        if not check_ollama_ready(OLLAMA_BASE_URL, required_model=cand, timeout=0.4):
            continue
        try:
            text = await _call_ollama_chat(
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                model_name=cand,
                temperature=kwargs.get("temperature", sampling["temperature"]),
                max_tokens=kwargs.get("max_tokens", 4096),
                top_p=kwargs.get("top_p", sampling["top_p"]),
                top_k=kwargs.get("top_k", sampling["top_k"]),
                min_p=kwargs.get("min_p", sampling["min_p"]),
                repeat_penalty=kwargs.get("repeat_penalty", sampling["repeat_penalty"]),
                presence_penalty=kwargs.get("presence_penalty", sampling["presence_penalty"]),
            )
            if tracker is not None:
                tracker.record_success("ollama", cand)
            return text
        except Exception as oe:
            if tracker is not None:
                tracker.record_failure("ollama", cand, format_gemini_error(oe))
    return None


async def _try_unsloth_chat(
    prompt: str,
    *,
    model_override: str | None,
    system_prompt: str | None,
    history_messages: list,
    tracker: ModelExecutionTracker | None,
    kwargs: dict,
) -> str | None:
    """Tente Unsloth Studio (:8888/v1) si le serveur est actif."""
    if not check_unsloth_ready(UNSLOTH_BASE_URL, UNSLOTH_API_KEY, timeout=0.4):
        return None
    target_model = model_override if (model_override and not is_gemini_model_name(model_override)) else UNSLOTH_MODEL
    enable_thinking = os.environ.get("RAG_ENABLE_THINKING", "false").strip().lower() in ("1", "true", "yes")
    call_kwargs = dict(kwargs)
    call_kwargs.setdefault("max_tokens", 8192 if enable_thinking else 4096)
    call_kwargs.setdefault("temperature", 1.0 if enable_thinking else QWEN_QA_SAMPLING["temperature"])
    call_kwargs.setdefault("top_p", 0.95 if enable_thinking else QWEN_QA_SAMPLING["top_p"])
    call_kwargs.setdefault("presence_penalty", 0.0 if enable_thinking else QWEN_QA_SAMPLING["presence_penalty"])
    extra_body = build_local_openai_extra_body(
        top_k=call_kwargs.pop("top_k", QWEN_QA_SAMPLING["top_k"]),
        min_p=call_kwargs.pop("min_p", QWEN_QA_SAMPLING["min_p"]),
        repeat_penalty=call_kwargs.pop("repeat_penalty", QWEN_QA_SAMPLING["repeat_penalty"]),
    )
    extra_body["chat_template_kwargs"] = {"enable_thinking": enable_thinking}
    user_extra = call_kwargs.pop("extra_body", None)
    if isinstance(user_extra, dict):
        extra_body.update(user_extra)
    try:
        text = await openai_complete_if_cache(
            target_model,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            base_url=UNSLOTH_BASE_URL,
            api_key=UNSLOTH_API_KEY,
            extra_body=extra_body,
            **call_kwargs,
        )
        if text and str(text).strip():
            if tracker is not None:
                tracker.record_success("unsloth", target_model)
            return str(text)
    except Exception as ue:
        if tracker is not None:
            tracker.record_failure("unsloth", target_model, format_gemini_error(ue))
    return None


async def llm_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    role = _CURRENT_RAG_ROLE.get()
    norm_role = normalize_rag_role(role)
    tracker = _CURRENT_TRACKER.get()
    prov_override = _CURRENT_PROVIDER_OVERRIDE.get()
    model_override = _CURRENT_MODEL_OVERRIDE.get()
    pref = (prov_override or RAG_LLM_PROVIDER or "auto").strip().lower()
    if pref in ("local", "vmlx"):
        pref = "unsloth"

    if pref == "1minai":
        base_url, default_om, om_key = resolve_1minai_config(role=norm_role)
        if not om_key:
            raise RuntimeError("Clé API 1min.ai manquante (ONEMINAI_API_KEY).")
        target_om = (
            model_override.strip()
            if (model_override and is_1minai_compatible_model_override(model_override))
            else default_om
        )
        try:
            messages = build_openai_messages(prompt, system_prompt=system_prompt, history_messages=history_messages)
            om_txt, _, _ = await call_1minai_stateless_async(
                target_om,
                messages,
                base_url=base_url,
                api_key=om_key,
                temperature=float(kwargs.get("temperature", 0.1 if norm_role in ("index", "audit") else 0.2)),
                max_tokens=int(kwargs.get("max_tokens", 8192 if norm_role == "index" else 4096)),
                timeout_s=60.0 if norm_role in ("index", "audit") else 30.0,
            )
            if tracker is not None:
                tracker.record_success("1minai", target_om)
            return om_txt
        except Exception as ome:
            if tracker is not None:
                tracker.record_failure("1minai", target_om, format_gemini_error(ome))
            raise

    if pref in ("auto", "gemini"):
        res, _ = await _call_gemini_chat(
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            model_name=model_override if is_gemini_model_name(model_override) else os.environ.get("RAG_DEFAULT_MODEL"),
            thinking_level_str=os.environ.get("RAG_DEFAULT_THINKING_LEVEL", "low"),
            role=role,
            tracker=tracker,
            wait_on_transient=False,
        )
        if res:
            return res
        if pref == "gemini":
            detail = tracker.format_summary() if tracker else "Cascade Gemini indisponible"
            raise RuntimeError(f"API Gemini indisponible ou quota épuisé ({detail})")

    if pref == "auto" and kwargs.get("keyword_extraction"):
        prompt_lower = (prompt or "").lower()
        if "high_level_keywords" in prompt_lower and "low_level_keywords" in prompt_lower:
            hl, ll = extract_lexical_keywords(prompt)
            return json.dumps({"high_level_keywords": hl, "low_level_keywords": ll}, ensure_ascii=False)

    # Palier 2 QA / Audit : passerelle 1min.ai (mistral-small-2603 par defaut)
    if pref == "auto" and norm_role in ("qa", "audit"):
        om_sess = _get_oneminai_session(norm_role, model_override=model_override)
        if om_sess.is_available:
            om_txt = await om_sess.call(
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                temperature=kwargs.get("temperature"),
                max_tokens=kwargs.get("max_tokens", 4096),
                tracker=tracker,
            )
            if om_txt:
                return om_txt

    # Palier 3 local adapte au role : QA / Audit -> Ollama gemma4:26b (repli qwen3.8:27b-mlx) ; Index -> qwen3.8:27b-mlx
    if pref in ("auto", "ollama"):
        o_txt = await _try_ollama_role_chat(
            prompt, role=role, model_override=model_override, system_prompt=system_prompt,
            history_messages=history_messages, tracker=tracker, kwargs=kwargs,
        )
        if o_txt:
            return o_txt
        if pref == "ollama":
            detail = tracker.format_summary() if tracker else OLLAMA_BASE_URL
            raise RuntimeError(f"Ollama indisponible ({detail})")

    if pref in ("auto", "unsloth"):
        u_txt = await _try_unsloth_chat(
            prompt, model_override=model_override, system_prompt=system_prompt,
            history_messages=history_messages, tracker=tracker, kwargs=kwargs,
        )
        if u_txt:
            return u_txt
        if pref == "unsloth":
            raise RuntimeError(f"Unsloth Studio indisponible sur {UNSLOTH_BASE_URL}")

    or_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if pref in ("auto", "openrouter") and or_key:
        target_or = model_override if (model_override and not is_gemini_model_name(model_override)) else DEFAULT_OPENROUTER_MODEL
        try:
            text = await openai_complete_if_cache(
                target_or,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                base_url="https://openrouter.ai/api/v1",
                api_key=or_key,
            )
            if text and str(text).strip():
                if tracker is not None:
                    tracker.record_success("openrouter", target_or)
                return str(text)
        except Exception as ore:
            if tracker is not None:
                tracker.record_failure("openrouter", target_or, format_gemini_error(ore))
            if pref == "openrouter":
                raise

    detail = tracker.format_summary() if tracker else f"{UNSLOTH_BASE_URL} / {OLLAMA_BASE_URL}"
    raise RuntimeError(f"Aucun backend LLM joignable ({detail})")


async def get_rag() -> LightRAG:
    """Retourne l'instance LightRAG avec rechargement automatique si mise a jour disque."""
    global _rag_instance, _rag_disk_path, _rag_disk_stamp
    async with _get_rag_reload_lock():
        target_db = str(DB_PATH)
        disk_stamp = compute_rag_disk_stamp(DB_PATH)

        if _rag_instance is not None:
            if target_db == _rag_disk_path and disk_stamp == _rag_disk_stamp:
                return _rag_instance
            if target_db == _rag_disk_path and is_indexing_lock_active(DB_PATH):
                print(
                    "ℹ️ Indexation externe en cours — conservation temporaire de l'instance RAG en mémoire.",
                    file=sys.stderr,
                )
                return _rag_instance
            print(
                "🔄 Rechargement automatique du RAG (mise à jour disque détectée)...",
                file=sys.stderr,
            )
            old_rag = _rag_instance
            _rag_instance = None
            if hasattr(old_rag, "finalize_storages"):
                try:
                    await old_rag.finalize_storages()
                except Exception as fin_err:
                    print(f"⚠️ Erreur finalize_storages lors du rechargement : {fin_err}", file=sys.stderr)

        print(f"🔍 Initialisation RAG sur : {DB_PATH}", file=sys.stderr)
        if not DB_PATH.exists():
            print(f"❌ DOSSIER DB INTROUVABLE : {DB_PATH}", file=sys.stderr)
            raise RuntimeError(f"Base de données introuvable : {DB_PATH}")

        # Vérification sommaire du contenu
        kv_file = DB_PATH / "kv_store_full_docs.json"
        if kv_file.exists():
            size = kv_file.stat().st_size
            print(f"📊 Base trouvée : {size} octets de documents.", file=sys.stderr)
        else:
            print("⚠️ ATTENTION : La base semble vide (pas de kv_store_full_docs.json)", file=sys.stderr)

        chunk_size = int(os.environ.get("CHUNK_SIZE", "1600"))
        chunk_overlap = int(os.environ.get("CHUNK_OVERLAP_SIZE", "150"))
        force_summary_merge = max(8, int(os.environ.get("RAG_FORCE_LLM_SUMMARY_ON_MERGE", "24")))
        rag = LightRAG(
            working_dir=target_db,
            llm_model_func=llm_func,
            embedding_func=embedding_func,
            rerank_model_func=fastembed_rerank_func if HAS_RERANKER else None,
            chunking_func=chunking_markdown_anchored,
            chunk_token_size=chunk_size,
            chunk_overlap_token_size=chunk_overlap,
            force_llm_summary_on_merge=force_summary_merge,
            llm_model_max_async=max(1, int(os.environ.get("LLM_MAX_ASYNC", "1"))),
            default_llm_timeout=600,
            addon_params={"language": "French"},
        )
        rag.llm_response_timeout = 1200
        await rag.initialize_storages()
        _rag_instance = rag
        _rag_disk_path = target_db
        _rag_disk_stamp = compute_rag_disk_stamp(DB_PATH)
        print("✅ Serveur RAG prêt et initialisé.", file=sys.stderr)
        return _rag_instance


# ─── Définition des Audits & Résolutions ──────────────────────────────────────

QA_PROMPT = (
    "\n\nIMPORTANT: Pour chaque incohérence ou chiffre divergent identifié, tu dois d'abord lister clairement les noms des fichiers sources qui se contredisent. "
    "Ensuite, tu DOIS obligatoirement générer une question précise pour l'utilisateur. Tu dois formater cette question EXACTEMENT de cette manière sur une nouvelle ligne : "
    "'**Question :** [Ta question ici]'. Ne rajoute aucun texte après la question."
)

AUDIT_TOPICS = {
    "squelette_masse": (
        "1. Squelette (Masse & Moteurs)",
        "Établis un tableau comparatif de la Masse Totale et du Nombre total de Moteurs RobStride cités dans les différents fichiers. Relève toute contradiction." + QA_PROMPT
    ),
    "cinematique_moteurs": (
        "2. Cinématique (Moteurs par Axe)",
        "Vérifie si le modèle de moteur associé à chaque articulation (Épaule, Coude, Poignet, Hanche, Genou, Cheville) est cohérent dans toute la doc. Signale si des anciens modèles apparaissent encore." + QA_PROMPT
    ),
    "electronique_bus": (
        "3. Électronique (Bus & Puissance)",
        "Vérifie la cohérence du bus CAN (nombre de moteurs par bus) et de l'alimentation (Tension batterie) entre les synthèses et le guide électronique." + QA_PROMPT
    ),
    "perception_ia": (
        "4. Perception & IA",
        "Vérifie si les spécifications de la caméra OAK-D, de l'IMU principale et de la Jetson Orin Nano sont identiques partout. Note les divergences sur le matériel audio." + QA_PROMPT
    ),
}

def extract_questions_from_text(text: str) -> list[dict]:
    questions = []
    sections = re.split(r'\n##+ ', text)
    for section in sections:
        lines = section.split('\n')
        if not lines:
            continue
        section_title = lines[0].strip().replace('#', '').strip()
        for line in lines:
            stripped = line.strip()
            if 'Question' in stripped and ':' in stripped:
                match = re.search(r'Question\s*:\s*\*\*?\s*(.*)', stripped)
                if match:
                    q_text = match.group(1).strip()
                    if q_text:
                        questions.append({
                            "section": section_title,
                            "question": q_text,
                            "answer": ""
                        })
    for i, q in enumerate(questions, 1):
        q["id"] = i
    return questions

# ─── Définition des Outils MCP ────────────────────────────────────────────────

TOOLS = [
    Tool(
        name="rag_search",
        description=(
            "Recherche sémantique dans toute la documentation D-Bot (fichiers Markdown et code Python). "
            "Utilise un mode hybride combinant similarité vectorielle et graphe de connaissances. "
            "Idéal pour des questions générales sur le robot, ses composants ou son fonctionnement."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "La question ou le sujet à rechercher dans la documentation D-Bot."
                },
                "llm_mode": {
                    "type": "string",
                    "enum": ["antigravity", "internal", "auto"],
                    "description": "Choix du moteur : 'auto' (défaut : Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b avec repli Antigravity), 'internal' (synthèse LLM stricte), ou 'antigravity' (extraits classés sans appel LLM).",
                    "default": "auto"
                },
                "provider": {
                    "type": "string",
                    "enum": ["auto", "gemini", "1minai", "ollama", "unsloth", "openrouter"],
                    "description": "Fournisseur LLM en mode internal/auto (défaut: auto = Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b).",
                    "default": "auto"
                },
                "model": {
                    "type": "string",
                    "description": "Modèle spécifique optionnel en mode internal/auto (ex: 'gemini-3.1-flash-lite', 'mistral-small-2603', 'gemma4:26b')."
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="rag_analyze_impact",
        description=(
            "Analyse les relations de cause à effet entre les composants du robot D-Bot. "
            "Utilise le graphe de connaissances pour relier des informations provenant de fichiers différents. "
            "UTILISEZ CET OUTIL pour des questions du type : "
            "'Si X change, quel impact sur Y ?' ou 'Quels composants sont affectés par Z ?'. "
            "Exemples : impact d'une augmentation de masse des bras sur la vitesse de course, "
            "impact d'un changement de moteur sur l'autonomie batterie."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "scenario": {
                    "type": "string",
                    "description": "Le scénario d'impact à analyser. Soyez précis et décrivez la cause ET l'effet potentiel recherché."
                },
                "context": {
                    "type": "string",
                    "description": "Contexte optionnel supplémentaire pour affiner l'analyse.",
                    "default": ""
                },
                "llm_mode": {
                    "type": "string",
                    "enum": ["antigravity", "internal", "auto"],
                    "description": "Choix du moteur : 'auto' (défaut : Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b avec repli Antigravity), 'internal' (synthèse LLM stricte), ou 'antigravity' (extrait brut du graphe).",
                    "default": "auto"
                },
                "provider": {
                    "type": "string",
                    "enum": ["auto", "gemini", "1minai", "ollama", "unsloth", "openrouter"],
                    "description": "Fournisseur LLM en mode internal/auto (défaut: auto = Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b).",
                    "default": "auto"
                },
                "model": {
                    "type": "string",
                    "description": "Modèle spécifique optionnel en mode internal/auto."
                }
            },
            "required": ["scenario"]
        }
    ),
    Tool(
        name="rag_get_context",
        description=(
            "Récupère le contexte détaillé et précis autour d'un sujet spécifique dans la documentation D-Bot. "
            "Mode 'local' : retourne les passages les plus pertinents sur un sujet précis. "
            "Idéal pour : spécifications techniques d'un composant, extraits de code, valeurs numériques précises."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Le sujet précis dont vous voulez le contexte (ex: 'moteur RS06 couple max', 'code audio stt.py', 'cheville cardan')."
                }
            },
            "required": ["topic"]
        }
    ),
    Tool(
        name="rag_list_topics",
        description=(
            "Liste les grandes thématiques couvertes dans la documentation D-Bot indexée. "
            "Utile pour savoir quels domaines sont documentés avant de faire une recherche plus précise."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domaine optionnel à explorer (ex: 'mécanique', 'audio', 'IA', 'moteurs', 'batterie'). Laissez vide pour tout lister.",
                    "default": ""
                }
            }
        }
    ),
    Tool(
        name="rag_audit_integrity",
        description=(
            "Audite la cohérence et détecte les contradictions/désynchronisations dans la documentation D-Bot via le Graph-RAG. "
            "Compare les valeurs numériques, références de moteurs, masses, bus CAN ou composants entre tous les fichiers. "
            "Peut auditer un domaine précis (rapide) ou toute la base, et générer les questions d'arbitrage."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "scope": {
                    "type": "string",
                    "enum": ["all", "squelette_masse", "cinematique_moteurs", "electronique_bus", "perception_ia", "custom"],
                    "description": "Domaine à auditer. Privilégier un domaine précis pour un résultat rapide (15-25s) ou 'all' pour l'audit complet.",
                    "default": "all"
                },
                "llm_mode": {
                    "type": "string",
                    "enum": ["antigravity", "internal", "auto"],
                    "description": "Choix du moteur d'intelligence : 'auto' (défaut : Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b avec repli Antigravity), 'internal' (synthèse LLM stricte), ou 'antigravity' (extraits bruts).",
                    "default": "auto"
                },
                "provider": {
                    "type": "string",
                    "enum": ["auto", "gemini", "1minai", "ollama", "unsloth", "openrouter"],
                    "description": "Fournisseur LLM en mode internal/auto (défaut: auto = Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b).",
                    "default": "auto"
                },
                "model": {
                    "type": "string",
                    "description": "Modèle spécifique optionnel en mode internal/auto."
                },
                "custom_query": {
                    "type": "string",
                    "description": "La règle ou l'incohérence spécifique à auditer si scope='custom'.",
                    "default": ""
                },
                "save_report": {
                    "type": "boolean",
                    "description": "Si true, écrit le rapport dans annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md et génère AUDIT_QUESTION_REPONSE.json.",
                    "default": True
                },
                "clear_cache": {
                    "type": "boolean",
                    "description": "Si true, vide le cache LLM pour forcer une ré-analyse neuve.",
                    "default": False
                }
            }
        }
    ),
    Tool(
        name="rag_resolve_audit",
        description=(
            "Résout les contradictions d'audit en préparant un plan de remédiation documenté. "
            "Prend les décisions techniques validées, interroge la base RAG pour identifier tous les fichiers contenant encore les anciennes valeurs, "
            "et génère le plan de correction (PLAN_CORRECTION.md) prêt à être appliqué après validation utilisateur."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "decisions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Liste de décisions techniques officielles à appliquer (ex: ['Masse bride = 202.3 g', 'Moteur épaule = RS-04']).",
                    "default": []
                },
                "from_json": {
                    "type": "boolean",
                    "description": "Si true, charge également les décisions renseignées dans AUDIT_QUESTION_REPONSE.json.",
                    "default": False
                },
                "save_plan": {
                    "type": "boolean",
                    "description": "Si true, sauvegarde le plan dans annexes/Outils_de_Travail/RAG/PLAN_CORRECTION.md et le prompt de cadrage.",
                    "default": True
                }
            }
        }
    ),
    Tool(
        name="rag_index_document",
        description=(
            "Indexe ou réindexe un document spécifique (Markdown, Python, PDF, schéma SVG XML, image PNG/JPG) dans la base RAG locale au fil de l'eau. "
            "En mode auto : cascade complète Gemini Free Tier (gemini-3.8-flash, ..., gemini-2.5-flash) puis repli automatique sur Ollama local (qwen3.8:27b-mlx, think=False ; palier 1min.ai optionnel si RAG_AUTO_1MINAI=true)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Chemin absolu ou relatif vers le fichier à indexer (ex: '01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_Synthese_Mecanique_Torse.md')."
                },
                "provider": {
                    "type": "string",
                    "enum": ["auto", "gemini", "1minai", "ollama"],
                    "description": "Fournisseur LLM : 'auto' (Gemini Free Tier -> Ollama qwen3.8:27b-mlx, 0 crédit), 'gemini', '1minai' (explicite, défaut mistral-small-latest), ou 'ollama' (100% local).",
                    "default": "auto"
                },
                "thinking_level": {
                    "type": "string",
                    "enum": ["minimal", "low", "medium", "high"],
                    "description": "Niveau d'effort de raisonnement Gemini (défaut: 'low', ignoré en mode ollama où think=False).",
                    "default": "low"
                },
                "model": {
                    "type": "string",
                    "description": "Modèle spécifique (défaut: cascade Gemini Free Tier puis 'qwen3.8:27b-mlx' en repli Ollama)."
                }
            },
            "required": ["file_path"]
        }
    ),
    Tool(
        name="rag_prepare_agent_index",
        description=(
            "Prépare un lot d'indexation LightRAG (0 LLM tiers, 0 crédit, 0 RAM Ollama) pour traitement direct par "
            "l'agent Antigravity : découpe les documents en chunks exacts (1600/150 tokens), repère les images VLM "
            "à lire visuellement, et attribue à chaque chunk un niveau de thinking adapté ('flash' standard vs "
            "'inherit' pour Niveau 1 / PDF / images, jamais extra_high). À finaliser ensuite avec rag_commit_agent_index."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Liste optionnelle de chemins (relatifs à Documentation/ ou absolus). Si omis, scanne uniquement les fichiers modifiés, nouveaux ou supprimés."
                },
                "effort_profile": {
                    "type": "string",
                    "enum": ["fast", "balanced", "thorough"],
                    "description": "Niveau de thinking adapté (jamais extra_high) : 'balanced' (défaut optimal : flash sur texte standard, inherit sur Niveau 1/PDF/VLM), 'fast' (flash partout), ou 'thorough' (inherit borné sans extra_high).",
                    "default": "balanced"
                },
                "include_inline_chunks": {
                    "type": "boolean",
                    "description": "Inclut le texte des chunks directement dans la réponse (défaut automatique : true si <= 12 chunks, sinon chemin manifest.json)."
                },
                "job_id": {
                    "type": "string",
                    "description": "Identifiant de job optionnel (généré automatiquement sinon)."
                }
            }
        }
    ),
    Tool(
        name="rag_commit_agent_index",
        description=(
            "Valide (linter <|#|> / <|COMPLETE|> / 0 dollar / SHA-256) et injecte atomiquement dans le vrai pipeline "
            "LightRAG.ainsert() les extractions produites par Antigravity suite à rag_prepare_agent_index, "
            "sans aucun appel LLM tiers (purge, embeddings CPU, graphe et indexed_files.json préservés)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "Identifiant job_id (ou chemin vers manifest.json) retourné par rag_prepare_agent_index."
                },
                "extractions": {
                    "type": "object",
                    "description": "Objet JSON inline optionnel {chunk_extractions, vlm_descriptions, vlm_extractions, entity_summaries} fusionné avec extractions.json."
                },
                "extractions_path": {
                    "type": "string",
                    "description": "Chemin JSON alternatif si les extractions n'ont pas été écrites dans extractions.json du job ni passées inline."
                },
                "apply_deletes": {
                    "type": "boolean",
                    "description": "Applique aussi la purge des fichiers supprimés ou archivés (défaut: true).",
                    "default": True
                },
                "force_llm_summary_on_merge": {
                    "type": "integer",
                    "description": "Seuil de fusions avant résumé déterministe local (défaut: 24, 0 appel LLM tiers).",
                    "default": 24
                },
                "cleanup": {
                    "type": "boolean",
                    "description": "Supprime les fichiers temporaires du job après commit réussi (défaut: true).",
                    "default": True
                },
                "allow_stale": {
                    "type": "boolean",
                    "description": "Autorise le commit même si un fichier source a été réédité après préparation (défaut: false).",
                    "default": False
                }
            },
            "required": ["job_id"]
        }
    ),
]

# ─── Serveur MCP ──────────────────────────────────────────────────────────────

server = Server("dbot-rag")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "rag_prepare_agent_index":
        try:
            eff_profile = resolve_effort_profile(arguments.get("effort_profile", "balanced"))
            profile_cfg = AGENT_EFFORT_PROFILES[eff_profile]
            files_arg = arguments.get("files")
            raw_files = [str(f) for f in files_arg] if isinstance(files_arg, list) and files_arg else None
            prep = prepare_agent_bundle(
                docs_root=DOCS_ROOT,
                db_path=DB_PATH,
                files=raw_files,
                effort_profile=eff_profile,
                chunk_size=int(os.environ.get("CHUNK_SIZE", "1600")),
                chunk_overlap=int(os.environ.get("CHUNK_OVERLAP_SIZE", "150")),
                job_id=arguments.get("job_id"),
            )
            man = prep["manifest"]
            chunks = man["chunks"]
            images = man["images"]
            inline_opt = arguments.get("include_inline_chunks")
            show_inline = (len(chunks) <= 12) if inline_opt is None else bool(inline_opt)

            payload_summary: dict = {
                "job_id": prep["job_id"],
                "manifest_path": prep["manifest_path"],
                "extractions_path": prep["extractions_path"],
                "effort_profile": man["effort_profile"],
                "thinking_directive": profile_cfg["thinking_directive"],
                "tier_counts": man["effort_summary"]["tier_counts"],
                "documents_count": len(man["documents"]),
                "chunks_count": len(chunks),
                "images_count": len(images),
                "to_delete_count": len(man["to_delete"]),
                "orphan_ids_count": len(man["orphan_ids"]),
                "missing_files": man["missing_files"],
                "format_contract": {
                    "entity_row": f"entity{TUPLE_DELIMITER}<entity_name>{TUPLE_DELIMITER}<entity_type>{TUPLE_DELIMITER}<entity_description>",
                    "relation_row": f"relation{TUPLE_DELIMITER}<source_entity>{TUPLE_DELIMITER}<target_entity>{TUPLE_DELIMITER}<keywords_virgules>{TUPLE_DELIMITER}<relationship_description>",
                    "completion_delimiter": COMPLETION_DELIMITER,
                    "rules": [
                        "Pas de symbole dollar ni de syntaxe LaTeX.",
                        "Pas de extra_high : extraction directe 1 passe selon recommended_subagent_model (flash vs inherit).",
                    ],
                },
                "images": images,
            }
            if show_inline:
                payload_summary["chunks"] = chunks
            else:
                payload_summary["chunks_preview"] = [
                    {k: ch[k] for k in ("chunk_hash", "doc_rel", "chunk_index", "total_doc_chunks", "tokens", "recommended_subagent_model", "effort_tier")}
                    for ch in chunks
                ]
            return [TextContent(type="text", text=json.dumps(payload_summary, ensure_ascii=False, indent=2))]
        except Exception as prep_err:
            return [TextContent(type="text", text=f"❌ Erreur rag_prepare_agent_index : {prep_err}")]

    try:
        rag = await get_rag()
    except RuntimeError as e:
        return [TextContent(type="text", text=f"❌ Erreur : {e}")]

    try:
        if name == "rag_audit_integrity":
            scope = arguments.get("scope", "all")
            custom_query = arguments.get("custom_query", "")
            save_report = arguments.get("save_report", True)
            clear_cache = arguments.get("clear_cache", False)

            if clear_cache:
                cache_path = DB_PATH / "llm_response_cache.json"
                if cache_path.exists():
                    try:
                        cache_path.unlink()
                        print("🧹 Cache LLM vidé.", file=sys.stderr)
                    except Exception as ce:
                        print(f"⚠️ Erreur purge cache: {ce}", file=sys.stderr)

            audits_to_run = []
            if scope == "custom":
                if not custom_query:
                    return [TextContent(type="text", text="❌ 'custom_query' est obligatoire lorsque scope='custom'.")]
                audits_to_run.append(("Audit Personnalisé", custom_query + QA_PROMPT))
            elif scope == "all":
                for k, (title, q) in AUDIT_TOPICS.items():
                    audits_to_run.append((title, q))
            elif scope in AUDIT_TOPICS:
                audits_to_run.append(AUDIT_TOPICS[scope])
            else:
                return [TextContent(type="text", text=f"❌ Scope inconnu : {scope}. Options valides : 'all', 'squelette_masse', 'cinematique_moteurs', 'electronique_bus', 'perception_ia', 'custom'.")]

            llm_mode = arguments.get("llm_mode", "auto").lower()
            if llm_mode not in ("antigravity", "internal", "auto"):
                llm_mode = "auto"
            prov_arg = (arguments.get("provider") or "").strip().lower() or None
            model_arg = (arguments.get("model") or "").strip() or None
            audit_tracker = ModelExecutionTracker(
                role="audit",
                default_no_llm_label=(
                    f"Cache LightRAG (réponse en cache — 0 appel LLM [mode {llm_mode}])"
                    if llm_mode in ("internal", "auto")
                    else "Aucun LLM (extraction graphe/vecteur — mode antigravity)"
                ),
            )

            from datetime import datetime
            section_blocks = []
            tok_role = _CURRENT_RAG_ROLE.set("audit")
            tok_trk = _CURRENT_TRACKER.set(audit_tracker)
            tok_prov = _CURRENT_PROVIDER_OVERRIDE.set(prov_arg)
            tok_mod = _CURRENT_MODEL_OVERRIDE.set(model_arg)
            try:
                for title, q_str in audits_to_run:
                    # Mode Internal : cascade Gemini -> repli local Qwen3.8 (Unsloth/Ollama) -> OpenRouter
                    if llm_mode in ("internal", "auto"):
                        try:
                            ans = await rag.aquery(q_str, param=QueryParam(mode="global", enable_rerank=False))
                            section_blocks.append(f"## {title} [Synthèse LLM Interne]\n\n{ans}\n\n---\n")
                            continue
                        except Exception as audit_err:
                            err_msg = str(audit_err)
                            if llm_mode == "internal":
                                section_blocks.append(
                                    f"## {title} [Mode: internal]\n\n"
                                    f"❌ Impossible de joindre le modèle de synthèse LLM ({err_msg}).\n\n---\n"
                                )
                                continue
                            else:
                                # Mode auto : fallback transparent sur le mode Antigravity
                                audit_tracker.default_no_llm_label = "Aucun LLM (extraction graphe/vecteur — repli antigravity)"
                                audit_tracker.fallback_note = audit_tracker.default_no_llm_label
                                section_blocks.append(f"> ℹ️ *LLM interne non joignable ({err_msg[:80]}...). Basculement sur l'analyse Antigravity.*\n")

                    # Mode Antigravity (ou Fallback Auto) :
                    # Extraction du corpus multi-fichiers pour analyse par l'agent Antigravity
                    try:
                        res = await rag.aquery_data(q_str, param=QueryParam(mode="naive"))
                        chunks = res.get("data", {}).get("chunks", []) if res.get("status") == "success" else []

                        try:
                            chunks = await fast_rerank_func(q_str, chunks)
                        except Exception:
                            pass

                        section_md = [
                            f"## {title} [Analyse par l'Agent Antigravity]",
                            "> **Consigne pour l'Agent Antigravity** : Analyse ce corpus multi-sources extrait de la documentation. "
                            "Identifie les divergences et contradictions (masses, cotes, références moteurs, bus CAN). "
                            "Cite les fichiers sources qui se contredisent et génère les questions d'arbitrage au format '**Question :** ...'.\n",
                            f"### Données Multi-Fichiers Extraites du RAG ({len(chunks)} sources candidates) :\n"
                        ]
                        for idx, chunk in enumerate(chunks[:12]):
                            src = chunk.get("file_path", "Source inconnue")
                            txt = chunk.get("content", "").strip()
                            sc = chunk.get("rerank_score", 0.0)
                            sc_str = f" [Score: {sc:.2f}]" if sc > 0 else ""
                            section_md.append(f"**[Extrait {idx+1}: {src}]**{sc_str}\n```text\n{txt}\n```\n")

                        section_blocks.append("\n".join(section_md) + "\n---\n")
                    except Exception as ex:
                        section_blocks.append(f"## {title}\n\n❌ Erreur d'extraction des données RAG : {ex}\n\n---\n")
            finally:
                _CURRENT_RAG_ROLE.reset(tok_role)
                _CURRENT_TRACKER.reset(tok_trk)
                _CURRENT_PROVIDER_OVERRIDE.reset(tok_prov)
                _CURRENT_MODEL_OVERRIDE.reset(tok_mod)

            results_text = [
                f"# 🛡️ Dossier d'Audit d'Intégrité D-Bot [Scope: {scope}]",
                f"> **Date de génération** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"> **Mode d'intelligence** : `{llm_mode}`",
                f"{audit_tracker.format_markdown_line()}\n",
                *section_blocks,
            ]
            full_report = "\n".join(results_text)

            if save_report:
                try:
                    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
                    REPORT_PATH.write_text(full_report, encoding="utf-8")
                    extracted_qs = extract_questions_from_text(full_report)
                    QUESTIONS_JSON_PATH.write_text(json.dumps(extracted_qs, ensure_ascii=False, indent=2), encoding="utf-8")
                    full_report += f"\n\n*(Rapport enregistré dans `{REPORT_PATH}` et `{QUESTIONS_JSON_PATH}`)*"
                except Exception as save_err:
                    full_report += f"\n\n⚠️ Impossible de sauvegarder les fichiers de rapport : {save_err}"

            return [TextContent(type="text", text=full_report)]

        elif name == "rag_resolve_audit":
            decisions = arguments.get("decisions", [])
            from_json = arguments.get("from_json", False)
            save_plan = arguments.get("save_plan", True)

            loaded_answers = []
            if from_json and QUESTIONS_JSON_PATH.exists():
                try:
                    with open(QUESTIONS_JSON_PATH, "r", encoding="utf-8") as qf:
                        q_data = json.load(qf)
                        for item in q_data:
                            ans = item.get("answer", "").strip()
                            if ans:
                                loaded_answers.append(f"- Décision pour '{item.get('section', 'Sujet')}' : {ans}")
                except Exception as je:
                    print(f"⚠️ Erreur lecture JSON: {je}", file=sys.stderr)

            if isinstance(decisions, str):
                decisions = [decisions]
            for d in decisions:
                if d and d.strip():
                    loaded_answers.append(f"- Décision explicite : {d.strip()}")

            if not loaded_answers:
                return [TextContent(type="text", text=(
                    "❌ Aucune décision technique trouvée.\n"
                    "Veuillez fournir une liste de décisions via le paramètre 'decisions' "
                    "ou renseigner les champs 'answer' dans AUDIT_QUESTION_REPONSE.json avec from_json=True."
                ))]

            # Pour chaque décision, interroger le RAG en mode retrieval pour localiser les fichiers candidats
            candidate_files_by_decision = {}
            for dec in loaded_answers:
                search_query = dec.split(":")[-1].strip()
                try:
                    res = await rag.aquery_data(search_query, param=QueryParam(mode="naive"))
                    chunks = res.get("data", {}).get("chunks", []) if res.get("status") == "success" else []
                    files = []
                    for c in chunks[:5]:
                        fp = c.get("file_path")
                        if fp and fp != "unknown_source" and fp not in files:
                            files.append(fp)
                    candidate_files_by_decision[dec] = files
                except Exception as se:
                    candidate_files_by_decision[dec] = [f"Erreur recherche : {se}"]

            from datetime import datetime
            plan_lines = [
                "# 📋 PLAN_CORRECTION — Plan de Remédiation Documentaire D-Bot",
                f"> **Date de génération** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "> **Statut** : En attente de validation utilisateur avant modification\n",
                "## 1. Décisions Techniques Officielles Validées\n"
            ]
            for dec in loaded_answers:
                plan_lines.append(f"{dec}")

            plan_lines.append("\n## 2. Cartographie des Fichiers Identifiés à Corriger (RAG)\n")
            for dec, files in candidate_files_by_decision.items():
                plan_lines.append(f"### {dec}")
                if files:
                    for f in files:
                        plan_lines.append(f"- [ ] `{f}`")
                else:
                    plan_lines.append("- *(Aucun fichier source direct identifié automatiquement)*")
                plan_lines.append("")

            plan_lines.append(
                "## 3. Règles d'Application Strictes\n"
                "1. **Périmètre Officiel** : Ne modifier que les fichiers de Niveau 1 (spécifications actives, BOM, dossiers techniques). Ne jamais altérer les études d'hypothèses historiques (`STUDY_`).\n"
                "2. **Cohérence Mathématique** : Mettre à jour les calculs dépendants (couples, contraintes, autonomie) associés à la nouvelle valeur.\n"
                "3. **Validation Requise** : L'agent ne modifie aucun fichier avant confirmation explicite ('OK') de l'utilisateur sur ce plan.\n"
            )

            full_plan = "\n".join(plan_lines)

            prompt_content = f"""Lis le fichier d'audit `{REPORT_PATH}`. 
J'ai analysé les incohérences. Voici mes décisions techniques officielles pour mettre à jour la documentation :

{chr(10).join(loaded_answers)}

Ta mission :
1. Scanne l'ensemble de la documentation pour localiser tous les fichiers contenant les anciennes valeurs contradictoires.
2. RÈGLE D'OR : Ne touche jamais aux valeurs situées dans des études d'hypothèses ou brouillons. Uniquement les spécifications de la version officielle.
3. PRÉPARE UN PLAN DOCUMENTÉ dans `annexes/Outils_de_Travail/RAG/PLAN_CORRECTION.md`.
4. ATTENDS MA VALIDATION avant de modifier le moindre document.
5. Une fois validé, applique les corrections et recalcule les équations impactées.
"""

            if save_plan:
                try:
                    PLAN_CORRECTION_PATH.parent.mkdir(parents=True, exist_ok=True)
                    PLAN_CORRECTION_PATH.write_text(full_plan, encoding="utf-8")
                    PROMPT_CORRECTION_PATH.write_text(prompt_content, encoding="utf-8")
                    full_plan += f"\n\n*(Plan sauvegardé dans `{PLAN_CORRECTION_PATH}` et prompt dans `{PROMPT_CORRECTION_PATH}`)*"
                except Exception as save_err:
                    full_plan += f"\n\n⚠️ Impossible de sauvegarder les fichiers de plan : {save_err}"

            return [TextContent(type="text", text=full_plan)]

        elif name == "rag_index_document":
            file_path_str = arguments.get("file_path", "").strip()
            if not file_path_str:
                return [TextContent(type="text", text="❌ 'file_path' est obligatoire.")]
            if is_indexing_lock_active(DB_PATH):
                return [TextContent(type="text", text=f"⏳ Une indexation externe est déjà en cours sur `{DB_PATH}`. Réessayez après sa complétion.")]

            # Résolution du chemin
            raw_path = Path(file_path_str)
            target_path = raw_path if raw_path.is_absolute() else (DOCS_ROOT / raw_path)
            if not target_path.exists():
                alt_path = DOCS_ROOT / file_path_str.lstrip("/")
                if alt_path.exists():
                    target_path = alt_path
                else:
                    return [TextContent(type="text", text=f"❌ Fichier introuvable : {target_path}")]

            target_path = target_path.resolve()
            try:
                relative = str(target_path.relative_to(DOCS_ROOT.resolve()))
            except Exception:
                relative = target_path.name

            provider_req = (arguments.get("provider") or "auto").strip().lower()
            if provider_req not in ("auto", "ollama", "gemini", "1minai"):
                provider_req = "auto"
            thinking_level_str = arguments.get("thinking_level", "low").lower()
            explicit_model = arguments.get("model")
            idx_tracker = ModelExecutionTracker(role="index")

            ext = target_path.suffix.lower()
            used_engine = provider_req
            v_sections: list[dict] | None = None
            file_norm_sha = ""
            if ext == ".pdf":
                try:
                    content = extract_pdf_text_cached(target_path, db_path=DB_PATH)
                except Exception as pe:
                    return [TextContent(type="text", text=f"❌ Erreur lecture PDF {target_path.name} : {pe}")]
                header = f"---\nFichier: {relative}\nType: Document PDF\nProjet: D-Bot\n---\n\n"
                full_content = header + f"# Document PDF : {target_path.name}\n\n" + content
                file_norm_sha = compute_normalized_sha256(full_content, ext=".pdf")
            elif ext == ".svg":
                try:
                    svg_text = extract_svg_text(target_path)
                except Exception as se:
                    return [TextContent(type="text", text=f"❌ Erreur lecture XML SVG {target_path.name} : {se}")]
                if not svg_text.strip():
                    return [TextContent(type="text", text=f"⚠️ Aucun texte exploitable dans le SVG {target_path.name}.")]
                header = f"---\nFichier: {relative}\nType: Schéma Vectoriel SVG (Texte XML)\nProjet: D-Bot\n---\n\n"
                full_content = header + f"# Schéma Technique SVG : {target_path.name}\n\n" + svg_text
                file_norm_sha = compute_normalized_sha256(svg_text, ext=".svg")
            elif ext in RASTER_VLM_EXTS:
                vlm_desc = None
                if provider_req in ("auto", "gemini") and (client := get_genai_client(timeout_s=get_gemini_timeout_s("index"))) is not None:
                    from PIL import Image
                    from google.genai import types as genai_types
                    img = Image.open(target_path)
                    vlm_models = build_gemini_cascade(
                        "vlm",
                        explicit_model=explicit_model if is_gemini_model_name(explicit_model) else None,
                    )
                    loop = asyncio.get_event_loop()
                    last_vlm_err = ""
                    for g_model in vlm_models:
                        try:
                            g_res = await loop.run_in_executor(
                                None,
                                lambda gm=g_model: client.models.generate_content(
                                    model=gm,
                                    contents=[img, _VLM_TECHNICAL_PROMPT],
                                    config=genai_types.GenerateContentConfig(
                                        thinking_config=genai_types.ThinkingConfig(thinking_budget=100)
                                    ),
                                ),
                            )
                            if g_res and g_res.text:
                                vlm_desc = g_res.text
                                used_engine = f"gemini-vlm ({g_model})"
                                idx_tracker.record_success("gemini-vlm", g_model)
                                break
                        except Exception as ge_vlm:
                            err_txt = format_gemini_error(ge_vlm)
                            if "invalid_argument" in err_txt.lower() and "deadline" not in err_txt.lower():
                                try:
                                    g_retry = await loop.run_in_executor(
                                        None,
                                        lambda gm=g_model: client.models.generate_content(
                                            model=gm,
                                            contents=[img, _VLM_TECHNICAL_PROMPT],
                                        ),
                                    )
                                    if g_retry and g_retry.text:
                                        vlm_desc = g_retry.text
                                        used_engine = f"gemini-vlm ({g_model})"
                                        idx_tracker.record_success("gemini-vlm", g_model)
                                        break
                                except Exception as retry_err:
                                    err_txt = format_gemini_error(retry_err)
                            last_vlm_err = err_txt
                            idx_tracker.record_failure("gemini-vlm", g_model, err_txt)
                    if vlm_desc is None and provider_req == "gemini":
                        return [TextContent(type="text", text=f"❌ Erreur VLM Gemini sur {target_path.name} : {last_vlm_err}")]
                if vlm_desc is None:
                    try:
                        o_model = explicit_model if (explicit_model and not is_gemini_model_name(explicit_model)) else OLLAMA_MODEL
                        if not check_ollama_ready(OLLAMA_BASE_URL, required_model=o_model, timeout=0.4) and RAG_AUTO_START_SERVER:
                            _MANAGED_OLLAMA.model = o_model
                            _MANAGED_OLLAMA.ensure_started()
                        img_b64 = _encode_image_for_ollama(target_path)
                        vlm_desc = await _call_ollama_chat(
                            _VLM_TECHNICAL_PROMPT,
                            model_name=o_model,
                            images=[img_b64],
                            num_ctx=int(os.environ.get("OLLAMA_VLM_NUM_CTX", "8192")),
                        )
                        used_engine = f"ollama-vlm ({o_model})"
                        idx_tracker.record_success("ollama-vlm", o_model)
                    except Exception as oe_vlm:
                        return [TextContent(type="text", text=f"❌ Erreur VLM sur {target_path.name} : {oe_vlm}")]
                type_label = "Image VLM (Ollama)" if used_engine.startswith("ollama") else "Image VLM"
                header = f"---\nFichier: {relative}\nType: {type_label}\nProjet: D-Bot\n---\n\n"
                full_content = header + f"# Analyse Visuelle et Spécifications Techniques : {target_path.name}\n\n" + vlm_desc
                file_norm_sha = compute_normalized_sha256(full_content, ext=".md")
            else:
                try:
                    content = target_path.read_text(encoding="utf-8")
                except Exception as read_err:
                    return [TextContent(type="text", text=f"❌ Erreur lecture du fichier {target_path.name} : {read_err}")]
                file_norm_sha = compute_normalized_sha256(content, ext=ext)
                if ext == ".md":
                    v_sections = split_markdown_into_virtual_sections(content, relative)
                header = f"---\nFichier: {relative}\nProjet: D-Bot\n---\n\n"
                full_content = header + content

            resolved_engine = [provider_req]
            om_auto_enabled, om_auto_url, om_auto_model, om_auto_key = resolve_1minai_auto_index_target()
            om_state = {"exhausted": not om_auto_enabled, "consecutive_err": 0}
            summary_mode_mcp = os.environ.get("RAG_SUMMARY_MODE", "deterministic").strip().lower()

            async def custom_llm_insert(prompt, system_prompt=None, history_messages=[], **kwargs):
                if summary_mode_mcp == "deterministic" and is_entity_summary_prompt(prompt, history_messages):
                    return deterministic_merge_descriptions(prompt)

                raw_out: str | None = None
                if provider_req in ("auto", "gemini"):
                    g_txt, g_used = await _call_gemini_chat(
                        prompt,
                        system_prompt=system_prompt,
                        history_messages=history_messages,
                        model_name=explicit_model if is_gemini_model_name(explicit_model) else None,
                        thinking_level_str=thinking_level_str,
                        role="index",
                        tracker=idx_tracker,
                        wait_on_transient=True,
                    )
                    if g_txt:
                        resolved_engine[0] = f"Google Gemini API ({g_used}, thinking={thinking_level_str})"
                        raw_out = g_txt
                    elif provider_req == "gemini":
                        raise RuntimeError(f"Échec Gemini API lors de l'indexation de {relative} ({idx_tracker.format_summary()})")

                if raw_out is None and (provider_req == "1minai" or (provider_req == "auto" and not om_state["exhausted"])):
                    if provider_req == "1minai":
                        om_url, om_def_model, om_key = resolve_1minai_config()
                        if not om_key or "<VOTRE_CLE" in om_key:
                            raise RuntimeError(f"ONEMINAI_API_KEY manquante pour indexer {relative}")
                        om_model = (
                            explicit_model.strip()
                            if (explicit_model and not is_gemini_model_name(explicit_model))
                            else om_def_model
                        )
                    else:
                        om_url, om_model, om_key = om_auto_url, om_auto_model, om_auto_key

                    om_messages = []
                    if system_prompt:
                        om_messages.append({"role": "system", "content": system_prompt})
                    for msg in history_messages or []:
                        if isinstance(msg, dict) and "role" in msg and msg.get("content") is not None:
                            om_messages.append({"role": str(msg["role"]), "content": str(msg["content"])})
                    om_messages.append({"role": "user", "content": prompt})
                    try:
                        om_txt, _, _ = await call_1minai_stateless_async(
                            om_model,
                            om_messages,
                            base_url=om_url,
                            api_key=om_key,
                            temperature=0.1 if kwargs.get("temperature") is None else kwargs["temperature"],
                            max_tokens=kwargs.get("max_tokens") or 8192,
                        )
                        om_state["consecutive_err"] = 0
                        idx_tracker.record_success("1minai", om_model)
                        resolved_engine[0] = f"1min.ai ({om_model})"
                        raw_out = om_txt
                    except Exception as om_err:
                        idx_tracker.record_failure("1minai", om_model, str(om_err))
                        if provider_req == "1minai":
                            raise RuntimeError(
                                f"Échec 1min.ai lors de l'indexation de {relative} : {om_err}"
                            ) from om_err
                        om_state["consecutive_err"] += 1
                        if is_1minai_permanent_or_quota_error(str(om_err)) or om_state["consecutive_err"] >= 2:
                            om_state["exhausted"] = True

                if raw_out is None:
                    o_model = explicit_model if (explicit_model and not is_gemini_model_name(explicit_model)) else OLLAMA_MODEL
                    if not check_ollama_ready(OLLAMA_BASE_URL, required_model=o_model, timeout=0.4) and RAG_AUTO_START_SERVER:
                        _MANAGED_OLLAMA.model = o_model
                        _MANAGED_OLLAMA.ensure_started()
                    o_txt = await _call_ollama_chat(
                        prompt,
                        system_prompt=system_prompt,
                        history_messages=history_messages,
                        model_name=o_model,
                        temperature=kwargs.get("temperature", 0.1),
                        max_tokens=kwargs.get("max_tokens", 8192),
                    )
                    idx_tracker.record_success("ollama", o_model)
                    resolved_engine[0] = f"Ollama local ({o_model}, think=False)"
                    raw_out = o_txt

                return sanitize_lightrag_extraction_output(raw_out) if isinstance(raw_out, str) else raw_out

            log_file = DB_PATH / "indexed_files.json"
            log_idx = {}
            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as lf:
                        log_idx = json.load(lf)
                except Exception:
                    pass

            ds_items: list = []
            full_docs_map: dict = {}
            try:
                async with rag.doc_status._storage_lock:
                    ds_items = list(rag.doc_status._data.items())
                try:
                    async with rag.full_docs._storage_lock:
                        full_docs_map = dict(rag.full_docs._data)
                except Exception:
                    pass
            except Exception as pe:
                print(f"Info lecture doc_status pour {relative}: {pe}", file=sys.stderr)

            expected_flat = relative.replace("/", "--") if "/" in relative else f"root--{relative}"

            if v_sections is not None:
                processed_ids = {d_id for d_id, d_data in ds_items if is_doc_processed(d_data)}
                prev_entry = log_idx.get(str(target_path)) if isinstance(log_idx.get(str(target_path)), dict) else {}
                prev_sections = prev_entry.get("sections") if isinstance(prev_entry.get("sections"), dict) else {}
                target_sec_ids = {s["doc_id"] for s in v_sections}

                changed_sections = [
                    s for s in v_sections
                    if not (
                        s["doc_id"] in processed_ids
                        and isinstance(prev_sections.get(s["section_key"]), dict)
                        and prev_sections[s["section_key"]].get("sha256") == s["content_sha256"]
                    )
                ]
                matching_ids: list[str] = []
                changed_sec_keys = {s["section_key"] for s in changed_sections}
                for d_id, d_data in ds_items:
                    fp = d_data.get("file_path", "") or ""
                    fd_entry = full_docs_map.get(d_id)
                    fd_rel = extract_rel_path(fd_entry.get("content", "")) if isinstance(fd_entry, dict) else None
                    if not (fd_rel == relative or fp in (relative, str(target_path), expected_flat)):
                        continue
                    ex_sec = extract_section_key(fd_entry.get("content", "")) if isinstance(fd_entry, dict) else None
                    if d_id not in target_sec_ids or ex_sec in changed_sec_keys or ex_sec is None:
                        matching_ids.append(d_id)

                purged_count = len(matching_ids)
                for old_id in matching_ids:
                    if not old_id.startswith("dup-"):
                        try:
                            await rag.adelete_by_doc_id(old_id)
                        except Exception:
                            pass
                    try:
                        await rag.doc_status.delete([old_id])
                    except Exception:
                        pass

                purged_set = set(matching_ids)
                ds_remaining = {d_id: d_data for d_id, d_data in ds_items if d_id not in purged_set}
                resolved_remaining = {
                    d_id: extract_rel_path(full_docs_map[d_id].get("content", ""))
                    if isinstance(full_docs_map.get(d_id), dict)
                    else None
                    for d_id in ds_remaining
                }
                claimed_sources = build_claimed_source_map(ds_remaining, resolved_remaining)

                if changed_sections:
                    insert_contents: list[str] = []
                    insert_ids: list[str] = []
                    insert_keys: list[str] = []
                    for sec in changed_sections:
                        s_key = build_section_source_key(relative, sec["section_key"], claimed_sources=claimed_sources)
                        claimed_sources.setdefault(canonical_source_name(s_key), set()).add(relative)
                        insert_contents.append(sec["content"])
                        insert_ids.append(sec["doc_id"])
                        insert_keys.append(s_key)

                    gleaning_mode = os.environ.get("RAG_GLEANING_MODE", "adaptive").strip().lower() or "adaptive"
                    target_gleaning = resolve_gleaning_for_doc(relative, gleaning_mode)
                    prev_gleaning = getattr(rag, "entity_extract_max_gleaning", 1)
                    rag.entity_extract_max_gleaning = target_gleaning
                    prev_llm = rag.llm_model_func
                    role_states = getattr(rag, "_role_llm_states", {}) or {}
                    saved_role_raws = {k: st.raw_func for k, st in role_states.items()}
                    rag.llm_model_func = custom_llm_insert
                    for st in role_states.values():
                        st.raw_func = custom_llm_insert
                    if hasattr(rag, "_rebuild_role_llm_funcs"):
                        rag._rebuild_role_llm_funcs()
                    try:
                        if len(insert_contents) == 1:
                            await rag.ainsert(insert_contents[0], ids=insert_ids, file_paths=insert_keys)
                        else:
                            await rag.ainsert(insert_contents, ids=insert_ids, file_paths=insert_keys)
                    finally:
                        rag.entity_extract_max_gleaning = prev_gleaning
                        rag.llm_model_func = prev_llm
                        for k, raw_fn in saved_role_raws.items():
                            if k in role_states:
                                role_states[k].raw_func = raw_fn
                        if hasattr(rag, "_rebuild_role_llm_funcs"):
                            rag._rebuild_role_llm_funcs()

                    for sec, s_key in zip(changed_sections, insert_keys):
                        inserted_row = await rag.doc_status.get_by_id(sec["doc_id"])
                        if not is_doc_processed(inserted_row):
                            st_val = inserted_row.get("status") if isinstance(inserted_row, dict) else "absent/rejeté (dup-*)"
                            return [TextContent(type="text", text=(
                                f"❌ **Échec ou Rejet d'Indexation RAG** pour `{relative}` (section `{sec['section_key']}`)\n\n"
                                f"- **Doc ID** : `{sec['doc_id']}`\n"
                                f"- **Clé source** : `{s_key}`\n"
                                f"- **Statut `doc_status`** : `{st_val}`"
                            ))]

                sec_dict = {
                    s["section_key"]: {
                        "doc_id": s["doc_id"],
                        "sha256": s["content_sha256"],
                        "title": s["section_title"],
                    }
                    for s in v_sections
                }
                log_idx[str(target_path)] = {
                    "mtime": os.path.getmtime(target_path),
                    "doc_id": v_sections[0]["doc_id"],
                    "content_sha256": file_norm_sha,
                    "sections": sec_dict,
                }
                try:
                    with open(log_file, "w", encoding="utf-8") as lf:
                        json.dump(log_idx, lf, indent=2, ensure_ascii=False)
                except Exception as write_log_err:
                    print(f"⚠️ Erreur écriture indexed_files.json: {write_log_err}", file=sys.stderr)
                _mark_rag_disk_fresh(DB_PATH)
                trace_str = idx_tracker.format_summary()
                sec_gleaning_mode = os.environ.get("RAG_GLEANING_MODE", "adaptive").strip().lower() or "adaptive"
                sec_gleaning = resolve_gleaning_for_doc(relative, sec_gleaning_mode)
                return [TextContent(type="text", text=(
                    f"✅ **Document Indexé par Sections Virtuelles dans le RAG D-Bot** !\n\n"
                    f"- **Fichier** : `{relative}`\n"
                    f"- **Sections mises à jour** : `{len(changed_sections)}/{len(v_sections)}` ({purged_count} version(s) purgée(s))\n"
                    f"- **Gleaning** : `{sec_gleaning}` (`{sec_gleaning_mode}`)\n"
                    f"- **Moteur LLM** : {resolved_engine[0]}\n"
                    f"- **Trace Moteur RAG** : `{trace_str}`\n"
                    f"- **Base RAG** : `{DB_PATH}`"
                ))]

            # Purge des anciennes versions exactes dans doc_status et graphe (protège les homonymes)
            purged_count = 0
            matching_ids = []
            try:
                for d_id, d_data in ds_items:
                    fp = d_data.get("file_path", "") or ""
                    fd_entry = full_docs_map.get(d_id)
                    fd_rel = extract_rel_path(fd_entry.get("content", "")) if isinstance(fd_entry, dict) else None
                    if fd_rel == relative or fp in (relative, str(target_path), expected_flat):
                        matching_ids.append(d_id)

                if matching_ids:
                    purged_count = len(matching_ids)
                    for old_id in matching_ids:
                        if not old_id.startswith("dup-"):
                            try:
                                await rag.adelete_by_doc_id(old_id)
                            except Exception:
                                pass
                        try:
                            await rag.doc_status.delete([old_id])
                        except Exception:
                            pass
            except Exception as pe:
                print(f"Info purge doc_status pour {relative}: {pe}", file=sys.stderr)

            purged_set = set(matching_ids)
            ds_remaining = {d_id: d_data for d_id, d_data in ds_items if d_id not in purged_set}
            resolved_remaining = {
                d_id: extract_rel_path(full_docs_map[d_id].get("content", ""))
                if isinstance(full_docs_map.get(d_id), dict)
                else None
                for d_id in ds_remaining
            }
            claimed_sources = build_claimed_source_map(ds_remaining, resolved_remaining)
            other_basenames = {
                canonical_source_name(rel_val)
                for rel_val in resolved_remaining.values()
                if rel_val and rel_val != relative
            }
            source_key = build_rag_source_key(
                relative,
                claimed_sources=claimed_sources,
                other_basenames=other_basenames,
            )

            doc_id = _compute_doc_id(full_content)
            gleaning_mode = os.environ.get("RAG_GLEANING_MODE", "adaptive").strip().lower() or "adaptive"
            target_gleaning = resolve_gleaning_for_doc(relative, gleaning_mode)
            prev_gleaning = getattr(rag, "entity_extract_max_gleaning", 1)
            rag.entity_extract_max_gleaning = target_gleaning
            prev_llm = rag.llm_model_func
            role_states = getattr(rag, "_role_llm_states", {}) or {}
            saved_role_raws = {k: st.raw_func for k, st in role_states.items()}
            rag.llm_model_func = custom_llm_insert
            for st in role_states.values():
                st.raw_func = custom_llm_insert
            if hasattr(rag, "_rebuild_role_llm_funcs"):
                rag._rebuild_role_llm_funcs()
            try:
                await rag.ainsert(full_content, ids=[doc_id], file_paths=[source_key])
            finally:
                rag.entity_extract_max_gleaning = prev_gleaning
                rag.llm_model_func = prev_llm
                for k, raw_fn in saved_role_raws.items():
                    if k in role_states:
                        role_states[k].raw_func = raw_fn
                if hasattr(rag, "_rebuild_role_llm_funcs"):
                    rag._rebuild_role_llm_funcs()

            inserted_row = None
            try:
                inserted_row = await rag.doc_status.get_by_id(doc_id)
            except Exception:
                inserted_row = None
            if not is_doc_processed(inserted_row):
                st_val = inserted_row.get("status") if isinstance(inserted_row, dict) else "absent/rejeté (dup-*)"
                return [TextContent(type="text", text=(
                    f"❌ **Échec ou Rejet d'Indexation RAG** pour `{relative}`\n\n"
                    f"- **Doc ID** : `{doc_id}`\n"
                    f"- **Clé source** : `{source_key}`\n"
                    f"- **Statut `doc_status`** : `{st_val}`\n"
                    f"- `indexed_files.json` n'a pas été modifié afin de permettre une réindexation propre."
                ))]

            # Synchronisation du journal d'indexation indexed_files.json
            log_idx[str(target_path)] = {
                "mtime": os.path.getmtime(target_path),
                "doc_id": doc_id,
                "content_sha256": file_norm_sha,
            }
            try:
                with open(log_file, "w", encoding="utf-8") as lf:
                    json.dump(log_idx, lf, indent=2, ensure_ascii=False)
            except Exception as write_log_err:
                print(f"⚠️ Erreur écriture indexed_files.json: {write_log_err}", file=sys.stderr)
            _mark_rag_disk_fresh(DB_PATH)

            char_count = len(full_content)
            purge_info = f" ({purged_count} ancienne(s) version(s) purgée(s))" if purged_count > 0 else ""
            trace_str = idx_tracker.format_summary()
            return [TextContent(type="text", text=(
                f"✅ **Document Indexé avec Succès dans le RAG D-Bot** !\n\n"
                f"- **Fichier** : `{relative}`\n"
                f"- **Clé source** : `{source_key}`\n"
                f"- **Doc ID** : `{doc_id}`\n"
                f"- **Volume** : {char_count} caractères{purge_info}\n"
                f"- **Gleaning** : `{target_gleaning}` (`{gleaning_mode}`)\n"
                f"- **Moteur LLM** : {resolved_engine[0]}\n"
                f"- **Trace Moteur RAG** : `{trace_str}`\n"
                f"- **Base RAG** : `{DB_PATH}` (graphe et index vectoriel à jour)"
            ))]

        elif name == "rag_commit_agent_index":
            job_id = (arguments.get("job_id") or "").strip()
            if not job_id:
                return [TextContent(type="text", text="❌ 'job_id' est obligatoire pour rag_commit_agent_index.")]
            if is_indexing_lock_active(DB_PATH):
                return [TextContent(type="text", text=f"⏳ Une indexation externe est déjà en cours sur `{DB_PATH}`. Réessayez après sa complétion.")]
            res_commit = await commit_agent_bundle(
                rag=rag,
                db_path=DB_PATH,
                job_id_or_path=job_id,
                extractions=arguments.get("extractions"),
                extractions_path=arguments.get("extractions_path"),
                apply_deletes=bool(arguments.get("apply_deletes", True)),
                force_llm_summary_on_merge=int(arguments.get("force_llm_summary_on_merge", 24)),
                allow_stale=bool(arguments.get("allow_stale", False)),
                cleanup=bool(arguments.get("cleanup", True)),
            )
            _mark_rag_disk_fresh(DB_PATH)
            committed_list = ", ".join(c["rel_path"] for c in res_commit["committed"]) or "aucun"
            failed_txt = (
                f"\n- **Échecs** : {res_commit['failed']}"
                if res_commit["failed"]
                else ""
            )
            return [TextContent(type="text", text=(
                f"✅ **Indexation Agent Commitée dans le RAG D-Bot** (`0` LLM tiers)\n\n"
                f"- **Job ID** : `{res_commit['job_id']}`\n"
                f"- **Profil Thinking** : `{res_commit['effort_profile']}` (sans `extra_high`)\n"
                f"- **Documents indexés ({len(res_commit['committed'])})** : `{committed_list}`\n"
                f"- **Chunks rejoués** : `{res_commit['chunks_replayed']}` | **Fusions dédupliquées** : `{res_commit['summaries_merged']}`\n"
                f"- **Purge** : `{res_commit['replaced_count']}` remplacé(s), `{res_commit['deleted_count']}` supprimé(s), `{res_commit['orphan_count']}` orphelin(s)"
                f"{failed_txt}\n"
                f"- **Trace Moteur RAG** : `antigravity / self-agent [role=index | profile={res_commit['effort_profile']}]`\n"
                f"- **Base RAG** : `{DB_PATH}`"
            ))]

        # On définit le mode de recherche selon l'outil standard
        llm_mode = arguments.get("llm_mode", "auto").lower()
        if llm_mode not in ("antigravity", "internal", "auto"):
            llm_mode = "auto"
        prov_arg = (arguments.get("provider") or "").strip().lower() or None
        model_arg = (arguments.get("model") or "").strip() or None

        mode = "hybrid"
        query = ""

        def _build_synthesis_param(q_mode: str) -> QueryParam:
            max_total = int(os.environ.get("RAG_QUERY_MAX_TOKENS", "9500"))
            chunk_k = int(os.environ.get("RAG_QUERY_CHUNK_TOP_K", "6"))
            return QueryParam(
                mode=q_mode,
                chunk_top_k=max(1, chunk_k),
                top_k=int(os.environ.get("RAG_QUERY_GRAPH_TOP_K", "20")),
                max_entity_tokens=int(os.environ.get("RAG_QUERY_MAX_ENTITY_TOKENS", "2000")),
                max_relation_tokens=int(os.environ.get("RAG_QUERY_MAX_RELATION_TOKENS", "2500")),
                max_total_tokens=max_total,
                user_prompt=(
                    "Réponds en français technique précis et factuel. "
                    "Écris toutes les formules, unités et tolérances en texte brut lisible "
                    "(jamais de syntaxe LaTeX ni de symbole dollar)."
                ),
            )

        if name == "rag_search":
            query = arguments.get("query", "")
            mode = "hybrid"
            search_tracker = ModelExecutionTracker(
                role="qa",
                default_no_llm_label=f"Aucun LLM (extraction graphe/vecteur — mode {llm_mode})",
            )
            if llm_mode in ("internal", "auto"):
                search_tracker.default_no_llm_label = (
                    f"Cache LightRAG (réponse en cache — 0 appel LLM [mode {llm_mode}])"
                )
                tok_role = _CURRENT_RAG_ROLE.set("qa")
                tok_trk = _CURRENT_TRACKER.set(search_tracker)
                tok_prov = _CURRENT_PROVIDER_OVERRIDE.set(prov_arg)
                tok_mod = _CURRENT_MODEL_OVERRIDE.set(model_arg)
                try:
                    ans = await rag.aquery(query, param=_build_synthesis_param("hybrid"))
                    return [TextContent(type="text", text=(
                        f"### Synthèse RAG [Mode: {llm_mode}] pour : {query}\n"
                        f"{search_tracker.format_markdown_line()}\n\n{ans}"
                    ))]
                except Exception as ex:
                    if llm_mode == "internal":
                        return [TextContent(type="text", text=f"❌ Erreur synthèse LLM ({search_tracker.format_summary()}) : {ex}")]
                    search_tracker.default_no_llm_label = "Aucun LLM (extraction graphe/vecteur — repli antigravity)"
                    search_tracker.fallback_note = search_tracker.default_no_llm_label
                    print(f"ℹ️ Fallback Antigravity pour rag_search : {ex}", file=sys.stderr)
                finally:
                    _CURRENT_RAG_ROLE.reset(tok_role)
                    _CURRENT_TRACKER.reset(tok_trk)
                    _CURRENT_PROVIDER_OVERRIDE.reset(tok_prov)
                    _CURRENT_MODEL_OVERRIDE.reset(tok_mod)

        elif name == "rag_analyze_impact":
            scenario = arguments.get("scenario", "")
            context = arguments.get("context", "")
            query = f"{scenario}\n{context}".strip() if context else scenario
            mode = "global"
            search_tracker = ModelExecutionTracker(
                role="audit",
                default_no_llm_label=f"Aucun LLM (extraction graphe/vecteur — mode {llm_mode})",
            )
            if llm_mode in ("internal", "auto"):
                search_tracker.default_no_llm_label = (
                    f"Cache LightRAG (réponse en cache — 0 appel LLM [mode {llm_mode}])"
                )
                tok_role = _CURRENT_RAG_ROLE.set("audit")
                tok_trk = _CURRENT_TRACKER.set(search_tracker)
                tok_prov = _CURRENT_PROVIDER_OVERRIDE.set(prov_arg)
                tok_mod = _CURRENT_MODEL_OVERRIDE.set(model_arg)
                try:
                    ans = await rag.aquery(query, param=_build_synthesis_param("global"))
                    return [TextContent(type="text", text=(
                        f"### Analyse d'Impact [Mode: {llm_mode}] pour : {scenario}\n"
                        f"{search_tracker.format_markdown_line()}\n\n{ans}"
                    ))]
                except Exception as ex:
                    if llm_mode == "internal":
                        return [TextContent(type="text", text=f"❌ Erreur analyse d'impact LLM ({search_tracker.format_summary()}) : {ex}")]
                    search_tracker.default_no_llm_label = "Aucun LLM (extraction graphe/vecteur — repli antigravity)"
                    search_tracker.fallback_note = search_tracker.default_no_llm_label
                    print(f"ℹ️ Fallback Antigravity pour rag_analyze_impact : {ex}", file=sys.stderr)
                finally:
                    _CURRENT_RAG_ROLE.reset(tok_role)
                    _CURRENT_TRACKER.reset(tok_trk)
                    _CURRENT_PROVIDER_OVERRIDE.reset(tok_prov)
                    _CURRENT_MODEL_OVERRIDE.reset(tok_mod)

        elif name == "rag_get_context":
            query = arguments.get("topic", "")
            mode = "local"
            search_tracker = ModelExecutionTracker(
                role="qa",
                default_no_llm_label="Aucun LLM (extraction locale sans synthèse)",
            )
        elif name == "rag_list_topics":
            domain = arguments.get("domain", "")
            query = f"thématiques documentées {domain}"
            mode = "naive"
            search_tracker = ModelExecutionTracker(
                role="qa",
                default_no_llm_label="Aucun LLM (index thématique vectoriel sans synthèse)",
            )
        else:
            return [TextContent(type="text", text=f"❌ Outil inconnu : {name}")]

        # Stratégie de recherche résiliente :
        try:
            search_param = QueryParam(mode=mode)
            if mode in ("hybrid", "local", "global", "mix"):
                hl_kw, ll_kw = extract_lexical_keywords(query)
                search_param = QueryParam(mode=mode, hl_keywords=hl_kw, ll_keywords=ll_kw)
            result = await rag.aquery_data(query, param=search_param)
            
            # Vérification si on a des résultats
            chunks = result.get("data", {}).get("chunks", [])
            if not chunks and mode != "naive":
                # Fallback Naive si le mode complexe a échoué
                result = await rag.aquery_data(query, param=QueryParam(mode="naive"))
                chunks = result.get("data", {}).get("chunks", [])
                data_mode = "naive (fallback)"
            else:
                data_mode = mode
        except Exception as e:
            print(f"⚠️ Erreur recherche initiale : {e}", file=sys.stderr)
            result = await rag.aquery_data(query, param=QueryParam(mode="naive"))
            chunks = result.get("data", {}).get("chunks", [])
            data_mode = "naive (emergency)"

        if result.get("status") == "success":
            if not chunks:
                return [TextContent(type="text", text=f"Aucun document pertinent trouvé dans la base pour : '{query}'.")]

            # --- Filtrage optionnel des chunks d'images (modèles non-VLM) ---
            if SKIP_IMAGES:
                _before = len(chunks)
                chunks = [c for c in chunks if os.path.splitext(c.get("file_path", ""))[1].lower() not in IMAGE_EXTS]
                _skipped = _before - len(chunks)
                if _skipped:
                    print(f"⚠️  Ignoré {_skipped} chunk(s) d'image (RAG_SKIP_IMAGES=true).", file=sys.stderr)
                if not chunks:
                    return [TextContent(type="text", text=f"Aucun document texte pertinent pour : '{query}'. (chunks images exclus)")]

            # --- RERANKING MANUEL ---
            try:
                chunks = await fast_rerank_func(query, chunks)
                data_mode += " + rerank"
            except Exception as e:
                print(f"⚠️ Échec Rerank : {e}", file=sys.stderr)

            # Formatage de la réponse pour le LLM
            # Strip markdown image refs so clients don't try to read image files for non-VLM models
            if name == "rag_analyze_impact":
                output = [
                    f"### Dossier d'Analyse d'Impact D-Bot [Mode: {data_mode} / Antigravity] pour : {query}",
                    search_tracker.format_markdown_line(),
                    "> **Consigne pour l'Agent Antigravity** : Analyse en profondeur l'impact de ce scénario sur le robot (masses, inerties, couples moteurs, rigidité, cinématique, thermique et consommation) à partir des données ci-dessous issues du graphe de connaissances.\n"
                ]
            else:
                output = [
                    f"### Extraits D-Bot [Mode: {data_mode}] pour : {query}",
                    search_tracker.format_markdown_line(),
                ]
            for i, chunk in enumerate(chunks[:10]): # Top 10 chunks
                source = chunk.get("file_path", "Source inconnue")
                content = chunk.get("content", "").strip()
                content = _md_img.sub("[référence image — voir source originale]", content)
                content = _orphan_ref.sub("[référence image — voir source originale]", content)
                score = chunk.get("rerank_score", 0.0)
                score_str = f" [Score: {score:.2f}]" if score > 0 else ""
                output.append(f"\n---\n[Source {i+1}: {source}]{score_str}\n{content}")
            
            return [TextContent(type="text", text="\n".join(output))]
        else:
            return [TextContent(type="text", text=f"⚠️ Erreur de recherche : {result.get('message')}")]

    except Exception as e:
        return [TextContent(type="text", text=f"❌ Erreur critique MCP : {e}")]


# ─── Point d'Entrée ───────────────────────────────────────────────────────────

async def main():
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    finally:
        _MANAGED_OLLAMA.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
