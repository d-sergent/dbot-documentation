import subprocess
import os
import time
import sys

class AudioIOError(Exception):
    """Exception personnalisée pour les erreurs de gestion audio (entrée/sortie)."""
    pass

class AudioIO:
    """
    Module de gestion des entrées/sorties audio via le ReSpeaker (XVF-3800).
    Configure les registres ALSA et gère les flux de capture et lecture.
    """
    def __init__(self, pulse_sink=None):
        self.card_id = self._detect_respeaker_card()
        self.pulse_sink = pulse_sink
        
        if self.card_id is None:
            print("⚠ [AudioIO] ReSpeaker XVF3800 non détecté via arecord -l. Tentative sur carte 0 par défaut.")
            self.card_id = "0"

        self.alsa_device = f"plughw:{self.card_id},0"
        self._initialize_hardware()

    def _detect_respeaker_card(self):
        """Détecte dynamiquement le numéro de carte du ReSpeaker."""
        try:
            out = subprocess.check_output(["arecord", "-l"], text=True)
            for line in out.splitlines():
                if "reSpeaker" in line or "XVF3800" in line:
                    # Extrait le X de 'carte X :'
                    return line.split("carte ")[1].split(":")[0].strip()
        except Exception:
            return None
        return None

    def _initialize_hardware(self):
        """Active l'amplificateur JST et règle les volumes ALSA."""
        try:
            # Activation de l'ampli (numid 3 et 4) et volume (5 et 6)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=3", "on"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=4", "on"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=5", "70"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=6", "70"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ [AudioIO] Hardware ReSpeaker (Carte {self.card_id}) initialisé.")
        except Exception as e:
            print(f"⚠ [AudioIO] Erreur initialisation hardware : {e}")

    def record_audio(self, duration: float, output_file: str) -> bool:
        """
        Enregistre l'audio en stéréo (pour éviter le bug driver) et convertit en mono pour le STT.
        """
        try:
            # On force la durée en entier car arecord peut rejeter les décimales
            d = int(duration)
            # On enregistre en stéréo (-c 2) à 16kHz, puis sox convertit en mono pour le robot
            cmd = f"arecord -D {self.alsa_device} -f S16_LE -r 16000 -c 2 -d {d} | sox -t wav - -c 1 {output_file}"
            subprocess.run(cmd, shell=True, check=True)
            print(f"🎤 [AudioIO] Enregistrement terminé : {output_file}")
            return True
        except Exception as e:
            raise AudioIOError(f"[AudioIO] Échec de l'enregistrement : {e}")

    def play_audio(self, input_file: str) -> bool:
        """Lit un fichier audio via PulseAudio (paplay)."""
        if not os.path.exists(input_file):
            raise AudioIOError(f"[AudioIO] Fichier introuvable : {input_file}")
        try:
            cmd = ["paplay", input_file]
            if self.pulse_sink:
                cmd.extend(["--device", self.pulse_sink])
            subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
            print(f"🔊 [AudioIO] Lecture terminée : {input_file}")
            return True
        except Exception as e:
            raise AudioIOError(f"[AudioIO] Échec de la lecture : {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 audio_io.py <duree> <fichier_sortie>")
        sys.exit(1)
    
    io = AudioIO()
    io.record_audio(float(sys.argv[1]), sys.argv[2])
    io.play_audio(sys.argv[2])