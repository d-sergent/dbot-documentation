#!/opt/homebrew/bin/python3.11
"""
Primitives partagees de chunking structurel, sectionnement virtuel, hachage
normalise, filtrage du corpus et cache PDF Docling pour le RAG D-Bot.
"""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

from lightrag.lightrag import chunking_by_token_size

EXCLUDE_DIRS = {
    ".git",
    ".continue",
    "__pycache__",
    "Archives",
    "Images_ORCA",
    ".DS_Store",
    "lightrag_dbot_db",
    "00_Archives_Recherche",
    ".kilo",
    ".gemini",
    ".cursor",
    ".roo",
    "scratch",
    "cad_views",
}
EXCLUDE_FILES = {
    "ROADMAP_STRATEGIQUE_V1.md",
    "PROMPT_Audit_Etude.md",
    "PROMPT_Consolidation_Technique.md",
}
INCLUDE_EXTS = {".md", ".py", ".txt", ".png", ".jpg", ".jpeg", ".webp", ".pdf", ".svg"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
PDF_EXTS = {".pdf"}
SVG_EXTS = {".svg"}
CRITICAL_DOC_PREFIXES = (
    "FINAL_",
    "DOSSIER_TECHNIQUE_",
    "STUDY_",
    "GUIDE_COMPLET_",
    "AUDIT_",
    "SYNTHESE_METROLOGIQUE_",
)


def is_critical_doc(rel_path: str) -> bool:
    """Indique si un document releve du socle critique (PDF, SVG ou prefixe Niveau 1/2)."""
    base = os.path.basename(rel_path or "")
    ext = Path(rel_path or "").suffix.lower()
    return ext in (".pdf", ".svg") or base.startswith(CRITICAL_DOC_PREFIXES)


def resolve_gleaning_for_doc(rel_path: str, gleaning_mode: str = "adaptive") -> int:
    """Retourne 1 ou 0 pour entity_extract_max_gleaning selon la politique demandee."""
    mode = (gleaning_mode or "adaptive").strip().lower()
    if mode in ("off", "0", "none", "false"):
        return 0
    if mode in ("on", "1", "all", "true"):
        return 1
    return 1 if is_critical_doc(rel_path) else 0

SECTION_SPLIT_MIN_BYTES = int(os.environ.get("RAG_SECTION_SPLIT_MIN_BYTES", "24576"))
SECTION_SPLIT_MIN_H2 = int(os.environ.get("RAG_SECTION_SPLIT_MIN_H2", "3"))

_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
_TOC_HEADING_RE = re.compile(r"^##\s+(?:[^\w\n]*\s*)?Sommaire\b", re.IGNORECASE)
_TOC_LINK_LINE_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\[.*?\]\(#.*?\)\s*$")
_TABLE_SEP_RE = re.compile(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$")


def _exclude_tests_and_plumbing_enabled() -> bool:
    raw = os.environ.get("RAG_EXCLUDE_TESTS_AND_PLUMBING", "true").strip().lower()
    return raw not in ("0", "false", "no", "off")


def is_path_excluded(path: Path, docs_root: Path | None = None) -> bool:
    """Indique si un fichier doit etre exclu de l'indexation LightRAG D-Bot."""
    if any(excl in path.parts for excl in EXCLUDE_DIRS):
        return True
    if path.name in EXCLUDE_FILES:
        return True

    rel_parts: tuple[str, ...]
    if docs_root is not None:
        try:
            rel_parts = path.resolve().relative_to(docs_root.resolve()).parts
        except ValueError:
            rel_parts = path.parts
    else:
        rel_parts = path.parts

    if path.suffix.lower() == ".py" and _exclude_tests_and_plumbing_enabled():
        lower_parts = [p.lower() for p in rel_parts]
        if len(lower_parts) >= 2 and lower_parts[0] == "code" and lower_parts[1] == "rag":
            return True
        if docs_root is None:
            for idx in range(len(lower_parts) - 1):
                if lower_parts[idx] == "code" and lower_parts[idx + 1] == "rag":
                    return True
        name_low = path.name.lower()
        if name_low.startswith("test_") or name_low.endswith("_test.py"):
            return True
        if any(part == "tests" for part in lower_parts):
            return True

    if path.is_file():
        try:
            st_size = path.stat().st_size
            if st_size == 0:
                return True
            if path.suffix.lower() in (".md", ".py", ".txt") and st_size <= 256:
                if not path.read_text(encoding="utf-8", errors="replace").strip():
                    return True
        except OSError:
            pass

    return False


def collect_docs_files(docs_root: Path) -> list[Path]:
    """Liste les fichiers actifs eligibles a l'indexation RAG sous docs_root."""
    if not docs_root.is_dir():
        return []
    files: list[Path] = []
    for path in docs_root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in INCLUDE_EXTS:
            continue
        if is_path_excluded(path, docs_root):
            continue
        files.append(path)
    return sorted(files)


def _update_fence_state(line: str, fence_char: str | None, fence_len: int) -> tuple[str | None, int]:
    """Suit l'ouverture/fermeture des blocs de code Markdown (backticks ou tildes)."""
    m = _FENCE_RE.match(line)
    if not m:
        return fence_char, fence_len
    marker = m.group(1)
    ch = marker[0]
    ln = len(marker)
    if fence_char is None:
        return ch, ln
    if ch == fence_char and ln >= fence_len and line.strip() == marker:
        return None, 0
    return fence_char, fence_len


def strip_markdown_toc(text: str) -> str:
    """Supprime les sections '## Sommaire' purement navigationnelles hors blocs de code."""
    if not text:
        return ""
    lines = text.splitlines()
    out: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    in_toc = False

    for line in lines:
        fence_char, fence_len = _update_fence_state(line, fence_char, fence_len)
        in_fence = fence_char is not None
        if not in_fence:
            if in_toc:
                if line.startswith("## ") and not _TOC_HEADING_RE.match(line):
                    in_toc = False
                    out.append(line)
                continue
            if _TOC_HEADING_RE.match(line):
                in_toc = True
                continue
        out.append(line)
    return "\n".join(out)


def normalize_content_for_hash(text: str, ext: str = ".md") -> str:
    """Normalise fins de ligne, espaces terminaux et sommaires avant calcul SHA-256."""
    norm = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    norm = "\n".join(line.rstrip(" \t") for line in norm.split("\n"))
    if (ext or "").lower() == ".md":
        norm = strip_markdown_toc(norm)
    norm = re.sub(r"\n{3,}", "\n\n", norm)
    return norm.strip()


def compute_normalized_sha256(text: str, ext: str = ".md") -> str:
    """Empreinte SHA-256 deterministe insensible au bruit de formatage et sommaires."""
    normalized = normalize_content_for_hash(text, ext=ext)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_doc_id(content: str) -> str:
    """Identifiant MD5 canonique compatible LightRAG."""
    return "doc-" + hashlib.md5(content.strip().encode("utf-8"), usedforsecurity=False).hexdigest()


def _split_outside_fences(text: str, heading_prefix: str) -> list[str]:
    """Decoupe un texte Markdown sur un prefixe de titre (ex. '## ') hors code fences."""
    parts: list[str] = []
    buf: list[str] = []
    fence_char: str | None = None
    fence_len = 0

    for line in text.splitlines(keepends=True):
        prev_in_fence = fence_char is not None
        fence_char, fence_len = _update_fence_state(line, fence_char, fence_len)
        if not prev_in_fence and fence_char is None and line.startswith(heading_prefix):
            if buf:
                parts.append("".join(buf))
                buf = []
        buf.append(line)

    if buf:
        parts.append("".join(buf))
    return parts


def _has_markdown_headings(text: str) -> bool:
    """Verifie la presence d'au moins un titre '## ' ou '### ' hors bloc de code."""
    fence_char: str | None = None
    fence_len = 0
    for line in text.splitlines():
        prev_in_fence = fence_char is not None
        fence_char, fence_len = _update_fence_state(line, fence_char, fence_len)
        if not prev_in_fence and fence_char is None:
            if line.startswith("## ") or line.startswith("### "):
                return True
    return False


def _token_len(tokenizer: Any, text: str) -> int:
    return len(tokenizer.encode(text))


def _is_metadata_only_preamble(preamble: str) -> bool:
    """Indique si l'en-tete avant le premier '## ' ne contient que YAML/titre H1/regles."""
    stripped = preamble.strip()
    if not stripped:
        return True
    body = re.sub(r"^---\s*\n.*?\n---\s*(?:\n+|$)", "", stripped, count=1, flags=re.DOTALL).strip()
    meaningful = [
        ln.strip()
        for ln in body.splitlines()
        if ln.strip() and not ln.strip().startswith("# ") and ln.strip() != "---"
    ]
    return len(meaningful) == 0


def _split_oversized_block(
    tokenizer: Any,
    block: str,
    max_tokens: int,
    overlap_tokens: int,
) -> list[str]:
    """Decoupe un bloc > max_tokens par paragraphes/tables Markdown avant repli fenetre."""
    if _token_len(tokenizer, block) <= max_tokens:
        return [block.strip()]

    lines = block.splitlines(keepends=True)
    # Capture un eventuel prefixe contextuel [Section parente : ...] + titre ###
    prefix_lines: list[str] = []
    body_start = 0
    for idx, ln in enumerate(lines[:3]):
        st = ln.strip()
        if st.startswith("[Section parente :") or st.startswith("## ") or st.startswith("### "):
            prefix_lines.append(ln)
            body_start = idx + 1
        elif not st and prefix_lines:
            prefix_lines.append(ln)
            body_start = idx + 1
        else:
            break

    header_prefix = "".join(prefix_lines).strip()
    rest = "".join(lines[body_start:]).strip()
    if not rest:
        return [
            c["content"].strip()
            for c in chunking_by_token_size(tokenizer, block, None, False, overlap_tokens, max_tokens)
            if str(c.get("content", "")).strip()
        ]

    # Decoupe en paragraphes hors fences
    paragraphs: list[str] = []
    cur: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    for ln in rest.splitlines(keepends=True):
        prev_in = fence_char is not None
        fence_char, fence_len = _update_fence_state(ln, fence_char, fence_len)
        if not prev_in and fence_char is None and not ln.strip():
            if cur:
                paragraphs.append("".join(cur).strip())
                cur = []
        else:
            cur.append(ln)
    if cur:
        paragraphs.append("".join(cur).strip())

    # Eclate un tableau Markdown trop gros ligne par ligne en repetant son en-tete
    atomic_units: list[str] = []
    for para in paragraphs:
        if _token_len(tokenizer, para) <= max_tokens - 64:
            atomic_units.append(para)
            continue
        p_lines = para.splitlines()
        if (
            len(p_lines) >= 3
            and p_lines[0].lstrip().startswith("|")
            and _TABLE_SEP_RE.match(p_lines[1])
        ):
            tbl_header = p_lines[0] + "\n" + p_lines[1]
            cur_rows = [tbl_header]
            for row in p_lines[2:]:
                cand = "\n".join(cur_rows + [row])
                if _token_len(tokenizer, cand) <= max_tokens - 64 or len(cur_rows) == 1:
                    cur_rows.append(row)
                else:
                    atomic_units.append("\n".join(cur_rows))
                    cur_rows = [tbl_header, row]
            if cur_rows:
                atomic_units.append("\n".join(cur_rows))
        else:
            for sc in chunking_by_token_size(
                tokenizer, para, None, False, overlap_tokens, max(256, max_tokens - 64)
            ):
                txt_sc = str(sc.get("content", "")).strip()
                if txt_sc:
                    atomic_units.append(txt_sc)

    out: list[str] = []
    buf = header_prefix
    for unit in atomic_units:
        cand = f"{buf}\n\n{unit}".strip() if buf else unit
        if _token_len(tokenizer, cand) <= max_tokens:
            buf = cand
        else:
            if buf and buf != header_prefix:
                out.append(buf)
            fresh = f"{header_prefix}\n\n{unit}".strip() if header_prefix else unit
            if _token_len(tokenizer, fresh) <= max_tokens:
                buf = fresh
            else:
                for sc in chunking_by_token_size(tokenizer, unit, None, False, overlap_tokens, max_tokens):
                    txt_sc = str(sc.get("content", "")).strip()
                    if txt_sc:
                        out.append(txt_sc)
                buf = ""
    if buf and buf != header_prefix:
        out.append(buf)
    return out or [block.strip()]


def chunking_markdown_anchored(
    tokenizer: Any,
    content: str,
    split_by_character: str | None = None,
    split_by_character_only: bool = False,
    chunk_overlap_token_size: int = 150,
    chunk_token_size: int = 1600,
) -> list[dict[str, Any]]:
    """
    Decoupage ancre sur les titres Markdown '##' et '###' pour stabiliser les empreintes
    de chunks et ne jamais invalider les sections non modifiees en cascade.

    Respecte exactement le contrat legacy LightRAG (6 parametres positionnels).
    """
    if not content or not content.strip():
        return []

    if split_by_character is not None or split_by_character_only or not _has_markdown_headings(content):
        return chunking_by_token_size(
            tokenizer,
            content,
            split_by_character,
            split_by_character_only,
            chunk_overlap_token_size,
            chunk_token_size,
        )

    max_tok = max(128, int(chunk_token_size or 1600))
    overlap_tok = max(0, int(chunk_overlap_token_size or 0))

    h2_parts = [p.strip() for p in _split_outside_fences(content, "## ") if p.strip()]
    if len(h2_parts) >= 2 and not h2_parts[0].startswith("## ") and _is_metadata_only_preamble(h2_parts[0]):
        h2_parts[1] = f"{h2_parts[0]}\n\n{h2_parts[1]}"
        h2_parts = h2_parts[1:]

    raw_chunks: list[str] = []
    for h2_block in h2_parts:
        # Frontiere stricte entre blocs '##' : on ne fusionne jamais deux H2 distincts
        if _token_len(tokenizer, h2_block) <= max_tok:
            raw_chunks.append(h2_block)
            continue

        h3_parts = [sp.strip() for sp in _split_outside_fences(h2_block, "### ") if sp.strip()]
        h2_heading = ""
        for ln in h2_block.splitlines():
            if ln.startswith("## "):
                h2_heading = ln.strip()
                break

        pack_cap = int(max_tok * 0.75)
        cur_buf = ""
        for sp in h3_parts:
            prefixed = (
                f"[Section parente : {h2_heading}]\n{sp}"
                if h2_heading and not sp.startswith("## ") and not sp.startswith(h2_heading)
                else sp
            )
            if not cur_buf:
                if _token_len(tokenizer, prefixed) <= max_tok:
                    cur_buf = prefixed
                else:
                    raw_chunks.extend(_split_oversized_block(tokenizer, prefixed, max_tok, overlap_tok))
                continue

            cur_tok = _token_len(tokenizer, cur_buf)
            cand = f"{cur_buf}\n\n{sp}"
            if cur_tok < 250 and _token_len(tokenizer, cand) <= pack_cap:
                cur_buf = cand
            else:
                raw_chunks.append(cur_buf)
                if _token_len(tokenizer, prefixed) <= max_tok:
                    cur_buf = prefixed
                else:
                    raw_chunks.extend(_split_oversized_block(tokenizer, prefixed, max_tok, overlap_tok))
                    cur_buf = ""

        if cur_buf:
            raw_chunks.append(cur_buf)

    results: list[dict[str, Any]] = []
    for idx, ch_txt in enumerate(raw_chunks):
        cleaned = ch_txt.strip()
        if not cleaned:
            continue
        results.append(
            {
                "tokens": _token_len(tokenizer, cleaned),
                "content": cleaned,
                "chunk_order_index": len(results),
            }
        )
    if not results:
        return chunking_by_token_size(
            tokenizer,
            content,
            split_by_character,
            split_by_character_only,
            overlap_tok,
            max_tok,
        )
    return results


def _slugify_section(title: str) -> str:
    """Convertit un titre de section Markdown en slug ASCII compact (<= 48 car.)."""
    nfd = unicodedata.normalize("NFKD", title or "")
    ascii_txt = "".join(ch for ch in nfd if not unicodedata.combining(ch)).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_txt).strip("-")
    return (slug[:48].strip("-")) or "section"


def _is_pure_toc_h2(h2_block: str) -> bool:
    """Identifie une section '## Sommaire' ne contenant que des liens internes."""
    lines = [ln.strip() for ln in h2_block.splitlines() if ln.strip()]
    if not lines or not _TOC_HEADING_RE.match(lines[0]):
        return False
    body_lines = [ln for ln in lines[1:] if ln != "---"]
    if not body_lines:
        return True
    return all(_TOC_LINK_LINE_RE.match(ln) for ln in body_lines)


def split_markdown_into_virtual_sections(
    raw_markdown: str,
    rel_path: str,
    *,
    min_bytes: int | None = None,
    min_h2: int | None = None,
) -> list[dict[str, Any]] | None:
    """
    Decoupe un gros document Markdown (>= min_bytes et >= min_h2 sections H2) en
    sous-documents virtuels independants pour l'indexation incrementale LightRAG.

    Retourne None si le fichier doit rester un document monolithique.
    """
    eff_min_bytes = SECTION_SPLIT_MIN_BYTES if min_bytes is None else max(0, int(min_bytes))
    eff_min_h2 = SECTION_SPLIT_MIN_H2 if min_h2 is None else max(2, int(min_h2))

    if not raw_markdown or len(raw_markdown.encode("utf-8")) < eff_min_bytes:
        return None

    parts = [p.strip() for p in _split_outside_fences(raw_markdown, "## ") if p.strip()]
    if not parts:
        return None

    preamble = ""
    h2_blocks: list[str] = []
    if not parts[0].startswith("## "):
        preamble = parts[0]
        h2_blocks = parts[1:]
    else:
        h2_blocks = parts

    kept_h2 = [blk for blk in h2_blocks if not _is_pure_toc_h2(blk)]
    if len(kept_h2) < eff_min_h2:
        return None

    sections: list[dict[str, Any]] = []
    used_slugs: dict[str, int] = {}
    file_name = Path(rel_path).name

    def _alloc_slug(raw_slug: str) -> str:
        cnt = used_slugs.get(raw_slug, 0) + 1
        used_slugs[raw_slug] = cnt
        return raw_slug if cnt == 1 else f"{raw_slug}-{cnt}"

    if preamble:
        # Retire un eventuel frontmatter YAML natif avant de verifier si l'intro a du contenu utile
        body_no_yaml = re.sub(r"^---\s*\n.*?\n---\s*(?:\n+|$)", "", preamble, count=1, flags=re.DOTALL).strip()
        meaningful_intro = [
            ln.strip()
            for ln in body_no_yaml.splitlines()
            if ln.strip() and not ln.strip().startswith("# ") and ln.strip() != "---"
        ]
        if meaningful_intro:
            sec_key = _alloc_slug("intro")
            sec_title = "Introduction et En-tête"
            full_content = (
                f"---\n"
                f"Fichier: {rel_path}\n"
                f"Section: {sec_key}\n"
                f"SectionTitre: {sec_title}\n"
                f"Projet: D-Bot\n"
                f"---\n\n"
                f"# {file_name} — {sec_title}\n\n"
                f"{body_no_yaml}"
            ).strip()
            sections.append(
                {
                    "section_key": sec_key,
                    "section_title": sec_title,
                    "content": full_content,
                    "content_sha256": compute_normalized_sha256(body_no_yaml, ext=".md"),
                    "doc_id": compute_doc_id(full_content),
                }
            )

    for blk in kept_h2:
        first_line = blk.splitlines()[0]
        sec_title = first_line[3:].strip() if first_line.startswith("## ") else "Section"
        sec_key = _alloc_slug(_slugify_section(sec_title))
        sec_body = blk.strip()
        full_content = (
            f"---\n"
            f"Fichier: {rel_path}\n"
            f"Section: {sec_key}\n"
            f"SectionTitre: {sec_title}\n"
            f"Projet: D-Bot\n"
            f"---\n\n"
            f"# {file_name} — {sec_title}\n\n"
            f"{sec_body}"
        ).strip()
        sections.append(
            {
                "section_key": sec_key,
                "section_title": sec_title,
                "content": full_content,
                "content_sha256": compute_normalized_sha256(sec_body, ext=".md"),
                "doc_id": compute_doc_id(full_content),
            }
        )

    return sections if len(sections) >= 2 else None


def is_entity_summary_prompt(prompt: str, history_messages: list | None = None) -> bool:
    """Detecte les appels LightRAG de synthese/resume de descriptions lors de fusions."""
    if history_messages:
        return False
    p = prompt or ""
    if "Description List:" not in p:
        return False
    return ("---Task---" in p) or ("summarize" in p.lower())


def extract_pdf_text_cached(path: Path, db_path: Path | None = None) -> str:
    """Extrait le texte d'un PDF via Docling (repli pypdf) avec cache disque par SHA-256."""
    pdf_bytes = path.read_bytes()
    pdf_sha = hashlib.sha256(pdf_bytes).hexdigest()[:16]
    cache_file: Path | None = None
    if db_path is not None:
        cache_dir = Path(db_path) / ".docling_cache"
        cache_file = cache_dir / f"{pdf_sha}.md"
        if cache_file.is_file():
            try:
                cached_txt = cache_file.read_text(encoding="utf-8")
                if cached_txt.strip():
                    return cached_txt
            except OSError:
                pass

    extracted = ""
    try:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        result = converter.convert(str(path))
        md_text = result.document.export_to_markdown()
        if md_text and md_text.strip():
            extracted = md_text
    except Exception:
        extracted = ""

    if not extracted:
        import pypdf

        reader = pypdf.PdfReader(path)
        pages_text: list[str] = []
        for idx, page in enumerate(reader.pages, 1):
            txt = page.extract_text()
            if txt and txt.strip():
                pages_text.append(f"--- Page {idx} ---\n{txt.strip()}")
        extracted = "\n\n".join(pages_text)

    if cache_file is not None and extracted.strip():
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(prefix=f".{pdf_sha}.", dir=str(cache_file.parent))
            tmp_path = Path(tmp_name)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    fh.write(extracted)
                tmp_path.replace(cache_file)
            except Exception:
                if tmp_path.exists():
                    tmp_path.unlink()
                raise
        except OSError:
            pass

    return extracted


_GLUED_RECORD_RE = re.compile(
    r"(?<!^)(?<!\n)(?=(?:entity|relation)<\|#\|>)|(?<=<\|#\|>)(?=(?:entity|relation)#[^<\n]+<\|#\|>)",
    re.IGNORECASE,
)
_GLUED_COMPLETE_RE = re.compile(r"([^\n])(<\|COMPLETE\|>)")
_HASH_RECORD_PREFIX_RE = re.compile(r"^(entity|relation)#([^<\n]+<\|#\|>)", re.IGNORECASE)


def sanitize_lightrag_extraction_output(text: str) -> str:
    """Nettoie les anomalies syntaxiques LLM benignes (<|#|> terminal, collage, entity#...)."""
    if not isinstance(text, str) or ("<|#|>" not in text and "<|COMPLETE|>" not in text):
        return text

    normalized = _GLUED_RECORD_RE.sub("\n", text)
    normalized = _GLUED_COMPLETE_RE.sub(r"\1\n\2", normalized)

    cleaned_lines: list[str] = []
    for raw_line in normalized.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = _HASH_RECORD_PREFIX_RE.sub(lambda m: f"{m.group(1).lower()}<|#|>{m.group(2)}", line)
        low = line.lower()
        if low.startswith("entity<|#|>") or low.startswith("relation<|#|>"):
            while line.endswith("<|#|>"):
                line = line[:-5].rstrip()
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
