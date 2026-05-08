# Synthèse : Électronique & Câblage - État de l'Art

Ce document résume la configuration finale et aboutie de l'infrastructure électrique du D-Bot.

## 1. Alimentation (Haute Puissance)
- **Batterie Principale** : **13S NMC (48V nominal)** — Type AT WEY 10Ah (Cellules LG M50LT).
- **Extensibilité** : Passage de 1 pack (Centré) à 2 packs (Parallèle via ORing MOSFET) en Phase 4.
- **Sécurité** : 
  - Fusible 80A Automobile.
  - Coupure de puissance par MOSFET piloté par la Spresense (Watchdog).
  - Connecteur principal : **Anderson SB50**.

## 2. Distribution (PDB)
- **Carte** : **Matek PDB-HEX** pour gérer les forts courants du bus 48V.
- **Topologie de Puissance** : **ÉTOILE impérative**. Aucun chaînage de puissance sur les XT30 des moteurs (risque de fonte immédiate).
- **Régulation** : DC-DC 48V → 19V (Jetson) et 48V → 5V (Spresense).


## 4. Capteurs & Temps Réel
- **FSR (Pieds)** : 4 capteurs par pied, pont diviseur 10kΩ.
- **Lecture ADC** : Spresense (A0-A3) à haute fréquence pour le Centre de Pression (CoP).
- **IMU** : BMI270 (Torse) à 416 Hz via SPI/I2C sur Spresense.

## 5. Liens et Archives
- **Guide Électronique Complet** : [04_Electronique_Cablage.md](../04_Electronique_Cablage.md)
- **Guide Watchdog & Spresense** : [11_Guide_SensiEDGE_Watchdog.md](../11_Guide_SensiEDGE_Watchdog.md)
- **Archives** : 
  - [Archives/ETUDE_Batterie_LiFePO4.md](../Archives/ETUDE_Batterie_LiFePO4.md) (Rejetée pour cause de masse excessive)
  - [Archives/ETUDE_Cablage_DaisyChain_Power.md](../Archives/ETUDE_Cablage_DaisyChain_Power.md) (L'erreur technique à ne pas reproduire)
