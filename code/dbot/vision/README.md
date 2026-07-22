# 👁️ dbot.vision — Package de Perception Visuelle & Fusion Spatiale 3D

Ce sous-module contient la brique de perception visuelle temps réel du D-Bot, couplant l'IA sémantique Open-Vocabulary et la géométrie 3D de la caméra OAK-D Pro.

---

## 📄 Fichiers & Rôles

| Fichier | Rôle & Description |
| :--- | :--- |
| **[`yolo_world.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/vision/yolo_world.py)** | Détecteur sémantique Zero-Shot YOLO-World v2 (`yolov8m-worldv2`). Gère la détection multi-boîtes hiérarchique avec palette de couleurs BGR distinctes par classe, les prompts CLIP en langage naturel et l'accélération TensorRT FP16 / ONNX. |
| **[`oak_camera.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/vision/oak_camera.py)** | Interface matérielle Luxonis OAK-D Pro. Déporte le filtrage de profondeur stéréo WLS (gain 25% CPU Jetson) et le nœud `SpatialLocationCalculator` ($Z < 500\text{ mm}$ à $< 5\text{ ms}$) sur le VPU Myriad X. |
| **[`spatial_fusion.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/vision/spatial_fusion.py)** | Calculateur de géométrie $3D$. Fusionne les Bounding Boxes $2D$ produites par YOLO-World avec la carte de profondeur stéréo pour extraire les coordonnées physiques réelles $[X, Y, Z]$ en mm. |
| **[`face_tracker.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/vision/face_tracker.py)** | Détecteur spatial de visages basé sur l'ancien modèle `face-detection-retail-0005` (VPU). |
| **[`depth_reflex.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/vision/depth_reflex.py)** | Boucle réflexe rapide d'évitement sur seuil de profondeur. |

---

## ⚡ Utilisation Rapide

```python
from dbot.vision.oak_camera import DbotCamera
from dbot.vision.yolo_world import YoloWorldDetector
from dbot.vision.spatial_fusion import SpatialFusion

# Initialisation
cam = DbotCamera(enable_depth=True)
detector = YoloWorldDetector(model_name="yolov8m-worldv2.pt", classes=["main", "telephone", "personne"])
fusion = SpatialFusion()

cam.start()

# Lecture & Inférence
frame_rgb = cam.get_frame()
frame_depth = cam.get_depth_frame()
dets_2d, latency = detector.detect(frame_rgb)
dets_3d = fusion.compute_spatial_3d(dets_2d, frame_depth)
```
