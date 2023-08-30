import numpy as np
from energy_data_extractor import EnergyData
from tariff_extractor import EnergyTariff
from battery_control import BatteryControl
import energy_chart_seaborn
from tabulate import tabulate

#------- User parameters

# set source for energy bill data
inverter_readings_path = '/Users/luke/Documents/1. Projects/2. Noah Energy/1. Research/1. Energy bills'
# set name of tariff file
tariff_file_name = '/2023-08-16 Energy tariffs.xlsx'

# set battery parameters
battery_capacity = 16 # set battery capacity in kWh
max_SOC = 1 * battery_capacity # set max SOC to 100% of capacity
min_SOC = 0.04 * battery_capacity # set min SOC to 4% of capacity
battery_max_charge = 3.7 # set the battery's max charge rate in kW
battery_max_discharge = 3.7 # set the battery's max discharge rate in kW

# Set time intervals in minutes
time_intervals = '5T'

# ------ Remainder of code

# find the s and h arrays from the energy bill data
s, h, b_default, SOC_default, g_default, starting_SOC, chart_save_path = EnergyData.extract_data(inverter_readings_path,time_intervals, battery_capacity)

# Generate an array of time intervals for a 24-hour period
readings_per_hour = round(len(s)/24,0)
t = np.arange(0, 24 * 60, 60/readings_per_hour)

# import energy tariffs from excel file that is saved in the same root folder as the inverter readings
tariffs = EnergyTariff.read_arrays_from_excel(inverter_readings_path+tariff_file_name,t)

# Determine number of tariff pairs
num_tariff_pairs = int(len(tariffs)/2)

# assign tariffs and set tariff names
i_1 = tariffs[0].values.flatten()
e_1 = tariffs[0+num_tariff_pairs].values.flatten()
first_tariff_name = tariffs[0].columns.name + ' + ' + tariffs[0+num_tariff_pairs].columns.name
i_2 = tariffs[1].values.flatten()
e_2 = tariffs[1+num_tariff_pairs].values.flatten()
second_tariff_name = tariffs[1].columns.name + ' + ' + tariffs[1+num_tariff_pairs].columns.name
i_3 = tariffs[2].values.flatten()
e_3 = tariffs[2+num_tariff_pairs].values.flatten()
third_tariff_name = tariffs[2].columns.name + ' + ' + tariffs[2+num_tariff_pairs].columns.name
tariff_names = [first_tariff_name, second_tariff_name, third_tariff_name]

# Initialize b, g, and SOC arrays
b_arrays = [np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float)]
g_arrays = [np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float)]
SOC_arrays = [np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float), np.zeros_like(t, dtype=float)]

# assign default battery and grid load arrays to the arrays sets
b_arrays[0] = b_default
g_arrays[0] = g_default
SOC_arrays[0] = SOC_default * battery_capacity # convert from % to kWh

# Set up the energy bill table
energy_bill_table = [["Tariff name", "Daily import bill (£)", "Daily export bill (£)", "Total daily bill (£)"],
                     [tariff_names[0], round(-np.sum(np.maximum(0, g_default) * e_1) / readings_per_hour, 2), 0, round(-np.sum(np.maximum(0, g_default) * e_1) / readings_per_hour, 2)],
                     [tariff_names[1], None, None, None],
                     [tariff_names[2], None, None, None]]

# skip the first tariff because it uses the existing battery control logic
tariff_counter = 1

# Iterate over the second and third energy tariffs
for import_tariff, export_tariff in [(i_2, e_2),(i_3, e_3)]:

    # Create separate b, g, and SOC arrays for each control mechanism
    b = np.zeros_like(t, dtype=float)
    SOC = np.zeros_like(t, dtype=float)
    SOC[0] = starting_SOC * max_SOC if tariff_counter == 0 else 0.1 * max_SOC

    # Calculate battery power, battery SOC, and grid draw for the given tariff
    b, SOC, g = BatteryControl.find_power_and_SOC(s,h,min_SOC,max_SOC,import_tariff,export_tariff,readings_per_hour, battery_max_charge, battery_max_discharge)

    # Calculate the energy bill based on the tariff and grid draw and divide by readings per hour
    import_energy_bill = -np.sum(np.minimum(0, g) * import_tariff) / readings_per_hour
    export_energy_bill = -np.sum(np.maximum(0, g) * export_tariff) / readings_per_hour
    energy_bill = import_energy_bill + export_energy_bill

    # add the energy bills to the table
    energy_bill_table[tariff_counter+1] = [tariff_names[tariff_counter], round(import_energy_bill,2), round(export_energy_bill,2), round(energy_bill,2)]

    # add the battery and grid load arrays to their respective array sets
    b_arrays[tariff_counter] = b
    g_arrays[tariff_counter] = g
    SOC_arrays[tariff_counter] = SOC

    tariff_counter = tariff_counter + 1

# Print the output table
print(tabulate(energy_bill_table, headers = 'firstrow', tablefmt='fancy_grid'), '\n')
# print and save down the tariff charts
for i in range (0,num_tariff_pairs-1):
    energy_chart_seaborn.create_chart(s, h, t, b_arrays, g_arrays, SOC_arrays, i, tariff_names, chart_save_path)

# print daily house consumption and solar generation
print('House daily kWh consumption: ', round(np.sum(h)/readings_per_hour,1),' kWh')
print('Solar daily kWh generation: ', round(np.sum(s)/readings_per_hour,1),' kWh')