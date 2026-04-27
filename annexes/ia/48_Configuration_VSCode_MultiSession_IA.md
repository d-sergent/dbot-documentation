# 48 - Configuration VS Code Multi-Session & Partage IA

> **Document de référence — Configuration Bipède D-Bot**
> Ce guide détaille comment partager les extensions et les données IA (Continue, Roo Code) entre deux sessions macOS (ex: Session Standard et Session IA) pour maximiser les performances du M1 Max (64 Go RAM) tout en gardant des environnements étanches.

---

## 1. Principe de l'Architecture

L'idée est de déporter les dossiers lourds de VS Code vers un espace commun accessible par tous les utilisateurs de la machine, puis de créer des **liens symboliques (`symlinks`)** pour faire croire à chaque session que les fichiers sont chez elle.

*   **Avantage 1** : Une seule mise à jour d'extension pour toutes les sessions.
*   **Avantage 2** : L'indexation de la codebase (LanceDB) est partagée (l'IA "apprend" partout en même temps).
*   **Avantage 3** : Isolation des ressources (la session IA peut saturer le GPU/RAM sans impacter le reste).

---

## 2. Étape 1 : Création de l'Espace Commun

Ouvrez un terminal et créez le dossier qui hébergera les données partagées.

```bash
# Créer le dossier parent
sudo mkdir -p /Users/Shared/vscode-common

# Donner la propriété au groupe 'staff' (tous les utilisateurs standards)
sudo chown -R :staff /Users/Shared/vscode-common
sudo chmod -R 775 /Users/Shared/vscode-common
```

---

## 3. Étape 2 : Migration des Extensions (Session Principale)

Lancez ces commandes depuis votre session où VS Code est déjà configuré.

```bash
# 1. Déplacer les extensions actuelles vers l'espace commun
sudo mv ~/.vscode/extensions /Users/Shared/vscode-common/

# 2. Créer le lien symbolique pour que VS Code les retrouve
ln -s /Users/Shared/vscode-common/extensions ~/.vscode/extensions

# 3. Vérifier le lien
ls -la ~/.vscode/extensions
# Devrait pointer vers -> /Users/Shared/vscode-common/extensions
```

---

## 4. Étape 3 : Liaison de la Session IA

Connectez-vous à votre **Session IA** et liez-la au même dossier.

```bash
# 1. Supprimer le dossier d'extensions vide (s'il existe)
rm -rf ~/.vscode/extensions

# 2. Créer le même lien symbolique
ln -s /Users/Shared/vscode-common/extensions ~/.vscode/extensions
```

---

## 5. Étape 4 : Partage du "Cerveau" IA (Continue / Roo Code)

Pour que l'indexation de vos fichiers (RAG) soit partagée entre vos sessions, déplacez les données de configuration de vos outils IA.

```bash
# Depuis la session qui a déjà les données :
sudo mv ~/.continue /Users/Shared/vscode-common/continue-data

# Sur LES DEUX sessions (Standard et IA) :
rm -rf ~/.continue
ln -s /Users/Shared/vscode-common/continue-data ~/.continue
```

*Note : Faites la même chose pour `~/.roo-code` si vous utilisez cette extension.*

---

## 6. Étape 5 : Script d'Automatisation des Permissions

Pour éviter les erreurs de lecture/écriture entre sessions, créez ce script de maintenance.

```bash
# Créer le script
sudo nano /Users/Shared/fix_ia_perms.sh
```

Copiez-y le contenu suivant :
```bash
#!/bin/bash
# Fix-Permissions pour l'environnement VS Code Partagé
sudo chown -R :staff /Users/Shared/vscode-common
sudo chmod -R 775 /Users/Shared/vscode-common
# Ajout d'un ACL pour l'héritage des droits
sudo chmod -R +a "group:staff allow list,add_file,search,add_subdirectory,delete_child,readattr,writeattr,readextattr,writeextattr,readsecurity" /Users/Shared/vscode-common
echo "✅ Permissions synchronisées pour le projet Robot."
```

Rendez-le exécutable :
```bash
chmod +x /Users/Shared/fix_ia_perms.sh
```

---

## 7. Étape 6 : Partage des Réglages Utilisateur (settings.json)

Pour que vos thèmes, raccourcis clavier et surtout vos **clés d'API** soient identiques partout, nous allons lier le fichier de configuration principal de VS Code.

