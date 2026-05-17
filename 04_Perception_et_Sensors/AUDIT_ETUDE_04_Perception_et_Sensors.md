# 🔍 Rapport d'Audit d'Ingénierie : 04 Perception et Sensors (D-Bot)

En tant qu'Ingénieur Senior en Revue de Conception, j'ai examiné les documents fournis pour le module "04 Perception et Sensors" du projet D-Bot. L'architecture proposée est ambitieuse et bien pensée, notamment la stratégie de fusion sensorielle et la gestion des IMU. Cependant, plusieurs points nécessitent une clarification, une validation ou une optimisation pour garantir la robustesse et la performance attendues en V1.x.

## 0. Décision d'Architecture Retenue

L'architecture de perception du D-Bot V1.x repose sur une **fusion sensorielle hétérogène** pour une localisation globale robuste et une perception locale agile.

| Choix de Conception | Justification Technique | Source(s) |
| :------------------ | :---------------------- | :-------- |
| **LiDAR Unitree L2 sur le torse (fixe)** | Stabilité du SLAM global (mouvement prévisible), FOV vertical 96° (sol au plafond), TF ROS2 statique. | `STUDY_LiDAR_Slam.md` (§5.2) |
| **Caméra OAK-D Pro FF sur la tête (orientable)** | Perception locale dense (300k pts/frame), vision nocturne active, IA embarquée, stabilisation du regard (VOR) via 2 DOF du cou. | `STUDY_LiDAR_Slam.md` (§5.2), `FINAL_Pipeline_Vision.md` (§1.2) |
| **IMU Bosch BMI270 sur le torse (co-localisée L2)** | Référentiel d'équilibre du corps (proche CoM), timing stable 416 Hz, compensation des mouvements du torse pour le SLAM LiDAR. | `STUDY_IMU_Fusion.md` (§3.1), `STUDY_LiDAR_Slam.md` (§5.1) |
| **Module audio ReSpeaker XVF-3800 (crâne)** | Solution tout-en-un (4 micros, DoA 360°, beamforming, AEC matériel), faible coût et masse, intégration simplifiée. | `FINAL_Architecture_Audio.md` (§2.1) |
| **Haut-parleur 5W 8Ω (bouche) relié au ReSpeaker** | Activation de l'AEC matériel du ReSpeaker pour une communication bidirectionnelle fluide. | `FINAL_Architecture_Audio.md` (§2.2) |

## 1. Vérification des Calculs Clés

Cette section détaille la vérification de chaque calcul numérique et des hypothèses associées.

1.  **Masse des capteurs sur la tête (OAK-D Pro FF)**
    *   **Valeur déclarée :** 91 g (`FINAL_CONSOLIDE_04`, `FINAL_Pipeline_Vision`)
    *   **Vérification :** La valeur est cohérente entre les documents.
    *   **Hypothèse sous-jacente :** Cette masse est critique pour le calcul de l'inertie cervicale et la capacité des moteurs RS-05 à réaliser la stabilisation du regard (VOR).
    *   **Statut :** ✅ Validé.
    *   **Criticité :** 🟢 SUGGESTION : Confirmer la masse réelle avec le support de montage final.

2.  **Masse du module audio ReSpeaker XVF-3800**
    *   **Valeur déclarée :** ~30 g (`FINAL_CONSOLIDE_04`, `FINAL_Architecture_Audio`)
    *   **Vérification :** La valeur est cohérente entre les documents.
    *   **Hypothèse sous-jacente :** Cette masse s'ajoute à celle de l'OAK-D Pro sur la tête, impactant l'inertie cervicale totale.
    *   **Statut :** ✅ Validé.
    *   **Criticité :** 🟢 SUGGESTION : Confirmer la masse réelle avec l'anneau TPU et les vis nylon.

3.  **Masse du haut-parleur 5W 8Ω**
    *   **Valeur déclarée :** ~20 g (`FINAL_CONSOLIDE_04`, `FINAL_Architecture_Audio`)
    *   **Vérification :** La valeur est cohérente entre les documents.
    *   **Hypothèse sous-jacente :** Le HP est placé dans la zone buccale, donc sa masse est également sur la tête.
    *   **Statut :** ✅ Validé.
    *   **Criticité :** 🟢 SUGGESTION : Confirmer la masse réelle avec le câblage JST.

