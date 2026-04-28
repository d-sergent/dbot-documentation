# 50 - Optimisation du Workflow LLM Local (M1 Max 64 Go)

> **Document de référence — Intelligence Artificielle D-Bot**
> Ce guide recense toutes les techniques d'optimisation pour maximiser l'intelligence et la fluidité des LLM locaux sur le Mac M1 Max, dans le cadre de la stack **VS Code + Continue + Ollama**.

---

## 1. Contexte : Les Contraintes de la Stack

La stack en place est fixe :
**Session dédiée IA → macOS → VS Code → Continue → Ollama**

Chaque couche impose des contraintes. Le tableau suivant liste toutes les techniques disponibles et leur compatibilité réelle avec cette stack.

| # | Technique | Compatible | Effort | Gain Estimé |
| :--- | :--- | :--- | :--- | :--- |
| A | **MLX (moteur natif Apple)** | ⚠️ Partiel (via serveur) | Moyen | +50% vitesse |
| B | **KV Cache Quantizé** | ✅ Oui | 2 lignes Modelfile | 2x plus de contexte |
| C | **Préfixe de Cache (auto)** | ✅ Automatique | Garder VS Code ouvert | -50% temps 1er token |
| D | **Décodage Spéculatif** | ⚠️ Partiel (via LM Studio) | Moyen | 2-4x vitesse |
| E | **GPTCache (chatbot.py)** | ⚠️ Partiel (scripts Python) | Code custom | ~0ms sur répétitions |
| F | **Session macOS dédiée IA** | ✅ Déjà en place | — | +8-12 Go de RAM |

---

## 2. Techniques Directement Compatibles avec Continue/Ollama

### B. KV Cache Quantizé ✅

La technique la plus impactante, applicable immédiatement.

**Principe :** La fenêtre de contexte (la mémoire de la conversation) consomme de la RAM proportionnellement à sa taille. En quantifiant ce cache en 8-bit, on divise sa RAM par deux, ce qui permet de doubler la taille du contexte sans utiliser plus de mémoire.

**Application dans le Modelfile :**
```dockerfile
# --- Dans votre Modelfile ---

# Quantifie le KV Cache en 8-bit → RAM du contexte divisée par 2
PARAMETER cache_type_k q8_0
PARAMETER cache_type_v q8_0

# Fenêtre de contexte élargie (32k à 64k tokens selon le modèle)
PARAMETER num_ctx 32768
```

Après modification du Modelfile, recompiler le modèle :
```bash
ollama create qwen-3.6-custom -f Modelfile
```

---

### C. Préfixe de Cache (Prompt Caching) ✅

**Principe :** Si vous gardez VS Code ouvert, Ollama met en cache le calcul de votre `SYSTEM` prompt. Les questions suivantes n'ont pas à le recalculer.

**Conséquence pratique :**
- **Première question** de la session : légèrement plus lente (calcul du contexte système).
- **Questions suivantes** : quasi-instantanées sur la partie déjà calculée.

> ⚠️ **Règle d'or** : Ne fermez pas VS Code sans raison entre deux sessions de travail. Plus la session reste ouverte, plus le cache préfixe est rentabilisé.

---

## 3. Techniques Partiellement Compatibles

### A. MLX — Le Moteur Natif Apple ⚠️

**Pourquoi c'est plus rapide :** MLX est le framework d'inférence créé par Apple pour la puce M-series. Il surpasse Ollama (basé sur `llama.cpp`) car il ne copie jamais les données entre CPU et GPU (opération "zero-copy"), tirant parti de la RAM unifiée de manière native.

**Pourquoi ce n'est pas compatible en direct :** Continue utilise Ollama comme provider. MLX est un moteur séparé. Il faut donc **lancer MLX comme un serveur OpenAI-compatible**, et pointer Continue vers ce serveur.

**Procédure (Mode Avancé) :**

*Étape 1 : Installer MLX et ses modèles*
```bash
pip install mlx-lm
# Les modèles MLX (pré-quantisés pour Apple Silicon) sont sur mlx-community (Hugging Face)
```

*Étape 2 : Lancer le serveur MLX*
```bash
# Lance un serveur OpenAI-compatible sur le port 8080
mlx_lm.server --model mlx-community/Qwen2.5-32B-Instruct-4bit
```

*Étape 3 : Pointer Continue vers ce serveur (config.yaml)*
```yaml
models:
  - name: "Qwen 32B (MLX Natif)"
    provider: "openai"          # Utilise le provider openai-compatible
    model: "qwen"               # Le serveur MLX ignore ce champ
    apiBase: "http://localhost:8080/v1"  # Le /v1 est obligatoire
    apiKey: "not-needed"
```

