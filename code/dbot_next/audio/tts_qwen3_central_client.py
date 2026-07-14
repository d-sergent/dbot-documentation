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
        
        # File d'attente de lecture asynchrone pour éviter les chevauchements
        self.playback_queue = asyncio.Queue()
        self.worker_task = None
        
        # Buffer de la phrase en cours de réception
        self.current_sentence_audio = bytearray()
        
        # Processus de lecture audio actif
        self.play_process = None
        self._is_connected = False

        # Callbacks utilisateur
        self.on_text_received = None
        self.on_response_end = None

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

    async def _play_audio_data(self, audio_data: bytes, sample_rate: int):
        """Joue un bloc complet d'audio (une phrase) de manière asynchrone via aplay/paplay."""
        if not audio_data:
            return

        # Éviter la redirection audio virtuelle de NoMachine (bulle NX)
        os.environ.pop("PULSE_SERVER", None)
            
        use_pulse = self.is_pulse_running()
        card_id = None
        if not use_pulse:
            try:
                card_id = self.detect_respeaker_card()
            except Exception:
                pass

        # Si aucun lecteur n'est disponible (ex: macOS de test), on simule la durée
        import platform
        if platform.system() == "Darwin" or (not use_pulse and card_id is None):
            # 2 octets par sample (S16_LE)
            duration = len(audio_data) / (2 * sample_rate)
            await asyncio.sleep(duration)
            return

        if use_pulse:
            play_cmd = ["paplay", "--raw", "--channels=1", f"--rate={sample_rate}", "--format=s16le"]
            sink_name = self.detect_respeaker_sink()
            if sink_name:
                play_cmd.extend(["--device", sink_name])
            play_cmd.append("/dev/stdin")
        else:
            play_cmd = ["aplay", "-D", f"plughw:{card_id},0", "-t", "raw", "-c", "1", "-r", str(sample_rate), "-f", "S16_LE", "-"]

        try:
            # On lance le processus de lecture asynchrone
            process = await asyncio.create_subprocess_exec(
                *play_cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            self.play_process = process
            
            # Écriture des données audio sur stdin
            if process.stdin:
                process.stdin.write(audio_data)
                await process.stdin.drain()
                process.stdin.close()
                
            # Attente de la fin de lecture
            await process.wait()
        except Exception as e:
            print(f"❌ [Client Audio] Erreur de lecture : {e}")
        finally:
            self.play_process = None

    async def _playback_worker(self):
        """Worker en tâche de fond qui dépile les phrases et les joue séquentiellement."""
        while True:
            try:
                item = await self.playback_queue.get()
                if item is None:
                    self.playback_queue.task_done()
                    break
                
                audio_data, sample_rate = item
                await self._play_audio_data(audio_data, sample_rate)
                self.playback_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ [Playback Worker] Erreur inattendue : {e}")

    async def connect(self):
        """Se connecte au serveur WebSocket sur le Mac."""
        print(f"🔌 Connexion au serveur central D-Bot : {self.uri}")
        try:
            self.websocket = await websockets.connect(self.uri)
            self._is_connected = True
            print("✅ Connecté au serveur central.")
            
            # Lance le worker de lecture et la boucle de réception
            self.worker_task = asyncio.create_task(self._playback_worker())
            asyncio.create_task(self._receive_loop())
        except Exception as e:
            print(f"❌ Échec de la connexion au serveur central : {e}")
            self._is_connected = False

    async def send_prompt(self, text: str):
        """Envoie la transcription vocale de l'utilisateur au serveur."""
        if not self._is_connected or not self.websocket:
            print("⚠ Impossible d'envoyer le prompt : non connecté.")
            return
            
        await self.websocket.send(json.dumps({
            "text": text
        }))

    async def interrupt(self):
        """Interrompt instantanément la lecture et vide la file d'attente."""
        # 1. Vide la file d'attente
        while not self.playback_queue.empty():
            try:
                self.playback_queue.get_nowait()
                self.playback_queue.task_done()
            except asyncio.QueueEmpty:
                break
                
        # 2. Tue le processus de lecture actuel
        if self.play_process:
            try:
                self.play_process.terminate()
            except Exception:
                pass
            self.play_process = None
            
        # 3. Envoie le signal d'interruption au serveur
        if self._is_connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    "type": "interrupt"
                }))
            except Exception as e:
                print(f"⚠ Échec envoi interruption : {e}")

    async def _wait_for_playback_done(self):
        """Attend la fin de lecture de toutes les phrases en cours et notifie."""
        await self.playback_queue.join()
        if self.on_response_end:
            self.on_response_end()

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
                    self.current_sentence_audio.extend(audio_bytes)
                    
                elif msg_type == "audio_end":
                    if self.current_sentence_audio:
                        sample_rate = payload.get("sample_rate", 24000)
                        self.playback_queue.put_nowait((bytes(self.current_sentence_audio), sample_rate))
                        self.current_sentence_audio = bytearray()
                    
                elif msg_type == "end_of_response":
                    if self.current_sentence_audio:
                        self.playback_queue.put_nowait((bytes(self.current_sentence_audio), 24000))
                        self.current_sentence_audio = bytearray()
                    
                    # On attend que la file d'attente de lecture soit vide avant de finir
                    asyncio.create_task(self._wait_for_playback_done())
                        
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connexion fermée par le serveur.")
            self._is_connected = False
        except Exception as e:
            print(f"❌ Erreur boucle de réception : {e}")
            self._is_connected = False

    def close(self):
        """Ferme proprement la connexion et la lecture."""
        if self.worker_task:
            self.worker_task.cancel()
        if self.play_process:
            try:
                self.play_process.terminate()
            except Exception:
                pass
        if self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), asyncio.get_event_loop())
