# Étude & Benchmarks d'Indexation RAG D-Bot (`2026-11-21`)

> **Statut** : Synthèse empirique consolidée (`Niveau 2 — STUDY`)  
> **Poste de référence** : Apple MacBook Pro M1 Max (`64 Go` mémoire unifiée, macOS, Ollama `0.40.16`/`0.40.17` MLX)  
> **Documents étalons & corpus** :
> - Étalon 1 (`19 Ko`, `5` chunks `1600/150`) : [`STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md)
> - Corpus réel jumeau (`147–164 Ko`, `19–20` chunks) : manuels RobStride `RS00..RS06` & `RS10PCANFD` mesurés dans [`rag_indexing.log`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/rag_indexing.log) et le cache LightRAG de production
> - Banc A interactif (`15` requêtes QA/Tools/Vision) : [`BENCHMARK_QA_DBOT_120.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/BENCHMARK_QA_DBOT_120.json) et [`57_Veille_et_Benchmark_Modeles_Robotique_Ollama_Unsloth.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/IA_sur_Mac_M1_Pro_Max_64Go/57_Veille_et_Benchmark_Modeles_Robotique_Ollama_Unsloth.md)
> - Campagnes locales antérieures (`Phase 1` & `Phase 2`) : [`56_Plan_Deploiement_Tests_Qwen38_LightRAG.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/IA_sur_Mac_M1_Pro_Max_64Go/56_Plan_Deploiement_Tests_Qwen38_LightRAG.md)

---

## 📑 Sommaire

