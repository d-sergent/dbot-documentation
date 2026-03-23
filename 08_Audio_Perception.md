# 08 - Audio et Perception Sensorielle

## 1. Cerveau IA (Jetson Orin Nano Super)
Le cœur du traitement audio et cognitif du D-Bot est la **NVIDIA Jetson Orin Nano Super** (40 TOPS). Grâce à ses *Tensor Cores*, le robot fait tourner la suite logicielle **NVIDIA Riva** intégralement en local (sans serveur cloud, latence quasi nulle) :
- **ASR (Speech-to-Text)** : Compréhension de la parole gérée par le DSP de l'IA.
- **NLP** : Analyse de l'intention humaine.
- **TTS (Text-to-Speech)** : Voix de synthèse naturelle.

> *Marge Processeur : La marche (CAN), la vision (OAK-D), le beamforming et l'audio IA (Riva) consomment environ 52% du processeur au maximum, laissant 48% de marge de sécurité.*

## 2. Architecture Audio Hybride (Double Système)
Le robot adopte une configuration "Luxe" séparant la localisation spatiale de la compréhension pure de la parole.

### 2.1 Rôles des Systèmes
- **Matrice 8-micros** (L'Ouïe Spatiale) : Son but unique est le **DoA (Direction of Arrival)**. En tâche de fond, elle localise le son et s'interface avec ROS2 pour ordonner au cou (Pan/Tilt) d'orienter le masque vers l'interlocuteur.
- **Système DSP (Type Jabra/Anker)** (L'Écoute IA) : Son annulation d'écho matérielle (AEC) filtre le bruit de ses propres moteurs et de son propre haut-parleur. Il capte "proprement" les mots pour l'ASR (Riva).

### 2.2 Câblage et Alimentation (EMI & USB)
La Jetson, dépourvue de prise audio native, nécessite un intermédiaire.
- **Concentrateur** : Les deux systèmes audio sont branchés sur un **Hub USB 3.0 Alimenté**.
- **Alimentation Audio Dédiée** : L'audio requiert ~1,5 W (micros) + 5 à 10 W (DSP). Une ligne **5 V / 3 A dédiée et isolée galvaniquement** du circuit 48 V des moteurs est vitale pour éviter les *boucles de masse* (sifflements de ligne).
- **Câblage PDM (Si micros sur-mesure I2S/USB)** : Le signal d'horloge (1-3 MHz) est sensible aux interférences (EMI) des moteurs RobStride. Utilisez du câble blindé **LiYCY 4x0.14 mm²**. 
    - ⚠️ *Règle de blindage* : La tresse métallique ne doit être connectée à la masse (GND) **que d'un seul côté** (côté Hub/Carte) pour créer une cage de Faraday. Évitez les antennes parasites.

### 2.3 Intégration Casque & Routage Logiciel
- **Agencement & Isolation Vibratoire** : La matrice est logée en couronne au sommet du crâne. Le haut-parleur DSP est logé en bas (visière). Les bases micros doivent être montées sur des fixations imprimées en **TPU 95A-HF** (profil "spongieux" à 15% Gyroid) pour absorber les vibrations haute fréquence du robot.
- **Isolement Acoustique Séparé** : La chambre du haut (micros) et la chambre du bas (haut-parleur) doivent être impérativement rendues imperméables au son l'une de l'autre par une large cloison de **mousse haute densité**. Si les micros captent le haut-parleur par l'intérieur du plastique du casque, le robot "s'assourdira" en parlant.
- **Gestion du Vent** : Le ventilateur de la Jetson ne doit absolument pas recracher l'air vers les micros (le bruit de vent détruit l'algorithme de beamforming).
- **Routage Linux (PipeWire)** : Logiciel utilisé pour router la Matrice comme *Source* et le DSP comme *Sink*.
- **"Muzzle" ROS2** : Le système baisse algorithmiquement la sensibilité d'écoute à l'instant précis où les genoux RS-04 forcent (effort max), ignorant les pics sonores de la pignonnerie et préservant l'IA des erreurs.

## 3. Stratégie IMU (Fusion Multi-Capteurs)

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
