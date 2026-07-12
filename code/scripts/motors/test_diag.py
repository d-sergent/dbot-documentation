#!/usr/bin/env python3
"""
scripts/motors/test_diag.py — Diagnostic brut du bus CAN et des moteurs
======================================================================
Ce script tente de communiquer directement avec les moteurs 1 et 2 en affichant
les erreurs SocketCAN brutes en cas d'échec.

Usage :
    export PYTHONPATH=.
    python3 scripts/motors/test_diag.py
"""

import sys
import time
import can
import robstride
from dbot.config import CAN_CHANNEL, CAN_BITRATE

def main():
    print(f"Initialisation du bus CAN sur l'interface : {CAN_CHANNEL} ({CAN_BITRATE / 1e6:.1f} Mbps)...")
    try:
        bus = can.interface.Bus(interface='socketcan', channel=CAN_CHANNEL, bitrate=CAN_BITRATE)
        rs = robstride.Client(bus)
    except Exception as e:
        print(f"❌ Impossible d'ouvrir l'interface CAN '{CAN_CHANNEL}' : {e}")
        sys.exit(1)

    for motor_id in [1, 2]:
        role = "Pan" if motor_id == 1 else "Tilt"
        print(f"\n--- Test Moteur ID:{motor_id} ({role}) ---")
        try:
            # Essai de lecture simple du mode de fonctionnement
            mode = rs.read_param(motor_id, 'run_mode')
            print(f"✅ Moteur ID:{motor_id} répond ! Mode = {mode}")
        except Exception as e:
            print(f"  ❌ Échec de lecture directe : {e}")
            print(f"  → Tentative d'activation pour diagnostic...")
            try:
                resp = rs.enable(motor_id)
                print(f"  ✅ ID:{motor_id} a répondu à l'activation ! Angle={resp.angle:.3f} rad | Temp={resp.temp:.1f}°C")
                time.sleep(0.5)
                rs.disable(motor_id)
            except Exception as e2:
                print(f"  ❌ Pas de réponse à l'activation : {e2}")

    bus.shutdown()

if __name__ == "__main__":
    main()
