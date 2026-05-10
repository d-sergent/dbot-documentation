# 45 - Guide de Configuration Audio : ReSpeaker XVF3800 sur Jetson Orin Nano

> **Document de référence — Validé Avril 2026**
> Ce guide est auto-suffisant. Si un problème survient, pointez un assistant IA vers ce fichier pour qu'il dispose de tout le contexte nécessaire sans historique de conversation.

---

## 1. Architecture Matérielle

| Composant | Connexion | Remarque |
| :--- | :--- | :--- |
| **ReSpeaker XVF3800** | Port **USB-A Bleu (USB 3.0)** de la Jetson | NE PAS utiliser USB-C ou USB 2.0 (instabilités isochrones) |
| **Haut-parleur JST 5W** | Port **JST 1.25mm** sur la carte ReSpeaker | Bénéficie de l'AEC (Annulation d'Écho) matérielle |

### Comment le ReSpeaker apparaît dans Linux
```
# Entrée micro (Source PulseAudio) :
alsa_input.usb-Seeed_Studio_reSpeaker_XVF3800_4-Mic_Array_...-00.iec958-stereo

# Sortie HP (Sink PulseAudio) :
alsa_output.usb-Seeed_Studio_reSpeaker_XVF3800_4-Mic_Array_...-00.iec958-stereo

# Carte ALSA :
plughw:0,0   (carte 0, périphérique 0 — USB Audio)
```

Le suffixe `iec958` désigne le profil PulseAudio (numérique S/PDIF). Le DSP XMOS convertit les 4 micros PDM en flux numérique USB — ce **n'est pas** une connexion S/PDIF physique.

---

## 2. Comportement Selon l'État de NoMachine

> [!IMPORTANT]
> **NoMachine modifie profondément l'état de PulseAudio.** Le robot doit fonctionner **sans NoMachine** en production. Les différences de comportement sont documentées ici.

### Avec NoMachine connecté
| Élément | État |
| :--- | :--- |
| Source micro | `RUNNING` — audio live reçu immédiatement |
| Source par défaut PulseAudio | **`nx_remapped_out`** (micro du Mac distant !) |
| Amplitude de fond | ~200 RMS |
| Amplitude voix | ~400–900 RMS |
| VAD (mode 3) | Fonctionne normalement |

### Sans NoMachine (Production / Robot Autonome)
| Élément | État |
| :--- | :--- |
| Source micro | **`SUSPENDED`** — retourne un signal constant (~600 RMS) |
| Source par défaut PulseAudio | ReSpeaker (correct) |
| Amplitude de fond | ~600–900 RMS (signal figé, ne varie PAS) |
| Amplitude voix | Identique au fond — la voix ne "monte" pas |
| VAD (mode 3) | Ne détecte rien (signal constant perçu comme non-parole) |

> [!CAUTION]
> **PIÈGE :** Sans NoMachine, l'amplitude de fond peut être de ~880 RMS. Si le seuil de détection est codé en dur (ex: 500), il y a des faux positifs. Si le seuil est trop haut (ex: 1877 = 3×626), la voix ne dépasse jamais le bruit de fond car le signal est FIGÉ.
> La solution n'est pas d'ajuster le seuil : c'est de **sortir la source de l'état SUSPENDED**.

---

## 3. Diagnostic Rapide

| Symptôme | Cause Racine | Solution |
| :--- | :--- | :--- |
| **Amplitude bloquée à 128** | `parecord` capture en 1 canal (mono) mais le ReSpeaker est déclaré stéréo (2ch) | Utiliser `--channels=2` dans `parecord`, puis extraire le canal gauche pour le VAD |
| **Amplitude constante (~600–900) — voix ne monte pas** | Source PulseAudio en état **SUSPENDED** | `pactl unload-module module-suspend-on-idle` puis `pactl suspend-source SOURCE 0` |
| **VAD ne détecte pas la parole** | Mode VAD 3 (ultra-agressif) refuse le signal brut USB sans traitement NoMachine | Passer au mode VAD **1** + détection hybride RMS calibrée dynamiquement |
| **Erreur Status 2 (arecord)** | Le paramètre `-d` (duration) a reçu une valeur décimale (ex: 5.0) | Toujours utiliser un nombre entier pour la durée (ex: `-d 5`) |
| **Haut-parleur JST muet** | Amplificateur matériel éteint — **PulseAudio ne l'active JAMAIS automatiquement** | `amixer -c 0 cset numid=3 on && numid=4 on && numid=5 60 && numid=6 60` |
| **Son sorti vers le Mac au lieu du HP** | NoMachine a capturé le Sink par défaut | `pactl set-default-sink SINK_RESPEAKER` + variable `PULSE_SINK` dans l'env Python |
| **`aplay -D plughw:0,0` → "Périphérique occupé"** | PulseAudio verrouille le matériel | Ne jamais utiliser `hw:` — toujours passer par PulseAudio (`paplay` ou `aplay` sans `-D`) |
| **`webrtcvad.Error: Error while processing frame`** | Frame stéréo (1920 octets) passée au VAD qui attend du mono (960 octets) | Extraire le canal gauche : `mono = b''.join([frame[i:i+2] for i in range(0, len(frame), 4)])` |
| **Faux positifs de détection (parole détectée sans parler)** | Seuil RMS fixe trop bas par rapport au bruit amplifié à 150% | Calibrer le seuil dynamiquement : `seuil = max(rms_fond × 3.0, 300)` |

