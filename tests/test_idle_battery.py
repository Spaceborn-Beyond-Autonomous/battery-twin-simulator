from batterytwin.battery_config_loader import load_battery_config
from batterytwin.battery_model import BatteryModel


config = load_battery_config(
    "config/batteries/spektrum_6s_5000mah_100c.yaml"
)

battery = BatteryModel(config=config)

state = battery.update(
    current_a=0.0,
    dt_s=1.0,
    temperature_c=25.0,
)

print(f"SOC: {state.soc * 100:.4f}%")
print(f"Voltage: {state.voltage_v:.4f} V")
print(f"Current: {state.current_a:.4f} A")
print(f"Power: {state.power_w:.4f} W")
print(f"Energy consumed: {state.energy_consumed_wh:.6f} Wh")
