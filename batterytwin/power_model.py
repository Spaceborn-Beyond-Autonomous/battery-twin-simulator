class PowerModel:
    """
    Electrical power model.

    Positive current:
        Battery discharge

    Negative current:
        Battery charging

    Positive power:
        Battery delivering power

    Negative power:
        Battery absorbing power
    """

    def calculate(
        self,
        voltage_v: float,
        current_a: float,
    ) -> float:

        return voltage_v * current_a
