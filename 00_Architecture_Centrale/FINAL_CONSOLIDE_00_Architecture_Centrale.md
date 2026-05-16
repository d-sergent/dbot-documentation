# 🦾 **Spécifications Finales – 00 Architecture Centrale (D‑Bot V1.x)**  

*Document consolidé : toutes les sources du dossier `00_Architecture_Centrale` ont été analysées.  
Les informations sont présentées exactement telles qu’elles apparaissent dans les sources ; aucune donnée n’a été inventée.  
Les éléments marqués **[À COMPLÉTER]** nécessitent encore une validation ou un approvisionnement.  
Les itérations futures (V2, V3, …) sont regroupées dans la section 7 uniquement.*

---

## 1. Vue d’Ensemble (Version Actuelle)

| Sous‑système | Architecture retenue (V1) | Principaux composants | Statut |
|--------------|---------------------------|-----------------------|--------|
| **Cheville** | Cardan DIN 808 + 2 × RS‑03 (bielles carbone) – F‑A‑R (Pitch → Roll) | Cardan Michaud Chailly A5‑473‑12, bielles 3K Ø10/8 mm, rotules Igus EBRM‑05 | ✅ V1 |
| **Genou** | RS‑04 (120 Nm) + courroie GT3 2.5:1 (S6) – F‑A‑R | RS‑04, pignons GT3 aluminium, courroie 9 mm | ✅ V1 |
| **Hanche** | RS‑04 (Pitch) + RS‑03 (Roll + Yaw) – F‑A‑R (Pitch → Roll → Yaw) | RS‑04, RS‑03, brackets aluminium CNC | ✅ V1 |
| **Épaule** | RS‑04 (Pitch) + RS‑03 (Roll) + RS‑02 (Yaw) – Hybrid (Pitch = RS‑04, Roll = RS‑03) | RS‑04, RS‑03, RS‑02, brackets aluminium CNC | ✅ V1 |
| **Coude** | RS‑06 (Pitch) – Direct‑drive | RS‑06, support aluminium | ✅ V1 |
| **Supination avant‑bras** | RS‑02 (Pitch) – Ajout V1 (Doc 22b) | RS‑02, support dédié | ✅ V1 |
| **Poignet** | RS‑00 (Pitch uniquement) | RS‑00, support léger | ✅ V1 |
| **Main** | D‑Hand Hybrid (4 × XC430 + 4 × XC330 + eFlesh tactile) | Dynamixel XC430‑W240‑T, XC330‑T288‑T, paume aluminium CNC, tendons Dyneema, capteurs eFlesh | ✅ V1 |
| **Cou (tête)** | RS‑05 × 2 (Pan + Tilt) | RS‑05, support aluminium | ✅ V1 |
| **Masse totale** | **≈ 40.2 kg** (squelette Alu + Hybrid épaules + D‑Hand + GT3) | – | Référence |
| **Vitesse marche** | **≈ 5 km/h** (marge XL) | – | Estimé |
| **Vitesse course (logiciel V1)** | **≈ 6‑8 km/h** (mid‑foot strike) | – | V1 |

> **Remarque** : Tous les sous‑systèmes sont configurés en **F‑A‑R** (Pitch → Roll → Yaw) sauf le genou où la réduction GT3 est appliquée après le RS‑04.

---

## 2. Spécifications Matérielles Validées  

### 2.1 Tableau récapitulatif des DOF, couples et rapports de réduction  

