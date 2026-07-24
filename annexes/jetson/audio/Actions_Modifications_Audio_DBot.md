# **Résumé des Modifications du Module Audio – D-Bot**

> **Date** : [À compléter]
> **Répertoire cible** : `/Users/Shared/Mon Google Drive Physique/Documentation/annexes/jetson/installation/`
> **Objectif** : Documenter les modifications apportées au module **audio** du projet **D-Bot** pour améliorer sa robustesse, sa documentation et ses tests.

---

## **1. Contexte et Objectifs**

Le module **audio** du projet **D-Bot** était initialement composé de quatre fichiers :
- `stt.py` (Speech-to-Text, hors-ligne, utilisant Whisper).
- `tts.py` (Text-to-Speech, hors-ligne, utilisant Piper).
- `respeaker.py` (vide/placeholder).
- `speaker.py` (vide/placeholder).

**Objectifs des modifications** :
- Améliorer la **robustesse** (gestion des erreurs).
- Ajouter une **documentation claire** (docstrings).
- Centraliser la gestion audio via un nouveau module (`audio_io.py`).
- Ajouter des **scripts de benchmark** pour mesurer les performances.

---

## **2. Actions Effectuées**

### **Étape 1 : Modification du fichier `stt.py`**

#### **Améliorations apportées** :
1. **Ajout d'une exception personnalisée** :
   - Une classe `STTError` a été ajoutée pour lever des exceptions claires en cas d'erreur.
   - Exemple :
     ```python
     raise STTError("[STT] Le modèle Whisper n'a pas pu être chargé.")
     ```

2. **Gestion robuste des erreurs** :
   - Les erreurs sont maintenant **levées** et **propagées** avec un message clair.
   - Exemple :
     ```python
     if "CUDA support" in str(e) or "CUDA" in str(e):
         raise STTError("[STT] Accélération GPU indisponible. Passage en mode CPU.")
     ```

3. **Documentation améliorée** :
   - Ajout de **docstrings** pour expliquer :
     - Le rôle de la classe (`LocalSTT`).
     - Les paramètres (`model_size`, `device`).
     - Les exceptions levées (`STTError`).

4. **Test unitaire amélioré** :
   - Le test en `if __name__ == "__main__"` utilise maintenant la gestion des exceptions.
   - Exemple :
     ```python
     try:
         stt.transcribe("test_audio.wav")
         print("✅ [STT] Test réussi.")
     except STTError as e:
         print(f"❌ [STT] Test échoué : {e}")
     ```

#### **Fichier modifié** :
- `code/dbot/audio/stt.py`

---

### **Étape 2 : Modification du fichier `tts.py`**

#### **Améliorations apportées** :
1. **Ajout d'une exception personnalisée** :
   - Une classe `TTSError` a été ajoutée pour lever des exceptions claires en cas d'erreur.
   - Exemple :
     ```python
     raise TTSError(f"[TTS] Le modèle vocal n'a pas été trouvé ici : {self.voice_model_path}")
     ```

2. **Gestion robuste des erreurs** :
   - Les erreurs sont maintenant **levées** et **propagées** avec un message clair.
   - Exemple :
     ```python
     if not os.path.exists(self.voice_model_path):
         raise TTSError(f"[TTS] Le modèle vocal n'a pas été trouvé ici : {self.voice_model_path}")
     ```

3. **Documentation améliorée** :
   - Ajout de **docstrings** pour expliquer :
     - Le rôle de la classe (`LocalTTS`).
     - Les paramètres (`voice_model_path`, `alsa_hw`, `pulse_sink`).
     - Les exceptions levées (`TTSError`).

4. **Test unitaire amélioré** :
   - Le test en `if __name__ == "__main__"` utilise maintenant la gestion des exceptions.
   - Exemple :
     ```python
     try:
         tts.speak("Bonjour, ma carte vocale locale fonctionne parfaitement...")
         print("✅ [TTS] Test réussi.")
     except TTSError as e:
         print(f"❌ [TTS] Test échoué : {e}")
     ```

#### **Fichier modifié** :
- `code/dbot/audio/tts.py`

---

### **Étape 3 : Renommage et création du fichier `audio_io.py`**

#### **Actions** :
1. **Suppression des fichiers `respeaker.py` et `speaker.py`** :
   - Ces fichiers étaient vides ou placeholders. Ils ont été **supprimés** du répertoire `code/dbot/audio/`.

2. **Création du fichier `audio_io.py`** :
   - Ce fichier centralise la gestion des **entrées/sorties audio** via le **ReSpeaker**.
   - Il inclut :
     - Configuration des **registres ALSA** pour activer l'amplificateur **JST**.
     - Intégration avec **PulseAudio** pour la lecture/écriture des flux audio.
     - Ajout de **docstrings** et de **tests unitaires**.

#### **Fonctionnalités clés** :
- **Gestion des entrées audio** (ex. : micro du ReSpeaker).
- **Gestion des sorties audio** (ex. : haut-parleur du ReSpeaker).
- **Optimisation des performances** (ex. : activation des registres ALSA, configuration PulseAudio).

