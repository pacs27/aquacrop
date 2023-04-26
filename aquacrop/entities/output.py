import pandas as pd
import numpy as np


class Output:
    """
    Class to hold output data

    During Simulation these are numpy arrays and are converted to pandas dataframes
    at the end of the simulation

    Atributes:
    
        water_flux (pandas.DataFrame, numpy.array): Daily water flux changes

        water_storage (pandas.DataFrame, numpy array): daily water content of each soil compartment

        crop_growth (pandas.DataFrame, numpy array): daily crop growth variables

        final_stats (pandas.DataFrame, numpy array): final stats at end of each season

    """

    def __init__(self, time_span, initial_th):

        water_storage_n_columns = 4 + len(initial_th) # 4 because time_step_counter, current_simulation_date, growing_season, dap
        self.water_storage = np.zeros((len(time_span), water_storage_n_columns)) 
        self.water_flux = np.zeros((len(time_span), 17)) # 17 columns
        self.crop_growth = np.zeros((len(time_span), 14)) # 14 columns
        
        self.final_stats = pd.DataFrame(
            columns=[
                "Season",
                "crop Type",
                "Harvest Date (YYYY/MM/DD)",
                "Harvest Date (Step)",
                "Yield (tonne/ha)",
                "Seasonal irrigation (mm)", # 1mm = 10 m3/ha
            ]
        )