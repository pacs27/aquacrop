import sys
sys.path.append('/Users/pacopuig/Desktop/PROGRAMACION/aquacrop_cameras/aquacrop_wrapper/aquacrop')

from aquacrop import (
    Soil,
)

try:
    from constants import AquacropConstants
except ImportError:
    from ..constants import AquacropConstants


class WSoil:
    """ Wrapper for the Soil class from aquacrop package.
        The class also checks if the soil type is valid.
    """

    def __init__(self, soil_type: AquacropConstants.TYPES_OF_SOILS):
        if (soil_type not in AquacropConstants.TYPES_OF_SOILS):
            raise ValueError("""Invalid soil type, valid values are: Clay, ClayLoam, 
                             Loam, LoamySand, Sand, SandyClay, SandyClayLoam, SandyLoam, 
                             Silt, SiltClayLoam, SiltLoam, SiltClay, Paddy, ac_TunisLocal""")
        self.soil_type = soil_type
        self.soil = Soil(soil_type=soil_type)


