# Étude Structurale : Architecture DOF & Benchmark Industriel du D-Bot

Ce document détaille la cinématique du D-Bot (Standard 26 DOF), son évolution par rapport au standard K-Scale, et le positionnement concurrentiel du robot face aux leaders de l'industrie.

## 1. Configuration K-Bot Standard (20 DOF)

### 📊 Architecture Officielle K-Scale
Le K-Bot standard est un robot humanoïde open-source de taille réelle développé par K-Scale Labs, équipé de **20 moteurs RobStride** pour 20 degrés de liberté. La configuration D-Bot étend cette base avec une tête articulée.

**Source** : [K-Scale Official Documentation](https://docs.kscale.dev/robots/k-bot/motor-id-mapping)

---

### 🦾 BRAS (10 moteurs - 5 par bras)

**Configuration par bras :**
*   **Épaule Pitch** : RS-03
*   **Épaule Roll** : RS-03
*   **Épaule Yaw** : RS-02
*   **Coude Pitch** : RS-02
*   **Poignet Roll** : RS-00

**Total par bras** : ~3 kg environ  
**Total 2 bras** : 10 moteurs (4× RS-03 + 4× RS-02 + 2× RS-00)

---

### 🦵 JAMBES (10 moteurs - 5 par jambe)

**Configuration par jambe :**

| Articulation | Moteur | IDs (G/D) | Couple Pic | Couple Nom. | Poids | Fonction |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Hanche Pitch** | RS-04 | 31 / 41 | 120 N.m | 40 N.m | 1420g | Flexion jambe |
| **Hanche Roll** | RS-03 | 32 / 42 | 60 N.m | 20 N.m | 880g | Équilibre latéral |
| **Hanche Yaw** | RS-03 | 33 / 43 | 60 N.m | 20 N.m | 880g | Rotation hanche |
| **Genou Pitch** | RS-04 | 34 / 44 | 120 N.m | 40 N.m | 1420g | Flexion genou |
| **Cheville Pitch** | RS-02 | 35 / 45 | 17 N.m | 6 N.m | 405g | Propulsion (via mécanisme tirant) |

**Total par jambe** : ~4.6 kg environ  
**Total 2 jambes** : 10 moteurs (4× RS-04 + 4× RS-03 + 2× RS-02)

---

### 🔢 INVENTAIRE K-BOT STANDARD

| Modèle | Quantité | Poids Unit. | Poids Total | Usage Principal |
| :---: | :---: | :---: | :---: | :--- |
| **RS-04** | 6 | 1420g | 8.52 kg | Hanches Pitch + Genoux + Épaules Pitch |
| **RS-03** | 10 | 880g | 8.80 kg | Épaules Roll + Rotations hanches + Chevilles Cardan |
| **RS-06** | 2 | 621g | 1.24 kg | Coudes |
| **RS-02** | 2 | 405g | 0.81 kg | Yaw épaules |
| **RS-00** | 2 | 310g | 0.62 kg | Poignets |
| **RS-05** | 2 | 191g | 0.38 kg | Cou Pan/Tilt |
| **TOTAL** | **26** | — | **~20.37 kg** | **Ensemble du corps robotisé** |

---

## 2. Évolution D-Bot (26 DOF — "D-Bot Performance")

Le **D-Bot** ne se contente pas d'ajouter des moteurs, il change de catégorie de performance. On distingue deux types de modifications par rapport au standard K-Scale :

### 2.1 Nouveaux Degrés de Liberté (Additions DOF)
*Ces moteurs ajoutent des mouvements inexistants sur le K-Bot standard.*

| Ajout DOF | Moteur | Qté | Couple Pic | Fonction |
| :--- | :---: | :---: | :---: | :--- |
| **Tête (Pan/Tilt)** | RS-05 | 2 | 5.5 N.m | Vision active & Interaction sociale |
| **Supination Avant-Bras** | RS-02 | 2 | 17 N.m | **Forearm Roll** (Biomimétique Tesla) |
| **Cheville Roll** | RS-03 | 2 | 60 N.m | Équilibre latéral & terrain irrégulier |

### 2.2 Upgrades de Puissance (Évolutions Moteurs)
*Ces moteurs remplacent les modèles standards pour augmenter les capacités de portage et de course.*

| Articulation | K-Bot (Std) | D-Bot (Perf) | Gain Couple | Bénéfice |
| :--- | :---: | :---: | :---: | :--- |
| **Épaule Pitch** | RS-03 | **RS-04** | **+100%** | Portage frontal (5 kg → 10 kg) |
| **Coude Pitch** | RS-02 | **RS-06** | **+110%** | Manipulation bras plié |
| **Cheville Pitch** | RS-02 | **RS-03** | **+250%** | Propulsion & Course (Cardan) |

**Total D-Bot** : 20 (Base K-Bot) + 6 (Nouveaux DOF) = **26 DOF**.

---

## 3. Benchmark Industrie — D-Bot vs Robots Haut de Gamme

### 3.1 Comparatif Global (Corps Entier)

| Robot | DOF | DOF/Jambe | Cheville | Méca. Cheville | Couple max jambe | Poids | Actionneurs | Prix |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :--- | :---: |
| **D-Bot (notre)** | **26** | **6** | **2 (P+R)** | **Série QDD** | **120 N.m** (RS-04) | ~40.2 kg | QDD RobStride 9:1 | ~$5k |
| K-Bot (base) | 20 | 5 | 1 (P) | Tirant (linkage) | 120 N.m (RS-04) | ~34 kg | QDD RobStride 9:1 | ~$4k |
| **Unitree G1** | 23 | **6** | **2** | **Parallèle RSU** | **120 N.m** | 35-47 kg | QDD propriétaire | ~$16k |
| **Tesla Optimus** | 28+ | 6 | 2 | **Parallèle SPU** | **180 N.m** rotary / 8000N linéaire | ~73 kg | Harmonic + Linéaire | N/A |
| **Figure 02** | 28 | 6 | 2 | **Universel + linéaire** | **150 N.m** | ~60 kg | Custom harmonic | N/A |
| **Fourier GR-2** | 53 | ~8 | 2+ | **Parallèle** (FSA 2.0) | **380 N.m** | 63 kg | FSA 2.0 (7 types) | ~$150k |
| **Agility Digit** | 28 | 5 | 2 | **SEA** (élastique) | N/A | 65 kg | Series-Elastic | ~$300k+ |

> [!NOTE]
> **Positionnement D-Bot** : Avec 26 DOF, 6 DOF/jambe et 6 DOF/bras, le D-Bot est au niveau du Unitree G1 (23 DOF) et se rapproche du Tesla Optimus en termes d'architecture cinématique.
