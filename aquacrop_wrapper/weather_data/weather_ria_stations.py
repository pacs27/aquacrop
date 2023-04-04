from ria import RIA

import pandas as pd
import datetime
import copy
# import statistics
import pandas as pd

try:
    from constants import AquacropConstants
except ImportError:
    from ..constants import AquacropConstants

ria = RIA()

print(ria.listar_todas_estaciones_en_una_provincia(14))

ria.obtener_datos_dia(14, 1, "2023-03-21")


class WeatherRIAStations():
    def __init__(self):
        self.ria = RIA()

    def get_weather_df(self, start_simulation_date, end_simulation_date,  start_year,
                       end_year, province_id, station_id,
                       complete_type: AquacropConstants.COMPLETE_WEATHER_DATA_TYPE.keys(),
                       complete_values_method: AquacropConstants.COMPLETE_WEATHER_DATA_METHOD.keys(),
                       complete_data=False):
        # TODO: CHECK IF THE WEATHER IS THE SAME AS THE COMPLETE ONE, IF ITS USE THE SAME DATA, IF NOT, CREATE TWO CALLS TO RIA WSTATIONS.
        # dIFFERENCIATE BETWEEN START_SIM_DATE AND WEATHER_START_DATES
        """Get weather data from RIA API
        Args:
            start_simulation_date (_type_): initial date of the simulation (format: YYYY-MM-DD)
            end_simulation_date (_type_): end date of the simulation (format: YYYY-MM-DD)
            start_year (_type_): start year of the period where the weather data is used
            end_year (_type_): end year of the period where the weather data is used
            province_id (_type_): id of the province
            station_id (_type_): id of the station
            complete_data (_type_): if True, the data will be completed with the last year data
            complete_type (_type_): type of data to complete the data (last_year or last_n_years)
            number_of_years (_type_): number of years to complete the data
            complete_values_method (_type_): method to complete the data (mean or rainest, driest)


        Returns:
            _type_: json file with the weatherdata
        """
        # data change caracter / to -
        initial_simulation_day = start_simulation_date.replace("/", "-")
        end_simulation_day = end_simulation_date.replace("/", "-")

        json_weather_data = self.ria.obtener_datos_diarios_periodo_con_et0(
            provincia_id=province_id, estacion_id=station_id,
            fecha_inicio=initial_simulation_day, fecha_fin=end_simulation_day)

        weather_df = pd.DataFrame(json_weather_data)

        if (complete_data):
            if not complete_type in AquacropConstants.COMPLETE_WEATHER_DATA_TYPE.keys():
                raise ValueError(
                    f"Complete type not valid. Valid values are: {AquacropConstants.COMPLETE_WEATHER_DATA_TYPE.keys()}")

            if complete_type == "last_year_data":
                weather_df = self.complete_data_with_last_year(
                    weather_df, province_id, station_id, end_simulation_date)
            elif complete_type == "last_n_years":
                weather_df = self.complete_data_with_selected_years(
                    start_year, end_year, weather_df, province_id, station_id, end_simulation_date, complete_values_method)

        return weather_df

    def complete_data_with_last_year(self, weather_df, province_id, station_id, end_simulation_date):
        """This method complete the weather data with the last year data.

        Args:
            weather_df (_type_): weather dataframe
            province_id (_type_):   id of the province
            station_id (_type_):    id of the station
            end_simulation_date (_type_):   end date of the simulation (format: YYYY-MM-DD)

        Returns:
            _type_: _description_
        """

        today_date = datetime.datetime.now()
        last_year = today_date.year - 1

        weather_df_last_year = self.complete_data_with_selected_years(
            start_year=last_year-1,
            end_year=last_year,
            weather_df=weather_df,
            province_id=province_id,
            station_id=station_id,
            end_simulation_date=end_simulation_date)

        return weather_df_last_year

    def complete_data_with_selected_years(self,
                                          start_year,
                                          end_year,
                                          weather_df,
                                          province_id,
                                          station_id,
                                          end_simulation_date,
                                          complete_values_method: AquacropConstants.COMPLETE_WEATHER_DATA_METHOD.keys()):
        """This method is quite important. It complete the weather data with the last year data.
            When the simulation is running in future dates, the weather data, of course, is not available.
            It is necessary to complete the weather data with a selected year, so this method is used to complete the weather data.
        Args:
            start_year (_type_): start year of the period where the weather data is used
            end_year (_type_): end year of the period where the weather data is used
            weather_df (_type_): weather dataframe
            province_id (_type_): id of the province
            station_id (_type_): id of the station
            end_simulation_date (_type_): end date of the simulation (format: YYYY-MM-DD)

        Returns:
            _type_: json file with the weatherdata
        """
        today_date = datetime.datetime.now()

        # check if year_of_the_weather_data AND today_date.year are the same or more
        if end_year >= today_date.year:
            raise Exception(
                "The year of the weather data must be less than the current year")

        # # CALCULATE THE DAYS UNTIL 31 OF DECEMBER FORM TODAY
        # days_to_end_the_year =  today_date - datetime.datetime(today_date.year, 12, 31)

        number_of_days_between_today_and_last_date = (
            datetime.datetime.strptime(end_simulation_date, "%Y/%m/%d") - today_date).days

        historic_weather_df = self.get_weather_dataframe(
            start_year=start_year, end_year=end_year, ria_province_id=province_id, ria_station_id=station_id, complete_values_method=complete_values_method)

       # CREATE LEAP YEAR AND NOT LEAP YEAR DATA TO USE IT IN ALL THE SUTUATIONS

        # Leap year
        if not self.check_if_a_year_is_leap(historic_weather_df["fecha"].iloc[0].year
                                            ):
            weather_df_leap = self._create_weather_df_with_29_2(
                historic_weather_df)
        else:
            weather_df_leap = historic_weather_df

        # No leap year
        if not self.check_if_a_year_is_leap(historic_weather_df["fecha"].iloc[0].year):
            weather_df_no_leap = historic_weather_df
        else:
            weather_df_no_leap = self._remove_29_2_from_weather_data(
                historic_weather_df)

        # iterate over all days between today and last date
        day_date = today_date

        # This for iterate over all the simulation days to create the weather dataframe using
        # last year weather data
        # TODO: This is too slow. It is necessary to improve this
        for _ in range(0, number_of_days_between_today_and_last_date+2):
            # check if year is leap year to select the correct weather dataframe
            if self.check_if_a_year_is_leap(day_date.year):
                weather_data_last_year = weather_df_leap
            else:
                weather_data_last_year = weather_df_no_leap

            # copy the same day in last year weather data
            current_day_of_the_year = day_date.timetuple().tm_yday

            # Copy to doesnt change the date value in the item
            weather_df_last_year_item = copy.deepcopy(
                weather_data_last_year.loc[weather_data_last_year['dia'] == current_day_of_the_year])
            # change the date
            weather_df_last_year_item["fecha"] = pd.to_datetime(day_date)

            # adding days to the json weather date
            # weather_df.loc[len(weather_df)] = weather_df_last_year_item
            weather_df = pd.concat([weather_df, weather_df_last_year_item], ignore_index=True)

            print(_)
            # Next day date
            day_date = day_date + datetime.timedelta(days=1)

        return weather_df

    def get_weather_dataframe(self, start_year, end_year, ria_province_id, ria_station_id, complete_values_method):
        # start_date = f"{year_of_the_weather_data}-01-01"
        # end_date = f"{year_of_the_weather_data+1}-01-01"
        # end_year should be less than start_year

        if not complete_values_method in AquacropConstants.COMPLETE_WEATHER_DATA_METHOD.keys():
            raise Exception(
                f"The complete_values_method must be one of the following: {AquacropConstants.COMPLETE_WEATHER_DATA_METHOD.keys()}")

        today_date = datetime.datetime.now()
        if end_year <= start_year:
            raise Exception(
                "The end year must be less than the start year")

        # end year date should be less than today date
        if end_year >= today_date.year:
            raise Exception(
                "The end year must be less than the current year")

        json_weather_data_last_year = self.ria.obtener_datos_diarios_periodo_con_et0(
            provincia_id=ria_province_id, estacion_id=ria_station_id,
            fecha_inicio=f"{start_year}-01-01", fecha_fin=f"{end_year}-12-31")

        # TODO: Is better to create a list of type: `weather_complete_type``
        weather_year_df = pd.DataFrame(json_weather_data_last_year)

        if complete_values_method == "means":
            weather_year_df = self.get_means_from_weather_data(
                weather_year_df)

        elif complete_values_method == "driest_year":
            weather_year_df = self.get_the_driest_year(
                weather_year_df)

        elif complete_values_method == "rainest_year":
            weather_year_df = self.get_the_driest_year(
                weather_year_df)

        return weather_year_df

    def get_means_from_weather_data(self, weather_year_df):
        """
        This method take a dataframe, calculates the mean for each day of the year, 
        and returns a dataframe with the mean values

        Args:
            weather_year_df (pd.Dataframe): weather dataframe

        Returns:
            pd.Dataframe: _description_
        """

        # sum item where dia column is the same and get the mean. Preserve the fehca column
        weather_df_dia_sum = weather_year_df.groupby(['dia']).mean()

        # create a date column with the day of the year taking into account the leap year
        weather_df_dia_sum['fecha'] = weather_df_dia_sum.index.map(
            lambda day: self.get_date_using_julian_day(day_of_the_year=day, is_year_leap=True))

        weather_df_dia_sum = weather_df_dia_sum.reset_index()

        return weather_df_dia_sum

    def get_the_driest_year(self, weather_year_df):
        """This method take a dataframe, calculates the total irrigation for each  year, and selects the data of the driest year

        Args:
            weather_year_df (pd.Dataframe): The weather dataframe

        Returns:
            pd.Dataframe: The driest year weather dataframe
        """

        weather_year_df['fecha'] = pd.to_datetime(weather_year_df['fecha'])

        precipitation_df = weather_year_df.loc[:, ['precipitacion']]

        precipitation_df["year"] = weather_year_df["fecha"].apply(
            lambda fecha: fecha.year)

        precipitation_df = precipitation_df.groupby("year").sum()

        driest_year = precipitation_df['precipitacion'].idxmin()

        weather_filtered_df = weather_year_df[weather_year_df['fecha'].dt.year == driest_year]

        weather_filtered_df = weather_filtered_df.reset_index()

        return weather_filtered_df

    def get_rainest_year(self, weather_year_df):
        """This method take a dataframe, calculates the total irrigation for each  year, and selects the data of the driest year

        Args:
            weather_year_df (pd.Dataframe): The weather dataframe

        Returns:
            pd.Dataframe: _description_
        """

        weather_year_df['fecha'] = pd.to_datetime(weather_year_df['fecha'])

        precipitation_df = weather_year_df.loc[:, ['precipitacion']]

        precipitation_df["year"] = weather_year_df["fecha"].apply(
            lambda fecha: fecha.year)

        precipitation_df = precipitation_df.groupby("year").sum()

        driest_year = precipitation_df['precipitacion'].idxmax()

        weather_filtered_df = weather_year_df[weather_year_df['fecha'].dt.year == driest_year]

        weather_filtered_df = weather_filtered_df.reset_index()

        return weather_filtered_df

    def get_date_using_julian_day(self, day_of_the_year, is_year_leap=True):
        """This method calculate the date using the julian day and the year

        Args:
            day_of_the_year (_type_): The day of the year (1-365)
            is_year_leap (bool, optional): If year is leap, 29-02 is taken into account. Defaults to True.

        Returns:
            _type_: _description_
        """
        # using julian date and leap year to get the date
        leap_year = 2020
        no_leap_year = 2019
        if is_year_leap:
            first_day_year_date = datetime.datetime(leap_year, 1, 1)
            date = first_day_year_date + \
                datetime.timedelta(day_of_the_year - 1)
        else:
            first_day_year_date = datetime.datetime(no_leap_year, 1, 1)
            date = first_day_year_date + \
                datetime.timedelta(day_of_the_year - 1)

        return date

    @staticmethod
    def _create_weather_df_with_29_2(weather_df):
        """Add 29-2 to weather data
        Args:
            json_weather_data_last_year (_type_): json file with the weatherdata

        Returns:
            _type_: json file with the weatherdata
        """
        year = weather_df['fecha'].dt.year.unique()[0]

       # find 28-2 in json_weather_data_last_year
        weather_df_28_2 = weather_df[weather_df['fecha'] == f"{year}-02-28"]
        # create 29-2
        weather_df_29_2 = weather_df_28_2.copy()
        # add weather_df_29_2 after 28-02 date
        weather_df_29_2['fecha'] = f"{year}-02-29"
        # add 29-2 to json_weather_data_last_year
        weather_df = weather_df.append(weather_df_29_2)

        weather_df = weather_df.reset_index(drop=True)
        weather_df.index = weather_df.index + 1

        return weather_df

    def _remove_29_2_from_weather_data(self, weather_df):
        """Remove 29-2 from weather data
        Args:
            json_weather_data_last_year (_type_): json file with the weatherdata

        Returns:
            _type_: json file with the weatherdata
        """
        # remove 29-2 from weather_df
        year = weather_df['fecha'].dt.year.unique()[0]
        weather_df = weather_df[weather_df['fecha']
                                != f"{year}-02-29"].reset_index(drop=True)
        weather_df.index = weather_df.index + 1

        return weather_df

    @staticmethod
    def check_if_a_year_is_leap(year):
        """Check if a year is leap
        Args:
            year (_type_): year to check

        Returns:
            _type_: True if the year is leap, False if not
        """
        if year % 4 == 0:
            if year % 100 == 0:
                if year % 400 == 0:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    @staticmethod
    def transform_data_into_aquacrop_format(json_weather_data):
        """Transform json data into aquacrop format
        Args:
            json_weather_data (_type_): json file with the weatherdata

        Returns:
            _type_: pandas dataframe with the weatherdata
        """
        weather_df = pd.DataFrame(
            json_weather_data,
            columns=["fecha", "tempMin", "tempMax", "precipitation", "et0"],
        )

        weather_df["precipitation"] = weather_df["precipitation"].fillna(0.00)

        weather_df.rename(
            columns={
                "tempMin": "MinTemp",
                "tempMax": "MaxTemp",
                "precipitation": "Precipitation",
                "et0": "ReferenceET",
            },
            inplace=True,
        )

        # set limit on ET0 to avoid divide by zero errors
        weather_df.ReferenceET.clip(lower=0.1, inplace=True)

        # Fill missing date values with the previous value
        weather_df.index = pd.DatetimeIndex(weather_df["fecha"]).floor("D")
        weather_df = weather_df.resample("D").mean().fillna(method="ffill")

        # Create Date column
        weather_df["Date"] = weather_df.index

        # Change index from date to row number
        weather_df.index = range(len(weather_df))

        return weather_df
