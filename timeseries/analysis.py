import pandas as pd
import numpy as np
import statsmodels.tsa.stattools as ts
import matplotlib.pyplot as plt
import preprocessing as pre
import os


# returns true if the time series is of I(1)
def unit_root_test(data, confidence_level=0.9):
    result = ts.adfuller(data, regression='ct')
    confidence_level = (1 - confidence_level) * 100
    alpha = '{:.0f}%'.format(confidence_level)
    return result[0] >= result[4][alpha]


def try_parse_long(s):
    try:
        return long(s)
    except ValueError:
        return float(s)


def correlation_test(ds1, ds2):
    df = pd.DataFrame({'ds1': ds1, 'ds2': ds2})
    return df['ds1'].corr(df['ds2'])


def cointegration_test(y, x):
    result = ts.coint(x, y)
    return result[0] < result[1]


def chunks(stream, step):
    n = len(stream)
    return (stream[i:i + step if i + step < n else n] for i in xrange(0, n, step))


for i in xrange(3):
    file_path = pre.get_all_data_files()[i]
    recv, exch = pre.get_time_series(file_path)
    size = 5000
    recv_ur_ok = True
    exch_ur_ok = True
    coint_ok = True
    print os.path.basename(file_path)
    for r, e in zip(chunks(recv, size), chunks(exch, size)):
        recv_ur_ok = recv_ur_ok and unit_root_test(r)
        exch_ur_ok = exch_ur_ok and unit_root_test(e)
        coint_ok = coint_ok and cointegration_test(e, r)

    recv_io = 'I(1)' if recv_ur_ok else 'I(0)'
    exch_io = 'I(1)' if exch_ur_ok else 'I(0)'
    print 'recv:{0}\texch:{1}\tcointegration:{2}'.format(recv_io, exch_io, coint_ok)

    corr = np.mean([cointegration_test(e, r) for e, r in zip(chunks(recv, size), chunks(exch, size))])
    print 'correlation:{}'.format(corr)


recv = pre.normalize_data(recv)
exch = pre.normalize_data(exch)
plt.plot(recv)
plt.plot(exch)
plt.title('Time series after normalization')
plt.show()

