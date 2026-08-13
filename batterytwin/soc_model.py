class SOCModel:
    """
    Battery State-of-Charge model using coulomb counting.

    SOC is represented as a normalized value:
        1.0 = 100%
        0.5 = 50%
        0.0 = 0%
    """

    def __init__(self, capacity_ah: float, initial_soc: float = 1.0):
        if capacity_ah <= 0:
            raise ValueError("Battery capacity must be greater than zero.")

        if not 0.0 <= initial_soc <= 1.0:
            raise ValueError("Initial SOC must be between 0.0 and 1.0.")

        self.capacity_ah = capacity_ah
        self.soc = initial_soc

    def update(self, current_a: float, dt_s: float) -> float:
        """
        Update SOC using coulomb counting.

        Positive current = battery discharge.
        Negative current = battery charging.

        Equation:

            SOC_new = SOC_old - (I * dt) / (3600 * Q)
        """

        if dt_s < 0:
            raise ValueError("Time step cannot be negative.")

        delta_soc = (current_a * dt_s) / (3600.0 * self.capacity_ah)

        self.soc -= delta_soc

        # Keep SOC physically bounded.
        self.soc = max(0.0, min(1.0, self.soc))

        return self.soc

    def get_soc(self) -> float:
        return self.soc
