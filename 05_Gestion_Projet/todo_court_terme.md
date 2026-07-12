# TODO List — Actions Court Terme (Intégration Tête et Cou D-Bot)

Ce document liste les étapes d'intégration mécanique et électronique à court terme pour la tête, le cou et les capteurs associés avant d'entamer la phase d'IA locale.

---

## 📋 Actions de Montage et Validation Physique

- [ ] **Démonter le casque** (pour accéder librement au mécanisme et aux moteurs du cou).
- [ ] **Câblage des moteurs RS-05** :
  - Brancher les 2 moteurs RS-05 (Pan & Tilt).
  - Ajuster les longueurs de câbles pour qu'elles soient correctes (voire finales) en fonction du débattement et des rotations nécessaires pour éviter les tensions.
- [ ] **Premier test de rotation (Sans Casque)** :
  - Tester les rotations via le script `test_neck.py` pour valider le comportement dynamique et l'efficacité de la limite de vitesse logicielle (20°/s).
- [ ] **Remonter le casque**.
- [ ] **Définition et verrouillage des limites avec casque** :
  - Ajuster et figer les limites de rotation logicielles dans `config.py` afin d'éviter que le casque ne vienne buter mécaniquement contre la structure du cou ou n'atteigne ses limites de contrainte.
- [ ] **Intégration des Capteurs Tête** :
  - Brancher le microphone **ReSpeaker** et la caméra **OAK-D Pro**.
  - S'assurer du bon fonctionnement global de tous les éléments (moteurs, micro, caméra) lorsqu'ils sont branchés et alimentés simultanément.
- [ ] **Transition** :
  - Une fois la validation physique validée à 100%, basculer sur les tâches logicielles du fichier [TODO_Integration_IA_Locales.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/05_Gestion_Projet/TODO_Integration_IA_Locales.md).
