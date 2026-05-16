# 🦾 Spécifications Finales : Tête et Cou (D‑Bot) – Version **V1.x**  *(Mars / Mai 2026)*  

---  

## 1. Vue d’Ensemble (Version Actuelle)  

Le sous‑assemblage **Cou (Neck)** du D‑Bot comporte **3 DOF** :  

| DOF | Axe (URDF) | Mouvement | Motorisation | Réduction | Couple nominal | Couple pic |
|-----|------------|-----------|--------------|-----------|----------------|------------|
| **Yaw (Pan)** | **Z** (vertical) | Rotation gauche‑droite de la tête | **RobStride RS‑05** (Moteur 1) | Direct : 1 : 1 (pas de réducteur) | 1.6 N·m | 5.5 N·m |
| **Pitch (Tilt)** | **Y** (latéral) | Inclinaison avant‑arrière (oui/non) | **RobStride RS‑05** (Moteur 2) | Direct : 1 : 1 | 1.6 N·m | 5.5 N·m |
| **Roll** | **X** (longitudinal) | Inclinaison latérale (oreille → épaule) | **RobStride RS‑05** (Moteur 3) | Direct : 1 : 1 | 1.6 N·m | 5.5 N·m |

*La masse totale de la tête (structure + capteurs OAK‑D Pro + électronique) ≈ 2 kg.*  

Le **cou** est monté sur le **torse** (link `torso_link`). Chaque axe possède un joint révolute avec limites angulaires ±90 ° (Yaw) ou ±45 ° (Pitch / Roll) et un effort maximal de **5.5 N·m** (voir tableau 2).  

---

## 2. Spécifications Matérielles Validées  

### 2.1 Tableau récapitulatif des joints (URDF)

| Joint URDF | Type | Axe (xyz) | Limites (rad) | Limites (°) | Effort max (N·m) | Vitesse max (rad/s) |
|------------|------|-----------|---------------|-------------|------------------|----------------------|
| `neck_yaw_joint`   | revolute | 0 0 1 (Z) | [-1.57 , 1.57] | ±90° | 5.5 | 6.28 |
| `neck_pitch_joint` | revolute | 0 1 0 (Y) | [-0.79 , 0.79] | ±45° | 5.5 | 6.28 |
| `neck_roll_joint`  | revolute | 1 0 0 (X) | [-0.79 , 0.79] | ±45° | 5.5 | 6.28 |
| `head_fixed_joint` | fixed    | – | – | – | – | – |

### 2.2 Moteurs RS‑05 (3 unités)

| Référence | Masse (g) | Dimensions (mm) | Couple nominal (N·m) | Couple pic (N·m) | Alimentation | Vitesse max (rpm) | Fournisseur |
|-----------|-----------|-----------------|----------------------|------------------|---------------|-------------------|-------------|
| **RS‑05‑1** (Yaw) | 191 | 46 × 46 × 44 | 1.6 | 5.5 | 24 V DC | 120 | RobStride |
| **RS‑05‑2** (Pitch) | 191 | idem | 1.6 | 5.5 | 24 V DC | 120 | RobStride |
| **RS‑05‑3** (Roll) | 191 | idem | 1.6 | 5.5 | 24 V DC | 120 | RobStride |

> **Note** : Le RS‑05 ne possède aucun arbre de sortie. La transmission du couple se fait via la face du rotor (plot de centrage + trous M4).  

### 2.3 Roulements (solution retenue – **Solution 4**)  

| Référence | Type | Ø Int. (mm) | Ø Ext. (mm) | Largeur (mm) | Charge radiale (kN) | Charge axiale (N) | Prix (≈) | Fournisseur |
|-----------|------|-------------|-------------|--------------|----------------------|-------------------|----------|-------------|
| **6804‑2RS** | Radial étanche, 2 RS | 20 | 32 | 7 | 3.0 | 1 900 | 3‑5 € | SKF / NSK / Amazon |
| **6804‑2RS** (second, Pitch) | idem | idem | idem | idem | idem | idem | idem | idem |

### 2.4 Pièces mécaniques associées (Solution 4 – Hub réduit)

