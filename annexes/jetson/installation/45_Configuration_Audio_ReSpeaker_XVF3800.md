# 45 - Guide de Configuration Audio : ReSpeaker XVF3800 sur Jetson Orin Nano

Ce guide documente les solutions **validées en Avril 2026** pour stabiliser le pipeline audio complet (STT → TTS) du D-Bot sur Jetson Orin Nano. Il est conçu pour être auto-suffisant : si un problème survient, ce guide doit permettre de retrouver la solution même sans contexte.

---

## 1. Architecture Matérielle (Câblage)

| Composant | Connexion | Remarque |
| :--- | :--- | :--- |
| **ReSpeaker XVF3800** | Port USB-A **Bleu** (USB 3.0) de la Jetson | NE PAS utiliser USB-C ou USB 2.0 |
| **Haut-parleur JST 5W** | Port **JST 1.25mm** sur le ReSpeaker | Bénéficie de l'AEC (Annulation d'Écho) matérielle |

> [!IMPORTANT]
> Le port JST du ReSpeaker possède un **amplificateur matériel** qui **n'est pas activé automatiquement** par Linux/PulseAudio. Il faut l'activer manuellement via les registres ALSA à chaque démarrage (voir section 3).

---

## 2. Diagnostic Rapide des Problèmes

| Symptôme | Cause | Solution |
| :--- | :--- | :--- |
| **Amplitude bloquée à 128** | PulseAudio capte en 1 canal (mono) au lieu de 2 (stéréo) | Utiliser `--channels=2` dans `parecord` puis extraire le canal gauche |
| **Voix non reconnue sans NoMachine** | La source PulseAudio reste en état **SUSPENDED** : elle retourne un signal constant (bruit de fond fixe ~600 RMS) au lieu de l'audio live | Appeler `pactl suspend-source SOURCE 0` avant de lancer parecord, ET booster le volume à 150% |
| **Haut-parleur muet** | Amplificateur JST éteint (non géré par PulseAudio) | Lancer les 4 commandes `amixer cset numid=3/4/5/6` |
| **Son sorti uniquement vers le Mac (NoMachine)** | NoMachine capture le Sink par défaut | Forcer `pactl set-default-sink` sur le ReSpeaker ET utiliser `PULSE_SINK` en variable d'environnement |
| **Grésillement assourdissant** | Accès direct ALSA `hw:0,0` instable | Passer par PulseAudio (ne jamais utiliser `hw:`, toujours `plughw:`) |
| **`aplay -D plughw:0,0` → "Périphérique occupé"** | PulseAudio verrouille le matériel | Utiliser `paplay` ou `aplay` sans `-D` (via PulseAudio) |
| **`webrtcvad.Error: Error while processing frame`** | Frame en stéréo passée au VAD (qui attend du mono) | Extraire le canal gauche avant de passer la frame au VAD |

---

## 3. Solution Complète : Séquence de Démarrage Obligatoire

**Ces commandes doivent être exécutées à chaque démarrage du robot**, avant tout script audio. Elles sont intégrées dans `test_audio_loop.py` et `LocalTTS` mais peuvent être lancées manuellement :

```bash
# 1. Identifier les noms des périphériques
SOURCE=$(pactl list short sources | grep "XVF3800" | grep "input" | grep -v "monitor" | awk '{print $2}')
SINK=$(pactl list short sinks | grep "XVF3800" | awk '{print $2}')

# 2. Réveiller le micro
pactl set-source-mute "$SOURCE" false
pactl set-source-volume "$SOURCE" 100%

# 3. Réveiller le haut-parleur PulseAudio
pactl set-default-sink "$SINK"
pactl set-sink-mute "$SINK" false
pactl set-sink-volume "$SINK" 100%

# 4. CRITIQUE : Activer l'amplificateur matériel JST du ReSpeaker
# (PulseAudio ne le fait JAMAIS automatiquement)
amixer -c 0 cset numid=3 on   # PCM Playback Switch (canal Gauche)
amixer -c 0 cset numid=4 on   # PCM Playback Switch (canal Droit)
amixer -c 0 cset numid=5 60   # PCM Playback Volume (canal Gauche) — max=100
amixer -c 0 cset numid=6 60   # PCM Playback Volume (canal Droit)  — max=100
```

> [!TIP]
> Pour tester que le haut-parleur fonctionne après ces commandes :
> ```bash
> piper -m ~/.local/share/piper-voices/fr_FR-upmc-medium.onnx --output_file /tmp/test.wav <<< "Bonjour je suis le robot" && paplay /tmp/test.wav
> ```

---

## 4. Architecture Logicielle Validée (Pipeline Python)

