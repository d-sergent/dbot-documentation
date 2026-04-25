import os
import sys
import tempfile
import wave
import time
import collections
import subprocess
import webrtcvad

# Permet d'importer nos modules D-Bot locaux même si le script est lancé de n'importe où
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dbot.audio.stt import LocalSTT
from dbot.audio.tts import LocalTTS
from dbot.brain.llm_client import DbotBrain

SAMPLE_RATE = 16000
FRAME_MS    = 30
FRAME_SIZE  = int(SAMPLE_RATE * FRAME_MS / 1000)  # 480 samples


def get_respeaker_alsa_hw() -> str:
    """Détecte l'index ALSA (plughw:X,0) du ReSpeaker pour le haut-parleur."""
    try:
        out = subprocess.check_output(["arecord", "-l"], text=True)
        for line in out.splitlines():
            if "carte" in line and ("reSpeaker" in line or "XVF3800" in line):
                card_num = line.split("carte ")[1].split(":")[0].strip()
                return f"plughw:{card_num},0"
            if "card" in line and ("reSpeaker" in line or "XVF3800" in line):
                card_num = line.split("card ")[1].split(":")[0].strip()
                return f"plughw:{card_num},0"
    except Exception:
        pass
    return "plughw:0,0"


def get_pulse_device_name() -> str:
    """Détecte le nom exact du périphérique PulseAudio (ie958) pour le ReSpeaker."""
    try:
        out = subprocess.check_output(["pactl", "list", "short", "sources"], text=True)
        for line in out.splitlines():
            if ("reSpeaker" in line or "XVF3800" in line) and ".monitor" not in line:
                if "iec958" in line:
                    return line.split()[1]
        # Fallback
        for line in out.splitlines():
            if ("reSpeaker" in line or "XVF3800" in line) and ".monitor" not in line:
                return line.split()[1]
    except Exception as e:
        print(f"Erreur pactl: {e}")
    return None


