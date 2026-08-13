from batterytwin.resistance_model import ResistanceModel


model = ResistanceModel(
    resistance_ohm=0.020
)

print("========== RESISTANCE MODEL ==========")

conditions = [
    ("New / 25C / 100% SOC", 1.00, 25.0, 1.00),
    ("New / 25C / 50% SOC", 0.50, 25.0, 1.00),
    ("New / 25C / 10% SOC", 0.10, 25.0, 1.00),
    ("New / 0C / 50% SOC", 0.50, 0.0, 1.00),
    ("New / -10C / 50% SOC", 0.50, -10.0, 1.00),
    ("Aged / 25C / 50% SOC", 0.50, 25.0, 0.80),
]

for name, soc, temperature, soh in conditions:

    resistance = model.get_resistance(
        soc=soc,
        temperature_c=temperature,
        soh=soh,
    )

    print(
        f"{name:30s} | "
        f"R={resistance:.6f} ohm"
    )
