"""
respeaker_sdk.py — Interface USB directe avec le chip XMOS XVF3800.

Sources :
  - https://wiki.seeedstudio.com/respeaker_xvf3800_python_sdk/
  - https://github.com/respeaker/reSpeaker_XVF3800_USB_4MIC_ARRAY

Dépendances : pip install pyusb

Fonctionnalités :
  - VAD matériel on-chip (plus fiable que webrtcvad, intègre l'AEC)
  - DOA (Direction of Arrival) : angle 0-359° de la voix
  - Version firmware, Reboot chip
"""

import struct
import sys
import time
from typing import Tuple

try:
    import usb.core
    import usb.util
    PYUSB_AVAILABLE = True
except ImportError:
    PYUSB_AVAILABLE = False


class ReSpeakerSDKError(Exception):
    """Exception levée en cas d'erreur dans le SDK ReSpeaker."""
    pass


# Registres du chip XVF3800 (source : wiki officiel Seeed Studio)
# Format : (resid, cmdid, length, access, type)
PARAMETERS = {
    "VERSION":     (48,  0,  3, "ro", "uint8"),
    "AEC_AZIMUTH": (33, 75, 16, "ro", "radians"),
    "DOA_VALUE":   (20, 18,  4, "ro", "uint16"),  # [angle_doa, vad_flag]
    "REBOOT":      (48,  7,  1, "wo", "uint8"),
}

RESPEAKER_VID = 0x2886
RESPEAKER_PID = 0x001A


class ReSpeakerSDK:
    """
    Interface USB directe avec le chip XMOS XVF3800.

    Permet de lire le DOA, le VAD matériel, sans passer par ALSA/PulseAudio.

    Args:
        timeout (int): Timeout USB en ms (défaut : 100000).

    Raises:
        ReSpeakerSDKError: Si pyusb n'est pas installé ou le device non trouvé.
    """

    def __init__(self, timeout: int = 100000):
        if not PYUSB_AVAILABLE:
            raise ReSpeakerSDKError(
                "[SDK] pyusb non installé. Lancez : pip install pyusb"
            )
        self.timeout = timeout
        self.dev = usb.core.find(idVendor=RESPEAKER_VID, idProduct=RESPEAKER_PID)
        if self.dev is None:
            raise ReSpeakerSDKError(
                "[SDK] ReSpeaker XVF3800 non détecté. "
                "Vérifiez le branchement USB-A et le firmware USB."
            )
        print(f"✅ [SDK] ReSpeaker XVF3800 détecté sur le bus USB.")

    def _read(self, name: str):
        """Lit un registre du chip via USB Control Transfer."""
        if name not in PARAMETERS:
            raise ReSpeakerSDKError(f"[SDK] Registre inconnu : {name}")
        resid, cmdid, length, access, data_type = PARAMETERS[name]
        if access == "wo":
            raise ReSpeakerSDKError(f"[SDK] {name} est en écriture seule.")
        try:
            response = self.dev.ctrl_transfer(
                usb.util.CTRL_IN | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
                0, 0x80 | cmdid, resid, length + 1, self.timeout
            )
        except Exception as e:
            raise ReSpeakerSDKError(f"[SDK] Erreur lecture USB : {e}")
        byte_data = response.tobytes()
        if data_type == "uint8":
            return list(response)
        elif data_type == "uint16":
            num_words = length // 2
            return list(struct.unpack(f"<{'H' * num_words}", byte_data[1:1 + num_words * 2]))
        elif data_type == "radians":
            num_floats = length // 4
            return list(struct.unpack(f"<{'f' * num_floats}", byte_data[1:1 + num_floats * 4]))
        return None

    def get_doa_and_vad(self) -> Tuple[int, bool]:
        """
        Lit l'angle DOA et le flag VAD directement depuis le chip XMOS.

        Returns:
            Tuple[int, bool]: (angle_doa 0-359°, is_speech True/False)
        """
        result = self._read("DOA_VALUE")
        return result[0], bool(result[1])

    def get_version(self) -> str:
        """Lit la version du firmware installé."""
        result = self._read("VERSION")
        return ".".join(str(b) for b in result if b != 0)

    def reboot(self):
        """Redémarre le chip XVF3800."""
        resid, cmdid, _, _, _ = PARAMETERS["REBOOT"]
        try:
            self.dev.ctrl_transfer(
                usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
                0, cmdid, resid, [1], self.timeout
            )
            print("🔄 [SDK] Reboot du chip XVF3800 envoyé.")
        except Exception as e:
            raise ReSpeakerSDKError(f"[SDK] Erreur reboot : {e}")

    def close(self):
        """Libère les ressources USB."""
        if self.dev:
            usb.util.dispose_resources(self.dev)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


if __name__ == "__main__":
    print("\n--- Test SDK ReSpeaker XVF3800 ---")
    try:
        with ReSpeakerSDK() as sdk:
            print(f"📟 Firmware : {sdk.get_version()}")
            print("\n🎤 Écoute DOA + VAD pendant 10s...")
            for _ in range(100):
                doa, is_speech = sdk.get_doa_and_vad()
                status = "🗣️  PAROLE" if is_speech else "🔇 silence"
                print(f"  {status} — Direction : {doa:3d}°")
                time.sleep(0.1)
        print("\n✅ Test SDK réussi !")
    except ReSpeakerSDKError as e:
        print(f"❌ {e}")
        sys.exit(1)
