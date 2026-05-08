# SYNTHÈSE : Architecture Torse & Cou (D-Bot)

## 1. Actionneurs (RobStride)
Le torse et le cou utilisent des moteurs compacts pour la précision de la perception (Vision OAK-D).

| Articulation | Moteur | Couple (Pic) | Rôle |
| :--- | :--- | :---: | :--- |
| **Roll Tête** | **RobStride RS-05** | 5.5 N.m | Inclinaison latérale de la tête |
| **Tilt Tête** | **RobStride RS-05** | 5.5 N.m | Pitch (regarder en haut/bas) |
| **Yaw Tête** | **RobStride RS-05** | 5.5 N.m | Rotation gauche/droite |

## 2. Architecture Mécanique (Cou)
- **Solution Pivot** : Montage "Yoke Mount" (Chape en U).
- **Supports** : Utilisation de roulements externes **6804-2RS** (Ø20×Ø32×7mm).
- **Avantage** : Reprise de 100% des charges statiques (~2 kg de tête) par les roulements, protégeant l'intégrité des moteurs RS-05.

## 3. Structure Torse
- **Squelette** : Tubes 6060 + Nœuds d'aluminium **6061-T6** usinés sur CNC C500.
- **Design** : Architecture ouverte facilitant le refroidissement de l'électronique de contrôle (Jetson Orin Nano).
- **Masse totale robot** : **40.2 kg** (Scenario B "Option Hybride").

## 4. Intégration URDF
- **Nommage** : Harmonisé pour export Fusion 360 direct.
- **Câblage** : Passage interne prévu dans les chapes en U.

---
### 🔗 Études Complètes
- **[29 — Étude Montage Cou RS-05](../29_Etude_Montage_Cou_RS05.md)**
- **[29b — Étude Squelette Torse](../29_Etude_Squelette_Torse_Alu.md)**
- **[16 — Conclusions Architecture Finale](../16_Conclusions_Architecture_DBot.md)**

*Dernière mise à jour : Mars 2026*
