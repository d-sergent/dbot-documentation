# 40 — Installation de base Jetson Orin Nano Super (JetPack 6.2.1)

Ce guide détaille la procédure de préparation de la carte SD (ou NVMe) de la NVIDIA Jetson Orin Nano Super, qui servira de cerveau principal au D-Bot.

## 1. Prérequis sur le Mac

Pour préparer l'image système depuis votre Mac, vous aurez besoin de deux éléments :

1. **L'image système NVIDIA (JetPack)** :
   - Fichier : `jetson-orin-nano-devkit-super-SD-image_JP6.2.1.zip`
   - Cette image inclut **Ubuntu 22.04** et les drivers fondamentaux NVIDIA préconfigurés.

2. **Le logiciel de flash (BalenaEtcher)** :
   - Version recommandée pour Mac Silicon (M1/M2/M3) : `balenaEtcher-2.1.4-arm64.dmg`
   - [Téléchargement officiel](https://etcher.balena.io/)

## 2. Flashage de la Carte SD

1. Insérez votre carte MicroSD haute vitesse (ou votre adaptateur M.2 vers USB si vous flashez le NVMe) dans votre Mac.
2. Lancez **BalenaEtcher**.
3. **Flash from file** : Sélectionnez l'archive téléchargée `jetson-orin-nano-devkit-super-SD-image_JP6.2.1.zip`. Il n'est généralement pas nécessaire d'extraire le `.zip`, Etcher sait le lire à la volée.
4. **Select target** : Choisissez votre carte SD (vérifiez bien la taille pour ne pas flasher un disque de votre Mac par erreur !).
5. **Flash!** : Lancez la procédure. Le Mac vous demandera probablement votre mot de passe administrateur pour autoriser l'écriture bas-niveau.
6. Une fois la validation (verification) terminée, retirez la carte SD en toute sécurité.

## 3. Premier démarrage (First Boot)

Pour l'initialisation de la carte, il est obligatoire d'avoir un accès physique.

1. Insérez la carte MicroSD dans la fente sous le dissipateur thermique de la Jetson Orin Nano.
2. Branchez :
   - Un écran (Câble DisplayPort).
   - Un clavier et une souris en USB.
   - Idéalement, un câble réseau Ethernet (ou vérifiez la configuration WiFi).
3. Connectez l'alimentation (via l'entrée DC barrel jack, 19V). La carte s'allume automatiquement.
4. Suivez l'assistant de configuration Ubuntu (oem-config) :
   - Acceptez les licences NVIDIA.
   - Choisissez la langue et le fuseau horaire.
   - Créez votre nom d'utilisateur (ex: `dbot`) et votre mot de passe administrateur. **Mémorisez bien ce mot de passe, il est crucial pour le bus CAN et ROS2.**
   - Configurez la taille de la partition (RootFS) au maximum allouable.

Une fois que vous arrivez sur le bureau Ubuntu 22.04 classique, l'installation de base est terminée. Il faut maintenant configurer les accès distants pour pouvoir remettre le robot en mode serveur aveugle (Headless). Voir l'annexe [41_Acces_Distant_NoMachine](./41_Acces_Distant_NoMachine.md).
