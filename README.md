# solar-consumer-tariff-advisor

Description
This project reads downloaded data from battery-connected SolarEdge, Solis, and GivEnergy inverters and recommends the optimal energy tariff and battery control scheme based on the energy consumption and solar generation. It requires daily energy inverter data in excel format, energy tariffs in excel format, and battery size and charge/discharge rates as variables. It outputs an energy profile chart for each energy tariff <> battery control scheme and estimate daily energy bills for each. 

Required libraries
* numpy
* pandas
* tabulate
* scipy
* seaborn
* matploylib

Usage
1. Download daily inverter reading files from either SolarEdge Monitoring, Solis Cloud, or GivEnergy cloud. Download as many days of data as necessary, these will be summarised into a single day that represents the average data point for the given daily time interval. If using SolarEdge monitoring, make sure you download as a .xls, or convert to an .xls. 
2. Save these files to a unique folder. Append the name of the brand to the folder name as follows: ‘[folder name]_[inverter name]’. For example: ‘my-energy-data_GivEnergy’. Change the variable ‘tariff_and_inverter_readings_path’ within main.py to the directory of the folder’s root folder. 
3. Set the following battery parameters by changing the relevant variable within main.py: capacity (in kWh), max state of charge (in %), min state of charge (in %), max charge rate (in kW), max discharge rate (in kW)
4. Create an excel file containing the energy tariffs you wish to include. Use the format included in the excel file in this project. The first import / export tariff pair should be the current import/export tariff. The program does not run any new battery control logic for this tariff pair. Save the file to the same root folder that you provided in step 2. 
5. Run main.py. Provide your folder selection when prompted. 
6. A table showing daily import and export energy bills will be printed to the terminal. The average daily solar generation and daily household consumption will also be printed to the terminal. A series of charts will be printed to the folder containing the inverter data. 

Roadmap
* Incorporate EV charger behaviour. Ask user for the EV charger’s max charge rate and the typical daily kWh required. For time of use tariffs, this consumption be disaggregated from the house’s demand and reassigned to charge during the relevant off-peak period. 
