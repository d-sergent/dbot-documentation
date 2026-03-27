# 25 — Étude : Compatibilité IA & Apprentissage par Renforcement (Isaac Gym)

Avec l'avènement de l'Apprentissage par Renforcement (RL) de bout-en-bout (Sim2Real) propulsé par des simulateurs ultra-rapides comme **NVIDIA Isaac Gym**, **MuJoCo** ou **PyBullet**, concevoir l'architecture cinématique (matérielle) d'un robot de manière "aléatoire" est une erreur stratégique. 

Pour qu'un robot puisse réutiliser des *policies* open-source existantes (générées par les laboratoires de recherche) et s'entraîner rapidement, son fichier physique (`URDF` / `MJCF`) doit correspondre intimement aux standards morphologiques de l'industrie.

Ce document analyse les attentes "standards" de ces algorithmes pour la totalité du corps humainoïde.

---

## 1. Le Tronc (Waist / Torso) : La Rotation Z (Yaw)

**Question** : *Les algorithmes s'attendent-ils à avoir un degré de liberté en rotation Z juste au-dessus des hanches (Waist Yaw) ?*

### La Réponse Courte : C'est très fréquent, mais pas universel.

Presque tous les algorithmes d'entraînement modernes se basent sur des modèles humanoïdes génériques créés par OpenAI, DeepMind ou NVIDIA. Dans ces modèles, le tronc est l'ancrage central du robot ("Base Link").

| Articulation du Tronc | Statut Standard IA | Fonction | Présent sur D-Bot V1 ? |
| :--- | :---: | :--- | :---: |
| **Waist Yaw (Rotation Z)** | 🟡 **Standard / Recommandé** | Dissocier la direction du regard/ciblage des bras de la trajectoire des jambes. | ❌ (Mais recommandé V2) |
| **Waist Pitch (Flexion Y)** | 🟡 Fréquent | Se pencher en avant pour ramasser un objet lourd. | ❌ |
| **Waist Roll (Torsion X)** | 🔴 Rare | Équilibre asymétrique extrême. | ❌ |

### Faut-il ajouter un Waist Yaw au D-Bot V1 ?

**Pour la Locomotion Pure (marcher/courir)** : Non. L'IA peut parfaitement apprendre à marcher et tourner en utilisant uniquement les 6 DOFs des jambes (dont le *Hip Yaw*). Le robot Tesla Optimus Gen 1 et le Unitree H1 apprennent à marcher ainsi. L'absence de Waist Yaw signifie simplement que le buste et le bassin pointeront toujours dans la même direction.

**Pour la Manipulation Mobile (marcher ET manipuler)** : Oui. Dès que vous entraînez une "Whole-Body Control Policy" (WBC) où le robot doit avancer dans un couloir tout en regardant et attrapant un objet sur une table à sa droite, l'IA cherchera l'axe *Waist Yaw*. Sans axe Z au torse, le robot devrait marcher en "pas chassés" (crabe) ce qui est énergétiquement inefficace, ou tourner entièrement son corps sans cesse.

> **Verdict D-Bot** : La version actuelle (V1) fait l'impasse sur le Waist Yaw pour des raisons de rigidité structurelle et de simplicité. Mais, comme expliqué plus bas dans la **Section 4 (La Tête et le Cou)**, cette absence est **magistralement compensée par les 2 moteurs du cou (Pan/Tilt)**. En utilisant la Vision Active (Active Vision), le robot peut tourner la tête pour cibler un objet asymétrique, et utiliser les 5 DOFs de ses bras pour l'atteindre, sans avoir besoin de faire pivoter son bassin. L'ajout d'un Waist Yaw reste une piste d'optimisation (V2) pour des postures extrêmes, mais l'IA s'adaptera sans problème à son absence sur la V1 grâce à la tête articulée.

---

## 2. Le Haut du Corps : Épaules et Coudes

Pour le haut du corps, les algorithmes de RL (surtout ceux formés sur des données de *Motion Capture* humaine) sont beaucoup plus rigides sur le standard attendu.

### 2.1 Les Épaules (3 DOFs) : Le Standard Absolu

Le bras humain est un système à 7 DOF au total (3 épaule, 1 coude, 3 poignet). L'IA s'attend à une vraie conception sphérique (3 axes concourants) ou quasi-sphérique à l'épaule.

