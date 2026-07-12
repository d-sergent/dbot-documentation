# 43 — Tests Cou RS-05 : Python Validé & Roadmap ROS2

> *Ce document fait suite à la Doc 42 (Configuration CAN InnoMaker) et à la Doc 33 §4 (Étapes Post-Validation Banc). Il regroupe tous les scripts Python validés en conditions réelles et décrit la roadmap d'intégration ROS2.*

---

## Prérequis (Docs 32 & 42 terminées)

- [x] Moteur Pan : **ID=1**, Zéro calibré, limites ±1.396 rad flashées en firmware
- [x] Moteur Tilt : **ID=2**, Zéro calibré, limites ±0.524 rad flashées en firmware
- [x] InnoMaker USB2CAN-C détecté (`lsusb` → `ID 1d50:606f`)
- [x] Interface `can1` UP à 1 Mbps (`sudo ip link set can1 type can bitrate 1000000 && sudo ip link set can1 up`)
- [x] Librairie Python installée (`pip3 install robstride`)

---

## Constantes de Référence — Limites Mécaniques du Cou

> [!IMPORTANT]
> Ces limites sont définies dans la **Doc 32 §3** et doivent être respectées dans **tous les scripts et nœuds ROS2** liés au cou. Elles correspondent aux contraintes mécaniques de câblage et de structure.

```python
import math

# ── Limites mécaniques cou (Doc 32 §3) ────────────────────
PAN_MIN_RAD  = -1.396   # Pan  ID:1 — -80°
PAN_MAX_RAD  =  1.396   # Pan  ID:1 — +80°
TILT_MIN_RAD = -0.524   # Tilt ID:2 — -30°
TILT_MAX_RAD =  0.524   # Tilt ID:2 — +30°

def clamp_pan(angle_rad: float) -> float:
    """Force la consigne Pan dans les limites mécaniques [-40°, +40°]."""
    return max(PAN_MIN_RAD, min(PAN_MAX_RAD, angle_rad))

def clamp_tilt(angle_rad: float) -> float:
    """Force la consigne Tilt dans les limites mécaniques [-30°, +30°]."""
    return max(TILT_MIN_RAD, min(TILT_MAX_RAD, angle_rad))
```

---

## Alimentation Wanptek — Réglage Standard (2 Moteurs RS-05)

| Paramètre | Valeur |
| :--- | :--- |
| **Tension** | 48.0 V (tension nominale sous charge, 24.0 V toléré sur banc) |
| **Limite courant** | **5.0 A** (2 moteurs en simultané) |
| **Mode OCP** | ✅ Activé |

> En holding (Enable sans mouvement), les 2 RS-05 tirent ~200–400 mA. Sur un mouvement modéré simultané, comptez 1–2 A. La limite à 5A protège sans couper intempestivement.

---

## 1. Script de Détection — Diagnostic Rapide

Confirme que les 2 moteurs sont joignables avant tout test. **Validé en conditions réelles.**

Le script d'automatisation est disponible dans le dépôt à l'adresse suivante : [detect_motors.py](../../../Code/scripts/motors/detect_motors.py).

### Lancement depuis la Jetson :
```bash
cd ~/dbot/Code
export PYTHONPATH=.
python3 scripts/motors/detect_motors.py
```

*(Code brut sous-jacent :)*

```python
import can
import robstride

with can.Bus(interface='socketcan', channel='can1') as bus:
    rs = robstride.Client(bus)

    for motor_id, role in [(1, 'Pan'), (2, 'Tilt')]:
        try:
            mode = rs.read_param(motor_id, 'run_mode')
            print(f"✅ Moteur ID:{motor_id} ({role}) détecté — Mode = {mode}")
        except Exception as e:
            print(f"❌ Moteur ID:{motor_id} ({role}) introuvable : {e}")
```

---

## 1.5. Script de Calibration du Zéro Mécanique

Permet de définir la position physique actuelle de la tête comme référence `0.0` rad (regard droit devant et horizontal) et de la sauvegarder dans la ROM/Flash des moteurs de cou (Pan et Tilt).

Le script d'automatisation est disponible dans le dépôt à l'adresse suivante : [calib_neck_zero.py](../../../Code/scripts/motors/calib_neck_zero.py).

### Lancement depuis la Jetson :
1. Éteignez ou déconnectez les moteurs (`Disable`) pour pouvoir orienter librement et manuellement la tête dans sa position neutre idéale.
2. Une fois la tête parfaitement droite, lancez le script depuis le dossier `Code` de la Jetson :
   ```bash
   cd ~/dbot/Code
   export PYTHONPATH=.
   python3 scripts/motors/calib_neck_zero.py
   ```
