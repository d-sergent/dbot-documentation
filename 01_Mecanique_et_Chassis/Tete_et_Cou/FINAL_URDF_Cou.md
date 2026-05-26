# 30 — Préparation URDF : Cou (Neck) — Naming et Axes (Fusion 360)

Ce document détaille les conventions de nommage et d'orientation à respecter dans Fusion 360 pour permettre un export URDF propre du sous-assemblage du cou du D-Bot.

> 📄 **Origine** : Cette section a été extraite de **[STUDY_Montage_Cou.md](STUDY_Montage_Cou.md)** pour en faciliter la consultation indépendante. Elle s'applique au sous-assemblage Neck v28 (2 DOF : Yaw / Pitch) utilisant 2× RS-05 et des roulements 6804-2RS.

---

## 1. Convention d'Axes : Fusion 360 vs URDF

Fusion 360 (en mode **Z-up**, réglable dans *Préférences → Conception → Orientation de modélisation par défaut*) utilise les axes suivants :

```
FUSION 360 (Z-up)              URDF (REP 103)

     Z (haut)                       Z (haut)
     │                              │
     │   Y (arrière)                │   X (avant / regard)
     │  /                           │  /
     │ /                            │ /
     └──── X (droite)               └──── Y (gauche)
```

> 📐 **Règle d'or** : Dans Fusion 360, orientez votre robot pour qu'il **regarde vers X+** (vers la droite quand vous regardez la face "AVANT" du ViewCube). Ainsi, lors de l'export URDF, l'axe X de Fusion correspondra directement à l'axe X de l'URDF (direction du regard).

| Axe Fusion 360 | Direction physique | Axe URDF | Mouvement du cou |
| :---: | :--- | :---: | :--- |
| **Z+** | Vers le haut (ciel) | **Z+** | Axe du **Yaw** (Pan) : tourner la tête gauche/droite |
| **Y+** | Vers l'arrière | **-Y** | Axe du **Pitch** (Tilt) : hocher la tête oui/non |

---

## 2. Renommage des Pièces Fusion 360 → URDF

En URDF, chaque pièce rigide s'appelle un **link**, et chaque articulation un **joint**. Les pièces qui ne bougent pas l'une par rapport à l'autre doivent être **fusionnées en un seul link** (ou reliées par un joint `fixed`).

### 2.1 Règles de nommage URDF

1. **Tout en `snake_case`** (minuscules + underscores) : `neck_pitch_link`, pas `NeckPitchLink`
2. **Préfixer par la zone du corps** : `neck_`, `head_`, `torso_`
3. **Suffixer les links par `_link`** et les joints par `_joint`**
4. **Pas de numéros de version** : `neck_pitch_motor`, pas `robstride05 v1:2`
5. **Pas de caractères spéciaux** : ni tirets `-`, ni accents, ni espaces, ni points

### 2.2 Tableau de correspondance (assemblage Neck v28)

| Nom actuel Fusion 360 | Rôle mécanique | Nom URDF (Link) | Remarque |
| :--- | :--- | :--- | :--- |
| `robstride05 v1:1` | Moteur Pan (Yaw) | `neck_yaw_motor` | Fusionné dans `neck_yaw_link` |
| `U-Pan v15:1` | Bracket en U (Pan→Tilt) | `neck_yaw_bracket` | Fusionné dans `neck_yaw_link` |
| `robstride05 v1:2` | Moteur Tilt (Pitch) | `neck_pitch_motor` | Fusionné dans `neck_pitch_link` |
| `Tilt v14:1` | Bracket du Tilt (Pitch) | `neck_pitch_bracket` | Fusionné dans `neck_pitch_link` |
| `6804_2rs v1:1` | Roulement 6804-2RS (Yaw) | `neck_yaw_bearing` | Joint `fixed` vers `neck_yaw_link` |
| `6804_2rs v1:2` | Roulement 6804-2RS (Pitch) | `neck_pitch_bearing` | Joint `fixed` vers `neck_pitch_link` |

> 💡 **"Fusionné" signifie** : dans l'URDF, ces pièces font partie du **même link** (même corps rigide). Par exemple, le moteur Pan (`robstride05 v1:1`) et le bracket U-Pan (`U-Pan v15:1`) bougent ensemble → ils forment un seul link appelé `neck_yaw_link`. On ne crée **pas** de joint entre eux.

