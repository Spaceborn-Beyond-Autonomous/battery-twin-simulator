from batterytwin.protection_model import ProtectionModel


protection = ProtectionModel(
    min_voltage_v=19.8,
    max_voltage_v=25.2,
    min_temperature_c=0.0,
    max_temperature_c=60.0,
    max_discharge_current_a=500.0,
    max_charge_current_a=15.0,
)


def show_test(name, voltage, temperature, current):
    status = protection.check(
        voltage_v=voltage,
        temperature_c=temperature,
        current_a=current,
    )

    print(
        f"{name:<30} | "
        f"FAULT={status.fault} | "
        f"OV={status.over_voltage} | "
        f"UV={status.under_voltage} | "
        f"OT={status.over_temperature} | "
        f"UT={status.under_temperature} | "
        f"OC={status.over_current}"
    )


print("========== PROTECTION MODEL ==========")

show_test(
    "Normal",
    voltage=22.2,
    temperature=25.0,
    current=20.0,
)

show_test(
    "Over-voltage",
    voltage=25.5,
    temperature=25.0,
    current=20.0,
)

show_test(
    "Under-voltage",
    voltage=19.0,
    temperature=25.0,
    current=20.0,
)

show_test(
    "Over-temperature",
    voltage=22.2,
    temperature=65.0,
    current=20.0,
)

show_test(
    "Under-temperature",
    voltage=22.2,
    temperature=-5.0,
    current=20.0,
)

show_test(
    "Over-discharge-current",
    voltage=22.2,
    temperature=25.0,
    current=600.0,
)

show_test(
    "Over-charge-current",
    voltage=22.2,
    temperature=25.0,
    current=-20.0,
)