3. Suivez l'invite de commande et validez avec `y`. Le script enverra la commande CAN `ZeroPos` (Instruction `6` du protocole RobStride) avec le paramètre d'écriture en ROM.
4. Une fois calibré, le script activera brièvement les moteurs en mode position pour vérifier que la tête se maintient d'elle-même à cette nouvelle position `0.0` rad.

---

## 2. Script de Mouvement Simple — 1 Moteur à la fois

Fait bouger un seul moteur (utile pour vérifier chaque axe indépendamment). **Validé en conditions réelles.**

> [!CAUTION]
> Assurez-vous que l'axe est **libre de tourner** avant de lancer ce script.

```python
import can
import robstride
import time
import math

# ── Limites mécaniques (Doc 32 §3) ────────────────────────
PAN_MIN_RAD, PAN_MAX_RAD   = -1.396, 1.396
TILT_MIN_RAD, TILT_MAX_RAD = -0.524, 0.524

def clamp_pan(v):  return max(PAN_MIN_RAD,  min(PAN_MAX_RAD,  v))
def clamp_tilt(v): return max(TILT_MIN_RAD, min(TILT_MAX_RAD, v))

MOTOR_ID = 1           # 1 = Pan, 2 = Tilt
TARGET_DEG = 20        # Consigne en degrés
TARGET_RAD = math.radians(TARGET_DEG)

# Appliquer les limites selon le moteur testé
target_safe = clamp_pan(TARGET_RAD) if MOTOR_ID == 1 else clamp_tilt(TARGET_RAD)

with can.Bus(interface='socketcan', channel='can1') as bus:
    rs = robstride.Client(bus)

    rs.write_param(MOTOR_ID, 'run_mode', robstride.RunMode.Position)
    time.sleep(0.1)

    resp = rs.enable(MOTOR_ID)
    print(f"Position de départ : {math.degrees(resp.angle):.1f}°")

    print(f"→ Aller à +{math.degrees(target_safe):.1f}°...")
    rs.write_param(MOTOR_ID, 'loc_ref', target_safe)
    time.sleep(2.0)

    print(f"→ Aller à -{math.degrees(target_safe):.1f}°...")
    rs.write_param(MOTOR_ID, 'loc_ref', -target_safe)
    time.sleep(2.0)

    print("→ Retour à 0°...")
    rs.write_param(MOTOR_ID, 'loc_ref', 0.0)
    time.sleep(2.0)

    rs.disable(MOTOR_ID)
    print("✅ Test terminé.")
```

---

## 3. Script Pan + Tilt Simultanés — Test ±20°

Fait bouger les 2 moteurs en même temps. **Validé en conditions réelles.**

```python
import can
import robstride
import time
import math

# ── Limites mécaniques (Doc 32 §3) ────────────────────────
PAN_MIN_RAD, PAN_MAX_RAD   = -1.396, 1.396   # ±80°
TILT_MIN_RAD, TILT_MAX_RAD = -0.524, 0.524   # ±30°

def clamp_pan(v):  return max(PAN_MIN_RAD,  min(PAN_MAX_RAD,  v))
def clamp_tilt(v): return max(TILT_MIN_RAD, min(TILT_MAX_RAD, v))

ANGLE_RAD = clamp_pan(math.radians(20))  # 20° — dans les limites des 2 moteurs

with can.Bus(interface='socketcan', channel='can1') as bus:
    rs = robstride.Client(bus)

    # Détection préalable
    for mid, role in [(1, 'Pan'), (2, 'Tilt')]:
        try:
            rs.read_param(mid, 'run_mode')
            print(f"✅ ID:{mid} ({role}) détecté")
        except:
            print(f"❌ ID:{mid} ({role}) introuvable — arrêt")
            exit()

    # Mode Position sur les 2
    for mid in [1, 2]:
        rs.write_param(mid, 'run_mode', robstride.RunMode.Position)
    time.sleep(0.1)

    resp1 = rs.enable(1)
    resp2 = rs.enable(2)
    print(f"\nPositions départ : Pan={math.degrees(resp1.angle):.1f}° | Tilt={math.degrees(resp2.angle):.1f}°")

    # +20°
    print(f"\n→ +{math.degrees(ANGLE_RAD):.1f}° sur les 2 moteurs...")
    rs.write_param(1, 'loc_ref', clamp_pan(ANGLE_RAD))
    rs.write_param(2, 'loc_ref', clamp_tilt(ANGLE_RAD))
    time.sleep(2.0)
    p1 = rs.read_param(1, 'mechpos')
    p2 = rs.read_param(2, 'mechpos')
    print(f"   Pan={math.degrees(p1):.1f}° | Tilt={math.degrees(p2):.1f}°")

    time.sleep(1.0)

    # -20°
    print(f"\n→ -{math.degrees(ANGLE_RAD):.1f}° sur les 2 moteurs...")
    rs.write_param(1, 'loc_ref', clamp_pan(-ANGLE_RAD))
    rs.write_param(2, 'loc_ref', clamp_tilt(-ANGLE_RAD))
    time.sleep(2.0)
    p1 = rs.read_param(1, 'mechpos')
    p2 = rs.read_param(2, 'mechpos')
    print(f"   Pan={math.degrees(p1):.1f}° | Tilt={math.degrees(p2):.1f}°")

    time.sleep(1.0)

    # Retour 0
    print("\n→ Retour à 0°...")
    rs.write_param(1, 'loc_ref', 0.0)
    rs.write_param(2, 'loc_ref', 0.0)
    time.sleep(2.0)

    rs.disable(1)
    rs.disable(2)
    print("\n✅ Test terminé — 2 moteurs désactivés.")
```

