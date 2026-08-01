# 🤖 **Guide d'Inférence LLM Locale avec DwarfStar 4 (ds4) sur Mac M1/M2/M3/M4 (64 Go RAM)**

*Document technique dédié à l'installation, au paramétrage du SSD Streaming, au débridage mémoire Metal GPU et à l'exécution de modèles géants MoE (DeepSeek V4 Flash 284B) sur Mac Apple Silicon 64 Go.*

---

## 1. Présentation de DwarfStar 4 (ds4)

**DwarfStar 4 (`ds4`)** est un moteur d'inférence LLM local écrit en **C natif pur**, développé par **Salvatore Sanfilippo (`antirez`)**, le créateur historique de **Redis**. 

Contrairement aux frameworks génériques (`llama.cpp`, `Ollama`), `ds4` est un moteur ultra-spécialisé et hyper-optimisé au niveau du code C et des noyaux Metal (Apple Silicon) pour faire tourner des modèles de classe "frontière" (*frontier models*) basés sur des architectures MoE (*Mixture of Experts*) géantes.

### Liens & Ressources Officielles
- **Dépôt GitHub officiel** : [antirez/ds4 (GitHub)](https://github.com/antirez/ds4)
- **Site web & documentation** : [dwarfstar.sh](https://dwarfstar.sh/)
- **Documentation d'installation** : [dwarfstar.sh/docs/quickstart](https://dwarfstar.sh/docs/quickstart/)
- **Guide matériel & benchmarks** : [dwarfstar.sh/hardware](https://dwarfstar.sh/hardware/)

---

## 2. Modèles Supportés à ce Jour

| Modèle | Architecture | Poids `q2-imatrix` | RAM Optimale | Mode sur Mac 64 Go |
|:---|:---:|:---:|:---:|:---:|
| **DeepSeek V4 Flash** ⭐ | MoE 284B param. | **~81 Go** | 96 Go – 128 Go | **SSD Streaming (Recommandé)** |
| **GLM 5.2 (Zhipu AI)** | MoE 744B param. | ~180 Go | 128 Go – 256 Go | SSD Streaming (Très lourd) |
| **DeepSeek V4 PRO** | MoE 512B+ param. | ~150 Go | 256 Go – 512 Go | Exécution distribuée (2× Mac Studio) |

---

## 3. Analyse Matérielle & Bilan Mémoire pour Mac 64 Go RAM

### A. Empreinte Mémoire Vive (RAM Unifiée) — Commande Recommandée
Pour la commande d'inférence optimisée Mac 64 Go :
```bash
./ds4 -m ./ds4flash.gguf --ssd-streaming --ssd-streaming-cache-experts 32GB --ctx 32768 --nothink
```

La mémoire unifiée (RAM) est allouée comme suit :

| Composant | Allocation | Rôle |
|:---|:---:|:---|
| **Couches fixes (*Backbone* Dense + Attention)** | ~14 Go | Conservé en RAM permanente |
| **Cache d'Experts MoE (`--ssd-streaming-cache-experts 32GB`)** | **32 Go** | Enveloppe mémoire vive pour les experts streamed |
| **KV Cache (`--ctx 32768`)** | ~3,5 Go | Mémoire contexte en FP16 MLA |
| **Buffers GPU Metal (Scratch / Activations)** | ~3 Go | Zones de calcul dynamique du GPU Apple |
| **TOTAL RAM NETT EXIGÉ PAR DS4** | **~52,5 à 54 Go** | **S'inscrit sous le plafond des 64 Go** |

### B. Espace Disque SSD Requis
- **Fichier modèle `ds4flash.gguf` (`q2-imatrix`)** : **~81 Go**
- **Buffer & KV Cache persistant sur SSD** : **~10 à 15 Go**
- **Espace SSD libre recommandé** : **100 Go à 120 Go sur SSD interne NVMe**.

---

## 4. Guide d'Installation Pas à Pas sur macOS

### Étape 1 : Prérequis système
Assurez-vous d'avoir les outils de compilation Apple installés dans le terminal :
```bash
xcode-select --install
```

### Étape 2 : Cloner le dépôt et compiler
```bash
# 1. Cloner le dépôt officiel
git clone https://github.com/antirez/ds4.git
cd ds4

# 2. Compiler l'exécutable natif pour macOS Metal (prend ~2 secondes)
make
```

### Étape 3 : Télécharger le modèle DeepSeek V4 Flash (q2-imatrix)
```bash
# Téléchargement automatique de la version 2-bit (81 Go)
./download_model.sh q2-imatrix
```
*Le script télécharge le fichier GGUF quantifié et crée le lien symbolique `ds4flash.gguf`.*

---

## 5. Débridage de la Mémoire Metal & Libération du Système

Sur macOS, par défaut, le système réserve environ 25% de la RAM unifiée pour les besoins internes du système d'exploitation, ce qui peut brider l'allocation du GPU Metal sur un Mac de 64 Go.

### A. Débrider le plafond mémoire Metal (Wired Memory)
Pour autoriser le GPU Metal à utiliser jusqu'à 56 Go de RAM unifiée sur votre Mac 64 Go :

```bash
# Débloquer la limite d'allocation mémoire Metal à 56 Go (57344 Mo)
sudo sysctl iogpu.wired_mem_limit=57344
```

> [!TIP]
> Pour rendre ce réglage permanent au démarrage du Mac, ajoutez la ligne `iogpu.wired_mem_limit=57344` dans le fichier `/etc/sysctl.conf`.

### B. Procédure de libération de RAM avant lancement
1. Fermez les applications gourmandes en mémoire (Chrome, Docker, VS Code, Slack, serveurs locaux).
2. Purgez le cache mémoire macOS via le terminal :
   ```bash
   sudo purge
   ```
3. Vérifiez la RAM disponible (doit être > 54 Go libre) :
   ```bash
   memory_pressure
   ```

---

## 6. Commandes d'Exécution & Modes d'Utilisation

### A. Mode Chat CLI Interactif (Test rapide)
```bash
./ds4 -m ./ds4flash.gguf --ssd-streaming --ssd-streaming-cache-experts 32GB --ctx 32768 --nothink
```

### B. Mode Serveur Local API (Compatible OpenAI & Anthropic)
Pour connecter vos outils d'agents de code (Claude Code, OpenCode, Codex CLI, Pi) sur votre Mac local :

```bash
./ds4-server -m ./ds4flash.gguf --ssd-streaming --ssd-streaming-cache-experts 32GB --ctx 32768 --port 8080
```
- **Endpoint OpenAI** : `http://localhost:8080/v1/chat/completions`
- **Endpoint Anthropic** : `http://localhost:8080/v1/messages`

### C. Mode Agent de Code Autonome Native (`./ds4-agent`)
`ds4` embarque son propre agent de codage autonome qui modifie le code source local par édition de balises (*tag-based editing*) :

```bash
./ds4-agent --dir /chemin/vers/votre/projet
```

---

## 7. Performances Attendues & Benchmarks sur Mac 64 Go

Sur un Mac M1/M2/M3/M4 Max/Pro (64 Go RAM) avec SSD interne NVMe :

- **Vitesse de Prefill (Prompts longs / Lecture de contexte)** : **100 à 200 tokens/seconde**.
- **Vitesse de Génération (Decode tok/s)** : **7 à 10 tokens/seconde**.
- **Stabilité** : **100% stable** sans crash OOM (grâce au streaming SSD dynamique des experts).

---

## 8. Alternatives 100% RAM pour Mac 64 Go (Productivité quotidienne)

Si vous recherchez un débit d'inférence plus rapide (25 à 40 tok/s) sans utiliser le streaming SSD, privilégiez des modèles tenant 100% en RAM unifiée sur **Ollama** ou **`llama.cpp`** :

| Modèle | Quantification | Taille RAM | Usage recommandé | Vitesse sur 64 Go |
|:---|:---:|:---:|:---|:---:|
| **Qwen2.5-Coder 32B** | Q6_K | ~26 Go | **Codage autonome ultra-rapide** | **35–40 tok/s** |
| **DeepSeek-R1-Distill-Qwen 32B** | Q6_K | ~26 Go | Raisonnement & mathématiques | **30–35 tok/s** |
| **Llama 3.3 70B Instruct** | Q3_K_M | ~35 Go | Modèle généraliste puissant | **20–25 tok/s** |

---

*Guide technique validé en Août 2026 d'après les spécifications officielles de DwarfStar 4 (ds4) et les benchmarks Apple Silicon.*
