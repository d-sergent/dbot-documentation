"""
test_respeaker_sdk.py — Script de validation du SDK USB ReSpeaker XVF3800.

Ce script teste progressivement les fonctionnalités du SDK officiel :
  1. Connexion USB au chip XMOS
  2. Lecture de la version firmware
  3. Lecture en boucle du DOA + VAD matériel

Prérequis :
  pip install pyusb
  (Sous Linux, peut nécessiter : sudo usermod -a -G plugdev $USER + udev rules)

Usage :
  python3 code/scripts/audio/test_respeaker_sdk.py
"""

import sys
import time
import os

# Ajout du chemin pour les imports relatifs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from dbot.audio.respeaker_sdk import ReSpeakerSDK, ReSpeakerSDKError


def test_connexion(sdk: ReSpeakerSDK) -> bool:
    """Test de connexion USB et lecture de la version firmware."""
    print("\n🔌 Test 1 : Connexion USB et version firmware")
    try:
        version = sdk.get_version()
        print(f"   ✅ Firmware : {version}")
        return True
    except ReSpeakerSDKError as e:
        print(f"   ❌ {e}")
        return False


def test_vad_doa(sdk: ReSpeakerSDK, duration: int = 10) -> bool:
    """
    Test du VAD matériel et du DOA en temps réel.
    Parlez pendant le test pour voir le robot détecter votre direction.
    """
    print(f"\n🎤 Test 2 : VAD matériel + DOA ({duration}s — Parlez maintenant !)")
    print("   Format : [VAD] Direction")

    speech_detected = False
    try:
        for i in range(duration * 10):  # 10 lectures/seconde
            doa, is_speech = sdk.get_doa_and_vad()
            if is_speech:
                speech_detected = True
                bar = "▓" * (doa // 30)  # Représentation visuelle grossière
                print(f"   🗣️  {doa:3d}° {bar}")
            else:
                if i % 10 == 0:  # Affiche le silence 1x/s pour ne pas spammer
                    print(f"   🔇 silence — DOA : {doa:3d}°")
            time.sleep(0.1)

        if speech_detected:
            print(f"   ✅ VAD matériel fonctionnel — Parole détectée !")
        else:
            print(f"   ⚠  Aucune parole détectée pendant {duration}s.")

        return True
    except ReSpeakerSDKError as e:
        print(f"   ❌ {e}")
        return False


def main():
    print("=" * 50)
    print("  D-Bot — Test SDK USB ReSpeaker XVF3800")
    print("=" * 50)

    results = {}

    try:
        sdk = ReSpeakerSDK()
    except ReSpeakerSDKError as e:
        print(f"\n❌ Impossible de se connecter au ReSpeaker : {e}")
        print("\n💡 Conseil : Sur Linux, vérifiez les permissions udev :")
        print('   echo \'SUBSYSTEM=="usb", ATTR{idVendor}=="2886", MODE="0666"\' | sudo tee /etc/udev/rules.d/99-respeaker.rules')
        print("   sudo udevadm control --reload-rules && sudo udevadm trigger")
        sys.exit(1)

    results["connexion"] = test_connexion(sdk)
    results["vad_doa"] = test_vad_doa(sdk, duration=10)

    sdk.close()

    print("\n" + "=" * 50)
    print("  Résultats du Test SDK")
    print("=" * 50)
    all_ok = True
    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {name}")
        if not passed:
            all_ok = False

    if all_ok:
        print("\n✅ Stack SDK v2 opérationnelle !")
        print("   Prochaine étape : tester audio_io_v2.py")
    else:
        print("\n⚠  Certains tests ont échoué. Consultez la Doc 46.")


if __name__ == "__main__":
    main()
