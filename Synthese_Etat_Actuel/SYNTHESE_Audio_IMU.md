# Synthèse : Audio & Perception (IMU) - État de l'Art

Ce document résume les décisions finales arrêtées pour l'architecture audio et sensorielle du D-Bot.

## 1. Traitement Audio (IA)
- **Cerveau** : NVIDIA Jetson Orin Nano Super (67 TOPS).
- **Suite Logicielle** : NVIDIA Riva (ASR/TTS/NLP) traitée intégralement en local.
- **Routage** : Intégration native dans ROS2 via PulseAudio.

## 2. Hardware Audio (Simplifié V1)
Le robot utilise une architecture centralisée USB :
- **Module Micros** : Seeed **ReSpeaker XVF-3800** (4 micros MEMS, 6 canaux (4 micros + 2 référence), DoA 360°, AEC matériel).
- **Haut-Parleur** : 5W / 8Ω (Connecteur JST sur ReSpeaker).
- **Interfaces** : USB vers Jetson (Audio), JST vers HP.

### Règles de Montage Critiques :
- **Évents** : 4 perçages de **Ø1.5 mm à Ø2 mm** dans la coque face aux micros.
- **Isolation** : Joint **TPU souple (0.5mm)** obligatoire entre le ReSpeaker et la coque.
- **Séparation** : Mousse acoustique haute densité entre les micros (haut du crâne) et le HP (zone buccale).

## 3. Stratégie IMU (Fusion)
Trois IMU spécialisées pour une stabilité optimale :
| Capteur | Position | Rôle | Fréquence |
| :--- | :--- | :--- | :---: |
| **Bosch BMI270** | Torse (CM) | **Équilibre Bipède** | 416 Hz |
| **BNO085** (OAK-D) | Tête | Stabilisation Regard / SLAM | 100 Hz |
| **LiDAR Unitree L2** | Torse | Odométrie LiDAR (LIO-SLAM) | 1000 Hz |

> [!IMPORTANT]
> L'équilibre est géré exclusivement par l'IMU du torse (BMI270 connectée à la Spresense) pour découpler les mouvements de la tête de la stabilisation du corps.

## 4. Liens et Archives
- **Analyse Audio** : [08_Architecture_Audio.md](../08_Architecture_Audio.md)
- **Analyse IMU** : [18_Strategie_IMU_Fusion.md](../18_Strategie_IMU_Fusion.md)
- **Historique des Choix** : [Archives/ETUDE_Audio_8Mic_PDM.md](../Archives/ETUDE_Audio_8Mic_PDM.md) (Ancienne architecture Luxe)
