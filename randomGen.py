import random as rand
import numpy as np
import unittest as ut
from scipy.stats import chi2
from scipy.stats import norm


class RandomGen(object):
    # Values that may be returned by next_num()
    _random_nums = []
    # Probability of the occurrence of random_nums
    _probabilities = []

    def __init__(self, nums, prob):
        RandomGen._random_nums = nums
        RandomGen._probabilities = prob

    def next_num(self):
        uni_rand = rand.random()
        for idx, prob in enumerate(self.running_sum(RandomGen._probabilities)):
            if uni_rand < prob:
                return RandomGen._random_nums[idx]
        return RandomGen._random_nums[-1]

    def running_sum(self, a):
        result = 0
        for i in a:
            result += i
            yield result


class RandomGenTests(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._random_nums = [-1, 0, 1, 2, 3]
        cls._probabilities = [0.01, 0.3, 0.58, 0.1, 0.01]
        cls._expected_value = np.average(cls._random_nums, weights=cls._probabilities)
        cls._variance = np.average([(x - cls._expected_value) ** 2 for x in cls._random_nums],
                                   weights=cls._probabilities)
        cls._gen = RandomGen(cls._random_nums, cls._probabilities)

    def _get_frequencies_of_experiments(self, n):
        frequencies = {x: 0 for x in self._random_nums}
        for i in range(n):
            r = self._gen.next_num()
            frequencies[r] += 1
        return frequencies

    def _get_chi2_test_statistics(self, frequencies, n):
        expected_counts = {x: round(p * n) for x, p in zip(self._random_nums, self._probabilities)}
        c2 = sum([(frequencies[x]) ** 2 / expected_counts[x] for x in self._random_nums]) - n
        return c2

    def _get_experiment_data(self, n):
        return [self._gen.next_num() for _ in range(n)]

    def _get_auto_covariance(self, n, k):
        data = self._get_experiment_data(n)
        r_k = np.mean([(data[i] - self._expected_value) * (data[i + k] - self._expected_value) for i in range(n - k)])
        print(r_k)
        i_mean = np.mean([data[i] for i in range(n - k)])
        ik_mean = np.mean([data[i + k] for i in range(n - k)])
        r_k1 = np.mean([data[i] * data[i + k] for i in range(n - k)]) \
               - self._expected_value * (i_mean + ik_mean) \
               + self._expected_value ** 2
        print(i_mean, ik_mean, r_k1)
        return r_k

    def _get_confidence_bound(self, alpha, scale):
        cb = norm.ppf(1 - alpha / 2) * scale
        return cb

    def test_uniformity(self):
        alpha = 0.05
        n = 10000
        k = len(self._random_nums)
        c2 = self._get_chi2_test_statistics(self._get_frequencies_of_experiments(n), n)
        quantile = chi2.ppf(1 - alpha, k - 1)
        self.assertTrue(c2 <= quantile)

    def test_independence(self):
        alpha = 0.05
        n = 100
        k = 1
        std = (float(self._variance) / (n - k)) ** (.5)
        auto_cvar = self._get_auto_covariance(n, k)
        conf_bnd = self._get_confidence_bound(alpha, std)
        self.assertTrue((auto_cvar - conf_bnd) * (auto_cvar + conf_bnd) < 0)
