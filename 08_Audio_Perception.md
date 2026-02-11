# 08 - Audio et Perception Sensorielle

## 1. Système Audio Sony Spresense
L'architecture audio est conçue pour l'interaction sociale et la localisation spatiale des sons.

### Configuration Microphones (Audit)
- **Standard (8 micros)** : Utilisation de microphones **MEMS numériques (PDM)**.
- **Placement stratégique** : 
    - 2x Oreilles
    - 1x Torse (Face)
    - 1x Nuque (Dos)
    - + 4x Additionnels pour le beamforming 3D.
- **Câblage** : Utiliser impérativement des **câbles blindés** pour éviter que les interférences des antennes (LTE/Wifi) ou des moteurs ne créent de "buzz" audio.

### Isolation Acoustique
- **Filtrage Mécanique** : Les microphones doivent être montés sur des supports en **TPU souple** pour isoler les capteurs des vibrations haute fréquence des moteurs RobStride.
- **Synchronisation** : La Spresense garantit une capture synchronisée à **192 kHz**, indispensable pour le calcul du TDOA (Time Difference of Arrival).

## 2. Fusion de Capteurs (IMU)
Le D-bot gère une **Double IMU** pour une stabilité maximale :
1.  **IMU Tête (Spresense)** : Référence pour la stabilisation du regard et le V-SLAM.
2.  **IMU Torse (LiDAR/Jetson)** : Référence pour l'équilibre global et la compensation de la marche.
- **Synergie** : Le décalage entre les deux IMU permet de détecter les flexions structurelles du châssis en temps réel.
