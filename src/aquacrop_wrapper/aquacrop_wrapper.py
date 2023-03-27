
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


class Crop:
    def __init__(self, crop_type: AquacropConstants.TYPES_OF_CROPS, planting_date):
        if (crop_type not in AquacropConstants.TYPES_OF_CROPS):
            raise ValueError("""Invalid crop type, valid values are: Barley, Cotton, 
                             DryBean, Maize, PaddyRice, Potato, Quinoa, Sorghum, 
                             Soybean, SugarBeet, SugarCane, Sunflower, Tomato, Wheat""")
        self.crop_type = AquacropConstants.TYPES_OF_CROPS[crop_type]
        self.crop = Crop(crop_type=crop_type, planting_date=planting_date)


class Soil:
    def __init__(self, soil_type: AquacropConstants.TYPES_OF_SOILS):
        if (soil_type not in AquacropConstants.TYPES_OF_SOILS):
            raise ValueError("""Invalid soil type, valid values are: Clay, ClayLoam, 
                             Loam, LoamySand, Sand, SandyClay, SandyClayLoam, SandyLoam, 
                             Silt, SiltClayLoam, SiltLoam, SiltClay, Paddy, ac_TunisLocal""")
        self.soil_type = AquacropConstants.TYPES_OF_SOILS[soil_type]
        self.soil = Soil(soil_type=soil_type)


class Irrigation:
    def __init__(self, irrigation_method: AquacropConstants.IRRIGATION_METHODS):
        if (irrigation_method not in AquacropConstants.IRRIGATION_METHODS.keys()):
            raise ValueError("""Invalid irrigation method, valid values are: rainfed, 
                             soil_moisture_targets, set_time_interval,
                             predifined_schedule, net_irrigation, constant_depth""")

        self.irrigation_method = AquacropConstants.IRRIGATION_METHODS[irrigation_method]

        self.irrigation = IrrigationManagement(
            method=irrigation_method
        )

    def getIrrigation(self):
        return self.irrigation


class Weather:
    def __init__(self, weather_file_path):
        self.weather_file_path = weather_file_path
        self.weather = prepare_weather(
            weather_file_path
        )


class AquacropWrapper:

    def __init__(self,  sim_start, _sim_end, weather: Weather, soil: Soil, crop: Crop, irrigation: Irrigation):
        self.sim_start = sim_start
        self.sim_end = _sim_end
        self.weather = weather
        self.soil = soil
        self.crop = crop
        self.irrigation = irrigation
        
    def run(self):
        model = AquaCropModel(
            weather=self.weather.weather,
            crop=self.crop.crop,
            soil=self.soil.soil,
            irrigation=self.irrigation.irrigation,
            sim_start=self.sim_start,
            sim_end=self.sim_end,
        )
        model.run()
        return model
