# 14 - Cinématique & Choix Moteurs

Ce document détaille l'architecture cinématique du D-Bot (**Standard 24 DOF**) et les spécifications techniques des actionneurs **RobStride**.

## 1. Configuration K-Bot Standard (20 DOF)

### 📊 Architecture Officielle K-Scale
Le K-Bot standard est un robot humanoïde open-source de taille réelle développé par K-Scale Labs, équipé de **20 moteurs RobStride** pour 20 degrés de liberté. La configuration D-Bot étend cette base avec une tête articulée.

**Source** : [K-Scale Official Documentation](https://docs.kscale.dev/robots/k-bot/motor-id-mapping)

---

### 🦾 BRAS (10 moteurs - 5 par bras)

**Configuration par bras :**

| Articulation | Moteur | IDs<br/>(G/D) | Couple<br/>Pic | Couple<br/>Nom. | Poids | Fonction |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Épaule Pitch** | RS-03 | 11 / 21 | 60 N.m | 20 N.m | 880g | Lever le bras |
| **Épaule Roll** | RS-03 | 12 / 22 | 60 N.m | 20 N.m | 880g | Écarter le bras |
| **Épaule Yaw** | RS-02 | 13 / 23 | 17 N.m | 6 N.m | 405g | Rotation interne |
| **Coude Pitch** | RS-02 | 14 / 24 | 17 N.m | 6 N.m | 405g | Flexion |
| **Poignet Roll** | RS-00 | 15 / 25 | 14 N.m | 5 N.m | 310g | Orientation fine |

**Total par bras** : 3 kg environ  
**Total 2 bras** : 10 moteurs (4× RS-03 + 4× RS-02 + 2× RS-00)

---

### 🦵 JAMBES (10 moteurs - 5 par jambe)

**Configuration par jambe :**

| Articulation | Moteur | IDs<br/>(G/D) | Couple<br/>Pic | Couple<br/>Nom. | Poids | Fonction |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Hanche Pitch** | RS-04 | 31 / 41 | 120 N.m | 40 N.m | 1420g | Flexion jambe |
| **Hanche Roll** | RS-03 | 32 / 42 | 60 N.m | 20 N.m | 880g | Équilibre latéral |
| **Hanche Yaw** | RS-03 | 33 / 43 | 60 N.m | 20 N.m | 880g | Rotation hanche |
| **Genou Pitch** | RS-04 | 34 / 44 | 120 N.m | 40 N.m | 1420g | Flexion genou |
| **Cheville Pitch** | RS-02 | 35 / 45 | 17 N.m | 6 N.m | 405g | Propulsion (via mécanisme tirant) |

**Total par jambe** : 4.6 kg environ  
**Total 2 jambes** : 10 moteurs (4× RS-04 + 4× RS-03 + 2× RS-02)

---

### 🔢 INVENTAIRE K-BOT STANDARD

| Modèle | Quantité | Poids Unit. | Poids Total | Usage Principal |
| :---: | :---: | :---: | :---: | :--- |
| **RS-04** | 4 | 1420g | 5.68 kg | Hanches Pitch + Genoux |
| **RS-03** | 8 | 880g | 7.04 kg | Épaules + Rotations hanches |
| **RS-02** | 6 | 405g | 2.43 kg | Coudes + Yaw épaules + Chevilles |
| **RS-00** | 2 | 310g | 0.62 kg | Poignets |
| **TOTAL** | **20** | | **15.77 kg** | Total moteurs K-Bot |

---

### 🤖 ÉVOLUTION D-BOT (24 DOF — "D-Bot Performance")

Le **D-Bot** étend le K-Bot de 20 à **24 DOF** avec trois ajouts. Voir [Analyse Biomécanique](./15_Analyse_Biomecanique.md) pour la justification détaillée de chaque upgrade.

| Ajout D-Bot | Moteur | Quantité | Couple Pic | Fonction |
| :--- | :---: | :---: | :---: | :--- |
| **Cou Pan** (Yaw) | RS-05 | 1 | 5.5 N.m | Rotation horizontale tête |
| **Cou Tilt** (Pitch) | RS-05 | 1 | 5.5 N.m | Inclinaison tête |
| **Cheville Pitch** ⬆️ | RS-02 → **RS-03** | 2 (remplacement) | 17 → **60 N.m** | **Propulsion améliorée** (K-Bot trop faible en direct-drive) |
| **Cheville Roll** 🆕 | RS-02 | 2 (ajout) | 17 N.m | **Stabilité latérale** (Correction équilibre) |

**Total D-Bot** : 20 (Base) + 2 (Tête) + 2 (Chevilles Roll) = **24 moteurs**, avec upgrade Pitch intégré.

> [!NOTE]
> **Mécanisme de cheville K-Bot (Tirant/Linkage)** : Dans le K-Bot original, le RS-02 de cheville n'est **pas en prise directe** sur l'axe de la cheville. Il est monté **haut dans le tibia** et actionne le pied via un **mécanisme de tirant** (connecting rod / pushrod). Ce bras de levier crée un avantage mécanique (~2-3:1) qui multiplie le couple effectif : 17 N.m × 2 ≈ **34 N.m** à la cheville, suffisant pour la marche lente. Pour le D-Bot, l'upgrade en RS-03 élimine le besoin de ce mécanisme et permet un montage **direct-drive** plus simple.

![Mécanisme de cheville K-Bot avec tirant (RS-02 haut dans le tibia)](./assets/kbot_ankle_linkage.png)

## 2. Spécifications Moteurs RobStride (Gamme Complète)
Voici les données techniques consolidées pour l'ensemble de la gamme RobStride (Février 2025).  
*Prix officiels RobStride ou sources vérifiées (OpenELAB, AiFitLab) - Hors taxes/livraison.*

| Modèle | Pic<br/>(N.m) | Nom.<br/>(N.m) | Vmax<br/>(RPM) | Poids<br/>(g) | Dim.<br/>(mm) | Ratio | Prix<br/>($) | Volt.<br/>(V) | Usage D-Bot |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **RS-05** | **5.5** | 1.6 | 480 | **191** | 46×46×44 | 7.75:1 | **$120** | 48V (15-60V) | **Cou**, Doigts (futur) |
| **RS-00** | **14.0** | 5.0 | 315 | **310** | 57×57×51 | 10:1 | **$135** | 48V (24-60V) | **Poignet** (Compact, fort couple) |
| **RS-01** | **17.0** | 6.0 | 350 | **380** | 78.5×78.5×40 | 7.75:1 | **$140** | 36V (24-48V) | Alternative RS-02 (36V) |
| **RS-02** | **17.0** | 6.0 | 410 | **405** | 78.5×78.5×45.5 | 7.75:1 | **$160** | 48V (24-60V) | **Coude**, Biceps, Poignet |
| **RS-06** | **36.0** | 11.0 | 480 | **621** | 88×88×49 | 9:1 | **$230** | 48V (15-60V) | Entre-deux (Épaule légère) |
| **RS-03** | **60.0** | 20.0 | 195 | **880** | 106×106×56 | 9:1 | **$250** | 48V (15-60V) | **Épaule** (Force brute) |
| **RS-04** | **120.0** | 40.0 | 200 | **1420** | 120×120×56 | 9:1 | **$280** | 48V (15-60V) | **Hanche**, Genou, Cheville |

### Analyse Comparative

####  RS-05 vs RS-00 (Petits Moteurs)
*   **RS-05** : Ultraléger (191g), idéal pour le cou où chaque gramme compte. Couple modeste (5.5 N.m) mais suffisant pour orientation.
*   **RS-00** : Plus dense (310g, +62%) mais délivre **2,5× plus de couple** (14 N.m). Parfait pour un poignet devant porter des charges sans fléchir.

#### RS-01 vs RS-02 (Moteurs Moyens)
*   **Même couple** (17 N.m pic), mais **RS-01** optimisé pour **36V** (idéal pour batteries LiPo 8S), plus compact en profondeur (40mm vs 45.5mm).
*   **RS-02** : Conçu pour **48V**, marginalement plus lourd (+25g). Standard pour D-Bot aux coudes/biceps.

#### RS-06 (Intermédiaire Nouveau)
*   **Niche** : Entre RS-02 (17 N.m) et RS-03 (60 N.m). Avec **36 N.m** et 621g, c'est un compromis pour des articulations nécessitant plus que du RS-02 sans le poids du RS-03.
*   **Usage potentiel** : Épaule de petits robots, torse rotation, ou remplacer un RS-03 si l'on veut économiser 260g et 20$.

#### RS-03 vs RS-04 (Gros Moteurs)
*   **Saut de performance brutal** : RS-03 → 60 N.m (880g) ; RS-04 → **120 N.m** (1420g, +61% poids).
*   **RS-03** : Minimum vital pour l'épaule D-Bot (couple nécessaire pour contrer le bras-de-levier).
*   **RS-04** : Incontournable pour hanches/jambes. **Attention** : Peut briser des pièces PLA/PETG standard → Utiliser **PETG-CF (100% remplissage)** ou **Alu 6061 CNC**.

### Choix pour le D-Bot — Répartition Complète (24 DOF)
| Zone | Moteur | Quantité | Couple Pic | Justification |
| :--- | :---: | :---: | :---: | :--- |
| Cou (Pan/Tilt) | RS-05 | 2 | 5.5 N.m | Légèreté critique (tête lourde avec LiDAR/caméras) |
| Poignet | RS-00 | 2 | 14 N.m | Compact, fort couple pour manipulation fine |
| Épaule Yaw + Coude | RS-02 | 4 | 17 N.m | Standard polyvalent 48V |
| Épaule Pitch/Roll | RS-03 | 4 | 60 N.m | Force pour porte-à-faux bras tendu |
| Hanche Roll/Yaw | RS-03 | 4 | 60 N.m | Équilibre latéral + rotation |
| Hanche Pitch + Genou | RS-04 | 4 | 120 N.m | Portance totale (~36 kg robot) |
| **Cheville Pitch** ⬆️ | **RS-03** | **2** | **60 N.m** | **Propulsion (upgrade vs RS-02 K-Bot)** |
| **Cheville Roll** 🆕 | **RS-02** | **2** | **17 N.m** | **Stabilité latérale (NOUVEAU)** |

**Total moteurs D-Bot** : 2 + 2 + 4 + 4 + 4 + 4 + 2 + 2 = **24 moteurs**.

## 3. Communication & Alimentation
Tous les moteurs partagent le même protocole :
*   **Bus** : CAN 2.0B @ 1 Mbps.
*   **Alimentation** : 48V DC Nominal (Supportent 24V mais avec couple/vitesse réduits). RS-01 optimisé pour 36V.
*   **Câblage** : Daisy-chain (Chaîne) via connecteurs JST-GH 1.25mm (Data) et XT60 (Power).
*   **Encodeurs** : Dual 14-bit magnetic encoders (haute précision + redondance).
*   **Protection** : IP52 standard (IP67 en option sur certains modèles).

> [!WARNING]
> **Attention au RS-04** : Avec 120 N.m de couple, ce moteur peut briser des pièces imprimées en PLA ou PETG standard en cas de collision. Utilisez impérativement du **PETG-CF** (Remplissage 100%) ou des pièces CNC Alu 6061 pour les brackets de hanches.

> [!NOTE]
> **Prix et Disponibilité** : Les prix sont issus des sources officielles RobStride et distributeurs agréés (OpenELAB, AiFitLab) en Février 2025. Vérifiez la disponibilité avant commande - certains modèles peuvent avoir des délais variables.
