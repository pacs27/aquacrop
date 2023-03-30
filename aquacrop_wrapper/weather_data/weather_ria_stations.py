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

    def get_json_data(self, initial_date, end_date, province_id, station_id, complete_data=False, complete_type: AquacropConstants.COMPLETE_WEATHER_DATA_TYPE.keys() = "last_year_data", number_of_years=1):
        """Get weather data from RIA API
        Args:
            initial_date (_type_): initial date of the period (format: YYYY-MM-DD)
            end_date (_type_): end date of the period (format: YYYY-MM-DD)
            province_id (_type_): id of the province
            station_id (_type_): id of the station
            complete_data (_type_): if True, the data will be completed with the last year data
            complete_type (_type_): type of data to complete the data (last_year or last_n_years)
            number_of_years (_type_): number of years to complete the data


        Returns:
            _type_: json file with the weatherdata
        """
        # data change caracter / to -
        fecha_inicio = initial_date.replace("/", "-")
        fecha_fin = end_date.replace("/", "-")

        json_weather_data = self.ria.obtener_datos_diarios_periodo_con_et0(
            provincia_id=province_id, estacion_id=station_id,
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

        if (complete_data):
            if not complete_type in AquacropConstants.COMPLETE_WEATHER_DATA_TYPE.keys():
                raise ValueError(
                    f"Complete type not valid. Valid values are: {AquacropConstants.COMPLETE_WEATHER_DATA_TYPE.keys()}")

            if complete_type == "last_year_data":
                json_weather_data = self.complete_data_with_last_year(
                    json_weather_data, province_id, station_id, fecha_inicio, fecha_fin)

        return json_weather_data

    def complete_data_with_last_year(self, json_weather_data, province_id, station_id, fecha_inicio, fecha_fin):

        today_date = datetime.datetime.now()
        last_year = today_date.year - 1

        # TODO: Delete -2
        json_weather_data = self.complete_data_with_a_selected_year(
            start_year=last_year-2,
            end_year=last_year,
            json_weather_data=json_weather_data,
            province_id=province_id,
            station_id=station_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin)

        return json_weather_data

    def complete_data_with_a_selected_year(self,
                                           start_year,
                                           end_year,
                                           json_weather_data,
                                           province_id,
                                           station_id,
                                           fecha_inicio,
                                           fecha_fin):
        """This method is quite important. It complete the weather data with the last year data.
            When the simulation is running in future dates, the weather data, of course, is not available.
            It is necessary to complete the weather data with a selected year, so this method is used to complete the weather data.
        Args:
            json_weather_data (_type_): json file with the weatherdata

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
            datetime.datetime.strptime(fecha_fin, "%Y-%m-%d") - today_date).days

        json_weather_data_last_year = self.get_json_with_weather_data(
            start_year=start_year, end_year=end_year, ria_province_id=province_id, ria_station_id=station_id)

        # json_weather_data_last_year = self.ria.obtener_datos_diarios_periodo_con_et0(
        #     provincia_id=province_id, estacion_id=station_id,
        #     fecha_inicio=f"{year_of_the_weather_data}-01-01", fecha_fin=f"{year_of_the_weather_data+1}-01-01")

        # CREATE LEAP YEAR AND NOT LEAP YEAR DATA TO USE IT IN ALL THE SUTUATIONS

        # Leap year
        if not self.check_if_a_year_is_leap(year_of_the_weather_data):
            json_weather_data_last_year_leap = self.create_a_weather_data_with_29_2(
                json_weather_data_last_year)
        else:
            json_weather_data_last_year_leap = json_weather_data_last_year

        # No leap year
        if not self.check_if_a_year_is_leap(year_of_the_weather_data):
            pass
        else:
            json_weather_data_last_year_leap = self.remove_29_2_from_weather_data(
                json_weather_data_last_year)

        # iterate over all days between today and last date
        day_date = today_date

        # This for iterate over all the simulation days to create the weather dataframe using
        # last year weather data
        for _ in range(0, number_of_days_between_today_and_last_date+2):
            # check if year is leap year to select the correct weather dataframe
            if self.check_if_a_year_is_leap(day_date.year):
                weather_data_last_year = json_weather_data_last_year_leap
            else:
                weather_data_last_year = json_weather_data_last_year

            # copy the same day in last year weather data
            current_day_of_the_year = day_date.timetuple().tm_yday
            # Copy to doesnt change the date value in the item
            json_weather_last_year_item = copy.deepcopy(
                weather_data_last_year[current_day_of_the_year - 1])
            # change the date
            json_weather_last_year_item["fecha"] = day_date.strftime(
                "%Y-%m-%d")

            # adding days to the json weather date
            json_weather_data.append(json_weather_last_year_item)

            # Next day date
            day_date = day_date + datetime.timedelta(days=1)

        return json_weather_data

    def get_weather_dataframe(self, start_year, end_year, ria_province_id, ria_station_id, get_means=True, get_driest_year=False, get_rainest_year=False):
        # start_date = f"{year_of_the_weather_data}-01-01"
        # end_date = f"{year_of_the_weather_data+1}-01-01"
        # end_year should be less than start_year

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
        
        #TODO: Is better to create a list of type: `weather_complete_type``
        weather_year_df = pd.DataFrame(json_weather_data_last_year)


        if get_means:
            weather_year_df = self.get_means_from_weather_data(
                weather_year_df)
        
        if get_driest_year:
             weather_year_df = self.get_the_driest_year(
                weather_year_df)
             
        if get_rainest_year:
            weather_year_df = self.get_the_driest_year(
                weather_year_df)

    def get_means_from_weather_data(self, weather_year_df):

        # sum item where dia column is the same and get the mean. Preserve the fehca column
        weather_df_dia_sum = weather_year_df.groupby(['dia']).mean()

        # create a date column with the day of the year taking into account the leap year
        weather_df_dia_sum['fecha'] = weather_df_dia_sum.index.map(
            lambda day: self.get_date_using_julian_day(day_of_the_year=day, is_year_leap=True))

        return weather_df_dia_sum
    
    def get_the_driest_year(self, weather_year_df):
        
        weather_year_df['fecha'] = pd.to_datetime(weather_year_df['fecha'])

        precipitation_df = weather_year_df.loc[:, ['precipitacion']]
        
        precipitation_df["year"] = weather_year_df["fecha"].apply(lambda fecha: fecha.year)
        
        precipitation_df = precipitation_df.groupby("year").sum()
        
        driest_year = precipitation_df['precipitacion'].idxmin()
        
        weather_filtered_df = weather_year_df[weather_year_df['fecha'].dt.year == driest_year]
        
        
        return weather_filtered_df
    
    def get_rainest_year(self, weather_year_df):
        
        weather_year_df['fecha'] = pd.to_datetime(weather_year_df['fecha'])

        precipitation_df = weather_year_df.loc[:, ['precipitacion']]
        
        precipitation_df["year"] = weather_year_df["fecha"].apply(lambda fecha: fecha.year)
        
        precipitation_df = precipitation_df.groupby("year").sum()
        
        driest_year = precipitation_df['precipitacion'].idxmax()
        
        weather_filtered_df = weather_year_df[weather_year_df['fecha'].dt.year == driest_year]
        
        return weather_filtered_df

        

    def get_date_using_julian_day(self, day_of_the_year, is_year_leap=True):
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
    def create_a_weather_data_with_29_2(json_weather_data_last_year):
        """Add 29-2 to weather data
        Args:
            json_weather_data_last_year (_type_): json file with the weatherdata

        Returns:
            _type_: json file with the weatherdata
        """
        year = json_weather_data_last_year[0]["fecha"].split("-")[0]

       # find 28-2 in json_weather_data_last_year
        json_weather_data_28_2 = [
            d for d in json_weather_data_last_year if "02-28" in d["fecha"]][0]
        json_weather_data_28_2_copy = copy.deepcopy(json_weather_data_28_2)
        json_weather_data_28_2_copy['fecha'] = f"{year}-02-29"
        json_weather_data_28_2_copy['dia'] = 60

        # add 29-2 to json_weather_data_last_year before 28-2
        json_weather_data_last_year.insert(json_weather_data_last_year.index(
            json_weather_data_28_2) + 1, json_weather_data_28_2_copy)

        for index, json_weather_item in enumerate(json_weather_data_last_year):
            # 59 is 28/2
            if index > 59:
                json_weather_item["dia"] = json_weather_item["dia"] + 1

        return json_weather_data_last_year

    def remove_29_2_from_weather_data(self, json_weather_data_last_year, day_date):
        """Remove 29-2 from weather data
        Args:
            json_weather_data_last_year (_type_): json file with the weatherdata

        Returns:
            _type_: json file with the weatherdata
        """
        # remove 29-2 from json_weather_data_last_year
        json_weather_data_last_year = [
            d for d in json_weather_data_last_year if d["fecha"] != f"{day_date.year - 1}-02-29"]
        return json_weather_data_last_year

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


# def get_data_for_aquacrop(self, initial_date, end_date):
#         """
#         The output have to be a pandas dataframe with this structure:
#               MinTemp     MaxTemp  Precipitation ReferenceET       Date
#         0       5.101    15.68            0.0     1.600394       2001-02-09
#         """
#         json_weather_data = self.get_json_data(initial_date, end_date)

#         weather_df = pd.DataFrame(
#             json_weather_data,
#             columns=["fecha", "tempMin", "tempMax", "precipitation", "et0"],
#         )
#         weather_df["precipitation"] = weather_df["precipitation"].fillna(0.00)

#         weather_df.rename(
#             columns={
#                 "tempMin": "MinTemp",
#                 "tempMax": "MaxTemp",
#                 "precipitation": "Precipitation",
#                 "et0": "ReferenceET",
#             },
#             inplace=True,
#         )

#         # set limit on ET0 to avoid divide by zero errors
#         weather_df.ReferenceET.clip(lower=0.1, inplace=True)

#         # Fill missing date values with the previous value
#         weather_df.index = pd.DatetimeIndex(weather_df["fecha"]).floor("D")
#         weather_df = weather_df.resample("D").mean().fillna(method="ffill")

#         # Create Date column
#         weather_df["Date"] = weather_df.index

#         # Change index from date to row number
#         weather_df.index = range(len(weather_df))

#         return weather_df
