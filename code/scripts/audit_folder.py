#!/usr/bin/env python3
"""
audit_folder.py — Génère un rapport d'audit d'ingénierie (Design Review) pour un dossier du projet D-Bot.

Usage :
    python3 audit_folder.py <chemin_relatif_dossier> [--local] [--port 8007]

Exemples :
    python3 audit_folder.py 01_Mecanique_et_Chassis/Bras_et_Mains
    python3 audit_folder.py 00_Architecture_Centrale --local --port 8007

Comportement :
    - Charge d'abord le FINAL_CONSOLIDE_*.md du dossier (référence décision validée).
    - Charge ensuite tous les fichiers STUDY_*.md du dossier (études sources).
    - Exclut les fichiers AUDIT_ETUDE_*.md existants (pour ne pas s'auto-inclure).
    - Génère un rapport critique dans AUDIT_ETUDE_<dossier>.md.
    - Archive la version précédente en AUDIT_ETUDE_<dossier>_PREVIOUS.md.
"""
import os
import asyncio
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

# Charger les clés API
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# Liste des modèles (Ordre de priorité) — identique à consolidate_folder.py
MODELS_FALLBACK = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "deepseek/deepseek-v4-flash:free",
    "google/gemma-4-31b-it:free",
    "openai/gpt-oss-120b:free"
]

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LOCAL_LLM_URL = "http://127.0.0.1:8001/v1"
PROMPT_PATH = Path("/Users/Shared/Mon Google Drive Physique/Documentation/05_Gestion_Projet/PROMPT_Audit_Etude.md")

ROOT = Path("/Users/Shared/Mon Google Drive Physique/Documentation")


async def get_folder_content_for_audit(folder_path: Path):
    """
    Construit le contexte source pour l'audit :
    1. Le fichier FINAL_CONSOLIDE_*.md en premier (référence de décision).
    2. Tous les fichiers STUDY_*.md ensuite (études sources).
    Les fichiers AUDIT_ETUDE_*.md sont exclus pour éviter l'auto-inclusion.
    """
    content = []

    # 1. Chercher et injecter le FINAL_CONSOLIDE en premier
    final_files = list(folder_path.glob("FINAL_CONSOLIDE_*.md"))
    if final_files:
        final_file = sorted(final_files)[0]  # prendre le premier si plusieurs
        try:
            text = final_file.read_text(encoding="utf-8")
            content.append(
                f"### 📋 DOCUMENT DE RÉFÉRENCE (FINAL_CONSOLIDE) : {final_file.name}\n"
                f"*Ce document représente les décisions de conception validées pour ce module.*\n\n{text}\n\n---\n"
            )
            print(f"📋 Document de référence chargé : {final_file.name}")
        except Exception as e:
            print(f"⚠️ Erreur lecture {final_file.name}: {e}")
    else:
        print("⚠️ Aucun fichier FINAL_CONSOLIDE trouvé. L'audit sera basé uniquement sur les études.")

    # 2. Charger les fichiers STUDY_*.md
    study_files = sorted(folder_path.glob("STUDY_*.md"))
    print(f"🔍 {len(study_files)} fichier(s) STUDY_*.md trouvé(s) dans {folder_path.name}")

    for file_path in study_files:
        try:
            text = file_path.read_text(encoding="utf-8")
            content.append(f"### 📄 SOURCE D'ÉTUDE : {file_path.name}\n\n{text}\n\n---\n")
        except Exception as e:
            print(f"⚠️ Erreur lecture {file_path.name}: {e}")

    # 3. Charger les autres fichiers .md non-FINAL, non-STUDY, non-AUDIT (ex: BENCHMARK_*.md)
    other_files = sorted([
        f for f in folder_path.glob("*.md")
        if not f.name.startswith("FINAL_CONSOLIDE_")
        and not f.name.startswith("STUDY_")
        and not f.name.startswith("AUDIT_ETUDE_")
    ])
    for file_path in other_files:
        try:
            text = file_path.read_text(encoding="utf-8")
            content.append(f"### 📄 SOURCE COMPLÉMENTAIRE : {file_path.name}\n\n{text}\n\n---\n")
        except Exception as e:
            print(f"⚠️ Erreur lecture {file_path.name}: {e}")

    total = len(final_files) + len(study_files) + len(other_files)
    print(f"📚 Total : {total} fichier(s) source(s) chargé(s).")
    return "\n".join(content)


