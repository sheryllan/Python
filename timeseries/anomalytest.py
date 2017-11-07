import preprocessing as pre
import statsmodels.api as sm
import numpy as np
import pandas as pd
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.arima_model import ARMAResults
import scipy.stats as stats
import matplotlib.pyplot as plt
import math


def get_ARMA_result(train, p, q):
    size = 5000
    return [ARMA(c, order=(p, 1, q)).fit(disp=-1) for c in al.chunks(train, size)]


def find_best_pq(train):
    min_bic = 0
    p, q = 0, 0
    for i in xrange(5):
        for j in xrange(5):
            results = get_ARMA_result(train, i, j)
            bic = np.mean([ARMAResults.bic(r) for r in results])
            if bic < min_bic :
                p = i
                q = j
    return (p, q, min_bic)

    

def cross_validation():
    for i in xrange(4, y=1):
        k = 2 * i
        best = (0, 0, 0)
        while not k == i:
           recv, exch = pre.get_time_series(pre.get_all_data_files()[k])
           est = sm.OLS(exch, recv).fit()
           potential = find_best_pq(est.resid)
           best = potential if potential[2] < best[2] else best
           k = (k + 1) % 6




def detect(expected, actual, lag):
    h = 200000
    l = 20000
    residuals = [y - x for y, x in zip(actual, expected)]
    mean = np.mean(residuals)
    std = np.std(residuals)
    threshold = std
    df = pd.DataFrame({'resid': residuals})
    mv_avg = df.rolling(lag, center=False).mean()['resid'].tolist()
    mv_var = df.rolling(lag, center=False).var()['resid'].tolist()

    avg_delta = threshold / lag
    var_delta = 2 * (threshold**2 / lag**2 + 1)

    for i in xrange(h, h + l):
        if math.isnan(mv_avg[i]) or math.isnan(mv_var[i]):
            if abs(residuals[i]) > threshold:
                yield i

        if i > 1:
            if abs(residuals[i] - mean) > threshold or abs(mv_avg[i] - mean) > avg_delta or mv_var[i] > mv_var[i - 1] + var_delta:
                yield i

    """for i in xrange(h+lag, h+l+lag):
        t_test = stats.ttest_ind(expected[i-lag:i], actual[i-lag:i])
        if t_test.statistic > t_test.pvalue:
            print i-h
            yield i"""





file_path = pre.get_all_data_files()[0]
recv, exch = pre.get_time_series(file_path)
recv = pre.normalize_data(recv)
exch = pre.normalize_data(exch)

xs, ys = zip(*[(x - 200000, exch[x]) for x in detect(recv, exch, 10)])
plt.plot(recv[200000:220000])
plt.plot(exch[200000:220000])
plt.plot(xs, ys, 'ro', color='black')
plt.show()

plt.show()

