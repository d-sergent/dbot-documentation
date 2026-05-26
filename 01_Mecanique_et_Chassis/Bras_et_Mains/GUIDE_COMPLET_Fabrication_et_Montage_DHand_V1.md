# 📘 MANUEL TECHNIQUE COMPLET — Fabrication & Montage de la D-Hand V1 Révisée (8 DOF)

> **Projet :** D-Bot Humanoid (40 kg)  
> **Module :** Bras et Mains — Main D-Hand V1 Révisée  
> **Auteur :** Antigravity AI  
> **Date de publication :** 2026-05-25  
> **Statut :** Document technique de fabrication consolidé et prêt pour exécution  

---

## 🎯 Introduction & Objectifs de ce Guide

Ce manuel rassemble et unifie l'intégralité des instructions, méthodes, tolérances et références nécessaires pour fabriquer et assembler la main robotique **D-Hand V1 Révisée**. 

Basée sur une architecture hybride haut de gamme à **8 Degrés de Liberté (8 DOF)** sous-actionnée, cette conception combine le meilleur de l'ingénierie mécanique : de la puissance brute via des servomoteurs **Feetech STS3250** (50 kg.cm), de la précision fine grâce aux servos **Feetech HL-3915** avec mode force constante, un squelette ultra-robuste en **PA12-CF** (Nylon Carbone) et une paume en **Aluminium 6061-T6** usinée CNC.

Ce guide est conçu pour vous accompagner pas-à-pas de l'achat des matières premières à la calibration logicielle finale sur votre banc d'essai.

---

## 📦 1. Nomenclature Globale (BOM Complète & Validée)

Voici la liste exacte des composants, fixations et matières premières nécessaires pour assembler **une main complète (D-Hand V1)**.

### 1.1 Motorisation & Électronique (Dans l'Avant-Bras)
| Désignation | Référence / Spécifications | Qté | Rôle mécanique |
| :--- | :--- | :---: | :--- |
| **Servomoteur de Force** | **Feetech STS3250** (12V, 50 kg.cm stall, coreless, boîtier alu CNC, pignons acier, TTL) | **5** | Actionnement en flexion/serrage des 5 doigts. |
| **Servomoteur de Précision** | **Feetech HL-3915** (12V, 14.2 kg.cm stall, coreless, boîtier alu CNC, mode force matérielle, TTL) | **3** | Opposition du pouce, abduction index, curl palmaire. |
| **Convertisseur Buck** | **Pololu D24V150F12** (Entrée 48V / Sortie 12V synchrone, 15A continu / 20A pic, efficacité 95%) | **1** | Alimentation stable du bus de servomoteurs 12V. |
| **Plaque de Dissipation** | **Gap Pad Bergquist 5000S35** (Épaisseur 0.5 mm) | **1** | Couplage thermique entre le convertisseur et le tube carbone/alu. |

### 1.2 Structure & Quincaillerie Mécanique
| Désignation | Référence / Spécifications | Qté | Emplacement |
| :--- | :--- | :---: | :--- |
| **Micro-roulements** | **MR84ZZ** (Acier, étanche double flasque, 4 × 8 × 3 mm) | **35** | Pivots des phalanges et roulettes de paume. |
| **Roulements Moyen** | **6x13x5 mm** (double flasque étanche) | **2** | Pivot de la base du pouce. |
| **Axes Cylindriques** | Goupilles cylindriques en acier rectifié **2 × 6 mm** | **20** | Verrouillage des chapes de phalanges (MCP/PIP/DIP). |
| **Axes Longs** | Axes en Inox rectifié **3 × 55 mm** | **4** | Axes principaux de montage de la base des doigts. |
| **Aimants Néodyme** | *EXCLUS / NON REQUIS* | **0** | Aucun aimant requis en V1 (FSR 402) ni en V2 (AnySkin). |
| **Tubes de Guidage** | Tube Téflon **PTFE 0.9 mm (ID) / 1.5 mm (OD)** | 2 m | Acheminement interne courbe des tendons. |
| **Manchons de Sertissage** | Manchons en cuivre ou aluminium **Ø 1.5 mm** | **25** | Sécurisation mécanique des lignes sans nœuds. |

