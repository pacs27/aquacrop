import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from numpy import ndarray

def outputs_when_model_is_finished(
    model_is_finished: bool,
    flux_output: "ndarray",
    water_output: "ndarray",
    growth_outputs: "ndarray",
    steps_are_finished: bool,
):
    """
    Function that turns numpy array outputs into pandas dataframes

    Arguments:

        model_is_finished (bool):  is model finished

        flux_output (numpy.array): water flux_output

        water_output (numpy.array):  water storage in each compartment

        growth_outputs (numpy.array):  crop growth variables

        n_seasons (int):  total number of seasons being simulated

        steps_are_finished (bool):  have the simulated num_steps finished

    Returns:

        flux_output (pandas.DataFrame): water flux_output

        water_output (pandas.DataFrame):  water storage in each compartment

        growth_outputs (pandas.DataFrame):  crop growth variables


    """
    if model_is_finished is True or steps_are_finished is True:
        # ClockStruct.step_start_time = ClockStruct.step_end_time
        # ClockStruct.step_end_time = ClockStruct.step_end_time + np.timedelta64(1, "D")
        flux_output_df = pd.DataFrame(
            flux_output,
            columns=[
                "time_step_counter",
                "date",
                "season_counter",
                "dap",
                "Wr", # Soil water content in the root zone expressed as an equivalent depth mm.
                "depletion_root_zone",
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
            ],
        )

        water_output_columns_first_columns = ["time_step_counter", "date", "growing_season", "dap"]
        number_of_compartments = water_output.shape[1] - len(water_output_columns_first_columns)
        compartments_columns = ["th" + str(i) for i in range(1, number_of_compartments+1)]
        
        water_output_df = pd.DataFrame(
            water_output,
            columns=water_output_columns_first_columns + compartments_columns,
        )

        growth_outputs_df = pd.DataFrame(
            growth_outputs,
            columns=[
                "time_step_counter",
                "date",
                "season_counter",
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
                "is_stomatal_closed"
            ],
        )

        return flux_output_df, water_output_df, growth_outputs_df

    return False
