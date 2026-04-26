import subprocess
import os

class LocalTTS:
    """
    Système de synthèse vocale 100% hors-ligne utilisant Piper.
    Piper est ultra rapide et léger sur les processeurs ARM.
    """
    def __init__(self, voice_model_path=None, alsa_hw="plughw:2,0", pulse_sink=None):
        self.alsa_hw = alsa_hw
        self.pulse_sink = pulse_sink
        
        # Par défaut, utilise la voix téléchargée par l'utilisateur
        if voice_model_path is None:
            self.voice_model_path = os.path.expanduser("~/.local/share/piper-voices/fr_FR-upmc-medium.onnx")
        else:
            self.voice_model_path = voice_model_path
            
        if not os.path.exists(self.voice_model_path):
            print(f"⚠ [TTS] AVERTISSEMENT : Le modèle vocal n'a pas été trouvé ici : {self.voice_model_path}")
            
        print(f"🔊 [TTS] Initialisé avec la voix : {os.path.basename(self.voice_model_path)}")

    def speak(self, text: str):
        if not text: return
        print(f"🗣️ [D-Bot dit] : {text}")
        
        try:
            # 1. On prépare l'environnement avec le Sink spécifique
            env = os.environ.copy()
            if self.pulse_sink:
                env["PULSE_SINK"] = self.pulse_sink
                subprocess.run(["pactl", "set-sink-mute", self.pulse_sink, "false"], stderr=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-sink-volume", self.pulse_sink, "100%"], stderr=subprocess.DEVNULL)

            # 2. On lance la commande
            cmd = f'echo "{text}" | piper -m {self.voice_model_path} --output_raw | aplay -r 22050 -f S16_LE -t raw'
            
            if self.alsa_hw:
                direct_cmd = cmd + f" -D {self.alsa_hw}"
                res = subprocess.run(direct_cmd, shell=True, stderr=subprocess.PIPE, env=env)
                if res.returncode != 0:
                    print("ℹ️ [TTS] ALSA occupé, passage par PulseAudio...")
                    subprocess.run(cmd, shell=True, env=env)
            else:
                subprocess.run(cmd, shell=True, env=env)
            
        except Exception as e:
            print(f"❌ [TTS] Erreur : {e}")

if __name__ == "__main__":
    # Test unitaire autonome de la voix
    print("\n--- Test Voix Locale (Piper) ---")
    tts = LocalTTS()
    tts.speak("Bonjour, ma carte vocale locale fonctionne parfaitement à une fréquence de 22050 hertz.")
