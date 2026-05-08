# 🛡️ Rapport d'Intégrité de la Documentation D-Bot
> **Date de génération** : 2026-05-08 18:33:11
> **Modèle utilisé** : `openrouter` (tencent/hy3-preview:free)

Ce rapport est généré automatiquement via le système **Graph-RAG**.

## 1. Squelette (Masse & Moteurs)
Les données présentées ci-dessous sont extraites du Graphe de Connaissances (KG) et des fragments de documents du projet D-Bot, en distinguant la plateforme D-Bot (projet actuel) de K-Bot (plateforme prédécesseur open-source). Toutes les informations sont strictement limitées au contenu fourni dans le contexte.

### Tableau comparatif : Masse Totale et Nombre de Moteurs RobStride

| Source / Document | Robot | Masse Totale | Nombre total de Moteurs RobStride | Notes / Contexte |
| :--- | :--- | :--- | :--- | :--- |
| Graphe de Connaissances (Entité D-Bot) | D-Bot | 38-39 kg (cible), 39 kg, 39.4 kg, 40.2 kg (calcul Juin 2026, architecture 6-DOF) | 24 | Description générale du projet : 24 DOF, actionneurs QDD RobStride. |
| Graphe de Connaissances (Entité K-Bot) | K-Bot | ~20.37 kg ou ~34 kg | 10 ou 20 | Plateforme précédente : 20 DOF standard, 10 moteurs de jambe dans les phases initiales. |
| `annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md` | D-Bot | 38-39 kg (KG), 39 kg (`15_Analyse_Biomecanique.md`), ~39.4 kg (`Synthese_Torse_Cou.md`) | 24 (`01_Synthese_Projet.md`, `04_Electronique_Cablage.md`) | Rapport d'audit automatique identifiant les incohérences de documentation. |
| `annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md` | K-Bot | ~20.37 kg ou ~34 kg | 10 ou 20 | Données K-Bot extraites du KG pour comparaison avec D-Bot. |
| `01_Synthese_Projet.md` (version initiale) | D-Bot | Non spécifié | 24 (membres, cou) + 16 servomoteurs Dynamixel (mains D-Hand) | 24 moteurs RobStride pour les membres et le cou, 16 Dynamixel pour les mains. |
| `01_Synthese_Projet.md` (version 6-DOF) | D-Bot | 40.2 kg (calcul Juin 2026) | 26 (2 cou + 6 bras G + 6 bras D + 12 jambes) | Architecture 6-DOF par bras, masse révisée à 40.2 kg. |
| `04_Electronique_Cablage.md` | D-Bot | Non spécifié | 24 (2 cou + 5 bras G + 5 bras D + 12 jambes) | Décompte par bus CAN, total validé à 24 moteurs. |
| Document de benchmark industriel (sans nom de fichier explicite) | D-Bot | ~38 kg | 24 | Comparatif avec les robots haut de gamme, 24 DOF. |

---

### Contradictions identifiées

Toutes les contradictions ci-dessous concernent la plateforme D-Bot, sauf mention contraire pour K-Bot.

#### 1. Divergence sur la Masse Totale du D-Bot
Plusieurs valeurs sont rapportées selon les sources :
- ~38 kg (benchmark industriel, Entité D-Bot du KG)
- 39 kg (Entité D-Bot du KG, `15_Analyse_Biomecanique.md`)
- ~39.4 kg (`Synthese_Torse_Cou.md`, scénario B hybride)
- 40.2 kg (`01_Synthese_Projet.md` version 6-DOF, calcul Juin 2026)

