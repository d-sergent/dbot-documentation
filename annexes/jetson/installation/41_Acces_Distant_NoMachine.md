# 41 — Accès Distant (Headless) : NoMachine & SSH

Une fois la Jetson installée, l'objectif est de pouvoir l'intégrer physiquement dans le robot et de s'y connecter à distance depuis votre Mac, sans devoir brancher d'écran ni de clavier au robot.

## 1. Comprendre l'architecture d'accès

Il y a deux moyens de se connecter à la Jetson, selon votre besoin :

- **Accès Ligne de Commande (SSH)** : Idéal pour programmer, lancer des scripts ROS2 ou compiler. Léger et rapide.
- **Accès Bureau à Distance (NoMachine)** : Connecte votre Mac directement à l'interface graphique (bureau Ubuntu) de la Jetson. Indispensable pour utiliser des outils graphiques comme *RobStride MotorStudio* ou visualiser la caméra OAK-D.

## 2. Préparation sur la Jetson (Côté Serveur)

**A. Trouver l'adresse IP de la Jetson**
Sur la Jetson, ouvrez un terminal et tapez :
```bash
ip a
```
Notez l'adresse IP (elle ressemble souvent à `192.168.1.X` ou `10.0.0.X`).
*Conseil : Fixez cette adresse IP dans l'interface de votre Box Internet/Routeur pour qu'elle ne change jamais.*

**B. Installer et Configurer NoMachine Server**
1. Sur la Jetson (depuis le navigateur Firefox), téléchargez le paquet **NoMachine for ARM64 (DEB)** depuis le site officiel de NoMachine.
2. Installez-le via le terminal :
   ```bash
   sudo dpkg -i nomachine_*.deb
   ```
3. L'icône NoMachine devrait apparaître en haut à droite de l'écran Ubuntu. Le serveur est maintenant actif.

*(Note : Sous Ubuntu 22.04 LTS, le système d'affichage par défaut est Wayland. NoMachine gère mieux X11. S'il y a un écran noir lors de la connexion, désactivez Wayland dans `/etc/gdm3/custom.conf` en décommentant `WaylandEnable=false` et redémarrez).*

## 3. Configuration sur le Mac (Côté Client)

**A. Connexion SSH simple**
Sur votre Mac, ouvrez le Terminal et tapez (remplacez `dbot` par votre nom d'utilisateur et `IP_JETSON` par l'IP trouvée précédemment) :
```bash
ssh dbot@IP_JETSON
```
Le mot de passe de compte vous sera demandé. Vous êtes maintenant connecté.

**B. Connexion au Bureau (NoMachine)**
1. Téléchargez et installez **NoMachine for Mac** sur votre MacBook.
2. Lancez l'application NoMachine.
3. Cliquez sur **Ajouter (Add)** pour créer une nouvelle connexion :
   - **Nom** : D-Bot Jetson
   - **Protocol** : NX (par défaut)
   - **Host** : *L'adresse IP de la Jetson*
   - **Port** : 4000 (par défaut)
4. Double-cliquez sur la nouvelle icône "D-Bot Jetson".
5. Une fenêtre vous demande vos identifiants. Entrez :
   - **Nom d'utilisateur** : (ex: `dbot`)
   - **Mot de passe** : (Le mot de passe d'administration de la Jetson)
6. Acceptez le certificat de sécurité.
7. Vous avez maintenant accès au bureau du robot en temps réel !

## 4. Fonctionnement "Headless" (Sans écran)

Si la Jetson démarre **sans écran branché** (HDMI ou DP), le système ne détecte pas de moniteur matériel. 

**Bonne nouvelle confirmée sur le D-Bot (JetPack 6.2.1)** : Contrairement à d'anciennes versions, NoMachine est capable de simuler de lui-même un bureau virtuel fluide. Vous n'avez **pas** besoin d'acheter un "HDMI Dummy Plug" (une petite clé hardware qui trompe la carte graphique) pour conserver l'interface graphique. La prise en main fonctionne immédiatement ("Out-of-the-box") !

## 5. Clavier AZERTY (Mac Français) — Configuration validée

Lorsqu'on se connecte depuis un Mac avec un clavier français via NoMachine, certaines touches sont mal interprétées par Ubuntu (ex: `&` devient `à`, `@` et `#` absents). Cela est dû à un conflit entre la traduction faite par NoMachine et le modèle de clavier attendu par Linux.

**Solution validée sur le D-Bot (MacBook Pro FR → Jetson Orin Nano, JetPack 6.2.1) :**

Le modèle `macintosh` (différent de `apple`) est la seule combinaison qui résout le problème en une fois.

**Étape 1 — Mettre à jour le fichier de configuration clavier système :**
```bash
sudo nano /etc/default/keyboard
```
Contenu à mettre :
```text
XKBMODEL="macintosh"
XKBLAYOUT="fr"
XKBVARIANT=""
XKBOPTIONS=""
```

**Étape 2 — Appliquer de manière permanente au niveau système :**
```bash
sudo dpkg-reconfigure keyboard-configuration
```

**Étape 3 — Forcer la prise en compte par NoMachine (session graphique) :**

> [!IMPORTANT]
> NoMachine gère sa propre session graphique et n'applique pas toujours `/etc/default/keyboard`. Il faut également ajouter la commande `setxkbmap` au profil utilisateur pour qu'elle soit exécutée à chaque ouverture de session.

```bash
echo "setxkbmap -model macintosh -layout fr" >> ~/.profile
```

Pour appliquer immédiatement sans redémarrer :
```bash
setxkbmap -model macintosh -layout fr
```

**Résultat :** Toutes les touches AZERTY fonctionnent correctement, y compris `@`, `#`, `&`, `é`, `è`, `à`, etc. La configuration survit aux redémarrages et aux reconnexions NoMachine.

