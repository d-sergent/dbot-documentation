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
- **Double IMU** : L'IMU interne de l'OAK-D est fusionnée avec celle de la Spresense pour stabiliser le regard (Gimbal V-SLAM).

## 2. LiDAR : Unitree L2
Placé sur le haut du torse ou le bassin selon la configuration.
- **Montage Inversé** : Recommandé pour minimiser l'angle mort au sol.
- **Paramètres** : 64 000 points/s, FOV 360°x90°.

## 3. Stack Logicielle (NVIDIA Isaac)
- **Isaac ROS** : Utilise les moteurs de deep learning de la Jetson pour traiter le flux OAK-D en temps réel.
- **Isaac Gym** : Utilisé pour l'apprentissage par renforcement de la marche (Deep RL), en important l'URDF mis à jour avec la masse de l'OAK-D (91g).
