# 📘 MANUEL TECHNIQUE COMPLET — Fabrication & Montage de la D-Hand V1 Révisée (8 DOF)

> **Projet :** D-Bot Humanoid (40 kg)  
> **Module :** Bras et Mains — Main D-Hand V1 Révisée  
> **Auteur :** Antigravity AI  
> **Date de publication :** 2026-05-25  
> **Statut :** Document technique de fabrication consolidé et prêt pour exécution  

---

## 🎯 Introduction & Objectifs de ce Guide

Ce manuel rassemble et unifie l'intégralité des instructions, méthodes, tolérances et références nécessaires pour fabriquer et assembler la main robotique **D-Hand V1 Révisée**. 

> 🔗 **Référence Officielle (ORCA Hand) :** L'architecture originelle de cette main, ainsi que les méthodes détaillées pour le moulage de la peau en silicone et l'intégration des capteurs FSR, sont librement consultables sur le site officiel du projet *Soft Robotics Lab* de l'ETH Zurich : **[https://orca.ethz.ch/](https://orca.ethz.ch/)**.

Basée sur une architecture hybride haut de gamme à **8 Degrés de Liberté (8 DOF)** sous-actionnée, cette conception combine le meilleur de l'ingénierie mécanique : de la puissance brute via des servomoteurs **Feetech STS3250** (50 kg.cm), de la précision fine grâce aux servos **Feetech HL-3915** avec mode force constante, et un squelette ainsi qu'une paume ultra-robustes en **PA12-CF** (Nylon Carbone) imprimés en 3D.

Ce guide est conçu pour vous accompagner pas-à-pas de l'achat des matières premières à la calibration logicielle finale sur votre banc d'essai.

---

## 📦 1. Nomenclature Globale (BOM Complète & Validée)

Voici la liste exacte des composants, fixations et matières premières nécessaires pour assembler **une main complète (D-Hand V1)**.

### 1.1 Motorisation & Électronique (Dans l'Avant-Bras)
| Désignation | Référence / Spécifications | Qté | Rôle mécanique |
| :--- | :--- | :---: | :--- |
| **Servomoteur de Force** | **Feetech STS3250** (12V, 50 kg.cm stall, coreless, boîtier alu CNC, pignons acier, TTL) | **5** | Actionnement en flexion/serrage des 5 doigts. |
| **Servomoteur de Précision** | **Feetech HL-3915** (12V, 14.2 kg.cm stall, coreless, boîtier alu CNC, mode force matérielle, TTL) | **3** | Opposition du pouce, abduction index, curl palmaire. |
| **Convertisseur Buck** | **DROK 48V→12V 25A** (Entrée 30–60V / Sortie 12V fixe, 25A max / 20A continu, efficacité 96%, boîtier alu IP67, 74×74×32mm) | **1** | Alimentation stable du bus de servomoteurs 12V depuis le bus 48V principal. |
| **Fusible Réarmable** | **PTC 15A** | **1** | Protection surcourant du rail 12V entre le DROK et le bus servo. |

