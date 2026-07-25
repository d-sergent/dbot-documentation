"""
test_jetson_edge_cloud.py — Architecture Autonome Cloud 100% Jetson (Mode 3 - Edge-TTS)
====================================================================================
Ce script s'exécute 100% sur la Jetson Orin Nano (SANS AUCUNE DÉPENDANCE SUR LE MAC) :
1. Capture Audio ReSpeaker XVF-3800 + VAD logicielle RMS + Pre-roll 5 chunks.
2. ASR Direct Jetson ➔ Groq Cloud API (Whisper Large v3 Turbo < 300 ms).
3. LLM Direct Jetson ➔ Gemini 2.0 Flash (Streaming de tokens par phrase).
4. TTS Direct Jetson ➔ Microsoft Edge-TTS Cloud (Voix `fr-FR-HenriNeural` par défaut).
5. Restitution Audio Local ➔ Joue l'audio sur l'enceinte ReSpeaker JST 5W via paplay.

Usage sur Jetson :
   python3 code/dbot_next/scripts/test_jetson_edge_cloud.py
"""

import sys
import os
import time
import json
import asyncio
import collections
import numpy as np
import subprocess
import wave
import tempfile

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


class JetsonEdgeCloudClient:
    def __init__(self, voice_id: str = "fr-FR-HenriNeural"):
        self.voice_id = os.environ.get("DBOT_EDGE_VOICE", voice_id)
        
        # Chargement de l'environnement .env
        env_found = load_env_robust()
        self.groq_key = os.environ.get("GROQ_API_KEY", "").strip()
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        
        if not self.groq_key:
            print("⚠ [Jetson Edge Cloud] GROQ_API_KEY absente dans ~/dbot/.env")
            print("   👉 Créez le fichier `~/dbot/.env` avec : GROQ_API_KEY=gsk_...\n")

        self.brain = DbotBrainStreaming()
        
        # Initialisation Groq ASR Direct
        self.groq_client = None
        if self.groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_key)
                print("✅ [ASR Direct Jetson] Groq Whisper Large v3 Turbo actif (< 300 ms)")
            except Exception as e:
                print(f"⚠ [ASR Direct Jetson] Module groq non installé : {e}")

        # Vérification du module edge-tts
        try:
            import edge_tts
            print(f"✅ [TTS Direct Jetson] Microsoft Edge-TTS actif (Voix : {self.voice_id})")
        except ImportError:
            print("❌ [TTS Direct Jetson] `edge-tts` n'est pas installé sur la Jetson.")
            print("   👉 Exécutez sur la Jetson : pip3 install edge-tts\n")

        # Détection du sink haut-parleur ReSpeaker
        self.sink_name = self._find_respeaker_sink()

    def _find_respeaker_sink(self) -> str:
        """Trouve le sink PulseAudio du ReSpeaker et active son amplificateur JST."""
        sink_name = "alsa_output.usb-Seeed_Studio_reSpeaker_XVF3800_4-Mic_Array_114993701260500251-00.iec958-stereo"
        try:
            res = subprocess.run(["pactl", "list", "short", "sinks"], capture_output=True, text=True)
            for line in res.stdout.splitlines():
                if any(k in line.lower() for k in ["respeaker", "xvf3800", "seeed"]):
                    parts = line.split()
                    if len(parts) >= 2:
                        sink_name = parts[1]
                        break
        except Exception:
            pass

        print(f"🔊 [Client Audio Jetson] Init sink PulseAudio : {sink_name}")
        cmds = [
            ["pactl", "suspend-sink", sink_name, "0"],
            ["pactl", "set-default-sink", sink_name],
            ["pactl", "set-sink-mute", sink_name, "false"],
            ["pactl", "set-sink-volume", sink_name, "100%"],
            ["amixer", "-c", "0", "cset", "numid=3", "on"],
            ["amixer", "-c", "0", "cset", "numid=4", "on"],
            ["amixer", "-c", "0", "cset", "numid=5", "60"],
            ["amixer", "-c", "0", "cset", "numid=6", "60"],
        ]
        for cmd in cmds:
            subprocess.run(cmd, capture_output=True)
        print("✅ [Client Audio Jetson] Amplificateur JST et sink PulseAudio activés.")

        return sink_name

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

                hallucinations = ["merci d'avoir", "sous-titres", "soustitres", "visionné cette vidéo", "c'est tout pour"]
                if any(h in text.lower() for h in hallucinations):
                    return ""
                return text
            except Exception as e:
                print(f"⚠ [ASR Direct Jetson] Erreur Groq : {e}")
                return ""
        else:
            print("⚠ [ASR Direct Jetson] Clé GROQ_API_KEY absente.")
            return ""

    def _convert_mp3_to_wav(self, mp3_path: str, wav_path: str) -> bool:
        """Convertit un fichier MP3 Edge-TTS en WAV 24kHz mono pour paplay."""
        # 1. ffmpeg
        try:
            res = subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path, "-ar", "24000", "-ac", "1", wav_path],
                capture_output=True, text=True
            )
            if res.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                return True
        except Exception:
            pass

        # 2. mpg123
        try:
            res = subprocess.run(["mpg123", "-w", wav_path, mp3_path], capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                return True
        except Exception:
            pass

        # 3. sox
        try:
            res = subprocess.run(["sox", mp3_path, "-r", "24000", "-c", "1", wav_path], capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                return True
        except Exception:
            pass

        return False

    def speak_text_sync(self, text: str):
        """Synthétise la phrase via Microsoft Edge-TTS (HenriNeural) et la joue. Appel synchrone."""
        asyncio.run(self._speak_text_edge_async(text))

    async def _speak_text_edge_async(self, text: str):
        """Génère l'audio Edge-TTS, le convertit en WAV 24kHz et le joue sur ReSpeaker."""
        import edge_tts

        mp3_path = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
        wav_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name

        try:
            t0 = time.time()
            communicate = edge_tts.Communicate(text, self.voice_id)
            await communicate.save(mp3_path)
            dt_tts_ms = (time.time() - t0) * 1000

            print(f"⏱️  [PROFILING] Edge-TTS ({self.voice_id}) : {dt_tts_ms:.0f} ms")

            # Conversion MP3 -> WAV (paplay PulseAudio n'accepte pas le MP3 brut)
            converted = self._convert_mp3_to_wav(mp3_path, wav_path)
            play_file = wav_path if converted else mp3_path

            print(f"🔊 [Client Audio Jetson] Joue la réponse sur ReSpeaker...")

            # Essai 1 : paplay avec le sink ReSpeaker spécifié
            cmd = ["paplay", f"--device={self.sink_name}", play_file]
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if res.returncode != 0:
                # Essai 2 : paplay sur sink par défaut
                res2 = subprocess.run(["paplay", play_file], capture_output=True, text=True)
                if res2.returncode != 0:
                    # Essai 3 : aplay direct si WAV
                    subprocess.run(["aplay", "-D", "default", play_file], capture_output=True)

        except Exception as e:
            print(f"⚠ [Edge-TTS Jetson] Erreur de synthèse ou de lecture : {e}")
        finally:
            for p in [mp3_path, wav_path]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass


def main():
    print("🧠 === ARCHITECTURE AUTONOME : JETSON EDGE CLOUD (100% Jetson) === 🧠\n")

    voice_id = os.environ.get("DBOT_EDGE_VOICE", "fr-FR-HenriNeural")

    print(f"🌐 Jetson Edge Cloud active (Sans Mac) :")
    print(f"   • ASR Cloud  : Groq Whisper Large v3 Turbo (Direct Jetson ➔ Groq API)")
    print(f"   • LLM Cloud  : Gemini 2.0 Flash (Direct Jetson ➔ Google Cloud API)")
    print(f"   • TTS Cloud  : Microsoft Edge-TTS ({voice_id} ➔ Direct Jetson)")
    print("")

    client = JetsonEdgeCloudClient(voice_id=voice_id)

    # ─── Acquisition audio ───────────────────────────────────────────────────
    audio = AudioIOStreaming(block_size=2560)
    audio.start_capture()

    # ─── Calibration bruit de fond ───────────────────────────────────────────
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

            # Anti-auto-écoute pendant que le robot parle ou réfléchit
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

                        # ─── 3. Synthèse Edge-TTS Direct Jetson (HenriNeural) ─
                        for sentence in sentences_stream:
                            sentence = sentence.strip()
                            if sentence:
                                print(f"🤖 [D-BOT RÉPOND] : \"{sentence}\"")
                                client.speak_text_sync(sentence)

                        # Purge des échos résiduels dans la file micro
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
        print("\n\n🛑 Arrêt du test Jetson Edge Cloud.")
    finally:
        audio.close()


if __name__ == "__main__":
    main()
