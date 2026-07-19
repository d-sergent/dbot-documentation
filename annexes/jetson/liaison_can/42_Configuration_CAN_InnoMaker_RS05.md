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

### Résistances de Terminaison 120 Ω — Nécessaires ?

> [!NOTE]
> **Validé D-Bot (câbles courts < 30 cm) :** Les résistances de terminaison se sont révélées **non nécessaires** avec les câbles courts du cou du robot. Le bus fonctionne correctement sans elles dans cette configuration.

La règle théorique du protocole CAN impose 120 Ω à chaque extrémité du bus. En pratique :

| Longueur des câbles | Résistances nécessaires ? |
| :--- | :--- |
| **< 30 cm** (cas du cou D-Bot) | ❌ Non requises — validé en conditions réelles |
| **30 cm – 1 m** | ⚠️ Recommandées (erreurs sporadiques possibles) |
| **> 1 m** | ✅ Obligatoires (erreurs `Bus-off` garanties sans elles) |

Si vous devez en ajouter (câbles longs ou futurs membres), placez une résistance 120 Ω **sur le câble lui-même** en pontant CAN H (rouge) et CAN L (noir) juste avant le connecteur JST moteur — l'InnoMaker possède la sienne intégrée en interne.

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

### 3.2. Présence de l'interface réseau `can1`

```bash
ip link show
```

Vérifiez que `can1` apparaît dans la liste. C'est l'InnoMaker (l'interface interne de la Jetson est `can0`).

---

## 4. Activation de l'Interface CAN

Le RS-05 fonctionne à **1 Mbps**. À chaque démarrage, l'interface doit être activée :

```bash
sudo ip link set can1 type can bitrate 1000000
sudo ip link set can1 up
```

Vérification :
```bash
ip link show can1
# Attendu : state UP
```

### Persistance au Démarrage (optionnel)

Pour que `can1` se lève automatiquement à chaque boot :

```bash
sudo nano /etc/network/interfaces.d/can1
```

Contenu à coller :
```
auto can1
iface can1 inet manual
    pre-up /sbin/ip link set can1 type can bitrate 1000000
    up /sbin/ip link set can1 up
    down /sbin/ip link set can1 down
```

---

## 5. Tests de Communication Python

> [!IMPORTANT]
> **Sécurité Alimentation (Wanptek)** : Pour TOUS les tests de laboratoire sur banc, paramétrez obligatoirement votre alimentation stabilisée à **24.0V**.
> Définissez une limite de courant stricte (OCP - Over Current Protection) :
> - **2.0A maximum** pour tester **1 seul moteur**.
> - **5.0A maximum** pour tester **2 moteurs simultanément**.
> Cela protège l'électronique interne (mosfets) en cas de blocage inattendu de l'arbre ou de court-circuit.

> [!NOTE]
> Les RS-05 utilisent le protocole **CAN Extended 29-bit** — les trames standard 11-bit sont ignorées par le moteur. La librairie `robstride` gère ce protocole correctement.

### 5.1. Installation

```bash
pip3 install robstride
```

### 5.2. Étape Préliminaire : Détection des Moteurs (Diagnostic Rapide)

Avant toute manipulation ou test de mouvement, il est **indispensable** de vérifier que les moteurs répondent sur le bus CAN. Même si `candump` est silencieux (les moteurs peuvent être au repos en attente de requête), ce script va forcer un "Ping" de détection.

C'est une étape standard à exécuter systématiquement lors des usages préliminaires. Copiez-collez simplement ce bloc dans le terminal de la Jetson :

```bash
cd ~/dbot/code
export PYTHONPATH=.
python3 scripts/motors/detect_motors.py
```

Le script va balayer les IDs de 1 à 30. 
**Résultat attendu (avec moteurs 1 et 2 branchés) :**
```text
✅ [ID 01] RobStride motor detected! (Mode: RunMode.Operation)
✅ [ID 02] RobStride motor detected! (Mode: RunMode.Operation)
```

Si le script ne trouve rien, référez-vous au tableau de **Dépannage Rapide** (Section 7), et vérifiez en priorité que le GND de l'InnoMaker est bien sur la borne Noire de la Wanptek (et non la borne Terre verte).

### 5.3. Test de Mouvement (Séquence Regard)

Une fois la détection réussie, vous pouvez lancer la séquence de mouvement complète.
Ce test fait physiquement bouger les moteurs Pan et Tilt (±80° et ±30°). **Validé en conditions réelles.**

> [!CAUTION]
> 1. Assurez-vous que l'axe des moteurs est **libre de tourner**.
> 2. Assurez-vous que la Wanptek est réglée à **24V et 5A maximum** pour ce premier test sur banc, afin de limiter la vitesse et les dégâts en cas de problème.

Copiez-collez ce bloc pour lancer le balayage :

```bash
cd ~/dbot/code
export PYTHONPATH=.
python3 scripts/motors/test_neck.py
```

Le script va doucement centrer la tête, balayer à gauche, à droite, et se recentrer de manière sécurisée en utilisant le `NeckController`.

### 5.4. Bilan de Santé Détaillé (Diagnostic Avancé)

Si un moteur se comporte de façon inattendue (saccades, manque de force) ou n'est pas détecté à l'étape 5.2, utilisez ce script d'investigation approfondie. 
Il ne fait pas tourner les moteurs, mais extrait leurs paramètres internes (gains PID de rigidité et d'amortissement) pour s'assurer que la configuration flashée est toujours intacte, et affiche les erreurs CAN brutes.

Copiez-collez ce bloc :

```bash
cd ~/dbot/code
export PYTHONPATH=.
python3 scripts/motors/test_diag.py
```

*Note : Si le moteur semble endormi, le script forcera une activation silencieuse d'une demi-seconde pour lire sa température interne et sa position absolue.*

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
| **`can1` absent dans `ip link`** | Driver non chargé | `sudo modprobe gs_usb` |
| **`candump` vide et muet** | 1. Comportement normal (moteur au repos)<br>2. Erreur de masse Wanptek<br>3. Câblage inversé | 1. Placez-vous dans le répertoire `~/dbot/code` de la Jetson et lancez : `export PYTHONPATH=. && python3 scripts/motors/detect_motors.py`.<br>2. Branchez le GND InnoMaker sur la borne **Noire (-)** de la Wanptek, JAMAIS sur la Verte (⏚ GND).<br>3. Vérifiez Rouge=CANH, Noir=CANL |
| **Erreur `Bus-off`** | Câble trop long sans terminaison | Souder 120 Ω entre Rouge et Noir sur le câble JST si câbles > 30cm |
| **`OSError: [Errno 100]`** | Interface réseau à l'état DOWN | `sudo ip link set can1 up` |
| **`No response from motor`** | Moteur non alimenté ou ID incorrect | Vérifier l'alim 24-48V, tester ID 1 et 2 |
| **Mauvais CAN ID reçu** | Conflit d'ID sur le bus | Reconfigurer les IDs via RobStride MotorStudio sur PC |
