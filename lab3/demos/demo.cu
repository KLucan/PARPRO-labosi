#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>
// -------- KERNEL --------
__global__ void vecAdd(const float* A, const float* B, float* C, int N) {
 int i = blockIdx.x * blockDim.x + threadIdx.x;
 if (i < N) {
 C[i] = A[i] + B[i];
 }
}
// -------- MAIN --------
int main() {
 int N = 1 << 20; // ~1M elements
 size_t size = N * sizeof(float);
 // Host memory
 float *h_A = (float*)malloc(size);
 float *h_B = (float*)malloc(size);
 float *h_C = (float*)malloc(size);
 // Initialize data
 for (int i = 0; i < N; i++) {
 h_A[i] = (float)i;
 h_B[i] = (float)i;
 }
 // Device memory
 float *d_A, *d_B, *d_C;
 cudaMalloc(&d_A, size);
 cudaMalloc(&d_B, size);
 cudaMalloc(&d_C, size);
 // Copy to device
 cudaMemcpy(d_A, h_A, size, cudaMemcpyHostToDevice);
 cudaMemcpy(d_B, h_B, size, cudaMemcpyHostToDevice);
 // Kernel launch configuration
 int threadsPerBlock = 256;
 int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;
 // Launch kernel
 vecAdd<<<blocksPerGrid, threadsPerBlock>>>(d_A, d_B, d_C, N);
 // Copy result back
 cudaMemcpy(h_C, d_C, size, cudaMemcpyDeviceToHost);

 // Check result (first few values)
 printf("C[0]=%f, C[1]=%f, C[2]=%f\n", h_C[0], h_C[1], h_C[2]);
 // Cleanup
 cudaFree(d_A);
 cudaFree(d_B);
 cudaFree(d_C);
 free(h_A);
 free(h_B);
 free(h_C);
 return 0;
}
