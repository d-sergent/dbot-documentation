import sys
import os
import time
import json
import base64
import asyncio
import numpy as np
import mlx.core as mx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

# Configuration du PYTHONPATH pour importer la stack D-Bot
WORKSPACE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation"
sys.path.append(os.path.join(WORKSPACE_DIR, "Code"))

# Chargement robuste de l'environnement (clés API, etc.)
from dbot.brain.llm_client import load_env_robust
load_env_robust()

from dbot_next.brain.llm_client_streaming import DbotBrainStreaming
from mlx_audio.tts import load as load_mlx_model

app = FastAPI(title="D-Bot Central Streaming Server (Mac)")

# Modèle Qwen3-TTS VoiceDesign MLX
MODEL_REPO = "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit"
INSTRUCT_FR = (
    "A deep, warm, and slightly husky masculine voice speaking with a clear French accent. "
    "The tone is calm, firm, and composed."
)

print("⏳ Chargement du modèle Qwen3-TTS VoiceDesign MLX sur le GPU...")
tts_model = load_mlx_model(MODEL_REPO)
print(f"✅ Modèle TTS chargé (Sample Rate: {tts_model.sample_rate} Hz)")

# Cerveau Gemini / Ollama
print("⏳ Initialisation du Cerveau LLM...")
brain = DbotBrainStreaming()
print("✅ Cerveau LLM prêt.")


class SessionState:
    def __init__(self):
        self.is_interrupted = False


@app.websocket("/conversation")
async def conversation_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔌 Client connecté au serveur central.")
    
    state = SessionState()
    prompts_queue = asyncio.Queue()
    
    # Tâche en arrière-plan pour recevoir les messages (prompts et interruptions)
    async def receive_loop():
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    payload = json.loads(data)
                    msg_type = payload.get("type")
                    if msg_type == "interrupt":
                        print("🚨 [Serveur] Signal d'interruption reçu !")
                        state.is_interrupted = True
                    elif "text" in payload:
                        await prompts_queue.put(payload["text"])
                except Exception:
                    # Traiter comme un prompt brut
                    await prompts_queue.put(data)
        except WebSocketDisconnect:
            print("🔌 Client déconnecté (receive_loop).")
        except Exception as e:
            print(f"⚠ Erreur receive_loop : {e}")

    receiver_task = asyncio.create_task(receive_loop())
    
    try:
        while True:
            # Attend le prochain prompt utilisateur
            user_text = await prompts_queue.get()
            user_text = user_text.strip()
            if not user_text:
                continue
                
            # Réinitialisation de l'état d'interruption
            state.is_interrupted = False
            print(f"👤 Traitement de la requête : '{user_text}'")
            
            loop = asyncio.get_running_loop()
            
            # 1. Lancement de la génération Gemini en streaming
            # Pour pouvoir être interrompu entre chaque phrase, on consomme le générateur
            # sur le thread principal phrase par phrase (l'appel réseau lui-même est synchrone par bloc)
            def run_gemini_stream():
                return brain.generate_response_stream(user_text)
                
            # On obtient l'itérateur
            sentences_iter = await loop.run_in_executor(None, run_gemini_stream)
            
            # Boucle sur les phrases de réponse
            while not state.is_interrupted:
                # Récupère la phrase suivante sans bloquer l'event loop
                def get_next_sentence():
                    try:
                        return next(sentences_iter)
                    except StopIteration:
                        return None
                        
                sentence = await loop.run_in_executor(None, get_next_sentence)
                if sentence is None:
                    break
                    
                print(f"🤖 Phrase générée : '{sentence}'")
                
                # Envoi du texte au robot
                await websocket.send_json({
                    "type": "text",
                    "content": sentence
                })
                
                # Inférence et streaming audio par chunks
                # On utilise un générateur pour Qwen3-TTS afin de pouvoir interrompre au milieu de la phrase
                def get_tts_generator(txt):
                    return tts_model.generate(
                        text=txt,
                        instruct=INSTRUCT_FR,
                        temperature=0.6,
                        top_p=0.9,
                        repetition_penalty=1.1,
                        max_tokens=1024,
                        lang_code="french",
                        stream=True,
                        streaming_interval=0.4,
                    )
                    
                tts_iter = await loop.run_in_executor(None, get_tts_generator, sentence)
                
                while not state.is_interrupted:
                    def get_next_chunk():
                        try:
                            return next(tts_iter)
                        except StopIteration:
                            return None
                            
                    result = await loop.run_in_executor(None, get_next_chunk)
                    if result is None:
                        break
                        
                    # Conversion float32 [-1, 1] en int16 PCM
                    audio_np = np.array(result.audio)
                    pcm_int16 = (audio_np * 32767).astype(np.int16)
                    encoded_data = base64.b64encode(pcm_int16.tobytes()).decode("utf-8")
                    
                    # Envoi du chunk audio
                    await websocket.send_json({
                        "type": "audio",
                        "data": encoded_data,
                        "sample_rate": result.sample_rate
                    })
                    
                    # Permet à l'event loop d'exécuter d'autres tâches (comme la réception d'interruption)
                    await asyncio.sleep(0.005)
                    
            if state.is_interrupted:
                print("🛑 Traitement interrompu au milieu de la réponse.")
                
            # Fin de la réponse complète
            await websocket.send_json({
                "type": "end_of_response"
            })
            print("✅ Cycle de réponse terminé.")
            
    except WebSocketDisconnect:
        print("🔌 Client déconnecté du serveur central.")
    except Exception as e:
        print(f"❌ Erreur boucle principale serveur : {e}")
    finally:
        receiver_task.cancel()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
