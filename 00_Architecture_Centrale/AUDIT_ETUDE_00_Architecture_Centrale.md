# 🔍 Rapport d'Audit d'Ingénierie : 00 Architecture Centrale (D-Bot)

En tant qu'Ingénieur Senior en Revue de Conception, j'ai procédé à un audit approfondi du module **00 Architecture Centrale** du projet D-Bot, en me basant sur les documents d'études et de synthèse du sous-dossier (`FINAL_CONSOLIDE_00_Architecture_Centrale.md`, `FINAL_Architecture_Globale.md`, `STUDY_Architecture_DOF_Benchmark.md`, `BENCHMARK_K-Bot_K-Scale.md`).

Mon objectif est de fournir une évaluation synthétique, critique et vérifiée des choix d'architecture globale du robot D-Bot.

---

## 0. Décisions d'Architecture Retenues

| Choix Architectural | Spécification Technique | Justification & Impact D-Bot |
| :--- | :--- | :--- |
| **Masse Totale Cible** | **40.4 kg** (buste ~18 kg, jambes ~18 kg, tête/cou/divers ~4.4 kg) | Ratio puissance/masse optimal pour la marche dynamique et le portage de charge. |
| **Taille / Degrés de Liberté** | **1.35 m / 26 DOF actifs** | Répartition : Cou (2), Épaules (6), Coude/Poignet (6), Hanches/Genoux/Chevilles (12). |
| **Actionneurs Principaux** | **RobStride QDD (RS-04, RS-03, RS-06, RS-05, RS-02, RS-00)** | Technologie Quasi-Direct Drive (QDD) à backdrivabilité et bande passante élevées. |
| **Alimentation & Bus Power** | **Batterie 12S LiFePO4 / NMC (48V nominal, 480–576 Wh)** | Bus continu 48V distribué vers tous les moteurs QDD et régulation 19V/5V embarquée. |
| **Communication Bus** | **CAN-FD découpé en bus sectorisés** | Fréquence de rafraîchissement >= 1 kHz pour les boucles de contrôle temps réel. |
| **Squelette & Fabrication** | **Monocoque Hybride (PA12-CF + Squelette Alu 6061-T6/Fibre Carbone)** | Allie légèreté de l'impression 3D FDM et rigidité métallique usinée sur CNC C500. |

---

## 1. Synthèse des Degrés de Liberté (26 DOF)

```
                       [Tête / Cou] (2 DOF)
                       RS-05 Yaw / RS-05 Pitch
                                │
          ┌─────────────────────┴─────────────────────┐
   [Bras Gauche] (6 DOF)                       [Bras Droit] (6 DOF)
   - Épaule Pitch (RS-04)                      - Épaule Pitch (RS-04)
   - Épaule Roll (RS-03)                       - Épaule Roll (RS-03)
   - Épaule Yaw (RS-02)                        - Épaule Yaw (RS-02)
   - Coude Flexion (RS-06)                     - Coude Flexion (RS-06)
   - Poignet Yaw (RS-02)                       - Poignet Yaw (RS-02)
   - Poignet Pitch (RS-00)                     - Poignet Pitch (RS-00)
                                │
                          [Taille / Waist]
                        Waist Yaw (RS-06)
                                │
          ┌─────────────────────┴─────────────────────┐
   [Jambe Gauche] (6 DOF)                      [Jambe Droite] (6 DOF)
   - Hanche Pitch (RS-04)                      - Hanche Pitch (RS-04)
   - Hanche Roll (RS-03)                       - Hanche Roll (RS-03)
   - Hanche Yaw (RS-03)                        - Hanche Yaw (RS-03)
   - Genou Flexion (RS-04 / GT3)               - Genou Flexion (RS-04 / GT3)
   - Cheville Pitch (RS-03)                    - Cheville Pitch (RS-03)
   - Cheville Roll (RS-03)                     - Cheville Roll (RS-03)
```

---

## 2. Vérification de Cohérence & Points de Vigilance

### 2.1 Bilan de Masse et Centrage
- **Masse Globale** : 40.4 kg validée à travers les études de sous-systèmes.
- **Répartition** : Le centre de masse est maintenu bas (proche du pelvis), ce qui favorise la stabilité de la marche et réduit le moment d'inertie lors des accélérations de la taille.

### 2.2 Chaîne de Communication CAN-FD
- **Sectorisation nécessaire** : Les 26 moteurs ne doivent pas être placés sur un bus unique. La sectorisation recommandée (Bus Bras G, Bus Bras D, Bus Jambe G, Bus Jambe D, Bus Cou/Tête) prévient la saturation de la bande passante et garantit le déterminisme temporelle à 1 kHz.

### 2.3 Gestion Thermique et Structurelle
- **Interfaces Métalliques CNC** : L'utilisation de flasques/carters en Aluminium 6061-T6 usinés sur la CNC C500 pour les moteurs RS-04 (120 Nm) prévient le fluage du PA12-CF et sert de dissipateur thermique.

---

## 3. Conclusion d'Audit

L'architecture globale 00 du D-Bot est **cohérente, réaliste et correctement dimensionnée**. Les choix matériels (RobStride, PA12-CF, Alu 6061-T6, Bus 48V) correspondent aux standards actuels de la robotique humanoïde agile (ex: Unitree G1, K-Scale, Berkeley Humanoid).

*Rapport d'audit nettoyé et consolidé.*