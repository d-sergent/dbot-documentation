# 🦾 **Spécifications Finales – Jambes et Pieds (D‑Bot V1.x)**  
*Version consolidée – avril 2026*  

---  

## 1. Vue d’Ensemble (Version Actuelle)

Le module **Jambes et Pieds** du D‑Bot (masse totale ≈ 40.2 kg) repose sur l’architecture **F‑A‑R** (Pitch → Roll → Yaw) pour la hanche, un **genou à transmission GT3 2.5 : 1** et une **cheville à cardan DIN 808** pilotée par **2 × RS‑03** (bielles différentielles).  

* **DOF par jambe** : 6 (Hanche P/R/Y + Genou P + Cheville P/R).  
* **Moteurs par jambe** : 6 (2 × RS‑04 – Hip Pitch + Knee Pitch, 2 × RS‑03 – Hip Roll/Yaw, 2 × RS‑03 – Cheville Pitch/Roll).  
* **Transmission principale** :  
  * **Genou** – Courroie GT3 (9 mm, 2.5 : 1) entre le RS‑04 Knee (haut cuisse) et l’axe du genou.  
  * **Cheville** – Cardan central DIN 808 + deux bielles en tube carbone (actionnement différentiel).  

Cette configuration a été validée par les études biomécaniques (15c, 15d, 15f, 15h) et par les calculs de charge dynamique (15f, 15c).  

---  

## 2. Spécifications Matérielles Validées  

| Articulation | Mouvement | Moteur | Couple (pic) | Réduction | Vitesse max (RPM) | Masse moteur (g) | Remarques |
|---|---|---|---|---|---|---|---|
| **Hanche – Pitch** | Flexion/extension | **RS‑04** (RobStride) | **120 N·m** | 1 : 1 (direct‑drive) | 167 rpm | 1 420 g | Fixé dans le bassin (maillon 1 F‑A‑R). |
| **Hanche – Roll** | Abduction/Adduction | **RS‑03** | 60 N·m (par moteur) | 1 : 1 | 200 rpm | 880 g | Couplé en série avec le Pitch via bracket L‑Alu. |
| **Hanche – Yaw** | Rotation interne/externe | **RS‑03** | 60 N·m (par moteur) | 1 : 1 | 200 rpm | 880 g | Dernier maillon de la chaîne F‑A‑R. |
| **Genou – Pitch** | Flexion/extension | **RS‑04** (déplacé en haut de cuisse) | 120 N·m | **GT3 2.5 : 1** → **300 N·m** à l’axe du genou | 67 rpm (effet de réduction) | 1 420 g | Courroie GT3 9 mm, pignons 20 T (moteur) / 50 T (genou). |
| **Cheville – Pitch** | Flexion/extension | **2 × RS‑03** (différentiel) | 120 N·m (synchronisé) | 1 : 1 | 200 rpm | 2 × 880 g | Cardan DIN 808, bielles carbone Ø10/8 mm. |
| **Cheville – Roll** | Inversion/Éversion | **2 × RS‑03** (différentiel) | 120 N·m (différentiel) | 1 : 1 | 200 rpm | 2 × 880 g | Même cardan, action différentiel. |

### 2.1. Bilan de Couple vs. Besoins (extraits des études)

| Situation | Couple requis (N·m) | Couple disponible | Marge |
|---|---|---|---|
| **Statique – Hanche Pitch** | 49 N·m | 120 N·m | **+144 %** |
| **Statique – Genou (sans GT3)** | 69 N·m | 120 N·m | **+74 %** |
| **Genou avec GT3 (2.5 : 1)** | 172 N·m (course) | **300 N·m** | **+74 %** |
| **Cheville Pitch (marche 2‑3 km/h)** | 45 N·m | 120 N·m | **+167 %** |
| **Cheville Roll (marche)** | 20 N·m | 120 N·m | **+500 %** |
| **Course 5 km/h – Genou** | 177 N·m | 120 N·m | **‑30 %** (limite, voir § 6) |
| **Course 5 km/h – Cheville** | 103 N·m | 120 N·m | **+17 %** |

