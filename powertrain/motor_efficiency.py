"""
Motor Efficiency Model (BTS-B - Day 7)
Breaks down motor power losses into copper, iron, and mechanical
components, giving a realistic efficiency curve vs simple I*V accounting.
"""

from powertrain.powertrain_config import MotorSpec


class MotorEfficiencyModel:
    """
    Copper losses:      P_cu = I^2 * R                (resistive heating)
    Iron losses:        P_fe = k_fe * RPM^1.5          (empirical, hysteresis+eddy)
    Mechanical losses:  P_mech = k_mech * RPM          (bearing/windage friction)
    """

    # Empirical loss coefficients for a small BLDC motor (EMAX ECO II class)
    IRON_LOSS_COEFF = 0.00002      # W per (RPM^1.5)
    MECH_LOSS_COEFF = 0.0003       # W per RPM

    def __init__(self, spec: MotorSpec = None):
        self.spec = spec or MotorSpec()

    def compute(self, current: float, rpm: float) -> dict:
        copper_loss = (current ** 2) * self.spec.resistance
        iron_loss = self.IRON_LOSS_COEFF * (rpm ** 1.5)
        mech_loss = self.MECH_LOSS_COEFF * rpm

        total_loss = copper_loss + iron_loss + mech_loss

        return {
            "copper_loss_w": round(copper_loss, 3),
            "iron_loss_w": round(iron_loss, 3),
            "mechanical_loss_w": round(mech_loss, 3),
            "total_loss_w": round(total_loss, 3),
        }


if __name__ == "__main__":
    model = MotorEfficiencyModel()

    print("Test 1: 10.25A, 6015.9 RPM (throttle 25%)")
    print(model.compute(current=10.25, rpm=6015.9))

    print("\nTest 2: 25A, 9537 RPM (throttle 50%+, current-limited)")
    print(model.compute(current=25.0, rpm=9537.0))
