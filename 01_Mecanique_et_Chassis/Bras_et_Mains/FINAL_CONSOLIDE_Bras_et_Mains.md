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
*   **Main D-Hand Hybrid Premium :** Combinaison de **5 servomoteurs Feetech STS3250** (flexion en force) et **3 servomoteurs Feetech HL-3915** (axes de précision avec mode force matérielle) pour un grip effectif réel de **438 N en pic** (140 N en continu nominal) et 8 DOF complets. L'actionnement est déporté dans l'avant-bras via des tendons Dyneema DM20 (fluage quasi nul).
*   **Capteurs Tactiles :** Intégration de capteurs tactiles eFlesh 3-axes basés sur une structure TPU à infill gyroïde 8% et aimants N52 (V1 immédiate), évoluant vers AnySkin (V2).
*   **Structure :** Utilisation d'un tube en fibre de carbone pour l'humérus (avec inserts alu CNC) et d'un châssis hybride pour l'avant-bras (plaque centrale en aluminium 6061-T6 Isogrid fermée par des coques structurelles PA12-CF vissées formant une boîte de torsion). Cette solution hybride optimise la rigidité torsionnelle et la dissipation thermique.

---

## 2. Spécifications Matérielles Validées

### 2.1 Architecture Cinématique et Actionneurs

| Articulation | Joint URDF | Type | Axe (xyz) | Moteur | Couple Nominal | Couple Pic | Poids Moteur | Interface |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Épaule Pitch** | `shoulder_pitch` | revolute | 0 1 0 (Y) | RobStride RS-04 | 40 N·m | 120 N·m | 1420 g | CAN (1 Mbps) |
| **Épaule Roll** | `shoulder_roll` | revolute | 1 0 0 (X) | RobStride RS-03 | 20 N·m | 60 N·m | 880 g | CAN (1 Mbps) |
| **Épaule Yaw** | `shoulder_yaw` | revolute | 0 0 1 (Z) | RobStride RS-02 | 6 N·m | 17 N·m | 405 g | CAN (1 Mbps) |
| **Coude Pitch** | `elbow_pitch` | revolute | 0 1 0 (Y) | RobStride RS-03 | 20 N·m | 60 N·m | 880 g | CAN (1 Mbps) |
| **Coude Supination** | `forearm_roll` | revolute | 0 0 1 (Z) | RobStride RS-02 | 6 N·m | 17 N·m | 405 g | CAN (1 Mbps) |
| **Poignet Pitch** | `wrist_pitch` | revolute | 0 1 0 (Y) | RobStride RS-00 | 5 N·m | 14 N·m | 310 g | CAN (1 Mbps) |
| **Main (8 DOF)** | `finger_joint_*` | under-act | - | 5x STS3250 + 3x HL-3915 | 1.39 N·m (HL) / 1.57 N·m (STS) | 1.39 N·m / 4.9 N·m | 480 g (total) | TTL (SCServo) |

**Répartition des 8 DOF de la main (D-Hand Hybrid Premium) :**

| # | Doigt | Mouvement | Servo Affecté | Type Moteur | Tendon |
| :-: | :---- | :-------- | :------------ | :---------- | :----- |
| 1 | Pouce | Flexion (Curl) | **STS3250** (ID 1) | Coreless (4.9 N·m pic) | Dyneema DM20 Ø1.0mm |
| 2 | Pouce | Opposition (Abd.) | **HL-3915** (ID 6) | Coreless (Mode Force Matérielle) | Dyneema DM20 Ø1.0mm |
| 3 | Index | Flexion (Curl) | **STS3250** (ID 2) | Coreless (4.9 N·m pic) | Dyneema DM20 Ø1.0mm |
| 4 | Index | Abduction | **HL-3915** (ID 7) | Coreless (Mode Force Matérielle) | Dyneema DM20 Ø1.0mm |
| 5 | Majeur | Flexion (Curl) | **STS3250** (ID 3) | Coreless (4.9 N·m pic) | Dyneema DM20 Ø1.0mm |
| 6 | Annulaire | Flexion | **STS3250** (ID 4) | Coreless (4.9 N·m pic) | Dyneema DM20 Ø1.0mm |
| 7 | Auriculaire | Flexion | **STS3250** (ID 5) | Coreless (4.9 N·m pic) | Dyneema DM20 Ø1.0mm |
| 8 | Paume | Curl palmaire | **HL-3915** (ID 8) | Coreless (Mode Force Matérielle) | Dyneema DM20 Ø1.0mm |

