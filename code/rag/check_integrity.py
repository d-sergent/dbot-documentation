import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastembed import TextEmbedding
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
import numpy as np
import openai

_RAG_DIR = os.path.dirname(os.path.abspath(__file__))
if _RAG_DIR not in sys.path:
    sys.path.insert(0, _RAG_DIR)

from rag_runtime import (  # noqa: E402
    DEFAULT_OLLAMA_INDEX_MODEL,
    DEFAULT_OPENROUTER_MODEL,
    GeminiCascadeSession,
    ManagedOllamaServer,
    ModelExecutionTracker,
    OneMinAiCascadeSession,
    build_gemini_cascade,
    build_local_openai_extra_body,
    build_openai_messages,
    call_1minai_stateless_async,
    call_openai_chat_adaptive_async,
    check_ollama_ready,
    check_unsloth_ready,
    create_genai_client,
    extract_lexical_keywords,
    format_gemini_error,
    get_gemini_timeout_s,
    is_1minai_compatible_model_override,
    is_gemini_model_name,
    resolve_1minai_config,
    resolve_default_db_path,
    resolve_ollama_config,
    resolve_unsloth_config,
)
from rag_quality_audit import compute_bitemporal_doc_hierarchy  # noqa: E402

_REPO_ENV = Path(__file__).resolve().parent.parent.parent / ".env"
if _REPO_ENV.exists():
    load_dotenv(dotenv_path=_REPO_ENV)
else:
    load_dotenv()

# ─── Configuration ────────────────────────────────────────────────────────────
BASE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation"
WORKING_DIR = resolve_default_db_path()
REPORT_PATH = os.path.join(BASE_DIR, "Annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md")
QUESTIONS_JSON_PATH = os.path.join(BASE_DIR, "Annexes/Outils_de_Travail/RAG/AUDIT_QUESTION_REPONSE.json")

# ─── Fonctions Embedding ──────────────────────
import warnings
warnings.filterwarnings("ignore", message=".*intfloat/multilingual-e5-large now uses mean pooling.*")

FASTEMBED_CACHE_DIR = os.environ.get("FASTEMBED_CACHE_PATH", os.path.expanduser("~/.cache/fastembed"))

_embed_model = None
def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding("intfloat/multilingual-e5-large", cache_dir=FASTEMBED_CACHE_DIR)
    return _embed_model

async def fastembed_func(texts: list[str]) -> np.ndarray:
    model = get_embed_model()
    return np.array(list(model.embed(texts)), dtype=np.float32)

# ─── LLM Factory ─────────────────────────────────────────────────────────────
def _build_ollama_audit_llm(
    ollama_url: str,
    ollama_model: str,
    api_key: str | None,
    tracker: ModelExecutionTracker,
):
    from ask_rag import get_llm_func as _rag_get_llm_func

    base_fn = _rag_get_llm_func("ollama", model_override=ollama_model, api_key_override=api_key)

    async def tracked_ollama(prompt, system_prompt=None, history_messages=None, **kwargs):
        res = await base_fn(prompt, system_prompt=system_prompt, history_messages=history_messages or [], **kwargs)
        tracker.record_success("ollama", ollama_model)
        return res

    return tracked_ollama