> **Conclusion** : La cheville n’est plus le goulot d’étranglement. Le genou devient la contrainte principale pour la course rapide.  

---  

## 3. Nomenclature (BOM Locale)  

> **Tous les prix et fournisseurs proviennent des sources indiquées.**  
> **[À COMPLÉTER]** indique une donnée manquante dans les documents sources.  

| Réf. | Désignation | Spécifications | Quantité (2 jambes) | Fournisseur | Prix unitaire (€) | Masse (g) |
|---|---|---|---|---|---|---|
| **MOT‑01** | Moteur RS‑04 – Hip Pitch | 120 N·m, 167 rpm, 48 V, 1 420 g | 2 | RobStride (distributeur officiel) | 1 200 € | 1 420 |
| **MOT‑02** | Moteur RS‑04 – Knee | 120 N·m, 167 rpm, 48 V, 1 420 g | 2 | RobStride | 1 200 € | 1 420 |
| **MOT‑03** | Moteur RS‑03 – Hip Roll/Yaw | 60 N·m, 200 rpm, 48 V, 880 g | 4 | RobStride | 850 € | 880 |
| **MOT‑04** | Moteur RS‑03 – Cheville (x2) | 60 N·m, 200 rpm, 48 V, 880 g | 4 | RobStride | 850 € | 880 |
| **CAR‑01** | Cardan DIN 808 – Série G, axe 12 mm, acier C45 (ou Duralumin) | 12 mm, rainure 4 mm, poids 80‑120 g | 2 | Michaud Chailly (ref A5‑473‑12) | 45 € | 100 |
| **BRK‑01** | Bracket L‑Alu 6061‑T6 (hauteur genou) | CNC C500, 30 mm × 20 mm × 10 mm, alésage Ø8 mm | 2 | Usinage interne (C500) | 12 € | 30 |
| **BRK‑02** | Bracket U‑Alu 6061‑T6 (hip‑roll) | CNC C500, 40 mm × 25 mm × 12 mm | 2 | Usinage interne | 14 € | 35 |
| **TIB‑01** | Tibia – tube carbone tressé Ø40 mm × 2 mm (3K, twill, roll‑wrapped) | Longueur 500 mm (2 pièces) | 2 | CarbonTube.net / EasyComposites | 22 € | 80 g (≈ 40 g/piece) |
| **TIB‑02** | Bouchon interne Ø36 mm (Alu 6061) – époxy structurale | Longueur 30 mm, masse 15 g | 4 (2 × haut + bas) | Usinage interne | 4 € | 15 |
| **GPI‑01** | Goupille élastique Mécanindus Ø3 mm (roll‑pin) | Acier, 6 300 N cisaillement (double) | 8 (4 × tibia) | Mécanindus | 1 € | 2 |
| **BIL‑01** | Bielle – tube carbone 3K pultrudé Ø10 mm × Ø8 mm | Longueur 200 mm, 20 g/m | 4 (2 × cheville) | CarbonTube.net | 6 € | 4 |
| **ROT‑01** | Rotule Igus EBRM‑05 (polymer) | Ø5 mm, 0.5 N·m friction | 8 (extrémités bielles) | Igus | 3 € | 1 |
| **CRT‑01** | Courroie GT3 9 mm – longueur 650 mm (fermé) | 9 mm, 650 mm, 2 × paires | 2 (genou D + G) | AliExpress / Amazon | 15 € | 25 g |
| **PIG‑01** | Pignon GT3 20 T – Alu 8 mm bore | Ø32 mm, 2 mm épaisseur | 2 (un par genou) | AliExpress | 8 € | 15 g |
| **PIG‑02** | Pignon GT3 50 T – Alu 12 mm bore | Ø51 mm, 3 mm épaisseur | 2 (un par genou) | AliExpress | 18 € | 85 g |
| **GAL‑01** | Galet tendeur (roulement 625ZZ Ø16 mm + bras ressort) | 9 mm GT3, tension 5‑10 N | 2 | AliExpress | 5 € | 20 g |
| **PAD‑01** | Pads d’appui TPU (Shore 95A) – 30 mm × 30 mm | 2 mm d’épaisseur, 2 pcs/pied | 4 | Qidi (impression) | 2 € | 5 g |
| **COU‑01** | Cou‑de‑pied – PA12‑CF (Qidi) | 30 mm × 20 mm × 10 mm | 2 | Qidi (impression) | 4 € | 12 g |
| **PLA‑01** | Plaque plantaire – fibre carbone 3 mm (CNC) | 120 mm × 80 mm × 3 mm | 2 | CNC C500 (feuille carbone) | 12 € | 30 g |
| **SHT‑01** | Soufflet néoprène (protection cardan) | 12 mm × 150 mm | 2 | Fournisseur cardan (Michaud) | 6 € | 10 g |
| **VIS‑01** | Vis M4 × 12 mm inox, classe 12.9 | – | Lot 200 | Quincaillerie locale | 0.02 € | 0.5 g |
| **COL‑01** | Époxy structurale bicomposant (Loctite EA / DP490) | 2 : 1, résistance cisaillement > 6 kN | Lot 1 L | Loctite | 30 € | – |

