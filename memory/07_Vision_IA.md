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
- **Rôle dans la stratégie IMU** : Voir [Stratégie IMU](./08_Audio_Perception.md) pour la répartition des rôles (IMU tête vs IMU torse vs IMU LiDAR).

## 2. LiDAR : Unitree L2 (Option V2)

### Position : Haut du Torse (avant le cou)
- **Montage** : Fixé sur le haut du torse, devant la base du cou, **incliné de 10-20° vers l'avant**.
- **Orientation** : Légèrement incliné vers le sol pour maximiser la détection d'obstacles proches et le SLAM au sol.
- **Justification du placement** :
    - ✅ **Pas de câble à passer dans le cou** (contrairement au placement sur la tête)
    - ✅ **Position stable** : le torse bouge moins que la tête (pas de vibrations Pan/Tilt)
    - ✅ **FOV 360°×90°** dégagé (les bras n'occultent que partiellement en position levée)
    - ⚠️ **Occlusion partielle** par les bras lors de manipulation frontale — compensée par l'OAK-D Pro (vision stéréo)
- **IMU intégrée** : 3 axes accéléromètre + 3 axes gyroscope, 1 kHz sampling. Utilisée pour la **fusion odométrique LiDAR-inertielle** (LIO-SLAM).
- **Paramètres** : 128 000 pts/s bruts (64 000 effectifs), portée 30m, zone aveugle 0.05m.

## 3. Stack Logicielle (NVIDIA Isaac)
- **Isaac ROS** : Utilise les moteurs de deep learning de la Jetson pour traiter le flux OAK-D en temps réel.
- **Isaac Gym** : Utilisé pour l'apprentissage par renforcement de la marche (Deep RL), en important l'URDF mis à jour avec la masse de l'OAK-D (91g).
