# 🧭 Veille & Benchmark Modèles Complémentaires Robotique D-Bot (Ollama MLX & Unsloth — Nov. 2026)

> [!NOTE]
> Document de référence complémentaire à [00_GUIDE_IA_Locale_M1Max_64Go.md](./00_GUIDE_IA_Locale_M1Max_64Go.md), [55_Rapport_Expert_Qwen38_Unsloth_M1Max.md](./55_Rapport_Expert_Qwen38_Unsloth_M1Max.md) et [56_Plan_Deploiement_Tests_Qwen38_LightRAG.md](./56_Plan_Deploiement_Tests_Qwen38_LightRAG.md).
> Il évalue systématiquement les nouveaux modèles **Ollama (`0.40.16+`)** et **Unsloth (Dynamic V3.1 GGUF / QAT / LoRA)** au regard des contraintes matérielles exactes de D-Bot : station **MacBook Pro M1 Max `64 Go`**, robot **Jetson Orin Nano Super `8 Go`**, et pipeline spatial **Active Gaze**.

---

## 📑 Sommaire

- [1. Verdict Exécutif par Étage Matériel](#1-verdict-exécutif-par-étage-matériel)
- [2. Architecture Matérielle D-Bot et Contraintes Réelles](#2-architecture-matérielle-d-bot-et-contraintes-réelles)
  - [2.1 Station Compagnon Mac M1 Max 64 Go](#21-station-compagnon-mac-m1-max-64-go)
  - [2.2 Cerveau Embarqué Jetson Orin Nano Super 8 Go](#22-cerveau-embarqué-jetson-orin-nano-super-8-go)
  - [2.3 Frontière Stricte avec la Commande Temps Réel](#23-frontière-stricte-avec-la-commande-temps-réel)
- [3. Optimisation Réelle Ollama MLX versus Unsloth Studio](#3-optimisation-réelle-ollama-mlx-versus-unsloth-studio)
- [4. Évaluation des Candidats Mac M1 Max 64 Go](#4-évaluation-des-candidats-mac-m1-max-64-go)
  - [4.1 Comparatif Consolidé Mac](#41-comparatif-consolidé-mac)
  - [4.2 Arbitrage RAG Embeddings LightRAG](#42-arbitrage-rag-embeddings-lightrag)
- [5. Évaluation des Candidats Embarqués Jetson Orin Nano 8 Go](#5-évaluation-des-candidats-embarqués-jetson-orin-nano-8-go)
  - [5.1 Les Faux Amis Mémoire à Écarter en Concurrence](#51-les-faux-amis-mémoire-à-écarter-en-concurrence)
  - [5.2 Les Trois Modèles Recommandés sous 2,60 Go de Marge](#52-les-trois-modèles-recommandés-sous-260-go-de-marge)
- [6. Raisonnement Spatial et Vision Physique Active Gaze](#6-raisonnement-spatial-et-vision-physique-active-gaze)
- [7. Protocole de Benchmarks et Commandes Prêtes](#7-protocole-de-benchmarks-et-commandes-prêtes)
  - [7.1 Banc A Mac Gemma 4 26B versus Qwen3.8 27B MLX](#71-banc-a-mac-gemma-4-26b-versus-qwen38-27b-mlx)
  - [7.2 Banc B Jetson Orin Nano LFM3 versus Qwen3.5 2B](#72-banc-b-jetson-orin-nano-lfm3-versus-qwen35-2b)
  - [7.3 Commandes de Téléchargement et Test en 1 Clic](#73-commandes-de-téléchargement-et-test-en-1-clic)

---

## 1. Verdict Exécutif par Étage Matériel

1. **Station Mac M1 Max `64 Go` (Cerveau RAG, Code, Tool Calling & VLM CAO)** :
   - **Le socle principal actuel (`qwen3.8:27b-mlx` + `unsloth/Qwen3.8-27B-GGUF UD-Q4_K_XL`) reste la référence optimale** pour la fiabilité agentique, le JSON tool calling strict et l'analyse technique. Aucun méga-MoE récent (`Qwen3.8-Flash-Next`, `DeepSeek-V4.1-Flash`, `GLM-5.3-Flash`) ne tient proprement dans `64 Go` de RAM unifiée sans casser la marge mémoire Metal (`51,3 GiB` par défaut, `56 GiB` relevable).
   - **Modèle déjà présent à benchmarker en priorité** : **`gemma4:26b`** (`16 GB`, `26,2B` MoE à seulement `~4B` paramètres actifs par token, `nvfp4`) est déjà installé localement mais non encore mesuré face à `qwen3.8:27b-mlx` dans [56_Plan_Deploiement_Tests_Qwen38_LightRAG.md](./56_Plan_Deploiement_Tests_Qwen38_LightRAG.md). Il constitue le meilleur candidat pour un **agent vocal/multimodal déporté à latence minimale**.
   - **Complément code pur ciblé** : **`Qwen3-Coder-Next`** (`80B-A3B`) uniquement en quantification Unsloth **`UD-Q3_K_XL`** (`~33–38 Go`) pour du refactoring lourd ROS 2 / C++ (en fermant Fusion 360).
2. **Jetson Orin Nano Super `8 Go` (Cerveau Embarqué Hors-Ligne & Routage ROS 2)** :
   - **C'est le véritable point d'amélioration immédiat.** Le fallback hors-ligne codé dans [async_conversation.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/brain/async_conversation.py) et [llm_client.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/brain/llm_client.py) utilise encore **`qwen2.5:0.5b`**, et la note [47_Cerveau_IA_Ollama_LLM.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/jetson/brain/47_Cerveau_IA_Ollama_LLM.md) référence d'anciens modèles de mai 2026 (`qwen2.5:3b`, `nemotron-mini`, `gemma3:4b`).
   - Sous la contrainte réelle des **`2,60 Go` de marge VRAM** disponible en mode robotique complet, **`Liquid LFM3` (`lfm3:1.7b`)** et **`Qwen3.5:2b`** (ainsi que **`FunctionGemma 270M`** fine-tuné via Unsloth en micro-routeur) apportent un saut net de vitesse et de fiabilité sans risque de swap.
3. **Couche Vision Spatiale & Physique (`Active Gaze` Mac)** :
   - `NVIDIA Cosmos-Reason2` (`2B` / `8B`) est nativement optimisé pour l'écosystème **NVIDIA Jetson AI Lab / CUDA / vLLM**, pas pour Apple Silicon MLX ni la bibliothèque Ollama standard. Sur Mac, **`LocateAnything-3B`** (`llama.cpp` GGUF) et **`Molmo2-4B`** (natif `mlx-vlm`, `~5,4 Go`) sont plus simples à déployer en daemon léger si `qwen3.8:27b-mlx` doit être soulagé.

---

## 2. Architecture Matérielle D-Bot et Contraintes Réelles

### 2.1 Station Compagnon Mac M1 Max 64 Go

- **Matériel vérifié** : `MacBookPro18,2`, Apple M1 Max (`10` cœurs CPU), `64 Go` de RAM unifiée (`~400 Go/s` de bande passante mémoire), limite câblée GPU Metal par défaut à `~51,3 GiB` (relevable temporairement à `56 GiB` via `sysctl iogpu.wired_limit_mb=57344`, voir [00_GUIDE_IA_Locale_M1Max_64Go.md](./00_GUIDE_IA_Locale_M1Max_64Go.md)).
- **Inventaire Ollama `0.40.16` et Unsloth relevé** :
  - `qwen3.8:27b-mlx` (`18 GB`, architecture `qwen3_5`, `27,8B` paramètres, `nvfp4`, contexte `262144`, vision + tools + thinking ; mesuré à `32,3 tok/s` en décodage et `144,4 tok/s` en prefill avec `68,5 %` d'acceptation MTP native et `27,57 GiB` de pic RAM).
  - `gemma4:26b` (`16 GB`, architecture `gemma4`, `26,2B` paramètres MoE `A4B`, `nvfp4`, contexte `262144`, vision + tools + thinking).
  - `qwen3.5:9b` (`7,6 GB`, architecture `qwen3_5`, `9,7B` paramètres, `nvfp4`, `draft_num_predict 3`, contexte `262144`).
  - Unsloth Studio (`~/.unsloth/`, intégrant `llama.cpp`, `whisper.cpp`, `audio.cpp` sur `:8888`) : `unsloth/Qwen3.8-27B-GGUF` (`UD-Q4_K_XL` + `mmproj-F16.gguf`, Dynamic V3.1, tool healing testé en `8,67 s`).

### 2.2 Cerveau Embarqué Jetson Orin Nano Super 8 Go

D'après [FINAL_Architecture_Master_V1_Hybride.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/05_Gestion_Projet/FINAL_Architecture_Master_V1_Hybride.md) et [FINAL_Bilan_Ressources_et_Calcul.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/00_Architecture_Centrale/FINAL_Bilan_Ressources_et_Calcul.md) :

- Mémoire utile totale en headless (`67 TOPS`, ROS 2 Humble, JetPack `6.2.1`) : **`5,50 Go`**.
- Consommation des briques perception / audio actives : `OAK-D Pro FF` + `YOLO-World v2 TensorRT` (`0,40 Go`) + `face_tracker` (`< 0,10 Go`) + `Faster-Whisper small` (`1,50 Go`) + buffers/OS (`1,00 Go`) = **`2,90 Go`**.
- **Marge VRAM restante maximale : `2,60 Go`** (et encore plus réduite lorsqu'une politique motrice `LeRobot ACT TensorRT 0,80 Go` s'exécute simultanément).
- Conséquence physique impérative : tout dépassement vers le swap NVMe/eMMC effondre l'inférence à **`< 2 tok/s`** sur Orin Nano.

### 2.3 Frontière Stricte avec la Commande Temps Réel

Les boucles d'asservissement et de perception rapide restent intégralement hors LLM :

- **Bas niveau `100–500 Hz`** : `Pinocchio` (`G(q)` dynamique inverse) et trames CAN-FD MIT sur les `2x Teensy 4.1`, politiques visuomotrices **`LeRobot` (`ACT / Diffusion Policy`)**, détection `80–120 FPS` **`YOLO-World v2 TensorRT`** ([FINAL_Pipeline_Vision.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/04_Perception_et_Sensors/FINAL_Pipeline_Vision.md)).
- **Rôle exclusif des modèles Ollama / Unsloth** : dialogue vocal, extraction d'intentions et appels d'outils structurés ROS 2 / MCP, raisonnement physique haut niveau (`Active Gaze`), synthèse RAG (`LightRAG`) et développement logiciel.

---

## 3. Optimisation Réelle Ollama MLX versus Unsloth Studio

| Critère Technique | Ollama `0.40.16` (Apple MLX + `nvfp4`) | Unsloth Studio (`~/.unsloth/llama.cpp` + Dynamic V3.1) | Impact Pratique pour D-Bot |
| :--- | :--- | :--- | :--- |
| **Exploitation M1 Max (`~400 Go/s`)** | Kernels Metal JIT via **Apple MLX** avec déquantification `nvfp4` à la volée (sans cœurs Tensor FP4 matériels, mais moitié moins d'erreur de quantification que `Q4_K_M`). | Exécution `llama.cpp` Metal sur poids GGUF mixtes (`UD-Q4_K_XL`, `UD-Q3_K_XL`). | **Ollama MLX** garde l'avantage en débit pur et gestion unifiée sur M1 Max. |
| **Décodage Spéculatif MTP** | **MTP natif intégré** sur `qwen3.8:27b-mlx` (`68,5 %` d'acceptation mesurée, `32,3 tok/s`) et `qwen3.5:9b` (`draft_num_predict 3`). | Sur `llama.cpp` Metal Apple Silicon, l'ajout d'une tête draft MTP séparée (`--spec-draft`) provoque fréquemment une **régression de débit en `tok/s`** (bande passante additionnelle du draft). | Privilégier **Ollama MLX** pour la vitesse MTP sur Mac ; en `llama.cpp` pur, préférer les GGUF mono-fichier sans draft externe pour la vitesse brute. |
| **Qualité Agentique & Tool Calls** | Parsers natifs intégrés par famille (`parser qwen3.5`, `gemma4`, `lfm3`). | **Quantification sélective Dynamic V3.1** (couches d'attention critiques gardées en haute précision) + proxy d'auto-réparation (`Tool Healing`) sur `:8888`. | **Unsloth Studio** reste pertinent pour les sessions agentiques complexes sous Kilo ou les quants `UD-Q3_K_XL` optimisées. |
| **Fine-tuning & Robotique** | Consommation uniquement (via `Modelfile` ou `hf.co/...`). | **Support officiel LoRA / QLoRA** + export direct GGUF (`FunctionGemma`, `Gemma 4`, `Qwen3.5`, `Nemotron-3-Nano`, `Cosmos-Reason1-7B`). | Point fort exclusif d'**Unsloth** pour spécialiser de petits routeurs d'actions D-Bot (`FunctionGemma 270M` ou `Qwen3.5-2B`). |

---

## 4. Évaluation des Candidats Mac M1 Max 64 Go

### 4.1 Comparatif Consolidé Mac

| Modèle & Source | Architecture & Paramètres | Empreinte RAM (`64 Go` Mac) | Débit & Comportement Stack | Statut & Justification |
| :--- | :--- | :--- | :--- | :--- |
| **`qwen3.8:27b-mlx`**<br>(`unsloth/Qwen3.8-27B-GGUF`) | `27,8B` dense (`qwen3_5`), vision + tools + thinking | `18 Go` (`27,6 GiB` pic MLX) | `32,3 tok/s` mesurés (MTP `68,5 %`) ; `LiveCodeBench v6 : 90,3`, `Terminal-Bench 2.1 : 73,0` ; ~`95–96 %` fiabilité JSON | **CONSERVER (Référence Maître)** — Optimal pour LightRAG, outils MCP stricts et audit code/CAO. |
| **`gemma4:26b`**<br>(`unsloth/gemma-4-26B-A4B-it-GGUF`) | `26,2B` MoE (**~4B actifs**), vision + tools + thinking | `16 Go` (`nvfp4` MLX) | `35 à 75+ tok/s` sur Apple Silicon Max grâce aux ~4B actifs ; natif Ollama MLX + Unsloth QAT | **TESTER EN PRIORITÉ (Déjà installé)** — Meilleur candidat pour le dialogue robot déporté à faible latence si le tool calling ROS 2 valide le seuil de qualité. |
| **`LFM2.5-24B-A2B`**<br>(`lfm2.5:24b`) | `24B` hybride MoE (**~2,45B actifs**, LIV + GQA), `<think>` | `~15 Go` (`Q4`) | Très rapide (jusqu'à `~184 tok/s` rapportés sur M5 Max) ; `LiveClaw : 48,09` (vs `38,19` `Qwen3.6-35B-A3B`) ; **texte uniquement**, `llama.cpp` Metal | **OPTIONNEL** — Excellent pur routeur d'outils couplé à RAG, mais sans vision et moins polyvalent en code que `qwen3.8:27b-mlx` ou `gemma4:26b`. |
| **`Qwen3-Coder-Next`**<br>(`unsloth/Qwen3-Coder-Next-GGUF`) | `80B` MoE (**3B actifs**) + Gated DeltaNet | `~33–38 Go` (`UD-Q3_K_XL`)<br>`~46–50 Go` (`UD-Q4`) | `UD-Q3_K_XL` : `22–35 tok/s` estimés sur M1 Max ; `UD-Q4` : `15–22 tok/s` avec risque de swap SSD ; **sans vision** | **COMPLÉMENT CODE PUR** — Utile uniquement pour gros chantiers multi-fichiers ROS 2 / C++ en fermant Fusion 360 (`UD-Q3_K_XL` obligatoire sur `64 Go`). |
| **`Nemotron-3-Nano` 30B**<br>(`nemotron-3-nano`) | `31,6B` Mamba-Transformer MoE (`~3,5B` actifs) | `~21–24 Go` (`Q4_K_M`) | `50+ tok/s` sur M-series Max ; KV cache Mamba minimal sur très longs contextes ; texte seul | **ÉCARTER EN ROUTINE** — Plus lourd et sans vision face à `gemma4:26b` (`16 Go` MLX `nvfp4`). |
| **`GLM-4.7-Flash`**<br>(`glm-4.7-flash`) | `~30B` MoE (`~3,6B` actifs) | `~17–19 Go` | `45–75 tok/s` ; texte seul ; frictions documentées entre mode thinking et schémas JSON stricts | **ÉCARTER** — Redondant et sans apport face au tandem Qwen3.8 / Gemma 4 26B. |
| **`Qwen3.5/3.6-35B-A3B`** | `35B` MoE (`3B` actifs) | `~19–24 Go` | Plus rapide en génération brute, mais nettement battu par `Qwen3.8-27B` sur `LiveCodeBench` (`74,6 / 80,4` vs `90,3`) et `Terminal-Bench` (`40,5 / 51,5` vs `73,0`) | **ÉCARTER** — Moins intelligent que `Qwen3.8-27B` et moins sobre que `Gemma 4 26B`. |
| **`Qwen3.8-Flash-Next`** | `176B` (`125B` MoE + `51B` table PLE N-gram, `6B` actifs) | `~79,6 Go` (`UD-Q2_K_XL`) à `~94 Go` (`UD-IQ4_XS`) | Nécessite offload SSD NVMe de la table PLE (`oMLX` / `llama.cpp` mmap), non natif Ollama/Unsloth standard | **EXCLURE SUR `64 Go`** — Dépasse le plafond GPU Metal (`56 GiB`). |
| **`DeepSeek-V4.1-Flash`** / **`GLM-5.3-Flash`** / **`Nemotron 3.5 Super VL & Bolt`** | `552B+196B` / `320B` / `120B` / `74B-A9B` | `~500 Go` / `>180 Go` / `>70 Go` / `>44 Go` | Réservés aux serveurs multi-GPU ou Mac Studio `192–512 Go` (ou surcharge complète RAM avec contextes longs) | **EXCLURE SUR `64 Go`** — Incompatibles avec une station de travail multi-tâches. |

### 4.2 Arbitrage RAG Embeddings LightRAG

Google propose **`EmbeddingGemma 2`** (multimodal) dans le catalogue Ollama. Toutefois, la base vectorielle LightRAG de D-Bot ([index_docs.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py)) est indexée en **`bge-m3`** (`1024` dimensions, bilingue FR/EN éprouvé). Changer d'embedder obligerait à purger et réindexer l'ensemble des vecteurs existants sans bénéfice avéré sur le corpus français technique. **`bge-m3` reste maintenu.**

---

## 5. Évaluation des Candidats Embarqués Jetson Orin Nano 8 Go

### 5.1 Les Faux Amis Mémoire à Écarter en Concurrence

Sous les **`2,60 Go` de marge VRAM réelle** (capteurs + `YOLO-World TensorRT` + `Faster-Whisper` actifs), trois candidats populaires sur Jetson sont à écarter en fonctionnement concurrent :

1. **`Gemma 4 E2B` (`gemma4:e2b`)** : bien qu'annoncé à `2,3B` effectifs, ses *Per-Layer Embeddings* portent le modèle à **`5,1B` paramètres réels** (`~4,6 Go` sous Ollama standard, `~3,2–4,3 Go` en QAT). Des erreurs CUDA OOM sont documentées sur Orin Nano `8 Go` lorsqu'Ollama charge `mmproj` sur GPU (imposant `llama-server --no-mmproj-offload`). Trop lourd pour cohabiter avec la perception.
2. **`Qwen3.5:4b`** (`~2,5–2,8 Go` en `Q4_K_M`, `~3,3–3,8 Go` VRAM en charge) : excellent équilibre qualité/JSON sur `8 Go` dédié, mais provoque du swap si `Faster-Whisper small` (`1,5 Go`) et `LeRobot ACT` (`0,8 Go`) restent chargés simultanément.
3. **`Nemotron-3-Nano-4B`** (`~2,8–2,9 Go` en `Q4_K_M`, `~3–4 Go` VRAM) : officiellement supporté par **NVIDIA Jetson AI Lab**, mais mesuré à **`12,7 tok/s`** seulement sur Orin Nano `8 Go` via `llama.cpp`, soit trop lent et trop volumineux face aux hybrides convolutifs.

### 5.2 Les Trois Modèles Recommandés sous 2,60 Go de Marge

| Modèle & Tag | Empreinte Disque / VRAM | Débit Jetson Orin | Optimisation Stack (`Ollama` / `Unsloth` / `CUDA`) | Rôle Ciblé D-Bot |
| :--- | :--- | :--- | :--- | :--- |
| **`lfm3:1.7b`** *(ou **`lfm2.5:1.2b`**)* | `~1,1–1,7 Go` Q4 (`~1,5–2,2 Go` VRAM) ; `lfm2.5:1.2b` : `~0,8–1,2 Go` | `100–125+ tok/s` pour `LFM2.5-1.2B` (TTFT `< 50–100 ms`), très élevé pour `LFM3-1.7B` | Architecture tri-hybride économe sur bus LPDDR5 ; entraînée par RL pour appels d'outils ; **parseur `RENDERER/PARSER lfm3` natif Ollama** ; compatible GGUF Unsloth | **RECOMMANDÉ N° 1** — Remplaçant direct de `qwen2.5:0.5b` pour fallback vocal et routage d'outils ROS 2 *(fixer impérativement `num_ctx 2048` à `4096`)*. |
| **`qwen3.5:2b`** | `~1,3–1,6 Go` `Q4_K_M` (`~1,5–2,7 Go` VRAM) | `~18–22 tok/s` vérifiés sur Orin Nano `8 Go` | Cohérence totale avec `Qwen3.8` Mac ; support **Unsloth Dynamic GGUF** ; **vision native early-fusion** incluse | **RECOMMANDÉ N° 2** — À tester si le fallback embarqué doit analyser directement des captures `OAK-D` *(désactiver `<think>` et borner `num_ctx 2048–4096`)*. |
| **`functiongemma`** (`270M`) | `~288 Mo` en 4-bit (`~550 Mo` FP16) | Quelques millisecondes | **Co-optimisé Google + Unsloth** (`unsloth/functiongemma-270m-it-GGUF`) pour QLoRA rapide vers GGUF | **MICRO-AIGUILLEUR ROS 2** — Fine-tunable en quelques minutes sur Unsloth pour convertir des ordres vocaux en JSON ROS 2 sans consommer la VRAM. |

---

## 6. Raisonnement Spatial et Vision Physique Active Gaze

La documentation [FINAL_Pipeline_Vision.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/04_Perception_et_Sensors/FINAL_Pipeline_Vision.md) prévoit un VLM spatial déporté sur Mac (`8–12 Go`) de classe **`NVIDIA Cosmos 3D Edge / LocateAnything-3B`** pour orienter dynamiquement le cou vers des cibles complexes :

- **`NVIDIA Cosmos-Reason2` (`2B` et `8B`)** : modèle dédié à la **physique du monde réel, à la localisation de points 2D/3D et au raisonnement spatio-temporel robotique**.
  - *État d'optimisation stack* : **très bien optimisé sur écosystème NVIDIA (`Jetson AI Lab`, vLLM FP8/W4A16, `llama.cpp` CUDA)**, mais **absence d'optimisation officielle Apple MLX `nvfp4` et absence de tag natif dans la bibliothèque Ollama standard** (nécessite des dépôts GGUF communautaires type `Kbenkhaled/Cosmos-Reason2-8B-GGUF` ou `mradermacher/Cosmos-Reason2-8B-GGUF` via `Modelfile` custom, tandis qu'Unsloth héberge officiellement `unsloth/Cosmos-Reason1-7B`). Sur Jetson Orin Nano `8 Go`, la version `2B` (`~3,8 Go` F16 GGUF, `~4–5 Go` FP8/W4A16) ne peut pas tourner en même temps que `YOLO-World` + `Whisper` + `LeRobot`.
- **`LocateAnything-3B`** (`mudler/locate-anything.cpp-gguf` : `~4,7 Go` en `Q4_K`, `~6,3 Go` en `Q8_0`) : décode les boîtes englobantes en parallèle via `llama.cpp` avec une meilleure précision géométrique que la sérialisation texte séquentielle.
- **`Molmo2-4B`** (`AllenAI`) : porté nativement en **`4-bit` sur `mlx-vlm` (`~5,4 Go`)** pour Apple Silicon ; constitue l'option la plus légère et la mieux optimisée MLX si un **pointeur d'objets visuels permanent** (`~5 Go`) est souhaité aux côtés de `qwen3.8:27b-mlx` ou `gemma4:26b`.
- **Concurrence directe interne** : `qwen3.8:27b-mlx` reposant sur le socle multimodal `qwen3_5`, il gère déjà nativement la localisation 2D/3D et la lecture d'images ; tout VLM spatial séparé doit donc prouver un gain réel de latence ou d'empreinte (`~5 Go` permanent vs `18 Go`) pour justifier sa présence.

---

## 7. Protocole de Benchmarks et Commandes Prêtes

### 7.1 Banc A Mac Gemma 4 26B versus Qwen3.8 27B MLX

Exécuter sur la station Mac (`ollama 0.40.16`, `num_ctx 8192`, température `0,1`, avec **nonce aléatoire en début de prompt système** pour neutraliser le KV prefix cache lors de la mesure TTFT) sur `15` requêtes robotiques réelles :

1. **5 appels d'outils ROS 2 / MCP imbriqués** (taux de JSON strict valide au premier essai, sans prose parasite).
2. **5 questions de synthèse FR issues de `BENCHMARK_QA_DBOT_120`** (exactitude numérique sur tolérances mécaniques et références).
3. **5 analyses visuelles de snapshots CAO / caméra `OAK-D`** (latence TTFT + précision d'identification spatiale gauche/droite).
4. **Métriques enregistrées** : `prompt_eval_count / prompt_eval_duration` (prefill `tok/s`), `eval_count / eval_duration` (décodage `tok/s`), pic RAM unifiée (`Activity Monitor` / `ollama ps`).

### 7.2 Banc B Jetson Orin Nano LFM3 versus Qwen3.5 2B

Exécuter sur la Jetson Orin Nano avec `OAK-D` + `YOLO-World v2 TensorRT` (`0,40 Go`) actifs et **contexte impérativement borné (`num_ctx 2048` puis `4096`)** :

1. Mesurer la marge mémoire instantanée avant/pendant inférence via `sudo tegrastats` (vérifier zéro utilisation swap).
2. Comparer `lfm3:1.7b` (paramètres recommandés Liquid AI : `temperature 0.1`, `top_p 0.1`, `repeat_penalty 1.05`) face à `qwen3.5:2b` (`thinking: false`) et à la ligne de base actuelle `qwen2.5:0.5b` sur `20` commandes vocales robotiques en français.
3. Si `lfm3:1.7b` dépasse `2,2 Go` VRAM sous charge avec `Faster-Whisper small`, tester `lfm2.5:1.2b` (`~0,8–1,2 Go`) ou ajouter un pré-routeur `functiongemma` fine-tuné via Unsloth.

### 7.3 Commandes de Téléchargement et Test en 1 Clic

**Sur Mac M1 Max (le modèle `gemma4:26b` est déjà installé) :**

```bash
ollama ps
```

*(Optionnel — uniquement pour test de refactoring code C++ / ROS 2 lourd sur `64 Go` en fermant Fusion 360, choisir `UD-Q3_K_XL`)* :

```text
unsloth/Qwen3-Coder-Next-GGUF
```

**Sur Jetson Orin Nano Super `8 Go` :**

```bash
ollama pull lfm3:1.7b
```

```bash
ollama pull qwen3.5:2b
```

```bash
ollama pull functiongemma
```

```bash
sudo tegrastats
```
