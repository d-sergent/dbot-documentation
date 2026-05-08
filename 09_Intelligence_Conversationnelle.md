# 09. Intelligence Conversationnelle (100% Locale)

*Dernière mise à jour : 20 Avril 2026*

Ce document détaille l'intégration d'une boucle conversationnelle autonome (sans API Cloud) sur le robot D-Bot, alimentée par son ordinateur de bord : la **NVIDIA Jetson Orin Nano Super 8Go**. La contrainte principale était de faire rentrer trois modèles d'Intelligence Artificielle de pointe (STT, LLM, TTS) dans un budget strict de 8 Go de RAM unifiée.

---

## 1. Architecture Logicielle et Choix Technologiques

Pour atteindre une latence de réponse humaine (3 à 6 secondes) sans l'aide du Cloud, l'architecture suivante a été sélectionnée après plusieurs essais :

1. **Écoute Automatique (VAD)** :
   La librairie standard `SpeechRecognition` scanne le bruit ambiant. Lorsqu'elle détecte une voix humaine (Voice Activity Detection), elle ouvre un flux micro, enregistre la phrase jusqu'au prochain silence, et l'envoie au STT.
2. **Speech-to-Text (STT) - Les Oreilles** :
   **Faster-Whisper (modèle "small")**. Retranscrit l'audio en texte français.
3. **Large Language Model (LLM) - Le Cerveau** :
   **Ollama + Qwen2.5:3B**. Le modèle quantizé d'Alibaba (Qwen) à 3 Milliards de paramètres offre actuellement le meilleur rapport Qualité du Français / Vitesse / Consommation RAM. Le client `code/dbot/brain/llm_client.py` lui injecte un "Prompt Système" strict pour qu'il garde sa personnalité de D-Bot et fasse des réponses courtes de 2 ou 3 lignes.
4. **Text-to-Speech (TTS) - La Bouche** :
   **Piper-TTS** (avec la voix `fr_FR-upmc-medium.onnx`). Ce moteur VITS nécessite moins de 100 Mo de RAM et parle presque instantanément sur architecture ARM64. Le flux généré est envoyé en RAW directement dans l'amplificateur matériel du robot.

---

## 2. Les Défis (et leurs Solutions)

Bâtir une IA locale sur les 8 Go d'une Jetson comporte quelques pièges majeurs rencontrés lors du développement :

### A. Le Problème du "Micro Muet" (Hardware)
**Problème** : Le micro du ReSpeaker XVF-3800 enregistrait toujours un "silence absolu" sous Linux (malgré des LEDs réactives au bruit) via `arecord`, ce qui bloquait indéfiniment la fonction `.listen()` du VAD.
**Solution** : Le port **USB-C** de la Jetson Orin Nano (destiné au mode Recovery) a un bug matériel connu avec les flux Audio entrants isochrones. La puce ne transmet que des Zéros. **Il faut toujours brancher le microphone matériel sur le port **USB-A (bleu)** à l'arrière.**

### B. Le Crash "Error 500 : Llama runner terminated"
**Problème** : Lors du chargement du modèle `Qwen2.5:3b`, Ollama s'arrêtait immédiatement en balançant une erreur de serveur 500, un Go Panic, ou une impossibilité d'allouer un buffer CUDA0.
**Cause** : Le modèle de 1,9 Go essayait d'allouer un énorme bloc dans la mémoire unifiée CUDA de la Jetson. Or, le bureau `NoMachine`, l'interface `GNOME` d'Ubuntu et d'autres outils fragmentaient déjà 5 à 6 Go des 8 Go totaux.
**Solution** :
1. Fermeture complète de l'application NoMachine (qui utilise énormément la VRAM/RAM).
2. Forçage du mode "Terminal/Console pure" (tue le processeur d'interface graphique) : `sudo systemctl isolate multi-user.target` *(Note : pour réactiver le bureau plus tard, utilisez la commande inverse `sudo systemctl isolate graphical.target`)*.
3. Purge des caches Linux : `sudo sysctl -w vm.drop_caches=3`.
4. Ajout vital d'un espace **SWAP (fichier d'échange) de 10 Go** sur le SSD NVMe (`sudo fallocate -l 10G /swapfile ...`). Ce fichier permet à Ubuntu de déporter temporairement les processus inutiles sur le disque pour libérer un grand bloc complet de RAM physique pour CUDA.
5. Activation du profil de performance maximale de la Jetson : `sudo nvpmodel -m 0`.

