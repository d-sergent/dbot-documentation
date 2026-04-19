# 42 — Configuration Bus CAN : InnoMaker USB2CAN et Moteurs RS-05 (Cou)

Ce guide décrit la mise en place du **Bus CAN 1** dédié aux moteurs RobStride RS-05 du cou du D-Bot, incluant la configuration système sur la Jetson Orin Nano, le câblage physique, et les scripts Python validés en conditions réelles.

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

**Méthode pratique :** Soudez les deux pattes de la résistance 120 Ω directement entre les fils rouge et noir, **juste avant** que le câble n'entre dans le connecteur JST qui se fiche sur le moteur.

---

## 2. Installation Driver gs_usb (Noyau JetPack 6)

> [!IMPORTANT]
> Le module `gs_usb` n'est **pas inclus** dans le noyau JetPack 6 par défaut. Il faut le compiler depuis un script dédié avant toute utilisation de l'InnoMaker.

### 2.1. Compilation du driver

```bash
wget https://github.com/lucianovk/jetson-gs_usb-kernel-builder/raw/main/jetson-gs_usb-kernel-builder.sh
chmod +x jetson-gs_usb-kernel-builder.sh
sudo ./jetson-gs_usb-kernel-builder.sh
```

Le script télécharge les sources du noyau NVIDIA, compile uniquement le module `gs_usb` et l'installe. Il prend quelques minutes.

### 2.2. Vérification après installation

```bash
sudo modprobe gs_usb
sudo dmesg | grep gs_usb
```

Résultat attendu :
```
gs_usb: loading out-of-tree module taints kernel.
gs_usb 1-2.3:1.0: Configuring for 1 interfaces
usbcore: registered new interface driver gs_usb
```

---

## 3. Vérification de l'Interface CAN

### 3.1. Détection de l'InnoMaker

```bash
lsusb | grep "1d50:606f"
```

Résultat attendu :
```
Bus 001 Device 004: ID 1d50:606f OpenMoko, Inc. Geschwister Schneider CAN adapter
```

### 3.2. Présence de l'interface réseau `can0`

```bash
ip link show
```

