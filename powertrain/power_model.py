"""
Power Consumption Model (BTS-B - Day 5, final)

Solves the coupled Motor <-> Propeller torque balance via binary
search on RPM, correctly bounded by the throttle-applied voltage.
When motor current saturates at max_current, available torque
becomes independent of voltage -- causing a realistic RPM plateau
if the propeller's torque demand curve intersects the motor's
current-limited torque ceiling. This is expected, correct behavior
for a current-limited motor/propeller combination.
"""

from powertrain.motor_model import BLDCMotor
from powertrain.esc_model import ESC
from powertrain.propeller_model import Propeller
from powertrain.powertrain_config import PowertrainState


class PowerConsumptionModel:

    def __init__(self, motor: BLDCMotor = None, esc: ESC = None,
                 propeller: Propeller = None):
        self.motor = motor or BLDCMotor()
        self.esc = esc or ESC()
        self.propeller = propeller or Propeller()

    def _available_motor_torque(self, applied_voltage, rpm):
        spec = self.motor.spec
        back_emf = rpm / spec.kv_rating
        current = (applied_voltage - back_emf) / spec.resistance
        current = max(current, spec.no_load_current)
        current = min(current, spec.max_current)
        torque = self.motor.kt * (current - spec.no_load_current)
        return max(torque, 0.0), current

    def compute(self, battery_voltage: float, throttle_percent: float,
                air_density: float = 1.225) -> PowertrainState:
        applied_voltage = battery_voltage * (throttle_percent / 100.0)
        spec = self.motor.spec

        lo, hi = 0.0, spec.kv_rating * applied_voltage
        current = spec.no_load_current

        for _ in range(100):
            mid_rpm = (lo + hi) / 2.0
            motor_torque, current = self._available_motor_torque(applied_voltage, mid_rpm)
            prop_out = self.propeller.compute(rpm=mid_rpm, air_density=air_density)
            if motor_torque > prop_out["torque_nm"]:
                lo = mid_rpm
            else:
                hi = mid_rpm

        final_rpm = (lo + hi) / 2.0
        _, current = self._available_motor_torque(applied_voltage, final_rpm)
        prop_out = self.propeller.compute(rpm=final_rpm, air_density=air_density)

        esc_out = self.esc.process(
            battery_voltage=battery_voltage,
            throttle_percent=throttle_percent,
            motor_current=current,
        )
        current_draw = esc_out["limited_current_a"]
        electrical_power = battery_voltage * current_draw

        angular_velocity_rad_s = final_rpm * (2 * 3.14159265) / 60.0
        mechanical_power = prop_out["torque_nm"] * angular_velocity_rad_s

        efficiency = (
            mechanical_power / electrical_power if electrical_power > 0 else 0.0
        )
        efficiency = min(max(efficiency, 0.0), 1.0)

        return PowertrainState(
            rpm=round(final_rpm, 2),
            thrust=prop_out["thrust_n"],
            torque=prop_out["torque_nm"],
            current_draw=round(current_draw, 3),
            electrical_power=round(electrical_power, 3),
            mechanical_power=round(mechanical_power, 3),
            efficiency=round(efficiency, 4),
        )


if __name__ == "__main__":
    model = PowerConsumptionModel()

    for throttle in [25, 50, 75, 100]:
        state = model.compute(battery_voltage=22.2, throttle_percent=throttle)
        print(f"\nThrottle {throttle}%:")
        print(f"  RPM: {state.rpm}")
        print(f"  Thrust: {state.thrust} N ({state.thrust/9.81:.3f} kgf)")
        print(f"  Torque: {state.torque} N.m")
        print(f"  Current draw: {state.current_draw} A")
        print(f"  Electrical power: {state.electrical_power} W")
        print(f"  Mechanical power: {state.mechanical_power} W")
        print(f"  Efficiency: {state.efficiency * 100:.2f}%")
