#!/usr/bin/env python3
"""
Script d'indexation manuelle de la documentation D-Bot dans LightRAG (NanoVectorDB).

Usage:
    python3 index_docs.py --full    # Ré-indexation complète (supprime et recrée la DB)
    python3 index_docs.py --update  # Mise à jour incrémentale (fichiers modifiés uniquement)

Prérequis:
    - vMLX doit être lancé avec un modèle (35B ou 119B recommandé)
    - pip install lightrag-hku fastembed
"""

import argparse
import asyncio
import json
import os
import shutil
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path

# ─── Hack Tiktoken ────────────────────────────────────────────────────────────
# Désactive globalement la vérification des "special tokens" (<|endoftext|>)
# pour éviter que les guides LLM ne fassent planter le tokenizer.
import tiktoken
_original_encode = tiktoken.Encoding.encode
def _safe_encode(self, text, *args, **kwargs):
    kwargs["disallowed_special"] = ()
    return _original_encode(self, text, *args, **kwargs)
tiktoken.Encoding.encode = _safe_encode

# ─── Configuration ────────────────────────────────────────────────────────────

DOCS_ROOT = Path("/Users/Shared/Mon Google Drive Physique/Documentation")
DB_PATH   = Path("/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db")
INDEX_LOG = DB_PATH / "indexed_files.json"

# Port de votre serveur vMLX (modifiez si différent)
VMLX_BASE_URL = os.environ.get("VMLX_BASE_URL", "http://127.0.0.1:8080/v1")
VMLX_MODEL    = os.environ.get("VMLX_MODEL", "JANGQ-AI/Qwen3.6-35B-A3B-JANGTQ4")

# Fichiers et dossiers à exclure de l'indexation
EXCLUDE_DIRS = {".git", ".continue", "__pycache__", "Archives", "assets",
                "Images_ORCA", ".DS_Store", "lightrag_dbot_db"}
INCLUDE_EXTS = {".md", ".py", ".txt"}

# Paramètres de découpage des documents
# Chunks plus petits = chaque appel LLM est 2× plus rapide, moins de risque de timeout
CHUNK_SIZE    = 600   # tokens par chunk (réduit de 1200 à 600)
CHUNK_OVERLAP = 100   # tokens de chevauchement entre chunks

# ─── Imports LightRAG ─────────────────────────────────────────────────────────

try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import openai_complete_if_cache
    from lightrag.utils import EmbeddingFunc
    from fastembed import TextEmbedding
except ImportError as e:
    print(f"❌ Dépendance manquante : {e}")
    print("   Lancez : pip install lightrag-hku fastembed")
    sys.exit(1)

# ─── Modèle d'Embedding FastEmbed (CPU, multilingue) ─────────────────────────

import numpy as np

print("⏳ Chargement du modèle d'embedding FastEmbed (multilingual-e5-large)...")
_embed_model = TextEmbedding("intfloat/multilingual-e5-large")
EMBEDDING_DIM = 1024

async def fastembed_func(texts: list[str]) -> np.ndarray:
    """Génère les embeddings via FastEmbed sur CPU.
    Retourne un np.ndarray shape (N, DIM) — obligatoire pour LightRAG >= 1.4."""
    embeddings = list(_embed_model.embed(texts))
    return np.array(embeddings, dtype=np.float32)

embedding_func = EmbeddingFunc(
    embedding_dim=EMBEDDING_DIM,
    max_token_size=8192,
    func=fastembed_func
)

# ─── LLM via vMLX (OpenAI-compatible) ─────────────────────────────────────────

async def llm_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    """Appelle le LLM local via vMLX pour l'extraction d'entités."""
    # max_tokens limité à 4096 : force le modèle à être concis et évite les timeouts vMLX
    kwargs.setdefault("max_tokens", 4096)
    return await openai_complete_if_cache(
        VMLX_MODEL,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        base_url=VMLX_BASE_URL,
        api_key="not-needed",
        **kwargs
    )

# ─── Fonctions Utilitaires ────────────────────────────────────────────────────

def collect_files() -> list[Path]:
    """Collecte tous les fichiers indexables depuis DOCS_ROOT."""
    files = []
    for path in DOCS_ROOT.rglob("*"):
        if any(excl in path.parts for excl in EXCLUDE_DIRS):
            continue
        if path.is_file() and path.suffix.lower() in INCLUDE_EXTS:
            files.append(path)
    return sorted(files)


