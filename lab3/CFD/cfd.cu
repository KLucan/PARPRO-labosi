#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "arraymalloc.h"
#include "boundary.h"
#include "jacobi.cuh"
#include "cfdio.h"


int main(int argc, char **argv)
{
	int printfreq=1000; //output frequency
	double error, bnorm;
	double tolerance=0.0; //tolerance for convergence. <=0 means do not check

	//main arrays
	double *psi;
	//temporary versions of main arrays
	double *psitmp;

	//command line arguments
	int scalefactor, numiter;

	//simulation sizes
	int bbase=10;
	int hbase=15;
	int wbase=5;
	int mbase=32;
	int nbase=32;

	int checkerr = 0;

	int m,n,b,h,w;
	int iter;

	double tstart, tstop, ttot, titer;

	//do we stop because of tolerance?
	if (tolerance > 0) {checkerr=1;}

	//check command line parameters and parse them

	if (argc <3|| argc >4) {
		printf("Usage: cfd <scale> <numiter>\n");
		return 0;
	}

	scalefactor=atoi(argv[1]);
	numiter=atoi(argv[2]);

	if(!checkerr) {
		printf("Scale Factor = %i, iterations = %i\n",scalefactor, numiter);
	}
	else {
		printf("Scale Factor = %i, iterations = %i, tolerance= %g\n",scalefactor,numiter,tolerance);
	}

	printf("Irrotational flow\n");

	//Calculate b, h & w and m & n
	b = bbase*scalefactor;
	h = hbase*scalefactor;
	w = wbase*scalefactor;
	m = mbase*scalefactor;
	n = nbase*scalefactor;

	printf("Running CFD on %d x %d grid with parallel\n",m,n);

	//allocate host arrays
	psi    = (double *) malloc((m+2)*(n+2)*sizeof(double));
	psitmp = (double *) malloc((m+2)*(n+2)*sizeof(double));

	//zero the psi array
	for (int i=0;i<m+2;i++) {
		for(int j=0;j<n+2;j++) {
			psi[i*(m+2)+j]=0.0;
		}
	}

	//set the psi boundary conditions
	boundarypsi(psi,m,n,b,h,w);

	//compute normalisation factor for error
	bnorm=0.0;

	for (int i=0;i<m+2;i++) {
			for (int j=0;j<n+2;j++) {
			bnorm += psi[i*(m+2)+j]*psi[i*(m+2)+j];
		}
	}
	bnorm=sqrt(bnorm);

	// GPU SETUP

	double *d_psi, *d_psitmp, *d_partial;
	cudaMalloc(&d_psi,    (m+2)*(n+2)*sizeof(double));
	cudaMalloc(&d_psitmp, (m+2)*(n+2)*sizeof(double));

	cudaMemcpy(d_psi, psi, (m+2)*(n+2)*sizeof(double), cudaMemcpyHostToDevice);

	// 256 dretvi po bloku
	dim3 threadsPerBlock(16, 16);
	dim3 numBlocks((n + 15) / 16, (m + 15) / 16);
	int total_blocks = numBlocks.x * numBlocks.y;

	cudaMalloc(&d_partial, total_blocks * sizeof(double));
	double *h_partial = (double *)malloc(total_blocks * sizeof(double));

	//begin iterative Jacobi loop
	printf("\nStarting main loop...\n\n");
	tstart=gettime();

	for(iter=1;iter<=numiter;iter++) {

		//calculate psi for next iteration
		jacobistep_kernel<<<numBlocks, threadsPerBlock>>>(d_psitmp, d_psi, m, n);

		//calculate current error if required
		if (checkerr || iter == numiter) {
			// shared memory
			size_t smem_size = threadsPerBlock.x * threadsPerBlock.y * sizeof(double);
			deltasq_kernel<<<numBlocks, threadsPerBlock, smem_size>>>(d_psitmp, d_psi, d_partial, m, n);

			// suma na hostu
			cudaMemcpy(h_partial, d_partial, total_blocks * sizeof(double), cudaMemcpyDeviceToHost);
			double dsq = 0.0;
			for (int k = 0; k < total_blocks; k++) {
				dsq += h_partial[k];
			}
			error = sqrt(dsq);
			error = error / bnorm;
		}

		//quit early if we have reached required tolerance
		if (checkerr) {
			if (error < tolerance) {
				printf("Converged on iteration %d\n",iter);
				break;
			}
		}

		// psitmp -> psi
		copyback_kernel<<<numBlocks, threadsPerBlock>>>(d_psi, d_psitmp, m, n);

		//print loop information
		if(iter%printfreq == 0) {
			if (!checkerr) {
				printf("Completed iteration %d\n",iter);
			}
			else {
				printf("Completed iteration %d, error = %g\n",iter,error);
			}
		}
	}	// iter

	if (iter > numiter) iter=numiter;

	// razultat nazad na hosta
	cudaMemcpy(psi, d_psi, (m+2)*(n+2)*sizeof(double), cudaMemcpyDeviceToHost);

	tstop=gettime();

	ttot=tstop-tstart;
	titer=ttot/(double)iter;

	//print out some stats
	printf("\n... finished\n");
	printf("After %d iterations, the error is %g\n",iter,error);
	printf("Time for %d iterations was %g seconds\n",iter,ttot);
	printf("Each iteration took %g seconds\n",titer);

	//output results
	//writedatafiles(psi,m,n, scalefactor);
	//writeplotfile(m,n,scalefactor);

	//free un-needed arrays
	cudaFree(d_psi);
	cudaFree(d_psitmp);
	cudaFree(d_partial);
	free(h_partial);
	free(psi);
	free(psitmp);
	printf("... finished\n");

	return 0;
}
