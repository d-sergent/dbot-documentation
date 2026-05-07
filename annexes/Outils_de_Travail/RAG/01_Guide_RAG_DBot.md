# 🧠 Système RAG D-Bot : LightRAG + LanceDB + MCP

> **Objectif :** Permettre aux LLMs locaux (via vMLX) d'interroger intelligemment toute la documentation D-Bot, d'effectuer des analyses d'impact croisées (ex: "si les bras sont plus lourds, quel impact sur la vitesse de course ?") et d'accéder à ces capacités via un serveur MCP standard.
>
> **Dernière mise à jour :** 05/05/2026

---

## 📁 Structure des Fichiers

```
/Users/Shared/                          ← Accessible depuis toutes les sessions Mac
└── lightrag_dbot_db/                   ← Base de données RAG (LightRAG + LanceDB)
    ├── graph_chunk_entity_relation.graphml   ← Graphe de connaissances
    ├── kv_store_*.json                 ← Caches KV de LightRAG
    └── lancedb/                        ← Index vectoriel LanceDB

/Users/Shared/Mon Google Drive Physique/Documentation/
└── code/rag/
    ├── index_docs.py                   ← Script d'indexation (lancement manuel)
    └── mcp_lightrag_server.py          ← Serveur MCP (exposé dans mcp-config.json)
```

---

## 🏗️ Pourquoi cette Architecture ?

### Le problème du RAG classique pour D-Bot

Un RAG vectoriel classique (Qdrant ou LanceDB seul) répond bien à "qu'est-ce que dit la doc sur les bras ?", mais est **aveugle aux relations de cause à effet** entre documents différents. Si votre fichier `27_Etude_Epaule_Architecture.md` indique une masse de bras de 1.2 kg, et que `15d_Genou_et_Course.md` décrit les exigences de couple pour courir, un RAG classique ne fera jamais le lien entre ces deux informations.

### La solution : LightRAG (Graph RAG)

LightRAG combine **deux types de mémoire** :

| Mémoire | Technologie | Usage |
|:---|:---|:---|
| **Vectorielle** | LanceDB (embarqué) | Recherche par similarité sémantique |
| **Graphe de connaissances** | GraphML (fichier) | Relations entité → entité |

Lors de l'indexation, LightRAG utilise le LLM pour extraire automatiquement des **entités** (composants, masses, couples, vitesses...) et leurs **relations** (impacte, limite, requiert, détermine...). Ces relations sont stockées dans un graphe qui permet des analyses d'impact croisées.

```
Exemple de graphe extrait de votre documentation :

[Bras Robot] ──pèse──> [1.2 kg]
[Masse Bras]  ──contribue_à──> [Masse Totale Robot]
[Masse Totale]──détermine──> [Couple Requis Cheville]
[Couple Requis]──limite──> [Vitesse de Course Max]
[Vitesse Course]──contraint──> [Moteur Genou RS06]
```

### Pourquoi FastEmbed (CPU) ?

Votre M1 Max est déjà sollicité par les modèles 119B ou 35B. FastEmbed génère les vecteurs sur le **CPU uniquement**, laissant le GPU entièrement disponible pour le LLM. Le modèle utilisé est `BAAI/bge-m3` : multilingue (Français/Anglais), 570 Mo, très rapide sur Apple Silicon.

---

## ⚙️ Installation (Une seule fois)

```bash
# 1. Installer les dépendances
pip install lightrag-hku lancedb fastembed mcp

# 2. Créer le dossier partagé de la base de données
mkdir -p "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"
chmod 777 "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"
```

---

## 🚀 Initialisation (Première Indexation)

> [!IMPORTANT]
> Cette étape prend **10 à 30 minutes** selon le nombre de fichiers. Elle appelle votre LLM local (via vMLX) pour extraire les entités de chaque document. Assurez-vous que **vMLX est lancé avec le modèle 35B ou 119B** avant de lancer le script.

```bash
# Vérifiez que vMLX tourne
curl http://127.0.0.1:1800/v1/models

# Lancez l'indexation complète
python3 /Users/Shared/Mon\ Google\ Drive\ Physique/Documentation/code/rag/index_docs.py --full
```

**Ce que fait le script :**
1. Parcourt récursivement tout `/Documentation/` (fichiers `.md` et `.py`)
2. Découpe chaque fichier en chunks de 1200 tokens avec 200 tokens de chevauchement
3. Génère les embeddings via **FastEmbed** (CPU, silencieux)
4. Appelle votre **LLM local** pour extraire les entités et relations de chaque chunk
5. Stocke tout dans `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db/`

---

## 🔄 Mise à Jour (Après Modification de Fichiers)

La mise à jour est **manuelle** : vous lancez le script uniquement quand vous avez modifié ou ajouté des fichiers.

