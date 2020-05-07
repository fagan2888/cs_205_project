#~/bin/bash

mkdir -p s3
cd s3
wget -O tracers_info https://spark-illustris-tng.s3.amazonaws.com/tracers_info
echo 'Finish download tracers info'
wget -O particles_info https://spark-illustris-tng.s3.amazonaws.com/particles_info
echo 'Finish download particles info'
wget -O tracers_info_full https://spark-illustris-tng.s3.amazonaws.com/tracers_info_full
