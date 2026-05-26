# 🦾 Spécifications Finales : Tête et Cou (D‑Bot) – Version **V1.x** *(Mars / Mai 2026)*

---

## 1. Vue d’Ensemble (Version Actuelle)

Le sous‑assemblage **Cou (Neck)** du D‑Bot comporte **2 DOF (Degrés de Liberté)** :

| DOF | Axe (URDF) | Mouvement | Motorisation | Réduction | Couple nominal | Couple pic |
|-----|------------|-----------|--------------|-----------|----------------|------------|
| **Yaw (Pan)** | **Z** (vertical) | Rotation gauche‑droite de la tête | **RobStride RS‑05** (Moteur 1) | Direct : 1 : 1 (pas de réducteur) | 1.6 N·m | 5.5 N·m |
| **Pitch (Tilt)** | **Y** (latéral) | Inclinaison avant‑arrière (oui/non) | **RobStride RS‑05** (Moteur 2) | Direct : 1 : 1 | 1.6 N·m | 5.5 N·m |

*La masse totale de la tête (structure + capteurs OAK‑D Pro FF + électronique) ≈ 2 kg.*

Le **cou** est monté sur le **torse** (link `torso_link`). Chaque joint révolute possède une amplitude de ±90° (Yaw) ou ±45° (Pitch) et un effort maximal de **5.5 N·m** (voir tableau 2). L'axe Roll n'est pas implémenté sur cette version.

---

## 2. Spécifications Matérielles Validées

### 2.1 Tableau récapitulatif des joints (URDF)

| Joint URDF | Type | Axe (xyz) | Limites (rad) | Limites (°) | Effort max (N·m) | Vitesse max (rad/s) |
|------------|------|-----------|---------------|-------------|------------------|----------------------|
| `neck_yaw_joint`   | revolute | 0 0 1 (Z) | [-1.57 , 1.57] | ±90° | 5.5 | 3.14 |
| `neck_pitch_joint` | revolute | 0 1 0 (Y) | [-0.79 , 0.79] | ±45° | 5.5 | 3.14 |
| `head_fixed_joint` | fixed    | – | – | – | – | – |

### 2.2 Moteurs RS‑05 (2 unités)

| Référence | Masse (g) | Dimensions (mm) | Couple nominal (N·m) | Couple pic (N·m) | Alimentation | Vitesse max (rpm) | Fournisseur |
|-----------|-----------|-----------------|----------------------|------------------|---------------|-------------------|-------------|
| **RS‑05‑1** (Yaw) | 191 | 46 × 46 × 44 | 1.6 | 5.5 | 48 V DC (15‑60V) | 120 | RobStride |
| **RS‑05‑2** (Pitch) | 191 | idem | 1.6 | 5.5 | idem | 120 | RobStride |

