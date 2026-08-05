# 26 — Étude : Architecture du Bloc Pelvien (Cardan de Hanche)

Suite à la définition du "Fémur Hybride" (qui se connecte en sandwich au dernier moteur de la jambe), il est indispensable d'étudier ce qui se passe *au-dessus* du fémur : le fameux **"Bloc de Hanche" à 3 degrés de liberté (DOF)**.

L'**Addendum 11 de la page 15b** montrait l'architecture historique du K-Bot. Comment cette architecture se compare-t-elle aux standards actuels de l'industrie (Tesla Optimus, Unitree G1/H1, Agility Digit) et comment devons-nous concevoir celle du D-Bot ?

---

## 1. La Problématique des Moteurs QDD (Quasi-Direct Drive)

Dans le corps humain, la hanche est une articulation sphérique parfaite : les 3 axes de rotation (Yaw, Roll, Pitch) se croisent exactement au même point x,y,z (le centre de la tête du fémur).

En robotique basée sur des actionneurs cylindriques massifs (les moteurs QDD type RS-03/RS-04), **deux moteurs physiques ne peuvent pas occuper le même espace au même moment**. 
Il est donc géométriquement impossible d'avoir une vraie liaison sphérique concourante. L'industrie résout ce problème en séparant les axes et en *empilant* les moteurs les uns à la suite des autres via de solides équerres structurelles. C'est ce qu'on appelle la **Chaîne Cinématique (Kinematic Chain)**.

---

## 2. Benchmark de l'Industrie

### A. L'approche K-Bot Originale
Les images du K-Bot montrent une tentative de compacter les 3 moteurs dans un espace très restreint (sorte de grappe entremêlée).
- *Inconvénient majeur* : Cette conception crée souvent des collisions (auto-intersections) lors de mouvements combinés extrêmes et rend l'usinage des pièces de liaison affreusement complexe en CAO 3D.

### B. L'approche Tesla Optimus : séquentielle A-R-F

Tesla a opté pour une chaîne cinématique **A-R-F** (Abduction→Rotation→Flexion), soit Roll→Yaw→Pitch dans notre nomenclature :
1. **Maillon 1 : Roll (Abduction)** — fixé au bassin, stabilité latérale.
2. **Maillon 2 : Yaw (Rotation)** — rotation interne/externe.
3. **Maillon 3 : Pitch (Flexion)** — dans la cuisse, levée et propulsion.

![Référence du Pelvis et Bloc de Hanche Tesla Optimus](../../Assets/img_optimus_pelvis_reference.jpg)

*Figure 2.1 : Référence d'architecture du bloc pelvien et de hanche de Tesla Optimus.*

---

**Avantage** : Le gros moteur Pitch (le plus lourd) est le dernier maillon et ne porte que la cuisse.  
**Inconvénient** : Architecture "Gen 1" — le bassin reste très large et les proportions du torse sont moins naturelles.

### C. L'approche Unitree H1 / H1-2 : Sphérique (Grappe Concentrée)

De son côté, Unitree adopte une philosophie radicalement différente pour maximiser la dynamique et la vitesse (le H1 détient le record du monde de vitesse humanoïde).
1. **Concentration des masses** : Les trois moteurs de la hanche (des modèles M107 ultra-compacts et très coupleux développés en interne) sont agglutinés en une **grappe très dense** directement centrée sur le bassin.
2. **Quasi-concourants** : À l'inverse de Tesla, Unitree s'efforce de faire en sorte que les axes de ces 3 moteurs se croisent *presque* au même point géométrique. L'objectif est d'imiter la vraie articulation "sur rotule" du corps humain.
3. **Bras de levier réduit** : Aucun moteur lourd n'est inséré dans le haut de la cuisse. Toute la puissance est dans le bassin, réduisant l'inertie lors des déplacements rapides.

> ⚠️ L'approche sphérique d'Unitree nécessite des moteurs sur-mesure imbriqués, incompatibles avec nos moyens de production en atelier.

### D. L'approche Gen2 (Figure 02, Unitree G1) : F-A-R

Les robots humanoides de deuxième génération (Figure 02, Unitree G1) ont convergé vers l'ordre **F-A-R** (Flexion→Abduction→Rotation), soit Pitch→Roll→Yaw :

