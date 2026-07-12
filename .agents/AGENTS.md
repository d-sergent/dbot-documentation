# D-Bot Project Rules

## Documentation and Knowledge Base Search (RAG)
- Whenever you need to search or verify details about the D-Bot project (such as mechanical specs, electronics, motor choices, wiring, CAN bus, or software components), you MUST query the local RAG database first.
- To perform this query, run the following command using the shell:
  `/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode naive "<your search terms>"`
- Always prioritize the retrieved context over general model knowledge for D-Bot specifications, measurements, and layouts.
