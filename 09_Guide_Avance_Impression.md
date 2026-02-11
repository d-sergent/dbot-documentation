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

## 2. Calibration de Fiabilité (OrcaSlicer)
Pour du filament générique sur la Qidi Plus 4, la calibration manuelle est indispensable pour éviter les "blobs" et les clics d'extrudeur.

### Calibration du Débit (Flow Rate)
*   **Menu** : *Calibration > Flow Rate > Pass 1*.
*   **Objectif** : Repérez la surface la plus lisse sans bourrelets.
*   **Calcul** : $Flow_{New} = Flow_{Current} \times (100 + Modificateur) / 100$.

### Limite de Débit Volumétrique (Le verrou de sécurité)
C'est le réglage le plus critique pour la Plus 4.
*   **PLA Générique** : Limitez à **15 mm³/s**.
*   **PETG Générique** : Limitez à **8 mm³/s** pour éviter l'accumulation sur la buse.
*   **Action** : Réduisez la valeur par défaut de 20% pour garantir une fiabilité totale sur des impressions de longue durée.

### Pressure Advance (Coins nets)
*   **Valeurs typiques (Direct Drive)** : 
    *   PLA : **0.02 - 0.04**
    *   PETG : **0.04 - 0.06**

---

## 3. Profils JSON Optimisés (Réglages "Safe")
Plutôt que d'importer des fichiers JSON instables, modifiez ces valeurs dans vos profils @Qidi Plus4 :

| Paramètre | PLA Fiable | PETG Anti-Échec |
| :--- | :--- | :--- |
| **Max Volumetric Speed** | 15 mm³/s | 8 mm³/s |
| **Vitesse paroi ext.** | 60 mm/s | 60 mm/s |
| **Z-hop** | Standard | **Spiral Z-hop** (évite les chocs) |
| **Ventilateur Aux.** | 20% max | **OFF** (évite le warping) |

---

## 4. Post-Traitement : Recuit (Annealing) & Macros G-Code
Le recuit stabilise les molécules et augmente la rigidité (+30%). Profitez de la chambre chauffée de la Qidi Plus 4.

### Protocoles et Consignes
| Matériau | Plateau / Chambre | Durée | Conseils |
| :--- | :--- | :--- | :--- |
| **eSUN PLA+** | 70°C / 60°C | 1h | Laisser les supports (Tree) pour éviter l'affaissement. |
| **PETG-CF** | 85°C / 60°C | 3h | Stable dimensionnellement. |
| **PA12-CF** | 100°C / 65°C | 8h | **Refroidissement lent** (2h porte fermée) obligatoire. |

> [!CAUTION]
> **Inserts Ruthex** : Ne faites JAMAIS de recuit sur des pièces équipées d'inserts. Le plastique ramollirait et les inserts se décentreraient. **Recuit d'abord, inserts après.**

### Macros G-Code (Recuit Automatique)
Vous pouvez enregistrer ces scripts en `.gcode` sur votre clé USB pour lancer un cycle de recuit indépendant.

```gcode
; --- Macro Recuit PA12-CF (Exemple de saturation thermique) ---
G28 ; Home
M106 S0 ; Fan Off
M140 S100 ; Plateau 100°C (Radiateur)
M191 S65 ; Chambre 65°C
M117 Recuit PA12-CF (8h)...
G4 P28800000 ; Pause 8h
M140 S0 ; Bed Off
M191 S0 ; Chamber Off
M117 Refroidissement passif...
```

---

## 5. Validation et Calibration Finale
*   **Test du "Son" (PA12-CF)** : Une pièce bien recuite émet un son clair, presque métallique, lorsqu'on la tapote. Une pièce "brute" sonne plastique et mat.
*   **Retrait PLA+** : Si vous constatez un retrait de 3% après recuit, appliquez un facteur d'échelle (Scale) de **103%** dans OrcaSlicer avant l'impression finale.
*   **Maintenance Carbon** : Soufflez les poussières de carbone dans l'extrudeur tous les 2kg de filament pour éviter les glissements de roue dentée.
