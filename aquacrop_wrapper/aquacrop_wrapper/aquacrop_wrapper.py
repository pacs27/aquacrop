import sys
sys.path.append('/Users/pacopuig/Desktop/PROGRAMACION/aquacrop_cameras/aquacrop_wrapper/aquacrop')

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aquacrop.entities.clockStruct import ClockStruct
    from aquacrop.entities.initParamVariables import InitialCondition
    from aquacrop.entities.paramStruct import ParamStruct
    from aquacrop.entities.output import Output
    from .crop_wrapper import WCrop
    from .irrigation_wrapper import WIrrigation
    from .soil_wrapper import WSoil
    from .weather_wrapper import WWeather



from aquacrop import (
    AquaCropModel,
)


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

    def __init__(self,  sim_start, sim_end, weather: "WWeather", soil: "WSoil", crop: "WCrop", irrigation: "WIrrigation"):
        self.sim_start = sim_start
        self.sim_end = sim_end
        self.weather = weather
        self.soil = soil
        self.crop = crop
        self.irrigation = irrigation

    def run(self):
        """Runs the AquaCrop model and returns the final statistics

        Returns:
            _type_: _description_
        """
        self.model = AquaCropModel(
            weather_df=self.weather.weather,
            crop=self.crop.crop,
            soil=self.soil.soil,
            irrigation_management=self.irrigation.irrigation_management,
            initial_water_content=self.irrigation.initial_water_content,
            sim_start_time=self.sim_start,
            sim_end_time=self.sim_end,
        )
        self.model.run_model(till_termination=True)

        additional_information = self.model.get_additional_information()
        return additional_information
    @staticmethod
    def controlled_variables_func(clock_struct: "ClockStruct", init_cond:"InitialCondition", param_struct:"ParamStruct", outputs:"Output"):
        """ Note: This function is called by the AquaCrop model and should not be called directly.
                It also depends on this library's implementation of the AquaCrop model. The implementation
                of this function is inside the while loop of the core file in aquacrop.
                
            TODO: I know tha this is not the best approach to do this, but I couldn't find a better way 

        Returns:
            _type_: _description_
        """
        return  clock_struct, init_cond, param_struct, outputs

    def save_outputs(self, file_path):
        simulation_results = self.model.get_simulation_results()
        water_storage = self.model.get_water_storage()
        water_flux = self.model.get_water_flux()
        crop_growth = self.model.get_crop_growth()
        additional_information = self.model.get_additional_information()

        json_functions = JSONFunctions()

        simulation_result_json = json_functions.transform_pandas_to_json(
            simulation_results)
        water_storage_json = json_functions.transform_pandas_to_json(
            water_storage)
        water_flux_json = json_functions.transform_pandas_to_json(water_flux)
        crop_growth_json = json_functions.transform_pandas_to_json(crop_growth)
 

        json_files = {
            "simulation_info": additional_information,
            "simulation_results": json_functions.json_load(simulation_result_json),
            "crop_growth": json_functions.json_load(crop_growth_json),
            "water_storage": json_functions.json_load(water_storage_json),
            "water_flux": json_functions.json_load(water_flux_json),
        }

        json_functions.save_json_file(json_files, file_path)
