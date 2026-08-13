class VoltageModel:
    """
    Terminal-voltage model.

    V_terminal = V_OCV - I * R_internal
    """

    def calculate(
        self,
        ocv_v: float,
        current_a: float,
        resistance_ohm: float
    ) -> float:

        voltage_drop = current_a * resistance_ohm

        return ocv_v - voltage_drop
