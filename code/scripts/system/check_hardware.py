#!/usr/bin/env python3
"""
scripts/system/check_hardware.py — Vérification Périphériques D-Bot
====================================================================
Vérifie la présence de tous les composants matériels nécessaires.
Lancé automatiquement par startup.sh au démarrage.
"""

import subprocess
import sys


CHECKS = {
    "InnoMaker USB2CAN": {
        "cmd": "lsusb",
        "expect": "1d50:606f",
        "fix": "Brancher le câble USB de l'InnoMaker",
    },
    "Interface CAN0": {
        "cmd": "ip link show can0",
        "expect": "can0",
        "fix": "sudo ip link set can0 type can bitrate 1000000 && sudo ip link set can0 up",
    },
    "OAK-D Pro": {
        "cmd": "lsusb",
        "expect": "03e7",   # Vendor ID Luxonis
        "fix": "Brancher l'OAK-D Pro en USB3",
    },
    "ReSpeaker USB": {
        "cmd": "lsusb",
        "expect": "2886",   # Seeed (ReSpeaker)
        "fix": "Brancher le ReSpeaker XVF-3800",
    },
    "Udev Rules OAK-D": {
        "cmd": "ls /etc/udev/rules.d/99-depthai.rules",
        "expect": "99-depthai.rules",
        "fix": "sudo tee /etc/udev/rules.d/99-depthai.rules <<< 'SUBSYSTEM==\"usb\", ATTR{idVendor}==\"03e7\", MODE=\"0666\"' && sudo udevadm control --reload-rules",
    },
}

OPTIONAL_CHECKS = {
}


def check(name: str, cmd: str, expect: str) -> bool:
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=3)
        return expect in result.stdout
    except Exception:
        return False


def main():
    print("\n🤖 D-Bot — Vérification Matériel")
    print("─" * 40)

    all_ok = True
    for name, cfg in CHECKS.items():
        ok = check(name, cfg["cmd"], cfg["expect"])
        icon = "✅" if ok else "❌"
        print(f"  {icon} {name}")
        if not ok:
            print(f"     → Fix : {cfg['fix']}")
            all_ok = False

    print()
    for name, cfg in OPTIONAL_CHECKS.items():
        ok = check(name, cfg["cmd"], cfg["expect"])
        icon = "✅" if ok else "⚠️ "
        print(f"  {icon} {name} (optionnel)")

    print("─" * 40)
    if all_ok:
        print("✅ Tout le matériel requis est détecté — D-Bot prêt.\n")
        sys.exit(0)
    else:
        print("❌ Matériel manquant — corrigez avant de lancer les scripts.\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
