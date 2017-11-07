import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
import matplotlib.pyplot as plt
import math
import statsmodels.tsa.arima_model as arma
import scipy.stats as stats
from pandas.plotting import autocorrelation_plot
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tools.eval_measures import bic
from statsmodels.tsa.arima_model import ARMAResults
import preprocessing as pre
import os



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





"""print correlation_test(recv[:1000], exch[:1000])

est = sm.OLS(exch, recv).fit()

# print est.resid[:500]

# print ts.adfuller(est.resid[:1000])
rr = ts.coint(recv[:5000], exch[:5000])
print rr"""

"""l = 2000
h = 5000
lag_acf = ts.acf(est.resid[h:h + l], nlags=30)
lag_pacf = ts.pacf(est.resid[h:h + l], nlags=10, method='ols')

threshold = 1.96 / np.sqrt(l)
p = next(i for i, x in enumerate(lag_pacf) if x < threshold)
q = next(i for i, x in enumerate(lag_acf) if x < threshold)

print p, q"""

"""plt.subplot(121)
plt.plot(lag_acf)
plt.axhline(y=0,linestyle='--', color='gray')
plt.axhline(y=-1.96/np.sqrt(l),linestyle='--',color='gray')
plt.axhline(y=1.96/np.sqrt(l),linestyle='--',color='gray')
plt.title('Autocorrelation Function')


plt.subplot(122)
plt.plot(lag_pacf)
plt.axhline(y=0,linestyle='--', color='gray')
plt.axhline(y=-1.96/np.sqrt(l),linestyle='--',color='gray')
plt.axhline(y=1.96/np.sqrt(l),linestyle='--',color='gray')
plt.title('Partial Autocorrelation Function')
plt.tight_layout()

plt.show()"""



"""model = arma.ARMA(est.resid[h:h + l], order=(p, 1, q))
result_arma = model.fit(disp=-1)
resid = est.resid[h:h + l] - result_arma.fittedvalues
rss = sum(resid ** 2)
print result_arma.summary()
bayesian = l* math.log(rss/l) + (p+q+1)*math.log(l)
print bayesian"""



"""plt.plot(est.resid[h:h+500])
plt.plot(result_arma.fittedvalues[:500], color='red')
plt.show()"""

"""interval = 15
for i in range(100):
    ttest = stats.ttest_ind(est.resid[h+i + interval:h + i + 2 * interval], result_arma.fittedvalues[interval + i:2 * interval + i])
    print i, ttest.statistic < ttest.pvalue,  ttest

plt.plot(est.resid[h+interval:h+interval+100])
plt.plot(result_arma.fittedvalues[interval: interval+100], color='red')
plt.show()
"""



def chi2_test(obs1, obs2):
    obs = np.array([obs1, obs2])
    chi2, p, dof, expected = stats.chi2_contingency(obs)
    return chi2 < p


def chunks(list, n):
    l = len(list)
    return (list[i:i + n if i + n < l else l] for i in xrange(0, l, n))

"""for i in xrange(3):
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

    recv_io = 'I(1)' if recv_ur_ok else 'unkown'
    exch_io = 'I(1)' if exch_ur_ok else 'unkown'
    print 'recv:{0}\texch:{1}\tcointegration:{2}'.format(recv_io, exch_io, coint_ok)

    corr = np.mean([cointegration_test(e, r) for e, r in zip(chunks(recv, size), chunks(exch, size))])
    print 'correlation:{}'.format(corr)

"""


for i in xrange(10):
    file_path = pre.get_all_data_files()[i]
    recv, exch = pre.get_time_series(file_path)
    recv = pre.normalize_data(recv)
    exch = pre.normalize_data(exch)
    #scale = max(abs(min(recv)), abs(min(exch))) + 1
    #recv = pre.scale_up(recv, scale)
    #exch = pre.scale_up(exch, scale)
    #lag = 12
    #recv = pd.rolling_mean(recv, lag)
    #exch = pd.rolling_mean(exch, lag)
    #df = pd.DataFrame({'recv': recv, 'exch': exch})
    #recv = pd.rolling_mean(df['recv'], lag)[lag:]
    #exch = pd.rolling_mean(df['exch'], lag)[lag:]

    """plt.plot(recv)
    plt.plot(exch)
    plt.show()"""

    """est = sm.OLS(exch, recv).fit()
    print est.params
    rrs = sum([(y - x)**2 for y, x in zip(recv, exch)])
    rrs_fit = est.ssr
    print (rrs - rrs_fit)/rrs_fit
    print"""



    """size = 5000
    is_stationary = True
    res = [y - x for y, x in zip(recv, exch)]
    for c in chunks(res, size):
        is_stationary = is_stationary and not unit_root_test(c)

    print 'adf test for normalized residual(recv - exch) {}'.format('passed' if is_stationary else 'failed')"""



