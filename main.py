import numpy as np
from energy_data_extractor import EnergyData
from tariff_extractor import EnergyTariff
from battery_control import BatteryControl
import energy_chart_seaborn
from tabulate import tabulate

#------- User parameters

# set source for energy bill data
tariff_and_inverter_readings_path = '/Users/luke/GitHub'
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
s, h, b_default, SOC_default, g_default, starting_SOC, chart_save_path = EnergyData.extract_data(tariff_and_inverter_readings_path,time_intervals)

# Generate an array of time intervals for a 24-hour period
readings_per_hour = round(len(s)/24,0)
t = np.arange(0, 24 * 60, 60/readings_per_hour)

# import energy tariffs from excel file that is saved in the same root folder as the inverter readings
tariffs = EnergyTariff.read_arrays_from_excel(tariff_and_inverter_readings_path+tariff_file_name,t)

# Determine number of tariff pairs
num_tariff_pairs = int(len(tariffs)/2)

# Initialize lists to store import tariffs, export tariffs, and tariff names
import_tariffs = []
export_tariffs = []
tariff_names = []

# Loop through the tariffs and assign values
for i in range(num_tariff_pairs):
    import_tariff = tariffs[i].values.flatten()
    export_tariff = tariffs[i + num_tariff_pairs].values.flatten()
    tariff_name = tariffs[i].columns.name + ' + ' + tariffs[i + num_tariff_pairs].columns.name

    import_tariffs.append(import_tariff)
    export_tariffs.append(export_tariff)
    tariff_names.append(tariff_name)

# Initialize b, g, and SOC lists
b_arrays = []
g_arrays = []
SOC_arrays = []

# Set up the energy bill table with headers
energy_bill_table = [["Tariff name", "Daily import bill (£)", "Daily export bill (£)", "Total daily bill (£)"]]

# skip the first tariff because it uses the existing battery control logic
tariff_counter = 0

# Iterate over the second and third energy tariffs
for import_tariff, export_tariff, tariff_name in zip(import_tariffs, export_tariffs, tariff_names):

    # set the battery power + SOC and grid draw to default behaviour for the first tariff
    if tariff_counter == 0:
        b = b_default
        g = g_default
        SOC = SOC_default * battery_capacity # convert from % to kWh
    else:
        # Calculate battery power, battery SOC, and grid draw for the given tariff
        b, SOC, g = BatteryControl.find_power_and_SOC(s,h,min_SOC,max_SOC,import_tariff,export_tariff,readings_per_hour, battery_max_charge, battery_max_discharge)

    # Calculate the energy bill based on the tariff and grid draw and divide by readings per hour
    import_energy_bill = -round(np.sum(np.minimum(0, g) * import_tariff) / readings_per_hour,2)
    export_energy_bill = -round(np.sum(np.maximum(0, g) * export_tariff) / readings_per_hour,2)
    energy_bill = import_energy_bill + export_energy_bill

    # add the energy bills to the table
    energy_bill_table.append([tariff_name, import_energy_bill, export_energy_bill, energy_bill])

    # add the battery and grid load arrays to their respective array sets
    b_arrays.append(b)
    g_arrays.append(g)
    SOC_arrays.append(SOC)

    tariff_counter = tariff_counter + 1

# Print the output table
print(tabulate(energy_bill_table, headers = 'firstrow', tablefmt='fancy_grid'), '\n')
# print and save down the tariff charts
for i in range (0,num_tariff_pairs-1):
    energy_chart_seaborn.create_chart(s, h, t, b_arrays, g_arrays, SOC_arrays, i, tariff_names, chart_save_path)

# print daily house consumption and solar generation
print('House daily kWh consumption: ', round(np.sum(h)/readings_per_hour,1),' kWh')
print('Solar daily kWh generation: ', round(np.sum(s)/readings_per_hour,1),' kWh')