**Total masse estimée (par jambe, pièces mobiles uniquement)** ≈ **460 g** (tibia + bielles + cardan + pied).  

**Coût matériel (2 jambes)** ≈ **1 850 €** (hors moteurs, qui sont déjà comptés dans le budget global du robot).  

---  

## 4. État de la Conception (CAD & Simulation)

| Élément | Fichier CAD | Format | Statut | Commentaires |
|---|---|---|---|---|
| **Tibia (tube carbone + bracket L)** | `tibia_haut.step` / `tibia_bas.step` | STEP | ✅ Validé (dimensions 500 mm, Ø40 mm) | Assemblage avec goupille et bouchon testé en simulation dynamique (Ansys). |
| **Bracket L (Alu 6061‑T6)** | `bracket_L_alu.step` | STEP | ✅ Usinage CNC C500 validé | Tolérance d’alésage 8.00 ± 0.02 mm. |
| **Bracket U (Hip‑Roll)** | `bracket_U_alu.step` | STEP | ✅ Usinage CNC C500 validé | Interface RS‑03‑Roll/Yaw. |
| **Cardan DIN 808** | `cardan_808.step` | STEP | ✅ Modèle fourni par Michaud Chailly | Perçage Ø3 mm ajouté (goupille). |
| **Bielles (carbone Ø10/8)** | `bielle_cheville.step` | STEP | ✅ Simulation de flambement (E = 130 GPa) – facteur de sécurité > 10. |
| **Pignon GT3 20T / 50T** | `pignon_GT3_20T.step` / `pignon_GT3_50T.step` | STEP | ✅ Modèle CAO importé d’Aliexpress (dimensions vérifiées). |
| **Courroie GT3** | `courroie_GT3.step` | STEP | ✅ Trajectoire de montage définie, tension calculée (5‑10 N). |
| **Pied (PA12‑CF + plaque carbone + TPU pads)** | `pied_assemblage.step` | STEP | ✅ Analyse de fréquence (mode 1 ≈ 250 Hz, hors bande de contrôle). |
| **Fémur hybride (Iso‑grid + PA12‑CF)** | `femur_hybride.step` | STEP | ✅ FAO C500 (Iso‑grid 4 mm struts, épaisseur 5 mm) – masse ≈ 500 g. |
| **Simulation dynamique globale** | `simulation_dbot_kinematics.feb` | FEBio | ✅ Couple, inertie, impact vérifiés pour marche 0‑5 km/h. |

---  

## 5. Instructions de Montage Critiques  