4.  **Masse totale de la tête (capteurs)**
    *   **Calcul :** Masse OAK-D + Masse ReSpeaker + Masse HP = 91 g + 30 g + 20 g = **141 g**
    *   **Vérification :** Le document `STUDY_LiDAR_Slam.md` (§5.2) mentionne "OAK-D seul (~91g)" et "330g (L2+OAK-D) sur la tête" (rejeté). La masse de 141g est bien inférieure à 330g, ce qui valide l'avantage de ne pas mettre le L2 sur la tête.
    *   **Statut :** ✅ Validé.
    *   **Criticité :** 🟢 SUGGESTION : Mettre à jour la documentation pour inclure cette masse totale de la tête (capteurs) pour une meilleure visibilité.

5.  **Masse du LiDAR Unitree L2**
    *   **Valeur déclarée :** 230 g (`FINAL_CONSOLIDE_04`, `STUDY_LiDAR_Slam`)
    *   **Vérification :** La valeur est cohérente entre les documents.
    *   **Hypothèse sous-jacente :** Cette masse est ajoutée au torse, impactant le centre de masse global du robot et la dynamique du torse.
    *   **Statut :** ✅ Validé.

6.  **Fréquence de l'IMU torse (BMI270)**
    *   **Valeur déclarée :** 416 Hz (`FINAL_CONSOLIDE_04`, `STUDY_IMU_Fusion`)
    *   **Vérification :** Cohérent.
    *   **Hypothèse sous-jacente :** Cette fréquence est suffisante pour le contrôle d'équilibre bipède et la compensation de mouvement du LiDAR.
    *   **Statut :** ✅ Validé.

7.  **Fréquence de l'IMU tête (BNO085)**
    *   **Valeur déclarée :** 100 Hz (`FINAL_CONSOLIDE_04`, `STUDY_IMU_Fusion`)
    *   **Vérification :** Cohérent.
    *   **Hypothèse sous-jacente :** Cette fréquence est suffisante pour la stabilisation du regard (VOR) et le V-SLAM visuel.
    *   **Statut :** ✅ Validé.

8.  **Fréquence de scan du LiDAR L2**
    *   **Valeur déclarée :** 5.55 Hz (`FINAL_CONSOLIDE_04`, `STUDY_LiDAR_Slam`)
    *   **Vérification :** Cohérent.
    *   **Hypothèse sous-jacente :** Cette fréquence est jugée "suffisante pour marche lente" mais "insuffisante pour FAST-LIVO2" (`STUDY_LiDAR_Slam.md`). La fusion avec l'OAK-D Pro à 30 Hz est la mitigation principale.
    *   **Statut :** ✅ Validé.

9.  **Portée de la caméra OAK-D Pro FF**
    *   **Valeur déclarée :** 0,07 - 12 m (`FINAL_CONSOLIDE_04`) ou 70 cm - 12 m (`FINAL_Pipeline_Vision`)
    *   **Vérification :** **Incohérence détectée.** Le `FINAL_CONSOLIDE_04` indique 0,07 m (7 cm) tandis que le `FINAL_Pipeline_Vision` (§1.2) indique 70 cm. Le `FINAL_Pipeline_Vision` (§1.2) mentionne explicitement "Limitation connue : La portée minimale de 70cm signifie que le robot ne voit pas nettement les objets très proches de son visage."
    *   **Statut :** 🟠 IMPORTANT : Clarifier la portée minimale réelle. Si 70 cm est correct, cela a un impact sur la détection d'obstacles très proches et la manipulation fine.
    *   **Recommandation :** Mettre à jour `FINAL_CONSOLIDE_04` pour refléter la portée minimale de 70 cm et évaluer l'impact sur les scénarios de détection d'obstacles proches (ex: objets au sol juste devant les pieds).

