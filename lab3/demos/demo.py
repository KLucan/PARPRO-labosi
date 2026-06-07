import pycuda.autoinit
import pycuda.driver as drv
import numpy

from pycuda.compiler import SourceModule
mod = SourceModule("""
__global__ void vecAdd(const float* A, const float* B, float* C, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
    C[i] = A[i] + B[i];
    }
}
""")

vecAdd = mod.get_function("vecAdd")

N = 2 ** 20
a = numpy.array([i for i in range(N)]).astype(numpy.float32)
b = numpy.array([i for i in range(N)]).astype(numpy.float32)
c = numpy.zeros(N, dtype=numpy.float32)

vecAdd(drv.In(a), drv.In(b), drv.Out(c), numpy.int32(N), block=(256, 1, 1), grid=((N + 255) // 256, 1))

print(c[0:3])
