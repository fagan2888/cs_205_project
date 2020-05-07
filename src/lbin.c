#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#define NBINS 256

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

void bin_particles_smoothed(double *xpos, double *ypos, double *mass, double *size, long npart, double width, long nbins, MyArray *ans)
{
    long i, j, k, xbin, ybin;
    double min, max, binwidth, binarea;
    double x, y, xj, yk;
    double sqdist, sqsize, this_mass;

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

        xj = -width/2.0;
        yk = -width/2.0;

        sqsize = size[i] * size[i];
        this_mass = mass[i];

        for(j=0; j<nbins; j++)
        {
            yk = -width/2.0;
            for(k=0; k<nbins; k++)
            {
                // find dist
                sqdist = (x - xj) * (x - xj) + (y - yk) * (y - yk);
                if(sqdist < 9 * sqsize)
                    ans->data[j][k] += this_mass * exp(-sqdist / sqsize);
                
                yk += binwidth;
            }
            xj += binwidth;
        }
    }
    return;
}