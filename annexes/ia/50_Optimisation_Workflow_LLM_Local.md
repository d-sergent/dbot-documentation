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
  # L'Agent de terrain (Chargé en JIT via MLX natif, très fiable pour les outils)
  - name: "Agent (Qwen 3.6 35B MLX)"
    provider: openai
    model: "mlx-community/Qwen3.6-35B-4bit"
    apiBase: "http://localhost:1234/v1"
    apiKey: "lm-studio"
    roles: [chat, edit]

  # Le Spécialiste (Pré-chargé, bénéficie du décodage spéculatif)
  - name: "Expert (DeepSeek R1 70B)"
    provider: openai
    model: "deepseek-r1-70b"
    apiBase: "http://localhost:1234/v1"
    apiKey: "lm-studio"
    roles: [chat]

tabAutocompleteModel:
  # Autocomplete ultra-léger via JIT
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
| **Qwen 3.6 35B** | **MLX 4-bit** | Fiabilité outils, MLX natif plus rapide |
| **Qwen 3.6 27B** | MLX 4-bit | Alternative ultra-rapide |
| **Starcoder2 3B** | MLX 4-bit | Légèreté, MLX parfait |
| **nomic-embed-text** | MLX | Embedding Apple Silicon natif |

> [!IMPORTANT]
> **Pourquoi 4-bit et non 8-bit ?**
> Sur 64 Go de RAM, un modèle 35B en 8-bit pèse ~35 Go. Lors d'un swap JIT avec DeepSeek R1 (40 Go), vous dépasserez les 64 Go, provoquant un ralentissement massif (Swap disque). Le **4-bit (~20 Go)** permet un switch fluide.

---

### Procédure LM Studio (Configuration Optimale)

**1 —** Télécharger LM Studio sur **[lmstudio.ai](https://lmstudio.ai)** (macOS Apple Silicon).

**2 —** Charger le modèle principal (onglet "My Models" → **DeepSeek R1 GGUF** → "Load").

**3 —** Configurer le serveur (onglet "Developer" > "Server") :

| Paramètre | Valeur | Impact |
| :--- | :--- | :--- |
| **Context Length** | `32768` | RAM KV Cache maîtrisée |
| **GPU Offload** | `Max` | Tout sur Metal (M1 Max) |
| **KV Cache Quantization** | `Q8_0` | RAM KV ÷ 2 |
| **Flash Attention** | Activé | +20% vitesse |
| **Speculative Decoding** | Activé | **+200 à 400% vitesse** |
| **Draft Model** | `qwen1.5b-q4` | Prédictions rapides |
| **Just in Time Loading** | Activé | Swap automatique de modèles |
| **Auto Unload Unused Models** | Activé | Libère RAM des modèles inactifs |

**4 —** Cliquer "Start Server" → API sur `http://localhost:1234/v1`

**5 —** Réduire LM Studio dans le Dock — le serveur continue de tourner.

### Dépannage : Erreur "No LM Runtime found" (Multi-Session)

Si vous utilisez LM Studio sur une **session macOS différente** de celle où il a été installé, vous rencontrerez l'erreur :
`Failed to load the model: No LM Runtime found for model format 'gguf' (ou 'safetensors')!`

**Explication :** L'application est installée globalement, mais les moteurs d'inférence (runtimes) sont téléchargés silencieusement dans un dossier caché propre à chaque utilisateur (`~/.cache/lm-studio/`). La nouvelle session n'a donc pas le moteur.

**Solution (Méthode 1) :**
1. Ouvrez LM Studio sur la nouvelle session Admin.
2. Cliquez sur l'icône **Dossier (Local Models)** ou **Paramètres** (engrenage) sur la barre latérale gauche.
3. Cherchez la section **"Runtimes"** (souvent située dans le panneau de gauche ou sous Advanced).
4. Cliquez sur le bouton **"Update"** ou **"Download Runtimes"**.
5. Une fois le téléchargement du moteur terminé, votre modèle GGUF / MLX se chargera normalement.

## 5. Workflow Optimal : Architecture Multi-Agents

Pour maximiser l'efficacité sur M1 Max 64 Go, la stratégie recommandée est de séparer les rôles entre deux modèles spécialisés.

### A. Le Pattern "Agent de terrain vs Spécialiste"

| Rôle | Modèle | Atout | Usage |
| :--- | :--- | :--- | :--- |
| **L'Agent (Outils)** | **Qwen 3.6 35B MLX** | Fiabilité JSON / Tools | Filesystem, Git, MCP, Recherche Web, Application de code. |
| **Le Spécialiste** | **DeepSeek R1 70B GGUF** | Raisonnement pur | Algorithmes complexes, Debug critique, Architecture. |

### B. Déroulement du Workflow "Relais" dans VS Code

Le contexte (fichiers lus, logs, résultats web) est lié au **fil de discussion du chat** et non au modèle.

1. **Phase d'Exploration (Agent)** : Utilisez Qwen pour fouiller le code, utiliser MCP et rassembler le contexte.
2. **Phase de Réflexion (Spécialiste)** : Switchez sur DeepSeek R1 dans VS Code. Il reçoit tout l'historique et résout le problème complexe sans avoir à gérer les outils (qu'il maîtrise moins bien).
3. **Phase d'Exécution (Agent)** : Revenez sur Qwen pour appliquer les modifications, tester et faire le commit Git.

