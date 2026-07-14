"""
async_conversation.py — Orchestrateur conversationnel asynchrone et interruptible (Barge-In).
========================================================================================
- Boucle d'écoute ASR en tâche de fond via sounddevice et Nemotron-3.5-ASR.
- Inférence LLM (Gemini/Ollama) et synthèse TTS (Qwen3-TTS ou Kokoro) en continu.
- Connexion centralisée sur le Mac compagnon avec repli local automatique (ASR -> Ollama -> Kokoro).
- Gestion d'un automate d'états pour interrompre le robot dès que l'utilisateur parle.
"""

import os
import sys
import time
import threading
import queue
import asyncio
import numpy as np
from typing import Optional

# Importations locales de la stack Next
from dbot_next.audio.audio_io_streaming import AudioIOStreaming
from dbot_next.audio.stt_streaming import StreamingSTTNemotron
from dbot_next.audio.tts_kokoro import KokoroTTS
from dbot_next.audio.tts_qwen3_central_client import Qwen3CentralClient
from dbot_next.brain.llm_client_streaming import DbotBrainStreaming

class AsyncConversationManager:
    def __init__(self, 
                 model_stt: str = "nvidia/nemotron-3.5-asr-streaming-0.6b",
                 model_llm: str = "qwen2.5:0.5b",
                 voice_tts: str = "ff_siwis"):
        
        self.voice_tts = voice_tts
        self.state = "idle"  # idle, listening, thinking, speaking
        self.lock = threading.Lock()
        
        # Signaux de synchronisation
        self.interrupted = threading.Event()
        self.stop_requested = threading.Event()
        
        # Initialisation des composants
        print("🤖 [D-Bot Next] Initialisation de la stack Audio...")
        
        # Callback pour afficher la direction de la source sonore
        def on_doa(angle):
            if self.state == "idle":
                print(f"🧭 [DOA] Son détecté à {angle}°.")

        self.audio = AudioIOStreaming(doa_callback=on_doa)
        
        # Liaison de l'interruption matérielle sur le décodeur STT
        self.stt = StreamingSTTNemotron(
            model_name=model_stt,
            interrupt_callback=self.trigger_interrupt
        )
        
        # Stockage de la transcription courante
        self.current_transcript = ""
        self.silence_start_time = None
        self.silence_threshold = 1.0  # secondes de silence pour considérer la fin de phrase
        
        # Threads
        self.asr_thread: Optional[threading.Thread] = None
        self.llm_tts_thread: Optional[threading.Thread] = None
        
        # Queue de tâches LLM à traiter (uniquement pour le mode local)
        self.pending_transcripts = queue.Queue()

        # Config de la connexion centralisée
        self.mac_ip = os.environ.get("DBOT_MAC_IP", "127.0.0.1")
        self.use_central = False
        
        # Démarrage de l'event loop asyncio dans un thread séparé
        self.loop = asyncio.new_event_loop()
        self.async_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.async_thread.start()

        # Tentative de connexion au serveur central du Mac
        print(f"🔌 Tentative de connexion au serveur Mac compagnon ({self.mac_ip})...")
        self.central_client = Qwen3CentralClient(host=self.mac_ip, port=8001)
        
        # On attend la connexion de façon synchrone avec un timeout court
        fut = asyncio.run_coroutine_threadsafe(self.central_client.connect(), self.loop)
        try:
            fut.result(timeout=2.0)
            if self.central_client._is_connected:
                self.use_central = True
                self.central_client.on_text_received = self.handle_central_text
                self.central_client.on_response_end = self.handle_central_end
                print("✨ [D-Bot Next] Serveur centralisé activé avec succès.")
        except Exception:
            pass

        if not self.use_central:
            print("⚠ [D-Bot Next] Serveur central injoignable. Activation de la stack locale (Ollama + KokoroTTS).")
            self.tts = KokoroTTS()
            self.brain = DbotBrainStreaming(model_name=model_llm)

    def _run_async_loop(self):
        """Démarre la boucle d'event loop asyncio pour le WebSocket client."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def handle_central_text(self, content: str):
        """Callback appelé lorsque le serveur central envoie du texte."""
        with self.lock:
            if self.state in ["thinking", "listening"]:
                self.state = "speaking"
        print(f"🤖 [D-Bot (Central)] : {content}")

    def handle_central_end(self):
        """Callback appelé à la fin de la réponse centralisée."""
        with self.lock:
            self.state = "idle"
        print("\n👀 À l'écoute...\n")

    def trigger_interrupt(self):
        """Déclenche une interruption immédiate du robot."""
        with self.lock:
            if self.state in ["thinking", "speaking"]:
                print("\n🚨 [Automate] Interruption demandée (Barge-In ou Mot-clé) !")
                self.interrupted.set()
                
                if self.use_central:
                    asyncio.run_coroutine_threadsafe(self.central_client.interrupt(), self.loop)
                else:
                    self.tts.stop_speaking()
                    
                self.state = "listening"
                self.stt.reset()
                self.current_transcript = ""

    def start(self):
        """Démarre l'orchestrateur."""
        self.stop_requested.clear()
        self.audio.start_capture()
        
        # Démarrage du thread d'ASR en continu
        self.asr_thread = threading.Thread(target=self._asr_loop, daemon=True)
        self.asr_thread.start()
        
        # Démarrage du thread de traitement de dialogue (uniquement si local)
        if not self.use_central:
            self.llm_tts_thread = threading.Thread(target=self._dialogue_loop, daemon=True)
            self.llm_tts_thread.start()
            
        print("\n🤖 [D-Bot Next] Système prêt et à l'écoute ! (Appuyez sur Ctrl+C pour quitter)\n")
        
        if self.use_central:
            # Message vocal d'accueil
            asyncio.run_coroutine_threadsafe(
                self.central_client.send_prompt("Bonjour, système de streaming centralisé initialisé et prêt."),
                self.loop
            )
        else:
            self.tts.speak("Système de streaming local initialisé. Je vous écoute.")

    def stop(self):
        """Arrête proprement l'orchestrateur."""
        print("🤖 [D-Bot Next] Arrêt du système...")
        self.stop_requested.set()
        
        if self.use_central:
            self.central_client.close()
        else:
            self.tts.stop_speaking()
            
        self.audio.close()
        self.loop.call_soon_threadsafe(self.loop.stop)

    def _asr_loop(self):
        """Boucle d'écoute continue en tâche de fond."""
        while not self.stop_requested.is_set():
            # 1. Lire le chunk audio
            chunk = self.audio.get_audio_chunk(timeout=0.05)
            if chunk is None:
                continue
                
            # 2. Lire le statut VAD du matériel
            _, is_speech = self.audio.get_speech_status()
            
            with self.lock:
                if is_speech:
                    # L'utilisateur parle
                    if self.state in ["idle", "thinking", "speaking"]:
                        # Si le robot réfléchissait ou parlait, on l'interrompt !
                        if self.state in ["thinking", "speaking"]:
                            print("\n🗣️  [VAD] Parole détectée pendant la réponse. Interruption...")
                            self.interrupted.set()
                            if self.use_central:
                                asyncio.run_coroutine_threadsafe(self.central_client.interrupt(), self.loop)
                            else:
                                self.tts.stop_speaking()
                        self.state = "listening"
                        self.stt.reset()
                        self.current_transcript = ""
                        self.silence_start_time = None
                        print("🎙️  [D-Bot] Écoute en cours...")
                        
                    # Processus ASR sur le chunk
                    text_part = self.stt.process_chunk(chunk)
                    if text_part:
                        self.current_transcript = text_part
                        # Reset de la détection de fin de phrase
                        self.silence_start_time = None
                        
                else:
                    # L'utilisateur ne parle pas ou plus
                    if self.state == "listening":
                        if self.silence_start_time is None:
                            self.silence_start_time = time.time()
                        elif time.time() - self.silence_start_time > self.silence_threshold:
                            # Fin de phrase détectée !
                            self.state = "thinking"
                            clean_text = self.current_transcript.strip()
                            if len(clean_text) > 2:
                                print(f"\n👤 Vous : '{clean_text}'")
                                if self.use_central:
                                    # Envoi direct au serveur central
                                    asyncio.run_coroutine_threadsafe(
                                        self.central_client.send_prompt(clean_text),
                                        self.loop
                                    )
                                else:
                                    # Envoi à la queue locale
                                    self.pending_transcripts.put(clean_text)
                            else:
                                self.state = "idle"
                            self.current_transcript = ""
                            self.silence_start_time = None

    def _dialogue_loop(self):
        """Boucle de traitement dialogue locale (LLM -> TTS)."""
        while not self.stop_requested.is_set():
            try:
                # Attente d'un texte transcrit
                user_text = self.pending_transcripts.get(timeout=0.1)
            except queue.Empty:
                continue
                
            # Reset du signal d'interruption
            self.interrupted.clear()
            
            print("⏳ [Dialogue] Génération de la réponse locale...")
            try:
                # Streaming LLM
                response_stream = self.brain.generate_response_stream(user_text)
                
                # Parcours des phrases au fur et à mesure de leur génération
                for sentence in response_stream:
                    # Si une interruption a eu lieu pendant qu'on générait ou parlait, on coupe tout !
                    if self.interrupted.is_set():
                        print("🛑 [Dialogue] Flux LLM stoppé suite à une interruption.")
                        break
                        
                    with self.lock:
                        if self.state == "thinking":
                            self.state = "speaking"
                            
                    # Synthèse et lecture de la phrase
                    try:
                        self.tts.speak(sentence, voice=self.voice_tts)
                    except Exception as e_tts:
                        print(f"⚠ [Dialogue] Erreur de lecture : {e_tts}")
                        
                with self.lock:
                    if not self.interrupted.is_set():
                        self.state = "idle"
                        print("\n👀 À l'écoute...\n")
                        
            except Exception as e:
                print(f"❌ [Dialogue] Erreur traitement : {e}")
                with self.lock:
                    self.state = "idle"
                    
            self.pending_transcripts.task_done()

if __name__ == "__main__":
    manager = AsyncConversationManager()
    try:
        manager.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()


if __name__ == "__main__":
    manager = AsyncConversationManager()
    try:
        manager.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()
