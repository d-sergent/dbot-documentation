# 25 — Étude Mécanique : Montage Direct Cantilever vs Montage Découplé & Analyse Torso Yaw (RS06)

Cette étude complète et synthétise les principes de montage mécanique pour les actionneurs Quasi-Direct Drive (QDD) du projet **D-Bot** (moteurs RobStride RS-04, RS-03, RS-06, RS-02), à la lumière de l'état de l'art mondial de la robotique humanoïde et quadrupède (Unitree G1/H1, Tesla Optimus Gen 1/2, Figure 01/02).

---

## 1. Synthèse de l'État de l'Art : La Norme "100% Cantilever Direct"

Dans la robotique humanoïde moderne, le **Montage Direct en Porte-à-Faux (*Cantilever Direct Mount*)** s'est imposé comme la référence pour la quasi-totalité des articulations rotatives (Épaules, Hanches, Coudes, Genoux rotatifs, Chevilles).

### Pourquoi le montage en Chape (U-Bracket) et les Accouplements Flexibles sont abandonnés sur les axes rotatifs :
1. **Élimination de l'Hyperstatisme** : Un montage en chape à double palier exige une tolérance d'usinage parfaite (< 0,05 mm). Tout défaut d'alignement engendre des contraintes radiales parasites (*sur-contrainte*) qui provoquent du grippage, de la friction et la destruction prématurée des roulements. Le cantilever est **isostatique**.
2. **Capacité des Roulements à Rouleaux Croisés (CRB) Intégrés** : Les actionneurs QDD modernes (Robstride, Unitree) intègrent en sortie un roulement annulaire haute capacité (CRB ou roulement à contact oblique à section mince). Les rouleaux croisés disposés à 90° reprennent simultanément les forces radiales, axiales et les **moments de basculement/flexion** (*tilting moments*).
3. **Rigidité Torsionnelle et Bande Passante de Contrôle** : Visser directement le bras/membre sur la bride du rotor garantit une liaison métallique rigide ("Zero Compliance"). Cela évite l'effet ressort introduit par les accouplements flexibles, indispensable pour le contrôle en impédance et les algorithmes de marche MPC / RL.
4. **Gain de Masse et de Volumétrie** : Suppression des paliers externes, des flectors/accouplements lourds et des structures enveloppantes en U.

---

## 2. Matrice Comparative des Modes de Montage pour QDD

| Critère | Montage Cantilever Direct | Montage en Chape (U-Bracket) | Montage Découplé (Accouplement Flex) |
| :--- | :--- | :--- | :--- |
| **Statut Isostatique** | **Isostatique parfait** | Hyperstatique (Risque de coincement) | Isostatique (mais complexe) |
| **Rigidité Torsionnelle** | **Maximale (Liaison rigide)** | Élevée | Faible à Moyenne (Effet ressort) |
| **Complexité / Pièces** | **Minimale** (Moteur + Équerre L) | Élevée (Chape + Palier opposé) | Élevée (Moteur + Palier + Accouplement) |
| **Usage Recommandé** | **Épaules, Hanches, Genoux, Coudes** | Actionneurs linéaires (Pistons) | Supination / Axes longs sujets à flexion |

---

## 3. Analyse du Montage Particulier Torso Yaw (Rotation Buste RS06 — reBOT B601)

L'étude du document [24_Bracket_RS06_Reprise_Effort_Axial.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Annexes/mecanique/24_Bracket_RS06_Reprise_Effort_Axial.md) propose une architecture hybride basée sur le moteur **RobStride RS06 (RSM1)** et une butée à aiguilles **`AXK 5578`** (+ rondelles trempées **`AS 5578`**).

### Évaluation de l'Approche pour la Rotation du Torse (Torso Yaw) :

**Verdict : APPROCHE EXCELLENTE ET TRÈS PERTINENTE POUR CET AXE SPÉCIFIQUE.**

#### Pourquoi cette architecture est particulièrement adaptée au Torso Yaw :
1. **Nature de la Charge sur le Torse** :
   - L'axe de rotation du torse (lacet / torso yaw) est un axe **vertical (Z)**.
   - Contrairement à une épaule ou un coude où la charge principale est un moment de flexion perpendiculaire, la charge permanente principale du torse est une **compression axiale pure de gravité ($F_z$)** (poids cumulé du haut du corps, des bras, de la tête, des batteries et de l'électronique : environ 80 N à 150 N en statique, et jusqu'à 300 N à 450 N sous accélérations dynamiques de marche).
2. **Protection du Réducteur RS06** :
   - Bien que le RS06 possède un roulement interne, soumettre ce roulement à une précharge axiale permanente de 15 kg à 30 kg en continu accélérerait l'usure du train planétaire et créerait du jeu axial.
   - En intercalant la butée à aiguilles flat `AXK 5578` (diamètre extérieur 78 mm) sous le flasque de liaison du rotor, **100% de la compression axiale verticale ($F_z$) est déchargée directement dans la platine aluminium CNC et transmise au châssis inférieur via les 4 tirants M4×70 mm**.
   - Le rotor du RS06 ne transmet ainsi que le **couple de rotation pur ($T_z$)**, en toute sécurité.
3. **Respect de l'Isostatisme** :
   - Ce montage n'est **pas** une chape hyperstatique en U. C'est un **appui plan axial concentrique**. Il ne crée pas de sur-contrainte radiale.

