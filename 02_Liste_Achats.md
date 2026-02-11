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

## 2. Moteurs & Actionneurs (Par Phase)

### Phase 1 : Tête / Torse (Aucun Moteur)
*   Focus uniquement sur les capteurs et l'intelligence.

### Phase 2 : Premier Bras (6 DOF)
| Modèle | Quantité | Couple (Peak) | Usage |
| :--- | :--- | :--- | :--- |
| **Robstride 03** | 2 | 35 Nm | Épaule (Force brute - Pitch/Roll) |
| **Robstride 02** | 3 | 24.8 Nm | Biceps / Coude / Avant-bras |
| **Robstride 00** | 1 | - | Poignet / Effecteur Final (Rotation) |

*(Note: Le RS05 initialement prévu pour le cou est reporté ou intégré différemment selon le design final de la tête)*.

### Autres Composants Électroniques
| Composant | Modèle | Quantité | Note |
| :--- | :--- | :--- | :--- |
| **Robstride 04** | - | Hanches / Torse Pivot (Marche) | - |
| Distribution (PDB) | **Matek PDB-HEX** (Master) + **PDB-XT60-W** (Satellites) | 2 + 4 | Hubs de puissance pro |
| Connectique Data | **JST-GH 4-pin** (Silicone / Holybro) | 30m | Fils torsadés blindés |
| Maintenance Tête | **WAGO 221-413 / 415** | 10 | Connecteurs rapides sans soudure |
| Alimentation Labo | **Wanptek DPS605U** (60V/5A) | 1 | Réglage précis 24V/48V + OCP |
| Interface CAN | **InnoMaker USB2CAN-C** | 1 | Natif Linux (SocketCAN) |

> **Note** : Vérifiez bien que les moteurs arrivent avec leurs câbles d'alimentation (XT60) et data (JST-GH). Sinon, commander séparément.

---

## 3. Électronique & Cerveau (Détail Phase 1 & 2)

| Composant | Modèle | Note |
| :--- | :--- | :--- |
| **Cerveau IA** | NVIDIA Jetson Orin Nano (8GB) | Le modèle Super est un plus, mais le 8GB suffit. |
| **Vision (Tête)** | Luxonis OAK-D Pro | Version Fixed-Focus (FF) recommandée (vibrations). |
### Électronique de Contrôle
- **Sony Spresense** :
    - *Main Board* + *Extension Board* (Standard).
    - **Note sémantique** : L'Extension Board Standard est préférée pour ses 8 entrées micro (vs 4 sur la version LTE).
    - **Connectivité** : Pour la LTE, utilisez un shield tiers (Waveshare SIM7600) via UART pour conserver les 8 micros.
- **Audio** : 8x Microphones numériques MEMS (PDM) + câbles blindés.
| **LiDAR** | **Unitree L2** | FOV 360°x90°, Portée 30m, IMU intégrée. |
| **Alimentation Labo** | **Wanptek DPS605U** | Indispensable Phase 2 (Régler sur 24V / Lim. 1A). |

### Interface CAN & Câbles
*   **Adaptateur USB-CAN** : **InnoMaker USB2CAN-C**
    *   *Critique* : Basé sur firmware `gs_usb` (compatible Linux natif).
*   **Connecteurs Data** : **JST-GH 1.25mm** (Marque Holybro recommandée pour la qualité).
    *   Acheter des câbles "tout faits" si possible pour éviter de sertir du 1.25mm.
*   **Connecteurs Puissance** : **XT60** (Jaune).
*   **Câble Bus CAN** : Utiliser impérativement des **paires torsadées** pour CAN_H / CAN_L.

---

## 4. Infrastructure & Connexion
| Composant | Modèle | Usage |
| :--- | :--- | :--- |
| **WiFi Imprimante** | **TP-Link Archer T3U** | AC1300 Mbps, USB 3.0. Connectivité stable pour Qidi Plus 4. |

---

## 5. Consommables & Outils
*   **Frein Filet** : **Loctite 222** (Faible/Moyen). Indispensable ! Les vibrations des moteurs Robstride desserrent les vis M3 en quelques heures sans cela.
*   **Clés Allen** : Jeu de clés de précision (Facom ou Wera) pour ne pas foire les têtes de vis.