1. **Maillon 1 : Pitch (Flexion)** — fixé au haut du bassin/torse, axe principal.
2. **Maillon 2 : Roll (Abduction)** — suspendu sous l'axe Pitch.
3. **Maillon 3 : Yaw (Rotation)** — en bas, vers la cuisse.

**Avantages** :
- Packaging anatomique — le bassin est plus fin, le torse proportionnellement plus long.
- Le pivot principal (Pitch) est haut, ce qui donne des proportions humaines naturelles.
- Standard de l'industrie 2024-2025.

**Inconvénient** :
- Le moteur Pitch porte les masses des moteurs Roll et Yaw lors du swing de jambe, ce qui augmente théoriquement l'inertie distale. En pratique, les marges de couple des RS-04 rendent cet inconvénient négligeable (voir §4).

---

## 3. L'Architecture D-Bot : Chaîne F-A-R (Méthode Gen2)

**Pour le D-Bot, nous adoptons officiellement l'ordre F-A-R**, en ligne avec les standards de la robotique humanoïde 2024-2025. C'est la seule approche qui soit à la fois réaliste avec des moteurs QDD standards "off-the-shelf" (RobStride) et qui offre des proportions anatomiques satisfaisantes.

Concrètement, la liaison entre le Bassin et le Fémur (Cuisse) du robot se décompose ainsi :

![Schéma Éclaté du Cardan de Hanche](./assets/img_hip_kinematic_chain.png)

### Maillon 1 : L'Axe Pitch (Moteur RS-04)
* **Emplacement** : Fixé au sommet du bassin ou en partie basse du torse (axe Y — horizontal, regarde sur les côtés du robot).
* **Rôle** : C'est le boss de la motricité. Il encaisse la charge principale pour lever la cuisse, s'accroupir, ou propulser le robot en avant.
* **Connexion sortante** : Son rotor porte la première équerre (un L-Bracket usiné en alu massif) qui descend vers le moteur Roll.
* **Motorisation** : RS-04 (120 N.m pic) — le plus fort, justement placé en premier pour encaisser tous les efforts.

### Maillon 2 : L'Axe Roll (Moteur RS-03)
* **Emplacement** : Fixé horizontalement (axe X) à l'extrémité du L-Bracket venant du moteur Pitch. Il regarde devant ou derrière le robot.
* **Rôle** : Permettre au robot de faire le grand écart ou d'écarter la jambe sur le côté.
* **Connexion sortante** : Son rotor porte la deuxième équerre (un U-Bracket ou L-Bracket) vers le Yaw.

### Maillon 3 : L'Axe Yaw (Moteur RS-03)
* **Emplacement** : Fixé verticalement (axe Z) à l'extrémité de l'équerre du moteur Roll, en haut de la cuisse.
* **Rôle** : Rotation interne/externe (tourner la pointe du pied vers l'intérieur ou l'extérieur).
* **Connexion sortante** : Son rotor est la ligne d'arrivée — c'est ici que vient se greffer le **Fémur Hybride en Sandwich**.

### Le Bout de la Chaîne : Le Fémur Hybride
Les deux épaisses plaques latérales du fémur viennent prendre en sandwich l'interface (cloche/rotor) du moteur Yaw (RS-03). Le fémur ne "sait pas" qu'il y a 2 autres moteurs au-dessus de lui. Il n'est attaché qu'au dernier maillon de la chaîne.

---

## 4. Analyse des Marges de Couple en F-A-R

En F-A-R, le RS-04 Pitch porte les masses des moteurs Roll et Yaw en plus de la jambe entière. Voici l'analyse des couples mis en jeu :

**Masses portées par le Hip Pitch (RS-04) :**

| Composant | Masse |
|:---|:---:|
| RS-03 Roll | 880g |
| RS-03 Yaw | 880g |
| 2× Brackets de liaison | ~400g |
| Fémur hybride complet | ~750g |
| RS-04 Knee (relocalisé en haut de cuisse via GT3) | 1 420g |
| Tibia + pied | ~800g |
| **TOTAL porté par le Hip Pitch** | **~5 130g** |

**Couple requis (bras de levier au CdG de la jambe ~0.15m) :**
```
τ_statique      = 5.13 × 9.81 × 0.15  ≈  7.5 N.m
τ_marche normale (×2.5 dyn.)          ≈ 18.8 N.m   → RS-04 (120 N.m) : 16% ✅
τ_course pic (×4.0 dyn.)             ≈ 30.0 N.m   → RS-04 (120 N.m) : 25% ✅
```

