"""
Torque Estimation & Margin Analysis (BTS-B - Day 14)

Analyzes motor available torque vs propeller demanded torque across
the full RPM range, identifying the operating point and torque margin
(headroom for acceleration/maneuvering) at each throttle setting.
"""

from powertrain.power_model import PowerConsumptionModel
from powertrain.propeller_model import Propeller


class TorqueAnalysis:

    def __init__(self):
        self.power_model = PowerConsumptionModel()
        self.propeller = Propeller()

    def analyze(self, battery_voltage: float, throttle_percent: float,
                air_density: float = 1.225) -> dict:
        state = self.power_model.compute(
            battery_voltage=battery_voltage,
            throttle_percent=throttle_percent,
            air_density=air_density,
        )

        motor = self.power_model.motor
        applied_voltage = battery_voltage * (throttle_percent / 100.0)
        motor_torque_available, _ = self.power_model._available_motor_torque(
            applied_voltage, 0.0  # torque ceiling at zero RPM (max headroom)
        )

        torque_margin = motor_torque_available - state.torque
        margin_percent = (
            (torque_margin / motor_torque_available * 100)
            if motor_torque_available > 0 else 0.0
        )

        return {
            "throttle_percent": throttle_percent,
            "operating_rpm": state.rpm,
            "operating_torque_nm": state.torque,
            "max_available_torque_nm": round(motor_torque_available, 4),
            "torque_margin_nm": round(torque_margin, 4),
            "torque_margin_percent": round(margin_percent, 2),
            "current_limited": state.current_draw >= motor.spec.max_current,
        }


if __name__ == "__main__":
    analysis = TorqueAnalysis()

    print("Torque margin analysis across throttle range:")
    for throttle in [10, 25, 40, 50, 65, 80, 100]:
        r = analysis.analyze(battery_voltage=22.2, throttle_percent=throttle)
        flag = " <-- CURRENT LIMITED" if r["current_limited"] else ""
        print(f"  Throttle={throttle:3d}%  RPM={r['operating_rpm']:8.1f}  "
              f"Margin={r['torque_margin_percent']:6.2f}%{flag}")
