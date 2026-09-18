"""
Propeller Aerodynamic Model (BTS-B - Day 4)

Converts motor RPM into thrust and torque using standard
propeller aerodynamics (momentum/blade element theory simplified
via empirical thrust/torque coefficients).

Reference propeller: 10x4.5 inch (typical for small multirotor UAVs)

Equations:
    n = RPM / 60                      (rotations per second)
    Thrust (N) = Ct * rho * n^2 * D^4
    Torque (N.m) = Cq * rho * n^2 * D^5

Where Ct, Cq are empirical thrust/torque coefficients derived
from manufacturer propeller performance data (e.g. APC prop charts).
"""

from powertrain.powertrain_config import PropellerSpec


class Propeller:
    """
    Simulates propeller aerodynamic behavior: converts RPM into
    thrust (N) and torque (N.m), accounting for air density.
    """

    # Empirical coefficients for a typical 10x4.5" multirotor propeller
    THRUST_COEFFICIENT = 0.10   # Ct
    TORQUE_COEFFICIENT = 0.0055  # Cq

    def __init__(self, spec: PropellerSpec = None):
        self.spec = spec or PropellerSpec()
        self.diameter_m = self.spec.diameter_inch * 0.0254

    def compute(self, rpm: float, air_density: float = 1.225) -> dict:
        """
        Args:
            rpm: motor RPM (from motor_model)
            air_density: kg/m^3 (1.225 = sea level standard)

        Returns:
            dict with thrust_n, torque_nm, thrust_kgf
        """
        if rpm < 0:
            raise ValueError("rpm cannot be negative")
        if air_density <= 0:
            raise ValueError("air_density must be positive")

        n = rpm / 60.0  # revolutions per second

        thrust_n = (
            self.THRUST_COEFFICIENT * air_density * (n ** 2) * (self.diameter_m ** 4)
        )
        torque_nm = (
            self.TORQUE_COEFFICIENT * air_density * (n ** 2) * (self.diameter_m ** 5)
        )

        return {
            "thrust_n": round(thrust_n, 4),
            "thrust_kgf": round(thrust_n / 9.81, 4),
            "torque_nm": round(torque_nm, 5),
            "rps": round(n, 2),
        }


if __name__ == "__main__":
    prop = Propeller()

    print("Test 1: 7215 RPM (25% throttle)")
    print(prop.compute(rpm=7215))

    print("\nTest 2: 21645 RPM (75% throttle)")
    print(prop.compute(rpm=21645))

    print("\nTest 3: 28860 RPM (100% throttle)")
    print(prop.compute(rpm=28860))