10. **Densité de points de la fusion L2 + OAK-D Pro (zone avant 80°)**
    *   **Calcul L2 seul (zone avant 80°) :** (80° / 360°) * 64 000 pts/s ≈ 14 222 pts/s (`STUDY_LiDAR_Slam.md` §5.3)
    *   **Calcul OAK-D Pro depth :** 640 x 480 pixels = 307 200 pts/frame (`STUDY_LiDAR_Slam.md` §5.3)
    *   **Calcul fusionné :** 14 222 pts/s (L2) + 307 200 pts/frame (OAK-D) ≈ **314 000 pts/frame** (à 30 Hz) (`STUDY_LiDAR_Slam.md` §5.3)
    *   **Vérification :** Les calculs sont cohérents et la conclusion que "Notre solution budget bat le MID-360 en densité locale !" est justifiée par les chiffres.
    *   **Statut :** ✅ Validé.

11. **Vitesse maximale des moteurs du cou (RS-05)**
    *   **Valeur déclarée :** 21 rad/s (max) (`FINAL_CONSOLIDE_04`)
    *   **Vérification :** Cohérent.
    *   **Calcul de la vitesse requise pour VOR en course :**
        *   Oscillation torse en course : ±15° à 3 Hz (`STUDY_LiDAR_Slam.md` §10.2)
        *   Amplitude angulaire : 15° = 0.2618 rad
        *   Fréquence angulaire : 3 Hz
        *   Vitesse angulaire max (simplifiée) : Amplitude * 2 * π * Fréquence = 0.2618 * 2 * π * 3 ≈ 4.93 rad/s
        *   Le document `STUDY_LiDAR_Slam.md` (§10.2) estime "15°×3Hz = ~45°/s = ~0.785 rad/s". Cette estimation est plus conservative et probablement basée sur une moyenne ou une vitesse crête différente.
        *   Marge : 0.785 rad/s / 21 rad/s ≈ 3.7% de la capacité du RS-05.
    *   **Statut :** ✅ Validé. La marge est très confortable, même avec l'estimation la plus élevée.

12. **Consommation de courant du ReSpeaker XVF-3800**
    *   **Valeur déclarée :** ≈ 300 mA (`FINAL_CONSOLIDE_04`, `FINAL_Architecture_Audio`)
    *   **Vérification :** Cohérent.
    *   **Hypothèse sous-jacente :** Le hub USB 3.0 de la Jetson doit fournir ≥ 1 A.
    *   **Statut :** ✅ Validé.
    *   **Criticité :** 🟠 IMPORTANT : La capacité du hub USB n'est pas confirmée dans les sources. Il est crucial de s'assurer que le hub peut fournir 300mA pour le ReSpeaker, plus l'OAK-D Pro (qui peut consommer jusqu'à 900mA en pointe) et le LiDAR L2 (non spécifié, mais un LiDAR 3D peut consommer 500mA-1A).

13. **Distance entre scans L2 et OAK-D en course (7 km/h)**
    *   **Vitesse :** 7 km/h = 1.94 m/s
    *   **Distance entre scans L2 :** 1.94 m/s / 5.55 Hz ≈ **0.35 m** (`STUDY_LiDAR_Slam.md` §10.1)
    *   **Distance entre frames OAK-D :** 1.94 m/s / 30 Hz ≈ **0.065 m** (`STUDY_LiDAR_Slam.md` §10.1)
    *   **Vérification :** Les calculs sont cohérents.
    *   **Statut :** ✅ Validé.

14. **GPU Jetson Orin Nano Super (67 TOPS)**
    *   **Utilisation déclarée :** ~52% max (marche, OAK-D, audio IA), laissant 48% de marge (`FINAL_Architecture_Audio`)
    *   **Utilisation RTAB-Map :** ~40-60% GPU (`STUDY_LiDAR_Slam.md` §10.3)
    *   **Utilisation Planning/Contrôle :** ~20-30% GPU (`STUDY_LiDAR_Slam.md` §10.3)
    *   **Vérification :** Il y a une légère incohérence ou un manque de clarté. Si RTAB-Map seul peut consommer 40-60%, et que le planning/contrôle prend 20-30%, le total pourrait dépasser 52% (ex: 60% + 30% = 90%). L'estimation de 52% max dans `FINAL_Architecture_Audio` semble sous-estimer la charge combinée.
    *   **Statut :** 🟠 IMPORTANT : L'estimation de la consommation GPU est potentiellement sous-évaluée.
    *   **Recommandation :** Fournir une estimation consolidée de la consommation GPU pour les scénarios de charge maximale (ex: course avec SLAM, VOR, audio IA, planning et contrôle). Préciser si le 52% inclut déjà le SLAM et le planning, ou si c'est une somme partielle.

