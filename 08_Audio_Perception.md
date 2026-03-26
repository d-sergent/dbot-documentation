# 08 - Audio et Perception Sensorielle

## 1. Cerveau IA (Jetson Orin Nano Super)
Le cœur du traitement audio et cognitif du D-Bot est la **NVIDIA Jetson Orin Nano Super** (67 TOPS). Grâce à ses *Tensor Cores*, le robot fait tourner la suite logicielle **NVIDIA Riva** intégralement en local (sans serveur cloud, latence quasi nulle) :
- **ASR (Speech-to-Text)** : Compréhension de la parole.
- **NLP** : Analyse de l'intention humaine.
- **TTS (Text-to-Speech)** : Voix de synthèse naturelle.

> *Marge Processeur : La marche, la vision OAK-D et l'audio IA consomment environ 52% du processeur au maximum, laissant 48% de marge de sécurité.*

## 2. Architecture Audio Simplifiée (ReSpeaker XVF-3800)

> [!NOTE]
> **Simplification V1 (Mars 2026)** : L'ancienne architecture "Luxe" (8 micros PDM + Spresense DSP + Jabra Speak 510) a été remplacée par un **module unique** ReSpeaker XVF-3800. Cette décision s'aligne sur les pratiques de l'industrie (Unitree G1 : 4 micros, Figure 02 : micros intégrés, 1X NEO : micros + LLM).

### 2.1 Module Unique : Seeed ReSpeaker XVF-3800

