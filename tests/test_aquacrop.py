import unittest

from aquacrop_wrapper.weather_data.weather import Weather
from aquacrop_wrapper.config import AQUACROP_DIRECTORY_PATH

import matplotlib.pyplot as plt

import sys

sys.path.append(AQUACROP_DIRECTORY_PATH)

print(AQUACROP_DIRECTORY_PATH)

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement
from aquacrop.utils import prepare_weather, get_filepath


class TestAquacropWrapper(unittest.TestCase):
    """
    Simple test of AquacropModel
    """
   
    _weather_file_path = get_filepath("tunis_climate.txt")

    _weather_data = prepare_weather(_weather_file_path)

    _sandy_loam = Soil(soil_type="SandyLoam")
    _wheat = Crop("Wheat", planting_date="11/15")
    _initial_water_content = InitialWaterContent(value=["WP"])
    _model_os = AquaCropModel(
        sim_start_time=f"{1979}/11/15",
        sim_end_time=f"{1980}/08/30",
        weather_df=_weather_data,
        soil=_sandy_loam,
        crop=_wheat,
        initial_water_content=_initial_water_content,
    )
    _model_os.run_model(till_termination=True)

    
    def test_charts_water(self):
        """
        Test final statistics
        """
        pass
        # final_statistics = self._model_os.get_water_storage_chart(multiples_plots_joined=True, show_chart=True, save_chart=False, save_path=None)
        print("done")
        
    def test_chart_water_flux(self):
        pass
        # final_statistics = self._model_os.get_water_flux_chart(single_plot="Infl", multiples_plots_joined=False, show_chart=True, save_chart=False, save_path=None)
        # final_statistics = self._model_os.get_crop_growth_chart(single_plot="canopy_cover", multiples_plots_joined=False, show_chart=True, save_chart=False, save_path=None)
        # final_statistics = self._model_os.get_crop_growth_chart(multiples_plots_joined=True, show_chart=True, save_chart=False, save_path=None)
        # final_statistics = self._model_os.get_weather_chart( multiples_plots_joined=True, show_chart=True, save_chart=False, save_path=None)

        
        print("done")
        
    def test_compare_rainfed_and_irrigated(self):
        """
        Test final statistics
        """   """
        SOIL_MOISTURE_METHOD = 1
        irrigation = IrrigationManagement(irrigation_method=SOIL_MOISTURE_METHOD, SMT=[100]*4)
        
        model_os = AquaCropModel(
        sim_start_time=f"{1979}/11/15",
        sim_end_time=f"{1980}/08/30",
        weather_df=self._weather_data,
        soil=self._sandy_loam,
        crop=self._wheat,
        initial_water_content=self._initial_water_content,
        irrigation_management=irrigation
    )
        model_os.run_model(till_termination=True)
        
        canopy_cover_rainfed = self._model_os.get_crop_growth()["canopy_cover"]
        canopy_cover_irrigated = model_os.get_crop_growth()["canopy_cover"]
        irrigation = model_os.get_water_flux()["IrrDay"]
        
        fig, ax = plt.subplots()
        ax.plot(canopy_cover_rainfed, label="rainfed", linestyle="--", color="red")
        ax.plot(canopy_cover_irrigated, label="irrigated", linestyle="-", color="green")
        # ax.plot(irrigation, label="irrigation", linestyle="-.", color="blue")
        
        # max x axis value 150
        # ax.set_xlim(0, 150)
        ax.legend()
        
        self._model_os.get_water_flux_chart(multiples_plots_joined=True, show_chart=True, save_chart=False, save_path=None)
        

        # final_statistics = self._model_os.get_water_storage_chart(multiples_plots_joined=True, show_chart=True, save_chart=False, save_path=None)
        print("done") """




if __name__ == "__main__":
    unittest.main()