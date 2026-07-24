"""
audio_io_streaming.py — Acquisition audio non-bloquante (sounddevice/parecord) pour la stack Next.
=================================================================================================
- Capture en continu sur le ReSpeaker XVF3800
- Sur Jetson (Linux) : Utilise 'parecord' en sous-processus (100% fiable sous PulseAudio, évite le flux à 0)
- Sur Mac (Darwin) : Utilise 'sounddevice' en local
- Interface de queue thread-safe pour alimenter l'ASR
"""

import atexit
import os
import queue
import platform
import signal
import threading
import time
from typing import Optional, Callable

import numpy as np
import sounddevice as sd
import subprocess

from dbot.audio.respeaker_sdk import ReSpeakerSDK, ReSpeakerSDKError

class AudioIOStreamingError(Exception):
    """Exception personnalisée pour le module AudioIO Streaming."""
    pass

class AudioIOStreaming:
    """
    Gestionnaire d'acquisition audio en streaming non-bloquant
    avec couplage VAD matériel (ReSpeaker XVF3800).
    """
    def __init__(self, sample_rate: int = 16000, block_size: int = 1024, doa_callback: Optional[Callable[[int], None]] = None):
        # Suppression de la bulle virtuelle NoMachine (PULSE_SERVER) pour accéder aux vrais micros physiques
        os.environ.pop("PULSE_SERVER", None)
        
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.doa_callback = doa_callback
        
        self.audio_queue = queue.Queue()
        self.is_recording = False
        
        # Références des workers de capture
        self.sd_stream = None         # sounddevice (Mac)
        self.proc = None              # parecord (Linux)
        self.capture_thread = None    # thread de lecture parecord
        
        # Détection de l'OS
        self.is_mac = (platform.system() == "Darwin")
        
        # Détection du matériel (uniquement sur Linux)
        self.card_id = "0"
        self.device_index = None
        self.source_name = None
        
        if not self.is_mac:
            self.card_id = self._detect_respeaker_card()
            self.device_index = self._find_respeaker_device_index()
            self.source_name = self._find_respeaker_source_name()
            # Initialisation et réveil PulseAudio
            self._initialize_hardware()
        else:
            self.device_index = self._find_respeaker_device_index()
        
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
        """Détecte dynamiquement le numéro de carte ALSA du ReSpeaker (insensible à la casse)."""
        try:
            out = subprocess.check_output(["arecord", "-l"], text=True)
            for line in out.splitlines():
                line_lower = line.lower()
                if "respeaker" in line_lower or "xvf3800" in line_lower or "seeed" in line_lower:
                    if "carte" in line_lower:
                        return line.split("carte ")[1].split(":")[0].strip()
                    elif "card" in line_lower:
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

    def _find_respeaker_source_name(self) -> Optional[str]:
        """Trouve le nom symbolique de la source micro dans PulseAudio (insensible à la casse)."""
        try:
            out = subprocess.check_output(["pactl", "list", "short", "sources"], text=True)
            for line in out.splitlines():
                line_lower = line.lower()
                if ("respeaker" in line_lower or "xvf3800" in line_lower or "seeed" in line_lower) and "input" in line_lower and ".monitor" not in line_lower:
                    return line.split()[1]
        except Exception:
            pass
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

        # RÉVEIL FORCÉ DE LA SOURCE MICRO PULSEAUDIO ET ALSA DIRECT
        try:
            # Réveil ALSA hardware direct
            subprocess.run(["amixer", "-c", self.card_id, "cset", "name='Capture Switch'", "on"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            subprocess.run(["amixer", "-c", self.card_id, "cset", "name='Capture Volume'", "60"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            
            if self.source_name:
                print(f"⚡ [AudioIO Streaming] Réveil de la source PulseAudio : {self.source_name}")
                subprocess.run(["pactl", "unload-module", "module-suspend-on-idle"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["pactl", "suspend-source", self.source_name, "0"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-source-mute", self.source_name, "false"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-source-volume", self.source_name, "150%"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                print("✅ [AudioIO Streaming] Source micro réveillée et configurée à 150%.")
            else:
                print("⚠ [AudioIO Streaming] Source PulseAudio ReSpeaker introuvable, utilisation ALSA direct.")
        except Exception as e:
            print(f"⚠ [AudioIO Streaming] Échec réveil PulseAudio/ALSA : {e}")

    def _audio_callback_sd(self, indata, frames, time_info, status):
        """Callback sounddevice utilisé pour macOS (stéréo 2ch -> mono)."""
        if status:
            print(f"⚠ [AudioIO Streaming] Status sounddevice : {status}")
        
        # Extraction du canal gauche mono
        if indata.shape[1] > 1:
            mono_data = indata[:, 0].copy()
        else:
            mono_data = indata[:, 0].copy() if len(indata.shape) > 1 else indata.copy()
        self.audio_queue.put(mono_data)

    def _read_parecord_loop(self):
        """Boucle de lecture en tâche de fond pour lire la sortie brute de parecord/arecord."""
        bytes_to_read = self.block_size * 4  # 2 canaux * 2 octets (int16) = 4 octets par frame
        
        while self.is_recording and self.proc:
            try:
                raw_bytes = self.proc.stdout.read(bytes_to_read)
                if not raw_bytes:
                    time.sleep(0.005)
                    continue
                    
                # Si lecture partielle, on attend le reste
                while len(raw_bytes) < bytes_to_read and self.is_recording:
                    more = self.proc.stdout.read(bytes_to_read - len(raw_bytes))
                    if not more:
                        break
                    raw_bytes += more
                
                if len(raw_bytes) < bytes_to_read:
                    continue
                
                # Conversion des octets bruts PCM en tableau numpy
                data_np = np.frombuffer(raw_bytes, dtype=np.int16).reshape(-1, 2)
                # Canal 0 (mono gauche)
                mono_data = data_np[:, 0].copy()
                self.audio_queue.put(mono_data)
            except Exception as e:
                if self.is_recording:
                    print(f"⚠ [AudioIO Streaming] Erreur lecture parecord/arecord : {e}")
                time.sleep(0.05)

    def start_capture(self):
        """Démarre le flux d'acquisition non-bloquant (sounddevice sur Mac, parecord/arecord sur Linux)."""
        if self.is_recording:
            return
        
        # Vider la queue avant de commencer
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
        self.is_recording = True
        
        if self.is_mac:
            # Démarrage Sounddevice (macOS)
            try:
                self.sd_stream = sd.InputStream(
                    device=self.device_index,
                    samplerate=self.sample_rate,
                    blocksize=self.block_size,
                    channels=2 if self.device_index is not None else 1,
                    dtype='int16',
                    callback=self._audio_callback_sd
                )
                self.sd_stream.start()
                print("🎤 [AudioIO Streaming] Flux d'acquisition démarré (sounddevice mac).")
            except Exception as e:
                self.is_recording = False
                raise AudioIOStreamingError(f"Impossible de démarrer le flux sur Mac : {e}")
        else:
            # Démarrage parecord ou arecord (Linux / Jetson)
            try:
                if self.source_name:
                    cmd = ["parecord", f"--device={self.source_name}", "--format=s16le", "--channels=2", f"--rate={self.sample_rate}", "--raw"]
                    print(f"⚡ [AudioIO Streaming] Lancement parecord (PulseAudio) : {' '.join(cmd)}")
                else:
                    # Repli ALSA Direct si PulseAudio ne possède pas le périphérique
                    cmd = ["arecord", "-D", f"plughw:{self.card_id},0", "-f", "S16_LE", "-c", "2", "-r", f"{self.sample_rate}", "-t", "raw"]
                    print(f"⚡ [AudioIO Streaming] Lancement arecord (ALSA Direct, Carte {self.card_id}) : {' '.join(cmd)}")
                
                self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                
                self.capture_thread = threading.Thread(target=self._read_parecord_loop, daemon=True)
                self.capture_thread.start()
                print("🎤 [AudioIO Streaming] Flux d'acquisition démarré.")
            except Exception as e:
                self.is_recording = False
                raise AudioIOStreamingError(f"Impossible de démarrer le flux via parecord/arecord : {e}")

    def stop_capture(self):
        """Arrête le flux d'acquisition (SIGTERM puis SIGKILL si nécessaire)."""
        if not self.is_recording:
            return
        self.is_recording = False
        try:
            if self.sd_stream:
                self.sd_stream.stop()
                self.sd_stream.close()
                self.sd_stream = None
            if self.proc:
                try:
                    self.proc.terminate()  # SIGTERM
                    self.proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    # arecord résiste à SIGTERM → forcer SIGKILL
                    self.proc.kill()
                    self.proc.wait(timeout=1)
                except Exception:
                    pass
                finally:
                    self.proc = None
            print("🎤 [AudioIO Streaming] Flux d'acquisition arrêté.")
        except Exception as e:
            print(f"⚠ [AudioIO Streaming] Erreur arrêt flux : {e}")

    def __del__(self):
        """Destructeur de secours — tue arecord même si close() n'a pas été appelé."""
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.kill()
        except Exception:
            pass

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
