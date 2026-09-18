"""
PWM Response / Motor Dynamics Model (BTS-B - Day 9)

Models the motor's transient response to a throttle (PWM) change:
RPM doesn't jump instantly to its target value -- it accelerates
toward it based on the rotor+propeller's moment of inertia and the
available torque margin (motor torque - propeller drag torque).

Equation of motion:
    J * dω/dt = T_motor - T_prop
Where J = combined rotor+propeller inertia (kg.m^2), ω = angular velocity (rad/s)
"""

import math
from powertrain.propeller_model import Propeller
from powertrain.motor_model import BLDCMotor


class PWMResponseModel:
    """
    Simulates motor spin-up/spin-down dynamics over time using a
    simple Euler integration of the torque-inertia equation.
    """

    # Combined rotor + propeller moment of inertia (kg.m^2), typical
    # small estimate for a 2807-class motor with a 10-inch propeller.
    INERTIA_KG_M2 = 0.000025

    def __init__(self, motor: BLDCMotor = None, propeller: Propeller = None):
        self.motor = motor or BLDCMotor()
        self.propeller = propeller or Propeller()

    def simulate_step_response(self, battery_voltage: float,
                                target_throttle_percent: float,
                                dt: float = 0.01, duration: float = 1.0,
                                air_density: float = 1.225) -> list:
        """
        Simulates a step change from 0 RPM to the target throttle,
        returning a time series of RPM values.
        """
        applied_voltage = battery_voltage * (target_throttle_percent / 100.0)
        spec = self.motor.spec

        rpm = 0.0
        omega = 0.0  # rad/s
        history = []

        steps = int(duration / dt)
        for step in range(steps):
            t = step * dt

            # Torque motor can deliver at current RPM (voltage-current-limited)
            back_emf = rpm / spec.kv_rating
            current = (applied_voltage - back_emf) / spec.resistance
            current = max(current, spec.no_load_current)
            current = min(current, spec.max_current)
            motor_torque = self.motor.kt * (current - spec.no_load_current)
            motor_torque = max(motor_torque, 0.0)

            # Propeller drag torque at current RPM
            prop_out = self.propeller.compute(rpm=rpm, air_density=air_density)
            prop_torque = prop_out["torque_nm"]

            # Newton's second law for rotation: J*dω/dt = T_motor - T_prop
            net_torque = motor_torque - prop_torque
            angular_accel = net_torque / self.INERTIA_KG_M2
            omega += angular_accel * dt
            omega = max(omega, 0.0)

            rpm = omega * 60.0 / (2 * math.pi)

            history.append({"t": round(t, 3), "rpm": round(rpm, 1)})

        return history


if __name__ == "__main__":
    model = PWMResponseModel()

    history = model.simulate_step_response(
        battery_voltage=22.2, target_throttle_percent=50.0,
        dt=0.01, duration=0.3
    )

    print("Spin-up response: 0% -> 50% throttle step")
    for point in history[::5]:  # print every 5th sample
        print(f"  t={point['t']:.2f}s  RPM={point['rpm']:.1f}")

    print(f"\nFinal RPM after {history[-1]['t']:.2f}s: {history[-1]['rpm']:.1f}")
    print("(Expected steady-state from Day 5-6: ~9537 RPM)")
