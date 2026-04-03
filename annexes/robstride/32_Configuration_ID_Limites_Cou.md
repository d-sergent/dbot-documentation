# 32 — Guide : Configuration ID, Zéro et Limites (Cou RS-05)

> *Document créé Avril 2026 — Complément à la Doc 29 (Montage Cou) et Doc 31 (Debug).*

Ce document détaille la procédure de configuration logicielle des deux moteurs **RobStride RS-05** du cou (Pan & Tilt) pour garantir une communication stable et une sécurité mécanique via des bornes logicielles.

---

## 1. Attribution des IDs CAN (Priorité 1)

Par défaut, tous les moteurs RobStride sortent d'usine avec l'**ID=1**. Pour faire cohabiter les deux moteurs du cou sur le même bus CAN sans collision, ils doivent avoir des IDs uniques.

### Stratégie recommandée
| ID | Fonction | Axe |
| :---: | :--- | :--- |
| **1** | **Pan** | Roll du cou (inclinaison latérale) |
| **2** | **Tilt** | Pitch du cou (inclinaison avant/arrière) |

### Procédure de changement (UN moteur à la fois)
**⚠️ IMPORTANT : Ne branchez qu'un seul moteur physiquement au module EL05 pendant cette phase.**

1. Brancher uniquement le moteur **Pan**.
2. Dans MotorStudio → **Detection Devices** → l'ID 1 apparaît.
3. Aller dans les réglages du moteur → Champ **"Motor ID"** (ou CAN ID).
4. Saisir **1** (déjà par défaut, mais permet de valider la procédure).
5. Cliquer **"Save"** ou **"Write to Flash"**.
6. Débrancher Pan, brancher uniquement **Tilt**.
7. Detection Devices → l'ID 1 apparaît (ID d'usine).
8. Changer le Motor ID en **2**.
9. Cliquer **"Save"** ou **"Write to Flash"**.
10. **Test final** : Relier les deux moteurs au bus via un connecteur en T ou en chaine → les deux IDs (1 et 2) doivent apparaître simultanément lors du scan.

---

## 2. Calibration du Zéro Mécanique

Le "Zéro" doit correspondre exactement à la **position neutre** du robot (regard horizontal, tête centrée).

1. Mettre le robot sous tension (Wanptek 24V).
2. Positionner manuellement (moteurs en **Disable**) la tête dans sa position de référence idéale.
3. Dans MotorStudio :
   - Sélectionner ID=1 (Pan) → Bouton **"Set Zero"** → **Save/Write to Flash**.
   - Sélectionner ID=2 (Tilt) → Bouton **"Set Zero"** → **Save/Write to Flash**.
4. Vérifier : en cliquant sur **"Enable"**, le moteur doit rester immobile à cette position (le holding torque s'active sur 0.0 rad).

---

## 3. Définition des Bornes de Rotation (Limits)

Pour éviter que les câbles ne s'arrachent ou que la structure ne vienne buter mécaniquement, nous définissons des limites logicielles à trois niveaux.

### Niveau 1 — Bornes Firmware (Hard Limits)
Si votre version de firmware (ex: **0.5.0.9**) le permet, saisissez les valeurs directement dans les registres du moteur via MotorStudio.

**Valeurs cibles :**
- **Pan (Roll)** : ±40° (soit ±0.698 rad)
- **Tilt (Pitch)** : ±30° (soit ±0.524 rad)

| Registre / Champ | Valeur Pan (ID 1) | Valeur Tilt (ID 2) | Unité |
| :--- | :---: | :---: | :--- |
| **Min Position** (Limit Low) | -0.698 | -0.524 | Radians |
| **Max Position** (Limit High) | +0.698 | +0.524 | Radians |

> **Action** : Une fois saisies, cliquer impérativement sur **"Save"**. Le moteur refusera désormais toute commande `pos` au-delà de ces valeurs, même en cas de bug du contrôleur principal.

---

### Niveau 2 — Bornes URDF (Soft Limits)
Ces limites doivent être reportées dans le fichier URDF du robot (voir Doc 30) pour que ROS2 puisse planifier des trajectoires valides.

```xml
<!-- Extrait URDF - Joint Pan -->
<joint name="neck_pan" type="revolute">
  <limit lower="-0.698" upper="0.698" effort="5.5" velocity="10.0"/>
</joint>

<!-- Extrait URDF - Joint Tilt -->
<joint name="neck_tilt" type="revolute">
  <limit lower="-0.524" upper="0.524" effort="5.5" velocity="10.0"/>
</joint>
```

---

### Niveau 3 — Butées Mécaniques (Safety)
En dernier recours, des butées physiques (plots en aluminium ou impressions 3D renforcées) doivent être présentes à ±45° (Pan) et ±35° (Tilt). Elles ne doivent jamais être atteintes en fonctionnement normal, mais servent de "fusible" mécanique en cas de défaillance totale de l'électronique.

---

## 4. Maintenance Post-Flash

> [!CAUTION]
> **Rappel Critique** : Toute mise à jour de firmware (Flash) efface le Zéro et peut réinitialiser l'ID à 1.
> **Toujours suivre cet ordre après un flash :**
> 1. Vérifier/Fixer l'ID
> 2. Calibrer le Zéro
> 3. Ré-écrire les Bornes Min/Max
