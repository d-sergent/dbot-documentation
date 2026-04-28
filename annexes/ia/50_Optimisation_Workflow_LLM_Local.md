# 50 - Optimisation du Workflow LLM Local (M1 Max 64 Go)

> **Document de référence — Intelligence Artificielle D-Bot**
> Ce guide recense toutes les techniques d'optimisation pour maximiser l'intelligence et la fluidité des LLM locaux sur le Mac M1 Max, dans le cadre de la stack **VS Code + Continue**.

---

## 1. Contexte : Les Contraintes de la Stack

La stack en place est fixe :
**Session dédiée IA → macOS → VS Code → Continue → Moteur d'inférence**

| # | Technique | Ollama | LM Studio | llama-server |
| :--- | :--- | :---: | :---: | :---: |
| A | MLX (moteur natif Apple) | ⚠️ Via serveur | ✅ Natif | ❌ |
| B | KV Cache quantizé | ❌ | ✅ Q8_0 | ✅ |
| C | Préfixe de Cache (auto) | ✅ | ✅ | ✅ |
| D | Décodage Spéculatif | ❌ | ✅ | ✅ |
| E | Swap automatique de modèles (JIT) | ✅ | ✅ | ❌ (1 modèle) |
| F | Session macOS dédiée IA | ✅ (déjà en place) | ✅ | ✅ |

---

## 2. Techniques Disponibles avec Ollama (Stack actuelle)

### B. Contrôle du Contexte via num_ctx ✅

> [!IMPORTANT]
> Les paramètres `cache_type_k` et `cache_type_v` **ne sont PAS supportés** dans Ollama. Seul `num_ctx` contrôle la RAM du KV cache.

```dockerfile
# Modelfile Ollama valide pour DeepSeek R1 70B
FROM deepseek-r1:70b-llama-distill-q4_K_M

SYSTEM """
Tu es l'assistant technique du robot bipède D-Bot.
Tes réponses sont concises et orientées code Python/ROS2.
"""

PARAMETER num_ctx 32768
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"
```

**Impact RAM selon num_ctx (KV cache fp16 Ollama) :**

| Contexte | KV Cache | RAM Totale | Statut |
| :--- | :--- | :--- | :--- |
| 16 384 | ~5 Go | **~47 Go** | ✅ Confortable |
| 32 768 | ~10 Go | **~52 Go** | ✅ **Recommandé** |
| 49 152 | ~15 Go | **~57 Go** | ⚠️ Session dédiée |
| 65 536 | ~20 Go | **~62 Go** | ❌ Swap probable |
| ~~131 072 (défaut)~~ | ~~40 Go~~ | ~~**~102 Go**~~ | ❌ Crash |

### C. Préfixe de Cache ✅

Ollama met en cache le calcul du `SYSTEM` prompt si VS Code reste ouvert. Les questions suivantes ne recalculent pas ce préfixe.

> **Règle d'or :** Ne fermez pas VS Code entre deux sessions de travail.

### E. GPTCache (Scripts Python uniquement) ⚠️

Non compatible avec Continue (appels internes opaques). Compatible avec `chatbot_local.py`.

```python
# pip install gptcache
from gptcache import cache
from gptcache.adapter import openai
cache.init()
```

---

## 3. Dépasser les Limites d'Ollama : llama-server

### Comparatif

| Fonctionnalité | Ollama | llama-server |
| :--- | :---: | :---: |
| KV Cache quantizé (`--cache-type-k q8_0`) | ❌ | ✅ |
| Flash Attention | Auto | ✅ Explicite |
| Décodage Spéculatif (`--model-draft`) | ❌ | ✅ |
| Swap JIT multi-modèles | ✅ | ❌ (1 modèle par instance) |

### Installation

```bash
brew install llama.cpp
```

### Le Script Maître `/Users/Shared/IA/launch_ia.sh`

```bash
./launch_ia.sh rapide            # 16k tokens, ~47 Go RAM
./launch_ia.sh quotidien         # 32k tokens, ~49 Go RAM (recommandé)
./launch_ia.sh documentation oui # 48k tokens + décodage spéculatif
./launch_ia.sh maximum           # 64k tokens, ~55 Go RAM ⚠️
```

Applique automatiquement : `--cache-type-k q8_0`, `--flash-attn`, `--n-gpu-layers 999`, `--model-draft`.

### Profils llama-server (KV Cache q8_0)

| Profil | Contexte | RAM Totale | Statut |
| :--- | :--- | :--- | :--- |
| rapide | 16 384 | **~47 Go** | ✅ |
| quotidien | 32 768 | **~49 Go** | ✅ **Recommandé** |
| documentation | 49 152 | **~52 Go** | ✅ |
| maximum | 65 536 | **~55 Go** | ⚠️ |

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

## 4. Alternative Graphique : LM Studio (Recommandé)

### Pourquoi LM Studio plutôt que llmster ?

`llmster` (daemon headless de LM Studio) libère ~500 Mo en fermant l'interface. Mais il **ne supporte pas le décodage spéculatif**. Or ce dernier apporte 2 à 4x plus de tokens/seconde — un gain sans commune mesure.

