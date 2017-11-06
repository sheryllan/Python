import csv
import matplotlib.pyplot as plt
import statsmodels.tsa.stattools as ts
import numpy as np


class DataAccess(object):
    @staticmethod
    def read_csv(path):
        with(open(path)) as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                yield row


filepath = r"/Users/sheryllan/Downloads/data (5)/FDAX-F-DEC2017-20170920-060000.csv"
data = DataAccess.read_csv(filepath)

#data = data[10000:10500]
recv, exch = zip(*[(d['recv'], d['exch']) for d in data])

plt.plot(recv[:1000])
#plt.plot(exch[:1000])

plt.show()

"""recv = list(map(int, recv[:1000]))
exch = list(map(int, exch[:1000]))


result_recv = ts.adfuller(recv, regression='ct')
statistics_recv = result_recv[0]
critical_value_recv = result_recv[4]

result_exch = ts.adfuller(exch, 1, regression='ct')
statistics_exch = result_exch[0]
critical_value_exch = result_exch[4]

print statistics_recv
print critical_value_recv

print statistics_exch
print critical_value_exch
"""

