# 43. Configuration PyTorch (GPU CUDA) & VLM sur JetPack 6.1

> **Statut** : Documenté et validé sur Jetson Orin Nano Super (JetPack 6.1, cuDNN 9, Python 3.10).  
> **Date** : Juillet 2026.

---

## ⚠️ Règle d'Or Absolue sur Jetson (À NE JAMAIS OUBLIER)

> [!CAUTION]
> **NE JAMAIS faire un simple `pip install torch` ou `pip install torchvision` !**  
> Les dépôts PyPI standard envoient des versions compilées pour PC x86/CUDA 13. Cela **écrasera la version NVIDIA JetPack GPU** par une version CPU/incompatible, cassant immédiatement CUDA et désactivant l'accélération matérielle.
> 
> *Règle : Toujours installer PyTorch depuis les wheels NVIDIA Redist et installer les paquets satellites (comme `torchvision`) avec le drapeau `--no-deps`.*

---

## 🛠️ Procédure d'Installation / Restauration de PyTorch GPU

### 1. Installation du Wheel PyTorch NVIDIA JP6.1 (cuDNN 9)
```bash
# Téléchargement du wheel officiel NVIDIA (JetPack 6.1 / Python 3.10)
wget https://developer.download.nvidia.com/compute/redist/jp/v61/pytorch/torch-2.5.0a0+872d972e41.nv24.08.17622132-cp310-cp310-linux_aarch64.whl -O torch-jp61.whl

# Installation forcée sans passer par le cache pip
pip3 install torch-jp61.whl --force-reinstall --no-cache-dir

# Suppression du fichier d'installation
rm torch-jp61.whl
```

### 2. Installation de `torchvision` sans casser `torch`
```bash
pip3 install torchvision --no-deps
```

### 3. Résolution de la dépendance `cuSPARSELt` (JetPack 6.1)
Sur JetPack 6.1, PyTorch 2.5 requiert `libcusparseLt.so.0`.
```bash
# Installation via pip
pip3 install nvidia-cusparselt-cu12

# Ajout permanent du chemin au ~/.bashrc
echo 'export LD_LIBRARY_PATH=$HOME/.local/lib/python3.10/site-packages/nvidia/cusparselt/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

---

## 📦 Dépendances Spécifiques pour Modèles VLM (LocateAnything / Transformers)

### 1. Mise à jour de Pillow (PIL)
*Problème résolu :* L'erreur `AttributeError: module 'PIL.Image' has no attribute 'Resampling'` est due à une version obsolète de PIL sur JetPack.
```bash
pip3 install --upgrade Pillow transformers accelerate bitsandbytes
```

### 2. Contournement `decord` sur ARM64 (Mock Python)
`decord` est une bibliothèque de décodage vidéo qui n'a pas de wheels PyPI pour ARM64 (`aarch64`).
Pour valider l'import des modèles VLM (comme `nvidia/LocateAnything-3B`) traitant des images fixes 2D, injecter ce mock au début de votre script Python :

```python
import sys, types
try:
    import decord
except ImportError:
    decord_mock = types.ModuleType("decord")
    decord_mock.VideoReader = None
    sys.modules["decord"] = decord_mock
```

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
