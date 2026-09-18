"""
Unified Powertrain Engine (BTS-B - Day 16)

Single integration point combining every powertrain submodule built
across Days 1-15 into one coherent engine with a clean public API.
This is the module other subsystems (Battery Engine, ROS2, Dashboard)
will call in Week 4 integration.
"""

from powertrain.motor_model import BLDCMotor
from powertrain.esc_model import ESC
from powertrain.propeller_model import Propeller
from powertrain.power_model import PowerConsumptionModel
from powertrain.motor_efficiency import MotorEfficiencyModel
from powertrain.current_consumption import CurrentConsumptionModel
from powertrain.pwm_response import PWMResponseModel
from powertrain.flight_endurance import FlightEnduranceModel
from powertrain.dynamic_thrust import DynamicThrustModel
from powertrain.torque_analysis import TorqueAnalysis
from powertrain.environmental_effects import EnvironmentalEffectsModel


class PowertrainEngine:
    """
    Unified engine exposing all powertrain capabilities built in
    Weeks 1-3 through a single, stable interface.
    """

    def __init__(self, num_motors: int = 4):
        self.motor = BLDCMotor()
        self.esc = ESC()
        self.propeller = Propeller()

        self.power_model = PowerConsumptionModel(
            motor=self.motor, esc=self.esc, propeller=self.propeller
        )
        self.efficiency_model = MotorEfficiencyModel(spec=self.motor.spec)
        self.current_model = CurrentConsumptionModel(
            motor=self.motor, propeller=self.propeller
        )
        self.pwm_response = PWMResponseModel(
            motor=self.motor, propeller=self.propeller
        )
        self.endurance_model = FlightEnduranceModel(num_motors=num_motors)
        self.dynamic_thrust = DynamicThrustModel()
        self.torque_analysis = TorqueAnalysis()
        self.environmental = EnvironmentalEffectsModel()

    # --- Core steady-state step (used by ROS2 telemetry loop, Week 4) ---
    def step(self, battery_voltage: float, throttle_percent: float,
             air_density: float = 1.225) -> dict:
        state = self.power_model.compute(
            battery_voltage=battery_voltage,
            throttle_percent=throttle_percent,
            air_density=air_density,
        )
        losses = self.efficiency_model.compute(
            current=state.current_draw, rpm=state.rpm
        )
        return {
            "rpm": state.rpm,
            "thrust_n": state.thrust,
            "torque_nm": state.torque,
            "current_a": state.current_draw,
            "electrical_power_w": state.electrical_power,
            "mechanical_power_w": state.mechanical_power,
            "efficiency": state.efficiency,
            "losses": losses,
        }

    # --- Flight planning utilities ---
    def hover_flight_time(self, aircraft_mass_kg: float,
                           battery_capacity_ah: float,
                           battery_voltage: float) -> dict:
        return self.endurance_model.remaining_flight_time(
            aircraft_mass_kg=aircraft_mass_kg,
            battery_capacity_ah=battery_capacity_ah,
            battery_voltage=battery_voltage,
        )

    def torque_margin(self, battery_voltage: float, throttle_percent: float) -> dict:
        return self.torque_analysis.analyze(
            battery_voltage=battery_voltage, throttle_percent=throttle_percent
        )

    def performance_at_altitude(self, battery_voltage: float,
                                 throttle_percent: float, altitude_m: float) -> dict:
        return self.environmental.performance_at_altitude(
            battery_voltage=battery_voltage,
            throttle_percent=throttle_percent,
            altitude_m=altitude_m,
        )

    def performance_at_soc(self, soc_percent: float, throttle_percent: float) -> dict:
        return self.dynamic_thrust.thrust_at_soc(
            soc_percent=soc_percent, throttle_percent=throttle_percent
        )


if __name__ == "__main__":
    engine = PowertrainEngine(num_motors=4)

    print("=== Unified Powertrain Engine Validation (Day 16) ===\n")

    print("1. Steady-state step @ 50% throttle:")
    print(" ", engine.step(battery_voltage=22.2, throttle_percent=50.0))

    print("\n2. Hover flight time (1.2kg quad, 6S 5000mAh):")
    print(" ", engine.hover_flight_time(
        aircraft_mass_kg=1.2, battery_capacity_ah=5.0, battery_voltage=22.2
    ))

    print("\n3. Torque margin @ 40% throttle:")
    print(" ", engine.torque_margin(battery_voltage=22.2, throttle_percent=40.0))

    print("\n4. Performance @ 2000m altitude, 100% throttle:")
    print(" ", engine.performance_at_altitude(
        battery_voltage=22.2, throttle_percent=100.0, altitude_m=2000
    ))

    print("\n5. Performance @ 20% SOC, 100% throttle:")
    print(" ", engine.performance_at_soc(soc_percent=20, throttle_percent=100.0))
