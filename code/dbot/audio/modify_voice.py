import sys
import os
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter, sosfilt
from scipy.ndimage import uniform_filter1d

# ──────────────────────────────────────────────
# UTILITAIRES
# ──────────────────────────────────────────────

def normalize(audio, target=0.85):
    peak = np.max(np.abs(audio))
    return audio / peak * target if peak > 0 else audio

def eq_shelf(audio, sr, low_gain_db=0, high_freq=4000, high_gain_db=0):
    def apply_gain(sig, freq, gain_db, btype):
        if abs(gain_db) < 0.1: return sig
        gain = 10 ** (gain_db / 20)
        nyq = sr / 2
        norm = np.clip(freq / nyq, 0.001, 0.999)
        b, a = butter(1, norm, btype=btype)
        filtered = lfilter(b, a, sig)
        return sig + (gain - 1) * filtered if gain_db > 0 else sig - (1 - gain) * filtered
    audio = apply_gain(audio, 300, low_gain_db, 'low')
    audio = apply_gain(audio, high_freq, high_gain_db, 'high')
    return audio

def pitch_shift_simple(audio, sr, semitones=0):
    if semitones == 0: return audio
    factor = 2 ** (semitones / 12.0)
    grain_size = int(sr * 0.03)
    overlap = grain_size // 2
    out = np.zeros_like(audio)
    for i in range(0, len(audio) - grain_size, overlap):
        grain = audio[i:i+grain_size]
        n_new = int(grain_size / factor)
        resampled = np.interp(np.linspace(0, grain_size-1, n_new), np.arange(grain_size), grain)
        resampled = resampled[:grain_size] if len(resampled) > grain_size else np.pad(resampled, (0, grain_size - len(resampled)))
        out[i:i+grain_size] += resampled * np.hanning(grain_size)
    return out

def vocoder_approx(audio, sr, bands=12, wet=0.6, carrier_pitch=0):
    nyq = sr / 2
    freqs = np.logspace(np.log10(80), np.log10(8000), bands + 1)
    out = np.zeros_like(audio)
    t = np.arange(len(audio)) / sr
    factor = 2 ** (carrier_pitch / 12.0)
    for i in range(bands):
        lo, hi = np.clip(freqs[i]/nyq, 0.001, 0.999), np.clip(freqs[i+1]/nyq, 0.001, 0.999)
        sos = butter(2, [lo, hi], btype='band', output='sos')
        band = sosfilt(sos, audio)
        env = uniform_filter1d(np.abs(band), size=int(sr * 0.02))
        carrier_freq = ((freqs[i] + freqs[i+1]) / 2) * factor
        carrier = np.sin(2 * np.pi * carrier_freq * t) + 0.3 * np.sin(2 * np.pi * carrier_freq * 2 * t)
        out += env * carrier
    return (1 - wet) * audio + wet * normalize(out, 0.7)

# ──────────────────────────────────────────────
# PRESETS
# ──────────────────────────────────────────────

PRESETS = {
    "11_vocodeur_dark_10": {
        "desc": "Vocodeur sombre — Pitch -10 + Bass Boost",
        "fn": lambda a, sr: normalize(
            eq_shelf(
                vocoder_approx(pitch_shift_simple(a, sr, semitones=-4), sr, bands=12, wet=0.85, carrier_pitch=-10),
                sr, low_gain_db=15, high_gain_db=-18
            )
        )
    },
    "16_deep_clean_4": {
        "desc": "Homme Posé — Pitch -4 + Bass Boost léger",
        "fn": lambda a, sr: normalize(
            eq_shelf(pitch_shift_simple(a, sr, semitones=-4), sr, low_gain_db=6, high_gain_db=-2)
        )
    }
}

# ──────────────────────────────────────────────
# API PUBLIQUE
# ──────────────────────────────────────────────

def apply_fx(audio, sr, preset_name):
    """Applique un preset DSP à un array numpy audio."""
    target = None
    for k in PRESETS.keys():
        if k.startswith(str(preset_name)):
            target = k
            break
    if not target: return audio
    return PRESETS[target]["fn"](audio, sr)

def main():
    if len(sys.argv) < 2:
        print("Usage : python modify_voice.py input.wav")
        sys.exit(1)
    audio, sr = sf.read(sys.argv[1])
    if audio.ndim == 2: audio = audio.mean(axis=1)
    os.makedirs("dbot_fx", exist_ok=True)
    for name, preset in PRESETS.items():
        print(f"▶  Traitement {name}...")
        res = preset["fn"](audio.copy(), sr)
        sf.write(f"dbot_fx/{name}.wav", np.clip(res, -1.0, 1.0), sr)

if __name__ == "__main__":
    main()
