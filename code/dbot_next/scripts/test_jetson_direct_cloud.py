"""
test_jetson_direct_cloud.py — Architecture Découplée "Jetson Direct Cloud" (Action 1)

Ce script s'exécute directement sur la Jetson Orin Nano :
1. Capture Audio ReSpeaker XVF-3800 + VAD logicielle RMS + Pre-roll.
2. ASR Direct Jetson ➔ Groq Cloud API (Whisper Large v3 Turbo < 300 ms).
3. LLM Direct Jetson ➔ Gemini 2.0 Flash (Streaming de tokens).
4. TTS Stream Mac ➔ Envoie chaque phrase au Mac (Port 8002) pour Qwen3-TTS MLX (GPU Metal).
5. Restitution Audio Local ➔ Reçoit le PCM 24 kHz et le joue sur l'enceinte JST 5W via paplay.

Usage sur Jetson :
   export DBOT_MAC_IP="192.168.68.120"
   python3 code/dbot_next/scripts/test_jetson_direct_cloud.py
"""

import sys
import os
import time
import json
import base64
import asyncio
import collections
import numpy as np
import subprocess
import wave
import tempfile
import threading

# Configuration du PYTHONPATH
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(WORKSPACE_DIR, "Code"))
sys.path.append(os.path.join(WORKSPACE_DIR, "code"))

from dbot.brain.llm_client import load_env_robust
load_env_robust()

from dbot_next.audio.audio_io_streaming import AudioIOStreaming
from dbot_next.brain.llm_client_streaming import DbotBrainStreaming

# ─── Constantes VAD Logicielle ─────────────────────────────────────────────
CALIBRATION_DURATION_S  = 2.0   # Durée de mesure du bruit de fond
RMS_MIN_SPEECH          = 150   # Seuil RMS absolu minimum adaptatif pour déclencher
SPEECH_TRIGGER_CHUNKS   = 2     # Nb de chunks consécutifs > seuil pour "début de phrase"
SILENCE_TRIGGER_CHUNKS  = 10    # Nb de chunks consécutifs < seuil pour "fin de phrase" (~1.6s @ 160ms/chunk)
PRE_ROLL_CHUNKS         = 5     # Nb de chunks de silence pré-parole à inclure


def compute_rms(chunk: np.ndarray) -> float:
    if len(chunk) == 0:
        return 0.0
    return float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))


def calibrate_noise_floor(audio: AudioIOStreaming, duration_s: float) -> float:
    print(f"🔇 Calibration du bruit de fond ({duration_s:.0f}s) — restez silencieux...")
    rms_samples = []
    t_start = time.time()
    while time.time() - t_start < duration_s:
        elapsed = time.time() - t_start
        pct = int(elapsed / duration_s * 20)
        bar = "█" * pct + "░" * (20 - pct)
        sys.stdout.write(f"\r  [{bar}] {elapsed:.1f}/{duration_s:.1f}s")
        sys.stdout.flush()
        chunk = audio.get_audio_chunk(timeout=0.2)
        if chunk is not None:
            rms_samples.append(compute_rms(chunk))
    sys.stdout.write("\n")
    if not rms_samples:
        return RMS_MIN_SPEECH
    noise_rms = float(np.mean(rms_samples))
    threshold = max(noise_rms * 3.0, RMS_MIN_SPEECH)
    print(f"✅ Bruit de fond moyen : {noise_rms:.0f} RMS → Seuil voix : {threshold:.0f} RMS")
    return threshold


