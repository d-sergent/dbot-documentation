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
  (+) 24V ──────────┬──── XT30 (+) ──→ [Pan  ID=1]
                    └──── XT30 (+) ──→ [Tilt ID=2]
  (-) GND ──────────┬──── XT30 (-) ──→ [Pan  ID=1]
                    └──── XT30 (-) ──→ [Tilt ID=2]
                    └────────────── GND borne à vis [module de debug]
```

> Le GND commun du module de debug est relié **directement** à la borne (-) de la Wanptek, pas via un fil CAN.

---

## 2. Câblage CAN (Bus Partagé)

### 2.0 Nombre de Ports CAN par Moteur — Tableau de Référence

> [!IMPORTANT]
> **Constat terrain (Avril 2026)** : Le RS-05 est le **seul moteur RobStride du D-Bot à n'avoir qu'un seul port CAN**. Tous les autres modèles (RS-02, RS-03, RS-04, RS-06) disposent de **2 ports CAN** (entrée + sortie) permettant un daisy-chain natif.

| Modèle | Ports CAN | Topologie | Utilisation D-Bot |
| :--- | :---: | :--- | :--- |
| **RS-02** | 2 | Daisy-chain natif | Cheville, Mains |
| **RS-03** | 2 | Daisy-chain natif | Hanche, Épaule |
| **RS-04** | 2 | Daisy-chain natif | Hanche, Genou |
| **RS-05** | **1** | **Y au module de debug** | Cou (Pan + Tilt) |
| **RS-06** | 2 | Daisy-chain natif | Coude, Cheville |

---

### 2.1 Topologie pour le Cou RS-05 (1 port = Y au départ)

Puisque le RS-05 n'a qu'un seul port CAN, on ne peut pas faire de chaîne de moteur à moteur. La solution est un **Y au niveau des bornes à vis du module de debug** : les deux moteurs sont branchés en parallèle directement depuis les bornes.

```
[Module de debug CAN-to-USB]
     | (bornes à vis)
     |
     +-- GND (1 fil court) ---------------------> borne (-) Wanptek
     |
     +-- CANH (rouge) ---+------> fil rouge CAN [Pan  ID=1]
     |                   |
     |                   +------> fil rouge CAN [Tilt ID=2]
     |
     +-- CANL (noir) ----+------> fil noir  CAN [Pan  ID=1]
                         |
                         +------> fil noir  CAN [Tilt ID=2]
```

> **Pourquoi un Y est acceptable ici** : La règle "pas de Y" s'applique aux bus CAN longs (> 30 cm de dérivation) avec de nombreux nœuds. Pour 2 moteurs de cou à moins de 50 cm, un Y aux bornes du module de debug fonctionne parfaitement à 1 Mbps.

---

### 2.2 Topologie pour les Autres Moteurs (2 ports = Daisy-Chain Natif)

Pour tous les autres moteurs du D-Bot (RS-02, RS-03, RS-04, RS-06), la chaîne est directe d'un moteur à l'autre :

```
[Module de debug / InnoMaker]
CANH ----> [Moteur A - port 1] ----> [Moteur B - port 1] ----> [Moteur C - port 1]
CANL ----> [Moteur A - port 1] ----> [Moteur B - port 1] ----> [Moteur C - port 1]

                  [Moteur A - port 2]  [Moteur B - port 2]  [Moteur C - port 2]
                  (vers Moteur B)       (vers Moteur C)       Fin de bus (120Ω)
```

Châque moteur possède 2 ports identiques. Vous entrez par l'un et sortez par l'autre. Le dernier moteur en bout de chaîne a son deuxième port muni d'une résistance 120Ω (ou laissé ouvert si la terminaison est déjà intégrée dans le moteur).

---

### 2.3 Type de Câble CAN — Ce qu'il Faut Acheter

> [!IMPORTANT]
> Les moteurs RobStride RS-05 sont livrés avec un câble CAN **2 fils uniquement** (fil rouge = CANH, fil noir = CANL). Il n'y a **pas de fil GND séparé** dans le câble CAN. Le GND est assuré par le câble d'alimentation XT30 noir.

#### Pour le Banc Prototype (Disponible sur Amazon.fr - Livré demain)

**Option 1 — La plus rapide : Démonter un câble Ethernet Cat6/Cat7**
Un câble Ethernet S/FTP Cat7 contient 4 paires torsadées blindées. Vous n'avez besoin que d'**une seule paire** (2 fils torsadés) pour CANH + CANL.

| Recherche Amazon.fr | Prix | Notes |
| :--- | :---: | :--- |
| "câble ethernet Cat7 S/FTP 1m" | 3–5 € | Couper, dégainer, utiliser 1 paire |
| "câble ethernet RJ45 plat Cat6" | 2–4 € | Éviter le plat (non torsadé) |

> Choisissez **Cat7 S/FTP** (pas Cat5 UTP) : les conducteurs sont torsadés par paire et blindés individuellement = parfait pour le CAN.

**Option 2 — Câble servo RC 2 fils (le plus simple à utiliser)**
Ces câbles ont des bouts dénués prêts à s'insérer dans les bornes à vis du module de debug.

| Recherche Amazon.fr | Prix | Notes |
| :--- | :---: | :--- |
| "servo extension lead 30cm" | 5–8 €/pack 10 | Fils fins, pas blindés, OK < 50cm |
| "câble biplaire torsadé 26AWG" | 5–10 €/5m | Plus professionnel |

**Option 3 — Achat définitif : Câble STP dédié CAN**
Pour la production finale dans le robot :

| Produit | Enseigne | Prix |
| :--- | :--- | :---: |
| Belden 9841 (STP 2×24AWG 120Ω) | RS Components.fr / Mouser.fr | ~2–3 €/m |
| Alpha Wire 5902 | Mouser.fr | ~2 €/m |
| Câble CAN Holybro (avec connecteurs JST-GH) | MyBotShop.de | ~4–6 €/câble |

#### Blindé ou pas ?

| Cas | Blindage |
| :--- | :---: |
| Cou (2 moteurs, < 50 cm, prototype) | ❌ Inutile |
| Bras (4–6 moteurs, < 80 cm) | ❌ Facultatif |
| Jambes (6–8 moteurs, 80–150 cm, RS-04 à pleine puissance) | ✅ Recommandé |
| Production définitive robot complet | ✅ Standard |

---

### 2.4 Terminaisons 120Ω — Règle des 2 Extrémités

Un bus CAN correctement câblé a **exactement 2 résistances de terminaison de 120Ω**, une à chaque extrémité physique du bus.

| Extrémité | Composant | Terminaison |
| :--- | :--- | :---: |
| **Début du bus** | Module de debug CAN-to-USB | ✅ SW2=ON (intégrée) |
| **Fin du bus** | Dernier moteur en bout (Tilt ID=2) | ✅ À ajouter |

**Comment terminer le côté dernier moteur :**

- **Option A (recommandée)** : Souder une résistance traversante 120Ω entre les 2 fils CANH et CANL à l'entrée du connecteur du dernier moteur (côté libre).
- **Option B (dépannage rapide)** : Insérer une résistance 120Ω entre deux fils Dupont femelles branchés sur CANH et CANL.

> **Vérification** : Avec tous moteurs hors tension, mesurer au multimètre entre CANH et CANL depuis les bornes du module de debug → vous devez lire **environ 60Ω** (120Ω // 120Ω = 60Ω). Si > 100Ω : une terminaison manque. Si < 40Ω : court-circuit.

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
