import random as rand


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


def test_next_num():
    random_nums = [-1, 0, 1, 2, 3]
    probabilities = [0.01, 0.3, 0.58, 0.1, 0.01]
    gen = RandomGen(random_nums, probabilities)
    pmf = {x: 0 for x in random_nums}
    for i in range(100):
        r = gen.next_num()
        pmf[r] += 1
    print(pmf)


test_next_num()




