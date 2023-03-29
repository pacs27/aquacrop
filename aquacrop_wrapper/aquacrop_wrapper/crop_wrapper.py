import sys
sys.path.append('/Users/pacopuig/Desktop/PROGRAMACION/aquacrop_cameras/aquacrop_wrapper/aquacrop')

try:
    from constants import AquacropConstants
except ImportError:
    from ..constants import AquacropConstants

from aquacrop import Crop

class WCrop:
    """Wrapper for the Crop class from aquacrop package.
       The class also checks if the crop type is valid.
    """

    def __init__(self, crop_type: AquacropConstants.TYPES_OF_CROPS, planting_date):
        if (crop_type not in AquacropConstants.TYPES_OF_CROPS):
            raise ValueError("""Invalid crop type, valid values are: Barley, Cotton, 
                             DryBean, Maize, PaddyRice, Potato, Quinoa, Sorghum, 
                             Soybean, SugarBeet, SugarCane, Sunflower, Tomato, Wheat""")
        self.crop_type = crop_type
        self.crop = Crop(c_name=self.crop_type, planting_date=planting_date)
