import sys
sys.path.append('/Users/pacopuig/Desktop/PROGRAMACION/aquacrop_cameras/aquacrop_wrapper/aquacrop')

from aquacrop.utils import prepare_weather, get_filepath

class WWeather:
    """Wrapper for the Weather class from AquaCrop package.
    """

    def __init__(self, weather_file_path, test_mode=False):
        self.weather_file_path = weather_file_path
        print(test_mode)
        if self.weather_file_path is None:
            raise ValueError("Weather file path is not provided")

        if (test_mode):
            self.weather_file_path = get_filepath(weather_file_path)

        self.weather = prepare_weather(
            self.weather_file_path
        )