#### Points d'Attention et Règles de Conception D-Bot pour ce Montage :
* **Platine CNC Obligatoire** : La platine supérieure (`2-RSM1-STATOR-2`) accueillant le lamage de la butée `AXK 5578` **doit impérativement être usinée en Aluminium 6061-T6**. L'impression 3D plastique fluerait sous la pression continue des aiguilles.
* **Efforts de Traction (Lifting)** : La butée `AXK 5578` ne reprend que la **compression**. En cas de traction (robot soulevé par les épaules), le rocher/rotor repose sur les roulements internes du RS06, ce qui est tout à fait acceptable pour des efforts temporaires.
* **Entretoises anti-fluage** : Autour des 4 tirants M4×70 mm traversant le carter stator, insérer des tubes entretoises métalliques pour éviter le fluage du plastique du carter sous tension des tirants.

---

## 4. Analyse Comparative : Torso Yaw vs Supination Avant-Bras (RS02)

Une question stratégique se pose : **Pourquoi ne pas réutiliser le même montage à butée axiale `AXK` (type reBOT B601) pour la rotation de l'avant-bras (supination RS02) ?**

La réponse mécanique est **NON, ce montage à butée axiale pure `AXK` n'est pas adapté à l'avant-bras.**

### 3 Raisons Mécaniques Fondamentales :

1. **Orientation et Nature des Forces (Fixe Verticale vs Tridimensionnelle)** :
   * **Torso Yaw (Buste)** : L'axe est **vertical (Z) en permanence**. La charge dominante est une **compression axiale unidirectionnelle $F_z$** (poids du haut du corps poussant vers le bas sous la gravité). La butée à aiguilles `AXK` travaille idéalement dans ce sens unique.
   * **Avant-Bras (Supination)** : L'avant-bras bouge dans toutes les directions de l'espace 3D.
     * Bras à l'horizontale tenant une charge : La force principale n'est **pas** de la compression axiale, mais un **moment de flexion perpendiculaire massif ($M$)** (bras de levier de 25 à 35 cm avec la main) et un **effort tranchant radial ($F_r$)**.
     * Pousser contre un mur : Compression axiale ($F_z > 0$).
     * Tirer un objet ou porter une valise : **Traction axiale ($F_z < 0$)**.

2. **Incapacité de la Butée Axiale `AXK` à Supporter les Moments et la Traction** :
   * Une cage à aiguilles plate `AXK` est une **butée axiale pure à simple effet (unidirectionnelle)**.
   * Sous un **moment de flexion ($M$)**, les deux rondelles d'acier tentent de se décaler en arc : un côté des aiguilles subit une pincée destructrice tandis que l'autre côté se décolle.
   * Sous une **force de traction ($F_z < 0$)** (bras tiré), la rondelle supérieure se sépare complètement de la cage (`AXK` se décolle).

3. **Masse et Encombrement Distal** :
   * Un assemblage `AXK` (rondelles trempées + cage + platine CNC à lamage + tirants) ajoute un diamètre et une masse considérables.
   * Placer cette masse au bout du coude (à l'avant-bras) augmente drastiquement l'inertie rotative du bras ($I = m \cdot r^2$), surchargeant inutilement les moteurs d'épaule et de coude.

---

## 5. Solution Recommandée pour l'Avant-Bras / Supination (RS02)

Pour le moteur **RobStride RS02** (supination de l'avant-bras), l'architecture optimale est :

### Option A : Montage Direct Cantilever (Standard Unitree G1 / Tesla Optimus Gen 2)
* **Principe** : Le tube de l'avant-bras est directement vissé sur la bride de sortie du moteur RS02.
* **Pourquoi ça marche** : Le roulement à section mince / rouleaux croisés intégré au carter du RS02 encaisse seul le moment de flexion de la main ($M$), l'effort tranchant ($F_r$) et les efforts axiaux ($F_z$ en poussée et en traction). C'est la solution la plus légère et la plus compacte.

### Option B : Montage à Double Roulement Annulaire (Si l'avant-bras est très long ou souple)
* Si l'avant-bras est un long tube plastique/carbone subissant des flexions importantes, intercaler un **Roulement Annulaire à Section Mince ou à Contact Oblique (ex: type 6807 / 6808 ou Thin Section CRB)** — et **NON une butée `AXK`**.
* Ce type de roulement reprend simultanément les moments de flexion ($M$), les forces radiales ($F_r$), la compression ($F_z$) ET la traction ($-F_z$).

---

## 6. Recommandations Synthétiques pour la Gamme D-Bot

1. **Torso Yaw / Articulations Lourdes (RS06)** : **Conserver l'approche et s'inspirer directement du projet reBOT B601 (Doc 24 & assemblage `reBot_B601_RS_v1.0_20260625.step`)** avec butée axiale `AXK 5578` + platine/brackets CNC Alu pour décharger les contraintes axiales lourdes.
2. **Épaules, Hanches, Genoux (RS04 / RS03 / RS02)** : **Adopter le Montage Direct Cantilever** (Doc 25). Boulonnage direct de l'équerre en aluminium CNC sur la bride du rotor.
   * *Note CAO Sourcing* :
     * **RobStride RS06** : Brackets et intégration mécanique inspirés du projet **reBot B601 RS** (`reBot_B601_RS_v1.0_20260625.step` en local).
     * **RobStride RS02 & RS03** : Brackets et fixations inspirés des fichiers STEP du projet **LeRobot / Berkeley Humanoid** (ex: `bipedal_platform_no_arm.step`).
3. **Avant-Bras / Supination (RS02)** : **Montage Direct Cantilever** (Option A) ou guidage par **Roulement Annulaire Radial / Section Mince** (Option B) en cas de tube très long. Ne **pas** utiliser de butée axiale `AXK`.

---

*Document mis à jour en Juillet 2026 — Référence pour l'ingénierie mécanique D-Bot.*

