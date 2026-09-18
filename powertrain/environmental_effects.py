"""
Environmental Effects Model (BTS-B - Day 15)

Models how air density (function of altitude and temperature) affects
propeller thrust output. Uses the International Standard Atmosphere
(ISA) approximation for density vs altitude.
"""

import math
from powertrain.power_model import PowerConsumptionModel


class EnvironmentalEffectsModel:

    def __init__(self):
        self.power_model = PowerConsumptionModel()

    def air_density_at_altitude(self, altitude_m: float,
                                 temperature_c: float = 15.0) -> float:
        """
        Simplified ISA density model:
        rho = P / (R_specific * T)
        Using barometric formula for pressure vs altitude.
        """
        p0 = 101325.0       # Pa, sea level standard pressure
        t0_k = temperature_c + 273.15
        lapse_rate = 0.0065  # K/m
        g = 9.80665
        r_specific = 287.05  # J/(kg.K) for dry air
        m = 0.0289644        # kg/mol

        t_k = t0_k - lapse_rate * altitude_m
        pressure = p0 * (t_k / t0_k) ** (g * m / (8.3144598 * lapse_rate))
        density = pressure / (r_specific * t_k)
        return density

    def performance_at_altitude(self, battery_voltage: float,
                                 throttle_percent: float,
                                 altitude_m: float,
                                 temperature_c: float = 15.0) -> dict:
        rho = self.air_density_at_altitude(altitude_m, temperature_c)
        state = self.power_model.compute(
            battery_voltage=battery_voltage,
            throttle_percent=throttle_percent,
            air_density=rho,
        )
        return {
            "altitude_m": altitude_m,
            "air_density_kg_m3": round(rho, 4),
            "rpm": state.rpm,
            "thrust_n": state.thrust,
            "current_a": state.current_draw,
        }


if __name__ == "__main__":
    model = EnvironmentalEffectsModel()

    print("Thrust performance vs altitude (100% throttle, 22.2V):")
    for alt in [0, 500, 1000, 2000, 3000, 4000]:
        r = model.performance_at_altitude(
            battery_voltage=22.2, throttle_percent=100.0, altitude_m=alt
        )
        print(f"  Alt={alt:5d}m  rho={r['air_density_kg_m3']:.4f}  "
              f"RPM={r['rpm']:8.1f}  Thrust={r['thrust_n']:6.2f}N  "
              f"I={r['current_a']:.2f}A")
