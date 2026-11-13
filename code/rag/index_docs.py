#!/opt/homebrew/bin/python3.11
import argparse
import asyncio
import json
import os
import shutil
import sys
import time
import hashlib
import logging
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from itertools import cycle

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

handler_file = logging.FileHandler(Path(__file__).resolve().parent / "rag_indexing.log", encoding="utf-8")
handler_file.setFormatter(formatter)
handler_file.addFilter(NoExcInfoFilter())

logging.basicConfig(level=logging.INFO, handlers=[handler_stdout, handler_file], force=True)
logger = logging.getLogger("D-Bot-RAG")

logging.getLogger("lightrag").setLevel(logging.WARNING)
logging.getLogger("lightrag").addFilter(NoExcInfoFilter())
logging.getLogger("nano-vectordb").setLevel(logging.WARNING)


# ─── Configuration Chemins ───────────────────────────────────────────────────
DOCS_ROOT = Path("/Users/Shared/Mon Google Drive Physique/Documentation")
DB_PATH   = Path("/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db")
INDEX_LOG = DB_PATH / "indexed_files.json"

EXCLUDE_DIRS = {".git", ".continue", "__pycache__", "Archives",
                "Images_ORCA", ".DS_Store", "lightrag_dbot_db", "00_Archives_Recherche",
                ".kilo", ".gemini", ".cursor", ".roo", "scratch", "cad_views"}
INCLUDE_EXTS = {".md", ".py", ".txt", ".png", ".jpg", ".jpeg", ".webp", ".pdf", ".svg"}
IMAGE_EXTS   = {".png", ".jpg", ".jpeg", ".webp"}
PDF_EXTS     = {".pdf"}
SVG_EXTS     = {".svg"}

# ─── Stratégie Round-Robin Hybride (Gemini + OpenRouter) ────────────────────────
import aiohttp