- [1. Périmètre et Protocole des Essais](#1-périmètre-et-protocole-des-essais)
- [2. Audit Gemini Free Tier sur Manuels Jumeaux](#2-audit-gemini-free-tier-sur-manuels-jumeaux)
- [3. Micro-sondes Unitaires sur 1min.ai](#3-micro-sondes-unitaires-sur-1minai)
- [4. Banc Complet 5 Chunks sur Étalon 1](#4-banc-complet-5-chunks-sur-étalon-1)
- [5. Banc Complet QA et Audit d'Intégrité sur 1min.ai](#5-banc-complet-qa-et-audit-dintégrité-sur-1minai)
- [6. Rappel Banc A Local sur Apple M1 Max](#6-rappel-banc-a-local-sur-apple-m1-max)
- [7. Architecture Finale Retenue et Règles Exploitation](#7-architecture-finale-retenue-et-règles-exploitation)

---

## 1. Périmètre et Protocole des Essais

La campagne menée le **`2026-11-21`** vise à qualifier objectivement **la qualité d'extraction graphe LightRAG (`1600/150`, `gleaning=1`)**, **la discipline sur les délimiteurs `<|#|>`, `<|COMPLETE|>`**, **la préservation des valeurs numériques D-Bot**, **le coût réel en crédits** et **la vitesse** des moteurs cloud (`Google Gemini Free Tier` et `1min.ai /openai/v1`) face à la référence locale **`Ollama qwen3.8:27b-mlx`** (`think=False`).

- **Isolation stricte** : chaque test `5` chunks sur l'Étalon 1 a été exécuté dans un répertoire vierge `/tmp/rag_1min_*` via `RAG_DB_PATH` (supprimé en fin de campagne), sans polluer ni déclencher le cache de la base active [`lightrag_dbot_db`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/lightrag_dbot_db).
- **Double lecture qualité** : comparaison simultanée de la couche graphe (`nœuds`, `arêtes`, `nœuds/arêtes chiffrés`, `CamelCase`, `UNKNOWN`, warnings `found X/Y` / `Complete delimiter`) et de la couche vectorielle `vdb_chunks` (`BAAI/bge-reranker-base`).

---

## 2. Audit Gemini Free Tier sur Manuels Jumeaux

L'analyse croisée de [`rag_indexing.log`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/rag_indexing.log) et des entrées réelles en cache de [`lightrag_dbot_db`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/lightrag_dbot_db) révèle deux faits majeurs sur l'ancien ordre de `GEMINI_INDEX_CASCADE` :

### 2.1 Saturation réelle des modèles non-lite en tête de cascade

Sur l'ensemble des tentatives journalisées dans [`rag_indexing.log`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/rag_indexing.log) :
- `gemini-3.8-flash` (`active_switches=0`, `4` échecs `503`/`504`), `gemini-4-hydrogen` (`0` active, `4` échecs `503`/timeout), `gemini-flash-latest` (`0` active, `4` échecs), `gemini-3.7-flash` (`0` active, `7` échecs) et `gemini-3.5-flash` (`0` active, `2` échecs) ont saturé avant de tenir un document complet.
- `gemini-3.6-flash` (`4` activations, `10` échecs `504`/`429`) et `gemini-3-flash-preview` (`3` activations) n'ont traité que de courtes fenêtres.
- Conséquence : la quasi-totalité des documents marqués « Gemini » ont été indexés par les modèles légers **`gemini-3.1-flash-lite`** (`12`), **`gemini-3.5-flash-lite`** (`11`), **`gemini-flash-lite-latest`** (`6`) et **`gemini-2.5-flash`** (`6`).

### 2.2 Sous-extraction mesurée sur manuels PDF jumeaux (`RS00` à `RS06`)

Comparaison directe sur des notices PDF quasi identiques (`~147–164 Ko`, `19–20` chunks `1600/150`) :

| Manuel PDF (`19–20` chunks) | Moteur réel observé | Car. moy. passe 1 | Entités / chunk | Relations / chunk | *Gleaning* (passe 2) à vide | Graphe final (`ents` / `rels`) | `no_COMPLETE` |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`RS05User Manual260713.pdf`** (`153,7 Ko`, `19` ch.) | **`Ollama qwen3.8:27b-mlx`** | **`6 181`** | **`20,9`** | **`18,6`** | **`1 / 19`** (`1 683` car.) | **`401` / `461`** (`19` CamelCase) | `0` |
| **`RS03User Manual261013.pdf`** (`20` ch.) | Gemini puis reprise **`qwen3.8:27b-mlx`** | `4 585` | `18,6` | `12,3` | `7 / 20` (`1 419` car.) | `382` / `344` (`46` CamelCase) | `0` |
| **`RS04User Manual260713.pdf`** (`20` ch.) | Gemini (`flash-lite-latest` + `2.5-flash`) | `2 518` | `15,2` | **`5,2`** | `18 / 20` (`48` car.) | `274` / `106` (`40` CamelCase) | `0` |
| **`RS00User Manual260713.pdf`** (`160,9 Ko`, `20` ch.) | Gemini (`3.5-flash-lite` + `3.1-flash-lite`) | `1 708` | `10,8` | **`3,5`** | `10 / 20` (`462` car.) | `212` / `94` (`26` CamelCase) | `0` |
| **`RS06User Manual260713.pdf`** (`147,2 Ko`, `19` ch.) | Gemini (`3.5-flash-lite` + `3.1-flash-lite`) | `1 622` | `12,2` | **`2,5`** | `16 / 19` (`99` car.) | `212` / **`52`** (`22` CamelCase) | `0` |
| **`RS02User Manual260713.pdf`** (`20` ch.) | Gemini (`flash-lite-latest`) | `1 542` | `10,9` | **`2,4`** | `17 / 20` (`151` car.) | `197` / **`52`** (`17` CamelCase) | `0` |
| **`RS01User Manual260713.pdf`** (`155,5 Ko`, `19` ch.) | Gemini (`flash-lite-latest` + `2.5-flash`) | **`1 502`** | `9,8` | **`2,8`** | `16 / 19` (`99` car.) | `163` / **`59`** (`19` CamelCase) | `0` |
| **`RS10PCANFDUser Manual261016.pdf`** (`15` ch.) | Gemini `3.1-flash-lite` puis `1min.ai qwen3.7-flash` | `4 319` | `19,5` | `13,6` | `0 / 15` (`1 633` car.) | `373` / `285` (`28` CamelCase) | `2` |

**Enseignement clé & correctif appliqué** :
- Gemini ne souffre **pas** du bridage à `4096` tokens (`max_output_tokens=8192`, `0` `<|COMPLETE|>` manquant sur `RS00..RS06`), mais les variantes **`*-flash-lite` sont ~4× plus laconiques**, abandonnent **`50 % à 90 %`** des passes de *gleaning* à vide et amputent le graphe de **`-77 % à -89 %` de relations** (`52–106` vs `461` sur `RS05`), tout en créant du CamelCase (`17–40` par manuel, avec quelques artefacts comme `EchoFre Hz` ou `CanTim`).
- En conséquence, [`rag_runtime.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/rag_runtime.py) sépare strictement les deux cascades Gemini :
  - **`GEMINI_INDEX_CASCADE`** (`8` modèles non-lite uniquement : `gemini-3.8-flash` -> `gemini-4-hydrogen` -> `gemini-3.6-flash` -> `gemini-3-flash-preview` -> `gemini-flash-latest` -> `gemini-2.5-flash` -> `gemini-3.7-flash` -> `gemini-3.5-flash`).
  - **`GEMINI_QA_CASCADE`** (`3` modèles `-lite` rapides uniquement pour QA & Audit : `gemini-3.1-flash-lite` -> `gemini-3.5-flash-lite` -> `gemini-flash-lite-latest`), avant bascule rapide vers **`1min.ai` (`mistral-small-2603`)** puis **`Ollama gemma4:26b`**.

---

## 3. Micro-sondes Unitaires sur 1min.ai

Sondes minimales exécutées via [`check_1minai.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/check_1minai.py) sur `https://api.1min.ai/openai/v1` avec relevé exact du solde sur `app.1min.ai` (`19` modèles individuels sondés, ordonnés par coût par token mesuré) :

| Modèle (`1min.ai`) | Tokens (`in + out = total`) | Crédits déduits | Ratio mesuré (`cr/tok`) | Contraintes API & comportement observés | Verdict présélection |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **`qwen3.7-flash`** | `19 + 1 = 20 tok` | **`0`** (`2` barré -> `Gratuit`) | ~`0,10` nominal *(puis payant)* | Accepte `temperature=0.1` ; **quota gratuit vite épuisé**, facturation jusqu'à ~`3 527` cr/chunk dur (`Bassin`) | Retenu en test `5` chunks *(petits lots)* |
| **`mistral-small-latest`** | `22 + 2 = 24 tok` | **`9 crédits`** (`11 147 436 -> 11 147 427`) | **`0,375 cr/tok`** | Accepte `temperature=0.1` ; plafond serveur `4096` tokens en sortie (`HTTP 400` si `> 4096`) | **Retenu -> Défaut `1minai`** |
| **`open-mistral-nemo`** | `10 + 2 = 12 tok` | `6 crédits` (`11 063 897 -> 11 063 891`) | `0,500 cr/tok` | Accepte `temperature=0.1`, `+33 %` plus cher au token que `mistral-small-latest` pour un `12B` | Écarté |
| **`gpt-4o-mini`** | `14 + 1 = 15 tok` | `8 crédits` (`11 063 905 -> 11 063 897`) | `0,533 cr/tok` | Accepte `temperature=0.1`, `+42 %` plus cher que `mistral-small-latest` (proche `mistral-small-2603` / `gpt-6-luna`) | Candidat optionnel *(sans cap `4096`)* |
| **`mistral-small-2603`** *(Mistral Small 4)* | `22 + 2 = 24 tok` | **`14 crédits`** (`11 204 996 -> 11 204 982`) | `0,583 cr/tok` | Accepte `temperature=0.1` ; pas de plafond `4096` | **Retenu en banc `5` chunks** *(docs denses)* |
| **`gpt-6-luna`** | `13 + 4 = 17 tok` | **`10 crédits`** (`11 147 419 -> 11 147 409`) | `0,588 cr/tok` | **Refuse `temperature`** (`HTTP 400` -> omis dans `_ONEMINAI_BASE_OMIT_TEMP`) | **Retenu en banc `5` chunks** |
| **`ministral-14b-latest`** | `10 + 3 = 13 tok` | **`8 crédits`** (`11 147 427 -> 11 147 419`) | `0,615 cr/tok` | Accepte `temperature=0.1`, plus petit (`14B`), plus cher au token que `mistral-small-latest` | Écarté |
| **`gpt-5-nano`** | `13 + 16 = 29 tok` | `21 crédits` (`11 205 039 -> 11 205 018`) | `0,724 cr/tok` | Refuse `temperature`, consomme du *thinking* interne et renvoie **`""` vide** sur `max_tokens=16` | **Éliminé** |
| **`qwen3.6-flash`** | `19 + 1 = 20 tok` | `19 crédits` (`11 314 886 -> 11 314 867`) | `0,950 cr/tok` | Accepte `temperature=0.1`, ~`2,5×` plus cher que `mistral-small-latest` | Écarté |
| **`qwen-flash`** | `16 + 1 = 17 tok` | `18 crédits` (`11 314 927 -> 11 314 909`) | `1,059 cr/tok` | Accepte `temperature=0.1` | Écarté |
| **`gpt-5.4-nano`** | `13 + 4 = 17 tok` | `23 crédits` (`11 314 909 -> 11 314 886`) | `1,353 cr/tok` | **Refuse `temperature`** (`HTTP 400` -> ajouté à `_ONEMINAI_BASE_OMIT_TEMP`) | Écarté *(cher)* |
| **`qwen-plus`** | `16 + 1 = 17 tok` | `23 crédits` (`11 063 891 -> 11 063 868`) | `1,353 cr/tok` | Accepte `temperature=0.1`, `3,6×` plus cher que `mistral-small-latest` | Écarté *(cher)* |
| **`qwen3.7-plus`** | `19 + 1 = 20 tok` | `28 crédits` | `1,400 cr/tok` | Plus cher sans avantage sur le modèle local `27B` | Écarté |
| **`gpt-4.1-mini`** | `14 + 1 = 15 tok` | `22 crédits` (`11 205 018 -> 11 204 996`) | `1,467 cr/tok` | Trop onéreux au token | Écarté |
| **`deepseek-flash`** *(DeepSeek V4.1 Flash)* | `37 + 11 = 48 tok` | `73 crédits` (`11 315 000 -> 11 314 927`) | `1,521 cr/tok` | **Refuse `temperature`** (`HTTP 400`), `11` tokens de raisonnement cachés sur `"OK"` | Écarté *(cher)* |
| **`mistral-medium-3-5`** *(Mistral Medium 3.5)* | `22 + 2 = 24 tok` | **`144 crédits`** (`11 063 868 -> 11 063 724`) | **`6,000 cr/tok`** | Accepte `temperature=0.1` ; **`16×` plus cher au ping** que `mistral-small-latest` (~`400k+` cr sur `5` ch.) | **Écarté *(coût prohibitif)*** |
| **`qwen3.7-max`** | `19 + 1 = 20 tok` | `166 crédits` | `8,300 cr/tok` | `~22×` plus cher au token que `mistral-small-latest` | Écarté |
| **`glm-5.3`** | `19 + 16 = 35 tok` | `291 crédits` | `8,314 cr/tok` | Refuse `temperature`, *thinking* caché + **`""` vide** sur `max_tokens=16` | **Éliminé** |
| **`meta/muse-spark-1.2`** *(Meta Muse Spark)* | `15 + 16 = 31 tok` | **`260 crédits`** (`11 064 165 -> 11 063 905`) | **`8,387 cr/tok`** | *Thinking* caché + **`""` vide** sur `max_tokens=16`, `~22,4×` plus cher que `mistral-small-latest` | **Éliminé** |
| *Cumul résiduel `kimi-k2.6` + `mistral-medium-latest`* | `31 + 24 = 55 tok` | `273 crédits` résiduels *(`417 - 144`)* | ~`4,96 cr/tok` *(moy.)* | Coût prohibitif comparable à `mistral-medium-3-5` | Écartés |

---

## 4. Banc Complet 5 Chunks sur Étalon 1

Comparatif complet en conditions identiques sur [`STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Densites_Apparentes_FDM_PA12-CF_Torse_et_Bassin.md) (`19 Ko`, `5` chunks `1600/150`, `10` appels LightRAG avec `gleaning=1`) :

| Modèle & run | Durée `real` | Tokens (`in + out = total`) | Crédits réels (`5` ch.) | Ratio pondéré (`cr/tok`) | Autonomie `11,06 M` cr. | Format `<\|#\|>` & `COMPLETE` | Nœuds (chiffrés) | Arêtes (chiffrées) | Cotes `12/12` & `g/cm` | `unk` / `camel` | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`Ollama qwen3.8:27b-mlx`** (`p1_c1600`, Local) | `515,78 s` | — *(pic `27,57 GiB` RAM)* | **`0`** | `0` | Illimitée | **`0` warning** (`10/10` `<\|COMPLETE\|>`) | `100` (`79`) | `135` (`99`) | Référence | Canonique | **RÉFÉRENCE QUALITÉ (`0` cr)** |
| **`1min.ai mistral-small-latest`** | `~98 s` (`5,26×`) | `51 346 + 22 078 = 73 424` | **`35 275`** (`~7 055`/ch.) | **`0,480`** | **~`1 568` chunks** | `3` warnings `4/5` (`chunk-004`), cap `4096` out | **`146` (`100`)** | **`158` (`123`)** | **`12/12`** (`g/cm=56`) | `unk=4`, `camel=35` | **GAGNANT `1minai` (`défaut`)** |
| **`1min.ai gpt-6-luna`** | `~120 s` | `44 427 + 23 090 = 67 517` | `47 969` (`+36 %` vs Small) | `0,710` | ~`1 153` chunks | **`0` warning**, refuse `temperature` | `103` (`72`) | `111` (`58`) | `7/12` (`g/cm=21`) | **`unk=0`, `camel=5`** | Noms très propres mais faible en arêtes/cotes |
| **`1min.ai mistral-small-2603`** | **`~88 s`** (`5,86×`) | `48 694 + 19 295 = 67 989` | `56 644` (`+60,6 %` vs Small) | `0,833` | ~`976` chunks | **`0` warning**, pas de cap `4096` | `116` (`78`) | `158` (`115`) | `7/12` (`g/cm=42`) | `unk=1`, `camel=30` | **Gagnant QA/Audit `1min.ai`** *(challenger index dense)* |
| **`1min.ai gpt-4o-mini`** | `97 s` | `40 965 + 9 085 = 50 050` | — *(`0,533` ping)* | ~`0,53` | — | `3` warnings `4/5` (`chunk-001`), trop concis | `75` (`50`) | **`70` (`49`)** | `7/12` (`g/cm=5`) | `unk=0`, `camel=2` | **`NO-GO` Indexation** *(`-48 %` arêtes vs `27B`)* |
| **`1min.ai qwen3.7-flash`** | `~75 s` | `11 699` crédits nominaux* | Mini slot `0` puis payant *(pics `3 527`/ch.)* | ~`0,10` *(nominal)* | Variable | `0` sur Étalon 1, **cassé sur `Bassin`** (`2/4`–`4/5` + `COMPLETE` manquant) | `143` (`83`) | `169` (`113`) | `12/12` (`g/cm=14`) | `unk=6`, `camel=3` | Limité aux petits lots rapides |
| **`Antigravity Agent (Gemini 4 Hydrogen High, 1 passe)`** | Quelques s | **`0`** *(session IDE)* | **`0`** | `0` | Sans crédit externe | **`0` warning** (`5/5` `<\|COMPLETE\|>`) | **`84` (`84`)** | **`84` (`84`)** | **`g/cm=68`** *(100 % chiffré)* | **`unk=0`** | **Optimal `0` crédit / `0` RAM Ollama** |
| **`Antigravity Agent (Gemini 4 Hydrogen Medium, 1 passe)`** | Quelques s | **`0`** *(session IDE)* | **`0`** | `0` | Sans crédit externe | **`0` warning** (`5/5` `<\|COMPLETE\|>`) | **`69` (`69`)** | **`60` (`60`)** | `g/cm=54` *(100 % chiffré)* | **`unk=0`** | Validé `0` crédit / `0` RAM Ollama |
| **`Antigravity Agent (Gemini 4 Hydrogen Low, 1 passe)`** | Quelques s | **`0`** *(session IDE)* | **`0`** | `0` | Sans crédit externe | **`0` warning** (`5/5` `<\|COMPLETE\|>`) | `39` (`—`) | `22` (`—`) | Synthétique | **`unk=0`** | Rapide *(incrémental léger)* |
| **`Ollama gemma4:26b`** (`p1_gemma4_c1600`, Local) | `160,0 s` (`3,22×`) | — *(local)* | **`0`** | `0` | Illimitée | **`37` lignes `<\|#\|\|>` cassées** (`30` warnings `4/5`) | `69` (`46`) | **`44`** (`42`, **`-67,4 %`**) | Altère nom `Fusion 364` | Trop dégradé | **`NO-GO` Indexation** *(QA & Audit seul)* |

*\*Note `Antigravity Agent` : essais isolés sur `/tmp/rag_agent_bench*` via `index_docs.py --prepare-agent` / `--commit-agent` (`effort_profile="balanced"` routant les `5` chunks `STUDY_` en `inherit`, sans `extra_high` ni `gleaning`). Progression mesurée : `Low` (`39`/`22`) -> `Medium` (`69`/`60`, `g/cm=54`) -> `High` (`84`/`84`, `100 %` nœuds et arêtes chiffrés, `g/cm=68`, `unk=0`, `0` warning), tout en conservant `100 %` du texte verbatim dans `vdb_chunks`.*

*\*Note `qwen3.7-flash` : sur l'essai réel complet hors Étalon 1 (`DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md`), `qwen3.7-flash` a déclenché des oublis répétés de délimiteurs (`found 2/4`–`4/5`, `Complete delimiter can not be found`) et consommé jusqu'à `3 527` crédits sur un seul gros appel avant bascule.*

---

## 5. Banc Complet QA et Audit d'Intégrité sur 1min.ai

Banc en conditions réelles exécuté sur `6` tâches extraites à froid (`0` LLM) de [`lightrag_dbot_db`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/lightrag_dbot_db) (`4` QA techniques issues de [`BENCHMARK_QA_DBOT_120.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/RAG/BENCHMARK_QA_DBOT_120.json) + `2` audits globaux `36–40 Ko` issus de [`check_integrity.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/rag/check_integrity.py), `max_tokens=2048`, `timeout=60 s`) :

| Modèle (`1min.ai`) | Latence moy. (total `6` appels) | Tokens (`in + out = total`) | QA (`4` cas / `3` faisables*) | Audit global (`36–40 Ko` + `**Question :**`) | Hygiène (`0` dollar / `0` LaTeX) | Observations & défauts critiques | Verdict QA / Audit |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **`mistral-small-2603`** *(Mistral Small 4)* | **`4,69 s`** (`28,17 s`) | `63 323 + 4 255 = 67 578` | **`3 / 3`** (`3/4`, `1,33–2,35 s` QA) | **`2 / 2`** (`11,16 s` et `6,28 s`) | **`6 / 6`** | **Seul modèle `100 %` sur tâches faisables + Audit** ; `0` troncature sur `40 Ko`, cotes Z exactes, cite les `.md` | **🏆 GAGNANT (`ONEMINAI_QA_MODEL` & `ONEMINAI_AUDIT_MODEL`)** |
| **`gpt-6-luna`** | `8,49 s` (`50,97 s`) | `57 654 + 4 345 = 61 999` | **`3 / 3`** (`3/4`, `2,16–5,30 s`) | `1 / 2` | `6 / 6` | Trop verbeux en audit : sature à `2048` tokens en cours de phrase sur `audit_cinematique` (`22,08 s`), coupe avant les questions | Écarté en Audit *(plus lent)* |
| **`qwen3.7-flash`** | `8,62 s` (`51,71 s`) | `64 021 + 4 482 = 68 503` | `2 / 3` (`2/4`, `2,66–6,66 s`) | **`2 / 2`** (`16,77 s` et `17,30 s`) | `6 / 6` | **Erreur factuelle QA** sur IMU (`0,5–0,6 N.m` bien présent mais affirmé absent) ; `2×` plus lent que `mistral-small-2603` | Écarté en QA |
| **`gpt-4o-mini`** | `8,75 s` (`52,49 s`) | `57 660 + 1 745 = 59 405` | `2 / 3` (`2/4`, `2,32–4,29 s`) | `1 / 2` (`13,75 s` et `24,84 s`) | `6 / 6` | **Erreur catalogue** (`92125A220` au lieu de `91292A130`) et format `- **Question :**` rejeté en audit (`24,84 s`) | **Écarté (`NO-GO`)** |
| **`mistral-small-latest`** | `1,65 s` *(QA seul)* (`9,89 s`) | `38 440 + 653 = 39 093` | **`3 / 3`** (`3/4`, `1,68–3,51 s`) | **`0 / 2`** (`HTTP 400`) | `4 / 6` *(2 crashs)* | **Fenêtre bloquée à ~`16K` tokens sur `1min.ai`** : crash immédiat `context_length_exceeded` sur tout contexte d'audit (`36–40 Ko`) | Gardé pour **Indexation `1600 tok`** uniquement |

*\*Note `qa_fea_von_mises` : les `6` chunks top-k remontés par LightRAG concernent l'étude `Bride Épaule RS04` (`109,62 MPa` Cas 2 / `133,12 MPa` Cas 5), correctement synthétisée par tous les modèles (`mistral-small-2603` détaillant les `6` extraits), et non la vieille valeur `5,759 / 26,04` du jeu JSON.*

---

## 6. Rappel Banc A Local sur Apple M1 Max

Mesures complètes détaillées dans [`57_Veille_et_Benchmark_Modeles_Robotique_Ollama_Unsloth.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/IA_sur_Mac_M1_Pro_Max_64Go/57_Veille_et_Benchmark_Modeles_Robotique_Ollama_Unsloth.md#L194-L225) (`15` requêtes sous Ollama `0.40.16`, `num_ctx=8192`, `think=False`) :

- **`gemma4:26b`** (`18,28 GiB` VRAM `ollama ps`, `67,9 tok/s` decode, `472,4 tok/s` prefill) : **`15 / 15` (`49,69 s`)** en Tool Calling ROS 2/MCP (`5/5`, `2,66 s`), QA chiffrée FR (`5/5`, `1,12 s`, TTFT `0,43 s`) et Vision CAO/FEA (`5/5`, `6,16 s`) — **`2,55×` plus rapide** que `qwen3.8:27b-mlx` (`15/15`, `126,48 s`). Validé comme repli local par défaut pour le **QA rapide ET l'Audit rapide** (`OLLAMA_QA_MODEL`) et écarté de l'indexation graphe (`NO-GO`).
- **`inkling-2-mini:26b-a5b-nvfp4`** (`24,38 GiB` VRAM) : **`9 / 15` (`356,29 s`)**, `0 / 5` en Tool Calling sans *Thinking* -> **retiré du disque (`NO-GO`)**.

---

## 7. Architecture Finale Retenue et Règles Exploitation

1. **Deux vitesses en `--provider auto` (`index_docs.py`, `ask_rag.py`, `check_integrity.py`, `rag_cli.py`, et défaut MCP `llm_mode="auto"`)** :
   - **Indexation** (`index_docs.py`, `rag_index_document`, `0` crédit par défaut) : **`Gemini Free Tier non-lite` (`8` modèles)** -> **`Ollama qwen3.8:27b-mlx`** (`think=False`). Aucun passage par `*-flash-lite` ni par `1min.ai` sans option explicite (`--with-1minai` ou `RAG_AUTO_1MINAI=true`).
   - **QA rapide & Audit rapide** (`ask_rag.py`, `check_integrity.py`, `rag_search`, `rag_analyze_impact`, `rag_audit_integrity` en `llm_mode="auto"` par défaut) : **Cascade courte `Gemini -lite` (`3` modèles : `gemini-3.1-flash-lite` -> `gemini-3.5-flash-lite` -> `gemini-flash-lite-latest`)** -> **`1min.ai` (`mistral-small-2603`)** -> **`Ollama gemma4:26b`** *(repli `qwen3.8:27b-mlx` si absent)* -> `Unsloth` -> `OpenRouter` *(puis repli transparent `antigravity` sous MCP `llm_mode="auto"`)*.
2. **`--provider ollama` (`0` crédit, référence absolue)** : recommandé directement pour l'indexation des lots critiques et dossiers Niveau 1 (`FINAL_`, `DOSSIER_TECHNIQUE_`, `FINAL_BOM`) afin de garantir `~6 200` car./chunk, `18–20` relations/chunk et `0` troncature `4096`.
3. **`--provider 1minai` (spécialisé par rôle)** : **`mistral-small-latest`** (`0,480 cr/tok`, cap `4096` out) par défaut en **indexation** chunk par chunk (`1600 tok`), et **`mistral-small-2603`** (`4,69 s` moy., `100 %` QA faisables + `100 %` Audits `40 Ko+`) par défaut en **QA & Audit**.
4. **Règle d'interrogation** : `vdb_chunks` + `BAAI/bge-reranker-base` préservent **100 % du texte verbatim** quel que soit le LLM d'indexation ; privilégier `--mode naive` pour les cotes exactes et codes `McMaster-Carr`, et `--mode hybrid` pour les dépendances système.
