"""
companion_server_tts_mac.py — Serveur TTS Seul Qwen3-TTS MLX (Port 8002)

Ce serveur ultra-léger héberge EXCLUSIVEMENT la synthèse vocale Qwen3-TTS MLX 8-bit
sur le GPU Metal du Mac M1 Max. Il est utilisé par l'architecture "Jetson Direct Cloud"
où l'ASR (Groq) et le LLM (Gemini 2.0 Flash) sont exécutés directement sur la Jetson.

Port par défaut : 8002
"""

import sys
import os
import time
import json
import base64
import asyncio
import gc
import numpy as np
import mlx.core as mx

# Configuration du PYTHONPATH
WORKSPACE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation"
sys.path.append(os.path.join(WORKSPACE_DIR, "Code"))
sys.path.append(os.path.join(WORKSPACE_DIR, "code"))

from dbot.brain.llm_client import load_env_robust
load_env_robust()

from mlx_audio.tts import load as load_mlx_model
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI(title="D-Bot TTS-Only Server (Qwen3-TTS MLX on Port 8002)")

# ─── Chargement du modèle Qwen3-TTS VoiceDesign MLX sur GPU Metal ───────────
MODEL_REPO = "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit"
INSTRUCT_FR = (
    "A deep, warm, and slightly husky masculine voice speaking with a clear French accent. "
    "The tone is calm, firm, and composed."
)

print("⏳ [TTS Mac] Chargement du modèle Qwen3-TTS VoiceDesign MLX sur le GPU Metal...")
tts_model = load_mlx_model(MODEL_REPO)
SAMPLE_RATE = tts_model.sample_rate
print(f"✅ [TTS Mac] Modèle Qwen3-TTS prêt (Sample Rate: {SAMPLE_RATE} Hz) sur le port 8002")

# Lock d'exclusion mutuelle pour protéger le GPU Metal contre des inférences concurrentes
tts_lock = asyncio.Lock()


class TTSState:
    def __init__(self):
        self.is_interrupted = False


def cleanup_memory():
    """Vide le cache mémoire GPU Metal d'MLX et force la collecte du Garbage Collector."""
    try:
        mx.metal.clear_cache()
    except Exception:
        pass
    gc.collect()


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "D-Bot TTS-Only Server (Qwen3-TTS MLX)",
        "port": 8002,
        "sample_rate": SAMPLE_RATE
    }


@app.websocket("/tts")
@app.websocket("/ws")
@app.websocket("/conversation")
async def websocket_tts_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"🔌 Client (Jetson) connecté au serveur TTS Mac (Port 8002).")
    state = TTSState()

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                msg = json.loads(raw_data)
                msg_type = msg.get("type", "")

                if msg_type == "interrupt":
                    print("🚨 [TTS Mac] Signal d'interruption reçu !")
                    state.is_interrupted = True
                    continue

                if msg_type in ["synthesize", "tts_request"] or "text" in msg:
                    text_to_speak = msg.get("text", "").strip()
                    if not text_to_speak:
                        continue

                    state.is_interrupted = False
                    print(f"🗣️  [TTS Mac] Synthèse demandée pour : \"{text_to_speak}\"")
                    t0 = time.time()
                    _first_chunk_sent = False

                    async with tts_lock:
                        loop = asyncio.get_running_loop()

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

                        try:
                            tts_iter = await loop.run_in_executor(None, get_tts_generator, text_to_speak)

                            while not state.is_interrupted:
                                def get_next_chunk():
                                    try:
                                        return next(tts_iter)
                                    except StopIteration:
                                        return None
                                    except Exception as e:
                                        print(f"⚠ Erreur chunk TTS : {e}")
                                        return None

                                result = await loop.run_in_executor(None, get_next_chunk)
                                if result is None:
                                    break

                                chunk_pcm = result.audio
                                chunk_np = np.array(chunk_pcm)
                                if chunk_np.ndim > 0 and chunk_np.size > 0:
                                    int16_chunk = (chunk_np * 32767.0).clip(-32768, 32767).astype(np.int16)
                                    b64_data = base64.b64encode(int16_chunk.tobytes()).decode('utf-8')
                                    
                                    await websocket.send_json({
                                        "type": "audio_chunk",
                                        "data": b64_data,
                                        "sample_rate": getattr(result, "sample_rate", SAMPLE_RATE)
                                    })
                                    if not _first_chunk_sent:
                                        dt_ms = (time.time() - t0) * 1000
                                        print(f"⏱️  [TTS Mac] 1er chunk envoyé en {dt_ms:.0f} ms")
                                        _first_chunk_sent = True

                                await asyncio.sleep(0.001)

                        finally:
                            cleanup_memory()

                    # Signaler la fin de synthèse pour cette phrase
                    if not state.is_interrupted:
                        await websocket.send_json({"type": "tts_end"})

            except json.JSONDecodeError:
                # Format texte brut
                text_to_speak = raw_data.strip()
                if text_to_speak:
                    print(f"🗣️  [TTS Mac] Synthèse texte brut : \"{text_to_speak}\"")
                    state.is_interrupted = False
                    t0 = time.time()
                    _first_chunk_sent = False

                    async with tts_lock:
                        loop = asyncio.get_running_loop()

                        def get_tts_generator_raw(txt):
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

                        try:
                            tts_iter = await loop.run_in_executor(None, get_tts_generator_raw, text_to_speak)

                            while not state.is_interrupted:
                                def get_next_chunk():
                                    try:
                                        return next(tts_iter)
                                    except StopIteration:
                                        return None

                                result = await loop.run_in_executor(None, get_next_chunk)
                                if result is None:
                                    break

                                chunk_pcm = result.audio
                                chunk_np = np.array(chunk_pcm)
                                if chunk_np.ndim > 0 and chunk_np.size > 0:
                                    int16_chunk = (chunk_np * 32767.0).clip(-32768, 32767).astype(np.int16)
                                    b64_data = base64.b64encode(int16_chunk.tobytes()).decode('utf-8')

                                    await websocket.send_json({
                                        "type": "audio_chunk",
                                        "data": b64_data,
                                        "sample_rate": getattr(result, "sample_rate", SAMPLE_RATE)
                                    })

                                await asyncio.sleep(0.001)

                        finally:
                            cleanup_memory()

                    await websocket.send_json({"type": "tts_end"})

    except WebSocketDisconnect:
        print("🔌 Client déconnecté du serveur TTS (Port 8002).")
    except Exception as e:
        print(f"⚠ Erreur serveur TTS : {e}")
    finally:
        cleanup_memory()


if __name__ == "__main__":
    port = int(os.environ.get("DBOT_TTS_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