| Étape | Action | Points de vigilance |
|---|---|---|
| **1 – Pré‑assemblage tibia** | Insérer le **bouchon interne Ø36 mm** dans le tube carbone, coller avec **époxy structurale** (10 min de cure). | Vérifier que le bouchon est centré (±0.1 mm). |
| **2 – Fixation du bracket L** | Aligner le **bracket L** sur l’axe de sortie du RS‑04 Knee, insérer la **goupille Ø3 mm** traversante (roll‑pin). | La goupille doit être enfoncée jusqu’à la butée du bouchon – résistance ≈ 6 300 N. |
| **3 – Montage du cardan** | Placer le **cardan DIN 808** dans le bas du tibia, percer les deux moyeux (déjà usinés Ø3 mm) et insérer la **goupille Mécanindus**. | Utiliser le **canon de perçage** du cardan pour percer le tube carbone – évite tout désalignement. |
| **4 – Installation des bielles** | Insérer les **tubes carbone Ø10/8 mm** dans les supports du cardan, coller les **rotules Igus EBRM‑05** à chaque extrémité avec époxy. | Contrôler le jeu axial < 0.05 mm, sinon risque de jeu de direction. |
| **5 – Montage du genou (GT3)** | Fixer le **RS‑04 Knee** sur le **bracket haut** (vis M4 × 12 mm), monter le **pignon 20 T** sur l’arbre moteur, le **pignon 50 T** sur l’axe du genou, enfiler la **courroie GT3** et installer le **galet tendeur**. | Tension de la courroie : 5‑10 N (mesurée avec dynamomètre). Vérifier l’alignement des axes (déviation < 1 mm). |
| **6 – Assemblage du pied** | Coller le **cou‑de‑pied PA12‑CF** sur le cardan, visser la **plaque carbone 3 mm** (ossature plantaire), coller les **pads TPU** (avant‑pied & talon). | S’assurer que la plaque est bien centrée – sinon déséquilibre latéral. |
| **7 – Vérification finale** | Faire tourner chaque articulation à la main (0‑360°) – aucune friction anormale, aucun jeu > 0.2°. Connecter les capteurs FSR (si présents) et vérifier les valeurs d’étalonnage. | En cas de jeu, resserrer la goupille ou refaire l’époxy du bouchon. |

---  

## 6. Backlog Technique & Questions en Suspens  

| N° | Question / Incertitude | Source | Priorité | Commentaire / Action proposée |
|---|---|---|---|---|
| **6.1** | **Durée de vie exacte de la courroie GT3 sous charge cyclique** (10 M cycles estimés, mais pas de test réel). | 15d §3.3 | ★★ | Planifier un banc d’essai de fatigue (10 k cycles) pour valider le facteur de sécurité. |
| **6.2** | **Valeur exacte du coefficient de frottement des rotules Igus EBRM‑05** (datasheet non fournie). | 15b §7‑10 | ★ | Contacter Igus pour fiche technique ou mesurer en laboratoire. |
| **6.3** | **Masse exacte du “soufflet néoprène”** (déclaration “~10 g” sans mesure). | 15c | ★ | Peser le composant fourni par le fabricant. |
| **6.4** | **Tolérance d’usinage du perçage Ø3 mm du cardan** (±0.05 mm ou ±0.1 mm ?). | 15c | ★ | Vérifier le plan de fabrication du fournisseur (Michaud Chailly). |
| **6.5** | **Compatibilité du GT3 2.5 : 1 avec un futur moteur RS‑06 (si on upgrade le genou)** – besoin d’un nouveau pignon (ratio). | 15d §3.3 | ★★ | Étudier un pignon 30 T (moteur) / 75 T (genou) pour garder 2.5 : 1. |
| **6.6** | **Impact thermique du RS‑04 Knee à 300 N·m (GT3)** – aucune donnée de température en charge continue. | 15d §3.3 | ★★ | Simuler thermique (CFD) ou mesurer sur banc à 80 % du couple max pendant 5 min. |
| **6.7** | **Possibilité d’ajouter un capteur de couple intégré au pignon GT3** (pour contrôle en boucle). | 15d | ★ | Recherche de pignons “torque‑sensing” (ex : NXP). |
| **6.8** | **Valeur exacte du poids du fémur hybride (Iso‑grid + PA12‑CF)** – seulement “≈ 500 g” indiqué. | 15g (fémur) | ★ | Mesurer le prototype usiné. |
| **6.9** | **Éventuel besoin d’un joint d’étanchéité supplémentaire entre le cardan et le tibia** (pour poussière). | 15c | ★ | Étudier l’ajout d’un joint en néoprène (type “oil‑seal”). |
| **6.10** | **Compatibilité du système de contrôle (firmware) avec la nouvelle réduction GT3 (délais de commande)** – aucune latence mesurée. | 15d §3.3 | ★★ | Faire un test de réponse (step‑response) sur le contrôleur. |

