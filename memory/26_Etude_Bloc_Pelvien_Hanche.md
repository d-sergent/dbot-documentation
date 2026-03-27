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

### B. L'approche Tesla Optimus : Séquentielle (Chaîne Empilée)

![Référence : Actionneurs de Hanche Tesla Optimus (AI Day 2022)](./assets/img_optimus_pelvis_reference.jpg)
*(Note : Vue des actionneurs rotatifs de la hanche du Tesla Optimus, illustrant parfaitement l'empilement séquentiel des axes de rotation).*

Tesla a opté pour une approche mécanique très franche dite en **chaîne cinématique séquentielle**. Le bassin abrite le premier moteur, et les suivants s'y attachent comme des maillons de chaîne :
1. **L'empilement** : Le premier moteur est fixé au bassin, puis un *bracket* (équerre) métallique le relie au deuxième moteur, qui lui-même porte le troisième.
2. **Intégration dans la cuisse** : Pour gagner de la compacité en largeur, Tesla a carrément descendu le moteur de Lacet (Yaw) **à l'intérieur de la cuisse** (le fémur), tandis que les moteurs de Pitch et de Roll restent au niveau du bassin.
3. **Conséquence géométrique** : Les 3 axes de rotation ne se croisent pas au même point (ils sont non-concourants et décalés dans l'espace). C'est une approche géométriquement imparfaite mais **extrêmement robuste et facile à usiner** (ce qui est logique pour un constructeur automobile).

### C. L'approche Unitree H1 / H1-2 : Sphérique (Grappe Concentrée)

De son côté, Unitree adopte une philosophie radicalement différente pour maximiser la dynamique et la vitesse (le H1 détient le record du monde de vitesse humanoïde).
1. **Concentration des masses** : Les trois moteurs de la hanche (des modèles M107 ultra-compacts et très coupleux développés en interne) sont agglutinés en une **grappe très dense** directement centrée sur le bassin.
2. **Quasi-concourants** : À l'inverse de Tesla, Unitree s'efforce de faire en sorte que les axes de ces 3 moteurs se croisent *presque* au même point géométrique. L'objectif est d'imiter la vraie articulation "sur rotule" du corps humain.
3. **Bras de levier réduit** : Aucun moteur lourd n'est inséré dans le haut de la cuisse. Toute la puissance est dans le bassin, réduisant l'inertie lors des déplacements rapides.

---

## 3. L'Architecture D-Bot : Le Cardan de Hanche Séquentiel (Méthode Tesla)

Pour le D-Bot, nous validons officiellement l'approche **séquentielle (type Optimus)**, car c'est la seule qui soit réaliste avec des moteurs QDD standards "off-the-shelf" (RobStride) et usinable avec notre CNC C500. L'approche sphérique d'Unitree nécessite des moteurs sur-mesure imbriqués, incompatibles avec nos moyens de production en atelier.

Concrètement, la liaison entre le Bassin et le Fémur (Cuisse) du robot se décompose ainsi :

![Schéma Éclaté du Cardan de Hanche](./assets/img_hip_kinematic_chain.png)

### Maillon 1 : L'Axe Yaw (Moteur RS-03)
* **Emplacement** : Fixe, monté *à l'intérieur* ou directement sous le châssis du bassin (Pelvis). Il pointe vers le bas (axe Z).
* **Rôle** : Tourner la pointe du pied vers l'intérieur ou l'extérieur.
* **Connexion sortante** : Son rotor (qui tourne) porte la première équerre (un L-Bracket usiné en alu massif).

### Maillon 2 : L'Axe Roll (Moteur RS-03)
* **Emplacement** : Fixé horizontalement (axe X) à l'extrémité du L-Bracket venant du moteur Yaw. Il regarde devant ou derrière le robot.
* **Rôle** : Permettre au robot de faire le grand écart ou d'écarter la jambe sur le côté.
* **Connexion sortante** : Son rotor porte la deuxième équerre (un U-Bracket ou L-Bracket).

### Maillon 3 : L'Axe Pitch (Gros Moteur RS-04)
* **Emplacement** : Fixé perpendiculairement (axe Y) à l'extrémité de l'équerre du moteur Roll. Il regarde sur les côtés du robot.
* **Rôle** : C'est le boss de la motricité. Il encaisse la charge principale pour lever la cuisse, s'accroupir, ou propulser le robot en avant. C'est pour cela qu'il nécessite un RS-04 (120 Nm) contre des RS-03 pour les deux autres.
* **Connexion sortante** : Son rotor est la ligne d'arrivée du bassin.

### Le Bout de la Chaîne : Le Fémur Hybride
Et c'est ici - *et uniquement ici !* - que vient se greffer notre **"Fémur Hybride en Sandwich"** (décrit dans le document 24).
Les deux épaisses plaques latérales du fémur viennent prendre en sandwich l'interface (cloche/rotor) du dernier moteur, le RS-04 de Pitch. 

Le fémur, en réalité, ne "sait pas" qu'il y a 2 autres moteurs au-dessus de lui. Il n'est attaché qu'au dernier maillon de la chaîne.

---

## 4. Conséquences pour l'Ingénierie (Usinage C500)

L'énorme avantage de rejeter le "cluster" touffu du K-Bot pour cette chaîne séquentielle, c'est l'usinabilité immédiate !

Nous avons réduit la hanche d'une géométrie 3D impénétrable à **seulement 2 pièces mécaniques simples (Brackets)** :
1. **Le "Yaw-Roll Bracket"** : Une simple équerre de profilé aluminium.
2. **Le "Roll-Pitch Bracket"** : Une seconde équerre en aluminium reliant le deuxième et le troisième moteur.

La D-Bot peut ainsi s'appuyer sur des blocs massifs d'aluminium (7075-T6 de haute résistance) taillés par la C500. Ces Brackets mesurent tout au plus 5 à 8 cm de long chacun, offrant une rigidité exceptionnelle sans le moindre risque de flambement, contrairement aux longues pièces en plastique du dos ou des tibias.

> **Verdict / Action Recommandée** : Toute la modélisation CAO du bloc pelvien doit se concentrer sur le design ultra-rigide de ces 2 Brackets de liaison. C'est la seule façon moderne et viable de raccrocher notre "Fémur Hybride Sandwich" aux 3 DOFs exigés par les algorithmes de locomotion (Isaac Gym).
