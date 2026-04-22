import os
import sys
import tempfile
import speech_recognition as sr
import time

# Permet d'importer nos modules D-Bot locaux même si le script est lancé de n'importe où
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dbot.audio.stt import LocalSTT
from dbot.audio.tts import LocalTTS
from dbot.brain.llm_client import DbotBrain

def get_respeaker_hw_info():
    """Tente de détecter automatiquement le ReSpeaker via PyAudio"""
    import pyaudio
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        # On doit ABSOLUMENT vérifier qu'il s'agit d'un canal de captation (maxInputChannels > 0)
        # et pas du canal haut-parleur.
        if info.get('maxInputChannels') > 0 and ("reSpeaker" in info.get('name', '') or "XVF3800" in info.get('name', '')):
            # Info nom ressemble souvent à "reSpeaker XVF3800 4-Mic Array: USB Audio (hw:2,0)"
            card_num = 2 # valeur par défaut raisonnable si on n'arrive pas à parser
            for part in info['name'].split(','):
                if 'hw:' in part:
                    try:
                        card_num = ''.join(filter(str.isdigit, part.split('hw:')[1]))
                    except:
                        pass
            return i, f"plughw:{card_num},0"
    return None, None

def main():
    print("🤖 === D-Bot : Démarrage du Cerveau 100% Hors-Ligne === 🤖\n")
    
    idx, alsa_hw = get_respeaker_hw_info()
    if idx is None:
        print("❌ ReSpeaker introuvable. Branchez-le sur un port USB-A et relancez le programme.")
        sys.exit(1)
        
    print(f"🔌 Matériel Audio détecté : PyAudio={idx}, ALSA={alsa_hw}")
        
    # --- PHASE D'INITIALISATION DE L'IA ---
    # Cette étape demande beaucoup de calculs pour charger les modèles en VRAM
    try:
        tts = LocalTTS(alsa_hw=alsa_hw)
        brain = DbotBrain(model_name="qwen2.5:3b")
        stt = LocalSTT(model_size="small", device="cuda")
    except Exception as e:
        print(f"\n❌ Erreur sérieuse lors de l'activation des réseaux neuronaux : {e}")
        sys.exit(1)
    
    # Moteur "bête" pour la Détection d'Activité Vocale (VAD)
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = False
    recognizer.pause_threshold = 0.8

    # On fait parler le robot pour signaler qu'il a fini de "booter"
    tts.speak("Mes réseaux neuronaux sont chargés. Je suis totalement autonome.")
    time.sleep(0.8)

    # --- CALIBRATION INTELLIGENTE EN 2 PHASES ---
    # Phase 1 : Mesure du bruit de fond (ventilateur Jetson, etc.)
    # Phase 2 : Mesure de la voix pour trouver un seuil qui passe entre les deux
    try:
        with sr.Microphone(device_index=idx, sample_rate=16000) as source:
            print("\n⏳ Phase 1/2 : Mesure du bruit ambiant (Ne parlez pas pendant 2s)...")
            recognizer.adjust_for_ambient_noise(source, duration=2.0)
            noise_level = recognizer.energy_threshold
            print(f"   → Bruit de fond mesuré : {noise_level:.0f}")

            tts.speak("Maintenant parlez pendant 3 secondes.")
            time.sleep(0.3)
            print("⏳ Phase 2/2 : Parlez maintenant pendant 3 secondes...")

            # On écoute la voix brute pendant 3 secondes pour mesurer son énergie
            import audioop, struct
            p_test = sr.Recognizer()
            p_test.dynamic_energy_threshold = True
            p_test.adjust_for_ambient_noise(source, duration=3.0)
            voice_level = p_test.energy_threshold
            print(f"   → Niveau de voix mesuré : {voice_level:.0f}")

            # Le seuil optimal est à mi-chemin entre bruit et voix
            optimal = (noise_level + voice_level) / 2
            # Sécurité minimale : on ne peut pas descendre sous le bruit de fond + 10%
            optimal = max(optimal, noise_level * 1.1)
            recognizer.energy_threshold = optimal
            print(f"✅ Seuil VAD optimal calculé : {optimal:.0f} (Bruit={noise_level:.0f} / Voix={voice_level:.0f})")
            tts.speak(f"Calibration terminée. Je vous écoute.")
            time.sleep(0.3)

    except Exception as e:
        # Fallback si la calibration échoue : valeur statique conservative
        recognizer.energy_threshold = 1800
        print(f"⚠ Calibration impossible ({e}), seuil statique à 1800")

    # --- BOUCLE CONVERSATIONNELLE HORS-LIGNE ---
    try:
        with sr.Microphone(device_index=idx, sample_rate=16000) as source:
            print(f"\n👀 Je vous écoute... (Seuil={recognizer.energy_threshold:.0f}) (Ctrl+C pour m'éteindre)")
            while True:
                try:
                    # 1. ÉCOUTE DE L'UTILISATEUR (Attend ici automatiquement)
                    audio_data = recognizer.listen(source, phrase_time_limit=15)
                    print("💭 [VAD] Parole captée, transmission au STT...")
                    
                    # 2. Sauvegarde de la phrase dans la RAM (WAV temporaire)
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        wav_path = f.name
                        f.write(audio_data.get_wav_data())
                        
                    # 3. RÉFLEXION (STT) : Transforme l'onde sonore en texte via le GPU
                    user_text = stt.transcribe(wav_path)
                    os.remove(wav_path) # Nettoyage de la RAM
                    
                    # Filtre anti-hallucination du modèle Whisper sur les silences profonds
                    hallus = ["amara.org", "sous-titre", "merci de votre attention", "merci."]
                    if not user_text or len(user_text) < 2 or any(h in user_text.lower() for h in hallus):
                        continue
                        
                    print(f"👤 Vous avez dit : '{user_text}'")
                        
                    # 4. CERVEAU (LLM) : Génère la réplique du robot à partir du texte
                    ai_response = brain.generate_response(user_text)
                    
                    # On évite à la RAM de s'effondrer après des heures de discussion
                    brain.trim_memory(max_messages=10)
                    
                    # 5. PAROLE (TTS) : Envoie le texte du LLM dans le haut-parleur
                    tts.speak(ai_response)
                    
                    print("\n👀 À l'écoute...")
                    
                except sr.UnknownValueError:
                    pass
                except OSError:
                    # Rétouffe les alertes ALSA 'underflow' inoffensives de Linux
                    pass
                
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt manuel du système robotique.")

if __name__ == "__main__":
    main()