---

## 4. Séquence de Démarrage Complète (Obligatoire)

Ces commandes sont intégrées dans `test_audio_loop.py` et dans `LocalTTS.__init__()`, mais peuvent être lancées manuellement pour déboguer.

```bash
# Variables
SOURCE="alsa_input.usb-Seeed_Studio_reSpeaker_XVF3800_4-Mic_Array_114993701260500251-00.iec958-stereo"
SINK="alsa_output.usb-Seeed_Studio_reSpeaker_XVF3800_4-Mic_Array_114993701260500251-00.iec958-stereo"

# ÉTAPE 1 : Désactiver la mise en veille automatique de PulseAudio
# module-suspend-on-idle re-suspend le micro quelques secondes après inactivité
# C'est la CAUSE RACINE du signal constant sans NoMachine
pactl unload-module module-suspend-on-idle

# ÉTAPE 2 : Sortir le micro de l'état SUSPENDED
pactl suspend-source "$SOURCE" 0
pactl set-source-mute "$SOURCE" false
pactl set-source-volume "$SOURCE" 150%   # 150% car sans NoMachine le gain est plus faible

# ÉTAPE 3 : Configurer le haut-parleur
pactl suspend-sink "$SINK" 0
pactl set-default-sink "$SINK"
pactl set-sink-mute "$SINK" false
pactl set-sink-volume "$SINK" 100%

# ÉTAPE 4 : Activer l'amplificateur JST (CRITIQUE — non géré par PulseAudio)
amixer -c 0 cset numid=3 on    # PCM Playback Switch Gauche
amixer -c 0 cset numid=4 on    # PCM Playback Switch Droit
amixer -c 0 cset numid=5 60    # PCM Playback Volume Gauche (0-100)
amixer -c 0 cset numid=6 60    # PCM Playback Volume Droit  (0-100)
```

> [!TIP]
> **Test rapide du haut-parleur** (après les étapes ci-dessus) :
> ```bash
> piper -m ~/.local/share/piper-voices/fr_FR-upmc-medium.onnx \
>   --output_file /tmp/test.wav <<< "Bonjour je suis le robot" \
>   && paplay /tmp/test.wav
> ```

---

## 5. Fix Permanent : Désactiver `module-suspend-on-idle` au Démarrage

Sans ce fix, il faut exécuter `pactl unload-module module-suspend-on-idle` à chaque redémarrage de PulseAudio.

```bash
# Créer un fichier de configuration PulseAudio qui supprime ce module au démarrage
sudo mkdir -p /etc/pulse/default.pa.d
sudo tee /etc/pulse/default.pa.d/no-suspend-on-idle.conf << 'EOF'
### Fix D-Bot : désactive la mise en veille automatique des périphériques audio
### Sans ce fix, le micro ReSpeaker reste en état SUSPENDED hors session NoMachine
### et retourne un signal constant (non réactif à la voix).
unload-module module-suspend-on-idle
EOF

# Redémarrer PulseAudio pour appliquer
pulseaudio -k && pulseaudio --start
```

---

## 6. Architecture Logicielle Validée (Pipeline Python)

### A. Détection des Périphériques
```python
import subprocess

def get_pulse_device_names():
    source, sink = None, None
    out = subprocess.check_output(["pactl", "list", "short", "sources"], text=True)
    for line in out.splitlines():
        if ("XVF3800" in line or "reSpeaker" in line) and "input" in line and ".monitor" not in line:
            source = line.split()[1]
    out = subprocess.check_output(["pactl", "list", "short", "sinks"], text=True)
    for line in out.splitlines():
        if "XVF3800" in line or "reSpeaker" in line:
            sink = line.split()[1]
    return source, sink
```

### B. Capture Audio — CRITIQUE : 2 canaux + extraction mono
```python
# Le ReSpeaker est déclaré stéréo (2ch). Capturer en mono provoque amplitude = 128.
cmd = ["parecord", f"--device={source_name}", "--format=s16le",
       "--channels=2",   # OBLIGATOIRE
       "--rate=16000", "--raw"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

FRAME_SIZE = 480  # 16000 Hz × 30ms
while True:
    frame_stereo = proc.stdout.read(FRAME_SIZE * 4)   # 4 octets = 2ch × 2 octets/sample
    # Extraction canal gauche pour le VAD (webrtcvad attend du mono)
    mono_frame = b''.join([frame_stereo[i:i+2] for i in range(0, len(frame_stereo), 4)])
    # Calcul RMS pour détection hybride
    import struct, math
    shorts = struct.unpack("<" + "h" * (len(mono_frame)//2), mono_frame)
    rms = math.sqrt(sum(s*s for s in shorts) / len(shorts))
    # Détection hybride : VAD (mode 1) OU seuil RMS calibré
    is_speech = vad.is_speech(mono_frame, 16000) or (rms > RMS_SPEECH_THRESHOLD)
```

