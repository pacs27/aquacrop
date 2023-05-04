"""
This test is for bug testing
"""
import unittest

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, GroundWater
from aquacrop.utils import prepare_weather, get_filepath


class TestModelExceptions(unittest.TestCase):
    """
    Test of what happens if the model does not run.
    """

    _weather_file_path = get_filepath("tunis_climate.txt")

    _weather_data = prepare_weather(_weather_file_path)

    _sandy_loam = Soil(soil_type="SandyLoam")
    _wheat = Crop("Wheat", planting_date="10/01")
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

    def test_anything(self):
        """
        Test Crop Growth
        """
        crop_growth = self._model_os.get_crop_growth().head()

        gdd_4_expected = 22.5
        gdd_4_returned = crop_growth["gdd"][4]
        self.assertEqual(gdd_4_expected, gdd_4_returned)

        gd_cum_d_4_expected = 104
        gdd_4_cum_returned = crop_growth["gdd_cum"][4]
        self.assertEqual(gd_cum_d_4_expected, gdd_4_cum_returned)


if __name__ == "__main__":
    unittest.main()
