from argparse import ArgumentParser
from time import time

import numpy as np
from numba import float64, guvectorize, int64, vectorize

@guvectorize([(int64[:], int64, float64[:])], '(n),()->()', target="cuda")
def partial_sum(indices, n, out):
    s = np.float64(0.0)
    for i in indices:
        s += 1 / (1 + ((i - 0.5) / n)**2)
    out[0] = s

parser = ArgumentParser()
parser.add_argument("exp", type=int, default=26)
parser.add_argument("-b", type=int, default=1024, required=False)

args = parser.parse_args()

n = np.int64(2**args.exp)
n_blocks = n // args.b
indices = np.arange(1, n + 1, dtype=np.int64).reshape(n_blocks, args.b)
n_arr = np.full(n_blocks, n, dtype=np.int64)
partials = np.zeros(n_blocks, dtype=np.float64)
pi = np.float64(0.0)

start = time()
partial_sum(indices, n_arr, partials)
pi = 4 * np.sum(partials) / n
end = time()

baseline_pi = np.pi
error = abs(pi - baseline_pi)

print(pi, f"{error}, {end - start:.4f}s")