### 1.2 Structure & Quincaillerie Mécanique
| Désignation | Référence / Spécifications | Qté | Emplacement |
| :--- | :--- | :---: | :--- |
| **Micro-roulements** | **MR84ZZ** (Acier, étanche double flasque, 4 × 8 × 3 mm) | **36** | Pivots des phalanges (24 pour les 4 doigts, 4 pour le pouce) et contre-paliers des spools (8). |
| **Roulements Moyen** | **6x13x5 mm** (double flasque étanche) | **2** | Pivot de la base du pouce. |
| **Axes Cylindriques** | Goupilles cylindriques en acier rectifié **2 × 6 mm** | **20** | Verrouillage des chapes de phalanges (MCP/PIP/DIP). |
| **Axes Longs** | Axes en Inox rectifié **3 × 55 mm** | **4** | Axes principaux de montage de la base des doigts. |
| **Aimants Néodyme** | **N48 ronds (Ø 3 mm × 1.0 mm d'épaisseur - Supermagnete S-03-01-N)** | **8** | Insérés dans l'infill TPU (5 pulpes doigts + 3 pads paume). |
| **Tubes de Guidage (Option A)** | Tube Téflon **PTFE 1.2 mm (ID) / 1.6 mm (OD)** | ~4 m | ✅ **Reçu** (5 m en stock). Option serrée (jeu 0.2 mm, ratio ×1.2). |
| **Tubes de Guidage (Option B — recommandée)** | Tube Téflon **PTFE 1.5 mm (ID) / 1.9 mm (OD)** | ~4 m | ✅ **Reçu** (5 m en stock). Option confortable (jeu 0.5 mm, ratio ×1.5, identique ORCA v1). |
| **Manchons de Sertissage** | Manchons en cuivre ou aluminium **Ø 1.5 mm** | **25** | Sécurisation mécanique des lignes sans nœuds. |

### 1.3 Matières Premières & Consommables
| Désignation | Marque / Spécifications | Rôle |
| :--- | :--- | :--- |
| **Fil de Flexion (Tendon)** | Dyneema DM20 tressé **Ø 1.0 mm** (Rupture ~980 N, fluage quasi nul / zero-creep, frottement bas, bobine de 50 m achetée) | Tendons de force standardisés (force et précision) pour éliminer le recalibrage. |
| **Fil de Précision (Tendon)** | Dyneema DM20 tressé **Ø 1.0 mm** (identique aux tendons de force) | Lignes de précision identiques, simplification du stock. |
| **Fil de Retour (Tendon Élastique)** | **Fil élastique mono-brin 100% Polyuréthane (TPU) de Ø 0.8 mm (Beadalon Elasticity)**. ✅ **Reçu (en stock)** | Rappel d'extension passif principal des doigts, placé dans les canaux dorsaux d'origine (libres). |
| **Filament d'Impression** | **PA12-CF** (Nylon chargé à 15% de fibres de carbone). ✅ **Reçu (4 kg en stock)** | Impression 3D des phalanges rigides et squelette du doigt. |
| **Filament Flexible** | **Qidi TPU 95A-HF** (ou TPU 98A) | Gainage de protection élastique, rappel élastique secondaire (gaine), pulpes et pads paume. |
| **Silicone de Moulage** | *SUPPRIMÉ / NON REQUIS* | Remplacé avantageusement par le gainage imprimé en TPU. |
| **Colle d'Assemblage** | **Loctite Super Glue Gel** (Gel cyanoacrylate rapide) | Collage instantané des aimants de maintien sur les coques en PLA. |
| **Matériau Poulies** | Rond d'**Aluminium 7075-T6** ou Bronze CuSn8 | Usinage CNC des 8 spools d'enroulement. |

### 1.4 Tactile Sensing (Système de Préhension)
| Désignation | Spécifications | Qté | Rôle |
| :--- | :--- | :---: | :--- |
| **Capteurs V1 (eFlesh)** | **Magnétomètre MLX90393** (3 axes, sur micro-PCB WowRobo) | **8** | Capteurs de champ magnétique (5 doigts + 3 paume en triangle). |
| **Micro-Hub Tactile** | **ESP32-S3 USB local** (reçoit les 2 bus I2C natifs des 8 MLX90393) | **1** | Achemine les données eFlesh formatées vers le Jetson via USB CDC. |
| **Capteurs FSR 402** | *SUPPRIMÉS / EN RETRAIT* | **0** | Remplacés par la détection eFlesh 3 axes plus riche. |
| **Capteurs V2 (3 Axes)** | **AnySkin** (Peau silicone magnétique 2.0 mm + 5 magnétomètres 3 axes) | 5 | Évolution logicielle future sans recalibration (V2, uniquement sur doigts). |

### 1.5 Choix de Conception : Tresse Dyneema DM20 1.0 mm (Zéro-Fluage)
Suite à des analyses de frottement et de résistance mécanique, nous avons opté pour l'utilisation d'une **tresse Dyneema DM20 de 1.0 mm** de diamètre (achetée en bobine de 50 m) au lieu du Vectran 0.80 mm initial.
*   **Pourquoi le DM20 ?** Cette fibre associe le très faible coefficient de frottement du Dyneema classique (0.08 à 0.12 contre le PTFE) à la stabilité dimensionnelle du Vectran (zéro-creep, pas d'allongement permanent sous tension constante). Cela élimine définitivement les besoins de recalibrage de la main.
*   **Pourquoi 1.0 mm ?** Les moteurs Feetech STS3250 génèrent une tension de pic de 677 N en blocage. Une tresse DM20 de 1.0 mm (MBS d'environ 980 N, ou 882 N après sertissage à 90%) assure un facteur de sécurité confortable (Fs de pic de 1.30, et supérieur à 1.6 avec limitation électronique du couple en firmware). Les tresses DM20 n'existant pas en 0.8 mm (uniquement sous forme de fils à surlier torsadés qui se défont sous tension), le diamètre 1.0 mm est le minimum requis en tresse 12 fuseaux.
*   **Impact sur le guidage :** Le passage libre d'un câble de 1.0 mm nécessite des gaines **PTFE de 1.2 mm ID / 1.6 mm OD** (au lieu de 0.9 x 1.5 mm) pour offrir 0.2 mm de jeu mécanique et éviter tout coincement ou frottement dans les courbes des phalanges.

### 1.6 Choix de Conception : Mécanisme de Retour Passif (Tendons Élastiques Dorsaux)
L'ORCA V1 d'origine est un système actif antagoniste à 17 moteurs (flexion et extension actives). La main **D-Hand V1 est sous-actionnée à 8 moteurs** (flexion active par fil Dyneema, sans moteurs d'extension). L'ouverture des doigts doit donc être assurée de manière passive. 

Pour vaincre le frottement du câble de flexion et assurer une réouverture franche et dynamique, nous implémentons un **système de tendons élastiques dorsaux passifs**, s'inspirant du concept éprouvé de la main Pisa/IIT SoftHand.

*   **Intégration sans modification CAO :** Le fil élastique de Ø 0.8 mm est passé directement dans les canaux dorsaux des phalanges PA12-CF. Ces canaux d'origine ORCA accueillent le fil de 0.8 mm avec un jeu mécanique excellent et un frottement minimal sans aucun alésage requis (contrairement au fil de 1.0 mm qui risquerait de frotter ou nécessiterait un perçage fragilisant les parois des phalanges en PA12-CF).
*   **Matériau validé :**
    *   **Fil élastique mono-brin 100% Polyuréthane (TPU) de Ø 0.8 mm** (de marque *Beadalon Elasticity*, *Griffin* ou *The Beadsmith*). C'est un élastomère thermoplastique plein extrêmement résistant, qui ne s'effiloche pas, offre un excellent glissement et possède une mémoire de forme parfaite (zéro fluage sous tension).
    *   *Pourquoi le 0.8 mm est supérieur au 1.0 mm ?* 
        1.  **Géométrie :** Il coulisse avec du jeu dans les canaux dorsaux d'origine sans aucun risque de coincement.
        2.  **Rendement moteur :** Il offre une force de rappel de **~2 N au repos** et **~5 N en flexion complète**. C'est amplement suffisant pour redresser le doigt (couple de rappel 1.6x supérieur au couple gravitaire du doigt), tout en réduisant l'effort résistant opposé au moteur STS3250 lors des flexions (consommation électrique et échauffement moteur réduits).
*   **Où acheter immédiatement depuis la France :**
    *   Disponible en stock avec livraison 24/48h sur les sites français de loisirs créatifs comme **Perles & Co** (perlesandco.com), **France Perles** ou sur **Amazon.fr** (rechercher *« fil élastique polyuréthane 0.8mm perles »* ou *« Beadalon Elasticity 0.8mm »*). Une bobine de 25 m ou 100 m coûte environ 3 à 6 €.
*   **Impact sur les Degrés de Liberté (DOF) :**
    *   Cette solution **n'ajoute aucun DOF supplémentaire** à la main. Le système conserve ses 8 DOF actifs (contrôlés par les servos).
    *   Le tendon élastique agit comme un **antagoniste passif (ressort)**. Il convertit la structure lâche (qui serait indéterminée et molle une fois le câble de flexion relâché) en un mécanisme stable, complétant l'élasticité de la gaine TPU externe. Il apporte une compliance passive qui permet aux doigts d'épouser naturellement les formes complexes des objets saisis.

---

## 🛠️ 2. Fabrication des Composants (Usinage, Impression, Moulage)

Le succès mécanique de la main repose sur trois procédés de fabrication distincts. Respectez scrupuleusement les consignes machine ci-dessous :

### 2.1 Impression 3D des Doigts (Qidi Plus 4 — Filament PA12-CF)
Le Nylon Carbone (PA12-CF) est obligatoire pour sa grande rigidité axiale et son faible coefficient de frottement dans les pivots.
*   **Hauteur de couche :** 0.12 mm (pour la précision des passages internes des goupilles et roulements).
*   **Remplissage (Infill) :** 100% rectiligne ou gyroïde sur les zones de pivots (MCP/PIP/DIP) ; 40% sur le reste du corps.
*   **Buse :** Acier trempé ou Rubis de 0.4 mm (obligatoire pour le filament abrasif carbone). Température : 285°C.
*   **Lit chauffant :** 80°C avec colle PVP ou Magigoo PA.
*   **Séchage indispensable :** Le PA12-CF est extrêmement hygroscopique. **Séchez le filament à 80°C pendant 12h** avant impression. Une fois imprimées, laissez les pièces reposer 24h à 50% d'humidité pour qu'elles retrouvent leur flexibilité nominale. Un filament humide génère des bulles et du suintement (stringing) qui bouchent irrémédiablement les canaux internes.

> [!IMPORTANT]
> **Réglages Slicer Anti-Obstruction des Canaux (OrcaSlicer / QidiSlicer - Interface en Anglais) :**
> Pour éviter que les canaux de routage des phalanges ne soient bouchés par des supports ou rétrécis par la rétraction naturelle du Nylon, appliquez strictement les réglages suivants :
> 1. **Bloquer les supports internes :** 
>    * Ne laissez jamais le slicer générer de structures de support à l'intérieur des canaux de Ø 1.6 mm ou 1.9 mm.
>    * **Méthode :** Cochez **Don't support bridges** sous l'onglet `Support` -> section `Filament/Part relation`. Si des supports externes sont nécessaires pour le corps des phalanges (ex: sous les axes), utilisez des **Support Blockers** : faites un clic droit sur le modèle dans la vue 3D, sélectionnez `Add Support Blocker` (Boîte ou Cylindre) et positionnez les volumes sur les orifices d'entrée/sortie des canaux pour exclure toute génération de support à cet endroit.
> 2. **Compensation des diamètres de trous (Hole Compensation) :**
>    * Les contours circulaires FDM ont tendance à se resserrer sous la tension du filament.
>    * **Réglage :** Allez dans l'onglet `Quality` -> section `Precision` -> Réglez **X-Y hole compensation** sur **+0.15 mm** (ou +0.10 mm au minimum). Cela compense la contraction thermique et assure le bon diamètre de passage pour les tubes PTFE.
> 3. **Calibration du débit (Flow Calibration) :**
>    * Une sur-extrusion minime fermera le canal. Calibrez précisément le débit de votre PA12-CF.
>    * **Réglage :** Profil de filament -> onglet `Filament` -> ajustez le **Flow ratio** (généralement calé entre 0.96 et 0.99 pour le PA12-CF après calibration).
> 4. **Vitesse et pontage des parois :**
>    * Pour éviter l'affaissement ("sagging") du plafond des canaux :
>    * **Réglages :** Onglet `Speed` -> Réglez **Inner wall** à 40-50 mm/s. Dans la section `Speed` -> `Bridges` -> Réglez **Internal bridge speed** à 25-30 mm/s.

*   **Ajustement et ébavurage des canaux :**
    *   **Alésage manuel :** Avant d'insérer les tubes PTFE, passez manuellement un foret de précision (de Ø 1.6 mm pour l'Option A, ou Ø 1.9 mm pour l'Option B) à travers les canaux imprimés. Tournez le foret **à la main uniquement** (sans outil électroportatif) pour araser en douceur les lignes de couches ou les micro-bavures internes.
    *   **Biseautage du PTFE :** Taillez légèrement en chanfrein (biseau à 45°) l'extrémité extérieure du tube PTFE au cutter pour l'aider à glisser sans accrocher les stries de couches.

### 2.2 Fabrication de la Paume (Palm Block) & DFM (Design for Manufacturing)
La paume de la main D-Hand Hybrid révisée est une pièce structurelle majeure qui abrite le routage des câbles. 

> [!IMPORTANT]
> **Simplification et réutilisation des canaux (Transition 17 ➔ 8 moteurs + 5 retours passifs) :**
> L'adoption de la gaine élastique en TPU pour l'extension passive a permis de supprimer les moteurs d'extension active, mais le rappel d'extension principal est assuré par des tendons élastiques dorsaux de Ø 0.8 mm. Afin de centraliser leur tensionnement à la base de la main, ces élastiques traversent entièrement la paume.
> *   **Action CAO :** Sous Fusion 360, conservez **13 canaux ouverts** (8 canaux actifs pour les tendons fléchisseurs de Ø 1.0 mm guidés par gaines PTFE, et 5 canaux supérieurs/dorsaux pour les élastiques de retour de Ø 0.8 mm). Supprimez ou bouchez uniquement les **4 canaux restants** totalement inutilisés du modèle d'origine ORCA v1 (conçu pour 17 câbles). Cela renforce la rigidité mécanique du bloc de paume tout en garantissant un routage interne propre.

#### A. Méthode standard recommandée : L'Impression 3D en PA12-CF (Qidi Plus 4)
L'impression additive est la seule méthode capable de fabriquer des canaux courbes internes fermés dans un bloc monobloc sans aucun support. Le PA12-CF (Nylon Carbone) offre un excellent coefficient de glissement naturel pour les tubes PTFE et une résistance mécanique phénoménale.
*   **Hauteur de couche :** 0.12 mm ou 0.16 mm.
*   **Remplissage (Infill) :** **100% rectiligne** (obligatoire pour éviter tout écrasement structurel sous la compression axiale des 8 gaines PTFE sous tension).
*   **Buse :** Acier trempé ou rubis de 0.4 mm. Température : 285°C.
*   **Post-traitement & Insertion PTFE :** 
    *   Ébavurez les entrées et sorties de canaux.
    *   Appliquez les mêmes **Réglages Slicer Anti-Obstruction** que pour les doigts (voir §2.1) : notamment la compensation **X-Y hole compensation** de **+0.15 mm** et l'utilisation de **Support Blockers** sur les orifices pour empêcher tout dépôt de support interne.
    *   Faites un alésage manuel doux des canaux avec un foret adapté (Ø 1.6 mm ou 1.9 mm selon l'option choisie) avant d'insérer les tubes PTFE (Option A : 1.2×1.6 mm ou Option B : 1.5×1.9 mm).

#### B. Méthode alternative pour information : L'Usinage CNC en Aluminium 6061-T6 (Split-Palm)
Si vous choisissez l'usinage sur votre NestWorks C500 pour des raisons d'esthétique métal et de rigidité absolue, **un bloc monobloc est strictement inusinable** car une fraiseuse ne peut pas percer des canaux courbes fermés à l'intérieur d'un métal plein.
*   **Conception CAO en "Coquilles assemblées" (Split-Palm) :** Vous devez utiliser la version CAO découpée en deux moitiés (coquille palmaire et coquille dorsale) le long du plan médian des canaux.
*   **Usinage :** Les canaux fermés deviennent alors des **rainures ouvertes en 2,5D** sur les faces internes des deux coquilles, facilement usinables à l'aide d'une fraise hémisphérique (ball-nose) sur la C500.
*   **Finition :** Polissez méticuleusement les rainures au papier grain 1000 pour éliminer toute arête vive susceptible de cisailler les tendons.
*   **Assemblage :** Insérez les gaines PTFE dans les rainures, puis vissez les deux coquilles ensemble à l'aide de vis M3 transversales et de goupilles de centrage en acier pour reconstituer les canaux étanches.

### 2.3 Les 8 Poulies d'Enroulement (Spools) — Aluminium 7075-T6 (ou Bronze)
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

### 2.3 Impression 3D des Gaines Articulaires et Pulpes eFlesh en TPU (Rappel Élastique Secondaire & Protection)
Le gainage externe continu imprimé en TPU 95A/98A assure l'étanchéité, la protection du système tactile eFlesh, et sert de **rappel élastique secondaire** pour l'extension des doigts. Ce procédé élimine tout besoin de moulage de silicone chimique.

*   **Matériau :** Qidi TPU 95A-HF ou TPU 98A (séché à 65°C pendant 12h dans la Qidi Box).
*   **Méthode d'Impression Séparée et Assemblage en Chaussette (Microstructure eFlesh + Glove) :**
    Pour éviter l'effondrement ou la présence de supports internes impossibles à retirer dans le tunnel de la phalange PA12-CF, la gaine TPU du doigt est imprimée en **deux parties distinctes**, puis assemblée physiquement :
    *   **Partie tactile (Zone A — pulpe inférieure) :** Imprimée **à plat sur le plateau** (poche d'aimant vers le haut) pour permettre l'insertion de l'aimant lors de la pause d'impression. Contient la microstructure **cut-cell** générée par le pipeline eFLESH. *L'infill slicer standard est interdit dans cette zone.*
    *   **Gant structurel (Zone B & C — logement phalange et ongle) :** Imprimé **verticalement** (debout, base sur le plateau). Dans cette orientation, le tunnel interne de la phalange est vertical (comme une cheminée) et s'imprime de façon impeccable sans aucun support interne.
    *   **Assemblage des deux pièces TPU :** La pulpe (Zone A) et le gant (Zone B & C) sont collés hors de l'os à l'aide d'une colle polyuréthane flexible ou d'une micro-soudure thermique périphérique (fusion au fer à souder à 200°C), créant un gant étanche et extrêmement solide.
    *   **Montage et serrage sur la phalange PA12-CF :** 
        *   **Ajustement serré (Snug Fit) :** Le tunnel interne du gant TPU est modélisé avec un **sous-dimensionnement de 2% à 3%** par rapport à la phalange rigide PA12-CF. Le TPU s'étire à l'enfilage pour enserrer fermement l'os et éliminer tout glissement parasite.
        *   **Verrouillage axial :** Une petite vis M2 transversale à la base du doigt (ou une lèvre clipsable en TPU) verrouille mécaniquement le gant en position pour éviter qu'il ne se déchausse lors des saisies.

    > 📄 **Procédure complète détaillée :** Voir `Documentation/03_Electronique_Capteurs/GUIDE_PCB_MLX90393_et_Recyclage_WowRobo.md` **§2.6** — Workflow de découpe CAO, orientation d'impression optimale de chaque pièce, et méthode d'assemblage/séchage.

*   **Insertion de l'aimant (Pause d'impression sur la pulpe) :**
    *   La poche d'aimant (Ø3.2 mm × 1.1 mm) est générée automatiquement sur le fichier de la pulpe seule par le Stage 2 du pipeline eFLESH (`create_pouch.py`).
    *   Insérez une commande de pause (`M601` Qidi ou `M600` Marlin) à la couche de fermeture de la poche sur l'aperçu du slicer.
    *   Lors de la pause, **attendez 1 à 2 minutes** pour stabiliser la température du plateau, puis insérez l'aimant néodyme N48 (avec double pastille isolante en tissu de verre 3M 69), pôle Nord vers le bas.
    *   Relancez l'impression pour emprisonner hermétiquement l'aimant sous les dernières couches de la pulpe.

### 2.4 Le Mécanisme de Retour Passif Principal : Les Tendons Élastiques Dorsaux
Le rappel principal d'extension est assuré par un cordon élastique technique mono-brin de Ø 0.8 mm (Beadalon Elasticity) logé dans les canaux supérieurs (dorsaux) des phalanges en PA12-CF. Ces canaux, initialement prévus pour les tendons extenseurs actifs d'ORCA, guident parfaitement le cordon.

```
                  SCHÉMA DU RETOUR PASSIF DORSAL (VUE LATÉRALE)
                  
                  [Cordon Élastique Dorsal Ø0.8 mm] (Rappel principal)
                  ┌──────────────────────────────────────────────┐
                  │                                              │
      MCP         ▼             PIP                              ▼          DIP
     ┌───┐                     ┌───┐                                       ┌───┐
     │   │═════════════════════│   │═══════════════════════════════════════│   │ [Ancrage distal]
     │   │  (Passage dorsal)   │   │  (Passage dorsal)                     │   │ (Sertissage/Nœud)
     └───┘                     └───┘                                       └───┘
       ▲                         ▲                                           ▲
       └─────────────────────────┴───────────────────────────────────────────┘
                           [Tubes PTFE de guidage interne]
```

*   **Fonctionnement :** Lors de la flexion active (le servo tire sur le Dyneema DM20 palmar), le doigt s'enroule et étire le cordon élastique dorsal. Lorsque le moteur relâche la tension, l'énergie élastique accumulée tire sur la phalange distale pour réaligner le doigt à 180°.
*   **Avantage :** Ce système isole la force de rappel dans les canaux de guidage, évitant la fatigue structurelle prématurée de la gaine TPU externe et garantissant un retour complet même en présence de frictions dans les articulations.

---

## 🔩 3. Assemblage Mécanique Étape par Étape

### Étape 1 : Préparation et Pré-tensionnement des Tendons
1.  **Coupe nette :** Coupez vos tendons (Dyneema DM20 Ø1.0 mm pour toutes les lignes, force et précision) à une longueur d'environ **0.6 m** à l'aide d'une lame de scalpel neuve sous tension. *Le Dyneema DM20 est très résistant — utilisez une lame neuve bien affilée pour une coupe nette sans effilochage.*
    > 💡 **Note UV :** Contrairement au Vectran, le Dyneema DM20 présente une excellente résistance aux UV. L'acheminement interne protège toutefois le câble contre l'usure mécanique externe.
2.  **Bridage distal sans nœud :** À une extrémité du câble, insérez un manchon en cuivre de Ø1.5 mm. Repliez le câble en créant une micro-boucle (épissure Brummel si possible) et **sertissez le manchon de manière ferme** à l'aide d'une pince à sertir technique.
    > 💡 **Astuce de Sourcing (Pêche Sportive) :** Pour trouver facilement et à très bas coût ces manchons ultra-fins et la pince en France, recherchez du matériel de gréement de pêche aux carnassiers :
    > *   **Les manchons :** Sont vendus sous le nom de **"Sleeves de pêche"** simples ou doubles de **1.2 mm ou 1.5 mm** (cuivre ou laiton). Disponibles par paquets de 50 pour moins de 4 € chez Decathlon, Pecheur.com ou Amazon.fr.
    > *   **La pince :** Recherchez une **"Pince à sleeves de pêche"** (Crimping Tool) avec empreintes de micro-compression rondes (0.1 à 2 mm). Compter entre 10 € et 15 € sur Amazon.fr ou boutiques de pêche.
3.  *Alternative pour prototype :* Si vous utilisez des nœuds, réalisez un **Nœud Ashley Stopper** serré à la pince à bec plat, en laissant une queue de sécurité de 5 mm. Une micro-goutte de **Loctite Super Glue Gel** sur le nœud et sur les 5 mm de fil restants est indispensable pour figer les fibres extrêmement glissantes du Dyneema DM20.

### Étape 2 : Assemblage des Phalanges
1.  Prenez les phalanges en PA12-CF préalablement ébavurées.
2.  Insérez en force modérée (press-fit) les roulements **MR84ZZ** dans les logements circulaires de chaque chape d'articulation (2 roulements par articulation).
3.  Emboîtez les phalanges distale, médiane et proximale.
4.  Alignez parfaitement les trous et insérez les goupilles cylindriques en acier rectifié **2x6 mm** à l'aide d'un petit maillet en plastique. La goupille doit affleurer de chaque côté de la phalange sans dépasser.

### Étape 3 : Routage des Tendons dans les Doigts
1.  **Préparation des guidages :**
    *   **Canal Fléchisseur (Palmar) :** Insérez des segments de tube Téflon **PTFE** (Option A : **1.2 × 1.6 mm** ou Option B : **1.5 × 1.9 mm**) dans les canaux internes inférieurs courbes des phalanges. Les tubes PTFE doivent dépasser de 1 mm à chaque extrémité pour éviter tout contact direct du câble avec le PA12-CF.
    *   **Canal Extenseur (Dorsal) :** Laissez le fil élastique en TPU glisser directement dans les canaux supérieurs en PA12-CF (le PA12-CF a un excellent coefficient de friction naturel avec le TPU).
2.  **Routage du tendon de flexion (Dyneema) :**
    *   Passez le tendon Dyneema DM20 Ø1.0 mm préparé à l'Étape 1 depuis la pulpe distale à travers le canal inférieur vers la base du doigt à l'aide de brucelles.
    *   Vérifiez que le manchon serti distal vient se loger parfaitement dans le renfoncement de la pulpe. Tirez fermement pour valider l'ancrage.
3.  **Routage du tendon de retour élastique (Dorsal) :**
    *   Coupez une longueur d'environ **20 cm** de fil élastique de Ø 0.8 mm (fil TPU Beadalon).
    *   Réalisez un nœud d'arrêt ou sertissez un manchon à une extrémité. Logez cette butée dans la cavité dorsale supérieure de la phalange distale.
    *   Faites passer le cordon élastique à travers les canaux dorsaux des articulations DIP, PIP et MCP à l'aide de brucelles jusqu'à ce qu'il ressorte à la base du doigt.
4.  **Tensionnement provisoire du retour passif :**
    *   Tirez sur le cordon élastique dorsal pour appliquer un pré-étirement (allongement de 20 à 30 % de sa longueur au repos, correspondant à une force de **2 N à 2.5 N**).
    *   Sous cette tension, le doigt doit se redresser complètement (180°) et offrir une résistance élastique ferme lorsqu'on le plie manuellement.
    *   Bloquez temporairement le cordon à la base du doigt à l'aide d'une pince de maintien. L'ancrage définitif se fera après passage à travers la paume (Étape 4).
5.  **Identification des lignes :**
    *   **Tendon Inférieur = Fléchisseur** (Câble Dyneema DM20 Ø1.0 mm qui rejoindra les moteurs de l'avant-bras).
    *   **Tendon Supérieur = Retour Passif** (Fil élastique Ø0.8 mm qui traverse entièrement la paume et est ancré/ajusté à l'entrée du poignet).
    *   *Note sur l'extension active :* Dans cette architecture révisée sous-actionnée à 8 DOF, **aucun câble d'extension active ne traverse le poignet vers l'avant-bras**, simplifiant drastiquement le routage à travers le poignet RS-00.

### Étape 4 : Assemblage de la Paume (Palm Block) et Guidage des Élastiques
1.  Insérez les tubes PTFE de guidage (Option A : 1.2×1.6 mm ou Option B : 1.5×1.9 mm) uniquement pour les **8 canaux fléchisseurs actifs** de la paume (alésés au préalable au diamètre extérieur du tube retenu). Les 5 canaux supérieurs de la paume restent libres (sans PTFE) pour servir de canaux de traversée pour les élastiques de retour de Ø 0.8 mm.
2.  Montez les doigts sur la paume en alignant les bases de doigts avec les chapes de la paume.
3.  Insérez les axes longs en inox rectifié **3x55 mm** pour traverser l'assemblage complet de la paume et verrouiller les 5 doigts.
4.  Sécurisez les axes longs à l'aide de micro-circlips ou de points de frein-filet faible sur les filetages d'extrémité.
5.  **Routage et tensionnement des élastiques à l'entrée du poignet :**
    *   Faites passer les 5 cordons élastiques émergeant du dos des doigts à travers les 5 canaux supérieurs respectifs du bloc de paume. Utilisez un fil de tirage ou des brucelles fines pour les faire ressortir à l'arrière de la paume, au niveau de l'interface paume/poignet (entrée du poignet).
    *   **Système de blocage et réglage centralisé :** À l'entrée du poignet (interface arrière de la paume), faites passer les cordons dans la plaquette de serrage dédiée (un peigne de tensionnement ou plaque d'arrêt dotée de micro-vis de pression M2.5/M3 ou de serre-câbles à vis).
    *   Appliquez la pré-tension nominale sur chaque élastique (allongement de 20 à 30 % pour obtenir une force de rappel de **2 N à 2.5 N**), puis serrez la vis de pression correspondante de la plaquette de serrage pour bloquer le cordon.
    *   *Avantage mécanique majeur :* Ce design regroupe tous les réglages de tension à l'entrée du poignet. Il est possible de régler finement le rappel de chaque doigt de manière indépendante en desserrant simplement la vis associée à la base de la main, sans aucun démontage des doigts ni de la paume.
    *   Vérifiez que chaque doigt se rouvre de manière autonome et vive après une flexion manuelle complète. Ajustez la tension individuellement si nécessaire en agissant directement sur la vis de réglage correspondante.

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
3.  Une fois les câbles sortis du poignet à l'intérieur de la structure d'avant-bras (entre la plaque alu isogrid et les coques), distribuez-les vers leurs moteurs respectifs.

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

### 5.1 Raccordement et Dissipation du Convertisseur Buck DROK 48V→12V
Le convertisseur DROK est un module compact en boîtier alu IP67 (étanche) qui ne nécessite pas de Gap Pad :
1.  Fixez le module **DROK 48V→12V 25A** directement sur la plaque de montage en aluminium de l'avant-bras à l'aide de 4 vis M3 (trous de montage intégrés au boîtier). Le contact métal-métal assure la conduction thermique.
2.  Raccordez l'alimentation principale (Batterie 48V du robot) sur l'entrée du DROK (fils rouges +/noirs -).
3.  Raccordez la sortie 12V stabilisée sur le bus d'alimentation des servomoteurs.
4.  Insérez un **fusible réarmable PTC de 15A** sur le fil + de la sortie 12V, entre le DROK et le premier servomoteur de la chaîne.

### 5.2 Chaînage des Servomoteurs (Bus Unique SCServo)
Les moteurs Feetech partagent tous le même protocole de communication série TTL half-duplex.
1.  Chaînez les 8 moteurs en cascade (Daisy Chain) à l'aide des câbles à 3 broches fournis.
2.  Attribuez une **adresse matérielle unique (ID)** à chaque moteur via le logiciel de configuration Feetech :
    *   **ID 1 à 5 :** STS3250 (Flexion des 5 doigts)
    *   **ID 6 à 8 :** HL-3915 (Opposition Pouce, Abduction Index, Curl Palmaire)
3.  Raccordez l'extrémité de la chaîne à un unique adaptateur **USB-to-UART TTL (Feetech URT-1)** relié au calculateur principal du bras.

### 5.3 Montage des Capteurs Tactiles eFlesh en TPU (Phase V1 Actuelle)
L'ORCA/D-Hand V1 intègre désormais le système tactile magnétique 3-axes **eFlesh**, développé par le Pinto Lab de NYU. Ce système mesure à la fois les forces de compression (pression normale) et de cisaillement (friction latérale), permettant la détection fine du glissement d'objets.

#### A. Ressources Officielles & Logistique d'Achat (WowRobo vs Standard)
*   **Documentation du projet :**
    *   **Dépôt GitHub eFlesh :** [https://github.com/notvenky/eFlesh](https://github.com/notvenky/eFlesh)
    *   **Site Officiel de Documentation :** [https://e-flesh.github.io](https://e-flesh.github.io)
    *   **Référence Scientifique :** arXiv:2506.09994 (*"eFlesh: Highly customizable Magnetic Touch Sensing using Cut-Cell Microstructures"*).
*   **Ce qu'il faut acheter chez WowRobo :**
    *   **2× [eFlesh Magnetometer Board](https://shop.wowrobo.com/products/eflesh-magnetometer-board)** (1 par main pour la paume) + *1 unité de spare*. Ce PCB est en réalité un **Array multicapteurs (ReSkin/AnySkin Patch)** mesurant 20 × 20 mm et comportant 5 magnétomètres MLX90393 disposés en croix. C'est le seul format commercialisé par WowRobo.
*   **Clarification sur l'inexistence du format "Solo" officiel :**
    *   **Constat :** Il n'existe aucun module "eFlesh Solo" (10 × 10 mm) commercialisé par WowRobo ou par le Pinto Lab de NYU. Les publications académiques utilisent l'Array de 5 capteurs pour la reconstruction vectorielle ou fabriquent des prototypes sur mesure.
    *   **Solution retenue pour les Doigts (Format individuel) :** PCB custom **10 × 10 mm** fabriqué via **JLCPCB PCBA** avec 1 seul MLX90393 (boîtier QFN-16, 3×3mm) + composants passifs minimaux (2 condensateurs, connecteur JST-SH). Coût estimé : ~30–40 € pour 5 pièces assemblées, délai ~10 jours.
        > **⚠️ Note :** Les modules GY-90393 / CJMCU-90393 (~26×26mm ou ~15×15mm selon vendeur) ont été étudiés mais rejetés car trop volumineux et peu fiables sur les dimensions annoncées. Le PCB custom est la seule solution garantissant un format ≤ 12mm compatible avec la phalange distale de l'ORCA V1.
        > **📄 Guide complet JLCPCB :** Voir `Documentation/03_Electronique_Capteurs/GUIDE_PCB_MLX90393_et_Recyclage_WowRobo.md` — contient le schéma électrique, BOM, guide EasyEDA pas-à-pas, CPL et checklist DFM complète.

    ![WowRobo 5-Magnetometer Array PCB](/Users/davidsergent/.gemini/antigravity-ide/brain/ee02a0a9-cc0e-4cec-ba5d-bc241d7d624b/media__1781032802219.jpg)

    > [!WARNING]
    > **Découpe des 4 œillets de fixation du PCB 5-capteurs (Array) :**
    *   **Faisabilité :** Il est **envisageable de couper les 4 œillets métallisés des coins** car aucune piste active (alimentation ou signal) ne traverse ces zones (les pistes vertes claires s'arrêtent bien avant les cercles de fixation).
    *   **Méthode de découpe (Sans casser le PCB) :** 
        *   *À proscrire absolument :* L'utilisation d'une pince coupante ou d'une cisaille. La force d'écrasement va fissurer le substrat en fibre de verre (FR4) et sectionner les pistes internes multicouches invisibles, rendant définitivement le capteur HS.
        *   *Méthode recommandée :* Utilisez un outil rotatif (type Dremel) équipé d'un mini-disque diamant ou renforcé. Coupez lentement à l'extérieur de la zone active des composants. *Sécurité : Portez un masque de type FFP2 car la poussière d'époxy/fibre de verre est irritante pour les voies respiratoires.*
        *   *Méthode manuelle :* Fixez délicatement le PCB dans un étau (avec des mors souples en bois ou protégés par du carton) et coupez les coins avec une scie de bijoutier ou une scie à métaux à denture très fine, puis ébavurez au papier de verre grain 600.
        *   *Vérification :* Contrôlez au multimètre (test de continuité) qu'aucun court-circuit n'est apparu entre VCC et GND après découpe (des micro-bavures de cuivre peuvent ponter les plans internes sur la tranche coupée).

*   **Ce qu'il faut acheter ailleurs (Amazon, Lextronic, GoTronic, Supermagnete) :**
    *   **10× Micro-breakouts magnétomètres GY-90393** (5 par main pour les bouts de doigts, mesurant environ 15x15mm).
    *   **16× Aimants N48 ronds (Ø 3 mm × 1.0 mm d'épaisseur)** (8 par main - Supermagnete S-03-01-N).
    *   **2× Cartes de développement ESP32-S3** ultra-compactes (ex: *Seeed XIAO ESP32-S3* ou *Adafruit QT Py S3*).
    *   **1× Bobine de micro-fil émaillé** (Ø 0.15 mm ou 0.20 mm) ou micro-nappes FFC extra-plates pour le câblage interne des canaux.
    *   **Câbles de liaison JST-SH 4 broches femelles (Pas de 1.0 mm) :** Pour connecter les embases mâles blanches des PCB WowRobo sans sertissage manuel.
        *   **Option 1 (France) - GoTronic :** [Cordon Qwiic femelle-femelle 100 mm](https://www.gotronic.fr/art-faisceau-qwiic-flexible-100-mm-prt-14427-26829.htm) ou [Cordon Qwiic vers fils nus dénudés](https://www.gotronic.fr/art-faisceau-qwiic-vers-fils-nus-prt-14426-26798.htm) (recommandé).
        *   **Option 2 (France) - Lextronic :** [Câble STEMMA QT femelle-femelle 100 mm](https://www.lextronic.fr/cordon-stemma-qt-qwiic-femelle-femelle-100-mm-57688.html) ou [Câble STEMMA QT vers fils dénudés](https://www.lextronic.fr/cordon-stemma-qt-qwiic-vers-fils-denudes-57689.html).
        *   **Option 3 (France) - Kubii :** [Cordon Adafruit STEMMA QT femelle-femelle 100 mm](https://www.kubii.com/fr/cables-nappes/3739-cordon-adafruit-stemma-qt-100mm-4054-3272496302914.html).
        *   **Option 4 (Alternative économique) - Amazon.fr :** Rechercher *"Câble JST SH 1.0mm 4 broches"* (packs de 10/20 câbles femelles pré-sertis avec fils de couleurs).

#### B. Directives de Conception CAD (Lissage Esthétique & Évacuation d'Air)
Pour préserver une esthétique anthropomorphe haut de gamme (sans les structures nid d'abeille ouvertes présentées pour la recherche) et assurer une étanchéité parfaite à l'eau et à la poussière, suivez ces règles de design CAO :
1.  **Finition de Gaine Lisse (Coque continue) :** La peau lisse extérieure de la zone tactile est assurée par le paramètre `skin_thickness` du pipeline eFLESH (1.0 mm), complétée par **2 périmètres externes** du slicer (0.8 mm). Cela masque entièrement la microstructure cut-cell interne, offrant un aspect externe lisse et continu identique à une peau en silicone.
2.  **Lissage de Surface :** Pour combler les stries d'impression FDM, passez brièvement un décapeur thermique modéré (180°C à 10 cm) sur la coque TPU ou appliquez une micro-couche de vernis élastomère polyuréthane fluide pour obtenir un fini gomme mate haut de gamme.
3.  **Évitement de l'Effet Coussin d'Air (Venting Hole) :** Une coque de TPU hermétique emprisonne l'air, ce qui augmente artificiellement la rigidité de la pulpe tactile et ralentit le retour élastique. Pour y remédier, modélisez un **micro-canal de purge d'air de 0.8 mm** caché à la base de la phalange PA12-CF. Lors de la compression du doigt, l'air s'échappe de manière fluide vers le squelette interne sans aucune résistance pneumatique.
4.  **Logement Aimant & Capteur (Dimensionnement Physique eFlesh) :**
    *   **Squelette PA12-CF (Doigts) :** Évidement rectangulaire de 10 × 12 mm (ou 12 × 15 mm à ajuster selon le modèle de carte générique GY-90393 retenue) pour fixer le micro-PCB de bout de doigt.
    *   **Squelette PA12-CF (Paume) :** Évidement carré de 20 × 20 mm pour intégrer le PCB Array 5-capteurs de WowRobo.
    *   **Gaine TPU (Doigts) :** La poche d'aimant de Ø 3.2 mm × 1.1 mm est générée automatiquement par le pipeline eFLESH (Stage 2 — `create_pouch.py`). L'ajustement à 1.1 mm de profondeur maintient fermement l'aimant N48 de 1.0 mm tout en évitant tout flottement ou basculement lors des compressions de la pulpe.
    *   **Air-Gap Nominal :** Conservez une distance d'air-gap (espace libre) de **3.0 à 4.0 mm** au repos entre la face inférieure de l'aimant et le silicium du capteur MLX90393.
    *   **Justification Physique & Non-saturation :** 
        *   Un aimant néodyme N48 certifié de Ø 3 × 1.0 mm (force d'adhérence de ~190 g) possède une aimantation rémanente $B_r \approx 1.4\text{ T}$.
        *   À une distance d'air-gap de **3.0 à 4.0 mm**, le flux magnétique axial (axe Z) reçu par le capteur se situe dans une plage idéale de **14 mT à 28 mT**.
        *   Cette plage s'insère parfaitement au centre de la zone de détection dynamique linéaire du MLX90393 (configuré en gain moyen pour une dynamique de ±50 mT).
        *   *Sécurité mécanique :* Si l'air-gap était inférieur à 2.0 mm, le flux dépasserait 50 mT lors de fortes pressions, entraînant une saturation du capteur (écrêtage de la mesure). Si l'air-gap était supérieur à 6.0 mm, le signal faiblirait sous les 5 mT, dégradant le rapport signal/bruit et la résolution de la force tactile mesurée.

#### C. Étude Physique & Dimensionnement du "Mini-eFlesh" (Aimants Ø 3 × 1.0 mm N48)
L'utilisation d'aimants fins de Ø 3 × 1.0 mm au lieu des aimants massifs recommandés dans le projet académique d'origine (Pinto Lab de NYU) permet de lever le principal verrou d'intégration sur un doigt anthropomorphe :

1.  **Réduction de l'Épaisseur (Faisabilité CAO) :**
    *   Le système eFlesh universitaire utilise des cellules en TPU cubiques massives de 8.0 mm de côté.
    *   Avec des aimants de 1.0 mm d'épaisseur, la cellule TPU est aplatie à **~3.8 mm d'épaisseur** au total (1.2 mm de pulpe supérieure, 1.0 mm pour l'aimant en force, 0.8 mm de course d'écrasement/air-gap, et 0.8 mm de plancher).
    *   Avec le PCB du magnétomètre (~1.6 mm avec le chip), l'épaisseur totale du capteur n'est que de **~5.4 mm**.
2.  **Préservation Structurelle du Squelette (PA12-CF) :**
    *   Sur une phalange distale de 12.0 mm d'épaisseur (limite anthropomorphe), intégrer un eFlesh classique de 8.0 mm ne laisserait que 2.0 à 4.0 mm de matière structurelle. Sous l'immense tension du tendon (pic de 581 N sous STS3250), la phalange se briserait au niveau du pivot.
    *   Le **Mini-eFlesh** de 5.4 mm d'épaisseur préserve **6.6 mm de cœur structurel en PA12-CF**. Les parois entourant les axes en acier de 2.0 mm et les roulements MR84ZZ restent extrêmement rigides et sécurisées.
3.  **Loi Cubique de la Distance ($1/d^3$) & Qualité de Signal :**
    *   Un petit aimant N48 de Ø 3 × 1.0 mm génère un champ magnétique intrinsèquement plus faible qu'un gros bloc N52.
    *   Néanmoins, la force du champ décroît avec le cube de la distance ($1/d^3$). En réduisant l'épaisseur de la cellule, la distance au repos entre l'aimant et le silicium du magnétomètre passe de 5.0 mm à seulement 2.0 mm (facteur de réduction de 2.5×).
    *   Le champ magnétique perçu à courte distance est multiplié par $(2.5)^3 \approx 15.6$ fois, ce qui compense largement la perte de volume de l'aimant. Le rapport signal/bruit sur le MLX90393 reste optimal.
4.  **Découplage entre la Force de Mesure et la Force d'Attraction (190g) :**
    *   La spécification commerciale de l'aimant d'une force d'adhérence de ~190g (1.86 N sur plaque d'acier) **ne limite en aucun cas la plage de force mesurable** par le capteur. L'aimant n'est qu'un émetteur de champ magnétique passif.
    *   La plage de mesure (ex: 0 à 50 N) est gouvernée exclusivement par la **rigidité mécanique de l'élastomère (TPU 95A)** de la cellule cut-cell. Pour mesurer des forces élevées, il suffit d'augmenter le module d'Young `E` dans la fonction `def young(k)` du notebook `cut-cell.ipynb` afin de rigidifier les poutres de la lattice et limiter l'écrasement. Le capteur mesurera fidèlement la déformation mécanique de cette structure en TPU.

#### D. Routage & Adressage I2C Dual (Sans Multiplexeur)
Le capteur MLX90393 dispose de 2 pins d'adresse (AD0/AD1) permettant au maximum 4 adresses sur une seule ligne physique. Pour connecter 8 capteurs par main (5 doigts + 3 paume) sans ajouter de puce de multiplexage encombrante, nous utilisons les deux bus I2C natifs de l'**ESP32-S3** :

```
             SCHÉMA DU DOUBLE BUS I2C DIRECT SUR L'ESP32-S3 (8 CANAUX)
             
                  ┌─────────────────────────────────────────┐
                  │           ESP32-S3 Micro-Hub            │
                  └───────────┬─────────────────┬───────────┘
                              │                 │
           [ BUS I2C N°1 (GPIO 1/2) ]         [ BUS I2C N°2 (GPIO 5/6) ]
                    │                                 │
     ┌──────────┬───┴──────┬──────────┐       ┌──────────┬───┴──────┬──────────┐
     ▼          ▼          ▼          ▼       ▼          ▼          ▼          ▼
  [Index]    [Majeur]  [Annul.]   [Auric.] [Pouce]   [Palm-A]   [Palm-B]   [Palm-C]
   Addr:      Addr:      Addr:      Addr:    Addr:      Addr:      Addr:      Addr:
   0x0C       0x0D       0x0E       0x0F     0x0C       0x0D       0x0E       0x0F
```

1.  **Soudure :** Soudez les micro-fils émaillés émergeant des 8 phalanges/coussinets sur les bus I2C respectifs de l'ESP32-S3 (Bus 1 = Doigts externes, Bus 2 = Pouce + Triangle de Paume).
2.  **Configuration des adresses :** Reliez les pastilles d'adresse AD0/AD1 à GND ou VCC sur chaque PCB WowRobo pour attribuer la bonne adresse (0x0C à 0x0F).
3.  **Acquisition (ESP32-S3 Firmware) :** Flashez l'ESP32-S3 avec le code fourni dans `/arduino` du dépôt eFlesh. Il interroge les deux bus en parallèle à **100 Hz** et transmet le flux unifié ($B_x, B_y, B_z$ pour les 8 capteurs) en USB CDC vers le Jetson pour le calcul de force MLP en temps réel.

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