MODELS_ROTATION = [
    {"name": "models/gemini-3.1-flash-lite", "type": "gemini"},
    {"name": "models/gemini-3.6-flash", "type": "gemini"},
    {"name": "models/gemini-3.5-flash-lite", "type": "gemini"},
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
    import defusedxml.ElementTree as DefusedET
except ImportError as e:
    logger.error(f"Dépendance manquante : {e}")
    sys.exit(1)

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

async def get_llm_func(args):
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    
    if args.provider == "local":
        base_url = os.environ.get("VMLX_BASE_URL", "http://127.0.0.1:8008/v1")
        model = os.environ.get("VMLX_MODEL", "JANGQ-AI/Qwen3.5-9B-JANG_4S")
        logger.info(f"🔗 Mode LOCAL : vMLX ({model}) sur {base_url}")
        
        async def llm_local(prompt, system_prompt=None, history_messages=[], **kwargs):
            res = await openai_complete_if_cache(
                model,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                base_url=base_url,
                api_key="EMPTY",
                max_tokens=8192,
                **kwargs
            )
            return res
        return llm_local

    elif args.provider == "openrouter":
        target_model = args.model or "tencent/hy3-preview:free"
        logger.info(f"🌐 Mode OPENROUTER : Modèle unique {target_model}")
        
        async def call_openrouter_fixed(model_name, prompt, system_prompt):
            or_key = os.environ.get("OPENROUTER_API_KEY")
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {or_key}", "Content-Type": "application/json"}
            messages = []
            if system_prompt: messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json={"model": model_name, "messages": messages}) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP_{resp.status}")
                    data = await resp.json()
                    if "error" in data:
                        err_info = data["error"]
                        raise Exception(f"OpenRouter_{err_info.get('code', 'Error')}: {err_info.get('message', 'Unknown error')}")
                    choices = data.get("choices")
                    if not choices:
                        raise Exception("OpenRouter response missing 'choices'")
                    return choices[0]["message"]["content"]

        async def llm_openrouter(prompt, system_prompt=None, history_messages=[], **kwargs):
            return await call_openrouter_fixed(target_model, prompt, system_prompt)
            
        return llm_openrouter

    elif args.provider == "gemini":
        client = genai.Client(api_key=api_key)
        target_model = args.model or "gemini-3.1-flash-lite"
        th_level_str = getattr(args, "thinking_level", "low").lower()
        th_budget_map = {
            "minimal": 0,
            "low": 100,
            "medium": 512,
            "high": 1024
        }
        thinking_budget = th_budget_map.get(th_level_str, 100)
        logger.info(f"💎 Mode GEMINI : Modèle {target_model} [Budget raisonnement: {thinking_budget} tokens ({th_level_str})]")

        # Cascade intelligente de tous les modèles rapides disponibles
        all_gemini_models = [
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash-lite",
            "gemini-3.6-flash",
            "gemini-3.7-flash",
            "gemini-flash-lite-latest",
            "gemini-2.5-flash"
        ]
        models_cascade = [target_model] + [m for m in all_gemini_models if m != target_model]
        exhausted_models = set()

        async def call_openrouter_fallback(model_name, p, sp):
            or_key = os.environ.get("OPENROUTER_API_KEY")
            if not or_key:
                return None
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {or_key}", "Content-Type": "application/json"}
            messages = []
            if sp: messages.append({"role": "system", "content": sp})
            messages.append({"role": "user", "content": p})
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json={"model": model_name, "messages": messages}, timeout=25) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            choices = data.get("choices")
                            if choices:
                                return choices[0]["message"]["content"]
            except Exception:
                pass
            return None

        async def llm_gemini(prompt, system_prompt=None, history_messages=[], **kwargs):
            loop = asyncio.get_event_loop()
            
            for current_model in models_cascade:
                if current_model in exhausted_models:
                    continue
                try:
                    cfg = genai_types.GenerateContentConfig(
                        system_instruction=system_prompt if system_prompt else None,
                        thinking_config=genai_types.ThinkingConfig(thinking_budget=thinking_budget),
                        max_output_tokens=kwargs.get("max_tokens", 4096),
                        temperature=kwargs.get("temperature", 0.1)
                    )
                    response = await loop.run_in_executor(
                        None,
                        lambda m=current_model: client.models.generate_content(
                            model=m,
                            contents=prompt,
                            config=cfg
                        )
                    )
                    if response and response.text:
                        await asyncio.sleep(2.5)  # Respect du quota 15 RPM
                        return response.text
                except Exception as e:
                    err_s = str(e)
                    if any(k in err_s for k in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE"]) or "quota" in err_s.lower() or "high demand" in err_s.lower():
                        logger.warning(f"⚠️ Modèle {current_model} saturé ou indisponible ({err_s[:70]}). Verrouillé pour cette session, bascule immédiate sur la cascade.")
                        exhausted_models.add(current_model)
                        continue
                    else:
                        logger.warning(f"⚠️ Erreur LLM ({current_model}): {err_s[:80]}. Nouvelle tentative...")
                        await asyncio.sleep(2)
                        continue

            # Repli de secours sur OpenRouter gratuit si tous les modèles Gemini gratuits sont saturés
            for or_model in ["nvidia/nemotron-3-super-120b-a12b:free", "meta-llama/llama-3.3-70b-instruct:free"]:
                res = await call_openrouter_fallback(or_model, prompt, system_prompt)
                if res:
                    logger.info(f"🟢 Repli OpenRouter ({or_model}) réussi.")
                    await asyncio.sleep(2.0)
                    return res

            logger.error("❌ Tous les modèles Gemini et OpenRouter sont temporairement saturés. Pause de 15s...")
            await asyncio.sleep(15)
            return await llm_gemini(prompt, system_prompt=system_prompt, history_messages=history_messages, **kwargs)

        return llm_gemini

    elif args.provider == "online":
        logger.info(f"🚀 Round-Robin Online Parallélisé ({len(MODELS_ROTATION)} modèles)")
        client = genai.Client(api_key=api_key)
        
        async def call_openrouter(model_name, prompt, system_prompt):
            or_key = os.environ.get("OPENROUTER_API_KEY")
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {or_key}", "Content-Type": "application/json"}
            messages = []
            if system_prompt: messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json={"model": model_name, "messages": messages}) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP_{resp.status}")
                    data = await resp.json()
                    if "error" in data:
                        err_info = data["error"]
                        raise Exception(f"OpenRouter_{err_info.get('code', 'Error')}: {err_info.get('message', 'Unknown error')}")
                    choices = data.get("choices")
                    if not choices:
                        raise Exception("OpenRouter response missing 'choices'")
                    return choices[0]["message"]["content"]
        
        async def llm_online_round_robin(prompt, system_prompt=None, history_messages=[], **kwargs):
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            loop = asyncio.get_event_loop()
            
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
                            response = await loop.run_in_executor(
                                None, 
                                lambda: client.models.generate_content(
                                    model=model_name,
                                    contents=full_prompt,
                                    config=genai_types.GenerateContentConfig(
                                        max_output_tokens=kwargs.get("max_tokens", 4096),
                                        temperature=kwargs.get("temperature", 0.1)
                                    )
                                )
                            )
                            result_text = response.text
                        
                        elif model_type == "openrouter":
                            # Appel HTTP pur pour OpenRouter (0 log parasite de LightRAG)
                            result_text = await call_openrouter(model_name, prompt, system_prompt)
     
                        s["success"] += 1
                        s["failures"] = 0  # Réinitialisation des erreurs sur un succès
                        logger.info(f"🔵 [{log_id}] OK:{s['success']} -> ✅ OK")
                        await asyncio.sleep(2.5)  # Espace de 2.5s pour respecter ~15-20 RPM
                        return result_text
                    
                    except Exception as e:
                        err_msg = str(e)
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
    files = []
    for path in DOCS_ROOT.rglob("*"):
        if any(excl in path.parts for excl in EXCLUDE_DIRS): continue
        if path.is_file() and path.suffix.lower() in INCLUDE_EXTS:
            files.append(path)
    return sorted(files)

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
    if not content:
        return None
    m = re.match(r"^---\s*\nFichier:\s*(.+?)\n", content)
    return m.group(1).strip() if m else None


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