| Axe (Convention) | Action | Statut IA | D-Bot V1 |
| :--- | :--- | :---: | :---: |
| **Shoulder Pitch (Y)** | Lever le bras devant soi | 🟢 **Obligatoire** | ✅ RS-03 |
| **Shoulder Roll (X)** | Écarter le bras sur le côté | 🟢 **Obligatoire** | ✅ RS-03 |
| **Shoulder Yaw (Z)** | Effectuer une rotation interne du bras | 🟢 **Fortement Recommandé** | ✅ RS-02 |

> **Bonne nouvelle pour le D-Bot** : L'architecture actuelle du bras (Pitch/Roll puissants + Yaw plus léger) correspond **exactement** à la topologie standard URDF utilisée dans Isaac Gym pour l'entraînement à la manipulation (par exemple, le bras du robot PANDA ou ALOHA). L'IA n'aura besoin d'aucun "hack".

### 2.2 Le Coude (1 ou 2 DOFs)

| Axe | Action | Statut IA | D-Bot V1 |
| :--- | :--- | :---: | :---: |
| **Elbow Pitch (Y)** | Plier le coude | 🟢 **Obligatoire** | ✅ RS-02 |
| **Elbow Yaw (Z)** | Supination/Pronation de l'avant bras | 🟡 Optionnel | ❌ |

Beaucoup de robots simplifiés transfèrent le Yaw de l'avant-bras directement au niveau du poignet. C'est ce que nous faisons.

---

## 3. L'Extrémité : Le Poignet et la Main (End-Effectors)

Dans les environnements comme Isaac Gym, la main est généralement traitée comme un objet terminal appelé **End-Effector**.

### 3.1 Le Poignet (1 à 3 DOFs)

Le minimum viable pour qu'une IA puisse orienter un outil dans l'espace (couplé aux 4 DOFs Épaule+Coude) est l'ajout du "Poignet Roll" (Torsion).

| Axe | Action | Statut IA | D-Bot V1 |
| :--- | :--- | :---: | :---: |
| **Wrist Roll (Z)** | Tourner la poignée de porte | 🟢 **Obligatoire** | ✅ RS-00 |
| **Wrist Pitch (Y)** | Casser le poignet bas/haut | 🟡 Recommandé | ❌ |
| **Wrist Yaw (X)** | Saluer de la main | 🔴 Optionnel | ❌ |

Le D-Bot possède un bras à **5 DOFs** (3 épaule + 1 coude + 1 poignet torsif). C'est le strict minimum canonique pour faire de la manipulation d'objets en RL. Cela couvre 90% de l'espace de travail frontal. 

### 3.2 La Main (L'approche IA)

C'est ici que l'approche matérielle dicte l'approche logicielle. Isaac Gym gère la main de deux manières distinctes :

1. **Approche "Pince Parallel" (Gripper - 1 DOF)** : L'IA envoie simplement un signal (Ouvrir / Fermer / Force). 90% des challenges RL grand public (ramasser une pomme) utilisent ça.
2. **Approche "Dexterous Hand" (Main Anthropomorphe - >4 DOFs)** : C'est le domaine phare actuel (Shadow Hand, D-Hand). L'IA doit contrôler individuellement les doigts. Isaac Gym excelle dans ce domaine de la *Dexterous Manipulation*.

> **Verdict D-Bot** : L'utilisation de notre **D-Hand Premium (8 moteurs XC330)** oblige à utiliser les "policies" de *Dexterous Manipulation* de NVIDIA. L'intégration de la main à 8 axes dans l'URDF va ralentir l'apprentissage global du robot (beaucoup de paramètres).  
> **Conseil Sim2Real** : Lors de l'entraînement inital du robot (pour lui apprendre à marcher en balançant ses bras), la main D-Hand doit être configurée comme un "objet solide passif" de ~250g. Les DOFs des doigts ne doivent être activés dans Isaac Gym que pour des tâches stationnaires (manipulation devant une table). Apprendre la marche ET la manipulation fine simultanément (*Whole-Body Dexterous Control*) est la frontière ultime de la recherche actuelle.

---

## 4. La Tête et le Cou (Active Vision)

**Question** : *Les algorithmes s'attendent-ils à avoir 2 DOFs au niveau du cou ? Le Pan/Tilt de la tête peut-il compenser l'absence de rotation du buste (Waist Yaw) ?*

### 4.1 La Tête dans Isaac Gym (Active Vision)

