# SYNTHÈSE : D-Hand Hybrid (Mains Robotiques)

## 1. Actionneurs (Dynamixel 2.0)
La D-Hand Hybrid utilise une architecture tandem déportée dans l'avant-bras, combinant force et précision via le bus TTL Dynamixel.

| Fonction | Servo | Couple (12V) | Type | Rôle |
| :--- | :--- | :---: | :---: | :--- |
| **Poussée (×4)**| **XC430-W240-T** | **1.9 N.m** | Force | Pouce (Curl), Index, Majeur, Paume |
| **Précision (×4)**| **XC330-T288-T** | 1.0 N.m | Dextérité | Pouce (Opp.), Index (Abd.), Annu., Auric. |

## 2. Transmission & Tactile
- **Tendons** : Tresse **Dyneema Ø0.8mm-1.0mm** (résistance 18-20 kg) guidée par gaines PTFE.
- **Amplification** : Poulies Alu CNC Ø8mm usinées sur C500.
- **Toucher (Tactile)** : Capteurs 3-axes **eFlesh** (magnétiques sous élastomère) sur la pulpe des doigts.
- **Résultat** : Force de grip effective de **~175 N** (niveau Tesla Optimus).

## 3. Conception Mécanique
- **Masse** : ~850g par ensemble (Main + Avant-bras + Servos).
- **Structure** : Phalanges imprimées en **PA12-CF** (V1) ou Alu 7075 CNC (V4).
- **Compliance** : Supporte la compliance active (Current Control) pour la sécurité des interactions.

## 4. Performances & IA
- **DOF** : 8 DOF actifs par main (total 16).
- **Fréquence** : Boucle de contrôle à 200 Hz via SDK Python / ROS 2.
- **Simulation** : Modèle URDF haute-fidélité prêt pour l'apprentissage par renforcement (Isaac Gym).

---
### 🔗 Études Complètes
- **[21 — Étude Main Robotique D-Hand Hybrid](../21_Etude_Main_Robotique.md)**
- **[16 — Conclusions Architecture Finale](../16_Conclusions_Architecture_DBot.md)**

*Dernière mise à jour : Mars 2026*
