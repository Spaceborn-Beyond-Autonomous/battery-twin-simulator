from batterytwin.aging_model import AgingModel


aging = AgingModel(
    initial_soh=1.0,
    capacity_fade_per_cycle=0.0005,
    resistance_growth_factor=1.5,
)

print("Initial SOH:", aging.get_soh())
print(
    "Initial resistance factor:",
    aging.get_resistance_factor()
)

for cycle in range(1, 11):

    soh = aging.update(1.0)

    print(
        f"Cycle={cycle:2d} | "
        f"SOH={soh * 100:.4f}% | "
        f"Resistance factor="
        f"{aging.get_resistance_factor():.6f}"
    )
