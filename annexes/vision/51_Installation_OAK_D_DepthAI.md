# 51 — Installation OAK-D Pro et Framework DepthAI

> *Document créé Avril 2026 — Validé en conditions réelles sur Jetson Orin Nano + NoMachine.*

Ce document détaille l'installation logicielle et matérielle de la caméra **Luxonis OAK-D Pro (Fixed Focus)** sur la Jetson Orin Nano, ainsi que la configuration du framework `depthai`.

---

## 1. Comprendre l'OAK-D Pro et DepthAI

L'OAK-D Pro (Fixed Focus) n'est pas une simple webcam, c'est une **caméra intelligente**. Elle intègre son propre processeur (VPU Intel Movidius MyriadX) qui exécute directement :
- Le calcul de la carte de profondeur (stéréo-vision)
- Les réseaux de neurones (détection de visages, objets, pose)
- L'encodage vidéo

**Avantage majeur pour le D-Bot :** Elle ne consomme pratiquement aucune ressource CPU ou GPU sur la Jetson. La Jetson ne fait que récupérer les résultats via USB !

Le framework logiciel s'appelle **DepthAI**. La version installée est la **3.5.0** (API 3.x, incompatible avec la 2.x).

---

## 2. Branchement Matériel

> [!CAUTION]
> L'OAK-D Pro nécessite un port **SuperSpeed USB 3.0** pour transférer les flux haute résolution.

1. Utilisez le câble **USB-C vers USB-A** fourni avec la caméra.
2. Branchez le côté USB-A sur l'un des ports **bleus** (USB 3.2 Gen 2) de la Jetson Orin Nano.
3. Vérifiez la reconnaissance sous Linux :
   ```bash
   lsusb | grep 03e7
   ```
   *L'identifiant `03e7:2485` correspond au composant Intel Movidius MyriadX.*

---

## 3. Installation du Logiciel (sur la Jetson)

### 3.1 Installer les paquets requis

```bash
pip3 install depthai opencv-python
```

### 3.2 Configurer les droits USB — règle udev (obligatoire)

Sans cette étape, Python obtient une erreur `Insufficient permissions` au démarrage.

```bash
# Créer la règle udev pour l'OAK-D Pro
sudo tee /etc/udev/rules.d/99-depthai.rules > /dev/null <<'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="03e7", MODE="0666"
EOF

# Appliquer les règles
sudo udevadm control --reload-rules && sudo udevadm trigger

# Débrancher et rebrancher la caméra (ou redémarrer la Jetson)
```

> [!IMPORTANT]
> Cette règle udev est **indispensable**. Sans elle, DepthAI affiche `No available devices` même si la caméra est détectée par `lsusb`.

---

## 4. API DepthAI 3.x — Changements par rapport à 2.x

> [!WARNING]
> L'API DepthAI 3.x est **incompatible** avec les exemples écrits pour la 2.x.

| Ancien (DepthAI 2.x) | Nouveau (DepthAI 3.x) |
| :--- | :--- |
| `pipeline.create(dai.node.ColorCamera)` | `pipeline.create(dai.node.Camera).build(socket)` |
| `cam.setBoardSocket(...)` | Passé directement dans `.build()` |
| `pipeline.create(dai.node.XLinkOut)` | N'existe plus — utiliser `requestOutput()` |
| `dai.Device(pipeline)` | N'existe plus — utiliser `pipeline.start()` |
| `device.getOutputQueue("rgb")` | `video_out.createOutputQueue()` |
| Boucle sur `True` | Boucle sur `pipeline.isRunning()` |

**Pattern correct DepthAI 3.x :**

```python
with dai.Pipeline() as pipeline:
    cam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)
    video_out = cam.requestOutput((640, 360), dai.ImgFrame.Type.BGR888p)
    queue = video_out.createOutputQueue()   # ← obligatoire !

    pipeline.start()

    while pipeline.isRunning():
        frame = queue.get().getCvFrame()
        # ... traitement ...
```

---

## 5. Test Fonctionnel (Flux RGB)

Le script de test est inclus dans le code source du D-Bot (`code/scripts/vision/test_camera.py`).

### 5.1 Mode capture disque (compatible NoMachine — recommandé)

```bash
cd ~/dbot && git pull
python3 code/scripts/vision/test_camera.py
```

Le script :
1. Se connecte à la caméra
2. Laisse **30 frames** de warm-up pour que l'auto-exposition se stabilise
3. Sauvegarde **5 captures JPEG** dans `/tmp/dbot_frames/`
4. Quitte proprement

Résultat attendu :
```
✅ Caméra connectée avec succès.
⏳ Warm-up auto-exposition (30 frames)...
✅ Frame 0 sauvegardée : /tmp/dbot_frames/frame_000.jpg  [640×360]
...
✅ 5 images sauvegardées dans /tmp/dbot_frames/
```

### 5.2 Visualiser les captures

```bash
eog /tmp/dbot_frames/   # Eye of GNOME (Ubuntu)
```

### 5.3 Mode affichage temps réel

> [!NOTE]
> Ce mode fonctionne uniquement si vous avez un écran directement branché sur la Jetson. Via NoMachine, la fenêtre OpenCV s'affiche noire (limitation du rendu graphique).

```bash
python3 code/scripts/vision/test_camera.py --display
```

### 5.4 Mode Affichage Local Réseau (Stream Wi-Fi)

La méthode la plus confortable (et recommandée) pour visualiser le flux tout en codant, sans écran branché et pour contourner les limitations de rendu de NoMachine, est de lancer le serveur de streaming embarqué. Le flux s'affichera directement dans le navigateur Safari/Chrome de votre Mac.

1. **Sur la Jetson** (assurez-vous d'avoir installé `flask`) :
   ```bash
   python3 code/scripts/vision/stream_camera.py
   ```
2. **Sur votre Mac** (ou téléphone connecté au même Wi-Fi) :
   Ouvrez un navigateur Web et accédez à : `http://<IP_DE_LA_JETSON>:5000`

Vous obtiendrez un rendu en temps réel !

> [!TIP]
> Pour **arrêter la caméra et fermer le stream**, allez simplement dans le terminal de la Jetson et appuyez sur la combinaison clavier **`Ctrl + C`**.

---

## 6. Dépannage

| Problème | Cause Probable | Solution |
| :--- | :--- | :--- |
| **`Insufficient permissions`** | Règle udev manquante | Créer `/etc/udev/rules.d/99-depthai.rules` (voir §3.2) |
| **`No available devices`** | Caméra non reconnue ou droits manquants | Vérifier `lsusb \| grep 03e7`, puis appliquer la règle udev |
| **`AttributeError: XLinkOut`** | Code écrit pour l'API 2.x | Utiliser le pattern DepthAI 3.x (voir §4) |
| **`incompatible constructor arguments (Device)`** | `dai.Device(pipeline)` n'existe plus | Utiliser `pipeline.start()` |
| **Fenêtre OpenCV noire via NoMachine** | Limitation du rendu graphique distant | Utiliser le mode capture disque (défaut) |
| **Images trop sombres** | Auto-exposition pas stabilisée | Le warm-up de 30 frames est intégré dans le script |
| **`QFontDatabase: Cannot find font`** | Qt/OpenCV sans polices système | Avertissement sans gravité, n'affecte pas le flux vidéo |
