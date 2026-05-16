# 🦾 **Spécifications Finales – Torse (D‑Bot) – Version V1.x**  

*Document de référence unique pour le module **Torse** du robot humanoïde D‑Bot (40 kg). Toutes les données proviennent des sources fournies ; aucune valeur n’a été extrapolée. Les éléments manquants sont indiqués **[À COMPLÉTER]**.*

---

## 1. Vue d’Ensemble (Version Actuelle)

Le torse de D‑Bot est une **cage tubulaire boulonnée** en aluminium, constituée de profilés creux rectangulaires reliés par des nœuds de jonction usinés CNC.  
- **Hauteur (épaule → hanche)** : **420 mm**  
- **Largeur (latéral droit ↔ latéral gauche)** : **300 mm**  
- **Profondeur (avant ↔ arrière)** : **220 mm**  

Cette architecture permet d’accueillir les sous‑modules internes (batterie 12 S, Jetson Orin Nano, PDB Matek, câblage CAN) tout en offrant une rigidité suffisante pour les charges dynamiques générées par la marche (facteur dynamique ≈ 3).  

Les coques extérieures sont imprimées en **PETG‑CF** (non structurelles) et servent uniquement de protection et d’esthétique.

---

## 2. Spécifications Matérielles Validées  

| **Composant** | **Quantité** | **Dimensions** | **Matériau** | **Section / Masse** | **Couple / Charge Max** | **Facteur de Sécurité (FS)** | **Remarques** |
|---|---|---|---|---|---|---|---|
| **Montants verticaux** | 4 | 40 × 40 mm, épaisseur 2 mm, longueur 420 mm | Alu 6060 T6 (Re ≈ 150 MPa) | Aire ≈ 304 mm², masse ≈ 136 g/unité | Compression ≈ 0.97 MPa (P/4) | **≈ 155** | Vérif. flambage : Pcr ≈ 272 kN (FS ≈ 922) |
| **Traverse basse (hanches) – largeur** | 2 | 60 × 60 mm, épaisseur 2 mm, longueur 300 mm | Alu 6060 T6 | Masse ≈ 190 g/unité | Torsion ≈ 10.3 MPa, Flexion ≈ 5.1 MPa, Von Mises ≈ 18.6 MPa | **≈ 8.1** | Supporte couple moteur RS‑04 (120 N·m) |
| **Traverse basse (hanches) – profondeur** | 2 | 60 × 60 mm, épaisseur 2 mm, longueur 220 mm | Alu 6060 T6 | Masse ≈ 139 g/unité | Identique à largeur (charge répartie) | **≥ 8** |  |
| **Traverse haute (épaules) – largeur** | 2 | 35 × 35 mm, épaisseur 2 mm, longueur 300 mm | Alu 6060 T6 | Masse ≈ 108 g/unité | Flexion ≈ 2.9 MPa (bras ≈ 4 kg) | **≈ 52** |  |
| **Traverse haute (épaules) – profondeur** | 2 | 35 × 35 mm, épaisseur 2 mm, longueur 220 mm | Alu 6060 T6 | Masse ≈ 79 g/unité | Identique à largeur | **≥ 50** |  |
| **Nœuds de jonction CNC** | 8 | Bloc 50 × 50 × 50 mm usiné (tri‑axial) | Alu 6061 T6 (Re ≈ 275 MPa) | Masse ≈ 50 g/unité | Transfert de charge entre tubes | **≥ 10** (calcul interne) | Tenons h7/H7, 2× vis M6 par face, Loctite 243 |
| **Boulonnerie (vis M6 12.9)** | ~48 | - | Acier 12.9 | Masse ≈ 8 g/vis | Résistance à traction ≈ 1 200 N | **≥ 10** (selon charge) | Toutes les fixations structurelles |
| **Coques extérieures** | 2 (avant/arrière) | Adaptées à la cage (300 × 220 mm) | PETG‑CF (impression 3D) | **[À COMPLÉTER]** | Non structurel | – | Fixées M3 dans inserts Ruthex |
| **Total masse estimée du squelette** | – | – | – | **≈ 2.36 kg** | – | – | ≈ 5.9 % du poids total du robot |

> **Note** : Les valeurs de couple/charge max sont issues des calculs présentés dans *STUDY_Squelette_Torse.md* (section 4). Aucun test physique n’a encore été réalisé ; les facteurs de sécurité sont donc théoriques.

---

## 3. Nomenclature (BOM Locale)

| **Référence** | **Désignation** | **Quantité** | **Fournisseur** | **Référence Fournisseur** | **Prix Unitaire** | **Prix Total** |
|---|---|---|---|---|---|---|
| **TUBE‑V40** | Tube carré 40 × 40 × 2 mm, Alu 6060 T6, longueur 420 mm | 4 | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** |
| **TUBE‑B60‑W** | Tube carré 60 × 60 × 2 mm, Alu 6060 T6, longueur 300 mm | 2 | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** |
| **TUBE‑B60‑D** | Tube carré 60 × 60 × 2 mm, Alu 6060 T6, longueur 220 mm | 2 | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** |
| **TUBE‑H35‑W** | Tube carré 35 × 35 × 2 mm, Alu 6060 T6, longueur 300 mm | 2 | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** |
| **TUBE‑H35‑D** | Tube carré 35 × 35 × 2 mm, Alu 6060 T6, longueur 220 mm | 2 | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** |
| **NODE‑CNC** | Nœud de jonction tri‑axial usiné, bloc 50 × 50 × 50 mm, Alu 6061 T6 | 8 | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** |
| **SCREW‑M6‑12.9** | Vis métrique M6, classe 12.9, longueur 30 mm (exemple) | 48 | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** |
| **COUPE‑PETG‑CF** | Plaques PETG‑CF imprimées 3 mm, format 300 × 220 mm | 2 | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** |
| **LOCTITE‑243** | Loctite 243 (medium strength thread locker) – 10 ml | 1 | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** |

