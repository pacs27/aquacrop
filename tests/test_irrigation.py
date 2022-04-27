''' import unittest
import pandas as pd

from aquacrop.utils.data import get_filepath
from aquacrop.core import AquaCropModel
from aquacrop.utils.prepare_weather import prepare_weather
from aquacrop.entities.soil import SoilClass
from aquacrop.entities.crop import CropClass
from aquacrop.entities.inititalWaterContent import InitialWaterContent
from aquacrop.entities.irrigationManagement import IrrMngtClass


class TestIrrigation(unittest.TestCase):
    """
    Tests of different irrigation methodologies in AquaCrop.
    """

    _sim_start = "1982/05/01"
    _sim_end = "2018/10/30"

    weather_file_path = get_filepath("champion_climate.txt")

    _weather_data = prepare_weather(weather_file_path)

    _sandy_loam = SoilClass(soil_type="SandyLoam")
    _wheat = CropClass("Maize", planting_date="05/01")
    _initial_water_content = InitialWaterContent(value=["FC"])

    def test_rainfed_strategy(self):
        """
        Rainfed methodology
        """
        irrigation = IrrMngtClass(irrigation_method=0)

        model_os = AquaCropModel(
            sim_start_time=self._sim_start,
            sim_end_time=self._sim_end,
            weather_df=self._weather_data,
            soil=self._sandy_loam,
            crop=self._wheat,
            initial_water_content=self._initial_water_content,
            irrigation_management=irrigation,
        )
        # run model till termination
        model_os.run_model(till_termination=True)
        
        final_statistics = model_os.get_simulation_results().head(10)
        print(final_statistics)

        print(final_statistics)

        yied_1_result = 10.782165097906882
        yield1 = final_statistics["Yield (tonne/ha)"][0]

        yied_10_result = 9.905317889844312
        yield10 = final_statistics["Yield (tonne/ha)"][9]

        self.assertEqual(yield1, yied_1_result)
        self.assertEqual(yield10, yied_10_result)

    def test_threshold4_irrigate_strategy(self):
        """
        Threshold methodology
        """
        irrigation = IrrMngtClass(irrigation_method=1, SMT=[40, 60, 70, 30] * 4)

        model_os = AquaCropModel(
            sim_start_time=self._sim_start,
            sim_end_time=self._sim_end,
            weather_df=self._weather_data,
            soil=self._sandy_loam,
            crop=self._wheat,
            initial_water_content=self._initial_water_content,
            irrigation_management=irrigation,
        )
        # run model till termination
        model_os.run_model(till_termination=True)
        
        final_statistics = model_os.get_simulation_results().head(10)
        print(final_statistics)
        print(final_statistics)
        yied_1_result = 12.650076726957787
        yield1 = final_statistics["Yield (tonne/ha)"][0]

        yied_10_result = 13.974969216935104
        yield10 = final_statistics["Yield (tonne/ha)"][9]

        self.assertEqual(yield1, yied_1_result)
        self.assertEqual(yield10, yied_10_result)

    def test_interval_7days__strategy(self):
        """
        7 days interval methodology
        """

        irrigation = IrrMngtClass(irrigation_method=2, IrrInterval=7)

        model_os = AquaCropModel(
            sim_start_time=self._sim_start,
            sim_end_time=self._sim_end,
            weather_df=self._weather_data,
            soil=self._sandy_loam,
            crop=self._wheat,
            initial_water_content=self._initial_water_content,
            irrigation_management=irrigation,
        )
        # run model till termination
        model_os.run_model(till_termination=True)
        
        final_statistics = model_os.get_simulation_results().head(10)
        print(final_statistics)

        yield_1_result = 12.646543675646381
        yield1 = final_statistics["Yield (tonne/ha)"][0]

        yield_10_result = 14.018772249158092
        yield10 = final_statistics["Yield (tonne/ha)"][9]

        self.assertEqual(yield1, yield_1_result)
        self.assertEqual(yield10, yield_10_result)

    def test_predefined_schedule_strategy(self):
        """
        Predefined schedule methodology
        """
        irrigation_schedule_df = create_pandas_irrigation_schedule(
            self._sim_start, self._sim_end
        )
        # print(irrigationSchedule)
        irrigate_schedule = IrrMngtClass(irrigation_method=3, Schedule=irrigation_schedule_df)

        model_os = AquaCropModel(
            sim_start_time=self._sim_start,
            sim_end_time=self._sim_end,
            weather_df=self._weather_data,
            soil=self._sandy_loam,
            crop=self._wheat,
            initial_water_content=self._initial_water_content,
            irrigation_management=irrigate_schedule,
        )

        # run model till termination
        model_os.run_model(till_termination=True)
        
        final_statistics = model_os.get_simulation_results().head(10)
        print(final_statistics)

        yield_1_result = 12.128998898669153
        yield1 = final_statistics["Yield (tonne/ha)"][0]

        yield_10_result = 11.997890714696235
        yield10 = final_statistics["Yield (tonne/ha)"][9]

        self.assertEqual(yield1, yield_1_result)
        self.assertEqual(yield10, yield_10_result)

    def test_net_irrigation_strategy(self):
        """
        Net methodology
        """
        irrigation = IrrMngtClass(irrigation_method=4, NetIrrSMT=70)

        model_os = AquaCropModel(
            sim_start_time=self._sim_start,
            sim_end_time=self._sim_end,
            weather_df=self._weather_data,
            soil=self._sandy_loam,
            crop=self._wheat,
            initial_water_content=self._initial_water_content,
            irrigation_management=irrigation,
        )

        # run model till termination
        model_os.run_model(till_termination=True)
        
        final_statistics = model_os.get_simulation_results().head(10)
        print(final_statistics)

        yield_1_result = 12.657670494485089
        yield1 = final_statistics["Yield (tonne/ha)"][0]

        yield_10_result = 13.981859189056273
        yield10 = final_statistics["Yield (tonne/ha)"][9]

        self.assertEqual(yield1, yield_1_result)
        self.assertEqual(yield10, yield_10_result)


def create_pandas_irrigation_schedule(sim_start, sim_end):
    """
    This function create a irrigation schedule
    """
    all_days = pd.date_range(
        sim_start, sim_end
    )  # list of all dates in simulation period

    new_month = True
    dates = []
    # iterate through all simulation days
    for date in all_days:
        # check if new month
        if date.is_month_start:
            new_month = True

        if new_month:
            # check if tuesday (dayofweek=1)
            if date.dayofweek == 1:
                # save date
                dates.append(date)
                new_month = False
    depths = [25] * len(dates)  # depth of irrigation applied
    schedule = pd.DataFrame([dates, depths]).T  # create pandas DataFrame
    schedule.columns = ["Date", "Depth"]  # name columns

    return schedule


if __name__ == "__main__":
    unittest.main()
 '''