---

## 4. Script Séquence "Regard" — Simulation Comportement Robot

Enchaîne automatiquement : gauche → droite → haut → bas → centre. Utile pour valider la fluidité du mouvement combiné.

Le script d'automatisation exécutant cette séquence est disponible dans le dépôt : [test_neck.py](../../../Code/scripts/motors/test_neck.py).

### Lancement depuis la Jetson :
```bash
cd ~/dbot/Code
export PYTHONPATH=.
python3 scripts/motors/test_neck.py
```

*(Code brut sous-jacent :)*

```python
import can
import robstride
import time
import math

# ── Limites mécaniques (Doc 32 §3) ────────────────────────
PAN_MIN_RAD, PAN_MAX_RAD   = -1.396, 1.396
TILT_MIN_RAD, TILT_MAX_RAD = -0.524, 0.524

def clamp_pan(v):  return max(PAN_MIN_RAD,  min(PAN_MAX_RAD,  v))
def clamp_tilt(v): return max(TILT_MIN_RAD, min(TILT_MAX_RAD, v))

def look_at(rs, pan_deg, tilt_deg, duration=1.5):
    """Envoie une consigne Pan + Tilt en degrés, avec bornes automatiques."""
    pan_rad  = clamp_pan(math.radians(pan_deg))
    tilt_rad = clamp_tilt(math.radians(tilt_deg))
    rs.write_param(1, 'loc_ref', pan_rad)
    rs.write_param(2, 'loc_ref', tilt_rad)
    time.sleep(duration)
    p1 = rs.read_param(1, 'mechpos')
    p2 = rs.read_param(2, 'mechpos')
    print(f"   Pan={math.degrees(p1):.1f}° | Tilt={math.degrees(p2):.1f}°")

# Séquence de regard (Pan°, Tilt°)
SEQUENCE = [
    ("Centre",         0,   0),
    ("Gauche",       -30,   0),
    ("Centre",         0,   0),
    ("Droite",        30,   0),
    ("Centre",         0,   0),
    ("Haut",           0, -20),
    ("Centre",         0,   0),
    ("Bas",            0,  20),
    ("Centre",         0,   0),
    ("Haut-Gauche",  -25, -15),
    ("Bas-Droite",    25,  15),
    ("Centre final",   0,   0),
]

with can.Bus(interface='socketcan', channel='can1') as bus:
    rs = robstride.Client(bus)

    for mid in [1, 2]:
        rs.write_param(mid, 'run_mode', robstride.RunMode.Position)
    time.sleep(0.1)
    rs.enable(1)
    rs.enable(2)
    print("Moteurs activés — Démarrage séquence regard\n")

    for label, pan_deg, tilt_deg in SEQUENCE:
        print(f"→ {label} ({pan_deg}°, {tilt_deg}°)")
        look_at(rs, pan_deg, tilt_deg, duration=1.5)

    rs.disable(1)
    rs.disable(2)
    print("\n✅ Séquence terminée — Moteurs désactivés.")
```

---

## 5. Surveillance Télémétrie en Temps Réel

Lit en boucle la position, vitesse, tension et température des 2 moteurs. Utile pour diagnostiquer des comportements anormaux.

```python
import can
import robstride
import time
import math

with can.Bus(interface='socketcan', channel='can1') as bus:
    rs = robstride.Client(bus)

    print("Surveillance temps réel — Ctrl+C pour arrêter\n")
    print(f"{'ID':<4} {'Pos (°)':<10} {'Vit (°/s)':<12} {'Vbus (V)':<10} {'Temp (°C)':<10}")
    print("-" * 50)

    try:
        while True:
            for mid in [1, 2]:
                try:
                    pos  = math.degrees(rs.read_param(mid, 'mechpos'))
                    vel  = math.degrees(rs.read_param(mid, 'mechvel'))
                    vbus = rs.read_param(mid, 'vbus')
                    print(f"{mid:<4} {pos:<10.1f} {vel:<12.1f} {vbus:<10.1f}", end='\r' if mid == 1 else '\n')
                except:
                    print(f"ID:{mid} — pas de réponse")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n\nArrêt surveillance.")
```

