# 07 - Vision et Intelligence Artificielle

## 1. Capteur Principal : Luxonis OAK-D Pro (FF) ⭐ CONFIRMÉ (Mars 2026)
Le choix s'est porté sur la version **Fixed Focus (FF)** pour garantir la stabilité de l'IA malgré les vibrations mécaniques des moteurs RobStride.

### 1.1 Comparatif des Caméras de Profondeur (État de l'Art — Mars 2026)

Le marché des caméras de profondeur pour la robotique a évolué depuis le choix initial. Voici l'analyse comparative des alternatives envisagées :

| Critère | **OAK-D Pro FF** ⭐ | **Orbbec Gemini 335** | **OAK-D S2** | **Intel RealSense D435i** | **OAK-D SR** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Prix** | ~399 € | ~264-359 € | ~249 € | ~300 € | ~199 € |
| **Poids** | 91g | 97g | 68g | 72g | ~60g |
| **Dimensions** | 97×29×23 mm | ~comparable | Plus petit | 90×25×25 mm | Très compact |
| **Vision nocturne (IR)** | ✅ Laser + LED | ❌ | ❌ | ❌ | ❌ |
| **IA embarquée (VPU)** | ✅ 4 TOPS (Myriad X) | ❌ (ASIC prof.) | ✅ 4 TOPS | ❌ | ✅ 4 TOPS |
| **Caméra RGB** | 12 MP (IMX378) | 1080p | 12 MP | 1080p | 1 MP |
| **Portée profondeur** | 70cm – 12m | 10cm – 20m+ | 20cm – 10m | 15cm – 10m | 30cm – 1m |
| **IMU intégré** | ✅ 9 axes (BNO085) | ❌ | ✅ 9 axes | ✅ 6 axes | ✅ 6 axes |
| **Résistance poussière** | ❌ | ✅ IP5X | ❌ | ❌ | ❌ |
| **SDK / Ecosystem** | DepthAI (ROS2) | Orbbec SDK (ROS2) | DepthAI (ROS2) | librealsense (ROS2) | DepthAI (ROS2) |

### 1.2 Justification du Choix OAK-D Pro FF pour la Tête du D-Bot

L'OAK-D Pro FF est le **seul** capteur qui combine ces 4 atouts critiques pour un robot humanoïde :

1. **IA embarquée (4 TOPS)** : Détection d'objets, reconnaissance faciale et tracking 3D directement sur le VPU, sans consommer de GPU sur la Jetson → latence réduite.
2. **Vision nocturne active** : Le projecteur IR à 4700 points + LED IR flood permettent au robot de percevoir la profondeur dans le noir total (déplacement nocturne, pièces sombres).
3. **Caméra RGB 12 MP** : Résolution suffisante pour la reconnaissance faciale, la lecture de texte, et le streaming vidéo HD.
4. **IMU 9 axes** : Fusion capteur pour la stabilisation du regard et le Visual-SLAM (V-SLAM).

> ⚠️ **Limitation connue** : La portée minimale de 70cm signifie que le robot ne voit pas nettement les objets très proches de son visage. Pour la manipulation d'objets (mains), une caméra courte portée complémentaire sera nécessaire (cf. section 1.3).

### 1.3 Caméras Complémentaires (Futures — Poignets/Mains)

Pour de futures itérations avec des mains préhensiles, deux options sont à surveiller :

| Option | Portée min. | Intérêt |
| :--- | :---: | :--- |
| **Orbbec Gemini 305** (CES 2026) | 4 cm | Conçue pour montage au poignet de robot, compatible Jetson Thor |
| **Luxonis OAK-D SR** | 30 cm | Ultra-compact, 60g, idéal pour le guidage de préhension |

### Intégration Mécanique
Pour un encastrement parfait dans le visage du robot :
- **Dimensions du perçage** : **98 x 30 mm** (prévoir +0.5 mm de tolérance).
- **Fixation** : 2x vis M3, entraxe de **75 mm**, centrées.
- **Passage Câble** : Encoche de **18 mm** en bas pour le connecteur USB-C coudé.
- **Orientation** : Inclinaison de **-10° à -15°** vers le sol recommandée pour détecter les obstacles proches.

