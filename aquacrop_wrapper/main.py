import os
import argparse
import datetime

try:
    from .constants import AquacropConstants
    from .aquacrop_wrapper.crop_wrapper import WCrop
    from .aquacrop_wrapper.soil_wrapper import WSoil
    from .aquacrop_wrapper.irrigation_wrapper import WIrrigation
    from .aquacrop_wrapper.aquacrop_wrapper import AquacropWrapper
    from .aquacrop_wrapper.aquacrop_variables_controller import (
        AquacropVariablesController,
    )
    from .weather_data.weather import Weather
    from .config import OUTPUT_FOLDER



except ImportError:
    from aquacrop_wrapper.crop_wrapper import WCrop
    from aquacrop_wrapper.soil_wrapper import WSoil
    from aquacrop_wrapper.irrigation_wrapper import WIrrigation
    from aquacrop_wrapper.aquacrop_wrapper import AquacropWrapper
    from aquacrop_wrapper.aquacrop_variables_controller import (
        AquacropVariablesController,
    )
    from weather_data.weather import Weather

    from constants import AquacropConstants
    from config import OUTPUT_FOLDER


# ----- Parse arguments -----
# In this section, we parse the arguments passed to the script
parser = argparse.ArgumentParser()

parser.add_argument(
    "-sstart", "--sim_start", type=str, help="Date of simulation start (YYYY/MM/DD)"
)
parser.add_argument(
    "-send", "--sim_end", type=str, help="Date of simulation end (YYYY/MM/DD)"
)
# parser.add_argument("--test_mode", action="store_true", help="Test mode (True/False)")
# parser.add_argument(
#     "-wpath", "--weather_path", type=str, help="File path with weather data"
# )
parser.add_argument(
    "-stype",
    "--soil_type",
    choices=AquacropConstants.TYPES_OF_SOILS,
    type=str,
    help="Soil type",
)
parser.add_argument(
    "-crop",
    "--crop_type",
    type=str,
    choices=AquacropConstants.TYPES_OF_CROPS,
    help="Crop type",
)
parser.add_argument("-pdate", "--planting_date", type=str, help="Planting date (MM/DD)")

# -+-+-+- IRRIGATION -+-+-+-+-
parser.add_argument(
    "-iwc",
    "--initial_water_content",
    choices=AquacropConstants.INITIAL_WATER_CONTENT,
    type=str,
    help="Sowing date (MM/DD)",
)
parser.add_argument(
    "-imethod",
    "--irrigation_method",
    choices=list(AquacropConstants.IRRIGATION_METHODS.keys()),
    type=str,
    help="Irrigation method",
)
parser.add_argument(
    "-itintervals",
    "--irrigation_time_interval",
    type=int,
    help="Irrigation interval in days (only used if irrigation_method is equal to set_time_interval)",
)

# parser.add_argument("-ischedule", "--irrigation_schedule", type=str, help="Irrigation schedule (only used if irrigation_method is equal to predifined_schedule)")
parser.add_argument(
    "-nismt",
    "--net_irrigation_soil_moisture_target",
    type=float,
    help="Net irrigation soil moisture target (%taw) (only used if irrigation_method is equal to net_irrigation)",
)
parser.add_argument(
    "-cdepth",
    "--constant_depth",
    type=float,
    help="Constant depth of irrigation (mm) (only used if irrigation_method is equal to constant_depth)",
)

parser.add_argument(
    "-smt",
    "--soil_moisture_targets",
    type=str,
    help="""(list): Soil moisture targets (%taw) to maintain in each growth stage (4)
                    (only used if irrigation method is equal to soil_moisture_targets). Info: growing stages are emergence, 
                    canopy_growth, max_canopy and senescence""",
)

# type of simulation
parser.add_argument(
    "-simtype",
    "--simulation_types",
    type=str,
    choices=AquacropConstants.SIMULATION_TYPES,
    default="normal_simulation",
    help="Type of simulation",
)

