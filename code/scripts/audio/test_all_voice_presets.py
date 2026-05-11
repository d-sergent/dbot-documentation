"""
test_all_voice_presets.py — Comparaison auditive des presets D-Bot
==================================================================
1. Génère une phrase via Piper TTS
2. Applique les 7 presets DSP du moteur modify_voice.py
3. Sauvegarde tout dans le dossier ./dbot_fx/
"""

import os
import sys
import subprocess

# Importation du moteur FX
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from dbot.audio.tts import LocalTTS

def main():
    print("🎙️  D-Bot : Test comparatif des presets vocaux\n")
    
    # 1. Génération de la phrase de référence
    sentence = "Bonjour, je suis le robot D-Bot. Voici un test de mon identité vocale avec différents presets."
    ref_path = "/tmp/reference_voice.wav"
    
    # On récupère la voix via l'env pour pouvoir tester du masculin facilement
    voice_env = os.environ.get("PIPER_VOICE", "fr_FR-upmc-medium.onnx")
    print(f"⏳ Génération de la voix Piper ({os.path.basename(voice_env)})...")
    
    try:
        tts = LocalTTS()
        tts.generate_wav(sentence, ref_path)
        print("✅ Référence générée.\n")
    except Exception as e:
        print(f"❌ Erreur Piper : {e}")
        return

    # 2. Application des presets via modify_voice.py
    print(f"⏳ Application des 7 presets DSP...")
    try:
        # On appelle le script modify_voice.py en tant que module ou process
        # Ici on le lance via subprocess pour valider le fonctionnement en ligne de commande
        cmd = [sys.executable, "code/dbot/audio/modify_voice.py", ref_path]
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"❌ Erreur DSP : {e}")
        return

    print("\n🎉 Terminé ! Les fichiers sont dans le dossier ./dbot_fx/")
    print("\nPour les écouter sur la Jetson, lance cette commande :\n")
    print("for f in dbot_fx/*.wav; do echo \"Lecture de $f...\"; paplay $f; sleep 1; done")

if __name__ == "__main__":
    main()
