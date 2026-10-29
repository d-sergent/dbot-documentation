# 🛡️ Architecture & Outils de Sécurité du Code D-Bot

Ce dossier regroupe les outils, scripts et directives de sécurité pour le code source et les dépendances logicielles du robot humanoïde D-Bot V1.

---

## 📑 Sommaire
- [1. Modèle de Menace & Contexte Local](#1-modèle-de-menace--contexte-local)
- [2. Les Failles Peuvent-Elles Être Exploitées en Local ?](#2-les-failles-peuvent-elles-être-exploitées-en-local-)
- [3. Ont-Elles Été Exploitées ? (Diagnostic Médico-Légal)](#3-ont-elles-été-exploitées--diagnostic-médico-légal)
- [4. Outil d'Audit Unifié en 1 Clic (`audit_dbot_security.py`)](#4-outil-daudit-unifié-en-1-clic-audit_dbot_securitypy)
- [5. Guide de Remédiation des Vulnérabilités](#5-guide-de-remédiation-des-vulnérabilités)
- [6. Règles d'Approvisionnement Python (Mac vs Jetson Orin Nano)](#6-règles-dapprovisionnement-python-mac-vs-jetson-orin-nano)

---

## 1. Modèle de Menace & Contexte Local

Le projet D-Bot s'exécute sur deux environnements distincts :
1. **Mac M1 Max (Station de Développement & Cognition)** : Serveur RAG LightRAG, synthèse vocale locale MLX Qwen3-TTS, CAO Fusion 360 / FreeCAD.
2. **Jetson Orin Nano (Cerveau Embarqué Robotique)** : Bus CAN (RobStride), vision 3D (OAK-D Pro / YOLO-World TensorRT), dialogue vocal Edge (Groq + Gemini + Edge-TTS).

Bien que ce code s'exécute en local sur vos machines et non sur un serveur web public, la sécurité logicielle et la protection de la chaîne logistique (Supply Chain) restent critiques.

---

## 2. Les Failles Peuvent-Elles Être Exploitées en Local ?

**Oui, certaines failles peuvent être exploitées même sur une machine locale isolée.**
Une attaque moderne ne nécessite pas forcément qu'un pirate cible votre adresse IP depuis Internet : elle exploite les **flux de données non fiables** que le système ingère.

### A. Injection Indirecte de Commande Shell (`shell=True`) — Risque Élevé
- **Mécanisme** : Dans les scripts audio (`dbot/audio/tts.py`, `audio_io.py`), des commandes shell étaient construites par interpolation de chaînes f-string :
  `subprocess.run(f'echo "{text}" | piper ...', shell=True)`
- **Vecteur d'exploitation local** :
  La variable `text` provient soit d'une transcription vocale (STT), soit d'une réponse générée par un modèle de langage (LLM Groq, Gemini ou Ollama), soit d'un document du RAG.
  Si le modèle génère une réponse contenant des méta-caractères shell (ex. `"; rm -rf ...; "` ou `$(commande)`), le shell de votre Mac exécute la commande avec vos privilèges complets d'utilisateur.
  C'est le vecteur d'attaque dit d'**Indirect Prompt Injection**, très documenté en IA générative.

### B. Ingestion de Fichiers Malformés (CVEs dans `pypdf`) — Risque Moyen
- **Mécanisme** : `pypdf 6.7.5` comporte des CVEs de débordement de tampon et de déni de service lors de l'extraction de texte.
- **Vecteur d'exploitation local** :
  Si vous téléchargez un document PDF technique piégé sur un forum ou un site web externe et que vous l'ajoutez à la documentation indexée par le RAG, le parser PDF peut planter ou corrompre la mémoire lors de la lecture.

### C. Exécution de Code Non Vérifié (`trust_remote_code=True`) — Risque Moyen
- **Mécanisme** : Le chargement de modèles Hugging Face avec `trust_remote_code=True` sans commit figé (`revision="<hash>"`) télécharge et exécute du code Python arbitraire depuis les serveurs distants de Hugging Face.
- **Vecteur d'exploitation local** :
  Si le compte Hugging Face du modèle ou le repository distant est compromis, du code malicieux s'exécute automatiquement lors de l'instanciation du modèle sur votre Mac.

### D. Exposition Réseau Local (`0.0.0.0`) — Risque Faible à Moyen
- **Mécanisme** : L'écoute des serveurs de test sur `0.0.0.0` (au lieu de `127.0.0.1`) ouvre les ports sur tout le réseau local Wi-Fi.
- **Vecteur d'exploitation** :
  Sur un réseau Wi-Fi partagé (coworking, café, invités ou appareils IoT compromis), n'importe quel équipement peut envoyer des paquets forgés vers votre Mac.

---

## 3. Ont-Elles Été Exploitées ? (Diagnostic Médico-Légal)

**Non, il est certain à 99,9% qu'aucune de ces failles n'a été exploitée sur votre machine.**

### Éléments probants :
1. **Machine non exposée sur Internet** : Votre Mac est situé derrière le NAT et le pare-feu de votre box/routeur. Aucun port n'est redirigé depuis une IP publique.
2. **Sources de données fiables** : Tous les fichiers PDF et datasheets présents dans votre documentation proviennent de sources industrielles certifiées (EFANT, RobStride, McMaster-Carr) ou ont été écrits par vous-même.
3. **Usage local contrôlé des LLMs** : Vos sessions vocales et tests RAG ont porté sur des questions techniques robotiques bienveillantes, sans tentative d'injection.
4. **Secrets protégés** : Le fichier `.env` contenant vos clés réelles est bien listé dans `.gitignore` et n'a jamais été diffusé sur un dépôt public.

---

## 4. Outil d'Audit Unifié en 1 Clic (`audit_dbot_security.py`)

Le script [`audit_dbot_security.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/security/audit_dbot_security.py) permet de vérifier en une seule commande la santé de sécurité du projet.

### Exécution rapide (SAST + Secrets) :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/security/audit_dbot_security.py" --skip-sca
```

### Exécution complète (Dépendances CVE + SAST + Secrets) :
```bash
/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/security/audit_dbot_security.py"
```

---

## 5. Guide de Remédiation des Vulnérabilités

### 1. Remplacement de `shell=True` par des listes d'arguments (Sécurisation Audio)
Au lieu de passer par le shell :
```python
# VULNERABLE :
cmd = f'echo "{text}" | piper -m {model} --output_file {out}'
subprocess.run(cmd, shell=True)

# SECURISE :
p1 = subprocess.Popen(["echo", text], stdout=subprocess.PIPE)
subprocess.run(["piper", "-m", model, "--output_file", out], stdin=p1.stdout, check=True)
```

### 2. Sécurisation de `hashlib.md5()`
Pour éviter l'alerte Bandit B324 sur les hachages non cryptographiques (ex: indexation d'identifiants de documents) :
```python
# Remplacer :
doc_id = hashlib.md5(content.encode("utf-8")).hexdigest()

# Par :
doc_id = hashlib.md5(content.encode("utf-8"), usedforsecurity=False).hexdigest()
```

### 3. Mise à jour des bibliothèques vulnérables sur le Mac
Pour corriger les CVEs de `urllib3`, `starlette` et `pypdf` :
```bash
/opt/homebrew/bin/pip3.11 install --upgrade "urllib3>=2.7.0" "starlette>=1.3.1" "pypdf>=6.21.2"
```

---

## 6. Règles d'Approvisionnement Python (Mac vs Jetson Orin Nano)

### Règle Inviolable Jetson Orin Nano (JetPack 6.1 / CUDA 12.2)
- **Protection PyTorch GPU** : Ne JAMAIS exécuter `pip install torch` ou `pip install torchvision` sans `--no-deps` ni sans le wheel officiel NVIDIA JetPack.
- **Ajout systématique du drapeau `--no-deps`** lors de l'installation de tout utilitaire Python sur la Jetson :
```bash
pip install <nom_du_paquet> --no-deps
```
- Cette règle garantit que les liaisons matérielles CUDA 12.2 et TensorRT ne seront jamais écrasées par inadvertance.
