# 11 - Guide SensiEDGE & Watchdog (Sécurité & Environnement)

Ce guide détaille l'intégration de la carte **SensiEDGE CommonSense** et la mise en place de l'architecture de **Sécurité Active** (Watchdog + Power Management) pilotée par la Sony Spresense.

## 1. Matériel : SensiEDGE CommonSense
Cette carte "Tout-en-un" transforme la Spresense en une boîte noire environnementale et inertielle indépendante de la Jetson.

### Spécifications Techniques
*   **Connexion** : S'enfiche sur le port I2C/UART de la **Spresense Extension Board**.
*   **Capteurs Critiques** :
    *   **IMU 6-Axes (LSM6DSOX)** : Accéléromètre + Gyroscope. Sert de "Sens de l'équilibre" de secours pour détecter une chute quand la Jetson est éteinte.
    *   **Magnétomètre (LIS2MDL)** : Boussole numérique.
    *   **Environnement** : Température/Humidité (HTS221) et Pression (LPS22HH). Indispensable pour surveiller la température interne du torse (Moteurs + Jetson).
    *   **Qualité d'Air (SGP40)** : Détection de VOC (Composés Organiques Volatils). Utile pour détecter une surchauffe de gaine ou un début d'incendie électrique.
    *   **Lumière/Proximité** : Capteur de lumière ambiante.

### Montage Mécanique
L'empilement (Stack) se fait verticalement dans le torse :
1.  **Base** : Spresense Extension Board (Arduino form factor).
2.  **Milieu** : Spresense Main Board.
3.  **Haut** : SensiEDGE CommonSense (se connecte sur les headers).

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
 * K-Bot Power Manager & Watchdog
 * Matériel : Sony Spresense + SensiEDGE (IMU)
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
  Serial.println("--- K-Bot Security Sentinel Started ---");
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
  Serial.println("Réveil du K-Bot...");
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
Pour lire les capteurs environnementaux (Air Quality, Temp), utilisez les bibliothèques Arduino standard compatibles :
- **IMU** : `Arduino_LSM6DSOX`
- **Temp/Hum** : `Arduino_HTS221`
- **Pression** : `Arduino_LPS22HH`
- **Gaz** : `Sensirion I2C SGP40`

*Note : La carte CommonSense utilise le bus I2C standard. Aucune électronique additionnelle n'est requise.*
