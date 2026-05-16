# Étude Comparative : Conception, Squelettisation & Hybridation du Fémur (Cuisse)

Ce document présente l'analyse d'ingénierie mécanique justifiant le rejet du tube carbone rond pour le fémur du D-Bot, l'étude comparative de 3 concepts alternatifs (Poutre en U, Treillis, Hybride), et fournit les directives FAO précises pour l'usinage sur la CNC NestWorks C500 et l'impression 3D Nylon-Carbone.

---

## 1. Pourquoi le Tube Carbone Rond est rejeté pour le Fémur ?

L'application d'un tube carbone cylindrique classique au fémur, bien que séduisante pour le gain de poids, se heurte à deux problèmes majeurs d'architecture système :

1.  **L'encombrement et la géométrie des interfaces (Hanche & Genou)** : 
    Le fémur doit relier la **Hanche** (un cluster massif de 2 à 3 moteurs orientés à 90°, dont les volumineux RobStride RS-04 et RS-03) au **Genou** (moteur RS-04). Ces articulations exigent des fixations structurelles très larges (brackets en "U" ou en "H"). Transférer les couples extrêmes de ces larges embases vers un tube rond étroit (Ø40 ou Ø50 mm) exigerait des adaptateurs (inserts) en entonnoir géants et lourds en aluminium. Le poids gagné sur le tube carbone serait totalement reperdu dans ces adaptateurs d'extrémités.
2.  **L'intégration système (Câblage et Électronique)** : 
    Le fémur est la zone centrale d'acheminement des bus de données et de puissance (alimentation 48V/12V, bus CAN, câblages des capteurs) reliant le torse aux jambes. Un tube cylindrique fermé empêche toute intégration propre de l'électronique de contrôle et oblige à faire courir les faisceaux de câblage à l'extérieur du membre, les exposant aux pincements et aux collisions.

---

## 2. Comparatif des 3 Concepts Alternatifs pour le Fémur

Pour résoudre ces contraintes, l'ingénierie biomimétique moderne propose trois solutions adaptées aux moyens de fabrication locaux (fraiseuse CNC NestWorks C500 et imprimante Qidi Plus 4) :

### Concept 1 : La Poutre en U (Aluminium Plein CNC)
Un large profilé évidé en Aluminium 6061-T6 usiné dans la masse.
*   **Rigidité** : Exceptionnelle en flexion et en torsion.
*   **Intégration** : Offre de larges plans de vissage aux extrémités pour les blocs de Hanche et de Genou.
*   **Câblage** : Cavité interne parfaite pour protéger les câbles et cartes électroniques (Odrive, Moteus) sous des capots en plastique.
*   **Inconvénient** : Très lourd (~700g - 800g) et fort gaspillage de matière lors de l'usinage (beaucoup de copeaux).

### Concept 2 : L'Exosquelette en Treillis (Plates Carbone + Entretoises Alu)
Une structure en "boîte" formée de deux grandes plaques latérales parallèles en fibre de carbone découpées à la CNC, reliées par des entretoises en aluminium.
*   **Rigidité** : Excellente dans l'axe, mais plus sensible aux chocs latéraux et au voilage en torsion.
*   **Poids** : Ultra-léger (~300g - 400g).
*   **Câblage** : Les câbles passent au milieu mais restent visibles et exposés aux débris extérieurs.

