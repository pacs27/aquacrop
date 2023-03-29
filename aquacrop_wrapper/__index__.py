import sys
sys.path.append('/Users/pacopuig/Desktop/PROGRAMACION/aquacrop_cameras/aquacrop_wrapper/aquacrop')

if not '-m' in sys.argv:
    from .aquacrop_wrapper.aquacrop_wrapper import AquacropWrapper
    from .aquacrop_wrapper.soil_wrapper import WSoil
    from .aquacrop_wrapper.weather_wrapper import WWeather
    from .aquacrop_wrapper.crop_wrapper import WCrop
    from .aquacrop_wrapper.irrigation_wrapper import WIrrigation
    

