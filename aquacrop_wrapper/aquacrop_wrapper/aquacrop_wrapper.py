
from typing import TYPE_CHECKING
import sys
import datetime 

try:
    from aquacrop_wrapper.config import AQUACROP_DIRECTORY_PATH
except ImportError:
    from config import AQUACROP_DIRECTORY_PATH
    
sys.path.append(
    AQUACROP_DIRECTORY_PATH
)

from aquacrop import (
    AquaCropModel,
)
if TYPE_CHECKING:
    from .crop_wrapper import WCrop
    from .irrigation_wrapper import WIrrigation
    from .soil_wrapper import WSoil
    from .weather_wrapper import WWeather
    from .aquacrop_variables_controller import AquacropVariablesController


try:
    from aquacrop_wrapper.json_functions import JSONFunctions
except ImportError:
    from .json_functions import JSONFunctions


class AquacropWrapper:
    """Wrapper for the AquaCropModel class from aquacrop package.
        Args:
            sim_start: Start date of the simulation in the format of YYYY-MM-DD
            sim_end: End date of the simulation in the format of YYYY-MM-DD
            weather: WWeather object that contains the weather data
            soil: WSoil object that contains the soil data
            crop: WCrop object that contains the crop data
            irrigation: WIrrigation object that contains the irrigation data
        Methods:
            run: Runs the AquaCrop model and returns the final statistics

        TODO: RUN UNTIL THE CURRENT DATE, UPDATE THE PARAMETERS AND CONTINUE THE SIMULATION

    """

    def __init__(self,  sim_start, sim_end, weather, soil: "WSoil", crop: "WCrop", irrigation: "WIrrigation"):
        self.sim_start = sim_start
        self.sim_end = sim_end
        self.weather = weather
        self.soil = soil
        self.crop = crop
        self.irrigation = irrigation

    def run(self, aquacrop_variables_controller: "AquacropVariablesController"):
        """Runs the AquaCrop model and returns the final statistics

        Returns:
            _type_: _description_
        """
        self.model = AquaCropModel(
            weather_df=self.weather,
            crop=self.crop.crop,
            soil=self.soil.soil,
            irrigation_management=self.irrigation.irrigation_management,
            initial_water_content=self.irrigation.initial_water_content,
            sim_start_time=self.sim_start,
            sim_end_time=self.sim_end,
        )
        self.model.run_model(till_termination=True,
                             controlled_variables_func=aquacrop_variables_controller.variables_controller_interface)

        additional_information = self.model.get_additional_information()
        return additional_information
    
    def get_simulation_results(self):
        return self.model.get_simulation_results()
    def show_charts(self):
        self.model.get_crop_growth_chart(multiples_plots_joined=True, show_chart=True)
        self.model.get_water_storage_chart(multiples_plots_joined=True, show_chart=True)
        self.model.get_water_flux_chart(multiples_plots_joined=True, show_chart=True)
        self.model.get_weather_chart(multiples_plots_joined=True, show_chart=True)
        

    def save_outputs(self,simulation_id, folder_path):
        simulation_results = self.model.get_simulation_results()
        water_storage = self.model.get_water_storage()
        water_flux = self.model.get_water_flux()
        crop_growth = self.model.get_crop_growth()
        additional_information = self.model.get_additional_information()
        weather_df = self.model.weather_df

        json_functions = JSONFunctions()
    
        

        simulation_result_json = json_functions.transform_pandas_to_json(
            simulation_results)
        water_storage_json = json_functions.transform_pandas_to_json(
            water_storage)
        water_flux_json = json_functions.transform_pandas_to_json(water_flux)
        crop_growth_json = json_functions.transform_pandas_to_json(crop_growth)
        weather_json = json_functions.transform_pandas_to_json(weather_df)

        # json_files = {
        #     # "simulation_info": additional_information,
        #     "simulation_results": json_functions.json_load(simulation_result_json),
        #     # "crop_growth": json_functions.json_load(crop_growth_json),
        #     # "water_storage": json_functions.json_load(water_storage_json),
        #     # "water_flux": json_functions.json_load(water_flux_json),
        # }
        
        # get the timestamp from 1970 in millisecoms
        today_date = datetime.datetime.now()
        today_year = today_date.year
        today_month = today_date.month
        today_day = today_date.day
        
         
        simulation_info_path = f"{folder_path}/{simulation_id}_{today_year}-{today_month}-{today_day}_simulation_info.json"
        simulation_result_path = f"{folder_path}/{simulation_id}_{today_year}-{today_month}-{today_day}_simulation_results.json"
        crop_growth_path = f"{folder_path}/{simulation_id}_{today_year}-{today_month}-{today_day}_crop_growth.json"
        water_storage_path = f"{folder_path}/{simulation_id}_{today_year}-{today_month}-{today_day}_water_storage.json"
        water_flux_path = f"{folder_path}/{simulation_id}_{today_year}-{today_month}-{today_day}_water_flux.json"
        weather_path = f"{folder_path}/{simulation_id}_{today_year}-{today_month}-{today_day}_weather.json"
        

        json_functions.save_json_file( additional_information, simulation_info_path)
        json_functions.save_json_file( json_functions.json_load(simulation_result_json), simulation_result_path)
        json_functions.save_json_file( json_functions.json_load(crop_growth_json), crop_growth_path)
        json_functions.save_json_file( json_functions.json_load(water_storage_json), water_storage_path)
        json_functions.save_json_file( json_functions.json_load(water_flux_json), water_flux_path)
        json_functions.save_json_file( json_functions.json_load(weather_json), weather_path)
        
