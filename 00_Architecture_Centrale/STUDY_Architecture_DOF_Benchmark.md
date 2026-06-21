# Étude Structurale : Architecture DOF & Benchmark Industriel du D-Bot

Ce document détaille la cinématique du robot **D-Bot (Standard 27 DOF)**, son inventaire de motorisation actif, et son positionnement technique comparé aux leaders mondiaux de l'industrie robotique.

---

## 1. Architecture Cinématique D-Bot (27 Degrés de Liberté)

Le D-Bot est un robot humanoïde de performance agile conçu pour la recherche dynamique (marche rapide, course, manipulation fine). Son squelette hybride intègre **27 moteurs RobStride (Quasi-Direct Drive)** ainsi que **16 servomoteurs Feetech** pour ses mains articulées (D-Hand).

```
                 [ TÊTE ] ── Cou Pan/Tilt (2× RS-05)
                    │
        ┌───────────┴───────────┐
     [ BRAS G ]              [ BRAS D ] ── Épaules (RS-04/RS-03/RS-02), Coudes (RS-03), 
        │                       │          Supination (RS-02), Poignets (RS-00) et D-Hand
   ┌────┴───────────────────────┴────┐
   │             [ BUSTE ]           │ ── Taille Yaw (1× RS-06)
   └────┬───────────────────────┬────┘
        │                       │
    [ JAMBE G ]             [ JAMBE D ] ── Hanches (RS-04/RS-03), Genoux (RS-04 + GT3)
                                           et Chevilles Cardan (2× RS-03 en différentiel)
```

### 🦾 Répartition des 27 Degrés de Liberté (RobStride)

*   **Tête / Cou (2 DOF)** : Pan (Rotation) + Tilt (Inclinaison) ➔ **2× RS-05**
*   **Taille / Waist (1 DOF)** : Lacet de la taille (Waist Yaw) ➔ **1× RS-06** (moteur actif V1)
*   **Membres Supérieurs (12 DOF - 6 par bras)** :
    *   Épaule Pitch (Flexion/Extension) ➔ **1× RS-04** (Upgrade couple)
    *   Épaule Roll (Abduction/Adduction) ➔ **1× RS-03**
    *   Épaule Yaw (Rotation interne/externe) ➔ **1× RS-02**
    *   Coude Pitch (Flexion/Extension) ➔ **1× RS-03** (Upgrade couple)
    *   Supination Avant-Bras (Forearm Roll) ➔ **1× RS-02** (Nouveau DOF biomimétique)
    *   Poignet Pitch (Flexion/Extension main) ➔ **1× RS-00**
*   **Membres Inférieurs (12 DOF - 6 par jambe)** :
    *   Hanche Pitch (Flexion/Extension) ➔ **1× RS-04**
    *   Hanche Roll (Abduction/Adduction) ➔ **1× RS-03**
    *   Hanche Yaw (Rotation interne/externe) ➔ **1× RS-03**
    *   Genou Pitch (Flexion/Extension) ➔ **1× RS-04** (Déplacé haut cuisse + réduction courroie GT3 2.5:1)
    *   Cheville Pitch (Flexion/Extension pied) ➔ **2× RS-03** (Mécanisme différentiel à cardan)
    *   Cheville Roll (Inversion/Éversion pied) ➔ *(Partagé cinématiquement par les 2 mêmes moteurs RS-03 de Cheville)*

> [!NOTE]
> **Le point clé de la Cheville Différentielle** : 
> Physiquement, chaque jambe possède **2 moteurs RS-03** dédiés à la cheville. Par couplage cinématique différentiel, ces deux moteurs gèrent **à la fois** le mouvement de Pitch (flexion) et de Roll (stabilité latérale). Il n'y a donc que 4 moteurs physiques de chevilles au total sur le robot pour 4 DOF distincts, ce qui minimise la masse suspendue.

---

## 2. Inventaire Physique des Moteurs RobStride du D-Bot

Voici le décompte matériel et le bilan de masse exact de la motorisation QDD du D-Bot :

| Modèle Moteur | Quantité Active | Couple Nom. (Unit.) | Couple Pic (Unit.) | Masse Unit. (g) | Masse Totale | Usage Principal sur le D-Bot |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **RS-04** | **6** | 40 N.m | 120 N.m | 1420g | 8.52 kg | Hanches Pitch (2) + Genoux (2) + Épaules Pitch (2) |
| **RS-03** | **12** | 20 N.m | 60 N.m | 880g | 10.56 kg | Épaules Roll (2) + Coudes Pitch (2) + Hanches Roll/Yaw (4) + Chevilles (4) |
| **RS-06** | **1** | 11 N.m | 36 N.m | 621g | 0.62 kg | Taille (Waist Yaw) (1 acheté & monté) |
| **RS-02** | **4** | 6 N.m | 17 N.m | 405g | 1.62 kg | Épaules Yaw (2) + Supination Avant-Bras (2) |
| **RS-00** | **2** | 5 N.m | 14 N.m | 310g | 0.62 kg | Poignets Pitch (2) |
| **RS-05** | **2** | 1.6 N.m | 5.5 N.m | 191g | 0.38 kg | Cou Pan/Tilt (2) |
| **TOTAL** | **27** | — | — | — | **~22.32 kg**| **Masse totale de la motorisation QDD** |

