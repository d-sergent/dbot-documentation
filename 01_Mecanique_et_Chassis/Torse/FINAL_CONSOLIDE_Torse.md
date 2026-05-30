# 🦾 **Spécifications Finales – Torse Hybride et Liaison Taille (D‑Bot) – Version V1.x**  

*Document de référence unique pour les modules **Torse** et **Taille (Waist)** du robot humanoïde D‑Bot (40,2 kg). Toutes les dimensions et spécifications découlent de l'intégration de la coque organique et de la liaison rotative de l'Asimov v1 (mises à l'échelle à +18 %), adaptées aux actionneurs RobStride et aux capacités de fabrication de notre atelier (Imprimante FDM Qidi Plus 4 + CNC C500).*

---

## 1. Vue d’Ensemble (Torse Rigide en 2 Parties & Liaison Active Waist Yaw)

Le châssis du torse adopte une **architecture monocoque bionique hybride** inspirée de l'Asimov v1.
* **Le Torse Rigide :** Pour maximiser la rigidité structurelle et obtenir des **brides d'épaules 100 % monoblocs (cercles continus à 360°)**, le torse est divisé horizontalement au niveau du ventre (découpe de fabrication FDM). À l'assemblage, les deux moitiés (le Thorax en haut, la coque abdominale en bas) sont verrouillées de manière **100 % rigide** par un emboîtement périphérique serré (Lap Joint de 3 mm), des bossages de vissage internes, et **deux lattes en aluminium CNC de 5 mm de la colonne vertébrale interne**. Chaque moitié est imprimée d'un seul tenant en orientant son **dos à plat sur le plateau** (FDM PA12-CF).
* **La Liaison Active Waist Yaw (1 DoF) :** Située immédiatement sous la plaque en aluminium inférieure du torse rigide, cette liaison active permet la rotation en lacet de la taille (dissociation du buste et du bassin). Elle est animée par un moteur **RobStride RS-03** (60 N.m pic / 20 N.m nom.) accouplé à un roulement à section fine de grand diamètre (scale +18 % de l'Asimov v1) reprenant l'intégralité des moments de flexion.

### A. Dimensions Clés du Torse

| Paramètre | Dimension CAO Physique | Dimension Cinématique Réelle | Justification / Proportions |
| :--- | :---: | :---: | :--- |
| **Hauteur** | **432,67 mm** *(Coque nue)* | **495,60 mm** *(Épaule ➔ Hanche)* | 🔄 Modèle CAO global scalé à +18% pour intégrer les moteurs RS-04 qui coinçaient initialement dans la coque MJF standard. |
| **Largeur** | **295,00 mm** *(Flanc ➔ Flanc)* | **~378,00 mm** *(Entraxe Épaules)* | 🔄 Largeur portée de 250 mm à 295 mm. L'entraxe des épaules s'ajuste à ~378 mm avec les moteurs RS-04. |
| **Profondeur** | **259,60 mm** *(Max)* | **259,60 mm** *(Max)* | 🔄 Espace intérieur étendu à 259.60 mm, offrant encore plus de place pour la batterie 12S et l'électronique embarquée. |

---

## 2. Spécifications Matérielles Validées (Architecture Hybride & Waist Yaw Actif)

Pour garantir une rigidité structurelle absolue sous les efforts des bras (moteurs RS-04 à 120 N.m), le buste est consolidé par un squelette métallique interne usiné sur la CNC C500. La rotation dynamique est quant à elle assurée par le module Waist d'Asimov v1 mis à l'échelle et équipé du moteur RobStride RS-03.

| **Composant** | **Qté** | **Dimensions / Fichier** | **Matériau** | **Masse (Est.)** | **Mise en Œuvre & Rôle** |
| :--- | :---: | :--- | :--- | :---: | :--- |
| **Demi-Coques Torse** | 2 | Thorax (Haut) & Abdomen (Bas) | **PA12-CF** | ~1 640 g | 🔄 Pièces imprimées monoblocs sur Qidi Plus 4, dos à plat. Épaisseur de paroi : 3 mm (6 périmètres à 0.48 mm, remplissage gyroïde 35%). Assemblage rigide par Lap Joint 3 mm + vis. |
| **Flasques d'Épaules** | 2 | Épaisseur : 5 mm *(CNC)* | **Aluminium 6061-T6** | ~223 g | 🔄 Logés dans des poches internes de la coque (agrandies). Reçoivent les vis des moteurs RS-04 (120 N.m) pour dissiper la chaleur et bloquer le cisaillement. |
| **Plaques de Structure Torse** | 2 | Supérieure (Cou) & Inférieure (Taille) | **Aluminium 6061-T6** | ~780 g | 🔄 Armatures horizontales d'origine Asimov v1 (scale +18 %, plaques de 5 et 6 mm). Maintiennent la cohérence rigide et tridimensionnelle du torse en prenant les coques en sandwich. |
| **Lattes de la Colonne** | 2 | Profil plat 5 mm *(CNC)* | **Aluminium 6061-T6** | ~130 g | 🔄 Attelles verticales reliant rigidement la plaque supérieure (cou) à la plaque inférieure (taille) à l'intérieur de la coque pour bloquer toute flexion. |
| **Moteur Waist Yaw** | 1 | RobStride RS-03 (CAN-FD) | **Brushless QDD** | ~880 g | 🔄 Actionneur de lacet de la taille (60 N.m pic / 20 N.m nom.). Standardisé sur l'ID 21, assure la rotation dynamique de la Waist Plate par rapport au bassin. |
| **Bague d'Adaptation CNC** | 1 | Épaisseur radiale : 4,8 mm *(CNC)* | **Aluminium 6061-T6** | ~110 g | 🔄 Bague d'adaptation pour encastrer le RS-03 (106 mm) dans le logement d'Asimov mis à l'échelle à +18 % (115,6 mm). |
| **Roulement de la Taille** | 1 | Section fine Ø110 mm (scale +18%) | **Acier Roulement** | ~280 g | 🔄 Roulement à section fine de grand diamètre d'Asimov v1 reprenant l'intégralité des moments de flexion axiaux/radiaux du buste. |
| **Inserts Filetés** | 30 | Filetage M4 (Ruthex) | **Laiton** | ~18 g | Insérés à chaud dans les coques PA12-CF pour le vissage rigide des bossages d'assemblage et fixations internes. |
| **Boulonnerie Interne** | — | M4 / M5 classe 10.9 | **Acier noir** | ~85 g | Vis d'accouplement de la liaison rotative, des plaques alu et des lattes de colonne. |
| **Masse Totale Buste + Waist** | — | — | — | **~4 146 g** | 🔄 Masse incluant le torse hybride 100 % rigide, l'armature métallique de structure, le moteur RobStride RS-03 et le roulement de grand diamètre. |

---

## 3. Nomenclature (BOM)

| **Référence** | **Désignation** | **Quantité** | **Fournisseur** | **Spécifications Techniques** |
| :--- | :--- | :---: | :--- | :--- |
| **FIL-PA12CF** | Filament PA12-CF (Nylon Carbone) - Bobine 1kg | 2 | Qidi / Extrudr | Diamètre 1.75 mm, buse carbure obligatoire. **2 bobines strictement nécessaires** (masse imprimée de ~1.64 kg, total ~1.9 kg avec supports/purges). |
| **MOT-RS03** | Moteur RobStride RS-03 (CAN-FD) | 1 | RobStride / OpenELAB | Actionneur quasi-direct (QDD) 48V, couple de pointe **60 N.m**, diamètre 106 mm. |
| **ALU-6061-5** | Tôle d'aluminium 6061-T6 - Épaisseur 5 mm | 1 | Métal Maker / Source locale | 🔄 Format 250 x 200 mm pour les flasques d'épaules, la plaque supérieure (cou) et les lattes CNC. |
| **ALU-6061-6** | Tôle d'aluminium 6061-T6 - Épaisseur 6 mm | 1 | Métal Maker / Source locale | 🔄 Format 320 x 280 mm pour la plaque de structure inférieure (Waist Plate) et la bague d'adaptation CNC (épaisseur 6 mm ou bloc). |
| **BRG-FINE110** | Roulement à section fine Ø110 mm (interne) | 1 | AliExpress / Misumi | Roulement mince à billes à quatre points de contact (scale +18 % de l'Asimov v1). |
| **INSERT-M4** | Inserts filetés à chaud M4 x 8.1 mm | 40 | Ruthex | Laiton, moletage croisé, pose au fer à souder à 260°C. |
| **SCREW-M4** | Vis CHC M4, longueurs diverses (12 à 24 mm) | 40 | Bricovis | Acier classe 10.9 minimum. |
| **LOCTITE-243** | Frein filet moyen (bleu) | 1 | Loctite | Flacon de 10 ml. |

---

## 4. État de la Conception (CAD & Simulation)

| **Élément** | **Statut** | **Fichier(s) CAD** | **Commentaires** |
| :--- | :---: | :--- | :--- |
| **Modèle Torse Global** | **Importé & Scalé (100%)** | `asimov_v1_imported.f3d` | Dimensions après scale +18% : hauteur physique 432,67 mm, largeur aux épaules 295 mm. |
| **Découpe Unique (Haut/Bas)** | **Validé & Documenté** | `torso_hybrid_split.f3d` | Modélisation de la lèvre d'emboîtement (Lap Joint) de 3 mm avec bandeau de renfort interne de 3 mm (épaisseur locale 5,88 mm) et jeux fonctionnels (0,15 mm radial / 0,10 mm axial). |
| **Logements CNC Épaules** | **Modélisé (100%)** | `shoulder_flange_pocket.f3d` | Poches intérieures de 5 mm de profondeur pour encastrer les flasques alu de 5 mm. |
| **Programmation CNC (CAM)** | **À faire** | `shoulder_plate_cam.nc` | Parcours d'outils à générer dans Fusion 360 pour la CNC C500. |
| **Simulation Thermique (Moteurs)** | **À faire** | — | Valider le rôle de dissipateur des plaques d'épaules alu en continu. |

---

## 5. Instructions de Montage et d'Usinage Critiques

1. **Usinage des Flasques et Lattes CNC (Aluminium 6061-T6) :**
   * Utiliser une fraise plate carbure de 1/4" (6,35 mm) pour l'ébauche et 1/8" (3,175 mm) pour la finition des contours.
   * Veiller à calibrer l'alésage central au diamètre exact du pilote du RobStride RS-04 (ajustement glissant).

2. **Impression des Demi-Coques en PA12-CF (Qidi Plus 4) :**
   * **Orientation :** Poser les pièces **à plat sur leur face dorsale (le dos)**. Les couches d'impression s'empilent horizontalement (axe Z-imprimante = axe Y-robot). 
   * **Supports :** Activer des supports arborescents (Tree Supports) uniquement à l'extérieur pour soutenir les courbes du dos et le dessous des collets d'épaules. Aucun support interne n'est requis (la cavité s'imprime comme un bol ouvert).
   * **Paramètres Thermiques :** Buse à 295°C, plateau à 80°C, chambre préchauffée à 60°C pour éliminer le warping.

3. **Insertion des inserts et des goupilles :**
   * Insérer les inserts Ruthex M4 à l'aide d'un fer à souder réglé à **260°C**. Appliquer une pression axiale douce sans forcer pour éviter que le plastique fondu ne reflue dans le filetage.
   * Emmancher les goupilles de centrage en inox Ø4 mm sur le plan de joint du Pelvis (Bas).

4. **Serrage des liaisons mécaniques :**
   * Appliquer de la **Loctite 243** sur toutes les vis M4 assemblant la coque PA12-CF sur les flasques alu et le moteur d'épaule.
   * Serrer les deux lattes en alu (colonnes internes) à travers le plan de joint horizontal pour former une attelle rigide.
   * Couple de serrage recommandé pour les fixations d'épaules : **3,5 Nm** (dans l'aluminium).

---

*Spécifications approuvées et mises à jour en Mai 2026 suite à la transition vers l'architecture hybride Asimov v1 en 2 pièces (Haut/Bas).*