"""
test_stt_streaming.py — Test de la transcription ASR Nemotron en streaming.
========================================================================
- Capture l'audio du ReSpeaker en temps réel (sounddevice)
- Transmet les frames à StreamingSTTNemotron
- Affiche la transcription en continu à l'écran
"""

import os
import sys
import time

# Permet d'importer nos modules D-Bot locaux
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dbot_next.audio.audio_io_streaming import AudioIOStreaming
from dbot_next.audio.stt_streaming import StreamingSTTNemotron

def main():
    print("🧠 === TEST DE TRANSCRIPTION EN CONTINU (ASR Nemotron 3.5) === 🧠\n")
    
    # Callback d'interruption mot-clé
    def on_interrupt():
        print("\n🚨 [TEST] SIGNAL D'INTERRUPTION DÉCLENCHÉ (Mot-clé détecté) !")

    try:
        # Initialiser l'acquisition (160ms chunks pour correspondre au frame_len de 0.16s)
        audio = AudioIOStreaming(block_size=2560) # 2560 samples = 160ms à 16kHz
        
        # Initialiser l'ASR
        stt = StreamingSTTNemotron(
            model_name="nvidia/nemotron-3.5-asr-streaming-0.6b",
            device="cpu",
            frame_len=0.16,
            interrupt_callback=on_interrupt
        )
        
        audio.start_capture()
        print("\n🎤 Prêt ! Parlez dans le micro ReSpeaker (Dites 'stop' pour tester l'interruption, Ctrl+C pour quitter)...")
        
        last_text = ""
        while True:
            chunk = audio.get_audio_chunk(timeout=0.1)
            if chunk is not None:
                # Transcrire le chunk
                text = stt.process_chunk(chunk)
                if text and text != last_text:
                    # Affichage à la volée
                    sys.stdout.write(f"\r📝 Transcription : {text}")
                    sys.stdout.flush()
                    last_text = text
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du test.")
    except Exception as e:
        print(f"\n❌ Erreur critique : {e}")
    finally:
        if 'audio' in locals():
            audio.close()

if __name__ == "__main__":
    main()
