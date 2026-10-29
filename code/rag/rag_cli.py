#!/opt/homebrew/bin/python3.11
"""Client CLI pour le RAG D-Bot — communique via MCP avec le serveur dbot-rag."""
import argparse
import asyncio
import os
import sys

PYTHON = "/opt/homebrew/bin/python3.11"
SERVER_SCRIPT = "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/mcp_lightrag_server.py"
DB_PATH = "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"


async def main():
    parser = argparse.ArgumentParser(
        description="Recherche sémantique et contrôle d'intégrité dans la documentation D-Bot (RAG D-Bot)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Exemples :
  rag "moteur RS04 spécifications"             # Contexte précis (mode local/naive)
  rag --search "impact d'une hausse de masse"       # Recherche sémantique hybride
  rag --topics "mécanique"                      # Liste des thématiques
  rag --audit cinematique_moteurs               # Audit ciblé de cohérence cinématique
  rag --audit                                   # Audit d'intégrité global (tous les domaines)
  rag --resolve "Masse torse = 202.3g"          # Génère le plan de correction pour une décision
  rag --resolve --from-json                     # Génère le plan depuis AUDIT_QUESTION_REPONSE.json
""",
    )
    parser.add_argument("query", nargs="*", help="Question, sujet à rechercher ou décision technique")
    parser.add_argument("--index", metavar="FILE", help="Indexe un fichier spécifique au fil de l'eau (rag_index_document)")
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
        default="antigravity",
        help="Choix du moteur d'intelligence (audit, impact, search) : 'antigravity' (délègue à l'agent Antigravity via votre abonnement), 'internal' (vLLM local ou OpenRouter comme avant), ou 'auto'."
    )
    parser.add_argument(
        "--thinking-level",
        choices=["minimal", "low", "medium", "high"],
        default="low",
        help="Niveau d'effort de raisonnement Antigravity (défaut: low)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-3.1-flash-lite",
        help="Modèle Gemini pour l'indexation (défaut: gemini-3.1-flash-lite)"
    )
    args = parser.parse_args()

    query = " ".join(args.query) if args.query else ""
    if not query and not args.topics and not args.audit and not args.index and not (args.resolve and args.from_json):
        query = input("Recherche ou consigne RAG D-Bot: ").strip()
        if not query:
            parser.error("Une question, un paramètre --index, --audit, --impact ou --resolve est requis.")

    server_env = os.environ.copy()
    server_env["RAG_DB_PATH"] = DB_PATH
    server_env["PYTHONPATH"] = os.path.dirname(SERVER_SCRIPT)
    server_env["VMLX_BASE_URL"] = "http://127.0.0.1:8012/v1"
    server_env["VMLX_MODEL"] = "lmstudio-community/Qwen3.6-27B-MLX-8bit"
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
            if args.index:
                result = await session.call_tool("rag_index_document", {
                    "file_path": args.index,
                    "thinking_level": args.thinking_level,
                    "model": args.model
                })
            elif args.audit:
                scope = args.audit
                custom_q = query if scope == "custom" else ""
                result = await session.call_tool("rag_audit_integrity", {
                    "scope": scope,
                    "llm_mode": args.llm_mode,
                    "custom_query": custom_q,
                    "save_report": True
                })
            elif args.impact:
                result = await session.call_tool("rag_analyze_impact", {"scenario": query, "llm_mode": args.llm_mode})
            elif args.resolve:
                decisions_list = [query] if query else []
                result = await session.call_tool("rag_resolve_audit", {"decisions": decisions_list, "from_json": args.from_json, "save_plan": True})
            elif args.search:
                result = await session.call_tool("rag_search", {"query": query, "llm_mode": args.llm_mode})
            elif args.topics:
                result = await session.call_tool("rag_list_topics", {"domain": query})
            else:
                result = await session.call_tool("rag_get_context", {"topic": query})

            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)


if __name__ == "__main__":
    asyncio.run(main())
