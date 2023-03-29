import sys
sys.path.append('/Users/pacopuig/Desktop/PROGRAMACION/aquacrop_cameras/aquacrop_wrapper/aquacrop')

if not '-m' in sys.argv:
    from .aquacrop_wrapper import AquacropWrapper
    from .crop_wrapper import WCrop
    from .irrigation_wrapper import WIrrigation
    from .soil_wrapper import WSoil
    from .weather_wrapper import WWeather
    