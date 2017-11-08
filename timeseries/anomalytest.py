import preprocessing as pre
import statsmodels.api as sm
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import math


def chunks(stream, step):
    n = len(stream)
    return (stream[i:i + step if i + step < n else n] for i in xrange(0, n, step))
    

def get_best_params(fnums):
    best = {}
    for i in fnums:
        file_path = pre.get_all_data_files()[i]
        recv, exch = pre.get_time_series(file_path)
        recv = pre.normalize_data(recv)
        exch = pre.normalize_data(exch)
        best[i] = [float('inf'), -1, -1]
        residuals = [y - x for y, x in zip(recv, exch)]
        for lag in xrange(5, 21):
            for m in np.arange(0.5, 1, 0.1):
                #anomalies = detect_anomaly(recv, exch, lag, m)
                #mse = np.mean([r**2 for r in residuals if r not in anomalies])
                mse = np.mean([residuals[index]**2 for index in remove_anomaly(recv, exch, lag, m)])
                if mse < best[i][0]:
                    best[i] = [mse, m, lag]
        print best[i]
    return best


def get_weighted_best_params(params):
    params = zip(*params)
    min_mse = min(params[0])
    mse = [min_mse / x for x in params[0]]
    weights = [m / sum(mse) for m in mse]
    weighted_threshold = np.average(params[1], weights=weights)
    weighted_lag = int(round(np.average(params[2], weights=weights)))
    return [weighted_threshold, weighted_lag]



def cross_validation(fnums, params):
    for i in fnums:
        file_path = pre.get_all_data_files()[i]
        recv, exch = pre.get_time_series(file_path)
        recv = pre.normalize_data(recv)
        exch = pre.normalize_data(exch)

        params_trainning = [params[j] for j in fnums if not j == i]
        best = get_weighted_best_params(params_trainning)
        best_threshold = best[0]
        best_lag = best[1]

        anomaly_indices = list(detect_anomaly(recv, exch, best_lag, best_threshold))
        """anomaly_free_indices = [ind for ind in xrange(len(recv)) if ind not in anomaly_indices]
        expected = [recv[index] for index in anomaly_free_indices]
        actual = [exch[index] for index in anomaly_free_indices]
        t_test = stats.ttest_ind(expected, actual)
        print t_test[0] < t_test[1]"""

        anomalies = [exch[ind] for ind in anomaly_indices]
        non_anomalies = [recv[ind] for ind in anomaly_indices]
        t_test = stats.ttest_ind(non_anomalies, anomalies, equal_var=False)

        print t_test
        print t_test.statistic >= t_test.pvalue








def remove_anomaly(expected, actual, lag, threshold):
    h = 0
    l = len(actual)
    residuals = [y - x for y, x in zip(actual, expected)]
    mean = np.mean(residuals)
    std = np.std(residuals)
    threshold = threshold * std
    df = pd.DataFrame({'resid': residuals})
    mv_var = df.rolling(lag, center=False).var()['resid'].tolist()
    var_delta = 2 * (threshold**2 / lag**2 + 1)

    for i in xrange(h, h + l):
        if math.isnan(mv_var[i]):
            if abs(residuals[i]) <= threshold:
                yield i
        else:
            if abs(residuals[i] - mean) <= threshold and abs(mv_var[i] - std**2) <= var_delta:
                yield i




def detect_anomaly(expected, actual, lag, threshold):
    h = 0
    l = len(actual)
    residuals = [y - x for y, x in zip(actual, expected)]
    mean = np.mean(residuals)
    std = np.std(residuals)
    threshold = threshold * std
    df = pd.DataFrame({'resid': residuals})
    mv_avg = df.rolling(lag, center=False).mean()['resid'].tolist()
    mv_var = df.rolling(lag, center=False).var()['resid'].tolist()

    var_delta = 2 * (threshold**2 / lag**2 + 1)

    for i in xrange(h, h + l):
        if math.isnan(mv_avg[i]) or math.isnan(mv_var[i]):
            if abs(residuals[i]) > threshold:
                yield i

        if i > 1:
            if abs(residuals[i] - mean) > threshold or abs(mv_var[i] - std**2) > var_delta:
                yield i

    """for i in xrange(h+lag, h+l+lag):
        t_test = stats.ttest_ind(expected[i-lag:i], actual[i-lag:i])
        if t_test.statistic > t_test.pvalue:
            print i-h
            yield i"""





file_path = pre.get_all_data_files()[3]
recv, exch = pre.get_time_series(file_path)
recv = pre.normalize_data(recv)
exch = pre.normalize_data(exch)

xs, ys = zip(*[(x, exch[x]) for x in detect_anomaly(recv, exch, 10, 2)])
plt.plot(recv)
plt.plot(exch)
plt.plot(xs, ys, 'ro', color='black')
plt.show()

#print find_best_params([4])

a = [[3.8194700411831127e-08, 0.5, 6], [2.9043829563732082e-05, 0.5, 17], [1.4181636918767581e-09, 0.5, 8], [1.3564396985124244e-10, 0.5, 5], [1.5822187251236839e-07, 0.5, 9]]

#cross_validation(xrange(5), a)
#print get_weighted_best_params(a)

