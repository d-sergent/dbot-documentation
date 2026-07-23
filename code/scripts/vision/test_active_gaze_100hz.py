"""
scripts/vision/test_active_gaze_100hz.py — Test Unitaire du Découplage Temporel Boucle 100 Hz
==========================================================================================
Vérifie que la boucle d'asservissement CAN du cou s'exécute à 100 Hz (période de 10 ms)
en parfaite autonomie, indépendamment de la cadence de l'inférence visuelle IA (30 Hz).

Exécution :
    python3 code/scripts/vision/test_active_gaze_100hz.py
"""

import time
import threading
import numpy as np
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

class DecoupledGazeLoop100Hz:
    """
    Simulateur de boucle découplée 100 Hz pour l'asservissement du cou.
    """
    def __init__(self, target_can_freq_hz=100.0):
        self.period_s = 1.0 / target_can_freq_hz
        self.is_running = False
        self.target_position = (0.0, 0.0)  # Position filtrée mise à jour par l'IA (30 Hz)
        self.current_position = (0.0, 0.0) # Interpolation fine transmise au CAN (100 Hz)
        self.can_timestamps = []
        self.lock = threading.Lock()

    def update_vision_target(self, pan_deg, tilt_deg):
        """Thread Perception (30 Hz) : met à jour la consigne."""
        with self.lock:
            self.target_position = (pan_deg, tilt_deg)

    def _can_control_loop(self):
        """Thread Moteur CAN (100 Hz / 10 ms) : s'exécute en boucle autonome."""
        t_next = time.perf_counter()
        while self.is_running:
            t_now = time.perf_counter()
            self.can_timestamps.append(t_now)

            with self.lock:
                # Interpolation douce 100 Hz vers la consigne visuelle
                t_pan, t_tilt = self.target_position
                c_pan, c_tilt = self.current_position

                alpha = 0.20  # Lissage 100 Hz
                new_pan = c_pan + alpha * (t_pan - c_pan)
                new_tilt = c_tilt + alpha * (t_tilt - c_tilt)
                self.current_position = (new_pan, new_tilt)

            t_next += self.period_s
            sleep_time = t_next - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._can_control_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if hasattr(self, 'thread'):
            self.thread.join()

def test_100hz_decoupled_loop():
    print("⏳ [Test Unitaire 4] Démarrage de la boucle découplée 100 Hz CAN...")
    loop = DecoupledGazeLoop100Hz(target_can_freq_hz=100.0)
    loop.start()

    # Simulation d'un flux de détection visuelle IA lent (30 Hz / 33 ms)
    print("🎥 Simulation de l'inférence visuelle IA (cadence 30 Hz)...")
    t_start = time.perf_counter()
    for i in range(10):
        # L'IA envoie une nouvelle consigne toutes les ~33 ms
        simulated_pan = math_target_x = 10.0 * (i + 1)
        simulated_tilt = -5.0 * (i + 1)
        loop.update_vision_target(simulated_pan, simulated_tilt)
        time.sleep(0.033)

    loop.stop()

    # Analyse des timestamps de la boucle CAN 100 Hz
    timestamps = loop.can_timestamps
    intervals_ms = [(timestamps[i+1] - timestamps[i]) * 1000.0 for i in range(len(timestamps)-1)]

    avg_freq_hz = len(timestamps) / (timestamps[-1] - timestamps[0])
    avg_interval_ms = np.mean(intervals_ms)
    std_interval_ms = np.std(intervals_ms)

    print("\n========================================================")
    print(f"🎯 RÉSULTATS TEST UNITAIRE 4 (Boucle 100 Hz Découplée)")
    print(f"   • Nombre total d'itérations CAN : {len(timestamps)}")
    print(f"   • Fréquence moyenne mesurée    : {avg_freq_hz:.1f} Hz (Cible : 100 Hz)")
    print(f"   • Période d'itération moyenne  : {avg_interval_ms:.2f} ms (Cible : 10.00 ms)")
    print(f"   • Gitter temporel (Écart-type) : ±{std_interval_ms:.2f} ms")
    print("========================================================\n")

    assert 95.0 <= avg_freq_hz <= 105.0, "La boucle CAN doit se maintenir entre 95 Hz et 105 Hz !"
    print("✅ [Test Unitaire 4] VALIDE avec succès !")

if __name__ == "__main__":
    try:
        test_100hz_decoupled_loop()
    except Exception as e:
        print(f"❌ Échec Test Unitaire 4 : {e}")
        sys.exit(1)
