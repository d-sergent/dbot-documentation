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
| B | **Contrôle du contexte (num_ctx)** | ✅ Oui | 1 ligne Modelfile | RAM maîtrisée |
| C | **Préfixe de Cache (auto)** | ✅ Automatique | Garder VS Code ouvert | -50% temps 1er token |
| D | **Décodage Spéculatif** | ⚠️ Via LM Studio ou llama-server | Moyen | 2-4x vitesse |
| E | **GPTCache (chatbot.py)** | ⚠️ Partiel (scripts Python) | Code custom | ~0ms sur répétitions |
| F | **Session macOS dédiée IA** | ✅ Déjà en place | — | +8-12 Go de RAM |

---

## 2. Techniques Directement Compatibles avec Continue/Ollama

### B. Contrôle du Contexte via num_ctx ✅

> [!IMPORTANT]
> Les paramètres `cache_type_k` et `cache_type_v` **ne sont PAS supportés** par le Modelfile d'Ollama. Seul `num_ctx` contrôle la RAM du KV cache dans Ollama.

**Principe :** La RAM du KV cache est strictement proportionnelle au nombre de tokens de contexte. Réduire `num_ctx` est le seul levier disponible dans Ollama pour contrôler la RAM.

```dockerfile
# Modelfile Ollama valide pour DeepSeek R1 70B
FROM deepseek-r1:70b-llama-distill-q4_K_M

SYSTEM """
Tu es l'assistant technique du robot bipède D-Bot.
Tes réponses sont concises et orientées code Python/ROS2.
"""

# Seuls paramètres valides dans un Modelfile Ollama :
PARAMETER num_ctx 32768       # Contexte 32k : ~52 Go RAM totale
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"
```

**Impact RAM selon num_ctx (DeepSeek R1 70B Q4, KV cache fp16 Ollama) :**

| Contexte | KV Cache | RAM Totale | Statut |
| :--- | :--- | :--- | :--- |
| 16 384 | ~5 Go | **~47 Go** | ✅ Confortable |
| 32 768 | ~10 Go | **~52 Go** | ✅ **Recommandé** |
| 49 152 | ~15 Go | **~57 Go** | ⚠️ Session dédiée |
| 65 536 | ~20 Go | **~62 Go** | ❌ Swap probable |
| ~~131 072 (défaut)~~ | ~~40 Go~~ | ~~**~102 Go**~~ | ❌ Crash |

---

### C. Préfixe de Cache (Prompt Caching) ✅

**Principe :** Si vous gardez VS Code ouvert, Ollama met en cache le calcul de votre `SYSTEM` prompt. Les questions suivantes ne le recalculent pas.

> ⚠️ **Règle d'or** : Ne fermez pas VS Code sans raison entre deux sessions de travail.

---

## 3. Techniques Partiellement Compatibles

### A. MLX — Le Moteur Natif Apple ⚠️

**Principe :** MLX est le framework d'inférence Apple, optimisé pour la RAM unifiée M-series (zero-copy CPU↔GPU). Il surpasse Ollama sur la vitesse des longs contextes.

**Utilisation avec Continue :** Lancer MLX comme serveur OpenAI-compatible, puis pointer Continue dessus.

```bash
# Installation
pip install mlx-lm

# Lancement du serveur (modèles sur huggingface.co/mlx-community)
mlx_lm.server --model mlx-community/Qwen2.5-32B-Instruct-4bit
```

```yaml
# config.yaml Continue
models:
  - name: "Qwen 32B (MLX Natif)"
    provider: openai
    model: qwen
    apiBase: "http://localhost:8080/v1"
    apiKey: "not-needed"
```

---

### D. Décodage Spéculatif ⚠️

**Principe :** Un petit modèle rapide (ex: `1.5B`) devine les prochains tokens, le grand modèle (ex: `70B`) les valide en parallèle. Résultat : **2 à 4x plus de tokens par seconde** à qualité identique.

Non disponible dans Ollama. Deux alternatives (voir sections 5 et 6).

---

### E. GPTCache (Scripts Python) ⚠️

Intercepte les appels LLM avant qu'ils n'atteignent le modèle. Si une question similaire a déjà été répondue, retourne le cache en millisecondes.