15. **Dimensions des ouvertures acoustiques du crâne pour les micros**
    *   **Spécifications :** 4 trous Ø10 mm, chanfrein 45° (~1 mm profondeur), 3-5 mm d'air libre entre micro et ouverture. (`FINAL_Architecture_Audio` §2.3.1)
    *   **Vérification :** Ces spécifications sont détaillées et acoustiquement sensées.
    *   **Statut :** ✅ Validé.

16. **Épaisseur de l'anneau TPU anti-vibration**
    *   **Spécification :** 3 mm (`FINAL_CONSOLIDE_04`, `FINAL_Architecture_Audio`)
    *   **Vérification :** Cohérent.
    *   **Statut :** ✅ Validé.

17. **Seuils d'alerte Spresense (Détection Réflexe)**
    *   **Seuil d'alerte :** >10% de la zone "Proche" (0-40cm) (`FINAL_Perception_Collaborative`)
    *   **Seuil E-Stop :** < 15cm (`FINAL_Perception_Collaborative`)
    *   **Vérification :** Cohérent.
    *   **Hypothèse sous-jacente :** La caméra HDR du bassin est capable de détecter des objets avec une précision suffisante à ces distances et la latence de l'E-Stop est compatible avec la vitesse du robot.
    *   **Statut :** ✅ Validé.

18. **Prix total estimé (BOM locale)**
    *   **Valeur déclarée :** ≈ 1 259 € (hors éléments à compléter) (`FINAL_CONSOLIDE_04`)
    *   **Vérification :**
        *   ReSpeaker: 35 €
        *   HP: 5 €
        *   OAK-D Pro: 399 €
        *   Unitree L2: 380 € (419$ ≈ 380€)
        *   Total = 35 + 5 + 399 + 380 = 819 €
        *   Le total de 1259 € est significativement plus élevé que la somme des composants listés avec un prix. La différence (1259 - 819 = 440 €) doit correspondre aux éléments "À COMPLÉTER" (BMI270, RS-05 x2, câbles, silent-blocks, anneau TPU, vis, mousses).
    *   **Statut :** 🟠 IMPORTANT : Le calcul du "Total estimé" est correct si les éléments "À COMPLÉTER" représentent bien 440 €. Cependant, sans les prix unitaires de ces éléments, il est difficile de valider la cohérence de ce total.
    *   **Recommandation :** Compléter la BOM avec des estimations de prix pour tous les éléments afin de justifier le total estimé.

## 2. Carte des Dépendances Inter-Membres

Ce module est au cœur de l'interaction du D-Bot avec son environnement et a de nombreuses dépendances.

