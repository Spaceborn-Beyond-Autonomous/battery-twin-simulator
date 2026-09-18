"""
Load-Dependent Current Consumption Model (BTS-B - Day 8)

Models total current draw as a function of mechanical load (thrust
demand), not just throttle percentage -- accounting for how external
factors (payload, wind resistance, climbing) increase required thrust
and therefore current draw beyond simple throttle mapping.
"""

from powertrain.propeller_model import Propeller
from powertrain.motor_model import BLDCMotor


class CurrentConsumptionModel:
    """
    Given a required thrust (e.g., to hover or climb), back-calculates
    the RPM needed, then the current draw needed to sustain that RPM
    against the propeller's torque demand.
    """

    def __init__(self, motor: BLDCMotor = None, propeller: Propeller = None):
        self.motor = motor or BLDCMotor()
        self.propeller = propeller or Propeller()

    def current_for_required_thrust(self, required_thrust_n: float,
                                     air_density: float = 1.225) -> dict:
        """
        Solve for the RPM that produces the required thrust, then
        compute the current draw needed to sustain that RPM's torque demand.
        """
        if required_thrust_n < 0:
            raise ValueError("required_thrust_n cannot be negative")

        # Binary search RPM for target thrust (thrust grows with RPM^2)
        lo, hi = 0.0, 60000.0
        for _ in range(100):
            mid = (lo + hi) / 2.0
            out = self.propeller.compute(rpm=mid, air_density=air_density)
            if out["thrust_n"] < required_thrust_n:
                lo = mid
            else:
                hi = mid
        rpm = (lo + hi) / 2.0

        prop_out = self.propeller.compute(rpm=rpm, air_density=air_density)
        load_torque = prop_out["torque_nm"]

        current_needed = (load_torque / self.motor.kt) + self.motor.spec.no_load_current
        current_needed = min(current_needed, self.motor.spec.max_current)

        return {
            "required_thrust_n": round(required_thrust_n, 3),
            "rpm_needed": round(rpm, 1),
            "current_needed_a": round(current_needed, 3),
            "achievable": current_needed < self.motor.spec.max_current,
        }


if __name__ == "__main__":
    model = CurrentConsumptionModel()

    print("Test 1: 3N thrust required (light load)")
    print(model.current_for_required_thrust(required_thrust_n=3.0))

    print("\nTest 2: 12N thrust required (hover-class load)")
    print(model.current_for_required_thrust(required_thrust_n=12.0))

    print("\nTest 3: 20N thrust required (heavy load, likely unreachable)")
    print(model.current_for_required_thrust(required_thrust_n=20.0))
