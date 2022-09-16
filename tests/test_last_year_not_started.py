"""
This test is for bug testing
"""
import unittest
import pandas as pd


from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement
from aquacrop.utils import prepare_weather, get_filepath


class TestLastYearNotStarted(unittest.TestCase):
    """
    Test what happend when last year in the simulation does not reach the planting date.
    """
    _weather_file_path = get_filepath("tunis_climate.txt")

    _weather_data = prepare_weather(_weather_file_path)

    _model_os = AquaCropModel(
                sim_start_time=f"{1983}/05/15", # test with leap year
                sim_end_time=f"{1984}/05/14",
                weather_df=_weather_data,
                soil=Soil(soil_type='SiltClayLoam'),
                crop=Crop('Wheat', planting_date='05/15'),
                initial_water_content=InitialWaterContent(),
                irrigation_management=IrrigationManagement(irrigation_method=1, SMT=[70] * 4)
            )
    _model_os.run_model(till_termination=True)
  
    def test_get_additional_information(self):
        """
        Tets if model is finished
        """
        additional_info = self._model_os.get_additional_information()
        
        model_is_finished = additional_info["has_model_finished"]
        
        self.assertEqual(model_is_finished, True)


if __name__ == "__main__":
    unittest.main()