```bash
# Mise à jour incrémentale (re-indexe uniquement les fichiers modifiés depuis la dernière indexation)
python3 /Users/Shared/Mon\ Google\ Drive\ Physique/Documentation/code/rag/index_docs.py --update

# Forcer la ré-indexation complète (si vous avez supprimé des fichiers ou restructuré)
python3 /Users/Shared/Mon\ Google\ Drive\ Physique/Documentation/code/rag/index_docs.py --full
```

> [!TIP]
> Le flag `--update` compare les dates de modification des fichiers avec celles enregistrées dans `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db/indexed_files.json`. Seuls les fichiers nouveaux ou modifiés sont re-traités, ce qui rend la mise à jour très rapide (souvent moins d'une minute si vous avez modifié 2-3 fichiers).

---

## 🔌 Serveur MCP — Intégration avec vMLX

### Configuration dans `mcp-config.json`

Ajoutez cette entrée dans votre fichier `/Users/davidsergent/Downloads/mcp-config.json` :

```json
{
  "mcpServers": {
    "dbot-rag": {
      "command": "python3",
      "args": [
        "/Users/Shared/Mon Google Drive Physique/Documentation/code/rag/mcp_lightrag_server.py"
      ],
      "env": {
        "VMLX_BASE_URL": "http://127.0.0.1:1800/v1",
        "RAG_DB_PATH": "/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db"
      }
    }
  }
}
```

### Outils MCP Exposés

Le serveur MCP expose **4 outils** utilisables directement par le LLM :

| Outil MCP | Description | Mode LightRAG |
|:---|:---|:---|
| `rag_search` | Recherche sémantique dans la documentation | `hybrid` |
| `rag_analyze_impact` | Analyse de cause à effet croisée entre composants | `global` |
| `rag_get_context` | Récupère le contexte précis autour d'un sujet | `local` |
| `rag_list_topics` | Liste les grandes thématiques indexées | `naive` |

### Exemple d'utilisation par le LLM

Une fois le serveur MCP actif, le LLM peut utiliser ces outils naturellement :

```
Utilisateur : "Si les bras de D-Bot passent à 1.8 kg chacun, quel impact sur la vitesse de course ?"

LLM → appelle rag_analyze_impact("augmentation masse bras 1.8kg impact vitesse course")
     → reçoit le graphe de relations pertinent
     → génère une réponse contextualisée avec les données exactes de votre documentation
```

---

## 🔍 Modes de Requête LightRAG

LightRAG possède **4 modes** que le serveur MCP exploite intelligemment :

| Mode | Quand l'utiliser | Exemple |
|:---|:---|:---|
| `local` | Question précise sur un composant | "Quel est le couple max du RS06 ?" |
| `global` | Analyse croisée entre plusieurs docs | "Impact masse bras sur autonomie batterie" |
| `hybrid` | Requête générale (mode par défaut) | "Comment fonctionne l'audio du robot ?" |
| `naive` | Recherche simple par mot-clé | "Liste tous les fichiers sur la cheville" |

---

## 🧪 Test de l'Installation

```bash
# Test direct sans MCP (en Python)
python3 - << 'EOF'
from lightrag import LightRAG, QueryParam

rag = LightRAG(working_dir="/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db")

result = rag.query(
    "Quels sont les composants qui influencent la vitesse de course du robot ?",
    param=QueryParam(mode="global")
)
print(result)
EOF
```

---

## ⚠️ Points d'Attention

> [!WARNING]
> **Port vMLX variable :** Le port de vMLX change selon le modèle chargé (1800 pour le 119B, 8004 pour d'autres). Le script lit la variable d'environnement `VMLX_BASE_URL`. Si votre modèle tourne sur un autre port, modifiez-la dans le `mcp-config.json`.

> [!NOTE]
> **Base de données partagée :** Le dossier `/Users/Shared/Mon Google Drive Physique/lightrag_dbot_db/` est accessible depuis toutes les sessions macOS (compte principal, compte invité, etc.) sans nécessiter de configuration supplémentaire.

> [!CAUTION]
> **Ré-indexation complète destructive :** Le flag `--full` supprime et recrée intégralement la base de données. Ne l'utilisez que si vous avez supprimé ou massivement restructuré des fichiers. Préférez toujours `--update` en usage courant.

---

## 📊 Performances Estimées sur M1 Max

| Opération | Durée estimée |
|:---|:---|
| Indexation initiale (~40 fichiers .md) | 15–25 minutes |
| Mise à jour incrémentale (3–5 fichiers) | 1–3 minutes |
| Requête `local` (recherche précise) | < 2 secondes |
| Requête `global` (analyse croisée) | 3–8 secondes |
| Démarrage du serveur MCP | < 5 secondes |

---

## 🔗 Fichiers Associés

- [Script d'indexation](../../code/rag/index_docs.py)
- [Serveur MCP LightRAG](../../code/rag/mcp_lightrag_server.py)
- [Guide optimisation 119B](../ia/54_Guide_Optimisation_MLX_119B.md)
- [Base de données RAG](file:///Users/Shared/Mon%20Google%20Drive%20Physique/lightrag_dbot_db/)
