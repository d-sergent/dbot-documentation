"""
dbot/motors/neck.py — Contrôleur du Cou (Pan + Tilt)
=====================================================
Encapsule les deux moteurs RS-05 du cou dans une interface haut niveau.
Toutes les consignes sont automatiquement bornées aux limites mécaniques
définies dans config.py (Doc 32 §3).

Utilisation :
    from dbot.motors.neck import NeckController
    with NeckController() as neck:
        neck.look_at(pan_deg=20, tilt_deg=-10)
"""

import math
import time
import robstride

from dbot.config import (
    NECK_PAN_ID, NECK_TILT_ID,
    PAN_MIN_RAD, PAN_MAX_RAD,
    TILT_MIN_RAD, TILT_MAX_RAD,
)
from dbot.motors.can_bus import get_bus, close_bus


class NeckController:
    """
    Contrôle les 2 moteurs RS-05 du cou (Pan ID:1, Tilt ID:2).
    Les limites mécaniques sont TOUJOURS appliquées automatiquement.
    """

    def __init__(self):
        self._client = robstride.Client(get_bus())
        self._enabled = False

    # ── Context Manager ────────────────────────────────────
    def __enter__(self):
        self.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable()
        close_bus()

    # ── Bornes Mécaniques ──────────────────────────────────
    @staticmethod
    def clamp_pan(angle_rad: float) -> float:
        """Borne la consigne Pan dans [-40°, +40°] (Doc 32 §3)."""
        return max(PAN_MIN_RAD, min(PAN_MAX_RAD, angle_rad))

    @staticmethod
    def clamp_tilt(angle_rad: float) -> float:
        """Borne la consigne Tilt dans [-30°, +30°] (Doc 32 §3)."""
        return max(TILT_MIN_RAD, min(TILT_MAX_RAD, angle_rad))

    # ── Activation / Désactivation ─────────────────────────
    def enable(self) -> None:
        """Active les 2 moteurs en mode Position."""
        for mid in [NECK_PAN_ID, NECK_TILT_ID]:
            self._client.write_param(mid, 'run_mode', robstride.RunMode.Position)
        time.sleep(0.05)
        self._client.enable(NECK_PAN_ID)
        self._client.enable(NECK_TILT_ID)
        self._enabled = True

    def disable(self) -> None:
        """Désactive les 2 moteurs (coupe le holding torque)."""
        if self._enabled:
            self._client.disable(NECK_PAN_ID)
            self._client.disable(NECK_TILT_ID)
            self._enabled = False

    # ── Commandes ──────────────────────────────────────────
    def look_at(self, pan_deg: float = 0.0, tilt_deg: float = 0.0) -> None:
        """
        Envoie une consigne de regard en degrés.
        Les bornes mécaniques sont appliquées automatiquement.

        Args:
            pan_deg:  Rotation gauche/droite en degrés (+= droite)
            tilt_deg: Inclinaison en degrés (+= bas)
        """
        pan_rad  = self.clamp_pan(math.radians(pan_deg))
        tilt_rad = self.clamp_tilt(math.radians(tilt_deg))
        self._client.write_param(NECK_PAN_ID,  'loc_ref', pan_rad)
        self._client.write_param(NECK_TILT_ID, 'loc_ref', tilt_rad)

    def look_at_rad(self, pan_rad: float = 0.0, tilt_rad: float = 0.0) -> None:
        """Idem look_at() mais en radians."""
        self._client.write_param(NECK_PAN_ID,  'loc_ref', self.clamp_pan(pan_rad))
        self._client.write_param(NECK_TILT_ID, 'loc_ref', self.clamp_tilt(tilt_rad))

    def center(self) -> None:
        """Recentre la tête à 0°, 0°."""
        self.look_at(0.0, 0.0)

    # ── Télémétrie ─────────────────────────────────────────
    def get_state(self) -> dict:
        """
        Lit la position et la vitesse actuelles des 2 moteurs.

        Returns:
            dict avec clés: pan_deg, tilt_deg, pan_vel_dps, tilt_vel_dps, vbus_v
        """
        pan_pos  = math.degrees(self._client.read_param(NECK_PAN_ID,  'mechpos'))
        tilt_pos = math.degrees(self._client.read_param(NECK_TILT_ID, 'mechpos'))
        pan_vel  = math.degrees(self._client.read_param(NECK_PAN_ID,  'mechvel'))
        tilt_vel = math.degrees(self._client.read_param(NECK_TILT_ID, 'mechvel'))
        vbus     = self._client.read_param(NECK_PAN_ID, 'vbus')
        return {
            'pan_deg':      pan_pos,
            'tilt_deg':     tilt_pos,
            'pan_vel_dps':  pan_vel,
            'tilt_vel_dps': tilt_vel,
            'vbus_v':       vbus,
        }

    def print_state(self) -> None:
        """Affiche la télémétrie dans le terminal."""
        s = self.get_state()
        print(
            f"Pan={s['pan_deg']:+6.1f}°  "
            f"Tilt={s['tilt_deg']:+6.1f}°  "
            f"Vbus={s['vbus_v']:.1f}V"
        )

    # ── Détection ──────────────────────────────────────────
    def detect(self) -> dict[int, bool]:
        """
        Vérifie si les moteurs répondent sur le bus CAN.

        Returns:
            {1: True/False, 2: True/False}
        """
        result = {}
        for mid in [NECK_PAN_ID, NECK_TILT_ID]:
            try:
                self._client.read_param(mid, 'run_mode')
                result[mid] = True
            except Exception:
                result[mid] = False
        return result
