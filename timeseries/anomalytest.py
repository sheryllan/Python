import preprocessing as pre
import numpy as np
import scipy.stats as stats
import math

op_threshold = 0.5
op_increment = 0.1


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


def test(fnums):
    for i in fnums:
        file_path = pre.get_all_data_files()[i]
        recv, exch = pre.get_time_series(file_path)
        recv = pre.normalize_data(recv)
        exch = pre.normalize_data(exch)

        norm_indices = [x[0] for x in detect_anomaly_adaptive(recv, exch, op_threshold, op_increment) if not x[1]]

        actual = [exch[ind] for ind in norm_indices]
        expected = [recv[ind] for ind in norm_indices]

        t_test = stats.ttest_ind(actual, expected, equal_var=False)
        print t_test
        print t_test[0] < t_test[1]


test([5, 6, 7, 8, 9])
