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

> **Verdict D-Bot** : La version actuelle (V1) n'a pas de Waist Yaw pour des raisons de rigidité structurelle et de simplicité (et le K-Bot n'en a pas). C'est le **premier axe à ajouter dans une V2** (via un gros moteur type RS-04 ou un Harmonic Drive) entre le bassin et les épaules, dès que le D-Bot devra faire des tâches de manipulation complexes. L'IA s'adaptera sans problème à son absence pour l'apprentissage de la marche initiale.

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
