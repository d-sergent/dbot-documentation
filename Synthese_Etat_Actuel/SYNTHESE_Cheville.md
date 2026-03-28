# SYNTHÈSE : Architecture Cheville (D-Bot)

## 1. Actionneurs & Différentiel (RobStride)
La cheville abandonne le montage direct pour une architecture différentielle déportée, libérant le bas du tibia de toute masse morte.

| Composant | Modèle | Couple Combiné (Pic) |
| :--- | :--- | :---: |
| **Moteurs (2x)** | **RobStride RS-03** | **120 N.m** (Pitch & Roll) |

## 2. Transmission (Cardan & Bielles)
- **Cœur Mécanique** : **Joint de Cardan DIN 808** de haute résistance (permet 2 DOF : Pitch & Roll).
- **Liaison** : Deux bielles parallèles reliant les moteurs (placés en haut du tibia) au plateau du pied.
- **Différentiel** : 
    - Mouvements identiques des moteurs = **Pitch** (flexion/extension).
    - Mouvements opposés des moteurs = **Roll** (inversion/éversion).

## 3. Conception Mécanique
- **Masse distale** : Gain de **-310g** en bas de jambe par rapport au K-Bot.
- **Composants** : Cardan acier, bielles alu CNC, rotules GE12UK.
- **Structure** : Montage par bagues d'arrêt et axes 12.9 pour encaisser les 120 N.m.

## 4. Performances & Limites
- **Marge Statique** : **+167%** pour un robot de 39 kg (résolution du goulot d'étranglement historique).
- **Vitesse** : Capacité de marche rapide jusqu'à 6-9 km/h théoriques.
- **Stabilité latérale** : Couple de Roll exceptionnel (120 N.m) pour le rattrapage d'équilibre sur terrain accidenté.

---
*Dernière mise à jour : Mars 2026*
