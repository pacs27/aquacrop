import os
class ProjectConstants:
    """Constants used in Aquacrop project."""
    # Aquacrop project constants
    PROJECT_FOLDER_NAME = "aquacrop_cameras"
    PARENT_DIRECTORY_PATH = os.getcwd()

    
class AquacropConstants:
    """Constants used in Aquacrop model."""
    # Aquacrop constants

    TYPES_OF_SOILS = [
        "Clay",
        "ClayLoam",
        "Loam",
        "LoamySand",
        "Sand",
        "SandyClay",
        "SandyClayLoam",
        "SandyLoam",
        "Silt",
        "SiltClayLoam",
        "SiltLoam",
        "SiltClay",
        "Paddy",
        "ac_TunisLocal",
    ]

    TYPES_OF_CROPS = [
        "Barley",
        "Cotton",
        "DryBean",
        "Maize",
        "PaddyRice",
        "Potato",
        "Quinoa",
        "Sorghum",
        "Soybean",
        "SugarBeet",
        "SugarCane",
        "Sunflower",
        "Tomato",
        "Wheat",
    ]

    # WP is the wilting point, FC is the field capacity, and SAT is the saturation point
    INITIAL_WATER_CONTENT = [
        'WP',
        'FC',
        'SAT'
    ]

    IRRIGATION_METHODS = {
        "rainfed": 0, "soil_moisture_targets": 1, "set_time_interval": 2,
        "predifined_schedule": 3, "net_irrigation": 4, "constant_depth": 5
    }

    CROP_GROWTH_STAGES = {
        "emergence": 0, "canopy_growth": 1, "max_canopy": 2, "senescence": 3
    }
    
    SIMULATION_TYPES = {
        "normal_simulation":0,
        "real_time_update":1,
    }

    COMPLETE_WEATHER_DATA_TYPE = {
        "last_year_data": 0,
        "last_n_years": 1,
        
    }
    
    COMPLETE_WEATHER_DATA_METHOD = {
        "means": 0,
        "driest_year": 1,
        "rainest_year": 2

    }