def _is_orphan_entry(
    d_id: str,
    d_data: dict,
    rel: str | None,
    active_rel_set: set[str],
    all_files_str: set[str],
    active_basenames: set[str],
) -> bool:
    """Détermine si une entrée doc_status correspond à un fichier archivé ou supprimé du disque."""
    if rel is not None:
        return rel not in active_rel_set
    fp = (d_data.get("file_path", "") or "").strip()
    if not fp or fp == "unknown_source":
        return False
    if "/" in fp:
        cand = str(Path(fp).resolve()) if Path(fp).is_absolute() else str((DOCS_ROOT / fp).resolve())
        return cand not in all_files_str
    return os.path.basename(fp) not in active_basenames


def _load_disk_state(
    all_files_str: set[str], active_rel_set: set[str], active_basenames: set[str]
) -> tuple[set[str], set[str], set[str], list[str]]:
    """Lit les stores JSON locaux en lecture seule pour détecter le statut réel et les orphelins."""
    processed_ids, processed_rels, processed_basenames = set(), set(), set()
    orphan_ids: list[str] = []
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
            if _is_orphan_entry(d_id, d_data, rel, active_rel_set, all_files_str, active_basenames):
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
        elif fp_entry in (target_abs, rel_target):
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


async def _purge_doc_ids(rag: LightRAG, doc_ids: list[str], label: str) -> int:
    """Supprime proprement doc_ids des chunks, vecteurs et graphe de connaissances LightRAG."""
    purged = 0
    seen: set[str] = set()
    for d_id in doc_ids:
        if not d_id or d_id in seen:
            continue
        seen.add(d_id)
        if not d_id.startswith("dup-"):
            try:
                res = await rag.adelete_by_doc_id(d_id)
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

VLM_MODELS = [
    "models/gemini-3.8-flash",
    "models/gemini-3.1-flash-lite",
    "models/gemini-3.6-flash",
    "models/gemini-3.5-flash-lite",
    "models/gemini-2.5-flash"
]

def analyze_image_with_vlm(client: genai.Client, image_path: Path) -> str:
    if not client:
        raise RuntimeError("API Client VLM non disponible")
    
    img = Image.open(image_path)
    prompt = (
        "Tu es un expert en ingénierie mécanique, robotique et électronique pour le projet D-Bot.\n"
        "Analyse cette image technique en détail. Décris avec précision :\n"
        "1. Les composants mécaniques, électroniques, moteurs, roulements, fixations ou assemblages visibles.\n"
        "2. Toutes les cotations, dimensions, références, marquages ou annotations textuelles (ex: AXK 5578, M4x70, etc.).\n"
        "3. La géométrie, le montage et la fonction technique de ce sous-ensemble.\n"
        "Fournis une description technique exhaustive et structurée."
    )

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
                return response.text
        except Exception as e:
            last_error = str(e)
            if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                logger.warning(f"⚠️ Quota 429 sur {model_name} pour {image_path.name}. Basculement sur le modèle VLM suivant...")
                time.sleep(2)
                continue
            else:
                logger.warning(f"⚠️ Erreur sur {model_name}: {e}")
                continue
                
    raise RuntimeError(f"Échec de l'analyse VLM sur {image_path.name} après tous les modèles (Dernière erreur: {last_error})")