---  

## 7. Roadmap & Itérations Futures (Optionnel)

| Phase | Objectif | Modifications prévues | Impact attendu |
|---|---|---|---|
| **V2 (6‑12 mois)** | **Course > 5 km/h** | – Ajouter un **SEA** (Series‑Elastic Actuator) au genou (ressort en série) pour augmenter le couple effectif à ≈ 250 N·m.<br>– Optimiser la **tension de la courroie GT3** (galet à ressort à mémoire de forme). | Marge genou + ≈ +80 % → capacité de course 8‑10 km/h. |
| **V3 (12‑18 mois)** | **Réduction de l’inertie distale** | – Remplacer le **tibia carbone** par une **lame carbone** (solution S5) couplée à un **amortisseur passif** (visco‑élastique). | Inertie tibia ↓ ≈ 30 % → consommation énergétique ↓ ≈ 15 %. |
| **V4 (> 18 mois)** | **Transmission hybride** | – Étudier une **double‑courroie GT3** (ratio 1.5 : 1 + 2 : 1) pour offrir deux vitesses (marche / course). | Flexibilité dynamique, adaptation à la charge. |
| **V5 (2 ans)** | **Intégration de capteurs de couple** | – Installer des **capteurs de contrainte** sur les pignons GT3 (type “torque‑sensing gear”). | Boucle de contrôle en temps réel, meilleure protection contre les surcharges. |

---  

### Annexes (références rapides)

| Ref. | Document source | Section clé |
|---|---|---|
| **15a** | Analyse Locomotion Baseline | Paramètres physiques, couples requis. |
| **15b** | Configurations Moteurs & Évolutions | Options A‑D, DOF Roll, capteurs FSR. |
| **15c** | Révision Cardan 40.2 kg | Calculs de couple cheville, masse 40.2 kg. |
| **15d** | Genou – Analyse & Solution GT3 | Choix S6 (GT3 2.5 : 1). |
| **15e** | Alternatives Moteurs Genou | RS‑02, RS‑03, RS‑06 comparatif. |
| **15f** | Portage de Charges & Marche | Limites de charge du genou. |
| **15g** | Courroie GT3 (redirection) | Fusionnée dans 15d. |
| **15h** | Alternatives Transmission Genou | Tirant, chaîne, courroie, pivots variables. |
| **16** | Conclusions & Architecture Finale | Décisions finales par articulation. |
| **Study_Mecanismes_Cheville** | Comparatif mécanismes de cheville | Analyse des 4 approches (direct‑drive, tirant, hybride, parallèle). |
| **Study_Structure_Femur_Hybride** | Conception fémur hybride | Iso‑grid + PA12‑CF recommandé. |


**Document généré le 16 mai 2026 – Version V1.0**  
*Toutes les valeurs proviennent des sources listées ci‑dessus. Toute donnée manquante est indiquée comme **[À COMPLÉTER]** et figure dans la section 6.*

---

## 8. Capteurs Tactiles Plantaires — Semelle Intelligente (Ajout V1.1)

> **Référence complète :** `Documentation/03_Electronique_Capteurs/GUIDE_PCB_MLX90393_et_Recyclage_WowRobo.md` §4 et §5.2

### 8.1 Décision d'Architecture

**4× PCBs WowRobo eFlesh** (20×20mm, 5× MLX90393 chacun) sont intégrés dans chaque semelle plantaire, exploitant le stock existant de PCBs WowRobo excédentaires par rapport au besoin de la main.

### 8.2 Les Capteurs Plantaires sont-ils Utiles si le Robot a un IMU ?

> **Réponse : OUI — ils sont complémentaires et irremplaçables l'un par l'autre.**

