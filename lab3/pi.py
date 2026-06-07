from argparse import ArgumentParser
from time import time

import numpy as np
import pycuda.autoinit
import pycuda.driver as drv
from pycuda.compiler import SourceModule

mod = SourceModule("""
__global__ void partial_pi(double *izlaz, long long n)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int korak = blockDim.x * gridDim.x;
    for (long long i = tid + 1; i <= n; i += korak) {
        double sqr = ((i - 0.5) / n);
        sqr *= sqr;
        double sum = 1 / (1 + sqr);
        izlaz[tid] += sum;
    }
}
""")

partial_pi = mod.get_function("partial_pi")

parser = ArgumentParser()
parser.add_argument("exp", type=int, default=26)
parser.add_argument("-L", type=int, default=512, required=False)
parser.add_argument("-B", type=int, default=256, required=False)

args = parser.parse_args()

n = np.int64(2 ** args.exp)
blocksize = (args.L, 1, 1)
gridsize = (args.B, 1, 1)
izlaz = np.zeros((args.L * args.B, 1), dtype=np.float64)
pi = np.float64(0.0)

start = time()
partial_pi(drv.Out(izlaz), n, block=blocksize, grid=gridsize)
pi = 4 * np.sum(izlaz) / n
end = time()

baseline_pi = np.pi
error = abs(pi - baseline_pi)

print(pi, f"{error}, {end - start:.4f}s")