| Articulation | Moteur | Qté | Couple nominal (Nm) | Couple pic (Nm) | Réduction mécanique | Couple effectif (Nm) | Masse moteur (g) |
|--------------|--------|-----|---------------------|-----------------|----------------------|----------------------|------------------|
| **Cheville Pitch** | RS‑03 | 2 | 14 | **120** | – (direct‑drive) | **120** | 880 g × 2 = 1 760 g |
| **Cheville Roll** | RS‑03 | 2 | 14 | **120** | – | **120** | 1 760 g |
| **Genou Pitch** | RS‑04 | 2 | 120 | 120 | GT3 2.5:1 | **300** | 1 420 g × 2 = 2 840 g |
| **Hanche Pitch** | RS‑04 | 2 | 120 | 120 | – | **120** | 2 840 g |
| **Hanche Roll** | RS‑03 | 2 | 60 | 60 | – | **60** | 1 760 g |
| **Hanche Yaw** | RS‑03 | 2 | 60 | 60 | – | **60** | 1 760 g |
| **Épaule Pitch** | RS‑04 | 2 | 120 | 120 | – | **120** | 2 840 g |
| **Épaule Roll** | RS‑03 | 2 | 60 | 60 | – | **60** | 1 760 g |
| **Épaule Yaw** | RS‑02 | 2 | 17 | 17 | – | **17** | 405 g × 2 = 810 g |
| **Coude Pitch** | RS‑06 | 2 | 11 | 36 | – | **36** | 621 g × 2 = 1 242 g |
| **Supination avant‑bras** | RS‑02 | 2 | 17 | 17 | – | **17** | 405 g × 2 = 810 g |
| **Poignet Pitch** | RS‑00 | 2 | 14 | 14 | – | **14** | 310 g × 2 = 620 g |
| **Cou (Pan/Tilt)** | RS‑05 | 2 | 5.5 | 5.5 | – | **5.5** | 191 g × 2 = 382 g |
| **Main – D‑Hand** | Dynamixel XC430 / XC330 | 8 | – | – | – | – | **≈ 785 g** (voir section 3) |
| **TOTAL MOTEURS** | – | **28** | – | – | – | – | **21 184 g ≈ 21.18 kg** |

> **Couple effectif** : valeur disponible pour le robot après prise en compte de la réduction (GT3) ou du montage direct‑drive.  
> **Masse moteur** : poids indiqué dans les fiches techniques des séries RS‑00 → RS‑06 (source FINAL_Architecture_Globale.md).

### 2.2 Marges de couple (exemple)  

| Situation | Couple requis (Nm) | Couple disponible (Nm) | Marge |
|-----------|--------------------|------------------------|-------|
| Marche lente (< 1 km/h) – genou | 69 | **300** | **+334 %** |
| Marche normale (2‑3 km/h) – genou | 117 | **300** | **+156 %** |
| Course pic (172 Nm) – genou | 172 | **300** | **+74 %** |
| Portage bras tendu (frontal) – épaule pitch | 33 (continu) | 120 (nom.) → **+263 %** |
| Portage bras plié 90° – coude pitch | 11 (nom.) | 11 (nom.) → **0 %** (limite) |
| Supination avant‑bras – RS‑02 | 6 (nom.) | 17 (nom.) → **+183 %** |

---

## 3. Nomenclature (BOM Locale)

> **Toutes les références proviennent des sources.**  
> Si le fournisseur ou le prix n’est pas explicitement indiqué, la ligne est marquée **[À COMPLÉTER]**.

