# D-Bot Code

Package Python de contrôle du robot humanoïde D-Bot.

## Installation (Jetson — première fois)

```bash
# Clone sparse (code uniquement, sans la documentation)
git clone --filter=blob:none --sparse \
    https://github.com/d-sergent/dbot-documentation.git \
    ~/dbot
cd ~/dbot
git sparse-checkout set code/

# Installer le package en mode développement
cd ~/dbot/code
pip3 install -e .
```

## Mise à jour

```bash
cd ~/dbot && git pull
```

## Démarrage Robot

```bash
bash ~/dbot/code/scripts/system/startup.sh
```

## Tests Rapides

```bash
# Vérification matériel
python3 scripts/system/check_hardware.py

# Test cou (Pan + Tilt)
python3 scripts/motors/test_neck.py
```

## Structure

```
dbot/
├── config.py          ← Constantes centralisées (limites, IDs, baudrates)
├── motors/
│   ├── can_bus.py     ← Singleton bus CAN partagé
│   ├── neck.py        ← Contrôleur Cou (Pan + Tilt RS-05)
│   ├── arm.py         ← (Phase 2)
│   └── legs.py        ← (Phase 4)
├── vision/            ← (Phase 1) OAK-D Pro
├── audio/             ← (Phase 1) ReSpeaker
├── balance/           ← (Phase 4) IMU BMI270
└── behaviors/         ← Comportements haut niveau
```
