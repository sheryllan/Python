import preprocessing as pre
import analysis as al
import statsmodels.api as sm
import numpy as np
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.arima_model import ARMAResults


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

def validate():
    

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





