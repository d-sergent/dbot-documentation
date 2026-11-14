#!/opt/homebrew/bin/python3.11
import asyncio
import argparse
import sys
import os
from pathlib import Path
import openai
import numpy as np
from dotenv import load_dotenv

# Charger les variables d'environnement (depuis la racine Documentation même hors cwd)
_REPO_ENV = Path(__file__).resolve().parent.parent.parent / ".env"
if _REPO_ENV.exists():
    load_dotenv(dotenv_path=_REPO_ENV)
else:
    load_dotenv()

try:
    from lightrag import LightRAG, QueryParam
    from lightrag.utils import EmbeddingFunc
    from fastembed import TextEmbedding
    from fastembed.rerank.cross_encoder import TextCrossEncoder
except ImportError as e:
    print(f"❌ Dépendance manquante : {e}")
    sys.exit(1)

# ─── Configuration ────────────────────────────────────────────────────────────
DB_PATH = os.environ.get("RAG_DB_PATH", "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db")
VMLX_BASE_URL = os.environ.get("VMLX_BASE_URL", "http://127.0.0.1:8888/v1").strip().rstrip("/")
VMLX_MODEL = os.environ.get("VMLX_MODEL", "unsloth/Qwen3.8-27B-GGUF")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip().rstrip("/")
if OLLAMA_BASE_URL.endswith("/v1"):
    OLLAMA_BASE_URL = OLLAMA_BASE_URL[:-3]
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.8:27b-mlx")
OLLAMA_NUM_CTX = int(os.environ.get("OLLAMA_NUM_CTX", "16384"))
OLLAMA_KEEP_ALIVE = os.environ.get("OLLAMA_KEEP_ALIVE", "10m")


def _resolve_local_api_key() -> str:
    """Retourne la clé d'authentification locale (Unsloth Studio / vMLX) sans secret hardcodé."""
    return os.environ.get("VMLX_API_KEY") or os.environ.get("UNSLOTH_API_KEY") or "EMPTY"

# Profil QA Non-Thinking recommandé pour Qwen3.8 / Unsloth
QWEN_QA_SAMPLING = {
    "temperature": 0.7,
    "top_p": 0.80,
    "top_k": 20,
    "min_p": 0.0,
    "repeat_penalty": 1.0,
    "presence_penalty": 1.0,
}

# Dossier de cache permanent et fiable (protégé contre les nettoyages macOS)
DEFAULT_CACHE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/models_cache"
FASTEMBED_CACHE_DIR = os.environ.get("FASTEMBED_CACHE_PATH", DEFAULT_CACHE_DIR)

# ─── Moteur RAG & Embeddings ──────────────────────────────────────────────────
import warnings
warnings.filterwarnings("ignore", message=".*intfloat/multilingual-e5-large now uses mean pooling.*")

_embed_model = None
def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding("intfloat/multilingual-e5-large", cache_dir=FASTEMBED_CACHE_DIR)
    return _embed_model

async def fastembed_func(texts: list[str]) -> np.ndarray:
    model = get_embed_model()
    return np.array(list(model.embed(texts)), dtype=np.float32)

embedding_func = EmbeddingFunc(embedding_dim=1024, max_token_size=8192, func=fastembed_func)

# ─── Modèle de Reranking Cross-Encoder ────────────────────────────────────────
_rerank_model = None
def get_rerank_model():
    global _rerank_model
    if _rerank_model is None:
        _rerank_model = TextCrossEncoder("BAAI/bge-reranker-base", cache_dir=FASTEMBED_CACHE_DIR)
    return _rerank_model

async def fastembed_rerank_func(query: str, documents: list[str], top_n: int = None, **kwargs) -> list[dict]:
    """Fonction de Reranking native pour LightRAG basée sur FastEmbed Cross-Encoder."""
    if not documents:
        return []
    try:
        model = get_rerank_model()
        scores = list(model.rerank(query, documents))
        indexed = [
            {"index": i, "relevance_score": float(1.0 / (1.0 + np.exp(-float(s))))}
            for i, s in enumerate(scores)
        ]
        indexed.sort(key=lambda x: x["relevance_score"], reverse=True)
        return indexed[:top_n] if top_n else indexed
    except Exception as e:
        print(f"⚠️ Avertissement Reranking natif : {e}", file=sys.stderr)
        return [{"index": i, "relevance_score": 0.0} for i in range(len(documents))]

