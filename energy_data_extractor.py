import pandas as pd
import os
import numpy as np
import glob

def extract_s_and_h(t):
    s_values = []
    h_values = []
    average_starting_SOC = 0.00

    # find folders in current folder
    current_directory = os.getcwd()
    folders_list = [folder for folder in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, folder))]

    inverter_names = [folder.split('_')[-1] for folder in folders_list]

    # ask customer to select which set of inverter data to analyse
    inverter_data_select_input = "Choose which inverter data set to analyse: "
    for i in range(0,len(folders_list)):
        inverter_data_select_input = inverter_data_select_input + str(i+1) + " = " + folders_list[i] + ", "

    # ask which inverter data set to analyse
    inverter_data_select = int(input(inverter_data_select_input))-1
    bill_directory = current_directory+"/"+folders_list[inverter_data_select]+'/*.xl*'
    save_path = current_directory+"/"+folders_list[inverter_data_select]+'/'

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
    excel_files = glob.glob(bill_directory)

    # create an empty list to store the data frames
    dfs = []

    # define structure of different data sets
    solar_generation_data_headers = ['Solar Generation','Total Inverter Power(W)','Solar Production (W)'] # define headers for solar generation column
    house_load_data_headers = ['Load Power','Total Consume Energy Power(W)','Consumption (W)'] # define headers for house load column
    battery_SOC_data_headers = ['Battery %','Battery SOC(%)','Battery Charge Level (%)'] # define headers for battery SOC column
    batter_power_data_headers = ['Battery Power','Battery Power(W)','StoragePower.Power (W)']
    grid_power_data_headers = ['Grid Power', 'Grid Total Active Power(W)', ''] #need to fix solaredge grid power. currently has export and import as separate data poitns
    time_data_headers = ['Time','Time','Time'] # define headers for time column
    date_time_formats = ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S (UTC%z)","%m/%d/%Y %H:%M"]
    data_start_rows = [1, 8, 1] # define starting rows for each data set
    target_sheet_names = [0, 0, 0] # define order of sheet data to be pulled from
    inverter_battery_sign = [-1,1,1] # define battery power data as positive or negative based on inverter type

    data_start_row = data_start_rows[inverter_type_input]
    target_sheet_name = target_sheet_names[inverter_type_input]

    # Loop through the list of Excel files and read each file into a dataframe
    for file in excel_files:
        dfs.append(pd.read_excel(file,skiprows=data_start_row-1,sheet_name=target_sheet_name))

    battery_SOC_data_header = battery_SOC_data_headers[inverter_type_input]
    battery_power_data_header = batter_power_data_headers[inverter_type_input]
    grid_power_data_header = grid_power_data_headers[inverter_type_input]
    solar_generation_data_header = solar_generation_data_headers[inverter_type_input]
    house_load_data_header = house_load_data_headers[inverter_type_input]
    date_time_format = date_time_formats[inverter_type_input]

    # Concatenate all DataFrames into a single DataFrame
    df = pd.concat(dfs, ignore_index=True)
    # df['Time'] = pd.to_datetime(df['Time'], format=date_time_format).dt.floor('5T')

    # Convert the 'Time' column to pandas datetime and average to nearest 5min
    df['Time'] = pd.to_datetime(df['Time'], format=date_time_format).dt.floor('20T')

    # # Set the 'Time' column as the DataFrame's index
    # df.set_index('Time', inplace=True)
    
    # Remove the date
    df['Time'] = df['Time'].dt.time

    # find the mean solar generation, house draw, and battery SOC for each 5 min interval
    s_values = df.groupby('Time')[solar_generation_data_header].mean() / 1000 # change from W to kW
    h_values = df.groupby('Time')[house_load_data_header].mean() / 1000 # change from W to kW
    SOC_values = df.groupby('Time')[battery_SOC_data_header].mean() / 100 # change from % to decimal
    b_values = df.groupby('Time')[battery_power_data_header].mean() * inverter_battery_sign[inverter_type_input] / 1000 # change from W to kW and interpret data as positive or negative based on inverter type
    g_values = df.groupby('Time')[grid_power_data_header].mean() / 1000 # change from W to kW

    # find the average SOC at the start of each day
    average_starting_SOC = SOC_values[0]

    # interpolate to ensure there are sufficient values to match the time data
    s_values = np.interp(np.linspace(0, len(s_values)-1, len(t)), np.arange(len(s_values)), s_values)
    h_values = np.interp(np.linspace(0, len(h_values)-1, len(t)), np.arange(len(h_values)), h_values)
    b_values = np.interp(np.linspace(0, len(b_values)-1, len(t)), np.arange(len(b_values)), b_values)
    SOC_values = np.interp(np.linspace(0, len(SOC_values)-1, len(t)), np.arange(len(SOC_values)), SOC_values)
    g_values = np.interp(np.linspace(0, len(g_values)-1, len(t)), np.arange(len(g_values)), g_values)

    return s_values, h_values, b_values, SOC_values, g_values, average_starting_SOC, save_path