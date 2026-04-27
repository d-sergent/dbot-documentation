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
PARAMETER temperature 0.3
PARAMETER top_p 0.9
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

## 7. Diagnostic Rapide

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