*   **[Masse OAK-D Pro (91g) + ReSpeaker (30g) + HP (20g) = 141g]** → **Module Cou (RS-05)** → **Inertie cervicale, couple requis pour VOR**.
*   **[Données IMU Torse (BMI270, 416 Hz)]** → **Module Locomotion (Contrôle d'équilibre)** → **Stabilité bipède, détection de chute**.
*   **[Données IMU Torse (BMI270, 416 Hz)]** → **Module Navigation (SLAM)** → **Odométrie inertielle pour le SLAM LiDAR/Visuel**.
*   **[Données IMU Tête (BNO085, 100 Hz)]** → **Module Cou (RS-05)** → **Stabilisation active du regard (VOR)**.
*   **[Données IMU Tête (BNO085, 100 Hz)]** → **Module Navigation (SLAM)** → **V-SLAM visuel**.
*   **[Nuage de points LiDAR (L2, 64k pts/s)]** → **Module Navigation (SLAM)** → **Cartographie 3D, localisation globale, évitement d'obstacles**.
*   **[Flux Depth/RGB OAK-D Pro (30 FPS)]** → **Module Navigation (SLAM)** → **Perception locale dense, V-SLAM, reconnaissance d'objets**.
*   **[Flux Depth/RGB OAK-D Pro (30 FPS)]** → **Module IA (Jetson Orin Nano)** → **Exécution IA embarquée (VPU), traitement IA audio/vision**.
*   **[Données DoA ReSpeaker (360°)]** → **Module Cou (RS-05)** → **Orientation de la tête vers la source sonore**.
*   **[Consommation électrique ReSpeaker (~300mA), OAK-D Pro (~900mA), L2 (~500mA-1A)]** → **Module Énergie (Jetson USB Hub, Batterie)** → **Capacité du hub, autonomie de la batterie**.
*   **[Flag `OBSTACLE_NEAR` (Spresense)]** → **Module IA (Jetson Orin Nano)** → **Déclenchement de la confirmation cognitive par l'OAK-D**.
*   **[Flag `E-Stop` (Spresense)]** → **Module Électronique (Bus CAN)** → **Arrêt d'urgence du robot**.
*   **[Câbles USB (OAK-D, L2)]** → **Module Mécanique (Cou)** → **Contraintes de torsion, fatigue mécanique**.
*   **[Vibrations du cou (RS-05)]** → **Module Audio (ReSpeaker)** → **Bruit mécanique sur les micros (mitigé par TPU)**.
*   **[Vibrations du torse (locomotion)]** → **Module Perception (LiDAR L2)** → **Bruit sur le nuage de points (mitigé par silent-blocks et filtre SOR)**.
*   **[Thermistance moteurs RS-04/RS-05]** → **Module Électronique (Spresense ADC)** → **Surveillance thermique des actionneurs**.

## 3. Manques Critiques & Incertitudes

Cette section met en lumière les informations manquantes, les hypothèses non justifiées et les points nécessitant une validation physique.

1.  **🔴 BLOQUANT : Complétude et Validation de la BOM (Prix et Fournisseurs)**
    *   **Description :** De nombreux éléments de la BOM (`FINAL_CONSOLIDE_04` §3) sont marqués **[À COMPLÉTER]** (BMI270 Add-on, RS-05, câbles USB, silent-blocks, anneau TPU, vis, mousses). Le prix total estimé de 1259 € est basé sur des hypothèses pour ces éléments non spécifiés.
    *   **Risque :** Dépassement budgétaire, retards d'approvisionnement, choix de composants non optimaux faute de spécifications claires.
    *   **Action recommandée :** Finaliser la BOM avec des références précises, fournisseurs et prix unitaires pour *chaque* composant. Obtenir des devis pour les RS-05 et le BMI270.

2.  **🟠 IMPORTANT : Capacité du Hub USB de la Jetson Orin Nano**
    *   **Description :** Le ReSpeaker consomme ≈ 300 mA. L'OAK-D Pro peut consommer jusqu'à 900 mA. Le LiDAR L2 n'a pas de consommation spécifiée mais peut être de l'ordre de 500 mA à 1 A. Le document mentionne "vérifier que le hub USB 3.0 fournit ≥ 1 A" (`FINAL_CONSOLIDE_04` §6, point 6). Un hub de 1A serait insuffisant pour l'ensemble des capteurs.
    *   **Risque :** Instabilité des capteurs (déconnexions, performances dégradées) due à une alimentation insuffisante, surtout en pointe.
    *   **Action recommandée :** Mesurer la consommation réelle de l'OAK-D Pro et du L2 en fonctionnement nominal et en pointe. Spécifier et valider la capacité totale du hub USB de la Jetson (ou d'un hub externe si nécessaire) pour supporter la charge combinée de tous les périphériques USB.

