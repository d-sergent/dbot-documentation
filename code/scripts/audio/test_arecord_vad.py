import subprocess
import webrtcvad
import audioop
import collections
import wave
import sys

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)
CHUNK_BYTES = FRAME_SIZE * 2  # 16-bit = 2 bytes per sample

def test_arecord_vad():
    print("==================================================")
    print("  D-Bot — Test VAD via 'arecord' direct")
    print("==================================================")

    vad = webrtcvad.Vad(3)
    
    # Lancement de arecord en tâche de fond pour capturer le flux propre de Linux
    cmd = [
        "arecord",
        "-f", "S16_LE",
        "-r", "16000",
        "-c", "1",
        "-D", "default",  # On utilise le mixeur par défaut de Linux qui fonctionne toujours
        "-q"              # Mode silencieux
    ]
    
    print("\nLancement de l'enregistrement via ALSA système...")
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"❌ Impossible de lancer arecord : {e}")
        sys.exit(1)

    print("🎤 Parlez maintenant (l'enregistrement s'arrêtera après 1.5s de silence)...")
    
    voiced_frames = []
    triggered = False
    ring_buffer = collections.deque(maxlen=int(1.5 * 1000 / FRAME_MS))
    
    try:
        while True:
            # On lit exactement la taille d'une frame VAD (960 octets)
            frame = process.stdout.read(CHUNK_BYTES)
            if not frame or len(frame) < CHUNK_BYTES:
                break
                
            is_speech = vad.is_speech(frame, SAMPLE_RATE)
            rms = audioop.rms(frame, 2)
            
            print(f"Volume RMS: {rms:5d} | VAD dit voix: {is_speech} ", end='\r')
            
            if not triggered:
                ring_buffer.append(is_speech)
                if sum(ring_buffer) > 0.8 * ring_buffer.maxlen:
                    triggered = True
                    print("\n\n   [VAD] Parole détectée ! Enregistrement en cours...")
                    voiced_frames.append(frame)
                    ring_buffer.clear()
            else:
                voiced_frames.append(frame)
                ring_buffer.append(is_speech)
                if sum(1 for s in ring_buffer if not s) > 0.9 * ring_buffer.maxlen:
                    print("\n   [VAD] Silence détecté, fin de l'enregistrement.")
                    break
                    
            if len(voiced_frames) > int(10.0 * 1000 / FRAME_MS):
                print("\n   [VAD] Durée maximale atteinte (10s).")
                break
                
    finally:
        process.kill()

    if not voiced_frames:
        print("\n❌ Aucune voix n'a été enregistrée.")
        return

    wav_path = "test_arecord_mic.wav"
    with wave.open(wav_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(voiced_frames))
        
    print(f"\n✅ Fichier sauvegardé sous : {wav_path}")

if __name__ == "__main__":
    test_arecord_vad()
