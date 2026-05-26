# Guide Avancé : Impression 3D Technique (PETG-CF & PA12-CF)

Ce guide compile les procédures critiques pour réussir vos impressions sur **Qidi Plus 4**, issues des retours techniques de Février 2026.

## 1. Gestion de l'Humidité (Facteur #1 d'Échec)
Le **PA12-CF** (Nylon) est extrêmement hygroscopique. Une exposition de 15 minutes à l'air libre suffit pour ruiner une impression.

### Protocole de Séchage & Transfert
1.  **Séchage Initial** :
    *   **PETG-CF** : 65°C pendant 6-8h. (La Qidi Box suffit).
    *   **PA12-CF** : 80°C - 90°C pendant 12h. (Four dédié recommandé si la Qidi Box plafonne).
2.  **Le Transfert "Flash"** (PA12-CF uniquement) :
    *   Ne laissez jamais la bobine refroidir dans le four (elle réabsorbe l'humidité).
    *   Transférez-la dans la Qidi Box en **moins de 2 minutes**.
3.  **Maintien en Qidi Box** :
    *   Réglez la Box sur **60°C - 70°C** pendant toute l'impression.
    *   **Règle absolue** : Le chemin de filament Box -> Extrudeur doit être 100% sous tube PTFE. Le moindre centimètre à l'air libre est un point de contamination.

## 2. La Révolution de la Buse en Carbure de Tungstène (Tungsten Carbide)
La Qidi Plus 4 est désormais équipée d'une **buse en carbure de tungstène**. Cette mise à niveau change radicalement la donne pour l'impression des filaments techniques et chargés de carbone (PLA-CF, PETG-CF, PA12-CF).

### Conséquences et Avantages Physiques
*   **Conductivité Thermique Exceptionnelle (~110 W/m·K) :** Contrairement à l'acier trempé (~15-20 W/m·K) qui est un très mauvais conducteur de chaleur, le carbure de tungstène conduit la chaleur presque aussi bien que le laiton.
    *   *Conséquence sur la température :* **Plus besoin de surchauffer le filament.** Vous pouvez imprimer aux températures nominales recommandées par les fabricants (ex: 210-220°C pour le PLA-CF, 240-250°C pour le PETG-CF) sans risquer de sous-extrusion ou de mauvaise liaison inter-couches.
    *   *Conséquence sur le débit :* La fusion est beaucoup plus rapide et homogène au cœur de la buse. Cela réduit la pression interne dans la tête et élimine les risques de clics de l'extrudeur à haut débit.
*   **Résistance à l'Abrasion Quasi-Éternelle (Dureté ~9 Mohs) :** Le carbure de tungstène est pratiquement inusable. Vous pouvez imprimer des dizaines de kilogrammes de filaments hautement abrasifs sans aucune dégradation du diamètre de sortie ou de la géométrie de la pointe (contrairement à l'acier trempé qui s'érode lentement sur le long terme).

### Ajustements des Réglages dans OrcaSlicer
*   **Température d'extrusion :** Réduisez de **5°C à 10°C** vos températures d'impression si vous aviez l'habitude de surchauffer pour compenser le manque de conductivité de l'acier trempé.
*   **Débit Volumétrique :** Bien que la buse en carbure de tungstène permette d'augmenter le débit maximal, nous vous conseillons de maintenir les limites de sécurité ci-dessous. Elles garantissent un fini mat homogène parfait et éliminent les risques de warping, mais vous bénéficiez désormais d'une marge de sécurité mécanique et thermique bien plus importante.

---

## 3. Calibration de Fiabilité (OrcaSlicer)
Pour du filament générique sur la Qidi Plus 4, la calibration manuelle est indispensable pour éviter les "blobs" et les clics d'extrudeur.

### Calibration du Débit (Flow Rate)
*   **Menu** : *Calibration > Flow Rate > Pass 1*.
*   **Objectif** : Repérez la surface la plus lisse sans bourrelets.
*   **Calcul** : $Flow_{New} = Flow_{Current} \times (100 + Modificateur) / 100$.

### Limite de Débit Volumétrique (Le verrou de sécurité)
C'est le réglage le plus critique pour la Plus 4.
*   **PLA Générique** : Limitez à **15 mm³/s**.
*   **eSUN PLA-CF** : Limitez à **12 mm³/s** (la viscosité augmente avec les charges de carbone, augmentant les forces de poussée dans l'extrudeur).
*   **PETG Générique** : Limitez à **8 mm³/s** pour éviter l'accumulation sur la buse.
*   **Action** : Réduisez la valeur par défaut de 20% pour garantir une fiabilité totale sur des impressions de longue durée.

### Pressure Advance (Coins nets)
*   **Valeurs typiques (Direct Drive)** : 
    *   PLA : **0.02 - 0.04**
    *   PETG : **0.04 - 0.06**

---

## 4. Profils JSON Optimisés (Réglages "Safe")
Plutôt que d'importer des fichiers JSON instables, modifiez ces valeurs dans vos profils @Qidi Plus4 :

| Paramètre | PLA Fiable | eSUN PLA-CF | PETG Anti-Échec |
| :--- | :--- | :--- | :--- |
| **Max Volumetric Speed** | 15 mm³/s | **12 mm³/s** | 8 mm³/s |
| **Vitesse paroi ext.** | 60 mm/s | **50 mm/s** (fini mat très propre) | 60 mm/s |
| **Z-hop** | Standard | **Spiral Z-hop** (évite les chocs) | **Spiral Z-hop** (évite les chocs) |
| **Ventilateur Aux.** | 20% max | **10% max** | **OFF** (évite le warping) |

### 🗺️ Localisation des Paramètres dans OrcaSlicer

Pour appliquer ces réglages dans le slicer, suivez ces chemins d'accès précis :

1.  **Max Volumetric Speed (Débit volumétrique max) :**
    *   **Chemin :** Cliquez sur l'icône d'édition (crayon) à côté de votre **Filament** sélectionné en haut à gauche ➔ Onglet **Filament** ➔ Faites défiler vers le bas jusqu'au champ **"Max volumetric speed"** ($mm^3/s$) dans la section *Performance*.
2.  **Vitesse paroi ext. (Outer Wall Speed) :**
    *   **Chemin :** Section de gauche **Process (Processus)** ➔ Onglet **Speed (Vitesse)** ➔ Recherchez la ligne **"Outer wall (Paroi externe)"** dans la sous-section *Speed* (exprimée en $mm/s$).
3.  **Z-hop (Type de levée de Z lors de la rétraction) :**
    *   **Chemin :** Cliquez sur l'icône d'édition (crayon) à côté de votre **Imprimante (Printer)** en haut à gauche ➔ Onglet **Extruder (Extrudeur)** ➔ Recherchez la catégorie **"Z-hop when retracting"** ➔ Réglez le paramètre **"Z-hop type"** sur *Normal* (Standard) ou *Spiral*.
4.  **Ventilateur Aux. (Ventilateur de refroidissement auxiliaire) :**
    *   **Chemin :** Cliquez sur l'icône d'édition (crayon) à côté de votre **Filament** sélectionné ➔ Onglet **Cooling (Refroidissement)** ➔ Cochez le champ **"Auxiliary part cooling fan"** et réglez le pourcentage (mettez à 0% ou OFF pour désactiver totalement sur le PETG).

---

## 5. Post-Traitement : Recuit (Annealing) & Macros G-Code
Le recuit stabilise les molécules et augmente la rigidité (+30%). Profitez de la chambre chauffée de la Qidi Plus 4.

### Protocoles et Consignes
| Matériau | Plateau / Chambre | Durée | Conseils |
| :--- | :--- | :--- | :--- |
| **eSUN PLA+** | 70°C / 60°C | 1h | Laisser les supports (Tree) pour éviter l'affaissement. |
| **eSUN PLA-CF** | 80°C / 55°C | 2h | Haute rigidité structurelle. Très stable dimensionnellement. |
| **PETG-CF** | 85°C / 60°C | 3h | Stable dimensionnellement. |
| **PA12-CF** | 100°C / 65°C | 8h | **Refroidissement lent** (2h porte fermée) obligatoire. |

> [!CAUTION]
> **Inserts Ruthex** : Ne faites JAMAIS de recuit sur des pièces équipées d'inserts. Le plastique ramollirait et les inserts se décentreraient. **Recuit d'abord, inserts après.**

### 🗺️ Localisation des G-codes dans le Slicer (Séquence Critique)

> [!WARNING]
> **Ne confondez pas les deux emplacements !**
> Si vous placez une macro de recuit (ex: PA12-CF à 100°C) dans les paramètres généraux de l'imprimante, elle s'exécutera également lors de vos impressions PLA, ce qui détruira totalement vos pièces PLA par surchauffe.

OrcaSlicer exécute les codes de fin de tâche selon un ordre séquentiel logique très précis :
1.  **Filament End G-code (G-code de fin du filament) :** S'exécute en tout premier. **C'est ici qu'il faut insérer vos macros de recuit.** Ainsi, chaque filament aura sa propre macro automatique (PLA+, PLA-CF, PETG-CF ou PA12-CF) qui s'exécutera uniquement si ce filament est imprimé.
2.  **Printer End G-code (G-code de fin de la machine) :** S'exécute en second, immédiatement après le code de fin du filament. **C'est ici qu'il faut insérer la macro d'Arrêt Automatique Sécurisé (M81).** Elle se chargera de refroidir la buse en sécurité et d'éteindre l'imprimante une fois que tout le cycle (impression + recuit spécifique) sera achevé.

#### 📍 Chemins d'Accès dans OrcaSlicer :

*   **Pour les Macros de Recuit (PLA+, PLA-CF, PETG-CF, PA12-CF) :**
    *   Cliquez sur l'icône d'édition (crayon) à côté de votre **Filament** sélectionné (en haut à gauche) ➔ Onglet **Advanced (Avancé)** ➔ Recherchez le champ **"Filament end G-code"** (tout en bas) ➔ Collez la macro correspondant à ce matériau spécifique.
*   **Pour la Macro d'Arrêt Automatique Sécurisé (M81) :**
    *   Cliquez sur l'icône d'édition (crayon) à côté de votre **Imprimante (Printer)** en haut à gauche ➔ Onglet **Machine G-code** ➔ Recherchez le champ **"End G-code"** ➔ Collez la macro d'arrêt sécurisé à la toute fin (après les commandes de déplacement de fin d'origine).

---
#### 1. eSUN PLA+ (Cristallisation)
```gcode
; --- G-code de fin : Recuit Direct PLA+ ---
M104 S0 ; Éteindre la buse
M140 S70 ; Plateau à 70°C (Maintien base)
M191 S60 ; Chambre à 60°C
M117 Cristallisation PLA+ (1h)...
G4 P3600000 ; Pause de 1 heure
M140 S0 M191 S0
M117 Terminé. Refroidissement porte fermée.
M84
```

### Avantages du Recuit "In-Situ" (Audit)
Il est fortement recommandé de lancer le recuit **immédiatement après l'impression** sans retirer la pièce du plateau :
- **Absence d'humidité** : Le PA12-CF n'a pas le temps d'absorber l'humidité ambiante (ce qui ferait bouillir l'eau lors du recuit).
- **Contrainte mécanique** : Le plateau agit comme un gabarit de maintien, empêchant le retrait (shrinkage) de la base de la pièce.
- **Béquille Thermique** : Pour les pièces hautes et fines, laissez les **Tree Supports** (supports arborescents). Ils servent de béquille thermique pour éviter que la pièce ne penche lors de la phase de ramollissement à 70-80°C.

#### 2. eSUN PLA-CF (Stabilisation & Rigidité)
```gcode
; --- G-code de fin : Recuit Direct PLA-CF ---
M104 S0 ; Éteindre la buse
M140 S80 ; Plateau à 80°C (Crystallisation)
M191 S55 ; Chambre à 55°C
M117 Recuit PLA-CF (2h)...
G4 P7200000 ; Pause de 2 heures
M140 S0 M191 S0
M117 Terminé. Refroidissement progressif.
M84
```

#### 3. PETG-CF (Finition & Stress-Relief)
```gcode
; --- G-code de fin : Recuit Direct PETG-CF ---
M104 S0 ; Éteindre buse
M140 S85 ; Plateau à 85°C (Transition vitreuse)
M191 S60 ; Chambre à 60°C
M117 Recuit PETG-CF (3h)...
G4 P10800000 ; Pause de 3 heures
M140 S0 M191 S0
M117 Finition. Refroidissement lent.
M84
```

#### 4. PA12-CF (Performance Maximale)
```gcode
; --- G-code de fin : Recuit Direct PA12-CF ---
M104 S0 ; Éteindre buse
M140 S100 ; Plateau à 100°C (Radiateur)
M191 S65 ; Chambre à 65°C
M117 Recuit PA12-CF (8h)...
G4 P28800000 ; Pause de 8 heures
M140 S0 M191 S0
M117 Refroidissement passif (2h)...
M84
```

#### 5. Arrêt Automatique Sécurisé (M81)
Pour éteindre l'imprimante en fin de cycle (après un recuit ou une impression simple), utilisez ce bloc. L'utilisation de `M109 R50` est **critique** pour éviter le bouchage de la buse par remontée de chaleur (Heat Creep).

```gcode
; --- G-code : Arrêt Automatique Sécurisé ---
M104 S0 ; Éteindre la chauffe buse
M140 S0 ; Éteindre la chauffe plateau
M109 R50 ; ATTENDRE refroidissement buse < 50°C (SÉCURITÉ)
M81 ; Éteindre l'imprimante (Relais PSU)
```

---

## 6. Validation et Calibration Finale
*   **Test du "Son" (PA12-CF)** : Une pièce bien recuite émet un son clair, presque métallique, lorsqu'on la tapote. Une pièce "brute" sonne plastique et mat.
*   **Retrait PLA+** : Si vous constatez un retrait de 3% après recuit, appliquez un facteur d'échelle (Scale) de **103%** dans OrcaSlicer avant l'impression finale.
*   **Maintenance Carbon** : Soufflez les poussières de carbone dans l'extrudeur tous les 2kg de filament pour éviter les glissements de roue dentée.
