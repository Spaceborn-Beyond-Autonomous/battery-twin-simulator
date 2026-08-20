class OCVModel:
    """
    Open-Circuit Voltage model.

    Uses a configurable SOC -> cell voltage lookup table.

    SOC:
        0.0 = 0%
        1.0 = 100%
    """

    def __init__(self, soc_points, voltage_points, series_cells):

        if len(soc_points) != len(voltage_points):
            raise ValueError(
                "SOC and voltage tables must have equal length."
            )

        if len(soc_points) < 2:
            raise ValueError(
                "At least two OCV points are required."
            )

        if series_cells <= 0:
            raise ValueError(
                "Number of series cells must be greater than zero."
            )

        self.soc_points = soc_points
        self.voltage_points = voltage_points
        self.series_cells = series_cells

    def get_cell_voltage(self, soc):

        soc = max(0.0, min(1.0, soc))

        for i in range(len(self.soc_points) - 1):

            soc_low = self.soc_points[i]
            soc_high = self.soc_points[i + 1]

            if soc_low <= soc <= soc_high:

                voltage_low = self.voltage_points[i]
                voltage_high = self.voltage_points[i + 1]

                ratio = (
                    (soc - soc_low)
                    / (soc_high - soc_low)
                )

                return (
                    voltage_low
                    + ratio * (voltage_high - voltage_low)
                )

        return self.voltage_points[-1]

    def get_pack_voltage(self, soc):

        cell_voltage = self.get_cell_voltage(soc)

        return cell_voltage * self.series_cells
