# 33 — Guide : Test Multi-Moteurs et Câblage CAN Banc (Cou RS-05)

> *Document créé Avril 2026 — Suite directe de la Doc 32 (Configuration ID, Zéro & Limites). À réaliser avant l'intégration Jetson/ROS2.*

Ce guide couvre le test de deux moteurs RS-05 (Pan+Tilt du cou) fonctionnant **simultanément** sur un même bus CAN, le câblage complet du bus avec les bons câbles, et les étapes de validation avant de passer à l'intégration logicielle.

---

## Prérequis (Doc 32 terminée)

- [x] Moteur Pan : **ID=1**, Zéro calibré, limites ±0.698 rad flashées.
- [x] Moteur Tilt : **ID=2**, Zéro calibré, limites ±0.524 rad flashées.

---

## 1. Câblage Puissance (24V) — 2 Moteurs en Parallèle

Les deux moteurs alimentés **en parallèle** sur une seule Wanptek. Les câbles de puissance et les câbles CAN sont **totalement indépendants**.

### Réglage Wanptek (2 moteurs RS-05)

| Paramètre | Valeur |
| :--- | :--- |
| **Tension** | 24.0V |
| **Limite courant** | **3.0A** (1.5A × 2 moteurs avec marge) |
| **Mode OCP** | ✅ Activé |

> En holding (Enable sans mouvement), les 2 RS-05 tirent ~200–400 mA au total. Sur un mouvement de tête modéré, comptez 500 mA à 1.5A au total. La limite à 3A vous protège des court-circuits sans couper intempestivement.

### Schéma Puissance

```
Wanptek DPS605U
  (+) 24V ──────────┬──── XT30 Mâle ──→ [Pan  ID=1]
                    └──── XT30 Mâle ──→ [Tilt ID=2]
  (-) GND ──────────┬──── XT30 Mâle ──→ [Pan  ID=1]
                    └──── XT30 Mâle ──→ [Tilt ID=2]
```

> Utilisez deux câbles XT30 (ou XT30 → bornes à vis) pour relier chaque moteur à la Wanptek.

---

## 2. Câblage CAN (Bus Partagé) — Daisy-Chain

Le CAN est un **bus différentiel partagé**. Les deux moteurs sont branchés **en chaîne** sur les trois fils GND/CANH/CANL. Ce n'est **pas une connexion en étoile (Y)** — les dérivations dégradent le signal à 1 Mbps.

### 2.1 Type de Câble CAN — Spécifications Requises

> [!IMPORTANT]
> Le câble CAN n'est **pas** un câble USB ni un câble Ethernet standard. Utiliser le mauvais câble provoque des erreurs "Bus Off" ou une communication instable à haute fréquence.

Le câble idéal pour le bus CAN-to-USB du D-Bot est une **paire torsadée blindée** (STP — Shielded Twisted Pair) :

| Critère | Spécification |
| :--- | :--- |
| **Type** | Paire torsadée blindée (STP) |
| **Impédance caractéristique** | **120 Ω** (correspondance avec les terminaisons du bus) |
| **Section conducteurs** | **0.22 mm²** (24 AWG) à 0.34 mm² (22 AWG) |
| **Blindage** | Feuillard aluminium (drain wire) ou tresse |
| **Couleurs recommandées** | CANH = Jaune, CANL = Vert, GND = Noir |
| **Longueur maxi (banc)** | 2 m sans problème à 1 Mbps |
| **Longueur maxi (robot)** | 3 m max par segment entre nœuds |

#### Câbles Acceptables pour le Banc (Disponibles en France)

| Produit | Référence / Nom | Prix | Lien |
| :--- | :--- | :---: | :--- |
| **Câble CAN dédié** | Belden 9841, Alpha 5902 (câble 120Ω STP) | ~3–5 €/m | Mouser, RS Components |
| **Câble réseau S/FTP Cat7** | N'importe quel Cat7 S/FTP | ~1–2 €/m | Amazon, LDLC |
| **Câble Holybro CAN** | Holybro JST-GH CAN Cable | ~8–12 € | Holybro.com, AliExpress |
| **Câble JST-GH robotique** | Silicone 24AWG STP (Pimoroni, SparkFun) | ~5–15 € | SparkFun, AliExpress |

