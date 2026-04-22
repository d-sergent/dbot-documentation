import os
import wave
import pyaudio
import webrtcvad
import collections

# On redirige les erreurs ALSA vers /dev/null pour un affichage propre
from ctypes import *
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
try:
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
except OSError:
    pass


SAMPLE_RATE = 16000
FRAME_MS    = 30
FRAME_SIZE  = int(SAMPLE_RATE * FRAME_MS / 1000)

def get_respeaker_pyaudio_index():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info.get('maxInputChannels', 0) > 0 and \
           ("reSpeaker" in info.get('name', '') or "XVF3800" in info.get('name', '')):
            p.terminate()
            return i
    p.terminate()
    return None

def test_microphone():
    print("==================================================")
    print("  D-Bot — Test d'enregistrement WebRTC VAD")
    print("==================================================")

    idx = get_respeaker_pyaudio_index()
    if idx is None:
        print("❌ ReSpeaker introuvable via PyAudio.")
        return

    print(f"✅ ReSpeaker détecté (index {idx}).")
    
    vad = webrtcvad.Vad(3) # Agressivité max
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLE_RATE,
                    input=True,
                    input_device_index=idx,
                    frames_per_buffer=FRAME_SIZE)

    print("\n🎤 Parlez maintenant (l'enregistrement s'arrêtera après 1.5s de silence)...")
    print("Affichage du volume brut (RMS) et de la détection VAD :")
    
    voiced_frames = []
    triggered = False
    ring_buffer = collections.deque(maxlen=int(1.5 * 1000 / FRAME_MS))
    
    import audioop
    
    try:
        while True:
            frame = stream.read(FRAME_SIZE, exception_on_overflow=False)
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
        stream.stop_stream()
        stream.close()
        p.terminate()

    if not voiced_frames:
        print("❌ Aucune voix n'a été enregistrée.")
        return

    wav_path = "test_vad_mic.wav"
    with wave.open(wav_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(voiced_frames))
        
    print(f"\n✅ Fichier sauvegardé sous : {wav_path}")
    print("Copiez-le sur votre Mac pour vérifier la qualité de votre voix !")

if __name__ == "__main__":
    test_microphone()