L'IMU et les capteurs plantaires ne mesurent pas la même chose :

| Capteur | Ce qu'il mesure | Ce qu'il ne peut PAS mesurer |
|:---|:---|:---|
| **IMU** | Orientation/accélération du **corps** (torse) | Ce qui se passe sous les pieds |
| **Capteurs plantaires** | Forces au point de **contact sol** | L'orientation globale du corps |

**Limitations critiques de l'IMU seul :**

1. **Dérive gyroscopique** (1–5°/heure) → après 10 min de marche, erreur de 1.5° → moment déstabilisant de ~10 N·m. Les capteurs plantaires fournissent une référence absolue au sol qui corrige cette dérive.
2. **Terrain non-plat** : L'IMU voit le torse pencher mais ne sait pas si c'est une montée normale ou une chute imminente. Le capteur plantaire voit immédiatement la sur-charge du talon ou un CoP hors zone de stabilité.
3. **Détection de glissement** : Détectable en **< 10ms** par les capteurs plantaires (vecteur cisaillement Bx/By), vs **200–500ms** de délai pour l'IMU (la chute est déjà amorcée).

> **Tous les robots bipèdes de référence** (Atlas, Digit, H1, Figure 01) utilisent les deux types de capteurs simultanément. L'IMU seul ne suffit pas pour un bipède performant.

### 8.3 Nouvelles Entrées BOM (par pied)

| Réf. | Désignation | Quantité | Fournisseur | Prix |
|---|---|---|---|---|
| **TAC‑01** | PCB eFlesh WowRobo (20×20mm, 5× MLX90393) | 4 | WowRobo (stock existant) | 0 € (déjà acheté) |
| **TAC‑02** | Aimants néodyme Ø3mm × 1mm (N48) | 20 | Supermagnete (S-03-01-N) | ~3.4 € |
| **TAC‑03** | ESP32-S3 micro (Seeed XIAO S3 ou équivalent) | 1 | Seeed Studio | ~8 € |
| **TAC‑04** | Câbles JST-SH 4P 1.0mm 300mm (I2C) | 4 | GoTronic / AliExpress | ~4 € |
| **TAC‑05** | TPU Shore 85A/95A (semelle gyroïde 8%) | ~50g | Filament Qidi | ~2 € |

**Surpoids total par pied : ~29 g** (PCBs ~8g + aimants ~1g + câbles ~5g + TPU semelle ~15g)

### 8.4 Disposition des 4 PCBs dans la Semelle (120×80mm)

```
         ← 80mm →
    ┌───────────────────────────┐  ↑
    │  [PCB#3 Métatarse Médial] │  │
    │  [PCB#4 Métatarse Latéral]│  │  120mm
    │                           │  │
    │  [PCB#2 Voûte Plantaire]  │  │
    │                           │  │
    │  [PCB#1 Talon Calcanéum]  │  │
    └───────────────────────────┘  ↓
```

### 8.5 Centre de Pression (CoP) — Principe de Calcul

Avec 4 PCBs (20 capteurs magnétiques au total), l'ESP32-S3 calcule le CoP en temps réel :

```
CoP_x = Σ(F_i × x_i) / Σ(F_i)
CoP_y = Σ(F_i × y_i) / Σ(F_i)
```

où F_i est la force normale estimée de chaque PCB (norme du vecteur Bz), et (x_i, y_i) sont les coordonnées de chaque PCB dans le repère de la semelle.

**Données transmises au Jetson (USB CDC) :**
- CoP_x, CoP_y (position du centre de pression, mm)
- GRF_z (force de réaction verticale estimée, N)
- Vecteur de cisaillement (Bx, By) → détection de glissement
- Phase de contact (talon / flat / toe-off)

### 8.6 Câblage I2C Pied

```
ESP32-S3 Pied (dans boîtier PA12-CF, bas du tibia)
├── Bus I2C N°1 → PCB#1 (Talon) + PCB#2 (Voûte)
└── Bus I2C N°2 → PCB#3 (Métat. Médial) + PCB#4 (Métat. Latéral)
```