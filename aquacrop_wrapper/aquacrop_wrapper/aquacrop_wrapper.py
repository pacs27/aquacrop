# import sys
# sys.path.append('.\aquacrop\aquacrop')

from aquacrop import (
        AquaCropModel,
        Soil,
        Crop,
        InitialWaterContent,
        IrrigationManagement,
    )
from aquacrop.utils import prepare_weather, get_filepath


try:
    from constants import AquacropConstants
except ImportError:
    from ..constants import AquacropConstants
   


class WCrop:
    def __init__(self, crop_type: AquacropConstants.TYPES_OF_CROPS, planting_date):
        if (crop_type not in AquacropConstants.TYPES_OF_CROPS):
            raise ValueError("""Invalid crop type, valid values are: Barley, Cotton, 
                             DryBean, Maize, PaddyRice, Potato, Quinoa, Sorghum, 
                             Soybean, SugarBeet, SugarCane, Sunflower, Tomato, Wheat""")
        self.crop_type = crop_type
        self.crop = Crop(c_name=self.crop_type, planting_date=planting_date)


class WSoil:
    def __init__(self, soil_type: AquacropConstants.TYPES_OF_SOILS):
        if (soil_type not in AquacropConstants.TYPES_OF_SOILS):
            raise ValueError("""Invalid soil type, valid values are: Clay, ClayLoam, 
                             Loam, LoamySand, Sand, SandyClay, SandyClayLoam, SandyLoam, 
                             Silt, SiltClayLoam, SiltLoam, SiltClay, Paddy, ac_TunisLocal""")
        self.soil_type = soil_type
        self.soil = Soil(soil_type=soil_type)


class WIrrigation:
    def __init__(self, irrigation_method: AquacropConstants.IRRIGATION_METHODS, initial_water_content: AquacropConstants.INITIAL_WATER_CONTENT, soil_moisture_targets):
        if (irrigation_method not in AquacropConstants.IRRIGATION_METHODS.keys()):
            raise ValueError("""Invalid irrigation method, valid values are: rainfed, 
                             soil_moisture_targets, set_time_interval,
                             predifined_schedule, net_irrigation, constant_depth""")
        
        if (initial_water_content not in AquacropConstants.INITIAL_WATER_CONTENT):
            raise ValueError("""Invalid initial water content, valid values are: WP, FC, SAT""")
        
        self.initial_water_content = InitialWaterContent(value=[initial_water_content])

        self.irrigation_method = AquacropConstants.IRRIGATION_METHODS[irrigation_method]

        print(self.irrigation_method)
        self.irrigation_management = IrrigationManagement(
            irrigation_method=self.irrigation_method
        )

    def getIrrigation(self):
        return (self.irrigation_management, self.initial_water_content)


class WWeather:
    def __init__(self, weather_file_path, test_mode=False):
        self.weather_file_path = weather_file_path
        print(test_mode)
        if self.weather_file_path is None:
            raise ValueError("Weather file path is not provided")
        
        if(test_mode):
            self.weather_file_path = get_filepath(weather_file_path)
            
        self.weather = prepare_weather(
            self.weather_file_path
        )


class AquacropWrapper:

    def __init__(self,  sim_start, sim_end, weather: WWeather, soil: WSoil, crop: WCrop, irrigation: WIrrigation):
        self.sim_start = sim_start
        self.sim_end = sim_end
        self.weather = weather
        self.soil = soil
        self.crop = crop
        self.irrigation = irrigation
        
    def run(self):
        model = AquaCropModel(
            weather_df=self.weather.weather,
            crop=self.crop.crop,
            soil=self.soil.soil,
            irrigation_management=self.irrigation.irrigation_management,
            initial_water_content=self.irrigation.initial_water_content,
            sim_start_time=self.sim_start,
            sim_end_time=self.sim_end,
        )
        model.run_model(till_termination=True)
        final_statistics = model.get_simulation_results().head(10)
    
        return final_statistics
