import numpy as np

class BatteryControl: 
    def __init__(self):
        pass
    
    @classmethod
    def find_power_and_SOC(cls, s, h, min_SOC, max_SOC, import_tariff, export_tariff, readings_per_hour, max_charge, max_discharge):
        average_import_tariff = import_tariff.mean()
        average_export_tariff = export_tariff.mean()
        reading_intervals = 60/readings_per_hour

        b = np.zeros_like(s,dtype = float)
        SOC = np.zeros_like(s, dtype=float)

        # if there is a flat import / export tariff pair, employ a simple self-consumption battery control mechanism
        if np.std(import_tariff) + np.std(export_tariff) == 0:
        
            for i in range (1,len(s)):

                # battery charge / (discharge) is simply the solar generation minus the house load
                b[i] = s[i] - h[i]

                # controls to ensure the battery SOC doesn't exceed the limits
                if SOC[i-1] + b[i] * reading_intervals / 60 > max_SOC:
                    b[i] = (max_SOC - SOC[i-1]) * 60 / reading_intervals

                if SOC[i-1] + b[i] * reading_intervals / 60 < min_SOC:
                    b[i] = (min_SOC - SOC[i-1]) * 60 / reading_intervals

                # Calculate the state of charge (SOC) based on the cumulative battery discharge rate
                SOC[i] = SOC[i-1] + b[i] * reading_intervals / 60

        else:

            for i in range (1,len(s)):

                # during off-peak periods
                if import_tariff[i]<average_import_tariff and export_tariff[i]<average_export_tariff:
                    # Charge from grid, in kW
                    b[i] = max_charge + s[i] - h[i]
                # during peak periods
                elif import_tariff[i]>average_import_tariff and export_tariff[i]>average_export_tariff:
                    # Discharge to grid, in kW
                    b[i] = -max_discharge
                else:
                    b[i] = s[i] - h[i]
                # controls to ensure the battery SOC doesn't exceed the limits
                if SOC[i - 1] + b[i] * reading_intervals / 60 > max_SOC:
                    b[i] = (max_SOC - SOC[i - 1]) * 60 / reading_intervals

                if SOC[i - 1] + b[i] * reading_intervals / 60 < min_SOC:
                    b[i] = (min_SOC - SOC[i - 1]) * 60 / reading_intervals

                # Calculate the state of charge (SOC) based on the cumulative battery discharge rate
                SOC[i] = SOC[i - 1] + b[i] * reading_intervals / 60
        
        # determine the resulting grid load
        g = -h - b + s
        return b, SOC, g
    