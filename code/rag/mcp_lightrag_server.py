#!/opt/homebrew/bin/python3.11
"""
Serveur MCP pour LightRAG — Documentation D-Bot

Expose 4 outils MCP utilisables par n'importe quel LLM compatible MCP (vMLX, Claude, etc.) :
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
        "VMLX_BASE_URL": "http://127.0.0.1:1800/v1",
        "RAG_DB_PATH": "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"
      }
    }
  }

Prérequis : pip install lightrag-hku lancedb fastembed mcp
"""

import asyncio
import base64
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
    canonical_source_name,
    extract_rel_path,
    is_doc_processed,
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

DB_PATH               = Path(os.environ.get("RAG_DB_PATH", "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"))
DOCS_ROOT             = Path(os.environ.get("RAG_DOCS_ROOT", "/Users/Shared/Mon Google Drive Physique/Documentation"))
REPORT_PATH           = DOCS_ROOT / "annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md"
QUESTIONS_JSON_PATH   = DOCS_ROOT / "annexes/Outils_de_Travail/RAG/AUDIT_QUESTION_REPONSE.json"
PLAN_CORRECTION_PATH  = DOCS_ROOT / "annexes/Outils_de_Travail/RAG/PLAN_CORRECTION.md"
PROMPT_CORRECTION_PATH = DOCS_ROOT / "annexes/Outils_de_Travail/RAG/PROMPT_CORRECTION.md"
VMLX_BASE_URL         = os.environ.get("VMLX_BASE_URL", "http://127.0.0.1:8888/v1").strip().rstrip("/")
VMLX_MODEL            = os.environ.get("VMLX_MODEL", "unsloth/Qwen3.8-27B-GGUF")
VMLX_API_KEY          = os.environ.get("VMLX_API_KEY") or os.environ.get("UNSLOTH_API_KEY") or "EMPTY"
OLLAMA_BASE_URL       = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip().rstrip("/")
if OLLAMA_BASE_URL.endswith("/v1"):
    OLLAMA_BASE_URL = OLLAMA_BASE_URL[:-3]
OLLAMA_MODEL          = os.environ.get("OLLAMA_MODEL", "qwen3.8:27b-mlx")
OLLAMA_NUM_CTX        = int(os.environ.get("OLLAMA_NUM_CTX", "16384"))
OLLAMA_KEEP_ALIVE     = os.environ.get("OLLAMA_KEEP_ALIVE", "10m")
RAG_LLM_PROVIDER      = os.environ.get("RAG_LLM_PROVIDER", "auto").strip().lower()
SKIP_IMAGES           = os.environ.get("RAG_SKIP_IMAGES", "true").lower() in ("1", "true", "yes")
IMAGE_EXTS            = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}
RASTER_VLM_EXTS       = {".png", ".jpg", ".jpeg", ".webp"}

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

_genai_client = None

def get_genai_client():
    global _genai_client
    if _genai_client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                from google import genai
                _genai_client = genai.Client(api_key=api_key)
            except Exception as ge:
                print(f"⚠️ Erreur initialisation genai.Client: {ge}", file=sys.stderr)
    return _genai_client


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


