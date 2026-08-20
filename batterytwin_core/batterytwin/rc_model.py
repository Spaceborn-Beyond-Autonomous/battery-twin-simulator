class RCModel:
    """
    First-order Thevenin RC polarization model.

    dV1/dt = -V1/(R1*C1) + I/C1
    """

    def __init__(
        self,
        resistance_ohm: float,
        capacitance_f: float,
        initial_voltage_v: float = 0.0,
    ):
        if resistance_ohm <= 0:
            raise ValueError("RC resistance must be greater than zero.")

        if capacitance_f <= 0:
            raise ValueError("RC capacitance must be greater than zero.")

        self.resistance_ohm = resistance_ohm
        self.capacitance_f = capacitance_f
        self.polarization_voltage_v = initial_voltage_v

    def update(self, current_a: float, dt_s: float) -> float:

        if dt_s < 0:
            raise ValueError("Time step cannot be negative.")

        derivative = (
            -self.polarization_voltage_v
            / (self.resistance_ohm * self.capacitance_f)
            + current_a / self.capacitance_f
        )

        self.polarization_voltage_v += derivative * dt_s

        return self.polarization_voltage_v

    def get_polarization_voltage(self) -> float:
        return self.polarization_voltage_v
