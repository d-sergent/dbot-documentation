# 42 — Configuration Bus CAN : InnoMaker USB2CAN et Moteurs RS-05 (Cou)

Ce guide décrit la mise en place du **Bus CAN 1** dédié aux moteurs RobStride RS-05 du cou du D-Bot, incluant la configuration système sur la Jetson Orin Nano, le câblage physique, et un script de test Python complet (Mode MIT).

> [!NOTE]
> Les RS-05 sont les **seuls moteurs du D-Bot sans second port CAN**. Ils ne supportent donc pas le câblage en "daisy chain" (chaîne) classique. La connexion se fait obligatoirement en **étoile via un splitter CAN** (connecteur en T ou mini-hub à 3 bornes).

---

## 1. Schéma de Câblage et Réseau Physique

![Schéma Câblage CAN - Cou (Bus 1)](../../../assets/can_innomaker_rs05_wiring.png)

### Points clés du câblage
- **CAN H** (rouge) et **CAN L** (noir) partent de l'InnoMaker vers un **splitter CAN** central (topologie étoile obligatoire).
- Le splitter distribue les 2 fils vers chaque RS-05 **en parallèle**.
- La **masse (GND)** doit être commune entre la Jetson, l'InnoMaker et les alimentations moteurs pour éviter un bus flottant.

### Résistances de Terminaison 120 Ω — Où les Placer ?

> [!IMPORTANT]
> Le RS-05 n'ayant **qu'un seul port CAN** (entrée uniquement, pas de sortie), il n'y a aucun cavalier ou DIP switch de terminaison intégré au moteur. C'est une topologie en étoile, et les résistances doivent être placées **sur les câbles**, pas sur les boîtiers moteurs.

Le bus CAN requiert une résistance de **120 Ω à chaque extrémité physique du réseau**. Dans cette topologie étoile, les 3 extrémités sont :

| Extrémité | Résistance | Comment |
| :--- | :--- | :--- |
| **InnoMaker (côté Jetson)** | 120 Ω **intégrée en interne** | Activée en usine — vérifiez le cavalier sur la carte ✅ |
| **Câble RS-05 ID:1** | 120 Ω **à souder sur la prise JST** | Ponter CAN H (rouge) et CAN L (noir) juste avant le connecteur |
| **Câble RS-05 ID:2** | 120 Ω **à souder sur la prise JST** | Idem |

**Méthode pratique :** Soudez les deux pattes de la résistance 120 Ω directement entre les fils rouge et noir, **juste avant** que le câble n'entre dans le connecteur JST qui se fiche sur le moteur. La résistance doit être sur le câble indépendamment du moteur, de sorte qu'elle reste en place même si vous débranchez le moteur pour maintenance.

---

## 2. Configuration Système (Jetson)

### 2.1. Prérequis et Dépendances
Installez les outils de diagnostic CAN et les bibliothèques Python :
```bash
sudo apt-get update
sudo apt-get install -y can-utils
pip3 install python-can
```

### 2.2. Vérification de la détection de l'InnoMaker
Branchez l'adaptateur USB :
```bash
lsusb
```
*(Vous devez voir : `ID 1d50:606f OpenMoko, Inc. Geschwister Schneider CAN adapter`)*

Vérifiez que le noyau Linux l'a bien assigné :
```bash
dmesg | grep can
```
*(Vous devez voir `gs_usb ... registered` indiquant le bon chargement du driver)*

> [!WARNING]
> Si l'adaptateur n'apparaît pas ou que `can0` est introuvable, forcez le chargement du driver : `sudo modprobe gs_usb`.

### 2.3. Lancement de l'interface `can0`
Le protocole standard RobStride tourne à **1 Mbps**. 
```bash
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up
```

