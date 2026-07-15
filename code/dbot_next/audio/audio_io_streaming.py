"""
audio_io_streaming.py — Acquisition audio non-bloquante (sounddevice) pour la stack Next.
=========================================================================================
- Capture en continu sur le ReSpeaker XVF3800 (canaux stéréo, extraction mono)
- Interface de queue thread-safe pour alimenter l'ASR en temps réel
- Couplage VAD matériel via respeaker_sdk.py
"""

import sounddevice as sd
import numpy as np
import queue
import subprocess
import time
from typing import Optional, Callable
import threading

from dbot.audio.respeaker_sdk import ReSpeakerSDK, ReSpeakerSDKError

class AudioIOStreamingError(Exception):
    """Exception personnalisée pour le module AudioIO Streaming."""
    pass

class AudioIOStreaming:
    """
    Gestionnaire d'acquisition audio en streaming non-bloquant (sounddevice)
    avec couplage VAD matériel (ReSpeaker XVF3800).
    """
    def __init__(self, sample_rate: int = 16000, block_size: int = 1024, doa_callback: Optional[Callable[[int], None]] = None):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.doa_callback = doa_callback
        
        self.audio_queue = queue.Queue()
        self.stream: Optional[sd.InputStream] = None
        self.is_recording = False
        
        # Détection de la carte ALSA
        self.card_id = self._detect_respeaker_card()
        # sounddevice attend l'index du périphérique sous forme de numéro ou d'API native.
        self.device_index = self._find_respeaker_device_index()
        
        # Activation de l'ampli JST
        self._initialize_hardware()
        
        # Connexion au SDK USB ReSpeaker
        try:
            self.sdk = ReSpeakerSDK()
            self.sdk_available = True
            version = self.sdk.get_version()
            print(f"✅ [AudioIO Streaming] SDK USB actif — Firmware {version}")
        except ReSpeakerSDKError as e:
            self.sdk_available = False
            print(f"⚠ [AudioIO Streaming] SDK USB indisponible ({e}).")

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

    def _find_respeaker_device_index(self) -> Optional[int]:
        """Trouve l'index de périphérique sounddevice correspondant au ReSpeaker."""
        try:
            devices = sd.query_devices()
            for idx, dev in enumerate(devices):
                name = dev.get('name', '')
                if "reSpeaker" in name or "XVF3800" in name:
                    if dev.get('max_input_channels', 0) > 0:
                        return idx
        except Exception as e:
            print(f"⚠ [AudioIO Streaming] Erreur recherche périphérique : {e}")
        return None

    def _initialize_hardware(self):
        """Active l'amplificateur JST du ReSpeaker et réveille le périphérique PulseAudio."""
        try:
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=3", "on"], stdout=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=4", "on"], stdout=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=5", "70"], stdout=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "numid=6", "70"], stdout=subprocess.DEVNULL)
            print(f"✅ [AudioIO Streaming] Ampli JST activé (Carte {self.card_id})")
        except Exception as e:
            print(f"⚠ [AudioIO Streaming] Erreur init ampli : {e}")

        # RÉVEIL FORCÉ DE LA SOURCE MICRO PULSEAUDIO (Évite le retour de flux à 0 dû à module-suspend-on-idle)
        try:
            source_name = None
            out = subprocess.check_output(["pactl", "list", "short", "sources"], text=True)
            for line in out.splitlines():
                if ("reSpeaker" in line or "XVF3800" in line) and "input" in line and ".monitor" not in line:
                    source_name = line.split()[1]
                    break
            
            if source_name:
                print(f"⚡ [AudioIO Streaming] Réveil de la source PulseAudio : {source_name}")
                subprocess.run(["pactl", "unload-module", "module-suspend-on-idle"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["pactl", "suspend-source", source_name, "0"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-source-mute", source_name, "false"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-source-volume", source_name, "150%"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                print("✅ [AudioIO Streaming] Source micro réveillée et configurée à 150%.")
            else:
                print("⚠ [AudioIO Streaming] Source PulseAudio ReSpeaker introuvable pour réveil.")
        except Exception as e:
            print(f"⚠ [AudioIO Streaming] Échec réveil PulseAudio : {e}")

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback interne de sounddevice poussant l'audio mono 16-bit dans la queue."""
        if status:
            print(f"⚠ [AudioIO Streaming] Status sounddevice : {status}")
        # Le XMOS produit du stéréo 2ch, on extrait le canal 0 (mono)
        mono_data = indata[:, 0].copy()
        self.audio_queue.put(mono_data)

    def start_capture(self):
        """Démarre le flux d'acquisition non-bloquant."""
        if self.is_recording:
            return
        
        # Vider la queue avant de commencer
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
        try:
            self.stream = sd.InputStream(
                device=self.device_index,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                channels=2,
                dtype='int16',
                callback=self._audio_callback
            )
            self.stream.start()
            self.is_recording = True
            print("🎤 [AudioIO Streaming] Flux d'acquisition démarré.")
        except Exception as e:
            raise AudioIOStreamingError(f"Impossible de démarrer le flux d'entrée : {e}")

    def stop_capture(self):
        """Arrête le flux d'acquisition."""
        if not self.is_recording:
            return
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
            self.is_recording = False
            print("🎤 [AudioIO Streaming] Flux d'acquisition arrêté.")
        except Exception as e:
            print(f"⚠ [AudioIO Streaming] Erreur arrêt flux : {e}")

    def get_audio_chunk(self, timeout: Optional[float] = None) -> Optional[np.ndarray]:
        """Récupère le chunk audio suivant depuis la queue."""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_speech_status(self) -> tuple[int, bool]:
        """Interroge le SDK USB du ReSpeaker pour récupérer la direction (DoA) et le VAD (is_speech)."""
        if not self.sdk_available:
            return 0, False
        try:
            doa, is_speech = self.sdk.get_doa_and_vad()
            if is_speech and self.doa_callback:
                self.doa_callback(doa)
            return doa, is_speech
        except Exception as e:
            print(f"⚠ [AudioIO Streaming] Erreur SDK VAD : {e}")
            return 0, False

    def close(self):
        """Libère toutes les ressources matérielles."""
        self.stop_capture()
        if self.sdk_available and self.sdk:
            self.sdk.close()
