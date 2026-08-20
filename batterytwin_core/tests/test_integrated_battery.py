from batterytwin.battery_config_loader import load_battery_config
from batterytwin.battery_model import BatteryModel


config = load_battery_config(
    "config/batteries/spektrum_6s_5000mah_100c.yaml"
)


battery = BatteryModel(
    config=config,
    initial_soc=1.0,
)


print("BatteryTwin YAML-configured simulation")
print("--------------------------------------")

print(f"Battery: {config.name}")
print(f"Capacity: {config.nominal_capacity_ah} Ah")
print(f"Cells: {config.series_cells}S")
print(f"Nominal voltage: {config.nominal_voltage_v} V")
print(f"Nominal energy: {config.nominal_energy_wh} Wh")
print()


for step in range(10):

    state = battery.update(
        current_a=20.0,
        dt_s=1.0,
        temperature_c=25.0,
    )

    print(
        f"t={state.simulation_time_s:2.0f}s | "
        f"SOC={state.soc * 100:8.4f}% | "
        f"Voltage={state.voltage_v:7.3f} V | "
        f"Current={state.current_a:6.2f} A | "
        f"Power={state.power_w:8.2f} W | "
        f"Energy used={state.energy_consumed_wh:8.4f} Wh | "
        f"Energy left={state.energy_remaining_wh:8.4f} Wh"
    )
