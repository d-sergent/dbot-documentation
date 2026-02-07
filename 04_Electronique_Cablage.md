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

### Câbles (Règles d'Or)
1.  **Torsades** : Les fils CAN_H et CAN_L *doivent* être torsadés ensemble sur toute la longueur. Ne jamais les laisser parallèles et séparés.
2.  **Séparation** : Éloignez les câbles CAN (Data) des câbles d'alimentation Moteur (Puissance) d'au moins 2-3 cm pour éviter les parasites EMI lors des pics de couple.
3.  **Terminaison** : Le dernier moteur de la chaîne doit avoir une résistance de terminaison de 120 Ohms activée (souvent via un DIP switch sur le moteur ou un bouchon externe).

___

## 3. Sony Spresense & OAK-D Pro

### OAK-D Pro (Vision)
*   Agit comme un capteur USB3.
*   Intègre une **IMU (BNO085/BMI270)**.
*   Le flux vidéo et les données IMU remontent à la Jetson via USB.
*   *Note* : L'IMU embarquée est suffisante pour la stabilisation de base (équivalent Option A).

### Sony Spresense (Audio & I/O)
*   **Carte Extension Choisie** : **Standard Board** (CXD5602PWBEXT1).
    *   *Raison* : Permet de brancher jusqu'à **8 microphones numériques** pour le Beamforming (localisation de la voix).
    *   *Évolutivité* : Headers Arduino compatibles pour ajouter des shields futurs.
*   **Alternative LTE** : Si le robot doit sortir en extérieur (hors Wi-Fi), une **LTE Extension Board** aurait été préférée, mais la Standard offre plus de flexibilité I/O audio pour un robot social.
*   **Liaison Jetson** : Via USB (Port principal micro-USB de la Spresense). La Spresense apparaît comme un périphérique série (`/dev/ttyUSBx`) ou Audio USB selon le sketch chargé.

---

## 4. Alimentation (Power Distribution)
*   **Batterie** : LiPo 6S ou alimentation stabilisée 24V (selon moteurs).
*   **Connecteurs** :
    *   **XT60 (Jaune)** : Pour la ligne principale de puissance. Indestructible.
    *   **Distribution** : Utiliser un **PDB (Power Distribution Board)** de drone pour éclater le 24V vers chaque moteur.
*   **Sécurité** :
    *   Fusible automobile sur la ligne principale.
    *   Bouton d'arrêt d'urgence (E-Stop) coupant l'alim moteurs mais *pas* la Jetson.
