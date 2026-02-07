# Guide Mécanique et Impression 3D

## 1. Paramètres de Conception (Fusion 360)
Pour intégrer correctement les vis DIN 912 et les inserts chauffants dans vos pièces imprimées, respectez scrupuleusement ces cotes.

### Chambrages (Counterbore) pour têtes de vis DIN 912
L'objectif est de noyer la tête de vis pour qu'elle ne dépasse pas, tout en laissant passer la clé Allen.
| Paramètre | Symbole | M3 | M4 |
| :--- | :--- | :--- | :--- |
| **Diamètre Chambrage** | $D_{cb}$ | **6.5 mm** | **8.5 mm** |
| **Profondeur** | $H_{cb}$ | **3.5 mm** | **4.5 mm** |
| **Passage de vis** | $d$ | 3.4 mm | 4.5 mm |

> **Astuce Fusion 360** : Utilisez l'outil *Hole (H)* > *Counterbore* > *Simple* > *Flat*.

### Trous pour Inserts (Heat-set)
Ces diamètres sont optimisés pour les inserts Ruthex standards.
| Paramètre | M3 | M4 |
| :--- | :--- | :--- | 
| **Diamètre perçage** | **4.2 - 4.5 mm** | **5.6 - 5.8 mm** |
| **Épaisseur paroi min** | 1.6 mm | 2.0 mm |
| **Épaisseur fond plan** | **3.0 mm** (Min) | **4.0 mm** (Min) |

---

## 2. Impression 3D (Qidi Plus 4)

### Matériau Recommandé : PETG-CF
Le PETG renforcé fibre de carbone (PETG-CF) est le meilleur compromis pour le D-Bot sur cette machine.
*   **Avantages** : Rigidité accrue (moins de flexion que le PETG pur), aspect mat qui cache les couches, bonne tenue en température (vers 80°C).
*   **Inconvénients** : Abrasif (utilisez une buse acier trempé).

### Paramètres de Slicer (OrcaSlicer / QidiSlicer)
*   **Matériau** : Creality Hyper **PETG-CF** (Recommandé pour débuter).
    *   *Alternative Pro* : **PA12-CF** (Nylon Carbone). Plus rigide et résistant à la chaleur, mais nécessite une enceinte chauffée et un séchage parfait. À réserver aux utilisateurs expérimentés.
*   **Températures** :
    *   **Buse** : 270°C
    *   **Plateau** : 80°C
    *   **Chambre (Active)** : 50°C
*   **Vitesse** : 200-300 mm/s.
*   **Hauteur de couche** : 0.20 mm (Standard) ou 0.16 mm (Précision engrenages).
*   **Périmètres (Walls)** : **4 à 5 murs minimum**. C'est le plus important pour la solidité des filetages/inserts.
*   **Remplissage (Infill)** :
    *   **100% (Solid)** pour : Hanches, Épaules, Supports Moteurs.
    *   **40% (Gyroid)** pour : Coques, avant-bras, tête.
*   **Séchage** : Obligatoire avant impression (65°C / 6h).

---

## 3. Montage des Moteurs Robstride

### Intégration Robstride 05 (RS05) - Cou / Poignets
*   **Ancrage** : Le couple de pointe (5.5 Nm) est élevé pour du plastique.
    *   Utilisez des **vis M4 x 12mm Acier 12.9 (Noir)** pour fixer le corps moteur au châssis. L'Inox est trop "mou" pour ces zones de force pure si vous démontez souvent.
*   **Longueur de vis** : Règle d'or = Épaisseur pièce plastique + (Profondeur trou moteur - 1mm).
    *   *Ne forcez jamais* si la vis touche le fond du trou borgne du moteur ! Vous détruiriez le filetage interne du stator.

### Roulements 608ZZ
*   Utilisés pour les articulations passives.
*   **Indépendance** : La bague intérieure et extérieure sont indépendantes. Vous pouvez fixer l'une au châssis et l'autre au membre mobile.
*   **Fichier STEP** : Disponible dans le dossier `Discussions/ou recuperer le modele step...`.

### Positionnement LiDAR Unitree L2
*   **Emplacement** : Sommet de la tête (Top of Head).
*   **Pourquoi ?** Champ de vision dégagé à 360° pour le SLAM.
*   **Fixation** : 4 vis M3 traversantes vers des inserts dans la coque de tête.
*   **Orientation** : Câble vers l'arrière pour ne pas gêner la caméra OAK-D Pro (placée en frontal).
