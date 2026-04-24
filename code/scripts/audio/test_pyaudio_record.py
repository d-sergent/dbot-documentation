import pyaudio
import wave
import sys

SAMPLE_RATE = 16000
FRAME_SIZE = 320  # 20ms
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "test_pyaudio_default.wav"

def test_record():
    p = pyaudio.PyAudio()

    print("==================================================")
    print("  D-Bot — Test d'Enregistrement PyAudio par Défaut")
    print("==================================================")
    
    try:
        # On utilise None pour forcer le même comportement que le VAD
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=SAMPLE_RATE,
                        input=True,
                        input_device_index=None,
                        frames_per_buffer=FRAME_SIZE)
    except Exception as e:
        print(f"❌ Erreur d'ouverture du flux : {e}")
        p.terminate()
        sys.exit(1)

    print("\n🎤 PARLEZ MAINTENANT ! (Enregistrement de 5 secondes...)")

    frames = []
    for _ in range(0, int(SAMPLE_RATE / FRAME_SIZE * RECORD_SECONDS)):
        data = stream.read(FRAME_SIZE, exception_on_overflow=False)
        frames.append(data)

    print("✅ Enregistrement terminé.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))

    print(f"💾 Fichier sauvegardé sous : {WAVE_OUTPUT_FILENAME}")
    print("👉 Transférez ce fichier sur votre Mac et écoutez-le !")

if __name__ == "__main__":
    test_record()
