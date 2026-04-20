import os
import sys
import tempfile
import speech_recognition as sr

# Permet d'importer nos modules D-Bot locaux même si le script est lancé de n'importe où
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from code.dbot.audio.stt import LocalSTT
from code.dbot.audio.tts import LocalTTS
from code.dbot.brain.llm_client import DbotBrain

def get_respeaker_hw_info():
    """Tente de détecter automatiquement le ReSpeaker via PyAudio"""
    import pyaudio
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if "reSpeaker" in info.get('name', ''):
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
    # Il ne fait que découper le son quand on arrête de parler.
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    
    # On fait parler le robot pour signaler qu'il a fini de "booter"
    tts.speak("Mes réseaux neuronaux sont chargés. Je suis totalement autonome.")
    
    # --- BOUCLE CONVERSATIONNELLE HORS-LIGNE ---
    try:
        with sr.Microphone(device_index=idx, sample_rate=16000) as source:
            print("\n⏳ Calibration de l'acoustique ambiante (1 seconde)...")
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            
            print("\n👀 Je vous écoute... (Appuyez sur Ctrl+C pour m'éteindre)")
            while True:
                try:
                    # 1. ÉCOUTE DE L'UTILISATEUR (Attend ici automatiquement)
                    audio_data = recognizer.listen(source, timeout=None, phrase_time_limit=15)
                    
                    # 2. Sauvegarde de la phrase dans la RAM (WAV temporaire)
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        wav_path = f.name
                        f.write(audio_data.get_wav_data())
                        
                    # 3. RÉFLEXION (STT) : Transforme l'onde sonore en texte via le GPU
                    user_text = stt.transcribe(wav_path)
                    os.remove(wav_path) # Nettoyage de la RAM
                    
                    # Si c'était juste un souffle ou un claquement de porte, on ignore
                    if not user_text or len(user_text) < 2:
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