> [!TIP]
> Pour le **banc de test**, un câble S/FTP Cat7 dépinné avec terminaux Dupont ou JST suffit amplement sur des longueurs < 50 cm. Pour l'intégration définitive dans le robot, privilégiez des câbles Holybro avec connecteurs JST-GH moulés.

#### Câbles à Éviter

| Type de Câble | Pourquoi c'est problématique |
| :--- | :--- |
| Câble USB simple | Non différentiel, pas torsadé → reflections |
| Câble non blindé (UTP simple) | Sensible aux perturbations des moteurs |
| Câble en "Y" (dérivation) | Stub length > 30 cm → oscillations à 1 Mbps |
| Câble téléphonique RJ11 | Impédance incorrecte (600Ω vs 120Ω) |

---

### 2.2 Topologie de Câblage CAN — Daisy-Chain

```
[Module de debug CAN-to-USB]
     │  (bornes à vis)
     ├── GND  (fil noir)  ──────────────┬─────────────────────┐
     ├── CANH (fil jaune) ──────────────┼──────────┐          │
     └── CANL (fil vert)  ──────────────┼──────────┼──────┐   │
                                        │          │      │   │
                               [Pan ID=1 - JST-GH 4-pin] │   │
                               Pin 1: CANH ────────┘      │   │
                               Pin 2: CANL ───────────────┘   │
                               Pin 3: GND  ───────────────────┘
                               Pin 4: BOOT → NC (non connecté)
                                        │
                                [Fil de liaison vers Tilt]
                                        │
                               [Tilt ID=2 - JST-GH 4-pin]
                               Pin 1: CANH
                               Pin 2: CANL
                               Pin 3: GND
                               Pin 4: BOOT → NC
                                        │
                               [Fin du bus — Terminaison 120Ω]
                               → Résistance 120Ω entre CANH et CANL
                                 (ou résistance intégrée du moteur si disponible)
```

### 2.3 Terminaisons 120Ω — Règle des 2 Extrémités

Un bus CAN correctement câblé a **exactement 2 résistances de terminaison de 120Ω**, une à chaque extrémité physique du bus.

| Extrémité | Composant | Terminaison |
| :--- | :--- | :---: |
| **Début du bus** | Module de debug CAN-to-USB | ✅ SW2=ON (intégrée) |
| **Fin du bus** | Dernier moteur en bout (Tilt ID=2) | ✅ À ajouter |

**Comment terminer le côté moteur :**

- **Option A (recommandée)** : Souder une résistance CMS 120Ω 0805 directement entre CANH (Pin 1) et CANL (Pin 2) du connecteur JST du Tilt, sur un petit PCB ou un connecteur adapté.
- **Option B (dépannage rapide)** : Insérer une résistance 120Ω traversante entre deux fils Dupont femelles branchés sur CANH et CANL.
- **Option C** : Certains câbles Holybro ont un bouchon de terminaison optionnel à clipper en bout de bus.

