#!/opt/homebrew/bin/python3.11
"""
Primitives partagees pour la resilience, la configuration des backends LLM,
le reranking, le filtrage documentaire et le cycle de vie Ollama du RAG D-Bot.
"""

from __future__ import annotations

import atexit
import os
import re
import shutil
import subprocess
import sys
import time
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


DEFAULT_DB_PATH = "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"
DEFAULT_FASTEMBED_CACHE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/models_cache"
DEFAULT_EMBED_MODEL = "intfloat/multilingual-e5-large"
DEFAULT_RERANK_MODEL = "BAAI/bge-reranker-base"

DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "qwen3.8:27b-mlx"
DEFAULT_UNSLOTH_BASE_URL = "http://127.0.0.1:8888/v1"
DEFAULT_UNSLOTH_MODEL = "unsloth/Qwen3.8-27B-GGUF"

# Les SVG (schemas vectoriels) et PDF sont volontairement conserves comme contenu textuel utile.
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")

# Profil Qwen3.8 Non-Thinking / QA technique recommande pour la synthese RAG.
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


def resolve_ollama_config() -> tuple[str, str, int, str]:
    """Resout (base_url, model, num_ctx, keep_alive) pour Ollama local."""
    base_url = (os.environ.get("OLLAMA_BASE_URL") or DEFAULT_OLLAMA_BASE_URL).strip().rstrip("/")
    if base_url.endswith("/v1"):
        base_url = base_url[:-3]
    model = (os.environ.get("OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL).strip()
    num_ctx = int(os.environ.get("OLLAMA_NUM_CTX", "16384"))
    keep_alive = os.environ.get("OLLAMA_KEEP_ALIVE", "10m").strip() or "10m"
    return base_url, model, num_ctx, keep_alive


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
) -> str | None:
    """
    Determine le fournisseur LLM actif selon la cascade du guide M1 Max :
    ollama (:11434) -> unsloth (:8888/v1) -> gemini -> openrouter.
    """
    norm = (preferred or "auto").strip().lower()
    if norm in ("local", "vmlx"):
        norm = "unsloth"

    eff_ollama_url, eff_ollama_model, _, _ = resolve_ollama_config()
    eff_ollama_url = ollama_url or eff_ollama_url
    eff_ollama_model = ollama_model or eff_ollama_model

    eff_unsloth_url, _, eff_unsloth_key = resolve_unsloth_config()
    eff_unsloth_url = unsloth_url or eff_unsloth_url
    eff_unsloth_key = unsloth_api_key if unsloth_api_key is not None else eff_unsloth_key

    eff_gemini = (gemini_key if gemini_key is not None else os.environ.get("GEMINI_API_KEY", "")).strip()
    eff_openrouter = (
        openrouter_key if openrouter_key is not None else os.environ.get("OPENROUTER_API_KEY", "")
    ).strip()

    if norm != "auto":
        if norm == "ollama":
            return "ollama" if check_ollama_ready(eff_ollama_url, eff_ollama_model, timeout=timeout) else None
        if norm == "unsloth":
            return "unsloth" if check_unsloth_ready(eff_unsloth_url, eff_unsloth_key, timeout=timeout) else None
        if norm == "gemini":
            return "gemini" if eff_gemini else None
        if norm == "openrouter":
            return "openrouter" if eff_openrouter else None
        return None

    if check_ollama_ready(eff_ollama_url, eff_ollama_model, timeout=timeout):
        return "ollama"
    if check_unsloth_ready(eff_unsloth_url, eff_unsloth_key, timeout=timeout):
        return "unsloth"
    if eff_gemini:
        return "gemini"
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
