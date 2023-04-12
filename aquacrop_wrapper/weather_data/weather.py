import sys
import os

import pandas as pd

try:
    from aquacrop_wrapper.weather_data.weather_ria_stations import WeatherRIAStations
except ImportError:
    from .weather_ria_stations import WeatherRIAStations


path_to_utils = os.getenv("OWN_UTILS_PATH")
sys.path.append(path_to_utils)

from utils.weather.apis.open_weather_api import OpenWeather
from utils.weather.convert import kelvin2celsius


class Weather:
    def __init__(self, start_simulation_date=None, end_simulation_date=None):
        self.weather_ria_stations = WeatherRIAStations()
        self.start_simulation_date = start_simulation_date
        self.end_simulation_date = end_simulation_date

    def get_weather_data_using_ria(
        self,
        start_year,
        end_year,
        station_id,
        province_id,
        complete_data,
        complete_type,
        complete_values_method,
    ):
        """_summary_

        Args:
            station_id (_type_): _description_
            province_id (_type_): _description_
            complete_data (_type_): _description_
            complete_type (_type_): _description_

        Returns:
            _type_: _description_
        """

        # Get weather data from RIA
        weather_df = self.weather_ria_stations.get_weather_df(
            start_simulation_date=self.start_simulation_date,
            end_simulation_date=self.end_simulation_date,
            start_year=start_year,
            end_year=end_year,
            station_id=station_id,
            province_id=province_id,
            complete_data=complete_data,
            complete_type=complete_type,
            complete_values_method=complete_values_method,
        )

        weather_aquacrop = (
            self.weather_ria_stations.transform_dataframe_into_aquacrop_format(
                weather_df=weather_df
            )
        )
        
        # Date to Timestamp
        weather_aquacrop["Date"] = pd.to_datetime(weather_aquacrop["Date"])
        
        

        weather_aquacrop = WeatherAcuacropDataframe(aquacrop_dataframe=weather_aquacrop)

        return weather_aquacrop.getDataframe()

    def get_forecast_for_the_next_5_days(self, lat_degrees, lon_degrees, altitude=0):
        open_weather_api = OpenWeather()

        forecast_with_et0 = (
            open_weather_api.get_forecast_on_geographic_coordinates_with_et0(
                lat_degrees=lat_degrees, lon_degrees=lon_degrees, altitude=altitude
            )
        )

        # Create Date column with format YYYY-MM-D usinf julian day

        forecast_with_et0 = forecast_with_et0[
            ["Date", "t_max_k", "t_min_k", "rain_3h", "et0"]
        ]

        forecast_with_et0 = forecast_with_et0.rename(
            columns={
                "t_max_k": "MaxTemp",
                "t_min_k": "MinTemp",
                "rain_3h": "Precipitation",
                "et0": "ReferenceET",
            }
        )

        forecast_with_et0["MaxTemp"] = kelvin2celsius(forecast_with_et0["MaxTemp"])
        forecast_with_et0["MinTemp"] = kelvin2celsius(forecast_with_et0["MinTemp"])
        
          # Date to Timestamp
        forecast_with_et0["Date"] = pd.to_datetime(forecast_with_et0["Date"])
        
        

        
        
        forecast_with_et0 = WeatherAcuacropDataframe(aquacrop_dataframe=forecast_with_et0)
        

        return forecast_with_et0.getDataframe()
    


class WeatherAcuacropDataframe:
    def __init__(self, aquacrop_dataframe) -> None:
        self.check_datframe(aquacrop_dataframe)

        self.aquacrop_dataframe = aquacrop_dataframe

    @staticmethod
    def check_datframe(aquacrop_dataframe):
        """Check if the dataframe has the correct columns

        Note: The dataframe must have the following columns:
        ['Date', 'MinTemp', 'MaxTemp', 'Precipitation', 'ReferenceET']

        where:
            Date: Date in format YYYY-MM-DD
            MinTemp: Minimum temperature in degrees Celsius
            MaxTemp: Maximum temperature in degrees Celsius
            Precipitation: Precipitation in mm
            ReferenceET: Reference evapotranspiration in mm/day

        Args:
            aquacrop_dataframe (_type_): _description_

        Raises:
            Exception: _description_
        """
        # check if the dataframe has the correct columns
        correct_columns = [
            "Date",
            "MinTemp",
            "MaxTemp",
            "Precipitation",
            "ReferenceET",
        ]

        if not all(elem in aquacrop_dataframe.columns for elem in correct_columns):
            raise Exception(
                f"The dataframe must have the following columns: {correct_columns}"
            )
            
        # Check if Date is in Timestamp format
        if not isinstance(aquacrop_dataframe.iloc[0]['Date'], pd.Timestamp):
            raise Exception(
                f"The Date column must be in Timestamp format"
            )

    def getDataframe(self):
        return self.aquacrop_dataframe
    
  