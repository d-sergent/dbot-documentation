"""
Code/scripts/audio/test_audio_gaze.py — Script de Test & Validation Terrain Audio Gaze Tracking
================================================================──────────────────────────────
Teste la conversion angulaire DoA 0-359° vers les consignes Pan/Tilt du cou RS-05,
et valide le couplage ReSpeaker XVF-3800 + Boucle Moteur CAN 100 Hz.

Usage :
    /opt/homebrew/bin/python3.11 Code/scripts/audio/test_audio_gaze.py --test-unit
    python3 Code/scripts/audio/test_audio_gaze.py --live
"""

import sys
import time
import argparse
import logging
from pathlib import Path

# Ajouter le dossier Code au sys.path
CODE_DIR = Path(__file__).resolve().parents[2]
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from dbot.behaviors.audio_gaze import AudioGazeTracker
from dbot.audio.respeaker_sdk import ReSpeakerSDK, ReSpeakerSDKError

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
log = logging.getLogger('test_audio_gaze')


def run_unit_tests():
    """Exécute les tests unitaires de la logique mathématique AudioGazeTracker."""
    print("\n--- 🧪 Execution des Tests Unitaires AudioGazeTracker ---")
    tracker = AudioGazeTracker(min_vad_frames=1, deadband_doa_deg=5.0)

    # Test 1 : Conversions angulaires DoA
    test_cases = [
        (0.0, 0.0, "Face (0°) -> RelPan 0.0°"),
        (90.0, -90.0, "Droite (90°) -> RelPan -90.0°"),
        (270.0, 90.0, "Gauche (270°) -> RelPan +90.0°"),
        (45.0, -45.0, "Avant-Droite (45°) -> RelPan -45.0°"),
        (315.0, 45.0, "Avant-Gauche (315°) -> RelPan +45.0°"),
        (180.0, -180.0, "Arriere (180°) -> RelPan -180.0°"),
    ]

    for doa, expected_rel, desc in test_cases:
        rel = tracker.doa_to_relative_pan(doa)
        assert abs(rel - expected_rel) < 1e-3, f"❌ Échec pour {desc} : obtenu {rel}, attendu {expected_rel}"
        print(f"  ✅ {desc}")

    # Test 2 : Seuil Deadband
    pan, tilt, state = tracker.process_audio_frame(
        doa_deg=2.0, is_speech=True, current_pan_deg=0.0, current_tilt_deg=0.0
    )
    assert state == "IDLE", f"❌ Échec Deadband : attendu IDLE, obtenu {state}"
    print("  ✅ Deadband angulaire (2° < 5°) : IDLE respecté.")

    # Test 3 : Traitement d'un son à Droite (90°) depuis position neutre (0°) -> Consigne bridée à -80°
    pan, tilt, state = tracker.process_audio_frame(
        doa_deg=90.0, is_speech=True, current_pan_deg=0.0, current_tilt_deg=0.0
    )
    assert state == "AUDIO_ORIENTING", f"❌ Échec transition d'état : attendu AUDIO_ORIENTING, obtenu {state}"
    assert pan == -80.0, f"❌ Échec bridage mécanique : attendu -80.0°, obtenu {pan}"
    print("  ✅ Consigne sonore 90° -> Pan bridé correctement à -80.0° (limite mécanique).")

    # Test 4 : Priorité au suivi visuel (is_visual_locked=True)
    pan, tilt, state = tracker.process_audio_frame(
        doa_deg=90.0, is_speech=True, current_pan_deg=0.0, current_tilt_deg=0.0, is_visual_locked=True
    )
    assert state == "VISUAL_LOCKED", f"❌ Échec priorité visuelle : attendu VISUAL_LOCKED, obtenu {state}"
    print("  ✅ Priorité absolue du verrouillage visuel (VISUAL_LOCKED) validée.")

    print("\n🎉 TOUS LES TESTS UNITAIRES ONT RÉUSSI AVEC SUCCÈS !\n")


def run_live_test():
    """Exécute l'écoute en direct du ReSpeaker XVF-3800 et simule l'asservissement du cou."""
    print("\n--- 🎤 Test Terrain en Direct : ReSpeaker USB DoA ➔ Audio Gaze ---")
    tracker = AudioGazeTracker(min_vad_frames=2, deadband_doa_deg=10.0)

    try:
        sdk = ReSpeakerSDK()
        print(f"📟 Firmware ReSpeaker : {sdk.get_version()}")
        print("🗣️  Parlez autour du robot pour tester l'orientation du cou (Ctrl+C pour quitter)...")

        curr_pan = 0.0
        curr_tilt = 0.0

        while True:
            doa, is_speech = sdk.get_doa_and_vad()
            target_pan, target_tilt, state = tracker.process_audio_frame(
                doa_deg=doa,
                is_speech=is_speech,
                current_pan_deg=curr_pan,
                current_tilt_deg=curr_tilt
            )

            status_str = "🗣️  PAROLE" if is_speech else "🔇 silence"
            print(
                f"\r[{status_str}] DoA: {doa:3d}° | État: {state:15s} | Consigne Pan: {target_pan:+6.1f}°",
                end="",
                flush=True
            )
            time.sleep(0.05)

    except ReSpeakerSDKError as e:
        print(f"\n❌ Erreur SDK ReSpeaker : {e}")
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du test terrain.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Audio Gaze Tracking D-Bot")
    parser.add_argument("--test-unit", action="store_true", help="Exécute la suite de tests unitaires")
    parser.add_argument("--live", action="store_true", help="Exécute le suivi en direct avec le ReSpeaker USB")

    args = parser.parse_args()

    if args.test_unit or not sys.argv[1:]:
        run_unit_tests()

    if args.live:
        run_live_test()
