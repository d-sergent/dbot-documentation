#!/usr/bin/env python3
"""
scripts/motors/test_neck.py — Séquence Regard Complète
=======================================================
Lance la séquence de test du cou (Pan + Tilt) validée en conditions réelles.
Utilise NeckController qui applique automatiquement les bornes mécaniques.

Usage :
    python3 scripts/motors/test_neck.py
"""

import time
import sys
from dbot.motors.neck import NeckController


SEQUENCE = [
    ("Centre",        0,   0, 1.5),
    ("Pan +80°",     80,   0, 9.0),
    ("Centre",        0,   0, 1.5),
    ("Pan -80°",    -80,   0, 9.0),
    ("Centre final",  0,   0, 1.5),
]


def main():
    print("=" * 50)
    print("  D-Bot — Séquence Regard Cou (Pan + Tilt)")
    print("=" * 50)

    with NeckController() as neck:
        # Vérification préalable
        status = neck.detect()
        for mid, ok in status.items():
            role = "Pan" if mid == 1 else "Tilt"
            icon = "✅" if ok else "❌"
            print(f"  {icon} Moteur ID:{mid} ({role})")

        if not any(status.values()):
            print("\n❌ Aucun moteur détecté — arrêt.")
            sys.exit(1)
        elif not all(status.values()):
            print("\n⚠️ Attention : Un moteur est manquant. Seuls les moteurs détectés réagiront.")

        print("\nMoteurs connectés. Activation en cours...")
        neck.enable()
        print("Moteurs activés — Démarrage séquence...\n")
        neck.print_state()

        for label, pan_deg, tilt_deg, duration in SEQUENCE:
            print(f"→ {label:15s} (Pan={pan_deg:+4}°, Tilt={tilt_deg:+4}°)")
            neck.look_at(pan_deg, tilt_deg)
            time.sleep(duration)

        neck.center()
        time.sleep(1.0)
        neck.print_state()

    print("\n✅ Séquence terminée — Moteurs désactivés.")


if __name__ == '__main__':
    main()
