import os
import requests
import json
import time
from dotenv import load_dotenv

# Charger la clé du .env
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key or "<VOTRE_CLE" in api_key:
    print("❌ Erreur : La clé API OpenRouter n'est pas configurée dans le .env")
    exit(1)

MODELS_TO_TEST = [
    "tencent/hy3-preview:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "qwen/qwen-2.5-coder-32b-instruct:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "liquid/lfm2.5-1.2b-thinking:free",
    "google/gemini-2.0-flash-lite-preview-02-05:free"
]

print(f"📡 Test de connectivité OpenRouter pour {len(MODELS_TO_TEST)} modèles...\n")

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/d-bot" # Bonnes pratiques OpenRouter
}

for model in MODELS_TO_TEST:
    print(f"🔍 Test du modèle : {model}")
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Réponds par un seul mot (en majuscules) : 'FONCTIONNEL'"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            res_json = response.json()
            content = res_json['choices'][0]['message']['content'].strip()
            print(f"  ✅ Succès ! Réponse : {content}\n")
        elif response.status_code == 429:
            print(f"  ⚠️ Quota dépassé (429) ou Rate-limit amont atteint.\n")
        elif response.status_code == 404:
            print(f"  ❌ Erreur 404 : Le endpoint ou le modèle n'existe plus.\n")
        else:
            print(f"  ❌ Erreur API ({response.status_code}) : {response.text}\n")
    except Exception as e:
        print(f"  ❌ Erreur réseau : {e}\n")
        
    time.sleep(1) # Petite pause pour éviter le rate-limiting trop agressif