### Atouts Techniques (Audit)
- **Stéréo Active** : Contrairement à la version Lite, la Pro dispose d'un projecteur IR permettant de voir la profondeur même sur des surfaces sans texture (murs blancs unis).
- **IMU Intégrée (BNO085/BMI270)** : Utilisée **uniquement pour la stabilisation du regard** et le V-SLAM. ⚠️ **Ne doit PAS servir pour l'équilibre du corps** car l'OAK-D est dans la tête qui bouge indépendamment du torse (2 DOF cou).
- **Rôle dans la stratégie IMU** : Voir [18 — Stratégie IMU](./18_Strategie_IMU_Fusion.md) pour la répartition des rôles (IMU tête vs IMU torse vs IMU LiDAR).


- **Rôle de la Vision** : Perception locale, détection d'obstacles rapprochés (0-10m), reconnaissance d'objets et V-SLAM.
- **Rôle du LiDAR** : SLAM global 360°, cartographie à longue portée (30m) et odométrie LiDAR-Inertielle (LIO-SLAM).
- **Fusion** : Les flux sont fusionnés dans **RTAB-Map** pour une localisation redondante et précise.

> 👉 Pour l'étude technique complète du LiDAR, son montage sur le torse et la stratégie de fusion : **[19 — Perception Spatiale & LiDAR](./19_Perception_Spatiale_LiDAR.md)**.


## 3. Implémentation Logicielle (Mai 2026)
Le système de vision est désormais structuré autour de deux modules Python cœurs :
- **`code/dbot/vision/oak_camera.py`** : Gère l'accès bas niveau à la caméra, le flux RGB et le contrôle des projecteurs IR (Vision Nocturne).
- **`code/dbot/vision/face_tracker.py`** : Implémente le **Spatial Face Detection**. Le calcul de la position 3D (X, Y, Z) est fait intégralement sur le VPU de l'OAK-D, ne consommant aucune ressource sur la Jetson.

### 3.1 Stack Logicielle et Dépendances
- **API** : **DepthAI v2.24.0 obligatoire**. L'API 3.x (expérimentale) casse la compatibilité avec le réseau de détection spatiale (`MobileNetSpatialDetectionNetwork`).
  ```bash
  pip3 install depthai==2.24.0 --force-reinstall
  ```
- **Modèle IA** : `face-detection-retail-0005`. Doit être téléchargé et compilé spécifiquement via l'outil officiel :
  ```bash
  python3 -m pip install blobconverter
  python3 -c "import blobconverter; blobconverter.from_zoo(name='face-detection-retail-0005', shaves=4, output_dir='/home/david/dbot/models', version='2021.4')"
  ```

### 3.2 Gestion du Champ de Vision (FOV)
Pour conserver le **vrai champ de vision grand angle (81°)** du capteur Sony IMX378 de l'OAK-D, il ne faut **pas** régler la caméra sur 1080p (ce qui provoque un *Center Crop*).
La stratégie implémentée dans `face_tracker.py` est :
1. Capturer l'image complète en **4K** (`THE_4_K`).
2. Utiliser l'ISP interne pour réduire à **640x360** (`setIspScale(1, 6)`).
Cela offre une image 16:9 parfaite sans surcharge USB, pendant que l'IA tourne en parallèle sur un crop de 300x300.

### 3.3 Mode de Débogage Visuel (Serveur Web)
L'affichage classique via `cv2.imshow` pose des problèmes de crash OpenGL/Qt (`qt.qpa.xcb`) lorsqu'il est utilisé à travers NoMachine ou SSH.
Pour contourner cela, le script de démo intègre un **Serveur Web MJPEG (Flask)**.
- **Lancement** : `./code/scripts/behaviors/start_look_nomachine.sh` (qui appelle le script Python avec le flag `--web`).
- **Visualisation** : Depuis n'importe quel navigateur sur le réseau à l'adresse `http://<IP_JETSON>:5000`.
