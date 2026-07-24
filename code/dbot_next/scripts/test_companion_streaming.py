"""
test_companion_streaming.py — Test unitaire de la boucle conversationnelle déportée.
==================================================================================
- Se connecte au serveur compagnon unique du Mac (companion_server.py).
- Capture l'audio micro de la Jetson avec une VAD LOGICIELLE (seuil RMS calibré).
- Stream l'audio PCM brut au Mac uniquement en cours d'élocution.
- Reçoit et joue la synthèse vocale retournée.

VAD LOGICIELLE :
  - Phase de calibration : 2s d'écoute silence → mesure RMS bruit de fond.
  - Seuil de déclenchement : max(bruit_rms * 3.0, RMS_MIN_SPEECH)
  - Pre-roll : les 5 derniers chunks de silence avant déclenchement sont inclus
    pour éviter de couper le début des mots.
"""

import os
import sys
import time
import asyncio
import threading
import collections
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dbot_next.audio.audio_io_streaming import AudioIOStreaming
from dbot_next.audio.tts_qwen3_central_client import Qwen3CentralClient


# ─── Constantes VAD Logicielle ─────────────────────────────────────────────
CALIBRATION_DURATION_S  = 2.0   # Durée de mesure du bruit de fond
RMS_MIN_SPEECH          = 150   # Seuil RMS absolu minimum adaptatif pour déclencher
SPEECH_TRIGGER_CHUNKS   = 2     # Nb de chunks consécutifs > seuil pour "début de phrase"
SILENCE_TRIGGER_CHUNKS  = 10    # Nb de chunks consécutifs < seuil pour "fin de phrase" (~1.6s à 160ms/chunk)
PRE_ROLL_CHUNKS         = 5     # Nb de chunks de silence pré-parole à inclure dans le stream


def compute_rms(chunk: np.ndarray) -> float:
    """Calcule le volume RMS d'un chunk audio numpy int16."""
    if len(chunk) == 0:
        return 0.0
    return float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))


def calibrate_noise_floor(audio: AudioIOStreaming, duration_s: float) -> float:
    """
    Écoute `duration_s` secondes de silence et retourne le RMS moyen du bruit de fond.
    Affiche une barre de progression.
    """
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


def main():
    print("🧠 === TEST DE CONVERSATION DÉPORTÉE (ASR + LLM + TTS sur Mac) === 🧠\n")

    mac_ip = os.environ.get("DBOT_MAC_IP", "127.0.0.1")
    print(f"🔌 Tentative de connexion au serveur compagnon Mac ({mac_ip}:8001)...")

    client = Qwen3CentralClient(host=mac_ip, port=8001)

    # ─── État de la machine à états ─────────────────────────────────────────
    state = "idle"  # idle | listening | thinking | speaking
    lock  = threading.Lock()

    # ─── Callbacks réception Mac ─────────────────────────────────────────────
    def on_asr(text):
        print(f"\n🗣️  [VOUS AVEZ DIT] : \"{text}\"")
        nonlocal state
        with lock:
            state = "speaking"

    def on_text(content):
        print(f"🤖 [D-BOT RÉPOND] : \"{content}\"")

    def on_end():
        print("\n👀 À l'écoute...\n")
        nonlocal state
        with lock:
            state = "idle"

    client.on_asr_received = on_asr
    client.on_text_received = on_text
    client.on_response_end = on_end

    # ─── Démarrage event loop asyncio ───────────────────────────────────────
    loop = asyncio.new_event_loop()
    threading.Thread(target=lambda: (asyncio.set_event_loop(loop), loop.run_forever()), daemon=True).start()

    fut = asyncio.run_coroutine_threadsafe(client.connect(), loop)
    try:
        fut.result(timeout=5.0)
        if not client._is_connected:
            print("❌ Impossible de se connecter au serveur Mac.")
            return
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return

    print("✨ Connexion établie avec succès !")

    # ─── Acquisition audio ───────────────────────────────────────────────────
    audio = AudioIOStreaming(block_size=2560)  # ≈160ms/chunk @ 16kHz stéréo
    audio.start_capture()

    # ─── Calibration bruit de fond ───────────────────────────────────────────
    rms_threshold = calibrate_noise_floor(audio, CALIBRATION_DURATION_S)

    print(f"\n🎙️ Prêt ! Parlez dans le micro ReSpeaker (Ctrl+C pour quitter)...")
    print(f"   (Seuil de déclenchement : {rms_threshold:.0f} RMS)\n")

    # ─── Variables VAD logicielle ─────────────────────────────────────────────
    above_threshold_count = 0   # Chunks consécutifs au-dessus du seuil
    below_threshold_count = 0   # Chunks consécutifs en-dessous du seuil
    pre_roll = collections.deque(maxlen=PRE_ROLL_CHUNKS)  # Buffer pré-parole

    chunk_count   = 0
    is_listening  = False

    try:
        while True:
            chunk = audio.get_audio_chunk(timeout=0.1)
            if chunk is None:
                continue

            chunk_count += 1
            rms = compute_rms(chunk)
            max_val = int(np.max(np.abs(chunk)))

            # Affichage diagnostic toutes les 15 frames
            if chunk_count % 15 == 0:
                marker = "🔴" if is_listening else "⬜"
                sys.stdout.write(f"\r{marker} [Diag] Chunks: {chunk_count:4d} | RMS: {rms:6.0f} | Max: {max_val:5d} | Seuil: {rms_threshold:.0f}   ")
                sys.stdout.flush()

            with lock:
                current_state = state

            # ─── Machine à états VAD + streaming ────────────────────────────
            if not is_listening:
                # On accumule les chunks dans le pre-roll
                pre_roll.append(chunk)

                if rms > rms_threshold:
                    above_threshold_count += 1
                    if above_threshold_count >= SPEECH_TRIGGER_CHUNKS:
                        # Déclenchement de la détection vocale
                        is_listening = True
                        below_threshold_count = 0
                        above_threshold_count = 0
                        print(f"\n🎙️ [VAD] Parole détectée (RMS={rms:.0f}). Streaming au Mac...")

                        if current_state == "speaking":
                            # Barge-in : interrompre la réponse en cours
                            asyncio.run_coroutine_threadsafe(client.interrupt(), loop)

                        asyncio.run_coroutine_threadsafe(client.send_control("start"), loop)

                        # Envoyer le pre-roll (début du mot possiblement coupé)
                        for pre_chunk in list(pre_roll):
                            asyncio.run_coroutine_threadsafe(
                                client.send_audio_chunk(pre_chunk.tobytes()), loop
                            )

                        with lock:
                            state = "listening"
                else:
                    above_threshold_count = 0

            else:
                # En cours d'écoute : streamer chaque chunk vers le Mac
                asyncio.run_coroutine_threadsafe(
                    client.send_audio_chunk(chunk.tobytes()), loop
                )

                if rms < rms_threshold:
                    below_threshold_count += 1
                    if below_threshold_count >= SILENCE_TRIGGER_CHUNKS:
                        # Fin de phrase
                        print(f"\n🎙️ [VAD] Fin de phrase (silence {below_threshold_count} chunks). Envoi pour transcription...")
                        asyncio.run_coroutine_threadsafe(client.send_control("end"), loop)
                        is_listening = False
                        above_threshold_count = 0
                        below_threshold_count = 0
                        pre_roll.clear()
                        with lock:
                            state = "thinking"
                else:
                    below_threshold_count = 0

    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du test.")
    finally:
        audio.close()
        client.close()
        loop.call_soon_threadsafe(loop.stop)


if __name__ == "__main__":
    main()
