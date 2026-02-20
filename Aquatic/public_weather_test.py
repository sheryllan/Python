import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import unittest
import weather

from io import StringIO

_INPUT_HEADER = "Station Name,Measurement Timestamp,Air Temperature,Wet Bulb Temperature,Humidity,Rain Intensity,Interval Rain,Total Rain,Precipitation Type,Wind Direction,Wind Speed,Maximum Wind Speed,Barometric Pressure,Solar Radiation,Heading,Battery Life,Measurement Timestamp Label,Measurement ID"
_OUTPUT_HEADER = "Station Name,Date,Min Temp,Max Temp,First Temp,Last Temp"


class TestingWeather(unittest.TestCase):
    # Feel free to modify this class in any way that you see fit, including deleting existing code.

    def test_simple(self):
        input_io = StringIO(
            f"{_INPUT_HEADER}\nUnion Square,06/13/2023 04:11:12 PM,2.3,-0.4,58,0,0,135.1,0,338,1.4,3,991.1,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID")
        output_io = StringIO()
        weather.process_csv(input_io, output_io)

        self.assertEqual(output_io.getvalue().strip(), f"{_OUTPUT_HEADER}\nUnion Square,06/13/2023,2.3,2.3,2.3,2.3")

    def test_sample_data(self):
        with open("data/chicago_beach_weather.csv") as input_file:
            output_io = StringIO()
            weather.process_csv(input_file, output_io)

        output = output_io.getvalue().strip().split("\n")
        self.assertEqual(len(output), 16)

    def test_temperature_aggregation(self):
        input_io = StringIO(
            f"{_INPUT_HEADER}\n"
            "Union Square,06/13/2023 04:11:12 PM,20.3,-0.4,58,0,0,135.1,0,338,1.4,3,991.1,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Foster Weather Station,06/13/2023 05:01:00 PM,18.55,-0.4,58,0,0,,0,338,1.4,3,991.1,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Union Square,06/13/2023 05:11:12 PM,25,-0.4,58,0,0,135.1,0,338,1.4,3,991.1,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Union Square,06/13/2023 05:30:12 AM,17.9,-0.4,58,0,0,135.1,0,338,1.4,3,991.1,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Union Square,06/14/2023 09:26:12 AM,13.76,-0.4,58,0,0,135.1,0,338,1.4,3,991.1,2,0,,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Foster Weather Station,06/13/2023 04:11:12 AM,8,,58,0,0,135.1,0,338,1.4,3,,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Foster Weather Station,06/13/2023 11:00:00 PM,10.94,,58,0,0,135.1,0,338,1.4,3,991.1,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n")
        output_io = StringIO()
        weather.process_csv(input_io, output_io)
        actual = output_io.getvalue().strip().split("\n")
        expected = [
            _OUTPUT_HEADER,
            f"Union Square,06/13/2023,17.9,25.0,17.9,25.0",
            f"Union Square,06/14/2023,13.76,13.76,13.76,13.76",
            f"Foster Weather Station,06/13/2023,8.0,18.55,8.0,10.94"
        ]
        self.assertCountEqual(expected, actual)

    def test_invalid_data_format(self):
        input_io = StringIO(
            f"{_INPUT_HEADER}\n"
            "Union Square,06/13/2023 04:11:12 PM,20.3,-0.4,58,0,0,135.1,0,338,1.4,3,991.1,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Foster Weather Station,06/13/2023 05:01:00 PM,18.55,-0.4,58,0,0,,0,338,1.4,3,991.1,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Union Square,06/13/2023 05:11:12 PM,25,-0.4,58,0,0,135.1,0,338,1.4,3,991.1,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Union Square,06/13/2023 05:30:12 AM,17.9,-0.4,58,0,0,135.1,0,338,1.4,3,991.1,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Union Square,06/14/2023 09:26:12 AM,,-0.4,58,0,0,135.1,0,338,1.4,3,991.1,2,0,,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Foster Weather Station,06/13/2023 04:11:12 AM,8,,58,0,0,135.1,0,338,1.4,3,,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n"
            "Foster Weather Station,06/13/2023 11:00:00,10.94,,58,0,0,135.1,0,338,1.4,3,991.1,2,0,12.1,A Completely Contrived Sample,And Its Completely Contrived Measurement ID\n")
        output_io = StringIO()
        weather.process_csv(input_io, output_io)

        actual = output_io.getvalue().strip().split("\n")
        expected = [
            _OUTPUT_HEADER,
            f"Union Square,06/13/2023,17.9,25.0,17.9,25.0",
            f"Foster Weather Station,06/13/2023,8.0,18.55,8.0,18.55"
        ]
        self.assertCountEqual(expected, actual)

    def test_get_7day_moving_average(self):
        with open("data/chicago_beach_weather.csv") as input_file:
            output_io = StringIO()
            weather.get_7day_moving_average(input_file, output_io)

            output_io.getvalue()



