import math


class ThermalModel:
    """
    Lumped-parameter battery thermal model.

    Heat generation:
        Q_gen = I² * R

    Heat rejection:
        Q_loss = h * (T - T_ambient)

    Thermal balance:
        dT/dt = (Q_gen - Q_loss) / C_th

    Sign convention:
        Current sign does not affect Joule heating because
        heating depends on I².

    Units:
        Temperature              : °C
        Current                  : A
        Resistance               : Ω
        Thermal capacity         : J/K
        Heat-transfer coefficient: W/K
        Power                    : W
        Time                     : s
    """

    def __init__(
        self,
        thermal_capacity_j_per_k: float,
        heat_transfer_w_per_k: float,
        initial_temperature_c: float = 25.0,
        ambient_temperature_c: float = 25.0,
    ):
        self._validate_finite(
            thermal_capacity_j_per_k,
            "Thermal capacity",
        )

        self._validate_finite(
            heat_transfer_w_per_k,
            "Heat transfer coefficient",
        )

        self._validate_finite(
            initial_temperature_c,
            "Initial temperature",
        )

        self._validate_finite(
            ambient_temperature_c,
            "Ambient temperature",
        )

        if thermal_capacity_j_per_k <= 0.0:
            raise ValueError(
                "Thermal capacity must be greater than zero."
            )

        if heat_transfer_w_per_k < 0.0:
            raise ValueError(
                "Heat transfer coefficient cannot be negative."
            )

        self.thermal_capacity_j_per_k = (
            thermal_capacity_j_per_k
        )

        self.heat_transfer_w_per_k = (
            heat_transfer_w_per_k
        )

        self.temperature_c = initial_temperature_c
        self.ambient_temperature_c = ambient_temperature_c

        # Diagnostic thermal quantities.
        self.heat_generation_w = 0.0
        self.heat_loss_w = 0.0
        self.net_heat_w = 0.0
        self.temperature_rate_c_per_s = 0.0

    @staticmethod
    def _validate_finite(value: float, name: str) -> None:
        if not math.isfinite(value):
            raise ValueError(
                f"{name} must be finite."
            )

    def update(
        self,
        current_a: float,
        resistance_ohm: float,
        dt_s: float,
    ) -> float:
        """
        Advance the thermal state by dt_s.

        Returns:
            Updated battery temperature in °C.
        """

        self._validate_finite(
            current_a,
            "Current",
        )

        self._validate_finite(
            resistance_ohm,
            "Resistance",
        )

        self._validate_finite(
            dt_s,
            "Time step",
        )

        if dt_s < 0.0:
            raise ValueError(
                "Time step cannot be negative."
            )

        if resistance_ohm < 0.0:
            raise ValueError(
                "Resistance cannot be negative."
            )

        # --------------------------------------------------
        # 1. Joule heating
        # --------------------------------------------------

        self.heat_generation_w = (
            current_a * current_a * resistance_ohm
        )

        # --------------------------------------------------
        # 2. Convective / effective heat rejection
        # --------------------------------------------------

        self.heat_loss_w = (
            self.heat_transfer_w_per_k
            * (
                self.temperature_c
                - self.ambient_temperature_c
            )
        )

        # --------------------------------------------------
        # 3. Net thermal power
        # --------------------------------------------------

        self.net_heat_w = (
            self.heat_generation_w
            - self.heat_loss_w
        )

        # --------------------------------------------------
        # 4. Temperature derivative
        # --------------------------------------------------

        self.temperature_rate_c_per_s = (
            self.net_heat_w
            / self.thermal_capacity_j_per_k
        )

        # --------------------------------------------------
        # 5. Integrate temperature
        # --------------------------------------------------

        self.temperature_c += (
            self.temperature_rate_c_per_s * dt_s
        )

        return self.temperature_c

    def get_temperature(self) -> float:
        """Return battery temperature in °C."""
        return self.temperature_c

    def get_heat_generation(self) -> float:
        """Return instantaneous Joule heat generation in W."""
        return self.heat_generation_w

    def get_heat_loss(self) -> float:
        """Return instantaneous heat rejection in W."""
        return self.heat_loss_w

    def get_net_heat(self) -> float:
        """Return net thermal power in W."""
        return self.net_heat_w

    def get_temperature_rate(self) -> float:
        """Return temperature rate in °C/s."""
        return self.temperature_rate_c_per_s
