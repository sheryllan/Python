import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
import matplotlib.pyplot as plt


def test_stationarity(data_frame, confidence_level=0.9):
    result = ts.adfuller(data_frame, regression='ct')
    confidence_level = (1 - confidence_level) * 100
    alpha = '{:.0f}%'.format(confidence_level)
    print result[0]
    print result[4]
    return result[0] < result[4][alpha]


def try_parse_long(s):
    try:
        return long(s)
    except ValueError:
        return float(s)


def test_correlation(ds1, ds2):
    df = pd.DataFrame({'ds1': ds1, 'ds2': ds2})
    return df['ds1'].corr(df['ds2'])


filepath = r"/Users/sheryllan/Downloads/data (5)/FDAX-F-DEC2017-20170920-060000.csv"
data = pd.read_csv(filepath, index_col=False, dtype={'recv': str, 'exch': str}, usecols=['recv', 'exch'])
print data.head()

recv = [try_parse_long(d) for d in data.recv]
exch = [try_parse_long(d) for d in data.exch]


"""pr = plt.plot(recv[:1000], label='recv')
pe = plt.plot(exch[:1000], label='exch')
plt.legend(handles=(pr, pe))
plt.show()"""

print test_stationarity(recv[:1000])
print test_stationarity(exch[:1000])

print test_correlation(recv, exch)


est = sm.OLS(recv, exch)
