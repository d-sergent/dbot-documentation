import sys
import os
import time
import json
import base64
import asyncio
import numpy as np
import io

# Configuration du PYTHONPATH pour importer la stack D-Bot
WORKSPACE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation"
sys.path.append(os.path.join(WORKSPACE_DIR, "Code"))

# Chargement robuste de l'environnement (clés API, etc.)
from dbot.brain.llm_client import load_env_robust
load_env_robust()

from dbot_next.brain.llm_client_streaming import DbotBrainStreaming
from mlx_audio.tts import load as load_mlx_model
from faster_whisper import WhisperModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI(title="D-Bot Companion Server (ASR + LLM + TTS on Mac)")

# 1. Chargement de l'ASR (faster-whisper)
# On utilise le modèle "medium" en français. Il est très précis et rapide sur CPU.
# Note : ctranslate2 ne supporte pas MPS nativement sur Apple Silicon, mais tourne à très haute vitesse sur CPU (multi-threaded).
ASR_MODEL_NAME = "medium"
print(f"⏳ Chargement du modèle ASR '{ASR_MODEL_NAME}' sur CPU...")
asr_model = WhisperModel(ASR_MODEL_NAME, device="cpu", compute_type="float32")
print("✅ Modèle ASR prêt.")

# 2. Chargement du TTS (Qwen3-TTS VoiceDesign MLX)
MODEL_REPO = "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit"
INSTRUCT_FR = (
    "A deep, warm, and slightly husky masculine voice speaking with a clear French accent. "
    "The tone is calm, firm, and composed."
)
print("⏳ Chargement du modèle Qwen3-TTS VoiceDesign MLX sur le GPU...")
tts_model = load_mlx_model(MODEL_REPO)
print(f"✅ Modèle TTS chargé (Sample Rate: {tts_model.sample_rate} Hz)")

# 3. Chargement du Cerveau LLM (Gemini 2.0 Flash)
print("⏳ Initialisation du Cerveau LLM...")
brain = DbotBrainStreaming()
print("✅ Cerveau LLM prêt.")


class SessionState:
    def __init__(self):
        self.is_interrupted = False
        # Accumulateur pour les chunks audio reçus de la Jetson
        self.audio_buffer = []


@app.websocket("/conversation")
async def conversation_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔌 Client (Jetson) connecté au serveur central compagnon.")
    
    state = SessionState()
    prompts_queue = asyncio.Queue()
    
    # Boucle de réception asynchrone des messages et du flux audio micro
    async def receive_loop():
        try:
            while True:
                # On attend une notification (texte ou binaire) du client
                message = await websocket.receive()
                
                # Cas 1 : Message binaire (flux audio brut PCM de la Jetson)
                if "bytes" in message:
                    pcm_bytes = message["bytes"]
                    # Conversion des octets reçus (PCM 16-bit) en tableau numpy int16
                    chunk_np = np.frombuffer(pcm_bytes, dtype=np.int16)
                    state.audio_buffer.append(chunk_np)
                
                # Cas 2 : Message texte (commandes JSON ou prompt texte brut de test)
                elif "text" in message:
                    data = message["text"]
                    try:
                        payload = json.loads(data)
                        msg_type = payload.get("type")
                        
                        if msg_type == "start":
                            # Début de parole VAD : on vide l'accumulateur audio
                            print("🎙️  [VAD Mac] Début de parole détecté, nettoyage du buffer audio.")
                            state.audio_buffer = []
                            
                        elif msg_type == "end":
                            # Fin de parole VAD : on lance la transcription ASR
                            print("🎙️  [VAD Mac] Fin de parole détectée. Lancement de la transcription...")
                            if len(state.audio_buffer) > 0:
                                # Concaténer tout l'audio accumulé et le normaliser en float32 [-1.0, 1.0]
                                full_audio_int16 = np.concatenate(state.audio_buffer)
                                full_audio_float32 = full_audio_int16.astype(np.float32) / 32768.0
                                
                                # Lancer la transcription ASR dans un thread-pool (faster-whisper)
                                loop = asyncio.get_running_loop()
                                def transcribe_task():
                                    segments, info = asr_model.transcribe(
                                        full_audio_float32, 
                                        language="fr", 
                                        beam_size=5
                                    )
                                    return " ".join([seg.text for seg in segments]).strip()
                                
                                start_t = time.time()
                                transcribed_text = await loop.run_in_executor(None, transcribe_task)
                                print(f"🗣️  [ASR Mac] Transcrit en {(time.time() - start_t)*1000:.0f} ms : '{transcribed_text}'")
                                
                                if len(transcribed_text) > 1:
                                    # Envoyer le texte reconnu au robot (pour feedback visuel)
                                    await websocket.send_json({
                                        "type": "asr_transcription",
                                        "text": transcribed_text
                                    })
                                    # Pousser dans la file d'attente LLM
                                    await prompts_queue.put(transcribed_text)
                                else:
                                    print("ℹ️ [ASR Mac] Transcription vide ou trop courte, ignorée.")
                            
                        elif msg_type == "interrupt":
                            print("🚨 [Serveur] Signal d'interruption reçu !")
                            state.is_interrupted = True
                            
                        elif "text" in payload:
                            # Mode secours ou test direct de texte
                            await prompts_queue.put(payload["text"])
                    except json.JSONDecodeError:
                        # Texte brut direct (compatibilité)
                        await prompts_queue.put(data)
                        
        except WebSocketDisconnect:
            print("🔌 Client déconnecté (receive_loop).")
        except Exception as e:
            print(f"⚠ Erreur dans receive_loop : {e}")

    receiver_task = asyncio.create_task(receive_loop())
    
    # Boucle principale de traitement : attend un texte transcrit, appelle LLM puis génère le TTS
    try:
        while True:
            user_text = await prompts_queue.get()
            user_text = user_text.strip()
            if not user_text:
                continue
                
            state.is_interrupted = False
            print(f"👤 Requête reçue : '{user_text}'")
            
            loop = asyncio.get_running_loop()
            
            # 1. Appel LLM Gemini en streaming
            def run_gemini_stream():
                return brain.generate_response_stream(user_text)
                
            sentences_iter = await loop.run_in_executor(None, run_gemini_stream)
            
            # 2. Boucle de génération et envoi audio/texte phrase par phrase
            while not state.is_interrupted:
                def get_next_sentence():
                    try:
                        return next(sentences_iter)
                    except StopIteration:
                        return None
                        
                sentence = await loop.run_in_executor(None, get_next_sentence)
                if sentence is None:
                    break
                    
                print(f"🤖 Phrase générée : '{sentence}'")
                
                # Envoyer la phrase au robot pour affichage
                await websocket.send_json({
                    "type": "text",
                    "content": sentence
                })
                
                # 3. Inférence Qwen3-TTS en streaming
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
                    
                    await asyncio.sleep(0.005)
                
                if not state.is_interrupted:
                    await websocket.send_json({
                        "type": "audio_end"
                    })
                    
            if state.is_interrupted:
                print("🛑 Traitement interrompu au milieu de la réponse.")
                
            await websocket.send_json({
                "type": "end_of_response"
            })
            print("✅ Cycle de réponse terminé.")
            
    except WebSocketDisconnect:
        pass
    finally:
        receiver_task.cancel()
        print("🔌 Session close.")


if __name__ == "__main__":
    # Lancement du serveur unifié sur le port 8001
    uvicorn.run(app, host="0.0.0.0", port=8001)