def _build_openai_compat_audit_llm(
    provider_label: str,
    base_url: str,
    model: str,
    api_key: str,
    is_unsloth: bool,
    tracker: ModelExecutionTracker,
):
    async def llm_func(prompt, system_prompt=None, history_messages=None, **kwargs):
        client = openai.AsyncOpenAI(base_url=base_url, api_key=api_key, max_retries=0)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for msg in history_messages or []:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})

        allowed = ["max_tokens", "temperature", "top_p", "presence_penalty", "response_format", "extra_body"]
        req_kwargs = {k: v for k, v in kwargs.items() if k in allowed}

        if provider_label == "1minai":
            extra_params = {
                k: v
                for k, v in req_kwargs.items()
                if k in ("top_p", "presence_penalty", "response_format")
            }
            response = await call_openai_chat_adaptive_async(
                client,
                model,
                messages,
                temperature=req_kwargs.get("temperature", 0.1),
                max_tokens=req_kwargs.get("max_tokens"),
                extra_params=extra_params or None,
            )
        else:
            if is_unsloth:
                enable_thinking = os.environ.get("RAG_ENABLE_THINKING", "false").strip().lower() in (
                    "1",
                    "true",
                    "yes",
                )
                req_kwargs.setdefault("max_tokens", 4096)
                req_kwargs.setdefault("temperature", 1.0 if enable_thinking else 0.1)
                req_kwargs.setdefault("top_p", 0.95 if enable_thinking else 0.80)
                req_kwargs.setdefault("presence_penalty", 0.0 if enable_thinking else 1.0)
                extra_body = build_local_openai_extra_body()
                extra_body["chat_template_kwargs"] = {"enable_thinking": enable_thinking}
                if isinstance(req_kwargs.get("extra_body"), dict):
                    extra_body.update(req_kwargs["extra_body"])
                req_kwargs["extra_body"] = extra_body
            else:
                req_kwargs.setdefault("temperature", 0.1)
                if provider_label == "openrouter":
                    req_kwargs["extra_headers"] = {
                        "HTTP-Referer": "https://github.com/d-bot",
                        "X-Title": "D-Bot Integrity Audit",
                    }

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                **req_kwargs,
            )
        content = response.choices[0].message.content
        if not content:
            finish = response.choices[0].finish_reason
            raise RuntimeError(f"Réponse LLM vide ({provider_label}, finish_reason={finish})")
        tracker.record_success(provider_label, model)
        return content

    return llm_func


