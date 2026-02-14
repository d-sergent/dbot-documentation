# 11 - Guide IMU & Watchdog (Sécurité & Équilibre)

Ce guide détaille l'intégration de l'**IMU torse** (BMI270 Add-on Board) et la mise en place de l'architecture de **Sécurité Active** (Watchdog + Power Management) pilotée par la Sony Spresense.

> [!WARNING]
> **Migration SensiEDGE → BMI270** : La carte SensiEDGE CommonSense initialement prévue **n'est pas disponible au grand public** (réservée aux professionnels). Ce guide a été mis à jour pour utiliser le **BMI270 Add-on Board** (Switch Science) comme IMU principale.

## 1. Matériel : IMU Torse

### Option Recommandée : BMI270 Add-on Board (Switch Science)
*   **Connexion** : S'enfiche sur les headers I2C/SPI de la **Spresense Extension Board**.
*   **Capteur** : **Bosch BMI270** — Accéléromètre + Gyroscope 6 axes.
*   **Fréquence** : Jusqu'à **416 Hz** (accéléromètre) / **6.4 kHz** (gyroscope).
*   **Rôle primaire** : **IMU d'équilibre** du robot — contrôle du centre de masse en temps réel.
*   **Rôle secondaire** : Détection de chute quand la Jetson est éteinte (Watchdog).
*   **Bibliothèque Arduino** : `Arduino_BMI270_BMM150` ou `BMI270-Sensor-API`.

### Alternative Haute Précision : Sony Spresense Multi-IMU Add-on Board
*   **Sortie** : Février 2025.
*   **Principe** : 16 MEMS IMUs fusionnées pour une précision comparable aux **gyroscopes à fibre optique (FOG)**.
*   **Quand l'utiliser** : Si la marche dynamique sur terrain complexe nécessite une précision angulaire extrême.
*   **Interface** : SPI.

### ~~SensiEDGE CommonSense~~ (Indisponible)
*   ⚠️ **Non disponible au grand public** — réservée aux clients professionnels.
*   Contenait : IMU (LSM6DSOX), Magnétomètre (LIS2MDL), Temp/Humidité (HTS221), Pression (LPS22HH), Qualité d'air (SGP40).
*   Les capteurs environnementaux ne sont **pas critiques** pour le prototype V1. Si nécessaire, ajouter des thermistances ($1) sur les moteurs RS-04.

### Montage Mécanique
L'empilement (Stack) se fait verticalement dans le torse :
1.  **Base** : Spresense Extension Board (Arduino form factor).
2.  **Milieu** : Spresense Main Board.
3.  **Haut** : **BMI270 Add-on Board** (se connecte sur les headers I2C/SPI).

---

## 2. Architecture "Power Manager" (Veille & Réveil)
La Spresense est le seul composant "Always-On" du robot. Elle contrôle l'alimentation de puissance (44V) via un **MOSFET**.

### Schéma de Câblage (Protection 12S)
*   **Entrée Batterie** : 12S LiPo (44.4V Nominal / 50.4V Max).
*   **Pont Diviseur (Surveillance Tension)** :
    *   Connecté à la **Pin A0** de la Spresense.
    *   **R1** (Côté Batterie) : **150 kΩ**
    *   **R2** (Côté Masse) : **10 kΩ**
    *   *Ratio* : 50V en entrée donne ~3.12V en lecture (Compatible 3.3V).
*   **Commande Puissance (MOSFET)** :
    *   Connecté à la **Pin D13**.
    *   Composant recommandé : **Infineon BTS50085** (Smart High-Side Switch) ou Module MOSFET 100V opto-isolé.
    *   Rôle : Coupe physiquement l'alimentation de la Jetson et des Moteurs RobStride.
*   **Heartbeat (Watchdog)** :
    *   Connecté à la **Pin D12**.
    *   Signal : La Jetson envoie une impulsion "Vivant" toutes les 100ms.

---

## 3. Code Spresense (C++)
Voici le code complet pour gérer la sécurité, la batterie et le réveil.

### Gestionnaire d'Alimentation & Watchdog
Ce code surveille la batterie (protection décharge profonde) et la Jetson (anti-freeze).

