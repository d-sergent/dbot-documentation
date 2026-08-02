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
        description="Recherche sémantique dans la documentation D-Bot (RAG D-Bot)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Exemples :
  rag "moteur RS04 spécifications"        # Contexte précis (mode local/naive)
  rag --search "impact d'une hausse de masse"  # Recherche sémantique hybride
  rag --topics "mécanique"                 # Liste des thématiques
""",
    )
    parser.add_argument("query", nargs="*", help="Question ou sujet à rechercher")
    parser.add_argument("--search", action="store_true", help="Recherche sémantique hybride (rag_search)")
    parser.add_argument("--topics", action="store_true", help="Liste les thématiques indexées")
    args = parser.parse_args()

    query = " ".join(args.query) if args.query else input("Recherche RAG D-Bot: ").strip()
    if not query and not args.topics:
        parser.error("Une question est requise (ou utilisez --topics)")

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
            if args.search:
                result = await session.call_tool("rag_search", {"query": query})
            elif args.topics:
                result = await session.call_tool("rag_list_topics", {"domain": query})
            else:
                result = await session.call_tool("rag_get_context", {"topic": query})

            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)


if __name__ == "__main__":
    asyncio.run(main())
