import sys
import os
import time
import json
import base64
import asyncio
import numpy as np
import soundfile as sf

# Configuration du PYTHONPATH
WORKSPACE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation"
sys.path.append(os.path.join(WORKSPACE_DIR, "Code"))

from dbot_next.audio.tts_qwen3_central_client import Qwen3CentralClient

async def main():
    print("🚀 Démarrage du benchmark de l'architecture centralisée...")
    
    # Initialisation du client pointant sur localhost
    client = Qwen3CentralClient(host="127.0.0.1", port=8001)
    
    # Callback pour mesurer la latence du premier texte
    t_start = time.perf_counter()
    first_text_time = None
    first_audio_time = None
    audio_data_received = []
    
    def on_text(text):
        nonlocal first_text_time
        if first_text_time is None:
            first_text_time = time.perf_counter() - t_start
            print(f"⏱️ Premier texte reçu en : {first_text_time:.3f}s")
        print(f"🤖 [Texte] : {text}")
        
    client.on_text_received = on_text
    
    # Pour le benchmark, on court-circuite write_audio_chunk pour enregistrer les octets reçus
    original_write = client.write_audio_chunk
    def mock_write(data):
        nonlocal first_audio_time
        if first_audio_time is None:
            first_audio_time = time.perf_counter() - t_start
            print(f"⏱️ Premier chunk audio (TTFA) reçu en : {first_audio_time:.3f}s ⚡")
        audio_data_received.append(data)
        
    client.write_audio_chunk = mock_write

    # Connexion au serveur local
    await client.connect()
    
    if not client._is_connected:
        print("❌ Impossible de se connecter au serveur. Assurez-vous que server_qwen3_central.py tourne sur le port 8001.")
        return
        
    # Envoi d'un prompt test
    prompt = "Bonjour D-Bot, raconte-moi une blague courte."
    print(f"👤 Envoi du prompt : '{prompt}'")
    t_start = time.perf_counter()
    
    await client.send_prompt(prompt)
    
    # Attend la fin de la réponse
    loop_count = 0
    while client._is_connected and loop_count < 30:
        await asyncio.sleep(0.5)
        loop_count += 1
        # Si on a fini la réponse, on s'arrête
        if first_audio_time and len(audio_data_received) > 0 and client.play_process is None:
            # Fin détectée
            break
            
    print("\n📊 Résultats du benchmark :")
    if first_text_time:
        print(f"  - Latence Premier Texte (Gemini) : {first_text_time:.3f}s")
    if first_audio_time:
        print(f"  - Latence Premier Audio (TTFA Qwen3) : {first_audio_time:.3f}s")
        
    if audio_data_received:
        all_audio = b"".join(audio_data_received)
        audio_np = np.frombuffer(all_audio, dtype=np.int16).astype(np.float32) / 32767.0
        out_file = "/Users/davidsergent/Downloads/benchmark_central_out.wav"
        sf.write(out_file, audio_np, 24000)
        print(f"✅ Fichier audio généré enregistré sous : {out_file}")
    else:
        print("❌ Aucun audio reçu.")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
