# SYNTHÈSE : Architecture Torse & Cou (D-Bot)

## 1. Actionneurs (RobStride)
Le torse et le cou utilisent des moteurs compacts pour la précision de la perception (Vision OAK-D).

| Articulation | Moteur | Couple (Pic) | Rôle |
| :--- | :--- | :---: | :--- |
| **Roll Tête** | **RobStride RS-05** | 5.5 N.m | Inclinaison latérale de la tête |
| **Tilt Tête** | **RobStride RS-05** | 5.5 N.m | Pitch (regarder en haut/bas) |
| **Yaw Tête** | **RobStride RS-05** | 5.5 N.m | Rotation gauche/droite |

## 2. Architecture Mécanique (Cou)
- **Solution Pivot** : Montage "Yoke Mount" (Chape en U) validé.
- **Supports** : Utilisation de roulements externes **6804-2RS** (Ø20×Ø32×7mm) pour décharger les rotors.
- **Avantage** : Reprise de 100% des charges statiques (~2 kg de tête) par les roulements, protégeant l'intégrité des moteurs RS-05.

## 3. Structure Torse
- **Squelette** : Plaques d'aluminium **6061-T6** découpées/usinées sur CNC C500.
- **Design** : Architecture ouverte facilitant le refroidissement de l'électronique de contrôle (Jetson Orin Nano).
- **Masse totale estimée** : ~39.4 kg (global robot).

## 4. Intégration URDF
- **Nommage** : Harmonisé pour export Fusion 360 direct (Chainage : Torso -> Head_Roll -> Head_Tilt -> Head_Yaw).
- **Câblage** : Passage interne prévu dans les chapes en U pour éviter l'usure par frottement.

---
*Dernière mise à jour : Mars 2026*