---

## 6. Roadmap Intégration ROS2

> *La suite logique après validation des scripts Python ci-dessus.*

### Étape A — Installation ROS2 Humble (Jetson)

```bash
# Ajouter les dépôts ROS2
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
     -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
     http://packages.ros.org/ros2/ubuntu jammy main" \
     | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt-get update
sudo apt-get install -y ros-humble-desktop python3-colcon-common-extensions
```

### Étape B — Nœud de Contrôle du Cou (RobStride → ROS2)

Le nœud ROS2 "cou" devra :
1. S'abonner aux topics `/neck/pan/cmd` et `/neck/tilt/cmd` (type `std_msgs/Float64`, en **degrés** ou **radians**)
2. Appliquer systématiquement les fonctions `clamp_pan()` et `clamp_tilt()` avant tout envoi CAN
3. Publier la télémétrie sur `/neck/pan/state` et `/neck/tilt/state`

### Étape C — Test Stabilisation Regard (OAK-D Pro)

1. Connecter l'OAK-D Pro (USB3 → Jetson)
2. Lancer le nœud de détection de visage (DepthAI ou MediaPipe)
3. Calculer l'erreur angulaire (face_x, face_y) → consigne Pan/Tilt
4. Boucler avec les fonctions `clamp_pan()` / `clamp_tilt()` pour garantir les butées

### Étape D — Intégration URDF

Reporter les limites dans le fichier URDF (cf. Doc 32 §3.2) pour que MoveIt2 planifie des trajectoires valides :

```xml
<!-- Joint Pan (ID:1) -->
<joint name="neck_pan" type="revolute">
  <limit lower="-1.396" upper="1.396" effort="5.5" velocity="10.0"/>
</joint>

<!-- Joint Tilt (ID:2) -->
<joint name="neck_tilt" type="revolute">
  <limit lower="-0.524" upper="0.524" effort="5.5" velocity="10.0"/>
</joint>
```

---

## Récapitulatif des Limites — Référence Rapide

| Moteur | ID | Axe | Limite Min | Limite Max | Source |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **Pan** | 1 | Rotation gauche/droite | -80° (-1.396 rad) | +80° (+1.396 rad) | Doc 32 §3 |
| **Tilt** | 2 | Inclinaison avant/arrière | -30° (-0.524 rad) | +30° (+0.524 rad) | Doc 32 §3 |

> [!WARNING]
> Ces limites doivent être appliquées à **chaque couche** : firmware moteur (flashé via MotorStudio), scripts Python (`clamp_pan` / `clamp_tilt`), nœud ROS2, et URDF. La défaillance d'une seule couche peut créer une contrainte mécanique sur les câbles ou la structure du cou.

---

## Réglages d'Asservissement & Fluidité (Validés sous Charge de 2 kg)

Lors de la calibration finale sur le robot assemblé, les réglages d'usine par défaut ont été optimisés pour éliminer les micro-saccades induites par l'inertie de la tête lestée de ses caméras et capteurs.

### 1. Gains d'Asservissement (PID)
Les gains suivants doivent être injectés à l'activation des moteurs pour garantir la rigidité du cou :

| Gain | Registre RobStride | Valeur par Défaut | Valeur Validée (Charge) | Effet sur le comportement |
| :--- | :---: | :---: | :---: | :--- |
| **loc_kp** | `0x701E` | 30.0 | **50.0** | Supprime la mollesse ("effet ressort") sur le Pan et le Tilt. |
| **spd_kp** | `0x701F` | 1.0 | **3.0** | Amortit activement les rebonds d'inertie lors des accélérations. |
| **spd_ki** | `0x7020` | 0.02 | **0.05** | Annule la dérive du Tilt provoquée par le porte-à-faux. |

### 2. Stratégie d'Interpolation Logicielle
Pour éviter les chocs mécaniques d'accélération (Jerk infini) et compenser la gigue de communication (Jitter), la bibliothèque de contrôle implémente :
* **Fréquence de 100 Hz** (`time_step = 0.01` s) : adoucit l'enchaînement des micro-consignes.
* **Interpolation Cosinusoïdale (Cosine Interpolation / Smoothstep)** : génère des accélérations et des freinages en douceur (forme en cloche), évitant le broutement au démarrage et à l'arrêt.
* **Marge matérielle de vitesse (Hardware Headroom)** : La limite de vitesse matérielle écrite dans le registre `limit_spd` est configurée à **3.0 × la vitesse logicielle cible** (soit 90°/s pour une consigne de 30°/s), évitant tout conflit d'écrêtage de vitesse.
