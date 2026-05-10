import subprocess
import os
import time

class TTSError(Exception):
    """
    Exception levée en cas d'erreur dans le module TTS.
    """
    pass

class LocalTTS:
    """
    Système de synthèse vocale 100% hors-ligne utilisant Piper.
    Piper est ultra rapide et léger sur les processeurs ARM de la Jetson.
    
    Args:
        voice_model_path (str, optional): Chemin vers le modèle vocal Piper (.onnx).
        pulse_sink (str, optional): Sink PulseAudio à utiliser.
    """
    def __init__(self, voice_model_path=None, pulse_sink=None):
        self.pulse_sink = pulse_sink
        self.card_id = self._detect_respeaker_card()

        # Chemin de la voix — priorité : argument > variable env > défaut
        # Voir Doc 48 pour le catalogue des voix disponibles
        if voice_model_path is None:
            voice_model_path = os.environ.get(
                "PIPER_VOICE",
                os.path.expanduser("~/.local/share/piper-voices/fr_FR-upmc-medium.onnx")
            )
        self.voice_model_path = voice_model_path

            
        if not os.path.exists(self.voice_model_path):
            raise TTSError(f"[TTS] Modèle vocal introuvable : {self.voice_model_path}")

        self._initialize_hardware()
        print(f"🔊 [TTS] Initialisé avec la voix : {os.path.basename(self.voice_model_path)} (Carte {self.card_id})")

    def _detect_respeaker_card(self):
        """Détecte dynamiquement le numéro de carte du ReSpeaker."""
        try:
            out = subprocess.check_output(["arecord", "-l"], text=True)
            for line in out.splitlines():
                if "reSpeaker" in line or "XVF3800" in line:
                    return line.split("carte ")[1].split(":")[0].strip()
        except Exception:
            return "0"
        return "0"

    def _initialize_hardware(self):
        """Active l'amplificateur JST du ReSpeaker via ALSA."""
        try:
            # Activation de l'ampli (numid 3 et 4) et volume (5 et 6)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=3", "on"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=4", "on"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=5", "70"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=6", "70"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"⚠ [TTS] Avertissement : Impossible d'initialiser l'ampli via amixer : {e}")

    def speak(self, text: str):
        """
        Génère un fichier audio à partir d'un texte et le joue via paplay (PulseAudio).
        """
        if not text:
            return
        
        import tempfile
        print(f"🗣️ [D-Bot dit] : {text}")
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                temp_wav = tf.name

            # Génération Piper
            gen_cmd = f'echo "{text}" | piper -m {self.voice_model_path} --output_file {temp_wav}'
            subprocess.run(gen_cmd, shell=True, check=True, stderr=subprocess.DEVNULL)
            
            # Lecture PulseAudio
            if os.path.exists(temp_wav) and os.path.getsize(temp_wav) > 0:
                play_cmd = ["paplay", temp_wav]
                if self.pulse_sink:
                    play_cmd.extend(["--device", self.pulse_sink])
                
                subprocess.run(play_cmd, check=True)
                os.remove(temp_wav)
            else:
                raise TTSError("[TTS] Le fichier audio généré est vide.")
                
        except Exception as e:
            raise TTSError(f"[TTS] Erreur lors de la synthèse vocale : {e}")

if __name__ == "__main__":
    tts = LocalTTS()
    tts.speak("Test du système vocal optimisé pour D-Bot.")
