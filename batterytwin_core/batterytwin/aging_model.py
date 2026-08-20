class AgingModel:
    """
    Battery degradation model.

    Models:
        1. Capacity fade
        2. Internal resistance growth

    SOH:
        1.0 = new battery
        0.0 = fully degraded
    """

    def __init__(
        self,
        initial_soh: float = 1.0,
        capacity_fade_per_cycle: float = 0.0005,
        resistance_growth_factor: float = 1.5,
    ):
        if not 0.0 < initial_soh <= 1.0:
            raise ValueError(
                "Initial SOH must be greater than 0 and <= 1."
            )

        if capacity_fade_per_cycle < 0:
            raise ValueError(
                "Capacity fade cannot be negative."
            )

        if resistance_growth_factor < 0:
            raise ValueError(
                "Resistance growth factor cannot be negative."
            )

        self.soh = initial_soh

        self.capacity_fade_per_cycle = (
            capacity_fade_per_cycle
        )

        self.resistance_growth_factor = (
            resistance_growth_factor
        )

        self.cycle_count = 0.0

    def update(self, equivalent_full_cycles: float) -> float:
        """
        Update SOH based on equivalent full cycles.

        One equivalent full cycle represents battery throughput
        equal to 100% of nominal capacity.

        SOH_new =
            SOH_old - fade_per_cycle * cycle_increment
        """

        if equivalent_full_cycles < 0:
            raise ValueError(
                "Cycle increment cannot be negative."
            )

        self.cycle_count += equivalent_full_cycles

        self.soh -= (
            self.capacity_fade_per_cycle
            * equivalent_full_cycles
        )

        self.soh = max(0.0, min(1.0, self.soh))

        return self.soh

    def get_soh(self) -> float:
        return self.soh

    def get_capacity_factor(self) -> float:
        """
        Fraction of original capacity still available.
        """

        return self.soh

    def get_resistance_factor(self) -> float:
        """
        Resistance multiplier caused by aging.

        At SOH = 1:
            factor = 1.0

        As SOH decreases:
            resistance increases.
        """

        return (
            1.0
            + self.resistance_growth_factor
            * (1.0 - self.soh)
        )
