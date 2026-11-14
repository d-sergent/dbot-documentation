# 💻 Guide Référence : IA Locale sur MacBook Pro M1 Max (64 Go)

> [!NOTE]
> Ce guide synthétise le socle actif d'inférence locale retenu sur Mac M1 Max (`64 Go` de RAM unifiée, `~400 Go/s`). Il remplace les anciens guides de mai 2026 archivés dans [Archives](./Archives/) (`01_` à `54_`, exclus automatiquement de LightRAG).
> Pour l'architecture détaillée des modèles (`Gated DeltaNet`, `MTP`, calibration sampling) et les mesures empiriques sur le dépôt, voir [55_Rapport_Expert_Qwen38_Unsloth_M1Max.md](./55_Rapport_Expert_Qwen38_Unsloth_M1Max.md) et [56_Plan_Deploiement_Tests_Qwen38_LightRAG.md](./56_Plan_Deploiement_Tests_Qwen38_LightRAG.md).

---

## 📑 Sommaire

- [1. Architecture Retenue](#1-architecture-retenue)
- [2. Modèles Viables Conservés](#2-modèles-viables-conservés)
- [3. Exclusions Actées](#3-exclusions-actées)
- [4. Réglages Système M1 Max](#4-réglages-système-m1-max)
- [5. Commandes et Nettoyage Disque](#5-commandes-et-nettoyage-disque)

---

## 1. Architecture Retenue

La station locale repose sur **deux moteurs complémentaires uniquement**, pilotés depuis **Antigravity / Kilo** ([kilo.jsonc](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/.kilo/kilo.jsonc)) et le serveur MCP `dbot-rag` :

| Moteur | Port / Stockage | Rôle principal dans D-Bot |
| :--- | :--- | :--- |
| **Ollama (`0.40.16+` MLX)** | `http://127.0.0.1:11434`<br>Modèles : `/Users/Shared/ollama-models` | Moteur principal d'indexation et de requêtes LightRAG (`index_docs.py`, `mcp_lightrag_server.py`), gagnant de la campagne `p1_c1600`, et usage interactif rapide sans friction. |
| **Unsloth Studio (`llama-server`)** | `http://127.0.0.1:8888/v1`<br>Modèles : `~/.cache/huggingface/hub` | Moteur agentique haute fidélité (Tool Healing, raisonnement) et audit **Vision CAO** (`mmproj-F16.gguf`) sur [Visual_Snapshots](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots). |

---

## 2. Modèles Viables Conservés

Le catalogue actif est volontairement restreint à **trois profils complémentaires** tenant confortablement en mémoire unifiée avec Fusion 360 ouvert :

| Rôle | Modèle & Tag | Moteur | Empreinte | Usage recommandé |
| :--- | :--- | :--- | :--- | :--- |
| **Principal (Code, RAG, Raisonnement & VLM)** | `unsloth/Qwen3.8-27B-GGUF` (`UD-Q4_K_XL` + `mmproj-F16.gguf`) | Unsloth Studio (`:8888`) | ~`19 Go` (+ vision) | Orchestration agentique Kilo, appels outils MCP, analyse schémas/captures CAO. |
| **Principal MLX (RAG & Débit)** | `qwen3.8:27b-mlx` | Ollama MLX (`:11434`) | `18 Go` | Indexation/synthèse LightRAG, inférence MLX native rapide sur M1 Max. |
| **Challenger Vitesse (MoE)** | `gemma4:26b` (`26B-A4B nvfp4`, `4B` actifs) | Ollama MLX (`:11434`) | `16 Go` | Itérations conversationnelles rapides quand la latence prime sur le raisonnement dense profond. |
| **Poids Plume Utilitaire** | `qwen3.5:9b` | Ollama (`:11434`) | `7,6 Go` | Tâches légères en arrière-plan, classification rapide et repli minimal en VRAM. |

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
  - **Modèles massifs `70B` à `120B+`** (`DeepSeek-R1-Distill-Llama-70B`, `Llama 4 Scout`) : `37` à `43 Go` de poids laissant trop peu de marge pour le KV cache, macOS et Fusion 360 sur `64 Go`, avec un débit limité par la bande passante mémoire (`~400 Go/s`).
  - **Anciennes générations remplacées** : `Qwen 3.6`, `DeepSeek-R1 32B`, `Gemma 4 31B Dense` (redondant face à `Qwen3.8-27B`), `Nemotron Omni`, `MiniMax M2.7`.

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
