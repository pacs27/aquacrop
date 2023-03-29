import sys
sys.path.append('/Users/pacopuig/Desktop/PROGRAMACION/aquacrop_cameras/aquacrop_wrapper/aquacrop')

try:
    from constants import AquacropConstants
except ImportError:
    from ..constants import AquacropConstants


from aquacrop import (
    InitialWaterContent,
    IrrigationManagement,
)

class WIrrigation:
    """ Wrapper for the IrrigationManagement class from aquacrop package.
        The class also checks if the irrigation method is valid and if the initial water content is valid.
    """

    def __init__(self, irrigation_method: AquacropConstants.IRRIGATION_METHODS,
                 initial_water_content: AquacropConstants.INITIAL_WATER_CONTENT,
                 soil_moisture_targets,
                 irrigation_time_interval,
                 net_irrigation_soil_moisture_target,
                 constant_depth,
                 predefined_schedule=None):
        # Define variables
        self.irrigation_method = irrigation_method
        self.soil_moisture_targets = soil_moisture_targets
        self.irrigation_time_interval = irrigation_time_interval
        self.net_irrigation_soil_moisture_target = net_irrigation_soil_moisture_target
        self.constant_depth = constant_depth
        self.predefined_schedule = predefined_schedule

        # Checking
        self.checkIrrigationMethod(irrigation_method)
        self.irrigation_method = AquacropConstants.IRRIGATION_METHODS[irrigation_method]

        self.checkInitialWaterContent(initial_water_content)
        self.initial_water_content = InitialWaterContent(
            value=[initial_water_content])

        # Calculate irrigation management
        self.irrigation_management = self.calculateIrrigationManagement()

    def checkIrrigationMethod(self, irrigation_method):
        if (irrigation_method not in AquacropConstants.IRRIGATION_METHODS.keys()):
            raise ValueError("""Invalid irrigation method, valid values are: rainfed, 
                             soil_moisture_targets, set_time_interval,
                             predifined_schedule, net_irrigation, constant_depth""")

    def checkInitialWaterContent(self, initial_water_content):
        if (initial_water_content not in AquacropConstants.INITIAL_WATER_CONTENT):
            raise ValueError(
                """Invalid initial water content, valid values are: WP, FC, SAT""")

    def calculateIrrigationManagement(self):
        if self.irrigation_method == AquacropConstants.IRRIGATION_METHODS["rainfed"]:
            irrigation_management = IrrigationManagement(
                irrigation_method=self.irrigation_method
            )
        elif self.irrigation_method == AquacropConstants.IRRIGATION_METHODS["soil_moisture_targets"]:
            irrigation_management = IrrigationManagement(
                irrigation_method=self.irrigation_method,
                soil_moisture_targets=self.soil_moisture_targets
            )
        elif self.irrigation_method == AquacropConstants.IRRIGATION_METHODS["set_time_interval"]:
            irrigation_management = IrrigationManagement(
                irrigation_method=self.irrigation_method,
                time_interval=self.irrigation_time_interval
            )
        elif self.irrigation_method == AquacropConstants.IRRIGATION_METHODS["predifined_schedule"]:
            irrigation_management = IrrigationManagement(
                irrigation_method=self.irrigation_method,
                predefined_schedule=self.predefined_schedule
            )
        elif self.irrigation_method == AquacropConstants.IRRIGATION_METHODS["net_irrigation"]:
            irrigation_management = IrrigationManagement(
                irrigation_method=self.irrigation_method,
                net_irrigation_soil_moisture_target=self.net_irrigation_soil_moisture_target
            )
        elif self.irrigation_method == AquacropConstants.IRRIGATION_METHODS["constant_depth"]:
            irrigation_management = IrrigationManagement(
                irrigation_method=self.irrigation_method,
                constant_depth=self.constant_depth
            )
        else:
            raise ValueError(
                "Invalid irrigation method, valid values are: rainfed, soil_moisture_targets, set_time_interval, predifined_schedule, net_irrigation, constant_depth"
            )
        return irrigation_management

    def getIrrigationManagementAndInitialWaterContent(self):
        return (self.irrigation_management, self.initial_water_content)