3.  **🟠 IMPORTANT : Spécifications détaillées des câbles USB flexibles**
    *   **Description :** Le document mentionne "Câble USB-3 (30-40cm) ; blindé ; résistance aux torsions du cou" (`FINAL_CONSOLIDE_04` §2) et "câble USB3 spiralé ou extra-souple" (`STUDY_LiDAR_Slam.md` §8). Cependant, aucune référence spécifique, impédance ou spécification de cycle de torsion n'est donnée (`FINAL_CONSOLIDE_04` §6, point 3).
    *   **Risque :** Défaillance prématurée des câbles due à la fatigue mécanique, perte de données ou interférences EMI/RFI.
    *   **Action recommandée :** Sélectionner un modèle de câble USB 3.0 industriel (ex: Amphenol Ultra-Flex, LAPP UNITRONIC® ROBOT) avec une spécification de cycle de flexion/torsion adaptée aux mouvements du cou. Valider la longueur et le blindage.

4.  **🟠 IMPORTANT : Validation des gains VOR et latence totale du système**
    *   **Description :** Les gains `vor_gain_pitch = 0.9` et `vor_gain_yaw = 0.85` sont proposés (`STUDY_IMU_Fusion.md` §4.2). La latence totale du système VOR doit être < 30 ms (`FINAL_CONSOLIDE_04` §5.11). Ces valeurs sont des hypothèses de conception.
    *   **Risque :** Stabilisation inefficace du regard, motion blur sur l'OAK-D, ou oscillations indésirables de la tête.
    *   **Action recommandée :** Réaliser des tests physiques sur le robot en mouvement (marche, course) pour ajuster et valider empiriquement les gains VOR. Mesurer la latence réelle de la boucle de contrôle (IMU → Jetson → Moteurs RS-05 → Mouvement tête).

5.  **🟡 À SURVEILLER : Caractérisation thermique du BMI270**
    *   **Description :** Aucune caractérisation thermique n'est fournie pour le BMI270 (`FINAL_CONSOLIDE_04` §6, point 8).
    *   **Risque :** Dérive des mesures IMU en cas de variations de température importantes à l'intérieur du torse, impactant la précision du SLAM et de l'équilibre.
    *   **Action recommandée :** Effectuer un test de dérive en température (0°C-50°C) sur le banc pour le BMI270. Si une dérive significative est observée, implémenter une compensation logicielle.

6.  **🟡 À SURVEILLER : Efficacité de l'isolation acoustique et anti-vibration**
    *   **Description :** L'efficacité de la mousse haute densité entre HP et micros, de l'anneau TPU et des silent-blocks pour le L2 est assumée mais non quantifiée (ex: en dB de réduction). La simulation dynamique vérifie que les vibrations du cou n'excèdent pas 5 mm s⁻¹ sur le ReSpeaker (`FINAL_CONSOLIDE_04` §4), mais cela ne garantit pas l'absence de bruit acoustique.
    *   **Risque :** Bruit résiduel sur les micros (moteurs, HP), dégradation des performances audio (DoA, ASR). Bruit sur le nuage de points LiDAR.
    *   **Action recommandée :** Réaliser des tests acoustiques (mesure du rapport signal/bruit) et vibratoires (analyse spectrale) sur le robot assemblé pour valider l'efficacité des solutions d'isolation. Ajuster les matériaux ou les designs si nécessaire.

7.  **🟡 À SURVEILLER : Performance et robustesse de la "Détection Réflexe" Spresense**
    *   **Description :** Le système de détection réflexe utilise une caméra HDR (Bassin) et un CNN léger sur la Spresense (`FINAL_Perception_Collaborative`). Les détails sur le modèle CNN (précision, taux de faux positifs/négatifs), le FOV et la résolution de la caméra sont manquants.
    *   **Risque :** Faux positifs (arrêts inutiles) ou faux négatifs (collisions non détectées) du système d'alerte et d'E-Stop.
    *   **Action recommandée :** Spécifier la caméra du bassin (modèle, résolution, FOV). Caractériser les performances du modèle CNN (précision, rappel, latence) et réaliser des tests de validation rigoureux avec différents types d'obstacles et conditions d'éclairage.

## 4. Propositions d'Amélioration

Voici quelques propositions concrètes pour renforcer la conception actuelle du module "Perception et Sensors" pour la V1.x.

