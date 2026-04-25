import subprocess
import os

class LocalTTS:
    """
    Système de synthèse vocale 100% hors-ligne utilisant Piper.
    Piper est ultra rapide et léger sur les processeurs ARM.
    """
    def __init__(self, voice_model_path=None, alsa_hw="plughw:2,0"):
        self.alsa_hw = alsa_hw
        
        # Par défaut, utilise la voix téléchargée par l'utilisateur
        if voice_model_path is None:
            self.voice_model_path = os.path.expanduser("~/.local/share/piper-voices/fr_FR-upmc-medium.onnx")
        else:
            self.voice_model_path = voice_model_path
            
        if not os.path.exists(self.voice_model_path):
            print(f"⚠ [TTS] AVERTISSEMENT : Le modèle vocal n'a pas été trouvé ici : {self.voice_model_path}")
            
        print(f"🔊 [TTS] Initialisé avec la voix : {os.path.basename(self.voice_model_path)}")

    def speak(self, text: str):
        """
        Transforme le texte en audio et le joue simultanément via ALSA.
        On utilise un "pipe" Unix pour lier la génération Piper directement à la lecture aplay.
        Cela donne une latence virtuellement nulle !
        """
        if not text:
            return
            
        print(f"🗣️ [D-Bot dit] : {text}")
        
        try:
            # La commande piper génère du RAW audio à 22050 Hz (format standard des modèles medium).
            piper_cmd = ["piper", "-m", self.voice_model_path, "--output_raw"]
            
            # On demande à aplay de lire ce flux brut tout de suite sur la sortie audio du ReSpeaker.
            aplay_cmd = ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-D", self.alsa_hw]
            
            # echo text | piper ... | aplay ...
            p1 = subprocess.Popen(["echo", text], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(piper_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            p3 = subprocess.Popen(aplay_cmd, stdin=p2.stdout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # On attend que la lecture soit complètement terminée avant de rendre la main au script principal
            p3.wait()
            
        except FileNotFoundError:
            print("❌ [TTS] Erreur : La commande 'piper' ou 'aplay' est introuvable. Avez-vous installé piper-tts ?")
        except Exception as e:
            print(f"❌ [TTS] Erreur inattendue : {e}")

if __name__ == "__main__":
    # Test unitaire autonome de la voix
    print("\n--- Test Voix Locale (Piper) ---")
    tts = LocalTTS()
    tts.speak("Bonjour, ma carte vocale locale fonctionne parfaitement à une fréquence de 22050 hertz.")
