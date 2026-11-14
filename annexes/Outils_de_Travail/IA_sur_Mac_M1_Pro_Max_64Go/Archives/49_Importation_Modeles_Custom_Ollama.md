# 49 - Importation de Modèles Custom (Hugging Face → Ollama)

> **Document de référence — Intelligence Artificielle D-Bot**
> Ce guide explique comment utiliser n'importe quel modèle téléchargé sur Hugging Face (via LM Studio ou manuellement) au sein de l'écosystème Ollama.

---

## 1. Pourquoi cette méthode ?

Ollama possède une bibliothèque officielle vaste, mais les nouveaux modèles (ex: **Qwen 3.6**) ou les versions spécialisées (quantifications spécifiques) apparaissent souvent d'abord sur Hugging Face au format **GGUF**. Cette méthode permet d'être "à la pointe" sans attendre les mises à jour officielles.

---

## 2. Étape 1 : Téléchargement via LM Studio

LM Studio est l'outil le plus simple pour explorer Hugging Face sur Mac.

1.  Ouvrez **LM Studio**.
2.  Utilisez la barre de recherche (ex: `Qwen 3.6 27B GGUF`).
3.  Choisissez une version (préférez les versions de **Bartowski** ou **MaziyarPanahi**).
4.  **Important** : Choisissez une quantification équilibrée (ex: `Q4_K_M` ou `Q6_K`).
5.  Cliquez sur **Download**.

---

## 3. Étape 2 : Localisation du fichier GGUF

Une fois le téléchargement terminé, vous devez récupérer le chemin exact du fichier.
*   Par défaut, LM Studio les stocke ici : 
    `~/.cache/lm-studio/models/`
*   Vous pouvez aussi cliquer sur l'icône de dossier dans LM Studio pour ouvrir l'emplacement.

---

## 4. Étape 3 : Création du Modelfile

Le `Modelfile` est le "plan de montage" pour Ollama. Créez un fichier nommé `Modelfile` (sans extension) dans votre dossier de travail.

```bash
touch Modelfile
nano Modelfile
```

Copiez-y la structure suivante :

```dockerfile
# 1. Le lien vers le fichier GGUF (chemin absolu recommandé)
FROM "/Users/davidsergent/.cache/lm-studio/models/publisher/model-name/model.gguf"

# 2. Le System Prompt (Personnalité du D-Bot)
SYSTEM """
Tu es l'intelligence centrale du robot bipède D-Bot.
Tes réponses sont techniques, précises et orientées vers le développement en Python/ROS2.
Tu as accès aux schémas du robot et aux capteurs Jetson.
"""

# 3. Les paramètres de comportement
# 'temperature' (0.0 à 1.0) : Définit la créativité. 0.3 est idéal pour du code technique.
PARAMETER temperature 0.3
# 'top_p' : Filtre de vocabulaire. 0.9 empêche l'IA d'utiliser des termes hors sujet.
PARAMETER top_p 0.9
# 'stop' : Les mots clés qui disent à l'IA d'arrêter de parler.
# Ces 3 tokens sont obligatoires pour éviter le bug de "boucle" sur les modèles Qwen/Mistral.
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"
```

---

## 5. Étape 4 : Injection dans Ollama

Ouvrez un terminal et lancez la compilation du modèle :

```bash
# Syntaxe : ollama create <nom_choisi> -f <chemin_du_modelfile>
ollama create qwen-3.6-custom -f Modelfile
```

Ollama va lire le fichier GGUF, intégrer vos paramètres et créer une entrée dans sa base de données interne. 
*Note : Si le modèle existe déjà (par exemple après avoir modifié vos paramètres), relancer exactement la même commande écrasera la version précédente et mettra le modèle à jour instantanément.*

---

## 6. Étape 5 : Vérification et Usage

### A. Vérifier la présence du modèle
```bash
ollama list
```
Vous devriez voir `qwen-3.6-custom` dans la liste.

### B. Tester le modèle
```bash
ollama run qwen-3.6-custom
```

### C. Usage dans VS Code (Continue / Roo Code)
Dans votre fichier `config.yaml` de Continue, vous pouvez désormais référencer ce nom :
```yaml
models:
  - name: Qwen Custom Agent
    provider: ollama
    model: qwen-3.6-custom
```

---

## 7. Gérer les Modèles Officiels et le "Tool Calling"

Si vous utilisez un fichier GGUF manuel, les outils avancés (comme la recherche web Tavily via `@tavily`) ne fonctionneront pas par défaut dans Continue. Ollama a besoin d'un `TEMPLATE` interne très complexe pour comprendre les outils, qui est absent des GGUF bruts.

Pour utiliser les "Tools", voici les 3 options :

### Option 1 : Le catalogue officiel Ollama (Recommandée)
C'est la méthode la plus sûre. Les modèles du catalogue incluent déjà le code nécessaire pour les outils.
Pour trouver les modèles disponibles, allez sur **[ollama.com/library](https://ollama.com/library)** dans votre navigateur (il n'y a pas de commande de recherche dans le terminal).
```bash
# Exemple de téléchargement d'un modèle officiel
ollama pull qwen2.5:32b
```

### Option 2 : Le pont direct Hugging Face
Ollama peut désormais télécharger directement depuis Hugging Face sans passer par LM Studio. Il parvient parfois à auto-détecter le bon template pour les outils.
```bash
ollama run hf.co/bartowski/Qwen2.5-32B-Instruct-GGUF
```

### Option 3 : Copier le Template officiel (Expert)
Si vous tenez absolument à votre fichier GGUF manuel :
1. Téléchargez la version officielle la plus proche : `ollama pull qwen2.5`
2. Affichez son code interne : `ollama show --modelfile qwen2.5`
3. Copiez l'immense bloc `TEMPLATE """ ... """` qui s'affiche et collez-le dans votre propre `Modelfile`.

---

## 8. Diagnostic Rapide

| Erreur | Solution |
| :--- | :--- |
| **"Error: FROM requires a valid file"** | Vérifiez le chemin du fichier GGUF. Utilisez des guillemets si le chemin contient des espaces. |
| **Lenteur extrême** | Vérifiez que vous n'avez pas pris un modèle trop gros (ex: 120B) pour vos 64 Go de RAM. |
| **Réponses incohérentes** | Le modèle a besoin d'un prompt spécifique. Vérifiez la page Hugging Face du modèle original. |

---

## 9. Nettoyage et Suppression

Tester des modèles volumineux (72B, 110B) peut rapidement saturer votre SSD. Voici comment faire le ménage proprement.

### A. Lister les modèles installés
Pour voir ce qui prend de la place :
```bash
ollama list
```

### B. Supprimer un modèle
```bash
# Syntaxe : ollama rm <nom_du_modele>
ollama rm qwen-3.6-custom
```

### C. Vérifier l'espace libéré
Le dossier de stockage d'Ollama sur Mac se trouve dans `~/.ollama/models`. Vous pouvez vérifier que la taille du dossier a bien diminué.

---

## 10. Résumé des Fichiers Modifiés

| Fichier | Modification clé |
| :--- | :--- |
| `annexes/ia/49_Importation_Modeles_Custom_Ollama.md` | Guide complet : Importation GGUF, Modelfile et Suppression. |
