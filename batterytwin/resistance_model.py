class ResistanceModel:
    """
    SOC-, temperature-, and SOH-dependent battery internal resistance.

    Base model:

        R = R0 * f_soc * f_temp * f_soh

    where:

        R0     = resistance of a new battery at nominal conditions
        f_soc  = SOC correction factor
        f_temp = temperature correction factor
        f_soh  = aging correction factor

    Sign convention:
        Resistance is always positive.

    Notes:
        This is a compact engineering model intended for simulation.
        Parameters should eventually be identified from manufacturer
        pulse-test / HPPC data for the specific battery chemistry.
    """

    def __init__(
        self,
        resistance_ohm: float,
        nominal_temperature_c: float = 25.0,
        minimum_soc: float = 0.05,
        cold_temperature_c: float = 0.0,
        hot_temperature_c: float = 45.0,
        cold_resistance_factor: float = 2.0,
        low_soc_resistance_factor: float = 1.5,
    ):
        if resistance_ohm <= 0:
            raise ValueError(
                "Base resistance must be greater than zero."
            )

        if minimum_soc <= 0 or minimum_soc >= 1:
            raise ValueError(
                "Minimum SOC must be between 0 and 1."
            )

        if cold_temperature_c >= nominal_temperature_c:
            raise ValueError(
                "Cold temperature must be below nominal temperature."
            )

        if hot_temperature_c <= nominal_temperature_c:
            raise ValueError(
                "Hot temperature must be above nominal temperature."
            )

        if cold_resistance_factor < 1.0:
            raise ValueError(
                "Cold resistance factor must be >= 1."
            )

        if low_soc_resistance_factor < 1.0:
            raise ValueError(
                "Low SOC resistance factor must be >= 1."
            )

        self.resistance_ohm = resistance_ohm
        self.nominal_temperature_c = nominal_temperature_c
        self.minimum_soc = minimum_soc

        self.cold_temperature_c = cold_temperature_c
        self.hot_temperature_c = hot_temperature_c

        self.cold_resistance_factor = cold_resistance_factor
        self.low_soc_resistance_factor = low_soc_resistance_factor

    def _soc_factor(self, soc: float) -> float:
        """
        Increase resistance progressively as SOC approaches zero.
        """

        soc = max(0.0, min(1.0, soc))

        if soc >= 0.20:
            return 1.0

        normalized = (
            (0.20 - soc)
            / (0.20 - self.minimum_soc)
        )

        normalized = max(0.0, min(1.0, normalized))

        return (
            1.0
            + (
                self.low_soc_resistance_factor - 1.0
            )
            * normalized
        )

    def _temperature_factor(
        self,
        temperature_c: float,
    ) -> float:
        """
        Temperature correction.

        At 25 C:
            factor = 1.0

        At cold temperature:
            resistance increases.

        Above nominal temperature:
            resistance changes only mildly.
        """

        if temperature_c <= self.nominal_temperature_c:

            if temperature_c <= self.cold_temperature_c:
                return self.cold_resistance_factor

            ratio = (
                self.nominal_temperature_c - temperature_c
            ) / (
                self.nominal_temperature_c
                - self.cold_temperature_c
            )

            return (
                1.0
                + (
                    self.cold_resistance_factor - 1.0
                ) * ratio
            )

        # Mild increase at elevated temperature.
        temperature_delta = (
            temperature_c
            - self.nominal_temperature_c
        )

        return 1.0 + 0.005 * temperature_delta

    def get_resistance(
        self,
        soc: float,
        temperature_c: float,
        soh: float = 1.0,
    ) -> float:
        """
        Calculate effective internal resistance.

        Parameters
        ----------
        soc:
            State of charge, 0.0 to 1.0.

        temperature_c:
            Battery temperature in degrees Celsius.

        soh:
            State of health, 0.0 to 1.0.

        Returns
        -------
        float
            Effective internal resistance in ohms.
        """

        if not 0.0 <= soc <= 1.0:
            raise ValueError(
                "SOC must be between 0 and 1."
            )

        if not 0.0 < soh <= 1.0:
            raise ValueError(
                "SOH must be greater than 0 and <= 1."
            )

        soc_factor = self._soc_factor(soc)

        temperature_factor = self._temperature_factor(
            temperature_c
        )

        # Aging relationship:
        #
        # SOH = 1.0 -> factor = 1.0
        # SOH -> 0   -> resistance increases strongly
        #
        # The coefficient provides a smooth engineering
        # approximation of resistance growth.
        soh_factor = 1.0 + 1.5 * (1.0 - soh)

        return (
            self.resistance_ohm
            * soc_factor
            * temperature_factor
            * soh_factor
        )