class JetsonDirectCloudClient:
    def __init__(self, mac_ip: str, tts_port: int = 8002):
        self.mac_ip = mac_ip
        self.tts_port = tts_port
        
        # S'assurer que le .env est bien chargé
        env_found = load_env_robust()
        self.groq_key = os.environ.get("GROQ_API_KEY", "").strip()
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        
        if not self.groq_key:
            print("⚠ [Jetson Direct] GROQ_API_KEY absente.")
            print("   👉 Rappel : Le fichier `.env` est dans `.gitignore` (non synchronisé par Git).")
            print("   👉 Créez le fichier `~/dbot/.env` sur la Jetson avec : GROQ_API_KEY=gsk_...\n")

        self.brain = DbotBrainStreaming()
        
        # Initialisation du client Groq ASR direct
        self.groq_client = None
        if self.groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_key)
                print("✅ [ASR Direct Jetson] Groq Whisper Large v3 Turbo actif (< 300 ms)")
            except Exception as e:
                print(f"⚠ [ASR Direct Jetson] Module groq non installé ou erreur : {e}")
                print("   👉 Exécutez sur la Jetson : pip3 install groq httpx sniffio distro pydantic --no-deps")

        # Détection du sink haut-parleur ReSpeaker
        self.sink_name = self._find_respeaker_sink()

    def _find_respeaker_sink(self) -> str:
        try:
            res = subprocess.run(["pactl", "list", "short", "sinks"], capture_output=True, text=True)
            for line in res.stdout.splitlines():
                if any(k in line.lower() for k in ["respeaker", "xvf3800", "seeed"]):
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
        except Exception:
            pass
        return "alsa_output.usb-Seeed_Studio_reSpeaker_XVF3800_4-Mic_Array_114993701260500251-00.iec958-stereo"

    def transcribe_audio_int16(self, audio_int16: np.ndarray) -> str:
        """Transcrit le buffer audio int16 en texte via Groq Cloud ASR Direct."""
        if self.groq_client is not None:
            try:
                import io
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(16000)
                    wf.writeframes(audio_int16.tobytes())
                wav_buffer.seek(0)

                t0 = time.time()
                transcription = self.groq_client.audio.transcriptions.create(
                    file=("audio.wav", wav_buffer, "audio/wav"),
                    model="whisper-large-v3-turbo",
                    language="fr",
                    response_format="text"
                )
                dt_ms = (time.time() - t0) * 1000
                text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
                print(f"⏱️  [PROFILING] Groq Cloud ASR Direct : {dt_ms:.0f} ms → \"{text}\"")

                # Filtre anti-hallucinations
                hallucinations = ["merci d'avoir", "sous-titres", "soustitres", "visionné cette vidéo", "c'est tout pour"]
                if any(h in text.lower() for h in hallucinations):
                    return ""
                return text
            except Exception as e:
                print(f"⚠ [ASR Direct Jetson] Erreur Groq : {e}")
                return ""
        else:
            print("⚠ [ASR Direct Jetson] Clé GROQ_API_KEY absente dans .env")
            return ""

    async def speak_text_via_mac_tts(self, text: str):
        """Envoie la phrase au serveur Mac (Port 8002) pour synthèse Qwen3-TTS et la joue localement."""
        import websockets

        url = f"ws://{self.mac_ip}:{self.tts_port}/tts"
        try:
            async with websockets.connect(url, open_timeout=5.0) as ws:
                # Demande de synthèse au serveur Mac
                await ws.send(json.dumps({"type": "synthesize", "text": text}))

                audio_bytes_list = []
                sample_rate = 24000

                # Réception des chunks audio du Mac
                async for raw_msg in ws:
                    try:
                        msg = json.loads(raw_msg)
                        if msg.get("type") == "audio_chunk":
                            b64 = msg.get("data", "")
                            sample_rate = msg.get("sample_rate", 24000)
                            audio_bytes_list.append(base64.b64decode(b64))
                        elif msg.get("type") == "tts_end":
                            break
                    except Exception:
                        pass

                if audio_bytes_list:
                    full_pcm = b"".join(audio_bytes_list)
                    self._play_pcm_audio(full_pcm, sample_rate)

        except Exception as e:
            print(f"⚠ [TTS Mac Connection] Erreur connexion serveur TTS {url} : {e}")

    def _play_pcm_audio(self, pcm_bytes: bytes, sample_rate: int):
        """Joue les octets PCM 16-bit mono sur l'enceinte ReSpeaker JST via paplay."""
        duration_s = len(pcm_bytes) / (sample_rate * 2)
        print(f"🔊 [Client Audio Jetson] Joue la réponse TTS ({duration_s:.1f}s, {sample_rate} Hz)...")
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name

        try:
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(pcm_bytes)

            # Essai 1 : avec le sink ReSpeaker spécifié
            cmd = ["paplay", f"--device={self.sink_name}", wav_path]
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if res.returncode != 0:
                # Essai 2 : paplay sur le sink par défaut PulseAudio
                cmd_def = ["paplay", wav_path]
                res_def = subprocess.run(cmd_def, capture_output=True, text=True)
                if res_def.returncode != 0:
                    # Essai 3 : aplay ALSA direct
                    subprocess.run(["aplay", "-D", "default", wav_path], capture_output=True)
        except Exception as err:
            print(f"⚠ [Client Audio Jetson] Erreur de lecture audio : {err}")
        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)


