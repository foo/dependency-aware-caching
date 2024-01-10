import algorithms as algorithms
import treespace
import logging
from numpy import random
import numpy as np


def calculate_l(n):
    x = 0
    for i in range(n-1, -1, -2):
        x += 2**i
    return x


logging.basicConfig(filename='logs.txt', format='%(levelname)s:%(message)s',
                    level=logging.DEBUG)
results = []
for n in range(4, 10):
    tree = treespace.BinaryTree(n)
    alg = algorithms.RandomBucket(tree)
    tree_caching = algorithms.TreeCaching(tree)
    requests_idx = random.zipf(a=1.5, size=1000)
    requests_idx = list(2**n - requests_idx[requests_idx <= tree.get_size()])
    req_len = len(requests_idx)
    requests = list(map(lambda x: tree.nodes[x - 1], requests_idx))
    for k in np.linspace(2**(n-3), 2**(n-1), 5).astype('int'):
        alg = algorithms.RandomBucket(tree)
        alg_cost = alg.serve_requests(requests, k, calculate_l(n), 1)
        print(f"Alg Cost = {alg_cost}")
        tree_c_cost = tree_caching.serve_requests(requests, k, 1)
        print(f"Tree C Cost = {tree_c_cost}")
        results.append({'n': n, 'k': k, 'alg': alg_cost,
                        'tree_caching': tree_c_cost})
print(results)