---

### 2.2 Structure des Membres Supérieurs

*   **Humérus (Bras) :** Tube Carbone Ø35 mm or Ø40 mm (épaisseur de paroi ~1.5-2 mm).
    *   **Raccordement :** Inserts cylindriques en Aluminium 6061-T6 (usinés CNC) collés à l'époxy structurelle (3M DP490).
    *   **Verrouillage :** Goupille élastique double Mécanindus Ø3 mm ou Ø4 mm.
*   **Avant-Bras :** Plaque centrale en Aluminium 6061-T6 (Isogrid 4 mm) fermée par deux coques structurelles en PA12-CF (boîte de torsion semi-monocoque). 
    *   **Longueur physique du châssis d'avant-bras :** **200 mm**. Il abrite de manière ultra-dense le bloc des 8 servos Feetech empilés sur deux couches (90 mm) et le RS-00 de Pitch (57 mm), laissant 53 mm libres pour l'électronique de puissance (Buck converter DROK vissé à plat sur la plaque alu pour dissipation thermique active) et de contrôle.
    *   **Longueur fonctionnelle coude ➔ poignet :** **278 mm** (RS-02 Supination de 78 mm au niveau du coude + 200 mm de châssis d'avant-bras), s'insérant parfaitement dans les proportions anthropomorphes d'un robot de 170 cm.
    *   **Raccordement :** Platines et inserts en Aluminium 6061-T6 (usinés CNC) fixés sur la plaque Isogrid.
    *   **Verrouillage :** Goupille élastique double Mécanindus Ø2 mm ou Ø2.5 mm.
*   **Brackets Moteurs Épaule :** Aluminium 6061-T6 usiné CNC (NestWorks C500).
    *   **Bracket #1 (Pitch→Roll) :** Relie Rotor RS-04 Pitch au Stator RS-03 Roll. Masse estimée ~140g.
    *   **Bracket #2 (Roll→Yaw) :** Relie Rotor RS-03 Roll au Stator RS-02 Yaw. Masse estimée ~80g.
    *   **Objectif :** Minimiser le décalage inter-axe (< 30mm entre Pitch et Roll, < 25mm entre Roll et Yaw).

---

### 2.3 Système de Tendons et Guidage (Main)

*   **Tendon Universel (×8) :** Tresse **Dyneema DM20 Ø1.0 mm** (résistance à la rupture brute ~900–1000 N, fluage quasi nul sous charge statique, frottement très bas de 0.08 à 0.12, bobine de 50 m achetée). Le DM20 est standardisé sur toutes les lignes (force et précision) pour allier le glissement du Dyneema et la stabilité dimensionnelle du Vectran sans nécessiter de retensionnement.
*   **Gaine de guidage (pour tendons fléchisseurs DM20) :** Deux variantes de tube PTFE sont en cours de test comparatif pour déterminer le meilleur compromis jeu/frottement avec le câble Dyneema DM20 de Ø 1.0 mm :
    *   **Option A :** Tube PTFE **Ø 1.2 mm ID / Ø 1.6 mm OD** (jeu de 0.2 mm, ratio ×1.2 — serré, alésage CAO à 1.6 mm). ✅ **Reçu** (5 m en stock).
    *   **Option B (recommandée) :** Tube PTFE **Ø 1.5 mm ID / Ø 1.9 mm OD** (jeu de 0.5 mm, ratio ×1.5 — identique à l'ORCA v1 d'origine, alésage CAO à 1.9 mm). ✅ **Reçu** (5 m en stock).
    *   *Décision finale :* À valider sur prototype après test d'enfilage et de frottement dans les courbes de la paume. 5 m supplémentaires de la taille retenue seront à commander pour la seconde main.
    *   Les tendons de retour élastiques TPU dorsaux (passifs) coulissent directement dans les canaux supérieurs de la structure PA12-CF, sans nécessiter de gaine PTFE.
*   **Poulie d'enroulement (Spool) :** Ø14 mm en Aluminium 7075-T6 usinée CNC (NestWorks C500).
    *   **Rayon effectif au fond de gorge :** r = 6 mm (Ø12 mm au fond de gorge, flasques à Ø14 mm).
    *   **Gorge :** Profil en U de 0.75 mm de large et 0.6 mm de profondeur, pitch hélicoïdal de 0.7 mm/tour sur exactly 1.5 tour.
    *   **Sécurité et bridage sans nœud :** Le tendon s'enroule dans sa gorge et est pincé de manière indestructible via une **vis sans tête de blocage radial M1.6** vissée dans le spool. Cela conserve **95%** de la résistance mécanique brute du câble (pas d'affaiblissement par nœud simple).
    *   **Roulement intégré :** MR84ZZ (4x8x3 mm) pressé en force H7 dans le spool.
