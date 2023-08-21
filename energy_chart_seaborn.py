import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import seaborn.objects as so
from scipy.ndimage.filters import gaussian_filter1d
# import scipy.stats as stats
# from scipy.interpolate import make_interp_spline, BSpline


def create_chart(s, h, t, b_arrays, g_arrays, SOC_arrays, chart_select, tariff_names, chart_save_path):
    
    # Convert t from minutes to hours
    t = t / 60

    h = gaussian_filter1d(h,sigma=2)
    s = gaussian_filter1d(s,sigma=2)
    b_arrays = gaussian_filter1d(b_arrays,sigma=2)
    g_arrays = gaussian_filter1d(g_arrays,sigma=2)

    power = np.append(np.append(np.append(s,-h),-b_arrays[chart_select]),g_arrays[chart_select])
    power_name = np.append(np.append(np.append(np.full(len(s),'Solar generation'),np.full(len(h),'House demand')),np.full(len(b_arrays[1]),'Battery power')),np.full(len(g_arrays[0]),'Grid load'))
    power_t = np.append(np.append(np.append(t,t),t),t)


    power_df = {
        "Time": power_t, 
        "Power (kW)": power,
        "Type": power_name
        }
    
    power_df = pd.DataFrame(power_df)


    SOC_df = {
        "Time": t,
        "Battery SOC (kWh)": SOC_arrays[chart_select]
        }
    
    # Create the plot
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))
    
    sns.lineplot(data=power_df, x="Time", y="Power (kW)", hue = "Type", ax=ax[0])
    sns.lineplot(data=SOC_df, x="Time", y="Battery SOC (kWh)", color='black', ax=ax[1])

    power_df_solar = power_df[power_df["Type"] == 'Solar generation']
    power_df_battery = power_df[power_df["Type"] == 'Battery power']
    power_df_load = power_df[power_df["Type"] == 'House demand']
    power_df_grid = power_df[power_df["Type"] == 'Grid load']
    ax[0].fill_between(data=power_df_solar,x="Time",y1="Power (kW)", y2=0,color='blue',alpha=0.3)
    ax[0].fill_between(data=power_df_battery,x="Time",y1="Power (kW)", y2=0,color='green',alpha=0.3)
    # ax[0].fill_between(data=power_df_load,x="Time",y1="Power (kW)", y2=0,color='orange',alpha=0.3)
    ax[0].fill_between(data=power_df_grid,x="Time",y1="Power (kW)", y2=0,color='red',alpha=0.3)

    ax[1].set_ylim(0)  # This sets the lower limit to 0
    ax[1].fill_between(data=SOC_df,x="Time",y1="Battery SOC (kWh)", y2=0,color='black',alpha=0.3)

    # Set titles for subplots
    ax[0].set_title("Power consumption")
    ax[1].set_title("Battery state of charge")


    # Show the plot (optional)
    fig.tight_layout()
    # plt.show()
    plt.savefig(chart_save_path + tariff_names[chart_select] + '.png')


