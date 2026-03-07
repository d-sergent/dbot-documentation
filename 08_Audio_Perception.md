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

## 2. Stratégie IMU (Fusion Multi-Capteurs)

Le D-Bot exploite **3 IMUs** positionnées stratégiquement, chacune avec un rôle clairement défini :

### Matrice des Rôles IMU

| IMU | Capteur | Position | Fréquence | Rôle Principal | Rôle Secondaire |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **IMU Torse** | **BMI270** (Add-on Spresense) | Torse (centre de masse) | **416 Hz** | 🔴 **Équilibre bipède** | Détection de chute (Watchdog) |
| **IMU Tête** | BNO085/BMI270 (OAK-D Pro) | Front (tête) | 100 Hz | **Stabilisation regard** | V-SLAM visuel |
| **IMU LiDAR** | IMU intégrée (Unitree L2) | Haut du torse | **1000 Hz** | **Odométrie LiDAR** (LIO-SLAM) | Fusion avec V-SLAM |

### Architecture de Fusion

```
IMU Torse (BMI270, 416 Hz)
  → Spresense (Temps Réel)
    → Contrôle d'équilibre (hanche/cheville Roll)
    → Détection chute si Jetson hors ligne
    → Publie sur ROS2 : /imu/balance

IMU Tête (OAK-D Pro, 100 Hz)
  → Jetson (DepthAI / Isaac ROS)
    → Stabilisation du regard (compensation cou Pan/Tilt)
    → Odométrie visuelle (V-SLAM)
    → Publie sur ROS2 : /imu/head

IMU LiDAR (Unitree L2, 1000 Hz)
  → Jetson (ROS2 driver L2)
    → Fusion LiDAR-Inertielle (LIO-SLAM)
    → Localisation et cartographie
    → Publie sur ROS2 : /imu/lidar
```

### ⚠️ Erreur Fréquente à Éviter

L'IMU de l'OAK-D (dans la tête) **ne doit PAS être utilisée pour l'équilibre du corps**. La tête bouge indépendamment du torse via les 2 DOF du cou (Pan RS-05 + Tilt RS-05). Son IMU mesure l'orientation de la **tête**, pas du **corps**.

> **Règle** : L'IMU la plus proche du centre de masse = IMU d'équilibre. C'est le **BMI270 dans le torse** (via Spresense).

### Note : Migration depuis SensiEDGE CommonSense

La carte **SensiEDGE CommonSense** (IMU LSM6DSOX + capteurs environnementaux) était initialement prévue mais **n'est pas disponible au grand public** (réservée aux clients professionnels).

**Remplacement** : **BMI270 Add-on Board** (Switch Science / Bosch) — compatible Spresense, 6 axes (accéléromètre + gyroscope), I2C/SPI, bibliothèque Arduino disponible.

> [!NOTE]
> **Alternative haute précision** : Sony a sorti en février 2025 le **Spresense Multi-IMU Add-on Board** embarquant 16 MEMS IMUs fusionnées, atteignant une précision comparable aux gyroscopes à fibre optique (FOG). Cette carte est recommandée si une précision extrême est requise (marche dynamique sur terrain complexe).

### Perte des Capteurs Environnementaux SensiEDGE

La SensiEDGE apportait aussi : température (HTS221), pression (LPS22HH), qualité d'air (SGP40), magnétomètre (LIS2MDL). Si ces capteurs restent souhaités pour la surveillance interne du torse :
- **Thermistance** (~$1) : Collée sur les moteurs RS-04 les plus puissants → ADC Spresense
- **Magnétomètre** : Non critique (pas de cap magnétique nécessaire pour un robot d'intérieur)
- **Qualité d'air** : Non critique pour un prototype V1
