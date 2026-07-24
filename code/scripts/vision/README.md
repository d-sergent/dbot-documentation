# 👁️ scripts/vision — Scripts d'Exécution & Qualification Visuelle

Ce dossier regroupe les scripts exécutables de test sur le terrain, d'exportation de modèles et de qualification de la perception visuelle du D-Bot.

---

## 📄 Fichiers & Procédures

| Script | Utilisation & Commande |
| :--- | :--- |
| **[`test_face_tracker.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_face_tracker.py)** | **Reconnaissance & Enregistrement Faciale Nommée**. Pipeline complet SCRFD 500M (5 keypoints) + ArcFace MobileFaceNet 512-dim + Lissage temporel 5 trames + Serveur Web UI MJPEG (http://ubuntu.local:8090).<br>`python3 code/scripts/vision/test_face_tracker.py --register "David"` |
| **[`test_active_gaze.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_active_gaze.py)** | **Test complet du Regard Actif (Active Gaze)**. Inférence Zero-Shot YOLO-World v2 en Français natif, fusion 3D, poursuite prédictive d'inertie, gain dynamique Kp(e) et asservissement du cou RS-05.<br>`python3 code/scripts/vision/test_active_gaze.py --target "personne"` |
| **[`export_tensorrt.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/export_tensorrt.py)** | **Compilation 1-Clic TensorRT FP16**. Compile `yolov8m-worldv2.pt` au format `.engine` TensorRT sur le GPU Jetson pour réduire la latence à 8-12 ms (80+ FPS).<br>`python3 code/scripts/vision/export_tensorrt.py` |
| **[`test_oak_tracker.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_oak_tracker.py)** | **Test Unitaire 1 (VPU ObjectTracker)**. Qualification du suivi optique matériel embarqué sur VPU Myriad X à 60+ FPS.<br>`python3 code/scripts/vision/test_oak_tracker.py` |
| **[`test_kalman_gaze.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_kalman_gaze.py)** | **Test Unitaire 2 (Filtre de Kalman 3D)**. Validation de la réduction du bruit Bbox Jitter (> 60%) et de l'extrapolation 500 ms.<br>`python3 code/scripts/vision/test_kalman_gaze.py` |
| **[`test_active_gaze_100hz.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_active_gaze_100hz.py)** | **Test Unitaire 4 (Boucle 100 Hz CAN)**. Mesure de la cadence du thread de commande moteur découplé à 100 Hz ± 2 Hz.<br>`python3 code/scripts/vision/test_active_gaze_100hz.py` |
| **[`test_triad_vision.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_triad_vision.py)** | **Test complet de la Triade Visuelle**. Inférence Zero-Shot YOLO-World v2, fusion 3D OAK-D, déport VPU WLS et clichés dans `/tmp/dbot_snapshots/`.<br>`python3 code/scripts/vision/test_triad_vision.py` |

---

## 🚀 Commandes d'Exécution sur la Jetson

```bash
# 1. Optionnel : Compiler le moteur TensorRT FP16 (80+ FPS, latence < 10 ms)
python3 code/scripts/vision/export_tensorrt.py

# 2. Test Active Gaze complet (Recentrage du cou sur objet/personne)
python3 code/scripts/vision/test_active_gaze.py --target "personne"
```