| Critère | LM Studio GUI | llmster (CLI) |
| :--- | :---: | :---: |
| Décodage spéculatif | ✅ | ❌ |
| KV Cache Q8_0 | ✅ | ✅ |
| MLX natif | ✅ | ✅ |
| JIT swap multi-modèles | ✅ | ✅ |
| RAM économisée | — | ~500 Mo |
| Gain vitesse spéculatif | **+200 à 400%** | — |

**Conclusion : LM Studio GUI est recommandé.**

---

### LM Studio swape-t-il les modèles automatiquement (comme Ollama) ?

**Oui, via le "Just in Time (JIT) Model Loading".**

Quand Continue demande un modèle différent (ex: l'autocomplete utilise `starcoder2:3b` et le chat `deepseek-r1:70b`), LM Studio charge automatiquement le bon modèle et décharge l'ancien si la RAM est insuffisante.

**À activer dans l'onglet Server :**
- ✅ **"Just in Time Model Loading"**
- ✅ **"Auto Unload Unused JIT Models"**

**Limite importante :** Le décodage spéculatif ne s'applique qu'au **modèle principal pré-chargé**. Les modèles chargés via JIT en bénéficient pas.

**Stratégie config.yaml recommandée :**
```yaml
models:
  # Modèle principal : pré-chargé, bénéficie du spéculatif
  - name: "DeepSeek R1 70B"
    provider: openai
    model: deepseek-r1-70b
    apiBase: "http://localhost:1234/v1"
    apiKey: "lm-studio"

  # Modèle léger : chargé à la demande via JIT
  - name: "Qwen 27B (rapide)"
    provider: openai
    model: qwen2.5-27b
    apiBase: "http://localhost:1234/v1"
    apiKey: "lm-studio"

tabAutocompleteModel:
  name: "Starcoder2 3B"
  provider: openai
  model: starcoder2-3b
  apiBase: "http://localhost:1234/v1"
  apiKey: "lm-studio"
```

---

### MLX dans LM Studio : Quel format selon la taille du modèle ?

LM Studio peut utiliser deux backends :

| Format | Backend | Spéculatif | Gain vitesse |
| :--- | :--- | :--- | :--- |
| `.gguf` | llama.cpp | ✅ | Référence |
| `.safetensors` (MLX) | Apple MLX | ❌ | +30 à 50% |

**Règle : spéculatif (2-4x) > MLX seul (30-50%). Ne pas mettre les gros modèles en MLX.**

| Modèle | Format recommandé | Raison |
| :--- | :--- | :--- |
| **DeepSeek R1 70B** | GGUF Q4_K_M | Spéculatif disponible → gain maximal |
| **Qwen 3.6 27B** | MLX 4-bit | Déjà fluide, MLX natif plus rapide |
| **Qwen 3.6 35B MoE** | GGUF Q8 | Meilleure disponibilité en GGUF |
| **Starcoder2 3B (autocomplete)** | MLX 4-bit | Légèreté, MLX parfait |
| **nomic-embed-text** | MLX | Embedding Apple Silicon natif |

**Modèles MLX disponibles :** `huggingface.co/mlx-community`
```
mlx-community/Qwen2.5-32B-Instruct-4bit
mlx-community/Qwen2.5-14B-Instruct-4bit
mlx-community/starcoder2-3b-4bit
```

> [!TIP]
> Pour le DeepSeek R1 70B : **GGUF + spéculatif reste toujours plus rapide que MLX seul**. Ne le convertissez pas en MLX.

---

### Procédure LM Studio (Configuration Optimale)

**1 —** Télécharger LM Studio sur **[lmstudio.ai](https://lmstudio.ai)** (macOS Apple Silicon).

**2 —** Charger le modèle principal (onglet "My Models" → GGUF → "Load").

**3 —** Configurer le serveur (onglet "Developer" > "Server") :

| Paramètre | Valeur | Impact |
| :--- | :--- | :--- |
| **Context Length** | `32768` | RAM KV Cache maîtrisée |
| **GPU Offload** | `Max` | Tout sur Metal (M1 Max) |
| **KV Cache Quantization** | `Q8_0` | RAM KV ÷ 2 |
| **Flash Attention** | Activé | +20% vitesse |
| **Speculative Decoding** | Activé | **+200 à 400% vitesse** |
| **Draft Model** | `qwen2.5-1.5b-q4` | Prédictions rapides |
| **Just in Time Loading** | Activé | Swap automatique de modèles |
| **Auto Unload Unused Models** | Activé | Libère RAM des modèles inactifs |

**4 —** Cliquer "Start Server" → API sur `http://localhost:1234/v1`

**5 —** Réduire LM Studio dans le Dock — le serveur continue de tourner.

---

## 5. Récapitulatif — Quel outil choisir ?

| Scénario | Outil recommandé |
| :--- | :--- |
| **Maximum performance** (KV q8 + spéculatif + contrôle fin) | `launch_ia.sh` (llama-server) |
| **Simplicité + spéculatif + JIT swap + MLX** | **LM Studio GUI** ✅ |
| **Production légère sans spéculatif** | `lms load` + `lms server start` |
| **Tests et exploration de modèles** | LM Studio GUI |

---

*Document créé en Avril 2026 — Architecture IA D-Bot.*