*Note : Les 16 servomoteurs Feetech (10× STS3250 + 6× HL-3915) équipant les mains hybrides (D-Hand) ajoutent ~1.10 kg de motorisation fine (avec drivers/convertisseurs locaux sur l'avant-bras), portant le total à 43 actionneurs embarqués.*

---

## 3. Évolution D-Bot par rapport au Standard K-Scale

Le D-Bot ne se contente pas d'ajouter des moteurs, il change de catégorie de performance par rapport au **K-Bot standard de K-Scale Labs** (fiche technique de référence disponible séparément dans [BENCHMARK_K-Bot_K-Scale.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/00_Architecture_Centrale/BENCHMARK_K-Bot_K-Scale.md)).

Cette évolution est structurée selon deux axes stratégiques :

### 3.1 Nouveaux Degrés de Liberté (Additions DOF)
*Ces moteurs ajoutent des mouvements essentiels à l'équilibre et à la manipulation, inexistants sur le K-Bot standard.*

| Ajout DOF D-Bot | Moteur retenu | Qté | Couple Pic unitaire | Intérêt Technique |
| :--- | :---: | :---: | :---: | :--- |
| **Tête (Pan/Tilt)** | RS-05 | 2 | 5.5 N.m | Vision active orientable (SLAM/Perception) sans tourner le buste. |
| **Supination Avant-Bras** | RS-02 | 2 | 17 N.m | Forearm Roll biomimétique (type Tesla Optimus) pour l'orientation des mains. |
| **Cheville Roll** | RS-03 (partagé) | (2) | 60 N.m | Correction latérale fine, équilibrage actif et marche sur terrains irréguliers. |
| **Waist Yaw (Taille)** | RS-06 | 1 | 36 N.m | Lacet actif de la taille (dissociation buste/bassin pour l'équilibre dynamique). |

### 3.2 Upgrades de Puissance (Moteurs surclassés)
*Ces moteurs remplacent les modèles standards K-Scale pour augmenter drastiquement la charge utile et permettre la course.*

| Articulation | K-Bot (Std) | D-Bot (Upgrade) | Gain Couple Pic | Bénéfice Direct |
| :--- | :---: | :---: | :---: | :--- |
| **Épaule Pitch** | RS-03 | **RS-04** | **+100%** (60 ➔ 120 N.m) | Charge utile bras tendu doublée (➔ 10 kg). |
| **Coude Pitch** | RS-02 | **RS-03** | **+252%** (17 ➔ 60 N.m) | Soulagement du coude, portage lourd. |
| **Cheville Pitch** | RS-02 | **2× RS-03** | **+252%** (34 ➔ 120 N.m) | Double RS-03 en différentiel cardan pour la propulsion et la course. |

---

## 4. Benchmark Industrie — D-Bot vs Robots Humanoïdes

Pour situer nos choix de conception mécanique sur l'échelle de l'état de l'art mondial en 2026 :

| Robot | DOF | DOF/Jambe | Mécanique Cheville | Couple max Jambe | Poids | Type d'Actionneurs |
| :--- | :---: | :---: | :--- | :---: | :---: | :--- |
| **D-Bot (notre)** | **27** | **6** | **Série QDD Cardan Différentiel** | **120 N.m** (RS-04) | **~40.4 kg** | QDD RobStride (9:1) |
| K-Bot (base) | 20 | 5 | Tirant simple Pitch uniquement (pas de Roll) | 120 N.m (RS-04) | ~34.0 kg | QDD RobStride (9:1) |
| **Unitree G1** | 23 | 6 | Parallèle à 2 bielles (différentiel) | 120 N.m | 35-47 kg | QDD propriétaire |
| **Tesla Optimus** | 28+ | 6 | Parallèle à 2 bielles (différentiel) | 180 N.m rotary | ~73.0 kg | Réducteurs Harmonic + Linéaire |
| **Figure 02** | 28 | 6 | Joint universel + transmission linéaire | 150 N.m | ~60.0 kg | Actionneurs harmoniques custom |
| **Fourier GR-2** | 53 | 8 | Parallèle bielles différentiel | 380 N.m | 63.0 kg | Actionneurs FSA 2.0 intégrés |

> [!TIP]
> **Positionnement Technique** : 
> Avec 27 DOF (dont le lacet de taille actif en RS-06), une cheville différentielle active à double RS-03 (120 N.m) et un genou suralimenté à courroie GT3 (300 N.m effectifs), le D-Bot surclasse le K-Bot et se place au niveau cinématique d'un **Unitree G1** ou d'un **Tesla Optimus**, tout en préservant un budget matière très bas (~$5k).