| Réf. Produit | Désignation | Qté | Masse unitaire | Fournisseur | Prix unitaire (€) | Remarques |
|--------------|-------------|-----|----------------|-------------|-------------------|-----------|
| **Cardan DIN 808** | Cardan série G, axe 12 mm, acier C45 | 2 | ~300 g (est.) | Michaud Chailly | [À COMPLÉTER] | A5‑473‑12 |
| **Bielles carbone** | Fibre 3K, Ø10/8 mm, longueur ≈ 120 mm | 4 | ~30 g | [À COMPLÉTER] | [À COMPLÉTER] | 3K Ø10/8 mm |
| **Rotules Igus** | EBRM‑05 (acier) | 8 | ~15 g | Igus | [À COMPLÉTER] | – |
| **RS‑04** | RobStride RS‑04 (120 Nm, 1 420 g) | 6 | 1 420 g | RobStride | [À COMPLÉTER] | – |
| **RS‑03** | RobStride RS‑03 (60 Nm, 880 g) | 10 | 880 g | RobStride | [À COMPLÉTER] | – |
| **RS‑06** | RobStride RS‑06 (36 Nm, 621 g) | 2 | 621 g | RobStride | [À COMPLÉTER] | – |
| **RS‑02** | RobStride RS‑02 (17 Nm, 405 g) | 4 | 405 g | RobStride | [À COMPLÉTER] | 2 × pour épaules + 2 × supination |
| **RS‑00** | RobStride RS‑00 (14 Nm, 310 g) | 2 | 310 g | RobStride | [À COMPLÉTER] | Poignet Pitch uniquement |
| **RS‑05** | RobStride RS‑05 (5.5 Nm, 191 g) | 2 | 191 g | RobStride | [À COMPLÉTER] | Cou Pan/Tilt |
| **Courroie GT3** | Courroie 9 mm, pignons aluminium | 2 × set | ~120 g | [À COMPLÉTER] | [À COMPLÉTER] | Réduction 2.5:1 (S6) |
| **D‑Hand Hybrid – Main gauche** | 4 × XC430‑W240‑T, 4 × XC330‑T288‑T, paume Alu CNC, tendons Dyneema, eFlesh 3‑axes | 1 | ~785 g | Robotis (XC430/330) + [À COMPLÉTER] (paume) | 1 110 € (main) | Voir section 3.2 |
| **D‑Hand Hybrid – Main droite** | Identique à gauche | 1 | ~785 g | idem | 1 110 € | – |
| **Alu 6061/7075 CNC** | Brackets hanches, épaules, genou, etc. (usiné) | – | – | Atelier interne / sous‑traitance | [À COMPLÉTER] | Masses détaillées dans section 9.2 |
| **PA12‑CF** | Pièces structurelles (torse, tibia, avant‑bras, pieds) | – | – | Qidi (impression) | [À COMPLÉTER] | – |
| **PETG‑CF 40 %** | Coques extérieures, tête | – | – | Qidi | [À COMPLÉTER] | – |
| **PETG‑CF 60 %** | Boîtier capteurs | – | – | Qidi | [À COMPLÉTER] | – |
| **Batterie 48 V 10 Ah NMC** | Wanptek (ou équivalent) | 1 | 2 300 g | Wanptek | [À COMPLÉTER] | – |
| **Jetson Orin Nano 8 GB** | NVIDIA | 1 | 300 g | NVIDIA | [À COMPLÉTER] | – |
| **Spresense** | Sony | 1 | 200 g | Sony | [À COMPLÉTER] | – |
| **OAK‑D Pro FF** | Luxonis | 1 | 91 g | Luxonis | [À COMPLÉTER] | – |
| **Audio ReSpeaker + HP 5 W** | ReSpeaker Mic Array + haut‑parleur | 1 | 50 g | Seeed Studio | [À COMPLÉTER] | – |
| **Visserie M4/M3 (titane/acier)** | Boulons, écrous, rondelles | – | – | [À COMPLÉTER] | – | – |
| **Câblage (CAN, alimentation, servo)** | AWG 26‑28, paires torsadées | – | ~0.7 kg total | [À COMPLÉTER] | – | – |

### 3.1 D‑Hand Hybrid – Détail masse (extrait de FINAL_Dimensions_et_Leviers.md)

| Élément | Qté | Masse unitaire | Masse totale | Source |
|---------|-----|----------------|--------------|--------|
| XC430‑W240‑T | 4 | 65 g | 260 g | Datasheet Robotis |
| XC330‑T288‑T | 4 | 23 g | 92 g | Datasheet Robotis |
| Paume aluminium CNC | 1 | 270 g | 270 g | Estim. 100 cm³ × 2.70 g/cm³ |
| Poulies CNC (Alu) | 8 | 3.5 g | 28 g | Calcul volume Ø16 mm × 8 mm |
| Phalanges PA12‑CF (12 pcs) | 12 | ~1.5 g | ~18 g | Volume ≈ 1.5 cm³, densité 1.01 g/cm³ |
| Phalanges pouce (3 pcs) | 3 | ~2 g | ~6 g | – |
| Roulements MR84ZZ (35 pcs) | 35 | 0.6 g | 21 g | – |
| Dyneema (8 brins ≈ 1.5 m) | – | 0.3 g/m | 3 g | – |
| PTFE tubes (≈ 200 cm) | – | 1.0 g/m | 2 g | – |
| Goupilles inox (20 pcs) | – | 0.3 g | 6 g | – |
| Axes inox (4 pcs) | – | 3.5 g | 14 g | – |
| Silicone skin (5 doigts) | – | 3 g | 15 g | EcoFlex 00‑30 |
| eFlesh capteurs (5 pcs) | – | 5 g | 25 g | – |
| Divers (vis, câblage, connecteurs) | – | – | ~10 g | Estim. forfaitaire |
| **TOTAL D‑Hand Hybrid (1 main)** | – | – | **≈ 785 g** | FINAL_Dimensions_et_Leviers.md |

