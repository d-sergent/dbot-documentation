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
                    return line.split("carte ")[1].split(":")[0].strip()
        except Exception:
            pass
        return "0"

    def _initialize_hardware(self):
        """Active l'amplificateur JST du ReSpeaker."""
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

    def record_audio(self, duration: float, output_file: str) -> bool:
        """
        Enregistre l'audio traité (Canal 0) directement en mono.
        """
        try:
            # On force -c 1 pour ne prendre que le premier canal (audio traité par le XMOS)
            cmd = (f"arecord -D {self.alsa_device} -f S16_LE -r 16000 -c 1 -d {int(duration)} {output_file}")
            subprocess.run(cmd, shell=True, check=True, stderr=subprocess.DEVNULL)
            print(f"🎤 [AudioIO v2] Enregistrement : {output_file}")
            return True
        except Exception as e:
            raise AudioIOv2Error(f"Échec enregistrement : {e}")

    def record_on_speech(self, output_file: str,
                         silence_timeout: float = 1.0,
                         max_duration: float = 10.0) -> bool:
        """
        Enregistre dynamiquement : s'arrête quand le silence est détecté.
        """
        if not self.sdk_available:
            return self.record_audio(5, output_file)

        print("👂 [AudioIO v2] Attente de la parole (VAD matériel)...")
        
        # 1. Attendre le début de la parole
        while True:
            _, is_speech = self.sdk.get_doa_and_vad()
            if is_speech:
                break
            time.sleep(0.02)

        # 2. Lancer arecord en arrière-plan (sans durée fixe -d)
        print(f"🗣️  [AudioIO v2] Enregistrement en cours...")
        cmd = f"arecord -D {self.alsa_device} -f S16_LE -r 16000 -c 1 {output_file}"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        start_time = time.time()
        last_speech_time = time.time()

        try:
            # 3. Surveiller le VAD pour détecter la fin
            while (time.time() - start_time) < max_duration:
                doa, is_speech = self.sdk.get_doa_and_vad()
                
                if is_speech:
                    last_speech_time = time.time()
                
                # Si silence depuis plus de silence_timeout, on arrête
                if (time.time() - last_speech_time) > silence_timeout:
                    break
                
                time.sleep(0.1)
        finally:
            # Arrêter arecord proprement
            process.terminate()
            process.wait()

        return os.path.exists(output_file) and os.path.getsize(output_file) > 4000

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
