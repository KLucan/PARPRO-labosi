#include <stdio.h>

#include "jacobi.cuh"


// CPU ORIGINAL

void jacobistep(double *psinew, double *psi, int m, int n)
{
	int i, j;

	for(i=1;i<=m;i++) {
		for(j=1;j<=n;j++) {
		psinew[i*(m+2)+j]=0.25*(psi[(i-1)*(m+2)+j]+psi[(i+1)*(m+2)+j]+psi[i*(m+2)+j-1]+psi[i*(m+2)+j+1]);
		}
	}
}


double deltasq(double *newarr, double *oldarr, int m, int n)
{
	int i, j;

	double dsq=0.0;
	double tmp;

	for(i=1;i<=m;i++)
	{
		for(j=1;j<=n;j++)
	{
		tmp = newarr[i*(m+2)+j]-oldarr[i*(m+2)+j];
		dsq += tmp*tmp;
		}
	}

	return dsq;
}


// CUDA

__global__ void jacobistep_kernel(double *psinew, double *psi, int m, int n)
{
	int j = blockIdx.x * blockDim.x + threadIdx.x + 1;
	int i = blockIdx.y * blockDim.y + threadIdx.y + 1;

	if (i <= m && j <= n) {
		int idx = i * (m + 2) + j;
		psinew[idx] = 0.25 * (psi[(i-1)*(m+2)+j] +
		                      psi[(i+1)*(m+2)+j] +
		                      psi[i*(m+2)+j-1] +
		                      psi[i*(m+2)+j+1]);
	}
}


__global__ void deltasq_kernel(double *newarr, double *oldarr, double *partial_sum, int m, int n)
{
	extern __shared__ double shared[];

	int j = blockIdx.x * blockDim.x + threadIdx.x + 1;
	int i = blockIdx.y * blockDim.y + threadIdx.y + 1;
	int tid = threadIdx.y * blockDim.x + threadIdx.x;
	int block_size = blockDim.x * blockDim.y;

	// doprinos dretve
	double val = 0.0;
	if (i <= m && j <= n) {
		int idx = i * (m + 2) + j;
		double tmp = newarr[idx] - oldarr[idx];
		val = tmp * tmp;
	}
	shared[tid] = val;
	__syncthreads();

	// Redukcija
	for (int s = block_size / 2; s > 0; s /= 2) {
		if (tid < s) {
			shared[tid] += shared[tid + s];
		}
		__syncthreads();
	}

	// suma za blok
	if (tid == 0) {
		partial_sum[blockIdx.y * gridDim.x + blockIdx.x] = shared[0];
	}
}


__global__ void copyback_kernel(double *dst, double *src, int m, int n)
{
	int j = blockIdx.x * blockDim.x + threadIdx.x + 1;
	int i = blockIdx.y * blockDim.y + threadIdx.y + 1;

	if (i <= m && j <= n) {
		dst[i*(m+2)+j] = src[i*(m+2)+j];
	}
}
