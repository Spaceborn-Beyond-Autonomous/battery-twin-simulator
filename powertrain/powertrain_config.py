"""
Powertrain Configuration & Framework (BTS-B - Day 1)
Defines the core data structures connecting Battery -> ESC -> Motor -> Propeller.
"""

from dataclasses import dataclass


@dataclass
class MotorSpec:
    """EMAX ECO II 2807-1300KV motor specifications."""
    kv_rating: float = 1300.0        # RPM per volt (no load)
    resistance: float = 0.09         # motor internal resistance (Ohms)
    no_load_current: float = 0.5     # Amps at no load
    max_current: float = 25.0        # Amps continuous rating
    poles: int = 14                  # motor pole count


@dataclass
class ESCSpec:
    """Electronic Speed Controller specifications."""
    max_current: float = 30.0        # Amps continuous
    switching_efficiency: float = 0.97
    pwm_frequency: float = 400.0     # Hz


@dataclass
class PropellerSpec:
    """Propeller aerodynamic specifications."""
    diameter_inch: float = 10.0
    pitch_inch: float = 4.5
    blades: int = 2


@dataclass
class PowertrainInputs:
    """Inputs coming from the Battery Engine (BTS-A) and flight controller."""
    battery_voltage: float           # Volts, supplied by BatteryTwin (Anand)
    throttle_percent: float          # 0-100 %


@dataclass
class PowertrainState:
    """Outputs produced by the Powertrain subsystem at each timestep."""
    rpm: float = 0.0
    thrust: float = 0.0              # Newtons
    torque: float = 0.0              # N·m
    current_draw: float = 0.0        # Amps
    electrical_power: float = 0.0    # Watts
    mechanical_power: float = 0.0    # Watts
    efficiency: float = 0.0          # 0-1


class PowertrainFramework:
    """
    Connects Battery -> ESC -> Motor -> Propeller.
    This is the Day 1 skeleton: initializes subsystem specs and
    verifies it can receive battery parameters correctly.
    """

    def __init__(self, motor: MotorSpec = None, esc: ESCSpec = None,
                 propeller: PropellerSpec = None):
        self.motor = motor or MotorSpec()
        self.esc = esc or ESCSpec()
        self.propeller = propeller or PropellerSpec()
        self.state = PowertrainState()

    def receive_battery_input(self, inputs: PowertrainInputs) -> bool:
        """
        Day 1 check: Does the Powertrain subsystem successfully receive
        battery parameters and initialize correctly?
        """
        if inputs.battery_voltage <= 0:
            raise ValueError("Battery voltage must be positive")
        if not (0 <= inputs.throttle_percent <= 100):
            raise ValueError("Throttle must be between 0 and 100")

        self._last_inputs = inputs
        return True

    def summary(self):
        return {
            "motor_kv": self.motor.kv_rating,
            "esc_max_current": self.esc.max_current,
            "propeller_diameter_in": self.propeller.diameter_inch,
        }


if __name__ == "__main__":
    pt = PowertrainFramework()
    inputs = PowertrainInputs(battery_voltage=22.2, throttle_percent=25.0)
    ok = pt.receive_battery_input(inputs)
    print("Powertrain initialized:", ok)
    print(pt.summary())
