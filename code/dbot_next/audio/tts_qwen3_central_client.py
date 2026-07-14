import sys
import os
import json
import base64
import asyncio
import subprocess
import threading
from typing import Optional
import websockets

class Qwen3CentralClient:
    """
    Client centralisé de génération de voix pour D-Bot.
    Se connecte au Mac compagnon via WebSocket pour générer Gemini + Qwen3-TTS.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8001):
        self.host = host
        self.port = port
        self.uri = f"ws://{self.host}:{self.port}/conversation"
        self.websocket = None
        
        # Processus de lecture audio en cours
        self.play_process = None
        self.lock = threading.Lock()
        
        # Callbacks utilisateur
        self.on_text_received = None
        self.on_response_end = None
        
        # Boucle d'event loop pour l'audio asynchrone
        self.loop = None
        self._is_connected = False

    def detect_respeaker_card(self) -> str:
        """Détecte la carte ReSpeaker ou XVF3800 pour ALSA (insensible à la casse)."""
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

    def is_pulse_running(self) -> bool:
        """Vérifie si le serveur PulseAudio est actif pour l'utilisateur actuel."""
        try:
            uid = os.getuid()
            out = subprocess.check_output(["pgrep", "-u", str(uid), "pulseaudio"])
            return len(out) > 0
        except Exception:
            return False

    def detect_respeaker_sink(self) -> Optional[str]:
        """Détecte dynamiquement le nom du sink PulseAudio du ReSpeaker (insensible à la casse)."""
        try:
            out = subprocess.check_output(["pactl", "list", "short", "sinks"], text=True)
            for line in out.splitlines():
                line_lower = line.lower()
                if "respeaker" in line_lower or "xvf3800" in line_lower or "seeed" in line_lower:
                    parts = line.split()
                    if len(parts) > 1:
                        return parts[1]
        except Exception:
            pass
        return None

    def start_playback_stream(self, sample_rate: int = 24000):
        """Démarre un processus aplay ou paplay persistant pour lire l'audio en continu."""
        with self.lock:
            if self.play_process:
                self.stop_playback_stream()
                
            # Éviter la redirection audio virtuelle de NoMachine (bulle NX)
            os.environ.pop("PULSE_SERVER", None)
                
            # Détection de l'absence de lecteurs Linux (ex: macOS)
            use_pulse = self.is_pulse_running()
            card_id = None
            if not use_pulse:
                try:
                    card_id = self.detect_respeaker_card()
                except Exception:
                    pass

            # Si aucun lecteur n'est disponible (ex: macOS de test), on simule
            # pour pouvoir récupérer les chunks audio dans les callbacks sans planter
            import platform
            if platform.system() == "Darwin" or (not use_pulse and card_id is None):
                print("ℹ [Client Audio] Aucun périphérique audio physique détecté. Mode simulation (DummyProcess) activé.")
                class DummyProcess:
                    def __init__(self):
                        class DummyStdin:
                            def write(self, d): pass
                            def flush(self): pass
                        self.stdin = DummyStdin()
                    def terminate(self): pass
                    def kill(self): pass
                    def wait(self, timeout=None): pass
                
                self.play_process = DummyProcess()
                return

            if use_pulse:
                # Utilisation de paplay (PulseAudio) pour la lecture de flux brut
                play_cmd = ["paplay", "--raw", "--channels=1", f"--rate={sample_rate}", "--format=s16le"]
                sink_name = self.detect_respeaker_sink()
                if sink_name:
                    print(f"🔊 [Client Audio] Utilisation du sink PulseAudio : {sink_name}")
                    play_cmd.extend(["--device", sink_name])
                else:
                    print("🔊 [Client Audio] Aucun sink ReSpeaker spécifique détecté, utilisation du sink par défaut.")
                play_cmd.append("/dev/stdin")
            else:
                # Utilisation de aplay (ALSA Direct) sur la carte audio détectée
                play_cmd = ["aplay", "-D", f"plughw:{card_id},0", "-t", "raw", "-c", "1", "-r", str(sample_rate), "-f", "S16_LE", "-"]
                print(f"🔊 [Client Audio] Lecture via ALSA Direct sur carte : {card_id}")
                
            print(f"📣 Exécution commande audio : {' '.join(play_cmd)}")
            try:
                # On ne redirige plus stderr vers DEVNULL pour afficher les erreurs ALSA/Pulse dans la console SSH
                self.play_process = subprocess.Popen(
                    play_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL
                )
            except Exception as e:
                print(f"❌ [Central Client] Erreur lors du lancement de la lecture audio : {e}")
                self.play_process = None

    def stop_playback_stream(self):
        """Arrête instantanément la lecture audio en cours (interruption matérielle)."""
        with self.lock:
            if self.play_process:
                try:
                    self.play_process.terminate()
                    self.play_process.wait(timeout=0.2)
                except Exception:
                    try:
                        self.play_process.kill()
                    except Exception:
                        pass
                self.play_process = None

    def write_audio_chunk(self, data: bytes):
        """Écrit un chunk audio PCM sur l'entrée standard du lecteur."""
        with self.lock:
            if self.play_process and self.play_process.stdin:
                try:
                    self.play_process.stdin.write(data)
                    self.play_process.stdin.flush()
                except Exception as e:
                    print(f"⚠ [Central Client] Erreur d'écriture audio : {e}")

    async def connect(self):
        """Se connecte au serveur WebSocket sur le Mac."""
        print(f"🔌 Connexion au serveur central D-Bot : {self.uri}")
        try:
            self.websocket = await websockets.connect(self.uri)
            self._is_connected = True
            print("✅ Connecté au serveur central.")
            # Lance le récepteur en tâche de fond
            asyncio.create_task(self._receive_loop())
        except Exception as e:
            print(f"❌ Échec de la connexion au serveur central : {e}")
            self._is_connected = False

    async def send_prompt(self, text: str):
        """Envoie la transcription vocale de l'utilisateur au serveur."""
        if not self._is_connected or not self.websocket:
            print("⚠ Impossible d'envoyer le prompt : non connecté.")
            return
            
        # Démarre le lecteur audio pour recevoir le flux
        self.start_playback_stream()
        
        await self.websocket.send(json.dumps({
            "text": text
        }))

    async def interrupt(self):
        """Envoie un signal d'interruption immédiat au serveur central et coupe le haut-parleur."""
        self.stop_playback_stream()
        if self._is_connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    "type": "interrupt"
                }))
            except Exception as e:
                print(f"⚠ Échec envoi interruption : {e}")

    async def _receive_loop(self):
        """Boucle de réception continue des messages du serveur."""
        try:
            async for message in self.websocket:
                payload = json.loads(message)
                msg_type = payload.get("type")
                
                if msg_type == "text":
                    content = payload.get("content", "")
                    if self.on_text_received:
                        self.on_text_received(content)
                    else:
                        print(f"🤖 [D-Bot] : {content}")
                        
                elif msg_type == "audio":
                    base64_data = payload.get("data", "")
                    sample_rate = payload.get("sample_rate", 24000)
                    
                    audio_bytes = base64.b64decode(base64_data)
                    self.write_audio_chunk(audio_bytes)
                    
                elif msg_type == "end_of_response":
                    self.stop_playback_stream()
                    if self.on_response_end:
                        self.on_response_end()
                        
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connexion fermée par le serveur.")
            self._is_connected = False
        except Exception as e:
            print(f"❌ Erreur boucle de réception : {e}")
            self._is_connected = False

    def close(self):
        """Ferme proprement la connexion et la lecture."""
        self.stop_playback_stream()
        if self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), asyncio.get_event_loop())