**Question :** Quelle est la masse totale exacte cible pour la version finale du D-Bot : ~38 kg, 39 kg (arrondi/cible initiale), 39.4 kg (calcul précis du Scenario B) ou 40.2 kg (calcul Juin 2026 pour l'architecture 6-DOF) ?

#### 2. Divergence sur le Nombre Total de Moteurs RobStride du D-Bot
Deux comptages principaux sont en conflit :
- 24 moteurs (Entité D-Bot du KG, version initiale de `01_Synthese_Projet.md`, `04_Electronique_Cablage.md`, benchmark industriel) : décomposé en 2 (cou) + 5 (bras G) + 5 (bras D) + 12 (jambes)
- 26 moteurs (version 6-DOF de `01_Synthese_Projet.md`) : décomposé en 2 (cou) + 6 (bras G) + 6 (bras D) + 12 (jambes)

Cette divergence provient du nombre de moteurs par bras : 5 par bras dans les versions initiales, 6 par bras dans l'architecture 6-DOF.

**Question :** Le comptage final des moteurs RobStride est-il de 24 (5 moteurs par bras) ou 26 (6 moteurs par bras pour l'architecture 6-DOF) ? Confirmez-vous que les 16 servomoteurs Dynamixel des mains D-Hand ne sont pas inclus dans ce comptage ?

#### 3. Divergence sur le Nombre de Moteurs par Bras
- Versions initiales : 5 moteurs par bras (total 10 pour les deux bras)
- Version 6-DOF : 6 moteurs par bras (total 12 pour les deux bras)

**Question :** Le bras du D-Bot final utilise-t-il 5 ou 6 moteurs RobStride par bras (pour l'architecture 6-DOF) ?

#### 4. Confusion entre les Masses D-Bot et K-Bot
K-Bot (plateforme précédente) a une masse de ~20.37 kg ou ~34 kg, tandis que D-Bot a une masse de ~38-40.2 kg. Le rapport d'audit signale un risque de mélanger les deux plateformes.

**Question :** Confirmez-vous que la masse de ~39-40.2 kg s'applique exclusivement au D-Bot, et que les valeurs de ~20.37 kg ou ~34 kg correspondent uniquement à la plateforme K-Bot ?

#### 5. Incohérence résolue sur le Décompte de Moteurs des Jambes
Le rapport d'audit initial signalait une contradiction entre les 12 moteurs de jambes (`04_Electronique_Cablage.md`) et un calcul théorique de 14 moteurs (3 hanche F-A-R + 2 genou + 2 cheville par jambe). Les documents ultérieurs clarifient que le genou utilise 1 moteur par jambe (et non 2), soit 3 (hanche) + 1 (genou) + 2 (cheville) = 6 moteurs par jambe, 12 au total pour les deux jambes, ce qui résout l'incohérence.

**Question :** Le décompte de 12 moteurs pour les jambes (6 par jambe : 3 hanche F-A-R + 1 genou + 2 cheville Cardan) est-il le chiffre final validé ?

---

### References

- [1] annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md
- [2] 01_Synthese_Projet.md
- [3] 04_Electronique_Cablage.md
- [4] annexes/robstride/configuration_initiale/32_Configuration_ID_Limites_Cou.md
- [5] 5. Benchmark Industrie — D-Bot vs Robots Haut de Gamme

---

## 2. Cinématique (Moteurs par Axe)
# Vérification de la cohérence des modèles de moteurs par articulation

Nous avons analysé l'ensemble des données du Knowledge Graph et des Document Chunks pour valider la cohérence des modèles de moteurs RobStride associés à chaque articulation (Épaule, Coude, Poignet, Hanche, Genou, Cheville) dans la documentation du projet D-Bot. Plusieurs incohérences, chiffres divergents et références à d'anciens modèles ont été identifiés, avec des questions de validation associées pour chaque point.

## Épaule (Shoulder)
Les modèles d'épaule Roll (X) et Yaw (Z) sont cohérents dans l'ensemble de la documentation :
- **Épaule Roll (X)** : RS-03 (60 N.m de couple pic), confirmé par la documentation biomécanique initiale et la synthèse des moteurs totaux.
- **Épaule Yaw (Z)** : RS-02 (17 N.m de couple pic), cohérent sur toutes les sources. Une question de validation est nécessaire pour ce modèle, car son couple est nettement inférieur à celui du RS-03 utilisé pour le Roll.

Une incohérence majeure concerne l'**Épaule Pitch (Y)** :
- La documentation biomécanique initiale (15_Analyse_Biomecanique.md) liste le RS-03 (60 N.m) pour cet axe.
- La synthèse des moteurs totaux et l'entité Knowledge Graph RS-04 indiquent que le RS-04 (120 N.m) est le modèle utilisé pour l'Épaule Pitch.
- Un chiffre divergent de couple est associé : 60 N.m vs 120 N.m.

**Question :** Le modèle de moteur pour l'Épaule Pitch (Y) est-il le RS-03 (60 N.m, comme indiqué dans la documentation biomécanique initiale) ou le RS-04 (120 N.m, comme indiqué dans la synthèse des moteurs totaux et l'entité RS-04) ?
**Question :** Le choix du RS-02 pour l'Épaule Yaw (17 N.m) est-il validé malgré sa faible puissance par rapport au RS-03 utilisé pour le Roll, ou convient-il de passer au RS-03 pour plus de marge de sécurité ?

## Coude (Elbow)
Une incohérence directe est présente pour le **Coude Pitch (Y)** :
- La documentation biomécanique initiale liste le RS-02 (17 N.m) pour cet axe.
- La synthèse des moteurs totaux et la section Composition du Bras indiquent que le RS-06 (36 N.m) est le modèle retenu.
- Le couple associé diverge : 17 N.m vs 36 N.m.

**Question :** Le modèle de moteur pour le Coude Pitch (Y) est-il le RS-02 (17 N.m, documentation biomécanique initiale) ou le RS-06 (36 N.m, synthèse des moteurs totaux) ?

## Poignet (Wrist)
Les modèles de poignet sont cohérents dans l'ensemble de la documentation :
- **Poignet Roll (Z)** : RS-00 (14 N.m de couple pic), confirmé par toutes les sources.
- Les axes Poignet Pitch et Yaw ne sont pas implémentés dans la version V1, donc aucune incohérence n'est à signaler pour ces derniers.

## Hanche (Hip)
Tous les modèles de hanche sont cohérents et validés par plusieurs sources :
- **Hanche Pitch (Y)** : RS-04 (120 N.m de couple pic), utilisé pour la propulsion et le levage du fémur.
- **Hanche Roll (X) et Yaw (Z)** : RS-03 (60 N.m de couple pic), dédiés à la stabilité latérale et à la rotation.
Aucune référence à d'anciens modèles n'a été identifiée pour cette articulation.

## Genou (Knee)
Le modèle de genou est cohérent dans l'ensemble de la documentation :
- **Genou Pitch** : RS-04 (120 N.m de couple pic), identifié comme facteur limitant pour la course et nécessitant la solution de transmission GT3 (S6) en évolution V2.
Les alternatives (RS-02, RS-03, RS-06) sont listées pour des mises à niveau mais ne sont pas présentées comme des modèles actuels, donc aucune incohérence n'est à signaler.

## Cheville (Ankle)
L'architecture actuelle de la cheville est le système Cardan avec 2× RS-03 par articulation (120 N.m de couple total), mais des références à d'anciens modèles persistent :
- L'ancienne configuration avec RS-02/RS-00 est mentionnée dans plusieurs documents, bien qu'elle ait été remplacée par l'architecture Cardan.
- L'entité RS-04 indique par erreur que ce modèle est utilisé pour la cheville, ce qui est obsolète.

**Question :** Souhaitez-vous supprimer toutes les références aux anciennes configurations de cheville (RS-02/RS-00) et corriger les mentions de RS-04 pour l'articulation, sachant que l'architecture actuelle est strictement Cardan avec 2× RS-03 ?

## Autres chiffres divergents
Une incohérence de spécification poids est présente pour le moteur RS-04 :
- La majorité des sources indiquent un poids de 1420g.
- Certaines parties de la documentation listent un poids de 120.0g, ce qui est physiquement impossible pour un actionneur de 120 N.m.

**Question :** Le poids du moteur RS-04 doit-il être corrigé à 1420g partout pour supprimer l'incohérence avec la valeur de 120g présente dans certaines parties de la documentation ?

### References

- [1] Synthese_Etat_Actuel/SYNTHESE_Hanche.md
- [2] 15_Analyse_Biomecanique.md
- [3] 16_Conclusions_Architecture_DBot.md
- [4] 15d_Genou_et_Course.md
- [5] 15g_Solution_S6_Courroie_GT3_Genou.md

---

## 3. Électronique (Bus & Puissance)
# Vérification de cohérence : Alimentation et Bus CAN

Cette analyse compare la cohérence des informations entre les documents de synthèse (y compris le rapport de vérification de cohérence, les conclusions d'architecture finales) et le guide électronique (Doc 04 : *04_Electronique_Cablage.md*) pour deux domaines clés : l'alimentation (tension batterie) et le bus CAN (nombre de moteurs par bus).

## 1. Alimentation (Tension Batterie)

### Points de cohérence identifiés
Les documents sont globalement cohérents sur les tensions de base. Le guide électronique Doc 04 précise que le processeur principal (NVIDIA Jetson Orin Nano) est alimenté en **19V DC**, tandis que tous les moteurs Robstride sont alimentés en **24V** via le bus CAN, avec un câblage en parallèle sur une alimentation de laboratoire dédiée (Wanptek DPS605U). Cette configuration est validée par les guides de test : le document Doc 33 (*33_Test_Multi_Moteurs_CAN_Banc.md*) confirme une tension de 24V pour les deux moteurs RS-05 du cou, avec une limite de courant de 3.0A pour l'ensemble.

Le rapport de synthèse de cohérence note qu'aucune incohérence majeure n'existe sur la tension de base, l'architecture séparée (19V Jetson / 24V moteurs) étant logique si les deux composants sont alimentés par des sources distinctes ou via un régulateur dédié.

### Incohérences et chiffres divergents
Une divergence notable apparaît entre le guide électronique et le graphe de connaissances D-Bot : ce dernier mentionne une alimentation globale de **48V** pour les 24 actionneurs QDD Robstride, contre 24V dans Doc 04. Par ailleurs, une nuance non validée subsiste : il n'est pas précisé si le système final utilisera une batterie unique de 24V avec régulateur pour la Jetson, ou maintiendra des alimentations séparées.

#### Questions de validation
- Question : Le système final de D-Bot utilise-t-il une alimentation 19V pour la Jetson et 24V pour les moteurs (comme indiqué dans le guide électronique Doc 04), ou prévoyez-vous d'utiliser l'alimentation 48V mentionnée dans le graphe de connaissances, avec régulation en aval pour les composants ?
- Question : Souhaitez-vous alimenter l'ensemble du système (Jetson incluse) depuis une batterie unique de 24V via un régulateur, ou maintenir des sources d'alimentation séparées (19V pour la Jetson, 24V dédiés aux moteurs) ?

## 2. Bus CAN (Nombre de moteurs par bus)

### Points de cohérence identifiés
Le guide électronique Doc 04 établit une règle de capacité théorique de **5 à 6 moteurs par bus CAN** à 1 Mbps, calculée sur la base de trames de 130 bits par moteur, une boucle de contrôle à 1 kHz, et une marge pour les acquittements. Cette règle est cohérente avec les tests du document Doc 33, qui valide le fonctionnement simultané de 2 moteurs RS-05 (Pan + Tilt) sur le Bus 1 (cou) à 1 Mbps.

Les conclusions d'architecture finales (*16_Conclusions_Architecture_DBot.md*) confirment le décompte total de 24 moteurs Robstride, ce qui correspond aux spécifications du graphe de connaissances D-Bot.

### Incohérences et chiffres divergents
Plusieurs contradictions techniques apparaissent entre la théorie du guide électronique et la réalité physique des moteurs :

1. **Topologie de câblage** : Doc 04 impose une topologie en chaîne (daisy-chain) pour tous les moteurs d'un bus, avec une résistance de terminaison de 120 Ω sur le dernier moteur. Or, les documents Doc 33 et Doc 42 (*42_Configuration_CAN_InnoMaker_RS05.md*) confirment que les moteurs RS-05 du cou ne disposent que d'un seul port CAN, rendant la chaîne daisy-chain impossible. La topologie obligatoire est donc une étoile (star) via un splitter CAN, ce qui contredit directement la règle de Doc 04.
2. **Résistances de terminaison** : Doc 04 exige une résistance de 120 Ω sur le dernier moteur de chaque bus. Doc 42 valide que pour les câbles courts (< 30 cm, cas du cou), ces résistances sont inutiles, contredisant la règle universelle de Doc 04.
3. **Applicabilité du quota de moteurs** : La règle des 5-6 moteurs par bus s'applique aux moteurs en daisy-chain. Il n'est pas précisé si les moteurs RS-05 (en étoile) comptent dans ce quota, ou s'ils utilisent un bus dédié (Bus 1) indépendant de la chaîne principale des membres.
4. **Répartition des bus** : La version initiale de Doc 04 mentionne un "Bus Bras G" (bras gauche) avec 5 moteurs, mais une version ultérieure remplace les bus des bras par des "Bus Jambe G" et "Bus Jambe D" (jambes gauche et droite) avec 6 moteurs chacun, sans mention des bus pour les membres supérieurs.
5. **Bus centralisé vs bus dédiés** : Le graphe de connaissances D-Bot mentionne une "communication centralisée par bus CAN 2.0B", mais les documents Doc 33 et Doc 42 confirment que le cou utilise un bus dédié (Bus 1) en étoile, séparé du bus principal des membres.

#### Questions de validation
- Question : Le bus CAN centralisé décrit dans la Doc 04 (5-6 moteurs en série) doit-il inclure les moteurs du cou (RS-05), ou le cou dispose-t-il d'un bus CAN dédié (Bus 1) indépendant de la chaîne principale des membres ?
- Question : Souhaitez-vous appliquer la règle de terminaison de 120 Ω (Doc 04) à l'ensemble du robot, ou acceptez-vous l'exception validée pour les câbles courts (< 30 cm) où les terminaisons sont omises (Doc 42) ?
- Question : Pour la documentation finale, souhaitez-vous modifier le schéma global (Doc 04) pour préciser que les RS-05 utilisent une topologie en étoile (splitter CAN) au lieu de la chaîne daisy-chain, en raison de leur port CAN unique ?
- Question : Les moteurs des bras (épaules, coudes, poignets) sont-ils répartis sur les bus des jambes (Bus Jambe G/D) comme indiqué dans la version mise à jour de la Doc 04, ou disposent-ils de bus dédiés avec un quota de 5-6 moteurs par bus ?
- Question : La mention d'un bus CAN centralisé dans le graphe de connaissances D-Bot correspond-elle à une architecture logique, malgré l'utilisation physique d'un bus dédié (Bus 1) en topologie étoile pour le cou ?

### References

- [1] 04_Electronique_Cablage.md
- [2] 33_Test_Multi_Moteurs_CAN_Banc.md
- [3] 42_Configuration_CAN_InnoMaker_RS05.md
- [4] 16_Conclusions_Architecture_DBot.md
- [5] Synthèse de Vérification de Cohérence (Syntheses, Guide Électronique et Guides de Test)

---

## 4. Perception & IA
# Vérification de la cohérence des spécifications matérielles

## 1. Caméra OAK-D Pro
Les spécifications de la caméra OAK-D Pro ne sont pas totalement identiques d'un document à l'autre. La majorité des sources (`SYNTHESE_Audio_IMU.md`, `07_Vision_IA.md`) confirment l'utilisation de la version **Fixed Focus (FF)**, avec un poids de 91g, une portée de profondeur de 70cm à 12m, un capteur RGB de 12 MP et une IMU BNO085 intégrée de 9 axes. Le document `07_Vision_IA.md` mentionne également l'OAK-D SR comme alternative non retenue (portée 30cm-1m, 60g), sans impact sur la configuration finale.

Une divergence majeure subsiste concernant l'IMU BNO085 : la synthèse système indique que ce composant est un capteur distinct situé dans la tête du robot pour la stabilisation du regard, tandis que les spécifications officielles de l'OAK-D Pro confirment son intégration native dans la caméra.

Question : L'IMU BNO085 mentionnée pour la stabilisation du regard dans la tête est-elle celle intégrée à l'OAK-D Pro, ou s'agit-il d'un capteur IMU supplémentaire ajouté spécifiquement pour la stabilisation ?

## 2. Jetson Orin Nano
Les spécifications de la Jetson Orin Nano présentent plusieurs divergences. Le modèle validé et acheté est la version **8 Go**, pesant 0,3 kg, avec une consommation de 10W à 15W, selon `ETUDE_Hardware_Orin_vs_Thor.md`. Cependant, `SYNTHESE_Audio_IMU.md` attribue 67 TOPS à la "Jetson Orin Nano Super", une valeur correspondant au mode performance de la version 8 Go, mais le document d'étude matériel ne mentionne pas explicitement la variante "Super". Par ailleurs, l'étude matériel compare la configuration actuelle à la Jetson AGX Orin (64 Go, 275 TOPS) et la Jetson AGX Thor (128 Go, 2070 TFLOPS), des modèles haut de gamme non utilisés dans l'architecture actuelle du D-Bot.

Question : La carte mère installée est-elle bien la Jetson Orin Nano 8 Go (et non une AGX Orin 64 Go) ?
Question : Le modèle exact est-il la "Jetson Orin Nano Super" (67 TOPS) ou la version standard 8 Go ?

## 3. IMU Principale (BNO085 pour la stabilisation du regard)
Comme mentionné précédemment, l'IMU BNO085 fait l'objet d'une contradiction directe entre les documents : elle est soit intégrée à l'OAK-D Pro, soit un capteur externe distinct. Aucune autre divergence n'est identifiée sur les autres IMU du système (BMI270 pour l'équilibre du torse, LiDAR Unitree L2 pour l'odométrie).

## 4. Divergences sur le matériel audio
Le domaine audio présente le plus grand nombre d'incohérences, liées au module ReSpeaker XVF-3800, aux interfaces logicielles et aux configurations de canaux.

### 4.1 Nombre de microphones et canaux audio
Les informations sur le ReSpeaker XVF-3800 sont contradictoires :
- Les entités Knowledge Graph et `SYNTHESE_Audio_IMU.md` indiquent que le module dispose de 4 micros MEMS, tandis qu'une autre entité Knowledge Graph attribue 6 microphones à la gamme Respeaker générale.
- Le script `test_audio.py` initialise 6 canaux (4 micros + 2 canaux de référence/traités) et détecte dynamiquement le nombre de canaux réels via `maxInputChannels`.
- Le script `test_arecord_vad.py` utilise une configuration mono (1 canal) via l'interface ALSA.
- Le script `test_audio_loop.py` utilise une configuration stéréo (2 canaux) via PulseAudio.

Question : Le ReSpeaker XVF-3800 est-il configuré avec 4 micros MEMS (canaux 6 incluant les références) ou 6 micros au total ?
Question : Le nombre de canaux audio actifs est-il de 1 (mono), 2 (stéréo) ou 6 (complet) ?

### 4.2 Problème de "Micro Muet" (enregistrement silencieux)
Les documents de dépannage liés à la Jetson Orin notent que le ReSpeaker enregistre un silence absolu sous Linux via `arecord` en raison d'un bug du port USB-C de la Jetson, la solution étant de brancher le module sur un port USB-A (bleu). `SYNTHESE_Audio_IMU.md` ne mentionne pas ce problème, et aucune information ne confirme le type de port utilisé actuellement.

Question : Le ReSpeaker XVF-3800 est-il actuellement branché sur un port USB-A (bleu) ou USB-C de la Jetson ?

### 4.3 Interface audio (ALSA vs PulseAudio)
- `SYNTHESE_Audio_IMU.md` indique une intégration native dans ROS2 via PulseAudio.
- Plusieurs scripts de test utilisent directement l'interface ALSA (`arecord`, `plughw:X,0`) ou mélangent les deux approches : `test_audio_loop.py` utilise PulseAudio pour la détection des périphériques et l'enregistrement (`parecord`), mais configure l'amplificateur JST via ALSA (`amixer`).

Question : L'architecture audio utilise-t-elle PulseAudio comme routeur principal (comme indiqué dans la synthèse) ou ALSA directement ?

### References

---

