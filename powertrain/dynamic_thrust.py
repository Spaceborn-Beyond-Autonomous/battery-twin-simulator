"""
Dynamic Thrust Model (BTS-B - Day 13)

Models how propulsion performance (RPM, thrust) degrades as the
battery depletes, since terminal voltage drops with State of Charge
(SOC) and with internal resistance under load.

Uses a simplified voltage-vs-SOC curve typical of LiPo chemistry
(flat mid-discharge region, steep drop near empty) until BTS-A's
real battery model is available for integration (Week 4).
"""

from powertrain.power_model import PowerConsumptionModel


class DynamicThrustModel:
    """
    Simplified LiPo voltage-vs-SOC curve (6S nominal 22.2V, max 25.2V,
    cutoff ~19.8V / 3.3V per cell). Used to show how thrust changes
    across a flight as the battery depletes, pending real integration
    with the Battery Physics Engine (BTS-A) in Week 4.
    """

    def __init__(self):
        self.power_model = PowerConsumptionModel()

    def voltage_from_soc(self, soc_percent: float) -> float:
        """
        Simplified LiPo discharge curve (6S pack).
        soc_percent: 0-100 (100 = fully charged)
        """
        soc = max(0.0, min(100.0, soc_percent)) / 100.0

        v_max = 25.2   # fully charged (4.2V/cell)
        v_nom = 22.2   # nominal (3.7V/cell)
        v_cutoff = 19.8  # discharge cutoff (3.3V/cell)

        if soc > 0.9:
            # steep initial drop from max to nominal
            frac = (soc - 0.9) / 0.1
            return v_nom + frac * (v_max - v_nom)
        elif soc > 0.15:
            # flat middle region
            frac = (soc - 0.15) / 0.75
            return v_cutoff + frac * (v_nom - v_cutoff) * 1.05
        else:
            # steep final drop near empty
            frac = soc / 0.15
            return v_cutoff * frac

    def thrust_at_soc(self, soc_percent: float, throttle_percent: float,
                       air_density: float = 1.225) -> dict:
        voltage = self.voltage_from_soc(soc_percent)
        state = self.power_model.compute(
            battery_voltage=voltage,
            throttle_percent=throttle_percent,
            air_density=air_density,
        )
        return {
            "soc_percent": soc_percent,
            "battery_voltage": round(voltage, 3),
            "rpm": state.rpm,
            "thrust_n": state.thrust,
            "current_a": state.current_draw,
        }


if __name__ == "__main__":
    model = DynamicThrustModel()

    print("Thrust degradation across battery discharge (100% throttle):")
    for soc in [100, 80, 60, 40, 20, 10]:
        result = model.thrust_at_soc(soc_percent=soc, throttle_percent=100.0)
        print(f"  SOC={soc:3d}%  V={result['battery_voltage']:.2f}V  "
              f"RPM={result['rpm']:8.1f}  Thrust={result['thrust_n']:6.2f}N  "
              f"I={result['current_a']:.2f}A")