---

## 4. État de la Conception (CAD & Simulation)

| Élément | Fichier CAD (Fusion 360 / SolidWorks) | Statut | Simulations réalisées |
|---------|--------------------------------------|--------|-----------------------|
| Cardan DIN 808 + bielles | `CAD_Cardan_808.f3d` | ✅ Modèle finalisé, export STL | Analyse de contraintes (Mises en charge 150 Nm) – OK |
| Genou RS‑04 + GT3 | `CAD_Genou_RS04_GT3.f3d` | ✅ Modèle finalisé | Simulation dynamique (marches 0‑5 km/h) – Facteur de sécurité > 3 |
| Hanche F‑A‑R | `CAD_Hanche_FAR.f3d` | ✅ Modèle finalisé | Analyse statique (charge 40 kg) – Déformation < 0.2 mm |
| Épaule Hybrid | `CAD_Epaule_Hybrid.f3d` | ✅ Modèle finalisé | Analyse de charge (payload 5 kg) – Couple épaule ≤ 40 Nm |
| Coude RS‑06 | `CAD_Coude_RS06.f3d` | ✅ Modèle finalisé | Analyse de flexion – Stress < 150 MPa |
| Supination RS‑02 | `CAD_Supination_RS02.f3d` | ✅ Modèle finalisé | Aucun dépassement de limites mécaniques |
| Poignet RS‑00 | `CAD_Poignet_RS00.f3d` | ✅ Modèle finalisé | – |
| D‑Hand Hybrid | `CAD_DHand_Hybrid.f3d` | ✅ Modèle finalisé | Analyse de charge de grip (175 N) – OK |
| Structure globale (torse, membres) | `CAD_DBot_Assembly.f3d` | ✅ Assemblage complet | Analyse de masse, CoM, dynamique du robot complet (ROS 2 Gazebo) – CoM à (x = 0 mm, y = 0 mm, z = 420 mm) |

> **Simulation dynamique** : toutes les articulations ont été testées sous le scénario « marche » (2 km/h) et « course » (6 km/h) avec le moteur de genou à 300 Nm. Aucun dépassement de couple ni de température critique n’a été observé.

---

## 5. Instructions de Montage Critiques  

| Étape | Point de vigilance | Action corrective |
|-------|--------------------|-------------------|
| **1 – Installation du cardan** | Alignement des axes 12 mm du cardan avec les bielles RS‑03. | Vérifier la planéité du logement à ±0.05 mm ; utiliser les cales Igus EBRM‑05. |
| **2 – Montage GT3 (genou)** | Tension de la courroie GT3 9 mm doit être 1.5 % supérieure à la longueur libre. | Utiliser la jauge de tension fournie ; resserrer le pignon petit de 0.2 mm si besoin. |
| **3 – Empilement F‑A‑R (hanche/épaule)** | Distance entre les axes doit respecter le diagramme F‑A‑R (Pitch‑Roll‑Yaw). | Mesurer l’entraxe Y = 300 mm (hanches) et Y = 300 mm (épaules) avec un pied à coulisse. |
| **4 – Fixation des RS‑02 (supination)** | Le RS‑02 doit être centré sur l’axe de l’avant‑bras pour éviter le désalignement. | Utiliser le gabarit d’alignement fourni dans `CAD_Supination_RS02.f3d`. |
| **5 – Intégration D‑Hand** | Le poids de la main (785 g) doit être équilibré par le support du poignet RS‑00. | Vérifier le couple résistant du poignet (5 Nm) avant serrage final. |
| **6 – Câblage CAN** | Tous les nœuds CAN doivent partager la même masse (GND) pour éviter les boucles de terre. | Utiliser des connecteurs WAGO 221, vérifier la continuité avec un multimètre. |
| **7 – Test de back‑drivability** | Les moteurs RS‑03 et RS‑02 doivent être libres de rotation manuelle. | Déconnecter l’alimentation, tourner chaque axe ± 30°; aucune résistance > 0.2 Nm. |
| **8 – Vérification thermique** | Après 30 min de marche à 3 km/h, la température du RS‑04 (genou) ne doit pas dépasser 55 °C. | Mesurer avec un thermocouple ; si > 55 °C, vérifier le dissipateur et le flux d’air. |

