from batterytwin.battery_config_loader import load_battery_config


config = load_battery_config(
    "config/batteries/spektrum_6s_5000mah_100c.yaml"
)


print("Name:", config.name)
print("Chemistry:", config.chemistry)
print("Cells:", f"{config.series_cells}S{config.parallel_cells}P")
print("Capacity:", config.nominal_capacity_ah, "Ah")
print("Nominal voltage:", config.nominal_voltage_v, "V")
print("Maximum voltage:", config.pack_max_voltage_v, "V")
print("Energy:", config.nominal_energy_wh, "Wh")
print("Mass:", config.mass_kg, "kg")
print("Discharge:", config.continuous_discharge_c, "C")
print("Charge:", config.maximum_charge_c, "C")