| Pièce | Matériau | Dimensions principales | Fonction | Quantité | Fabrication / Fournisseur |
|-------|----------|------------------------|----------|----------|---------------------------|
| **Tube Hub** | Al 6061 (extrudé puis usiné) | Ø 20 mm (int.) – Ø 22 mm (ext.) – hauteur ≈ 12‑15 mm | Support rotor RS‑05, accueille la bague intérieure du 6804‑2RS | 1 (par moteur) | Usinage interne |
| **Carter fixe** | Al 6061 | Alésage Ø 32 mm (H7) – épaisseur ≥ 3 mm | Emmanche la bague extérieure du 6804‑2RS, fixé au torse | 1 (par moteur) | Usinage interne |
| **Bride d’adaptation** | Al 6061 | Ø 20 mm (cercle de centrage) + 6×M4 8 mm | Fixe le hub sur le rotor (vis M4) | 1 | Usinage interne |
| **Circlip E20** | Acier ressort | – | Retenue axiale haute du hub | 1 | Stock standard |
| **Visserie** | Acier M3 / M4 | – | Fixations diverses (4×M3 torse, 6×M4 hub‑rotor, 4×M4 tête‑hub) | 1 set | Visserie standard |
| **Solénoïde de blocage** (parking brake – Pitch) | – | 50 × 16 × 19 mm | Verrouillage mécanique du Tilt en position « parking » | 2 (un par côté) | LEX‑SOLEN‑04, 12 VDC, 0.6 A |

---

## 3. Nomenclature (BOM Locale)

| # | Référence interne | Nom URDF (link / joint) | Description détaillée | Quantité | Fournisseur / Source | Prix Unitaire (€) |
|---|-------------------|--------------------------|-----------------------|----------|----------------------|-------------------|
| 1 | **robstride05 v1:1** | `neck_yaw_motor` (dans `neck_yaw_link`) | Moteur RS‑05 – Yaw | 1 | RobStride | – |
| 2 | **U‑Pan v15:1** | `neck_yaw_bracket` (fusionné) | Bracket en U support Yaw | 1 | [À COMPLÉTER] | – |
| 3 | **robstride05 v1:2** | `neck_roll_motor` (dans `neck_roll_link`) | Moteur RS‑05 – Roll | 1 | RobStride | – |
| 4 | **6082Z v1:1** | `neck_roll_housing` (fusionné) | Carter alu du Roll | 1 | [À COMPLÉTER] | – |
| 5 | **6804_2rs v1:1** | `neck_roll_bearing` (fixed) | Roulement 6804‑2RS – Roll | 1 | SKF/NSK | 4 € |
| 6 | **Tilt v14:1** | `neck_pitch_bracket` (dans `neck_pitch_link`) | Bracket Pitch (U‑shape) | 1 | [À COMPLÉTER] | – |
| 7 | **6804_2rs v1:2** | `neck_pitch_bearing` (fixed) | Roulement 6804‑2RS – Pitch | 1 | SKF/NSK | 4 € |
| 8 | **Head assembly** | `head_link` | Crâne, capteurs OAK‑D Pro, électronique | 1 | – | – |
| 9 | **Tube Hub (Roll)** | – | Hub Ø20 mm, usiné | 1 | Usinage interne | – |
|10| **Carter fixe (Roll)** | – | Carter Ø32 mm H7, usiné | 1 | Usinage interne | – |
|11| **Tube Hub (Pitch)** | – | Hub Ø20 mm (identique) | 1 | Usinage interne | – |
|12| **Carter fixe (Pitch)** | – | Carter Ø32 mm H7 (identique) | 1 | Usinage interne | – |
|13| **Circlip E20** | – | Retenue axiale haute | 2 | Stock standard | 0.30 € |
|14| **Solénoïde LEX‑SOLEN‑04** | – | Parking brake du Pitch | 2 | LEX | 3 € |
|15| **Visserie M3 / M4** | – | Jeux de vis (4×M3, 6×M4, 4×M4) | 1 set | Stock standard | 0.50 € |

*Total coût matériel estimé (hors usinage) ≈  ≈  30 €.*

---

## 4. État de la Conception (CAD & Simulation)