### Concept 3 : La Solution Hybride (Alu *Iso-grid* évidé + Habillage PA12-CF) 🏆
Il s'agit de la recommandation ultime pour le D-Bot. On usine une poutre en aluminium 6061 ou 7075-T6 que l'on squelettise de manière agressive en fraisant des poches triangulaires (motif *Iso-grid* ou *Waffle-grid*). On vient refermer et rigidifier cette structure en y vissant/collant des coques structurelles en PA12-CF (Nylon chargé carbone).
*   **Rigidité** : Exceptionnelle (structure composite fermée stable en torsion).
*   **Poids** : Optimisé (~500g, soit -30% par rapport à l'Alu plein).
*   **Câblage** : Cavité interne fermée, étanche et ultra-sécurisée.
*   **Esthétique** : Finition premium et futuriste.

---

## 3. Ingénierie de Fabrication & Assemblage "Sandwich"

Afin de simplifier l'usinage sur la C500 et d'éliminer le gaspillage de matière, le fémur est conçu selon une architecture en **platines assemblées "Sandwich"** :

```
    Interface Hanche (Bloc CNC) ───┐
                                    ├──> Assemblé en sandwich par
    Plates Latérales (Joue 5mm) ────┤    Goupilles élastiques Mécanindus
                                    │    (Traversantes et débouchantes)
    Interface Genou (Bloc CNC) ─────┘
```

1.  **Les "Bouchons" Structurels (Haut & Bas)** : Deux petits blocs massifs en Aluminium 6061-T6 usinés. L'un possède l'empreinte pour le rotor du RS-04 de la Hanche, l'autre le logement berceau pour le RS-04 du Genou.
2.  **Les Joues Latérales** : Deux plaques plates d'Aluminium 7075-T6 de 5 mm d'épaisseur, évidées en Iso-grid (usinage rapide en 2.5D sur la C500).
3.  **L'Assemblage par Goupilles** : Les platines latérales s'encastrent précisément dans des rainures usinées sur les blocs Hanche/Genou. L'ensemble est verrouillé par des **goupilles élastiques transversales débouchantes**.
    *   *Intérêt mécanique* : Les goupilles offrent une résistance au cisaillement (secousses de la marche) infiniment supérieure aux filetages de vis dans l'aluminium, et ne craignent pas les vibrations. L'alésage débouchant permet un démontage facile au chasse-goupille.

---

## 4. Directives de Modélisation CAO & Fraisage FAO (C500)

Pour concevoir et usiner les deux joues latérales en Iso-grid, respectez scrupuleusement les cotes de sécurité suivantes :

1.  **Épaisseur brute de la plaque d'Alu** : **5 mm** (compromis parfait flexion/poids).
2.  **Largeur des branches du treillis (Struts)** : **4 mm à 6 mm** (ne jamais descendre en dessous de 4 mm pour éviter les vibrations à l'usinage).
3.  **Profondeur d'usinage des poches** : **3.5 mm**.
    *   *Règle d'or* : Ne transpercez pas les poches ! Conservez une **fine toile de fond (Web) de 1.5 mm d'épaisseur**. Cette membrane unit le treillis et apporte une rigidité au cisaillement et à la torsion phénoménale pour un surpoids quasi-nul.
4.  **Angles internes (Congés de poche)** : **Rayon > 3.175 mm (Ø6.35 mm)**.
    *   Dessinez des poches triangulaires aux angles généreusement arrondis. Cela permet l'usinage rapide des poches avec une fraise d'ébauche standard de 1/4" sans temps d'arrêt.

---

## 5. Synthèse Comparative des Solutions de Fémur

| Critère | A. Poutre en U (Plein) | B. Exosquelette Treillis | C. Solution Hybride (Iso-grid) |
| :--- | :--- | :--- | :--- |
| **Poids estimé** | Lourd (~700g - 800g) | **Ultra-Léger (~300g - 400g)** | **Optimisé (~500g)** |
| **Solidité torsion** | **Exceptionnelle** | Moyenne (vibrations vis) | **Exceptionnelle** (composite fermé)|
| **Usinage C500** | Simple (2 Setups) | **Très simple (découpe 2D)** | Complexe (poches profondes) |
| **Intégration Câble**| Parfaite (cavité) | Difficile (câbles visibles) | **Parfaite (cavité étanche)** |
| **Esthétique** | Industriel classique | Agressif "racing" | **Premium (Agility Digit)** |
| **Verdict D-Bot** | Solution de secours simple | Pour gain de poids extrême | 🏆 **Recommandé (Sweet Spot)** |
