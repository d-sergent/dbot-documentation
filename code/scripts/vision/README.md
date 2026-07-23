# 👁️ scripts/vision — Scripts d'Exécution & Qualification Visuelle

Ce dossier regroupe les scripts exécutables de test sur le terrain, d'exportation de modèles et de qualification de la perception visuelle du D-Bot.

---

## 📄 Fichiers & Procédures

| Script | Utilisation & Commande |
| :--- | :--- |
| **[`test_active_gaze.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_active_gaze.py)** | **Test complet du Regard Actif (Active Gaze)**. Inférence Zero-Shot YOLO-World v2 en Français natif, fusion $3D$, poursuite prédictive d'inertie et asservissement fluide des moteurs du cou RS-05.<br>`python3 code/scripts/vision/test_active_gaze.py --target "main"` |
| **[`test_oak_tracker.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_oak_tracker.py)** | **Test Unitaire 1 (VPU ObjectTracker)**. Qualification du suivi optique matériel embarqué sur VPU Myriad X à $> 50\text{ FPS}$.<br>`python3 code/scripts/vision/test_oak_tracker.py` |
| **[`test_kalman_gaze.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_kalman_gaze.py)** | **Test Unitaire 2 (Filtre de Kalman 3D)**. Validation de la réduction du bruit *Bbox Jitter* (> 60%) et de l'estimation de vitesse/occultation.<br>`python3 code/scripts/vision/test_kalman_gaze.py` |
| **[`test_active_gaze_100hz.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_active_gaze_100hz.py)** | **Test Unitaire 4 (Boucle 100 Hz CAN)**. Mesure de la cadence du thread de commande moteur découplé à $100\text{ Hz} \pm 2\text{ Hz}$.<br>`python3 code/scripts/vision/test_active_gaze_100hz.py` |
| **[`server_active_gaze_mac.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/server_active_gaze_mac.py)** | **Serveur Compagnon Visual Grounding Mac**. API HTTP (port 8090) exécutée sur Mac M1 Max (64 Go VRAM) pour le Visual Grounding et le raisonnement multimodal complexe (LocateAnything / Cosmos).<br>`python3 code/scripts/vision/server_active_gaze_mac.py --port 8090` |
| **[`test_triad_vision.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/test_triad_vision.py)** | **Test complet de la Triade Visuelle**. Inférence Zero-Shot YOLO-World v2, fusion $3D$ OAK-D, déport VPU WLS et enregistrement de clichés incrémentaux dans `/tmp/dbot_snapshots/`.<br>`python3 code/scripts/vision/test_triad_vision.py` |
| **[`export_yolo_tensorrt.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/vision/export_yolo_tensorrt.py)** | **Exporteur TensorRT FP16 / ONNX**. Compile `yolov8m-worldv2.pt` au format `.engine` TensorRT directement sur le GPU Jetson pour booster l'inférence à $> 40\text{ FPS}$.<br>`python3 code/scripts/vision/export_yolo_tensorrt.py` |

---

## 🚀 Commandes de Test Rapide

```bash
# Tests unitaires des optimisations Active Gaze
python3 code/scripts/vision/test_oak_tracker.py
python3 code/scripts/vision/test_kalman_gaze.py
python3 code/scripts/motors/test_neck_velocity.py
python3 code/scripts/vision/test_active_gaze_100hz.py

# Test Active Gaze complet (Recentrage du cou sur objet en Français)
python3 code/scripts/vision/test_active_gaze.py --target "main"
```