### 1.3 Matières Premières & Consommables
| Désignation | Marque / Spécifications | Rôle |
| :--- | :--- | :--- |
| **Fil de Flexion (Tendon)** | Dyneema tressé PE 9 brins **Ø 0.80 mm** (Rupture 1177 N) ou **Ø 0.60 mm** (Rupture 750 N) | Lignes de flexion en force (STS3250) |
| **Fil de Précision (Tendon)** | Vectran ou Dyneema tressé **Ø 0.60 mm** | Lignes de précision sans fluage (HL-3915) |
| **Filament d'Impression** | **PA12-CF** (Nylon chargé à 15% de fibres de carbone) | Impression 3D des phalanges et doigts. |
| **Silicone de Moulage** | **Smooth-On EcoFlex 00-30** ou **Dragon Skin 10** | Coulée de la peau élastique pour retour passif. |
| **Matériau Paume** | Bloc d'**Aluminium 6061-T6** | Usinage CNC du châssis principal (Palm Block). |
| **Matériau Poulies** | Rond d'**Aluminium 7075-T6** ou Bronze CuSn8 | Usinage CNC des 8 spools d'enroulement. |

### 1.4 Tactile Sensing (Système de Préhension)
| Désignation | Spécifications | Qté | Rôle |
| :--- | :--- | :---: | :--- |
| **Capteurs V1 (Simples)** | **FSR 402** (Capteurs analogiques fins, épaisseur <0.3 mm) | **5** | Intégration immédiate sous la pulpe des doigts. |
| **Capteurs V2 (3 Axes)** | **AnySkin** (Peau magnétique 2.0 mm + 5 magnétomètres 3 axes) | 5 | Évolution logicielle fine sans recalibration (V2). |

---

## 🛠️ 2. Fabrication des Composants (Usinage, Impression, Moulage)

Le succès mécanique de la main repose sur trois procédés de fabrication distincts. Respectez scrupuleusement les consignes machine ci-dessous :

### 2.1 Impression 3D des Doigts (Qidi Plus 4 — Filament PA12-CF)
Le Nylon Carbone (PA12-CF) est obligatoire pour sa grande rigidité axiale et son faible coefficient de frottement dans les pivots.
*   **Hauteur de couche :** 0.12 mm (pour la précision des passages internes des goupilles et roulements).
*   **Remplissage (Infill) :** 100% rectiligne ou gyroïde sur les zones de pivots (MCP/PIP/DIP) ; 40% sur le reste du corps.
*   **Buse :** Acier trempé ou Rubis de 0.4 mm (obligatoire pour le filament abrasif carbone). Température : 285°C.
*   **Lit chauffant :** 80°C avec colle PVP ou Magigoo PA.
*   **Post-traitement crucial :** Le PA12-CF est extrêmement hygroscopique. **Séchez le filament à 80°C pendant 12h** avant impression. Une fois imprimées, laissez les pièces reposer 24h à 50% d'humidité pour qu'elles retrouvent leur flexibilité nominale (évite le côté cassant post-impression).

### 2.2 Usinage CNC de la Paume et des Poulies (NestWorks C500)
L'utilisation de pièces usinées CNC résout définitivement les problèmes de déformation sous charge de compression axiale.

#### A. Le Châssis Paume (Palm Block) — Aluminium 6061-T6
*   **Fraisage :** Réalisez l'usinage en 2 posages sur la C500. Portez une attention particulière aux alésages destinés à recevoir les axes inox 3x55 mm.
*   **Finition :** Ébavurez soigneusement toutes les arêtes intérieures. Une arête vive sur le trajet d'un tendon Dyneema provoquera sa rupture par cisaillement en quelques cycles. Passez un fil de polissage ou du papier abrasif grain 1000 dans tous les canaux de guidage.

#### B. Les 8 Poulies d'Enroulement (Spools) — Aluminium 7075-T6 (ou Bronze)
Ces pièces requièrent une précision d'horlogerie (tolérances H7/g6) :
*   **Tambour d'enroulement :** Diamètre extérieur de Ø14 mm. Usinez une **gorge hélicoïdale en U de 0.75 mm de large et 0.6 mm de profondeur** avec un pas (pitch) de 0.7 mm sur exactement **1.5 tour**.
*   **Alésage Central :** Ø8 mm en tolérance H7 pour un emboîtement en force (press-fit) du roulement de guidage MR84ZZ.
*   **Trou de blocage du tendon :** Percez un trou radial de Ø1.0 mm sur la flasque latérale de la poulie et taraudez-le en **M1.6**. Ce trou recevra une vis sans tête en inox destinée à brider le câble Dyneema.

