# 🔍 Recherche Approfondie : Modèles CAO de Robots Humanoïdes Open-Source

Ce document recense les projets de robots humanoïdes de premier plan, notamment les initiatives chinoises récentes et les alternatives internationales, qui publient leurs fichiers de conception mécanique éditables (STEP, Onshape).

L'objectif est d'identifier des bases de travail solides (designs de torse) pour accélérer le développement du D-Bot sans avoir à concevoir chaque forme bionique complexe à partir de zéro dans Fusion 360.

---

## 🎨 0. Visualisation & Style de Design

Voici une comparaison visuelle générée en haute définition des deux philosophies de design majeures pour les torses humanoïdes de pointe :

````carousel
![Design Fourier N1 Style](media/design_fourier_n1_style.png)
<!-- slide -->
![Design Asimov v1 Style](media/design_asimov_v1_style.png)
````

*   **À gauche (Fourier N1 Style)** : Une esthétique "produit commercial" ultra-lisse et bionique. Les panneaux de carénage enveloppent entièrement la structure, l'électronique et le câblage sont dissimulés, et les actionneurs intégrés (moteurs couples) sont noyés dans la ligne générale du robot.
*   **À droite (Asimov v1 Style)** : Une esthétique "châssis de laboratoire" squelettique et technique. La structure externe en aluminium usiné CNC 7075 et en pièces de jonction foncées en Nylon PA12 (MJF) est entièrement apparente. Les moteurs brushless, les engrenages et les cartes électroniques sont visibles et faciles d'accès pour la maintenance.

---

## 🇨🇳 1. Les Robots Humanoïdes Chinois

### A. **Fourier N1 (Nexus Open Ecosystem Initiative)**
* **Développeur** : Fourier Intelligence (Shanghai)
* **Hauteur / Poids** : 1.3 m / 38 kg
* **Statut Open-Source** : Partiellement ouvert. Fourier a annoncé en avril 2025 l'ouverture des plans structurels et de la nomenclature complète (BOM) pour son modèle d'ingénierie N1.
* **Fichiers disponibles** : 
  * Fichiers CAO (STEP/IGES pour usinage et impression)
  * Modèles URDF pour la simulation
  * Guide de montage et nomenclature complète
* **Où les trouver** : Sur le GitHub officiel de Fourier Intelligence (`FFTAI/Wiki-GRx-Models` pour les visuels de simulation, et les dépôts matériels liés au Nexus N1).
* **Points Forts pour le Torse** : Look commercial haut de gamme, design bionique d'une grande fluidité esthétique, gestion interne optimisée pour le câblage et l'intégration des actionneurs.

### B. **Qinglong / OpenLoong**
* **Développeur** : Consortium dirigé par la Shanghai Humanoid Robotics Manufacturing Innovation Center et la fondation OpenAtom.
* **Hauteur / Poids** : 1.85 m / 80 kg (Taille réelle)
* **Statut Open-Source** : Entièrement open-source pour le matériel et le contrôle.
* **Fichiers disponibles** :
  * Modèles CAO complets
  * Dépôts de contrôle dynamique (WBC/MPC)
* **Où les trouver** : Hébergé principalement sur **AtomGit** (la plateforme open-source chinoise) sous le projet [OpenLoong-Hardware](https://atomgit.com/openloong/OpenLoong-Hardware).
* **Points Forts pour le Torse** : Architecture extrêmement robuste et éprouvée pour supporter de lourdes charges.
* **Limites** : Très lourd et complexe, typé ingénierie industrielle lourde. Difficilement imprimable en une seule fois sur une Qidi Plus 4 sans découpes majeures.

### C. **Tiangong**
* **Développeur** : Beijing Humanoid Robot Innovation Center
* **Statut Open-Source** : Axé principalement sur la simulation et le contrôle.
* **Fichiers disponibles** : URDF et meshes STL. Les fichiers sources de CAO originaux (STEP paramétriques éditables) restent fermés.

---

## 🌍 2. Les Meilleurs Modèles Open-Source Internationaux

### A. **LeRobot Humanoid (Hugging Face)** ⚡ *(Recommandé)*
* **Développeur** : Hugging Face
* **Hauteur / Poids** : Format de bureau (low-cost ~2500$)
* **Statut Open-Source** : 100% libre et conçu dès le départ pour la fabrication additive (FDM/impression 3D).
* **Fichiers disponibles** :
  * Fichiers CAO complets (STEP éditables)
  * Fichiers STL optimisés pour l'impression 3D
  * URDF et simulateur MuJoCo intégrés
* **Où les trouver** : [Virgileboat/lerobot-humanoid-hardware](https://github.com/Virgileboat/lerobot-humanoid-hardware)
* **Points Forts pour le Torse** : Il partage la même philosophie que l'Option C de votre D-Bot (boîtiers modulaires imprimés en 3D reliés par des tubes). C'est la base la plus rapide à modifier et directement imprimable sur votre Qidi Plus 4 sans adaptations géométriques complexes.
* **Précision** : La version matérielle actuelle se concentre uniquement sur la partie bipède (jambes et bassin). La partie haute (torse complet, bras) est prévue dans la feuille de route à venir.

### B. **Berkeley Humanoid Lite (UC Berkeley)**
* **Développeur** : UC Berkeley Hybrid Robotics Lab
* **Statut Open-Source** : Entièrement libre via la plateforme cloud **Onshape**.
* **Fichiers disponibles** :
  * Fichiers CAO natifs Onshape (exportables en STEP en 3 clics)
  * Fichiers de simulation et de contrôle
* **Où les trouver** : Liens sur leur [documentation officielle](https://berkeley-humanoid-lite.gitbook.io/docs/releases).
* **Points Forts pour le Torse** : Très modulaire et facile à adapter grâce à la structure Onshape interactive. Vous pouvez mesurer directement chaque pièce avant de l'exporter.

### C. **Asimov v1**
* **Développeur** : Asimov Robotics Inc.
* **Hauteur / Poids** : 1.2 m
* **Statut Open-Source** : Matériel disponible sur GitHub.
* **Fichiers disponibles** : Fichiers STEP éditables et STL pour l'assemblage complet.
* **Où les trouver** : [asimovinc/asimov-1](https://github.com/asimovinc/asimov-1)

---

## 🎯 Plan d'Action Recommandé pour D-Bot

1. **Récupérer le Torse LeRobot (Hugging Face)** : Télécharger le sous-ensemble du torse pour comprendre comment ils ont structuré les pièces d'impression 3D autour des axes.
2. **Exporter le Berkeley Humanoid Lite via Onshape** : Naviguer dans leur projet public, isoler les blocs thoraciques et pelviens, et les exporter en format `.step` pour les importer dans Fusion 360.
3. **Fusionner avec votre Option C** : Utiliser ces modèles comme références dimensionnelles et esthétiques pour créer vos boîtiers de clampage sur vos 4 tubes carbone Ø25 mm.
