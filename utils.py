from numpy import random
import numpy as np


def calculate_l(n):
    x = 0
    for i in range(n-1, -1, -2):
        x += 2**i
    return x


def generate_requests(n, perm=None,
                      a=1.5,
                      size=1000,
                      dist="zipf",
                      rand_type="index"):
    '''
    Generates requests based on the given distribution and parameters
    n: maximum index of the tree in index-wise, and maximum tree level in\
        level-wise generation.
    a: the a parameter in zipf and p in geometric distribution
    size: size of the requested array
    dist: distribution ("zipf" or "geo")
    rand_type: setting the randomness of the distribution on the index or the\
        level of the tree'''
    if dist == "zipf":
        requests_idx = random.zipf(a=a, size=size)
        requests_idx = list(n - requests_idx[requests_idx <= n] + 1)
        while len(requests_idx) < size:
            req_len = len(requests_idx)
            t = size - req_len
            new_reqs = random.zipf(a=a, size=t)
            new_reqs = list(n - new_reqs[new_reqs <= n] + 1)
            requests_idx = np.concatenate((requests_idx, new_reqs))
    elif dist == "geo":
        requests_idx = random.geometric(p=a, size=size)
        requests_idx = requests_idx[requests_idx <= (n - 1)]
        while len(requests_idx) < size:
            req_len = len(requests_idx)
            t = size - req_len
            new_reqs = random.geometric(p=a, size=t)
            new_reqs = new_reqs[new_reqs <= (n - 1)]
            requests_idx = np.concatenate((requests_idx, new_reqs))
        requests_idx = n - requests_idx

    # apply permutation if there are any
    if type(perm) is not type(None):
        perm_func = np.vectorize(lambda x: perm[x-1])
        requests_idx = perm_func(requests_idx)

    # check whether the distribution should be level-wise or index-wise
    if rand_type == "level":
        reqs = list(map(lambda x: np.random.randint(low=2**(x-1), high=2**(x)),
                        requests_idx))
        return reqs

    elif rand_type == "index":
        return requests_idx
