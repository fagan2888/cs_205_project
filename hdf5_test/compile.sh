#!/bin/bash

CC=gcc-9
HDF5_HOME=/usr/local

HDF5_LIB=${HDF5_HOME}/lib
HDF5_INCLUDE=${HDF5_HOME}/include

echo "$CC -I${HDF5_INCLUDE} -L${HDF5_LIB} -lhdf5 read_hdf5.c -o read_hdf5"
$CC -I${HDF5_INCLUDE} -L${HDF5_LIB} -lhdf5 read_hdf5.c -o read_hdf5

