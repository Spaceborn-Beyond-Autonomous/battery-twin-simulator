"""
BLDC Motor Mathematical Model (BTS-B - Day 2, revised)
Based on EMAX ECO II 2807-1300KV specifications.

Now accounts for mechanical load torque (from the propeller) when
solving for steady-state RPM and current draw, using a torque-balance
equation instead of assuming near-zero load.

Motor torque constant: Kt = 60 / (2*pi*Kv)   [N.m per Amp]
Motor torque produced: T_motor = Kt * (I - I_no_load)
At steady state: T_motor = T_load (propeller torque)
"""

import math
from powertrain.powertrain_config import MotorSpec


class BLDCMotor:
    """
    Simulates a brushless DC motor's electrical/mechanical behavior,
    solving for the current draw required to meet a mechanical load.
    """

    def __init__(self, spec: MotorSpec = None):
        self.spec = spec or MotorSpec()
        # Torque constant (N.m/A) derived from Kv rating
        self.kt = 60.0 / (2 * math.pi * self.spec.kv_rating)

    def compute(self, battery_voltage: float, throttle_percent: float,
                load_torque: float = 0.0) -> dict:
        """
        Args:
            battery_voltage: Volts supplied by the battery (from BTS-A)
            throttle_percent: 0-100 %
            load_torque: mechanical load from propeller (N.m). If 0,
                         motor spins at near no-load speed.

        Returns:
            dict with rpm, current_a, back_emf_v, applied_voltage_v
        """
        if battery_voltage <= 0:
            raise ValueError("battery_voltage must be positive")
        if not (0 <= throttle_percent <= 100):
            raise ValueError("throttle_percent must be 0-100")

        applied_voltage = battery_voltage * (throttle_percent / 100.0)

        kv = self.spec.kv_rating
        r = self.spec.resistance
        i_no_load = self.spec.no_load_current

        # Current needed to produce the required load torque
        # T = Kt * (I - I_no_load)  =>  I = T/Kt + I_no_load
        current_from_load = (load_torque / self.kt) + i_no_load if self.kt else i_no_load
        current = max(current_from_load, i_no_load)
        current = min(current, self.spec.max_current)

        # RPM from voltage equation: V = I*R + back_emf, back_emf = RPM/Kv
        back_emf = applied_voltage - (current * r)
        back_emf = max(back_emf, 0.0)
        rpm = back_emf * kv

        return {
            "rpm": round(rpm, 2),
            "current_a": round(current, 3),
            "back_emf_v": round(back_emf, 3),
            "applied_voltage_v": round(applied_voltage, 3),
        }


if __name__ == "__main__":
    motor = BLDCMotor()

    print("Test 1: 22.2V battery, 25% throttle, no load")
    print(motor.compute(battery_voltage=22.2, throttle_percent=25.0, load_torque=0.0))

    print("\nTest 2: 22.2V battery, 100% throttle, 0.1 N.m load")
    print(motor.compute(battery_voltage=22.2, throttle_percent=100.0, load_torque=0.1))
