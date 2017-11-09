import preprocessing as pre
import numpy as np
import scipy.stats as stats
import math


def prob(x):
    x = abs(x)
    return 1 - 2 * math.erf(x)


def detect_anomaly_adaptive(expected, actual, threshold, increment):
    residuals = [a - e for a, e in zip(actual, expected)]
    mean = np.mean(residuals)
    std = np.std(residuals)
    threshold = threshold * std

    tot_norm, tot_anom = 0, 0
    no_norm, no_anom = 0, 0
    centroids = [mean, mean + threshold / 2]
    score_up, score_down = 0, 0

    for i in xrange(len(actual)):
        dist = [abs(residuals[i] - c) for c in centroids]
        if abs(residuals[i] - mean) > threshold:
            label = dist[0] * prob(dist[1]) < dist[1] * prob(dist[0])
            if label and threshold < 3 * std:
                label = False
                tot_norm = tot_norm + residuals[i]
                no_norm = no_norm + 1
                centroids[0] = tot_norm / no_norm
                score_up = score_up + dist[1] / sum(dist) * prob(dist[0])
                if score_up > 0.8:
                    score_up = 0
                    threshold = threshold + increment
            else:
                label = True
                tot_anom = tot_anom + residuals[i]
                no_anom = no_anom + 1
                centroids[1] = tot_anom / no_anom
        else:
            label = dist[1] * prob(dist[0]) < dist[0] * prob(dist[1])
            if label and threshold > 0.5 * std:
                label = True
                tot_anom = tot_anom + residuals[i]
                no_anom = no_anom + 1
                centroids[1] = tot_anom / no_anom
                score_down = score_down + dist[0] / sum(dist) * prob(dist[1])
                if score_down > 0.8:
                    score_down = 0
                    threshold = threshold - increment
            else:
                label = False
                tot_norm = tot_norm + residuals[i]
                no_norm = no_norm + 1
                centroids[0] = tot_norm / no_norm

        yield (i, label)


def get_best_params(fnums):
    best = {}
    for i in fnums:
        file_path = pre.get_all_data_files()[i]
        recv, exch = pre.get_time_series(file_path)
        recv = pre.normalize_data(recv)
        exch = pre.normalize_data(exch)
        best[i] = [float('inf'), -1, -1]
        residuals = [y - x for y, x in zip(recv, exch)]
        for threshold in np.arange(0.5, 3.1, 0.2):
            for increment in np.arange(0.1, 1.1, 0.1):
                anom_indices = [x[0] for x in detect_anomaly_adaptive(recv, exch, threshold, increment) if x[1]]
                norm_indices = [x[0] for x in detect_anomaly_adaptive(recv, exch, threshold, increment) if not x[1]]

                anomalies = [exch[ind] for ind in anom_indices]
                normal = [recv[ind] for ind in norm_indices]

                t_test = stats.ttest_ind(normal, anomalies, equal_var=False)
                if t_test[0] >= t_test[1]:
                    mse = np.mean([residuals[a] ** 2 for a in anom_indices])
                    if mse < best[i][0]:
                        best[i] = [mse, threshold, increment]
        print best[i]
    return best


print get_best_params([0, 1, 2, 3, 4])
