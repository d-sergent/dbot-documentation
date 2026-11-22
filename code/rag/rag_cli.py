#!/opt/homebrew/bin/python3.11
"""Client CLI pour le RAG D-Bot — communique via MCP avec le serveur dbot-rag."""
import argparse
import asyncio
import os
import sys

from pathlib import Path

_RAG_DIR = os.path.dirname(os.path.abspath(__file__))
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

from rag_runtime import resolve_default_db_path  # noqa: E402

PYTHON = "/opt/homebrew/bin/python3.11"
SERVER_SCRIPT = "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/mcp_lightrag_server.py"
DB_PATH = resolve_default_db_path()


async def main():
    parser = argparse.ArgumentParser(
        description="Recherche sémantique et contrôle d'intégrité dans la documentation D-Bot (RAG D-Bot)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Exemples :
  rag "moteur RS04 spécifications"             # Contexte précis (mode local/naive)
  rag --search "impact d'une hausse de masse"       # Recherche sémantique hybride
  rag --index fichier.md --provider ollama          # Indexation rapide via Ollama (qwen3.8:27b-mlx)
  rag --topics "mécanique"                      # Liste des thématiques
  rag --audit cinematique_moteurs               # Audit ciblé de cohérence cinématique
  rag --audit                                   # Audit d'intégrité global (tous les domaines)
  rag --resolve "Masse torse = 202.3g"          # Génère le plan de correction pour une décision
  rag --resolve --from-json                     # Génère le plan depuis AUDIT_QUESTION_REPONSE.json
""",
    )
    parser.add_argument("query", nargs="*", help="Question, sujet à rechercher ou décision technique")
    parser.add_argument("--index", metavar="FILE", help="Indexe un fichier spécifique au fil de l'eau (rag_index_document)")
    parser.add_argument(
        "--prepare-agent",
        nargs="?",
        const="auto",
        default=None,
        help="Prépare un lot d'indexation directe sans LLM tiers (rag_prepare_agent_index)",
    )
    parser.add_argument(
        "--commit-agent",
        metavar="JOB_ID",
        default=None,
        help="Valide et committe dans LightRAG un lot préparé par l'agent (rag_commit_agent_index)",
    )
    parser.add_argument(
        "--extractions",
        metavar="JSON_PATH",
        default=None,
        help="Chemin JSON des extractions agent pour --commit-agent",
    )
    parser.add_argument(
        "--effort-profile",
        choices=["fast", "balanced", "thorough"],
        default="balanced",
        help="Niveau de thinking adapté en mode agent (défaut: balanced = flash standard + inherit critique, jamais extra_high)",
    )
    parser.add_argument("--search", action="store_true", help="Recherche sémantique hybride (rag_search)")
    parser.add_argument("--impact", action="store_true", help="Analyse d'impact systémique de cause à effet (rag_analyze_impact)")
    parser.add_argument("--topics", action="store_true", help="Liste les thématiques indexées (rag_list_topics)")
    parser.add_argument(
        "--audit",
        nargs="?",
        const="all",
        choices=["all", "squelette_masse", "cinematique_moteurs", "electronique_bus", "perception_ia", "custom"],
        help="Audite l'intégrité de la documentation via Graph-RAG (rag_audit_integrity)"
    )
    parser.add_argument(
        "--resolve",
        action="store_true",
        help="Génère le plan de remédiation PLAN_CORRECTION.md (rag_resolve_audit)"
    )
    parser.add_argument(
        "--from-json",
        action="store_true",
        help="À utiliser avec --resolve : charge les réponses d'arbitrage depuis AUDIT_QUESTION_REPONSE.json"
    )
    parser.add_argument(
        "--llm-mode",
        choices=["antigravity", "internal", "auto"],
        default="auto",
        help="Choix du moteur d'intelligence (audit, impact, search) : 'auto' (défaut : Gemini -lite -> 1min.ai mistral-small-2603 -> Ollama gemma4:26b avec repli Antigravity), 'internal' (synthèse LLM stricte), ou 'antigravity' (extraits bruts sans LLM).",
    )
    parser.add_argument(
        "--provider",
        choices=["auto", "gemini", "1minai", "ollama", "unsloth", "openrouter"],
        default="auto",
        help="Fournisseur LLM pour --index (Gemini non-lite -> qwen3.8:27b-mlx) et --search/--audit/--impact (défaut: auto = Gemini -lite -> 1min.ai -> Ollama gemma4:26b).",
    )
    parser.add_argument(
        "--thinking-level",
        choices=["minimal", "low", "medium", "high"],
        default="low",
        help="Niveau d'effort de raisonnement Gemini (défaut: low, ignoré en mode ollama)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Modèle spécifique optionnel (défaut: cascade Gemini -> qwen3.8:27b-mlx en index, ou mistral-small-2603 / gemma4:26b en QA/audit)",
    )
    args = parser.parse_args()

    query = " ".join(args.query) if args.query else ""
    if (
        not query
        and not args.topics
        and not args.audit
        and not args.index
        and args.prepare_agent is None
        and not args.commit_agent
        and not (args.resolve and args.from_json)
    ):
        query = input("Recherche ou consigne RAG D-Bot: ").strip()
        if not query:
            parser.error("Une question, un paramètre --index, --audit, --impact ou --resolve est requis.")

    server_env = os.environ.copy()
    server_env["RAG_DB_PATH"] = DB_PATH
    server_env["PYTHONPATH"] = os.path.dirname(SERVER_SCRIPT)
    server_env.setdefault("RAG_LLM_PROVIDER", "auto")
    server_env.setdefault("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    server_env.setdefault("OLLAMA_MODEL", "qwen3.8:27b-mlx")
    server_env.setdefault("OLLAMA_QA_MODEL", "gemma4:26b")
    # UNSLOTH_BASE_URL / UNSLOTH_MODEL / UNSLOTH_API_KEY (et alias legacy VMLX_*) sont résolus depuis .env ou défauts Unsloth (:8888/v1) dans mcp_lightrag_server.py
    server_env["PYTHONWARNINGS"] = "ignore"

    from mcp.client.stdio import stdio_client, StdioServerParameters
    from mcp.client.session import ClientSession

    server_params = StdioServerParameters(
        command=PYTHON,
        args=[SERVER_SCRIPT],
        env=server_env,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            if args.prepare_agent is not None:
                prep_payload: dict = {"effort_profile": args.effort_profile}
                if args.prepare_agent not in ("auto", ""):
                    prep_payload["job_id"] = args.prepare_agent
                if args.query:
                    prep_payload["files"] = args.query
                result = await session.call_tool("rag_prepare_agent_index", prep_payload)
            elif args.commit_agent:
                commit_payload: dict = {"job_id": args.commit_agent}
                if args.extractions:
                    commit_payload["extractions_path"] = args.extractions
                result = await session.call_tool("rag_commit_agent_index", commit_payload)
            elif args.index:
                idx_prov = args.provider if args.provider in ("auto", "ollama", "gemini", "1minai") else "auto"
                index_payload = {
                    "file_path": args.index,
                    "provider": idx_prov,
                    "thinking_level": args.thinking_level,
                }
                if args.model:
                    index_payload["model"] = args.model
                result = await session.call_tool("rag_index_document", index_payload)
            elif args.audit:
                scope = args.audit
                custom_q = query if scope == "custom" else ""
                audit_payload = {
                    "scope": scope,
                    "llm_mode": args.llm_mode,
                    "custom_query": custom_q,
                    "save_report": True,
                    "provider": args.provider,
                }
                if args.model:
                    audit_payload["model"] = args.model
                result = await session.call_tool("rag_audit_integrity", audit_payload)
            elif args.impact:
                impact_payload = {
                    "scenario": query,
                    "llm_mode": args.llm_mode,
                    "provider": args.provider,
                }
                if args.model:
                    impact_payload["model"] = args.model
                result = await session.call_tool("rag_analyze_impact", impact_payload)
            elif args.resolve:
                decisions_list = [query] if query else []
                result = await session.call_tool("rag_resolve_audit", {"decisions": decisions_list, "from_json": args.from_json, "save_plan": True})
            elif args.search:
                search_payload = {
                    "query": query,
                    "llm_mode": args.llm_mode,
                    "provider": args.provider,
                }
                if args.model:
                    search_payload["model"] = args.model
                result = await session.call_tool("rag_search", search_payload)
            elif args.topics:
                result = await session.call_tool("rag_list_topics", {"domain": query})
            else:
                result = await session.call_tool("rag_get_context", {"topic": query})

            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)


if __name__ == "__main__":
    asyncio.run(main())