def extract_audit_prompts(folder_rel_path, folder_name):
    """Extrait le System Prompt et le User Prompt en injectant les variables de dossier."""
    text = PROMPT_PATH.read_text(encoding="utf-8")
    try:
        system_part = text.split("### SYSTEM PROMPT")[1].split("### USER PROMPT")[0].strip().replace(">", "").strip()
        user_part = text.split("### USER PROMPT")[1].split("---")[0].strip().replace(">", "").strip()

        # Injection dynamique du dossier cible
        user_part = user_part.replace("{{FOLDER_PATH}}", str(folder_rel_path))
        user_part = user_part.replace("{{FOLDER_NAME}}", folder_name.replace("_", " "))

        # Injection dans le system prompt aussi
        system_part = system_part.replace("{{FOLDER_PATH}}", str(folder_rel_path))
        system_part = system_part.replace("{{FOLDER_NAME}}", folder_name.replace("_", " "))

        return system_part, user_part
    except IndexError:
        raise Exception("Format du fichier PROMPT_Audit_Etude.md invalide.")


# ─── Fonctions d'appel API (copiées de consolidate_folder.py) ────────────────

async def call_openrouter(model_name, system_prompt, user_prompt, data_content):
    """Appelle l'API OpenRouter."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    full_user_content = f"{user_prompt}\n\n--- DONNÉES SOURCES ---\n\n{data_content}"
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_content}
        ],
        "temperature": 0.2  # Légèrement plus élevé pour la créativité des propositions
    }
    print(f"🚀 Tentative avec {model_name}...")
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Erreur API ({resp.status}): {text}")
            data = await resp.json()
            if "choices" not in data:
                raise Exception(f"Réponse API inattendue : {data}")
            return data["choices"][0]["message"]["content"]


async def call_gemini(system_prompt, user_prompt, data_content):
    """Appelle l'API Gemini (Google AI Studio)."""
    if not GEMINI_API_KEY:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}\n\n--- DONNÉES SOURCES ---\n\n{data_content}"}]}],
        "generationConfig": {"temperature": 0.2}
    }
    print("🚀 Tentative avec Gemini Pro (via Google AI Studio)...")
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                err_text = await resp.text()
                print(f"⚠️ Erreur Gemini ({resp.status}): {err_text}")
                return None
            data = await resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                print(f"⚠️ Format de réponse Gemini invalide : {data}")
                return None


