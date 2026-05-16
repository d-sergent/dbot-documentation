# FINAL - Câblage des Solénoïdes (Blocage Tête)

Le blocage de la tête (Tilt) est assuré par deux solénoïdes **LEX-SOLEN-04** (12V, 0.6A chacun). Ils fonctionnent en mode **"Power to Unlock"** (alimentés pour débloquer).

## 1. Composants Requis
*   **Module de commande MOSFET** : Dual MOSFET D4184 (compatible logique 3.3V).
*   **Inductive Protection** : 2x Diodes **1N4007** (roue libre).
*   **Alimentation** : Rail 12V Logique.
*   **Commande** : Jetson Orin Nano (GPIO).

## 2. Schéma de Câblage

```text
                                 +---------------------------+
[Rail 12V Logique]               |                           |
   (+) 12V -------------------> | VIN+                      |
   (-) GND -------------------> | VIN-     MODULE D4184     |
                                 |                           |
[Jetson Orin Nano]              |                           |
   Pin GPIO (ex: Pin 32) -----> | PWM (Signal)              |
   Masse (GND) ---------------> | GND (Masse)               |
                                 +---------------------------+
                                   | OUT+            | OUT-
                                   |                 |
                                   +-------+---------+
                                   |       |         |
                                 [Diode 1N4007]      |
                                 (Anneau gris vers OUT+)
                                   |       |         |
                                   |  [Solénoïde 1]  |
                                   |                 |
                                   +-------+---------+
                                   |       |         |
                                 [Diode 1N4007]      |
                                 (Anneau gris vers OUT+)
                                   |       |         |
                                   |  [Solénoïde 2]  |
                                   |                 |
                                   +-----------------+
```

## 3. Sécurité Critique
> [!DANGER]
> **Diode de Roue Libre Obligatoire** : Les solénoïdes sont des charges inductives massives. À la coupure du courant, ils génèrent un pic de tension inverse qui peut détruire le MOSFET et remonter jusqu'à la Jetson. La diode 1N4007 doit être placée en parallèle (en inverse) de chaque solénoïde.

## 4. Logique de Contrôle
*   **Signal HIGH** : Libération des freins (mouvement possible).
*   **Signal LOW / Coupure** : Verrouillage mécanique par ressort (sécurité en cas de panne).
*   **Mode** : Les deux solénoïdes sont branchés en parallèle sur une seule sortie pour une synchronisation parfaite.
