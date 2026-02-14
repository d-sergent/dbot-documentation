# Électronique & Câblage

## 1. Schéma Global de Connexion
L'architecture repose sur un bus CAN centralisé et des liaisons USB High-Speed.

### Cerveau Principal (NVIDIA Jetson Orin Nano)
*   **Alimentation** : 19V DC (via Jack ou XT60 régulé).
*   **Rôle** : Orchestrateur ROS2, Vision IA, Planification de mouvement.
*   **Ports** :
    *   **USB A** -> **InnoMaker USB2CAN** (Contrôle Moteurs)
    *   **USB C** -> **OAK-D Pro** (Vision Stéréo + IA)
    *   **USB A** -> **Sony Spresense** (Audio / Capteurs TR)

---

## 2. Bus CAN (Moteurs Robstride)
C'est la colonne vertébrale du robot. Une erreur ici rend le robot inerte.

### Adaptateur : InnoMaker USB2CAN-C
*   **Firmware** : `gs_usb` (Natif Linux).
*   **Configuration Switch** : Mettre le switch **120 \Omega** sur **ON** (si l'adaptateur est en début de chaîne).
*   **Câblage Bornier** :
    *   **CAN_H** -> Fil Vert (souvent) du moteur.
    *   **CAN_L** -> Fil Jaune (souvent) du moteur.
    *   **GND** -> **CRITIQUE**. Relier la masse de l'USB2CAN à la masse commune des moteurs (Batterie -). Sans ça, le signal flotte et crée des erreurs "Bus Off".

### Bus de Communication (CAN 1 Mbps)
Le Bus CAN est le système nerveux du D-Bot. Une erreur de câblage ici rend le robot incontrôlable.

#### Règle d'or du Câblage 3 fils
Bien que différentiel, le CAN exige une référence commune :
1.  **CAN_H** (Jaune)
2.  **CAN_L** (Blanc)
3.  **GND** (Noir) : **CRITIQUE.** Doit relier la borne GND de l'InnoMaker à la masse des moteurs.
*Note : Le fil rouge (VCC 5V) du Hub Holybro ne doit JAMAIS être connecté aux moteurs alimentés en 48V.*

#### Architecture Daisy Chain
- **Stubs** : Les dérivations vers les moteurs doivent mesurer moins de **30 cm**.
- **Terminaison** : Une résistance de **120 Ω** doit être placée à chaque extrémité (Jetson et dernier moteur).
- **Torsion** : Torsader les fils (33 tours/mètre) pour annuler les EMI.

___

## 3. Sony Spresense & OAK-D Pro

### OAK-D Pro (Vision)
*   Agit comme un capteur USB3.
*   Intègre une **IMU (BNO085/BMI270)** — **utilisée uniquement pour la stabilisation du regard**, pas pour l'équilibre du corps (voir [Stratégie IMU](./08_Audio_Perception.md)).

### Sony Spresense (Audio & I/O)
*   **Carte Extension Choisie** : **Standard Board** (CXD5602PWBEXT1).
    *   *Raison* : Permet de brancher jusqu'à **8 microphones numériques** pour le Beamforming (localisation de la voix).
    *   *Évolutabilité* : Headers Arduino compatibles pour ajouter des shields futurs.
*   **Alternative LTE** : Si le robot doit sortir en extérieur (hors Wi-Fi), une **LTE Extension Board** aurait été préférée, mais la Standard offre plus de flexibilité I/O audio pour un robot social.
*   **Liaison Jetson** : Via USB (Port principal micro-USB de la Spresense). La Spresense apparaît comme un périphérique série (`/dev/ttyUSBx`) ou Audio USB selon le sketch chargé.

---

### Mise sous tension (Sécurité Wanptek)
Pour les premiers tests moteurs (Banc d'essai) :
1.  Régler la tension à **24.0V** (ou 48V) à vide.
2.  Régler la limite de courant à **1.000A** (en court-circuitant les pinces).
3.  Activer le mode **OCP** (Overcurrent Protection).
4.  Séquence : Allumer l'alim -> Vérifier tension -> Brancher XT60 -> `Enable` logiciel.

## 4. Alimentation (Power Distribution)
*   **Batterie** : LiPo 6S ou alimentation stabilisée 24V (selon moteurs).
*   **Connecteurs** :
    *   **XT60 (Jaune)** : Pour la ligne principale de puissance. Indestructible.
    *   **Distribution** : Utiliser un **PDB (Power Distribution Board)** de drone pour éclater le 24V vers chaque moteur.
*   **Sécurité** :
    *   Fusible automobile sur la ligne principale.
    *   Bouton d'arrêt d'urgence (E-Stop) coupant l'alim moteurs mais *pas* la Jetson.
