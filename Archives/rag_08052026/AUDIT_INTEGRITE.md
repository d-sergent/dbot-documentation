# 🛡️ Rapport d'Intégrité de la Documentation D-Bot
> **Date de génération** : 2026-05-08 21:39:01
> **Modèle utilisé** : `openrouter` (tencent/hy3-preview:free)

Ce rapport est généré automatiquement via le système **Graph-RAG**.

## 1. Squelette (Masse & Moteurs)
# Tableau Comparatif Masse Totale & Nombre de Moteurs RobStride (D-Bot)

| Source Document / Entité KG | Masse Totale (D-Bot) | Nombre de Moteurs RobStride | Notes |
| :--- | :--- | :--- | :--- |
| **Entité KG : D-Bot** | 38-39 kg (cible), 39.4 kg (cible), 40.2 kg (référence) | 24 (majoritaire), 26 (autre record) | Confirme l'utilisation d'actionneurs QDD RobStride, mentionne une contradiction sur le nombre de moteurs. |
| **annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md** | 38-39 kg (KG), 39 kg (15_Analyse_Biomecanique.md), ~39.4 kg (Synthese_Torse_Cou.md) | 24 (majoritaire) | Synthèse des contradictions de masse et de nombre de moteurs entre documents. |
| **01_Synthese_Projet.md (version 5-DOF)** | 38-39 kg | 24 | Mentionne 24 moteurs RobStride + 16 servomoteurs Dynamixel pour les mains. |
| **01_Synthese_Projet.md (version 6-DOF)** | 40.2 kg | 26 | Spécification finale 6-DOF : 2 (cou) + 6 (bras G) + 6 (bras D) + 12 (jambes) = 26 moteurs. |
| **14_Cinematique_Moteurs.md** | Non spécifié | 24 | Base K-Bot (20 moteurs) + 2 (cou) + 2 (poignets) = 24 moteurs totaux. |
| **04_Electronique_Cablage.md** (cité dans AUDIT_INTEGRITE.md) | Non spécifié | 24 | Décomposition : 2 (cou) + 5 (bras G) + 5 (bras D) + 12 (jambes) = 24 moteurs. |
| **15_Analyse_Biomecanique.md** (cité dans AUDIT_INTEGRITE.md) | 39 kg | Non spécifié | Référence à la "Révision Cardan 39 kg". |
| **Synthese_Torse_Cou.md** (cité dans AUDIT_INTEGRITE.md) | ~39.4 kg | Non spécifié | Scénario B Option Hybride. |
| **Relation KG : D-Bot ↔ RobStride** | - | 24 vs 26 | Confirme explicitement la divergence entre 24 et 26 moteurs. |

# Contradictions Identifiées

## 1. Contradiction sur la Masse Totale du D-Bot
Les fichiers sources suivants présentent des valeurs divergentes pour la masse totale du D-Bot :
- annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md
- 01_Synthese_Projet.md (version 5-DOF)
- 01_Synthese_Projet.md (version 6-DOF)
- 15_Analyse_Biomecanique.md
- Synthese_Torse_Cou.md
- Entité Knowledge Graph : D-Bot

