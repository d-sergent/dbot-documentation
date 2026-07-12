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
    NECK_SPEED_LIMIT,
)
from dbot.motors.can_bus import get_bus, close_bus
from robstride.client import MotorMsg
import struct

def drain_bus(bus):
    """Reads and discards all pending messages in the CAN bus queue to avoid command desync."""
    while True:
        msg = bus.recv(timeout=0.005)
        if msg is None:
            break


class RobustClient(robstride.Client):
    """
    Subclass of robstride.Client that filters out CAN messages from other motor IDs
    instead of throwing 'Invalid motor ID received' exceptions due to queue congestion.
    """
    def _recv_matching(self, expected_msg_type: int, expected_motor_id: int, timeout=1.0):
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            resp = self.bus.recv(timeout=0.05)
            if not resp:
                continue
            if resp.is_error_frame:
                continue
            
            msg_type, msg_motor_id, host_id = self._parse_resp_abitration_id(resp.arbitration_id)
            if msg_type == expected_msg_type and msg_motor_id == expected_motor_id and host_id == self.host_can_id:
                return resp
        raise Exception(f"No response from motor {expected_motor_id} for command type {expected_msg_type} (Timeout)")

    def enable(self, motor_id: int, motor_model=1):
        drain_bus(self.bus)
        self.bus.send(self._rs_msg(MotorMsg.Enable, self.host_can_id, motor_id, [0, 0, 0, 0, 0, 0, 0, 0]))
        resp = self._recv_matching(MotorMsg.Feedback.value, motor_id)
        return self._parse_feedback_resp(resp, motor_id, motor_model)

    def disable(self, motor_id: int, motor_model=1):
        drain_bus(self.bus)
        self.bus.send(self._rs_msg(MotorMsg.Disable, self.host_can_id, motor_id, [0, 0, 0, 0, 0, 0, 0, 0]))
        resp = self._recv_matching(MotorMsg.Feedback.value, motor_id)
        return self._parse_feedback_resp(resp, motor_id, motor_model)

    def read_param(self, motor_id: int, param_id: int | str):
        drain_bus(self.bus)
        p_id = self._normalize_param_id(param_id)
        data = [p_id & 0xFF, p_id >> 8, 0, 0, 0, 0, 0, 0]
        self.bus.send(self._rs_msg(MotorMsg.ReadParam, self.host_can_id, motor_id, data))
        resp = self._recv_matching(MotorMsg.ReadParam.value, motor_id)
        
        resp_param_id = struct.unpack('<H', resp.data[:2])[0]
        if resp_param_id != p_id:
            raise Exception('Invalid param id')

        if p_id == 0x7005:
            value = robstride.RunMode(int(resp.data[4]))
        else:
            value = struct.unpack('<f', resp.data[4:])[0]
        return value

    def write_param(self, motor_id: int, param_id: int | str, param_value: float | robstride.RunMode | int, motor_model=1):
        drain_bus(self.bus)
        p_id = self._normalize_param_id(param_id)
        data = bytes([p_id & 0xFF, p_id >> 8, 0, 0])
        if p_id == 0x7005:
            if isinstance(param_value, robstride.RunMode):
                int_value = int(param_value.value)
            elif isinstance(param_value, int):
                int_value = param_value
            data += bytes([int_value, 0, 0, 0])
        else:
            data += struct.pack('<f', param_value)

        self.bus.send(self._rs_msg(MotorMsg.WriteParam, self.host_can_id, motor_id, data))
        resp = self._recv_matching(MotorMsg.Feedback.value, motor_id)
        return self._parse_feedback_resp(resp, motor_id, motor_model)


