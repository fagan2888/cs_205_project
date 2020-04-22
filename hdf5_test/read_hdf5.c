//#include <stdlib.h>
//#include <stdio.h>
#include <hdf5.h>
#include <time.h>

#define FNAME "test.hdf5"
#define DATASET "random_ints"
#define DIM 100000000
//#define DIM 1000

static long data[DIM];

int main(int argc, char**argv)
{
  hid_t file, dset;
  herr_t status;
  clock_t t0, t1;
  double time_used;

  t0 = clock();
  file = H5Fopen(FNAME, H5F_ACC_RDONLY, H5P_DEFAULT);
  dset = H5Dopen(file, DATASET, H5P_DEFAULT);
  status = H5Dread(dset, H5T_NATIVE_LONG, H5S_ALL, H5S_ALL, H5P_DEFAULT, data);
  t1 = clock();

  for(long i =0; i<10; i++)
  {
    printf("data[%ld] = %ld\n", i, data[i]);
  }

  time_used = ((double) (t1 - t0)) / CLOCKS_PER_SEC;

  printf("time(s): %f\n", time_used);

}