```
                  SCHÉMA TECHNIQUE D'UN SPOOL CNC D-HAND
                  
       ◄─────────────────────── 4.05 mm ───────────────────────►
       ┌──────┬────────────────────────────────────────┬──────┐
       │      │  Gorge hélicoïdale (Pitch 0.7mm)       │      │  ◄── Vis M1.6
       │ Flasq│  r = 6.0 mm (fond de gorge)            │ Flasq│      de bridage
       │ Ø14mm│                                        │ Ø14mm│      du câble
       ├──────┴────────────────────────────────────────┴──────┤
       │             Alésage Central H7 (Ø 8 mm)              │
       │           Reçoit le roulement MR84ZZ pressé          │
       └──────────────────────────────────────────────────────┘
```

### 2.3 Coulage de la Peau Élastique en Silicone (Retour Passif)
L'ORCA/D-Hand n'ayant pas de ressorts physiques, **la peau en silicone assure l'extension (l'ouverture) passive des doigts**.
1.  Nettoyez les moules négatifs (moules imprimés en PLA ou PETG).
2.  Appliquez un agent de démoulage (Ease Release 200).
3.  Mélangez le silicone (EcoFlex 00-30 ou Dragon Skin 10) à parts égales (1A:1B en poids).
4.  Passez le mélange dans une cloche à vide (débullage) pendant 5 minutes.
5.  Positionnez les phalanges assemblées du doigt bien droites dans le moule à l'aide des piges de centrage.
6.  Coulez le silicone lentement par le bas du moule pour chasser l'air. Laissez polymériser pendant 4 heures à 22°C (ou 30 minutes au four à 60°C).
7.  Démoulez délicatement en évitant de déchirer les zones minces au niveau des articulations.

---

## 🔩 3. Assemblage Mécanique Étape par Étape

### Étape 1 : Préparation et Pré-tensionnement des Tendons
1.  **Coupe nette :** Coupez vos tendons (Dyneema Ø0.80 mm pour la flexion, Vectran Ø0.60 mm pour la précision) à une longueur d'environ **0.6 m** à l'aide d'une lame de scalpel neuve sous tension. *Ne jamais utiliser de ciseaux sous peine d'ébouriffer les fibres.*
2.  **Bridage distal sans nœud :** À une extrémité du câble, insérez un manchon en cuivre de Ø1.5 mm. Repliez le câble en créant une micro-boucle (épissure Brummel si possible) et **sertissez le manchon de manière ferme** à l'aide d'une pince à sertir technique.
3.  *Alternative pour prototype :* Si vous utilisez des nœuds, réalisez un **Nœud Ashley Stopper** serré à la pince à bec plat, en laissant une queue de sécurité de 5 mm.

### Étape 2 : Assemblage des Phalanges
1.  Prenez les phalanges en PA12-CF préalablement ébavurées.
2.  Insérez en force modérée (press-fit) les roulements **MR84ZZ** dans les logements circulaires de chaque chape d'articulation (2 roulements par articulation).
3.  Emboîtez les phalanges distale, médiane et proximale.
4.  Alignez parfaitement les trous et insérez les goupilles cylindriques en acier rectifié **2x6 mm** à l'aide d'un petit maillet en plastique. La goupille doit affleurer de chaque côté de la phalange sans dépasser.

### Étape 3 : Routage des Tendons dans les Doigts
1.  Insérez des segments de tube Téflon **PTFE [0.9 × 1.5 mm]** dans les canaux internes courbes prévus dans les phalanges. Les tubes PTFE doivent dépasser de 1 mm à chaque extrémité pour éviter tout contact direct du câble avec le PA12-CF.
2.  Passez le tendon préparé à l'étape 1 depuis la pulpe distale vers la base du doigt à l'aide de brucelles.
3.  Vérifiez que le manchon serti (ou le nœud Ashley) vient se loger parfaitement dans le renfoncement de la pulpe. Tirez fermement pour valider l'ancrage.
4.  Marquez au feutre de couleur le rôle de chaque tendon à sa sortie à la base du doigt :
    *   **Tendon Inférieur = Fléchisseur** (Serrage, unique tendon requis relié au spool moteur).
    *   *Note sur l'extension :* Dans cette architecture révisée sous-actionnée à 8 DOF, **les tendons d'extension supérieure sont complètement supprimés**. L'extension et la réouverture du doigt sont assurées de manière 100% passive par l'élasticité de la peau en silicone coulée (Étape 2.3).