*(Optionnel : Les RS-05 supportent le **CAN-FD** si configurés. Pour l'activer :)*
```bash
sudo ip link set can0 type can bitrate 1000000 dbitrate 5000000 fd on
sudo ip link set can0 up
```

Vérifiez l'état (`UP`) :
```bash
ip link show can0
```

---

## 3. Communication et Test (Mode MIT)

Avant d'utiliser un SDK complexe, voici le script "brut" de référence qui construit manuellement la trame **MIT Motor Control**. Il permet de valider toute la chaîne : format des données, conversion Flottant ↔ Hexadécimal 12/16 bits, et réception de la télémétrie.

Créez le fichier `test_robstride_mit.py` et exécutez-le (`python3 test_robstride_mit.py`) :

```python
import can
import time

# ── Configuration ──────────────────────────────────────────
MOTOR_ID = 0x01          # ID CAN du moteur (usine souvent 0x01 ou 0x7F)
BUS_INTERFACE = 'can0'
BUS_TYPE = 'socketcan'

# Constantes du protocole Robstride 05
P_MIN, P_MAX = -12.5, 12.5   # Position (rad)
V_MIN, V_MAX = -30.0, 30.0   # Vitesse (rad/s)
T_MIN, T_MAX = -50.0, 50.0   # Couple (Nm)
KP_MIN, KP_MAX = 0.0, 500.0  # Gain P
KD_MIN, KD_MAX = 0.0, 5.0    # Gain D

# ── Fonctions Mathématiques (Packing / Unpacking MIT) ──────
def float_to_uint(x, x_min, x_max, bits):
    span = x_max - x_min
    x = max(x_min, min(x_max, x))
    return int((x - x_min) / span * ((1 << bits) - 1))

def uint_to_float(x, x_min, x_max, bits):
    span = x_max - x_min
    return x / ((1 << bits) - 1) * span + x_min

def build_mit_command(p_des, v_des, kp, kd, t_ff):
    """Construit une trame MIT Motor Control (8 octets)."""
    p  = float_to_uint(p_des, P_MIN, P_MAX, 16)
    v  = float_to_uint(v_des, V_MIN, V_MAX, 12)
    kp_i = float_to_uint(kp, KP_MIN, KP_MAX, 12)
    kd_i = float_to_uint(kd, KD_MIN, KD_MAX, 12)
    t  = float_to_uint(t_ff, T_MIN, T_MAX, 12)
    
    return [
        (p >> 8) & 0xFF,
        p & 0xFF,
        (v >> 4) & 0xFF,
        ((v & 0xF) << 4) | ((kp_i >> 8) & 0xF),
        kp_i & 0xFF,
        (kd_i >> 4) & 0xFF,
        ((kd_i & 0xF) << 4) | ((t >> 8) & 0xF),
        t & 0xFF,
    ]

def parse_response(msg):
    """Décode la télémétrie de la réponse moteur."""
    d = msg.data
    motor_id = (d[0]) & 0x0F
    p_raw = (d[1] << 8) | d[2]
    v_raw = (d[3] << 4) | (d[4] >> 4)
    t_raw = ((d[4] & 0xF) << 8) | d[5]
    
    return (
        motor_id,
        uint_to_float(p_raw, P_MIN, P_MAX, 16),
        uint_to_float(v_raw, V_MIN, V_MAX, 12),
        uint_to_float(t_raw, T_MIN, T_MAX, 12)
    )

# ── Exécution ──────────────────────────────────────────────
bus = can.interface.Bus(channel=BUS_INTERFACE, bustype=BUS_TYPE)

def send(data, arb_id=MOTOR_ID):
    msg = can.Message(arbitration_id=arb_id, data=data, is_extended_id=False)
    bus.send(msg)

ENTER_CONTROL = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC]
EXIT_CONTROL  = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFD]
ZERO_POSITION = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE]

try:
    print("1. Activation du moteur...")
    send(ENTER_CONTROL)
    time.sleep(0.1)

    print("2. Calibration Zéro...")
    send(ZERO_POSITION)
    time.sleep(0.5)

    print("3. Tir d'une position cible (1.0 rad)...")
    cmd = build_mit_command(p_des=1.0, v_des=0.0, kp=20.0, kd=0.5, t_ff=0.0)
    send(cmd)
    
    # Lecture réponse immédiate
    resp = bus.recv(timeout=1.0)
    if resp and resp.arbitration_id == MOTOR_ID:
        mid, pos, vel, trq = parse_response(resp)
        print(f"✅ Télémétrie reçue : Pos={pos:.3f} rad | Vit={vel:.3f} rad/s | Couple={trq:.3f} Nm")
    else:
        print("❌ Timeout : Pas de réponse du moteur.")

finally:
    print("4. Désactivation et sécurité...")
    send(EXIT_CONTROL)
    bus.shutdown()
```

---

## 4. Persistance & Automatisation

### Udev Rules (Nommage Fixe)
Pour que l'Innomaker s'appelle toujours `can_cou` et jamais `can1` par erreur au boot :
```bash
sudo nano /etc/udev/rules.d/80-can.rules
```
Ajoutez : 
`SUBSYSTEM=="net", ACTION=="add", ATTRS{idVendor}=="1d50", ATTRS{idProduct}=="606f", NAME="can_cou"`
*(Recharger : `sudo udevadm control --reload-rules && sudo udevadm trigger`)*

### Auto-Activation au Boot
Pour que l'interface se lève seule à 1 Mbps à chaque redémarrage, créez un fichier `/etc/network/interfaces.d/can0` :
```text
auto can0
iface can0 inet manual
    pre-up /sbin/ip link set can0 type can bitrate 1000000
    up /sbin/ip link set can0 up
    down /sbin/ip link set can0 down
```

---

## 5. Dépannage Rapide

| Symptôme | Cause Probable | Solution |
| :--- | :--- | :--- |
| **`can0` absent dans `ip link`** | Driver non chargé | `sudo modprobe gs_usb` |
| **`candump` vide** | Moteur débranché ou pas d'ID match | Vérifier alim 48V, lancer un boot moteur (s'affiche ID 0x...FE) |
| **Erreur `Bus-off`** | Terminaison manquante | Brancher ou souder la résistance de Terminaison **120Ω** |
| **`OSError: [Errno 100]`** | Interface réseau baissée | Lancer `sudo ip link set can0 up` |
| **Mauvais CAN ID lu** | Conflit / Réglage Usine | Utiliser "RobStride MotorStudio" (PC) pour fixer les ID 1 et 2 |
