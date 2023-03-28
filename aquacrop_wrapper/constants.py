

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
