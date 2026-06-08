#ifndef JACOBI_CUH
#define JACOBI_CUH

// CPU functions
void jacobistep(double *psinew, double *psi, int m, int n);
double deltasq(double *newarr, double *oldarr, int m, int n);

// CUDA kernels
__global__ void jacobistep_kernel(double *psinew, double *psi, int m, int n);
__global__ void deltasq_kernel(double *newarr, double *oldarr, double *partial_sum, int m, int n);
__global__ void copyback_kernel(double *dst, double *src, int m, int n);

#endif
