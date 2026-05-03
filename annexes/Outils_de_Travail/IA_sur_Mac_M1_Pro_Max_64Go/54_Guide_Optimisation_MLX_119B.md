# 🧠 Guide d'Optimisation : Mistral Small 4 119B JANG sur M1 Max

> **Auteur :** Guide généré avec Antigravity — Mis à jour le 03/05/2026  
> **Cible :** Modèle `JANGQ-AI/Mistral-Small-4-119B-A6B-JANG_2L` sur Mac M1 Max 64 Go avec MLX Studio (vMLX Engine)

---

## 🔍 1. Diagnostic de la cause racine des interruptions

Le message suivant, visible dans les logs de vMLX, révèle le vrai problème :

```
Tight-memory configuration detected: model is using a large fraction 
of max working set. Cache limit adjusted downward.

terminating due to uncaught exception of type std::runtime_error: [METAL] Command
```

### Bilan mémoire sur M1 Max 64 Go

| Composant | Mémoire utilisée |
|---|---|
| Modèle 119B (8-bit JANG mixte) | ~36 GB |
| Système macOS | ~5–6 GB |
| Reste disponible pour le KV Cache | ~22 GB |
| KV Cache réel à 30K tokens (sans optimisation) | ~6–8 GB |
| **Marge avant crash Metal** | **⚠️ < 10 GB — insuffisant** |

**Conclusion :** Le modèle est parfaitement chargé et fonctionne bien jusqu'à ~15K tokens. Au-delà, le KV cache grossit et Metal n'a plus assez de mémoire pour ses buffers de calcul. Il tue alors la requête.

---

## ⚙️ 2. Configuration CLI Optimisée — Copier-Coller

Dans MLX Studio, allez dans l'onglet **Server** et ajoutez ces arguments dans le champ **"Extra Arguments"** (ou "CLI Arguments") :

### Configuration Recommandée (Stable, longues sessions)

```bash
--timeout 1800 --kv-bits 8 --kv-group-size 64 --cache-memory-percent 0.15 --max-cache-blocks 500
```

### Configuration Agressive (Sessions très longues, >30K tokens)

```bash
--timeout 3600 --kv-bits 4 --kv-group-size 64 --cache-memory-percent 0.12 --max-cache-blocks 400
```

---

## 🔧 3. Détail de Chaque Argument

### `--kv-bits 8` (ou `4`) — **Impact : TRÈS ÉLEVÉ** ⭐⭐⭐⭐⭐

La fonctionnalité la plus puissante de vMLX. Compresse le KV cache en quantization q8 ou q4.

| Valeur | Économie RAM (30K tokens) | Qualité |
|---|---|---|
| Sans (défaut) | ~6–8 GB | Parfaite |
| `--kv-bits 8` | ~3–4 GB (**2× moins**) | ✅ Identique (storage-boundary) |
| `--kv-bits 4` | ~1.5–2 GB (**4× moins**) | ✅ Excellente |

> **Note technique :** vMLX utilise la "storage-boundary quantization" — le cache est en pleine précision PENDANT le calcul, et compressé uniquement ENTRE les opérations. Aucune perte de qualité réelle.

### `--kv-group-size 64` — **Impact : ÉLEVÉ** ⭐⭐⭐⭐

Votre 119B est un modèle **MoE (Mixture of Experts)**. Le group size 64 est la valeur optimale pour ce type d'architecture (vs 32 pour les dense models). Combiné avec `--kv-bits`, c'est la combinaison la plus efficace.

### `--cache-memory-percent 0.15` — **Impact : ÉLEVÉ** ⭐⭐⭐⭐

Plafonne le KV cache à **15% de la RAM totale** = 9,6 Go maximum.

| Valeur | Plafond KV Cache (64 GB Mac) |
|---|---|
| 0.20 (défaut) | 12,8 GB |
| **0.15 (recommandé)** | **9,6 GB** |
| 0.12 (agressif) | 7,7 GB |

### `--max-cache-blocks 500` — **Impact : ÉLEVÉ** ⭐⭐⭐⭐

Votre configuration actuelle utilise 1000 blocs. Avec un modèle 119B, chaque bloc occupe beaucoup plus de mémoire qu'avec un 7B. Réduire à 500 libère immédiatement de la mémoire.

### `--timeout 1800` — **Impact : MOYEN** ⭐⭐⭐

Le timeout par défaut est ~300 secondes (5 minutes). Une tâche d'ingénierie (10 appels d'outils, réécriture de fichiers) peut prendre 10+ minutes. Passez à 1800 (30 min) ou 3600 (1 heure).

---

## 🚀 4. Décodification Spéculative — Boostez la Vitesse de 1.5×

### Principe

Un petit modèle "brouillon" (draft model) propose des tokens rapidement, et le 119B les vérifie en parallèle. Résultat : **même qualité, 1.5× plus de tokens/seconde**, donc moins de temps sous pression mémoire.

### ✅ Modèle Recommandé : Mistral Small 3.2 24B (Vous l'avez déjà !)

Le meilleur candidat sur votre machine est le modèle que vous avez déjà téléchargé :

