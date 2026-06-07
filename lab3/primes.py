from argparse import ArgumentParser
from time import time

import numpy as np
import pycuda.autoinit
import pycuda.driver as drv
from pycuda.compiler import SourceModule

mod = SourceModule("""
__global__ void count_primes(int *izlaz, int *numbers, int size)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int korak = blockDim.x * gridDim.x;
    for (int i = tid; i < size; i += korak) {
        int num = numbers[i];
        int is_prime = 1;
        if (num < 2) continue;
        for (int j = 2; j * j <= num; j++) {
            if (num % j == 0) {
                is_prime = 0;
                break;
            }
        }
        *izlaz += is_prime;
    }
}

__global__ void count_primes_atomic(int *izlaz, int *numbers, int size)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int korak = blockDim.x * gridDim.x;
    for (int i = tid; i < size; i += korak) {
        int num = numbers[i];
        int is_prime = 1;
        if (num < 2) continue;
        for (int j = 2; j * j <= num; j++) {
            if (num % j == 0) {
                is_prime = 0;
                break;
            }
        }
        atomicAdd(izlaz, is_prime);
    }
}
""")

count_primes = mod.get_function("count_primes")
count_primes_atomic = mod.get_function("count_primes_atomic")

parser = ArgumentParser()
parser.add_argument("exp", type=int)
parser.add_argument("L", type=int)
parser.add_argument("B", type=int)

args = parser.parse_args()

size = np.int32(2**args.exp)
ulaz = np.array([i for i in range(size)], dtype=np.int32)
blocksize = (args.L, 1, 1)
gridsize = (args.B, 1, 1)
izlaz = np.array([0], dtype=np.int32)

izlaz_atomic = np.array([0], dtype=np.int32)

start = time()
count_primes(drv.Out(izlaz), drv.In(ulaz), size, block=blocksize, grid=gridsize)
end = time()
start_atomic = time()
count_primes_atomic(
    drv.Out(izlaz_atomic), drv.In(ulaz), size, block=blocksize, grid=gridsize
)
end_atomic = time()
print(izlaz[0], izlaz_atomic[0], f"{end - start:.4f}s", f"{end_atomic - start_atomic:.4f}s")