### A. Identification Dynamique des Périphériques
```python
import subprocess

def get_pulse_device_names():
    """Détecte les noms d'entrée (source) et de sortie (sink) du ReSpeaker."""
    source, sink = None, None
    out_sources = subprocess.check_output(["pactl", "list", "short", "sources"], text=True)
    for line in out_sources.splitlines():
        if ("XVF3800" in line or "reSpeaker" in line) and "input" in line and ".monitor" not in line:
            source = line.split()[1]
    out_sinks = subprocess.check_output(["pactl", "list", "short", "sinks"], text=True)
    for line in out_sinks.splitlines():
        if "XVF3800" in line or "reSpeaker" in line:
            sink = line.split()[1]
    return source, sink
```

### B. Capture Audio (VAD) — CRITIQUE : 2 canaux
Le ReSpeaker est déclaré en **2 canaux (stéréo)** dans PulseAudio. Si on force `--channels=1`, on obtient une amplitude bloquée à 128 (silence). Il faut capturer en stéréo puis extraire le canal gauche pour le VAD :

```python
cmd = ["parecord", f"--device={source_name}", "--format=s16le",
       "--channels=2",  # OBLIGATOIRE — le ReSpeaker est déclaré stéréo
       "--rate=16000", "--raw"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

FRAME_SIZE = 480  # = 16000 Hz × 30ms
while True:
    frame_stereo = proc.stdout.read(FRAME_SIZE * 4)  # 4 octets/sample (2ch × 2 octets)
    # Extraction du canal gauche pour le VAD (mono 16-bit)
    mono_frame = b''.join([frame_stereo[i:i+2] for i in range(0, len(frame_stereo), 4)])
    is_speech = vad.is_speech(mono_frame, 16000)  # Toujours passer mono_frame, pas frame_stereo
```

### C. Sortie TTS — Méthode Fichier Temporaire + paplay
La méthode la plus robuste (immunisée contre les interceptions NoMachine) :

```python
import tempfile, os, subprocess

def speak(text, voice_model_path, pulse_sink=None):
    env = os.environ.copy()
    if pulse_sink:
        env["PULSE_SINK"] = pulse_sink
        subprocess.run(["pactl", "set-sink-mute", pulse_sink, "false"], stderr=subprocess.DEVNULL)
        subprocess.run(["pactl", "set-sink-volume", pulse_sink, "100%"], stderr=subprocess.DEVNULL)

    # Générer le WAV dans un fichier temporaire (évite les bugs de pipe Python)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        temp_wav = tf.name
    subprocess.run(f'echo "{text}" | piper -m {voice_model_path} --output_file {temp_wav}',
                   shell=True, stderr=subprocess.DEVNULL, env=env)
    if os.path.exists(temp_wav) and os.path.getsize(temp_wav) > 0:
        play_cmd = ["paplay", temp_wav]
        if pulse_sink:
            play_cmd.extend(["--device", pulse_sink])
        subprocess.run(play_cmd, env=env)
        os.remove(temp_wav)
```

---

## 5. Profil PulseAudio Correct (`pavucontrol`)

Si le profil PulseAudio est perdu (après une mise à jour ou un redémarrage) :
1. Lancer `pavucontrol` (via NoMachine ou interface graphique)
2. Onglet **Configuration** → ReSpeaker XVF3800
3. Sélectionner : **`Stéréo numérique (IEC958)`**
4. *(Note : Le port JST analogique n'a pas de profil séparé — il est piloté via les registres amixer)*

---

## 6. Optimisation des Ressources (RAM)

Sur Jetson Orin Nano (8GB), le pipeline STT+LLM est gourmand. Pour libérer ~1.5 Go de RAM :

| Action | Commande |
| :--- | :--- |
| **Passer en mode Headless** | `sudo systemctl isolate multi-user.target` |
| **Relancer l'interface graphique** | `sudo systemctl isolate graphical.target` |
| **Vérifier la RAM libre** | `free -m` |

---

## 7. Résumé de l'Architecture Finale Validée

```
Micro (4 canaux PDM)
    ↓ [XVF3800 DSP : Beamforming + NS + AEC]
    ↓ [USB Audio IEC958 → parecord 2ch 16kHz]
    ↓ [Extraction canal Gauche → Mono 16kHz]
    ↓ [webrtcvad (VAD) → Faster-Whisper (STT)]
    ↓ [LLM Ollama]
    ↓ [Piper TTS → /tmp/robot.wav]
    ↓ [paplay → PulseAudio Sink ReSpeaker]
    ↓ [DAC interne XVF3800 → Ampli JST (numid=3,4,5,6)]
Haut-parleur JST 5W
```