> **Note** : Le RS‑05 ne possède aucun arbre de sortie. La transmission du couple se fait via la face du rotor (plot de centrage + trous M4).
>
> > [!IMPORTANT]
> > **Vigilance Développement (Protocole MIT vs Limites Physiques) :**
> > Dans le firmware officiel de RobStride et la bibliothèque de pilotes constructeur (`RobStride_Control/python/robstride_dynamics/table.py`), le moteur **RS-05** utilise les constantes de mise à l'échelle (scaling factors) du protocole CAN MIT suivantes :
> > *   **Torque Range (Couple max d'échelle) :** **`17.0 N·m`** (et non 5.5 N·m)
> > *   **Velocity Range (Vitesse max d'échelle) :** **`33.0 rad/s`** (et non 12.57 rad/s)
> > 
> > **Le piège d'ingénierie :** Si vous implémentez un contrôleur en mode MIT à haute fréquence (ex: MoveIt / ros2_control), vous **devez** utiliser ces facteurs d'échelle constructeurs de **17.0** et **33.0** pour encoder/décoder les paquets 16-bit CAN (sinon vos commandes réelles subiront un gain erroné d'un facteur $\approx 3$). En revanche, vous devez brider vos commandes dans le planificateur logiciel à des **limites opérationnelles maximales** de **5.5 N·m** et **3.14 rad/s (ou 12.57 rad/s)** pour protéger la mécanique.

### 2.3 Roulements (solution de support externe – **Solution 4**)

| Référence | Type | Ø Int. (mm) | Ø Ext. (mm) | Largeur (mm) | Charge radiale (kN) | Charge axiale (N) | Prix (≈) | Fournisseur |
|-----------|------|-------------|-------------|--------------|----------------------|-------------------|----------|-------------|
| **6804‑2RS** (Yaw) | Radial étanche, 2 RS | 20 | 32 | 7 | 3.0 | 1 900 | 3‑5 € | SKF / NSK / Amazon |
| **6804‑2RS** (second, Pitch) | idem | idem | idem | idem | idem | idem | idem | idem |

### 2.4 Pièces mécaniques associées (Solution 4 – Hub réduit)

| Pièce | Matériau | Dimensions principales | Fonction | Quantité | Fabrication / Fournisseur |
|-------|----------|------------------------|----------|----------|---------------------------|
| **Tube Hub** | Al 6061 (extrudé puis usiné) | Ø 20 mm (int.) – Ø 22 mm (ext.) – hauteur ≈ 12‑15 mm | Support rotor RS‑05, accueille la bague intérieure du 6804‑2RS | 2 | Usinage interne |
| **Carter fixe** | Al 6061 | Alésage Ø 32 mm (H7) – épaisseur ≥ 3 mm | Emmanche la bague extérieure du 6804‑2RS, fixé au torse (Yaw) ou chape (Pitch) | 2 | Usinage interne |
| **Bride d’adaptation** | Al 6061 | Ø 20 mm (cercle de centrage) + 6×M4 8 mm | Fixe le hub sur le rotor (vis M4) | 2 | Usinage interne |
| **Circlip E20** | Acier ressort | – | Retenue axiale haute du hub | 2 | Stock standard |
| **Visserie** | Acier M3 / M4 | – | Fixations diverses (4×M3 torse, 6×M4 hub‑rotor, 4×M4 tête‑hub) | 1 set | Visserie standard |
| **Solénoïde de blocage** (parking brake – Pitch) | – | 50 × 16 × 19 mm | Verrouillage mécanique du Tilt en position « parking » | 2 (un par côté) | LEX‑SOLEN‑04, 12 VDC, 0.6 A |

---

## 3. Nomenclature (BOM Locale)

| # | Référence interne | Nom URDF (link / joint) | Description détaillée | Quantité | Fournisseur / Source | Prix Unitaire (€) |
|---|-------------------|--------------------------|-----------------------|----------|----------------------|-------------------|
| 1 | **robstride05 v1:1** | `neck_yaw_motor` (dans `neck_yaw_link`) | Moteur RS‑05 – Yaw | 1 | RobStride | – |
| 2 | **U‑Pan v15:1** | `neck_yaw_bracket` (fusionné) | Bracket en U support Yaw (Pan→Tilt) | 1 | [À COMPLÉTER] | – |
| 3 | **robstride05 v1:2** | `neck_pitch_motor` (dans `neck_pitch_link`) | Moteur RS‑05 – Pitch | 1 | RobStride | – |
| 4 | **Tilt v14:1** | `neck_pitch_bracket` (dans `neck_pitch_link`) | Bracket Pitch (U‑shape / chape) | 1 | [À COMPLÉTER] | – |
| 5 | **6804_2rs v1:1** | `neck_yaw_bearing` (fixed) | Roulement 6804‑2RS – Yaw | 1 | SKF/NSK | 4 € |
| 6 | **6804_2rs v1:2** | `neck_pitch_bearing` (fixed) | Roulement 6804‑2RS – Pitch | 2 | SKF/NSK | 4 € |
| 7 | **Head assembly** | `head_link` | Crâne, capteurs OAK‑D Pro, électronique | 1 | – | – |
| 8 | **Tube Hub (Yaw)** | – | Hub Ø20 mm, usiné | 1 | Usinage interne | – |
| 9 | **Carter fixe (Yaw)** | – | Carter Ø32 mm H7, usiné | 1 | Usinage interne | – |
|10 | **Tube Hub (Pitch)** | – | Hub Ø20 mm, usiné (identique) | 1 | Usinage interne | – |
|11 | **Carter fixe (Pitch)** | – | Carter Ø32 mm H7, usiné (identique) | 1 | Usinage interne | – |
|12 | **Circlip E20** | – | Retenue axiale haute | 2 | Stock standard | 0.30 € |
|13 | **Solénoïde LEX‑SOLEN‑04** | – | Parking brake du Pitch | 2 | LEX | 3 € |
|14 | **Visserie M3 / M4** | – | Jeux de vis (4×M3, 6×M4, 4×M4) | 1 set | Stock standard | 0.50 € |

*Total coût matériel estimé (hors usinage) ≈ 19 €.*

---

## 4. État de la Conception (CAD & Simulation)

| Élément | Fichier CAD (Fusion 360) | Version | Statut |
|---------|--------------------------|---------|--------|
| **Neck v28** (assemblage complet) | `Neck_v28.f3d` | v28 (Mars 2026) | **Validé** – Export URDF 2-DOF testé dans RViz, axes conformes. |
| **Hub Yaw** | `Hub_Yaw.f3d` | v1 (Mars 2026) | **Validé** – Prototype fonctionnel avec roulement 6804‑2RS. |
| **Carter Yaw** | `Carter_Yaw.f3d` | v1 (Mars 2026) | **Validé** – Alésage Ø32 mm H7. |
| **Bracket Pitch (U‑shape)** | `Bracket_Pitch_U.f3d` | v1 (Mai 2026) | **Validé** – Conception “Yoke Mount” avec 2× 6804‑2RS. |
| **Hub Pitch** | `Hub_Pitch.f3d` | v1 (Mai 2026) | **Validé** – Identique au hub Yaw. |
| **Carter Pitch** | `Carter_Pitch.f3d` | v1 (Mai 2026) | **Validé** – Identique au carter Yaw. |
| **Solénoïde Parking Brake** | `Brake_Pitch.f3d` | v1 (Mai 2026) | **Validé** – Intégré sur le palier fixe arrière. |
| **Simulation dynamique (Gazebo)** | `neck_sim.world` | v1 (Mai 2026) | **Validé** – Accélération dynamique du Yaw validée, couple Pitch < couple nominal. |

---

## 5. Instructions de Montage Critiques

### 5.1 Généralités
1. **Orientation Fusion 360** : Le robot doit être orienté **regardant X+** (ViewCube → « Front » à droite).
2. **Nommage** : Tous les composants doivent être renommés selon le tableau §2.2 avant export URDF.
3. **Contrôle d’alignement** : Après chaque étape, faire tourner le moteur à la main → vérifier l’absence de jeu axial ou radial.

### 5.2 Montage du Yaw (Solution 4 – 6804‑2RS)

| Étape | Action | Détail clé |
|-------|--------|------------|
| 1 | **Pré‑assemblage du roulement** | Emmancher la bague extérieure du 6804‑2RS dans le carter fixe (alésage Ø32 mm H7). Ne pas serrer les vis du carter à ce stade. |
| 2 | **Fixation du stator** | Visser le RS‑05 (Yaw) au torse avec 4×M3 (profondeur 8 mm). |
| 3 | **Montage du hub** | Aligner le hub Ø20 mm sur le boss de centrage du rotor (Ø17.7 mm). Visser 6×M4 (≈1.5 N·m). |
| 4 | **Insertion du roulement** | Glisser la bague intérieure du 6804‑2RS dans le tube hub (diamètre Ø20 mm). |
| 5 | **Retenue axiale haute** | Installer le circlip E20 dans la gorge prévue sur le hub. |
| 6 | **Fixation du carter** | Aligner le carter (bague extérieure) sur le hub, laisser les vis libres, tourner le moteur → le roulement s'auto‑centre. Serrage final des vis du carter au couple recommandé (≈ 2 N·m). |
| 7 | **Montage du bracket Pitch** | Fixer la structure en U du Yaw bracket (`U-Pan v15:1`) sur le hub avec 4×M4. |
| 8 | **Vérification** | Actionner `neck_yaw_joint` via `joint_state_publisher_gui` : rotation fluide, aucune vibration. |

### 5.3 Montage du Pitch (Tilt) – Yoke Mount avec 2× 6804‑2RS

| Étape | Action | Détail clé |
|-------|--------|------------|
| 1 | **Fabrication du bracket en U** | Usinage en une seule prise CNC pour garantir la coaxialité des deux alésages (Ø 32 mm H7). |
| 2 | **Montage du roulement avant** | Identique à la procédure Yaw (bague extérieure dans le bras avant du U, bague intérieure dans le hub rotor). |
| 3 | **Montage du roulement arrière** | Bague extérieure logée dans le palier fixe arrière (fixé au torse). Bague intérieure reçoit l’axe du bras arrière du U. |
| 4 | **Fixation du rotor** | Visser le RS‑05 (Pitch) sur le hub avant (6×M4). |
| 5 | **Assemblage du U** | Engager les deux bras du U autour du hub (avant) et de l’axe arrière (bague intérieure). |
| 6 | **Serrage final** | Vis du bras arrière (fixées au torse) serrées à 2 N·m. |
| 7 | **Installation du solénoïde de parking** | Fixer les deux solénoïdes LEX‑SOLEN‑04 sur le palier fixe arrière ; aligner la goupille avec le perçage du bras arrière du U. |
| 8 | **Vérification dynamique** | Actionner `neck_pitch_joint` : mouvement fluide, aucune contrainte latérale. Tester le parking brake (déverrouillage → mouvement, verrouillage → blocage). |

### 5.4 Points de Vigilance

* **Concentricité** : L’alésage du hub (Ø 17.7 mm) et le trou du rotor doivent être usinés en une seule prise CNC. Tout décalage > 0.05 mm entraîne une usure prématurée du roulement.
* **Retenue axiale** : Le circlip E20 doit être correctement enclenché ; sinon le roulement peut migrer sous charge.
* **Couple de serrage** : Respecter les couples indiqués (M4 ≈ 1.5 N·m, vis du carter ≈ 2 N·m). Un serrage excessif déforme le roulement.
* **Orientation des axes** : Après export URDF, vérifier dans RViz que `neck_yaw_joint` tourne autour de Z et `neck_pitch_joint` autour de Y. Inverser le signe dans le `<axis xyz="…"/>` si nécessaire.
* **Parking brake** : Le solénoïde doit être **normally locked** (alimentation uniquement pour déverrouiller). Vérifier le temps de réponse ≈ 50 ms.

---

## 6. Backlog Technique & Questions en Suspens

| # | Sujet | Statut | Commentaire / Action requise |
|---|-------|--------|------------------------------|
| 1 | **Fournisseur exact du bracket U‑Pan (Yaw)** | [À COMPLÉTER] | Recherche de catalogue ou devis auprès fournisseurs mécaniques. |
| 2 | **Fournisseur du tube hub et du carter (usinage interne)** | [À COMPLÉTER] | Définir si usinage interne ou sous‑traitance (ex : Protolabs). |
| 3 | **Tolérances d’alésage H7 / k6** | Validé (interne) | Confirmer avec le fabricant de pièces usinées. |
| 4 | **Intégration du firmware de parking brake** | En cours (v0.5.0.9) | Tester la séquence ROS 2 `Solenoid_Node` → `Motor_Node`. |
| 5 | **Gestion thermique du RS‑05 sous charge continue** | [À COMPLÉTER] | Mesurer la température du Pitch à 100 % du couple pendant 30 min. |
| 6 | **Documentation du câblage des 2 RS‑05 (schéma électrique)** | [À COMPLÉTER] | Créer le schéma de puissance 48 V → drivers → RS‑05. |
| 7 | **Validation du modèle dynamique Gazebo (inerties)** | En cours | Exporter les inerties depuis Fusion 360 et comparer aux mesures expérimentales. |

---

## 7. Roadmap & Itérations Futures

| Future Iteration | Objectif | Principales Modifications envisagées |
|------------------|----------|--------------------------------------|
| **V2.0 – Allongement du cou** | Augmenter le rayon d’action de la tête (±60° Pitch/Yaw) | Introduire réducteurs planétaires (ratio ≈ 5:1) ; motoriser le Yaw avec RS‑06 (plus de couple). |
| **V2.1 – Capteur de force au cou** | Mesurer les charges d’interaction avec l’environnement | Intégrer un capteur de contrainte (strain‑gauge) dans le bracket Yaw. |
| **V3 – Ajout de l'Axe de Roll (3 DOF)** | Ajouter un axe de **Roll** (oreille-épaule) ou de torsion combinée | Intégrer un troisième moteur RS-05 horizontal pointant vers l'avant, avec double roulement de support. |
| **V4 – Système de refroidissement actif** | Dissiper la chaleur des RS‑05 en charge continue | Canalisation d’air forcé via micro‑ventilateurs intégrés au carter. |

*Ces itérations sont listées uniquement à titre de planification et **n’apparaissent pas** dans les tableaux principaux du présent document.*

---

## 8. Validation CAO Haute Précision (Fusion 360)

Les caractéristiques physiques et cinématiques du sous-assemblage ont été validées par extraction directe des propriétés volumétriques et des liaisons fonctionnelles du modèle CAO actif **`neck_head_assembly v158`** (Mai 2026).

### 8.1 Caractéristiques Physiques CAO (Matériau Acier par défaut)

| Link URDF | Masse CAO brute (kg) | Volume CAO ($m^3$) | Centre de Gravité ($X, Y, Z$) relatif au monde (m) |
|---|---|---|---|
| `torso_link` | 0.4815 | $6.133 \times 10^{-5}$ | $[-0.0379, 0.0349, -0.2282]$ |
| `neck_yaw_link` | 1.3176 | $1.678 \times 10^{-4}$ | $[-0.0379, 0.0345, -0.1622]$ |
| `neck_pitch_link` (Tête complète) | 13.3621 | $1.702 \times 10^{-3}$ | $[-0.0386, 0.0353, -0.0529]$ |

### 8.2 Calcul de la Masse Réelle Imprimée (PLA à 20% d'infill)

Dans la CAO, le casque Mandalorian (`Casque_Mando_Final-k-bot`) est modélisé comme un bloc solide en acier, ce qui donne une masse brute irréaliste de **12.29 kg**. En impression 3D réelle en PLA avec un taux de remplissage standard de **20% (infill)** et 4 parois (densité moyenne imprimée $\approx 0.38\text{ g/cm}^3$), la masse réelle est calculée ainsi :

$$\text{Masse Casque Mando (PLA)} = 1565\text{ cm}^3 \text{ (volume)} \times 0.38\text{ g/cm}^3 \approx 595\text{ g}$$

#### Bilan de Masse Réel Consolide (Tête et Cou) :
*   **Structure Plastique PLA (Casque + Brackets + Hubs) :** ~715 g
*   **Actionneurs Moteurs (2x RobStride RS-05) :** 382 g (2x 191 g, overrides réels)
*   **Paliers mécaniques (3x Roulements 6804-2RS) :** 54 g (3x 18 g, overrides réels)
*   **Sécurité Pitch (2x Solénoïdes LEX-SOLEN-04) :** 60 g (2x 30 g)
*   **Électronique embarquée (ESP32-S3 Xiao + ReSpeaker XVF3800) :** ~87 g
*   **Caméra de vision (OAK-D Pro dans son boîtier léger) :** ~115 g

*   **Masse totale en mouvement (Tête assemblée sur joint Pitch) :** **~1.03 kg** (parfaitement dans les capacités dynamiques nominales de 1.6 N.m du RS-05).
*   **Masse totale du sous-ensemble (Yaw + Pitch) :** **~1.41 kg**.

### 8.3 Noms de Référence CAO Validés (Nomenclature CAO)
Le modèle CAO intègre les références industrielles exactes suivantes, validant la cohérence cinématique 2-DOF du robot :
*   **Moteurs :** `robstride05 Pan` (Yaw) et `robstride05 tilt` (Pitch).
*   **Roulements :** `6804_2rs Pan` (Yaw), `6804_2rs tilt droite` (Pitch) et `6804_2rs tilt gauche` (Pitch) $\rightarrow$ **3 roulements 6804-2RS au total**.
*   **Caméra principale :** `DM9098Pro_enclosure v1` (OAK-D Pro).
*   **Processeur audio :** `respeaker_mic_array_xvf3800_1_with-xiao-0820 v1` (Seeed Studio).

---

**Fin du document consolidé – Version V1.x (Mars/Mai 2026).**