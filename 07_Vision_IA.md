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

### 3.1 Stack Logicielle
- **API** : DepthAI v2 (Stable).
- **Modèle IA** : `face-detection-retail-0005` (Optimisé OpenVINO).
- **Fusion** : Intégration prévue dans **Isaac ROS** pour la navigation et la stabilisation du regard.

### 3.2 Scripts de démarrage
- **`start_look_autonomous.sh`** : Lance le robot en mode détection pure (Headless).
- **`start_look_nomachine.sh`** : Lance le robot avec retour vidéo temps réel.
