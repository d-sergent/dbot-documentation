# 💻 Guide Référence : IA Locale sur MacBook Pro M1 Max (64 Go)

> [!NOTE]
> Ce guide synthétise le socle actif d'inférence locale retenu sur Mac M1 Max (`64 Go` de RAM unifiée, `~400 Go/s`). Il remplace les anciens guides de mai 2026 archivés dans [Archives](./Archives/) (`01_` à `54_`, exclus automatiquement de LightRAG).
> Pour l'architecture détaillée des modèles (`Gated DeltaNet`, `MTP`, calibration sampling), les mesures empiriques et la veille robotique complète, voir [55_Rapport_Expert_Qwen38_Unsloth_M1Max.md](./55_Rapport_Expert_Qwen38_Unsloth_M1Max.md), [56_Plan_Deploiement_Tests_Qwen38_LightRAG.md](./56_Plan_Deploiement_Tests_Qwen38_LightRAG.md) et [57_Veille_et_Benchmark_Modeles_Robotique_Ollama_Unsloth.md](./57_Veille_et_Benchmark_Modeles_Robotique_Ollama_Unsloth.md).

---

## 📑 Sommaire

- [1. Architecture Retenue](#1-architecture-retenue)
- [2. Modèles Viables Conservés](#2-modèles-viables-conservés)
  - [2.1 Compléments Spécialisés et Pont Robotique](#21-compléments-spécialisés-et-pont-robotique)
  - [2.2 Matrice Pratique d'Usage : Qwen3.8-27B vs Gemma 4 26B](#22-matrice-pratique-dusage--qwen38-27b-vs-gemma-4-26b)
- [3. Exclusions Actées](#3-exclusions-actées)
- [4. Réglages Système M1 Max](#4-réglages-système-m1-max)
- [5. Commandes et Nettoyage Disque](#5-commandes-et-nettoyage-disque)

---

## 1. Architecture Retenue

La station locale repose sur **deux moteurs complémentaires uniquement**, pilotés depuis **Antigravity / Kilo** ([kilo.jsonc](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/.kilo/kilo.jsonc)) et le serveur MCP `dbot-rag` :

| Moteur | Port / Stockage | Rôle principal dans D-Bot |
| :--- | :--- | :--- |
| **Ollama (`0.40.17+` MLX)** | `http://127.0.0.1:11434`<br>Modèles : `/Users/Shared/ollama-models` | Moteur principal d'indexation (`qwen3.8:27b-mlx`), requêtes QA rapides (`gemma4:26b`), et usage interactif / vocal déporté sans friction. |
| **Unsloth Studio (`llama-server`)** | `http://127.0.0.1:8888/v1`<br>Modèles : `~/.cache/huggingface/hub` | Moteur agentique haute fidélité (Tool Healing, raisonnement) et audit **Vision CAO** (`mmproj-F16.gguf`) sur [Visual_Snapshots](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots). |

---

## 2. Modèles Viables Conservés

Le catalogue actif est volontairement restreint à **trois profils complémentaires** tenant confortablement en mémoire unifiée avec Fusion 360 ouvert :

| Rôle | Modèle & Tag | Moteur | Empreinte | Usage recommandé |
| :--- | :--- | :--- | :--- | :--- |
| **Principal (Code, RAG, Raisonnement & VLM)** | `unsloth/Qwen3.8-27B-GGUF` (`UD-Q4_K_XL` + `mmproj-F16.gguf`) | Unsloth Studio (`:8888`) | ~`19 Go` (+ vision) | Orchestration agentique Kilo, appels outils MCP, analyse schémas/captures CAO. |
| **Principal MLX (RAG & Débit)** | `qwen3.8:27b-mlx` | Ollama MLX (`:11434`) | `18 Go` | Indexation/synthèse LightRAG, inférence MLX native rapide sur M1 Max. |
| **Agent Vocal, QA & VLM Rapide (MoE)** | `gemma4:26b` (`26B-A4B nvfp4`, `~4B` actifs) | Ollama MLX (`:11434`) | `16 Go` (`18,28 GiB` VRAM) | **Validé Banc A (`15/15`, `67,9 tok/s`, `TTFT` QA `0,43 s`)** : dialogue vocal déporté, tool calling ROS 2 rapide et synthèse QA ; **`NO-GO` en indexation LightRAG** (`-67,4 %` d'arêtes). |
| **Poids Plume Utilitaire** | `qwen3.5:9b` | Ollama (`:11434`) | `7,6 Go` | Tâches légères en arrière-plan, classification rapide et repli minimal en VRAM. |

### 2.1 Compléments Spécialisés et Pont Robotique

Des options spécialisées sont documentées et cadrées dans [57_Veille_et_Benchmark_Modeles_Robotique_Ollama_Unsloth.md](./57_Veille_et_Benchmark_Modeles_Robotique_Ollama_Unsloth.md) sans alourdir le socle permanent :

- **Code lourd ponctuel (Mac `64 Go`, Fusion 360 fermé)** : `unsloth/Qwen3-Coder-Next-GGUF` en **`UD-Q3_K_XL`** (`~33–38 Go`, `80B-A3B`, sans vision ; éviter `UD-Q4` à `~46–50 Go` qui frôle le swap SSD).
- **Vision Spatiale `Active Gaze` légère (Mac)** : `Molmo2-4B` (`~5,4 Go` natif `mlx-vlm`) ou `LocateAnything-3B` (`~4,7 Go` GGUF), alors que `NVIDIA Cosmos-Reason2` (`2B/8B`) vise d'abord l'écosystème NVIDIA CUDA/Jetson AI Lab et ne dispose pas de portage MLX/`Ollama` officiel sur Mac.
- **Upgrade Embarqué Jetson Orin Nano `8 Go` (hors-ligne, marge `2,60 Go`)** : **`lfm3:1.7b`** (ou `lfm2.5:1.2b`), **`qwen3.5:2b`** et le micro-routeur **`functiongemma`** (`270M`, `~288 Mo`, fine-tunable Unsloth) en remplacement de `qwen2.5:0.5b` ([47_Cerveau_IA_Ollama_LLM.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/jetson/brain/47_Cerveau_IA_Ollama_LLM.md)).

### 2.2 Matrice Pratique d'Usage : Qwen3.8-27B vs Gemma 4 26B

| Cas d'usage concret D-Bot | Modèle & Moteur à utiliser | Pourquoi (mesuré) | Exemple direct |
| :--- | :--- | :--- | :--- |
| **Indexation graphe LightRAG & intégrité** | **Gemini Free Tier (cascade complète) -> repli local `qwen3.8:27b-mlx`** | Cascade cloud complète d'abord (`auto`), puis seul modèle local à `0` erreur `<\|#\|>` (`gemma4:26b` = `-67,4 %` d'arêtes). | `index_docs.py --update` (`--provider ollama` pour forcer local) |
| **Code complexe, FEA & Tool Healing** | **`unsloth/Qwen3.8-27B-GGUF`** (`UD-Q4_K_XL` sur `:8888`) | Mode `Thinking` + auto-réparation JSON MCP/Kilo (`Terminal-Bench 73,0`, `LiveCodeBench 90,3`). | Profil `unsloth-qwen38` dans Kilo / `unsloth studio run` |
| **Dialogue vocal déporté & commandes ROS 2** | **`gemma4:26b`** (`Ollama :11434`) | `TTFT` chaud `~0,43–0,60 s`, `67,9 tok/s`, `5/5` tool calling JSON strict (`2,94×` plus rapide). | `DbotBrainStreaming(model_name="gemma4:26b")` |
| **Synthèse QA rapide sur extraits RAG** | **Gemini Free Tier (`3.8-flash` -> ...) -> repli local `gemma4:26b`** | Priorité cloud Free Tier en `auto`, sinon repli local `1,12 s` par réponse (`2,81×` plus rapide, `5/5` exactitude cotes). | `ask_rag.py "..."` (ou `--provider ollama` pour local direct) |
| **Audit visuel CAO / FEA ponctuel** | **`gemma4:26b`** (rapide, `6,16 s`) ou **`Qwen3.8-27B`** (dense critique) | `gemma4:26b` donne un `100 %` OCR/spatial en `2,32×` moins de temps ; garder `Qwen3.8` (`mmproj-F16`) pour les vues d'assemblage très chargées en `Thinking`. | Vision via Ollama (`gemma4:26b`) ou Unsloth `:8888` (`Qwen3.8`) |

---

## 3. Exclusions Actées

Pour éviter les crashs Metal, le swap SSD et la dispersion documentaire, les options suivantes sont définitivement écartées du socle actif :

- **Moteurs retirés** :
  - **vMLX / MLX Studio** : écarté après l'échec mesuré en Piste C (`1096,76 s`, bug `BatchMambaCache.extend()`, `block-disk-only` — voir [56_Plan_Deploiement_Tests_Qwen38_LightRAG.md](./56_Plan_Deploiement_Tests_Qwen38_LightRAG.md)).
  - **LM Studio / `llmster` & Jan** : redondants avec le duo Ollama MLX + Unsloth Studio.
  - **SGLang** : non mature sur Apple Silicon (`RadixAttention` absent sous MLX).
  - **VS Code + Continue / Roo Code / LanceDB** : remplacés par **Antigravity / Kilo** et **LightRAG MCP**.
- **Modèles & formats retirés** :
  - **Quantifications `2-bit`** (`JANG_2L`, `JANG_2S`, ex. `Mistral-Small-4-119B-A6B-JANG_2L`, `Qwen3.5-122B-A10B-JANG_2S`) : perte de rigueur sur le code, la syntaxe XML/JSON et les cotes mécaniques, et instabilité Metal sur longs contextes.
  - **Modèles massifs `70B` à `550B+`** (`DeepSeek-R1-Distill-Llama-70B`, `Llama 4 Scout`, `Qwen3.8-Flash-Next` `176B` à `~80–94 Go`, `DeepSeek-V4.1-Flash` `~500 Go`, `GLM-5.3-Flash` `320B`, `Nemotron 3.5 Super VL` `120B` et `Bolt` `74B`) : dépassent le plafond GPU Metal (`56 GiB`) ou saturent les `64 Go` sans offload SSD ni swap SSD avec Fusion 360 / LightRAG.
  - **Anciennes générations & MoE intermédiaires redondants** : `Qwen 3.6`, `Qwen3.5/3.6-35B-A3B` (battu en code terminal par `Qwen3.8-27B`), `GLM-4.7-Flash` et `Nemotron-3-Nano` `30B` (texte seul, redondants face à `gemma4:26b` MLX `16 Go`), `DeepSeek-R1 32B`, `Gemma 4 31B Dense`, `Nemotron Omni`, `MiniMax M2.7`.
  - **`inkling-2-mini:26b-a5b-nvfp4`** (*Thinking Machines Lab*, `26,4B` *looped MoE*) : retiré après échec mesuré au **Banc A** sous Ollama `0.40.17` (`18,1 tok/s` decode, `356,29 s` cumulés soit `7,17×` plus lent que `gemma4:26b`, `24,38 GiB` VRAM `ollama ps`, `0/5` `tool_calls` natifs hors Thinking, et comptage erroné `"9"` en Vision `V2`).
  - **Embeddings LightRAG** : `EmbeddingGemma 2` non retenu face à `bge-m3` (`1024-dim`) déjà indexé.

---

## 4. Réglages Système M1 Max

Par défaut, macOS plafonne la mémoire GPU câblée (`wired`) autour de `70` à `80 %` de la RAM totale (`~48 Go` sur `64 Go`). Pour autoriser jusqu'à `56 Go` au GPU lors des grosses sessions tout en gardant `8 Go` vitaux pour macOS :

```bash
# Vérifier le plafond actuel (en Mo)
sysctl iogpu.wired_limit_mb

# Relever temporairement le plafond à 56 Go (56 * 1024 = 57344)
sudo sysctl iogpu.wired_limit_mb=57344
```

> [!CAUTION]
> Ne jamais relever `iogpu.wired_limit_mb` à `64 Go` (`100 %` de la RAM) : macOS doit impérativement conserver `4` à `8 Go` libres pour éviter un gel complet ou un redémarrage noyau.

---

## 5. Commandes et Nettoyage Disque

### Maintenance Ollama courante

```bash
# Lister les modèles actifs (stockés sous /Users/Shared/ollama-models)
ollama list

# Supprimer un modèle inutilisé
ollama rm <nom_du_modele>

# Inspecter le template/Modelfile d'un modèle existant
ollama show --modelfile qwen3.8:27b-mlx

# Exécuter un GGUF Hugging Face directement si besoin ponctuel
ollama run hf.co/<auteur>/<depot-gguf>
```

### Règles de vigilance avant nettoyage du cache Hugging Face (`~/.cache/huggingface/hub`)

Lors des purges de caches modèles obsolètes (`JANGQ-AI`, `OsaurusAI`, `dealignai`, `lmstudio-community`, `mlx-community`, `ncls-p`, `~/.lmstudio`, `Jan`, `/Users/Shared/IA`), **conserver impérativement** :

1. **`~/.cache/huggingface/hub/models--unsloth--Qwen3.8-27B-GGUF`** : poids `UD-Q4_K_XL`, `MTP` et `mmproj-F16.gguf` servis par Unsloth Studio (`:8888`).
2. **`~/.cache/huggingface/hub/models--docling-project--*`** : modèles `Docling / TableFormer` utilisés par [index_docs.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py) pour l'extraction des PDF techniques.
3. **Modèles vocaux D-Bot (`faster-whisper`, `Qwen3-TTS`, `F5-TTS`)** : vérifier leur usage dans les pipelines audio avant suppression.
