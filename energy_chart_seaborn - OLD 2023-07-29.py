import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn.objects as so

def create_chart(s, h, t, b_arrays, g_arrays, SOC_arrays, tariff_names, chart_save_path):
    SOC_0 = SOC_arrays[0]
    b_0 = b_arrays[0]
    g_0 = g_arrays[0]

    SOC_1 = SOC_arrays[1]
    b_1 = b_arrays[1]
    g_1 = g_arrays[1]

    # Convert t from minutes to hours
    t = t / 60

    # Set Seaborn style
    sns.set(style="whitegrid", palette="tab10")

    # Create the plot
    fig, axs = plt.subplots(figsize=(10, 6))

    # Plot using Seaborn's lineplot
    sns.lineplot(x=t, y=s, label='Solar Generation (s)', ax=axs[0])
    sns.lineplot(x=t, y=h, label='House Power Draw (h)', ax=axs[0])
    sns.lineplot(x=t, y=b_1, label='Battery charge / discharge (b)', ax=axs[0])
    sns.lineplot(x=t, y=g_1, label='Grid load (g)', ax=ax[0])

    axs[0].set_xlabel('Time (hours)')
    axs[0].set_xlim(0, 24)
    axs[0].set_xticks(np.arange(0, 24, 4))
    axs[0].set_ylabel('Power (kW)')
    axs[0].set_ylim(np.min([s, h, b, g]) * 1.3, np.max([s, h, b, g]) * 1.3)
    axs[0].legend(loc='lower center')

    # Create a second y-axis (right-hand side)
    axs[1] = axs[0].twinx()

    # Plot using Seaborn's lineplot
    sns.lineplot(x=t, y=SOC_1, label='Battery SOC (SOC)', color='tab:green', ax=ax[1])

    axs[1].set_ylabel('Battery SOC (kWh)', color='tab:green')
    axs[1].set_ylim(0, max(SOC) * 1.2)
    axs[1].legend(loc='upper right')

    # Remove the y-axis lines for the right-hand y-axis
    axs[1].yaxis.grid(False)
    axs[1].grid(False)  # No grid lines for the right y-axis

    # Title and grid
    plt.title('Power Generation, Consumption, and Battery Status')

    # Get the y-tick locations on the left-hand y-axis (ax1)
    yticks = axs[0].get_yticks()

    # Plot horizontal lines at each y-tick position on the left-hand y-axis
    for ytick in yticks:
        axs[0].axhline(ytick, color='grey', linestyle='--', alpha=0.5)

    # Title and grid
    # plt.title('Power generation, consumption, and Battery state of charge (SOC) | ' + tariff_names[chart_select])

    # Save the plot as a png using Seaborn's savefig method (you can use any file extension you want)
    # plt.savefig(chart_save_path + tariff_names[chart_select] + '.png')

    # Show the plot (optional)
    plt.show()

# Example usage:
# create_chart(s, h, t, b_arrays, g_arrays, SOC_arrays, chart_select, tariff_names, chart_save_path)