> [!NOTE]
> Les modèles MLX se trouvent sur `huggingface.co/mlx-community`. La convention de nommage est `NomDuModele-Xbit` (ex: `Qwen2.5-32B-Instruct-4bit`).

---

### D. Décodage Spéculatif ⚠️

**Principe :** Un petit modèle rapide (ex: `qwen 1.5B`) "devine" les prochains tokens. Le grand modèle (ex: `27B`) les valide en parallèle. Résultat : **2 à 4x plus de tokens par seconde** à qualité identique.

**Pourquoi ce n'est pas disponible dans Ollama :** Ollama ne supporte pas nativement cette fonctionnalité en 2026. Deux alternatives permettent d'y accéder :

**Alternative 1 : LM Studio (Interface graphique, le plus simple)**
LM Studio intègre nativement le décodage spéculatif depuis début 2025. Vous pouvez y configurer graphiquement un "modèle principal" et un "modèle brouillon".
*Inconvénient :* LM Studio est un outil lourd. Il remplace Ollama dans votre stack, ce qui retire l'avantage de la simplicité d'Ollama.

**Alternative 2 : llama.cpp Server (Mode Expert)**
`llama.cpp` peut être lancé directement en serveur OpenAI-compatible avec le décodage spéculatif activé.
```bash
# Exemple avec Qwen 27B + Qwen 1.5B comme brouillon
llama-server \
  --model ./qwen27b-q4.gguf \
  --model-draft ./qwen1.5b-q4.gguf \
  --draft 8 \
  --host 0.0.0.0 --port 8080
```
Ensuite, pointer Continue vers `http://localhost:8080/v1` comme pour MLX.

> [!IMPORTANT]
> **Contrainte RAM :** Le décodage spéculatif nécessite de charger **deux modèles simultanément** en RAM. Sur 64 Go, cela signifie par exemple un modèle 27B Q4 (~16 Go) + un modèle 1.5B Q4 (~1 Go). Cette contrainte reste très gérable sur M1 Max.

---

### E. GPTCache (Scripts Python) ⚠️

**Principe :** GPTCache intercepte les appels LLM. Si la question posée est sémantiquement proche d'une question déjà répondue, il retourne la réponse mise en cache en **quelques millisecondes** sans interroger le modèle.