async def call_local_llm(local_url, system_prompt, user_prompt, data_content):
    """Appelle le modèle local via l'API compatible OpenAI (LM Studio/MLX)."""
    url = f"{local_url}/chat/completions"
    headers = {"Content-Type": "application/json"}
    full_user_content = f"{user_prompt}\n\n--- DONNÉES SOURCES ---\n\n{data_content}"
    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_content}
        ],
        "temperature": 0.2
    }
    data_size = len(data_content)
    print(f"📊 Volume de données : {data_size} caractères.")
    print(f"🔗 URL Cible : {url}")
    print("🚀 Envoi de la requête au serveur local...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload, timeout=3600) as resp:
                print(f"📡 Réponse reçue. Code Statut : {resp.status}")
                if resp.status != 200:
                    err_body = await resp.text()
                    print(f"⚠️ Erreur du serveur local ({resp.status}): {err_body}")
                    return None
                data = await resp.json()
                if "choices" in data:
                    content = data["choices"][0]["message"]["content"]
                    if content:
                        print(f"✅ Contenu extrait avec succès ({len(content)} caractères).")
                        return content
                    else:
                        print("⚠️ Le modèle a renvoyé une réponse VIDE.")
                        return None
                else:
                    print(f"⚠️ Format JSON inattendu : {data}")
                    return None
        except Exception as e:
            print(f"⚠️ Erreur d'exception locale : {type(e).__name__} - {e}")
            return None


# ─── Fonction principale ───────────────────────────────────────────────────────

async def audit(folder_rel_path, force_local=False, force_gemini=False, local_url=None):
    folder_path = ROOT / folder_rel_path

    if not folder_path.exists():
        print(f"❌ Dossier introuvable : {folder_path}")
        return

    folder_name = folder_path.name
    print(f"\n🔍 Démarrage de l'audit du dossier : {folder_rel_path}")
    print("=" * 60)

    # 1. Préparer les données sources (FINAL + STUDY)
    data_content = await get_folder_content_for_audit(folder_path)
    if not data_content:
        print("⚠️ Aucun fichier source trouvé. Arrêt.")
        return

    # 2. Extraire les prompts d'audit
    system_prompt, user_prompt = extract_audit_prompts(folder_rel_path, folder_name)
    print(f"📝 Prompts chargés depuis : {PROMPT_PATH.name}")

    result = None

    # 3. Mode GEMINI prioritaire si demandé
    if force_gemini:
        result = await call_gemini(system_prompt, user_prompt, data_content)
        if not result:
            print("❌ Échec de Gemini 2.5 Flash (via Google AI Studio). Fin du script (Mode --gemini activé).")
            return

    # 4. Mode LOCAL prioritaire si demandé (seulement si pas déjà résolu)
    if not result and force_local:
        result = await call_local_llm(local_url, system_prompt, user_prompt, data_content)
        if not result:
            print("❌ Échec du modèle local. Fin du script (Mode --local activé).")
            return

    # 5. Fallback Cloud (OpenRouter)
    if not result:
        for model_name in MODELS_FALLBACK:
            try:
                result = await call_openrouter(model_name, system_prompt, user_prompt, data_content)
                if result:
                    break
            except Exception as e:
                print(f"⚠️ Échec avec {model_name} : {e}")
                continue

    # 6. Fallback Gemini (si pas déjà forcé en étape 3)
    if not result and not force_gemini:
        try:
            result = await call_gemini(system_prompt, user_prompt, data_content)
        except Exception:
            pass

    # 7. Fallback final local si pas déjà tenté
    if not result and not force_local:
        result = await call_local_llm(local_url, system_prompt, user_prompt, data_content)

    if not result:
        print("❌ Tous les modèles ont échoué.")
        return

    # 8. Sauvegarde avec rotation (_PREVIOUS)
    output_name = f"AUDIT_ETUDE_{folder_name}.md"
    output_path = folder_path / output_name

    if output_path.exists():
        backup_name = f"AUDIT_ETUDE_{folder_name}_PREVIOUS.md"
        backup_path = folder_path / backup_name
        if backup_path.exists():
            backup_path.unlink()
        output_path.rename(backup_path)
        print(f"🔄 Version précédente archivée sous : {backup_path.name}")

    output_path.write_text(result, encoding="utf-8")
    print(f"\n✅ Audit terminé ! Rapport créé : {output_path}")
    print(f"📊 Taille du rapport : {len(result)} caractères / {len(result.splitlines())} lignes")


if __name__ == "__main__":
    import sys

    force_local = "--local" in sys.argv
    force_gemini = "--gemini" in sys.argv

    custom_port = "8001"
    if "--port" in sys.argv:
        try:
            idx = sys.argv.index("--port")
            custom_port = sys.argv[idx + 1]
        except (IndexError, ValueError):
            pass

    local_url = f"http://127.0.0.1:{custom_port}/v1"
    path_args = [a for a in sys.argv[1:] if a not in ["--local", "--gemini", "--port", custom_port]]

    if len(path_args) < 1:
        print("Usage: python3 audit_folder.py <chemin_relatif_dossier> [--gemini] [--local] [--port 8007]")
        print("")
        print("Exemples :")
        print("  python3 audit_folder.py 01_Mecanique_et_Chassis/Bras_et_Mains --gemini")
        print("  python3 audit_folder.py 00_Architecture_Centrale --local --port 8007")
    else:
        asyncio.run(audit(path_args[0], force_local=force_local, force_gemini=force_gemini, local_url=local_url))