### C. Synergie Technique (JIT & Spéculatif)

Ce workflow exploite la gestion dynamique de LM Studio :
*   **DeepSeek (Brain)** : Pré-chargé avec son modèle **Draft** → génération instantanée de la pensée.
*   **Qwen (Hands)** : Chargé à la demande via **JIT**. Le format MLX 4-bit garantit un chargement éclair et une exécution native sans saturer les 64 Go de RAM.

> [!TIP]
> Ce workflow "Multi-Modèles" est la configuration la plus avancée possible en local en 2026. Il permet d'allier la puissance de raisonnement d'un 70B à la fiabilité technique d'un agent spécialisé 35B.

---

## 6. Récapitulatif — Quel outil choisir ?

| Scénario | Outil recommandé |
| :--- | :--- |
| **Maximum performance** (KV q8 + spéculatif + contrôle fin) | `launch_ia.sh` (llama-server) |
| **Simplicité + spéculatif + JIT swap + MLX** | **LM Studio GUI** ✅ |
| **Production légère sans spéculatif** | `lms load` + `lms server start` |
| **Tests et exploration de modèles** | LM Studio GUI |

---

## 7. Technologie à Surveiller : SGLang

### Qu'est-ce que SGLang ?

**SGLang** (Structured Generation Language) est un moteur d'inférence haute performance créé par l'équipe **LMSYS** (Berkeley), les mêmes qui ont créé Vicuna et le benchmark Chatbot Arena. Il est conçu comme une alternative de niveau production à `vLLM` et `llama.cpp`, avec une innovation centrale unique : **RadixAttention**.

### La Technologie Clé : RadixAttention

Les moteurs classiques allouent un bloc KV cache indépendant par requête. SGLang utilise un **arbre Radix partagé** qui détecte automatiquement les préfixes communs entre toutes les requêtes simultanées et les mutualise.

**Gain mesuré : jusqu'à 6.4x plus de requêtes traitées par seconde** sur des workloads avec contextes partagés — comme votre usage D-Bot où le SYSTEM prompt est identique pour chaque question.

### Fonctionnalités Uniques (Absentes des Autres Moteurs)

**1 — Génération Structurée Ultra-rapide (xGrammar)**
Force la sortie du modèle à respecter un schéma JSON ou regex, jusqu'à **10x plus rapide** que les méthodes classiques. Très pertinent pour les commandes robot :

```python
# SGLang garantit un JSON valide en sortie — idéal pour D-Bot
{"action": "move_left", "speed": 0.5, "duration": 2.0}
```

**2 — Pipeline Python Natif**
SGLang propose un DSL Python pour des workflows d'inférence complexes (appels parallèles, branchements conditionnels, tool use) :

```python
@sgl.function
def robot_decision(s, sensor_data):
    s += sgl.system("Tu es le cerveau de D-Bot.")
    s += sgl.user(f"Données capteurs : {sensor_data}")
    s += sgl.assistant(sgl.gen("analyse", max_tokens=100))
    s += sgl.user("Décision motrice ?")
    s += sgl.assistant(sgl.gen("decision", choices=["avancer", "reculer", "stop"]))
```

**3 — API OpenAI-compatible**
Le serveur SGLang écoute sur `http://localhost:30000/v1` — Continue et Roo Code peuvent s'y connecter exactement comme avec Ollama ou LM Studio.

### État de Compatibilité Mac M1 (Avril 2026)

| Fonctionnalité | État sur M1 Max |
| :--- | :--- |
| Backend Apple Silicon | ⚠️ Via MLX (expérimental) |
| RadixAttention sur MLX | ❌ Pas encore porté |
| Génération structurée (JSON) | ✅ Disponible |
| Décodage spéculatif | ⚠️ Partiel |
| Performance vs llama.cpp | ❌ Encore inférieure sur M1 |
| API OpenAI-compatible | ✅ `localhost:30000/v1` |

> [!NOTE]
> SGLang est optimisé pour les GPU NVIDIA (H100, A100). Le backend MLX pour Apple Silicon est actif mais encore expérimental en 2026. Les gains de RadixAttention ne sont pas encore disponibles sur M1.

### Verdict pour D-Bot

| Scénario | Recommandation |
| :--- | :--- |
| **Moteur d'inférence principal (Mac)** | ❌ Pas encore — llama.cpp/LM Studio restent supérieurs |
| **Génération de commandes JSON robot** | ✅ Pertinent dès maintenant (côté client Python) |
| **Workloads serveur sur GPU NVIDIA** | ✅ Excellent choix (Jetson AGX Orin par exemple) |
| **Surveillance et adoption future** | ✅ Technologie à intégrer dans 6-12 mois |

> [!TIP]
> Si vous développez des scripts comportementaux Python pour D-Bot (ex: `chatbot_local.py`) qui génèrent des commandes structurées pour les moteurs RobStride, la **bibliothèque cliente SGLang** peut être utilisée dès maintenant en se connectant à votre LM Studio ou llama-server existant.

```bash
# Installation du client SGLang (sans le serveur complet)
pip install sglang
```

---

*Document créé en Avril 2026 — Architecture IA D-Bot.*

