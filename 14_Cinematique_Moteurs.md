# 14 - Cinématique & Choix Moteurs

Ce document détaille l'architecture cinématique du D-Bot (Target 24 DOF) et les spécifications techniques des actionneurs **RobStride**.

## 1. Architecture Cinématique (Cible)
L'architecture du D-Bot est une évolution du K-Bot standard (20 DOF + 2 Tête), portant le total à **24 Degrés de Liberté** pour une manipulation plus fine.

### Répartition des Moteurs
| Zone | Articulation | DOF | Moteur Recommandé | Rôle |
| :--- | :--- | :--- | :--- | :--- |
| **Tête** | Cou (Pan / Tilt) | 2 | **2x RS-05** | Orientation du regard (LiDAR + Caméras). |
| **Bras (x2)** | Épaule (Pitch, Roll) | 2 | **2x RS-03** | Force brute pour lever le bras. |
| | Biceps (Yaw) | 1 | **1x RS-02** | Rotation du bras. |
| | Coude (Pitch) | 1 | **1x RS-02** | Flexion. |
| | Avant-bras (Roll) | 1 | **1x RS-02** | Pronation/Supination. |
| | Poignet (Pitch/Yaw) | 1 | **1x RS-00** | Orientation fine de la main. |
| **Jambes (x2)** | Hanche (Roll, Yaw, Pitch) | 3 | **3x RS-04** | Portance principale et équilibre. |
| | Genou (Pitch) | 1 | **1x RS-04** | Flexion (Couple max requis). |
| | Cheville (Pitch/Roll) | 1 | **1x RS-04** | Propulsion et adaptation au sol. |

*Note : La configuration standard "K-Bot" n'a que 5 moteurs par bras (pas de RS-00) et 5 par jambe, soit 20 moteurs au total. Le D-Bot ajoute le Cou (+2) et le Poignet (+2), soit 24 moteurs.*

## 2. Spécifications Moteurs RobStride (Gamme Complète)
Voici les données techniques consolidées pour l'ensemble de la gamme RobStride (Février 2025).  
*Prix officiels RobStride ou sources vérifiées (OpenELAB, AiFitLab) - Hors taxes/livraison.*

| Modèle | Couple Pic (N.m) | Couple Nominal (N.m) | Vitesse Max (RPM) | Poids (g) | Dimensions (mm) | Ratio | Prix ($) | Voltage | Usage D-Bot |
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

### Choix pour le D-Bot (Rappel Répartition)
| Zone | Moteur | Quantité | Couple Requis | Justification |
| :--- | :---: | :---: | :---: | :--- |
| Cou (Pan/Tilt) | RS-05 | 2 | 5.5 N.m | Légèreté critique (tête lourde avec LiDAR/caméras) |
| Poignet | RS-00 | 2 | 14 N.m | Compact, fort couple pour manipulation fine |
| Coude/Biceps/Avant-bras | RS-02 | 6 (3 par bras) | 17 N.m | Standard polyvalent 48V |
| Épaule | RS-03 | 2 | 60 N.m | Force indispensable pour porte-à-faux max |
| Jambes (Hanche/Genou/Cheville) | RS-04 | 10 (5 par jambe) | 120 N.m | Portance totale (~15 kg robot) |

**Total moteurs D-Bot** : 2 + 2 + 6 + 2 + 10 = **22 moteurs** (peut évoluer à 24 avec ajout doigts/torse).

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
