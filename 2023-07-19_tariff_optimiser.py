import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import energy_data_extractor
import energy_chart
import energy_chart_seaborn
from tabulate import tabulate

# Generate an array of time intervals with 5-minute intervals for a 24-hour period
t = np.arange(0, 24 * 60, 5)
readings_per_hour = round(len(t)/24,0)

# set battery values    
battery_capacity = 8 # set battery capacity to 8kWh
max_SOC = 1 * battery_capacity # set max SOC to 100% of capacity
min_SOC = 0.04 * battery_capacity # set min SOC to 4% of capacity

# find the s and h arrays from the energy bill data
s, h, b_default, SOC_default, g_default, starting_SOC, chart_save_path = energy_data_extractor.extract_s_and_h(t)

# first tariff pair is a fixed import of 29p and fixed export of 15p (for solar only)
i_1 = np.full(len(t),0.29)
e_1 = np.full(len(t),0.15)

# second tariff pair is variable
i_2 = np.zeros_like(t,dtype=float)
e_2 = np.zeros_like(t,dtype=float)
for i in range (1, len(t)):
    if i >= 2 * readings_per_hour and i < 5 * readings_per_hour:
        i_2[i] = 0.1854
        e_2[i] = 0.0754
    elif i >= 16 * readings_per_hour and i < 19 * readings_per_hour:
        i_2[i] = 0.4326
        e_2[i] = 0.3226
    else:
        i_2[i] = 0.309
        e_2[i] = 0.199
# interpolate the tariff pairs to ensure length matches the t variable
i_2 = np.interp(np.linspace(0, len(i_2)-1, len(t)), np.arange(len(i_2)), i_2)
e_2 = np.interp(np.linspace(0, len(e_2)-1, len(t)), np.arange(len(e_2)), e_2)

# set tariff names
tariff_names = ["Price cap and SEG", "Flux", "Original"]

# Define different battery control mechanisms
# Each control mechanism can be represented by a function that takes t as input and returns the discharge rate b(t)
def battery_control_mechanism_1(t,b,SOC):

    for i in range(1, len(t)):
        
        b[i] = s[i] - h[i]

        if SOC[i-1] + b[i] * 5 / 60 > max_SOC:
            b[i] = (max_SOC - SOC[i-1]) * 60 / 5

        if SOC[i-1] + b[i] * 5 / 60 < min_SOC:
            b[i] = (min_SOC - SOC[i-1]) * 60 / 5

        SOC[i] = SOC[i-1] + b[i] * 5 / 60  # Calculate the state of charge (SOC) based on the cumulative battery discharge rate

    return b, SOC

def battery_control_mechanism_2(t,b,SOC):

    for i in range(1, len(t)):
        if t[i] >= 2 * 60 and t[i] < 5 * 60:  # Between 2am and 5am
            b[i] = 3 + s[i] - h[i] # Charge at 3 kW from the grid
        elif t[i] >= 16 * 60 and t[i] < 19 * 60:  # Between 4pm and 7pm
            b[i] = -3 + s[i] - h[i]  # Discharge at 3kW to grid
        else:  # All other times
            b[i] = s[i] - h[i]
        
        if SOC[i-1] + b[i] * 5 / 60 > max_SOC:
            b[i] = (max_SOC - SOC[i-1]) * 60 / 5

        if SOC[i-1] + b[i] * 5 / 60 < min_SOC:
            b[i] = (min_SOC - SOC[i-1]) * 60 / 5

        SOC[i] = SOC[i-1] + b[i] * 5 / 60  # Calculate the state of charge (SOC) based on the cumulative battery discharge rate

    return b, SOC


# Initialize variables to store the minimum energy bill and corresponding tariff-control mechanism pair
min_energy_bill = float('inf')
tariff_counter = 0

# Initialize b, g, and SOC arrays outside the functions
b_arrays = [np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float)]
g_arrays = [np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float)]
SOC_arrays = [np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float)]

# Iterate over each tariff and control mechanism combination
# Initialize variables to store the minimum energy bill and corresponding tariff-control mechanism pair
min_energy_bill = float('inf')
optimal_tariff = None
optimal_control_mechanism = None
b_optimal = None
SOC_optimal = None
g_optimal = None

# Set up the energy bill table
energy_bill_table = [["Tariff name", "Daily import bill (£)", "Daily export bill (£)", "Total daily bill (£)"],
                     [tariff_names[0], None, None, None],
                     [tariff_names[1], None, None, None],
                     [tariff_names[2], round(-np.sum(np.minimum(0, g_default) * i_1) / readings_per_hour, 2), 0, round(-np.sum(np.minimum(0, g_default) * i_1) / readings_per_hour, 2)]]

# Iterate over each tariff and control mechanism combination
for import_tariff, export_tariff, control_mechanism in [(i_1, e_1, battery_control_mechanism_1),
                                                        (i_2, e_2, battery_control_mechanism_2)]:

    # Create separate b, g, and SOC arrays for each control mechanism
    b = np.zeros_like(t, dtype=float)
    SOC = np.zeros_like(t, dtype=float)
    SOC[0] = starting_SOC * max_SOC if tariff_counter == 0 else 0.1 * max_SOC

    # Calculate the battery power and the battery SOC for the given control scheme
    b, SOC = control_mechanism(t, b, SOC)

    g = -h - b + s

    # Calculate the energy bill based on the tariff and grid draw and divide by readings per hour
    import_energy_bill = -np.sum(np.minimum(0, g) * import_tariff) / readings_per_hour
    export_energy_bill = -np.sum(np.maximum(0, g) * export_tariff) / readings_per_hour
    energy_bill = import_energy_bill + export_energy_bill

    energy_bill_table[tariff_counter+1] = [tariff_names[tariff_counter], round(import_energy_bill,2), round(export_energy_bill,2), round(energy_bill,2)]

    b_arrays[tariff_counter] = b
    g_arrays[tariff_counter] = g
    SOC_arrays[tariff_counter] = SOC

    tariff_counter = tariff_counter + 1



b_arrays[2] = b_default
g_arrays[2] = g_default
SOC_arrays[2] = SOC_default

# Print the output table
print(tabulate(energy_bill_table, headers = 'firstrow', tablefmt='fancy_grid'), '\n')

# chart the system behaviours
# energy_chart.create_chart(s, h, t, b_arrays, g_arrays, SOC_arrays, 0, tariff_names, chart_save_path) # first tariff.
# energy_chart.create_chart(s, h, t, b_arrays, g_arrays, SOC_arrays, 1, tariff_names, chart_save_path) # second tariff

# print both tariff charts
energy_chart_seaborn.create_chart(s, h, t, b_arrays, g_arrays, SOC_arrays, 0, tariff_names, chart_save_path)
energy_chart_seaborn.create_chart(s, h, t, b_arrays, g_arrays, SOC_arrays, 1, tariff_names, chart_save_path)
energy_chart_seaborn.create_chart(s, h, t, b_arrays, g_arrays, SOC_arrays, 2, tariff_names, chart_save_path)

# print daily house consumption and soalr generaiton
print('House daily kWh consumption: ', np.sum(h)/readings_per_hour)
print('Solar daily kWh generation: ', np.sum(s)/readings_per_hour)