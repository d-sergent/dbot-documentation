import os
import sys
import tempfile
import wave
import time
import collections
import subprocess
import webrtcvad

# Ajout du chemin pour les modules D-Bot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dbot.audio.stt import LocalSTT
from dbot.audio.tts import LocalTTS

SAMPLE_RATE = 16000
FRAME_MS    = 30
FRAME_SIZE  = int(SAMPLE_RATE * FRAME_MS / 1000)

def get_respeaker_alsa_hw() -> str:
    """Détecte l'index ALSA (plughw:X,0) du ReSpeaker."""
    try:
        out = subprocess.check_output(["arecord", "-l"], text=True)
        for line in out.splitlines():
            if "carte" in line and ("reSpeaker" in line or "XVF3800" in line):
                card_num = line.split("carte ")[1].split(":")[0].strip()
                return f"plughw:{card_num},0"
            if "card" in line and ("reSpeaker" in line or "XVF3800" in line):
                card_num = line.split("card ")[1].split(":")[0].strip()
                return f"plughw:{card_num},0"
    except Exception:
        pass
    return "plughw:0,0"

def get_pulse_device_name() -> str:
    """Détecte le périphérique PulseAudio d'entrée du ReSpeaker (évite le .monitor)."""
    try:
        out = subprocess.check_output(["pactl", "list", "short", "sources"], text=True)
        for line in out.splitlines():
            # On cherche impérativement 'input' et on exclut '.monitor'
            if "reSpeaker" in line or "XVF3800" in line:
                if "input" in line and ".monitor" not in line:
                    return line.split()[1]
        # Fallback si 'input' n'est pas explicite
        for line in out.splitlines():
            if ("reSpeaker" in line or "XVF3800" in line) and ".monitor" not in line:
                return line.split()[1]
    except Exception:
        pass
    return None

def main():
    print("🔊 === TEST BOUCLE AUDIO D-BOT (STT -> TTS) === 🔊")
    
    device_name = get_pulse_device_name()
    alsa_hw = get_respeaker_alsa_hw()
    
    if not device_name:
        print("❌ ReSpeaker introuvable. Vérifiez la connexion USB.")
        return

    print(f"✅ Micro (PulseAudio): {device_name}")
    print(f"✅ HP (ALSA): {alsa_hw}")

    # Initialisation IA
    print("\n⏳ Chargement des modèles STT et TTS (Faster-Whisper + Piper)...")
    stt = LocalSTT(model_size="base", device="cuda")
    tts = LocalTTS(alsa_hw=alsa_hw)

    vad = webrtcvad.Vad(3)
    
    # Import des fonctions de capture partagées (pour rester cohérent avec chatbot_local.py)
    from chatbot_local import measure_noise_vad_ratio, record_until_silence, frames_to_wav

    print("\n⏳ Calibration acoustique (SILENCE pendant 2s)...")
    noise_ratio = measure_noise_vad_ratio(device_name, vad, duration=2.0)
    print(f"✅ Bruit calibré à {noise_ratio*100:.0f}%.")

    print("\n🎤 Je vous écoute... Parlez maintenant !")

    try:
        while True:
            raw_frames = record_until_silence(device_name, vad, noise_ratio)
            if raw_frames:
                wav_path = frames_to_wav(raw_frames)
                text = stt.transcribe(wav_path)
                os.remove(wav_path)

                if text and len(text.strip()) > 2:
                    print(f"👤 RECONNU : \"{text}\"")
                    response = f"Vous avez dit : {text}"
                    print(f"🤖 TTS : \"{response}\"")
                    tts.speak(response)
                
                print("\n👀 À l'écoute...")

    except KeyboardInterrupt:
        print("\n🛑 Test arrêté.")

if __name__ == "__main__":
    main()
