# 23 — Étude Mécanique : Découplage des Articulations et Transmission de Puissance

Cette étude fait suite à l'analyse de l'architecture biomimétique (Doc 22b) nécessitant le découplage des efforts (poids, flexion) par rapport au couple de rotation pur fourni par le moteur.

---

## 1. La Solution du Roulement Annulaire (Slewing Ring / Thin Section)

Le principe fondamental du "découplage" en robotique est de ne jamais laisser l'arbre d'un servomoteur supporter le poids ou le bras de levier d'un membre (moment de flexion). 

La structure externe du bras doit reposer sur un **grand roulement annulaire** (ou palier). L'axe du moteur passe au centre de ce roulement et ne fait qu'entraîner la rotation.

### Types de roulements recommandés :
1. **Thin Section Bearings (Roulements à section mince)** : Très prisés en robotique car ils offrent un grand diamètre intérieur (pour passer les câbles) tout en étant ultra-légers.
2. **Cross Roller Bearings (Roulements à rouleaux croisés)** : La "Rolls-Royce" de la robotique. Les rouleaux sont disposés en X, ce qui permet à un seul roulement d'encaisser des charges radiales, axiales et des moments de renversement massifs.

### Exemples de Références Industrielles :
*   **Kaydon (Groupe SKF)** : La série *Reali-Slim®* est le standard mondial absolu pour les bras robotiques et l'aérospatial.
*   **IKO International / THK** : Leurs *Cross Roller Rings* (séries CRB, RU) sont utilisés dans 90% des articulations de cobots industriels (UR, KUKA).
*   **Silverthin** : Excellente alternative américaine, souvent plus abordable pour les prototypes.

---

## 2. Focus : Spline Coupling vs Joint Flexible

Une fois la structure portée par le roulement annulaire, il faut relier l'axe du moteur à la coque rotative. C'est ici qu'intervient l'accouplement.

### A. Spline Coupling (Accouplement Cannelé)
C'est un arbre rainuré qui s'insère dans un moyeu correspondant.
*   **Avantages** : Transmission de couple **massive**. Zéro backlash (jeu) si bien usiné. Permet un léger glissement *axial* (pratique pour l'assemblage ou la dilatation thermique). Très utilisé pour les modules "Quick-Disconnect" (démontage rapide d'un bras).
*   **Inconvénients** : **Zéro tolérance au désalignement**. Si votre moteur n'est pas parfaitement centré au dixième de millimètre avec votre grand roulement annulaire, le spline va forcer, créer des vibrations et détruire les roulements du moteur.

### B. Joint Flexible (Accouplement Élastique)
C'est un accouplement qui intègre une partie déformable (soufflet métallique, flector en élastomère, ou joint d'Oldham).
*   **Avantages** : **Tolère le désalignement** (angulaire, radial et axial). C'est le véritable "sauveur" en prototypage et en impression 3D/usinage amateur, car il absorbe les imperfections géométriques. Il amortit également les chocs dynamiques, protégeant le réducteur du moteur.
*   **Inconvénients** : Plus volumineux, et certains modèles bon marché peuvent introduire un léger backlash (jeu élastique).

> **Recommandation D-Bot** : Si vous usinez vous-même les pièces (Aluminium CNC ou Impression 3D Carbone), optez pour un **Accouplement Flexible type Oldham ou à Soufflet (Bellows)**. Il protégera vos moteurs RS-02 des inévitables micro-désalignements avec la structure.

---

## 3. Les Systèmes "Prêts à l'Emploi" (COTS - Modules Tout-en-un)

Plutôt que d'acheter un moteur d'un côté, un roulement de l'autre, et d'usiner les pièces de liaison, l'industrie a créé des modules qui intègrent tout : le moteur, l'encodeur, l'accouplement, et un énorme roulement à rouleaux croisés. 

Ces systèmes s'appellent des **Hollow Rotary Actuators** (Actionneurs Rotatifs Creux) ou **Slewing Drives**.

### Avantage majeur :
Ils possèdent un grand trou central (Hollow Bore) pour passer les câbles du poignet et des doigts directement à travers l'axe, empêchant le vrillage des câbles !

### Références commerciales (En métal, prêts à monter) :

1.  **Oriental Motor (Série DGII / DH)**
    *   *Concept* : Table tournante creuse intégrant un moteur pas-à-pas en boucle fermée et un énorme roulement à rouleaux croisés. 
    *   *Matériau* : Acier/Aluminium. Très robuste, on visse directement la charge dessus.
2.  **Harmonic Drive (Série FHA / CSF)**
    *   *Concept* : La référence absolue en robotique humanoïde. Réducteur à onde de déformation ultra-compact avec arbre creux massif. Zéro backlash absolu.
    *   *Note* : C'est ce qui équipe les bras des robots Spot (Boston Dynamics) et Optimus.
3.  **Sango Automation / Tallman Robotics**
    *   *Concept* : Fabricants asiatiques proposant des plateformes rotatives creuses (Hollow Rotary Platforms) très similaires à Oriental Motor, mais souvent vendues nues (pour y fixer votre propre moteur RS-02 via une courroie ou un joint flexible interne). 

### Conclusion pour la Conception du D-Bot
Si vous avez le budget et l'espace, l'achat d'une **Hollow Rotary Platform** nue (sans moteur) dans laquelle vous insérez votre RS-02 est la voie la plus professionnelle. La plateforme encaissera 100% des contraintes du bras de levier, et vous offrira un passage de câble parfait pour les tendons et les fils de la main.
