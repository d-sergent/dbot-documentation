# 📓 JOURNAL DE BORD DU PROJET D-BOT V1

Ce document enregistre l'historique chronologique des jalons validés, des choix d'architecture et des résultats de tests terrain sur le robot D-Bot V1.

## 📅 2026-09-05 — Standardisation Équerres Torse V2 (Cornière Alu 6060-T6 30×30×3 mm, Option C Zéro Taraudage, Sourcing Blockenstock & Blueprints SVG)

### 🎯 Objectif de la session
1. **Passage au Profilé Commercial Standard (Blockenstock)** : Abandon des équerres spécifiques découpées sur mesure (40×40 mm et 20×20 mm) au profit d'une cornière marchande unique en Aluminium 6060-T6 `30 × 30 × 3,0 mm` (barre de 500 mm, réf. `30x30x3-lg500mm-corniere-alu-6060t6`, 4,80 € TTC).
2. **Débit & Dégagements Géométriques Torse V2** : Vérification des largeurs et découpe CNC NestWorks C500 : 2 équerres de Cou L = 50,0 mm (dégagement latéral de 14,5 mm sous Neck Plate de 94 mm, fourche assemblée 65 mm sur colonne de 5 mm) et 2 équerres de Waist L = 80,0 mm (dégagement de 27,5 mm sur embase de 120 mm, marge radiale de 11,5 mm par rapport au stator Ø 88 mm du moteur RS-06). Total débité : 260 mm (230 mm de réserve matière).
3. **Sécurisation Mécanique & Choix de l'Option C (Zéro Taraudage)** : Analyse de la prise de filet dans 3 mm d'alu (seulement 4,3 filets, risque de foirage > 3,2 N.m). Adoption de l'Option C : 2 perçages lisses débouchants Ø 4,30 mm par équerre, boulonnés de part en part avec vis FHC M4 × 16 mm (tête conique affleurant à 0,0 mm sur la Neck Plate) et écrous de sécurité acier zingué Nylstop M4 serrés par le dessous de l'équerre à l'établi avant montage sur colonne. Résistance acier sur acier intégrale (> 10 kN à l'arrachement), 7,1 filets en prise, démontages illimités sans usure.
4. **Préservation Stricte du Carré de Vissage CAO (30 × 30 mm)** : Trous positionnés à 12,50 mm du pli extérieur de l'équerre. Avec l'appui contre la colonne centrale de 5 mm (demi-épaisseur 2,50 mm), les coordonnées restent exactement à Y = +/- (2,50 + 12,50) = +/- 15,00 mm et X = +/- 15,00 mm (zéro modification de l'entraxe 30×30 mm existant sur la Neck Plate).
5. **Harmonisation de la Visserie, Devis & Blueprints Vectoriels** : Standardisation de la visserie de flanc sur vis CHC M4 × 20 mm traversant la colonne (écrous Nylstop M4), mise à jour du devis Blockenstock (129,36 € TTC) et Bricovis / Vis-Express (~48,00 € TTC), et actualisation intégrale des schémas SVG de fabrication.

### 📝 Réalisations & Évolutions
1. **Équerres Hautes et Basses Unifiées (Cornière Alu 6060-T6 30×30×3 mm)** :
   - Cou (Haut) : 2 équerres L = 50,0 mm, 2 trous lisses Ø 4,30 mm à plat + 2 trous lisses Ø 4,30 mm de flanc, masse 22,6 g / équerre.
   - Waist (Bas) : 2 équerres L = 80,0 mm, 3 trous lisses Ø 4,30 mm à plat + 3 trous lisses Ø 4,30 mm de flanc, masse 36,2 g / équerre.
   - Masse cumulée des 4 équerres : 117,6 g (+ ~28,0 g de visserie/écrous). Bilan de masse haut du torse actualisé à ~1 751 g (~1,75 kg).
2. **Option C Opérationnelle (Protocole d'Assemblage en 5 Étapes)** :
   - Étape 1 : Perçages Ø 4,30 mm sur cornière à la CNC C500 (zéro taraudage machine ni manuel).
   - Étape 2 : Pré-assemblage sur établi de la fourche Neck Plate + 2 équerres via 4× FHC M4 × 16 mm + 4× écrous Nylstop M4 serrés par le dessous à 2,8 ~ 3,0 N.m à la clé plate de 7 mm.
   - Étape 3 : Emmanchement du bloc fourche sur le haut de la colonne 5 mm.
   - Étape 4 : Clamping transversal via 2× vis traversantes CHC M4 × 20 mm + écrous Nylstop M4.
   - Étape 5 : Fixation du support RS-05 du cou sur la face supérieure plane.
3. **Mise à Jour Intégrale de la Documentation & des Devis** :
   - `DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md` synchronisé (§7.C.1, §7.C.2, §7.C.3, §7.D, §9.A, §9.C.2, §9.C.3, §9.C.5, §10.A, §10.B).
   - Références marchandes et normalisées ajoutées (Blockenstock réf. `30x30x3-lg500mm-corniere-alu-6060t6`, DIN 7991 / ISO 10642 pour FHC M4×16, DIN 985 / ISO 7040 pour Nylstop M4, McMaster-Carr `90576A103`).
4. **Régénération des Blueprints Vectoriels SVG** :
   - `details_equerres_liaisons_extremites_cou_waist.svg` régénéré avec géométrie 30×30×3 mm, cotes d'usinage, coupe de montage Option C et plan de débitage sur barre de 500 mm.
   - `solution_liaison_embase_cou.svg` actualisé avec la section de vissage FHC M4×16 + Nylstop M4 et CHC M4×20.

---

## 📅 2026-09-03 — Consolidation Réelle CAO Torse V2.5 (Option B Traversante, Mesures Fusion 360, Sourcing France & Protocole d'Atelier)

### 🎯 Objectif de la session
1. **Validation & Intégration de l'Option B Traversante (Inserts & Semelles)** : Alésage circulaire débouchant Ø 35,0 mm traversant sur toute l'épaisseur de 15,0 mm de l'insert, semelle éclisse 100% pleine en dessous (fermeture naturelle, étanchéité poussière) et colonne sagittale pleine.
2. **Ajustement Géométrique Réel du Tube Carré 60×60×2 mm (Fusion 360)** : Prise en compte de la longueur réelle mesurée sur CAO L = 80,05 mm, maintien du jeu axial de 1,0 mm côté semelle, portée insert/tube de 14,0 mm (93% de l'insert), entraxe perçages M5 recalculé à 65,05 mm (X = 7,5 mm et X = 72,55 mm).
3. **Extraction & Consolidation des Masses Réelles sous Fusion 360** : Mesure des masses réelles avec affectation rigoureuse des matériaux physiques (Alu 7075-T6 à 2,81 g/cm3, Alu 6060-T6 à 2,70 g/cm3) : confirmation du tube à 100,0 g et de la bride monobloc réelle à 266,9 g (anneau Ø 120 / alésage Ø 95 mm sur 18,2 mm). Bilan de masse haut du torse actualisé à ~1 605 g (~1,61 kg).
4. **Sécurisation de la Visserie & Précision Géométrique** : Validation du passage aux vis FHC M4 × 30 mm traversantes (marge de filet libre de 10 mm sous écrous Nylstop M4). Analyse trigonométrique de la fraisure conique 90° (profondeur de 1,95 mm calculée par Fusion 360 pour perçage Ø 4,50 mm, affleurement parfait à 0,0 mm).
5. **Gamme d'Atelier, Chanfreinage & Approvisionnement France** : Spécification des chanfreins d'emmanchement de 1,0 mm × 45° (insert et bossage bride), chanfrein intérieur anti-talonnage de 0,5 mm × 45° sur le tube pour appui franc à 0,0 mm, ébavurage 2 faces à 0,3 mm × 45°. Ajout du guide d'achat quincaillerie en France (Bricovis, Vis-Express, FixnVis, RS Particuliers, Amazon) avec tableau normalisé DIN/ISO.

### 📝 Réalisations & Évolutions
1. **Architecture V2.5 Consolidée (Option B Traversante)** :
   - Usinage simplifié de l'insert 15 mm en 1 passe sur table martyr (zéro poche borgne, gain -40,5 g / insert).
   - Semelles éclisses 100% pleines sous l'insert (masse 67,6 g / semelle).
   - Vis FHC M4 × 30 mm à tête fraisée à fleur (0,0 mm) et écrous frein Nylstop M4 (portée pleine continue de +8,20 mm autour du trou Ø 35 mm).
2. **Mesures Réelles Fusion 360 & Méthodologie Documentée** :
   - Tube 60×60×2 mm mesuré à 100,036 g (en parfait accord avec les 100,27 g analytiques diminués des perçages M5).
   - Bride monobloc mesurée à 266,86 g (due à la couronne Ø 120 mm / alésage Ø 95 mm sur 18,2 mm représentant 216 g). Analyse des pistes d'allègement et validation du design actuel plein pour rigidité maximale aux 120 N.m du RS-04.
   - Ajout d'une section méthodologique détaillée (Section 10.C) pour l'assignation des matériaux dans Fusion 360.
3. **Alimentation du Refroidissement Actif Épaules (Noctua 5V PWM)** :
   - Confirmation de la compatibilité directe avec le Rail 5V Always-On existant (Buck 48V -> 5V 5A). Les 2 ventilateurs (0,2 A) puisent sur la marge disponible de 3,3 A sans composant additionnel.
4. **Plans Vectoriels, Captures CAO & Dossier Technique Synchronisés** :
   - `DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md` synchronisé sur toutes les sections.
   - Blueprints vectoriels SVG (`plan_detail_semelle_eclisse_lumieres_2d.svg`, `solution_c_detail_fraisage_fhc_et_imbrication_7075.svg`, `solution_c_imbrication_inserts_15x80x80_7075.svg`) et capture CAO (`cad_insert_evidement_diametre_35mm_fusion360.png`) à jour.

---

## 📅 2026-08-30 — Adaptation Géométrique Réelle CAO Torse v71 (Traverses 15,0°, Offset 11 mm, Colonne 100 mm & Semelles Éclisses)

### 🎯 Objectif de la session
1. **Intégration de la Géométrie Réelle de l'Assemblage CAO Torse v71** : Prise en compte de l'inclinaison angulaire des tubes d'épaules à 15,0° (pitch) et du décentrement sagittal de 11,055 mm.
2. **Optimisation Profilée de la Colonne Sagittale (Alu 7075-T6, 5 mm)** : Élargissement local à 100,0 mm aux épaules avec redan asymétrique de +6,0 mm et double rayon tangent en S R = 15,0 mm (Kt ≈ 1,05), conservant 94,0 mm à la base pour l'empreinte de la Waist Plate.
3. **Validation & Recalcul RDM Global** : Démonstration du gain de rigidité au nœud d'épaule (+20,4% en flexion Pitch, I_y = 416 667 mm4, Sf = ×32,64) et décomposition vectorielle du couple RS-04 120 N.m (Roll 115,9 N.m + Yaw 31,1 N.m) absorbé par le sandwich préchargé à 19 200 N.
4. **Actualisation des Blueprints Vectoriels & Semelles Éclisses** : Mise à jour complète du plan 2D de la semelle éclisse (100 × 130 mm, insert orienté à 15,0°, 4 vis FHC M4, alésage Ø 28 mm, masse 59,0 g) et de la fiche des couples dynamométriques (§9.C.5).

### 📝 Réalisations & Évolutions
1. **Colonne Sagittale Profilée (Plat Marchand 5 × 100 × 495 mm 7075-T6)** :
   - 86,5 ~ 94,0 mm au cou (biseauté), 100,0 mm aux épaules (marge 5,20 mm à l'arête du tube 15°), 94,0 mm au waist.
   - Transitions raccordées par double rayon tangent R = 15,0 mm éliminant toute concentration de contraintes.
2. **Semelles Éclisses V2.3 (Alu 7075-T6, 5 mm, 59,0 g)** :
   - Semelle 100 × 130 mm épousant le profil de la colonne, insert carré 15 mm tourné de 15,0° (offset 11,055 mm).
   - 4 vis FHC M4 × 25 mm traversantes à tête fraisée à fleur (0,0 mm) + 4 vis CHC M5 × 25 mm traversantes sandwich.
3. **Schémas Vectoriels & Dossier Technique Synchronisés** :
   - `plan_detail_semelle_eclisse_lumieres_2d.svg` et `solution_c_sandwich_eclisse_colonne_2_parties.svg` régénérés.
   - `DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md` actualisé aux §2.B, §2.D, §5.C, §9.A, §9.C.5.

---

## 📅 2026-08-29 — Optimisation V2.2 de la Bride d'Épaule 3 Étages (Alu 7075-T6), Intégration CAO Réelle, Interface Thermique & Reranking RAG

### 🎯 Objectif de la session
1. **Audit & Optimisation RDM de la Bride d'Épaule Monobloc** : Intégration de la réduction de hauteur d'insertion (bossage 20 mm ➔ 15 mm) et de la poche centrale carrée 44×44 mm débouchante.
2. **Décomposition en 3 Étages Fonctionnels & Intégration CAO Réelle** : Clarification de la structure monolithique (Étage 1 Flasque 5,0 mm, Étage 2 Hub 13,2 mm avec alésage Ø 95 mm prof. 13,8 mm, Étage 3 Bossage 15,0 mm), et intégration des 3 captures de conception CAO Fusion 360.
3. **Isostatisme & Tolérancement de l'Interface Stator RS-04** : Définition du jeu fonctionnel axial de fond de 0,60 mm (garantissant l'appui franc primaire sur la flasque Ø 120 mm), du chanfrein d'entrée de 0,5 mm × 45° et du congé intérieur de fond R = 0,5 mm.
4. **Calibrage de la Visserie & Interface Thermique** : Confirmation du serrage M4 stator (Zone 1 : M4×12 mm, Zone 2 : M4×25 mm sur 18,2 mm de matière cumulée avec rondelles Nord-Lock M4) et protocole d'application de pâte thermique non conductrice.
5. **Modernisation & Sécurisation du Moteur RAG** : Déplacement des modèles d'Embedding et de Reranking vers un dossier local persistant (`Code/rag/models_cache`), intégration du modèle Cross-Encoder `BAAI/bge-reranker-base` avec scoring de pertinence et limitation automatique au Top 5.

### 📝 Réalisations & Évolutions
1. **Bride d'Épaule Monobloc 3 Étages (Gain net -33 g sur la paire, Sf > 50 partout)** :
   - Usinée dans le brut marchand Ø 120 × 50 mm Alu 7075-T651 (hauteur utile = 33,20 mm).
   - Poche carrée 44×44 mm R=5 mm sur 15,0 mm de profondeur débouchant sur la face du hub.
   - Vis M5 traversante verticale à X = 7,5 mm (entraxe perçages tube 60×60 = 69,5 mm).
2. **Interface Moteur RobStride RS-04 (Ø 94 mm × 13,2 mm)** :
   - Alésage de centrage Ø 95,0 mm H7 prof. 13,80 mm (0,60 mm de jeu axial de fond).
   - Conduction thermique augmentée de +60% (82 cm² d'interface métal-métal drainée vers le tube 60×60 et la ventilation forcée).
3. **Documentation & Blueprints Synchronisés** :
   - `DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md` actualisé avec toutes les cotes et captures CAO.
   - `solution_c_bride_monobloc_7075_et_vis_traversantes.svg` régénéré intégralement en 3 panneaux.
4. **Moteur RAG & Reranker Local Opérationnels** :
   - `ask_rag.py`, `index_docs.py` et `mcp_lightrag_server.py` configurés sur `Code/rag/models_cache`.
   - Reranking Cross-Encoder `BAAI/bge-reranker-base` actif (< 100 ms).

---

## 📅 2026-08-24 — Standardisation 100% Nord-Lock & Visserie Étagée RS-04, Analyse Fatigue Multirégime & RDM Choc

### 🎯 Objectif de la session
1. **Qualification de la Visserie Stator RS-04 & Respect de la Cote Borgne 6,0 mm Constructeur** : Élimination du risque de destruction des bobinages par vis trop longues suite à l'analyse du plan officiel RobStride (`Manuels/RS04User Manual260112.pdf`, p.10).
2. **Prise en Compte de la Géométrie Asymétrique Étagée de la Bride CAO** : Intégration des mesures CAO Fusion 360 (secteur mince 5,00 mm et secteur épais 18,20 mm).
3. **Standardisation Globale sur Rondelles Frein Nord-Lock M4 (ép. 1,8 mm)** : Harmonisation du couple de serrage et des longueurs de vis normalisées (M4×12 mm en zone 5 mm, M4×25 mm en zone 18,2 mm).
4. **Analyse RDM Multirégime & Réfutation Fatigue / Choc** : Démonstration de la tenue en fatigue infinie en marche continue (30 N.m, 9,05 MPa, Sf = ×14,36 à 10^9 cycles) et validation anti-voilement du tube 60×60×2 mm (b/t = 28, classe 1 compacte).
5. **Charte des Freins-Filets Chimiques** : Formalisation des règles d'emploi (Loctite 243 Bleu démontable à froid vs interdiction absolue de la Loctite 270 Rouge à chaud sur les actionneurs).

### 📝 Réalisations & Évolutions
1. **Visserie d'Épaules Sécurisée (100% Nord-Lock M4)** :
   - Zone Mince (5,0 mm) : Vis CHC M4 × 12 mm + Nord-Lock (1,8 mm) ➔ Clamping 6,80 mm ➔ Pénétration 5,20 mm (marge 0,80 mm dans trou 6 mm).
   - Zone Épaisse (18,2 mm) : Vis CHC M4 × 25 mm + Nord-Lock (1,8 mm) ➔ Clamping 20,00 mm ➔ Pénétration 5,00 mm (marge 1,00 mm dans trou 6 mm).
   - Prise de filet parfaitement équilibrée à ~5,1 mm (1,25×d) sur les 20 vis, zéro risque de talonner au fond des taraudages.
2. **Dossier Technique V2 & Guide Hybride Actualisés** :
   - Tableau McMaster-Carr normalisé (Réf `91290A154` pour M4×12, `91290A170` pour M4×25, `92620A203` pour Nord-Lock M4).
   - Guide des freins-filets ajouté (Section 9.C.3) : Loctite 243 Bleu démontable à froid (~10-15 N.m) assurant l'étanchéité et la protection galvanique acier/7075.
3. **Clarification Fatigue Multirégime** :
   - Régime 1 Marche Continue (2 Hz) : Moment 30 N.m ➔ Sf = ×14,36 (durée de vie infinie).
   - Régime 2 Pic d'Urgence (275 N.m) : Sf = ×1,93 à 10^7 cycles (hyper-conservatisme académique).
   - Confirmation de la section 5,0 mm Alu 7075-T6 (surdimensionnement complet, inutile de passer à 6 mm).

---

## 📅 2026-08-23 — Validation Finale Torse V2 Tout Métal (Alu 7075/6060), Fixation Directe Bride ➔ Stator RS-04 & Circuit Aéraulique par Tuyères 3D

### 🎯 Objectif de la session
1. **Revue Exhaustive & Audit Critique du Dossier Technique Torse V2** : Audit complet du document `01_Mecanique_et_Chassis/Torse/DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md` suite à la simplification d'épaule (suppression des cages H-bracket au profit d'une fixation directe bride monobloc Alu 7075-T6 sur le stator RS-04).
2. **Harmonisation Géométrique, Tolérances & RDM** : Élimination des résidus d'anciennes versions (tirants, écrous M4, perçages), correction des diamètres de passage (Ø 5,3 mm ISO 273 pour vis CHC M5×70), standardisation de la largeur colonne à 94,0 mm constante.
3. **Conception & Intégration du Circuit Thermo-Aéraulique** : Modélisation du flux d'expulsion annulaire (gap 2,0 mm autour du RS-04), dimensionnement des tuyères convergentes 3D (PA12-CF/TPU), ventilation globale du torse et barrière active anti-poussière.
4. **Génération des Blueprints Vectoriels SVG & RAG Sync** : Mise à jour intégrale des 7 schémas SVG du torse dans `./media/` et indexation RAG.

### 📝 Réalisations & Évolutions
1. **Architecture V2 Validée (Gain Net de 368 g vs Cages H-bracket)** :
   - **Demi-traverses d'épaules** : Tube carré commercial 60×60×2 mm Alu 6060-T6 (L = 85 mm, 106 g) emboîté sur bossage 55,8×55,8×20 mm et verrouillé par 1 seule vis traversante verticale CHC M5×70 mm (axe Z, X = 10,0 mm).
   - **Brides d'épaules monoblocs** : Usinées dans le disque brut Ø 120 × 50 mm Alu 7075-T651 (Flasque 6 mm + Bossage 20 mm + Centrage pilote Ø 95,05 mm H7) vissées directement dans les 10 taraudages M4 du stator RS-04 (PCD Ø 106 mm). Facteur de sécurité torsion friction Sf = ×2,76 (331 N.m).
   - **Colonne sagittale** : Découpée en 2 plaques 2D (5 mm) dans 1 seul plat marchand 5 × 100 × 495 mm Alu 7075-T6 (18,16 € TTC), assemblée par double éclisse sandwich 15 mm (4 vis CHC M5×25 mm). Flèche au cou en Roll = 0,121 mm (marge ×4,1 face au seuil 0,5 mm).
2. **Circuit Aéraulique Interne & Tuyère Convergente 3D** :
   - Évacuation forcée de l'air interne du torse par l'interstice annulaire de 2,0 mm (section 766,6 mm2) entourant le corps Ø 120 mm du RS-04.
   - Vitesse d'éjection v = 5,07 m/s multipliant par ~5 le coefficient d'échange convectif (h = 28 W/m2·K, T_stator maintenu à 44 °C sous 30 W continu).
   - Tuyères convergentes 3D (angle ~28°) logeant chacune 1 ventilateur 40×40×20 mm PWM haute pression statique (Noctua NF-A4x20), régulé en PWM asservi sur télémétrie CAN RS-04.
   - Effet « rideau d'air » sous surpression refoulant 100% des poussières extérieures.
3. **Mise à Jour Intégrale des Schémas Vectoriels Blueprints SVG** :
   - `solution_c_tube_carre_fixation_detaillee.svg` (fixation directe stator 10x M4, vis M5x70 en Z).
   - `solution_c_bride_monobloc_7075_et_vis_traversantes.svg` (suppression oreilles, vis unique en Z).
   - `solution_c_fixation_tube_sur_eclisse_detaillee.svg` (insert 20 mm, perçage Ø 5,3 mm).
   - `solution_c_insert_taraudages_et_liaisons.svg` (gamme d'atelier 4 étapes).
   - `concept_demi_traverse_epaule_directe.svg` (vue frontale sans cage).
   - `comparatif_usinage_traverse_monobloc_vs_assemblage.svg` (tube carré 60x60 retenu V2).
   - `paniers_batteries_hot_swap_vue_dessus.svg` (harmonisation plaque sagittale 2D).
   - `tuyere_ventilation_epaule_annulaire.svg` (nouveau schéma 4 panneaux thermo-aéraulique).

---

## 📅 2026-08-20 — Finalisation CAO Nœud Central (v62), Match-Drilling, RDM Yaw & Protocoles Anti-Corrosion

### 🎯 Objectif de la session
1. **Intégration du Design CAO Fusion 360 (Torse v62)** : Valider l'architecture du nœud central à ailes verticales d'appui, adapter les dimensions finies d'usinage (`118 × 45 × 38,5 mm`) et valider le sourcing économique en 2× chutes `40 × 50 × 120 mm Alu 7075-T6 Blockenstock`.
2. **Clarification RDM de la Répartition des Moments Fléchissants** : Lever l'ambiguïté entre le moment à la base du bassin (`275 N.m`, $S_f = \times 7,36$) et le moment au nœud central d'épaules (`131 N.m`, $S_f = \times 18,65$ ; même sous 275 N.m théorique, $S_f = \times 8,88$).
3. **Formalisation du Protocole d'Usinage « Match-Drilling »** : Documenter la séquence inviolable d'usinage en place (collage préalable des bouchons $\rightarrow$ serrage des brides $\rightarrow$ perçage/alésage direct sur NestWorks C500 $\rightarrow$ goupillage Inox scellé $\rightarrow$ montage des moteurs RS-04 à la fin).
4. **Protection Anti-Corrosion Galvanique DIY** : Spécifier les 3 barrières diélectriques simples d'atelier (ruban Kapton $50\ \mu\text{m}$ extérieur + colle époxy intérieure + scellement Loctite 243 des goupilles rectifiées Inox ISO 8734).

### 📝 Réalisations & Évolutions
1. **Consolidation Géométrique des Demi-Coquilles** :
   - Dimensions finies : $118,0\text{ mm}$ (longueur Y) × $45,0\text{ mm}$ (largeur X) × $38,5\text{ mm}$ (hauteur Z hors-tout avec aile de $17,5\text{ mm}$).
   - Perçages : 4× vis M6 verticales de pincement ($Y = 17$ et $101\text{ mm}$), 4× vis M4 horizontales d'ancrage colonne ($Z = \pm 30\text{ mm}$, $Y = 14, 44, 74, 104\text{ mm}$), goupille $Z$ décalée à $X = +12\text{ mm}$, $Y = 59\text{ mm}$.
2. **Génération & Mise à Jour des Schémas Vectoriels Blueprints SVG** :
   - `plan_percage_demi_coquille_noeud.svg` (plan d'usinage 3 panneaux aux cotes réelles $118\text{ mm}$).
   - `comparatif_decoupe_colonne_bride.svg` (comparatif coupe droite $Z = +22\text{ mm}$ vs découpe en arche).
   - `noeud_demi_coquilles_bride.svg` (nomenclature et sourcing 2× $40\times 50\times 120\text{ mm}$ mis à jour).
   - Intégration de la capture CAO écorchée `torse_v62_eclate_squelette_epaule.png` illustrant le dégagement de la broche Z sur la bride d'épaule.
3. **Calcul de Rigidité en Torsion Yaw** :
   - Déformation angulaire du tube carbone Ø 30 mm sous couple crête RS-06 ($60\text{ N.m}$) : $\Delta\theta_{\text{yaw}} \approx 1,91^\circ < 2,0^\circ$, garantissant une stabilité dynamique optimale pour l'estimation d'état IMU/SLAM.
4. **Standardisation sur Goupilles Rectifiées Inox ISO 8734** :
   - Remplacement des goupilles élastiques fendues par des goupilles rectifiées trempées Inox A1/A2 Ø 4,0 mm m6 × 40 mm (précision $\pm 0,005\text{ mm}$, zéro couple galvanique avec le carbone $\Delta V < 0,05\text{ V}$, $S_f = \times 9,73$).

---

## 📅 2026-08-13 — Audit Complet d'Ingénierie, Validation Constructeur RS-04 & Harmonisation Globale du Dossier Torse

### 🎯 Objectif de la session
1. **Validation Constructeur des Fixations RS-04** : Analyse rigoureuse du plan officiel constructeur RobStride (`Manuels/RS04User Manual260112.pdf`, page 10) pour confirmer la profondeur borgne ($5\text{ à }6\text{ mm}$) et valider les longueurs de vis d'épaule.
2. **Audit Mécanique & Vérification de Cohérence Globale** : Relire l'intégralité du dossier technique (`ANALYSE_STRATEGIE_Torse.md`, `ETUDE_Dimensionnement_Colonne_Vertebrale.md`, `GUIDE_Fabrication_Torse_D-Bot_Hybride.md`) pour éliminer toute incohérence, résidu d'anciennes versions, coquille de perçage ou erreur de couple.
3. **Harmonisation de la Visserie & Perçages CNC** : Spécifier la partition exacte de la visserie (10× vis M4×10 avant, 4× vis M4×10 arrière hors bride, 6× vis M4×25 bride épaule 13.20 mm), corriger les diamètres de perçages de passage à Ø 4.3 mm (ISO 273 Moyen) et harmoniser le serrage dynamométrique à 3.0 N.m.

### 📝 Réalisations & Évolutions
1. **Validation Constructeur RobStride RS-04 (PCD Ø106 mm × 10 vis M4)** :
   - Conformité Page 10 Manuel RS-04 : Taraudages borgnes $5\text{ mm Min à }6\text{ mm Max}$.
   - Face Avant : **10× Vis CHC M4 × 10 mm** (plaque 5.0 mm + rondelle 0.8 mm $\rightarrow$ pénétration $4.20\text{ mm}$, garde $1.80\text{ mm}$ au fond).
   - Face Arrière : **4× Vis CHC M4 × 10 mm** (hors bride) + **6× Vis CHC M4 × 25 mm** (traversant flasque bride $13.20\text{ mm}$ + plaque $5.00\text{ mm}$ + rondelle $0.8\text{ mm} \rightarrow$ pénétration $5.20\text{ à }6.00\text{ mm}$).
2. **Harmonisation Globale & Élimination des Résidus Historiques** :
   - **Perçages de passage M4** : Remplacement de tous les "Ø 3.3 mm" (taraudage) par **Ø 4.3 mm (ISO 273 Moyen)** pour les perçages de passage de vis dans les plaques et brides alu.
   - **Couple de serrage M4 de pincement** : Correction des mentions résiduelles de "6 N.m" à **3.0 N.m (classe 8.8)** et **3.5 N.m (classe 10.9)** avec écrous Nylstop DIN 985 et rondelles Nord-Lock (zéro Loctite liquide).
   - **Goupille d'épaule** : Harmonisation de toutes les références à **Goupille élastique Mécanindus Ø 4.0 mm × 40 mm (ISO 8752 Inox)** (s'aligne à fleur Ø 40 mm).
   - **Tirants de Roll Waist Plate** : Suppression des perçages obsolètes à ±60 mm sur la Waist Plate dans le workflow, la rigidité Roll étant reprise à 100% par la cage H-Bracket (tirants M5 diagonaux $R = 72\text{ mm}$ à 23.4°).
   - **Terminologie** : Purge définitive du terme "isogrid" au profit de "plaque sagittale à lumières 2D (Option B)".
   - **Statut Carter Acier E470** : Classé explicitement comme solution de secours/archive, la cage H-Bracket Alu 7075-T6 étant la solution active standard V1.
3. **Restructuration Globale & Archivage Propre** :
   - Création du document d'archive officiel [`01_Mecanique_et_Chassis/Torse/00_Archives_Recherche/ETUDE_ARCHIVEE_Carter_Epaule_Acier_E470.md`](../01_Mecanique_et_Chassis/Torse/00_Archives_Recherche/ETUDE_ARCHIVEE_Carter_Epaule_Acier_E470.md).
   - Réécriture intégrale et linéaire du [`GUIDE_Fabrication_Torse_D-Bot_Hybride.md`](../01_Mecanique_et_Chassis/Torse/GUIDE_Fabrication_Torse_D-Bot_Hybride.md) : la solution d'épaule finale H-Bracket 7075-T6 est promue en Section 4, supprimant toute ambiguïté sur les approvisionnements et les gammes d'usinage C500.
4. **Optimisation Géométrique du Nœud Central Demi-Coquilles** :
   - Réduction de l'épaisseur de paroi de demi-bride à 6.0 mm au dos du demi-alésage R15 -> hauteur totale du nœud ramenée de 60.0 mm à **42.0 mm** (+18 mm d'espace vertical libre dans le torse, gain de -115 g).
   - Décalage latéral de la goupille de sécurité à X = +12.0 mm pour contourner sans conflit la plaque sagittale centrale (5.0 mm) et standardisation sur la référence d'épaule **Goupille élastique Mécanindus Ø 4.0 mm × 40 mm (ISO 8752 Inox)**.
5. **Validation du Sourcing Matière des Bouchons Tube Carbone** :
   - Validation de la référence Blockenstock **[Ø 30×500 mm Alu 7075-T651 filé](https://www.blockenstock.fr/c-30x500mm-alu-7075-file-t651-c2x21035319)** au tarif de **16.20 EUR TTC (13.50 EUR HT)** pour usiner les 2 bouchons anti-écrasement Ø 26.0 ext / Ø 18.0 int × 34.5 mm.
6. **Validation du Sourcing Matière des Demi-Coquilles du Nœud Central** :
   - Validation de la référence Blockenstock **[Plat méplat 25×50×500 mm Alu 7075-T6](https://www.blockenstock.fr/25x-50x500mm-alu-7075-t6-c2x21792953)** au tarif de **39.38 EUR TTC (32.82 EUR HT)** pour usiner les 2 demi-brides 120×45×21 mm (Bride Supérieure et Bride Inférieure).
7. **Spécification Explicite du Split Gap au Nœud Central** :
   - Intégration dans le guide de la consigne d'usinage de demi-alésage à **14.5 mm de profondeur** (surfaçage Z = -0.5 mm) garantissant un **Split Gap de 1.0 mm net (0.8 à 1.0 mm)** entre les demi-coquilles assemblées pour convertir 100% de la force des 4 vis M6 en pression radiale directe (6.3 MPa) sur le composite.
8. **Justification RDM Formelle de l'Épaisseur de 6.0 mm au Nœud Central (§12 ETUDE)** :
   - Calcul RDM complet sous précharge maximale des 4 vis M6 (30 000 N) : Sigma = 93.75 MPa (Sf = × 4.91 en Alu 7075-T6).
   - Calcul sous choc dynamique Pitch 131 N.m : Sigma = 24.26 MPa (Sf = × 18.96).
   - Calcul matage goupille Ø 4.0 mm : Sigma_bearing = 43.06 MPa (Sf = × 16.03).
9. **Intégration du Manchon Central Anti-Écrasement & Mise à Jour Blueprint SVG** :
   - Ajout d'un 3ème insert tourné en **Alu 7075-T651 (Ø 26.0 ext / Ø 18.0 int × 45.0 mm, 35 g)** positionné au centre du tube carbone sous le nœud, usiné dans la barre de 500 mm existante (coût 0 €).
   - Mise à jour intégrale du schéma vectoriel [`noeud_demi_coquilles_bride.svg`](../01_Mecanique_et_Chassis/Torse/media/noeud_demi_coquilles_bride.svg) : affichage de la hauteur 42.0 mm (dos 6.0 mm), du Split Gap 1.0 mm, de l'insert central, de la goupille Ø 4×40 mm décalée à X = +12.0 mm et de la nomenclature officielle.
10. **Découplage Isostatique en Z au Cou & Refonte Blueprint SVG Liaisons d'Extrémités** :
   - Spécification des **lumières oblongues verticales (4.3 × 6.5 mm, ±1.0 mm en Z)** sur les cornières L sandwich reliant la plaque sagittale à la Plaque de Cou, pour interdire toute traction parasite vers le haut sur la Bride Supérieure et protéger le Split Gap (1.0 mm).
   - Formalisation du **protocole de serrage séquentiel en 5 étapes** (Phase 4 du Guide).
   - Refonte complète du blueprint vectoriel [`solution_liaison_embase_cou.svg`](../01_Mecanique_et_Chassis/Torse/media/solution_liaison_embase_cou.svg) (vue en coupe, séquence de montage et comparatif L-Brackets vs Tenon/Mortaise).

---

## 📅 2026-08-09 — Validation Mécanique Finale & Sourcing de l'Épaule (Cage H-Bracket 7075-T6, Évidement Ø95mm, Pincement 3.0 N.m & 2 Paniers Hot-Swap)

### 🎯 Objectif de la session
1. **Validation Mécanique du Design Quasi-Final Fusion 360 (Screenshots epaule1 à epaule9)** : Analyser et valider l'assemblage réel d'épaule composé de 2 plaques H-bracket identiques (5,0 mm Alu 7075-T6) + bride d'ancrage tube (48.20 mm Alu 7075-T651) + 2 tirants M5 axiaux à 23.4°.
2. **Prise en compte de l'évidement central Ø95 mm (epaule9.png)** : Calculer la résistance mécanique de la couronne annulaire de 12.5 mm de largeur radiale et évaluer le gain de masse.
3. **Validation de l’Assemblage 100% Mécanique Sans Colle** : Quantifier le serrage dynamométrique à froid (vis CHC M4 à 3.0 N.m, écrous Nylstop / rondelles Nord-Lock, sans Loctite) et le rôle de la goupille Ø4 mm Mecanindus sur le bouchon alu interne (Ø26/18×34.5 mm).
4. **Rétablissement Officiel des 2 Paniers Batterie Latéraux Hot-Swap** : Confirmer que la cage H-bracket libère l'espace sous les épaules et valider l'architecture V1 des 2 paniers batterie avec basculement ORing.
5. **Nettoyage et Normalisation du Repository** : Supprimer les fichiers orphelins du dossier `./media/` et mettre à jour le schéma vectoriel Blueprint SVG.

### 📝 Réalisations & Évolutions
1. **Validation par Calcul RDM de l'Évidement Ø95 mm (Gain de -400 g sur le torse)** :
   - Contrainte de bending dans la couronne annulaire 5,0 mm 7075-T6 : $\sigma_{\text{flexion}} = 43.1\text{ MPa}$ ($S_f = \times 10.7$ ✅).
   - Flexion des oreilles cylindriques : $\sigma = 8.7\text{ MPa}$ ($S_f = \times 53.1$ ✅).
   - Pince radiale de matière sur trous M4 PCD Ø106 mm : 3.35 mm nets de matière pleine, contrainte de matage $\sigma_{\text{bearing}} = 11.3\text{ MPa}$ ($S_f = \times 61.0$ ✅).
   - Gain de masse : $35.4\text{ cm}^3$ évidés par plaque, soit $-100\text{ g/plaque}$ ($\mathbf{-398.4\text{ g}}$ d'allégement au total sur le torse).
2. **Caractérisation de la Liaison Tube-Bride 100% Mécanique (Zéro Colle Époxy)** :
   - Portée d'encastrement $L = 35.0\text{ mm}$ ($L/D = 1.17$, parfait respect ISO).
   - Couple dynamométrique préconisé à 3.0 N.m (vis 8.8) ou 3.5 N.m (vis 10.9) $\rightarrow$ force radiale cumulée de $780\text{ kgf}$ ($7\,645\text{ N}$) $\rightarrow 27.0\text{ N.m}$ transmis par friction pure.
   - Verrouillage mécanique anti-vibration par écrous Nylstop M4 + rondelles Nord-Lock / Schnorr dentelées (zéro Loctite liquide).
   - Procédure de serrage à la clé dynamométrique alterné en 3 passes (1.5 N.m $\rightarrow$ 2.5 N.m $\rightarrow$ 3.0 N.m).
   - **Spécification de la Boulonnerie (Fixation Stator RS-04, Bride d'Épaule, Tirants M5 & Pincement M4) & Perçage CNC** : Fixation stator directe (10× vis CHC M4 × 10 mm ISO 4762 sur face avant + 4× vis CHC M4 × 10 mm sur face arrière hors bride, engagement 4.2 mm, profondeur borgne max 6.0 mm validée constructeur), fixation bride d'épaule + stator (6× vis CHC M4 × 25 mm traversant flasque 13.20 mm + plaque arrière 5.0 mm, engagement 5.2–6.0 mm), vis CHC M5 × 60 mm (ISO 4762 classe 8.8 / 10.9) pour empilement 49.0–51.0 mm (saillie bague nylon +2.4 mm), vis CHC M4 × 18 mm (ou M4 × 20 mm) pour pincement radial sur bloc 11.0 mm (trous traversants **Ø 4.3 mm ISO 273 Moyen**, chanfreins 0.5 mm × 45°), goupille élastique Mécanindus Ø 4.0 mm × 40 mm (ISO 8752 / DIN 1481 Inox à fleur), rondelles DIN 125A (M4/M5), écrous Nylstop DIN 985 (M4/M5), trou tirant **Ø 5.5 mm (ISO 273 Moyen)**. Règle CAO critique : fente de pincement fixée à **1.0 mm net (±0.1 mm)** pour interdire la butée prématurée alu-alu d'une fente à 0.1 mm. Intégration du tutoriel d'importation directe 3D STEP M4/M5/Goupille via l'outil McMaster-Carr de Fusion 360.
3. **Mise à Jour des 9 Illustrations CAO & Génération du Blueprint SVG** :
   - Mise à jour du blueprint vectoriel [`hbracket_rs04_quasi_final_blueprint.svg`](./media/hbracket_rs04_quasi_final_blueprint.svg) intégrant l'évidement Ø95 mm et le tableau récapitulatif.
   - Remplacement complet des 8 anciens visuels par les 9 captures d'écran CAO réelles (`epaule_cao_1_vue_ensemble.png` à `epaule_cao_9_evidement_central_95mm.png`) illustrant toutes les cotations au §3.E du Guide.
   - Suppression de 8 fichiers orphelins inutiles dans `./media/`.
4. **Rétablissement Officiel des 2 Paniers Batteries Latéraux Hot-Swap (§8)** :
   - Confirmation que l'espace sous les épaules est 100% libre avec les tirants M5 à 23.4°.
   - Validation de l'architecture V1 480–576 Wh ($2\times 12\text{S}$) avec basculement ORing sans coupure (< 0.5 ms).
5. **Mise à Jour Globale de la Documentation (`ETUDE_Dimensionnement_Colonne_Vertebrale.md` & `GUIDE_Fabrication_Torse_D-Bot_Hybride.md`)**.

---

## 📅 2026-08-01 — Finalisation de la Fabrication C500 du Torse (Perçage Z, Split Gap 0.8-1.0mm & Adoption Officielle Option B 2D)

### 🎯 Objectif de la session
1. **Validation & Sourcing NestWorks C500** : Spécifier la zone de travail réelle (230 × 213 × 128 mm), le 4ème axe rotatif (Ø3–80 mm) et établir l'outillage pour le sous-système tube.
2. **Correction des axes du Nœud d'Épaule** : Corriger la direction du perçage de la goupille du nœud central en axe Z (vertical) de haut en bas sur 60 mm de profondeur (15mm Alu Sup + 2mm CFRP + 26mm vide + 2mm CFRP + 15mm Alu Inf), réalisable à 100% en 3 axes direct sur la C500.
3. **Mise à l'état de l'art du pincement (Split Gap)** : Définir la dépouille de serrage de 0,8 mm à 1,0 mm au plan de joint des brides (surfaçage CAM Z = -0.4 à -0.5 mm) pour bannir la butée alu/alu et garantir 100% de la force radiale sur le composite sans écrasement (serrage 6-8 N.m, 15-18 MPa).
4. **Adoption Officielle de l'Option B (Lumières 2D Traversantes)** : Valider l'Option B pour la colonne vertébrale (plaques 5,0 mm Alu 6061-T6 évidées en 2D) face à l'Isogrid (Option C), avec recalcul RDM complet ($I_{x,\text{net}} = 506\,667\text{ mm}^4$, contrainte $\sigma_{\text{max}} = 26,05\text{ MPa}$, facteur de sécurité $S_f = \times 9.21$).

### 📝 Réalisations & Évolutions
1. **Blueprints Vectoriels SVG Générés dans `./media/`** :
   - `noeud_demi_coquilles_bride.svg` : Vue en coupe frontale Y-Z et vue de dessus X-Y avec la goupille verticale en Z (60 mm traversant) et le tableau récapitulatif des forces.
   - `comparatif_plaques_colonne.svg` : Diagramme comparatif 3 panneaux (Option A Plaque pleine, Option B Lumières 2D, Option C Isogrid).
   - `plaques_colonne_2d_evidees.svg` : Plan de fabrication détaillé des 2 plaques (Supérieure biseautée 142.67 mm et Inférieure rectangulaire 290.0 mm).
2. **Mise à Jour du Document de Dimensionnement (`ETUDE_Dimensionnement_Colonne_Vertebrale.md`)** :
   - Formules d'inertie et contraintes révisées pour l'Option B ($\sigma_{\text{max, base}} = 26,05\text{ MPa}$, $S_f = \times 9.21$, flèche $\Delta = 0,08\text{ mm}$).
   - Tableau de décision et intégration des visualisations vectorielles.
3. **Mise à Jour du Guide Torse Hybride (`GUIDE_Fabrication_Torse_D-Bot_Hybride.md`)** :
   - Adoption formelle de l'Option B comme architecture officielle (355 g au total, 15 min d'usinage sur C500, 0% risque de voilement).
   - Ajout des règles CAM pour le Split Gap de 0.8-1.0 mm et la plage de couple 6-8 N.m.
4. **Actualisation de la Documentation CNC (`22_Usinage_CNC_C500.md`)** :
   - Mise à jour des spécifications officielles C500 (course 230 × 213 × 128 mm) et du perçage goupille Z en 3 axes direct.

---



## 📅 2026-07-28 — Refonte de la Structure Cruciforme du Torse (Carter Monobloc Alu, Colonne Sagittale Isogrid 5mm & Schémas SVG Vectoriels)

### 🎯 Objectif de la session
1. **Refonte du carter d'épaule RS-04** : Remplacer l'ancien manchon arrière à lip intérieur par un carter monobloc CNC Alu 6061-T6 à insertion frontale (Front-Loading), cerclage 360°, flasque arrière de 6 mm et socket pour tube carbone Ø30 mm.
2. **Normalisation des schémas techniques (`AGENTS.md`)** : Interdire les schémas ASCII et Mermaid pour la mécanique, imposer la génération systématique de blueprints vectoriels SVG haute qualité dans `./media/` et supprimer la syntaxe LaTeX dans les textes.
3. **Dimensionnement & Validation de la colonne vertébrale** : Réaliser l'étude mécanique de dimensionnement de la plaque sagittale Isogrid à partir des relevés CAO réels Fusion 360 v25 (86,5 mm au cou, 127,2 mm aux épaules, 127,7 mm à la taille).
4. **Ingénierie des liaisons d'assemblage** : Résoudre les fixations haute/basse (équerres L-Brackets en sandwich) et le nœud d'intersection cruciforme (bride 2 pièces Mâle/Femelle avec centrage par fût Ø38 mm et manchons 360° haut/bas).

### 📝 Réalisations & Évolutions
1. **Carter Monobloc d'Épaule (Option B Front-Loading)** :
   * Validation de l'insertion frontale du moteur RobStride RS-04 par la face extérieure de l'épaule.
   * Contact direct métal-métal 100% entre le stator et la flasque alu 6 mm pour une dissipation thermique maximale (~167 W/m.K) et l'absence de fluage sous précharge des 8 vis CHC M5.
2. **Génération de 10 Blueprints Vectoriels SVG dans `./media/`** :
   * `structure_cruciforme.svg` (Vue de face et de dessus du squelette cruciforme).
   * `motif_isogrid_diamant_45.svg` (Motif diamant ±45° avec coupe double-face symétrique en I).
   * `bride_tube_carbone_eclatee.svg` & `bride_tube_carbone_eclatee_3d.png` (Vue éclatée coaxiale 2D et rendu 3D Isométrique).
   * `bride_tube_carbone_coupe.svg` (Coupe longitudinale A-A du détail d'ancrage carbone/carter alu).
   * `solution_liaison_embase_cou.svg` (L-Brackets en sandwich pour embase cou et waist plate).
   * `noeud_intersection_cruciforme.svg` (Assemblage 2 pièces Mâle/Femelle avec centrage Ø38 mm et pincement 360°).
3. **Création du document d'étude dédié ([ETUDE_Dimensionnement_Colonne_Vertebrale.md](./01_Mecanique_et_Chassis/Torse/ETUDE_Dimensionnement_Colonne_Vertebrale.md))** :
   * Validation de l'épaisseur de tôle brute de **5,0 mm** Alu 6061-T6 (poches 1,75 mm de chaque côté + voile résiduel 1,5 mm).
   * Contrainte dynamique maximale à la base : **36,8 MPa** (marge de sécurité $S_f = 6.5$).
   * Flèche globale au cou sous choc de 220 Nm : **~0.11 mm** (rigidité absolue).
4. **Mise à jour des règles `AGENTS.md`** :
   * Règle stricte imposant les schémas vectoriels SVG thématiques sombres dans `./media/`.
   * Interdiction stricte de la syntaxe mathématique LaTeX dans tous les textes et documents markdown.
5. **Mise à jour complète du Guide de Fabrication ([GUIDE_Fabrication_Torse_D-Bot_Hybride.md](./01_Mecanique_et_Chassis/Torse/GUIDE_Fabrication_Torse_D-Bot_Hybride.md))**.

---

## 📅 2026-07-25 — Diagnostic & Résolution du Crash Mémoire Mac MLX (Port 8002) et Validation Architecture Direct Cloud

### 🎯 Objectif de la session
1. **Diagnostic du plantage Mac** : Identifier la cause de la saturation mémoire RAM/Metal GPU lors de l'exécution de `companion_server_tts_mac.py`.
2. **Assainissement & Sécurisation MLX** : Implémenter le bridage de la génération Qwen3-TTS et la libération mémoire GPU Metal.
3. **Validation Terrain Jetson Direct Cloud** : Valider l'exécution complète du flux ASR Groq + Gemini LLM (sur Jetson) + Qwen3-TTS MLX (sur Mac M1 Max) via `test_jetson_direct_cloud.py`.

### 📝 Réalisations & Évolutions
1. **Résolution des fuites mémoire MLX GPU (`companion_server_tts_mac.py` & `companion_server.py`)** :
   - **Bridage de génération** : Ajout explicite de `repetition_penalty=1.1`, `max_tokens=1024`, `stream=True`, `streaming_interval=0.4` et `lang_code="french"` pour éviter que Qwen3-TTS n'entre dans une boucle de génération infinie sur GPU Metal.
   - **Vidange du cache GPU Metal** : Implémentation d'une routine de nettoyage `cleanup_memory()` exécutant `mx.metal.clear_cache()` et `gc.collect()` après chaque phrase synthétisée.
   - **Verrouillage d'inférence (`asyncio.Lock`)** : Ajout d'un verrou `tts_lock` empêchant les requêtes concurrentes de corrompre l'état du modèle MLX.
   - **Suppression des threads orphelins** : Remplacement du thread `threading.Thread` en tâche de fond par une consommation itérative contrôlée via `loop.run_in_executor`.
2. **Correctif du script de lancement (`start_companion_server.sh`)** :
   - Actualisation dynamique de la vérification PID après l'ouverture effective du port Uvicorn.
3. **Validation 100% de la chaîne "Jetson Direct Cloud" (`test_jetson_direct_cloud.py`)** :
   - ASR Groq Cloud Direct : **510 ms** (Whisper Large v3 Turbo).
   - LLM Gemini 2.0 Flash Direct : **0 ms** (1er token).
   - TTS Stream Mac GPU Metal : Synthèse fluide 24000 Hz lue sur l'enceinte ReSpeaker (2,2s d'audio) avec retour automatique à l'écoute VAD.
   - Zéro fuite RAM / zéro plantage système sur Mac M1 Max.
4. **Création & Évaluation des Voix Cloud Edge-TTS (`test_edge_tts_voices.py`)** :
   - Qualification des voix françaises Microsoft Neural : `fr-FR-HenriNeural` (314 ms, voix homme calme), `fr-FR-DeniseNeural` (329 ms, femme claire), `fr-FR-EloiseNeural` (328 ms) et `fr-FR-RemyMultilingualNeural` (664 ms).
5. **Déploiement du Mode 3 "Jetson Edge Cloud" (`test_jetson_edge_cloud.py`) — ADOPTÉ PAR DÉFAUT** :
   - **Architecture 100% Autonome Jetson** : ASR Groq Cloud + LLM Gemini 2.0 Flash Direct Jetson + TTS Microsoft Edge-TTS (`fr-FR-HenriNeural`) exécuté intégralement sur la Jetson sans aucune dépendance serveur Mac.
   - **Correction du format Audio** : Ajout du convertisseur automatique `_convert_mp3_to_wav()` (MP3 ➔ WAV 24 kHz Mono via `ffmpeg`/`mpg123`/`sox`) rendant le flux Edge-TTS 100% compatible avec l'utilitaire `paplay` et l'amplificateur JST du ReSpeaker.
   - **Adoption par défaut** : Ce mode devient la solution nominale de production du projet D-Bot V1 (0€, illimité, zéro charge Mac, latence ~350 ms).

---

## 📅 2026-07-24 — Audio Gaze Tracking, Clarification EEPROM RS-05 & Pipeline Streaming Audio Déporté (1.55s)

### 🎯 Objectif de la session
1. **Audio Gaze Tracking (`audio_gaze.py`)** : Asservir la direction DoA (0–359°) du ReSpeaker XVF-3800 sur la rotation Pan du cou (-80° à +80°).
2. **Clarification Moteurs RS-05** : Vérifier la persistance des bornes d'angle dans l'EEPROM des moteurs RobStride RS-05 et mettre à jour la documentation.
3. **Pipeline Audio Déporté `dbot_next`** : Déboguer la chaîne conversationnelle interactive ASR + LLM + TTS (`test_companion_streaming.py` Jetson ↔ `companion_server.py` Mac) et résoudre les interruptions/hallucinations.
4. **Profilage & Optimisation de Latence** : Mesurer chaque étape du pipeline et réduire la latence perçue pour une conversation fluide.

### 📝 Réalisations & Évolutions
1. **Module Audio Gaze Tracking (`dbot/behaviors/audio_gaze.py` & `test_audio_gaze.py`)** :
   - Mappage linéaire et continu de la DoA ReSpeaker (0° à 359°) vers l'angle Pan (-80° à +80°).
   - Zone morte de 12.0° et filtrage d'hystérésis pour éliminer les petits mouvements brusques.
   - Validation 100% de la suite de tests unitaires et vérification des verrous de bridage logiciel `clamp_pan` / `clamp_tilt`.
2. **Clarification Matérielle RS-05 (Doc 32 & 43)** :
   - Confirmation que les moteurs FOC RobStride RS-05 ne possèdent aucun registre EEPROM pour les limites d'angle.
   - Formalisation du bridage logiciel à 3 niveaux (Python `clamp_pan/tilt`, URDF soft limits, controller bounds).
   - Suppression des notations LaTeX mathématiques dans les docs textuelles conformément aux règles du projet.
3. **Correctifs Majeurs Stack Audio `dbot_next` (`companion_server.py` & `audio_io_streaming.py`)** :
   - **Bug WebSocket Starlette** : Correction du parsing ASGI `message.get("bytes")` qui interceptait par erreur les messages texte JSON `start` et `end`.
   - **Bug Mono / Stéréo** : Suppression du double désentrelacement stéréo/mono dans le serveur Mac (`AudioIOStreaming` extrayant déjà le canal gauche 16 kHz mono).
   - **VAD RMS & Pre-roll** : Calibration dynamique du bruit de fond (`seuil = max(bruit_rms * 3.0, 150)`), pre-roll de 5 chunks de silence et réduction de la fenêtre de fin de phrase de 20 chunks (3.2s) à 10 chunks (1.6s).
   - **Verrouillage Anti-Auto-Écoute** : Mute temporaire de la VAD pendant la réponse du robot (`speaking`/`thinking`) et purge du buffer audio dans `on_end()` pour éliminer l'effet d'auto-interruption du haut-parleur.
4. **Intégration Groq Cloud ASR & Profilage de Latence** :
   - Intégration de **Groq Whisper Large v3 Turbo** Cloud (< 300 ms) via `GROQ_API_KEY` dans `.env` avec fallback automatique sur **Faster-Whisper `small`** local CPU.
   - Création du script de gestion propre `Code/dbot_next/scripts/start_companion_server.sh` (`--start`, `--restart`, `--stop`, `--status`, `--logs`).
   - Latence totale mesurée (fin de parole ➔ 1er paquet audio) : **1553 ms** en local (Faster-Whisper `small`), réduisant la latence initiale de **57.7%** !

---

## 📅 2026-07-22 — Stabilisation I/O Motorbridge Web UI & Cou Pan/Tilt

### 🎯 Objectif de la session
1. Éliminer les blocages du serveur HTTP Motorbridge Web UI et sécuriser les threads de mouvement du cou RS-05.
2. Fluidifier les curseurs sliders HTML/JS et désactiver les requêtes réseau superflues.
3. Éliminer les timeouts CAN et verrous bloquants (`self.lock`).

### 📝 Réalisations & Évolutions
1. **Refactoring Multithread Web UI (`web_ui.py`)** :
   - Migration de toutes les opérations d'I/O CAN (`detect`, `get_state`, `enable`) hors du verrou `self.lock`. `self.lock` ne protège plus que l'écriture ultra-courte (< 1 ms) des variables Python partagées.
2. **Optimisation du Protocole CAN (`neck.py`)** :
   - Passage des paramètres de configuration (`run_mode`, `limit_spd`, gains PID) en mode *fire-and-forget* (`write_param_no_ack`).
   - Réduction du temps d'exécution d'activation `enable()` de ~9s à ~1.5s.
3. **Robustesse de la Télémétrie** :
   - Appel de `detect(update_active=False)` pendant la télémétrie périodique pour éviter toute remise à zéro intempestive de `active_motors` pendant un déplacement.
   - Suppression du bruit de logs `DEBUG` de `python-can` et `robstride` avec élévation des logs de cycle de vie des threads de mouvement en `INFO`.

---

## 📅 2026-07-22 — Qualification de la Triade Visuelle Sémantique & Fusion Spatiale 3D OAK-D Pro

### 🎯 Objectif de la session
1. Corriger les échecs de détection visuelle Zero-Shot (absence de détection simultanée main/téléphone/personne).
2. Développer l'affichage multi-boîtes hiérarchique avec palette de couleurs vifs par classe BGR et bannières opaques.
3. Implémenter le stockage incrémental des clichés de débogage visuel (`/tmp/dbot_snapshots/snap_XXX_...jpg`).
4. Déployer l'accélération TensorRT FP16 / ONNX sur la Jetson Orin Nano pour abaisser la latence et maîtriser la RAM.
5. Mettre à jour la documentation d'installation GPU JetPack 6.1 et valider le budget mémoire unifié LPDDR5.
6. Implémenter le déport VPU Myriad X (Filtre WLS + `SpatialLocationCalculator`) et restaurer le plein champ optique (81° FOV via ISP Scaling).

### 📝 Réalisations & Évolutions
1. **Refonte de la Triade Visuelle (`test_triad_vision.py` & `dbot/vision/yolo_world.py`)** :
   - Mise à niveau du modèle de `yolov8s` vers `yolov8m-worldv2` (26M paramètres).
   - Passage des requêtes CLIP en Anglais pur 1-to-1 (`hand`, `phone`, `bottle`, `person`, `chair`, `table`, `obstacle`).
   - Configuration NMS multi-classes permissive (`agnostic_nms=False`, `iou=0.70`, `conf=0.05`, `max_det=100`) permettant la coexistence de boîtes enfants (`MAIN`, `TELEPHONE`) dans des boîtes parents (`PERSONNE`).
2. **Superposition Visuelle & Spatiale 3D** :
   - Mappage de couleurs BGR distinctes par classe (`MAIN` Vert, `TELEPHONE` Cyan, `PERSONNE` Bleu, `TABLE` Violet, `CHAISE` Magenta, `BOUTEILLE` Orange) avec bannières de texte opaques.
   - Fusion spatiale $3D$ via OAK-D Pro affichant les coordonnées physiques réelles $[X, Y, Z]$ en mm.
3. **Stockage Incrémental de Clichés** :
   - Enregistrement sous `/tmp/dbot_snapshots/snap_XXX_LABEL_DIST.jpg` sans écrasement avec raccourci `/tmp/triad_last_detection.jpg`.
4. **Optimisation Matérielle & Documentation GPU/Mémoire** :
   - Implémentation du script d'exportation TensorRT FP16 / ONNX (`export_yolo_tensorrt.py`) avec limitation workspace à 2 GB.
   - Documentation complète des pièges `pip` (`cuda-toolkit-cu13`, `numpy 2.x`) et mise à jour de [`Annexes/jetson/installation/43_Configuration_PyTorch_CUDA_JetPack6.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/jetson/installation/43_Configuration_PyTorch_CUDA_JetPack6.md).
   - Validation du budget mémoire : Empreinte VRAM/RAM de la vision à **$1.2\text{ Go}$ à $1.8\text{ Go}$**, parfaitement conforme à l'alloué ($\le 2.5\text{ Go}$) dans `FINAL_Architecture_Master_V1_Hybride.md`, laissant **$> 4.5\text{ Go}$ libres**.
5. **Déport VPU Myriad X & Optique Grand Angle 81° FOV (`oak_camera.py`)** :
   - Déport matériel du lissage de profondeur WLS (gain 25% CPU Jetson) et du nœud `SpatialLocationCalculator` ($Z < 500\text{ mm}$ à $< 5\text{ ms}$).
   - Remplacement du rognage `setVideoSize` par l'ISP scaling matériel `setIspScale(1, 3)` pour restituer le plein champ grand angle 81° FOV.

---

## 📅 2026-07-22 — Finalisation Active Gaze, Support Français YOLO-World & Compilation PyTorch GPU

### 🎯 Objectif de la session
1. Intégrer la traduction automatique natif Français ➔ Anglais pour YOLO-World sans charge processeur.
2. Développer la boucle d'asservissement physique du cou **Active Gaze (Regard Actif)** et le serveur compagnon Visual Grounding sur Mac (`server_active_gaze_mac.py`).
3. Ajouter la poursuite prédictive par inertie de fuite (`Predictive Gaze`) et la gestion des conflits NMS multi-classes (`PERSONNE` vs `MAIN`).
4. Résoudre la régression PyTorch CPU et re-compiler nativement `torchvision` v0.20.0 avec accélération CUDA GPU.
5. Inscrire la règle de protection `pip install --no-deps` dans `.agents/AGENTS.md`.

### 📝 Réalisations & Évolutions
1. **Traduction Automatique & Dictionnaire Persistant (`fr_en_dictionary.json` & `yolo_world.py`)** :
   - Fichier JSON local pré-chargé avec **+150 objets du quotidien**.
   - Traduction zéro-ressource via `urllib.request` (Google Translate < 30 ms, 0 Mo RAM, 0% CPU) pour les mots inédits avec mémorisation automatique.
2. **Asservissement du Regard (Active Gaze & Predictive Tracking)** :
   - Création de `dbot/behaviors/active_gaze.py` et `scripts/vision/test_active_gaze.py`.
   - Conversion du décalage $2D$ en correction d'angles $(\Delta \theta_{pan}, \Delta \theta_{tilt})$ pour le cou RS-05 avec bridage de sécurité absolu aux bornes `config.py` ($[-80°, +80°]$ Pan, $[-20°, +30°]$ Tilt).
   - Extrapolation de vitesse (`predict_lost_target`) pendant 0.4s pour anticiper les fuites rapides de cibles et éviter le décrochage visuel.
3. **Résolution du Conflit NMS Hiérarchique** :
   - Configuration de `iou=0.90` et `agnostic_nms=False` dans `yolo_world.py` pour autoriser la détection simultanée de `PERSONNE` et `MAIN` sans écrasement de la boîte enfant par le corps.
4. **Restauration de PyTorch CUDA GPU & Compilation Native `torchvision` v0.20.0** :
   - Ré-installation du wheel officiel NVIDIA JetPack 6.1 `torch==2.5.0a0+872d972e41.nv24.08`.
   - Compilation depuis les sources de `torchvision` v0.20.0 avec `MAX_JOBS=1 FORCE_CUDA=1` sous `ninja` pour éviter le crash OOM RAM. Validation `CUDA disponible : True | NMS CUDA OK : True`.
5. **Pérennisation dans les Règles du Projet** :
   - Règle de protection `pip install <paquet> --no-deps` gravée dans `.agents/AGENTS.md`.

### 📌 Statut Général
- **Vision Réflexe Local & Regard Actif** : Totalement opérationnels et validés sur la Jetson Orin Nano GPU CUDA avec asservissement fluide du cou RS-05 et support du Français natif !

---

## 📅 2026-07-23 — Qualification Active Gaze 80 FPS TensorRT, Boucle Fermée CAN & Verrouillage Statique

### 🎯 Objectif de la session
1. Éliminer l'emballement d'angle et les oscillations percutantes contre les butées mécaniques (-80°) du cou RS-05 lors du suivi visuel (`test_active_gaze.py`).
2. Asservir le cou en boucle fermée sur la télémétrie angulaire réelle des codeurs moteurs CAN `neck.get_state()`.
3. Éliminer 100% des micro-tressautements diagonaux à l'arrêt (droite, bas, gauche) via une Hystérésis Adaptative et un filtre de consigne angulaire minimale (0.8°).
4. Accélérer la cadence d'inférence visuelle de 28 FPS (35 ms) à **80+ FPS (10 ms de latence)** via la compilation locale d'un binaire **TensorRT FP16 `.engine`** sur le GPU Ampere de la Jetson Orin Nano.
5. Intégrer un système de chargement bivalent résilient (YOLO/YOLOWorld) et un notificateur d'enrichissement du dictionnaire au démarrage.
6. Résoudre la perception Zero-Shot des tasses/mugs (`"mug, coffee mug, cup"`) et enrichir la suite de tests terrain.

### 📝 Réalisations & Évolutions
1. **Asservissement en Boucle Fermée sur Télémétrie CAN (`test_active_gaze.py`)** :
   - Mise à jour du thread d'asservissement visuel pour lire à chaque itération la position physique réelle des moteurs `state = neck.get_state()` (`curr_pan`, `curr_tilt`).
   - Élimination définitive du runaway d'angle (qui accumulait les deltas sur des variables logicielles open-loop avant la fin du mouvement physique).
2. **Verrouillage Statique par Hystérésis Adaptative & Filtrage Angulaire (`active_gaze.py` & `test_active_gaze.py`)** :
   - Implémentation d'une Hystérésis Adaptative : deadband d'entrée à 65 px, s'élargissant à **117 px (x1.8)** une fois le cou verrouillé au centre (`is_centered_state = True`).
   - Ajout d'un seuil angulaire minimal de **0.8°** pour envoyer un ordre de mouvement aux moteurs RS-05.
   - Résultat : Suppression totale des tressautements. Le cou reste 100% immobile et silencieux à l'arrêt.
3. **Gain Proportionnel Dynamique Non-Linéaire $K_p(e)$ & Extrapolation 500 ms** :
   - Variation automatique du gain $K_p(e) \in [0.20, 0.55]$ selon l'éloignement relatif au bord de l'image. Accélération de 2.75x lors des mouvements récents rapides.
   - Extension de la fenêtre d'extrapolation cinématique 3D de 5 à **15 trames (500 ms)** pour traverser les flous de bougé.
4. **Compilation TensorRT FP16 80+ FPS & Chargement Bivalent Résilient (`export_yolo_tensorrt.py` & `yolo_world.py`)** :
   - Création du script d'exportation 1-clic `export_yolo_tensorrt.py` pré-injectant l'ensemble des 74 catégories du dictionnaire D-Bot dans le plan binaire `.engine`.
   - Compilation réussie du fichier `yolov8m-worldv2.engine` (57.1 Mo) sur le GPU Jetson : réduction de la latence de **35 ms à 8-10 ms** (cadence de **80-120 FPS**, gain de 250 Mo VRAM).
   - Chargement bivalent résilient : `yolo_world.py` utilise `YOLO("model.engine")` pour TensorRT 80 FPS avec mappage automatique des index de classe `results[0].names`, et bascule en douceur sur `YOLOWorld("model.pt")` PyTorch CUDA en cas de besoin.
5. **Système de Notification Automatique du Dictionnaire** :
   - Suivi des nouveaux mots ajoutés dans `_new_words_since_export` et message de notification au démarrage suggérant la re-compilation en 1 clic.
   - Ajout de `*.engine` et `*.onnx` dans `.gitignore` pour protéger les modèles binaires locaux.
6. **Perception Zero-Shot des Tasses (`"mug, coffee mug, cup"`)** :
   - Séparation des sub-prompts par virgules pour des embeddings CLIP individuels et abaissement du seuil à 0.08 dans `CLASS_CONF_THRESHOLDS`.

### 📌 Statut Général
- **Active Gaze & Performance Vision 80 FPS** : Totalement qualifiés, ultra-fluides, synchronisés avec la boucle CAN 100 Hz, et verrouillés sans tressautement à l'arrêt !

---

## 📅 2026-07-24 — Qualification de la Reconnaissance Faciale Nommée (SCRFD 500M + ArcFace MobileFaceNet)

### 🎯 Objectif de la session
1. Intégrer un système d'identification faciale nommée ultra-compact et réactif sur la Jetson Orin Nano GPU CUDA (< 100 Mo VRAM, < 10 ms).
2. Résoudre les imprécisions des découpages géométriques en utilisant le détecteur exact **SCRFD 500M (`det_500m.onnx`)** et la transformation affine d'Umeyama sur 5 points clés.
3. Éliminer les fluctuations de scores et les incertitudes d'identification entre membres du foyer (ex: David vs Léa) via un buffer de lissage temporel sur 5 trames et un score par centroïde avec marge anti-hésitation (2%).
4. Fournir un serveur Web UI MJPEG déporté (`http://ubuntu.local:8090`) pour enregistrer à distance de nouveaux visages avec rétroaction graphique.

### 📝 Réalisations & Évolutions
1. **Pipeline de Reconnaissance Faciale Complexe (`code/dbot/vision/face_tracker.py`)** :
   - Chaînage natif : Bbox `PERSONNE` YOLO-World ➔ Détection SCRFD 500M (boîte exacte + 5 landmarks faciaux) ➔ Transformation affine `align_face()` (112 x 112 px) ➔ Embedding ArcFace MobileFaceNet (512-dim normalisé L2).
   - Score de comparaison hybride : 70% Centroïde Moyen du profil + 30% Échantillon Peak avec vérification de marge anti-hésitation ramenée à 2% (0.02) pour une séparation nette des profils familiaux.
2. **Lissage Temporel sur 5 Trames (`test_face_tracker.py`)** :
   - Mise en place d'un buffer glissant `emb_buffers` moyennant les vecteurs d'embeddings sur 5 trames consécutives.
   - Résultat : Élimination totale des trames parasites "INCONNU", score de similarité stabilisé à 70% - 95%.
3. **Serveur Web UI MJPEG & Rétroaction Graphique (`http://ubuntu.local:8090`)** :
   - Intégration d'un serveur HTTP multithreadé servant le flux vidéo MJPEG et permettant l'enregistrement d'un prénom (`--register "Nom"`) en 1 clic.
   - Recadrage graphique dynamique du rectangle nominatif ajusté sur la zone du visage.

### 📌 Statut Général
- **Reconnaissance Faciale Nommée** : Validée sur le terrain, fluide et intégrée à la perception 3D du D-Bot !

---

## 📅 2026-07-24 (Session du Soir) — Déploiement de la Discrimination Faciale High-Precision 3 Étapes & Poursuite Nominative Active Gaze

### 🎯 Objectif de la session
1. Déployer la Feuille de Route à 3 Étapes pour résoudre définitivement l'incertitude faciale intra-familiale (ex: David vs Léa vs Émilie).
2. Augmenter la résolution utile du visage (passer de crops flous de 30 x 30 px à des crops nets de 180 x 180 px).
3. Intégrer la reconnaissance faciale nommée directement dans la boucle d'asservissement en vitesse 100 Hz du cou RS-05 (`test_active_gaze.py --target "David"`).
4. Implémenter un filtre d'unicité physique spatio-temporelle pour empêcher les détections multiples en doublon d'un même membre de la famille.

### 📝 Réalisations & Évolutions

1. **Étape 2 : Découpage HD Natif Full-Resolution 1080p (`oak_camera.py` & `face_tracker.py`)** :
   - Ajout du flux parallèle `video_hd` (1920 x 1080 px brut) dans `DbotCamera` aux côtés du flux 640 x 360 px utilisé par YOLO.
   - Mise à jour de `process_person_crop()` pour découper le visage directement sur l'image source 1080p d'origine, apportant **3.5x plus de pixels nets réels** sur le visage (180 x 180 px contre 30 x 30 px auparavant).

2. **Étape 1 : Passage au Modèle ArcFace ResNet50 (`w600k_r50.onnx` ~160 Mo)** :
   - Téléchargement et chargement automatique du pack InsightFace `buffalo_l.zip` (~280 Mo) sur GPU CUDA ONNXRuntime.
   - Backbone 512-dim haute capacité multipliant par 4 la séparation angulaire. Les scores d'identification de David sont passés de **55%–65% à 92.2%–93.1%**.

3. **Étape 3 : Classifieur SVM à Marge Maximale (`sklearn.svm.SVC`)** :
   - Implémentation du ré-entraînement automatique d'un classifieur SVM linéaire avec calcul de probabilités calibrées à chaque enregistrement de profil familial.
   - Frontière de décision stricte éliminant l'hésitation entre les membres du foyer.

4. **Poursuite Nominative Active Gaze (`test_active_gaze.py`)** :
   - Couplage de `FaceTracker` avec la boucle d'asservissement en vitesse 100 Hz du cou RS-05.
   - Prise en charge des commandes nominatives : `python3 code/scripts/vision/test_active_gaze.py --target "David"` filtre les détections et oriente le cou spécifiquement sur David en ignorant les autres personnes.

5. **Filtre d'Unicité Physico-Spatiale (`deduplicate_identities`)** :
   - Ajout d'une règle d'exclusion spatio-temporelle : maximum 1 seule détection nominative (ex: Émilie) conservée par trame vidéo (sélection de la meilleure similarité, élimination des boîtes englobantes en doublon de YOLO-World).

### 📌 Statut Général
- **Discrimination Faciale & Regard Nominatif** : 100% Qualifiés et validés sur le terrain sur la Jetson Orin Nano GPU CUDA ! 🚀

---

## 📅 2026-07-27 — Stratégie de Prototypage Structurel 3D (Brackets Épaule RS-04/RS-03/RS-02) & Guide de Recuit Thermique (Sunlu FilaDryer E2)

### 🎯 Objectif de la session
1. Définir la stratégie de prototypage 3D pour les pièces de structure d'épaule (brackets RS-04 / RS-03 / RS-02) en remplacement temporaire de l'Aluminium 6061-T6 en attendant la livraison de la CNC C500 Networks.
2. Valider l'utilisation du sécheur et recuiseur professionnel Sunlu FilaDryer E2 (110°C max) pour le séchage et le recuit thermique des pièces D-Bot.
3. Répondre à l'étude spécifique sur le PETG-CF et l'intérêt d'un recuit thermique post-impression (polymère amorphe vs semi-cristallin PA12-CF/PPA-CF).
4. Rédiger la documentation de référence et mettre à jour les guides d'impression.

### 📝 Réalisations & Évolutions
1. **Choix et Qualification des Filaments de Prototypage** :
   - Qualification du **PA12-CF** (Nylon 12 + Carbone) comme choix N°1 pour les pièces à fort couple et chocs (résistance 90-115 MPa, léger, excellent comportement après recuit).
   - Qualification du **PPA-CF** (Polyphthalamide + Carbone) comme choix N°2 pour les sollicitations maximales (résistance > 120-140 MPa, module proche de l'Alu 6061).
   - Validation du **PETG-CF** pour le prototypage rapide à vide et la validation fonctionnelle complète de la chaîne de bout en bout (bus CAN 1 Mbps, alim 48V/12V, drivers et nodes ROS2, cinématique inverse et main D-Hand).
2. **Paramètres de Tranchage & Précautions d'Assemblage** :
   - Établissement des règles de slicing sur Qidi Plus 4 (6 à 8 parois minimum, remplissage gyroïde 50-75%, buse carbure de tungstène, chambre active à 50°C-65°C).
   - Recommandations d'assemblage (vis traversantes avec écrous nylostop / inserts Ruthex à chaud) et bridage logiciel du couple (`Max Torque` limité à 20-30% sous ROS2/firmware pour protéger le polymère de l'échauffement des stators).
3. **Étude du Recuit & Qualification du Sunlu FilaDryer E2** :
   - Formalisation des spécifications du Sunlu FilaDryer E2 (température jusqu'à 110°C, fonctions duales séchage et recuit).
   - Définition du protocole de séchage pré-impression pour filaments hygroscopiques (80-90°C pendant 8-12h pour PA12-CF/PPA-CF ; 65°C pendant 6h pour PETG-CF).
   - Définition du protocole de recuit thermique (90-100°C pendant 2-4h) pour PA12-CF/PPA-CF (gain de cohésion Z +20% à +30%, hausse HDT > 150°C-180°C).
   - Démonstration physique de l'absence d'intérêt du recuit post-impression pour le PETG-CF (structure amorphe, ramollissement au-dessus de Tg 75°C, gain mécanique quasi nul).
4. **Documentation & Guides de Référence** :
   - Création du guide [11_Prototypage_Mecanique_et_Recuit_Sunlu_E2.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/impression_3d/11_Prototypage_Mecanique_et_Recuit_Sunlu_E2.md).
   - Mise à jour du guide [09_Guide_Avance_Impression.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/Outils_de_Travail/impression_3d/09_Guide_Avance_Impression.md).

### 📌 Statut Général
- **Prototypage 3D Épaules & Recuit Sunlu E2** : Métrologie et protocoles 100% qualifiés et documentés ! 🚀
