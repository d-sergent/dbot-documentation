# 43. Configuration PyTorch (GPU CUDA), TensorRT & Gestion de la Mémoire sur JetPack 6.1

> **Statut** : Documenté et validé sur Jetson Orin Nano Super (JetPack 6.1, cuDNN 9, Python 3.10, CUDA 12.2).  
> **Dernière mise à jour** : Juillet 2026.

---

## ⚠️ Règle d'Or Absolue sur Jetson (À NE JAMAIS OUBLIER)

> [!CAUTION]
> **NE JAMAIS faire un simple `pip install torch` ou `pip install torchvision` !**  
> Les dépôts PyPI standard envoient des versions compilées pour PC x86 avec des sous-paquets `nvidia-*-cu13` (CUDA 13). Cela **écrasera le pilote GPU natif CUDA 12.2 de la Jetson** et entraînera l'erreur `UserWarning: CUDA initialization: The NVIDIA driver on your system is too old (found version 12060)` avec bascule forcée sur le CPU.
> 
> *Règle : Toujours installer PyTorch depuis le wheel NVIDIA JetPack officiel et installer les paquets satellites (comme `torchvision`) avec le drapeau `--no-deps`.*

---

## 🛠️ Procédure d'Installation / Restauration de PyTorch GPU

### 1. Installation du Wheel PyTorch NVIDIA JP6.1 (cuDNN 9)
```bash
# Téléchargement et installation du wheel officiel NVIDIA (JetPack 6.1 / Python 3.10)
wget https://developer.download.nvidia.com/compute/redist/jp/v61/pytorch/torch-2.5.0a0+872d972e41.nv24.08.17622132-cp310-cp310-linux_aarch64.whl
pip3 install torch-2.5.0a0+872d972e41.nv24.08.17622132-cp310-cp310-linux_aarch64.whl --force-reinstall --no-cache-dir
rm torch-2.5.0a0+872d972e41.nv24.08.17622132-cp310-cp310-linux_aarch64.whl
```

### 2. Compilation et Installation de `torchvision` Native CUDA (JP6.1)
```bash
# Cloner et installer la version v0.20.0 (alignée avec PyTorch 2.5.0a0)
git clone --branch v0.20.0 https://github.com/pytorch/vision.git torchvision_src
cd torchvision_src
MAX_JOBS=1 FORCE_CUDA=1 python3 setup.py install --user
cd ..
rm -rf torchvision_src
```

### 3. Nettoyage en cas de fausse manipulation (Présence de paquets CUDA 13 ou NumPy 2.x)
Si `pip` a téléchargé des paquets CUDA 13 parasites ou NumPy 2.x qui font chuter l'IA en mode simulation :
```bash
# Nettoyage des sous-paquets CUDA 13 parasites
pip uninstall -y cuda-toolkit nvidia-cudnn-cu13 nvidia-cublas-cu13 nvidia-cuda-runtime-cu13 nvidia-cusparse-cu13 nvidia-nccl-cu13

# Fixation de NumPy 1.x (NumPy 2.x casse matplotlib et ultralytics sur Ubuntu 22.04)
pip install "numpy<2"
```

---

## ⚡ Accélération TensorRT FP16 (.engine) de YOLO-World

Pour maximiser le taux de rafraîchissement visuel et libérer la mémoire :

```bash
# Compilation du moteur TensorRT FP16 (effectuée 1 seule fois sur la Jetson)
python3 code/scripts/vision/export_yolo_tensorrt.py
```

* **Effet de TensorRT FP16** :
  - **Latence d'inférence** : Réduite de $\sim 50\text{ ms}$ à **$\sim 15\text{ ms}$**.
  - **Cadence** : Boostée de $\approx 18\text{ FPS}$ à **$> 40\text{ FPS}$**.
  - **Graphe Autograd** : Supprimé par la quantification FP16.

---

## 📊 Analyse du Budget Mémoire (RAM / VRAM) & Conformité Architecture

La Jetson Orin Nano 8 Go dispose d'une **mémoire LPDDR5 unifiée** partagée dynamiquement entre le processeur CPU et le GPU CUDA.

### Tableau de Comparaison par rapport au Plan Master V1

| Composant / Module | Budget VRAM / RAM Alloué dans le Plan Master V1 | Empreinte Réelle Mesurée (TensorRT FP16 / YOLO-World Medium) | Marge Libre & Statut |
| :--- | :---: | :---: | :--- |
| **Vision & Triade Sémantique (YOLO-World + DepthAI)** | $\le 2.5\text{ GB}$ | **$1.2\text{ GB}$ à $1.8\text{ GB}$** | **✅ CONFORME** ($0.7\text{ Go}$ sous la limite) |
| **Services Système, OS & NoMachine** | $\approx 0.8\text{ GB}$ | **$0.7\text{ GB}$** | **✅ CONFORME** |
| **ROS2, micro-ROS & Bus CANopen Moteurs** | $\approx 1.5\text{ GB}$ | Réservez $\sim 1.0\text{ GB}$ | **✅ CONFORME** |
| **Mémoire Libre Totale Résiduelle (Headroom)** | $\ge 3.2\text{ GB}$ | **$> 4.5\text{ GB}$ Libres** | **🎉 EXCELLENT (Marge de sécurité confortable)** |

> 📌 **Verdict** : Le mode **TensorRT FP16 avec YOLO-World Medium (`v8m`)** s'inscrit **parfaitement dans les limites du plan d'architecture initial**, en laissant plus de **$4.5\text{ Go}$ de RAM unifiée libre** pour le contrôle cinématique et les nœuds ROS2.

---

## ✅ Vérification de l'Accélération Matérielle GPU

Exécuter la commande de validation :
```bash
python3 -c "import torch; print('CUDA disponible :', torch.cuda.is_available(), '| Version PyTorch :', torch.__version__)"
```

**Résultat attendu :**
```text
CUDA disponible : True | Version PyTorch : 2.5.0a0+872d972e41.nv24.08
```
