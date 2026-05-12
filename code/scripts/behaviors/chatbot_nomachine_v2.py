"""
chatbot_nomachine_v2.py — Version DÉVELOPPEMENT (NoMachine).
===========================================================================
- Utilise audio_io_nomachine.py (PulseAudio / NX)
- Auto-healing du serveur audio si NoMachine plante
- Permet le retour audio distant vers votre Mac/PC
"""

import os
import sys
import time

# Permet d'importer nos modules D-Bot locaux
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dbot.audio.audio_io_nomachine import AudioIONoMachine
from dbot.audio.stt import LocalSTT
from dbot.audio.tts import LocalTTS
from dbot.brain.llm_client import DbotBrain

WHISPER_HALLUCINATIONS = [
    "amara.org", "sous-titre", "merci de votre attention",
    "merci.", "sous titres", "communauté d'amara",
    "transcription", "généré automatiquement"
]

def is_hallucination(text: str) -> bool:
    if not text or len(text.strip()) < 3: return True
    return any(h in text.lower() for h in WHISPER_HALLUCINATIONS)

def main():
    print("🤖 === D-Bot : Chatbot DÉVELOPPEMENT (NoMachine — PulseAudio) === 🤖\n")

    # --- INITIALISATION AUDIO (NoMachine / PulseAudio) ---
    try:
        audio = AudioIONoMachine()
    except Exception as e:
        print(f"❌ Erreur critique Audio NoMachine : {e}")
        sys.exit(1)

    # --- INITIALISATION IA ---
    _default_voice = os.path.expanduser("~/.local/share/piper-voices/fr_FR-siwis-medium.onnx")
    voice_model = os.environ.get("PIPER_VOICE", _default_voice)
    llm_model   = os.environ.get("DBOT_LLM_MODEL", "qwen2.5:0.5b")
    stt_device  = os.environ.get("DBOT_STT_DEVICE", "cuda")
    stt_model   = os.environ.get("DBOT_STT_MODEL", "small")

    try:
        print(f"⏳ [STT] Chargement '{stt_model}' sur {stt_device.upper()}...")
        stt   = LocalSTT(model_size=stt_model, device=stt_device)
        tts   = LocalTTS(voice_model_path=voice_model)
        brain = DbotBrain(model_name=llm_model)
        
        print(f"✅ [Système] D-Bot prêt en mode NoMachine.")
    except Exception as e:
        print(f"\n❌ Erreur initialisation IA : {e}")
        sys.exit(1)

    tts.speak("Mode développement activé. Je communique via NoMachine.")

    print("\n👀 À l'écoute (VAD matériel)... (Ctrl+C pour quitter)\n")

    try:
        while True:
            wav_path = "/tmp/dbot_input_nomachine.wav"
            if audio.record_on_speech(wav_path):
                user_text = stt.transcribe(wav_path)
                if os.path.exists(wav_path): os.remove(wav_path)

                if is_hallucination(user_text):
                    continue

                print(f"👤 Vous : '{user_text}'")
                ai_response = brain.generate_response(user_text)
                print(f"🤖 D-Bot : {ai_response}")
                tts.speak(ai_response)
                print("\n👀 À l'écoute...\n")

    except KeyboardInterrupt:
        print("\n🛑 Arrêt manuel.")
        audio.close()

if __name__ == "__main__":
    main()