Absolument. En Apprentissage par Renforcement, la capacité de la *policy* à orienter ses propres capteurs s'appelle l'**Active Vision** (ou l'Attention Active). Les algorithmes les plus avancés ne se contentent pas de subir un flux vidéo statique découpé au hasard ; ils apprennent à *bouger* la caméra (la tête) pour scanner l'environnement, construire une carte de profondeur efficace (avec l'OAK-D et le LiDAR L2), et "verrouiller" visuellement une cible pendant que le corps bouge.

| Axe (Convention) | Action | Statut IA | D-Bot V1 |
| :--- | :--- | :---: | :---: |
| **Head Pan (Yaw/Z)** | Dire "Non", tourner la tête gauche/droite | 🟢 **Très Important** | ✅ RS-05 |
| **Head Tilt (Pitch/Y)** | Dire "Oui", lever/baisser la tête | 🟢 **Très Important** | ✅ RS-05 |

Une tête articulée à 2 DOFs est la norme absolue pour les robots humanoïdes de nouvelle génération (Figure 01, Optimus, Atlas). Cela permet au robot de regarder où il va poser les pieds sur un sol accidenté sans avoir à incliner tout son torse avec un Waist Pitch.

### 4.2 Le "Head Pan" comme Substitut Ultime au "Waist Yaw"

C'est là que l'architecture du D-Bot est très élégante et que votre intuition est parfaitement exacte. **Oui, le Pan de la tête (rotation Z du cou) compense la majeure partie des inconvénients liés à l'absence de Waist Yaw (rotation Z du buste).**

Si un robot est dépourvu de Waist Yaw *et* de tête articulée, et qu'il veut manipuler un objet situé à 45° sur sa droite, il a un énorme problème : il ne le voit plus. Il doit donc tourner tout son corps avec ses jambes pour le ramener au centre de son champ de vision.

Grâce à ses **2 moteurs RS-05 au cou**, le D-Bot résout ce problème de ciblage spatial sans impliquer la dynamique complexe du torse :
1. **Perception Indépendante** : Le D-Bot peut conserver sa dynamique de marche rectiligne (stable) tout en tournant la tête (Head Pan) pour repérer et "verrouiller" une cible sur sa gauche ou sa droite.
2. **Ciblage Asymétrique pour la Manipulation** : Puisque la caméra stéréo (OAK-D) donne les coordonnées XYZ exactes de la cible à l'IA, le contrôleur des bras peut utiliser son **bras à 5 DOFs** (qui est amplement assez articulé) pour aller cueillir l'objet de côté, même si les épaules restent alignées avec les hanches.

> **Verdict D-Bot** : L'intégration des 2 RS-05 au cou n'est pas un simple "gadget". C'est un composant fondamental pour la survie du robot dans un environnement RL. Le Pan/Tilt transforme l'absence de rotation du buste d'un véritable goulot d'étranglement (blocage perceptif) en une simple contrainte de "reachability" (espace de travail des bras) pour l'IA. Tant que l'objet est dans le champ visuel du cou et physiquement atteignable par les bras, l'absence de Waist Yaw est totalement transparente pour une tâche de manipulation en mouvement.

---

## Bilan Cinématique D-Bot vs Standards RL

Le D-Bot V1 est **parfaitement aligné** sur les standards pour un humanoïde d'apprentissage :

| Région | DOFs D-Bot V1 | DOF Manquant (Évolution V2) | Total DOFs |
| :--- | :---: | :--- | :---: |
| **Jambes** | 2 × 6 DOFs | Aucun | 12 |
| **Torse** | 0 DOF | **Hanche Z (Waist Yaw)** | 0 |
| **Bras** | 2 × 5 DOFs | Poignet Pitch (Flexion) | 10 |
| **Mains** | 2 × 8 DOFs | Aucun | 16 |
| **Tête** | 2 DOFs | Aucun | 2 |
| **TOTAL** | **40 DOFs* ** | | |

*Note : 40 DOFs avec les mains actives complètes, 24 DOFs pour la locomotion de base.*

Il ne lui manque que 3 DOFs d'ingénierie fine (le Waist Yaw et les Poignets Pitch) pour atteindre les capacités cinématiques exactes d'un Tesla Optimus (lequel en possède 28 + 22 pour les mains). Pour un robot de 40 kg conçu en garage, le D-Bot V1 est une plateforme "Sim2Real ready" d'excellence.
