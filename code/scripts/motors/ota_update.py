#!/usr/bin/env python3
"""
scripts/motors/ota_update.py — Flash firmware OTA RobStride via SocketCAN
=========================================================================
Adapte le script officiel RobStride (OTA/OTA.py) pour l'écosystème D-Bot sous
Linux / Jetson Orin Nano via SocketCAN (bitrate 1 Mbps obligatoire pendant l'OTA).

Protocole officiel (trames étendues 29 bits) :
  - Type 0  (0x00) : Lecture MCU UID 64 bits
  - Type 11 (0x0B) : OTA_START (envoi MCU UID)
  - Type 12 (0x0C) : OTA_INFO  (taille binaire + nombre de paquets de 8 octets)
  - Type 13 (0x0D) : OTA_ING   (transfert des paquets + reprise sur erreur)
  - Type 14 (0x0E) : OTA_END   (validation finale)

Usage sur Jetson / Linux :
    export PYTHONPATH=Code
    python3 Code/scripts/motors/ota_update.py --id 1 --bin "/chemin/vers/rs05_0.5.0.17.bin"
    python3 Code/scripts/motors/ota_update.py --id 2 --channel can1 --bin rs05_0.5.0.17.bin --yes
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import can

try:
    from dbot.config import CAN_CHANNEL as DEFAULT_CAN_CHANNEL
except Exception:
    DEFAULT_CAN_CHANNEL = "can1"


CANCOM_ANNOUNCE_DEVID = 0
CANCOM_OTA_START = 11
CANCOM_OTA_INFO = 12
CANCOM_OTA_ING = 13
CANCOM_OTA_END = 14

FEEDBACK_SUCCESS = 0x00
FEEDBACK_FAILED = 0xF0

MAX_BIN_SIZE = 0x80000
DEFAULT_BITRATE = 1_000_000
DEFAULT_HOST_ID = 0xFD
DEFAULT_TIMEOUT_S = 2.0
DEFAULT_RETRIES = 3


class RobStrideOTA:
    """Client de mise à jour firmware OTA sur bus SocketCAN pour moteurs RobStride."""

    def __init__(
        self,
        channel: str = DEFAULT_CAN_CHANNEL,
        host_id: int = DEFAULT_HOST_ID,
        bitrate: int = DEFAULT_BITRATE,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        retries: int = DEFAULT_RETRIES,
    ) -> None:
        self.channel = channel
        self.host_id = host_id
        self.bitrate = bitrate
        self.timeout_s = timeout_s
        self.retries = retries
        self.bus: can.BusABC | None = None
        self.bin_data: bytes = b""
        self.bin_size: int = 0
        self.pack_number: int = 0
        self.mcu_uid: bytes | None = None

    @staticmethod
    def build_id(mode: int, data: int, dev_id: int) -> int:
        """Construit l'identifiant CAN étendu 29 bits RobStride."""
        return (
            ((mode & 0x1F) << 24)
            | ((data & 0xFFFF) << 8)
            | (dev_id & 0xFF)
        ) & 0x1FFFFFFF

    @staticmethod
    def parse_id(can_id: int) -> tuple[int, int, int]:
        """Extrait (mode, data, dev_id) depuis un identifiant CAN étendu 29 bits."""
        can_id &= 0x1FFFFFFF
        mode = (can_id >> 24) & 0x1F
        data = (can_id >> 8) & 0xFFFF
        dev_id = can_id & 0xFF
        return mode, data, dev_id

    def open_bus(self) -> None:
        """Ouvre l'interface SocketCAN."""
        self.bus = can.interface.Bus(
            channel=self.channel,
            interface="socketcan",
            bitrate=self.bitrate,
        )

    def close_bus(self) -> None:
        """Ferme proprement l'interface SocketCAN."""
        if self.bus is not None:
            self.bus.shutdown()
            self.bus = None

    def drain_bus(self) -> None:
        """Vide le tampon de réception CAN avant de lancer une transaction OTA."""
        if self.bus is None:
            return
        while self.bus.recv(timeout=0.005) is not None:
            pass

    def load_bin(self, bin_path: Path) -> bool:
        """Charge et valide la taille du fichier firmware .bin."""
        if not bin_path.is_file():
            print(f"❌ Fichier firmware introuvable : {bin_path}")
            return False

        self.bin_data = bin_path.read_bytes()
        self.bin_size = len(self.bin_data)
        if self.bin_size == 0 or self.bin_size > MAX_BIN_SIZE:
            print(f"❌ Taille .bin invalide ({self.bin_size} octets, max {MAX_BIN_SIZE}).")
            return False

        self.pack_number = (self.bin_size + 7) // 8
        print(f"📦 Firmware : {bin_path.name} ({self.bin_size} octets, {self.pack_number} paquets)")
        return True

    def get_device_id(self, motor_id: int) -> bool:
        """Récupère l'identifiant unique 64 bits du MCU cible (Type 0)."""
        assert self.bus is not None
        print(f"📡 Interrogation MCU UID du moteur ID {motor_id}...")
        tx_id = self.build_id(CANCOM_ANNOUNCE_DEVID, self.host_id, motor_id)
        msg = can.Message(arbitration_id=tx_id, data=[0] * 8, is_extended_id=True)
        self.bus.send(msg)

        deadline = time.time() + self.timeout_s
        while time.time() < deadline:
            rx = self.bus.recv(timeout=0.1)
            if not rx or not rx.is_extended_id:
                continue
            mode, _data, dev_id = self.parse_id(rx.arbitration_id)
            if mode == CANCOM_ANNOUNCE_DEVID and dev_id == 0xFE:
                self.mcu_uid = bytes(rx.data)
                print(f"✅ MCU UID : {self.mcu_uid.hex()}")
                return True

        print("❌ Échec récupération MCU UID (vérifiez alimentation, câblage CAN et bitrate 1 Mbps).")
        return False

    def send_and_wait_ack(
        self,
        motor_id: int,
        mode: int,
        data: int,
        payload: list[int],
    ) -> tuple[bool, can.Message | None]:
        """Envoie une trame OTA et attend l'acquittement du moteur cible."""
        assert self.bus is not None
        tx_id = self.build_id(mode, data, motor_id)
        msg = can.Message(arbitration_id=tx_id, data=payload, is_extended_id=True)

        for _retry in range(self.retries):
            self.bus.send(msg)
            deadline = time.time() + self.timeout_s
            while time.time() < deadline:
                rx = self.bus.recv(timeout=0.1)
                if not rx or not rx.is_extended_id:
                    continue
                rx_mode, rx_data, rx_id = self.parse_id(rx.arbitration_id)
                if rx_mode != mode or rx_id != self.host_id:
                    continue
                result = (rx_data >> 8) & 0xFF
                rx_motor_id = rx_data & 0xFF
                if rx_motor_id != motor_id:
                    continue
                if result == FEEDBACK_SUCCESS:
                    return True, rx
                if result == FEEDBACK_FAILED:
                    return False, rx
            time.sleep(0.05)

        return False, None

    def flash(self, motor_id: int, bin_path: Path) -> bool:
        """Exécute la séquence OTA complète (START -> INFO -> ING -> END)."""
        if not self.load_bin(bin_path):
            return False

        self.open_bus()
        try:
            self.drain_bus()
            if not self.get_device_id(motor_id):
                return False

            assert self.mcu_uid is not None
            ok, _ = self.send_and_wait_ack(
                motor_id,
                CANCOM_OTA_START,
                self.host_id,
                list(self.mcu_uid),
            )
            if not ok:
                print("❌ Échec phase OTA_START.")
                return False

            info_payload = list(self.bin_size.to_bytes(4, "little"))
            info_payload += list(self.pack_number.to_bytes(4, "little"))
            ok, _ = self.send_and_wait_ack(
                motor_id,
                CANCOM_OTA_INFO,
                self.host_id,
                info_payload,
            )
            if not ok:
                print("❌ Échec phase OTA_INFO.")
                return False

            pack_cnt = 0
            while pack_cnt < self.pack_number:
                start_idx = pack_cnt * 8
                chunk = self.bin_data[start_idx : start_idx + 8]
                payload = list(chunk) + [0xFF] * (8 - len(chunk))
                ok, rx = self.send_and_wait_ack(motor_id, CANCOM_OTA_ING, pack_cnt, payload)
                if ok:
                    pack_cnt += 1
                    if pack_cnt % 250 == 0 or pack_cnt == self.pack_number:
                        pct = (pack_cnt * 100) // self.pack_number
                        print(f"⏳ Progression : {pack_cnt}/{self.pack_number} ({pct} %)")
                elif rx is not None:
                    resend_cnt = int.from_bytes(rx.data[0:2], "little")
                    print(f"🔁 Reprise demandée par le moteur au paquet {resend_cnt}")
                    pack_cnt = resend_cnt
                else:
                    print(f"❌ Timeout/échec pendant OTA_ING au paquet {pack_cnt}.")
                    return False

            end_payload = list(self.pack_number.to_bytes(4, "little")) + [0] * 4
            ok, _ = self.send_and_wait_ack(motor_id, CANCOM_OTA_END, 0, end_payload)
            if not ok:
                print("❌ Échec phase OTA_END.")
                return False

            print("🎉 Mise à jour firmware OTA terminée avec succès !")
            print("⚠️  RAPPEL OBLIGATOIRE : vérifier le Motor ID et recalibrer le zéro mécanique.")
            return True
        finally:
            self.close_bus()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mise à jour firmware OTA RobStride via SocketCAN (1 Mbps)."
    )
    parser.add_argument(
        "--id",
        type=lambda v: int(v, 0),
        required=True,
        help="ID CAN du moteur cible (ex: 1 ou 0x03).",
    )
    parser.add_argument(
        "--bin",
        type=Path,
        required=True,
        help="Chemin du fichier firmware .bin (ex: rs05_0.5.0.17.bin).",
    )
    parser.add_argument(
        "--channel",
        default=DEFAULT_CAN_CHANNEL,
        help=f"Interface SocketCAN (défaut : {DEFAULT_CAN_CHANNEL}).",
    )
    parser.add_argument(
        "--host-id",
        type=lambda v: int(v, 0),
        default=DEFAULT_HOST_ID,
        help="Host CAN ID (défaut : 0xFD).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Ne pas demander de confirmation interactive avant le flash.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print("=" * 64)
    print("  D-Bot — Mise à jour Firmware OTA RobStride (SocketCAN 1 Mbps)")
    print("=" * 64)
    print(f"  Interface : {args.channel}")
    print(f"  Moteur ID : {args.id} (0x{args.id:02X})")
    print(f"  Firmware  : {args.bin}")
    print("  ⚠️  Vérifiez que l'alimentation est stable et l'arbre libre.")

    if not args.yes:
        ans = input("\nConfirmer le flash OTA ? (o/N) : ").strip().lower()
        if ans not in ("o", "oui", "y", "yes"):
            print("Flash annulé.")
            return 0

    ota = RobStrideOTA(channel=args.channel, host_id=args.host_id)
    return 0 if ota.flash(args.id, args.bin) else 1


if __name__ == "__main__":
    sys.exit(main())