### Étape 4 : Assemblage de la Paume CNC (Palm Block)
1.  Insérez les tubes PTFE de guidage dans les 8 canaux de la paume en alu.
2.  Montez les doigts sur la paume en alignant les bases de doigts avec les chapes de la paume.
3.  Insérez les axes longs en inox rectifié **3x55 mm** pour traverser l'assemblage complet de la paume et verrouiller les 5 doigts.
4.  Sécurisez les axes longs à l'aide de micro-circlips ou de points de frein-filet faible sur les filetages d'extrémité.

---

## ⚡ 4. Routage, Tensionnement & Raccordement Final (Vers l'Avant-Bras)

Le raccordement entre la main (paume CNC) et la motorisation (avant-bras) s'effectue à travers le poignet creux.

```
       SCHÉMA DE CHEMINEMENT DES TENDONS DANS L'AVANT-BRAS
       
        [Doigts]
           │ (Tendons Dyneema / Vectran gainés PTFE)
           ▼
     [Poignet RS-00] (Passage creux central)
           │
           ├───────────────────────────────┐ (Séparation des 8 lignes)
           ▼                               ▼
     ┌─────────────┐                 ┌─────────────┐
     │ 4× STS3250  │ (Couche 1)      │ 1× STS3250  │ + 3× HL-3915 (Couche 2)
     └──────┬──────┘                 └──────┬──────┘
            │                               │
            └──────► [Poulies CNC Ø14mm] ◄──┘
```

### Étape 5 : Routage à travers le poignet creux
1.  Regroupez les 8 tendons sortant de la paume.
2.  Faites-les glisser délicatement à l'intérieur du poignet creux de pronosupination **RS-00**. Veillez à ce que les câbles ne se croisent pas et ne s'entortillent pas lors de cette étape.
3.  Une fois les câbles sortis du poignet à l'intérieur du tube carbone de l'avant-bras, distribuez-les vers leurs moteurs respectifs.

### Étape 6 : Montage des Poulies (Spools) sur les Moteurs
1.  Montez les 8 spools en aluminium CNC sur les arbres cannelés des servomoteurs **STS3250** et **HL-3915**.
2.  Sécurisez chaque spool sur l'arbre moteur avec sa vis axiale centrale d'origine Feetech en y appliquant une goutte de **frein-filet moyen (Loctite 243)**.

### Étape 7 : Raccordement sans nœud et Tensionnement
1.  Mettez les 8 servomoteurs sous tension électronique et commandez-les en **position zéro (neutre)** via votre bus TTL.
2.  Prenez le tendon libre d'un doigt, passez-le dans la gorge hélicoïdale de son spool dédié.
3.  Faites **1.5 tour d'enroulement complet** à la main dans la gorge hélicoïdale. Le câble doit être parfaitement logé dans sa spirale.
4.  Tirez fermement sur l'extrémité libre du câble avec une pince à bec plat pour éliminer tout jeu et mettre le tendon sous une pré-tension constante d'environ **10 à 15 N** (le doigt doit commencer à esquisser un mouvement de flexion).
5.  Tout en maintenant cette tension, vissez fermement la vis sans tête **M1.6** dans le trou radial du spool. La vis vient pincer le Dyneema contre le métal, assurant un bridage mécanique indestructible sans aucun nœud.
6.  Coupez le surplus de fil à 5 mm du spool et appliquez une micro-goutte de vernis ou de colle cyanoacrylate sur l'extrémité coupée pour éviter l'effilochage.

---

## 🔌 5. Intégration Tactile & Câblage Électrique

L'intégration électronique de la D-Hand V1 a été simplifiée pour n'utiliser qu'un seul bus de données et assurer une fiabilité thermique maximale.

### 5.1 Raccordement et Dissipation du Convertisseur Buck 12V
Pour éviter tout risque de surchauffe à l'intérieur de l'avant-bras fermé :
1.  Appliquez un morceau de **Gap Pad thermique Bergquist 5000S35** de 0.5 mm sur le dos plat du PCB du convertisseur **Pololu D24V150F12**.
2.  Vissez le convertisseur contre la plaque de montage en aluminium usinée de l'avant-bras. Cette plaque doit être en contact structurel direct avec le tube principal en carbone.
3.  Raccordez l'alimentation principale (Batterie 48V du robot) sur l'entrée du Buck.
4.  Raccordez la sortie 12V stabilisée sur le bus d'alimentation des servomoteurs.

