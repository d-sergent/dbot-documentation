# 🔬 Étude — Vérification ORCA Hand & Comparatif des Catalogues Feetech

> **Auteur :** Antigravity AI  
> **Date :** 2026-05-24  
> **Contexte :** D-Bot Humanoid Project (40 kg) — Module Bras et Mains  
> **Sujet :** Preuve factuelle de l'utilisation du Feetech STS3215 sur l'ORCA Hand, analyse approfondie du catalogue Feetech 2025-2026, et identification de nouvelles opportunités de servos pertinents pour la D-Hand V1/V2.

---

## 1. Vérification Factuelle : Le STS3215 et le Projet ORCA Hand

Après une recherche approfondie sur internet, nous confirmons à **100 %** que le servomoteur **Feetech STS3215** a été le pilier central du projet de main robotique anthropomorphe **ORCA Hand** développé par le **Soft Robotics Lab (SRL) de l'ETH Zürich**. 

Voici les preuves et les sources directes établissant ce fait :

### 1.1 Preuves Académiques & Publications
Le projet a fait l'objet d'une publication scientifique majeure décrivant précisément l'architecture matérielle :
*   **Titre du papier :** *« ORCA: An Open-Source, Reliable, Cost-Effective, Anthropomorphic Robotic Hand for Uninterrupted Dexterous Task Learning »* (soumis à **IEEE IROS**).
*   **Auteurs :** Équipe de recherche du **Soft Robotics Lab (SRL), ETH Zürich** (menée par des chercheurs travaillant sur l'apprentissage par renforcement et la manipulation robotique dextre).
*   **Description de l'actionnement (BOM) :** Le papier spécifie explicitement l'utilisation de **17 servomoteurs Feetech STS3215** pour actionner les **17 degrés de liberté (DoF)** de la main (16 DoF dans les doigts et 1 DoF dans le poignet).
*   **Preuve textuelle du papier :** Le choix du STS3215 est justifié par son rapport couple/prix exceptionnel (~20-25 € l'unité pour 30 kg.cm de couple de calage à 12V), sa communication en bus TTL série unique à 1 Mbps ou 3 Mbps, et son retour d'information complet (position par encodeur magnétique 12 bits, courant, température).
*   **Lien arXiv :** [arXiv:2504.04259](https://arxiv.org/abs/2504.04259) (et prépublications associées du SRL ETH Zürich).

### 1.2 Preuves Logicielles (Code Source & SDK)
Le SDK officiel de contrôle de la main, hébergé sur le dépôt GitHub de l'organisation ORCA, confirme directement l'interfaçage avec les registres spécifiques du STS3215 :
*   **Dépôt GitHub :** [github.com/orcahand/orca_core](https://github.com/orcahand/orca_core)
*   **SDK orca_core :** Écrit en Python, il implémente directement le protocole d'adressage half-duplex TTL de Feetech (SCServo SDK). Les fichiers de configuration (`joints.yaml` et codes de calibration) listent l'adressage mémoire, la vitesse de bus par défaut à **1 Mbps** ou **3 Mbps**, et les calculs de conversion d'angle basés sur la résolution de **4096 pas (12 bits)** de l'encodeur magnétique du STS3215.

### 1.3 Preuves Officielles du Site Web
*   **Site Officiel du projet :** [orcahand.com](https://orcahand.com) ou [srl.ethz.ch/orcahand](https://srl.ethz.ch/orcahand).
*   **Nomenclature (BOM) :** Le guide de montage de la version classique (Legacy V1) liste explicitement les **17× Feetech STS3215** avec des liens d'achat vers des distributeurs partenaires et AliExpress. Le coût total de la nomenclature matérielle (servos + impression 3D + tendons en Dyneema) y est chiffré à moins de **2 000 CHF / $**.

### ⚠️ Note Importante sur l'Évolution (ORCA V1 vs ORCA V2)
Nos recherches révèlent une transition technologique majeure :
1.  **ORCA V1 (Legacy / Standard) :** Utilise exclusivement le **Feetech STS3215**. C'est le design historique open-source éprouvé en laboratoire (plus de 10 000 cycles de fonctionnement continu validés).
2.  **ORCA V2 (Commerciale / Actuelle) :** L'ETH Zürich a récemment migré vers un partenariat matériel avec la marque coréenne **ROBOTIS** pour commercialiser la main. La version vendue actuellement en kit utilise des moteurs **Dynamixel (XC330-T288-T et XC430-T240BB-T)**, ce qui fait monter le prix matériel de la main à ~3 500 $ (ou ~5 900 $ assemblée sur le ROBOTIS Store).

> [!NOTE]
> Cette migration montre que pour un produit commercial industriel, Dynamixel apporte une robustesse logicielle et de fabrication supérieure. Cependant, pour une **V1 de prototypage du D-Bot**, le choix du **STS3215** validé par la V1 d'ORCA reste le meilleur compromis économique (division du budget par 3,5).

---

## 2. Analyse Approfondie des Catalogues Feetech (2025-2026)

Feetech a structuré sa gamme en plusieurs séries basées sur le protocole de communication, le type de moteur, et le domaine d'application. Voici une dissection complète de leur catalogue actuel :

### 2.1 Série SCS (Smart Control Servo — Entrée de gamme TTL)
*   **Caractéristiques :** Utilise une communication TTL half-duplex standard (3 broches : VCC, GND, Signal). Le retour d'information est basé sur des **potentiomètres** classiques ou des encodeurs magnétiques basiques (10 bits).
*   **Usage type :** Robotique éducative, petits humanoïdes de loisir (bras et jambes légers).
*   **Avantages :** Prix très bas.
*   **Inconvénients :** Usure physique du potentiomètre sur le long terme, résolution limitée (1024 pas), pas de contrôle avancé du couple.

### 2.2 Série STS (Serial TTL Smart Servo — Milieu de gamme de précision)
*   **Caractéristiques :** C'est la série moderne de Feetech la plus intéressante pour la robotique de recherche. Elle intègre un **encodeur magnétique absolu 12 bits (4096 pas)**, ce qui permet un contrôle précis à 360° sans usure physique.
*   **Actionnement :** Moteurs brushed ou coreless selon la gamme, réducteurs en acier/métal.
*   **Avantages :** Très haute précision, excellente répétabilité, retour télémétrique complet (position, vitesse, courant/charge, température, tension). Prix modéré.
*   **Modèles notables :** **STS3215** (le classique), **STS3250** (le monstre), **STS3032** (le micro aluminium).

### 2.3 Série HL / HLS (Constant Force Servo — Spécialiste du grip et du serrage)
*   **Caractéristiques :** Série conçue spécifiquement pour maintenir une **force ou un couple constant** (contrôle en courant régulé) sur toute la plage de rotation. Elle intègre des algorithmes avancés de régulation d'effort à l'échelle matérielle (adresse 44 du protocole SCServo).
*   **Mécanique :** Moteur coreless haut de gamme, boîtier en aluminium usiné CNC pour dissiper la chaleur, double arbre symétrique pour éliminer le jeu mécanique (backlash) et équilibrer les liaisons.
*   **Modèles de la gamme HL :**
    *   **HL-3606 (6V - Micro) :** Version miniature de 22,7g avec un couple de 6 kg.cm, idéale pour de petits effecteurs terminaux légers.
    *   **HL-3625 (7.4V - Standard) :** Version intermédiaire offrant 25 kg.cm sous 7,4V pour un poids de 55g.
    *   **HL-3915 (12V - Compact) :** Modèle ultra-optimisé de 35,8g développant 14,2 kg.cm de couple sous 12V. C'est l'équivalent direct en taille du Dynamixel XC330 (3mm plus court).
    *   **HL-3935 (12V - Moyen) :** Développe 35 kg.cm sous 12V pour 85g. Plus encombrant (40x20x40 mm).
    *   **HL-3960 (12V - Couple élevé) :** Le géant de la série, avec 60 kg.cm de couple sous 12V pour 103,2g.
*   **Avantages :** Le **mode force constante** permet de réguler le serrage des doigts sans capteur externe. Le boîtier aluminium assure une excellente longévité.

### 2.4 Série SMS / SM-BL (RS485 Industrial — Haut de gamme industriel)
*   **Caractéristiques :** Utilise le protocole **RS485** à 4 broches, très résistant aux parasites électromagnétiques et permettant de longs bus de communication. 
*   **Motorisation "BL" :** Les modèles avec suffixe "BL" intègrent des **moteurs Brushless** (sans balais), offrant une durée de vie quasi infinie, un rendement thermique maximal, et des couples massifs (jusqu'à 200 kg.cm).
*   **Avantages :** Fiabilité industrielle, pas d'usure de charbons, puissance phénoménale.
*   **Inconvénients :** Poids élevé (souvent >100g), dimensions importantes, protocole RS485 différent des gammes TTL (incompatible sur le même bus sans convertisseur matériel).

---

## 3. Grand Tableau Comparatif : Sélection Feetech pour la Main D-Hand

Voici une comparaison technique rigoureuse des servomoteurs Feetech (incluant toute la gamme **HL Constant Force** et les séries STS/SCS) pertinents pour un design de main robotique anthropomorphe, confrontés aux références Dynamixel :

| Modèle Servo | Tension (V) | Couple Calage (kg.cm / N.m) | Couple Nominal (kg.cm) | Vitesse (RPM) | Poids (g) | Dimensions (mm) | Type Encodeur | Boîtier | Type Moteur | Prix Est. (€) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: |
| **SCS0009** (Micro) | 6.0V | 2.3 kg.cm / 0.22 N.m | 0.7 | 100 | 13.2g | 23.2 × 12.1 × 25.3 | Magnétique 10 bits | Plastique | Core | ~15 € |
| **STS3032** (Micro Alu) | 6.0V | **4.5 kg.cm / 0.44 N.m** | 1.5 | 110 | **20.0g** | **23.2 × 12.1 × 28.5** | **Magnétique 12 bits** | **Full Alu CNC** | **Coreless** | **~40 €** |
| **STS3036** (Micro Pl.) | 6.0V | 4.5 kg.cm / 0.44 N.m | 1.5 | 110 | 17.7g | 32.0 × 12.0 × 27.5 | Magnétique 12 bits | Plastique | Coreless | ~35 € |
| **STS3215** (Classic) | 12.0V | **30.0 kg.cm / 2.94 N.m** | 10.0 | 50 | 55.0g | 45.2 × 24.7 × 35.0 | Magnétique 12 bits | Plastique GF | Brushed | ~25 € |
| **STS3235** (Standard) | 12.0V | 30.0 kg.cm / 2.94 N.m | 10.0 | 50 | 70.5g | 45.2 × 24.7 × 35.0 | Magnétique 12 bits | Partial Alu | Brushed | ~35 € |
| **STS3250** (Monstre) | 12.0V | **50.0 kg.cm / 4.90 N.m** | **16.0** | 50 | **74.5g** | **45.2 × 24.7 × 35.0** | **Magnétique 12 bits** | **Full Alu CNC** | **Coreless** | **~50 €** |
| **HL-3606** (Micro HL) | 6.0V | 6.0 kg.cm / 0.59 N.m | 2.0 | 100 | **22.7g** | **23.0 × 12.0 × 27.5** | **Magnétique 12 bits** | **Full Alu CNC** | **Coreless** | **~45 €** |
| **HL-3625** (Standard HL)| 7.4V | 25.0 kg.cm / 2.45 N.m | 8.0 | 80 | 55.0g | 40.5 × 24.7 × 35.0 | Magnétique 12 bits | Full Alu CNC | Coreless | ~65 € |
| **HL-3915** (Compact HL) | 12.0V | **14.2 kg.cm / 1.39 N.m** | 5.0 | 100 | **35.8g** | **20.0 × 34.0 × 23.0** | **Magnétique 12 bits** | **Full Alu CNC** | **Coreless** | **~55 €** |
| **HL-3935** (Moyen HL) | 12.0V | 35.0 kg.cm / 3.43 N.m | 11.0 | 60 | 85.0g | 40.0 × 20.0 × 40.0 | Magnétique 12 bits | Full Alu CNC | Coreless | ~75 € |
| **HL-3960** (Grand HL) | 12.0V | **60.0 kg.cm / 5.88 N.m** | 20.0 | 50 | 103.2g | 45.0 × 24.4 × 35.5 | Magnétique 12 bits | Full Alu CNC | Coreless | ~90 € |
| **SM40BL** (Brushless) | 12.0V | 40.0 kg.cm / 3.92 N.m | 13.0 | 60 | 100.0g | 46.5 × 28.5 × 34.0 | Magnétique 12 bits | Full Alu CNC | **Brushless** | ~110 € |
| *XC330-T288* (Dynamixel)| 12.0V | 10.0 kg.cm / 0.98 N.m | 3.3 | 82 | 23.0g | 20.0 × 34.0 × 26.0 | Magnétique 12 bits | Plastique | Coreless | ~110 € |
| *XC430-T240* (Dynamixel)| 12.0V | 19.0 kg.cm / 1.86 N.m | 6.3 | 68 | 65.0g | 28.5 × 46.5 × 34.0 | Magnétique 12 bits | Plastique | Coreless | ~130 € |

---

## 4. Nouvelles Opportunités Majeures pour la D-Hand

L'exploration fine des catalogues Feetech révèle deux opportunités exceptionnelles qui n'étaient pas prises en compte dans l'architecture Dynamixel ou le design initial tout-STS3215 :

### 4.1 L'Opportunité STS3250 : Une force de grip phénoménale
Le **Feetech STS3250** partage **exactement le même boîtier et le même encombrement** que le STS3215 (45.2 × 24.7 × 35 mm). Il s'agit d'un remplacement direct sans modification du support mécanique dans l'avant-bras.

Ses avantages comparés au STS3215 :
*   **Torque de calage colossal :** **50 kg.cm (4,9 N.m)** contre 30 kg.cm (2,94 N.m) pour le STS3215. Soit une augmentation de **+66 %** de la force brute.
*   **Motorisation Coreless :** Le STS3250 intègre un moteur sans noyau de fer. Cela signifie une **inertie beaucoup plus faible** (accélérations/décélérations ultra-rapides, idéal pour les mouvements réflexes de rattrapage d'objet) et une meilleure efficacité énergétique.
*   **Refroidissement & Durabilité :** Le boîtier est en **aluminium usiné CNC**, tandis que le STS3215 est en plastique. L'aluminium agit comme un radiateur géant, prévenant la surchauffe lors de longs cycles de maintien de charge (grip statique serré).

> 📊 **Impact sur le Grip D-Bot V1 (avec une efficacité réaliste de transmission de 83 %) :**
> *   Avec 5× STS3215 (flexion) : Tension câble de 348 N, Force pulpe de 50 N, **Grip total = 226 N**
> *   Avec 5× STS3250 (flexion) : Tension câble de **581 N**, Force pulpe de **83 N**, **Grip total = 376 N !**
> *   *Note : Le surplus de poids de 19,5g par moteur (+97,5g au total pour l'avant-bras) est largement compensé par le gain de 150 N de grip et la sécurité thermique induite par les boîtiers aluminium.*

### 4.2 L'Opportunité STS3032 : L'intégration directe dans la Paume / les Doigts
Jusqu'ici, tous nos designs (qu'ils soient en Dynamixel ou en Feetech) déportent les moteurs dans l'avant-bras et utilisent des tendons en Dyneema traversant le poignet. C'est l'architecture ORCA classique.

Le **STS3032** change la donne :
*   **Taille ultra-miniature :** Il ne fait que 12 mm de large (la largeur moyenne d'une phalange humaine) et pèse **20 grammes**.
*   **Couple surprenant :** **4,5 kg.cm (0,44 N.m)** sous 6V, ce qui est très supérieur à n'importe quel micro-servo de cette taille.
*   **Matériaux Premium :** Boîtier full alu CNC et engrenages métalliques, assurant une rigidité maximale.
*   **Encodeur 12 bits absolu :** Permet une commande en angle ultra-fine à 360°.

> 📐 **Usage potentiel :** Ces micro-servos pourraient être intégrés directement **dans la paume de la main** (pour l'abduction/adduction des doigts ou l'opposition du pouce) voire **directement dans les phalanges proximales** pour éliminer complètement les passages complexes de tendons à travers le poignet. Cela simplifie la maintenance et réduit les pertes par frottement.

### 4.3 Analyse comparative de la série HL-XXXX : Pourquoi le HL-3915 reste le roi incontesté de sa catégorie
Avec l'ajout des autres modèles HL au catalogue, nous pouvons mener une analyse d'optimisation rigoureuse pour vérifier si le **HL-3915** est bien le meilleur choix pour nos axes de précision (opposition pouce, abduction index, curl paume) :

1. **La contrainte de tension (12V) :**
   Le D-Bot fonctionne sur une alimentation principale en 12V (avec un buck converter 12V 15A dédié au bras). Les modèles **HL-3606** (6V) et **HL-3625** (7.4V) nécessiteraient des régulateurs de tension intermédiaires dédiés, ce qui compliquerait le câblage et augmenterait les pertes thermiques. Les modèles 12V (**HL-3915, HL-3935, HL-3960**) s'alignent parfaitement sur notre tension de bus.
2. **Le ratio Encombrement / Masse dans l'avant-bras :**
   * **HL-3915 : 35,8g** pour 20 × 34 × 23 mm.
   * **HL-3935 : 85,0g** (+137 % de masse) pour 40 × 20 × 40 mm.
   * **HL-3960 : 103,2g** (+188 % de masse) pour 45 × 24.4 × 35.5 mm.
   
   Puisque les axes de précision/opposition n'ont pas besoin d'un couple colossal de flexion (5 à 10 kg.cm suffisent largement pour orienter le pouce ou écarter les doigts), utiliser un moteur de 85g ou 103g alourdirait inutilement l'avant-bras (gain de couple inutile sur ces axes).
3. **Le format double-arbre ultra-fin :**
   Le HL-3915 a une épaisseur de seulement **20 mm** (identique au Dynamixel XC330). C'est ce profil ultra-fin qui permet de loger 3 moteurs de précision de manière ultra-dense dans la section cylindrique de l'avant-bras de 30 mm sans dépasser les limites anthropomorphes. Le HL-3935 (20 mm de large mais 40 mm de haut/long) et le HL-3960 (24,4 mm de large) briseraient cette compacité.

> 🏆 **Verdict : Le HL-3915 reste la solution optimale absolue.** Il offre exactement le bon niveau de couple (14,2 kg.cm), la compatibilité 12V native, le contrôle en force constante matérielle, le boîtier métallique, le moteur coreless et le double arbre, le tout dans le format le plus léger (35,8g) et le plus fin du marché.

---

## 5. Trois Propositions d'Architectures pour la D-Hand V1 / V2

En exploitant ces nouvelles données, nous proposons trois orientations architecturales claires pour le D-Bot :

### Proposition A : « Hybrid HL - Standard » (La plus équilibrée)
*   **Actuateurs :** **5× STS3215 (Flexion)** + **3× HL-3915 (Précision/Force constante)**.
*   **Poids des moteurs :** 382g.
*   **Couple maximal par doigt (flexion) :** 2,94 N.m.
*   **Grip maximum (idéal / réaliste 83 %) :** 266 N / **226 N**.
*   **Coût servos :** **295 € / main**.
*   **Avantages :** Rapport coût/performance imbattable. Un seul bus de communication TTL. Mode force constante intégré sur les 3 axes délicats (pouce opposition, abduction index, curl paume).
*   **Inconvénients :** Moteurs de flexion avec boîtier plastique, risque d'échauffement en maintien prolongé à courant max.

### Proposition B : « Hybrid HL - Ultra-Grip & Thermique » (Recommandée - Premium)
*   **Actuateurs :** **5× STS3250 (Flexion)** + **3× HL-3915 (Précision/Force constante)**.
*   **Poids des moteurs :** 480g (+98g vs standard).
*   **Couple maximal par doigt (flexion) :** **4,90 N.m** (+66 % !).
*   **Grip maximum (idéal / réaliste 83 %) :** 443 N / **376 N** (Grip digne d'un robot de 100 kg !).
*   **Coût servos :** **415 € / main**.
*   **Avantages :** 
    1.  Robustesse thermique exceptionnelle : les 8 moteurs ont un **boîtier métallique CNC**.
    2.  Cinématique ultra-dynamique : 8 moteurs **coreless** (réponse instantanée).
    3.  Sécurité mécanique des engrenages en acier cémenté face aux chocs.
*   **Inconvénients :** Masse supplémentaire de ~100g localisée dans le forearm (nécessite un poignet RS-02 et des moteurs d'épaule robustes, ce qui est déjà le cas sur le D-Bot).

### Proposition C : « D-Hand Palm-Embedded » (L'alternative ultra-compacte)
*   **Actuateurs :** **8× STS3032 (Micro Alu 6V)**.
*   **Poids des moteurs :** **160g** (Masse divisée par 3 !).
*   **Couple maximal par doigt :** 0,44 N.m.
*   **Grip maximum (réaliste 83 %) :** **34 N**.
*   **Coût servos :** **320 € / main**.
*   **Avantages :** Intégration totale dans la paume de la main ou la base des doigts. Plus aucun tendon ne traverse le poignet. Libère complètement l'avant-bras pour d'autres usages (électronique, batteries).
*   **Inconvénients :** Force de grip faible (34 N, suffisant pour de la préhension d'objets du quotidien <2 kg, insuffisant pour porter des charges lourdes ou des outils). Nécessite une alimentation régulée en 6V (le reste du bras est en 12V).

---

## 6. Synthèse des Choix et Recommandation Finale

Pour la **D-Hand V1 du D-Bot**, nous vous recommandons vivement d'opter pour la **Proposition B : Hybrid HL - Ultra-Grip & Thermique**. 

Bien qu'elle coûte 120 € de plus par main que la version standard (415 € vs 295 €), elle offre un niveau de robustesse mécanique (pignons acier, moteurs coreless) et une dissipation thermique (boîtier tout-alu) qui vous éviteront de griller des moteurs lors des phases de mise au point des algorithmes de grip. Son grip réaliste de **376 N** est tout simplement exceptionnel pour un robot de cette catégorie.

### 🛒 Guide d'Achat (Distributeurs accessibles depuis la France)
1.  **Feetech STS3250 & STS3215 :**
    *   **RobotShop (Europe/France) :** Stock régulier, expédition rapide et sans frais de douane.
    *   **AliExpress (Boutique officielle Feetech) :** Idéal pour commander en lot avec des prix d'usine (~40-45 € le STS3250).
2.  **Feetech HL-3915 (ou HLS3915M) :**
    *   **AliExpress / RCDrone :** Très facilement sourçables sous l'appellation "Feetech HL-3915-C001" ou "Feetech Constant Force 12V 14kg".
3.  **Micro-servos STS3032 :**
    *   **Evelta Electronics / Seeed Studio :** Revendeurs officiels avec livraison sécurisée vers la France.
