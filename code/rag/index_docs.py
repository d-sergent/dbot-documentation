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
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from itertools import cycle

# Charger les variables d'environnement
load_dotenv()

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

handler_file = logging.FileHandler("/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/rag_indexing.log", encoding="utf-8")
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

EXCLUDE_DIRS = {".git", ".continue", "__pycache__", "Archives", "assets",
                "Images_ORCA", ".DS_Store", "lightrag_dbot_db", "00_Archives_Recherche"}
INCLUDE_EXTS = {".md", ".py", ".txt"}

# ─── Stratégie Round-Robin Hybride (Gemini + OpenRouter) ────────────────────────
import aiohttp

MODELS_ROTATION = [
    {"name": "models/gemini-2.5-flash", "type": "gemini"},
    {"name": "models/gemini-3.1-flash-lite", "type": "gemini"},
    {"name": "tencent/hy3:free", "type": "openrouter"},
    {"name": "nvidia/nemotron-3-ultra-550b-a55b:free", "type": "openrouter"},
    {"name": "nvidia/nemotron-3-super-120b-a12b:free", "type": "openrouter"},
    {"name": "google/gemma-4-31b-it:free", "type": "openrouter"},
    {"name": "google/gemma-4-26b-a4b-it:free", "type": "openrouter"}
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
except ImportError as e:
    logger.error(f"Dépendance manquante : {e}")
    sys.exit(1)

# ─── Embeddings Locaux (FastEmbed) ───────────────────────────────────────────
_embed_model = TextEmbedding("intfloat/multilingual-e5-large")
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
        base_url = os.environ.get("VMLX_BASE_URL", "http://127.0.0.1:8080/v1")
        model = os.environ.get("VMLX_MODEL", "dealignai/Nemotron-3-Nano-Omni-30B-A3B-JANGTQ4-CRACK")
        logger.info(f"🔗 Mode LOCAL : vMLX sur {base_url}")
        
        async def llm_local(prompt, system_prompt=None, history_messages=[], **kwargs):
            return await openai_complete_if_cache(
                model, prompt, system_prompt=system_prompt, history_messages=history_messages,
                base_url=base_url, api_key="none", **kwargs
            )
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
                            # Google bloque pour toute la journée, donc après 3 erreurs on bloque pour 12 heures
                            if s["failures"] >= 3:
                                s["locked_until"] = now + 43200
                                continue
                                
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
                        logger.info(f"🔵 [{log_id}] OK:{s['success']} ERR:{s['failures']} -> ✅ OK")
                        await asyncio.sleep(2) 
                        return result_text
                    
                    except Exception as e:
                        err_msg = str(e)
                        s["failures"] += 1
                        # Pénalité "intelligente" :
                        # - OpenRouter : pause de 60 secondes car le quota se régénère
                        # - Gemini : après chaque erreur, on augmente la pénalité
                        penalty = 60 if model_type == "openrouter" else 300 * s["failures"]
                        s["locked_until"] = now + penalty
                        
                        logger.warning(f"🔵 [{log_id}] OK:{s['success']} ERR:{s['failures']} -> ⚠️ PAUSE ({penalty}s) | Erreur: {err_msg[:100]}")
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
    return "doc-" + hashlib.md5(content.encode("utf-8")).hexdigest()

def prepare_document(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8")
        relative = path.relative_to(DOCS_ROOT)
        header = f"---\nFichier: {relative}\nProjet: D-Bot\n---\n\n"
        return header + content
    except: return ""

async def run_indexing(args):
    all_files = collect_files()
    all_files_str = set(str(p) for p in all_files)
    log_idx = load_index_log() if not args.full else {}
    
    to_update = [p for p in all_files if str(p) not in log_idx or log_idx[str(p)]["mtime"] < os.path.getmtime(p)]
    to_delete = [path_str for path_str in list(log_idx.keys()) if path_str not in all_files_str]

    if not to_update and not to_delete:
        logger.info("✅ Tout est à jour.")
        return

    llm_func = await get_llm_func(args)
    
    # Parallélisme : 4 pour cloud (online/openrouter), 1 pour local
    max_async = 1 if args.provider == "local" else 4
    
    rag = LightRAG(
        working_dir=str(DB_PATH),
        llm_model_func=llm_func,
        embedding_func=embedding_func,
        llm_model_max_async=max_async
    )
    await rag.initialize_storages()
    
    if to_delete:
        logger.info(f"🗑️  Nettoyage intelligent : Suppression de {len(to_delete)} fichier(s) exclu(s)/supprimé(s)...")
        for path_str in to_delete:
            doc_id = log_idx[path_str].get("doc_id")
            if doc_id:
                try:
                    await rag.adelete_by_doc_id(doc_id)
                except Exception as e:
                    logger.warning(f"Impossible de supprimer {doc_id} de LightRAG: {e}")
            del log_idx[path_str]
            logger.info(f"   [-] Oublié : {Path(path_str).name}")

    if to_update:
        logger.info(f"📂 Indexation de {len(to_update)} fichier(s) [Parallélisme: {max_async}]...")
    for i, path in enumerate(to_update, 1):
        content = prepare_document(path)
        if not content: continue
        logger.info(f"[{i:3d}/{len(to_update)}] 📄 {path.name}")
        try:
            await rag.ainsert(content)
            log_idx[str(path)] = {"mtime": os.path.getmtime(path), "doc_id": compute_doc_id(content)}
        except Exception: 
            pass 

    save_index_log(log_idx)
    logger.info("🎉 Synthèse Finale :")
    for m in MODELS_ROTATION:
        name = m["name"]
        logger.info(f"  - {name}: OK={stats[name]['success']} | ERR={stats[name]['failures']}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--provider", choices=["local", "online", "openrouter"], default="online")
    parser.add_argument("--model", type=str, help="Forcer un modèle spécifique (uniquement avec --provider openrouter)")
    parser.add_argument("--api-key", type=str)
    args = parser.parse_args()
    await run_indexing(args)

if __name__ == "__main__":
    asyncio.run(main())