### 5.2 Chaînage des Servomoteurs (Bus Unique SCServo)
Les moteurs Feetech partagent tous le même protocole de communication série TTL half-duplex.
1.  Chaînez les 8 moteurs en cascade (Daisy Chain) à l'aide des câbles à 3 broches fournis.
2.  Attribuez une **adresse matérielle unique (ID)** à chaque moteur via le logiciel de configuration Feetech :
    *   **ID 1 à 5 :** STS3250 (Flexion des 5 doigts)
    *   **ID 6 à 8 :** HL-3915 (Opposition Pouce, Abduction Index, Curl Palmaire)
3.  Raccordez l'extrémité de la chaîne à un unique adaptateur **USB-to-UART TTL (Feetech URT-1)** relié au calculateur principal du bras.

### 5.3 Montage des Capteurs Tactiles FSR 402 (Phase V1)
1.  Collez la face adhésive double face du capteur **FSR 402** directement sur la pulpe rigide en PA12-CF de chaque doigt.
2.  Acheminez les deux fils extra-fins de chaque capteur le long des canaux latéraux prévus sur le dos des doigts.
3.  Coulez la peau silicone (Étape 2.3) directement par-dessus le FSR 402. Le capteur est ainsi parfaitement encapsulé et protégé de l'usure, tout en bénéficiant de la répartition de pression qu'offre le silicone.
4.  Raccordez les 5 paires de fils FSR à un module convertisseur analogique-numérique (ADC) **ADS1115** ou multiplexeur **CD4051** situé dans la paume ou l'avant-bras, puis envoyez les valeurs de pression via le bus de contrôle.

---

## 📈 6. Mise en Route, Tensionnement & Calibration Logicielle

Une fois l'assemblage physique validé, la main doit être calibrée pour initialiser les tensions et définir les limites d'effort.

### 6.1 Premier Allumage et Vérification du Bus
Lancez un scan de votre bus série à 3 Mbps pour vérifier la présence des 8 actuateurs :
```bash
# Exemple via le terminal d'outils Feetech / orca_core
python -m orca_core.tools.ping_bus --port /dev/ttyUSB0 --baud 3000000
```
*Vérifiez que les IDs 1 à 8 répondent tous sans aucune perte de paquets.*

### 6.2 Script de Tensionnement Automatique des Tendons
Avant toute utilisation, les tendons doivent être pré-tendus de manière homogène. Le SDK `orca_core` intègre un script qui utilise le retour d'information en courant des servos pour tendre chaque ligne à une valeur cible (typiquement **5 N**) :

1.  Lancez le script de tensionnement :
    ```bash
    uv run python scripts/tension.py --config config/dhand_v1_right.yaml
    ```
2.  Le script va faire tourner très lentement chaque moteur dans le sens de l'enroulement tout en surveillant le courant (torque feedback). Dès que le courant atteint le seuil correspondant à 5 N de tension dans le câble, le moteur s'arrête et enregistre sa position angulaire comme la **Position Zéro Réelle**.
3.  Si le script détecte qu'un moteur doit tourner de plus de 1.5 tour pour obtenir la tension nominale, il s'arrête et affiche une alerte : *cela signifie que votre pré-tension manuelle lors du montage (Étape 7) était trop lâche.* Desserrez la vis M1.6 du spool concerné, retendez le câble à la pince, resserrez et relancez le script.

### 6.3 Calibration des Butées de Course
Pour éviter que les puissants STS3250 (50 kg.cm) ne forcent sur la structure en PA12-CF en cas de mauvaise commande logicielle :
1.  Lancez la procédure de calibration de course :
    ```bash
    uv run python scripts/calibrate.py --config config/dhand_v1_right.yaml
    ```
2.  Le script vous demandera de fermer manuellement chaque doigt de manière complète et douce (le silicone doit être écrasé, le doigt formant un poing fermé).
3.  Enregistrez cette position maximale. Le script va inscrire ces valeurs limites (Min/Max angle) directement dans la **mémoire EEPROM non volatile de chaque servomoteur Feetech**. 
4.  *Sécurité matérielle :* Même en cas de crash de votre programme de contrôle principal, les moteurs refuseront physiquement de dépasser ces angles limites enregistrés dans leur firmware, protégeant ainsi vos câbles Dyneema et vos articulations imprimées de toute destruction accidentelle.

---

Votre main **D-Hand V1 Révisée** est désormais entièrement assemblée, câblée, protégée thermiquement et calibrée. Elle est prête à effectuer ses premières tâches de préhension !
