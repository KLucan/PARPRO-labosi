from argparse import ArgumentParser
from time import time

import numpy as np
from numba import float64, guvectorize, int64, vectorize


@vectorize([float64(int64, int64)], target="cuda")
def term(i, n):
    x = (i - 0.5) / n
    return 1 /(1.0 + x * x)


parser = ArgumentParser()
parser.add_argument("exp", type=int, default=26)

args = parser.parse_args()

n = np.int64(2**args.exp)
indices = np.arange(1, n + 1, dtype=np.int64)
n_arr = np.full(n, n, dtype=np.int64)
pi = np.float64(0.0)

start = time()
partials = term(indices, n_arr)
pi = 4 * np.sum(partials) / n
end = time()

baseline_pi = np.pi
error = abs(pi - baseline_pi)

print(pi, f"{error}, {end - start:.4f}s")
