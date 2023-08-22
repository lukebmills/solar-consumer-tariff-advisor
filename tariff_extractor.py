import openpyxl
import pandas as pd
import numpy as np

class EnergyTariff:
    def __init__(self, name="Default Tariff", values=None):
        self.name = name
        self.values = values if values is not None else []

    @classmethod
    def read_arrays_from_excel(cls, filename, t):
        tariff_dataframes = []

        try:
            wb = openpyxl.load_workbook(filename)

            for sheet in wb:
                for col in sheet.iter_cols(min_col=2, values_only=True):
                    name = col[0]
                    values = col[1:]
                    values = np.interp(np.linspace(0, len(values) - 1, len(t)), np.arange(len(values)), values)

                    df = pd.DataFrame({'Value': values})
                    df.index.name = 'Hour'
                    df.columns.name = name
                    tariff_dataframes.append(df)


        except Exception as e:
            print("Error reading Excel file:", e)


        return tariff_dataframes
