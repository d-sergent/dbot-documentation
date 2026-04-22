import os
import sys
import tempfile
import wave
import time
import collections
import pyaudio
import webrtcvad

# Permet d'importer nos modules D-Bot locaux même si le script est lancé de n'importe où
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dbot.audio.stt import LocalSTT
from dbot.audio.tts import LocalTTS
from dbot.brain.llm_client import DbotBrain


def get_respeaker_pyaudio_index():
    """Détecte l'index PyAudio du ReSpeaker (canaux d'entrée uniquement)."""
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info.get('maxInputChannels', 0) > 0 and \
           ("reSpeaker" in info.get('name', '') or "XVF3800" in info.get('name', '')):
            name = info.get('name', '')
            p.terminate()
            # Extraction du numéro de carte depuis "hw:X,0"
            alsa_hw = "plughw:0,0"
            for part in name.split(','):
                if 'hw:' in part:
                    card_num = ''.join(filter(str.isdigit, part.split('hw:')[1]))
                    if card_num:
                        alsa_hw = f"plughw:{card_num},0"
                    break
            return i, alsa_hw
    p.terminate()
    return None, None


def record_until_silence(pa_index: int, vad_aggressiveness: int = 2,
                          sample_rate: int = 16000, silence_duration: float = 1.2):
    """
    Enregistre la voix jusqu'à un silence de 'silence_duration' secondes.
    Utilise WebRTC VAD (Google) pour distinguer voix vs bruit même avec AGC matériel.

    Returns: bytes bruts PCM (16-bit mono 16kHz) ou None si timeout
    """
    vad = webrtcvad.Vad(vad_aggressiveness)

    frame_ms = 30        # WebRTC VAD supporte 10, 20 ou 30ms
    frame_size = int(sample_rate * frame_ms / 1000)   # 480 samples à 16kHz
    silence_frames = int(silence_duration * 1000 / frame_ms)

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        input_device_index=pa_index,
        frames_per_buffer=frame_size
    )

    ring_buffer = collections.deque(maxlen=silence_frames)
    triggered = False
    voiced_frames = []

    print("💭 [VAD] En attente de voix...", end='\r')

    try:
        timeout_frames = int(30 * 1000 / frame_ms)  # 30 secondes max
        for _ in range(timeout_frames):
            frame = stream.read(frame_size, exception_on_overflow=False)
            is_speech = vad.is_speech(frame, sample_rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                # Déclenche si 60% des frames récentes sont de la voix
                if ring_buffer.maxlen and num_voiced > 0.6 * ring_buffer.maxlen:
                    triggered = True
                    print("💭 [VAD] Parole captée, enregistrement en cours...")
                    voiced_frames.extend([f for f, s in ring_buffer])
                    ring_buffer.clear()
            else:
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                # Arrête si 90% des frames récentes sont du silence
                if ring_buffer.maxlen and num_unvoiced > 0.9 * ring_buffer.maxlen:
                    break
        else:
            return None  # Timeout 30s
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    if not voiced_frames:
        return None

    return b''.join(voiced_frames)


def frames_to_wav(frames: bytes, sample_rate: int = 16000) -> str:
    """Sauvegarde des frames PCM brutes dans un fichier WAV temporaire."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        wav_path = f.name
    with wave.open(wav_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(frames)
    return wav_path


def main():
    print("🤖 === D-Bot : Démarrage du Cerveau 100% Hors-Ligne === 🤖\n")

    idx, alsa_hw = get_respeaker_pyaudio_index()
    if idx is None:
        print("❌ ReSpeaker introuvable. Branchez-le sur un port USB-A et relancez le programme.")
        sys.exit(1)
    print(f"🔌 ReSpeaker détecté : index PyAudio={idx}, ALSA={alsa_hw}")

    # --- PHASE D'INITIALISATION DE L'IA ---
    try:
        tts   = LocalTTS(alsa_hw=alsa_hw)
        brain = DbotBrain(model_name="qwen2.5:3b")
        stt   = LocalSTT(model_size="small", device="cuda")
    except Exception as e:
        print(f"\n❌ Erreur sérieuse lors de l'activation des réseaux neuronaux : {e}")
        sys.exit(1)

    tts.speak("Mes réseaux neuronaux sont chargés. Je suis totalement autonome.")
    time.sleep(0.5)

    # --- BOUCLE CONVERSATIONNELLE (WebRTC VAD — Google) ---
    print("\n👀 Je vous écoute... (Appuyez sur Ctrl+C pour m'éteindre)")
    print("   [WebRTC VAD — Aggressivité 2/3 — insensible au bruit du ventilateur]")

    try:
        while True:
            # 1. ÉCOUTE — WebRTC VAD détecte la voix indépendamment du bruit de fond
            raw_frames = record_until_silence(idx, vad_aggressiveness=2)
            if raw_frames is None:
                continue  # Timeout 30s — rien entendu

            try:
                # 2. Sauvegarde WAV temporaire
                wav_path = frames_to_wav(raw_frames)

                # 3. RÉFLEXION (STT via faster-whisper sur CPU)
                user_text = stt.transcribe(wav_path)
                os.remove(wav_path)

                # DEBUG — à retirer une fois stable
                print(f"🔍 [STT DEBUG] Transcrit : '{user_text}'")

                # Filtre anti-hallucination Whisper (silence enregistré accidentellement)
                hallus = ["amara.org", "sous-titre", "merci de votre attention", "merci.", "sous titres"]
                if not user_text or len(user_text) < 2 or any(h in user_text.lower() for h in hallus):
                    print(f"   ↳ Filtré (hallucination ou vide)")
                    continue

                print(f"👤 Vous avez dit : '{user_text}'")

                # 4. CERVEAU (LLM via Ollama)
                ai_response = brain.generate_response(user_text)
                brain.trim_memory(max_messages=10)

                # 5. PAROLE (TTS via Piper)
                tts.speak(ai_response)
                print("\n👀 À l'écoute...")

            except Exception as e:
                import traceback
                print(f"\n❌ Erreur dans la boucle IA :")
                traceback.print_exc()
                print("   → Reprise de l'écoute...\n")

    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt manuel du système robotique.")


if __name__ == "__main__":
    main()