### C. Calibration Dynamique (VAD + RMS)
```python
# Phase 1 : calibration VAD (2 secondes de silence)
noise_ratio = nb_frames_speech / nb_frames_total
trigger_ratio = min(noise_ratio + 0.10, 0.90)

# Phase 2 : calibration RMS (1 seconde de silence)
noise_rms = moyenne_rms_pendant_silence
RMS_SPEECH_THRESHOLD = max(noise_rms * 3.0, 300)
# → Exemple sans NoMachine : bruit = 626 RMS → seuil = 1878
# → La voix doit dépasser 1878 pour déclencher — mais comme le signal était FIGÉ,
#   il faut d'abord sortir la source du mode SUSPENDED (voir Section 4).
```

### D. TTS — Méthode Fichier Temporaire + paplay
```python
import tempfile, os, subprocess

def speak(text, voice_model_path, pulse_sink=None):
    env = os.environ.copy()
    if pulse_sink:
        env["PULSE_SINK"] = pulse_sink
        subprocess.run(["pactl", "set-sink-mute", pulse_sink, "false"], stderr=subprocess.DEVNULL)
        subprocess.run(["pactl", "set-sink-volume", pulse_sink, "100%"], stderr=subprocess.DEVNULL)
    # Fichier temporaire — évite les bugs de pipe Python avec Piper
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

## 7. Schéma du Pipeline Audio Complet

```
┌─────────────────────────────────────────────────────────────────┐
│                      CAPTURE (Entrée)                           │
│  4 micros PDM → XVF3800 DSP (Beamforming + NS + AEC)          │
│  → USB Audio IEC958 → PulseAudio Source (2ch, 16kHz)          │
│  → parecord --channels=2 → extraction canal gauche (mono)      │
│  → webrtcvad (mode 1) + seuil RMS calibré → déclenchement     │
│  → Faster-Whisper STT → texte                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    TRAITEMENT (Cerveau)                         │
│  Ollama LLM → réponse texte                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      SORTIE (Voix)                              │
│  Piper TTS → fichier .wav temporaire                           │
│  → paplay --device=SINK → PulseAudio Sink (avec PULSE_SINK)    │
│  → DAC interne XVF3800 → Ampli JST (numid=3,4,5,6 activés)    │
│  → Haut-parleur JST 5W                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Optimisation RAM (Jetson Orin Nano 8GB)

| Action | Commande |
| :--- | :--- |
| **Mode Headless** (libère ~1.5 Go) | `sudo systemctl isolate multi-user.target` |
| **Relancer l'interface graphique** | `sudo systemctl isolate graphical.target` |
| **Vérifier la RAM libre** | `free -m` |

---

## 10. Accélération GPU pour le STT (Whisper)

### Le Problème
Par défaut, la commande `pip install ctranslate2` sur Jetson (architecture ARM64) installe une version **CPU-only**. 
*   **Symptôme** : Message `⚠ [STT] Problème CUDA détecté : This CTranslate2 package was not compiled with CUDA support`.
*   **Impact** : Transcription 3 à 5 fois plus lente, forte charge CPU sur les cœurs Cortex-A78.

### La Solution : Compilation depuis les Sources
Pour exploiter le GPU de l'Orin Nano, il est impératif de compiler le moteur avec les flags NVIDIA.

#### 1. Configuration des chemins (Permanent)
Vérifiez que CUDA est dans votre environnement :
```bash
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

#### 2. Procédure de Compilation
```bash
cd ~/dbot
git clone --recursive https://github.com/OpenNMT/CTranslate2.git
cd CTranslate2
mkdir build && cd build

# CRITIQUE : Désactiver MKL (Intel) et activer CUDA/CUDNN
cmake -DWITH_CUDA=ON -DWITH_CUDNN=ON -DWITH_MKL=OFF -DOPENMP_RUNTIME=COMP ..

make -j$(nproc)
sudo make install
```

#### 3. Installation du module Python
```bash
cd ../python
pip install . --force-reinstall
```

### Liens de compatibilité (Si nécessaire)
Si `CTranslate2` cherche des versions plus anciennes de bibliothèques (ex: cherche v8 alors que JetPack 6 a la v9) :
```bash
sudo ln -sf /usr/lib/aarch64-linux-gnu/libcublas.so.12 /usr/lib/aarch64-linux-gnu/libcublas.so.11
sudo ln -sf /usr/lib/aarch64-linux-gnu/libcudnn.so.9 /usr/lib/aarch64-linux-gnu/libcudnn.so.8
```

---

## 11. Résumé des Fichiers Modifiés

| Fichier | Modification clé |
| :--- | :--- |
| `code/scripts/behaviors/test_audio_loop.py` | Script de test autonome : réveil complet, calibration dynamique, détection hybride. |
| `code/dbot/audio/tts.py` | `LocalTTS` : activation automatique ampli JST dans `__init__()`. |
| `code/dbot/audio/stt.py` | `LocalSTT` : gestion du fallback CPU si le GPU échoue. |