| Élément | Fichier CAD (Fusion 360) | Version | Statut |
|---------|--------------------------|---------|--------|
| **Neck v28** (assemblage complet) | `Neck_v28.f3d` | v28 (Mars 2026) | **Validé** – Export URDF testé dans RViz, axes conformes. |
| **Hub Roll** | `Hub_Roll.f3d` | v1 (Mars 2026) | **Validé** – Prototype fonctionnel avec roulement 6804‑2RS. |
| **Carter Roll** | `Carter_Roll.f3d` | v1 (Mars 2026) | **Validé** – Alésage Ø32 mm H7. |
| **Bracket Pitch (U‑shape)** | `Bracket_Pitch_U.f3d` | v1 (Mai 2026) | **Validé** – Conception “Yoke Mount” avec 2× 6804‑2RS. |
| **Hub Pitch** | `Hub_Pitch.f3d` | v1 (Mai 2026) | **Validé** – Identique au hub Roll. |
| **Carter Pitch** | `Carter_Pitch.f3d` | v1 (Mai 2026) | **Validé** – Identique au carter Roll. |
| **Solénoïde Parking Brake** | `Brake_Pitch.f3d` | v1 (Mai 2026) | **Validé** – Intégré sur le palier fixe arrière. |
| **Simulation dynamique (Gazebo)** | `neck_sim.world` | v1 (Mai 2026) | **Validé** – Couple gravitationnel (0.69 N·m) < couple nominal (1.6 N·m). |

---

## 5. Instructions de Montage Critiques  

### 5.1 Généralités  
1. **Orientation Fusion 360** : Le robot doit être orienté **regardant X+** (ViewCube → « Front » à droite).  
2. **Nomage** : Tous les composants doivent être renommés selon le tableau §2.2 avant export URDF.  
3. **Contrôle d’alignement** : Après chaque étape, faire tourner le moteur à la main → vérifier l’absence de jeu axial ou radial.  

### 5.2 Montage du Roll (Solution 4 – 6804‑2RS)  

| Étape | Action | Détail clé |
|-------|--------|------------|
| 1 | **Pré‑assemblage du roulement** | Emmancher la bague extérieure du 6804‑2RS dans le carter fixe (alésage Ø32 mm H7). Ne pas serrer les vis du carter à ce stade. |
| 2 | **Fixation du stator** | Viser le RS‑05 au torse avec 4×M3 (profondeur 8 mm). |
| 3 | **Montage du hub** | Aligner le hub Ø20 mm sur le boss de centrage du rotor (Ø17.7 mm). Viser 6×M4 (≈1.5 N·m). |
| 4 | **Insertion du roulement** | Glisser la bague intérieure du 6804‑2RS dans le tube hub (diamètre Ø20 mm). |
| 5 | **Retenue axiale haute** | Installer le circlip E20 dans la gorge prévue sur le hub. |
| 6 | **Fixation du carter** | Aligner le carter (bague extérieure) sur le hub, laisser les vis libres, tourner le moteur → le roulement auto‑centre. Serrage final des vis du carter au couple recommandé (≈ 2 N·m). |
| 7 | **Montage de la tête** | Fixer la structure de la tête sur le hub avec 4×M4. |
| 8 | **Vérification** | Actionner `neck_roll_joint` via `joint_state_publisher_gui` : rotation fluide, aucune vibration. |

### 5.3 Montage du Pitch (Tilt) – Yoke Mount avec 2× 6804‑2RS  

| Étape | Action | Détail clé |
|-------|--------|------------|
| 1 | **Fabrication du bracket en U** | Usinage en une seule prise CNC pour garantir coaxialité des deux alésages (Ø 32 mm H7). |
| 2 | **Montage du roulement avant** | Identique à la procédure Roll (bague extérieure dans le bras avant du U, bague intérieure dans le hub). |
| 3 | **Montage du roulement arrière** | Bague extérieure logée dans le palier fixe arrière (fixé au torse). Bague intérieure reçoit l’axe du bras arrière du U. |
| 4 | **Fixation du rotor** | Viser le RS‑05 sur le hub avant (6×M4). |
| 5 | **Assemblage du U** | Engager les deux bras du U autour du hub (avant) et de l’axe arrière (bague intérieure). |
| 6 | **Serrage final** | Vis du bras arrière (fixées au torse) serrées à 2 N·m. |
| 7 | **Installation du solénoïde de parking** | Fixer les deux solénoïdes LEX‑SOLEN‑04 sur le palier fixe arrière ; aligner la goupille avec le perçage du bras arrière. |
| 8 | **Vérification dynamique** | Actionner `neck_pitch_joint` : mouvement fluide, aucune contrainte latérale. Tester le parking brake (déverrouillage → mouvement, verrouillage → blocage). |

