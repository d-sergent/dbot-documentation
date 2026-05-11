
"""
dbot_voice_fx.py
Post-traitement audio pour voix Piper TTS — presets dbot
Dépendances : pip install numpy scipy soundfile
Usage      : python dbot_voice_fx.py input.wav
Sortie     : dossier dbot_fx/ avec un fichier par preset
"""

import sys
import os
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter, sosfilt, butter as _butter
from scipy.ndimage import uniform_filter1d

# ──────────────────────────────────────────────
# UTILITAIRES
# ──────────────────────────────────────────────

def load(path):
    audio, sr = sf.read(path, always_2d=False)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)          # stéréo → mono
    return audio.astype(np.float32), sr

def save(audio, sr, path):
    audio = np.clip(audio, -1.0, 1.0)
    sf.write(path, audio, sr)
    print(f"  ✓  {path}")

def normalize(audio, target=0.85):
    peak = np.max(np.abs(audio))
    return audio / peak * target if peak > 0 else audio

# ──────────────────────────────────────────────
# BLOCS DSP
# ──────────────────────────────────────────────

def eq_shelf(audio, sr, low_gain_db=0, high_freq=4000, high_gain_db=0):
    """Shelving EQ simple via biquad approximé avec butter."""
    def apply_gain(sig, freq, gain_db, btype):
        if abs(gain_db) < 0.1:
            return sig
        gain = 10 ** (gain_db / 20)
        nyq = sr / 2
        norm = freq / nyq
        norm = np.clip(norm, 0.001, 0.999)
        b, a = butter(1, norm, btype=btype)
        filtered = lfilter(b, a, sig)
        if gain_db > 0:
            return sig + (gain - 1) * filtered
        else:
            return sig - (1 - gain) * filtered
    audio = apply_gain(audio, 300, low_gain_db, 'low')
    audio = apply_gain(audio, high_freq, high_gain_db, 'high')
    return audio

def bandpass(audio, sr, low=300, high=8000):
    nyq = sr / 2
    sos = butter(4, [low / nyq, high / nyq], btype='band', output='sos')
    return sosfilt(sos, audio)

def pitch_shift_simple(audio, sr, semitones=0):
    """Pitch shift approché par resample + time-stretch (sans librosa)."""
    if semitones == 0:
        return audio
    ratio = 2 ** (semitones / 12)
    # Resample (change pitch + durée)
    n_new = int(len(audio) / ratio)
    indices = np.linspace(0, len(audio) - 1, n_new)
    shifted = np.interp(indices, np.arange(len(audio)), audio)
    # Remettre à la durée originale (tempo-stretch naïf)
    indices2 = np.linspace(0, len(shifted) - 1, len(audio))
    return np.interp(indices2, np.arange(len(shifted)), shifted)

def add_reverb(audio, sr, room=0.3, wet=0.25):
    """Reverb simple par convolution avec IR synthétique."""
    decay_samples = int(sr * room)
    t = np.linspace(0, room, decay_samples)
    ir = np.exp(-6 * t) * np.random.randn(decay_samples) * 0.3
    ir[0] = 1.0
    reverbed = np.convolve(audio, ir, mode='full')[:len(audio)]
    return (1 - wet) * audio + wet * reverbed

def ring_modulator(audio, sr, freq=80, depth=0.3):
    """Modulation en anneau → effet métallique/robot."""
    t = np.arange(len(audio)) / sr
    carrier = np.sin(2 * np.pi * freq * t)
    return audio * (1 - depth + depth * carrier)

def bitcrush(audio, bits=10):
    """Réduction de bit depth → texture numérique."""
    steps = 2 ** bits
    return np.round(audio * steps) / steps

def chorus(audio, sr, depth_ms=5, rate_hz=1.2, wet=0.4):
    """Chorus léger pour épaissir la voix."""
    depth = int(sr * depth_ms / 1000)
    t = np.arange(len(audio)) / sr
    lfo = (np.sin(2 * np.pi * rate_hz * t) * 0.5 + 0.5) * depth
    out = np.zeros_like(audio)
    for i in range(len(audio)):
        d = int(lfo[i])
        j = max(0, i - d)
        out[i] = audio[j]
    return (1 - wet) * audio + wet * out

def telephone_filter(audio, sr):
    """Bande passante téléphonique 300–3400 Hz."""
    nyq = sr / 2
    sos = butter(4, [300 / nyq, 3400 / nyq], btype='band', output='sos')
    return sosfilt(sos, audio)

