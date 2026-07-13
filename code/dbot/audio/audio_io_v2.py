"""
audio_io_v2.py — Version 2 du module AudioIO intégrant le SDK USB ReSpeaker.

DIFFÉRENCES vs audio_io.py (v1) :
  - VAD matériel on-chip via respeaker_sdk.py (remplace webrtcvad)
  - DOA disponible en temps réel pour orienter le cou Pan/Tilt
  - Capture audio inchangée (arecord stéréo → sox mono, validée v1)
  - Callback optionnel pour publier le DOA vers ROS2 ou un autre module

FICHIERS DE RÉFÉRENCE (ne pas modifier) :
  - code/dbot/audio/audio_io.py  (v1 stable, validée 10/05/2026)
  - code/dbot/audio/respeaker_sdk.py (SDK USB officiel Seeed)
"""

import subprocess
import os
import sys
import time
import threading
from typing import Optional, Callable

from dbot.audio.respeaker_sdk import ReSpeakerSDK, ReSpeakerSDKError


class AudioIOv2Error(Exception):
    """Exception pour les erreurs du module AudioIO v2."""
    pass


class AudioIOv2:
    """
    Module AudioIO v2 — Capture audio + VAD matériel + DOA.

    Utilise le SDK USB officiel Seeed pour exploiter le VAD on-chip
    et le DOA (Direction of Arrival) du ReSpeaker XVF3800.

    Args:
        pulse_sink (str, optional): Sink PulseAudio pour la lecture.
        doa_callback (Callable, optional): Fonction appelée avec l'angle DOA
            à chaque détection de parole. Signature : fn(angle: int)
    """

    def __init__(self, pulse_sink: Optional[str] = None,
                 doa_callback: Optional[Callable[[int], None]] = None):

        self.pulse_sink = pulse_sink
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
            print(f"✅ [AudioIO v2] SDK USB actif — Firmware {version}")
        except ReSpeakerSDKError as e:
            self.sdk_available = False
            print(f"⚠ [AudioIO v2] SDK USB indisponible ({e}). Fonctionnement dégradé.")

    def _detect_respeaker_card(self) -> str:
        """Détecte dynamiquement le numéro de carte ALSA du ReSpeaker."""
        try:
            out = subprocess.check_output(["arecord", "-l"], text=True)
            for line in out.splitlines():
                if "reSpeaker" in line or "XVF3800" in line:
                    if "carte" in line:
                        return line.split("carte ")[1].split(":")[0].strip()
                    elif "card" in line:
                        return line.split("card ")[1].split(":")[0].strip()
        except Exception:
            pass
        return "0"

    def _initialize_hardware(self):
        """Active l'amplificateur JST et réveille la source PulseAudio (Doc 45 §4)."""
        # 1. Amplificateur JST
        try:
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=3", "on"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=4", "on"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=5", "70"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=6", "70"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ [AudioIO v2] Ampli JST activé (Carte {self.card_id})")
        except Exception as e:
            print(f"⚠ [AudioIO v2] Erreur init ampli : {e}")

        # 2. Réveil de la source PulseAudio (CRITIQUE sans NoMachine — Doc 45 §4)
        # Sans NoMachine, PulseAudio suspend le micro → signal constant → silence
        try:
            # Désactiver la mise en veille automatique
            subprocess.run(["pactl", "unload-module", "module-suspend-on-idle"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Identifier la source ReSpeaker dynamiquement
            result = subprocess.check_output(
                ["pactl", "list", "short", "sources"], text=True
            )
            source_name = None
            for line in result.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[1]
                    # Exclure les sources "monitor" (loopback du HP, pas le micro)
                    if name.endswith('.monitor'):
                        continue
                    if ("respeaker" in name.lower() or "xvf3800" in name.lower() or "iec958" in name.lower()):
                        source_name = name
                        break
            if source_name:
                subprocess.run(["pactl", "suspend-source", source_name, "0"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-source-mute", source_name, "false"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-source-volume", source_name, "150%"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.pulse_source = source_name  # Mémoriser pour parecord
                print(f"✅ [AudioIO v2] Source micro réveillée : ...{source_name[-45:]}")
            else:
                self.pulse_source = None
                print("⚠ [AudioIO v2] Source ReSpeaker non trouvée dans PulseAudio")
        except Exception as e:
            print(f"⚠ [AudioIO v2] Erreur réveil source PulseAudio : {e}")

    def record_audio(self, duration: float, output_file: str) -> bool:
        """
        Enregistre l'audio via PulseAudio (parecord).
        Note : parecord n'a pas d'option -d, on utilise 'timeout' pour limiter la durée.
        """
        try:
            device_arg = f"--device={self.pulse_source}" if getattr(self, 'pulse_source', None) else ""
            # 'timeout N' arrête parecord après N secondes (parecord n'a pas d'option -d)
            cmd = (f"timeout {int(duration)} parecord {device_arg} "
                   f"--channels=2 --format=s16le --rate=16000 --raw | "
                   f"sox -t raw -r 16000 -e signed -b 16 -c 2 - -c 1 {output_file}")
            subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)
            # Note : pas de check=True car timeout retourne exit code 124 à expiration (normal)
            print(f"🎤 [AudioIO v2] Enregistrement : {output_file}")
            return os.path.exists(output_file) and os.path.getsize(output_file) > 1000
        except Exception as e:
            raise AudioIOv2Error(f"Échec enregistrement : {e}")

    def record_on_speech(self, output_file: str,
                         silence_timeout: float = 1.0,
                         max_duration: float = 10.0) -> bool:
        """
        Attend la détection de parole par le VAD matériel,
        puis enregistre un segment audio de durée fixe.
        """
        if not self.sdk_available:
            return self.record_audio(5, output_file)

        print("👂 [AudioIO v2] Attente de la parole (VAD matériel)...")

        # Attendre que la parole commence
        while True:
            doa, is_speech = self.sdk.get_doa_and_vad()
            if is_speech:
                if self.doa_callback:
                    self.doa_callback(doa)
                break
            time.sleep(0.05)

        # Enregistrer un segment fixe (5 secondes — suffisant pour une phrase)
        print("🗣️  [AudioIO v2] Enregistrement en cours...")
        return self.record_audio(5, output_file)

    def play_audio(self, input_file: str) -> bool:
        """Lit un fichier audio via PulseAudio (paplay)."""
        if not os.path.exists(input_file):
            raise AudioIOv2Error(f"Fichier introuvable : {input_file}")
        try:
            cmd = ["paplay", input_file]
            if self.pulse_sink:
                cmd.extend(["--device", self.pulse_sink])
            subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
            print(f"🔊 [AudioIO v2] Lecture : {input_file}")
            return True
        except Exception as e:
            raise AudioIOv2Error(f"Échec lecture : {e}")

    def get_doa(self) -> int:
        """
        Lit l'angle DOA actuel (direction de la voix).

        Returns:
            int: Angle 0-359° ou -1 si le SDK est indisponible.
        """
        if not self.sdk_available:
            return -1
        doa, _ = self.sdk.get_doa_and_vad()
        return doa

    def close(self):
        """Libère les ressources (SDK USB)."""
        if self.sdk_available and self.sdk:
            self.sdk.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


if __name__ == "__main__":
    print("\n--- Test AudioIO v2 (SDK USB + VAD matériel) ---")
    try:
        with AudioIOv2() as audio:
            print("\n🎯 Test 1 : Lecture du DOA")
            doa = audio.get_doa()
            print(f"   Direction actuelle : {doa}°")

            print("\n🎯 Test 2 : Enregistrement sur détection de parole")
            success = audio.record_on_speech("/tmp/test_audio_v2.wav")
            if success:
                audio.play_audio("/tmp/test_audio_v2.wav")
                print("✅ Test AudioIO v2 réussi !")
    except AudioIOv2Error as e:
        print(f"❌ {e}")
        sys.exit(1)
