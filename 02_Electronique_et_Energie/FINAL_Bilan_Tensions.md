# FINAL - Bilan des Tensions et Rails de Puissance

L'architecture électrique du D-Bot repose sur une source principale 48V (Batterie 13S) et quatre rails de tensions secondaires régulés.

## 1. Inventaire des Rails de Tension

| Rail | Composant Principal | Tension | Intensité Max | Source |
| :--- | :--- | :---: | :---: | :--- |
| **48V Raw** | 26x Moteurs RobStride | 46.8V nom. | 80A Peak | Batterie Directe / E-Stop |
| **19V IA** | Jetson Orin Nano Super | 19.0V | 5A (95W) | Buck 48V→19V |
| **12V Logic**| Hub USB, Solénoïdes | 12.0V | 10A (120W) | Buck 48V→12V (Logic) |
| **12V Power**| 16x Servomoteurs Feetech (Mains) | 12.0V | 20A (240W) | Buck 48V→12V (Power) |
| **5V Always**| Spresense, Capteurs | 5.0V | 5A (25W) | Buck 48V→5V |

## 2. Détails par Rail

### Rail 19V : Calculateur IA
*   **Composant** : NVIDIA Jetson Orin Nano Super.
*   **Intensité** : ~5.0 A Peak (inclut l'alimentation des périphériques USB : OAK-D Pro, ReSpeaker, HP).
*   **Source** : Buck DC-DC 48V→19V (95W).

### Rail 12V Logique (10A)
*   **Usage** : Hub USB Industriel (60W), Solénoïdes de tête (2A), accessoires torse.
*   **Source** : Buck DC-DC 60V In / 12V 10A Out (type Mean Well DDR-120C-12 ou Homelylife).
*   **Raison** : Ce rail reste "propre" (sans parasites moteurs) pour garantir la stabilité des connexions USB.

### Rail 12V Puissance (20A)
*   **Usage** : 16× servomoteurs Feetech des mains (STS3250/HL-3915).
*   **Intensité** : ~18.2 A Peak total (estimé à 20A max sous charge).
*   **Source** : Buck DC-DC 60V In / 12V 20A Out (ou DROK 25A par bras).
*   **Raison** : Supporte les appels de courant massifs lors des saisies d'objets sans faire chuter la tension de la Jetson.

### Rail 5V : Logique Always-On & Capteurs
*   **Sony Spresense** : Watchdog et Power Management. **~1.0 A**.
*   **Accessoires USB** : ReSpeaker, OAK-D Pro (via Jetson), Hub USB.
*   **Source** : Buck DC-DC 48V→5V 5A (Always-On).

### Rail 3.3V : Capteurs Fins & Tactile
*   **Capteurs eFlesh (Mains)** : 9 à 16 magnétomètres MLX90393 par main.
*   **IMU Torse** : BMI270 (équilibre).
*   **Source** : 
    *   **Pour le torse** : Régulation 3.3V interne de la Spresense.
    *   **Pour les mains (eFlesh)** : **Micro-Hub USB local (type ESP32-S3)**. Il puise son énergie dans le **5V du bus USB** (Hub Industriel) et régule lui-même le 3.3V pour ses 16 capteurs MLX90393. Aucune alimentation externe 12V ou 48V n'est nécessaire pour le tactile.
    *   **Pour les pieds (FSR)** : **Régulateur local (5V → 3.3V)** situé dans la **cheville ou le pied**, repiquant le **5V Always-On** du Buck Logique.
