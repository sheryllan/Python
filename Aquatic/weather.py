from typing import TextIO
from enum import IntEnum, auto
from dataclasses import dataclass
import logging
from collections import defaultdict

from datetime import datetime, date

import pandas as pd
from numpy import ndarray, array

"""
Station Name,Measurement Timestamp,Air Temperature,Wet Bulb Temperature,Humidity,Rain Intensity,Interval Rain,Total Rain,
Precipitation Type,Wind Direction,Wind Speed,Maximum Wind Speed,Barometric Pressure,Solar Radiation,Heading,Battery Life,
Measurement Timestamp Label,Measurement ID
"""

"""File-like objects are iterators that produce a line of text on each iteration. Iterators in general just means "
things you can loop over exactly once"; files differ from this pattern on insofar as they can (depending on what the represent) 
be seeked, which would reset the iterator to a new position in the file.

To be clear, they are not sequences; the term "sequence" has specific meaning, and includes the ability to index it, 
iterate it multiple times in a row or in parallel, all without manually fixing up state."""


logging.basicConfig()


class InputColumns(IntEnum):
    station_name = 0
    measurement_timestamp = auto()
    air_temperature = auto()
    wet_bulb_temperature = auto()
    humidity = auto()
    rain_intensity = auto()
    interval_rain = auto()
    total_rain = auto()
    precipitation_type = auto()
    wind_direction = auto()
    wind_speed = auto()
    maximum_wind_speed = auto()
    barometric_pressure = auto()
    solar_radiation = auto()
    heading = auto()
    battery_life = auto()
    measurement_timestamp_label = auto()
    measurement_id = auto()


CSV_SEP = ','
TIMESTAMP_FORMAT = '%m/%d/%Y %I:%M:%S %p'
DATE_FORMAT = '%m/%d/%Y'


@dataclass
class OutputDailyWeather:
    station_name: str
    date: date
    first_timestamp: datetime
    last_timestamp: datetime
    first_temperature: float
    last_temperature: float
    min_temperature: float
    max_temperature: float
    # total_temperature: float = None
    # measurement_counts: int = 1
    first_wet_bulb_temperature: float
    last_wet_bulb_temperature: float = None
    min_wet_bulb_temperature: float = None
    max_wet_bulb_temperature: float = None
    first_wet_bulb_timestamp: datetime = None
    last_wet_bulb_timestamp: datetime = None

    OUTPUT_COLUMNS = 'Station Name,Date,Min Temp,Max Temp,First Temp,Last Temp,Min Wet Bulb Temp,Max Wet Bulb Temp,First Wet Bulb Temp,Last Wet Bulb Temp'

    def __post_init__(self):
        if self.first_wet_bulb_timestamp is None:
            self.first_wet_bulb_timestamp = self.first_timestamp

        if self.last_wet_bulb_timestamp is None:
            self.last_wet_bulb_timestamp = self.last_timestamp

        if self.last_wet_bulb_temperature is None:
            self.last_wet_bulb_temperature = self.first_wet_bulb_temperature

        if self.min_wet_bulb_temperature is None:
            self.min_wet_bulb_temperature = self.first_wet_bulb_temperature

        if self.max_wet_bulb_temperature is None:
            self.max_wet_bulb_temperature = self.first_wet_bulb_temperature


    # def __post_init__(self):
    #     if self.total_temperature is None:
    #         self.total_temperature = self.first_temperature

    def __str__(self):
        return CSV_SEP.join(
            [
                self.station_name,
                self.date.strftime(DATE_FORMAT),
                str(self.min_temperature),
                str(self.max_temperature),
                str(self.first_temperature),
                str(self.last_temperature)
            ])

    def __repr__(self):
        return self.__str__()

    def update_temperature(self, timestamp: datetime, temperature: float):
        self.total_temperature += temperature
        self.measurement_counts += 1

        if timestamp < self.first_timestamp:
            self.first_timestamp = timestamp
            self.first_temperature = temperature
        elif timestamp > self.last_timestamp:
            self.last_timestamp = timestamp
            self.last_temperature = temperature

        if temperature < self.min_temperature:
            self.min_temperature = temperature
        elif temperature > self.max_temperature:
            self.max_temperature = temperature



def process_csv(reader: TextIO, writer: TextIO):
    reader.readline()
    temperatures = {}
    for i, line in enumerate(reader):
        values = line.split(CSV_SEP)
        try:
            station_name = values[InputColumns.station_name]
            measurement_timestamp = datetime.strptime(values[InputColumns.measurement_timestamp], TIMESTAMP_FORMAT)
            air_temperature = float(values[InputColumns.air_temperature])
            wet_bulb_temperature = str(values[InputColumns.wet_bulb_temperature])
            wet_bulb_temperature = float(wet_bulb_temperature) if wet_bulb_temperature else None
        except ValueError as e:
            logging.error(f'Error parsing row #{i}: {e}')
            continue

        measurement_date = measurement_timestamp.date()
        key = (station_name, measurement_date)
        if key not in temperatures:
            temperatures[key] = OutputDailyWeather(
                station_name, measurement_date, measurement_timestamp, measurement_timestamp,
                air_temperature, air_temperature, air_temperature, air_temperature, wet_bulb_temperature)
        else:
            temperatures[key].update_temperature(measurement_timestamp, air_temperature)

    writer.write(OutputDailyWeather.OUTPUT_COLUMNS)
    writer.write('\n')
    writer.writelines(f'{x}\n' for x in temperatures.values())


def calculate_average(daily_weathers: ndarray[OutputDailyWeather]):
    values = array([[x.total_temperature, x.measurement_counts] for x in daily_weathers])
    return values[:, 0].sum() / values[:, 1].sum()


# def get_7day_moving_average(reader: TextIO, writer: TextIO):
#     reader.readline()
#     temperatures = defaultdict(dict)
#     for i, line in enumerate(reader):
#         values = line.split(CSV_SEP)
#         try:
#             station_name = values[InputColumns.station_name]
#             measurement_timestamp = datetime.strptime(values[InputColumns.measurement_timestamp], TIMESTAMP_FORMAT)
#             air_temperature = float(values[InputColumns.air_temperature])
#             wet_bulb_temperature = str(values[InputColumns.wet_bulb_temperature])
#             wet_bulb_temperature = float(wet_bulb_temperature) if wet_bulb_temperature.isnumeric() else None
#         except ValueError as e:
#             logging.error(f'Error parsing row #{i}: {e}')
#             continue
#
#     measurement_date = measurement_timestamp.date()
#         if measurement_date not in temperatures[station_name]:
#             temperatures[station_name][measurement_date] = OutputDailyWeather(
#                 station_name, measurement_date, measurement_timestamp, measurement_timestamp,
#                 air_temperature, air_temperature, air_temperature, air_temperature, wet_bulb_temperature)
#         else:
#             temperatures[station_name][measurement_date].update_temperature(measurement_timestamp, air_temperature)
#
#     df = pd.concat({sn: pd.DataFrame.from_dict(daily_weathers, orient='index', columns=['total_temperature', 'measurement_counts'])
#                     for sn, daily_weathers in temperatures.items()}, axis=1).sort_index()
#     # cumsum_vec = numpy.cumsum(numpy.insert(data, 0, 0))
#     # ma_vec = (cumsum_vec[window_width:] - cumsum_vec[:-window_width]) / window_width
#     df_window = df.rolling(2)
#     df_window_sum = df_window.sum()
#     df_moving_average = df_window_sum.xs('total_temperature', axis=1, level=1) / df_window_sum.xs('measurement_counts', axis=1, level=1)
#     writer.write('\n')


