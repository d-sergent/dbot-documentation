# 09. Intelligence Conversationnelle (Architecture Hybride Cloud/Edge)

*Dernière mise à jour : 12 Mai 2026*

Ce document détaille l'intégration de la boucle conversationnelle de D-Bot, basée sur une architecture **Hybride** : une intelligence Cloud ultra-rapide en priorité (Gemini), avec une autonomie locale totale en secours (Ollama). Cette approche permet de libérer la RAM de la **NVIDIA Jetson Orin Nano** pour les tâches de marche et de vision.

---

## 1. Architecture Logicielle "Cerveau Déporté"

Pour atteindre une latence de réponse quasi-instantanée (< 1 seconde) tout en conservant une intelligence de haut niveau, l'architecture suivante est utilisée :

1. **Écoute et VAD Matériel (ReSpeaker XVF3800)** :
   Le traitement de la voix (réduction de bruit, annulation d'écho) est fait sur le VPU du ReSpeaker. Le signal propre est détecté par le script `code/dbot/audio/audio_io_v2.py`.
2. **Speech-to-Text (STT) - Les Oreilles** :
   **Faster-Whisper (modèle "small")** sur **CUDA**. Grâce au gain de RAM permis par le cloud, nous utilisons le modèle `small` qui offre une précision bien supérieure au modèle `tiny`. Latence : ~1.2s.
3. **Large Language Model (LLM) - Le Cerveau** :
   *   **Primaire (Cloud)** : **Google Gemini 3.1 Flash Lite**. Choisi pour sa latence record et sa gratuité. Géré par `code/dbot/brain/llm_client.py`.
   *   **Secours (Local)** : **Ollama + Qwen2.5:0.5b**. Si le WiFi est coupé, le robot bascule sur ce modèle ultra-léger pour rester capable de répondre.
4. **Text-to-Speech (TTS) - La Bouche** :
   **Piper-TTS** (voix `fr_FR-siwis-medium.onnx`). Synthèse vocale neuronale ultra-rapide (< 100ms).

---

## 2. Défis Résolus et Optimisations (Jetson Orin Nano)

### A. Le Conflit Audio GDM (Headless)
**Problème** : En mode autonome (SSH), le micro ReSpeaker était souvent "occupé" ou invisible.
**Cause** : L'interface graphique Ubuntu (GDM) verrouille les périphériques audio au démarrage, même si personne n'est connecté.
**Solution** : Désactivation de GDM via `sudo systemctl isolate multi-user.target`. Cela libère à la fois le matériel audio et **1.5 Go de RAM**.

### B. Optimisation de la Latence Cloud
**Problème** : Les modèles gratuits d'OpenRouter (ex: Nemotron 120B) présentaient des latences de 4 à 8 secondes.
**Solution** : Utilisation de l'**API Native Gemini** avec le modèle **3.1 Flash Lite**. La réponse arrive en moins de 500ms, permettant une conversation fluide et naturelle.

---

## 3. Capacité d'Action (Function Calling)

D-Bot utilise le **Function Calling natif** de Gemini pour interagir avec son environnement :
*   **Web Search** : Le robot peut décider de chercher sur internet via DuckDuckGo s'il ne connaît pas une information récente.
*   **Perception Spatiale** : (En cours) Capacité à demander une analyse visuelle via l'OAK-D pour identifier son interlocuteur.

---

## 4. Mode d'Emploi (Démarrage Automatisé)

Plus besoin de lancer plusieurs terminaux. Tout est automatisé via des scripts robustes :

**1. Mode Autonome (Le robot en liberté)**
Ce script coupe l'interface graphique, optimise la RAM, configure l'audio et lance l'IA :
```bash
./code/scripts/audio/start_autonomous.sh
```

**2. Mode Développement (Avec écran NoMachine)**
Pour travailler sur le code tout en ayant le retour visuel de la caméra :
```bash
./code/scripts/audio/start_nomachine.sh
```

---

## 5. Fichiers Sources de Référence
*   `code/dbot/brain/llm_client.py` : Logique hybride Gemini/Ollama.
*   `code/dbot/audio/stt.py` : Transcription Faster-Whisper sur CUDA.
*   `code/scripts/behaviors/chatbot_local_v2.py` : Script principal de la boucle conversationnelle.
