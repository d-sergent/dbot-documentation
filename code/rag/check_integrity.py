import asyncio
import os
import argparse
import json
import re
from pathlib import Path
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from fastembed import TextEmbedding
import openai
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

_REPO_ENV = Path(__file__).resolve().parent.parent.parent / ".env"
if _REPO_ENV.exists():
    load_dotenv(dotenv_path=_REPO_ENV)
else:
    load_dotenv()

# ─── Configuration ────────────────────────────────────────────────────────────
BASE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation"
WORKING_DIR = os.environ.get("RAG_DB_PATH", "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db")
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
async def get_llm_func(args):
    if args.provider == "local":
        base_url = os.environ.get("VMLX_BASE_URL", "http://127.0.0.1:8888/v1").strip().rstrip("/")
        model = args.model or os.environ.get("VMLX_MODEL", "unsloth/Qwen3.8-27B-GGUF")
        api_key = os.environ.get("VMLX_API_KEY") or os.environ.get("UNSLOTH_API_KEY") or "EMPTY"
        print(f"🔗 Audit via LOCAL : Unsloth / vMLX sur {base_url} ({model})")
    elif args.provider == "gemini":
        base_url = "https://generativelanguage.googleapis.com/v1/openai/"
        model = args.model or "models/gemini-1.5-flash"
        api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Clé API Gemini manquante.")
        print(f"🚀 Audit via CLOUD : Google Gemini ({model})")
    elif args.provider == "openrouter":
        base_url = "https://openrouter.ai/api/v1"
        model = args.model or "tencent/hy3-preview:free"
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("Clé API OpenRouter manquante.")
        print(f"🌐 Audit via OPENROUTER : Modèle de raisonnement ({model})")

    async def llm_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        client = openai.AsyncOpenAI(base_url=base_url, api_key=api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for msg in history_messages or []:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})

        allowed = ["max_tokens", "temperature", "top_p", "presence_penalty", "response_format", "extra_body"]
        req_kwargs = {k: v for k, v in kwargs.items() if k in allowed}

        if args.provider == "local":
            enable_thinking = os.environ.get("RAG_ENABLE_THINKING", "false").strip().lower() in ("1", "true", "yes")
            req_kwargs.setdefault("max_tokens", 4096)
            req_kwargs.setdefault("temperature", 1.0 if enable_thinking else 0.1)
            req_kwargs.setdefault("top_p", 0.95 if enable_thinking else 0.80)
            req_kwargs.setdefault("presence_penalty", 0.0 if enable_thinking else 1.0)
            extra_body = {
                "chat_template_kwargs": {"enable_thinking": enable_thinking},
                "top_k": kwargs.get("top_k", 20),
                "min_p": kwargs.get("min_p", 0.0),
                "repeat_penalty": kwargs.get("repeat_penalty", 1.0),
            }
            if isinstance(req_kwargs.get("extra_body"), dict):
                extra_body.update(req_kwargs["extra_body"])
            req_kwargs["extra_body"] = extra_body
        else:
            req_kwargs.setdefault("temperature", 0.1)
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
            raise RuntimeError(f"Réponse LLM vide ({args.provider}, finish_reason={finish})")
        return content
    return llm_func

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

    llm_func = await get_llm_func(args)

    # Initialisation du RAG
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_func,
        embedding_func=EmbeddingFunc(embedding_dim=1024, max_token_size=8192, func=fastembed_func)
    )
    
    await rag.initialize_storages()
    
    print(f"--- Début de l'Audit d'Intégrité D-Bot ---")
    
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(f"# 🛡️ Rapport d'Intégrité de la Documentation D-Bot\n")
        f.write(f"> **Date de génération** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> **Modèle utilisé** : `{args.provider}` ({args.model or 'default'})\n\n")
        f.write("Ce rapport est généré automatiquement via le système **Graph-RAG**.\n\n")
        
        for title, query in AUDITS.items():
            print(f"Analyse en cours : {title}...")
            f.write(f"## {title}\n")
            try:
                # Mode global sans reranker pour l'audit complet (évite les warnings inutiles)
                response = await rag.aquery(query, param=QueryParam(mode="global", enable_rerank=False))
                f.write(f"{response}\n\n---\n\n")
            except Exception as e:
                print(f"❌ Erreur sur {title}: {e}")
                f.write(f"❌ Erreur lors de cet audit : {e}\n\n---\n\n")
            print(f"Terminé : {title}")
    
    print(f"\n✅ Rapport d'intégrité généré : {REPORT_PATH}")
    
    # Générer le fichier JSON structuré avec les questions
    generate_questions_json(REPORT_PATH, QUESTIONS_JSON_PATH)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["local", "gemini", "openrouter"], default="local")
    parser.add_argument("--api-key", type=str)
    parser.add_argument("--model", type=str)
    parser.add_argument("--clear-cache", action="store_true", help="Forcer une nouvelle génération en vidant le cache")
    args = parser.parse_args()
    asyncio.run(run_audit(args))
