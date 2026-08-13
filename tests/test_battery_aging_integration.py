from batterytwin.battery_model import BatteryModel
from batterytwin.battery_config_loader import load_battery_config


CONFIG_FILE = "config/batteries/spektrum_6s_5000mah_100c.yaml"


config = load_battery_config(CONFIG_FILE)

battery = BatteryModel(
    config=config,
    initial_soc=1.0,
    initial_soh=1.0,
)

print("========== BATTERY AGING INTEGRATION ==========")
print(f"Initial SOH: {battery.state.soh * 100:.4f}%")
print(
    f"Initial capacity: "
    f"{battery.get_effective_capacity_ah():.6f} Ah"
)

print(
    f"Initial resistance factor: "
    f"{battery.aging_model.get_resistance_factor():.6f}"
)

print()

# Simulate discharge
for second in range(1, 11):

    state = battery.update(
        current_a=20.0,
        dt_s=1.0,
    )

    print(
        f"t={second:2d}s | "
        f"SOC={state.soc * 100:8.4f}% | "
        f"SOH={state.soh * 100:8.4f}% | "
        f"Capacity={battery.get_effective_capacity_ah():.6f} Ah | "
        f"Voltage={state.voltage_v:7.3f} V | "
        f"Current={state.current_a:6.2f} A | "
        f"Temp={state.temperature_c:7.3f} °C"
    )

print()
print("========== FINAL AGING STATE ==========")

print(f"SOH: {battery.state.soh * 100:.6f}%")

print(
    f"Effective capacity: "
    f"{battery.get_effective_capacity_ah():.6f} Ah"
)

print(
    f"Resistance factor: "
    f"{battery.aging_model.get_resistance_factor():.6f}"
)

print(
    f"Charge throughput: "
    f"{battery.charge_throughput_ah:.6f} Ah"
)

print(
    f"Equivalent full cycles: "
    f"{battery.aging_model.cycle_count:.6f}"
)
