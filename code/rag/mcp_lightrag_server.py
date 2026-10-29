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
import json
import os
import re
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
VMLX_BASE_URL         = os.environ.get("VMLX_BASE_URL", "http://127.0.0.1:8006/v1")
VMLX_MODEL            = os.environ.get("VMLX_MODEL", "JANGQ-AI/Gemma-4-31B-it-JANG_4M")
SKIP_IMAGES           = os.environ.get("RAG_SKIP_IMAGES", "true").lower() in ("1", "true", "yes")
IMAGE_EXTS            = {".png", ".jpg", ".jpeg", ".svg", ".gif", ".bmp", ".webp", ".tiff", ".pdf"}

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


async def llm_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    client = get_genai_client()
    if client is not None:
        try:
            from google.genai import types as genai_types
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            model_name = os.environ.get("RAG_DEFAULT_MODEL", "gemini-3.8-flash")
            th_budget = 0 if os.environ.get("RAG_DEFAULT_THINKING_LEVEL", "low") == "minimal" else 100
            cfg = genai_types.GenerateContentConfig(
                thinking_config=genai_types.ThinkingConfig(thinking_budget=th_budget)
            )
            loop = asyncio.get_event_loop()
            for attempt in range(3):
                try:
                    res = await loop.run_in_executor(
                        None,
                        lambda: client.models.generate_content(
                            model=model_name,
                            contents=full_prompt,
                            config=cfg
                        )
                    )
                    if res and res.text:
                        await asyncio.sleep(1.0)
                        return res.text
                except Exception as e:
                    err_s = str(e)
                    wait_t = 15 if "429" in err_s else 2
                    print(f"⚠️ Erreur Gemini LLM (tentative {attempt+1}/3): {err_s[:80]}. Pause {wait_t}s...", file=sys.stderr)
                    await asyncio.sleep(wait_t)
        except Exception as ge_err:
            print(f"⚠️ Échec appel Gemini: {ge_err}. Repli sur vLLM...", file=sys.stderr)

    # Repli vLLM local ou OpenRouter
    kwargs.setdefault("max_tokens", 512)
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
            llm_model_max_async=1,
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
            "Indexe ou réindexe un document spécifique (Markdown, Python, etc.) dans la base RAG locale au fil de l'eau. "
            "Permet une mise à jour instantanée en quelques secondes sans devoir relancer l'indexation complète de la documentation. "
            "Utilise l'API Google Gemini (modèle économe gemini-3.1-flash-lite en mode raisonnement low/minimal)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Chemin absolu ou relatif vers le fichier à indexer (ex: '01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_Synthese_Mecanique_Torse.md')."
                },
                "thinking_level": {
                    "type": "string",
                    "enum": ["minimal", "low", "medium", "high"],
                    "description": "Niveau d'effort de raisonnement Gemini (défaut: 'low', ou 'minimal' pour économie maximale de quota).",
                    "default": "low"
                },
                "model": {
                    "type": "string",
                    "description": "Modèle Gemini à utiliser (défaut: 'gemini-3.1-flash-lite').",
                    "default": "gemini-3.1-flash-lite"
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

            thinking_level_str = arguments.get("thinking_level", "low").lower()
            model_name = arguments.get("model", "gemini-3.8-flash")

            ext = target_path.suffix.lower()
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
            else:
                try:
                    content = target_path.read_text(encoding="utf-8")
                except Exception as read_err:
                    return [TextContent(type="text", text=f"❌ Erreur lecture du fichier {target_path.name} : {read_err}")]

            try:
                relative = target_path.relative_to(DOCS_ROOT)
            except Exception:
                relative = target_path.name

            header = f"---\nFichier: {relative}\nProjet: D-Bot\n---\n\n"
            full_content = header + content

            # Configuration LLM optimisée pour l'insertion
            client = get_genai_client()
            if client is not None:
                from google.genai import types as genai_types
                th_budget = 0 if thinking_level_str == "minimal" else 100
                insert_cfg = genai_types.GenerateContentConfig(
                    thinking_config=genai_types.ThinkingConfig(thinking_budget=th_budget)
                )
                loop = asyncio.get_event_loop()
                async def custom_llm_insert(prompt, system_prompt=None, history_messages=[], **kwargs):
                    full_p = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                    for attempt in range(3):
                        try:
                            res = await loop.run_in_executor(
                                None,
                                lambda: client.models.generate_content(
                                    model=model_name,
                                    contents=full_p,
                                    config=insert_cfg
                                )
                            )
                            if res and res.text:
                                await asyncio.sleep(2.0)
                                return res.text
                        except Exception as ce:
                            err_s = str(ce)
                            wait_t = 15 if "429" in err_s else 2
                            print(f"⚠️ Pause retry ({attempt+1}/3) insertion {err_s[:80]}", file=sys.stderr)
                            await asyncio.sleep(wait_t)
                rag.llm_model_func = custom_llm_insert

            # Purge des anciennes versions dans doc_status et graphe
            purged_count = 0
            try:
                async with rag.doc_status._storage_lock:
                    matching_ids = [
                        d_id for d_id, d_data in rag.doc_status._data.items()
                        if os.path.basename(d_data.get("file_path", "")) == target_path.name
                    ]
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
                print(f"Info purge doc_status pour {target_path.name}: {pe}", file=sys.stderr)

            # Insertion du document
            await rag.ainsert(full_content, file_paths=[str(target_path)])

            # Synchronisation du journal d'indexation indexed_files.json
            log_file = DB_PATH / "indexed_files.json"
            log_idx = {}
            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as lf:
                        log_idx = json.load(lf)
                except Exception:
                    pass

            import hashlib
            doc_id = hashlib.md5(full_content.encode("utf-8"), usedforsecurity=False).hexdigest()
            log_idx[str(target_path.resolve())] = {
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
                f"- **Volume** : {char_count} caractères{purge_info}\n"
                f"- **Moteur LLM** : Google Gemini API (`{model_name}`)\n"
                f"- **Niveau de Raisonnement** : `{thinking_level_str}`\n"
                f"- **Base RAG** : `{DB_PATH}` (graphe et index vectoriel à jour)"
            ))]

        # On définit le mode de recherche selon l'outil standard
        llm_mode = arguments.get("llm_mode", "antigravity").lower()
        if llm_mode not in ("antigravity", "internal", "auto"):
            llm_mode = "antigravity"

        mode = "hybrid"
        query = ""

        if name == "rag_search":
            query = arguments.get("query", "")
            mode = "hybrid"
            if llm_mode in ("internal", "auto"):
                try:
                    ans = await rag.aquery(query, param=QueryParam(mode="hybrid"))
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
                    ans = await rag.aquery(query, param=QueryParam(mode="global"))
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