> 🛠️ **Cas particulier des roulements** : Un roulement entier (bague intérieure + bague extérieure) doit être placé dans **un seul link**. La règle est de le placer dans le composant **parent (fixe)**, c'est-à-dire celui qui supporte la bague extérieure (le carter). La masse du roulement est ainsi fusionnée avec celle du parent, ce qui ne change rien à la dynamique de simulation. Visuellement, le cylindre de révolution parfait ne trahit pas son appartenance au corps fixe dans RViz/Isaac.

---

## 3. Chaîne Cinématique URDF du Cou

Arbre parent-enfant complet à définir dans l'URDF :

```
torso_link
  │
  └── neck_yaw_joint (type: revolute, axe: Z)
        │
        └── neck_yaw_link   ← [robstride05 v1:1 + U-Pan bracket + roulement 6804-2RS (Yaw)]
              │
              └── neck_pitch_joint (type: revolute, axe: Y)
                    │
                    └── neck_pitch_link   ← [robstride05 v1:2 + Tilt bracket + roulement 6804-2RS (Pitch)]
                          │
                          └── head_fixed_joint (type: fixed)
                                │
                                └── head_link   ← [tête + capteurs]
```

---

## 4. Définition des Joints (DOF)

Chaque joint `revolute` doit spécifier son **axe de rotation**, ses **limites angulaires** et son **effort maximal** :

| Joint URDF | Type | Axe | Limites (rad) | Limites (deg) | Effort max (N.m) | Vitesse max (rad/s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `neck_yaw_joint` | revolute | `0 0 1` (Z) | [-1.57, 1.57] | ±90° | 5.5 | 3.14 |
| `neck_pitch_joint` | revolute | `0 1 0` (Y) | [-0.79, 0.79] | ±45° | 5.5 | 3.14 |

> ⚠️ **Note sur la vitesse maximale** : Bien que les moteurs RS-05 puissent physiquement atteindre 12,57 rad/s (120 rpm) à vide, la vitesse maximale opérationnelle dans l'URDF est volontairement bridée à **3,14 rad/s (180°/s)** pour les axes **Yaw** et **Pitch**. Cela permet de limiter les efforts d'inertie sur la structure mécanique lors des arrêts brusques, de préserver la durée de vie du cou et d'éviter le flou de bougé cinétique sur la caméra OAK-D Pro. Les profils de trajectoire quotidiens seront régulés en logiciel à 1,57 rad/s (90°/s) pour un rendu naturel.

> ⚠️ Les axes `0 0 1` (Yaw/Z) et `0 1 0` (Pitch/Y) sont les directions dans le référentiel du link **parent**. Vérifiez après export que chaque axe correspond bien au mouvement attendu. Si un mouvement est inversé, changer le signe (ex: `0 0 -1`).

---

## 5. Workflow d'Export Fusion 360 → URDF

1. **Renommer les pièces** dans Fusion 360 selon le tableau §2.2 (clic droit → Renommer dans le navigateur).
2. **Vérifier l'orientation** : le robot doit regarder vers X+ dans Fusion (face AVANT du ViewCube à droite).
3. **Utiliser le plugin URDF Exporter** (Autodesk ou Fusion2URDF communautaire).
4. **Vérifier le fichier `.urdf`** généré : contrôler que les axes `<axis xyz="..."/>` correspondent bien à la colonne "Axe URDF" du tableau §1.
5. **Tester dans RViz** : charger le modèle, actionner manuellement chaque joint via `joint_state_publisher_gui` et vérifier la direction de rotation.
6. **Ajuster les signes d'axe** si nécessaire dans le fichier URDF directement.

---

## 6. Résumé des Links URDF à créer

| Link URDF | Pièces Fusion fusionnées | Description |
| :--- | :--- | :--- |
| `torso_link` | Structure du torse (existant) | Point d'ancrage fixe |
| `neck_yaw_link` | `robstride05 v1:1` + `U-Pan v15:1` + `6804_2rs v1:1` | Tourne en Yaw (gauche/droite) |
| `neck_pitch_link` | `robstride05 v1:2` + `Tilt v14:1` + `6804_2rs v1:2` | Tourne en Pitch (oui/non) |
| `head_link` | Crâne, capteurs, boîtier électronique | La tête elle-même |

---

*Dernière mise à jour : Mars 2026. Document extrait de [STUDY_Montage_Cou.md](STUDY_Montage_Cou.md).*
