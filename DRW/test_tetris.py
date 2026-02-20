import os
import sys
import unittest

THIS_DIR = os.path.dirname(__file__)
sys.path.insert(0, THIS_DIR)

# from tetris import process_line
from tetris_columnar_optimized import process_line


class TestTetrisFromInput(unittest.TestCase):
    def test_input_txt_cases(self):
        input_path = os.path.join(THIS_DIR, "input.txt")
        with open(input_path, "r", encoding="utf-8") as handle:
            lines = [line for line in handle if line.strip()]

        expected = [
            "2",
            "4",
            "0",
            "2",
            "4",
            "1",
            "0",
            "2",
            "2",
            "2",
            "1",
            "1",
            "4",
            "3",
            "1",
            "2",
            "1",
            "8",
            "8",
            "0",
            "3",
        ]

        actual = [str(process_line(line)) for line in lines]
        self.assertEqual(actual, expected)

    def test_additional_cases(self):
        cases = {
            "I0": "1",
            "I0,I0": "2",
            "Q0,Q2,Q4,Q6,Q8": "0",
            "Q0,Q2,Q4,Q6,Q8,Q1": "2",
            "T0": "2",
            "T0,T4": "2",
            "T0,T3,I6,I6": "1",
            "S0,Z2": "3",
            "S0,Z2,I4": "3",
            "L0,J2,L4,J6": "3",
            "L0,J2,L4,J6,Q8": "2",
            "L0,J2,L4,J6,Q8,Q0": "4",
            "Q0,I2,I6,I0,I6,I6,Q2,Q4": "3",
            "Q0,I2,I6,I0,I6,I6,Q2,Q4,Q4": "3",
            "I0,I4,Q8,Q0": "2",
            "I0,I4,Q8,Q0,Q0": "4",
            "S0,S2,S4,S6": "8",
            "S0,S2,S4,S6,Z1": "8",
        }
        for line, expected in cases.items():
            with self.subTest(line=line):
                self.assertEqual(str(process_line(line)), expected)


if __name__ == "__main__":
    unittest.main()
