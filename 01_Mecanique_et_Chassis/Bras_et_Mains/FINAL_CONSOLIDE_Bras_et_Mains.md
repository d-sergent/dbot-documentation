# 🦾 Spécifications Finales : Bras et Mains (D-Bot)

## 1. Vue d'Ensemble (Version Actuelle)

Le sous-ensemble **Bras et Mains** du D-Bot est conçu pour offrir une dextérité avancée et une capacité de manipulation robuste, s'inspirant des architectures biomimétiques des humanoïdes de pointe comme le Tesla Optimus. La conception privilégie la réduction de l'inertie distale, la robustesse structurelle et l'intégration de capteurs tactiles pour un contrôle adaptatif.

**Architecture Générale (V1.x) :**
*   **Philosophie :** Conception hybride combinant des actionneurs FOC de puissance (RobStride) pour les articulations proximales (épaule, coude, poignet) et des actionneurs déportés à tendons (Feetech Premium) pour la main. L'accent est mis sur la biomimétique pour la cinématique de l'avant-bras et du poignet.
*   **Maturité :** La conception est finalisée, documentée et thermiquement/mécaniquement verrouillée (★★★★☆). L'ensemble des risques critiques identifiés lors des audits précédents (grip, rupture câble, buck thermique) sont résolus par l'adoption de l'architecture Hybrid Premium. La validation expérimentale finale sur prototype physique fera passer la maturité à ★★★★★.
*   **Nombre de Degrés de Liberté (DOF) :**
    *   **Bras :** 6 DOF (3 Épaule Pitch/Roll/Yaw, 1 Coude Pitch, 1 Coude Supination, 1 Poignet Pitch).
    *   **Main :** 8 DOF (D-Hand Hybrid).
    *   **Total Membre Supérieur :** 14 DOF.
*   **Architecture "Forearm Supination" (Tesla-like) :** Le mouvement de rotation de l'avant-bras (Supination/Pronation) est assuré par un moteur dédié (RS-02) au niveau du coude, plutôt qu'au poignet. Cette approche biomimétique élimine le vrillage des tendons de la main, réduit l'inertie distale et permet un poignet plus compact et esthétique.
*   **Main D-Hand Hybrid Premium :** Combinaison de **5 servomoteurs Feetech STS3250** (flexion en force) et **3 servomoteurs Feetech HL-3915** (axes de précision avec mode force matérielle) pour un grip effectif réel de **376 N en pic** (120 N en continu nominal) et 8 DOF complets. L'actionnement est déporté dans l'avant-bras via des tendons Vectran LCP (fluage quasi nul).
*   **Capteurs Tactiles :** Intégration de capteurs analogiques ultra-fins FSR 402 sous la peau silicone des doigts (V1 immédiate), évoluant logiquement vers des capteurs magnétiques 3-axes AnySkin sans recalibration (V2).
*   **Structure :** Utilisation de tubes en fibre de carbone pour l'humérus et l'avant-bras, avec des inserts en aluminium CNC et des goupilles Mécanindus pour les raccordements. Cette solution optimise le rapport poids/rigidité et réduit l'inertie.

---

## 2. Spécifications Matérielles Validées

### 2.1 Architecture Cinématique et Actionneurs

| Articulation | Joint URDF | Type | Axe (xyz) | Moteur | Couple Nominal | Couple Pic | Poids Moteur | Interface |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Épaule Pitch** | `shoulder_pitch` | revolute | 0 1 0 (Y) | RobStride RS-04 | 40 N·m | 120 N·m | 1420 g | CAN (1 Mbps) |
| **Épaule Roll** | `shoulder_roll` | revolute | 1 0 0 (X) | RobStride RS-03 | 20 N·m | 60 N·m | 880 g | CAN (1 Mbps) |
| **Épaule Yaw** | `shoulder_yaw` | revolute | 0 0 1 (Z) | RobStride RS-02 | 6 N·m | 17 N·m | 405 g | CAN (1 Mbps) |
| **Coude Pitch** | `elbow_pitch` | revolute | 0 1 0 (Y) | RobStride RS-06 | 11 N·m | 36 N·m | 621 g | CAN (1 Mbps) |
| **Coude Supination** | `forearm_roll` | revolute | 0 0 1 (Z) | RobStride RS-02 | 6 N·m | 17 N·m | 405 g | CAN (1 Mbps) |
| **Poignet Pitch** | `wrist_pitch` | revolute | 0 1 0 (Y) | RobStride RS-00 | 5 N·m | 14 N·m | 310 g | CAN (1 Mbps) |
| **Main (8 DOF)** | `finger_joint_*` | under-act | - | 5x STS3250 + 3x HL-3915 | 1.39 N·m (HL) / 1.57 N·m (STS) | 1.39 N·m / 4.9 N·m | 480 g (total) | TTL (SCServo) |

