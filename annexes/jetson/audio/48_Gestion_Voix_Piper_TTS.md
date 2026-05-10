# 48 — Gestion des Voix Piper (TTS)

*Dernière mise à jour : 10 Mai 2026*

---

## 1. Principe de Fonctionnement

D-Bot utilise **Piper-TTS** pour la synthèse vocale. Piper fonctionne avec des fichiers de voix au format `.onnx` (réseau de neurones léger) accompagnés d'un fichier de configuration `.onnx.json`.

```
texte → [Piper + fichier .onnx] → fichier .wav → [paplay] → haut-parleur
```

Les voix sont stockées dans : `~/.local/share/piper-voices/`

La voix par défaut est `fr_FR-upmc-medium.onnx`.

---

## 2. Catalogue des Voix Françaises Disponibles

| Identifiant | Genre | Qualité | Vitesse | Usage recommandé |
| :--- | :---: | :---: | :---: | :--- |
| `fr_FR-upmc-medium` | Féminin | ⭐⭐⭐ | Rapide | Voix actuelle (défaut) |
| `fr_FR-siwis-medium` | Féminin | ⭐⭐⭐⭐ | Moyenne | Voix naturelle, conversations |
| `fr_FR-siwis-low` | Féminin | ⭐⭐ | Très rapide | Si latence critique |
| `fr_FR-gilles-low` | Masculin | ⭐⭐ | Très rapide | Voix robot grave |
| `fr_FR-mls-medium` | Masculin | ⭐⭐⭐ | Rapide | Voix neutre masculine |

> [!TIP]
> Pour D-Bot, la voix `fr_FR-siwis-medium` offre le meilleur équilibre naturalité/latence. La voix `fr_FR-gilles-low` donne un effet "voix de robot" plus prononcé si souhaité.

---

## 3. Télécharger une Nouvelle Voix

Toutes les voix sont disponibles sur **Hugging Face** (dépôt officiel Piper).

### Commande générique

```bash
# Remplacez <NOM_VOIX> par l'identifiant du tableau ci-dessus
cd ~/.local/share/piper-voices/

# Télécharger les deux fichiers obligatoires (.onnx + .onnx.json)
BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main"
wget "$BASE/fr/fr_FR/<NOM_VOIX>.onnx"
wget "$BASE/fr/fr_FR/<NOM_VOIX>.onnx.json"
```

### Exemples concrets

```bash
cd ~/.local/share/piper-voices/

# Voix féminine naturelle (recommandée)
wget "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx"
wget "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json"

# Voix masculine grave
wget "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx"
wget "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx.json"
```

> [!NOTE]
> Chaque voix pèse entre **30 Mo** (low) et **65 Mo** (medium). Toutes fonctionnent hors-ligne une fois téléchargées.

---

## 4. Tester une Voix Rapidement

```bash
# Test direct en ligne de commande (sans lancer le robot)
echo "Bonjour, je suis D-Bot, votre robot compagnon." | \
  piper -m ~/.local/share/piper-voices/fr_FR-siwis-medium.onnx \
        --output_file /tmp/test_voix.wav \
  && paplay /tmp/test_voix.wav
```

---

## 5. Changer la Voix du Robot

### Méthode 1 — Variable d'environnement (sans modifier le code)

```bash
# La variable PIPER_VOICE surcharge le chemin par défaut dans tts.py
PIPER_VOICE=~/.local/share/piper-voices/fr_FR-siwis-medium.onnx \
  python3 ~/dbot/code/scripts/behaviors/chatbot_local_v2.py
```

> [!IMPORTANT]
> Cette méthode nécessite que `tts.py` soit mis à jour pour lire `PIPER_VOICE` (voir section 6).

### Méthode 2 — Argument au constructeur (dans le code)

```python
from dbot.audio.tts import LocalTTS

# Passer le chemin de la voix directement
tts = LocalTTS(
    voice_model_path="/home/david/.local/share/piper-voices/fr_FR-siwis-medium.onnx"
)
```

### Méthode 3 — Modifier le chemin par défaut dans `tts.py`

Ouvrir `code/dbot/audio/tts.py` et changer la ligne :
```python
# Avant
self.voice_model_path = os.path.expanduser("~/.local/share/piper-voices/fr_FR-upmc-medium.onnx")

# Après (exemple avec siwis)
self.voice_model_path = os.path.expanduser("~/.local/share/piper-voices/fr_FR-siwis-medium.onnx")
```

---

## 6. Mise à jour de `tts.py` pour la Variable d'Environnement

Pour que la **Méthode 1** fonctionne, `tts.py` doit lire la variable `PIPER_VOICE`.
Le constructeur `__init__` de `LocalTTS` doit contenir :

```python
# Chemin de la voix — priorité : argument > variable env > défaut
if voice_model_path is None:
    voice_model_path = os.environ.get(
        "PIPER_VOICE",
        os.path.expanduser("~/.local/share/piper-voices/fr_FR-upmc-medium.onnx")
    )
self.voice_model_path = voice_model_path
```

---

## 7. Trouver d'Autres Voix

L'index complet des voix Piper (toutes langues) est disponible ici :
- **[Liste officielle des voix](https://huggingface.co/rhasspy/piper-voices/blob/main/VOICES.md)**

Pour filtrer les voix françaises uniquement :
```bash
# Chercher les voix FR dans l'index Piper
curl -s https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json | \
  python3 -c "import sys,json; v=json.load(sys.stdin); [print(k) for k in v if k.startswith('fr_FR')]"
```

---

*Document créé le 10/05/2026*
