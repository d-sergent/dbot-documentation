# 🦾 Spécifications Finales : 04 Perception et Sensors (D‑Bot – Version V1.x)

> **Version du document** : Juillet 2026 – Consolidation de la stratégie visuelle et audio Master V1.  
> **Portée** : Configuration matérielle et logicielle validée pour la version actuelle (V1.x).

---

## 1. Vue d’Ensemble & Répartition Tri-Niveaux (Jetson / VPU / Mac)

Le module **Perception & Sensors** regroupe :

| Sous‑système | Capteur principal | Position / Support | Rôle & Inférence |
| :--- | :--- | :--- | :--- |
| **Audio & DoA** | **Seeed ReSpeaker XVF‑3800** | Sommet du crâne | Capture 4 mic MEMS, DoA 360°, VAD matériel, AEC et Barge-In (coupure `aplay` immédiate). |
| **Vision Réflexe Temps Réel** | **Luxonis OAK‑D Pro FF** + GPU Jetson | Front de la tête (2 DOF cou RS-05) | Inférence sémantique Zero-Shot YOLO-World v2 TensorRT FP16 ($> 40\text{ FPS}$, latence $\sim 15\text{ ms}$, VRAM $\sim 1.2\text{ Go}$). |
| **Déport VPU OAK-D** | **Myriad X (4 TOPS)** | Intégré à l'OAK-D Pro | Filtrage de profondeur matériel WLS (gain 25% CPU Jetson) + `SpatialLocationCalculator` ($Z < 500\text{ mm}$ à $< 5\text{ ms}$). |
| **Cognition Spatiale 3D (Déporté Mac)** | **Mac M1 Max (64 Go)** | Déporté via gRPC/HTTP | Inférence multimodale **NVIDIA Cosmos 3D Edge / LocateAnything-3B** pour le regard actif (*Active Gaze*) et la planification. |
| **LiDAR 3D** | **Unitree L2** | Haut du torse (fixe) | 360° × 96° FOV, cartographie SLAM globale. |
| **IMU Torse** | **Bosch BMI270** | Centre de masse du torse | Référence inertielle équilibre et odométrie. |
| **IMU Tête** | **BNO085** (intégré OAK-D) | Tête (mobile) | Stabilisation du regard (VOR) et V-SLAM. |

---

## 2. Spécifications Matérielles Validées

| Élément | Référence | Caractéristiques détaillées | Interface | Masse |
| :--- | :--- | :--- | :--- | :--- |
| **Module audio** | **Seeed ReSpeaker XVF-3800** | XMOS XVF-3800, 4 MEMS, DoA 360°, AEC matériel | USB 2.0 | ~30 g |
| **Haut-parleur** | HP 5 W 8 Ω (40 mm) | Puissance 5 W RMS, branché sur JST ReSpeaker | JST 1.25 mm | ~20 g |
| **Caméra depth** | **Luxonis OAK-D Pro FF** | Myriad X 4 TOPS, RGB 12 MP, Stéréo Active IR, IMU 9-axes | USB-C 3.1 | 91 g |
| **LiDAR 3D** | **Unitree L2** | 360° × 96° FOV, 64 k pts/s, IP52 | USB-C 3.0 | 230 g |
| **Moteurs du cou** | **RS-05** (pan + tilt) | 48V DC, 1.6 N·m nom / 5.5 N·m pic, Direct Drive | Bus CAN (1 Mbps) | – |

---

## 3. Architecture Logicielle & Flux de Données

```
[ Caméra OAK-D Pro ] ──► [ VPU Myriad X : Depth & Filtre WLS & SpatialLocation (Alerte < 5 ms) ]
                               │
                               ├─► [ GPU Jetson Orin Nano : YOLO-World v2 TensorRT FP16 (> 40 FPS) ]
                               │
                               └─► [ Réseau Hybride HTTP/gRPC ] ──► [ Mac M1 Max : NVIDIA Cosmos 3D Edge ]
```

---

*Fin du document consolidé – 04 Perception et Sensors (V1.x).*