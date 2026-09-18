"""
Hover Power Prediction & Remaining Flight Time (BTS-B - Days 10-11)

Estimates:
1. Hover thrust requirement (must equal aircraft weight)
2. Current/power draw needed to sustain hover
3. Remaining flight time given battery capacity and hover current draw

Assumes a quadcopter (4 motors) for total thrust/current scaling.
"""

from powertrain.current_consumption import CurrentConsumptionModel


class FlightEnduranceModel:

    GRAVITY = 9.81  # m/s^2

    def __init__(self, num_motors: int = 4):
        self.num_motors = num_motors
        self.current_model = CurrentConsumptionModel()

    def hover_requirements(self, aircraft_mass_kg: float,
                            air_density: float = 1.225) -> dict:
        """
        Computes per-motor and total current/power draw required to hover.
        """
        total_thrust_needed_n = aircraft_mass_kg * self.GRAVITY
        thrust_per_motor_n = total_thrust_needed_n / self.num_motors

        per_motor = self.current_model.current_for_required_thrust(
            required_thrust_n=thrust_per_motor_n,
            air_density=air_density,
        )

        total_current_a = per_motor["current_needed_a"] * self.num_motors

        return {
            "aircraft_mass_kg": aircraft_mass_kg,
            "total_thrust_needed_n": round(total_thrust_needed_n, 3),
            "thrust_per_motor_n": round(thrust_per_motor_n, 3),
            "rpm_per_motor": per_motor["rpm_needed"],
            "current_per_motor_a": per_motor["current_needed_a"],
            "total_hover_current_a": round(total_current_a, 3),
            "hover_achievable": per_motor["achievable"],
        }

    def remaining_flight_time(self, aircraft_mass_kg: float,
                               battery_capacity_ah: float,
                               battery_voltage: float,
                               usable_capacity_fraction: float = 0.8,
                               air_density: float = 1.225) -> dict:
        """
        Estimates hover-only flight time.
        usable_capacity_fraction accounts for not fully discharging
        the LiPo (typically stop at ~20% remaining for battery health).
        """
        hover = self.hover_requirements(aircraft_mass_kg, air_density)
        total_current_a = hover["total_hover_current_a"]

        usable_ah = battery_capacity_ah * usable_capacity_fraction
        flight_time_hours = usable_ah / total_current_a if total_current_a > 0 else 0.0
        flight_time_minutes = flight_time_hours * 60.0

        hover_power_w = total_current_a * battery_voltage

        return {
            **hover,
            "usable_capacity_ah": round(usable_ah, 3),
            "hover_power_w": round(hover_power_w, 2),
            "estimated_flight_time_min": round(flight_time_minutes, 2),
        }


if __name__ == "__main__":
    model = FlightEnduranceModel(num_motors=4)

    print("Scenario: 1.2 kg quadcopter, Spektrum 6S 5000mAh battery")
    result = model.remaining_flight_time(
        aircraft_mass_kg=1.2,
        battery_capacity_ah=5.0,
        battery_voltage=22.2,
    )
    for k, v in result.items():
        print(f"  {k}: {v}")
