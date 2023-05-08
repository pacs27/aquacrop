from typing import TYPE_CHECKING
import datetime
import sys
sys.path.append(
    '/Users/pacopuig/Desktop/PROGRAMACION/aquacrop_cameras/aquacrop_wrapper/aquacrop')


if TYPE_CHECKING:
    from aquacrop.entities.clockStruct import ClockStruct
    from aquacrop.entities.initParamVariables import InitialCondition
    from aquacrop.entities.paramStruct import ParamStruct
    from aquacrop.entities.output import Output

try:
    from constants import AquacropConstants
except ImportError:
    from ..constants import AquacropConstants


class AquacropVariablesController:
    """This class is used to control the variables before timestemp function is called in aquacrop library.
        I know that this is not the best approach to do this, but I couldn't find a better way
        The variables controller is a param of the aquacrop run_simualtion method that in this case is called
        in aquacrop_wrapper file

        TODO: This class is a little complicated. Take care of the commends and the code.
    """

    def __init__(self, simulation_types: AquacropConstants.SIMULATION_TYPES.keys(), cameras_data_df):

        if (simulation_types not in AquacropConstants.SIMULATION_TYPES.keys()):
            raise ValueError("""Invalid simulation type, valid values are:
                                 "normal_simulation", "simulation_until_today" """)
        self.simulation_types = AquacropConstants.SIMULATION_TYPES[simulation_types]
        self.cameras_data_df = cameras_data_df

    def variables_controller_interface(self, clock_struct: "ClockStruct",
                                       init_cond: "InitialCondition",
                                       param_struct: "ParamStruct",
                                       outputs: "Output"
                                    ):
        """ Note: This function is called by the AquaCrop model and should not be called directly.
                It also depends on this library's implementation of the AquaCrop model. The implementation
                of this function is inside the while loop of the core file in aquacrop.

            TODO: I know tha this is not the best approach to do this, but I couldn't find a better way 

        Returns:
            _type_: _description_
        """
        # datetime.datetime.date(clock_struct.planting_dates[0])
        # clock_struct.current_simulation_date
        (clock_struct, init_cond, param_struct, outputs) = self.body_interface(
            clock_struct, init_cond, param_struct, outputs)

        return (clock_struct, init_cond, param_struct, outputs)

    def body_interface(self, clock_struct: "ClockStruct", init_cond: "InitialCondition", param_struct: "ParamStruct", outputs: "Output"):

        if (self.simulation_types == AquacropConstants.SIMULATION_TYPES["normal_simulation"]):
            return (clock_struct, init_cond, param_struct, outputs)
        elif (self.simulation_types == AquacropConstants.SIMULATION_TYPES["real_time_update"]):
            return self.simulation_until_today(clock_struct, init_cond, param_struct, outputs)
        else:
            return (clock_struct, init_cond, param_struct, outputs)

    def simulation_until_today(self, clock_struct: "ClockStruct",
                               init_cond: "InitialCondition",
                               param_struct: "ParamStruct", outputs: "Output"):
        """This function is called when the simulation type is "simulation_until_today"
            This function is used to run the simulation until the current date.
            The simulation will be updated with the current values of the variables and will continue
            the simulation until the end date."""
        # simulation_start_date = clock_struct.simulation_start_date
        simulation_end_date = clock_struct.simulation_end_date
        

        date_now = datetime.datetime.now()
        # Check if the simulation start date is before the current date
        if (date_now > simulation_end_date):
            raise Exception(
                """The end date of the simulation is before today, 
                so this type of simulation will not work. 
                Please update the simulation start date""")
            
        current_simulation_date = clock_struct.current_simulation_date
        # transform to foarmat day-month-year
        current_simulation_date_str = current_simulation_date.strftime("%d-%m-%Y")
        
        cameras_data = self.cameras_data_df
        
        # select the same day-month-year as current_simulation_date
        cameras_data = cameras_data[cameras_data["day-month-year"] == current_simulation_date_str]
        
        real_canopy_cover = 0
         # check if the cameras_data is empty
        if not cameras_data.empty:
            real_canopy_cover = float(cameras_data["canopyCover"].iloc[0])/100
        
        if(init_cond.canopy_cover > 0):
            if real_canopy_cover and real_canopy_cover > 0:
                init_cond.camera_canopy_cover = real_canopy_cover
            else:
                init_cond.camera_canopy_cover = None
        
        # TODO: DELETE!!!!!!!!!!!
        # date_now = datetime.datetime(2023, 4, 1)
        
        
        # SEE IF THE SIMULATION IS PERFOMING IN THE FUTURE
        # if (date_now.date() < current_simulation_date):
        #     param_struct.IrrMngt.irrigation_method = 1 # 1 = SOIL MOISTURE TARGETS
        
        # TODO: DELETE!!!!!!!!!!!  
        # date2 = datetime.datetime(2023, 5, 1)
        # date3 = datetime.datetime(2023, 5, 30)
        # if(current_simulation_date > date2.date()):
        #     param_struct.IrrMngt.irrigation_method = 0
        # if(current_simulation_date > date3.date()):
        #     param_struct.IrrMngt.irrigation_method = 1
        # # if (current_simulation_date > date3):
        #     param_struct.IrrMngt.irrigation_method = 1 # 1 = SOIL MOISTURE TARGETS
        # else:
        #     param_struct.IrrMngt.irrigation_method = 0
            
        return (clock_struct, init_cond, param_struct, outputs)
