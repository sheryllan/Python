import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
import matplotlib.pyplot as plt
import math
import statsmodels.tsa.arima_model as arma
import scipy.stats as stats


def unit_root_test(data_frame, confidence_level=0.9):
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


def correlation_test(ds1, ds2):
    df = pd.DataFrame({'ds1': ds1, 'ds2': ds2})
    return df['ds1'].corr(df['ds2'])


def cointegration_test(y, x):
    result = ts.coint(x, y)
    return result


filepath = r"D:\MyGitHub.git\Python\timeseries\FDAX-F-DEC2017-20170920-060000.csv"
data_frame = pd.read_csv(filepath, index_col=False, dtype={'recv': str, 'exch': str}, usecols=['recv', 'exch'])

recv = [try_parse_long(d) for d in data_frame.recv]
exch = [try_parse_long(d) for d in data_frame.exch]
recv, exch = zip(*[(r, e) for r, e in zip(recv, exch) if not (math.isnan(r) or math.isnan(e))])

"""pr = plt.plot(recv[:1000], label='recv')
pe = plt.plot(exch[:1000], label='exch')
plt.legend(handles=(pr, pe))
plt.show()"""

"""print unit_root_test(recv[:1000])
print unit_root_test(exch[:1000])

print correlation_test(recv[:1000], exch[:1000])"""

est = sm.OLS(exch, recv).fit()

# print est.resid[:500]

# print ts.adfuller(est.resid[:1000])
"""rr = ts.coint(recv[:1000], exch[:1000])
print rr"""

l = 2000
h = 5000
lag_acf = ts.acf(est.resid[h:h + l], nlags=10)
lag_pacf = ts.pacf(est.resid[h:h + l], nlags=10, method='ols')

threshold = 1.96 / np.sqrt(l)
p = next(i for i, x in enumerate(lag_pacf) if x < threshold)
q = next(i for i, x in enumerate(lag_acf) if x < threshold)

print p, q

"""plt.subplot(121)
plt.plot(lag_acf[:30])
plt.axhline(y=0,linestyle='--', color='gray')
plt.axhline(y=-1.96/np.sqrt(l),linestyle='--',color='gray')
plt.axhline(y=1.96/np.sqrt(l),linestyle='--',color='gray')
plt.title('Autocorrelation Function')

plt.subplot(122)
plt.plot(lag_pacf[:30])
plt.axhline(y=0,linestyle='--', color='gray')
plt.axhline(y=-1.96/np.sqrt(l),linestyle='--',color='gray')
plt.axhline(y=1.96/np.sqrt(l),linestyle='--',color='gray')
plt.title('Partial Autocorrelation Function')
plt.tight_layout()

plt.show()
"""

model = arma.ARMA(est.resid[h:h + l], order=(p, 1, q))
result_arma = model.fit(disp=-1)
"""plt.plot(est.resid[h:h+500])
plt.plot(result_arma.fittedvalues[:500], color='red')
plt.show()"""

interval = 15
for i in range(100):
    ttest = stats.ttest_ind(est.resid[h+i + interval:h + i + 2 * interval], result_arma.fittedvalues[interval + i:2 * interval + i])
    print i, ttest.statistic < ttest.pvalue,  ttest

plt.plot(est.resid[h+interval:h+interval+100])
plt.plot(result_arma.fittedvalues[interval: interval+100], color='red')
plt.show()