from tariff_extractor import EnergyTariff
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

tariffs = EnergyTariff.read_arrays_from_excel('2023-08-16 Energy tariffs.xlsx')

# for idx, tariff in enumerate(tariffs, start=1):
#     print(f"Tariff {idx} - Name: {tariff.name}, Values: {tariff.values}")


tariff_dataframes = []
for idx, tariff in enumerate(tariffs, start=1):
    df = pd.DataFrame({'Value': tariff.values})
    df.index.name = 'Hour'
    df.columns.name = tariff.name
    tariff_dataframes.append(df)

def tariff_chart(import_tariff_df,export_tariff_df):

    # Define the custom tick positions and labels
    custom_ticks = [0, 4, 8, 12, 16, 20, 24]
    custom_tick_labels = ["", "4 AM", "8 AM", "12 PM", "4 PM", "8 PM", ""]

    fig, ax = plt.subplots(1, 2, figsize=(10, 6))

    sns.lineplot(data=import_tariff_df, x="Hour", y="Value", color='green', ax=ax[0])
    ax[0].set_title("Import tariff")
    ax[0].set_ylim(0,0.5)
    ax[0].set_xlim(0, 24)
    ax[0].set_xticks(custom_ticks)
    ax[0].set_xticklabels(custom_tick_labels)
    ax[0].set_xlabel("")
    ax[0].set_ylabel("GBP per kWh")
    ax[0].set_aspect(15)

    sns.lineplot(data=export_tariff_df, x="Hour", y="Value", color='red', ax=ax[1])
    ax[1].set_title("Export tariff")
    ax[1].set_ylim(0, 0.5)
    ax[1].set_xlim(0, 24)
    ax[1].set_xticks(custom_ticks)
    ax[1].set_xticklabels(custom_tick_labels)
    ax[1].set_xlabel("")
    ax[1].set_ylabel("GBP per kWh")
    ax[1].set_aspect(15)

    fig.tight_layout()

    plt.savefig(os.getcwd() + '/'+ import_tariff_df.columns.name + export_tariff_df.columns.name + '.png')

tariff_chart(tariff_dataframes[0],tariff_dataframes[4])
tariff_chart(tariff_dataframes[1],tariff_dataframes[5])
tariff_chart(tariff_dataframes[2],tariff_dataframes[6])
tariff_chart(tariff_dataframes[3],tariff_dataframes[7])