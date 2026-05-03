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

## **3. Structure Finale du Module Audio**

```
code/dbot/audio/
├── stt.py          (STT avec gestion d'erreur et docstrings)
├── tts.py          (TTS avec gestion d'erreur et docstrings)
└── audio_io.py     (Module central pour l'audio, remplace respeaker.py/speaker.py)

code/scripts/audio/
├── benchmark_stt.py   (Benchmark pour STT)
├── benchmark_tts.py   (Benchmark pour TTS)
└── test_audio_io.py   (Test unitaire pour AudioIO)
```

---

## **4. Points Forts des Modifications**

✅ **Robustesse** :
- Ajout d'exceptions personnalisées (`STTError`, `TTSError`, `AudioIOError`).
- Gestion explicite des erreurs (ex. : modèle non trouvé, activation ALSA).

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

- `code/dbot/audio/stt.py`
- `code/dbot/audio/tts.py`
- `code/dbot/audio/audio_io.py`
- `code/scripts/audio/benchmark_stt.py`
- `code/scripts/audio/benchmark_tts.py`
- `code/scripts/audio/test_audio_io.py`

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

**Auteur** : [Assistant IA]
**Date** : [À compléter]
**Version** : 1.0