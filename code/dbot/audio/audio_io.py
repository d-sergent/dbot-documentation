import subprocess
import os
import time

class AudioIOError(Exception):
    """Exception personnalisée pour les erreurs de gestion audio (entrée/sortie)."""
    pass

class AudioIO:
    """
    Module de gestion des entrées/sorties audio via le ReSpeaker (XVF-3800).
    Configure les registres ALSA et utilise PulseAudio pour les flux audio.

    Args:
        alsa_device (str, optional): Device ALSA à utiliser (ex. : 'plughw:2,0').
        pulse_sink (str, optional): Sink PulseAudio à utiliser.
    """
    def __init__(self, alsa_device="plughw:2,0", pulse_sink=None):
        self.alsa_device = alsa_device
        self.pulse_sink = pulse_sink

        # Activation manuelle de l'amplificateur JST du ReSpeaker (voir doc 45_Configuration...)
        try:
            subprocess.run(["amixer", "-c", "0", "cset", "numid=3", "on"],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", "0", "cset", "numid=4", "on"],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", "0", "cset", "numid=5", "60"],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", "0", "cset", "numid=6", "60"],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ [AudioIO] Amplificateur JST activé pour le ReSpeaker.")
        except Exception as e:
            raise AudioIOError(f"[AudioIO] Échec de l'activation de l'amplificateur JST : {e}")

        # Vérification de la configuration PulseAudio
        if self.pulse_sink:
            try:
                subprocess.run(["pactl", "set-sink-mute", self.pulse_sink, "false"], stderr=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-sink-volume", self.pulse_sink, "100%"], stderr=subprocess.DEVNULL)
                print(f"✅ [AudioIO] Sink PulseAudio '{self.pulse_sink}' configuré.")
            except Exception as e:
                raise AudioIOError(f"[AudioIO] Échec de la configuration du sink PulseAudio : {e}")

    def record_audio(self, duration: float, output_file: str) -> bool:
        """
        Enregistre l'audio via le micro du ReSpeaker.

        Args:
            duration (float): Durée de l'enregistrement en secondes.
            output_file (str): Chemin vers le fichier de sortie (WAV).

        Returns:
            bool: True si l'enregistrement a réussi, False sinon.
        """
        try:
            # Commande pour enregistrer l'audio (via ALSA + sox ou parec)
            cmd = f"parec -d {self.alsa_device} --format=S16_LE --rate=16000 --channels=1 | sox -t wav - {output_file}"
            subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)
            print(f"🎤 [AudioIO] Audio enregistré dans : {output_file}")
            return True
        except Exception as e:
            raise AudioIOError(f"[AudioIO] Échec de l'enregistrement audio : {e}")

    def play_audio(self, input_file: str) -> bool:
        """
        Lit un fichier audio via le haut-parleur du ReSpeaker.

        Args:
            input_file (str): Chemin vers le fichier audio (WAV).

        Returns:
            bool: True si la lecture a réussi, False sinon.
        """
        if not os.path.exists(input_file):
            raise AudioIOError(f"[AudioIO] Fichier audio introuvable : {input_file}")

        try:
            # Lecture via paplay (PulseAudio)
            cmd = ["paplay", input_file]
            if self.pulse_sink:
                cmd.extend(["--device", self.pulse_sink])
            subprocess.run(cmd, stderr=subprocess.DEVNULL)
            print(f"🔊 [AudioIO] Lecture de : {input_file}")
            return True
        except Exception as e:
            raise AudioIOError(f"[AudioIO] Échec de la lecture audio : {e}")

    def capture_and_play(self, duration: float, input_file: str, output_file: str) -> bool:
        """
        Capture l'audio et le joue immédiatement (ex. : pour un test en temps réel).

        Args:
            duration (float): Durée de l'enregistrement en secondes.
            input_file (str): Chemin vers le fichier d'entrée (pour la lecture).
            output_file (str): Chemin vers le fichier de sortie (pour l'enregistrement).

        Returns:
            bool: True si l'opération a réussi, False sinon.
        """
        try:
            self.record_audio(duration, output_file)
            self.play_audio(input_file)
            return True
        except AudioIOError as e:
            raise AudioIOError(f"[AudioIO] Échec de la capture et lecture : {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("❌ [AudioIO] Usage: python audio_io.py <duration> <output_file>")
        sys.exit(1)

    try:
        audio_io = AudioIO()
        audio_io.record_audio(float(sys.argv[1]), sys.argv[2])
        print("✅ [AudioIO] Test réussi.")
    except AudioIOError as e:
        print(f"❌ [AudioIO] Erreur : {e}")