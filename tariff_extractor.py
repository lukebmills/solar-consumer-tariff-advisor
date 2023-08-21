import openpyxl

class EnergyTariff:
    def __init__(self, name="Default Tariff", values=None):
        self.name = name
        self.values = values if values is not None else []

    # ... Other methods here ...

    @classmethod
    def read_arrays_from_excel(cls, filename):
        tariff_instances = []

        try:
            wb = openpyxl.load_workbook(filename)

            for sheet in wb:
                for col in sheet.iter_cols(min_col=2, values_only=True):
                    name = col[0]
                    values = col[1:]

                    tariff_instance = cls(name, values)
                    tariff_instances.append(tariff_instance)

        except Exception as e:
            print("Error reading Excel file:", e)

        return tariff_instances
