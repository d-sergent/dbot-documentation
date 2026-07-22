# 👁️ scripts/vision — Scripts d'Exécution & Qualification Visuelle

Ce dossier regroupe les scripts exécutables de test sur le terrain, d'exportation de modèles et de qualification de la perception visuelle du D-Bot.

---

## 📄 Fichiers & Procédures

| Script | Utilisation & Commande |
| :--- | :--- |
| **[`test_triad_vision.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_triad_vision.py)** | **Test complet de la Triade Visuelle**. Inférence Zero-Shot YOLO-World v2, fusion $3D$ OAK-D, déport VPU WLS et enregistrement de clichés incrémentaux dans `/tmp/dbot_snapshots/`.<br>`python3 code/scripts/vision/test_triad_vision.py` |
| **[`export_yolo_tensorrt.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/export_yolo_tensorrt.py)** | **Exporteur TensorRT FP16 / ONNX**. Compile `yolov8m-worldv2.pt` au format `.engine` TensorRT directement sur le GPU Jetson pour booster l'inférence à $> 40\text{ FPS}$.<br>`python3 code/scripts/vision/export_yolo_tensorrt.py` |
| **[`stream_camera.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/stream_camera.py)** | Serveur de streaming Web MJPEG Flask pour visualiser le flux caméra à distance. |

---

## 🚀 Commande de Test Rapide

```bash
python3 code/scripts/vision/test_triad_vision.py
```