### C. L'incompatibilité de CTranslate2 (Erreur CUDA STT)
**Problème** : Au lancement du code Python pour `faster-whisper`, la console crachait : `This CTranslate2 package was not compiled with CUDA support`.
**Cause** : Le raccourci `pip install faster-whisper` télécharge un paquet standard prévu pour processeurs ARM génériques, il n'incorpore pas les particularités matérielles de la série NVIDIA Jetson. Recompiler manuellement le support CUDA prenait des heures.
**Solution** : Création d'un système de *Fallback* intelligent dans le code (`code/dbot/audio/stt.py`). Face à l'erreur CUDA, D-Bot abandonne le GPU et charge son oreille sur le **CPU (Cortex-A78)** exclusif de la Jetson, avec une quantification matérielle `int8`. Le résultat : le STT reste ultra-rapide (1 à 2 sec) tout en libérant miraculeusement la puce graphique de sa charge, permettant au "Cerveau" (Ollama) de prendre tout le relai !

---

## 3. La Boucle Interactive Finale

L'assemblage a culminé dans un unique script : `code/scripts/behaviors/chatbot_local.py`.

Le cycle est le suivant :
1. **Écoute Active** : Le robot est silencieux et guette.
2. L'humain parle -> **Capture WAV temp**
3. **STT (CPU)** transcrit l'audio.
4. L'humain arrête de parler -> **LLM (GPU)** analyse le texte.
5. Le LLM répond -> **TTS (CPU)** synthétise l'onde.
6. Transmission directe à ALSA (ampli matériel i2s) -> **ReSpeaker JST Speaker**.
7. Le système efface les anciens messages de la mémoire (pour rester léger) et recommence à guetter.

**Validation Finale** : Le système fonctionne avec le module WiFi éteint (mode avion), ce qui prouve l'intégrale autonomisation de la réflexion du D-Bot.

---

## 4. Augmentation Cognitive (Tool Use / Function Calling)

Bien que le robot soit conçu pour fonctionner 100% hors-ligne, une capacité matérielle avancée de *"Function Calling"* a été intégrée à son Cerveau (`llm_client.py`) pour lui permettre d'interagir avec le monde extérieur (ex: Internet) de manière autonome.

### Le Principe
Le modèle `Qwen2.5:3B` est entraîné pour l'utilisation d'outils. Si un humain lui pose une question sur un événement récent qu'il ignore :
1. Le LLM évalue scrupuleusement ses propres connaissances. S'il n'est pas sûr, il refuse d'halluciner la réponse.
2. Il génère un ordre JSON système demandant l'utilisation formelle de l'outil `search_web` sur certains mots clés.
3. Notre code Python intercepte cet ordre, met la voix en pause, et exécute en sous-marin une recherche via la librairie légère `ddgs` (DuckDuckGo).
4. Python extrait les résumés des 2 premiers articles et les glisse discrètement dans la "mémoire court terme" du robot.
5. L'IA lit ces faits objectifs ultra-récents et formule finalement sa réponse à voix haute.

**Bénéfice Architectural** : Cette intégration de DuckDuckGo sert de "Preuve de Concept" (Proof of Concept). Puisque le cerveau LLM sait désormais invoquer des fonctions Python locales, il pourra dans le futur utiliser de la même manière des outils physiques comme `lever_bras_gauche()` ou `evaluer_batterie()`.

---

## 5. Mode d'Emploi (Démarrage Rapide)

Si vous venez de démarrer la Jetson, voici la procédure stricte pour réveiller le robot :

**1. Libérer la RAM (Crucial)**
Fermez les interfaces graphiques gourmandes :
```bash
sudo systemctl isolate multi-user.target
sudo sysctl -w vm.drop_caches=3
```

**2. Allumer le Cerveau (Ollama)**
Dans un premier terminal, lancez le serveur IA en tâche de fond :
```bash
ollama serve
```

**3. Lancer la Boucle d'Écoute**
Dans un second terminal, exécutez le script principal :
```bash
cd ~/dbot
python3 code/scripts/behaviors/chatbot_local.py
```
*(Patientez le temps du chargement des modèles, puis parlez au robot dès l'apparition du message `Je vous écoute...`).*
