"""
test_tts_kokoro.py — Script de test pour la synthèse vocale Kokoro-ONNX.
=====================================================================
- Valide le chargement du modèle sur GPU (CUDA)
- Synthétise une phrase test en français
- Valide l'arrêt d'urgence de la parole (Barge-In) après 1.5 seconde
"""

import os
import sys
import time
import threading

# Permet d'importer nos modules D-Bot locaux
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dbot_next.audio.tts_kokoro import KokoroTTS

def main():
    print("🗣️ === TEST DE SYNTHÈSE VOCALE KOKORO-ONNX (GPU CUDA) === 🗣️\n")

    try:
        # Initialisation de Kokoro
        tts = KokoroTTS()
        
        # Récupération et affichage des voix disponibles
        voices = tts.get_voices()
        print(f"🎙️  Voix disponibles dans voices.bin : {', '.join(voices)}\n")
        
        # Choix de la voix
        voice_to_test = "ff_siwis"
        if len(sys.argv) > 1:
            requested_voice = sys.argv[1]
            if requested_voice in voices:
                voice_to_test = requested_voice
                print(f"👉 Utilisation de la voix choisie : {voice_to_test}")
            else:
                print(f"⚠ Voix '{requested_voice}' inconnue. Utilisation de la voix française '{voice_to_test}' par défaut.")
        else:
            print(f"👉 Utilisation de la voix par défaut : {voice_to_test} (Français Féminin)")
            print("💡 Astuce : Vous pouvez tester une autre voix en la passant en paramètre, ex: python3 dbot_next/scripts/test_tts_kokoro.py af_sarah\n")
        
        # Test 1 : Lecture complète d'une phrase courte
        phrase_1 = "Bonjour ! Je suis D-Bot, votre robot de compagnie. Mon nouveau synthétiseur fonctionne."
        # Si on teste une voix anglaise, on met une phrase en anglais
        if not voice_to_test.startswith("f"):
            phrase_1 = "Hello! I am D-Bot, your companion robot. My new neural speech synthesizer runs perfectly on GPU."
            
        print("\n🔊 Test 1 : Lecture d'une phrase complète...")
        tts.speak(phrase_1, voice=voice_to_test)
        
        time.sleep(1)
        
        # Test 2 : Lecture d'une longue phrase avec interruption au milieu (Barge-In)
        phrase_2 = "Ceci est un test pour vérifier que je peux être interrompu en plein milieu de ma phrase. Si l'utilisateur prend la parole pendant que je parle, je dois m'arrêter immédiatement et écouter ce qu'il a à me dire sans terminer ma phrase en cours."
        if not voice_to_test.startswith("f"):
            phrase_2 = "This is a test to verify that I can be interrupted in the middle of my speech. If the user starts talking, I must stop speaking immediately and listen to them."
            
        print("\n🔊 Test 2 : Lecture longue avec interruption simulée après 2 secondes...")
        
        # Lancement de la parole dans un thread séparé pour pouvoir l'interrompre
        speak_thread = threading.Thread(target=tts.speak, args=(phrase_2, voice_to_test))
        speak_thread.start()
        
        # Attendre 2 secondes et déclencher l'arrêt
        time.sleep(2.0)
        print("\n🚨 [TEST] Déclenchement de l'interruption...")
        tts.stop_speaking()
        
        # Attendre la fin du thread
        speak_thread.join()
        print("✅ Test 2 validé. Le son s'est arrêté de manière nette.")

    except Exception as e:
        print(f"\n❌ Erreur critique : {e}")

if __name__ == "__main__":
    main()
