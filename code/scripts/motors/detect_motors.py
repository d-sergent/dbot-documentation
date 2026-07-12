#!/usr/bin/env python3
"""
scripts/motors/detect_motors.py — Scan and detect RobStride motors on the CAN bus.
==================================================================================
Usage on Jetson:
    export PYTHONPATH=.
    python3 scripts/motors/detect_motors.py
"""

import sys
import robstride
from dbot.motors.can_bus import get_bus, close_bus


def main():
    print("=" * 60)
    print("  D-Bot — CAN Bus Motor Detection Scan")
    print("=" * 60)
    print("Initializing CAN bus...")

    try:
        bus = get_bus()
        client = robstride.Client(bus)
    except Exception as e:
        print(f"❌ Error initializing CAN bus: {e}")
        print("Please check that the interface 'can1' is UP and configured at 1 Mbps.")
        sys.exit(1)

    print("Scanning IDs 1 to 30...")
    print("-" * 60)
    
    found_any = False
    for mid in range(1, 31):
        # Print progress in-place
        sys.stdout.write(f"\rChecking ID {mid}...")
        sys.stdout.flush()
        try:
            # Try to read the run mode to check if the motor is responsive
            mode = client.read_param(mid, 'run_mode')
            sys.stdout.write("\r" + " " * 40 + "\r")  # Clear line
            print(f"✅ [ID {mid:02d}] RobStride motor detected! (Mode: {mode})")
            found_any = True
        except Exception:
            pass

    # Clear progress line
    sys.stdout.write("\r" + " " * 40 + "\r")
    sys.stdout.flush()

    print("-" * 60)
    if found_any:
        print("🎉 Scan completed successfully!")
    else:
        print("❌ No motors detected on the CAN bus.")
        print("Troubleshooting checklist:")
        print("  1. Is the Wanptek power supply turned ON (24V or 48V)?")
        print("  2. Is the current limit (3.0A) or OCP blocking?")
        print("  3. Are the XT30 power cables properly plugged into the motors?")
        print("  4. Are the CANH and CANL wires connected and terminated (60 ohms total)?")
        print("  5. Is the InnoMaker USB adapter plugged into the host and is 'can1' active?")

    close_bus()


if __name__ == "__main__":
    main()