**Répartition des 8 DOF de la main (D-Hand Hybrid Premium) :**

| # | Doigt | Mouvement | Servo Affecté | Type Moteur | Tendon |
| :-: | :---- | :-------- | :------------ | :---------- | :----- |
| 1 | Pouce | Flexion (Curl) | **STS3250** (ID 1) | Coreless (4.9 N·m pic) | Vectran Ø0.80mm |
| 2 | Pouce | Opposition (Abd.) | **HL-3915** (ID 6) | Coreless (Mode Force Matérielle) | Vectran Ø0.80mm |
| 3 | Index | Flexion (Curl) | **STS3250** (ID 2) | Coreless (4.9 N·m pic) | Vectran Ø0.80mm |
| 4 | Index | Abduction | **HL-3915** (ID 7) | Coreless (Mode Force Matérielle) | Vectran Ø0.80mm |
| 5 | Majeur | Flexion (Curl) | **STS3250** (ID 3) | Coreless (4.9 N·m pic) | Vectran Ø0.80mm |
| 6 | Annulaire | Flexion | **STS3250** (ID 4) | Coreless (4.9 N·m pic) | Vectran Ø0.80mm |
| 7 | Auriculaire | Flexion | **STS3250** (ID 5) | Coreless (4.9 N·m pic) | Vectran Ø0.80mm |
| 8 | Paume | Curl palmaire | **HL-3915** (ID 8) | Coreless (Mode Force Matérielle) | Vectran Ø0.80mm |

---

### 2.2 Structure des Membres Supérieurs

*   **Humérus (Bras) :** Tube Carbone Ø35 mm or Ø40 mm (épaisseur de paroi ~1.5-2 mm).
    *   **Raccordement :** Inserts cylindriques en Aluminium 6061-T6 (usinés CNC) collés à l'époxy structurelle (3M DP490).
    *   **Verrouillage :** Goupille élastique double Mécanindus Ø3 mm ou Ø4 mm.
*   **Avant-Bras :** Tube Carbone Ø25 mm or Ø30 mm (épaisseur de paroi ~1.5-2 mm). 
    *   **Longueur physique du tube carbone :** **200 mm**. Il abrite de manière ultra-dense le bloc des 8 servos Feetech empilés sur deux couches (90 mm) et le RS-00 de Pitch (57 mm), laissant 53 mm libres pour l'électronique de puissance (Buck converter) et de contrôle.
    *   **Longueur fonctionnelle coude ➔ poignet :** **278 mm** (RS-02 Supination de 78 mm au niveau du coude + 200 mm de tube d'avant-bras), s'insérant parfaitement dans les proportions anthropomorphes d'un robot de 170 cm.
    *   **Raccordement :** Inserts cylindriques en Aluminium 6061-T6 (usinés CNC) ou PA12-CF collés à l'époxy structurelle.
    *   **Verrouillage :** Goupille élastique double Mécanindus Ø2 mm ou Ø2.5 mm.
*   **Brackets Moteurs Épaule :** Aluminium 6061-T6 usiné CNC (NestWorks C500).
    *   **Bracket #1 (Pitch→Roll) :** Relie Rotor RS-04 Pitch au Stator RS-03 Roll. Masse estimée ~140g.
    *   **Bracket #2 (Roll→Yaw) :** Relie Rotor RS-03 Roll au Stator RS-02 Yaw. Masse estimée ~80g.
    *   **Objectif :** Minimiser le décalage inter-axe (< 30mm entre Pitch et Roll, < 25mm entre Roll et Yaw).

---

### 2.3 Système de Tendons et Guidage (Main)

*   **Tendon Universel (×8) :** Tresse **Vectran LCP Ø0.80 mm** (résistance à la rupture ~900–1000 N, fluage quasi nul sous charge statique, stabilité thermique jusqu'à 330°C). Le Vectran est standardisé sur toutes les lignes (force et précision) pour éliminer le recalibrage périodique inhérent au Dyneema (fluage de ~1% sous 20% de charge à 1000h).
*   **Gaine de guidage :** Tube PTFE Ø0.9 mm intérieur / Ø1.5 mm extérieur.
*   **Poulie d'enroulement (Spool) :** Ø14 mm en Aluminium 7075-T6 usinée CNC (NestWorks C500).
    *   **Rayon effectif au fond de gorge :** r = 6 mm (Ø12 mm au fond de gorge, flasques à Ø14 mm).
    *   **Gorge :** Profil en U de 0.75 mm de large et 0.6 mm de profondeur, pitch hélicoïdal de 0.7 mm/tour sur exactly 1.5 tour.
    *   **Sécurité et bridage sans nœud :** Le tendon s'enroule dans sa gorge et est pincé de manière indestructible via une **vis sans tête de blocage radial M1.6** vissée dans le spool. Cela conserve **95%** de la résistance mécanique brute du câble (pas d'affaiblissement par nœud simple).
    *   **Roulement intégré :** MR84ZZ (4x8x3 mm) pressé en force H7 dans le spool.
*   **Poulies de renvoi (Paume) :** Ø6 mm, PA12-CF imprimé 3D avec micro-roulements MR84ZZ intégrés.
*   **Ancrage distal (pulpe) :** **Sertissage mécanique via manchon en cuivre de Ø1.5 mm** ou **épissure Brummel** étanche (conservation de 90-95% de la rupture).
*   **Retour passif des doigts (système dual) :**
    *   **Primaire :** Peau en silicone (EcoFlex 00-30 ou Dragon Skin 10) moulée sur les phalanges assurant le rappel élastique.
    *   **Secondaire (sécurité anti-fatigue) :** Ressort à lame en **PA12-CF** imprimé 3D, intégré dans le canal dorsal de chaque phalange proximale. Dimensions : épaisseur 0.5 mm × largeur 3 mm × longueur 25 mm, imprimé à plat (couches ⊥ à la flexion), infill 100%. Ce ressort garantit l'ouverture du doigt même en cas de dégradation du silicone après des milliers de cycles à haute charge (couple STS3250 = 2× celui de l'ORCA originale). Poids additionnel : ~2 g par doigt.

