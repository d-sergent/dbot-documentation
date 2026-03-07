# 07 - Vision et Intelligence Artificielle

## 1. Capteur Principal : Luxonis OAK-D Pro (FF)
Le choix s'est porté sur la version **Fixed Focus (FF)** pour garantir la stabilité de l'IA malgré les vibrations mécaniques des moteurs RobStride.

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

## 2. LiDAR : Unitree L2

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
