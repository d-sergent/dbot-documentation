import os
import sys
import tempfile
import wave
import time
import collections
import subprocess
import webrtcvad
import math
import struct

# Configuration Audio
SAMPLE_RATE = 16000
FRAME_MS    = 30
FRAME_SIZE  = int(SAMPLE_RATE * FRAME_MS / 1000)

def get_respeaker_alsa_hw() -> str:
    try:
        out = subprocess.check_output(["arecord", "-l"], text=True)
        for line in out.splitlines():
            if "carte" in line and ("reSpeaker" in line or "XVF3800" in line):
                return f"plughw:{line.split('carte ')[1].split(':')[0].strip()},0"
            if "card" in line and ("reSpeaker" in line or "XVF3800" in line):
                return f"plughw:{line.split('card ')[1].split(':')[0].strip()},0"
    except Exception: pass
    return "plughw:0,0"

def get_pulse_device_names():
    """Détecte les noms d'entrée (source) et de sortie (sink) du ReSpeaker."""
    source, sink = None, None
    try:
        # Sources (Micro)
        out = subprocess.check_output(["pactl", "list", "short", "sources"], text=True)
        for line in out.splitlines():
            if ("reSpeaker" in line or "XVF3800" in line) and "input" in line and ".monitor" not in line:
                source = line.split()[1]
        # Sinks (Haut-parleur)
        out = subprocess.check_output(["pactl", "list", "short", "sinks"], text=True)
        for line in out.splitlines():
            if "reSpeaker" in line or "XVF3800" in line:
                sink = line.split()[1]
    except Exception: pass
    return source, sink

def main():
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from dbot.audio.stt import LocalSTT
    from dbot.audio.tts import LocalTTS

    print("🔊 === TEST BOUCLE AUDIO AUTONOME (STT -> TTS) === 🔊")
    source_name, sink_name = get_pulse_device_names()
    alsa_hw = get_respeaker_alsa_hw()
    
    if not source_name:
        print("❌ ReSpeaker introuvable."); return

    print(f"✅ Micro: {source_name}\n✅ HP: {alsa_hw}\n✅ Sink Pulse: {sink_name}")

    # --- RÉVEIL FORCÉ ---
    print("⚡ Réveil forcé de PulseAudio + Amplificateur JST...")
    subprocess.run(["pactl", "set-source-mute", source_name, "false"], stderr=subprocess.DEVNULL)
    subprocess.run(["pactl", "set-source-volume", source_name, "100%"], stderr=subprocess.DEVNULL)
    if sink_name:
        subprocess.run(["pactl", "set-default-sink", sink_name], stderr=subprocess.DEVNULL)
        subprocess.run(["pactl", "set-sink-mute", sink_name, "false"], stderr=subprocess.DEVNULL)
        subprocess.run(["pactl", "set-sink-volume", sink_name, "100%"], stderr=subprocess.DEVNULL)
    # Activation de l'amplificateur JST du ReSpeaker (obligatoire, non géré par PulseAudio)
    subprocess.run(["amixer", "-c", "0", "cset", "numid=3", "on"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    subprocess.run(["amixer", "-c", "0", "cset", "numid=4", "on"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    subprocess.run(["amixer", "-c", "0", "cset", "numid=5", "60"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    subprocess.run(["amixer", "-c", "0", "cset", "numid=6", "60"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    print("✅ Amplificateur JST activé.")
    
    stt = LocalSTT(model_size="base", device="cuda")
    tts = LocalTTS(alsa_hw=alsa_hw, pulse_sink=sink_name)
    vad = webrtcvad.Vad(3)

    # --- CALIBRATION ---
    print("\n⏳ Calibration (Silence 2s)...")
    # On passe en --channels=2 car pactl a détecté 2ch
    cmd = ["parecord", f"--device={source_name}", "--format=s16le", "--channels=2", "--rate=16000", "--raw"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    noise_frames = 0
    speech_in_noise = 0
    # Lecture de FRAME_SIZE * 4 octets (2 octets par échantillon * 2 canaux)
    for _ in range(int(2.0 * 1000 / FRAME_MS)):
        frame = proc.stdout.read(FRAME_SIZE * 4)
        if not frame: break
        # Pour le VAD, on ne lui donne que le canal gauche (les premiers 2 octets de chaque paire)
        mono_frame = b''.join([frame[i:i+2] for i in range(0, len(frame), 4)])
        if vad.is_speech(mono_frame, 16000): speech_in_noise += 1
        noise_frames += 1
    proc.terminate(); proc.wait()
    
    noise_ratio = speech_in_noise / noise_frames
    trigger_ratio = min(noise_ratio + 0.15, 0.95)
    print(f"✅ Bruit: {noise_ratio*100:.0f}% -> Seuil: {trigger_ratio*100:.0f}%")

    # --- BOUCLE ---
    print("\n🎤 Parlez maintenant !")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    voiced_frames = []
    triggered = False
    detect_buf = collections.deque(maxlen=10) # Pour la détection (bool)
    pre_buffer = collections.deque(maxlen=10) # Pour garder le son AVANT le trigger (bytes)
    silence_buf = collections.deque(maxlen=30)

    try:
        while True:
            frame = proc.stdout.read(FRAME_SIZE * 4)
            if not frame: break

            # Extraction mono pour le VAD et l'Amplitude (Canal Gauche)
            mono_frame = b''.join([frame[i:i+2] for i in range(0, len(frame), 4)])

            # Calcul Amplitude RMS
            count = len(mono_frame) // 2
            shorts = struct.unpack("<" + "h" * count, mono_frame)
            rms = math.sqrt(sum(s*s for s in shorts) / count) if count > 0 else 0
            meter = "|" * int(min(rms / 100, 20))

            is_speech = vad.is_speech(mono_frame, 16000)
            
            if not triggered:
                print(f"\r💭 [VAD] Amplitude: {rms:5.0f} {meter:<20}", end='', flush=True)
                detect_buf.append(is_speech)
                pre_buffer.append(mono_frame) # On stocke le son nettoyé (mono)
                if (sum(detect_buf) / len(detect_buf) if detect_buf else 0) >= trigger_ratio:
                    triggered = True
                    print("\n✅ PAROLE DÉTECTÉE !")
                    voiced_frames.extend(list(pre_buffer)) # On ajoute le début du son
            else:
                voiced_frames.append(mono_frame)
                silence_buf.append(is_speech)
                if len(silence_buf) == silence_buf.maxlen and sum(silence_buf) < 3: # 90% silence
                    print("📝 Transcription...")
                    proc.terminate(); proc.wait()
                    
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                        wf = wave.open(f.name, 'wb')
                        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(16000)
                        wf.writeframes(b''.join(voiced_frames)); wf.close()
                        
                        text = stt.transcribe(f.name)
                        os.remove(f.name)
                        
                        if text:
                            print(f"👤 VOUS : {text}")
                            tts.speak(f"Vous avez dit : {text}")
                    
                    # Reset pour la suite
                    triggered = False; voiced_frames = []; detect_buf.clear(); silence_buf.clear()
                    print("\n🎤 À l'écoute...")
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    except KeyboardInterrupt:
        proc.terminate()
        print("\n🛑 Arrêt.")

if __name__ == "__main__":
    main()
