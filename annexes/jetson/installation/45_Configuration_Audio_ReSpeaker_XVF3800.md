# 45 - Guide de Configuration Audio : ReSpeaker XVF3800 sur Jetson Orin Nano

Ce guide documente les solutions critiques trouvées en Avril 2026 pour stabiliser le pipeline audio du D-Bot, confronté à des problèmes de grésillement numérique et de blocages matériels sur la Jetson.

## 1. Diagnostic des Problèmes Courants

| Symptôme | Cause Probable | Solution |
| :--- | :--- | :--- |
| **Grésillement assourdissant** (bruit blanc) | Accès direct ALSA (`hw:0,0`) instable sur Jetson | Passer par **PulseAudio (Flux Numérique)** |
| **Silence total** (micro sourd) | Mauvais profil PulseAudio ou micro NoMachine | Configurer le profil **Digital Input (S/PDIF)** |
| **Pas de son au HP JST** | Volume matériel (Mixer) coupé ou index caché | Forcer les **numid ALSA 3, 4, 5, 6** |
| **VAD ne détecte rien** | Flux PulseAudio par défaut redirigé vers NoMachine | Cibler la **Source PulseAudio explicite** |

---

## 2. Configuration du Matériel (Hardware)

1. **Port USB** : Connectez le ReSpeaker exclusivement sur un **port USB-A Bleu (USB 3.0)** de la Jetson. Les ports USB-C ou USB 2.0 peuvent causer des instabilités de timing isochrone sur le Jetson Orin.
2. **Haut-parleur** : Le HP doit être branché sur le port **JST 1.25mm** interne pour bénéficier de l'annulation d'écho matérielle (AEC).

---

## 3. Configuration logicielle (OS & PulseAudio)

### A. Choix du Profil (Crucial)
Ouvrez `pavucontrol` (Contrôle du volume) via NoMachine :
1. Onglet **Configuration** :
   - Chercher le ReSpeaker XVF3800.
   - Sélectionner : **Sortie Stéréo analogique + Entrée Stéréo numérique (IEC958)**.
   *Note : C'est le SEUL profil qui extrait la voix nettoyée par le DSP XMOS.*
2. Onglet **Périphériques d'entrée** :
   - Cliquez sur la coche verte (✔️) du ReSpeaker pour en faire le micro par défaut.

### B. Activation de l'Amplificateur (Mixer ALSA)
Sur Jetson, PulseAudio ne gère parfois que le premier index du volume. Il faut forcer l'allumage manuel de l'amplificateur JST via le terminal :
```bash
amixer -c 0 cset numid=3 on    # PCM Playback Switch (Index 0)
amixer -c 0 cset numid=4 on    # PCM Playback Switch (Index 1)
amixer -c 0 cset numid=5 60    # PCM Playback Volume (Index 0)
amixer -c 0 cset numid=6 60    # PCM Playback Volume (Index 1)
```

---

## 4. Implémentation dans le Cerveau (Python)

Pour éviter les bugs de timing USB et les interférences de NoMachine, le pipeline STT du D-Bot utilise désormais les outils natifs de PulseAudio via `subprocess` au lieu de `PyAudio`.

### A. Identification Dynamique de la Source
Le nom de la source PulseAudio change selon l'ID USB. On le récupère dynamiquement :
```python
import subprocess
def get_pulse_device_name():
    out = subprocess.check_output(["pactl", "list", "short", "sources"], text=True)
    for line in out.splitlines():
        if "reSpeaker" in line and "iec958" in line:
            return line.split()[1]
    return None
```

### B. Capture Audio Robuste (VAD)
Au lieu d'ouvrir un flux PyAudio instable, on utilise `parecord` qui gère parfaitement le ré-échantillonnage et le buffer :
```python
cmd = [
    "parecord",
    f"--device={device_name}",
    "--format=s16le",
    "--channels=1",
    "--rate=16000",
    "--raw"
]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
# Lire proc.stdout.read(640) pour obtenir 20ms de son
```

### C. Test de Sortie Directe (Bypass NoMachine)
Pour tester le haut-parleur sans que NoMachine n'intercepte le son :
```bash
pasuspender -- aplay -D plughw:0,0 /usr/share/sounds/alsa/Front_Center.wav
```

---

## 5. Résumé de l'Architecture Finale

- **Capture** : `parecord` (PulseAudio) → Capture le flux numérique traité (Beamforming + NS).
- **Traitement** : `webrtcvad` + `Faster-Whisper` (STT).
- **Sortie** : `aplay` (ALSA direct) → Joue directement sur le DAC matériel `plughw:0,0`.

Cette architecture garantit que le robot vous entend avec une clarté maximale et parle par sa propre "bouche" physique, même lors d'une session de contrôle à distance.
