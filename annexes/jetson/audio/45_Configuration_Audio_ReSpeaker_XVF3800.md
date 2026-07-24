# 45 - Guide de Configuration Audio : ReSpeaker XVF3800 sur Jetson Orin Nano

> **Document de référence — Validé Avril 2026**
> Ce guide est auto-suffisant. Si un problème survient, pointez un assistant IA vers ce fichier pour qu'il dispose de tout le contexte nécessaire sans historique de conversation.

---

## 1. Architecture Matérielle

| Composant | Connexion | Remarque |
| :--- | :--- | :--- |
| **ReSpeaker XVF3800** | Port **USB-A (USB 3.2 Gen 2)** de la Jetson | NE PAS utiliser le port USB-C (instabilités d'alimentation/transmission). Note : Les ports USB-A physiques du kit Jetson sont noirs mais supportent l'USB 3.2 Gen 2. |
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
> **NoMachine modifie profondément l'état de PulseAudio.** Il crée une "bulle virtuelle" qui intercepte l'audio. L'architecture a été scindée en double voie (Autonome vs NoMachine) pour gérer ce comportement.

### A. Le Piège de la Bulle Virtuelle NoMachine (Découverte Mai 2026)
Quand NoMachine est actif, il modifie la variable d'environnement `PULSE_SERVER` du terminal (ex: `PULSE_SERVER=~/.nx/devices/.../native.socket`).
*   **Conséquence** : Les commandes PulseAudio (`pactl`, `parecord`, `paplay`) se connectent au serveur virtuel de NoMachine, qui **masque totalement les cartes matérielles physiques ALSA** (`XVF3800` est introuvable). L'audio est entièrement déporté vers le client distant (Mac/PC).
*   **Solution (Auto-Healing)** : Le module `audio_io_nomachine.py` exécute `del os.environ["PULSE_SERVER"]`. Cela détruit la bulle NoMachine pour le processus Python en cours, forçant la reconnexion au vrai serveur physique PulseAudio de la Jetson.

### B. Le Danger de `graphical.target`
> [!CAUTION]
> Ne jamais utiliser `sudo systemctl isolate graphical.target` dans un script de lancement NoMachine (ex: `start_nomachine.sh`). Cela redémarre GDM, ce qui tue le serveur PulseAudio en cours, verrouille la carte son ALSA et corrompt définitivement la session NoMachine active.

### C. Sans NoMachine (Production / Robot Autonome)
| Élément | État |
| :--- | :--- |
| **Méthode** | Utilisation exclusive de **ALSA Direct** (`audio_io_autonomous.py`) |
| **Microphone** | `arecord -D plughw:0,0` |
| **Haut-parleur** | `aplay -D plughw:0,0` |
| **Avantage** | Bypasse PulseAudio et GDM, stabilité absolue en condition Headless (`multi-user.target`). |

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
| **`arecord -D plughw:X,0` → exit status 2 (device busy)** | PulseAudio verrouille exclusivement le device ALSA quand NoMachine est absent | Utiliser `parecord` à la place (passe par PulseAudio) |
| **`parecord` enregistre un fichier vide (0.09s de transcription)** | `parecord` n'a pas d'option `-d` pour la durée — elle est ignorée silencieusement | Utiliser `timeout N parecord ...` pour limiter la durée |
| **Source réveillée = "monitor" au lieu du micro** | La détection par mot-clé `iec958` matchait aussi `alsa_output...iec958.monitor` | Exclure les sources se terminant par `.monitor` dans la détection |
| **`aplay/arecord` → "Device busy" + `pactl` vide** | L'utilisateur **`gdm`** (GNOME) a verrouillé la carte au démarrage | `sudo systemctl isolate multi-user.target` pour libérer le matériel |
| **`arecord` → "Périphérique occupé" même après `pulseaudio -k`** | GDM tourne **son propre** PulseAudio (user `gdm`, distinct du user `david`). `pulseaudio -k` ne tue que l'instance `david`. Vérifier avec `ps aux \| grep pulse` et `cat /proc/asound/card0/pcm0c/sub0/status` → `owner_pid` appartient à `gdm`. | `sudo kill -9 <PID_gdm_pulse>` puis vérifier que l'`owner_pid` est passé au PID de david. Après ça, utiliser `parecord` (plus d'`arecord`). **Fix permanent :** `sudo systemctl set-default multi-user.target` (headless au reboot). |
| **`Vol Max: 0` dans Python même si `arecord` tourne sans erreur** | PulseAudio (GDM ou user) capture le device ALSA en exclusivité. `arecord -D plughw:` reçoit un accès partagé mais le flux est rempli de zéros (le vrai flux est côté PA). | Utiliser `parecord --device=<SOURCE>` via PulseAudio. S'assurer d'abord que `pactl list short sources` montre la source ReSpeaker (et non seulement `auto_null.monitor`). |
| **Source micro SUSPENDED sans NoMachine malgré le fix `/etc/pulse/default.pa.d/`** | Sur Ubuntu 20.04 Jetson, les fichiers `.d/` sont lus **avant** `default.pa` — `unload-module` n'a aucun effet | Commenter directement la ligne dans `default.pa` : `sudo sed -i 's/^load-module module-suspend-on-idle/### DBOT FIX.../'` |
| **Silence total sous NoMachine (Lecture/Capture inopérantes)** | La "bulle NoMachine" (socket NX via `PULSE_SERVER`) masque les périphériques matériels PulseAudio. | Supprimer la variable avant exécution : `del os.environ["PULSE_SERVER"]`. |

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

> [!CAUTION]
> **Sur Jetson (Ubuntu 20.04)**, les fichiers dans `default.pa.d/` sont traités **avant** `default.pa`. Un `unload-module` dans un fichier `.d/` n'a aucun effet car le module est rechargé ensuite par `default.pa`. 
> **La méthode correcte est de commenter directement la ligne dans `default.pa`.**

```bash
# Commenter la ligne incriminée dans le fichier principal PulseAudio
sudo sed -i 's/^load-module module-suspend-on-idle/### DBOT FIX: load-module module-suspend-on-idle/' /etc/pulse/default.pa

# Vérifier que la modification est correcte (doit afficher la ligne commentée)
grep "suspend-on-idle" /etc/pulse/default.pa

# Redémarrer PulseAudio pour appliquer
pulseaudio -k && pulseaudio --start

# Vérifier que le module est bien absent (doit retourner vide)
pactl list modules short | grep suspend
```

---

## 6. Architecture Logicielle Officielle (Pipeline Python)

> [!IMPORTANT]
> **VÉRITÉ TERRAIN (Juillet 2026 — dbot_next) :** Le comportement dépend de qui détient le device ALSA.
> - Si **PulseAudio (user `david`) détient le device** (cas normal en session graphique ou SSH après tuer le PulseAudio GDM) : utiliser **`parecord --device=<SOURCE>`**. C'est la méthode fiable.
> - Si **personne ne détient le device** (mode Headless `multi-user.target` sans PulseAudio) : utiliser **`arecord -D plughw:X,0`**.
> - **Ne JAMAIS tenter `arecord` quand PulseAudio tourne** — il recevra un flux de zéros (device busy silencieux).

### A. Détection Dynamique du Périphérique
```python
def detect_respeaker_card():
    """Détection insensible à la casse — supporte 'reSpeaker', 'Seeed', 'XVF3800'."""
    try:
        out = subprocess.check_output(["arecord", "-l"], text=True)
        for line in out.splitlines():
            line_lower = line.lower()
            if "respeaker" in line_lower or "xvf3800" in line_lower or "seeed" in line_lower:
                if "carte" in line_lower:
                    return line.split("carte ")[1].split(":")[0].strip()
                elif "card" in line_lower:
                    return line.split("card ")[1].split(":")[0].strip()
    except Exception:
        return "0"  # Fallback
```

> [!WARNING]
> La détection **doit être insensible à la casse** et inclure le mot-clé `"seeed"`. Le nom PulseAudio réel du device est `alsa_input.usb-Seeed_Studio_reSpeaker_XVF3800...iec958-stereo`. Si on ne cherche que `"reSpeaker"` (casse exacte), la détection peut rater selon la version du firmware ou la locale système.

### B. Capture Audio (dbot_next) — `parecord` via PulseAudio
```python
# Règle : si PulseAudio tourne ET détient le device → parecord
# Sinon (headless sans PA) → arecord
cmd = ["parecord", f"--device={source_name}", "--format=s16le", "--channels=2",
       f"--rate={sample_rate}", "--raw"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
```

### C. Capture Audio (dbot legacy) — ALSA Direct + Stéréo
```python
# OBLIGATOIRE : Capturer en 2 canaux (stéréo) pour éviter le gel du signal à 128.
# Utiliser arecord uniquement quand PulseAudio ne tourne PAS.
d = int(duration)
cmd = f"arecord -D plughw:{card_id},0 -f S16_LE -r 16000 -c 2 -d {d} | sox -t wav - -c 1 {output_file}"
subprocess.run(cmd, shell=True, check=True)
```

### C. Détection de Voix (VAD)
Utiliser `webrtcvad` en mode **1** pour plus de robustesse aux bruits ambiants de la Jetson.
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

## 9. Stack dbot_next — `AudioIOStreaming` (Streaming Non-Bloquant)

> [!IMPORTANT]
> **Valide Juillet 2026.** `AudioIOStreaming` (`code/dbot_next/audio/audio_io_streaming.py`) est le composant de capture audio de la stack `dbot_next`. Il remplace le modèle de capture par fichier temporaire de la stack `dbot`.

### Architecture
- **Détection automatique** : cherche le ReSpeaker via `pactl list short sources` (filtre : `respeaker`, `xvf3800`, `seeed` — insensible à la casse).
- **Priorité `parecord`** : si une source PulseAudio est trouvée → `parecord --device=<source>` (streaming non-bloquant vers une queue Python thread-safe).
- **Repli `arecord`** : si PulseAudio ne voit pas le device → `arecord -D plughw:X,0` (mode headless `multi-user.target`).
- **Anti-bulle NoMachine** : `os.environ.pop("PULSE_SERVER", None)` est appelé dans `__init__` pour forcer la connexion au vrai serveur PulseAudio local (et non au socket virtuel NoMachine).
- **Nettoyage robuste** : `stop_capture()` envoie SIGTERM puis SIGKILL (timeout 2s) pour garantir qu'aucun `arecord`/`parecord` ne reste orphelin après un `Ctrl+C`.

### Pipeline Streaming Complet (dbot_next)
```
┌─────────────────────────────────────────────────────────────────┐
│ JETSON ORIN NANO (Client Streaming)                             │
│  parecord --device=SOURCE --channels=2 --format=s16le           │
│  → AudioIOStreaming (mono gauche extrait direct @ 16 kHz)       │
│  → VAD logicielle RMS (seuil calibré 150 RMS min + pre-roll)    │
│  → Verrouillage anti-auto-écoute pendant paplay                │
│  → WebSocket (chunks PCM base64) ─────────────────────────┐     │
└───────────────────────────────────────────────────────────│─────┘
                                                            │
┌───────────────────────────────────────────────────────────│─────┐
│ MAC COMPAGNON (companion_server.py via script start)      │     │
│  → Groq Whisper Large v3 Turbo (< 300 ms Cloud ASR)       │←────┘
│    ou Faster-Whisper small CPU (~900 ms local fallback)         │
│  → Gemini 2.0 Flash LLM Streaming (Cloud, ~0 ms 1er token)      │
│  → Qwen3-TTS MLX (GPU Metal 24 kHz, ~0 ms 1er chunk)           │
│  └─ WebSocket (réponse audio PCM base64 + texte) ─────────┐     │
└───────────────────────────────────────────────────────────│─────┘
                                                            │
┌───────────────────────────────────────────────────────────│─────┐
│ JETSON (Lecture Audio) ───────────────────────────────────│←────┘
│  PCM 24kHz → paplay --device=SINK_RESPEAKER                     │
│  → DAC XVF3800 → Ampli JST (numid=3,4,5,6) → HP 5W              │
└─────────────────────────────────────────────────────────────────┘
```

### Séquence de Démarrage Recommandée (dbot_next)

```bash
# 1. Sur le Mac : Démarrage/Restart propre du serveur via le gestionnaire
./Code/dbot_next/scripts/start_companion_server.sh --restart

# Pour vérifier le statut ou suivre les logs :
./Code/dbot_next/scripts/start_companion_server.sh --status
./Code/dbot_next/scripts/start_companion_server.sh --logs

# 2. Sur la Jetson : Lancement de la boucle de test conversationnelle
git pull
export DBOT_MAC_IP="192.168.68.120"
python3 code/dbot_next/scripts/test_companion_streaming.py
```

### Métriques de Latence Perçue (Validées Juillet 2026)
- **VAD Fin de phrase** : `1600 ms` (10 chunks × 160 ms)
- **ASR Groq Cloud Turbo** : `~200 ms` (ou Faster-Whisper `small` CPU local : `993 ms`)
- **LLM Gemini 2.0 Flash** : `0 ms` (streaming premier token instantané)
- **TTS Qwen3-TTS GPU Metal** : `0 ms` (streaming premier chunk instantané)
- 🚀 **Latence Totale Perçue** : **1553 ms (Local)** / **~750 ms (Groq Cloud)**

### Commande de Diagnostic Volume (IMPORTANT : utiliser LANG=C)
```bash
# La locale française traduit la sortie de sox !
# "Maximum amplitude" devient "Amplitude maximum" → grep -E "Maximum|RMS" ne trouve rien.
# TOUJOURS utiliser LANG=C pour les tests de diagnostic sox :
SOURCE="alsa_input.usb-Seeed_Studio_reSpeaker_XVF3800_4-Mic_Array_114993701260500251-00.iec958-stereo"
pactl suspend-source "$SOURCE" 0 && pactl set-source-volume "$SOURCE" 150%
timeout 3 parecord --device="$SOURCE" --channels=2 --format=s16le --rate=16000 --raw > /tmp/raw_capture.raw
echo "Taille: $(wc -c < /tmp/raw_capture.raw) octets"  # doit être ~192000 pour 3s
LANG=C sox -t raw -r 16000 -e signed -b 16 -c 2 /tmp/raw_capture.raw -n stat 2>&1
```

---

| Action | Commande |
| :--- | :--- |
| **Mode Headless** (Libère ~1.5 Go + Audio GDM) | `sudo systemctl isolate multi-user.target` |
| **Purger le cache RAM** (avant lancement) | `sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches` |
| **Vérifier la RAM libre** | `free -m` |
| **Surveiller CPU/GPU/RAM** | `tegrastats` ou `jtop` |
| **Alléger le STT** (si OOM persiste) | Passer `model_size="tiny"` dans `LocalSTT` |
| **Forcer STT sur CPU/GPU** | `DBOT_STT_DEVICE=cpu` ou `cuda` |

> [!TIP]
> **Recommandation D-Bot (Orin Nano 8GB)** : Utilisez `DBOT_STT_DEVICE=cpu` (défaut). Cela laisse 100% du GPU libre pour Ollama, ce qui permet d'utiliser des modèles de 3B ou 4B sans aucun crash. La transcription sur CPU est instantanée grâce aux 6 cœurs ARM.

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
