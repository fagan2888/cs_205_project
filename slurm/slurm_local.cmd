#!/bin/bash
#
#SBATCH -p shared # partition (queue)
#SBATCH -N 1 # number of nodes
#SBATCH -n 2 # number of cores
#SBATCH -t 0-2:00 # time (D-HH:MM)
#SBATCH -o spark-%j.out # STDOUT
#SBATCH -e spark-%j.err # STDERR
#SBATCH --mem=8G

module load Anaconda/5.0.1-fasrc02
echo "Finish loading anaconda"
spark-submit generate_data.py
