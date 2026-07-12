"""
dbot/config.py — Configuration centralisée du robot D-Bot
=========================================================
Source de vérité unique pour toutes les constantes matérielles.
Toujours importer depuis ici, jamais définir de constantes en dur
dans les modules individuels.
"""

import math

def _detect_can_channel() -> str:
    """Détecte dynamiquement l'interface réseau CAN gérée par le driver gs_usb (InnoMaker)."""
    import os
    try:
        for iface in os.listdir('/sys/class/net'):
            if iface.startswith('can'):
                driver_path = f'/sys/class/net/{iface}/device/driver'
                if os.path.exists(driver_path):
                    driver_link = os.readlink(driver_path)
                    if 'gs_usb' in driver_link:
                        return iface
    except Exception:
        pass
    return 'can1'  # Fallback de secours

# ── Bus CAN ────────────────────────────────────────────────
CAN_CHANNEL = _detect_can_channel()
CAN_BITRATE = 1_000_000   # 1 Mbps (standard RobStride)

# ── IDs Moteurs ────────────────────────────────────────────
# Cou
NECK_PAN_ID  = 1   # Pan  : rotation gauche/droite
NECK_TILT_ID = 2   # Tilt : inclinaison avant/arrière

# ── Limites Mécaniques Cou (Doc 32 §3) ────────────────────
# Ces valeurs sont également flashées en firmware via MotorStudio.
# Les fonctions clamp_* doivent être appliquées à chaque couche logicielle.
PAN_MIN_RAD  = math.radians(-80)   # -1.396 rad
PAN_MAX_RAD  = math.radians( 80)   # +1.396 rad
TILT_MIN_RAD = math.radians(-30)   # -0.524 rad
TILT_MAX_RAD = math.radians( 30)   # +0.524 rad

# ── Vitesses et Couples par Défaut ─────────────────────────
NECK_DEFAULT_KP  = 20.0    # Gain proportionnel position
NECK_DEFAULT_KD  =  0.5    # Gain dérivé vitesse
NECK_SPEED_LIMIT = math.radians(30.0)  # 30°/s max (vitesse nominale optimisée pour l'asservissement)

# ── Alimentation (référence Wanptek) ──────────────────────
POWER_VOLTAGE    = 48.0   # Volts (Tension nominale des RS-05)
POWER_CURRENT_NECK = 5.0  # Ampères — limite pour 2× RS-05

# ── Vision (OAK-D Pro) ─────────────────────────────────────
OAK_DEVICE_ID  = None   # None = premier détecté automatiquement
OAK_RESOLUTION = (1920, 1080)
OAK_FPS        = 30

# ── Audio (ReSpeaker) ──────────────────────────────────────
RESPEAKER_RATE    = 16000   # Hz
RESPEAKER_CHANNELS = 6      # 6 mics physiques (4 utilisés pour DOA)

# ── IMU (BMI270 - torse) ───────────────────────────────────
IMU_I2C_BUS     = 1
IMU_I2C_ADDRESS = 0x68
IMU_SAMPLE_RATE = 100   # Hz