*   **Poulies de renvoi (Paume) :** Ø6 mm, PA12-CF imprimé 3D avec micro-roulements MR84ZZ intégrés.
*   **Ancrage distal (pulpe) :** **Sertissage mécanique via manchon en cuivre de Ø1.5 mm** ou **épissure Brummel** étanche (conservation de 90-95% de la rupture).
*   **Retour passif des doigts (système intégré) :**
    *   Assuré par un **système hybride** : du **fil élastique mono-brin 100% Polyuréthane (TPU) de Ø 0.8 mm** (bijouterie technique) logé dans les canaux supérieurs d'origine. Ces élastiques de retour traversent entièrement la paume par les 5 canaux supérieurs de celle-ci et sont **bridés et tensionnés au niveau d'une plaquette de serrage centralisée à l'entrée du poignet** (rappel d'extension principal de 2 N à 2.5 N). Le tout est complété par la **gaine élastomère externe en TPU 95A/98A** (rappel secondaire et étanchéité). Le silicone moulé et les lames en PA12-CF de 0.5 mm sont officiellement supprimés de l'architecture.

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
    *   **En pic (stall STS3250 à 4.9 N·m) :** **438 N** (avec rendement réaliste global $\eta_{total} = 0.83$ validant la friction Dyneema/PTFE et les pivots de phalanges, pour r = 6 mm).
    *   **En continu nominal (rated STS3250 à 1.57 N·m) :** **~140 N** (amplement suffisant pour toute manipulation d'objets courants ; une bouteille pleine requiert ~15 N).
*   **Détail du calcul de grip :**
    *   **Traction Dyneema DM20 STS3250 en pic :** $(4.9\text{ N.m} / 0.006\text{ m}) × 0.83 = \mathbf{677\text{ N}}$ (rayon effectif r = 6 mm au fond de gorge du spool).
    *   **Force à la pulpe par doigt en pic :** $677\text{ N} × (10\text{ mm} / 70\text{ mm}) = \mathbf{96.7\text{ N}}$.
    *   **Grip pic (5 doigts) :** $5 × 96.7\text{ N} × \cos(25°) = \mathbf{438\text{ N}}$ (valeur physique réelle pour r = 6 mm).
    *   **Traction Dyneema DM20 STS3250 en continu :** $(1.57\text{ N.m} / 0.006\text{ m}) × 0.83 = \mathbf{217\text{ N}}$.
    *   **Force à la pulpe par doigt en continu :** $217\text{ N} × (10\text{ mm} / 70\text{ mm}) = \mathbf{31.0\text{ N}}$.
    *   **Grip continu (5 doigts) :** $5 × 31.0\text{ N} × \cos(25°) = \mathbf{140\text{ N}}$ (valeur physique réelle pour r = 6 mm).
*   **Force de Pince Pouce-Index (Pinch Grasp) :** **~97 N** en pic, **~31 N** en continu.
*   **Vitesse de fermeture :** ~0.5 s.
*   **Facteur de Sécurité du câble Dyneema DM20 Ø1.0mm (rupture ~980 N, conservatif) :**
    *   Traction crête en pic (STS3250 à 4.9 N·m) = 677 N (à r = 6 mm avec rendement $\eta=0.83$).
    *   Rupture effective après sertissage (conservation 90%) = $980 × 0.90 = 882\text{ N}$.
    *   Fs = 882 N / 677 N = **1.30** en pic extrême. En usage continu : Fs = 882 / 217 = **4.06**.
    *   ⚠️ Le Fs en pic de 1.30 est acceptable pour des charges brèves de stall mais impose une **discipline stricte du bridage firmware** (registre Max Torque Feetech limité à 70–80%) pour ramener la traction de pic effective sous 550 N → Fs > 1.60 en usage réel.

---

### 2.6 Capacité de Portage du Bras (Analyse par Articulation)

#### Bilan de Masse des Segments (par bras)

| Segment | Composants | Masse Estimée |
| :--- | :--- | :---: |
| **Main (D-Hand)** | Paume alu CNC + 5 phalanges PA12-CF + peau silicone + poulies + roulements + capteurs FSR + câblage | ~300 g |
| **Avant-Bras (contenu)** | 8 servos Feetech (480 g) + RS-00 (310 g) + DROK buck (150 g) + plaque alu isogrid + coques 3D (450 g) + câblage + visserie (130 g) | ~1520 g |
| **Coude** | RS-03 (880 g) + RS-02 Supination (405 g) + bracket alu | ~1359 g |
| **Humérus** | Tube carbone Ø35-40mm + inserts alu + câblage | ~250 g |
| **Épaule** | RS-04 (1420 g) + RS-03 (880 g) + RS-02 (405 g) + brackets (220 g) + visserie (40 g) | ~2965 g |
| **TOTAL Bras Complet** | | **~6394 g** (~6.4 kg) |

#### Analyse du Facteur Limitant (Bras Tendu à 90°, Pire Cas Statique)

Le bras tendu horizontalement avec une charge dans la main représente le pire cas statique. Chaque articulation doit compenser la gravité sur tous les segments et la charge situés en aval.

**1. Poignet Pitch (RS-00, 5 N.m nominal / 14 N.m pic)**

*   Masse distale (main seule) : m_main = 0.30 kg
*   Couple gravitaire de la main : Couple_main = 0.30 * 9.81 * 0.060 = 0.18 N.m (CdM de la main à ~60 mm du poignet)
*   Couple restant pour la charge (nominal) : Couple_charge = 5.0 - 0.18 = 4.82 N.m
*   **Charge max au centre de préhension (nominal continu) :** m_max = 4.82 / (9.81 * 0.120) = **4.1 kg**
*   **Charge max en pic :** m_max,pic = (14.0 - 0.18) / (9.81 * 0.120) = **11.7 kg**

**2. Coude Pitch (RobStride RS-03, 20 N.m nominal / 60 N.m pic) — FACTEUR LIMITANT**

*   Masse distale (avant-bras + main) : m_distal = 1.52 + 0.30 = 1.82 kg
*   Centre de masse distal à ~172 mm du coude (pondéré entre avant-bras à 139 mm et main à 338 mm)
*   Couple gravitaire du bras distal : Couple_distal = 1.82 * 9.81 * 0.172 = 3.07 N.m
*   Distance coude -> centre de préhension : L_2 + L_3 = 0.278 + 0.120 = 0.398 m
*   Couple restant pour la charge (nominal) : Couple_charge = 20.0 - 3.07 = 16.93 N.m
*   **Charge max au centre de préhension (nominal continu) :** m_max = 16.93 / (9.81 * 0.398) = **4.3 kg**
*   **Charge max en pic :** m_max,pic = (60.0 - 3.07) / (9.81 * 0.398) = **14.6 kg**

**3. Épaule Pitch (RS-04, 40 N.m nominal / 120 N.m pic)**

*   Masse distale (humérus + coude + avant-bras + main) : m_distal = 3.43 kg (humérus 0.25 kg + coude RS-03 1.359 kg + avant-bras 1.52 kg + main 0.30 kg)
*   Centre de masse du bras complet : ~255 mm de l'épaule (pondéré)
*   Couple gravitaire du bras : Couple_bras = 3.43 * 9.81 * 0.255 = 8.58 N.m
*   Distance épaule -> centre de préhension : L_1 + L_2 + L_3 = 0.300 + 0.278 + 0.120 = 0.698 m
*   Couple restant pour la charge (nominal) : Couple_charge = 40.0 - 8.58 = 31.42 N.m
*   **Charge max au centre de préhension (nominal continu) :** m_max = 31.42 / (9.81 * 0.698) = **4.59 kg**
*   **Charge max en pic :** m_max,pic = (120.0 - 8.58) / (9.81 * 0.698) = **16.2 kg**

#### Tableau Récapitulatif des Capacités de Portage (Configuration RS-03)

| Articulation | Moteur | Couple Nominal | Charge Nominale Continue | Charge Pic | **Limitant ?** |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Poignet Pitch** | RS-00 | 5 N.m | **4.1 kg** | 11.7 kg | 🔴 **OUI — LIMITANT EN PITCH FRONTALE** |
| **Coude Pitch** | RS-03 | 20 N.m | **4.3 kg** | 14.6 kg | ✅ Non, dimensionnement homogène |
| **Épaule Pitch** | RS-04 | 40 N.m | **4.59 kg** | 16.2 kg | ✅ Marge confortable |
| **Épaule Roll** | RS-03 | 20 N.m | **~1.7 kg** (bras latéral) | ~6.2 kg | 🔴 **OUI — LIMITANT EN ABDUCTION** |

> ⚠️ **Le poignet pitch (RS-00, 4.1 kg) et l'épaule roll (RS-03, ~1.7 kg) sont les facteurs limitants du bras en position tendue horizontalement**. En flexion frontale (axe Pitch), le bras présente un dimensionnement extrêmement homogène où le poignet (4.1 kg), le coude (4.3 kg) et l'épaule (4.59 kg) sont équilibrés. En abduction latérale (axe Roll), le grand bras de levier limite la charge continue à ~1.7 kg. En pratique, dans les postures naturelles de manipulation (coude fléchi proche du corps), la capacité de portage du coude et du poignet augmente considérablement.

#### Capacité en Posture Réaliste (Coude Fléchi à 45°)

En posture naturelle de manipulation (coude fléchi à 45°), le bras de levier gravitaire est réduit par cos(45°) = 0.707 :
*   **Charge au coude (continu) :** 16.93 / (9.81 * 0.398 * 0.707) = **6.1 kg**
*   **Charge au coude (pic) :** (60.0 - 3.07) / (9.81 * 0.398 * 0.707) = **20.6 kg**

En tenant l'objet **près du corps** (bras le long du torse, coude fléchi à 90°, charge à ~200 mm du coude) :
*   **Charge au coude (continu) :** 16.93 / (9.81 * 0.200) = **8.6 kg**
*   **Charge au coude (pic) :** (60.0 - 3.07) / (9.81 * 0.200) = **29.0 kg**

#### Comparaison avec l'État de l'Art (Configuration Choisie — RS-03 au Coude)

| Robot | Charge Max (bras tendu) | Charge Max (proche corps) | Masse Bras |
| :--- | :---: | :---: | :---: |
| **D-Bot (RS-03 au coude)** | **4.3 kg continu / 14.6 kg pic** | **8.6 kg continu / 29.0 kg pic** | ~6.4 kg |
| Tesla Optimus Gen 2 | ~4.5 kg (annoncé) | ~9 kg (estimé) | ~7 kg (estimé) |
| Figure 01 | ~2.3 kg (estimé) | N/A | ~6 kg (estimé) |
| Unitree G1 | ~2 kg (annoncé) | ~5 kg (estimé) | ~4.5 kg |
| Humain moyen | ~3–5 kg (tenu longtemps) | ~15–25 kg | ~4–5 kg |

---

#### ⚡ Alternative Étudiée : Version RS-06 au Coude (Plus légère et économique)

Une alternative consistant à utiliser le moteur **RobStride RS-06** (11 N.m nominal / 36 N.m pic) au coude a été étudiée lors de la phase de conception :
*   **Différentiel RS-03 → RS-06 :**
    *   Couple nominal : 20 N.m (RS-03) → **11 N.m (RS-06)** (baisse de 45%).
    *   Couple pic : 60 N.m (RS-03) → **36 N.m (RS-06)** (baisse de 40%).
    *   Masse : 880 g (RS-03) → **621 g (RS-06)** (gain de 259 g sur le coude).
    *   Prix : ~$250 (RS-03) → **~$200 (RS-06)** (économie de $50/bras).
*   **Conclusion et Décision :**
    *   **La version avec le moteur RS-03 est définitivement choisie** au détriment de la version RS-06. Le surcoût modéré (+$50/bras) et le surpoids (+259 g) sont très largement compensés par le fait que la capacité de portage utile du bras est **plus que doublée (x2.1)** dans toutes les postures, élevant le D-Bot au niveau du Tesla Optimus Gen 2 tout en restant plus léger de 600 g. La platine de liaison et le bracket du coude sont spécifiquement dimensionnés en CAO pour adapter le Ø106 mm du RS-03.

---

## 3. Nomenclature (BOM Locale)

### 3.1 Composants Majeurs (par bras)

| Composant | Qté | Fournisseur | Prix Unit. (est.) | Total (est.) | Statut |
| :--- | :---: | :--- | :---: | :---: | :--- |
| RobStride RS-04 (Épaule Pitch) | 1 | RobStride | ~$300 | ~$300 | À commander |
| RobStride RS-03 (Épaule Roll) | 1 | RobStride | ~$250 | ~$250 | À commander |
| RobStride RS-02 (Épaule Yaw) | 1 | RobStride | ~$170 | ~$170 | À commander |
| RobStride RS-03 (Coude Pitch) | 1 | RobStride | ~$250 | ~$250 | À commander |
| RobStride RS-02 (Coude Supination) | 1 | RobStride | ~$170 | ~$170 | À commander |
| RobStride RS-00 (Poignet Pitch) | 1 | RobStride | ~$135 | ~$135 | À commander |
| **8x Servomoteurs Feetech Hybrid** | 1 set | Feetech (SCServo TTL) | **415 €** (total) | **415 €** | ✅ **Commandé** (2 sets commandés) |
| Buck Converter DROK 48V→12V 25A (IP67) | 1 | Amazon.fr / Droking.com | ~25 € | ~25 € | ✅ **Commandé** (2 unités commandées) |
| **Micro-Hub ESP32-S3 local** (eFlesh) | 1 | Adafruit / AliExpress | 15 € | 15 € | À commander |
| **Magnétomètres MLX90393 (sur micro-PCB)** | 8 | WowRobo / shop.wowrobo.com | 5 € | 40 € | ✅ **Commandé** (20 unités commandées) |
| **Aimants N48 ronds (Ø3 × 1.0 mm, S-03-01-N)** | 8 | Supermagnete | 0.22 € | 2 € | ✅ **Commandé** (aimants commandés) |
| Fusible réarmable PTC 15A (rail 12V) | 1 | Mouser / Farnell | ~3 € | ~3 € | À commander |
| **TOTAL MOTEURS & ÉLECTRONIQUE (par bras)** | | | | **~2076 €** | |

### 3.2 Matériaux Structurels & Quincaillerie (par bras)

| Composant | Qté | Fournisseur | Prix Unit. (est.) | Total (est.) |
| :--- | :---: | :--- | :---: | :---: |
| Tube Carbone Humérus (Ø35-40mm) | 1 | Composite-Works | ~$25 | ~$25 |
| Aluminium 6061-T6 (Brackets, Inserts, Plaque Isogrid) | ~1 kg | NestWorks | ~40 €/kg | ~40 € |
| Aluminium 7075-T6 (Poulies CNC) | ~50 g | NestWorks | ~5 € | ~5 € |
| Filament PA12-CF (Phalanges, Coques avant-bras) | ~400 g | Qidi Tech | ~12 € | ~12 € | ✅ **Reçu** (4 kg en stock). |
| **Filament Flexible TPU 95A-HF / 98A** | ~100 g | Qidi Tech | ~5 € | ~5 € | |
| **Fil élastique TPU Ø0.8 mm (5m)** | 1 | Perles & Co / Amazon.fr | ~3 € | ~3 € | Tendon de retour passif dorsal de bijouterie (Beadalon). ✅ **Reçu** (en stock). |
| Dyneema DM20 tressé Ø1.0mm (bobine 50m) | 1 | Liros (D-Pro Static) / Mastrant-M | ~35 € | ~35 € |
| Tubes PTFE Ø1.2 × Ø1.6 mm (5m) | 1 | PTFE Tube Shop / AliExpress | ~5 € | ~5 € | ✅ **Reçu** (5 m). Option A de test (jeu serré ×1.2 avec Dyneema Ø1.0 mm). |
| Tubes PTFE Ø1.5 × Ø1.9 mm (5m) | 1 | PTFE Tube Shop / AliExpress | ~5 € | ~5 € | ✅ **Reçu** (5 m). Option B de test recommandée (jeu confortable ×1.5, identique ORCA v1). |
| Roulements MR84ZZ (4x8x3mm) | 36 | SKF | ~1 € | ~36 € | 24 pour les articulations des 4 doigts, 4 pour le pouce, et 8 pour les contre-paliers des spools. ✅ **Commandé** (100 unités commandées sur AliExpress). |
| Roulements 6x13x5 mm | 2 | SKF | ~2 € | ~4 € |
| Goupilles cylindriques 2x6 mm (acier) | 20 | Mécanindus | ~0.5 € | ~10 € |
| Axes Inox 3x55 mm | 4 | McMaster-Carr | ~1 € | ~4 € |
| Colle époxy structurelle 3M DP490 | 1 cart. | 3M | ~30 € | ~30 € | Idéale pour coller le carbone, le métal et les aimants de coques sur le PA12-CF et le PLA. |
| **Colle Loctite Super Glue Gel** | 1 tube | Supermarché / Amazon | ~5 € | ~5 € | Idéale pour coller instantanément les aimants sur les coques esthétiques en PLA. |
| **TOTAL Matériaux & Quincaillerie (par bras)** | | | | **~221 €** |

### 3.3 Fournisseurs Dyneema DM20 / Liros D-Pro Static (depuis la France)

| Fournisseur | Localisation | Contact / Lien | Note |
| :--- | :--- | :--- | :--- |
| **Passion Radio** | France | passion-radio.fr | Revendeur français de la gamme Mastrant-M (âme Dyneema DM20 sous gaine polyester de 1.3 mm). |
| **Hamburger Tauwerk Fabrik** | Hambourg, DE | hamburgertauwerk.de | Vente en ligne (en français) de tresse pure Liros D-Pro Static (DM20) en 1.0 mm et 1.5 mm au mètre. |
| **Mastrant** | Europe (CZ) | mastrant.com/fr/ | Fabricant européen de lignes de haubanage, propose le Mastrant-M (DM20) en 1.0 mm et 1.3 mm, livraison rapide. |
| **Proust Sailing** | France | proust-sailing.com | Distributeur français de la gamme Liros, peut commander les diamètres fins D-Pro Static sur demande. |
| **Ino-Rope** | Concarneau, France | inorope.com | Atelier de gréement textile de haute technologie, peut fournir de la tresse DM20 fine sur demande. |

### 3.4 Coût Total Estimé (par bras)

*   **Total Moteurs & Électronique :** ~2076 €
*   **Total Matériaux & Quincaillerie :** ~232 €
*   **TOTAL GÉNÉRAL ESTIMÉ PAR BRAS : ~2308 €** (Économie de **~973 €** sur le robot complet par rapport au design Dynamixel initial).

---

## 4. État de la Conception (CAD & Simulation)

*   **Phalanges et Paume (Base) :** Les fichiers STEP/STL de la main ORCA v1 sont modifiés dans Fusion 360 pour adapter la paume aux 8 canaux de guidage et intégrer les poulies CNC et roulements MR84ZZ.
*   **Phalanges distales :** Adaptées pour intégrer les capteurs eFlesh (aimants N48 et magnétomètres MLX90393) sous la gaine en TPU.
*   **Usinage CNC (C500) :** Spools à vis de blocage radial en Aluminium 7075-T6 (ou Bronze) et inserts carbone/alu.
*   **Simulation dynamique :** Modèles URDF/MJCF adaptés pour refléter l'architecture 8 DOF sous-actionnée Feetech dans Isaac Gym (`orca-gym`), permettant la validation des politiques d'apprentissage par renforcement (RL).

---

## 5. Instructions de Montage Critiques

*   **Manuel Principal :** Se référer au guide [GUIDE_COMPLET_Fabrication_et_Montage_DHand_V1.md](GUIDE_COMPLET_Fabrication_et_Montage_DHand_V1.md) pour les détails d'impression, d'usinage, de coulage du silicone et d'assemblage pas-à-pas.
*   **Suppression des Nœuds :** N'utiliser aucun nœud simple sur les lignes de charge en tension. Employer des manchons en cuivre Ø1.5 mm pour le sertissage distal à la pulpe (ou épissure Brummel), et la vis radiale M1.6 du spool pour le bridage moteur.
*   **Tensionnement automatique des tendons :** Utiliser le script officiel `tension.py` (via SDK `orca_core`) qui régule le courant des servomoteurs pour établir automatiquement la pré-tension initiale uniforme de **5 N** et calibrer le Point Zéro Réel.
*   **Butées logicielles (Sécurité structurelle) :** Lancer la procédure de calibration `calibrate.py` pour inscrire les limites de course angulaire directement dans la mémoire EEPROM non volatile des servos Feetech. Les moteurs refuseront de forcer au-delà des limites de flexion structurelle du doigt en cas d'erreur logicielle.

---

## 6. Backlog Technique & Questions en suspens

1.  **Mesure de masse physique du bras complet :** La masse totale estimée du bras et de la main (~6.4 kg avec l'articulation d'épaule, ou ~3.43 kg pour le bras et la main seuls) est conforme aux calculs, mais une mesure physique finale sur le prototype complet est indispensable pour valider son influence sur l'équilibre dynamique lors de la locomotion bipède.
2.  **Dissipation thermique sous cycle de grip intensif :** Valider expérimentalement la température du convertisseur DROK 48V→12V lors d'une phase de blocage prolongé (stall de grip) sous 50°C. Le boîtier IP67 alu du DROK devrait évacuer efficacement les 6W en grip soutenu.
3.  **Validation du bridage firmware :** Confirmer sur prototype que la limitation du registre « Max Torque » des servos Feetech à 70–80% maintient bien le courant de pic total sous 15A et assure un Fs de câble Vectran > 1.5.
4.  **Validation expérimentale AnySkin (V2) :** Préparer le pipeline de transition logicielle des capteurs FSR 402 vers la peau magnétique AnySkin pour au-delà de la manipulation fine sans recalibrage.
5.  **Test d'usinage de spools en Bronze CuSn8 :** Réaliser un essai d'usinage sur la C500 avec du bronze CuSn8 pour évaluer le gain de glissement et de durabilité de la gorge par rapport à l'Aluminium 7075-T6.
6.  **Protection UV des tendons :** Le Dyneema DM20 possède une excellente résistance naturelle aux UV, contrairement au Vectran. Le routage interne protège toutefois les tendons contre l'usure par abrasion externe et la poussière.

---

## 7. Roadmap & Itérations Futures

*   **Utilisation de spools en Bronze CuSn8 (V1.1) :** Remplacer les poulies alu par du bronze auto-lubrifiant pour augmenter la durabilité axiale de la gorge et réduire l'usure du câble.
*   **Poignet Yaw (V2) :** Intégrer un DOF de Yaw au poignet (RS-00) pour atteindre une cinématique complète (Pitch + Yaw) similaire au poignet du Tesla Optimus.
*   **Intégration d'AnySkin (V2) :** Remplacer les capteurs de force FSR 402 analogiques par une peau tactile magnétique 3-axes AnySkin à base de magnétomètres CD4051 pour un apprentissage machine tactile avancé.

---
**Fin du document consolidé – Version V1.2 (Mai 2026). Corrections : DROK 48V, Vectran LCP standardisé, couples datasheet, rayon spool r=6mm, ressort à lame PA12-CF.**