def extract_pdf_text(path: Path) -> str:
    # 1. Extraction haute fidélité via Docling (reconstruction des tableaux Markdown et hiérarchies)
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(str(path))
        md_text = result.document.export_to_markdown()
        if md_text and md_text.strip():
            logger.info(f"   ✨ Extraction Docling réussie pour {path.name} ({len(md_text)} caractères)")
            return md_text
    except ImportError:
        pass
    except Exception as docling_err:
        logger.warning(f"⚠️ Docling indisponible pour {path.name}: {docling_err}. Basculement sur pypdf.")

    # 2. Fallback standard léger via pypdf
    try:
        reader = pypdf.PdfReader(path)
        pages_text = []
        for i, page in enumerate(reader.pages, 1):
            t = page.extract_text()
            if t and t.strip():
                pages_text.append(f"--- Page {i} ---\n{t.strip()}")
        return "\n\n".join(pages_text)
    except Exception as e:
        logger.warning(f"⚠️ Erreur de lecture PDF {path.name}: {e}")
        return ""


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


def prepare_document(path: Path, genai_client: genai.Client = None) -> str:
    relative = path.relative_to(DOCS_ROOT)
    ext = path.suffix.lower()
    
    if ext in IMAGE_EXTS:
        logger.info(f"📸 Analyse VLM en cours pour l'image: {path.name}...")
        try:
            vlm_desc = analyze_image_with_vlm(genai_client, path)
            header = f"---\nFichier: {relative}\nType: Image VLM\nProjet: D-Bot\n---\n\n"
            return header + f"# Analyse Visuelle et Spécifications Techniques : {path.name}\n\n" + vlm_desc
        except Exception as e:
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