# start weather data
parser.add_argument(
    "-swdate",
    "--start_weather_year",
    type=int,
    help="Start weather date for historic data",
)

# end weather data
parser.add_argument(
    "-ewdate",
    "--end_weather_year",
    type=int,
    help="End weather date for historic data",
)

# RIA STATION ID
parser.add_argument(
    "-rsid",
    "--ria_station_id",
    type=int,
    help="RIA station id",
)

# RIA PROVINCE ID
parser.add_argument(
    "-rpid",
    "--ria_province_id",
    type=int,
    help="RIA province id",
)

# Complete weather data
parser.add_argument(
    "-cwd",
    "--complete_weather_data",
    type=bool,
    choices=[True, False],
    help="Complete Weather Data or Not?",
)

# Complete type
parser.add_argument(
    "-cwtype",
    "--complete_weather_type",
    type=str,
    choices=AquacropConstants.COMPLETE_WEATHER_DATA_TYPE,
    help="Complete weather  type",
)

# Complete values method
parser.add_argument(
    "-cwvm",
    "--complete_weather_values_method",
    type=str,
    choices=AquacropConstants.COMPLETE_WEATHER_DATA_METHOD,
    help="Complete weather values method",
)

# latitude
parser.add_argument(
    "-lat",
    "--latitude",
    type=float,
    help="Latitude (degrees)",
)

# longitude
parser.add_argument(
    "-lon",
    "--longitude",
    type=float,
    help="Longitude (degrees)",
)

# Altitude
parser.add_argument(
    "-alt",
    "--altitude",
    type=float,
    help="Altitude (m) ",
)


args = parser.parse_args()


# ----- Check Variables -----
args.ria_station_id = str(args.ria_station_id)
args.soil_moisture_targets = args.soil_moisture_targets.split(',')
if(len(args.soil_moisture_targets)!= 4):
    raise ValueError("Soil moisture targets must be a list of 4 values")

# ----- Run Aquacrop -----
print("args = ", args)
crop = WCrop(crop_type=args.crop_type, planting_date=args.planting_date)
soil = WSoil(soil_type=args.soil_type)
irrigation = WIrrigation(
    irrigation_method=args.irrigation_method,
    initial_water_content=args.initial_water_content,
    soil_moisture_targets=args.soil_moisture_targets,
    net_irrigation_soil_moisture_target=args.net_irrigation_soil_moisture_target,
    constant_depth=args.constant_depth,
    irrigation_time_interval=args.irrigation_time_interval,
)
# weather = WWeather(weather_file_path=args.weather_path,
#                    test_mode=args.test_mode)

aquacrop_variables_controller = AquacropVariablesController(
    simulation_types=args.simulation_types
)



# start_weather_year = 2000  # start year weather data
# end_weather_year = 2022  # end year weather data
# ria_station_id = "2"  # station id
# ria_province_id = 14  # province id
# complete_weather_data = True  # complete data
# complete_weather_type = "last_n_years"  # complete type
# complete_weather_values_method = "driest_year"  # complete values method (rainest_year, driest_year, means, in_percentage_of_the_average)
# # harvest_date =  "08-4" # format MM/DD (aproximate) This is used in the complete data method. Why? Because..
# lat_deg = 37.0  # latitude
# lon_deg = -4.0  # longitude
# altitude = 200.0  # altitude


output_file_path = f"{OUTPUT_FOLDER}/output_{args.start_weather_year}_{args.end_weather_year}_{args.complete_weather_values_method}.json"

# julian_harvest_date = datetime.datetime.strptime(harvest_date, "%m-%d").timetuple().tm_yday

weather = Weather(
    start_simulation_date=args.sim_start, end_simulation_date=args.sim_end
)

# Important notes:
# 1. The weather data is downloaded from the RIA (https://www.riagro.net/). The data is downloaded in a json format.
# 2. The weather data is downloaded for the period of time between start_weather_year and end_weather_year.
# 3. Complete values method is used to complete the future weather data. The complete values method can be: rainest_year, driest_year, means
## In the raienest and driest the algorithm select the months with more and less precipitation