async def get_llm_func(
    args,
    tracker: ModelExecutionTracker | None = None,
    managed_ollama: ManagedOllamaServer | None = None,
):
    eff_tracker = tracker or ModelExecutionTracker(role="audit")
    ollama_url, default_ollama_model, _, _ = resolve_ollama_config(role="audit")
    unsloth_url, default_unsloth_model, unsloth_key = resolve_unsloth_config()
    gemini_key = (args.api_key or os.environ.get("GEMINI_API_KEY") or "").strip()
    openrouter_key = (os.environ.get("OPENROUTER_API_KEY") or "").strip()

    if args.provider == "ollama":
        ollama_model = (
            args.model if (args.model and not is_gemini_model_name(args.model)) else default_ollama_model
        )
        if not check_ollama_ready(ollama_url, required_model=ollama_model, timeout=0.5):
            if managed_ollama is not None:
                managed_ollama.model = ollama_model
                managed_ollama.ensure_started()
            if (
                not args.model
                and ollama_model != DEFAULT_OLLAMA_INDEX_MODEL
                and not check_ollama_ready(ollama_url, required_model=ollama_model, timeout=0.5)
                and check_ollama_ready(ollama_url, required_model=DEFAULT_OLLAMA_INDEX_MODEL, timeout=0.5)
            ):
                ollama_model = DEFAULT_OLLAMA_INDEX_MODEL
        print(f"🔗 Audit via OLLAMA : {ollama_url} ({ollama_model})")
        return _build_ollama_audit_llm(ollama_url, ollama_model, args.api_key, eff_tracker)

    if args.provider in ("local", "unsloth"):
        model = args.model or default_unsloth_model
        print(f"🔗 Audit via UNSLOTH : {unsloth_url} ({model})")
        return _build_openai_compat_audit_llm("unsloth", unsloth_url, model, unsloth_key, True, eff_tracker)

    if args.provider == "1minai":
        base_url, default_model, def_key = resolve_1minai_config(role="audit")
        om_key = (args.api_key or def_key).strip()
        if not om_key:
            raise ValueError("Clé API 1min.ai manquante (ONEMINAI_API_KEY).")
        model = (
            args.model.strip()
            if (args.model and is_1minai_compatible_model_override(args.model))
            else default_model
        )
        print(f"🪙 Audit via 1MIN.AI ({base_url}) : {model}")

        async def oneminai_audit_llm(prompt, system_prompt=None, history_messages=None, **kwargs):
            messages = build_openai_messages(prompt, system_prompt=system_prompt, history_messages=history_messages)
            content, _, _ = await call_1minai_stateless_async(
                model,
                messages,
                base_url=base_url,
                api_key=om_key,
                temperature=float(kwargs.get("temperature", 0.1)),
                max_tokens=int(kwargs.get("max_tokens", 4096)),
                timeout_s=60.0,
            )
            eff_tracker.record_success("1minai", model)
            return content

        return oneminai_audit_llm

    if args.provider == "openrouter":
        if not openrouter_key:
            raise ValueError("Clé API OpenRouter manquante.")
        model = args.model or DEFAULT_OPENROUTER_MODEL
        print(f"🌐 Audit via OPENROUTER : Modèle ({model})")
        return _build_openai_compat_audit_llm(
            "openrouter", "https://openrouter.ai/api/v1", model, openrouter_key, False, eff_tracker
        )

    gemini_cascade = build_gemini_cascade(
        "audit",
        explicit_model=args.model if is_gemini_model_name(args.model) else None,
    )
    timeout_s = get_gemini_timeout_s("audit")
    genai_client = create_genai_client(gemini_key, timeout_s=timeout_s) if gemini_key else None
    gemini_session = GeminiCascadeSession(
        gemini_cascade,
        timeout_s=timeout_s,
        thinking_budget=100,
        rpm_delay=0.0,
        wait_on_transient=False,
        tracker=eff_tracker,
    )

    if args.provider == "gemini":
        if not gemini_key:
            raise ValueError("Clé API Gemini manquante.")
        print(f"🚀 Audit via CLOUD : Cascade Gemini ({gemini_cascade[0]}...)")

        async def gemini_only(prompt, system_prompt=None, history_messages=None, **kwargs):
            text, _ = await gemini_session.call(
                genai_client,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                max_tokens=int(kwargs.get("max_tokens", 4096)),
                temperature=float(kwargs.get("temperature", 0.1)),
                tracker=eff_tracker,
            )
            if not text:
                raise RuntimeError(f"Cascade Gemini indisponible ({eff_tracker.format_summary()})")
            return text

        return gemini_only

    # Mode 'auto' : Cascade Gemini -lite -> 1min.ai (mistral-small-2603) -> Ollama (gemma4:26b / qwen3.8) -> Unsloth -> OpenRouter
    local_ollama_model = (
        args.model if (args.model and not is_gemini_model_name(args.model)) else default_ollama_model
    )
    oneminai_session = OneMinAiCascadeSession(
        role="audit",
        model_override=args.model,
        api_key_override=args.api_key if (args.api_key and not gemini_key) else None,
        timeout_s=60.0,
    )
    print(
        f"⚡ Audit AUTO : Gemini -lite ({gemini_cascade[0]}...) -> 1min.ai ({oneminai_session.model}) -> "
        f"Ollama ({local_ollama_model}) -> Unsloth ({default_unsloth_model})"
    )

    async def auto_audit_llm(prompt, system_prompt=None, history_messages=None, **kwargs):
        if genai_client is not None and not gemini_session.cloud_exhausted:
            text, _ = await gemini_session.call(
                genai_client,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                max_tokens=int(kwargs.get("max_tokens", 4096)),
                temperature=float(kwargs.get("temperature", 0.1)),
                tracker=eff_tracker,
            )
            if text:
                return text

        if kwargs.get("keyword_extraction"):
            prompt_lower = (prompt or "").lower()
            if "high_level_keywords" in prompt_lower and "low_level_keywords" in prompt_lower:
                hl, ll = extract_lexical_keywords(prompt)
                return json.dumps({"high_level_keywords": hl, "low_level_keywords": ll}, ensure_ascii=False)

        if oneminai_session.is_available:
            om_text = await oneminai_session.call(
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                temperature=kwargs.get("temperature", 0.1),
                max_tokens=kwargs.get("max_tokens", 4096),
                tracker=eff_tracker,
            )
            if om_text:
                return om_text

        ollama_ready = check_ollama_ready(ollama_url, required_model=local_ollama_model, timeout=0.5)
        if not ollama_ready and managed_ollama is not None:
            managed_ollama.model = local_ollama_model
            ollama_ready = managed_ollama.ensure_started() and check_ollama_ready(
                ollama_url, required_model=local_ollama_model, timeout=1.0
            )
        if not ollama_ready and check_ollama_ready(ollama_url, required_model=DEFAULT_OLLAMA_INDEX_MODEL, timeout=0.5):
            local_ollama_target = DEFAULT_OLLAMA_INDEX_MODEL
            ollama_ready = True
        else:
            local_ollama_target = local_ollama_model

        if ollama_ready:
            try:
                o_fn = _build_ollama_audit_llm(ollama_url, local_ollama_target, args.api_key, eff_tracker)
                return await o_fn(prompt, system_prompt=system_prompt, history_messages=history_messages, **kwargs)
            except Exception as oe:
                eff_tracker.record_failure("ollama", local_ollama_target, format_gemini_error(oe))

        if check_unsloth_ready(unsloth_url, unsloth_key, timeout=0.5):
            try:
                u_fn = _build_openai_compat_audit_llm(
                    "unsloth", unsloth_url, default_unsloth_model, unsloth_key, True, eff_tracker
                )
                return await u_fn(prompt, system_prompt=system_prompt, history_messages=history_messages, **kwargs)
            except Exception as ue:
                eff_tracker.record_failure("unsloth", default_unsloth_model, format_gemini_error(ue))

        if openrouter_key:
            or_fn = _build_openai_compat_audit_llm(
                "openrouter", "https://openrouter.ai/api/v1", DEFAULT_OPENROUTER_MODEL, openrouter_key, False, eff_tracker
            )
            return await or_fn(prompt, system_prompt=system_prompt, history_messages=history_messages, **kwargs)

        raise RuntimeError(f"Aucun backend disponible pour l'audit ({eff_tracker.format_summary()})")

    return auto_audit_llm

