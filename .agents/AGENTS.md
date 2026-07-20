# D-Bot Project Rules

## Documentation and Knowledge Base Search (RAG)
- Whenever you need to search or verify details about the D-Bot project (such as mechanical specs, electronics, motor choices, wiring, CAN bus, or software components), you MUST query the local RAG database first.
- To perform this query, run the following command using the shell:
  `/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode naive "<your search terms>"`
- Always prioritize the retrieved context over general model knowledge for D-Bot specifications, measurements, and layouts.

## Interaction & Workflow Rules
- ALWAYS provide a detailed text explanation of the problem, diagnosis, and proposed code changes FIRST in your response message BEFORE invoking any `git push` or tool execution.
- NEVER run `git push` or execute modifying commands without explaining the rationale to the user beforehand in the text output.

## Session Lifecycle & Context Persistence
- **Session Startup**: At the beginning of any work session, ALWAYS consult the latest entry in `05_Gestion_Projet/JOURNAL_DE_BORD.md` and review the current active level in `05_Gestion_Projet/ROADMAP_STRATEGIQUE_V1.md` to immediately get up to speed with current project status.
- **Session Closure & RAG Sync**: Before concluding a significant set of actions or when the user indicates the work session is ending, ALWAYS ask the user if they wish to close the session, update `05_Gestion_Projet/JOURNAL_DE_BORD.md` with the session log, update checkmarks in `ROADMAP_STRATEGIQUE_V1.md` / `todo_court_terme.md`, and execute the RAG re-indexing command:
  `/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py"`
