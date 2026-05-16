# Étude Comparative : Mécanismes de Cheville & Impact Dynamique (D-Bot)

Ce document présente l'analyse des différentes architectures d'articulations de cheville pour le D-Bot, le sourcing des composants de transmission, et l'impact de l'inertie distale sur les performances de marche et de course.

## 1. Mécanismes de Cheville — Les 4 Approches

L'articulation de la cheville est l'une des zones les plus critiques d'un robot humanoïde bipède de 40 kg. Elle doit supporter d'importants impacts dynamiques tout en gardant une masse minimale pour réduire l'inertie de la jambe lors de la phase de balancement.

---

### A. Série Direct-Drive (❌ Abandonné)
Le moteur Pitch (RS-02) est monté en haut du tibia avec un mécanisme de tirant (bielle). Le moteur Roll (RS-00) est monté directement au niveau de la cheville en couplage direct.

*   **Moteurs** : RS-02 (Pitch, haut tibia + tirant) + RS-00 (Roll, à la cheville).
*   **Masse distale** : **~1190g** (Moteur Roll lourd en bas du membre).
*   **Couple Pitch effectif** : ~34 N.m (RS-02 17 N.m × ratio tirant ~2:1).
*   **Couple Roll effectif** : 14 N.m (= couple direct du RS-00).
*   **Complexité** : ⭐ Très faible — conception et assemblage triviaux.
*   **Coût mécanique** : Très faible (simple bracket en L usiné).
*   **Verdict** : Abandonné en raison de la trop grande masse distale en bout de jambe, limitant la réactivité.

---

### B. Tirant simple / Linkage (K-Bot Original)
Le moteur RS-02 est monté en haut du tibia et actionne le pied uniquement en Pitch via une unique barre de poussée (pushrod). Le ratio de levier multiplie le couple.

*   **Moteurs** : RS-02 (Pitch uniquement), positionné haut dans le tibia.
*   **Masse distale** : **~0g** (aucun moteur en bas).
*   **Couple Pitch effectif** : ~34 N.m (17 N.m × ratio ~2:1).
*   **Roll** : ❌ Totalement absent (1 seul DOF).
*   **Complexité** : ⭐⭐ Moyenne.
*   **Verdict** : Insuffisant pour la stabilité latérale sur un robot dynamique de 40 kg (nécessite un axe de Roll).

---