# ─── Définition des Audits ─────────────────────────────────────────────────────
QA_PROMPT = "\n\nIMPORTANT: Pour chaque incohérence ou chiffre divergent identifié, tu dois d'abord lister clairement les noms des fichiers sources qui se contredisent. Ensuite, tu DOIS obligatoirement générer une question précise pour l'utilisateur. Tu dois formater cette question EXACTEMENT de cette manière sur une nouvelle ligne : '**Question :** [Ta question ici]'. Ne rajoute aucun texte après la question."

AUDITS = {
    "1. Squelette (Masse & Moteurs)": 
        "Établis un tableau comparatif de la Masse Totale et du Nombre total de Moteurs RobStride cités dans les différents fichiers. Relève toute contradiction." + QA_PROMPT,
    
    "2. Cinématique (Moteurs par Axe)": 
        "Vérifie si le modèle de moteur associé à chaque articulation (Épaule, Coude, Poignet, Hanche, Genou, Cheville) est cohérent dans toute la doc. Signale si des anciens modèles apparaissent encore." + QA_PROMPT,
    
    "3. Électronique (Bus & Puissance)": 
        "Vérifie la cohérence du bus CAN (nombre de moteurs par bus) et de l'alimentation (Tension batterie) entre les synthèses et le guide électronique." + QA_PROMPT,
    
    "4. Perception & IA": 
        "Vérifie si les spécifications de la caméra OAK-D, de l'IMU principale et de la Jetson Orin Nano sont identiques partout. Note les divergences sur le matériel audio." + QA_PROMPT,
}


