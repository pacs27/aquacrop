"""
This file contains the AquacropModel class that runs the simulation.
"""
import time
import datetime
import os
import logging

import pandas as pd

from typing import (
    Dict,
    Union,
    Optional,
    Tuple,
    TYPE_CHECKING,
    Callable,
    Literal,
    get_args,
)
from .scripts.checkIfPackageIsCompiled import compile_all_AOT_files

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from pandas import DataFrame
    from aquacrop.entities.clockStruct import ClockStruct
    from aquacrop.entities.co2 import CO2
    from aquacrop.entities.crop import Crop
    from aquacrop.entities.initParamVariables import InitialCondition
    from aquacrop.entities.inititalWaterContent import InitialWaterContent
    from aquacrop.entities.paramStruct import ParamStruct
    from aquacrop.entities.soil import Soil


# Important: This code is necessary to check if the AOT files are compiled.
if os.getenv("DEVELOPMENT"):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logging.info("Running the simulation in development mode.")
else:
    compile_all_AOT_files()


# pylint: disable=wrong-import-position
from .entities.co2 import CO2
from .entities.fieldManagement import FieldMngt
from .entities.groundWater import GroundWater
from .entities.irrigationManagement import IrrigationManagement
from .entities.output import Output
from .initialize.compute_variables import compute_variables
from .initialize.create_soil_profile import create_soil_profile
from .initialize.read_clocks_parameters import read_clock_paramaters
from .initialize.read_field_managment import read_field_management
from .initialize.read_groundwater_table import read_groundwater_table
from .initialize.read_irrigation_management import read_irrigation_management
from .initialize.read_model_initial_conditions import read_model_initial_conditions
from .initialize.read_model_parameters import read_model_parameters
from .initialize.read_weather_inputs import read_weather_inputs
from .timestep.check_if_model_is_finished import check_model_is_finished
from .timestep.run_single_timestep import solution_single_time_step
from .timestep.update_time import update_time
from .timestep.outputs_when_model_is_finished import outputs_when_model_is_finished


