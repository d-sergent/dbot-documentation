# 08 - Audio et Perception Sensorielle

## 1. Cerveau IA (Jetson Orin Nano Super)
Le cœur du traitement audio et cognitif du D-Bot est la **NVIDIA Jetson Orin Nano Super** (40 TOPS). Grâce à ses *Tensor Cores*, le robot fait tourner la suite logicielle **NVIDIA Riva** intégralement en local (sans serveur cloud, latence quasi nulle) :
- **ASR (Speech-to-Text)** : Compréhension de la parole.
- **NLP** : Analyse de l'intention humaine.
- **TTS (Text-to-Speech)** : Voix de synthèse naturelle.

> *Marge Processeur : La marche, la vision OAK-D et l'audio IA consomment environ 52% du processeur au maximum, laissant 48% de marge de sécurité.*

## 2. Architecture Audio Hybride (Double Système)
Le robot adopte une configuration "Luxe" séparant la localisation spatiale de la compréhension pure de la parole. L'architecture repose sur deux flux traités concurremment.

### 2.1 Rôles et Câblage
- **Matrice 8-micros PDM** (L'Ouïe Spatiale) : Son but unique est le **DoA (Direction of Arrival)** à 360°. Elle s'interface avec ROS2 pour ordonner au cou (Pan/Tilt) d'orienter la tête.
- **Système DSP type Jabra/Anker** (L'Écoute IA) : Son annulation d'écho matérielle (AEC) filtre le bruit de ses propres moteurs/haut-parleurs. Il capte les mots pour Riva.
- **Alimentation et Hub USB** : La Jetson n'ayant pas de prise son native, les deux systèmes se branchent sur un **Hub USB 3.0 Alimenté**. Prévoyez une ligne **5 V / 3 A dédiée et isolée galvaniquement** du circuit moteur (48V) pour éviter les sifflements de boucle de masse.

### 2.2 Configuration Microphones & Blindage (Audit EMI)
- **Placement stratégique** : 
    - 2x Oreilles
    - 1x Torse (Face)
    - 1x Nuque (Dos)
    - + 4x Additionnels en couronne sur la tête (pour le beamforming 3D).
- **Câblage PDM (Microphones)** : Le signal d'horloge (1-3 MHz) est très sensible aux interférences électromagnétiques (EMI) générées par les moteurs RobStride. **L'utilisation d'un câble blindé est impérative** entre chaque micro et la puce d'acquisition.
    - **Option 1 (Hack "Maker")** : Câble USB 2.0 sacrificiel (4 fils internes + tresse). *Note : le pin SEL Adafruit se câble via un pont local.*
    - **Option 2 (Standard)** : Câble de type "Microphone" ou **LiYCY 4x0.14 mm²** (Gotronic).
    - **Option 3 (Industriel)** : **SAB ou LappKabel LiYCY 4x0.14** (RS, Mouser). Résistant aux flexions répétées au cou.
    - ⚠️ **Règle d'or de blindage** : La tresse métallique ne doit être connectée à la masse (GND) **que d'un seul côté** (côté Hub/Acquisition). Laissez la tresse coupée "en l'air" côté microphone pour créer une cage de Faraday parfaite.

### 2.3 Intégration Mécanique & Acoustique
- **Filtrage Vibratoire** : Les bases des microphones doivent impérativement être montées sur des fixations imprimées en **Qidi TPU 95A-HF**. Pour amortir les vibrations haute fréquence des moteurs (cliquetis des pignons métalliques), imprimez le TPU avec un profil "spongieux" (Remplissage **10% à 15% Gyroid** et 1 seul mur externe).
- **Isolement Acoustique (HP vs Micros)** : La zone haute (micros en couronne) et la zone basse (haut-parleur DSP, derrière la visière) doivent être séparées physiquement. Utilisez un barrage de **mousse haute densité** pour bloquer la repisse sonore à l'intérieur de la coque du casque. Si le son interne du HP excite les micros, le robot s'assourdira en parlant.
- **Gestion du vent Jetson** : L'air de refroidissement de la Jetson ne doit absolument pas effleurer les micros (le vent détruit le beamforming).
- **Synchronisation TDOA** : La capture des 8 micros doit garantir une synchro à **192 kHz**, indispensable pour le calcul TDOA.
- **"Muzzle" ROS2** : Le nœud de contrôle audio (PipeWire) baisse algorithmiquement la sensibilité d'écoute à l'instant où les genoux RS-04 forcent à 100%, ignorant les bruits mécaniques pour l'IA.

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
