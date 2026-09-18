"""
Powertrain MVP (BTS-B - Day 6)
Unified entry point combining Motor, ESC, Propeller, and Power models
into a single callable interface for the rest of the system.
"""

from powertrain.power_model import PowerConsumptionModel


class PowertrainMVP:
    """
    Single interface: given battery voltage + throttle, returns the
    complete powertrain state (RPM, thrust, torque, current, power,
    efficiency).
    """

    def __init__(self):
        self.power_model = PowerConsumptionModel()

    def step(self, battery_voltage: float, throttle_percent: float,
             air_density: float = 1.225):
        return self.power_model.compute(
            battery_voltage=battery_voltage,
            throttle_percent=throttle_percent,
            air_density=air_density,
        )


if __name__ == "__main__":
    pt = PowertrainMVP()
    print("=== Powertrain MVP Validation (Day 6) ===")
    for throttle in [0, 25, 50, 75, 100]:
        state = pt.step(battery_voltage=22.2, throttle_percent=throttle)
        print(f"Throttle {throttle:3d}% -> RPM={state.rpm:8.1f} "
              f"Thrust={state.thrust:7.2f}N Current={state.current_draw:5.2f}A "
              f"Eff={state.efficiency*100:5.2f}%")
