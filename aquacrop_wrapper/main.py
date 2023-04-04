import argparse

try:
    from .constants import AquacropConstants
    from .aquacrop_wrapper.crop_wrapper import WCrop
    from .aquacrop_wrapper.soil_wrapper import WSoil
    from .aquacrop_wrapper.irrigation_wrapper import WIrrigation
    from .aquacrop_wrapper.weather_wrapper import WWeather
    from .aquacrop_wrapper.aquacrop_wrapper import AquacropWrapper
    from .aquacrop_wrapper.aquacrop_variables_controller import AquacropVariablesController
    from .weather_data.weather_ria_stations import WeatherRIAStations
    from .weather_data.weather import Weather


except ImportError:
    from aquacrop_wrapper.crop_wrapper import WCrop
    from aquacrop_wrapper.soil_wrapper import WSoil
    from aquacrop_wrapper.irrigation_wrapper import WIrrigation
    from aquacrop_wrapper.weather_wrapper import WWeather
    from aquacrop_wrapper.aquacrop_wrapper import AquacropWrapper
    from aquacrop_wrapper.aquacrop_variables_controller import AquacropVariablesController
    from weather_data.weather_ria_stations import WeatherRIAStations
    from weather_data.weather import Weather

    from constants import AquacropConstants


# ----- Parse arguments -----
# In this section, we parse the arguments passed to the script
parser = argparse.ArgumentParser()

parser.add_argument("-sstart", "--sim_start", type=str,
                    help="Date of simulation start (YYYY/MM/DD)")
parser.add_argument("-send", "--sim_end", type=str,
                    help="Date of simulation end (YYYY/MM/DD)")
parser.add_argument("--test_mode", action='store_true',
                    help="Test mode (True/False)")
parser.add_argument("-wpath", "--weather_path", type=str,
                    help="File path with weather data")
parser.add_argument("-stype", "--soil_type",
                    choices=AquacropConstants.TYPES_OF_SOILS, type=str, help="Soil type")
parser.add_argument("-crop", "--crop_type", type=str,
                    choices=AquacropConstants.TYPES_OF_CROPS, help="Crop type")
parser.add_argument("-pdate", "--plating_date", type=str,
                    help="Planting date (MM/DD)")

# -+-+-+- IRRIGATION -+-+-+-+-
parser.add_argument("-iwc", "--initial_water_content",
                    choices=AquacropConstants.INITIAL_WATER_CONTENT, type=str,
                    help="Sowing date (MM/DD)")
parser.add_argument("-imethod", "--irrigation_method", choices=list(
    AquacropConstants.IRRIGATION_METHODS.keys()), type=str, help="Irrigation method")
parser.add_argument("-itintervals", "--irrigation_time_interval", type=int,
                    help="Irrigation interval in days (only used if irrigation_method is equal to set_time_interval)")

# parser.add_argument("-ischedule", "--irrigation_schedule", type=str, help="Irrigation schedule (only used if irrigation_method is equal to predifined_schedule)")
parser.add_argument("-nismt", "--net_irrigation_soil_moisture_target", type=float,
                    help="Net irrigation soil moisture target (%taw) (only used if irrigation_method is equal to net_irrigation)")
parser.add_argument("-cdepth", "--constant_depth", type=float,
                    help="Constant depth of irrigation (mm) (only used if irrigation_method is equal to constant_depth)")

parser.add_argument("-smt", "--soil_moisture_targets", type=str,
                    help="""(list): Soil moisture targets (%taw) to maintain in each growth stage 
                    (only used if irrigation method is equal to soil_moisture_targets). Info: growing stages are emergence, 
                    canopy_growth, max_canopy and senescence""")

# type of simulation
parser.add_argument("-simtype", "--simulation_types", type=str,
                    choices=AquacropConstants.SIMULATION_TYPES, default="normal_simulation", help="Type of simulation")

args = parser.parse_args()

# ----- Run Aquacrop -----
print("args = ", args)
crop = WCrop(crop_type=args.crop_type, planting_date=args.plating_date)
soil = WSoil(soil_type=args.soil_type)
irrigation = WIrrigation(irrigation_method=args.irrigation_method,
                         initial_water_content=args.initial_water_content,
                         soil_moisture_targets=args.soil_moisture_targets,
                         net_irrigation_soil_moisture_target=args.net_irrigation_soil_moisture_target,
                         constant_depth=args.constant_depth,
                         irrigation_time_interval=args.irrigation_time_interval

                         )
# weather = WWeather(weather_file_path=args.weather_path,
#                    test_mode=args.test_mode)

aquacrop_variables_controller = AquacropVariablesController(
    simulation_types=args.simulation_types)
weather_ria_stations = WeatherRIAStations()
weather = Weather(start_simulation_date=args.sim_start,
                  end_simulation_date=args.sim_end)

weather_df = weather.get_weather_data_using_ria(start_year=2015, end_year=2019,
                                                station_id="2", province_id=14, complete_data=True,
                                                complete_type="last_n_years", complete_values_method="means")
json_weather_data = weather_ria_stations.get_json_data(
    province_id=14, station_id="2", initial_date=args.sim_start, end_date=args.sim_end, complete_data=True)

weather_df = weather_ria_stations.get_weather_data()
aquacrop_weather = weather_ria_stations.transform_data_into_aquacrop_format(
    json_weather_data=json_weather_data)

aquacrop = AquacropWrapper(sim_start=args.sim_start, sim_end=args.sim_end,
                           weather=aquacrop_weather, soil=soil, crop=crop, irrigation=irrigation)


print(aquacrop.run(aquacrop_variables_controller=aquacrop_variables_controller))

output_file_path = "/Users/pacopuig/Desktop/PROGRAMACION/aquacrop_cameras/aquacrop_wrapper/data/output.json"
aquacrop.save_outputs(file_path=output_file_path)


# EXAMPLE

# python main.py -sstart 1982/05/01 -send 1983/10/30 --test_mode -wpath champion_climate.txt -stype SandyLoam -crop Maize -pdate 05/01 -iwc FC -imethod rainfed