> **Remarque** : Les fournisseurs et références exactes n’ont pas été spécifiés dans les sources. Ils seront complétés dès réception des devis fournisseurs.

---

## 4. État de la Conception (CAD & Simulation)

| **Élément** | **Statut** | **Fichier(s) CAD** | **Commentaires** |
|---|---|---|---|
| Cage tubulaire (tubes + nœuds) | **Modélisation 80 %** | `torso_frame.f3d` (Fusion 360) | Dimensions externes validées ; besoin de vérifier dégagement interne pour batterie et cartes. |
| Nœuds CNC | **Usinage programmé** | `node_cnc_cam.nc` (G‑code) | Parcours CNC à valider sur Carvera / C500. |
| Coques PETG‑CF | **Modélisation 100 %** | `torso_shells.f3d` | Prêtes pour impression, à tester pour ajustement des inserts M3. |
| Analyse FEM | **Complète (statique)** | `torso_fem_analysis.fem` | Résultats présentés dans *STUDY_Squelette_Torse.md* (FS > 8). |
| Analyse dynamique (marches) | **À faire** | – | Simuler charges transitoires, valider facteur dynamique 3. |
| Gestion câblage interne | **Concept** | – | Utiliser le vide des tubes 40 × 40 comme chemin de câbles (CAN, alimentation). |

---

## 5. Instructions de Montage Critiques

1. **Pré‑assemblage des nœuds**  
   - Insérer les tenons des tubes dans les alésages du nœud (tolérance h7/H7).  
   - Vérifier le jeu axial : < 0.2 mm, sinon ajuster avec lime fine.  
   - Appliquer **Loctite 243** sur chaque vis M6 avant serrage.

2. **Serrage des vis M6**  
   - Utiliser une clé dynamométrique à **12 Nm** (classe 12.9).  
   - Serrage séquentiel en croix pour chaque nœud afin d’éviter les contraintes de déformation.

3. **Installation des traverses**  
   - Positionner d’abord la **traverse basse** (hanches) afin de garantir le parallélisme des montants.  
   - Vérifier l’alignement avec un niveau à bulle (tolerance ≤ 0.5 mm).  
   - Fixer la **traverse haute** (épaules) en suivant le même procédé.

4. **Passage des câbles**  
   - Introduire les gaines de câble dans les tubes 40 × 40 avant le serrage final.  
   - S’assurer que les courbures ne dépassent pas **30 mm** de rayon pour éviter l’endommagement du fil.

5. **Montage des coques PETG‑CF**  
   - Aligner les inserts Ruthex (M3) pré‑insérés dans la coque avec les points de fixation du châssis.  
   - Visser avec **M3 × 6 mm** à **4 Nm**.

6. **Contrôle final**  
   - Mesurer la distance entre les deux traverses (largeur) : **300 ± 1 mm**.  
   - Vérifier l’absence de jeu latéral sur chaque montant (déviation < 0.3 mm).  
   - Effectuer un test de charge statique (≈ 1 200 N) en appliquant une charge centrale sur la traverse basse pour confirmer le facteur de sécurité.

---

## 6. Backlog Technique & Questions en Suspens

| **Item** | **Description** | **Priorité** | **État** |
|---|---|---|---|
| **Fournisseurs / Prix** | Identification des fournisseurs pour chaque tube, nœud CNC, vis M6, PETG‑CF, Loctite. | Haute | **[À COMPLÉTER]** |
| **Longueurs exactes des tubes** | Confirmation des longueurs découpées (tolérance ± 1 mm) après réception. | Moyenne | **[À COMPLÉTER]** |
| **Analyse dynamique** | Simulation des impacts de marche (facteur dynamique 2.5‑3) sur les traverses. | Haute | **Non réalisée** |
| **Test de fatigue** | Essais cycliques sur le prototype complet (≥ 10 000 cycles). | Moyenne | **Non réalisé** |
| **Gestion thermique** | Étude du transfert de chaleur des moteurs RS‑04 vers la traverse basse (possibilité de dissipation via la cage). | Moyenne | **[À COMPLÉTER]** |
| **Intégration du système de câblage** | Validation du passage des câbles dans les tubes (diamètre maximal, protection EMI). | Haute | **[À COMPLÉTER]** |
| **Poids exact des coques PETG‑CF** | Mesure après impression (épaisseur, densité). | Faible | **[À COMPLÉTER]** |
| **Documentation des inserts Ruthex** | Références et procédures d’insertion dans les coques. | Faible | **[À COMPLÉTER]** |

---

## 7. Roadmap & Itérations Futures (Optionnel)

| **Version Future** | **Modification Proposée** | **Justification** |
|---|---|---|
| **V2.0** | Augmentation de l’épaisseur des traverses (de 2 mm à 3 mm) | Accroître la marge de sécurité pour des charges supérieures (ex. : ajout d’un exosquelette). |
| **V2.1** | Remplacement des nœuds CNC en Alu 6061 par des pièces en **titanium Ti‑6Al‑4V** | Réduction du poids tout en augmentant la résistance aux chocs. |
| **V2.2** | Intégration de **capteurs de contrainte** (strain‑gauge) dans les traverses | Monitoring en temps réel des charges pour la stratégie de contrôle dynamique. |
| **V3.0** | Passage à une architecture **cage en fibre de carbone** (composite) | Objectif de réduction de masse à < 2 kg pour le torse. |

*Ces itérations sont mentionnées uniquement à titre de planification et **ne figurent pas** dans les tableaux principaux du document.*