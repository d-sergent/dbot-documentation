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

## 2. Profils d'Impression Qidi Plus 4
Paramètres validés pour une buse Acier Trempé 0.4mm.

| Paramètre | PETG-CF (Structure) | PA12-CF (Mécanique/Chaleur) |
| :--- | :--- | :--- |
| **Buse** | 250°C - 260°C | 280°C - 300°C |
| **Plateau** | 70°C - 80°C (PEI Texturé) | 80°C - 100°C (Colle Magigoo PA requise) |
| **Chambre Active** | 40°C - 50°C (Optionnel) | **60°C - 70°C** (Indispensable anti-warping) |
| **Ventilation** | 20% - 50% | **0% (Off)** ou 10% max pour ponts |
| **Vitesse** | 200 - 300 mm/s | 60 - 100 mm/s (Liaison inter-couches) |
| **Rétraction** | Standard | Faible (1.0 - 2.0 mm) pour éviter bouchage |

## 3. Stratégie de Supports (Détachement Facile)
Le carbone rend les supports cassants et difficiles à retirer s'ils fusionnent.
**Recommandation** : Utiliser "Tree Slim" (Arborescent fin) pour économiser la matière coûteuse.

### Paramètres d'Interface (Z-Distance)
*   **PETG-CF** : Top Z Distance = **0.20 mm - 0.24 mm**.
*   **PA12-CF** : Top Z Distance = **0.25 mm - 0.28 mm** (Le Nylon colle plus, augmentez l'écart).

### Astuces Pro
*   **Interface Dense** : 3 à 4 couches d'interface, Espacement 0.2mm (Motif Rectiligne).
*   **Support de Support** : Pour les grandes surfaces planes (sous le torse), activez les interfaces intermédiaires avec un motif **Giroïde** pour le corps du support.
*   **Retrait à Froid** : Pour le PA12-CF, n'essayez pas de retirer les supports à chaud. Attendez le refroidissement complet, le matériau deviendra cassant et "sautera" nettement.

## 4. Maintenance "Spécial Carbone"
*   **Buse** : L'acier trempé s'use aussi ! Vérifiez le diamètre toutes les 2kg.
*   **Extrudeur** : Soufflez les poussières de carbone dans les engrenages d'entraînement régulièrement (risque de glissement).