> [!TIP]
> **Conclusion** : Même en portant tous les maillons de la chaîne, le RS-04 Hip Pitch ne dépasse jamais 30% de ses capacités lors de la locomotion normale. Les marges sont très confortables. **Aucune amplification GT3 n'est nécessaire à la hanche** (voir §5).

---

## 5. Étude Option GT3 Hip Pitch — Analyse et Rejet

Face aux très bonnes marges du §4, nous avons étudié l'option d'ajouter une réduction GT3 sur le Hip Pitch (en s'inspirant de la Doc 15g pour le genou), afin de délocaliser le RS-04 dans le torse et de réduire encore l'inertie du bassin. L'analyse conclut que cette option, bien que techniquement viable, n'est **pas retenue**.

### Principe étudié

Le RS-04 Hip Pitch serait placé dans la partie basse du torse, et sa puissance transmise à l'axe de pivot de la hanche via une courroie GT3 (ratio 1.5:1 → 180 N.m).

### Avantages identifiés
- Réduction de la masse suspendue au bassin (RS-04 fixe dans le torse)
- Légère amplification de couple supplémentaire (180 N.m vs 120 N.m)
- Inertie de balancement de jambe légèrement réduite

### Raisons du rejet

| Raison | Détail |
|:---|:---|
| **Couple déjà suffisant** | Le RS-04 à 120 N.m est sollicité à max 25% en locomotion. La GT3 serait une complexité sans bénéfice mesurable. |
| **Complexité de routage** | La courroie doit traverser une zone mobile (articulation Pitch). Le passage du brin de courroie est difficile à protéger lors des rotations Roll et Yaw. |
| **Encombrement torse** | Le torse basse héberge déjà la batterie 48V et la PDB. Ajouter 2 RS-04 (2 840g) dans cet espace est un défi d'intégration important. |
| **GT3 genou déjà mise en place** | La délocalisation du moteur genou via GT3 (Doc 15g) apporte déjà la réduction d'inertie distale majeure. La GT3 hanche est redondante avec cet effort. |

> [!IMPORTANT]
> **Décision** : Le RS-04 Hip Pitch reste **directement sur l'axe de la hanche**, en direct drive 1:1. C'est plus simple, plus robuste, et les marges de couple sont largement suffisantes.

---

## 6. Conséquences pour l'Ingénierie (Usinage C500)

L'énorme avantage de l'ordre F-A-R avec chaîne séquentielle, c'est l'usinabilité immédiate.

Nous avons réduit la hanche à **seulement 2 pièces mécaniques simples (Brackets)** :
1. **Le "Pitch-Roll Bracket"** : Une équerre reliant l'axe Pitch (RS-04) au moteur Roll (RS-03).
2. **Le "Roll-Yaw Bracket"** : Une seconde équerre reliant le moteur Roll au moteur Yaw.

Ces deux pièces sont des usinages simples en aluminium 7075-T6 sur C500. Elles mesurent tout au plus 5 à 10 cm de long chacune, offrant une rigidité exceptionnelle.

| Comparaison des ordres cinématiques | Packaging bassin | Proportions | Standard industrie |
|:---|:---:|:---:|:---:|
| R-A-F (Yaw→Roll→Pitch) — **Ancien D-Bot** | Moyen | Peu naturel | Non-standard |
| A-R-F (Roll→Yaw→Pitch) — **Tesla Optimus** | Bon (Pitch en bas) | Gen1 | Déclinant |
| **F-A-R (Pitch→Roll→Yaw) — D-Bot V2** | **Excellent** | **Anatomique** | **Gen2 standard** ✅ |

> **Verdict / Action Recommandée** : Toute la modélisation CAO du bloc pelvien doit se concentrer sur le design ultra-rigide des 2 Brackets de liaison (Pitch-Roll et Roll-Yaw). Le RS-04 Pitch est positionné au sommet du bassin/bas du torse, son rotor orienté vers le côté (axe Y), définissant le plan médio-latéral du robot.

---

*Document mis à jour en Avril 2026 — Passage de l'architecture R-A-F à F-A-R suite à l'analyse comparative des standards de l'industrie (Tesla Optimus Gen1 = A-R-F, Figure 02 / Unitree G1 Gen2 = F-A-R). Option GT3 Hip Pitch étudiée et rejetée (couple RS-04 suffisant en direct drive).*