def build_bitemporal_audit_query(base_query: str, bitemporal: dict) -> str:
    """Enrichit une requete d'audit avec la hierarchie bi-temporelle Niveau 1 > Niveau 2."""
    pending = list((bitemporal or {}).get("pending_consolidations") or [])
    if pending:
        pending_lines = "\n".join(
            f"- {item['study_rel_path']} ({item['study_date']}) est plus recent que "
            f"{item['target_level1_rel_path']} ({item['target_level1_date']}, +{item['lead_days']} j)"
            for item in pending[:15]
        )
    else:
        pending_lines = "- Aucune etude STUDY_ plus recente que son dossier Niveau 1."

    bitemporal_rules = (
        "\n\nREGLES BI-TEMPORELLES OBLIGATOIRES (HIERARCHIE NIVEAU 1 > NIVEAU 2) :\n"
        "- Cas 1 (t_invalid — Etude STUDY_ ou AUDIT_ plus ancienne qu'un document FINAL_ / DOSSIER_TECHNIQUE_ / GUIDE_COMPLET_ / SYNTHESE_METROLOGIQUE_) : "
        "NE SIGNALE JAMAIS d'incoherence et ne pose aucune question si une valeur ancienne d'un fichier STUDY_ differe d'un dossier Niveau 1 plus recent (le Niveau 1 fait foi).\n"
        "- Cas 2 (Contradiction Niveau 1 vs Niveau 1) : signale en priorite absolue toute divergence entre deux fichiers de Niveau 1 et genere une question.\n"
        "- Cas 3 (Consolidation en attente — STUDY_ plus recent que Niveau 1) : verifie si les etudes recentes ci-dessous apportent de nouvelles valeurs non encore reportees dans le dossier Niveau 1 cible :\n"
        f"{pending_lines}"
    )

    if QA_PROMPT in base_query:
        core = base_query.replace(QA_PROMPT, "")
        return core + bitemporal_rules + QA_PROMPT
    return base_query + bitemporal_rules

