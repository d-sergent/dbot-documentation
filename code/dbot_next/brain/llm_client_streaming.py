"""
llm_client_streaming.py — Client LLM Hybride (Gemini + Ollama) avec streaming de réponse.
========================================================================================
- Requêtes en streaming pour minimiser le Time To First Token (TTFT)
- Utilise Gemini streamGenerateContent en priorité, Ollama stream=True en secours local
- Yield des morceaux de phrase (phrases complètes) dès qu'ils sont générés
"""

import os
import time
import requests
import json
import ollama
from typing import Generator

# Importation robuste des variables d'environnement de la stack parente
from dbot.brain.llm_client import load_env_robust, DbotBrain, GEMINI_API_KEY, GEMINI_MODEL, DEFAULT_LOCAL_MODEL

class DbotBrainStreaming(DbotBrain):
    """
    Cerveau IA de D-Bot avec streaming natif (Cloud Gemini & local Ollama).
    Hérite de DbotBrain pour réutiliser l'initialisation et la mémoire.
    """
    def __init__(self, model_name: str = DEFAULT_LOCAL_MODEL):
        super().__init__(model_name=model_name)

    def generate_response_stream(self, user_text: str) -> Generator[str, None, None]:
        """
        Génère la réponse sous forme de générateur de phrases.
        Yield chaque phrase dès qu'elle est délimitée (par ponctuation) pour alimenter le TTS.
        """
        if GEMINI_API_KEY:
            try:
                yield from self._stream_gemini(user_text)
                return
            except Exception as e:
                print(f"⚠ [Cerveau Streaming] Échec Gemini ({e}). Bascule locale...")
                
        yield from self._stream_ollama(user_text)

    def _stream_gemini(self, text: str) -> Generator[str, None, None]:
        """Appel streaming à l'API Gemini via SSE."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:streamGenerateContent?key={GEMINI_API_KEY}&alt=sse"
        
        content = [{"role": "user", "parts": [{"text": self.system_prompt + "\n\n" + text}]}]
        payload = {
            "contents": content
        }
        
        # Requête SSE en continu
        res = requests.post(url, json=payload, stream=True, timeout=10)
        res.raise_for_status()
        
        sentence_buffer = ""
        punctuations = [".", "!", "?", "\n"]
        
        for line in res.iter_lines():
            if not line:
                continue
            
            line_str = line.decode('utf-8')
            if line_str.startswith("data: "):
                # Enlever le préfixe data: de SSE
                line_str = line_str[6:]
                
            try:
                # Les lignes SSE peuvent être des fragments de JSON
                data = json.loads(line_str)
                # Extraire le texte du fragment
                part = data['candidates'][0]['content']['parts'][0]
                text_chunk = part.get('text', '')
                
                # Regrouper en phrases
                for char in text_chunk:
                    sentence_buffer += char
                    if char in punctuations:
                        clean_sentence = sentence_buffer.strip()
                        if len(clean_sentence) > 3:
                            yield clean_sentence
                            sentence_buffer = ""
            except Exception:
                # Parfois la structure JSON est incomplète ou est une meta-data, on ignore
                continue
                
        # Reste du buffer si présent
        clean_sentence = sentence_buffer.strip()
        if len(clean_sentence) > 0:
            yield clean_sentence

    def _stream_ollama(self, text: str) -> Generator[str, None, None]:
        """Appel streaming à Ollama local."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text}
        ]
        
        sentence_buffer = ""
        punctuations = [".", "!", "?", "\n", ";"]
        
        try:
            response_stream = ollama.chat(
                model=self.local_model,
                messages=messages,
                stream=True
            )
            
            for chunk in response_stream:
                text_chunk = chunk['message']['content']
                for char in text_chunk:
                    sentence_buffer += char
                    if char in punctuations:
                        clean_sentence = sentence_buffer.strip()
                        if len(clean_sentence) > 3:
                            yield clean_sentence
                            sentence_buffer = ""
                            
            # Reste du buffer
            clean_sentence = sentence_buffer.strip()
            if len(clean_sentence) > 0:
                yield clean_sentence
        except Exception as e:
            print(f"❌ [Cerveau Streaming] Erreur Ollama : {e}")
            yield "Une erreur locale est survenue."
