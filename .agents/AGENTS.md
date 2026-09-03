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
- **ABSOLUTE ZERO TOLERANCE FOR LATEX AND DOLLAR SIGNS ($ or $$)**: NEVER use LaTeX math syntax, dollar signs, or LaTeX symbols (such as `$0.5\text{ m}$`, `$\varnothing 80\text{ mm}$`, `$\pm 0,02^\circ$`, `$$...$$`, `\text{...}`, `\varnothing`, `\pm`, `\approx`, `\circ`, `\sqrt{...}`, `\mathbf{...}`) in text responses, chat messages, markdown documentation, artifacts (plans, walkthroughs), or code comments. ALWAYS write angles, ranges, diameters, tolerances, formulas, calculations, variables, and units in clean plain text (e.g. `0.5 m`, `500 mm`, `Ø 80 mm`, `+/- 0.02 deg`, `M_stat ~ 110 Nm`, `36.8 MPa`, `Delta_theta`, `Sigma_max`, `R_vis = sqrt(21^2 + 21^2) = 29.7 mm`). Every formula must be written in standard readable ASCII / plain text.

## Technical Diagrams & Schematics Generation
- **Systematic High-Quality SVG Vector Blueprints**: Whenever a technical, mechanical, electrical, or architectural diagram/schematic is needed in documentation or markdown files, NEVER use ASCII art or basic graph flowcharts (like Mermaid) which lack spatial proportions and native preview support.
- **SVG Generation Standard**: ALWAYS generate a dedicated, standalone SVG vector file in the local `./media/` directory (e.g. `./media/<diagram_name>.svg`) and embed it into markdown using `![Description](./media/<diagram_name>.svg)`.
- **Design Specifications for SVG Schematics**:
  - **Theme**: Dark technical blueprint aesthetic (`#0f172a` background canvas, `#1e293b` panel cards, subtle `#2a324b` grid background).
  - **Layout**: Multi-panel view layout (e.g., Vue de Face / Vue de Dessus / Vue de Profil) with clear titles.
  - **Visual Elements**: Color-coded material gradients (Aluminium, Tube Carbone, Moteurs QDD, Batteries), callout text, dimension lines, and a technical legend box.
- **Mandatory Markdown Image Embedding**: NEVER create, generate, or save any image file (PNG, JPG, SVG, WebP) in the workspace without IMMEDIATELY embedding and referencing it in a corresponding active Markdown document (e.g. `![Description](./media/<image_name>.png)`). No orphan media files are allowed in the repository.

## Documentation Structure & Navigation
- **Systematic Table of Contents (Sommaire Cliquable)** : In every main technical Markdown document (`.md`), ALWAYS include a structured `## 📑 Sommaire` / `## 📑 Sommaire Général` at the beginning of the file (immediately after the header / intro callout) with markdown anchor links (`[Titre](#slug-ancre)`) pointing directly to all major sections (`##`) and sub-sections (`###`).