**Non compatible avec Continue** (qui gère ses propres appels de manière opaque).
**Compatible avec votre `chatbot_local.py`** (appels directs à l'API Ollama depuis Python).

```python
# Installation
# pip install gptcache

from gptcache import cache
from gptcache.adapter import openai

cache.init()
cache.set_openai_key()

# Ensuite, utiliser `openai` de gptcache au lieu du module standard
response = openai.ChatCompletion.create(
    model="qwen-3.6-custom",
    messages=[{"role": "user", "content": votre_question}]
)
```

---

## 4. Récapitulatif des Actions Prioritaires

Pour la stack actuelle (VS Code + Continue + Ollama), les actions à faire **maintenant** par ordre de priorité :

1. **[Priorité 1]** Ajouter `cache_type_k q8_0` / `cache_type_v q8_0` dans vos Modelfiles → Gain immédiat sur le contexte.
2. **[Priorité 2]** Ne pas fermer VS Code entre les sessions → Cache préfixe automatique.
3. **[Priorité 3]** Tester MLX comme backend alternatif (mode avancé) si la vitesse devient un frein.
4. **[Futur]** Surveiller l'évolution d'Ollama : le support du décodage spéculatif est dans leur roadmap.

---

## 5. Calibrage DeepSeek R1 70B Q4 — Le Problème du KV Cache Géant

### Le Bug : Pourquoi 102 Go au lieu de 42 Go ?

Le modèle `deepseek-r1:70b-llama-distill-q4_K_M` charge par défaut une fenêtre de contexte de **131 072 tokens (128k)**. Le KV Cache associé est aussi volumineux que le modèle lui-même :

| Composant | Calcul | Taille |
| :--- | :--- | :--- |
| **Poids du modèle** (Q4_K_M) | — | ~42 Go |
| **KV Cache** (131k tokens, fp16 défaut) | 2 × 80 couches × 8 têtes × 128 dim × 131072 tokens × 2 octets | **~45 Go** |
| **Overhead système** | — | ~10 Go |
| **TOTAL observé** | | **~102 Go** |

**La règle clé :** La RAM du KV Cache est **strictement proportionnelle** au nombre de tokens de contexte. Couper le contexte par 4 divise le KV Cache par 4.

---

### Les 4 Modelfiles Calibrés pour M1 Max 64 Go

> [!IMPORTANT]
> Le paramètre `cache_type_k q8_0` est **obligatoire** pour les contextes ≥ 32k afin d'éviter de dépasser la RAM disponible.

#### 🎯 Profil "Code Concentré" — 16k tokens (~46 Go RAM)
*Usage : Debug de fonctions, questions ponctuelles, échanges courts. Le plus fluide.*

```dockerfile
FROM deepseek-r1:70b-llama-distill-q4_K_M

SYSTEM """
Tu es l'assistant technique du robot bipède D-Bot.
Tes réponses sont concises et orientées code Python/ROS2.
"""

# Contexte 16k : idéal pour la majorité des tâches de développement
PARAMETER num_ctx 16384
PARAMETER cache_type_k q8_0
PARAMETER cache_type_v q8_0
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"
```

```bash
ollama create deepseek-r1-16k -f Modelfile_16k
```
**RAM estimée : ~46 Go** ✅ Confortable (laisse 10+ Go pour le système)

---

#### 🎯 Profil "Architecture Système" — 32k tokens (~49 Go RAM)
*Usage : Lecture d'un module complet, analyse d'une centaine de fichiers Python.*

```dockerfile
FROM deepseek-r1:70b-llama-distill-q4_K_M

SYSTEM """
Tu es l'assistant technique du robot bipède D-Bot.
Tes réponses sont concises et orientées code Python/ROS2.
"""

# Contexte 32k : pour analyser plusieurs fichiers simultanément
PARAMETER num_ctx 32768
PARAMETER cache_type_k q8_0
PARAMETER cache_type_v q8_0
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"
```

```bash
ollama create deepseek-r1-32k -f Modelfile_32k
```
**RAM estimée : ~49 Go** ✅ Bon équilibre (recommandé pour usage quotidien)

---

#### 🎯 Profil "Lecture Documentation" — 48k tokens (~52 Go RAM)
*Usage : Ingestion de la documentation D-Bot complète, analyse de logs ROS2 longs.*

```dockerfile
FROM deepseek-r1:70b-llama-distill-q4_K_M

SYSTEM """
Tu es l'assistant technique du robot bipède D-Bot.
Tes réponses sont concises et orientées code Python/ROS2.
"""

# Contexte 48k : pour des tâches de lecture intensive de documentation
PARAMETER num_ctx 49152
PARAMETER cache_type_k q8_0
PARAMETER cache_type_v q8_0
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"
```

```bash
ollama create deepseek-r1-48k -f Modelfile_48k
```
**RAM estimée : ~52 Go** ✅ Fonctionnel en session dédiée IA

---

#### 🎯 Profil "Projet Complet" — 64k tokens (~55 Go RAM)
*Usage : Contexte maximal raisonnable. Ingestion du projet entier. Réservé à la session dédiée IA.*

```dockerfile
FROM deepseek-r1:70b-llama-distill-q4_K_M

SYSTEM """
Tu es l'assistant technique du robot bipède D-Bot.
Tes réponses sont concises et orientées code Python/ROS2.
"""

# Contexte 64k : maximum recommandé sur M1 Max 64 Go en session dédiée
# ⚠️ Fermer Chrome, Slack et toutes les apps tierces avant de lancer
PARAMETER num_ctx 65536
PARAMETER cache_type_k q8_0
PARAMETER cache_type_v q8_0
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"
```

```bash
ollama create deepseek-r1-64k -f Modelfile_64k
```
**RAM estimée : ~55 Go** ⚠️ Nécessite la session dédiée IA + toutes apps fermées

---

### Tableau de Synthèse des 4 Profils

| Profil | num_ctx | KV Cache (q8_0) | RAM Totale | Utilisation |
| :--- | :--- | :--- | :--- | :--- |
| **16k** "Code Concentré" | 16 384 | ~2.5 Go | **~46 Go** ✅ | Questions courtes, debug |
| **32k** "Architecture" | 32 768 | ~5 Go | **~49 Go** ✅ | Usage quotidien recommandé |
| **48k** "Documentation" | 49 152 | ~7.5 Go | **~52 Go** ✅ | Lecture de fichiers longs |
| **64k** "Projet Complet" | 65 536 | ~10 Go | **~55 Go** ⚠️ | Session dédiée obligatoire |
| ~~**128k (défaut)**~~ | ~~131 072~~ | ~~45 Go~~ | ~~**102 Go** ❌~~ | Impossible sur 64 Go |

---

*Document créé en Avril 2026 — Architecture IA D-Bot.*