def _open_pulse_stream(device_name: str):
    """Lance parecord pour capturer le flux numérique natif via PulseAudio."""
    cmd = [
        "parecord",
        f"--device={device_name}",
        "--format=s16le",
        "--channels=1",
        "--rate=16000",
        "--raw"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return proc


def measure_noise_vad_ratio(device_name: str, vad: webrtcvad.Vad, duration: float = 2.5) -> float:
    """
    Mesure le ratio de frames classées 'parole' par le VAD quand personne ne parle.
    Sert de seuil de référence pour ignorer le bruit du ventilateur Jetson.
    """
    proc = _open_pulse_stream(device_name)
    total = int(duration * 1000 / FRAME_MS)
    speech_count = 0
    bytes_per_frame = FRAME_SIZE * 2
    try:
        for _ in range(total):
            frame = proc.stdout.read(bytes_per_frame)
            if not frame or len(frame) < bytes_per_frame:
                break
            if vad.is_speech(frame, SAMPLE_RATE):
                speech_count += 1
    finally:
        proc.terminate()
        proc.wait()
    return speech_count / total if total > 0 else 0.0


def record_until_silence(device_name: str, vad: webrtcvad.Vad,
                          noise_ratio: float,
                          silence_duration: float = 1.0,
                          max_record_s: float = 10.0):
    """
    Enregistre la voix jusqu'à un silence détecté ou max_record_s secondes.
    Le déclenchement n'a lieu que si le ratio de parole dépasse 'noise_ratio + marge'.
    Cela empêche le bruit du ventilateur de déclencher faussement l'enregistrement.

    Returns: bytes bruts PCM (16-bit mono 16kHz) ou None si rien capté
    """
    silence_frames   = int(silence_duration * 1000 / FRAME_MS)
    max_rec_frames   = int(max_record_s * 1000 / FRAME_MS)
    trigger_ratio    = min(noise_ratio + 0.35, 0.95)  # Seuil adaptatif : bruit + 35%

    ring_buffer  = collections.deque(maxlen=silence_frames)
    detect_buf   = collections.deque(maxlen=10)  # Fenêtre de détection (300ms)
    triggered    = False
    voiced_frames = []
    rec_count     = 0

    proc = _open_pulse_stream(device_name)
    bytes_per_frame = FRAME_SIZE * 2
    print(f"💭 [VAD] Écoute (seuil adaptatif: {trigger_ratio*100:.0f}% — bruit fond: {noise_ratio*100:.0f}%)...", end='\r')

    try:
        timeout = int(30 * 1000 / FRAME_MS)
        for _ in range(timeout):
            frame = proc.stdout.read(bytes_per_frame)
            if not frame or len(frame) < bytes_per_frame:
                break
            
            is_speech = vad.is_speech(frame, SAMPLE_RATE)

            if not triggered:
                detect_buf.append(is_speech)
                current_ratio = sum(detect_buf) / len(detect_buf) if detect_buf else 0
                if current_ratio >= trigger_ratio:
                    triggered = True
                    print("💭 [VAD] Parole détectée — enregistrement en cours...")
                    voiced_frames.extend([frame])
                    ring_buffer.clear()
                    rec_count = 0
            else:
                voiced_frames.append(frame)
                rec_count += 1
                ring_buffer.append(is_speech)

                num_unvoiced = sum(1 for s in ring_buffer if not s)
                silence_ok = len(ring_buffer) == ring_buffer.maxlen and \
                             num_unvoiced > 0.85 * ring_buffer.maxlen
                max_ok = rec_count >= max_rec_frames

                if silence_ok or max_ok:
                    if max_ok:
                        print(f"⏱ [VAD] Durée max ({max_record_s}s) — envoi au STT.")
                    break
        else:
            return None  # Timeout sans déclenchement
    finally:
        proc.terminate()
        proc.wait()

    return b''.join(voiced_frames) if voiced_frames else None


def frames_to_wav(frames: bytes) -> str:
    """Sauvegarde des frames PCM brutes dans un fichier WAV temporaire."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        wav_path = f.name
    with wave.open(wav_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(frames)
    return wav_path


def main():
    print("🤖 === D-Bot : Démarrage du Cerveau 100% Hors-Ligne === 🤖\n")

    device_name = get_pulse_device_name()
    if not device_name:
        print("❌ ReSpeaker introuvable via PulseAudio. Branchez-le sur un port USB et relancez.")
        sys.exit(1)
        
    alsa_hw = get_respeaker_alsa_hw()
    print(f"🔌 ReSpeaker détecté : PulseAudio={device_name[:30]}..., ALSA={alsa_hw}")

    # --- INITIALISATION IA ---
    try:
        tts   = LocalTTS(alsa_hw=alsa_hw)
        brain = DbotBrain(model_name="qwen2.5:3b")
        stt   = LocalSTT(model_size="small", device="cuda")
    except Exception as e:
        print(f"\n❌ Erreur initialisation IA : {e}")
        sys.exit(1)

    tts.speak("Mes réseaux neuronaux sont chargés. Je suis totalement autonome.")
    time.sleep(0.8)

    # --- CALIBRATION BRUIT DE FOND ---
    vad = webrtcvad.Vad(3)  # Aggressivité max
    print("\n⏳ Calibration acoustique : Ne parlez pas pendant 2.5 secondes...")
    noise_ratio = measure_noise_vad_ratio(device_name, vad, duration=2.5)
    print(f"✅ Bruit de fond calibré : {noise_ratio*100:.0f}% de frames classées 'parole' par le VAD")
    print(f"   → Seuil de déclenchement fixé à : {min(noise_ratio+0.35, 0.95)*100:.0f}%")

    # --- BOUCLE CONVERSATIONNELLE ---
    print("\n👀 Je vous écoute... (Ctrl+C pour quitter)")

    try:
        while True:
            raw_frames = record_until_silence(device_name, vad, noise_ratio)
            if raw_frames is None:
                continue

            try:
                wav_path  = frames_to_wav(raw_frames)
                user_text = stt.transcribe(wav_path)
                os.remove(wav_path)

                hallus = ["amara.org", "sous-titre", "merci de votre attention",
                          "merci.", "sous titres", "communauté d'amara"]
                if not user_text or len(user_text) < 3 or \
                   any(h in user_text.lower() for h in hallus):
                    continue

                print(f"👤 Vous avez dit : '{user_text}'")

                ai_response = brain.generate_response(user_text)
                brain.trim_memory(max_messages=10)
                tts.speak(ai_response)
                print("\n👀 À l'écoute...")

            except Exception:
                import traceback
                traceback.print_exc()
                print("   → Reprise...\n")

    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt manuel.")


if __name__ == "__main__":
    main()
