import can
import robstride
import time

# Utilisation de 'can1' (l'adaptateur InnoMaker USB sur la Jetson)
with can.Bus(interface='socketcan', channel='can1') as bus:
    rs = robstride.Client(bus)

    for motor_id in [1, 2]:
        print(f"\n--- Test Moteur ID:{motor_id} ---")
        try:
            mode = rs.read_param(motor_id, 'run_mode')
            print(f"✅ Moteur ID:{motor_id} répond ! Mode = {mode}")
        except Exception as e:
            print(f"  Lecture directe échouée : {e}")
            print(f"  → Tentative d'activation...")
            try:
                resp = rs.enable(motor_id)
                print(f"✅ ID:{motor_id} activé ! Angle={resp.angle:.3f} rad | Temp={resp.temp:.1f}°C")
                time.sleep(0.5)
                rs.disable(motor_id)
            except Exception as e2:
                print(f"❌ ID:{motor_id} ne répond pas : {e2}")
