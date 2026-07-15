"""
test_companion_streaming.py — Test unitaire de la boucle conversationnelle déportée.
==================================================================================
- Se connecte au serveur compagnon unique du Mac (companion_server.py).
- Capture l'audio micro de la Jetson et utilise le VAD matériel.
- Stream l'audio PCM brut au Mac uniquement en cours d'élocution.
- Reçoit et joue la synthèse vocale retournée.
"""

import os
import sys
import time
import asyncio
import threading
import numpy as np

# Permet d'importer nos modules D-Bot locaux
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dbot_next.audio.audio_io_streaming import AudioIOStreaming
from dbot_next.audio.tts_qwen3_central_client import Qwen3CentralClient

def main():
    print("🧠 === TEST DE CONVERSATION DÉPORTÉE (ASR + LLM + TTS sur Mac) === 🧠\n")
    
    mac_ip = os.environ.get("DBOT_MAC_IP", "127.0.0.1")
    print(f"🔌 Tentative de connexion au serveur compagnon Mac ({mac_ip}:8001)...")
    
    # Initialisation du client
    client = Qwen3CentralClient(host=mac_ip, port=8001)
    
    # Flag d'état local
    state = "idle"  # idle, listening, speaking
    lock = threading.Lock()
    silence_start_time = None
    silence_threshold = 1.0  # 1 seconde de silence pour fin de phrase
    
    # Callbacks du client
    def on_asr(text):
        print(f"\n👤 Vous (Mac ASR) : '{text}'")
        nonlocal state
        with lock:
            state = "speaking"  # Le serveur commence à parler / répondre

    def on_text(content):
        print(f"🤖 D-Bot (Mac LLM) : {content}")

    def on_end():
        print("\n👀 À l'écoute...\n")
        nonlocal state
        with lock:
            state = "idle"

    client.on_asr_received = on_asr
    client.on_text_received = on_text
    client.on_response_end = on_end

    # Démarrage de l'event loop asyncio pour le WebSocket client
    loop = asyncio.new_event_loop()
    def run_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()
        
    async_thread = threading.Thread(target=run_loop, daemon=True)
    async_thread.start()

    # Connexion synchrone avec timeout
    fut = asyncio.run_coroutine_threadsafe(client.connect(), loop)
    try:
        fut.result(timeout=3.0)
        if not client._is_connected:
            print("❌ Impossible de se connecter au serveur compagnon Mac. Assurez-vous que companion_server.py est lancé.")
            return
    except Exception as e:
        print(f"❌ Erreur lors de la connexion : {e}")
        return

    print("✨ Connexion établie avec succès !")
    
    # Initialiser l'acquisition audio
    audio = AudioIOStreaming(block_size=2560)  # 160ms chunks
    audio.start_capture()
    print("\n🎙️ Prêt ! Parlez dans le micro ReSpeaker (Dites 'stop' pour interrompre, Ctrl+C pour quitter)...")

    chunk_count = 0
    try:
        while True:
            chunk = audio.get_audio_chunk(timeout=0.05)
            if chunk is None:
                continue
                
            chunk_count += 1
            max_val = np.max(np.abs(chunk))
            
            # Affichage de diagnostic du volume toutes les 15 frames (~2 secondes)
            if chunk_count % 15 == 0:
                sys.stdout.write(f"\r[Diag] Chunks: {chunk_count} | Vol Max: {max_val}  ")
                sys.stdout.flush()
                
            # Interrogation de la VAD matérielle (ReSpeaker XMOS)
            _, is_speech = audio.get_speech_status()
            
            with lock:
                if is_speech:
                    if state in ["idle", "speaking"]:
                        # Si le robot répondait, on l'interrompt immédiatement !
                        if state == "speaking":
                            print("\n🗣️ [VAD] Parole détectée. Interruption de la réponse...")
                            asyncio.run_coroutine_threadsafe(client.interrupt(), loop)
                            
                        # Notifier le début de parole au serveur
                        asyncio.run_coroutine_threadsafe(client.send_control("start"), loop)
                        state = "listening"
                        silence_start_time = None
                        print("🎙️ Écoute en cours (audio streamé au Mac)...")
                        
                    # Stream du chunk binaire vers le Mac
                    asyncio.run_coroutine_threadsafe(
                        client.send_audio_chunk(chunk.tobytes()), 
                        loop
                    )
                else:
                    if state == "listening":
                        if silence_start_time is None:
                            silence_start_time = time.time()
                        elif time.time() - silence_start_time > silence_threshold:
                            # Fin de phrase détectée
                            print("\n🎙️ [VAD] Fin de phrase. Envoi pour transcription...")
                            asyncio.run_coroutine_threadsafe(client.send_control("end"), loop)
                            state = "thinking"
                            silence_start_time = None
                            
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du test.")
    finally:
        audio.close()
        client.close()
        loop.call_soon_threadsafe(loop.stop)

if __name__ == "__main__":
    main()