def main():
    print("🧠 === ARCHITECTURE DÉCOUPLÉE : JETSON DIRECT CLOUD (Action 1) === 🧠\n")

    mac_ip = os.environ.get("DBOT_MAC_IP", "192.168.68.120")
    tts_port = int(os.environ.get("DBOT_TTS_PORT", 8002))

    print(f"🌐 Jetson Direct Cloud active :")
    print(f"   • ASR Cloud  : Groq Whisper Large v3 Turbo (Direct Jetson ➔ Groq API)")
    print(f"   • LLM Cloud  : Gemini 2.0 Flash (Direct Jetson ➔ Google Cloud API)")
    print(f"   • TTS GPU    : Mac M1 Max ({mac_ip}:{tts_port})")
    print("")

    client = JetsonDirectCloudClient(mac_ip=mac_ip, tts_port=tts_port)

    # ─── Acquisition audio ───────────────────────────────────────────────────
    audio = AudioIOStreaming(block_size=2560)
    audio.start_capture()

    # ─── Calibration ─────────────────────────────────────────────────────────
    rms_threshold = calibrate_noise_floor(audio, CALIBRATION_DURATION_S)

    print(f"\n🎙️ Prêt ! Parlez dans le micro ReSpeaker (Ctrl+C pour quitter)...")
    print(f"   (Seuil de déclenchement : {rms_threshold:.0f} RMS)\n")

    above_threshold_count = 0
    below_threshold_count = 0
    pre_roll = collections.deque(maxlen=PRE_ROLL_CHUNKS)

    chunk_count = 0
    is_listening = False
    speech_chunks = []
    state = "idle"  # idle | listening | thinking | speaking

    loop = asyncio.new_event_loop()
    threading.Thread(target=lambda: (asyncio.set_event_loop(loop), loop.run_forever()), daemon=True).start()

    try:
        while True:
            chunk = audio.get_audio_chunk(timeout=0.1)
            if chunk is None:
                continue

            chunk_count += 1
            rms = compute_rms(chunk)
            max_val = int(np.max(np.abs(chunk)))

            if chunk_count % 15 == 0:
                marker = "🔴" if is_listening else "⬜"
                sys.stdout.write(f"\r{marker} [Diag] Chunks: {chunk_count:4d} | RMS: {rms:6.0f} | Max: {max_val:5d} | Seuil: {rms_threshold:.0f}   ")
                sys.stdout.flush()

            # anti-auto-écoute pendant que le robot parle ou réfléchit
            if not is_listening:
                if state in ["speaking", "thinking"]:
                    pre_roll.clear()
                    above_threshold_count = 0
                    continue

                pre_roll.append(chunk)

                if rms > rms_threshold:
                    above_threshold_count += 1
                    if above_threshold_count >= SPEECH_TRIGGER_CHUNKS:
                        is_listening = True
                        above_threshold_count = 0
                        below_threshold_count = 0
                        print(f"\n🎙️ [VAD Jetson] Parole détectée (RMS={rms:.0f}). Accumulation...")
                        speech_chunks = list(pre_roll)
                        state = "listening"
                else:
                    above_threshold_count = 0

            else:
                speech_chunks.append(chunk)

                if rms < rms_threshold:
                    below_threshold_count += 1
                    if below_threshold_count >= SILENCE_TRIGGER_CHUNKS:
                        print(f"\n🎙️ [VAD Jetson] Fin de phrase. Lancement ASR Direct Groq...")
                        is_listening = False
                        above_threshold_count = 0
                        below_threshold_count = 0
                        pre_roll.clear()
                        state = "thinking"

                        full_audio = np.concatenate(speech_chunks, axis=0) if speech_chunks else np.array([], dtype=np.int16)
                        speech_chunks = []

                        # ─── 1. ASR Groq Direct ──────────────────────────────
                        text_user = client.transcribe_audio_int16(full_audio)
                        if not text_user:
                            print("ℹ️ [ASR Jetson] Aucun texte reconnu.")
                            state = "idle"
                            continue

                        print(f"🗣️  [VOUS AVEZ DIT] : \"{text_user}\"")

                        # ─── 2. LLM Gemini Stream Direct ─────────────────────
                        t0_llm = time.time()
                        sentences_stream = client.brain.generate_response_stream(text_user)
                        dt_llm_ms = (time.time() - t0_llm) * 1000
                        print(f"⏱️  [PROFILING] Gemini LLM Direct : {dt_llm_ms:.0f} ms (1er token)")

                        state = "speaking"

                        # ─── 3. Transmettre chaque phrase au Mac TTS ────────
                        for sentence in sentences_stream:
                            sentence = sentence.strip()
                            if sentence:
                                print(f"🤖 [D-BOT RÉPOND] : \"{sentence}\"")
                                fut = asyncio.run_coroutine_threadsafe(
                                    client.speak_text_via_mac_tts(sentence), loop
                                )
                                fut.result()

                        # Purge des échos résiduels
                        time.sleep(0.3)
                        while not audio.audio_queue.empty():
                            try:
                                audio.audio_queue.get_nowait()
                            except Exception:
                                break

                        state = "idle"
                        print("\n👀 À l'écoute...\n")
                else:
                    below_threshold_count = 0

    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du test Jetson Direct Cloud.")
    finally:
        audio.close()
        loop.call_soon_threadsafe(loop.stop)


if __name__ == "__main__":
    main()