> **Vérification** : Avec les deux moteurs hors tension, mesurer au multimètre entre CANH et CANL depuis les bornes du module de debug → vous devez lire **environ 60Ω** (120Ω // 120Ω = 60Ω en parallèle). Si vous lisez >100Ω, une terminaison manque. Si vous lisez <40Ω, il y a un court-circuit.

---

## 3. Procédure de Test — 2 Moteurs Simultanés

### Checklist Pré-Test

- [ ] Wanptek : 24.0V, limite 3.0A, OCP activé
- [ ] Câble CAN en daisy-chain Pan → Tilt monté
- [ ] Terminaisons 120Ω aux deux extrémités (SW2=ON sur le module de debug + résistance côté Tilt)
- [ ] Module de debug CAN-to-USB : **SW1=OFF** (pas en mode bootloader), **SW2=ON**
- [ ] USB du module de debug branché sur le PC Windows avec MotorStudio

### Séquence d'Allumage

1. Allumer la Wanptek (vérifier 24.0V, limite 3A, OCP).
2. Brancher les 2 câbles XT30 de puissance (Pan + Tilt).
3. Brancher le câble USB du module de debug.
4. Lancer MotorStudio → **"Refresh COM"** → Sélectionner le port COM → **"Open COM"**.
5. Cliquer **"Detection Devices"** → **Les deux IDs 1 et 2 doivent apparaître simultanément**.

> Si un seul ID apparaît : vérifier la continuité du câble CAN entre Pan et Tilt (fil arraché ?), et vérifier que le moteur absent est bien sous tension.

### Test Fonctionnel Séquentiel

**Test Pan (ID=1) :**
1. Sélectionner ID=1 dans MotorStudio → **Enable**.
2. Envoyer `pos = +0.3 rad` (Kp=5, Kd=0.5) → La tête tourne légèrement à gauche.
3. Retour `pos = 0.0 rad` → La tête revient au centre.
4. **Disable** ID=1.

**Test Tilt (ID=2) :**
1. Sélectionner ID=2 → **Enable**.
2. Envoyer `pos = +0.2 rad` → La tête s'incline légèrement en avant.
3. Retour `pos = 0.0 rad` → Retour au centre.
4. **Disable** ID=2.

**Test Simultané :**
1. Enable ID=1 **et** ID=2 en même temps.
2. Envoyer `pos = +0.2 rad` aux deux → Mouvement combiné Pan+Tilt.
3. Vérifier que les deux moteurs bougent sans perturbation mutuelle sur le bus.

---

## 4. Étapes Suivantes (Post-Validation Banc)

Une fois les deux IDs validés simultanément sur MotorStudio, la configuration matérielle est terminée.

### Étape A — Intégration Jetson via InnoMaker USB2CAN-C

1. Remplacer le module de debug CAN-to-USB par l'**InnoMaker USB2CAN-C** (interface Linux/ROS2 — voir Doc 04 §2).
2. Configurer le bus CAN sous Linux :
```bash
sudo ip link set can0 up type can bitrate 1000000
ip link show can0   # vérifier l'état
candump can0        # écouter le trafic brut (les 2 moteurs doivent envoyer)
```
3. Vérifier que les deux nœuds (ID 1 et 2) transmettent des trames.

### Étape B — Intégration ROS2 (Contrôleur Cou)

1. Lancer le nœud RobStride ROS2 :
```bash
ros2 run robstride_driver robstride_node --ros-args -p can_channel:=can0
```
2. Vérifier les topics :
```bash
ros2 topic list    # doit montrer /neck/pan/cmd et /neck/tilt/cmd
ros2 topic echo /neck/pan/state
```

### Étape C — Test Stabilisation Regard (OAK-D Pro)

1. Connecter l'OAK-D Pro (USB3 → Jetson).
2. Lancer le nœud de suivi de visage (Isaac ROS FaceDetect ou MediaPipe).
3. Valider que le cou suit la cible visuelle en temps réel sans oscillation (ajuster Kd si besoin).

### Étape D — Intégration URDF ROS2

Reporter les limites du Doc 32 §3.2 dans le fichier URDF du robot pour que MoveIt2 puisse planifier des trajectoires valides.

---

## Récapitulatif des Câblages

| Bus | Type de câble | Connecteurs | Terminaisons |
| :--- | :--- | :--- | :--- |
| **Puissance (24V)** | Silicone 16-18 AWG | XT30 mâle/femelle | Aucune |
| **CAN (data)** | STP 24AWG 120Ω (S/FTP Cat7 acceptable) | JST-GH 4-pin + bornes à vis | 2× 120Ω (module debug + Tilt) |
| **USB (PC/Jetson)** | USB-A → USB-C standard | standard | N/A |

---
*Document créé Avril 2026 — Complément à la Doc 32 ; précède l'intégration Jetson/ROS2.*