historical_weather = weather.get_weather_data_using_ria(
    start_year=args.start_weather_year,
    end_year=args.end_weather_year,
    station_id=args.ria_station_id,
    province_id=args.ria_province_id,
    complete_data=args.complete_weather_data,
    complete_type=args.complete_weather_type,
    complete_values_method=args.complete_weather_values_method,
)

forecast_weather = weather.get_forecast_for_the_next_5_days(
    lat_degrees=args.latitude, lon_degrees=args.longitude, altitude=args.altitude
)

# THIS CODE UPDATE THE HISTORICAL WEATHER WITH THE FORECAST WEATHER (very simple)
historical_weather.set_index("Date", inplace=True)
forecast_weather.set_index("Date", inplace=True)

historical_weather.update(forecast_weather)
historical_weather.reset_index(inplace=True)

aquacrop = AquacropWrapper(
    sim_start=args.sim_start,
    sim_end=args.sim_end,
    weather=historical_weather,
    soil=soil,
    crop=crop,
    irrigation=irrigation,
)

aquacrop = AquacropWrapper(
    sim_start=args.sim_start,
    sim_end=args.sim_end,
    weather=historical_weather,
    soil=soil,
    crop=crop,
    irrigation=irrigation,
)
# delete this +-+-+-+-+-+-+-
import matplotlib.pyplot as plt
irrigation2 = WIrrigation(
    irrigation_method="soil_moisture_targets",
    initial_water_content=args.initial_water_content,
    soil_moisture_targets=args.soil_moisture_targets,
    net_irrigation_soil_moisture_target=args.net_irrigation_soil_moisture_target,
    constant_depth=args.constant_depth,
    irrigation_time_interval=args.irrigation_time_interval,
)
aquacrop2 = AquacropWrapper(
    sim_start=args.sim_start,
    sim_end=args.sim_end,
    weather=historical_weather,
    soil=soil,
    crop=crop,
    irrigation=irrigation2,
)
aquacrop.run(aquacrop_variables_controller=aquacrop_variables_controller)

# aquacrop2.run(aquacrop_variables_controller=aquacrop_variables_controller)
# crop_growth_rainfed = aquacrop.model.get_crop_growth()
# crop_growth_irrigated = aquacrop2.model.get_crop_growth()

# # drop time_step_counter == 0
# crop_growth_rainfed = crop_growth_rainfed[crop_growth_rainfed["time_step_counter"] != 0]
# crop_growth_irrigated = crop_growth_irrigated[crop_growth_irrigated["time_step_counter"] != 0]

# canopy_cover_rainfed = crop_growth_rainfed["canopy_cover"]
# canopy_cover_irrigated = crop_growth_irrigated["canopy_cover"]

# date_formated_rainfed = crop_growth_rainfed["date"].apply(
#             lambda x: datetime.datetime.fromtimestamp(x)
#         )
# date_formated_irrigated = crop_growth_irrigated["date"].apply(

#             lambda x: datetime.datetime.fromtimestamp(x)
#         )

# irrigation = aquacrop2.model.get_water_flux()["IrrDay"]

# fig, ax = plt.subplots()
# ax.plot(date_formated_rainfed,canopy_cover_rainfed, label="rainfed", linestyle="--", color="red")
# ax.plot(date_formated_irrigated,canopy_cover_irrigated, label="irrigated", linestyle="-", color="green")


# ax.set_xlabel("Days")
# ax.set_ylabel("Canopy cover")
# ax.legend()

# delete until this

# print(aquacrop.run(aquacrop_variables_controller=aquacrop_variables_controller))

# print(aquacrop.get_simulation_results())

# aquacrop.show_charts()

aquacrop.save_outputs(file_path=output_file_path)


# EXAMPLE

# python main.py -sstart 1982/05/01 -send 1983/10/30 --test_mode -wpath champion_climate.txt -stype SandyLoam -crop Maize -pdate 05/01 -iwc FC -imethod rainfed
