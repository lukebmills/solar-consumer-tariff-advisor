import numpy as np

# takes time array and returns energy tariffs and battery control mechanisms for each tariff

def main(t, readings_per_hour): 
    
    # set tariff names
    tariff_names = ["Price cap and SEG", "Flux"]

    
    # first tariff pair is a fixed import of 29p and fixed export of 15p (for solar only)
    i_1 = np.full(len(t),0.29)
    e_1 = np.full(len(t),0.15)

    # second tariff pair is variable
    i_2 = np.zeros_like(t,dtype=float)
    e_2 = np.zeros_like(t,dtype=float)
    for i in range (1, len(t)):
        if i >= 2 * readings_per_hour and i < 5 * readings_per_hour:
            i_2[i] = 0.1854
            e_2[i] = 0.0754
        elif i >= 16 * readings_per_hour and i < 19 * readings_per_hour:
            i_2[i] = 0.4326
            e_2[i] = 0.3226
        else:
            i_2[i] = 0.309
            e_2[i] = 0.199
    # interpolate the tariff pairs to ensure length matches the t variable
    i_2 = np.interp(np.linspace(0, len(i_2)-1, len(t)), np.arange(len(i_2)), i_2)
    e_2 = np.interp(np.linspace(0, len(e_2)-1, len(t)), np.arange(len(e_2)), e_2)

    
    
    return tariff_names, 