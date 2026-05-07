#!/usr/bin/env python3
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
import json
import os
import sys
from pathlib import Path

# ─── Hack Tiktoken ────────────────────────────────────────────────────────────
# Désactive globalement la vérification des "special tokens" (<|endoftext|>)
# pour éviter que les requêtes ou le graphe ne fassent planter le tokenizer.
import tiktoken
_original_encode = tiktoken.Encoding.encode
def _safe_encode(self, text, *args, **kwargs):
    kwargs["disallowed_special"] = ()
    return _original_encode(self, text, *args, **kwargs)
tiktoken.Encoding.encode = _safe_encode

# ─── Configuration ────────────────────────────────────────────────────────────

DB_PATH       = Path(os.environ.get("RAG_DB_PATH", "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"))
VMLX_BASE_URL = os.environ.get("VMLX_BASE_URL", "http://127.0.0.1:8080/v1")
VMLX_MODEL    = os.environ.get("VMLX_MODEL", "JANGQ-AI/Qwen3.6-35B-A3B-JANGTQ4")

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
_embed_model  = None


def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding("intfloat/multilingual-e5-large")
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
            print("⏳ Chargement du modèle de Rerank (bge-reranker-v2-m3)...", file=sys.stderr)
            _rerank_model = TextRerankerClass("BAAI/bge-reranker-v2-m3")
        except Exception as e:
            print(f"⚠️ Impossible de charger le Reranker : {e}", file=sys.stderr)
            return None
    return _rerank_model


async def fast_rerank_func(query: str, chunks: list) -> list:
    """Ré-ordonne les morceaux de texte manuellement (si disponible)."""
    if not chunks or not HAS_RERANKER:
        return chunks
    
    model = get_rerank_model()
    if model is None:
        return chunks

    try:
        texts = [c.get("content", "") for c in chunks]
        print(f"⚖️  Reranking de {len(chunks)} morceaux...", file=sys.stderr)
        scores = list(model.rerank(query, texts))
        
        # Association score + chunk
        for i, score in enumerate(scores):
            chunks[i]["rerank_score"] = float(score)
        
        # Tri par score décroissant
        return sorted(chunks, key=lambda x: x.get("rerank_score", 0), reverse=True)
    except Exception as e:
        print(f"⚠️ Échec technique du Reranking : {e}", file=sys.stderr)
        return chunks


# --- Fonctions LLM ---


async def llm_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    return await openai_complete_if_cache(
        VMLX_MODEL,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        base_url=VMLX_BASE_URL,
        api_key="not-needed",
        **kwargs
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
        kv_file = DB_PATH / "kv_storage_full_docs.json"
        if kv_file.exists():
            size = kv_file.stat().st_size
            print(f"📊 Base trouvée : {size} octets de documents.", file=sys.stderr)
        else:
            print(f"⚠️ ATTENTION : La base semble vide (pas de kv_storage_full_docs.json)", file=sys.stderr)

        rag = LightRAG(
            working_dir=str(DB_PATH),
            llm_model_func=llm_func,
            embedding_func=embedding_func,
        )
        rag.llm_response_timeout = 1200
        await rag.initialize_storages()
        _rag_instance = rag
        print("✅ Serveur RAG prêt et initialisé.", file=sys.stderr)
    return _rag_instance


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
        # On définit le mode de recherche selon l'outil
        mode = "hybrid"
        query = ""

        if name == "rag_search":
            query = arguments.get("query", "")
            mode = "hybrid"
        elif name == "rag_analyze_impact":
            scenario = arguments.get("scenario", "")
            context = arguments.get("context", "")
            query = f"{scenario}\n{context}"
            mode = "global"
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

            # --- RERANKING MANUEL ---
            try:
                chunks = await fast_rerank_func(query, chunks)
                data_mode += " + rerank"
            except Exception as e:
                print(f"⚠️ Échec Rerank : {e}", file=sys.stderr)

            # Formatage de la réponse pour le LLM
            output = [f"### Extraits D-Bot [Mode: {data_mode}] pour : {query}"]
            for i, chunk in enumerate(chunks[:10]): # Top 10 chunks
                source = chunk.get("file_path", "Source inconnue")
                content = chunk.get("content", "").strip()
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
