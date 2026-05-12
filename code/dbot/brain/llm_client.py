"""
llm_client.py — Cerveau IA de D-Bot (Architecture Hybride Gemini + Ollama)

Ce module gère la communication avec l'IA :
1. Priorité Cloud : Google Gemini 3.1 Flash (Ultra-rapide, 0 RAM sur Jetson)
2. Secours Local  : Ollama qwen2.5:0.5b (Hors-ligne, faible consommation RAM)

Prérequis :
  pip3 install requests ollama
"""

import ollama
import os
import time
import requests
import json

# Tentative de chargement du .env pour les clés API (Cloud)
env_path = os.path.join(os.path.dirname(__file__), "../../../.env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False
    print("⚠ [Cerveau] ddgs non installé. Recherche web désactivée.")

# --- CONFIGURATION ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

# Modèle de secours local (Ollama)
DEFAULT_LOCAL_MODEL = os.environ.get("DBOT_LLM_MODEL", "qwen2.5:0.5b")


def perform_web_search(query: str) -> str:
    """Interroge DuckDuckGo et retourne un résumé."""
    print(f"🔍 [Cerveau] Recherche web : '{query}'...")
    if not HAS_DDGS:
        return "Erreur : l'outil duckduckgo-search n'est pas installé."
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=2)]
            if not results:
                return "Aucun résultat trouvé."
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        return f"Erreur réseau : {e}"


# Schéma d'outil pour Gemini (Format Google)
GEMINI_TOOLS = {
    "function_declarations": [
        {
            "name": "search_web",
            "description": "Recherche des données factuelles à jour sur internet.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {"type": "STRING", "description": "Mots-clés de recherche"}
                },
                "required": ["query"]
            }
        }
    ]
}

# Schéma d'outil pour Ollama (Format OpenAI)
OLLAMA_TOOLS = [{
    'type': 'function',
    'function': {
        'name': 'search_web',
        'description': 'Recherche des données factuelles à jour sur internet.',
        'parameters': {
            'type': 'object',
            'properties': {
                'query': {'type': 'string', 'description': 'Mots-clés'}
            },
            'required': ['query']
        }
    }
}]


class DbotBrain:
    def __init__(self, model_name: str = DEFAULT_LOCAL_MODEL):
        self.local_model = model_name
        self.system_prompt = (
            "Tu es D-Bot, un robot compagnon intelligent. "
            "Réponses très concises pour l'oral. En français exclusivement. "
            "Si tu as un doute sur un fait récent, utilise l'outil search_web."
        )
        self.reset_memory()
        
        if GEMINI_API_KEY:
            print(f"🧠 [Cerveau] Mode HYBRIDE activé.")
            print(f"   ☁️  Cloud (Gemini) : {GEMINI_MODEL}")
            print(f"   🏠 Local (Secours) : {self.local_model}")
        else:
            print(f"🧠 [Cerveau] Mode LOCAL uniquement (Clé Gemini manquante).")

    def reset_memory(self):
        """Initialise la mémoire."""
        self.chat_history = [] # On gère le format différemment selon l'API

    def generate_response(self, user_text: str) -> str:
        """Génère une réponse (Gemini d'abord, Ollama si échec)."""
        if GEMINI_API_KEY:
            try:
                return self._call_gemini(user_text)
            except Exception as e:
                print(f"⚠ [Cerveau] Échec Gemini ({e}). Bascule locale...")
                return self._call_ollama(user_text)
        else:
            return self._call_ollama(user_text)

    def _call_gemini(self, text: str) -> str:
        """Appel direct à l'API Google Gemini via REST."""
        start_time = time.time()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        
        # Conversion historique format Gemini
        gemini_history = []
        # On injecte le système prompt au début si vide
        content = [{"role": "user", "parts": [{"text": self.system_prompt + "\n\n" + text}]}]
        # TODO: Implémenter le vrai historique si besoin, ici on simplifie pour la vitesse
        
        payload = {
            "contents": content,
            "tools": [GEMINI_TOOLS]
        }
        
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        candidate = data['candidates'][0]
        msg = candidate['content']['parts'][0]
        
        # Gestion des outils
        if 'functionCall' in msg:
            fn = msg['functionCall']
            if fn['name'] == 'search_web':
                query = fn['args'].get('query')
                result = perform_web_search(query)
                
                # Deuxième appel Gemini avec le résultat
                payload["contents"].append(candidate['content'])
                payload["contents"].append({
                    "role": "function",
                    "parts": [{"functionResponse": {"name": "search_web", "response": {"content": result}}}]
                })
                res = requests.post(url, json=payload, timeout=10)
                res.raise_for_status()
                msg = res.json()['candidates'][0]['content']['parts'][0]

        ai_text = msg.get('text', '')
        elapsed = time.time() - start_time
        print(f"☁️  [Cerveau] Réponse Gemini en {elapsed:.2f}s")
        return ai_text

    def _call_ollama(self, text: str) -> str:
        """Appel Ollama local."""
        start_time = time.time()
        # On prépare l'historique minimal
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text}
        ]
        try:
            response = ollama.chat(
                model=self.local_model,
                messages=messages,
                tools=OLLAMA_TOOLS
            )
            ai_text = response['message']['content']
            elapsed = time.time() - start_time
            print(f"🏠 [Cerveau] Réponse Locale en {elapsed:.2f}s ({self.local_model})")
            return ai_text
        except Exception as e:
            print(f"❌ [Cerveau] Erreur Ollama : {e}")
            return "Désolé, mes deux cerveaux sont inaccessibles."

    def trim_memory(self, max_messages: int = 10):
        pass # À implémenter si on active le multi-tour complet sur Gemini

if __name__ == "__main__":
    brain = DbotBrain()
    print(brain.generate_response("Bonjour, qui es-tu ?"))