### C. Hybride Tirant + Roll Direct (D-Bot V1 & V2)
Combine le meilleur des deux mondes : le Pitch est géré par tirant (moteur haut, couple multiplié), tandis que le Roll reste en direct-drive à la cheville (correction latérale fine, pas besoin d'un fort rapport de levier).

*   **Moteur Pitch** : RS-02 (V1) ou **RS-03 (V2)** monté haut dans le tibia + pushrod.
*   **Moteur Roll** : RS-00 monté directement à la cheville (direct-drive).
*   **Masse distale** : **~310g** (seulement le petit RS-00 en bas).
*   **Couple Pitch effectif** : **~120 N.m** (RS-03 60 N.m × ratio ~2:1) ⚡.
*   **Couple Roll effectif** : 14 N.m.
*   **Complexité** : ⭐⭐⭐ Élevée (pushrod + brackets pivot).
*   **Schéma cinématique** :
```
  ┌─────┐
  │GENOU│
  └──┬──┘
     │
  ╔══╧══╗ RS-03 Pitch ← Moteur HAUT (880g)
  ║PITCH║──────┐
  ╚═════╝      │ Pushrod
     │ Tibia   │ (barre de poussée)
     │         │
     │         │ Ratio levier ~2:1
     │         │ → 60 × 2 = 120 N.m effectifs !
     │         │
     │    ╔════╧═╗
     └────╢ ROLL ╟── RS-00 (310g) ← Seul moteur EN BAS (compact 57mm)
          ╚══╤═══╝
          ┌──┴──┐
          │PIED │
          └─────┘
```

---

### D. Parallèle à 2 Bielles Rotulées (Unitree G1, Tesla Optimus)
Deux moteurs sont montés en haut du tibia, chacun relié au pied par une bielle équipée de rotules sphériques. Les mouvements coordonnés (symétriques) gèrent le Pitch, les mouvements différentiels (asymétriques) gèrent le Roll. **Aucun moteur n'est présent à la cheville.**

*   **Moteurs** : 2× RS-02 ou RS-03 positionnés en haut du tibia.
*   **Bielles** : 2× tiges filetées M4 inox + 4× rotules sphériques (rod end bearings).
*   **Masse distale** : **~40g** (seules les bielles et rotules sont mobiles en bas).
*   **Couple Pitch effectif** : ~34 N.m (2× RS-02) ou ~120 N.m (2× RS-03).
*   **Couple Roll effectif** : ~17 N.m (2× RS-02) ou ~60 N.m (2× RS-03).
*   **Complexité** : ⭐⭐⭐⭐ Très élevée (cinématique parallèle inverse).
*   **Schéma cinématique** :
```
    Moteur A            Moteur B      ← 2 moteurs HAUT dans le tibia
        │                    │
        │ Bielle A           │ Bielle B    ← Tiges filetées avec
        │ (rod end +         │               rod end bearings
        │  tige M4)          │               à chaque extrémité
        │                    │
        ╰────────┬───────────╯
                 │
            ┌────┴────┐
            │  PIED   │        ← Plateforme mobile (2 DOF)
            └─────────┘

A↑ + B↑ (même sens)    = PITCH (flexion/extension)
A↑ + B↓ (sens opposé) = ROLL  (inversion/éversion)
```

> [!WARNING]
> **Le retour d'expérience industriel (Fourier GR-2)**
> En septembre 2024, Fourier Intelligence a **abandonné l'architecture parallèle** au profit du série pour le GR-2. Raisons officielles : simplification drastique du contrôle (suppression de la cinématique inverse parallèle), maintenance facilitée, et meilleur transfert Sim-to-Real. 
> Pour notre prototype D-Bot, la configuration hybride série/tirant (V2) est donc le choix le plus prudent avant d'envisager le parallèle.

---

## 2. Composants de Transmission pour Solution Parallèle (Sourcing)

Si l'architecture parallèle (V3) est adoptée, les pièces issues du modélisme RC gros calibre (hélicoptères 700/800) sont directement utilisables :

| Composant | Spécification | Source | Coût (est.) | Note |
| :--- | :--- | :--- | :---: | :--- |
| **Rotule sphérique M4** | Fisheye ball bearing SA4T/K | AliExpress / eBay | ~$5 / 10pcs | Acier trempé, débattement ±15° |
| **Tige filetée M4** | Inox A2 × 80mm | Quincaillerie | ~$3 | Longueur ajustable par écrou/contre-écrou |
| **Kit Pushrod RC complet** | RJX Swashplate Linkage M4 | RJXHobby | ~$10 / kit | Prêt à l'emploi (tige + rotules assemblées) |
| **Rotule industrielle** | Heim joint M4 male/female | RS Components | ~$5 / pièce | Qualité d'ajustement sans jeu mécanique |

**BOM Estimée pour équiper les 2 chevilles en parallèle :**
*   8× Rotules M4 (SA4T/K) : ~$8
*   4× Tiges filetées M4 inox : ~$5
*   8× Écrous nylstop M4 : ~$2
*   4× Brackets de pivot (PA12-CF imprimé) : ~$15
*   **Total transmission** : **~$30**

---

## 3. Analyse de l'Inertie Distale & Impact Dynamique

Le moment d'inertie de la jambe durant la phase de balancement (swing phase) est donné par la formule physique :

$$I = \sum (m \cdot r^2)$$

Où $m$ est la masse d'un composant et $r$ sa distance par rapport au pivot de rotation (l'axe de la hanche, environ $0.70\text{ m}$).

| Architecture | Masse Distale (Cheville) | Distance Pivot ($r$) | Contribution à l'Inertie ($I$) |
| :--- | :---: | :---: | :---: |
| **Hybride (V1/V2)** | **310 g** (RS-00) | $0.70\text{ m}$ | **$152\text{ g}\cdot\text{m}^2$** |
| **Parallèle (V3)** | **~40 g** (bielles) | $0.70\text{ m}$ | **$~19.6\text{ g}\cdot\text{m}^2$** |

### Conséquences sur la locomotion :
1.  **Marche lente (< 1 km/h)** : Toutes les architectures conviennent.
2.  **Course (> 5 km/h)** : La fréquence de foulée monte à ~3 Hz. Le balancement rapide d'une cheville lourde demande un couple d'accélération pharaonique à la hanche. L'architecture **parallèle (V3)** ou **hybride (V2)** est indispensable pour espérer courir en minimisant la consommation d'énergie.
3.  **Récupération de chutes** : Une faible inertie permet aux algorithmes de contrôle d'étendre la jambe d'appui en quelques millisecondes pour intercepter une chute.

---

## 4. Recommandation d'Itération Évolutive

| Phase | Architecture Cheville | Actionneurs | Coût add. | Intérêt technique |
| :--- | :--- | :--- | :---: | :--- |
| **V1 (Proto)** | **Hybride A** (Tirant + direct) | RS-02 Pitch + RS-00 Roll | $0 | Simple, éprouvé, suffisant pour stabiliser la marche. |
| **V2 (Optimisation)** | **Hybride B** (Tirant RS-06) | RS-02 → **RS-06** Pitch | ~$70 | Double le couple Pitch (~72 N.m effectifs) pour seulement +75g. *Sweet Spot* pour la marche rapide. |
| **V3 (Performance)** | **Parallèle** (Cinématique 2 bielles) | 2× RS-06 (ou RS-03) | ~$30 bielles | Élimine le moteur du pied. Inertie minimale (~20g.m²), idéal pour la course. |
