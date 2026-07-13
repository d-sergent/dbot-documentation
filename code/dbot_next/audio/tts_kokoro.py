"""
tts_kokoro.py — Synthèse vocale Kokoro-ONNX accélérée sur GPU pour la stack Next.
=============================================================================
- Charge le modèle Kokoro-82M en ONNX via CUDA Execution Provider
- Génère les signaux audio à la volée (inférence ultra-rapide < 150 ms)
- Lecture audio hybride : utilise paplay (Pulse) ou aplay (ALSA Direct) selon l'environnement
"""

import os
import subprocess
import tempfile
from typing import Optional
import soundfile as sf

try:
    from onnxruntime import InferenceSession
    from kokoro_onnx import Kokoro
    HAS_KOKORO = True
except ImportError:
    HAS_KOKORO = False

class TTSError(Exception):
    """Exception personnalisée pour les erreurs de synthèse vocale."""
    pass

class KokoroTTS:
    """
    Système de synthèse vocale génératif Kokoro-ONNX accéléré GPU.
    """
    def __init__(self, 
                 model_path: Optional[str] = None, 
                 voices_path: Optional[str] = None, 
                 pulse_sink: Optional[str] = None):
        self.pulse_sink = pulse_sink
        self.current_play_process = None
        
        if not HAS_KOKORO:
            raise TTSError("Les packages kokoro-onnx ou onnxruntime ne sont pas installés.")

        # Résolution des fichiers du modèle et voix
        self.model_path = model_path or self._find_file("kokoro-v1.0.onnx", ["~/.local/share/kokoro", "./models", "."])
        self.voices_path = voices_path or self._find_file("voices-v1.0.bin", ["~/.local/share/kokoro", "./models", "."])

        if not self.model_path or not os.path.exists(self.model_path):
            raise TTSError(f"[KokoroTTS] Modèle ONNX introuvable. Veuillez vérifier vos chemins.")
        if not self.voices_path or not os.path.exists(self.voices_path):
            raise TTSError(f"[KokoroTTS] Fichier voix BIN introuvable. Veuillez vérifier vos chemins.")

        print(f"⏳ [KokoroTTS] Chargement du modèle {self.model_path} sur GPU...")
        try:
            # Import optionnel de torch pour faciliter la détection CUDA par ORT sur Jetson
            try:
                import torch
            except ImportError:
                pass
                
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            self.session = InferenceSession(self.model_path, providers=providers)
            
            # Afficher quel provider a été retenu (doit être CUDA de préférence)
            active_providers = self.session.get_providers()
            print(f"✅ [KokoroTTS] Session ONNX initialisée. Providers actifs : {active_providers}")
            
            self.kokoro = Kokoro.from_session(self.session, self.voices_path)
            print("✅ [KokoroTTS] Synthétiseur prêt.")
        except Exception as e:
            raise TTSError(f"Échec de l'initialisation de Kokoro-ONNX : {e}")

    def _find_file(self, filename: str, search_dirs: list[str]) -> Optional[str]:
        for d in search_dirs:
            path = os.path.expanduser(os.path.join(d, filename))
            if os.path.exists(path):
                return path
        return None

    def generate_wav(self, text: str, output_path: str, voice: str = "ff_siwis", speed: float = 1.0) -> bool:
        """
        Synthétise le texte et l'écrit au format WAV.
        
        Args:
            text (str): Texte en français à synthétiser.
            output_path (str): Chemin du fichier WAV généré.
            voice (str): Nom de la voix (ex: 'ff_siwis' pour le français).
            speed (float): Vitesse d'élocution.
        """
        if not text:
            return False
            
        try:
            # Choix automatique du code langue selon la voix choisie (f* pour French, a* pour American...)
            lang = "fr-fr" if voice.startswith("f") else "en-us"
            
            samples, sample_rate = self.kokoro.create(
                text=text,
                voice=voice,
                speed=speed,
                lang=lang
            )
            sf.write(output_path, samples, sample_rate)
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        except Exception as e:
            raise TTSError(f"Erreur d'inférence Kokoro-ONNX : {e}")

    def speak(self, text: str, voice: str = "ff_siwis", speed: float = 1.0):
        """
        Génère et joue l'audio de manière synchrone en s'adaptant à l'environnement audio actuel.
        """
        if not text:
            return
            
        print(f"🗣️ [D-Bot dit (Kokoro)] : {text}")
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            temp_wav = tf.name
            
        try:
            if self.generate_wav(text, temp_wav, voice=voice, speed=speed):
                played = False
                
                # 1. Tenter la lecture via PulseAudio si le serveur est actif
                pa_running = False
                try:
                    out = subprocess.check_output(["pgrep", "pulseaudio"])
                    pa_running = len(out) > 0
                except Exception:
                    pass
                
                if pa_running:
                    try:
                        play_cmd = ["paplay", temp_wav]
                        if self.pulse_sink:
                            play_cmd.extend(["--device", self.pulse_sink])
                        self.current_play_process = subprocess.Popen(play_cmd, stderr=subprocess.DEVNULL)
                        self.current_play_process.wait()
                        played = True
                    except Exception:
                        pass
                
                # 2. Repli sur ALSA Direct (aplay) en mode autonome/headless
                if not played:
                    try:
                        card_id = self._detect_respeaker_card()
                        play_cmd = ["aplay", "-D", f"plughw:{card_id},0", temp_wav]
                        self.current_play_process = subprocess.Popen(play_cmd, stderr=subprocess.DEVNULL)
                        self.current_play_process.wait()
                        played = True
                    except Exception as e_alsa:
                        raise TTSError(f"Échec de lecture ALSA direct (aplay) : {e_alsa}")
                
                self.current_play_process = None
        finally:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)

    def stop_speaking(self):
        """Interrompt instantanément la lecture audio en cours en tuant le sous-processus."""
        if self.current_play_process:
            try:
                print("🛑 [KokoroTTS] Interruption immédiate du processus de lecture audio...")
                self.current_play_process.terminate()
                self.current_play_process.wait(timeout=0.2)
            except Exception:
                try:
                    self.current_play_process.kill()
                except Exception:
                    pass
            self.current_play_process = None

    def _detect_respeaker_card(self) -> str:
        """Détecte dynamiquement la carte ALSA."""
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
