import sys
import os
import time
import json
import base64
import asyncio
import gc
import numpy as np
import mlx.core as mx
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

# 1. Initialisation de l'ASR
# Stratégie prioritaire : Groq Whisper Large v3 Turbo (cloud, < 300 ms)
# Fallback automatique : Faster-Whisper "small" CPU si Groq indisponible ou clé manquante
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
asr_mode = "local"  # Par défaut fallback local
groq_client = None

if GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        asr_mode = "groq"
        print("✅ Groq Whisper Large v3 Turbo activé (ASR Cloud, < 300 ms)")
    except ImportError:
        print("⚠ [ASR] groq non installé — fallback Faster-Whisper local.")
else:
    print("⚠ [ASR] GROQ_API_KEY absent — fallback Faster-Whisper local.")

if asr_mode == "local":
    ASR_MODEL_NAME = "small"
    print(f"⏳ Chargement du modèle ASR '{ASR_MODEL_NAME}' sur CPU...")
    from faster_whisper import WhisperModel
    asr_model = WhisperModel(ASR_MODEL_NAME, device="cpu", compute_type="float32")
    print("✅ Modèle ASR local prêt.")
else:
    asr_model = None
    from faster_whisper import WhisperModel  # Garde l'import pour le fallback runtime


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
                
                # Extraction sécurisée des champs WebSocket Starlette/ASGI
                pcm_bytes = message.get("bytes")
                text_data = message.get("text")
                
                # Cas 1 : Message binaire (flux audio brut PCM de la Jetson)
                if pcm_bytes is not None and len(pcm_bytes) > 0:
                    chunk_np = np.frombuffer(pcm_bytes, dtype=np.int16)
                    state.audio_buffer.append(chunk_np)
                
                # Cas 2 : Message texte (commandes JSON start/end/interrupt)
                elif text_data is not None and len(text_data) > 0:
                    try:
                        payload = json.loads(text_data)
                        msg_type = payload.get("type")
                        
                        if msg_type == "start":
                            # Début de parole VAD : on vide l'accumulateur audio
                            print("\n🎙️  [VAD Mac] Début de parole détecté (Signal start reçu). Nettoyage du buffer.")
                            state.audio_buffer = []
                            
                        elif msg_type == "end":
                            # Fin de parole VAD : on lance la transcription ASR
                            print(f"\n🎙️  [VAD Mac] Fin de parole détectée (Signal end). {len(state.audio_buffer)} chunks reçus.")
                            if len(state.audio_buffer) > 0:
                                # Concaténer tout l'audio accumulé
                                # IMPORTANT : AudioIOStreaming._read_parecord_loop() extrait déjà le
                                # canal gauche mono (data_np[:, 0]) avant de mettre le chunk en queue.
                                # Les chunks reçus ici sont donc déjà MONO int16 à 16 kHz.
                                # NE PAS ré-appliquer une conversion stéréo→mono ici (doublement).
                                full_audio_int16 = np.concatenate(state.audio_buffer)
                                full_audio_float32 = full_audio_int16.astype(np.float32) / 32768.0
                                duration_sec = len(full_audio_float32) / 16000.0
                                rms_vol = float(np.sqrt(np.mean(full_audio_float32**2)) * 32767.0)
                                print(f"📊 [ASR Mac] Buffer audio : {duration_sec:.2f} s | Volume RMS: {rms_vol:.1f}")
                                
                                # Sauvegarde d'un fichier WAV de débogage pour inspection sonore
                                try:
                                    import wave
                                    debug_wav_path = "/tmp/mac_debug_voice.wav"
                                    with wave.open(debug_wav_path, "wb") as wf:
                                        wf.setnchannels(1)
                                        wf.setsampwidth(2)
                                        wf.setframerate(16000)
                                        wf.writeframes(full_audio_int16.tobytes())
                                    print(f"💾 [ASR Mac] Fichier audio de débogage sauvegardé sous {debug_wav_path}")
                                except Exception as wav_err:
                                    print(f"⚠ [ASR Mac] Erreur sauvegarde WAV : {wav_err}")

                                # Filtrage préalable : ignorer les bruits brefs < 1.0s ou trop faibles
                                if duration_sec < 1.0:
                                    print(f"ℹ️ [ASR Mac] Durée audio trop courte ({duration_sec:.2f} s < 1.0 s), ignorée pour éviter l'hallucination.")
                                    state.audio_buffer = []
                                    continue

                                if rms_vol < 200.0:
                                    print(f"ℹ️ [ASR Mac] Volume sonore trop faible ({rms_vol:.1f} < 200), ignoré.")
                                    state.audio_buffer = []
                                    continue

                                # Lancer la transcription ASR dans un thread-pool
                                loop = asyncio.get_running_loop()
                                
                                def transcribe_task():
                                    text = ""
                                    
                                    if asr_mode == "groq" and groq_client is not None:
                                        # ─── Groq Whisper Large v3 Turbo (Cloud, ~200-350 ms) ───
                                        try:
                                            import io, wave as wave_mod
                                            wav_buffer = io.BytesIO()
                                            with wave_mod.open(wav_buffer, "wb") as wf:
                                                wf.setnchannels(1)
                                                wf.setsampwidth(2)
                                                wf.setframerate(16000)
                                                wf.writeframes(full_audio_int16.tobytes())
                                            wav_buffer.seek(0)
                                            transcription = groq_client.audio.transcriptions.create(
                                                file=("audio.wav", wav_buffer, "audio/wav"),
                                                model="whisper-large-v3-turbo",
                                                language="fr",
                                                response_format="text"
                                            )
                                            text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
                                        except Exception as groq_err:
                                            print(f"⚠ [ASR Groq] Erreur : {groq_err} — fallback local.")
                                            # Fallback local si Groq échoue
                                            if asr_model:
                                                segments, _ = asr_model.transcribe(full_audio_float32, language="fr", beam_size=3)
                                                text = " ".join([s.text for s in segments]).strip()
                                    else:
                                        # ─── Faster-Whisper small CPU (Local) ───────────────────
                                        segments, _ = asr_model.transcribe(
                                            full_audio_float32, 
                                            language="fr", 
                                            beam_size=3,
                                            temperature=0.0,
                                            no_speech_threshold=0.3
                                        )
                                        text = " ".join([seg.text for seg in segments]).strip()
                                    
                                    # Filtre anti-hallucinations Whisper
                                    hallucination_patterns = [
                                        "merci d'avoir", "sous-titres", "soustitres",
                                        "merci pour votre", "visionné cette vidéo",
                                        "regardé la vidéo", "c'est tout pour aujourd'hui",
                                        "c'est tout pour", "abonne", "bon visionnage", "st'501"
                                    ]
                                    if any(p in text.lower() for p in hallucination_patterns):
                                        print(f"🧹 [ASR] Hallucination détectée et nettoyée : '{text}'")
                                        return ""
                                    return text
                                
                                # ─── ⏱️ PROFILING LATENCE PIPELINE ────────────────────────────────
                                t0_end = time.time()  # Référence : instant de réception du signal "end"
                                
                                transcribed_text = await loop.run_in_executor(None, transcribe_task)
                                t_asr = time.time()
                                dt_asr_ms = (t_asr - t0_end) * 1000
                                print(f"⏱️  [PROFILING] ASR Whisper :    {dt_asr_ms:6.0f} ms → \"{transcribed_text}\"")
                                state._t0_end = t0_end  # Partager avec la boucle LLM/TTS
                                state._dt_asr_ms = dt_asr_ms
                                
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
                            else:
                                print("⚠ [ASR Mac] Buffer audio vide à la fin de phrase.")
                            
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
            t0_llm = time.time()
            print(f"\n👤 Requête LLM : '{user_text}'")
            
            loop = asyncio.get_running_loop()
            
            # 1. Appel LLM Gemini en streaming
            def run_gemini_stream():
                return brain.generate_response_stream(user_text)
                
            sentences_iter = await loop.run_in_executor(None, run_gemini_stream)
            dt_llm_ms = (time.time() - t0_llm) * 1000
            print(f"⏱️  [PROFILING] LLM 1er token : {dt_llm_ms:6.0f} ms")
            _first_tts = True
            
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
                t0_tts = time.time()
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
                dt_tts_init_ms = (time.time() - t0_tts) * 1000
                if _first_tts:
                    t0_end_ref = getattr(state, '_t0_end', t0_tts)
                    dt_total_ms = (time.time() - t0_end_ref) * 1000
                    print(f"⏱️  [PROFILING] TTS 1er chunk : {dt_tts_init_ms:6.0f} ms")
                    print(f"⏱️  [PROFILING] ━━━ LATENCE TOTALE : {dt_total_ms:6.0f} ms (fin parole → 1er audio) ━━━")
                    _first_tts = False
                
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
            try:
                mx.metal.clear_cache()
            except Exception:
                pass
            gc.collect()
            
    except WebSocketDisconnect:
        pass
    finally:
        receiver_task.cancel()
        print("🔌 Session close.")


if __name__ == "__main__":
    # Lancement du serveur unifié sur le port 8001
    uvicorn.run(app, host="0.0.0.0", port=8001)