| Caractéristique | Détail |
| :--- | :--- |
| **Chip** | XMOS XVF-3800 |
| **Microphones** | 4× MEMS numériques (arrangement circulaire) |
| **DoA (Direction of Arrival)** | ✅ 360° (traitement on-chip) |
| **Beamforming** | ✅ (on-chip, focalisation sur la voix cible) |
| **AEC (Annulation d'Écho)** | ✅ Matériel (élimine la voix TTS du HP) |
| **Suppression de Bruit** | ✅ (on-chip, moteurs + environnement) |
| **Dé-réverbération** | ✅ (on-chip) |
| **VAD** | ✅ Détection d'activité vocale |
| **Haut-parleur intégré** | ❌ Non — Sortie JST amplifiée 5W |
| **Sortie audio** | Jack 3.5mm + **connecteur JST 5W** |
| **Interface** | **USB** (Plug-and-play Jetson, PulseAudio natif) |
| **Dimensions** | Ø70 mm (version ronde avec boîtier) |
| **Masse** | ~30 g |
| **Prix** | ~35 € |

**Achat (France)** :
- [Gotronic.fr](https://www.gotronic.fr) — Distributeur français, stock local
- [Seeed Studio](https://www.seeedstudio.com) — Direct fabricant, livraison internationale
- [AliExpress](https://www.aliexpress.com) — Alternative économique

### 2.2 Haut-Parleur Externe (TTS)

Le ReSpeaker ne possédant pas de HP intégré, un **mini haut-parleur 5W / 8Ω** est connecté via le port JST de la carte.

| Composant | Spécification | Prix |
| :--- | :--- | :---: |
| HP 5W 8Ω (40mm) | Connecteur JST, ~20 g | ~5 € |

### 2.3 Placement dans le Robot

```
                    ┌─────────────────────────┐
                    │       CRÂNE (top)        │
                    │                          │
                    │   ┌──────────────────┐   │
                    │   │  ReSpeaker Ø70mm │   │ ← 4 micros DoA 360°
                    │   │  (USB → Jetson)  │   │
                    │   └──────────────────┘   │
                    │                          │
                    │ ~~~~~~~~ MOUSSE ~~~~~~~~ │ ← Isolation acoustique
                    │                          │
                    │   ┌──────────────────┐   │
                    │   │  HP 5W (JST)     │   │ ← Zone buccale (grille)
                    │   └──────────────────┘   │
                    │                          │
                    │       OAK-D Pro (FF)     │ ← Vision (front)
                    └──────────┬───────────────┘
                               │ Cou (USB dans tube)
                             TORSE
```

- **ReSpeaker** : Sommet du crâne (intérieur de la coque). Les 4 micros circulaires captent le son à 360° sans obstruction.
- **HP 5W** : Zone buccale (derrière la grille faciale). Séparé physiquement des micros par une **mousse haute densité** pour éviter la repisse sonore.

#### 2.3.1 Détails d'Intégration Acoustique (Crucial)

Pour que les microphones fonctionnent à travers la coque en PETG-CF, vous devez respecter ces deux règles :

1.  **Évents Acoustiques (Mic Ports)** : La coque du robot **ne doit pas être pleine** devant les micros. Vous devez percer (ou prévoir à la conception 3D) **4 petits trous de Ø1.5 mm à Ø2 mm**, alignés précisément avec les 4 microphones MEMS de la carte ReSpeaker. Sans ces trous, le son sera étouffé et la localisation (DoA) sera impossible.
2.  **Joint TPU (Gasket)** : Il est impératif d'interposer un joint fin (0.5 mm à 1.0 mm) imprimé en **TPU souple** entre la face supérieure du ReSpeaker et la paroi interne du crâne.
    - **Rôle 1** : Étanchéité acoustique. Empêche le son interne du robot (ventilation Jetson, sifflement des moteurs) de "remonter" vers les micros par l'intérieur du crâne.
    - **Rôle 2** : Isolation vibratoire. Empêche les vibrations mécaniques du châssis d'exciter directement les membranes des micros.
    - **Conception** : Le joint doit comporter 4 perçages alignés avec les évents de la coque et les micros.

> [!TIP]
> **Protection Poussière** : Vous pouvez coller une fine membrane de **tulle acoustique** ou un morceau de collant en nylon entre le joint TPU et la coque pour empêcher la poussière d'entrer dans les micros sans bloquer le son.

- **Câblage** : Un seul câble USB descend dans le cou vers le Hub USB Jetson. Le HP est relié au ReSpeaker par un fil JST de ~15 cm.

### 2.4 Intégration Logicielle

- **Routage Audio (PulseAudio)** : JetPack 6 (L4T) reconnaît nativement le ReSpeaker comme source USB. PulseAudio le configure automatiquement en *Source* ASR et *Sink* TTS (via la sortie HP).
- **DoA via ROS2** : Le ReSpeaker publie les données DoA sur **`/audio/doa`** (via un nœud ROS2 léger, basé sur le package `respeaker_ros2`). Le cou Pan/Tilt s'oriente automatiquement vers la source sonore.
- **"Muzzle" ROS2** : Le nœud de contrôle audio baisse algorithmiquement la sensibilité d'écoute lorsque les moteurs forcent, ignorant les bruits mécaniques.

### 2.5 Schéma de Routage Audio

```
                          ┌──────────────────┐
                          │  ReSpeaker USB   │
                          │  (XMOS XVF-3800) │
                          │                  │
[4 Micros MEMS] ─────────┤  DoA 360°        ├──── USB ──→ Jetson (PulseAudio)
                          │  Beamforming     │              │
                          │  AEC + NS        │              ├─→ Riva ASR → ROS2 /audio/command
                          │                  │              ├─→ DoA → ROS2 /audio/doa → Cou Pan/Tilt
                          │  Sortie JST 5W ──┼──→ HP 5W    ├─← Riva TTS (Voix)
                          └──────────────────┘
```

### 2.6 Comparatif Ancien vs Nouveau Système

| Critère | Ancien (8-mic + Jabra) | **Nouveau (ReSpeaker)** |
| :--- | :---: | :---: |
| **Coût** | ~180 € | **~40 €** |
| **Masse** | ~250 g | **~50 g** (ReSpeaker + HP) |
| **Câblage** | 10+ fils blindés | **1 câble USB + 1 JST** |
| **EMI à gérer** | Critique (8 lignes PDM) | **Aucun** (traitement on-chip) |
| **DoA 360°** | ✅ | ✅ |
| **AEC** | ✅ (Jabra) | ✅ (on-chip) |
| **Complexité montage** | Très élevée | **Très faible** |

> [!IMPORTANT]
> **Impact sur la Spresense** : La Spresense **ne gère plus l'audio**. Ses rôles restants sont : Watchdog (heartbeat Jetson), Power Management (surveillance batterie 12S, MOSFET 48V), IMU BMI270 (équilibre bipède 416 Hz), lecture des FSR plantaires (ADC), et thermistances moteurs. Les deux cartes (Main Board + Extension Board) restent nécessaires pour ces fonctions critiques. Voir [Guide Watchdog](./11_Guide_SensiEDGE_Watchdog.md).

## 3. Stratégie IMU (Fusion Multi-Capteurs)

Le D-Bot exploite **3 IMUs** positionnées stratégiquement, chacune avec un rôle clairement défini :

### Matrice des Rôles IMU

| IMU | Capteur | Position | Fréquence | Rôle Principal | Rôle Secondaire |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **IMU Torse** | **BMI270** (Add-on Spresense) | Torse (centre de masse) | **416 Hz** | 🔴 **Équilibre bipède** | Détection de chute (Watchdog) |
| **IMU Tête** | BNO085/BMI270 (OAK-D Pro) | Front (tête) | 100 Hz | **Stabilisation regard** | V-SLAM visuel |
| **IMU LiDAR** | IMU intégrée (Unitree L2) | Haut du torse | **1000 Hz** | **Odométrie LiDAR** (LIO-SLAM) | Fusion avec V-SLAM | ⚠️ **V2** |

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
