# 11 — Guide de Prototypage Structurel & Recuit Thermique (Sunlu FilaDryer E2)

Ce document rassemble les méthodologies de prototypage rapide en impression 3D pour remplacer temporairement les pièces en Aluminium 6061-T6 sur le robot **D-Bot**, ainsi que le protocole d'utilisation du sécheur/recuiseur **Sunlu FilaDryer E2**.

> [!IMPORTANT]
> **📐 Spécifications de la Chambre & Dimensions Utiles de Recuit (Sunlu FilaDryer E2)** :
> 
> | Caractéristique de la Chambre | Valeur Maximale Utile | Note d'Intégration Pièces D-Bot |
> | :--- | :---: | :--- |
> | **Largeur Utile ($L$)** | **220 mm** | Permet de loger les grandes brides et coquilles d'épaule. |
> | **Profondeur Utile ($P$)** | **210 mm** | Adaptée aux demi-coques d'articulation et nœuds centraux. |
> | **Hauteur Utile ($H$)** | **120 mm** (jusqu'à **130 mm** sans grille) | Accueille jusqu'à 2 carters d'épaule RS-04 en simultané. |
> | **Diagonale Maximale Utile** | **~280 mm** | Pour les pièces allongées (fémurs, brackets) orientées à 45 deg. |
> | **Volume Utile Total** | **~5,5 Litres** | Diffusion thermique homogène 360° avec ventilation forcée. |

---

## 1. Prototypage Structurel en Impression 3D (Remplacement Temporaire Alu 6061-T6)

### 1.1 Contexte et Objectif
En attendant la réception et la mise en service de la **CNC C500 Networks**, la réalisation des pièces de structure (brackets des moteurs d'épaule RS-04 / RS-03 / RS-02, nœuds de jonction, hubs d'articulation) s'effectue par impression 3D composite sur l'imprimante **Qidi Plus 4**.

L'objectif de ces prototypes est d'assurer la **validation fonctionnelle de la chaîne complète de bout en bout** :
* Validation du câblage électrique et du bus CAN (48V alimentation, 12V auxiliaire, bus CAN 1 Mbps).
* Validation des cartes électroniques, convertisseurs DROK et micro-hubs.
* Intégration logicielle **ROS2** : cinématique inverse, boucles de contrôle, limites articulaires et communication avec la main **D-Hand**.
* Validation des mouvements à vide ou sous sollicitations dynamiques modérées (sans charges extrêmes).

---

## 2. Matrice de Choix des Filaments de Prototypage

| Filament | Propriétés & Résistance | Recuit Requis ? | Usage pour D-Bot |
| :--- | :--- | :--- | :--- |
| **PA12-CF** (Nylon 12 + Carbone) | Résistance 90-115 MPa, très haute résilience aux chocs, faible absorption d'eau pour un Nylon. | **Oui** (Recuit à 90°C - 100°C) | **Choix N°1** pour pièces de structure sollicitées (brackets, fémurs). |
| **PPA-CF** (Polyphthalamide + Carbone) | Résistance > 120-140 MPa, module proche de l'Alu 6061, HDT très élevée. | **Oui** (Recuit à 100°C - 110°C) | **Choix N°2** pour rigidité maximale sous fortes charges statiques. |
| **PETG-CF** (PETG + Carbone) | Résistance 55-70 MPa, très faible warping, grande facilité d'impression. | **Non** (Polymère amorphe, voir section 3.3) | **Idéal pour prototypage rapide** à vide / validation ROS2 et câblage. |

---

## 3. Équipement & Procédure de Recuit : Sunlu FilaDryer E2

### 3.1 Spécifications du Sunlu FilaDryer E2
Le **Sunlu FilaDryer E2** est un sécheur et recuiseur 2-en-1 spécifiquement conçu pour les filaments et pièces techniques d'ingénierie.

* **Température Maximale** : **jusqu'à 110°C** (vs 70°C max pour la série S2).
* **Fonctions Duales** :
  1. **Séchage dynamique de filaments** : Élimination de l'humidité avant et pendant l'impression via tube PTFE guidé.
  2. **Recuit thermique de pièces imprimées (Annealing)** : Maintien en température contrôlée pour recristallisation.
* **Capacité** : 2 bobines de 1 kg ou pièces imprimées volumineuses.
* **Plage de température** : 40°C à 110°C avec minuterie programmable.

---

### 3.2 Utilisation et Avantages pour D-Bot

#### 1. Séchage des Filaments Hygroscopiques (Avant Impression)
Les polymères techniques (PA12-CF, PPA-CF, PETG-CF) doivent être séchés au Sunlu E2 pour éviter le bullage et la délamination :
* **PA12-CF / PPA-CF** : Séchage à **80°C à 90°C pendant 8 h à 12 h**.
* **PETG-CF** : Séchage à **65°C pendant 6 h**.

#### 2. Recuit Thermique Post-Impression (Semi-cristallins : PA12-CF / PPA-CF)
Pour les pièces en PA12-CF ou PPA-CF, le passage au Sunlu E2 à **90°C à 100°C pendant 2 h à 4 h** apporte :
* **Cohésion Z (Inter-couches)** : Augmentation de **+20% à +30%** de la résistance à l'arrachement entre couches.
* **Hausse de la HDT (Heat Deflection Temp)** : Température de déflexion repoussée au-delà de 150°C à 180°C.
* **Refroidissement progressif obligatoire** : Laisser la pièce refroidir lentement dans le boîtier fermé du Sunlu E2 pour éviter le vrillage thermique.

---

### 3.3 Analyse Spécifique du PETG-CF et du Recuit

#### Le PETG-CF a-t-il intérêt à être recuit ?
**Non. Le recuit classique de cristallisation n'est ni nécessaire ni bénéfique pour le PETG-CF.**

#### Explication Physique :
1. **Structure Amorphe** : Le PETG (Polyethylene Terephthalate Glycol-modified) contient du glycol destiné à empêcher la cristallisation. Il s'agit d'un polymère amorphe qui ne possède pas de phase semi-cristalline à développer sous chauffe.
2. **Effet d'un chauffage au-delà de Tg (75°C)** : Si le PETG-CF est chauffé au-dessus de sa température de transition vitreuse (Tg ~ 75°C) dans le Sunlu E2 (ex: à 85°C-90°C), il ramollit et s'affaisse sous son propre poids.
3. **Seule opération utile (Relaxation des contraintes à 70°C)** : Un maintien doux à **70°C (sous Tg)** pendant 2h relaxe les micro-tensions de retrait sans déformer la pièce. Cependant, le gain mécanique reste marginal (0% à 3% sur le module).

**Consigne officielle pour D-Bot** : Séchez le PETG-CF dans le Sunlu E2 avant impression, mais **ne réalisez aucun recuit post-impression sur le PETG-CF**. Réservez le recuit thermique aux filaments **PA12-CF** et **PPA-CF**.

---

## 4. Guide de Tranchage (Slicing) sur Qidi Plus 4

Pour les prototypes de brackets d'épaule (RS-04 / RS-03) en PETG-CF ou PA12-CF :

* **Périmètres (Walls)** : **6 à 8 parois minimum** (la reprise de torsion et le cisaillement des vis s'effectuent sur les parois extérieures).
* **Remplissage (Infill)** : **50% à 75% Gyroïde** (ou 100% sur les brides de serrage).
* **Couches Sup / Inf** : 6 couches minimum.
* **Buse** : Carbure de Tungstène 0.4 mm ou 0.6 mm.
* **Températures Qidi Plus 4** :
  * Buse : 270°C (PETG-CF) / 290°C (PA12-CF).
  * Plateau : 80°C.
  * Enceinte active : **50°C** (PETG-CF) / **65°C** (PA12-CF).

---

## 5. Précautions d'Assemblage et de Test sous ROS2

1. **Fixations Mécaniques** :
   * Privilégier les vis traversantes avec de larges rondelles et écrous frein (Nylostop) ou des inserts laiton Ruthex posés à chaud. Ne pas tarauder directement dans le plastique composite.
2. **Protection Thermique du Plastique (Bridage Logiciel ROS2)** :
   * Le stator des moteurs RobStride chauffant sous maintien statique, la température du carter peut approcher 60°C à 70°C.
   * **Consigne** : Lors des tests ROS2 à vide, brider le registre `Max Torque` dans le firmware / driver à **20% ou 30%** pour limiter l'échauffement thermique sur les brackets imprimés.
