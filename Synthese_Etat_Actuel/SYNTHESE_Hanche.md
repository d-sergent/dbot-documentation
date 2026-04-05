# SYNTHÈSE : Architecture Hanche (D-Bot)

## 1. Actionneurs (RobStride)
La hanche adopte une architecture **séquentielle F-A-R** (Flexion→Abduction→Rotation), standard des robots humanoides Gen2 (Figure 02, Unitree G1), pour maximiser la compacité du bassin et offrir des proportions anatomiques naturelles.

| Maillon | Axe | Moteur | Couple (Pic) | Couple (Nominal) | Rôle |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | **Pitch (Y)** | **RobStride RS-04** | **120 N.m** | 40 N.m | Propulsion et levage fémur — fixé au bassin/torse |
| **2** | **Roll (X)** | **RobStride RS-03** | 60 N.m | 20 N.m | Stabilité latérale (grand écart) |
| **3** | **Yaw (Z)** | **RobStride RS-03** | 60 N.m | 20 N.m | Rotation interne/externe — vers la cuisse |

## 2. Transmission & Cinématique
- **Type** : Séquentiel F-A-R à 3 DOF — **Maillon 1: Pitch → Maillon 2: Roll → Maillon 3: Yaw**.
- **Liaison Fémur** : Le dernier moteur (RS-03 Yaw) est pris en "sandwich" par les plaques latérales du fémur hybride.
- **Direct Drive** : Pas de courroie GT3 sur la hanche (marges de couple RS-04 largement suffisantes — max 25% en locomotion ; voir Doc 26 §5).
- **Concentration des masses** : Moteurs regroupés au plus près du centre de gravité pour minimiser l'inertie de balancement.

## 3. Conception Mécanique
- **Brackets de liaison** : 2 pièces CNC en aluminium **7075-T6** (haute résistance).
  - **Bracket 1 (Pitch-Roll)** : Relie l'axe RS-04 Pitch au corps RS-03 Roll.
  - **Bracket 2 (Roll-Yaw)** : Relie l'axe RS-03 Roll au corps RS-03 Yaw.
- **Usinage** : Fabrication CNC sur C500 — géométrie simple (équerres plates).

## 4. Marges de Couple Hip Pitch en F-A-R

Le RS-04 Pitch (Maillon 1) porte les masses de tous les maillons suivants :

| Scénario | Couple requis | RS-04 (120 N.m) | Marge |
|:---|:---:|:---:|:---:|
| **Marche normale (2-3 km/h)** | ~19 N.m | 120 N.m | **+530% ✅** |
| **Course pic (×4.0 dyn.)** | ~30 N.m | 120 N.m | **+300% ✅** |

> Les marges sont si confortables que **l'amplification GT3 n'est pas retenue pour la hanche**. Pour l'amplification GT3, voir la Doc 15g (Genou — 300 N.m).

## 5. Rationale du Choix F-A-R vs Alternatives

| Config | Standard | Bassin | Proportions | Verdict D-Bot |
|:---|:---:|:---:|:---:|:---:|
| R-A-F (ancien D-Bot) | Non-standard | Moyen | Peu naturel | ❌ Abandonné |
| A-R-F (Tesla Optimus) | Gen1 déclinant | Bon | Court | ❌ Gen1 |
| **F-A-R (D-Bot V2)** | **Gen2 ✅** | **Excellent** | **Anatomique** | **✅ Adopté** |

---
### 🔗 Études Complètes
- **[26 — Étude Bloc Pelvien Hanche](../26_Etude_Bloc_Pelvien_Hanche.md)** — Benchmark industrie + analyse GT3 rejetée
- **[15g — GT3 Genou](../15g_Solution_S6_Courroie_GT3_Genou.md)** — Amplification GT3 appliquée au genou (300 N.m)
- **[16 — Conclusions Architecture Finale](../16_Conclusions_Architecture_DBot.md)**

*Dernière mise à jour : Avril 2026 — Passage à l'architecture F-A-R (Pitch→Roll→Yaw).*
