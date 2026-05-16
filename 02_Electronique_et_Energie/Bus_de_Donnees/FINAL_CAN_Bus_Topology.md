# FINAL - Topologie du Bus CAN (Moteurs RobStride)

Le bus CAN est la colonne vertébrale du robot. Cette fiche définit l'adressage, la segmentation et le matériel de communication.

## 1. Principe du Bus CAN
*   **Protocole** : CAN (Controller Area Network).
*   **Vitesse** : 1 Mbps.
*   **Signaux** : CAN_H, CAN_L, GND (indispensable).
*   **Terminaison** : Résistance 120 Ω sur le dernier moteur de chaque chaîne daisy-chain.
*   **Exception** : Pas de terminaison nécessaire pour le bus du cou (RS-05) si câbles < 30cm.

## 2. Segmentation des Bus (Bande passante)
La boucle de contrôle cible est de **1 kHz**. Pour éviter la saturation à 1 Mbps, le robot est divisé en 5 bus indépendants.

| Bus CAN | Moteurs | Nb | Adaptateur |
| :--- | :--- | :---: | :--- |
| **Bus Cou** | RS-05 Pan + RS-05 Tilt | 2 | InnoMaker USB2CAN-C (Jetson Direct) |
| **Bus Bras G** | 6 moteurs RS | 6 | CANable Pro n°1 (via Hub) |
| **Bus Bras D** | 6 moteurs RS | 6 | CANable Pro n°2 (via Hub) |
| **Bus Jambe G** | 6 moteurs RS | 6 | CANable Pro n°3 (via Hub) |
| **Bus Jambe D** | 6 moteurs RS | 6 | CANable Pro n°4 (via Hub) |

## 3. Matériel et Architecture USB
Pour garantir l'isolation et la compacité :
*   **InnoMaker USB2CAN-C** : Utilisé pour le cou (liaison directe Jetson).
*   **CANable Pro (Firmware candleLight)** : Utilisé pour les membres. Isolation galvanique 2.5kV obligatoire.
*   **Hub USB Industriel** : Centralise les 4 CANable + U2D2 + Spresense dans le torse.

```text
Jetson Orin Nano
    ├── Port 4 (Direct) : InnoMaker USB2CAN-C → Bus Cou (RS-05 ×2)
    └── Port 2 (Hub Industriel Alimenté)
         ├── CANable Pro n°1 → Bus Bras G (6 moteurs)
         ├── CANable Pro n°2 → Bus Bras D (6 moteurs)
         ├── CANable Pro n°3 → Bus Jambe G (6 moteurs)
         ├── CANable Pro n°4 → Bus Jambe D (6 moteurs)
         ├── Sony Spresense → Watchdog / Capteurs
         ├── U2D2 n°1 (Main G) → Dynamixel TTL
         └── U2D2 n°2 (Main D) → Dynamixel TTL
```

## 4. Câblage et Couleurs
*   **Daisy-Chain** : Interdiction de faire des "Y" (étoiles). Les stubs doivent être < 30 cm.
*   **Couleurs fils RobStride** :
    *   **CAN_H** : Jaune
    *   **CAN_L** : Blanc
    *   **GND** : Noir
*   **Masse commune** : Le fil GND CAN doit relier l'adaptateur CAN à la borne (-) du busbar.
