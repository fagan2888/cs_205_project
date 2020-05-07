#include <stdio.h>
#include <stdlib.h>
#define NBINS 64 

typedef struct MyArray {
    float   data[NBINS][NBINS];
} MyArray;

void bin_particles(double *xpos, double *ypos, double *mass, long npart, double width, long nbins, MyArray *ans)
{
	long i, j, k, xbin, ybin;
	double min, max, binwidth, binarea;
	double x, y;

	//printf("npart=%d, nbins=%d\n", npart, nbins);

	binwidth = width/nbins;
	binarea = binwidth * binwidth;

	// #pragma omp parallel shared(xpos,ypos,ans) private(xbin,ybin,i,j)
	// #pragma omp for
	for(i=0; i<npart; i++)
	{
		x = xpos[i];
		y = ypos[i];

		xbin = -1;
		ybin = -1;

		// determine its x bin
		min = -width/2.0;
		max = min + binwidth;
		for(j=0; j<nbins; j++)
		{
			if(x > min && x <= max)
			{
				xbin = j;
				break;
			}
			else
			{
				min += binwidth;
				max += binwidth;
			}
		}

		// determine its y bin
		min = -width/2.0;
		max = min + binwidth;
		for(j=0; j<nbins; j++)
		{
			if(y > min && y <= max)
			{
				ybin = j;
				break;
			}
			else
			{
				min += binwidth;
				max += binwidth;
			}
		}

		if(xbin == -1 || ybin == -1) // we are outside the domain
			continue;

		ans->data[xbin][ybin] += mass[i] / binarea;
	}
	return;
}