def vocoder_approx(audio, sr, bands=8, wet=0.6):
    """Vocodeur simplifié par banque de filtres."""
    nyq = sr / 2
    freqs = np.logspace(np.log10(80), np.log10(8000), bands + 1)
    out = np.zeros_like(audio)
    t = np.arange(len(audio)) / sr
    for i in range(bands):
        lo, hi = freqs[i] / nyq, freqs[i + 1] / nyq
        lo, hi = np.clip(lo, 0.001, 0.999), np.clip(hi, 0.001, 0.999)
        if lo >= hi:
            continue
        sos = butter(2, [lo, hi], btype='band', output='sos')
        band = sosfilt(sos, audio)
        env = uniform_filter1d(np.abs(band), size=int(sr * 0.02))
        carrier_freq = (freqs[i] + freqs[i + 1]) / 2
        carrier = np.sin(2 * np.pi * carrier_freq * t)
        out += env * carrier
    return (1 - wet) * audio + wet * normalize(out, 0.7)

# ──────────────────────────────────────────────
# PRESETS
# ──────────────────────────────────────────────

PRESETS = {

    "01_ia_froide": {
        "desc": "IA assistante froide et précise — Siri-like",
        "fn": lambda a, sr: (
            lambda a1: normalize(
                eq_shelf(a1, sr, low_gain_db=-4, high_gain_db=3) * 0.95
            )
        )(pitch_shift_simple(a, sr, semitones=-1))
    },

    "02_android_soft": {
        "desc": "Androïde subtil — légèrement synthétique mais naturel",
        "fn": lambda a, sr: normalize(
            ring_modulator(
                eq_shelf(a, sr, low_gain_db=-6, high_gain_db=4),
                sr, freq=60, depth=0.15
            )
        )
    },

    "03_robot_classique": {
        "desc": "Robot classique — ring mod + bitcrush léger",
        "fn": lambda a, sr: normalize(
            bitcrush(
                ring_modulator(a, sr, freq=100, depth=0.5),
                bits=12
            )
        )
    },

    "04_synthwave": {
        "desc": "Voix synthwave / rétro-futuriste — chorus + reverb",
        "fn": lambda a, sr: normalize(
            add_reverb(
                chorus(
                    eq_shelf(a, sr, high_gain_db=2),
                    sr, depth_ms=8, rate_hz=0.8, wet=0.5
                ),
                sr, room=0.4, wet=0.3
            )
        )
    },

    "05_radio_cockpit": {
        "desc": "Filtre radio / intercom — téléphonique + léger bruit",
        "fn": lambda a, sr: normalize(
            telephone_filter(a, sr) +
            np.random.randn(len(a)) * 0.005
        )
    },

    "06_vocodeur": {
        "desc": "Vocodeur synthétique — très robotique",
        "fn": lambda a, sr: normalize(
            vocoder_approx(a, sr, bands=12, wet=0.75)
        )
    },

    "07_dbot_signature": {
        "desc": "Mix dbot — IA froide + légère modulation + reverb court",
        "fn": lambda a, sr: normalize(
            add_reverb(
                ring_modulator(
                    eq_shelf(
                        pitch_shift_simple(a, sr, semitones=-1.5),
                        sr, low_gain_db=-5, high_gain_db=3.5
                    ),
                    sr, freq=70, depth=0.18
                ),
                sr, room=0.15, wet=0.18
            )
        )
    },

    "08_dbot_heavy": {
        "desc": "Voix lourde et puissante — Pitch bas + Boost Basses",
        "fn": lambda a, sr: normalize(
            eq_shelf(
                pitch_shift_simple(a, sr, semitones=-4),
                sr, low_gain_db=8, high_gain_db=-2
            )
        )
    },

    "09_cyborg_male": {
        "desc": "Cyborg masculin — Pitch -2.5 + Ring Mod + Chorus",
        "fn": lambda a, sr: normalize(
            chorus(
                ring_modulator(
                    pitch_shift_simple(a, sr, semitones=-2.5),
                    sr, freq=50, depth=0.25
                ),
                sr, depth_ms=10, rate_hz=0.5, wet=0.3
            )
        )
    },
}

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage : python dbot_voice_fx.py input.wav")
        sys.exit(1)

    input_path = sys.argv[1]
    out_dir = "dbot_fx"
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n🔊  Chargement : {input_path}")
    audio, sr = load(input_path)
    print(f"    Durée : {len(audio)/sr:.2f}s  |  SR : {sr} Hz\n")

    for name, preset in PRESETS.items():
        print(f"▶  {name}  —  {preset['desc']}")
        try:
            result = preset["fn"](audio.copy(), sr)
            out_path = os.path.join(out_dir, f"{name}.wav")
            save(result, sr, out_path)
        except Exception as e:
            print(f"  ✗  Erreur : {e}")

    print(f"\n✅  {len(PRESETS)} fichiers générés dans ./{out_dir}/")
    print("   → Écoute chaque preset et note tes préférences pour affiner.\n")

if __name__ == "__main__":
    main()