async def run_indexing(args):
    all_files = collect_files()
    all_files_str = {str(p) for p in all_files}
    active_rel_set = {str(p.relative_to(DOCS_ROOT)) for p in all_files}
    active_name_counts = Counter(p.name for p in all_files)
    active_basenames = set(active_name_counts.keys())
    log_idx = load_index_log() if not args.full else {}

    processed_ids, processed_rels, processed_basenames, pending_orphans = _load_disk_state(
        all_files_str, active_rel_set, active_basenames
    )

    def file_needs_update(p: Path) -> bool:
        if str(p) not in log_idx:
            return True
        if log_idx[str(p)].get("mtime", 0) < os.path.getmtime(p):
            return True
        rel = str(p.relative_to(DOCS_ROOT))
        cached_id = log_idx[str(p)].get("doc_id")
        if cached_id in processed_ids or rel in processed_rels:
            return False
        if active_name_counts.get(p.name, 0) == 1 and p.name in processed_basenames:
            return False
        return True

    if args.files:
        to_update = [Path(f).resolve() for f in args.files if Path(f).exists()]
        to_delete = []
        check_orphans = False
    elif args.full:
        to_update = all_files
        to_delete = [path_str for path_str in list(log_idx.keys()) if path_str not in all_files_str]
        check_orphans = bool(pending_orphans)
    else:
        to_update = [p for p in all_files if file_needs_update(p)]
        to_delete = [path_str for path_str in list(log_idx.keys()) if path_str not in all_files_str]
        check_orphans = bool(pending_orphans)

    if not to_update and not to_delete and not check_orphans:
        logger.info("✅ Tout est à jour.")
        return

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    genai_client = genai.Client(api_key=api_key) if api_key else None

    llm_func = await get_llm_func(args)

    # Parallélisme : 4 pour cloud multi-modèles (online/openrouter), 1 pour local et gemini (quota 15 RPM)
    max_async = 1 if args.provider in ("local", "gemini") else 4

    rag = LightRAG(
        working_dir=str(DB_PATH),
        llm_model_func=llm_func,
        embedding_func=embedding_func,
        llm_model_max_async=max_async,
    )
    await rag.initialize_storages()

    ds_snapshot, fd_map = await _snapshot_doc_status_and_full_docs(rag)
    resolved_rels = {
        d_id: _rel_path_from_doc_entry(d_id, d_data, fd_map)
        for d_id, d_data in ds_snapshot.items()
    }

    if to_delete:
        logger.info(f"🗑️  Nettoyage intelligent : Suppression de {len(to_delete)} fichier(s) exclu(s)/supprimé(s)...")
        for path_str in to_delete:
            target_path = Path(path_str)
            try:
                rel_target = str(target_path.relative_to(DOCS_ROOT))
            except ValueError:
                rel_target = None

            matched_ids = _find_matching_doc_ids(
                ds_snapshot=ds_snapshot,
                resolved_rels=resolved_rels,
                target_abs=path_str,
                rel_target=rel_target,
                target_basename=target_path.name,
                allow_basename_match=(target_path.name not in active_basenames),
                extra_doc_id=log_idx[path_str].get("doc_id"),
            )
            purged_n = await _purge_doc_ids(rag, matched_ids, target_path.name)
            for mid in matched_ids:
                ds_snapshot.pop(mid, None)
                resolved_rels.pop(mid, None)
            del log_idx[path_str]
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
                if purged_n:
                    logger.info(f"   [-] Orphelin purgé : {o_label} ({o_id})")

    if to_update:
        logger.info(f"📂 Indexation de {len(to_update)} fichier(s) [Parallélisme: {max_async}]...")
    for i, path in enumerate(to_update, 1):
        content = prepare_document(path, genai_client)
        if not content:
            continue
        logger.info(f"[{i:3d}/{len(to_update)}] 📄 {path.name}")
        try:
            rel_path = str(path.relative_to(DOCS_ROOT))
        except ValueError:
            rel_path = str(path)
        try:
            # Purge complète de l'ancienne version (chunks + vecteurs + graphe) avant réinsertion
            matching_ids = _find_matching_doc_ids(
                ds_snapshot=ds_snapshot,
                resolved_rels=resolved_rels,
                target_abs=str(path),
                rel_target=rel_path,
                target_basename=path.name,
                allow_basename_match=(active_name_counts.get(path.name, 0) <= 1),
                extra_doc_id=log_idx.get(str(path), {}).get("doc_id"),
            )
            if matching_ids:
                await _purge_doc_ids(rag, matching_ids, path.name)
                for mid in matching_ids:
                    ds_snapshot.pop(mid, None)
                    resolved_rels.pop(mid, None)

            doc_id = compute_doc_id(content)
            await rag.ainsert(content, ids=[doc_id], file_paths=[rel_path])
            ds_snapshot[doc_id] = {"file_path": rel_path, "status": "processed"}
            resolved_rels[doc_id] = rel_path
            log_idx[str(path)] = {"mtime": os.path.getmtime(path), "doc_id": doc_id}
            save_index_log(log_idx)
        except Exception as e:
            logger.warning(f"⚠️ Échec d'indexation pour {path.name}: {e}")

    save_index_log(log_idx)
    logger.info("🎉 Synthèse Finale :")
    for m in MODELS_ROTATION:
        name = m["name"]
        logger.info(f"  - {name}: OK={stats[name]['success']} | ERR={stats[name]['failures']}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Réindexation complète depuis zéro")
    parser.add_argument("--update", action="store_true", help="Forcer la vérification et mise à jour incrémentale")
    parser.add_argument("--files", nargs="+", help="Chemins de fichiers spécifiques à réindexer")
    parser.add_argument("--provider", choices=["local", "online", "openrouter", "gemini"], default="gemini", help="Fournisseur LLM (défaut: gemini)")
    parser.add_argument("--thinking-level", choices=["minimal", "low", "medium", "high"], default="low", help="Niveau d'effort de réflexion Gemini (défaut: low)")
    parser.add_argument("--model", type=str, default="gemini-3.1-flash-lite", help="Forcer un modèle spécifique (défaut: gemini-3.1-flash-lite)")
    parser.add_argument("--api-key", type=str)
    args = parser.parse_args()
    await run_indexing(args)

if __name__ == "__main__":
    asyncio.run(main())