```cpp
/*
 * D-Bot Power Manager & Watchdog
 * Matériel : Sony Spresense + BMI270 Add-on (IMU Équilibre)
 */

#include <RTC.h> // Pour la gestion du temps

const int PIN_MOSFET = 13;    // Commande du Relais/MOSFET Puissance
const int PIN_HEARTBEAT = 12; // Entrée signal vie Jetson
const int PIN_WAKEUP = 11;    // Bouton de Test (ou Trigger Vocal)
const int PIN_BATTERY = A0;   // Pont diviseur

// Paramètres Batterie 12S (Sécurité)
const float R1 = 150000.0; 
const float R2 = 10000.0;
const float VOLTAGE_THRESHOLD = 37.0; // Seuil critique (3.08V / cellule)

// Paramètres Watchdog
unsigned long lastHeartbeat = 0;
const unsigned long WATCHDOG_TIMEOUT = 5000; // 5 secondes sans signal = Crash
bool isRobotAwake = false;

// Lecture sécurisée de la tension batterie
float readBatteryVoltage() {
  int raw = analogRead(PIN_BATTERY);
  // Conversion ADC (Ref 3.3V ou 5V selon jumper Extension Board)
  float vOut = (raw * 5.0) / 1023.0; // Assumes 5V ref on Extension Board ADC
  float vBat = vOut * ((R1 + R2) / R2);
  return vBat;
}

void setup() {
  pinMode(PIN_MOSFET, OUTPUT);
  pinMode(PIN_HEARTBEAT, INPUT);
  pinMode(PIN_WAKEUP, INPUT_PULLUP);
  
  digitalWrite(PIN_MOSFET, LOW); // Sécurité : Tout éteint au démarrage
  Serial.begin(115200);
  Serial.println("--- D-Bot Security Sentinel Started ---");
}

void loop() {
  // 1. Surveillance Batterie (Priorité Absolue)
  float voltage = readBatteryVoltage();
  if (voltage < VOLTAGE_THRESHOLD && voltage > 5.0) { // >5V pour éviter faux positif si pas branché
    Serial.print("CRITIQUE : Batterie faible (");
    Serial.print(voltage);
    Serial.println("V). Arrêt d'urgence.");
    emergencyShutdown();
    return; // On ne fait rien d'autre
  }

  // 2. Gestion du Réveil (Si éteint)
  if (!isRobotAwake) {
    if (digitalRead(PIN_WAKEUP) == LOW) { // Ou détection vocale
       if (voltage > VOLTAGE_THRESHOLD) {
          wakeupRobot();
       } else {
          Serial.println("Refus d'allumage : Batterie trop faible.");
       }
    }
  }

  // 3. Watchdog (Si allumé)
  if (isRobotAwake) {
    if (digitalRead(PIN_HEARTBEAT) == HIGH) {
      lastHeartbeat = millis();
    }
    
    if (millis() - lastHeartbeat > WATCHDOG_TIMEOUT) {
      Serial.println("ALERTE : Perte signal Jetson (Freeze). Reboot...");
      emergencyShutdown();
      // Optionnel : Tentative de redémarrage après 5s
    }
  }
  
  delay(100);
}

void wakeupRobot() {
  Serial.println("Réveil du D-Bot...");
  digitalWrite(PIN_MOSFET, HIGH);
  isRobotAwake = true;
  lastHeartbeat = millis(); 
  delay(2000); // Laisser le temps à l'alim de se stabiliser
}

void emergencyShutdown() {
  digitalWrite(PIN_MOSFET, LOW);
  isRobotAwake = false;
  Serial.println("Système mis en sécurité.");
}
```

### Intégration des Capteurs SensiEDGE
Pour lire l'IMU BMI270 (remplacement de la SensiEDGE), utilisez :
- **IMU** : `Arduino_BMI270_BMM150` (Bosch officiel) ou `BMI270-Sensor-API`

Si des capteurs environnementaux sont ajoutés ultérieurement :
- **Température** : Thermistance NTC sur ADC Spresense
- **Note** : Les bibliothèques SensiEDGE (`Arduino_LSM6DSOX`, `Arduino_HTS221`, etc.) ne sont plus nécessaires.

*Note : Le BMI270 Add-on utilise le bus I2C ou SPI standard. Aucune électronique additionnelle n'est requise.*