def extract_questions_from_report(report_path):
    """Extrait les questions du rapport d'audit généré"""
    questions = []
    
    if not os.path.exists(report_path):
        return questions
    
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split by sections (## headers)
    sections = re.split(r'\n##+ ', content)
    
    for section in sections:
        lines = section.split('\n')
        if not lines:
            continue
        
        # Get section title from first line
        section_title = lines[0].strip().replace('#', '').strip()
        
        # Find all questions in this section
        for line in lines:
            stripped = line.strip()
            # Match various question formats
            if 'Question' in stripped and ':' in stripped:
                # Extract question text
                match = re.search(r'Question\s*:\s*\*\*?\s*(.*)', stripped)
                if match:
                    q_text = match.group(1).strip()
                    if len(q_text) >= 15 and any(ch.isalpha() for ch in q_text):
                        questions.append({
                            "section": section_title,
                            "question": q_text,
                            "answer": ""  # To be filled by user/AI
                        })

    # Deduplicate exact and truncated duplicate questions while keeping section order & longest text
    deduped = []
    for candidate in questions:
        norm_c = re.sub(r"\s+", " ", candidate["question"]).strip().lower()
        replaced = False
        duplicate = False
        for i, item in enumerate(deduped):
            norm_e = re.sub(r"\s+", " ", item["question"]).strip().lower()
            if norm_c == norm_e or (len(norm_c) >= 60 and norm_e.startswith(norm_c[:80])):
                duplicate = True
                break
            if len(norm_e) >= 60 and norm_c.startswith(norm_e[:80]) and len(norm_c) > len(norm_e):
                deduped[i] = candidate
                replaced = True
                break
        if not duplicate and not replaced:
            deduped.append(candidate)

    return deduped

def generate_questions_json(report_path, json_path):
    """Génère le fichier JSON structuré avec les questions"""
    questions = extract_questions_from_report(report_path)
    
    # Add IDs
    for i, q in enumerate(questions, 1):
        q["id"] = i
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    
    print(f"📝 Fichier JSON généré : {json_path} ({len(questions)} questions)")
    return questions

async def run_audit(args):
    if not os.path.exists(WORKING_DIR):
        print(f"Erreur: Index non trouvé dans {WORKING_DIR}")
        return

    if args.clear_cache:
        cache_path = os.path.join(WORKING_DIR, "kv_store_llm_response_cache.json")
        if os.path.exists(cache_path):
            os.remove(cache_path)
            print("🧹 Cache LLM vidé avec succès.")

    tracker = ModelExecutionTracker(
        role="audit",
        default_no_llm_label="Cache LightRAG (réponse en cache — 0 appel LLM)",
    )
    ollama_url, default_ollama_model, _, _ = resolve_ollama_config(role="audit")
    managed_ollama = ManagedOllamaServer(base_url=ollama_url, model=default_ollama_model)
    try:
        llm_func = await get_llm_func(args, tracker=tracker, managed_ollama=managed_ollama)

        # Initialisation du RAG
        rag = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=llm_func,
            embedding_func=EmbeddingFunc(embedding_dim=1024, max_token_size=8192, func=fastembed_func)
        )

        await rag.initialize_storages()

        print("--- Début de l'Audit d'Intégrité D-Bot ---")
        bitemporal = compute_bitemporal_doc_hierarchy(Path(BASE_DIR))

        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        section_blocks = []
        for title, query in AUDITS.items():
            print(f"Analyse en cours : {title}...")
            eff_query = build_bitemporal_audit_query(query, bitemporal)
            try:
                # Mode global sans reranker pour l'audit complet (évite les warnings inutiles)
                response = await rag.aquery(eff_query, param=QueryParam(mode="global", enable_rerank=False))
                section_blocks.append(f"## {title}\n{response}\n\n---\n\n")
            except Exception as e:
                print(f"❌ Erreur sur {title}: {e}")
                section_blocks.append(f"## {title}\n❌ Erreur lors de cet audit : {e}\n\n---\n\n")
            print(f"Terminé : {title}")

        trace_summary = tracker.format_summary()
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("# 🛡️ Rapport d'Intégrité de la Documentation D-Bot\n")
            f.write(f"> **Date de génération** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"> **Fournisseur demandé** : `{args.provider}` ({args.model or 'cascade/défaut'})\n")
            f.write(f"> **Moteur réel utilisé** : `{trace_summary}`\n")
            f.write(
                f"> **Filtre Bi-Temporel (`Niveau 1 > Niveau 2`)** : "
                f"`{bitemporal['level1_count']}` Niveau 1 | "
                f"`{bitemporal['level2_superseded_count']}` etudes anterieures ignorees (`t_invalid`) | "
                f"`{bitemporal['pending_consolidations_count']}` etudes recentes a consolider\n\n"
            )
            f.write("Ce rapport est généré automatiquement via le système **Graph-RAG**.\n\n")
            f.writelines(section_blocks)

        print(f"\n🧭 {trace_summary}")
        print(f"✅ Rapport d'intégrité généré : {REPORT_PATH}")

        # Générer le fichier JSON structuré avec les questions
        generate_questions_json(REPORT_PATH, QUESTIONS_JSON_PATH)
    finally:
        managed_ollama.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["auto", "gemini", "ollama", "unsloth", "local", "1minai", "openrouter"], default="auto")
    parser.add_argument("--api-key", type=str)
    parser.add_argument("--model", type=str)
    parser.add_argument("--clear-cache", action="store_true", help="Forcer une nouvelle génération en vidant le cache")
    args = parser.parse_args()
    asyncio.run(run_audit(args))
