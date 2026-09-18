"""
Powertrain Runtime Configuration API (BTS-B - Day 17)

Allows external modules (Battery Engine, ROS2 nodes, test harnesses)
to reconfigure motor/ESC/propeller parameters at runtime without
modifying source code -- useful for swapping hardware profiles or
running parameter sweeps.
"""

from powertrain.powertrain_config import MotorSpec, ESCSpec, PropellerSpec
from powertrain.powertrain_engine import PowertrainEngine


class PowertrainAPI:
    """
    Thin configuration layer wrapping PowertrainEngine, exposing safe
    setters for hardware parameters with validation.
    """

    def __init__(self):
        self.engine = PowertrainEngine()

    def set_motor_spec(self, kv_rating: float = None, resistance: float = None,
                        no_load_current: float = None, max_current: float = None):
        spec = self.engine.motor.spec
        if kv_rating is not None:
            if kv_rating <= 0:
                raise ValueError("kv_rating must be positive")
            spec.kv_rating = kv_rating
        if resistance is not None:
            if resistance <= 0:
                raise ValueError("resistance must be positive")
            spec.resistance = resistance
        if no_load_current is not None:
            spec.no_load_current = max(no_load_current, 0.0)
        if max_current is not None:
            if max_current <= spec.no_load_current:
                raise ValueError("max_current must exceed no_load_current")
            spec.max_current = max_current

        # kt depends on kv_rating -- recompute
        import math
        self.engine.motor.kt = 60.0 / (2 * math.pi * spec.kv_rating)
        return self.get_config()

    def set_propeller_spec(self, diameter_inch: float = None):
        spec = self.engine.propeller.spec
        if diameter_inch is not None:
            if diameter_inch <= 0:
                raise ValueError("diameter_inch must be positive")
            spec.diameter_inch = diameter_inch
            self.engine.propeller.diameter_m = diameter_inch * 0.0254
        return self.get_config()

    def get_config(self) -> dict:
        return {
            "motor": {
                "kv_rating": self.engine.motor.spec.kv_rating,
                "resistance": self.engine.motor.spec.resistance,
                "no_load_current": self.engine.motor.spec.no_load_current,
                "max_current": self.engine.motor.spec.max_current,
            },
            "propeller": {
                "diameter_inch": self.engine.propeller.spec.diameter_inch,
            },
        }


if __name__ == "__main__":
    api = PowertrainAPI()

    print("Default config:")
    print(" ", api.get_config())

    print("\nStep @ default config, 50% throttle:")
    print(" ", api.engine.step(battery_voltage=22.2, throttle_percent=50.0))

    print("\nTesting an alternative 900KV motor configuration...")
    api.set_motor_spec(kv_rating=900.0, max_current=30.0)
    print("Updated config:", api.get_config())

    print("\nStep @ new config, 50% throttle:")
    print(" ", api.engine.step(battery_voltage=22.2, throttle_percent=50.0))