class NeckController:
    """
    Contrôle les 2 moteurs RS-05 du cou (Pan ID:1, Tilt ID:2).
    Les limites mécaniques sont TOUJOURS appliquées automatiquement.
    """

    def __init__(self):
        self._client = RobustClient(get_bus())
        self._enabled = False
        self.active_motors = []  # Liste des IDs détectés

    # ── Context Manager ────────────────────────────────────
    def __enter__(self):
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
        """Active les moteurs détectés en mode Position."""
        for mid in self.active_motors:
            self._client.write_param(mid, 'run_mode', robstride.RunMode.Position)
            # Double sécurité : injecter la limite de vitesse de sécurité directement en matériel (dans la RAM du moteur)
            self._client.write_param(mid, 'limit_spd', NECK_SPEED_LIMIT)
        
        if self.active_motors:
            time.sleep(0.05)
            
        for mid in self.active_motors:
            self._client.enable(mid)
        self._enabled = True

    def disable(self) -> None:
        """Désactive les moteurs détectés (coupe le holding torque)."""
        if self._enabled:
            for mid in self.active_motors:
                self._client.disable(mid)
            self._enabled = False

    # ── Commandes ──────────────────────────────────────────
    def look_at(self, pan_deg: float = 0.0, tilt_deg: float = 0.0) -> None:
        """
        Envoie une consigne de regard en degrés.
        Les bornes mécaniques et de vitesse sont appliquées automatiquement.

        Args:
            pan_deg:  Rotation gauche/droite en degrés (+= droite)
            tilt_deg: Inclinaison en degrés (+= bas)
        """
        pan_rad  = math.radians(pan_deg)
        tilt_rad = math.radians(tilt_deg)
        self.look_at_rad(pan_rad, tilt_rad)

    def look_at_rad(self, pan_rad: float = 0.0, tilt_rad: float = 0.0) -> None:
        """
        Envoie des consignes de position en radians avec interpolation linéaire (LERP)
        pour limiter la vitesse de déplacement physique au niveau logiciel.
        """
        target_pan = self.clamp_pan(pan_rad)
        target_tilt = self.clamp_tilt(tilt_rad)

        # 1. Lire la position actuelle estimée
        curr_pan = 0.0
        curr_tilt = 0.0
        
        if NECK_PAN_ID in self.active_motors:
            try:
                curr_pan = self._client.read_param(NECK_PAN_ID, 'mechpos')
            except Exception:
                curr_pan = target_pan # Fallback si échec de lecture
                
        if NECK_TILT_ID in self.active_motors:
            try:
                curr_tilt = self._client.read_param(NECK_TILT_ID, 'mechpos')
            except Exception:
                curr_tilt = target_tilt # Fallback si échec de lecture

        # 2. Calculer les distances de mouvement
        delta_pan = target_pan - curr_pan
        delta_tilt = target_tilt - curr_tilt
        max_delta = max(abs(delta_pan), abs(delta_tilt))

        # Si le mouvement est trop faible, envoi direct pour éviter l'interpolation
        if max_delta < 0.005:
            if NECK_PAN_ID in self.active_motors:
                self._client.write_param(NECK_PAN_ID, 'loc_ref', target_pan)
            if NECK_TILT_ID in self.active_motors:
                self._client.write_param(NECK_TILT_ID, 'loc_ref', target_tilt)
            return

        # 3. Calculer la trajectoire interpolée
        total_time = max_delta / NECK_SPEED_LIMIT
        time_step = 0.02  # Fréquence d'envoi de 50 Hz (toutes les 20 ms)
        steps = int(total_time / time_step)

        if steps <= 1:
            if NECK_PAN_ID in self.active_motors:
                self._client.write_param(NECK_PAN_ID, 'loc_ref', target_pan)
            if NECK_TILT_ID in self.active_motors:
                self._client.write_param(NECK_TILT_ID, 'loc_ref', target_tilt)
            return

        for step in range(1, steps + 1):
            t = step / steps
            interp_pan = curr_pan + delta_pan * t
            interp_tilt = curr_tilt + delta_tilt * t

            if NECK_PAN_ID in self.active_motors:
                self._client.write_param(NECK_PAN_ID, 'loc_ref', interp_pan)
            if NECK_TILT_ID in self.active_motors:
                self._client.write_param(NECK_TILT_ID, 'loc_ref', interp_tilt)
            
            time.sleep(time_step)

    def center(self) -> None:
        """Recentre la tête à 0°, 0°."""
        self.look_at(0.0, 0.0)

    # ── Télémétrie ─────────────────────────────────────────
    def get_state(self) -> dict:
        """
        Lit la position et la vitesse actuelles des moteurs connectés.

        Returns:
            dict avec clés: pan_deg, tilt_deg, pan_vel_dps, tilt_vel_dps, vbus_v
        """
        state = {
            'pan_deg': 0.0, 'tilt_deg': 0.0,
            'pan_vel_dps': 0.0, 'tilt_vel_dps': 0.0,
            'vbus_v': 0.0,
        }
        if NECK_PAN_ID in self.active_motors:
            state['pan_deg'] = math.degrees(self._client.read_param(NECK_PAN_ID,  'mechpos'))
            state['pan_vel_dps'] = math.degrees(self._client.read_param(NECK_PAN_ID,  'mechvel'))
            state['vbus_v'] = self._client.read_param(NECK_PAN_ID, 'vbus')
            
        if NECK_TILT_ID in self.active_motors:
            state['tilt_deg'] = math.degrees(self._client.read_param(NECK_TILT_ID, 'mechpos'))
            state['tilt_vel_dps'] = math.degrees(self._client.read_param(NECK_TILT_ID, 'mechvel'))
            if state['vbus_v'] == 0.0:
                state['vbus_v'] = self._client.read_param(NECK_TILT_ID, 'vbus')
                
        return state

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
        self.active_motors.clear()
        for mid in [NECK_PAN_ID, NECK_TILT_ID]:
            try:
                self._client.read_param(mid, 'run_mode')
                result[mid] = True
                self.active_motors.append(mid)
            except Exception:
                result[mid] = False
        return result