class AquaCropModel:
    """
    This is the main class of the AquaCrop-OSPy model.
    It is in charge of executing all the operations.

    Parameters:

        sim_start_time (str): YYYY/MM/DD, Simulation start date

        sim_end_time (str): date YYYY/MM/DD, Simulation end date

        weather_df: daily weather data , created using prepare_weather

        soil: Soil object contains paramaters and variables of the soil
                used in the simulation

        crop: Crop object contains Paramaters and variables of the crop used
                in the simulation

        initial_water_content: Defines water content at start of simulation

        irrigation_management: Defines irrigation strategy

        field_management: Defines field management options

        fallow_field_management: Defines field management options during fallow period

        groundwater: Stores information on water table parameters

        co2_concentration: Defines CO2 concentrations


    """

    # Model parameters
    # True if all steps of the simulation are done.
    __steps_are_finished: bool = False
    __has_model_executed: bool = False  # Determines if the model has been run
    __has_model_finished: bool = False  # Determines if the model is finished
    __start_model_execution: float = 0.0  # Time when the execution start
    __end_model_execution: float = 0.0  # Time when the execution end
    # Attributes initialised later
    _clock_struct: "ClockStruct"
    _param_struct: "ParamStruct"
    _init_cond: "InitialCondition"
    _outputs: "Output"
    _weather_df: "DataFrame"

    def __init__(
        self,
        sim_start_time: str,
        sim_end_time: str,
        weather_df: "DataFrame",
        soil: "Soil",
        crop: "Crop",
        initial_water_content: "InitialWaterContent",
        irrigation_management: Optional["IrrigationManagement"] = None,
        field_management: Optional["FieldMngt"] = None,
        fallow_field_management: Optional["FieldMngt"] = None,
        groundwater: Optional["GroundWater"] = None,
        co2_concentration: Optional["CO2"] = None,
    ) -> None:
        self.sim_start_time = sim_start_time
        self.sim_end_time = sim_end_time
        self.weather_df = weather_df
        self.soil = soil
        self.crop = crop
        self.initial_water_content = initial_water_content
        self.co2_concentration = co2_concentration

        self.irrigation_management = irrigation_management
        self.field_management = field_management
        self.fallow_field_management = fallow_field_management
        self.groundwater = groundwater

        if irrigation_management is None:
            self.irrigation_management = IrrigationManagement(irrigation_method=0)
        if field_management is None:
            self.field_management = FieldMngt()
        if fallow_field_management is None:
            self.fallow_field_management = FieldMngt()
        if groundwater is None:
            self.groundwater = GroundWater()
        if co2_concentration is None:
            self.co2_concentration = CO2()

    @property
    def sim_start_time(self) -> str:
        """
        Return sim start date
        """
        return self._sim_start_time

    @sim_start_time.setter
    def sim_start_time(self, value: str) -> None:
        """
        Check if sim start date is in a correct format.
        """

        if _sim_date_format_is_correct(value) is not False:
            self._sim_start_time = value
        else:
            raise ValueError("sim_start_time format must be 'YYYY/MM/DD'")

    @property
    def sim_end_time(self) -> str:
        """
        Return sim end date
        """
        return self._sim_end_time

    @sim_end_time.setter
    def sim_end_time(self, value: str) -> None:
        """
        Check if sim end date is in a correct format.
        """
        if _sim_date_format_is_correct(value) is not False:
            self._sim_end_time = value
        else:
            raise ValueError("sim_end_time format must be 'YYYY/MM/DD'")

    @property
    def weather_df(self) -> "DataFrame":
        """
        Return weather dataframe
        """
        return self._weather_df

    @weather_df.setter
    def weather_df(self, value: "DataFrame"):
        """
        Check if weather dataframe is in a correct format.
        """
        weather_df_columns = "Date MinTemp MaxTemp Precipitation ReferenceET".split(" ")
        if not all([column in value for column in weather_df_columns]):
            raise ValueError(
                "Error in weather_df format. Check if all the following columns exist "
                + "(Date MinTemp MaxTemp Precipitation ReferenceET)."
            )

        self._weather_df = value

    def _initialize(self) -> None:
        """
        Initialise all model variables
        """

        # Initialize ClockStruct object
        self._clock_struct = read_clock_paramaters(
            self.sim_start_time, self.sim_end_time
        )

        # get _weather_df data
        self.weather_df = read_weather_inputs(self._clock_struct, self.weather_df)

        # read model params
        self._clock_struct, self._param_struct = read_model_parameters(
            self._clock_struct, self.soil, self.crop, self.weather_df
        )

        # read irrigation management
        self._param_struct = read_irrigation_management(
            self._param_struct, self.irrigation_management, self._clock_struct
        )

        # read field management
        self._param_struct = read_field_management(
            self._param_struct, self.field_management, self.fallow_field_management
        )

        # read groundwater table
        self._param_struct = read_groundwater_table(
            self._param_struct, self.groundwater, self._clock_struct
        )

        # Compute additional variables
        self._param_struct.CO2 = self.co2_concentration
        self._param_struct = compute_variables(
            self._param_struct, self.weather_df, self._clock_struct
        )

        # read, calculate inital conditions
        self._param_struct, self._init_cond = read_model_initial_conditions(
            self._param_struct, self._clock_struct, self.initial_water_content
        )

        self._param_struct = create_soil_profile(self._param_struct)

        # Outputs results (water_flux, crop_growth, final_stats)
        self._outputs = Output(self._clock_struct.time_span, self._init_cond.th)

    def run_model(
        self,
        num_steps: int = 1,
        till_termination: bool = False,
        initialize_model: bool = True,
        process_outputs: bool = False,
        controlled_variables_func: Callable = None,
    ) -> bool:
        """
        This function is responsible for executing the model.

        Arguments:

            num_steps: Number of steps (Days) to be executed.

            till_termination: Run the simulation to completion

            initialize_model: Whether to initialize the model \
            (i.e., go back to beginning of season)

            process_outputs: process outputs into dataframe before \
                simulation is finished

        Returns:
            True if finished
        """

        if initialize_model:
            self._initialize()

        if till_termination:
            self.__start_model_execution = time.time()

            while self._clock_struct.model_is_finished is False:
                if controlled_variables_func is not None:
                    (
                        self._clock_struct,
                        self._init_cond,
                        self._param_struct,
                        self._outputs,
                    ) = controlled_variables_func(
                        self._clock_struct,
                        self._init_cond,
                        self._param_struct,
                        self._outputs,
                    )

                (
                    self._clock_struct,
                    self._init_cond,
                    self._param_struct,
                    self._outputs,
                ) = self._perform_timestep()
            self.__end_model_execution = time.time()
            self.__has_model_executed = True
            self.__has_model_finished = True
            return True
        else:
            if num_steps < 1:
                raise ValueError("num_steps must be equal to or greater than 1.")
            self.__start_model_execution = time.time()
            for i in range(num_steps):
                if (i == range(num_steps)[-1]) and (process_outputs is True):
                    self.__steps_are_finished = True

                (
                    self._clock_struct,
                    self._init_cond,
                    self._param_struct,
                    self._outputs,
                ) = self._perform_timestep()

                if self._clock_struct.model_is_finished:
                    self.__end_model_execution = time.time()
                    self.__has_model_executed = True
                    self.__has_model_finished = True
                    return True

            self.__end_model_execution = time.time()
            self.__has_model_executed = True
            self.__has_model_finished = False
            return True

    def _perform_timestep(
        self,
    ) -> Tuple["ClockStruct", "InitialCondition", "ParamStruct", "Output"]:
        """
        Function to run a single time-step (day) calculation of AquaCrop-OS
        """

        # extract _weather_df data for current timestep
        weather_step = _weather_data_current_timestep(
            self._weather_df, self._clock_struct.time_step_counter
        )

        # Get model solution_single_time_step
        new_cond, param_struct, outputs = solution_single_time_step(
            self._init_cond,
            self._param_struct,
            self._clock_struct,
            weather_step,
            self._outputs,
        )

        # Check model termination
        clock_struct = self._clock_struct
        clock_struct.model_is_finished = check_model_is_finished(
            self._clock_struct.step_end_time,
            self._clock_struct.simulation_end_date,
            self._clock_struct.model_is_finished,
            self._clock_struct.season_counter,
            self._clock_struct.n_seasons,
            new_cond.harvest_flag,
        )

        # Update time step
        clock_struct, _init_cond, param_struct = update_time(
            clock_struct, new_cond, param_struct, self._weather_df
        )

        # Create  _outputsdataframes when model is finished
        final_water_flux_growth_outputs = outputs_when_model_is_finished(
            clock_struct.model_is_finished,
            outputs.water_flux,
            outputs.water_storage,
            outputs.crop_growth,
            self.__steps_are_finished,
        )

        if final_water_flux_growth_outputs is not False:
            (
                outputs.water_flux,
                outputs.water_storage,
                outputs.crop_growth,
            ) = final_water_flux_growth_outputs

        return clock_struct, _init_cond, param_struct, outputs

    def get_simulation_results(self):
        """
        Return all the simulation results
        """
        if self.__has_model_executed:
            if self.__has_model_finished:
                return self._outputs.final_stats
            else:
                # If the model is not finished, the results are not generated.
                return False
        else:
            raise ValueError(
                "You cannot get results without running the model. "
                + "Please execute the run_model() method."
            )

    def get_water_storage(self):
        """
        Return water storage in soil results
        """
        if self.__has_model_executed:
            return self._outputs.water_storage
        else:
            raise ValueError(
                "You cannot get results without running the model. "
                + "Please execute the run_model() method."
            )

    def get_water_storage_chart(
        self,
        multiples_plots_joined: bool = False,
        show_chart: bool = True,
        save_chart: bool = False,
        save_path: str = None,
    ):
        """
        Return water storage in soil results
        TODO: It is a good idea to have a config files with column names
        """

        if save_chart and save_path is None:
            raise ValueError("You must provide a path to save the chart")

        water_storage_df = self.get_water_storage()

        # delete rows where not in growing season
        water_storage_df = water_storage_df[water_storage_df["growing_season"] == 1]

        water_storage_columns = water_storage_df.columns

        th_columns = [column for column in water_storage_columns if "th" in column]
        # create two charts, one with all water storage columns and one with only th columns

        date_formated = water_storage_df["date"].apply(
            lambda x: datetime.datetime.fromtimestamp(x)
        )

        size_soil_layers = self._param_struct.Soil.dz
        depth_each_layer = [
            round(sum(size_soil_layers[: i + 1]), 2)
            for i in range(len(size_soil_layers))
        ]

        if multiples_plots_joined:
            columns = 2

            rows = int(len(th_columns) / columns)

            fig, axs = plt.subplots(
                nrows=rows,
                ncols=columns,
                sharey=True,
                layout="constrained",
                figsize=(7, 10),
            )

            # for with int index for th_columns
            for index in range(len(th_columns)):
                # calculate column number using index and number of columns
                column_number = int(index % columns)
                # calculate row number using index and number of columns
                row_number = int(index / columns)

                axs[row_number, column_number].plot(
                    date_formated, water_storage_df[th_columns[index]]
                )

                # Title
                axs[row_number, column_number].set_title(
                    f"{th_columns[index]} - {depth_each_layer[index]} m"
                )

            fig.tight_layout()

        else:
            fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))
            index = 0
            for column in th_columns:
                # date from millisecond to datetime
                ax1.plot(
                    date_formated,
                    water_storage_df[column],
                    label=f"{column} - {depth_each_layer[index]} m",
                )
                index += 1

            ax1.set_xlabel("Date")
            ax1.set_ylabel("Water storage (mm)")
            # Add legend
            ax1.legend()

        if show_chart:
            plt.show()

        if save_chart:
            fig.savefig(save_path)

    def get_water_flux(self):
        """
        Return water flux results
        """
        if self.__has_model_executed:
            return self._outputs.water_flux
        else:
            raise ValueError(
                "You cannot get results without running the model. "
                + "Please execute the run_model() method."
            )

    WATER_FLUX_OPTIONS = Literal[
        "dap",
        "Wr",
        "z_gw",
        "surface_storage",
        "IrrDay",
        "Infl",
        "Runoff",
        "DeepPerc",
        "CR",
        "GwIn",
        "Es",
        "EsPot",
        "Tr",
        "TrPot",
    ]

    def get_water_flux_chart(
        self,
        single_plot: Literal[WATER_FLUX_OPTIONS] = False,  # Just one plot
        multiples_plots_joined: bool = False,  # all plots in the same fig
        multiples_plots_splited: bool = False,  # each plot in a different fig
        show_chart: bool = True,
        save_chart: bool = False,
        save_path: str = None,
    ):
        """
        Return water storage in soil results
        TODO: It is a good idea to have a config files with column names
        """

        water_flux = self._outputs.water_flux

        # delete rows where not dap
        water_flux = water_flux[water_flux["dap"] != 0]

        date_formated = water_flux["date"].apply(
            lambda x: datetime.datetime.fromtimestamp(x)
        )

        class StructItemForChart:
            def __init__(self, id, title, unit):
                self.id = id
                self.title = title
                self.unit = unit

        dap_chart = StructItemForChart(id="dap", title="DAP", unit="DAP")
        wr_chart = StructItemForChart(id="Wr", title="Soil Water Content", unit="mm")
        z_gw_chart = StructItemForChart(id="z_gw", title="Groundwater Depth", unit="m")
        surface_storage_chart = StructItemForChart(
            id="surface_storage", title="Surface Storage", unit="mm"
        )
        irrDay_chart = StructItemForChart(id="IrrDay", title="Irrigation", unit="mm")
        infl_chart = StructItemForChart(id="Infl", title="Infiltration", unit="mm")
        runoff_chart = StructItemForChart(id="Runoff", title="Runoff", unit="mm")
        deepPerc_chart = StructItemForChart(
            id="DeepPerc", title="Deep Percolation", unit="mm"
        )
        cr_chart = StructItemForChart(id="CR", title="Capilarity Rise", unit="mm")
        gwIn_chart = StructItemForChart(
            id="GwIn", title="Groundwater Inflow", unit="mm"
        )
        es_chart = StructItemForChart(id="Es", title="Surface evaporation", unit="mm")
        esPot_chart = StructItemForChart(
            id="EsPot", title="Potential surface evaporation", unit="mm"
        )
        tr_chart = StructItemForChart(id="Tr", title="Transpiration", unit="mm")
        trPot_chart = StructItemForChart(
            id="TrPot", title="Potential Transpiration", unit="mm"
        )

        charts = [
            dap_chart,
            wr_chart,
            z_gw_chart,
            surface_storage_chart,
            irrDay_chart,
            infl_chart,
            runoff_chart,
            deepPerc_chart,
            cr_chart,
            gwIn_chart,
            es_chart,
            esPot_chart,
            tr_chart,
            trPot_chart,
        ]
        if single_plot:
            if not single_plot in get_args(self.WATER_FLUX_OPTIONS):
                raise ValueError(
                    f"Invalid option {single_plot}, please choose one of {self.WATER_FLUX_OPTIONS}"
                )

            # select chart where id is equal to single_plot
            chart = next((chart for chart in charts if chart.id == single_plot), None)

            fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))
            ax1.plot(date_formated, water_flux[chart.id], label=chart.title)
            # TODO: IFINISH THID
            ax1.set_xlabel("Date")
            ax1.set_ylabel(f"{chart.title} ({chart.unit})")
            # Add legend
            ax1.legend()

        elif multiples_plots_joined:
            columns = 2
            rows = int(len(charts) / columns)

            fig, axs = plt.subplots(
                nrows=rows, ncols=columns, layout="constrained", figsize=(7, 10)
            )

            for index in range(len(charts)):
                column_number = int(index % columns)
                row_number = int(index / columns)

                axs[row_number, column_number].plot(
                    date_formated, water_flux[charts[index].id]
                )
                axs[row_number, column_number].set_title(charts[index].title)

            fig.tight_layout()

        elif multiples_plots_splited:
            fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))
            for chart in charts:
                ax1.plot(date_formated, water_flux[chart.id], label=chart.title)
            # TODO: FINISH THIS
            ax1.set_xlabel("Date")
            ax1.set_ylabel("Water storage (mm)")
            # Add legend
            ax1.legend()

        else:
            raise ValueError("Please choose one of the options")

        if show_chart:
            plt.show()

        if save_chart:
            fig.savefig(save_path)

        print("done")

    def get_crop_growth(self):
        """
        Return crop growth results
        """
        if self.__has_model_executed:
            return self._outputs.crop_growth
        else:
            raise ValueError(
                "You cannot get results without running the model. "
                + "Please execute the run_model() method."
            )

    CROP_GROWTH_OPTIONS = Literal[
        "dap",
        "gdd",
        "gdd_cum",
        "z_root",
        "canopy_cover",
        "canopy_cover_ns",
        "biomass",
        "biomass_ns",
        "harvest_index",
        "harvest_index_adj",
        "yield_",
    ]

    CROP_GROWTH_OPTIONS = Literal[
        "dap",
        "gdd",
        "gdd_cum",
        "z_root",
        "canopy_cover",
        "canopy_cover_ns",
        "biomass",
        "biomass_ns",
        "harvest_index",
        "harvest_index_adj",
        "yield_",
    ]

    def get_crop_growth_chart(
        self,
        single_plot: Literal[WATER_FLUX_OPTIONS] = False,  # Just one plot
        multiples_plots_joined: bool = False,  # all plots in the same fig
        multiples_plots_splited: bool = False,  # each plot in a different fig
        show_chart: bool = True,
        save_chart: bool = False,
        save_path: str = None,
    ):
        """
        Return water storage in soil results
        TODO: It is a good idea to have a config files with column names
        """

        crop_growth = self._outputs.crop_growth

        # delete rows where not dap
        crop_growth = crop_growth[crop_growth["dap"] != 0]

        date_formated = crop_growth["date"].apply(
            lambda x: datetime.datetime.fromtimestamp(x)
        )

        class StructItemForChart:
            def __init__(self, id, title, unit):
                self.id = id
                self.title = title
                self.unit = unit

        dap_chart = StructItemForChart(id="dap", title="DAP", unit="DAP")
        gdd_chart = StructItemForChart(
            id="gdd", title="growing degree-days", unit="days"
        )
        gdd_cum_chart = StructItemForChart(
            id="gdd_cum", title="growing degree-day cum", unit="days"
        )
        z_root_chart = StructItemForChart(id="z_root", title="Roots depth", unit="mm")
        canopy_cover_chart = StructItemForChart(
            id="canopy_cover", title="Canopy Cover", unit="%"
        )
        canopy_cover_ns_chart = StructItemForChart(
            id="canopy_cover_ns", title="Canopy Cover Not Stressed", unit="mm"
        )
        biomass_chart = StructItemForChart(id="biomass", title="Biomass", unit="kg/ha")
        biomass_ns_chart = StructItemForChart(
            id="biomass_ns", title="Biomass Not Stressed", unit="kg/ha"
        )
        harvest_index_chart = StructItemForChart(
            id="harvest_index", title="Harvest Index", unit=""
        )
        harvest_index_adj_chart = StructItemForChart(
            id="harvest_index_adj", title="Harvest Index Adjusted", unit=""
        )
        yield_chart = StructItemForChart(id="yield_", title="Yield", unit="kg/ha")

        charts = [
            dap_chart,
            gdd_chart,
            gdd_cum_chart,
            z_root_chart,
            canopy_cover_chart,
            canopy_cover_ns_chart,
            biomass_chart,
            biomass_ns_chart,
            harvest_index_chart,
            harvest_index_adj_chart,
            yield_chart,
        ]

        if single_plot:
            if not single_plot in get_args(self.CROP_GROWTH_OPTIONS):
                raise ValueError(
                    f"Invalid option {single_plot}, please choose one of {self.CROP_GROWTH_OPTIONS}"
                )

            # select chart where id is equal to single_plot
            chart = next((chart for chart in charts if chart.id == single_plot), None)

            fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))
            ax1.plot(date_formated, crop_growth[chart.id], label=chart.title)
            # TODO: IFINISH THID
            ax1.set_xlabel("Date")
            ax1.set_ylabel(f"{chart.title} ({chart.unit})")
            # Add legend
            ax1.legend()

        elif multiples_plots_joined:
            columns = 2
            rows = int(round(len(charts) / columns, 0))

            fig, axs = plt.subplots(
                nrows=rows, ncols=columns, layout="constrained", figsize=(7, 10)
            )

            for index in range(len(charts)):
                column_number = int(index % columns)
                row_number = int(index / columns)

                axs[row_number, column_number].plot(
                    date_formated, crop_growth[charts[index].id]
                )
                axs[row_number, column_number].set_title(charts[index].title)

            fig.tight_layout()

        elif multiples_plots_splited:
            fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))
            for chart in charts:
                ax1.plot(date_formated, crop_growth[chart.id], label=chart.title)
            # TODO: FINISH THIS
            ax1.set_xlabel("Date")
            ax1.set_ylabel("Water storage (mm)")
            # Add legend
            ax1.legend()

        else:
            raise ValueError("Please choose one of the options")

        if show_chart:
            plt.show()

        if save_chart:
            fig.savefig(save_path)

        print("done")

    WEATHER_DATA_OPTIONS = Literal[
        "Date", "MinTem", "MaxTemp", "Precipitation", "ReferenceET"
    ]

    def get_weather_chart(
        self,
        single_plot: Literal[WEATHER_DATA_OPTIONS] = False,  # Just one plot
        multiples_plots_joined: bool = False,  # all plots in the same fig
        multiples_plots_splited: bool = False,  # each plot in a different fig
        show_chart: bool = True,
        save_chart: bool = False,
        save_path: str = None,
    ):
        """
        Return weather results
        """

        weather_df = self._weather_df

        date_formated = weather_df["Date"].apply(
            lambda x: datetime.datetime.fromtimestamp(x)
        )

        class StructItemForChart:
            def __init__(self, id, title, unit):
                self.id = id
                self.title = title
                self.unit = unit

        min_temp_chart = StructItemForChart(
            id="MinTemp", title="Min Temperature", unit="ºC"
        )
        max_temp_chart = StructItemForChart(
            id="MaxTemp", title="Max Temperature", unit="ºC"
        )
        precipitation_chart = StructItemForChart(
            id="Precipitation", title="Precipitation", unit="mm"
        )
        reference_et_chart = StructItemForChart(
            id="ReferenceET", title="Reference Evapotranspiration", unit="mm"
        )

        charts = [
            min_temp_chart,
            max_temp_chart,
            precipitation_chart,
            reference_et_chart,
        ]

        if single_plot:
            if not single_plot in get_args(self.WEATHER_DATA_OPTIONS):
                raise ValueError(
                    f"Invalid option {single_plot}, please choose one of {self.WEATHER_DATA_OPTIONS}"
                )

            # select chart where id is equal to single_plot
            chart = next((chart for chart in charts if chart.id == single_plot), None)

            fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))
            ax1.plot(date_formated, weather_df[chart.id], label=chart.title)
            # TODO: IFINISH THID
            ax1.set_xlabel("Date")
            ax1.set_ylabel(f"{chart.title} ({chart.unit})")
            # Add legend
            ax1.legend()

        elif multiples_plots_joined:
            columns = 2
            rows = int(round(len(charts) / columns, 0))

            fig, axs = plt.subplots(
                nrows=rows, ncols=columns, layout="constrained", figsize=(7, 10)
            )

            for index in range(len(charts)):
                column_number = int(index % columns)
                row_number = int(index / columns)

                axs[row_number, column_number].plot(
                    date_formated, weather_df[charts[index].id]
                )
                axs[row_number, column_number].set_title(charts[index].title)

            fig.tight_layout()

        elif multiples_plots_splited:
            fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))
            for chart in charts:
                ax1.plot(date_formated, weather_df[chart.id], label=chart.title)
            # TODO: FINISH THIS
            ax1.set_xlabel("Date")
            ax1.set_ylabel("Water storage (mm)")
            # Add legend
            ax1.legend()

        else:
            raise ValueError("Please choose one of the options")

        if show_chart:
            plt.show()

        if save_chart:
            fig.savefig(save_path)

        print("done")

    def get_additional_information(self) -> Dict[str, Union[bool, float]]:
        """
        Additional model information.

        Returns:
            dict: {has_model_finished,execution_time}

        """
        if self.__has_model_executed:
            return {
                "has_model_finished": self.__has_model_finished,
                "execution_time": self.__end_model_execution
                - self.__start_model_execution,
            }
        else:
            raise ValueError(
                "You cannot get results without running the model. "
                + "Please execute the run_model() method."
            )


def _sim_date_format_is_correct(date: str) -> bool:
    """
    This function checks if the start or end date of the simulation is in the correct format.

    Arguments:
        date

    Return:
        boolean: True if the date is correct.
    """
    format_dates_string = "%Y/%m/%d"
    try:
        datetime.datetime.strptime(date, format_dates_string)
        return True
    except ValueError:
        return False


def _weather_data_current_timestep(_weather_df, time_step_counter):
    """
    Extract _weather_df data for current timestep
    """
    weather_step = _weather_df.iloc[time_step_counter]

    weather_dict = {
        "Date": weather_step["Date"],
        "MinTemp": weather_step["MinTemp"],
        "MaxTemp": weather_step["MaxTemp"],
        "Precipitation": weather_step["Precipitation"],
        "ReferenceET": weather_step["ReferenceET"],
    }
    return weather_dict
