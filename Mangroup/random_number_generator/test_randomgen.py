from unittest import TestCase
from unittest.mock import patch
import numpy as np
from scipy.stats import chisquare, norm

from randomgen import RandomGen


class RandomGenTests(TestCase):

    def test_init_validation(self):
        with self.assertRaises(ValueError) as context:
            RandomGen([-1, 0, 1, 2], [0.3, 0.08, 0.31, 0.2, 0.11])
        self.assertTrue('The length of random numbers and probabilities do not match' in context.exception.args)

        with self.assertRaises(ValueError) as context:
            RandomGen([-1, 0, 1, 2, 3], [0.3, 0.08, 0.31, 0.19, 0.11])
        self.assertTrue('Probabilities do not sum up to 1' in context.exception.args)

    @patch('randomgen.random')
    def test_next_num_with_seed(self, rangen_patch):
        cdf = [0.6398, 0.511, 0.3, 0.007, 0.999, 0.8205, 0.382, 0.75, 0.20005, 0.18]
        rangen_patch.random.side_effect = lambda: cdf.pop() if cdf else 0

        randgen = RandomGen([-1, 0, 1, 2, 3], [0.14, 0.3, 0.28, 0.1, 0.18])
        actual = [randgen.next_num() for _ in range(10)]
        expected = [0, 0, 2, 0, 3, 3, -1, 0, 1, 1]
        self.assertListEqual(actual, expected)

    @patch('randomgen.random')
    def test_next_num_at_prob_edge(self, rangen_patch):
        prob = [0.01, 0.3, 0.58, 0.1, 0.01]
        cdf = list(np.cumsum(prob))
        rangen_patch.random.side_effect = lambda: cdf.pop() if cdf else 0

        randgen = RandomGen([-1, 0, 1, 2, 3], prob)
        actual = [randgen.next_num() for _ in range(7)]
        expected = [3, 2, 1, 0, -1, -1, -1]
        self.assertListEqual(actual, expected)

    def test_goodness_of_fit(self):
        random_nums = [-5, 2, 0, 3.3, -70, 9.5]
        probs = [0.29, 0.13, 0.09, 0.18, 0.20, 0.11]
        randgen = RandomGen(random_nums, probs)

        # chi-square test for the frequencies of random_nums
        n_tests = 10000
        samples = [randgen.next_num() for _ in range(n_tests)]
        nums_obs, f_obs = np.unique(samples, return_counts=True)
        f_exp = [probs[random_nums.index(x)] * n_tests for x in nums_obs]

        alpha = 0.05
        chi2, p = chisquare(f_obs, f_exp=f_exp)
        self.assertTrue(p >= alpha)

        # z-test for the randomness
        p_mean = np.average(random_nums, weights=probs)
        p_var = np.average(np.square(random_nums), weights=probs) - np.square(p_mean)

        sampling_size = 4
        samples2 = np.reshape(samples, (-1, sampling_size))
        sampled_means = np.average(samples2, axis=1)
        s_mean_var = p_var / sampling_size

        z_scores = (sampled_means - p_mean) / s_mean_var
        critical_value = norm.ppf(1 - alpha / 2)
        self.assertTrue((z_scores <= critical_value).all())


