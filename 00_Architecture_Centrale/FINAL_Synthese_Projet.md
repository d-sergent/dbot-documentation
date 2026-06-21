# Synthèse du Projet D-Bot (Évolution)

## 1. Vision et Objectifs
Le projet consiste à construire un robot humanoïde baptisé **D-Bot**.
Il s'agit d'une **évolution majeure** de la plateforme open-source **K-Bot**, améliorée avec des actionneurs modernes et une intelligence embarquée avancée. Ce n'est pas un simple fork, mais une refonte complète de l'architecture électronique et motrice.

### Améliorations Clés (vs K-Bot Original)
Le D-Bot repose sur un système de **27 moteurs RobStride** (membres, cou, taille) et **16 servomoteurs Feetech** (mains tactiles D-Hand Hybrid à 8 DOF chacune), une vision IA **Luxonis OAK-D Pro** (le LiDAR Unitree L2 étant réservé pour la V2), le tout piloté par une **NVIDIA Jetson Orin Nano Super** (67 TOPS) et une **Sony Spresense**.

## 2. Feuille de Route (Roadmap)
Le projet est découpé en 4 phases distinctes pour valider chaque étape critique.

### Phase 1 : Tête, Torse et Cou (Focus Actuel)
*   **Objectif** : Valider l'intelligence perception/audio et l'intégration mécanique du cou (VOR).
*   **Matériel** : Jetson Orin Nano (**✅ Déjà achetée**), OAK-D Pro, Spresense.
*   **Moteurs** : 2× RS-05 cou Pan/Tilt (**✅ Déjà achetés**).

### Phase 2 : Premier Bras (6-DOF)
*   **Objectif** : Validation mécanique et manipulation.
*   **Moteurs** : 6 Moteurs Robstride (1x RS-04, 2x RS-03, 2x RS-02, 1x RS-00) et **D-Hand Hybrid**.
    *   *Note : Les moteurs sont achetés ou à commander selon la BOM.*
*   **Budget Est.** : ~3 000 € (Bras + Main).

### Phase 3 : Deuxième Bras
*   **Objectif** : Coordination bimanuelle.
*   **Matériel** : + 6 Moteurs Robstride et **D-Hand Hybrid**.

### Phase 4 : Marche (Jambes)
*   **Objectif** : Locomotion et équilibre dynamique.
*   **Matériel** : + 12 Moteurs (RS-04 hanches/genoux, RS-03 hanche/cheville cardan).

## 3. Architecture Matérielle
L'architecture repose sur une séparation claire entre la puissance de calcul (IA) et le contrôle temps réel (Moteurs/Capteurs bas niveau).

### Spécifications Globales (Version Finale 6-DOF / 27-DOF)
| Paramètre | Valeur | Source / Validation |
| :--- | :--- | :--- |
| **Masse Totale** | **40.4 kg** | Calcul Juin 2026 (Architecture 27-DOF) |
| **Nb Moteurs RobStride** | **27** | 2 (Cou) + 6 (Bras G) + 6 (Bras D) + 12 (Jambes) + 1 (Taille) |
| **Nb Servomoteurs Feetech**| **16** | 2 mains D-Hand Hybrid |
| **Moteur Coude** | **RS-03** | Choisi pour le couple accru (60 N.m) |
| **Moteur Taille (Waist)** | **RS-06** | Choisi pour le lacet actif (36 N.m) |

## 4. Stratégie de Fabrication
L'utilisation d'une **Makera Carvera (CNC + 4ème axe)** combinée à une **Qidi X-Max 3 (Impression 3D Industrielle)** permet de mixer les matériaux.

| Composant | Matériau | Machine | Rationale |
| :--- | :--- | :--- | :--- |
| Brackets épaules (RS-04/03) | **Alu 6061 CNC** | C500 | Porte-à-faux du bras |
| Pied / semelle structurelle | **PA12-CF** 100% | Qidi | Résistance aux chocs, rigidité |
| Tibia / avant-bras | **PA12-CF** ou **Alu tubulaire** | Qidi/C500 | Rigidité en flexion |
| Torse (structure interne) | **PA12-CF** 100% | Qidi | Grande surface, CNC trop coûteuse |
| Coques extérieures (torse, bras) | **PETG-CF** 40% gyroid | Qidi | Esthétique carbone, léger |
| Tête (boîtier capteurs) | **PETG-CF** 60% | Qidi | Masse à minimiser |

## 5. Points de Vigilance Critique (Audit Discussion)
-   **Motorisation** : Le couple de pointe (Peak Torque) des RS-04 (hanches/genoux) atteint 120 Nm. La structure doit être en PA12-CF ou Aluminium 6061.
-   **Sécurité Électrique** : Toujours utiliser le mode **OCP** (Overcurrent Protection) sur l'alimentation Wanptek (limite à 1A pour les premiers tests).
-   **Communication** : Le bus CAN 1 Mbps exige des paires torsadées et une masse commune (GND) entre la Jetson et les moteurs.
-   **Maintenance** : Utiliser des connecteurs **WAGO 221** dans le cou pour faciliter le démontage rapide de la tête.

---
**Note** : Ce projet est une évolution active. Les choix techniques documentés ici reflètent l'état des lieux en Juin 2026.
