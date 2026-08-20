from batterytwin.battery_config_loader import load_battery_config
from batterytwin.battery_model import BatteryModel


config = load_battery_config(
    "config/batteries/spektrum_6s_5000mah_100c.yaml"
)

battery = BatteryModel(
    config=config,
    initial_soc=0.50,
)

for step in range(10):

    state = battery.update(
        current_a=-10.0,
        dt_s=1.0,
        temperature_c=25.0,
    )

    print(
        f"t={state.simulation_time_s:2.0f}s | "
        f"SOC={state.soc * 100:.4f}% | "
        f"Voltage={state.voltage_v:.3f} V | "
        f"Current={state.current_a:.2f} A | "
        f"Power={state.power_w:.2f} W"
    )
