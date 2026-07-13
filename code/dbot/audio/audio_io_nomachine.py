"""
audio_io_nomachine.py — Version Spécifique pour le mode DÉVELOPPEMENT (NoMachine).
Utilise PulseAudio (parecord/paplay) pour passer à travers le réseau NoMachine.
Intègre une logique de réparation automatique du serveur de son.
"""

import subprocess
import os
import sys
import time
import threading
from typing import Optional, Callable

from dbot.audio.respeaker_sdk import ReSpeakerSDK, ReSpeakerSDKError

class AudioIONoMachineError(Exception):
    """Exception pour les erreurs du module AudioIO NoMachine."""
    pass

class AudioIONoMachine:
    """
    Module AudioIO Spécifique NoMachine — PulseAudio + VAD matériel.
    """

    def __init__(self, pulse_sink: Optional[str] = None,
                 doa_callback: Optional[Callable[[int], None]] = None):
        self.pulse_sink = pulse_sink
        self.doa_callback = doa_callback
        
        # 0. Réparation PulseAudio NoMachine
        self._ensure_pulseaudio()

        # Détection de la carte ALSA (pour amixer)
        self.card_id = self._detect_respeaker_card()
        
        # Activation de l'ampli JST
        self._initialize_hardware()

        # Connexion au SDK USB
        try:
            self.sdk = ReSpeakerSDK()
            self.sdk_available = True
            print(f"✅ [AudioIO NoMachine] SDK USB actif.")
        except ReSpeakerSDKError as e:
            self.sdk_available = False
            print(f"⚠ [AudioIO NoMachine] SDK USB indisponible ({e}).")

    def _ensure_pulseaudio(self):
        """Force la connexion au serveur audio physique de la Jetson au lieu du virtuel NoMachine."""
        # Si on est dans un terminal NoMachine, PULSE_SERVER force l'audio vers le réseau (nx_voice_out)
        pulse_server = os.environ.get("PULSE_SERVER", "")
        if "nx/devices" in pulse_server or "PULSE_SERVER" in os.environ:
            print("⚠ [AudioIO NoMachine] Redirection audio NX détectée. Destruction de la bulle pour récupérer le matériel...")
            del os.environ["PULSE_SERVER"]
        
        # Test de connexion au vrai serveur physique
        try:
            subprocess.check_output("pactl info", shell=True, stderr=subprocess.STDOUT)
            print("✅ [AudioIO NoMachine] Connecté au serveur de son physique de la Jetson.")
        except subprocess.CalledProcessError:
            print("⚠ [AudioIO NoMachine] Le vrai PulseAudio est injoignable. Lancement...")
            subprocess.run("pulseaudio --start", shell=True, stderr=subprocess.DEVNULL)
            time.sleep(2)

    def _detect_respeaker_card(self) -> str:
        try:
            out = subprocess.check_output(["arecord", "-l"], text=True)
            for line in out.splitlines():
                if "reSpeaker" in line or "XVF3800" in line:
                    if "carte" in line:
                        return line.split("carte ")[1].split(":")[0].strip()
                    elif "card" in line:
                        return line.split("card ")[1].split(":")[0].strip()
        except Exception: pass
        return "0"

    def _initialize_hardware(self):
        """Ampli JST + Réveil Source et Sink PulseAudio (Conforme Doc 45 §4)."""
        try:
            # 1. Amplificateur JST
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=3", "on"], stdout=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=4", "on"], stdout=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=5", "70"], stdout=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=6", "70"], stdout=subprocess.DEVNULL)
            print(f"✅ [AudioIO NoMachine] Ampli JST activé (Carte {self.card_id}).")
            
            subprocess.run(["pactl", "unload-module", "module-suspend-on-idle"], stdout=subprocess.DEVNULL)
            
            # 2. Réveil Source (Micro)
            sources = subprocess.check_output(["pactl", "list", "short", "sources"], text=True)
            self.pulse_source = None
            for line in sources.splitlines():
                if ("XVF3800" in line or "ReSpeaker" in line or "iec958" in line) and ".monitor" not in line:
                    self.pulse_source = line.split()[1]
                    break
            
            if self.pulse_source:
                subprocess.run(["pactl", "suspend-source", self.pulse_source, "0"], stdout=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-source-mute", self.pulse_source, "false"], stdout=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-source-volume", self.pulse_source, "150%"], stdout=subprocess.DEVNULL)
                print(f"✅ [AudioIO NoMachine] Micro réveillé : {self.pulse_source}")
            else:
                print("⚠ [AudioIO NoMachine] Micro ReSpeaker INTROUVABLE dans PulseAudio.")
                
            # 3. Réveil Sink (Haut-parleur)
            sinks = subprocess.check_output(["pactl", "list", "short", "sinks"], text=True)
            for line in sinks.splitlines():
                if "XVF3800" in line or "ReSpeaker" in line:
                    self.pulse_sink = line.split()[1]
                    break
            
            if self.pulse_sink:
                subprocess.run(["pactl", "suspend-sink", self.pulse_sink, "0"], stdout=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-sink-mute", self.pulse_sink, "false"], stdout=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-sink-volume", self.pulse_sink, "100%"], stdout=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-default-sink", self.pulse_sink], stdout=subprocess.DEVNULL)
                print(f"✅ [AudioIO NoMachine] Haut-parleur réveillé : {self.pulse_sink}")
            else:
                print("⚠ [AudioIO NoMachine] Haut-parleur ReSpeaker INTROUVABLE dans PulseAudio.")
                
        except Exception as e:
            print(f"⚠ [AudioIO NoMachine] Erreur init matérielle : {e}")

    def record_audio(self, duration: float, output_file: str) -> bool:
        """Enregistre via PulseAudio (parecord)."""
        try:
            d = int(duration)
            device_arg = f"--device={self.pulse_source}" if hasattr(self, 'pulse_source') and self.pulse_source else ""
            cmd = (f"timeout {d} parecord {device_arg} --channels=2 --format=s16le --rate=16000 --raw | "
                   f"sox -t raw -r 16000 -e signed -b 16 -c 2 - -c 1 {output_file}")
            subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)
            return os.path.exists(output_file) and os.path.getsize(output_file) > 1000
        except Exception as e:
            print(f"❌ [AudioIO NoMachine] Échec record : {e}")
            return False

    def record_on_speech(self, output_file: str) -> bool:
        print("👂 [AudioIO NoMachine] Attente parole...")
        while True:
            doa, is_speech = self.sdk.get_doa_and_vad()
            if is_speech: break
            time.sleep(0.05)
        return self.record_audio(5, output_file)

    def play_audio(self, input_file: str) -> bool:
        """Lit via PulseAudio (paplay)."""
        try:
            cmd = ["paplay", input_file]
            if self.pulse_sink: cmd.extend(["--device", self.pulse_sink])
            subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            # Petit fallback ALSA si PulseAudio lâche en cours de route
            print("⚠ [AudioIO NoMachine] Fallback ALSA pour la lecture.")
            subprocess.run(["aplay", "-D", f"plughw:{self.card_id},0", input_file], stderr=subprocess.DEVNULL)
            return True

    def close(self):
        if hasattr(self, 'sdk'): self.sdk.close()
    def __enter__(self): return self
    def __exit__(self, *args): self.close()
