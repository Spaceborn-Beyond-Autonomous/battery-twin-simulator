from batterytwin.battery_state import BatteryState
from batterytwin.battery_config import BatteryConfig
from batterytwin.soc_model import SOCModel
from batterytwin.ocv_model import OCVModel
from batterytwin.resistance_model import ResistanceModel
from batterytwin.rc_model import RCModel
from batterytwin.energy_model import EnergyModel
from batterytwin.power_model import PowerModel
from batterytwin.thermal_model import ThermalModel
from batterytwin.aging_model import AgingModel
from batterytwin.protection_model import ProtectionModel


class BatteryModel:
    """
    Integrated BatteryTwin battery model.

    Includes:

        - SOC
        - SOH / battery aging
        - OCV
        - Internal resistance
        - RC polarization
        - Power
        - Energy
        - Thermal behavior
        - Automatic equivalent-full-cycle tracking
        - Current limits
        - Battery protection

    Current convention:

        current > 0  -> discharge
        current < 0  -> charge
        power > 0    -> discharge
        power < 0    -> charge
    """

    def __init__(
        self,
        config: BatteryConfig,
        initial_soc: float = 1.0,
        initial_soh: float = 1.0,
        r0_ohm: float = 0.020,
        r1_ohm: float = 0.010,
        c1_f: float = 1000.0,
    ):

        self.config = config

        # ==================================================
        # BATTERY STATE
        # ==================================================

        self.state = BatteryState()

        # ==================================================
        # AGING
        # ==================================================

        self.aging_model = AgingModel(
            initial_soh=initial_soh
        )

        # ==================================================
        # AUTOMATIC EFC TRACKING
        # ==================================================

        # Accumulated absolute charge throughput [Ah].
        #
        # 2 * nominal_capacity corresponds to
        # approximately one Equivalent Full Cycle.
        self.charge_throughput_ah = 0.0

        # ==================================================
        # EFFECTIVE CAPACITY
        # ==================================================

        effective_capacity_ah = (
            config.nominal_capacity_ah
            * self.aging_model.get_capacity_factor()
        )

        # ==================================================
        # SOC
        # ==================================================

        self.soc_model = SOCModel(
            capacity_ah=effective_capacity_ah,
            initial_soc=initial_soc,
        )

        # ==================================================
        # OCV
        # ==================================================

        self.ocv_model = OCVModel(
            soc_points=[
                0.0,
                0.5,
                1.0,
            ],
            voltage_points=[
                3.3,
                3.75,
                4.2,
            ],
            series_cells=config.series_cells,
        )

        # ==================================================
        # RESISTANCE
        # ==================================================

        # Store fresh/new-battery resistance.
        self.base_r0_ohm = r0_ohm

        self.resistance_model = ResistanceModel(
            resistance_ohm=r0_ohm
        )

        # ==================================================
        # RC POLARIZATION
        # ==================================================

        self.rc_model = RCModel(
            resistance_ohm=r1_ohm,
            capacitance_f=c1_f,
        )

        # ==================================================
        # ENERGY
        # ==================================================

        self.energy_model = EnergyModel(
            initial_energy_wh=config.nominal_energy_wh
        )

        # ==================================================
        # POWER
        # ==================================================

        self.power_model = PowerModel()

        # ==================================================
        # THERMAL
        # ==================================================

        self.thermal_model = ThermalModel(
            thermal_capacity_j_per_k=(
                config.thermal_capacity_j_per_k
            ),
            heat_transfer_w_per_k=(
                config.heat_transfer_w_per_k
            ),
            initial_temperature_c=(
                config.initial_temperature_c
            ),
            ambient_temperature_c=(
                config.ambient_temperature_c
            ),
        )

        # ==================================================
        # INITIAL STATE
        # ==================================================

        self.state.soc = initial_soc
        self.state.soh = initial_soh

        self.state.energy_remaining_wh = (
            config.nominal_energy_wh
        )

        self.state.energy_consumed_wh = 0.0

        self.state.temperature_c = (
            config.initial_temperature_c
        )

        # ==================================================
        # PROTECTION
        # ==================================================

        self.protection_model = ProtectionModel(
            min_voltage_v=(
                config.series_cells
                * config.cell_nominal_voltage_v
                * 0.90
            ),

            max_voltage_v=(
                config.pack_max_voltage_v
            ),

            min_temperature_c=0.0,

            max_temperature_c=60.0,

            max_discharge_current_a=(
                config.continuous_discharge_c
                * config.nominal_capacity_ah
            ),

            max_charge_current_a=(
                config.maximum_charge_c
                * config.nominal_capacity_ah
            ),
        )

    # ======================================================
    # CAPACITY
    # ======================================================

    def get_effective_capacity_ah(self) -> float:
        """
        Return effective battery capacity [Ah].

        Q_effective = Q_nominal * SOH
        """

        return (
            self.config.nominal_capacity_ah
            * self.aging_model.get_capacity_factor()
        )

    # ======================================================
    # CURRENT LIMITS
    # ======================================================

    def get_max_discharge_current(self) -> float:
        """
        Maximum continuous discharge current [A].
        """

        return (
            self.config.continuous_discharge_c
            * self.get_effective_capacity_ah()
        )

    def get_max_charge_current(self) -> float:
        """
        Maximum charging current [A].
        """

        return (
            self.config.maximum_charge_c
            * self.get_effective_capacity_ah()
        )

    def validate_current(self, current_a: float) -> None:
        """
        Validate charge/discharge current.
        """

        max_discharge = (
            self.get_max_discharge_current()
        )

        max_charge = (
            self.get_max_charge_current()
        )

        if current_a > max_discharge:
            raise ValueError(
                f"Discharge current {current_a:.2f} A "
                f"exceeds limit of "
                f"{max_discharge:.2f} A"
            )

        if current_a < -max_charge:
            raise ValueError(
                f"Charge current {abs(current_a):.2f} A "
                f"exceeds limit of "
                f"{max_charge:.2f} A"
            )

    # ======================================================
    # AGING
    # ======================================================

    def update_aging(
        self,
        equivalent_full_cycles: float,
    ) -> float:
        """
        Update battery SOH after completed EFCs.
        """

        soh = self.aging_model.update(
            equivalent_full_cycles
        )

        # Update effective SOC capacity.
        self.soc_model.capacity_ah = (
            self.get_effective_capacity_ah()
        )

        # Increase resistance as battery ages.
        resistance_factor = (
            self.aging_model.get_resistance_factor()
        )

        self.resistance_model.resistance_ohm = (
            self.base_r0_ohm
            * resistance_factor
        )

        # Update state.
        self.state.soh = soh

        return soh

    # ======================================================
    # PROTECTION
    # ======================================================

    def check_protection(self):
        """
        Check the current battery state against
        configured protection limits.
        """

        return self.protection_model.check(
            voltage_v=self.state.voltage_v,
            temperature_c=self.state.temperature_c,
            current_a=self.state.current_a,
        )

    def is_safe(self) -> bool:
        """
        Return True when the current battery state
        satisfies all protection limits.
        """

        return self.protection_model.is_safe(
            voltage_v=self.state.voltage_v,
            temperature_c=self.state.temperature_c,
            current_a=self.state.current_a,
        )

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        current_a: float,
        dt_s: float,
        temperature_c: float = None,
    ):
        """
        Advance battery simulation by dt_s seconds.
        """

        if dt_s < 0:
            raise ValueError(
                "Time step cannot be negative."
            )

        # --------------------------------------------------
        # 1. CURRENT LIMITS
        # --------------------------------------------------

        self.validate_current(current_a)

        # Use internally simulated temperature unless
        # an external temperature is supplied.
        if temperature_c is None:
            temperature_c = self.state.temperature_c

        # --------------------------------------------------
        # 2. SOC
        # --------------------------------------------------

        soc = self.soc_model.update(
            current_a=current_a,
            dt_s=dt_s,
        )

        # --------------------------------------------------
        # 3. OCV
        # --------------------------------------------------

        ocv_v = self.ocv_model.get_pack_voltage(
            soc
        )

        # --------------------------------------------------
        # 4. INTERNAL RESISTANCE
        # --------------------------------------------------

        r0 = self.resistance_model.get_resistance(
            soc=soc,
            temperature_c=temperature_c,
            soh=self.aging_model.get_soh(),
        )

        # --------------------------------------------------
        # 5. RC POLARIZATION
        # --------------------------------------------------

        polarization_v = self.rc_model.update(
            current_a=current_a,
            dt_s=dt_s,
        )

        # --------------------------------------------------
        # 6. TERMINAL VOLTAGE
        #
        # V = OCV - I*R0 - Vpolarization
        # --------------------------------------------------

        terminal_voltage = (
            ocv_v
            - current_a * r0
            - polarization_v
        )

        terminal_voltage = max(
            0.0,
            terminal_voltage,
        )

        # --------------------------------------------------
        # 7. POWER
        # --------------------------------------------------

        power_w = self.power_model.calculate(
            voltage_v=terminal_voltage,
            current_a=current_a,
        )

        # --------------------------------------------------
        # 8. ENERGY
        # --------------------------------------------------

        remaining_energy = (
            self.energy_model.update(
                power_w=power_w,
                dt_s=dt_s,
            )
        )

        consumed_energy = (
            self.energy_model.get_consumed_energy()
        )

        # --------------------------------------------------
        # 9. AUTOMATIC EFC TRACKING
        # --------------------------------------------------

        throughput_ah = (
            abs(current_a)
            * dt_s
            / 3600.0
        )

        self.charge_throughput_ah += (
            throughput_ah
        )

        # One EFC:
        #
        # 2 * Q_nominal Ah of total throughput
        #
        # Example:
        # 5 Ah battery
        # 10 Ah throughput = 1 EFC

        efc = (
            self.charge_throughput_ah
            / (
                2.0
                * self.config.nominal_capacity_ah
            )
        )

        if efc >= 1.0:

            completed_cycles = int(efc)

            self.update_aging(
                float(completed_cycles)
            )

            self.charge_throughput_ah -= (
                completed_cycles
                * 2.0
                * self.config.nominal_capacity_ah
            )

        # --------------------------------------------------
        # 10. C-RATE
        # --------------------------------------------------

        capacity = self.soc_model.capacity_ah

        if capacity > 0.0:
            c_rate = (
                abs(current_a)
                / capacity
            )
        else:
            c_rate = 0.0

        # --------------------------------------------------
        # 11. THERMAL MODEL
        # --------------------------------------------------

        temperature = (
            self.thermal_model.update(
                current_a=current_a,
                resistance_ohm=r0,
                dt_s=dt_s,
            )
        )

        # --------------------------------------------------
        # 12. UPDATE BATTERY STATE
        # --------------------------------------------------

        self.state.voltage_v = terminal_voltage
        self.state.current_a = current_a
        self.state.power_w = power_w

        self.state.soc = soc

        self.state.soh = (
            self.aging_model.get_soh()
        )

        self.state.c_rate = c_rate

        self.state.temperature_c = temperature

        self.state.energy_remaining_wh = (
            remaining_energy
        )

        self.state.energy_consumed_wh = (
            consumed_energy
        )

        self.state.simulation_time_s += dt_s

        # --------------------------------------------------
        # 13. PROTECTION STATUS
        # --------------------------------------------------

        self.protection_model.check(
            voltage_v=terminal_voltage,
            temperature_c=temperature,
            current_a=current_a,
        )

        # Return latest battery state.
        return self.state

    # ======================================================
    # GETTERS
    # ======================================================

    def get_state(self) -> BatteryState:
        """
        Return current battery state.
        """

        return self.state

    def get_soh(self) -> float:
        """
        Return State of Health.
        """

        return self.aging_model.get_soh()

    def get_soc(self) -> float:
        """
        Return State of Charge.
        """

        return self.soc_model.get_soc()

    def get_temperature(self) -> float:
        """
        Return battery temperature [°C].
        """

        return self.thermal_model.get_temperature()

    def get_resistance_factor(self) -> float:
        """
        Return aging-related resistance multiplier.
        """

        return (
            self.aging_model.get_resistance_factor()
        )

    def get_charge_throughput_ah(self) -> float:
        """
        Return accumulated charge throughput [Ah].
        """

        return self.charge_throughput_ah
