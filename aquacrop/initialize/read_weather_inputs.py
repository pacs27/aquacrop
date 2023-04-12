"""
Initialize weather data
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.clockStruct import ClockStruct
    from pandas import DataFrame

def read_weather_inputs(
    clock_sctruct: "ClockStruct",
    weather_df: "DataFrame") -> "DataFrame":
    """
    Clip weather to start and end simulation dates

    Arguments:

        clock_sctruct (ClockStruct): ClockStruct object

        weather_df (DataFrame): weather dataframe

    Returns:

        weather_df (DataFrame): clipped weather dataframe

    """

    # get the start and end dates of simulation
    start_date = clock_sctruct.simulation_start_date
    end_date = clock_sctruct.simulation_end_date

    if weather_df.Date.iloc[0] > start_date:
        raise ValueError(
            "The first date of the climate data cannot be longer than the start date of the model."
        )

    if weather_df.Date.iloc[-1] < end_date:
        raise ValueError(
            "The model end date cannot be longer than the last date of climate data."
        )

    # remove weather data outside of simulation dates
    weather_df = weather_df[weather_df.Date >= start_date]
    weather_df = weather_df[weather_df.Date <= end_date]
    
    # Fill missing days
    weather_df = weather_df.set_index('Date')
    ## delete duplicated dates
    weather_df = weather_df[~weather_df.index.duplicated(keep='first')]
    weather_df = weather_df.asfreq('D')
    weather_df = weather_df.fillna(method='ffill')
    weather_df = weather_df.reset_index()
    

    return weather_df
