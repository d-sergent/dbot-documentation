#!/opt/homebrew/bin/python3.11
import asyncio
import argparse
import sys
import os
import openai
import numpy as np
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

try:
    from lightrag import LightRAG, QueryParam
    from lightrag.utils import EmbeddingFunc
    from fastembed import TextEmbedding
except ImportError as e:
    print(f"❌ Dépendance manquante : {e}")
    sys.exit(1)

# ─── Configuration ────────────────────────────────────────────────────────────
DB_PATH = os.environ.get("RAG_DB_PATH", "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db")
VMLX_BASE_URL = os.environ.get("VMLX_BASE_URL", "http://127.0.0.1:8080/v1")
VMLX_MODEL = os.environ.get("VMLX_MODEL", "JANGQ-AI/Qwen3.6-35B-A3B-JANGTQ4")

# ─── Moteur RAG ───────────────────────────────────────────────────────────────
_embed_model = None
def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding("intfloat/multilingual-e5-large")
    return _embed_model

async def fastembed_func(texts: list[str]) -> np.ndarray:
    model = get_embed_model()
    return np.array(list(model.embed(texts)), dtype=np.float32)

embedding_func = EmbeddingFunc(embedding_dim=1024, max_token_size=8192, func=fastembed_func)

def get_llm_func(provider: str, target_model: str):
    async def llm_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history_messages)
        messages.append({"role": "user", "content": prompt})
        
        allowed = ["max_tokens", "temperature", "top_p", "response_format"]
        clean_kwargs = {k: v for k, v in kwargs.items() if k in allowed}
        
        if provider == "local":
            client = openai.AsyncOpenAI(base_url=VMLX_BASE_URL, api_key="none")
            response = await client.chat.completions.create(model=target_model, messages=messages, **clean_kwargs)
            return response.choices[0].message.content
            
        elif provider == "openrouter":
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
    parser = argparse.ArgumentParser(description="Interroge la documentation D-Bot via le RAG")
    parser.add_argument("query", type=str, help="La question à poser au RAG")
    parser.add_argument("--mode", type=str, choices=["naive", "local", "global", "hybrid"], default="naive", help="Mode de recherche (naive = le plus rapide)")
    parser.add_argument("--search-only", action="store_true", help="Retourne uniquement les morceaux de texte trouvés, sans synthèse LLM")
    parser.add_argument("--provider", type=str, choices=["local", "openrouter"], default="local", help="Fournisseur d'IA pour la réponse (defaut: local)")
    parser.add_argument("--model", type=str, help="Modèle à utiliser (surcharge le défaut du provider)")
    args = parser.parse_args()

    # Sélection automatique du modèle par défaut selon le provider si non spécifié
    if not args.model:
        args.model = VMLX_MODEL if args.provider == "local" else "nvidia/nemotron-3-super-120b-a12b:free"

    # Redirige les prints des bibliothèques vers stderr pour garder stdout propre
    old_stdout = sys.stdout
    sys.stdout = sys.stderr

    if not os.path.exists(DB_PATH):
        print(f"❌ Base introuvable à {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    rag = LightRAG(working_dir=DB_PATH, llm_model_func=get_llm_func(args.provider, args.model), embedding_func=embedding_func)
    await rag.initialize_storages()
    
    # Restaure stdout pour le vrai résultat
    sys.stdout = old_stdout
    
    try:
        if args.search_only:
            # Récupère uniquement les données structurées (retrieval seul)
            result = await rag.aquery_data(args.query, param=QueryParam(mode=args.mode))
            if result.get("status") == "success":
                data = result.get("data", {})
                chunks = data.get("chunks", [])
                print(f"--- CONTEXTE TROUVÉ ({len(chunks)} morceaux) ---")
                for i, chunk in enumerate(chunks):
                    print(f"\n[Source {i+1}: {chunk.get('file_path')}]\n{chunk.get('content')}")
            else:
                print(f"❌ Échec de la recherche : {result.get('message')}")
        else:
            # Mode RAG complet (retrieval + synthesis via LLM local)
            result = await rag.aquery(args.query, param=QueryParam(mode=args.mode))
            print(result)
    except Exception as e:
        print(f"❌ Erreur lors de la requête : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