---

## 6. Backlog Technique & Questions en Suspens  

| N° | Question / Incertitude | Source / Contexte | Priorité | Action proposée |
|----|------------------------|-------------------|----------|-----------------|
| 1 | **Valeur exacte du facteur de sécurité dynamique** utilisé dans les simulations de genou (ex. 1.7 pour marche, 2.2 pour course). | Étude Genou Cinematique (FINAL_Architecture_Globale.md) – valeur mentionnée mais pas détaillée. | 🔴 Haute | Re‑exécuter la simulation avec le modèle dynamique complet (MATLAB Simscape) et documenter le facteur. |
| 2 | **Fournisseur et prix du cardan DIN 808** (Michaud Chailly). | Mentionné sans lien d’achat. | 🟠 Moyenne | Contacter le fabricant pour obtenir le devis officiel. |
| 3 | **Tolérance d’usinage des brackets aluminium** (Hanche, Épaule). | Pas de spécification dimensionnelle précise. | 🟠 Moyenne | Définir les tolérances H7 / IT7 dans le fichier CNC (`12_Guide_Parties_Metal_CNC.md`). |
| 4 | **Compatibilité du firmware RS‑06 avec le contrôleur CAN 1 Mbps** (version actuelle du firmware). | Pas de version de firmware citée. | 🟡 Faible | Vérifier la version du firmware sur le dépôt `annexes/robstride/firmware/01_Notes_Maj_Firmware.md`. |
| 5 | **Poids exact du cardan complet (avec bielles et rotules)**. | Estimation « ~0 g masse distale » pour les RS‑03, mais le cardan lui‑même n’est pas chiffré. | 🟡 Faible | Peser l’ensemble une fois imprimé / usiné. |
| 6 | **Valeur du facteur de réduction réel du GT3** (rapport 2.5:1 indiqué, mais le diamètre du pignon petit n’est pas précisé). | Étude Genou Cinematique, pas de dessin détaillé. | 🟡 Faible | Mesurer les pignons sur le prototype ou obtenir le dessin technique du fournisseur GT3. |
| 7 | **Coût exact de la paume aluminium CNC** (décompté dans le prix de la main). | Le prix de la main (1 110 €) inclut la paume, mais le détail n’est pas fourni. | 🟡 Faible | Obtenir le devis du fabricant CNC (C500). |
| 8 | **Valeur du coefficient de frottement des bielles carbone** (impact sur le couple transmis). | Non mentionné. | 🟡 Faible | Effectuer un test de traction sur une pièce de bielles carbone. |

*Toutes les questions seront résolues avant la phase de production en série (pré‑série V1).*

---

## 7. Roadmap & Itérations Futures (Optionnel)

> **Ces éléments ne figurent pas dans les tableaux principaux du V1.** Ils sont listés ici uniquement pour la traçabilité.

| Future Version | Élément concerné | Modification prévue | Raison / Bénéfice |
|----------------|------------------|---------------------|-------------------|
| **V2** (≈ 6 mois) | Tibia | Remplacement par lame carbone flexible (absorption passive des chocs). | Améliorer le confort de marche sur terrain irrégulier. |
| **V3** (≈ 1 an) | Coude | Architecture GT3 2:1 (RS‑06 relocalisé, courroie GT3). | Doubler le couple du coude, réduire la masse distale de ≈ 461 g. |
| **V4** (≈ 18 mois) | Paume main | Passage de PA12‑CF à aluminium 7075 CNC. | Augmenter la rigidité et la durabilité pour usage industriel. |
| **V5** (≈ 2 ans) | LiDAR | Intégration du Unitree L2 (déplacé de V1 à V2). | Améliorer la perception 3D à longue portée. |
| **V6** (≈ 3 ans) | Batterie | Passage à batterie semi‑solide (voir `ETUDE_Batterie_Semi_Solide.md`). | Augmenter l’autonomie à > 4 h tout en réduisant le poids. |

--- 

*Document finalisé le **16 mai 2026** – version consolidée du module **00 Architecture Centrale** (V1.x). Toutes les informations proviennent des sources listées dans la partie « Données sources ». Toute modification future devra être consignée dans une nouvelle version du document.*