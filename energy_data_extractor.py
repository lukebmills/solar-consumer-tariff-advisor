import pandas as pd
import os
import numpy as np
import glob

class EnergyData:

    def __init__(self):
        pass

    @classmethod
    def extract_data(cls,inverter_readings_path,t):

        # find folders in current folder
        folders_list = [folder for folder in os.listdir(inverter_readings_path) if os.path.isdir(os.path.join(inverter_readings_path, folder))]

        inverter_names = [folder.split('_')[-1] for folder in folders_list]

        # ask customer to select which set of inverter data to analyse
        inverter_data_select_input = "Choose which inverter data set to analyse: "
        for i in range(0,len(folders_list)):
            inverter_data_select_input = inverter_data_select_input + str(i+1) + " = " + folders_list[i] + ", "

        # ask which inverter data set to use
        inverter_data_select = int(input(inverter_data_select_input))-1
        bill_directory = inverter_readings_path+"/"+folders_list[inverter_data_select]

        # determine the inverter type based on the folder name. If not recognised then ask
        if inverter_names[inverter_data_select] == 'Solis':
            inverter_type_input = 1
        elif inverter_names[inverter_data_select] == 'GivEnergy':
            inverter_type_input = 0
        elif inverter_names[inverter_data_select] == 'SolarEdge':
            inverter_type_input = 2
        else:
            inverter_type_input = int(input("Which inverter is this data from: 1 = GivEnergy, 2 = Solis, 3 = SolarEdge"))-1

        # Get a list of all Excel files in the folder
        excel_files = glob.glob(bill_directory+'/*.xl*')

        # Define structure of each data set
        data_headers = [
                ['Solar Generation', 'Total Inverter Power(W)', 'Solar Production (W)'],
                ['Load Power', 'Total Consume Energy Power(W)', 'Consumption (W)'],
                ['Battery Power', 'Battery Power(W)', 'StoragePower.Power (W)'],
                ['Battery %', 'Battery SOC(%)', 'Battery Charge Level (%)'],
                ['Grid Power', 'Grid Total Active Power(W)', '']
            ]

        date_time_formats = ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S (UTC%z)","%m/%d/%Y %H:%M"]
        data_start_rows = [1, 8, 1] # define starting rows for each data set
        target_sheet_names = [0, 0, 0] # define sheet of each excel file that data will be pulled from
        inverter_battery_sign = [-1,1,1] # define battery power data as positive or negative based on inverter type
        data_start_row = data_start_rows[inverter_type_input] # assign the starting row
        target_sheet_name = target_sheet_names[inverter_type_input] # assign the target sheet name

        # create an empty list to store the data frames
        dfs = []

        # Loop through the list of Excel files and read each file into a dataframe
        for file in excel_files:
            dfs.append(pd.read_excel(file,skiprows=data_start_row-1,sheet_name=target_sheet_name))

        # Concatenate all DataFrames into a single DataFrame
        df = pd.concat(dfs, ignore_index=True)

        # Assign headers and date format based on inverter type input
        chosen_inverter_data_headers = [] # create an empty array for the headers
        inner_list_counter = 0
        for inner_list in data_headers:
            inner_list_counter = inner_list_counter+1

            # append the headers for each data point except for the SolarEdge's Grid Power reading
            if inner_list_counter < 5 or inverter_type_input != 2:
                chosen_inverter_data_headers.append(inner_list[inverter_type_input])

            # Add two separate data headers for SolarEdge's grid readings
            if inner_list_counter == 5 and inverter_type_input ==2:
                chosen_inverter_data_headers.append('Import (W)')
                chosen_inverter_data_headers.append('Export (W)')

        # set the appropriate date time format for the inverter
        date_time_format = date_time_formats[inverter_type_input]

        # Convert the 'Time' column to pandas datetime and average to nearest time interval
        df['Time'] = pd.to_datetime(df['Time'], format=date_time_format).dt.floor(t)

        # Remove the date
        df['Time'] = df['Time'].dt.time

        # Extract and process data values
        data_values = [df.groupby('Time')[header].mean() for header in chosen_inverter_data_headers]

        # divide battery SOC % values by 100 and multiply by battery capacity to go from % to kWh and other figures by 1000 to go from W to kW
        data_values = [values / 100 if i == 3 else values / 1000 for i, values in enumerate(data_values)]

        # for SolarEdge inverters, sum the 'import' and 'export' columns
        if inverter_type_input == 2:
            data_values[4] = data_values[4]+data_values[5]

        # find the average SOC at the start of each day
        average_starting_SOC = data_values[3][0]

        # Interpolate data to align with time intervals
        t = np.arange(len(data_values[0]))
        interpolated_values = [np.interp(np.linspace(0, len(values) - 1, len(t)), np.arange(len(values)), values)
                               for values in data_values]

        return interpolated_values[0], interpolated_values[1], interpolated_values[2]*inverter_battery_sign[inverter_type_input], interpolated_values[3], interpolated_values[4], average_starting_SOC, bill_directory