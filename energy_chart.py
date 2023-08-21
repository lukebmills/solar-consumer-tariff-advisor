import numpy as np
import matplotlib.pyplot as plt

def create_chart(s, h, t, b_arrays, g_arrays, SOC_arrays, chart_select, tariff_names, chart_save_path):

    SOC = SOC_arrays[chart_select]
    b = b_arrays[chart_select]
    g = g_arrays[chart_select]

    # Create the plot
    t = t/60 # convert t from minutes to hours
    fig, ax1 = plt.subplots(figsize=(10,6))

    ax1.plot(t, s, label='Solar Generation (s)', color = 'tab:orange')
    ax1.plot(t, h, label='House Power Draw (h)', color = 'black')
    ax1.plot(t, b, label='Battery charge / discharge (b)', color = 'tab:blue')
    ax1.plot(t, g, label='Grid load (g)', color = 'tab:grey')
    ax1.set_xlabel('Time (hours)')
    ax1.set_xlim(0,24)
    ax1.set_xticks(np.arange(0,24,4))
    ax1.set_ylabel('Power (kW)', color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.legend(loc='lower center')
    ax1.set_ylim(np.min([s,h,b,g])*1.3, np.max([s,h,b,g])*1.3)


    # Create a second y-axis (right-hand side)
    ax2 = ax1.twinx()
    ax2.plot(t, SOC, label='Battery SOC (SOC)', color='tab:green')
    ax2.set_ylabel('Battery SOC (kWh)', color='tab:green')
    ax2.set_ylim(0, max(SOC)*1.2)
    ax2.tick_params(axis='y', labelcolor='tab:green')
    ax2.legend(loc='upper right')

    # Remove the y-axis lines for the right-hand y-axis
    ax2.yaxis.grid(False)
    ax2.grid(False)  # No grid lines for the right y-axis

    # Title and grid
    plt.title('Power Generation, Consumption, and Battery Status')
    plt.grid(True)

    # Get the y-tick locations on the left-hand y-axis (ax1)
    yticks = ax1.get_yticks()

    # Plot horizontal lines at each y-tick position on the left-hand y-axis
    for ytick in yticks:
        ax1.axhline(ytick, color='grey', linestyle='--', alpha=0.5)

    # Title and grid
    plt.title('Power generation, consumption, and Battery state of charge (SOC) | ' + tariff_names[chart_select])
    plt.grid(True)

    # save the plot as a png
    plt.savefig(chart_save_path + tariff_names[chart_select] + '.png')
    # show the plot
    # plt.show()