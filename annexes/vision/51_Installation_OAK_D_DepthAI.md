# 51 — Installation OAK-D Pro et Framework DepthAI

> *Document créé Avril 2026 — Configuration de la vision stéréo et IA embarquée du D-Bot.*

Ce document détaille l'installation logicielle et matérielle de la caméra **Luxonis OAK-D Pro** sur la Jetson Orin Nano, ainsi que la configuration du framework `depthai` nécessaire pour interagir avec elle.

---

## 1. Comprendre l'OAK-D Pro et DepthAI

L'OAK-D Pro n'est pas une simple webcam, c'est une **caméra intelligente**. Elle intègre son propre processeur (VPU Myriad X) qui exécute directement :
- Le calcul de la carte de profondeur (stéréo-vision)
- Les réseaux de neurones (détection de visages, objets, pose)
- L'encodage vidéo

**Avantage majeur pour le D-Bot :** Elle ne consomme pratiquement aucune ressource CPU ou GPU sur la Jetson. La Jetson ne fait que récupérer les résultats via USB !

Le framework logiciel qui permet de communiquer avec l'OAK-D s'appelle **DepthAI**.

---

## 2. Branchement Matériel

> [!CAUTION]
> L'OAK-D Pro nécessite un port **SuperSpeed USB 3.0** pour transférer les flux haute résolution.

1. Utilisez le câble **USB-C vers USB-A** fourni avec la caméra.
2. Branchez le côté USB-A sur l'un des ports **bleus** (USB 3.2 Gen 2) de la Jetson Orin Nano.
3. Vérifiez la bonne reconnaissance sous Linux :
   ```bash
   lsusb | grep 03e7
   ```
   *L'identifiant `03e7:2485` correspond au composant Intel Movidius MyriadX utilisé par Luxonis.*

---

## 3. Installation du Logiciel (sur la Jetson)

Puisque nous utilisons Python pour orchestrer le robot, l'installation se fait directement via `pip3`.

### Installer les paquets requis
Dans le terminal de la Jetson :

```bash
# 1. DepthAI (framework principal) et OpenCV (pour l'affichage d'images)
pip3 install depthai opencv-python
```

*(Note : `opencv-python` est requis pour utiliser `cv2.imshow`, qui permet d'afficher le flux vidéo à travers notre bureau à distance NoMachine).*

### Optionnel : Vérifier l'installation globale
Si vous avez installé le package robot `dbot` en mode développement (Doc 43), les dépendances de vision peuvent se vérifier via :
```bash
cd ~/dbot/code
pip3 install -e .[vision]
```

---

## 4. Test Fonctionnel (Flux RGB)

Un script de test est inclus dans le code source officiel du D-Bot. Il configure la caméra couleur (RGB) en 1080p, la relie à la Jetson, et affiche l'image en temps réel.

### Lancer le test

Sur le bureau de la Jetson (via NoMachine) :

```bash
cd ~/dbot
python3 code/scripts/vision/test_camera.py
```

### Résultat attendu :
1. Le terminal affiche l'initialisation du pipeline DepthAI.
2. Une nouvelle fenêtre **"OAK-D Pro - Vue D-Bot"** s'ouvre sur le bureau.
3. L'image de la caméra s'affiche de manière fluide (~30 FPS).
4. Cliquez sur la vidéo vidéo et appuyez sur la touche **`q`** pour quitter proprement.

---

## 5. Dépannage

| Problème | Cause Probable | Solution |
| :--- | :--- | :--- |
| **Erreur `No available devices`** | Caméra non branchée ou en USB 2.0 | Vérifiez que le câble est bien sur le port USB Bleu de la Jetson. |
| **L'image met du temps à s'afficher** | Compilation initiale du pipeline | C'est normal lors du premier lancement, les lancements suivants seront instantanés. |
| **Erreur lors de l' `import cv2`** | `opencv-python` manquant | Exécutez `pip3 install opencv-python`. |
| **`QXcbConnection: Could not connect to display`** | SSH sans interface graphique | Vous devez lancer le script de test depuis le Terminal du bureau **NoMachine**, pas via une simple connexion SSH texte. |