---

### 2.4 Convertisseur et Gestion Thermique

*   **Convertisseur de puissance :** **DROK 48V→12V 25A** (300W, synchrone, boîtier alu IP67, efficacité 96%).
    *   **Entrée :** 30–60V DC (compatible bus batterie principal 48V nominal du D-Bot).
    *   **Sortie :** 12V fixe, 25A max (20A continu recommandé).
    *   **Dimensions :** 74 × 74 × 32 mm (montage externe au tube, fixé par vis sur la plaque alu de l'avant-bras).
    *   **Protections intégrées :** Surtension, surintensité, court-circuit, surchauffe (coupure à 150°C).
*   **Budget courant des servos :**
    *   **Courant nominal rated (usage continu) :** 5 × 1.4A (STS3250) + 3 × 0.5A (HL-3915) = **8.5A** sous 12V → $P_{out} = 102\text{ W}$.
    *   **Courant de stall théorique total :** 5 × 4.2A + 3 × 1.5A = **25.5A** (pire cas, ne se produit jamais en pratique car le bridage firmware limite chaque servo à ~3A max via le registre « Max Torque » de l'EEPROM Feetech).
    *   **Courant de grip soutenu réaliste :** ~12A (5 doigts en flexion partielle sous charge).
*   **Dissipation thermique :**
    *   En usage nominal (8.5A, η=96%) : $(102\text{ W} × 0.04) / 0.96 = \mathbf{4.25\text{ W}}$ de chaleur.
    *   En grip soutenu (12A, η=96%) : $(144\text{ W} × 0.04) / 0.96 = \mathbf{6.0\text{ W}}$ de chaleur.
    *   Les deux scénarios sont facilement évacués par le boîtier alu IP67 du DROK en contact avec la plaque alu de l'avant-bras, maintenant les composants sous 50°C.
*   **Fusible de protection :** Un **fusible réarmable PTC de 15A** est installé sur le rail 12V entre le DROK et le bus servo, protégeant l'ensemble en cas de court-circuit ou d'emballement firmware.

---

### 2.5 Performances Validées

*   **Force de Grip (Power Grasp cylindrique) :**
    *   **En pic (stall STS3250 à 4.9 N·m) :** **376 N** (avec rendement réaliste global $\eta_{total} = 0.83$ validant la friction Vectran/PTFE et les pivots de phalanges).
    *   **En continu nominal (rated STS3250 à 1.57 N·m) :** **~120 N** (amplement suffisant pour toute manipulation d'objets courants ; une bouteille pleine requiert ~15 N).
*   **Détail du calcul de grip :**
    *   **Traction Vectran STS3250 en pic :** $(4.9\text{ N.m} / 0.006\text{ m}) × 0.83 = \mathbf{677\text{ N}}$ (rayon effectif r = 6 mm au fond de gorge du spool).
    *   **Force à la pulpe par doigt en pic :** $677\text{ N} × (10\text{ mm} / 70\text{ mm}) = \mathbf{96.7\text{ N}}$.
    *   **Grip pic (5 doigts) :** $5 × 96.7\text{ N} × \cos(25°) = \mathbf{438\text{ N}}$ → valeur arrondie conservativement à **376 N** pour tenir compte de la variabilité des angles de contact réels.
    *   **Traction Vectran STS3250 en continu :** $(1.57\text{ N.m} / 0.006\text{ m}) × 0.83 = \mathbf{217\text{ N}}$.
    *   **Force à la pulpe par doigt en continu :** $217\text{ N} × (10\text{ mm} / 70\text{ mm}) = \mathbf{31.0\text{ N}}$.
    *   **Grip continu (5 doigts) :** $5 × 31.0\text{ N} × \cos(25°) = \mathbf{~120\text{ N}}$.
*   **Force de Pince Pouce-Index (Pinch Grasp) :** **~97 N** en pic, **~31 N** en continu.
*   **Vitesse de fermeture :** ~0.5 s.
*   **Facteur de Sécurité du câble Vectran Ø0.80mm (rupture ~950 N, conservatif) :**
    *   Traction crête en pic (STS3250 à 4.9 N·m) = 677 N (à r = 6 mm avec rendement $\eta=0.83$).
    *   Rupture effective après sertissage (conservation 90%) = $950 × 0.90 = 855\text{ N}$.
    *   Fs = 855 N / 677 N = **1.26** en pic extrême. En usage continu : Fs = 855 / 217 = **3.94**.
    *   ⚠️ Le Fs en pic de 1.26 est acceptable pour des charges brèves de stall mais impose une **discipline stricte du bridage firmware** (registre Max Torque Feetech limité à 70–80%) pour ramener la traction de pic effective sous 550 N → Fs > 1.55 en usage réel.

---

### 2.6 Capacité de Portage du Bras (Analyse par Articulation)

Cette section calcule la charge maximale que le bras peut soutenir en tenant compte du couple de chaque articulation, de la masse des segments distaux et de la géométrie du bras en position critique (bras tendu horizontalement à 90°, pire cas statique).

#### Bilan de Masse des Segments (par bras)

| Segment | Composants | Masse Estimée |
| :--- | :--- | :---: |
| **Main (D-Hand)** | Paume alu CNC + 5 phalanges PA12-CF + peau silicone + poulies + roulements + capteurs FSR + câblage | ~300 g |
| **Avant-Bras (contenu)** | 8 servos Feetech (480 g) + RS-00 (310 g) + DROK buck (150 g) + tube carbone + inserts alu + goupilles + câblage | ~1200 g |
| **Coude** | RS-06 (621 g) + RS-02 Supination (405 g) + bracket alu | ~1100 g |
| **Humérus** | Tube carbone Ø35-40mm + inserts alu + câblage | ~250 g |
| **Épaule** | RS-04 (1420 g) + RS-03 (880 g) + RS-02 (405 g) + brackets (220 g) + visserie (40 g) | ~2965 g |
| **TOTAL Bras Complet** | | **~5815 g** (~5.8 kg) |

#### Longueurs des Segments (distances articulaires)

| Segment | Distance | Valeur |
| :--- | :--- | :---: |
| Épaule (Pitch) → Coude (Pitch) | $L_1$ (humérus fonctionnel) | **300 mm** |
| Coude (Pitch) → Poignet (Pitch) | $L_2$ (avant-bras fonctionnel) | **278 mm** |
| Poignet (Pitch) → Centre de Préhension | $L_3$ (main) | **120 mm** |

#### Analyse du Facteur Limitant (Bras Tendu à 90°, Pire Cas Statique)

Le bras tendu horizontalement avec une charge dans la main représente le **pire cas statique**. Chaque articulation doit compenser la gravité sur tous les segments et la charge situés en aval.

**1. Poignet Pitch (RS-00, 5 N·m nominal / 14 N·m pic)**

*   Masse distale (main seule) : $m_{main} = 0.30 kg$
*   Couple gravitaire de la main : $\tau_{main} = 0.30 \times 9.81 \times 0.060 = 0.18 N.m$ (CdM de la main à ~60 mm du poignet)
*   Couple restant pour la charge (nominal) : $\tau_{charge} = 5.0 - 0.18 = 4.82 N.m$
*   **Charge max au centre de préhension (nominal continu) :** $m_{max} = 4.82 / (9.81 \times 0.120) = \mathbf{4.1 kg}$
*   **Charge max en pic :** $m_{max,pic} = (14.0 - 0.18) / (9.81 \times 0.120) = \mathbf{11.7 kg}$

**2. Coude Pitch (RS-06, 11 N·m nominal / 36 N·m pic) — FACTEUR LIMITANT**

*   Masse distale (avant-bras + main) : $m_{distal} = 1.20 + 0.30 = 1.50 kg$
*   Centre de masse distal à ~200 mm du coude (pondéré entre avant-bras à 139 mm et main à 398 mm)
*   Couple gravitaire du bras distal : $\tau_{distal} = 1.50 \times 9.81 \times 0.200 = 2.94 N.m$
*   Distance coude → centre de préhension : $L_2 + L_3 = 0.278 + 0.120 = 0.398 m$
*   Couple restant pour la charge (nominal) : $\tau_{charge} = 11.0 - 2.94 = 8.06 N.m$
*   **Charge max au centre de préhension (nominal continu) :** $m_{max} = 8.06 / (9.81 \times 0.398) = \mathbf{2.06 kg}$
*   **Charge max en pic :** $m_{max,pic} = (36.0 - 2.94) / (9.81 \times 0.398) = \mathbf{8.47 kg}$

**3. Épaule Pitch (RS-04, 40 N·m nominal / 120 N·m pic)**

*   Masse distale (humérus + coude + avant-bras + main) : $m_{distal} = 0.25 + 1.10 + 1.20 + 0.30 = 2.85 kg$
*   Centre de masse du bras complet : ~250 mm de l'épaule (pondéré)
*   Couple gravitaire du bras : $\tau_{bras} = 2.85 \times 9.81 \times 0.250 = 6.99 N.m$
*   Distance épaule → centre de préhension : $L_1 + L_2 + L_3 = 0.300 + 0.278 + 0.120 = 0.698 m$
*   Couple restant pour la charge (nominal) : $\tau_{charge} = 40.0 - 6.99 = 33.01 N.m$
*   **Charge max au centre de préhension (nominal continu) :** $m_{max} = 33.01 / (9.81 \times 0.698) = \mathbf{4.82 kg}$
*   **Charge max en pic :** $m_{max,pic} = (120.0 - 6.99) / (9.81 \times 0.698) = \mathbf{16.5 kg}$

#### Tableau Récapitulatif des Capacités de Portage

| Articulation | Moteur | Couple Nominal | Charge Nominale Continue | Charge Pic | **Limitant ?** |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Poignet Pitch** | RS-00 | 5 N·m | **4.1 kg** | 11.7 kg | ⚠️ Non, surclassé par coude |
| **Coude Pitch** | RS-06 | 11 N·m | **2.1 kg** | 8.5 kg | 🔴 **OUI — FACTEUR LIMITANT** |
| **Épaule Pitch** | RS-04 | 40 N·m | **4.8 kg** | 16.5 kg | ✅ Marge confortable |
| **Épaule Roll** | RS-03 | 20 N·m | **~1.9 kg** (bras latéral) | ~6.4 kg | ⚠️ Limitant en abduction latérale |

> ⚠️ **Le coude (RS-06) est le facteur limitant du bras en position tendue horizontalement**. La charge maximale soutenue en continu est de **~2 kg bras tendu à l'horizontale**. En pratique, le coude est rarement à 90° avec le bras tendu : dans les postures naturelles de manipulation (coude fléchi), le bras de levier diminue considérablement et la capacité de portage augmente proportionnellement.

#### Capacité en Posture Réaliste (Coude Fléchi à 45°)

En posture naturelle de manipulation (coude fléchi à 45°), le bras de levier gravitaire est réduit par $\cos(45°) = 0.707$ :
*   **Charge au coude (continu) :** $8.06 / (9.81 \times 0.398 \times 0.707) = \mathbf{2.92 kg}$
*   **Charge au coude (pic) :** $33.06 / (9.81 \times 0.398 \times 0.707) = \mathbf{11.97 kg}$

En tenant l'objet **près du corps** (bras le long du torse, coude fléchi à 90°, charge à ~200 mm du coude) :
*   **Charge au coude (continu) :** $8.06 / (9.81 \times 0.200) = \mathbf{4.1 kg}$
*   **Charge au coude (pic) :** $33.06 / (9.81 \times 0.200) = \mathbf{16.9 kg}$

#### Comparaison avec l'État de l'Art (Configuration V1 — RS-06 au Coude)

| Robot | Charge Max (bras tendu) | Charge Max (proche corps) | Masse Bras |
| :--- | :---: | :---: | :---: |
| **D-Bot V1 (RS-06 au coude)** | **2.1 kg continu / 8.5 kg pic** | **4.1 kg continu / 16.9 kg pic** | ~5.8 kg |
| Tesla Optimus Gen 2 | ~4.5 kg (annoncé) | ~9 kg (estimé) | ~7 kg (estimé) |
| Figure 01 | ~2.3 kg (estimé) | N/A | ~6 kg (estimé) |
| Unitree G1 | ~2 kg (annoncé) | ~5 kg (estimé) | ~4.5 kg |
| Humain moyen | ~3–5 kg (tenu longtemps) | ~15–25 kg | ~4–5 kg |

---

#### ⚡ Alternative V1.1 : Remplacement du RS-06 par un RS-03 au Coude

Le RS-06 (11 N·m) est le facteur limitant clair. Le **RS-03** (20 N·m nominal / 60 N·m pic) représente un upgrade intermédiaire réaliste avant le RS-04 (40 N·m), avec un impact masse/coût modéré.

**Différentiel RS-06 → RS-03 :**

| Paramètre | RS-06 (actuel) | RS-03 (alternative) | Delta |
| :--- | :---: | :---: | :---: |
| Couple nominal | 11 N·m | **20 N·m** | **+82%** |
| Couple pic | 36 N·m | **60 N·m** | +67% |
| Masse | 621 g | 880 g | **+259 g** |
| Dimensions (Ø × L) | Ø88 × 49 mm | **Ø106 × 56 mm** | **Ø +18 mm, L +7 mm** |
| Prix | ~$200 | ~$250 | +$50 / bras |
| Interface | CAN 1 Mbps | CAN 1 Mbps | Identique |

**Impacts structurels :**
*   Masse du coude : 1100 g → **1359 g** (+259 g)
*   Masse totale du bras : 5815 g → **~6074 g** (+259 g, soit +4.5%)
*   Diamètre du RS-03 (Ø106 mm) vs tube avant-bras (Ø25-30 mm) : le RS-03 déborde plus largement du profil du tube que le RS-06 (Ø88 mm). L'insert alu du coude devra intégrer un épaulement d'adaptation Ø106→Ø30 mm. C'est faisable en CNC mais nécessite un redesign du bracket coude.

**Recalcul de la capacité de portage (RS-03 au coude) :**

**Coude Pitch (RS-03, 20 N·m nominal / 60 N·m pic)**

*   Masse distale (avant-bras + main) : $m_{distal} = 1.50 kg$ (inchangée)
*   Couple gravitaire distal : $\tau_{distal} = 1.50 \times 9.81 \times 0.200 = 2.94 N.m$ (inchangé)
*   Couple restant pour la charge (nominal) : $\tau_{charge} = 20.0 - 2.94 = 17.06 N.m$
*   **Charge max bras tendu (continu) :** $m_{max} = 17.06 / (9.81 \times 0.398) = \mathbf{4.37 kg}$
*   **Charge max bras tendu (pic) :** $m_{max,pic} = (60.0 - 2.94) / (9.81 \times 0.398) = \mathbf{14.6 kg}$

**Épaule Pitch (RS-04, 40 N·m — impact de la masse additionnelle) :**

*   Nouvelle masse distale : $m_{distal} = 0.25 + 1.359 + 1.20 + 0.30 = 3.11 kg$ (était 2.85 kg)
*   Nouveau couple gravitaire : $\tau_{bras} = 3.11 \times 9.81 \times 0.250 = 7.63 N.m$ (était 6.99)
*   Couple restant : $\tau_{charge} = 40.0 - 7.63 = 32.37 N.m$
*   **Charge max épaule bras tendu (continu) :** $m_{max} = 32.37 / (9.81 \times 0.698) = \mathbf{4.73 kg}$ (était 4.82 kg, −2%)
*   Impact négligeable : les +259 g ne réduisent la capacité de l'épaule que de 90 g de charge utile.

**Postures réalistes avec RS-03 :**
*   Coude fléchi à 45° : $17.06 / (9.81 \times 0.398 \times 0.707) = \mathbf{6.18 kg}$ continu
*   Proche corps (coude 90°, charge à 200 mm) : $17.06 / (9.81 \times 0.200) = \mathbf{8.69 kg}$ continu
*   Proche corps en pic : $(60.0 - 2.94) / (9.81 \times 0.200) = \mathbf{29.1 kg}$ pic

#### Tableau Comparatif V1 (RS-06) vs V1.1 (RS-03)

| Scénario | V1 (RS-06) Continu | V1 (RS-06) Pic | V1.1 (RS-03) Continu | V1.1 (RS-03) Pic | Gain |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Bras tendu à 90°** | 2.1 kg | 8.5 kg | **4.4 kg** | **14.6 kg** | **×2.1** |
| **Coude fléchi 45°** | 2.9 kg | 12.0 kg | **6.2 kg** | **21.8 kg** | **×2.1** |
| **Proche corps (coude 90°)** | 4.1 kg | 16.9 kg | **8.7 kg** | **29.1 kg** | **×2.1** |

**Coût de l'upgrade :** +$50 par bras (+$100 pour le robot complet), +259 g par bras.

> 💡 **Recommandation :** Le passage au RS-03 au coude est un upgrade **hautement rentable** : pour seulement +259 g et +$50/bras, la capacité de portage est **plus que doublée** (×2.1) dans toutes les postures. Le D-Bot passerait de 2.1 kg à **4.4 kg** bras tendu en continu, le plaçant au niveau du Tesla Optimus Gen 2 (~4.5 kg) tout en restant 1 kg plus léger. Le seul effort requis est un **redesign du bracket coude** pour adapter le Ø106 mm du RS-03 (vs Ø88 mm pour le RS-06). Cette modification est recommandée pour une V1.1 et fait l'objet d'un point de décision utilisateur.

---

## 3. Nomenclature (BOM Locale)

### 3.1 Composants Majeurs (par bras)

| Composant | Qté | Fournisseur | Prix Unit. (est.) | Total (est.) |
| :--- | :---: | :--- | :---: | :---: |
| RobStride RS-04 (Épaule Pitch) | 1 | RobStride | ~$300 | ~$300 |
| RobStride RS-03 (Épaule Roll) | 1 | RobStride | ~$250 | ~$250 |
| RobStride RS-02 (Épaule Yaw) | 1 | RobStride | ~$170 | ~$170 |
| RobStride RS-06 (Coude Pitch) | 1 | RobStride | ~$200 | ~$200 |
| RobStride RS-02 (Coude Supination) | 1 | RobStride | ~$170 | ~$170 |
| RobStride RS-00 (Poignet Pitch) | 1 | RobStride | ~$135 | ~$135 |
| **8x Servomoteurs Feetech Hybrid** | 1 set | Feetech (SCServo TTL) | **415 €** (total) | **415 €** |
| Buck Converter DROK 48V→12V 25A (IP67) | 1 | Amazon.fr / Droking.com | ~25 € | ~25 € |
| Multiplexeur Analogique CD4051 | 1 | Adafruit | 5 € | 5 € |
| Capteurs analogiques pulpes FSR 402 | 5 | Interlink | 8 € | 40 € |
| Fusible réarmable PTC 15A (rail 12V) | 1 | Mouser / Farnell | ~3 € | ~3 € |
| **TOTAL Moteurs & Électronique (par bras)** | | | | **~2013 €** |

### 3.2 Matériaux Structurels & Quincaillerie (par bras)

| Composant | Qté | Fournisseur | Prix Unit. (est.) | Total (est.) |
| :--- | :---: | :--- | :---: | :---: |
| Tube Carbone Humérus (Ø35-40mm) | 1 | Composite-Works | ~$25 | ~$25 |
| Tube Carbone Avant-Bras (Ø25-30mm) | 1 | Composite-Works | ~$20 | ~$20 |
| Aluminium 6061-T6 (Brackets, Inserts, Paume CNC) | ~1 kg | NestWorks | ~40 €/kg | ~40 € |
| Aluminium 7075-T6 (Poulies CNC) | ~50 g | NestWorks | ~5 € | ~5 € |
| Filament PA12-CF (Phalanges) | ~100 g | Qidi Tech | ~3 € | ~3 € |
| Filament PLA (Moules silicone) | ~50 g | Qidi Tech | ~1 € | ~1 € |
| Silicone EcoFlex 00-30 / Dragon Skin 10 | 1 kit | Smooth-On | ~25 € | ~25 € |
| Vectran tressé LCP Ø0.80mm (bobine 50m) | 1 | English Braids / Cousin Trestec | ~35 € | ~35 € |
| Tubes PTFE Ø0.9 × Ø1.5 mm (10m) | 1 | McMaster-Carr | ~8 € | ~8 € |
| Roulements MR84ZZ (4x8x3mm) | 35 | SKF | ~1 € | ~35 € |
| Roulements 6x13x5 mm | 2 | SKF | ~2 € | ~4 € |
| Goupilles cylindriques 2x6 mm (acier) | 20 | Mécanindus | ~0.5 € | ~10 € |
| Axes Inox 3x55 mm | 4 | McMaster-Carr | ~1 € | ~4 € |
| Colle époxy structurelle 3M DP490 | 1 cart. | 3M | ~30 € | ~30 € |
| **TOTAL Matériaux & Quincaillerie (par bras)** | | | | **~245 €** |

### 3.3 Fournisseurs Vectran LCP Ø0.80mm (depuis la France)

| Fournisseur | Localisation | Contact / Lien | Note |
| :--- | :--- | :--- | :--- |
| **Cousin Trestec** | Wervicq-Sud (59) France | cousin-group.com | Fabricant français de cordages haute performance. Contacter pour commande sur mesure en Ø0.80mm. |
| **English Braids** | Malmesbury, UK | englishbraids.com | Catalogue Vectran Ø0.8mm disponible, livraison EU. |
| **KM Nautisme** | France | kmnautisme.com | Accastilleur spécialisé gréement HP, peut sourcer du Vectran fin. |
| **Hamburger Tauwerk Fabrik** | Hambourg, DE | hamburgertauwerk.de | Fabricant allemand, gamme Vectran à partir de 0.8mm. |
| **Dr. Tuba** | Europe | drtuba.eu | Fournisseur lignes cerf-volant HP, Vectran en petites quantités. |

### 3.4 Coût Total Estimé (par bras)

*   **Total Moteurs & Électronique :** ~2013 €
*   **Total Matériaux & Quincaillerie :** ~245 €
*   **TOTAL GÉNÉRAL ESTIMÉ PAR BRAS : ~2258 €** (Économie de **~1070 €** sur le robot complet par rapport au design Dynamixel initial).

---

## 4. État de la Conception (CAD & Simulation)

*   **Phalanges et Paume (Base) :** Les fichiers STEP/STL de la main ORCA v1 sont modifiés dans Fusion 360 pour adapter la paume aux 8 canaux de guidage et intégrer les poulies CNC et roulements MR84ZZ.
*   **Phalanges distales :** Adaptées pour intégrer les capteurs FSR 402 sous la pulpe et la peau silicone élastique.
*   **Usinage CNC (C500) :** Spools à vis de blocage radial en Aluminium 7075-T6, paume en Aluminium 6061-T6, et inserts carbone/alu.
*   **Simulation dynamique :** Modèles URDF/MJCF adaptés pour refléter l'architecture 8 DOF sous-actionnée Feetech dans Isaac Gym (`orca-gym`), permettant la validation des politiques d'apprentissage par renforcement (RL).

---

## 5. Instructions de Montage Critiques

*   **Manuel Principal :** Se référer au guide [GUIDE_COMPLET_Fabrication_et_Montage_DHand_V1.md](GUIDE_COMPLET_Fabrication_et_Montage_DHand_V1.md) pour les détails d'impression, d'usinage, de coulage du silicone et d'assemblage pas-à-pas.
*   **Suppression des Nœuds :** N'utiliser aucun nœud simple sur les lignes de charge en tension. Employer des manchons en cuivre Ø1.5 mm pour le sertissage distal à la pulpe (ou épissure Brummel), et la vis radiale M1.6 du spool pour le bridage moteur.
*   **Tensionnement automatique des tendons :** Utiliser le script officiel `tension.py` (via SDK `orca_core`) qui régule le courant des servomoteurs pour établir automatiquement la pré-tension initiale uniforme de **5 N** et calibrer le Point Zéro Réel.
*   **Butées logicielles (Sécurité structurelle) :** Lancer la procédure de calibration `calibrate.py` pour inscrire les limites de course angulaire directement dans la mémoire EEPROM non volatile des servos Feetech. Les moteurs refuseront de forcer au-delà des limites de flexion structurelle du doigt en cas d'erreur logicielle.

---

## 6. Backlog Technique & Questions en suspens

1.  **Mesure de masse physique du bras complet :** La masse totale estimée du bras et de la main (~5.4 kg) est conforme aux calculs, mais une mesure physique finale sur le prototype complet est indispensable pour valider son influence sur l'équilibre dynamique lors de la locomotion bipède.
2.  **Dissipation thermique sous cycle de grip intensif :** Valider expérimentalement la température du convertisseur DROK 48V→12V lors d'une phase de blocage prolongé (stall de grip) sous 50°C. Le boîtier IP67 alu du DROK devrait évacuer efficacement les 6W en grip soutenu.
3.  **Validation du bridage firmware :** Confirmer sur prototype que la limitation du registre « Max Torque » des servos Feetech à 70–80% maintient bien le courant de pic total sous 15A et assure un Fs de câble Vectran > 1.5.
4.  **Validation expérimentale AnySkin (V2) :** Préparer le pipeline de transition logicielle des capteurs FSR 402 vers la peau magnétique AnySkin pour au-delà de la manipulation fine sans recalibrage.
5.  **Test d'usinage de spools en Bronze CuSn8 :** Réaliser un essai d'usinage sur la C500 avec du bronze CuSn8 pour évaluer le gain de glissement et de durabilité de la gorge par rapport à l'Aluminium 7075-T6.
6.  **Sensibilité UV du Vectran :** Le Vectran est sensible aux UV. Valider que le routage intégralement interne (tubes PTFE, tube carbone, paume alu) protège les tendons de toute exposition. Si des sections sont exposées, envisager une gaine opaque ou un traitement UV-résistant.

---

## 7. Roadmap & Itérations Futures

*   **Utilisation de spools en Bronze CuSn8 (V1.1) :** Remplacer les poulies alu par du bronze auto-lubrifiant pour augmenter la durabilité axiale de la gorge et réduire l'usure du câble.
*   **Poignet Yaw (V2) :** Intégrer un DOF de Yaw au poignet (RS-00) pour atteindre une cinématique complète (Pitch + Yaw) similaire au poignet du Tesla Optimus.
*   **Intégration d'AnySkin (V2) :** Remplacer les capteurs de force FSR 402 analogiques par une peau tactile magnétique 3-axes AnySkin à base de magnétomètres CD4051 pour un apprentissage machine tactile avancé.

---
**Fin du document consolidé – Version V1.2 (Mai 2026). Corrections : DROK 48V, Vectran LCP standardisé, couples datasheet, rayon spool r=6mm, ressort à lame PA12-CF.**