class EnergyModel:
    """
    Battery energy accounting model.

    Energy is represented in Wh.
    """

    def __init__(self, initial_energy_wh: float):
        if initial_energy_wh <= 0:
            raise ValueError(
                "Initial energy must be greater than zero."
            )

        self.initial_energy_wh = initial_energy_wh
        self.energy_consumed_wh = 0.0

    def update(self, power_w: float, dt_s: float) -> float:
        if dt_s < 0:
            raise ValueError(
                "Time step cannot be negative."
            )

        energy_delta_wh = (
            power_w * dt_s / 3600.0
        )

        self.energy_consumed_wh += energy_delta_wh

        self.energy_consumed_wh = max(
            0.0,
            min(
                self.initial_energy_wh,
                self.energy_consumed_wh
            )
        )

        return self.get_remaining_energy()

    def get_remaining_energy(self) -> float:
        return (
            self.initial_energy_wh
            - self.energy_consumed_wh
        )

    def get_consumed_energy(self) -> float:
        return self.energy_consumed_wh