def rerank_chunks(query: str, chunks: list[dict], top_k: int = 5, min_score: float = 0.25) -> list[dict]:
    """Ré-ordonne et filtre les chunks par pertinence sémantique croisée (Cross-Encoder fallback)."""
    if not chunks:
        return []
    try:
        model = get_rerank_model()
        texts = [c.get("content", "") for c in chunks]
        raw_scores = list(model.rerank(query, texts))
        
        # Normalisation Sigmoïde : 1 / (1 + exp(-score)) -> Score entre 0.0 et 1.0 (0% à 100%)
        for i, score in enumerate(raw_scores):
            norm_score = float(1.0 / (1.0 + np.exp(-float(score))))
            chunks[i]["rerank_score"] = norm_score
            chunks[i]["raw_score"] = float(score)
        
        # Tri par score de pertinence décroissant
        sorted_chunks = sorted(chunks, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        
        # Filtrage par score minimum
        filtered = [c for c in sorted_chunks if c.get("rerank_score", 0.0) >= min_score]
        return filtered[:top_k] if filtered else sorted_chunks[:top_k]
    except Exception as e:
        print(f"⚠️ Avertissement Reranking : {e}", file=sys.stderr)
        return chunks[:top_k]

def get_llm_func(provider: str, target_model: str):
    """Construit la fonction LLM asynchrone compatible LightRAG pour local, ollama ou openrouter."""
    async def llm_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for msg in history_messages or []:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})

        if provider == "ollama":
            import aiohttp

            payload = {
                "model": target_model,
                "messages": messages,
                "stream": False,
                "think": False,
                "keep_alive": OLLAMA_KEEP_ALIVE,
                "options": {
                    "num_ctx": OLLAMA_NUM_CTX,
                    "temperature": kwargs.get("temperature", QWEN_QA_SAMPLING["temperature"]),
                    "top_p": kwargs.get("top_p", QWEN_QA_SAMPLING["top_p"]),
                    "top_k": kwargs.get("top_k", QWEN_QA_SAMPLING["top_k"]),
                    "min_p": kwargs.get("min_p", QWEN_QA_SAMPLING["min_p"]),
                    "repeat_penalty": kwargs.get("repeat_penalty", QWEN_QA_SAMPLING["repeat_penalty"]),
                    "presence_penalty": kwargs.get("presence_penalty", QWEN_QA_SAMPLING["presence_penalty"]),
                    "num_predict": kwargs.get("max_tokens", 4096),
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

        allowed = ["max_tokens", "temperature", "top_p", "presence_penalty", "response_format", "extra_body"]
        clean_kwargs = {k: v for k, v in kwargs.items() if k in allowed}

        if provider == "local":
            enable_thinking = os.environ.get("RAG_ENABLE_THINKING", "false").strip().lower() in ("1", "true", "yes")
            clean_kwargs.setdefault("max_tokens", 8192 if enable_thinking else 4096)
            clean_kwargs.setdefault("temperature", 1.0 if enable_thinking else QWEN_QA_SAMPLING["temperature"])
            clean_kwargs.setdefault("top_p", 0.95 if enable_thinking else QWEN_QA_SAMPLING["top_p"])
            clean_kwargs.setdefault("presence_penalty", 0.0 if enable_thinking else QWEN_QA_SAMPLING["presence_penalty"])
            extra_body = {
                "chat_template_kwargs": {"enable_thinking": enable_thinking},
                "top_k": kwargs.get("top_k", QWEN_QA_SAMPLING["top_k"]),
                "min_p": kwargs.get("min_p", QWEN_QA_SAMPLING["min_p"]),
                "repeat_penalty": kwargs.get("repeat_penalty", QWEN_QA_SAMPLING["repeat_penalty"]),
            }
            if isinstance(clean_kwargs.get("extra_body"), dict):
                extra_body.update(clean_kwargs["extra_body"])
            clean_kwargs["extra_body"] = extra_body
            client = openai.AsyncOpenAI(base_url=VMLX_BASE_URL, api_key=_resolve_local_api_key())
            response = await client.chat.completions.create(model=target_model, messages=messages, **clean_kwargs)
            content = response.choices[0].message.content
            if not content:
                finish = response.choices[0].finish_reason
                raise RuntimeError(f"Réponse locale vide ({VMLX_BASE_URL}, finish_reason={finish})")
            return content

        elif provider == "openrouter":
            clean_kwargs.pop("extra_body", None)
            or_key = os.environ.get("OPENROUTER_API_KEY")
            if not or_key:
                raise ValueError("OPENROUTER_API_KEY manquante dans le .env")
            client = openai.AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=or_key)
            response = await client.chat.completions.create(
                model=target_model,
                messages=messages,
                extra_headers={"HTTP-Referer": "https://github.com/d-bot"},
                **clean_kwargs
            )
            return response.choices[0].message.content

    return llm_func

async def main():
    parser = argparse.ArgumentParser(description="Interroge la documentation D-Bot via le RAG avec Reranking")
    parser.add_argument("query", type=str, help="La question à poser au RAG")
    parser.add_argument("--mode", type=str, choices=["naive", "local", "global", "hybrid"], default="naive", help="Mode de recherche (naive = rapide)")
    parser.add_argument("--search-only", action="store_true", help="Retourne uniquement les morceaux de texte trouvés, sans synthèse LLM")
    parser.add_argument("--top-k", type=int, default=5, help="Nombre maximal d'extraits pertinents à renvoyer (défaut: 5)")
    parser.add_argument(
        "--max-context-tokens",
        type=int,
        default=int(os.environ.get("RAG_QUERY_MAX_TOKENS", "9500")),
        help="Plafond de tokens de contexte transmis au LLM en synthèse (défaut: 9500)",
    )
    parser.add_argument("--min-score", type=float, default=0.25, help="Score minimal de confiance entre 0.0 et 1.0 (défaut: 0.25)")
    parser.add_argument("--no-rerank", action="store_true", help="Désactive le Reranking Cross-Encoder")
    parser.add_argument("--provider", type=str, choices=["local", "ollama", "openrouter"], default="local", help="Fournisseur d'IA pour la réponse (defaut: local)")
    parser.add_argument("--model", type=str, help="Modèle à utiliser (surcharge le défaut du provider)")
    args = parser.parse_args()

    # Sélection automatique du modèle par défaut selon le provider si non spécifié
    if not args.model:
        default_models = {
            "local": VMLX_MODEL,
            "ollama": OLLAMA_MODEL,
            "openrouter": "nvidia/nemotron-3-super-120b-a12b:free",
        }
        args.model = default_models[args.provider]

    # Redirige les prints des bibliothèques vers stderr pour garder stdout propre
    old_stdout = sys.stdout
    sys.stdout = sys.stderr

    if not os.path.exists(DB_PATH):
        print(f"❌ Base introuvable à {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    rag = LightRAG(
        working_dir=DB_PATH,
        llm_model_func=get_llm_func(args.provider, args.model),
        embedding_func=embedding_func,
        rerank_model_func=fastembed_rerank_func if not args.no_rerank else None,
        addon_params={"language": "French"},
    )
    await rag.initialize_storages()
    
    # Restaure stdout pour le vrai résultat
    sys.stdout = old_stdout
    
    if args.search_only:
        param = QueryParam(mode=args.mode, enable_rerank=not args.no_rerank)
    else:
        param = QueryParam(
            mode=args.mode,
            enable_rerank=not args.no_rerank,
            chunk_top_k=max(1, args.top_k),
            top_k=max(10, args.top_k * 4),
            max_entity_tokens=min(2000, args.max_context_tokens // 4),
            max_relation_tokens=min(2500, args.max_context_tokens // 3),
            max_total_tokens=args.max_context_tokens,
            user_prompt=(
                "Réponds en français technique précis et factuel. "
                "Écris toutes les formules, unités et tolérances en texte brut lisible "
                "(jamais de syntaxe LaTeX ni de symbole dollar)."
            ),
        )

    try:
        if args.search_only:
            # Récupère les données candidates (retrieval)
            result = await rag.aquery_data(args.query, param=param)
            if result.get("status") == "success":
                data = result.get("data", {})
                chunks = data.get("chunks", [])
                
                # Le reranker natif LightRAG classe déjà les chunks si actif
                if not args.no_rerank and chunks:
                    if "rerank_score" not in chunks[0]:
                        chunks = rerank_chunks(args.query, chunks, top_k=args.top_k, min_score=args.min_score)
                    else:
                        chunks = [c for c in chunks if c.get("rerank_score", 1.0) >= args.min_score][:args.top_k]
                else:
                    chunks = chunks[:args.top_k]

                print(f"--- CONTEXTE TROUVÉ ({len(chunks)} extraits classés par pertinence) ---")
                for i, chunk in enumerate(chunks):
                    file_p = chunk.get("file_path", "Source inconnue")
                    score_info = f" [Score: {chunk.get('rerank_score', 0.0):.1%}]" if "rerank_score" in chunk else ""
                    print(f"\n[Source {i+1}: {file_p}]{score_info}\n{chunk.get('content')}")
            else:
                print(f"❌ Échec de la recherche : {result.get('message')}")
        else:
            # Mode RAG complet (retrieval + synthesis via LLM)
            result = await rag.aquery(args.query, param=param)
            print(result)
    except Exception as e:
        print(f"❌ Erreur lors de la requête : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
