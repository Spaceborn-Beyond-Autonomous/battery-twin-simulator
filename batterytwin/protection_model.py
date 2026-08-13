import math
from dataclasses import dataclass


@dataclass
class ProtectionStatus:
    """
    Battery protection status.

    True means the corresponding protection condition
    is currently active.
    """

    over_voltage: bool = False
    under_voltage: bool = False
    over_temperature: bool = False
    under_temperature: bool = False
    over_current: bool = False

    fault: bool = False

    @property
    def healthy(self) -> bool:
        return not self.fault


class ProtectionModel:
    """
    Battery operating-limit and protection model.

    The model monitors:
        - Pack voltage
        - Battery temperature
        - Battery current

    Current convention:
        positive current -> discharge
        negative current -> charge

    Protection limits are intentionally configurable.
    """

    def __init__(
        self,
        min_voltage_v: float,
        max_voltage_v: float,
        min_temperature_c: float,
        max_temperature_c: float,
        max_discharge_current_a: float,
        max_charge_current_a: float,
    ):
        limits = {
            "Minimum voltage": min_voltage_v,
            "Maximum voltage": max_voltage_v,
            "Minimum temperature": min_temperature_c,
            "Maximum temperature": max_temperature_c,
            "Maximum discharge current": max_discharge_current_a,
            "Maximum charge current": max_charge_current_a,
        }

        for name, value in limits.items():
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite.")

        if min_voltage_v < 0:
            raise ValueError(
                "Minimum voltage cannot be negative."
            )

        if max_voltage_v <= min_voltage_v:
            raise ValueError(
                "Maximum voltage must be greater than minimum voltage."
            )

        if max_temperature_c <= min_temperature_c:
            raise ValueError(
                "Maximum temperature must be greater than minimum temperature."
            )

        if max_discharge_current_a < 0:
            raise ValueError(
                "Maximum discharge current cannot be negative."
            )

        if max_charge_current_a < 0:
            raise ValueError(
                "Maximum charge current cannot be negative."
            )

        self.min_voltage_v = min_voltage_v
        self.max_voltage_v = max_voltage_v

        self.min_temperature_c = min_temperature_c
        self.max_temperature_c = max_temperature_c

        self.max_discharge_current_a = (
            max_discharge_current_a
        )

        self.max_charge_current_a = (
            max_charge_current_a
        )

        self.status = ProtectionStatus()

    def check(
        self,
        voltage_v: float,
        temperature_c: float,
        current_a: float,
    ) -> ProtectionStatus:
        """
        Evaluate all protection conditions.

        Returns:
            ProtectionStatus containing the active faults.
        """

        values = {
            "Voltage": voltage_v,
            "Temperature": temperature_c,
            "Current": current_a,
        }

        for name, value in values.items():
            if not math.isfinite(value):
                raise ValueError(
                    f"{name} must be finite."
                )

        self.status.over_voltage = (
            voltage_v > self.max_voltage_v
        )

        self.status.under_voltage = (
            voltage_v < self.min_voltage_v
        )

        self.status.over_temperature = (
            temperature_c > self.max_temperature_c
        )

        self.status.under_temperature = (
            temperature_c < self.min_temperature_c
        )

        self.status.over_current = (
            current_a > self.max_discharge_current_a
            or
            current_a < -self.max_charge_current_a
        )

        self.status.fault = (
            self.status.over_voltage
            or self.status.under_voltage
            or self.status.over_temperature
            or self.status.under_temperature
            or self.status.over_current
        )

        return self.status

    def is_safe(
        self,
        voltage_v: float,
        temperature_c: float,
        current_a: float,
    ) -> bool:
        """
        Return True when all protection limits are satisfied.
        """

        return self.check(
            voltage_v=voltage_v,
            temperature_c=temperature_c,
            current_a=current_a,
        ).healthy

    def get_status(self) -> ProtectionStatus:
        """Return the latest protection status."""
        return self.status
