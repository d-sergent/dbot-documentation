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
    PAN_LOC_KP, PAN_SPD_KP, PAN_SPD_KI,
    TILT_LOC_KP, TILT_SPD_KP, TILT_SPD_KI,
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
        self.emergency_stopped = False
        self.is_moving = False
        self.can_lock = threading.Lock()
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
        with self.can_lock:
            self.emergency_stopped = False
            self.is_moving = False
            for mid in self.active_motors:
                self._client.write_param(mid, 'run_mode', robstride.RunMode.Position)
                self._client.write_param(mid, 'limit_spd', NECK_SPEED_LIMIT * 3.0)
                if mid == NECK_PAN_ID:
                    self._client.write_param(mid, 'loc_kp', PAN_LOC_KP)
                    self._client.write_param(mid, 'spd_kp', PAN_SPD_KP)
                    self._client.write_param(mid, 'spd_ki', PAN_SPD_KI)
                elif mid == NECK_TILT_ID:
                    self._client.write_param(mid, 'loc_kp', TILT_LOC_KP)
                    self._client.write_param(mid, 'spd_kp', TILT_SPD_KP)
                    self._client.write_param(mid, 'spd_ki', TILT_SPD_KI)
            
            if self.active_motors:
                time.sleep(0.05)
                
            for mid in self.active_motors:
                self._client.enable(mid)
            self._enabled = True

    def disable(self) -> None:
        """Désactive INCONDITIONNELLEMENT tous les moteurs du cou (coupe le couple et le bruit PWM).
        
        IMPORTANT: N'attend JAMAIS can_lock pour ne pas se bloquer derrière un mouvement en cours.
        Les trames Disable sont envoyées directement sur le bus, ce qui interrompt tout mouvement.
        """
        self.emergency_stopped = True  # Interrompt la boucle LERP immédiatement
        self.is_moving = False
        self._enabled = False
        target_ids = list(set(self.active_motors + [NECK_PAN_ID, NECK_TILT_ID]))
        
        # Envoi DIRECT sans attendre can_lock : la trame Disable coupe tout
        for mid in target_ids:
            try:
                drain_bus(self._client.bus)
                for _ in range(3):
                    self._client.bus.send(self._client._rs_msg(
                        MotorMsg.Disable, self._client.host_can_id, mid, [0]*8
                    ))
                    time.sleep(0.002)
            except Exception as e:
                print(f"⚠️ Erreur d'extinction CAN sur le moteur {mid}: {e}")

    # ── Commandes ──────────────────────────────────────────
    def look_at(self, pan_deg: float = 0.0, tilt_deg: float = 0.0) -> None:
        """
        Envoie une consigne de regard en degrés.
        Les bornes mécaniques et de vitesse sont appliquées automatiquement.
        """
        pan_rad  = math.radians(pan_deg)
        tilt_rad = math.radians(tilt_deg)
        self.look_at_rad(pan_rad, tilt_rad)

    def look_at_rad(self, pan_rad: float = 0.0, tilt_rad: float = 0.0) -> None:
        """
        Envoie des consignes de position en radians avec interpolation smooth (ease in/out).
        
        ARCHITECTURE THREAD-SAFE :
        - can_lock ne protège QUE chaque écriture CAN individuelle (jamais la boucle entière)
        - La boucle LERP s'exécute hors du verrou pour ne jamais bloquer disable()
        - emergency_stopped interrompt la boucle à chaque itération
        """
        if self.emergency_stopped:
            print("🚨 Mouvement refusé : Le contrôleur est en état d'Arrêt d'Urgence.")
            return

        target_pan = self.clamp_pan(pan_rad)
        target_tilt = self.clamp_tilt(tilt_rad)

        def shortest_angular_distance(from_rad: float, to_rad: float) -> float:
            d = (to_rad - from_rad) % (2.0 * math.pi)
            if d > math.pi:
                d -= 2.0 * math.pi
            return d

        # ── 1. Lire la position actuelle (verrou sur chaque lecture individuelle) ──
        curr_pan = target_pan
        curr_tilt = target_tilt
        if NECK_PAN_ID in self.active_motors:
            try:
                with self.can_lock:
                    curr_pan = self._client.read_param(NECK_PAN_ID, 'mechpos')
            except Exception:
                curr_pan = target_pan
        if NECK_TILT_ID in self.active_motors:
            try:
                with self.can_lock:
                    curr_tilt = self._client.read_param(NECK_TILT_ID, 'mechpos')
            except Exception:
                curr_tilt = target_tilt

        # ── 2. Calculer le delta (shortest path) et appliquer les gardes-fous ──
        delta_pan  = shortest_angular_distance(curr_pan,  target_pan)
        delta_tilt = shortest_angular_distance(curr_tilt, target_tilt)

        MAX_SAFE_DELTA_PAN  = math.radians(45.0)
        MAX_SAFE_DELTA_TILT = math.radians(35.0)

        if abs(delta_pan) > MAX_SAFE_DELTA_PAN:
            print(f"⚠️ Delta Pan {math.degrees(delta_pan):.1f}° bridé à {math.degrees(MAX_SAFE_DELTA_PAN):.1f}°.")
            delta_pan = math.copysign(MAX_SAFE_DELTA_PAN, delta_pan)
        if abs(delta_tilt) > MAX_SAFE_DELTA_TILT:
            print(f"⚠️ Delta Tilt {math.degrees(delta_tilt):.1f}° bridé à {math.degrees(MAX_SAFE_DELTA_TILT):.1f}°.")
            delta_tilt = math.copysign(MAX_SAFE_DELTA_TILT, delta_tilt)

        max_delta = max(abs(delta_pan), abs(delta_tilt))

        # ── 3. Mouvement trivial : envoi direct (verrou individuel) ──
        if max_delta < 0.005:
            if NECK_PAN_ID in self.active_motors:
                with self.can_lock:
                    self._client.write_param(NECK_PAN_ID, 'loc_ref', target_pan)
            if NECK_TILT_ID in self.active_motors:
                with self.can_lock:
                    self._client.write_param(NECK_TILT_ID, 'loc_ref', target_tilt)
            return

        # ── 4. Boucle LERP — can_lock sur CHAQUE écriture, jamais sur la boucle ──
        total_time = max_delta / NECK_SPEED_LIMIT
        time_step  = 0.02   # 50 Hz (suffisant pour du mouvement de tête)
        steps      = max(1, int(total_time / time_step))

        start_pan  = target_pan  - delta_pan
        start_tilt = target_tilt - delta_tilt

        self.is_moving = True
        try:
            for step in range(1, steps + 1):
                if self.emergency_stopped:
                    print("🚨 E-STOP : interruption immédiate de la boucle LERP.")
                    return

                t        = step / steps
                t_smooth = (1.0 - math.cos(math.pi * t)) / 2.0
                ip = start_pan  + delta_pan  * t_smooth
                it = start_tilt + delta_tilt * t_smooth

                if NECK_PAN_ID in self.active_motors:
                    with self.can_lock:
                        self._client.write_param(NECK_PAN_ID,  'loc_ref', ip)
                if NECK_TILT_ID in self.active_motors:
                    with self.can_lock:
                        self._client.write_param(NECK_TILT_ID, 'loc_ref', it)

                time.sleep(time_step)
        finally:
            self.is_moving = False

    def center(self) -> None:
        """Recentre la tête à 0°, 0°."""
        self.look_at(0.0, 0.0)

    # ── Télémétrie ─────────────────────────────────────────
    def get_state(self) -> dict:
        """
        Lit la position et la vitesse actuelles des moteurs connectés.
        """
        state = {
            'pan_deg': 0.0, 'tilt_deg': 0.0,
            'pan_vel_dps': 0.0, 'tilt_vel_dps': 0.0,
            'vbus_v': 0.0,
        }
        with self.can_lock:
            if NECK_PAN_ID in self.active_motors:
                try:
                    state['pan_deg'] = math.degrees(self._client.read_param(NECK_PAN_ID,  'mechpos'))
                    state['pan_vel_dps'] = math.degrees(self._client.read_param(NECK_PAN_ID,  'mechvel'))
                    state['vbus_v'] = self._client.read_param(NECK_PAN_ID, 'vbus')
                except Exception:
                    pass
                
            if NECK_TILT_ID in self.active_motors:
                try:
                    state['tilt_deg'] = math.degrees(self._client.read_param(NECK_TILT_ID, 'mechpos'))
                    state['tilt_vel_dps'] = math.degrees(self._client.read_param(NECK_TILT_ID, 'mechvel'))
                    if state['vbus_v'] == 0.0:
                        state['vbus_v'] = self._client.read_param(NECK_TILT_ID, 'vbus')
                except Exception:
                    pass
                
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
