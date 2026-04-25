"""
dbot/motors/can_bus.py — Singleton Bus CAN Partagé
===================================================
Un seul objet `can.Bus` est ouvert pour tout le programme.
Tous les contrôleurs moteurs partagent cette instance.
"""

import can
from dbot.config import CAN_CHANNEL, CAN_BITRATE

_bus_instance: can.BusABC | None = None


def get_bus() -> can.BusABC:
    """Retourne l'instance partagée du bus CAN (crée si nécessaire)."""
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = can.Bus(
            interface='socketcan',
            channel=CAN_CHANNEL,
            bitrate=CAN_BITRATE,
        )
    return _bus_instance


def close_bus() -> None:
    """Ferme proprement le bus CAN (à appeler à la fin du programme)."""
    global _bus_instance
    if _bus_instance is not None:
        _bus_instance.shutdown()
        _bus_instance = None
