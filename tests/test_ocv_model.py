from batterytwin.ocv_model import OCVModel


ocv = OCVModel(
    soc_points=[0.0, 0.5, 1.0],
    voltage_points=[3.3, 3.75, 4.2],
    series_cells=6
)


for soc in [0.0, 0.25, 0.5, 0.75, 1.0]:

    cell_voltage = ocv.get_cell_voltage(soc)
    pack_voltage = ocv.get_pack_voltage(soc)

    print(
        f"SOC={soc:.2f} | "
        f"Cell={cell_voltage:.3f} V | "
        f"Pack={pack_voltage:.3f} V"
    )
