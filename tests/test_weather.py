import unittest

from aquacrop_wrapper.weather_data.weather import Weather


class TestWeather(unittest.TestCase):
    def test_weather(self):
        """TODO: CREATE A REAL TEST. THIS IS JUST TO TRY THE CODE
        """
        weather = Weather(
            start_simulation_date="2018-01-01", end_simulation_date="2018-01-31"
        )
        lat_deg = 37.8916
        lon_deg = -4.7728
        altitude = 100
        forecast_with_et0 = weather.get_forecast_for_the_next_5_days(
            lat_degrees=lat_deg, lon_degrees=lon_deg, altitude=altitude
        )
        self.assertEqual(1, 1)
