import preprocessing as pre
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import math

"""file_path = pre.get_all_data_files()[4]
recv, exch = pre.get_time_series(file_path)
recv = pre.normalize_data(recv)
exch = pre.normalize_data(exch)

residuals = [y - x for y, x in zip(recv, exch)]"""

"""X = np.reshape(residuals)


kmeans = KMeans(n_clusters=2).fit(residuals)

print kmeans.cluster_centers_

print kmeans.labels_[3500:4500]"""


def kmeans_detection(expected, actual, lag, threshold):
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

    tot_norm, tot_anom = 0, 0
    no_norm, no_anom = 0, 0
    centroids = [mean, mean + threshold]
    for i in xrange(h, h + l):
        dist = [(residuals[i] - c)**2 for c in centroids]
        label = dist[0] > dist[1]
        if label:
            tot_anom = tot_anom + residuals[i]
            no_anom = no_anom + 1
            centroids[1] = tot_anom / no_anom
        else:
            tot_norm = tot_norm + residuals[i]
            no_norm = no_norm + 1
            centroids[0] = tot_norm / no_norm

        yield (i, label)


file_path = pre.get_all_data_files()[4]
recv, exch = pre.get_time_series(file_path)
recv = pre.normalize_data(recv)
exch = pre.normalize_data(exch)

print [x for x in kmeans_detection(recv, exch) if not x]
#for p in kmeans_detection(recv, exch):
#    print p
