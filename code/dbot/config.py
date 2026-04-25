"""
dbot/config.py — Configuration centralisée du robot D-Bot
=========================================================
Source de vérité unique pour toutes les constantes matérielles.
Toujours importer depuis ici, jamais définir de constantes en dur
dans les modules individuels.
"""

import math

# ── Bus CAN ────────────────────────────────────────────────
CAN_CHANNEL = 'can0'
CAN_BITRATE = 1_000_000   # 1 Mbps (standard RobStride)

# ── IDs Moteurs ────────────────────────────────────────────
# Cou
NECK_PAN_ID  = 1   # Pan  : rotation gauche/droite
NECK_TILT_ID = 2   # Tilt : inclinaison avant/arrière

# ── Limites Mécaniques Cou (Doc 32 §3) ────────────────────
# Ces valeurs sont également flashées en firmware via MotorStudio.
# Les fonctions clamp_* doivent être appliquées à chaque couche logicielle.
PAN_MIN_RAD  = math.radians(-40)   # -0.698 rad
PAN_MAX_RAD  = math.radians( 40)   # +0.698 rad
TILT_MIN_RAD = math.radians(-30)   # -0.524 rad
TILT_MAX_RAD = math.radians( 30)   # +0.524 rad

# ── Vitesses et Couples par Défaut ─────────────────────────
NECK_DEFAULT_KP  = 20.0    # Gain proportionnel position
NECK_DEFAULT_KD  =  0.5    # Gain dérivé vitesse
NECK_SPEED_LIMIT = math.radians(60)   # 60°/s max en opération normale

# ── Alimentation (référence Wanptek) ──────────────────────
POWER_VOLTAGE    = 24.0   # Volts
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
