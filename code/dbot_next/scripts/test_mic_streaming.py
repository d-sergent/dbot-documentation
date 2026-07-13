"""
test_mic_streaming.py — Script de test d'acquisition non-bloquante pour la stack Next.
====================================================================================
- Démarre la capture audio en streaming non-bloquant
- Affiche périodiquement le niveau sonore RMS et le statut VAD du ReSpeaker
"""

import os
import sys
import time
import numpy as np

# Permet d'importer nos modules D-Bot locaux
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dbot_next.audio.audio_io_streaming import AudioIOStreaming

def main():
    print("🎤 === TEST ACQUISITION AUDIO EN STREAMING (sounddevice) === 🎤\n")
    
    def on_doa_change(angle):
        print(f"🧭 [DOA Callback] Son détecté à {angle}°.")

    try:
        audio = AudioIOStreaming(doa_callback=on_doa_change)
        audio.start_capture()
        
        print("\n👀 Capture démarrée. Parlez dans le micro ReSpeaker (Ctrl+C pour arrêter)...")
        print("{:<12} | {:<12} | {:<12}".format("Index Chunk", "Amplitude RMS", "Statut VAD"))
        print("-" * 45)
        
        chunk_idx = 0
        while True:
            chunk = audio.get_audio_chunk(timeout=0.2)
            if chunk is not None:
                chunk_idx += 1
                rms = np.sqrt(np.mean(chunk.astype(np.float32)**2))
                _, is_speech = audio.get_speech_status()
                
                # Affiche une ligne toutes les 10 chunks pour ne pas saturer le terminal
                if chunk_idx % 10 == 0:
                    print("{:<12} | {:<12.1f} | {:<12}".format(
                        chunk_idx, 
                        rms, 
                        "PAROLE" if is_speech else "silence"
                    ))
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du test.")
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
    finally:
        if 'audio' in locals():
            audio.close()

if __name__ == "__main__":
    main()
