import unittest

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from aquacrop.utils.prepare_weather import prepare_weather
from aquacrop.utils.data import get_filepath
from aquacrop.core import AquaCropModel
from aquacrop.entities.soil import Soil
from aquacrop.entities.crop import Crop
from aquacrop.entities.inititalWaterContent import InitialWaterContent
from aquacrop.entities.groundWater import GroundWater


"""
Simple test of AquacropModel
"""
depths = np.linspace(1.0, 5.0)

results_df = pd.DataFrame()
weather_file_path = get_filepath("tunis_climate.txt")

weather_data = prepare_weather(weather_file_path)
weather_data2 = weather_data.copy()
weather_data2["Precipitation"] = (
    weather_data2["Precipitation"] / 10
)  # too much rain for ground water effect in the original

_sandy_loam = Soil(soil_type="SandyLoam")
_wheat = Crop("Wheat", planting_date="10/01")
_initial_water_content = InitialWaterContent(value=["FC"])
for d in depths:

    _model_os = AquaCropModel(
        sim_start_time=f"{1979}/10/01",
        sim_end_time=f"{1980}/05/30",
        weather_df=weather_data2,
        soil=_sandy_loam,
        crop=_wheat,
        initial_water_content=_initial_water_content,
        groundwater=GroundWater(water_table="Y", dates=[f"{1979}/10/01"], values=[d]),
    )
    _model_os.run_model(till_termination=True)
    _model_os.get_simulation_results()['water_table'] = d

    results_df = pd.concat([results_df, _model_os.get_simulation_results()])
    results_water_df = pd.concat([results_df, _model_os.get_water_storage()])
    results_flux_df = pd.concat([results_df, _model_os.get_water_flux()])
    results_crop_growth_df = pd.concat([results_df, _model_os.get_crop_growth()])


plt.plot(results_df['water_table'], results_df['Yield (tonne/ha)'])
plt.xlabel('water_table')
plt.ylabel('yield')
plt.show()


# """
# # Simple test of AquacropModel
# # """
# class TestIrrigation(unittest.TestCase):
#     def test_groundwater(self):
#         weather_file_path = get_filepath("tunis_climate.txt")

#         weather_data = prepare_weather(weather_file_path)
#         weather_data2 = weather_data.copy()
#         weather_data2["Precipitation"] = (
#             weather_data2["Precipitation"] / 10
#         )  # too much rain for ground water effect in the original

#         _sandy_loam = Soil(soil_type="SandyLoam")
#         _wheat = Crop("Wheat", planting_date="10/01")
#         _initial_water_content = InitialWaterContent(value=["FC"])

#         _model_os = AquaCropModel(
#             sim_start_time=f"{1979}/10/01",
#             sim_end_time=f"{1980}/05/30",
#             weather_df=weather_data2,
#             soil=_sandy_loam,
#             crop=_wheat,
#             initial_water_content=_initial_water_content,
#             groundwater=GroundWater(water_table="Y", dates=[f"{1979}/10/01"], values=[2.66]),
#         )
#         pd.set_option('display.max_columns', None)
#         _model_os.run_model(till_termination=True)
#         # results= _model_os.get_crop_growth().to_csv("2.67.csv")
#         # print(results)
#         results= _model_os.get_simulation_results()["Yield (tonne/ha)"]
#         print("results = ",results)

#         x = 0


# if __name__ == "__main__":
#     unittest.main()