```bash
# 1. Depuis la session qui a vos réglages préférés :
cp ~/Library/Application\ Support/Code/User/settings.json /Users/Shared/vscode-common/settings.json

# 2. Sur LES DEUX sessions (Standard et IA) :
# Supprimer l'ancien fichier local
rm ~/Library/Application\ Support/Code/User/settings.json
# Créer le lien vers le fichier partagé
ln -s /Users/Shared/vscode-common/settings.json ~/Library/Application\ Support/Code/User/settings.json
```

---

## 8. Optimisation Spécifique à la Session IA

Dans votre `.zshrc` (ou `.bashrc`) de la **Session IA uniquement**, ajoutez cette ligne pour forcer Ollama à exploiter toute la puissance du M1 Max :

```bash
export OLLAMA_NUM_GPU=999
```

---

## 9. Règles d'Or pour éviter la Corruption

| Action | Règle à suivre |
| :--- | :--- |
| **Modification Config** | Ne jamais ouvrir les menus de réglages (UI ou JSON) de VS Code sur les deux sessions en même temps. |
| **Mises à jour** | Faire l'update d'une extension sur une session pendant que VS Code est FERMÉ sur l'autre. |
| **Settings Sync** | **Désactiver impérativement** la synchronisation Cloud de Microsoft (GitHub Sync). Le lien symbolique local fait déjà tout le travail plus proprement. |
| **Expérience** | Tout changement (thème, police, clé API) est désormais **instantané** sur les deux sessions. |

---

## 10. Configuration d'Ollama (Le Moteur Local)

Pour que vos extensions IA fonctionnent, Ollama doit être opérationnel. Dans un setup multi-session, il faut suivre une règle de "Serveur Unique".

### A. Démarrage du Serveur
Ollama ne peut pas tourner en deux exemplaires sur la même machine (conflit sur le port `11434`).
*   **Recommandation** : Lancez Ollama uniquement sur votre **Session IA**.
*   **Faut-il le démarrer à l'avance ?** : **Oui.** Soit via l'application Ollama, soit via la commande `ollama serve` dans un terminal de la session IA. Les extensions (Continue/Roo Code) ne lancent pas le serveur automatiquement, elles ne font que s'y connecter.
*   **Accès depuis la Session Standard** : Comme les deux sessions partagent la même IP locale (`localhost`), VS Code sur la session Standard verra l'Ollama lancé sur la session IA sans configuration supplémentaire.

### B. Configuration dans Continue (`config.json`)
Puisque nous avons lié le dossier `~/.continue`, la modification faite sur une session sera répercutée sur l'autre.
Ajoutez vos modèles dans la section `models` :

```json
{
  "models": [
    {
      "title": "Ollama - Llama 3",
      "provider": "ollama",
      "model": "llama3",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Starcoder 2",
    "provider": "ollama",
    "model": "starcoder2:3b"
  }
}
```

### C. Configuration dans Roo Code
Dans les paramètres de l'extension Roo Code (icône en forme de robot) :
1.  **API Provider** : Sélectionnez `Ollama`.
2.  **Base URL** : Gardez `http://localhost:11434`.
3.  **Model ID** : Tapez le nom exact (ex: `codestral` ou `llama3`).

---

## 11. Diagnostic Rapide

*   **VS Code ne voit aucune extension** : Le lien symbolique est mort ou pointe vers un dossier inexistant. Vérifiez avec `ls -la ~/.vscode/extensions`.
*   **Erreur "Permission Denied"** : Lancez le script `/Users/Shared/fix_ia_perms.sh`.
*   **Ollama Error (Connection Refused)** : Vérifiez que `ollama serve` tourne bien sur l'une de vos deux sessions.
*   **Lenteur extrême** : Vérifiez si Ollama ne tourne pas en double. Tapez `lsof -i :11434` pour voir qui occupe le port.

---

## 12. Résumé des Fichiers Modifiés

| Fichier | Modification clé |
| :--- | :--- |
| `code/scripts/behaviors/test_audio_loop.py` | Script de test autonome : réveil complet, calibration dynamique. |
| `code/dbot/audio/tts.py` | `LocalTTS` : activation automatique ampli JST. |
| `annexes/ia/48_Configuration_VSCode_MultiSession_IA.md` | Guide complet multi-session (Extensions + Settings + Ollama). |
