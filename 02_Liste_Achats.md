# Liste des Achats (BOM Consolidée)

## 1. Visserie & Fixations (Hardware)
**Stratégie** : Utilisation de vis **DIN 912 (Tête Cylindrique)** en Acier Inoxydable A2 (Inox 304) pour la résistance à la corrosion, ou Acier Noir 12.9 pour les axes moteurs de force.

### Quantités Requises (D-Bot + 2x RS05)
| Type | Diamètre | Longueur | Quantité Est. | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Vis CHC** | M3 | 6mm - 12mm | ~240 | Fixations électroniques, caches, small motors |
| **Vis CHC** | M4 | 10mm - 15mm | ~160 | Structure principale, moteurs RS01-RS04 |
| **Vis CHC** | M5 | 12mm - 20mm | ~40 | Hanches, Grosses articulations |
| **Écrous/Rondelles** | M3/M4/M5 | - | ~150 de chaque | - |

### Liens d'Achat Recommandés
*   **Protorx (France)** : [Lien vers Boîtes M3/M4 Inox](https://www.protorx.com) - *Idéal pour un stock propre*.
*   **Vis-Express** : [Lien vers M4 DIN 912 Inox A2](https://www.vis-express.fr) - *Livraison rapide*.
*   **ScrewsAndMore** : [Lien vers Assortiment 400pcs](https://www.screwsandmore.de) - *Rapport quantité/prix*.

> **Conseil** : Achetez un kit "Build Complet" (1225pcs M2-M5) pour avoir du stock, et complétez avec des sachets de 50 vis M4 Acier 12.9 pour les moteurs.

### Inserts Filetés (Heat-set)
*   **Marque Recommandée** : **Ruthex** (ou CNC Kitchen).
*   **Modèle** : RX-M3x5.7 (M3) et versions "Longues" pour M4.
*   **Pourquoi ?** Les moletages opposés offrent la meilleure résistance à l'arrachement dans le PETG-CF.
*   **Acheter chez** : [3DJake France](https://www.3djake.fr) ou Amazon.

---

## 2. Moteurs & Actionneurs
### Moteurs Intelligents (Robstride)
| Modèle | Quantité | Couple (Peak) | Usage |
| :--- | :--- | :--- | :--- |
| **Robstride 05** | 2 | 5.5 Nm | Cou, Poignets (Nouveaux ajouts) |
| **Robstride 01** | - | 17 Nm | Coude / Épaule (Léger) |
| **Robstride 02** | - | 24.8 Nm | Épaule / Torse |
| **Robstride 03** | - | 35 Nm | Épaule (Force) |
| **Robstride 04** | - | 60 Nm | Hanches / Torse Pivot |

> **Note** : Vérifiez bien que les moteurs arrivent avec leurs câbles d'alimentation (XT60) et data (JST-GH). Sinon, commander séparément.

---

## 3. Électronique & Câblage
### Cerveau & Perception
*   **NVIDIA Jetson Orin Nano** (Developer Kit)
*   **Sony Spresense** :
    *   Main Board (CXD5602PWBMAIN1)
    *   **Extension Board (Recommandé : Standard)** pour l'audio et l'évolutivité. *(La version LTE est une alternative si usage outdoor sans Wi-Fi)*.
*   **OAK-D Pro** (Luxonis) : Caméra IA Stéréo (avec IMU BNO085/BMI270 intégrée).
*   **LiDAR Unitree L2** : Pour la navigation SLAM.

### Interface CAN & Câbles
*   **Adaptateur USB-CAN** : **InnoMaker USB2CAN-C**
    *   *Critique* : Basé sur firmware `gs_usb` (compatible Linux natif).
    *   [Lien InnoMaker](http://www.innomaker.com)
*   **Connecteurs Data** : **JST-GH 1.25mm** (Marque Holybro recommandée pour la qualité).
    *   Acheter des câbles "tout faits" si possible pour éviter de sertir du 1.25mm.
*   **Connecteurs Puissance** : **XT60** (Jaune).
*   **Câble Bus CAN** : Utiliser impérativement des **paires torsadées** pour CAN_H / CAN_L.

---

## 4. Consommables & Outils
*   **Frein Filet** : **Loctite 222** (Faible/Moyen). Indispensable ! Les vibrations des moteurs Robstride desserrent les vis M3 en quelques heures sans cela.
*   **Clés Allen** : Jeu de clés de précision (Facom ou Wera) pour ne pas foire les têtes de vis.
