import random
import math


class RandomGen(object):

    def __init__(self, random_nums: list, probabilities: list[float]):
        if len(random_nums) != len(probabilities):
            raise ValueError('The length of random numbers and probabilities do not match')

        distribution = []
        cum_sum = 0
        for prob in probabilities:
            if prob < 0 or prob > 1:
                raise ValueError('Probabilities must be between 0 and 1, non-inclusive')
            cum_sum += prob
            distribution.append(cum_sum)

        if not math.isclose(cum_sum, 1):
            raise ValueError('Probabilities do not sum up to 1')

        self._random_nums = random_nums
        self._probabilities = probabilities
        self._distribution = distribution

    def next_num(self):
        random_n = random.random()
        N = len(self._random_nums)

        # binary search to find the corresponding index of the generated probability in the random_nums
        low, high = 0, N - 1
        while low < high:
            mid = (low + high) // 2
            if random_n == self._distribution[mid]:
                low = high = mid
            elif random_n > self._distribution[mid]:
                low = mid + 1
            else:
                high = mid

        return self._random_nums[low]



