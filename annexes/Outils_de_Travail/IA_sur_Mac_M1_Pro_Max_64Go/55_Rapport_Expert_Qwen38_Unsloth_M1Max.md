# Rapport d'Expertise — Inférence Locale `Qwen3.8-27B`, Écosystème Unsloth & Accélération du Pipeline LightRAG D-Bot

> **Document de référence D-Bot (`Mac M1 Max 64 Go`)** — Généré le `2026-11-14`  
> **Document compagnon exécutable** : [56_Plan_Deploiement_Tests_Qwen38_LightRAG.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/IA_sur_Mac_M1_Pro_Max_64Go/56_Plan_Deploiement_Tests_Qwen38_LightRAG.md) (Plan détaillé de déploiement et bancs d'essai Points 1, 2 et 3).

> [!IMPORTANT]
> **Verdict Exécutif (Basé sur mesures réelles sur ton Apple M1 Max 64 Go)** :
> 1. **Ton moteur actuel (`Ollama 0.40.16` runner MLX `nvfp4` sur `qwen3.8:27b-mlx`) est déjà hautement optimisé** en mono-flux : l'audit des logs prouve qu'il active nativement le décodage spéculatif **MTP** (`68,5 %` d'acceptation globale, `3,27` tokens acceptés par pas) et un **KV Prefix Cache à `71,3 %`**, atteignant **`144,4 tok/s` en prefill** et **`32,3 tok/s` moyen en décodage** (`27,20 GiB` pic RAM).
> 2. **Pourquoi les `17` chunks FEA prennent `35 min 57 s`** : **`82 %` du temps LLM pur** (`73,9 %` du temps total) vient du décodage **strictement séquentiel** (`llm_model_max_async = 1` dans [`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py#L964-L973)) sur les **2 passes d'extraction** (`entity_extract_max_gleaning = 1`) suivies de `12` fusions — **pas d'une lenteur anormale du moteur**.
> 3. **Alerte qualité critique mesurée** : sur `Calculs_FEA`, la passe 2 de *gleaning* ajoute **`+140` entités (`+59 %`) et `+156` relations (`+73 %`)**. Désactiver le gleaning irait ~`1,7x` plus vite mais amputerait gravement le graphe de connaissances.
> 4. **Ce qu'apporte Unsloth réellement sur Mac versus NVIDIA** : l'accélération **`1,49x NVFP4` (vLLM)** et le fine-tuning **QLoRA `24 Go`** ciblent les GPU **NVIDIA** (Blackwell pour NVFP4, CUDA/T4/RTX pour Flash Linear Attention). Sur ton **M1 Max**, la vraie valeur ajoutée d'Unsloth réside dans ses quants **GGUF Dynamic V3.1 (`+5-10 %` de précision agentique)** avec tête **MTP**, le proxy **`unsloth start` (`:8888`)** avec auto-réparation des tool calls pour le dev D-Bot, et **Data Recipes** pour créer des jeux de tests/benchmarks QA.
> 5. **Le principal levier de vitesse brute pour `index_docs.py` sur M1 Max** consiste à **casser le goulot séquentiel `max_async = 1`** via le **batching continu** (`llama-server` / Unsloth `-np 2..4` ou `vMLX` avec bundle MLX+MTP compatible) combiné à une **optimisation du chunking** (`1200 -> 1600-1800` tokens), tout en réalisant une **séparation nette des paramètres Thinking (code/CAO) vs Non-Thinking (extraction/synthèse RAG)**.

---

## 📑 Sommaire

- [1. Analyse critique des trois documents de référence](#1-analyse-critique-des-trois-documents-de-référence)
  - [1.1 Architecture hybride Gated DeltaNet et Gated Attention de Qwen3.8-27B](#11-architecture-hybride-gated-deltanet-et-gated-attention-de-qwen38-27b)
  - [1.2 Paramètres recommandés Qwen et Unsloth versus pipeline D-Bot actuel](#12-paramètres-recommandés-qwen-et-unsloth-versus-pipeline-d-bot-actuel)
  - [1.3 Dynamic V3.1 GGUF versus NVFP4 Blackwell et état réel de ton cache local](#13-dynamic-v31-gguf-versus-nvfp4-blackwell-et-état-réel-de-ton-cache-local)
- [2. Audit comparatif des moteurs d'inférence sur ton MacBook Pro M1 Max](#2-audit-comparatif-des-moteurs-dinférence-sur-ton-macbook-pro-m1-max)
  - [2.1 Ollama 0.40.16 MLX nvfp4 : la référence mono-flux déjà rapide](#21-ollama-04016-mlx-nvfp4--la-référence-mono-flux-déjà-rapide)
  - [2.2 Unsloth Desktop, Unsloth Studio et llama-server b10639](#22-unsloth-desktop-unsloth-studio-et-llama-server-b10639)
  - [2.3 vMLX 1.6.19 : le candidat batching continu sur MLX natif](#23-vmlx-1619--le-candidat-batching-continu-sur-mlx-natif)
  - [2.4 LM Studio 0.4.18+1 : rôle exploratoire uniquement](#24-lm-studio-04181--rôle-exploratoire-uniquement)
- [3. Ce qu'Unsloth apporte au dépôt D-Bot en général](#3-ce-quunsloth-apporte-au-dépôt-d-bot-en-général)
  - [3.1 Agents de code locaux, tool calling auto-réparateur et vision CAO FEA](#31-agents-de-code-locaux-tool-calling-auto-réparateur-et-vision-cao-fea)
  - [3.2 Data Recipes pour benchmarker et fiabiliser le RAG D-Bot](#32-data-recipes-pour-benchmarker-et-fiabiliser-le-rag-d-bot)
  - [3.3 Entraînement QLoRA, RL et réalité Apple Silicon versus CUDA](#33-entraînement-qlora-rl-et-réalité-apple-silicon-versus-cuda)
- [4. Leviers concrets pour accélérer l'indexation LightRAG sans perte de qualité](#4-leviers-concrets-pour-accélérer-lindexation-lightrag-sans-perte-de-qualité)
  - [4.1 Radiographie chiffrée du run étalon Calculs FEA](#41-radiographie-chiffrée-du-run-étalon-calculs-fea)
  - [4.2 Optimisations à gain immédiat dans le code RAG](#42-optimisations-à-gain-immédiat-dans-le-code-rag)
  - [4.3 Protocole de benchmark A B recommandé avant toute bascule de moteur](#43-protocole-de-benchmark-a-b-recommandé-avant-toute-bascule-de-moteur)

---

## 1. Analyse critique des trois documents de référence

Les trois documentations ([Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), [Unsloth Qwen3.8](https://unsloth.ai/docs/models/qwen3.8) et [Unsloth Qwen3.8 Train](https://unsloth.ai/docs/models/qwen3.8/train)) décrivent une rupture architecturale majeure pour un modèle dense de `27,8 B` paramètres, qui explique à la fois ses performances sur D-Bot et les précautions de réglage requises.

### 1.1 Architecture hybride Gated DeltaNet et Gated Attention de Qwen3.8-27B

- **Architecture (`qwen3_5` / `Qwen3_5ForConditionalGeneration`)** : `64` couches organisées en `16` blocs répétitifs de `3 x (Gated DeltaNet -> FFN)` suivis de `1 x (Gated Attention -> FFN)`. Dimension cachée `5120`, vocabulaire `248 320` tokens, encodeur vision/vidéo natif.
- **Conséquence directe sur ton Mac `64 Go`** : Seule **1 couche sur 4** (`16` couches sur `64`) maintient un cache KV attention classique (`24` têtes Q, seulement **`4` têtes KV** de dimension `256` en GQA). Les `48` autres couches (`Gated DeltaNet`, `48` têtes V / `16` têtes QK) utilisent un **état récurrent linéaire de taille fixe**, indépendant de la longueur du contexte.
- **Impact pratique** : À `16 384` tokens (et jusqu'à `64k-128k` pour du code/RAG), l'empreinte KV reste très faible (`~25-27 GiB` tenus en pic sous Ollama avec `24 GiB` GPU encore libres).
- **Contexte natif & YaRN** : `262 144` tokens natifs, extensibles à `1 000 000` via YaRN (`factor = 4.0`). **Ne jamais activer YaRN statique pour D-Bot** : la documentation officielle Qwen avertit explicitement que YaRN statique pénalise la qualité sur les textes courts et moyens (< `262k`).

### 1.2 Paramètres recommandés Qwen et Unsloth versus pipeline D-Bot actuel

La lecture croisée des docs met en évidence **deux régimes strictement distincts** et révèle plusieurs décalages silencieux dans la configuration actuelle du pipeline RAG :

| Paramètre | Qwen / Unsloth **Thinking Mode** (Code, CAO, FEA) | Qwen / Unsloth **Instruct / Non-Thinking** (Chat/RAG rapide) | Modelfile Ollama actuel (`qwen3.8:27b-mlx`) | [`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py#L222-L233) & MCP actuel (`think=False`) | Écart identifié & impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`enable_thinking`** | `True` (défaut HF) | `False` | `True` (`default: medium`, choix `false/low/medium/xhigh`) | **`False`** (`"think": False`) | Correct pour extraction rapide LightRAG ; pour le dev D-Bot, activer Thinking `medium` ou `xhigh`. |
| **`preserve_thinking`** | `True` (défaut HF) | sans objet / conservé sur historique | géré par renderer `qwen3.8` | non applicable (appels 1-shot + gleaning 2 tours) | Indispensable en multi-tours agentiques (`Claude Code`, `Kilo`) : évite de recalculer le raisonnement et maximise le hit KV cache. |
| **`temperature`** | **`1.0`** (HF / benchmarks Unsloth ; `0.6-1.0` toléré) | **`0.7`** | `1.0` | **`0.1`** | `0.1` est voulu en extraction structurée `<|#|>`, mais **trop bas** pour la synthèse finale RAG dans [`mcp_lightrag_server.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/mcp_lightrag_server.py). |
| **`top_p`** | **`0.95`** | **`0.80`** | `0.95` (hérité par défaut) | hérité = **`0.95`** | En mode `think=False`, Qwen prescrit **`0.80`**, pas `0.95`. |
| **`top_k`** | **`20`** | **`20`** | `20` | hérité = **`20`** (si Ollama) ; **`40`** par défaut en `llama-cli` brut | Piège critique sous `llama.cpp` brut / Unsloth sans preset : `top_k=40` dégrade la précision. |
| **`min_p`** | **`0.0`** | **`0.0`** | `0` | hérité = **`0`** (si Ollama) ; **`0.05-0.1`** par défaut en `llama.cpp` | **Piège critique** documenté : laisser `min_p > 0` casse l'équilibre de calibration de Qwen3.8. |
| **`presence_penalty`** | **`0.0`** | **`1.5`** (plage `0..2`) | `0` | hérité = **`0`** | En Non-Thinking (`think=False`), `presence_penalty=0` favorise les boucles répétitives sur descriptions longues ; toutefois Qwen alerte qu'à `1.5-2.0`, un **mélange de langues** peut apparaître (tester `0.5-0.8` en extraction française, `1.0-1.5` en synthèse QA). |
| **`repetition_penalty`** | **`1.0`** | **`1.0`** | `1` (`repeat_penalty`) | hérité = **`1`** (`1.1` par défaut en CLI `unsloth inference`) | Doit impérativement rester à **`1.0`** (éviter `1.1` qui abîme les noms de références `McMaster` et identifiants `RS-04`). |

> [!WARNING]
> **Le vrai réglage à retenir selon l'usage** :
> - **Pour l'indexation LightRAG (`index_docs.py`, `think=False`)** : conserver `temperature=0.1` (ou `0.2`), mais fixer explicitement `top_p=0.80`, `top_k=20`, `min_p=0.0`, `repeat_penalty=1.0` et un `presence_penalty` léger (`0.3` à `0.5` max pour éviter les boucles sans provoquer de bascule linguistique anglais/français).
> - **Pour les réponses RAG utilisateur (`mcp_lightrag_server.py`, `ask_rag.py`) en mode `think=False`** : aligner sur le profil **Instruct officiel** (`temperature=0.7`, `top_p=0.80`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.0-1.5`, `repeat_penalty=1.0`), ou passer en mode Thinking `low`/`medium` (`temperature=1.0`, `top_p=0.95`, `presence_penalty=0.0`) sur les requêtes d'architecture complexes.

### 1.3 Dynamic V3.1 GGUF versus NVFP4 Blackwell et état réel de ton cache local

Il faut lever immédiatement une ambiguïté terminologique importante issue des documentations :

1. **`NVFP4` Unsloth (`unsloth/Qwen3.8-27B-NVFP4`) = NVIDIA Blackwell uniquement** :
   - Les chiffres impressionnants de la doc Unsloth (**`1,41x à 1,49x` plus rapide** que BF16, `89,8 -> 133,7 tok/s` en batch=1, `4407 tok/s` en batch=64, `92 % à 97 %` top-1 agreement vs BF16, `24 Go` VRAM avec cache KV FP8) sont mesurés sur **1x NVIDIA B200** sous **vLLM** (`CompressedTensorsW8A8Fp8`) ou SGLang `v0.5.19`.
   - Cette quantification matérielle FP4 nécessite des Tensor Cores **NVIDIA Blackwell** (`RTX 50X`, `DGX Spark`, `B200`, `B300`). **Elle ne s'exécute pas sur Apple M1 Max**.
   - **Attention à l'homonymie Ollama** : `ollama show qwen3.8:27b-mlx` affiche `quantization: nvfp4`, mais il s'agit ici du **format 4-bit flottant propre au runner MLX d'Ollama sur Apple Silicon Metal**, et non du checkpoint `unsloth/Qwen3.8-27B-NVFP4` pour vLLM/Blackwell.

2. **`Dynamic V3.1 (preview)` GGUF (mise à jour du 11–12 nov 2026) = compatible Mac via `llama.cpp` / Unsloth Studio** :
   - Améliore les scores agentiques et de code (`Terminal Bench 2.1`, `DeepSWE v1.1`, `LiveCodeBench v6`, `GPQA Diamond`) de **`+5 à +10 %`** à empreinte mémoire équivalente (2-bit à 6-bit) en préservant en plus haute précision les couches critiques (attention, routeurs, projections sensibles).
   - Inclut désormais le support **Developer Role**, le parsing amélioré d'outils JSON imbriqués et une **tête de prédiction multi-tokens séparée** sur Hugging Face (`MTP/mtp-Qwen3.8-27B-Q4_0.gguf` = `1,37 Go`).
   - **Constat vérifié sur ton disque** : tu possèdes déjà `~/.cache/huggingface/hub/models--unsloth--Qwen3.8-27B-GGUF` (`Qwen3.8-27B-UD-Q4_K_XL.gguf`, `17,56 Go` + `mmproj-F16.gguf`, `0,93 Go`), **MAIS il date du 23 août 2026** (`866` tenseurs, **`0` tenseur MTP**). La version **Dynamic V3.1** actuelle sur Hugging Face (`lastModified: 2026-11-12`, `UD-Q4_K_XL` à `17,66 Go` + `MTP/mtp-Qwen3.8-27B-Q4_0.gguf` à `1,37 Go`) est plus récente et nettement supérieure pour l'agentique.

---

## 2. Audit comparatif des moteurs d'inférence sur ton MacBook Pro M1 Max

Ton Mac (`MacBookPro18,2`, Apple M1 Max, `10` CPU / `32` GPU, `64,0 GiB` RAM unifiée dont `51,3 GiB` allouables Metal GPU) dispose déjà de **cinq runtimes locaux installés**. Le tableau ci-dessous synthétise leur architecture réelle pour `Qwen3.8-27B` :

| Moteur installé | Format modèle | Support MTP sur Qwen3.8 | Batching continu (parallélisme `> 1`) | Contrôle fin paramètres (`min_p`, `presence_penalty`) | État actuel sur ta machine | Pertinence pour `index_docs.py` | Pertinence pour D-Bot général (dev/chat/VLM) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ollama `0.40.16`** (runner MLX `0.32.4`) | MLX (`nvfp4`, `18 Go`) | **Oui, actif nativement** (`68,5 %` acceptation mesurée) | Partiel (`OLLAMA_NUM_PARALLEL`), bridé à `1` dans `index_docs.py` | Partiel (via `options` JSON `/api/chat`) | Actif, validé **`32,3 tok/s`** decode / **`144,4 tok/s`** prefill | **Très bonne (référence stable sans erreur)** | Moyenne (pas de self-healing tools ni sandbox) |
| **Unsloth Desktop `0.1.804-beta` / Studio `2026.8.22`** | GGUF (`llama-server b10639`) + MLX (`mlx 0.32.1`, `mlx-lm 0.31.3`) | **Oui** (`--speculative-type auto/mtp`, nécessite `MTP/*.gguf` récent) | **Oui (`-np 4` slots par défaut)** via `llama-server` | **Auto-tuning** + flags dédiés complets | Installé (`~/.unsloth/llama.cpp b10639`), GGUF cache d'août à rafraîchir | **À tester en `UD-Q4_K_XL` V3.1 + MTP `-np 2`** | **Excellente** (`unsloth start`, tool healing, Python/Bash, Data Recipes) |
| **`llama-server`** pur (Unsloth `b10639` ou Homebrew `b10450`) | GGUF (`UD-Q4_K_XL` `17,66 Go` ou `UD-Q5_K_XL` `20,98 Go`) | **Oui** (`--spec-type draft-mtp`, `ngram-simple`) | **Oui (`-cb`, `-np 2..4`, `-fa on`)** | **Total (`100 %` des flags)** | Binaires prêts (`b10639` compilé Metal par Unsloth Team) | **Très prometteur pour batching parallèle contrôlé** | Bonne en serveur headless (`--reasoning-effort`) |
| **`vMLX.app` `1.6.19`** (`vmlx 1.6.19`, `jang 2.5.37`) | MLX / JANG / MXFP4 | **Oui** (`native_mtp.py` supporte `qwen3_5` / `qwen3_6`) | **Oui (`EngineCore` paged + prefix + disk cache)** | Complet via API OpenAI (`--continuous-batching`) | Installé (`--provider local` `:8008` dans `index_docs.py`, `:8012` dans `.kilo`) | **Potentiel #1 en débit agrégé** *si* `transformers 5.12.1` + `mlx-lm 0.31.3` de juillet valident le template `qwen3.8` | Très bonne si déjà servi en tâche de fond pour Kilo |
| **LM Studio `0.4.18+1`** | GGUF / MLX GUI | Variable selon runtime interne | Basique GUI | GUI / OpenAI API | Cache `Qwen3.6-35B-A3B` Q6_K (`28,5 Go`) | Faible (aucun avantage sur Ollama/vMLX/Unsloth) | Utile pour tests visuels ponctuels |

### 2.1 Ollama 0.40.16 MLX nvfp4 : la référence mono-flux déjà rapide

L'audit complet du journal `~/.ollama/logs/server.log` pendant ton run unitaire (`13:10:46` à `13:46:40`, 46 requêtes `/api/chat` toutes en HTTP `200`) explique pourquoi `qwen3.8:27b-mlx` a donné d'excellents résultats :

- **Pourquoi il bat la vitesse brute théorique d'un 27B dense sur M1 Max** : sans MTP, un modèle dense 27B en 4-bit (~16–18 Go lus par token) plafonne typiquement sous `20–24 tok/s` sur M1 Max. Grâce au **speculative decoding MTP natif** (`39 340` tokens validés sur `57 394` brouillons = **`68,5 %` d'acceptation**, moyenne **`3,27` tokens acceptés/itération**, pic `5,32`), Ollama MLX atteint **`32,3 tok/s` en moyenne** (pointes à **`36,4 tok/s`**).
- **Prefix Cache déjà performant** : `106 612` tokens sur `149 503` ont été servis depuis le cache préfixe (**`71,3 %`**), réduisant le prefill réel à `51 299` tokens traités à **`144,4 tok/s`** (`5,9 min` au total sur `35m 57s`).
- **Ce qui le bride aujourd'hui** : [`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py#L964-L973) force `max_async = 1`. De plus, Ollama masque certains réglages (`presence_penalty`, `min_p`, `top_k`) si on ne les injecte pas explicitement dans `"options"`.

### 2.2 Unsloth Desktop, Unsloth Studio et llama-server b10639

Unsloth Studio (`2026.8.22` sur ton poste) n'est pas un noyau d'inférence propriétaire isolé : sur macOS ARM64, il orchestre **`llama.cpp` (`b10639-mix-f6f92fe`, compilé avec Metal par l'équipe Unsloth)** pour les GGUF et **`mlx 0.32.1` / `mlx-lm 0.31.3` / `mlx-vlm 0.6.17`** pour les modèles MLX, tout en ajoutant une couche serveur FastAPI (`:8888`).

- **Ce qu'il fait mieux qu'Ollama en GGUF** :
  1. **Qualité de quantification (`Dynamic V3.1`)** : à poids égal (~`17,7 Go`), `Qwen3.8-27B-UD-Q4_K_XL` V3.1 vise une fidélité supérieure sur les tâches d'extraction complexe, de code et de raisonnement agentique, avec option facile de monter en **`UD-Q5_K_XL` (`20,98 Go`)** ou **`UD-Q6_K` (`21,98 Go`)** puisque tu as **`64 Go` de RAM unifiée**.
  2. **Parallélisme natif via slots (`-np 4` par défaut dans `unsloth run`)** : plusieurs requêtes LightRAG peuvent partager le modèle en mémoire simultanément avec contexte partagé.
  3. **Quantification KV cache (`-ctk q8_0 -ctv q8_0`) + Flash Attention (`-fa on`)** : sur des appels répétés LightRAG, garder le KV cache compact libère de la bande passante GPU.
- **Sa limite en vitesse pure pour LightRAG vs MLX** : sur Apple Silicon mono-flux, les noyaux Metal `mlx` (4-bit natif Apple) restent généralement au coude-à-coude ou légèrement devant `llama.cpp` GGUF en `tok/s`, surtout lorsque la tête MTP de Qwen3.8 MLX accepte `68,5 %` des tokens. En GGUF, pour activer MTP sous `llama-server b10639`, il faut explicitement télécharger **`MTP/mtp-Qwen3.8-27B-Q4_0.gguf` (`1,37 Go`)** qui manque dans ton cache d'août. Sans lui, `llama.cpp` retombe sur du décodage 1-token ou `ngram`.

### 2.3 vMLX 1.6.19 : le candidat batching continu sur MLX natif

Ton inspection du code source embarqué dans `vMLX.app` (`1.6.19`, compilé le 31 juillet) révèle deux caractéristiques très intéressantes face à Ollama :

1. **Support architectural déjà présent** : [`native_mtp.py`](file:///Applications/vMLX.app/Contents/Resources/vmlx-engine-source/vmlx_engine/native_mtp.py) mappe explicitement `qwen3_5` et `qwen3_6` avec activation MTP native (`GenerationBatch`) et politique `compatible-only` / rejection sampling. Or `Qwen3.8-27B` utilise exactement l'architecture `qwen3_5`.
2. **Continuous Batching + Paged/Prefix/Disk Cache (`EngineCore`)** : contrairement à un runner séquentiel, `vMLX` est conçu pour servir **plusieurs requêtes en parallèle** sur MLX (exactement ce qui manque à `index_docs.py` limité à `max_async = 1`). Comme les `34` requêtes d'extraction LightRAG partagent le même préfixe système + exemples few-shot (~`2 318` tokens constants par chunk sur le run FEA), le **prefix cache + batching continu** permet d'amortir les lectures poids GPU sur `2` à `4` chunks simultanés !
3. **Réserve impérative à vérifier** : `vMLX 1.6.19` embarque `transformers 5.12.1` et `mlx-lm 0.31.3` du 31 juillet (antérieurs à la sortie officielle d'août de `Qwen3.8-27B`). Il faut donc **valider par un test unitaire** que le chat template `qwen3.8` (`enable_thinking=False` via `extra_body` / `chat_template_kwargs`) est bien pris en charge et que le MTP reste actif lorsque le batching continu est enclenché.

### 2.4 LM Studio 0.4.18+1 : rôle exploratoire uniquement

Déjà présent avec des quants `Qwen3.6-35B-A3B` (`Q6_K`, `28,5 Go`), LM Studio reste un bon outil visuel ponctuel, mais **n'apporte aucun avantage architectural** face à Ollama MLX, Unsloth Studio ou `vMLX` pour un pipeline d'indexation automatisé : pas de proxy tool-healing ni de batching continu comparable à `vMLX` ou `llama-server -np`.

---

## 3. Ce qu'Unsloth apporte au dépôt D-Bot en général

Au-delà de la seule indexation RAG, l'écosystème Unsloth (`Unsloth Studio`, CLI `unsloth`, `Data Recipes`, `FastModel`) répond à **trois besoins structurants** de ton dépôt D-Bot :

### 3.1 Agents de code locaux, tool calling auto-réparateur et vision CAO FEA

- **Souveraineté locale sur l'ingénierie D-Bot (`unsloth start`)** : la passerelle unifiée Unsloth (`127.0.0.1:8888`) parle nativement `/v1/messages` (Claude Code, OpenClaw) et `/v1/chat/completions` (Codex, OpenCode, `.kilo/kilo.jsonc`). En chargeant `Qwen3.8-27B` **Dynamic V3.1 (`UD-Q4_K_XL` ou `UD-Q5_K_XL` + `mmproj-F16.gguf`)** en **Thinking Mode** (`temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `preserve_thinking=True`), tu obtiens sur M1 Max un modèle classé à **`73.0`** sur Terminal Bench 2.1, **`61.7`** sur SWE-bench Pro et **`90.3`** sur LiveCodeBench v6.
- **Pourquoi l'auto-healing tool calling change la donne en local** : sur des refactorings lourds (`Code/scripts/fusion360/AuditTorse/AuditTorse.py`, `FreeCAD FEM` / `CalculiX`, ou génération de schémas SVG), les modèles quantifiés locaux cassent parfois le schéma JSON d'appel d'outils. Unsloth Studio réduit ces échecs de **`50 %`** par auto-réparation côté proxy et ajoute l'exécution **Python / Bash sandboxée** pour vérifier les calculs RDM avant d'écrire la documentation.
- **Exploitation multimodale (`Visual_Snapshots` & fiches techniques PDF)** : avec **`91.1`** sur OmniDocBench 1.5 et **`85.6`** sur BabyVision (avec CI), `Qwen3.8-27B + mmproj-F16` (ou MLX vision) permet d'auditer visuellement les planches PNG de [`Visual_Snapshots`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots) et d'extraire des tableaux mécaniques/BOM complexes sans dépendre d'un quota cloud.

### 3.2 Data Recipes pour benchmarker et fiabiliser le RAG D-Bot

C'est probablement **l'apport le plus immédiatement rentable et sous-estimé d'Unsloth pour D-Bot** :

- **Problème actuel du RAG D-Bot** : aujourd'hui tu vérifies un run d'indexation par le format (`34/34 <|COMPLETE|>`) ou sur quelques requêtes manuelles. Tu n'as pas de banc de non-régression quantifié mesurant le taux de rappel exact des cotes métrologiques, références `McMaster-Carr`, couples de serrage ou résultats `CalculiX`.
- **Usage concret de `Data Recipes` (`unsloth.ai/docs/new/studio/data-recipe`)** : en chargeant tes documents maîtres (`FINAL_BOM_*`, `DOSSIER_TECHNIQUE_*`, `SYNTHESE_METROLOGIQUE_*`) dans le graphe nodal de Data Recipes avec validateurs, tu peux **générer automatiquement un jeu étalon de `100` à `200` paires Question / Réponse / Source / Cote exacte** en français. Ce dataset sert alors de référence objective pour noter `qwen3.8:27b-mlx` versus `gemma4:26b` versus `Qwen3.8-UD-Q4_K_XL` V3.1 avant toute réindexation complète !

### 3.3 Entraînement QLoRA, RL et réalité Apple Silicon versus CUDA

La page [`unsloth.ai/docs/models/qwen3.8/train`](https://unsloth.ai/docs/models/qwen3.8/train) présente des avancées majeures (`FastModel`, **Flash Linear Attention kernels** offrant **`~1,5x` plus de vitesse** et **`~50 %` moins de VRAM** que FlashAttention-2 sur l'architecture hybride DeltaNet), permettant du QLoRA `4-bit` en **`24 Go VRAM`** (y compris sur `2× Tesla T4` gratuits Kaggle grâce à `offload_embedding=True`).

- **Ce qui est réaliste sur ton Mac versus à déporter sur CUDA** :
  - Bien que ta stack locale (`unsloth 2026.8.22`, `mlx 0.32.1`, logs `mlx training stack ready`) embarque déjà les shims d'entraînement MLX macOS, la doc officielle `qwen3.8/train` documente encore exclusivement la voie CUDA/bitsandbytes (`MLX` indiqué en déploiement). De plus, entraîner un modèle dense **27B** sur M1 Max (sans Tensor Cores FP8/BF16 dédiés) reste lent pour du SFT ou du RL (`GRPO`).
  - **Stratégie pragmatique pour D-Bot** :
    1. **Ne pas fine-tuner pour la connaissance brute** : ton RAG LightRAG + `FastEmbed` reste largement supérieur au fine-tuning pour retenir des cotes évolutives (`Torse-123 v42` -> future v43) sans réentraîner.
    2. **Réserver un éventuel QLoRA CUDA (Kaggle / cloud) à deux cas ciblés** : (a) **spécialiser un `Qwen3.8` / petit modèle sur l'extraction stricte LightRAG** (format `<|#|>`, zéro dérive anglaise, `0` erreur de délimiteur, 1 seule passe au lieu de 2 !) puis l'exporter en **GGUF `q4_k_m` / Dynamic V3.1**, ou (b) **distiller un petit modèle embarqué (`<= 4B–9B`)** depuis `Qwen3.8-27B` + Data Recipes pour la **Jetson Orin Nano (`8 Go` RAM partagée)** du robot D-Bot (car un `27B` ne tiendra jamais sur la Jetson).

---

## 4. Leviers concrets pour accélérer l'indexation LightRAG sans perte de qualité

### 4.1 Radiographie chiffrée du run étalon Calculs FEA

Voici exactement où sont passées les **`35 min 57 s`** lors du test `13:10:40 – 13:46:40` sur les `17` chunks de [`DOSSIER_TECHNIQUE_Calculs_FEA_Torse_et_Bassin.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Calculs_FEA_Torse_et_Bassin.md) :

| Phase mesurée | Nombre d'opérations / volume | Temps cumulé | Part du temps total (`2157 s`) | Vitesse mesurée |
| :--- | :--- | :--- | :--- | :--- |
| **1. Hors-LLM & orchestrateur** (lecture MD, chunking `1200` tok, `multilingual-e5-large`, graph merge, écriture JSON/GraphML) | `17` chunks -> `303` entités / `359` relations | `~3 min 28 s` (`~208 s` hors fenêtres LLM ; `237 s` vs somme HTTP `[GIN]` `1920,0 s`) | `~9,6 %` | — |
| **2. Prefill LLM** (prompt system/few-shot/chunk non caché) | `51 299` tokens préfillés (`71,3 %` déjà en prefix cache !) | `5 min 55 s` (`355,2 s`) | `16,5 %` | **`144,4 tok/s`** |
| **3. Décodage LLM Pass 1 + Pass 2 + Fusions** (`max_async=1`) | **`51 430` tokens générés** en `46` appels (`34` extract + `12` merges) | **`26 min 34 s`** (`1594,1 s`) | **`73,9 %`** (`81,8 %` du LLM) | **`32,3 tok/s`** (MTP `68,5 %`) |

**Enseignement clé du cache LightRAG (`doc-32bdb56e3f545f6bbc9e0fd88055870a`)** :
- **Pass 1 (`17` appels)** : `237` entités et `213` relations (`4 573` car./réponse en moyenne).
- **Pass 2 *gleaning* (`17` appels)** : **`+140` entités (`+59 %`)** et **`+156` relations (`+73 %`)** (`2 879` car./réponse en moyenne).
- **Conclusion mathématique** : Changer simplement d'un backend à `32 tok/s` vers un backend à `40 tok/s` ne fera gagner que `~5 min` (`-15 %`). En revanche, **augmenter le débit effectif de décodage via parallélisme (`2` à `3` requêtes simultanées en continuous batching) et réduire le nombre de chunks/fusions redondantes** permet de viser un facteur **`1,8x à 2,5x`** à qualité constante.

### 4.2 Optimisations à gain immédiat dans le code RAG

Classées par ratio **gain de temps / risque qualité**, sans toucher au moteur Ollama dans un premier temps puis avec option serveur parallèle :

1. **Ajuster `chunk_token_size` (`1200 -> 1600` ou `1800` tokens, overlap `150`) — Gain estimé : `-20 %` à `-25 %` du temps, qualité souvent améliorée**
   - LightRAG utilise par défaut `CHUNK_SIZE = 1200` (`CHUNK_OVERLAP_SIZE = 100`). `Qwen3.8-27B` possède `262k` de contexte natif avec `Gated DeltaNet` et le prompt `index_docs.py` alloue déjà `num_ctx=16384`.
   - Passer à `chunk_token_size=1600` ou `1800` réduit de **`~25 %` le nombre total de chunks** (et donc le nombre d'allers-retours Pass 1 + Pass 2 + merges `force_llm_summary_on_merge=8`), tout en donnant plus de cohésion sémantique aux grands tableaux techniques D-Bot (BOM, tableaux FEA) sans saturer `num_predict=8192`.
2. **Paralléliser les requêtes LightRAG (`llm_model_max_async = 2` voire `3`) sur un moteur à Continuous Batching — Gain potentiel : `1,5x à 2,2x`**
   - Aujourd'hui [`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py#L964-L973) bloque `max_async = 1` pour `local` (`vMLX`), `ollama` et `gemini`.
   - Or ton M1 Max a **`24 GiB` de marge RAM GPU** avec un 27B 4-bit (~`27 GiB` occupés sur `51,3 GiB`). Sous **`vMLX` (`--continuous-batching`)**, **`llama-server` (`-np 2` ou `-np 3`)**, ou Ollama testé prudemment avec `OLLAMA_NUM_PARALLEL=2` (à vérifier côté runner MLX s'il sérialise ou parallélise réellement), servir `2` à `3` chunks à la fois partage la lecture des poids `27B` en mémoire GPU — faisant monter le débit agrégé de `32 tok/s` vers `45–65 tok/s` cumulés.
3. **Ne PAS couper `entity_extract_max_gleaning` sur les dossiers maîtres (`FINAL_`, `DOSSIER_TECHNIQUE_`, `STUDY_`, `GUIDE_COMPLET_`)**
   - Comme mesuré sur `Calculs_FEA`, Pass 2 récupère `+59 %` d'entités et `+73 %` de relations. Si l'on souhaite accélérer les réindexations massives des `111` fichiers restants, il est bien plus intelligent de **conserver `gleaning = 1` sur la documentation d'ingénierie critique** et d'envisager ultérieurement `gleaning = 0` uniquement si l'on introduit un profil allégé sur les petits fichiers répétitifs (`Code/` ou `.svg` simples).
4. **Corriger les paramètres d'échantillonnage `think=False` dans [`index_docs.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/index_docs.py#L228-L232) et [`mcp_lightrag_server.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/mcp_lightrag_server.py)**
   - Fixer explicitement `top_p=0.80`, `top_k=20`, `min_p=0.0`, `repeat_penalty=1.0`, et `presence_penalty=0.3` (extraction) / `1.0` (synthèse QA à `temperature=0.7`). Tu évites ainsi les micro-boucles de fin de description qui consomment des tokens inutiles à `32 tok/s` tout en respectant strictement la calibration Qwen/Unsloth.
5. **Stratégie de taille de corpus (`111` fichiers en file)** :
   - Sur `111` fichiers (environ `500–900` chunks si volume homogène, soit ~`6–12 h` en mono-flux `max_async=1` à ce rythme), une bascule validée vers `max_async = 2–3` (continuous batching) + `chunk_token_size = 1600` peut ramener une réindexation de **plusieurs heures à ~`2,5–4 h`**, sans perte de richesse graphique.

### 4.3 Protocole de benchmark A B recommandé avant toute bascule de moteur

> [!TIP]
> Pour la **procédure complète pas-à-pas** (isolation sandbox sans polluer `lightrag_dbot_db`, commandes exactes serveur + RAG, patchs Python proposés et intégration Data Recipes / `unsloth start`), suis le document compagnon : [56_Plan_Deploiement_Tests_Qwen38_LightRAG.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/IA_sur_Mac_M1_Pro_Max_64Go/56_Plan_Deploiement_Tests_Qwen38_LightRAG.md).

Plutôt que de re-télécharger ou rebasculer `index_docs.py` à l'aveugle sur `111` fichiers, voici le protocole synthétique de validation en 3 points sur un seul fichier court représentatif (`--files` sur un `STUDY_` de ~5–8 chunks) :

| Candidat | Configuration exacte à comparer | Conditions paramètres alignées | Critères d'arbitrage |
| :--- | :--- | :--- | :--- |
| **A — Référence actuelle** | `Ollama 0.40.16` (`qwen3.8:27b-mlx`) + `max_async=1`, puis test `OLLAMA_NUM_PARALLEL=2` + `max_async=2` | `think=False`, `temp=0.1`, `top_p=0.80`, `top_k=20`, `min_p=0.0`, `repeat_penalty=1.0`, `presence_penalty=0.3` | Temps total (s), débit agrégé (`tok/s`), acceptation MTP (`%`), pic RAM (`GiB`), nb entités/relations uniques. |
| **B — Unsloth `Dynamic V3.1` GGUF + MTP** | Mise à jour `Qwen3.8-27B-UD-Q4_K_XL.gguf` (`17,66 Go`) + `MTP/mtp-Qwen3.8-27B-Q4_0.gguf` (`1,37 Go`) via `~/.unsloth/llama.cpp/llama-server` (`b10639`, `-fa on -ctk q8_0 -ctv q8_0 -np 2 --spec-type draft-mtp --spec-draft-n-max 3`) + `max_async=2` | Même prompt LightRAG, `enable_thinking=False`, mêmes bornes sampling | Vérifier si la qualité V3.1 + batching `-np 2` compense ou dépasse l'Ollama MLX en débit réel wall-clock. |
| **C — `vMLX 1.6.19` Continuous Batching** | Modèle MLX/JANG `Qwen3.8-27B` avec MTP via `vmlx-engine serve --continuous-batching` (`:8008`) + `--provider local` avec `max_async=2` puis `3` | `chat_template_kwargs: {"enable_thinking": False}` et vérification logs `native_mtp` | Vérifier compatibilité `qwen3.8` (`transformers 5.12.1` de juillet), stabilité `0` erreur format `<|COMPLETE|>`, et gain du batching continu MLX. |

**Commandes prêtes à l'emploi si tu souhaites préparer la mise à jour Dynamic V3.1 + MTP dans ton cache HF (hors lancement RAG)** :

```bash
hf download unsloth/Qwen3.8-27B-GGUF --include "*UD-Q4_K_XL*" "MTP/*" "mmproj-F16.gguf"
```

Et pour mettre à jour Unsloth Studio macOS (`2026.8.22` -> dernière version) si tu veux utiliser le modèle dans Unsloth Desktop ou `unsloth start claude` :

```bash
curl -fsSL https://unsloth.ai/install.sh | sh
```
