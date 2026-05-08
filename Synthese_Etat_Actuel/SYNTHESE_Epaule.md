# SYNTHÈSE : Architecture Épaule (D-Bot)

## 1. Actionneurs (RobStride)
L'épaule utilise une architecture **"Stacked Perpendicular"** (empilement série) optimisée pour le portage de charges frontales.

| Axe | Moteur | Couple (Pic) | Couple (Nominal) | Rôle |
| :--- | :--- | :---: | :---: | :--- |
| **Pitch** | **RobStride RS-04** | **120 N.m** | 40 N.m | Levage frontal (Axe critique) |
| **Roll** | **RobStride RS-03** | 60 N.m | 20 N.m | Écartement latéral |
| **Yaw** | **RobStride RS-02** | **17 N.m** | 6 N.m | Rotation de l'humérus (Axe distal) |

## 2. Transmission & Cinématique
- **Type** : Direct-Drive (via réducteurs planétaires intégrés).
- **Architecture** : Empilement séquentiel (Base Torse → RS-04 → RS-03 → RS-02 → Humérus).
- **Décalage Inter-Axe** : Cible < 25mm pour tendre vers une articulation quasi-sphérique.

## 3. Conception Mécanique
- **Matériau** : Aluminium **6061-T6** usiné sur NestWorks C500.
- **Brackets** :
    - **Bracket #1** : Liaison RS-04 (Rotor) → RS-03 (Stator).
    - **Bracket #2** : Liaison RS-03 (Rotor) → RS-02 (Stator).
- **Masse totale** : ~2 965g (moteurs + brackets).

## 4. Performances & Limites
- **Capacité de portage** : Jusqu'à 5 kg en continu à bras tendu, 10 kg en pic.
- **Vigilance** : Le moteur Pitch (RS-04) supporte seul la chaîne Roll+Yaw+Bras. Refroidissement passif obligatoire.