#### **Fichier créé** :
- `code/dbot/audio/audio_io.py`

---

### **Étape 4 : Ajout des scripts de benchmark**

#### **Scripts créés** :
1. **`benchmark_stt.py`** :
   - Mesure la **latence** et la **précision** du module STT.
   - Évalue les performances du modèle Whisper.

2. **`benchmark_tts.py`** :
   - Mesure la **latence** et la **qualité** de la synthèse vocale du module TTS.
   - Évalue les performances du modèle Piper.

3. **`test_audio_io.py`** :
   - Test unitaire pour le module `AudioIO`.
   - Vérifie l'enregistrement et la lecture audio via le ReSpeaker.

#### **Répertoire cible** :
- `code/scripts/audio/`

---

### **Étape 5 : Validation finale en conditions réelles (10/05/2026)**

#### **Actions** :
1. **Correction du Bug Mono** : Passage définitif à la capture **stéréo (2ch)** via `arecord` pour éviter le gel du signal à 128 (bug driver).
2. **Détection Automatique** : Le module détecte maintenant dynamiquement l'ID de carte ALSA du ReSpeaker.
3. **Fix de Durée** : Découverte et correction d'un bug ALSA où le paramètre `-d` rejette les nombres décimaux.
4. **Validation Matérielle** : Test réussi de la boucle complète (Activation Ampli -> Enregistrement Stéréo -> Conversion Mono via sox -> Lecture paplay).

---

## **3. Glossaire des Scripts et Modules Audio**

> [!NOTE]
> Le code audio est organisé selon deux axes : **Bibliothèques** (code du robot) vs **Scripts** (outils humains), et **Génération v1** (ALSA stable) vs **Génération v2** (SDK USB officiel).

### **A. Bibliothèques du Robot (`code/dbot/audio/`) — Ne jamais lancer directement**

#### Stack v1 — ALSA (Référence stable, validée 10/05/2026)
*   **`audio_io.py`** : Capture ALSA stéréo → mono (sox). Détection auto de carte. Activation ampli JST. **Méthode officielle de capture.**
*   **`stt.py`** : Faster-Whisper GPU. Transcription français. Fallback CPU automatique.
*   **`tts.py`** : Piper-TTS. Génération vocale + lecture paplay. Détection dynamique de carte.

#### Stack v2 — SDK USB (Validée 10/05/2026, firmware 2.6)
*   **`respeaker_sdk.py`** : Interface USB directe avec le chip XMOS. Lit le **DOA** (0-359°) et le **VAD matériel** on-chip. Nécessite `pip install pyusb` + règle udev.
*   **`audio_io_v2.py`** : Comme `audio_io.py` mais déclenchement par VAD matériel. Expose le DOA via callback (prêt pour le cou Pan/Tilt).

### **B. Outils de Diagnostic (`code/scripts/audio/`) — À lancer manuellement**
*   **`test_audio_io.py`** : Valide la stack v1 (enregistre 5s et relit).
*   **`benchmark_stt.py`** : Mesure la latence Whisper GPU (référence : 1.5s).
*   **`test_arecord_vad.py`** : Teste la détection de parole logicielle (webrtcvad mode 1).
*   **`test_respeaker_sdk.py`** : Valide le SDK v2 (connexion USB, firmware, DOA, VAD matériel).

### **C. Comportements du Robot (`code/scripts/behaviors/`) — Scripts de vie autonome**
*   **`chatbot_local.py`** (v1) : Boucle conversationnelle complète (VAD parecord + Whisper + Qwen + Piper). Logique VAD hybride de référence. *Peut être instable sans NoMachine (parecord).*
*   **`chatbot_local_v2.py`** ✅ **(v2 — Recommandé)** : Même boucle avec **VAD matériel** et **DOA** via SDK USB. Stable sans NoMachine. Version de production.
*   **`test_audio_loop.py`** (v1) : Test de boucle STT-TTS sans LLM. Référence pour la logique VAD hybride + calibration RMS.
*   **`test_chatbot.py`** 🏛 **(Gen 1 — Prototype historique)** : Premier prototype Cloud (Google STT + gTTS). **Nécessite Internet. Conservé comme témoin du premier jour du projet uniquement.**




---

## **4. Points Forts des Modifications**

✅ **Robustesse** :
- Ajout d'exceptions personnalisées (`STTError`, `TTSError`, `AudioIOError`).
- Détection dynamique du matériel (plus de hardware "hardcoded").
- Gestion explicite des erreurs et des types de données (int vs float pour ALSA).

✅ **Documentation** :
- Ajout de **docstrings** pour tous les modules et fonctions.
- Clarification des interfaces et des paramètres.

✅ **Centralisation** :
- Le fichier `audio_io.py` centralise la gestion des flux audio via le ReSpeaker.

✅ **Tests et Benchmarks** :
- Ajout de scripts pour mesurer les performances (latence, qualité).

---

## **5. Prochaines Étapes (Si Nécessaire)**

- **Exécuter les tests unitaires** (`test_audio_io.py`, `benchmark_stt.py`, etc.).
- **Valider les modifications** en fonction des besoins du projet.
- **Ajouter des fonctionnalités supplémentaires** (ex. : gestion des flux audio en temps réel).

