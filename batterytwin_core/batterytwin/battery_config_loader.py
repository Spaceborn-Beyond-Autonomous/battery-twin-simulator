import yaml

from batterytwin.battery_config import BatteryConfig


def load_battery_config(filename: str) -> BatteryConfig:
    """
    Load a battery configuration from a YAML file
    and convert it into a BatteryConfig object.
    """

    with open(filename, "r") as file:
        data = yaml.safe_load(file)

    battery = data["battery"]

    return BatteryConfig(
        name=battery["name"],
        chemistry=battery["chemistry"],

        series_cells=battery["cells"]["series"],
        parallel_cells=battery["cells"]["parallel"],

        nominal_capacity_ah=battery["capacity"]["nominal_ah"],

        nominal_voltage_v=battery["voltage"]["nominal_v"],
        cell_nominal_voltage_v=battery["voltage"]["cell_nominal_v"],
        cell_max_voltage_v=battery["voltage"]["cell_max_v"],
        pack_max_voltage_v=battery["voltage"]["pack_max_v"],

        continuous_discharge_c=battery["discharge"]["continuous_c"],
        maximum_charge_c=battery["charge"]["maximum_c"],

        nominal_energy_wh=battery["energy"]["nominal_wh"],
        mass_kg=battery["physical"]["mass_kg"],
        
        initial_temperature_c=battery["thermal"]["initial_temperature_c"],
        ambient_temperature_c=battery["thermal"]["ambient_temperature_c"],
        thermal_capacity_j_per_k=battery["thermal"]["thermal_capacity_j_per_k"],
        heat_transfer_w_per_k=battery["thermal"]["heat_transfer_w_per_k"],
    )
