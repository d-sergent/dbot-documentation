# D-Bot Project Rules

## Documentation and Knowledge Base Search (RAG)
- Whenever you need to search or verify details about the D-Bot project (such as mechanical specs, electronics, motor choices, wiring, CAN bus, or software components), you MUST query the local RAG database first.
- To perform this query, run the following command using the shell:
  `/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode naive "<your search terms>"`
- Always prioritize the retrieved context over general model knowledge for D-Bot specifications, measurements, and layouts.

## Interaction & Workflow Rules
- ALWAYS provide a detailed text explanation of the problem, diagnosis, and proposed code changes FIRST in your response message BEFORE invoking any `git push` or tool execution.
- NEVER run `git push` or execute modifying commands without explaining the rationale to the user beforehand in the text output.

## Jetson Package Management & PyTorch GPU Protection
- **JetPack Python Package Protection**: When installing any Python package via `pip` or suggesting installation commands for the Jetson Orin Nano, ALWAYS append the `--no-deps` flag (e.g. `pip install <package> --no-deps`).
- **NEVER** run `pip install torch` or `pip install torchvision` without `--no-deps` or without using the official NVIDIA JetPack 6.1 wheel, to prevent overwriting the native CUDA 12.2 GPU bindings.

## Session Lifecycle & Context Persistence
- **Session Startup**: At the beginning of any work session, ALWAYS consult the latest entry in `05_Gestion_Projet/JOURNAL_DE_BORD.md` and review the current active level in `05_Gestion_Projet/ROADMAP_STRATEGIQUE_V1.md` to immediately get up to speed with current project status.
- **Periodic Journal Updates**: Do NOT update `JOURNAL_DE_BORD.md` after every minor interaction or routine fix. Instead, accumulate progress and only update `05_Gestion_Projet/JOURNAL_DE_BORD.md` periodically (at major milestones or when completing a full work session) with a clean, consolidated summary.
- **Session Closure & RAG Sync**: When concluding a full work session or when the user indicates the session is ending, ask the user if they wish to record the final session summary in `05_Gestion_Projet/JOURNAL_DE_BORD.md`, update checkmarks in `ROADMAP_STRATEGIQUE_V1.md` / `todo_court_terme.md`, and execute the RAG re-indexing command:
  `/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/index_docs.py"`

## Text Formatting & Unit Representation
- **No LaTeX formatting for plain text measurements or units**: Do NOT use LaTeX math syntax (such as `$0.5\text{ m}$`, `$500\text{ mm}$`, `$30\text{ FPS}$`, `$81^\circ$`) for standard text responses or markdown documentation. ALWAYS write numbers and units in clean plain text (e.g. `0,5 m` or `0.5 m`, `500 mm`, `30 FPS`, `81°`).
