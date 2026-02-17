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
> **La clé de notre solution** : séparer le LiDAR de son IMU défectueuse et le fusionner avec l'OAK-D Pro pour compenser la faible densité de points. C'est l'approche du G1 (MID-360 + RealSense), adaptée à notre budget.

```
                    ┌─────────────────┐
                    │   TÊTE D-BOT     │
                    │                  │
                    │  ┌────────────┐  │
                    │  │ Unitree L2 │  │  ← LiDAR 3D : 360°×96°, 64k pts/s
                    │  │ (sans IMU) │  │     Nuage de points SPARSE (loin)
                    │  └────────────┘  │
                    │                  │
                    │  ┌────────────┐  │
                    │  │ OAK-D Pro  │  │  ← Depth Camera : 80° cone, 640×480 pixels
                    │  │ (stéréo)   │  │     Nuage de points DENSE (près, 0-10m)
                    │  └────────────┘  │
                    └────────┬─────────┘
                             │ USB3 × 2
                    ┌────────▼─────────┐
                    │   Jetson Orin     │
                    │                  │
                    │  ┌────────────┐  │     ROS2 Topics :
                    │  │  RTAB-Map  │◀─┼──── /lidar/points  (L2, 64k pts/s)
                    │  │    ou      │◀─┼──── /oakd/depth     (dense, 80° FOV)
                    │  │ FAST-LIO   │◀─┼──── /imu/data       (BMI270, 400 Hz)
                    │  └────────────┘  │
                    └──────────────────┘
                             ▲
                    ┌────────┴─────────┐
                    │  Spresense       │
                    │  BMI270 Add-on   │  ← IMU 6 axes : 400 Hz, timing stable
                    │  (Always-On)     │     Publie sur /imu/data via USB-Serial
                    └──────────────────┘
```

### 5.2 Pourquoi Cette Fusion est Optimale

| Rôle | Capteur | Ce qu'il apporte |
| :--- | :--- | :--- |
| **Couverture globale** | L2 (360°×96°) | Nuage de points sparse sur tout l'environnement — cartographie, localisation |
| **Densité locale** | OAK-D Pro (~80° forward) | ~300k pixels de profondeur dans le cône avant — obstacles proches, objets fins, reconnaissance |
| **Odométrie inertielle** | BMI270 (400 Hz) | Compensation du mouvement bipédal, prédiction inter-scans, stabilité SLAM |

**Résultat** : la zone **devant le robot** (là où il marche) bénéficie de la **densité OAK-D Pro** (~300k pixels depth). Le **reste** (côtés, arrière, sol, plafond) est couvert par le L2 avec 64k pts/s — largement suffisant pour la cartographie et la localisation.

> [!TIP]
> **Compensation de densité** : L'OAK-D Pro produit ~**300 000 points de profondeur** par frame (640×480 depth map @ 30 FPS) dans son cône de 80°. Le L2 ne produit que 64 000 pts/s sur 360°×96°. En fusionnant les deux, la **densité effective dans la zone de marche** est **5× supérieure** au L2 seul — et même supérieure au Livox MID-360 dans cette zone !

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
            │      TÊTE D-BOT        │
            │                        │
            │   ┌──────────┐         │    ← L2 sur le sommet, monté
            │   │ L2 (top) │         │       sur 4 silent blocks Ø6mm
            │   └──────────┘         │       vis M3 + rondelles caoutchouc
            │         │              │
            │   ┌──────────┐         │    ← OAK-D Pro en façade,
            │   │ OAK-D Pro│ ←→ 🔵   │       centré, incliné 10° vers bas
            │   │ (front)  │         │       fixation M4 sur support alu
            │   └──────────┘         │
            └────────────────────────┘
```

**Câblage** :
- L2 → USB3 (câble fourni) → Jetson Orin USB-A #1
- OAK-D Pro → USB3 (câble DepthAI) → Jetson Orin USB-A #2
- BMI270 → Serial (via Spresense) → Jetson Orin USB-C (ou ROS2-micro-ROS)

> [!NOTE]
> Le L2 et l'OAK-D Pro se partagent la bande passante USB3. Chacun utilise ~400-500 Mb/s. Le Jetson Orin Nano dispose de suffisamment de ports USB3 pour les deux. Vérifier que le hub USB est bien USB 3.0+ si un hub est nécessaire.