**Non compatible avec Continue** (appels internes opaques).
**Compatible avec votre `chatbot_local.py`** (appels directs à l'API Ollama).

```python
# pip install gptcache
from gptcache import cache
from gptcache.adapter import openai
cache.init()
```

---

## 4. Récapitulatif des Actions Prioritaires

1. **[Priorité 1]** Contrôler `num_ctx` dans vos Modelfiles Ollama (seul levier RAM valide).
2. **[Priorité 2]** Garder VS Code ouvert entre les sessions → cache préfixe automatique.
3. **[Priorité 3]** Migrer vers LM Studio ou llama-server pour débloquer le décodage spéculatif (voir sections 5 et 6).
4. **[Futur]** Surveiller Ollama : la quantification du KV cache est dans leur roadmap.

---

## 5. Dépasser les Limites d'Ollama : llama-server + Script Shell

### Comparatif Ollama vs llama-server

| Fonctionnalité | Ollama | llama-server |
| :--- | :---: | :---: |
| Contrôle du contexte | ✅ | ✅ |
| KV Cache quantizé (--cache-type-k q8_0) | ❌ | ✅ |
| Flash Attention | Auto | ✅ Explicite |
| Décodage Spéculatif (--model-draft) | ❌ | ✅ |
| API OpenAI-compatible (Continue) | ✅ | ✅ |

### Installation

```bash
brew install llama.cpp
```

### Le Script Maître `/Users/Shared/IA/launch_ia.sh`

```bash
# Usage
./launch_ia.sh [MODE] [DRAFT]

# Exemples
./launch_ia.sh rapide            # 16k tokens, ~47 Go RAM
./launch_ia.sh quotidien         # 32k tokens, ~49 Go RAM (recommandé)
./launch_ia.sh documentation oui # 48k tokens + décodage spéculatif
./launch_ia.sh maximum           # 64k tokens, ~55 Go RAM ⚠️
```

Le script applique automatiquement :
- `--cache-type-k q8_0` / `--cache-type-v q8_0` → KV Cache ÷ 2
- `--flash-attn` → +20% de vitesse
- `--n-gpu-layers 999` → tout sur GPU Metal
- `--model-draft` → décodage spéculatif si `DRAFT=oui`

### Tableau des Profils (llama-server, KV Cache q8_0)

| Profil | Contexte | KV Cache (q8_0) | RAM Totale | Statut |
| :--- | :--- | :--- | :--- | :--- |
| **rapide** | 16 384 | ~2.5 Go | **~47 Go** | ✅ Confortable |
| **quotidien** | 32 768 | ~5 Go | **~49 Go** | ✅ **Recommandé** |
| **documentation** | 49 152 | ~7.5 Go | **~52 Go** | ✅ Session dédiée |
| **maximum** | 65 536 | ~10 Go | **~55 Go** | ⚠️ Apps fermées |

### Connecter Continue à llama-server

```yaml
models:
  - name: "DeepSeek R1 70B (llama-server)"
    provider: openai
    model: deepseek-r1
    apiBase: "http://localhost:8080/v1"
    apiKey: "not-needed"
```

---

## 6. Alternative Graphique : LM Studio (Recommandé)

### Pourquoi LM Studio et non llmster ?

`llmster` est le daemon headless de LM Studio. Il libère ~500 Mo de RAM en fermant l'interface graphique. Cependant, **llmster ne supporte pas le décodage spéculatif** via la CLI `lms`.

Or le décodage spéculatif apporte **2 à 4x plus de tokens par seconde** — un gain bien supérieur aux 500 Mo économisés.

**Conclusion : préconiser LM Studio GUI plutôt que llmster.**

| Critère | LM Studio GUI | llmster (lms CLI) |
| :--- | :---: | :---: |
| Décodage spéculatif | ✅ | ❌ |
| KV Cache Q8_0 | ✅ | ✅ |
| Flash Attention | ✅ | ✅ |
| RAM économisée vs l'autre | — | ~500 Mo |
| Gain vitesse (spéculatif) | **+200 à +400%** | — |

### Procédure LM Studio (Configuration Optimale)

**1 — Télécharger** LM Studio sur **[lmstudio.ai](https://lmstudio.ai)** (version macOS Apple Silicon).

**2 — Charger le modèle** dans l'onglet "My Models" → sélectionner le GGUF → "Load".

**3 — Configurer le serveur** (onglet "Developer" > "Server") :

| Paramètre | Valeur | Impact |
| :--- | :--- | :--- |
| **Context Length** | `32768` | RAM KV Cache maîtrisée |
| **GPU Offload** | `Max` | Tout sur Metal (M1 Max) |
| **KV Cache Quantization** | `Q8_0` | RAM KV ÷ 2 |
| **Flash Attention** | Activé | +20% vitesse |
| **Speculative Decoding** | Activé | **+200 à 400% vitesse** |
| **Draft Model** | `qwen2.5-1.5b-q4` | Prédictions rapides |

**4 — Démarrer le serveur** → API sur `http://localhost:1234/v1`

**5 — Connecter Continue (config.yaml) :**
```yaml
models:
  - name: "DeepSeek R1 70B (LM Studio + Spéculatif)"
    provider: openai
    model: deepseek-r1
    apiBase: "http://localhost:1234/v1"
    apiKey: "lm-studio"
```

> [!NOTE]
> Une fois le serveur démarré, réduire LM Studio dans le Dock. Le serveur continue de tourner. Les ~500 Mo de l'interface sont largement compensés par le gain du décodage spéculatif.

### Récapitulatif — Quel outil choisir ?

| Scénario | Outil recommandé |
| :--- | :--- |
| **Maximum performance** (toutes options) | `launch_ia.sh` (llama-server) |
| **Simplicité + décodage spéculatif** | **LM Studio GUI** |
| **Simple production sans spéculatif** | `lms load` + `lms server start` (llmster) |
| **Tests et exploration** | LM Studio GUI |

---

*Document créé en Avril 2026 — Architecture IA D-Bot.*
