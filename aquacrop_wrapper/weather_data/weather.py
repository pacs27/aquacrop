
try:
    from weather_ria_stations import WeatherRIAStations
except ImportError:
    from .weather_ria_stations import WeatherRIAStations


class Weather:

    def __init__(self, start_simulation_date, end_simulation_date):
        self.weather_ria_stations = WeatherRIAStations()
        self.start_simulation_date = start_simulation_date
        self.end_simulation_date = end_simulation_date

    def get_weather_data_using_ria(self, start_year, end_year, station_id,
                                   province_id, complete_data, complete_type,
                                   complete_values_method):
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
            complete_values_method=complete_values_method
        )

        return weather_df
