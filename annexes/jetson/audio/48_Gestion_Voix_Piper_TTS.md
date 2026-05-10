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

## 2. Catalogue Complet des Voix Françaises

> Source : [voices.json officiel Piper](https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json) — Mis à jour le 10/05/2026.

Il existe **7 voix françaises** (`fr_FR`) dans le dépôt officiel Piper :

| Identifiant | Genre | Qualité | Vitesse | Taille | Usage recommandé |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `fr_FR-upmc-medium` | Féminin | ⭐⭐⭐ | Rapide | ~45 Mo | ✅ Voix actuelle (défaut) |
| `fr_FR-siwis-medium` | Féminin | ⭐⭐⭐⭐ | Moyenne | ~60 Mo | ⭐ Recommandée — naturelle |
| `fr_FR-siwis-low` | Féminin | ⭐⭐ | Très rapide | ~30 Mo | Si latence critique (<0.3s) |
| `fr_FR-tom-medium` | Masculin | ⭐⭐⭐⭐ | Moyenne | ~60 Mo | Voix masculine naturelle |
| `fr_FR-mls-medium` | Masculin | ⭐⭐⭐ | Rapide | ~45 Mo | Voix masculine neutre |
| `fr_FR-mls_1840-low` | Masculin | ⭐⭐ | Très rapide | ~30 Mo | Voix masculine légère |
| `fr_FR-gilles-low` | Masculin | ⭐⭐ | Très rapide | ~30 Mo | Effet "robot" prononcé |

> [!TIP]
> **Pour D-Bot :** `fr_FR-siwis-medium` (féminin naturel) ou `fr_FR-tom-medium` (masculin naturel) offrent le meilleur rendu conversationnel. `fr_FR-gilles-low` est à essayer si vous voulez un effet "voix de robot" délibéré.

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

### Télécharger TOUTES les voix en une seule commande

```bash
cd ~/.local/share/piper-voices/
BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR"

for f in \
  "siwis/medium/fr_FR-siwis-medium" \
  "siwis/low/fr_FR-siwis-low" \
  "tom/medium/fr_FR-tom-medium" \
  "mls/medium/fr_FR-mls-medium" \
  "mls_1840/low/fr_FR-mls_1840-low" \
  "gilles/low/fr_FR-gilles-low"
do
  wget -nc "$BASE/$f.onnx"
  wget -nc "$BASE/$f.onnx.json"
done

echo "✅ Toutes les voix françaises téléchargées dans ~/.local/share/piper-voices/"
```

> [!NOTE]
> L'option `-nc` (no-clobber) évite de re-télécharger les fichiers déjà présents. Espace total nécessaire : **~360 Mo** pour les 7 voix.

### Télécharger une voix individuelle

```bash
cd ~/.local/share/piper-voices/
BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR"

# Féminin — siwis medium (recommandée)
wget "$BASE/siwis/medium/fr_FR-siwis-medium.onnx"
wget "$BASE/siwis/medium/fr_FR-siwis-medium.onnx.json"

# Masculin — tom medium
wget "$BASE/tom/medium/fr_FR-tom-medium.onnx"
wget "$BASE/tom/medium/fr_FR-tom-medium.onnx.json"
```

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

> [!TIP]
> `tts.py` lit déjà `PIPER_VOICE` nativement depuis la mise à jour du 10/05/2026.

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

## 8. Piper est-il le Meilleur Choix ? — Comparatif TTS (Mai 2026)

*Analyse réalisée le 10/05/2026 à partir des benchmarks disponibles sur Jetson Orin Nano.*

### Tableau Comparatif

| Critère | **Piper** ✅ (actuel) | **Kokoro** | **XTTS v2** |
| :--- | :---: | :---: | :---: |
| **Qualité voix FR** | ⭐⭐⭐ Claire | ⭐⭐⭐⭐ Humaine | ⭐⭐⭐⭐⭐ Pro |
| **Latence Jetson Orin Nano** | **< 0.3s** ✅ | ~0.5-1s ✅ | **2-5s** ❌ |
| **RAM consommée** | ~50 Mo | ~200 Mo | ~1.5 Go GPU |
| **CPU seul possible** | ✅ Oui | ✅ Oui | ❌ GPU requis |
| **Français natif (voix dédiées)** | ✅ 7 voix | ⚠️ Limité | ✅ Multilingue |
| **Installation** | Triviale | Modérée | Complexe |
| **Licence** | MIT | Apache 2.0 | CPML (restrictive) |
| **Usage D-Bot** | ✅ Production | 🧪 À tester | ❌ Trop lent |

### Verdict

> [!IMPORTANT]
> **Piper est le bon choix pour la production D-Bot.** La latence < 0.3s est un avantage décisif pour une conversation fluide. Avec les voix `fr_FR-siwis-medium` ou `fr_FR-tom-medium`, la qualité est très acceptable pour un robot compagnon.

**Pourquoi pas XTTS ?**
2 à 5 secondes de synthèse sur Jetson Orin Nano = incompatible avec une conversation fluide. L'objectif de latence totale < 3 secondes (VAD → STT → LLM → TTS) ne peut pas être respecté.

**Pourquoi Kokoro pourrait être intéressant ?**
Si la voix Piper est jugée trop robotique après tests réels, Kokoro offre une prosodie plus naturelle avec une latence ~1s (acceptable). Son support du français est cependant encore limité en 2026.

### Tester Kokoro (optionnel)

```bash
pip install kokoro soundfile
```

```python
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code='f')  # 'f' = français
generator = pipeline("Bonjour, je suis D-Bot.", voice='ff_siwis')
for i, (_, _, audio) in enumerate(generator):
    sf.write('/tmp/kokoro_test.wav', audio, 24000)
    break
# Écouter : paplay /tmp/kokoro_test.wav
```

> [!NOTE]
> Si la qualité Kokoro en français est insuffisante, restez sur Piper `fr_FR-siwis-medium`. La décision peut être révisée à chaque nouvelle release de Kokoro.

---

*Document créé le 10/05/2026 — Comparatif TTS ajouté le 10/05/2026*
