# 19. Perception Spatiale & LiDAR — Analyse Complète

> **Objectif** : Doter le D-Bot d'une perception 3D fiable pour la navigation autonome (SLAM), l'évitement d'obstacles et la cartographie en temps réel.

---

## 1. Besoin Fonctionnel

Le D-Bot a besoin de percevoir son environnement en 3D pour :
- **Localisation** : savoir où il est dans l'espace (SLAM).
- **Navigation** : planifier un chemin et éviter les obstacles.
- **Cartographie** : construire une carte de l'environnement.
- **Sécurité** : détecter les escaliers, les trous, les marches, les objets en hauteur.

Pour un **bipède de 1.35 m marchant à 2-3 km/h en intérieur**, les contraintes sont :
- FOV vertical large (voir le sol ET les obstacles en hauteur).
- Portée ≥ 10 m (pièces, couloirs).
- Robustesse aux vibrations de la marche.
- Poids minimal (monté sur la tête = impact sur l'inertie cervicale).

---

## 2. Retour d'Expérience — Unitree L2

### 2.1 Points Forts

| Avantage | Détail |
| :--- | :--- |
| **FOV** | 360° × 96° — le FOV vertical le plus large de sa catégorie |
| **Zone aveugle** | 0.05 m seulement (excellent pour le near-field) |
| **Poids** | 230 g (très compact : 75×75×65 mm) |
| **Prix** | ~$419 — le 3D LiDAR le moins cher du marché |
| **Anti-éblouissement** | Fonctionne en extérieur (100 klux) |
| **ROS** | Support ROS1/ROS2 natif, SLAM open-source (Point-LIO) |
| **Précision** | ≤ 2 cm à 10 m |

### 2.2 Problèmes Identifiés (Retours Communauté)

> [!CAUTION]
> L'IMU intégrée du L2 est **défectueuse** — c'est un problème confirmé par de multiples utilisateurs et **non corrigé** par Unitree.

| Problème | Gravité | Détail |
| :--- | :---: | :--- |
| **IMU timing aléatoire** | 🔴 Critique | Intervalles de données aléatoires (2 µs – 100 ms au lieu de 500 Hz fixe). "Widespread issue" non corrigé. |
| **Drift SLAM** | 🔴 Critique | L'IMU incorrecte provoque une dérive sévère avec Point-LIO sur ROS2. |
| **Bruit nuage de points** | 🟠 Modéré | Données bruitées sur plateformes mobiles à cause du miroir rotatif. |
| **Vibrations** | 🟠 Modéré | Le L1 (prédécesseur) était "très sensible aux vibrations". Le L2 réduit le problème sans l'éliminer. |
| **Fréquence de scan** | 🟡 Mineur | 5.55 Hz — insuffisant pour FAST-LIVO2, suffisant pour marche lente. |

> [!NOTE]
> Le L1 (prédécesseur) n'a PAS ces problèmes d'IMU. C'est un **défaut spécifique au L2**, probablement lié à un changement de firmware.

---

## 3. Benchmark Industrie — Comment les Concurrents Perçoivent l'Espace

| Robot | Stratégie | LiDAR | Caméras | IMU | SLAM |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Unitree G1** | LiDAR + depth cam | **Livox MID-360** | Intel RealSense D435i | Intégrée LiDAR + dédiée | LiDAR-SLAM (FAST-LIO) |
| **Tesla Optimus** | **Vision pure** (pas de LiDAR) | ❌ | Caméras RGB multiples | IMU torse + capteurs couple | Vision end-to-end NN |
| **Figure 02** | **Vision pure** (6 caméras) | ❌ | 6× RGB + VLM embarqué | IMU torse | Vision Language Model |
| **Agility Digit** | LiDAR + caméras | Propriétaire | Multiples | Propriétaire | Fusion capteurs |
| **Fourier GR-2** | Intel RealSense | ❌ | RealSense D455 + RGB | IMU torse | Visual-Inertial |

**Tendance industrie** : Les robots haut de gamme (Optimus, Figure 02) abandonnent le LiDAR au profit de la vision pure grâce aux progrès de l'IA. Les robots milieu de gamme (G1) combinent LiDAR + depth camera. **Unitree n'utilise PAS le L2 sur son propre G1** — signal fort.

---

## 4. Alternatives Évaluées

### 4.1 LiDARs 3D

| LiDAR 3D | Prix | Points/s | FOV (H×V) | IMU | Poids | IP | Note |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Unitree L2** | **~$419** | 64k eff. | 360°×96° | ❌ Défectueuse | **230g** | IP52 | FOV vertical imbattable |
| **Livox MID-360** | ~$600-900 | 200k | 360°×59° | ✅ | 265g | IP67 | Choix du G1, solid-state |
| Hesai QT64 | ~$800+ | ~300k | 360°×104° | ❌ | 400g | IP67 | Excellent FOV, cher |
| Ouster OSDome | ~$1500+ | 5.2M | 360°×180° | ❌ | 470g | IP68 | Trop cher |

### 4.2 LiDARs 2D (paire avant + arrière)

| LiDAR 2D | Prix unité | Portée | Points/s | Poids |
| :--- | :---: | :---: | :---: | :---: |
| LD-19 | ~$50 | 12m | 4.5k | 100g |
| RPLidar A1 | ~$100 | 12m | 8k | 170g |
| RPLidar A2 | ~$285 | 12m | 16k | 190g |
| YDLIDAR X4 Pro | ~$80 | 10m | 5k | 115g |

> [!WARNING]
> **2D LiDAR ❌ inadapté pour un bipède** : un LiDAR 2D scanne un seul plan horizontal. Sur un bipède qui oscille en pitch/roll à chaque pas, le plan de scan bouge en permanence. Zéro information verticale = escaliers, seuils de porte et objets en hauteur invisibles.

### 4.3 Vision Pure (Multi-Caméras)

| Config | Caméras | FOV combiné | GPU Jetson Orin | Faisabilité |
| :--- | :---: | :---: | :---: | :---: |
| OAK-D Pro seul | 1 stéréo | ~80° depth | ~15% GPU | ✅ Trivial |
| OAK-D Pro + 1 cam arrière | 2 unités | ~160° | ~30% GPU | ✅ Réaliste |
| OAK-D Pro + 2 cam latérales | 3 unités | ~240° | ~50% GPU | ⚠️ Lourd |
| 4-6 caméras (style Figure 02) | 4-6 | 360° | >70% GPU | ❌ Hors budget GPU |

La vision pure est insuffisante à notre niveau : pas assez de puissance IA pour du visual SLAM end-to-end, sensible aux conditions de lumière et aux surfaces sans texture.

---

## 5. Solution Retenue — Triple Fusion L2 + OAK-D Pro + BMI270

### 5.1 Principe

> [!IMPORTANT]
> **La clé de notre solution** : séparer le LiDAR de son IMU défectueuse, le monter sur le **torse** (position stable pour le SLAM), et fusionner avec l'OAK-D Pro sur la **tête** (orientable pour la perception locale). C'est l'approche du G1 (MID-360 sur torse + RealSense en tête), adaptée à notre budget.

```
                    ┌─────────────────┐
                    │   TÊTE D-BOT     │    ← 2 DOF (2× RS-05 : Pitch + Yaw)
                    │   (orientable)   │       Gaze Control actif (VOR)
                    │  ┌────────────┐  │
                    │  │ OAK-D Pro  │  │  ← Depth Camera : 80° cone, 640×480 pixels
                    │  │ (stéréo)   │  │     Nuage de points DENSE (près, 0-10m)
                    │  └────────────┘  │     Orientation active → regarde où il faut
                    └────────┬─────────┘
                             │ Cou (2× RS-05)
                    ┌────────┴─────────┐
                    │   TORSE (haut)    │
                    │                  │
                    │  ┌────────────┐  │
                    │  │ Unitree L2 │  │  ← LiDAR 3D : 360°×96°, 64k pts/s
                    │  │ (sans IMU) │  │     Position FIXE sur torse = TF statique
                    │  │ [silent bl]│  │     Mouvement prévisible (locomotion)
                    │  └────────────┘  │
                    │                  │
                    │  ┌────────────┐  │
                    │  │ Spresense  │  │  ← IMU BMI270 : 400 Hz, timing stable
                    │  │ BMI270     │  │     Co-localisé avec le L2 sur le torse
                    │  └────────────┘  │     Publie sur /imu/data
                    └────────┬─────────┘
                             │ USB3 × 2 + Serial
                    ┌────────▼─────────┐
                    │   Jetson Orin     │
                    │                  │
                    │  ┌────────────┐  │     ROS2 Topics :
                    │  │  RTAB-Map  │◀─┼──── /lidar/points  (L2, 64k pts/s)
                    │  │    ou      │◀─┼──── /oakd/depth     (dense, 80° FOV)
                    │  │ FAST-LIO   │◀─┼──── /imu/data       (BMI270, 400 Hz)
                    │  └────────────┘  │
                    └──────────────────┘
```

### 5.2 Pourquoi Cette Architecture (L2 Torse / OAK-D Tête)

> [!NOTE]
> **Choix de placement du L2 sur le torse** : Le positionnement du L2 a fait l'objet d'une analyse approfondie. Le **torse** a été retenu plutôt que la tête pour 5 raisons :

| Critère | L2 sur la **tête** (rejeté) | L2 sur le **torse** (retenu) |
| :--- | :---: | :---: |
| **SLAM stabilité** | ⚠️ Mouvements tête imprévisibles → distorsion intra-scan | ✅ Mouvement locomotion prévisible |
| **TF ROS2** | Dynamique (lidar→head→neck→torso) | ✅ **Statique** (lidar→torso = constante) |
| **FOV L2 suffisant sans bouger ?** | Le L2 couvre déjà 96° vertical | ✅ **96° = sol au plafond sans incliner** |
| **Inertie cervicale** | 330g (L2+OAK-D) sur la tête | ✅ **~91g** (OAK-D seul) |
| **OAK-D libre de pointer ?** | ❌ Mouvements tête perturbent le L2 | ✅ **Tête 100% dédiée à l'OAK-D** |
| **Benchmark G1** | — | ✅ Le G1 fait exactement cela |

**Séparation des rôles** :

| Rôle | Capteur | Position | Ce qu'il apporte |
| :--- | :--- | :---: | :--- |
| **SLAM global (360°)** | L2 (360°×96°) | **Torse** (fixe) | Cartographie, localisation — mouvement stable et prévisible |
| **Perception locale (orientable)** | OAK-D Pro (~80°) | **Tête** (2 DOF) | Obstacles proches, reconnaissance, densité adaptative |
| **Odométrie inertielle** | BMI270 (400 Hz) | **Torse** (co-localisé L2) | Compensation locomotion, stabilité SLAM |

**Résultat** : la zone **devant le robot** (là où il marche) bénéficie de la **densité OAK-D Pro** (~300k pixels depth), orientable par le cou. Le **reste** (côtés, arrière, sol, plafond) est couvert par le L2 avec 64k pts/s en position stable — optimal pour le SLAM.

> [!TIP]
> **Compensation de densité** : L'OAK-D Pro produit ~**300 000 points de profondeur** par frame (640×480 depth map @ 30 FPS) dans son cône de 80°. Le L2 ne produit que 64 000 pts/s sur 360°×96°. En fusionnant les deux, la **densité effective dans la zone de marche** est **5× supérieure** au L2 seul — et même supérieure au Livox MID-360 dans cette zone !
>
> De plus, l'OAK-D étant sur la tête orientable, le robot peut **diriger le cône dense là où c'est nécessaire** : vers le sol en course, vers un objet d'intérêt à l'arrêt, vers une porte à franchir.

### 5.3 Comparaison Densité Effective (Zone Avant 80°)

| Source | Points dans le cône avant 80° | Fréquence |
| :--- | :---: | :---: |
| L2 seul | ~14k pts/s (80°/360° × 64k) | 5.55 Hz |
| OAK-D Pro depth | ~300k pts/frame | 30 Hz |
| **L2 + OAK-D Pro fusionnés** | **~314k pts/frame** | **30 Hz** |
| Livox MID-360 (80°/360°) | ~44k pts/s | 10 Hz |

→ Notre solution budget bat le MID-360 en densité locale !

### 5.4 Intégration Logicielle (ROS2)

**Algorithme SLAM recommandé** : **RTAB-Map** (ROS2)

RTAB-Map accepte nativement :
- Un nuage de points 3D (topic `/lidar/cloud`) → L2
- Une paire stéréo / depth map (topic `/oakd/depth`, `/oakd/rgb`) → OAK-D Pro
- Un flux IMU (topic `/imu/data`) → BMI270

```yaml
# Exemple de launch RTAB-Map avec fusion L2 + OAK-D Pro + IMU
rtabmap_ros:
  parameters:
    subscribe_depth: true        # OAK-D Pro depth
    subscribe_scan_cloud: true   # L2 point cloud
    wait_imu_to_init: true       # BMI270

  remappings:
    rgb/image: /oakd/rgb/image_raw
    rgb/camera_info: /oakd/rgb/camera_info
    depth/image: /oakd/stereo/depth
    scan_cloud: /lidar/cloud
    imu: /imu/data
```

### 5.5 Mitigation des Faiblesses du L2

| Problème | Solution | Coût |
| :--- | :--- | :---: |
| **IMU défectueuse** | Ignorer l'IMU L2, utiliser BMI270 Spresense (400 Hz, timing stable) | $0 (déjà prévu) |
| **Bruit nuage de points** | Filtre **Statistical Outlier Removal** (SOR) dans le pipeline PCL ROS2 | $0 (logiciel) |
| **Vibrations miroir rotatif** | Montage sur **silent blocks caoutchouc** (amortissement 50-70 Hz) | ~$5 |
| **Faible densité (64k pts/s)** | **Fusion avec depth map OAK-D Pro** (+300k pts/frame dans le cône avant) | $0 (déjà prévu) |
| **Fréquence scan 5.55 Hz** | Suffisant à 2-3 km/h. L'OAK-D Pro couvre à 30 Hz pour les obstacles proches | — |

---

## 6. Matrice Décisionnelle Finale

| # | Solution | Coût supp. | SLAM | FOV vertical | Densité zone avant | Vibrations | Verdict |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **🏆 A** | **L2 + OAK-D Pro + BMI270** | **$419** | ✅✅ | **96°** ⚡ | **314k pts** ⚡ | ⚠️ (amortisseur) | **Retenu — Meilleur rapport perf/prix** |
| B | MID-360 + OAK-D Pro | $700-900 | ✅✅ | 59° ⚠️ | ~344k pts | ✅ (solid-state) | Bon mais FOV vertical insuffisant |
| C | OAK-D Pro seul | $0 | ⚠️ | 80° cone | 300k pts | ✅ | Insuffisant (pas de 360°) |
| D | 2× LiDAR 2D + OAK-D Pro | $100-200 | ❌ | Plan unique | 300k pts + 2D | ⚠️ | ❌ Inadapté bipède |
| E | Vision pure multi-cam | $50-200 | ⚠️ | Variable | Élevée | ✅ | ❌ Hors capacité IA |

---

## 7. Évolutions Possibles

| Phase | Évolution | Raison |
| :--- | :--- | :--- |
| **Phase 4 V1** | L2 + OAK-D Pro + BMI270 (config retenue) | Couverture 360° + densité avant + IMU fiable |
| **Phase 4 V2** | + 1 caméra USB arrière (~$50) | Couverture depth 360° (avant + arrière) |
| **Phase 5+** | Réévaluer Livox MID-360 v2 ou équivalent solid-state | Si le bruit L2 est problématique en pratique |
| **2027+** | Puce IA embarquée + visual SLAM end-to-end | Quand les frameworks vision seront matures pour bipèdes |

---

## 8. Montage Physique

```
            ┌────────────────────────┐
            │      TÊTE D-BOT        │    ← Orientable (2× RS-05)
            │                        │       Légère : OAK-D seul (~91g)
            │   ┌──────────┐         │
            │   │ OAK-D Pro│ ←→ 🔵   │    ← En façade, centré
            │   │ (front)  │         │       Fixation M4 sur support alu
            │   └──────────┘         │
            └────────┬───────────────┘
                     │ Cou (2× RS-05)
            ┌────────┴───────────────┐
            │    TORSE HAUT          │    ← Position fixe, stable
            │                        │
            │   ┌──────────┐         │    ← L2 monté devant le cou,
            │   │ L2 (fix) │         │       sur 4 silent blocks Ø6mm
            │   └──────────┘         │       vis M3 + rondelles caoutchouc
            │                        │       TF statique lidar→torso
            │   ┌──────────┐         │
            │   │Spresense │         │    ← BMI270 co-localisé avec L2
            │   │ BMI270   │         │       Même repère = meilleure fusion
            │   └──────────┘         │
            └────────────────────────┘
```

**Avantage clé du montage** : Le L2 et le BMI270 sont **co-localisés sur le torse** → leur repère est quasi-identique, ce qui simplifie la fusion IMU+LiDAR dans l'algorithme SLAM (pas de bras de levier entre les deux capteurs).

**Câblage** :
- L2 → USB3 (câble fourni, passé dans le cou) → Jetson Orin USB-A #1
- OAK-D Pro → USB3 (câble DepthAI, flexible dans le cou) → Jetson Orin USB-A #2
- BMI270 → Serial (via Spresense) → Jetson Orin USB-C (ou micro-ROS)

> [!NOTE]
> Les câbles USB de l'OAK-D Pro passent par le cou articulé. Prévoir un **câble USB3 spiralé ou extra-souple** (type câble robot industriel) pour supporter les rotations du cou sans fatigue mécanique. Longueur recommandée : 30-40 cm avec mou.

---

## 9. Stabilisation Active du Regard (Gaze Control)

### 9.1 Le Problème en Marche Rapide / Course

À mesure que la vitesse augmente, le **torse oscille** en pitch (±5-15°) et roll (±3-8°) à chaque foulée. Ces oscillations :
- **Flouttent l'image** de l'OAK-D Pro (motion blur → depth map dégradée).
- **Déplacent le cône OAK-D** verticalement → le robot "perd de vue" le sol ou la direction.
- **Secouent le L2** (sur le torse) → bruit modéré, mais mouvement prévisible (compensable par IMU).

### 9.2 La Solution : le Réflexe Vestibulo-Oculaire (VOR) du D-Bot

> [!IMPORTANT]
> **La tête du D-Bot dispose de 2 DOF** (2× RS-05 : Pitch + Yaw) qui permettent une **stabilisation active du regard de l'OAK-D Pro**, exactement comme le réflexe vestibulo-oculaire humain compense les mouvements de la tête pendant la marche. Le L2, fixé sur le torse, n'a **pas besoin** de VOR — ses oscillations sont prévisibles et compensées par le BMI270 co-localisé.

**Principe** : Le BMI270 (IMU torse) mesure les oscillations du corps en temps réel. Le contrôleur de la tête applique une **compensation inverse** sur les moteurs du cou pour maintenir l'OAK-D Pro orienté de manière stable, indépendamment des mouvements du torse.

```
            Oscillation du torse (marche/course)
                    ┌──────────────┐
                    │   TORSE      │    ← Pitch ±10°, Roll ±5°
                    │ ┌──────┐     │
                    │ │  L2  │ fixe│    ← L2 subit les oscillations torse
                    │ └──────┘     │       MAIS mouvement prévisible
                    │ ┌──────┐     │       → compensé par BMI270 dans SLAM
                    │ │BMI270│     │
                    │ └──────┘     │
                    └────┬─────────┘
                         │ Cou 2× RS-05
           ╔═════════════╧══════════════╗
           ║   COMPENSATION INVERSE     ║
           ║                            ║
           ║  θ_tête = -θ_torse × k     ║    ← k ∈ [0.8, 1.0] (gain VOR)
           ║  + bias selon vitesse       ║       Uniquement pour l'OAK-D
           ║                            ║
           ╚═════════════╤══════════════╝
                    ┌────┴─────┐
                    │   TÊTE   │    ← Stable dans le repère monde
                    │ OAK-D Pro│       Image nette, depth map précise
                    └──────────┘
```

> [!TIP]
> **Avantage clé de l'architecture L2-torse / OAK-D-tête** : Le VOR ne doit stabiliser que **~91g** (OAK-D Pro seul) au lieu de 330g (L2+OAK-D). Les RS-05 ont une marge de vitesse immense et l'inertie cervicale réduite améliore toute la dynamique de marche.

### 9.3 Modes de Regard par Phase de Locomotion

| Phase | Vitesse | Pitch tête (OAK-D) | Yaw tête | OAK-D cible | L2 (torse, fixe) |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Debout / Station** | 0 km/h | Libre (exploration) | Libre | Scène en face / objet d'intérêt | SLAM 360° continu |
| **Marche lente** | 1-2 km/h | VOR actif (-pitch torse) | Direction marche | Sol 1-5m devant | SLAM optimal |
| **Marche rapide** | 3-4 km/h | VOR actif + bias -15° | Direction marche | **Sol + obstacles proches** | SLAM bon (filtré SOR) |
| **Course** | 5-8 km/h | VOR actif + bias -20° | Direction course | **Sol immédiat 0-3m** | SLAM dégradé mais compensé BMI270 |

**En mode course**, la tête s'incline davantage vers le bas (bias -15° à -20°) pour **maximiser la couverture du sol** de l'OAK-D à proximité immédiate. C'est critique : à 6 km/h (1.67 m/s), le robot parcourt ~1.7 m entre chaque scan L2 (5.55 Hz). L'OAK-D Pro à 30 FPS comble ce gap en scannant le sol toutes les 33 ms = ~5.5 cm d'avancée.

> [!NOTE]
> **Indépendance tête/torse** : En mode exploration (debout, station), la tête peut librement regarder autour sans perturber le SLAM LiDAR. C'est **impossible** avec le L2 sur la tête — chaque mouvement de curiosité aurait perturbé le scan.

### 9.4 Implémentation ROS2 (Gaze Stabilization Node)

```python
#!/usr/bin/env python3
"""
D-Bot Gaze Stabilization — Vestibulo-Ocular Reflex (VOR)
Compense les oscillations du torse en temps réel via les 2 DOF tête.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import Float32

class GazeStabilizer(Node):
    def __init__(self):
        super().__init__('gaze_stabilizer')
        
        # IMU torse (BMI270 via Spresense)
        self.sub_imu = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)
        
        # Commandes moteurs tête
        self.pub_pitch = self.create_publisher(Float32, '/head/pitch_cmd', 10)
        self.pub_yaw = self.create_publisher(Float32, '/head/yaw_cmd', 10)
        
        # Paramètres VOR
        self.vor_gain_pitch = 0.9   # Compensation à 90%
        self.vor_gain_yaw = 0.85
        self.speed_mode = 'walk'    # walk, fast_walk, run
        
        # Bias selon vitesse (inclinaison sol)
        self.pitch_bias = {
            'stand': 0.0,       # Exploration libre
            'walk': -5.0,       # Léger regard vers le sol
            'fast_walk': -15.0, # Sol + obstacles proches
            'run': -20.0,       # Sol immédiat prioritaire
        }
    
    def imu_callback(self, msg):
        # Extraire pitch et yaw du torse
        torso_pitch = self._quat_to_pitch(msg.orientation)
        torso_yaw_rate = msg.angular_velocity.z
        
        # Compensation inverse (VOR)
        head_pitch = -torso_pitch * self.vor_gain_pitch
        head_pitch += self.pitch_bias.get(self.speed_mode, 0.0)
        
        head_yaw_correction = -torso_yaw_rate * self.vor_gain_yaw * 0.01
        
        # Publier commandes
        self.pub_pitch.publish(Float32(data=head_pitch))
        self.pub_yaw.publish(Float32(data=head_yaw_correction))
```

---

## 10. Analyse par Régime de Vitesse

### 10.1 La Triple Fusion est-elle Suffisante en Course ?

| Critère | Marche (2 km/h) | Marche rapide (4 km/h) | Course (7 km/h) |
| :--- | :---: | :---: | :---: |
| **Distance entre scans L2** | ~10 cm | ~20 cm | ~35 cm |
| **OAK-D entre frames** | ~1.8 cm | ~3.7 cm | ~6.5 cm |
| **Vibrations torse (= L2)** | Faibles (±3°) | Modérées (±8°) | Fortes (±15°) |
| **L2 SLAM (torse fixe)** | ✅ Excellent | ✅ Bon (BMI270 compense) | ⚠️ Dégradé mais compensé BMI270 |
| **VOR OAK-D (tête)** | ✅ RS-05 : ~21 rad/s max | ✅ Marge confortable | ✅ 15°×5Hz = 75°/s << 21 rad/s |
| **OAK-D motion blur** | ❌ Négligeable | 🟡 Gérable (VOR) | 🟠 Résiduel malgré VOR |
| **Masse VOR (tête seule)** | ✅ 100g OAK-D seul | ✅ Réactif | ✅ Inertie faible |
| **Obstacles proches (OAK-D)** | ✅ Dense, orientable | ✅ Dense, VOR + bias sol | ✅ Dense, VOR + bias -20° |
| **Verdict** | ✅✅ Optimal | ✅ Suffisant | ⚠️ Viable avec VOR |

### 10.2 Pourquoi la Course Reste Viable

1. **VOR léger** : Le RS-05 ne stabilise que **~91g** (OAK-D seul, pas L2+OAK-D). L'oscillation torse en course (~15° × 3 Hz = ~45°/s) représente seulement **~4% de la capacité** du RS-05 (~21 rad/s). Marge immense.

2. **L2 stable sur torse** : Même en course, les oscillations du torse sont **prévisibles** (locomotion régulière). Le BMI270 co-localisé compense la distorsion dans l'algorithme SLAM (motion undistortion). C'est bien mieux que si le L2 subissait les mouvements aléatoires de la tête.

3. **OAK-D Pro à 30 FPS** : Même en course (1.9 m/s), l'OAK-D scanne tous les **6.5 cm** d'avancement — bien assez pour détecter les obstacles au sol. Le VOR stabilise l'image pour éviter le motion blur.

4. **Redondance SLAM** : En course, si le SLAM LiDAR dérive, le **SLAM visuel OAK-D** prend le relais comme source d'odométrie principale. Le L2 contribue toujours à la localisation globale même avec un nuage filtré.

5. **Stratégie de repli** : Si la course dégrade trop le SLAM, le robot peut automatiquement **ralentir à la marche rapide** pendant les phases de cartographie critique (virage, changement de pièce).

### 10.3 Facteur Limitant Réel

Le facteur limitant de la perception en course n'est **PAS le capteur** mais la **puissance de calcul** :
- RTAB-Map avec fusion L2 + OAK-D + IMU à pleine vitesse → **~40-60% GPU** Jetson Orin
- En course, les algorithmes de **planification de trajectoire** et de **contrôle de balance** consomment aussi du GPU
- Budget GPU total disponible : ~20-30% GPU pour le planning/contrôle

→ C'est largement gérable sur un Jetson Orin (NVDLA + GPU 1024-core).

> [!TIP]
> **Optimisation course** : En mode course, réduire la résolution OAK-D de 640×480 à 320×240 (75k pts/frame au lieu de 300k) pour libérer du GPU au contrôle de balance. La couverture reste suffisante pour la détection d'obstacles proches.