def load_index_log() -> dict:
    """Charge le journal des fichiers déjà indexés."""
    if INDEX_LOG.exists():
        with open(INDEX_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_index_log(log: dict):
    """Sauvegarde le journal des fichiers indexés."""
    DB_PATH.mkdir(parents=True, exist_ok=True)
    with open(INDEX_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def get_files_to_update(all_files: list[Path], log: dict) -> list[Path]:
    """Retourne uniquement les fichiers nouveaux ou modifiés."""
    to_update = []
    for path in all_files:
        mtime = os.path.getmtime(path)
        key   = str(path)
        if key not in log or log[key]["mtime"] < mtime:
            to_update.append(path)
    return to_update


def compute_doc_id(content: str) -> str:
    """Calcule l'ID unique d'un document (identique à la logique interne de LightRAG)."""
    return "doc-" + hashlib.md5(content.encode("utf-8")).hexdigest()


def prepare_document(path: Path) -> str:
    """Prépare un document pour l'indexation avec un header de métadonnées."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ⚠️  Impossible de lire {path.name}: {e}")
        return ""

    relative = path.relative_to(DOCS_ROOT)
    header = f"""---
Fichier: {relative}
Type: {"Documentation Markdown" if path.suffix == ".md" else "Code Source Python"}
Projet: D-Bot (Robot Humanoïde)
---

"""
    return header + content

# ─── Initialisation LightRAG (async — obligatoire en v1.4+) ──────────────────

async def create_rag() -> LightRAG:
    """Crée, initialise et retourne une instance LightRAG (LightRAG v1.4+ requires await initialize_storages)."""
    DB_PATH.mkdir(parents=True, exist_ok=True)
    # Configuration des timeouts via variables d'environnement (prioritaires dans LightRAG)
    os.environ["LLM_TIMEOUT"] = "1800"
    os.environ["WORKER_TIMEOUT"] = "1800"
    os.environ["TIMEOUT"] = "1800"

    rag = LightRAG(
        working_dir=str(DB_PATH),
        llm_model_func=llm_func,
        embedding_func=embedding_func,
        chunk_token_size=CHUNK_SIZE,
        chunk_overlap_token_size=CHUNK_OVERLAP,
        vector_storage="NanoVectorDBStorage",
        # 1 seul worker à la fois → évite la surcharge de vMLX (valeur par défaut: 4)
        llm_model_max_async=1,
        # Timeout 30 min par chunk (valeur par défaut: 180s)
        default_llm_timeout=1800,
    )
    # Obligatoire en LightRAG >= 1.4 avant tout insert/query
    await rag.initialize_storages()
    return rag

# ─── Commandes Principales ────────────────────────────────────────────────────

async def cmd_full():
    """Ré-indexation complète : supprime et recrée intégralement la base."""
    print("\n🗑️  Suppression de l'ancienne base de données...")
    if DB_PATH.exists():
        shutil.rmtree(DB_PATH)
    DB_PATH.mkdir(parents=True)
    print("✅ Base supprimée.")

    all_files = collect_files()
    print(f"\n📂 {len(all_files)} fichiers trouvés dans {DOCS_ROOT}")
    print(f"🔗 LLM : {VMLX_BASE_URL}")
    print(f"💾 Base : {DB_PATH}\n")

    rag = await create_rag()
    log = {}
    start_total = time.time()

    for i, path in enumerate(all_files, 1):
        content = prepare_document(path)
        if not content:
            continue

        print(f"[{i:3d}/{len(all_files)}] 📄 {path.relative_to(DOCS_ROOT)}")
        start = time.time()

        try:
            doc_id = compute_doc_id(content)
            await rag.ainsert(content)
            elapsed = time.time() - start
            log[str(path)] = {
                "mtime": os.path.getmtime(path),
                "indexed_at": datetime.now().isoformat(),
                "doc_id": doc_id
            }
            print(f"          ✅ Indexé en {elapsed:.1f}s")
        except Exception as e:
            print(f"          ❌ Erreur : {e}")

    save_index_log(log)
    total = time.time() - start_total
    print(f"\n🎉 Indexation complète terminée en {total/60:.1f} minutes.")
    print(f"   {len(log)} fichiers indexés dans {DB_PATH}")


async def cmd_update():
    """Mise à jour incrémentale : re-indexe uniquement les fichiers nouveaux ou modifiés."""
    all_files = collect_files()
    log       = load_index_log()
    to_update = get_files_to_update(all_files, log)

    if not to_update:
        print("\n✅ Tout est à jour. Aucun fichier à re-indexer.")
        return

    print(f"\n🔄 {len(to_update)} fichier(s) à mettre à jour sur {len(all_files)} au total.")
    print(f"🔗 LLM : {VMLX_BASE_URL}")
    print(f"💾 Base : {DB_PATH}\n")

    rag   = await create_rag()
    
    # 1. Nettoyage des fichiers supprimés du disque
    all_files_set = {str(p) for p in all_files}
    deleted_paths = [p for p in log if p not in all_files_set]
    
    if deleted_paths:
        print(f"🧹 Nettoyage de {len(deleted_paths)} fichier(s) obsolète(s)...")
        for path_str in deleted_paths:
            doc_id = log[path_str].get("doc_id")
            if doc_id:
                print(f"   🗑️  Retrait de l'index : {Path(path_str).name}")
                try:
                    await rag.adelete_by_doc_id(doc_id)
                except Exception as e:
                    print(f"      ⚠️  Erreur lors du retrait : {e}")
            del log[path_str]
        save_index_log(log)
        print("✅ Nettoyage terminé.\n")

    # 2. Mise à jour des fichiers nouveaux ou modifiés
    if not to_update:
        print("✅ Le reste de la base est déjà à jour.")
        return

    start = time.time()
    for i, path in enumerate(to_update, 1):
        content = prepare_document(path)
        if not content:
            continue

        print(f"[{i}/{len(to_update)}] 📄 {path.relative_to(DOCS_ROOT)}")
        try:
            doc_id = compute_doc_id(content)
            await rag.ainsert(content)
            log[str(path)] = {
                "mtime": os.path.getmtime(path),
                "indexed_at": datetime.now().isoformat(),
                "doc_id": doc_id
            }
            print(f"          ✅ OK")
        except Exception as e:
            print(f"          ❌ Erreur : {e}")

    save_index_log(log)
    print(f"\n🎉 Mise à jour terminée en {(time.time()-start):.1f}s.")


# ─── Point d'Entrée ───────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(
        description="Indexation de la documentation D-Bot dans LightRAG"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--full",   action="store_true", help="Ré-indexation complète")
    group.add_argument("--update", action="store_true", help="Mise à jour incrémentale")
    args = parser.parse_args()

    if args.full:
        confirm = input("⚠️  Cela supprimera toute la base existante. Continuer ? (oui/non) : ")
        if confirm.lower() not in ("oui", "o", "yes", "y"):
            print("Annulé.")
            sys.exit(0)
        await cmd_full()
    elif args.update:
        await cmd_update()


if __name__ == "__main__":
    asyncio.run(main())
