#!/usr/bin/env python3
import os
import asyncio
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

# Charger les clés API
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# Liste des modèles (Ordre de priorité)
MODELS_FALLBACK = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "deepseek/deepseek-v4-flash:free",
    "google/gemma-4-31b-it:free",
    "openai/gpt-oss-120b:free"
]

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LOCAL_LLM_URL = "http://127.0.0.1:8001/v1" # Port pour DeepSeek-R1 sur votre machine
PROMPT_PATH = Path("/Users/Shared/Mon Google Drive Physique/Documentation/05_Gestion_Projet/PROMPT_Consolidation_Technique.md")

async def get_folder_content(folder_path: Path):
    """Concatène tous les fichiers Markdown d'un dossier."""
    content = []
    # On trie par nom pour garder un semblant d'ordre logique
    md_files = list(folder_path.glob("*.md"))
    print(f"🔍 {len(md_files)} fichiers Markdown trouvés dans {folder_path.name}")
    
    for file_path in sorted(md_files):
        if "FINAL_CONSOLIDE" in file_path.name:
            continue # Éviter de s'auto-inclure
        
        try:
            text = file_path.read_text(encoding="utf-8")
            content.append(f"### SOURCE : {file_path.name}\n\n{text}\n\n---\n")
        except Exception as e:
            print(f"⚠️ Erreur lecture {file_path.name}: {e}")
            
    return "\n".join(content)

async def call_openrouter(model_name, system_prompt, user_prompt, data_content):
    """Appelle l'API OpenRouter."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Construction du message final
    full_user_content = f"{user_prompt}\n\n--- DONNÉES SOURCES ---\n\n{data_content}"
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_content}
        ],
        "temperature": 0.1
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
    if not GEMINI_API_KEY: return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # Format spécifique Gemini
    payload = {
        "contents": [{
            "parts": [{"text": f"{system_prompt}\n\n{user_prompt}\n\n--- DONNÉES SOURCES ---\n\n{data_content}"}]
        }],
        "generationConfig": {"temperature": 0.1}
    }
    
    print(f"🚀 Tentative avec Gemini Pro (via Google AI Studio)...")
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
        "temperature": 0.1
    }
    
    data_size = len(data_content)
    print(f"📊 Volume de données : {data_size} caractères.")
    print(f"🔗 URL Cible : {url}")
    print(f"🚀 Envoi de la requête au serveur local...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Timeout de 3600 secondes (1 heure)
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
                        print(f"📝 Début de la réponse : {content[:100]}...")
                        return content
                    else:
                        print("⚠️ Le modèle a renvoyé une réponse VIDE (0 caractères).")
                        # Vérification si le contenu est dans reasoning_content (cas de DeepSeek R1)
                        if "reasoning_content" in data["choices"][0]["message"]:
                            print("💡 Note : Le modèle a uniquement généré du raisonnement, pas de texte final.")
                        return None
                else:
                    print(f"⚠️ Format JSON inattendu : {data}")
                    return None
        except Exception as e:
            print(f"⚠️ Erreur d'exception locale : {type(e).__name__} - {e}")
            return None

def extract_prompts(folder_rel_path, folder_name):
    """Extrait le System Prompt et le User Prompt en injectant les variables de dossier."""
    text = PROMPT_PATH.read_text(encoding="utf-8")
    
    # Logique simple de découpage
    try:
        system_part = text.split("### SYSTEM PROMPT")[1].split("### USER PROMPT")[0].strip().replace(">", "").strip()
        user_part = text.split("### USER PROMPT")[1].split("---")[0].strip().replace(">", "").strip()
        
        # Injection dynamique
        user_part = user_part.replace("{{FOLDER_PATH}}", str(folder_rel_path))
        user_part = user_part.replace("{{FOLDER_NAME}}", folder_name.replace("_", " "))
        
        return system_part, user_part
    except IndexError:
        raise Exception("Format du fichier PROMPT_Consolidation_Technique.md invalide.")

async def consolidate(folder_rel_path, force_local=False, local_url=None):
    root = Path("/Users/Shared/Mon Google Drive Physique/Documentation")
    folder_path = root / folder_rel_path
    
    if not folder_path.exists():
        print(f"❌ Dossier introuvable : {folder_path}")
        return

    print(f"📂 Analyse du dossier : {folder_rel_path}")
    
    # 1. Préparer les données
    data_content = await get_folder_content(folder_path)
    if not data_content:
        print("⚠️ Aucun fichier Markdown trouvé.")
        return
        
    # 2. Récupérer les prompts (Dynamiques)
    system_prompt, user_prompt = extract_prompts(folder_rel_path, folder_path.name)
    
    result = None
    
    # 3. Mode LOCAL prioritaire si demandé
    if force_local:
        result = await call_local_llm(local_url, system_prompt, user_prompt, data_content)
        if not result:
            print("❌ Échec du modèle local. Fin du script (Mode --local activé).")
            return

    # 4. Fallback Cloud (OpenRouter) - Uniquement si PAS de mode local forcé
    if not result:
        for model_name in MODELS_FALLBACK:
            try:
                result = await call_openrouter(model_name, system_prompt, user_prompt, data_content)
                if result:
                    break
            except Exception as e:
                print(f"⚠️ Échec avec {model_name} : {e}")
                continue
            
    # 5. Fallback ultime sur Gemini - Uniquement si PAS de mode local forcé
    if not result:
        try:
            result = await call_gemini(system_prompt, user_prompt, data_content)
        except Exception:
            pass
            
    # 6. Fallback final sur Local si pas déjà tenté
    if not result and not force_local:
        result = await call_local_llm(local_url, system_prompt, user_prompt, data_content)
            
    if not result:
        print("❌ Tous les modèles ont échoué.")
        return
        
    # 7. Sauvegarder le résultat
    output_name = f"FINAL_CONSOLIDE_{folder_path.name}.md"
    output_path = folder_path / output_name
    
    if output_path.exists():
        backup_name = f"FINAL_CONSOLIDE_{folder_path.name}_PREVIOUS.md"
        backup_path = folder_path / backup_name
        if backup_path.exists():
            backup_path.unlink()
        output_path.rename(backup_path)
        print(f"🔄 Version précédente archivée sous : {backup_path.name}")
        
    output_path.write_text(result, encoding="utf-8")
    
    print(f"✅ Consolidation terminée ! Fichier créé : {output_path}")

if __name__ == "__main__":
    import sys
    force_local = "--local" in sys.argv
    
    # Extraction du port si spécifié (ex: --port 8007)
    custom_port = "8001"
    if "--port" in sys.argv:
        try:
            idx = sys.argv.index("--port")
            custom_port = sys.argv[idx + 1]
        except (IndexError, ValueError):
            pass
    
    local_url = f"http://127.0.0.1:{custom_port}/v1"
    path_args = [a for a in sys.argv[1:] if a not in ["--local", "--port", custom_port]]
    
    if len(path_args) < 1:
        print("Usage: python3 consolidate_folder.py <chemin_relatif_dossier> [--local] [--port 8007]")
    else:
        asyncio.run(consolidate(path_args[0], force_local=force_local, local_url=local_url))
