import unittest

from aquacrop_wrapper.weather_data.weather import Weather
from aquacrop_wrapper.config import AQUACROP_DIRECTORY_PATH


import sys

sys.path.append(AQUACROP_DIRECTORY_PATH)

print(AQUACROP_DIRECTORY_PATH)

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent
from aquacrop.utils import prepare_weather, get_filepath


class TestAquacropWrapper(unittest.TestCase):
    """
    Simple test of AquacropModel
    """
    
    _weather_file_path = get_filepath("tunis_climate.txt")

    _weather_data = prepare_weather(_weather_file_path)

    _sandy_loam = Soil(soil_type="SandyLoam")
    _wheat = Crop("Maize", planting_date="10/01")
    _initial_water_content = InitialWaterContent(value=["FC"])
    _model_os = AquaCropModel(
        sim_start_time=f"{1979}/10/01",
        sim_end_time=f"{1980}/05/30",
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
        final_statistics = self._model_os.get_water_storage_chart(multiples_plots=True, show_chart=True, save_chart=False, save_path=None)
        print("done")
        
    def test_chart_water_flux(self):
        # final_statistics = self._model_os.get_water_flux_chart(single_plot="Infl", multiples_plots_joined=False, show_chart=True, save_chart=False, save_path=None)
        # final_statistics = self._model_os.get_crop_growth_chart(single_plot="canopy_cover", multiples_plots_joined=False, show_chart=True, save_chart=False, save_path=None)
        final_statistics = self._model_os.get_crop_growth_chart(multiples_plots_joined=True, show_chart=True, save_chart=False, save_path=None)

        
        print("done")




if __name__ == "__main__":
    unittest.main()