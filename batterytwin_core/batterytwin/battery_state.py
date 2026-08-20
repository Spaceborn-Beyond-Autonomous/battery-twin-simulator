from dataclasses import dataclass


@dataclass
class BatteryState:
    voltage_v: float = 0.0
    current_a: float = 0.0
    power_w: float = 0.0

    soc: float = 1.0
    soh: float = 1.0

    temperature_c: float = 25.0

    energy_remaining_wh: float = 0.0
    energy_consumed_wh: float = 0.0

    c_rate: float = 0.0

    simulation_time_s: float = 0.0
    
    protection_fault: bool = False

    over_voltage: bool = False
    under_voltage: bool = False
    over_temperature: bool = False
    under_temperature: bool = False
    over_current: bool = False