**Question :** Quelle est la masse totale exacte cible pour la version finale du D-Bot : 39 kg (arrondi/cible), 39.4 kg (calcul précis du Scenario B) ou 40.2 kg (calcul juin 2026 pour l'architecture 6-DOF) ?

## 2. Contradiction sur le Nombre Total de Moteurs RobStride du D-Bot
Les fichiers sources suivants présentent des valeurs divergentes pour le nombre total de moteurs RobStride :
- Entité Knowledge Graph : D-Bot
- Relation Knowledge Graph : D-Bot ↔ RobStride
- annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md
- 01_Synthese_Projet.md (version 5-DOF)
- 01_Synthese_Projet.md (version 6-DOF)
- 14_Cinematique_Moteurs.md
- 04_Electronique_Cablage.md

**Question :** Le nombre total de moteurs RobStride pour le D-Bot final est-il de 24 (architecture 5-DOF par bras) ou 26 (architecture 6-DOF par bras) ?

## 3. Contradiction sur le Nombre de Moteurs par Jambe
Les fichiers sources suivants présentent des valeurs divergentes pour le nombre de moteurs RobStride alloués aux jambes :
- 04_Electronique_Cablage.md
- annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md
- 14_Cinematique_Moteurs.md

**Question :** Le décompte de 12 moteurs pour les jambes (6 par jambe) est-il correct, ou faut-il ajuster ce nombre pour refléter l'architecture F-A-R à la hanche et les actionneurs de la cheville (ce qui pourrait porter le total à 14 ou 16 moteurs RobStride pour les jambes) ?

### References

- [1] annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md
- [2] 01_Synthese_Projet.md
- [3] 14_Cinematique_Moteurs.md
- [4] 04_Electronique_Cablage.md
- [5] 15_Analyse_Biomecanique.md

---

## 2. Cinématique (Moteurs par Axe)
### Vérification de la cohérence des modèles de moteurs par articulation

J'ai analysé l'ensemble du Knowledge Graph et des Document Chunks fournis pour valider les modèles de moteurs associés à chaque articulation (Épaule, Coude, Poignet, Hanche, Genou, Cheville), identifier les contradictions et signaler les anciens modèles encore présents.

---

#### Épaule (Shoulder)
Aucun modèle de moteur spécifique n'est explicitement associé à l'épaule dans les documents consultés. Les servomoteurs RS-02, RS-03, RS-04 et RS-06 sont mentionnés comme utilisés dans les membres (limbs) du robot, mais aucune attribution claire à l'épaule n'est faite.

---

#### Coude (Elbow)
Le modèle **RS-06** (version 0.6.0.11) est cohérentment identifié comme le moteur de pitch du coude dans le document `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Ce modèle bénéficie de mises à jour en Avril 2026 (planificateur de vitesse adaptatif, remontées d'erreurs CANopen exclusives) et ne présente aucune contradiction documentaire.

---

#### Poignet (Wrist)
Le modèle **RS-00** est listé comme moteur de pitch du poignet dans `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Cependant, ce modèle n'est pas inclus dans les mises à jour de moteurs d'Avril 2026, et une référence à l'ancienne révision RS00.27 est faite dans les notes de mise à jour. L'entité Sn du Knowledge Graph mentionne également que les RS-00 sont destinés aux poignets, mais ce modèle semble être une version ancienne par rapport aux gammes RS-03 (v0.3.1.41), RS-04 (v0.4.1.29), RS-05 (v0.5.0.13) et RS-06 (v0.6.0.11) qui bénéficient de mises à jour régulières.

Fichiers sources en contradiction :
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- Notes de mise à jour des moteurs Avril 2026 (chunk sans nom de fichier, contenu débutant par "sur les bras/cuisses.\n\n### RS03 Actuel (v0.3.1.41)...")
- Knowledge Graph (entité Sn)

**Question :** Le moteur RS-00 (révision 0.0.27) est-il toujours le modèle actuel pour le poignet (Poignet Pitch) malgré l'absence de mises à jour dans les notes de version Avril 2026, ou doit-il être remplacé par un modèle plus récent ?

---

#### Hanche (Hip)
Les modèles **RS-04** (pitch, version 0.4.1.29) et **RS-03** (roll et yaw, version 0.3.1.41) sont cohérents entre tous les documents consultés. L'architecture F-A-R (Pitch→Roll→Yaw) adoptée en Avril 2026 référence explicitement ces modèles, qui bénéficient tous deux de mises à jour fonctionnelles en Avril 2026. Aucune contradiction n'est identifiée.

---

#### Genou (Knee)
Le modèle **RS-04** est associé au vilebrequin de la transmission GT3 du genou dans les chunks de leviers biomécaniques, ce qui est cohérent avec la documentation `15d_Genou_et_Course.md` référencée dans `15_Analyse_Biomecanique.md`. Les modèles RS-02, RS-03 et RS-06 sont listés uniquement comme alternatives de mise à niveau dans `15e_Alternatives_Moteurs_Genou.md`, sans contradiction avec l'usage actuel du RS-04.

---

#### Cheville (Ankle)
Le modèle **RS-03** (2 unités) est associé à l'architecture de cheville cardan dans `15c_Revision_Cardan_39kg.md` (référencé dans `15_Analyse_Biomecanique.md`). Ce modèle bénéficie de mises à jour en Avril 2026, et aucune contradiction n'est identifiée.

---

#### Incohérence supplémentaire : Attribution du RS-05 (Cou vs Poignet)
L'entité Sn du Knowledge Graph mentionne que les RS-05 sont destinés aux poignets et au cou, mais l'entité Rs05 du Knowledge Graph et le document `32_Configuration_ID_Limites_Cou.md` restreignent l'usage du RS-05 au cou (Neck) et aux applications Pan-Tilt. Le document `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md` confirme par ailleurs que le poignet utilise le RS-00, pas le RS-05.

Fichiers sources en contradiction :
- Knowledge Graph (entité Sn)
- Knowledge Graph (entité Rs05)
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- `32_Configuration_ID_Limites_Cou.md`

**Question :** Le moteur RS-05 est-il exclusivement réservé au cou (Neck) comme indiqué dans l'entité Rs05 et le document 32_Configuration_ID_Limites_Cou.md, ou doit-il également être utilisé pour les poignets comme mentionné dans l'entité Sn du Knowledge Graph ?

---

#### Anciens modèles encore présents
- **RS-02** : Utilisé comme moteur de supination (rotation de l'avant-bras) dans `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Ce modèle partage un bug (Sn bug) avec le RS-01 selon l'entité Sn, n'est pas inclus dans les mises à jour Avril 2026, et est listé uniquement comme alternative de mise à niveau pour le genou.

Fichiers sources en contradiction :
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- `15_Analyse_Biomecanique.md` (référence `15e_Alternatives_Moteurs_Genou.md`)
- Knowledge Graph (entité Sn)

**Question :** Le moteur RS-02 est-il toujours le modèle actuel pour la supination de l'avant-bras, ou doit-il être remplacé par un modèle plus récent (RS-03, RS-04, RS-06) comme suggéré par son absence des mises à jour Avril 2026 ?

---

### References

---

## 3. Électronique (Bus & Puissance)
Voici le résultat de la vérification de cohérence entre les documents de synthèse, le guide électronique (04_Electronique_Cablage.md) et les guides de test, portant sur la tension d'alimentation et le nombre de moteurs par bus CAN.

Plusieurs points sont cohérents entre les sources : les tests sur banc utilisent une tension de 24V pour les moteurs Robstride, conformément au guide de test (33_Test_Multi_Moteurs_CAN_Banc.md) et aux documents de configuration du cou. La Jetson Orin Nano est spécifiée pour recevoir une alimentation en 19V dans le guide électronique et les fiches techniques matérielles. Le système final D-Bot suit la norme de tension K-Bot de 48V (13S NMC), comme indiqué dans la synthèse et les entités de la base de connaissances. Le bus CAN fonctionne à une vitesse de 1 Mbps, partagé entre la Jetson et les 24 moteurs Robstride répartis sur 5 bus dédiés, ce qui est cohérent entre le guide électronique et les spécifications du projet.

## 1. Alimentation (Tension Batterie)

Une incohérence majeure concerne l'alimentation de la Jetson Orin Nano :
- Fichiers sources contradictoires :
  - 04_Electronique_Cablage.md indique une alimentation de 19V DC pour la Jetson.
  - Synthese_Etat_Actuel/SYNTHESE_Electronique.md indique une régulation DC-DC 48V → 5V pour la Jetson et la Spresense, incompatible avec la plage de tension de 19V requise pour la Jetson Orin Nano.

**Question :** Le document de synthèse indique une régulation 48V → 5V pour la Jetson, tandis que le guide électronique (04_Electronique_Cablage.md) et les spécifications matérielles de la Jetson Orin Nano imposent une alimentation en 19V : souhaitez-vous corriger la synthèse pour indiquer une régulation 48V → 19V pour la Jetson ?

## 2. Bus CAN (Nombre de moteurs par bus)

Première incohérence : règle de topologie du bus CAN
- Fichiers sources contradictoires :
  - 04_Electronique_Cablage.md interdit formellement toute topologie en étoile (Y) et impose une topologie en daisy-chain (série) pour tous les bus CAN.
  - Doc 42 (Guide de configuration du cou) et 33_Test_Multi_Moteurs_CAN_Banc.md imposent une topologie en étoile pour le bus du cou (moteurs RS-05), ces derniers ne disposant que d'un port CAN et ne pouvant être chaînés en série.

**Question :** Le guide électronique (04_Electronique_Cablage.md) interdit formellement toute topologie en étoile pour le bus CAN, mais les documents spécifiques au cou (Doc 42) et le guide de test (33_Test_Multi_Moteurs_CAN_Banc.md) imposent une topologie en étoile pour les moteurs RS-05 : souhaitez-vous modifier le guide électronique pour autoriser une exception de topologie en étoile pour les bus utilisant des moteurs à port CAN unique ?

Deuxième incohérence : règle de résistance de terminaison
- Fichiers sources contradictoires :
  - 04_Electronique_Cablage.md impose une résistance de terminaison 120 Ω sur le dernier moteur de chaque bus CAN en daisy-chain.
  - Doc 42 indique qu'aucune résistance de terminaison n'est nécessaire pour le bus du cou si les longueurs de câbles sont inférieures à 30 cm, contredisant la règle générale du guide électronique.

**Question :** Le guide électronique (04_Electronique_Cablage.md) impose une résistance de terminaison 120 Ω sur le dernier moteur de chaque bus, tandis que le Doc 42 indique qu'aucune terminaison n'est nécessaire pour le bus cou si les câbles sont < 30 cm : souhaitez-vous appliquer la règle de terminaison du guide électronique à l'ensemble du robot, ou valider l'exception pour les câbles courts < 30 cm ?

Troisième incohérence : capacité par bus et délimitation du bus centralisé
- Fichiers sources contradictoires :
  - 04_Electronique_Cablage.md décrit un bus CAN centralisé unique avec une limite de 5-6 moteurs par bus en topologie daisy-chain.
  - Doc 42 et 33_Test_Multi_Moteurs_CAN_Banc.md indiquent que le bus du cou (Bus CAN 1) est un bus dédié indépendant de la chaîne principale des membres, et ne compte pas dans le quota de 5-6 moteurs du bus centralisé.

**Question :** Le guide électronique (04_Electronique_Cablage.md) décrit un bus CAN centralisé unique avec 5-6 moteurs en série, mais les documents spécifiques au cou (Doc 42) et le guide de test (33_Test_Multi_Moteurs_CAN_Banc.md) indiquent que le cou dispose d'un bus CAN dédié (Bus 1) indépendant de la chaîne principale : souhaitez-vous modifier le guide électronique pour préciser que les moteurs RS-05 utilisent un bus dédié distinct du bus centralisé des membres ?

### References

* [1] 04_Electronique_Cablage.md
* [2] 33_Test_Multi_Moteurs_CAN_Banc.md
* [3] Synthese_Etat_Actuel/SYNTHESE_Electronique.md
* [4] Vérification de cohérence (Synthèses, Guide Électronique, Guides de Test)
* [5] Doc 42 (Guide de configuration du cou)

---

## 4. Perception & IA
Les spécifications de la caméra OAK-D Pro, de l'IMU principale et de la Jetson Orin Nano ne sont pas toutes identiques partout. Des divergences sont identifiées sur la version de l'OAK-D Pro, l'IMU intégrée, le modèle de Jetson installé et sa puissance de calcul. L'IMU principale (BMI270) est la seule à présenter des spécifications totalement cohérentes entre tous les documents.

## 1. Caméra OAK-D Pro
Les spécifications de la caméra OAK-D Pro présentent les points de cohérence et de divergence suivants :

### Spécifications cohérentes
Le poids de l'OAK-D Pro FF est confirmé à 91 g (0,091 kg) dans les documents `SYNTHESE_Audio_IMU.md`, `07_Vision_IA.md` et les annexes de calcul de masse. L'utilisation de la version Fixed Focus (FF) est confirmée par `SYNTHESE_Audio_IMU.md` et `07_Vision_IA.md`.

### Divergences identifiées
#### Divergence 1 : Version de l'OAK-D Pro
Fichiers sources contradictoires :
- `SYNTHESE_Audio_IMU.md`
- `07_Vision_IA.md`
- `51_Installation_OAK_D_DepthAI.md`

Le document de synthèse et l'étude de vision confirment la version Fixed Focus (FF), tandis que le guide d'installation ne précise pas la version (FF ou SR) et se contente de mentionner l'OAK-D Pro générique. Le tableau comparatif de `07_Vision_IA.md` liste l'OAK-D SR comme alternative non sélectionnée.

**Question :** Quelle est la version exacte de l'OAK-D Pro installée (Fixed Focus ou Standard) ?

#### Divergence 2 : IMU intégrée
Fichiers sources contradictoires :
- `SYNTHESE_Audio_IMU.md`
- `07_Vision_IA.md`

Le document de synthèse indique que l'IMU BNO085 est située dans la tête pour la stabilisation du regard, tandis que le tableau comparatif de l'étude de vision indique que l'OAK-D Pro possède une IMU BNO085 9 axes intégrée.

**Question :** L'IMU BNO085 mentionnée dans la tête est-elle celle intégrée à l'OAK-D Pro, ou s'agit-il d'un capteur IMU supplémentaire ajouté spécifiquement pour le SLAM ?

## 2. IMU principale
L'IMU principale pour l'équilibre bipède est le Bosch BMI270 situé dans le torse, avec une fréquence de 416 Hz. Cette spécification est cohérente entre `SYNTHESE_Audio_IMU.md`, `07_Vision_IA.md` et les guides d'intégration de capteurs. Aucune divergence n'est identifiée sur ce composant.

L'IMU BNO085 (OAK-D, tête, 100 Hz pour la stabilisation du regard et le SLAM) présente la même divergence que mentionnée en section 1.2.

## 3. Jetson Orin Nano
Les spécifications de la Jetson Orin Nano présentent les points suivants :

### Spécifications cohérentes
La capacité RAM de 8 Go est confirmée par `SYNTHESE_Audio_IMU.md` et `ETUDE_Hardware_Orin_vs_Thor.md`. Le poids de 0,3 kg et la plage de puissance de 10W à 15W sont cohérents entre les données du graphe de connaissances et les annexes de masse.

### Divergences identifiées
#### Divergence 1 : Modèle installé et capacité RAM
Fichiers sources contradictoires :
- `SYNTHESE_Audio_IMU.md`
- `ETUDE_Hardware_Orin_vs_Thor.md`

Le document de synthèse confirme l'utilisation de la Jetson Orin Nano 8 Go, validée en conditions réelles. L'étude matérielle compare cette configuration à la Jetson AGX Orin (64 Go) et à la Jetson AGX Thor (128 Go), et discute d'une évolution vers des architectures plus lourdes.

**Question :** La carte mère installée est-elle bien la Jetson Orin Nano 8 Go (et non une AGX Orin 64 Go) ?

#### Divergence 2 : Puissance de calcul (TOPS)
Fichiers sources contradictoires :
- `SYNTHESE_Audio_IMU.md`
- `01_Synthese_Projet.md`
- `ETUDE_Hardware_Orin_vs_Thor.md`

Le document de synthèse et la synthèse du projet attribuent 67 TOPS à la Jetson Orin Nano Super. L'étude matérielle liste des puissances de 275 TOPS pour l'AGX Orin et 2070 TFLOPS pour l'AGX Thor, qui correspondent à des modèles différents.

**Question :** Le modèle exact est-il la "Jetson Orin Nano Super" (67 TOPS) ou la version standard ?

## 4. Divergences sur le matériel audio
Plusieurs incohérences sont identifiées sur l'architecture audio du D-Bot :

### Divergence 1 : Nombre de microphones et canaux audio
Fichiers sources contradictoires :
- `SYNTHESE_Audio_IMU.md`
- `test_audio.py`
- `test_arecord_vad.py`
- `test_audio_loop.py`

Le document de synthèse indique que le ReSpeaker XVF-3800 possède 4 micros MEMS. Le script `test_audio.py` initialise 6 canaux (4 micros + 2 canaux de référence/traités), `test_arecord_vad.py` utilise une configuration mono (1 canal) et `test_audio_loop.py` utilise une configuration stéréo (2 canaux).

**Question :** Le nombre de canaux audio actifs est-il de 1 (mono), 2 (stéréo) ou 6 (complet) ?

### Divergence 2 : Problème de "Micro Muet"
Fichiers sources contradictoires :
- `SYNTHESE_Audio_IMU.md`
- `ETUDE_Hardware_Orin_vs_Thor.md`
- Document de dépannage "Les Défis"

Le document de synthèse ne mentionne pas ce problème, tandis que les documents de dépannage décrivent un enregistrement de silence absolu par le ReSpeaker via `arecord` dû à un bug du port USB-C de la Jetson Orin Nano, dont la solution est de brancher le micro sur un port USB-A (bleu).

**Question :** Le ReSpeaker XVF-3800 est-il actuellement branché sur un port USB-A (bleu) ou USB-C de la Jetson ?

### Divergence 3 : Interface audio (ALSA vs PulseAudio)
Fichiers sources contradictoires :
- `SYNTHESE_Audio_IMU.md`
- `test_arecord_vad.py`
- `test_audio_loop.py`
- `test_audio.py`

Le document de synthèse indique une intégration native dans ROS2 via PulseAudio. Cependant, `test_arecord_vad.py` utilise ALSA via la commande `arecord`, `test_audio_loop.py` utilise PulseAudio via `parecord`, et `test_audio.py` utilise PyAudio (qui s'appuie par défaut sur ALSA sous Linux).

**Question :** L'architecture audio utilise-t-elle PulseAudio comme routeur principal (comme indiqué dans la synthèse) ou ALSA directement ?

### Divergence 4 : Activation de l'amplificateur JST
Fichiers sources contradictoires :
- Documentation système PulseAudio (graphe de connaissances)
- Script de configuration PulseAudio

Le graphe de connaissances indique que PulseAudio ne peut pas activer automatiquement les amplificateurs matériels, nécessitant une configuration explicite. Le script de configuration utilise cependant des commandes ALSA (`amixer`) pour activer l'amplificateur JST du ReSpeaker.

**Question :** L'amplificateur JST du ReSpeaker est-il activé via ALSA (amixer) ou via PulseAudio ?

### References

* [1] SYNTHESE_Audio_IMU.md
* [2] 07_Vision_IA.md
* [3] 51_Installation_OAK_D_DepthAI.md
* [4] ETUDE_Hardware_Orin_vs_Thor.md
* [5] test_audio.py

---