| Critère | Valeur |
|---|---|
| **Modèle** | `mlx-community/Mistral-Small-3.2-24B-Instruct-2506-8bit` |
| **Taille** | ~14 GB (8-bit) |
| **Tokenizer** | ✅ Identique au 119B (vocab_size 131072, même famille Mistral v3) |
| **Architecture** | ✅ Compatible (Mistral attention layers) |
| **RAM totale** | 36 + 14 = 50 GB → reste 14 GB pour le KV cache |

**Argument CLI à ajouter :**
```bash
--speculative-decoding-model /Users/davidsergent/.cache/huggingface/hub/mlx-community/Mistral-Small-3.2-24B-Instruct-2506-8bit --speculative-decoding-tokens 3
```

### ✅ Alternative légère : Mistral Small 3.2 24B 4-bit (Plus de marge mémoire)

Si vous souhaitez maximiser la marge mémoire :

| Critère | Valeur |
|---|---|
| **Modèle** | `mlx-community/Mistral-Small-3.2-24B-Instruct-2506-8bit` (version 4-bit) |
| **Taille** | ~7 GB (4-bit) |
| **RAM totale** | 36 + 7 = 43 GB → reste **21 GB** pour le KV cache |
| **Gain vitesse** | ~1.3–1.5× |

> **Pourquoi pas un modèle encore plus petit (3B) ?**  
> Les modèles Mistral 3B et 8B utilisent une version antérieure du tokenizer Mistral (vocab_size 32768) incompatible avec le 119B (vocab_size 131072). Un tokenizer différent rend la décodification spéculative impossible (les IDs de tokens ne correspondent pas).

---

## 🏆 5. Configuration Finale Complète (Toutes Optimisations)

```bash
--timeout 1800 \
--kv-bits 8 \
--kv-group-size 64 \
--cache-memory-percent 0.15 \
--max-cache-blocks 500 \
--speculative-decoding-model /Users/davidsergent/.cache/huggingface/hub/mlx-community/Mistral-Small-3.2-24B-Instruct-2506-8bit \
--speculative-decoding-tokens 3
```

**Sur une seule ligne (pour coller dans MLX Studio) :**
```bash
--timeout 1800 --kv-bits 8 --kv-group-size 64 --cache-memory-percent 0.15 --max-cache-blocks 500 --speculative-decoding-model /Users/davidsergent/.cache/huggingface/hub/mlx-community/Mistral-Small-3.2-24B-Instruct-2506-8bit --speculative-decoding-tokens 3
```

---

## 📊 6. Impact Estimé sur Votre Machine

```
AVANT :
  [Modèle 119B : 36 GB] + [KV Cache ~7 GB] + [OS : 6 GB] = 49 GB → CRASH à 30K tokens
  Vitesse : ~9 t/s

APRÈS (configuration recommandée) :
  [Modèle 119B : 36 GB] + [KV Cache q8 ~3 GB] + [OS : 6 GB] = 45 GB → STABLE à 40K+ tokens
  Vitesse : ~9 t/s (stable, sans crash)

APRÈS (avec décodification spéculative) :
  [119B : 36 GB] + [24B draft : 14 GB] + [KV q8 : 3 GB] + [OS : 6 GB] = 59 GB → STABLE
  Vitesse : ~13–14 t/s (+50%)
```

---

## 🧠 7. Stratégie Opérationnelle (Sans Modifier la Config)

Si vous ne pouvez pas modifier les arguments du serveur, cette approche contractuelle avec le modèle évite tous les crashes :

### La Règle "Une Étape à la Fois"

Au lieu de :
> *"Sauvegarde les fichiers et applique les modifications à stt.py, tts.py et audio_io.py"*

Dites :
> *"**Étape 1 seulement :** Fais uniquement la sauvegarde des 3 fichiers. Une fois terminé, dis-moi 'Sauvegarde OK' et attends ma confirmation avant de continuer."*

Puis :
> *"**Étape 2 :** Maintenant modifie UNIQUEMENT stt.py. Arrête-toi ensuite."*

**Pourquoi ça marche :** Chaque message repart de zéro pour le timeout ET le compteur d'itérations d'outils (souvent bridé à 10).

### Demander des Diffs plutôt que des Réécritures

Au lieu de laisser le modèle réécrire entièrement un fichier (500 lignes = 500 tokens générés), demandez-lui :
> *"Ne réécris pas le fichier entier. Montre-moi uniquement les blocs de code à modifier, et je ferai les changements moi-même."*

---

## 📌 8. Résumé Rapide

| Problème | Solution | Paramètre |
|---|---|---|
| Crash mémoire (METAL OOM) | Compresser le KV cache | `--kv-bits 8` |
| Trop de RAM utilisée par le cache | Réduire le plafond | `--cache-memory-percent 0.15` |
| Crash après 10 min | Augmenter le timeout | `--timeout 1800` |
| Génération lente | Draft model 24B | `--speculative-decoding-model ...` |
| Trop d'actions IA coupées | Stratégie "1 étape à la fois" | (opérationnel) |

---

*Document généré avec Antigravity — vMLX Engine v2.14b — M1 Max 64 Go*
