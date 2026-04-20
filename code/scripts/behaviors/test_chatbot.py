#!/usr/bin/env python3
"""
scripts/behaviors/test_chatbot.py — Prototype de Chatbot Vocal (Option Mock Local)
==================================================================================
Une boucle complète d'Agent Conversationnel :
1. Écoute via le ReSpeaker (avec détection automatique de la voix - VAD).
2. Transcription via Google Speech-to-Text (gratuit, API publique).
3. "Cerveau" factice : analyse les mots-clés et génère une réponse texte.
4. Synthèse Vocale (TTS) via gTTS et lecture via le ReSpeaker.
"""

import sys
import pyaudio
import speech_recognition as sr
from gtts import gTTS
import subprocess
import re
import datetime
import os

def get_respeaker_info():
    """Détecte l'index PyAudio et l'adresse ALSA du ReSpeaker."""
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    
    device_index = None
    alsa_hw = "hw:2,0"  # fallback par défaut
    
    for i in range(info.get('deviceCount')):
        dev = p.get_device_info_by_host_api_device_index(0, i)
        name = dev.get('name')
        if dev.get('maxInputChannels') > 0 and ("ReSpeaker" in name or "XVF3800" in name):
            device_index = i
            # Essayer d'extraire l'adresse hw:X,X (ex: hw:2,0)
            match = re.search(r'hw:\d+,\d+', name)
            if match:
                alsa_hw = match.group(0)
            break
            
    p.terminate()
    return device_index, alsa_hw

def mock_brain(text):
    """Cerveau local factice pour simuler un LLM."""
    text_lower = text.lower()
    
    if "bonjour" in text_lower or "salut" in text_lower:
        return "Bonjour ! Je suis prêt, l'intégration de mon système vocal est un succès."
    elif "heure" in text_lower:
        now = datetime.datetime.now()
        heure = f"{now.hour} heure" if now.hour == 1 else f"{now.hour} heures"
        minute = f"{now.minute}" if now.minute > 0 else "pile"
        return f"Il est actuellement {heure} {minute}."
    elif "nom" in text_lower or "t'appelles" in text_lower:
        return "Je m'appelle D-Bot. Je suis un prototype de robot quadrupède explorateur."
    elif "comment" in text_lower and "ça va" in text_lower:
        return "Mes capteurs indiquent que tout fonctionne parfaitement. Je vais très bien, merci !"
    else:
        # Réponse perroquet pour valider la transcription sur tout ou n'importe quoi
        return f"Je n'ai pas de véritable cerveau intelligent pour le moment, mais j'ai très bien entendu que vous avez dit : {text}."

def speak(text, alsa_hw):
    """Transforme le texte en voix et le lit via le haut-parleur."""
    print(f"\n🤖 D-Bot : \"{text}\"\n")
    
    # Génération du fichier MP3
    tts = gTTS(text=text, lang='fr')
    output_file = "/tmp/dbot_response.mp3"
    tts.save(output_file)
    
    # Lecture du fichier via mpg123 en forçant la sortie ALSA du ReSpeaker
    subprocess.run(["mpg123", "-a", alsa_hw, output_file], 
                   stdout=subprocess.DEVNULL, 
                   stderr=subprocess.DEVNULL)
                   
    # Nettoyage
    if os.path.exists(output_file):
        os.remove(output_file)

def main():
    print("=" * 60)
    print("  D-Bot — Assistant Vocal (Cerveau Factice)")
    print("=" * 60)
    print("Initialisation des sens...")

    idx, alsa_hw = get_respeaker_info()
    
    if idx is None:
        print("❌ ReSpeaker non détecté. Vérifiez vos ports USB.")
        sys.exit(1)
        
    print(f"✅ ReSpeaker détecté (Index PyAudio: {idx}, Sortie ALSA: {alsa_hw})")
    
    # Fonction interne pour enregistrer 5 secondes via PyAudio (méthode robuste)
    def record_5_seconds(output_filename="/tmp/dbot_capture.wav"):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2  # Le ReSpeaker envoie 2 canaux traités
        RATE = 16000
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                        input=True, input_device_index=idx, frames_per_buffer=CHUNK)
        
        print("\n🔴 ENREGISTREMENT (5 secondes) - Parlez maintenant !")
        frames = []
        for i in range(0, int(RATE / CHUNK * 5)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        import wave
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return output_filename

    recognizer = sr.Recognizer()

    try:
        # Phrase de démarrage
        speak("Activation système. Appuyez sur Entrée pour me parler.", alsa_hw)
        
        while True:
            input("\n👉 Appuyez sur [ENTRÉE] puis parlez (Ctrl+C pour quitter)...")
            
            # Enregistre 5 secondes de manière fiable
            wav_file = record_5_seconds()
            
            print("💭 Traitement audio en cours...")
            try:
                # Lecture du fichier WAV fraichement enregistré
                with sr.AudioFile(wav_file) as source:
                    audio = recognizer.record(source)
                
                # Appel à Google Speech Recognition
                user_text = recognizer.recognize_google(audio, language="fr-FR")
                print(f"👤 Vous : \"{user_text}\"")
                
                # Analyse du texte par le faux cerveau
                response = mock_brain(user_text)
                
                # Génération et lecture de la réponse vocale
                speak(response, alsa_hw)
                
            except sr.UnknownValueError:
                print("💭 (Je n'ai pas très bien entendu)")
            except sr.RequestError as e:
                print(f"⚠ Erreur réseau (API Google STT inaccessible) : {e}")

    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt de l'assistant.")
        speak("Extinction de l'assistant.", alsa_hw)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur inattendue : {e}")

if __name__ == "__main__":
    main()
