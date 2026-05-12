"""
chatbot_local_v2.py — Boucle Conversationnelle D-Bot (Version 2 — SDK USB)
===========================================================================
Version corrigée et améliorée de chatbot_local.py utilisant :
  - audio_io_v2.py  : VAD matériel on-chip (SDK USB officiel XMOS)
  - respeaker_sdk.py : DOA temps réel pour orientation future du cou
  - stt.py          : Faster-Whisper (GPU, inchangé)
  - tts.py          : Piper (inchangé)

DIFFÉRENCES vs chatbot_local.py (v1) :
  ✅ VAD matériel → Plus besoin de parecord ni de webrtcvad
  ✅ DOA logué à chaque interaction (prêt pour le cou Pan/Tilt)
  ✅ Compatible avec tts.py v1 (suppression du paramètre alsa_hw obsolète)
  ✅ Mode VAD corrigé (mode 1, conforme à la Doc 45)
  ✅ Filtrage hallucinations Whisper conservé
  ✅ Gestion mémoire conversationnelle conservée

FICHIER DE RÉFÉRENCE (ne pas modifier) :
  code/scripts/behaviors/chatbot_local.py  (v1 — logique VAD hybride de référence)
"""

import os
import sys
import time

# Permet d'importer nos modules D-Bot locaux même si lancé depuis n'importe où
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dbot.audio.audio_io_v2 import AudioIOv2, AudioIOv2Error
from dbot.audio.stt import LocalSTT
from dbot.audio.tts import LocalTTS
from dbot.brain.llm_client import DbotBrain


# Mots/phrases générés par Whisper quand il n'entend rien (hallucinations connues)
WHISPER_HALLUCINATIONS = [
    "amara.org", "sous-titre", "merci de votre attention",
    "merci.", "sous titres", "communauté d'amara",
    "transcription", "généré automatiquement"
]


def is_hallucination(text: str) -> bool:
    """Détecte les hallucinations classiques de Whisper (silence transcrit en faux-texte)."""
    if not text or len(text.strip()) < 3:
        return True
    return any(h in text.lower() for h in WHISPER_HALLUCINATIONS)


def on_doa_update(angle: int):
    """
    Callback appelé par audio_io_v2 dès que la voix est détectée.
    Reçoit l'angle DOA (0-359°) de la source sonore.

    TODO : Envoyer cet angle au contrôleur du cou Pan/Tilt via ROS2 ou CAN.
    """
    print(f"🧭 [DOA] Source sonore détectée à {angle}° — Orientation cou à implémenter.")


def main():
    print("🤖 === D-Bot : Chatbot Local v2 (VAD Matériel + DOA) === 🤖\n")

    # --- INITIALISATION AUDIO (v2 avec SDK USB) ---
    try:
        audio = AudioIOv2(doa_callback=on_doa_update)
    except AudioIOv2Error as e:
        print(f"❌ Erreur AudioIO v2 : {e}")
        sys.exit(1)

    # --- INITIALISATION IA ---
    # Configuration via variables d'environnement
    _default_voice = os.path.expanduser("~/.local/share/piper-voices/fr_FR-siwis-medium.onnx")
    voice_model = os.environ.get("PIPER_VOICE", _default_voice)
    llm_model   = os.environ.get("DBOT_LLM_MODEL", "qwen2.5:0.5b")
    stt_device  = os.environ.get("DBOT_STT_DEVICE", "cuda") # On repasse en CUDA
    stt_model   = os.environ.get("DBOT_STT_MODEL", "small")  # 'small' est maintenant possible grâce au gain de RAM OpenRouter

    try:
        print(f"⏳ [STT] Chargement du réseau neuronal auditif '{stt_model}' sur {stt_device.upper()}...")
        stt   = LocalSTT(model_size=stt_model, device=stt_device)
        tts   = LocalTTS(voice_model_path=voice_model)
        brain = DbotBrain(model_name=llm_model)
        
        print(f"✅ [STT] Oreilles prêtes ({stt_device.upper()})")
        print(f"🔊 [TTS] Initialisé avec la voix : {os.path.basename(voice_model)}")
        if os.environ.get("OPENROUTER_API_KEY"):
            print(f"🧠 [Cerveau] Mode Hybride activé (Cloud: OpenRouter, Secours: {llm_model})")
        else:
            print(f"🧠 [Cerveau] Mode 100% Local activé (Modèle: {llm_model})")
        print(f"   (Variables : OPENROUTER_API_KEY, DBOT_LLM_MODEL, DBOT_STT_DEVICE, DBOT_STT_MODEL)")
    except Exception as e:
        print(f"\n❌ Erreur initialisation IA : {e}")
        sys.exit(1)

    tts.speak("Mes réseaux neuronaux sont chargés. Je suis totalement autonome.")
    time.sleep(0.5)

    # --- BOUCLE CONVERSATIONNELLE ---
    print("\n👀 Je vous écoute (VAD matériel actif)... (Ctrl+C pour quitter)\n")

    try:
        while True:
            # Le VAD matériel du chip XMOS déclenche l'enregistrement
            wav_path = "/tmp/dbot_input_v2.wav"
            success = audio.record_on_speech(
                output_file=wav_path,
                silence_timeout=1.5,
                max_duration=10.0
            )

            if not success:
                continue

            try:
                # Transcription Whisper GPU
                user_text = stt.transcribe(wav_path)
                os.remove(wav_path)

                if is_hallucination(user_text):
                    print("   (Silence ou hallucination ignoré)")
                    continue

                print(f"👤 Vous : '{user_text}'")

                # Génération de la réponse via LLM
                ai_response = brain.generate_response(user_text)
                brain.trim_memory(max_messages=10)

                # Synthèse et lecture de la réponse
                tts.speak(ai_response)
                print("\n👀 À l'écoute...\n")

            except Exception:
                import traceback
                traceback.print_exc()
                print("   → Reprise...\n")

    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt manuel.")
        audio.close()


if __name__ == "__main__":
    main()
