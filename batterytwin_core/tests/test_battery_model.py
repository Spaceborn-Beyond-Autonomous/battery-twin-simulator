from batterytwin.battery_config_loader import load_battery_config
from batterytwin.battery_model import BatteryModel


CONFIG_FILE = (
    "config/batteries/spektrum_6s_5000mah_100c.yaml"
)


config = load_battery_config(CONFIG_FILE)


battery = BatteryModel(
    config=config,
    initial_soc=1.0,
)


state = battery.update(
    current_a=20.0,
    dt_s=1.0,
)


print("Battery:", config.name)
print("Voltage:", state.voltage_v)
print("Current:", state.current_a)
print("SOC:", state.soc)
print("C-rate:", state.c_rate)
print("Power:", state.power_w)
print("Energy remaining:", state.energy_remaining_wh)
print("Energy consumed:", state.energy_consumed_wh)
print("Time:", state.simulation_time_s)