### 5.4 Points de Vigilance  

* **Concentricité** : L’alésage du hub (Ø 17.7 mm) et le trou du rotor doivent être usinés en une seule prise CNC. Toute décalée > 0.05 mm entraîne usure prématurée du roulement.  
* **Retenue axiale** : Le circlip E20 doit être correctement enclenché ; sinon le roulement peut migrer sous charge.  
* **Couple de serrage** : Respecter les couples indiqués (M4 ≈ 1.5 N·m, vis du carter ≈ 2 N·m). Un serrage excessif déforme le roulement.  
* **Orientation des axes** : Après export URDF, vérifier dans RViz que `neck_yaw_joint` tourne autour de Z, `neck_pitch_joint` autour de Y, `neck_roll_joint` autour de X. Inverser le signe dans le `<axis xyz="…"/>` si nécessaire.  
* **Parking brake** : Le solénoïde doit être **normally locked** (alimentation uniquement pour déverrouiller). Vérifier le temps de réponse ≈ 50 ms.  

---

## 6. Backlog Technique & Questions en Suspens  

| # | Sujet | Statut | Commentaire / Action requise |
|---|-------|--------|------------------------------|
| 1 | **Fournisseur exact du bracket U‑Pan (Yaw)** | [À COMPLÉTER] | Recherche de catalogue ou devis auprès fournisseurs mécaniques. |
| 2 | **Fournisseur du tube hub et du carter (usinage interne)** | [À COMPLÉTER] | Définir si usinage interne ou sous‑traitance (ex : Protolabs). |
| 3 | **Tolérances d’alésage H7 / k6** | Validé (interne) | Confirmer avec le fabricant de pièces usinées. |
| 4 | **Intégration du firmware de parking brake** | En cours (v0.5.0.9) | Tester la séquence ROS 2 `Solenoid_Node` → `Motor_Node`. |
| 5 | **Gestion thermique du RS‑05 sous charge continue** | [À COMPLÉTER] | Mesurer température à 100 % du couple pendant 30 min. |
| 6 | **Évaluation du bruit acoustique du Roll** | [À COMPLÉTER] | Mesure dB SPL en condition de marche. |
| 7 | **Documentation du câblage des 3 RS‑05 (schéma électrique)** | [À COMPLÉTER] | Créer le schéma de puissance 24 V → drivers → RS‑05. |
| 8 | **Validation du modèle dynamique Gazebo (inerties)** | En cours | Exporter les inerties depuis Fusion 360 et comparer aux mesures expérimentales. |

---

## 7. Roadmap & Itérations Futures  

| Future Iteration | Objectif | Principales Modifications envisagées |
|------------------|----------|--------------------------------------|
| **V2.0 – Allongement du cou** | Augmenter le rayon d’action de la tête (±60° Pitch/Yaw) | Introduire réducteurs planétaires (ratio ≈ 5:1) ; motoriser le Yaw avec RS‑06 (plus de couple). |
| **V2.1 – Capteur de force au cou** | Mesurer les charges d’interaction avec l’environnement | Intégrer un capteur de contrainte (strain‑gauge) dans le bracket Yaw. |
| **V3 – Cou à 6 DOF** | Ajouter un axe de **roll‑yaw** combiné pour mouvements de torsion | Redessiner le hub avec double roulement (6804‑2RS + 6804‑2RS) et ajouter un moteur supplémentaire. |
| **V4 – Système de refroidissement actif** | Dissiper la chaleur des RS‑05 en charge continue | Canalisation d’air forcé via micro‑ventilateurs intégrés au carter. |

*Ces itérations sont listées uniquement à titre de planification et **n’apparaissent pas** dans les tableaux principaux du présent document.*  

---  

**Fin du document consolidé – Version V1.x (Mars/Mai 2026).**  