async def _call_gemini_chat(
    prompt: str,
    system_prompt: str | None = None,
    model_name: str | None = None,
    thinking_level_str: str = "low",
    max_attempts: int = 2,
) -> str | None:
    """Appelle Gemini Flash via google-genai ; retourne None si saturé (429/503) ou absent."""
    client = get_genai_client()
    if client is None:
        return None
    from google.genai import types as genai_types

    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    target_model = model_name or os.environ.get("RAG_DEFAULT_MODEL", "gemini-3.1-flash-lite")
    th_budget = 0 if thinking_level_str == "minimal" else 100
    cfg = genai_types.GenerateContentConfig(
        thinking_config=genai_types.ThinkingConfig(thinking_budget=th_budget)
    )
    loop = asyncio.get_event_loop()
    for attempt in range(max_attempts):
        try:
            res = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=target_model,
                    contents=full_prompt,
                    config=cfg,
                ),
            )
            if res and res.text:
                await asyncio.sleep(1.0)
                return res.text
        except Exception as e:
            err_s = str(e)
            if any(k in err_s for k in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE")):
                print(f"⚠️ Gemini saturé ({target_model}): {err_s[:80]}", file=sys.stderr)
                return None
            print(f"⚠️ Erreur Gemini (tentative {attempt+1}/{max_attempts}): {err_s[:80]}", file=sys.stderr)
            await asyncio.sleep(2)
    return None


async def llm_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    pref = RAG_LLM_PROVIDER

    if pref in ("auto", "gemini"):
        res = await _call_gemini_chat(
            prompt,
            system_prompt=system_prompt,
            model_name=os.environ.get("RAG_DEFAULT_MODEL", "gemini-3.8-flash"),
            thinking_level_str=os.environ.get("RAG_DEFAULT_THINKING_LEVEL", "low"),
        )
        if res:
            return res
        if pref == "gemini":
            raise RuntimeError("API Gemini indisponible ou quota épuisé")

    if pref in ("auto", "ollama"):
        try:
            return await _call_ollama_chat(
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                temperature=kwargs.get("temperature", QWEN_QA_SAMPLING["temperature"]),
                max_tokens=kwargs.get("max_tokens", 4096),
                top_p=kwargs.get("top_p", QWEN_QA_SAMPLING["top_p"]),
                top_k=kwargs.get("top_k", QWEN_QA_SAMPLING["top_k"]),
                min_p=kwargs.get("min_p", QWEN_QA_SAMPLING["min_p"]),
                repeat_penalty=kwargs.get("repeat_penalty", QWEN_QA_SAMPLING["repeat_penalty"]),
                presence_penalty=kwargs.get("presence_penalty", QWEN_QA_SAMPLING["presence_penalty"]),
            )
        except Exception as oe:
            if pref == "ollama":
                raise RuntimeError(f"Ollama indisponible ({OLLAMA_BASE_URL}): {oe}") from oe
            print(f"ℹ️ Ollama non disponible ({oe}), repli sur vLLM...", file=sys.stderr)

    # Repli vLLM / Unsloth Studio / llama-server local (profil QA Qwen3.8)
    enable_thinking = os.environ.get("RAG_ENABLE_THINKING", "false").strip().lower() in ("1", "true", "yes")
    call_kwargs = dict(kwargs)
    call_kwargs.setdefault("max_tokens", 8192 if enable_thinking else 4096)
    call_kwargs.setdefault("temperature", 1.0 if enable_thinking else QWEN_QA_SAMPLING["temperature"])
    call_kwargs.setdefault("top_p", 0.95 if enable_thinking else QWEN_QA_SAMPLING["top_p"])
    call_kwargs.setdefault("presence_penalty", 0.0 if enable_thinking else QWEN_QA_SAMPLING["presence_penalty"])
    extra_body = {
        "chat_template_kwargs": {"enable_thinking": enable_thinking},
        "top_k": call_kwargs.pop("top_k", QWEN_QA_SAMPLING["top_k"]),
        "min_p": call_kwargs.pop("min_p", QWEN_QA_SAMPLING["min_p"]),
        "repeat_penalty": call_kwargs.pop("repeat_penalty", QWEN_QA_SAMPLING["repeat_penalty"]),
    }
    user_extra = call_kwargs.pop("extra_body", None)
    if isinstance(user_extra, dict):
        extra_body.update(user_extra)
    return await openai_complete_if_cache(
        VMLX_MODEL,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        base_url=VMLX_BASE_URL,
        api_key=VMLX_API_KEY,
        extra_body=extra_body,
        **call_kwargs
    )


async def get_rag() -> LightRAG:
    """Retourne l'instance LightRAG (création lazy + initialize_storages obligatoire en v1.4+)."""
    global _rag_instance
    if _rag_instance is None:
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

        rag = LightRAG(
            working_dir=str(DB_PATH),
            llm_model_func=llm_func,
            embedding_func=embedding_func,
            rerank_model_func=fastembed_rerank_func if HAS_RERANKER else None,
            llm_model_max_async=max(1, int(os.environ.get("LLM_MAX_ASYNC", "1"))),
            default_llm_timeout=600,
            addon_params={"language": "French"},
        )
        rag.llm_response_timeout = 1200
        await rag.initialize_storages()
        _rag_instance = rag
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
                    "description": "Choix du moteur : 'antigravity' (extraits classés pour synthèse par l'agent Antigravity via votre abonnement), 'internal' (synthèse vLLM local ou OpenRouter comme avant), ou 'auto'.",
                    "default": "antigravity"
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
                    "description": "Choix du moteur : 'antigravity' (extrait le graphe de cause à effet pour analyse par l'agent Antigravity via votre abonnement), 'internal' (analyse vLLM local ou OpenRouter), ou 'auto'.",
                    "default": "antigravity"
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
                    "description": "Choix du moteur d'intelligence : 'antigravity' (délègue le raisonnement à l'agent Antigravity via votre abonnement), 'internal' (synthèse via vLLM local ou OpenRouter comme avant), ou 'auto' (tente internal puis fallback antigravity).",
                    "default": "antigravity"
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
            "Supporte Ollama local (qwen3.8:27b-mlx, think=False) et Google Gemini avec bascule automatique."
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
                    "enum": ["auto", "ollama", "gemini"],
                    "description": "Fournisseur LLM : 'auto' (Gemini puis repli immédiat sur Ollama local), 'ollama' (100% local), ou 'gemini'.",
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
                    "description": "Modèle spécifique (défaut: 'qwen3.8:27b-mlx' pour ollama, 'gemini-3.1-flash-lite' pour gemini)."
                }
            },
            "required": ["file_path"]
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

            llm_mode = arguments.get("llm_mode", "antigravity").lower()
            if llm_mode not in ("antigravity", "internal", "auto"):
                llm_mode = "antigravity"

            from datetime import datetime
            results_text = [
                f"# 🛡️ Dossier d'Audit d'Intégrité D-Bot [Scope: {scope}]",
                f"> **Date de génération** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"> **Mode d'intelligence** : `{llm_mode}`\n"
            ]

            for title, q_str in audits_to_run:
                # Mode Internal : appel vLLM / OpenRouter comme dans l'ancienne version
                if llm_mode in ("internal", "auto"):
                    try:
                        ans = await rag.aquery(q_str, param=QueryParam(mode="global", enable_rerank=False))
                        results_text.append(f"## {title} [Synthèse LLM Interne]\n\n{ans}\n\n---\n")
                        continue
                    except Exception as audit_err:
                        err_msg = str(audit_err)
                        if llm_mode == "internal":
                            results_text.append(
                                f"## {title} [Mode: internal]\n\n"
                                f"❌ Impossible de joindre le modèle de synthèse LLM ({VMLX_BASE_URL}).\n"
                                f"Détail : {err_msg}\n\n---\n"
                            )
                            continue
                        else:
                            # Mode auto : fallback transparent sur le mode Antigravity
                            results_text.append(f"> ℹ️ *vLLM non joignable ({err_msg[:60]}...). Basculement sur l'analyse Antigravity (abonnement actif).*\n")

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

                    results_text.append("\n".join(section_md) + "\n---\n")
                except Exception as ex:
                    results_text.append(f"## {title}\n\n❌ Erreur d'extraction des données RAG : {ex}\n\n---\n")

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
            if provider_req not in ("auto", "ollama", "gemini"):
                provider_req = "auto"
            thinking_level_str = arguments.get("thinking_level", "low").lower()
            explicit_model = arguments.get("model")

            ext = target_path.suffix.lower()
            used_engine = provider_req
            if ext == ".pdf":
                try:
                    from docling.document_converter import DocumentConverter
                    conv = DocumentConverter()
                    res = conv.convert(str(target_path))
                    content = res.document.export_to_markdown()
                except Exception:
                    try:
                        import pypdf
                        reader = pypdf.PdfReader(target_path)
                        content = "\n\n".join([f"--- Page {i} ---\n{p.extract_text().strip()}" for i, p in enumerate(reader.pages, 1) if p.extract_text()])
                    except Exception as pe:
                        return [TextContent(type="text", text=f"❌ Erreur lecture PDF {target_path.name} : {pe}")]
                header = f"---\nFichier: {relative}\nType: Document PDF\nProjet: D-Bot\n---\n\n"
                full_content = header + f"# Document PDF : {target_path.name}\n\n" + content
            elif ext == ".svg":
                try:
                    svg_text = extract_svg_text(target_path)
                except Exception as se:
                    return [TextContent(type="text", text=f"❌ Erreur lecture XML SVG {target_path.name} : {se}")]
                if not svg_text.strip():
                    return [TextContent(type="text", text=f"⚠️ Aucun texte exploitable dans le SVG {target_path.name}.")]
                header = f"---\nFichier: {relative}\nType: Schéma Vectoriel SVG (Texte XML)\nProjet: D-Bot\n---\n\n"
                full_content = header + f"# Schéma Technique SVG : {target_path.name}\n\n" + svg_text
            elif ext in RASTER_VLM_EXTS:
                vlm_desc = None
                if provider_req in ("auto", "gemini") and (client := get_genai_client()) is not None:
                    try:
                        from PIL import Image
                        from google.genai import types as genai_types
                        img = Image.open(target_path)
                        g_model = explicit_model if (provider_req == "gemini" and explicit_model) else "gemini-3.1-flash-lite"
                        loop = asyncio.get_event_loop()
                        g_res = await loop.run_in_executor(
                            None,
                            lambda: client.models.generate_content(
                                model=g_model,
                                contents=[img, _VLM_TECHNICAL_PROMPT],
                                config=genai_types.GenerateContentConfig(
                                    thinking_config=genai_types.ThinkingConfig(thinking_budget=100)
                                ),
                            ),
                        )
                        if g_res and g_res.text:
                            vlm_desc = g_res.text
                            used_engine = f"gemini ({g_model})"
                    except Exception as ge_vlm:
                        if provider_req == "gemini":
                            return [TextContent(type="text", text=f"❌ Erreur VLM Gemini sur {target_path.name} : {ge_vlm}")]
                        print(f"⚠️ Repli VLM Ollama pour {target_path.name} : {ge_vlm}", file=sys.stderr)
                if vlm_desc is None:
                    try:
                        o_model = explicit_model if (provider_req == "ollama" and explicit_model) else OLLAMA_MODEL
                        img_b64 = _encode_image_for_ollama(target_path)
                        vlm_desc = await _call_ollama_chat(
                            _VLM_TECHNICAL_PROMPT,
                            model_name=o_model,
                            images=[img_b64],
                            num_ctx=int(os.environ.get("OLLAMA_VLM_NUM_CTX", "8192")),
                        )
                        used_engine = f"ollama ({o_model})"
                    except Exception as oe_vlm:
                        return [TextContent(type="text", text=f"❌ Erreur VLM sur {target_path.name} : {oe_vlm}")]
                type_label = "Image VLM (Ollama)" if used_engine.startswith("ollama") else "Image VLM"
                header = f"---\nFichier: {relative}\nType: {type_label}\nProjet: D-Bot\n---\n\n"
                full_content = header + f"# Analyse Visuelle et Spécifications Techniques : {target_path.name}\n\n" + vlm_desc
            else:
                try:
                    content = target_path.read_text(encoding="utf-8")
                except Exception as read_err:
                    return [TextContent(type="text", text=f"❌ Erreur lecture du fichier {target_path.name} : {read_err}")]
                header = f"---\nFichier: {relative}\nProjet: D-Bot\n---\n\n"
                full_content = header + content

            resolved_engine = [provider_req]

            async def custom_llm_insert(prompt, system_prompt=None, history_messages=[], **kwargs):
                if provider_req in ("auto", "gemini"):
                    g_model = explicit_model if (provider_req == "gemini" and explicit_model) else (explicit_model or "gemini-3.8-flash")
                    g_txt = await _call_gemini_chat(
                        prompt,
                        system_prompt=system_prompt,
                        model_name=g_model,
                        thinking_level_str=thinking_level_str,
                    )
                    if g_txt:
                        resolved_engine[0] = f"Google Gemini API ({g_model}, thinking={thinking_level_str})"
                        return g_txt
                    if provider_req == "gemini":
                        raise RuntimeError(f"Échec Gemini API ({g_model}) lors de l'indexation de {relative}")

                o_model = explicit_model if (provider_req == "ollama" and explicit_model) else OLLAMA_MODEL
                o_txt = await _call_ollama_chat(
                    prompt,
                    system_prompt=system_prompt,
                    history_messages=history_messages,
                    model_name=o_model,
                    temperature=kwargs.get("temperature", 0.1),
                    max_tokens=kwargs.get("max_tokens", 8192),
                )
                resolved_engine[0] = f"Ollama local ({o_model}, think=False)"
                return o_txt

            # Purge des anciennes versions exactes dans doc_status et graphe (protège les homonymes)
            purged_count = 0
            ds_items: list = []
            full_docs_map: dict = {}
            matching_ids: list[str] = []
            expected_flat = relative.replace("/", "--") if "/" in relative else f"root--{relative}"
            try:
                async with rag.doc_status._storage_lock:
                    ds_items = list(rag.doc_status._data.items())
                try:
                    async with rag.full_docs._storage_lock:
                        full_docs_map = dict(rag.full_docs._data)
                except Exception:
                    pass

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
            prev_llm = rag.llm_model_func
            rag.llm_model_func = custom_llm_insert
            try:
                await rag.ainsert(full_content, ids=[doc_id], file_paths=[source_key])
            finally:
                rag.llm_model_func = prev_llm

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
            log_file = DB_PATH / "indexed_files.json"
            log_idx = {}
            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as lf:
                        log_idx = json.load(lf)
                except Exception:
                    pass

            log_idx[str(target_path)] = {
                "mtime": os.path.getmtime(target_path),
                "doc_id": doc_id
            }
            try:
                with open(log_file, "w", encoding="utf-8") as lf:
                    json.dump(log_idx, lf, indent=2, ensure_ascii=False)
            except Exception as write_log_err:
                print(f"⚠️ Erreur écriture indexed_files.json: {write_log_err}", file=sys.stderr)

            char_count = len(full_content)
            purge_info = f" ({purged_count} ancienne(s) version(s) purgée(s))" if purged_count > 0 else ""
            return [TextContent(type="text", text=(
                f"✅ **Document Indexé avec Succès dans le RAG D-Bot** !\n\n"
                f"- **Fichier** : `{relative}`\n"
                f"- **Clé source** : `{source_key}`\n"
                f"- **Doc ID** : `{doc_id}`\n"
                f"- **Volume** : {char_count} caractères{purge_info}\n"
                f"- **Moteur LLM** : {resolved_engine[0]}\n"
                f"- **Base RAG** : `{DB_PATH}` (graphe et index vectoriel à jour)"
            ))]

        # On définit le mode de recherche selon l'outil standard
        llm_mode = arguments.get("llm_mode", "antigravity").lower()
        if llm_mode not in ("antigravity", "internal", "auto"):
            llm_mode = "antigravity"

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
            if llm_mode in ("internal", "auto"):
                try:
                    ans = await rag.aquery(query, param=_build_synthesis_param("hybrid"))
                    return [TextContent(type="text", text=f"### Synthèse RAG [Mode: internal (vLLM)] pour : {query}\n\n{ans}")]
                except Exception as ex:
                    if llm_mode == "internal":
                        return [TextContent(type="text", text=f"❌ Erreur synthèse vLLM ({VMLX_BASE_URL}) : {ex}")]
                    print(f"ℹ️ Fallback Antigravity pour rag_search : {ex}", file=sys.stderr)

        elif name == "rag_analyze_impact":
            scenario = arguments.get("scenario", "")
            context = arguments.get("context", "")
            query = f"{scenario}\n{context}".strip() if context else scenario
            mode = "global"
            if llm_mode in ("internal", "auto"):
                try:
                    ans = await rag.aquery(query, param=_build_synthesis_param("global"))
                    return [TextContent(type="text", text=f"### Analyse d'Impact [Mode: internal (vLLM)] pour : {scenario}\n\n{ans}")]
                except Exception as ex:
                    if llm_mode == "internal":
                        return [TextContent(type="text", text=f"❌ Erreur analyse d'impact vLLM ({VMLX_BASE_URL}) : {ex}")]
                    print(f"ℹ️ Fallback Antigravity pour rag_analyze_impact : {ex}", file=sys.stderr)

        elif name == "rag_get_context":
            query = arguments.get("topic", "")
            mode = "local"
        elif name == "rag_list_topics":
            domain = arguments.get("domain", "")
            query = f"thématiques documentées {domain}"
            mode = "naive"
        else:
            return [TextContent(type="text", text=f"❌ Outil inconnu : {name}")]

        # Stratégie de recherche résiliente :
        try:
            result = await rag.aquery_data(query, param=QueryParam(mode=mode))
            
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
                    "> **Consigne pour l'Agent Antigravity** : Analyse en profondeur l'impact de ce scénario sur le robot (masses, inerties, couples moteurs, rigidité, cinématique, thermique et consommation) à partir des données ci-dessous issues du graphe de connaissances.\n"
                ]
            else:
                output = [f"### Extraits D-Bot [Mode: {data_mode}] pour : {query}"]
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
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