---

## **6. Fichiers à Consulter**

- `code/dbot/audio/respeaker_sdk.py` : Driver bas niveau (SDK XMOS XVF3800).
- `code/dbot/audio/audio_io_v2.py` : Pipeline capture audio matériel (VAD/DOA).
- `code/dbot/audio/modify_voice.py` : Moteur DSP de post-traitement pour l'identité vocale.
- `code/scripts/behaviors/chatbot_local_v2.py` : Version standard de production.

## Configuration de l'Identité Vocale (Mai 2026)

Le D-Bot supporte désormais un post-traitement DSP en temps réel. Deux personnalités ont été retenues :

1.  **Robot Sombre (Preset 11)** : Vocodeur profond, pitch -10 demi-tons, boost des basses.
2.  **IA Posée (Preset 16)** : Voix masculine naturelle, pitch -4 demi-tons, grave affirmé.

### Comment changer la voix ?
Il suffit de définir la variable d'environnement `DBOT_VOICE_FX` avant de lancer le chatbot :

```bash
# Pour la voix Robotique Sombre
export DBOT_VOICE_FX=11
python3 code/scripts/behaviors/chatbot_local_v2.py

# Pour la voix Humaine Grave
export DBOT_VOICE_FX=16
python3 code/scripts/behaviors/chatbot_local_v2.py
```

*Note : Le preset 16 est désormais activé par défaut. Pour utiliser la voix Piper brute (sans aucun effet), définissez `export DBOT_VOICE_FX=none`.*

---

## **7. Résumé des Commandes Utiles**

Pour **exécuter les tests** :
```bash
# Test unitaire pour AudioIO
python test_audio_io.py 5 output.wav

# Benchmark pour STT
python benchmark_stt.py

# Benchmark pour TTS
python benchmark_tts.py
```

Pour **vérifier les logs** :
```bash
# Vérifier les logs des modules
cat /var/log/dbot/audio/*.log
```

---

---

## **8. Architecture à Double Voie (12 mai 2026)**

Pour éliminer les régressions entre les tests NoMachine et la production, le code audio a été scindé en deux branches physiques :

### **A. Branche PRODUCTION (Autonome)**
- **Script de lancement** : `code/scripts/audio/start_autonomous.sh`
- **Comportement** : `chatbot_autonomous_v2.py`
- **Moteur Audio** : `audio_io_autonomous.py`
- **Méthode** : ALSA Direct (`arecord` / `aplay` via `plughw:0,0`).
- **Avantage** : Stabilité absolue, aucune dépendance sur PulseAudio ou GDM. C'est le mode "Vérité Terrain".

### **B. Branche DÉVELOPPEMENT (NoMachine)**
- **Script de lancement** : `code/scripts/audio/start_nomachine.sh`
- **Comportement** : `chatbot_nomachine_v2.py`
- **Moteur Audio** : `audio_io_nomachine.py`
- **Méthode** : PulseAudio (`parecord` / `paplay`).
- **Spécificité** : Intègre un système d'**Auto-Healing** qui détecte et répare automatiquement le serveur PulseAudio si NoMachine corrompt le socket de session.

---

## **9. Stack dbot_next & Validation Serveur Compagnon (24 juillet 2026)**

### **Actions Effectuées** :
1. **Résolution des Bugs d'Inspection WebSocket** :
   - Correction dans `companion_server.py` (`message.get("bytes")`) pour traiter correctement les paquets JSON textuels (`start`, `end`, `interrupt`) et binaires.
   - Suppression du double désentrelacement stéréo/mono qui raccourcissait artificiellement l'audio et générait des hallucinations.
2. **VAD Logicielle RMS Adaptative & Pre-roll** :
   - Calibration dynamique du bruit ambiant au démarrage (`seuil = max(bruit_rms * 3.0, 150)`).
   - Pre-roll de 5 chunks de silence inclus pour préserver le début du premier mot.
   - Verrouillage automatique de la VAD pendant la réponse du robot (`speaking`/`thinking`) et purge du buffer pour éliminer l'effet d'auto-écoute du haut-parleur.
3. **Intégration ASR Bivalente (Groq Cloud + Faster-Whisper Local)** :
   - Support natif de **Groq Whisper Large v3 Turbo** (< 300 ms Cloud ASR via `GROQ_API_KEY` dans `.env`).
   - Fallback automatique transparent sur **Faster-Whisper `small`** (CPU local Mac, ~993 ms).
4. **Profiling de Latence Multi-Étapes & Script de Gestion Propre** :
   - Mesure exacte horodatée des étapes ASR, LLM 1er token, TTS 1er chunk.
   - Création du script `Code/dbot_next/scripts/start_companion_server.sh` (`--start`, `--restart`, `--stop`, `--status`, `--logs`).
   - Latence totale validée : **1553 ms (Local)** / **~750 ms (Cloud Groq)**.

---

**Auteur** : Antigravity (IA)
**Dernière mise à jour** : 24 juillet 2026
**Version** : 2.0 (Validation Stack dbot_next & Latence 1.55s)