Vérifiez que `can0` apparaît dans la liste. C'est l'InnoMaker (l'interface interne de la Jetson est `can1`).

---

## 4. Activation de l'Interface CAN

Le RS-05 fonctionne à **1 Mbps**. À chaque démarrage, l'interface doit être activée :

```bash
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up
```

Vérification :
```bash
ip link show can0
# Attendu : state UP
```

### Persistance au Démarrage (optionnel)

Pour que `can0` se lève automatiquement à chaque boot :

```bash
sudo nano /etc/network/interfaces.d/can0
```

Contenu à coller :
```
auto can0
iface can0 inet manual
    pre-up /sbin/ip link set can0 type can bitrate 1000000
    up /sbin/ip link set can0 up
    down /sbin/ip link set can0 down
```

---

## 5. Tests de Communication Python

> [!NOTE]
> Les RS-05 utilisent le protocole **CAN Extended 29-bit** — les trames standard 11-bit sont ignorées par le moteur. La librairie `robstride` gère ce protocole correctement.

### 5.1. Installation

```bash
pip3 install robstride
```

### 5.2. Script de Détection (Diagnostic)

Ce script scanne les IDs 1 et 2 et confirme que le moteur répond. **Validé en conditions réelles.**

```python
import can
import robstride
import time

with can.Bus(interface='socketcan', channel='can0') as bus:
    rs = robstride.Client(bus)

    for motor_id in [1, 2]:
        print(f"\n--- Test Moteur ID:{motor_id} ---")
        try:
            mode = rs.read_param(motor_id, 'run_mode')
            print(f"✅ Moteur ID:{motor_id} répond ! Mode = {mode}")
        except Exception as e:
            print(f"  Lecture directe échouée : {e}")
            print(f"  → Tentative d'activation...")
            try:
                resp = rs.enable(motor_id)
                print(f"✅ ID:{motor_id} activé ! Angle={resp.angle:.3f} rad | Temp={resp.temp:.1f}°C")
                time.sleep(0.5)
                rs.disable(motor_id)
            except Exception as e2:
                print(f"❌ ID:{motor_id} ne répond pas : {e2}")
```

Résultat attendu (avec moteur ID:1 seul branché) :
```
--- Test Moteur ID:1 ---
✅ Moteur ID:1 répond ! Mode = RunMode.Operation

--- Test Moteur ID:2 ---
❌ ID:2 ne répond pas : No response from motor received
```

### 5.3. Script de Mouvement (Test Complet)

Ce script fait physiquement bouger le moteur. **Validé en conditions réelles.**

> [!CAUTION]
> Assurez-vous que l'axe du moteur est **libre de tourner** avant de lancer ce script.

```python
import can
import robstride
import time

with can.Bus(interface='socketcan', channel='can0') as bus:
    rs = robstride.Client(bus)
    MOTOR_ID = 1  # Adaptez selon l'ID configuré

    print("1. Mode Position...")
    rs.write_param(MOTOR_ID, 'run_mode', robstride.RunMode.Position)
    time.sleep(0.1)

    print("2. Activation du moteur...")
    resp = rs.enable(MOTOR_ID)
    print(f"   Position actuelle : {resp.angle:.3f} rad")

    print("3. Aller à +1.0 rad (~57°)...")
    rs.write_param(MOTOR_ID, 'loc_ref', 1.0)
    time.sleep(2.0)

    pos = rs.read_param(MOTOR_ID, 'mechpos')
    print(f"   Position atteinte : {pos:.3f} rad")

    print("4. Retour à 0...")
    rs.write_param(MOTOR_ID, 'loc_ref', 0.0)
    time.sleep(2.0)

    print("5. Désactivation (sécurité)...")
    rs.disable(MOTOR_ID)
    print("✅ Test terminé !")
```

---

## 6. Référence Paramètres Disponibles

| Paramètre | ID Registre | Type | Description |
| :--- | :--- | :--- | :--- |
| `run_mode` | 0x7005 | `RunMode` | Mode de contrôle (Position, Speed, Current, Operation) |
| `loc_ref` | 0x7016 | float (rad) | Consigne de position cible |
| `spd_ref` | 0x700A | float (rad/s) | Consigne de vitesse cible |
| `limit_torque` | 0x700B | float (Nm) | Limite de couple |
| `mechpos` | 0x7019 | float (rad) | Position mécanique actuelle (lecture) |
| `mechvel` | 0x701B | float (rad/s) | Vitesse mécanique actuelle (lecture) |
| `vbus` | 0x701C | float (V) | Tension bus actuelle (lecture) |
| `limit_spd` | 0x7017 | float (rad/s) | Vitesse maximale autorisée |
| `limit_cur` | 0x7018 | float (A) | Courant maximal autorisé |

**Modes disponibles (`RunMode`) :**
- `RunMode.Operation` — Mode par défaut au démarrage
- `RunMode.Position` — Contrôle de position (aller à un angle précis)
- `RunMode.Speed` — Contrôle de vitesse (tourner à X rad/s)
- `RunMode.Current` — Contrôle de couple direct

---

## 7. Dépannage Rapide

| Symptôme | Cause Probable | Solution |
| :--- | :--- | :--- |
| **`can0` absent dans `ip link`** | Driver non chargé | `sudo modprobe gs_usb` |
| **`candump` vide au boot moteur** | Câblage incorrect ou alim absente | Vérifier alim 24-48V et couleurs Rouge=CANH, Noir=CANL |
| **Erreur `Bus-off`** | Résistance de terminaison manquante | Souder 120 Ω entre Rouge et Noir sur le câble JST moteur |
| **`OSError: [Errno 100]`** | Interface réseau à l'état DOWN | `sudo ip link set can0 up` |
| **`No response from motor`** | Moteur non alimenté ou ID incorrect | Vérifier l'alim 24-48V, tester ID 1 et 2 |
| **Mauvais CAN ID reçu** | Conflit d'ID sur le bus | Reconfigurer les IDs via RobStride MotorStudio sur PC |
