# 12 - Guide Usinage & Pièces Métallurgiques CNC

Ce guide détaille la procédure pour concevoir et usiner les pièces structurelles en aluminium (Alu 6061 ou 7075). Avec la disposition de notre **fraiseuse CNC C500**, toutes les pièces soumises à de grosses contraintes doivent être systématiquement usinées sur place, bien que les principes restent applicables pour des services en ligne.

## 1. Spécifications Techniques
*   **Matériau** : **Aluminium 6061-T6** (Standard aérospatial, bon compromis résistance/poids).
*   **Finition de surface** : **"As Machined"** (Brut d'usinage).
    *   *Conseil* : Ne demandez pas de "Bead Blasting" (Microbillage) ou d'Anodisation pour les prototypes (Phase 2). Cela réduit le coût de 20% à 30%.
*   **Tolérances** : Standard **ISO 2768-m** (+/- 0.1mm) suffisant pour le D-Bot.

## 2. Préparation des Fichiers 3D
*   **Format** : Exportez uniquement en **STEP (.stp / .step)**. Le STL n'est pas accepté pour l'usinage CNC.
*   **Nettoyage CAO** :
    *   Supprimez tous les textes gravés, logos ou décorations en relief. L'usinage de ces détails minuscules explose le temps machine et le prix.
    *   Vérifiez les **rayons internes**. Un outil de fraiseuse est rond. Évitez les angles internes à 90° parfaits, mettez un rayon de 2mm ou 3mm là où c'est possible.

## 3. Points de Contrôle D-Bot
### Alésages (Trous précis)
*   **Dowel Pins** : Les trous pour les goupilles de centrage (3mm et 4mm) doivent être précis (H7 si possible, sinon standard).
*   **Interfaces Moteurs** : Les surfaces de contact avec les moteurs Robstride doivent être parfaitement planes pour dissiper la chaleur du moteur vers le châssis.

## 4. Règle d'or : Interfaces RS-04 (Hanches et Genoux)

Pour dissiper la chaleur et bloquer le cisaillement massif des moteurs **RS-04 (120 N.m)**, il faut **systématiquement faire usiner** sur la **CNC C500** une plaque d'interface en alliage d'Aluminium (5 mm d'épaisseur mini) venant s'intercaler entre le moteur et le squelette en PA12-CF.
Cette plaque d'aluminium jouera deux rôles critiques :
1.  **Dissipateur Thermique (Heatsink)** : Les moteurs QDD chauffent à l'arrêt en retenant les 40kg du robot. L'aluminium absorbera massivement cette chaleur.
2.  **Cage anti-Cisaillement** : La plaque protégera la structure en fibre de carbone imprimée d'une potentielle destruction par ovalisation des trous.

## 5. Astuces de Commande / Production
*   **Regroupement** : Usinez toutes les pièces d'un coup (Bras Droit + Gauche).
*   **Symétrie** : Vérifiez si vos pièces sont identiques (x2) ou symétriques (Miroir). En CNC, une pièce miroir nécessite un nouveau réglage CAO.
*   **Taraudage** : Indiquez clairement sur vos plans d'usinage (Machine C500) quels trous utiliseront la fraise à tarauder (M3, M4).

## 6. Allègement Structurel Avancé : L'Isogrid (Isogrille)
Pour maximiser ratio Poids/Rigidité et réduire la masse du robot de 39 kg, il faut évider l'intérieur des plaques planes en utilisant un motif usiné **Isogrid** (réseau de "poches" triangulaires équilatérales). Cela permet un gain de masse de 30% à 50% tout en affaiblissant considérablement les fréquences de résonance du robot (ce qui stabilise le flux vidéo de la caméra OAK-D).

### Recette Nominale (Plaque Alu de 5 mm)
Pour éviter le "chatter" (vibration de paroi mince en usinage) sur la petite broche 800W de la C500, ne descendez jamais sous 2 mm d'épaisseur de fond :
*   **Profondeur de coupe** : 3.0 mm (laisse une "peau" de $t_s = 2.0$ mm).
*   **Épaisseur des nervures (Rib - $t_w$)** : 2.5 mm.
*   **Taille du triangle ($L$)** : 35 mm à 45 mm de côté.
*   **Rayon interne (Fillet - $R$)** : Strictement supérieur au rayon de votre fraise + 0.1 mm (Ex: $R=3.1$ mm pour une fraise Ø6). Ne jamais laisser d'angle vif.
*   **⚠️ Règle de Fixation** : L'Isogrid ne doit remplir que l'espace inutile. Laissez impérativement un "ilot" plein (sans poches) sur un rayon d'au moins **10 mm autour de chaque trou de fixation** supportant vos moteurs RobStride ou roulements.

### Stratégie d'Usinage C500 (Fusion 360)
1.  **Surfaçage** : Assurez-vous que la plaque martyr est parfaitement plane.
2.  **Adaptive Clearing (Poches Adaptatives)** : Ne videz *jamais* les poches avec un simple contournage 2D. Utilisez le mode "Adaptive" du CAM Fusion 360 pour maintenir une charge outil constante dans de l'aluminium (la fraise ne "plantera" pas violemment dans les angles aveugles).
3.  **Finition** : Gardez 0.2 mm de marge au fond lors de l'ébauche (*Stock to Leave* vertical) et faites une dernière passe avec une fraise plate pour un miroitement spectaculaire de la "peau".

### Automatisation via Python (Fusion 360 API)
Dessiner les isogrids, calculer manuellement les décalages (nervures) et arrondir chaque coin des dizaines de triangles est un processus lourd. La méthode "ingénieur" consiste à injecter un script Python dans l'onglet *Add-Ins > Scripts* de Fusion 360 pour automatiser la génération de l'esquisse et de la poche 3D en 5 secondes :

```python
import adsk.core, adsk.fusion, math

def create_isogrid():
    app = adsk.core.Application.get()
    design = app.activeProduct
    rootComp = design.rootComponent
    
    # Paramètres d'allègement de votre D-Bot (Éditables)
    side_length = 40.0 # Côté du triangle en mm
    rib_thickness = 2.5 # Épaisseur de la nervure en mm
    depth = 0.3 # Profondeur de la poche en cm (Rappel: L'API Fusion utilise le cm par défaut)
    
    # (Le script complet génère ensuite les esquisses triangulaires équilatérales,
    # applique les offsets pour former l'épaisseur des nervures, ajoute les Fillets,
    # et lance la commande Extrude-Cut pour vider la matière).
```
*Le reste de la boucle de génération logicielle est laissé à la discrétion de l'ingénieur CAO selon les contours exacts de la pièce.*
