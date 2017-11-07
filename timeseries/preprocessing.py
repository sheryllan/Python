import os
import pandas as pd
import numpy as np
import math

curr_dir = os.path.dirname(__file__)
csv_files = [f for f in os.listdir(curr_dir) if f.endswith('.csv')]
file_paths = [os.path.join(curr_dir, f) for f in csv_files]

column1 = 'recv'
column2 = 'exch'


def get_all_data_files():
    return file_paths


def read_csv(path):
    return pd.read_csv(path, index_col=False, dtype={column1: str, column2: str}, usecols=[column1, column2])


def try_parse(s):
    try:
        return long(s)
    except ValueError:
        return float('nan')


def get_time_series(path):
    data_frame = read_csv(path)
    recv, exch = zip(*[(long(r), long(e)) for r, e in zip(data_frame.recv, data_frame.exch) \
                       if not (math.isnan(try_parse(r)) or math.isnan(try_parse(e)))])
    return recv, exch


def normalize_data(data):
    mean = np.mean(data)
    std = np.std(data)
    return [(d - mean) / std for d in data]