1.  **🟢 SUGGESTION (Bénéfice Élevé / Complexité Faible) : Standardisation et Complétude de la BOM**
    *   **Description :** Créer un modèle de BOM standardisé pour tous les modules, incluant systématiquement : Référence fabricant, Fournisseur principal, Fournisseur secondaire, Prix unitaire, Quantité, Prix total, Délai d'approvisionnement estimé, et un lien vers la fiche technique.
    *   **Justification :** Cela permettra une gestion de projet plus fluide, une meilleure estimation des coûts et des délais, et une traçabilité accrue des composants. Le manque actuel d'informations pour de nombreux éléments est un point de faiblesse.
    *   **Action :** Mettre à jour la BOM du module 04 avec toutes les informations manquantes, en collaboration avec les équipes d'achat et de logistique.

2.  **🟠 IMPORTANT (Bénéfice Moyen / Complexité Moyenne) : Implémentation d'un Moniteur de Consommation USB**
    *   **Description :** Intégrer un petit module de mesure de courant USB (ex: INA219 ou équivalent) sur le port USB alimentant le hub ou les capteurs critiques (OAK-D, L2, ReSpeaker).
    *   **Justification :** Cela permettrait de surveiller en temps réel la consommation électrique des capteurs, de détecter les surcharges potentielles du hub USB, et de diagnostiquer rapidement les problèmes d'alimentation qui pourraient affecter la stabilité des capteurs. C'est une mesure préventive contre les risques identifiés au point 3.2.
    *   **Action :** Sélectionner un module de mesure de courant compatible Jetson, l'intégrer au câblage USB et développer un nœud ROS2 pour publier les données de consommation.

3.  **🟡 À SURVEILLER (Bénéfice Moyen / Complexité Faible) : Procédure de Calibration et de Validation Acoustique**
    *   **Description :** Développer une procédure de test standardisée pour valider les performances acoustiques du ReSpeaker après assemblage. Cela inclurait des mesures de DoA (précision angulaire), de SNR (rapport signal/bruit) en présence de bruit moteur, et de l'efficacité de l'AEC.
    *   **Justification :** Bien que l'intégration acoustique soit détaillée, sa performance réelle dépendra de l'assemblage. Une procédure de test permettra de garantir que les objectifs de performance audio sont atteints et de diagnostiquer les problèmes (ex: fuites acoustiques, vibrations).
    *   **Action :** Définir les métriques de performance acoustique cibles, élaborer un protocole de test (ex: utilisation d'une source sonore calibrée, enregistrement des micros, analyse spectrale) et l'intégrer aux instructions de montage critiques.

4.  **🟢 SUGGESTION (Bénéfice Faible / Complexité Faible) : Optimisation de la Résolution OAK-D en Mode Course**
    *   **Description :** Le document `STUDY_LiDAR_Slam.md` (§10.3) mentionne la possibilité de réduire la résolution OAK-D de 640x480 à 320x240 en mode course pour libérer du GPU. Cette optimisation devrait être implémentée et testée.
    *   **Justification :** Permet de maximiser la marge GPU pour les algorithmes de planification et de contrôle de balance critiques en mode course, tout en conservant une détection d'obstacles suffisante à courte portée.
    *   **Action :** Implémenter la logique de changement de résolution dynamique dans le nœud `oak_camera.py` en fonction du mode de locomotion du robot, et valider que la détection d'obstacles reste fiable à 320x240.

## 5. Synthèse du Niveau de Maturité

★★★★☆ — La conception du module "Perception et Sensors" est **très mature** sur le plan architectural et fonctionnel. La stratégie de fusion L2-torse/OAK-D-tête est particulièrement bien justifiée et innovante pour le budget. Les détails d'intégration acoustique et les stratégies IMU sont également solides. Le principal manque de maturité réside dans la **complétude de la BOM** et la **validation expérimentale** de certaines hypothèses (consommation USB, gains VOR, efficacité acoustique) qui, si non adressées, pourraient entraîner des retards ou des problèmes de performance en phase d'intégration finale.