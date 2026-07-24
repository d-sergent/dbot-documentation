"""
dbot/behaviors/audio_gaze.py — Boucle d'Orientation Audio (Audio Gaze Tracker)
==============================================================================
Gère l'asservissement angulaire du cou (Pan/Tilt) sur la direction d'origine
de la voix (DoA 0° à 359°) mesurée par le ReSpeaker XVF-3800.

Fonctionnalités :
- Conversion géométrique DoA 0-359° vers angle relatif Pan cou (-80° à +80°).
- Filtrage VAD & persistance acoustique (élimine le trépignement sur les bruits brefs).
- Deadband angulaire audio (ignore les variations < 12°).
- Machine à états d'attention multimodale (IDLE, AUDIO_ORIENTING, VISUAL_LOCKED).
"""

import time
import math
import logging
from typing import Tuple, Optional

from dbot.config import PAN_MIN_RAD, PAN_MAX_RAD, TILT_MIN_RAD, TILT_MAX_RAD

log = logging.getLogger('audio_gaze')


class AudioGazeTracker:
    """
    Gestionnaire d'asservissement angulaire du cou sur l'orientation sonore DoA.

    Args:
        min_vad_frames (int): Nombre de trames consécutives avec VAD=True requis pour valider une voix (défaut : 2 ~100-200 ms).
        deadband_doa_deg (float): Seuil d'écart angulaire minimal (défaut : 12.0°) pour engager un mouvement.
        invert_pan_sign (bool): Inverse le sens de rotation Pan si la carte ReSpeaker est orientée à 180° (défaut : False).
    """

    def __init__(
        self,
        min_vad_frames: int = 2,
        deadband_doa_deg: float = 12.0,
        invert_pan_sign: bool = False
    ):
        self.min_vad_frames = min_vad_frames
        self.deadband_doa_deg = deadband_doa_deg
        self.invert_pan_sign = invert_pan_sign

        self.min_pan_deg = math.degrees(PAN_MIN_RAD)    # -80.0°
        self.max_pan_deg = math.degrees(PAN_MAX_RAD)    # +80.0°
        self.min_tilt_deg = math.degrees(TILT_MIN_RAD)  # -20.0°
        self.max_tilt_deg = math.degrees(TILT_MAX_RAD)  # +30.0°

        self.vad_consecutive_count = 0
        self.last_valid_doa_deg: Optional[float] = None
        self.state = "IDLE"  # "IDLE", "AUDIO_ORIENTING", "VISUAL_LOCKED"

    def doa_to_relative_pan(self, doa_deg: float) -> float:
        """
        Convertit l'angle DoA ReSpeaker (0° à 359°) en un décalage relatif Pan.

        Conventions ReSpeaker XVF-3800 :
        - 0°   : Face (devant le micro)
        - 90°  : Droite
        - 180° : Arrière
        - 270° : Gauche

        Returns:
            float: Angle relatif en degrés (ex: -90.0° pour la droite, +90.0° pour la gauche)
        """
        doa_clean = float(doa_deg) % 360.0

        if doa_clean <= 180.0:
            rel_angle = -doa_clean  # Droite -> négatif
        else:
            rel_angle = 360.0 - doa_clean  # Gauche -> positif

        if self.invert_pan_sign:
            rel_angle = -rel_angle

        return rel_angle

    def process_audio_frame(
        self,
        doa_deg: float,
        is_speech: bool,
        current_pan_deg: float,
        current_tilt_deg: float,
        is_visual_locked: bool = False
    ) -> Tuple[float, float, str]:
        """
        Traitement d'une trame audio pour déterminer la nouvelle consigne de cou Pan/Tilt.

        Args:
            doa_deg (float): Angle DoA instantané (0-359°).
            is_speech (bool): Flag VAD (parole détectée).
            current_pan_deg (float): Angle Pan actuel du cou (télémétrie CAN).
            current_tilt_deg (float): Angle Tilt actuel du cou (télémétrie CAN).
            is_visual_locked (bool): Indique si le suivi visuel (Active Gaze) est actif et verrouillé sur un visage.

        Returns:
            Tuple[float, float, str]: (target_pan_deg, target_tilt_deg, current_state)
        """
        # Priorité absolue au suivi visuel une fois le visage verrouillé
        if is_visual_locked:
            self.state = "VISUAL_LOCKED"
            self.vad_consecutive_count = 0
            return current_pan_deg, current_tilt_deg, self.state

        # Filtrage VAD
        if is_speech:
            self.vad_consecutive_count += 1
        else:
            self.vad_consecutive_count = max(0, self.vad_consecutive_count - 1)

        # Si pas assez de confirmation vocale, rester en IDLE
        if self.vad_consecutive_count < self.min_vad_frames:
            self.state = "IDLE"
            return current_pan_deg, current_tilt_deg, self.state

        # Conversion de l'angle DoA
        rel_pan = self.doa_to_relative_pan(doa_deg)

        # Vérification du deadband angulaire
        if abs(rel_pan) < self.deadband_doa_deg:
            self.state = "IDLE"
            return current_pan_deg, current_tilt_deg, self.state

        # Calcul du nouvel angle absolu Pan
        target_pan = current_pan_deg + rel_pan

        # Bridage strict aux limites mécaniques (-80° à +80°)
        target_pan_clamped = max(self.min_pan_deg, min(self.max_pan_deg, target_pan))
        target_tilt_clamped = current_tilt_deg  # Le DoA USB ne donne que l'azimut (Pan)

        self.state = "AUDIO_ORIENTING"
        self.last_valid_doa_deg = doa_deg

        log.info(
            f"🎤 [AudioGaze] Son détecté DoA={doa_deg:.0f}° -> RelPan={rel_pan:+.1f}° | "
            f"Pan actuel={current_pan_deg:.1f}° -> Consigne={target_pan_clamped:.1f}°"
        )

        return target_pan_clamped, target_tilt_clamped, self.state
