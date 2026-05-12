"""
audio_io_autonomous.py — Version Spécifique pour le mode PRODUCTION (Headless).
Utilise exclusivement ALSA Direct (arecord/aplay) pour une stabilité maximale sans PulseAudio.
Conforme à la Doc 45 §6.B.
"""

import subprocess
import os
import sys
import time
import threading
from typing import Optional, Callable

from dbot.audio.respeaker_sdk import ReSpeakerSDK, ReSpeakerSDKError

class AudioIOAutonomousError(Exception):
    """Exception pour les erreurs du module AudioIO Autonomous."""
    pass

class AudioIOAutonomous:
    """
    Module AudioIO Spécifique Mode Autonome — ALSA Direct + VAD matériel.
    """

    def __init__(self, doa_callback: Optional[Callable[[int], None]] = None):
        self.doa_callback = doa_callback
        self._vad_thread: Optional[threading.Thread] = None
        self._stop_vad = threading.Event()

        # Détection de la carte ALSA
        self.card_id = self._detect_respeaker_card()
        self.alsa_device = f"plughw:{self.card_id},0"

        # Activation de l'ampli JST
        self._initialize_hardware()

        # Connexion au SDK USB
        try:
            self.sdk = ReSpeakerSDK()
            self.sdk_available = True
            version = self.sdk.get_version()
            print(f"✅ [AudioIO Autonome] SDK USB actif — Firmware {version}")
        except ReSpeakerSDKError as e:
            self.sdk_available = False
            print(f"⚠ [AudioIO Autonome] SDK USB indisponible ({e}).")

    def _detect_respeaker_card(self) -> str:
        """Détecte dynamiquement le numéro de carte ALSA du ReSpeaker."""
        try:
            out = subprocess.check_output(["arecord", "-l"], text=True)
            for line in out.splitlines():
                if "reSpeaker" in line or "XVF3800" in line:
                    return line.split("carte ")[1].split(":")[0].strip()
        except Exception:
            pass
        return "0"

    def _initialize_hardware(self):
        """Active l'amplificateur JST (Doc 45 §4)."""
        try:
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=3", "on"], stdout=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=4", "on"], stdout=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=5", "70"], stdout=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=6", "70"], stdout=subprocess.DEVNULL)
            print(f"✅ [AudioIO Autonome] Ampli JST activé (Carte {self.card_id})")
        except Exception as e:
            print(f"⚠ [AudioIO Autonome] Erreur init ampli : {e}")

    def record_audio(self, duration: float, output_file: str) -> bool:
        """Enregistre l'audio via ALSA direct (arecord) — Stéréo 2ch obligatoire."""
        try:
            d = int(duration)
            # Capture en 2ch (pour éviter le bug driver) et conversion mono via sox
            cmd = (f"arecord -D {self.alsa_device} -f S16_LE -r 16000 -c 2 -d {d} | "
                   f"sox -t wav - -c 1 {output_file}")
            subprocess.run(cmd, shell=True, check=True, stderr=subprocess.DEVNULL)
            print(f"🎤 [AudioIO Autonome] Enregistrement : {output_file} (via ALSA Direct)")
            return os.path.exists(output_file) and os.path.getsize(output_file) > 1000
        except Exception as e:
            print(f"❌ [AudioIO Autonome] Échec enregistrement : {e}")
            return False

    def record_on_speech(self, output_file: str) -> bool:
        """Attend la détection de parole par le VAD matériel."""
        if not self.sdk_available:
            return self.record_audio(5, output_file)

        print("👂 [AudioIO Autonome] Attente de la parole (VAD matériel)...")
        while True:
            doa, is_speech = self.sdk.get_doa_and_vad()
            if is_speech:
                if self.doa_callback:
                    self.doa_callback(doa)
                break
            time.sleep(0.05)

        print("🗣️  [AudioIO Autonome] Enregistrement en cours...")
        return self.record_audio(5, output_file)

    def play_audio(self, input_file: str) -> bool:
        """Lit un fichier audio via ALSA Direct (aplay)."""
        if not os.path.exists(input_file):
            return False
        try:
            # On utilise plughw pour gérer les conversions de fréquence si besoin
            cmd = ["aplay", "-D", self.alsa_device, input_file]
            subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
            print(f"🔊 [AudioIO Autonome] Lecture : {input_file} (via ALSA Direct)")
            return True
        except Exception as e:
            print(f"❌ [AudioIO Autonome] Échec lecture : {e}")
            return False

    def close(self):
        if self.sdk_available and self.sdk:
            self.sdk.close()

    def __enter__(self): return self
    def __exit__(self, *args): self.close()

if __name__ == "__main__":
    with AudioIOAutonomous() as audio:
        audio.record_on_speech("/tmp/test_autonomous.wav")
        audio.play_audio("/tmp/test_autonomous.wav")
