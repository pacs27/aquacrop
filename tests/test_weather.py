import unittest

from aquacrop_wrapper.weather_data.weather import Weather




class TestWeather(unittest.TestCase):
    
    # forecast
    start_simulation_date="2023/01/01"
    end_simulation_date="2023/12/31"
    lat_deg = 37.8916
    lon_deg = -4.7728
    altitude = 100
    
    # historic
    start_year=2015
    end_year=2019                             
    station_id="2"
    province_id=14
    complete_data=True,
    complete_type="last_n_years"
    complete_values_method="means"
    
    def weather_forecast(self):
        
        """TODO: CREATE A REAL TEST. THIS IS JUST TO TRY THE CODE
        """
        weather = Weather(
           
            
        )
       
        forecast_with_et0 = weather.get_forecast_for_the_next_5_days(
            lat_degrees=self.lat_deg, lon_degrees=self.lon_deg, altitude=self.altitude
        )
        
        return forecast_with_et0
        
    
        
    def weather_ria(self):
        
       
        
        weather = Weather(
            start_simulation_date=self.start_simulation_date, end_simulation_date=self.end_simulation_date
        )
        
        
        ria_weather = weather.get_weather_data_using_ria(
            start_year=self.start_year,
            end_year=self.end_year,
            station_id=self.station_id,
            province_id=self.province_id,
            complete_data=self.complete_data,
            complete_type=self.complete_type,
            complete_values_method=self.complete_values_method
        )
        
        return ria_weather
        
        
    def test_historic_and_forescat_weather(self):
        """This test doesnt do anything, just to try the code
        
        The test take the historic weather from RIA and the forecast weather from OpenWeather
        and merge them in a single dataframe
        
        Also if the simulation date is in the future, the forecast weather is used to fill the missing values
        """
        
        historical_weather = self.weather_ria()
        forecast_weather = self.weather_forecast()
        
        historical_weather.set_index("Date", inplace=True)
        forecast_weather.set_index("Date", inplace=True)
        
        historical_weather.update(forecast_weather)
        
        historical_weather.reset_index(inplace=True)
        
        
        
        
        print(historical_weather)
