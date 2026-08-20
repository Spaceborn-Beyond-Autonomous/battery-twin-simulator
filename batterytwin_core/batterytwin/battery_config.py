from dataclasses import dataclass


@dataclass
class BatteryConfig:
    name: str
    chemistry: str

    series_cells: int
    parallel_cells: int

    nominal_capacity_ah: float

    nominal_voltage_v: float
    cell_nominal_voltage_v: float
    cell_max_voltage_v: float
    pack_max_voltage_v: float

    continuous_discharge_c: float
    maximum_charge_c: float

    nominal_energy_wh: float
    mass_kg: float
    
    initial_temperature_c: float
    ambient_temperature_c: float
    thermal_capacity_j_per_k: float
    heat_transfer_w_per_k: float
