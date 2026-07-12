#!/usr/bin/env python3
"""
scripts/motors/calib_neck_zero.py — Calibrates the mechanical zero position for the neck motors.
==============================================================================================
This script defines the current physical position of the neck (Pan ID:1 & Tilt ID:2)
as the new zero reference (0.0 rad) and stores it in the motors' non-volatile memory (ROM).

IMPORTANT:
  1. The motors must be powered but DISABLED (free to rotate) during physical alignment.
  2. Align the head manually to its perfect center-front looking position.
  3. Run this script to write the zero position to the ROM of both motors.

Usage on Jetson:
    export PYTHONPATH=.
    python3 scripts/motors/calib_neck_zero.py
"""

import sys
import time
import can
import robstride
from dbot.motors.can_bus import get_bus, close_bus
from robstride.client import MotorMsg


def drain_bus(bus):
    """Reads and discards all pending messages in the CAN bus queue to avoid command desync."""
    while True:
        msg = bus.recv(timeout=0.005)
        if msg is None:
            break


def safe_disable(client: robstride.Client, motor_id: int):
    drain_bus(client.bus)
    client.disable(motor_id)


def safe_enable(client: robstride.Client, motor_id: int):
    drain_bus(client.bus)
    client.enable(motor_id)


def safe_read_param(client: robstride.Client, motor_id: int, param: str):
    drain_bus(client.bus)
    return client.read_param(motor_id, param)


def set_motor_zero(client: robstride.Client, motor_id: int):
    """
    Sends command 6 (ZeroPos) to the motor to set current position as zero.
    Payload: [1, 0, 0, 0, 0, 0, 0, 0] (write to ROM).
    """
    # Disable first (mandatory for zero calibration)
    print(f"  Ensuring motor ID {motor_id} is disabled...")
    safe_disable(client, motor_id)
    time.sleep(0.1)

    print(f"  Sending zero calibration command to ID {motor_id}...")
    # ZeroPos msg: msg_type=ZeroPos, id_data_1=host_can_id, id_data_2=motor_id, data=[1,0,0,0,0,0,0,0]
    msg = client._rs_msg(
        MotorMsg.ZeroPos, 
        client.host_can_id, 
        motor_id, 
        [1, 0, 0, 0, 0, 0, 0, 0]
    )
    client.bus.send(msg)
    
    # Wait for the motor to process and save to flash
    time.sleep(0.5)
    print(f"✅ Motor ID {motor_id} zero position calibrated and saved to ROM.")


def main():
    print("=" * 60)
    print("  D-Bot — Neck Motors Mechanical Zero Calibration")
    print("=" * 60)
    print("\nPREPARATION STEPS:")
    print("  1. Manually align the head/neck to its perfect zero reference position:")
    print("     - Look straight ahead (Pan/Yaw centered).")
    print("     - Look horizontally (Tilt/Pitch level).")
    print("  2. Ensure the motors are powered (Wanptek at 24V or 48V, OCP active).")
    print("  3. Keep the neck stable during calibration.\n")

    ans = input("Are you ready to calibrate the zero position? (y/N): ").strip().lower()
    if ans != 'y':
        print("Calibration cancelled.")
        sys.exit(0)

    print("\nInitializing CAN bus...")
    try:
        bus = get_bus()
        client = robstride.Client(bus)
    except Exception as e:
        print(f"❌ Error initializing CAN bus: {e}")
        sys.exit(1)

    try:
        # Check if motors respond first
        print("Checking motor presence...")
        for mid in [1, 2]:
            try:
                safe_read_param(client, mid, 'run_mode')
            except Exception:
                role = "Pan" if mid == 1 else "Tilt"
                print(f"❌ Motor ID {mid} ({role}) is not responding. Cannot calibrate.")
                close_bus()
                sys.exit(1)

        print("Both motors detected. Starting calibration...")
        print("-" * 60)
        
        # Calibrate Pan (ID 1)
        set_motor_zero(client, 1)
        
        # Calibrate Tilt (ID 2)
        set_motor_zero(client, 2)
        
        print("-" * 60)
        print("Verification phase:")
        print("  Enabling motors to hold the new zero position...")
        time.sleep(0.5)
        
        # Enable to test holding torque
        safe_enable(client, 1)
        safe_enable(client, 2)
        print("  Holding torque active at 0.0 rad. Tête figée au neutre.")
        
        time.sleep(3.0)
        
        # Disable
        safe_disable(client, 1)
        safe_disable(client, 2)
        print("  Motors disabled. Head is free.")
        print("\n🎉 Zero calibration successfully completed!")

    except Exception as e:
        print(f"\n❌ Calibration failed: {e}")
        # Make sure to disable motors in case of failure
        try:
            safe_disable(client, 1)
            safe_disable(client, 2)
        except Exception:
            pass
    finally:
        close_bus()


if __name__ == "__main__":
    main()
